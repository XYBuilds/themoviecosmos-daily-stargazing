"""audit_phase38_pilot.py · Automated checks for Phase 3.8.6 firewall pilot audit."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.deconstruct import _collect_forbidden_keys  # noqa: E402
from scripts.objective_expansion import _LENS_FRAMED_SNIPPETS  # noqa: E402

_FORBIDDEN_A0 = frozenset(
    {
        "skeleton",
        "load_bearing",
        "seeds",
        "resonance_type",
        "hypernym",
        "hypernyms",
        "alternatives",
        "valence",
    }
)
_INERT = frozenset({"tags", "geocode", "coordinates", "scale", "scene_archetype"})


def _collect_a0_violations(obj: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_lower = str(key).lower()
            if key in _FORBIDDEN_A0 or key_lower in _FORBIDDEN_A0:
                found.append(f"forbidden:{path}.{key}" if path else f"forbidden:{key}")
            if key in _INERT or key_lower in _INERT:
                found.append(f"inert:{path}.{key}" if path else f"inert:{key}")
            child = f"{path}.{key}" if path else str(key)
            found.extend(_collect_a0_violations(value, child))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            found.extend(_collect_a0_violations(item, f"{path}[{idx}]"))
    return found


def audit_run(run_dir: Path) -> dict[str, Any]:
    report: dict[str, Any] = {"run_dir": str(run_dir.resolve())}

    decon_path = run_dir / "reality-deconstructed.json"
    decon = json.loads(decon_path.read_text(encoding="utf-8"))
    deconstruction = decon.get("deconstruction") or {}
    a0_violations = _collect_a0_violations(deconstruction)
    report["a0"] = {
        "forbidden_or_inert_keys": a0_violations,
        "pass": not a0_violations,
    }

    exp_path = run_dir / "reality-expanded.json"
    expansion = json.loads(exp_path.read_text(encoding="utf-8"))
    lens_hypernyms: list[str] = []
    forbidden_exp_keys: list[str] = []
    for el in (expansion.get("expansion") or {}).get("elements") or []:
        if not isinstance(el, dict):
            continue
        for bad_key in ("lens", "alternatives", "valence"):
            if bad_key in el:
                forbidden_exp_keys.append(f"{el.get('element_id')}:{bad_key}")
        for hyper in el.get("hypernyms") or []:
            hl = str(hyper).lower()
            if any(snippet in hl for snippet in _LENS_FRAMED_SNIPPETS):
                lens_hypernyms.append(str(hyper))
    report["expansion"] = {
        "lens_framed_hypernyms": lens_hypernyms,
        "forbidden_keys_in_elements": forbidden_exp_keys,
        "validation_warnings": expansion.get("validation_warnings") or [],
        "pass": not lens_hypernyms and not forbidden_exp_keys,
    }

    personas_dir = run_dir / "personas"
    success: list[str] = []
    failed: list[str] = []
    neutral_count = 0
    toned_count = 0
    lens_in_neutral: list[str] = []
    toned_missing_anchor: list[str] = []
    for persona_dir in sorted(personas_dir.iterdir()):
        if not persona_dir.is_dir():
            continue
        pid = persona_dir.name
        pipeline_path = persona_dir / "persona-pipeline.json"
        if not pipeline_path.is_file():
            failed.append(pid)
            continue
        data = json.loads(pipeline_path.read_text(encoding="utf-8"))
        if data.get("error") or not data.get("pseudos"):
            failed.append(pid)
            continue
        success.append(pid)
        for pseudo in data.get("pseudos") or []:
            if not isinstance(pseudo, dict):
                continue
            src = pseudo.get("source") or {}
            role = src.get("channel_role")
            pseudo_id = str(pseudo.get("id", "?"))
            if role == "neutral":
                neutral_count += 1
                prov = src.get("provenance_layers") or []
                if "lens" in prov:
                    lens_in_neutral.append(f"{pid}/{pseudo_id}: provenance_layers")
                for term in src.get("terms") or []:
                    if isinstance(term, dict) and term.get("provenance") == "lens":
                        lens_in_neutral.append(f"{pid}/{pseudo_id}: lens term")
            elif role == "toned":
                toned_count += 1

    meta_path = run_dir / "phase38-run-meta.json"
    run_errors = []
    if meta_path.is_file():
        run_errors = (json.loads(meta_path.read_text(encoding="utf-8"))).get("errors") or []
    for err in run_errors:
        msg = str(err.get("message", ""))
        aid = str(err.get("agent_id", ""))
        if "hypernym anchor" in msg:
            toned_missing_anchor.append(f"{aid}: {msg[:120]}")
        if "neutral pseudo must not contain lens" in msg:
            lens_in_neutral.append(f"{aid}: assembly rejected — {msg[:100]}")

    retrieve_path = run_dir / "retrieve.json"
    retrieve = json.loads(retrieve_path.read_text(encoding="utf-8"))
    candidates = retrieve.get("candidates") or []
    annotations = [c for c in candidates if c.get("quality_candidate")]
    max_neutral_hits = max((c.get("neutral_hits", 0) for c in candidates), default=0)
    neutral_total = next(
        (c.get("neutral_total") for c in candidates if c.get("neutral_total")),
        neutral_count,
    )
    # Collision diagnostic: neutral union contributes one binary vote (neutral_vote=1), not per-persona.
    union_vote_ok = any(
        "neutral_vote=1" in str(c.get("quality_reason", "")) for c in annotations
    )

    report["neutral_channel"] = {
        "personas_ok": len(success),
        "personas_failed": len(failed),
        "failed_ids": failed,
        "neutral_pseudo_count": neutral_count,
        "toned_pseudo_count": toned_count,
        "lens_in_neutral": lens_in_neutral,
        "max_neutral_hits_on_candidate": max_neutral_hits,
        "neutral_total_denominator": neutral_total,
        "collision_union_one_vote": union_vote_ok,
        "pass": len(success) == 12 and neutral_count == len(success) and not lens_in_neutral,
    }
    report["toned_anchor"] = {
        "missing_anchor_errors": toned_missing_anchor,
        "pass": not toned_missing_anchor and toned_count > 0,
    }
    report["retrieve"] = {
        "candidate_count": len(candidates),
        "convergence_annotation_count": len(annotations),
        "meta": retrieve.get("meta") or {},
    }
    report["firewall"] = {
        "assembly_errors": run_errors,
        "pass": len(run_errors) == 0,
    }
    return report


def render_markdown(report: dict[str, Any], run_id: str) -> str:
    def status(pass_: bool) -> str:
        return "PASS (auto)" if pass_ else "FAIL / NEEDS EYEBALL"

    lines = [
        f"# Phase 3.8.6 Pilot Audit · `{run_id}`",
        "",
        f"**Output path:** `{report['run_dir']}`",
        "",
        "Automated checks below; **five firewall items require human sign-off** before Go → 3.8.7.",
        "",
        "## Summary table",
        "",
        "| # | Audit item | Automated | Human eyeball |",
        "|---|------------|-----------|---------------|",
    ]

    a0 = report["a0"]
    exp = report["expansion"]
    neu = report["neutral_channel"]
    toned = report["toned_anchor"]
    fw = report["firewall"]

    lines.extend(
        [
            f"| 1 | A0 verbatim — no hypernym/inert leak | "
            f"{'No forbidden/inert keys' if a0['pass'] else a0['forbidden_or_inert_keys']} | "
            f"Confirm surface text matches news; no interpretive framing |",
            f"| 2 | Expansion — hypernym touchstone, no lens framing | "
            f"{'Clean' if exp['pass'] else 'lens=' + str(exp['lens_framed_hypernyms'])} | "
            f"Read `reality-expanded.json` hypernyms vs news facts |",
            f"| 3 | 12 neutrals = objective floor; collision = 1 vote | "
            f"{neu['neutral_pseudo_count']}/12 neutrals; union_vote={neu['collision_union_one_vote']} "
            f"(neutral_hits diag max={neu['max_neutral_hits_on_candidate']}) | "
            f"Spot-check neutrals have no persona lens; quality_reason is diagnostic only |",
            f"| 4 | Toned hypernym anchor, on-topic | "
            f"{neu['toned_pseudo_count']} toned; anchor errors={len(toned['missing_anchor_errors'])} | "
            f"Read toned pseudos vs news; confirm anchors not decorative |",
            f"| 5 | Firewall — lens fact-entailed; hypernym/lens not mixed | "
            f"Assembly errors={len(fw['assembly_errors'])} | "
            f"Audit `alt-pool-overlay.json` per persona: lens terms entailed? layers separated? |",
            "",
            "## Detail",
            "",
            "### 1 · A0 verbatim",
            f"- Status: **{status(a0['pass'])}**",
            f"- Violations: `{a0['forbidden_or_inert_keys'] or 'none'}`",
            "",
            "### 2 · Expansion pass",
            f"- Status: **{status(exp['pass'])}**",
            f"- Lens-framed hypernyms: `{exp['lens_framed_hypernyms'] or 'none'}`",
            f"- Validation warnings: `{exp['validation_warnings'] or 'none'}`",
            "",
            "### 3 · Neutral channel + collision",
            f"- Status: **{status(neu['pass'])}**",
            f"- Personas OK: {neu['personas_ok']}/12 · failed: `{neu['failed_ids']}`",
            f"- Neutral pseudos: {neu['neutral_pseudo_count']} · toned: {neu['toned_pseudo_count']}",
            f"- Max neutral_hits diagnostic on any candidate: {neu['max_neutral_hits_on_candidate']} "
            f"(union vote binary: {neu['collision_union_one_vote']})",
            f"- Convergence annotations: {report['retrieve']['convergence_annotation_count']}",
            "",
            "### 4 · Toned anchors",
            f"- Status: **{status(toned['pass'])}**",
        ]
    )
    if toned["missing_anchor_errors"]:
        lines.append("- Missing anchor errors:")
        for e in toned["missing_anchor_errors"]:
            lines.append(f"  - {e}")
    else:
        lines.append("- No hypernym-anchor assembly errors in successful personas.")

    lines.extend(
        [
            "",
            "### 5 · Firewall (hypernym vs lens)",
            f"- Status: **{status(fw['pass'])}**",
        ]
    )
    if fw["assembly_errors"]:
        lines.append("- Assembly errors (channel_assembly rejected):")
        for e in fw["assembly_errors"]:
            lines.append(f"  - **{e.get('agent_id')}**: {e.get('message')}")
    if neu["lens_in_neutral"]:
        lines.append("- Lens leakage flags:")
        for e in neu["lens_in_neutral"]:
            lines.append(f"  - {e}")

    lines.extend(
        [
            "",
            "## Human checklist (sign each before Go)",
            "",
            "- [ ] **1** A0 fragments are verbatim news spans; no hypernym ladder or inert geocode/scale in decon.",
            "- [ ] **2** Expansion hypernyms are objective (A2/A4 agree); no cinematic/lens vocabulary.",
            "- [ ] **3** Each persona has exactly one neutral pseudo (surface+hypernym only); "
            "retrieve counts neutral union as **one** deduped vote.",
            "- [ ] **4** Each toned pseudo includes a real hypernym anchor and stays on the news topic.",
            "- [ ] **5** Lens alternatives in alt-pool are fact-entailed; hypernym and lens provenance not mixed in neutrals.",
            "",
            "_Generated by `scripts/audit_phase38_pilot.py`._",
        ]
    )
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Audit Phase 3.8 pilot run artifacts.")
    parser.add_argument("--run-id", required=True)
    parser.add_argument(
        "--write-md",
        action="store_true",
        help="Write pilot-audit.md into the run directory.",
    )
    args = parser.parse_args(argv)

    run_dir = _REPO_ROOT / "output" / "Eval" / "phase3.8" / args.run_id
    if not run_dir.is_dir():
        print(f"error: run dir not found: {run_dir}", file=sys.stderr)
        return 2

    report = audit_run(run_dir)
    print(json.dumps(report, ensure_ascii=False, indent=2))

    if args.write_md:
        md_path = run_dir / "pilot-audit.md"
        md_path.write_text(render_markdown(report, args.run_id), encoding="utf-8")
        print(f"Wrote {md_path}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
