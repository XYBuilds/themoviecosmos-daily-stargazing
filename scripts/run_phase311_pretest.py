"""run_phase311_pretest.py · Phase 3.11.1 ADR-0008 composition pretest vs 3.10 baseline.

Reuses phase3.10 alt-pools + neutral n1; re-runs screenwriter with ADR-0008 composition
mode; runs retrieval; compares candidate pool diff (Gap A POV-resonance targets).

Writes under output/Eval/phase3.11/pretest-{timestamp}/.
"""

from __future__ import annotations

import argparse
import asyncio
import json
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
from scripts.lib.phase311_pretest import (
    PHASE310_ROOT,
    PHASE311_ROOT,
    PretestRunSpec,
    assemble_adr8_channel_pseudos,
    build_adr8_screenwriter_user_prompt,
    compare_pool_diff,
    go_no_go_recommendation,
    load_alt_pool_overlay,
    load_baseline_neutral_pseudo,
    load_pretest_manifest,
    parse_adr8_pseudos_response,
    parse_pretest_runs,
    persona_agent_from_pseudos,
    pool_diff_result_to_dict,
    pseudo_segment_to_dict,
    render_pool_diff_markdown,
    summarize_center_granularity,
)
from scripts.personas import _sync_llm_call_with_system
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


async def run_adr8_screenwriter(
    persona_id: str,
    deconstruction: dict[str, Any],
    alt_pool_path: Path,
    *,
    expansion: dict[str, Any] | None,
    baseline_run_dir: Path,
    client: OpenAI,
    model: str,
    timeout: float,
) -> dict[str, Any]:
    alt_pool = load_alt_pool_overlay(alt_pool_path)
    known_frags = _known_fragment_ids(annotate_fragment_ids(deconstruction))
    known_elements = {
        e.element_id for e in alt_pool.elements
    } | {
        str(item.get("id"))
        for section in ("who", "where", "why", "how", "result")
        for item in (annotate_fragment_ids(deconstruction).get(section) or [])
        if isinstance(item, dict) and item.get("id")
    }

    prompt = build_adr8_screenwriter_user_prompt(
        persona_id,
        deconstruction,
        alt_pool,
        expansion=expansion,
    )
    raw = await asyncio.wait_for(
        asyncio.to_thread(
            _sync_llm_call_with_system, client, model, prompt, _SYSTEM_SCREEN
        ),
        timeout=timeout,
    )
    toned = parse_adr8_pseudos_response(
        raw,
        agent_id=persona_id,
        known_fragments=known_frags,
        known_elements=known_elements,
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
    channel_pseudos = assemble_adr8_channel_pseudos(
        persona_id,
        deconstruction,
        alt_pool,
        toned,
        neutral,
        expansion,
    )
    pipeline = {
        "persona_id": persona_id,
        "composition_mode": "ADR-0008",
        "overlay": alt_pool.to_dict() if hasattr(alt_pool, "to_dict") else {},
        "pseudos": [pseudo_segment_to_dict(p) for p in channel_pseudos],
        "screenwriter_raw": raw,
    }
    return pipeline


async def run_pretest_for_spec(
    spec: PretestRunSpec,
    *,
    baseline_root: Path,
    out_run_dir: Path,
    client: OpenAI | None,
    model: str | None,
    timeout: float,
    dry_run: bool,
    skip_retrieval: bool,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    baseline_run = baseline_root / spec.run_id
    if not baseline_run.is_dir():
        raise FileNotFoundError(f"baseline run missing: {baseline_run}")

    decon_path = baseline_run / "reality-deconstructed.json"
    deconstruction = load_deconstruction_from_file(decon_path)
    expansion = _load_expansion(baseline_run)

    persona_pipelines: list[dict[str, Any]] = []
    persona_agents: dict[str, dict[str, Any]] = {}

    for persona_id in spec.personas:
        persona_out = out_run_dir / "personas" / persona_id
        persona_out.mkdir(parents=True, exist_ok=True)

        if dry_run:
            baseline_pipeline = json.loads(
                (
                    baseline_run / "personas" / persona_id / "persona-pipeline.json"
                ).read_text(encoding="utf-8")
            )
            pipeline = {
                **baseline_pipeline,
                "composition_mode": "dry-run-baseline",
            }
        else:
            if client is None or model is None:
                raise RuntimeError("LLM client required for live pretest")
            alt_pool_path = baseline_run / "personas" / persona_id / "alt-pool-overlay.json"
            pipeline = await run_adr8_screenwriter(
                persona_id,
                deconstruction,
                alt_pool_path,
                expansion=expansion,
                baseline_run_dir=baseline_run,
                client=client,
                model=model,
                timeout=timeout,
            )

        persona_pipelines.append(pipeline)
        (persona_out / "persona-pipeline.json").write_text(
            json.dumps(pipeline, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        pseudos = pipeline.get("pseudos") or []
        persona_agents[persona_id] = persona_agent_from_pseudos(persona_id, [])  # placeholder
        from scripts.agents import PseudoSegment

        pseudo_objs = [
            PseudoSegment(
                str(p["id"]),
                str(p["text"]),
                dict(p.get("source") or {}),
                list(p.get("warnings") or []),
                fit=p.get("fit"),
            )
            for p in pseudos
        ]
        persona_agents[persona_id] = persona_agent_from_pseudos(persona_id, pseudo_objs)

    agents_payload = {"agents": reorder_persona_agents(spec.personas, persona_agents)}
    (out_run_dir / "agents.json").write_text(
        json.dumps(agents_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    baseline_retrieve = json.loads(
        (baseline_run / "retrieve.json").read_text(encoding="utf-8")
    )
    if skip_retrieval:
        pretest_retrieve = baseline_retrieve
        retrieval_note = "skipped: embeddings index unavailable or --skip-retrieval"
    else:
        pretest_retrieve = retrieve_from_agents(
            agents_payload["agents"],
            errors=[],
        )
        retrieval_note = "live"
    (out_run_dir / "retrieve.json").write_text(
        json.dumps(pretest_retrieve, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    diff = compare_pool_diff(
        run_id=spec.run_id,
        baseline_retrieve=baseline_retrieve,
        pretest_retrieve=pretest_retrieve,
        gap_a_targets=spec.gap_a_targets,
    )
    diff_dict = pool_diff_result_to_dict(diff)
    (out_run_dir / "pool-diff.json").write_text(
        json.dumps(diff_dict, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    center_obs = summarize_center_granularity(persona_pipelines)
    (out_run_dir / "center-granularity.json").write_text(
        json.dumps(center_obs, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    gap_target_ids = [int(t.tmdb_id) for t in spec.gap_a_targets]
    baseline_pool = {
        int(c["tmdb_id"])
        for c in baseline_retrieve.get("candidates") or []
        if isinstance(c, dict) and c.get("tmdb_id") is not None
    }
    run_summary = {
        "run_id": spec.run_id,
        "personas": spec.personas,
        "dry_run": dry_run,
        "retrieval": retrieval_note,
        "gap_a_targets_already_in_baseline": [
            tid for tid in gap_target_ids if tid in baseline_pool
        ],
        "gap_a_targets_missing_from_baseline": [
            tid for tid in gap_target_ids if tid not in baseline_pool
        ],
        "pool_diff": diff_dict,
        "center_granularity": center_obs,
    }
    return run_summary, persona_pipelines


async def main_async(args: argparse.Namespace) -> int:
    manifest = load_pretest_manifest(
        Path(args.manifest) if args.manifest else None
    )
    specs = parse_pretest_runs(manifest)
    if args.run_id:
        wanted = set(args.run_id)
        specs = [s for s in specs if s.run_id in wanted]
        if not specs:
            raise SystemExit(f"no matching run_id in manifest: {wanted}")

    ts = datetime.now(UTC).strftime("%Y%m%d-%H%M%S")
    out_root = Path(args.output_dir) if args.output_dir else PHASE311_ROOT / f"pretest-{ts}"
    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "pretest-manifest.json").write_text(
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
            f"[pretest] embeddings missing at {embeddings_npy()}; "
            "using --skip-retrieval (baseline pool diff only)"
        )
        skip_retrieval = True

    if not dry_run:
        provider = _resolve_provider(args.provider)
        client = get_llm_client(provider)
        model = _model_name(provider)

    baseline_root = Path(args.baseline_dir) if args.baseline_dir else PHASE310_ROOT
    run_summaries: list[dict[str, Any]] = []
    all_pipelines: list[dict[str, Any]] = []

    for spec in specs:
        print(f"[pretest] {spec.run_id} personas={spec.personas} dry_run={dry_run}")
        summary, pipelines = await run_pretest_for_spec(
            spec,
            baseline_root=baseline_root,
            out_run_dir=out_root / spec.run_id,
            client=client,
            model=model,
            timeout=timeout,
            dry_run=dry_run,
            skip_retrieval=skip_retrieval,
        )
        run_summaries.append(summary)
        all_pipelines.extend(pipelines)

    total_net_new = sum(
        len(s["pool_diff"]["net_new_tmdb_ids"]) for s in run_summaries
    )
    gap_hits = sum(
        len(s["pool_diff"]["gap_a_targets_in_net_new"]) for s in run_summaries
    )
    runs_with_gap = sum(
        1 for s in run_summaries if s["pool_diff"]["gap_a_targets_in_net_new"]
    )

    aggregate = {
        "run_count": len(run_summaries),
        "total_net_new_candidates": total_net_new,
        "gap_a_targets_recalled_net_new": gap_hits,
        "runs_with_gap_a_net_new": runs_with_gap,
        "dry_run": dry_run,
        "skip_retrieval": skip_retrieval,
        "runs": run_summaries,
    }
    go = go_no_go_recommendation(aggregate)
    aggregate["go_no_go"] = go

    (out_root / "summary.json").write_text(
        json.dumps(aggregate, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    center_all = summarize_center_granularity(all_pipelines)
    report_md = render_pool_diff_markdown(
        manifest=manifest,
        per_run=[
            compare_pool_diff(
                run_id=s["run_id"],
                baseline_retrieve=json.loads(
                    (baseline_root / s["run_id"] / "retrieve.json").read_text(
                        encoding="utf-8"
                    )
                ),
                pretest_retrieve=json.loads(
                    (out_root / s["run_id"] / "retrieve.json").read_text(
                        encoding="utf-8"
                    )
                ),
                gap_a_targets=next(
                    x.gap_a_targets for x in specs if x.run_id == s["run_id"]
                ),
            )
            for s in run_summaries
        ],
        center_summary=center_all,
        go_no_go=go,
    )
    (out_root / "pool-diff-report.md").write_text(report_md, encoding="utf-8")

    print(json.dumps({"output_dir": str(out_root), "go_no_go": go}, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Phase 3.11.1 ADR-0008 composition pretest")
    p.add_argument(
        "--dry-run",
        action="store_true",
        help="Reuse 3.10 pseudos (expect zero pool diff); scaffold/CI only",
    )
    p.add_argument(
        "--skip-retrieval",
        action="store_true",
        help="Skip embedding retrieval (pool diff vs baseline retrieve only)",
    )
    p.add_argument("--provider", default=None, help="LLM provider override")
    p.add_argument("--baseline-dir", default=None, help="3.10 eval root")
    p.add_argument("--output-dir", default=None, help="Output directory")
    p.add_argument("--manifest", default=None, help="Pretest manifest JSON path")
    p.add_argument(
        "--run-id",
        action="append",
        dest="run_id",
        help="Limit to run_id (repeatable)",
    )
    return p


def main() -> None:
    args = build_parser().parse_args()
    raise SystemExit(asyncio.run(main_async(args)))


if __name__ == "__main__":
    main()
