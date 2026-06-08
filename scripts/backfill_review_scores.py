"""Merge past-phase 共振分 / 共振类型 / 打分备注 into high-hit-score-review.md.

Past scores are inlined into the three editor fields (never a separate 历史打分 line).
Match key: tmdb_id (primary), normalized movie title (fallback).
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]

_HEADING = re.compile(r"^###\s+(.+)$", re.MULTILINE)
_TMDB_LINE = re.compile(r"^-\s*\*\*tmdb_id\*\*:\s*(\d+)\s*$", re.MULTILINE)
_SCORE_LINE = re.compile(r"^(-\s*\*\*共振分\*\*:)(.*)$", re.MULTILINE)
_TYPE_LINE = re.compile(r"^(-\s*\*\*共振类型\*\*:)(.*)$", re.MULTILINE)
_REMARK_LINE = re.compile(r"^(-\s*\*\*打分备注\*\*:)(.*)$", re.MULTILINE)
_HISTORY_LINE = re.compile(r"^-\s*\*\*历史打分\*\*:.*\n", re.MULTILINE)
_SCORE_COMMENT = "  <!-- 总编填写 0 / 1 / 2 -->"
_TYPE_COMMENT = (
    "  <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->"
)
_REMARK_PLACEHOLDER = "（可选）"
_TITLE_YEAR = re.compile(r"^(.+?)\s*\(\d{4}\)")

_PHASE_SOURCES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "phase3.5",
        (
            "output/Eval/phase3.5/high-hit-score-review.md",
            "output/Eval/phase3.5/multi-agent-hits-review.md",
        ),
    ),
    ("phase3.6", ("output/Eval/phase3.6/high-hit-score-review.md",)),
    ("phase3.7", ("output/Eval/phase3.7/high-hit-score-review.md",)),
)

_HEADER_CONFLICT_OLD = (
    "- **Conflict policy:** differing past scores kept in **历史打分**; "
    "phase 3.8 fields left blank for re-score"
)
_HEADER_CONFLICT_NEW = (
    "- **Conflict policy:** differing past scores/types inlined in "
    "**共振分** / **共振类型** / **打分备注**; phase 3.8 value left blank for re-score"
)
_HEADER_BACKFILL_NOTE = (
    "- **Backfill format:** past phase scores appear inline in editor fields "
    "(not a separate 历史打分 line)"
)


@dataclass(frozen=True)
class PastScore:
    phase: str
    score: int
    resonance_type: str | None
    remark: str | None


def _strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def _parse_score(raw: str) -> int | None:
    cleaned = _strip_html_comments(raw).strip()
    match = re.search(r"\b([012])\b", cleaned)
    return int(match.group(1)) if match else None


def _parse_editor_score(raw: str) -> int | None:
    """Return score only when the editor filled a plain value (not backfill inline)."""
    cleaned = _strip_html_comments(raw).strip()
    if not cleaned or "（" in cleaned or " / " in cleaned:
        return None
    return _parse_score(raw)


def _parse_editor_type(raw: str) -> str | None:
    cleaned = _strip_html_comments(raw).strip()
    if not cleaned or "（" in cleaned or " / " in cleaned:
        return None
    return _parse_resonance_type(raw)


def _parse_resonance_type(raw: str) -> str | None:
    from scripts.resonance_rubric import parse_resonance_type

    return parse_resonance_type(raw)


def _normalize_title(heading: str) -> str:
    title = heading.split("[", 1)[0].strip()
    match = _TITLE_YEAR.match(title)
    return (match.group(1) if match else title).strip().lower()


def _parse_remark(raw: str) -> str | None:
    cleaned = raw.strip()
    if not cleaned or cleaned == _REMARK_PLACEHOLDER:
        return None
    return cleaned


def _parse_blocks(text: str) -> list[tuple[str, str]]:
    """Return (heading, block_text) for each ### candidate block."""
    blocks: list[tuple[str, str]] = []
    for match in _HEADING.finditer(text):
        start = match.start()
        end = _HEADING.search(text, match.end())
        block = text[start : end.start() if end else len(text)]
        blocks.append((match.group(1), block))
    return blocks


