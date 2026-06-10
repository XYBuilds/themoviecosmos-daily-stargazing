"""Phase 3.11.1 pretest helpers: Gap A sample selection, ADR-0008 screenwriter wiring, pool diff.

Scaffolding only — full generation guards land in 3.11.2/3.11.3. References 3.11.0
authority wording verbatim (persona_screenwriter_contract.md composition section).
"""

from __future__ import annotations

import json
import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from scripts.agents import (
    PseudoSegment,
    _known_fragment_ids,
    annotate_fragment_ids,
    extract_json_object,
    minimal_clean,
    parse_pseudos_response,
)
from scripts.personas import (
    NEUTRAL_PSEUDO_ID,
    AltElement,
    AltPoolOverlay,
    AltTerm,
    build_screenwriter_user_prompt,
    collect_hypernym_anchor_terms,
    list_persona_ids,
    validate_toned_hypernym_anchor,
)

_CANONICAL_PERSONA_BY_UPPER = {pid.upper(): pid for pid in list_persona_ids()}

ChannelKind = Literal["toned", "focalized"]

PHASE39_SCORES = Path("output/Eval/phase3.9/llm-judge-scores.json")
PHASE310_ROOT = Path("output/Eval/phase3.10")
PHASE311_ROOT = Path("output/Eval/phase3.11")
PRETEST_MANIFEST = PHASE311_ROOT / "pretest-manifest.json"

_COMPOSITION_MARKER = "Composition mode: ADR-0008"


@dataclass
class GapATarget:
    tmdb_id: str
    title: str
    human_score: int
    judge_score: int
    judge_resonance_type: str | None
    rationale: str


@dataclass
class PretestRunSpec:
    run_id: str
    gap_a_targets: list[GapATarget]
    personas: list[str]
    note: str = ""


@dataclass
class PoolDiffResult:
    run_id: str
    baseline_candidate_count: int
    pretest_candidate_count: int
    net_new_tmdb_ids: list[int]
    lost_tmdb_ids: list[int]
    overlap_count: int
    gap_a_targets_in_net_new: list[dict[str, Any]]
    gap_a_targets_in_baseline_only: list[dict[str, Any]]
    net_new_details: list[dict[str, Any]] = field(default_factory=list)


def load_gap_a_samples(
    scores_path: Path | None = None,
) -> list[dict[str, Any]]:
    """Gap A: human=2, judge=1, judge_resonance_type=表层沾边 (ADR-0007 D1)."""
    path = scores_path or PHASE39_SCORES
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = data.get("scores") or []
    out: list[dict[str, Any]] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        if row.get("human_score") != 2:
            continue
        if row.get("judge_score") != 1:
            continue
        if row.get("judge_resonance_type") != "表层沾边":
            continue
        out.append(row)
    return out


def _normalize_persona_id(token: str) -> str | None:
    token = token.strip()
    if not token or "优质" in token:
        return None
    if token.startswith("The-"):
        return _CANONICAL_PERSONA_BY_UPPER.get(token.upper(), token)
    if token.startswith("THE-"):
        return _CANONICAL_PERSONA_BY_UPPER.get(f"THE-{token[4:]}".upper())
    return _CANONICAL_PERSONA_BY_UPPER.get(f"THE-{token}".upper())


def _personas_from_title_bracket(title: str) -> list[str]:
    m = re.search(r"\[([^\]]+)\]", title)
    if not m:
        return []
    raw = m.group(1)
    parts = [p.strip() for p in raw.split(",") if p.strip()]
    out: list[str] = []
    for part in parts:
        pid = _normalize_persona_id(part)
        if pid and pid not in out:
            out.append(pid)
    return out


