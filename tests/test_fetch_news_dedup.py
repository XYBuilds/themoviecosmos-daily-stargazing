from datetime import datetime, timedelta, timezone
from pathlib import Path
import tempfile
import unittest

from scripts.fetch_news import (
    filter_new_entries,
    is_title_similar,
    is_url_seen,
    mark_title_seen,
    mark_url_seen,
    normalize_url,
)


class FetchNewsDedupTests(unittest.TestCase):
    def _db_path(self, tmpdir: str) -> Path:
        return Path(tmpdir) / "seen_news.sqlite"

    def test_normalize_url_removes_tracking_and_preserves_real_query(self):
        raw = (
            "HTTPS://Example.COM/News/Article?utm_source=rss&b=two&fbclid=abc"
            "&gclid=def&a=one#comments"
        )

        normalized = normalize_url(raw)

        self.assertEqual(normalized, "https://example.com/News/Article?b=two&a=one")
        self.assertEqual(normalize_url(normalized), normalized)

    def test_url_seen_matches_same_url_with_different_tracking_params(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = self._db_path(tmpdir)
            mark_url_seen(
                "https://example.com/story?id=42&utm_medium=social", db_path=db_path
            )

            self.assertTrue(is_url_seen("https://example.com/story?id=42", db_path=db_path))
            self.assertTrue(
                is_url_seen(
                    "https://example.com/story?utm_source=rss&id=42&fbclid=x",
                    db_path=db_path,
                )
            )
            self.assertFalse(is_url_seen("https://example.com/story?id=43", db_path=db_path))

    def test_title_similarity_uses_recent_14_day_window(self):
        now = datetime(2026, 7, 3, 12, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = self._db_path(tmpdir)
            mark_title_seen(
                "NASA announces new moon mission timeline",
                db_path=db_path,
                seen_at=(now - timedelta(days=1)).isoformat(),
            )
            mark_title_seen(
                "European central bank updates inflation forecast",
                db_path=db_path,
                seen_at=(now - timedelta(days=30)).isoformat(),
            )

            self.assertTrue(
                is_title_similar(
                    "NASA announces a new moon mission timeline",
                    db_path=db_path,
                    now=now,
                )
            )
            self.assertFalse(
                is_title_similar(
                    "Local bakery opens a second neighborhood store",
                    db_path=db_path,
                    now=now,
                )
            )
            self.assertFalse(
                is_title_similar(
                    "European central bank updates inflation forecast",
                    db_path=db_path,
                    now=now,
                )
            )

    def test_filter_new_entries_only_filters_seen_urls_and_preserves_order(self):
        now = datetime(2026, 7, 3, 12, 0, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = self._db_path(tmpdir)
            mark_url_seen("https://example.com/seen", db_path=db_path)
            mark_title_seen(
                "Studio reveals cosmic sequel trailer",
                db_path=db_path,
                seen_at=now.isoformat(),
            )
            entries = [
                {"title": "Already seen", "url": "https://example.com/seen?utm_source=rss"},
                {
                    "title": "Studio reveals cosmic sequel trailer",
                    "url": "https://example.com/new-1",
                },
                {
                    "title": "Studio reveals a cosmic sequel trailer",
                    "url": "https://example.com/new-2",
                },
            ]

            filtered = filter_new_entries(entries, db_path=db_path, now=now)

            self.assertEqual(filtered, entries[1:])

    def test_schema_creation_is_idempotent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = self._db_path(tmpdir)

            self.assertFalse(is_url_seen("https://example.com/a", db_path=db_path))
            mark_url_seen("https://example.com/a", db_path=db_path)
            mark_url_seen("https://example.com/a?utm_campaign=x", db_path=db_path)
            mark_title_seen("Repeatable schema title", db_path=db_path)
            self.assertTrue(is_url_seen("https://example.com/a", db_path=db_path))


if __name__ == "__main__":
    unittest.main()