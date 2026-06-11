"""Canonical 2×2 resonance rubric (SSOT: docs/eval-the-bet.md §4)."""

from __future__ import annotations

import re

TYPE_NONE = "无共振（偶然词面重叠）"
TYPE_DEEP = "深层共振（仅逻辑，无表层）"
TYPE_SURFACE = "表层沾边"
TYPE_STRONG = "强共振（表层 + 逻辑）"

SUB_LABEL_POV_TRANSFORM = "POV变换"

VALID_SCORE_TYPES = frozenset({TYPE_DEEP, TYPE_SURFACE, TYPE_STRONG})
STRUCTURAL_TYPES = frozenset({TYPE_DEEP, TYPE_STRONG})

# Legacy labels (phase ≤3.8 human scores)
_LEGACY_TO_CANONICAL = {
    "表层": TYPE_SURFACE,
    "表层元素": TYPE_SURFACE,
    "结构": TYPE_DEEP,
    "深层逻辑": TYPE_DEEP,
    "双重": TYPE_STRONG,
    "深层共振（仅结构，无表层）": TYPE_DEEP,
    "强共振（表层 + 结构）": TYPE_STRONG,
}

_TYPE_PARSE_ORDER = (
    TYPE_STRONG,
    TYPE_DEEP,
    TYPE_SURFACE,
    TYPE_NONE,
    "强共振（表层 + 结构）",
    "深层共振（仅结构，无表层）",
    "深层逻辑",
    "表层元素",
    "双重",
    "结构",
    "表层",
)


def strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def parse_resonance_type(raw: str) -> str | None:
    """Parse editor or judge resonance_type; returns canonical label or None."""
    cleaned = strip_html_comments(raw).strip()
    if not cleaned:
        return None
    for token in _TYPE_PARSE_ORDER:
        if token in cleaned:
            return _LEGACY_TO_CANONICAL.get(token, token)
    return None


def validate_score_type_pair(score: int, resonance_type: str | None) -> None:
    """Raise ValueError when score and resonance_type disagree with the 2×2 matrix."""
    if score == 0:
        if resonance_type is not None:
            raise ValueError("score 0 must have null resonance_type")
        return
    if resonance_type is None:
        raise ValueError("score 1/2 requires resonance_type")
    if resonance_type not in VALID_SCORE_TYPES:
        raise ValueError(f"invalid resonance_type {resonance_type!r}")
    if score == 1 and resonance_type not in (TYPE_DEEP, TYPE_SURFACE):
        raise ValueError(
            f"score 1 must use {TYPE_DEEP!r} or {TYPE_SURFACE!r}"
        )
    if score == 2 and resonance_type != TYPE_STRONG:
        raise ValueError(f"score 2 must use {TYPE_STRONG!r}")


def parse_pov_transform(raw: str) -> bool | None:
    """Parse human or judge POV变换 sub-label line; None = unset."""
    cleaned = strip_html_comments(raw).strip()
    if not cleaned:
        return None
    if SUB_LABEL_POV_TRANSFORM in cleaned:
        return True
    lowered = cleaned.lower()
    if lowered in {"是", "yes", "true", "y", "1"}:
        return True
    if lowered in {"否", "no", "false", "n", "0", "—", "-", "无", "留空"}:
        return False
    return None


def validate_pov_transform_sub_label(
    score: int,
    resonance_type: str | None,
    pov_transform: bool | None,
) -> bool | None:
    """Normalize POV变换 sub-label; must stay compatible with the 2×2 matrix."""
    if pov_transform is None or pov_transform is False:
        return False if pov_transform is False else None
    if score != 2 or resonance_type != TYPE_STRONG:
        raise ValueError(
            f"{SUB_LABEL_POV_TRANSFORM} applies only to score 2 + {TYPE_STRONG!r}"
        )
    return True
