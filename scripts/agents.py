"""agents.py · Multi-agent writers' room (pseudo-overview).

Loads A1/A2/A4/A7 persona prompts, renders news placeholders, and calls the
LLM concurrently. Single-agent failures are recorded in ``errors`` without
blocking the rest.

MVP scope (1.1): core models, persona load, template render, async LLM, minimal
text cleaning. CLI and full post-processing live in 1.2 / 1.3.
"""

from __future__ import annotations

import asyncio
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from openai import OpenAI

from scripts.lib.env import default_llm_provider, load_env
from scripts.lib.llm import get_llm_client
from scripts.lib.paths import repo_root

# Explicit MVP persona files (no C*, no _shared).
PERSONA_FILENAMES: tuple[str, ...] = (
    "A1_reality_recorder.md",
    "A2_sociologist.md",
    "A4_mythologist.md",
    "A7_chaos_theorist.md",
)

RUN_ORDER: tuple[str, ...] = ("A2", "A4", "A7", "A1")

_ROLE_BY_AGENT: dict[str, str] = {
    "A1": "baseline",
    "A2": "creative",
    "A4": "creative",
    "A7": "creative",
}

_MODEL_ENV: dict[str, str] = {
    "mimo": "MIMO_MODEL",
    "deepseek": "DEEPSEEK_MODEL",
}

_SYSTEM_MESSAGE = "Follow the instructions in the user message exactly."

_PLACEHOLDER_EMPTY = "—"
_SOURCE_EMPTY = "unknown"

_PREFIX_PATTERNS: tuple[str, ...] = (
    "sure,",
    "sure.",
    "certainly,",
    "certainly.",
    "of course,",
    "of course.",
    "as requested,",
    "here is the ",
    "here is ",
    "here's the ",
    "here's ",
)

_AGENT_ID_RE = re.compile(r"^(A\d+)_", re.IGNORECASE)


@dataclass
class NewsItem:
    title: str
    description: str
    pub_time: str = ""
    source_name: str = ""
    url: str = ""


@dataclass
class Persona:
    agent_id: str
    persona_name: str
    role: str
    template: str
    filename: str


@dataclass
class AgentOutput:
    agent_id: str
    persona_name: str
    role: str
    text: str
    warnings: list[str] = field(default_factory=list)
    error: str | None = None


def _agent_llm_timeout() -> float:
    load_env()
    raw = os.getenv("AGENT_LLM_TIMEOUT", "120").strip()
    try:
        return float(raw)
    except ValueError:
        return 120.0


def _resolve_provider(explicit: str | None) -> str:
    if explicit is not None:
        return explicit.strip().lower()
    return default_llm_provider()


def _model_name(provider: str) -> str:
    load_env()
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


def _field_value(value: str, *, source_name: bool = False) -> str:
    if not value or not str(value).strip():
        return _SOURCE_EMPTY if source_name else _PLACEHOLDER_EMPTY
    return str(value).strip()


def _agent_id_from_filename(filename: str) -> str:
    match = _AGENT_ID_RE.match(filename)
    if not match:
        raise ValueError(f"Cannot parse agent_id from persona filename: {filename!r}")
    return match.group(1).upper()


def _persona_name_from_md(content: str, agent_id: str) -> str:
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            body = stripped[2:].strip()
            if "·" in body:
                return body.split("·", 1)[1].strip()
            if body.upper().startswith(agent_id):
                rest = body[len(agent_id) :].strip().lstrip("·").strip()
                if rest:
                    return rest
            return body
    return agent_id


def load_personas(prompts_dir: Path | None = None) -> list[Persona]:
    """Load MVP personas from explicit filenames under *prompts_dir*."""
    base = prompts_dir or (repo_root() / "prompts")
    personas: list[Persona] = []
    for filename in PERSONA_FILENAMES:
        path = base / filename
        if not path.is_file():
            raise FileNotFoundError(f"Persona prompt not found: {path}")
        content = path.read_text(encoding="utf-8")
        agent_id = _agent_id_from_filename(filename)
        role = _ROLE_BY_AGENT.get(agent_id, "creative")
        personas.append(
            Persona(
                agent_id=agent_id,
                persona_name=_persona_name_from_md(content, agent_id),
                role=role,
                template=content,
                filename=filename,
            )
        )
    return personas


def render_prompt(template: str, news: NewsItem) -> str:
    """Replace news placeholders; empty fields become em-dash or 'unknown'."""
    replacements = {
        "{{title}}": _field_value(news.title),
        "{{description}}": _field_value(news.description),
        "{{pub_time}}": _field_value(news.pub_time),
        "{{source_name}}": _field_value(news.source_name, source_name=True),
    }
    rendered = template
    for key, value in replacements.items():
        rendered = rendered.replace(key, value)
    return rendered


