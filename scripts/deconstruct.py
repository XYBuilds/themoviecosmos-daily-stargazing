"""deconstruct.py · Reality deconstruction agent (A0).

News JSON → LLM (MiMo 2.5 Pro by default) → validate → reality-deconstructed.json + .md.
Invalid JSON or schema issues are recorded in errors; the CLI does not hard-fail (MVP lenient).
"""

from __future__ import annotations

import argparse
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

from scripts.agents import (
    NewsItem,
    _field_value,
    _model_name,
    _resolve_provider,
    load_news_from_file,
    render_prompt,
)
from scripts.lib.env import load_env
from scripts.lib.llm import get_llm_client
from scripts.lib.paths import repo_root

_PROMPT_FILENAME = "A0_reality_deconstructor.md"
_SYSTEM_MESSAGE = (
    "You are a reality deconstructor. Output exactly one JSON object per the user "
    "message. No markdown fences, no explanation."
)

_WHEN_KEYS: tuple[str, ...] = (
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

_FORBIDDEN_KEYS: frozenset[str] = frozenset(
    {
        "skeleton",
        "load_bearing",
        "load-bearing",
        "seeds",
        "resonance",
        "resonance_type",
        "共振",
        "共振类型",
        "承重",
        "骨架",
    }
)

_LIST_FIELDS_WHERE: tuple[str, ...] = ("tags", "scene_archetype", "role")
_LIST_FIELDS_WHO: tuple[str, ...] = ("tags", "role_in_event", "relations")
_GEOCODE_KEYS: tuple[str, ...] = (
    "country",
    "state",
    "city",
    "district",
    "poi",
    "coordinates",
)

_JSON_FENCE_RE = re.compile(
    r"```(?:json)?\s*([\s\S]*?)\s*```",
    re.IGNORECASE,
)


def _agent_llm_timeout() -> float:
    load_env()
    raw = os.getenv("DECONSTRUCT_LLM_TIMEOUT", os.getenv("AGENT_LLM_TIMEOUT", "120")).strip()
    try:
        return float(raw)
    except ValueError:
        return 120.0


def load_deconstructor_prompt(prompts_dir: Path | None = None) -> str:
    base = prompts_dir or (repo_root() / "prompts")
    path = base / _PROMPT_FILENAME
    if not path.is_file():
        raise FileNotFoundError(f"Deconstructor prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def render_deconstructor_prompt(template: str, news: NewsItem) -> str:
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


def extract_json_object(raw: str) -> dict[str, Any]:
    text = raw.strip()
    if not text:
        raise ValueError("empty LLM response")

    fence = _JSON_FENCE_RE.search(text)
    if fence:
        text = fence.group(1).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("no JSON object found in LLM response")
    payload = text[start : end + 1]
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("root JSON value must be an object")
    return data


def _collect_forbidden_keys(obj: Any, path: str = "") -> list[str]:
    found: list[str] = []
    if isinstance(obj, dict):
        for key, value in obj.items():
            key_str = str(key)
            full = f"{path}.{key_str}" if path else key_str
            if key_str in _FORBIDDEN_KEYS:
                found.append(full)
            found.extend(_collect_forbidden_keys(value, full))
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            found.extend(_collect_forbidden_keys(item, f"{path}[{idx}]"))
    return found


def _ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, str) and not value.strip():
        return []
    return [value]


def _normalize_when(when: Any) -> dict[str, list[Any]]:
    base = {key: [] for key in _WHEN_KEYS}
    if not isinstance(when, dict):
        return base
    for key in _WHEN_KEYS:
        base[key] = _ensure_list(when.get(key))
    return base


def _normalize_geocode(geocode: Any) -> dict[str, Any]:
    empty = {k: None for k in _GEOCODE_KEYS}
    if not isinstance(geocode, dict):
        return empty
    out = dict(empty)
    for key in _GEOCODE_KEYS:
        val = geocode.get(key)
        if val is not None and str(val).strip():
            out[key] = str(val).strip()
    return out


def _normalize_where_item(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict):
        return {}
    out: dict[str, Any] = {
        "text": str(item.get("text") or "").strip() or None,
        "tags": [str(t).strip() for t in _ensure_list(item.get("tags")) if str(t).strip()],
        "geocode": _normalize_geocode(item.get("geocode")),
        "relative_pos": item.get("relative_pos"),
        "geopolitical": item.get("geopolitical"),
        "scene_archetype": [
            str(t).strip()
            for t in _ensure_list(item.get("scene_archetype"))
            if str(t).strip()
        ],
        "role": [str(t).strip() for t in _ensure_list(item.get("role")) if str(t).strip()],
        "intended_destination": item.get("intended_destination"),
        "scale": item.get("scale"),
        "trajectory": item.get("trajectory"),
        "contested_name": item.get("contested_name"),
    }
    if out["relative_pos"] is not None:
        out["relative_pos"] = str(out["relative_pos"]).strip() or None
    if out["geopolitical"] is not None:
        out["geopolitical"] = str(out["geopolitical"]).strip() or None
    if out["intended_destination"] is not None:
        out["intended_destination"] = str(out["intended_destination"]).strip() or None
    if out["scale"] is not None:
        out["scale"] = str(out["scale"]).strip() or None
    if out["trajectory"] is not None:
        out["trajectory"] = str(out["trajectory"]).strip() or None
    if out["contested_name"] is not None:
        out["contested_name"] = str(out["contested_name"]).strip() or None
    return out


def _normalize_who_item(item: Any) -> dict[str, Any]:
    if not isinstance(item, dict):
        return {}
    return {
        "text": str(item.get("text") or "").strip() or None,
        "tags": [str(t).strip() for t in _ensure_list(item.get("tags")) if str(t).strip()],
        "role_in_event": [
            str(t).strip()
            for t in _ensure_list(item.get("role_in_event"))
            if str(t).strip()
        ],
        "relations": [
            str(t).strip() for t in _ensure_list(item.get("relations")) if str(t).strip()
        ],
    }


def _normalize_fragments(items: Any, *, with_step: bool) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    if not isinstance(items, list):
        return out
    for idx, item in enumerate(items):
        if not isinstance(item, dict):
            continue
        text = str(item.get("text") or "").strip()
        if not text:
            continue
        row: dict[str, Any] = {"text": text}
        if with_step:
            step = item.get("step")
            if isinstance(step, int):
                row["step"] = step
            else:
                try:
                    row["step"] = int(step) if step is not None else idx + 1
                except (TypeError, ValueError):
                    row["step"] = idx + 1
        out.append(row)
    return out


def normalize_deconstructed(data: dict[str, Any]) -> dict[str, Any]:
    """Coerce LLM output toward contract §1 shape (lenient)."""
    anchor_raw = data.get("anchor")
    anchor: dict[str, Any] = {"dct": None, "report_locale": None}
    if isinstance(anchor_raw, dict):
        dct = anchor_raw.get("dct")
        anchor["dct"] = str(dct).strip() if dct is not None and str(dct).strip() else None
        rl = anchor_raw.get("report_locale")
        anchor["report_locale"] = (
            str(rl).strip() if rl is not None and str(rl).strip() else None
        )

    where_items = [
        _normalize_where_item(item)
        for item in _ensure_list(data.get("where"))
        if isinstance(item, dict)
    ]
    who_items = [
        _normalize_who_item(item)
        for item in _ensure_list(data.get("who"))
        if isinstance(item, dict)
    ]

    return {
        "anchor": anchor,
        "when": _normalize_when(data.get("when")),
        "where": where_items,
        "who": who_items,
        "why": _normalize_fragments(data.get("why"), with_step=False),
        "how": _normalize_fragments(data.get("how"), with_step=True),
        "result": _normalize_fragments(data.get("result"), with_step=False),
    }


def validate_deconstructed(data: dict[str, Any]) -> list[dict[str, str]]:
    """Return validation error records (empty if OK)."""
    errors: list[dict[str, str]] = []

    for path in _collect_forbidden_keys(data):
        errors.append(
            {
                "type": "forbidden_key",
                "message": f"forbidden field {path!r}",
            }
        )

    required_top = ("anchor", "when", "where", "who", "why", "how", "result")
    for key in required_top:
        if key not in data:
            errors.append(
                {
                    "type": "missing_key",
                    "message": f"missing top-level key {key!r}",
                }
            )

    when = data.get("when")
    if not isinstance(when, dict):
        errors.append({"type": "schema", "message": "when must be an object"})
    else:
        for key in _WHEN_KEYS:
            val = when.get(key)
            if val is not None and not isinstance(val, list):
                errors.append(
                    {
                        "type": "schema",
                        "message": f"when.{key} must be a list",
                    }
                )

    anchor = data.get("anchor")
    if anchor is not None and not isinstance(anchor, dict):
        errors.append({"type": "schema", "message": "anchor must be an object"})

    for section, list_key in (("where", "where"), ("who", "who")):
        items = data.get(list_key)
        if items is not None and not isinstance(items, list):
            errors.append(
                {"type": "schema", "message": f"{section} must be a list"}
            )

    for idx, item in enumerate(data.get("where") or []):
        if not isinstance(item, dict):
            continue
        for field in _LIST_FIELDS_WHERE:
            val = item.get(field)
            if val is not None and not isinstance(val, list):
                errors.append(
                    {
                        "type": "schema",
                        "message": f"where[{idx}].{field} must be a list",
                    }
                )

    for idx, item in enumerate(data.get("who") or []):
        if not isinstance(item, dict):
            continue
        for field in _LIST_FIELDS_WHO:
            val = item.get(field)
            if val is not None and not isinstance(val, list):
                errors.append(
                    {
                        "type": "schema",
                        "message": f"who[{idx}].{field} must be a list",
                    }
                )

    for idx, item in enumerate(data.get("how") or []):
        if isinstance(item, dict) and "step" not in item:
            errors.append(
                {
                    "type": "schema",
                    "message": f"how[{idx}] missing step",
                }
            )

    return errors


def _sync_llm_call(client: OpenAI, model: str, user_prompt: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": _SYSTEM_MESSAGE},
            {"role": "user", "content": user_prompt},
        ],
    )
    return (response.choices[0].message.content or "").strip()


