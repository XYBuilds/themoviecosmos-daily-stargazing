"""Tests for scripts/judge_prescreen.py (Phase 3.10.4)."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.judge_prescreen import (
    BUCKET_DOWNGRADE,
    BUCKET_HIGHLIGHT,
    BUCKET_MANUAL,
    DEFAULT_MIN_JUDGE_SCORE,
    PrescreenConfig,
    classify_prescreen_bucket,
    compute_threshold_safety,
    integrate_prescreen_into_review,
    item_passes_threshold,
    load_prescreen_report,
    run_prescreen,
    sample_rejection_audit_keys,
    write_prescreen_json,
    write_threshold_safety_report,
)
from scripts.llm_judge import (
    CalibrationReport,
    JudgeOutput,
    JudgeResult,
    TRUST_STATUS_TRUSTED,
)


def _result(
    run_id: str,
    tmdb_id: str,
    judge_score: int,
    human_score: int | None = None,
) -> JudgeResult:
    return JudgeResult(
        run_id=run_id,
        tmdb_id=tmdb_id,
        title=f"Film {tmdb_id}",
        judge_score=judge_score,
        judge_resonance_type=None,
        human_score=human_score,
    )


def _minimal_output(scores: list[JudgeResult]) -> JudgeOutput:
    return JudgeOutput(
        version=3,
        calibration=CalibrationReport(
            observation_run_ids=["01-grid-outage"],
            n_pairs=0,
            exact_agreement=None,
            within_one_agreement=None,
            pearson_r=None,
            thresholds={},
            trusted=True,
            trust_status=TRUST_STATUS_TRUSTED,
            screening_only=False,
        ),
        scores=scores,
    )


class BucketingTests(unittest.TestCase):
    def test_classify_buckets(self):
        self.assertEqual(classify_prescreen_bucket(0), BUCKET_DOWNGRADE)
        self.assertEqual(classify_prescreen_bucket(1), BUCKET_MANUAL)
        self.assertEqual(classify_prescreen_bucket(2), BUCKET_HIGHLIGHT)

    def test_threshold_pass_default_ge_one(self):
        self.assertFalse(item_passes_threshold(0, DEFAULT_MIN_JUDGE_SCORE))
        self.assertTrue(item_passes_threshold(1, DEFAULT_MIN_JUDGE_SCORE))
        self.assertTrue(item_passes_threshold(2, DEFAULT_MIN_JUDGE_SCORE))

    def test_run_prescreen_assigns_all_items(self):
        scores = [
            _result("01-grid-outage", "1", 0, 0),
            _result("01-grid-outage", "2", 1, 1),
            _result("01-grid-outage", "3", 2, 2),
        ]
        report = run_prescreen(_minimal_output(scores))
        self.assertEqual(len(report.items), 3)
        buckets = {i.tmdb_id: i.bucket for i in report.items}
        self.assertEqual(buckets["1"], BUCKET_DOWNGRADE)
        self.assertEqual(buckets["2"], BUCKET_MANUAL)
        self.assertEqual(buckets["3"], BUCKET_HIGHLIGHT)
        self.assertTrue(report.items[2].highlight)
        self.assertFalse(report.items[0].manual_review)


class SamplingTests(unittest.TestCase):
    def test_sample_reproducible(self):
        keys = [(f"run", str(i)) for i in range(20)]
        a = sample_rejection_audit_keys(keys, 0.25, seed=99)
        b = sample_rejection_audit_keys(keys, 0.25, seed=99)
        self.assertEqual(a, b)

    def test_sample_differs_with_seed(self):
        keys = [(f"run", str(i)) for i in range(50)]
        a = sample_rejection_audit_keys(keys, 0.20, seed=1)
        b = sample_rejection_audit_keys(keys, 0.20, seed=2)
        self.assertNotEqual(a, b)

    def test_sample_at_least_one_when_pile_non_empty(self):
        keys = [("r", "1")]
        sampled = sample_rejection_audit_keys(keys, 0.05, seed=7)
        self.assertEqual(len(sampled), 1)

    def test_per_run_audit_recorded(self):
        scores = [
            _result("01-grid-outage", "a", 0),
            _result("01-grid-outage", "b", 0),
            _result("02-corporate-layoff", "c", 0),
        ]
        report = run_prescreen(
            _minimal_output(scores),
            PrescreenConfig(rejection_sample_rate=1.0, random_seed=1),
        )
        self.assertEqual(len(report.rejection_audits), 2)
        for audit in report.rejection_audits:
            self.assertEqual(audit.sample_size, audit.rejection_count)


class ThresholdSafetyTests(unittest.TestCase):
    def test_zero_human_two_killed_on_phase39_data_pattern(self):
        """Simulate 3.9 fact: no human=2 with judge=0 at threshold≥1."""
        scores = [
            _result("01", "1", 0, 0),
            _result("01", "2", 1, 2),
            _result("01", "3", 2, 2),
            _result("01", "4", 1, 1),
        ]
        safety = compute_threshold_safety(scores, PrescreenConfig())
        self.assertTrue(safety.zero_human_two_killed)
        self.assertEqual(safety.n_human_two_killed, 0)
        self.assertEqual(safety.n_human_two_on_pass_side, 2)

    def test_detects_killed_human_two(self):
        scores = [
            _result("01", "1", 0, 2),
            _result("01", "2", 2, 2),
        ]
        safety = compute_threshold_safety(scores, PrescreenConfig(min_judge_score=1))
        self.assertFalse(safety.zero_human_two_killed)
        self.assertEqual(safety.n_human_two_killed, 1)
        self.assertEqual(len(safety.killed_items), 1)

    def test_threshold_two_stricter(self):
        scores = [_result("01", "1", 1, 2)]
        safety = compute_threshold_safety(scores, PrescreenConfig(min_judge_score=2))
        self.assertFalse(safety.zero_human_two_killed)

    def test_human_two_on_pass_side_assertion(self):
        scores = [
            _result("01", "1", 1, 2),
            _result("01", "2", 2, 2),
        ]
        report = run_prescreen(_minimal_output(scores))
        for item in report.items:
            if item.human_score == 2:
                self.assertTrue(item.passes_threshold)
                self.assertGreaterEqual(item.judge_score, DEFAULT_MIN_JUDGE_SCORE)

    def test_rejection_audit_flags_human_two_hit(self):
        scores = [_result("01-grid-outage", "99", 0, 2)]
        report = run_prescreen(
            _minimal_output(scores),
            PrescreenConfig(rejection_sample_rate=1.0),
        )
        self.assertEqual(len(report.rejection_audits[0].audit_hits), 1)
        self.assertFalse(report.threshold_safety.zero_human_two_killed)


class OutputRoundtripTests(unittest.TestCase):
    def test_json_roundtrip_and_safety_report(self):
        scores = [
            _result("01-grid-outage", "1", 0, 0),
            _result("01-grid-outage", "2", 2, 2),
        ]
        report = run_prescreen(_minimal_output(scores))
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out_json = root / "judge-prescreen.json"
            safety_md = root / "threshold-safety-report.md"
            write_prescreen_json(out_json, report)
            write_threshold_safety_report(safety_md, report)
            loaded = load_prescreen_report(out_json)
            self.assertEqual(len(loaded.items), 2)
            self.assertTrue(loaded.threshold_safety.zero_human_two_killed)
            text = safety_md.read_text(encoding="utf-8")
            self.assertIn("zero_human_two_killed", text)
            self.assertIn("SAFE TO FREEZE", text)
            roundtrip = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertEqual(roundtrip["version"], 1)
            self.assertIn("rejection_audits", roundtrip)


if __name__ == "__main__":
    unittest.main()