def _collapse_paragraph(text: str) -> str:
    collapsed = re.sub(r"\s*\n+\s*", " ", text.strip())
    return re.sub(r" +", " ", collapsed).strip()


def _strip_common_prefix(text: str) -> str:
    result = text.strip()
    while True:
        lower = result.lower()
        matched = False
        for prefix in _PREFIX_PATTERNS:
            if lower.startswith(prefix):
                result = result[len(prefix) :].lstrip()
                matched = True
                break
        if not matched:
            break
    return result


def minimal_clean(text: str) -> str:
    """Minimal 1.1 cleaning: strip, single paragraph, drop common preambles."""
    cleaned = _collapse_paragraph(text)
    return _strip_common_prefix(cleaned)


def _sync_llm_call(client: OpenAI, model: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_MESSAGE},
            {"role": "user", "content": user_prompt},
        ],
    )
    return (response.choices[0].message.content or "").strip()


def _error_type(message: str) -> str:
    lower = message.lower()
    if "timeout" in lower:
        return "timeout"
    if "missing" in lower and "api" in lower:
        return "config"
    return "api_error"


def _error_record(agent_id: str, message: str) -> dict[str, str]:
    return {
        "agent_id": agent_id,
        "type": _error_type(message),
        "message": message,
    }


async def _run_one_agent(
    persona: Persona,
    news: NewsItem,
    client: OpenAI,
    model: str,
    timeout: float,
) -> AgentOutput:
    rendered = render_prompt(persona.template, news)
    if not rendered.strip():
        msg = "rendered prompt is empty"
        return AgentOutput(
            agent_id=persona.agent_id,
            persona_name=persona.persona_name,
            role=persona.role,
            text="",
            error=msg,
        )

    try:
        raw = await asyncio.wait_for(
            asyncio.to_thread(_sync_llm_call, client, model, rendered),
            timeout=timeout,
        )
    except TimeoutError:
        msg = f"LLM call timed out after {timeout:g}s"
        return AgentOutput(
            agent_id=persona.agent_id,
            persona_name=persona.persona_name,
            role=persona.role,
            text="",
            error=msg,
        )
    except Exception as exc:
        return AgentOutput(
            agent_id=persona.agent_id,
            persona_name=persona.persona_name,
            role=persona.role,
            text="",
            error=str(exc),
        )

    if not raw.strip():
        return AgentOutput(
            agent_id=persona.agent_id,
            persona_name=persona.persona_name,
            role=persona.role,
            text="",
            error="empty LLM response",
        )

    return AgentOutput(
        agent_id=persona.agent_id,
        persona_name=persona.persona_name,
        role=persona.role,
        text=minimal_clean(raw),
    )


def _select_personas(
    personas: list[Persona], agent_ids: list[str] | None
) -> list[Persona]:
    by_id = {p.agent_id: p for p in personas}
    if agent_ids is None:
        return [by_id[aid] for aid in RUN_ORDER if aid in by_id]
    wanted = {aid.strip().upper() for aid in agent_ids if aid.strip()}
    return [by_id[aid] for aid in RUN_ORDER if aid in wanted and aid in by_id]


async def run_all(
    news: NewsItem,
    provider: str | None = None,
    agent_ids: list[str] | None = None,
    *,
    prompts_dir: Path | None = None,
) -> tuple[list[AgentOutput], list[dict]]:
    """Run all (or selected) personas concurrently; return outputs and errors."""
    load_env()
    resolved_provider = _resolve_provider(provider)
    timeout = _agent_llm_timeout()

    try:
        client = get_llm_client(resolved_provider)
        model = _model_name(resolved_provider)
    except Exception as exc:
        msg = str(exc)
        personas = load_personas(prompts_dir)
        selected = _select_personas(personas, agent_ids)
        outputs = [
            AgentOutput(
                agent_id=p.agent_id,
                persona_name=p.persona_name,
                role=p.role,
                text="",
                error=msg,
            )
            for p in selected
        ]
        errors = [_error_record(o.agent_id, msg) for o in outputs]
        return outputs, errors

    personas = load_personas(prompts_dir)
    selected = _select_personas(personas, agent_ids)
    if not selected:
        return [], []

    tasks = [
        _run_one_agent(p, news, client, model, timeout) for p in selected
    ]
    outputs = list(await asyncio.gather(*tasks))

    errors: list[dict] = []
    for out in outputs:
        if out.error:
            errors.append(_error_record(out.agent_id, out.error))

    return outputs, errors
