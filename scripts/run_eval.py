"""run_eval.py · 评测管线：新闻 → deconstruct → agents → retrieve → Eval 目录产物.

每条新闻写入 output/Eval/{run_id}/：reality / facts、各 Agent 文档、聚合候选（填分）、candidates.json。
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

from scripts.agents import (
    RUN_ORDER,
    agent_to_dict,
    annotate_fragment_ids,
    load_deconstruction_from_file,
    load_news_from_file,
    news_to_dict,
    run_all,
)
from scripts.extract import render_deconstruction_md, run_deconstruct
from scripts.eval_editor_fields import append_resonance_editor_lines
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


def resolve_run_dir(run_id: str, out: str | None) -> Path:
    if out:
        path = Path(out)
        if not path.is_absolute():
            path = _REPO_ROOT / path
        return path
    return _REPO_ROOT / "output" / "Eval" / run_id


def _eval_date(pub_time: str) -> str:
    if pub_time and pub_time.strip():
        return pub_time.strip()[:10] if len(pub_time.strip()) >= 10 else pub_time.strip()
    return datetime.now(UTC).strftime("%Y-%m-%d")


def _agent_outputs_by_id(outputs: list) -> dict[str, Any]:
    return {o.agent_id.upper(): o for o in outputs}


def _format_reality_body(run_id: str, news) -> str:
    source = news.source_name or "—"
    pub_time = news.pub_time or "—"
    lines = [
        f"# 现实波澜 · {run_id}",
        "",
        "## 元信息",
        f"- date: {_eval_date(news.pub_time)}",
        f"- news_url: {news.url or '—'}",
        f"- run_id: {run_id}",
        "",
        "## 现实波澜",
        f"- **title**: {news.title}",
        f"- **source** / **pub_time**: {source} / {pub_time}",
        f"- **summary**: {news.description}",
        "",
    ]
    return "\n".join(lines)


def _format_errors(errors: list[dict]) -> str:
    lines = ["# errors", ""]
    if not errors:
        lines.append("（无）")
        return "\n".join(lines) + "\n"
    for entry in errors:
        agent_id = entry.get("agent_id", "?")
        message = entry.get("message") or entry.get("error") or str(entry)
        lines.append(f"- **{agent_id}**: {message}")
    lines.append("")
    return "\n".join(lines)


def _hit_heading(hit: dict[str, Any]) -> str:
    title = hit.get("title") or "Untitled"
    return f"### {title}"


def _format_hit_lines(hit: dict[str, Any]) -> list[str]:
    sim = hit.get("similarity")
    sim_text = f"{sim:.4f}" if isinstance(sim, (int, float)) else str(sim)
    return [
        f"- **tmdb_id**: {hit.get('tmdb_id', '')}",
        f"- **相似度**: {sim_text}",
        f"- **跳转**: {hit.get('movie_url', '')}",
    ]


def _agents_from_hit_sources(cand: dict[str, Any]) -> list[str]:
    """All distinct agent_ids that hit this candidate (A1 included, display order)."""
    seen: set[str] = set()
    ordered: list[str] = []
    for src in cand.get("hit_sources") or []:
        agent_id = str(src.get("agent_id", "")).upper()
        if agent_id and agent_id not in seen:
            seen.add(agent_id)
            ordered.append(agent_id)
    order = {aid: idx for idx, aid in enumerate(_PSEUDO_ORDER)}
    return sorted(ordered, key=lambda aid: order.get(aid, 99))


def _pseudo_hit_total(cand: dict[str, Any]) -> int:
    """Secondary sort key: sum of fragment ids across hit_sources (ADR-0003 D1)."""
    total = 0
    for src in cand.get("hit_sources") or []:
        total += len(src.get("fragments") or [])
    return total


def _sort_candidates_for_display(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Display by pseudo hit total, then similarity; annotations do not rank."""
    return sorted(
        candidates,
        key=lambda c: (
            -_pseudo_hit_total(c),
            -(c.get("similarity") or 0.0),
            c.get("tmdb_id") or 0,
        ),
    )


