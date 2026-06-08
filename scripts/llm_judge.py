"""LLM-as-judge resonance scorer with observation-set calibration (Phase 3.9.4).

Scores candidates 0/1/2 plus resonance type per ``docs/eval-the-bet.md`` §4.
Calibration on observation-set human scores (runs 01–04); below alignment
threshold marks judge output as 不采信 (screening only).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
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
    TYPE_DEEP,
    TYPE_NONE,
    TYPE_STRONG,
    TYPE_SURFACE,
    parse_resonance_type,
    validate_score_type_pair,
)
from scripts.run_persona_batch import OBS_RUN_PREFIXES, split_obs_holdout
from scripts.summarize_eval import (
    _pearson,
    parse_eval_markdown,
    parse_unified_review,
)

_JUDGE_SCHEMA_VERSION = 2
_VALID_SCORES = frozenset({0, 1, 2})
_JSON_FENCE_RE = re.compile(r"```(?:json)?\s*([\s\S]*?)\s*```", re.IGNORECASE)

DEFAULT_MIN_EXACT_AGREEMENT = 0.60
DEFAULT_MIN_PEARSON = 0.50
DEFAULT_MIN_CALIBRATION_PAIRS = 5

TRUST_STATUS_TRUSTED = "采信"
TRUST_STATUS_UNTRUSTED = "不采信"

_JUDGE_SYSTEM = (
    "You are an expert resonance judge for a news-to-film matching eval. "
    "Return only valid JSON matching the requested schema. "
    "Follow the 2×2 decision tree: first assess 承重表层锚点 (yes/no), "
    "then 骨架同构 (yes/no), then map to score and resonance_type."
)

_JUDGE_RUBRIC = f"""\
## Resonance score rubric (2×2 matrix)

**Step 1 — 承重表层锚点**: Does the film share a **load-bearing** concrete anchor
with the news (place / event type / role type / setting that drives both stories)?
Incidental word overlap without load-bearing shared elements = NO.

**Step 2 — 骨架同构**: Are power / fate / theme skeletons isomorphic
(e.g. central authority sacrificing margins under scarcity; public rhetoric vs private motive)?

| 承重表层锚点 | 骨架同构 | score | resonance_type |
|---|---|---|---|
| 无 | 否 | **0** | null |
| 无 | 是 | **1** | {TYPE_DEEP} |
| 有 | 否 | **1** | {TYPE_SURFACE} |
| 有 | 是 | **2** | {TYPE_STRONG} |

**0-guard**: if unrelated news could explain the film equally → 无表层 + 不同构 → score 0
(resonance_type null; conceptually {TYPE_NONE}).

Output JSON (both fields required except resonance_type is null at score 0):
{{"score": 0|1|2, "resonance_type": {TYPE_DEEP!r}|{TYPE_SURFACE!r}|{TYPE_STRONG!r}|null, "rationale": "brief"}}
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
    human_score: int | None = None
    human_resonance_type: str | None = None
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


def validate_judge_payload(payload: dict[str, Any]) -> tuple[int, str | None]:
    """Validate LLM judge JSON; return (score, resonance_type)."""
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
    return score, resonance_type


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
_TMDB_LINE = re.compile(r"^-\s*\*\*tmdb_id\*\*:\s*(\S+)", re.MULTILINE)


def _human_fields_from_block(block: str) -> tuple[int | None, str | None]:
    score_match = _SCORE_LINE.search(block)
    human_score = (
        parse_plain_human_score(score_match.group(1)) if score_match else None
    )
    type_match = _TYPE_LINE.search(block)
    human_type = (
        parse_plain_human_type(type_match.group(1)) if type_match else None
    )
    return human_score, human_type


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
                human_score, human_type = _human_fields_from_block(block)
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
            human_score, human_type = _human_fields_from_block(block)
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


def parse_judge_response(text: str) -> tuple[int, str | None, str]:
    cleaned = text.strip()
    fence = _JSON_FENCE_RE.search(cleaned)
    if fence:
        cleaned = fence.group(1).strip()
    payload = json.loads(cleaned)
    score, resonance_type = validate_judge_payload(payload)
    rationale = str(payload.get("rationale") or "").strip()
    return score, resonance_type, rationale


def call_llm_judge(
    item: JudgeItem,
    *,
    provider: str | None = None,
    client: Any | None = None,
) -> tuple[int, str | None, str]:
    load_env()
    prov = (provider or default_llm_provider()).strip().lower()
    llm = client or get_llm_client(prov)
    model_env = "MIMO_MODEL" if prov == "mimo" else "DEEPSEEK_MODEL"
    import os

    model = os.getenv(model_env, "").strip()
    if not model:
        raise RuntimeError(f"Missing {model_env} for provider {prov!r}")

    response = llm.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _JUDGE_SYSTEM},
            {"role": "user", "content": build_judge_user_prompt(item)},
        ],
        temperature=0.2,
    )
    content = (response.choices[0].message.content or "").strip()
    return parse_judge_response(content)


JudgeFn = Callable[[JudgeItem], tuple[int, str | None, str]]


