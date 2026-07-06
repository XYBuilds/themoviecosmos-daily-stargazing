"""Unit tests for Phase 7.2 scripts/daily_batch.py orchestrator + checkpointing."""

from __future__ import annotations

import asyncio
import json
import time
import unittest
from contextlib import ExitStack
from dataclasses import dataclass, field
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from scripts.daily_batch import (
    BatchState,
    build_parser,
    init_batch_state,
    render_daily_batch_briefing,
    run_daily_batch,
    slugify,
    state_path,
    write_daily_batch_briefing,
)
from scripts.lib.run_options import RunOptions
from tests.smoke_daily_batch import build_parser as build_smoke_parser


def _fake_pool() -> list[dict[str, Any]]:
    return [
        {
            "url": "https://example.com/a",
            "title": "England Heatwave Grips the Nation Today",
            "pub_time": "2026-07-05T00:00:00Z",
            "description": "A longer description about the first story that is clearly sufficient.",
            "score": 3.0,
        },
        {
            "url": "https://example.com/b",
            "title": "Byzantine City Unearthed Reveals New Layers",
            "pub_time": "2026-07-05T00:00:00Z",
            "description": "A longer description about the second story that is clearly sufficient.",
            "score": 2.0,
        },
    ]


def _fake_deconstruction() -> dict[str, Any]:
    return {"who": [{"id": "who-1", "text": "someone"}]}


def _fake_retrieve_result() -> dict[str, Any]:
    return {
        "per_agent": [],
        "candidates": [
            {
                "title": "Prod Movie",
                "release_year": 2020,
                "tmdb_id": 42,
                "movie_url": "https://themoviecosmos.com/movie/42",
            }
        ],
        "human_candidates": [],
        "audit_pool": [],
        "funnel": {},
        "a1_oracle": None,
        "oracle_comparison": None,
        "divergence": {},
        "meta": {},
    }


@dataclass
class _FakePseudo:
    id: str = "pseudo-1"
    text: str = "a pseudo line"
    source: dict[str, Any] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)
    fit: float | None = None


@dataclass
class _FakePersonaResult:
    persona_id: str
    pseudos: list[Any] = field(default_factory=lambda: [_FakePseudo()])
    warnings: list[str] = field(default_factory=list)
    error: str | None = None
    overlay: Any = field(default_factory=lambda: SimpleNamespace(to_dict=lambda: {}))


@dataclass
class _FakeJudgeOutput:
    scores: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"version": 4, "calibration": {}, "scores": list(self.scores)}


@dataclass
class _FakeReviewResult:
    review_copies: list[Any] = field(default_factory=list)
    errors: list[dict[str, Any]] = field(default_factory=list)


def _fake_fetch_heat_pool(*, date=None, min_count=None, max_items=None, sections=None, out_dir=None):
    """Mimic heat_pool.fetch_heat_pool's real side effect of writing pool.json
    under out_dir/{date}/pool.json, so daily_batch's --resume path (which
    reads the pool back from disk) has something to load.
    """
    pool = _fake_pool()
    from scripts.heat_pool import pool_output_path

    pool_path = pool_output_path(date, out_dir)
    pool_path.parent.mkdir(parents=True, exist_ok=True)
    pool_path.write_text(json.dumps(pool), encoding="utf-8")
    return pool


