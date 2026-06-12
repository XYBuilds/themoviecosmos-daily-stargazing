"""Unit tests for Phase 3.6.3 run_eval candidate display (headings, quality, sort)."""

from __future__ import annotations

import unittest

from scripts.run_eval import (
    _candidate_heading,
    _format_candidate_block,
    _format_candidates_markdown,
    _pseudo_hit_total,
    _sort_candidates_for_display,
)
from scripts.score_eval_candidates import _agents_from_heading, _title_from_heading


class CandidateHeadingTests(unittest.TestCase):
    def test_heading_lists_all_hit_agents_including_a1(self) -> None:
        cand = {
            "title": "Shared Movie",
            "release_year": 2020,
            "quality_candidate": True,
            "hit_sources": [
                {"agent_id": "A2", "pseudo_id": "p1", "fragments": ["f1"]},
                {"agent_id": "A1", "pseudo_id": "p1", "fragments": ["f2"]},
            ],
        }
        heading = _candidate_heading(cand)
        self.assertIn("[A2, A1]", heading)
        self.assertIn("[汇聚标注]", heading)
        self.assertNotIn("baseline only", heading)

    def test_single_agent_heading_no_quality_tag(self) -> None:
        cand = {
            "title": "Solo",
            "quality_candidate": False,
            "also_baseline": True,
            "hit_sources": [{"agent_id": "A1", "pseudo_id": "p1", "fragments": []}],
        }
        heading = _candidate_heading(cand)
        self.assertIn("[A1]", heading)
        self.assertNotIn("汇聚标注", heading)
        self.assertNotIn("baseline only", heading)

    def test_format_block_includes_auto_score_section(self) -> None:
        cand = {
            "title": "X",
            "tmdb_id": 42,
            "quality_candidate": True,
            "quality_reason": "objective_match=1 + persona_semantic_match=1",
            "convergence_persona_count": 2,
            "convergent_score": 123.456,
            "match_diagnostics": {
                "surface_match": True,
                "event_match": False,
                "persona_semantic_match": True,
                "search_unit_kinds": ["surface-fragment-bundle", "persona-semantic"],
                "center_dimensions": ["how"],
            },
            "similarity": 0.9,
            "genres": "drama",
            "language": "en",
            "overview": "test",
            "movie_url": "http://x",
            "also_baseline": False,
            "hit_sources": [
                {
                    "agent_id": "A2",
                    "pseudo_id": "su-surface-1",
                    "fragments": ["who-0"],
                    "search_unit_kind": "surface-fragment-bundle",
                },
                {
                    "agent_id": "A2",
                    "pseudo_id": "su-persona-A2-p1",
                    "fragments": ["how-2"],
                    "search_unit_kind": "persona-semantic",
                    "center_element": "how-2",
                },
            ],
        }
        text = "\n".join(_format_candidate_block(cand, include_score=False))
        self.assertIn("- **自动打分**:", text)
        self.assertIn("  - **quality_candidate**: true", text)
        self.assertIn("  - **objective_match**: true (surface=true, event=false)", text)
        self.assertIn("  - **source_hits**: surface=1 / event=0 / persona=1", text)
        self.assertIn("  - **baseline_overlap**: false", text)
        self.assertNotIn("quality_candidate_annotation", text)
        self.assertNotIn("also_baseline", text)


class CandidateSortTests(unittest.TestCase):
    def test_annotation_does_not_rank_before_pseudo_hit_total(self) -> None:
        candidates = [
            {
                "tmdb_id": 1,
                "quality_candidate": False,
                "similarity": 0.99,
                "hit_sources": [{"fragments": ["a", "b", "c", "d", "e"]}],
            },
            {
                "tmdb_id": 2,
                "quality_candidate": True,
                "similarity": 0.50,
                "hit_sources": [{"fragments": ["a"]}],
            },
            {
                "tmdb_id": 3,
                "quality_candidate": True,
                "similarity": 0.40,
                "hit_sources": [{"fragments": ["a", "b", "c"]}],
            },
        ]
        ordered = _sort_candidates_for_display(candidates)
        self.assertEqual([c["tmdb_id"] for c in ordered], [1, 3, 2])

    def test_pseudo_hit_total_sums_fragments(self) -> None:
        cand = {
            "hit_sources": [
                {"fragments": ["f1", "f2"]},
                {"fragments": ["f3"]},
            ]
        }
        self.assertEqual(_pseudo_hit_total(cand), 3)


class CandidatesMarkdownTests(unittest.TestCase):
    def test_markdown_order_matches_sort(self) -> None:
        md = _format_candidates_markdown(
            "test-run",
            [
                {
                    "title": "High Hit Non Annotation",
                    "tmdb_id": 1,
                    "quality_candidate": False,
                    "distinct_agents": 1,
                    "similarity": 0.99,
                    "genres": "",
                    "language": "en",
                    "overview": "",
                    "movie_url": "",
                    "also_baseline": False,
                    "hit_sources": [
                        {"agent_id": "A2", "pseudo_id": "p1", "fragments": ["a", "b", "c"]}
                    ],
                },
                {
                    "title": "Quality Multi",
                    "release_year": 2019,
                    "tmdb_id": 2,
                    "quality_candidate": True,
                    "distinct_agents": 2,
                    "similarity": 0.60,
                    "genres": "",
                    "language": "en",
                    "overview": "",
                    "movie_url": "",
                    "also_baseline": True,
                    "hit_sources": [
                        {"agent_id": "A2", "pseudo_id": "p1", "fragments": ["a"]},
                        {"agent_id": "A1", "pseudo_id": "p1", "fragments": ["b"]},
                    ],
                },
            ],
        )
        high_hit_pos = md.find("High Hit Non Annotation")
        annotation_pos = md.find("Quality Multi")
        self.assertLess(high_hit_pos, annotation_pos)
        self.assertIn("[A2, A1] [汇聚标注]", md)


class ScoreEvalHeadingParseTests(unittest.TestCase):
    def test_agents_from_new_heading_skips_quality_bracket(self) -> None:
        heading = "Movie (2020) [A1, A2, A4] [汇聚标注]"
        self.assertEqual(_agents_from_heading(heading), ["A1", "A2", "A4"])

    def test_title_strips_agent_and_quality_brackets(self) -> None:
        heading = "Movie (2020) [A1, A2] [汇聚标注]"
        self.assertEqual(_title_from_heading(heading), "Movie")


if __name__ == "__main__":
    unittest.main()
