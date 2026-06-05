"""Offline checks for Phase 3.7 persona pipeline (no LLM)."""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.agents import (
    annotate_fragment_ids,
    load_deconstruction_from_file,
    parse_pseudos_response,
    _known_fragment_ids,
)
from scripts.personas import (
    NEUTRAL_PSEUDO_ID,
    AltElement,
    AltPoolOverlay,
    AltTerm,
    annotate_element_ids,
    assemble_persona_channel_pseudos,
    build_alt_pool_overlay,
    build_objective_floor_neutral_pseudo,
    build_screenwriter_user_prompt,
    collect_hypernym_anchor_terms,
    collect_lens_terms,
    known_element_ids,
    list_persona_ids,
    load_persona_card,
    overlay_forbids_decon_fork,
    parse_alt_pool_response,
    render_persona_prompt,
)
from scripts.run_persona_batch import (
    load_a1_agent_from_phase36,
    split_obs_holdout,
)

FIXTURE = _REPO / "tests" / "fixtures" / "01-grid-outage-deconstructed.json"

_LONG_TEXT = (
    "During a prolonged heat wave, several fossil-fuel generating units shut down "
    "as demand reaches a record peak. A regional grid operator warns that rolling "
    "outages will continue. For a second consecutive night, utilities rotate "
    "electricity cuts across major cities to keep the wider network from collapsing."
)


def _fixture_dec_inner() -> dict:
    return load_deconstruction_from_file(FIXTURE)


def _known_elements() -> set[str]:
    return known_element_ids(_fixture_dec_inner())


def _known_fragments() -> set[str]:
    return _known_fragment_ids(annotate_fragment_ids(_fixture_dec_inner()))


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


