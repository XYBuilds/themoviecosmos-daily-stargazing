"""Unit tests for Phase 6.0 dev shortcut switches (RunOptions + run_eval CLI wiring)."""

from __future__ import annotations

import unittest
from unittest.mock import patch

from scripts.lib.run_options import RunOptions
from scripts.run_eval import main


class RunOptionsTests(unittest.TestCase):
    def test_defaults_preserve_production_behavior(self) -> None:
        opts = RunOptions()
        self.assertIsNone(opts.persona_limit)
        self.assertFalse(opts.skip_expand)
        self.assertEqual(opts.judge_topk, 2)
        self.assertFalse(opts.force)

    def test_is_frozen_dataclass(self) -> None:
        opts = RunOptions()
        with self.assertRaises(Exception):
            opts.force = True  # type: ignore[misc]

    def test_custom_values_roundtrip(self) -> None:
        opts = RunOptions(persona_limit=2, skip_expand=True, judge_topk=5, force=True)
        self.assertEqual(opts.persona_limit, 2)
        self.assertTrue(opts.skip_expand)
        self.assertEqual(opts.judge_topk, 5)
        self.assertTrue(opts.force)


class RunEvalCliSwitchTests(unittest.TestCase):
    """Verify --personas/--skip-expand/--judge-topk/--force reach run_eval_pipeline."""

    def _run_with_patches(self, argv: list[str]):
        fake_news = type(
            "FakeNews",
            (),
            {"title": "Test", "pub_time": "2026-05-29T12:00:00Z", "url": "", "source_name": "", "description": ""},
        )()

        captured: dict = {}

        async def fake_pipeline(news, *, provider, deconstruction, run_dir, run_options=None):
            captured["run_options"] = run_options
            return [], [], {"candidates": [], "per_agent": []}, {}, {}, {}

        with (
            patch("scripts.run_eval.load_news_from_file", return_value=fake_news),
            patch("scripts.run_eval._resolve_deconstruction", return_value=({"x": 1}, {})),
            patch("scripts.run_eval.run_eval_pipeline", side_effect=fake_pipeline),
            patch("scripts.run_eval.write_eval_bundle"),
        ):
            code = main(argv)
        return code, captured

    def test_personas_and_skip_expand_and_judge_topk_flow_into_run_options(self) -> None:
        code, captured = self._run_with_patches(
            [
                "--news-file",
                "tests/sample_news.json",
                "--personas",
                "2",
                "--skip-expand",
                "--judge-topk",
                "5",
            ]
        )
        self.assertEqual(code, 0)
        opts = captured["run_options"]
        self.assertEqual(opts.persona_limit, 2)
        self.assertTrue(opts.skip_expand)
        self.assertEqual(opts.judge_topk, 5)
        self.assertFalse(opts.force)

    def test_defaults_when_no_dev_switches_passed(self) -> None:
        code, captured = self._run_with_patches(["--news-file", "tests/sample_news.json"])
        self.assertEqual(code, 0)
        opts = captured["run_options"]
        self.assertIsNone(opts.persona_limit)
        self.assertFalse(opts.skip_expand)
        self.assertEqual(opts.judge_topk, 2)
        self.assertFalse(opts.force)


if __name__ == "__main__":
    unittest.main()