def score_items(
    items: list[JudgeItem],
    judge_fn: JudgeFn,
    *,
    observation_run_ids: list[str] | None = None,
    min_exact_agreement: float = DEFAULT_MIN_EXACT_AGREEMENT,
    min_pearson: float = DEFAULT_MIN_PEARSON,
    min_pairs: int = DEFAULT_MIN_CALIBRATION_PAIRS,
) -> JudgeOutput:
    obs_ids = observation_run_ids or [
        r for r in {i.run_id for i in items} if r.startswith(OBS_RUN_PREFIXES)
    ]
    results: list[JudgeResult] = []
    cal_pairs: list[tuple[int, int]] = []

    for item in items:
        judge_score, judge_type, rationale = judge_fn(item)
        disagreement = (
            item.human_score is not None and item.human_score != judge_score
        )
        result = JudgeResult(
            run_id=item.run_id,
            tmdb_id=item.tmdb_id,
            title=item.title,
            judge_score=judge_score,
            judge_resonance_type=judge_type,
            rationale=rationale,
            human_score=item.human_score,
            human_resonance_type=item.human_resonance_type,
            disagreement=disagreement,
            trusted=True,
        )
        results.append(result)
        if item.run_id in obs_ids and item.human_score is not None:
            cal_pairs.append((item.human_score, judge_score))

    calibration = compute_calibration(
        cal_pairs,
        observation_run_ids=obs_ids,
        min_exact_agreement=min_exact_agreement,
        min_pearson=min_pearson,
        min_pairs=min_pairs,
    )
    for result in results:
        result.trusted = calibration.trusted
    return JudgeOutput(
        version=_JUDGE_SCHEMA_VERSION,
        calibration=calibration,
        scores=results,
    )


_RUN_ID_COMMENT = re.compile(r"^<!-- run_id: (\S+) -->$", re.MULTILINE)
_JUDGE_SCORE_LINE = re.compile(r"^-\s*\*\*judge分\*\*:.*$", re.MULTILINE)
_JUDGE_TYPE_LINE = re.compile(r"^-\s*\*\*judge共振类型\*\*:.*$", re.MULTILINE)
_JUDGE_DISAGREE_LINE = re.compile(r"^-\s*\*\*judge分歧\*\*:.*$", re.MULTILINE)
_JUDGE_TRUST_LINE = re.compile(r"^-\s*\*\*judge采信\*\*:.*$", re.MULTILINE)
_JUDGE_RATIONALE_LINE = re.compile(
    r"^-\s*\*\*(?:judge理由|rationale)\*\*:.*$", re.MULTILINE
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
            human_score=row.get("human_score"),
            human_resonance_type=row.get("human_resonance_type"),
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
    """Inline judge fields for a high-hit review candidate block."""
    lines = [f"- **judge分**: {result.judge_score}"]
    lines.append(
        f"- **judge共振类型**: {result.judge_resonance_type or ''}"
    )
    if result.disagreement:
        lines.append("- **judge分歧**: ⚠")
    if calibration.screening_only or not calibration.trusted:
        lines.append(
            f"- **judge采信**: {calibration.trust_status} · screening only"
        )
    else:
        lines.append(f"- **judge采信**: {calibration.trust_status}")
    if result.rationale:
        lines.append(f"- **judge理由**: {result.rationale}")
    return lines


def _strip_existing_judge_lines(block: str) -> str:
    for pattern in (
        _JUDGE_SCORE_LINE,
        _JUDGE_TYPE_LINE,
        _JUDGE_DISAGREE_LINE,
        _JUDGE_TRUST_LINE,
        _JUDGE_RATIONALE_LINE,
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
        note += " (screening only; inline judge fields per candidate)"
    else:
        note += " (inline judge fields per candidate)"
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


def write_judge_markdown(path: Path, output: JudgeOutput) -> None:
    lines = [
        "# LLM Judge Scores",
        "",
        f"- **trust_status**: {output.calibration.trust_status}",
        f"- **screening_only**: {output.calibration.screening_only}",
        f"- **calibration_pairs**: {output.calibration.n_pairs}",
    ]
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
            f"- **human_score**: {row.human_score if row.human_score is not None else ''}\n"
            f"- **human_resonance_type**: {row.human_resonance_type or ''}\n"
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

        def _replay(item: JudgeItem) -> tuple[int, str | None, str]:
            row = by_key[(item.run_id, item.tmdb_id)]
            return (
                int(row["judge_score"]),
                row.get("judge_resonance_type"),
                str(row.get("rationale") or ""),
            )

        judge_fn: JudgeFn = _replay
    else:
        provider = args.provider

        def _llm(item: JudgeItem) -> tuple[int, str | None, str]:
            return call_llm_judge(item, provider=provider)

        judge_fn = _llm

    output = score_items(
        items,
        judge_fn,
        observation_run_ids=obs_ids,
        min_exact_agreement=args.min_exact_agreement,
        min_pearson=args.min_pearson,
        min_pairs=args.min_pairs,
    )

    out_json = args.out_json or (eval_dir / "llm-judge-scores.json")
    out_json.write_text(
        json.dumps(output.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    out_md = args.out_md or (eval_dir / "llm-judge-scores.md")
    write_judge_markdown(out_md, output)

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
