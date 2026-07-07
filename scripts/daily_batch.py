"""daily_batch.py · Daily Batch 编排器 + 断点续跑 (Phase 7.2).

链路（复用 Phase 6 单条管线的下层 stage 函数，语义与 main.py 保持一致）:

  heat_pool.fetch_heat_pool() → batch_state 初始化
    → for each item:
        deconstruct(A0) → expand(P-Expand，可 --skip-expand)
        → persona_pipeline × N（可 --personas 限制，逐个 persona 落盘 checkpoint）
        → retrieve_from_agents → compose.run_review(C1) → briefing.md
        → 每完成一个 stage / persona 立即原子写 state/daily_batch_{date}.json

状态流转：pending → deconstruct → expand → persona → retrieve → compose → done

断点续跑：
  - item 级：status == "done" 的 item 直接跳过。
  - stage 级：已完成的 stage 产物（deconstruct.json / expand.json / retrieve.json /
    briefing.md）落在 output/daily_batch/{date}/{NN}-{slug}/ 下，resume 时优先从磁盘
    加载，不重新调用 LLM。
  - persona 级：personas/{persona_id}.json 存在且 persona_id 已在
    state.items[i].completed_personas 中时跳过，只补跑剩余 persona。

产出目录：output/daily_batch/{date}/{NN}-{slug}/
State 文件：state/daily_batch_{date}.json（.tmp + os.replace 原子写）
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import compose
from scripts.agents import NewsItem, news_to_dict
from scripts.extract import run_deconstruct
from scripts.heat_pool import DEFAULT_MIN_COUNT, RANKED_SECTIONS, fetch_heat_pool, pool_output_path
from scripts.lib.env import default_llm_provider
from scripts.lib.llm import get_llm_client
from scripts.lib.paths import repo_root, state_dir
from scripts.lib.run_options import RunOptions
from scripts.llm_judge import JudgeItem, call_llm_judge, score_items
from scripts.retrieve import retrieve_from_agents
from scripts.rewrite import list_persona_ids, pipeline_result_to_dict, run_persona_pipeline

# 状态流转顺序（用于日志 / 校验，实际续跑判断以磁盘产物 + completed_personas 为准）。
STAGE_ORDER: tuple[str, ...] = (
    "pending",
    "deconstruct",
    "expand",
    "persona",
    "retrieve",
    "compose",
    "done",
)

_MIN_DESCRIPTION_CHARS = 24


def _has_sufficient_description(entry: dict[str, Any]) -> bool:
    description = str(entry.get("description") or "").strip()
    if len(description) < _MIN_DESCRIPTION_CHARS:
        return False
    title = str(entry.get("title") or "").strip()
    return description.lower() != title.lower()


def _item_is_fully_complete(item_state: BatchItemState) -> bool:
    return item_state.status == "done" and item_state.last_completed_stage == "compose"


def _progress(message: str) -> None:
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    print(f"{ts} {message}", file=sys.stderr, flush=True)


_SLUG_WORD_COUNT = 6
_SLUG_STRIP_RE = re.compile(r"[^a-z0-9\s-]")
_SLUG_WS_RE = re.compile(r"\s+")


def slugify(title: str, *, max_words: int = _SLUG_WORD_COUNT) -> str:
    """title → lowercase，去标点，取前 max_words 个词，连字符连接。

    空标题 / 全标点标题回退为 "untitled"，保证目录名永不为空。
    """
    lowered = (title or "").strip().lower()
    cleaned = _SLUG_STRIP_RE.sub("", lowered)
    words = [w for w in _SLUG_WS_RE.split(cleaned.strip()) if w]
    slug = "-".join(words[:max_words])
    return slug or "untitled"


def _today_iso() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%d")


def batch_output_dir(date: str, out_dir: Path | None = None) -> Path:
    base = out_dir or (repo_root() / "output" / "daily_batch")
    return base / date


def item_dir(date: str, index: int, slug: str, out_dir: Path | None = None) -> Path:
    return batch_output_dir(date, out_dir) / f"{index + 1:02d}-{slug}"


def state_path(date: str, base_state_dir: Path | None = None) -> Path:
    base = base_state_dir if base_state_dir is not None else state_dir()
    return base / f"daily_batch_{date}.json"


def _atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    """原子写：先写 .tmp，再 os.replace，避免中断产出半截 state 文件。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(tmp_path, path)


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")



def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _judge_scores_path(item_out_dir: Path) -> Path:
    return item_out_dir / "llm-judge-scores.json"


def _candidate_overview(candidate: dict[str, Any]) -> str:
    overview = str(candidate.get("overview") or "").strip()
    if overview:
        return overview
    db_projection = compose._db_projection_for_candidate(candidate)
    return str(db_projection.get("overview") or "").strip()


def _build_judge_items(
    *,
    run_id: str,
    news_dict: dict[str, Any],
    retrieve_result: dict[str, Any],
) -> list[JudgeItem]:
    candidates = [c for c in retrieve_result.get("candidates") or [] if isinstance(c, dict)]
    return [
        JudgeItem(
            run_id=run_id,
            tmdb_id=str(cand.get("tmdb_id") or ""),
            title=str(cand.get("title") or ""),
            news_title=str(news_dict.get("title") or ""),
            news_summary=str(news_dict.get("description") or ""),
            movie_overview=_candidate_overview(cand),
        )
        for cand in candidates
        if str(cand.get("tmdb_id") or "").strip()
    ]