def _candidate_heading(cand: dict[str, Any]) -> str:
    title = cand.get("title") or "Untitled"
    year = cand.get("release_year")
    year_part = f" ({year})" if year is not None else ""

    agents = _agents_from_hit_sources(cand)
    suffix_parts: list[str] = []
    if agents:
        suffix_parts.append(f"[{', '.join(agents)}]")
    if cand.get("quality_candidate"):
        suffix_parts.append("[汇聚标注]")

    suffix = f" {' '.join(suffix_parts)}" if suffix_parts else ""
    return f"### {title}{year_part}{suffix}"


def _candidate_auto_score_lines(cand: dict[str, Any]) -> list[str]:
    hit_sources = cand.get("hit_sources") or []
    counts = {"surface": 0, "event": 0, "persona": 0}
    kinds: set[str] = set()
    center_dimensions: set[str] = set()
    for src in hit_sources:
        kind = str(src.get("search_unit_kind") or "").strip()
        if kind:
            kinds.add(kind)
        if kind.startswith("surface"):
            counts["surface"] += 1
        elif kind.startswith("event"):
            counts["event"] += 1
        elif kind.startswith("persona"):
            counts["persona"] += 1
        center = str(src.get("center_element") or "").strip()
        if "-" in center:
            center_dimensions.add(center.split("-", 1)[0])

    match = cand.get("match_diagnostics") or {}
    surface_match = bool(match.get("surface_match", counts["surface"] > 0))
    event_match = bool(match.get("event_match", counts["event"] > 0))
    persona_match = bool(match.get("persona_semantic_match", counts["persona"] > 0))
    objective_match = surface_match or event_match
    search_unit_kinds = list(match.get("search_unit_kinds") or sorted(kinds))
    center_dims = list(match.get("center_dimensions") or sorted(center_dimensions))
    persona_count = cand.get("convergence_persona_count", cand.get("persona_count"))
    score = cand.get("convergent_score")
    score_text = f"{score:.4f}" if isinstance(score, (int, float)) else "—"

    lines = [
        "- **自动打分**:",
        f"  - **quality_candidate**: {str(bool(cand.get('quality_candidate'))).lower()}",
        f"  - **objective_match**: {str(objective_match).lower()} (surface={str(surface_match).lower()}, event={str(event_match).lower()})",
        f"  - **persona_semantic_match**: {str(persona_match).lower()}",
        f"  - **convergent_score**: {score_text}",
        f"  - **persona_agent_count**: {persona_count if persona_count is not None else 0}",
        f"  - **source_hits**: surface={counts['surface']} / event={counts['event']} / persona={counts['persona']}",
    ]
    if search_unit_kinds:
        lines.append(f"  - **search_unit_kinds**: {', '.join(search_unit_kinds)}")
    if center_dims:
        lines.append(f"  - **center_dimensions**: {', '.join(center_dims)}")
    lines.append(f"  - **baseline_overlap**: {str(bool(cand.get('also_baseline'))).lower()}")
    reason = str(cand.get("quality_reason") or "").strip()
    if reason:
        lines.append(f"  - **quality_reason**: {reason}")
    return lines


def _format_candidate_block(cand: dict[str, Any], *, include_score: bool) -> list[str]:
    lines = [_candidate_heading(cand)]
    lines.append(f"- **tmdb_id**: {cand.get('tmdb_id', '')}")
    lines.extend(_candidate_auto_score_lines(cand))
    sim = cand.get("similarity")
    sim_text = f"{sim:.4f}" if isinstance(sim, (int, float)) else str(sim)
    lines.append(f"- **相似度**: {sim_text}")
    lines.append(
        f"- **genres** / **language**: {cand.get('genres', '')} / {cand.get('language', '')}"
    )
    overview = (cand.get("overview") or "").replace("\n", " ").strip()
    lines.append(f"- **overview**: {overview or '—'}")
    lines.append(f"- **跳转**: {cand.get('movie_url', '')}")
    hit_sources = cand.get("hit_sources") or []
    if hit_sources:
        lines.append("- **命中视角/碎片**:")
        for src in hit_sources:
            frags = src.get("fragments") or []
            frag_note = ", ".join(frags) if frags else "—"
            sim = src.get("similarity")
            sim_note = f"{sim:.4f}" if isinstance(sim, (int, float)) else "—"
            lines.append(
                f"  - {src.get('agent_id', '?')}/{src.get('pseudo_id', '?')}: "
                f"fragments=[{frag_note}] · sim={sim_note}"
            )
    if include_score:
        append_resonance_editor_lines(lines)
    return lines


