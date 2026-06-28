"""Tests for A0 verbatim deconstruction and inlined objective expansion (Phase 3.8.1; inlined into fragment_ladder in Phase 3.12.1)."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.agents import load_deconstruction_from_file
from scripts.extract import strip_inert_fields, validate_deconstruction
from scripts.expand import (
    apply_touchstone_to_expansion,
    filter_hypernyms,
    list_expandable_elements,
    passes_objectivity_touchstone,
    validate_expansion,
)

_GRID_FIXTURE = _REPO / "tests" / "fixtures" / "01-grid-outage-deconstructed.json"
_INDIA_FIXTURE = _REPO / "tests" / "fixtures" / "india-heatwave-deconstructed.json"
_SLUM_EXPANSION = _REPO / "tests" / "fixtures" / "slum-expansion-sample.json"

_INERT_KEYS = frozenset({"tags", "geocode", "coordinates", "scale", "scene_archetype"})


def _collect_keys(obj, keys: set[str] | None = None) -> set[str]:
    found: set[str] = set() if keys is None else keys
    if isinstance(obj, dict):
        for key, value in obj.items():
            found.add(str(key))
            _collect_keys(value, found)
    elif isinstance(obj, list):
        for item in obj:
            _collect_keys(item, found)
    return found


class A0VerbatimTests(unittest.TestCase):
    def test_fixture_has_no_inert_fields(self) -> None:
        dec = load_deconstruction_from_file(_GRID_FIXTURE)
        keys = _collect_keys(dec)
        self.assertFalse(keys & _INERT_KEYS)
        self.assertNotIn("hypernym", keys)
        self.assertNotIn("hypernyms", keys)

    def test_validate_rejects_inert_fields(self) -> None:
        sample = {
            "anchor": {"dct": "2026-05", "report_locale": None},
            "when": {
                "absolute": [],
                "relative": [],
                "daypart": [],
                "season": [],
                "fuzzy_era": [],
                "cultural": [],
                "anchored": [],
                "duration": [],
                "recurrence": [],
                "modality": [],
                "timezone": [],
            },
            "where": [
                {
                    "text": "Dharavi, Mumbai",
                    "tags": ["slum"],
                    "geocode": {"country": "India"},
                    "scene_archetype": ["urban"],
                    "scale": "city",
                    "role": ["site of occurrence"],
                }
            ],
            "who": [],
            "why": [],
            "how": [],
            "result": [],
        }
        errors, _ = validate_deconstruction(sample)
        self.assertTrue(any("inert_field" in e for e in errors))

    def test_strip_inert_fields(self) -> None:
        raw = {
            "where": [{"text": "Mumbai", "tags": ["city"], "scale": "metro", "role": ["site"]}],
            "who": [{"text": "residents", "tags": ["civilians"], "role_in_event": ["affected"]}],
        }
        cleaned = strip_inert_fields(raw)
        self.assertNotIn("tags", cleaned["where"][0])
        self.assertNotIn("scale", cleaned["where"][0])
        self.assertEqual(cleaned["where"][0]["role"], ["site"])
        self.assertNotIn("tags", cleaned["who"][0])

    def test_output_has_no_hypernym_field(self) -> None:
        dec = load_deconstruction_from_file(_GRID_FIXTURE)
        errors, _ = validate_deconstruction(dec)
        self.assertEqual(errors, [])
        keys = _collect_keys(dec)
        self.assertNotIn("hypernyms", keys)
        self.assertNotIn("hypernym", keys)


class ObjectiveExpansionTests(unittest.TestCase):
    def test_list_expandable_elements(self) -> None:
        dec = load_deconstruction_from_file(_INDIA_FIXTURE)
        elements = list_expandable_elements(dec)
        ids = {e["element_id"] for e in elements}
        self.assertIn("where-0", ids)
        self.assertIn("who-0", ids)
        self.assertIn("who-1", ids)
        self.assertIn("why-0", ids)
        self.assertIn("how-0", ids)
        self.assertIn("result-0", ids)
        self.assertIn("result-1", ids)

    def test_touchstone_keeps_objective_hypernym(self) -> None:
        self.assertTrue(passes_objectivity_touchstone("slum"))
        self.assertTrue(passes_objectivity_touchstone("Mumbai"))
        kept, rejected = filter_hypernyms(
            ["slum", "Mumbai", "India"],
            surface="Dharavi slum, Mumbai",
        )
        self.assertEqual(kept, ["slum", "Mumbai", "India"])
        self.assertEqual(rejected, [])

    def test_touchstone_rejects_lens_framing(self) -> None:
        self.assertFalse(passes_objectivity_touchstone("destiny's cage"))
        self.assertFalse(passes_objectivity_touchstone("宿命的牢笼"))
        kept, rejected = filter_hypernyms(
            ["slum", "destiny's cage", "宿命的牢笼", "Mumbai"],
            surface="Dharavi slum, Mumbai",
        )
        self.assertIn("slum", kept)
        self.assertIn("Mumbai", kept)
        self.assertIn("destiny's cage", rejected)
        self.assertIn("宿命的牢笼", rejected)

    def test_expansion_touchstone_filters_fixture(self) -> None:
        dec = {
            "where": [{"text": "Dharavi slum, Mumbai", "role": ["site of occurrence"]}],
            "who": [{"text": "Dharavi residents", "role_in_event": ["affected"]}],
            "why": [],
            "how": [],
            "result": [],
            "anchor": {},
            "when": {},
        }
        raw = json.loads(_SLUM_EXPANSION.read_text(encoding="utf-8"))
        filtered = apply_touchstone_to_expansion(raw)
        where_row = next(e for e in filtered["elements"] if e["element_id"] == "where-0")
        who_row = next(e for e in filtered["elements"] if e["element_id"] == "who-0")
        self.assertIn("slum", where_row["hypernyms"])
        self.assertIn("Mumbai", where_row["hypernyms"])
        self.assertNotIn("destiny's cage", where_row["hypernyms"])
        self.assertNotIn("宿命的牢笼", where_row["hypernyms"])
        self.assertIn("civilians", who_row["hypernyms"])
        self.assertNotIn("crushing the powerless", who_row["hypernyms"])

        errors, warnings = validate_expansion(raw, dec)
        self.assertEqual(errors, [])
        self.assertTrue(any("touchstone rejected" in w for w in warnings))


class InlinedExpansionModuleTests(unittest.TestCase):
    """Phase 3.12.1: objective expansion lives in fragment_ladder, not a standalone pass."""

    def test_objective_expansion_module_removed(self) -> None:
        import importlib

        with self.assertRaises(ModuleNotFoundError):
            importlib.import_module("scripts.objective_expansion")

    def test_expansion_contract_inlined_no_external_file(self) -> None:
        from scripts.expand import load_expansion_contract

        contract = load_expansion_contract()
        self.assertIn("Objective Expansion Contract", contract)
        self.assertIn("{{deconstruction_json}}", contract)
        legacy = _REPO / "prompts" / "_shared" / "objective_expansion_contract.md"
        self.assertFalse(legacy.exists())

    def test_render_prompt_self_contained(self) -> None:
        from scripts.expand import render_expansion_prompt

        dec = load_deconstruction_from_file(_INDIA_FIXTURE)
        prompt = render_expansion_prompt(dec)
        self.assertNotIn("{{deconstruction_json}}", prompt)
        self.assertIn("who-0", prompt)


if __name__ == "__main__":
    unittest.main()
