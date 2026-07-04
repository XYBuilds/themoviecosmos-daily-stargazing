"""LLM-as-judge resonance scorer with observation-set calibration (Phase 3.9.4 / 3.10.1).

Scores candidates 0/1/2 plus resonance type per dual-axis rubric (ADR-0007 D1;
authority: ``prompts/_shared/resonance_definition_v2.md``).
Calibration on observation-set human scores (runs 01–04); below alignment
threshold marks judge output as 不采信 (screening only).
"""

from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import UTC, datetime
import json
import re
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Callable

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.eval_batch_manifest import load_manifest
from scripts.lib.env import default_llm_provider, load_env
from scripts.lib.llm import get_llm_client
from scripts.resonance_rubric import (
    SUB_LABEL_POV_TRANSFORM,
    TYPE_DEEP,
    TYPE_NONE,
    TYPE_STRONG,
    TYPE_SURFACE,
    parse_pov_transform,
    parse_resonance_type,
    validate_pov_transform_sub_label,
    validate_score_type_pair,
)
from scripts.run_persona_batch import OBS_RUN_PREFIXES, split_obs_holdout
from scripts.summarize_eval import (
    _pearson,
    parse_eval_markdown,
    parse_unified_review,
)

_JUDGE_SCHEMA_VERSION = 4
_VALID_SCORES = frozenset({0, 1, 2})
_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)
_DEFAULT_JUDGE_MAX_TOKENS = 700
DEFAULT_JUDGE_WORKERS = 4
_MIMO_JUDGE_MAX_COMPLETION_TOKENS = 1024
_MIMO_JUDGE_THINKING_MAX_COMPLETION_TOKENS = 4096
_MIMO_THINKING_DISABLED = "disabled"
_MIMO_THINKING_ENABLED = "enabled"
_MIMO_DEFAULT_THINKING_MODE = _MIMO_THINKING_ENABLED
_MIMO_RETRY_ATTEMPTS = 4
_MIMO_RETRY_BASE_SECONDS = 8.0


def _progress(message: str) -> None:
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    print(f"{ts} {message}", file=sys.stderr, flush=True)


def _is_retryable_llm_error(exc: Exception) -> bool:
    status_code = getattr(exc, "status_code", None)
    if status_code in {408, 409, 429, 500, 502, 503, 504}:
        return True
    text = str(exc).lower()
    return any(token in text for token in ("429", "too many requests", "rate limit", "limitation"))


def normalize_mimo_thinking_mode(mode: str | None) -> str:
    if not mode:
        return _MIMO_DEFAULT_THINKING_MODE
    normalized = mode.strip().lower()
    if normalized in {_MIMO_THINKING_DISABLED, "off", "false", "0"}:
        return _MIMO_THINKING_DISABLED
    if normalized in {_MIMO_THINKING_ENABLED, "on", "true", "1", "auto"}:
        return _MIMO_THINKING_ENABLED
    raise ValueError(f"Unsupported MiMo thinking mode: {mode!r}")


def _judge_request_options(provider: str, *, mimo_thinking: str | None = None) -> dict[str, Any]:
    """Provider-specific request options for stable judge JSON output."""
    if provider == "mimo":
        thinking_mode = normalize_mimo_thinking_mode(mimo_thinking)
        if thinking_mode == _MIMO_THINKING_ENABLED:
            return {
                "max_completion_tokens": _MIMO_JUDGE_THINKING_MAX_COMPLETION_TOKENS,
                "extra_body": {"thinking": {"type": _MIMO_THINKING_ENABLED}},
            }
        return {
            "max_completion_tokens": _MIMO_JUDGE_MAX_COMPLETION_TOKENS,
            "extra_body": {"thinking": {"type": _MIMO_THINKING_DISABLED}},
        }
    return {"max_tokens": _DEFAULT_JUDGE_MAX_TOKENS}


def judge_run_metadata(provider: str | None, *, mimo_thinking: str | None = None) -> dict[str, Any]:
    prov = (provider or default_llm_provider()).strip().lower()
    options = _judge_request_options(prov, mimo_thinking=mimo_thinking)
    metadata: dict[str, Any] = {
        "provider": prov,
        "request_options": options,
    }
    if prov == "mimo":
        thinking_mode = normalize_mimo_thinking_mode(mimo_thinking)
        metadata["thinking_mode"] = thinking_mode
        if thinking_mode == _MIMO_THINKING_ENABLED:
            metadata["judge_condition_note"] = (
                "MiMo judge run with thinking enabled; separate from and not directly "
                "comparable to MiMo thinking-disabled judge artifacts."
            )
        else:
            metadata["judge_condition_note"] = (
                "MiMo judge run with thinking disabled; not directly comparable to "
                "MiMo runs where thinking was enabled or unspecified."
            )
    return metadata


def _extract_json_object(text: str) -> str:
    cleaned = text.strip()
    if not cleaned:
        raise ValueError("Empty LLM judge response")
    fence = _JSON_FENCE_RE.search(cleaned)
    if fence:
        return fence.group(1).strip()
    if cleaned.startswith("{") and cleaned.endswith("}"):
        return cleaned
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        return cleaned[start : end + 1].strip()
    raise ValueError("LLM judge response did not contain a JSON object")

DEFAULT_MIN_EXACT_AGREEMENT = 0.60
DEFAULT_MIN_PEARSON = 0.50
DEFAULT_MIN_CALIBRATION_PAIRS = 5

TRUST_STATUS_TRUSTED = "采信"
TRUST_STATUS_UNTRUSTED = "不采信"