def build_default_pretest_manifest(
    scores_path: Path | None = None,
) -> dict[str, Any]:
    """Derive pretest manifest from Gap A rows + sensible persona subset."""
    gap_rows = load_gap_a_samples(scores_path)
    by_run: dict[str, list[dict[str, Any]]] = {}
    for row in gap_rows:
        by_run.setdefault(str(row["run_id"]), []).append(row)

    runs: list[dict[str, Any]] = []
    for run_id in sorted(by_run):
        targets = by_run[run_id]
        persona_set: list[str] = []
        for t in targets:
            for pid in _personas_from_title_bracket(str(t.get("title", ""))):
                if pid not in persona_set:
                    persona_set.append(pid)
        # Cap to 4 personas per run for pretest cost control; prefer Everyman/Hero first.
        priority = [
            "The-Everyman",
            "The-Hero",
            "The-Innocent",
            "The-Explorer",
            "The-Caregiver",
        ]
        ordered = [p for p in priority if p in persona_set]
        ordered.extend(p for p in persona_set if p not in ordered)
        personas = ordered[:4] if ordered else ["The-Everyman", "The-Hero"]

        runs.append(
            {
                "run_id": run_id,
                "note": f"Gap A POV-resonance pretest ({len(targets)} target films)",
                "personas": personas,
                "gap_a_targets": [
                    {
                        "tmdb_id": str(t["tmdb_id"]),
                        "title": str(t.get("title", "")).split(" (")[0],
                        "human_score": t.get("human_score"),
                        "judge_score": t.get("judge_score"),
                        "judge_resonance_type": t.get("judge_resonance_type"),
                        "rationale": t.get("rationale", ""),
                    }
                    for t in targets
                ],
            }
        )

    return {
        "version": 1,
        "description": "Phase 3.11.1 pretest: ADR-0008 composition vs 3.10 baseline pool diff",
        "gap_a_sample_count": len(gap_rows),
        "runs": runs,
    }


def load_pretest_manifest(path: Path | None = None) -> dict[str, Any]:
    manifest_path = path or PRETEST_MANIFEST
    if manifest_path.is_file():
        return json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest = build_default_pretest_manifest()
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return manifest


def parse_pretest_runs(manifest: dict[str, Any]) -> list[PretestRunSpec]:
    specs: list[PretestRunSpec] = []
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
            PretestRunSpec(
                run_id=str(row["run_id"]),
                gap_a_targets=targets,
                personas=[str(p) for p in row.get("personas") or []],
                note=str(row.get("note", "")),
            )
        )
    return specs


def inject_adr8_composition_mode(
    prompt: str,
    *,
    salience: list[str],
) -> str:
    """Append ADR-0008 activation marker + salience (contract § authoritative rule source)."""
    salience_json = json.dumps(salience, ensure_ascii=False, indent=2)
    block = (
        f"\n## {_COMPOSITION_MARKER} (active)\n\n"
        "The Element-centered composition & POV focalization section in the contract "
        "above is **active**. Follow it exactly.\n\n"
        "Injected salience ranking (greedy top-down center selection):\n\n"
        f"```json\n{salience_json}\n```\n\n"
        "Each toned/focalized pseudo **must** declare `center`, `channel`, and `focal` "
        "(when `channel` is `focalized`). At least one pseudo must be non-focalized "
        "third-person toned (dual floor).\n"
    )
    return prompt + block


def build_adr8_screenwriter_user_prompt(
    persona_id: str,
    deconstruction: dict[str, Any],
    alt_pool: AltPoolOverlay,
    *,
    expansion: dict[str, Any] | None = None,
    repair_context: str | None = None,
    prompts_dir: Path | None = None,
) -> str:
    base = build_screenwriter_user_prompt(
        persona_id,
        deconstruction,
        alt_pool,
        expansion=expansion,
        repair_context=repair_context,
        prompts_dir=prompts_dir,
    )
    salience = list(alt_pool.salience)
    if not salience:
        raise ValueError(f"{persona_id}: alt_pool.salience required for ADR-0008 pretest")
    return inject_adr8_composition_mode(base, salience=salience)


def _parse_channel(row: dict[str, Any]) -> ChannelKind:
    channel = str(row.get("channel", "toned")).strip().lower()
    if channel not in ("toned", "focalized"):
        raise ValueError(f"invalid channel {channel!r}; expected toned|focalized")
    return channel  # type: ignore[return-value]


def parse_adr8_pseudos_response(
    raw: str,
    *,
    agent_id: str,
    known_fragments: set[str],
    known_elements: set[str],
) -> list[PseudoSegment]:
    """Parse screenwriter JSON with center/channel/focal provenance fields."""
    data = extract_json_object(raw)
    rows = data.get("pseudos")
    if not isinstance(rows, list):
        raise ValueError("JSON must contain a 'pseudos' array")

    # Reuse fragment/fit validation from agents.parse_pseudos_response.
    base_segments = parse_pseudos_response(
        raw,
        agent_id=agent_id,
        known_fragments=known_fragments,
        require_fit=True,
    )
    row_by_id = {str(r.get("id")): r for r in rows if isinstance(r, dict)}

    tagged: list[PseudoSegment] = []
    for seg in base_segments:
        row = row_by_id.get(seg.id, {})
        center = str(row.get("center", "")).strip()
        if not center:
            raise ValueError(f"pseudo {seg.id}: center is required in ADR-0008 mode")
        if center not in known_elements:
            raise ValueError(f"pseudo {seg.id}: unknown center element {center!r}")
        channel = _parse_channel(row)
        focal = str(row.get("focal", "")).strip() or None
        if channel == "focalized":
            if not focal:
                raise ValueError(f"pseudo {seg.id}: focal required when channel=focalized")
            if not focal.startswith("who-"):
                raise ValueError(f"pseudo {seg.id}: focal must be who-* id, got {focal!r}")
            if focal != center:
                raise ValueError(
                    f"pseudo {seg.id}: focal {focal!r} must equal center {center!r}"
                )
        elif focal:
            raise ValueError(f"pseudo {seg.id}: focal set but channel is toned")

        source = dict(seg.source)
        source.update(
            {
                "center": center,
                "channel": channel,
                "channel_role": channel,
                "composition_mode": "ADR-0008",
            }
        )
        if focal:
            source["focal"] = focal
        tagged.append(
            PseudoSegment(
                seg.id,
                seg.text,
                source,
                seg.warnings,
                fit=seg.fit,
            )
        )

    toned_count = sum(1 for p in tagged if p.source.get("channel") == "toned")
    if toned_count < 1:
        raise ValueError("ADR-0008 dual floor: need ≥1 non-focalized toned pseudo")

    return tagged


