"""Tests for scripts/llm_judge.py (Phase 3.9.4)."""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from scripts.llm_judge import (
    DEFAULT_MIN_EXACT_AGREEMENT,
    DEFAULT_MIN_PEARSON,
    TRUST_STATUS_TRUSTED,
    TRUST_STATUS_UNTRUSTED,
    _JUDGE_RUBRIC,
    _JUDGE_SYSTEM,
    JudgeItem,
    JudgeOutput,
    JudgeResult,
    CalibrationReport,
    compute_calibration,
    integrate_judge_into_review,
    load_judge_output,
    parse_judge_response,
    score_items,
    validate_judge_payload,
    write_judge_markdown,
)
from scripts.resonance_rubric import TYPE_DEEP, TYPE_STRONG, TYPE_SURFACE

_FIXTURES = Path(__file__).resolve().parent / "judge_fixtures"


_CAUSAL = "scarcity under grid failure drives families into survival mode"


class JudgeSchemaTests(unittest.TestCase):
    def test_dual_axis_rubric_wording_from_authority_source(self):
        self.assertIn("表层元素 (surface element)", _JUDGE_RUBRIC)
        self.assertIn("底层逻辑 (underlying logic)", _JUDGE_RUBRIC)
        self.assertIn("invariant under change of POV or scale", _JUDGE_RUBRIC)
        self.assertIn("causal counter-test", _JUDGE_RUBRIC)
        self.assertNotIn("骨架同构", _JUDGE_RUBRIC)
        self.assertIn("falsifiable causal counter-test", _JUDGE_SYSTEM.lower())

    def test_validate_score_zero_no_type(self):
        score, rtype, causal = validate_judge_payload(
            {
                "score": 0,
                "resonance_type": None,
                "causal_test": "",
                "rationale": "none",
            }
        )
        self.assertEqual(score, 0)
        self.assertIsNone(rtype)
        self.assertEqual(causal, "")

    def test_validate_score_two_strong(self):
        score, rtype, causal = validate_judge_payload(
            {
                "score": 2,
                "resonance_type": TYPE_STRONG,
                "causal_test": _CAUSAL,
                "rationale": "both axes",
            }
        )
        self.assertEqual(score, 2)
        self.assertEqual(rtype, TYPE_STRONG)
        self.assertEqual(causal, _CAUSAL)

    def test_validate_accepts_legacy_dual_alias(self):
        score, rtype, causal = validate_judge_payload(
            {
                "score": 2,
                "resonance_type": "双重",
                "causal_test": _CAUSAL,
                "rationale": "legacy",
            }
        )
        self.assertEqual(score, 2)
        self.assertEqual(rtype, TYPE_STRONG)

    def test_validate_score_one_deep_logic_requires_causal_test(self):
        score, rtype, causal = validate_judge_payload(
            {
                "score": 1,
                "resonance_type": TYPE_DEEP,
                "causal_test": _CAUSAL,
                "rationale": "logic only",
            }
        )
        self.assertEqual(score, 1)
        self.assertEqual(rtype, TYPE_DEEP)
        self.assertEqual(causal, _CAUSAL)

    def test_validate_rejects_missing_causal_test_field(self):
        with self.assertRaises(ValueError):
            validate_judge_payload(
                {"score": 0, "resonance_type": None, "rationale": "x"}
            )

    def test_validate_rejects_score_two_without_causal_test(self):
        with self.assertRaises(ValueError):
            validate_judge_payload(
                {
                    "score": 2,
                    "resonance_type": TYPE_STRONG,
                    "causal_test": "",
                    "rationale": "x",
                }
            )

    def test_validate_rejects_deep_logic_without_causal_test(self):
        with self.assertRaises(ValueError):
            validate_judge_payload(
                {
                    "score": 1,
                    "resonance_type": TYPE_DEEP,
                    "causal_test": "",
                    "rationale": "x",
                }
            )

    def test_validate_surface_only_allows_empty_causal_test(self):
        score, rtype, causal = validate_judge_payload(
            {
                "score": 1,
                "resonance_type": TYPE_SURFACE,
                "causal_test": "",
                "rationale": "surface only",
            }
        )
        self.assertEqual(score, 1)
        self.assertEqual(rtype, TYPE_SURFACE)
        self.assertEqual(causal, "")

    def test_validate_rejects_score_one_wrong_type(self):
        with self.assertRaises(ValueError):
            validate_judge_payload(
                {
                    "score": 1,
                    "resonance_type": TYPE_STRONG,
                    "causal_test": "",
                    "rationale": "x",
                }
            )

    def test_parse_judge_response_json_fence(self):
        text = (
            f'```json\n{{"score": 1, "resonance_type": "{TYPE_SURFACE}", '
            f'"causal_test": "", "rationale": "x"}}\n```'
        )
        score, rtype, rationale, causal = parse_judge_response(text)
        self.assertEqual(score, 1)
        self.assertEqual(rtype, TYPE_SURFACE)
        self.assertEqual(rationale, "x")
        self.assertEqual(causal, "")

    def test_score_type_matrix_consistency_new_constants(self):
        for score, rtype, causal in (
            (0, None, ""),
            (1, TYPE_DEEP, _CAUSAL),
            (1, TYPE_SURFACE, ""),
            (2, TYPE_STRONG, _CAUSAL),
        ):
            got_score, got_type, got_causal = validate_judge_payload(
                {
                    "score": score,
                    "resonance_type": rtype,
                    "causal_test": causal,
                    "rationale": "ok",
                }
            )
            self.assertEqual((got_score, got_type, got_causal), (score, rtype, causal))

    def test_output_schema_roundtrip(self):
        cal = compute_calibration(
            [(2, 2), (1, 1), (0, 0), (2, 1), (1, 1)],
            observation_run_ids=["01-grid-outage"],
        )
        output = JudgeOutput(
            version=1,
            calibration=cal,
            scores=[],
        )
        payload = output.to_dict()
        self.assertEqual(payload["version"], 1)
        self.assertIn("trust_status", payload["calibration"])
        self.assertIn("screening_only", payload["calibration"])


