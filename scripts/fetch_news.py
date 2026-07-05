"""fetch_news.py · RSS 抓取与候选新闻挑选 (MVP 半自动).

MVP 决策:
  - 用免费 RSS 源 (清单待定, 放本文件 FEEDS 常量).
  - "热度": 多源同事件计数 + 时间近端加权 (暂粗糙).
  - 去重:
      a) URL 规范化 (剥 utm_*) 后查 state/seen_news.sqlite, 跑过则跳过
      b) 标题相似度: 与过去 14 天选过的标题做 difflib.SequenceMatcher, >=0.7 跳过
  - 允许人工指定 url 绕过整段抓取 (CLI: --url <url>).
  - 不爬全文, 仅用 RSS 自带 title + description + pub_time + source_name.

输出: 一个 dict
  {
    "title": str,
    "description": str,
    "pub_time": str | None,
    "source_name": str | None,
  }
"""

from __future__ import annotations

import argparse
from contextlib import closing
from datetime import datetime, timedelta, timezone
import difflib
import html
import json
import logging
import os
from pathlib import Path
import re
import sqlite3
import sys
from typing import Any, TextIO
from urllib.parse import parse_qsl, urlencode, urlparse, urlsplit, urlunsplit

import feedparser
import requests

from scripts.lib.paths import seen_news_db

logger = logging.getLogger(__name__)

FEEDS: list[str] = [
    "https://www.theguardian.com/world/rss",
    "https://www.theguardian.com/us-news/rss",
    "https://www.theguardian.com/uk-news/rss",
]

# Guardian API defaults: wide-in section policy. The list is intentionally broad;
# the allow decision is made by the blacklist helpers below, not by hand-picking a
# small editorial whitelist.
GUARDIAN_API_SECTIONS: list[str] = [
    "artanddesign",
    "australia-news",
    "books",
    "business",
    "commentisfree",
    "culture",
    "education",
    "environment",
    "fashion",
    "film",
    "football",
    "food",
    "games",
    "global-development",
    "law",
    "lifeandstyle",
    "media",
    "money",
    "music",
    "politics",
    "science",
    "society",
    "sport",
    "stage",
    "technology",
    "travel",
    "tv-and-radio",
    "uk-news",
    "us-news",
    "world",
]

GUARDIAN_SECTION_META_TOOL_BLACKLIST: set[str] = {
    "about",
    "community",
    "crosswords",
    "extra",
    "guardian-foundation",
    "help",
    "info",
    "jobsadvice",
    "katine",
    "membership",
    "search",
    "theguardian",
    "theobserver",
    "thefilter",
    "thefilter-us",
}
GUARDIAN_SECTION_FUNCTIONAL_BLACKLIST: set[str] = {"weather", "travel-offers"}
# Low-event sections are article-bearing but dominated by personal travelogue/
# service texture rather than public event narratives. They are excluded at the
# section layer instead of being mixed into the pure functional-page blacklist.
GUARDIAN_SECTION_LOW_EVENT_BLACKLIST: set[str] = {"travel"}
GUARDIAN_SECTION_LOCAL_BLACKLIST: set[str] = {
    "local",
    "cardiff",
    "edinburgh",
    "leeds",
    "cities",
}
GUARDIAN_SECTION_SUFFIX_BLACKLIST = ("-network", "professional")
GUARDIAN_SECTION_EXACT_BLACKLIST: set[str] = (
    GUARDIAN_SECTION_META_TOOL_BLACKLIST
    | GUARDIAN_SECTION_FUNCTIONAL_BLACKLIST
    | GUARDIAN_SECTION_LOW_EVENT_BLACKLIST
    | GUARDIAN_SECTION_LOCAL_BLACKLIST
)


_TAG_RE = re.compile(r"<[^>]+>")
_WHITESPACE_RE = re.compile(r"\s+")
_GUARDIAN_CONTINUE_RE = re.compile(r"(?:\s*Continue reading\.{0,3}\s*)+$", re.IGNORECASE)
_TRACKING_QUERY_KEYS = {"fbclid", "gclid", "dclid", "msclkid", "mc_cid", "mc_eid", "igshid"}


def _load_env_value(name: str, env_path: Path | None = None) -> str | None:
    """Read a single KEY=value from .env without adding a runtime dependency."""

    if name in os.environ:
        return os.environ[name]
    path = env_path or Path(".env")
    if not path.exists():
        return None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        if key.strip() == name:
            return value.strip().strip('"').strip("'")
    return None


