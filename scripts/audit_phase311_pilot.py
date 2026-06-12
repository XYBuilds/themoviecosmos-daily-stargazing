"""audit_phase311_pilot.py · Offline firewall audit for Phase 3.11.6 pilot artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.agents import load_deconstruction_from_file
from scripts.lib.phase311_pretest import PHASE310_ROOT
from scripts.lib.phase311_pilot import (
    audit_pilot_run,
    go_no_go_pilot_recommendation,
    load_pilot_manifest,
    parse_pilot_runs,
    render_pilot_audit_markdown,
)


def _load_expansion(run_dir: Path) -> dict[str, Any] | None:
    path = run_dir / "reality-expanded.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    expansion = data.get("expansion")
    return expansion if isinstance(expansion, dict) else None


def audit_pilot_dir(
    pilot_root: Path,
    *,
    baseline_root: Path,
    run_id: str,
) -> dict[str, Any]:
    run_dir = pilot_root / run_id
    baseline_run = baseline_root / run_id
    if not run_dir.is_dir():
        raise FileNotFoundError(f"pilot run dir missing: {run_dir}")
    if not baseline_run.is_dir():
        raise FileNotFoundError(f"baseline run dir missing: {baseline_run}")

    deconstruction = load_deconstruction_from_file(
        run_dir / "reality-deconstructed.json"
    )
    expansion = _load_expansion(run_dir)
    baseline_retrieve = json.loads(
        (baseline_run / "retrieve.json").read_text(encoding="utf-8")
    )
    design_retrieve = json.loads(
        (run_dir / "retrieve.json").read_text(encoding="utf-8")
    )

    manifest = load_pilot_manifest(pilot_root / "pilot-manifest.json")
    spec = next((s for s in parse_pilot_runs(manifest) if s.run_id == run_id), None)
    gap_targets = spec.gap_a_targets if spec else []

    audit = audit_pilot_run(
        run_dir=run_dir,
        baseline_run_dir=baseline_run,
        deconstruction=deconstruction,
        expansion=expansion,
        baseline_retrieve=baseline_retrieve,
        design_retrieve=design_retrieve,
        gap_a_targets=gap_targets,
    )
    dry_run = any(
        (run_dir / "personas" / d.name / "persona-pipeline.json").is_file()
        and json.loads(
            (run_dir / "personas" / d.name / "persona-pipeline.json").read_text(
                encoding="utf-8"
            )
        ).get("composition_mode")
        == "dry-run-baseline"
        for d in (run_dir / "personas").iterdir()
        if d.is_dir()
    )
    go = go_no_go_pilot_recommendation(audit, dry_run=dry_run)
    return {"audit": audit, "go_no_go": go, "dry_run": dry_run}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Phase 3.11.6 pilot run artifacts.")
    parser.add_argument(
        "--pilot-dir",
        required=True,
        help="Pilot output root (e.g. output/Eval/phase3.11/pilot-20260611-...)",
    )
    parser.add_argument("--run-id", default="01-grid-outage")
    parser.add_argument("--baseline-dir", default=None)
    parser.add_argument(
        "--write-md",
        action="store_true",
        help="Rewrite pilot-audit.md in pilot root",
    )
    args = parser.parse_args(argv)

    pilot_root = Path(args.pilot_dir)
    if not pilot_root.is_dir():
        print(f"error: pilot dir not found: {pilot_root}", file=sys.stderr)
        return 2

    baseline_root = Path(args.baseline_dir) if args.baseline_dir else PHASE310_ROOT
    result = audit_pilot_dir(
        pilot_root,
        baseline_root=baseline_root,
        run_id=args.run_id,
    )
    print(json.dumps(result, ensure_ascii=False, indent=2))

    audit = result["audit"]
    (pilot_root / args.run_id / "audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if args.write_md:
        md = render_pilot_audit_markdown(
            audit,
            go_no_go=result["go_no_go"],
            output_dir=str(pilot_root.resolve()),
            baseline_dir=str((baseline_root / args.run_id).resolve()),
        )
        out_path = pilot_root / "pilot-audit.md"
        out_path.write_text(md, encoding="utf-8")
        print(f"Wrote {out_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
