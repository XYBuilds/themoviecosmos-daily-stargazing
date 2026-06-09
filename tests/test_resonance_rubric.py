"""Tests for scripts/resonance_rubric.py."""

from __future__ import annotations

import unittest

from scripts.resonance_rubric import (
    TYPE_DEEP,
    TYPE_STRONG,
    TYPE_SURFACE,
    parse_resonance_type,
    validate_score_type_pair,
)


class ResonanceRubricTests(unittest.TestCase):
    def test_parse_canonical_and_legacy(self):
        self.assertEqual(parse_resonance_type(TYPE_STRONG), TYPE_STRONG)
        self.assertEqual(parse_resonance_type("双重"), TYPE_STRONG)
        self.assertEqual(parse_resonance_type("结构"), TYPE_DEEP)
        self.assertEqual(parse_resonance_type("表层"), TYPE_SURFACE)
        self.assertEqual(
            parse_resonance_type("强共振（表层 + 结构）"), TYPE_STRONG
        )
        self.assertEqual(
            parse_resonance_type("深层共振（仅结构，无表层）"), TYPE_DEEP
        )

    def test_validate_matrix(self):
        validate_score_type_pair(0, None)
        validate_score_type_pair(1, TYPE_DEEP)
        validate_score_type_pair(1, TYPE_SURFACE)
        validate_score_type_pair(2, TYPE_STRONG)

    def test_validate_rejects_mismatch(self):
        with self.assertRaises(ValueError):
            validate_score_type_pair(1, TYPE_STRONG)
        with self.assertRaises(ValueError):
            validate_score_type_pair(2, TYPE_DEEP)


if __name__ == "__main__":
    unittest.main()
