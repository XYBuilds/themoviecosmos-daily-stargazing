"""Unit tests for Phase 3.11.4 candidate funnel + pool diff channel decomposition."""

from __future__ import annotations

import unittest

from scripts.retrieve import (
    DEFAULT_HUMAN_BUDGET,
    DEFAULT_QUALITY_FLOOR,
    apply_candidate_funnel,
    compare_pool_diff_by_channel,
    dedupe_candidates_by_tmdb_id,
    pool_diff_by_channel_to_dict,
    sort_candidates_convergent,
)


def _cand(
    tmdb_id: int,
    *,
    similarity: float,
    hit_sources: list[dict],
    quality_candidate: bool = False,
) -> dict:
    return {
        "tmdb_id": tmdb_id,
        "title": f"Movie {tmdb_id}",
        "similarity": similarity,
        "quality_candidate": quality_candidate,
        "triggered_by": [],
        "hit_sources": hit_sources,
    }


class DedupeTests(unittest.TestCase):
    def test_merges_same_tmdb_id_hit_sources(self) -> None:
        a = _cand(
            42,
            similarity=0.5,
            hit_sources=[
                {
                    "agent_id": "A2",
                    "pseudo_id": "t1",
                    "channel_role": "toned",
                    "similarity": 0.5,
                    "fragments": [],
                }
            ],
        )
        b = _cand(
            42,
            similarity=0.7,
            hit_sources=[
                {
                    "agent_id": "A4",
                    "pseudo_id": "t2",
                    "channel_role": "focalized",
                    "similarity": 0.7,
                    "fragments": [],
                }
            ],
        )
        merged = dedupe_candidates_by_tmdb_id([a, b])
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["similarity"], 0.7)
        agents = {h["agent_id"] for h in merged[0]["hit_sources"]}
        self.assertEqual(agents, {"A2", "A4"})


class ConvergentSortTests(unittest.TestCase):
    def test_multi_channel_ranks_above_single_channel(self) -> None:
        single = _cand(
            1,
            similarity=0.99,
            hit_sources=[
                {
                    "agent_id": "A2",
                    "pseudo_id": "t1",
                    "channel_role": "toned",
                    "similarity": 0.99,
                    "fragments": [],
                }
            ],
        )
        multi = _cand(
            2,
            similarity=0.5,
            hit_sources=[
                {
                    "agent_id": "A2",
                    "pseudo_id": "n1",
                    "channel_role": "neutral",
                    "similarity": 0.5,
                    "fragments": [],
                },
                {
                    "agent_id": "A2",
                    "pseudo_id": "t1",
                    "channel_role": "focalized",
                    "similarity": 0.5,
                    "fragments": [],
                },
            ],
            quality_candidate=True,
        )
        ranked = sort_candidates_convergent(
            [single, multi], quality_floor=DEFAULT_QUALITY_FLOOR
        )
        self.assertEqual(ranked[0]["tmdb_id"], 2)
        self.assertGreater(
            ranked[0]["convergent_score"],
            ranked[1]["convergent_score"],
        )

    def test_multi_persona_adds_convergent_weight(self) -> None:
        one_persona = _cand(
            10,
            similarity=0.8,
            hit_sources=[
                {
                    "agent_id": "A2",
                    "pseudo_id": "t1",
                    "channel_role": "toned",
                    "similarity": 0.8,
                    "fragments": [],
                }
            ],
        )
        two_personas = _cand(
            11,
            similarity=0.6,
            hit_sources=[
                {
                    "agent_id": "A2",
                    "pseudo_id": "t1",
                    "channel_role": "toned",
                    "similarity": 0.6,
                    "fragments": [],
                },
                {
                    "agent_id": "A7",
                    "pseudo_id": "t1",
                    "channel_role": "toned",
                    "similarity": 0.55,
                    "fragments": [],
                },
            ],
        )
        ranked = sort_candidates_convergent(
            [one_persona, two_personas], quality_floor=DEFAULT_QUALITY_FLOOR
        )
        self.assertEqual(ranked[0]["tmdb_id"], 11)
        self.assertEqual(ranked[0]["convergence_persona_count"], 2)