def _load_or_generate_judge_scores(
    *,
    item_out_dir: Path,
    run_id: str,
    news_dict: dict[str, Any],
    retrieve_result: dict[str, Any],
    provider: str | None,
) -> tuple[Path, bool]:
    """Materialize judge scores so compose can backfill rationale by tmdb_id."""
    judge_path = _judge_scores_path(item_out_dir)
    if judge_path.is_file():
        return judge_path, False

    judge_items = _build_judge_items(
        run_id=run_id,
        news_dict=news_dict,
        retrieve_result=retrieve_result,
    )
    if not judge_items:
        payload = {"version": 4, "calibration": {}, "scores": []}
        _write_json(judge_path, payload)
        return judge_path, True

    judge_output = score_items(
        judge_items,
        lambda item: call_llm_judge(item, provider=provider),
        observation_run_ids=[],
        workers=min(4, len(judge_items)),
    )
    _write_json(judge_path, judge_output.to_dict())
    return judge_path, True


_JUDGE_RATIONALE_FALLBACK_RE = re.compile(r"^- tmdb:(?P<tmdb_id>\d+):\s*(?P<text>.*)$")


def _news_briefing_body_text(news_dict: dict[str, Any]) -> str:
    """Prefer the downstream excerpt/body text, then fallback to other summary fields."""
    for key in ("excerpt", "body", "content", "summary", "description", "text"):
        value = str(news_dict.get(key) or "").strip()
        if value:
            return value
    return ""


def _candidate_year(candidate: dict[str, Any]) -> str:
    year = candidate.get("release_year")
    if year:
        return str(year)
    release_date = str(candidate.get("release_date") or "").strip()
    if len(release_date) >= 4 and release_date[:4].isdigit():
        return release_date[:4]
    return ""


def _candidate_title_line(candidate: dict[str, Any]) -> str:
    title = str(candidate.get("title") or "Untitled").strip() or "Untitled"
    year = _candidate_year(candidate)
    year_part = f" ({year})" if year else ""
    tmdb_id = str(candidate.get("tmdb_id") or "").strip()
    tmdb_part = f" [tmdb:{tmdb_id}]" if tmdb_id else ""
    return f"candidate {title}{year_part}{tmdb_part}"


def _load_review_copy_fallbacks(briefing_path: Path) -> dict[str, str]:
    if not briefing_path.is_file():
        return {}
    text = briefing_path.read_text(encoding="utf-8")
    if "## Review copies" not in text:
        return {}
    review_block = text.split("## Review copies", 1)[1].split("\n## ", 1)[0]
    fallbacks: dict[str, str] = {}
    for raw_line in review_block.splitlines():
        match = _JUDGE_RATIONALE_FALLBACK_RE.match(raw_line.strip())
        if match:
            tmdb_id = match.group("tmdb_id")
            text_value = match.group("text").strip()
            if text_value:
                fallbacks[tmdb_id] = text_value
    return fallbacks




_BRIEFING_ZH_TRANSLATION_CACHE_VERSION = 1
_BRIEFING_ZH_TRANSLATION_CACHE_NAME = "briefing.zh.translations.json"


def _briefing_zh_cache_path(date_dir: Path) -> Path:
    return date_dir / _BRIEFING_ZH_TRANSLATION_CACHE_NAME


def _load_briefing_zh_cache(date_dir: Path) -> dict[str, Any]:
    path = _briefing_zh_cache_path(date_dir)
    if not path.is_file():
        return {"version": _BRIEFING_ZH_TRANSLATION_CACHE_VERSION, "overview": {}, "rationale": {}}
    payload = _read_json(path)
    if not isinstance(payload, dict):
        return {"version": _BRIEFING_ZH_TRANSLATION_CACHE_VERSION, "overview": {}, "rationale": {}}
    payload.setdefault("version", _BRIEFING_ZH_TRANSLATION_CACHE_VERSION)
    payload.setdefault("overview", {})
    payload.setdefault("rationale", {})
    return payload


def _save_briefing_zh_cache(date_dir: Path, cache: dict[str, Any]) -> None:
    _write_json(_briefing_zh_cache_path(date_dir), cache)

def _load_judge_rows_by_tmdb(judge_scores_path: Path) -> dict[str, dict[str, Any]]:
    if not judge_scores_path.is_file():
        return {}
    payload = _read_json(judge_scores_path)
    rows = payload.get("scores") if isinstance(payload, dict) else []
    judge_rows: dict[str, dict[str, Any]] = {}
    for row in rows or []:
        if not isinstance(row, dict):
            continue
        tmdb_id = str(row.get("tmdb_id") or "").strip()
        if tmdb_id:
            judge_rows[tmdb_id] = row
    return judge_rows


def _candidate_judge_row(
    candidate: dict[str, Any], judge_rows: dict[str, dict[str, Any]]
) -> dict[str, Any]:
    tmdb_id = str(candidate.get("tmdb_id") or "").strip()
    return judge_rows.get(tmdb_id, {}) if tmdb_id else {}


def _candidate_judge_score(candidate: dict[str, Any], judge_rows: dict[str, dict[str, Any]]) -> int | None:
    row = _candidate_judge_row(candidate, judge_rows)
    score = row.get("judge_score")
    if isinstance(score, bool):
        return None
    if isinstance(score, int):
        return score
    if isinstance(score, float) and score.is_integer():
        return int(score)
    try:
        return int(score)
    except (TypeError, ValueError):
        return None


def _candidate_sort_key(
    candidate: dict[str, Any],
    *,
    original_index: int,
    judge_rows: dict[str, dict[str, Any]],
) -> tuple[int, int]:
    score = _candidate_judge_score(candidate, judge_rows)
    sortable_score = score if score is not None else -1
    return (-sortable_score, original_index)


