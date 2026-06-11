"""Offline tests for Phase 3.11.1 pretest scaffolding."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.lib.phase311_pretest import (
    build_default_pretest_manifest,
    compare_pool_diff,
    GapATarget,
    go_no_go_recommendation,
    inject_adr8_composition_mode,
    load_gap_a_samples,
    parse_adr8_pseudos_response,
    pool_diff_result_to_dict,
    summarize_center_granularity,
)
from scripts.agents import _known_fragment_ids, annotate_fragment_ids
from scripts.personas import load_deconstruction_from_file


class Phase311PretestTests(unittest.TestCase):
    def test_gap_a_sample_count_is_eight(self) -> None:
        rows = load_gap_a_samples()
        self.assertEqual(len(rows), 8)
        run_ids = {r["run_id"] for r in rows}
        self.assertIn("01-grid-outage", run_ids)
        self.assertIn("07-migration-border", run_ids)

    def test_manifest_covers_gap_a_runs(self) -> None:
        manifest = build_default_pretest_manifest()
        self.assertEqual(manifest["gap_a_sample_count"], 8)
        run_ids = [r["run_id"] for r in manifest["runs"]]
        self.assertEqual(len(run_ids), 5)
        self.assertIn("09-cultural-backlash", run_ids)

    def test_inject_adr8_composition_mode_marker(self) -> None:
        prompt = inject_adr8_composition_mode("base", salience=["who-0", "why-0"])
        self.assertIn("Composition mode: ADR-0008", prompt)
        self.assertIn("who-0", prompt)

    def test_parse_adr8_pseudos_response(self) -> None:
        fixture = _REPO / "tests" / "fixtures" / "01-grid-outage-deconstructed.json"
        dec = load_deconstruction_from_file(fixture)
        known_frags = _known_fragment_ids(annotate_fragment_ids(dec))
        known_elements = {"who-0", "who-1", "why-0", "how-0", "result-0"}
        raw = json.dumps(
            {
                "pseudos": [
                    {
                        "id": "p1",
                        "text": (
                            "From the plant floor, a worker watches officials order "
                            "emergency load shedding as a power grid strain hits the "
                            "region during a major power shortfall."
                        ),
                        "fit": 0.8,
                        "center": "who-1",
                        "channel": "focalized",
                        "focal": "who-1",
                        "source": {"fragments": ["why-0", "how-0", "result-0"]},
                    },
                    {
                        "id": "p2",
                        "text": (
                            "Grid operators face a large-scale power deficit after "
                            "seasonal heat drove demand into a thin margin, forcing "
                            "emergency measures across the power grid."
                        ),
                        "fit": 0.75,
                        "center": "why-0",
                        "channel": "toned",
                        "source": {"fragments": ["why-0", "how-0"]},
                    },
                ]
            }
        )
        pseudos = parse_adr8_pseudos_response(
            raw,
            agent_id="The-Everyman",
            known_fragments=known_frags,
            known_elements=known_elements,
        )
        self.assertEqual(len(pseudos), 2)
        self.assertEqual(pseudos[0].source.get("channel"), "focalized")
        self.assertEqual(pseudos[0].source.get("center"), "who-1")
        self.assertEqual(pseudos[1].source.get("channel"), "toned")

    def test_pool_diff_net_new(self) -> None:
        baseline = {"candidates": [{"tmdb_id": 1, "title": "A"}]}
        pretest = {
            "candidates": [
                {"tmdb_id": 1, "title": "A"},
                {"tmdb_id": 429918, "title": "Survival Family", "similarity": 0.44},
            ]
        }
        targets = [
            GapATarget(
                tmdb_id="429918",
                title="Survival Family",
                human_score=2,
                judge_score=1,
                judge_resonance_type="表层沾边",
                rationale="",
            )
        ]
        diff = compare_pool_diff(
            run_id="01-grid-outage",
            baseline_retrieve=baseline,
            pretest_retrieve=pretest,
            gap_a_targets=targets,
        )
        self.assertEqual(diff.net_new_tmdb_ids, [429918])
        self.assertEqual(len(diff.gap_a_targets_in_net_new), 1)
        d = pool_diff_result_to_dict(diff)
        self.assertIn("net_new_tmdb_ids", d)

    def test_go_no_go_heuristic(self) -> None:
        go = go_no_go_recommendation(
            {
                "total_net_new_candidates": 5,
                "gap_a_targets_recalled_net_new": 2,
                "runs_with_gap_a_net_new": 2,
                "run_count": 5,
            }
        )
        self.assertEqual(go["verdict"], "Go")

        no = go_no_go_recommendation(
            {
                "total_net_new_candidates": 0,
                "gap_a_targets_recalled_net_new": 0,
                "runs_with_gap_a_net_new": 0,
                "run_count": 5,
            }
        )
        self.assertEqual(no["verdict"], "No-Go")

    def test_center_granularity_summary(self) -> None:
        pipelines = [
            {
                "persona_id": "The-Everyman",
                "pseudos": [
                    {"id": "n1"},
                    {
                        "id": "p1",
                        "source": {"center": "who-1", "channel": "focalized"},
                    },
                    {
                        "id": "p2",
                        "source": {"center": "why-0", "channel": "toned"},
                    },
                ],
            }
        ]
        summary = summarize_center_granularity(pipelines)
        self.assertEqual(summary["center_element_counts"]["who-1"], 1)
        self.assertEqual(summary["channel_counts"]["focalized"], 1)


if __name__ == "__main__":
    unittest.main()
