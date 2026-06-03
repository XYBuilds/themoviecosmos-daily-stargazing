"""Tests for score_eval_candidates high-hit review markdown layout."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from scripts.score_eval_candidates import (
    _format_high_hit_review,
    _is_multi_agent_hit,
    process_eval_dir,
)

_FIXTURES = Path(__file__).resolve().parent / "eval_fixtures" / "score_eval_review"
_MINI_BATCH = _FIXTURES / "mini-batch"
_MANIFEST = _FIXTURES / "batch-manifest.json"


class MultiAgentBucketTests(unittest.TestCase):
    def test_quality_candidate_forces_multi(self):
        self.assertTrue(_is_multi_agent_hit(quality_candidate=True, agents=["A1"]))

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


if __name__ == "__main__":
    unittest.main()