class CalibrationTests(unittest.TestCase):
    def test_perfect_alignment_trusted(self):
        pairs = [(0, 0), (1, 1), (2, 2), (2, 2), (1, 1)]
        report = compute_calibration(
            pairs,
            observation_run_ids=["01-grid-outage", "02-corporate-layoff"],
            min_pairs=5,
        )
        self.assertTrue(report.trusted)
        self.assertEqual(report.trust_status, TRUST_STATUS_TRUSTED)
        self.assertFalse(report.screening_only)
        self.assertEqual(report.exact_agreement, 1.0)
        self.assertAlmostEqual(report.pearson_r or 0.0, 1.0)

    def test_low_agreement_downgrades_to_untrusted(self):
        pairs = [(0, 2), (2, 0), (1, 2), (2, 1), (0, 1)]
        report = compute_calibration(
            pairs,
            observation_run_ids=["01-grid-outage"],
            min_exact_agreement=DEFAULT_MIN_EXACT_AGREEMENT,
            min_pearson=DEFAULT_MIN_PEARSON,
            min_pairs=5,
        )
        self.assertFalse(report.trusted)
        self.assertEqual(report.trust_status, TRUST_STATUS_UNTRUSTED)
        self.assertTrue(report.screening_only)

    def test_insufficient_pairs_untrusted(self):
        report = compute_calibration(
            [(2, 2), (1, 0)],
            observation_run_ids=["01-grid-outage"],
            min_pairs=5,
        )
        self.assertFalse(report.trusted)
        self.assertEqual(report.n_pairs, 2)
        self.assertIsNone(report.exact_agreement)