_JUDGE_SYSTEM = (
    "You are an expert resonance judge for a news-to-film matching eval. "
    "A match resonates on two independent axes: (1) surface element and "
    "(2) underlying logic. The score equals the number of axes that hold. "
    "Return only valid JSON matching the requested schema. "
    "Follow the decision tree: first assess 表层元素 (load-bearing concrete "
    "anchor, passes the 0-guard) yes/no; then assess 底层逻辑 (a causal-stakes "
    "engine invariant under POV/scale change) yes/no — this axis is GATED by a "
    "falsifiable causal counter-test: you MUST write one 'X, under constraint Z, "
    "drives Y' sentence that is literally true of BOTH the news and the film; "
    "if you cannot, 底层逻辑 = NO. Apply the logic 0-guard: if that sentence "
    "would still hold for an unrelated news item paired with the same film, "
    "底层逻辑 = NO. When uncertain between score 0 and 1, prefer 0. "
    "Then map to score and resonance_type. "
    "Optionally set pov_transform=true only when score=2 and the resonance "
    "becomes visible only after a POV or scale shift (Gap A pattern)."
)

_JUDGE_RUBRIC = f"""\
## Resonance score rubric (two independent axes, 2×2 matrix)

A news–film pair can resonate on two **independent** axes. score = number of axes that hold.

**Axis 1 — 表层元素 (surface element)**: Do the news and film share a
**concrete, nameable** element that is **load-bearing** in both stories
(this place / this kind of occupation / this type of event / this setting or subject-matter)?
- **0-guard**: if an unrelated news item could be paired with the same film equally well,
  the shared element is NOT load-bearing → Axis 1 = NO.
- **Abstract power-role pairings (authority↔victim, leader↔team) are NOT surface elements**
  — they belong to Axis 2 (they fail the 0-guard: an unrelated institutional news item fits them too).

**Axis 2 — 底层逻辑 (underlying logic)**: Do the news and film instantiate the
**same causal-stakes engine**, invariant under change of POV or scale? The engine is one
sentence of the form **"X, under constraint Z, drives Y"**
(e.g. *systemic scarcity forces ordinary people into survival mode*). An institutional-scale
telling and an individual-scale telling of the **same** engine still count as the same logic.
- **Falsifiable causal counter-test (anti-inflation)**: you MUST write a single
  "X under constraint Z drives Y" sentence that is literally true of **both** sides.
  If you cannot write one, Axis 2 = NO → fall back to score 0/1.
  ("Logic" is broader than rigid structural isomorphism because it admits POV/scale shifts,
  but it does not collapse into "everything resonates".)
- **Logic 0-guard**: if your causal_test sentence would remain literally true for an
  **unrelated news item** paired with the same film, the engine is NOT specific to this
  pair → Axis 2 = NO (you cannot assign score 1 via {TYPE_DEEP}).
- **Tie-break**: when uncertain between score 0 and 1, prefer 0.

| 表层元素 | 底层逻辑 | score | resonance_type |
|---|---|---|---|
| 无 | 否 | **0** | null |
| 无 | 是 | **1** | {TYPE_DEEP} |
| 有 | 否 | **1** | {TYPE_SURFACE} |
| 有 | 是 | **2** | {TYPE_STRONG} |

**0-guard restated**: if an unrelated news item could explain the film equally well
→ 无表层 + 无逻辑 → score 0 (resonance_type null; conceptually {TYPE_NONE}).

**Optional sub-label — {SUB_LABEL_POV_TRANSFORM}**: set `pov_transform` to true **only**
when score = 2 and the pair reads as strong resonance **because** a POV or scale shift
was needed to see the shared causal engine (institutional news ↔ individual film, etc.).
Otherwise false. Never set true for score 0/1.

Output JSON. All fields required. `resonance_type` is null only at score 0.
`causal_test` is the bidirectional "X under constraint Z drives Y" sentence that holds for
BOTH news and film; set it to "" only when Axis 2 = NO. `rationale` is brief free text.
{{"score": 0|1|2, "resonance_type": {TYPE_DEEP!r}|{TYPE_SURFACE!r}|{TYPE_STRONG!r}|null, "pov_transform": true|false, "causal_test": "X under constraint Z drives Y — true of both news and film, or \\"\\" if none", "rationale": "brief"}}
"""


@dataclass
class JudgeItem:
    run_id: str
    tmdb_id: str
    title: str
    news_title: str
    news_summary: str
    movie_overview: str
    human_score: int | None = None
    human_resonance_type: str | None = None
    human_pov_transform: bool | None = None

    @property
    def key(self) -> tuple[str, str]:
        return (self.run_id, self.tmdb_id)


@dataclass
class JudgeResult:
    run_id: str
    tmdb_id: str
    title: str
    judge_score: int
    judge_resonance_type: str | None
    rationale: str = ""
    causal_test: str = ""
    human_score: int | None = None
    human_resonance_type: str | None = None
    human_pov_transform: bool | None = None
    judge_pov_transform: bool | None = None
    disagreement: bool = False
    trusted: bool = True

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CalibrationReport:
    observation_run_ids: list[str]
    n_pairs: int
    exact_agreement: float | None
    within_one_agreement: float | None
    pearson_r: float | None
    thresholds: dict[str, float | int]
    trusted: bool
    trust_status: str
    screening_only: bool

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class JudgeOutput:
    version: int
    calibration: CalibrationReport
    scores: list[JudgeResult] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "calibration": self.calibration.to_dict(),
            "scores": [s.to_dict() for s in self.scores],
        }


