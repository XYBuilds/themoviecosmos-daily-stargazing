"""fragment_ladder.py · Inlined objective expansion for the fragment ladder.

Phase 3.12.1 folded the standalone P-Expand pass (formerly
`scripts/objective_expansion.py`) into this module. The shared objective
expansion still runs **once per news item** and stays persona-independent;
only the file boundary and the on-disk `reality-expanded.json` orchestration
moved here. The objectivity touchstone and hypernym filter remain pure
functions reused by `scripts/personas.py` when building fragment ladders.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from openai import OpenAI

from scripts.agents import annotate_fragment_ids, extract_json_object
from scripts.lib.env import default_llm_provider, load_env
from scripts.lib.llm import get_llm_client

_MODEL_ENV: dict[str, str] = {
    "mimo": "MIMO_MODEL",
    "deepseek": "DEEPSEEK_MODEL",
}

_SYSTEM_MESSAGE = (
    "You are an objective expansion extractor. Follow the user message exactly. "
    "Return only valid JSON matching the objective expansion contract."
)

_ELEMENT_SECTIONS: tuple[str, ...] = ("who", "where", "why", "how", "result")

# Lens-framed patterns that fail the objectivity touchstone (A2 vs A4 would disagree).
_LENS_FRAMED_SNIPPETS: tuple[str, ...] = (
    "destiny's cage",
    "destiny cage",
    "fateful cage",
    "fateful prison",
    "fateful trap",
    "crushing the",
    "crushing individual",
    "systemic oppression",
    "apocalyptic reckoning",
    "dying regime",
    "宿命的牢笼",
    "宿命",
    "牢笼",
    "碾压",
    "牺牲品",
    "反讽",
    "悲剧",
    "ironic",
    "irony",
    "tragic",
    "plot twist",
    "turning point",
    "climax",
)

_FORBIDDEN_EXPANSION_KEYS: frozenset[str] = frozenset(
    {
        "tags",
        "geocode",
        "coordinates",
        "scale",
        "scene_archetype",
        "valence",
        "alternatives",
        "lens",
        "hypernym",
    }
)

# Inlined objective expansion contract (formerly
# prompts/_shared/objective_expansion_contract.md). One shared pass after A0
# verbatim extract; hypernym ladders only, persona-independent.
_EXPANSION_CONTRACT = """# Objective Expansion Contract (P-Expand · shared hypernym ladder)

> **Role:** One **shared** pass after A0 verbatim extract. Input = `reality-deconstructed.json`. Output = `reality-expanded.json` with **hypernym ladders only** — persona-independent objective floor for the neutral channel and toned anchors.

## Input

- Injected `{{deconstruction_json}}`: verbatim A0 output (`anchor`, `when`, `where`, `who`, `why`, `how`, `result`) with stable element ids:
  - `who-{i}`, `where-{i}`, `why-{i}`, `how-{i}`, `result-{i}`

{{deconstruction_json}}

## Output format

Return **only** valid JSON (no markdown fences, no preamble):

```json
{
  "elements": [
    {
      "element_id": "where-0",
      "surface": "Dharavi, Mumbai",
      "hypernyms": ["Mumbai", "Maharashtra", "India", "South Asia", "slum", "urban neighborhood"]
    },
    {
      "element_id": "who-0",
      "surface": "residents across central-northern India",
      "hypernyms": ["civilians", "affected population"]
    }
  ]
}
```

## Rules

1. **Hypernym only:** For each covered element, list broader terms from **more specific → more abstract** (English). Do not repeat the surface verbatim as a hypernym.
2. **Objectivity touchstone (mandatory):** Every hypernym must pass — *"Would A2 (sociologist) and A4 (mythologist) disagree on this label?"* If **yes** → it is **lens**, not objective → **omit**.
   - **Keep:** taxonomic / geographic generalizations (`slum`, `India`, `extreme weather`, `power grid`).
   - **Reject:** dramatic or valence-laden framing (`destiny's cage`, `crushing the individual`, `fateful prison`, `systemic oppression` when not verbatim in source).
3. **Fact-entailed:** Hypernyms must follow from A0 facts. Do not add events, actors, charges, or unstated causality.
4. **Shared, not per-persona:** One expansion for all personas. Persona differences belong in P-Lens.
5. **Coverage:** Prefer `who` and `where`; include `why` / `how` / `result` when a clean objective generalization exists. Skip when no defensible hypernym passes the touchstone.
6. **No inert fields:** Do not output `geocode`, `coordinates`, `scale`, `scene_archetype`, `tags`, `valence`, `alternatives`, or `lens` terms.

## Touchstone examples