class ScoreItemsTests(unittest.TestCase):
    def _mock_judge(
        self,
        mapping: dict[tuple[str, str], tuple[int, str | None, str, str]],
    ):
        def _fn(item: JudgeItem) -> tuple[int, str | None, str, str]:
            return mapping[(item.run_id, item.tmdb_id)]

        return _fn

    def test_score_items_marks_disagreement_and_untrusted(self):
        items = [
            JudgeItem(
                run_id="01-grid-outage",
                tmdb_id="100",
                title="Film A (2020)",
                news_title="News",
                news_summary="Summary",
                movie_overview="Overview A",
                human_score=2,
            ),
            JudgeItem(
                run_id="01-grid-outage",
                tmdb_id="200",
                title="Film B (2020)",
                news_title="News",
                news_summary="Summary",
                movie_overview="Overview B",
                human_score=0,
            ),
            JudgeItem(
                run_id="02-corporate-layoff",
                tmdb_id="300",
                title="Film C (2020)",
                news_title="News",
                news_summary="Summary",
                movie_overview="Overview C",
                human_score=1,
            ),
            JudgeItem(
                run_id="02-corporate-layoff",
                tmdb_id="400",
                title="Film D (2020)",
                news_title="News",
                news_summary="Summary",
                movie_overview="Overview D",
                human_score=2,
            ),
            JudgeItem(
                run_id="02-corporate-layoff",
                tmdb_id="500",
                title="Film E (2020)",
                news_title="News",
                news_summary="Summary",
                movie_overview="Overview E",
                human_score=1,
            ),
        ]
        judge_fn = self._mock_judge(
            {
                ("01-grid-outage", "100"): (0, None, "disagree", ""),
                ("01-grid-outage", "200"): (2, TYPE_STRONG, "disagree", _CAUSAL),
                ("02-corporate-layoff", "300"): (2, TYPE_STRONG, "off", _CAUSAL),
                ("02-corporate-layoff", "400"): (0, None, "off", ""),
                ("02-corporate-layoff", "500"): (1, TYPE_SURFACE, "ok", ""),
            }
        )
        output = score_items(
            items,
            judge_fn,
            observation_run_ids=["01-grid-outage", "02-corporate-layoff"],
            min_pairs=5,
        )
        self.assertFalse(output.calibration.trusted)
        self.assertEqual(output.calibration.trust_status, TRUST_STATUS_UNTRUSTED)
        disagreements = [s for s in output.scores if s.disagreement]
        self.assertGreaterEqual(len(disagreements), 3)
        for row in output.scores:
            self.assertFalse(row.trusted)

    def test_fixture_review_calibration_trusted(self):
        fixture_dir = _FIXTURES / "obs_calibration"
        review = fixture_dir / "high-hit-score-review.md"
        items = [
            JudgeItem(
                run_id="01-grid-outage",
                tmdb_id="429918",
                title="Survival Family (2017)",
                news_title="Blackout",
                news_summary="Grid stress",
                movie_overview="Electrical outage.",
                human_score=2,
            ),
            JudgeItem(
                run_id="01-grid-outage",
                tmdb_id="274855",
                title="Geostorm (2017)",
                news_title="Blackout",
                news_summary="Grid stress",
                movie_overview="Weather control fails.",
                human_score=1,
            ),
            JudgeItem(
                run_id="02-corporate-layoff",
                tmdb_id="100001",
                title="Layoff Drama (2019)",
                news_title="Layoffs",
                news_summary="Cuts",
                movie_overview="Corporate restructuring.",
                human_score=0,
            ),
            JudgeItem(
                run_id="02-corporate-layoff",
                tmdb_id="100002",
                title="Office Exodus (2018)",
                news_title="Layoffs",
                news_summary="Cuts",
                movie_overview="Mass firing.",
                human_score=2,
            ),
            JudgeItem(
                run_id="03-election-upset",
                tmdb_id="100003",
                title="Primary Shock (2020)",
                news_title="Election",
                news_summary="Upset",
                movie_overview="Political upset.",
                human_score=1,
            ),
        ]
        judge_fn = self._mock_judge(
            {
                ("01-grid-outage", "429918"): (2, TYPE_STRONG, "strong", _CAUSAL),
                ("01-grid-outage", "274855"): (1, TYPE_SURFACE, "surface", ""),
                ("02-corporate-layoff", "100001"): (0, None, "none", ""),
                ("02-corporate-layoff", "100002"): (1, TYPE_DEEP, "logic", _CAUSAL),
                ("03-election-upset", "100003"): (1, TYPE_SURFACE, "surface", ""),
            }
        )
        output = score_items(
            items,
            judge_fn,
            observation_run_ids=["01-grid-outage", "02-corporate-layoff", "03-election-upset"],
            min_pairs=5,
        )
        self.assertTrue(output.calibration.trusted)
        self.assertEqual(output.calibration.trust_status, TRUST_STATUS_TRUSTED)
        md_path = fixture_dir / "out.md"
        write_judge_markdown(md_path, output)
        self.assertIn("采信", md_path.read_text(encoding="utf-8"))
        json_path = fixture_dir / "out.json"
        json_path.write_text(
            json.dumps(output.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        loaded = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(loaded["calibration"]["trust_status"], TRUST_STATUS_TRUSTED)


class IntegrateReviewTests(unittest.TestCase):
    def test_integrate_judge_fields_after_editor_lines(self):
        review = """# Review

## Criteria

- **Editor fields:** placeholders

## 01-grid-outage

<!-- run_id: 01-grid-outage -->
### Survival Family (2017) [THE-HERO]
- **tmdb_id**: 429918
- **共振分**: 2
- **共振类型**: 双重
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
### Geostorm (2017) [THE-HERO]
- **tmdb_id**: 274855
- **共振分**: 1
- **共振类型**: 结构
- **打分备注**: （可选）
"""
        cal = compute_calibration([], observation_run_ids=["01-grid-outage"])
        output = JudgeOutput(
            version=1,
            calibration=cal,
            scores=[
                JudgeResult(
                    run_id="01-grid-outage",
                    tmdb_id="429918",
                    title="Survival Family (2017)",
                    judge_score=1,
                    judge_resonance_type=TYPE_SURFACE,
                    rationale="Surface anchor only; logic differs.",
                    causal_test="",
                    human_score=2,
                    human_resonance_type=TYPE_STRONG,
                    disagreement=True,
                    trusted=False,
                ),
                JudgeResult(
                    run_id="01-grid-outage",
                    tmdb_id="274855",
                    title="Geostorm (2017)",
                    judge_score=0,
                    judge_resonance_type=None,
                    rationale="No load-bearing surface anchor.",
                    causal_test="",
                    human_score=1,
                    human_resonance_type=TYPE_DEEP,
                    disagreement=True,
                    trusted=False,
                ),
            ],
        )
        merged = integrate_judge_into_review(review, output)
        self.assertIn("- **LLM judge:**", merged)
        self.assertIn("screening only", merged)
        self.assertIn("- **judge分**: 1", merged)
        self.assertIn(f"- **judge共振类型**: {TYPE_SURFACE}", merged)
        self.assertIn("- **judge分歧**: ⚠", merged)
        self.assertIn("- **judge采信**: 不采信 · screening only", merged)
        self.assertIn(
            "- **judge理由**: Surface anchor only; logic differs.", merged
        )
        self.assertIn("- **共振分**: 2", merged)
        survival_block = merged.split("Survival Family", 1)[1].split("Geostorm", 1)[0]
        self.assertLess(survival_block.index("共振分"), survival_block.index("judge分"))
        self.assertLess(survival_block.index("打分备注"), survival_block.index("judge分"))
        self.assertLess(survival_block.index("judge采信"), survival_block.index("judge理由"))

    def test_integrate_idempotent_replaces_prior_judge_lines(self):
        review = """## 01-grid-outage

<!-- run_id: 01-grid-outage -->
### Film (2020) [A1]
- **tmdb_id**: 100
- **共振分**: 1
- **共振类型**: 表层
- **打分备注**: （可选）
- **judge分**: 9
- **judge共振类型**: old
- **judge理由**: stale rationale
"""
        cal = CalibrationReport(
            observation_run_ids=["01-grid-outage"],
            n_pairs=0,
            exact_agreement=None,
            within_one_agreement=None,
            pearson_r=None,
            thresholds={},
            trusted=False,
            trust_status=TRUST_STATUS_UNTRUSTED,
            screening_only=True,
        )
        output = JudgeOutput(
            version=1,
            calibration=cal,
            scores=[
                JudgeResult(
                    run_id="01-grid-outage",
                    tmdb_id="100",
                    title="Film",
                    judge_score=2,
                    judge_resonance_type=TYPE_STRONG,
                    rationale="Updated rationale.",
                    causal_test=_CAUSAL,
                    trusted=False,
                )
            ],
        )
        merged = integrate_judge_into_review(review, output)
        self.assertNotIn("judge分**: 9", merged)
        self.assertNotIn("stale rationale", merged)
        self.assertIn("- **judge分**: 2", merged)
        self.assertIn(f"- **judge共振类型**: {TYPE_STRONG}", merged)
        self.assertIn("- **judge理由**: Updated rationale.", merged)

    def test_load_judge_output_roundtrip(self):
        cal = compute_calibration(
            [(2, 2), (1, 1), (0, 0), (2, 1), (1, 1)],
            observation_run_ids=["01-grid-outage"],
        )
        output = JudgeOutput(
            version=1,
            calibration=cal,
            scores=[
                JudgeResult(
                    run_id="01-grid-outage",
                    tmdb_id="42",
                    title="Film",
                    judge_score=2,
                    judge_resonance_type=TYPE_STRONG,
                    causal_test=_CAUSAL,
                    trusted=cal.trusted,
                )
            ],
        )
        path = _FIXTURES / "roundtrip.json"
        path.write_text(
            json.dumps(output.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        loaded = load_judge_output(path)
        self.assertEqual(loaded.scores[0].judge_score, 2)
        self.assertEqual(loaded.calibration.trust_status, cal.trust_status)


if __name__ == "__main__":
    unittest.main()
