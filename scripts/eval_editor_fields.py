"""Shared editor placeholder lines for eval candidate markdown blocks."""

from __future__ import annotations

import re

_RESONANCE_TYPE_LINE = re.compile(r"^(-\s*\*\*共振类型\*\*:.*)$", re.MULTILINE)
_POV_TRANSFORM_LINE = re.compile(r"^(-\s*\*\*POV变换\*\*:.*)$", re.MULTILINE)
_SCORING_REMARK_LINE = re.compile(r"^-\s*\*\*打分备注\*\*:", re.MULTILINE)

SCORING_REMARK_PLACEHOLDER = "（可选）"


def append_resonance_editor_lines(lines: list[str]) -> None:
    """Append 共振分 / 共振类型 / 打分备注 placeholders for human scoring."""
    lines.append("- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->")
    lines.append(
        "- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->"
    )
    lines.append(
        "- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->"
    )
    lines.append(f"- **打分备注**: {SCORING_REMARK_PLACEHOLDER}")


def ensure_scoring_remark_in_block(block: str) -> str:
    """Insert POV变换 + 打分备注 after 共振类型 when missing (idempotent)."""
    if _SCORING_REMARK_LINE.search(block):
        return block

    def _insert_after_resonance_type(match: re.Match[str]) -> str:
        lines = [match.group(1)]
        if not _POV_TRANSFORM_LINE.search(block):
            lines.append(
                "- **POV变换**:   <!-- 可选；仅 score 2 时填 是 -->"
            )
        lines.append(f"- **打分备注**: {SCORING_REMARK_PLACEHOLDER}")
        return "\n".join(lines)

    if _RESONANCE_TYPE_LINE.search(block):
        return _RESONANCE_TYPE_LINE.sub(_insert_after_resonance_type, block, count=1)
    return block