def _candidate_resonance_agents(
    candidate: dict[str, Any],
    retrieve_result: dict[str, Any],
) -> list[str]:
    agents: list[str] = []

    def add_many(values: Any) -> None:
        if isinstance(values, str):
            values = [values]
        if not isinstance(values, list):
            return
        for value in values:
            agent_id = str(value or "").strip().upper()
            if agent_id and agent_id not in agents:
                agents.append(agent_id)

    add_many(candidate.get("triggered_by"))
    match_diagnostics = candidate.get("match_diagnostics")
    if isinstance(match_diagnostics, dict):
        add_many(match_diagnostics.get("triggered_by"))
        add_many(match_diagnostics.get("agent_ids"))
        add_many(match_diagnostics.get("agents"))
        add_many(match_diagnostics.get("resonance_agents"))
    add_many(candidate.get("agents"))
    add_many(candidate.get("agent_ids"))
    for source in candidate.get("hit_sources") or []:
        if not isinstance(source, dict):
            continue
        add_many([source.get("agent_id")])

    if agents:
        return agents

    per_agent = retrieve_result.get("per_agent") or []
    if isinstance(per_agent, list):
        target_tmdb = str(candidate.get("tmdb_id") or "").strip()
        for agent in per_agent:
            if not isinstance(agent, dict):
                continue
            agent_id = str(agent.get("agent_id") or "").strip().upper()
            if not agent_id:
                continue
            for pseudo in agent.get("pseudos") or []:
                if not isinstance(pseudo, dict):
                    continue
                hits = pseudo.get("hits") or []
                for hit in hits:
                    if not isinstance(hit, dict):
                        continue
                    if str(hit.get("tmdb_id") or "").strip() == target_tmdb:
                        if agent_id not in agents:
                            agents.append(agent_id)
                        break
                if agent_id in agents:
                    break
    return agents




def _text_looks_like_zh(text: str) -> bool:
    zh_count = len(re.findall(r"[\u4e00-\u9fff]", str(text or "")))
    if zh_count == 0:
        return False
    latin_count = len(re.findall(r"[A-Za-z]", str(text or "")))
    return zh_count >= max(2, latin_count // 2)


def _translate_texts_to_zh(
    texts: list[str],
    *,
    kind: str,
    date_dir: Path,
    provider: str | None = None,
) -> dict[str, str]:
    unique_texts = []
    seen: set[str] = set()
    for text in texts:
        cleaned = str(text or "").strip()
        if cleaned and cleaned not in seen:
            seen.add(cleaned)
            unique_texts.append(cleaned)
    if not unique_texts:
        return {}

    cache = _load_briefing_zh_cache(date_dir)
    bucket = cache.setdefault(kind, {})
    if not isinstance(bucket, dict):
        bucket = {}
        cache[kind] = bucket

    for text in list(unique_texts):
        if _text_looks_like_zh(text):
            bucket[text] = text

    missing = [text for text in unique_texts if text not in bucket]
    if missing:
        resolved_provider = (provider or default_llm_provider()).strip().lower()
        model_env = {
            "mimo": "MIMO_MODEL",
            "deepseek": "DEEPSEEK_MODEL",
        }.get(resolved_provider)
        model = os.getenv(model_env or "", "").strip() if model_env else ""
        if not model:
            raise RuntimeError("Missing LLM model env for briefing translation")
        system = "你是忠实翻译器。只做简体中文翻译，不要改写、补充或总结。"
        client = get_llm_client(resolved_provider)

        def _strip_response_fence(raw_text: str) -> str:
            text = raw_text.strip()
            fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.S | re.I)
            if fence:
                return fence.group(1).strip()
            return text

        def _coerce_translation_value(value: Any) -> str:
            if isinstance(value, dict):
                for key in ("translation", "translated", "zh", "target", "text", "value"):
                    nested = str(value.get(key) or "").strip()
                    if nested:
                        return nested
                return ""
            return str(value or "").strip()

        def _translation_looks_rejected(value: str) -> bool:
            lowered = value.lower()
            return any(
                marker in lowered
                for marker in (
                    "request was rejected",
                    "considered high risk",
                    "i can't assist",
                    "i cannot assist",
                    "cannot comply",
                    "无法处理",
                    "不能处理",
                    "无法翻译",
                )
            )

        def _parse_translation_response(raw_text: str, batch: list[str]) -> list[str] | None:
            cleaned = _strip_response_fence(raw_text)
            parsed: Any | None = None
            for candidate in (cleaned,):
                try:
                    parsed = json.loads(candidate)
                    break
                except json.JSONDecodeError:
                    parsed = None
            if parsed is None:
                json_block = re.search(r"(\[[\s\S]*\]|\{[\s\S]*\})", cleaned)
                if json_block:
                    try:
                        parsed = json.loads(json_block.group(1))
                    except json.JSONDecodeError:
                        parsed = None

            values: list[str] | None = None
            if isinstance(parsed, list):
                values = [_coerce_translation_value(item) for item in parsed]
            elif isinstance(parsed, dict):
                for key in ("translations", "translated", "items", "results", "texts"):
                    nested = parsed.get(key)
                    if isinstance(nested, list):
                        values = [_coerce_translation_value(item) for item in nested]
                        break
                if values is None:
                    numeric_values = [_coerce_translation_value(parsed.get(str(i))) for i in range(len(batch))]
                    if all(numeric_values):
                        values = numeric_values
                if values is None:
                    source_values = [_coerce_translation_value(parsed.get(source)) for source in batch]
                    if all(source_values):
                        values = source_values

            if values is None:
                lines = []
                for line in cleaned.splitlines():
                    stripped = re.sub(r"^[-*\d.、)\s]+", "", line).strip()
                    if stripped:
                        lines.append(stripped)
                values = lines

            if len(values) == len(batch) and all(values) and not any(_translation_looks_rejected(value) for value in values):
                return values
            if len(batch) == 1 and cleaned and not _translation_looks_rejected(cleaned):
                return [cleaned.strip().strip('"')]
            return None

        def _request_translation_batch(batch: list[str]) -> list[str] | None:
            user = (
                "请把下面的英文文本逐条翻译成简体中文，保持原有含义和语气，不要添加解释。"
                "返回严格 JSON 对象：{\"translations\":[...]}，数组顺序必须与输入一致。\n\n"
                f"kind: {kind}\n"
                f"texts: {json.dumps(batch, ensure_ascii=False)}"
            )
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            )
            raw = (response.choices[0].message.content or "").strip()
            return _parse_translation_response(raw, batch)

        chunk_size = 6
        for start in range(0, len(missing), chunk_size):
            batch = missing[start : start + chunk_size]
            translated = _request_translation_batch(batch)
            if translated is None and len(batch) > 1:
                translated = []
                for source in batch:
                    single = _request_translation_batch([source])
                    translated.append((single or [source])[0])
            if translated is None or len(translated) != len(batch):
                translated = batch
            for source, target in zip(batch, translated):
                bucket[source] = target or source
            _save_briefing_zh_cache(date_dir, cache)

    return {text: str(bucket.get(text) or text) for text in unique_texts}


