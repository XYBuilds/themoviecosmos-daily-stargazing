"""Phase 3.10.7 holdout prescreen + recheck baseline orchestrator."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.judge_prescreen import (
    PrescreenConfig,
    integrate_prescreen_into_review,
    load_prescreen_report,
    run_prescreen,
    write_prescreen_json,
    write_prescreen_markdown,
    write_threshold_safety_report,
)
from scripts.llm_judge import integrate_judge_into_review, load_judge_output
from scripts.merge_phase310_judge_corpus import merge_corpus
from scripts.run_phase39_judge_batch import DEFAULT_JUDGE_WORKERS
from scripts.summarize_eval import parse_unified_review, summarize_runs

PHASE310 = _REPO_ROOT / "output" / "Eval" / "phase3.10"


def _run(cmd: list[str]) -> None:
    print("+", " ".join(cmd), flush=True)
    subprocess.run(cmd, check=True, cwd=_REPO_ROOT)


def write_baseline_summary(
    eval_dir: Path,
    prescreen_path: Path,
    summarize_json: dict,
) -> None:
    prescreen = load_prescreen_report(prescreen_path)
    ts = prescreen.threshold_safety
    d5 = summarize_json.get("d5_success_criteria") or {}
    res = d5.get("resonance") or {}
    wf = d5.get("workflow") or {}
    full = res.get("full_batch") or {}
    focal = full.get("focal_channel") or {}
    neutral_diag = full.get("neutral_diagnostic") or {}

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
        f"| Metric | Value |",
        f"| --- | --- |",
        (
            f"| workload_reduction_rate | {ts.workload_reduction_rate:.1%} |"
            if ts.workload_reduction_rate is not None
            else "| workload_reduction_rate | — |"
        ),
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
    out = eval_dir / "holdout-prescreen-baseline.md"
    out.write_text("\n".join(lines), encoding="utf-8", newline="\n")
    print(f"wrote {out}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-dir", type=Path, default=PHASE310)
    parser.add_argument("--provider", default=None)
    parser.add_argument(
        "--workers",
        type=int,
        default=DEFAULT_JUDGE_WORKERS,
        metavar="N",
        help=f"Concurrent judge pair scorers for holdout (default: {DEFAULT_JUDGE_WORKERS})",
    )
    parser.add_argument("--skip-judge", action="store_true")
    parser.add_argument("--skip-label", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    eval_dir = args.eval_dir if args.eval_dir.is_absolute() else _REPO_ROOT / args.eval_dir
    obs_json = _REPO_ROOT / "output/Eval/phase3.10/calibration/llm-judge-scores.json"
    holdout_json = eval_dir / "llm-judge-scores-holdout.json"
    full_json = eval_dir / "llm-judge-scores.json"
    full_md = eval_dir / "llm-judge-scores.md"
    prescreen_json = eval_dir / "judge-prescreen.json"
    review_path = eval_dir / "high-hit-score-review.md"

    if not args.skip_judge:
        cmd = [
            sys.executable,
            "scripts/run_phase39_judge_batch.py",
            "--eval-dir",
            str(eval_dir.relative_to(_REPO_ROOT)),
            "--out-json",
            str(holdout_json.relative_to(_REPO_ROOT)),
            "--holdout-only",
            "--mimo-thinking",
            "enabled",
            "--workers",
            str(max(1, args.workers)),
        ]
        if args.provider:
            cmd.extend(["--provider", args.provider])
        if not args.dry_run:
            _run(cmd)

    if not args.dry_run:
        merge_corpus(obs_json, holdout_json, full_json, full_md)

        config = PrescreenConfig(min_judge_score=1, threshold_frozen=True)
        report = run_prescreen(load_judge_output(full_json), config)
        write_prescreen_json(prescreen_json, report)
        write_prescreen_markdown(eval_dir / "judge-prescreen.md", report)
        write_threshold_safety_report(
            eval_dir / "threshold-safety-report.md", report
        )

        output = load_judge_output(full_json)
        review_text = integrate_judge_into_review(
            review_path.read_text(encoding="utf-8"), output
        )
        review_text = integrate_prescreen_into_review(review_text, report)
        review_path.write_text(review_text, encoding="utf-8")

    if not args.skip_label and not args.dry_run:
        cmd = [
            sys.executable,
            "scripts/apply_holdout_prescreen_labels_phase310.py",
            "--eval-dir",
            str(eval_dir.relative_to(_REPO_ROOT)),
            "--prescreen-json",
            str(prescreen_json.relative_to(_REPO_ROOT)),
        ]
        if args.provider:
            cmd.extend(["--provider", args.provider])
        _run(cmd)

    if not args.dry_run:
        runs = parse_unified_review(
            review_path, review_path.read_text(encoding="utf-8")
        )
        calibration = json.loads(full_json.read_text(encoding="utf-8"))
        summary = summarize_runs(runs, calibration=calibration)
        baseline_json = eval_dir / "holdout-prescreen-baseline.json"
        baseline_json.write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        write_baseline_summary(eval_dir, prescreen_json, summary)
        print(f"wrote {baseline_json}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
