"""Phase 3.10.7 pre-approve: threshold split sections + baseline export."""

from __future__ import annotations

import json
import sys
from dataclasses import replace
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.apply_obs_fresh_labels_phase310 import extract_human_labels_from_review
from scripts.eval_batch_manifest import load_manifest
from scripts.judge_prescreen import PrescreenConfig, compute_threshold_safety, load_prescreen_report
from scripts.llm_judge import load_judge_output
from scripts.run_persona_batch import split_obs_holdout
from scripts.summarize_eval import parse_unified_review, summarize_runs


def _human_merged_output(eval_dir: Path):
    text = (eval_dir / "high-hit-score-review.md").read_text(encoding="utf-8")
    human_map, _ = extract_human_labels_from_review(text)
    output = load_judge_output(eval_dir / "llm-judge-scores.json")
    new_scores = []
    for row in output.scores:
        label = human_map.get((row.run_id, str(row.tmdb_id)))
        if label is None:
            new_scores.append(
                replace(row, human_score=None, human_resonance_type=None)
            )
        else:
            new_scores.append(
                replace(
                    row,
                    human_score=label.score,
                    human_resonance_type=label.resonance_type,
                )
            )
    return replace(output, scores=new_scores), text


def append_threshold_split(eval_dir: Path) -> tuple:
    output, _ = _human_merged_output(eval_dir)
    cfg = PrescreenConfig(min_judge_score=1, threshold_frozen=True)
    obs_ids, holdout_ids = split_obs_holdout(load_manifest())
    obs_scores = [s for s in output.scores if s.run_id in obs_ids]
    holdout_scores = [s for s in output.scores if s.run_id in holdout_ids]
    obs_ts = compute_threshold_safety(obs_scores, cfg)
    holdout_ts = compute_threshold_safety(holdout_scores, cfg)

    path = eval_dir / "threshold-safety-report.md"
    base = path.read_text(encoding="utf-8").rstrip()
    marker = "## Observation set (01–04)"
    if marker in base:
        base = base.split(marker)[0].rstrip()

    lines = [
        base,
        "",
        marker,
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| n_scored | {obs_ts.n_scored} |",
        f"| n_human_labeled | {obs_ts.n_human_labeled} |",
        f"| n_human_two | {obs_ts.n_human_two} |",
        f"| n_human_two_killed | {obs_ts.n_human_two_killed} |",
        f"| zero_human_two_killed | **{'YES' if obs_ts.zero_human_two_killed else 'NO'}** |",
    ]
    if obs_ts.workload_reduction_rate is not None:
        lines.append(
            f"| workload_reduction_rate | {obs_ts.workload_reduction_rate:.1%} |"
        )
    lines += [
        "",
        "## Holdout set (05–10)",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        f"| n_scored | {holdout_ts.n_scored} |",
        f"| n_human_labeled | {holdout_ts.n_human_labeled} |",
        f"| n_human_two | {holdout_ts.n_human_two} |",
        f"| n_human_two_killed | {holdout_ts.n_human_two_killed} |",
        f"| zero_human_two_killed | **{'YES' if holdout_ts.zero_human_two_killed else 'NO'}** |",
    ]
    if holdout_ts.workload_reduction_rate is not None:
        lines.append(
            f"| workload_reduction_rate | {holdout_ts.workload_reduction_rate:.1%} |"
        )
    if holdout_ts.killed_items:
        lines += ["", "### Holdout killed human=2", ""]
        for row in holdout_ts.killed_items:
            lines.append(
                f"- {row['run_id']} / {row['tmdb_id']}: "
                f"judge={row['judge_score']} human={row['human_score']} — {row['title']}"
            )
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return obs_ts, holdout_ts


