"""run_phase311_pilot.py · Phase 3.11.6 single-news pilot A/B + firewall audit.

Runs ADR-0008 design-on (screenwriter + assembly) for one news item vs frozen 3.10
baseline; retrieval + pool diff; structured audit artifacts for human Go/No-Go.

Writes under output/Eval/phase3.11/pilot-{timestamp}/.
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

from openai import OpenAI

from scripts.agents import (
    _agent_llm_timeout,
    _known_fragment_ids,
    _model_name,
    _resolve_provider,
    annotate_fragment_ids,
    load_deconstruction_from_file,
    minimal_clean,
)
from scripts.lib.env import load_env
from scripts.lib.llm import get_llm_client
from scripts.lib.paths import embeddings_npy, repo_root
from scripts.lib.phase311_pilot import (
    PHASE311_ROOT,
    PilotRunSpec,
    audit_pilot_run,
    go_no_go_pilot_recommendation,
    load_pilot_manifest,
    parse_pilot_runs,
    render_pilot_audit_markdown,
)
from scripts.lib.phase311_pretest import (
    PHASE310_ROOT,
    assemble_adr8_channel_pseudos_with_baseline_neutral,
    build_adr8_screenwriter_user_prompt,
    load_alt_pool_overlay,
    load_baseline_neutral_pseudo,
    persona_agent_from_pseudos,
    pseudo_segment_to_dict,
)
from scripts.personas import (
    NEUTRAL_PSEUDO_ID,
    _sync_llm_call_with_system,
    known_element_ids,
    parse_adr8_pseudos_response,
)
from scripts.retrieve import retrieve_from_agents
from scripts.run_persona_batch import reorder_persona_agents

_SYSTEM_SCREEN = (
    "You are a persona screenwriter. Follow the user message exactly. "
    "Return only valid JSON matching the persona screenwriter contract "
    "(including fit, center, channel, focal when applicable)."
)


def _load_expansion(run_dir: Path) -> dict[str, Any] | None:
    path = run_dir / "reality-expanded.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    expansion = data.get("expansion")
    return expansion if isinstance(expansion, dict) else None


def _copy_baseline_static_inputs(baseline_run: Path, out_run: Path) -> None:
    """Copy read-only 3.10 inputs the pilot does not regenerate."""
    for name in (
        "reality-deconstructed.json",
        "reality-deconstructed.md",
        "reality-expanded.json",
        "reality.json",
        "reality.md",
    ):
        src = baseline_run / name
        if src.is_file():
            shutil.copy2(src, out_run / name)


async def run_design_on_persona(
    persona_id: str,
    deconstruction: dict[str, Any],
    alt_pool_path: Path,
    *,
    expansion: dict[str, Any] | None,
    baseline_run_dir: Path,
    out_persona_dir: Path,
    client: OpenAI,
    model: str,
    timeout: float,
) -> dict[str, Any]:
    out_persona_dir.mkdir(parents=True, exist_ok=True)
    alt_pool = load_alt_pool_overlay(alt_pool_path)
    known_frags = _known_fragment_ids(annotate_fragment_ids(deconstruction))
    known_elements = known_element_ids(deconstruction)
    repair_retries: list[dict[str, str]] = []
    drop_reasons: list[dict[str, str]] = []
    repair_context: str | None = None
    raw = ""
    toned = None

    for attempt in (1, 2):
        prompt = build_adr8_screenwriter_user_prompt(
            persona_id,
            deconstruction,
            alt_pool,
            expansion=expansion,
            repair_context=repair_context,
        )
        raw = await asyncio.wait_for(
            asyncio.to_thread(
                _sync_llm_call_with_system, client, model, prompt, _SYSTEM_SCREEN
            ),
            timeout=timeout,
        )
        try:
            attempt_drops: list[dict[str, str]] = []
            toned = parse_adr8_pseudos_response(
                raw,
                agent_id=persona_id,
                known_fragments=known_frags,
                known_elements=known_elements,
                deconstruction=deconstruction,
                alt_pool=alt_pool,
                expansion=expansion,
                drop_reasons=attempt_drops,
            )
            toned = [
                type(t)(
                    t.id,
                    minimal_clean(t.text),
                    t.source,
                    t.warnings,
                    fit=t.fit,
                )
                for t in toned
            ]
            neutral = load_baseline_neutral_pseudo(baseline_run_dir, persona_id)
            channel_pseudos = assemble_adr8_channel_pseudos_with_baseline_neutral(
                persona_id,
                deconstruction,
                alt_pool,
                toned,
                neutral,
                expansion,
                drop_reasons=attempt_drops,
            )
            drop_reasons = attempt_drops
            repair_retries.append(
                {"stage": "screenwriter", "attempt": str(attempt), "error": "ok"}
            )
            break
        except ValueError as exc:
            err = str(exc)
            repair_retries.append(
                {"stage": "screenwriter", "attempt": str(attempt), "error": err}
            )
            if attempt >= 2:
                raise
            repair_context = err

    if toned is None:
        raise RuntimeError(f"{persona_id}: screenwriter produced no pseudos")
    alt_dest = out_persona_dir / "alt-pool-overlay.json"
    if not alt_dest.is_file():
        shutil.copy2(alt_pool_path, alt_dest)

    element_centered = [p for p in channel_pseudos if p.id != NEUTRAL_PSEUDO_ID]
    pipeline = {
        "persona_id": persona_id,
        "composition_mode": "ADR-0008",
        "overlay": alt_pool.to_dict() if hasattr(alt_pool, "to_dict") else {},
        "pseudos": [pseudo_segment_to_dict(p) for p in channel_pseudos],
        "screenwriter_raw": raw,
        "repair_retries": repair_retries,
        "pseudo_guard": {
            "kept_pseudos": len(element_centered),
            "dropped_pseudos": len(drop_reasons),
            "drop_reasons": drop_reasons,
        },
    }
    (out_persona_dir / "persona-pipeline.json").write_text(
        json.dumps(pipeline, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return pipeline


async def run_pilot_for_spec(
    spec: PilotRunSpec,
    *,
    baseline_root: Path,
    out_run_dir: Path,
    client: OpenAI | None,
    model: str | None,
    timeout: float,
    dry_run: bool,
    skip_retrieval: bool,
    concurrency: int,
) -> dict[str, Any]:
    baseline_run = baseline_root / spec.run_id
    if not baseline_run.is_dir():
        raise FileNotFoundError(f"baseline run missing: {baseline_run}")

    out_run_dir.mkdir(parents=True, exist_ok=True)
    _copy_baseline_static_inputs(baseline_run, out_run_dir)

    decon_path = baseline_run / "reality-deconstructed.json"
    deconstruction = load_deconstruction_from_file(decon_path)
    expansion = _load_expansion(baseline_run)

    sem = asyncio.Semaphore(max(1, concurrency))
    pipelines: list[dict[str, Any]] = []
    errors: list[dict[str, str]] = []

    async def _one(pid: str) -> None:
        persona_out = out_run_dir / "personas" / pid
        async with sem:
            if dry_run:
                baseline_pipeline = json.loads(
                    (
                        baseline_run / "personas" / pid / "persona-pipeline.json"
                    ).read_text(encoding="utf-8")
                )
                persona_out.mkdir(parents=True, exist_ok=True)
                alt_src = baseline_run / "personas" / pid / "alt-pool-overlay.json"
                if alt_src.is_file():
                    shutil.copy2(alt_src, persona_out / "alt-pool-overlay.json")
                pipeline = {
                    **baseline_pipeline,
                    "composition_mode": "dry-run-baseline",
                }
            else:
                if client is None or model is None:
                    raise RuntimeError("LLM client required for live pilot")
                alt_pool_path = baseline_run / "personas" / pid / "alt-pool-overlay.json"
                try:
                    pipeline = await run_design_on_persona(
                        pid,
                        deconstruction,
                        alt_pool_path,
                        expansion=expansion,
                        baseline_run_dir=baseline_run,
                        out_persona_dir=persona_out,
                        client=client,
                        model=model,
                        timeout=timeout,
                    )
                except Exception as exc:
                    persona_out.mkdir(parents=True, exist_ok=True)
                    errors.append({"persona_id": pid, "error": str(exc)})
                    pipeline = {
                        "persona_id": pid,
                        "error": str(exc),
                        "pseudos": [],
                    }
                    (persona_out / "persona-pipeline.json").write_text(
                        json.dumps(pipeline, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8",
                    )
            pipelines.append(pipeline)

    await asyncio.gather(*[_one(pid) for pid in spec.personas])

    from scripts.agents import PseudoSegment

    persona_agents: dict[str, dict[str, Any]] = {}
    for pipeline in pipelines:
        pid = str(pipeline.get("persona_id", ""))
        pseudo_objs = [
            PseudoSegment(
                str(p["id"]),
                str(p["text"]),
                dict(p.get("source") or {}),
                list(p.get("warnings") or []),
                fit=p.get("fit"),
            )
            for p in pipeline.get("pseudos") or []
        ]
        persona_agents[pid] = persona_agent_from_pseudos(pid, pseudo_objs)

    agents_payload = {"agents": reorder_persona_agents(spec.personas, persona_agents)}
    (out_run_dir / "agents.json").write_text(
        json.dumps(agents_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    baseline_retrieve = json.loads(
        (baseline_run / "retrieve.json").read_text(encoding="utf-8")
    )
    if skip_retrieval:
        design_retrieve = baseline_retrieve
        retrieval_note = "skipped: embeddings index unavailable or --skip-retrieval"
    else:
        design_retrieve = retrieve_from_agents(
            agents_payload["agents"],
            errors=errors,
        )
        retrieval_note = "live"
    (out_run_dir / "retrieve.json").write_text(
        json.dumps(design_retrieve, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    audit = audit_pilot_run(
        run_dir=out_run_dir,
        baseline_run_dir=baseline_run,
        deconstruction=deconstruction,
        expansion=expansion,
        baseline_retrieve=baseline_retrieve,
        design_retrieve=design_retrieve,
        gap_a_targets=spec.gap_a_targets,
    )
    (out_run_dir / "audit.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_run_dir / "center-granularity.json").write_text(
        json.dumps(audit.get("center_granularity") or {}, ensure_ascii=False, indent=2)
        + "\n",
        encoding="utf-8",
    )
    (out_run_dir / "pool-diff.json").write_text(
        json.dumps(audit.get("pool_diff") or {}, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return {
        "run_id": spec.run_id,
        "personas": spec.personas,
        "dry_run": dry_run,
        "retrieval": retrieval_note,
        "persona_errors": errors,
        "audit": audit,
    }


async def main_async(args: argparse.Namespace) -> int:
    manifest = load_pilot_manifest(Path(args.manifest) if args.manifest else None)
    specs = parse_pilot_runs(manifest)
    if args.run_id:
        wanted = set(args.run_id)
        specs = [s for s in specs if s.run_id in wanted]
        if not specs:
            raise SystemExit(f"no matching run_id in manifest: {wanted}")

    ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    out_root = Path(args.output_dir) if args.output_dir else PHASE311_ROOT / f"pilot-{ts}"
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "pilot-manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    load_env()
    client: OpenAI | None = None
    model: str | None = None
    timeout = _agent_llm_timeout()
    dry_run = bool(args.dry_run)
    skip_retrieval = bool(args.skip_retrieval)
    if not skip_retrieval and not embeddings_npy().is_file():
        print(
            f"[pilot] embeddings missing at {embeddings_npy()}; "
            "using --skip-retrieval (baseline pool for diff only)"
        )
        skip_retrieval = True

    if not dry_run:
        provider = _resolve_provider(args.provider)
        client = get_llm_client(provider)
        model = _model_name(provider)

    baseline_root = Path(args.baseline_dir) if args.baseline_dir else PHASE310_ROOT
    run_summaries: list[dict[str, Any]] = []

    for spec in specs:
        print(
            f"[pilot] {spec.run_id} personas={len(spec.personas)} "
            f"dry_run={dry_run} skip_retrieval={skip_retrieval}"
        )
        summary = await run_pilot_for_spec(
            spec,
            baseline_root=baseline_root,
            out_run_dir=out_root / spec.run_id,
            client=client,
            model=model,
            timeout=timeout,
            dry_run=dry_run,
            skip_retrieval=skip_retrieval,
            concurrency=int(args.concurrency),
        )
        run_summaries.append(summary)

    primary = run_summaries[0] if run_summaries else {}
    primary_audit = primary.get("audit") or {}
    go = go_no_go_pilot_recommendation(
        primary_audit,
        dry_run=dry_run,
        persona_errors=primary.get("persona_errors"),
        skip_retrieval=skip_retrieval,
    )

    aggregate = {
        "run_count": len(run_summaries),
        "dry_run": dry_run,
        "skip_retrieval": skip_retrieval,
        "baseline_dir": str(baseline_root.resolve()),
        "go_no_go": go,
        "pipeline_go_metrics": go.get("metrics"),
        "runs": [
            {
                "run_id": s["run_id"],
                "retrieval": s["retrieval"],
                "persona_errors": s["persona_errors"],
                "all_automated_pass": s["audit"].get("all_automated_pass"),
                "pool_diff": s["audit"].get("pool_diff"),
            }
            for s in run_summaries
        ],
    }
    (out_root / "summary.json").write_text(
        json.dumps(aggregate, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    report_md = render_pilot_audit_markdown(
        primary_audit,
        go_no_go=go,
        output_dir=str(out_root.resolve()),
        baseline_dir=str((baseline_root / specs[0].run_id).resolve()),
    )
    (out_root / "pilot-audit.md").write_text(report_md, encoding="utf-8")

    print(
        json.dumps(
            {
                "output_dir": str(out_root),
                "go_no_go": go,
                "all_automated_pass": primary_audit.get("all_automated_pass"),
            },
            indent=2,
        )
    )
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Phase 3.11.6 single-news pilot A/B audit")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Reuse 3.10 pseudos (scaffold/CI only)",
    )
    p.add_argument(
        "--skip-retrieval",
        action="store_true",
        help="Skip embedding retrieval",
    )
    p.add_argument("--provider", default=None, help="LLM provider override")
    p.add_argument("--baseline-dir", default=None, help="3.10 eval root")
    p.add_argument("--output-dir", default=None, help="Output directory")
    p.add_argument("--manifest", default=None, help="Pilot manifest JSON path")
    p.add_argument(
        "--run-id",
        action="append",
        dest="run_id",
        help="Limit to run_id (repeatable)",
    )
    p.add_argument(
        "--concurrency",
        type=int,
        default=3,
        help="Max concurrent persona LLM calls (default 3)",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()
    raise SystemExit(asyncio.run(main_async(args)))


if __name__ == "__main__":
    main()
