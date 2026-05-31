"""summarize_eval.py · 解析已评分 Eval Markdown，汇总闸门指标."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]

_SCORE_LINE = re.compile(r"^-\s*\*\*共振分\*\*:\s*(.*)$", re.MULTILINE)
_TMDB_LINE = re.compile(r"^-\s*\*\*tmdb_id\*\*:\s*(\S+)", re.MULTILINE)
_ALSO_BASELINE_LINE = re.compile(
    r"^-\s*\*\*also_baseline\*\*:\s*(true|false)",
    re.MULTILINE | re.IGNORECASE,
)
_AGENTS_TAG = re.compile(r"\[([^\]]+)\]")
_BASELINE_ONLY_TAG = re.compile(r"baseline\s+only", re.IGNORECASE)
_RUN_ID_LINE = re.compile(r"^-\s*run_id:\s*(\S+)", re.MULTILINE)
_GATE_BATCH_PASS_RATE = 0.60


@dataclass
class CandidateScore:
    title: str
    tmdb_id: str
    triggered_by: list[str]
    also_baseline: bool
    score: int | None  # None = missing


@dataclass
class RunSummary:
    path: str
    run_id: str
    candidates: list[CandidateScore] = field(default_factory=list)

    @property
    def has_any_score_2(self) -> bool:
        return any(c.score == 2 for c in self.candidates)

    @property
    def missing_count(self) -> int:
        return sum(1 for c in self.candidates if c.score is None)


def _strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def _parse_agents_from_heading(heading: str) -> list[str]:
    match = _AGENTS_TAG.search(heading)
    if not match:
        return []
    tag = match.group(1).strip()
    if _BASELINE_ONLY_TAG.search(tag):
        return []
    return [part.strip() for part in tag.split(",") if part.strip()]


def _parse_score(raw_line: str) -> int | None:
    cleaned = _strip_html_comments(raw_line).strip()
    match = re.search(r"\b([012])\b", cleaned)
    if match:
        return int(match.group(1))
    return None


def _is_creative_candidate(cand: CandidateScore) -> bool:
    if cand.triggered_by:
        return True
    if cand.also_baseline and not cand.triggered_by:
        return False
    heading_agents = cand.triggered_by
    return bool(heading_agents)


def _split_candidate_blocks(text: str) -> list[tuple[str, str]]:
    """Return (heading_line, block_body) for each ### candidate section."""
    section_match = re.search(r"^##\s*候选星轨.*$", text, re.MULTILINE)
    if not section_match:
        return []

    section = text[section_match.start() :]
    parts = re.split(r"(?=^###\s+)", section, flags=re.MULTILINE)
    blocks: list[tuple[str, str]] = []
    for part in parts[1:]:
        lines = part.splitlines()
        if not lines:
            continue
        heading = lines[0]
        body = "\n".join(lines[1:])
        blocks.append((heading, body))
    return blocks


def _infer_run_id(path: Path, text: str) -> str:
    run_id_match = _RUN_ID_LINE.search(text)
    if run_id_match:
        return run_id_match.group(1)
    if path.name == "candidates.md" and path.parent.name != path.parent.parent.name:
        return path.parent.name
    return path.stem


def parse_eval_markdown(path: Path, text: str) -> RunSummary:
    run_id = _infer_run_id(path, text)

    candidates: list[CandidateScore] = []
    for heading, body in _split_candidate_blocks(text):
        title = heading.removeprefix("### ").strip()
        tmdb_match = _TMDB_LINE.search(body)
        tmdb_id = tmdb_match.group(1) if tmdb_match else ""
        baseline_match = _ALSO_BASELINE_LINE.search(body)
        also_baseline = (
            baseline_match.group(1).lower() == "true" if baseline_match else False
        )
        triggered_by = _parse_agents_from_heading(title)

        score: int | None = None
        score_match = _SCORE_LINE.search(body)
        if score_match:
            score = _parse_score(score_match.group(1))

        candidates.append(
            CandidateScore(
                title=title,
                tmdb_id=tmdb_id,
                triggered_by=triggered_by,
                also_baseline=also_baseline,
                score=score,
            )
        )

    return RunSummary(path=str(path), run_id=run_id, candidates=candidates)


def _bucket_rates(runs: list[RunSummary]) -> tuple[float, float, dict[str, int]]:
    """Return (baseline_2_rate, creative_2_rate, counts dict)."""
    baseline_scored = 0
    baseline_twos = 0
    creative_scored = 0
    creative_twos = 0

    for run in runs:
        for cand in run.candidates:
            if cand.score is None:
                continue
            creative = _is_creative_candidate(cand)
            if creative:
                creative_scored += 1
                if cand.score == 2:
                    creative_twos += 1
            else:
                baseline_scored += 1
                if cand.score == 2:
                    baseline_twos += 1

    baseline_rate = baseline_twos / baseline_scored if baseline_scored else 0.0
    creative_rate = creative_twos / creative_scored if creative_scored else 0.0
    counts = {
        "baseline_scored": baseline_scored,
        "baseline_twos": baseline_twos,
        "creative_scored": creative_scored,
        "creative_twos": creative_twos,
    }
    return baseline_rate, creative_rate, counts