def write_baseline(eval_dir: Path) -> dict:
    prescreen = load_prescreen_report(eval_dir / "judge-prescreen.json")
    review_path = eval_dir / "high-hit-score-review.md"
    text = review_path.read_text(encoding="utf-8")
    runs = parse_unified_review(review_path, text)
    calibration = json.loads(
        (eval_dir / "llm-judge-scores.json").read_text(encoding="utf-8")
    )
    summary = summarize_runs(runs, calibration=calibration)
    (eval_dir / "holdout-prescreen-baseline.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    d5 = summary.get("success_criteria") or summary["global"]["d5_success_criteria"]
    res = d5["resonance"]
    full = res["full_batch"]
    focal = full["focal_channel"]
    neutral_diag = full["neutral_diagnostic"]
    wf = d5.get("workflow") or {}
    ts = prescreen.threshold_safety
    wr = (
        f"| workload_reduction_rate | {ts.workload_reduction_rate:.1%} |"
        if ts.workload_reduction_rate is not None
        else "| workload_reduction_rate | — |"
    )
    lines = [
        "# Phase 3.10.7 · Holdout prescreen recheck baseline",
        "",
        f"**Generated:** {datetime.now(UTC).strftime('%Y-%m-%d')}",
        f"**Frozen threshold:** judge≥{prescreen.config.min_judge_score} "
        f"(threshold_frozen={prescreen.config.threshold_frozen})",
        "",
        "## Prescreen buckets (full corpus 156)",
        "",
        f"- downgrade (judge=0): {prescreen.bucket_counts.get('downgrade', 0)}",
        f"- manual (judge=1): {prescreen.bucket_counts.get('manual', 0)}",
        f"- highlight (judge=2): {prescreen.bucket_counts.get('highlight', 0)}",
        "",
        "## Resonance recheck (dual-axis v2 · n1 diagnostic-only)",
        "",
        "| Metric | focal_channel | n1_diagnostic | signal? |",
        "| --- | --- | --- | --- |",
        f"| structural_2_rate | {focal.get('structural_2_rate', 0):.1%} | "
        f"{neutral_diag.get('structural_2_rate', 0):.1%} | "
        f"{'YES' if res.get('focal_channel_has_signal') else 'NO'} |",
        f"| obs focal signal | {res.get('obs_focal_channel_has_signal')} |",
        f"| holdout focal signal | {res.get('holdout_focal_channel_has_signal')} |",
        f"| obs/holdout consistent | {res.get('obs_holdout_consistent')} |",
        "",
        "## Workflow safety",
        "",
        "| Metric | Value |",
        "| --- | --- |",
        wr,
        f"| n_human_two | {ts.n_human_two} |",
        f"| n_human_two_killed | {ts.n_human_two_killed} |",
        f"| zero_human_two_killed | **{'YES' if ts.zero_human_two_killed else 'NO'}** |",
        f"| judge_calibration_trusted | {wf.get('judge_calibration_trusted')} |",
        "",
        "## Artifacts",
        "",
        "- `llm-judge-scores.json` — full 156 judge corpus",
        "- `judge-prescreen.json` / `threshold-safety-report.md`",
        "- `holdout-fresh-labels.json` — prescreen-pool human labels",
        "- `holdout-prescreen-baseline.json` — summarize_eval D5 export",
        "",
    ]
    out = eval_dir / "holdout-prescreen-baseline-3107.md"
    out.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    return summary


def main() -> int:
    eval_dir = _REPO_ROOT / "output/Eval/phase3.10"
    obs_ts, holdout_ts = append_threshold_split(eval_dir)
    summary = write_baseline(eval_dir)
    res = (summary.get("success_criteria") or summary["global"]["d5_success_criteria"])[
        "resonance"
    ]
    print(
        f"obs killed={obs_ts.n_human_two_killed} "
        f"holdout killed={holdout_ts.n_human_two_killed}"
    )
    print(
        f"focal={res['full_batch']['focal_channel'].get('structural_2_rate', 0):.1%} "
        f"n1_diag={res['full_batch']['neutral_diagnostic'].get('structural_2_rate', 0):.1%}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