class FunnelBudgetTests(unittest.TestCase):
    def test_caps_human_candidates(self) -> None:
        pool = [
            _cand(
                i,
                similarity=1.0 - i * 0.01,
                hit_sources=[
                    {
                        "agent_id": "A2",
                        "pseudo_id": "t1",
                        "channel_role": "toned",
                        "similarity": 1.0 - i * 0.01,
                        "fragments": [],
                    }
                ],
            )
            for i in range(25)
        ]
        result = apply_candidate_funnel(pool, human_budget=5)
        self.assertEqual(len(result["human_candidates"]), 5)
        self.assertEqual(result["meta"]["human_count"], 5)

    def test_audit_pool_collects_below_cap_judge_ge_one(self) -> None:
        pool = [
            _cand(
                1,
                similarity=0.9,
                hit_sources=[
                    {
                        "agent_id": "A2",
                        "pseudo_id": "t1",
                        "channel_role": "toned",
                        "similarity": 0.9,
                        "fragments": [],
                    }
                ],
            ),
            _cand(
                2,
                similarity=0.8,
                hit_sources=[
                    {
                        "agent_id": "A2",
                        "pseudo_id": "t1",
                        "channel_role": "toned",
                        "similarity": 0.8,
                        "fragments": [],
                    }
                ],
            ),
            _cand(
                3,
                similarity=0.7,
                hit_sources=[
                    {
                        "agent_id": "A2",
                        "pseudo_id": "t1",
                        "channel_role": "toned",
                        "similarity": 0.7,
                        "fragments": [],
                    }
                ],
            ),
        ]
        result = apply_candidate_funnel(
            pool,
            human_budget=1,
            judge_scores={1: 2, 2: 1, 3: 0},
            min_judge_score=1,
        )
        self.assertEqual([c["tmdb_id"] for c in result["human_candidates"]], [1])
        self.assertEqual([c["tmdb_id"] for c in result["audit_pool"]], [2])
        self.assertEqual([c["tmdb_id"] for c in result["judge_zero"]], [3])

    def test_focalized_counts_toward_extended_collision_ticket(self) -> None:
        focal_only = _cand(
            99,
            similarity=0.75,
            hit_sources=[
                {
                    "agent_id": "A2",
                    "pseudo_id": "n1",
                    "channel_role": "neutral",
                    "similarity": 0.75,
                    "fragments": [],
                },
                {
                    "agent_id": "A2",
                    "pseudo_id": "f1",
                    "channel_role": "focalized",
                    "similarity": 0.75,
                    "fragments": [],
                },
            ],
        )
        from scripts.retrieve import _apply_quality_fields

        _apply_quality_fields(
            focal_only, quality_floor=DEFAULT_QUALITY_FLOOR, neutral_total=1
        )
        self.assertTrue(focal_only["quality_candidate"])


class PoolDiffChannelTests(unittest.TestCase):
    def test_decomposes_net_new_by_provenance_channel(self) -> None:
        baseline = {
            "candidates": [
                {"tmdb_id": 1, "title": "Kept"},
            ]
        }
        design = {
            "candidates": [
                {"tmdb_id": 1, "title": "Kept"},
                {
                    "tmdb_id": 100,
                    "title": "Focal new",
                    "similarity": 0.6,
                    "hit_sources": [
                        {
                            "agent_id": "A2",
                            "pseudo_id": "f1",
                            "channel": "focalized",
                            "similarity": 0.6,
                            "fragments": [],
                        }
                    ],
                },
                {
                    "tmdb_id": 101,
                    "title": "Multi channel",
                    "similarity": 0.55,
                    "hit_sources": [
                        {
                            "agent_id": "A2",
                            "pseudo_id": "n1",
                            "channel_role": "neutral",
                            "similarity": 0.55,
                            "fragments": [],
                        },
                        {
                            "agent_id": "A4",
                            "pseudo_id": "t1",
                            "channel_role": "toned",
                            "similarity": 0.5,
                            "fragments": [],
                        },
                    ],
                },
            ]
        }
        diff = compare_pool_diff_by_channel(
            run_id="01-test",
            baseline_retrieve=baseline,
            design_retrieve=design,
        )
        self.assertEqual(diff.net_new_tmdb_ids, [100, 101])
        self.assertIn(100, diff.by_channel["focalized"])
        self.assertIn(101, diff.by_channel["neutral"])
        self.assertIn(101, diff.by_channel["toned"])
        payload = pool_diff_by_channel_to_dict(diff)
        self.assertEqual(payload["run_id"], "01-test")
        self.assertEqual(len(payload["net_new_details"]), 2)


if __name__ == "__main__":
    unittest.main()
