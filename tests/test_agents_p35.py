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

_LONG_TEXT = (
    "During a prolonged heat wave, several fossil-fuel generating units shut down "
    "as demand reaches a record peak. A regional grid operator warns that rolling "
    "outages will continue. For a second consecutive night, utilities rotate "
    "electricity cuts across major cities to keep the wider network from collapsing."
)


def _fixture_fragment_ids() -> set[str]:
    dec = load_deconstruction_from_file(FIXTURE)
    return _known_fragment_ids(annotate_fragment_ids(dec))


def _pseudo_row(pseudo_id: str, fragments: list[str]) -> dict:
    return {
        "id": pseudo_id,
        "text": _LONG_TEXT,
        "source": {"fragments": fragments},
    }


def _parse_rows(rows: list[dict]) -> list:
    return parse_pseudos_response(
        json.dumps({"pseudos": rows}),
        agent_id="A1",
        known_fragments=_fixture_fragment_ids(),
    )


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


def test_parse_pseudos_three_segments() -> None:
    rows = [
        _pseudo_row("p1", ["why-0", "how-0", "result-0"]),
        _pseudo_row("p2", ["result-1"]),
        _pseudo_row("p3", ["how-0", "how-1"]),
    ]
    segs = _parse_rows(rows)
    assert len(segs) == 3
    assert [s.id for s in segs] == ["p1", "p2", "p3"]


def test_parse_pseudos_one_segment() -> None:
    segs = _parse_rows([_pseudo_row("p1", ["why-0", "how-0", "result-0"])])
    assert len(segs) == 1
    assert segs[0].id == "p1"


def test_parse_pseudos_two_segments() -> None:
    rows = [
        _pseudo_row("p1", ["why-0", "result-0"]),
        _pseudo_row("p2", ["how-0", "how-1"]),
    ]
    segs = _parse_rows(rows)
    assert len(segs) == 2
    assert [s.id for s in segs] == ["p1", "p2"]


def test_parse_pseudos_zero_segments_errors() -> None:
    try:
        _parse_rows([])
    except ValueError as exc:
        assert "1–3" in str(exc) or "1-3" in str(exc)
    else:
        raise AssertionError("expected ValueError for 0 pseudos")


def test_parse_pseudos_duplicate_id_errors() -> None:
    rows = [
        _pseudo_row("p1", ["why-0"]),
        _pseudo_row("p1", ["result-0"]),
    ]
    try:
        _parse_rows(rows)
    except ValueError as exc:
        assert "duplicate" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError for duplicate id")


def test_parse_pseudos_unknown_fragment_errors() -> None:
    try:
        _parse_rows([_pseudo_row("p1", ["why-0", "bogus-99"])])
    except ValueError as exc:
        assert "unknown fragment" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError for unknown fragment")


def test_parse_pseudos_too_many_segments_errors() -> None:
    rows = [_pseudo_row(f"p{i}", ["result-0"]) for i in range(1, 5)]
    try:
        _parse_rows(rows)
    except ValueError as exc:
        assert "1–3" in str(exc) or "1-3" in str(exc)
    else:
        raise AssertionError("expected ValueError for >3 pseudos")


def test_parse_pseudos_invalid_id_errors() -> None:
    try:
        _parse_rows([_pseudo_row("p4", ["why-0"])])
    except ValueError as exc:
        assert "invalid pseudo id" in str(exc).lower()
    else:
        raise AssertionError("expected ValueError for invalid pseudo id")


def test_render_prompt() -> None:
    dec = load_deconstruction_from_file(FIXTURE)
    persona = load_personas()[0]
    prompt = render_prompt(persona.template, deconstruction=dec)
    assert "{{deconstruction_json}}" not in prompt
    assert '"id": "why-0"' in prompt or '"why-0"' in prompt


if __name__ == "__main__":
    test_fragment_ids()
    test_parse_pseudos_three_segments()
    test_parse_pseudos_one_segment()
    test_parse_pseudos_two_segments()
    test_parse_pseudos_zero_segments_errors()
    test_parse_pseudos_duplicate_id_errors()
    test_parse_pseudos_unknown_fragment_errors()
    test_parse_pseudos_too_many_segments_errors()
    test_parse_pseudos_invalid_id_errors()
    test_render_prompt()
    print("test_agents_p35 OK")
