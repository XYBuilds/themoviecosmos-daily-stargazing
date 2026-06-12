"""Offline tests for Phase 3.11.6 pilot audit scaffolding."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.agents import PseudoSegment, load_deconstruction_from_file
from scripts.lib.phase311_pilot import (
    audit_center_truthfulness,
    audit_funnel_reasonable,
    audit_neutral_n1_unchanged,
    audit_persona_guards,
    build_default_pilot_manifest,
    go_no_go_pilot_recommendation,
    load_pilot_manifest,
    parse_pilot_runs,
)
from scripts.personas import AltElement, AltPoolOverlay, AltTerm

FIXTURE = _REPO / "tests" / "fixtures" / "01-grid-outage-deconstructed.json"


class Phase311PilotTests(unittest.TestCase):
    def test_default_manifest_single_grid_outage(self) -> None:
        manifest = build_default_pilot_manifest()
        self.assertEqual(len(manifest["runs"]), 1)
        self.assertEqual(manifest["runs"][0]["run_id"], "01-grid-outage")
        specs = parse_pilot_runs(manifest)
        self.assertEqual(len(specs[0].personas), 12)

    def test_center_truthfulness_pass(self) -> None:
        dec = load_deconstruction_from_file(FIXTURE)
        alt_pool = AltPoolOverlay(
            persona_id="The-Everyman",
            elements=[
                AltElement(
                    element_id="who-1",
                    original_term="Kepco SPC Power's Unit 2",
                    alternatives=[
                        AltTerm(term="a major power plant", valence="neutral")
                    ],
                )
            ],
            salience=["who-1"],
        )
        pseudo = PseudoSegment(
            "p1",
            (
                "On the plant floor, workers at Kepco SPC Power's Unit 2 face "
                "emergency load shedding as the grid strains under heat-driven demand."
            ),
            {
                "center": "who-1",
                "channel": "toned",
                "fragments": ["why-0", "how-0", "result-0"],
            },
            [],
            fit=0.7,
        )
        result = audit_center_truthfulness(pseudo, dec, alt_pool)
        self.assertTrue(result["pass"])

    def test_center_truthfulness_stuffing_risk(self) -> None:
        dec = load_deconstruction_from_file(FIXTURE)
        alt_pool = AltPoolOverlay(
            persona_id="The-Everyman",
            elements=[
                AltElement(
                    element_id="who-0",
                    original_term="The Philippines grid operator",
                    alternatives=[],
                )
            ],
            salience=["who-0"],
        )
        pseudo = PseudoSegment(
            "p1",
            (
                "Seasonal heat drove demand into a thin margin while officials "
                "ordered emergency measures across eleven generators and a "
                "large-scale power deficit unfolded."
            ),
            {
                "center": "who-0",
                "channel": "toned",
                "fragments": ["why-0", "how-0", "result-0"],
            },
            [],
            fit=0.6,
        )
        result = audit_center_truthfulness(pseudo, dec, alt_pool)
        self.assertFalse(result["pass"])
        self.assertTrue(result.get("stuffing_risk") or result["reason"])

    def test_focal_derivation_warning_is_diagnostic_only(self) -> None:
        dec = load_deconstruction_from_file(FIXTURE)
        alt_pool = AltPoolOverlay(
            persona_id="The-Everyman",
            elements=[
                AltElement(
                    element_id="who-0",
                    original_term="Philippines grid operator",
                    alternatives=[AltTerm(term="power grid", valence="neutral", provenance="hypernym")],
                ),
                AltElement(
                    element_id="how-2",
                    original_term="more than 950 megawatts became unavailable",
                    alternatives=[AltTerm(term="power shortage", valence="neutral", provenance="hypernym")],
                ),
                AltElement(
                    element_id="why-0",
                    original_term="Kepco SPC Power Unit 2 tripped offline alongside other long-running plant outages",
                    alternatives=[AltTerm(term="power plant outage", valence="neutral", provenance="hypernym")],
                ),
            ],
            salience=["how-2", "why-0", "who-0"],
        )
        pipeline = {
            "persona_id": "The-Everyman",
            "pseudos": [
                {
                    "id": "p1",
                    "text": (
                        "The Visayas grid was placed under red alert as more than "
                        "950 megawatts became unavailable across the power grid, "
                        "with emergency load shedding ordered to protect a critical "
                        "transmission line."
                    ),
                    "fit": 0.8,
                    "source": {
                        "center": "how-2",
                        "channel": "focalized",
                        "focal": "where-0",
                        "fragments": ["why-0", "how-1", "result-0"],
                    },
                },
                {
                    "id": "p2",
                    "text": (
                        "Seasonal heat drove demand into a thin operating margin "
                        "after a power plant outage, while emergency load shedding "
                        "spread across the power grid."
                    ),
                    "fit": 0.75,
                    "source": {
                        "center": "why-0",
                        "channel": "toned",
                        "fragments": ["why-0", "how-0", "result-0"],
                    },
                },
            ],
        }
        result = audit_persona_guards(
            "The-Everyman",
            pipeline,
            dec,
            alt_pool,
            expansion={"elements": []},
        )
        focal = result["focalized_derivation"]
        self.assertTrue(focal["pass"])
        self.assertTrue(focal["diagnostic_only"])
        self.assertGreater(focal["warning_count"], 0)
        self.assertTrue(result["fact_drift"]["pass"])
        self.assertTrue(result["center_truthfulness"]["pass"])

    def test_neutral_n1_unchanged(self) -> None:
        text = "neutral baseline wording"
        design = {"pseudos": [{"id": "n1", "text": text}]}
        baseline = {"pseudos": [{"id": "n1", "text": text}]}
        changed = {"pseudos": [{"id": "n1", "text": "different"}]}
        self.assertTrue(
            audit_neutral_n1_unchanged(design, baseline, "The-Everyman")["pass"]
        )
        self.assertFalse(
            audit_neutral_n1_unchanged(design, changed, "The-Everyman")["pass"]
        )

    def test_funnel_reasonable_meta(self) -> None:
        retrieve = {
            "candidates": [
                {
                    "tmdb_id": 1,
                    "similarity": 0.5,
                    "convergence_score": 3,
                },
                {
                    "tmdb_id": 2,
                    "similarity": 0.4,
                    "convergence_score": 2,
                },
            ],
            "funnel": {
                "deduped_count": 2,
                "sorted_count": 2,
                "human_count": 2,
                "human_budget": 10,
            },
        }
        result = audit_funnel_reasonable(retrieve)
        self.assertTrue(result["pass"])

    def test_go_no_go_guard_failure(self) -> None:
        audit = {
            "dimensions": {
                "fact_drift": {"pass": False, "hard_guard_failures": 2},
                "center_truthfulness": {"pass": True},
                "focalized_derivation": {"pass": True},
                "dual_floor": {"pass": True},
                "funnel": {"pass": True},
            },
            "pool_diff": {"net_new_tmdb_ids": []},
        }
        go = go_no_go_pilot_recommendation(audit, dry_run=False)
        self.assertEqual(go["verdict"], "Pipeline No-Go")

    def test_go_no_go_all_pass(self) -> None:
        audit = {
            "dimensions": {
                "fact_drift": {"pass": True, "hard_guard_failures": 0},
                "center_truthfulness": {"pass": True},
                "focalized_derivation": {"pass": True},
                "dual_floor": {
                    "pass": True,
                    "baseline_hits": {"lost_tmdb_ids": []},
                },
                "funnel": {"pass": True},
                "open_d_weak_fit": {"pass": True, "observations": []},
            },
            "personas": [
                {
                    "persona_id": "The-Everyman",
                    "pseudo_guard": {"kept_pseudos": 1, "dropped_pseudos": 0},
                    "center_truthfulness": {
                        "checks": [{"pass": True, "center": "who-0"}],
                    },
                }
            ],
            "pool_diff": {
                "baseline_candidate_count": 1,
                "net_new_tmdb_ids": [429918],
            },
        }
        go = go_no_go_pilot_recommendation(audit, dry_run=False)
        self.assertEqual(go["verdict"], "Pipeline Go")

    def test_load_pilot_manifest_roundtrip(self) -> None:
        manifest = build_default_pilot_manifest()
        path = _REPO / "output" / "Eval" / "phase3.11" / "_test-pilot-manifest.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        loaded = load_pilot_manifest(path)
        self.assertEqual(loaded["runs"][0]["run_id"], "01-grid-outage")
        path.unlink(missing_ok=True)


if __name__ == "__main__":
    unittest.main()
