"""run_eval.py · 评测管线：新闻 → deconstruct → agents → retrieve → Eval 目录产物.

每条新闻写入 output/Eval/{run_id}/：reality / facts、各 Agent 文档、聚合候选（填分）、candidates.json。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
import unicodedata
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.agents import (
    RUN_ORDER,
    AgentOutput,
    annotate_fragment_ids,
    load_deconstruction_from_file,
    load_news_from_file,
    news_to_dict,
)
from scripts.expand import run_expansion
from scripts.extract import render_deconstruction_md, run_deconstruct
from scripts.lib.render_briefing import (
    _agents_from_hit_sources,
    _candidate_auto_score_lines,
    _candidate_heading,
    _format_agent_markdown,
    _format_candidate_block,
    _format_candidates_markdown,
    _format_errors,
    _format_hit_lines,
    _format_reality_body,
    _format_run_index,
    _hit_heading,
    _pseudo_hit_total,
    _sort_candidates_for_display,
)
from scripts.lib.run_options import RunOptions
from scripts.retrieve import retrieve_from_agents
from scripts.rewrite import list_persona_ids, pipeline_result_to_dict, run_persona_pipeline

_PSEUDO_ORDER: tuple[str, ...] = RUN_ORDER


def _progress(message: str) -> None:
    ts = datetime.now(UTC).isoformat(timespec="seconds")
    print(f"{ts} {message}", file=sys.stderr, flush=True)


def _elapsed(start: float) -> str:
    return f"{time.perf_counter() - start:.1f}s"


def slugify(text: str, *, max_len: int = 60) -> str:
    """ASCII-safe slug from arbitrary title text."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    if len(slug) > max_len:
        slug = slug[:max_len].rstrip("-")
    return slug


def default_run_id(title: str) -> str:
    slug = slugify(title)
    if slug:
        return slug
    return datetime.now(UTC).strftime("%Y%m%d-%H%M%S")


def resolve_run_dir(run_id: str, out: str | None) -> Path:
    if out:
        path = Path(out)
        if not path.is_absolute():
            path = _REPO_ROOT / path
        return path
    return _REPO_ROOT / "output" / "Eval" / run_id


def _agent_outputs_by_id(outputs: list) -> dict[str, Any]:
    return {o.agent_id.upper(): o for o in outputs}