def _strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def parse_plain_human_score(raw: str) -> int | None:
    """Parse editor-filled 共振分; skip backfill inline values."""
    cleaned = _strip_html_comments(raw).strip()
    if not cleaned or "（" in cleaned or " / " in cleaned:
        return None
    match = re.search(r"\b([012])\b", cleaned)
    return int(match.group(1)) if match else None


def parse_plain_human_type(raw: str) -> str | None:
    cleaned = _strip_html_comments(raw).strip()
    if not cleaned or " / " in cleaned:
        return None
    if "（" in cleaned and not any(
        t in cleaned
        for t in (TYPE_DEEP, TYPE_SURFACE, TYPE_STRONG, TYPE_NONE)
    ):
        return None
    return parse_resonance_type(raw)


def _parse_pov_transform_field(raw: Any) -> bool | None:
    if raw is None or raw == "":
        return None
    if isinstance(raw, bool):
        return raw
    if isinstance(raw, (int, float)):
        return bool(raw)
    parsed = parse_pov_transform(str(raw))
    if parsed is not None:
        return parsed
    lowered = str(raw).strip().lower()
    if lowered in {"true", "yes", "1"}:
        return True
    if lowered in {"false", "no", "0"}:
        return False
    raise ValueError(f"invalid pov_transform {raw!r}")


def validate_judge_payload(
    payload: dict[str, Any],
) -> tuple[int, str | None, str, bool | None]:
    """Validate LLM judge JSON; return (score, resonance_type, causal_test, pov_transform)."""
    if not isinstance(payload, dict):
        raise ValueError("judge payload must be a JSON object")
    raw_score = payload.get("score")
    if raw_score not in _VALID_SCORES:
        raise ValueError(f"judge score must be 0, 1, or 2; got {raw_score!r}")
    score = int(raw_score)
    raw_type = payload.get("resonance_type")
    resonance_type: str | None
    if raw_type is None or raw_type == "":
        resonance_type = None
    else:
        resonance_type = parse_resonance_type(str(raw_type))
        if resonance_type is None or resonance_type == TYPE_NONE:
            raise ValueError(f"invalid resonance_type {raw_type!r}")
    validate_score_type_pair(score, resonance_type)
    if "causal_test" not in payload:
        raise ValueError("judge payload must include causal_test")
    causal_test = str(payload.get("causal_test") or "").strip()
    if score == 2 and not causal_test:
        raise ValueError("score 2 requires non-empty causal_test")
    if resonance_type == TYPE_DEEP and not causal_test:
        raise ValueError(f"{TYPE_DEEP!r} requires non-empty causal_test")
    raw_pov = payload.get("pov_transform")
    pov_transform = (
        _parse_pov_transform_field(raw_pov) if raw_pov is not None else None
    )
    return score, resonance_type, causal_test, validate_pov_transform_sub_label(
        score, resonance_type, pov_transform
    )


def compute_calibration(
    pairs: list[tuple[int, int]],
    *,
    observation_run_ids: list[str],
    min_exact_agreement: float = DEFAULT_MIN_EXACT_AGREEMENT,
    min_pearson: float = DEFAULT_MIN_PEARSON,
    min_pairs: int = DEFAULT_MIN_CALIBRATION_PAIRS,
) -> CalibrationReport:
    """Compare judge vs human scores on observation-set pairs."""
    thresholds = {
        "min_exact_agreement": min_exact_agreement,
        "min_pearson": min_pearson,
        "min_pairs": min_pairs,
    }
    n = len(pairs)
    if n < min_pairs:
        return CalibrationReport(
            observation_run_ids=observation_run_ids,
            n_pairs=n,
            exact_agreement=None,
            within_one_agreement=None,
            pearson_r=None,
            thresholds=thresholds,
            trusted=False,
            trust_status=TRUST_STATUS_UNTRUSTED,
            screening_only=True,
        )

    human = [float(h) for h, _ in pairs]
    judge = [float(j) for _, j in pairs]
    exact = sum(1 for h, j in pairs if h == j) / n
    within_one = sum(1 for h, j in pairs if abs(h - j) <= 1) / n
    pearson_r = _pearson(human, judge)

    trusted = (
        exact >= min_exact_agreement
        and pearson_r is not None
        and pearson_r >= min_pearson
    )
    return CalibrationReport(
        observation_run_ids=observation_run_ids,
        n_pairs=n,
        exact_agreement=exact,
        within_one_agreement=within_one,
        pearson_r=pearson_r,
        thresholds=thresholds,
        trusted=trusted,
        trust_status=TRUST_STATUS_TRUSTED if trusted else TRUST_STATUS_UNTRUSTED,
        screening_only=not trusted,
    )


def _load_news_context(run_dir: Path) -> tuple[str, str]:
    reality_path = run_dir / "reality.json"
    if reality_path.is_file():
        data = json.loads(reality_path.read_text(encoding="utf-8"))
        title = str(data.get("title") or "")
        summary = str(data.get("description") or data.get("summary") or "")
        return title, summary
    reality_md = run_dir / "reality.md"
    if reality_md.is_file():
        text = reality_md.read_text(encoding="utf-8")
        title_match = re.search(r"^- \*\*title\*\*:\s*(.+)$", text, re.MULTILINE)
        summary_match = re.search(r"^- \*\*summary\*\*:\s*(.+)$", text, re.MULTILINE)
        return (
            title_match.group(1).strip() if title_match else "",
            summary_match.group(1).strip() if summary_match else "",
        )
    return "", ""