def _collect_past_scores(repo_root: Path) -> tuple[dict[int, list[PastScore]], dict[str, list[PastScore]]]:
    by_tmdb: dict[int, list[PastScore]] = {}
    by_title: dict[str, list[PastScore]] = {}

    for phase, rel_paths in _PHASE_SOURCES:
        for rel_path in rel_paths:
            path = repo_root / rel_path
            if not path.is_file():
                continue
            for heading, block in _parse_blocks(path.read_text(encoding="utf-8")):
                tmdb_match = _TMDB_LINE.search(block)
                if not tmdb_match:
                    continue
                score = _parse_score(_score_value(block))
                if score is None:
                    continue
                entry = PastScore(
                    phase=phase,
                    score=score,
                    resonance_type=_parse_resonance_type(_type_value(block)),
                    remark=_parse_remark(_remark_value(block)),
                )
                tmdb_id = int(tmdb_match.group(1))
                existing = by_tmdb.setdefault(tmdb_id, [])
                if not any(e.phase == phase for e in existing):
                    existing.append(entry)
                title_key = _normalize_title(heading)
                title_existing = by_title.setdefault(title_key, [])
                if not any(e.phase == phase for e in title_existing):
                    title_existing.append(entry)
    return by_tmdb, by_title


def _score_value(block: str) -> str:
    match = _SCORE_LINE.search(block)
    return match.group(2) if match else ""


def _type_value(block: str) -> str:
    match = _TYPE_LINE.search(block)
    return match.group(2) if match else ""


def _remark_value(block: str) -> str:
    match = _REMARK_LINE.search(block)
    return match.group(2) if match else ""


def _lookup_past(
    *,
    tmdb_id: int,
    heading: str,
    by_tmdb: dict[int, list[PastScore]],
    by_title: dict[str, list[PastScore]],
) -> list[PastScore]:
    if tmdb_id in by_tmdb:
        return list(by_tmdb[tmdb_id])
    title_key = _normalize_title(heading)
    return list(by_title.get(title_key, []))


def _score_conflict(past: list[PastScore]) -> bool:
    return len({p.score for p in past}) > 1


def _type_conflict(past: list[PastScore]) -> bool:
    types = {p.resonance_type for p in past if p.resonance_type}
    return len(types) > 1


def _has_conflict(past: list[PastScore]) -> bool:
    if len(past) < 2:
        return False
    return _score_conflict(past) or _type_conflict(past)


def _format_score_value(past: list[PastScore], *, conflict: bool, current: int | None) -> str:
    if conflict and _score_conflict(past):
        parts = " / ".join(f"{p.score}（{p.phase}）" for p in past)
        return f"{parts}{_SCORE_COMMENT}"
    if conflict and not current:
        score = past[-1].score
        if len(past) > 1:
            detail = "；".join(f"{p.phase}: {p.score}" for p in past)
            return f"{score}（{detail}）{_SCORE_COMMENT}"
    if current is not None:
        return f"{current}{_SCORE_COMMENT}"
    score = past[-1].score
    if len(past) == 1:
        return f"{score}{_SCORE_COMMENT}"
    detail = "；".join(f"{p.phase}: {p.score}" for p in past)
    return f"{score}（{detail}）{_SCORE_COMMENT}"


def _format_type_value(past: list[PastScore], *, conflict: bool, current: str | None) -> str:
    if conflict and _type_conflict(past):
        parts = " / ".join(
            f"{p.resonance_type or '—'}（{p.phase}）" for p in past
        )
        return f"{parts}{_TYPE_COMMENT}"
    if current:
        return f"{current}{_TYPE_COMMENT}"
    rtype = past[-1].resonance_type or ""
    if not rtype:
        return _TYPE_COMMENT
    if len(past) == 1:
        return f"{rtype}{_TYPE_COMMENT}"
    detail = "；".join(
        f"{p.phase}: {p.resonance_type or '—'}" for p in past
    )
    return f"{rtype}（{detail}）{_TYPE_COMMENT}"


