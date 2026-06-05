# Objective Expansion Contract (P-Expand · shared hypernym ladder)

> **Role:** One **shared** pass after A0 verbatim extract. Input = `reality-deconstructed.json`. Output = `reality-expanded.json` with **hypernym ladders only** — persona-independent objective floor for the neutral channel and toned anchors.

## Input

- Injected `{{deconstruction_json}}`: verbatim A0 output (`anchor`, `when`, `where`, `who`, `why`, `how`, `result`) with stable element ids:
  - `who-{i}`, `where-{i}`, `why-{i}`, `how-{i}`, `result-{i}`

{{deconstruction_json}}

## Output format

Return **only** valid JSON (no markdown fences, no preamble):

```json
{
  "elements": [
    {
      "element_id": "where-0",
      "surface": "Dharavi, Mumbai",
      "hypernyms": ["Mumbai", "Maharashtra", "India", "South Asia", "slum", "urban neighborhood"]
    },
    {
      "element_id": "who-0",
      "surface": "residents across central-northern India",
      "hypernyms": ["civilians", "affected population"]
    }
  ]
}
```

## Rules

1. **Hypernym only:** For each covered element, list broader terms from **more specific → more abstract** (English). Do not repeat the surface verbatim as a hypernym.
2. **Objectivity touchstone (mandatory):** Every hypernym must pass — *"Would A2 (sociologist) and A4 (mythologist) disagree on this label?"* If **yes** → it is **lens**, not objective → **omit**.
   - **Keep:** taxonomic / geographic generalizations (`slum`, `India`, `extreme weather`, `power grid`).
   - **Reject:** dramatic or valence-laden framing (`destiny's cage`, `crushing the individual`, `fateful prison`, `systemic oppression` when not verbatim in source).
3. **Fact-entailed:** Hypernyms must follow from A0 facts. Do not add events, actors, charges, or unstated causality.
4. **Shared, not per-persona:** One expansion for all personas. Persona differences belong in P-Lens.
5. **Coverage:** Prefer `who` and `where`; include `why` / `how` / `result` when a clean objective generalization exists. Skip when no defensible hypernym passes the touchstone.
6. **No inert fields:** Do not output `geocode`, `coordinates`, `scale`, `scene_archetype`, `tags`, `valence`, `alternatives`, or `lens` terms.

## Touchstone examples

| Surface (verbatim) | Keep (objective hypernym) | Reject (lens) |
| --- | --- | --- |
| Dharavi slum, Mumbai | `slum`, `Mumbai`, `India` | `destiny's cage`, `fateful trap` |
| central-northern India heatwave | `India`, `extreme weather`, `climate hazard` | `crushing the powerless`, `apocalyptic reckoning` |
| national power grid | `power grid`, `critical infrastructure` | `fragile lifeline of a dying regime` |
