"""Unit tests for Phase 6.3 scripts/main.py publish subcommand."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts.main import (
    build_copy_markdown,
    find_candidate_by_tmdb_id,
    load_news_context_for_publish,
    main,
)


def _write_briefing(dir_path: Path, date: str) -> None:
    md = (
        f"# 每日星轨观测 · {date}\n\n"
        f"# 现实波澜 · {date}\n\n"
        "## 元信息\n"
        "- date: 2026-07-04\n"
        "- news_url: https://example.com/article/1\n"
        f"- run_id: {date}\n\n"
        "## 现实波澜\n"
        "- **title**: Test headline\n"
        "- **source** / **pub_time**: Example Wire / 2026-07-04T00:00:00Z\n"
        "- **summary**: Test description.\n\n"
        "# 候选星轨\n"
    )
    (dir_path / f"{date}.md").write_text(md, encoding="utf-8")


def _write_candidates(dir_path: Path, date: str, tmdb_id: int = 429918) -> None:
    payload = {
        "candidates": [
            {
                "tmdb_id": tmdb_id,
                "title": "Survival Family",
                "overview": "An overview.",
                "genres": "Comedy, Drama",
                "release_year": 2017,
                "movie_url": f"https://themoviecosmos.com/movie/{tmdb_id}",
            }
        ],
        "human_candidates": [],
        "meta": {},
    }
    (dir_path / f"{date}_candidates.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


class LoadNewsContextTests(unittest.TestCase):
    def test_parses_title_summary_url_from_briefing_md(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _write_briefing(tmp_path, "2026-07-04")
            news = load_news_context_for_publish("2026-07-04", out_dir=tmp_path)
            self.assertEqual(news["title"], "Test headline")
            self.assertEqual(news["description"], "Test description.")
            self.assertEqual(news["url"], "https://example.com/article/1")

    def test_missing_briefing_raises_value_error(self) -> None:
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                load_news_context_for_publish("2099-01-01", out_dir=Path(tmp))


class FindCandidateByTmdbIdTests(unittest.TestCase):
    def test_finds_matching_candidate(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _write_candidates(tmp_path, "2026-07-04", tmdb_id=429918)
            cand = find_candidate_by_tmdb_id("2026-07-04", 429918, out_dir=tmp_path)
            self.assertEqual(cand["title"], "Survival Family")

    def test_unmatched_tmdb_id_raises_with_clear_message(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _write_candidates(tmp_path, "2026-07-04", tmdb_id=429918)
            with self.assertRaises(ValueError) as ctx:
                find_candidate_by_tmdb_id("2026-07-04", 999999, out_dir=tmp_path)
            self.assertIn("999999", str(ctx.exception))
            self.assertIn("429918", str(ctx.exception))

    def test_missing_candidates_file_raises_value_error(self) -> None:
        with TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                find_candidate_by_tmdb_id("2099-01-01", 1, out_dir=Path(tmp))


class BuildCopyMarkdownTests(unittest.TestCase):
    def test_contains_chinese_body_news_source_and_links(self) -> None:
        candidate = {
            "title": "Survival Family",
            "release_year": 2017,
            "movie_url": "https://themoviecosmos.com/movie/429918",
        }
        news = {
            "title": "Test headline",
            "description": "Test description.",
            "url": "https://example.com/article/1",
        }
        draft = {"tmdb_id": 429918, "body": "这是中文正文。"}
        md = build_copy_markdown("2026-07-04", candidate, news, draft)
        self.assertIn("这是中文正文。", md)
        self.assertIn("Test headline", md)
        self.assertIn("Test description.", md)
        self.assertIn("https://themoviecosmos.com/movie/429918", md)
        self.assertIn("https://example.com/article/1", md)
        self.assertIn("《Survival Family》(2017)", md)


class MainPublishCliTests(unittest.TestCase):
    def test_publish_success_path_writes_copy_md(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _write_briefing(tmp_path, "2026-07-04")
            _write_candidates(tmp_path, "2026-07-04", tmdb_id=429918)

            def fake_run_publish(candidate, news, *, provider=None):
                return {"tmdb_id": candidate["tmdb_id"], "body": "这是中文正文。"}

            with (
                patch("scripts.main.resolve_briefing_path", side_effect=lambda date, out_dir=None: tmp_path / f"{date}.md"),
                patch("scripts.main.resolve_candidates_path", side_effect=lambda date, out_dir=None: tmp_path / f"{date}_candidates.json"),
                patch("scripts.main.resolve_copy_path", side_effect=lambda date, out_dir=None: tmp_path / f"{date}_copy.md"),
                patch("scripts.compose.run_publish", side_effect=fake_run_publish),
            ):
                code = main(["publish", "--date", "2026-07-04", "--tmdb-id", "429918"])

            self.assertEqual(code, 0)
            copy_path = tmp_path / "2026-07-04_copy.md"
            self.assertTrue(copy_path.is_file())
            content = copy_path.read_text(encoding="utf-8")
            self.assertIn("这是中文正文。", content)

    def test_publish_unmatched_tmdb_id_exits_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _write_briefing(tmp_path, "2026-07-04")
            _write_candidates(tmp_path, "2026-07-04", tmdb_id=429918)

            with (
                patch("scripts.main.resolve_briefing_path", side_effect=lambda date, out_dir=None: tmp_path / f"{date}.md"),
                patch("scripts.main.resolve_candidates_path", side_effect=lambda date, out_dir=None: tmp_path / f"{date}_candidates.json"),
            ):
                code = main(["publish", "--date", "2026-07-04", "--tmdb-id", "999999"])

            self.assertNotEqual(code, 0)

    def test_publish_missing_candidates_file_exits_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _write_briefing(tmp_path, "2026-07-04")
            # No candidates.json written.

            with (
                patch("scripts.main.resolve_briefing_path", side_effect=lambda date, out_dir=None: tmp_path / f"{date}.md"),
                patch("scripts.main.resolve_candidates_path", side_effect=lambda date, out_dir=None: tmp_path / f"{date}_candidates.json"),
            ):
                code = main(["publish", "--date", "2026-07-04", "--tmdb-id", "429918"])

            self.assertNotEqual(code, 0)


if __name__ == "__main__":
    unittest.main()