def _translate_texts_to_zh_safe(
    texts: list[str],
    *,
    kind: str,
    date_dir: Path,
    provider: str | None = None,
) -> dict[str, str]:
    """Translate only non-Chinese unique texts; preserve Chinese text as-is."""
    unique_texts: list[str] = []
    direct_map: dict[str, str] = {}
    seen: set[str] = set()
    for text in texts:
        cleaned = str(text or "").strip()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        if _text_looks_like_zh(cleaned):
            direct_map[cleaned] = cleaned
        else:
            unique_texts.append(cleaned)
    translated = _translate_texts_to_zh(unique_texts, kind=kind, date_dir=date_dir, provider=provider)
    direct_map.update(translated)
    return direct_map





_BRIEFING_LABELS_EN = {
    "news_title": "",
    "news_body": "",
    "candidate": "candidate",
    "overview": "",
    "score": "llm_judge_score",
    "rationale": "llm_judge_rationale",
}

_BRIEFING_LABELS_ZH = {
    "news_title": "新闻标题",
    "news_body": "新闻正文",
    "candidate": "候选电影",
    "overview": "剧情简介",
    "score": "LLM judge 分数",
    "rationale": "LLM judge 理由",
}


def _candidate_overview_text(candidate: dict[str, Any], *, zh: bool) -> str:
    if zh:
        for key in ("overview_zh", "zh_overview", "overview_cn", "cn_overview"):
            value = str(candidate.get(key) or "").strip()
            if value:
                return value
    return _candidate_overview(candidate)


def _candidate_rationale_text(
    candidate: dict[str, Any],
    *,
    judge_row: dict[str, Any],
    review_copy_fallbacks: dict[str, str],
) -> str:
    tmdb_id = str(candidate.get("tmdb_id") or "").strip()
    rationale = str(judge_row.get("rationale") or "").strip()
    if rationale:
        return rationale
    for key in ("rationale_zh", "judge_rationale_zh", "rationale_cn", "cn_rationale"):
        value = str(judge_row.get(key) or "").strip()
        if value:
            return value
    if tmdb_id:
        fallback = review_copy_fallbacks.get(tmdb_id, "").strip()
        if fallback:
            return fallback
    return ""


def _render_candidate_briefing_lines(
    candidate: dict[str, Any],
    *,
    judge_rows: dict[str, dict[str, Any]],
    review_copy_fallbacks: dict[str, str],
    retrieve_result: dict[str, Any],
    labels: dict[str, str],
    zh_overview_map: dict[str, str] | None = None,
    zh_rationale_map: dict[str, str] | None = None,
) -> list[str]:
    tmdb_id = str(candidate.get("tmdb_id") or "").strip()
    judge_row = judge_rows.get(tmdb_id, {}) if tmdb_id else {}
    rationale = _candidate_rationale_text(
        candidate,
        judge_row=judge_row,
        review_copy_fallbacks=review_copy_fallbacks,
    )
    score = judge_row.get("judge_score")
    score_text = str(score) if score is not None else "—"
    candidate_line = f"{labels['candidate']} {_candidate_title_line(candidate).removeprefix('candidate ').strip()}"
    overview_source = _candidate_overview_text(candidate, zh=False)
    overview_text = overview_source or "—"
    rationale_text = rationale or "—"
    if zh_overview_map is not None and overview_source:
        overview_text = zh_overview_map.get(overview_source, overview_text)
    if zh_rationale_map is not None and rationale:
        rationale_text = zh_rationale_map.get(rationale, rationale_text)
    agents = _candidate_resonance_agents(candidate, retrieve_result)
    resonance_text = ", ".join(agents) if agents else "—"
    lines = [
        candidate_line,
        f"共振agent(s): {resonance_text}",
        f"{labels['overview'] + ': ' if labels['overview'] else ''}{overview_text}",
        f"{labels['score']}: {score_text}",
        f"{labels['rationale']}: {rationale_text}",
        "",
    ]
    return lines


