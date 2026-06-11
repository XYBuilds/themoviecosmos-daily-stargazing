"""Offline checks for Phase 3.7 persona pipeline (no LLM)."""

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
    apply_adr8_pseudo_budget,
    assemble_adr8_channel_pseudos,
    assemble_persona_channel_pseudos,
    build_adr8_screenwriter_user_prompt,
    build_alt_pool_overlay,
    build_objective_floor_neutral_pseudo,
    build_screenwriter_user_prompt,
    collect_hypernym_anchor_terms,
    collect_lens_terms,
    composition_mode_active,
    derive_expected_channel,
    fragment_ids_from_salience,
    inject_adr8_composition_mode,
    known_element_ids,
    list_persona_ids,
    load_persona_card,
    overlay_forbids_decon_fork,
    parse_adr8_pseudos_response,
    parse_alt_pool_response,
    rank_adr8_pseudos_by_salience,
    render_persona_prompt,
    resolve_neutral_fragment_ids,
    run_persona_pipeline,
    salience_rank_of_center,
    validate_center_mutual_exclusion,
    validate_neutral_pseudo_batch_diversity,
    validate_salience,
    who_instantiates_vantage_seat,
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


def _alt_pool_json_with_salience(salience: list[str] | None = None) -> str:
    data = json.loads(_alt_pool_json())
    if salience is not None:
        data["salience"] = salience
    return json.dumps(data)


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

    def test_fragment_ids_from_salience_top_k(self) -> None:
        frags = fragment_ids_from_salience(self._VALID_SALIENCE, top_k=4)
        self.assertEqual(frags, self._VALID_SALIENCE[:4])

    def test_salience_drives_fragment_ids_not_default(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json_with_salience(["result-0", "who-0", "how-0", "why-0"]),
            persona_id="The-Caregiver",
            known_elements=_known_elements(),
        )
        frags = resolve_neutral_fragment_ids(dec, overlay, top_k=4)
        self.assertEqual(frags, ["result-0", "who-0", "how-0", "why-0"])
        default = resolve_neutral_fragment_ids(
            dec,
            AltPoolOverlay(persona_id="The-Caregiver", elements=overlay.elements),
        )
        self.assertNotEqual(frags, default)

    def test_who_where_optional_via_salience(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json(),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        overlay.salience = ["why-0", "how-0", "how-1", "result-0"]
        without_who = build_objective_floor_neutral_pseudo(
            "The-Ruler",
            dec,
            overlay,
            _expansion_fixture(),
            fragment_ids=overlay.salience,
        )
        self.assertNotIn("Philippines grid operator", without_who.text)
        self.assertNotIn("Visayas, Philippines", without_who.text)

        with_who = build_objective_floor_neutral_pseudo(
            "The-Ruler",
            dec,
            overlay,
            _expansion_fixture(),
            fragment_ids=["who-0", "why-0", "how-0", "result-0"],
        )
        self.assertIn("Philippines grid operator", with_who.text)

    def test_diversity_guard_passes_distinct_fragments(self) -> None:
        dec = _fixture_dec_inner()
        expansion = _full_expansion_fixture()
        saliences = [
            ["result-0", "who-0", "how-0", "why-0"],
            ["how-1", "how-2", "result-1", "why-1"],
            ["why-0", "how-0", "result-0", "where-0"],
        ]
        neutrals = []
        for idx, sal in enumerate(saliences):
            overlay = AltPoolOverlay(
                persona_id=f"P{idx}",
                elements=parse_alt_pool_response(
                    _alt_pool_json(),
                    persona_id=f"P{idx}",
                    known_elements=_known_elements(),
                ).elements,
                salience=sal,
            )
            neutrals.append(
                build_objective_floor_neutral_pseudo(
                    f"P{idx}",
                    dec,
                    overlay,
                    expansion,
                    fragment_ids=sal,
                )
            )
        validate_neutral_pseudo_batch_diversity(neutrals)

    def test_diversity_guard_fails_near_duplicate(self) -> None:
        dec = _fixture_dec_inner()
        expansion = _full_expansion_fixture()
        same_sal = ["why-0", "how-0", "how-1", "result-0"]
        neutrals = []
        for pid in ("The-Creator", "The-Caregiver"):
            overlay = AltPoolOverlay(
                persona_id=pid,
                elements=parse_alt_pool_response(
                    _alt_pool_json(),
                    persona_id=pid,
                    known_elements=_known_elements(),
                ).elements,
                salience=same_sal,
            )
            neutrals.append(
                build_objective_floor_neutral_pseudo(
                    pid,
                    dec,
                    overlay,
                    expansion,
                    fragment_ids=same_sal,
                )
            )
        with self.assertRaises(ValueError) as ctx:
            validate_neutral_pseudo_batch_diversity(neutrals)
        self.assertIn("diversity guard", str(ctx.exception).lower())

    def _collide_neutral_pair(self) -> list:
        dec = _fixture_dec_inner()
        expansion = _full_expansion_fixture()
        same_sal = ["why-0", "how-0", "how-1", "result-0"]
        neutrals = []
        for pid in ("The-Creator", "The-Caregiver"):
            overlay = AltPoolOverlay(
                persona_id=pid,
                elements=parse_alt_pool_response(
                    _alt_pool_json(),
                    persona_id=pid,
                    known_elements=_known_elements(),
                ).elements,
                salience=same_sal,
            )
            neutrals.append(
                build_objective_floor_neutral_pseudo(
                    pid, dec, overlay, expansion, fragment_ids=same_sal
                )
            )
        return neutrals

    def test_diversity_guard_tolerates_neutral_only_collision(self) -> None:
        # Neutral legs collide but toned legs diverge → warning, not failure.
        neutrals = self._collide_neutral_pair()
        warnings = validate_neutral_pseudo_batch_diversity(
            neutrals,
            toned_text_by_agent={
                "The-Creator": (
                    "A jubilant restoration of balance after a hard-won recovery."
                ),
                "The-Caregiver": (
                    "Families left exposed and vulnerable as the safety net frays."
                ),
            },
        )
        self.assertEqual(len(warnings), 1)
        self.assertIn("neutral-only", warnings[0].lower())

    def test_diversity_guard_fails_when_neutral_and_toned_collide(self) -> None:
        # Both neutral and toned legs collide → hard failure.
        neutrals = self._collide_neutral_pair()
        identical = "The same toned narrative shared verbatim across both personas."
        with self.assertRaises(ValueError) as ctx:
            validate_neutral_pseudo_batch_diversity(
                neutrals,
                toned_text_by_agent={
                    "The-Creator": identical,
                    "The-Caregiver": identical,
                },
            )
        self.assertIn("toned also near-duplicate", str(ctx.exception).lower())

    def test_neutral_pseudo_dedups_repeated_surface_sentences(self) -> None:
        # A fact framed as both cause (why-0) and mechanism (how-0) shares one
        # surface string; the neutral body must render that sentence only once.
        decon = {
            "who": [{"text": "Philippines grid operator"}],
            "where": [{"text": "Visayas, Philippines"}],
            "why": [{"text": "Unit 2 tripped offline"}],
            "how": [
                {"text": "Unit 2 tripped offline"},
                {"text": "the Visayas grid was placed under red alert"},
            ],
            "result": [{"text": "more than 950 megawatts unavailable"}],
        }
        expansion = {
            "elements": [
                {
                    "element_id": "result-0",
                    "surface": "more than 950 megawatts unavailable",
                    "hypernyms": ["power shortage"],
                },
                {
                    "element_id": "how-0",
                    "surface": "Unit 2 tripped offline",
                    "hypernyms": ["equipment failure"],
                },
                {
                    "element_id": "how-1",
                    "surface": "the Visayas grid was placed under red alert",
                    "hypernyms": ["alert declaration"],
                },
                {
                    "element_id": "why-0",
                    "surface": "Unit 2 tripped offline",
                    "hypernyms": ["equipment failure"],
                },
            ]
        }
        frags = ["result-0", "how-0", "how-1", "why-0"]
        overlay = AltPoolOverlay(persona_id="The-Sage", elements=[], salience=frags)
        pseudo = build_objective_floor_neutral_pseudo(
            "The-Sage",
            decon,
            overlay,
            expansion,
            fragment_ids=frags,
        )
        self.assertEqual(pseudo.text.lower().count("unit 2 tripped offline"), 1)
        self.assertIn("red alert", pseudo.text.lower())


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

    def test_collect_hypernym_anchor_terms_excludes_sentence_level(self) -> None:
        expansion = {
            "elements": [
                {
                    "element_id": "why-0",
                    "surface": "unit tripped",
                    "hypernyms": [
                        "power plant outage",
                        "a high-level warning was declared for the region.",
                    ],
                }
            ]
        }
        overlay = AltPoolOverlay(
            persona_id="The-Hero",
            elements=[
                AltElement(
                    element_id="why-0",
                    original_term="unit tripped",
                    alternatives=[
                        AltTerm(
                            "a high-level warning was declared for the region.",
                            "neutral",
                            "hypernym",
                        ),
                        AltTerm("power plant outage", "neutral", "hypernym"),
                    ],
                )
            ],
        )
        terms = collect_hypernym_anchor_terms(overlay, expansion)
        self.assertIn("power plant outage", terms)
        self.assertNotIn(
            "a high-level warning was declared for the region.",
            terms,
        )


class PersonaAdr8CompositionTests(unittest.TestCase):
    _SALIENCE = ["who-0", "why-0", "how-0", "result-0", "how-1"]

    def _adr8_raw(
        self,
        *,
        p1_center: str = "who-0",
        p1_channel: str = "toned",
        p2_center: str = "why-0",
    ) -> str:
        p1: dict = {
            "id": "p1",
            "text": (
                "Grid operators face a large-scale power deficit after seasonal heat "
                "drove demand into a thin margin, forcing emergency measures across "
                "the power grid and critical infrastructure."
            ),
            "fit": 0.8,
            "center": p1_center,
            "channel": p1_channel,
            "source": {"fragments": ["why-0", "how-0", "result-0"]},
        }
        if p1_channel == "focalized":
            p1["focal"] = p1_center
        return json.dumps(
            {
                "pseudos": [
                    p1,
                    {
                        "id": "p2",
                        "text": (
                            "A prolonged heat wave strains the Philippines grid operator "
                            "network as plant outages leave more than nine hundred "
                            "megawatts unavailable across the power grid."
                        ),
                        "fit": 0.75,
                        "center": p2_center,
                        "channel": "toned",
                        "source": {"fragments": ["why-0", "how-0"]},
                    },
                ]
            }
        )

    def test_composition_mode_active_when_salience_present(self) -> None:
        overlay = parse_alt_pool_response(
            _alt_pool_json_with_salience(self._SALIENCE),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        self.assertTrue(composition_mode_active(overlay))
        bare = AltPoolOverlay(persona_id="The-Ruler", elements=overlay.elements)
        self.assertFalse(composition_mode_active(bare))

    def test_inject_adr8_composition_mode_marker(self) -> None:
        prompt = inject_adr8_composition_mode("base", salience=["who-0", "why-0"])
        self.assertIn("Composition mode: ADR-0008", prompt)
        self.assertIn("who-0", prompt)

    def test_build_adr8_screenwriter_prompt_includes_marker(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json_with_salience(self._SALIENCE),
            persona_id="The-Everyman",
            known_elements=_known_elements(),
        )
        prompt = build_adr8_screenwriter_user_prompt("The-Everyman", dec, overlay)
        self.assertIn("Composition mode: ADR-0008", prompt)
        self.assertIn("Element-centered composition", prompt)

    def test_parse_adr8_pseudos_provenance_tags(self) -> None:
        pseudos = parse_adr8_pseudos_response(
            self._adr8_raw(),
            agent_id="The-Everyman",
            known_fragments=_known_fragments(),
            known_elements=_known_elements(),
        )
        self.assertEqual(len(pseudos), 2)
        for pseudo in pseudos:
            self.assertIn("center", pseudo.source)
            self.assertIn("channel", pseudo.source)
            self.assertIn(pseudo.source["channel"], ("toned", "focalized"))

    def test_parse_adr8_rejects_duplicate_center(self) -> None:
        raw = json.dumps(
            {
                "pseudos": [
                    {
                        "id": "p1",
                        "text": _LONG_TEXT,
                        "fit": 0.8,
                        "center": "why-0",
                        "channel": "toned",
                        "source": {"fragments": ["why-0", "how-0", "result-0"]},
                    },
                    {
                        "id": "p2",
                        "text": _LONG_TEXT + " Additional context on grid strain.",
                        "fit": 0.7,
                        "center": "why-0",
                        "channel": "toned",
                        "source": {"fragments": ["why-0", "how-1"]},
                    },
                ]
            }
        )
        with self.assertRaises(ValueError) as ctx:
            parse_adr8_pseudos_response(
                raw,
                agent_id="The-Everyman",
                known_fragments=_known_fragments(),
                known_elements=_known_elements(),
            )
        self.assertIn("mutual exclusion", str(ctx.exception).lower())

    def test_parse_adr8_dual_floor_requires_toned(self) -> None:
        raw = json.dumps(
            {
                "pseudos": [
                    {
                        "id": "p1",
                        "text": (
                            "From the control room, the Philippines grid operator "
                            "watches red-alert warnings climb as a power plant outage "
                            "spreads across the power grid."
                        ),
                        "fit": 0.8,
                        "center": "who-0",
                        "channel": "focalized",
                        "focal": "who-0",
                        "source": {"fragments": ["why-0", "how-0", "result-0"]},
                    }
                ]
            }
        )
        with self.assertRaises(ValueError) as ctx:
            parse_adr8_pseudos_response(
                raw,
                agent_id="The-Everyman",
                known_fragments=_known_fragments(),
                known_elements=_known_elements(),
            )
        self.assertIn("dual floor", str(ctx.exception).lower())

    def test_salience_rank_and_greedy_ordering(self) -> None:
        salience = self._SALIENCE
        self.assertEqual(salience_rank_of_center("who-0", salience), 0)
        self.assertEqual(salience_rank_of_center("how-1", salience), 4)
        self.assertEqual(salience_rank_of_center("where-0", salience), 5)

        pseudos = parse_adr8_pseudos_response(
            self._adr8_raw(p1_center="result-0", p2_center="who-0"),
            agent_id="The-Everyman",
            known_fragments=_known_fragments(),
            known_elements=_known_elements(),
        )
        ranked = rank_adr8_pseudos_by_salience(pseudos, salience)
        self.assertEqual(ranked[0].source["center"], "who-0")
        self.assertEqual(ranked[1].source["center"], "result-0")

    def test_apply_adr8_budget_preserves_dual_floor(self) -> None:
        legs = parse_adr8_pseudos_response(
            json.dumps(
                {
                    "pseudos": [
                        {
                            "id": "p1",
                            "text": (
                                "From the plant floor, operators watch emergency load "
                                "shedding ripple across the power grid during a major "
                                "power plant outage."
                            ),
                            "fit": 0.8,
                            "center": "who-0",
                            "channel": "focalized",
                            "focal": "who-0",
                            "source": {"fragments": ["why-0", "how-0", "result-0"]},
                        },
                        {
                            "id": "p2",
                            "text": _LONG_TEXT + " More on outages.",
                            "fit": 0.7,
                            "center": "how-1",
                            "channel": "focalized",
                            "focal": "who-0",
                            "source": {"fragments": ["how-1", "result-0"]},
                        },
                        {
                            "id": "p3",
                            "text": _LONG_TEXT + " Toned third-person leg.",
                            "fit": 0.65,
                            "center": "why-0",
                            "channel": "toned",
                            "source": {"fragments": ["why-0", "how-0"]},
                        },
                    ]
                }
            ),
            agent_id="The-Everyman",
            known_fragments=_known_fragments(),
            known_elements=_known_elements(),
        )
        from scripts.agents import PseudoSegment

        four_legs = legs + [
            PseudoSegment(
                "p4",
                _LONG_TEXT + " Another toned leg.",
                {
                    "center": "result-0",
                    "channel": "toned",
                    "fragments": ["result-0", "why-0"],
                },
                [],
                fit=0.6,
            )
        ]
        budgeted = apply_adr8_pseudo_budget(four_legs, self._SALIENCE, budget=3)
        self.assertEqual(len(budgeted), 3)
        self.assertTrue(any(p.source.get("channel") == "toned" for p in budgeted))

    def test_focalized_derivation_everyman_grid_operator(self) -> None:
        dec = _fixture_dec_inner()
        card = load_persona_card("The-Everyman")
        assert card is not None
        self.assertTrue(
            who_instantiates_vantage_seat(
                "Philippines grid operator",
                ["operators", "ordinary people", "fair-minded"],
            )
        )
        self.assertEqual(
            derive_expected_channel("who-0", dec, card),
            "focalized",
        )
        self.assertEqual(
            derive_expected_channel("why-0", dec, card),
            "toned",
        )

    def test_assemble_adr8_neutral_n1_unchanged_vs_legacy(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json_with_salience(self._SALIENCE),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        expansion = _full_expansion_fixture()
        frags = resolve_neutral_fragment_ids(dec, overlay)
        legacy_neutral = build_objective_floor_neutral_pseudo(
            "The-Ruler",
            dec,
            overlay,
            expansion,
            fragment_ids=frags,
        )
        legs = parse_adr8_pseudos_response(
            self._adr8_raw(),
            agent_id="The-Ruler",
            known_fragments=_known_fragments(),
            known_elements=_known_elements(),
        )
        assembled = assemble_adr8_channel_pseudos(
            "The-Ruler",
            dec,
            overlay,
            legs,
            expansion,
        )
        self.assertEqual(assembled[0].id, NEUTRAL_PSEUDO_ID)
        self.assertEqual(assembled[0].text, legacy_neutral.text)
        self.assertEqual(assembled[0].source.get("channel_role"), "neutral")
        self.assertGreaterEqual(len(assembled), 2)
        toned = [p for p in assembled if p.id != NEUTRAL_PSEUDO_ID]
        self.assertTrue(any(p.source.get("channel") == "toned" for p in toned))

    def test_assemble_adr8_provenance_complete(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json_with_salience(self._SALIENCE),
            persona_id="The-Everyman",
            known_elements=_known_elements(),
        )
        legs = parse_adr8_pseudos_response(
            self._adr8_raw(p1_center="who-0", p1_channel="focalized"),
            agent_id="The-Everyman",
            known_fragments=_known_fragments(),
            known_elements=_known_elements(),
        )
        assembled = assemble_adr8_channel_pseudos(
            "The-Everyman",
            dec,
            overlay,
            legs,
            _full_expansion_fixture(),
        )
        focal = next(p for p in assembled if p.source.get("channel") == "focalized")
        self.assertEqual(focal.source.get("composition_mode"), "ADR-0008")
        self.assertEqual(focal.source.get("center"), "who-0")
        self.assertEqual(focal.source.get("focal"), "who-0")
        self.assertEqual(focal.source.get("focal_role_id"), "who-0")
        self.assertIsNotNone(focal.source.get("salience_rank"))

    def test_validate_center_mutual_exclusion(self) -> None:
        legs = parse_adr8_pseudos_response(
            self._adr8_raw(),
            agent_id="The-Everyman",
            known_fragments=_known_fragments(),
            known_elements=_known_elements(),
        )
        validate_center_mutual_exclusion(legs)


class PersonaRepairTests(unittest.IsolatedAsyncioTestCase):
    async def test_repair_retry_on_parse_error_succeeds_second_turn(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json(),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        good_pseudos = _toned_pseudo_with_hypernym()
        calls: list[str | None] = []

        async def mock_screenwriter(*_args, repair_context=None, **_kwargs):
            calls.append(repair_context)
            if len(calls) == 1:
                return None, "screenwriter parse_error: unknown fragment ids ['who-0']"
            return good_pseudos, None

        with patch(
            "scripts.personas.run_alt_creator",
            new_callable=AsyncMock,
            return_value=(overlay, None),
        ):
            with patch(
                "scripts.personas.run_screenwriter",
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

    async def test_repair_retry_on_assembly_failure_succeeds_second_turn(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json(),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )
        bad_text = (
            "Seasonal heat drove demand to a record peak while multiple generating "
            "units remained unavailable, forcing emergency load shedding across the region."
        )
        bad_pseudos = parse_pseudos_response(
            json.dumps(
                {
                    "pseudos": [
                        {
                            "id": "p1",
                            "text": bad_text,
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
        good_pseudos = _toned_pseudo_with_hypernym()
        calls: list[str | None] = []

        async def mock_screenwriter(*_args, repair_context=None, **_kwargs):
            calls.append(repair_context)
            if len(calls) == 1:
                return bad_pseudos, None
            return good_pseudos, None

        with patch(
            "scripts.personas.run_alt_creator",
            new_callable=AsyncMock,
            return_value=(overlay, None),
        ):
            with patch(
                "scripts.personas.run_screenwriter",
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
        self.assertIn("channel_assembly", calls[1] or "")
        self.assertTrue(any(r["stage"] == "channel_assembly" for r in result.repair_retries))

    async def test_repair_retry_still_fails_cleanly(self) -> None:
        dec = _fixture_dec_inner()
        overlay = parse_alt_pool_response(
            _alt_pool_json(),
            persona_id="The-Ruler",
            known_elements=_known_elements(),
        )

        async def mock_screenwriter(*_args, **_kwargs):
            return None, "screenwriter parse_error: invalid JSON"

        with patch(
            "scripts.personas.run_alt_creator",
            new_callable=AsyncMock,
            return_value=(overlay, None),
        ):
            with patch(
                "scripts.personas.run_screenwriter",
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
