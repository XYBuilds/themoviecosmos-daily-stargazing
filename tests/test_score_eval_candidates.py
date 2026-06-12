"""Tests for score_eval_candidates high-hit review markdown layout."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from scripts.eval_editor_fields import SCORING_REMARK_PLACEHOLDER
from scripts.score_eval_candidates import (
    HitScore,
    RetrieveDiagnostics,
    _eligible_for_scoring_pool,
    _format_high_hit_review,
    _inject_retrieve_diagnostics,
    _is_multi_agent_hit,
    _is_pure_neutral_candidate,
    process_eval_dir,
    score_candidates_md,
)

_FIXTURES = Path(__file__).resolve().parent / "eval_fixtures" / "score_eval_review"
_MINI_BATCH = _FIXTURES / "mini-batch"
_MANIFEST = _FIXTURES / "batch-manifest.json"


class RetrieveDiagnosticsInjectionTests(unittest.TestCase):
    def test_inject_neutral_channel_fields_after_tmdb_id(self):
        block = """### Film (2020) [A2]
- **tmdb_id**: 42
- **相似度**: 0.5100
"""
        diag = RetrieveDiagnostics(
            quality_candidate=True,
            neutral_hits=6,
            neutral_total=12,
            neutral_hit_rate=0.5,
            distinct_agents=2,
        )
        patched = _inject_retrieve_diagnostics(block, diag)
        self.assertIn("- **neutral_hit_rate**: 0.5000", patched)
        self.assertIn("- **distinct_agents**: 2", patched)
        self.assertLess(patched.index("tmdb_id"), patched.index("neutral_hit_rate"))

    def test_score_candidates_md_writes_diagnostics_from_retrieve(self):
        text = """# candidates

### Film (2020) [A2]
- **tmdb_id**: 99
- **相似度**: 0.50
"""
        hits = {}
        diag = {
            99: RetrieveDiagnostics(
                quality_candidate=False,
                neutral_hits=3,
                neutral_total=12,
                neutral_hit_rate=0.25,
                distinct_agents=0,
            )
        }
        out, _ = score_candidates_md(
            text,
            "run-x",
            hits,
            diagnostics_by_tmdb=diag,
            min_total_score=999,
        )
        self.assertIn("- **neutral_hits**: 3", out)


class PureNeutralPoolTests(unittest.TestCase):
    def test_pure_neutral_is_diagnostic_only_below_min_score(self):
        diag = RetrieveDiagnostics(
            quality_candidate=False,
            neutral_hits=3,
            neutral_total=12,
            neutral_hit_rate=0.25,
            distinct_agents=0,
        )
        self.assertTrue(_is_pure_neutral_candidate(diag))
        self.assertFalse(_eligible_for_scoring_pool(1, min_total_score=5, diag=diag))

    def test_neutral_hits_do_not_contribute_to_high_hit_score(self):
        text = """# candidates

### Neutral Heavy Film (2020) [A2, A4]
- **tmdb_id**: 123
- **相似度**: 0.50
- **命中视角/碎片**:
  - A2/n1: fragments=[a, b, c, d, e] · sim=0.50
  - A4/p1: fragments=[x] · sim=0.49