def _overview_from_block(body: str) -> str:
    match = re.search(r"^-\s*\*\*overview\*\*:\s*(.+)$", body, re.MULTILINE)
    return match.group(1).strip() if match else ""


_SCORE_LINE = re.compile(r"^-\s*\*\*共振分\*\*:\s*(.*)$", re.MULTILINE)
_TYPE_LINE = re.compile(r"^-\s*\*\*共振类型\*\*:\s*(.*)$", re.MULTILINE)
_POV_TRANSFORM_LINE = re.compile(r"^-\s*\*\*POV变换\*\*:\s*(.*)$", re.MULTILINE)
_TMDB_LINE = re.compile(r"^-\s*\*\*tmdb_id\*\*:\s*(\S+)", re.MULTILINE)


def _human_fields_from_block(
    block: str,
) -> tuple[int | None, str | None, bool | None]:
    score_match = _SCORE_LINE.search(block)
    human_score = (
        parse_plain_human_score(score_match.group(1)) if score_match else None
    )
    type_match = _TYPE_LINE.search(block)
    human_type = (
        parse_plain_human_type(type_match.group(1)) if type_match else None
    )
    pov_match = _POV_TRANSFORM_LINE.search(block)
    human_pov = (
        parse_pov_transform(pov_match.group(1)) if pov_match else None
    )
    if human_score is not None and human_type is not None:
        human_pov = validate_pov_transform_sub_label(
            human_score, human_type, human_pov
        )
    return human_score, human_type, human_pov


def _blocks_from_text(text: str) -> list[tuple[str, str]]:
    parts = re.split(r"(?=^###\s+)", text, flags=re.MULTILINE)
    blocks: list[tuple[str, str]] = []
    for part in parts[1:]:
        heading_end = part.find("\n")
        heading = part[:heading_end] if heading_end >= 0 else part
        body = part[heading_end + 1 :] if heading_end >= 0 else ""
        if _TMDB_LINE.search(body):
            blocks.append((heading, body))
    return blocks


def collect_judge_items(
    eval_dir: Path,
    *,
    review_path: Path | None = None,
    run_ids: list[str] | None = None,
) -> list[JudgeItem]:
    """Build judge inputs from per-run candidates.md or unified review."""
    eval_dir = eval_dir if eval_dir.is_absolute() else _REPO_ROOT / eval_dir
    review = review_path or (eval_dir / "high-hit-score-review.md")
    items: list[JudgeItem] = []

    if review.is_file():
        review_text = review.read_text(encoding="utf-8")
        runs = parse_unified_review(review, review_text)
        if run_ids is not None:
            allowed = set(run_ids)
            runs = [r for r in runs if r.run_id in allowed]
        for run in runs:
            run_dir = eval_dir / run.run_id
            news_title, news_summary = _load_news_context(run_dir)
            section_match = re.search(
                rf"^## {re.escape(run.run_id)}\s*$",
                review_text,
                re.MULTILINE,
            )
            section_text = ""
            if section_match:
                start = section_match.end()
                next_sec = re.search(r"^## \d{2}-", review_text[start:], re.MULTILINE)
                section_text = (
                    review_text[start : start + next_sec.start()]
                    if next_sec
                    else review_text[start:]
                )
            blocks = _blocks_from_text(section_text)
            block_by_tmdb = {}
            for heading, body in blocks:
                tmdb_match = _TMDB_LINE.search(body)
                if tmdb_match:
                    block_by_tmdb[tmdb_match.group(1)] = (heading, body)
            for cand in run.candidates:
                block = block_by_tmdb.get(cand.tmdb_id, ("", ""))[1]
                human_score, human_type, human_pov = _human_fields_from_block(block)
                if human_score is None:
                    human_score = cand.score
                    human_type = cand.resonance_type
                items.append(
                    JudgeItem(
                        run_id=run.run_id,
                        tmdb_id=cand.tmdb_id,
                        title=cand.title,
                        news_title=news_title,
                        news_summary=news_summary,
                        movie_overview=_overview_from_block(block),
                        human_score=human_score,
                        human_resonance_type=human_type,
                        human_pov_transform=human_pov,
                    )
                )
        return items

    target_runs = run_ids or [
        p.name for p in sorted(eval_dir.iterdir()) if (p / "candidates.md").is_file()
    ]
    for run_id in target_runs:
        cand_path = eval_dir / run_id / "candidates.md"
        if not cand_path.is_file():
            continue
        text = cand_path.read_text(encoding="utf-8")
        run = parse_eval_markdown(cand_path, text)
        run.run_id = run_id
        news_title, news_summary = _load_news_context(eval_dir / run_id)
        blocks = _blocks_from_text(text)
        block_by_tmdb = {}
        for heading, body in blocks:
            tmdb_match = _TMDB_LINE.search(body)
            if tmdb_match:
                block_by_tmdb[tmdb_match.group(1)] = body
        for cand in run.candidates:
            block = block_by_tmdb.get(cand.tmdb_id, "")
            human_score, human_type, human_pov = _human_fields_from_block(block)
            if human_score is None:
                human_score = cand.score
                human_type = cand.resonance_type
            items.append(
                JudgeItem(
                    run_id=run_id,
                    tmdb_id=cand.tmdb_id,
                    title=cand.title,
                    news_title=news_title,
                    news_summary=news_summary,
                    movie_overview=_overview_from_block(block),
                    human_score=human_score,
                    human_resonance_type=human_type,
                    human_pov_transform=human_pov,
                )
            )
    return items


