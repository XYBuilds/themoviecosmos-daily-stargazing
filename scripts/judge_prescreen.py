"""Judge prescreen orchestration (Phase 3.10.4 · ADR-0007 D4).

Full judge scoring with **no physical deletion**; workflow bucketing:
``judge=0`` downgrade / ``judge≥1`` manual review / ``judge=2`` highlight.

Rejection-set audit: each run randomly samples *k*% of the ``judge=0`` pile into a
blind human-review pool. Threshold discipline scaffold: parameterized
``min_judge_score`` (default ``≥1``), adjustable until frozen on observation set.
"""

from __future__ import annotations

import argparse
import json
import random
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.llm_judge import JudgeOutput, JudgeResult, load_judge_output

_PRESCREEN_SCHEMA_VERSION = 1

BUCKET_DOWNGRADE = "downgrade"
BUCKET_MANUAL = "manual"
BUCKET_HIGHLIGHT = "highlight"

DEFAULT_MIN_JUDGE_SCORE = 1
DEFAULT_REJECTION_SAMPLE_RATE = 0.10
DEFAULT_RANDOM_SEED = 42


@dataclass(frozen=True)
class PrescreenConfig:
    """Threshold and rejection-audit knobs (freeze after obs verification)."""

    min_judge_score: int = DEFAULT_MIN_JUDGE_SCORE
    rejection_sample_rate: float = DEFAULT_REJECTION_SAMPLE_RATE
    random_seed: int = DEFAULT_RANDOM_SEED
    threshold_frozen: bool = False

    def __post_init__(self) -> None:
        if self.min_judge_score not in (0, 1, 2):
            raise ValueError("min_judge_score must be 0, 1, or 2")
        if not 0.0 < self.rejection_sample_rate <= 1.0:
            raise ValueError("rejection_sample_rate must be in (0, 1]")


@dataclass
class PrescreenItem:
    run_id: str
    tmdb_id: str
    title: str
    judge_score: int
    bucket: str
    passes_threshold: bool
    manual_review: bool
    highlight: bool
    rejection_audit_sampled: bool = False
    human_score: int | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class RejectionAuditRecord:
    """Sampling manifest for one run's ``judge=0`` pile."""

    run_id: str
    rejection_count: int
    sample_rate: float
    sample_size: int
    random_seed: int
    sampled_keys: list[tuple[str, str]]
    audit_hits: list[dict[str, Any]] = field(default_factory=list)
    reweight_factor: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "rejection_count": self.rejection_count,
            "sample_rate": self.sample_rate,
            "sample_size": self.sample_size,
            "random_seed": self.random_seed,
            "sampled": [
                {"run_id": rid, "tmdb_id": tid} for rid, tid in self.sampled_keys
            ],
            "audit_hits": self.audit_hits,
            "reweight_factor": self.reweight_factor,
        }


@dataclass
class ThresholdSafetyReport:
    """Zero human-2-killed verification slot (obs freeze gate)."""

    min_judge_score: int
    threshold_frozen: bool
    n_scored: int
    n_human_labeled: int
    n_human_two: int
    n_human_two_on_pass_side: int
    n_human_two_killed: int
    zero_human_two_killed: bool
    killed_items: list[dict[str, Any]] = field(default_factory=list)
    pass_side_human_two_retention: float | None = None
    workload_reduction_rate: float | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class PrescreenReport:
    version: int
    config: PrescreenConfig
    items: list[PrescreenItem]
    bucket_counts: dict[str, int]
    rejection_audits: list[RejectionAuditRecord]
    threshold_safety: ThresholdSafetyReport
    judge_trusted: bool
    judge_trust_status: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "version": self.version,
            "config": asdict(self.config),
            "bucket_counts": self.bucket_counts,
            "items": [i.to_dict() for i in self.items],
            "rejection_audits": [a.to_dict() for a in self.rejection_audits],
            "threshold_safety": self.threshold_safety.to_dict(),
            "judge_trusted": self.judge_trusted,
            "judge_trust_status": self.judge_trust_status,
        }


def classify_prescreen_bucket(judge_score: int) -> str:
    """Map judge score to workflow bucket (ADR-0007 D4)."""
    if judge_score <= 0:
        return BUCKET_DOWNGRADE
    if judge_score >= 2:
        return BUCKET_HIGHLIGHT
    return BUCKET_MANUAL


def item_passes_threshold(judge_score: int, min_judge_score: int) -> bool:
    return judge_score >= min_judge_score


