"""Backfill 共振分 / 共振类型 / 打分备注 from past eval reviews into a target review file."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_RUN_ID_COMMENT = re.compile(r"<!--\s*run_id:\s*(\S+)\s*-->")
_TMDB_LINE = re.compile(r"^-\s*\*\*tmdb_id\*\*:\s*(\d+)\s*$", re.MULTILINE)
_SCORE_LINE = re.compile(r"^(-\s*\*\*共振分\*\*:)(.*)$", re.MULTILINE)
_TYPE_LINE = re.compile(r"^(-\s*\*\*共振类型\*\*:)(.*)$", re.MULTILINE)
_REMARK_LINE = re.compile(r"^(-\s*\*\*打分备注\*\*:)(.*)$", re.MULTILINE)
_HISTORY_LINE = re.compile(r"^(-\s*\*\*历史打分\*\*:)(.*)$", re.MULTILINE)
_HEADING = re.compile(r"^###\s+(.+?)\s*(?:\[|$)", re.MULTILINE)
_SCORE_VALUE = re.compile(r"\b([012])\b")
_PLACEHOLDER_ONLY = re.compile(r"^\s*(?:<!--.*-->)?\s*$")


@dataclass(frozen=True)
class EditorScore:
    phase: str
    score: str
    resonance_type: str
    remark: str
    source: str
    tmdb_id: int | None = None
    title: str = ""
    run_id: str = ""

    @property
    def key(self) -> tuple[str, str, str]:
        return (self.score, self.resonance_type, self.remark)

    def label(self) -> str:
        parts = [self.phase, f"{self.score} / {self.resonance_type or '—'}"]
        if self.remark:
            parts.append(self.remark)
        return "（" + " / ".join(parts[:2]) + (f" / {self.remark}" if self.remark else "") + "）"


def _normalize_title(title: str) -> str:
    t = re.sub(r"\s*\(\d{4}\)\s*$", "", title.strip())
    return re.sub(r"\s+", " ", t).casefold()


def _strip_field_value(raw: str) -> str:
    no_comment = re.sub(r"<!--.*?-->", "", raw).strip()
    return no_comment


def _parse_score_value(raw: str) -> str | None:
    cleaned = _strip_field_value(raw)
    match = _SCORE_VALUE.search(cleaned)
    return match.group(1) if match else None


def _is_filled_field(raw: str) -> bool:
    cleaned = _strip_field_value(raw)
    if not cleaned:
        return False
    if cleaned in {"（可选）", "(可选)"}:
        return False
    return True


def _parse_review_blocks(text: str, phase: str, source: str) -> list[EditorScore]:
    entries: list[EditorScore] = []
    run_id = ""
    headings = list(re.finditer(r"^###\s+.+$", text, re.MULTILINE))
    for i, match in enumerate(headings):
        start = match.start()
        end = headings[i + 1].start() if i + 1 < len(headings) else len(text)
        block = text[start:end]
        run_comment = _RUN_ID_COMMENT.search(block)
        if run_comment:
            run_id = run_comment.group(1)
        heading = _HEADING.search(block)
        title = heading.group(1).strip() if heading else ""
        tmdb_match = _TMDB_LINE.search(block)
        tmdb_id = int(tmdb_match.group(1)) if tmdb_match else None

        score_match = _SCORE_LINE.search(block)
        if not score_match:
            continue
        score_val = _parse_score_value(score_match.group(2))
        if score_val is None:
            continue

        type_match = _TYPE_LINE.search(block)
        remark_match = _REMARK_LINE.search(block)
        resonance_type = _strip_field_value(type_match.group(2)) if type_match else ""
        remark = _strip_field_value(remark_match.group(2)) if remark_match else ""
        if remark in {"（可选）", "(可选)"}:
            remark = ""

        entries.append(
            EditorScore(
                phase=phase,
                score=score_val,
                resonance_type=resonance_type,
                remark=remark,
                source=source,
                tmdb_id=tmdb_id,
                title=title,
                run_id=run_id,
            )
        )
    return entries


def _collect_sources(sources: list[tuple[str, Path]]) -> tuple[dict[int, list[EditorScore]], dict[str, list[EditorScore]]]:
    by_tmdb: dict[int, list[EditorScore]] = {}
    by_title: dict[str, list[EditorScore]] = {}
    priority = {"high-hit-score-review.md": 0, "multi-agent-hits-review.md": 1, "candidates.md": 2}

    all_entries: list[tuple[int, EditorScore]] = []
    for phase, path in sources:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for entry in _parse_review_blocks(text, phase, str(path.relative_to(_REPO_ROOT))):
            prio = priority.get(path.name, 9)
            tmdb_id = getattr(entry, "tmdb_id", None)
            all_entries.append((prio, entry))

    # dedupe per phase+tmdb: keep highest-priority source
    seen_phase_tmdb: set[tuple[str, int]] = set()
    seen_phase_title: set[tuple[str, str]] = set()
    for prio, entry in sorted(all_entries, key=lambda x: x[0]):
        tmdb_id = entry.tmdb_id
        title_key = _normalize_title(entry.title)
        if tmdb_id is not None:
            key = (entry.phase, tmdb_id)
            if key in seen_phase_tmdb:
                continue
            seen_phase_tmdb.add(key)
            by_tmdb.setdefault(tmdb_id, []).append(entry)
        elif title_key:
            key = (entry.phase, title_key)
            if key in seen_phase_title:
                continue
            seen_phase_title.add(key)
            by_title.setdefault(title_key, []).append(entry)
    return by_tmdb, by_title


def _lookup_past(
    tmdb_id: int | None,
    title: str,
    by_tmdb: dict[int, list[EditorScore]],
    by_title: dict[str, list[EditorScore]],
) -> list[EditorScore]:
    if tmdb_id is not None and tmdb_id in by_tmdb:
        return by_tmdb[tmdb_id]
    title_key = _normalize_title(title)
    if title_key and title_key in by_title:
        return by_title[title_key]
    return []


def _format_history(labels: list[str]) -> str:
    return " ".join(labels)


def _insert_history(out: str, hist: str) -> str:
    if _HISTORY_LINE.search(out):
        return _HISTORY_LINE.sub(rf"\1 {hist}", out, count=1)
    remark_match = _REMARK_LINE.search(out)
    if remark_match:
        insert_at = remark_match.end()
        return out[:insert_at] + f"\n- **历史打分**: {hist}" + out[insert_at:]
    score_match = _SCORE_LINE.search(out)
    if score_match:
        insert_at = score_match.end()
        return out[:insert_at] + f"\n- **历史打分**: {hist}" + out[insert_at:]
    return out.rstrip() + f"\n- **历史打分**: {hist}\n"


def _backfill_block(
    block: str,
    by_tmdb: dict[int, list[EditorScore]],
    by_title: dict[str, list[EditorScore]],
) -> tuple[str, bool, bool]:
    heading = _HEADING.search(block)
    title = heading.group(1).strip() if heading else ""
    tmdb_match = _TMDB_LINE.search(block)
    tmdb_id = int(tmdb_match.group(1)) if tmdb_match else None

    past = _lookup_past(tmdb_id, title, by_tmdb, by_title)
    if not past:
        return block, False, False

    score_match = _SCORE_LINE.search(block)
    if not score_match:
        return block, False, False

    current_score_filled = _is_filled_field(score_match.group(2))
    if current_score_filled:
        return block, False, False  # preserve user edits

    unique_score_type = {(p.score, p.resonance_type) for p in past}
    labels = []
    seen_label: set[str] = set()
    for p in sorted(past, key=lambda x: x.phase):
        lbl = p.label()
        if lbl not in seen_label:
            labels.append(lbl)
            seen_label.add(lbl)

    conflict = len(unique_score_type) > 1
    remarks = [p.remark for p in past if p.remark]
    unique_remarks = list(dict.fromkeys(remarks))
    out = block

    if not conflict:
        p = past[0]
        remark_val = unique_remarks[0] if len(unique_remarks) == 1 else " · ".join(unique_remarks)
        out = _SCORE_LINE.sub(
            rf"\1 {p.score}  <!-- 总编填写 0 / 1 / 2 -->",
            out,
            count=1,
        )
        type_val = p.resonance_type if p.score != "0" else ""
        out = _TYPE_LINE.sub(
            rf"\1 {type_val}  <!-- 表层 / 结构 / 双重；0 分留空 -->",
            out,
            count=1,
        )
        out = _REMARK_LINE.sub(rf"\1 {remark_val}", out, count=1)
        if len(labels) > 1:
            out = _insert_history(out, _format_history(labels))
    else:
        out = _insert_history(out, _format_history(labels))

    return out, True, conflict


def _header_note(phases: list[str]) -> str:
    phase_list = ", ".join(phases)
    return (
        f"\n### Past score backfill\n\n"
        f"- **Merged from:** {phase_list}\n"
        f"- **Match key:** `tmdb_id` (primary), normalized movie title (fallback)\n"
        f"- **Conflict policy:** differing past scores kept in **历史打分**; phase 3.8 fields left blank for re-score\n"
    )


def backfill(target: Path, sources: list[tuple[str, Path]], dry_run: bool = False) -> dict[str, int]:
    by_tmdb, by_title = _collect_sources(sources)
    text = target.read_text(encoding="utf-8")

    matched = 0
    conflicts = 0
    filled = 0
    parts = re.split(r"(?=^###\s+)", text, flags=re.MULTILINE)
    rebuilt = parts[0]

    for part in parts[1:]:
        new_part, was_matched, was_conflict = _backfill_block(part, by_tmdb, by_title)
        if was_matched:
            matched += 1
            if was_conflict:
                conflicts += 1
            elif new_part != part:
                filled += 1
        rebuilt += new_part

    phases = sorted({p for p, _ in sources})
    note = _header_note(phases)
    if "### Past score backfill" not in rebuilt:
        marker = "## 留出集打分（3.8.7 · 总编必填）"
        if marker in rebuilt:
            idx = rebuilt.index(marker)
            end = rebuilt.find("\n## ", idx + 1)
            insert_at = end if end != -1 else rebuilt.find("\n## 01-", idx)
            if insert_at == -1:
                insert_at = rebuilt.find("\n## 01-grid-outage")
            rebuilt = rebuilt[:insert_at] + note + rebuilt[insert_at:]
        else:
            rebuilt = rebuilt.replace("\n## 01-grid-outage", note + "\n## 01-grid-outage", 1)

    if not dry_run and rebuilt != text:
        target.write_text(rebuilt, encoding="utf-8", newline="\n")

    return {
        "matched": matched,
        "filled": filled,
        "conflicts": conflicts,
        "tmdb_keys": len(by_tmdb),
        "title_keys": len(by_title),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--target",
        type=Path,
        default=_REPO_ROOT / "output" / "Eval" / "phase3.8" / "high-hit-score-review.md",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    eval_root = _REPO_ROOT / "output" / "Eval"
    sources: list[tuple[str, Path]] = [
        ("phase3.5", eval_root / "phase3.5" / "multi-agent-hits-review.md"),
        ("phase3.6", eval_root / "phase3.6" / "high-hit-score-review.md"),
        ("phase3.7", eval_root / "phase3.7" / "high-hit-score-review.md"),
    ]
    for phase in ("phase3.6",):
        phase_dir = eval_root / phase
        if phase_dir.is_dir():
            for candidates in sorted(phase_dir.glob("*/candidates.md")):
                sources.append((phase, candidates))

    stats = backfill(args.target, sources, dry_run=args.dry_run)
    print(
        f"matched={stats['matched']} filled={stats['filled']} conflicts={stats['conflicts']} "
        f"source_tmdb={stats['tmdb_keys']} source_title={stats['title_keys']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