def summarize_runs(runs: list[RunSummary]) -> dict[str, Any]:
    total_runs = len(runs)
    runs_with_2 = sum(1 for r in runs if r.has_any_score_2)
    batch_pass_rate = runs_with_2 / total_runs if total_runs else 0.0
    baseline_2_rate, creative_2_rate, bucket_counts = _bucket_rates(runs)
    missing_total = sum(r.missing_count for r in runs)

    gate_reasons: list[str] = []
    batch_ok = batch_pass_rate >= _GATE_BATCH_PASS_RATE
    rate_ok = baseline_2_rate < creative_2_rate

    if not batch_ok:
        gate_reasons.append(
            f"batch pass rate {batch_pass_rate:.1%} < {_GATE_BATCH_PASS_RATE:.0%} "
            f"({runs_with_2}/{total_runs} runs with >=1 score-2)"
        )
    if not rate_ok:
        gate_reasons.append(
            f"baseline_2_rate {baseline_2_rate:.1%} not < creative_2_rate {creative_2_rate:.1%}"
        )

    gate_pass = batch_ok and rate_ok

    return {
        "runs": [
            {
                "path": r.path,
                "run_id": r.run_id,
                "has_any_score_2": r.has_any_score_2,
                "missing_count": r.missing_count,
                "candidate_count": len(r.candidates),
            }
            for r in runs
        ],
        "global": {
            "total_runs": total_runs,
            "runs_with_score_2": runs_with_2,
            "batch_pass_rate": batch_pass_rate,
            "missing_scores_total": missing_total,
            "baseline_2_rate": baseline_2_rate,
            "creative_2_rate": creative_2_rate,
            **bucket_counts,
        },
        "gate": {
            "pass": gate_pass,
            "verdict": "GATE_PASS" if gate_pass else "GATE_FAIL",
            "reasons": gate_reasons,
        },
    }


def _format_stdout(report: dict[str, Any]) -> str:
    lines: list[str] = []
    g = report["global"]
    lines.append(f"Eval runs: {g['total_runs']}")
    lines.append("")

    for run in report["runs"]:
        flag = "yes" if run["has_any_score_2"] else "no"
        missing_note = (
            f", {run['missing_count']} missing" if run["missing_count"] else ""
        )
        lines.append(
            f"  {run['run_id']}: has_any_score_2={flag}"
            f" ({run['candidate_count']} candidates{missing_note})"
        )

    lines.append("")
    lines.append(
        f"Batch pass rate: {g['batch_pass_rate']:.1%} "
        f"({g['runs_with_score_2']}/{g['total_runs']} runs with >=1 score-2)"
    )
    lines.append(
        f"baseline_2_rate: {g['baseline_2_rate']:.1%} "
        f"({g['baseline_twos']}/{g['baseline_scored']} scored baseline candidates)"
    )
    lines.append(
        f"creative_2_rate: {g['creative_2_rate']:.1%} "
        f"({g['creative_twos']}/{g['creative_scored']} scored creative candidates)"
    )
    if g["missing_scores_total"]:
        lines.append(f"Missing scores (excluded from rates): {g['missing_scores_total']}")

    lines.append("")
    gate = report["gate"]
    lines.append(gate["verdict"])
    if gate["reasons"]:
        for reason in gate["reasons"]:
            lines.append(f"  - {reason}")
    elif gate["pass"]:
        lines.append(
            f"  - batch pass rate >= {_GATE_BATCH_PASS_RATE:.0%}; "
            "baseline_2_rate < creative_2_rate"
        )

    return "\n".join(lines)


def _collect_paths(args: argparse.Namespace) -> list[Path]:
    paths: list[Path] = []
    if args.dir:
        dir_path = Path(args.dir)
        if not dir_path.is_absolute():
            dir_path = _REPO_ROOT / dir_path
        if not dir_path.is_dir():
            raise FileNotFoundError(f"directory not found: {dir_path}")
        # New layout: output/Eval/{run_id}/candidates.md
        paths.extend(sorted(dir_path.glob("*/candidates.md")))
        # Legacy flat fixtures: tests/eval_fixtures/*.md
        paths.extend(sorted(dir_path.glob("*.md")))
    paths.extend(Path(p) for p in args.files)

    resolved: list[Path] = []
    seen: set[Path] = set()
    for p in paths:
        path = p if p.is_absolute() else _REPO_ROOT / p
        path = path.resolve()
        if path.is_dir():
            candidate = path / "candidates.md"
            if candidate.is_file():
                path = candidate
            else:
                continue
        if path.suffix.lower() != ".md" or not path.is_file():
            continue
        if path.name == "GATE_RESULT.md":
            continue
        if path not in seen:
            seen.add(path)
            resolved.append(path)

    if not resolved:
        raise FileNotFoundError(
            "no eval candidates markdown found (expected */candidates.md or fixture *.md)"
        )
    return resolved


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Summarize scored Eval Markdown files and check validation gate.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="candidates.md path(s), run dir(s), or legacy fixture .md",
    )
    parser.add_argument(
        "--dir",
        help="Scan for */candidates.md (e.g. output/Eval) or top-level fixture .md",
    )
    parser.add_argument(
        "--out",
        help="Optional JSON report path.",
    )
    args = parser.parse_args(argv)

    try:
        paths = _collect_paths(args)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    runs: list[RunSummary] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        runs.append(parse_eval_markdown(path, text))

    report = summarize_runs(runs)
    output = _format_stdout(report)
    print(output)

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = _REPO_ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {out_path.resolve()}", file=sys.stderr)

    return 0 if report["gate"]["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
