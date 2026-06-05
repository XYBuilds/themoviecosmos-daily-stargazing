"""Unit tests for Phase 3.8.3 neutral union vote + neutral_hit_rate collision."""

from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch

import numpy as np
import pandas as pd

from scripts.retrieve import (
    DEFAULT_QUALITY_FLOOR,
    DEFAULT_TOP_K,
    _apply_quality_fields,
    _count_neutral_personas,
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


def _neutral_agents(count: int, *, text: str = "shared neutral hit") -> list[dict]:
    return [
        {
            "agent_id": f"P{i:02d}",
            "role": "toned",
            "pseudos": [
                {
                    "id": "n1",
                    "text": text,
                    "source": {"fragments": [], "channel_role": "neutral"},
                }
            ],
        }
        for i in range(count)
    ]


class NeutralHitRateUnitTests(unittest.TestCase):
    def test_neutral_total_counts_personas_with_neutral_pseudo(self) -> None:
        agents = _neutral_agents(12)
        queries = _expand_retrieval_queries(agents, [])
        self.assertEqual(_count_neutral_personas(queries), 12)

    def test_neutral_hit_rate_denominator_and_numerator(self) -> None:
        neutral_total = 12
        cand = {
            "hit_sources": [
                {
                    "agent_id": f"P{i:02d}",
                    "pseudo_id": "n1",
                    "channel_role": "neutral",
                    "similarity": 0.85 if i < 6 else 0.30,
                }
                for i in range(12)
            ]
        }
        _apply_quality_fields(
            cand,
            quality_floor=DEFAULT_QUALITY_FLOOR,
            neutral_total=neutral_total,
        )
        self.assertEqual(cand["neutral_total"], 12)
        self.assertEqual(cand["neutral_hits"], 6)
        self.assertAlmostEqual(cand["neutral_hit_rate"], 0.5)
        self.assertFalse(cand["quality_candidate"])


class NeutralCollisionIntegrationTests(unittest.TestCase):
    @patch("scripts.retrieve._get_model")
    @patch("scripts.retrieve._load_index")
    def test_twelve_neutrals_same_film_one_vote_no_quality_without_toned(
        self, load_index: MagicMock, get_model: MagicMock
    ) -> None:
        meta = _mini_meta()
        embeddings = np.eye(4, dtype=np.float32)
        load_index.return_value = (embeddings, meta)

        model = MagicMock()
        model.encode.return_value = np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
        get_model.return_value = model

        result = retrieve_from_agents(
            _neutral_agents(12),
            [],
            top_k=DEFAULT_TOP_K,
            quality_floor=DEFAULT_QUALITY_FLOOR,
        )
        movie = next(c for c in result["candidates"] if c["tmdb_id"] == 1)
        self.assertEqual(movie["neutral_hits"], 12)
        self.assertEqual(movie["neutral_total"], 12)
        self.assertAlmostEqual(movie["neutral_hit_rate"], 1.0)
        self.assertFalse(movie["quality_candidate"])
        self.assertIn("neutral_hits=12", movie["quality_reason"])
        self.assertIn("toned_agents=0", movie["quality_reason"])

    @patch("scripts.retrieve._get_model")
    @patch("scripts.retrieve._load_index")
    def test_one_toned_convergence_marks_quality_candidate(
        self, load_index: MagicMock, get_model: MagicMock
    ) -> None:
        meta = _mini_meta()
        embeddings = np.eye(4, dtype=np.float32)
        load_index.return_value = (embeddings, meta)

        model = MagicMock()

        def fake_encode(text: str, normalize_embeddings: bool = True) -> np.ndarray:
            if "neutral" in text.lower():
                return np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
            return np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)

        model.encode.side_effect = fake_encode
        get_model.return_value = model

        agents = _neutral_agents(12, text="neutral shared hit")
        agents.append(
            {
                "agent_id": "P12",
                "role": "toned",
                "pseudos": [
                    {
                        "id": "t1",
                        "text": "toned converge hit",
                        "source": {"fragments": [], "channel_role": "toned"},
                    }
                ],
            }
        )

        result = retrieve_from_agents(
            agents,
            [],
            top_k=DEFAULT_TOP_K,
            quality_floor=DEFAULT_QUALITY_FLOOR,
        )
        movie = next(c for c in result["candidates"] if c["tmdb_id"] == 1)
        self.assertTrue(movie["quality_candidate"])
        self.assertIn("neutral_vote=1", movie["quality_reason"])
        self.assertIn("P12", movie["quality_reason"])
        self.assertIn("P12", movie["triggered_by"])

    @patch("scripts.retrieve._get_model")
    @patch("scripts.retrieve._load_index")
    def test_neutral_hit_respects_quality_floor(
        self, load_index: MagicMock, get_model: MagicMock
    ) -> None:
        meta = _mini_meta()
        embeddings = np.eye(4, dtype=np.float32)
        load_index.return_value = (embeddings, meta)

        model = MagicMock()

        def fake_encode(text: str, normalize_embeddings: bool = True) -> np.ndarray:
            if "strong" in text:
                return np.array([1.0, 0.0, 0.0, 0.0], dtype=np.float32)
            vec = np.array([0.35, 0.94, 0.0, 0.0], dtype=np.float32)
            return vec / np.linalg.norm(vec)

        model.encode.side_effect = fake_encode
        get_model.return_value = model

        agents = [
            {
                "agent_id": "P00",
                "pseudos": [
                    {
                        "id": "n1",
                        "text": "strong neutral",
                        "source": {"channel_role": "neutral", "fragments": []},
                    }
                ],
            },
            {
                "agent_id": "P01",
                "pseudos": [
                    {
                        "id": "n1",
                        "text": "weak neutral",
                        "source": {"channel_role": "neutral", "fragments": []},
                    }
                ],
            },
        ]

        result = retrieve_from_agents(
            agents,
            [],
            top_k=DEFAULT_TOP_K,
            quality_floor=DEFAULT_QUALITY_FLOOR,
        )
        movie_one = next(c for c in result["candidates"] if c["tmdb_id"] == 1)
        self.assertEqual(movie_one["neutral_hits"], 1)
        self.assertEqual(movie_one["neutral_total"], 2)
        self.assertAlmostEqual(movie_one["neutral_hit_rate"], 0.5)


if __name__ == "__main__":
    unittest.main()