def load_alt_pool_overlay(path: Path) -> AltPoolOverlay:
    data = json.loads(path.read_text(encoding="utf-8"))
    pid = str(data.get("persona_id", ""))
    pool = data.get("alt_pool") or data.get("overlay", {}).get("alt_pool") or data
    elements_raw = pool.get("elements") if isinstance(pool, dict) else None
    if not isinstance(elements_raw, list):
        elements_raw = data.get("elements")
    if not isinstance(elements_raw, list):
        raise ValueError(f"alt pool missing elements: {path}")

    elements: list[AltElement] = []
    for row in elements_raw:
        alts = [
            AltTerm(
                term=str(a["term"]),
                valence=str(a.get("valence", "neutral")),
                provenance=a.get("provenance"),
            )
            for a in row.get("alternatives") or []
        ]
        elements.append(
            AltElement(
                element_id=str(row["element_id"]),
                original_term=str(row.get("original_term", "")),
                alternatives=alts,
            )
        )
    salience = [str(s) for s in (data.get("salience") or pool.get("salience") or [])]
    return AltPoolOverlay(persona_id=pid, elements=elements, salience=salience)


def load_baseline_neutral_pseudo(
    baseline_run_dir: Path,
    persona_id: str,
) -> PseudoSegment:
    """Reuse 3.10 neutral n1 verbatim (ADR-0008 D3 zero-change rule)."""
    path = baseline_run_dir / "personas" / persona_id / "persona-pipeline.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    for row in data.get("pseudos") or []:
        if str(row.get("id")) != NEUTRAL_PSEUDO_ID:
            continue
        src = row.get("source") if isinstance(row.get("source"), dict) else {}
        return PseudoSegment(
            id=NEUTRAL_PSEUDO_ID,
            text=str(row.get("text", "")),
            source=src,
            warnings=list(row.get("warnings") or []),
            fit=row.get("fit"),
        )
    raise FileNotFoundError(f"neutral n1 missing in {path}")


def assemble_adr8_channel_pseudos(
    persona_id: str,
    deconstruction: dict[str, Any],
    alt_pool: AltPoolOverlay,
    adr8_toned: list[PseudoSegment],
    baseline_neutral: PseudoSegment,
    expansion: dict[str, Any] | None = None,
) -> list[PseudoSegment]:
    """neutral n1 from baseline + ADR-0008 toned/focalized legs."""
    hypernyms = collect_hypernym_anchor_terms(alt_pool, expansion)
    for pseudo in adr8_toned:
        validate_toned_hypernym_anchor(pseudo, hypernyms)
        pseudo.source["agent_id"] = persona_id

    neutral = PseudoSegment(
        baseline_neutral.id,
        baseline_neutral.text,
        dict(baseline_neutral.source),
        baseline_neutral.warnings,
        fit=baseline_neutral.fit,
    )
    neutral.source["agent_id"] = persona_id
    neutral.source["channel_role"] = "neutral"

    return [neutral, *adr8_toned]


def pseudo_segment_to_dict(pseudo: PseudoSegment) -> dict[str, Any]:
    row: dict[str, Any] = {
        "id": pseudo.id,
        "text": pseudo.text,
        "source": pseudo.source,
        "warnings": pseudo.warnings,
    }
    if pseudo.fit is not None:
        row["fit"] = pseudo.fit
    return row


