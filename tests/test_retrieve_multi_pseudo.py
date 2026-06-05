"""Unit tests for Phase 3.5.4 multi-pseudo retrieve aggregation."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from scripts.retrieve import (
    DEFAULT_MAX_CANDIDATES,
    _apply_containment,
    _expand_retrieval_queries,
    retrieve_from_agents,
)


def _mini_meta() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "id": [1, 2, 3, 4],
            "title": ["A", "B", "C", "D"],
            "overview": ["o1", "o2", "o3", "o4"],
            "genres": ["g"] * 4,
            "release_date": ["2010-01-01"] * 4,
            "original_language": ["en"] * 4,
            "poster_path": [""] * 4,
        }
    )


class ExpandQueriesTests(unittest.TestCase):
    def test_prefers_pseudos_over_legacy_text(self) -> None:
        agents = [
            {
                "agent_id": "A2",
                "role": "creative",
                "text": "legacy text",
                "pseudos": [
                    {"id": "p1", "text": "pseudo one", "source": {"fragments": ["why-0"]}},
                    {"id": "p2", "text": "pseudo two", "source": {"fragments": ["how-0"]}},
                ],
            }
        ]
        queries = _expand_retrieval_queries(agents, [])
        self.assertEqual(len(queries), 2)
        self.assertEqual(queries[0]["pseudo_id"], "p1")
        self.assertEqual(queries[0]["source"]["fragments"], ["why-0"])

    def test_legacy_text_when_no_pseudos(self) -> None:
        agents = [{"agent_id": "A1", "role": "baseline", "text": "baseline only"}]
        queries = _expand_retrieval_queries(agents, [])
        self.assertEqual(len(queries), 1)
        self.assertEqual(queries[0]["pseudo_id"], "legacy")
        self.assertEqual(queries[0]["channel_role"], "baseline")

    def test_skips_failed_agents(self) -> None:
        agents = [{"agent_id": "A4", "role": "creative", "text": "x", "pseudos": []}]
        errors = [{"agent_id": "A4", "type": "api_error"}]
        self.assertEqual(_expand_retrieval_queries(agents, errors), [])


class ContainmentTests(unittest.TestCase):
    def test_caps_candidate_list(self) -> None:
        items = [{"tmdb_id": i, "similarity": 1.0 - i * 0.01, "quality_candidate": False} for i in range(30)]
        capped = _apply_containment(items, max_candidates=19)
        self.assertEqual(len(capped), 19)
        self.assertEqual(capped[0]["tmdb_id"], 0)


class RetrieveAggregateTests(unittest.TestCase):
    @patch("scripts.retrieve._get_model")
    @patch("scripts.retrieve._load_index")
    def test_aggregate_hit_sources_and_collision_rules(
        self, load_index: MagicMock, get_model: MagicMock
    ) -> None:
        meta = _mini_meta()
        embeddings = np.eye(4, dtype=np.float32)
        load_index.return_value = (embeddings, meta)

        model = MagicMock()

        def fake_encode(text: str, normalize_embeddings: bool = True) -> np.ndarray:
            if "one" in text:
                return np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
            if "two" in text:
                return np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
            if "baseline" in text:
                return np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)
            return np.array([0.0, 0.0, 1.0, 0.0], dtype=np.float32)

        model.encode.side_effect = fake_encode
        get_model.return_value = model

        agents = [
            {
                "agent_id": "A2",
                "role": "toned",
                "pseudos": [
                    {
                        "id": "t1",
                        "text": "pseudo one",
                        "source": {"fragments": ["why-0"], "channel_role": "toned"},
                    },
                    {
                        "id": "t2",
                        "text": "pseudo two",
                        "source": {"fragments": ["how-0"], "channel_role": "toned"},
                    },
                ],
            },
            {
                "agent_id": "A1",
                "role": "baseline",
                "pseudos": [
                    {
                        "id": "p1",
                        "text": "baseline hit",
                        "source": {"fragments": ["result-0"]},
                    }
                ],
            },
        ]

        result = retrieve_from_agents(agents, [], top_k=2, max_candidates=DEFAULT_MAX_CANDIDATES)
        self.assertEqual(result["meta"]["query_count"], 3)
        self.assertGreater(result["meta"]["raw_hit_count"], 0)

        movie_a = next(c for c in result["candidates"] if c["tmdb_id"] == 1)
        self.assertIn("A2", movie_a["triggered_by"])
        self.assertNotIn("A1", movie_a["triggered_by"])
        self.assertTrue(any(h["agent_id"] == "A2" for h in movie_a["hit_sources"]))

        self.assertIn("quality_candidate", movie_a)
        self.assertIn("distinct_agents", movie_a)
        self.assertIn("quality_reason", movie_a)
        self.assertEqual(movie_a["distinct_agents"], 1)
        self.assertFalse(movie_a["quality_candidate"])
        self.assertIn("neutral_vote=0", movie_a["quality_reason"])

        per_a2 = next(p for p in result["per_agent"] if p["agent_id"] == "A2")
        self.assertEqual(len(per_a2["pseudos"]), 2)


if __name__ == "__main__":
    unittest.main()
