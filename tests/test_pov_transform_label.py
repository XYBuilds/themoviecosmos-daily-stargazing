"""Tests for POV变换 resonance sub-label (Phase 3.11.5)."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.eval_editor_fields import append_resonance_editor_lines
from scripts.llm_judge import (
    _JUDGE_RUBRIC,
    JudgeResult,
    format_judge_block_lines,
    integrate_judge_into_review,
    parse_judge_response,
    validate_judge_payload,
    CalibrationReport,
    JudgeOutput,
    TRUST_STATUS_TRUSTED,
)
from scripts.resonance_rubric import (
    SUB_LABEL_POV_TRANSFORM,
    TYPE_DEEP,
    TYPE_STRONG,
    TYPE_SURFACE,
    parse_pov_transform,
    validate_pov_transform_sub_label,
    validate_score_type_pair,
)
from scripts.summarize_eval import parse_eval_markdown

_CAUSAL = "scarcity under grid failure drives families into survival mode"


class PovTransformParseTests(unittest.TestCase):
    def test_parse_human_affirmative_values(self):
        self.assertTrue(parse_pov_transform("是"))
        self.assertTrue(parse_pov_transform("yes"))
        self.assertTrue(parse_pov_transform("POV变换"))

    def test_parse_human_negative_or_empty(self):
        self.assertFalse(parse_pov_transform("否"))
        self.assertFalse(parse_pov_transform("no"))
        self.assertIsNone(parse_pov_transform(""))
        self.assertIsNone(parse_pov_transform("   "))


class PovTransformMatrixTests(unittest.TestCase):
    def test_sub_label_only_on_score_two_strong(self):
        self.assertTrue(
            validate_pov_transform_sub_label(2, TYPE_STRONG, True)
        )
        with self.assertRaises(ValueError):
            validate_pov_transform_sub_label(1, TYPE_DEEP, True)
        with self.assertRaises(ValueError):
            validate_pov_transform_sub_label(2, TYPE_SURFACE, True)

    def test_compatible_with_existing_score_type_matrix(self):
        for score, rtype in (
            (0, None),
            (1, TYPE_DEEP),
            (1, TYPE_SURFACE),
            (2, TYPE_STRONG),
        ):
            validate_score_type_pair(score, rtype)
            pov = validate_pov_transform_sub_label(score, rtype, False)
            self.assertFalse(pov)
            unset = validate_pov_transform_sub_label(score, rtype, None)
            self.assertIsNone(unset)


class JudgePovTransformTests(unittest.TestCase):
    def test_rubric_documents_sub_label(self):
        self.assertIn(SUB_LABEL_POV_TRANSFORM, _JUDGE_RUBRIC)
        self.assertIn("pov_transform", _JUDGE_RUBRIC)

    def test_validate_judge_payload_accepts_pov_transform_on_score_two(self):
        score, rtype, causal, pov = validate_judge_payload(
            {
                "score": 2,
                "resonance_type": TYPE_STRONG,
                "pov_transform": True,
                "causal_test": _CAUSAL,
                "rationale": "Gap A POV shift",
            }
        )
        self.assertEqual((score, rtype, causal, pov), (2, TYPE_STRONG, _CAUSAL, True))

    def test_validate_rejects_pov_transform_on_score_one(self):
        with self.assertRaises(ValueError):
            validate_judge_payload(
                {
                    "score": 1,
                    "resonance_type": TYPE_DEEP,
                    "pov_transform": True,
                    "causal_test": _CAUSAL,
                    "rationale": "invalid",
                }
            )

    def test_parse_judge_response_includes_pov_transform(self):
        text = (
            '{"score": 2, "resonance_type": "强共振（表层 + 逻辑）", '
            '"pov_transform": true, "causal_test": "'
            + _CAUSAL
            + '", "rationale": "institutional vs personal"}'
        )
        score, rtype, rationale, causal, pov = parse_judge_response(text)
        self.assertEqual(score, 2)
        self.assertEqual(rtype, TYPE_STRONG)
        self.assertTrue(pov)
        self.assertIn("institutional", rationale)

    def test_format_judge_block_lines_emits_pov_when_true(self):
        cal = CalibrationReport(
            observation_run_ids=["01-grid-outage"],
            n_pairs=5,
            exact_agreement=1.0,
            within_one_agreement=1.0,
            pearson_r=1.0,
            thresholds={},
            trusted=True,
            trust_status=TRUST_STATUS_TRUSTED,
            screening_only=False,
        )
        lines = format_judge_block_lines(
            JudgeResult(
                run_id="01-grid-outage",
                tmdb_id="42",
                title="Film",
                judge_score=2,
                judge_resonance_type=TYPE_STRONG,
                judge_pov_transform=True,
                causal_test=_CAUSAL,
            ),
            cal,
        )
        self.assertIn("  - **judge POV变换**: 是", lines)

    def test_integrate_judge_includes_pov_transform_line(self):
        review = """## 01-grid-outage

<!-- run_id: 01-grid-outage -->
### Film (2020) [THE-HERO]
- **tmdb_id**: 100
- **共振分**: 2
- **共振类型**: 强共振（表层 + 逻辑）
- **打分备注**: （可选）
"""
        cal = CalibrationReport(
            observation_run_ids=["01-grid-outage"],
            n_pairs=0,
            exact_agreement=None,
            within_one_agreement=None,
            pearson_r=None,
            thresholds={},
            trusted=False,
            trust_status="不采信",
            screening_only=True,
        )
        output = JudgeOutput(
            version=4,
            calibration=cal,
            scores=[
                JudgeResult(
                    run_id="01-grid-outage",
                    tmdb_id="100",
                    title="Film",
                    judge_score=2,
                    judge_resonance_type=TYPE_STRONG,
                    judge_pov_transform=True,
                    causal_test=_CAUSAL,
                    rationale="POV shift unlocks resonance.",
                )
            ],
        )
        merged = integrate_judge_into_review(review, output)
        self.assertIn("- **judge POV变换**: 是", merged)


class HumanPovTransformParseTests(unittest.TestCase):
    def test_parse_eval_markdown_reads_pov_transform(self):
        md = """# Candidates

## 01-grid-outage

### Survival Family (2017) [THE-HERO]
- **tmdb_id**: 429918
- **共振分**: 2
- **共振类型**: 强共振（表层 + 逻辑）
- **POV变换**: 是
- **打分备注**: Gap A sample
"""
        run = parse_eval_markdown(
            Path("output/Eval/phase3.11/01-grid-outage/candidates.md"), md
        )
        self.assertEqual(len(run.candidates), 1)
        cand = run.candidates[0]
        self.assertEqual(cand.score, 2)
        self.assertEqual(cand.resonance_type, TYPE_STRONG)
        self.assertTrue(cand.pov_transform)

    def test_editor_placeholder_includes_pov_transform(self):
        lines: list[str] = []
        append_resonance_editor_lines(lines)
        joined = "\n".join(lines)
        self.assertIn("**POV变换**", joined)


if __name__ == "__main__":
    unittest.main()
