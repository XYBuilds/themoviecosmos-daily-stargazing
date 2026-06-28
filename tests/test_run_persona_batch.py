"""Offline tests for run_persona_batch concurrency, ordering, and backoff."""

from __future__ import annotations

import asyncio
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, patch

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.agents import PseudoSegment
from scripts.rewrite import PersonaPipelineResult, AltPoolOverlay
from scripts.run_persona_batch import (
    DEFAULT_CONCURRENCY,
    is_retryable_llm_error,
    reorder_persona_agents,
    run_batch_for_news,
    startup_jitter_seconds,
    with_llm_backoff,
)


def _agent_row(persona_id: str) -> dict:
    return {
        "agent_id": persona_id,
        "persona_name": persona_id,
        "role": "creative",
        "pseudos": [{"id": "p1", "text": f"text-{persona_id}", "source": {}}],
        "text": f"text-{persona_id}",
        "warnings": [],
    }


class TestRetryableLlmError(unittest.TestCase):
    def test_429_and_timeout_are_retryable(self) -> None:
        self.assertTrue(is_retryable_llm_error("HTTP 429 Too Many Requests"))
        self.assertTrue(is_retryable_llm_error("rate limit exceeded"))
        self.assertTrue(is_retryable_llm_error("alt_creator timed out after 120s"))
        self.assertTrue(is_retryable_llm_error(TimeoutError()))

    def test_parse_errors_not_retryable(self) -> None:
        self.assertFalse(is_retryable_llm_error("alt_creator parse_error: bad json"))
        self.assertFalse(is_retryable_llm_error(None))


class TestReorderPersonaAgents(unittest.TestCase):
    def test_preserves_persona_ids_order(self) -> None:
        persona_ids = ["The-Sage", "The-Ruler", "The-Hero"]
        agents_map = {
            "The-Hero": _agent_row("The-Hero"),
            "The-Sage": _agent_row("The-Sage"),
            "The-Ruler": _agent_row("The-Ruler"),
        }
        ordered = reorder_persona_agents(persona_ids, agents_map)
        self.assertEqual([a["agent_id"] for a in ordered], persona_ids)

    def test_prefix_agents_first(self) -> None:
        prefix = [{"agent_id": "A1", "role": "baseline"}]
        ordered = reorder_persona_agents(
            ["The-Sage"],
            {"The-Sage": _agent_row("The-Sage")},
            prefix_agents=prefix,
        )
        self.assertEqual(ordered[0]["agent_id"], "A1")
        self.assertEqual(ordered[1]["agent_id"], "The-Sage")

    def test_skips_missing_personas(self) -> None:
        ordered = reorder_persona_agents(
            ["The-Sage", "The-Ruler"],
            {"The-Sage": _agent_row("The-Sage")},
        )
        self.assertEqual(len(ordered), 1)
        self.assertEqual(ordered[0]["agent_id"], "The-Sage")


class TestStartupJitter(unittest.TestCase):
    def test_within_bounds(self) -> None:
        import random

        rng = random.Random(0)
        for _ in range(20):
            sec = startup_jitter_seconds(rng=rng)
            self.assertGreaterEqual(sec, 5.0)
            self.assertLessEqual(sec, 15.0)


class TestWithLlmBackoff(unittest.IsolatedAsyncioTestCase):
    async def test_retries_then_succeeds(self) -> None:
        calls = 0

        async def flaky() -> str:
            nonlocal calls
            calls += 1
            if calls < 3:
                raise RuntimeError("HTTP 429 Too Many Requests")
            return "ok"

        with patch("scripts.run_persona_batch.asyncio.sleep", new_callable=AsyncMock):
            result = await with_llm_backoff(flaky, max_retries=4, initial_delay=0.01)
        self.assertEqual(result, "ok")
        self.assertEqual(calls, 3)

    async def test_non_retryable_raises_immediately(self) -> None:
        calls = 0

        async def bad() -> str:
            nonlocal calls
            calls += 1
            raise ValueError("parse_error")

        with self.assertRaises(ValueError):
            await with_llm_backoff(bad, max_retries=4, initial_delay=0.01)
        self.assertEqual(calls, 1)


