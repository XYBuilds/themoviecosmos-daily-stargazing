"""extract.py · Reality deconstruction agent (A0).

News JSON → LLM (MiMo 2.5 Pro by default) → validate contract JSON →
write reality-deconstructed.json + reality-deconstructed.md.

Invalid JSON or validation issues are recorded in ``errors``; MVP does not
hard-fail the process (exit 0 when the CLI ran, unless news input is invalid).
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import re
import sys
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from openai import OpenAI

from scripts.agents import NewsItem, load_news_from_file, news_to_dict, render_prompt
from scripts.lib.env import default_llm_provider, load_env
from scripts.lib.llm import get_llm_client
from scripts.lib.paths import repo_root

_PROMPT_FILE = "extract_deconstructor.md"

_MODEL_ENV: dict[str, str] = {
    "mimo": "MIMO_MODEL",
    "deepseek": "DEEPSEEK_MODEL",
}

_SYSTEM_MESSAGE = (
    "You are a structured JSON extractor for English news. Follow the user message exactly. "
    "Return only valid JSON matching the specified verbatim A0 schema. English in, English out."
)

_JSON_FENCE_RE = re.compile(
    r"```(?:json)?\s*([\s\S]*?)\s*```",
    re.IGNORECASE,
)

_FORBIDDEN_KEYS: frozenset[str] = frozenset(
    {
        "skeleton",
        "load_bearing",
        "seeds",
        "resonance_type",
        "resonancetype",
        "共振类型",
        "hypernym",
        "hypernyms",
        "alternatives",
        "valence",
    }
)

_INERT_KEYS: frozenset[str] = frozenset(
    {
        "tags",
        "geocode",
        "coordinates",
        "scale",
        "scene_archetype",
    }
)

_WHEN_ARRAY_KEYS: tuple[str, ...] = (
    "absolute",
    "relative",
    "daypart",
    "season",
    "fuzzy_era",
    "cultural",
    "anchored",
    "duration",
    "recurrence",
    "modality",
    "timezone",
)

_SUBJECTIVE_SNIPPETS: tuple[str, ...] = (
    "反讽",
    "ironic",
    "irony",
    "悲剧",
    "tragic",
    "碾压",
    "宿命",
    "牺牲品",
    "握权",
    "核心赌注",
    "turning point",
    "climax",
    "plot twist",
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


def _deconstruct_timeout() -> float:
    load_env()
    raw = os.getenv("DECONSTRUCT_LLM_TIMEOUT", os.getenv("AGENT_LLM_TIMEOUT", "120")).strip()
    try:
        return float(raw)
    except ValueError:
        return 120.0


def load_deconstructor_prompt(prompts_dir: Path | None = None) -> str:
    base = prompts_dir or (repo_root() / "prompts")
    path = base / _PROMPT_FILE
    if not path.is_file():
        raise FileNotFoundError(f"Deconstructor prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def extract_json_object(raw: str) -> dict[str, Any]:
    """Parse JSON from model output (raw JSON or fenced block)."""
    text = raw.strip()
    if not text:
        raise ValueError("empty LLM response")

    fence = _JSON_FENCE_RE.search(text)
    if fence:
        text = fence.group(1).strip()

    # If extra prose surrounds JSON, try first { ... } span.
    if not text.startswith("{"):
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            text = text[start : end + 1]

    data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError("top-level JSON must be an object")
    return data


def _collect_forbidden_keys(obj: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_lower = str(key).lower()
            if key in _FORBIDDEN_KEYS or key_lower in _FORBIDDEN_KEYS:
                found.append(f"{path}.{key}" if path else str(key))
            if key in _INERT_KEYS or key_lower in _INERT_KEYS:
                found.append(f"inert_field:{path}.{key}" if path else f"inert_field:{key}")
            child_path = f"{path}.{key}" if path else str(key)
            found.extend(_collect_forbidden_keys(value, child_path))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            found.extend(_collect_forbidden_keys(item, f"{path}[{idx}]"))
    return found


def strip_inert_fields(data: dict[str, Any]) -> dict[str, Any]:
    """Return a deep copy with inert keys removed from where/who objects."""
    cleaned = copy.deepcopy(data)
    for section in ("where", "who"):
        items = cleaned.get(section)
        if not isinstance(items, list):
            continue
        for item in items:
            if not isinstance(item, dict):
                continue
            for key in _INERT_KEYS:
                item.pop(key, None)
            geo = item.get("geocode")
            if isinstance(geo, dict):
                geo.pop("coordinates", None)
    return cleaned


def _require_list(value: Any, field: str, errors: list[str]) -> None:
    if value is None:
        return
    if not isinstance(value, list):
        errors.append(f"{field} must be a list, got {type(value).__name__}")


def _scan_subjective_text(obj: Any, path: str, warnings: list[str]) -> None:
    if isinstance(obj, str):
        lower = obj.lower()
        for snippet in _SUBJECTIVE_SNIPPETS:
            if snippet.lower() in lower:
                warnings.append(f"possible_subjective_framing at {path}: contains {snippet!r}")
        return
    if isinstance(obj, dict):
        for key, value in obj.items():
            child = f"{path}.{key}" if path else str(key)
            _scan_subjective_text(value, child, warnings)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            _scan_subjective_text(item, f"{path}[{idx}]", warnings)


def validate_deconstruction(data: dict[str, Any]) -> tuple[list[str], list[str]]:
    """Return (errors, warnings) for contract compliance."""
    errors: list[str] = []
    warnings: list[str] = []

    errors.extend(_collect_forbidden_keys(data))

    required_top = ("anchor", "when", "where", "who", "why", "how", "result")
    for key in required_top:
        if key not in data:
            errors.append(f"missing top-level key: {key}")

    anchor = data.get("anchor")
    if anchor is not None and not isinstance(anchor, dict):
        errors.append("anchor must be an object")

    when = data.get("when")
    if when is not None:
        if not isinstance(when, dict):
            errors.append("when must be an object")
        else:
            for sub in _WHEN_ARRAY_KEYS:
                if sub in when:
                    _require_list(when[sub], f"when.{sub}", errors)

    where = data.get("where")
    if where is not None:
        if not isinstance(where, list):
            errors.append("where must be an array")
        else:
            for idx, item in enumerate(where):
                if not isinstance(item, dict):
                    errors.append(f"where[{idx}] must be an object")
                    continue
                _require_list(item.get("role"), f"where[{idx}].role", errors)
                _require_list(item.get("relations"), f"where[{idx}].relations", errors)

    who = data.get("who")
    if who is not None:
        if not isinstance(who, list):
            errors.append("who must be an array")
        else:
            for idx, item in enumerate(who):
                if not isinstance(item, dict):
                    errors.append(f"who[{idx}] must be an object")
                    continue
                _require_list(item.get("role_in_event"), f"who[{idx}].role_in_event", errors)
                _require_list(item.get("relations"), f"who[{idx}].relations", errors)

    for block_name in ("why", "result"):
        block = data.get(block_name)
        if block is not None:
            if not isinstance(block, list):
                errors.append(f"{block_name} must be an array")
            else:
                for idx, item in enumerate(block):
                    if not isinstance(item, dict) or "text" not in item:
                        errors.append(f"{block_name}[{idx}] must be object with text")

    how = data.get("how")
    if how is not None:
        if not isinstance(how, list):
            errors.append("how must be an array")
        else:
            for idx, item in enumerate(how):
                if not isinstance(item, dict):
                    errors.append(f"how[{idx}] must be an object")
                elif "text" not in item:
                    errors.append(f"how[{idx}] missing text")
                elif "step" not in item:
                    errors.append(f"how[{idx}] missing step")

    _scan_subjective_text(data, "", warnings)
    return errors, warnings


def _sync_llm_call(client: OpenAI, model: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_MESSAGE},
            {"role": "user", "content": user_prompt},
        ],
    )
    return (response.choices[0].message.content or "").strip()


def run_deconstruct(
    news: NewsItem,
    *,
    provider: str | None = None,
    prompts_dir: Path | None = None,
) -> dict[str, Any]:
    """Run A0 deconstruction; return payload with news, deconstruction, errors, warnings."""
    load_env()
    resolved = _resolve_provider(provider)
    errors: list[dict[str, str]] = []
    validation_warnings: list[str] = []
    deconstruction: dict[str, Any] | None = None

    try:
        template = load_deconstructor_prompt(prompts_dir)
        user_prompt = render_prompt(template, news)
        client = get_llm_client(resolved)
        model = _model_name(resolved)
        raw = _sync_llm_call(client, model, user_prompt)
    except Exception as exc:
        errors.append({"type": "llm_error", "message": str(exc)})
        return _build_payload(news, deconstruction, errors, validation_warnings, resolved, None)

    try:
        parsed = extract_json_object(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        errors.append({"type": "parse_error", "message": str(exc)})
        return _build_payload(news, deconstruction, errors, validation_warnings, resolved, model)

    val_errors, val_warnings = validate_deconstruction(parsed)
    validation_warnings.extend(val_warnings)
    if val_errors:
        for msg in val_errors:
            errors.append({"type": "validation_error", "message": msg})
    deconstruction = strip_inert_fields(parsed)

    return _build_payload(news, deconstruction, errors, validation_warnings, resolved, model)


def _build_payload(
    news: NewsItem,
    deconstruction: dict[str, Any] | None,
    errors: list[dict[str, str]],
    validation_warnings: list[str],
    provider: str,
    model: str | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "agent": "A0",
        "persona": "Reality Deconstructor",
        "provider": provider,
        "model": model,
        "news": news_to_dict(news),
        "deconstruction": deconstruction,
        "errors": errors,
        "validation_warnings": validation_warnings,
    }
    return payload


def render_deconstruction_md(payload: dict[str, Any], *, run_id: str | None = None) -> str:
    """Human-readable view for editors (Obsidian-friendly)."""
    news = payload.get("news") or {}
    title = news.get("title", "—")
    rid = run_id or "deconstruction"
    lines = [
        f"# 现实解构 · {rid}",
        "",
        "## 元信息",
        f"- **title**: {title}",
        f"- **source** / **pub_time**: {news.get('source_name') or '—'} / {news.get('pub_time') or '—'}",
        f"- **url**: {news.get('url') or '—'}",
        "",
    ]

    dec = payload.get("deconstruction")
    if not dec:
        lines.extend(["## 解构结果", "", "_（无有效解构 JSON）_", ""])
        if payload.get("errors"):
            lines.append("## Errors")
            for err in payload["errors"]:
                lines.append(f"- `{err.get('type', 'error')}`: {err.get('message', '')}")
            lines.append("")
        return "\n".join(lines)

    anchor = dec.get("anchor") or {}
    lines.extend(
        [
            "## Anchor",
            f"- **dct**: {anchor.get('dct')}",
            f"- **report_locale**: {anchor.get('report_locale')}",
            "",
        ]
    )

    when = dec.get("when") or {}
    lines.append("## When")
    for key in _WHEN_ARRAY_KEYS:
        vals = when.get(key) or []
        if vals:
            lines.append(f"- **{key}**: " + "; ".join(str(v) for v in vals))
    lines.append("")

    lines.append("## Where")
    for idx, place in enumerate(dec.get("where") or [], start=1):
        if not isinstance(place, dict):
            continue
        lines.append(f"### {idx}. {place.get('text', '—')}")
        for field in ("role", "relations"):
            vals = place.get(field)
            if vals:
                lines.append(f"- {field}: {', '.join(str(v) for v in vals)}")
        for field in (
            "relative_pos",
            "geopolitical",
            "trajectory",
            "intended_destination",
            "contested_name",
        ):
            if place.get(field):
                lines.append(f"- {field}: {place[field]}")
        lines.append("")

    lines.append("## Who")
    for idx, who in enumerate(dec.get("who") or [], start=1):
        if not isinstance(who, dict):
            continue
        lines.append(f"### {idx}. {who.get('text', '—')}")
        if who.get("role_in_event"):
            lines.append(f"- role_in_event: {', '.join(str(r) for r in who['role_in_event'])}")
        if who.get("relations"):
            lines.append(f"- relations: {', '.join(str(r) for r in who['relations'])}")
        lines.append("")

    for section, label in (("why", "Why"), ("how", "How"), ("result", "Result")):
        items = dec.get(section) or []
        if not items:
            continue
        lines.append(f"## {label}")
        for item in items:
            if not isinstance(item, dict):
                continue
            if section == "how":
                step = item.get("step", "?")
                lines.append(f"- [{step}] {item.get('text', '')}")
            else:
                lines.append(f"- {item.get('text', '')}")
        lines.append("")

    if payload.get("validation_warnings"):
        lines.append("## Validation warnings")
        for w in payload["validation_warnings"]:
            lines.append(f"- {w}")
        lines.append("")

    if payload.get("errors"):
        lines.append("## Errors")
        for err in payload["errors"]:
            lines.append(f"- `{err.get('type', 'error')}`: {err.get('message', '')}")
        lines.append("")

    return "\n".join(lines)


def write_outputs(
    payload: dict[str, Any],
    out_dir: Path,
    *,
    run_id: str | None = None,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    json_path = out_dir / "reality-deconstructed.json"
    md_path = out_dir / "reality-deconstructed.md"

    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    md_path.write_text(render_deconstruction_md(payload, run_id=run_id), encoding="utf-8")
    return json_path, md_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run A0 reality deconstructor on a news JSON file.",
    )
    parser.add_argument(
        "--news-file",
        required=True,
        help="Path to news JSON (title and description required).",
    )
    parser.add_argument(
        "--out-dir",
        help="Directory for reality-deconstructed.json and .md (default: output/deconstruct/<run-id>).",
    )
    parser.add_argument(
        "--run-id",
        help="Label for markdown header and default output folder name.",
    )
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider override (default: DEFAULT_LLM_PROVIDER).",
    )
    args = parser.parse_args(argv)

    news_path = Path(args.news_file)
    if not news_path.is_file():
        print(f"error: news file not found: {news_path}", file=sys.stderr)
        return 2

    try:
        news = load_news_from_file(news_path)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    run_id = args.run_id or news_path.stem
    out_dir = Path(args.out_dir) if args.out_dir else _REPO_ROOT / "output" / "deconstruct" / run_id
    if not out_dir.is_absolute():
        out_dir = _REPO_ROOT / out_dir

    payload = run_deconstruct(news, provider=args.provider)
    json_path, md_path = write_outputs(payload, out_dir, run_id=run_id)

    print(f"Wrote {json_path.resolve()}", file=sys.stderr)
    print(f"Wrote {md_path.resolve()}", file=sys.stderr)
    if payload.get("errors"):
        print(f"completed with {len(payload['errors'])} error(s) (MVP: exit 0)", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
