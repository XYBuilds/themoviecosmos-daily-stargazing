"""Unit tests for Phase 8.1 review_panel/build_data.py."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from review_panel.build_data import (
    _extract_resonance_agents,
    _join_judge_scores,
    build_panel_data,
    list_available_dates,
    write_panel_json,
)


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")


def _news_payload(title: str = "Headline") -> dict:
    return {
        "title": title,
        "description": "A description.",
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
) -> dict:
    return {
        "tmdb_id": tmdb_id,
        "title": title,
        "overview": "An overview.",
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


def _judge_entry(tmdb_id: str, title: str, score: int = 1) -> dict:
    return {
        "run_id": "run",
        "tmdb_id": tmdb_id,
        "title": title,
        "judge_score": score,
        "judge_resonance_type": "表层沾边",
        "rationale": "some rationale",
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
        self.assertEqual(joined[0]["causal_test"], "")

    def test_slims_fields_to_schema_only(self) -> None:
        candidates = [_candidate(1083324, "A Mother's Special Love", hit_sources=[{"agent_id": "THE-INNOCENT"}])]
        joined = _join_judge_scores(candidates, _judge_payload([]))

        expected_keys = {
            "tmdb_id",
            "title",
            "release_year",
            "overview",
            "genres",
            "language",
            "similarity",
            "movie_url",
            "poster_path",
            "resonance_agents",
            "judge_score",
            "judge_resonance_type",
            "judge_rationale",
            "causal_test",
        }
        self.assertEqual(set(joined[0].keys()), expected_keys)
        self.assertNotIn("triggered_by", joined[0])
        self.assertNotIn("hit_sources", joined[0])
        self.assertNotIn("also_baseline", joined[0])

    def test_missing_tmdb_id_in_judge_scores_falls_back_to_none(self) -> None:
        candidates = [_candidate(999999, "Unscored Movie")]
        judge_scores = _judge_payload([_judge_entry("1083324", "Other Movie")])

        joined = _join_judge_scores(candidates, judge_scores)

        self.assertIsNone(joined[0]["judge_score"])
        self.assertIsNone(joined[0]["judge_resonance_type"])
        self.assertIsNone(joined[0]["judge_rationale"])
        self.assertIsNone(joined[0]["causal_test"])

    def test_empty_judge_scores_dict_does_not_raise(self) -> None:
        candidates = [_candidate(1083324, "A Mother's Special Love")]
        joined = _join_judge_scores(candidates, {})
        self.assertIsNone(joined[0]["judge_score"])


class BuildPanelDataTests(unittest.TestCase):
    def _write_mini_batch(self, root: Path, date: str) -> None:
        date_dir = root / date

        # News 1: full retrieve + judge, one candidate missing from judge scores.
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

        # News 2 (deliberately created out of NN order on disk): no judge file at all.
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

            scored, unscored = first["candidates"]
            self.assertEqual(scored["tmdb_id"], 1083324)
            self.assertEqual(scored["judge_score"], 1)
            self.assertEqual(scored["resonance_agents"], ["THE-INNOCENT", "THE-HERO"])

            # Candidate absent from judge scores must fall back to empty, not raise.
            self.assertEqual(unscored["tmdb_id"], 999999)
            self.assertIsNone(unscored["judge_score"])

            # News dir with no llm-judge-scores.json at all must also degrade gracefully.
            no_judge_candidate = second["candidates"][0]
            self.assertIsNone(no_judge_candidate["judge_score"])
            self.assertIsNone(no_judge_candidate["judge_resonance_type"])

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