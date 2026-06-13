"""Tests for parallel judge batch scoring (Phase 3.10.7)."""

from __future__ import annotations

import json
import threading
import time
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from scripts.judge_batch_parallel import item_key, score_pending_pairs, sort_pending
from scripts.llm_judge import JudgeItem
from scripts.resonance_rubric import TYPE_STRONG
from scripts.run_phase39_judge_batch import _load_partial, _write_checkpoint

_CAUSAL = "scarcity under constraint drives survival"


def _item(run_id: str, tmdb_id: str) -> JudgeItem:
    return JudgeItem(
        run_id=run_id,
        tmdb_id=tmdb_id,
        title=f"Film {tmdb_id}",
        news_title="News",
        news_summary="Summary",
        movie_overview="Overview",
        human_score=None,
    )


class JudgeBatchParallelTests(unittest.TestCase):
    def test_sort_pending_deterministic(self):
        items = [_item("05-x", "2"), _item("05-x", "1"), _item("04-y", "9")]
        keys = [item_key(i) for i in sort_pending(items)]
        self.assertEqual(keys, [("04-y", "9"), ("05-x", "1"), ("05-x", "2")])

    def test_parallel_mock_scores_all_pairs_checkpoint_valid(self):
        items = [_item("05-a", str(i)) for i in range(8)]
        partial: dict[tuple[str, str], dict] = {}
        active = threading.Semaphore(0)
        peak = 0
        lock = threading.Lock()

        def mock_score(item: JudgeItem):
            nonlocal peak
            with lock:
                peak += 1
                if peak > 1:
                    active.release()
            time.sleep(0.05)
            with lock:
                peak -= 1
            return 2, TYPE_STRONG, f"ok {item.tmdb_id}", _CAUSAL, None

        with TemporaryDirectory() as tmp:
            out_json = Path(tmp) / "scores.json"
            out_md = Path(tmp) / "scores.md"
            all_items = items

            checkpoint_count = 0

            def checkpoint() -> None:
                nonlocal checkpoint_count
                checkpoint_count += 1
                _write_checkpoint(
                    out_json,
                    out_md,
                    all_items,
                    partial,
                    obs_ids=["01-grid-outage"],
                    prompt_version="test",
                    provider="mimo",
                    mimo_thinking="disabled",
                )

            score_pending_pairs(
                items,
                partial=partial,
                score_fn=mock_score,
                workers=4,
                checkpoint_fn=checkpoint,
            )

            self.assertEqual(len(partial), 8)
            self.assertEqual(checkpoint_count, 8)
            data = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertEqual(len(data["scores"]), 8)
            self.assertEqual(data["run_metadata"]["thinking_mode"], "disabled")
            self.assertIn("thinking disabled", data["run_metadata"]["judge_condition_note"])
            self.assertTrue(out_md.is_file())
            md_text = out_md.read_text(encoding="utf-8")
            self.assertIn("**thinking_mode**: disabled", md_text)
            self.assertIn("thinking disabled", md_text)
            for row in data["scores"]:
                self.assertEqual(row["judge_score"], 2)

    def test_checkpoint_can_mark_mimo_thinking_enabled(self):
        items = [_item("05-a", "1")]
        partial = {
            ("05-a", "1"): {
                "run_id": "05-a",
                "tmdb_id": "1",
                "title": "Film 1",
                "judge_score": 2,
                "judge_resonance_type": TYPE_STRONG,
                "rationale": "ok",
                "causal_test": _CAUSAL,
                "human_score": None,
                "human_resonance_type": None,
                "human_pov_transform": None,
                "judge_pov_transform": None,
                "disagreement": False,
            }
        }
        with TemporaryDirectory() as tmp:
            out_json = Path(tmp) / "scores.json"
            out_md = Path(tmp) / "scores.md"
            _write_checkpoint(
                out_json,
                out_md,
                items,
                partial,
                obs_ids=["01-grid-outage"],
                prompt_version="test-thinking-enabled",
                provider="mimo",
                mimo_thinking="enabled",
            )
            data = json.loads(out_json.read_text(encoding="utf-8"))
            self.assertEqual(data["run_metadata"]["thinking_mode"], "enabled")
            self.assertIn("thinking enabled", data["run_metadata"]["judge_condition_note"])
            md_text = out_md.read_text(encoding="utf-8")
            self.assertIn("**thinking_mode**: enabled", md_text)

    def test_resume_only_scores_pending_subset(self):
        """Caller filters completed keys; parallel runner scores only *pending*."""
        item_b = _item("05-a", "2")
        calls: list[str] = []

        def mock_score(item: JudgeItem):
            calls.append(item.tmdb_id)
            return 1, None, "r", "", None

        partial: dict[tuple[str, str], dict] = {
            ("05-a", "1"): {
                "run_id": "05-a",
                "tmdb_id": "1",
                "title": "cached",
                "judge_score": 0,
                "judge_resonance_type": None,
                "rationale": "cached",
                "causal_test": "",
                "human_score": None,
                "human_resonance_type": None,
                "disagreement": False,
            }
        }

        score_pending_pairs(
            [item_b],
            partial=partial,
            score_fn=mock_score,
            workers=4,
        )

        self.assertEqual(calls, ["2"])
        self.assertEqual(len(partial), 2)

    def test_load_partial_roundtrip(self):
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "partial.json"
            payload = {
                "version": 3,
                "calibration": {},
                "scores": [
                    {
                        "run_id": "05-a",
                        "tmdb_id": "99",
                        "title": "T",
                        "judge_score": 1,
                    }
                ],
            }
            path.write_text(json.dumps(payload), encoding="utf-8")
            loaded = _load_partial(path)
            self.assertIn(("05-a", "99"), loaded)
            self.assertEqual(loaded[("05-a", "99")]["judge_score"], 1)


if __name__ == "__main__":
    unittest.main()
