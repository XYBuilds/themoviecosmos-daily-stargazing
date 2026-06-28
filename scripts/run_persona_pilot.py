"""run_persona_pilot.py · Phase 3.7 single-run persona pilot (decon → persona → retrieve).

Reads neutral A0 decon (typically phase3.6, read-only), runs alt-creator + screenwriter for one
persona, retrieves movie candidates, writes artifacts under output/Eval/phase3.7/{run_id}/.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.agents import load_deconstruction_from_file, pseudo_to_dict
from scripts.lib.paths import repo_root
from scripts.rewrite import (
    build_alt_pool_overlay,
    pipeline_result_to_dict,
    run_persona_pipeline,
)
from scripts.retrieve import retrieve_from_agents

DEFAULT_DECON = (
    repo_root()
    / "output"
    / "Eval"
    / "phase3.6"
    / "04-celebrity-scandal"
    / "reality-deconstructed.json"
)
DEFAULT_BASELINE_RETRIEVE = (
    repo_root()
    / "output"
    / "Eval"
    / "phase3.6"
    / "04-celebrity-scandal"
    / "retrieve.json"
)


def _persona_agent_dict(persona_id: str, pseudos: list) -> dict[str, Any]:
    return {
        "agent_id": persona_id,
        "persona_name": persona_id,
        "role": "creative",
        "pseudos": [pseudo_to_dict(p) for p in pseudos],
        "text": pseudos[0].text if pseudos else "",
        "warnings": [],
    }


def _format_persona_agent_md(
    run_id: str,
    persona_id: str,
    pseudos: list,
    per_agent_entry: dict[str, Any] | None,
) -> str:
    lines = [
        f"# {persona_id} · Persona pilot · {run_id}",
        "",
        "## Pseudos (+ fit)",
        "",
    ]
    hits_by_id: dict[str, list] = {}
    if per_agent_entry:
        for row in per_agent_entry.get("pseudos") or []:
            pid = str(row.get("pseudo_id", ""))
            hits_by_id[pid] = row.get("hits") or []

    for p in pseudos:
        fit_str = f"{p.fit:.2f}" if p.fit is not None else "—"
        frags = (p.source or {}).get("fragments") or []
        lines.append(f"### {p.id} · fit={fit_str}")
        lines.append(f"- **fragments**: {', '.join(frags)}")
        lines.append("")
        lines.append(p.text)
        lines.append("")
        hits = hits_by_id.get(p.id) or []
        if hits:
            lines.append("#### Retrieve Top-K")
            for hit in hits:
                lines.append(
                    f"- **{hit.get('title')}** (tmdb {hit.get('tmdb_id')}, "
                    f"sim {hit.get('similarity', 0):.4f})"
                )
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def _baseline_a1_summary(baseline_path: Path) -> dict[str, Any]:
    if not baseline_path.is_file():
        return {"available": False}
    data = json.loads(baseline_path.read_text(encoding="utf-8"))
    a1 = next(
        (e for e in data.get("per_agent", []) if str(e.get("agent_id")).upper() == "A1"),
        None,
    )
    if not a1:
        return {"available": False}
    titles: list[str] = []
    for pseudo in a1.get("pseudos") or []:
        for hit in pseudo.get("hits") or []:
            titles.append(str(hit.get("title", "")))
    return {
        "available": True,
        "path": str(baseline_path),
        "candidate_count": len(data.get("candidates") or []),
        "a1_hit_titles": titles,
    }


def _pilot_comparison_notes(
    persona_id: str,
    retrieve_result: dict[str, Any],
    baseline: dict[str, Any],
    overlay: dict[str, Any],
    pseudos: list,
) -> str:
    lines = [
        "# Persona pilot notes",
        "",
        f"- **persona:** {persona_id}",
        f"- **candidates:** {len(retrieve_result.get('candidates') or [])}",
        f"- **raw hits:** {(retrieve_result.get('meta') or {}).get('raw_hit_count')}",
        "",
        "## Alt-pool sample (first 3 elements)",
        "",
    ]
    elements = (overlay.get("alt_pool") or {}).get("elements") or []
    for el in elements[:3]:
        lines.append(f"- `{el.get('element_id')}`: {el.get('original_term')}")
        for alt in el.get("alternatives") or []:
            lines.append(f"  - [{alt.get('valence')}] {alt.get('term')}")
    lines.append("")
    lines.append("## Pseudos · fit")
    lines.append("")
    for p in pseudos:
        fit_str = f"{p.fit:.2f}" if p.fit is not None else "—"
        lines.append(f"- {p.id}: fit={fit_str}")
    lines.append("")
    lines.append("## vs A1 baseline (phase3.6, read-only)")
    lines.append("")
    if baseline.get("available"):
        lines.append(f"- A1 retrieve path: `{baseline.get('path')}`")
        lines.append(f"- A1 phase3.6 aggregate candidates: {baseline.get('candidate_count')}")
        lines.append("- A1 hit titles (all pseudos):")
        for t in baseline.get("a1_hit_titles") or []:
            if t:
                lines.append(f"  - {t}")
    else:
        lines.append("- (baseline retrieve.json not found)")
    lines.append("")
    persona_titles: list[str] = []
    for entry in retrieve_result.get("per_agent") or []:
        for pseudo in entry.get("pseudos") or []:
            for hit in pseudo.get("hits") or []:
                persona_titles.append(str(hit.get("title", "")))
    lines.append("## Persona retrieve hit titles")
    lines.append("")
    for t in persona_titles:
        if t:
            lines.append(f"- {t}")
    lines.append("")
    lines.append(
        "_Steering check: Ruler should skew toward order/crime/scandal/legal containment "
        "vs A1 neutral faithful recap._"
    )
    return "\n".join(lines) + "\n"


async def run_pilot(
    *,
    persona_id: str,
    decon_path: Path,
    out_dir: Path,
    provider: str | None,
    baseline_retrieve: Path,
) -> int:
    deconstruction = load_deconstruction_from_file(decon_path)
    result = await run_persona_pipeline(
        persona_id,
        deconstruction,
        provider=provider,
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    overlay_dict = build_alt_pool_overlay(result.overlay)
    (out_dir / "alt-pool-overlay.json").write_text(
        json.dumps(overlay_dict, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    pipeline_payload = pipeline_result_to_dict(result)
    (out_dir / "persona-pipeline.json").write_text(
        json.dumps(pipeline_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    if result.error or not result.pseudos:
        err_path = out_dir / "errors.md"
        err_path.write_text(
            f"# Pilot error\n\n{result.error or 'no pseudos produced'}\n",
            encoding="utf-8",
        )
        print(f"error: {result.error or 'no pseudos'}", file=sys.stderr)
        return 1

    agent_row = _persona_agent_dict(persona_id, result.pseudos)
    agents_payload = {"agents": [agent_row], "errors": []}
    (out_dir / "agents.json").write_text(
        json.dumps(agents_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    retrieve_result = retrieve_from_agents(agents_payload["agents"], agents_payload["errors"])
    (out_dir / "retrieve.json").write_text(
        json.dumps(retrieve_result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    per_agent_by_id = {
        str(e["agent_id"]): e for e in retrieve_result.get("per_agent", [])
    }
    agents_dir = out_dir / "agents"
    agents_dir.mkdir(exist_ok=True)
    (agents_dir / f"{persona_id}.md").write_text(
        _format_persona_agent_md(
            out_dir.name,
            persona_id,
            result.pseudos,
            per_agent_by_id.get(persona_id),
        ),
        encoding="utf-8",
    )

    baseline = _baseline_a1_summary(baseline_retrieve)
    (out_dir / "pilot-notes.md").write_text(
        _pilot_comparison_notes(
            persona_id,
            retrieve_result,
            baseline,
            overlay_dict,
            result.pseudos,
        ),
        encoding="utf-8",
    )

    meta = retrieve_result.get("meta") or {}
    print(
        f"Wrote pilot to {out_dir.resolve()} · "
        f"candidates={meta.get('candidate_count')} raw_hits={meta.get('raw_hit_count')}",
        file=sys.stderr,
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run Phase 3.7 persona pilot on one decon.")
    parser.add_argument(
        "--persona-id",
        default="The-Ruler",
        help="Pearson persona_id (default: The-Ruler).",
    )
    parser.add_argument(
        "--deconstruction-file",
        type=Path,
        default=DEFAULT_DECON,
        help="Path to neutral reality-deconstructed.json.",
    )
    parser.add_argument(
        "--out",
        type=Path,
        help="Output directory (default: output/Eval/phase3.7/<run-id>/).",
    )
    parser.add_argument(
        "--run-id",
        default="04-celebrity-scandal",
        help="Eval run_id folder name under phase3.7.",
    )
    parser.add_argument(
        "--baseline-retrieve",
        type=Path,
        default=DEFAULT_BASELINE_RETRIEVE,
        help="phase3.6 retrieve.json for A1 contrast (read-only).",
    )
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider override.",
    )
    args = parser.parse_args(argv)

    out_dir = args.out
    if out_dir is None:
        out_dir = repo_root() / "output" / "Eval" / "phase3.7" / args.run_id

    try:
        return asyncio.run(
            run_pilot(
                persona_id=args.persona_id,
                decon_path=args.deconstruction_file,
                out_dir=out_dir,
                provider=args.provider,
                baseline_retrieve=args.baseline_retrieve,
            )
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
