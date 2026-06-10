"""Generate holdout-3107-rerun-summary.md after Phase 3.10.7 judge rerun."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.judge_prescreen import load_prescreen_report
from scripts.llm_judge import load_judge_output
from scripts.run_persona_batch import split_obs_holdout
from scripts.eval_batch_manifest import load_manifest


def _dist_by_run(scores: list[dict], run_ids: list[str]) -> dict[str, dict[int, int]]:
    out: dict[str, dict[int, int]] = {}
    for rid in run_ids:
        vals = [int(s["judge_score"]) for s in scores if s["run_id"] == rid]
        out[rid] = dict(sorted(Counter(vals).items()))
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--eval-dir",
        type=Path,
        default=_REPO_ROOT / "output/Eval/phase3.10",
    )
    parser.add_argument(
        "--before-json",
        type=Path,
        default=_REPO_ROOT / "output/Eval/phase3.10/llm-judge-scores-holdout-pre-3107.bak.json",
    )
    parser.add_argument(
        "--after-json",
        type=Path,
        default=_REPO_ROOT / "output/Eval/phase3.10/llm-judge-scores-holdout-3107.json",
    )
    parser.add_argument(
        "--prescreen-json",
        type=Path,
        default=None,
        help="Default: <eval-dir>/judge-prescreen.json",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=None,
        help="Default: <eval-dir>/holdout-3107-rerun-summary.md",
    )
    args = parser.parse_args(argv)

    eval_dir = args.eval_dir if args.eval_dir.is_absolute() else _REPO_ROOT / args.eval_dir
    before_path = args.before_json if args.before_json.is_absolute() else _REPO_ROOT / args.before_json
    after_path = args.after_json if args.after_json.is_absolute() else _REPO_ROOT / args.after_json
    prescreen_path = args.prescreen_json or (eval_dir / "judge-prescreen.json")
    if not prescreen_path.is_absolute():
        prescreen_path = _REPO_ROOT / prescreen_path
    out_path = args.out or (eval_dir / "holdout-3107-rerun-summary.md")
    if not out_path.is_absolute():
        out_path = _REPO_ROOT / out_path

    _, holdout_ids = split_obs_holdout(load_manifest())
    before_raw = json.loads(before_path.read_text(encoding="utf-8"))
    after_raw = json.loads(after_path.read_text(encoding="utf-8"))
    before_dist = _dist_by_run(before_raw["scores"], holdout_ids)
    after_dist = _dist_by_run(after_raw["scores"], holdout_ids)

    prescreen = load_prescreen_report(prescreen_path)
    holdout_items = [i for i in prescreen.items if i.run_id in holdout_ids]
    holdout_ge1 = sum(1 for i in holdout_items if i.passes_threshold)
    holdout_total = len(holdout_items)
    holdout_reduction = 1.0 - (holdout_ge1 / holdout_total) if holdout_total else 0.0
    holdout_buckets = Counter(i.bucket for i in holdout_items)

    # transition counts (pairs present in both)
    before_key = {(s["run_id"], str(s["tmdb_id"])): int(s["judge_score"]) for s in before_raw["scores"]}
    after_key = {(s["run_id"], str(s["tmdb_id"])): int(s["judge_score"]) for s in after_raw["scores"]}
    transitions: Counter[tuple[int, int]] = Counter()
    for key in before_key:
        if key in after_key:
            transitions[(before_key[key], after_key[key])] += 1

    lines = [
        "# Phase 3.10.7 · Holdout full judge rerun summary (3.10.1b)",
        "",
        f"**Generated:** {datetime.now(UTC).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**prompt_version (holdout):** {after_raw.get('prompt_version', '3.10.1b-logic-0-guard')}",
        f"**eval_dir:** `{eval_dir.relative_to(_REPO_ROOT).as_posix()}`",
        "",
        "## Holdout judge distribution (before → after)",
        "",
        "| run | before (0/1/2) | after (0/1/2) |",
        "| --- | --- | --- |",
    ]
    for rid in holdout_ids:
        b = before_dist.get(rid, {})
        a = after_dist.get(rid, {})
        fmt = lambda d: f"{{{', '.join(f'{k}: {v}' for k, v in sorted(d.items()))}}}"
        lines.append(f"| {rid} | {fmt(b)} | {fmt(a)} |")

    lines.extend(
        [
            "",
            "## Transition counts (pre-rerun → 3.10.1b)",
            "",
        ]
    )
    for (old, new), n in sorted(transitions.items()):
        lines.append(f"- {old}→{new}: **{n}**")

    lines.extend(
        [
            "",
            "## Prescreen (frozen threshold judge≥1)",
            "",
            f"- **holdout pairs scored:** {holdout_total}",
            f"- **holdout judge≥1 pool:** {holdout_ge1}",
            f"- **holdout workload_reduction:** {holdout_reduction:.1%}",
            f"- downgrade: {holdout_buckets.get('downgrade', 0)}",
            f"- manual: {holdout_buckets.get('manual', 0)}",
            f"- highlight: {holdout_buckets.get('highlight', 0)}",
            "",
            "## Full corpus prescreen buckets (156)",
            "",
            f"- downgrade: {prescreen.bucket_counts.get('downgrade', 0)}",
            f"- manual: {prescreen.bucket_counts.get('manual', 0)}",
            f"- highlight: {prescreen.bucket_counts.get('highlight', 0)}",
            "",
            "## Obs threshold safety (from obs-fresh-labels via calibration JSON)",
            "",
            f"- n_human_labeled: {prescreen.threshold_safety.n_human_labeled}",
            f"- n_human_two_killed: {prescreen.threshold_safety.n_human_two_killed}",
            f"- zero_human_two_killed: **{'YES' if prescreen.threshold_safety.zero_human_two_killed else 'NO'}**",
            "",
            "## Artifacts",
            "",
            "- `llm-judge-scores-holdout-pre-3107.bak.json` — pre-rerun holdout baseline",
            "- `llm-judge-scores-holdout-3107.json` — 3.10.1b holdout rerun",
            "- `llm-judge-scores.json` — unified 156-pair corpus",
            "- `judge-prescreen.json` / `judge-prescreen.md`",
            "- `threshold-safety-report.md`",
            "",
        ]
    )
    out_path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
