"""Unit tests for Phase 8.2 review_panel/publish_adapter.py."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.compose import JudgeEntry
from review_panel.publish_adapter import (
    find_candidate,
    load_judge_entry,
    load_news,
    locate_news_dir,
    main,
    run_adapter,
)


def _write_news(news_dir: Path) -> None:
    payload = {
        "title": "Test headline",
        "description": "Test description.",
        "pub_time": "2026-07-05T14:02:46Z",
        "source_name": "Guardian",
        "url": "https://example.com/article/1",
    }
    (news_dir / "news.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_retrieve(news_dir: Path, tmdb_id: int = 429918) -> None:
    payload = {
        "candidates": [
            {
                "tmdb_id": tmdb_id,
                "title": "Survival Family",
                "overview": "An overview.",
                "genres": "Comedy, Drama",
                "release_year": 2017,
                "language": "ja",
                "poster_path": "/poster.jpg",
                "movie_url": f"https://themoviecosmos.com/movie/{tmdb_id}",
                "similarity": 0.42,
                "triggered_by": ["THE-HERO"],
                "hit_sources": [],
            }
        ]
    }
    (news_dir / "retrieve.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _write_judge_scores(news_dir: Path, tmdb_id: int = 429918) -> None:
    payload = {
        "version": "1",
        "calibration": {},
        "scores": [
            {
                "tmdb_id": str(tmdb_id),
                "judge_score": 3,
                "judge_resonance_type": "深层共振",
                "rationale": "rationale text",
                "causal_test": "causal test text",
            }
        ],
    }
    (news_dir / "llm-judge-scores.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


def _make_batch(tmp_path: Path, date: str, slug: str, tmdb_id: int = 429918, with_judge: bool = True) -> Path:
    news_dir = tmp_path / date / slug
    news_dir.mkdir(parents=True)
    _write_news(news_dir)
    _write_retrieve(news_dir, tmdb_id=tmdb_id)
    if with_judge:
        _write_judge_scores(news_dir, tmdb_id=tmdb_id)
    return tmp_path


def _fake_run_publish(candidate, news, *, provider=None, judge=None):
    return {"tmdb_id": candidate["tmdb_id"], "body": "这是中文正文。"}


class LocateNewsDirTests(unittest.TestCase):
    def test_missing_slug_dir_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            with self.assertRaises(ValueError) as ctx:
                locate_news_dir("2026-07-06", "no-such-slug", batch_root=tmp_path)
            self.assertIn("no-such-slug", str(ctx.exception))

    def test_found_dir(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            news_dir = locate_news_dir("2026-07-06", "09-slug", batch_root=tmp_path)
            self.assertTrue(news_dir.is_dir())


class FindCandidateTests(unittest.TestCase):
    def test_int_str_normalization_matches(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug", tmdb_id=429918)
            news_dir = tmp_path / "2026-07-06" / "09-slug"

            cand_via_str = find_candidate(news_dir, "429918")
            cand_via_int = find_candidate(news_dir, 429918)
            self.assertEqual(cand_via_str["title"], "Survival Family")
            self.assertEqual(cand_via_int["title"], "Survival Family")

    def test_unmatched_tmdb_id_raises_with_available_ids(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug", tmdb_id=429918)
            news_dir = tmp_path / "2026-07-06" / "09-slug"

            with self.assertRaises(ValueError) as ctx:
                find_candidate(news_dir, 999999)
            self.assertIn("999999", str(ctx.exception))
            self.assertIn("429918", str(ctx.exception))


class LoadJudgeEntryTests(unittest.TestCase):
    def test_joins_judge_row_by_normalized_tmdb_id(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug", tmdb_id=429918)
            news_dir = tmp_path / "2026-07-06" / "09-slug"

            judge = load_judge_entry(news_dir, 429918)
            self.assertIsInstance(judge, JudgeEntry)
            self.assertEqual(judge.score, 3)
            self.assertEqual(judge.resonance_type, "深层共振")
            self.assertEqual(judge.rationale, "rationale text")
            self.assertEqual(judge.causal_test, "causal test text")

    def test_missing_judge_file_returns_none(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug", tmdb_id=429918, with_judge=False)
            news_dir = tmp_path / "2026-07-06" / "09-slug"

            self.assertIsNone(load_judge_entry(news_dir, 429918))

    def test_unmatched_tmdb_id_in_judge_file_returns_none(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug", tmdb_id=429918)
            news_dir = tmp_path / "2026-07-06" / "09-slug"

            self.assertIsNone(load_judge_entry(news_dir, 111))


class RunAdapterTests(unittest.TestCase):
    def test_writes_copy_md_with_body_and_links(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug", tmdb_id=429918)

            copy_path = run_adapter(
                "2026-07-06",
                "09-slug",
                429918,
                batch_root=tmp_path,
                run_publish=_fake_run_publish,
            )

            self.assertEqual(copy_path, tmp_path / "2026-07-06" / "09-slug_copy.md")
            self.assertTrue(copy_path.is_file())
            content = copy_path.read_text(encoding="utf-8")
            self.assertIn("这是中文正文。", content)
            self.assertIn("https://themoviecosmos.com/movie/429918", content)
            self.assertIn("https://example.com/article/1", content)
            self.assertIn("《Survival Family》(2017)", content)

    def test_judge_entry_passed_into_run_publish(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug", tmdb_id=429918)

            captured: dict = {}

            def capturing_run_publish(candidate, news, *, provider=None, judge=None):
                captured["judge"] = judge
                return {"tmdb_id": candidate["tmdb_id"], "body": "正文"}

            run_adapter(
                "2026-07-06",
                "09-slug",
                429918,
                batch_root=tmp_path,
                run_publish=capturing_run_publish,
            )

            judge = captured["judge"]
            self.assertIsInstance(judge, JudgeEntry)
            self.assertEqual(judge.score, 3)
            self.assertEqual(judge.rationale, "rationale text")
            self.assertEqual(judge.causal_test, "causal test text")
            self.assertEqual(judge.resonance_type, "深层共振")

    def test_missing_judge_file_passes_none_and_still_writes_copy(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug", tmdb_id=429918, with_judge=False)

            captured: dict = {}

            def capturing_run_publish(candidate, news, *, provider=None, judge=None):
                captured["judge"] = judge
                return {"tmdb_id": candidate["tmdb_id"], "body": "正文"}

            copy_path = run_adapter(
                "2026-07-06",
                "09-slug",
                429918,
                batch_root=tmp_path,
                run_publish=capturing_run_publish,
            )

            self.assertIsNone(captured["judge"])
            self.assertTrue(copy_path.is_file())

    def test_unmatched_tmdb_id_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug", tmdb_id=429918)

            with self.assertRaises(ValueError):
                run_adapter(
                    "2026-07-06",
                    "09-slug",
                    999999,
                    batch_root=tmp_path,
                    run_publish=_fake_run_publish,
                )

    def test_missing_slug_dir_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug", tmdb_id=429918)

            with self.assertRaises(ValueError):
                run_adapter(
                    "2026-07-06",
                    "no-such-slug",
                    429918,
                    batch_root=tmp_path,
                    run_publish=_fake_run_publish,
                )


class MainCliTests(unittest.TestCase):
    def test_cli_success_path_writes_copy_md(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug", tmdb_id=429918)

            from unittest.mock import patch

            with (
                patch("review_panel.publish_adapter.compose.run_publish", side_effect=_fake_run_publish),
                patch("review_panel.publish_adapter._default_batch_root", return_value=tmp_path),
            ):
                code = main(
                    [
                        "--date",
                        "2026-07-06",
                        "--news-slug",
                        "09-slug",
                        "--tmdb-id",
                        "429918",
                    ]
                )
            self.assertEqual(code, 0)
            self.assertTrue((tmp_path / "2026-07-06" / "09-slug_copy.md").is_file())

    def test_cli_missing_slug_exits_nonzero(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug", tmdb_id=429918)

            code = main(
                [
                    "--date",
                    "2026-07-06",
                    "--news-slug",
                    "no-such-slug",
                    "--tmdb-id",
                    "429918",
                ]
            )
            self.assertNotEqual(code, 0)


if __name__ == "__main__":
    unittest.main()