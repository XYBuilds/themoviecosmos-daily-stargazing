"""Promote phase3.9 eval runs to phase3.10 (generation recipe unchanged).

Phase 3.10.5: same decon+expansion+persona artifacts as 3.9; writes
``output/Eval/phase3.10/{run_id}/`` without modifying phase3.9 or earlier.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.eval_batch_manifest import load_manifest
from scripts.lib.paths import repo_root

PHASE39 = repo_root() / "output" / "Eval" / "phase3.9"
PHASE310 = repo_root() / "output" / "Eval" / "phase3.10"


def promote_run(run_id: str, *, dry_run: bool = False) -> dict:
    src = PHASE39 / run_id
    dst = PHASE310 / run_id
    if not src.is_dir():
        raise FileNotFoundError(f"phase3.9 run missing: {src}")
    if not dry_run:
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        meta_path = dst / "batch-run-meta.json"
        if meta_path.is_file():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        else:
            meta = {"run_id": run_id}
        meta["promoted_from"] = "phase3.9"
        meta["eval_phase"] = "3.10"
        meta["promoted_at"] = datetime.now(UTC).isoformat()
        meta_path.write_text(
            json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    return {"run_id": run_id, "src": str(src), "dst": str(dst)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Promote phase3.9 runs to phase3.10 (zero generation-side changes)."
    )
    parser.add_argument(
        "--run-ids",
        nargs="*",
        help="Run ids (default: all 10 from batch-manifest).",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    run_ids = list(args.run_ids) if args.run_ids else load_manifest()
    results: list[dict] = []
    for run_id in run_ids:
        try:
            row = promote_run(run_id, dry_run=args.dry_run)
            results.append(row)
            print(f"ok · {run_id} → {row['dst']}")
        except Exception as exc:
            results.append({"run_id": run_id, "error": str(exc)})
            print(f"FAIL · {run_id}: {exc}", file=sys.stderr)

    if not args.dry_run:
        PHASE310.mkdir(parents=True, exist_ok=True)
        summary = {
            "eval_phase": "3.10",
            "promoted_from": "phase3.9",
            "recipe": "3.9 decon+expansion+generation (unchanged)",
            "finished_at": datetime.now(UTC).isoformat(),
            "runs": results,
        }
        (PHASE310 / "batch-run-summary.json").write_text(
            json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    failed = [r for r in results if r.get("error")]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