def _db_path(db_path: Path | None = None) -> Path:
    """Resolve the dedup SQLite path; tests can inject a temp file."""

    return seen_news_db() if db_path is None else Path(db_path)


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Create RSS dedup tables if this is the first database access."""

    conn.execute(
        "CREATE TABLE IF NOT EXISTS seen_urls (url_norm TEXT PRIMARY KEY, seen_at TEXT)"
    )
    conn.execute("CREATE TABLE IF NOT EXISTS seen_titles (title TEXT, seen_at TEXT)")
    conn.commit()


def _connect(db_path: Path | None = None) -> sqlite3.Connection:
    """Open the dedup database and ensure URL/title state tables exist."""

    resolved = _db_path(db_path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(resolved)
    _ensure_schema(conn)
    return conn


def _utc_now(now: datetime | None = None) -> datetime:
    if now is None:
        return datetime.now(timezone.utc)
    if now.tzinfo is None:
        return now.replace(tzinfo=timezone.utc)
    return now.astimezone(timezone.utc)


def _iso_now(now: datetime | None = None) -> str:
    return _utc_now(now).isoformat()


def normalize_url(url: str) -> str:
    """Normalize an RSS article URL for deterministic URL-level deduplication.

    Tracking query parameters are removed, scheme/host are lower-cased, fragments are
    discarded, and normal query parameters are preserved. Path case is intentionally
    unchanged because URL paths can be case-sensitive.
    """

    split = urlsplit(url.strip())
    query_pairs = []
    for key, value in parse_qsl(split.query, keep_blank_values=True):
        key_lower = key.lower()
        if key_lower.startswith("utm_") or key_lower in _TRACKING_QUERY_KEYS:
            continue
        query_pairs.append((key, value))

    # 数据流向：RSS 原始 URL -> 去营销参数/fragment -> 规范化 URL -> seen_urls 主键。
    return urlunsplit(
        (
            split.scheme.lower(),
            split.netloc.lower(),
            split.path,
            urlencode(query_pairs, doseq=True),
            "",
        )
    )


def is_url_seen(url: str, db_path: Path | None = None) -> bool:
    """Return True when the normalized URL already exists in seen_urls."""

    url_norm = normalize_url(url)
    with closing(_connect(db_path)) as conn:
        row = conn.execute(
            "SELECT 1 FROM seen_urls WHERE url_norm = ? LIMIT 1", (url_norm,)
        ).fetchone()
    return row is not None


def mark_url_seen(
    url: str, db_path: Path | None = None, seen_at: str | None = None
) -> None:
    """Persist a normalized selected URL in seen_urls.

    This write belongs to the selection stage (5.3), not the RSS fetch/filter stage.
    """

    with closing(_connect(db_path)) as conn:
        conn.execute(
            "INSERT OR IGNORE INTO seen_urls (url_norm, seen_at) VALUES (?, ?)",
            (normalize_url(url), seen_at or _iso_now()),
        )
        conn.commit()


def _normalize_title(title: str) -> str:
    return _WHITESPACE_RE.sub(" ", title.strip().lower())


def is_title_similar(
    title: str,
    db_path: Path | None = None,
    *,
    threshold: float = 0.7,
    within_days: int = 14,
    now: datetime | None = None,
) -> bool:
    """Return True if title resembles a selected title within the recent window.

    标题相似度只供 5.3 选用阶段标注/展示；抓取阶段的 filter_new_entries
    不会因为标题相似而丢弃候选。
    """

    cutoff = _utc_now(now) - timedelta(days=within_days)
    candidate = _normalize_title(title)
    with closing(_connect(db_path)) as conn:
        rows = conn.execute(
            "SELECT title FROM seen_titles WHERE seen_at >= ?", (cutoff.isoformat(),)
        ).fetchall()

    for (seen_title,) in rows:
        ratio = difflib.SequenceMatcher(
            None, candidate, _normalize_title(str(seen_title))
        ).ratio()
        if ratio >= threshold:
            return True
    return False


def mark_title_seen(
    title: str, db_path: Path | None = None, seen_at: str | None = None
) -> None:
    """Persist a selected title for later 14-day similarity checks."""

    with closing(_connect(db_path)) as conn:
        conn.execute(
            "INSERT INTO seen_titles (title, seen_at) VALUES (?, ?)",
            (title.strip(), seen_at or _iso_now()),
        )
        conn.commit()


def filter_new_entries(
    entries: list[dict],
    db_path: Path | None = None,
    *,
    title_threshold: float = 0.7,
    within_days: int = 14,
    now: datetime | None = None,
) -> list[dict]:
    """Filter RSS candidates by URL seen state only, preserving input order.

    抓取阶段语义边界：这里只读 seen_urls，不写库，也不按标题相似度过滤。
    title_threshold/within_days/now 预留给 5.3 选用阶段 UI 标注，不参与本函数判定。
    """

    del title_threshold, within_days, now
    new_entries: list[dict] = []
    for entry in entries:
        url = entry.get("url")
        if not isinstance(url, str) or not url.strip():
            new_entries.append(entry)
            continue
        if not is_url_seen(url, db_path):
            new_entries.append(entry)
    return new_entries


def mark_selected(
    entry: dict, db_path: Path | None = None, now: datetime | None = None
) -> None:
    """Mark a picked news payload as seen by both URL and title for 5.3."""

    seen_at = _iso_now(now)
    url = entry.get("url")
    title = entry.get("title")
    # 数据流向：用户选中的 payload -> 同一时间戳写入 URL 去重 + 标题相似度状态。
    if isinstance(url, str) and url.strip():
        mark_url_seen(url, db_path, seen_at=seen_at)
    if isinstance(title, str) and title.strip():
        mark_title_seen(title, db_path, seen_at=seen_at)


def _get_value(obj: Any, key: str, default: Any = None) -> Any:
    """同时兼容 feedparser 对象、SimpleNamespace 与 dict 的字段读取。"""

    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _strip_html(text: str) -> str:
    """移除 RSS 摘要里的轻量 HTML，并压平多余空白。"""

    unescaped = html.unescape(text)
    without_tags = _TAG_RE.sub(" ", unescaped)
    normalized = _WHITESPACE_RE.sub(" ", without_tags).strip()
    return _GUARDIAN_CONTINUE_RE.sub("", normalized).strip()


_PARA_RE = re.compile(r"<p>(.*?)</p>", re.DOTALL)
_RELATED_RE = re.compile(r"^Related:\s", re.IGNORECASE)

# Data-table DSL for tone-driven extraction. Strategy rows are deliberately data,
# so adding a new Guardian tone should mean adding a row rather than changing the
# routing logic.
# These tones are immediate streams / reader letters / contribution calls rather
# than complete cause-process-result event narratives. Product needs complete
# event structure, so they are dropped as whole articles before extraction.
TONE_DROP_BLACKLIST: set[str] = {
    "tone/minutebyminute",
    "tone/letters",
    "tone/competitions",
}

EXTRACTION_TABLE: dict[str, dict[str, int | str]] = {
    "tone/recipes": {"strategy": "front", "paragraphs": 1},
    "tone/reviews": {"strategy": "front", "paragraphs": 3},
    "tone/interview": {"strategy": "front", "paragraphs": 3},
    "tone/analysis": {"strategy": "front", "paragraphs": 4},
    "tone/comment": {"strategy": "front", "paragraphs": 4},
    "tone/news": {"strategy": "front", "paragraphs": 5},
    "tone/features": {"strategy": "paragraph_decay"},
}
_TONE_SPECIFICITY_ORDER: dict[str, int] = {
    tone: rank for rank, tone in enumerate(EXTRACTION_TABLE.keys())
}
DEFAULT_NO_TONE_EXTRACTION = {"strategy": "front", "paragraphs": 3}


def is_guardian_section_allowed(section: str) -> bool:
    """Return True unless a Guardian section belongs to one of five blacklists."""

    normalized = section.strip().lower()
    if not normalized:
        return False
    if normalized in GUARDIAN_SECTION_EXACT_BLACKLIST:
        return False
    return not any(normalized.endswith(suffix) for suffix in GUARDIAN_SECTION_SUFFIX_BLACKLIST)


def filter_guardian_sections(sections: list[str]) -> list[str]:
    """Apply the wide-in blacklist policy while preserving section order."""

    kept: list[str] = []
    seen: set[str] = set()
    for section in sections:
        normalized = section.strip().lower()
        if normalized in seen or not is_guardian_section_allowed(normalized):
            continue
        kept.append(normalized)
        seen.add(normalized)
    return kept


def _extract_paragraphs(body: str) -> list[str]:
    """Extract meaningful Guardian paragraphs from HTML or bodyText/plain text."""

    paragraphs = _PARA_RE.findall(body)
    if paragraphs:
        raw_paragraphs = paragraphs
    else:
        # Guardian bodyText is plain text. Prefer blank-line paragraphs; if the API
        # flattens everything into one block, sentence splitting below still gives
        # the tone router bounded, paragraph-like chunks instead of one huge lead.
        raw_paragraphs = [part for part in re.split(r"\n\s*\n", body) if part.strip()]
        if len(raw_paragraphs) <= 1:
            raw_paragraphs = re.split(r"(?<=[.!?])\s+", body)

    kept: list[str] = []
    for paragraph in raw_paragraphs:
        clean = _WHITESPACE_RE.sub(" ", _TAG_RE.sub("", paragraph)).strip()
        if not clean or _RELATED_RE.match(clean):
            continue
        kept.append(clean)
    return kept


def _join_paragraphs(paragraphs: list[str]) -> str:
    return " ".join(paragraphs).strip()


def _take_front(paragraphs: list[str], count: int) -> str:
    return _join_paragraphs(paragraphs[:count])


def _paragraph_decay_heuristic(paragraphs: list[str]) -> str:
    """Heuristic for tone/features, Guardian's broad "format black hole" tone.

    The signal is paragraph-length decay: keep the lede, then keep follow-up
    paragraphs while they remain substantial compared with the lede/previous
    paragraph. Stop when a short bridge/list-like paragraph suggests the article
    has moved from core setup into looser feature texture. Cap at 4 paragraphs so
    this never becomes an implicit broad-news 5 paragraph extractor.
    """

    if not paragraphs:
        return ""
    if len(paragraphs) == 1:
        return paragraphs[0]

    kept = [paragraphs[0]]
    first_len = max(len(paragraphs[0]), 1)
    previous_len = first_len
    for paragraph in paragraphs[1:4]:
        length = len(paragraph)
        first_ratio = length / first_len
        previous_ratio = length / max(previous_len, 1)
        if length < 180 and first_ratio < 0.55 and previous_ratio < 0.75:
            break
        kept.append(paragraph)
        previous_len = length
    return _join_paragraphs(kept)


def _article_tones(tags: list[Any] | None) -> list[str]:
    tones: list[str] = []
    for tag in tags or []:
        value = tag.get("id") if isinstance(tag, dict) else getattr(tag, "id", None)
        if isinstance(value, str) and value.startswith("tone/"):
            tones.append(value)
    return tones


def _sort_tones_by_specificity(tones: list[str]) -> list[str]:
    return sorted(tones, key=lambda tone: _TONE_SPECIFICITY_ORDER.get(tone, 10_000))


def should_drop_article(tags: list[Any] | None) -> bool:
    """Return True for tone-level whole-article drops before extraction routing."""

    return any(tone in TONE_DROP_BLACKLIST for tone in _article_tones(tags))


def route_extraction_strategy(tags: list[Any] | None) -> dict[str, int | str]:
    """Route Guardian article extraction by tone/* tags, specific before generic."""

    if should_drop_article(tags):
        return {"strategy": "drop"}
    tones = _article_tones(tags)
    for tone in _sort_tones_by_specificity(tones):
        strategy = EXTRACTION_TABLE.get(tone)
        if strategy is not None:
            return strategy
    return DEFAULT_NO_TONE_EXTRACTION


def extract_guardian_description(body: str, tags: list[Any] | None = None) -> str:
    """Apply tone-driven extraction to a Guardian body.

    This only improves one article's description quality; it intentionally never
    introduces news-surface-similarity filtering, scoring, or ranking.
    """

    paragraphs = _extract_paragraphs(body)
    strategy = route_extraction_strategy(tags)
    if strategy.get("strategy") == "drop":
        return ""
    if strategy.get("strategy") == "paragraph_decay":
        return _paragraph_decay_heuristic(paragraphs)
    count = int(strategy.get("paragraphs", DEFAULT_NO_TONE_EXTRACTION["paragraphs"]))
    return _take_front(paragraphs, count)


def _extract_lead_paragraphs(body_html: str, max_paragraphs: int = 5) -> str:
    """Backward-compatible lead extractor for older RSS/API tests."""

    return _take_front(_extract_paragraphs(body_html), max_paragraphs)


def _published_to_iso(published_parsed: Any) -> str | None:
    """将 feedparser 的 published_parsed 转成 UTC ISO8601 字符串。"""

    if not published_parsed:
        return None

    try:
        return datetime(*published_parsed[:6], tzinfo=timezone.utc).isoformat()
    except (TypeError, ValueError):
        logger.warning("Invalid published_parsed value: %r", published_parsed)
        return None


def _source_name(parsed_feed: Any, feed_url: str) -> str | None:
    """优先使用 RSS 自带源名；缺失时回退到 feed URL 域名。"""

    feed_meta = _get_value(parsed_feed, "feed", {}) or {}
    title = _get_value(feed_meta, "title")
    if isinstance(title, str) and title.strip():
        return title.strip()

    hostname = urlparse(feed_url).hostname
    return hostname or None


def _entry_to_payload(entry: Any, source_name: str | None) -> dict[str, str | int | None] | None:
    """把单条 RSS entry 规范化为 news payload；缺必填字段则返回 None。"""

    title = _get_value(entry, "title")
    raw_description = _get_value(entry, "summary") or _get_value(entry, "description")
    url = _get_value(entry, "link")

    # 数据流向：RSS entry -> 必填字段校验 -> HTML 清洗 -> payload dict。
    if not isinstance(title, str) or not title.strip():
        return None
    if not isinstance(raw_description, str) or not raw_description.strip():
        return None
    if not isinstance(url, str) or not url.strip():
        return None

    description = _strip_html(raw_description)
    if not description:
        return None

    return {
        "title": title.strip(),
        "description": description,
        "pub_time": _published_to_iso(_get_value(entry, "published_parsed")),
        "source_name": source_name,
        "url": url.strip(),
    }


def fetch_feed(feed_url: str) -> list[dict]:
    """解析单个 RSS feed，返回符合 news payload schema 的条目列表。

    网络、解析异常或 bozo 失败不会向外抛出；调用方只会拿到空列表。
    """

    try:
        parsed_feed = feedparser.parse(feed_url)
    except Exception as exc:  # noqa: BLE001 - 抓取层必须隔离单源异常
        logger.warning("Failed to parse RSS feed %s: %s", feed_url, exc)
        return []

    if _get_value(parsed_feed, "bozo", False):
        logger.warning(
            "RSS feed parsed with bozo flag %s: %s",
            feed_url,
            _get_value(parsed_feed, "bozo_exception", "unknown parse error"),
        )
        return []

    source = _source_name(parsed_feed, feed_url)
    payloads: list[dict] = []

    # 数据流向：feed entries -> 单条规范化 -> 丢弃不完整条目 -> 合并返回。
    for entry in _get_value(parsed_feed, "entries", []) or []:
        payload = _entry_to_payload(entry, source)
        if payload is not None:
            payloads.append(payload)

    return payloads


def fetch_all_entries(feeds: list[str] | None = None) -> list[dict]:
    """合并多个 RSS feed 的规范化 news payload，单源失败不影响整批。"""

    selected_feeds = FEEDS if feeds is None else feeds
    entries: list[dict] = []

    for feed_url in selected_feeds:
        try:
            entries.extend(fetch_feed(feed_url))
        except Exception as exc:  # noqa: BLE001 - 保护整批抓取不被单源拖垮
            logger.warning("Skipping RSS feed %s after unexpected error: %s", feed_url, exc)

    return entries


def fetch_guardian_api(
    sections: list[str] | None = None,
    order_by: str = "newest",
    page_size: int = 30,
    min_body_len: int = 400,
    tag: str | None = None,
    *,
    db_path: Path | None = None,
    api_key: str | None = None,
) -> list[dict]:
    """Fetch Guardian Content API search results as news payloads."""

    resolved_api_key = api_key or _load_env_value("GUARDIAN_API_KEY")
    if resolved_api_key is None:
        raise RuntimeError("GUARDIAN_API_KEY not set")

    requested_sections = GUARDIAN_API_SECTIONS if sections is None else sections
    allowed_sections = filter_guardian_sections(requested_sections)
    params = {
        "api-key": resolved_api_key,
        "order-by": order_by,
        "from-date": __import__("datetime").date.today().isoformat(),
        "page-size": page_size,
        "show-fields": "bodyText,trailText,headline",
        "show-tags": "all",
    }
    if allowed_sections:
        params["section"] = "|".join(allowed_sections)
    if tag is not None:
        params["tag"] = tag

    response = requests.get("https://content.guardianapis.com/search", params=params, timeout=30)
    response.raise_for_status()
    results = response.json()["response"]["results"]

    payloads: list[dict] = []
    for result in results:
        fields = result.get("fields") or {}
        title = fields.get("headline") or result["webTitle"]
        body = fields.get("bodyText") or fields.get("body") or fields.get("trailText") or ""
        tags = result.get("tags") or []
        if should_drop_article(tags):
            continue
        if len(body) < min_body_len:
            continue
        description = extract_guardian_description(body, tags)
        if not description:
            continue
        url = result["webUrl"]
        if is_url_seen(url, db_path):
            continue
        payloads.append(
            {
                "title": title,
                "description": description,
                "pub_time": result["webPublicationDate"],
                "source_name": f"The Guardian | {result.get('sectionName', '')}",
                "url": url,
                "id": result.get("id"),
                "api_url": result.get("apiUrl"),
            }
        )

    return payloads


NEWS_KEYS = ("title", "description", "pub_time", "source_name", "url")
DEFAULT_LIMIT = 30
_TITLE_DISPLAY_LIMIT = 80


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be an integer >= 1") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be >= 1")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    """Build the fetch_news CLI parser."""

    parser = argparse.ArgumentParser(
        description="Fetch Guardian API news candidates automatically, or use RSS/debug overrides."
    )
    parser.add_argument(
        "--limit",
        type=_positive_int,
        default=DEFAULT_LIMIT,
        help=f"maximum candidates to print in list mode (default: {DEFAULT_LIMIT})",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="write the full deduplicated candidate pool as JSON",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        help="write the selected news JSON to this path instead of stdout",
    )
    parser.add_argument(
        "--provider",
        choices=["rss", "guardian-api"],
        default="guardian-api",
        help="news provider to use in candidate list mode (default: guardian-api)",
    )
    parser.add_argument(
        "--sections",
        help="comma-separated Guardian API sections; defaults to blacklist-filtered broad sections",
    )
    parser.add_argument(
        "--order-by",
        default="newest",
        help="Guardian API order-by value (default: newest)",
    )
    parser.add_argument("--tag", default=None, help="optional Guardian API tag filter")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--pick",
        type=_positive_int,
        help="1-based candidate number to output and mark as seen",
    )
    mode.add_argument(
        "--url",
        help="single article/feed URL bypassing the RSS candidate list",
    )
    parser.add_argument("--title", help="fallback title for --url")
    parser.add_argument("--description", help="fallback description for --url")
    parser.add_argument("--source-name", help="optional source name for --url fallback")
    parser.add_argument("--pub-time", help="optional publication time for --url fallback")
    return parser


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    return build_parser().parse_args(argv)


def _parse_sections_arg(value: str | None) -> list[str] | None:
    if value is None:
        return None
    sections = [section.strip() for section in value.split(",") if section.strip()]
    return sections or None


def _parse_pub_time(value: Any) -> datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    text = value.strip()
    if text.endswith("Z"):
        text = f"{text[:-1]}+00:00"
    try:
        parsed = datetime.fromisoformat(text)
    except ValueError:
        return None
    if parsed.tzinfo is None:
        return parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def sort_entries_by_pub_time(entries: list[dict]) -> list[dict]:
    """Return candidates sorted by pub_time descending; missing/invalid dates stay last."""

    def sort_key(item: dict) -> tuple[int, float]:
        parsed = _parse_pub_time(item.get("pub_time"))
        if parsed is None:
            return (1, 0.0)
        return (0, -parsed.timestamp())

    return sorted(entries, key=sort_key)


def _display_date(pub_time: Any) -> str:
    parsed = _parse_pub_time(pub_time)
    if parsed is not None:
        return parsed.date().isoformat()
    if isinstance(pub_time, str) and pub_time.strip():
        return pub_time.strip()
    return "-"


def _display_text(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return _WHITESPACE_RE.sub(" ", value.strip())
    return fallback


def _truncate(text: str, limit: int = _TITLE_DISPLAY_LIMIT) -> str:
    if len(text) <= limit:
        return text
    return f"{text[: max(0, limit - 1)].rstrip()}…"


def render_news_list(entries: list[dict], *, limit: int = DEFAULT_LIMIT) -> str:
    """Render numbered candidates for a human editor."""

    lines: list[str] = []
    for index, entry in enumerate(entries[:limit], start=1):
        date = _display_date(entry.get("pub_time"))
        source = _display_text(entry.get("source_name"), "Unknown Source")
        title = _truncate(_display_text(entry.get("title"), "Untitled"))
        url = _display_text(entry.get("url"), "-")
        lines.append(f"[{index}] {date} · {source} · {title}")
        lines.append(f"    {url}")
    if not lines:
        return "No new news candidates."
    return "\n".join(lines)


def _news_json_payload(entry: dict) -> dict[str, str | int | None]:
    return {key: entry.get(key) for key in NEWS_KEYS}


def write_json(payload: Any, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def emit_news_json(
    entry: dict,
    *,
    out_json: Path | None = None,
    stdout: TextIO | None = None,
) -> dict[str, str | int | None]:
    payload = _news_json_payload(entry)
    if out_json is not None:
        write_json(payload, out_json)
    else:
        stream = sys.stdout if stdout is None else stdout
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=stream)
    return payload


def fetch_candidate_pool(db_path: Path | None = None) -> list[dict]:
    """Fetch, URL-deduplicate, and sort the candidate pool."""

    entries = fetch_all_entries()
    return sort_entries_by_pub_time(filter_new_entries(entries, db_path=db_path))


def build_url_news_payload(
    url: str,
    *,
    title: str | None = None,
    description: str | None = None,
    source_name: str | None = None,
    pub_time: str | None = None,
) -> dict[str, str | None]:
    """Resolve a single URL to a news payload, using title/description fallback when needed."""

    parse_error: Exception | None = None
    try:
        parsed_feed = feedparser.parse(url)
        source = _source_name(parsed_feed, url)
        entries = _get_value(parsed_feed, "entries", []) or []
        if entries:
            payload = _entry_to_payload(entries[0], source)
            if payload is not None:
                return payload
    except Exception as exc:  # noqa: BLE001 - CLI must report cleanly, not traceback
        parse_error = exc

    clean_title = title.strip() if isinstance(title, str) else ""
    clean_description = _strip_html(description) if isinstance(description, str) else ""
    if not clean_title or not clean_description:
        detail = f" Parse error: {parse_error}" if parse_error is not None else ""
        raise ValueError(
            "Unable to parse required title/description from --url; "
            "please provide both --title and --description." + detail
        )

    return {
        "title": clean_title,
        "description": clean_description,
        "pub_time": pub_time.strip() if isinstance(pub_time, str) and pub_time.strip() else None,
        "source_name": source_name.strip()
        if isinstance(source_name, str) and source_name.strip()
        else None,
        "url": url.strip(),
    }


def run_cli(
    argv: list[str] | None = None,
    *,
    db_path: Path | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """Run CLI logic with injectable streams/database path for tests."""

    args = parse_args(argv)
    out = sys.stdout if stdout is None else stdout
    err = sys.stderr if stderr is None else stderr

    if args.url:
        try:
            entry = build_url_news_payload(
                args.url,
                title=args.title,
                description=args.description,
                source_name=args.source_name,
                pub_time=args.pub_time,
            )
        except ValueError as exc:
            print(f"Error: {exc}", file=err)
            return 1
        emit_news_json(entry, out_json=args.out_json, stdout=out)
        mark_selected(entry, db_path=db_path)
        return 0

    if args.provider == "guardian-api":
        candidates = fetch_guardian_api(
            sections=_parse_sections_arg(args.sections),
            order_by=args.order_by,
            tag=args.tag,
            db_path=db_path,
        )
    else:
        candidates = fetch_candidate_pool(db_path=db_path)
    if args.out is not None:
        write_json(candidates, args.out)

    if args.pick is not None:
        pick_index = args.pick - 1
        if pick_index >= len(candidates):
            print(
                f"Error: --pick {args.pick} is out of range; "
                f"only {len(candidates)} candidate(s) available.",
                file=err,
            )
            return 1
        selected = candidates[pick_index]
        emit_news_json(selected, out_json=args.out_json, stdout=out)
        mark_selected(selected, db_path=db_path)
        return 0

    selected_candidates = candidates[: args.limit]
    if args.out_json is not None:
        write_json([_news_json_payload(entry) for entry in selected_candidates], args.out_json)
    else:
        print(
            json.dumps(
                [_news_json_payload(entry) for entry in selected_candidates],
                ensure_ascii=False,
                indent=2,
            ),
            file=out,
        )
    return 0


def main(argv: list[str] | None = None) -> None:
    raise SystemExit(run_cli(argv))


if __name__ == "__main__":
    main()
