"""Offline tests for Phase 3.11.7 full-batch summary helpers."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.run_phase311_full_batch import (
    render_phase3117_report,
    summarize_phase3117_run,
    write_review_artifacts,
)


def _candidate(tmdb_id: int, *sources: dict) -> dict:
    return {
        "tmdb_id": tmdb_id,
        "title": f"Movie {tmdb_id}",
        "overview": "A test overview.",
        "similarity": 0.8,
        "hit_sources": list(sources),
        "triggered_by": sorted(
            {
                str(src.get("agent_id"))
                for src in sources
                if src.get("search_unit_kind") == "persona-semantic"
            }
        ),
        "match_diagnostics": {
            "search_unit_kinds": sorted(
                {
                    str(src.get("search_unit_kind"))
                    for src in sources
                    if src.get("search_unit_kind")
                }
            ),
            "center_dimensions": sorted(
                {
                    str(src.get("center_element", "")).split("-", 1)[0]
                    for src in sources
                    if src.get("center_element") and "-" in str(src.get("center_element"))
                }
            ),
            "surface_match": any(
                src.get("search_unit_kind") == "surface-fragment-bundle" for src in sources
            ),
            "event_match": any(
                src.get("search_unit_kind") == "event-fragment-bundle" for src in sources
            ),
            "persona_semantic_match": any(
                src.get("search_unit_kind") == "persona-semantic" for src in sources
            ),
        },
    }


def _write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class Phase3117SummaryTests(unittest.TestCase):
    def test_summary_decomposes_search_unit_kind_and_human_two_audit(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            baseline = root / "phase3.10"
            design = root / "phase3.11" / "full"
            run_dir = design / "01-grid-outage"
            base_run = baseline / "01-grid-outage"
            _write_json(
                base_run / "retrieve.json",
                {"candidates": [{"tmdb_id": 1, "title": "Base kept"}, {"tmdb_id": 9, "title": "Lost"}]},
            )
            _write_json(
                run_dir / "retrieve.json",
                {
                    "candidates": [
                        {"tmdb_id": 1, "title": "Base kept", "hit_sources": []},
                        _candidate(
                            2,
                            {
                                "agent_id": "A2",
                                "pseudo_id": "su-surface-1",
                                "search_unit_kind": "surface-fragment-bundle",
                                "similarity": 0.8,
                                "fragments": ["who-0"],
                            },
                        ),
                        _candidate(
                            3,
                            {
                                "agent_id": "A2",
                                "pseudo_id": "su-event-1",
                                "search_unit_kind": "event-fragment-bundle",
                                "similarity": 0.8,
                                "fragments": ["why-0"],
                            },
                            {
                                "agent_id": "A4",
                                "pseudo_id": "su-persona-1",
                                "search_unit_kind": "persona-semantic",
                                "center_element": "result-0",
                                "similarity": 0.7,
                                "fragments": ["result-0"],
                            },
                        ),
                    ],
                    "audit_pool": [{"tmdb_id": 4}],
                    "judge_zero": [{"tmdb_id": 9}],
                    "funnel": {"human_budget": 19, "human_count": 3},
                },
            )
            _write_json(
                run_dir / "audit.json",
                {
                    "all_automated_pass": True,
                    "dimensions": {"fact_drift": {"hard_guard_failures": 0}},
                },
            )
            _write_json(
                baseline / "llm-judge-scores.json",
                {
                    "scores": [
                        {"run_id": "01-grid-outage", "tmdb_id": "9", "human_score": 2},
                        {"run_id": "01-grid-outage", "tmdb_id": "1", "human_score": 1},
                    ]
                },
            )

            summary = summarize_phase3117_run(
                output_dir=design,
                baseline_dir=baseline,
                judge_json=baseline / "llm-judge-scores.json",
                run_ids=["01-grid-outage"],
            )

            self.assertEqual(summary["totals"]["net_new_candidates"], 2)
            self.assertEqual(summary["totals"]["lost_candidates"], 1)
            self.assertEqual(
                summary["search_unit_kind_decomposition"]["exclusive_counts"][
                    "surface-fragment-bundle"
                ],
                1,
            )
            self.assertEqual(summary["search_unit_kind_decomposition"]["collision_gain_count"], 1)
            self.assertEqual(summary["tuning_compass"]["persona_net_new_counts"], {"A4": 1})
            self.assertFalse(
                summary["rejection_audit"]["zero_human_two_killed_by_judge_zero"]
            )
            self.assertTrue((run_dir / "pool-diff-search-unit-kind.json").is_file())
            self.assertIn("search_unit_kind 分解", render_phase3117_report(summary))

    def test_review_artifacts_write_high_hit_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            run_dir = root / "01-grid-outage"
            (run_dir / "reality.md").parent.mkdir(parents=True, exist_ok=True)
            (run_dir / "reality.md").write_text("# reality", encoding="utf-8")
            _write_json(
                run_dir / "retrieve.json",
                {
                    "candidates": [
                        _candidate(
                            42,
                            {
                                "agent_id": "A2",
                                "pseudo_id": "su-persona-1",
                                "search_unit_kind": "persona-semantic",
                                "center_element": "who-0",
                                "similarity": 0.9,
                                "fragments": ["who-0", "why-0", "how-0", "result-0", "result-1"],
                            },
                        )
                    ]
                },
            )
            write_review_artifacts(root, min_score=5)
            review = (root / "high-hit-score-review.md").read_text(encoding="utf-8")
            self.assertIn("POV变换", review)
            self.assertIn("pseudo命中分合计", review)
            meta = json.loads((root / "high-hit-score-review.json").read_text(encoding="utf-8"))
            self.assertEqual(meta["high_hit_candidate_count"], 1)


if __name__ == "__main__":
    unittest.main()