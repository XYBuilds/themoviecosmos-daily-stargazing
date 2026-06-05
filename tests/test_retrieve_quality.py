"""Unit tests for Phase 3.6.2 retrieve quality floor + D1 marking."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from scripts.retrieve import (
    DEFAULT_QUALITY_FLOOR,
    _apply_containment,
    _apply_quality_fields,
    _distinct_agents_above_floor,
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


class QualityFieldTests(unittest.TestCase):
    def test_distinct_agents_counts_toned_agents_above_floor(self) -> None:
        cand = {
            "hit_sources": [
                {"agent_id": "A2", "pseudo_id": "t1", "channel_role": "toned", "similarity": 0.85},
                {"agent_id": "A1", "pseudo_id": "p1", "channel_role": "baseline", "similarity": 0.55},
            ]
        }
        agents = _distinct_agents_above_floor(cand, quality_floor=0.40)
        self.assertEqual(agents, {"A2"})

    def test_low_similarity_toned_hits_do_not_count(self) -> None:
        cand = {
            "hit_sources": [
                {"agent_id": "A2", "pseudo_id": "t1", "channel_role": "toned", "similarity": 0.85},
                {"agent_id": "A4", "pseudo_id": "t1", "channel_role": "toned", "similarity": 0.35},
            ]
        }
        _apply_quality_fields(cand, quality_floor=0.40, neutral_total=2)
        self.assertEqual(cand["distinct_agents"], 1)
        self.assertFalse(cand["quality_candidate"])
        self.assertIn("neutral_vote=0", cand["quality_reason"])

    def test_quality_candidate_requires_neutral_vote_and_toned_convergence(self) -> None:
        cand = {
            "hit_sources": [
                {"agent_id": "A2", "pseudo_id": "n1", "channel_role": "neutral", "similarity": 0.85},
                {"agent_id": "A7", "pseudo_id": "t1", "channel_role": "toned", "similarity": 0.72},
            ]
        }
        _apply_quality_fields(cand, quality_floor=0.40, neutral_total=3)
        self.assertEqual(cand["distinct_agents"], 1)
        self.assertEqual(cand["neutral_hits"], 1)
        self.assertTrue(cand["quality_candidate"])
        self.assertIn("A7", cand["quality_reason"])


class QualityContainmentTests(unittest.TestCase):
    def test_quality_candidates_retained_before_similarity_fill(self) -> None:
        items = [
            {"tmdb_id": 1, "similarity": 0.95, "quality_candidate": False},
            {"tmdb_id": 2, "similarity": 0.50, "quality_candidate": True},
            {"tmdb_id": 3, "similarity": 0.80, "quality_candidate": False},
        ]
        capped = _apply_containment(items, max_candidates=2)
        self.assertEqual([c["tmdb_id"] for c in capped], [2, 1])


class RetrieveQualityIntegrationTests(unittest.TestCase):
    @patch("scripts.retrieve._get_model")
    @patch("scripts.retrieve._load_index")
    def test_retrieve_json_includes_quality_fields(
        self, load_index: MagicMock, get_model: MagicMock
    ) -> None:
        meta = _mini_meta()
        embeddings = np.eye(4, dtype=np.float32)
        load_index.return_value = (embeddings, meta)

        model = MagicMock()

        def fake_encode(text: str, normalize_embeddings: bool = True) -> np.ndarray:
            if "shared-strong" in text:
                return np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
            if "shared-weak" in text:
                vec = np.array([0.35, 0.94, 0.0, 0.0], dtype=np.float32)
                return vec / np.linalg.norm(vec)
            return np.array([0.0, 1.0, 0.0, 0.0], dtype=np.float32)

        model.encode.side_effect = fake_encode
        get_model.return_value = model

        agents = [
            {
                "agent_id": "A2",
                "role": "toned",
                "pseudos": [
                    {
                        "id": "n1",
                        "text": "shared-strong hit",
                        "source": {"fragments": [], "channel_role": "neutral"},
                    },
                ],
            },
            {
                "agent_id": "A1",
                "role": "baseline",
                "pseudos": [
                    {
                        "id": "p1",
                        "text": "shared-weak hit",
                        "source": {"fragments": []},
                    },
                ],
            },
        ]

        result = retrieve_from_agents(
            agents,
            [],
            top_k=1,
            max_candidates=10,
            quality_floor=0.40,
        )
        self.assertEqual(result["meta"]["quality_floor"], DEFAULT_QUALITY_FLOOR)

        shared = next(c for c in result["candidates"] if c["tmdb_id"] == 1)
        self.assertIn("quality_candidate", shared)
        self.assertIn("distinct_agents", shared)
        self.assertIn("neutral_hit_rate", shared)
        self.assertIn("quality_reason", shared)
        self.assertEqual(shared["distinct_agents"], 0)
        self.assertFalse(shared["quality_candidate"])
        self.assertIn("toned_agents=0", shared["quality_reason"])

    @patch("scripts.retrieve._get_model")
    @patch("scripts.retrieve._load_index")
    def test_neutral_plus_toned_marks_quality_candidate(
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
                "agent_id": "A2",
                "role": "toned",
                "pseudos": [
                    {
                        "id": "n1",
                        "text": "same movie neutral",
                        "source": {"fragments": [], "channel_role": "neutral"},
                    },
                    {
                        "id": "t1",
                        "text": "same movie toned",
                        "source": {"fragments": [], "channel_role": "toned"},
                    },
                ],
            },
            {
                "agent_id": "A1",
                "role": "baseline",
                "pseudos": [{"id": "p1", "text": "same movie", "source": {"fragments": []}}],
            },
        ]

        result = retrieve_from_agents(agents, [], top_k=1, quality_floor=0.40)
        movie = next(c for c in result["candidates"] if c["tmdb_id"] == 1)
        self.assertEqual(movie["distinct_agents"], 1)
        self.assertEqual(movie["neutral_hits"], 1)
        self.assertTrue(movie["quality_candidate"])
        self.assertIn("A2", movie["quality_reason"])
        self.assertNotIn("A1", movie["quality_reason"])


if __name__ == "__main__":
    unittest.main()