class TestConcurrentBatchOrdering(unittest.IsolatedAsyncioTestCase):
    async def test_agents_order_stable_after_concurrent_completion(self) -> None:
        persona_ids = ["P-A", "P-B", "P-C", "P-D"]
        completion_order: list[str] = []

        async def fake_run(persona_id: str, *args, **kwargs):
            await asyncio.sleep(0.15 if persona_id == "P-A" else 0.01)
            completion_order.append(persona_id)
            return _agent_row(persona_id), None

        with (
            patch(
                "scripts.run_persona_batch.startup_jitter_seconds",
                return_value=0.0,
            ),
            patch(
                "scripts.run_persona_batch.run_persona_for_news",
                side_effect=fake_run,
            ),
            patch(
                "scripts.run_persona_batch.load_a1_agent_from_phase36",
                return_value={"agent_id": "A1", "role": "baseline", "pseudos": []},
            ),
            patch("scripts.run_persona_batch._copy_phase36_static"),
            patch(
                "scripts.run_persona_batch.finalize_run",
                new_callable=AsyncMock,
                return_value={"meta": {"candidate_count": 1}},
            ) as finalize_mock,
        ):
            row = await run_batch_for_news(
                "04-celebrity-scandal",
                persona_ids,
                provider=None,
                skip_existing=False,
                skip_finalize=False,
                eval_phase="3.7",
                concurrency=3,
            )
            agents_passed = finalize_mock.call_args[0][1]
            agent_ids = [a["agent_id"] for a in agents_passed]

        self.assertEqual(len(completion_order), 4)
        self.assertNotEqual(completion_order, persona_ids)
        self.assertEqual(agent_ids[0], "A1")
        self.assertEqual(agent_ids[1:], persona_ids)
        self.assertEqual(row.get("errors"), [])

    async def test_single_persona_failure_isolated(self) -> None:
        persona_ids = ["P-OK-1", "P-FAIL", "P-OK-2"]

        async def fake_run(persona_id: str, *args, **kwargs):
            if persona_id == "P-FAIL":
                return None, "simulated failure"
            return _agent_row(persona_id), None

        with (
            patch(
                "scripts.run_persona_batch.startup_jitter_seconds",
                return_value=0.0,
            ),
            patch(
                "scripts.run_persona_batch.run_persona_for_news",
                side_effect=fake_run,
            ),
            patch(
                "scripts.run_persona_batch.load_a1_agent_from_phase36",
                return_value={"agent_id": "A1", "role": "baseline", "pseudos": []},
            ),
            patch("scripts.run_persona_batch._copy_phase36_static"),
            patch(
                "scripts.run_persona_batch.finalize_run",
                new_callable=AsyncMock,
                return_value={"meta": {"candidate_count": 2}},
            ),
        ):
            row = await run_batch_for_news(
                "04-celebrity-scandal",
                persona_ids,
                provider=None,
                skip_existing=False,
                skip_finalize=True,
                eval_phase="3.7",
                concurrency=DEFAULT_CONCURRENCY,
            )

        self.assertEqual(row["agents"], 3)  # A1 + 2 ok personas
        self.assertEqual(len(row["errors"]), 1)
        self.assertEqual(row["errors"][0]["agent_id"], "P-FAIL")

    async def test_pipeline_backoff_on_429(self) -> None:
        from scripts.run_persona_batch import run_persona_for_news
        import tempfile

        calls = 0
        pseudo = PseudoSegment("p1", "hello", {}, [])

        async def fake_pipeline(*args, **kwargs):
            nonlocal calls
            calls += 1
            if calls < 2:
                return PersonaPipelineResult(
                    persona_id="The-Sage",
                    overlay=AltPoolOverlay(persona_id="The-Sage", elements=[]),
                    error="HTTP 429 Too Many Requests",
                )
            return PersonaPipelineResult(
                persona_id="The-Sage",
                overlay=AltPoolOverlay(persona_id="The-Sage", elements=[]),
                pseudos=[pseudo],
            )

        with tempfile.TemporaryDirectory() as tmp:
            persona_dir = Path(tmp)
            decon = _REPO / "tests" / "fixtures" / "01-grid-outage-deconstructed.json"
            with (
                patch(
                    "scripts.run_persona_batch.run_persona_pipeline",
                    side_effect=fake_pipeline,
                ),
                patch(
                    "scripts.run_persona_batch.asyncio.sleep",
                    new_callable=AsyncMock,
                ),
            ):
                agent, err = await run_persona_for_news(
                    "The-Sage",
                    decon,
                    persona_dir,
                    provider=None,
                    skip_existing=False,
                )
            self.assertIsNone(err)
            self.assertIsNotNone(agent)
            self.assertEqual(calls, 2)


if __name__ == "__main__":
    unittest.main()