def _apply_common_patches(stack: ExitStack, *, persona_side_effect=None, persona_ids=None) -> None:
    """Patch every LLM/network-touching function daily_batch calls, via an
    ExitStack so callers don't need to track patch ordering by hand.
    """
    persona_ids = persona_ids or ["The-Hero", "The-Sage"]

    stack.enter_context(patch("scripts.daily_batch.fetch_heat_pool", side_effect=_fake_fetch_heat_pool))
    stack.enter_context(
        patch("scripts.daily_batch.run_deconstruct", return_value={"deconstruction": _fake_deconstruction()})
    )
    stack.enter_context(patch("scripts.daily_batch.list_persona_ids", return_value=persona_ids))
    stack.enter_context(
        patch("scripts.daily_batch.retrieve_from_agents", return_value=_fake_retrieve_result())
    )
    stack.enter_context(
        patch(
            "scripts.daily_batch.pipeline_result_to_dict",
            side_effect=lambda result: {
                "persona_id": result.persona_id,
                "pseudos": [{"text": p.text} for p in result.pseudos],
                "warnings": result.warnings,
            },
        )
    )
    stack.enter_context(patch("scripts.daily_batch.compose.run_review", return_value=_FakeReviewResult()))
    stack.enter_context(patch("scripts.daily_batch.score_items", return_value=_FakeJudgeOutput(scores=[])))
    # run_expansion is imported lazily (`from scripts.expand import run_expansion`)
    # inside daily_batch's expand stage, so it must be patched at its source module.
    stack.enter_context(
        patch("scripts.expand.run_expansion", return_value={"expansion": {"fake": "expansion"}})
    )

    if persona_side_effect is not None:
        stack.enter_context(patch("scripts.daily_batch.run_persona_pipeline", side_effect=persona_side_effect))
    else:
        async def default_pipeline(persona_id, deconstruction, *, provider, expansion):
            return _FakePersonaResult(persona_id=persona_id)

        stack.enter_context(patch("scripts.daily_batch.run_persona_pipeline", side_effect=default_pipeline))



class SlugifyTests(unittest.TestCase):
    def test_lowercase_strips_punctuation_and_joins_words(self) -> None:
        self.assertEqual(
            slugify("England Heatwave Grips the Nation!"),
            "england-heatwave-grips-the-nation",
        )

    def test_limits_to_max_words(self) -> None:
        self.assertEqual(slugify("one two three four five six seven"), "one-two-three-four-five-six")

    def test_empty_title_falls_back_to_untitled(self) -> None:
        self.assertEqual(slugify(""), "untitled")
        self.assertEqual(slugify("!!!???"), "untitled")


class InitBatchStateTests(unittest.TestCase):
    def test_initializes_all_pending_items_from_pool(self) -> None:
        pool = _fake_pool()
        state = init_batch_state("2026-07-05", pool, "output/daily_batch/2026-07-05/pool.json")

        self.assertEqual(state.date, "2026-07-05")
        self.assertEqual(len(state.items), 2)
        for idx, item in enumerate(state.items):
            self.assertEqual(item.index, idx)
            self.assertEqual(item.status, "pending")
            self.assertIsNone(item.last_completed_stage)
            self.assertEqual(item.completed_personas, [])
        self.assertEqual(state.items[0].slug, "england-heatwave-grips-the-nation-today")

    def test_round_trips_through_dict(self) -> None:
        pool = _fake_pool()
        state = init_batch_state("2026-07-05", pool, "pool.json")
        restored = BatchState.from_dict(state.to_dict())
        self.assertEqual(restored.to_dict(), state.to_dict())



class ParserTests(unittest.TestCase):
    def test_build_parser_accepts_max_items(self) -> None:
        args = build_parser().parse_args(["--max-items", "1"])
        self.assertEqual(args.max_items, 1)
        self.assertIsNone(build_parser().parse_args([]).max_items)

    def test_parser_accepts_persona_concurrency(self) -> None:
        args = build_parser().parse_args(["--persona-concurrency", "12"])
        self.assertEqual(args.persona_concurrency, 12)
        self.assertEqual(build_parser().parse_args([]).persona_concurrency, 4)

    def test_smoke_parser_accepts_date_and_max_items(self) -> None:
        args = build_smoke_parser().parse_args(["--date", "2026-07-05-smoke-max1", "--max-items", "1"])
        self.assertEqual(args.date, "2026-07-05-smoke-max1")
        self.assertEqual(args.max_items, 1)

    def test_smoke_parser_accepts_persona_concurrency(self) -> None:
        args = build_smoke_parser().parse_args(["--persona-concurrency", "12"])
        self.assertEqual(args.persona_concurrency, 12)