def _resolve_deconstruction(
    news,
    run_dir: Path,
    *,
    provider: str | None,
    deconstruction_file: Path | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load or run A0; return (deconstruction object, full A0 payload for disk)."""
    if deconstruction_file is not None and deconstruction_file.is_file():
        dec = load_deconstruction_from_file(deconstruction_file)
        payload = {
            "agent": "A0",
            "news": news_to_dict(news),
            "deconstruction": annotate_fragment_ids(dec),
            "errors": [],
        }
        return dec, payload

    cached = run_dir / "facts.json"
    if cached.is_file():
        dec = load_deconstruction_from_file(cached)
        return dec, json.loads(cached.read_text(encoding="utf-8"))

    payload = run_deconstruct(news, provider=provider)
    dec = payload.get("deconstruction")
    if not isinstance(dec, dict) or not dec:
        raise ValueError("deconstruction failed — no valid deconstruction object")
    return dec, payload


def write_eval_bundle(
    run_dir: Path,
    run_id: str,
    news,
    outputs: list,
    errors: list[dict],
    retrieve_result: dict[str, Any],
    *,
    deconstruction_payload: dict[str, Any] | None = None,
    expansion_payload: dict[str, Any] | None = None,
    agents_payload: dict[str, Any] | None = None,
    persona_payloads: dict[str, dict[str, Any]] | None = None,
) -> None:
    """Write all Eval artifacts under run_dir."""
    run_dir.mkdir(parents=True, exist_ok=True)
    agents_dir = run_dir / "agents"
    agents_dir.mkdir(exist_ok=True)
    personas_dir = run_dir / "personas"

    (run_dir / "reality.json").write_text(
        json.dumps(news_to_dict(news), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_dir / "reality.md").write_text(_format_reality_body(run_id, news), encoding="utf-8")

    if deconstruction_payload is not None:
        (run_dir / "facts.json").write_text(
            json.dumps(deconstruction_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (run_dir / "facts.md").write_text(
            render_deconstruction_md(deconstruction_payload, run_id=run_id),
            encoding="utf-8",
        )
    if expansion_payload is not None:
        (run_dir / "bridges.json").write_text(
            json.dumps(expansion_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if agents_payload is not None:
        (run_dir / "agents.json").write_text(
            json.dumps(agents_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
    if persona_payloads:
        personas_dir.mkdir(exist_ok=True)
        for persona_id, payload in persona_payloads.items():
            persona_dir = personas_dir / persona_id
            persona_dir.mkdir(parents=True, exist_ok=True)
            (persona_dir / "persona-pipeline.json").write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
    (run_dir / "errors.md").write_text(_format_errors(errors), encoding="utf-8")
    (run_dir / "candidates.json").write_text(
        json.dumps(retrieve_result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_dir / "candidates.md").write_text(
        _format_candidates_markdown(run_id, retrieve_result.get("candidates", [])),
        encoding="utf-8",
    )
    if persona_payloads:
        run_persona_ids = list(persona_payloads.keys())
    else:
        run_persona_ids = [o.agent_id for o in outputs]
    (run_dir / "run.md").write_text(
        _format_run_index(run_id, errors, persona_ids=run_persona_ids),
        encoding="utf-8",
    )

    per_agent_by_id = {
        str(entry["agent_id"]).upper(): entry
        for entry in retrieve_result.get("per_agent", [])
    }
    by_output = _agent_outputs_by_id(outputs)
    output_ids = [o.agent_id.upper() for o in outputs]
    ordered_ids = [aid.upper() for aid in _PSEUDO_ORDER if aid.upper() in by_output]
    ordered_ids.extend(aid for aid in output_ids if aid not in ordered_ids)
    for agent_key in ordered_ids:
        output = by_output.get(agent_key)
        if output is None:
            continue
        agent_path = agents_dir / f"{output.agent_id}.md"
        agent_path.write_text(
            _format_agent_markdown(run_id, output.agent_id, output, per_agent_by_id.get(agent_key)),
            encoding="utf-8",
        )


def _resolve_expansion(
    deconstruction: dict[str, Any],
    run_dir: Path,
    *,
    provider: str | None,
) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    """Load cached P-Expand payload or run the shared objective expansion pass."""
    cached = run_dir / "bridges.json"
    if cached.is_file():
        payload = json.loads(cached.read_text(encoding="utf-8"))
        expansion = payload.get("expansion")
        return expansion if isinstance(expansion, dict) else None, payload

    payload = run_expansion(deconstruction, provider=provider)
    expansion = payload.get("expansion")
    return expansion if isinstance(expansion, dict) else None, payload


def _persona_result_to_agent(result) -> dict[str, Any]:
    payload = pipeline_result_to_dict(result)
    pseudos = payload.get("pseudos") or []
    agent: dict[str, Any] = {
        "agent_id": result.persona_id,
        "persona_name": result.persona_id,
        "role": "persona",
        "pseudos": pseudos,
        "text": str(pseudos[0].get("text", "")) if pseudos else "",
        "warnings": list(result.warnings or []),
    }
    if payload.get("search_units"):
        agent["search_units"] = payload["search_units"]
    if payload.get("fragment_ladders"):
        agent["fragment_ladders"] = payload["fragment_ladders"]
    return agent


def _persona_result_to_output(result) -> AgentOutput:
    return AgentOutput(
        agent_id=result.persona_id,
        persona_name=result.persona_id,
        role="persona",
        pseudos=list(result.pseudos or []),
        warnings=list(result.warnings or []),
        error=result.error,
    )


async def run_eval_pipeline(
    news,
    *,
    provider: str | None = None,
    deconstruction: dict[str, Any],
    run_dir: Path | None = None,
    run_options: RunOptions | None = None,
) -> tuple[list, list[dict], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, dict[str, Any]]]:
    """Run P-Expand → N persona search-units → retrieve.

    *run_options* applies dev-loop shortcuts (persona slice / skip expand /
    judge top-k) without touching the underlying function signatures.
    """
    options = run_options or RunOptions()

    if options.skip_expand:
        _progress("[stage 3/6] expand skipped (--skip-expand)")
        expansion, expansion_payload = None, {"expansion": None, "errors": [], "warnings": [], "skipped": True}
    else:
        stage_start = time.perf_counter()
        _progress("[stage 3/6] expand start")
        expansion, expansion_payload = _resolve_expansion(
            deconstruction,
            run_dir or (_REPO_ROOT / "output" / "Eval" / "_tmp"),
            provider=provider,
        )
        _progress(f"[stage 3/6] expand done ({_elapsed(stage_start)})")

    outputs: list[AgentOutput] = []
    errors: list[dict[str, Any]] = []
    agents_list: list[dict[str, Any]] = []
    persona_payloads: dict[str, dict[str, Any]] = {}

    persona_ids = list_persona_ids()
    if options.persona_limit is not None:
        persona_ids = persona_ids[: options.persona_limit]
    stage_start = time.perf_counter()
    _progress(f"[stage 4/6] persona start total={len(persona_ids)}")
    for idx, persona_id in enumerate(persona_ids, start=1):
        persona_start = time.perf_counter()
        _progress(f"[persona {idx}/{len(persona_ids)}] {persona_id} start")
        result = await run_persona_pipeline(
            persona_id,
            deconstruction,
            provider=provider,
            expansion=expansion,
        )
        _progress(f"[persona {idx}/{len(persona_ids)}] {persona_id} done ({_elapsed(persona_start)})")
        payload = pipeline_result_to_dict(result)
        persona_payloads[persona_id] = payload
        outputs.append(_persona_result_to_output(result))
        if result.error or not result.pseudos:
            errors.append({"agent_id": persona_id, "message": result.error or "no pseudos"})
            continue
        agents_list.append(_persona_result_to_agent(result))

    _progress(f"[stage 4/6] persona done ({_elapsed(stage_start)})")

    stage_start = time.perf_counter()
    _progress("[stage 5/6] retrieve start")
    retrieve_result = retrieve_from_agents(agents_list, errors, top_k=options.judge_topk)
    _progress(f"[stage 5/6] retrieve done ({_elapsed(stage_start)})")
    agents_payload = {"agents": agents_list, "errors": errors}
    return outputs, errors, retrieve_result, expansion_payload, agents_payload, persona_payloads


async def _run_cli(args: argparse.Namespace) -> int:
    news_path = Path(args.news_file)
    if not news_path.is_file():
        print(f"error: news file not found: {news_path}", file=sys.stderr)
        return 2

    stage_start = time.perf_counter()
    _progress("[stage 1/6] load news start")
    news = load_news_from_file(news_path)
    _progress(f"[stage 1/6] load news done ({_elapsed(stage_start)})")
    run_id = (args.run_id or "").strip() or default_run_id(news.title)
    run_dir = resolve_run_dir(run_id, args.out)

    run_options = RunOptions(
        persona_limit=args.personas,
        skip_expand=args.skip_expand,
        judge_topk=args.judge_topk,
        force=args.force,
    )
    if run_dir.is_dir() and any(run_dir.iterdir()) and not run_options.force:
        print(
            f"error: run dir already has output: {run_dir} (use --force to overwrite)",
            file=sys.stderr,
        )
        return 2

    decon_path = Path(args.deconstruction_file) if args.deconstruction_file else None
    if decon_path and not decon_path.is_absolute():
        decon_path = _REPO_ROOT / decon_path

    stage_start = time.perf_counter()
    _progress("[stage 2/6] deconstruct start")
    deconstruction, decon_payload = _resolve_deconstruction(
        news,
        run_dir,
        provider=args.provider,
        deconstruction_file=decon_path,
    )
    _progress(f"[stage 2/6] deconstruct done ({_elapsed(stage_start)})")

    outputs, errors, retrieve_result, expansion_payload, agents_payload, persona_payloads = await run_eval_pipeline(
        news,
        provider=args.provider,
        deconstruction=deconstruction,
        run_dir=run_dir,
        run_options=run_options,
    )
    stage_start = time.perf_counter()
    _progress(f"[stage 6/6] write outputs -> {run_dir} start")
    write_eval_bundle(
        run_dir,
        run_id,
        news,
        outputs,
        errors,
        retrieve_result,
        deconstruction_payload=decon_payload,
        expansion_payload=expansion_payload,
        agents_payload=agents_payload,
        persona_payloads=persona_payloads,
    )
    _progress(f"[stage 6/6] write outputs -> {run_dir} done ({_elapsed(stage_start)})")
    print(f"Wrote {run_dir.resolve()}/", file=sys.stderr)

    successes = sum(1 for o in outputs if o.pseudos and not o.error)
    if outputs and successes == 0:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run eval pipeline: news → agents → retrieve → output/Eval/{run_id}/.",
    )
    parser.add_argument(
        "--news-file",
        required=True,
        help="Path to news JSON (title and description required).",
    )
    parser.add_argument(
        "--run-id",
        help="Eval run slug (default: slugified title or UTC timestamp).",
    )
    parser.add_argument(
        "--out",
        help="Run output directory (default: output/Eval/{run_id}).",
    )
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider override (default: DEFAULT_LLM_PROVIDER from .env).",
    )
    parser.add_argument(
        "--deconstruction-file",
        help="Pre-built facts.json (skip A0 if set or if cached in run dir).",
    )
    parser.add_argument(
        "--personas",
        type=int,
        default=None,
        metavar="N",
        help="Dev shortcut: only run the first N personas (default: all 12).",
    )
    parser.add_argument(
        "--skip-expand",
        action="store_true",
        help="Dev shortcut: skip the P-Expand stage (personas run without expansion bridges).",
    )
    parser.add_argument(
        "--judge-topk",
        type=int,
        default=2,
        metavar="K",
        help="Retrieve top-k per pseudo (default: 2).",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing non-empty run dir instead of erroring out.",
    )
    args = parser.parse_args(argv)

    try:
        return asyncio.run(_run_cli(args))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