def sample_rejection_audit_keys(
    keys: list[tuple[str, str]],
    sample_rate: float,
    seed: int,
) -> list[tuple[str, str]]:
    """Reproducibly sample *k*% of rejection-pile keys (per-run or global)."""
    if not keys:
        return []
    if sample_rate >= 1.0:
        return list(keys)
    rng = random.Random(seed)
    ordered = sorted(keys)
    n_sample = max(1, round(len(ordered) * sample_rate))
    n_sample = min(n_sample, len(ordered))
    return rng.sample(ordered, n_sample)


def _reweight_factor(sample_rate: float, sample_size: int, rejection_count: int) -> float:
    """Inverse sampling rate for honest bucket denominators (ADR-0007 D4)."""
    if sample_size <= 0 or rejection_count <= 0:
        return 1.0
    return rejection_count / sample_size


def _build_prescreen_item(
    result: JudgeResult,
    *,
    min_judge_score: int,
    audit_sampled: bool,
) -> PrescreenItem:
    bucket = classify_prescreen_bucket(result.judge_score)
    passes = item_passes_threshold(result.judge_score, min_judge_score)
    return PrescreenItem(
        run_id=result.run_id,
        tmdb_id=str(result.tmdb_id),
        title=result.title,
        judge_score=result.judge_score,
        bucket=bucket,
        passes_threshold=passes,
        manual_review=passes,
        highlight=bucket == BUCKET_HIGHLIGHT,
        rejection_audit_sampled=audit_sampled and result.judge_score == 0,
        human_score=result.human_score,
    )


def compute_threshold_safety(
    scores: list[JudgeResult],
    config: PrescreenConfig,
) -> ThresholdSafetyReport:
    """Verify no human=2 sits on the reject side of ``min_judge_score``."""
    labeled = [s for s in scores if s.human_score is not None]
    human_twos = [s for s in labeled if s.human_score == 2]
    killed = [
        s for s in human_twos if s.judge_score < config.min_judge_score
    ]
    on_pass = [s for s in human_twos if s.judge_score >= config.min_judge_score]
    retention: float | None = None
    if human_twos:
        retention = len(on_pass) / len(human_twos)
    workload: float | None = None
    if labeled:
        n_pass = sum(
            1 for s in labeled if s.judge_score >= config.min_judge_score
        )
        workload = 1.0 - (n_pass / len(labeled))
    return ThresholdSafetyReport(
        min_judge_score=config.min_judge_score,
        threshold_frozen=config.threshold_frozen,
        n_scored=len(scores),
        n_human_labeled=len(labeled),
        n_human_two=len(human_twos),
        n_human_two_on_pass_side=len(on_pass),
        n_human_two_killed=len(killed),
        zero_human_two_killed=len(killed) == 0,
        killed_items=[
            {
                "run_id": s.run_id,
                "tmdb_id": str(s.tmdb_id),
                "title": s.title,
                "judge_score": s.judge_score,
                "human_score": s.human_score,
            }
            for s in killed
        ],
        pass_side_human_two_retention=retention,
        workload_reduction_rate=workload,
    )


def run_prescreen(
    judge_output: JudgeOutput,
    config: PrescreenConfig | None = None,
) -> PrescreenReport:
    """Orchestrate bucketing + per-run rejection audit + threshold safety."""
    cfg = config or PrescreenConfig()
    by_run: dict[str, list[JudgeResult]] = {}
    for row in judge_output.scores:
        by_run.setdefault(row.run_id, []).append(row)

    sampled_global: set[tuple[str, str]] = set()
    audits: list[RejectionAuditRecord] = []

    for run_id in sorted(by_run):
        rejection = [
            (r.run_id, str(r.tmdb_id))
            for r in by_run[run_id]
            if r.judge_score == 0
        ]
        sampled = sample_rejection_audit_keys(
            rejection,
            cfg.rejection_sample_rate,
            cfg.random_seed + hash(run_id) % 10_000,
        )
        sampled_global.update(sampled)
        hits: list[dict[str, Any]] = []
        by_key = {(r.run_id, str(r.tmdb_id)): r for r in by_run[run_id]}
        for key in sampled:
            row = by_key.get(key)
            if row is not None and row.human_score == 2:
                hits.append(
                    {
                        "run_id": row.run_id,
                        "tmdb_id": str(row.tmdb_id),
                        "title": row.title,
                        "judge_score": row.judge_score,
                        "human_score": row.human_score,
                    }
                )
        audits.append(
            RejectionAuditRecord(
                run_id=run_id,
                rejection_count=len(rejection),
                sample_rate=cfg.rejection_sample_rate,
                sample_size=len(sampled),
                random_seed=cfg.random_seed + hash(run_id) % 10_000,
                sampled_keys=sampled,
                audit_hits=hits,
                reweight_factor=_reweight_factor(
                    cfg.rejection_sample_rate, len(sampled), len(rejection)
                ),
            )
        )

    items = [
        _build_prescreen_item(
            row,
            min_judge_score=cfg.min_judge_score,
            audit_sampled=(row.run_id, str(row.tmdb_id)) in sampled_global,
        )
        for row in judge_output.scores
    ]
    bucket_counts: dict[str, int] = {
        BUCKET_DOWNGRADE: 0,
        BUCKET_MANUAL: 0,
        BUCKET_HIGHLIGHT: 0,
    }
    for item in items:
        bucket_counts[item.bucket] = bucket_counts.get(item.bucket, 0) + 1

    safety = compute_threshold_safety(judge_output.scores, cfg)
    cal = judge_output.calibration
    return PrescreenReport(
        version=_PRESCREEN_SCHEMA_VERSION,
        config=cfg,
        items=items,
        bucket_counts=bucket_counts,
        rejection_audits=audits,
        threshold_safety=safety,
        judge_trusted=cal.trusted,
        judge_trust_status=cal.trust_status,
    )