| Surface (verbatim) | Keep (objective hypernym) | Reject (lens) |
| --- | --- | --- |
| Dharavi slum, Mumbai | `slum`, `Mumbai`, `India` | `destiny's cage`, `fateful trap` |
| central-northern India heatwave | `India`, `extreme weather`, `climate hazard` | `crushing the powerless`, `apocalyptic reckoning` |
| national power grid | `power grid`, `critical infrastructure` | `fragile lifeline of a dying regime` |
"""


def _resolve_provider(explicit: str | None) -> str:
    if explicit is not None:
        return explicit.strip().lower()
    return default_llm_provider()


def _model_name(provider: str) -> str:
    load_env()
    if provider == "mimo":
        pro = os.getenv("MIMO_MODEL_PRO", "").strip()
        if pro:
            return pro
    env_key = _MODEL_ENV.get(provider)
    if not env_key:
        raise ValueError(f"Unknown provider {provider!r}")
    model = os.getenv(env_key, "").strip()
    if not model:
        raise RuntimeError(
            f"Missing {env_key} for provider {provider!r}. "
            "Copy .env.example to .env and set the model name."
        )
    return model


def _expansion_timeout() -> float:
    load_env()
    raw = os.getenv("EXPANSION_LLM_TIMEOUT", os.getenv("AGENT_LLM_TIMEOUT", "120")).strip()
    try:
        return float(raw)
    except ValueError:
        return 120.0


def element_id_for(section: str, index: int) -> str:
    return f"{section}-{index}"


def surface_text_for_element(deconstruction: dict[str, Any], element_id: str) -> str | None:
    """Return verbatim surface text for a stable element id."""
    if "-" not in element_id:
        return None
    section, _, idx_s = element_id.partition("-")
    if section not in _ELEMENT_SECTIONS:
        return None
    try:
        idx = int(idx_s)
    except ValueError:
        return None
    items = deconstruction.get(section)
    if not isinstance(items, list) or idx >= len(items):
        return None
    item = items[idx]
    if not isinstance(item, dict):
        return None
    return str(item.get("text", "") or "")


def list_expandable_elements(deconstruction: dict[str, Any]) -> list[dict[str, str]]:
    """Enumerate elements eligible for hypernym expansion with stable ids."""
    elements: list[dict[str, str]] = []
    for section in _ELEMENT_SECTIONS:
        items = deconstruction.get(section)
        if not isinstance(items, list):
            continue
        for idx, item in enumerate(items):
            if not isinstance(item, dict):
                continue
            text = str(item.get("text", "") or "").strip()
            if not text:
                continue
            elements.append(
                {
                    "element_id": element_id_for(section, idx),
                    "surface": text,
                }
            )
    return elements


def passes_objectivity_touchstone(term: str) -> bool:
    """True when A2 & A4 would not disagree — objective hypernym candidate."""
    cleaned = term.strip()
    if not cleaned:
        return False
    lower = cleaned.lower()
    for snippet in _LENS_FRAMED_SNIPPETS:
        if snippet.lower() in lower:
            return False
    return True


def filter_hypernyms(
    hypernyms: list[str],
    *,
    surface: str,
) -> tuple[list[str], list[str]]:
    """Apply touchstone; drop surface duplicates. Returns (kept, rejected)."""
    kept: list[str] = []
    rejected: list[str] = []
    surface_norm = surface.strip().lower()
    seen: set[str] = set()
    for raw in hypernyms:
        term = str(raw).strip()
        if not term:
            continue
        norm = term.lower()
        if norm == surface_norm or norm in seen:
            rejected.append(term)
            continue
        if not passes_objectivity_touchstone(term):
            rejected.append(term)
            continue
        seen.add(norm)
        kept.append(term)
    return kept, rejected


def load_expansion_contract() -> str:
    return _EXPANSION_CONTRACT


def render_expansion_prompt(deconstruction: dict[str, Any]) -> str:
    contract = load_expansion_contract()
    annotated = annotate_fragment_ids(deconstruction)
    # Attach stable who/where ids for the model (why/how/result already annotated).
    for section in ("who", "where"):
        items = annotated.get(section)
        if not isinstance(items, list):
            continue
        for idx, item in enumerate(items):
            if isinstance(item, dict):
                item["id"] = element_id_for(section, idx)
    payload = json.dumps(annotated, ensure_ascii=False, indent=2)
    rendered = contract.replace("{{deconstruction_json}}", payload)
    if "{{deconstruction_json}}" in rendered:
        rendered = f"{rendered.rstrip()}\n\n## Deconstruction input\n\n```json\n{payload}\n```\n"
    return rendered


def _collect_forbidden_keys(obj: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_lower = str(key).lower()
            if key in _FORBIDDEN_EXPANSION_KEYS or key_lower in _FORBIDDEN_EXPANSION_KEYS:
                found.append(f"{path}.{key}" if path else str(key))
            child_path = f"{path}.{key}" if path else str(key)
            found.extend(_collect_forbidden_keys(value, child_path))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            found.extend(_collect_forbidden_keys(item, f"{path}[{idx}]"))
    return found


def validate_expansion(
    data: dict[str, Any],
    deconstruction: dict[str, Any],
) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for expansion contract compliance."""
    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(_collect_forbidden_keys(data))

    elements = data.get("elements")
    if elements is None:
        errors.append("missing top-level key: elements")
        return errors, warnings
    if not isinstance(elements, list):
        errors.append("elements must be an array")
        return errors, warnings

    known_surfaces = {
        e["element_id"]: e["surface"] for e in list_expandable_elements(deconstruction)
    }

    for idx, row in enumerate(elements):
        prefix = f"elements[{idx}]"
        if not isinstance(row, dict):
            errors.append(f"{prefix} must be an object")
            continue
        element_id = row.get("element_id")
        surface = row.get("surface")
        hypernyms = row.get("hypernyms")
        if not element_id:
            errors.append(f"{prefix} missing element_id")
            continue
        if element_id not in known_surfaces:
            errors.append(f"{prefix} unknown element_id: {element_id}")
        if not isinstance(surface, str) or not surface.strip():
            errors.append(f"{prefix} missing surface")
        elif element_id in known_surfaces and surface.strip() != known_surfaces[element_id]:
            warnings.append(
                f"{prefix} surface mismatch for {element_id}: "
                f"expected {known_surfaces[element_id]!r}, got {surface!r}"
            )
        if hypernyms is None:
            errors.append(f"{prefix} missing hypernyms")
            continue
        if not isinstance(hypernyms, list):
            errors.append(f"{prefix}.hypernyms must be a list")
            continue
        kept, rejected = filter_hypernyms(
            [str(h) for h in hypernyms],
            surface=str(surface or known_surfaces.get(element_id, "")),
        )
        if rejected:
            warnings.append(f"{prefix} touchstone rejected: {rejected}")
        if not kept:
            warnings.append(f"{prefix} no hypernyms passed touchstone")

    return errors, warnings


