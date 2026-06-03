"""score_eval_candidates.py · Pseudo hit scores from retrieve.json → candidates.md + high-hit review.

pseudo命中分 is a **secondary review/sort key** (ADR-0003 D1): it helps editors triage
candidates but does **not** gate quality_candidate or eval summarize gates. 共振分 remains
the primary human score for publish gates.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
_EVAL_ROOT = _REPO_ROOT / "output" / "Eval"
_HIGH_HIT_REVIEW = _EVAL_ROOT / "high-hit-score-review.md"
_MIN_TOTAL_SCORE = 5

_HIT_LINE = re.compile(
    r"^(\s+-\s+)([A-Z0-9]+)/(p\d+):\s+fragments=\[(.*?)\]\s*·\s*sim=([\d.]+)"
    r"(?:\s*·\s*\*\*命中分=\d+\*\*)?$"
)
_SCORE_SUFFIX = re.compile(r"\s*·\s*\*\*命中分=\d+\*\*$")
_PSEUDO_TOTAL_LINE = re.compile(r"^-\s*\*\*pseudo命中分合计\*\*:\s*\d+\s*$", re.MULTILINE)
_HEADING = re.compile(r"^###\s+(.+)$", re.MULTILINE)
_TMDB_LINE = re.compile(r"^-\s*\*\*tmdb_id\*\*:\s*(\d+)\s*$", re.MULTILINE)
_RUN_ID_META = re.compile(r"^-\s*run_id:\s*(\S+)\s*$", re.MULTILINE)
_AGENTS_TAG = re.compile(r"\[([^\]]+)\]")


@dataclass
class HitScore:
    agent_id: str
    pseudo_id: str
    fragments: list[str]
    similarity: float | None
    score: int


@dataclass
class ScoredCandidate:
    run_id: str
    tmdb_id: int
    title: str
    agents: list[str]
    total_score: int
    block_text: str
    per_agent: dict[str, int] = field(default_factory=dict)


def _load_hit_scores(retrieve_path: Path) -> dict[int, list[HitScore]]:
    data = json.loads(retrieve_path.read_text(encoding="utf-8"))
    by_tmdb: dict[int, list[HitScore]] = {}
    for cand in data.get("candidates") or []:
        tmdb_id = int(cand["tmdb_id"])
        hits: list[HitScore] = []
        for src in cand.get("hit_sources") or []:
            frags = list(src.get("fragments") or [])
            sim = src.get("similarity")
            hits.append(
                HitScore(
                    agent_id=str(src.get("agent_id", "?")),
                    pseudo_id=str(src.get("pseudo_id", "?")),
                    fragments=frags,
                    similarity=float(sim) if isinstance(sim, (int, float)) else None,
                    score=len(frags),
                )
            )
        by_tmdb[tmdb_id] = hits
    return by_tmdb


def _hit_key(agent_id: str, pseudo_id: str) -> tuple[str, str]:
    return agent_id, pseudo_id


def _score_lookup(hits: list[HitScore]) -> dict[tuple[str, str], int]:
    return {_hit_key(h.agent_id, h.pseudo_id): h.score for h in hits}


def _per_agent_totals(hits: list[HitScore]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for h in hits:
        totals[h.agent_id] = totals.get(h.agent_id, 0) + h.score
    return totals


def _infer_run_id(candidates_path: Path, text: str) -> str:
    match = _RUN_ID_META.search(text)
    if match:
        return match.group(1)
    return candidates_path.parent.name


def _agents_from_heading(heading: str) -> list[str]:
    for match in _AGENTS_TAG.finditer(heading):
        tag = match.group(1).strip()
        if re.search(r"baseline\s+only", tag, re.IGNORECASE):
            continue
        if "优质" in tag or "多agent" in tag:
            continue
        return [p.strip() for p in tag.split(",") if p.strip()]
    return []


def _title_from_heading(heading: str) -> str:
    raw = heading.strip()
    while True:
        stripped = re.sub(r"\s*\[[^\]]*\]\s*$", "", raw)
        if stripped == raw:
            break
        raw = stripped
    return re.sub(r"\s*\(\d{4}\)\s*$", "", raw).strip()


def _patch_hit_line(line: str, lookup: dict[tuple[str, str], int]) -> tuple[str, int]:
    base = _SCORE_SUFFIX.sub("", line.rstrip())
    m = _HIT_LINE.match(base)
    if not m:
        return line, 0
    prefix, agent_id, pseudo_id, frag_text, _sim = m.groups()
    frags = [f.strip() for f in frag_text.split(",") if f.strip()]
    score = lookup.get(_hit_key(agent_id, pseudo_id), len(frags))
    return f"{base} · **命中分={score}**", score


def _patch_candidate_block(
    block: str,
    lookup: dict[tuple[str, str], int],
    total_from_retrieve: int,
) -> str:
    # splitlines() drops a trailing blank line between candidates; keep it.
    lines = block.split("\n")
    if lines and lines[-1] == "":
        lines.pop()
    out: list[str] = []
    in_hits = False
    hit_scores: list[int] = []
    total_inserted = False
    i = 0
    while i < len(lines):
        line = lines[i]
        if line.strip() == "- **命中视角/碎片**:":
            in_hits = True
            out.append(line)
            i += 1
            continue
        if in_hits and line.startswith("  - "):
            patched, sc = _patch_hit_line(line, lookup)
            out.append(patched)
            hit_scores.append(sc)
            i += 1
            continue
        if in_hits and not line.startswith("  - "):
            in_hits = False
            total = total_from_retrieve if total_from_retrieve else sum(hit_scores)
            if not total_inserted and hit_scores:
                out.append(f"- **pseudo命中分合计**: {total}")
                total_inserted = True
        if _PSEUDO_TOTAL_LINE.match(line):
            i += 1
            continue
        if line.startswith("- **共振分**") and not total_inserted and hit_scores:
            total = total_from_retrieve if total_from_retrieve else sum(hit_scores)
            out.append(f"- **pseudo命中分合计**: {total}")
            total_inserted = True
        out.append(line)
        i += 1
    if in_hits and hit_scores and not total_inserted:
        total = total_from_retrieve if total_from_retrieve else sum(hit_scores)
        out.append(f"- **pseudo命中分合计**: {total}")
    text = "\n".join(out)
    if text and not text.endswith("\n"):
        text += "\n"
    return text


def score_candidates_md(
    candidates_path: Path,
    hits_by_tmdb: dict[int, list[HitScore]],
    *,
    min_total_score: int = _MIN_TOTAL_SCORE,
) -> tuple[str, list[ScoredCandidate]]:
    text = candidates_path.read_text(encoding="utf-8")
    run_id = _infer_run_id(candidates_path, text)

    # Strip document header (before first ### candidate)
    first_heading = text.find("### ")
    if first_heading < 0:
        return text, []
    header = text[:first_heading]
    body = text[first_heading:]

    parts = re.split(r"(?=^### )", body, flags=re.MULTILINE)
    scored: list[ScoredCandidate] = []
    patched_blocks: list[str] = []

    for part in parts:
        if not part.strip():
            continue
        heading_m = _HEADING.match(part)
        if not heading_m:
            patched_blocks.append(part)
            continue
        heading = heading_m.group(1)
        tmdb_m = _TMDB_LINE.search(part)
        if not tmdb_m:
            patched_blocks.append(part)
            continue
        tmdb_id = int(tmdb_m.group(1))
        hits = hits_by_tmdb.get(tmdb_id, [])
        lookup = _score_lookup(hits)
        total = sum(h.score for h in hits)
        patched = _patch_candidate_block(part, lookup, total)
        # Preserve run_eval blank line between candidates (### … ###).
        patched = patched.rstrip("\n") + "\n\n"
        patched_blocks.append(patched)

        agents = _agents_from_heading(heading)
        if not agents and hits:
            agents = sorted({h.agent_id for h in hits})
        if total >= min_total_score:
            scored.append(
                ScoredCandidate(
                    run_id=run_id,
                    tmdb_id=tmdb_id,
                    title=_title_from_heading(heading),
                    agents=agents,
                    total_score=total,
                    block_text=patched.rstrip(),
                    per_agent=_per_agent_totals(hits),
                )
            )

    body_joined = "".join(patched_blocks)
    if body_joined and not body_joined.startswith("\n") and header and not header.endswith("\n"):
        body_joined = "\n" + body_joined
    new_text = header + body_joined
    if not new_text.endswith("\n"):
        new_text += "\n"
    return new_text, scored


def _format_high_hit_review(
    all_scored: list[ScoredCandidate],
    *,
    runs_scanned: int,
    min_score: int = _MIN_TOTAL_SCORE,
) -> str:
    all_scored.sort(key=lambda c: (-c.total_score, c.run_id, c.tmdb_id))
    today = date.today().isoformat()
    lines = [
        "# High Pseudo Hit Score — Unified Review",
        "",
        "## Criteria",
        "",
        "### Pseudo 命中分（二级审阅键 · 非质量闸）",
        "",
        f"**High-hit review** lists candidates with **pseudo命中分合计 ≥ {min_score}**",
        "as an editor triage aid. Inclusion here is **not** a quality gate; D1",
        "`quality_candidate` (≥2 agents above floor) is computed in retrieve/run_eval.",
        "",
        "For each hit line under **命中视角/碎片**, count entries in `fragments=[...]`",
        "— **each fragment id = 1 point** for that pseudo.",
        "",
        "- **Candidate 总分** (`pseudo命中分合计`) = sum of pseudo 命中分 across all hit lines.",
        "- Shown inline per line, e.g. `A2/p1: fragments=[...] · sim=... · **命中分=3**`.",
        "",
        "### Sources",
        "",
        "- **Primary:** `hit_sources` in each run's `retrieve.json` (fragment arrays).",
        "- **Editor fields:** 共振分 / 共振类型 are placeholders only (not filled by this script).",
        "",
        f"- **Generation date:** {today}",
        f"- **Total candidates (≥{min_score}):** {len(all_scored)}",
        f"- **Runs scanned:** {runs_scanned}",
        "",
        "## Summary table (sorted by pseudo命中分合计 ↓)",
        "",
        "| rank | run_id | tmdb_id | title | 总分 | agents |",
        "| ---: | --- | ---: | --- | ---: | --- |",
    ]
    for rank, c in enumerate(all_scored, start=1):
        agents = ", ".join(c.agents) if c.agents else "—"
        title = c.title.replace("|", "\\|")
        lines.append(
            f"| {rank} | {c.run_id} | {c.tmdb_id} | {title} | {c.total_score} | {agents} |"
        )
    lines.extend(
        [
            "",
            "## Candidates (global sort by pseudo命中分合计 ↓)",
            "",
            f"**Count:** {len(all_scored)} candidate(s)",
            "",
        ]
    )
    for c in all_scored:
        lines.extend(
            [
                f"<!-- run_id: {c.run_id} -->",
                f"<!-- pseudo命中分合计: {c.total_score} -->",
                c.block_text,
                "",
            ]
        )
    return "\n".join(lines) + "\n"


def process_eval_dir(
    eval_dir: Path,
    *,
    write_candidates: bool = True,
    min_total_score: int = _MIN_TOTAL_SCORE,
) -> tuple[list[ScoredCandidate], list[str], int]:
    """Score all runs; return high-score candidates and run_ids missing retrieve.json."""
    missing_retrieve: list[str] = []
    all_high: list[ScoredCandidate] = []
    runs_scanned = 0

    run_dirs = sorted(
        p for p in eval_dir.iterdir() if p.is_dir() and (p / "candidates.md").is_file()
    )
    for run_dir in run_dirs:
        retrieve_path = run_dir / "retrieve.json"
        candidates_path = run_dir / "candidates.md"
        if not retrieve_path.is_file():
            missing_retrieve.append(run_dir.name)
            continue
        runs_scanned += 1
        hits_by_tmdb = _load_hit_scores(retrieve_path)
        new_text, high = score_candidates_md(
            candidates_path, hits_by_tmdb, min_total_score=min_total_score
        )
        if write_candidates:
            candidates_path.write_text(new_text, encoding="utf-8")
        all_high.extend(high)

    return all_high, missing_retrieve, runs_scanned


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Score eval candidates from retrieve.json hit_sources; write high-hit review.",
    )
    parser.add_argument(
        "--dir",
        type=Path,
        default=_EVAL_ROOT,
        help="Eval root (default: output/Eval)",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=_MIN_TOTAL_SCORE,
        help="Minimum pseudo命中分合计 for high-hit review (default: 5)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write candidates.md or review file",
    )
    args = parser.parse_args(argv)

    eval_dir = args.dir if args.dir.is_absolute() else _REPO_ROOT / args.dir
    all_high, missing, runs_scanned = process_eval_dir(
        eval_dir,
        write_candidates=not args.dry_run,
        min_total_score=args.min_score,
    )
    review_text = _format_high_hit_review(
        all_high, runs_scanned=runs_scanned, min_score=args.min_score
    )
    if not args.dry_run:
        _HIGH_HIT_REVIEW.write_text(review_text, encoding="utf-8")

    all_high.sort(key=lambda c: (-c.total_score, c.run_id, c.tmdb_id))
    print(f"Runs scanned: {runs_scanned}")
    print(f"Candidates with pseudo命中分合计 >= {args.min_score}: {len(all_high)}")
    if missing:
        print(f"Missing retrieve.json: {', '.join(missing)}")
    print("Top 5 by score:")
    for c in all_high[:5]:
        print(f"  {c.total_score:3d}  {c.run_id}  {c.tmdb_id}  {c.title}")
    if not args.dry_run:
        print(f"Wrote {_HIGH_HIT_REVIEW.relative_to(_REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
