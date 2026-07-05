"""tests/test_heat_pool.py · Phase 7.1 Heat Pool 单元测试."""

from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.fetch_news import mark_url_seen
from scripts.heat_pool import (
    enrich_descriptions,
    fallback_newest,
    fetch_heat_pool,
    fetch_heat_signals,
    filter_seen,
    score_and_rank,
)


def _section_response(most_viewed: list[dict], editors_picks: list[dict]) -> dict:
    return {"response": {"mostViewed": most_viewed, "editorsPicks": editors_picks}}


class FakeResponse:
    def __init__(self, payload: dict):
        self._payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self._payload


class FetchHeatSignalsTests(unittest.TestCase):
    def test_fetch_heat_signals_maps_sections_and_rank_position(self):
        world_payload = _section_response(
            most_viewed=[
                {"webUrl": "https://example.com/a", "webTitle": "A", "webPublicationDate": "2026-07-05T00:00:00Z"},
                {"webUrl": "https://example.com/b", "webTitle": "B", "webPublicationDate": "2026-07-05T00:00:00Z"},
            ],
            editors_picks=[
                {"webUrl": "https://example.com/a", "webTitle": "A", "webPublicationDate": "2026-07-05T00:00:00Z"},
            ],
        )
        science_payload = _section_response(most_viewed=[], editors_picks=[])

        def fake_get(url, params=None, timeout=None):
            if url.endswith("/world"):
                return FakeResponse(world_payload)
            return FakeResponse(science_payload)

        with patch("scripts.heat_pool.requests.get", side_effect=fake_get):
            signals = fetch_heat_signals(["world", "science"], api_key="test-key", sleep_seconds=0)

        most_viewed_signals = [s for s in signals if s["signal_type"] == "mostViewed"]
        self.assertEqual(len(most_viewed_signals), 2)
        self.assertEqual(most_viewed_signals[0]["rank_position"], 1)
        self.assertEqual(most_viewed_signals[0]["url"], "https://example.com/a")
        self.assertEqual(most_viewed_signals[1]["rank_position"], 2)
        self.assertEqual(most_viewed_signals[0]["section"], "world")

        editors_picks_signals = [s for s in signals if s["signal_type"] == "editorsPicks"]
        self.assertEqual(len(editors_picks_signals), 1)
        self.assertEqual(editors_picks_signals[0]["url"], "https://example.com/a")

    def test_fetch_heat_signals_skips_failed_section_without_raising(self):
        def fake_get(url, params=None, timeout=None):
            if url.endswith("/world"):
                raise ConnectionError("network down")
            return FakeResponse(_section_response([], []))

        with patch("scripts.heat_pool.requests.get", side_effect=fake_get):
            signals = fetch_heat_signals(["world", "science"], api_key="test-key", sleep_seconds=0)

        self.assertEqual(signals, [])


class ScoreAndRankTests(unittest.TestCase):
    def test_score_and_rank_sums_cross_section_overlap(self):
        signals = [
            # url a: mostViewed rank 1 in world (+1.0) and rank 2 in science (+0.5) -> 1.5
            {"url": "https://example.com/a", "title": "A", "pub_time": None, "section": "world", "signal_type": "mostViewed", "rank_position": 1},
            {"url": "https://example.com/a", "title": "A", "pub_time": None, "section": "science", "signal_type": "mostViewed", "rank_position": 2},
            # url b: mostViewed rank 1 (+1.0) + editorsPicks (+0.5) -> 1.5, same score as a but fewer sources
            {"url": "https://example.com/b", "title": "B", "pub_time": None, "section": "world", "signal_type": "mostViewed", "rank_position": 1},
            {"url": "https://example.com/b", "title": "B", "pub_time": None, "section": "world", "signal_type": "editorsPicks", "rank_position": 3},
            # url c: only editorsPicks once -> 0.5, lowest
            {"url": "https://example.com/c", "title": "C", "pub_time": None, "section": "world", "signal_type": "editorsPicks", "rank_position": 1},
        ]

        ranked = score_and_rank(signals)

        scores = {item["url"]: item["score"] for item in ranked}
        self.assertAlmostEqual(scores["https://example.com/a"], 1.5)
        self.assertAlmostEqual(scores["https://example.com/b"], 1.5)
        self.assertAlmostEqual(scores["https://example.com/c"], 0.5)
        # DESC order; c must be last
        self.assertEqual(ranked[-1]["url"], "https://example.com/c")
        # a has 2 sources (cross-section overlap), b has 2 sources too (same section, two signals)
        self.assertEqual(len(ranked[0]["sources"]) + len(ranked[1]["sources"]), 4)

    def test_score_and_rank_ignores_signals_without_url(self):
        signals = [{"title": "No URL", "signal_type": "mostViewed", "rank_position": 1}]
        ranked = score_and_rank(signals)
        self.assertEqual(ranked, [])


