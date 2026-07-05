"""heat_pool.py · 热度池采集与计分 (Phase 7.1).

术语见 CONTEXT.md「热度池 (Heat Pool)」：纯数据信号驱动的候选新闻集。

数据流向：
  RANKED_SECTIONS
    → fetch_heat_signals (Guardian Section API: show-most-viewed + show-editors-picks)
    → score_and_rank      (URL 去重聚合, composite score, DESC 排序)
    → filter_seen         (排除 seen_news.sqlite 已跑过的 URL)
    → fallback_newest     (不够 min_count 时用 order-by=newest 补齐)
    → enrich_descriptions (逐条调 Content API 拿正文, 提取 description)
    → persist pool.json   (output/daily_batch/{date}/pool.json)

复用 scripts/fetch_news.py 的 is_url_seen / mark_selected / extract_guardian_description /
_load_env_value，避免重复实现 Guardian API 鉴权、dedup 与正文抽取逻辑。
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import sys
import time
from typing import Any

import requests

from scripts.fetch_news import (
    _load_env_value,
    extract_guardian_description,
    is_url_seen,
)
from scripts.lib.paths import repo_root, seen_news_db

# Guardian 32 个内容 section，用于热度池信号采集。与 fetch_news.GUARDIAN_API_SECTIONS
# 不同：这里是热度池专用的排名信号源列表（含 animals-farmed/inequality，无 travel），
# 由 Phase 7.1 grill session 直接给出，不复用旧的 blacklist 过滤逻辑。
RANKED_SECTIONS: list[str] = [
    "animals-farmed", "artanddesign", "australia-news", "books",
    "business", "commentisfree", "culture", "education",
    "environment", "fashion", "film", "food",
    "football", "games", "global-development", "inequality",
    "law", "lifeandstyle", "media", "money",
    "music", "news", "politics", "science",
    "society", "sport", "stage", "technology",
    "tv-and-radio", "uk-news", "us-news", "world",
]

DEFAULT_MIN_COUNT = 10
_SECTION_REQUEST_DELAY_SECONDS = 0.1  # Guardian 免费 tier rate limit (12 req/s) 缓冲
_SECTION_API_BASE = "https://content.guardianapis.com"


def _resolve_api_key(api_key: str | None) -> str:
    resolved = api_key or _load_env_value("GUARDIAN_API_KEY")
    if resolved is None:
        raise RuntimeError("GUARDIAN_API_KEY not set")
    return resolved


def _guardian_content_endpoint(item: dict[str, Any]) -> str | None:
    api_url = item.get("api_url")
    if isinstance(api_url, str) and api_url.strip():
        return api_url.strip()

    guardian_id = item.get("id")
    if isinstance(guardian_id, str) and guardian_id.strip():
        return f"{_SECTION_API_BASE}/{guardian_id.strip()}"

    url = item.get("url")
    if isinstance(url, str) and url.strip():
        return url.strip()

    return None


def _signal_from_result(result: dict[str, Any], section: str, signal_type: str, rank_position: int) -> dict[str, Any]:
    """把 Guardian mostViewed/editorsPicks 单条 result 规范化为 raw signal dict."""

    return {
        "url": result.get("webUrl"),
        "title": result.get("webTitle"),
        "pub_time": result.get("webPublicationDate"),
        "section": section,
        "signal_type": signal_type,
        "rank_position": rank_position,
        "id": result.get("id"),
        "api_url": result.get("apiUrl"),
    }


def fetch_heat_signals(
    sections: list[str] = RANKED_SECTIONS,
    *,
    api_key: str | None = None,
    sleep_seconds: float = _SECTION_REQUEST_DELAY_SECONDS,
) -> list[dict[str, Any]]:
    """遍历 sections，逐个调用 Guardian Section API 拉 mostViewed + editorsPicks 信号。

    单个 section 请求失败（网络错误 / 非 200）不会中断整批采集，只跳过该 section。
    请求之间插入 sleep_seconds，避免撞 Guardian 免费 tier 的 12 req/s 限速。
    """

    resolved_api_key = _resolve_api_key(api_key)
    signals: list[dict[str, Any]] = []
    consecutive_rate_limited_sections = 0

    for index, section in enumerate(sections):
        if index > 0 and sleep_seconds > 0:
            time.sleep(sleep_seconds)

        params = {
            "api-key": resolved_api_key,
            "show-most-viewed": "true",
            "show-editors-picks": "true",
        }

        def _request_section() -> dict[str, Any]:
            response = requests.get(f"{_SECTION_API_BASE}/{section}", params=params, timeout=30)
            response.raise_for_status()
            return response.json()

        try:
            payload = _request_guardian_with_retry(
                f"section {section}",
                _request_section,
                max_attempts=_SECTION_RETRY_ATTEMPTS,
                base_seconds=_SECTION_RETRY_BASE_SECONDS,
            )
        except (requests.RequestException, OSError, ValueError) as exc:
            status_code = getattr(getattr(exc, "response", None), "status_code", "unknown")
            _log_heat_pool(
                f"[heat_pool] section {section} skipped after {_SECTION_RETRY_ATTEMPTS} Guardian {status_code} retries"
            )
            if status_code == 429:
                consecutive_rate_limited_sections += 1
                if consecutive_rate_limited_sections >= _SECTION_CONSECUTIVE_429_CIRCUIT_BREAKER:
                    _log_heat_pool(
                        "[heat_pool] Guardian section scan circuit-open after "
                        f"{consecutive_rate_limited_sections} consecutive 429 sections; "
                        "remaining sections skipped"
                    )
                    break
            else:
                consecutive_rate_limited_sections = 0
            continue

        consecutive_rate_limited_sections = 0
        section_response = payload.get("response") or {}
        # 数据流向: section response -> mostViewed[]/editorsPicks[] -> 按数组下标算 rank_position(1-based) -> raw signal。
        for signal_type, key in (("mostViewed", "mostViewed"), ("editorsPicks", "editorsPicks")):
            for rank_position, result in enumerate(section_response.get(key) or [], start=1):
                signals.append(_signal_from_result(result, section, signal_type, rank_position))

    return signals


def score_and_rank(signals: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """按 URL 去重聚合 signals，计算 composite score，按 score DESC 排序。

    score = sum(1/rank_position for mostViewed 命中) + 0.5 * count(editorsPicks 命中)
    """

    aggregated: dict[str, dict[str, Any]] = {}

    for signal in signals:
        url = signal.get("url")
        if not isinstance(url, str) or not url.strip():
            continue

        entry = aggregated.get(url)
        if entry is None:
            entry = {
                "url": url,
                "title": signal.get("title"),
                "pub_time": signal.get("pub_time"),
                "score": 0.0,
                "sources": [],
                "id": signal.get("id"),
                "api_url": signal.get("api_url"),
            }
            aggregated[url] = entry

        rank_position = signal.get("rank_position")
        signal_type = signal.get("signal_type")
        if signal_type == "mostViewed" and isinstance(rank_position, int) and rank_position > 0:
            entry["score"] += 1.0 / rank_position
        elif signal_type == "editorsPicks":
            entry["score"] += 0.5

        entry["sources"].append(
            {
                "section": signal.get("section"),
                "signal_type": signal_type,
                "rank_position": rank_position,
            }
        )

    ranked = list(aggregated.values())
    ranked.sort(key=lambda item: item["score"], reverse=True)
    return ranked


def filter_seen(ranked: list[dict[str, Any]], *, db_path: Path | None = None) -> list[dict[str, Any]]:
    """排序后过滤掉 seen_news.sqlite 中已跑过的 URL，保留剩余顺序。"""

    return [item for item in ranked if not is_url_seen(item["url"], db_path)]


def _guardian_result_to_pool_item(result: dict[str, Any]) -> dict[str, Any]:
    """把 fetch_guardian_api() 返回的 news payload 转成 pool item 形状（补 score/sources）。"""

    return {
        "url": result.get("url"),
        "title": result.get("title"),
        "pub_time": result.get("pub_time"),
        "score": 0.0,
        "sources": [],
        "description": result.get("description"),
        "source_name": result.get("source_name"),
        "fallback": True,
    }


def _log_heat_pool(message: str) -> None:
    print(message, file=sys.stderr, flush=True)


_SECTION_RETRY_ATTEMPTS = 2
_SECTION_RETRY_BASE_SECONDS = 5.0
_SECTION_CONSECUTIVE_429_CIRCUIT_BREAKER = 2
_FALLBACK_RETRY_ATTEMPTS = 4
_FALLBACK_RETRY_BASE_SECONDS = 8.0


def _guardian_retry_delay_seconds(
    exc: Exception,
    attempt: int,
    *,
    base_seconds: float,
    max_delay_seconds: float,
) -> float:
    """Return retry delay for Guardian requests, honoring Retry-After when present."""

    response = getattr(exc, "response", None)
    retry_after = getattr(response, "headers", {}).get("Retry-After") if response is not None else None
    if retry_after is not None:
        try:
            parsed = float(retry_after)
            if parsed >= 0:
                return min(parsed, max_delay_seconds)
        except ValueError:
            pass
    return min(base_seconds * (2 ** max(attempt - 1, 0)), max_delay_seconds)


def _is_retryable_guardian_error(exc: Exception) -> bool:
    response = getattr(exc, "response", None)
    status_code = getattr(response, "status_code", None)
    return status_code == 429 or (isinstance(status_code, int) and 500 <= status_code < 600)


def _request_guardian_with_retry(
    operation: str,
    request_fn,
    *,
    max_attempts: int,
    base_seconds: float,
) -> Any:
    last_exc: Exception | None = None
    for attempt in range(1, max_attempts + 1):
        try:
            return request_fn()
        except requests.RequestException as exc:
            last_exc = exc
            if attempt >= max_attempts or not _is_retryable_guardian_error(exc):
                raise
            delay = _guardian_retry_delay_seconds(
                exc,
                attempt,
                base_seconds=base_seconds,
                max_delay_seconds=10.0 if operation.startswith("section ") else 120.0,
            )
            status_code = getattr(getattr(exc, "response", None), "status_code", "unknown")
            _log_heat_pool(
                f"[heat_pool] {operation} hit Guardian {status_code}; retry {attempt}/{max_attempts} in {delay:.1f}s"
            )
            time.sleep(delay)
    if last_exc is not None:
        raise last_exc
    raise RuntimeError(f"{operation} failed unexpectedly")


def fallback_newest(
    ranked: list[dict[str, Any]],
    *,
    min_count: int = DEFAULT_MIN_COUNT,
    db_path: Path | None = None,
    api_key: str | None = None,
) -> list[dict[str, Any]]:
    """ranked 不够 min_count 时，用 fetch_guardian_api(order_by='newest') 补齐。

    新补的条目沿用 fetch_guardian_api 自带的 is_url_seen 过滤，且跳过已在 ranked 中
    出现过的 URL，避免重复。
    """

    if len(ranked) >= min_count:
        return ranked

    from scripts.fetch_news import fetch_guardian_api  # 延迟导入避免测试 mock 循环依赖

    existing_urls = {item["url"] for item in ranked}
    needed = min_count - len(ranked)

    try:
        newest_results = _request_guardian_with_retry(
            "guardian newest fallback",
            lambda: fetch_guardian_api(
                sections=RANKED_SECTIONS,
                order_by="newest",
                page_size=max(needed * 2, min_count),
                db_path=db_path,
                api_key=api_key,
            ),
            max_attempts=_FALLBACK_RETRY_ATTEMPTS,
            base_seconds=_FALLBACK_RETRY_BASE_SECONDS,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Guardian newest fallback failed after retries with only {len(ranked)} ranked items; need {min_count}"
        ) from exc

    supplemented = list(ranked)
    for result in newest_results:
        if len(supplemented) >= min_count:
            break
        url = result.get("url")
        if not isinstance(url, str) or url in existing_urls:
            continue
        supplemented.append(_guardian_result_to_pool_item(result))
        existing_urls.add(url)

    if len(supplemented) < min_count:
        raise RuntimeError(
            f"Guardian newest fallback returned only {len(supplemented)} items; need {min_count}"
        )

    return supplemented


def enrich_descriptions(
    selected: list[dict[str, Any]],
    *,
    api_key: str | None = None,
) -> list[dict[str, Any]]:
    """对每条尚缺 description 的候选调 Content API 拿正文，提取 description 字段。

    优先使用 Guardian Content API 结果里的 apiUrl / id；fallback 到 url 仅用于兼容旧数据。
    """

    resolved_api_key = _resolve_api_key(api_key)
    enriched: list[dict[str, Any]] = []

    for item in selected:
        if item.get("description"):
            enriched.append(item)
            continue

        endpoint = _guardian_content_endpoint(item)
        item = dict(item)
        if endpoint is None:
            item["description"] = ""
            enriched.append(item)
            continue

        params = {
            "api-key": resolved_api_key,
            "show-fields": "bodyText,trailText",
            "show-tags": "all",
        }
        try:
            response = requests.get(endpoint, params=params, timeout=30)
            response.raise_for_status()
            payload = response.json()
            result = (payload.get("response") or {}).get("content") or {}
            fields = result.get("fields") or {}
            body = fields.get("bodyText") or fields.get("trailText") or ""
            tags = result.get("tags") or []
            item["description"] = extract_guardian_description(body, tags)
        except (requests.RequestException, OSError, ValueError, KeyError):
            item["description"] = ""

        enriched.append(item)

    return enriched


def pool_output_path(date: str, out_dir: Path | None = None) -> Path:
    base = out_dir or (repo_root() / "output" / "daily_batch")
    return base / date / "pool.json"


def _today_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def fetch_heat_pool(
    *,
    date: str | None = None,
    min_count: int = DEFAULT_MIN_COUNT,
    max_items: int | None = None,
    sections: list[str] | None = None,
    db_path: Path | None = None,
    api_key: str | None = None,
    dry_run: bool = False,
    out_dir: Path | None = None,
) -> list[dict[str, Any]]:
    """顶层入口：fetch → score → filter → fallback → enrich → persist pool.json。

    dry_run=True 时跳过写盘（供 CLI --dry-run 使用）。
    """

    resolved_date = date or _today_iso()
    resolved_db_path = db_path if db_path is not None else seen_news_db()
    resolved_sections = sections if sections is not None else RANKED_SECTIONS
    target_count = max_items if max_items is not None else min_count

    if max_items is not None and max_items <= 0:
        raise ValueError(f"max_items must be a positive integer, got {max_items}")

    signals = fetch_heat_signals(resolved_sections, api_key=api_key)
    ranked = score_and_rank(signals)
    filtered = filter_seen(ranked, db_path=resolved_db_path)
    supplemented = fallback_newest(
        filtered, min_count=target_count, db_path=resolved_db_path, api_key=api_key
    )
    # Heat Pool may rank hundreds of Guardian items across 32 sections, but the daily
    # batch contract is top-N selection.  The default N is min_count (10); smoke/dev
    # callers can narrow it further with max_items.  Description enrichment is the
    # expensive Content API step, so it must only run on the selected batch items.
    selected = supplemented[:target_count]
    pool = enrich_descriptions(selected, api_key=api_key)

    if not dry_run:
        output_path = pool_output_path(resolved_date, out_dir)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(pool, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )

    return pool


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Fetch and score the Guardian heat pool (mostViewed + editorsPicks).",
    )
    parser.add_argument("--date", help="briefing date override (default: today, UTC, YYYY-MM-DD)")
    parser.add_argument(
        "--min-count",
        type=int,
        default=DEFAULT_MIN_COUNT,
        metavar="N",
        help=f"minimum pool size after fallback (default: {DEFAULT_MIN_COUNT})",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="print the ranked pool without writing pool.json",
    )
    return parser


def run_cli(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        pool = fetch_heat_pool(
            date=args.date,
            min_count=args.min_count,
            dry_run=args.dry_run,
        )
    except RuntimeError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(pool, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> None:
    raise SystemExit(run_cli(argv))


if __name__ == "__main__":
    main()