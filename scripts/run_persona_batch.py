"""run_persona_batch.py · Phase 3.7 N=10 batch: 12 personas × news + A1 baseline per run.

Reads neutral decon from output/Eval/phase3.6/{run_id}/ (read-only). Writes under
output/Eval/phase3.7/{run_id}/ with per-persona subdirs and merged retrieve.json.
Editor scoring uses output/Eval/phase3.7/high-hit-score-review.md (from score_eval_candidates).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.agents import PseudoSegment, pseudo_to_dict
from scripts.eval_batch_manifest import load_manifest
from scripts.lib.paths import repo_root
from scripts.personas import (
    build_alt_pool_overlay,
    list_persona_ids,
    pipeline_result_to_dict,
    run_persona_pipeline,
)
from scripts.retrieve import retrieve_from_agents
from scripts.run_eval import load_deconstruction_from_file

PHASE36 = repo_root() / "output" / "Eval" / "phase3.6"
PHASE37 = repo_root() / "output" / "Eval" / "phase3.7"
OBS_RUN_PREFIXES = ("01-", "02-", "03-", "04-")


def split_obs_holdout(run_ids: list[str]) -> tuple[list[str], list[str]]:
    obs = [r for r in run_ids if r.startswith(OBS_RUN_PREFIXES)]
    holdout = [r for r in run_ids if r not in obs]
    return obs, holdout


def phase36_run_dir(run_id: str) -> Path:
    return PHASE36 / run_id


def phase37_run_dir(run_id: str) -> Path:
    return PHASE37 / run_id


def persona_artifact_dir(run_dir: Path, persona_id: str) -> Path:
    return run_dir / "personas" / persona_id


def _copy_phase36_static(run_id: str, out_dir: Path) -> None:
    """Copy read-only news/decon snapshots from phase3.6 (does not modify phase3.6)."""
    src = phase36_run_dir(run_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in (
        "reality.json",
        "reality.md",
        "reality-deconstructed.json",
        "reality-deconstructed.md",
    ):
        src_file = src / name
        if src_file.is_file():
            shutil.copy2(src_file, out_dir / name)


def load_a1_agent_from_phase36(run_id: str) -> dict[str, Any]:
    """Build agents[] row for A1 from phase3.6 retrieve (read-only)."""
    path = phase36_run_dir(run_id) / "retrieve.json"
    if not path.is_file():
        raise FileNotFoundError(f"phase3.6 retrieve missing: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    for entry in data.get("per_agent") or []:
        if str(entry.get("agent_id", "")).upper() != "A1":
            continue
        pseudos: list[dict[str, Any]] = []
        for row in entry.get("pseudos") or []:
            if not isinstance(row, dict):
                continue
            pseudo_id = str(row.get("pseudo_id") or row.get("id") or "").strip()
            text = str(row.get("pseudo") or row.get("text") or "").strip()
            source = row.get("source") if isinstance(row.get("source"), dict) else {}
            if not text or not pseudo_id:
                continue
            pseudos.append(
                {
                    "id": pseudo_id,
                    "text": text,
                    "source": source,
                }
            )
        if not pseudos:
            raise ValueError(f"A1 entry in {path} has no pseudos")
        return {
            "agent_id": "A1",
            "persona_name": "The Reality Recorder (Baseline)",
            "role": "baseline",
            "pseudos": pseudos,
            "text": pseudos[0]["text"],
            "warnings": [],
        }
    raise ValueError(f"A1 not found in {path}")


def persona_pipeline_to_agent(persona_id: str, pseudos: list) -> dict[str, Any]:
    return {
        "agent_id": persona_id,
        "persona_name": persona_id,
        "role": "creative",
        "pseudos": [pseudo_to_dict(p) for p in pseudos],
        "text": pseudos[0].text if pseudos else "",
        "warnings": [],
    }


def _fit_by_agent_pseudo(agents: list[dict[str, Any]]) -> dict[tuple[str, str], float]:
    lookup: dict[tuple[str, str], float] = {}
    for agent in agents:
        aid = str(agent.get("agent_id", "")).upper()
        for row in agent.get("pseudos") or []:
            if not isinstance(row, dict):
                continue
            pid = str(row.get("id") or row.get("pseudo_id") or "").strip()
            fit = row.get("fit")
            if aid and pid and isinstance(fit, (int, float)):
                lookup[(aid, pid)] = float(fit)
    return lookup


def _attach_fit_to_hit_sources(
    retrieve_result: dict[str, Any],
    fit_lookup: dict[tuple[str, str], float],
) -> None:
    for cand in retrieve_result.get("candidates") or []:
        for src in cand.get("hit_sources") or []:
            key = (
                str(src.get("agent_id", "")).upper(),
                str(src.get("pseudo_id", "")),
            )
            if key in fit_lookup:
                src["fit"] = fit_lookup[key]


def _persona_done(persona_dir: Path) -> bool:
    pipeline_path = persona_dir / "persona-pipeline.json"
    if not pipeline_path.is_file():
        return False
    try:
        data = json.loads(pipeline_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    if data.get("error"):
        return False
    return bool(data.get("pseudos"))


async def run_persona_for_news(
    persona_id: str,
    decon_path: Path,
    persona_dir: Path,
    *,
    provider: str | None,
    skip_existing: bool,
) -> tuple[dict[str, Any] | None, str | None]:
    persona_dir.mkdir(parents=True, exist_ok=True)
    legacy_pipeline = persona_dir.parent.parent / "persona-pipeline.json"
    if (
        skip_existing
        and persona_id == "The-Ruler"
        and not (persona_dir / "persona-pipeline.json").is_file()
        and legacy_pipeline.is_file()
    ):
        shutil.copy2(legacy_pipeline, persona_dir / "persona-pipeline.json")
        for name in ("alt-pool-overlay.json",):
            legacy = persona_dir.parent.parent / name
            if legacy.is_file():
                shutil.copy2(legacy, persona_dir / name)
    if skip_existing and _persona_done(persona_dir):
        data = json.loads((persona_dir / "persona-pipeline.json").read_text(encoding="utf-8"))
        if data.get("error"):
            return None, str(data["error"])
        pseudos_raw = data.get("pseudos") or []
        pseudos = [
            PseudoSegment(
                id=str(p["id"]),
                text=str(p["text"]),
                source=p.get("source") or {},
                warnings=list(p.get("warnings") or []),
                fit=p.get("fit"),
            )
            for p in pseudos_raw
            if isinstance(p, dict)
        ]
        return persona_pipeline_to_agent(persona_id, pseudos), None

    deconstruction = load_deconstruction_from_file(decon_path)
    result = await run_persona_pipeline(
        persona_id,
        deconstruction,
        provider=provider,
    )
    overlay_dict = build_alt_pool_overlay(result.overlay)
    (persona_dir / "alt-pool-overlay.json").write_text(
        json.dumps(overlay_dict, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (persona_dir / "persona-pipeline.json").write_text(
        json.dumps(pipeline_result_to_dict(result), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if result.error or not result.pseudos:
        return None, result.error or "no pseudos"
    return persona_pipeline_to_agent(persona_id, result.pseudos), None


async def finalize_run(
    run_id: str,
    agents: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    *,
    split: str,
) -> dict[str, Any]:
    out_dir = phase37_run_dir(run_id)
    retrieve_result = retrieve_from_agents(agents, errors)
    fit_lookup = _fit_by_agent_pseudo(agents)
    _attach_fit_to_hit_sources(retrieve_result, fit_lookup)

    (out_dir / "agents.json").write_text(
        json.dumps({"agents": agents, "errors": errors}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    (out_dir / "retrieve.json").write_text(
        json.dumps(retrieve_result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    meta = {
        "run_id": run_id,
        "split": split,
        "persona_count": sum(1 for a in agents if a.get("role") != "baseline"),
        "errors": errors,
        "retrieve_meta": retrieve_result.get("meta") or {},
        "finished_at": datetime.now(UTC).isoformat(),
    }
    (out_dir / "batch-run-meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return retrieve_result


async def run_batch_for_news(
    run_id: str,
    persona_ids: list[str],
    *,
    provider: str | None,
    skip_existing: bool,
    skip_finalize: bool,
) -> dict[str, Any]:
    decon_path = phase36_run_dir(run_id) / "reality-deconstructed.json"
    if not decon_path.is_file():
        raise FileNotFoundError(f"neutral decon missing: {decon_path}")

    out_dir = phase37_run_dir(run_id)
    _copy_phase36_static(run_id, out_dir)
    split = "observation" if run_id.startswith(OBS_RUN_PREFIXES) else "holdout"

    agents: list[dict[str, Any]] = [load_a1_agent_from_phase36(run_id)]
    errors: list[dict[str, Any]] = []

    for persona_id in persona_ids:
        persona_dir = persona_artifact_dir(out_dir, persona_id)
        agent_row, err = await run_persona_for_news(
            persona_id,
            decon_path,
            persona_dir,
            provider=provider,
            skip_existing=skip_existing,
        )
        if err or agent_row is None:
            errors.append({"agent_id": persona_id, "message": err or "failed"})
            continue
        agents.append(agent_row)

    if skip_finalize:
        return {"run_id": run_id, "agents": len(agents), "errors": errors}

    retrieve_result = await finalize_run(run_id, agents, errors, split=split)
    return {
        "run_id": run_id,
        "split": split,
        "agents": len(agents),
        "errors": errors,
        "candidate_count": (retrieve_result.get("meta") or {}).get("candidate_count"),
    }


async def run_batch(
    run_ids: list[str],
    persona_ids: list[str],
    *,
    provider: str | None,
    skip_existing: bool,
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    for run_id in run_ids:
        print(f"=== {run_id} ===", file=sys.stderr)
        try:
            row = await run_batch_for_news(
                run_id,
                persona_ids,
                provider=provider,
                skip_existing=skip_existing,
                skip_finalize=False,
            )
            results.append(row)
            print(
                f"  ok · agents={row.get('agents')} "
                f"candidates={row.get('candidate_count')} "
                f"errors={len(row.get('errors') or [])}",
                file=sys.stderr,
            )
        except Exception as exc:
            results.append({"run_id": run_id, "error": str(exc)})
            print(f"  FAIL: {exc}", file=sys.stderr)
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Phase 3.7 persona batch eval.")
    parser.add_argument(
        "--run-ids",
        nargs="*",
        help="Run ids (default: all 10 from batch-manifest).",
    )
    parser.add_argument(
        "--personas",
        nargs="*",
        help="Persona ids (default: all 12 from SSOT).",
    )
    parser.add_argument(
        "--obs-only",
        action="store_true",
        help="Only observation set 01–04.",
    )
    parser.add_argument(
        "--holdout-only",
        action="store_true",
        help="Only holdout set 05–10.",
    )
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider override.",
    )
    parser.add_argument(
        "--no-skip-existing",
        action="store_true",
        help="Re-run personas even if persona-pipeline.json exists.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print planned matrix only.",
    )
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
        print(f"LLM calls (persona only): {len(run_ids) * len(persona_ids) * 2}")
        return 0

    results = asyncio.run(
        run_batch(
            run_ids,
            persona_ids,
            provider=args.provider,
            skip_existing=not args.no_skip_existing,
        )
    )
    summary_path = PHASE37 / "batch-run-summary.json"
    summary_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    failed = [r for r in results if r.get("error")]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