class RunDailyBatchCheckpointTests(unittest.TestCase):
    """Full run: verify checkpoint file is written correctly after completion."""

    def test_max_items_limits_initial_state_even_when_pool_is_larger(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_dir = tmp_path / "output"
            state_dir = tmp_path / "state"

            with ExitStack() as stack:
                _apply_common_patches(stack)
                state = asyncio.run(
                    run_daily_batch(
                        date="2026-07-05",
                        max_items=1,
                        run_options=RunOptions(),
                        out_dir=out_dir,
                        base_state_dir=state_dir,
                    )
                )

            self.assertEqual(len(state.items), 1)
            self.assertEqual(state.items[0].index, 0)
            self.assertEqual(state.items[0].status, "done")
            saved_path = state_path("2026-07-05", state_dir)
            saved = BatchState.from_dict(json.loads(saved_path.read_text(encoding="utf-8")))
            self.assertEqual(len(saved.items), 1)
            self.assertEqual(state.items[0].slug, "england-heatwave-grips-the-nation-today")

    def test_daily_batch_raises_on_insufficient_description(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_dir = tmp_path / "output"
            state_dir = tmp_path / "state"

            bad_pool = [
                {"url": "https://example.com/a", "title": "A", "description": "", "pub_time": "2026-07-05T00:00:00Z"},
                {"url": "https://example.com/b", "title": "B", "description": "short enough?", "pub_time": "2026-07-05T00:00:00Z"},
                {"url": "https://example.com/c", "title": "C", "description": "This description is sufficiently long and informative for the batch.", "pub_time": "2026-07-05T00:00:00Z"},
            ]

            with ExitStack() as stack:
                _apply_common_patches(stack)
                stack.enter_context(patch("scripts.daily_batch.fetch_heat_pool", return_value=bad_pool))
                with self.assertRaisesRegex(ValueError, "insufficient description"):
                    asyncio.run(
                        run_daily_batch(
                            date="2026-07-05",
                            run_options=RunOptions(persona_limit=1, skip_expand=True),
                            out_dir=out_dir,
                            base_state_dir=state_dir,
                        )
                    )

            saved_path = state_path("2026-07-05", state_dir)
            self.assertTrue(saved_path.is_file())
            saved = BatchState.from_dict(json.loads(saved_path.read_text(encoding="utf-8")))
            self.assertEqual([item.status for item in saved.items], ["pending", "pending", "pending"])
            self.assertFalse((out_dir / "2026-07-05" / "01-a" / "deconstruct.json").exists())

    def test_resume_reprocesses_incomplete_done_item(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_dir = tmp_path / "output"
            state_dir = tmp_path / "state"

            pool = [
                {"url": "https://example.com/a", "title": "A", "description": "This description is sufficiently long and informative for the batch.", "pub_time": "2026-07-05T00:00:00Z"},
            ]
            state = init_batch_state("2026-07-05", pool, "output/daily_batch/2026-07-05/pool.json")
            state.items[0].status = "done"
            state.items[0].last_completed_stage = "done"
            pool_dir = out_dir / "2026-07-05"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_file = pool_dir / "pool.json"
            pool_file.write_text(json.dumps(pool), encoding="utf-8")
            state.pool_file = str(pool_file)
            state.save(state_path("2026-07-05", state_dir))

            called_personas: list[str] = []

            async def track_pipeline(persona_id, deconstruction, *, provider, expansion):
                called_personas.append(persona_id)
                return _FakePersonaResult(persona_id=persona_id)

            with ExitStack() as stack:
                _apply_common_patches(stack, persona_side_effect=track_pipeline, persona_ids=["The-Hero", "The-Sage"])
                final_state = asyncio.run(
                    run_daily_batch(
                        date="2026-07-05",
                        resume=True,
                        run_options=RunOptions(persona_limit=1, skip_expand=True),
                        out_dir=out_dir,
                        base_state_dir=state_dir,
                    )
                )

            self.assertEqual(called_personas, ["The-Hero"])
            self.assertEqual(final_state.items[0].status, "done")
            self.assertEqual(final_state.items[0].last_completed_stage, "compose")

    def test_resume_repairs_briefing_with_generated_judge_copies(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_dir = tmp_path / "output"
            state_dir = tmp_path / "state"

            pool = _fake_pool()[:1]
            pool_dir = out_dir / "2026-07-05" / "01-england-heatwave-grips-the-nation-today"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_file = tmp_path / "pool.json"
            pool_file.write_text(json.dumps(pool), encoding="utf-8")
            (pool_dir / "news.json").write_text(
                json.dumps(
                    {
                        "title": pool[0]["title"],
                        "description": pool[0]["description"],
                        "pub_time": pool[0]["pub_time"],
                        "source_name": "Guardian",
                        "url": pool[0]["url"],
                    }
                ),
                encoding="utf-8",
            )
            retrieve_result = _fake_retrieve_result()
            (pool_dir / "retrieve.json").write_text(json.dumps(retrieve_result), encoding="utf-8")
            (pool_dir / "briefing.md").write_text(
                "# Daily Batch item 01\n\n## Review copies\n- tmdb:42: （无）\n",
                encoding="utf-8",
            )

            state = init_batch_state("2026-07-05", pool, str(pool_file))
            state.items[0].status = "done"
            state.items[0].last_completed_stage = "compose"
            state.save(state_path("2026-07-05", state_dir))

            def fake_score_items(items, judge_fn, *, observation_run_ids=None, workers=1):
                self.assertEqual(len(items), 1)
                self.assertEqual(items[0].run_id, pool_dir.name)
                return _FakeJudgeOutput(
                    scores=[
                        {
                            "run_id": pool_dir.name,
                            "tmdb_id": "42",
                            "title": "Prod Movie",
                            "judge_score": 2,
                            "judge_resonance_type": "强共振",
                            "rationale": "Both center on outages.",
                            "causal_test": "Power loss drives crisis.",
                        }
                    ]
                )

            def fake_review(retrieve_result_arg, news_dict, *, provider=None, judge_index=None, run_id="", min_judge=None, prompts_dir=None, llm_call=None):
                self.assertEqual(run_id, pool_dir.name)
                self.assertIn((pool_dir.name, "42"), judge_index)
                entry = judge_index[(pool_dir.name, "42")]
                self.assertEqual(entry.rationale, "Both center on outages.")
                self.assertEqual(entry.causal_test, "Power loss drives crisis.")
                return SimpleNamespace(
                    review_copies=[
                        SimpleNamespace(
                            tmdb_id=42,
                            judge_rationale_zh="中文理由",
                            judge_causal_test_zh="",
                        )
                    ],
                    errors=[],
                )

            with ExitStack() as stack:
                stack.enter_context(patch("scripts.daily_batch.score_items", side_effect=fake_score_items))
                stack.enter_context(patch("scripts.daily_batch.compose.run_review", side_effect=fake_review))
                final_state = asyncio.run(
                    run_daily_batch(
                        date="2026-07-05",
                        resume=True,
                        run_options=RunOptions(persona_limit=1, skip_expand=True),
                        out_dir=out_dir,
                        base_state_dir=state_dir,
                    )
                )

            self.assertTrue((out_dir / "2026-07-05" / "briefing.md").is_file())
            root_briefing = (out_dir / "2026-07-05" / "briefing.md").read_text(encoding="utf-8")
            self.assertIn("England Heatwave Grips the Nation Today", root_briefing)
            self.assertIn("A longer description about the first story that is clearly sufficient.", root_briefing)
            self.assertIn("candidate Prod Movie (2020) [tmdb:42]", root_briefing)
            self.assertIn("llm_judge_score: 2", root_briefing)
            self.assertIn("llm_judge_rationale: Both center on outages.", root_briefing)

    def test_render_daily_batch_briefing_aggregates_item_news_and_candidates(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_dir = tmp_path / "output" / "daily_batch"
            date_dir = out_dir / "2026-07-06"
            item_dir = date_dir / "01-foo"
            item_dir.mkdir(parents=True, exist_ok=True)

            (item_dir / "news.json").write_text(
                json.dumps(
                    {
                        "title": "Daily News Title",
                        "description": "Short body used by downstream processing.",
                        "pub_time": "2026-07-06T00:00:00Z",
                        "source_name": "Guardian",
                        "url": "https://example.com/news",
                    }
                ),
                encoding="utf-8",
            )
            (item_dir / "retrieve.json").write_text(
                json.dumps(
                    {
                        "candidates": [
                            {
                                "title": "Candidate One",
                                "release_year": 2024,
                                "tmdb_id": 111,
                                "overview": "Candidate one overview.",
                            },
                            {
                                "title": "Candidate Two",
                                "release_date": "2022-04-01",
                                "tmdb_id": 222,
                                "overview": "Candidate two overview.",
                            },
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (item_dir / "llm-judge-scores.json").write_text(
                json.dumps(
                    {
                        "scores": [
                            {
                                "tmdb_id": "111",
                                "judge_score": 3,
                                "rationale": "English judge rationale.",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            (item_dir / "briefing.md").write_text(
                "# Daily Batch item 01\n\n## Review copies\n- tmdb:222: 中文兜底理由\n",
                encoding="utf-8",
            )

            written = write_daily_batch_briefing(date_dir)
            self.assertEqual(written, date_dir / "briefing.md")
            zh_written = date_dir / "briefing.zh.md"
            self.assertTrue(zh_written.is_file())
            briefing = written.read_text(encoding="utf-8")
            briefing_zh = zh_written.read_text(encoding="utf-8")
            self.assertIn("Daily News Title", briefing)
            self.assertIn("Short body used by downstream processing.", briefing)
            self.assertIn("candidate Candidate One (2024) [tmdb:111]", briefing)
            self.assertIn("Candidate one overview.", briefing)
            self.assertIn("llm_judge_score: 3", briefing)
            self.assertIn("llm_judge_rationale: English judge rationale.", briefing)
            self.assertIn("candidate Candidate Two (2022) [tmdb:222]", briefing)
            self.assertIn("llm_judge_rationale: 中文兜底理由", briefing)
            self.assertIn("新闻标题", briefing_zh)
            self.assertIn("新闻正文", briefing_zh)
            self.assertIn("候选电影", briefing_zh)
            self.assertIn("剧情简介", briefing_zh)
            self.assertIn("LLM judge 分数", briefing_zh)
            self.assertIn("LLM judge 理由", briefing_zh)
            self.assertIn("Candidate One (2024) [tmdb:111]", briefing_zh)
            self.assertIn("English judge rationale.", briefing_zh)
            self.assertIn("中文兜底理由", briefing_zh)

    def test_full_run_marks_all_items_done_and_writes_checkpoint(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_dir = tmp_path / "output"
            state_dir = tmp_path / "state"

            with ExitStack() as stack:
                _apply_common_patches(stack)
                state = asyncio.run(
                    run_daily_batch(
                        date="2026-07-05",
                        run_options=RunOptions(),
                        out_dir=out_dir,
                        base_state_dir=state_dir,
                    )
                )

            self.assertEqual(len(state.items), 2)
            for item in state.items:
                self.assertEqual(item.status, "done")
                self.assertEqual(item.last_completed_stage, "compose")
                self.assertEqual(set(item.completed_personas), {"The-Hero", "The-Sage"})

            saved_path = state_path("2026-07-05", state_dir)
            self.assertTrue(saved_path.is_file())
            on_disk = json.loads(saved_path.read_text(encoding="utf-8"))
            self.assertEqual(on_disk["items"][0]["status"], "done")

            item_dir_0 = out_dir / "2026-07-05" / "01-england-heatwave-grips-the-nation-today"
            self.assertTrue((item_dir_0 / "deconstruct.json").is_file())
            self.assertTrue((item_dir_0 / "retrieve.json").is_file())
            self.assertTrue((item_dir_0 / "briefing.md").is_file())
            self.assertTrue((item_dir_0 / "personas" / "The-Hero.json").is_file())
            self.assertTrue((item_dir_0 / "personas" / "The-Sage.json").is_file())


class PersonaConcurrencyTests(unittest.TestCase):
    def test_persona_stage_runs_concurrently_and_preserves_order(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_dir = tmp_path / "output"
            state_dir = tmp_path / "state"

            persona_ids = ["The-Hero", "The-Sage", "The-Lover", "The-Jester"]
            start_log: list[tuple[str, float]] = []
            retrieve_seen: list[list[str]] = []

            async def slow_pipeline(persona_id, deconstruction, *, provider, expansion):
                start_log.append((persona_id, time.perf_counter()))
                await asyncio.sleep(0.05)
                return _FakePersonaResult(persona_id=persona_id)

            def capture_retrieve(agents_list, errors, top_k):
                retrieve_seen.append([agent["agent_id"] for agent in agents_list])
                return _fake_retrieve_result()

            with ExitStack() as stack:
                stack.enter_context(patch("scripts.daily_batch.fetch_heat_pool", return_value=_fake_pool()[:1]))
                stack.enter_context(patch("scripts.daily_batch.run_deconstruct", return_value={"deconstruction": _fake_deconstruction()}))
                stack.enter_context(patch("scripts.daily_batch.list_persona_ids", return_value=persona_ids))
                stack.enter_context(patch("scripts.daily_batch.run_persona_pipeline", side_effect=slow_pipeline))
                stack.enter_context(patch("scripts.daily_batch.retrieve_from_agents", side_effect=capture_retrieve))
                stack.enter_context(patch("scripts.daily_batch.compose.run_review", return_value=_FakeReviewResult()))
                stack.enter_context(patch("scripts.daily_batch.score_items", return_value=_FakeJudgeOutput(scores=[])))
                stack.enter_context(patch("scripts.expand.run_expansion", return_value={"expansion": {"fake": "expansion"}}))
                stack.enter_context(
                    patch(
                        "scripts.daily_batch.pipeline_result_to_dict",
                        side_effect=lambda result: {
                            "persona_id": result.persona_id,
                            "pseudos": [{"text": p.text} for p in result.pseudos],
                            "warnings": result.warnings,
                        },
                    )
                )
                start = time.perf_counter()
                state = asyncio.run(
                    run_daily_batch(
                        date="2026-07-05",
                        run_options=RunOptions(persona_concurrency=4),
                        out_dir=out_dir,
                        base_state_dir=state_dir,
                    )
                )
                elapsed = time.perf_counter() - start

            self.assertEqual(len(start_log), 4)
            self.assertLess(elapsed, 0.14)
            self.assertEqual(retrieve_seen, [["The-Hero", "The-Sage", "The-Lover", "The-Jester"]])
            self.assertEqual(state.items[0].status, "done")

    def test_persona_stage_resume_skips_cached_persona(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_dir = tmp_path / "output"
            state_dir = tmp_path / "state"

            pool = _fake_pool()[:1]
            state = init_batch_state("2026-07-05", pool, "output/daily_batch/2026-07-05/pool.json")
            saved_state_path = state_path("2026-07-05", state_dir)
            item_dir_0 = out_dir / "2026-07-05" / "01-england-heatwave-grips-the-nation-today"
            (item_dir_0 / "personas").mkdir(parents=True, exist_ok=True)
            (item_dir_0 / "deconstruct.json").write_text(json.dumps(_fake_deconstruction()), encoding="utf-8")
            (item_dir_0 / "personas" / "The-Hero.json").write_text(
                json.dumps({"agent": {"agent_id": "The-Hero", "pseudos": [], "text": "cached"}}),
                encoding="utf-8",
            )
            state.items[0].last_completed_stage = "deconstruct"
            state.items[0].completed_personas = ["The-Hero"]
            pool_dir = out_dir / "2026-07-05"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_file = pool_dir / "pool.json"
            pool_file.write_text(json.dumps(pool), encoding="utf-8")
            state.pool_file = str(pool_file)
            state.save(saved_state_path)

            called_personas: list[str] = []

            async def track_pipeline(persona_id, deconstruction, *, provider, expansion):
                called_personas.append(persona_id)
                return _FakePersonaResult(persona_id=persona_id)

            with ExitStack() as stack:
                _apply_common_patches(stack, persona_side_effect=track_pipeline, persona_ids=["The-Hero", "The-Sage"])
                final_state = asyncio.run(
                    run_daily_batch(
                        date="2026-07-05",
                        resume=True,
                        run_options=RunOptions(),
                        out_dir=out_dir,
                        base_state_dir=state_dir,
                    )
                )

            self.assertEqual(called_personas, ["The-Sage"])
            self.assertEqual(final_state.items[0].status, "done")
            self.assertEqual(set(final_state.items[0].completed_personas), {"The-Hero", "The-Sage"})


class ResumeAfterInterruptionTests(unittest.TestCase):
    """Persona errors are isolated per persona and persisted without failing the whole item."""

    def test_persona_exception_is_recorded_without_failing_batch(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_dir = tmp_path / "output"
            state_dir = tmp_path / "state"

            call_log: list[str] = []

            async def crash_on_item1_the_sage(persona_id, deconstruction, *, provider, expansion):
                call_log.append(persona_id)
                if call_log == ["The-Hero", "The-Sage", "The-Hero", "The-Sage"]:
                    raise RuntimeError("simulated crash mid-persona")
                return _FakePersonaResult(persona_id=persona_id)

            with ExitStack() as stack:
                _apply_common_patches(stack, persona_side_effect=crash_on_item1_the_sage)
                final_state = asyncio.run(
                    run_daily_batch(
                        date="2026-07-05",
                        run_options=RunOptions(),
                        out_dir=out_dir,
                        base_state_dir=state_dir,
                    )
                )

            self.assertEqual(final_state.items[0].status, "done")
            self.assertEqual(final_state.items[1].status, "done")
            self.assertEqual(set(final_state.items[1].completed_personas), {"The-Hero", "The-Sage"})

            item1_dir = out_dir / "2026-07-05" / "02-byzantine-city-unearthed-reveals-new-layers"
            self.assertTrue((item1_dir / "personas" / "The-Hero.json").is_file())
            error_payload = json.loads((item1_dir / "personas" / "The-Sage.json").read_text(encoding="utf-8"))
            self.assertIn("simulated crash mid-persona", error_payload["error"])
            self.assertTrue((item1_dir / "briefing.md").is_file())


class PersonaLevelCheckpointTests(unittest.TestCase):
    """Persona-level checkpoint: personas already in completed_personas + with an
    existing personas/{id}.json must be skipped even without a full crash."""

    def test_skips_already_completed_persona_on_manual_resume(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            out_dir = tmp_path / "output"
            state_dir = tmp_path / "state"

            pool = _fake_pool()[:1]
            state = init_batch_state("2026-07-05", pool, "output/daily_batch/2026-07-05/pool.json")
            saved_state_path = state_path("2026-07-05", state_dir)

            item_dir_0 = out_dir / "2026-07-05" / "01-england-heatwave-grips-the-nation-today"
            (item_dir_0 / "personas").mkdir(parents=True, exist_ok=True)
            (item_dir_0 / "deconstruct.json").write_text(json.dumps(_fake_deconstruction()), encoding="utf-8")
            (item_dir_0 / "personas" / "The-Hero.json").write_text(
                json.dumps({"agent": {"agent_id": "The-Hero", "pseudos": [], "text": "cached"}}),
                encoding="utf-8",
            )
            state.items[0].last_completed_stage = "deconstruct"
            state.items[0].completed_personas = ["The-Hero"]

            pool_dir = out_dir / "2026-07-05"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_file = pool_dir / "pool.json"
            pool_file.write_text(json.dumps(pool), encoding="utf-8")
            state.pool_file = str(pool_file)
            state.save(saved_state_path)

            called_personas: list[str] = []

            async def track_pipeline(persona_id, deconstruction, *, provider, expansion):
                called_personas.append(persona_id)
                return _FakePersonaResult(persona_id=persona_id)

            with ExitStack() as stack:
                _apply_common_patches(
                    stack,
                    persona_side_effect=track_pipeline,
                    persona_ids=["The-Hero", "The-Sage"],
                )
                final_state = asyncio.run(
                    run_daily_batch(
                        date="2026-07-05",
                        resume=True,
                        run_options=RunOptions(),
                        out_dir=out_dir,
                        base_state_dir=state_dir,
                    )
                )

            self.assertEqual(called_personas, ["The-Sage"])
            self.assertEqual(final_state.items[0].status, "done")
            self.assertEqual(set(final_state.items[0].completed_personas), {"The-Hero", "The-Sage"})


if __name__ == "__main__":
    unittest.main()