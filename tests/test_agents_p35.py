"""Offline checks for Phase 3.5.3 agents (no LLM)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from scripts.agents import (
    annotate_fragment_ids,
    load_deconstruction_from_file,
    load_personas,
    parse_pseudos_response,
    render_prompt,
    _known_fragment_ids,
)

FIXTURE = _REPO / "tests" / "fixtures" / "01-grid-outage-deconstructed.json"


def test_fragment_ids() -> None:
    dec = load_deconstruction_from_file(FIXTURE)
    ann = annotate_fragment_ids(dec)
    ids = _known_fragment_ids(ann)
    assert ids == {
        "why-0",
        "why-1",
        "how-0",
        "how-1",
        "how-2",
        "result-0",
        "result-1",
    }


def test_parse_pseudos() -> None:
    dec = load_deconstruction_from_file(FIXTURE)
    ids = _known_fragment_ids(annotate_fragment_ids(dec))
    long = (
        "During a prolonged heat wave, several fossil-fuel generating units shut down "
        "as demand reaches a record peak. A regional grid operator warns that rolling "
        "outages will continue. For a second consecutive night, utilities rotate "
        "electricity cuts across major cities to keep the wider network from collapsing."
    )
    sample = {
        "pseudos": [
            {"id": "p1", "text": long, "source": {"fragments": ["why-0", "how-0", "result-0"]}},
            {"id": "p2", "text": long, "source": {"fragments": ["result-1"]}},
            {"id": "p3", "text": long, "source": {"fragments": ["how-0", "how-1"]}},
        ]
    }
    segs = parse_pseudos_response(
        json.dumps(sample),
        agent_id="A1",
        known_fragments=ids,
    )
    assert len(segs) == 3
    assert [s.id for s in segs] == ["p1", "p2", "p3"]


def test_render_prompt() -> None:
    dec = load_deconstruction_from_file(FIXTURE)
    persona = load_personas()[0]
    prompt = render_prompt(persona.template, deconstruction=dec)
    assert "{{deconstruction_json}}" not in prompt
    assert '"id": "why-0"' in prompt or '"why-0"' in prompt


if __name__ == "__main__":
    test_fragment_ids()
    test_parse_pseudos()
    test_render_prompt()
    print("test_agents_p35 OK")
