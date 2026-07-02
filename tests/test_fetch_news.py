from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts.fetch_news import fetch_all_entries, fetch_feed


class FetchNewsTests(unittest.TestCase):
    def test_fetch_feed_normalizes_payload_fields(self):
        fake_feed = SimpleNamespace(
            bozo=False,
            feed=SimpleNamespace(title="Example Wire"),
            entries=[
                SimpleNamespace(
                    title="  Example title  ",
                    summary="<p>Climate &amp; energy <strong>update</strong></p>",
                    link=" https://example.com/news/1 ",
                    published_parsed=(2026, 7, 3, 9, 15, 0, 4, 184, 0),
                )
            ],
        )

        with patch("scripts.fetch_news.feedparser.parse", return_value=fake_feed):
            payloads = fetch_feed("https://example.com/rss.xml")

        self.assertEqual(len(payloads), 1)
        self.assertEqual(
            payloads[0],
            {
                "title": "Example title",
                "description": "Climate & energy update",
                "pub_time": "2026-07-03T09:15:00+00:00",
                "source_name": "Example Wire",
                "url": "https://example.com/news/1",
            },
        )

    def test_fetch_feed_drops_entries_missing_required_fields(self):
        fake_feed = SimpleNamespace(
            bozo=False,
            feed=SimpleNamespace(title="Example Wire"),
            entries=[
                SimpleNamespace(
                    summary="Valid summary",
                    link="https://example.com/news/no-title",
                ),
                SimpleNamespace(
                    title="No link",
                    summary="Valid summary",
                ),
                SimpleNamespace(
                    title="No description",
                    link="https://example.com/news/no-description",
                ),
                SimpleNamespace(
                    title="Complete",
                    description="Plain description",
                    link="https://example.com/news/complete",
                ),
            ],
        )

        with patch("scripts.fetch_news.feedparser.parse", return_value=fake_feed):
            payloads = fetch_feed("https://example.com/rss.xml")

        self.assertEqual(len(payloads), 1)
        self.assertEqual(payloads[0]["title"], "Complete")
        self.assertEqual(payloads[0]["description"], "Plain description")
        self.assertEqual(payloads[0]["url"], "https://example.com/news/complete")

    def test_fetch_feed_returns_empty_on_parse_exception(self):
        with (
            self.assertLogs("scripts.fetch_news", level="WARNING"),
            patch("scripts.fetch_news.feedparser.parse", side_effect=RuntimeError("network down")),
        ):
            payloads = fetch_feed("https://example.com/rss.xml")

        self.assertEqual(payloads, [])

    def test_fetch_feed_returns_empty_on_bozo(self):
        fake_feed = SimpleNamespace(
            bozo=True,
            bozo_exception=ValueError("malformed xml"),
            feed=SimpleNamespace(title="Example Wire"),
            entries=[
                SimpleNamespace(
                    title="Should be skipped",
                    summary="Summary",
                    link="https://example.com/news/skip",
                )
            ],
        )

        with (
            self.assertLogs("scripts.fetch_news", level="WARNING"),
            patch("scripts.fetch_news.feedparser.parse", return_value=fake_feed),
        ):
            payloads = fetch_feed("https://example.com/rss.xml")

        self.assertEqual(payloads, [])

    def test_fetch_all_entries_merges_sources_and_skips_failures(self):
        def fake_fetch(feed_url):
            if feed_url == "bad-feed":
                raise RuntimeError("bad feed")
            return [
                {
                    "title": f"Title from {feed_url}",
                    "description": "Description",
                    "pub_time": None,
                    "source_name": "Example Wire",
                    "url": f"https://example.com/{feed_url}",
                }
            ]

        with (
            self.assertLogs("scripts.fetch_news", level="WARNING"),
            patch("scripts.fetch_news.fetch_feed", side_effect=fake_fetch),
        ):
            payloads = fetch_all_entries(["feed-a", "bad-feed", "feed-b"])

        self.assertEqual(len(payloads), 2)
        self.assertEqual([item["title"] for item in payloads], ["Title from feed-a", "Title from feed-b"])

    def test_acceptance_import_and_payload_keys(self):
        fake_payload = {
            "title": "Acceptance title",
            "description": "Acceptance description",
            "pub_time": None,
            "source_name": "Acceptance Source",
            "url": "https://example.com/acceptance",
        }

        with patch("scripts.fetch_news.fetch_feed", return_value=[fake_payload]):
            from scripts.fetch_news import fetch_all_entries as imported_fetch_all_entries

            entries = imported_fetch_all_entries(["acceptance-feed"])

        self.assertTrue(entries)
        self.assertEqual(
            set(entries[0].keys()),
            {"title", "description", "pub_time", "source_name", "url"},
        )


if __name__ == "__main__":
    unittest.main()