class FilterSeenTests(unittest.TestCase):
    def test_filter_seen_excludes_already_seen_urls(self):
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "seen_news.sqlite"
            mark_url_seen("https://example.com/seen", db_path)

            ranked = [
                {"url": "https://example.com/seen", "title": "Seen", "score": 2.0, "sources": []},
                {"url": "https://example.com/fresh", "title": "Fresh", "score": 1.0, "sources": []},
            ]
            filtered = filter_seen(ranked, db_path=db_path)

        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0]["url"], "https://example.com/fresh")


class FallbackNewestTests(unittest.TestCase):
    def test_fallback_newest_noop_when_already_enough(self):
        ranked = [
            {"url": f"https://example.com/{i}", "title": f"T{i}", "score": 1.0, "sources": []}
            for i in range(5)
        ]
        with patch("scripts.fetch_news.fetch_guardian_api") as mock_fetch:
            result = fallback_newest(ranked, min_count=3)

        mock_fetch.assert_not_called()
        self.assertEqual(result, ranked)

    def test_fallback_newest_supplements_up_to_min_count(self):
        ranked = [{"url": "https://example.com/existing", "title": "Existing", "score": 1.0, "sources": []}]
        newest_results = [
            {
                "title": "New 1",
                "description": "Desc 1",
                "pub_time": "2026-07-05T00:00:00Z",
                "source_name": "The Guardian | World",
                "url": "https://example.com/new1",
            },
            {
                "title": "New 2",
                "description": "Desc 2",
                "pub_time": "2026-07-05T00:00:00Z",
                "source_name": "The Guardian | World",
                "url": "https://example.com/new2",
            },
            # duplicate of an already-ranked url; must be skipped
            {
                "title": "Existing dup",
                "description": "dup",
                "pub_time": "2026-07-05T00:00:00Z",
                "source_name": "The Guardian | World",
                "url": "https://example.com/existing",
            },
        ]

        with patch("scripts.fetch_news.fetch_guardian_api", return_value=newest_results) as mock_fetch:
            result = fallback_newest(ranked, min_count=3)

        mock_fetch.assert_called_once()
        self.assertEqual(len(result), 3)
        urls = [item["url"] for item in result]
        self.assertEqual(urls, ["https://example.com/existing", "https://example.com/new1", "https://example.com/new2"])
        self.assertEqual(result[1]["description"], "Desc 1")
        self.assertTrue(result[1]["fallback"])