def _format_remark_value(
    past: list[PastScore], *, conflict: bool, current: str | None
) -> str:
    if conflict:
        parts = [
            f"{p.phase}: {p.remark}" if p.remark else f"{p.phase}: （无）"
            for p in past
        ]
        return "；".join(parts)
    if len(past) > 1:
        parts = [f"{p.phase}: {p.remark}" for p in past if p.remark]
        if parts:
            return "；".join(parts)
        return _REMARK_PLACEHOLDER
    if current:
        return current
    if past and past[-1].remark:
        return past[-1].remark  # type: ignore[return-value]
    return _REMARK_PLACEHOLDER


def _update_header(text: str) -> str:
    text = text.replace(_HEADER_CONFLICT_OLD, _HEADER_CONFLICT_NEW)
    if _HEADER_BACKFILL_NOTE not in text:
        text = text.replace(
            _HEADER_CONFLICT_NEW,
            f"{_HEADER_CONFLICT_NEW}\n{_HEADER_BACKFILL_NOTE}",
        )
    return text


def _apply_block(
    block: str,
    *,
    heading: str,
    by_tmdb: dict[int, list[PastScore]],
    by_title: dict[str, list[PastScore]],
) -> tuple[str, bool]:
    tmdb_match = _TMDB_LINE.search(block)
    if not tmdb_match:
        new_block = _HISTORY_LINE.sub("", block)
        return new_block, new_block != block

    tmdb_id = int(tmdb_match.group(1))
    past = _lookup_past(
        tmdb_id=tmdb_id, heading=heading, by_tmdb=by_tmdb, by_title=by_title
    )
    current_score = _parse_editor_score(_score_value(block))
    current_type = _parse_editor_type(_type_value(block))
    current_remark = _parse_remark(_remark_value(block))

    out = _HISTORY_LINE.sub("", block)
    changed = out != block

    if not past:
        return out, changed

    conflict = _has_conflict(past)
    if conflict or current_score is None:
        score_val = _format_score_value(past, conflict=conflict, current=current_score)
        type_val = _format_type_value(past, conflict=conflict, current=current_type)
        remark_val = _format_remark_value(
            past, conflict=conflict, current=current_remark
        )
        out2 = _SCORE_LINE.sub(rf"\1 {score_val}", out, count=1)
        out2 = _TYPE_LINE.sub(rf"\1 {type_val}", out2, count=1)
        out2 = _REMARK_LINE.sub(rf"\1 {remark_val}", out2, count=1)
        if out2 != out:
            changed = True
        out = out2
    elif current_remark is None and any(p.remark for p in past):
        remark_val = _format_remark_value(
            past, conflict=False, current=current_remark
        )
        out2 = _REMARK_LINE.sub(rf"\1 {remark_val}", out, count=1)
        if out2 != out:
            changed = True
        out = out2

    return out, changed


def backfill_review(
    review_path: Path,
    *,
    repo_root: Path = _REPO_ROOT,
) -> tuple[str, int]:
    """Return (updated_text, blocks_changed)."""
    by_tmdb, by_title = _collect_past_scores(repo_root)
    text = review_path.read_text(encoding="utf-8")
    text = _update_header(text)

    parts = re.split(r"(?=^###\s+)", text, flags=re.MULTILINE)
    changed_count = 0
    rebuilt = parts[0]
    for part in parts[1:]:
        heading_match = _HEADING.search(part)
        heading = heading_match.group(1) if heading_match else ""
        new_part, changed = _apply_block(
            part, heading=heading, by_tmdb=by_tmdb, by_title=by_title
        )
        if changed:
            changed_count += 1
        rebuilt += new_part

    return rebuilt, changed_count


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--review",
        type=Path,
        default=_REPO_ROOT / "output" / "Eval" / "phase3.8" / "high-hit-score-review.md",
        help="Target high-hit-score-review.md",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print stats only; do not write file",
    )
    args = parser.parse_args(argv)
    review_path = args.review if args.review.is_absolute() else _REPO_ROOT / args.review
    if not review_path.is_file():
        print(f"review not found: {review_path}", file=sys.stderr)
        return 1

    updated, changed = backfill_review(review_path)
    if not args.dry_run:
        review_path.write_text(updated, encoding="utf-8", newline="\n")
    print(f"updated {changed} candidate block(s) in {review_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