def build_judge_user_prompt(item: JudgeItem) -> str:
    return (
        f"{_JUDGE_RUBRIC}\n\n"
        f"## News\n"
        f"Title: {item.news_title}\n"
        f"Summary: {item.news_summary}\n\n"
        f"## Film candidate\n"
        f"Title: {item.title}\n"
        f"Overview: {item.movie_overview}\n"
    )


def parse_judge_response(
    text: str,
) -> tuple[int, str | None, str, str, bool | None]:
    payload = json.loads(_extract_json_object(text))
    score, resonance_type, causal_test, pov_transform = validate_judge_payload(payload)
    rationale = str(payload.get("rationale") or "").strip()
    return score, resonance_type, rationale, causal_test, pov_transform


def call_llm_judge(
    item: JudgeItem,
    *,
    provider: str | None = None,
    client: Any | None = None,
    mimo_thinking: str | None = None,
) -> tuple[int, str | None, str, str, bool | None]:
    load_env()
    prov = (provider or default_llm_provider()).strip().lower()
    llm = client or get_llm_client(prov)
    model_env = "MIMO_MODEL" if prov == "mimo" else "DEEPSEEK_MODEL"
    import os

    model = os.getenv(model_env, "").strip()
    if not model:
        raise RuntimeError(f"Missing {model_env} for provider {prov!r}")

    def _request_content(extra_user_prompt: str = "") -> str:
        user_content = build_judge_user_prompt(item)
        if extra_user_prompt:
            user_content = f"{user_content}\n\n{extra_user_prompt}"
        attempts = _MIMO_RETRY_ATTEMPTS if prov == "mimo" else 1
        for attempt in range(attempts):
            try:
                response = llm.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": _JUDGE_SYSTEM},
                        {"role": "user", "content": user_content},
                    ],
                    temperature=0.2,
                    timeout=90,
                    **_judge_request_options(prov, mimo_thinking=mimo_thinking),
                )
                return (response.choices[0].message.content or "").strip()
            except Exception as exc:
                if attempt >= attempts - 1 or not _is_retryable_llm_error(exc):
                    raise
                time.sleep(_MIMO_RETRY_BASE_SECONDS * (2**attempt))
        raise RuntimeError("unreachable judge retry state")

    content = _request_content()
    try:
        return parse_judge_response(content)
    except (json.JSONDecodeError, ValueError):
        retry_content = _request_content(
            "Your previous answer was not valid JSON. Return exactly one JSON object only, "
            "with keys: score, resonance_type, causal_test, rationale, pov_transform."
        )
        return parse_judge_response(retry_content)


JudgeFn = Callable[[JudgeItem], tuple[int, str | None, str, str, bool | None]]


def score_items(
    items: list[JudgeItem],
    judge_fn: JudgeFn,
    *,
    observation_run_ids: list[str] | None = None,
    min_exact_agreement: float = DEFAULT_MIN_EXACT_AGREEMENT,
    min_pearson: float = DEFAULT_MIN_PEARSON,
    min_pairs: int = DEFAULT_MIN_CALIBRATION_PAIRS,
    workers: int = 1,
) -> JudgeOutput:
    obs_ids = observation_run_ids or [
        r for r in {i.run_id for i in items} if r.startswith(OBS_RUN_PREFIXES)
    ]
    workers = max(1, workers)

    def _score_one(item: JudgeItem) -> JudgeResult:
        judge_score, judge_type, rationale, causal_test, pov_transform = judge_fn(item)
        disagreement = (
            item.human_score is not None and item.human_score != judge_score
        )
        return JudgeResult(
            run_id=item.run_id,
            tmdb_id=item.tmdb_id,
            title=item.title,
            judge_score=judge_score,
            judge_resonance_type=judge_type,
            rationale=rationale,
            causal_test=causal_test,
            human_score=item.human_score,
            human_resonance_type=item.human_resonance_type,
            human_pov_transform=item.human_pov_transform,
            judge_pov_transform=pov_transform,
            disagreement=disagreement,
            trusted=True,
        )

    results: list[JudgeResult | None] = [None] * len(items)
    total = len(items)
    done_count = 0
    if workers == 1 or len(items) <= 1:
        for idx, item in enumerate(items):
            _progress(f"[judge] scoring {idx + 1}/{total} {item.run_id}/{item.tmdb_id}")
            results[idx] = _score_one(item)
            done_count += 1
            _progress(f"[judge] done {done_count}/{total} {item.run_id}/{item.tmdb_id}")
    else:
        with ThreadPoolExecutor(max_workers=workers) as pool:
            futures = {pool.submit(_score_one, item): idx for idx, item in enumerate(items)}
            for future in as_completed(futures):
                idx = futures[future]
                results[idx] = future.result()
                done_count += 1
                item = items[idx]
                _progress(f"[judge] done {done_count}/{total} {item.run_id}/{item.tmdb_id}")

    ordered_results = [result for result in results if result is not None]
    cal_pairs: list[tuple[int, int]] = []
    for item, result in zip(items, ordered_results):
        if item.run_id in obs_ids and item.human_score is not None:
            cal_pairs.append((item.human_score, result.judge_score))

    calibration = compute_calibration(
        cal_pairs,
        observation_run_ids=obs_ids,
        min_exact_agreement=min_exact_agreement,
        min_pearson=min_pearson,
        min_pairs=min_pairs,
    )
    _progress(
        f"[judge] summary scored={len(ordered_results)} "
        f"calibration_pairs={calibration.n_pairs} trust_status={calibration.trust_status}"
    )
    for result in ordered_results:
        result.trusted = calibration.trusted
    return JudgeOutput(
        version=_JUDGE_SCHEMA_VERSION,
        calibration=calibration,
        scores=ordered_results,
    )