def persona_agent_from_pseudos(persona_id: str, pseudos: list[PseudoSegment]) -> dict[str, Any]:
    return {
        "agent_id": persona_id,
        "persona_name": persona_id,
        "role": "persona",
        "pseudos": [pseudo_segment_to_dict(p) for p in pseudos],
    }


def candidate_tmdb_ids(retrieve_payload: dict[str, Any]) -> set[int]:
    ids: set[int] = set()
    for row in retrieve_payload.get("candidates") or []:
        if isinstance(row, dict) and row.get("tmdb_id") is not None:
            ids.add(int(row["tmdb_id"]))
    return ids


def _candidate_detail(
    retrieve_payload: dict[str, Any],
    tmdb_id: int,
) -> dict[str, Any] | None:
    for row in retrieve_payload.get("candidates") or []:
        if isinstance(row, dict) and int(row.get("tmdb_id", -1)) == tmdb_id:
            return {
                "tmdb_id": tmdb_id,
                "title": row.get("title"),
                "similarity": row.get("similarity"),
                "quality_candidate": row.get("quality_candidate"),
                "triggered_by": row.get("triggered_by"),
                "hit_sources": row.get("hit_sources"),
            }
    return None


def compare_pool_diff(
    *,
    run_id: str,
    baseline_retrieve: dict[str, Any],
    pretest_retrieve: dict[str, Any],
    gap_a_targets: list[GapATarget],
) -> PoolDiffResult:
    base_ids = candidate_tmdb_ids(baseline_retrieve)
    new_ids = candidate_tmdb_ids(pretest_retrieve)
    net_new = sorted(new_ids - base_ids)
    lost = sorted(base_ids - new_ids)
    target_map = {int(t.tmdb_id): t for t in gap_a_targets}

    gap_in_net: list[dict[str, Any]] = []
    gap_baseline_only: list[dict[str, Any]] = []
    for tid, target in target_map.items():
        entry = {
            "tmdb_id": tid,
            "title": target.title,
            "human_score": target.human_score,
            "judge_resonance_type": target.judge_resonance_type,
        }
        if tid in net_new:
            detail = _candidate_detail(pretest_retrieve, tid) or {}
            gap_in_net.append({**entry, **detail})
        elif tid in base_ids:
            gap_baseline_only.append(entry)

    net_new_details = [
        d
        for d in (
            _candidate_detail(pretest_retrieve, tid) for tid in net_new
        )
        if d is not None
    ]

    return PoolDiffResult(
        run_id=run_id,
        baseline_candidate_count=len(base_ids),
        pretest_candidate_count=len(new_ids),
        net_new_tmdb_ids=net_new,
        lost_tmdb_ids=lost,
        overlap_count=len(base_ids & new_ids),
        gap_a_targets_in_net_new=gap_in_net,
        gap_a_targets_in_baseline_only=gap_baseline_only,
        net_new_details=net_new_details,
    )


def summarize_center_granularity(
    persona_pipelines: list[dict[str, Any]],
) -> dict[str, Any]:
    """OPEN c observation: center element id distribution across pretest pseudos."""
    centers: Counter[str] = Counter()
    channels: Counter[str] = Counter()
    focal_who: Counter[str] = Counter()
    per_persona: dict[str, list[dict[str, str]]] = {}

    for pipeline in persona_pipelines:
        pid = str(pipeline.get("persona_id", ""))
        rows: list[dict[str, str]] = []
        for pseudo in pipeline.get("pseudos") or []:
            if str(pseudo.get("id")) == NEUTRAL_PSEUDO_ID:
                continue
            src = pseudo.get("source") if isinstance(pseudo.get("source"), dict) else {}
            center = str(src.get("center") or pseudo.get("center") or "")
            channel = str(src.get("channel") or pseudo.get("channel") or "toned")
            if center:
                centers[center] += 1
            channels[channel] += 1
            if channel == "focalized":
                focal = str(src.get("focal") or "")
                if focal:
                    focal_who[focal] += 1
            rows.append({"pseudo_id": str(pseudo.get("id")), "center": center, "channel": channel})
        if pid:
            per_persona[pid] = rows

    return {
        "center_element_counts": dict(centers),
        "channel_counts": dict(channels),
        "focal_who_counts": dict(focal_who),
        "per_persona": per_persona,
        "open_c_note": (
            "Centers span who/where/why/how/result element ids; observe whether "
            "salience-greedy who-* centers unlock POV focalization without over-coarse buckets."
        ),
    }