def _render_daily_batch_briefing(
    date_dir: Path,
    *,
    labels: dict[str, str],
    zh: bool = False,
) -> str:
    """Render the date-root briefing by aggregating item subdirs."""
    lines: list[str] = []
    item_dirs = sorted(
        (path for path in date_dir.iterdir() if path.is_dir() and re.match(r"^\d{2}-", path.name)),
        key=lambda path: path.name,
    )
    for item_dir_path in item_dirs:
        news_path = item_dir_path / "news.json"
        retrieve_path = item_dir_path / "retrieve.json"
        if not news_path.is_file() or not retrieve_path.is_file():
            continue
        news_dict = _read_json(news_path)
        retrieve_result = _read_json(retrieve_path)
        judge_rows = _load_judge_rows_by_tmdb(_judge_scores_path(item_dir_path))
        review_copy_fallbacks = _load_review_copy_fallbacks(item_dir_path / "briefing.md")

        candidates = [cand for cand in retrieve_result.get("candidates") or [] if isinstance(cand, dict)]
        ranked_candidates = [
            cand
            for cand, _ in sorted(
                ((cand, idx) for idx, cand in enumerate(candidates)),
                key=lambda pair: _candidate_sort_key(pair[0], original_index=pair[1], judge_rows=judge_rows),
            )
            if _candidate_judge_score(cand, judge_rows) not in (None, 0)
        ]

        if lines:
            lines.append("")
        title = str(news_dict.get("title") or "").strip()
        if zh and title:
            title = _translate_texts_to_zh_safe(
                [title], kind="news_title", date_dir=date_dir
            ).get(title, title)
        if labels["news_title"]:
            lines.append(f"{labels['news_title']}: {title}")
        else:
            lines.append(title)
        news_body = _news_briefing_body_text(news_dict)
        if news_body:
            if zh:
                translated_news_body = _translate_texts_to_zh_safe(
                    [news_body], kind="news_body", date_dir=date_dir
                ).get(news_body, news_body)
                lines.append(f"{labels['news_body']}: {translated_news_body}")
            elif labels["news_body"]:
                lines.append(f"{labels['news_body']}: {news_body}")
            else:
                lines.append(news_body)
        lines.append("")

        zh_overview_map: dict[str, str] | None = None
        zh_rationale_map: dict[str, str] | None = None
        if zh and ranked_candidates:
            overview_sources = [
                _candidate_overview_text(candidate, zh=False) for candidate in ranked_candidates
            ]
            rationale_sources = [
                _candidate_rationale_text(
                    candidate,
                    judge_row=judge_rows.get(str(candidate.get("tmdb_id") or "").strip(), {}),
                    review_copy_fallbacks=review_copy_fallbacks,
                )
                for candidate in ranked_candidates
            ]
            zh_overview_map = _translate_texts_to_zh_safe(
                overview_sources, kind="overview", date_dir=date_dir
            )
            zh_rationale_map = _translate_texts_to_zh_safe(
                rationale_sources, kind="rationale", date_dir=date_dir
            )

        for candidate in ranked_candidates:
            lines.extend(
                _render_candidate_briefing_lines(
                    candidate,
                    judge_rows=judge_rows,
                    review_copy_fallbacks=review_copy_fallbacks,
                    retrieve_result=retrieve_result,
                    labels=labels,
                    zh_overview_map=zh_overview_map,
                    zh_rationale_map=zh_rationale_map,
                )
            )
    return "\n".join(lines).rstrip() + "\n"


def render_daily_batch_briefing(date_dir: Path) -> str:
    return _render_daily_batch_briefing(date_dir, labels=_BRIEFING_LABELS_EN, zh=False)


def render_daily_batch_briefing_zh(date_dir: Path) -> str:
    return _render_daily_batch_briefing(date_dir, labels=_BRIEFING_LABELS_ZH, zh=True)


def write_daily_batch_briefing(date_dir: Path) -> Path:
    path = date_dir / "briefing.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_daily_batch_briefing(date_dir), encoding="utf-8")
    zh_path = date_dir / "briefing.zh.md"
    zh_path.write_text(render_daily_batch_briefing_zh(date_dir), encoding="utf-8")
    return path


@dataclass
class BatchItemState:
    """单条 news 的批处理状态（对应 state.items[i]）。"""

    index: int
    url: str
    title: str
    slug: str
    status: str = "pending"
    last_completed_stage: str | None = None
    completed_personas: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "url": self.url,
            "title": self.title,
            "slug": self.slug,
            "status": self.status,
            "last_completed_stage": self.last_completed_stage,
            "completed_personas": list(self.completed_personas),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BatchItemState":
        return cls(
            index=int(data["index"]),
            url=str(data.get("url") or ""),
            title=str(data.get("title") or ""),
            slug=str(data.get("slug") or ""),
            status=str(data.get("status") or "pending"),
            last_completed_stage=data.get("last_completed_stage"),
            completed_personas=list(data.get("completed_personas") or []),
        )


@dataclass
class BatchState:
    """整个 daily batch 的状态（对应 state/daily_batch_{date}.json）。"""

    date: str
    pool_file: str
    created_at: str
    parallel_baseline: dict[str, Any] = field(default_factory=dict)
    items: list[BatchItemState] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "date": self.date,
            "pool_file": self.pool_file,
            "created_at": self.created_at,
            "parallel_baseline": dict(self.parallel_baseline),
            "items": [it.to_dict() for it in self.items],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BatchState":
        return cls(
            date=str(data["date"]),
            pool_file=str(data.get("pool_file") or ""),
            created_at=str(data.get("created_at") or ""),
            parallel_baseline=dict(data.get("parallel_baseline") or {}),
            items=[BatchItemState.from_dict(it) for it in data.get("items") or []],
        )

    def save(self, path: Path) -> None:
        _atomic_write_json(path, self.to_dict())


def init_batch_state(date: str, pool: list[dict[str, Any]], pool_file: str) -> BatchState:
    """从 heat_pool 的 ranked pool 构造初始 batch_state（全部 pending）。"""
    items = [
        BatchItemState(
            index=idx,
            url=str(entry.get("url") or ""),
            title=str(entry.get("title") or ""),
            slug=slugify(str(entry.get("title") or "")),
        )
        for idx, entry in enumerate(pool)
    ]
    return BatchState(
        date=date,
        pool_file=pool_file,
        created_at=datetime.now(UTC).isoformat(timespec="seconds"),
        parallel_baseline={},
        items=items,
    )


def load_batch_state(path: Path) -> BatchState:
    return BatchState.from_dict(_read_json(path))


def _news_item_for_pool_entry(entry: dict[str, Any]) -> NewsItem:
    return NewsItem(
        title=str(entry.get("title") or ""),
        description=str(entry.get("description") or ""),
        pub_time=str(entry.get("pub_time") or ""),
        source_name=str(entry.get("source_name") or "Guardian"),
        url=str(entry.get("url") or ""),
    )


