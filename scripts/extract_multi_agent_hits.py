"""extract_multi_agent_hits.py · 从 Eval candidates.json 提取多 agent 命中并生成统一审阅 Markdown."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.eval_editor_fields import append_resonance_editor_lines

SCREENPLAY_AGENTS = frozenset({"A1", "A2", "A4", "A7"})
DEFAULT_EVAL_ROOT = _REPO_ROOT / "output" / "Eval"
DEFAULT_OUT = DEFAULT_EVAL_ROOT / "multi-agent-hits-review.md"


def _overlap_note(agents: set[str]) -> str:
    if "A2" in agents:
        return "includes A2"
    if "A1" in agents and agents & {"A4", "A7"}:
        return "A1 + creative (A4/A7)"
    if agents <= {"A4", "A7"} and len(agents) >= 2:
        return "creative-only (A4+A7)"
    return ", ".join(sorted(agents))


def _pseudo_score(src: dict[str, Any]) -> int:
    frags = src.get("fragments") or []
    return len(frags)


def _screenplay_agents_from_hit_sources(hit_sources: list[dict[str, Any]]) -> set[str]:
    return {
        str(s.get("agent_id", "")).upper()
        for s in hit_sources
        if str(s.get("agent_id", "")).upper() in SCREENPLAY_AGENTS
    }


def _agent_breakdown(hit_sources: list[dict[str, Any]]) -> dict[str, int]:
    totals: dict[str, int] = defaultdict(int)
    for src in hit_sources:
        aid = str(src.get("agent_id", "")).upper()
        if aid not in SCREENPLAY_AGENTS:
            continue
        totals[aid] += _pseudo_score(src)
    return dict(sorted(totals.items()))


def _candidate_heading(cand: dict[str, Any]) -> str:
    title = cand.get("title") or "Untitled"
    year = cand.get("release_year")
    year_part = f" ({year})" if year is not None else ""
    triggered = cand.get("triggered_by") or []
    if triggered:
        bracket = f"[{', '.join(triggered)}]"
    elif cand.get("also_baseline"):
        bracket = "[baseline only]"
    else:
        bracket = ""
    suffix = f" {bracket}" if bracket else ""
    return f"### {title}{year_part}{suffix}"


def _format_hit_line(src: dict[str, Any]) -> str:
    frags = src.get("fragments") or []
    frag_note = ", ".join(frags) if frags else "—"
    sim = src.get("similarity")
    sim_note = f"{sim:.4f}" if isinstance(sim, (int, float)) else "—"
    score = _pseudo_score(src)
    return (
        f"  - {src.get('agent_id', '?')}/{src.get('pseudo_id', '?')}: "
        f"fragments=[{frag_note}] · sim={sim_note} · **命中分={score}**"
    )


def _format_candidate_block(
    cand: dict[str, Any],
    *,
    run_id: str,
    agents: set[str],
    total_score: int,
) -> list[str]:
    lines = [
        f"<!-- run_id: {run_id} -->",
        f"<!-- retrieve: {', '.join(sorted(agents))} -->",
        f"<!-- overlap: {_overlap_note(agents)} -->",
        f"<!-- pseudo命中分合计: {total_score} -->",
        _candidate_heading(cand),
        f"- **tmdb_id**: {cand.get('tmdb_id', '')}",
        f"- **run_id**: {run_id}",
        f"- **pseudo命中分合计**: {total_score}",
    ]
    breakdown = _agent_breakdown(cand.get("hit_sources") or [])
    if breakdown:
        parts = [f"{aid}:{pts}" for aid, pts in breakdown.items()]
        lines.append(f"- **per-agent 命中分**: {', '.join(parts)}")
    sim = cand.get("similarity")
    sim_text = f"{sim:.4f}" if isinstance(sim, (int, float)) else str(sim)
    lines.append(f"- **相似度**: {sim_text}")
    lines.append(
        f"- **genres** / **language**: {cand.get('genres', '')} / {cand.get('language', '')}"
    )
    overview = (cand.get("overview") or "").replace("\n", " ").strip()
    lines.append(f"- **overview**: {overview or '—'}")
    lines.append(f"- **跳转**: {cand.get('movie_url', '')}")
    lines.append(f"- **also_baseline**: {str(bool(cand.get('also_baseline'))).lower()}")
    hit_sources = cand.get("hit_sources") or []
    screenplay_sources = [
        s
        for s in hit_sources
        if str(s.get("agent_id", "")).upper() in SCREENPLAY_AGENTS
    ]
    if screenplay_sources:
        lines.append("- **命中视角/碎片**:")
        for src in screenplay_sources:
            lines.append(_format_hit_line(src))
    append_resonance_editor_lines(lines)
    lines.append("")
    return lines


def _eval_run_ids(eval_root: Path) -> list[str]:
    return sorted(
        p.name
        for p in eval_root.iterdir()
        if p.is_dir() and (p / "candidates.json").is_file()
    )


def _runs_scanned_label(eval_root: Path) -> str:
    ids = _eval_run_ids(eval_root)
    if not ids:
        return "—"
    if len(ids) <= 2:
        return " … ".join(ids)
    return f"{ids[0]} … {ids[-1]}"


def _load_multi_agent_candidates(eval_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    run_dirs = sorted(p for p in eval_root.iterdir() if p.is_dir())
    for run_dir in run_dirs:
        retrieve_path = run_dir / "candidates.json"
        if not retrieve_path.is_file():
            continue
        run_id = run_dir.name
        data = json.loads(retrieve_path.read_text(encoding="utf-8"))
        for cand in data.get("candidates") or []:
            hit_sources = cand.get("hit_sources") or []
            agents = _screenplay_agents_from_hit_sources(hit_sources)
            if len(agents) < 2:
                continue
            screenplay_sources = [
                s
                for s in hit_sources
                if str(s.get("agent_id", "")).upper() in SCREENPLAY_AGENTS
            ]
            total_score = sum(_pseudo_score(s) for s in screenplay_sources)
            rows.append(
                {
                    "run_id": run_id,
                    "cand": cand,
                    "agents": agents,
                    "overlap": _overlap_note(agents),
                    "total_score": total_score,
                    "breakdown": _agent_breakdown(hit_sources),
                }
            )
    rows.sort(key=lambda r: (-r["total_score"], r["run_id"], r["cand"].get("tmdb_id", 0)))
    return rows


def _format_breakdown_col(breakdown: dict[str, int]) -> str:
    if not breakdown:
        return "—"
    return ", ".join(f"{aid}:{pts}" for aid, pts in breakdown.items())


def render_markdown(rows: list[dict[str, Any]], *, eval_root: Path) -> str:
    scanned = _eval_run_ids(eval_root)
    gen_date = datetime.now(UTC).strftime("%Y-%m-%d")
    lines = [
        "# Multi-Agent Screenplay Hits — Unified Review",
        "",
        "## Criteria",
        "",
        "### 多 agent 同时命中（准入门槛 · 已实现）",
        "",
        "Candidate **enters this review** when **≥2 distinct `agent_id`s** among screenplay agents "
        "`{A1, A2, A4, A7}` contributed `hit_sources` for the same `tmdb_id` "
        "(existing retrieval aggregation rule).",
        "",
        "### Pseudo 命中分",
        "",
        "For each hit line under **命中视角/碎片**, count entries in `fragments=[...]` — "
        "**each fragment id = 1 point** for that pseudo.",
        "",
        "- **Candidate 总分** (`pseudo命中分合计`) = sum of pseudo 命中分 across all qualifying hit lines.",
        "- Shown inline per line, e.g. `A2/p1: fragments=[...] · sim=... · **命中分=3**`.",
        "",
        "### Sources",
        "",
        "- **Primary:** `hit_sources` in each run's `candidates.json` (fragment arrays).",
        "- **Cross-check:** `命中视角/碎片` in `candidates.md` when present.",
        "- **Editor fields:** 共振分 / 共振类型 / 打分备注 are placeholders only (not filled by this extract).",
        "",
        f"- **Generation date:** {gen_date}",
        f"- **Total multi-agent candidates:** {len(rows)}",
        f"- **Runs scanned:** {len(scanned)} ({_runs_scanned_label(eval_root)})",
        "",
        "## Summary table (sorted by pseudo命中分合计 ↓)",
        "",
        "| rank | run_id | tmdb_id | title | agents | pseudo命中分合计 | per-agent | overlap |",
        "| ---: | --- | ---: | --- | --- | ---: | --- | --- |",
    ]
    for rank, row in enumerate(rows, start=1):
        cand = row["cand"]
        agents_str = ", ".join(sorted(row["agents"]))
        lines.append(
            f"| {rank} | {row['run_id']} | {cand.get('tmdb_id', '')} | "
            f"{cand.get('title', '')} | {agents_str} | {row['total_score']} | "
            f"{_format_breakdown_col(row['breakdown'])} | {row['overlap']} |"
        )
    lines.extend(
        [
            "",
            "## Candidates (global sort by pseudo命中分合计 ↓)",
            "",
            f"**Count:** {len(rows)} multi-agent hit(s)",
            "",
        ]
    )
    for row in rows:
        lines.extend(
            _format_candidate_block(
                row["cand"],
                run_id=row["run_id"],
                agents=row["agents"],
                total_score=row["total_score"],
            )
        )
    return "\n".join(lines).rstrip() + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--eval-root",
        type=Path,
        default=DEFAULT_EVAL_ROOT,
        help="Eval output root (default: output/Eval)",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUT,
        help="Output markdown path",
    )
    args = parser.parse_args(argv)
    eval_root = args.eval_root if args.eval_root.is_absolute() else _REPO_ROOT / args.eval_root
    out_path = args.out if args.out.is_absolute() else _REPO_ROOT / args.out

    rows = _load_multi_agent_candidates(eval_root)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render_markdown(rows, eval_root=eval_root), encoding="utf-8")

    print(f"Wrote {len(rows)} candidates → {out_path}")
    for row in rows:
        cand = row["cand"]
        print(
            f"  {row['total_score']:3d}  tmdb={cand.get('tmdb_id')}  "
            f"{row['run_id']}  {cand.get('title', '')[:50]}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