def _error_record(error_type: str, message: str) -> dict[str, str]:
    return {"type": error_type, "message": message}


def run_deconstruct(
    news: NewsItem,
    provider: str | None = None,
    *,
    prompts_dir: Path | None = None,
) -> tuple[dict[str, Any] | None, list[dict[str, str]]]:
    """Call A0 LLM, parse JSON, normalize and validate. Returns (payload, errors)."""
    errors: list[dict[str, str]] = []
    load_env()
    resolved = _resolve_provider(provider)

    try:
        client = get_llm_client(resolved)
        model = _model_name(resolved)
    except Exception as exc:
        errors.append(_error_record("config", str(exc)))
        return None, errors

    template = load_deconstructor_prompt(prompts_dir)
    user_prompt = render_deconstructor_prompt(template, news)
    if not user_prompt.strip():
        errors.append(_error_record("prompt", "rendered prompt is empty"))
        return None, errors

    try:
        raw = _sync_llm_call(client, model, user_prompt)
    except Exception as exc:
        errors.append(_error_record("api_error", str(exc)))
        return None, errors

    try:
        parsed = extract_json_object(raw)
    except (json.JSONDecodeError, ValueError) as exc:
        errors.append(_error_record("parse", str(exc)))
        return None, errors

    normalized = normalize_deconstructed(parsed)
    errors.extend(validate_deconstructed(normalized))
    return normalized, errors


