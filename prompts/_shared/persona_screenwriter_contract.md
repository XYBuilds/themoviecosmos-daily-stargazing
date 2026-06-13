# Persona Screenwriter Contract (ADR-0009 fragment ladder / search unit)

> The persona drafting step emits **persona-semantic search units** directly. Each unit is a compact, fact-entailed English paragraph composed around one `center_element`, which downstream code converts into `search_units.persona_semantic_units`. There is no `pseudos[]` wrapper and no `toned` / `focalized` / `neutral` channel — those are retired (ADR-0008 superseded by ADR-0009).

## Shared base

Follow all rules in:

- `prompts/_shared/output_contract.md` (English, single paragraph, TMDB-overview voice)
- `prompts/_shared/deentification_rules.md`

> The `pseudos[]` / fragment-id contract in `multi_pseudo_output_contract.md` governs the A1/A2/A4/A7 news writer agents, **not** this persona-semantic step. This step emits `search_units[]` keyed on element ids.

## Inputs

- `{{deconstruction_json}}`: verbatim decon (element ids — for `center_element` + `supporting_elements` provenance).
- `{{alt_pool_json}}`: persona alt-pool overlay (`persona_id` + `elements[]` with `element_id`, `original_term`, `alternatives[]`). **Select terms from this pool** when wording entities; do not invent replacements outside the pool.
- Injected salience ranking: element ids ordered high → low salience for greedy center selection.
- Persona card (when present): steer tone and attention inventory; `valence` tags in the pool are annotations only, not selection priority.

## Element ids

`center_element` and every entry in `supporting_elements` must be existing element ids from the deconstruction: `when-*`, `where-*`, `who-*`, `why-*`, `how-*`, `result-*`. Do not invent ids and do not put free text here.

## Response format

Return **only** valid JSON with a root `search_units` array:

```json
{
  "search_units": [
    {
      "id": "p1",
      "kind": "persona-semantic",
      "center_element": "who-1",
      "supporting_elements": ["why-0", "how-1", "result-0"],
      "search_text": "<single English paragraph, 20–80 words>",
      "fit": 0.82
    }
  ]
}
```

## Rules

1. **One declared center per unit.** Each unit is composed around exactly one `center_element` and 2–4 naturally entailed `supporting_elements`. Use distinct centers across units.
2. **Greedy salience.** Use the injected salience ranking top-down. Prefer high-salience elements as centers. If a high-ranked element cannot support a fact-entailed 20–80 word paragraph, move down the ranking.
3. **Axis-alignment (P-Select · ADR-0008 D2, retained semantics):** Frame **each element** through this persona's value axis (the card's 价值轴 / attention inventory): where the lens has a genuine stance, select the pool term carrying that framing; where it does not (fuzzy zone), keep plain `surface` wording. **Do not aim the unit as a whole in one direction — units have no valence.** Pole-versus-pole tension inside one paragraph is welcome (e.g. The-Ruler: *authority* restoring order in an *ungoverned zone*, in the same sentence). You may **rephrase tone** (P-Tone) — e.g. secured a warrant → moved to restore order — but must not add people, causal links, or events not entailed by the neutral decon + chosen pool terms.
4. **Objective anchor required.** Each unit must include at least one objective phrase grounded in the decon vocabulary (a `surface` term or alias of a referenced element). Persona language may add interpretive framing, but cannot float without an objective anchor. The objective fragment bundles are produced separately in code from the fragment ladders; this step contributes only persona-semantic units.
5. **No free facts.** Do not add invented inner monologue, feelings, events, causal links, motives, actors, or outcomes. Only change attention, scale, and phrasing.
6. **POV is incidental.** Do not optimize for a viewpoint character. If a viewpoint read appears naturally it may remain in prose, but runtime treats it as generic `center_element` semantics, not a separate channel.
7. **fit (required):** Each unit must include `"fit": <number>` with **0 ≤ fit ≤ 1** — how well this unit reflects the persona lens on this event (1 = strong natural fit, 0 = forced but still fact-entailed). Do not abstain or omit units (P-Force); use low `fit` when steering is weak.
8. **Count:** 1–3 units, unique ids (`p1`/`p2`/`p3`), consecutive from `p1`.
9. **Variation:** When multiple units, differ by center element and/or fact bundle, not mere paraphrase.
10. **No flavored decon fork:** Do not return the alt-pool or full deconstruction in this response — only `search_units[]`.

## Propagation contract

- ADR-0009 architecture lives in this section, `docs/adr/0009-*.md`, and `docs/SSOT/simplified-news-to-film-workflow.md`.
- Any future change to search unit kinds, center/supporting rules, or objective-anchor semantics must update those three sources together.