def _format_agent_markdown(
    run_id: str,
    agent_id: str,
    output,
    per_agent_entry: dict[str, Any] | None,
) -> str:
    persona = output.persona_name
    baseline_note = " `[baseline]`" if output.role == "baseline" else ""
    lines = [
        f"# {agent_id} · {persona} · {run_id}{baseline_note}",
        "",
        "## 伪剧情（英文 · 1–3 pseudos）",
    ]
    if output.error:
        lines.append(f"*(error: {output.error})*")
    elif not output.pseudos:
        lines.append("—")
    else:
        for pseudo in output.pseudos:
            frags = pseudo.source.get("fragments") or []
            frag_note = ", ".join(frags) if frags else "—"
            lines.extend(
                [
                    "",
                    f"### {pseudo.id}",
                    f"- **fragments**: {frag_note}",
                    "",
                    pseudo.text.strip() or "—",
                ]
            )
    lines.extend(["", "## 本视角召回（Top-K · 按 pseudo）"])

    pseudo_rows = (per_agent_entry or {}).get("pseudos") or []
    legacy_hits = (per_agent_entry or {}).get("hits") or []
    if pseudo_rows:
        for row in pseudo_rows:
            pseudo_id = row.get("pseudo_id") or "?"
            frags = (row.get("source") or {}).get("fragments") or []
            frag_note = ", ".join(frags) if frags else "—"
            lines.extend(
                [
                    "",
                    f"#### {pseudo_id}",
                    f"- **fragments**: {frag_note}",
                ]
            )
            hits = row.get("hits") or []
            if not hits:
                lines.append("- （本段无召回）")
            else:
                for hit in hits:
                    lines.append("")
                    lines.extend([_hit_heading(hit), *_format_hit_lines(hit)])
    elif legacy_hits:
        for hit in legacy_hits:
            lines.append("")
            lines.extend([_hit_heading(hit), *_format_hit_lines(hit)])
    else:
        lines.append("（无 — pseudo 为空或 retrieve 跳过）")

    lines.append("")
    return "\n".join(lines)


def _format_candidates_markdown(run_id: str, candidates: list[dict[str, Any]]) -> str:
    lines = [
        f"# 候选星轨 · {run_id}",
        "",
        "## 元信息",
        f"- run_id: {run_id}",
        "",
        f"## 候选星轨（共 {len(candidates)} 部）",
    ]
    if not candidates:
        lines.append("（无候选 — agents 可能全部失败或 pseudo 为空）")
    else:
        for cand in _sort_candidates_for_display(candidates):
            lines.append("")
            lines.extend(_format_candidate_block(cand, include_score=True))
    lines.append("")
    return "\n".join(lines)


def _format_run_index(run_id: str, errors: list[dict]) -> str:
    error_note = "（无）" if not errors else f"{len(errors)} 条 — 见 [[errors]]"
    lines = [
        f"# 评测 · {run_id}",
        "",
        "| 文档 | 说明 |",
        "|------|------|",
        "| [[reality]] | 现实波澜（人类可读） |",
        "| `reality.json` | 新闻快照（JSON） |",
        "| [[facts]] | 现实解构（人类可读） |",
        "| `facts.json` | 解构契约 JSON |",
        "| [[candidates]] | **总编填共振分** |",
        "| `candidates.json` | 完整 retrieve 输出 |",
        "| [[errors]] | Agent 失败记录 |",
        "| [[agents/A2]] | 社会学家 |",
        "| [[agents/A4]] | 神话学者 |",
        "| [[agents/A7]] | 混沌理论家 |",
        "| [[agents/A1]] | 现实记录员（基线） |",
        "",
        f"- **errors**: {error_note}",
        "",
    ]
    return "\n".join(lines)


