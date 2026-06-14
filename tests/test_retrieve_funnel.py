"""Unit tests for Phase 3.11.4 candidate funnel + pool diff (ADR-0009 search_unit_kind)."""

from __future__ import annotations

import unittest

from scripts.retrieve import (
    DEFAULT_QUALITY_FLOOR,
    apply_candidate_funnel,
    compare_pool_diff_by_search_unit_kind,
    dedupe_candidates_by_tmdb_id,
    pool_diff_by_search_unit_kind_to_dict,
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


class SearchUnitFunnelTests(unittest.TestCase):
    def test_surface_event_persona_semantic_match_beats_plain_single_pseudo(self) -> None:
        plain = _cand(
            1,
            similarity=0.99,
            hit_sources=[
                {
                    "agent_id": "A2",
                    "pseudo_id": "su-persona-1",
                    "search_unit_kind": "persona-semantic",
                    "similarity": 0.99,
                    "fragments": [],
                }
            ],
        )
        structured = _cand(
            2,
            similarity=0.5,
            hit_sources=[
                {
                    "agent_id": "A2",
                    "pseudo_id": "su-surface-1",
                    "search_unit_kind": "surface-fragment-bundle",
                    "similarity": 0.5,
                    "fragments": ["who-0"],
                },
                {
                    "agent_id": "A2",
                    "pseudo_id": "su-event-1",
                    "search_unit_kind": "event-fragment-bundle",
                    "similarity": 0.5,
                    "fragments": ["why-0", "how-0"],
                },
                {
                    "agent_id": "A2",
                    "pseudo_id": "su-persona-The-Ruler-p1",
                    "search_unit_kind": "persona-semantic",
                    "center_element": "result-0",
                    "similarity": 0.5,
                    "fragments": ["result-0"],
                },
            ],
        )
        ranked = sort_candidates_convergent(
            [plain, structured], quality_floor=DEFAULT_QUALITY_FLOOR
        )
        self.assertEqual(ranked[0]["tmdb_id"], 2)
        diag = ranked[0]["match_diagnostics"]
        self.assertTrue(diag["surface_match"])
        self.assertTrue(diag["event_match"])
        self.assertTrue(diag["persona_semantic_match"])
        self.assertEqual(diag["center_dimensions"], ["result"])

    def test_quality_candidate_uses_objective_plus_persona_semantic_match(self) -> None:
        pool = [
            _cand(
                7,
                similarity=0.8,
                hit_sources=[
                    {
                        "agent_id": "A2",
                        "pseudo_id": "su-event-1",
                        "search_unit_kind": "event-fragment-bundle",
                        "similarity": 0.8,
                        "fragments": ["why-0"],
                    },
                    {
                        "agent_id": "A2",
                        "pseudo_id": "su-persona-The-Ruler-p1",
                        "search_unit_kind": "persona-semantic",
                        "similarity": 0.8,
                        "fragments": ["result-0"],
                    },
                ],
            )
        ]
        result = apply_candidate_funnel(pool, human_budget=1)
        self.assertTrue(result["human_candidates"][0]["quality_candidate"])
        self.assertIn("objective_match=1", result["human_candidates"][0]["quality_reason"])


class DedupeTests(unittest.TestCase):
    def test_merges_same_tmdb_id_hit_sources(self) -> None:
        a = _cand(
            42,
            similarity=0.5,
            hit_sources=[
                {
                    "agent_id": "A2",
                    "pseudo_id": "su-persona-1",
                    "search_unit_kind": "persona-semantic",
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
                    "pseudo_id": "su-persona-2",
                    "search_unit_kind": "persona-semantic",
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
    def test_search_unit_kind_convergence_ranks_above_plain_single_pseudo(self) -> None:
        single = _cand(
            1,
            similarity=0.99,
            hit_sources=[
                {
                    "agent_id": "A2",
                    "pseudo_id": "su-persona-1",
                    "search_unit_kind": "persona-semantic",
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
                    "pseudo_id": "su-surface-1",
                    "search_unit_kind": "surface-fragment-bundle",
                    "similarity": 0.5,
                    "fragments": ["who-0"],
                },
                {
                    "agent_id": "A2",
                    "pseudo_id": "su-event-1",
                    "search_unit_kind": "event-fragment-bundle",
                    "similarity": 0.5,
                    "fragments": ["why-0"],
                },
                {
                    "agent_id": "A2",
                    "pseudo_id": "su-persona-The-Ruler-p1",
                    "search_unit_kind": "persona-semantic",
                    "center_element": "result-0",
                    "similarity": 0.5,
                    "fragments": ["result-0"],
                },
            ],
            quality_candidate=True,
        )
        ranked = sort_candidates_convergent(
            [single, multi], quality_floor=DEFAULT_QUALITY_FLOOR
        )
        self.assertEqual(ranked[0]["tmdb_id"], 2)
        self.assertEqual(
            ranked[0]["match_diagnostics"]["search_unit_kinds"],
            ["event-fragment-bundle", "persona-semantic", "surface-fragment-bundle"],
        )
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
                    "pseudo_id": "su-persona-A2-p1",
                    "search_unit_kind": "persona-semantic",
                    "center_element": "why-0",
                    "similarity": 0.8,
                    "fragments": ["why-0"],
                }
            ],
        )
        two_personas = _cand(
            11,
            similarity=0.6,
            hit_sources=[
                {
                    "agent_id": "A2",
                    "pseudo_id": "su-persona-A2-p1",
                    "search_unit_kind": "persona-semantic",
                    "center_element": "why-0",
                    "similarity": 0.6,
                    "fragments": ["why-0"],
                },
                {
                    "agent_id": "A7",
                    "pseudo_id": "su-persona-A7-p1",
                    "search_unit_kind": "persona-semantic",
                    "center_element": "result-0",
                    "similarity": 0.55,
                    "fragments": ["result-0"],
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
                        "pseudo_id": "su-persona-1",
                        "search_unit_kind": "persona-semantic",
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
                        "pseudo_id": "su-persona-1",
                        "search_unit_kind": "persona-semantic",
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
                        "pseudo_id": "su-persona-1",
                        "search_unit_kind": "persona-semantic",
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
                        "pseudo_id": "su-persona-1",
                        "search_unit_kind": "persona-semantic",
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

    def test_persona_semantic_with_objective_match_counts_toward_quality_candidate(self) -> None:
        candidate = _cand(
            99,
            similarity=0.75,
            hit_sources=[
                {
                    "agent_id": "A2",
                    "pseudo_id": "su-event-1",
                    "search_unit_kind": "event-fragment-bundle",
                    "similarity": 0.75,
                    "fragments": ["why-0"],
                },
                {
                    "agent_id": "A2",
                    "pseudo_id": "su-persona-A2-p1",
                    "search_unit_kind": "persona-semantic",
                    "center_element": "result-0",
                    "similarity": 0.75,
                    "fragments": ["result-0"],
                },
            ],
        )
        from scripts.retrieve import _apply_quality_fields

        _apply_quality_fields(candidate, quality_floor=DEFAULT_QUALITY_FLOOR)
        self.assertTrue(candidate["quality_candidate"])


class PoolDiffSearchUnitKindTests(unittest.TestCase):
    def test_decomposes_net_new_by_search_unit_kind(self) -> None:
        baseline = {"candidates": [{"tmdb_id": 1, "title": "Kept"}]}
        design = {
            "candidates": [
                {"tmdb_id": 1, "title": "Kept"},
                {
                    "tmdb_id": 200,
                    "title": "Surface only",
                    "similarity": 0.6,
                    "hit_sources": [
                        {
                            "agent_id": "A2",
                            "pseudo_id": "su-surface-1",
                            "search_unit_kind": "surface-fragment-bundle",
                            "similarity": 0.6,
                            "fragments": ["who-0"],
                        }
                    ],
                },
                {
                    "tmdb_id": 201,
                    "title": "Collision gain",
                    "similarity": 0.7,
                    "hit_sources": [
                        {
                            "agent_id": "A2",
                            "pseudo_id": "su-event-1",
                            "search_unit_kind": "event-fragment-bundle",
                            "similarity": 0.7,
                            "fragments": ["why-0"],
                        },
                        {
                            "agent_id": "A2",
                            "pseudo_id": "su-persona-A2-p1",
                            "search_unit_kind": "persona-semantic",
                            "center_element": "result-0",
                            "similarity": 0.65,
                            "fragments": ["result-0"],
                        },
                    ],
                },
            ]
        }
        diff = compare_pool_diff_by_search_unit_kind(
            run_id="01-test",
            baseline_retrieve=baseline,
            design_retrieve=design,
        )
        self.assertEqual(diff.net_new_tmdb_ids, [200, 201])
        self.assertIn(200, diff.by_search_unit_kind["surface-fragment-bundle"])
        self.assertIn(201, diff.by_search_unit_kind["event-fragment-bundle"])
        self.assertIn(201, diff.by_search_unit_kind["persona-semantic"])
        self.assertEqual(diff.collision_gain_tmdb_ids, [201])
        payload = pool_diff_by_search_unit_kind_to_dict(diff)
        self.assertEqual(payload["run_id"], "01-test")
        self.assertEqual(payload["collision_gain_tmdb_ids"], [201])


if __name__ == "__main__":
    unittest.main()