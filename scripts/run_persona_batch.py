"""run_persona_batch.py · Phase 3.7 N=10 batch: 12 personas × news + A1 baseline per run.

Reads neutral decon from output/Eval/phase3.6/{run_id}/ (read-only). Writes under
output/Eval/phase3.7/{run_id}/ with per-persona subdirs and merged retrieve.json.
Editor scoring uses output/Eval/phase3.7/high-hit-score-review.md (from score_eval_candidates).

Phase 3.9.5: concurrent persona generation (Semaphore + gather), stable agent ordering,
startup jitter, and LLM 429/timeout exponential backoff.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import random
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Awaitable, Callable, TypeVar

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.agents import PseudoSegment, pseudo_to_dict
from scripts.eval_batch_manifest import load_manifest
from scripts.lib.paths import repo_root
from scripts.personas import (
    NEUTRAL_PSEUDO_ID,
    build_alt_pool_overlay,
    list_persona_ids,
    pipeline_result_to_dict,
    run_persona_pipeline,
    validate_neutral_pseudo_batch_diversity,
)
from scripts.retrieve import retrieve_from_agents
from scripts.run_eval import load_deconstruction_from_file

PHASE36 = repo_root() / "output" / "Eval" / "phase3.6"
PHASE37 = repo_root() / "output" / "Eval" / "phase3.7"
PHASE38 = repo_root() / "output" / "Eval" / "phase3.8"
PHASE39 = repo_root() / "output" / "Eval" / "phase3.9"
OBS_RUN_PREFIXES = ("01-", "02-", "03-", "04-")

DEFAULT_CONCURRENCY = 3
JITTER_SEC_MIN = 5.0
JITTER_SEC_MAX = 15.0
LLM_BACKOFF_INITIAL_SEC = 2.0
LLM_BACKOFF_MAX_RETRIES = 4

_T = TypeVar("_T")


def split_obs_holdout(run_ids: list[str]) -> tuple[list[str], list[str]]:
    obs = [r for r in run_ids if r.startswith(OBS_RUN_PREFIXES)]
    holdout = [r for r in run_ids if r not in obs]
    return obs, holdout


def phase36_run_dir(run_id: str) -> Path:
    return PHASE36 / run_id


def phase37_run_dir(run_id: str) -> Path:
    return PHASE37 / run_id


def phase38_run_dir(run_id: str) -> Path:
    return PHASE38 / run_id


def phase39_run_dir(run_id: str) -> Path:
    return PHASE39 / run_id


def eval_phase_dir(eval_phase: str) -> Path:
    if eval_phase == "3.9":
        return PHASE39
    if eval_phase == "3.8":
        return PHASE38
    return PHASE37


def eval_run_dir(run_id: str, eval_phase: str) -> Path:
    if eval_phase == "3.9":
        return phase39_run_dir(run_id)
    if eval_phase == "3.8":
        return phase38_run_dir(run_id)
    return phase37_run_dir(run_id)


def is_retryable_llm_error(exc: BaseException | str | None) -> bool:
    if exc is None:
        return False
    if isinstance(exc, TimeoutError):
        return True
    msg = str(exc).lower()
    return (
        "429" in msg
        or "rate limit" in msg
        or "rate_limit" in msg
        or "too many requests" in msg
        or "timed out" in msg
        or "timeout" in msg
    )


async def with_llm_backoff(
    fn: Callable[[], Awaitable[_T]],
    *,
    is_retryable: Callable[[BaseException | str | None], bool] = is_retryable_llm_error,
    max_retries: int = LLM_BACKOFF_MAX_RETRIES,
    initial_delay: float = LLM_BACKOFF_INITIAL_SEC,
) -> _T:
    """Exponential backoff for LLM 429 / timeout errors (raises from fn)."""
    delay = initial_delay
    for attempt in range(max_retries + 1):
        try:
            return await fn()
        except Exception as exc:
            if attempt >= max_retries or not is_retryable(exc):
                raise
            await asyncio.sleep(delay)
            delay *= 2
    raise RuntimeError("unreachable backoff state")


def startup_jitter_seconds(
    *,
    jitter_min: float = JITTER_SEC_MIN,
    jitter_max: float = JITTER_SEC_MAX,
    rng: random.Random | None = None,
) -> float:
    r = rng or random
    return r.uniform(jitter_min, jitter_max)


def _neutral_pseudos_from_persona_agents(
    persona_agents: dict[str, dict[str, Any]],
) -> list[PseudoSegment]:
    """Collect per-persona neutral pseudos for batch diversity guard."""
    neutrals: list[PseudoSegment] = []
    for agent in persona_agents.values():
        for row in agent.get("pseudos") or []:
            if not isinstance(row, dict):
                continue
            src = row.get("source") if isinstance(row.get("source"), dict) else {}
            pid = str(row.get("id") or row.get("pseudo_id") or "").strip()
            if src.get("channel_role") != "neutral" and pid != NEUTRAL_PSEUDO_ID:
                continue
            neutrals.append(
                PseudoSegment(
                    id=pid,
                    text=str(row.get("text") or ""),
                    source=src,
                    warnings=list(row.get("warnings") or []),
                    fit=row.get("fit"),
                )
            )
    return neutrals


def _toned_text_by_persona_agents(
    persona_agents: dict[str, dict[str, Any]],
) -> dict[str, str]:
    """Concatenate each persona's toned (non-neutral) pseudo texts for the guard."""
    toned: dict[str, str] = {}
    for agent_id, agent in persona_agents.items():
        parts: list[str] = []
        for row in agent.get("pseudos") or []:
            if not isinstance(row, dict):
                continue
            src = row.get("source") if isinstance(row.get("source"), dict) else {}
            pid = str(row.get("id") or row.get("pseudo_id") or "").strip()
            if src.get("channel_role") == "neutral" or pid == NEUTRAL_PSEUDO_ID:
                continue
            parts.append(str(row.get("text") or ""))
        toned[str(agent_id)] = " ".join(parts).strip()
    return toned