def write_prescreen_json(path: Path, report: PrescreenReport) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_prescreen_markdown(path: Path, report: PrescreenReport) -> None:
    lines = [
        "# Judge Prescreen Report",
        "",
        f"- **min_judge_score**: {report.config.min_judge_score} "
        f"({'frozen' if report.config.threshold_frozen else 'adjustable'})",
        f"- **rejection_sample_rate**: {report.config.rejection_sample_rate:.0%}",
        f"- **random_seed**: {report.config.random_seed}",
        f"- **judge_trust_status**: {report.judge_trust_status}",
        f"- **total_scored**: {len(report.items)} (no physical deletion)",
        "",
        "## Buckets",
        "",
        f"- **downgrade** (judge=0): {report.bucket_counts.get(BUCKET_DOWNGRADE, 0)}",
        f"- **manual** (judge=1): {report.bucket_counts.get(BUCKET_MANUAL, 0)}",
        f"- **highlight** (judge=2): {report.bucket_counts.get(BUCKET_HIGHLIGHT, 0)}",
        f"- **pass threshold** (judge≥{report.config.min_judge_score}): "
        f"{sum(1 for i in report.items if i.passes_threshold)}",
        "",
        "## Rejection-set audit (per run)",
        "",
    ]
    for audit in report.rejection_audits:
        hit_note = (
            f" · **{len(audit.audit_hits)} human=2 hit(s)**"
            if audit.audit_hits
            else ""
        )
        lines.append(
            f"- **{audit.run_id}**: {audit.sample_size}/{audit.rejection_count} "
            f"sampled @ {audit.sample_rate:.0%} "
            f"(reweight×{audit.reweight_factor:.2f}){hit_note}"
        )
    lines.extend(["", "## Threshold safety (verification slot)", ""])
    ts = report.threshold_safety
    status = "PASS" if ts.zero_human_two_killed else "FAIL"
    lines.append(f"- **zero human-2 killed**: {status} ({ts.n_human_two_killed} killed)")
    if ts.pass_side_human_two_retention is not None:
        lines.append(
            f"- **human=2 retention on pass side**: "
            f"{ts.pass_side_human_two_retention:.1%} "
            f"({ts.n_human_two_on_pass_side}/{ts.n_human_two})"
        )
    if ts.workload_reduction_rate is not None:
        lines.append(
            f"- **simulated workload reduction**: {ts.workload_reduction_rate:.1%}"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def write_threshold_safety_report(path: Path, report: PrescreenReport) -> None:
    """Dedicated obs-freeze gate report (3.10.6 slot)."""
    ts = report.threshold_safety
    cfg = report.config
    lines = [
        "# Threshold Safety Verification",
        "",
        "> ADR-0007 D4: ``min_judge_score`` must show zero human=2 killed on "
        "observation set before freeze.",
        "",
        "## Configuration",
        "",
        f"| Field | Value |",
        f"| --- | --- |",
        f"| min_judge_score | {cfg.min_judge_score} |",
        f"| threshold_frozen | {cfg.threshold_frozen} |",
        f"| rejection_sample_rate | {cfg.rejection_sample_rate:.0%} |",
        "",
        "## Verification",
        "",
        f"| Metric | Value |",
        f"| --- | --- |",
        f"| n_scored | {ts.n_scored} |",
        f"| n_human_labeled | {ts.n_human_labeled} |",
        f"| n_human_two | {ts.n_human_two} |",
        f"| n_human_two_on_pass_side | {ts.n_human_two_on_pass_side} |",
        f"| n_human_two_killed | {ts.n_human_two_killed} |",
        f"| zero_human_two_killed | **{'YES' if ts.zero_human_two_killed else 'NO'}** |",
    ]
    if ts.pass_side_human_two_retention is not None:
        lines.append(
            f"| pass_side_human_two_retention | "
            f"{ts.pass_side_human_two_retention:.1%} |"
        )
    if ts.workload_reduction_rate is not None:
        lines.append(
            f"| workload_reduction_rate | {ts.workload_reduction_rate:.1%} |"
        )
    lines.append("")
    if ts.killed_items:
        lines.extend(["## Killed human=2 items", ""])
        for row in ts.killed_items:
            lines.append(
                f"- {row['run_id']} / {row['tmdb_id']}: "
                f"judge={row['judge_score']} human={row['human_score']} — {row['title']}"
            )
        lines.append("")
    audit_hits = [
        hit
        for audit in report.rejection_audits
        for hit in audit.audit_hits
    ]
    if audit_hits:
        lines.extend(["## Rejection-audit human=2 hits", ""])
        for hit in audit_hits:
            lines.append(
                f"- {hit['run_id']} / {hit['tmdb_id']}: "
                f"judge={hit['judge_score']} human={hit['human_score']} — {hit['title']}"
            )
        lines.append("")
    verdict = "SAFE TO FREEZE" if ts.zero_human_two_killed and not audit_hits else "UNSAFE — relax threshold or fix rubric"
    lines.append(f"## Verdict: {verdict}")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8", newline="\n")


_PRESCREEN_LINE = re.compile(r"^-\s*\*\*Judge Prescreen\*\*:.*$", re.MULTILINE)
_TMDB_LINE = re.compile(r"^-\s*\*\*tmdb_id\*\*:\s*(\S+)", re.MULTILINE)
_RUN_ID_COMMENT = re.compile(r"^<!-- run_id: (\S+) -->$", re.MULTILINE)


def _prescreen_status(item: PrescreenItem) -> str:
    sampled = " · rejection-audit-sampled" if item.rejection_audit_sampled else ""
    return (
        f"- **Judge Prescreen**: {item.bucket} "
        f"(judge={item.judge_score}, pass_threshold={str(item.passes_threshold).lower()})"
        f"{sampled}"
    )


def _strip_existing_prescreen_line(block: str) -> str:
    return _PRESCREEN_LINE.sub("", block).rstrip() + "\n"


def _insert_prescreen_line(block: str, line: str) -> str:
    marker = "- **LLM Judge（自动评审）**:"
    if marker in block:
        return block.replace(marker, f"{line}\n{marker}", 1)
    return block.rstrip() + "\n" + line + "\n"


def integrate_prescreen_into_review(review_text: str, report: PrescreenReport) -> str:
    """Merge prescreen bucket annotations into a unified review markdown."""
    by_key = {(item.run_id, str(item.tmdb_id)): item for item in report.items}
    chunks = re.split(r"(?=<!-- run_id: )", review_text)
    if len(chunks) <= 1:
        return review_text

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
            item = by_key.get((run_id, tmdb_match.group(1))) if tmdb_match and run_id else None
            if item is not None:
                part = _strip_existing_prescreen_line(part)
                part = _insert_prescreen_line(part, _prescreen_status(item))
            if part and not part.endswith("\n\n"):
                part = part.rstrip() + "\n\n"
            patched_chunk += part
        out_parts.append(patched_chunk)
    merged = "".join(out_parts)
    return merged if merged.endswith("\n") else merged + "\n"


def load_prescreen_report(path: Path) -> PrescreenReport:
    data = json.loads(path.read_text(encoding="utf-8"))
    cfg_raw = data.get("config") or {}
    config = PrescreenConfig(
        min_judge_score=int(cfg_raw.get("min_judge_score", DEFAULT_MIN_JUDGE_SCORE)),
        rejection_sample_rate=float(
            cfg_raw.get("rejection_sample_rate", DEFAULT_REJECTION_SAMPLE_RATE)
        ),
        random_seed=int(cfg_raw.get("random_seed", DEFAULT_RANDOM_SEED)),
        threshold_frozen=bool(cfg_raw.get("threshold_frozen", False)),
    )
    items = [
        PrescreenItem(**{k: v for k, v in row.items() if k in PrescreenItem.__dataclass_fields__})
        for row in data.get("items") or []
    ]
    audits = []
    for raw in data.get("rejection_audits") or []:
        sampled = [
            (s["run_id"], s["tmdb_id"]) for s in raw.get("sampled") or []
        ]
        audits.append(
            RejectionAuditRecord(
                run_id=str(raw["run_id"]),
                rejection_count=int(raw["rejection_count"]),
                sample_rate=float(raw["sample_rate"]),
                sample_size=int(raw["sample_size"]),
                random_seed=int(raw["random_seed"]),
                sampled_keys=sampled,
                audit_hits=list(raw.get("audit_hits") or []),
                reweight_factor=float(raw.get("reweight_factor", 1.0)),
            )
        )
    ts_raw = data.get("threshold_safety") or {}
    threshold_safety = ThresholdSafetyReport(
        **{
            k: v
            for k, v in ts_raw.items()
            if k in ThresholdSafetyReport.__dataclass_fields__
        }
    )
    return PrescreenReport(
        version=int(data.get("version") or _PRESCREEN_SCHEMA_VERSION),
        config=config,
        items=items,
        bucket_counts=dict(data.get("bucket_counts") or {}),
        rejection_audits=audits,
        threshold_safety=threshold_safety,
        judge_trusted=bool(data.get("judge_trusted")),
        judge_trust_status=str(data.get("judge_trust_status") or ""),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--judge-json",
        type=Path,
        required=True,
        help="Input llm-judge-scores.json (full scoring, no deletion)",
    )
    parser.add_argument(
        "--eval-dir",
        type=Path,
        default=None,
        help="Eval directory for default output paths",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=None,
        help="Default: <eval-dir>/judge-prescreen.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=None,
        help="Default: <eval-dir>/judge-prescreen.md",
    )
    parser.add_argument(
        "--safety-report",
        type=Path,
        default=None,
        help="Default: <eval-dir>/threshold-safety-report.md",
    )
    parser.add_argument(
        "--min-judge-score",
        type=int,
        default=DEFAULT_MIN_JUDGE_SCORE,
        choices=(0, 1, 2),
    )
    parser.add_argument(
        "--rejection-sample-rate",
        type=float,
        default=DEFAULT_REJECTION_SAMPLE_RATE,
    )
    parser.add_argument("--random-seed", type=int, default=DEFAULT_RANDOM_SEED)
    parser.add_argument(
        "--threshold-frozen",
        action="store_true",
        help="Mark threshold as frozen (post obs verification)",
    )
    args = parser.parse_args(argv)

    judge_path = args.judge_json
    if not judge_path.is_absolute():
        judge_path = _REPO_ROOT / judge_path
    if not judge_path.is_file():
        print(f"judge JSON not found: {judge_path}", file=sys.stderr)
        return 1

    eval_dir = args.eval_dir
    if eval_dir is None:
        eval_dir = judge_path.parent
    elif not eval_dir.is_absolute():
        eval_dir = _REPO_ROOT / eval_dir

    config = PrescreenConfig(
        min_judge_score=args.min_judge_score,
        rejection_sample_rate=args.rejection_sample_rate,
        random_seed=args.random_seed,
        threshold_frozen=args.threshold_frozen,
    )
    report = run_prescreen(load_judge_output(judge_path), config)

    out_json = args.out_json or (eval_dir / "judge-prescreen.json")
    out_md = args.out_md or (eval_dir / "judge-prescreen.md")
    safety = args.safety_report or (eval_dir / "threshold-safety-report.md")
    for p in (out_json, out_md, safety):
        if not p.is_absolute():
            p = _REPO_ROOT / p

    write_prescreen_json(out_json, report)
    write_prescreen_markdown(out_md, report)
    write_threshold_safety_report(safety, report)

    ts = report.threshold_safety
    print(
        f"buckets downgrade={report.bucket_counts.get(BUCKET_DOWNGRADE, 0)} "
        f"manual={report.bucket_counts.get(BUCKET_MANUAL, 0)} "
        f"highlight={report.bucket_counts.get(BUCKET_HIGHLIGHT, 0)}"
    )
    print(
        f"threshold≥{config.min_judge_score} "
        f"human2_killed={ts.n_human_two_killed} "
        f"zero_killed={ts.zero_human_two_killed}"
    )
    print(f"wrote {out_json}")
    print(f"wrote {out_md}")
    print(f"wrote {safety}")
    return 0 if ts.zero_human_two_killed else 1


if __name__ == "__main__":
    raise SystemExit(main())
