"""run_phase38_eval.py · Phase 3.8 eval: news → A0 → expansion → persona → retrieve.

Writes under output/Eval/phase3.8/{run_id}/. English in, English out; verifies no CJK
residue in pipeline text artifacts after a successful run.
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.agents import load_news_from_file, news_to_dict, pseudo_to_dict
from scripts.deconstruct import run_deconstruct, write_outputs as write_decon_outputs
from scripts.eval_batch_manifest import news_file_for_run_id
from scripts.lib.paths import repo_root
from scripts.objective_expansion import run_expansion, write_outputs as write_expansion_outputs
from scripts.personas import list_persona_ids, pipeline_result_to_dict, run_persona_pipeline
from scripts.retrieve import retrieve_from_agents
from scripts.run_eval import _format_reality_body, slugify

PHASE38 = repo_root() / "output" / "Eval" / "phase3.8"

_CJK_RE = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\uf900-\ufaff]")


def phase38_run_dir(run_id: str) -> Path:
    return PHASE38 / run_id


def contains_cjk(text: str) -> bool:
    return bool(_CJK_RE.search(text))


def _collect_strings(obj: Any, *, skip_keys: frozenset[str] | None = None) -> list[str]:
    """Flatten string leaves from JSON-like structures."""
    skip = skip_keys or frozenset()
    out: list[str] = []
    if isinstance(obj, str):
        out.append(obj)
    elif isinstance(obj, dict):
        for key, val in obj.items():
            if key in skip:
                continue
            out.extend(_collect_strings(val, skip_keys=skip))
    elif isinstance(obj, list):
        for item in obj:
            out.extend(_collect_strings(item, skip_keys=skip_keys))
    return out


def find_cjk_violations(run_dir: Path) -> list[str]:
    """Scan key phase 3.8 artifacts for Chinese/CJK residue."""
    violations: list[str] = []
    targets = [
        "reality.json",
        "reality-deconstructed.json",
        "reality-expanded.json",
        "retrieve.json",
    ]
    for name in targets:
        path = run_dir / name
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        for text in _collect_strings(data, skip_keys=frozenset({"url"})):
            if contains_cjk(text):
                snippet = text[:80].replace("\n", " ")
                violations.append(f"{name}: {snippet!r}")
                break

    personas_dir = run_dir / "personas"
    if personas_dir.is_dir():
        for pipeline_path in personas_dir.glob("*/persona-pipeline.json"):
            try:
                data = json.loads(pipeline_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            for text in _collect_strings(data):
                if contains_cjk(text):
                    violations.append(f"{pipeline_path.relative_to(run_dir)}: CJK in persona output")
                    break
    return violations


def persona_pipeline_to_agent(persona_id: str, pseudos: list) -> dict[str, Any]:
    return {
        "agent_id": persona_id,
        "persona_name": persona_id,
        "role": "persona",
        "pseudos": [pseudo_to_dict(p) for p in pseudos],
        "text": pseudos[0].text if pseudos else "",
        "warnings": [],
    }


def _load_expansion_payload(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    expansion = data.get("expansion")
    return expansion if isinstance(expansion, dict) else None


async def run_persona_for_run(
    persona_id: str,
    deconstruction: dict[str, Any],
    expansion: dict[str, Any] | None,
    persona_dir: Path,
    *,
    provider: str | None,
    skip_existing: bool,
) -> tuple[dict[str, Any] | None, str | None]:
    persona_dir.mkdir(parents=True, exist_ok=True)
    pipeline_path = persona_dir / "persona-pipeline.json"
    if skip_existing and pipeline_path.is_file():
        data = json.loads(pipeline_path.read_text(encoding="utf-8"))
        if data.get("error"):
            return None, str(data["error"])
        from scripts.agents import PseudoSegment

        pseudos = [
            PseudoSegment(
                id=str(p["id"]),
                text=str(p["text"]),
                source=p.get("source") or {},
                warnings=list(p.get("warnings") or []),
                fit=p.get("fit"),
            )
            for p in data.get("pseudos") or []
            if isinstance(p, dict)
        ]
        if pseudos:
            return persona_pipeline_to_agent(persona_id, pseudos), None

    result = await run_persona_pipeline(
        persona_id,
        deconstruction,
        provider=provider,
        expansion=expansion,
    )
    pipeline_path.write_text(
        json.dumps(pipeline_result_to_dict(result), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    if result.error or not result.pseudos:
        return None, result.error or "no pseudos"
    return persona_pipeline_to_agent(persona_id, result.pseudos), None


async def run_phase38_for_news(
    run_id: str,
    news_path: Path,
    persona_ids: list[str],
    *,
    provider: str | None,
    skip_existing: bool,
    skip_decon: bool,
    skip_expansion: bool,
    skip_personas: bool,
    skip_retrieve: bool,
) -> dict[str, Any]:
    news = load_news_from_file(news_path)
    out_dir = phase38_run_dir(run_id)
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "reality.json").write_text(
        json.dumps(news_to_dict(news), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (out_dir / "reality.md").write_text(_format_reality_body(run_id, news), encoding="utf-8")

    decon_path = out_dir / "reality-deconstructed.json"
    if skip_existing and decon_path.is_file():
        decon_payload = json.loads(decon_path.read_text(encoding="utf-8"))
    elif skip_decon and decon_path.is_file():
        decon_payload = json.loads(decon_path.read_text(encoding="utf-8"))
    else:
        decon_payload = run_deconstruct(news, provider=provider)
        write_decon_outputs(decon_payload, out_dir, run_id=run_id)

    deconstruction = decon_payload.get("deconstruction")
    if not isinstance(deconstruction, dict) or not deconstruction:
        raise ValueError("A0 deconstruction missing or invalid")

    expansion_path = out_dir / "reality-expanded.json"
    expansion: dict[str, Any] | None = None
    if skip_existing and expansion_path.is_file():
        expansion = _load_expansion_payload(expansion_path)
    elif skip_expansion and expansion_path.is_file():
        expansion = _load_expansion_payload(expansion_path)
    else:
        expand_payload = run_expansion(deconstruction, provider=provider)
        write_expansion_outputs(expand_payload, out_dir)
        expansion = expand_payload.get("expansion") if isinstance(
            expand_payload.get("expansion"), dict
        ) else None

    agents: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []

    if not skip_personas:
        for persona_id in persona_ids:
            persona_dir = out_dir / "personas" / persona_id
            agent_row, err = await run_persona_for_run(
                persona_id,
                deconstruction,
                expansion,
                persona_dir,
                provider=provider,
                skip_existing=skip_existing,
            )
            if err or agent_row is None:
                errors.append({"agent_id": persona_id, "message": err or "failed"})
                continue
            agents.append(agent_row)

    retrieve_result: dict[str, Any] | None = None
    if not skip_retrieve and agents:
        retrieve_result = retrieve_from_agents(agents, errors)
        (out_dir / "agents.json").write_text(
            json.dumps({"agents": agents, "errors": errors}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (out_dir / "retrieve.json").write_text(
            json.dumps(retrieve_result, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    cjk_violations = find_cjk_violations(out_dir)

    meta = {
        "run_id": run_id,
        "news_file": str(news_path),
        "persona_ids": persona_ids,
        "agent_count": len(agents),
        "errors": errors,
        "cjk_violations": cjk_violations,
        "english_ok": not cjk_violations,
        "candidate_count": (retrieve_result or {}).get("meta", {}).get("candidate_count"),
        "finished_at": datetime.now(UTC).isoformat(),
    }
    (out_dir / "phase38-run-meta.json").write_text(
        json.dumps(meta, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return meta


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Phase 3.8 eval: news → A0 → expansion → persona (neutral+toned) → retrieve.",
    )
    parser.add_argument("--run-id", help="Eval run_id (basename under tests/eval_news/).")
    parser.add_argument("--news-file", type=Path, help="News JSON path (overrides --run-id lookup).")
    parser.add_argument(
        "--personas",
        nargs="*",
        help="Persona ids (default: The-Ruler for smoke; use --all-personas for full 12).",
    )
    parser.add_argument("--all-personas", action="store_true", help="Run all 12 personas.")
    parser.add_argument("--provider", choices=["mimo", "deepseek"])
    parser.add_argument("--no-skip-existing", action="store_true")
    parser.add_argument("--skip-decon", action="store_true")
    parser.add_argument("--skip-expansion", action="store_true")
    parser.add_argument("--skip-personas", action="store_true")
    parser.add_argument("--skip-retrieve", action="store_true")
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Only scan output/Eval/phase3.8/{run_id} for CJK residue.",
    )
    args = parser.parse_args(argv)

    if not args.run_id and not args.news_file:
        print("error: --run-id or --news-file required", file=sys.stderr)
        return 2

    run_id = args.run_id or slugify(load_news_from_file(args.news_file).title)
    news_path = args.news_file or news_file_for_run_id(run_id)

    if args.verify_only:
        violations = find_cjk_violations(phase38_run_dir(run_id))
        if violations:
            for v in violations:
                print(f"CJK: {v}", file=sys.stderr)
            return 1
        print(f"OK: no CJK in {phase38_run_dir(run_id)}", file=sys.stderr)
        return 0

    if args.all_personas:
        persona_ids = list_persona_ids()
    elif args.personas:
        persona_ids = list(args.personas)
    else:
        persona_ids = ["The-Ruler"]

    try:
        meta = asyncio.run(
            run_phase38_for_news(
                run_id,
                news_path,
                persona_ids,
                provider=args.provider,
                skip_existing=not args.no_skip_existing,
                skip_decon=args.skip_decon,
                skip_expansion=args.skip_expansion,
                skip_personas=args.skip_personas,
                skip_retrieve=args.skip_retrieve,
            )
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    print(
        f"Wrote {phase38_run_dir(run_id).resolve()} · "
        f"agents={meta.get('agent_count')} candidates={meta.get('candidate_count')} "
        f"english_ok={meta.get('english_ok')}",
        file=sys.stderr,
    )
    if meta.get("errors"):
        print(f"errors: {meta['errors']}", file=sys.stderr)
    if meta.get("cjk_violations"):
        for v in meta["cjk_violations"]:
            print(f"CJK violation: {v}", file=sys.stderr)
        return 1
    if meta.get("agent_count", 0) == 0:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