def reorder_persona_agents(
    persona_ids: list[str],
    persona_agents: dict[str, dict[str, Any]],
    *,
    prefix_agents: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Stable agents[] order matching persona_ids (retrieve.json reproducibility)."""
    ordered: list[dict[str, Any]] = list(prefix_agents or [])
    for persona_id in persona_ids:
        agent = persona_agents.get(persona_id)
        if agent is not None:
            ordered.append(agent)
    return ordered


def _load_expansion_from_run(run_dir: Path) -> dict[str, Any] | None:
    path = run_dir / "reality-expanded.json"
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    expansion = data.get("expansion")
    return expansion if isinstance(expansion, dict) else None


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


def _copy_phase38_static(run_id: str, out_dir: Path) -> None:
    """Copy read-only snapshots from phase3.8 into phase3.9 (does not modify phase3.8)."""
    src = phase38_run_dir(run_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    for name in (
        "reality.json",
        "reality.md",
        "reality-deconstructed.json",
        "reality-deconstructed.md",
        "reality-expanded.json",
    ):
        src_file = src / name
        if src_file.is_file():
            shutil.copy2(src_file, out_dir / name)


def write_a1_parallel_baseline(run_id: str, out_dir: Path | None = None) -> dict[str, Any]:
    """A1-only retrieve from phase3.6 pseudos (read-only) for 3.8.8 superset gate.

    Writes ``retrieve-a1.json`` and ``a1-baseline-meta.json`` under the phase3.8 run dir.
    Does not modify phase3.6.
    """
    out_dir = out_dir or phase38_run_dir(run_id)
    out_dir.mkdir(parents=True, exist_ok=True)
    a1_agent = load_a1_agent_from_phase36(run_id)
    retrieve_result = retrieve_from_agents([a1_agent], [])
    (out_dir / "retrieve-a1.json").write_text(
        json.dumps(retrieve_result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    a1_oracle = retrieve_result.get("a1_oracle") or {}
    hit_ids = sorted(int(x) for x in (a1_oracle.get("hit_tmdb_ids") or []))
    if not hit_ids:
        hit_ids = sorted(
            int(c["tmdb_id"])
            for c in retrieve_result.get("candidates") or []
            if c.get("tmdb_id") is not None
        )
    meta = {
        "run_id": run_id,
        "split": "observation" if run_id.startswith(OBS_RUN_PREFIXES) else "holdout",
        "source": str(phase36_run_dir(run_id) / "retrieve.json"),
        "a1_pseudo_count": len(a1_agent.get("pseudos") or []),
        "candidate_count": (retrieve_result.get("meta") or {}).get("candidate_count"),
        "a1_hit_tmdb_ids": hit_ids,
        "finished_at": datetime.now(UTC).isoformat(),
    }
    (out_dir / "a1-baseline-meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return meta


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


def persona_pipeline_to_agent(
    persona_id: str,
    pseudos: list,
    *,
    eval_phase: str = "3.7",
) -> dict[str, Any]:
    role = "persona" if eval_phase in ("3.8", "3.9") else "creative"
    return {
        "agent_id": persona_id,
        "persona_name": persona_id,
        "role": role,
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
    expansion: dict[str, Any] | None = None,
    eval_phase: str = "3.7",
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
        return persona_pipeline_to_agent(persona_id, pseudos, eval_phase=eval_phase), None

    deconstruction = load_deconstruction_from_file(decon_path)
    delay = LLM_BACKOFF_INITIAL_SEC
    result = None
    for attempt in range(LLM_BACKOFF_MAX_RETRIES + 1):
        result = await run_persona_pipeline(
            persona_id,
            deconstruction,
            provider=provider,
            expansion=expansion,
        )
        if not result.error or not is_retryable_llm_error(result.error):
            break
        if attempt < LLM_BACKOFF_MAX_RETRIES:
            await asyncio.sleep(delay)
            delay *= 2
    assert result is not None
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
    return persona_pipeline_to_agent(persona_id, result.pseudos, eval_phase=eval_phase), None


async def finalize_run(
    run_id: str,
    agents: list[dict[str, Any]],
    errors: list[dict[str, Any]],
    *,
    split: str,
    eval_phase: str = "3.7",
) -> dict[str, Any]:
    out_dir = eval_run_dir(run_id, eval_phase)
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
    if eval_phase in ("3.8", "3.9"):
        try:
            a1_meta = write_a1_parallel_baseline(run_id, out_dir)
            meta["a1_parallel"] = a1_meta
            (out_dir / "batch-run-meta.json").write_text(
                json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
        except (FileNotFoundError, ValueError) as exc:
            meta["a1_parallel_error"] = str(exc)
            (out_dir / "batch-run-meta.json").write_text(
                json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    return retrieve_result


async def _run_personas_concurrent(
    run_id: str,
    persona_ids: list[str],
    out_dir: Path,
    decon_path: Path,
    *,
    provider: str | None,
    skip_existing: bool,
    expansion: dict[str, Any] | None,
    eval_phase: str,
    concurrency: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    semaphore = asyncio.Semaphore(max(1, concurrency))
    errors: list[dict[str, Any]] = []
    persona_agents: dict[str, dict[str, Any]] = {}

    async def _one(persona_id: str) -> None:
        async with semaphore:
            await asyncio.sleep(startup_jitter_seconds())
            persona_dir = persona_artifact_dir(out_dir, persona_id)
            try:
                agent_row, err = await run_persona_for_news(
                    persona_id,
                    decon_path,
                    persona_dir,
                    provider=provider,
                    skip_existing=skip_existing,
                    expansion=expansion,
                    eval_phase=eval_phase,
                )
            except Exception as exc:
                errors.append({"agent_id": persona_id, "message": str(exc)})
                return
            if err or agent_row is None:
                errors.append({"agent_id": persona_id, "message": err or "failed"})
                return
            persona_agents[persona_id] = agent_row

    await asyncio.gather(*[_one(pid) for pid in persona_ids])

    if eval_phase in ("3.8", "3.9") and len(persona_agents) >= 2:
        diversity_warnings = validate_neutral_pseudo_batch_diversity(
            _neutral_pseudos_from_persona_agents(persona_agents),
            toned_text_by_agent=_toned_text_by_persona_agents(persona_agents),
        )
        for warning in diversity_warnings:
            print(f"[diversity guard] {warning}", file=sys.stderr)

    prefix: list[dict[str, Any]] = []
    if eval_phase not in ("3.8", "3.9"):
        prefix = [load_a1_agent_from_phase36(run_id)]
    agents = reorder_persona_agents(persona_ids, persona_agents, prefix_agents=prefix)
    return agents, errors


async def run_batch_for_news(
    run_id: str,
    persona_ids: list[str],
    *,
    provider: str | None,
    skip_existing: bool,
    skip_finalize: bool,
    eval_phase: str = "3.7",
    concurrency: int = DEFAULT_CONCURRENCY,
) -> dict[str, Any]:
    if eval_phase == "3.9":
        src38 = phase38_run_dir(run_id)
        decon_path = src38 / "reality-deconstructed.json"
        if not decon_path.is_file():
            raise FileNotFoundError(
                f"phase3.8 decon missing: {decon_path} "
                "(run scripts/run_phase38_eval.py first)"
            )
        out_dir = phase39_run_dir(run_id)
        _copy_phase38_static(run_id, out_dir)
        expansion = _load_expansion_from_run(src38)
    elif eval_phase == "3.8":
        out_dir = phase38_run_dir(run_id)
        decon_path = out_dir / "reality-deconstructed.json"
        if not decon_path.is_file():
            raise FileNotFoundError(
                f"phase3.8 decon missing: {decon_path} "
                "(run scripts/run_phase38_eval.py first)"
            )
        expansion = _load_expansion_from_run(out_dir)
    else:
        decon_path = phase36_run_dir(run_id) / "reality-deconstructed.json"
        if not decon_path.is_file():
            raise FileNotFoundError(f"neutral decon missing: {decon_path}")
        out_dir = phase37_run_dir(run_id)
        _copy_phase36_static(run_id, out_dir)
        expansion = None

    split = "observation" if run_id.startswith(OBS_RUN_PREFIXES) else "holdout"

    agents, errors = await _run_personas_concurrent(
        run_id,
        persona_ids,
        out_dir,
        decon_path,
        provider=provider,
        skip_existing=skip_existing,
        expansion=expansion,
        eval_phase=eval_phase,
        concurrency=concurrency,
    )

    if skip_finalize:
        return {"run_id": run_id, "agents": len(agents), "errors": errors}

    retrieve_result = await finalize_run(
        run_id, agents, errors, split=split, eval_phase=eval_phase
    )
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
    eval_phase: str = "3.7",
    concurrency: int = DEFAULT_CONCURRENCY,
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
                eval_phase=eval_phase,
                concurrency=concurrency,
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
    parser.add_argument(
        "--eval-phase",
        choices=["3.7", "3.8", "3.9"],
        default="3.7",
        help=(
            "Eval output phase (3.8: phase3.8/; 3.9: read phase3.8 decon+expansion, "
            "write phase3.9/; neither includes A1 in persona agents)."
        ),
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=DEFAULT_CONCURRENCY,
        help=f"Max concurrent personas per news run (default {DEFAULT_CONCURRENCY}).",
    )
    args = parser.parse_args(argv)

    if args.concurrency < 1:
        print("error: --concurrency must be >= 1", file=sys.stderr)
        return 2

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
        print(f"concurrency: {args.concurrency}")
        return 0

    results = asyncio.run(
        run_batch(
            run_ids,
            persona_ids,
            provider=args.provider,
            skip_existing=not args.no_skip_existing,
            eval_phase=args.eval_phase,
            concurrency=args.concurrency,
        )
    )
    summary_dir = eval_phase_dir(args.eval_phase)
    summary_path = summary_dir / "batch-run-summary.json"
    summary_path.write_text(
        json.dumps(results, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    failed = [r for r in results if r.get("error")]
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