def _persona_result_to_agent(result: Any) -> dict[str, Any]:
    """Convert a persona pipeline result into retrieve-facing agent dict."""
    payload = pipeline_result_to_dict(result)
    pseudos = payload.get("pseudos") or []
    agent: dict[str, Any] = {
        "agent_id": result.persona_id,
        "persona_name": result.persona_id,
        "role": "persona",
        "pseudos": pseudos,
        "text": str(pseudos[0].get("text", "")) if pseudos else "",
        "warnings": list(result.warnings or []),
    }
    if payload.get("search_units"):
        agent["search_units"] = payload["search_units"]
    if payload.get("fragment_ladders"):
        agent["fragment_ladders"] = payload["fragment_ladders"]
    return agent


def _persona_agent_dict_to_dict(agent: dict[str, Any]) -> dict[str, Any]:
    """Resume path stores the retrieve-facing agent dict directly."""
    return agent


def _parallel_baseline_summary(run_options: RunOptions) -> str:
    """Return a compact, human-readable parallel baseline summary."""
    return (
        f"item={run_options.item_concurrency} "
        f"persona={run_options.persona_concurrency} "
        f"global_llm={run_options.global_llm_concurrency} "
        f"rpm={run_options.global_rpm_budget} "
        f"tpm={run_options.global_tpm_budget} "
        f"retry={run_options.retry_attempts} "
        f"backoff={run_options.backoff}"
    )


def _parallel_baseline(run_options: RunOptions) -> dict[str, Any]:
    return {
        "item_concurrency": run_options.item_concurrency,
        "persona_concurrency": run_options.persona_concurrency,
        "global_llm_concurrency": run_options.global_llm_concurrency,
        "global_rpm_budget": run_options.global_rpm_budget,
        "global_tpm_budget": run_options.global_tpm_budget,
        "retry_attempts": run_options.retry_attempts,
        "backoff": run_options.backoff,
    }


def _validate_parallel_baseline(run_options: RunOptions) -> None:
    if run_options.item_concurrency <= 0:
        raise ValueError(f"item_concurrency must be a positive integer, got {run_options.item_concurrency}")
    if run_options.persona_concurrency <= 0:
        raise ValueError(
            f"persona_concurrency must be a positive integer, got {run_options.persona_concurrency}"
        )
    if run_options.global_llm_concurrency <= 0:
        raise ValueError(
            f"global_llm_concurrency must be a positive integer, got {run_options.global_llm_concurrency}"
        )
    if run_options.global_rpm_budget <= 0:
        raise ValueError(f"global_rpm_budget must be a positive integer, got {run_options.global_rpm_budget}")
    if run_options.global_tpm_budget <= 0:
        raise ValueError(f"global_tpm_budget must be a positive integer, got {run_options.global_tpm_budget}")
    if run_options.retry_attempts <= 0:
        raise ValueError(f"retry_attempts must be a positive integer, got {run_options.retry_attempts}")


async def _run_sync_with_budget(
    sem: asyncio.Semaphore,
    fn,
    /,
    *args: Any,
    **kwargs: Any,
) -> Any:
    async with sem:
        return await asyncio.to_thread(fn, *args, **kwargs)


async def _run_async_with_budget(
    sem: asyncio.Semaphore,
    coro_fn,
    /,
    *args: Any,
    **kwargs: Any,
) -> Any:
    async with sem:
        return await coro_fn(*args, **kwargs)


async def _run_persona_stage(
    deconstruction: dict[str, Any],
    *,
    expansion: dict[str, Any] | None,
    personas_dir: Path,
    item_state: BatchItemState,
    run_options: RunOptions,
    provider: str | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[str]]:
    """Run persona stage with bounded concurrency and local persona checkpoints."""
    personas_dir.mkdir(parents=True, exist_ok=True)
    persona_ids = list_persona_ids()
    if run_options.persona_limit is not None:
        persona_ids = persona_ids[: run_options.persona_limit]

    _validate_parallel_baseline(run_options)
    sem = asyncio.Semaphore(run_options.persona_concurrency)
    completed = set(item_state.completed_personas)

    async def _load_cached(persona_id: str, persona_json_path: Path) -> dict[str, Any] | None:
        if not persona_json_path.is_file():
            return None
        cached = _read_json(persona_json_path)
        completed.add(persona_id)
        return cached

    async def _run_one(persona_id: str) -> dict[str, Any]:
        persona_json_path = personas_dir / f"{persona_id}.json"
        cached = await _load_cached(persona_id, persona_json_path)
        if cached is not None:
            return {"persona_id": persona_id, "cached": True, "payload": cached}

        async with sem:
            _progress(
                f"[item {item_state.index}] persona stage start "
                f"({_parallel_baseline_summary(run_options)})"
            )
            try:
                result = await run_persona_pipeline(
                    persona_id,
                    deconstruction,
                    provider=provider,
                    expansion=expansion,
                )
            except Exception as exc:  # noqa: BLE001 - single persona failure must not fail the item
                error_message = f"{type(exc).__name__}: {exc}"
                _write_json(persona_json_path, {"error": error_message})
                return {"persona_id": persona_id, "error": error_message}

        if result.error or not result.pseudos:
            error_message = result.error or "no pseudos"
            _write_json(persona_json_path, {"error": error_message})
            return {"persona_id": persona_id, "error": error_message}

        agent = _persona_result_to_agent(result)
        _write_json(persona_json_path, {"agent": agent})
        return {"persona_id": persona_id, "agent": agent}

    results = await asyncio.gather(*(_run_one(persona_id) for persona_id in persona_ids))

    agents_by_id: dict[str, dict[str, Any]] = {}
    errors_by_id: dict[str, dict[str, Any]] = {}
    for result in results:
        persona_id = result["persona_id"]
        if result.get("agent") is not None:
            agents_by_id[persona_id] = _persona_agent_dict_to_dict(result["agent"])
        elif result.get("cached"):
            cached = result.get("payload") or {}
            if "agent" in cached and isinstance(cached["agent"], dict):
                agents_by_id[persona_id] = _persona_agent_dict_to_dict(cached["agent"])
            elif cached.get("error"):
                errors_by_id[persona_id] = {"agent_id": persona_id, "message": str(cached["error"])}
        else:
            message = str(result.get("error") or "unknown persona error")
            errors_by_id[persona_id] = {"agent_id": persona_id, "message": message}

    agents_list = [agents_by_id[persona_id] for persona_id in persona_ids if persona_id in agents_by_id]
    errors = [errors_by_id[persona_id] for persona_id in persona_ids if persona_id in errors_by_id]
    return agents_list, errors, persona_ids


