"""rewrite.py · persona pipeline (ADR-0009 fragment ladder / search unit).

Pipeline: verbatim decon + expansion → alt_creator(persona) → screenwriter(persona)
emitting native ``search_units[]`` (center_element + supporting_elements + fit) →
fragment ladders + search-unit payload (single source of truth, no channel split).

Produces a flavored-decon **overlay** (alt-pool + element id refs only; no fork of full decon text).
Reuses agents.py for render_prompt, extract_json_object, parse_search_units_response, and LLM calls.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from openai import OpenAI

from scripts.agents import (
    PseudoSegment,
    _agent_llm_timeout,
    _model_name,
    _resolve_provider,
    annotate_fragment_ids,
    extract_json_object,
    load_deconstruction_from_file,
    minimal_clean,
    parse_search_units_response,
    pseudo_to_dict,
    render_prompt,
)
from scripts.lib.env import load_env
from scripts.lib.llm import get_llm_client
from scripts.lib.paths import repo_root

FragmentLevel = Literal[
    "surface",
    "alias",
    "objective_close",
    "objective_mid",
    "objective_broad",
    "interpretive",
    "perspective",
    "persona_relative",
]
SearchUnitKind = Literal[
    "surface-fragment-bundle",
    "event-fragment-bundle",
    "persona-semantic",
]

NEUTRAL_PSEUDO_ID = "n1"

_ELEMENT_ID_RE = re.compile(r"^(when|who|where|why|how|result)-\d+$")

# Search-unit supporting-element cap (carried over from the element-centered design).
_ADR8_SUPPORTING_MAX = 4

ALT_CREATOR_CONTRACT = (
    repo_root() / "prompts" / "_shared" / "persona_alt_creator_contract.md"
)
SCREENWRITER_CONTRACT = (
    repo_root() / "prompts" / "_shared" / "persona_screenwriter_contract.md"
)
PERSONAS_SSOT = repo_root() / "docs" / "SSOT" / "personas-12.md"

_PERSONA_ID_ROW = re.compile(r"^\|\s*(The-[A-Za-z]+)\s*\|")


def list_persona_ids(ssot_path: Path | None = None) -> list[str]:
    """Return canonical Pearson persona_id list from personas-12 SSOT."""
    path = ssot_path or PERSONAS_SSOT
    if not path.is_file():
        raise FileNotFoundError(f"personas SSOT not found: {path}")
    ids: list[str] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        m = _PERSONA_ID_ROW.match(line.strip())
        if m:
            ids.append(m.group(1))
    # personas-12.md lists ids twice (roster + value-axis table); keep first occurrence.
    ids = list(dict.fromkeys(ids))
    if len(ids) != 12:
        raise ValueError(f"expected 12 persona_ids in {path}, got {len(ids)}: {ids}")
    return ids

_ELEMENT_SECTIONS: tuple[str, ...] = ("when", "who", "where", "why", "how", "result")

# Top-level decon keys that must not appear on alt-pool overlay (P-SSOT: no fork).
_DECON_TOP_LEVEL_KEYS: frozenset[str] = frozenset(
    {"anchor", "when", "where", "who", "why", "how", "result", "deconstruction", "news"}
)

_VALID_VALENCES: frozenset[str] = frozenset({"positive", "neutral", "negative"})
_VALID_PROVENANCES: frozenset[str] = frozenset({"surface", "hypernym", "lens"})
_OBJECTIVE_FRAGMENT_LEVELS: frozenset[str] = frozenset(
    {"surface", "alias", "objective_close", "objective_mid", "objective_broad"}
)
_INTERPRETIVE_FRAGMENT_LEVELS: frozenset[str] = frozenset(
    {"interpretive", "perspective", "persona_relative"}
)
_FRAGMENT_LEVEL_WEIGHTS: dict[str, float] = {
    "surface": 1.0,
    "alias": 0.95,
    "objective_close": 0.82,
    "objective_mid": 0.58,
    "objective_broad": 0.34,
    "interpretive": 0.38,
    "perspective": 0.34,
    "persona_relative": 0.34,
}

_SYSTEM_ALT = (
    "You are a persona alt-creator. Follow the user message exactly. "
    "Return only valid JSON matching the persona alt-creator contract."
)
_SYSTEM_SCREEN = (
    "You are a persona screenwriter. Follow the user message exactly. "
    "Return only valid JSON matching the persona screenwriter contract "
    "(including fit on each pseudo)."
)


@dataclass
class AltTerm:
    term: str
    valence: str
    provenance: str | None = None


@dataclass
class FragmentTerm:
    text: str
    weight: float
    level: FragmentLevel
    element_id: str


@dataclass
class FragmentLadder:
    element_id: str
    dimension: str
    fragments: list[FragmentTerm]

    def objective_fragments(self) -> list[FragmentTerm]:
        return [
            item
            for item in self.fragments
            if item.level in _OBJECTIVE_FRAGMENT_LEVELS
        ]

    def interpretive_fragments(self) -> list[FragmentTerm]:
        return [
            item
            for item in self.fragments
            if item.level in _INTERPRETIVE_FRAGMENT_LEVELS
        ]

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "element_id": self.element_id,
            "dimension": self.dimension,
        }
        for fragment in self.fragments:
            bucket = payload.setdefault(fragment.level, [])
            bucket.append({"text": fragment.text, "weight": fragment.weight})
        return payload


@dataclass
class SearchUnit:
    id: str
    kind: SearchUnitKind
    search_text: str
    source_elements: list[str]
    fragments: list[FragmentTerm] = field(default_factory=list)
    persona_id: str | None = None
    center_element: str | None = None
    supporting_elements: list[str] = field(default_factory=list)
    fit: str | float | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "id": self.id,
            "kind": self.kind,
            "source_elements": list(self.source_elements),
            "search_text": self.search_text,
        }
        if self.fragments:
            payload["fragments"] = [
                {
                    "element_id": item.element_id,
                    "level": item.level,
                    "text": item.text,
                    "weight": item.weight,
                }
                for item in self.fragments
            ]
        if self.persona_id:
            payload["persona_id"] = self.persona_id
        if self.center_element:
            payload["center_element"] = self.center_element
        if self.supporting_elements:
            payload["supporting_elements"] = list(self.supporting_elements)
        if self.fit is not None:
            payload["fit"] = self.fit
        return payload


@dataclass
class AltElement:
    element_id: str
    original_term: str
    alternatives: list[AltTerm]


@dataclass
class AltPoolOverlay:
    persona_id: str
    elements: list[AltElement]
    salience: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "persona_id": self.persona_id,
            "alt_pool": {
                "elements": [
                    {
                        "element_id": el.element_id,
                        "original_term": el.original_term,
                        "alternatives": [
                            _alt_term_to_dict(a) for a in el.alternatives
                        ],
                    }
                    for el in self.elements
                ],
            },
        }
        if self.salience:
            payload["salience"] = list(self.salience)
        return payload


@dataclass
class PersonaPipelineResult:
    persona_id: str
    overlay: AltPoolOverlay
    pseudos: list[PseudoSegment] = field(default_factory=list)
    workflow: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    repair_retries: list[dict[str, str]] = field(default_factory=list)
    error: str | None = None


def annotate_element_ids(deconstruction: dict[str, Any]) -> dict[str, Any]:
    """Annotate who/where/why/how/result with stable element ids (fragments included)."""
    annotated = annotate_fragment_ids(deconstruction)
    for section in ("who", "where"):
        items = annotated.get(section)
        if not isinstance(items, list):
            continue
        for idx, item in enumerate(items):
            if isinstance(item, dict) and "id" not in item:
                item["id"] = f"{section}-{idx}"
    return annotated


def known_element_ids(deconstruction: dict[str, Any]) -> set[str]:
    """All element ids present in an annotated deconstruction."""
    ann = annotate_element_ids(deconstruction)
    ids: set[str] = set()
    for section in _ELEMENT_SECTIONS:
        for item in ann.get(section) or []:
            if isinstance(item, dict) and item.get("id"):
                ids.add(str(item["id"]))
    return ids


def _alt_term_to_dict(term: AltTerm) -> dict[str, str]:
    row: dict[str, str] = {"term": term.term, "valence": term.valence}
    if term.provenance:
        row["provenance"] = term.provenance
    return row


def _resolve_provenance(valence: str, explicit: str | None) -> str:
    """Resolve provenance independently from valence; valence is annotation only."""
    if explicit:
        prov = explicit.strip().lower()
        if prov not in _VALID_PROVENANCES:
            raise ValueError(f"invalid provenance {explicit!r} (expected surface|hypernym|lens)")
        return prov
    return "lens"


def expansion_elements_by_id(
    expansion: dict[str, Any] | None,
) -> dict[str, dict[str, Any]]:
    if not expansion:
        return {}
    rows = expansion.get("elements")
    if not isinstance(rows, list):
        return {}
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        if isinstance(row, dict) and row.get("element_id"):
            out[str(row["element_id"])] = row
    return out


def _fragment_dimension(element_id: str) -> str:
    return element_id.split("-", 1)[0] if "-" in element_id else "unknown"


def _add_ladder_fragment(
    fragments: list[FragmentTerm],
    seen: set[tuple[str, str]],
    *,
    element_id: str,
    text: str,
    level: FragmentLevel,
    weight: float | None = None,
) -> None:
    cleaned = " ".join(str(text).strip().split())
    if not cleaned:
        return
    key = (level, cleaned.lower())
    if key in seen:
        return
    seen.add(key)
    fragments.append(
        FragmentTerm(
            text=cleaned,
            weight=float(weight if weight is not None else _FRAGMENT_LEVEL_WEIGHTS[level]),
            level=level,
            element_id=element_id,
        )
    )


def build_fragment_ladders(
    alt_pool: AltPoolOverlay,
    expansion: dict[str, Any] | None = None,
    deconstruction: dict[str, Any] | None = None,
) -> dict[str, FragmentLadder]:
    """Build fragment ladders by folding old surface/hypernym/lens material into levels."""
    by_id = expansion_elements_by_id(expansion)
    ladders: dict[str, FragmentLadder] = {}
    for element in alt_pool.elements:
        fragments: list[FragmentTerm] = []
        seen: set[tuple[str, str]] = set()
        eid = element.element_id
        _add_ladder_fragment(
            fragments,
            seen,
            element_id=eid,
            text=element.original_term,
            level="surface",
        )
        for alt in element.alternatives:
            provenance = alt.provenance or _resolve_provenance(alt.valence, None)
            if provenance == "surface":
                level: FragmentLevel = "alias"
            elif provenance == "hypernym":
                level = "objective_close"
            else:
                level = "interpretive"
            _add_ladder_fragment(
                fragments,
                seen,
                element_id=eid,
                text=alt.term,
                level=level,
            )
        row = by_id.get(eid)
        if row:
            _add_ladder_fragment(
                fragments,
                seen,
                element_id=eid,
                text=str(row.get("surface", "") or ""),
                level="surface",
            )
            for raw in row.get("hypernyms") or []:
                _add_ladder_fragment(
                    fragments,
                    seen,
                    element_id=eid,
                    text=str(raw),
                    level="objective_close",
                )
        ladders[eid] = FragmentLadder(
            element_id=eid,
            dimension=_fragment_dimension(eid),
            fragments=fragments,
        )

    for eid, row in by_id.items():
        if eid in ladders:
            continue
        fragments: list[FragmentTerm] = []
        seen: set[tuple[str, str]] = set()
        _add_ladder_fragment(
            fragments,
            seen,
            element_id=eid,
            text=str(row.get("surface", "") or ""),
            level="surface",
        )
        for raw in row.get("hypernyms") or []:
            _add_ladder_fragment(
                fragments,
                seen,
                element_id=eid,
                text=str(raw),
                level="objective_close",
            )
        ladders[eid] = FragmentLadder(
            element_id=eid,
            dimension=_fragment_dimension(eid),
            fragments=fragments,
        )

    if deconstruction:
        ann = annotate_element_ids(deconstruction)
        for section in _ELEMENT_SECTIONS:
            for item in ann.get(section) or []:
                if not isinstance(item, dict) or not item.get("id"):
                    continue
                eid = str(item["id"])
                if eid in ladders:
                    continue
                text = str(item.get("text", "") or item.get("step", "") or "").strip()
                fragments: list[FragmentTerm] = []
                seen: set[tuple[str, str]] = set()
                _add_ladder_fragment(
                    fragments,
                    seen,
                    element_id=eid,
                    text=text,
                    level="surface",
                )
                ladders[eid] = FragmentLadder(
                    element_id=eid,
                    dimension=_fragment_dimension(eid),
                    fragments=fragments,
                )
    return ladders


def fragment_ladders_to_dict(
    ladders: dict[str, FragmentLadder],
) -> dict[str, Any]:
    return {"elements": [ladders[eid].to_dict() for eid in sorted(ladders)]}


def _fragments_for_elements(
    ladders: dict[str, FragmentLadder],
    element_ids: list[str],
    *,
    objective_only: bool,
) -> list[FragmentTerm]:
    out: list[FragmentTerm] = []
    seen: set[tuple[str, str, str]] = set()
    for eid in element_ids:
        ladder = ladders.get(eid)
        if not ladder:
            continue
        fragments = ladder.objective_fragments() if objective_only else ladder.fragments
        for fragment in fragments:
            key = (fragment.element_id, fragment.level, fragment.text.lower())
            if key in seen:
                continue
            seen.add(key)
            out.append(fragment)
    return out


def build_fragment_bundle_search_units(
    ladders: dict[str, FragmentLadder],
) -> list[SearchUnit]:
    """Build surface/event fragment bundles from objective ladder levels only."""
    surface_ids = [
        eid
        for eid, ladder in ladders.items()
        if ladder.dimension in {"when", "where", "who"}
    ]
    event_ids = [
        eid
        for eid, ladder in ladders.items()
        if ladder.dimension in {"why", "how", "result"}
    ]
    units: list[SearchUnit] = []
    if surface_ids:
        fragments = _fragments_for_elements(ladders, surface_ids, objective_only=True)
        units.append(
            SearchUnit(
                id="su-surface-1",
                kind="surface-fragment-bundle",
                source_elements=surface_ids,
                fragments=fragments,
                search_text="; ".join(item.text for item in fragments),
            )
        )
    if event_ids:
        fragments = _fragments_for_elements(ladders, event_ids, objective_only=True)
        units.append(
            SearchUnit(
                id="su-event-1",
                kind="event-fragment-bundle",
                source_elements=event_ids,
                fragments=fragments,
                search_text="; ".join(item.text for item in fragments),
            )
        )
    return units


def search_unit_from_pseudo(
    pseudo: PseudoSegment,
    *,
    persona_id: str,
    ladders: dict[str, FragmentLadder] | None = None,
) -> SearchUnit:
    center = str(pseudo.source.get("center", "")).strip()
    supporting = _supporting_fragments(pseudo)
    source_elements = [center, *supporting] if center else supporting
    objective_anchor_fragments: list[FragmentTerm] = []
    if ladders:
        objective_anchor_fragments = _fragments_for_elements(
            ladders,
            list(dict.fromkeys(source_elements)),
            objective_only=True,
        )[:6]
    return SearchUnit(
        id=f"su-persona-{persona_id}-{pseudo.id}",
        kind="persona-semantic",
        persona_id=persona_id,
        center_element=center or None,
        supporting_elements=supporting,
        source_elements=list(dict.fromkeys(source_elements)),
        fragments=objective_anchor_fragments,
        search_text=pseudo.text,
        fit=pseudo.fit,
    )


def validate_search_unit(
    unit: SearchUnit,
    known_elements: set[str],
) -> None:
    if unit.kind in {"surface-fragment-bundle", "event-fragment-bundle"}:
        illegal = [
            item
            for item in unit.fragments
            if item.level not in _OBJECTIVE_FRAGMENT_LEVELS
        ]
        if illegal:
            raise ValueError(f"{unit.id}: fragment bundle cannot use interpretive levels")
        if unit.persona_id:
            raise ValueError(f"{unit.id}: fragment bundle must not bind persona")
    if unit.kind == "persona-semantic":
        if not unit.persona_id:
            raise ValueError(f"{unit.id}: persona-semantic requires persona_id")
        if not unit.center_element or unit.center_element not in known_elements:
            raise ValueError(f"{unit.id}: invalid center_element {unit.center_element!r}")
        if len(unit.supporting_elements) > _ADR8_SUPPORTING_MAX:
            raise ValueError(f"{unit.id}: too many supporting_elements")
        if not any(item.level in _OBJECTIVE_FRAGMENT_LEVELS for item in unit.fragments):
            raise ValueError(f"{unit.id}: persona-semantic requires objective anchor")
    for eid in [*unit.source_elements, *unit.supporting_elements]:
        if eid and eid not in known_elements:
            raise ValueError(f"{unit.id}: unknown source element {eid!r}")


def build_search_units_payload(
    *,
    persona_id: str,
    alt_pool: AltPoolOverlay,
    pseudos: list[PseudoSegment],
    expansion: dict[str, Any] | None,
    known_elements: set[str],
    deconstruction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    ladders = build_fragment_ladders(alt_pool, expansion, deconstruction=deconstruction)
    bundle_units = build_fragment_bundle_search_units(ladders)
    persona_units = [
        search_unit_from_pseudo(pseudo, persona_id=persona_id, ladders=ladders)
        for pseudo in pseudos
    ]
    for unit in [*bundle_units, *persona_units]:
        validate_search_unit(unit, known_elements)
    return {
        "fragment_ladders": fragment_ladders_to_dict(ladders),
        "search_units": {
            "surface_fragment_bundles": [
                unit.to_dict()
                for unit in bundle_units
                if unit.kind == "surface-fragment-bundle"
            ],
            "event_fragment_bundles": [
                unit.to_dict()
                for unit in bundle_units
                if unit.kind == "event-fragment-bundle"
            ],
            "persona_semantic_units": [unit.to_dict() for unit in persona_units],
        },
    }


def validate_salience(
    raw: list[Any],
    known_elements: set[str],
) -> list[str]:
    """Hard-validate salience: subset/permutation of known element ids only."""
    if not isinstance(raw, list) or not raw:
        raise ValueError("salience must be a non-empty ordered list of element_id strings")
    out: list[str] = []
    seen: set[str] = set()
    for item in raw:
        if not isinstance(item, str):
            raise ValueError("salience entries must be element_id strings, not free text")
        eid = item.strip()
        if not eid:
            raise ValueError("salience entry must not be empty")
        if not _ELEMENT_ID_RE.match(eid):
            raise ValueError(f"salience illegal element_id {eid!r}")
        if eid not in known_elements:
            raise ValueError(f"salience unknown element_id {eid!r}")
        if eid in seen:
            raise ValueError(f"salience duplicate element_id {eid!r}")
        seen.add(eid)
        out.append(eid)
    return out


def _supporting_fragments(pseudo: PseudoSegment) -> list[str]:
    frags = pseudo.source.get("fragments")
    if isinstance(frags, list):
        return [str(f).strip() for f in frags if str(f).strip()]
    return []


def parse_alt_pool_response(
    raw: str,
    *,
    persona_id: str,
    known_elements: set[str],
) -> AltPoolOverlay:
    """Parse alt-creator LLM JSON into AltPoolOverlay."""
    data = extract_json_object(raw)
    pid = str(data.get("persona_id", persona_id)).strip() or persona_id
    rows = data.get("elements")
    if not isinstance(rows, list) or not rows:
        raise ValueError("alt-pool JSON must contain a non-empty 'elements' array")

    elements: list[AltElement] = []
    seen: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each element must be an object")
        element_id = str(row.get("element_id", "")).strip()
        if not element_id:
            raise ValueError("element_id is required")
        if element_id not in known_elements:
            raise ValueError(f"unknown element_id {element_id!r}")
        if element_id in seen:
            raise ValueError(f"duplicate element_id {element_id!r}")
        seen.add(element_id)

        original_term = str(row.get("original_term", "")).strip()
        if not original_term:
            raise ValueError(f"element {element_id}: original_term is required")

        alts_raw = row.get("alternatives")
        if not isinstance(alts_raw, list) or not alts_raw:
            raise ValueError(f"element {element_id}: alternatives must be a non-empty list")

        alternatives: list[AltTerm] = []
        for alt in alts_raw:
            if not isinstance(alt, dict):
                raise ValueError(f"element {element_id}: each alternative must be an object")
            term = str(alt.get("term", "")).strip()
            valence = str(alt.get("valence", "")).strip().lower()
            explicit_prov = alt.get("provenance")
            prov_raw = str(explicit_prov).strip() if explicit_prov is not None else None
            if not term:
                raise ValueError(f"element {element_id}: alternative term is required")
            if valence not in _VALID_VALENCES:
                raise ValueError(
                    f"element {element_id}: invalid valence {valence!r} "
                    f"(expected positive|neutral|negative)"
                )
            provenance = _resolve_provenance(valence, prov_raw or None)
            alternatives.append(
                AltTerm(term=term, valence=valence, provenance=provenance)
            )

        elements.append(
            AltElement(
                element_id=element_id,
                original_term=original_term,
                alternatives=alternatives,
            )
        )

    salience: list[str] = []
    if "salience" in data:
        salience_raw = data.get("salience")
        if salience_raw is None:
            salience = []
        else:
            salience = validate_salience(salience_raw, known_elements)

    return AltPoolOverlay(persona_id=pid, elements=elements, salience=salience)


def overlay_forbids_decon_fork(overlay_dict: dict[str, Any]) -> None:
    """Raise if overlay looks like a full decon fork (P-SSOT)."""
    forbidden = _DECON_TOP_LEVEL_KEYS & set(overlay_dict.keys())
    if forbidden:
        raise ValueError(
            f"overlay must not fork deconstruction keys: {sorted(forbidden)}"
        )
    alt_pool = overlay_dict.get("alt_pool")
    if isinstance(alt_pool, dict):
        nested = _DECON_TOP_LEVEL_KEYS & set(alt_pool.keys())
        if nested:
            raise ValueError(
                f"alt_pool must not embed deconstruction keys: {sorted(nested)}"
            )


def build_alt_pool_overlay(parsed: AltPoolOverlay) -> dict[str, Any]:
    """Serialize overlay and assert it does not fork neutral decon."""
    payload = parsed.to_dict()
    overlay_forbids_decon_fork(payload)
    return payload


def load_shared_contract(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(f"contract not found: {path}")
    return path.read_text(encoding="utf-8")


def load_persona_card(persona_id: str, prompts_dir: Path | None = None) -> str | None:
    base = prompts_dir or (repo_root() / "prompts" / "personas")
    path = base / persona_id / "persona_card.md"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return None


def render_persona_prompt(
    template: str,
    *,
    deconstruction: dict[str, Any],
    alt_pool: AltPoolOverlay | dict[str, Any] | None = None,
    expansion: dict[str, Any] | None = None,
    persona_card: str | None = None,
) -> str:
    """Render persona step prompt with decon + optional alt-pool overlay."""
    rendered = render_prompt(template, deconstruction=deconstruction)
    if alt_pool is not None:
        if isinstance(alt_pool, AltPoolOverlay):
            pool_payload = build_alt_pool_overlay(alt_pool)
        else:
            overlay_forbids_decon_fork(alt_pool)
            pool_payload = alt_pool
        pool_json = json.dumps(pool_payload, ensure_ascii=False, indent=2)
        rendered = rendered.replace("{{alt_pool_json}}", pool_json)
    if expansion is not None:
        expansion_json = json.dumps(expansion, ensure_ascii=False, indent=2)
        rendered = rendered.replace("{{expansion_json}}", expansion_json)
    else:
        rendered = rendered.replace("{{expansion_json}}", "—")
    if persona_card:
        rendered = rendered.replace("{{persona_card}}", persona_card.strip())
    else:
        rendered = rendered.replace("{{persona_card}}", "—")
    return rendered


def build_alt_creator_user_prompt(
    persona_id: str,
    deconstruction: dict[str, Any],
    *,
    prompts_dir: Path | None = None,
) -> str:
    contract = load_shared_contract(ALT_CREATOR_CONTRACT)
    card = load_persona_card(persona_id, prompts_dir)
    body = (
        f"# Persona: {persona_id}\n\n"
        f"## Contract\n\n{contract}\n\n"
        f"## Persona card\n\n{card or '—'}\n\n"
        f"## Neutral deconstruction (annotated)\n\n"
        f"{{{{deconstruction_json}}}}\n"
    )
    return render_persona_prompt(
        body,
        deconstruction=deconstruction,
        persona_card=card,
    )


def build_screenwriter_user_prompt(
    persona_id: str,
    deconstruction: dict[str, Any],
    alt_pool: AltPoolOverlay,
    *,
    expansion: dict[str, Any] | None = None,
    repair_context: str | None = None,
    prompts_dir: Path | None = None,
) -> str:
    contract = load_shared_contract(SCREENWRITER_CONTRACT)
    card = load_persona_card(persona_id, prompts_dir)
    if not alt_pool.salience:
        raise ValueError(f"{persona_id}: alt_pool.salience required for search-unit drafting")
    salience_json = json.dumps(list(alt_pool.salience), ensure_ascii=False, indent=2)
    body = (
        f"# Persona: {persona_id}\n\n"
        f"## Contract\n\n{contract}\n\n"
        f"## Persona card\n\n{card or '—'}\n\n"
        f"## Alt-pool overlay\n\n"
        f"{{{{alt_pool_json}}}}\n\n"
        f"## Neutral deconstruction (element + fragment ids)\n\n"
        f"{{{{deconstruction_json}}}}\n\n"
        f"## Salience ranking (greedy top-down center selection)\n\n"
        f"```json\n{salience_json}\n```\n"
    )
    if repair_context:
        body += (
            f"\n## Repair (previous attempt failed)\n\n"
            f"Fix the issue below and return valid JSON only.\n\n"
            f"{repair_context.strip()}\n"
        )
    return render_persona_prompt(
        body,
        deconstruction=deconstruction,
        alt_pool=alt_pool,
        expansion=expansion,
        persona_card=card,
    )


def _sync_llm_call_with_system(
    client: OpenAI, model: str, user_prompt: str, system_message: str
) -> str:
    messages = [
        {"role": "system", "content": system_message},
        {"role": "user", "content": user_prompt},
    ]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            response_format={"type": "json_object"},
        )
    except TypeError:
        response = client.chat.completions.create(model=model, messages=messages)
    except Exception:
        response = client.chat.completions.create(model=model, messages=messages)
    return (response.choices[0].message.content or "").strip()


async def run_alt_creator(
    persona_id: str,
    deconstruction: dict[str, Any],
    client: OpenAI,
    model: str,
    timeout: float,
    *,
    prompts_dir: Path | None = None,
) -> tuple[AltPoolOverlay | None, str | None]:
    known = known_element_ids(deconstruction)
    prompt = build_alt_creator_user_prompt(
        persona_id, deconstruction, prompts_dir=prompts_dir
    )
    try:
        raw = await asyncio.wait_for(
            asyncio.to_thread(
                _sync_llm_call_with_system, client, model, prompt, _SYSTEM_ALT
            ),
            timeout=timeout,
        )
    except TimeoutError:
        return None, f"alt_creator timed out after {timeout:g}s"
    except Exception as exc:
        return None, str(exc)

    if not raw.strip():
        return None, "alt_creator empty LLM response"
    try:
        overlay = parse_alt_pool_response(
            raw, persona_id=persona_id, known_elements=known
        )
        build_alt_pool_overlay(overlay)
        return overlay, None
    except (json.JSONDecodeError, ValueError) as exc:
        return None, f"alt_creator parse_error: {exc}"


async def run_screenwriter(
    persona_id: str,
    deconstruction: dict[str, Any],
    alt_pool: AltPoolOverlay,
    client: OpenAI,
    model: str,
    timeout: float,
    *,
    expansion: dict[str, Any] | None = None,
    repair_context: str | None = None,
    prompts_dir: Path | None = None,
) -> tuple[list[PseudoSegment] | None, str | None]:
    known_elements = known_element_ids(deconstruction)
    prompt = build_screenwriter_user_prompt(
        persona_id,
        deconstruction,
        alt_pool,
        expansion=expansion,
        repair_context=repair_context,
        prompts_dir=prompts_dir,
    )
    try:
        raw = await asyncio.wait_for(
            asyncio.to_thread(
                _sync_llm_call_with_system, client, model, prompt, _SYSTEM_SCREEN
            ),
            timeout=timeout,
        )
    except TimeoutError:
        return None, f"screenwriter timed out after {timeout:g}s"
    except Exception as exc:
        return None, str(exc)

    if not raw.strip():
        return None, "screenwriter empty LLM response"
    try:
        units = parse_search_units_response(
            raw,
            agent_id=persona_id,
            known_elements=known_elements,
            require_fit=True,
        )
        cleaned = [
            PseudoSegment(
                p.id,
                minimal_clean(p.text),
                p.source,
                p.warnings,
                fit=p.fit,
            )
            for p in units
        ]
        return cleaned, None
    except (json.JSONDecodeError, ValueError) as exc:
        return None, f"screenwriter parse_error: {exc}"


async def run_persona_pipeline(
    persona_id: str,
    deconstruction: dict[str, Any],
    provider: str | None = None,
    *,
    expansion: dict[str, Any] | None = None,
    prompts_dir: Path | None = None,
    client: OpenAI | None = None,
    model: str | None = None,
) -> PersonaPipelineResult:
    """Run decon → alt_creator → screenwriter → neutral + toned channel pseudos."""
    if not isinstance(deconstruction, dict) or not deconstruction:
        raise ValueError("deconstruction must be a non-empty dict")

    dec = copy.deepcopy(deconstruction)
    load_env()
    resolved = _resolve_provider(provider)
    timeout = _agent_llm_timeout()

    if client is None or model is None:
        try:
            client = client or get_llm_client(resolved)
            model = model or _model_name(resolved)
        except Exception as exc:
            return PersonaPipelineResult(
                persona_id=persona_id,
                overlay=AltPoolOverlay(persona_id=persona_id, elements=[]),
                error=str(exc),
            )

    alt_pool, alt_err = await run_alt_creator(
        persona_id, dec, client, model, timeout, prompts_dir=prompts_dir
    )
    if alt_err or alt_pool is None:
        return PersonaPipelineResult(
            persona_id=persona_id,
            overlay=AltPoolOverlay(persona_id=persona_id, elements=[]),
            error=alt_err or "alt_creator failed",
        )

    repair_retries: list[dict[str, str]] = []

    pseudos, sw_err = await run_screenwriter(
        persona_id,
        dec,
        alt_pool,
        client,
        model,
        timeout,
        expansion=expansion,
        prompts_dir=prompts_dir,
    )
    if sw_err or pseudos is None:
        repair_retries.append(
            {
                "stage": "screenwriter_parse",
                "attempt": "1",
                "error": sw_err or "screenwriter failed",
            }
        )
        pseudos, sw_err = await run_screenwriter(
            persona_id,
            dec,
            alt_pool,
            client,
            model,
            timeout,
            expansion=expansion,
            repair_context=sw_err or "screenwriter failed",
            prompts_dir=prompts_dir,
        )
        repair_retries.append(
            {
                "stage": "screenwriter_parse",
                "attempt": "2",
                "error": sw_err or "ok",
            }
        )

    if sw_err or pseudos is None:
        return PersonaPipelineResult(
            persona_id=persona_id,
            overlay=alt_pool,
            repair_retries=repair_retries,
            error=sw_err or "screenwriter failed",
        )

    workflow_payload = build_search_units_payload(
        persona_id=persona_id,
        alt_pool=alt_pool,
        pseudos=pseudos,
        expansion=expansion,
        known_elements=known_element_ids(dec),
        deconstruction=dec,
    )

    return PersonaPipelineResult(
        persona_id=persona_id,
        overlay=alt_pool,
        pseudos=pseudos,
        workflow=workflow_payload,
        repair_retries=repair_retries,
    )


def pipeline_result_to_dict(result: PersonaPipelineResult) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "persona_id": result.persona_id,
        "overlay": build_alt_pool_overlay(result.overlay),
        "pseudos": [pseudo_to_dict(p) for p in result.pseudos],
        "warnings": result.warnings,
    }
    if result.workflow:
        payload.update(result.workflow)
    if result.repair_retries:
        payload["repair_retries"] = result.repair_retries
    if result.error:
        payload["error"] = result.error
    return payload


async def _run_cli(args: argparse.Namespace) -> int:
    decon_path = Path(args.deconstruction_file)
    if not decon_path.is_file():
        print(f"error: deconstruction file not found: {decon_path}", file=sys.stderr)
        return 2

    deconstruction = load_deconstruction_from_file(decon_path)
    result = await run_persona_pipeline(
        args.persona_id,
        deconstruction,
        provider=args.provider,
    )
    payload = pipeline_result_to_dict(result)
    serialized = json.dumps(payload, ensure_ascii=False, indent=2)

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = _REPO_ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(serialized + "\n", encoding="utf-8")
        print(f"Wrote {out_path.resolve()}", file=sys.stderr)
    else:
        sys.stdout.buffer.write((serialized + "\n").encode("utf-8"))

    return 1 if result.error else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run Phase 3.7 persona pipeline (alt-creator → screenwriter).",
    )
    parser.add_argument(
        "--deconstruction-file",
        required=True,
        help="Path to facts.json.",
    )
    parser.add_argument(
        "--persona-id",
        required=True,
        help="Pearson persona_id (e.g. The-Ruler).",
    )
    parser.add_argument(
        "--out",
        help="Write JSON result to this path.",
    )
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider override.",
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
