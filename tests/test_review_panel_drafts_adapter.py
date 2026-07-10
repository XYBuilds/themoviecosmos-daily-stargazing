"""Unit tests for Phase 10.3 review_panel/drafts_adapter.py."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.compose import build_header_projection, render_movie_header
from review_panel.drafts_adapter import (
    combine_bodies,
    run_combine,
    run_fanout,
)
from review_panel.publish_adapter import run_adapter

_TMDB_ID = 355196
_TRIGGERED_BY = ["THE-SAGE", "THE-EXPLORER", "THE-INNOCENT"]


def _write_news(news_dir: Path) -> None:
    payload = {
        "title": "Test headline",
        "description": "Test description.",
        "url": "https://example.com/article/1",
    }
    (news_dir / "news.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


def _write_retrieve(news_dir: Path, triggered_by: list[str], tmdb_id: int = _TMDB_ID) -> None:
    payload = {
        "candidates": [
            {
                "tmdb_id": tmdb_id,
                "title": "Some Movie",
                "overview": "An overview.",
                "genres": "Drama",
                "release_year": 2025,
                "movie_url": f"https://themoviecosmos.com/movie/{tmdb_id}",
                "triggered_by": triggered_by,
            }
        ]
    }
    (news_dir / "retrieve.json").write_text(
        json.dumps(payload, ensure_ascii=False), encoding="utf-8"
    )


def _make_batch(
    tmp_path: Path,
    date: str,
    slug: str,
    triggered_by: list[str] | None = None,
    tmdb_id: int = _TMDB_ID,
) -> None:
    news_dir = tmp_path / date / slug
    news_dir.mkdir(parents=True)
    resolved = _TRIGGERED_BY if triggered_by is None else triggered_by
    _write_news(news_dir)
    _write_retrieve(news_dir, resolved, tmdb_id=tmdb_id)


def _fake_perspective(persona_id: str) -> str:
    normalized = "-".join(part.capitalize() for part in persona_id.split("-"))
    return f"视角[{normalized}]"


def _make_fake_publish(calls: list[dict]):
    def _fake_publish(
        candidate,
        news,
        *,
        provider=None,
        judge=None,
        platform=None,
        persona_perspective="",
    ):
        calls.append({"persona_perspective": persona_perspective})
        return {
            "tmdb_id": candidate["tmdb_id"],
            "headline": f"标题-{len(calls)}",
            "body": f"正文-{persona_perspective}",
        }

    return _fake_publish


def _read_pool(tmp_path: Path, date: str, slug: str, platform: str = "xiaohongshu") -> list[dict]:
    path = tmp_path / date / f"{slug}_drafts_{platform}.json"
    return json.loads(path.read_text(encoding="utf-8"))


class FanoutTests(unittest.TestCase):
    def test_fanout_count_matches_deduped_triggered_by(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "02-slug")
            calls: list[dict] = []

            run_fanout(
                "2026-07-06",
                "02-slug",
                _TMDB_ID,
                batch_root=tmp_path,
                run_publish=_make_fake_publish(calls),
                load_persona_perspective=_fake_perspective,
            )

            pool = _read_pool(tmp_path, "2026-07-06", "02-slug")
            self.assertEqual(len(pool), 3)
            self.assertEqual(
                [d["draft_id"] for d in pool],
                ["The-Sage", "The-Explorer", "The-Innocent"],
            )
            self.assertEqual(
                [c["persona_perspective"] for c in calls],
                ["视角[The-Sage]", "视角[The-Explorer]", "视角[The-Innocent]"],
            )

    def test_fanout_falls_back_to_persona_semantic_hit_sources_when_triggered_by_is_truncated(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            all_personas = [
                "THE-CAREGIVER",
                "THE-INNOCENT",
                "THE-OUTLAW",
                "THE-EVERYMAN",
                "THE-HERO",
                "THE-EXPLORER",
                "THE-RULER",
                "THE-SAGE",
            ]
            _make_batch(
                tmp_path,
                "2026-07-06",
                "02-slug",
                triggered_by=["THE-INNOCENT", "THE-CAREGIVER", "THE-OUTLAW"],
            )
            news_dir = tmp_path / "2026-07-06" / "02-slug"
            retrieve = json.loads((news_dir / "retrieve.json").read_text(encoding="utf-8"))
            retrieve["candidates"][0]["hit_sources"] = [
                {
                    "agent_id": persona,
                    "pseudo_id": f"{persona}-p1",
                    "search_unit_kind": "persona-semantic",
                    "similarity": 0.9 - idx * 0.01,
                }
                for idx, persona in enumerate(all_personas)
            ]
            (news_dir / "retrieve.json").write_text(
                json.dumps(retrieve, ensure_ascii=False, indent=2), encoding="utf-8"
            )

            calls: list[dict] = []
            run_fanout(
                "2026-07-06",
                "02-slug",
                _TMDB_ID,
                batch_root=tmp_path,
                run_publish=_make_fake_publish(calls),
                load_persona_perspective=_fake_perspective,
            )

            pool = _read_pool(tmp_path, "2026-07-06", "02-slug")
            self.assertEqual(len(pool), 8)
            self.assertEqual(
                [d["draft_id"] for d in pool],
                [
                    "The-Innocent",
                    "The-Caregiver",
                    "The-Outlaw",
                    "The-Everyman",
                    "The-Hero",
                    "The-Explorer",
                    "The-Ruler",
                    "The-Sage",
                ],
            )
            calls: list[dict] = []
            run_fanout(
                "2026-07-06",
                "02-slug",
                _TMDB_ID,
                batch_root=tmp_path,
                run_publish=_make_fake_publish(calls),
                load_persona_perspective=_fake_perspective,
            )

            pool = _read_pool(tmp_path, "2026-07-06", "02-slug")
            self.assertEqual(len(pool), 8)
            self.assertEqual(
                [d["draft_id"] for d in pool],
                [
                    "The-Innocent",
                    "The-Caregiver",
                    "The-Outlaw",
                    "The-Everyman",
                    "The-Hero",
                    "The-Explorer",
                    "The-Ruler",
                    "The-Sage",
                ],
            )
            self.assertEqual(len(calls), 8)

    def test_fanout_and_publish_share_same_deterministic_header(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "02-slug", triggered_by=[])
            with self.assertRaises(ValueError):
                run_fanout(
                    "2026-07-06",
                    "02-slug",
                    _TMDB_ID,
                    batch_root=tmp_path,
                    run_publish=_make_fake_publish([]),
                    load_persona_perspective=_fake_perspective,
                )

    def test_fanout_overwrites_pool(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "02-slug")
            pool_path = tmp_path / "2026-07-06" / "02-slug_drafts_xiaohongshu.json"
            pool_path.write_text(
                json.dumps([{"draft_id": "STALE", "headline": "x", "body": "y"}]),
                encoding="utf-8",
            )
            run_fanout(
                "2026-07-06",
                "02-slug",
                _TMDB_ID,
                batch_root=tmp_path,
                run_publish=_make_fake_publish([]),
                load_persona_perspective=_fake_perspective,
            )
            pool = _read_pool(tmp_path, "2026-07-06", "02-slug")
            self.assertNotIn("STALE", [d["draft_id"] for d in pool])


class CombineTests(unittest.TestCase):
    def _seed_pool(self, tmp_path: Path, date: str, slug: str) -> None:
        _make_batch(tmp_path, date, slug)
        run_fanout(
            date,
            slug,
            _TMDB_ID,
            batch_root=tmp_path,
            run_publish=_make_fake_publish([]),
            load_persona_perspective=_fake_perspective,
        )

    def test_combine_mode_a_appends_one_and_calls_run_publish(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._seed_pool(tmp_path, "2026-07-06", "02-slug")
            calls: list[dict] = []

            run_combine(
                "2026-07-06",
                "02-slug",
                _TMDB_ID,
                ["The-Sage", "The-Explorer"],
                combine_mode="A",
                batch_root=tmp_path,
                run_publish=_make_fake_publish(calls),
                load_persona_perspective=_fake_perspective,
            )

            pool = _read_pool(tmp_path, "2026-07-06", "02-slug")
            ids = [d["draft_id"] for d in pool]
            self.assertIn("The-Sage+The-Explorer", ids)
            self.assertEqual(len(pool), 4)
            self.assertEqual(len(calls), 1)
            self.assertIn("视角[The-Sage]", calls[0]["persona_perspective"])
            self.assertIn("视角[The-Explorer]", calls[0]["persona_perspective"])

    def test_combine_mode_b_pure_fusion_no_llm(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._seed_pool(tmp_path, "2026-07-06", "02-slug")
            calls: list[dict] = []

            def should_not_be_called(*a, **k):
                calls.append(k)
                raise AssertionError("route B must not call run_publish")

            run_combine(
                "2026-07-06",
                "02-slug",
                _TMDB_ID,
                ["The-Sage", "The-Explorer"],
                combine_mode="B",
                batch_root=tmp_path,
                run_publish=should_not_be_called,
                load_persona_perspective=_fake_perspective,
            )

            pool = _read_pool(tmp_path, "2026-07-06", "02-slug")
            self.assertEqual(len(calls), 0)
            self.assertIn("The-Sage+The-Explorer", [d["draft_id"] for d in pool])

    def test_combine_mode_both_appends_two_variants(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._seed_pool(tmp_path, "2026-07-06", "02-slug")

            run_combine(
                "2026-07-06",
                "02-slug",
                _TMDB_ID,
                ["The-Sage", "The-Explorer"],
                combine_mode="both",
                batch_root=tmp_path,
                run_publish=_make_fake_publish([]),
                load_persona_perspective=_fake_perspective,
            )

            pool = _read_pool(tmp_path, "2026-07-06", "02-slug")
            ids = [d["draft_id"] for d in pool]
            self.assertIn("The-Sage+The-Explorer#A", ids)
            self.assertIn("The-Sage+The-Explorer#B", ids)
            self.assertEqual(len(pool), 5)

    def test_combine_more_than_two_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._seed_pool(tmp_path, "2026-07-06", "02-slug")
            with self.assertRaises(ValueError):
                run_combine(
                    "2026-07-06",
                    "02-slug",
                    _TMDB_ID,
                    ["The-Sage", "The-Explorer", "The-Innocent"],
                    combine_mode="A",
                    batch_root=tmp_path,
                    run_publish=_make_fake_publish([]),
                    load_persona_perspective=_fake_perspective,
                )

    def test_combine_unknown_draft_id_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._seed_pool(tmp_path, "2026-07-06", "02-slug")
            with self.assertRaises(ValueError):
                run_combine(
                    "2026-07-06",
                    "02-slug",
                    _TMDB_ID,
                    ["The-Sage", "The-Nonexistent"],
                    combine_mode="A",
                    batch_root=tmp_path,
                    run_publish=_make_fake_publish([]),
                    load_persona_perspective=_fake_perspective,
                )

    def test_combine_preserves_existing_drafts(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            self._seed_pool(tmp_path, "2026-07-06", "02-slug")
            before = [d["draft_id"] for d in _read_pool(tmp_path, "2026-07-06", "02-slug")]

            run_combine(
                "2026-07-06",
                "02-slug",
                _TMDB_ID,
                ["The-Sage", "The-Explorer"],
                combine_mode="A",
                batch_root=tmp_path,
                run_publish=_make_fake_publish([]),
                load_persona_perspective=_fake_perspective,
            )

            after = [d["draft_id"] for d in _read_pool(tmp_path, "2026-07-06", "02-slug")]
            for original in before:
                self.assertIn(original, after)


class CombineBodiesPureFunctionTests(unittest.TestCase):
    def test_dedupes_shared_attribution_line(self) -> None:
        a = "「Some Movie」(2025) D\nA 的正文。"
        b = "「Some Movie」(2025) D\nB 的正文。"
        merged = combine_bodies(a, b)
        self.assertEqual(merged.count("「Some Movie」(2025) D"), 1)
        self.assertIn("A 的正文。", merged)
        self.assertIn("B 的正文。", merged)

    def test_empty_a_returns_b(self) -> None:
        self.assertEqual(combine_bodies("", "只有 B"), "只有 B")

    def test_empty_b_returns_a(self) -> None:
        self.assertEqual(combine_bodies("只有 A", ""), "只有 A")


if __name__ == "__main__":
    unittest.main()