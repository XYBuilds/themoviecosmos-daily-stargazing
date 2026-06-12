"""run_phase311_full_batch.py · Phase 3.11.7 full-batch A/B wrapper.

Runs ADR-0009 fragment-ladder design-on across the N=10 eval corpus, then writes
search_unit_kind decomposition, review artifacts, and tuning/audit summaries.

The script only writes under the selected Phase 3.11 output directory. It reads
Phase 3.10 as the frozen baseline and never rewrites Phase 3.10 or earlier.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.eval_batch_manifest import load_manifest
from scripts.lib.phase311_pretest import PHASE310_ROOT, PHASE311_ROOT, load_gap_a_samples
from scripts.personas import list_persona_ids
from scripts.retrieve import (
    compare_pool_diff_by_search_unit_kind,
    pool_diff_by_search_unit_kind_to_dict,
)
from scripts.run_eval import _format_candidates_markdown
from scripts.run_phase311_pilot import main_async as run_phase311_design_on_async
from scripts.score_eval_candidates import _format_high_hit_review, process_eval_dir

_SEARCH_UNIT_KINDS = (
    "surface-fragment-bundle",
    "event-fragment-bundle",
    "persona-semantic",
)


def _resolve_path(path: str | Path | None, *, default: Path) -> Path:
    if path is None:
        return default
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = _REPO_ROOT / resolved
    return resolved


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _candidate_ids(payload: dict[str, Any], key: str = "candidates") -> set[int]:
    ids: set[int] = set()
    for row in payload.get(key) or []:
        if isinstance(row, dict) and row.get("tmdb_id") is not None:
            ids.add(int(row["tmdb_id"]))
    return ids


def _hit_source_kinds(candidate: dict[str, Any]) -> set[str]:
    kinds: set[str] = set()
    for source in candidate.get("hit_sources") or []:
        kind = str(source.get("search_unit_kind") or "").strip()
        if kind in _SEARCH_UNIT_KINDS:
            kinds.add(kind)
    return kinds


def _center_dimensions(candidate: dict[str, Any]) -> set[str]:
    match = candidate.get("match_diagnostics") or {}
    dims = {
        str(item).strip()
        for item in (match.get("center_dimensions") or [])
        if str(item).strip()
    }
    for source in candidate.get("hit_sources") or []:
        center = str(source.get("center_element") or "").strip()
        if "-" in center:
            dims.add(center.split("-", 1)[0])
    return dims


def _personas(candidate: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for source in candidate.get("hit_sources") or []:
        aid = str(source.get("agent_id") or "").strip()
        kind = str(source.get("search_unit_kind") or "").strip()
        if aid and kind == "persona-semantic":
            ids.add(aid)
    for aid in candidate.get("triggered_by") or []:
        if str(aid).strip():
            ids.add(str(aid).strip())
    return ids


def _load_human_two_keys(judge_json: Path | None) -> set[tuple[str, int]]:
    if judge_json is None or not judge_json.is_file():
        return set()
    data = _read_json(judge_json)
    keys: set[tuple[str, int]] = set()
    for row in data.get("scores") or []:
        if not isinstance(row, dict):
            continue
        if row.get("human_score") != 2:
            continue
        run_id = str(row.get("run_id") or "").strip()
        tmdb_id = row.get("tmdb_id")
        if run_id and tmdb_id is not None:
            keys.add((run_id, int(tmdb_id)))
    return keys


def _load_pov_transform_distribution(judge_json: Path | None) -> dict[str, Any]:
    if judge_json is None or not judge_json.is_file():
        return {
            "source": None,
            "human": {"true": 0, "false": 0, "unknown": 0},
            "judge": {"true": 0, "false": 0, "unknown": 0},
            "note": "pending human labels / judge output",
        }
    data = _read_json(judge_json)
    dist = {
        "source": str(judge_json),
        "human": Counter(),
        "judge": Counter(),
    }
    for row in data.get("scores") or []:
        for side, field in (("human", "human_pov_transform"), ("judge", "judge_pov_transform")):
            value = row.get(field)
            bucket = "unknown" if value is None else str(bool(value)).lower()
            dist[side][bucket] += 1
    return {
        "source": dist["source"],
        "human": {k: int(dist["human"].get(k, 0)) for k in ("true", "false", "unknown")},
        "judge": {k: int(dist["judge"].get(k, 0)) for k in ("true", "false", "unknown")},
    }


def build_phase3117_manifest(run_ids: list[str] | None = None) -> dict[str, Any]:
    selected = run_ids or load_manifest()
    gap_rows_by_run: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in load_gap_a_samples():
        gap_rows_by_run[str(row.get("run_id"))].append(row)
    personas = list_persona_ids()
    return {
        "version": 1,
        "description": "Phase 3.11.7 full-batch fragment-ladder design-on vs Phase 3.10 baseline",
        "baseline": "output/Eval/phase3.10",
        "run_ids": selected,
        "runs": [
            {
                "run_id": run_id,
                "note": "Phase 3.11.7 full-batch A/B run",
                "personas": personas,
                "gap_a_targets": [
                    {
                        "tmdb_id": str(row.get("tmdb_id")),
                        "title": str(row.get("title", "")).split(" (")[0],
                        "human_score": row.get("human_score"),
                        "judge_score": row.get("judge_score"),
                        "judge_resonance_type": row.get("judge_resonance_type"),
                        "rationale": row.get("rationale", ""),
                    }
                    for row in gap_rows_by_run.get(run_id, [])
                ],
            }
            for run_id in selected
        ],
    }


def write_phase3117_manifest(path: Path, run_ids: list[str] | None = None) -> dict[str, Any]:
    manifest = build_phase3117_manifest(run_ids)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return manifest


def _summarize_one_run(
    *,
    run_id: str,
    run_dir: Path,
    baseline_dir: Path,
    human_two_keys: set[tuple[str, int]],
) -> dict[str, Any]:
    baseline_run = baseline_dir / run_id
    baseline_retrieve = _read_json(baseline_run / "retrieve.json")
    design_retrieve = _read_json(run_dir / "retrieve.json")

    diff = compare_pool_diff_by_search_unit_kind(
        run_id=run_id,
        baseline_retrieve=baseline_retrieve,
        design_retrieve=design_retrieve,
    )
    diff_payload = pool_diff_by_search_unit_kind_to_dict(diff)
    (run_dir / "pool-diff-search-unit-kind.json").write_text(
        json.dumps(diff_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_dir / "candidates.md").write_text(
        _format_candidates_markdown(run_id, design_retrieve.get("candidates", [])),
        encoding="utf-8",
    )

    design_index = {
        int(row["tmdb_id"]): row
        for row in design_retrieve.get("candidates") or []
        if isinstance(row, dict) and row.get("tmdb_id") is not None
    }
    exclusive = {kind: [] for kind in _SEARCH_UNIT_KINDS}
    collision = []
    persona_counts: Counter[str] = Counter()
    center_counts: Counter[str] = Counter()
    for tmdb_id in diff.net_new_tmdb_ids:
        candidate = design_index.get(int(tmdb_id), {})
        kinds = _hit_source_kinds(candidate)
        if len(kinds) == 1:
            exclusive[next(iter(kinds))].append(int(tmdb_id))
        elif len(kinds) >= 2:
            collision.append(int(tmdb_id))
        for persona in _personas(candidate):
            persona_counts[persona] += 1
        for center_dimension in _center_dimensions(candidate):
            center_counts[center_dimension] += 1

    design_candidate_ids = _candidate_ids(design_retrieve)
    audit_pool_ids = _candidate_ids(design_retrieve, "audit_pool")
    judge_zero_ids = _candidate_ids(design_retrieve, "judge_zero")
    baseline_human_two = sorted(
        tmdb_id for rid, tmdb_id in human_two_keys if rid == run_id
    )
    killed_human_two = sorted(set(baseline_human_two) & judge_zero_ids)
    missing_human_two = sorted(set(baseline_human_two) - design_candidate_ids - audit_pool_ids)

    audit_path = run_dir / "audit.json"
    audit = _read_json(audit_path) if audit_path.is_file() else {}
    dims = audit.get("dimensions") or {}

    return {
        "run_id": run_id,
        "baseline_candidate_count": diff.baseline_candidate_count,
        "design_candidate_count": diff.design_candidate_count,
        "net_new_count": len(diff.net_new_tmdb_ids),
        "lost_count": len(diff.lost_tmdb_ids),
        "net_new_tmdb_ids": diff.net_new_tmdb_ids,
        "lost_tmdb_ids": diff.lost_tmdb_ids,
        "by_search_unit_kind": diff.by_search_unit_kind,
        "exclusive_by_search_unit_kind": exclusive,
        "collision_gain_tmdb_ids": collision,
        "persona_net_new_counts": dict(sorted(persona_counts.items())),
        "center_dimension_net_new_counts": dict(sorted(center_counts.items())),
        "funnel": design_retrieve.get("funnel") or design_retrieve.get("meta") or {},
        "audit_pool_count": len(design_retrieve.get("audit_pool") or []),
        "judge_zero_count": len(design_retrieve.get("judge_zero") or []),
        "baseline_human_two_tmdb_ids": baseline_human_two,
        "human_two_in_judge_zero_tmdb_ids": killed_human_two,
        "human_two_missing_from_design_review_tmdb_ids": missing_human_two,
        "zero_human_two_killed": not killed_human_two,
        "all_automated_pass": audit.get("all_automated_pass"),
        "guard_hard_failures": (dims.get("fact_drift") or {}).get("hard_guard_failures", 0),
    }


def summarize_phase3117_run(
    *,
    output_dir: Path,
    baseline_dir: Path = PHASE310_ROOT,
    judge_json: Path | None = None,
    run_ids: list[str] | None = None,
) -> dict[str, Any]:
    selected = run_ids or load_manifest()
    human_two_keys = _load_human_two_keys(judge_json or (baseline_dir / "llm-judge-scores.json"))
    runs = [
        _summarize_one_run(
            run_id=run_id,
            run_dir=output_dir / run_id,
            baseline_dir=baseline_dir,
            human_two_keys=human_two_keys,
        )
        for run_id in selected
    ]

    by_kind: dict[str, set[int]] = {kind: set() for kind in _SEARCH_UNIT_KINDS}
    exclusive_by_kind: dict[str, set[int]] = {kind: set() for kind in _SEARCH_UNIT_KINDS}
    collision_ids: set[int] = set()
    persona_counts: Counter[str] = Counter()
    center_counts: Counter[str] = Counter()
    total_baseline = total_design = total_net_new = total_lost = 0
    human_two_killed: list[dict[str, Any]] = []
    human_two_missing: list[dict[str, Any]] = []
    guard_hard_failures = 0
    automated_pass_count = 0

    for row in runs:
        total_baseline += int(row["baseline_candidate_count"])
        total_design += int(row["design_candidate_count"])
        total_net_new += int(row["net_new_count"])
        total_lost += int(row["lost_count"])
        guard_hard_failures += int(row.get("guard_hard_failures") or 0)
        if row.get("all_automated_pass") is True:
            automated_pass_count += 1
        for kind, ids in row["by_search_unit_kind"].items():
            by_kind.setdefault(kind, set()).update(int(i) for i in ids)
        for kind, ids in row["exclusive_by_search_unit_kind"].items():
            exclusive_by_kind.setdefault(kind, set()).update(int(i) for i in ids)
        collision_ids.update(int(i) for i in row["collision_gain_tmdb_ids"])
        persona_counts.update(row["persona_net_new_counts"])
        center_counts.update(row["center_dimension_net_new_counts"])
        if row["human_two_in_judge_zero_tmdb_ids"]:
            human_two_killed.append(
                {"run_id": row["run_id"], "tmdb_ids": row["human_two_in_judge_zero_tmdb_ids"]}
            )
        if row["human_two_missing_from_design_review_tmdb_ids"]:
            human_two_missing.append(
                {"run_id": row["run_id"], "tmdb_ids": row["human_two_missing_from_design_review_tmdb_ids"]}
            )

    budgets = [int((row.get("funnel") or {}).get("human_budget") or 0) for row in runs]
    human_counts = [int((row.get("funnel") or {}).get("human_count") or 0) for row in runs]
    summary = {
        "phase": "3.11.7",
        "output_dir": str(output_dir),
        "baseline_dir": str(baseline_dir),
        "run_count": len(runs),
        "totals": {
            "baseline_candidates": total_baseline,
            "design_candidates": total_design,
            "net_new_candidates": total_net_new,
            "lost_candidates": total_lost,
            "automated_pass_runs": automated_pass_count,
            "guard_hard_failures": guard_hard_failures,
        },
        "search_unit_kind_decomposition": {
            "any_kind_counts": {kind: len(ids) for kind, ids in sorted(by_kind.items())},
            "exclusive_counts": {kind: len(ids) for kind, ids in sorted(exclusive_by_kind.items())},
            "collision_gain_count": len(collision_ids),
            "collision_gain_tmdb_ids": sorted(collision_ids),
        },
        "tuning_compass": {
            "persona_net_new_counts": dict(sorted(persona_counts.items(), key=lambda x: (-x[1], x[0]))),
            "center_dimension_net_new_counts": dict(sorted(center_counts.items(), key=lambda x: (-x[1], x[0]))),
            "budget_N": {
                "per_run_human_budget": budgets,
                "per_run_human_count": human_counts,
                "min_human_count": min(human_counts) if human_counts else 0,
                "max_human_count": max(human_counts) if human_counts else 0,
            },
        },
        "rejection_audit": {
            "zero_human_two_killed_by_judge_zero": not human_two_killed,
            "human_two_in_judge_zero": human_two_killed,
            "human_two_missing_from_design_review": human_two_missing,
            "note": "judge_zero exists only when retrieve was run with judge_scores; missing_from_design_review is a review-pool retention warning, not final GATE裁决。",
        },
        "pov_transform_distribution": _load_pov_transform_distribution(
            output_dir / "llm-judge-scores.json"
        ),
        "runs": runs,
    }
    (output_dir / "phase3117-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def render_phase3117_report(summary: dict[str, Any]) -> str:
    totals = summary["totals"]
    decomp = summary["search_unit_kind_decomposition"]
    compass = summary["tuning_compass"]
    rejection = summary["rejection_audit"]
    pov = summary["pov_transform_distribution"]
    lines = [
        "# Phase 3.11.7 Full-batch A/B 调优记录",
        "",
        f"- **Output dir**: `{summary['output_dir']}`",
        f"- **Baseline dir**: `{summary['baseline_dir']}`",
        f"- **Runs**: {summary['run_count']}",
        "",
        "## 1. A/B 池差总览",
        "",
        f"- baseline candidates: {totals['baseline_candidates']}",
        f"- design candidates: {totals['design_candidates']}",
        f"- net-new candidates: {totals['net_new_candidates']}",
        f"- lost candidates: {totals['lost_candidates']}",
        f"- automated pass runs: {totals['automated_pass_runs']} / {summary['run_count']}",
        f"- guard hard failures: {totals['guard_hard_failures']}",
        "",
        "## 2. search_unit_kind 分解",
        "",
        f"- any-kind counts: `{decomp['any_kind_counts']}`",
        f"- exclusive counts: `{decomp['exclusive_counts']}`",
        f"- collision gain count: {decomp['collision_gain_count']}",
        f"- collision gain tmdb_ids: `{decomp['collision_gain_tmdb_ids']}`",
        "",
        "## 3. 调优指南针",
        "",
        f"- persona net-new counts: `{compass['persona_net_new_counts']}`",
        f"- center dimension net-new counts: `{compass['center_dimension_net_new_counts']}`",
        f"- budget N: `{compass['budget_N']}`",
        "",
        "## 4. POV变换 分布",
        "",
        f"- human: `{pov.get('human')}`",
        f"- judge: `{pov.get('judge')}`",
        f"- source: `{pov.get('source')}`",
        "",
        "## 5. 拒绝集 / human-2 监控",
        "",
        f"- zero human-2 killed by judge_zero: {rejection['zero_human_two_killed_by_judge_zero']}",
        f"- human-2 in judge_zero: `{rejection['human_two_in_judge_zero']}`",
        f"- human-2 missing from design review: `{rejection['human_two_missing_from_design_review']}`",
        f"- note: {rejection['note']}",
        "",
        "## 6. 人工抽审入口",
        "",
        "- `high-hit-score-review.md`：统一候选抽审表，含 `POV变换` 人工字段。",
        "- 每个 run 的 `pool-diff-search-unit-kind.json`：池差分解原始数据。",
        "- 每个 run 的 `audit.json`：自动守卫与 pipeline 审计。",
        "",
    ]
    return "\n".join(lines)


def write_review_artifacts(output_dir: Path, *, min_score: int) -> None:
    run_reviews, all_high, missing, runs_scanned = process_eval_dir(
        output_dir,
        write_candidates=True,
        min_total_score=min_score,
    )
    review_text = _format_high_hit_review(
        run_reviews,
        runs_scanned=runs_scanned,
        min_score=min_score,
    )
    (output_dir / "high-hit-score-review.md").write_text(review_text, encoding="utf-8")
    review_meta = {
        "runs_scanned": runs_scanned,
        "min_score": min_score,
        "high_hit_candidate_count": len(all_high),
        "missing_retrieve": missing,
    }
    (output_dir / "high-hit-score-review.json").write_text(
        json.dumps(review_meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


async def main_async(args: argparse.Namespace) -> int:
    run_ids = args.run_id or load_manifest()
    ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    output_dir = _resolve_path(
        args.output_dir,
        default=PHASE311_ROOT / f"full-batch-{ts}",
    )
    baseline_dir = _resolve_path(args.baseline_dir, default=PHASE310_ROOT)
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "phase3117-manifest.json"
    manifest = write_phase3117_manifest(manifest_path, run_ids)
    (output_dir / "pilot-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if not args.summarize_only:
        design_args = argparse.Namespace(
            dry_run=bool(args.dry_run),
            skip_retrieval=bool(args.skip_retrieval),
            provider=args.provider,
            baseline_dir=str(baseline_dir),
            output_dir=str(output_dir),
            manifest=str(manifest_path),
            run_id=run_ids,
            concurrency=int(args.concurrency),
        )
        code = await run_phase311_design_on_async(design_args)
        if code != 0:
            return int(code)

    write_review_artifacts(output_dir, min_score=int(args.min_score))
    summary = summarize_phase3117_run(
        output_dir=output_dir,
        baseline_dir=baseline_dir,
        judge_json=(baseline_dir / "llm-judge-scores.json"),
        run_ids=run_ids,
    )
    report = render_phase3117_report(summary)
    (output_dir / "phase3117-tuning-report.md").write_text(report, encoding="utf-8")
    (output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    pilot_audit = output_dir / "pilot-audit.md"
    if pilot_audit.is_file():
        pilot_audit.unlink()
    print(
        json.dumps(
            {
                "output_dir": str(output_dir),
                "runs": len(run_ids),
                "net_new": summary["totals"]["net_new_candidates"],
                "guard_hard_failures": summary["totals"]["guard_hard_failures"],
                "review": str(output_dir / "high-hit-score-review.md"),
                "summary": str(output_dir / "phase3117-summary.json"),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Phase 3.11.7 full-batch A/B runner")
    parser.add_argument("--provider", default=None, help="LLM provider override")
    parser.add_argument("--baseline-dir", default=None, help="Frozen Phase 3.10 eval root")
    parser.add_argument("--output-dir", default=None, help="Phase 3.11 full-batch output root")
    parser.add_argument("--run-id", action="append", help="Limit to run_id; repeatable")
    parser.add_argument("--concurrency", type=int, default=3)
    parser.add_argument("--min-score", type=int, default=5, help="High-hit review pseudo score cutoff")
    parser.add_argument("--dry-run", action="store_true", help="Reuse 3.10 pipelines; CI/scaffold only")
    parser.add_argument("--skip-retrieval", action="store_true")
    parser.add_argument("--summarize-only", action="store_true", help="Only summarize an existing output dir")
    return parser


def main() -> None:
    raise SystemExit(asyncio.run(main_async(build_parser().parse_args())))


if __name__ == "__main__":
    main()