"""Offline checks for the persona pipeline (ADR-0009 search-unit path, no LLM)."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.agents import (
    PseudoSegment,
    load_deconstruction_from_file,
    parse_search_units_response,
)
from scripts.rewrite import (
    AltElement,
    AltPoolOverlay,
    AltTerm,
    annotate_element_ids,
    build_alt_pool_overlay,
    build_fragment_bundle_search_units,
    build_fragment_ladders,
    build_screenwriter_user_prompt,
    build_search_units_payload,
    known_element_ids,
    list_persona_ids,
    load_persona_card,
    overlay_forbids_decon_fork,
    parse_alt_pool_response,
    render_persona_prompt,
    run_persona_pipeline,
    validate_salience,
)
from scripts.run_persona_batch import (
    load_a1_agent_from_phase36,
    split_obs_holdout,
)

FIXTURE = _REPO / "tests" / "fixtures" / "01-grid-outage-deconstructed.json"


def _fixture_dec_inner() -> dict:
    return load_deconstruction_from_file(FIXTURE)


def _known_elements() -> set[str]:
    return known_element_ids(_fixture_dec_inner())


def _expansion_fixture() -> dict:
    return {
        "elements": [
            {
                "element_id": "who-0",
                "surface": "Philippines grid operator",
                "hypernyms": ["power grid", "critical infrastructure"],
            },
            {
                "element_id": "where-0",
                "surface": "Visayas, Philippines",
                "hypernyms": ["Visayas", "Philippines", "Southeast Asia"],
            },
            {
                "element_id": "why-0",
                "surface": "Kepco SPC Power Unit 2 tripped offline alongside other long-running plant outages",
                "hypernyms": ["power plant outage", "supply shortfall"],
            },
        ]
    }


def _alt_pool_json() -> str:
    return json.dumps(
        {
            "persona_id": "The-Ruler",
            "elements": [
                {
                    "element_id": "who-0",
                    "original_term": "Philippines grid operator",
                    "alternatives": [
                        {"term": "grid steward", "valence": "positive", "provenance": "lens"},
                        {"term": "grid operator", "valence": "neutral", "provenance": "hypernym"},
                        {"term": "failing bureaucracy", "valence": "negative", "provenance": "lens"},
                    ],
                },
                {
                    "element_id": "where-0",
                    "original_term": "Visayas, Philippines",
                    "alternatives": [
                        {"term": "Visayas", "valence": "neutral", "provenance": "hypernym"},
                    ],
                },
                {
                    "element_id": "why-0",
                    "original_term": "Kepco SPC Power Unit 2 tripped offline alongside other long-running plant outages",
                    "alternatives": [
                        {"term": "restored balance after a trip", "valence": "positive", "provenance": "lens"},
                        {"term": "unit trip plus outages", "valence": "neutral", "provenance": "lens"},
                        {"term": "power plant outage", "valence": "neutral", "provenance": "hypernym"},
                        {"term": "cascade of plant failures", "valence": "negative", "provenance": "lens"},
                    ],
                },
            ],
        }
    )


def _alt_pool_json_with_salience(salience: list[str] | None = None) -> str:
    data = json.loads(_alt_pool_json())
    if salience is not None:
        data["salience"] = salience
    return json.dumps(data)


def _full_expansion_fixture() -> dict:
    """Expansion rows for all fixture element ids used in salience tests."""
    dec = _fixture_dec_inner()
    ann = annotate_element_ids(dec)
    elements: list[dict] = []
    for section in ("who", "where", "why", "how", "result"):
        for item in ann.get(section) or []:
            if isinstance(item, dict) and item.get("id"):
                eid = str(item["id"])
                text = str(item.get("text", "") or item.get("step", "") or "").strip()
                elements.append(
                    {
                        "element_id": eid,
                        "surface": text,
                        "hypernyms": [f"{section} hypernym"],
                    }
                )
    return {"elements": elements}


def _native_search_units_json() -> str:
    """Two ADR-0009 native search units with distinct centers."""
    return json.dumps(
        {
            "search_units": [
                {
                    "id": "p1",
                    "center_element": "why-0",
                    "supporting_elements": ["who-0", "how-0", "result-0"],
                    "search_text": (
                        "A power plant outage forced a grid authority to declare a "
                        "high-level warning as demand surged across the power grid."
                    ),
                    "fit": 0.8,
                },
                {
                    "id": "p2",
                    "center_element": "who-0",
                    "supporting_elements": ["why-0", "how-0", "result-0"],
                    "search_text": (
                        "A grid authority faced public scarcity after infrastructure "
                        "failures forced emergency power rationing across the region."
                    ),
                    "fit": 0.7,
                },
            ]
        }
    )


def _good_search_unit_segments() -> list[PseudoSegment]:
    return parse_search_units_response(
        _native_search_units_json(),
        agent_id="The-Ruler",
        known_elements=_known_elements(),
        require_fit=True,
    )


class FragmentLadderSearchUnitTests(unittest.TestCase):
    def test_build_fragment_ladders_maps_old_layers_to_new_levels(self) -> None:
        overlay = parse_alt_pool_response(
            _alt_pool_json_with_salience(["who-0", "where-0", "why-0", "how-0"]),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        ladders = build_fragment_ladders(overlay, _expansion_fixture())
        who = ladders["who-0"].to_dict()
        self.assertIn("surface", who)
        self.assertIn("objective_close", who)
        self.assertIn("interpretive", who)
        objective_terms = {row["text"] for row in who["objective_close"]}
        interpretive_terms = {row["text"] for row in who["interpretive"]}
        self.assertIn("power grid", objective_terms)
        self.assertIn("grid steward", interpretive_terms)

    def test_fragment_bundle_units_use_only_objective_levels(self) -> None:
        overlay = parse_alt_pool_response(
            _alt_pool_json_with_salience(["who-0", "where-0", "why-0", "how-0"]),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        units = build_fragment_bundle_search_units(
            build_fragment_ladders(overlay, _expansion_fixture())
        )
        self.assertEqual(
            {unit.kind for unit in units},
            {"surface-fragment-bundle", "event-fragment-bundle"},
        )
        for unit in units:
            self.assertTrue(unit.search_text)
            self.assertFalse(unit.persona_id)
            self.assertTrue(
                all(
                    fragment.level
                    in {
                        "surface",
                        "alias",
                        "objective_close",
                        "objective_mid",
                        "objective_broad",
                    }
                    for fragment in unit.fragments
                )
            )

    def test_build_search_units_payload_adds_persona_semantic_units(self) -> None:
        overlay = parse_alt_pool_response(
            _alt_pool_json_with_salience(["who-0", "where-0", "why-0", "how-0"]),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        pseudo = PseudoSegment(
            "p1",
            "A grid authority faces public scarcity after infrastructure failures force emergency power rationing.",
            {
                "center": "why-0",
                "fragments": ["who-0", "how-0", "result-0"],
            },
            [],
            fit=0.8,
        )
        payload = build_search_units_payload(
            persona_id="The-Ruler",
            alt_pool=overlay,
            pseudos=[pseudo],
            expansion=_full_expansion_fixture(),
            known_elements=_known_elements(),
        )
        self.assertIn("fragment_ladders", payload)
        units = payload["search_units"]
        self.assertEqual(len(units["persona_semantic_units"]), 1)
        self.assertEqual(
            units["persona_semantic_units"][0]["center_element"],
            "why-0",
        )

    def test_build_search_units_payload_has_no_channel_field(self) -> None:
        overlay = parse_alt_pool_response(
            _alt_pool_json_with_salience(["who-0", "why-0", "how-0", "result-0"]),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        payload = build_search_units_payload(
            persona_id="The-Ruler",
            alt_pool=overlay,
            pseudos=_good_search_unit_segments(),
            expansion=_full_expansion_fixture(),
            known_elements=_known_elements(),
        )
        serialized = json.dumps(payload)
        self.assertNotIn('"channel"', serialized)
        self.assertNotIn('"channel_role"', serialized)
        self.assertEqual(len(payload["search_units"]["persona_semantic_units"]), 2)


class NativeSearchUnitParserTests(unittest.TestCase):
    def test_parse_native_units_into_segments(self) -> None:
        segs = _good_search_unit_segments()
        self.assertEqual(len(segs), 2)
        self.assertEqual(segs[0].source["center"], "why-0")
        self.assertEqual(segs[0].source["fragments"], ["who-0", "how-0", "result-0"])
        self.assertEqual(segs[0].fit, 0.8)

    def test_parse_native_units_rejects_duplicate_center(self) -> None:
        data = json.loads(_native_search_units_json())
        data["search_units"][1]["center_element"] = "why-0"
        with self.assertRaises(ValueError) as ctx:
            parse_search_units_response(
                json.dumps(data),
                agent_id="The-Ruler",
                known_elements=_known_elements(),
                require_fit=True,
            )
        self.assertIn("mutual exclusion", str(ctx.exception).lower())

    def test_parse_native_units_rejects_unknown_center(self) -> None:
        data = json.loads(_native_search_units_json())
        data["search_units"][0]["center_element"] = "who-99"
        with self.assertRaises(ValueError) as ctx:
            parse_search_units_response(
                json.dumps(data),
                agent_id="The-Ruler",
                known_elements=_known_elements(),
                require_fit=True,
            )
        self.assertIn("unknown center_element", str(ctx.exception).lower())

    def test_parse_native_units_requires_fit(self) -> None:
        data = json.loads(_native_search_units_json())
        del data["search_units"][0]["fit"]
        with self.assertRaises(ValueError) as ctx:
            parse_search_units_response(
                json.dumps(data),
                agent_id="The-Ruler",
                known_elements=_known_elements(),
                require_fit=True,
            )
        self.assertIn("fit is required", str(ctx.exception).lower())

    def test_parse_native_units_supporting_cap(self) -> None:
        data = json.loads(_native_search_units_json())
        data["search_units"][0]["supporting_elements"] = [
            "who-0",
            "how-0",
            "result-0",
            "how-1",
            "why-1",
        ]
        with self.assertRaises(ValueError) as ctx:
            parse_search_units_response(
                json.dumps(data),
                agent_id="The-Ruler",
                known_elements=_known_elements(),
                require_fit=True,
            )
        self.assertIn("supporting_elements", str(ctx.exception).lower())


class PersonaSalienceTests(unittest.TestCase):
    _VALID_SALIENCE = [
        "result-0",
        "who-0",
        "how-0",
        "why-0",
        "how-1",
    ]

    def test_validate_salience_accepts_subset_permutation(self) -> None:
        known = _known_elements()
        out = validate_salience(self._VALID_SALIENCE, known)
        self.assertEqual(out, self._VALID_SALIENCE)

    def test_validate_salience_rejects_unknown_id(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            validate_salience(["who-99", "why-0", "how-0", "how-1", "result-0"], _known_elements())
        self.assertIn("unknown element_id", str(ctx.exception).lower())

    def test_validate_salience_rejects_free_text(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            validate_salience(
                ["result-0", "who is harmed", "how-0", "why-0", "how-1"],
                _known_elements(),
            )
        self.assertIn("illegal element_id", str(ctx.exception).lower())

    def test_validate_salience_rejects_duplicate(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            validate_salience(
                ["result-0", "result-0", "how-0", "why-0", "how-1"],
                _known_elements(),
            )
        self.assertIn("duplicate", str(ctx.exception).lower())

    def test_parse_alt_pool_with_salience(self) -> None:
        overlay = parse_alt_pool_response(
            _alt_pool_json_with_salience(self._VALID_SALIENCE),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        self.assertEqual(overlay.salience, self._VALID_SALIENCE)
        payload = build_alt_pool_overlay(overlay)
        self.assertEqual(payload["salience"], self._VALID_SALIENCE)


class PersonaScaffoldTests(unittest.TestCase):
    def test_annotate_element_ids(self) -> None:
        dec = _fixture_dec_inner()
        ann = annotate_element_ids(dec)
        self.assertEqual(ann["who"][0]["id"], "who-0")
        self.assertEqual(ann["where"][0]["id"], "where-0")
        self.assertEqual(ann["why"][0]["id"], "why-0")
        self.assertEqual(ann["how"][0]["id"], "how-0")

    def test_parse_alt_pool_valid(self) -> None:
        overlay = parse_alt_pool_response(
            _alt_pool_json(),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        self.assertEqual(overlay.persona_id, "The-Ruler")
        self.assertEqual(len(overlay.elements), 3)
        self.assertEqual(overlay.elements[0].alternatives[0].valence, "positive")

    def test_parse_alt_pool_unknown_element_errors(self) -> None:
        data = json.loads(_alt_pool_json())
        data["elements"][0]["element_id"] = "who-99"
        with self.assertRaises(ValueError) as ctx:
            parse_alt_pool_response(
                json.dumps(data),
                persona_id="The-Ruler",
                known_elements=_known_elements(),
            )
        self.assertIn("unknown element_id", str(ctx.exception).lower())

    def test_parse_alt_pool_provenance_layers(self) -> None:
        overlay = parse_alt_pool_response(
            _alt_pool_json(),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        who_alts = overlay.elements[0].alternatives
        self.assertEqual(who_alts[0].provenance, "lens")
        self.assertEqual(who_alts[1].provenance, "hypernym")
        why_hyper = next(
            a for a in overlay.elements[2].alternatives if a.term == "power plant outage"
        )
        self.assertEqual(why_hyper.provenance, "hypernym")

    def test_parse_alt_pool_invalid_provenance_errors(self) -> None:
        data = json.loads(_alt_pool_json())
        data["elements"][0]["alternatives"][0]["provenance"] = "myth"
        with self.assertRaises(ValueError) as ctx:
            parse_alt_pool_response(
                json.dumps(data),
                persona_id="The-Ruler",
                known_elements=_known_elements(),
            )
        self.assertIn("provenance", str(ctx.exception).lower())

    def test_overlay_forbids_decon_fork(self) -> None:
        overlay = parse_alt_pool_response(
            _alt_pool_json(),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        payload = build_alt_pool_overlay(overlay)
        self.assertNotIn("who", payload)
        self.assertNotIn("anchor", payload)
        self.assertEqual(payload["alt_pool"]["elements"][0]["element_id"], "who-0")
        with self.assertRaises(ValueError) as ctx:
            overlay_forbids_decon_fork({"persona_id": "X", "who": []})
        self.assertIn("fork", str(ctx.exception).lower())

    def test_render_persona_prompt_alt_pool_only(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json(),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        prompt = render_persona_prompt(
            "Pool:\n{{alt_pool_json}}\nDecon ids only in fragments section:\n{{deconstruction_json}}",
            deconstruction=dec,
            alt_pool=overlay,
        )
        self.assertNotIn("{{alt_pool_json}}", prompt)
        self.assertIn('"element_id": "who-0"', prompt)
        self.assertIn('"id": "why-0"', prompt)

    def test_screenwriter_prompt_includes_overlay_and_salience(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json_with_salience(["who-0", "why-0", "how-0", "result-0"]),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        prompt = build_screenwriter_user_prompt("The-Ruler", dec, overlay)
        self.assertIn('"element_id": "who-0"', prompt)
        self.assertNotIn("{{alt_pool_json}}", prompt)
        self.assertIn("Salience", prompt)
        self.assertIn("who-0", prompt)

    def test_screenwriter_prompt_requires_salience(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json(),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        with self.assertRaises(ValueError) as ctx:
            build_screenwriter_user_prompt("The-Ruler", dec, overlay)
        self.assertIn("salience", str(ctx.exception).lower())

    def test_load_persona_card_ruler(self) -> None:
        card = load_persona_card("The-Ruler")
        self.assertIsNotNone(card)
        assert card is not None
        self.assertIn("秩序", card)

    def test_list_persona_ids_twelve(self) -> None:
        ids = list_persona_ids()
        self.assertEqual(len(ids), 12)
        self.assertIn("The-Ruler", ids)
        self.assertIn("The-Sage", ids)

    def test_split_obs_holdout(self) -> None:
        from scripts.eval_batch_manifest import load_manifest

        run_ids = load_manifest()
        obs, holdout = split_obs_holdout(run_ids)
        self.assertEqual(len(obs), 4)
        self.assertEqual(len(holdout), 6)

    def test_load_a1_from_phase36_04(self) -> None:
        agent = load_a1_agent_from_phase36("04-celebrity-scandal")
        self.assertEqual(agent["agent_id"], "A1")
        self.assertEqual(agent["role"], "baseline")
        self.assertGreaterEqual(len(agent["pseudos"]), 1)

    def test_write_a1_parallel_baseline_04(self) -> None:
        import tempfile

        from scripts.run_persona_batch import write_a1_parallel_baseline

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            meta = write_a1_parallel_baseline("04-celebrity-scandal", out)
            self.assertTrue((out / "retrieve-a1.json").is_file())
            self.assertTrue((out / "a1-baseline-meta.json").is_file())
            self.assertGreater(meta.get("a1_pseudo_count", 0), 0)
            self.assertIsInstance(meta.get("a1_hit_tmdb_ids"), list)

    def test_all_persona_cards_exist(self) -> None:
        for pid in list_persona_ids():
            card = load_persona_card(pid)
            self.assertIsNotNone(card, pid)
            assert card is not None
            self.assertIn(pid, card)

    def test_build_alt_pool_overlay_dataclass(self) -> None:
        overlay = AltPoolOverlay(
            persona_id="The-Ruler",
            elements=[
                AltElement(
                    element_id="who-0",
                    original_term="operator",
                    alternatives=[
                        AltTerm("steward", "positive", "lens"),
                        AltTerm("operator", "neutral", "hypernym"),
                        AltTerm("bureaucracy", "negative", "lens"),
                    ],
                )
            ],
        )
        payload = build_alt_pool_overlay(overlay)
        self.assertEqual(payload["persona_id"], "The-Ruler")
        self.assertEqual(len(payload["alt_pool"]["elements"]), 1)
        self.assertEqual(
            payload["alt_pool"]["elements"][0]["alternatives"][1]["provenance"],
            "hypernym",
        )


class PersonaPipelineTests(unittest.IsolatedAsyncioTestCase):
    async def test_pipeline_native_search_units_path(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json_with_salience(["who-0", "why-0", "how-0", "result-0"]),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        good = _good_search_unit_segments()

        with patch(
            "scripts.rewrite.run_alt_creator",
            new_callable=AsyncMock,
            return_value=(overlay, None),
        ):
            with patch(
                "scripts.rewrite.run_screenwriter",
                new_callable=AsyncMock,
                return_value=(good, None),
            ):
                result = await run_persona_pipeline(
                    "The-Ruler",
                    dec,
                    expansion=_expansion_fixture(),
                    client=MagicMock(),
                    model="test-model",
                )

        self.assertIsNone(result.error)
        self.assertEqual(len(result.pseudos), 2)
        units = result.workflow["search_units"]["persona_semantic_units"]
        self.assertEqual(len(units), 2)
        self.assertEqual({u["center_element"] for u in units}, {"why-0", "who-0"})

    async def test_repair_retry_on_parse_error_succeeds_second_turn(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json_with_salience(["who-0", "why-0", "how-0", "result-0"]),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        good = _good_search_unit_segments()
        calls: list[str | None] = []

        async def mock_screenwriter(*_args, repair_context=None, **_kwargs):
            calls.append(repair_context)
            if len(calls) == 1:
                return None, "screenwriter parse_error: unknown center_element 'who-99'"
            return good, None

        with patch(
            "scripts.rewrite.run_alt_creator",
            new_callable=AsyncMock,
            return_value=(overlay, None),
        ):
            with patch(
                "scripts.rewrite.run_screenwriter",
                side_effect=mock_screenwriter,
            ):
                result = await run_persona_pipeline(
                    "The-Ruler",
                    dec,
                    expansion=_expansion_fixture(),
                    client=MagicMock(),
                    model="test-model",
                )

        self.assertIsNone(result.error)
        self.assertEqual(len(result.pseudos), 2)
        self.assertEqual(len(calls), 2)
        self.assertIsNone(calls[0])
        self.assertIn("parse_error", calls[1] or "")
        self.assertEqual(len(result.repair_retries), 2)

    async def test_repair_retry_still_fails_cleanly(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json_with_salience(["who-0", "why-0", "how-0", "result-0"]),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )

        async def mock_screenwriter(*_args, **_kwargs):
            return None, "screenwriter parse_error: invalid JSON"

        with patch(
            "scripts.rewrite.run_alt_creator",
            new_callable=AsyncMock,
            return_value=(overlay, None),
        ):
            with patch(
                "scripts.rewrite.run_screenwriter",
                side_effect=mock_screenwriter,
            ):
                result = await run_persona_pipeline(
                    "The-Ruler",
                    dec,
                    expansion=_expansion_fixture(),
                    client=MagicMock(),
                    model="test-model",
                )

        self.assertIsNotNone(result.error)
        self.assertEqual(result.pseudos, [])
        self.assertEqual(len(result.repair_retries), 2)
        self.assertIn("parse_error", result.error or "")


if __name__ == "__main__":
    unittest.main()