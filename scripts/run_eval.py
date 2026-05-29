"""run_eval.py · 评测管线：新闻 → agents → retrieve → 评测 Markdown.

串联 Phase 1 agents 与 Phase 2 retrieve，输出供总编填分的 Eval 简报。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import unicodedata
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.agents import RUN_ORDER, agent_to_dict, load_news_from_file, run_all
from scripts.retrieve import retrieve_from_agents

_PSEUDO_ORDER: tuple[str, ...] = RUN_ORDER


def slugify(text: str, *, max_len: int = 60) -> str:
    """ASCII-safe slug from arbitrary title text."""
    normalized = unicodedata.normalize("NFKD", text)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", ascii_text.lower()).strip("-")
    if len(slug) > max_len:
        slug = slug[:max_len].rstrip("-")
    return slug


def default_run_id(title: str) -> str:
    slug = slugify(title)
    if slug:
        return slug
    return datetime.now(UTC).strftime("%Y%m%d-%H%M%S")


def resolve_out_path(run_id: str, out: str | None) -> Path:
    if out:
        path = Path(out)
        if not path.is_absolute():
            path = _REPO_ROOT / path
        return path
    return _REPO_ROOT / "output" / "Eval" / f"{run_id}.md"


def _eval_date(pub_time: str) -> str:
    if pub_time and pub_time.strip():
        return pub_time.strip()[:10] if len(pub_time.strip()) >= 10 else pub_time.strip()
    return datetime.now(UTC).strftime("%Y-%m-%d")


def _agent_outputs_by_id(outputs: list) -> dict[str, Any]:
    return {o.agent_id.upper(): o for o in outputs}


def _format_meta(run_id: str, news) -> str:
    lines = [
        "## 元信息",
        f"- date: {_eval_date(news.pub_time)}",
        f"- news_url: {news.url or '—'}",
        f"- run_id: {run_id}",
    ]
    return "\n".join(lines)


def _format_reality(news) -> str:
    source = news.source_name or "—"
    pub_time = news.pub_time or "—"
    return "\n".join(
        [
            "## 现实波澜",
            f"- **title**: {news.title}",
            f"- **source** / **pub_time**: {source} / {pub_time}",
            f"- **summary**: {news.description}",
        ]
    )


def _format_pseudo(outputs: list) -> str:
    by_id = _agent_outputs_by_id(outputs)
    lines = ["## 伪剧情（英文）"]
    for agent_id in _PSEUDO_ORDER:
        out = by_id.get(agent_id)
        if out is None:
            continue
        label = f"**{agent_id}** {out.persona_name}"
        if out.role == "baseline":
            label += " `[baseline]`"
        text = out.text.strip() if out.text else "—"
        if out.error:
            text = f"*(error: {out.error})*"
        lines.append(f"- {label}: {text}")
    return "\n".join(lines)


def _format_errors(errors: list[dict]) -> str:
    lines = ["## errors"]
    if not errors:
        lines.append("（无）")
        return "\n".join(lines)
    for entry in errors:
        agent_id = entry.get("agent_id", "?")
        message = entry.get("message") or entry.get("error") or str(entry)
        lines.append(f"- **{agent_id}**: {message}")
    return "\n".join(lines)


def _format_divergence(divergence: dict[str, Any]) -> str:
    payload = json.dumps(divergence, ensure_ascii=False, indent=2)
    return "\n".join(
        [
            "## divergence",
            "<details>",
            "<summary>展开 JSON</summary>",
            "",
            "```json",
            payload,
            "```",
            "",
            "</details>",
        ]
    )


def _candidate_heading(cand: dict[str, Any]) -> str:
    title = cand.get("title") or "Untitled"
    year = cand.get("release_year")
    year_part = f" ({year})" if year is not None else ""

    triggered = cand.get("triggered_by") or []
    if triggered:
        agents_tag = ", ".join(triggered)
        bracket = f"[{agents_tag}]"
    elif cand.get("also_baseline"):
        bracket = "[baseline only]"
    else:
        bracket = ""

    suffix = f" {bracket}" if bracket else ""
    return f"### {title}{year_part}{suffix}"


def _format_candidates(candidates: list[dict[str, Any]]) -> str:
    lines = [f"## 候选星轨（共 {len(candidates)} 部）"]
    if not candidates:
        lines.append("（无候选 — agents 可能全部失败或 pseudo 为空）")
        return "\n".join(lines)

    for cand in candidates:
        lines.append("")
        lines.append(_candidate_heading(cand))
        lines.append(f"- **tmdb_id**: {cand.get('tmdb_id', '')}")
        sim = cand.get("similarity")
        sim_text = f"{sim:.4f}" if isinstance(sim, (int, float)) else str(sim)
        lines.append(f"- **相似度**: {sim_text}")
        lines.append(f"- **genres** / **language**: {cand.get('genres', '')} / {cand.get('language', '')}")
        overview = (cand.get("overview") or "").replace("\n", " ").strip()
        lines.append(f"- **overview**: {overview or '—'}")
        lines.append(f"- **跳转**: {cand.get('movie_url', '')}")
        lines.append(f"- **also_baseline**: {str(bool(cand.get('also_baseline'))).lower()}")
        lines.append("- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->")

    return "\n".join(lines)


def render_eval_markdown(
    run_id: str,
    news,
    outputs: list,
    errors: list[dict],
    retrieve_result: dict[str, Any],
) -> str:
    """Assemble the full eval briefing Markdown."""
    sections = [
        f"# 评测 · {run_id}",
        "",
        _format_meta(run_id, news),
        "",
        _format_reality(news),
        "",
        _format_pseudo(outputs),
        "",
        _format_errors(errors),
        "",
        _format_divergence(retrieve_result.get("divergence", {})),
        "",
        _format_candidates(retrieve_result.get("candidates", [])),
        "",
    ]
    return "\n".join(sections)


async def run_eval_pipeline(
    news,
    *,
    provider: str | None = None,
) -> tuple[list, list[dict], dict[str, Any]]:
    """Run agents then retrieve; return outputs, errors, retrieve payload."""
    outputs, errors = await run_all(news, provider=provider)
    agents_list = [agent_to_dict(o) for o in outputs]
    retrieve_result = retrieve_from_agents(agents_list, errors)
    return outputs, errors, retrieve_result


async def _run_cli(args: argparse.Namespace) -> int:
    news_path = Path(args.news_file)
    if not news_path.is_file():
        print(f"error: news file not found: {news_path}", file=sys.stderr)
        return 2

    news = load_news_from_file(news_path)
    run_id = (args.run_id or "").strip() or default_run_id(news.title)
    out_path = resolve_out_path(run_id, args.out)

    outputs, errors, retrieve_result = await run_eval_pipeline(
        news,
        provider=args.provider,
    )
    markdown = render_eval_markdown(run_id, news, outputs, errors, retrieve_result)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(markdown, encoding="utf-8")
    print(f"Wrote {out_path.resolve()}", file=sys.stderr)

    successes = sum(1 for o in outputs if o.text.strip() and not o.error)
    if outputs and successes == 0:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run eval pipeline: news → agents → retrieve → Eval Markdown.",
    )
    parser.add_argument(
        "--news-file",
        required=True,
        help="Path to news JSON (title and description required).",
    )
    parser.add_argument(
        "--run-id",
        help="Eval run slug (default: slugified title or UTC timestamp).",
    )
    parser.add_argument(
        "--out",
        help="Output Markdown path (default: output/Eval/{run_id}.md).",
    )
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider override (default: DEFAULT_LLM_PROVIDER from .env).",
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
