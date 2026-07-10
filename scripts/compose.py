"""compose.py · C1/C2 copywriter (Phase 4).

Stage ``review`` (C1): read a ``candidates.json`` candidate pool plus news context,
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

from math import floor, log10
import os
import re
import sys
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from openai import OpenAI

from scripts.lib.env import default_llm_provider, load_env
from scripts.lib.llm import get_llm_client
from scripts.lib.movie_labels import GENRE_EN_TO_ZH, LANG_CODE_TO_ZH
from scripts.lib.paths import repo_root
from scripts.movie_metadata import get_movie_detail_by_tmdb_id, get_tmdb_zh_title_by_tmdb_id

_MODEL_ENV: dict[str, str] = {
    "mimo": "MIMO_MODEL",
    "deepseek": "DEEPSEEK_MODEL",
}

_C1_PROMPT_REL = "prompts/compose_review.md"
# C2 发布稿 prompt 按平台选取（ADR-0015 D1）：prompts/compose_publish_<platform>.md。
_C2_PROMPT_FILENAME = "compose_publish_{platform}.md"
# headline-only 重生成 prompt（ADR-0016 D3）：body-aware，只吃现有正文重出标题，
# 与 monolithic 首发稿 _C2_PROMPT_FILENAME 分开选取，不共用同一份模板。
_HEADLINE_PROMPT_FILENAME = "compose_publish_{platform}_headline.md"
_DEFAULT_PLATFORM = "xiaohongshu"
_PLATFORMS: tuple[str, ...] = ("xiaohongshu",)

# headline 硬规则单一事实源（ADR-0016 D1）：monolithic 首发稿与 headline-only 重生成稿
# 共享同一份契约文件，通过 {{headline_contract}} 占位符注入，防止两处规则各写一份而漂移。
_HEADLINE_CONTRACT_REL = "prompts/_shared/xiaohongshu_headline_contract.md"

# persona 视角蒸馏文件（ADR-0017 D1）：C2 侧 persona 视角单一事实源，与 persona_card.md
# 同目录共置。C2 加载路径只认 c2_perspective.md，永不读 persona_card.md（防行话泄漏）。
_C2_PERSPECTIVE_FILENAME = "c2_perspective.md"

_SUPERSCRIPTS = str.maketrans("0123456789", "⁰¹²³⁴⁵⁶⁷⁸⁹")


def _progress(message: str) -> None:
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    print(f"{ts} {message}", file=sys.stderr, flush=True)


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

# Publish fallback: remove LLM-emitted header-ish lines if the prompt leaks them.
_PUBLISH_TITLE_LINE_RE = re.compile(
    r"^\s*(?:《.+?》|[^/／\n]+(?:\s*[/／]\s*[^/／\n]+){1,2})\s*$"
)
_PUBLISH_ATTRIBUTION_LINE_RE = re.compile(
    r"^\s*(?:「.+?」|《.+?》)(?:\s*[（(]\s*\d{3,4}\s*[)）])?(?:\s+[^。！？!?]+)?\s*$"
)
_PUBLISH_SIMPLE_META_RE = re.compile(
    r"^\s*(?:title|director|片名|导演|原片名|中文译名)\s*[：:]\s*.+$",
    re.IGNORECASE,
)
_PUBLISH_META_PREFIXES: tuple[str, ...] = (
    "坐标：",
    "文明：",
    "类型：",
    "光度：",
    "体积：",
    "导演：",
    "年份：",
    "片名：",
    "评分：",
    "时长：",
    "片长：",
    "title：",
    "director：",
    "title:",
    "director:",
    "原片名：",
    "中文译名：",
)

# ADR-0015 D4 sentinel 契约：publish LLM 输出用这两个标记分隔标题与正文，
# sentinel 由 parse_publish_output 剥离，不进成品。
_HEADLINE_SENTINEL = "【标题】"
_BODY_SENTINEL = "【正文】"

_SYSTEM_MESSAGE = (
    "你是「每日星轨观测」的编辑助理。严格按用户消息中的契约输出选片决策卡，"
    "每部候选电影一块，块首标注《片名》(年份)，块内只保留 judge 投影与双语直译字段。"
    "不要输出标题、读者文案、电影介绍、Hashtag 或任何发布稿内容。"
)

# C2 发布稿（创作环节）专用 system message。决策卡 message 明写「不要输出标题」，
# 与 headline + 读者正文直接冲突（ADR-0015 D4 / 风险清单），故 publish 单独一份：
# 允许并要求产出标题 + 正文，但正文首行的电影抬头 / 元信息由下游代码拼装，
# 模型只负责正文内容本身；同时守 ADR-0013 平视调性与 sentinel 契约。
_PUBLISH_SYSTEM_MESSAGE = (
    "你是「每日星轨观测」的发布稿创作者，为总编选定的 1 部电影写一版小红书笔记："
    "一句标题 + 一段中文正文，遵循影像平权的平视调性（不排名 / 不盖章 / 不煽动 / "
    "数字文字化 / 不回显输入结构 / 不编造）。严格按用户消息里的 sentinel 契约输出："
    "【标题】一行标题，随后 【正文】一段正文。正文里不要输出任何片名行、抬头行、元信息行（片名、年份、导演、类型、评分、时长等），"
    "这些由下游程序拼装；也不要输出电影链接、决策卡、字段键值、Hashtag 或任何额外说明。"
)

# headline-only 重生成（ADR-0016 D3）专用 system message。与 _PUBLISH_SYSTEM_MESSAGE
# 不同：这里只允许模型产一句标题，不产正文，因为下游只取 headline 字段（body 仍由
# run_publish 走首发路径产出，此路径不碰正文），避免模型误吐正文块与 sentinel 契约冲突。
_HEADLINE_SYSTEM_MESSAGE = (
    "你是「每日星轨观测」的标题重生成助理，只为总编已有的一版正文重出一句小红书标题，"
    "不产正文、不改正文。遵循影像平权的平视调性（不排名 / 不盖章 / 不煽动 / 数字文字化 / "
    "不回显输入结构 / 不编造）。严格按用户消息里的 sentinel 契约输出：只写 "
    "【标题】一行标题，这一行。不要输出【正文】、正文内容、字段键值、Hashtag、电影链接"
    "或任何额外说明。"
)

# Fixed field prefixes the LLM emits inside each decision card (DSL contract).
_CARD_FIELD_PREFIXES: dict[str, str] = {
    "judge_score:": "judge_score_text",
    "resonance_type:": "resonance_type_text",
    "causal_test_en:": "causal_test_en_text",
    "causal_test_zh:": "causal_test_zh",
    "rationale_en:": "rationale_en_text",
    "rationale_zh:": "rationale_zh",
}

_DB_PROJECTION_FIELDS: tuple[str, ...] = (
    "id",
    "title",
    "original_title",
    "overview",
    "genres",
    "release_date",
    "runtime",
    "director",
    "cast",
    "writers",
    "production_countries",
    "vote_average",
    "vote_count",
    "popularity",
    "imdb_rating",
    "imdb_votes",
)


@dataclass
class JudgeEntry:
    """One thinking-judge row: screening score plus its rationale (EN原文)."""

    score: int | None = None
    rationale: str = ""
    causal_test: str = ""
    resonance_type: str = ""


@dataclass
class ReviewCopy:
    """One editor-facing decision card mapped back to its candidate.

    The card is intentionally non-creative: movie facts come from DB projection,
    judge evidence comes from the thinking judge, and the LLM only provides faithful
    Chinese translations for the English judge fields.
    """

    tmdb_id: int | str
    title: str
    year: int | None
    triggered_by: list[str]
    center_dimensions: list[str]
    db_projection: dict[str, Any] = field(default_factory=dict)
    movie_url: str = ""
    news_url: str = ""
    judge_score: int | None = None
    judge_rationale_en: str = ""
    judge_causal_test_en: str = ""
    judge_resonance_type: str = ""
    judge_rationale_zh: str = ""
    judge_causal_test_zh: str = ""


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
    """Load a candidates.json product; require a ``candidates`` list."""
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
        "url": str(
            data.get("url")
            or data.get("source_url")
            or data.get("link")
            or data.get("article_url")
            or ""
        ).strip(),
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


def _dedupe_segments(parts: list[str]) -> list[str]:
    deduped: list[str] = []
    for part in parts:
        text = str(part or "").strip()
        if text and text not in deduped:
            deduped.append(text)
    return deduped


def _format_release_date(raw: Any) -> str:
    text = str(raw or "").strip()
    if len(text) >= 10 and text[:4].isdigit() and text[5:7].isdigit() and text[8:10].isdigit():
        return f"[Y: {text[:4]}, M: {text[5:7]}, D: {text[8:10]}]"
    return "未知"


def _language_display(code: Any) -> str:
    raw = str(code or "").strip()
    if not raw:
        return ""
    upper = raw.upper()
    label = LANG_CODE_TO_ZH.get(raw.lower(), "")
    return f"{upper} {label}".strip() if label else upper


def _vote_count_magnitude(vote_count: Any) -> str:
    text = str(vote_count or "").strip()
    if not text:
        return ""
    try:
        value = float(text)
    except (TypeError, ValueError):
        return ""
    if value <= 0:
        return ""
    magnitude = int(floor(log10(value)))
    return str(magnitude).translate(_SUPERSCRIPTS)


def _volume_display(proj: dict[str, Any]) -> str:
    """Render volume only from vote_count.

    If vote_count is missing, empty, zero, or invalid, keep the header clean and
    omit the line instead of pretending runtime is a volume proxy.
    """
    vote_count = proj.get("vote_count")
    magnitude = _vote_count_magnitude(vote_count)
    if not magnitude:
        return ""
    return f"{vote_count} - 10{magnitude} 投票级别"


def _split_genre_values(genres: Any) -> list[str]:
    if isinstance(genres, list):
        return [str(item).strip() for item in genres if str(item).strip()]
    if isinstance(genres, str):
        raw = genres.replace("|", ",")
        return [part.strip() for part in raw.split(",") if part.strip()]
    return []


def render_movie_header(proj: dict[str, Any]) -> str:
    """Render a deterministic movie header block for C2 output."""
    zh_title = str(proj.get("zh_title") or "").strip()
    original_title = str(proj.get("original_title") or proj.get("title") or "").strip()
    title = str(proj.get("title") or original_title or "").strip()
    language = str(proj.get("original_language") or "").strip()

    title_parts: list[str] = []
    if zh_title:
        title_parts.append(f"「{zh_title}」")
    if language.lower() == "en":
        title_parts.extend([title, original_title])
    elif original_title or title:
        # 非英语影片：优先原片名，不主动兜底拼出中文译名以外的重复抬头。
        title_parts.extend([original_title, title])
    title_parts = _dedupe_segments(title_parts)
    if not title_parts and title:
        title_parts = [title]

    lines: list[str] = []
    if title_parts:
        lines.append(" / ".join(title_parts))

    director = str(proj.get("director") or "").strip()
    if director:
        lines.append(director)

    lines.append("")

    release_line = _format_release_date(proj.get("release_date"))
    lines.append(f"坐标：{release_line}" if release_line != "未知" else "坐标：未知")

    language_line = _language_display(language)
    if language_line:
        lines.append(f"文明：{language_line}")

    genres = _split_genre_values(proj.get("genres"))
    if genres:
        mapped = [GENRE_EN_TO_ZH.get(genre, genre) for genre in genres]
        lines.append(f"类型：{'，'.join(mapped)}")

    vote_average = proj.get("vote_average")
    if vote_average not in (None, ""):
        lines.append(f"光度：{vote_average}/10")

    volume_text = _volume_display(proj)
    if volume_text:
        lines.append(f"体积：{volume_text}")

    return "\n".join(lines).strip()


def _detail_year(detail: dict[str, Any]) -> int | None:
    raw = detail.get("release_date")
    text = str(raw or "").strip()
    if len(text) >= 4 and text[:4].isdigit():
        return int(text[:4])
    return None


def _candidate_tmdb_id(candidate: dict[str, Any]) -> int | str | None:
    raw = candidate.get("tmdb_id")
    if raw in (None, ""):
        raw = candidate.get("id")
    if raw in (None, ""):
        return None
    return raw


def _candidate_zh_title(
    candidate: dict[str, Any],
    tmdb_id: int | str | None = None,
    zh_title_loader=None,
) -> str:
    zh_title = str(candidate.get("zh_title") or "").strip()
    if zh_title:
        return zh_title
    if tmdb_id in (None, ""):
        tmdb_id = _candidate_tmdb_id(candidate)
    if tmdb_id in (None, ""):
        return ""
    if zh_title_loader is None:
        zh_title_loader = get_tmdb_zh_title_by_tmdb_id
    try:
        return zh_title_loader(tmdb_id)
    except Exception:
        return ""


def build_header_projection(
    candidate: dict[str, Any],
    movie_detail_loader=None,
    zh_title_loader=None,
) -> dict[str, Any]:
    """Build a deterministic movie-header projection from retrieve candidate facts.

    The loader is injectable so tests can stub it and avoid touching cleaned.csv.
    Any loader failure, missing file, or missing detail row degrades softly to the
    candidate-only projection.
    """
    if movie_detail_loader is None:
        movie_detail_loader = get_movie_detail_by_tmdb_id
    if zh_title_loader is None:
        zh_title_loader = get_tmdb_zh_title_by_tmdb_id
    tmdb_id = _candidate_tmdb_id(candidate)
    direct_zh_title = str(candidate.get("zh_title") or "").strip()
    if not direct_zh_title:
        direct_zh_title = _candidate_zh_title(candidate, tmdb_id, zh_title_loader=zh_title_loader)
    projection: dict[str, Any] = {
        "tmdb_id": tmdb_id,
        "id": tmdb_id,
        "title": str(candidate.get("title") or "").strip(),
        "original_title": str(candidate.get("original_title") or "").strip(),
        "genres": candidate.get("genres"),
        "release_date": candidate.get("release_date"),
        "original_language": candidate.get("original_language"),
        "zh_title": direct_zh_title,
    }

    if tmdb_id in (None, ""):
        return projection

    try:
        detail = movie_detail_loader(tmdb_id)
    except Exception:
        detail = None
    if not isinstance(detail, dict):
        detail = {}

    for key in _DB_PROJECTION_FIELDS:
        value = detail.get(key)
        if value not in (None, "") and key not in projection:
            projection[key] = value

    for key in ("title", "original_title", "genres", "release_date", "original_language"):
        value = projection.get(key)
        if value in (None, "") and detail.get(key) not in (None, ""):
            projection[key] = detail.get(key)

    return projection


def _db_projection_for_candidate(candidate: dict[str, Any]) -> dict[str, Any]:
    projection = build_header_projection(candidate)
    detail_projection = {
        key: value
        for key, value in projection.items()
        if key in _DB_PROJECTION_FIELDS and value not in (None, "")
    }
    if "release_date" not in detail_projection and projection.get("release_date"):
        detail_projection["release_year"] = _candidate_year(candidate)
    return detail_projection


def _format_db_projection(projection: dict[str, Any]) -> str:
    if not projection:
        return "（无 DB 明细）"
    lines: list[str] = []
    for key in _DB_PROJECTION_FIELDS:
        if key not in projection:
            continue
        value = projection[key]
        if value is None or str(value).strip() == "":
            continue
        lines.append(f"     - {key}: {value}")
    if "release_year" in projection:
        lines.append(f"     - release_year: {projection['release_year']}")
    return "\n".join(lines) if lines else "（无 DB 明细）"


def clean_publish_body(body: str) -> str:
    """清洗 publish 正文：剥除 LLM 误吐的书名号标题行、元信息行与电影链接。

    归属行 `「片名」(YYYY) 导演名` 由创作环节保留；若 LLM 误吐 title/director
    这类抬头行，或把标题/导演重新排成元信息行，本函数会再次剥掉，避免只靠 prompt。
    """
    kept: list[str] = []
    for line in (body or "").splitlines():
        stripped = line.strip()
        if not stripped:
            kept.append(line)
            continue
        if _TITLE_LINE_RE.match(stripped):
            continue  # 剥除 LLM 误吐的《片名》(年份)；「片名」(YYYY) 归属行保留
        if _PUBLISH_TITLE_LINE_RE.match(stripped):
            continue
        if _PUBLISH_ATTRIBUTION_LINE_RE.match(stripped):
            continue
        if _PUBLISH_SIMPLE_META_RE.match(stripped):
            continue
        if any(stripped.startswith(prefix) for prefix in _PUBLISH_META_PREFIXES):
            continue
        if stripped.startswith("https://themoviecosmos.com/movie/"):
            continue  # 剥除 LLM 误吐的链接
        kept.append(line)
    return "\n".join(kept).strip()


def format_selected_movie_block(candidate: dict[str, Any]) -> str:
    projection = _db_projection_for_candidate(candidate)
    title = str(projection.get("title") or candidate.get("title") or "").strip()
    year = _detail_year(projection) or _candidate_year(candidate)
    year_str = str(year) if year is not None else "—"
    tmdb_id = candidate.get("tmdb_id") or projection.get("id") or ""
    movie_url = str(candidate.get("movie_url") or "").strip()
    lines = [f"《{title}》({year_str}) — tmdb_id: {tmdb_id}", "DB 字段:"]
    lines.append(_format_db_projection(projection))
    if movie_url:
        lines.append(f"电影链接: {movie_url}")
    return "\n".join(lines)


def format_judge_kernel(judge: JudgeEntry | None) -> str:
    if judge is None:
        return "（无 judge 内核）"
    score = "" if judge.score is None else str(judge.score)
    return "\n".join(
        [
            f"judge_score: {score or '（无）'}",
            f"resonance_type: {judge.resonance_type or '（无）'}",
            f"causal_test: {judge.causal_test or '（无）'}",
            f"rationale: {judge.rationale or '（无）'}",
        ]
    )


def parse_publish_output(raw: str) -> tuple[str, str]:
    """按 ADR-0015 D4 sentinel 契约把 publish LLM 原始输出解析为 (headline, body)。

    契约：``【标题】<一行标题>\\n【正文】\\n<正文…>``。解析规则：
    - 以 ``【正文】`` 切分：其前段取 ``【标题】`` 之后的首行为 headline，其后段为 body。
    - 缺 ``【正文】`` 时退化：若有 ``【标题】``，其后首行作 headline、余下作 body；
      两个 sentinel 都缺时 headline 为空、整段作 body（交由上层按「body 空则失败」
      判定，不静默出半稿）。
    headline 只取首行（LLM 若误吐多行标题，仅保留第一行）。
    """
    text = raw or ""
    if _BODY_SENTINEL in text:
        head_part, _, body_part = text.partition(_BODY_SENTINEL)
        body = body_part.strip()
        if _HEADLINE_SENTINEL in head_part:
            head_part = head_part.split(_HEADLINE_SENTINEL, 1)[1]
        headline = head_part.strip()
    elif _HEADLINE_SENTINEL in text:
        after = text.split(_HEADLINE_SENTINEL, 1)[1]
        lines = after.splitlines()
        headline = lines[0].strip() if lines else ""
        body = "\n".join(lines[1:]).strip()
    else:
        headline = ""
        body = text.strip()
    headline = headline.splitlines()[0].strip() if headline else ""
    return headline, body


def run_publish(
    candidate: dict[str, Any],
    news: dict[str, str],
    *,
    provider: str | None = None,
    judge: JudgeEntry | None = None,
    platform: str = _DEFAULT_PLATFORM,
    prompts_dir: Path | None = None,
    persona_perspective: str = "",
    llm_call: Any = None,
) -> dict[str, Any]:
    """Single-movie platform publish draft: the only creative compose step.

    产「电影 id + 标题(headline) + 正文(body)」结构化产物（ADR-0015 D4）；正文内容由 LLM 产出后再由代码前置确定性电影抬头，链接与平台呈现规则留给下游平台适配阶段。
    ``platform`` 选取 ``compose_publish_<platform>.md``（默认 xiaohongshu）。
    ``persona_perspective`` 注入 C2 主视角（ADR-0017 D2）；空串 = 现有默认行为，
    首发 publish / 9.8 重生成路径零回归。
    """
    template = load_c2_template(platform, prompts_dir)
    news_context = build_news_context(news, "")
    selected_movie = format_selected_movie_block(candidate)
    judge_kernel = format_judge_kernel(judge)
    # ADR-0016 D1：注入 headline 硬规则共享契约，monolithic 不再自带一份规则文本。
    headline_contract = load_headline_contract(prompts_dir)
    prompt = render_c2_prompt(
        template,
        news_context,
        selected_movie,
        judge_kernel,
        headline_contract,
        persona_perspective,
    )

    if llm_call is not None:
        raw = str(llm_call(prompt) or "").strip()
    else:
        load_env()
        resolved = _resolve_provider(provider)
        client = get_llm_client(resolved)
        model = _model_name(resolved)
        raw = _sync_llm_call(client, model, prompt, _PUBLISH_SYSTEM_MESSAGE)

    headline, body = parse_publish_output(raw)
    body = clean_publish_body(body)
    header = render_movie_header(build_header_projection(candidate))
    body = f"{header}\n\n{body}" if body else header
    return {
        "tmdb_id": candidate.get("tmdb_id"),
        "headline": headline,
        "body": body,
    }


def run_headline(
    candidate: dict[str, Any],
    news: dict[str, str],
    current_body: str,
    *,
    provider: str | None = None,
    judge: JudgeEntry | None = None,
    platform: str = _DEFAULT_PLATFORM,
    prompts_dir: Path | None = None,
    llm_call: Any = None,
) -> dict[str, Any]:
    """headline-only、body-aware 重生成（ADR-0016 D3）：只重出标题，不碰正文。

    正文重生成不设独立函数——下游适配器（后续 TODO）直接复用 run_publish 并只取其
    ``body``。本函数只贴合 ``current_body`` 重出一句标题，供总编「只改标题」时调用。
    """
    # judge 当前未被 headline prompt 消费（该 prompt 无 judge 占位符，是有意的
    # judge-free 设计）；参数保留仅为与 run_publish 签名对齐，供未来复用。
    template = load_headline_template(platform, prompts_dir)
    news_context = build_news_context(news, "")
    selected_movie = format_selected_movie_block(candidate)
    headline_contract = load_headline_contract(prompts_dir)
    prompt = render_headline_prompt(
        template, news_context, selected_movie, current_body, headline_contract
    )

    if llm_call is not None:
        raw = str(llm_call(prompt) or "").strip()
    else:
        load_env()
        resolved = _resolve_provider(provider)
        client = get_llm_client(resolved)
        model = _model_name(resolved)
        raw = _sync_llm_call(client, model, prompt, _HEADLINE_SYSTEM_MESSAGE)

    # 复用 parse_publish_output 的 headline 分支：即使模型误吐多行，也只取首行，
    # 无需为 headline-only 另写一套解析逻辑（ADR-0016 D3）。
    headline, _ = parse_publish_output(raw)
    return {
        "tmdb_id": candidate.get("tmdb_id"),
        "headline": headline,
    }


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
        detail_projection = _db_projection_for_candidate(cand)
        year = _detail_year(detail_projection) or _candidate_year(cand)
        year_str = str(year) if year is not None else "—"
        triggered = [str(p) for p in cand.get("triggered_by") or [] if str(p).strip()]
        dims = _dimension_phrase(_candidate_center_dimensions(cand))
        movie_url = str(cand.get("movie_url", "") or "").strip()
        judge = _lookup_judge(judge_index, run_id, cand.get("tmdb_id"))

        lines.append(f"{idx}. 《{title}》({year_str})")
        lines.append("   - DB 投影（照事实使用，不要改写）:")
        lines.append(_format_db_projection(detail_projection))
        lines.append(f"   - 被这些视角击中: {_persona_phrase(triggered)}")
        if dims:
            lines.append(f"   - 切面（可选参考，非强制聚焦）: {dims}")
        if movie_url:
            lines.append(f"   - 电影链接: {movie_url}")
        if judge is not None:
            score = "" if judge.score is None else str(judge.score)
            lines.append(f"   - judge_score: {score}")
            lines.append(f"   - resonance_type: {judge.resonance_type or '（无）'}")
            lines.append(f"   - causal_test_en: {judge.causal_test or '（无）'}")
            lines.append(f"   - rationale_en: {judge.rationale or '（无）'}")
        else:
            lines.append("   - judge_score: （无）")
            lines.append("   - resonance_type: （无）")
            lines.append("   - causal_test_en: （无）")
            lines.append("   - rationale_en: （无）")
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
    url = news.get("url", "").strip()
    if url:
        parts.append(f"原文链接: {url}")
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


def load_c2_template(
    platform: str = _DEFAULT_PLATFORM, prompts_dir: Path | None = None
) -> str:
    """按平台选取 C2 发布 prompt（ADR-0015 D1）：compose_publish_<platform>.md。"""
    filename = _C2_PROMPT_FILENAME.format(platform=platform)
    base = prompts_dir or (repo_root() / "prompts")
    path = base / filename
    if not path.is_file():
        path = repo_root() / "prompts" / filename
    if not path.is_file():
        raise FileNotFoundError(
            f"C2 prompt not found for platform {platform!r}: {path}"
        )
    return path.read_text(encoding="utf-8")


def render_c2_prompt(
    template: str,
    news_context: str,
    selected_movie: str,
    judge_kernel: str,
    headline_contract: str = "",
    persona_perspective: str = "",
) -> str:
    rendered = template.replace("{{news_context}}", news_context or "（无新闻语境）")
    rendered = rendered.replace("{{selected_movie}}", selected_movie or "（无选定电影）")
    rendered = rendered.replace("{{judge_kernel}}", judge_kernel or "（无 judge 内核）")
    # ADR-0016 D1：headline 规则单一事实源注入；模板无此占位符时 replace 为 no-op，
    # 渲染结果与抽取前完全一致（向后兼容，见 golden-snapshot 测试）。
    rendered = rendered.replace("{{headline_contract}}", headline_contract or "")
    # ADR-0017 D2：persona 主视角注入，完全复刻 headline_contract 的 no-op 模式——
    # 空串 = 默认平视调性（首发 publish / 9.8 重生成路径零回归，golden-snapshot 兜底）。
    rendered = rendered.replace("{{persona_perspective}}", persona_perspective or "")
    return rendered


def load_persona_perspective(
    persona_id: str, prompts_dir: Path | None = None
) -> str:
    """加载某 persona 的 C2 侧蒸馏视角（ADR-0017 D1）。

    ``persona_id`` 归一化：``triggered_by`` 用 ``THE-SAGE`` 大写连字符，persona 目录用
    ``The-Sage`` 首字母大写；按 hyphen 段做 title-case 归一（``THE-SAGE`` → ``The-Sage``）。
    查找顺序与 load_c2_template 一致：优先 prompts_dir/personas/…，回退 repo 根路径。
    只认 c2_perspective.md，缺文件 → 清晰报错（禁回退读 persona_card.md）。
    """
    normalized = "-".join(part.capitalize() for part in persona_id.split("-"))
    base = prompts_dir or (repo_root() / "prompts")
    path = base / "personas" / normalized / _C2_PERSPECTIVE_FILENAME
    if not path.is_file():
        path = repo_root() / "prompts" / "personas" / normalized / _C2_PERSPECTIVE_FILENAME
    if not path.is_file():
        raise FileNotFoundError(
            f"c2_perspective not found for persona {persona_id!r} "
            f"(normalized {normalized!r}): {path}"
        )
    return path.read_text(encoding="utf-8").strip()


def load_headline_contract(prompts_dir: Path | None = None) -> str:
    """加载 headline 硬规则共享契约（ADR-0016 D1 SSOT），供 render_c2_prompt 注入。

    查找顺序与 load_c2_template 一致：优先 prompts_dir/_shared/…，回退 repo 根路径。
    """
    base = prompts_dir or (repo_root() / "prompts")
    path = base / "_shared" / "xiaohongshu_headline_contract.md"
    if not path.is_file():
        path = repo_root() / _HEADLINE_CONTRACT_REL
    if not path.is_file():
        raise FileNotFoundError(f"headline contract not found: {path}")
    return path.read_text(encoding="utf-8")


def load_headline_template(
    platform: str = _DEFAULT_PLATFORM, prompts_dir: Path | None = None
) -> str:
    """按平台选取 headline-only 重生成 prompt（ADR-0016 D3）：沿用 load_c2_template 查找模式。"""
    filename = _HEADLINE_PROMPT_FILENAME.format(platform=platform)
    base = prompts_dir or (repo_root() / "prompts")
    path = base / filename
    if not path.is_file():
        path = repo_root() / "prompts" / filename
    if not path.is_file():
        raise FileNotFoundError(
            f"headline prompt not found for platform {platform!r}: {path}"
        )
    return path.read_text(encoding="utf-8")


def render_headline_prompt(
    template: str,
    news_context: str,
    selected_movie: str,
    current_body: str,
    headline_contract: str = "",
) -> str:
    rendered = template.replace("{{news_context}}", news_context or "（无新闻语境）")
    rendered = rendered.replace("{{selected_movie}}", selected_movie or "（无选定电影）")
    rendered = rendered.replace("{{current_body}}", current_body or "（无当前正文）")
    rendered = rendered.replace("{{headline_contract}}", headline_contract or "")
    return rendered


def render_c1_prompt(template: str, news_context: str, candidates_block: str) -> str:
    rendered = template.replace("{{news_context}}", news_context or "（无新闻语境）")
    rendered = rendered.replace("{{candidates}}", candidates_block or "（无候选）")
    return rendered


def _sync_llm_call(
    client: OpenAI,
    model: str,
    user_prompt: str,
    system_message: str = _SYSTEM_MESSAGE,
) -> str:
    messages = [
        {"role": "system", "content": system_message},
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
    news_url: str = "",
) -> list[ReviewCopy]:
    copies: list[ReviewCopy] = []
    for cand, text in pairs:
        if not text.strip():
            continue
        tmdb_id = cand.get("tmdb_id")
        judge = _lookup_judge(judge_index, run_id, tmdb_id)
        card = parse_card_fields(text)
        db_projection = _db_projection_for_candidate(cand)
        copies.append(
            ReviewCopy(
                tmdb_id=tmdb_id,
                title=str(cand.get("title", "") or ""),
                year=_detail_year(db_projection) or _candidate_year(cand),
                triggered_by=[
                    str(p) for p in cand.get("triggered_by") or [] if str(p).strip()
                ],
                center_dimensions=_candidate_center_dimensions(cand),
                db_projection=db_projection,
                movie_url=str(cand.get("movie_url", "") or ""),
                news_url=news_url,
                judge_score=judge.score if judge else None,
                judge_rationale_en=judge.rationale if judge else "",
                judge_causal_test_en=judge.causal_test if judge else "",
                judge_resonance_type=judge.resonance_type if judge else "",
                judge_rationale_zh=card.get("rationale_zh", ""),
                judge_causal_test_zh=card.get("causal_test_zh", ""),
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
    judge_index: dict[tuple[str, str], JudgeEntry] | None = None,
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
    copies = assemble_review_copies(
        pairs,
        judge_index,
        run_id,
        news_url=str(news.get("url", "") or "").strip(),
    )
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
        "db_projection": copy.db_projection,
        "movie_url": copy.movie_url,
        "news_url": copy.news_url,
        "judge": {
            "score": copy.judge_score,
            "resonance_type": copy.judge_resonance_type,
            "causal_test": {
                "en": copy.judge_causal_test_en,
                "zh": copy.judge_causal_test_zh,
            },
            "rationale": {
                "en": copy.judge_rationale_en,
                "zh": copy.judge_rationale_zh,
            },
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
    """Render one non-creative decision card into Obsidian-readable Markdown."""
    year_str = str(copy.year) if copy.year is not None else "—"
    lines = [f"### 《{copy.title}》({year_str})"]

    if copy.db_projection:
        lines.append("- DB 投影:")
        for key in _DB_PROJECTION_FIELDS:
            value = copy.db_projection.get(key)
            if value is not None and str(value).strip():
                lines.append(f"  - {key}: {value}")
        if copy.db_projection.get("release_year") is not None:
            lines.append(f"  - release_year: {copy.db_projection['release_year']}")

    if copy.triggered_by:
        lines.append(f"- 触发视角: {', '.join(copy.triggered_by)}")
    if copy.center_dimensions:
        lines.append(f"- 切面（可选参考）: {', '.join(copy.center_dimensions)}")
    if copy.judge_score is not None:
        lines.append(f"- judge_score（screening-only）: {copy.judge_score}")
    if copy.judge_resonance_type.strip():
        lines.append(f"- resonance_type: {copy.judge_resonance_type.strip()}")
    if copy.judge_causal_test_en.strip():
        lines.append(f"- causal_test EN: {copy.judge_causal_test_en.strip()}")
    if copy.judge_causal_test_zh.strip():
        lines.append(f"- causal_test ZH: {copy.judge_causal_test_zh.strip()}")
    if copy.judge_rationale_en.strip():
        lines.append(f"- rationale EN: {copy.judge_rationale_en.strip()}")
    if copy.judge_rationale_zh.strip():
        lines.append(f"- rationale ZH: {copy.judge_rationale_zh.strip()}")
    if copy.news_url:
        lines.append(f"- 新闻原文链接: {copy.news_url}")
    if copy.movie_url:
        lines.append(f"- 电影链接: {copy.movie_url}")
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
    header: list[str] = ["# 选片决策卡（Decision Card · 待总编肉眼审核）"]
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
    if not args.retrieve_json:
        print("error: --retrieve-json is required for review", file=sys.stderr)
        return 2
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

    review_start = time.perf_counter()
    candidate_count = len([c for c in retrieve.get("candidates") or [] if isinstance(c, dict)])
    _progress(f"[compose] review start candidates={candidate_count}")
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

    done_target = str(out_path.resolve()) if out_path is not None else "stdout"
    _progress(f"[compose] review done -> {done_target} ({time.perf_counter() - review_start:.1f}s)")

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


def _run_publish_cli(args: argparse.Namespace) -> int:
    if not args.retrieve_json:
        print("error: --retrieve-json is required for publish", file=sys.stderr)
        return 2
    if not args.tmdb_id:
        print("error: --tmdb-id is required for publish", file=sys.stderr)
        return 2

    retrieve_path = Path(args.retrieve_json)
    if not retrieve_path.is_absolute():
        retrieve_path = _REPO_ROOT / retrieve_path
    if not retrieve_path.is_file():
        print(f"error: retrieve JSON not found: {retrieve_path}", file=sys.stderr)
        return 2
    retrieve = load_retrieve(retrieve_path)
    candidate = next(
        (
            c
            for c in retrieve.get("candidates") or []
            if isinstance(c, dict) and str(c.get("tmdb_id")) == str(args.tmdb_id)
        ),
        None,
    )
    if candidate is None:
        print(f"error: tmdb_id not found in candidates: {args.tmdb_id}", file=sys.stderr)
        return 2

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
    judge = _lookup_judge(judge_index, run_id, args.tmdb_id)

    try:
        draft = run_publish(
            candidate,
            news,
            provider=args.provider,
            judge=judge,
            platform=args.platform,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 1

    # C2 产物契约（ADR-0015 D4）：电影 id + headline + body，序列化为 JSON。
    serialized = json.dumps(draft, ensure_ascii=False, indent=2)

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
    return 0 if str(draft.get("body", "")).strip() else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compose: editor-facing decision cards (Phase 4 4.3-fix).",
    )
    parser.add_argument(
        "--stage",
        choices=["review", "publish"],
        default="review",
        help="Pipeline stage: review decision card or single-movie publish draft.",
    )
    parser.add_argument(
        "--retrieve-json",
        dest="retrieve_json",
        required=False,
        help="Path to candidates.json (review consumes candidates[]; publish selects one candidate).",
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
        help="Run id for judge keying (default: candidates.json parent dir name).",
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
    parser.add_argument(
        "--tmdb-id",
        dest="tmdb_id",
        help="Selected TMDB id for --stage publish.",
    )
    parser.add_argument(
        "--platform",
        choices=list(_PLATFORMS),
        default=_DEFAULT_PLATFORM,
        help=(
            "Publish platform for --stage publish (default: xiaohongshu). "
            "Selects prompts/compose_publish_<platform>.md."
        ),
    )
    args = parser.parse_args(argv)

    try:
        if args.stage == "publish":
            return _run_publish_cli(args)
        return _run_review_cli(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())