"""Tests for scripts/fix_review_field_separation_phase310.py."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.apply_obs_fresh_labels_phase310 import FreshLabel, _apply_labels_to_review
from scripts.fix_review_field_separation_phase310 import (
    fix_review_field_separation,
    is_llm_generated_remark,
    parse_llm_remark_content,
)
from scripts.llm_judge import CalibrationReport, JudgeOutput, JudgeResult, load_judge_output

_FIXTURES = Path(__file__).resolve().parent / "judge_fixtures"


class RemarkParsingTests(unittest.TestCase):
    def test_is_llm_generated_remark(self):
        self.assertTrue(is_llm_generated_remark("v2 fresh · rationale here"))
        self.assertTrue(is_llm_generated_remark("v2 fresh · x · holdout prescreen"))
        self.assertFalse(is_llm_generated_remark("（可选）"))
        self.assertFalse(is_llm_generated_remark("总编批注"))

    def test_parse_with_causal_test(self):
        body = (
            "v2 fresh · No shared surface. · 反测: "
            "Failures under stress drive emergency action."
        )
        rationale, causal = parse_llm_remark_content(body)
        self.assertIn("No shared surface", rationale)
        self.assertIn("Failures under stress", causal)

    def test_parse_without_causal_test(self):
        body = "v2 fresh · Only rationale, no causal sentence."
        rationale, causal = parse_llm_remark_content(body)
        self.assertIn("Only rationale", rationale)
        self.assertEqual(causal, "")


class ApplyLabelsHumanFlagTests(unittest.TestCase):
    def test_default_does_not_touch_human_fields(self):
        review = (
            "### Title\n"
            "- **tmdb_id**: 1\n"
            "- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->\n"
            "- **共振类型**:   <!-- -->\n"
            "- **打分备注**: （可选）\n"
        )
        labels = {
            ("01-grid-outage", "1"): FreshLabel(
                run_id="01-grid-outage",
                tmdb_id="1",
                title="T",
                score=2,
                resonance_type="强共振（表层 + 逻辑）",
                causal_test="x",
                labeled_at="t",
                rationale="llm rationale",
            )
        }
        section = "## 01-grid-outage\n" + review
        out = _apply_labels_to_review(section, labels, human_fields=False)
        self.assertIn("共振分**:   <!--", out)
        self.assertNotIn("共振分**: 2", out)

    def test_human_flag_writes_scores_not_llm_remark(self):
        review = (
            "### Title\n"
            "- **tmdb_id**: 1\n"
            "- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->\n"
            "- **共振类型**:   <!-- -->\n"
            "- **打分备注**: （可选）\n"
        )
        labels = {
            ("01-grid-outage", "1"): FreshLabel(
                run_id="01-grid-outage",
                tmdb_id="1",
                title="T",
                score=1,
                resonance_type="深层共振（仅逻辑，无表层）",
                causal_test="causal",
                labeled_at="t",
                rationale="llm rationale",
            )
        }
        section = "## 01-grid-outage\n" + review
        out = _apply_labels_to_review(section, labels, human_fields=True)
        self.assertIn("共振分**: 1", out)
        self.assertNotIn("llm rationale", out)


class FixReviewSeparationTests(unittest.TestCase):
    def test_clears_v2_remark_preserves_obs_score(self):
        review = (
            "## 01-grid-outage\n"
            "<!-- run_id: 01-grid-outage -->\n"
            "### Jet Stream (2013)\n"
            "- **tmdb_id**: 210219\n"
            "- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->\n"
            "- **共振类型**: 深层共振（仅逻辑，无表层）  <!-- -->\n"
            "- **打分备注**: v2 fresh · Editor rationale here. · 反测: Causal sentence.\n"
            "- **judge分**: 0\n"
            "- **judge共振类型**: \n"
            "- **judge理由**: Official judge rationale.\n"
        )
        obs_labels = {
            ("01-grid-outage", "210219"): FreshLabel(
                run_id="01-grid-outage",
                tmdb_id="210219",
                title="Jet Stream",
                score=1,
                resonance_type="深层共振（仅逻辑，无表层）",
                causal_test="Causal sentence.",
                labeled_at="t",
                rationale="Editor rationale here.",
            )
        }
        judge_output = JudgeOutput(
            version=3,
            calibration=CalibrationReport(
                observation_run_ids=["01-grid-outage"],
                n_pairs=1,
                exact_agreement=0.0,
                within_one_agreement=0.0,
                pearson_r=0.0,
                thresholds={},
                trusted=False,
                trust_status="不采信",
                screening_only=True,
            ),
            scores=[
                JudgeResult(
                    run_id="01-grid-outage",
                    tmdb_id="210219",
                    title="Jet Stream",
                    judge_score=0,
                    judge_resonance_type=None,
                    rationale="Official judge rationale.",
                    causal_test="",
                    human_score=1,
                    human_resonance_type="深层共振（仅逻辑，无表层）",
                    disagreement=True,
                    trusted=False,
                )
            ],
        )
        fixed, stats = fix_review_field_separation(
            review,
            judge_output=judge_output,
            obs_labels=obs_labels,
            holdout_labels={},
        )
        self.assertEqual(stats.remarks_cleared, 1)
        self.assertEqual(stats.obs_scores_preserved, 1)
        self.assertIn("打分备注**: （可选）", fixed)
        self.assertNotIn("v2 fresh", fixed)
        self.assertIn("共振分**: 1", fixed)
        self.assertIn("judge分**: 0", fixed)
        self.assertIn("Official judge rationale.", fixed)

    def test_roundtrip_fixture_judge_json(self):
        path = _FIXTURES / "roundtrip.json"
        if not path.is_file():
            self.skipTest("roundtrip fixture missing")
        output = load_judge_output(path)
        self.assertIsInstance(output.scores, list)


if __name__ == "__main__":
    unittest.main()