- **共振分**: 
- **共振类型**: 
- **打分备注**: 
"""
        hits = {
            123: [
                HitScore(
                    agent_id="A2",
                    pseudo_id="n1",
                    fragments=["a", "b", "c", "d", "e"],
                    similarity=0.50,
                    score=5,
                    channel_role="neutral",
                ),
                HitScore(
                    agent_id="A4",
                    pseudo_id="p1",
                    fragments=["x"],
                    similarity=0.49,
                    score=1,
                    channel_role="toned",
                ),
            ]
        }
        out, high = score_candidates_md(text, "run-x", hits, min_total_score=5)
        self.assertIn("- **pseudo命中分合计**: 1", out)
        self.assertEqual(high, [])

    def test_neutral_only_run_not_included_by_n1_alone(self):
        neutral_batch = _FIXTURES / "neutral-only-batch"
        _reviews, high, missing, scanned = process_eval_dir(
            neutral_batch,
            write_candidates=False,
            min_total_score=5,
        )
        self.assertEqual(scanned, 1)
        self.assertEqual(missing, [])
        self.assertEqual(high, [])


class MultiAgentBucketTests(unittest.TestCase):
    def test_quality_candidate_is_annotation_not_multi(self):
        self.assertFalse(_is_multi_agent_hit(quality_candidate=True, agents=["A1"]))

    def test_two_agents_without_quality_flag(self):
        self.assertTrue(_is_multi_agent_hit(quality_candidate=False, agents=["A4", "A7"]))

    def test_single_agent(self):
        self.assertFalse(_is_multi_agent_hit(quality_candidate=False, agents=["A7"]))


class HighHitReviewFormatTests(unittest.TestCase):
    def setUp(self) -> None:
        self.run_reviews, self.all_high, self.missing, self.runs_scanned = process_eval_dir(
            _MINI_BATCH,
            write_candidates=False,
            min_total_score=5,
            manifest_path=_MANIFEST,
        )
        self.review = _format_high_hit_review(
            self.run_reviews,
            runs_scanned=self.runs_scanned,
            min_score=5,
        )

    def test_processes_both_runs(self):
        self.assertEqual(self.runs_scanned, 2)
        self.assertEqual(self.missing, [])
        self.assertEqual(len(self.run_reviews), 2)

    def test_news_sections_follow_manifest_order(self):
        alpha_pos = self.review.index("## 01-alpha")
        beta_pos = self.review.index("## 02-beta")
        self.assertLess(alpha_pos, beta_pos)

    def test_reality_at_top_of_each_section(self):
        alpha_block = self.review.split("## 01-alpha", 1)[1].split("## 02-beta", 1)[0]
        self.assertIn("Alpha grid test headline", alpha_block)
        self.assertLess(
            alpha_block.index("Alpha grid test headline"),
            alpha_block.index("### 多 agents 命中"),
        )
        beta_block = self.review.split("## 02-beta", 1)[1]
        self.assertIn("Beta layoff test headline", beta_block)
        self.assertLess(
            beta_block.index("Beta layoff test headline"),
            beta_block.index("### 多 agents 命中"),
        )

    def test_alpha_multi_single_split_and_sort(self):
        alpha = next(r for r in self.run_reviews if r.run_id == "01-alpha")
        self.assertEqual([c.tmdb_id for c in alpha.multi_agent], [100])
        self.assertEqual([c.tmdb_id for c in alpha.single_agent], [200])
        self.assertEqual(alpha.multi_agent[0].total_score, 8)
        self.assertEqual(alpha.single_agent[0].total_score, 6)

    def test_beta_two_agents_in_multi_bucket(self):
        beta = next(r for r in self.run_reviews if r.run_id == "02-beta")
        self.assertEqual(len(beta.multi_agent), 1)
        self.assertEqual(beta.multi_agent[0].tmdb_id, 300)
        self.assertEqual(beta.multi_agent[0].total_score, 9)
        self.assertEqual(beta.single_agent, [])

    def test_subsection_order_within_news(self):
        alpha_block = self.review.split("## 01-alpha", 1)[1].split("## 02-beta", 1)[0]
        multi_pos = alpha_block.index("### 多 agents 命中")
        single_pos = alpha_block.index("### 单 agent 命中")
        self.assertLess(multi_pos, single_pos)

    def test_markdown_lists_multi_before_single_candidates(self):
        alpha_block = self.review.split("## 01-alpha", 1)[1].split("## 02-beta", 1)[0]
        multi_pos = alpha_block.index("### Multi Hit Film")
        single_pos = alpha_block.index("### Single Hit Film")
        self.assertLess(multi_pos, single_pos)

    def test_scores_descending_within_subsection(self):
        alpha_block = self.review.split("## 01-alpha", 1)[1].split("## 02-beta", 1)[0]
        multi_block = alpha_block.split("### 多 agents 命中", 1)[1].split("### 单 agent 命中", 1)[0]
        multi_scores = [
            int(m.group(1))
            for m in re.finditer(r"<!-- pseudo命中分合计: (\d+) -->", multi_block)
        ]
        self.assertEqual(multi_scores, sorted(multi_scores, reverse=True))

    def test_scoring_remark_after_resonance_type_in_review(self):
        self.assertIn(f"- **打分备注**: {SCORING_REMARK_PLACEHOLDER}", self.review)
        type_positions = [
            m.start() for m in re.finditer(r"^- \*\*共振类型\*\*:", self.review, re.MULTILINE)
        ]
        remark_positions = [
            m.start() for m in re.finditer(r"^- \*\*打分备注\*\*:", self.review, re.MULTILINE)
        ]
        self.assertGreater(len(type_positions), 0)
        self.assertEqual(len(type_positions), len(remark_positions))
        for t_pos, r_pos in zip(type_positions, remark_positions, strict=True):
            self.assertLess(t_pos, r_pos)


if __name__ == "__main__":
    unittest.main()