def _fmt_scalar(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value) if value else "—"
    return str(value)


def _render_where_block(item: dict[str, Any], index: int) -> list[str]:
    lines = [f"### Where {index + 1}: {_fmt_scalar(item.get('text'))}", ""]
    lines.append(f"- **tags**: {_fmt_scalar(item.get('tags'))}")
    geocode = item.get("geocode") or {}
    if isinstance(geocode, dict):
        geo_parts = [
            f"{k}={geocode.get(k)}" for k in _GEOCODE_KEYS if geocode.get(k)
        ]
        lines.append(f"- **geocode**: {', '.join(geo_parts) if geo_parts else '—'}")
    lines.append(f"- **scene_archetype**: {_fmt_scalar(item.get('scene_archetype'))}")
    lines.append(f"- **role**: {_fmt_scalar(item.get('role'))}")
    for key in (
        "relative_pos",
        "geopolitical",
        "intended_destination",
        "scale",
        "trajectory",
        "contested_name",
    ):
        val = item.get(key)
        if val:
            lines.append(f"- **{key}**: {val}")
    lines.append("")
    return lines


def _render_who_block(item: dict[str, Any], index: int) -> list[str]:
    lines = [f"### Who {index + 1}: {_fmt_scalar(item.get('text'))}", ""]
    lines.append(f"- **tags**: {_fmt_scalar(item.get('tags'))}")
    lines.append(f"- **role_in_event**: {_fmt_scalar(item.get('role_in_event'))}")
    rel = item.get("relations") or []
    if rel:
        lines.append(f"- **relations**: {_fmt_scalar(rel)}")
    lines.append("")
    return lines


