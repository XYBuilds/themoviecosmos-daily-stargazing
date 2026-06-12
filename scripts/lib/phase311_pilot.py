"""Phase 3.11.6 pilot helpers: single-news A/B audit (design-on vs 3.10 baseline).

Firewall audit dimensions (human Go/No-Go):
  ① fact drift  ② center truthfulness  ③ POV/focal diagnostic distribution
  ④ dual floor  ⑤ funnel dedup/sort  ⑥ OPEN d weak-fit valence optionalization
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from scripts.agents import PseudoSegment, annotate_fragment_ids, load_deconstruction_from_file
from scripts.lib.phase311_pretest import (
    PHASE310_ROOT,
    PHASE311_ROOT,
    GapATarget,
    compare_pool_diff,
    load_alt_pool_overlay,
    load_baseline_neutral_pseudo,
    load_gap_a_samples,
    pool_diff_result_to_dict,
    pseudo_segment_to_dict,
    summarize_center_granularity,
)
from scripts.personas import (
    NEUTRAL_PSEUDO_ID,
    AltPoolOverlay,
    _allowed_proper_noun_phrases,
    _guard_tokens,
    _original_term_for_element,
    _supporting_fragments,
    adr8_dual_floor_enabled,
    collect_entailed_vocabulary,
    known_element_ids,
    load_persona_card,
    validate_adr8_dual_floor,
    validate_adr8_fact_guard,
    validate_adr8_runtime_guards,
    validate_focalized_derivation,
)
from scripts.retrieve import (
    compare_pool_diff_by_channel,
    dedupe_candidates_by_tmdb_id,
    pool_diff_by_channel_to_dict,
)

PILOT_DEFAULT_RUN_ID = "01-grid-outage"
PILOT_MANIFEST = PHASE311_ROOT / "pilot-manifest.json"

# Personas often weak-fit on infrastructure/grid news (OPEN d observation set).
_WEAK_FIT_PERSONAS_GRID = frozenset(
    {"The-Innocent", "The-Jester", "The-Lover", "The-Creator"}
)
_WEAK_FIT_THRESHOLD = 0.55


@dataclass
class PilotRunSpec:
    run_id: str
    personas: list[str]
    gap_a_targets: list[GapATarget] = field(default_factory=list)
    note: str = ""


def _gap_a_targets_for_run(run_id: str) -> list[GapATarget]:
    rows = [r for r in load_gap_a_samples() if str(r.get("run_id")) == run_id]
    return [
        GapATarget(
            tmdb_id=str(r["tmdb_id"]),
            title=str(r.get("title", "")).split(" (")[0],
            human_score=int(r.get("human_score", 2)),
            judge_score=int(r.get("judge_score", 1)),
            judge_resonance_type=r.get("judge_resonance_type"),
            rationale=str(r.get("rationale", "")),
        )
        for r in rows
    ]


def build_default_pilot_manifest() -> dict[str, Any]:
    from scripts.personas import list_persona_ids

    run_id = PILOT_DEFAULT_RUN_ID
    return {
        "version": 1,
        "description": (
            "Phase 3.11.6 single-news pilot: ADR-0008 design-on vs 3.10 baseline "
            "with firewall audit"
        ),
        "runs": [
            {
                "run_id": run_id,
                "note": (
                    "Grid outage · Gap A POV-resonance news · full 12-persona chain"
                ),
                "personas": list_persona_ids(),
                "gap_a_targets": [
                    {
                        "tmdb_id": t.tmdb_id,
                        "title": t.title,
                        "human_score": t.human_score,
                        "judge_score": t.judge_score,
                        "judge_resonance_type": t.judge_resonance_type,
                        "rationale": t.rationale,
                    }
                    for t in _gap_a_targets_for_run(run_id)
                ],
            }
        ],
    }


def load_pilot_manifest(path: Path | None = None) -> dict[str, Any]:
    manifest_path = path or PILOT_MANIFEST
    if manifest_path.is_file():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = build_default_pilot_manifest()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def parse_pilot_runs(manifest: dict[str, Any]) -> list[PilotRunSpec]:
    specs: list[PilotRunSpec] = []
    for row in manifest.get("runs") or []:
        targets = [
            GapATarget(
                tmdb_id=str(t["tmdb_id"]),
                title=str(t.get("title", "")),
                human_score=int(t.get("human_score", 2)),
                judge_score=int(t.get("judge_score", 1)),
                judge_resonance_type=t.get("judge_resonance_type"),
                rationale=str(t.get("rationale", "")),
            )
            for t in row.get("gap_a_targets") or []
        ]
        specs.append(
            PilotRunSpec(
                run_id=str(row["run_id"]),
                personas=[str(p) for p in row.get("personas") or []],
                gap_a_targets=targets,
                note=str(row.get("note", "")),
            )
        )
    return specs


def _center_vocabulary(
    center: str,
    deconstruction: dict[str, Any],
    alt_pool: AltPoolOverlay,
) -> set[str]:
    vocab: set[str] = set()
    term = _original_term_for_element(deconstruction, center)
    if term:
        vocab |= _guard_tokens(term)
    for el in alt_pool.elements:
        if el.element_id != center:
            continue
        vocab |= _guard_tokens(el.original_term)
        for alt in el.alternatives:
            vocab |= _guard_tokens(alt.term)
    return vocab


def audit_center_truthfulness(
    pseudo: PseudoSegment,
    deconstruction: dict[str, Any],
    alt_pool: AltPoolOverlay,
) -> dict[str, Any]:
    """② Center declaration truthfulness: declared center vocabulary appears in text."""
    center = str(pseudo.source.get("center", "")).strip()
    if not center:
        return {"pass": False, "reason": "missing center declaration"}

    center_vocab = _center_vocabulary(center, deconstruction, alt_pool)
    text_tokens = _guard_tokens(pseudo.text)
    overlap = sorted(center_vocab & text_tokens)

    support_vocab: set[str] = set()
    for frag_id in _supporting_fragments(pseudo):
        term = _original_term_for_element(deconstruction, frag_id)
        if term:
            support_vocab |= _guard_tokens(term)
    support_overlap = sorted(support_vocab & text_tokens)

    # Heuristic: center tokens OR alt terms for center must surface; supporting helps.
    center_surfaces = bool(overlap) or any(
        len(w) >= 5 and w in pseudo.text.lower() for w in center_vocab
    )
    stuffing_risk = (
        len(support_overlap) >= 3
        and len(overlap) == 0
        and not center_surfaces
    )

    return {
        "pass": center_surfaces and not stuffing_risk,
        "center": center,
        "center_token_overlap": overlap,
        "support_token_overlap": support_overlap[:8],
        "stuffing_risk": stuffing_risk,
        "reason": (
            "center vocabulary not surfaced in pseudo text"
            if not center_surfaces
            else (
                "supporting fragments dominate without center surfacing"
                if stuffing_risk
                else "ok"
            )
        ),
    }


def _pseudo_objects_from_pipeline(pipeline: dict[str, Any]) -> list[PseudoSegment]:
    out: list[PseudoSegment] = []
    for row in pipeline.get("pseudos") or []:
        if not isinstance(row, dict):
            continue
        src = row.get("source") if isinstance(row.get("source"), dict) else {}
        out.append(
            PseudoSegment(
                str(row.get("id", "")),
                str(row.get("text", "")),
                dict(src),
                list(row.get("warnings") or []),
                fit=row.get("fit"),
            )
        )
    return out


def audit_persona_guards(
    persona_id: str,
    pipeline: dict[str, Any],
    deconstruction: dict[str, Any],
    alt_pool: AltPoolOverlay,
    expansion: dict[str, Any] | None,
) -> dict[str, Any]:
    """Run runtime guards + per-dimension audit for one persona."""
    pseudos = _pseudo_objects_from_pipeline(pipeline)
    legs = [p for p in pseudos if p.id != NEUTRAL_PSEUDO_ID]
    neutral = next((p for p in pseudos if p.id == NEUTRAL_PSEUDO_ID), None)
    persona_card = load_persona_card(persona_id)
    known = known_element_ids(deconstruction)
    vocab = collect_entailed_vocabulary(deconstruction, alt_pool, expansion)
    allowed_proper = _allowed_proper_noun_phrases(deconstruction, alt_pool, expansion)

    guard_errors: list[str] = []
    fact_checks: list[dict[str, Any]] = []
    center_checks: list[dict[str, Any]] = []
    focal_checks: list[dict[str, Any]] = []
    dual_floor_on = adr8_dual_floor_enabled()

    try:
        validate_adr8_runtime_guards(
            legs,
            deconstruction=deconstruction,
            alt_pool=alt_pool,
            known_elements=known,
            expansion=expansion,
            check_hypernym=True,
            check_dual_floor=dual_floor_on,
        )
    except ValueError as exc:
        guard_errors.append(str(exc))

    for pseudo in legs:
        try:
            validate_adr8_fact_guard(
                pseudo,
                deconstruction=deconstruction,
                vocab=vocab,
                allowed_proper_nouns=allowed_proper,
            )
            fact_checks.append({"pseudo_id": pseudo.id, "pass": True})
        except ValueError as exc:
            fact_checks.append(
                {"pseudo_id": pseudo.id, "pass": False, "error": str(exc)}
            )

        center_checks.append(
            {
                "pseudo_id": pseudo.id,
                **audit_center_truthfulness(pseudo, deconstruction, alt_pool),
            }
        )

        focal_warnings = validate_focalized_derivation(
            pseudo, deconstruction, persona_card
        )
        channel = str(pseudo.source.get("channel", "toned"))
        focal_checks.append(
            {
                "pseudo_id": pseudo.id,
                "channel": channel,
                "center": pseudo.source.get("center"),
                "focal": pseudo.source.get("focal"),
                "derivation_warnings": focal_warnings,
                "diagnostic_only": True,
                "pass": True,
            }
        )

    toned_count = sum(1 for p in legs if p.source.get("channel") == "toned")
    focal_count = sum(1 for p in legs if p.source.get("channel") == "focalized")
    dual_floor: dict[str, Any] = {
        "pass": True,
        "toned_count": toned_count,
        "focalized_count": focal_count,
        "neutral_present": neutral is not None,
    }
    if dual_floor_on:
        try:
            validate_adr8_dual_floor(legs)
            dual_floor["pass"] = toned_count >= 1
        except ValueError as exc:
            dual_floor = {
                "pass": False,
                "error": str(exc),
                "toned_count": toned_count,
                "focalized_count": focal_count,
                "neutral_present": neutral is not None,
            }
    else:
        dual_floor["guard_skipped"] = True
        dual_floor["skip_reason"] = "ADR8_DUAL_FLOOR_ENABLED=false"

    return {
        "persona_id": persona_id,
        "guard_hard_failures": guard_errors,
        "fact_drift": {
            "pass": all(c["pass"] for c in fact_checks) and not guard_errors,
            "checks": fact_checks,
        },
        "center_truthfulness": {
            "pass": all(c["pass"] for c in center_checks),
            "checks": center_checks,
        },
        "focalized_derivation": {
            "pass": True,
            "diagnostic_only": True,
            "warning_count": sum(
                len(c.get("derivation_warnings") or []) for c in focal_checks
            ),
            "checks": focal_checks,
        },
        "dual_floor": dual_floor,
        "pipeline_error": pipeline.get("error"),
    }


def audit_neutral_n1_unchanged(
    design_pipeline: dict[str, Any],
    baseline_pipeline: dict[str, Any],
    persona_id: str,
) -> dict[str, Any]:
    """ADR-0008 D3: neutral n1 wording must match 3.10 baseline verbatim."""
    def _n1_text(pipe: dict[str, Any]) -> str | None:
        for row in pipe.get("pseudos") or []:
            if str(row.get("id")) == NEUTRAL_PSEUDO_ID:
                return str(row.get("text", ""))
        return None

    design = _n1_text(design_pipeline)
    baseline = _n1_text(baseline_pipeline)
    if design is None or baseline is None:
        return {
            "persona_id": persona_id,
            "pass": False,
            "reason": "neutral n1 missing in design or baseline",
        }
    unchanged = design.strip() == baseline.strip()
    return {
        "persona_id": persona_id,
        "pass": unchanged,
        "baseline_chars": len(baseline),
        "design_chars": len(design),
        "reason": "ok" if unchanged else "neutral n1 text differs from 3.10 baseline",
    }


def audit_baseline_hits_retained(
    baseline_retrieve: dict[str, Any],
    design_retrieve: dict[str, Any],
) -> dict[str, Any]:
    """④ 3.10 candidate hits should not be lost in design-on pool."""
    def _ids(payload: dict[str, Any]) -> set[int]:
        out: set[int] = set()
        for row in payload.get("candidates") or []:
            if isinstance(row, dict) and row.get("tmdb_id") is not None:
                out.add(int(row["tmdb_id"]))
        return out

    base_ids = _ids(baseline_retrieve)
    design_ids = _ids(design_retrieve)
    lost = sorted(base_ids - design_ids)
    return {
        "pass": not lost,
        "baseline_count": len(base_ids),
        "design_count": len(design_ids),
        "overlap_count": len(base_ids & design_ids),
        "lost_tmdb_ids": lost,
    }


def audit_funnel_reasonable(retrieve_payload: dict[str, Any]) -> dict[str, Any]:
    """⑤ Funnel dedup/sort sanity checks on retrieve meta."""
    meta = retrieve_payload.get("funnel") or retrieve_payload.get("meta") or {}
    candidates = retrieve_payload.get("candidates") or []
    issues: list[str] = []

    deduped = int(meta.get("deduped_count", len(candidates)))
    sorted_count = int(meta.get("sorted_count", len(candidates)))
    human_count = int(meta.get("human_count", len(candidates)))
    human_budget = int(meta.get("human_budget", human_count or 1))

    if human_count > human_budget:
        issues.append(f"human_count {human_count} > budget {human_budget}")
    if deduped > sorted_count and sorted_count > 0:
        issues.append("deduped_count > sorted_count (unexpected)")

    # Convergence monotonicity: later human candidates should not beat earlier on sort key.
    sort_keys = [
        (
            -(c.get("convergence_score") or 0),
            -(c.get("similarity") or 0.0),
            int(c.get("tmdb_id", 0)),
        )
        for c in candidates
    ]
    if sort_keys != sorted(sort_keys):
        issues.append("human_candidates not monotonic by convergence/sort key")

    # Dedup invariant on raw pool replay when available.
    raw_pool = retrieve_payload.get("sorted_candidates")
    if isinstance(raw_pool, list) and raw_pool:
        dedup_replay = dedupe_candidates_by_tmdb_id(raw_pool)
        if len(dedup_replay) > len(raw_pool):
            issues.append("dedupe replay expanded pool (unexpected)")

    return {
        "pass": not issues,
        "meta": meta,
        "issues": issues,
        "candidate_count": len(candidates),
    }


def audit_open_d_weak_fit(
    persona_audits: list[dict[str, Any]],
    pipelines: list[dict[str, Any]],
) -> dict[str, Any]:
    """⑥ OPEN d: valence optionalization quality for weak-fit personas."""
    pipeline_by_id = {str(p.get("persona_id")): p for p in pipelines}
    observations: list[dict[str, Any]] = []

    for audit in persona_audits:
        pid = str(audit.get("persona_id", ""))
        if pid not in _WEAK_FIT_PERSONAS_GRID:
            continue
        pipe = pipeline_by_id.get(pid, {})
        legs = [
            row
            for row in pipe.get("pseudos") or []
            if str(row.get("id")) != NEUTRAL_PSEUDO_ID
        ]
        fits = [float(row.get("fit", 0)) for row in legs if row.get("fit") is not None]
        min_fit = min(fits) if fits else None
        max_fit = max(fits) if fits else None
        low_fit = min_fit is not None and min_fit < _WEAK_FIT_THRESHOLD

        has_error = bool(pipe.get("error") or audit.get("pipeline_error"))
        guard_ok = not audit.get("guard_hard_failures")
        center_ok = audit.get("center_truthfulness", {}).get("pass", False)
        fact_ok = audit.get("fact_drift", {}).get("pass", False)

        quality = "acceptable"
        notes: list[str] = []
        if has_error:
            quality = "failed"
            notes.append("pipeline error")
        elif not guard_ok:
            quality = "guard_fail"
            notes.append("runtime guard hard failure")
        elif low_fit and not (center_ok and fact_ok):
            quality = "weak_and_drift"
            notes.append("low fit with center/fact issues")
        elif low_fit:
            quality = "weak_but_clean"
            notes.append("low fit but guards clean — valence optionalization ok")

        observations.append(
            {
                "persona_id": pid,
                "weak_fit_cohort": True,
                "min_fit": min_fit,
                "max_fit": max_fit,
                "low_fit": low_fit,
                "quality": quality,
                "notes": notes,
                "pseudo_count": len(legs),
                "channels": [
                    (row.get("source") or {}).get("channel")
                    for row in legs
                ],
            }
        )

    weak_failed = [o for o in observations if o["quality"] in ("failed", "guard_fail")]
    return {
        "pass": not weak_failed,
        "weak_fit_personas": sorted(_WEAK_FIT_PERSONAS_GRID),
        "observations": observations,
        "open_d_note": (
            "Observe whether weak-fit personas still produce fact-entailed, "
            "axis-aligned pseudos without forced valence coverage after 3.11.0 downgrade."
        ),
    }


def audit_pilot_run(
    *,
    run_dir: Path,
    baseline_run_dir: Path,
    deconstruction: dict[str, Any],
    expansion: dict[str, Any] | None,
    baseline_retrieve: dict[str, Any],
    design_retrieve: dict[str, Any],
    gap_a_targets: list[GapATarget],
) -> dict[str, Any]:
    """Full firewall audit for one pilot run directory."""
    persona_audits: list[dict[str, Any]] = []
    n1_checks: list[dict[str, Any]] = []
    pipelines: list[dict[str, Any]] = []

    personas_dir = run_dir / "personas"
    baseline_personas = baseline_run_dir / "personas"

    for persona_dir in sorted(personas_dir.iterdir()):
        if not persona_dir.is_dir():
            continue
        pid = persona_dir.name
        pipeline_path = persona_dir / "persona-pipeline.json"
        if not pipeline_path.is_file():
            continue
        pipeline = json.loads(pipeline_path.read_text(encoding="utf-8"))
        pipelines.append(pipeline)

        alt_path = persona_dir / "alt-pool-overlay.json"
        if not alt_path.is_file():
            alt_path = baseline_personas / pid / "alt-pool-overlay.json"
        alt_pool = load_alt_pool_overlay(alt_path)

        persona_audit = audit_persona_guards(
            pid, pipeline, deconstruction, alt_pool, expansion
        )
        guard_meta = pipeline.get("pseudo_guard")
        if isinstance(guard_meta, dict):
            persona_audit["pseudo_guard"] = guard_meta
        persona_audits.append(persona_audit)

        baseline_pipe_path = baseline_personas / pid / "persona-pipeline.json"
        if baseline_pipe_path.is_file():
            baseline_pipe = json.loads(baseline_pipe_path.read_text(encoding="utf-8"))
            n1_checks.append(audit_neutral_n1_unchanged(pipeline, baseline_pipe, pid))

    pool_diff = compare_pool_diff(
        run_id=run_dir.name,
        baseline_retrieve=baseline_retrieve,
        pretest_retrieve=design_retrieve,
        gap_a_targets=gap_a_targets,
    )
    channel_diff = compare_pool_diff_by_channel(
        run_id=run_dir.name,
        baseline_retrieve=baseline_retrieve,
        design_retrieve=design_retrieve,
    )

    dimensions = {
        "fact_drift": {
            "pass": all(a["fact_drift"]["pass"] for a in persona_audits),
            "hard_guard_failures": sum(
                len(a["guard_hard_failures"]) for a in persona_audits
            ),
            "persona_failures": [
                a["persona_id"]
                for a in persona_audits
                if not a["fact_drift"]["pass"]
            ],
        },
        "center_truthfulness": {
            "pass": all(a["center_truthfulness"]["pass"] for a in persona_audits),
            "persona_failures": [
                a["persona_id"]
                for a in persona_audits
                if not a["center_truthfulness"]["pass"]
            ],
        },
        "focalized_derivation": {
            "pass": True,
            "diagnostic_only": True,
            "warning_count": sum(
                len(c.get("derivation_warnings") or [])
                for a in persona_audits
                for c in a["focalized_derivation"].get("checks", [])
            ),
            "persona_failures": [],
        },
        "dual_floor": {
            "pass": (
                (
                    all(a["dual_floor"]["pass"] for a in persona_audits)
                    if adr8_dual_floor_enabled()
                    else True
                )
                and all(c["pass"] for c in n1_checks)
            ),
            "guard_enabled": adr8_dual_floor_enabled(),
            "n1_unchanged": n1_checks,
            "baseline_hits": audit_baseline_hits_retained(
                baseline_retrieve, design_retrieve
            ),
            "persona_dual_failures": [
                a["persona_id"]
                for a in persona_audits
                if not a["dual_floor"]["pass"]
            ],
        },
        "funnel": audit_funnel_reasonable(design_retrieve),
        "open_d_weak_fit": audit_open_d_weak_fit(persona_audits, pipelines),
    }

    all_pass = all(
        dimensions[k]["pass"]
        for k in (
            "fact_drift",
            "center_truthfulness",
            "dual_floor",
            "funnel",
        )
    )

    return {
        "run_id": run_dir.name,
        "persona_count": len(persona_audits),
        "personas": persona_audits,
        "dimensions": dimensions,
        "pool_diff": pool_diff_result_to_dict(pool_diff),
        "pool_diff_by_channel": pool_diff_by_channel_to_dict(channel_diff),
        "center_granularity": summarize_center_granularity(pipelines),
        "all_automated_pass": all_pass,
    }


def compute_pipeline_go_metrics(
    audit: dict[str, Any],
    *,
    persona_errors: list[dict[str, str]] | None = None,
    skip_retrieval: bool = False,
) -> dict[str, Any]:
    """Element-centered pipeline go metrics (decision doc §5–§8)."""
    persona_audits = audit.get("personas") or []
    total_personas = max(len(persona_audits), 1)
    covered_personas = 0
    generated_legs = 0
    kept_legs = 0
    valid_center_legs = 0
    drop_reasons: list[dict[str, str]] = []

    for pa in persona_audits:
        pid = str(pa.get("persona_id", ""))
        if any(e.get("persona_id") == pid for e in (persona_errors or [])):
            continue
        guard = pa.get("pseudo_guard") or {}
        kept = int(guard.get("kept_pseudos", 0))
        dropped = int(guard.get("dropped_pseudos", 0))
        generated_legs += kept + dropped
        kept_legs += kept
        if kept >= 1:
            covered_personas += 1
        for row in guard.get("drop_reasons") or []:
            if isinstance(row, dict):
                drop_reasons.append({**row, "persona_id": pid})
        checks = pa.get("center_truthfulness", {}).get("checks") or []
        for chk in checks:
            if chk.get("pass") and chk.get("center"):
                valid_center_legs += 1

    pool = audit.get("pool_diff") or {}
    retrieve_ok = not skip_retrieval or bool(pool)
    pool_diff_ok = pool.get("baseline_candidate_count") is not None

    survival = kept_legs / generated_legs if generated_legs else 0.0
    valid_center_rate = (
        valid_center_legs / kept_legs if kept_legs else 0.0
    )

    pipeline_go = (
        covered_personas >= max(1, total_personas // 2)
        and retrieve_ok
        and pool_diff_ok
        and (len(drop_reasons) > 0 or kept_legs > 0)
    )

    return {
        "persona_coverage": f"{covered_personas}/{total_personas}",
        "persona_coverage_count": covered_personas,
        "persona_coverage_total": total_personas,
        "pseudo_survival_rate": round(survival, 4),
        "valid_center_rate": round(valid_center_rate, 4),
        "drop_reasons": drop_reasons,
        "dropped_pseudo_count": len(drop_reasons),
        "retrieve_complete": retrieve_ok,
        "pool_diff_produced": pool_diff_ok,
        "pipeline_go": pipeline_go,
        "overlap_count": pool.get("overlap_count"),
        "net_new_count": len(pool.get("net_new_tmdb_ids") or []),
        "lost_count": len(pool.get("lost_tmdb_ids") or []),
    }


def go_no_go_pilot_recommendation(
    audit: dict[str, Any],
    *,
    dry_run: bool,
    persona_errors: list[dict[str, str]] | None = None,
    skip_retrieval: bool = False,
) -> dict[str, Any]:
    """Pipeline Go heuristic for element-centered 3.11.6 (decision doc)."""
    if dry_run:
        return {
            "verdict": "Pending live run",
            "reason": "Dry-run scaffold only — rerun with LLM + retrieval for Go/No-Go.",
            "pipeline_go": False,
        }

    metrics = compute_pipeline_go_metrics(
        audit,
        persona_errors=persona_errors,
        skip_retrieval=skip_retrieval,
    )

    if metrics["pipeline_go"]:
        verdict = "Pipeline Go"
        reason = (
            f"persona_coverage={metrics['persona_coverage']}, "
            f"pseudo_survival_rate={metrics['pseudo_survival_rate']}, "
            f"dropped={metrics['dropped_pseudo_count']}, "
            f"net_new={metrics['net_new_count']}, lost={metrics['lost_count']} (recorded only)"
        )
    else:
        verdict = "Pipeline No-Go"
        reason = (
            f"persona_coverage={metrics['persona_coverage']} below threshold or "
            f"retrieve/pool_diff incomplete"
        )

    return {
        "verdict": verdict,
        "reason": reason,
        "pipeline_go": metrics["pipeline_go"],
        "metrics": metrics,
    }


def render_pilot_audit_markdown(
    audit: dict[str, Any],
    *,
    go_no_go: dict[str, Any],
    output_dir: str,
    baseline_dir: str,
) -> str:
    dims = audit.get("dimensions") or {}
    pool = audit.get("pool_diff") or {}
    by_ch = audit.get("pool_diff_by_channel") or {}
    center = audit.get("center_granularity") or {}

    def status(pass_: bool) -> str:
        return "PASS (auto)" if pass_ else "FAIL / NEEDS EYEBALL"

    lines = [
        "# Phase 3.11.6 Pilot Audit · Firewall",
        "",
        f"**Design-on output:** `{output_dir}`",
        f"**3.10 baseline:** `{baseline_dir}`",
        f"**Run:** `{audit.get('run_id', '?')}` · personas: {audit.get('persona_count', '?')}",
        "",
        "## Go/No-Go (heuristic · requires human approve)",
        "",
        f"- **Verdict:** {go_no_go.get('verdict')}",
        f"- **Reason:** {go_no_go.get('reason')}",
        "",
        "## Summary table",
        "",
        "| # | Audit dimension | Automated | Human eyeball |",
        "|---|-----------------|-----------|---------------|",
        f"| ① | Fact drift (no inner monologue / novel events) | "
        f"{status(dims.get('fact_drift', {}).get('pass', False))} · "
        f"hard_failures={dims.get('fact_drift', {}).get('hard_guard_failures', 0)} | "
        f"Read focalized legs for invented interiority |",
        f"| ② | Center declaration truthfulness | "
        f"{status(dims.get('center_truthfulness', {}).get('pass', False))} · "
        f"fails={dims.get('center_truthfulness', {}).get('persona_failures', [])} | "
        f"Confirm declared center is load-bearing in prose |",
        f"| ③ | POV/focal diagnostic label | PASS (diagnostic-only) · "
        f"warnings={dims.get('focalized_derivation', {}).get('warning_count', 0)} | "
        f"Use only to explain possible POV变换 labels; not a Go/No-Go standard |",
        f"| ④ | Dual floor (n1 + non-focal toned; baseline hits) | "
        f"{status(dims.get('dual_floor', {}).get('pass', False))} · "
        f"lost={dims.get('dual_floor', {}).get('baseline_hits', {}).get('lost_tmdb_ids', [])} | "
        f"Spot-check n1 verbatim; 3.10 hits retained |",
        f"| ⑤ | Funnel dedup / convergent sort | "
        f"{status(dims.get('funnel', {}).get('pass', False))} | "
        f"Review top human_candidates ordering |",
        f"| ⑥ | OPEN d weak-fit valence optionalization | "
        f"{status(dims.get('open_d_weak_fit', {}).get('pass', False))} | "
        f"Read Innocent/Jester/Lover/Creator legs for honest low-fit tone |",
        "",
        "## Pool diff (design-on ∖ 3.10)",
        "",
        f"- Baseline candidates: {pool.get('baseline_candidate_count')}",
        f"- Design candidates: {pool.get('pretest_candidate_count')}",
        f"- Net-new tmdb_ids: `{pool.get('net_new_tmdb_ids')}`",
        f"- Lost vs baseline: `{pool.get('lost_tmdb_ids')}`",
        f"- By channel: `{by_ch.get('by_channel')}`",
        "",
        "## Center granularity (OPEN c carry-over)",
        "",
        f"- Centers: `{center.get('center_element_counts')}`",
        f"- Channels: `{center.get('channel_counts')}`",
        f"- Focal who-*: `{center.get('focal_who_counts')}`",
        "",
        "## OPEN d · weak-fit observations",
        "",
    ]

    for obs in dims.get("open_d_weak_fit", {}).get("observations") or []:
        lines.append(
            f"- **{obs.get('persona_id')}** · quality={obs.get('quality')} · "
            f"fit={obs.get('min_fit')}–{obs.get('max_fit')} · "
            f"channels={obs.get('channels')} · {', '.join(obs.get('notes') or [])}"
        )

    lines.extend(
        [
            "",
            "## Per-persona guard detail",
            "",
        ]
    )
    for pa in audit.get("personas") or []:
        pid = pa.get("persona_id")
        if pa.get("guard_hard_failures"):
            lines.append(f"### {pid} — GUARD FAIL")
            for err in pa["guard_hard_failures"]:
                lines.append(f"- {err}")
        elif not pa.get("center_truthfulness", {}).get("pass"):
            lines.append(f"### {pid} — center truthfulness flags")
            for chk in pa["center_truthfulness"]["checks"]:
                if not chk.get("pass"):
                    lines.append(
                        f"- {chk.get('pseudo_id')}: {chk.get('reason')} "
                        f"(center={chk.get('center')})"
                    )

    lines.extend(
        [
            "",
            "## Human checklist (sign each before Go → 3.11.7)",
            "",
            "- [ ] **①** No invented inner monologue, events, causality, or outcomes in focalized/toned legs.",
            "- [ ] **②** Each pseudo's declared center element is genuinely load-bearing (no keyword stuffing).",
            "- [ ] **③** POV/focal annotations are used only as explanation labels for possible POV变换, not as acceptance criteria.",
            "- [ ] **④** Neutral n1 unchanged vs 3.10; ≥1 non-focal toned per persona; baseline hits not lost.",
            "- [ ] **⑤** Funnel dedup and convergent sort look reasonable for human review budget.",
            "- [ ] **⑥** Weak-fit personas produce honest, fact-entailed prose without forced valence coverage.",
            "",
            "_Generated by `scripts/run_phase311_pilot.py` / `scripts/audit_phase311_pilot.py`._",
        ]
    )
    return "\n".join(lines) + "\n"


def pseudos_from_pipeline_dict(pipeline: dict[str, Any]) -> list[PseudoSegment]:
  return _pseudo_objects_from_pipeline(pipeline)


__all__ = [
    "PILOT_DEFAULT_RUN_ID",
    "PILOT_MANIFEST",
    "PilotRunSpec",
    "audit_pilot_run",
    "audit_center_truthfulness",
    "audit_funnel_reasonable",
    "build_default_pilot_manifest",
    "go_no_go_pilot_recommendation",
    "load_pilot_manifest",
    "parse_pilot_runs",
    "pseudo_segment_to_dict",
    "pseudos_from_pipeline_dict",
    "render_pilot_audit_markdown",
]