_RUN_ID_COMMENT = re.compile(r"^<!-- run_id: (\S+) -->$", re.MULTILINE)
_JUDGE_SCORE_LINE = re.compile(
    r"^\s*-\s*\*\*judge分\*\*:.*$", re.MULTILINE
)
_JUDGE_TYPE_LINE = re.compile(
    r"^\s*-\s*\*\*judge共振类型\*\*:.*$", re.MULTILINE
)
_JUDGE_DISAGREE_LINE = re.compile(
    r"^\s*-\s*\*\*judge分歧\*\*:.*$", re.MULTILINE
)
_JUDGE_TRUST_LINE = re.compile(
    r"^\s*-\s*\*\*judge采信\*\*:.*$", re.MULTILINE
)
_JUDGE_CAUSAL_TEST_LINE = re.compile(
    r"^\s*-\s*\*\*judge因果反测\*\*:.*$", re.MULTILINE
)
_JUDGE_RATIONALE_LINE = re.compile(
    r"^\s*-\s*\*\*(?:judge理由|rationale)\*\*:.*$", re.MULTILINE
)
_JUDGE_POV_TRANSFORM_LINE = re.compile(
    r"^\s*-\s*\*\*judge POV变换\*\*:.*$", re.MULTILINE
)
_JUDGE_BLOCK_HEADER_LINE = re.compile(
    r"^-\s*\*\*LLM Judge（自动评审）\*\*:.*$", re.MULTILINE
)
_SCORING_REMARK_LINE = re.compile(r"^(-\s*\*\*打分备注\*\*:.*)$", re.MULTILINE)
_REVIEW_JUDGE_HEADER = re.compile(
    r"^- \*\*LLM judge:\*\*.*$", re.MULTILINE
)


def load_judge_output(path: Path) -> JudgeOutput:
    """Load ``llm-judge-scores.json`` into dataclasses."""
    data = json.loads(path.read_text(encoding="utf-8"))
    cal_raw = data.get("calibration") or {}
    calibration = CalibrationReport(
        observation_run_ids=list(cal_raw.get("observation_run_ids") or []),
        n_pairs=int(cal_raw.get("n_pairs") or 0),
        exact_agreement=cal_raw.get("exact_agreement"),
        within_one_agreement=cal_raw.get("within_one_agreement"),
        pearson_r=cal_raw.get("pearson_r"),
        thresholds=dict(cal_raw.get("thresholds") or {}),
        trusted=bool(cal_raw.get("trusted")),
        trust_status=str(cal_raw.get("trust_status") or TRUST_STATUS_UNTRUSTED),
        screening_only=bool(cal_raw.get("screening_only")),
    )
    scores = [
        JudgeResult(
            run_id=str(row["run_id"]),
            tmdb_id=str(row["tmdb_id"]),
            title=str(row.get("title") or ""),
            judge_score=int(row["judge_score"]),
            judge_resonance_type=row.get("judge_resonance_type"),
            rationale=str(row.get("rationale") or ""),
            causal_test=str(row.get("causal_test") or ""),
            human_score=row.get("human_score"),
            human_resonance_type=row.get("human_resonance_type"),
            human_pov_transform=row.get("human_pov_transform"),
            judge_pov_transform=row.get("judge_pov_transform"),
            disagreement=bool(row.get("disagreement")),
            trusted=bool(row.get("trusted", calibration.trusted)),
        )
        for row in data.get("scores") or []
    ]
    return JudgeOutput(
        version=int(data.get("version") or _JUDGE_SCHEMA_VERSION),
        calibration=calibration,
        scores=scores,
    )


def format_judge_block_lines(
    result: JudgeResult, calibration: CalibrationReport
) -> list[str]:
    """Candidate-local LLM judge block, separate from human editor fields."""
    lines = [
        "- **LLM Judge（自动评审）**:",
        f"  - **judge分**: {result.judge_score}",
        f"  - **judge共振类型**: {result.judge_resonance_type or ''}",
    ]
    if result.judge_pov_transform:
        lines.append("  - **judge POV变换**: 是")
    if result.disagreement:
        lines.append("  - **judge分歧**: ⚠")
    if calibration.screening_only or not calibration.trusted:
        lines.append(
            f"  - **judge采信**: {calibration.trust_status} · screening only"
        )
    else:
        lines.append(f"  - **judge采信**: {calibration.trust_status}")
    if result.causal_test:
        lines.append(f"  - **judge因果反测**: {result.causal_test}")
    if result.rationale:
        lines.append(f"  - **judge理由**: {result.rationale}")
    return lines


def _strip_existing_judge_lines(block: str) -> str:
    for pattern in (
        _JUDGE_BLOCK_HEADER_LINE,
        _JUDGE_SCORE_LINE,
        _JUDGE_TYPE_LINE,
        _JUDGE_DISAGREE_LINE,
        _JUDGE_TRUST_LINE,
        _JUDGE_CAUSAL_TEST_LINE,
        _JUDGE_RATIONALE_LINE,
        _JUDGE_POV_TRANSFORM_LINE,
    ):
        block = pattern.sub("", block)
    return re.sub(r"\n{3,}", "\n\n", block.rstrip()) + "\n"