async def _process_item(
    entry: dict[str, Any],
    item_state: BatchItemState,
    item_out_dir: Path,
    *,
    provider: str | None,
    run_options: RunOptions,
    batch_state: BatchState,
    state_file: Path,
) -> None:
    """跑单条 news 的完整 stage 链，每个 stage / persona 后立即 checkpoint。

    resume 时：deconstruct/expand/retrieve/compose 的产物文件存在即直接加载，跳过重跑；
    persona 逐个检查 personas/{id}.json 是否已存在于 completed_personas 中。
    """
    if item_state.status == "done":
        judge_path = _judge_scores_path(item_out_dir)
        if judge_path.is_file():
            return
        news_path = item_out_dir / "news.json"
        retrieve_path = item_out_dir / "retrieve.json"
        if not news_path.is_file() or not retrieve_path.is_file():
            return
        _progress(f"[item {item_state.index}] compose repair start")
        news_dict = _read_json(news_path)
        retrieve_result = _read_json(retrieve_path)
        judge_path, judge_created = _load_or_generate_judge_scores(
            item_out_dir=item_out_dir,
            run_id=item_out_dir.name,
            news_dict=news_dict,
            retrieve_result=retrieve_result,
            provider=provider,
        )
        judge_index = compose.load_judge_scores(judge_path)
        if judge_created:
            compose.run_review(
                retrieve_result,
                news_dict,
                provider=provider,
                judge_index=judge_index,
                run_id=item_out_dir.name,
            )
            _progress(f"[item {item_state.index}] compose repair done")
        return

    if not _has_sufficient_description(entry):
        raise ValueError(
            f"item {item_state.index}: insufficient description from heat pool; "
            "refresh pool.json before resuming daily batch"
        )

    news = _news_item_for_pool_entry(entry)
    item_out_dir.mkdir(parents=True, exist_ok=True)
    _write_json(item_out_dir / "news.json", news_to_dict(news))

    # --- Stage: deconstruct(A0) ---
    deconstruct_path = item_out_dir / "deconstruct.json"
    if deconstruct_path.is_file():
        deconstruction = _read_json(deconstruct_path)
    else:
        _progress(f"[item {item_state.index}] deconstruct start")
        decon_payload = run_deconstruct(news, provider=provider)
        deconstruction = decon_payload.get("deconstruction")
        if not isinstance(deconstruction, dict) or not deconstruction:
            raise ValueError(f"item {item_state.index}: deconstruct failed — no valid deconstruction")
        _write_json(deconstruct_path, deconstruction)
        item_state.status = "deconstruct"
        item_state.last_completed_stage = "deconstruct"
        batch_state.save(state_file)
        _progress(f"[item {item_state.index}] deconstruct done")

    # --- Stage: expand(P-Expand) ---
    expand_path = item_out_dir / "expand.json"
    if run_options.skip_expand:
        expansion: dict[str, Any] | None = None
    elif expand_path.is_file():
        expansion = _read_json(expand_path)
    else:
        from scripts.expand import run_expansion

        _progress(f"[item {item_state.index}] expand start")
        expansion_payload = run_expansion(deconstruction, provider=provider)
        expansion = expansion_payload.get("expansion")
        if not isinstance(expansion, dict):
            expansion = None
        _write_json(expand_path, expansion or {})
        item_state.status = "expand"
        item_state.last_completed_stage = "expand"
        batch_state.save(state_file)
        _progress(f"[item {item_state.index}] expand done")

    # --- Stage: persona × N (per-persona checkpoint) ---
    personas_dir = item_out_dir / "personas"
    agents_list, errors, persona_ids = await _run_persona_stage(
        deconstruction,
        expansion=expansion,
        personas_dir=personas_dir,
        item_state=item_state,
        run_options=run_options,
        provider=provider,
    )

    completed_set = set(item_state.completed_personas)
    for persona_id in persona_ids:
        if persona_id not in completed_set:
            item_state.completed_personas.append(persona_id)
            completed_set.add(persona_id)
    item_state.last_completed_stage = "persona"
    item_state.status = "persona"
    batch_state.save(state_file)

    # --- Stage: retrieve ---
    retrieve_path = item_out_dir / "retrieve.json"
    if retrieve_path.is_file():
        retrieve_result = _read_json(retrieve_path)
    else:
        _progress(f"[item {item_state.index}] retrieve start")
        retrieve_result = retrieve_from_agents(agents_list, errors, top_k=run_options.judge_topk)
        _write_json(retrieve_path, retrieve_result)
        item_state.status = "retrieve"
        item_state.last_completed_stage = "retrieve"
        batch_state.save(state_file)
        _progress(f"[item {item_state.index}] retrieve done")

    # --- Stage: compose(C1) + briefing ---
    news_dict = news_to_dict(news)
    judge_path, judge_created = _load_or_generate_judge_scores(
        item_out_dir=item_out_dir,
        run_id=item_out_dir.name,
        news_dict=news_dict,
        retrieve_result=retrieve_result,
        provider=provider,
    )
    judge_index = compose.load_judge_scores(judge_path)
    if judge_created:
        _progress(f"[item {item_state.index}] compose start")
        review_result = compose.run_review(
            retrieve_result,
            news_dict,
            provider=provider,
            judge_index=judge_index,
            run_id=item_out_dir.name,
        )
        for err in review_result.errors:
            errors.append({"agent_id": "C1", "message": err.get("message", str(err))})
        item_state.status = "compose"
        item_state.last_completed_stage = "compose"
        batch_state.save(state_file)
        _progress(f"[item {item_state.index}] compose done")

    item_state.status = "done"
    item_state.last_completed_stage = "compose"
    batch_state.save(state_file)


