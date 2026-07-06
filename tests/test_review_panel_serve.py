"""Unit tests for Phase 8.3 review_panel/serve.py.

优先测纯路由函数 route()（不起真实端口），符合 serve.py 里「传输层与路由逻辑
解耦」的设计：造临时 batch_root + mini 数据，直接调 route() 验证行为。
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from review_panel.serve import read_selection, route


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
                "hit_sources": [],
            }
        ]
    }
    (news_dir / "retrieve.json").write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _make_batch(tmp_path: Path, date: str, slug: str, tmdb_id: int = 429918) -> None:
    news_dir = tmp_path / date / slug
    news_dir.mkdir(parents=True)
    _write_news(news_dir)
    _write_retrieve(news_dir, tmdb_id=tmdb_id)


class DatesRouteTests(unittest.TestCase):
    def test_returns_dates_in_descending_order(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-05", "01-slug")
            _make_batch(tmp_path, "2026-07-06", "01-slug")

            status, payload = route("GET", "/api/dates", {}, None, batch_root=tmp_path)

            self.assertEqual(status, 200)
            self.assertEqual(payload, {"dates": ["2026-07-06", "2026-07-05"]})


class DataRouteTests(unittest.TestCase):
    def test_returns_panel_dict_with_news_items(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")

            status, payload = route(
                "GET", "/api/data", {"date": "2026-07-06"}, None, batch_root=tmp_path
            )

            self.assertEqual(status, 200)
            self.assertEqual(payload["date"], "2026-07-06")
            self.assertEqual(len(payload["news_items"]), 1)
            self.assertEqual(payload["news_items"][0]["slug"], "09-slug")
            self.assertEqual(payload["news_items"][0]["candidates"][0]["title"], "Survival Family")

    def test_missing_date_param_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route("GET", "/api/data", {}, None, batch_root=tmp_path)
            self.assertEqual(status, 400)
            self.assertIn("error", payload)

    def test_unknown_date_returns_404(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route(
                "GET", "/api/data", {"date": "2099-01-01"}, None, batch_root=tmp_path
            )
            self.assertEqual(status, 404)
            self.assertIn("error", payload)


class SelectRouteTests(unittest.TestCase):
    def test_writes_selection_json(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")

            status, payload = route(
                "POST",
                "/api/select",
                {},
                {"date": "2026-07-06", "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            selection = read_selection(tmp_path, "2026-07-06")
            self.assertEqual(selection["selected"]["news_slug"], "09-slug")
            self.assertEqual(selection["selected"]["tmdb_id"], 429918)
            self.assertFalse(selection["published"])
            self.assertIsNone(selection["copy_path"])

    def test_repeated_select_is_idempotent_last_wins(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            _make_batch(tmp_path, "2026-07-06", "10-slug", tmdb_id=99)

            route(
                "POST",
                "/api/select",
                {},
                {"date": "2026-07-06", "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )
            route(
                "POST",
                "/api/select",
                {},
                {"date": "2026-07-06", "news_slug": "10-slug", "tmdb_id": 99, "title": "Other Movie"},
                batch_root=tmp_path,
            )

            selection = read_selection(tmp_path, "2026-07-06")
            self.assertEqual(selection["selected"]["news_slug"], "10-slug")
            self.assertEqual(selection["selected"]["tmdb_id"], 99)

    def test_missing_required_field_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route(
                "POST", "/api/select", {}, {"date": "2026-07-06"}, batch_root=tmp_path
            )
            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])


class PublishRouteTests(unittest.TestCase):
    def test_success_updates_selection_and_returns_copy_path(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            route(
                "POST",
                "/api/select",
                {},
                {"date": "2026-07-06", "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )

            expected_copy_path = tmp_path / "2026-07-06" / "09-slug_copy.md"

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                # 断言子进程命令行的确切形态：脚本路径 + --date/--news-slug/--tmdb-id。
                self.assertIn("--date", cmd)
                self.assertIn("2026-07-06", cmd)
                self.assertIn("--news-slug", cmd)
                self.assertIn("09-slug", cmd)
                self.assertIn("--tmdb-id", cmd)
                self.assertIn("429918", cmd)
                return SimpleNamespace(
                    returncode=0, stdout="", stderr=f"Wrote {expected_copy_path}\n"
                )

            status, payload = route(
                "POST",
                "/api/publish",
                {},
                {"date": "2026-07-06"},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 200)
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["copy_path"], str(expected_copy_path))

            selection = read_selection(tmp_path, "2026-07-06")
            self.assertTrue(selection["published"])
            self.assertEqual(selection["copy_path"], str(expected_copy_path))

    def test_failure_returns_ok_false_and_stderr(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")
            route(
                "POST",
                "/api/select",
                {},
                {"date": "2026-07-06", "news_slug": "09-slug", "tmdb_id": 429918, "title": "Survival Family"},
                batch_root=tmp_path,
            )

            def fake_run_subprocess(cmd, capture_output, text):  # noqa: ANN001
                return SimpleNamespace(returncode=2, stdout="", stderr="error: tmdb_id not found")

            status, payload = route(
                "POST",
                "/api/publish",
                {},
                {"date": "2026-07-06"},
                batch_root=tmp_path,
                run_subprocess=fake_run_subprocess,
            )

            self.assertEqual(status, 500)
            self.assertFalse(payload["ok"])
            self.assertIsNone(payload["copy_path"])
            self.assertEqual(payload["stderr"], "error: tmdb_id not found")

            selection = read_selection(tmp_path, "2026-07-06")
            self.assertFalse(selection["published"])

    def test_missing_selection_returns_400(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "09-slug")

            status, payload = route(
                "POST", "/api/publish", {}, {"date": "2026-07-06"}, batch_root=tmp_path
            )

            self.assertEqual(status, 400)
            self.assertFalse(payload["ok"])


class UnknownRouteTests(unittest.TestCase):
    def test_unknown_path_returns_404(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            status, payload = route("GET", "/api/nope", {}, None, batch_root=tmp_path)
            self.assertEqual(status, 404)
            self.assertIn("error", payload)


if __name__ == "__main__":
    unittest.main()