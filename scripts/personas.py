"""personas.py · Phase 3.7 dual-step persona pipeline (scaffold).

Pipeline: neutral decon → alt_creator(persona) → screenwriter(persona) → pseudos(+fit).

Produces a flavored-decon **overlay** (alt-pool + element id refs only; no fork of full decon text).
Reuses agents.py for render_prompt, extract_json_object, parse_pseudos_response, and LLM calls.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from openai import OpenAI

from scripts.agents import (
    AgentOutput,
    PseudoSegment,
    _agent_llm_timeout,
    _known_fragment_ids,
    _model_name,
    _resolve_provider,
    annotate_fragment_ids,
    extract_json_object,
    load_deconstruction_from_file,
    minimal_clean,
    parse_pseudos_response,
    post_process_output,
    pseudo_to_dict,
    render_prompt,
)
from scripts.lib.env import load_env
from scripts.lib.llm import get_llm_client
from scripts.lib.paths import repo_root

Valence = Literal["positive", "neutral", "negative"]

ALT_CREATOR_CONTRACT = (
    repo_root() / "prompts" / "_shared" / "persona_alt_creator_contract.md"
)
SCREENWRITER_CONTRACT = (
    repo_root() / "prompts" / "_shared" / "persona_screenwriter_contract.md"
)
PERSONAS_SSOT = repo_root() / "docs" / "SSOT" / "personas-12.md"

_ELEMENT_SECTIONS: tuple[str, ...] = ("who", "where", "why", "how", "result")

# Top-level decon keys that must not appear on alt-pool overlay (P-SSOT: no fork).
_DECON_TOP_LEVEL_KEYS: frozenset[str] = frozenset(
    {"anchor", "when", "where", "who", "why", "how", "result", "deconstruction", "news"}
)

_VALID_VALENCES: frozenset[str] = frozenset({"positive", "neutral", "negative"})

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


@dataclass
class AltElement:
    element_id: str
    original_term: str
    alternatives: list[AltTerm]


@dataclass
class AltPoolOverlay:
    persona_id: str
    elements: list[AltElement]

    def to_dict(self) -> dict[str, Any]:
        return {
            "persona_id": self.persona_id,
            "alt_pool": {
                "elements": [
                    {
                        "element_id": el.element_id,
                        "original_term": el.original_term,
                        "alternatives": [
                            {"term": a.term, "valence": a.valence} for a in el.alternatives
                        ],
                    }
                    for el in self.elements
                ],
            },
        }


@dataclass
class PersonaPipelineResult:
    persona_id: str
    overlay: AltPoolOverlay
    pseudos: list[PseudoSegment] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
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


def _original_term_for_element(
    deconstruction: dict[str, Any], element_id: str
) -> str | None:
    ann = annotate_element_ids(deconstruction)
    section = element_id.split("-", 1)[0]
    items = ann.get(section)
    if not isinstance(items, list):
        return None
    for item in items:
        if isinstance(item, dict) and str(item.get("id")) == element_id:
            if section in ("how",):
                return str(item.get("text", "")).strip() or None
            return str(item.get("text", "")).strip() or None
    return None


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
        valences_seen: set[str] = set()
        for alt in alts_raw:
            if not isinstance(alt, dict):
                raise ValueError(f"element {element_id}: each alternative must be an object")
            term = str(alt.get("term", "")).strip()
            valence = str(alt.get("valence", "")).strip().lower()
            if not term:
                raise ValueError(f"element {element_id}: alternative term is required")
            if valence not in _VALID_VALENCES:
                raise ValueError(
                    f"element {element_id}: invalid valence {valence!r} "
                    f"(expected positive|neutral|negative)"
                )
            alternatives.append(AltTerm(term=term, valence=valence))
            valences_seen.add(valence)

        missing_valences = _VALID_VALENCES - valences_seen
        if missing_valences:
            raise ValueError(
                f"element {element_id}: missing valence bucket(s) "
                f"{sorted(missing_valences)}"
            )

        elements.append(
            AltElement(
                element_id=element_id,
                original_term=original_term,
                alternatives=alternatives,
            )
        )

    return AltPoolOverlay(persona_id=pid, elements=elements)


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
    prompts_dir: Path | None = None,
) -> str:
    contract = load_shared_contract(SCREENWRITER_CONTRACT)
    card = load_persona_card(persona_id, prompts_dir)
    body = (
        f"# Persona: {persona_id}\n\n"
        f"## Contract\n\n{contract}\n\n"
        f"## Persona card\n\n{card or '—'}\n\n"
        f"## Alt-pool overlay\n\n"
        f"{{{{alt_pool_json}}}}\n\n"
        f"## Neutral deconstruction (fragment ids)\n\n"
        f"{{{{deconstruction_json}}}}\n"
    )
    return render_persona_prompt(
        body,
        deconstruction=deconstruction,
        alt_pool=alt_pool,
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
    prompts_dir: Path | None = None,
) -> tuple[list[PseudoSegment] | None, str | None]:
    known_frags = _known_fragment_ids(annotate_fragment_ids(deconstruction))
    prompt = build_screenwriter_user_prompt(
        persona_id, deconstruction, alt_pool, prompts_dir=prompts_dir
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
        pseudos = parse_pseudos_response(
            raw,
            agent_id=persona_id,
            known_fragments=known_frags,
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
            for p in pseudos
        ]
        out = post_process_output(
            AgentOutput(
                agent_id=persona_id,
                persona_name=persona_id,
                role="persona",
                pseudos=cleaned,
            )
        )
        if out.error:
            return None, out.error
        return out.pseudos, None
    except (json.JSONDecodeError, ValueError) as exc:
        return None, f"screenwriter parse_error: {exc}"


async def run_persona_pipeline(
    persona_id: str,
    deconstruction: dict[str, Any],
    provider: str | None = None,
    *,
    prompts_dir: Path | None = None,
    client: OpenAI | None = None,
    model: str | None = None,
) -> PersonaPipelineResult:
    """Run decon → alt_creator → screenwriter for one persona."""
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

    pseudos, sw_err = await run_screenwriter(
        persona_id, dec, alt_pool, client, model, timeout, prompts_dir=prompts_dir
    )
    if sw_err or pseudos is None:
        return PersonaPipelineResult(
            persona_id=persona_id,
            overlay=alt_pool,
            error=sw_err or "screenwriter failed",
        )

    return PersonaPipelineResult(
        persona_id=persona_id,
        overlay=alt_pool,
        pseudos=pseudos,
    )


def pipeline_result_to_dict(result: PersonaPipelineResult) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "persona_id": result.persona_id,
        "overlay": build_alt_pool_overlay(result.overlay),
        "pseudos": [pseudo_to_dict(p) for p in result.pseudos],
        "warnings": result.warnings,
    }
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
        help="Path to reality-deconstructed.json.",
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
