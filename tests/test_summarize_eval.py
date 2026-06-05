"""Tests for summarize_eval resonance-type parsing and gate compare modes."""

from __future__ import annotations

import unittest
from pathlib import Path

from scripts.summarize_eval import (
    _format_stdout,
    parse_eval_markdown,
    summarize_runs,
)

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
        self.assertEqual(report["gate"]["compare_mode"], "multi_vs_single")
        self.assertAlmostEqual(g["single_2_rate"], 0.2)
        self.assertAlmostEqual(g["multi_2_rate"], 1.0)
        self.assertAlmostEqual(g["single_structural_2_rate"], 0.0)
        self.assertAlmostEqual(g["multi_structural_2_rate"], 0.0)
        self.assertEqual(report["gate"]["verdict"], "GATE_PASS")
        stdout = _format_stdout(report)
        self.assertIn("Gate line 2 compare: multi_vs_single", stdout)
        self.assertIn("(fallback: no 共振类型)", stdout)

    def test_multi_vs_single_pass_structural_rates(self):
        run = _load_run("multi-vs-single-pass/candidates.md")
        report = summarize_runs([run])
        g = report["global"]
        self.assertTrue(g["resonance_types_filled"])
        self.assertEqual(report["gate"]["compare_mode"], "multi_vs_single")
        self.assertAlmostEqual(g["single_2_rate"], 0.5)
        self.assertAlmostEqual(g["single_structural_2_rate"], 0.0)
        self.assertAlmostEqual(g["multi_2_rate"], 1.0)
        self.assertAlmostEqual(g["multi_structural_2_rate"], 1.0)
        self.assertEqual(g["multi_structural_twos"], 2)
        self.assertEqual(report["gate"]["verdict"], "GATE_PASS")
        stdout = _format_stdout(report)
        self.assertIn("Gate line 2 compare: multi_vs_single", stdout)
        self.assertIn("(共振类型 present)", stdout)

    def test_multi_vs_single_fail_when_single_structural_beats_multi(self):
        run = _load_run("multi-vs-single-fail/candidates.md")
        report = summarize_runs([run])
        g = report["global"]
        self.assertTrue(g["resonance_types_filled"])
        self.assertAlmostEqual(g["single_structural_2_rate"], 1.0)
        self.assertAlmostEqual(g["multi_structural_2_rate"], 0.0)
        self.assertAlmostEqual(g["single_2_rate"], 1.0)
        self.assertAlmostEqual(g["multi_2_rate"], 1.0)
        self.assertEqual(report["gate"]["verdict"], "GATE_FAIL")
        self.assertEqual(report["gate"]["compare_mode"], "multi_vs_single")

    def test_quality_candidate_field_overrides_heading_agent_count(self):
        text = """# fixture

## 候选星轨（共 2 部）

### One Agent Marked Quality (2020) [A1]
- **tmdb_id**: 800001
- **quality_candidate**: true
- **共振分**: 2
- **共振类型**: 结构

### Two Agents Not Quality (2019) [A2, A4]
- **tmdb_id**: 800002
- **quality_candidate**: false
- **共振分**: 2
- **共振类型**: 双重
"""
        run = parse_eval_markdown(Path("fixture.md"), text)
        report = summarize_runs([run])
        g = report["global"]
        self.assertEqual(g["multi_scored"], 1)
        self.assertEqual(g["single_scored"], 1)
        self.assertEqual(g["multi_structural_twos"], 1)
        self.assertEqual(g["single_structural_twos"], 1)

    def test_persona_vs_baseline_pass_structural_rates(self):
        run = _load_run("persona-vs-baseline-pass/candidates.md")
        report = summarize_runs([run])
        g = report["global"]
        self.assertTrue(g["persona_gate"])
        self.assertEqual(report["gate"]["compare_mode"], "persona_vs_baseline")
        self.assertAlmostEqual(g["baseline_structural_2_rate"], 1 / 3)
        self.assertAlmostEqual(g["persona_touched_structural_2_rate"], 1.0)
        self.assertEqual(g["a1_path_scored"], 3)
        self.assertEqual(g["persona_path_scored"], 1)
        self.assertEqual(report["gate"]["verdict"], "GATE_PASS")
        stdout = _format_stdout(report)
        self.assertIn("Gate line 2 compare: persona_vs_baseline", stdout)
        self.assertIn("fit×sim ranking", stdout)

    def test_persona_vs_baseline_fail_when_baseline_beats_persona(self):
        run = _load_run("persona-vs-baseline-fail/candidates.md")
        report = summarize_runs([run])
        g = report["global"]
        self.assertTrue(g["persona_gate"])
        self.assertAlmostEqual(g["baseline_structural_2_rate"], 1.0)
        self.assertAlmostEqual(g["persona_touched_structural_2_rate"], 0.0)
        self.assertEqual(report["gate"]["verdict"], "GATE_FAIL")
        self.assertEqual(report["gate"]["compare_mode"], "persona_vs_baseline")


class SummarizeEvalPhase38DiagnosticTests(unittest.TestCase):
    def test_phase38_dual_diagnostic_pass_gate2(self):
        run = _load_run("phase38-dual-diagnostic-pass/candidates.md")
        report = summarize_runs([run])
        g = report["global"]
        self.assertTrue(g["phase38_gate"])
        self.assertFalse(g["persona_gate"])
        self.assertEqual(report["gate"]["compare_mode"], "quality_vs_neutral_only")
        d1 = g["diagnostic_1_neutral_hit_rate"]
        d2 = g["diagnostic_2_toned_convergence"]
        self.assertEqual(d1["n"], 4)
        self.assertIsNotNone(d1["partial_corr_neutral_hit_rate_vs_score_given_similarity"])
        self.assertGreater(d1["partial_corr_neutral_hit_rate_vs_score_given_similarity"], 0)
        self.assertAlmostEqual(d2["quality_structural_2_rate"], 1.0)
        self.assertAlmostEqual(d2["neutral_only_structural_2_rate"], 0.0)
        self.assertTrue(d2["precision_lift_ok"])
        self.assertEqual(report["gate"]["verdict"], "GATE_PASS")
        self.assertEqual(report["a1_superset"]["status"], "pending")
        stdout = _format_stdout(report)
        self.assertIn("Diagnostic ①", stdout)
        self.assertIn("Diagnostic ②", stdout)
        self.assertIn("A1-superset check: pending", stdout)
        self.assertIn("Gate line 2 compare: quality_vs_neutral_only", stdout)

    def test_phase38_dual_diagnostic_fail_when_neutral_beats_quality(self):
        run = _load_run("phase38-dual-diagnostic-fail/candidates.md")
        report = summarize_runs([run])
        g = report["global"]
        d2 = g["diagnostic_2_toned_convergence"]
        self.assertAlmostEqual(d2["neutral_only_structural_2_rate"], 1.0)
        self.assertAlmostEqual(d2["quality_structural_2_rate"], 0.0)
        self.assertFalse(d2["precision_lift_ok"])
        self.assertEqual(report["gate"]["verdict"], "GATE_FAIL")
        self.assertIn("diagnostic ②", report["gate"]["reasons"][0].lower())

    def test_similarity_bins_present_in_diagnostic_1(self):
        run = _load_run("phase38-dual-diagnostic-pass/candidates.md")
        report = summarize_runs([run])
        bins = report["global"]["diagnostic_1_neutral_hit_rate"]["similarity_bins"]
        self.assertIn("mid", bins)
        self.assertIn("high", bins)


if __name__ == "__main__":
    unittest.main()