def _resolve_deconstruction(
    news,
    run_dir: Path,
    *,
    provider: str | None,
    deconstruction_file: Path | None,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Load or run A0; return (deconstruction object, full A0 payload for disk)."""
    if deconstruction_file is not None and deconstruction_file.is_file():
        dec = load_deconstruction_from_file(deconstruction_file)
        payload = {
            "agent": "A0",
            "news": news_to_dict(news),
            "deconstruction": annotate_fragment_ids(dec),
            "errors": [],
        }
        return dec, payload

    cached = run_dir / "facts.json"
    if cached.is_file():
        dec = load_deconstruction_from_file(cached)
        return dec, json.loads(cached.read_text(encoding="utf-8"))

    payload = run_deconstruct(news, provider=provider)
    dec = payload.get("deconstruction")
    if not isinstance(dec, dict) or not dec:
        raise ValueError("deconstruction failed — no valid deconstruction object")
    return dec, payload


def write_eval_bundle(
    run_dir: Path,
    run_id: str,
    news,
    outputs: list,
    errors: list[dict],
    retrieve_result: dict[str, Any],
    *,
    deconstruction_payload: dict[str, Any] | None = None,
) -> None:
    """Write all Eval artifacts under run_dir."""
    run_dir.mkdir(parents=True, exist_ok=True)
    agents_dir = run_dir / "agents"
    agents_dir.mkdir(exist_ok=True)

    (run_dir / "reality.json").write_text(
        json.dumps(news_to_dict(news), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_dir / "reality.md").write_text(_format_reality_body(run_id, news), encoding="utf-8")

    if deconstruction_payload is not None:
        (run_dir / "facts.json").write_text(
            json.dumps(deconstruction_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (run_dir / "facts.md").write_text(
            render_deconstruction_md(deconstruction_payload, run_id=run_id),
            encoding="utf-8",
        )
    (run_dir / "errors.md").write_text(_format_errors(errors), encoding="utf-8")
    (run_dir / "candidates.json").write_text(
        json.dumps(retrieve_result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_dir / "candidates.md").write_text(
        _format_candidates_markdown(run_id, retrieve_result.get("candidates", [])),
        encoding="utf-8",
    )
    (run_dir / "run.md").write_text(_format_run_index(run_id, errors), encoding="utf-8")

    per_agent_by_id = {
        str(entry["agent_id"]).upper(): entry
        for entry in retrieve_result.get("per_agent", [])
    }
    by_output = _agent_outputs_by_id(outputs)
    for agent_id in _PSEUDO_ORDER:
        output = by_output.get(agent_id)
        if output is None:
            continue
        agent_path = agents_dir / f"{agent_id}.md"
        agent_path.write_text(
            _format_agent_markdown(run_id, agent_id, output, per_agent_by_id.get(agent_id)),
            encoding="utf-8",
        )


async def run_eval_pipeline(
    news,
    *,
    provider: str | None = None,
    deconstruction: dict[str, Any],
) -> tuple[list, list[dict], dict[str, Any]]:
    """Run agents then retrieve; return outputs, errors, retrieve payload."""
    outputs, errors = await run_all(
        news,
        provider=provider,
        deconstruction=deconstruction,
    )
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
    run_dir = resolve_run_dir(run_id, args.out)

    decon_path = Path(args.deconstruction_file) if args.deconstruction_file else None
    if decon_path and not decon_path.is_absolute():
        decon_path = _REPO_ROOT / decon_path

    deconstruction, decon_payload = _resolve_deconstruction(
        news,
        run_dir,
        provider=args.provider,
        deconstruction_file=decon_path,
    )

    outputs, errors, retrieve_result = await run_eval_pipeline(
        news,
        provider=args.provider,
        deconstruction=deconstruction,
    )
    write_eval_bundle(
        run_dir,
        run_id,
        news,
        outputs,
        errors,
        retrieve_result,
        deconstruction_payload=decon_payload,
    )
    print(f"Wrote {run_dir.resolve()}/", file=sys.stderr)

    successes = sum(1 for o in outputs if o.pseudos and not o.error)
    if outputs and successes == 0:
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run eval pipeline: news → agents → retrieve → output/Eval/{run_id}/.",
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
        help="Run output directory (default: output/Eval/{run_id}).",
    )
    parser.add_argument(
        "--provider",
        choices=["mimo", "deepseek"],
        help="LLM provider override (default: DEFAULT_LLM_PROVIDER from .env).",
    )
    parser.add_argument(
        "--deconstruction-file",
        help="Pre-built facts.json (skip A0 if set or if cached in run dir).",
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
