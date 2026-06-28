"""copywriter.py · C1/C2 copywriter (Phase 4).

Stage ``review`` (C1): read a ``retrieve.json`` candidate pool plus news context,
ask the LLM to write one structured Chinese review card per candidate (标题短语 /
文案 / 电影介绍 / Hashtag / 评分理由中译), and emit a structured JSON for editorial
review, plus render an Obsidian-readable Markdown review document. The card pairs
LLM-authored copy with non-authored facts: the original news, the movie's original
overview, genres, a director placeholder (待补, DB backfill later), and the judge's
rationale in both English (data原文) and Chinese (C1 译文).

ADR-0009 candidate contract (verified against phase3.11 products):
- ``candidates[]`` holds the funnel+budget pool C1 consumes (== ``human_candidates``).
- ``triggered_by`` (top level) lists persona ids that recalled the movie.
- ``center_dimensions`` / ``search_unit_kinds`` live under ``match_diagnostics`` and
  are透传 as OPEN-a soft hints only (never used to force a focal POV).
- A1/oracle stays in ``a1_oracle`` (never in ``candidates``); it is never rendered.
- News context comes from a news/reality JSON (title + description); a representative
  ``persona-semantic`` search unit from ``per_agent`` is appended when available.
- ``judge_score`` is screening-only, lives in a separate judge-scores file, and is
  backfilled by (run_id, tmdb_id); missing scores are treated as empty.

MVP scope: review stage only. No platform finalization, no bilingual, no images.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from openai import OpenAI

from scripts.lib.env import default_llm_provider, load_env
from scripts.lib.llm import get_llm_client
from scripts.lib.paths import repo_root

_MODEL_ENV: dict[str, str] = {
    "mimo": "MIMO_MODEL",
    "deepseek": "DEEPSEEK_MODEL",
}

_C1_PROMPT_REL = "prompts/compose_review.md"

_OVERVIEW_MAX_CHARS = 240

# OPEN-a soft hint: human-readable labels for center_dimensions (W-axes).
_DIMENSION_LABELS: dict[str, str] = {
    "who": "人物",
    "where": "地点",
    "when": "时间",
    "why": "动因",
    "how": "过程",
    "result": "结果",
}

# Section-leader pattern for parsing C1 multi-paragraph output: 《片名》(年份).
_TITLE_LINE_RE = re.compile(r"^\s*《(?P<title>.+?)》\s*[（(]\s*(?P<year>\d{3,4})\s*[)）]")

_SYSTEM_MESSAGE = (
    "你是「每日星轨观测」的随刊评论员。严格按用户消息中的契约输出中文结构化审核卡，"
    "每部候选电影一块，块首标注《片名》(年份)，块内按固定字段前缀逐行输出。不要前言后语。"
)

# Fixed field prefixes the LLM emits inside each review card (DSL contract).
_CARD_FIELD_PREFIXES: dict[str, str] = {
    "标题:": "headline",
    "文案:": "copy_text",
    "电影介绍:": "intro",
    "Hashtag:": "hashtags",
    "评分理由中译:": "rationale_zh",
}

# Director is not in retrieve.json yet; placeholder until DB backfill lands.
_DIRECTOR_PLACEHOLDER = "待补"


@dataclass
class JudgeEntry:
    """One thinking-judge row: screening score plus its rationale (EN原文)."""

    score: int | None = None
    rationale: str = ""
    causal_test: str = ""
    resonance_type: str = ""


@dataclass
class ReviewCopy:
    """One C1 structured review card mapped back to its candidate.

    Fields split into three provenances:
    - candidate data (overview/genres/movie_url) — TMDB facts, never LLM-authored;
    - judge data (score + EN rationale) — screening evidence, never LLM-authored;
    - LLM-authored card fields (headline/copy_text/intro/hashtags/rationale_zh).
    ``director`` is a placeholder until a DB lookup backfills it.
    """

    tmdb_id: int | str
    title: str
    year: int | None
    triggered_by: list[str]
    center_dimensions: list[str]
    overview: str = ""
    genres: str = ""
    director: str = _DIRECTOR_PLACEHOLDER
    movie_url: str = ""
    judge_score: int | None = None
    judge_rationale_en: str = ""
    judge_causal_test_en: str = ""
    judge_resonance_type: str = ""
    headline: str = ""
    copy_text: str = ""
    intro: str = ""
    hashtags: str = ""
    rationale_zh: str = ""


@dataclass
class ReviewResult:
    review_copies: list[ReviewCopy] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)
    dropped_candidates: list[dict[str, Any]] = field(default_factory=list)
    min_judge: int | None = None


def _resolve_provider(explicit: str | None) -> str:
    if explicit is not None:
        return explicit.strip().lower()
    return default_llm_provider()


def _model_name(provider: str) -> str:
    load_env()
    env_key = _MODEL_ENV.get(provider)
    if not env_key:
        raise ValueError(f"Unknown provider {provider!r}")
    model = os.getenv(env_key, "").strip()
    if not model:
        raise RuntimeError(
            f"Missing {env_key} for provider {provider!r}. "
            "Copy .env.example to .env and set the model name."
        )
    return model


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_retrieve(path: Path) -> dict[str, Any]:
    """Load a retrieve.json product; require a ``candidates`` list."""
    data = _load_json(path)
    if not isinstance(data, dict):
        raise ValueError("retrieve JSON must be a JSON object")
    if not isinstance(data.get("candidates"), list):
        raise ValueError("retrieve JSON requires a 'candidates' array")
    return data


def load_news(path: Path | None, retrieve: dict[str, Any]) -> dict[str, str]:
    """Resolve news context: explicit file > retrieve['news'] > empty.

    Only ``title`` / ``description`` are load-bearing for C1 context.
    """
    if path is not None:
        data = _load_json(path)
        if not isinstance(data, dict):
            raise ValueError("news JSON must be a JSON object")
    else:
        data = retrieve.get("news")
        if not isinstance(data, dict):
            data = {}
    return {
        "title": str(data.get("title", "") or "").strip(),
        "description": str(data.get("description", "") or "").strip(),
    }


def representative_persona_semantic(retrieve: dict[str, Any]) -> str:
    """Highest-similarity ``persona-semantic`` search unit text from per_agent.

    Never draws from A1/oracle. Returns ``""`` when none is present.
    """
    best_text = ""
    best_sim = float("-inf")
    for agent in retrieve.get("per_agent") or []:
        if not isinstance(agent, dict):
            continue
        for pseudo in agent.get("pseudos") or []:
            if not isinstance(pseudo, dict):
                continue
            source = pseudo.get("source")
            kind = ""
            if isinstance(source, dict):
                kind = str(source.get("search_unit_kind", ""))
            if kind != "persona-semantic":
                continue
            hits = pseudo.get("hits") or []
            top_sim = float("-inf")
            for hit in hits:
                if isinstance(hit, dict) and isinstance(hit.get("similarity"), (int, float)):
                    top_sim = max(top_sim, float(hit["similarity"]))
            text = str(pseudo.get("pseudo", "") or "").strip()
            if text and top_sim > best_sim:
                best_sim = top_sim
                best_text = text
    return best_text


def load_judge_scores(path: Path | None) -> dict[tuple[str, str], JudgeEntry]:
    """Index judge rows by (run_id, tmdb_id) → JudgeEntry (screening-only).

    Carries the screening ``judge_score`` plus its English rationale fields so C1
    can surface the judge's reasoning. Missing file/scores yield an empty index;
    C1 never hard-fails on it. Only ``.score`` gates filtering (see filter).
    """
    if path is None or not path.is_file():
        return {}
    data = _load_json(path)
    scores = data.get("scores") if isinstance(data, dict) else None
    index: dict[tuple[str, str], JudgeEntry] = {}
    for row in scores or []:
        if not isinstance(row, dict):
            continue
        run_id = str(row.get("run_id", "") or "").strip()
        tmdb_id = str(row.get("tmdb_id", "") or "").strip()
        if not tmdb_id:
            continue
        raw = row.get("judge_score")
        score = int(raw) if isinstance(raw, (int, float)) else None
        index[(run_id, tmdb_id)] = JudgeEntry(
            score=score,
            rationale=str(row.get("rationale", "") or "").strip(),
            causal_test=str(row.get("causal_test", "") or "").strip(),
            resonance_type=str(row.get("judge_resonance_type", "") or "").strip(),
        )
    return index


def _persona_phrase(triggered_by: list[str]) -> str:
    if not triggered_by:
        return "（无触发视角记录）"
    return "、".join(triggered_by)


def _dimension_phrase(center_dimensions: list[str]) -> str:
    labels = [
        f"{_DIMENSION_LABELS.get(d, d)}" for d in center_dimensions if str(d).strip()
    ]
    return "、".join(labels) if labels else ""


def _truncate_overview(overview: str) -> str:
    text = overview.strip()
    if len(text) <= _OVERVIEW_MAX_CHARS:
        return text
    return text[:_OVERVIEW_MAX_CHARS].rstrip() + "…"


def _candidate_match_diagnostics(candidate: dict[str, Any]) -> dict[str, Any]:
    diag = candidate.get("match_diagnostics")
    return diag if isinstance(diag, dict) else {}


def _candidate_center_dimensions(candidate: dict[str, Any]) -> list[str]:
    diag = _candidate_match_diagnostics(candidate)
    dims = diag.get("center_dimensions")
    return [str(d) for d in dims if str(d).strip()] if isinstance(dims, list) else []


def _candidate_year(candidate: dict[str, Any]) -> int | None:
    raw = candidate.get("release_year")
    if isinstance(raw, int):
        return raw
    if isinstance(raw, str) and raw.strip().isdigit():
        return int(raw.strip())
    return None


def format_candidates_block(
    candidates: list[dict[str, Any]],
    judge_index: dict[tuple[str, str], "JudgeEntry"] | None = None,
    run_id: str = "",
) -> str:
    """Render candidates into the C1 ``{{candidates}}`` block (one entry each).

    Each entry now also feeds the LLM the movie genres and the judge's English
    rationale, so the structured card can translate the rationale and stay
    grounded in TMDB facts.
    """
    judge_index = judge_index or {}
    lines: list[str] = []
    for idx, cand in enumerate(candidates, start=1):
        title = str(cand.get("title", "") or "").strip()
        year = _candidate_year(cand)
        year_str = str(year) if year is not None else "—"
        overview = _truncate_overview(str(cand.get("overview", "") or ""))
        genres = str(cand.get("genres", "") or "").strip()
        triggered = [str(p) for p in cand.get("triggered_by") or [] if str(p).strip()]
        dims = _dimension_phrase(_candidate_center_dimensions(cand))
        movie_url = str(cand.get("movie_url", "") or "").strip()
        judge = _lookup_judge(judge_index, run_id, cand.get("tmdb_id"))

        lines.append(f"{idx}. 《{title}》({year_str})")
        if overview:
            lines.append(f"   - overview: {overview}")
        if genres:
            lines.append(f"   - genres: {genres}")
        lines.append(f"   - 被这些视角击中: {_persona_phrase(triggered)}")
        if dims:
            lines.append(f"   - 切面（可选参考，非强制聚焦）: {dims}")
        if movie_url:
            lines.append(f"   - 链接: {movie_url}")
        rationale_en = _judge_rationale_en(judge)
        if rationale_en:
            lines.append(f"   - judge 英文评分理由（请翻译为中文）: {rationale_en}")
        lines.append("")
    return "\n".join(lines).rstrip()


def build_news_context(news: dict[str, str], persona_semantic: str) -> str:
    parts: list[str] = []
    title = news.get("title", "").strip()
    description = news.get("description", "").strip()
    if title:
        parts.append(f"标题: {title}")
    if description:
        parts.append(f"摘要: {description}")
    if persona_semantic:
        parts.append(f"代表性视角片段（persona-semantic）: {persona_semantic}")
    return "\n".join(parts).strip()


def load_c1_template(prompts_dir: Path | None = None) -> str:
    base = prompts_dir or (repo_root() / "prompts")
    path = base / "compose_review.md"
    if not path.is_file():
        path = repo_root() / _C1_PROMPT_REL
    if not path.is_file():
        raise FileNotFoundError(f"C1 prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def render_c1_prompt(template: str, news_context: str, candidates_block: str) -> str:
    rendered = template.replace("{{news_context}}", news_context or "（无新闻语境）")
    rendered = rendered.replace("{{candidates}}", candidates_block or "（无候选）")
    return rendered


def _sync_llm_call(client: OpenAI, model: str, user_prompt: str) -> str:
    messages = [
        {"role": "system", "content": _SYSTEM_MESSAGE},
        {"role": "user", "content": user_prompt},
    ]
    response = client.chat.completions.create(model=model, messages=messages)
    return (response.choices[0].message.content or "").strip()


def split_into_paragraphs(raw: str) -> list[tuple[str, int | None, str]]:
    """Split C1 output into (title, year, text) by 《片名》(年份) section leaders."""
    blocks: list[tuple[str, int | None, str]] = []
    current_title: str | None = None
    current_year: int | None = None
    current_lines: list[str] = []

    def flush() -> None:
        if current_title is not None:
            text = "\n".join(current_lines).strip()
            blocks.append((current_title, current_year, text))

    for line in raw.splitlines():
        match = _TITLE_LINE_RE.match(line)
        if match:
            flush()
            current_title = match.group("title").strip()
            year_raw = match.group("year")
            current_year = int(year_raw) if year_raw.isdigit() else None
            current_lines = [line.strip()]
        elif current_title is not None:
            current_lines.append(line)
    flush()
    return blocks


def _normalize_title(title: str) -> str:
    return re.sub(r"\s+", "", title).strip().lower()


def map_paragraphs_to_candidates(
    blocks: list[tuple[str, int | None, str]],
    candidates: list[dict[str, Any]],
) -> tuple[list[tuple[dict[str, Any], str]], list[dict[str, Any]]]:
    """Map parsed paragraphs back to candidates, preferring title+year match.

    Falls back to positional order when titles do not match (LLM may translate
    titles). Returns (matched pairs in candidate order, errors).
    """
    errors: list[dict[str, Any]] = []
    by_title: dict[tuple[str, int | None], str] = {}
    by_title_any_year: dict[str, str] = {}
    for title, year, text in blocks:
        norm = _normalize_title(title)
        by_title[(norm, year)] = text
        by_title_any_year.setdefault(norm, text)

    pairs: list[tuple[dict[str, Any], str]] = []
    for cand in candidates:
        norm = _normalize_title(str(cand.get("title", "")))
        year = _candidate_year(cand)
        text = by_title.get((norm, year)) or by_title_any_year.get(norm)
        pairs.append((cand, text or ""))

    if len(blocks) == len(candidates) and any(not t for _, t in pairs):
        # Title matching failed for some; fall back to positional alignment.
        pairs = [(cand, blocks[i][2]) for i, cand in enumerate(candidates)]

    for cand, text in pairs:
        if not text.strip():
            errors.append(
                {
                    "tmdb_id": cand.get("tmdb_id"),
                    "title": cand.get("title"),
                    "type": "missing_paragraph",
                    "message": "C1 output had no paragraph for this candidate",
                }
            )
    return pairs, errors


def parse_card_fields(block_text: str) -> dict[str, str]:
    """Parse a C1 card block into its DSL fields by fixed line prefixes.

    The first ``《片名》(年份)`` leader line is skipped; remaining lines are bucketed
    by the field prefix that opened them, so multi-line ``电影介绍`` is preserved.
    Unknown lines before any field prefix are ignored; lines after a prefix append
    to the current field.
    """
    fields: dict[str, list[str]] = {key: [] for key in _CARD_FIELD_PREFIXES.values()}
    current: str | None = None
    for raw_line in block_text.splitlines():
        line = raw_line.strip()
        if not line or _TITLE_LINE_RE.match(line):
            continue
        line = line.lstrip("> ").strip()
        matched = False
        for prefix, key in _CARD_FIELD_PREFIXES.items():
            if line.startswith(prefix):
                current = key
                fields[key].append(line[len(prefix):].strip())
                matched = True
                break
        if matched:
            continue
        if current is not None:
            fields[current].append(line)
    return {key: "\n".join(parts).strip() for key, parts in fields.items()}


def assemble_review_copies(
    pairs: list[tuple[dict[str, Any], str]],
    judge_index: dict[tuple[str, str], "JudgeEntry"],
    run_id: str,
) -> list[ReviewCopy]:
    copies: list[ReviewCopy] = []
    for cand, text in pairs:
        if not text.strip():
            continue
        tmdb_id = cand.get("tmdb_id")
        judge = _lookup_judge(judge_index, run_id, tmdb_id)
        card = parse_card_fields(text)
        copies.append(
            ReviewCopy(
                tmdb_id=tmdb_id,
                title=str(cand.get("title", "") or ""),
                year=_candidate_year(cand),
                triggered_by=[
                    str(p) for p in cand.get("triggered_by") or [] if str(p).strip()
                ],
                center_dimensions=_candidate_center_dimensions(cand),
                overview=str(cand.get("overview", "") or "").strip(),
                genres=str(cand.get("genres", "") or "").strip(),
                director=_DIRECTOR_PLACEHOLDER,
                movie_url=str(cand.get("movie_url", "") or ""),
                judge_score=judge.score if judge else None,
                judge_rationale_en=judge.rationale if judge else "",
                judge_causal_test_en=judge.causal_test if judge else "",
                judge_resonance_type=judge.resonance_type if judge else "",
                headline=card.get("headline", ""),
                copy_text=card.get("copy_text", ""),
                intro=card.get("intro", ""),
                hashtags=card.get("hashtags", ""),
                rationale_zh=card.get("rationale_zh", ""),
            )
        )
    return copies


def _lookup_judge(
    judge_index: dict[tuple[str, str], "JudgeEntry"],
    run_id: str,
    tmdb_id: Any,
) -> "JudgeEntry | None":
    """Resolve a candidate's JudgeEntry by (run_id, tmdb_id), blank-run fallback."""
    entry = judge_index.get((run_id, str(tmdb_id)))
    if entry is None:
        entry = judge_index.get(("", str(tmdb_id)))
    return entry


