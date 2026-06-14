"""copywriter.py · C1/C2 copywriter (Phase 4).

Stage ``review`` (C1): read a ``retrieve.json`` candidate pool plus news context,
ask the LLM to write one Chinese review-draft paragraph per candidate, and emit a
structured JSON for editorial review. Obsidian rendering and platform finalization
land in later 4.x todos.

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

_C1_PROMPT_REL = "prompts/C1_copywriter_review.md"

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
    "你是「每日星轨观测」的随刊评论员。严格按用户消息中的契约输出中文审核稿，"
    "每部候选电影一段，段首标注《片名》(年份)。不要前言后语。"
)


@dataclass
class ReviewCopy:
    """One C1 review-draft paragraph mapped back to its candidate."""

    tmdb_id: int | str
    title: str
    year: int | None
    triggered_by: list[str]
    center_dimensions: list[str]
    text_zh: str
    judge_score: int | None = None
    movie_url: str = ""


@dataclass
class ReviewResult:
    review_copies: list[ReviewCopy] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


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


def load_judge_scores(path: Path | None) -> dict[tuple[str, str], int]:
    """Index judge scores by (run_id, tmdb_id) → judge_score (screening-only).

    Missing file or missing scores yield an empty index; C1 never hard-fails on it.
    """
    if path is None or not path.is_file():
        return {}
    data = _load_json(path)
    scores = data.get("scores") if isinstance(data, dict) else None
    index: dict[tuple[str, str], int] = {}
    for row in scores or []:
        if not isinstance(row, dict):
            continue
        run_id = str(row.get("run_id", "") or "").strip()
        tmdb_id = str(row.get("tmdb_id", "") or "").strip()
        raw = row.get("judge_score")
        if tmdb_id and isinstance(raw, (int, float)):
            index[(run_id, tmdb_id)] = int(raw)
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


def format_candidates_block(candidates: list[dict[str, Any]]) -> str:
    """Render candidates into the C1 ``{{candidates}}`` block (one entry each)."""
    lines: list[str] = []
    for idx, cand in enumerate(candidates, start=1):
        title = str(cand.get("title", "") or "").strip()
        year = _candidate_year(cand)
        year_str = str(year) if year is not None else "—"
        overview = _truncate_overview(str(cand.get("overview", "") or ""))
        triggered = [str(p) for p in cand.get("triggered_by") or [] if str(p).strip()]
        dims = _dimension_phrase(_candidate_center_dimensions(cand))
        movie_url = str(cand.get("movie_url", "") or "").strip()

        lines.append(f"{idx}. 《{title}》({year_str})")
        if overview:
            lines.append(f"   - overview: {overview}")
        lines.append(f"   - 被这些视角击中: {_persona_phrase(triggered)}")
        if dims:
            lines.append(f"   - 切面（可选参考，非强制聚焦）: {dims}")
        if movie_url:
            lines.append(f"   - 链接: {movie_url}")
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
    path = base / "C1_copywriter_review.md"
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


def assemble_review_copies(
    pairs: list[tuple[dict[str, Any], str]],
    judge_index: dict[tuple[str, str], int],
    run_id: str,
) -> list[ReviewCopy]:
    copies: list[ReviewCopy] = []
    for cand, text in pairs:
        if not text.strip():
            continue
        tmdb_id = cand.get("tmdb_id")
        judge = judge_index.get((run_id, str(tmdb_id)))
        if judge is None:
            judge = judge_index.get(("", str(tmdb_id)))
        copies.append(
            ReviewCopy(
                tmdb_id=tmdb_id,
                title=str(cand.get("title", "") or ""),
                year=_candidate_year(cand),
                triggered_by=[
                    str(p) for p in cand.get("triggered_by") or [] if str(p).strip()
                ],
                center_dimensions=_candidate_center_dimensions(cand),
                text_zh=text.strip(),
                judge_score=judge,
                movie_url=str(cand.get("movie_url", "") or ""),
            )
        )
    return copies


def run_review(
    retrieve: dict[str, Any],
    news: dict[str, str],
    *,
    provider: str | None = None,
    judge_index: dict[tuple[str, str], int] | None = None,
    run_id: str = "",
    prompts_dir: Path | None = None,
    llm_call: Any = None,
) -> ReviewResult:
    """Core C1 review pipeline (LLM call is injectable for offline tests)."""
    candidates = [c for c in retrieve.get("candidates") or [] if isinstance(c, dict)]
    judge_index = judge_index or {}
    if not candidates:
        return ReviewResult(review_copies=[], errors=[])

    template = load_c1_template(prompts_dir)
    persona_semantic = representative_persona_semantic(retrieve)
    news_context = build_news_context(news, persona_semantic)
    candidates_block = format_candidates_block(candidates)
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
        )

    raw = (raw or "").strip()
    if not raw:
        return ReviewResult(
            review_copies=[],
            errors=[{"type": "llm_error", "message": "empty LLM response"}],
        )

    blocks = split_into_paragraphs(raw)
    pairs, map_errors = map_paragraphs_to_candidates(blocks, candidates)
    copies = assemble_review_copies(pairs, judge_index, run_id)
    return ReviewResult(review_copies=copies, errors=map_errors)


def review_copy_to_dict(copy: ReviewCopy) -> dict[str, Any]:
    return {
        "tmdb_id": copy.tmdb_id,
        "title": copy.title,
        "year": copy.year,
        "triggered_by": copy.triggered_by,
        "center_dimensions": copy.center_dimensions,
        "judge_score": copy.judge_score,
        "movie_url": copy.movie_url,
        "text_zh": copy.text_zh,
    }


def result_to_payload(result: ReviewResult) -> dict[str, Any]:
    return {
        "review_copies": [review_copy_to_dict(c) for c in result.review_copies],
        "errors": result.errors,
    }


def _infer_run_id(retrieve_path: Path) -> str:
    """Best-effort run id (== news dir name) for judge backfill keying."""
    parent = retrieve_path.parent.name
    return parent.strip()


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

    result = run_review(
        retrieve,
        news,
        provider=args.provider,
        judge_index=judge_index,
        run_id=run_id,
    )
    payload = result_to_payload(result)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = _REPO_ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(serialized + "\n", encoding="utf-8")
        print(f"Wrote {out_path.resolve()}", file=sys.stderr)
    else:
        sys.stdout.buffer.write((serialized + "\n").encode("utf-8"))

    if not result.review_copies and retrieve.get("candidates"):
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
        "--out",
        help="Write review JSON to this path; otherwise print UTF-8 JSON to stdout.",
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