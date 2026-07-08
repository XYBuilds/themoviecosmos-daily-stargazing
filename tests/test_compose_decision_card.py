from __future__ import annotations

import unittest
from unittest.mock import patch

from scripts.compose import (
    JudgeEntry,
    build_news_context,
    format_candidates_block,
    result_to_markdown,
    run_review,
)


def _retrieve() -> dict:
    return {
        "candidates": [
            {
                "tmdb_id": 157336,
                "title": "Interstellar",
                "overview": "A team travels through a wormhole.",
                "genres": "Adventure, Drama, Science Fiction",
                "release_year": 2014,
                "triggered_by": ["THE-HERO"],
                "movie_url": "https://themoviecosmos.com/movie/157336",
                "match_diagnostics": {"center_dimensions": ["why", "result"]},
            }
        ],
        "per_agent": [],
    }


_DETAIL = {
    "id": 157336,
    "title": "Interstellar",
    "overview": "A team travels through a wormhole.",
    "genres": "Adventure, Drama, Science Fiction",
    "release_date": "2014-11-05",
    "runtime": 169,
    "director": "Christopher Nolan",
    "production_countries": "United States of America, United Kingdom",
    "vote_average": 8.5,
    "vote_count": 37000,
    "popularity": 154.2,
    "imdb_rating": 8.7,
    "imdb_votes": 2300000,
}


class ComposeDecisionCardTests(unittest.TestCase):
    def test_prompt_candidate_block_uses_db_projection_and_judge_kernel(self) -> None:
        judge = {("run", "157336"): JudgeEntry(2, "same engine", "X drives Y", "strong")}
        with patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL):
            block = format_candidates_block(_retrieve()["candidates"], judge, "run")

        self.assertIn("DB 投影", block)
        self.assertIn("director: Christopher Nolan", block)
        self.assertIn("vote_average: 8.5", block)
        # ADR-0015 D6：production_countries 进投影白名单，C1 决策卡也带该列（无害透传）。
        self.assertIn("production_countries: United States of America, United Kingdom", block)
        self.assertIn("causal_test_en: X drives Y", block)
        self.assertNotIn("Hashtag", block)
        self.assertNotIn("文案", block)

    def test_review_output_is_non_creative_decision_card(self) -> None:
        judge = {("run", "157336"): JudgeEntry(2, "same engine", "X drives Y", "strong")}
        llm = lambda _prompt: """《Interstellar》(2014)
judge_score: 2
resonance_type: strong
causal_test_en: X drives Y
causal_test_zh: X 驱动 Y
rationale_en: same engine
rationale_zh: 相同的机制
"""
        news = {"title": "News", "description": "Summary", "url": "https://example.com/news"}
        with patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL):
            result = run_review(_retrieve(), news, judge_index=judge, run_id="run", llm_call=llm)
            markdown = result_to_markdown(result, news=news, run_id="run")

        self.assertEqual(len(result.review_copies), 1)
        payload = result.review_copies[0]
        self.assertEqual(payload.db_projection["director"], "Christopher Nolan")
        self.assertEqual(payload.judge_causal_test_zh, "X 驱动 Y")
        self.assertEqual(payload.news_url, "https://example.com/news")
        self.assertNotIn("Hashtag", markdown)
        self.assertNotIn("文案", markdown)
        self.assertNotIn("标题:", markdown)

    def test_news_context_includes_source_url(self) -> None:
        context = build_news_context(
            {"title": "T", "description": "D", "url": "https://example.com/src"}, ""
        )
        self.assertIn("原文链接: https://example.com/src", context)


if __name__ == "__main__":
    unittest.main()