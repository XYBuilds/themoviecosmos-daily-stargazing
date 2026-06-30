from __future__ import annotations

import unittest
from unittest.mock import patch

from scripts.compose import (
    JudgeEntry,
    format_judge_kernel,
    format_selected_movie_block,
    render_c2_prompt,
    run_publish,
)


_CANDIDATE = {
    "tmdb_id": 157336,
    "title": "Interstellar",
    "overview": "A team travels through a wormhole.",
    "genres": "Adventure, Drama, Science Fiction",
    "release_year": 2014,
    "movie_url": "https://themoviecosmos.com/movie/157336",
}

_DETAIL = {
    "id": 157336,
    "title": "Interstellar",
    "overview": "A team travels through a wormhole.",
    "genres": "Adventure, Drama, Science Fiction",
    "release_date": "2014-11-05",
    "runtime": 169,
    "director": "Christopher Nolan",
    "vote_average": 8.5,
    "vote_count": 37000,
    "popularity": 154.2,
    "imdb_rating": 8.7,
    "imdb_votes": 2300000,
}


class ComposePublishTests(unittest.TestCase):
    def test_selected_movie_block_exposes_real_numbers(self) -> None:
        with patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL):
            block = format_selected_movie_block(_CANDIDATE)

        self.assertIn("vote_average: 8.5", block)
        self.assertIn("vote_count: 37000", block)
        self.assertIn("popularity: 154.2", block)
        self.assertIn("director: Christopher Nolan", block)
        self.assertIn("https://themoviecosmos.com/movie/157336", block)

    def test_judge_kernel_uses_upstream_judge_fields(self) -> None:
        kernel = format_judge_kernel(JudgeEntry(2, "same engine", "X drives Y", "strong"))
        self.assertIn("resonance_type: strong", kernel)
        self.assertIn("causal_test: X drives Y", kernel)
        self.assertIn("rationale: same engine", kernel)

    def test_publish_prompt_is_single_draft_not_platform_variants(self) -> None:
        prompt = render_c2_prompt(
            "{{news_context}}\n{{selected_movie}}\n{{judge_kernel}}",
            "News",
            "Movie",
            "Judge",
        )
        self.assertEqual(prompt, "News\nMovie\nJudge")

    def test_run_publish_feeds_db_and_judge_to_llm(self) -> None:
        captured: dict[str, str] = {}

        def fake_llm(prompt: str) -> str:
            captured["prompt"] = prompt
            return "这是一段正文。"

        with patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL):
            draft = run_publish(
                _CANDIDATE,
                {"title": "News", "description": "Summary"},
                judge=JudgeEntry(2, "same engine", "X drives Y", "strong"),
                llm_call=fake_llm,
            )

        self.assertIn("vote_average: 8.5", captured["prompt"])
        self.assertIn("causal_test: X drives Y", captured["prompt"])
        # C2 产物契约：只保留电影 id + 正文，不含骨架（片名/年份/链接）。
        self.assertEqual(draft["tmdb_id"], 157336)
        self.assertEqual(draft["body"], "这是一段正文。")
        self.assertNotIn("《Interstellar》", draft["body"])
        self.assertNotIn("https://themoviecosmos.com/movie/", draft["body"])
        self.assertNotIn("#", draft["body"])

    def test_run_publish_strips_llm_emitted_skeleton(self) -> None:
        # LLM 误吐标题行/链接时，正文清洗应剥除，只留纯正文。
        def fake_llm(prompt: str) -> str:
            return (
                "《Interstellar》(2014)\n这是正文。\n\n"
                "https://themoviecosmos.com/movie/157336"
            )

        with patch("scripts.compose.get_movie_detail_by_tmdb_id", return_value=_DETAIL):
            draft = run_publish(
                _CANDIDATE,
                {"title": "News", "description": "Summary"},
                judge=JudgeEntry(2, "same engine", "X drives Y", "strong"),
                llm_call=fake_llm,
            )

        self.assertEqual(draft["tmdb_id"], 157336)
        self.assertEqual(draft["body"], "这是正文。")
        self.assertNotIn("《Interstellar》(2014)", draft["body"])
        self.assertNotIn("https://themoviecosmos.com/movie/157336", draft["body"])


if __name__ == "__main__":
    unittest.main()