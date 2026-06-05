"""objective_expansion.py · Shared objective expansion pass (P-Expand).

Reads A0 verbatim deconstruction → LLM → hypernym ladder overlay with
objectivity touchstone filtering → reality-expanded.json.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from openai import OpenAI

from scripts.agents import annotate_fragment_ids, extract_json_object, load_deconstruction_from_file
from scripts.lib.env import default_llm_provider, load_env
from scripts.lib.llm import get_llm_client
from scripts.lib.paths import repo_root

_CONTRACT_FILE = repo_root() / "prompts" / "_shared" / "objective_expansion_contract.md"

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
    if not _CONTRACT_FILE.is_file():
        raise FileNotFoundError(f"Expansion contract not found: {_CONTRACT_FILE}")
    return _CONTRACT_FILE.read_text(encoding="utf-8")


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
    """Run P-Expand; return payload with expansion, errors, warnings."""
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


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run shared objective expansion pass on A0 deconstruction JSON.",
    )
    parser.add_argument(
        "--decon-file",
        required=True,
        help="Path to reality-deconstructed.json (or raw deconstruction object).",
    )
    parser.add_argument(
        "--out-dir",
        help="Directory for reality-expanded.json (default: same dir as decon file).",
    )
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider override (default: DEFAULT_LLM_PROVIDER).",
    )
    args = parser.parse_args(argv)

    decon_path = Path(args.decon_file)
    if not decon_path.is_file():
        print(f"error: deconstruction file not found: {decon_path}", file=sys.stderr)
        return 2

    try:
        deconstruction = load_deconstruction_from_file(decon_path)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    out_dir = Path(args.out_dir) if args.out_dir else decon_path.parent
    if not out_dir.is_absolute():
        out_dir = _REPO_ROOT / out_dir

    payload = run_expansion(deconstruction, provider=args.provider)
    json_path = write_outputs(payload, out_dir)

    print(f"Wrote {json_path.resolve()}", file=sys.stderr)
    if payload.get("errors"):
        print(f"completed with {len(payload['errors'])} error(s) (MVP: exit 0)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
