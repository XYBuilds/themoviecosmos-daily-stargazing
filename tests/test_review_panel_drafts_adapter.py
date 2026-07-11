"""Unit tests for Phase 10.3 review_panel/drafts_adapter.py."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

from scripts import compose
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


def _make_fake_publish(calls: list[dict], warnings_by_perspective: dict | None = None):
    def _fake_publish(
        candidate,
        news,
        *,
        provider=None,
        judge=None,
        platform=None,
        persona_perspective="",
        judge_llm_call=None,
        max_body_retries=1,
    ):
        calls.append(
            {
                "persona_perspective": persona_perspective,
                "judge_llm_call": judge_llm_call,
                "max_body_retries": max_body_retries,
            }
        )
        draft = {
            "tmdb_id": candidate["tmdb_id"],
            "headline": f"标题-{len(calls)}",
            "body": f"正文-{persona_perspective}",
        }
        if warnings_by_perspective and persona_perspective in warnings_by_perspective:
            draft["warnings"] = warnings_by_perspective[persona_perspective]
        return draft

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
            # 池首是中性默认稿（混合视角），其后才是 triggered_by 各 persona。
            self.assertEqual(len(pool), 4)
            self.assertEqual(
                [d["draft_id"] for d in pool],
                ["混合视角", "The-Sage", "The-Explorer", "The-Innocent"],
            )
            self.assertEqual(
                [c["persona_perspective"] for c in calls],
                ["", "视角[The-Sage]", "视角[The-Explorer]", "视角[The-Innocent]"],
            )

    def test_fanout_prepends_neutral_default_draft_at_index_0(self) -> None:
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
            # 第 0 条 = 中性默认稿：draft_id「混合视角」+ 空 persona_perspective 注入。
            self.assertEqual(pool[0]["draft_id"], "混合视角")
            self.assertEqual(calls[0]["persona_perspective"], "")
            # 其余顺序仍是 triggered_by 去重后的 persona。
            self.assertEqual(
                [d["draft_id"] for d in pool[1:]],
                ["The-Sage", "The-Explorer", "The-Innocent"],
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
            self.assertEqual(len(pool), 9)
            self.assertEqual(
                [d["draft_id"] for d in pool],
                [
                    "混合视角",
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
            self.assertEqual(len(pool), 9)
            self.assertEqual(
                [d["draft_id"] for d in pool],
                [
                    "混合视角",
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
            self.assertEqual(len(calls), 9)

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

    def test_fanout_keeps_warnings_in_pool_entry_when_present(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "02-slug")
            calls: list[dict] = []
            warnings = {"body_lint": ["hard_transition"], "fabrication": []}

            run_fanout(
                "2026-07-06",
                "02-slug",
                _TMDB_ID,
                batch_root=tmp_path,
                run_publish=_make_fake_publish(
                    calls, warnings_by_perspective={"视角[The-Sage]": warnings}
                ),
                load_persona_perspective=_fake_perspective,
            )

            pool = _read_pool(tmp_path, "2026-07-06", "02-slug")
            by_id = {d["draft_id"]: d for d in pool}
            self.assertEqual(by_id["The-Sage"]["warnings"], warnings)
            # 其余没有 warnings 的条目不应带 warnings 键。
            self.assertNotIn("warnings", by_id["混合视角"])
            self.assertNotIn("warnings", by_id["The-Explorer"])
            self.assertNotIn("warnings", by_id["The-Innocent"])

    def test_fanout_passes_judge_llm_call_and_max_body_retries_through(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _make_batch(tmp_path, "2026-07-06", "02-slug")
            calls: list[dict] = []
            sentinel_judge = object()

            run_fanout(
                "2026-07-06",
                "02-slug",
                _TMDB_ID,
                batch_root=tmp_path,
                run_publish=_make_fake_publish(calls),
                load_persona_perspective=_fake_perspective,
                judge_llm_call=sentinel_judge,
                max_body_retries=3,
            )

            self.assertTrue(calls)
            for call in calls:
                self.assertIs(call["judge_llm_call"], sentinel_judge)
                self.assertEqual(call["max_body_retries"], 3)

    def test_fanout_defaults_judge_llm_call_to_none(self) -> None:
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

            self.assertTrue(calls)
            for call in calls:
                self.assertIsNone(call["judge_llm_call"])
                self.assertEqual(call["max_body_retries"], 1)


class MakeRealLlmCallTests(unittest.TestCase):
    def test_factory_closure_calls_client_and_returns_content(self) -> None:
        captured: dict[str, Any] = {}

        class _FakeMessage:
            content = "  已生成正文  "

        class _FakeChoice:
            message = _FakeMessage()

        class _FakeResponse:
            choices = [_FakeChoice()]

        class _FakeCompletions:
            def create(self, *, model, messages):
                captured["model"] = model
                captured["messages"] = messages
                return _FakeResponse()

        class _FakeChat:
            completions = _FakeCompletions()

        class _FakeClient:
            chat = _FakeChat()

        import unittest.mock as mock

        with mock.patch.object(compose, "load_env", lambda: None), mock.patch.object(
            compose, "get_llm_client", lambda provider: _FakeClient()
        ), mock.patch.object(compose, "_model_name", lambda provider: "fake-model"):
            llm_call = compose.make_real_llm_call(provider="mimo")
            result = llm_call("判断这段正文是否虚构")

        self.assertEqual(result, "已生成正文")
        self.assertEqual(captured["model"], "fake-model")
        self.assertEqual(captured["messages"][1]["content"], "判断这段正文是否虚构")


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
            # 池 = 中性默认(1) + 3 persona + 合并稿(1) = 5
            self.assertEqual(len(pool), 5)
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
            # 池 = 中性默认(1) + 3 persona + 两个合并变体(2) = 6
            self.assertEqual(len(pool), 6)

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