def render_deconstructed_markdown(
    data: dict[str, Any],
    news: NewsItem,
    *,
    run_label: str = "",
    errors: list[dict[str, str]] | None = None,
) -> str:
    title = run_label or news.title
    lines = [
        f"# 现实解构 · {title}",
        "",
        "## 源新闻",
        f"- **title**: {news.title}",
        f"- **source** / **pub_time**: {news.source_name or '—'} / {news.pub_time or '—'}",
        f"- **summary**: {news.description}",
        "",
    ]

    if errors:
        lines.extend(["## 校验 / 解析备注", ""])
        for entry in errors:
            lines.append(f"- **{entry.get('type', '?')}**: {entry.get('message', '')}")
        lines.append("")

    anchor = data.get("anchor") or {}
    lines.extend(
        [
            "## Anchor",
            f"- **dct**: {_fmt_scalar(anchor.get('dct'))}",
            f"- **report_locale**: {_fmt_scalar(anchor.get('report_locale'))}",
            "",
            "## When",
        ]
    )
    when = data.get("when") or {}
    if isinstance(when, dict):
        for key in _WHEN_KEYS:
            vals = when.get(key) or []
            if vals:
                lines.append(f"- **{key}**: {_fmt_scalar(vals)}")

    lines.append("")
    lines.append("## Where")
    lines.append("")
    for idx, item in enumerate(data.get("where") or []):
        if isinstance(item, dict):
            lines.extend(_render_where_block(item, idx))

    lines.append("## Who")
    lines.append("")
    for idx, item in enumerate(data.get("who") or []):
        if isinstance(item, dict):
            lines.extend(_render_who_block(item, idx))

    lines.append("## Why")
    lines.append("")
    for item in data.get("why") or []:
        if isinstance(item, dict) and item.get("text"):
            lines.append(f"- {item['text']}")
    lines.append("")

    lines.append("## How")
    lines.append("")
    for item in data.get("how") or []:
        if isinstance(item, dict) and item.get("text"):
            step = item.get("step", "?")
            lines.append(f"- **{step}**. {item['text']}")
    lines.append("")

    lines.append("## Result")
    lines.append("")
    for item in data.get("result") or []:
        if isinstance(item, dict) and item.get("text"):
            lines.append(f"- {item['text']}")
    lines.append("")

    return "\n".join(lines)


def write_deconstruct_bundle(
    out_dir: Path,
    news: NewsItem,
    data: dict[str, Any] | None,
    errors: list[dict[str, str]],
) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    if data is not None:
        json_path = out_dir / "reality-deconstructed.json"
        json_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        md_path = out_dir / "reality-deconstructed.md"
        md_path.write_text(
            render_deconstructed_markdown(
                data, news, run_label=out_dir.name, errors=errors or None
            ),
            encoding="utf-8",
        )
    if errors:
        err_path = out_dir / "deconstruct-errors.json"
        err_path.write_text(
            json.dumps({"errors": errors}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )


def _run_cli(args: argparse.Namespace) -> int:
    news_path = Path(args.news_file)
    if not news_path.is_file():
        print(f"error: news file not found: {news_path}", file=sys.stderr)
        return 2

    news = load_news_from_file(news_path)
    out_dir = Path(args.out_dir)
    if not out_dir.is_absolute():
        out_dir = _REPO_ROOT / out_dir

    data, errors = run_deconstruct(news, provider=args.provider)
    write_deconstruct_bundle(out_dir, news, data, errors)

    if data is not None:
        print(f"Wrote {out_dir.resolve()}/reality-deconstructed.json", file=sys.stderr)
        print(f"Wrote {out_dir.resolve()}/reality-deconstructed.md", file=sys.stderr)
    if errors:
        for entry in errors:
            print(
                f"warning: [{entry.get('type')}] {entry.get('message')}",
                file=sys.stderr,
            )
        if args.out_dir:
            print(f"Wrote {out_dir.resolve()}/deconstruct-errors.json", file=sys.stderr)

    return 0


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
        required=True,
        help="Directory for reality-deconstructed.json and .md.",
    )
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider (default: DEFAULT_LLM_PROVIDER, use mimo for MiMo 2.5 Pro).",
    )
    args = parser.parse_args(argv)

    try:
        return _run_cli(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
