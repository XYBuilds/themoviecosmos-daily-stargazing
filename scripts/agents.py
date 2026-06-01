"""agents.py · Multi-agent writers' room (pseudo-overview).

Loads A1/A2/A4/A7 persona prompts, injects reality-deconstructed JSON, and calls the
LLM concurrently. Each agent returns 3 pseudos with fragment provenance.

MVP scope: persona load, template render, async LLM, JSON parse, post-processing,
and CLI.
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from openai import OpenAI

from scripts.lib.env import default_llm_provider, load_env
from scripts.lib.llm import get_llm_client
from scripts.lib.paths import repo_root

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

_SYSTEM_MESSAGE = (
    "You are a screenwriter's-room agent. Follow the user message exactly. "
    "Return only valid JSON matching the multi-pseudo output contract."
)

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
_CAPITALIZED_NAME_RE = re.compile(
    r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b"
)
_SENTENCE_END_RE = re.compile(r"[.!?](?:\s+|$)")
_JSON_FENCE_RE = re.compile(
    r"```(?:json)?\s*([\s\S]*?)\s*```",
    re.IGNORECASE,
)

MIN_WORDS_SHORT = 40
MAX_WORDS = 120
EXPECTED_PSEUDO_COUNT = 3
EXPECTED_PSEUDO_IDS: tuple[str, ...] = ("p1", "p2", "p3")

_BRAND_WORDS: frozenset[str] = frozenset(
    {
        "Tesla",
        "Twitter",
        "X",
        "Apple",
        "Google",
        "Microsoft",
        "Meta",
        "Amazon",
        "OpenAI",
        "Facebook",
        "Instagram",
        "Netflix",
        "Disney",
        "Nvidia",
        "SpaceX",
    }
)

_NEWS_CLICHES: tuple[str, ...] = (
    "reportedly",
    "according to",
    "sources say",
    "sources said",
    "it is reported",
    "据报道",
    "据说",
    "消息称",
)

_REFUSAL_SNIPPETS: tuple[str, ...] = (
    "i cannot",
    "i can't",
    "i am unable",
    "i'm unable",
    "as an ai",
    "as a language model",
    "i'm not able to",
    "cannot fulfill",
    "can't fulfill",
    "cannot comply",
    "can't comply",
)


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
class PseudoSegment:
    id: str
    text: str
    source: dict[str, Any]
    warnings: list[str] = field(default_factory=list)


@dataclass
class AgentOutput:
    agent_id: str
    persona_name: str
    role: str
    pseudos: list[PseudoSegment] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    error: str | None = None

    @property
    def text(self) -> str:
        """First pseudo text (legacy retrieve until Phase 3.5.4)."""
        return self.pseudos[0].text if self.pseudos else ""


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


def annotate_fragment_ids(deconstruction: dict[str, Any]) -> dict[str, Any]:
    """Return a copy of deconstruction with stable why/how/result ids."""
    annotated = copy.deepcopy(deconstruction)
    for section in ("why", "result"):
        items = annotated.get(section)
        if not isinstance(items, list):
            continue
        for idx, item in enumerate(items):
            if isinstance(item, dict):
                item["id"] = f"{section}-{idx}"
    how_items = annotated.get("how")
    if isinstance(how_items, list):
        for idx, item in enumerate(how_items):
            if isinstance(item, dict):
                item["id"] = f"how-{idx}"
    return annotated


def _known_fragment_ids(deconstruction: dict[str, Any]) -> set[str]:
    ids: set[str] = set()
    for section in ("why", "how", "result"):
        for item in deconstruction.get(section) or []:
            if isinstance(item, dict) and item.get("id"):
                ids.add(str(item["id"]))
    return ids


def _how_indices(fragment_ids: list[str]) -> list[int]:
    indices: list[int] = []
    for fid in fragment_ids:
        if fid.startswith("how-"):
            try:
                indices.append(int(fid.split("-", 1)[1]))
            except ValueError:
                continue
    return sorted(indices)


def _how_contiguous(fragment_ids: list[str]) -> bool:
    indices = _how_indices(fragment_ids)
    if len(indices) <= 1:
        return True
    return indices == list(range(indices[0], indices[-1] + 1))


def render_prompt(
    template: str,
    news: NewsItem | None = None,
    *,
    deconstruction: dict[str, Any] | None = None,
) -> str:
    """Replace template placeholders with news and/or annotated deconstruction JSON."""
    rendered = template
    if deconstruction is not None:
        annotated = annotate_fragment_ids(deconstruction)
        payload = json.dumps(annotated, ensure_ascii=False, indent=2)
        rendered = rendered.replace("{{deconstruction_json}}", payload)
    if news is not None:
        replacements = {
            "{{title}}": _field_value(news.title),
            "{{description}}": _field_value(news.description),
            "{{pub_time}}": _field_value(news.pub_time),
            "{{source_name}}": _field_value(news.source_name, source_name=True),
        }
        for key, value in replacements.items():
            rendered = rendered.replace(key, value)
    return rendered


def extract_json_object(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if not text:
        raise ValueError("empty LLM response")
    fence = _JSON_FENCE_RE.search(text)
    if fence:
        text = fence.group(1).strip()
    if not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            text = text[start : end + 1]
    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("top-level JSON must be an object")
    return data


def parse_pseudos_response(
    raw: str,
    *,
    agent_id: str,
    known_fragments: set[str],
) -> list[PseudoSegment]:
    """Parse LLM JSON into pseudo segments with validation."""
    data = extract_json_object(raw)
    rows = data.get("pseudos")
    if not isinstance(rows, list):
        raise ValueError("JSON must contain a 'pseudos' array")
    if len(rows) != EXPECTED_PSEUDO_COUNT:
        raise ValueError(
            f"expected {EXPECTED_PSEUDO_COUNT} pseudos, got {len(rows)}"
        )

    segments: list[PseudoSegment] = []
    seen_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("each pseudo must be an object")
        pseudo_id = str(row.get("id", "")).strip()
        if pseudo_id not in EXPECTED_PSEUDO_IDS:
            raise ValueError(f"invalid pseudo id {pseudo_id!r}")
        if pseudo_id in seen_ids:
            raise ValueError(f"duplicate pseudo id {pseudo_id!r}")
        seen_ids.add(pseudo_id)

        text = str(row.get("text", "")).strip()
        if not text:
            raise ValueError(f"pseudo {pseudo_id} has empty text")

        source = row.get("source")
        if not isinstance(source, dict):
            source = {}
        fragments = source.get("fragments")
        if fragments is None:
            fragments = source.get("fragment_ids", [])
        if not isinstance(fragments, list):
            raise ValueError(f"pseudo {pseudo_id}: source.fragments must be a list")
        frag_ids = [str(f).strip() for f in fragments if str(f).strip()]
        unknown = [f for f in frag_ids if f not in known_fragments]
        if unknown:
            raise ValueError(
                f"pseudo {pseudo_id}: unknown fragment ids {unknown}"
            )
        if not _how_contiguous(frag_ids):
            raise ValueError(
                f"pseudo {pseudo_id}: how-* fragments must be contiguous"
            )

        segments.append(
            PseudoSegment(
                id=pseudo_id,
                text=text,
                source={
                    "agent_id": agent_id,
                    "fragments": frag_ids,
                },
            )
        )

    if seen_ids != set(EXPECTED_PSEUDO_IDS):
        missing = set(EXPECTED_PSEUDO_IDS) - seen_ids
        raise ValueError(f"missing pseudo ids: {sorted(missing)}")

    segments.sort(key=lambda p: EXPECTED_PSEUDO_IDS.index(p.id))
    return segments


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
    """Strip, single paragraph, drop common preambles."""
    cleaned = _collapse_paragraph(text)
    return _strip_common_prefix(cleaned)


def word_count(text: str) -> int:
    return len(text.split()) if text.strip() else 0


def _truncate_at_sentence(text: str, max_words: int) -> str:
    words = text.split()
    if len(words) <= max_words:
        return text
    prefix = " ".join(words[:max_words])
    last_end = None
    for match in _SENTENCE_END_RE.finditer(prefix):
        last_end = match.end()
    if last_end and last_end > len(prefix) // 3:
        return prefix[:last_end].strip()
    return prefix.strip()


def _looks_like_refusal(text: str) -> bool:
    lower = text.lower()
    return any(snippet in lower for snippet in _REFUSAL_SNIPPETS)


def _collect_deentify_warnings(text: str) -> list[str]:
    """Heuristic warnings (load-bearing proper names are allowed per ADR-0002)."""
    warnings: list[str] = []
    for brand in _BRAND_WORDS:
        if re.search(rf"\b{re.escape(brand)}\b", text):
            warnings.append(f"deentify_warning: brand name {brand!r}")
    lower = text.lower()
    for cliche in _NEWS_CLICHES:
        if cliche in lower:
            warnings.append(f"deentify_warning: news cliché {cliche!r}")
    return warnings


def post_process_pseudo(segment: PseudoSegment) -> PseudoSegment:
    text = segment.text
    warnings = list(segment.warnings)

    if _looks_like_refusal(text):
        segment.text = ""
        segment.warnings = warnings + ["refusal_detected"]
        return segment

    wc = word_count(text)
    if wc > MAX_WORDS:
        text = _truncate_at_sentence(text, MAX_WORDS)
        warnings.append("truncated_over_length")
    elif wc < MIN_WORDS_SHORT:
        warnings.append("short_output")

    warnings.extend(_collect_deentify_warnings(text))
    segment.text = text
    segment.warnings = warnings
    return segment


def post_process_output(output: AgentOutput) -> AgentOutput:
    if output.error:
        return output

    if not output.pseudos:
        output.error = "no pseudos produced"
        return output

    agent_warnings: list[str] = []
    processed: list[PseudoSegment] = []
    for seg in output.pseudos:
        seg = post_process_pseudo(seg)
        if not seg.text.strip():
            output.error = f"pseudo {seg.id} empty after cleaning"
            return output
        agent_warnings.extend(seg.warnings)
        processed.append(seg)

    output.pseudos = processed
    output.warnings = agent_warnings
    return output


def _sync_llm_call(client: OpenAI, model: str, user_prompt: str) -> str:
    messages = [
        {"role": "system", "content": _SYSTEM_MESSAGE},
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
    deconstruction: dict[str, Any],
    client: OpenAI,
    model: str,
    timeout: float,
    *,
    news: NewsItem | None = None,
) -> AgentOutput:
    known = _known_fragment_ids(annotate_fragment_ids(deconstruction))
    rendered = render_prompt(
        persona.template,
        news,
        deconstruction=deconstruction,
    )
    if not rendered.strip():
        msg = "rendered prompt is empty"
        return AgentOutput(
            agent_id=persona.agent_id,
            persona_name=persona.persona_name,
            role=persona.role,
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
            error=msg,
        )
    except Exception as exc:
        return AgentOutput(
            agent_id=persona.agent_id,
            persona_name=persona.persona_name,
            role=persona.role,
            error=str(exc),
        )

    if not raw.strip():
        return AgentOutput(
            agent_id=persona.agent_id,
            persona_name=persona.persona_name,
            role=persona.role,
            error="empty LLM response",
        )

    try:
        pseudos = parse_pseudos_response(
            raw,
            agent_id=persona.agent_id,
            known_fragments=known,
        )
    except (json.JSONDecodeError, ValueError) as exc:
        return AgentOutput(
            agent_id=persona.agent_id,
            persona_name=persona.persona_name,
            role=persona.role,
            error=f"parse_error: {exc}",
        )

    cleaned_segments = [PseudoSegment(p.id, minimal_clean(p.text), p.source) for p in pseudos]
    return post_process_output(
        AgentOutput(
            agent_id=persona.agent_id,
            persona_name=persona.persona_name,
            role=persona.role,
            pseudos=cleaned_segments,
        )
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
    news: NewsItem | None,
    provider: str | None = None,
    agent_ids: list[str] | None = None,
    *,
    deconstruction: dict[str, Any],
    prompts_dir: Path | None = None,
) -> tuple[list[AgentOutput], list[dict]]:
    """Run all (or selected) personas concurrently; return outputs and errors."""
    if not isinstance(deconstruction, dict) or not deconstruction:
        raise ValueError("deconstruction must be a non-empty dict")

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
        _run_one_agent(
            p,
            deconstruction,
            client,
            model,
            timeout,
            news=news,
        )
        for p in selected
    ]
    outputs = list(await asyncio.gather(*tasks))

    errors: list[dict] = []
    for out in outputs:
        if out.error:
            errors.append(_error_record(out.agent_id, out.error))

    return outputs, errors


def news_to_dict(news: NewsItem) -> dict[str, str]:
    return {
        "title": news.title,
        "description": news.description,
        "pub_time": news.pub_time,
        "source_name": news.source_name,
        "url": news.url,
    }


def pseudo_to_dict(segment: PseudoSegment) -> dict[str, Any]:
    return {
        "id": segment.id,
        "text": segment.text,
        "source": segment.source,
        "warnings": segment.warnings,
    }


def agent_to_dict(output: AgentOutput) -> dict[str, Any]:
    pseudos = [pseudo_to_dict(p) for p in output.pseudos]
    return {
        "agent_id": output.agent_id,
        "persona_name": output.persona_name,
        "role": output.role,
        "pseudos": pseudos,
        "text": output.text,
        "warnings": output.warnings,
    }


def load_news_from_file(path: Path) -> NewsItem:
    """Load a news item from JSON (title and description required)."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("news file must be a JSON object")
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    if not title or not description:
        raise ValueError("news JSON requires non-empty title and description")
    return NewsItem(
        title=title,
        description=description,
        pub_time=str(data.get("pub_time", "") or ""),
        source_name=str(data.get("source_name", "") or ""),
        url=str(data.get("url", "") or ""),
    )


