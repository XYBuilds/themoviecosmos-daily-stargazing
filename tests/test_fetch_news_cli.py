from contextlib import redirect_stderr
from io import StringIO
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest
from unittest.mock import patch

from scripts.fetch_news import (
    build_parser,
    is_url_seen,
    render_news_list,
    run_cli,
    sort_entries_by_pub_time,
)


class FetchNewsCliTests(unittest.TestCase):
    def _db_path(self, tmpdir: str) -> Path:
        return Path(tmpdir) / "seen_news.sqlite"

    def _entries(self) -> list[dict]:
        return [
            {
                "title": "Old story",
                "description": "Old description",
                "pub_time": "2026-05-28T10:00:00+00:00",
                "source_name": "Source A",
                "url": "https://example.com/old",
            },
            {
                "title": "Newest story",
                "description": "Newest description",
                "pub_time": "2026-05-29T12:00:00+00:00",
                "source_name": "Source B",
                "url": "https://example.com/newest",
            },
            {
                "title": "No date story",
                "description": "No date description",
                "pub_time": None,
                "source_name": None,
                "url": "https://example.com/no-date",
            },
        ]

    def test_sort_pub_time_desc_none_last_and_stable(self):
        entries = [
            {"title": "first same", "pub_time": "2026-05-29T12:00:00+00:00"},
            {"title": "none", "pub_time": None},
            {"title": "newer", "pub_time": "2026-05-30T08:00:00+00:00"},
            {"title": "second same", "pub_time": "2026-05-29T12:00:00+00:00"},
        ]

        sorted_entries = sort_entries_by_pub_time(entries)

        self.assertEqual(
            [entry["title"] for entry in sorted_entries],
            ["newer", "first same", "second same", "none"],
        )

    def test_render_news_list_includes_number_url_truncation_and_placeholders(self):
        long_title = "A" * 120
        output = render_news_list(
            [
                {
                    "title": long_title,
                    "description": "Description",
                    "pub_time": None,
                    "source_name": None,
                    "url": "https://example.com/story",
                }
            ]
        )

        self.assertIn("[1]", output)
        self.assertIn("https://example.com/story", output)
        self.assertIn("Unknown Source", output)
        self.assertIn("- · Unknown Source ·", output)
        self.assertIn("…", output)

    def test_out_writes_deduplicated_candidate_pool_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = self._db_path(tmpdir)
            out_path = Path(tmpdir) / "state" / "news_pool.json"

            with patch("scripts.fetch_news.fetch_all_entries", return_value=self._entries()):
                code = run_cli(["--provider", "rss", "--out", str(out_path), "--limit", "2"], db_path=db_path, stdout=StringIO())

            self.assertEqual(code, 0)
            loaded = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(len(loaded), 3)
            self.assertEqual(loaded[0]["title"], "Newest story")
            self.assertEqual(loaded[-1]["title"], "No date story")

    def test_pick_outputs_news_json_and_marks_seen(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = self._db_path(tmpdir)
            stdout = StringIO()

            with patch("scripts.fetch_news.fetch_all_entries", return_value=self._entries()):
                code = run_cli(["--provider", "rss", "--pick", "2"], db_path=db_path, stdout=stdout)

            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(set(payload.keys()), {"title", "description", "pub_time", "source_name", "url"})
            self.assertEqual(payload["title"], "Old story")
            self.assertTrue(is_url_seen("https://example.com/old", db_path=db_path))

    def test_pick_out_of_range_returns_nonzero_and_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = self._db_path(tmpdir)
            stderr = StringIO()

            with patch("scripts.fetch_news.fetch_all_entries", return_value=self._entries()):
                code = run_cli(["--provider", "rss", "--pick", "99"], db_path=db_path, stdout=StringIO(), stderr=stderr)

            self.assertEqual(code, 1)
            self.assertIn("out of range", stderr.getvalue())

    def test_pick_and_url_are_mutually_exclusive(self):
        with redirect_stderr(StringIO()):
            with self.assertRaises(SystemExit) as raised:
                build_parser().parse_args(["--pick", "1", "--url", "https://example.com/article"])

        self.assertEqual(raised.exception.code, 2)

    def test_url_fallback_outputs_news_json_and_marks_seen(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = self._db_path(tmpdir)
            stdout = StringIO()
            fake_parsed = SimpleNamespace(feed=SimpleNamespace(title="Ignored"), entries=[])

            with patch("scripts.fetch_news.feedparser.parse", return_value=fake_parsed):
                code = run_cli(
                    [
                        "--url",
                        "https://example.com/article",
                        "--title",
                        "Manual title",
                        "--description",
                        "<p>Manual description</p>",
                    ],
                    db_path=db_path,
                    stdout=stdout,
                )

            self.assertEqual(code, 0)
            payload = json.loads(stdout.getvalue())
            self.assertEqual(payload["title"], "Manual title")
            self.assertEqual(payload["description"], "Manual description")
            self.assertEqual(payload["url"], "https://example.com/article")
            self.assertTrue(is_url_seen("https://example.com/article", db_path=db_path))

    def test_url_without_parse_or_fallback_returns_nonzero(self):
        stderr = StringIO()
        fake_parsed = SimpleNamespace(feed=SimpleNamespace(title="Ignored"), entries=[])

        with patch("scripts.fetch_news.feedparser.parse", return_value=fake_parsed):
            code = run_cli(["--url", "https://example.com/article"], stdout=StringIO(), stderr=stderr)

        self.assertEqual(code, 1)
        self.assertIn("--title and --description", stderr.getvalue())

    def test_pick_out_json_file_is_valid_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = self._db_path(tmpdir)
            out_path = Path(tmpdir) / "output" / "picked_news.json"

            with patch("scripts.fetch_news.fetch_all_entries", return_value=self._entries()):
                code = run_cli(["--provider", "rss", "--pick", "1", "--out-json", str(out_path)], db_path=db_path)

            self.assertEqual(code, 0)
            payload = json.loads(out_path.read_text(encoding="utf-8"))
            self.assertEqual(payload["title"], "Newest story")


if __name__ == "__main__":
    unittest.main()