def _toned_pseudo_with_hypernym() -> list:
    return parse_pseudos_response(
        json.dumps(
            {
                "pseudos": [
                    {
                        "id": "p1",
                        "text": (
                            "During a prolonged heat wave, a power plant outage on the "
                            "Philippines grid operator's network left the Visayas region "
                            "under red alert as critical infrastructure strained under "
                            "record demand and rolling cuts spread across major cities."
                        ),
                        "fit": 0.75,
                        "source": {"fragments": ["why-0", "how-0", "result-0"]},
                    }
                ]
            }
        ),
        agent_id="The-Ruler",
        known_fragments=_known_fragments(),
        require_fit=True,
    )


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

    def test_parse_alt_pool_persona_relative_partial_valence_ok(self) -> None:
        data = json.loads(_alt_pool_json())
        data["elements"][0]["alternatives"] = [
            {"term": "rumor spreader", "valence": "negative", "provenance": "lens"},
        ]
        overlay = parse_alt_pool_response(
            json.dumps(data),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        alts = overlay.elements[0].alternatives
        self.assertEqual(len(alts), 1)
        self.assertEqual(alts[0].valence, "negative")
        self.assertEqual(alts[0].provenance, "lens")

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
        self.assertEqual(prompt.count('"anchor"'), 1)

    def test_parse_pseudos_with_fit(self) -> None:
        rows = [
            {
                "id": "p1",
                "text": _LONG_TEXT,
                "fit": 0.75,
                "source": {"fragments": ["why-0", "how-0", "result-0"]},
            }
        ]
        segs = parse_pseudos_response(
            json.dumps({"pseudos": rows}),
            agent_id="The-Ruler",
            known_fragments=_known_fragments(),
            require_fit=True,
        )
        self.assertEqual(len(segs), 1)
        self.assertEqual(segs[0].fit, 0.75)

    def test_parse_pseudos_fit_out_of_range_errors(self) -> None:
        rows = [
            {
                "id": "p1",
                "text": _LONG_TEXT,
                "fit": 1.5,
                "source": {"fragments": ["why-0"]},
            }
        ]
        with self.assertRaises(ValueError) as ctx:
            parse_pseudos_response(
                json.dumps({"pseudos": rows}),
                agent_id="The-Ruler",
                known_fragments=_known_fragments(),
                require_fit=True,
            )
        self.assertIn("fit", str(ctx.exception).lower())

    def test_parse_pseudos_require_fit_missing_errors(self) -> None:
        rows = [
            {
                "id": "p1",
                "text": _LONG_TEXT,
                "source": {"fragments": ["why-0"]},
            }
        ]
        with self.assertRaises(ValueError) as ctx:
            parse_pseudos_response(
                json.dumps({"pseudos": rows}),
                agent_id="The-Ruler",
                known_fragments=_known_fragments(),
                require_fit=True,
            )
        self.assertIn("fit is required", str(ctx.exception).lower())

    def test_screenwriter_prompt_includes_overlay(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json(),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        prompt = build_screenwriter_user_prompt("The-Ruler", dec, overlay)
        self.assertTrue(
            "persona_screenwriter_contract" in prompt or "Screenwriter" in prompt
        )
        self.assertIn('"element_id": "who-0"', prompt)
        self.assertNotIn("{{alt_pool_json}}", prompt)

    def test_screenwriter_prompt_includes_expansion_hypernyms(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json(),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        expansion = _expansion_fixture()
        prompt = build_screenwriter_user_prompt(
            "The-Ruler", dec, overlay, expansion=expansion
        )
        self.assertNotIn("{{expansion_json}}", prompt)
        self.assertIn("power grid", prompt)
        self.assertIn("critical infrastructure", prompt)
        self.assertIn("supply shortfall", prompt)

    def test_parse_pseudos_rejects_element_ids_as_fragments(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            parse_pseudos_response(
                json.dumps(
                    {
                        "pseudos": [
                            {
                                "id": "p1",
                                "text": _LONG_TEXT,
                                "fit": 0.7,
                                "source": {"fragments": ["who-0", "where-0"]},
                            }
                        ]
                    }
                ),
                agent_id="The-Caregiver",
                known_fragments=_known_fragments(),
                require_fit=True,
            )
        self.assertIn("unknown fragment ids", str(ctx.exception).lower())
        self.assertIn("who-0", str(ctx.exception))
        self.assertIn("where-0", str(ctx.exception))

    def test_toned_with_hypernym_anchor_passes(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json(),
            persona_id="The-Hero",
            known_elements=_known_elements(),
        )
        toned = parse_pseudos_response(
            json.dumps(
                {
                    "pseudos": [
                        {
                            "id": "p1",
                            "text": (
                                "A power plant outage forced administrators to declare "
                                "a high-level warning as demand surged across the power grid."
                            ),
                            "fit": 0.8,
                            "source": {"fragments": ["why-0", "how-0"]},
                        }
                    ]
                }
            ),
            agent_id="The-Hero",
            known_fragments=_known_fragments(),
            require_fit=True,
        )
        pseudos = assemble_persona_channel_pseudos(
            "The-Hero",
            dec,
            overlay,
            toned,
            _expansion_fixture(),
        )
        self.assertEqual(len(pseudos), 2)
        self.assertTrue(any("power plant outage" in p.text.lower() for p in pseudos if p.id != NEUTRAL_PSEUDO_ID))

    def test_load_persona_card_ruler(self) -> None:
        card = load_persona_card("The-Ruler")
        self.assertIsNotNone(card)
        assert card is not None
        self.assertIn("秩序", card)
        self.assertIn("负向捍卫秩序", card)

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
        self.assertTrue(all(r.startswith("01-") or r.startswith("02-") for r in obs[:2]))

    def test_load_a1_from_phase36_04(self) -> None:
        agent = load_a1_agent_from_phase36("04-celebrity-scandal")
        self.assertEqual(agent["agent_id"], "A1")
        self.assertEqual(agent["role"], "baseline")
        self.assertGreaterEqual(len(agent["pseudos"]), 1)

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

    def test_neutral_pseudo_surface_hypernym_only(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json(),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        neutral = build_objective_floor_neutral_pseudo(
            "The-Ruler",
            dec,
            overlay,
            _expansion_fixture(),
        )
        self.assertEqual(neutral.id, NEUTRAL_PSEUDO_ID)
        self.assertEqual(neutral.source.get("channel_role"), "neutral")
        layers = neutral.source.get("provenance_layers") or []
        self.assertIn("surface", layers)
        self.assertIn("hypernym", layers)
        self.assertNotIn("lens", layers)
        lens_terms = collect_lens_terms(overlay)
        text_lower = neutral.text.lower()
        for term in lens_terms:
            self.assertNotIn(term, text_lower, msg=f"lens leak: {term}")

    def test_assemble_channels_one_neutral_plus_toned(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json(),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        toned = _toned_pseudo_with_hypernym()
        pseudos = assemble_persona_channel_pseudos(
            "The-Ruler",
            dec,
            overlay,
            toned,
            _expansion_fixture(),
        )
        self.assertEqual(len(pseudos), 2)
        self.assertEqual(pseudos[0].id, NEUTRAL_PSEUDO_ID)
        self.assertEqual(pseudos[0].source.get("channel_role"), "neutral")
        self.assertEqual(pseudos[1].source.get("channel_role"), "toned")
        hypernyms = collect_hypernym_anchor_terms(overlay, _expansion_fixture())
        self.assertTrue(any(h in pseudos[1].text.lower() for h in hypernyms))

    def test_toned_without_hypernym_anchor_errors(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json(),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        no_anchor_text = (
            "Seasonal heat drove demand to a record peak while multiple generating "
            "units remained unavailable, forcing emergency load shedding across the region."
        )
        toned = parse_pseudos_response(
            json.dumps(
                {
                    "pseudos": [
                        {
                            "id": "p1",
                            "text": no_anchor_text,
                            "fit": 0.5,
                            "source": {"fragments": ["why-0"]},
                        }
                    ]
                }
            ),
            agent_id="The-Ruler",
            known_fragments=_known_fragments(),
            require_fit=True,
        )
        with self.assertRaises(ValueError) as ctx:
            assemble_persona_channel_pseudos(
                "The-Ruler",
                dec,
                overlay,
                toned,
                _expansion_fixture(),
            )
        self.assertIn("hypernym anchor", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
