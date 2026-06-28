"""run_phase38_batch.py · Phase 3.8.7 N=10 batch: A0 → expansion → 12 persona → retrieve + A1 parallel.

Writes under output/Eval/phase3.8/{run_id}/ only. Does not modify phase3.5/3.6/3.7.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.eval_batch_manifest import load_manifest
from scripts.lib.paths import repo_root
from scripts.rewrite import list_persona_ids
from scripts.run_persona_batch import (
    OBS_RUN_PREFIXES,
    phase38_run_dir,
    split_obs_holdout,
    write_a1_parallel_baseline,
)
from scripts.run_phase38_eval import run_phase38_for_news

PHASE38 = repo_root() / "output" / "Eval" / "phase3.8"


def _run_complete(run_id: str) -> bool:
    d = phase38_run_dir(run_id)
    return (
        (d / "retrieve.json").is_file()
        and (d / "retrieve-a1.json").is_file()
        and (d / "reality-deconstructed.json").is_file()
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 3.8.7 full eval batch (10 × 12 persona + A1).")
    parser.add_argument("--run-ids", nargs="*", help="Subset of manifest run_ids.")
    parser.add_argument("--obs-only", action="store_true")
    parser.add_argument("--holdout-only", action="store_true")
    parser.add_argument("--personas", nargs="*")
    parser.add_argument("--provider", choices=["mimo", "deepseek"])
    parser.add_argument("--no-skip-existing", action="store_true")
    parser.add_argument("--a1-only", action="store_true", help="Only write retrieve-a1.json for run_ids.")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    all_run_ids = load_manifest()
    obs, holdout = split_obs_holdout(all_run_ids)
    if args.obs_only and args.holdout_only:
        print("error: --obs-only and --holdout-only are mutually exclusive", file=sys.stderr)
        return 2
    if args.obs_only:
        run_ids = obs
    elif args.holdout_only:
        run_ids = holdout
    else:
        run_ids = all_run_ids
    if args.run_ids:
        run_ids = list(args.run_ids)

    persona_ids = list_persona_ids() if not args.personas else list(args.personas)

    if args.dry_run:
        print(f"runs ({len(run_ids)}): {', '.join(run_ids)}")
        print(f"personas ({len(persona_ids)}): {', '.join(persona_ids)}")
        return 0

    if args.a1_only:
        results = []
        for run_id in run_ids:
            try:
                meta = write_a1_parallel_baseline(run_id)
                results.append({"run_id": run_id, "a1_hit_count": len(meta.get("a1_hit_tmdb_ids") or [])})
            except Exception as exc:
                results.append({"run_id": run_id, "error": str(exc)})
        summary_path = PHASE38 / "batch-run-summary.json"
        summary_path.write_text(
            json.dumps(
                {"mode": "a1-only", "finished_at": datetime.now(UTC).isoformat(), "runs": results},
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        failed = [r for r in results if r.get("error")]
        return 1 if failed else 0

    # Fix: run_phase38_for_news needs news_path — import helper
    from scripts.eval_batch_manifest import news_file_for_run_id

    async def _run_all() -> list[dict]:
        out: list[dict] = []
        for run_id in run_ids:
            split = "observation" if run_id.startswith(OBS_RUN_PREFIXES) else "holdout"
            print(f"=== {run_id} ({split}) ===", file=sys.stderr)
            if not args.no_skip_existing and _run_complete(run_id):
                print("  skip (complete)", file=sys.stderr)
                out.append({"run_id": run_id, "split": split, "skipped": True})
                continue
            try:
                meta = await run_phase38_for_news(
                    run_id,
                    news_file_for_run_id(run_id),
                    persona_ids,
                    provider=args.provider,
                    skip_existing=not args.no_skip_existing,
                    skip_decon=False,
                    skip_expansion=False,
                    skip_personas=False,
                    skip_retrieve=False,
                )
                out.append(
                    {
                        "run_id": run_id,
                        "split": split,
                        "agent_count": meta.get("agent_count"),
                        "candidate_count": meta.get("candidate_count"),
                        "errors": meta.get("errors") or [],
                        "english_ok": meta.get("english_ok"),
                        "a1_parallel": (phase38_run_dir(run_id) / "retrieve-a1.json").is_file(),
                    }
                )
            except Exception as exc:
                out.append({"run_id": run_id, "split": split, "error": str(exc)})
                print(f"  FAIL: {exc}", file=sys.stderr)
        return out

    results = asyncio.run(_run_all())

    persona_failures: dict[str, int] = {}
    for row in results:
        for err in row.get("errors") or []:
            aid = str(err.get("agent_id", "unknown"))
            persona_failures[aid] = persona_failures.get(aid, 0) + 1

    summary = {
        "phase": "3.8.7",
        "finished_at": datetime.now(UTC).isoformat(),
        "run_ids_planned": run_ids,
        "persona_ids": persona_ids,
        "runs": results,
        "succeeded": [r["run_id"] for r in results if not r.get("error") and not r.get("skipped")],
        "skipped": [r["run_id"] for r in results if r.get("skipped")],
        "failed": [r["run_id"] for r in results if r.get("error")],
        "persona_failure_counts": persona_failures,
        "holdout_scoring": {
            "review_file": "output/Eval/phase3.8/high-hit-score-review.md",
            "holdout_run_ids": holdout,
            "instruction": "Fill 共振分 (0/1/2) and 共振类型 on ≥2 holdout sections (05–10).",
        },
    }
    summary_path = PHASE38 / "batch-run-summary.json"
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {summary_path}", file=sys.stderr)

    if summary["failed"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