def _insert_judge_lines_after_remark(block: str, judge_lines: list[str]) -> str:
    insert = "\n".join(judge_lines)
    if _SCORING_REMARK_LINE.search(block):
        return _SCORING_REMARK_LINE.sub(
            lambda m: f"{m.group(1)}\n{insert}",
            block,
            count=1,
        )
    if _TYPE_LINE.search(block):
        return _TYPE_LINE.sub(
            lambda m: f"{m.group(0)}\n{insert}",
            block,
            count=1,
        )
    if _SCORE_LINE.search(block):
        return _SCORE_LINE.sub(
            lambda m: f"{m.group(0)}\n{insert}",
            block,
            count=1,
        )
    return block.rstrip() + "\n" + insert + "\n"


def _ensure_review_judge_header(text: str, calibration: CalibrationReport) -> str:
    note = (
        f"- **LLM judge:** `llm-judge-scores.json` — "
        f"trust_status={calibration.trust_status}"
    )
    if calibration.screening_only:
        note += " (screening only; separate LLM Judge block per candidate)"
    else:
        note += " (separate LLM Judge block per candidate)"
    if _REVIEW_JUDGE_HEADER.search(text):
        return _REVIEW_JUDGE_HEADER.sub(note, text, count=1)
    anchor = "- **Editor fields:**"
    if anchor in text:
        return text.replace(
            anchor,
            f"{note}\n{anchor}",
            1,
        )
    return text


def integrate_judge_into_review(review_text: str, output: JudgeOutput) -> str:
    """Merge judge scores inline after each candidate's editor scoring fields."""
    by_key = {(s.run_id, str(s.tmdb_id)): s for s in output.scores}
    text = _ensure_review_judge_header(review_text, output.calibration)

    chunks = re.split(r"(?=<!-- run_id: )", text)
    if len(chunks) <= 1:
        return _integrate_judge_blocks_without_comments(text, by_key, output.calibration)

    out_parts: list[str] = [chunks[0]]
    for chunk in chunks[1:]:
        run_match = _RUN_ID_COMMENT.match(chunk)
        run_id = run_match.group(1) if run_match else ""
        heading_parts = re.split(r"(?=^### )", chunk, flags=re.MULTILINE)
        patched_chunk = heading_parts[0]
        for part in heading_parts[1:]:
            if not part.strip():
                continue
            tmdb_match = _TMDB_LINE.search(part)
            if tmdb_match and run_id:
                key = (run_id, tmdb_match.group(1))
                result = by_key.get(key)
                if result is not None:
                    part = _strip_existing_judge_lines(part)
                    part = _insert_judge_lines_after_remark(
                        part, format_judge_block_lines(result, output.calibration)
                    )
            if part and not part.endswith("\n\n"):
                part = part.rstrip() + "\n\n"
            patched_chunk += part
        out_parts.append(patched_chunk)
    merged = "".join(out_parts)
    if not merged.endswith("\n"):
        merged += "\n"
    return merged


def _integrate_judge_blocks_without_comments(
    text: str,
    by_key: dict[tuple[str, str], JudgeResult],
    calibration: CalibrationReport,
) -> str:
    """Fallback when review lacks run_id HTML comments (fixtures)."""
    current_run = ""
    lines = text.splitlines(keepends=True)
    out: list[str] = []
    i = 0
    while i < len(lines):
        line = lines[i]
        sec = re.match(r"^## (\S+)\s*$", line)
        if sec:
            current_run = sec.group(1)
        if line.startswith("### "):
            block_lines = [line]
            i += 1
            while i < len(lines) and not lines[i].startswith("### ") and not (
                lines[i].startswith("## ") and not lines[i].startswith("### ")
            ):
                block_lines.append(lines[i])
                i += 1
            block = "".join(block_lines)
            tmdb_match = _TMDB_LINE.search(block)
            if tmdb_match and current_run:
                key = (current_run, tmdb_match.group(1))
                result = by_key.get(key)
                if result is not None:
                    block = _strip_existing_judge_lines(block)
                    block = _insert_judge_lines_after_remark(
                        block,
                        format_judge_block_lines(result, calibration),
                    )
            out.append(block)
            continue
        out.append(line)
        i += 1
    merged = "".join(out)
    if not merged.endswith("\n"):
        merged += "\n"
    return merged


