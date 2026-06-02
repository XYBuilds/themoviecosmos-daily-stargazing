"""Tests for summarize_eval resonance-type parsing and gate compare modes."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.summarize_eval import parse_eval_markdown, summarize_runs

_FIXTURES = Path(__file__).resolve().parent / "eval_fixtures"


def _load_run(rel_path: str):
    path = _FIXTURES / rel_path
    return parse_eval_markdown(path, path.read_text(encoding="utf-8"))


class SummarizeEvalResonanceTypeTests(unittest.TestCase):
    def test_legacy_fixtures_fallback_to_total_2_rate(self):
        runs = [
            _load_run("run-alpha.md"),
            _load_run("run-beta.md"),
            _load_run("run-gamma.md"),
        ]
        report = summarize_runs(runs)
        g = report["global"]
        self.assertFalse(g["resonance_types_filled"])
        self.assertEqual(report["gate"]["compare_mode"], "total_2_rate")
        self.assertAlmostEqual(g["baseline_2_rate"], 0.0)
        self.assertAlmostEqual(g["creative_2_rate"], 0.5)
        self.assertAlmostEqual(g["baseline_structural_2_rate"], 0.0)
        self.assertAlmostEqual(g["creative_structural_2_rate"], 0.0)
        self.assertEqual(report["gate"]["verdict"], "GATE_PASS")

    def test_structural_fixture_rates_match_hand_calc(self):
        run = _load_run("resonance-structural/candidates.md")
        report = summarize_runs([run])
        g = report["global"]
        self.assertTrue(g["resonance_types_filled"])
        self.assertEqual(report["gate"]["compare_mode"], "structural_2_rate")
        self.assertAlmostEqual(g["baseline_2_rate"], 1.0)
        self.assertAlmostEqual(g["baseline_structural_2_rate"], 0.0)
        self.assertEqual(g["baseline_structural_twos"], 0)
        self.assertAlmostEqual(g["creative_2_rate"], 1.0)
        self.assertAlmostEqual(g["creative_structural_2_rate"], 1.0)
        self.assertEqual(g["creative_structural_twos"], 2)
        self.assertEqual(report["gate"]["verdict"], "GATE_PASS")

    def test_structural_gate_fails_when_only_surface_twos(self):
        run = _load_run("resonance-mixed/candidates.md")
        report = summarize_runs([run])
        g = report["global"]
        self.assertTrue(g["resonance_types_filled"])
        self.assertAlmostEqual(g["baseline_structural_2_rate"], 1.0)
        self.assertAlmostEqual(g["creative_structural_2_rate"], 0.0)
        self.assertAlmostEqual(g["baseline_2_rate"], 1.0)
        self.assertAlmostEqual(g["creative_2_rate"], 1.0)
        self.assertEqual(report["gate"]["verdict"], "GATE_FAIL")
        self.assertEqual(report["gate"]["compare_mode"], "structural_2_rate")


if __name__ == "__main__":
    unittest.main()
