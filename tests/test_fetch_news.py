from io import StringIO
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts.fetch_news import (
    extract_guardian_description,
    fetch_all_entries,
    fetch_feed,
    fetch_guardian_api,
    filter_guardian_sections,
    run_cli,
)


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

    def test_fetch_feed_removes_guardian_continue_reading_tail(self):
        fake_feed = SimpleNamespace(
            bozo=False,
            feed=SimpleNamespace(title="The Guardian"),
            entries=[
                SimpleNamespace(
                    title="Guardian title",
                    summary=(
                        "<p>Officials said the policy would affect families in several cities "
                        "after weeks of public pressure.</p>"
                        '<p><a href="https://www.theguardian.com/example">Continue reading...</a></p>'
                    ),
                    link="https://www.theguardian.com/example",
                )
            ],
        )

        with patch("scripts.fetch_news.feedparser.parse", return_value=fake_feed):
            payloads = fetch_feed("https://www.theguardian.com/world/rss")

        self.assertEqual(len(payloads), 1)
        self.assertEqual(
            payloads[0]["description"],
            "Officials said the policy would affect families in several cities after weeks of public pressure.",
        )
        self.assertNotIn("Continue reading", payloads[0]["description"])

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

    def test_fetch_guardian_api_no_key(self):
        with patch("scripts.fetch_news._load_env_value", return_value=None):
            with self.assertRaisesRegex(RuntimeError, "GUARDIAN_API_KEY not set"):
                fetch_guardian_api(api_key=None)

    def test_fetch_guardian_api_success(self):
        # HTML body with paragraph tags
        body_html = (
            "<p>Death and rescue story in the city centre.</p>"
            "<p>Police arrived at the scene within minutes.</p>"
            "<p>Witnesses described chaos and heroism.</p>"
            "<p>The mayor issued a statement of condolence.</p>"
            "<p>Investigations are ongoing into the cause.</p>"
            "<p>Extra paragraph that should not be included.</p>"
        )
        trail_body_html = (
            "<p>A survivor describes an attack in detail.</p>"
            "<p>The community rallied around the victims.</p>"
            "<p>Related: Another story link</p>"
            "<p>Authorities launched a full inquiry.</p>"
            "<p>Support services were deployed immediately.</p>"
            "<p>The event shook the nation.</p>"
        )

        class FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {
                    "response": {
                        "results": [
                            {
                                "webTitle": "Death and rescue in city",
                                "fields": {"body": body_html, "trailText": "short trail"},
                                "tags": [{"id": "tone/news"}],
                                "webPublicationDate": "2026-07-03T10:00:00Z",
                                "sectionName": "World news",
                                "webUrl": "https://www.theguardian.com/world/one",
                            },
                            {
                                "webTitle": "Too short",
                                "fields": {"body": "<p>short</p>"},
                                "webPublicationDate": "2026-07-03T09:00:00Z",
                                "sectionName": "Society",
                                "webUrl": "https://www.theguardian.com/society/short",
                            },
                            {
                                "webTitle": "Fallback trail story",
                                "fields": {"body": trail_body_html},
                                "tags": [{"id": "tone/news"}],
                                "webPublicationDate": "2026-07-03T08:00:00Z",
                                "sectionName": "Law",
                                "webUrl": "https://www.theguardian.com/law/fallback",
                            },
                        ]
                    }
                }

        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "seen_news.sqlite"
            with patch("scripts.fetch_news.requests.get", return_value=FakeResponse()) as mock_get:
                payloads = fetch_guardian_api(
                    sections=["world", "law"],
                    order_by="relevance",
                    page_size=3,
                    min_body_len=100,
                    tag="world/example",
                    db_path=db_path,
                    api_key="test-key",
                )

        self.assertEqual(len(payloads), 2)
        # First item: 5 paragraphs (6th excluded by max_paragraphs=5)
        expected_desc_0 = (
            "Death and rescue story in the city centre. "
            "Police arrived at the scene within minutes. "
            "Witnesses described chaos and heroism. "
            "The mayor issued a statement of condolence. "
            "Investigations are ongoing into the cause."
        )
        self.assertEqual(payloads[0]["title"], "Death and rescue in city")
        self.assertEqual(payloads[0]["description"], expected_desc_0)
        self.assertEqual(payloads[0]["pub_time"], "2026-07-03T10:00:00Z")
        # Second item: "Related:" paragraph skipped, so 5 kept from remaining
        expected_desc_1 = (
            "A survivor describes an attack in detail. "
            "The community rallied around the victims. "
            "Authorities launched a full inquiry. "
            "Support services were deployed immediately. "
            "The event shook the nation."
        )
        self.assertEqual(payloads[1]["description"], expected_desc_1)
        mock_get.assert_called_once_with(
            "https://content.guardianapis.com/search",
            params={
                "api-key": "test-key",
                "section": "world|law",
                "order-by": "relevance",
                "from-date": __import__("datetime").date.today().isoformat(),
                "page-size": 3,
                "show-fields": "bodyText,trailText,headline",
                "show-tags": "all",
                "tag": "world/example",
            },
            timeout=30,
        )

    def test_guardian_tone_drop_blacklist_excludes_articles_before_payload_pool(self):
        body = " ".join(f"Sentence {index} with enough public event context." for index in range(1, 30))

        def result(title, tones, url_suffix):
            return {
                "webTitle": title,
                "fields": {"bodyText": body},
                "tags": [{"id": tone} for tone in tones],
                "webPublicationDate": "2026-07-03T10:00:00Z",
                "sectionName": "World news",
                "webUrl": f"https://www.theguardian.com/world/{url_suffix}",
            }

        class FakeResponse:
            def raise_for_status(self):
                return None

            def json(self):
                return {
                    "response": {
                        "results": [
                            result("Live updates", ["tone/minutebyminute"], "live"),
                            result("Reader letter", ["tone/letters"], "letter"),
                            result("Competition call", ["tone/competitions"], "competition"),
                            result(
                                "Live news hybrid",
                                ["tone/minutebyminute", "tone/news"],
                                "live-news",
                            ),
                            result("Pure news", ["tone/news"], "pure-news"),
                        ]
                    }
                }

        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "seen_news.sqlite"
            with patch("scripts.fetch_news.requests.get", return_value=FakeResponse()):
                payloads = fetch_guardian_api(
                    sections=["world"],
                    min_body_len=100,
                    db_path=db_path,
                    api_key="test-key",
                )

        self.assertEqual([payload["title"] for payload in payloads], ["Pure news"])

    def test_guardian_section_blacklist_filters_low_event_travel_but_keeps_mixed_sections(self):
        sections = ["travel", "culture", "film"]

        self.assertEqual(filter_guardian_sections(sections), ["culture", "film"])

    def test_guardian_section_blacklist_filters_five_categories(self):
        sections = [
            "media-network",  # suffix/B2B
            "professional",  # professional class
            "about",  # meta/tool
            "weather",  # functional
            "travel",  # low-event travelogue/service texture
            "local",  # local news
            "film",
            "education",
            "sport",
        ]

        self.assertEqual(filter_guardian_sections(sections), ["film", "education", "sport"])

    def test_tone_extraction_routes_news_to_front_five(self):
        body = "".join(f"<p>paragraph {index} with useful hard news facts.</p>" for index in range(1, 7))

        description = extract_guardian_description(body, [{"id": "tone/news"}])

        self.assertIn("paragraph 1", description)
        self.assertIn("paragraph 5", description)
        self.assertNotIn("paragraph 6", description)

    def test_tone_extraction_routes_recipes_to_lede(self):
        body = "".join(f"<p>paragraph {index} with text.</p>" for index in range(1, 4))

        recipe = extract_guardian_description(body, [{"id": "tone/recipes"}])

        self.assertEqual(recipe, "paragraph 1 with text.")

    def test_tone_extraction_uses_specific_tone_before_features(self):
        body = "".join(f"<p>paragraph {index} with text.</p>" for index in range(1, 4))

        description = extract_guardian_description(
            body,
            [{"id": "tone/features"}, {"id": "tone/recipes"}],
        )

        self.assertEqual(description, "paragraph 1 with text.")

    def test_tone_features_uses_paragraph_decay_heuristic(self):
        long_lede = "Lede " + "core setup " * 30
        strong_followup = "Followup " + "context detail " * 20
        short_bridge = "Short bridge."
        body = f"<p>{long_lede}</p><p>{strong_followup}</p><p>{short_bridge}</p><p>Later texture.</p>"

        description = extract_guardian_description(body, [{"id": "tone/features"}])

        self.assertIn(long_lede.strip(), description)
        self.assertIn(strong_followup.strip(), description)
        self.assertNotIn(short_bridge, description)

    def test_tone_extraction_without_tone_defaults_to_front_three(self):
        body = "".join(f"<p>paragraph {index} with text.</p>" for index in range(1, 5))

        description = extract_guardian_description(body, [])

        self.assertIn("paragraph 1", description)
        self.assertIn("paragraph 3", description)
        self.assertNotIn("paragraph 4", description)

    def test_cli_without_pick_auto_outputs_limited_news_collection(self):
        fake_payloads = [
            {
                "title": "First automatic story",
                "description": "Description one",
                "pub_time": "2026-07-03T10:00:00Z",
                "source_name": "The Guardian | World",
                "url": "https://example.com/one",
            },
            {
                "title": "Second automatic story",
                "description": "Description two",
                "pub_time": "2026-07-03T09:00:00Z",
                "source_name": "The Guardian | Film",
                "url": "https://example.com/two",
            },
        ]
        stdout = StringIO()

        with patch("scripts.fetch_news.fetch_guardian_api", return_value=fake_payloads):
            code = run_cli(["--limit", "1"], stdout=stdout)

        self.assertEqual(code, 0)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(len(payload), 1)
        self.assertEqual(payload[0]["title"], "First automatic story")


if __name__ == "__main__":
    unittest.main()