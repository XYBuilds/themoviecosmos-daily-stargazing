"""render_briefing · 共享 Markdown 渲染函数（eval / prod 单点维护）.

从 ``scripts/run_eval.py`` 抽离的纯格式化函数：reality / candidates / errors /
per-agent markdown / run index。逻辑与迁移前保持一致（bit-for-bit），仅做
位置迁移 + 模块化封装。``run_eval.py`` 改为从本模块 import 这些函数。

candidates 渲染新增可选 ``copies`` 参数槽位，用于 Phase 6.2 main.py 传入
C1（``compose.run_review``）产出的中文文案；``copies`` 为 ``None`` 时保持
原有渲染行为不变（eval 模式调用方式）。
"""

from __future__ import annotations

from typing import Any

from scripts.agents import RUN_ORDER
from scripts.eval_editor_fields import append_resonance_editor_lines

# 历史遗留排序键：源自旧 4-agent 流（A2/A4/A7/A1）。当前生产管线走 12-persona
# pipeline，persona_id（如 The-Hero）不在此元组中，故排序回退到追加顺序
# （见 _agents_from_hit_sources 的 order.get(aid, 99) 兜底）。保留此常量只是为了
# 与迁移前行为完全一致；参见交付报告"技术债"一节。
_PSEUDO_ORDER: tuple[str, ...] = RUN_ORDER


def _eval_date(pub_time: str) -> str:
    if pub_time and pub_time.strip():
        return pub_time.strip()[:10] if len(pub_time.strip()) >= 10 else pub_time.strip()
    from datetime import UTC, datetime

    return datetime.now(UTC).strftime("%Y-%m-%d")


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


def _candidate_copy_text(cand: dict[str, Any], copies: dict[Any, Any] | list[dict] | None) -> str | None:
    """Look up C1 (compose.run_review) 中文文案 for this candidate, if provided.

    ``copies`` may be a mapping keyed by tmdb_id, or a list of dicts each
    carrying a ``tmdb_id`` field alongside the copy text (shape TBD by 6.2 —
    both are supported defensively so the slot does not need to change again
    once 6.2 wires compose.run_review's real output shape).
    """
    if not copies:
        return None
    tmdb_id = cand.get("tmdb_id")
    if isinstance(copies, dict):
        entry = copies.get(tmdb_id)
    else:
        entry = next((c for c in copies if c.get("tmdb_id") == tmdb_id), None)
    if entry is None:
        return None
    if isinstance(entry, str):
        return entry
    if isinstance(entry, dict):
        return entry.get("copy") or entry.get("text") or entry.get("draft")
    return None


def _format_candidate_block(
    cand: dict[str, Any],
    *,
    include_score: bool,
    copies: dict[Any, Any] | list[dict] | None = None,
) -> list[str]:
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
    copy_text = _candidate_copy_text(cand, copies)
    if copy_text:
        lines.append(f"- **中文文案（C1 审核稿）**: {copy_text}")
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


def _format_candidates_markdown(
    run_id: str,
    candidates: list[dict[str, Any]],
    *,
    copies: dict[Any, Any] | list[dict] | None = None,
) -> str:
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
            lines.extend(_format_candidate_block(cand, include_score=True, copies=copies))
    lines.append("")
    return "\n".join(lines)


def _format_run_index(
    run_id: str,
    errors: list[dict],
    *,
    persona_ids: list[str] | None = None,
) -> str:
    """Render run.md index. ``persona_ids`` drives the dynamic persona link rows.

    Historically this hardcoded four dead links (``[[agents/A2]] [[agents/A4]]
    [[agents/A7]] [[agents/A1]]``) pointing at the retired 4-agent flow. When
    ``persona_ids`` is supplied (the real run's persona list, e.g. from
    ``outputs``/``persona_payloads``), rows are generated dynamically instead.
    When omitted, no persona rows are emitted (empty list is the safe default
    rather than resurrecting the dead links).
    """
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
    ]
    for persona_id in persona_ids or []:
        lines.append(f"| [[agents/{persona_id}]] | {persona_id} |")
    lines.extend(
        [
            "",
            f"- **errors**: {error_note}",
            "",
        ]
    )
    return "\n".join(lines)