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


if __name__ == "__main__":
    unittest.main()