def write_judge_markdown(
    path: Path,
    output: JudgeOutput,
    run_metadata: dict[str, Any] | None = None,
) -> None:
    lines = [
        "# LLM Judge Scores",
        "",
        f"- **trust_status**: {output.calibration.trust_status}",
        f"- **screening_only**: {output.calibration.screening_only}",
        f"- **calibration_pairs**: {output.calibration.n_pairs}",
    ]
    if run_metadata:
        lines.extend(
            [
                f"- **provider**: {run_metadata.get('provider', '')}",
                f"- **thinking_mode**: {run_metadata.get('thinking_mode', '')}",
                f"- **judge_condition_note**: {run_metadata.get('judge_condition_note', '')}",
            ]
        )
    if output.calibration.exact_agreement is not None:
        lines.append(
            f"- **exact_agreement**: {output.calibration.exact_agreement:.3f}"
        )
    if output.calibration.pearson_r is not None:
        lines.append(f"- **pearson_r**: {output.calibration.pearson_r:.3f}")
    lines.append("")
    for row in output.scores:
        flag = " ⚠ disagreement" if row.disagreement else ""
        trust = "" if row.trusted else " · 不采信"
        lines.append(
            f"### {row.title} ({row.run_id}){flag}{trust}\n"
            f"- **tmdb_id**: {row.tmdb_id}\n"
            f"- **judge_score**: {row.judge_score}\n"
            f"- **judge_resonance_type**: {row.judge_resonance_type or ''}\n"
            f"- **judge_pov_transform**: {row.judge_pov_transform or ''}\n"
            f"- **human_score**: {row.human_score if row.human_score is not None else ''}\n"
            f"- **human_resonance_type**: {row.human_resonance_type or ''}\n"
            f"- **human_pov_transform**: {row.human_pov_transform or ''}\n"
            f"- **causal_test**: {row.causal_test}\n"
            f"- **rationale**: {row.rationale}\n"
        )
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--eval-dir",
        type=Path,
        default=_REPO_ROOT / "output" / "Eval" / "phase3.8",
        help="Eval phase directory with runs and optional high-hit-score-review.md",
    )
    parser.add_argument(
        "--review",
        type=Path,
        default=None,
        help="Unified review markdown (default: <eval-dir>/high-hit-score-review.md)",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=None,
        help="Write judge output JSON (default: <eval-dir>/llm-judge-scores.json)",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=None,
        help="Write human-readable summary markdown",
    )
    parser.add_argument("--provider", default=None, help="LLM provider (mimo/deepseek)")
    parser.add_argument(
        "--mimo-thinking",
        choices=["disabled", "enabled"],
        default="enabled",
        help="MiMo thinking mode for judge requests (default: enabled)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_JUDGE_WORKERS,
        metavar="N",
        help=f"Concurrent judge pair scorers (default: {DEFAULT_JUDGE_WORKERS})",
    )
    parser.add_argument(
        "--calibrate-only",
        action="store_true",
        help="Skip LLM calls; use existing judge JSON scores for calibration replay",
    )
    parser.add_argument(
        "--min-exact-agreement",
        type=float,
        default=DEFAULT_MIN_EXACT_AGREEMENT,
    )
    parser.add_argument(
        "--min-pearson",
        type=float,
        default=DEFAULT_MIN_PEARSON,
    )
    parser.add_argument(
        "--min-pairs",
        type=int,
        default=DEFAULT_MIN_CALIBRATION_PAIRS,
    )
    parser.add_argument(
        "--integrate-review",
        action="store_true",
        help="Merge existing judge JSON into high-hit-score-review.md (no LLM calls)",
    )
    args = parser.parse_args(argv)

    if args.workers < 1:
        print("error: --workers must be >= 1", file=sys.stderr)
        return 2

    eval_dir = args.eval_dir if args.eval_dir.is_absolute() else _REPO_ROOT / args.eval_dir
    review = args.review or (eval_dir / "high-hit-score-review.md")
    out_json = args.out_json or (eval_dir / "llm-judge-scores.json")
    if not out_json.is_absolute():
        out_json = _REPO_ROOT / out_json

    if args.integrate_review:
        if not out_json.is_file():
            print(f"integrate-review requires judge JSON: {out_json}", file=sys.stderr)
            return 1
        if not review.is_file():
            print(f"integrate-review requires review: {review}", file=sys.stderr)
            return 1
        output = load_judge_output(out_json)
        merged = integrate_judge_into_review(
            review.read_text(encoding="utf-8"), output
        )
        review.write_text(merged, encoding="utf-8")
        print(f"integrated {len(output.scores)} judge scores into {review}")
        return 0

    items = collect_judge_items(eval_dir, review_path=review if review.is_file() else None)
    if not items:
        print("no candidates found for judging", file=sys.stderr)
        return 1

    all_run_ids = load_manifest()
    obs_ids, _ = split_obs_holdout(all_run_ids)

    if args.calibrate_only:
        in_json = args.out_json or (eval_dir / "llm-judge-scores.json")
        if not in_json.is_file():
            print(f"calibrate-only requires existing JSON: {in_json}", file=sys.stderr)
            return 1
        prior = json.loads(in_json.read_text(encoding="utf-8"))
        by_key = {
            (s["run_id"], str(s["tmdb_id"])): s for s in prior.get("scores", [])
        }

        def _replay(item: JudgeItem) -> tuple[int, str | None, str, str, bool | None]:
            row = by_key[(item.run_id, item.tmdb_id)]
            return (
                int(row["judge_score"]),
                row.get("judge_resonance_type"),
                str(row.get("rationale") or ""),
                str(row.get("causal_test") or ""),
                row.get("judge_pov_transform"),
            )

        judge_fn: JudgeFn = _replay
    else:
        provider = args.provider

        def _llm(item: JudgeItem) -> tuple[int, str | None, str, str, bool | None]:
            return call_llm_judge(item, provider=provider, mimo_thinking=args.mimo_thinking)

        judge_fn = _llm

    output = score_items(
        items,
        judge_fn,
        observation_run_ids=obs_ids,
        min_exact_agreement=args.min_exact_agreement,
        min_pearson=args.min_pearson,
        min_pairs=args.min_pairs,
        workers=args.workers,
    )

    out_json = args.out_json or (eval_dir / "llm-judge-scores.json")
    out_json.write_text(
        json.dumps(output.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    out_md = args.out_md or (eval_dir / "llm-judge-scores.md")
    write_judge_markdown(
        out_md,
        output,
        run_metadata=judge_run_metadata(args.provider, mimo_thinking=args.mimo_thinking),
    )

    cal = output.calibration
    print(
        f"trust_status={cal.trust_status} pairs={cal.n_pairs} "
        f"exact={cal.exact_agreement} pearson={cal.pearson_r}"
    )
    print(f"wrote {out_json}")
    print(f"wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