def _judge_rationale_en(judge: "JudgeEntry | None") -> str:
    """Join the judge's English rationale + causal test for the LLM/audit view."""
    if judge is None:
        return ""
    parts = [p for p in (judge.rationale, judge.causal_test) if p]
    return " / ".join(parts)


def filter_candidates_by_judge(
    candidates: list[dict[str, Any]],
    judge_index: dict[tuple[str, str], "JudgeEntry"],
    run_id: str,
    min_judge: int | None,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Drop candidates below the judge floor before the C1 LLM call.

    ``min_judge`` is ``None`` → no filtering (library default; back-compat).
    Otherwise keep only candidates whose thinking-judge score is present AND
    ``>= min_judge``. This single predicate drops both ``judge_score == 0`` and
    candidates with no judge score (those that never entered the ≥5 high-hit pool
    the judge scored), so the C1 input == the ≥5-hit ∩ judge≥min_judge pool.

    Returns ``(kept, dropped)``; each dropped entry records why for audit.
    """
    if min_judge is None:
        return candidates, []
    kept: list[dict[str, Any]] = []
    dropped: list[dict[str, Any]] = []
    for cand in candidates:
        judge = _lookup_judge(judge_index, run_id, cand.get("tmdb_id"))
        score = judge.score if judge else None
        if score is not None and score >= min_judge:
            kept.append(cand)
        else:
            dropped.append(
                {
                    "tmdb_id": cand.get("tmdb_id"),
                    "title": cand.get("title"),
                    "judge_score": score,
                    "reason": (
                        "no_judge_score" if score is None else "below_min_judge"
                    ),
                }
            )
    return kept, dropped


def run_review(
    retrieve: dict[str, Any],
    news: dict[str, str],
    *,
    provider: str | None = None,
    judge_index: dict[tuple[str, str], int] | None = None,
    run_id: str = "",
    min_judge: int | None = None,
    prompts_dir: Path | None = None,
    llm_call: Any = None,
) -> ReviewResult:
    """Core C1 review pipeline (LLM call is injectable for offline tests).

    ``min_judge`` gates the C1 input: ``None`` keeps every candidate (default),
    while an int drops candidates with no judge score or ``judge_score < min_judge``
    *before* the LLM call (token-saving). See ``filter_candidates_by_judge``.
    """
    candidates = [c for c in retrieve.get("candidates") or [] if isinstance(c, dict)]
    judge_index = judge_index or {}
    if not candidates:
        return ReviewResult(review_copies=[], errors=[], min_judge=min_judge)

    candidates, dropped = filter_candidates_by_judge(
        candidates, judge_index, run_id, min_judge
    )
    if not candidates:
        return ReviewResult(
            review_copies=[],
            errors=[],
            dropped_candidates=dropped,
            min_judge=min_judge,
        )

    template = load_c1_template(prompts_dir)
    persona_semantic = representative_persona_semantic(retrieve)
    news_context = build_news_context(news, persona_semantic)
    candidates_block = format_candidates_block(candidates, judge_index, run_id)
    prompt = render_c1_prompt(template, news_context, candidates_block)

    try:
        if llm_call is not None:
            raw = llm_call(prompt)
        else:
            load_env()
            resolved = _resolve_provider(provider)
            client = get_llm_client(resolved)
            model = _model_name(resolved)
            raw = _sync_llm_call(client, model, prompt)
    except Exception as exc:  # noqa: BLE001 — record, never crash the batch
        return ReviewResult(
            review_copies=[],
            errors=[{"type": "llm_error", "message": str(exc)}],
            dropped_candidates=dropped,
            min_judge=min_judge,
        )

    raw = (raw or "").strip()
    if not raw:
        return ReviewResult(
            review_copies=[],
            errors=[{"type": "llm_error", "message": "empty LLM response"}],
            dropped_candidates=dropped,
            min_judge=min_judge,
        )

    blocks = split_into_paragraphs(raw)
    pairs, map_errors = map_paragraphs_to_candidates(blocks, candidates)
    copies = assemble_review_copies(pairs, judge_index, run_id)
    return ReviewResult(
        review_copies=copies,
        errors=map_errors,
        dropped_candidates=dropped,
        min_judge=min_judge,
    )


def review_copy_to_dict(copy: ReviewCopy) -> dict[str, Any]:
    return {
        "tmdb_id": copy.tmdb_id,
        "title": copy.title,
        "year": copy.year,
        "triggered_by": copy.triggered_by,
        "center_dimensions": copy.center_dimensions,
        "overview": copy.overview,
        "genres": copy.genres,
        "director": copy.director,
        "movie_url": copy.movie_url,
        "judge": {
            "score": copy.judge_score,
            "resonance_type": copy.judge_resonance_type,
            "rationale_en": copy.judge_rationale_en,
            "causal_test_en": copy.judge_causal_test_en,
            "rationale_zh": copy.rationale_zh,
        },
        "card": {
            "headline": copy.headline,
            "copy_text": copy.copy_text,
            "intro": copy.intro,
            "hashtags": copy.hashtags,
        },
    }


def result_to_payload(result: ReviewResult) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "review_copies": [review_copy_to_dict(c) for c in result.review_copies],
        "errors": result.errors,
    }
    if result.min_judge is not None:
        payload["filter"] = {
            "min_judge": result.min_judge,
            "dropped_count": len(result.dropped_candidates),
            "dropped_candidates": result.dropped_candidates,
        }
    return payload


def render_review_copy_block(copy: ReviewCopy) -> str:
    """Render one structured review card into Obsidian-readable Markdown.

    Layout mirrors the upgraded template: a 片名 | 标题短语 heading, the C1
    copy/quote, the 电影信息 line (导演占位「待补」｜年份｜genres), the movie's
    original overview, the C1 movie intro, the judge's rationale in both English
    (data原文) and Chinese (C1 译文), Hashtag, the link, and a manual selection
    checkbox the editor never sees pre-checked.
    """
    year_str = str(copy.year) if copy.year is not None else "—"
    headline = copy.headline.strip()
    heading = f"### 《{copy.title}》({year_str})"
    if headline:
        heading += f" | {headline}"
    lines = [heading]

    copy_text = copy.copy_text.strip() or "（本候选无文案）"
    lines.append(f"- 文案:\n\n> {copy_text}")

    genres = copy.genres.strip() or "—"
    lines.append(f"- 电影信息: {copy.director} | {year_str} | {genres}")

    if copy.overview.strip():
        lines.append(f"- 电影原 overview: {copy.overview.strip()}")
    if copy.intro.strip():
        lines.append(f"- 电影介绍（C1）:\n\n{copy.intro.strip()}")

    if copy.judge_score is not None:
        lines.append(f"- judge_score（screening-only）: {copy.judge_score}")
    if copy.judge_resonance_type.strip():
        lines.append(f"- 共振类型: {copy.judge_resonance_type.strip()}")
    rationale_en = _judge_rationale_en(
        JudgeEntry(
            rationale=copy.judge_rationale_en,
            causal_test=copy.judge_causal_test_en,
        )
    )
    if rationale_en:
        lines.append(f"- 评分理由（EN 原文）: {rationale_en}")
    if copy.rationale_zh.strip():
        lines.append(f"- 评分理由（中译）: {copy.rationale_zh.strip()}")

    if copy.hashtags.strip():
        lines.append(f"- Hashtag: {copy.hashtags.strip()}")
    if copy.movie_url:
        lines.append(f"- 链接: {copy.movie_url}")
    lines.append("- [ ] ✅ 选用")
    return "\n".join(lines)


def result_to_markdown(
    result: ReviewResult,
    *,
    news: dict[str, str] | None = None,
    run_id: str = "",
) -> str:
    """Assemble the full Obsidian review document (one card per candidate).

    The original news (title + description) leads the document so the editor reads
    each candidate group against the source event.
    """
    news = news or {}
    header: list[str] = ["# 审核稿候选（C1 · 待总编肉眼审核）"]
    title = str(news.get("title", "") or "").strip()
    description = str(news.get("description", "") or "").strip()
    if title:
        header.append(f"\n> 原新闻: {title}")
    if description:
        header.append(f"> 新闻摘要: {description}")
    if run_id:
        header.append(f"> run_id: {run_id}")
    header.append(f"> 候选数: {len(result.review_copies)}")

    parts = ["\n".join(header)]
    for copy in result.review_copies:
        parts.append(render_review_copy_block(copy))

    if result.errors:
        err_lines = ["## 生成异常（errors）"]
        for err in result.errors:
            err_lines.append(
                f"- `{err.get('type', 'error')}`: "
                f"{err.get('title') or err.get('tmdb_id') or ''} "
                f"{err.get('message', '')}".rstrip()
            )
        parts.append("\n".join(err_lines))

    return "\n\n".join(parts).rstrip() + "\n"


def _infer_run_id(retrieve_path: Path) -> str:
    """Best-effort run id (== news dir name) for judge backfill keying."""
    parent = retrieve_path.parent.name
    return parent.strip()


def _resolve_md_out(args: argparse.Namespace, out_path: Path | None) -> Path | None:
    """Resolve the Obsidian Markdown output path.

    Explicit ``--md-out`` wins. Otherwise, when ``--out`` is given, default the
    Markdown next to it (``*.md``). With neither (stdout JSON mode), emit no file.
    """
    if getattr(args, "md_out", None):
        md_path = Path(args.md_out)
        if not md_path.is_absolute():
            md_path = _REPO_ROOT / md_path
        return md_path
    if out_path is not None:
        return out_path.with_suffix(".md")
    return None


def _run_review_cli(args: argparse.Namespace) -> int:
    retrieve_path = Path(args.retrieve_json)
    if not retrieve_path.is_absolute():
        retrieve_path = _REPO_ROOT / retrieve_path
    if not retrieve_path.is_file():
        print(f"error: retrieve JSON not found: {retrieve_path}", file=sys.stderr)
        return 2

    retrieve = load_retrieve(retrieve_path)

    news_path: Path | None = None
    if args.news_file:
        news_path = Path(args.news_file)
        if not news_path.is_absolute():
            news_path = _REPO_ROOT / news_path
        if not news_path.is_file():
            print(f"error: news file not found: {news_path}", file=sys.stderr)
            return 2
    news = load_news(news_path, retrieve)

    judge_path: Path | None = None
    if args.judge_scores:
        judge_path = Path(args.judge_scores)
        if not judge_path.is_absolute():
            judge_path = _REPO_ROOT / judge_path
    judge_index = load_judge_scores(judge_path)
    run_id = args.run_id or _infer_run_id(retrieve_path)

    # CLI contract: --min-judge 0 (or negative) disables filtering entirely
    # (whole pool passes through), matching the documented toggle semantics.
    min_judge = args.min_judge if args.min_judge and args.min_judge > 0 else None

    result = run_review(
        retrieve,
        news,
        provider=args.provider,
        judge_index=judge_index,
        run_id=run_id,
        min_judge=min_judge,
    )
    if result.min_judge is not None:
        print(
            f"judge filter: min_judge={result.min_judge} "
            f"kept={len(result.review_copies)} "
            f"dropped={len(result.dropped_candidates)}",
            file=sys.stderr,
        )
    payload = result_to_payload(result)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)

    out_path: Path | None = None
    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = _REPO_ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(serialized + "\n", encoding="utf-8")
        print(f"Wrote {out_path.resolve()}", file=sys.stderr)
    else:
        sys.stdout.buffer.write((serialized + "\n").encode("utf-8"))

    md_path = _resolve_md_out(args, out_path)
    if md_path is not None:
        markdown = result_to_markdown(result, news=news, run_id=run_id)
        md_path.parent.mkdir(parents=True, exist_ok=True)
        md_path.write_text(markdown, encoding="utf-8")
        print(f"Wrote {md_path.resolve()}", file=sys.stderr)

    # A non-empty candidate pool that yields no copies is only a failure when no
    # judge filter was applied; with --min-judge an empty result is a legit "all
    # candidates fell below the floor" outcome.
    if (
        not result.review_copies
        and retrieve.get("candidates")
        and not result.dropped_candidates
    ):
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Copywriter: C1 Chinese review drafts (Phase 4 MVP).",
    )
    parser.add_argument(
        "--stage",
        choices=["review"],
        default="review",
        help="Pipeline stage (MVP: review only; publish lands in Stage 1).",
    )
    parser.add_argument(
        "--retrieve-json",
        dest="retrieve_json",
        required=True,
        help="Path to retrieve.json (consumes candidates[]).",
    )
    parser.add_argument(
        "--news-file",
        dest="news_file",
        help="Optional news JSON (title/description); falls back to retrieve['news'].",
    )
    parser.add_argument(
        "--judge-scores",
        dest="judge_scores",
        help="Optional judge-scores JSON for screening-only judge_score backfill.",
    )
    parser.add_argument(
        "--run-id",
        dest="run_id",
        help="Run id for judge keying (default: retrieve.json parent dir name).",
    )
    parser.add_argument(
        "--min-judge",
        dest="min_judge",
        type=int,
        default=1,
        help=(
            "Drop candidates with no thinking-judge score or judge_score below "
            "this floor before C1 (default: 1, i.e. drop judge==0 and unjudged). "
            "Set 0 to disable filtering and pass the whole candidate pool."
        ),
    )
    parser.add_argument(
        "--out",
        help="Write review JSON to this path; otherwise print UTF-8 JSON to stdout.",
    )
    parser.add_argument(
        "--md-out",
        dest="md_out",
        help=(
            "Write the Obsidian-readable Markdown candidate blocks to this path. "
            "Defaults to the --out path with a .md suffix when --out is given."
        ),
    )
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider override (default: DEFAULT_LLM_PROVIDER from .env).",
    )
    args = parser.parse_args(argv)

    try:
        return _run_review_cli(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())