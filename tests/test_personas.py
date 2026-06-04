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
    AltElement,
    AltPoolOverlay,
    AltTerm,
    annotate_element_ids,
    build_alt_pool_overlay,
    build_screenwriter_user_prompt,
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


def _alt_pool_json() -> str:
    return json.dumps(
        {
            "persona_id": "The-Ruler",
            "elements": [
                {
                    "element_id": "who-0",
                    "original_term": "菲律宾电网运营商",
                    "alternatives": [
                        {"term": "grid steward", "valence": "positive"},
                        {"term": "grid operator", "valence": "neutral"},
                        {"term": "failing bureaucracy", "valence": "negative"},
                    ],
                },
                {
                    "element_id": "why-0",
                    "original_term": "Kepco SPC Power Unit 2 跳闸脱网，叠加其他机组长期停运",
                    "alternatives": [
                        {"term": "restored balance after a trip", "valence": "positive"},
                        {"term": "unit trip plus outages", "valence": "neutral"},
                        {"term": "cascade of plant failures", "valence": "negative"},
                    ],
                },
            ],
        }
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
        self.assertEqual(len(overlay.elements), 2)
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

    def test_parse_alt_pool_missing_valence_errors(self) -> None:
        data = json.loads(_alt_pool_json())
        data["elements"][0]["alternatives"] = [
            {"term": "only neutral", "valence": "neutral"},
        ]
        with self.assertRaises(ValueError) as ctx:
            parse_alt_pool_response(
                json.dumps(data),
                persona_id="The-Ruler",
                known_elements=_known_elements(),
            )
        self.assertIn("valence", str(ctx.exception).lower())

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
                        AltTerm("steward", "positive"),
                        AltTerm("operator", "neutral"),
                        AltTerm("bureaucracy", "negative"),
                    ],
                )
            ],
        )
        payload = build_alt_pool_overlay(overlay)
        self.assertEqual(payload["persona_id"], "The-Ruler")
        self.assertEqual(len(payload["alt_pool"]["elements"]), 1)


if __name__ == "__main__":
    unittest.main()