class EnrichDescriptionsTests(unittest.TestCase):
    def test_enrich_descriptions_fills_missing_description_via_content_api(self):
        body_html = (
            "<p>Officials confirmed the incident occurred near the harbour.</p>"
            "<p>Residents were evacuated overnight as a precaution.</p>"
            "<p>Emergency services remained on scene into the morning.</p>"
        )
        content_payload = {
            "response": {
                "content": {
                    "fields": {"bodyText": body_html},
                    "tags": [{"id": "tone/news"}],
                }
            }
        }
        selected = [
            {
                "url": "https://example.com/needs-body",
                "title": "Needs body",
                "score": 1.0,
                "sources": [],
                "id": "world/2026/jul/05/needs-body",
                "api_url": "https://content.guardianapis.com/world/2026/jul/05/needs-body",
            },
            {"url": "https://example.com/has-body", "title": "Has body", "score": 0.5, "sources": [], "description": "Already there"},
        ]

        with patch("scripts.heat_pool.requests.get", return_value=FakeResponse(content_payload)) as mock_get:
            enriched = enrich_descriptions(selected, api_key="test-key")

        mock_get.assert_called_once()
        self.assertEqual(
            mock_get.call_args.args[0],
            "https://content.guardianapis.com/world/2026/jul/05/needs-body",
        )
        self.assertIn("Officials confirmed the incident occurred near the harbour.", enriched[0]["description"])
        self.assertEqual(enriched[1]["description"], "Already there")

    def test_enrich_descriptions_sets_empty_string_on_request_failure(self):
        selected = [{"url": "https://example.com/broken", "title": "Broken", "score": 1.0, "sources": []}]

        with patch("scripts.heat_pool.requests.get", side_effect=ConnectionError("down")):
            enriched = enrich_descriptions(selected, api_key="test-key")

        self.assertEqual(enriched[0]["description"], "")


class FetchHeatPoolTests(unittest.TestCase):
    def test_fetch_heat_pool_dry_run_skips_write_and_returns_pool(self):
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "seen_news.sqlite"
            out_dir = Path(temp_dir) / "daily_batch"

            fake_signals = [
                {"url": "https://example.com/x", "title": "X", "pub_time": None, "section": "world", "signal_type": "mostViewed", "rank_position": 1}
            ]
            with (
                patch("scripts.heat_pool.fetch_heat_signals", return_value=fake_signals),
                patch("scripts.heat_pool.enrich_descriptions", side_effect=lambda items, **_: items),
            ):
                pool = fetch_heat_pool(
                    date="2026-07-05",
                    min_count=1,
                    db_path=db_path,
                    api_key="test-key",
                    dry_run=True,
                    out_dir=out_dir,
                )

            self.assertEqual(len(pool), 1)
            self.assertFalse((out_dir / "2026-07-05" / "pool.json").exists())

    def test_fetch_heat_pool_selects_top_min_count_before_enrichment(self):
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "seen_news.sqlite"
            out_dir = Path(temp_dir) / "daily_batch"

            fake_signals = [
                {
                    "url": f"https://example.com/{i}",
                    "title": f"T{i}",
                    "pub_time": None,
                    "section": "world",
                    "signal_type": "mostViewed",
                    "rank_position": i + 1,
                }
                for i in range(5)
            ]
            enriched_batches: list[list[dict]] = []

            def fake_enrich(items, **_):
                enriched_batches.append(list(items))
                return items

            with (
                patch("scripts.heat_pool.fetch_heat_signals", return_value=fake_signals),
                patch("scripts.heat_pool.enrich_descriptions", side_effect=fake_enrich),
            ):
                pool = fetch_heat_pool(
                    date="2026-07-05",
                    min_count=2,
                    db_path=db_path,
                    api_key="test-key",
                    dry_run=True,
                    out_dir=out_dir,
                )

            self.assertEqual(len(pool), 2)
            self.assertEqual(len(enriched_batches), 1)
            self.assertEqual([item["url"] for item in enriched_batches[0]], [
                "https://example.com/0",
                "https://example.com/1",
            ])

    def test_fetch_heat_pool_writes_pool_json_when_not_dry_run(self):
        with TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "seen_news.sqlite"
            out_dir = Path(temp_dir) / "daily_batch"

            fake_signals = [
                {"url": "https://example.com/y", "title": "Y", "pub_time": None, "section": "world", "signal_type": "mostViewed", "rank_position": 1}
            ]
            with (
                patch("scripts.heat_pool.fetch_heat_signals", return_value=fake_signals),
                patch("scripts.heat_pool.enrich_descriptions", side_effect=lambda items, **_: items),
            ):
                fetch_heat_pool(
                    date="2026-07-05",
                    min_count=1,
                    db_path=db_path,
                    api_key="test-key",
                    dry_run=False,
                    out_dir=out_dir,
                )

            output_path = out_dir / "2026-07-05" / "pool.json"
            self.assertTrue(output_path.is_file())


if __name__ == "__main__":
    unittest.main()