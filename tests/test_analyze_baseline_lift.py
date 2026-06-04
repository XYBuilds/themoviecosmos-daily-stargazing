"""Tests for analyze_baseline_lift bucketing and lift verdict."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.analyze_baseline_lift import (
    _classify_bucket,
    _go_no_go,
    analyze_eval_dir,
    analyze_runs,
    format_markdown,
)
from scripts.summarize_eval import parse_eval_markdown

_FIXTURES = Path(__file__).resolve().parent / "eval_fixtures" / "baseline_lift"


class ClassifyBucketTests(unittest.TestCase):
    def test_baseline_only(self):
        self.assertEqual(
            _classify_bucket(also_baseline=True, agents=["A1"]),
            "baseline-only",
        )

    def test_creative_only(self):
        self.assertEqual(
            _classify_bucket(also_baseline=False, agents=["A4"]),
            "creative-only",
        )

    def test_both(self):
        self.assertEqual(
            _classify_bucket(also_baseline=True, agents=["A2", "A1"]),
            "both",
        )


class BaselineLiftFixtureTests(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture_dir = _FIXTURES

    def test_mini_fixture_rates_and_go(self):
        report = analyze_eval_dir(self.fixture_dir)
        baseline = report.buckets["baseline-only"]
        creative = report.buckets["creative-only"]
        both = report.buckets["both"]

        self.assertEqual(baseline.scored, 2)
        self.assertEqual(baseline.twos, 1)
        self.assertAlmostEqual(baseline.two_rate, 0.5)

        self.assertEqual(creative.scored, 2)
        self.assertEqual(creative.twos, 1)
        self.assertAlmostEqual(creative.two_rate, 0.5)

        self.assertEqual(both.scored, 1)
        self.assertEqual(both.twos, 1)

        verdict, _, lift_pure, _ = _go_no_go(report)
        self.assertEqual(lift_pure, 0.0)
        # Tie at 50% → No-Go (lift ≈ 0)
        self.assertEqual(verdict, "No-Go")

        md = format_markdown(report)
        self.assertIn("Go/No-Go", md)
        self.assertIn("baseline-only", md)


class BaselineLiftGoTests(unittest.TestCase):
    def test_creative_beats_baseline(self):
        text = """# 候选星轨 · 01-test

## 元信息
- run_id: 01-test

## 候选星轨（共 2 部）

### Baseline Hit (2020) [A1]
- **tmdb_id**: 1
- **also_baseline**: true
- **共振分**: 0

### Creative Hit (2020) [A4]
- **tmdb_id**: 2
- **also_baseline**: false
- **共振分**: 2
"""
        run = parse_eval_markdown(Path("candidates.md"), text)
        report = analyze_runs([run])
        verdict, _, lift_pure, _ = _go_no_go(report)
        self.assertEqual(lift_pure, 1.0)
        self.assertEqual(verdict, "Go")


if __name__ == "__main__":
    unittest.main()
