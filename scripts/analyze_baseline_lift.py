"""analyze_baseline_lift.py · Phase 3.7.0 baseline vs creative 2-point lift from scored eval."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.summarize_eval import RunSummary, _collect_paths, parse_eval_markdown

CREATIVE_AGENTS = frozenset({"A2", "A4", "A7"})
BASELINE_AGENT = "A1"
_BUCKETS = ("baseline-only", "creative-only", "both")
_LIFT_EPSILON = 0.001


@dataclass
class BucketStats:
    scored: int = 0
    twos: int = 0
    ones: int = 0
    zeros: int = 0

    @property
    def two_rate(self) -> float:
        return self.twos / self.scored if self.scored else 0.0


@dataclass
class BaselineLiftReport:
    source_dir: str
    runs_scanned: int
    buckets: dict[str, BucketStats] = field(default_factory=dict)
    unbucketed: int = 0
    missing_scores: int = 0

    def __post_init__(self) -> None:
        for name in _BUCKETS:
            self.buckets.setdefault(name, BucketStats())


def _classify_bucket(*, also_baseline: bool, agents: list[str]) -> str | None:
    agent_set = {a.upper() for a in agents}
    has_baseline = also_baseline or BASELINE_AGENT in agent_set
    has_creative = bool(agent_set & CREATIVE_AGENTS)

    if has_baseline and not has_creative:
        return "baseline-only"
    if has_creative and not has_baseline:
        return "creative-only"
    if has_baseline and has_creative:
        return "both"
    return None


def analyze_runs(runs: list[RunSummary]) -> BaselineLiftReport:
    report = BaselineLiftReport(
        source_dir="",
        runs_scanned=len(runs),
    )

    for run in runs:
        for cand in run.candidates:
            if cand.score is None:
                report.missing_scores += 1
                continue

            bucket = _classify_bucket(
                also_baseline=cand.also_baseline,
                agents=cand.triggered_by,
            )
            if bucket is None:
                report.unbucketed += 1
                continue

            stats = report.buckets[bucket]
            stats.scored += 1
            if cand.score == 2:
                stats.twos += 1
            elif cand.score == 1:
                stats.ones += 1
            else:
                stats.zeros += 1

    return report


def _creative_aggregate(report: BaselineLiftReport) -> BucketStats:
    """Merge creative-only + both for 'any creative steering' comparison."""
    merged = BucketStats()
    for name in ("creative-only", "both"):
        stats = report.buckets[name]
        merged.scored += stats.scored
        merged.twos += stats.twos
        merged.ones += stats.ones
        merged.zeros += stats.zeros
    return merged


def _go_no_go(report: BaselineLiftReport) -> tuple[str, str, float, float]:
    baseline = report.buckets["baseline-only"]
    creative_only = report.buckets["creative-only"]
    creative_any = _creative_aggregate(report)

    lift_pure = creative_only.two_rate - baseline.two_rate
    lift_any = creative_any.two_rate - baseline.two_rate

    # Primary anchor: creative-only vs baseline-only (A1 neutral). The "both"
    # bucket mixes A1 signal and is reported separately, not used for verdict.
    if lift_pure > _LIFT_EPSILON:
        verdict = "Go"
        reason = (
            f"creative-only 2-point rate ({creative_only.two_rate:.1%}, "
            f"{creative_only.twos}/{creative_only.scored}) exceeds baseline-only "
            f"({baseline.two_rate:.1%}, {baseline.twos}/{baseline.scored}); "
            f"lift={lift_pure:+.1%}"
        )
    else:
        verdict = "No-Go"
        reason = (
            f"creative-only vs A1 neutral lift ≈ 0 ({lift_pure:+.1%}; "
            f"creative-touched aggregate {lift_any:+.1%}); pause and re-evaluate "
            f"whether emotion steering is worth pursuing before 3.7.1"
        )

    return verdict, reason, lift_pure, lift_any


def _pct(rate: float) -> str:
    return f"{rate:.1%}"


def format_markdown(report: BaselineLiftReport) -> str:
    baseline = report.buckets["baseline-only"]
    creative_only = report.buckets["creative-only"]
    both = report.buckets["both"]
    creative_any = _creative_aggregate(report)
    verdict, reason, lift_pure, lift_any = _go_no_go(report)

    lines = [
        "# Phase 3.7.0 · Baseline vs Creative 2-Point Lift",
        "",
        f"- **Source:** `{report.source_dir}`",
        f"- **Runs scanned:** {report.runs_scanned}",
        f"- **Scored candidates (excluded missing 共振分):** "
        f"{sum(b.scored for b in report.buckets.values())}",
        f"- **Missing 共振分:** {report.missing_scores}",
        "",
        "## Buckets",
        "",
        "| Bucket | Scored | 2-point | 2-point rate | 1-point | 0-point |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]

    for name in _BUCKETS:
        stats = report.buckets[name]
        lines.append(
            f"| {name} | {stats.scored} | {stats.twos} | {_pct(stats.two_rate)} | "
            f"{stats.ones} | {stats.zeros} |"
        )

    lines.extend(
        [
            "",
            "## Creative vs A1 neutral lift",
            "",
            f"- **baseline-only (A1 neutral):** {_pct(baseline.two_rate)} "
            f"({baseline.twos}/{baseline.scored})",
            f"- **creative-only (A2/A4/A7, no A1):** {_pct(creative_only.two_rate)} "
            f"({creative_only.twos}/{creative_only.scored})",
            f"- **both (A1 + creative):** {_pct(both.two_rate)} "
            f"({both.twos}/{both.scored})",
            f"- **creative-touched (creative-only + both):** {_pct(creative_any.two_rate)} "
            f"({creative_any.twos}/{creative_any.scored})",
            "",
            f"- **Lift (creative-only - baseline-only):** {lift_pure:+.1%}",
            f"- **Lift (creative-touched - baseline-only):** {lift_any:+.1%}",
            "",
            f"## Go/No-Go: **{verdict}**",
            "",
            reason,
            "",
            "### Interpretation",
            "",
            "- **baseline-only:** candidate hit only via A1 faithful restatement.",
            "- **creative-only:** hit via A2/A4/A7 injection-style agents without A1.",
            "- **both:** A1 and at least one creative agent both contributed hits.",
            "- Phase 3.7 bets on persona emotional diffusion *adding* resonance beyond "
            "A1; this anchor uses Phase 3.6 scored data as the pre-refactor baseline.",
            "",
        ]
    )

    if report.unbucketed:
        lines.append(f"_Note: {report.unbucketed} scored candidate(s) could not be bucketed._")
        lines.append("")

    return "\n".join(lines)


def analyze_eval_dir(eval_dir: Path) -> BaselineLiftReport:
    paths = _collect_paths(argparse.Namespace(dir=str(eval_dir), files=[]))
    runs = [
        parse_eval_markdown(path, path.read_text(encoding="utf-8")) for path in paths
    ]
    report = analyze_runs(runs)
    report.source_dir = str(eval_dir.resolve())
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Compute baseline-only / creative-only / both 2-point rates.",
    )
    parser.add_argument(
        "--dir",
        required=True,
        help="Eval directory (e.g. output/Eval/phase3.6)",
    )
    parser.add_argument(
        "--out",
        help="Markdown output path (default: output/Eval/phase3.7/baseline-lift.md)",
    )
    args = parser.parse_args(argv)

    eval_dir = Path(args.dir)
    if not eval_dir.is_absolute():
        eval_dir = _REPO_ROOT / eval_dir
    if not eval_dir.is_dir():
        print(f"error: directory not found: {eval_dir}", file=sys.stderr)
        return 2

    report = analyze_eval_dir(eval_dir)
    md = format_markdown(report)

    out_path = Path(args.out) if args.out else _REPO_ROOT / "output/Eval/phase3.7/baseline-lift.md"
    if not out_path.is_absolute():
        out_path = _REPO_ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")
    print(md)
    print(f"\nWrote {out_path.resolve()}", file=sys.stderr)

    verdict, _, _, _ = _go_no_go(report)
    return 0 if verdict == "Go" else 1


if __name__ == "__main__":
    raise SystemExit(main())