def apply_touchstone_to_expansion(expansion: dict[str, Any]) -> dict[str, Any]:
    """Return a copy with hypernyms filtered through the objectivity touchstone."""
    result = json.loads(json.dumps(expansion))
    elements = result.get("elements")
    if not isinstance(elements, list):
        return result
    for row in elements:
        if not isinstance(row, dict):
            continue
        surface = str(row.get("surface", "") or "")
        raw = row.get("hypernyms")
        if not isinstance(raw, list):
            continue
        kept, _ = filter_hypernyms([str(h) for h in raw], surface=surface)
        row["hypernyms"] = kept
        row["rejected_hypernyms"] = [
            h for h in raw if str(h).strip() and str(h).strip() not in kept
        ]
    return result


def _sync_llm_call(client: OpenAI, model: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_MESSAGE},
            {"role": "user", "content": user_prompt},
        ],
    )
    return (response.choices[0].message.content or "").strip()


def run_expansion(
    deconstruction: dict[str, Any],
    *,
    provider: str | None = None,
) -> dict[str, Any]:
    """Run the shared P-Expand pass; return payload with expansion, errors, warnings."""
    load_env()
    resolved = _resolve_provider(provider)
    errors: list[dict[str, str]] = []
    validation_warnings: list[str] = []
    expansion: dict[str, Any] | None = None

    try:
        user_prompt = render_expansion_prompt(deconstruction)
        client = get_llm_client(resolved)
        model = _model_name(resolved)
        raw = _sync_llm_call(client, model, user_prompt)
    except Exception as exc:
        errors.append({"type": "llm_error", "message": str(exc)})
        return _build_payload(deconstruction, expansion, errors, validation_warnings, resolved, None)

    try:
        parsed = extract_json_object(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        errors.append({"type": "parse_error", "message": str(exc)})
        return _build_payload(deconstruction, expansion, errors, validation_warnings, resolved, model)

    val_errors, val_warnings = validate_expansion(parsed, deconstruction)
    validation_warnings.extend(val_warnings)
    if val_errors:
        for msg in val_errors:
            errors.append({"type": "validation_error", "message": msg})

    filtered = apply_touchstone_to_expansion(parsed)
    expansion = filtered

    return _build_payload(
        deconstruction,
        expansion,
        errors,
        validation_warnings,
        resolved,
        model,
    )


def _build_payload(
    deconstruction: dict[str, Any],
    expansion: dict[str, Any] | None,
    errors: list[dict[str, str]],
    validation_warnings: list[str],
    provider: str,
    model: str | None,
) -> dict[str, Any]:
    return {
        "agent": "P-Expand",
        "persona": "Objective Expansion",
        "provider": provider,
        "model": model,
        "deconstruction": deconstruction,
        "expansion": expansion,
        "errors": errors,
        "validation_warnings": validation_warnings,
    }


def write_outputs(payload: dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "reality-expanded.json"
    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return json_path