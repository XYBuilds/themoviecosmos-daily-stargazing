"""Unit tests for Phase 6.2 scripts/main.py daily briefing pipeline."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts.main import build_daily_briefing, main


def _fake_news_dict() -> dict:
    return {
        "title": "Test headline",
        "description": "Test description.",
        "pub_time": "2026-07-04T00:00:00Z",
        "source_name": "Example Wire",
        "url": "https://example.com/article/1",
    }


def _fake_retrieve_result(*, with_oracle: bool = False) -> dict:
    result = {
        "per_agent": [],
        "candidates": [
            {
                "title": "Prod Movie",
                "release_year": 2020,
                "tmdb_id": 42,
                "quality_candidate": True,
                "quality_reason": "objective_match=1",
                "convergence_persona_count": 2,
                "convergent_score": 12.5,
                "match_diagnostics": {},
                "also_baseline": False,
                "similarity": 0.8,
                "genres": "drama",
                "language": "en",
                "overview": "An overview.",
                "movie_url": "https://themoviecosmos.com/movie/42",
                "hit_sources": [{"agent_id": "The-Hero", "pseudo_id": "p1", "fragments": ["f1"]}],
            }
        ],
        "human_candidates": [],
        "audit_pool": [],
        "funnel": {},
        "a1_oracle": None,
        "oracle_comparison": None,
        "divergence": {},
        "meta": {"query_count": 1, "candidate_count": 1},
    }
    if with_oracle:
        result["a1_oracle"] = {
            "raw_hit_count": 3,
            "hit_tmdb_ids": [42, 999],
        }
        result["oracle_comparison"] = {
            "oracle_only": [999],
            "production_only": [42],
        }
    return result


class BuildDailyBriefingA1IsolationTests(unittest.TestCase):
    """A1 oracle data must never leak into the candidate list / C1 input section."""

    def test_a1_only_appears_in_oracle_appendix(self) -> None:
        retrieve_result = _fake_retrieve_result(with_oracle=True)
        md = build_daily_briefing("2026-07-04", _fake_news_dict(), [], retrieve_result)

        candidates_section = md.split("## 候选星轨", 1)[1].split("# errors", 1)[0]
        appendix_section = md.split("## 附录 · A1 Reality Recorder", 1)[1]

        # The A1-only oracle hit (999) must not appear in the candidates block.
        self.assertNotIn("999", candidates_section)
        # It must appear in the oracle appendix.
        self.assertIn("999", appendix_section)
        # Production candidate 42 appears in candidates (its own section) and
        # is also referenced in the appendix comparison — that's expected since
        # oracle_comparison summarizes overlap, not a leak of A1 data itself.
        self.assertIn("Prod Movie", candidates_section)

    def test_no_oracle_data_renders_placeholder(self) -> None:
        retrieve_result = _fake_retrieve_result(with_oracle=False)
        md = build_daily_briefing("2026-07-04", _fake_news_dict(), [], retrieve_result)
        appendix_section = md.split("## 附录 · A1 Reality Recorder", 1)[1]
        self.assertIn("无 A1 oracle 数据", appendix_section)

    def test_movie_url_not_hand_built(self) -> None:
        retrieve_result = _fake_retrieve_result()
        md = build_daily_briefing("2026-07-04", _fake_news_dict(), [], retrieve_result)
        self.assertIn("https://themoviecosmos.com/movie/42", md)

    def test_review_copies_rendered_under_candidate(self) -> None:
        retrieve_result = _fake_retrieve_result()
        md = build_daily_briefing(
            "2026-07-04",
            _fake_news_dict(),
            [],
            retrieve_result,
            review_copies=[{"tmdb_id": 42, "copy": "中文文案示例"}],
        )
        self.assertIn("中文文案示例", md)


class MainCliArgTests(unittest.TestCase):
    def test_no_args_prints_usage_and_exits_nonzero(self) -> None:
        code = main([])
        self.assertNotEqual(code, 0)

    def test_missing_input_source_exits_nonzero(self) -> None:
        code = main(["--date", "2026-07-04"])
        self.assertNotEqual(code, 0)


class MainCliFullFlowTests(unittest.TestCase):
    """Full pipeline with mocked news/deconstruct/expand/persona/retrieve/C1."""

    def _patched_run(self, argv: list[str], *, briefing_dir: Path):
        fake_news = type(
            "FakeNews",
            (),
            {
                "title": "Test",
                "description": "Test description.",
                "pub_time": "2026-07-04T00:00:00Z",
                "url": "https://example.com/article/1",
                "source_name": "Example Wire",
            },
        )()

        async def fake_pipeline(news, *, provider, run_options):
            return _fake_news_dict(), [], _fake_retrieve_result()

        with (
            patch("scripts.main.resolve_news", return_value=fake_news),
            patch("scripts.main.run_daily_pipeline", side_effect=fake_pipeline),
            patch("scripts.main.resolve_briefing_path", side_effect=lambda date, out_dir=None: briefing_dir / f"{date}.md"),
        ):
            return main(argv)

    def test_news_file_flow_no_copy_writes_briefing(self) -> None:
        with TemporaryDirectory() as tmp:
            briefing_dir = Path(tmp)
            code = self._patched_run(
                [
                    "--news-file",
                    "tests/sample_news.json",
                    "--no-copy",
                    "--personas",
                    "2",
                    "--date",
                    "2026-07-04",
                ],
                briefing_dir=briefing_dir,
            )
            self.assertEqual(code, 0)
            briefing_path = briefing_dir / "2026-07-04.md"
            self.assertTrue(briefing_path.is_file())
            content = briefing_path.read_text(encoding="utf-8")
            self.assertIn("每日星轨观测 · 2026-07-04", content)
            self.assertIn("候选星轨", content)

            candidates_path = briefing_dir / "2026-07-04_candidates.json"
            self.assertTrue(candidates_path.is_file())
            payload = json.loads(candidates_path.read_text(encoding="utf-8"))
            self.assertIn("candidates", payload)

    def test_date_override_used_for_output_path(self) -> None:
        with TemporaryDirectory() as tmp:
            briefing_dir = Path(tmp)
            code = self._patched_run(
                [
                    "--news-file",
                    "tests/sample_news.json",
                    "--no-copy",
                    "--personas",
                    "1",
                    "--date",
                    "2099-01-01",
                ],
                briefing_dir=briefing_dir,
            )
            self.assertEqual(code, 0)
            self.assertTrue((briefing_dir / "2099-01-01.md").is_file())

    def test_force_protection_blocks_overwrite_without_force(self) -> None:
        with TemporaryDirectory() as tmp:
            briefing_dir = Path(tmp)
            briefing_dir.mkdir(parents=True, exist_ok=True)
            existing = briefing_dir / "2026-07-04.md"
            existing.write_text("existing content", encoding="utf-8")

            code = self._patched_run(
                [
                    "--news-file",
                    "tests/sample_news.json",
                    "--no-copy",
                    "--personas",
                    "1",
                    "--date",
                    "2026-07-04",
                ],
                briefing_dir=briefing_dir,
            )
            self.assertNotEqual(code, 0)
            # Original content must be untouched (no silent overwrite).
            self.assertEqual(existing.read_text(encoding="utf-8"), "existing content")

    def test_force_flag_allows_overwrite(self) -> None:
        with TemporaryDirectory() as tmp:
            briefing_dir = Path(tmp)
            briefing_dir.mkdir(parents=True, exist_ok=True)
            existing = briefing_dir / "2026-07-04.md"
            existing.write_text("existing content", encoding="utf-8")

            code = self._patched_run(
                [
                    "--news-file",
                    "tests/sample_news.json",
                    "--no-copy",
                    "--personas",
                    "1",
                    "--date",
                    "2026-07-04",
                    "--force",
                ],
                briefing_dir=briefing_dir,
            )
            self.assertEqual(code, 0)
            self.assertNotEqual(existing.read_text(encoding="utf-8"), "existing content")


if __name__ == "__main__":
    unittest.main()