def go_no_go_recommendation(summary: dict[str, Any]) -> dict[str, Any]:
    """Heuristic Go/No-Go for human gate (not a hard gate)."""
    if summary.get("dry_run") or summary.get("skip_retrieval"):
        return {
            "verdict": "Pending live run",
            "reason": (
                "Scaffold/dry-run only — rerun with LLM + retrieval index for "
                "authoritative Go/No-Go on net-new resonance pieces."
            ),
        }

    total_net_new = int(summary.get("total_net_new_candidates", 0))
    gap_hits = int(summary.get("gap_a_targets_recalled_net_new", 0))
    runs_with_gap_hit = int(summary.get("runs_with_gap_a_net_new", 0))

    if gap_hits >= 2 or (gap_hits >= 1 and runs_with_gap_hit >= 2):
        verdict = "Go"
        reason = (
            f"Net-new pool contains {gap_hits} Gap A target film(s) across "
            f"{runs_with_gap_hit} run(s) — plausible POV/composition recall lift."
        )
    elif total_net_new >= 3 and gap_hits == 0:
        verdict = "Conditional Go"
        reason = (
            f"{total_net_new} net-new candidates but none match Gap A targets; "
            "manual review whether additions are resonance vs noise."
        )
    else:
        verdict = "No-Go"
        reason = (
            "Pool diff shows little/no net-new signal on Gap A targets; "
            "composition pretest did not surface missed resonance pieces."
        )

    return {"verdict": verdict, "reason": reason}


def pool_diff_result_to_dict(result: PoolDiffResult) -> dict[str, Any]:
    return {
        "run_id": result.run_id,
        "baseline_candidate_count": result.baseline_candidate_count,
        "pretest_candidate_count": result.pretest_candidate_count,
        "overlap_count": result.overlap_count,
        "net_new_tmdb_ids": result.net_new_tmdb_ids,
        "lost_tmdb_ids": result.lost_tmdb_ids,
        "gap_a_targets_in_net_new": result.gap_a_targets_in_net_new,
        "gap_a_targets_in_baseline_only": result.gap_a_targets_in_baseline_only,
        "net_new_details": result.net_new_details,
    }


def render_pool_diff_markdown(
    *,
    manifest: dict[str, Any],
    per_run: list[PoolDiffResult],
    center_summary: dict[str, Any],
    go_no_go: dict[str, Any],
) -> str:
    lines = [
        "# Phase 3.11.1 Pretest — Pool Diff Report",
        "",
        f"Gap A samples in manifest: {manifest.get('gap_a_sample_count', '?')}",
        "",
        "## Go/No-Go (heuristic · requires human approve)",
        "",
        f"- **Verdict:** {go_no_go.get('verdict')}",
        f"- **Reason:** {go_no_go.get('reason')}",
        "",
        "## Per-run pool diff",
        "",
    ]
    for result in per_run:
        lines.extend(
            [
                f"### {result.run_id}",
                "",
                f"- Baseline candidates: {result.baseline_candidate_count}",
                f"- Pretest candidates: {result.pretest_candidate_count}",
                f"- Net-new tmdb_ids ({len(result.net_new_tmdb_ids)}): "
                + (", ".join(str(x) for x in result.net_new_tmdb_ids) or "—"),
                f"- Lost vs baseline ({len(result.lost_tmdb_ids)}): "
                + (", ".join(str(x) for x in result.lost_tmdb_ids[:10]) or "—"),
                "",
            ]
        )
        if result.gap_a_targets_in_net_new:
            lines.append("**Gap A targets newly in pool:**")
            for row in result.gap_a_targets_in_net_new:
                lines.append(
                    f"- {row.get('title')} (tmdb {row.get('tmdb_id')}) "
                    f"sim={row.get('similarity')}"
                )
            lines.append("")
        if result.gap_a_targets_in_baseline_only:
            lines.append("**Gap A targets already in baseline (not net-new):**")
            for row in result.gap_a_targets_in_baseline_only:
                lines.append(f"- {row.get('title')} (tmdb {row.get('tmdb_id')})")
            lines.append("")

    lines.extend(
        [
            "## Center element granularity (OPEN c)",
            "",
            f"- Center counts: `{center_summary.get('center_element_counts')}`",
            f"- Channel counts: `{center_summary.get('channel_counts')}`",
            f"- Focal who-* counts: `{center_summary.get('focal_who_counts')}`",
            f"- Note: {center_summary.get('open_c_note')}",
            "",
        ]
    )
    return "\n".join(lines) + "\n"


def known_elements_from_decon(deconstruction: dict[str, Any]) -> set[str]:
    ann = annotate_fragment_ids(deconstruction)
    known: set[str] = set()
    for section in ("who", "where", "why", "how", "result"):
        for item in ann.get(section) or []:
            if isinstance(item, dict) and item.get("id"):
                known.add(str(item["id"]))
    return known
