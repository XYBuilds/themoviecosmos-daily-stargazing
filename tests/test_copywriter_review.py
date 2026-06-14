"""Offline tests for copywriter --stage review (C1).

Covers candidate assembly, news-context build, persona-semantic selection (never
A1/oracle), OPEN-a soft hints passthrough, judge backfill, multi-paragraph parsing
with title/year and positional fallback, and missing-paragraph error recording.
The LLM call is injected, so no network or API key is needed.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.copywriter import (
    build_news_context,
    format_candidates_block,
    load_judge_scores,
    map_paragraphs_to_candidates,
    representative_persona_semantic,
    result_to_payload,
    run_review,
    split_into_paragraphs,
)


def _candidate(tmdb_id, title, year, triggered, dims, overview="An overview."):
    return {
        "tmdb_id": tmdb_id,
        "title": title,
        "overview": overview,
        "release_year": year,
        "movie_url": f"https://themoviecosmos.com/movie/{tmdb_id}",
        "triggered_by": triggered,
        "match_diagnostics": {
            "center_dimensions": dims,
            "search_unit_kinds": ["persona-semantic"],
        },
    }


def _retrieve(candidates, per_agent=None, news=None):
    payload = {"candidates": candidates}
    if per_agent is not None:
        payload["per_agent"] = per_agent
    if news is not None:
        payload["news"] = news
    return payload


class TestPersonaSemantic(unittest.TestCase):
    def test_picks_highest_similarity_persona_semantic(self) -> None:
        per_agent = [
            {
                "agent_id": "THE-INNOCENT",
                "pseudos": [
                    {
                        "pseudo": "surface bundle text",
                        "source": {"search_unit_kind": "surface-fragment-bundle"},
                        "hits": [{"similarity": 0.9}],
                    },
                    {
                        "pseudo": "low semantic",
                        "source": {"search_unit_kind": "persona-semantic"},
                        "hits": [{"similarity": 0.4}],
                    },
                ],
            },
            {
                "agent_id": "THE-SAGE",
                "pseudos": [
                    {
                        "pseudo": "high semantic",
                        "source": {"search_unit_kind": "persona-semantic"},
                        "hits": [{"similarity": 0.8}],
                    }
                ],
            },
        ]
        text = representative_persona_semantic(_retrieve([], per_agent))
        self.assertEqual(text, "high semantic")

    def test_ignores_non_persona_semantic(self) -> None:
        per_agent = [
            {
                "agent_id": "A1",
                "pseudos": [
                    {
                        "pseudo": "surface only",
                        "source": {"search_unit_kind": "surface-fragment-bundle"},
                        "hits": [{"similarity": 0.99}],
                    }
                ],
            }
        ]
        self.assertEqual(representative_persona_semantic(_retrieve([], per_agent)), "")


class TestCandidateBlock(unittest.TestCase):
    def test_block_has_soft_hints_and_no_hashtag(self) -> None:
        cands = [_candidate(111, "Survival Family", 2017, ["THE-INNOCENT"], ["how", "result"])]
        block = format_candidates_block(cands)
        self.assertIn("《Survival Family》(2017)", block)
        self.assertIn("被这些视角击中: THE-INNOCENT", block)
        self.assertIn("切面（可选参考，非强制聚焦）: 过程、结果", block)
        self.assertIn("https://themoviecosmos.com/movie/111", block)
        self.assertNotIn("#", block)

    def test_missing_year_renders_dash(self) -> None:
        cands = [_candidate(222, "No Year", None, [], [])]
        block = format_candidates_block(cands)
        self.assertIn("《No Year》(—)", block)


class TestNewsContext(unittest.TestCase):
    def test_includes_title_description_and_semantic(self) -> None:
        ctx = build_news_context(
            {"title": "T", "description": "D"}, "rep semantic fragment"
        )
        self.assertIn("标题: T", ctx)
        self.assertIn("摘要: D", ctx)
        self.assertIn("persona-semantic", ctx)


class TestParsing(unittest.TestCase):
    def test_split_paragraphs_by_title_leader(self) -> None:
        raw = "《甲》(2001)\n第一段。\n\n《乙》(1999)\n第二段。"
        blocks = split_into_paragraphs(raw)
        self.assertEqual(len(blocks), 2)
        self.assertEqual(blocks[0][0], "甲")
        self.assertEqual(blocks[0][1], 2001)
        self.assertIn("第一段", blocks[0][2])

    def test_title_match_mapping(self) -> None:
        cands = [
            _candidate(1, "Alpha", 2001, ["THE-HERO"], ["who"]),
            _candidate(2, "Beta", 1999, ["THE-SAGE"], ["why"]),
        ]
        blocks = [("Beta", 1999, "《Beta》(1999)\nB"), ("Alpha", 2001, "《Alpha》(2001)\nA")]
        pairs, errors = map_paragraphs_to_candidates(blocks, cands)
        self.assertEqual(errors, [])
        self.assertEqual(pairs[0][0]["tmdb_id"], 1)
        self.assertIn("A", pairs[0][1])
        self.assertIn("B", pairs[1][1])

    def test_positional_fallback_when_titles_differ(self) -> None:
        cands = [
            _candidate(1, "Alpha", 2001, [], []),
            _candidate(2, "Beta", 1999, [], []),
        ]
        # LLM translated titles, no title match possible, equal counts.
        blocks = [("甲", 2001, "《甲》(2001)\nA-zh"), ("乙", 1999, "《乙》(1999)\nB-zh")]
        pairs, errors = map_paragraphs_to_candidates(blocks, cands)
        self.assertEqual(errors, [])
        self.assertIn("A-zh", pairs[0][1])
        self.assertIn("B-zh", pairs[1][1])

    def test_missing_paragraph_recorded_as_error(self) -> None:
        cands = [
            _candidate(1, "Alpha", 2001, [], []),
            _candidate(2, "Beta", 1999, [], []),
            _candidate(3, "Gamma", 2010, [], []),
        ]
        # Only two blocks for three candidates, counts differ → no positional fallback.
        blocks = [
            ("Alpha", 2001, "《Alpha》(2001)\nA"),
            ("Beta", 1999, "《Beta》(1999)\nB"),
        ]
        pairs, errors = map_paragraphs_to_candidates(blocks, cands)
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0]["tmdb_id"], 3)


class TestJudgeBackfill(unittest.TestCase):
    def test_load_judge_scores_indexes_by_run_and_tmdb(self) -> None:
        import json
        import tempfile

        data = {
            "scores": [
                {"run_id": "01-grid-outage", "tmdb_id": "429918", "judge_score": 2},
                {"run_id": "01-grid-outage", "tmdb_id": "33495", "judge_score": 1},
            ]
        }
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        ) as fh:
            json.dump(data, fh)
            path = Path(fh.name)
        index = load_judge_scores(path)
        self.assertEqual(index[("01-grid-outage", "429918")], 2)
        path.unlink()

    def test_missing_file_returns_empty(self) -> None:
        self.assertEqual(load_judge_scores(Path("does-not-exist.json")), {})


class TestRunReview(unittest.TestCase):
    def _prompts_dir(self) -> Path:
        return _REPO / "prompts"

    def test_n_candidates_yield_n_copies(self) -> None:
        cands = [
            _candidate(1, "Alpha", 2001, ["THE-HERO"], ["who"]),
            _candidate(2, "Beta", 1999, ["THE-SAGE"], ["why"]),
        ]
        fake_output = "《Alpha》(2001)\n甲文案。\n\n《Beta》(1999)\n乙文案。"
        result = run_review(
            _retrieve(cands, news={"title": "T", "description": "D"}),
            {"title": "T", "description": "D"},
            judge_index={("", "1"): 2},
            prompts_dir=self._prompts_dir(),
            llm_call=lambda _prompt: fake_output,
        )
        self.assertEqual(len(result.review_copies), 2)
        self.assertEqual(result.errors, [])
        first = result.review_copies[0]
        self.assertEqual(first.tmdb_id, 1)
        self.assertEqual(first.judge_score, 2)
        self.assertEqual(first.triggered_by, ["THE-HERO"])
        self.assertEqual(first.center_dimensions, ["who"])
        self.assertIn("甲文案", first.text_zh)

    def test_empty_candidates_returns_empty(self) -> None:
        result = run_review(
            _retrieve([]),
            {"title": "", "description": ""},
            prompts_dir=self._prompts_dir(),
            llm_call=lambda _p: "",
        )
        self.assertEqual(result.review_copies, [])
        self.assertEqual(result.errors, [])

    def test_llm_error_recorded_not_raised(self) -> None:
        def boom(_prompt):
            raise RuntimeError("api down")

        result = run_review(
            _retrieve([_candidate(1, "Alpha", 2001, [], [])]),
            {"title": "T", "description": "D"},
            prompts_dir=self._prompts_dir(),
            llm_call=boom,
        )
        self.assertEqual(result.review_copies, [])
        self.assertEqual(result.errors[0]["type"], "llm_error")

    def test_payload_shape(self) -> None:
        cands = [_candidate(1, "Alpha", 2001, ["THE-HERO"], ["who"])]
        result = run_review(
            _retrieve(cands),
            {"title": "T", "description": "D"},
            prompts_dir=self._prompts_dir(),
            llm_call=lambda _p: "《Alpha》(2001)\n文案。",
        )
        payload = result_to_payload(result)
        self.assertIn("review_copies", payload)
        self.assertIn("errors", payload)
        row = payload["review_copies"][0]
        for key in (
            "tmdb_id",
            "title",
            "year",
            "triggered_by",
            "center_dimensions",
            "judge_score",
            "movie_url",
            "text_zh",
        ):
            self.assertIn(key, row)


if __name__ == "__main__":
    unittest.main()