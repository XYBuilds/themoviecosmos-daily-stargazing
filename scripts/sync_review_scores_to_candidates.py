"""Copy 共振分 / 共振类型 / 打分备注 from high-hit-score-review.md into run candidates.md."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_RUN_ID_COMMENT = re.compile(r"<!--\s*run_id:\s*(\S+)\s*-->")
_TMDB_LINE = re.compile(r"^-\s*\*\*tmdb_id\*\*:\s*(\d+)\s*$", re.MULTILINE)
_SCORE_LINE = re.compile(r"^(-\s*\*\*共振分\*\*:)(.*)$", re.MULTILINE)
_TYPE_LINE = re.compile(r"^(-\s*\*\*共振类型\*\*:)(.*)$", re.MULTILINE)
_REMARK_LINE = re.compile(r"^(-\s*\*\*打分备注\*\*:)(.*)$", re.MULTILINE)
_HEADING = re.compile(r"^###\s+.+$", re.MULTILINE)


def _parse_review_blocks(text: str) -> dict[tuple[str, int], dict[str, str]]:
    """Map (run_id, tmdb_id) -> editor field lines (value portion only)."""
    scores: dict[tuple[str, int], dict[str, str]] = {}
    run_id = ""
    for match in _HEADING.finditer(text):
        start = match.start()
        end = _HEADING.search(text, match.end())
        block = text[start : end.start() if end else len(text)]
        run_comment = _RUN_ID_COMMENT.search(block)
        if run_comment:
            run_id = run_comment.group(1)
        tmdb_match = _TMDB_LINE.search(block)
        if not run_id or not tmdb_match:
            continue
        tmdb_id = int(tmdb_match.group(1))
        fields: dict[str, str] = {}
        for key, pattern in (
            ("score", _SCORE_LINE),
            ("type", _TYPE_LINE),
            ("remark", _REMARK_LINE),
        ):
            line_match = pattern.search(block)
            if line_match:
                fields[key] = line_match.group(2).strip()
        if "score" in fields and re.search(r"\b[012]\b", fields["score"]):
            scores[(run_id, tmdb_id)] = fields
    return scores


def _apply_to_candidates(path: Path, fields_by_tmdb: dict[int, dict[str, str]]) -> int:
    text = path.read_text(encoding="utf-8")
    updated = 0

    def replace_block(block: str) -> str:
        nonlocal updated
        tmdb_match = _TMDB_LINE.search(block)
        if not tmdb_match:
            return block
        tmdb_id = int(tmdb_match.group(1))
        fields = fields_by_tmdb.get(tmdb_id)
        if not fields:
            return block
        out = block
        if "score" in fields:
            out, n = _SCORE_LINE.subn(
                rf"\1 {fields['score']}  <!-- 总编填写 0 / 1 / 2 -->",
                out,
                count=1,
            )
            if n:
                updated += 1
        if "type" in fields:
            out = _TYPE_LINE.subn(
                rf"\1 {fields['type']}  <!-- 0 留空；1→深层共振|表层沾边；2→强共振 -->",
                out,
                count=1,
            )[0]
        if "remark" in fields:
            out = _REMARK_LINE.subn(rf"\1 {fields['remark']}", out, count=1)[0]
        return out

    parts = re.split(r"(?=^###\s+)", text, flags=re.MULTILINE)
    rebuilt = parts[0]
    for part in parts[1:]:
        rebuilt += replace_block(part)
    if rebuilt != text:
        path.write_text(rebuilt, encoding="utf-8", newline="\n")
    return updated


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--eval-dir",
        type=Path,
        default=_REPO_ROOT / "output" / "Eval" / "phase3.6",
        help="Phase eval directory containing high-hit-score-review.md and run folders",
    )
    parser.add_argument(
        "--review",
        type=Path,
        default=None,
        help="Review markdown (default: <eval-dir>/high-hit-score-review.md)",
    )
    args = parser.parse_args(argv)
    eval_dir = args.eval_dir if args.eval_dir.is_absolute() else _REPO_ROOT / args.eval_dir
    review_path = args.review or (eval_dir / "high-hit-score-review.md")
    if not review_path.is_file():
        print(f"review not found: {review_path}", file=sys.stderr)
        return 1

    scores = _parse_review_blocks(review_path.read_text(encoding="utf-8"))
    by_run: dict[str, dict[int, dict[str, str]]] = {}
    for (run_id, tmdb_id), fields in scores.items():
        by_run.setdefault(run_id, {})[tmdb_id] = fields

    total = 0
    for run_id, fields_by_tmdb in sorted(by_run.items()):
        candidates = eval_dir / run_id / "candidates.md"
        if not candidates.is_file():
            print(f"skip missing: {candidates}", file=sys.stderr)
            continue
        n = _apply_to_candidates(candidates, fields_by_tmdb)
        total += n
        print(f"{run_id}: synced {n} candidate(s)")

    print(f"done: {total} candidate block(s) updated across {len(by_run)} run(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
