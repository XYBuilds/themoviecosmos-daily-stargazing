"""Unit tests for Phase 3.9.2 A1 held-out oracle retrieve path (ADR-0009 kinds)."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from scripts.retrieve import (
    DEFAULT_MAX_CANDIDATES,
    _build_oracle_comparison,
    _is_oracle_query,
    _split_oracle_judge_queries,
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


class OracleQuerySplitTests(unittest.TestCase):
    def test_a1_and_baseline_kind_route_to_oracle(self) -> None:
        queries = [
            {"agent_id": "A1", "search_unit_kind": "baseline", "role": "baseline"},
            {"agent_id": "P01", "search_unit_kind": "surface-fragment-bundle", "role": "toned"},
            {"agent_id": "P02", "search_unit_kind": "persona-semantic", "role": "toned"},
        ]
        oracle, judge = _split_oracle_judge_queries(queries)
        self.assertEqual(len(oracle), 1)
        self.assertEqual(len(judge), 2)
        self.assertTrue(_is_oracle_query(oracle[0]))


class OracleComparisonTests(unittest.TestCase):
    def test_superset_when_objective_covers_a1(self) -> None:
        candidates = [
            {
                "tmdb_id": 1,
                "hit_sources": [
                    {
                        "agent_id": "P01",
                        "pseudo_id": "su-surface-1",
                        "search_unit_kind": "surface-fragment-bundle",
                        "similarity": 0.85,
                    }
                ],
            },
            {
                "tmdb_id": 2,
                "hit_sources": [
                    {
                        "agent_id": "P02",
                        "pseudo_id": "su-event-1",
                        "search_unit_kind": "event-fragment-bundle",
                        "similarity": 0.80,
                    }
                ],
            },
        ]
        comparison = _build_oracle_comparison({1, 2}, candidates, quality_floor=0.40)
        self.assertTrue(comparison["objective_union_superset_of_a1_hits"])
        self.assertEqual(comparison["a1_only_tmdb_ids"], [])
        self.assertEqual(comparison["objective_only_tmdb_ids"], [])

    def test_superset_false_when_a1_has_unique_hits(self) -> None:
        candidates = [
            {
                "tmdb_id": 1,
                "hit_sources": [
                    {
                        "agent_id": "P01",
                        "pseudo_id": "su-surface-1",
                        "search_unit_kind": "surface-fragment-bundle",
                        "similarity": 0.85,
                    }
                ],
            }
        ]
        comparison = _build_oracle_comparison({1, 3}, candidates, quality_floor=0.40)
        self.assertFalse(comparison["objective_union_superset_of_a1_hits"])
        self.assertEqual(comparison["a1_only_tmdb_ids"], [3])
        self.assertEqual(comparison["objective_only_tmdb_ids"], [])


class RetrieveA1OracleIntegrationTests(unittest.TestCase):
    @patch("scripts.retrieve._get_model")
    @patch("scripts.retrieve._load_index")
    def test_a1_excluded_from_candidates_collision_and_ranking(
        self, load_index: MagicMock, get_model: MagicMock
    ) -> None:
        meta = _mini_meta()
        embeddings = np.eye(4, dtype=np.float32)
        load_index.return_value = (embeddings, meta)

        model = MagicMock()

        def fake_encode(text: str, normalize_embeddings: bool = True) -> np.ndarray:
            if "baseline" in text:
                return np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)
            return np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)

        model.encode.side_effect = fake_encode
        get_model.return_value = model

        agents = [
            {
                "agent_id": "P01",
                "role": "toned",
                "pseudos": [
                    {
                        "id": "su-surface-1",
                        "text": "surface bundle hit",
                        "source": {
                            "fragments": ["who-0"],
                            "search_unit_kind": "surface-fragment-bundle",
                        },
                    },
                    {
                        "id": "su-persona-1",
                        "text": "persona semantic hit",
                        "source": {
                            "fragments": ["result-0"],
                            "search_unit_kind": "persona-semantic",
                        },
                    },
                ],
            },
            {
                "agent_id": "A1",
                "role": "baseline",
                "pseudos": [
                    {
                        "id": "p1",
                        "text": "baseline oracle hit",
                        "source": {"fragments": ["result-0"]},
                    }
                ],
            },
        ]

        result = retrieve_from_agents(
            agents,
            [],
            top_k=1,
            max_candidates=DEFAULT_MAX_CANDIDATES,
            quality_floor=0.40,
        )

        candidate_ids = {c["tmdb_id"] for c in result["candidates"]}
        self.assertNotIn(2, candidate_ids)
        self.assertIn(1, candidate_ids)

        for cand in result["candidates"]:
            self.assertFalse(cand.get("also_baseline"))
            self.assertNotIn("A1", cand.get("triggered_by") or [])
            for source in cand.get("hit_sources") or []:
                self.assertNotEqual(source.get("agent_id"), "A1")

        oracle = result["a1_oracle"]
        self.assertIsNotNone(oracle)
        assert oracle is not None
        self.assertEqual(oracle["role"], "held_out_oracle")
        self.assertEqual(oracle["hit_tmdb_ids"], [2])
        self.assertEqual(oracle["meta"]["query_count"], 1)

        comparison = result["oracle_comparison"]
        self.assertIsNotNone(comparison)
        assert comparison is not None
        self.assertEqual(comparison["a1_hit_tmdb_ids"], [2])
        self.assertIn("objective_union_superset_of_a1_hits", comparison)

        per_agent_ids = {row["agent_id"] for row in result["per_agent"]}
        self.assertNotIn("A1", per_agent_ids)

    @patch("scripts.retrieve._get_model")
    @patch("scripts.retrieve._load_index")
    def test_a1_only_populates_oracle_not_candidates(
        self, load_index: MagicMock, get_model: MagicMock
    ) -> None:
        meta = _mini_meta()
        embeddings = np.eye(4, dtype=np.float32)
        load_index.return_value = (embeddings, meta)

        model = MagicMock()
        model.encode.return_value = np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)
        get_model.return_value = model

        agents = [
            {
                "agent_id": "A1",
                "role": "baseline",
                "pseudos": [{"id": "p1", "text": "baseline only", "source": {}}],
            }
        ]

        result = retrieve_from_agents(agents, [], top_k=1)
        self.assertEqual(result["candidates"], [])
        self.assertIsNotNone(result["a1_oracle"])
        assert result["a1_oracle"] is not None
        self.assertEqual(result["a1_oracle"]["hit_tmdb_ids"], [2])

    @patch("scripts.retrieve._get_model")
    @patch("scripts.retrieve._load_index")
    def test_personas_only_have_no_oracle_payload(
        self, load_index: MagicMock, get_model: MagicMock
    ) -> None:
        meta = _mini_meta()
        embeddings = np.eye(4, dtype=np.float32)
        load_index.return_value = (embeddings, meta)

        model = MagicMock()
        model.encode.return_value = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        get_model.return_value = model

        agents = [
            {
                "agent_id": "P01",
                "role": "toned",
                "pseudos": [
                    {
                        "id": "su-persona-1",
                        "text": "persona semantic only",
                        "source": {"search_unit_kind": "persona-semantic", "fragments": []},
                    }
                ],
            }
        ]

        result = retrieve_from_agents(agents, [], top_k=1)
        self.assertIsNone(result["a1_oracle"])
        self.assertIsNone(result["oracle_comparison"])
        self.assertGreater(len(result["candidates"]), 0)


if __name__ == "__main__":
    unittest.main()