async def run_daily_batch(
    *,
    date: str | None = None,
    resume: bool = False,
    min_count: int = DEFAULT_MIN_COUNT,
    max_items: int | None = None,
    heat_sections: list[str] | None = None,
    run_options: RunOptions | None = None,
    provider: str | None = None,
    out_dir: Path | None = None,
    base_state_dir: Path | None = None,
) -> BatchState:
    """顶层入口：非 resume 时先跑 heat_pool 选题并初始化 state；resume 时加载既有 state，
    跳过 done 的 item，从断点继续。逐条处理 items，每完成 stage/persona 立即落盘 checkpoint。
    """
    resolved_date = date or _today_iso()
    resolved_run_options = run_options or RunOptions()
    _validate_parallel_baseline(resolved_run_options)
    provider = provider or getattr(resolved_run_options, "provider", None)
    resolved_state_path = state_path(resolved_date, base_state_dir)

    if max_items is not None and max_items <= 0:
        raise ValueError(f"max_items must be a positive integer, got {max_items}")
    if resolved_run_options.persona_concurrency <= 0:
        raise ValueError(
            f"persona_concurrency must be a positive integer, got {resolved_run_options.persona_concurrency}"
        )

    if resume:
        if not resolved_state_path.is_file():
            raise ValueError(f"--resume requested but no state file found: {resolved_state_path}")
        batch_state = load_batch_state(resolved_state_path)
        pool_file_path = Path(batch_state.pool_file)
        if not batch_state.parallel_baseline:
            batch_state.parallel_baseline = _parallel_baseline(resolved_run_options)
        if not pool_file_path.is_absolute():
            pool_file_path = repo_root() / pool_file_path
        pool = _read_json(pool_file_path)
    else:
        pool = fetch_heat_pool(
            date=resolved_date,
            min_count=min_count,
            max_items=max_items,
            sections=heat_sections,
            out_dir=out_dir,
        )
        if max_items is not None:
            pool = pool[:max_items]
        pool_file_path = pool_output_path(resolved_date, out_dir)
        batch_state = init_batch_state(resolved_date, pool, str(pool_file_path))
        batch_state.parallel_baseline = _parallel_baseline(resolved_run_options)
        batch_state.save(resolved_state_path)

    for item_state in batch_state.items:
        if item_state.index >= len(pool):
            continue
        entry = pool[item_state.index]
        target_dir = item_dir(resolved_date, item_state.index, item_state.slug, out_dir)
        judge_path = _judge_scores_path(target_dir)
        if _item_is_fully_complete(item_state) and judge_path.is_file():
            continue
        if item_state.status == "done" and not _item_is_fully_complete(item_state):
            item_state.status = "pending"
            item_state.last_completed_stage = None
            batch_state.save(resolved_state_path)
        if not _has_sufficient_description(entry):
            raise ValueError(
                f"item {item_state.index}: insufficient description from heat pool; "
                "refresh pool.json before resuming daily batch"
            )
        await _process_item(
            entry,
            item_state,
            target_dir,
            provider=provider,
            run_options=resolved_run_options,
            batch_state=batch_state,
            state_file=resolved_state_path,
        )

    write_daily_batch_briefing(batch_output_dir(resolved_date, out_dir))
    return batch_state


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run the daily batch orchestrator: heat pool → N news → daily pipeline, "
        "with stage+persona level checkpointing and resume.",
    )
    parser.add_argument("--date", help="Batch date override (default: today, UTC, YYYY-MM-DD).")
    parser.add_argument("--resume", action="store_true", help="Resume from an existing state file.")
    parser.add_argument(
        "--min-count",
        type=int,
        default=DEFAULT_MIN_COUNT,
        metavar="N",
        help=f"Minimum heat pool size after fallback (default: {DEFAULT_MIN_COUNT}).",
    )
    parser.add_argument(
        "--max-items",
        type=int,
        default=None,
        metavar="N",
        help="Limit the number of items initialized from the heat pool (default: all).",
    )
    parser.add_argument(
        "--max-sections",
        type=int,
        default=None,
        metavar="N",
        help="Limit Guardian heat-pool sections for smoke/dev runs (default: all).",
    )
    parser.add_argument(
        "--personas",
        type=int,
        default=None,
        metavar="N",
        help="Dev shortcut: only run the first N personas per item (default: all 12).",
    )
    parser.add_argument(
        "--persona-concurrency",
        type=int,
        default=4,
        metavar="N",
        help="Persona stage concurrency limit (default: 4).",
    )
    parser.add_argument("--skip-expand", action="store_true", help="Dev shortcut: skip the P-Expand stage.")
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider override (default: DEFAULT_LLM_PROVIDER from .env).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    run_options = RunOptions(
        persona_limit=args.personas,
        persona_concurrency=args.persona_concurrency,
        skip_expand=args.skip_expand,
    )
    heat_sections = RANKED_SECTIONS[: args.max_sections] if args.max_sections is not None else None
    try:
        asyncio.run(
            run_daily_batch(
                date=args.date,
                resume=args.resume,
                min_count=args.min_count,
                max_items=args.max_items,
                heat_sections=heat_sections,
                run_options=run_options,
                provider=args.provider,
            )
        )
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())