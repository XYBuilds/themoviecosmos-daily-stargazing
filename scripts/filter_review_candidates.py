"""filter_review_candidates.py · Filter high-hit-score-review.md by eval criteria."""

from __future__ import annotations

import argparse
import re
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.summarize_eval import (  # noqa: E402
    _AGENTS_TAG,
    _DISTINCT_AGENTS_LINE,
    _NEUTRAL_HIT_RATE_LINE,
    _NEUTRAL_HITS_LINE,
    _REVIEW_RUN_SECTION,
    _parse_agents_from_heading,
)

_DEFAULT_IN = _REPO_ROOT / "output" / "Eval" / "phase3.8" / "high-hit-score-review.md"
_DEFAULT_OUT = _REPO_ROOT / "output" / "Eval" / "phase3.8" / "multi-agent-neutral-hits-review.md"

_CANDIDATE_BLOCK_START = re.compile(r"^<!-- run_id:", re.MULTILINE)
_HIT_AGENT = re.compile(r"^\s*-\s+(THE-[A-Z]+)/", re.MULTILINE)
_SUBSECTION = re.compile(r"^### (多 agents 命中|单 agent 命中)\s*$", re.MULTILINE)


def _split_run_sections(text: str) -> list[tuple[str, str, str]]:
    """Return (run_id, preamble, body) for each ## run section."""
    matches = list(_REVIEW_RUN_SECTION.finditer(text))
    sections: list[tuple[str, str, str]] = []
    for index, match in enumerate(matches):
        run_id = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[start:end]
        first_candidate = _CANDIDATE_BLOCK_START.search(section)
        if first_candidate:
            preamble = section[: first_candidate.start()].rstrip()
            body = section[first_candidate.start() :]
        else:
            preamble = section.rstrip()
            body = ""
        sections.append((run_id, preamble, body))
    return sections


def _split_raw_candidate_blocks(body: str) -> list[str]:
    starts = [m.start() for m in _CANDIDATE_BLOCK_START.finditer(body)]
    if not starts:
        return []
    blocks: list[str] = []
    for index, start in enumerate(starts):
        end = starts[index + 1] if index + 1 < len(starts) else len(body)
        blocks.append(body[start:end].rstrip())
    return blocks


def _distinct_agents_in_hits(block: str) -> set[str]:
    return {m.group(1) for m in _HIT_AGENT.finditer(block)}


def _is_multi_agent(block: str) -> bool:
    heading_match = re.search(r"^### (.+)$", block, re.MULTILINE)
    heading = heading_match.group(1) if heading_match else ""
    agents_from_heading = _parse_agents_from_heading(f"### {heading}")

    da_match = _DISTINCT_AGENTS_LINE.search(block)
    if da_match and int(da_match.group(1)) >= 2:
        return True

    if len(agents_from_heading) >= 2:
        return True

    hit_agents = _distinct_agents_in_hits(block)
    if len(hit_agents) >= 2:
        return True

    return False


def _has_neutral_hits(block: str) -> bool:
    nh_match = _NEUTRAL_HITS_LINE.search(block)
    if nh_match:
        return int(nh_match.group(1)) > 0
    nhr_match = _NEUTRAL_HIT_RATE_LINE.search(block)
    if nhr_match:
        return float(nhr_match.group(1)) > 0.0
    return False


def _matches_filter(block: str) -> bool:
    return _is_multi_agent(block)


def _extract_global_header(text: str) -> str:
    first_run = _REVIEW_RUN_SECTION.search(text)
    if not first_run:
        return text.rstrip()
    return text[: first_run.start()].rstrip()


def render_filtered_review(
    text: str,
    *,
    source_name: str,
    generated_at: datetime | None = None,
) -> tuple[str, dict[str, int]]:
    """Return filtered markdown and per-run_id counts."""
    gen = generated_at or datetime.now(UTC)
    gen_date = gen.strftime("%Y-%m-%d %H:%M UTC")

    all_blocks: list[tuple[str, str]] = []
    per_run: dict[str, list[str]] = defaultdict(list)

    for run_id, _preamble, body in _split_run_sections(text):
        for block in _split_raw_candidate_blocks(body):
            if _matches_filter(block):
                all_blocks.append((run_id, block))
                per_run[run_id].append(block)

    total = len(all_blocks)
    run_counts = {run_id: len(blocks) for run_id, blocks in sorted(per_run.items())}

    lines = [
        "# Multi-Agent Hits — Filtered Review",
        "",
        "## Filter summary",
        "",
        f"- **Source:** `{source_name}`",
        "- **Filter criteria (ALL must match):**",
        "  1. **多 agent 命中** — `distinct_agents` ≥ 2, or ≥2 agents in heading / hit lines; `quality_candidate` is ignored as a filter and shown only as retrieve annotation",
        "  2. **n1 / neutral_hits** — diagnostic-only; shown when present, never used as this filter's inclusion criterion",
        f"- **Generated:** {gen_date}",
        f"- **Total matching candidates:** {total}",
        f"- **Runs with matches:** {len(run_counts)}",
        "",
        "### Count by run_id",
        "",
        "| run_id | count |",
        "| --- | ---: |",
    ]
    for run_id, count in run_counts.items():
        lines.append(f"| {run_id} | {count} |")
    if not run_counts:
        lines.append("| — | 0 |")

    lines.extend(["", "---", ""])

    for run_id, preamble, body in _split_run_sections(text):
        blocks = per_run.get(run_id, [])
        if not blocks:
            continue
        lines.append(f"## {run_id}")
        lines.append("")
        if preamble:
            cleaned = _SUBSECTION.sub("", preamble)
            cleaned = re.sub(
                r"^\*\*Count:\*\* \d+ candidate\(s\)\s*$",
                "",
                cleaned,
                flags=re.MULTILINE,
            ).rstrip()
            if cleaned:
                lines.append(cleaned)
                lines.append("")
        lines.append("### 多 agents 命中")
        lines.append("")
        lines.append(f"**Count:** {len(blocks)} candidate(s)")
        lines.append("")
        for index, block in enumerate(blocks):
            if index:
                lines.append("")
            lines.append(block)
        lines.append("")

    return "\n".join(lines).rstrip() + "\n", run_counts


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        default=_DEFAULT_IN,
        help="Input high-hit-score-review.md",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=_DEFAULT_OUT,
        help="Output filtered review markdown",
    )
    args = parser.parse_args(argv)

    in_path = args.in_path if args.in_path.is_absolute() else _REPO_ROOT / args.in_path
    out_path = args.out if args.out.is_absolute() else _REPO_ROOT / args.out

    text = in_path.read_text(encoding="utf-8")
    rendered, run_counts = render_filtered_review(
        text,
        source_name=in_path.relative_to(_REPO_ROOT).as_posix(),
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")

    total = sum(run_counts.values())
    print(f"Wrote {total} candidates → {out_path}")
    for run_id, count in run_counts.items():
        print(f"  {run_id}: {count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
