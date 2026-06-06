"""score_eval_candidates.py · Pseudo hit scores from retrieve.json → high-hit review.

Builds `high-hit-score-review.md` from each run's `retrieve.json` (and patches
per-run `candidates.md` when present, e.g. phase3.5/3.6). Phase 3.7 batch runs
do not write per-run candidates.md; the review file is the editor SSOT.

pseudo命中分 is a **secondary review/sort key** (ADR-0003 D1): it helps editors triage
candidates but does **not** gate quality_candidate or eval summarize gates. 共振分 remains
the primary human score for publish gates.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.eval_batch_manifest import load_manifest
from scripts.eval_editor_fields import ensure_scoring_remark_in_block
from scripts.run_eval import _format_candidates_markdown
_EVAL_ROOT = _REPO_ROOT / "output" / "Eval"
_LEGACY_HIGH_HIT_REVIEW = _EVAL_ROOT / "high-hit-score-review.md"
_MIN_TOTAL_SCORE = 5


def _default_review_path(eval_dir: Path) -> Path:
    """Phase-scoped review file; avoids clobbering output/Eval/high-hit-score-review.md."""
    return eval_dir / "high-hit-score-review.md"

_HIT_LINE = re.compile(
    r"^(\s+-\s+)([A-Z0-9][A-Z0-9-]*)/(p\d+)"
    r"(?:\s*·\s*fit=[\d.]+)?\s*:\s*fragments=\[(.*?)\]\s*·\s*sim=([\d.]+)"
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
class RetrieveDiagnostics:
    """ADR-0005 channel fields from retrieve.json (for summarize_eval diagnostics)."""

    quality_candidate: bool
    neutral_hits: int
    neutral_total: int
    neutral_hit_rate: float
    distinct_agents: int


@dataclass
class ScoredCandidate:
    run_id: str
    tmdb_id: int
    title: str
    agents: list[str]
    total_score: int
    block_text: str
    is_multi_agent: bool = False
    per_agent: dict[str, int] = field(default_factory=dict)


@dataclass
class RunHighHitReview:
    run_id: str
    reality_text: str
    multi_agent: list[ScoredCandidate] = field(default_factory=list)
    single_agent: list[ScoredCandidate] = field(default_factory=list)


def _agents_from_hit_sources(hits: list[HitScore]) -> list[str]:
    seen: set[str] = set()
    ordered: list[str] = []
    for h in hits:
        aid = h.agent_id.upper()
        if aid and aid not in seen:
            seen.add(aid)
            ordered.append(aid)
    return ordered


def _is_multi_agent_hit(*, quality_candidate: bool, agents: list[str]) -> bool:
    """D1 bucketing aligned with run_eval / retrieve quality_candidate."""
    if quality_candidate:
        return True
    return len(agents) >= 2


def _is_pure_neutral_candidate(diag: RetrieveDiagnostics | None) -> bool:
    """ADR-0006 D4: neutral vote without toned convergence (pure-fact bucket)."""
    if diag is None:
        return False
    return diag.neutral_hits >= 1 and diag.distinct_agents == 0


def _eligible_for_scoring_pool(
    total_score: int,
    *,
    min_total_score: int,
    diag: RetrieveDiagnostics | None,
) -> bool:
    """High-hit / scoring pool: pseudo总分 threshold OR pure-neutral (neutral-only)."""
    if total_score >= min_total_score:
        return True
    return _is_pure_neutral_candidate(diag)


def _load_retrieve_meta(
    retrieve_path: Path,
) -> tuple[dict[int, list[HitScore]], dict[int, bool], dict[int, RetrieveDiagnostics]]:
    data = json.loads(retrieve_path.read_text(encoding="utf-8"))
    hits_by_tmdb: dict[int, list[HitScore]] = {}
    quality_by_tmdb: dict[int, bool] = {}
    diagnostics_by_tmdb: dict[int, RetrieveDiagnostics] = {}
    for cand in data.get("candidates") or []:
        tmdb_id = int(cand["tmdb_id"])
        quality = bool(cand.get("quality_candidate"))
        quality_by_tmdb[tmdb_id] = quality
        neutral_hits = int(cand.get("neutral_hits") or 0)
        neutral_total = int(cand.get("neutral_total") or 0)
        raw_rate = cand.get("neutral_hit_rate")
        neutral_hit_rate = (
            float(raw_rate)
            if isinstance(raw_rate, (int, float))
            else (float(neutral_hits) / neutral_total if neutral_total > 0 else 0.0)
        )
        distinct_agents = int(cand.get("distinct_agents") or 0)
        diagnostics_by_tmdb[tmdb_id] = RetrieveDiagnostics(
            quality_candidate=quality,
            neutral_hits=neutral_hits,
            neutral_total=neutral_total,
            neutral_hit_rate=neutral_hit_rate,
            distinct_agents=distinct_agents,
        )
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
        hits_by_tmdb[tmdb_id] = hits
    return hits_by_tmdb, quality_by_tmdb, diagnostics_by_tmdb


def _load_hit_scores(retrieve_path: Path) -> dict[int, list[HitScore]]:
    hits_by_tmdb, _, _ = _load_retrieve_meta(retrieve_path)
    return hits_by_tmdb


def _inject_retrieve_diagnostics(block: str, diag: RetrieveDiagnostics) -> str:
    """Insert ADR-0005 retrieve fields after tmdb_id for summarize_eval parsing."""
    lines = block.split("\n")
    out: list[str] = []
    injected = False
    for line in lines:
        out.append(line)
        if not injected and _TMDB_LINE.match(line):
            out.append(f"- **quality_candidate**: {str(diag.quality_candidate).lower()}")
            out.append(f"- **neutral_hits**: {diag.neutral_hits}")
            out.append(f"- **neutral_total**: {diag.neutral_total}")
            out.append(f"- **neutral_hit_rate**: {diag.neutral_hit_rate:.4f}")
            out.append(f"- **distinct_agents**: {diag.distinct_agents}")
            injected = True
    text = "\n".join(out)
    if text and not text.endswith("\n"):
        text += "\n"
    return text


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
    return ensure_scoring_remark_in_block(text)


def _load_candidates_text(run_dir: Path, retrieve_path: Path) -> tuple[str, str]:
    """Return (markdown body, run_id). Synthesize from retrieve.json if no candidates.md."""
    candidates_path = run_dir / "candidates.md"
    if candidates_path.is_file():
        text = candidates_path.read_text(encoding="utf-8")
        return text, _infer_run_id(candidates_path, text)
    data = json.loads(retrieve_path.read_text(encoding="utf-8"))
    run_id = run_dir.name
    return _format_candidates_markdown(run_id, data.get("candidates") or []), run_id


def score_candidates_md(
    candidates_text: str,
    run_id: str,
    hits_by_tmdb: dict[int, list[HitScore]],
    *,
    quality_by_tmdb: dict[int, bool] | None = None,
    diagnostics_by_tmdb: dict[int, RetrieveDiagnostics] | None = None,
    min_total_score: int = _MIN_TOTAL_SCORE,
) -> tuple[str, list[ScoredCandidate]]:
    text = candidates_text

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
        diag = (diagnostics_by_tmdb or {}).get(tmdb_id)
        if diag is not None:
            patched = _inject_retrieve_diagnostics(patched, diag)
        # Preserve run_eval blank line between candidates (### … ###).
        patched = patched.rstrip("\n") + "\n\n"
        patched_blocks.append(patched)

        agents = _agents_from_heading(heading)
        if not agents and hits:
            agents = _agents_from_hit_sources(hits)
        quality = (quality_by_tmdb or {}).get(tmdb_id, False)
        is_multi = _is_multi_agent_hit(quality_candidate=quality, agents=agents)
        if _eligible_for_scoring_pool(
            total, min_total_score=min_total_score, diag=diag
        ):
            scored.append(
                ScoredCandidate(
                    run_id=run_id,
                    tmdb_id=tmdb_id,
                    title=_title_from_heading(heading),
                    agents=agents,
                    total_score=total,
                    block_text=patched.rstrip(),
                    is_multi_agent=is_multi,
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


def _sort_scored(candidates: list[ScoredCandidate]) -> list[ScoredCandidate]:
    return sorted(candidates, key=lambda c: (-c.total_score, c.tmdb_id))


def _read_reality(run_dir: Path) -> str:
    reality_path = run_dir / "reality.md"
    if reality_path.is_file():
        return reality_path.read_text(encoding="utf-8").strip()
    return "_No `reality.md` for this run._"


def _split_multi_single(high: list[ScoredCandidate]) -> tuple[list[ScoredCandidate], list[ScoredCandidate]]:
    multi = [c for c in high if c.is_multi_agent]
    single = [c for c in high if not c.is_multi_agent]
    return _sort_scored(multi), _sort_scored(single)


def _append_candidate_blocks(lines: list[str], candidates: list[ScoredCandidate]) -> None:
    for c in candidates:
        lines.extend(
            [
                f"<!-- run_id: {c.run_id} -->",
                f"<!-- pseudo命中分合计: {c.total_score} -->",
                c.block_text,
                "",
            ]
        )


def _ordered_run_dirs(eval_dir: Path, manifest_path: Path | None = None) -> list[Path]:
    """Run folders in batch-manifest order, then any extras alphabetically."""
    try:
        manifest_ids = load_manifest(manifest_path)
    except (OSError, json.JSONDecodeError, ValueError):
        manifest_ids = []

    dirs_by_name = {
        p.name: p
        for p in eval_dir.iterdir()
        if p.is_dir() and (p / "retrieve.json").is_file()
    }
    ordered: list[Path] = []
    seen: set[str] = set()
    for run_id in manifest_ids:
        if run_id in dirs_by_name:
            ordered.append(dirs_by_name[run_id])
            seen.add(run_id)
    for name in sorted(dirs_by_name):
        if name not in seen:
            ordered.append(dirs_by_name[name])
    if not ordered:
        return sorted(dirs_by_name.values(), key=lambda p: p.name)
    return ordered


def _format_high_hit_review(
    runs: list[RunHighHitReview],
    *,
    runs_scanned: int,
    min_score: int = _MIN_TOTAL_SCORE,
) -> str:
    total_candidates = sum(len(r.multi_agent) + len(r.single_agent) for r in runs)
    today = date.today().isoformat()
    lines = [
        "# High Pseudo Hit Score — Unified Review",
        "",
        "## Criteria",
        "",
        "### Pseudo 命中分（二级审阅键 · 非质量闸）",
        "",
        f"**High-hit review** lists candidates with **pseudo命中分合计 ≥ {min_score}**",
        "or **pure-neutral** hits (`neutral_hits≥1` and `distinct_agents=0`, ADR-0006 D4).",
        "Inclusion is **not** a quality gate; D1 `quality_candidate` is from retrieve.",
        "",
        "For each hit line under **命中视角/碎片**, count entries in `fragments=[...]`",
        "— **each fragment id = 1 point** for that pseudo.",
        "",
        "- **Candidate 总分** (`pseudo命中分合计`) = sum of pseudo 命中分 across all hit lines.",
        "- Shown inline per line, e.g. `A2/p1: fragments=[...] · sim=... · **命中分=3**`.",
        "",
        "### Per-news layout",
        "",
        "- News sections follow `tests/eval_news/batch-manifest.json` order (01–10).",
        "- Each section opens with that run's `reality.md`.",
        "- **多 agents 命中**: `quality_candidate` or ≥2 agents in heading / hit_sources.",
        "- **单 agent 命中**: all other high-hit candidates.",
        "- Within each subsection, sort by **pseudo命中分合计** descending.",
        "",
        "### Sources",
        "",
        "- **Primary:** `hit_sources` in each run's `retrieve.json` (fragment arrays).",
        "- **Editor fields:** 共振分 / 共振类型 / 打分备注 are placeholders only (not filled by this script).",
        "",
        f"- **Generation date:** {today}",
        f"- **Total candidates (≥{min_score}):** {total_candidates}",
        f"- **Runs scanned:** {runs_scanned}",
        "",
    ]
    for run in runs:
        multi_n = len(run.multi_agent)
        single_n = len(run.single_agent)
        lines.extend(
            [
                f"## {run.run_id}",
                "",
                run.reality_text,
                "",
                "### 多 agents 命中",
                "",
                f"**Count:** {multi_n} candidate(s)",
                "",
            ]
        )
        _append_candidate_blocks(lines, run.multi_agent)
        lines.extend(
            [
                "### 单 agent 命中",
                "",
                f"**Count:** {single_n} candidate(s)",
                "",
            ]
        )
        _append_candidate_blocks(lines, run.single_agent)
    return "\n".join(lines) + "\n"


def process_eval_dir(
    eval_dir: Path,
    *,
    write_candidates: bool = True,
    min_total_score: int = _MIN_TOTAL_SCORE,
    manifest_path: Path | None = None,
) -> tuple[list[RunHighHitReview], list[ScoredCandidate], list[str], int]:
    """Score all runs; return per-run review rows, flat high list, missing retrieve ids."""
    missing_retrieve: list[str] = []
    all_high: list[ScoredCandidate] = []
    run_reviews: list[RunHighHitReview] = []
    runs_scanned = 0

    for run_dir in _ordered_run_dirs(eval_dir, manifest_path):
        retrieve_path = run_dir / "retrieve.json"
        candidates_path = run_dir / "candidates.md"
        if not retrieve_path.is_file():
            missing_retrieve.append(run_dir.name)
            continue
        runs_scanned += 1
        hits_by_tmdb, quality_by_tmdb, diagnostics_by_tmdb = _load_retrieve_meta(
            retrieve_path
        )
        candidates_text, run_id = _load_candidates_text(run_dir, retrieve_path)
        new_text, high = score_candidates_md(
            candidates_text,
            run_id,
            hits_by_tmdb,
            quality_by_tmdb=quality_by_tmdb,
            diagnostics_by_tmdb=diagnostics_by_tmdb,
            min_total_score=min_total_score,
        )
        if write_candidates and candidates_path.is_file():
            candidates_path.write_text(new_text, encoding="utf-8")
        multi, single = _split_multi_single(high)
        run_reviews.append(
            RunHighHitReview(
                run_id=run_dir.name,
                reality_text=_read_reality(run_dir),
                multi_agent=multi,
                single_agent=single,
            )
        )
        all_high.extend(high)

    return run_reviews, all_high, missing_retrieve, runs_scanned


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
        "--review-out",
        type=Path,
        default=None,
        help=(
            "High-hit review markdown path (default: <eval-dir>/high-hit-score-review.md). "
            "Use an explicit path when --dir is not the batch root you want reviewed."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Do not write review file or patch existing candidates.md",
    )
    parser.add_argument(
        "--judge-json",
        type=Path,
        default=None,
        help=(
            "Merge LLM judge scores from JSON into the review after generation "
            "(default: <eval-dir>/llm-judge-scores.json when file exists)"
        ),
    )
    args = parser.parse_args(argv)

    eval_dir = args.dir if args.dir.is_absolute() else _REPO_ROOT / args.dir
    review_path = (
        args.review_out
        if args.review_out is not None
        else _default_review_path(eval_dir)
    )
    if not review_path.is_absolute():
        review_path = _REPO_ROOT / review_path
    run_reviews, all_high, missing, runs_scanned = process_eval_dir(
        eval_dir,
        write_candidates=not args.dry_run,
        min_total_score=args.min_score,
    )
    review_text = _format_high_hit_review(
        run_reviews, runs_scanned=runs_scanned, min_score=args.min_score
    )
    judge_path = args.judge_json
    if judge_path is None and not args.dry_run:
        default_judge = eval_dir / "llm-judge-scores.json"
        if default_judge.is_file():
            judge_path = default_judge
    if judge_path is not None:
        if not judge_path.is_absolute():
            judge_path = _REPO_ROOT / judge_path
        if judge_path.is_file():
            from scripts.llm_judge import integrate_judge_into_review, load_judge_output

            review_text = integrate_judge_into_review(
                review_text, load_judge_output(judge_path)
            )
        elif args.judge_json is not None:
            print(f"warning: judge JSON not found: {judge_path}", file=sys.stderr)
    if not args.dry_run:
        review_path.parent.mkdir(parents=True, exist_ok=True)
        review_path.write_text(review_text, encoding="utf-8")

    all_high.sort(key=lambda c: (-c.total_score, c.run_id, c.tmdb_id))
    print(f"Runs scanned: {runs_scanned}")
    print(f"Candidates with pseudo命中分合计 >= {args.min_score}: {len(all_high)}")
    if missing:
        print(f"Missing retrieve.json: {', '.join(missing)}")
    print("Top 5 by score:")
    for c in all_high[:5]:
        print(f"  {c.total_score:3d}  {c.run_id}  {c.tmdb_id}  {c.title}")
    if not args.dry_run:
        print(f"Wrote {review_path.relative_to(_REPO_ROOT)}")
        if review_path.resolve() == _LEGACY_HIGH_HIT_REVIEW.resolve():
            print(
                "Note: wrote legacy output/Eval/high-hit-score-review.md; "
                "prefer --dir output/Eval/phase3.6 for phase-scoped review.",
                file=sys.stderr,
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
