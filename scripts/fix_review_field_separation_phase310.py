"""Relocate LLM-generated text from human editor fields to judge fields (Phase 3.10.7).

Human fields (共振分, 共振类型, 打分备注) must contain only human editorial input.
LLM output from ``apply_obs_fresh_labels`` / ``apply_holdout_prescreen_labels`` that
was incorrectly written to human fields is cleared or preserved per policy:

- obs 01–04: keep approved 共振分/共振类型 from ``obs-fresh-labels.json``; clear LLM 打分备注
- holdout 05–10: reset human fields when they came from LLM fresh-label scripts
- judge fields: SSOT ``llm-judge-scores.json``, with optional causal_test backfill from
  parsed remark when the official judge left it empty
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, replace
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.apply_obs_fresh_labels_phase310 import FreshLabel
from scripts.llm_judge import (
    JudgeOutput,
    JudgeResult,
    _SCORE_LINE,
    _TMDB_LINE,
    _TYPE_LINE,
    integrate_judge_into_review,
    load_judge_output,
)
from scripts.run_persona_batch import OBS_RUN_PREFIXES

_REMARK_LINE = re.compile(r"^(-\s*\*\*打分备注\*\*:)\s*(.*)$", re.MULTILINE)
_RUN_ID_COMMENT = re.compile(r"^<!-- run_id: (\S+) -->$", re.MULTILINE)
_V2_PREFIX = "v2 fresh · "
_CAUSAL_MARKER = " · 反测: "
_HOLDOUT_SUFFIX = " · holdout prescreen"
_HEADING = re.compile(r"^###\s+", re.MULTILINE)

_HUMAN_SCORE_PLACEHOLDER = (
    "- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->"
)
_HUMAN_TYPE_PLACEHOLDER = (
    "- **共振类型**:   <!-- 0 留空；1→深层共振（仅逻辑，无表层）|表层沾边；2→强共振（表层 + 逻辑） -->"
)
_HUMAN_REMARK_PLACEHOLDER = "- **打分备注**: （可选）"


def is_llm_generated_remark(content: str) -> bool:
    text = content.strip()
    return text.startswith("v2 fresh") or "holdout prescreen" in text


def parse_llm_remark_content(content: str) -> tuple[str, str]:
    """Return ``(rationale, causal_test)`` parsed from an LLM 打分备注 body."""
    text = content.strip()
    if text.endswith(_HOLDOUT_SUFFIX):
        text = text[: -len(_HOLDOUT_SUFFIX)].strip()
    if text.startswith(_V2_PREFIX):
        text = text[len(_V2_PREFIX) :]
    if _CAUSAL_MARKER in text:
        rationale, causal = text.rsplit(_CAUSAL_MARKER, 1)
        return rationale.strip(), causal.strip()
    return text.strip(), ""


def _is_obs_run(run_id: str) -> bool:
    return run_id.startswith(OBS_RUN_PREFIXES)


def _format_human_score_line(score: int) -> str:
    return f"- **共振分**: {score}  <!-- 总编填写 0 / 1 / 2 -->"


def _format_human_type_line(resonance_type: str | None) -> str:
    type_str = resonance_type or ""
    return (
        f"- **共振类型**: {type_str}  "
        "<!-- 0 留空；1→深层共振（仅逻辑，无表层）|表层沾边；2→强共振（表层 + 逻辑） -->"
    )


def _set_human_score_type(block: str, score: int, resonance_type: str | None) -> str:
    block, _ = _SCORE_LINE.subn(_format_human_score_line(score), block, count=1)
    block, _ = _TYPE_LINE.subn(_format_human_type_line(resonance_type), block, count=1)
    return block


def _reset_human_fields(block: str) -> str:
    block, _ = _SCORE_LINE.subn(_HUMAN_SCORE_PLACEHOLDER, block, count=1)
    block, _ = _TYPE_LINE.subn(_HUMAN_TYPE_PLACEHOLDER, block, count=1)
    return block


def _clear_llm_remark(block: str) -> str:
    def _repl(match: re.Match[str]) -> str:
        body = match.group(2).strip()
        if is_llm_generated_remark(body):
            return _HUMAN_REMARK_PLACEHOLDER
        return match.group(0)

    return _REMARK_LINE.sub(_repl, block, count=1)


@dataclass
class FixStats:
    blocks_scanned: int = 0
    remarks_cleared: int = 0
    obs_scores_preserved: int = 0
    holdout_human_reset: int = 0
    judge_causal_backfilled: int = 0


def _load_fresh_labels(path: Path) -> dict[tuple[str, str], FreshLabel]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    out: dict[tuple[str, str], FreshLabel] = {}
    for row in data.get("labels") or []:
        key = (row["run_id"], str(row["tmdb_id"]))
        if "rationale" not in row and row.get("remark"):
            rat, _ = parse_llm_remark_content(str(row["remark"]))
            row = {**row, "rationale": rat}
        out[key] = FreshLabel(**row)
    return out


def augment_judge_output(
    output: JudgeOutput,
    supplemental: dict[tuple[str, str], tuple[str, str]],
) -> tuple[JudgeOutput, int]:
    """Fill empty judge rationale/causal_test from parsed LLM remarks."""
    backfilled = 0
    new_scores: list[JudgeResult] = []
    for result in output.scores:
        key = (result.run_id, str(result.tmdb_id))
        extra = supplemental.get(key)
        if not extra:
            new_scores.append(result)
            continue
        rationale_extra, causal_extra = extra
        new_rationale = result.rationale
        new_causal = result.causal_test
        changed = False
        if not new_rationale.strip() and rationale_extra:
            new_rationale = rationale_extra
            changed = True
        if not new_causal.strip() and causal_extra:
            new_causal = causal_extra
            changed = True
        if changed:
            backfilled += 1
        new_scores.append(
            replace(
                result,
                rationale=new_rationale,
                causal_test=new_causal,
            )
        )
    return replace(output, scores=new_scores), backfilled


def fix_review_field_separation(
    review_text: str,
    *,
    judge_output: JudgeOutput,
    obs_labels: dict[tuple[str, str], FreshLabel],
    holdout_labels: dict[tuple[str, str], FreshLabel],
) -> tuple[str, FixStats]:
    stats = FixStats()
    supplemental: dict[tuple[str, str], tuple[str, str]] = {}

    chunks = re.split(r"(?=<!-- run_id: )", review_text)
    if len(chunks) <= 1:
        return review_text, stats

    out_parts: list[str] = [chunks[0]]
    for chunk in chunks[1:]:
        run_match = _RUN_ID_COMMENT.match(chunk)
        run_id = run_match.group(1) if run_match else ""
        parts = re.split(r"(?=^### )", chunk, flags=re.MULTILINE)
        patched = parts[0]
        for part in parts[1:]:
            if not part.strip():
                continue
            tmdb_match = _TMDB_LINE.search(part)
            if not tmdb_match or not run_id:
                patched += part
                continue
            key = (run_id, tmdb_match.group(1))
            stats.blocks_scanned += 1
            block = part

            remark_match = _REMARK_LINE.search(block)
            if remark_match and is_llm_generated_remark(remark_match.group(2)):
                rationale, causal = parse_llm_remark_content(remark_match.group(2))
                supplemental[key] = (rationale, causal)
                block = _clear_llm_remark(block)
                stats.remarks_cleared += 1

            if key in obs_labels and _is_obs_run(run_id):
                label = obs_labels[key]
                block = _set_human_score_type(
                    block, label.score, label.resonance_type
                )
                stats.obs_scores_preserved += 1
            elif key in holdout_labels and not _is_obs_run(run_id):
                block = _reset_human_fields(block)
                stats.holdout_human_reset += 1

            patched += block
        out_parts.append(patched)

    merged = "".join(out_parts)
    augmented, stats.judge_causal_backfilled = augment_judge_output(
        judge_output, supplemental
    )
    merged = integrate_judge_into_review(merged, augmented)
    if not merged.endswith("\n"):
        merged += "\n"
    return merged, stats


def _sanitize_fresh_labels_audit(path: Path) -> int:
    """Strip LLM boilerplate from audit JSON remark fields; keep rationale separate."""
    if not path.is_file():
        return 0
    data = json.loads(path.read_text(encoding="utf-8"))
    changed = 0
    for row in data.get("labels") or []:
        remark = str(row.get("remark") or "")
        if not is_llm_generated_remark(remark):
            continue
        rationale, causal = parse_llm_remark_content(remark)
        row["rationale"] = rationale
        if causal and not row.get("causal_test"):
            row["causal_test"] = causal
        row["remark"] = ""
        row["source"] = row.get("source") or "llm"
        changed += 1
    if changed:
        path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return changed


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--eval-dir",
        type=Path,
        default=_REPO_ROOT / "output" / "Eval" / "phase3.10-visible",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report counts without writing files",
    )
    args = parser.parse_args(argv)

    eval_dir = args.eval_dir if args.eval_dir.is_absolute() else _REPO_ROOT / args.eval_dir
    review_path = eval_dir / "high-hit-score-review.md"
    judge_path = eval_dir / "llm-judge-scores.json"
    obs_path = eval_dir / "obs-fresh-labels.json"
    holdout_path = eval_dir / "holdout-fresh-labels.json"

    if not review_path.is_file():
        print(f"missing review: {review_path}", file=sys.stderr)
        return 1
    if not judge_path.is_file():
        print(f"missing judge SSOT: {judge_path}", file=sys.stderr)
        return 1

    review_text = review_path.read_text(encoding="utf-8")
    judge_output = load_judge_output(judge_path)
    obs_labels = _load_fresh_labels(obs_path)
    holdout_labels = _load_fresh_labels(holdout_path)

    fixed, stats = fix_review_field_separation(
        review_text,
        judge_output=judge_output,
        obs_labels=obs_labels,
        holdout_labels=holdout_labels,
    )

    print(
        f"blocks={stats.blocks_scanned} remarks_cleared={stats.remarks_cleared} "
        f"obs_preserved={stats.obs_scores_preserved} "
        f"holdout_reset={stats.holdout_human_reset} "
        f"judge_backfill={stats.judge_causal_backfilled}"
    )

    if args.dry_run:
        return 0

    review_path.write_text(fixed, encoding="utf-8")
    obs_changed = _sanitize_fresh_labels_audit(obs_path)
    holdout_changed = _sanitize_fresh_labels_audit(holdout_path)
    print(f"wrote {review_path}")
    if obs_changed:
        print(f"sanitized {obs_changed} rows in {obs_path}")
    if holdout_changed:
        print(f"sanitized {holdout_changed} rows in {holdout_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