def load_deconstruction_from_file(path: Path) -> dict[str, Any]:
    """Load deconstruction object from A0 output or raw contract JSON."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("deconstruction file must be a JSON object")
    if isinstance(data.get("deconstruction"), dict):
        dec = data["deconstruction"]
    else:
        dec = data
    if not dec:
        raise ValueError("deconstruction JSON is empty")
    required = ("anchor", "when", "where", "who", "why", "how", "result")
    missing = [k for k in required if k not in dec]
    if missing:
        raise ValueError(f"deconstruction missing keys: {missing}")
    return dec


def build_result_payload(
    news: NewsItem | None,
    outputs: list[AgentOutput],
    errors: list[dict],
    *,
    deconstruction: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "agents": [agent_to_dict(o) for o in outputs],
        "errors": errors,
    }
    if news is not None:
        payload["news"] = news_to_dict(news)
    if deconstruction is not None:
        payload["deconstruction"] = annotate_fragment_ids(deconstruction)
    return payload


def _parse_agent_ids(raw: str | None) -> list[str] | None:
    if raw is None or not raw.strip():
        return None
    return [part.strip() for part in raw.split(",") if part.strip()]


async def _run_cli(args: argparse.Namespace) -> int:
    decon_path = Path(args.deconstruction_file)
    if not decon_path.is_file():
        print(f"error: deconstruction file not found: {decon_path}", file=sys.stderr)
        return 2

    deconstruction = load_deconstruction_from_file(decon_path)
    news: NewsItem | None = None
    if args.news_file:
        news_path = Path(args.news_file)
        if not news_path.is_file():
            print(f"error: news file not found: {news_path}", file=sys.stderr)
            return 2
        news = load_news_from_file(news_path)

    outputs, errors = await run_all(
        news,
        provider=args.provider,
        agent_ids=_parse_agent_ids(args.agents),
        deconstruction=deconstruction,
    )
    payload = build_result_payload(
        news,
        outputs,
        errors,
        deconstruction=deconstruction,
    )
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

    successes = sum(
        1 for o in outputs if o.pseudos and not o.error
    )
    if outputs and successes == 0:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run A1/A2/A4/A7 pseudo agents on reality-deconstructed JSON.",
    )
    parser.add_argument(
        "--deconstruction-file",
        required=True,
        help="Path to reality-deconstructed.json (or raw deconstruction object).",
    )
    parser.add_argument(
        "--news-file",
        help="Optional news JSON for payload metadata (not injected into prompts).",
    )
    parser.add_argument(
        "--out",
        help="Write JSON result to this path; otherwise print UTF-8 JSON to stdout.",
    )
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider override (default: DEFAULT_LLM_PROVIDER from .env).",
    )
    parser.add_argument(
        "--agents",
        help="Comma-separated agent ids to run, e.g. A2,A4 (default: all MVP agents).",
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
