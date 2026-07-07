"""Unit tests for Phase 8.1/8.6 review_panel/build_data.py."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from review_panel.build_data import (
    _extract_resonance_agents,
    _join_judge_scores,
    _load_zh_cache,
    build_panel_data,
    list_available_dates,
    write_panel_json,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _news_payload(title: str = "Headline", description: str = "A description.") -> dict:
    return {
        "title": title,
        "description": description,
        "pub_time": "2026-07-05T14:02:46Z",
        "source_name": "Guardian",
        "url": "https://example.com/article",
    }


def _retrieve_payload(candidates: list[dict]) -> dict:
    return {"per_agent": [], "candidates": candidates}


def _candidate(
    tmdb_id: int,
    title: str,
    hit_sources: list[dict] | None = None,
    overview: str = "An overview.",
) -> dict:
    return {
        "tmdb_id": tmdb_id,
        "title": title,
        "overview": overview,
        "genres": "Comedy, Drama",
        "release_year": 2024,
        "language": "fr",
        "poster_path": "/poster.jpg",
        "movie_url": f"https://themoviecosmos.com/movie/{tmdb_id}",
        "similarity": 0.619,
        "triggered_by": ["THE-INNOCENT"],
        "also_baseline": False,
        "hit_sources": hit_sources or [],
    }


def _judge_payload(scores: list[dict]) -> dict:
    return {"version": 4, "calibration": {}, "scores": scores}


def _judge_entry(tmdb_id: str, title: str, score: int | None = 1, rationale: str = "some rationale") -> dict:
    return {
        "run_id": "run",
        "tmdb_id": tmdb_id,
        "title": title,
        "judge_score": score,
        "judge_resonance_type": "表层沾边",
        "rationale": rationale,
        "causal_test": "",
    }


class ExtractResonanceAgentsTests(unittest.TestCase):
    def test_dedupes_and_preserves_first_seen_order(self) -> None:
        hit_sources = [
            {"agent_id": "THE-INNOCENT"},
            {"agent_id": "THE-HERO"},
            {"agent_id": "THE-INNOCENT"},
            {"agent_id": "THE-LOVER"},
        ]
        self.assertEqual(
            _extract_resonance_agents(hit_sources),
            ["THE-INNOCENT", "THE-HERO", "THE-LOVER"],
        )

    def test_empty_hit_sources_returns_empty_list(self) -> None:
        self.assertEqual(_extract_resonance_agents([]), [])


class JoinJudgeScoresTests(unittest.TestCase):
    def test_joins_int_tmdb_id_candidate_with_str_tmdb_id_judge_entry(self) -> None:
        candidates = [_candidate(1083324, "A Mother's Special Love")]
        judge_scores = _judge_payload([_judge_entry("1083324", "A Mother's Special Love", score=2)])

        joined = _join_judge_scores(candidates, judge_scores)

        self.assertEqual(joined[0]["judge_score"], 2)
        self.assertEqual(joined[0]["judge_resonance_type"], "表层沾边")
        self.assertEqual(joined[0]["judge_rationale"], "some rationale")

    def test_slims_fields_to_schema_only_and_drops_causal_test(self) -> None:
        candidates = [
            _candidate(1083324, "A Mother's Special Love", hit_sources=[{"agent_id": "THE-INNOCENT"}])
        ]
        joined = _join_judge_scores(
            candidates, _judge_payload([_judge_entry("1083324", "A Mother's Special Love", score=1)])
        )

        expected_keys = {
            "tmdb_id",
            "title",
            "release_year",
            "overview",
            "overview_zh",
            "genres",
            "language",
            "similarity",
            "movie_url",
            "poster_path",
            "resonance_agents",
            "judge_score",
            "judge_resonance_type",
            "judge_rationale",
            "judge_rationale_zh",
        }
        self.assertEqual(set(joined[0].keys()), expected_keys)
        self.assertNotIn("triggered_by", joined[0])
        self.assertNotIn("hit_sources", joined[0])
        self.assertNotIn("also_baseline", joined[0])
        # causal_test is a judge-internal audit artifact and must not be exposed.
        self.assertNotIn("causal_test", joined[0])

    def test_missing_tmdb_id_in_judge_scores_is_filtered_out(self) -> None:
        # A candidate absent from judge scores has judge_score=None, which is
        # filtered out entirely (same cutoff as daily_batch briefing).
        candidates = [_candidate(999999, "Unscored Movie")]
        judge_scores = _judge_payload([_judge_entry("1083324", "Other Movie")])

        joined = _join_judge_scores(candidates, judge_scores)

        self.assertEqual(joined, [])

    def test_empty_judge_scores_dict_does_not_raise_and_filters_all(self) -> None:
        candidates = [_candidate(1083324, "A Mother's Special Love")]
        joined = _join_judge_scores(candidates, {})
        self.assertEqual(joined, [])

    def test_judge_score_zero_is_filtered_out(self) -> None:
        candidates = [
            _candidate(1, "Zero Score Movie"),
            _candidate(2, "Kept Movie"),
        ]
        judge_scores = _judge_payload(
            [
                _judge_entry("1", "Zero Score Movie", score=0),
                _judge_entry("2", "Kept Movie", score=1),
            ]
        )

        joined = _join_judge_scores(candidates, judge_scores)

        self.assertEqual(len(joined), 1)
        self.assertEqual(joined[0]["tmdb_id"], 2)

    def test_sorted_descending_by_judge_score(self) -> None:
        candidates = [
            _candidate(1, "Low"),
            _candidate(2, "High"),
            _candidate(3, "Mid"),
        ]
        judge_scores = _judge_payload(
            [
                _judge_entry("1", "Low", score=1),
                _judge_entry("2", "High", score=3),
                _judge_entry("3", "Mid", score=2),
            ]
        )

        joined = _join_judge_scores(candidates, judge_scores)

        self.assertEqual([c["tmdb_id"] for c in joined], [2, 3, 1])
        self.assertEqual([c["judge_score"] for c in joined], [3, 2, 1])

    def test_tied_score_keeps_original_retrieve_order_stable(self) -> None:
        candidates = [
            _candidate(1, "First"),
            _candidate(2, "Second"),
            _candidate(3, "Third"),
        ]
        judge_scores = _judge_payload(
            [
                _judge_entry("1", "First", score=1),
                _judge_entry("2", "Second", score=1),
                _judge_entry("3", "Third", score=1),
            ]
        )

        joined = _join_judge_scores(candidates, judge_scores)

        self.assertEqual([c["tmdb_id"] for c in joined], [1, 2, 3])

    def test_zh_cache_joins_overview_and_rationale_translations(self) -> None:
        candidates = [_candidate(1083324, "Movie", overview="An overview.")]
        judge_scores = _judge_payload(
            [_judge_entry("1083324", "Movie", score=1, rationale="some rationale")]
        )
        zh_cache = {
            "overview": {"An overview.": "一段简介。"},
            "rationale": {"some rationale": "一些理由。"},
        }

        joined = _join_judge_scores(candidates, judge_scores, zh_cache)

        self.assertEqual(joined[0]["overview_zh"], "一段简介。")
        self.assertEqual(joined[0]["judge_rationale_zh"], "一些理由。")

    def test_zh_cache_miss_falls_back_to_empty_string(self) -> None:
        candidates = [_candidate(1083324, "Movie", overview="Untranslated overview.")]
        judge_scores = _judge_payload(
            [_judge_entry("1083324", "Movie", score=1, rationale="Untranslated rationale.")]
        )
        zh_cache = {"overview": {}, "rationale": {}}

        joined = _join_judge_scores(candidates, judge_scores, zh_cache)

        self.assertEqual(joined[0]["overview_zh"], "")
        self.assertEqual(joined[0]["judge_rationale_zh"], "")

    def test_missing_zh_cache_does_not_raise(self) -> None:
        candidates = [_candidate(1083324, "Movie")]
        judge_scores = _judge_payload([_judge_entry("1083324", "Movie", score=1)])

        joined = _join_judge_scores(candidates, judge_scores, None)

        self.assertEqual(joined[0]["overview_zh"], "")
        self.assertEqual(joined[0]["judge_rationale_zh"], "")


class LoadZhCacheTests(unittest.TestCase):
    def test_missing_cache_file_returns_empty_dict(self) -> None:
        with TemporaryDirectory() as tmp:
            date_dir = Path(tmp) / "2026-07-06"
            date_dir.mkdir()
            self.assertEqual(_load_zh_cache(date_dir), {})

    def test_reads_existing_cache_file(self) -> None:
        with TemporaryDirectory() as tmp:
            date_dir = Path(tmp) / "2026-07-06"
            date_dir.mkdir()
            cache = {
                "version": 1,
                "news_body": {"Hello.": "你好。"},
                "news_title": {"Title": "标题"},
                "overview": {},
                "rationale": {},
            }
            _write_json(date_dir / "briefing.zh.translations.json", cache)

            loaded = _load_zh_cache(date_dir)
            self.assertEqual(loaded["news_body"]["Hello."], "你好。")
            self.assertEqual(loaded["news_title"]["Title"], "标题")

    def test_malformed_cache_file_does_not_raise(self) -> None:
        with TemporaryDirectory() as tmp:
            date_dir = Path(tmp) / "2026-07-06"
            date_dir.mkdir()
            (date_dir / "briefing.zh.translations.json").write_text("not json", encoding="utf-8")

            self.assertEqual(_load_zh_cache(date_dir), {})


class BuildPanelDataTests(unittest.TestCase):
    def _write_mini_batch(self, root: Path, date: str) -> None:
        date_dir = root / date

        # News 1: full retrieve + judge, one candidate missing from judge scores
        # (filtered out), one candidate scored and kept.
        news1_dir = date_dir / "01-first-news"
        _write_json(news1_dir / "news.json", _news_payload("First headline"))
        _write_json(
            news1_dir / "retrieve.json",
            _retrieve_payload(
                [
                    _candidate(1083324, "Scored Movie", hit_sources=[{"agent_id": "THE-INNOCENT"}, {"agent_id": "THE-HERO"}]),
                    _candidate(999999, "Unscored Movie"),
                ]
            ),
        )
        _write_json(
            news1_dir / "llm-judge-scores.json",
            _judge_payload([_judge_entry("1083324", "Scored Movie", score=1)]),
        )

        # News 2 (deliberately created out of NN order on disk): no judge file at all
        # -> its only candidate is filtered out entirely.
        news2_dir = date_dir / "02-second-news"
        _write_json(news2_dir / "news.json", _news_payload("Second headline"))
        _write_json(
            news2_dir / "retrieve.json",
            _retrieve_payload([_candidate(313, "No Judge File Movie")]),
        )

        # Non-news noise: panel.json itself and a stray file must be ignored.
        _write_json(date_dir / "panel.json", {"stale": True})

    def test_join_slim_fields_and_order(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_mini_batch(root, "2026-07-06")

            panel = build_panel_data("2026-07-06", batch_root=root)

            self.assertEqual(panel["date"], "2026-07-06")
            self.assertIn("generated_at", panel)
            self.assertEqual(len(panel["news_items"]), 2)

            first, second = panel["news_items"]
            self.assertEqual(first["index"], 1)
            self.assertEqual(first["slug"], "01-first-news")
            self.assertEqual(second["index"], 2)
            self.assertEqual(second["slug"], "02-second-news")

            # Unscored candidate (judge_score=None) is filtered out entirely.
            self.assertEqual(len(first["candidates"]), 1)
            scored = first["candidates"][0]
            self.assertEqual(scored["tmdb_id"], 1083324)
            self.assertEqual(scored["judge_score"], 1)
            self.assertEqual(scored["resonance_agents"], ["THE-INNOCENT", "THE-HERO"])
            self.assertNotIn("causal_test", scored)

            # News dir with no llm-judge-scores.json at all: its only candidate
            # is unscored (None) and therefore filtered out, leaving an empty list.
            self.assertEqual(second["candidates"], [])

    def test_news_items_sorted_ascending_by_nn_prefix(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            date_dir = root / "2026-07-06"

            # Write dirs in reverse disk order to prove sort is by NN, not creation order.
            for slug, title in [("10-tenth", "Tenth"), ("02-second", "Second"), ("01-first", "First")]:
                news_dir = date_dir / slug
                _write_json(news_dir / "news.json", _news_payload(title))
                _write_json(news_dir / "retrieve.json", _retrieve_payload([]))

            panel = build_panel_data("2026-07-06", batch_root=root)
            slugs = [item["slug"] for item in panel["news_items"]]
            self.assertEqual(slugs, ["01-first", "02-second", "10-tenth"])

    def test_non_news_directories_are_ignored(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            date_dir = root / "2026-07-06"
            _write_json(date_dir / "01-real-news" / "news.json", _news_payload())
            _write_json(date_dir / "01-real-news" / "retrieve.json", _retrieve_payload([]))
            # A directory without news.json must not be treated as a news item.
            (date_dir / "personas-leftover").mkdir(parents=True)

            panel = build_panel_data("2026-07-06", batch_root=root)
            self.assertEqual(len(panel["news_items"]), 1)

    def test_candidates_sorted_descending_by_judge_score_end_to_end(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            date_dir = root / "2026-07-06"
            news_dir = date_dir / "01-news"
            _write_json(news_dir / "news.json", _news_payload())
            _write_json(
                news_dir / "retrieve.json",
                _retrieve_payload(
                    [
                        _candidate(1, "Low"),
                        _candidate(2, "High"),
                        _candidate(3, "Zero"),
                    ]
                ),
            )
            _write_json(
                news_dir / "llm-judge-scores.json",
                _judge_payload(
                    [
                        _judge_entry("1", "Low", score=1),
                        _judge_entry("2", "High", score=2),
                        _judge_entry("3", "Zero", score=0),
                    ]
                ),
            )

            panel = build_panel_data("2026-07-06", batch_root=root)
            candidates = panel["news_items"][0]["candidates"]
            # judge_score=0 is filtered; remaining candidates sorted descending.
            self.assertEqual([c["tmdb_id"] for c in candidates], [2, 1])

    def test_news_title_and_description_zh_joined_from_cache(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            date_dir = root / "2026-07-06"
            news_dir = date_dir / "01-news"
            _write_json(
                news_dir / "news.json",
                _news_payload(title="English Title", description="English body."),
            )
            _write_json(news_dir / "retrieve.json", _retrieve_payload([]))
            _write_json(
                date_dir / "briefing.zh.translations.json",
                {
                    "version": 1,
                    "news_title": {"English Title": "中文标题"},
                    "news_body": {"English body.": "中文正文。"},
                    "overview": {},
                    "rationale": {},
                },
            )

            panel = build_panel_data("2026-07-06", batch_root=root)
            news = panel["news_items"][0]["news"]
            self.assertEqual(news["title"], "English Title")
            self.assertEqual(news["title_zh"], "中文标题")
            self.assertEqual(news["description"], "English body.")
            self.assertEqual(news["description_zh"], "中文正文。")

    def test_missing_zh_translation_cache_file_does_not_raise(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            date_dir = root / "2026-07-06"
            news_dir = date_dir / "01-news"
            _write_json(news_dir / "news.json", _news_payload())
            _write_json(news_dir / "retrieve.json", _retrieve_payload([]))

            panel = build_panel_data("2026-07-06", batch_root=root)
            news = panel["news_items"][0]["news"]
            self.assertEqual(news["title_zh"], "")
            self.assertEqual(news["description_zh"], "")


class WritePanelJsonTests(unittest.TestCase):
    def test_writes_panel_json_and_returns_path(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            date_dir = root / "2026-07-06"
            _write_json(date_dir / "01-first-news" / "news.json", _news_payload())
            _write_json(date_dir / "01-first-news" / "retrieve.json", _retrieve_payload([]))

            panel_path = write_panel_json("2026-07-06", batch_root=root)

            self.assertEqual(panel_path, date_dir / "panel.json")
            self.assertTrue(panel_path.is_file())
            written = json.loads(panel_path.read_text(encoding="utf-8"))
            self.assertEqual(written["date"], "2026-07-06")


class ListAvailableDatesTests(unittest.TestCase):
    def test_returns_dates_in_descending_order(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            for date in ["2026-07-04", "2026-07-06", "2026-07-05"]:
                (root / date).mkdir()

            self.assertEqual(
                list_available_dates(batch_root=root),
                ["2026-07-06", "2026-07-05", "2026-07-04"],
            )

    def test_ignores_non_directory_entries(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "2026-07-06").mkdir()
            (root / "pool.json").write_text("{}", encoding="utf-8")

            self.assertEqual(list_available_dates(batch_root=root), ["2026-07-06"])

    def test_missing_root_returns_empty_list(self) -> None:
        with TemporaryDirectory() as tmp:
            missing_root = Path(tmp) / "does-not-exist"
            self.assertEqual(list_available_dates(batch_root=missing_root), [])


if __name__ == "__main__":
    unittest.main()