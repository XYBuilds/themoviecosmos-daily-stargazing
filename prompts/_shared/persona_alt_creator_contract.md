# Persona Alt-Creator Contract (Phase 3.7)

> **Role:** Per-persona step between neutral A0 deconstruction and screenwriter. Input is **lens-neutral decon only** (no pre-built alternatives). Output is an **alt-pool overlay** referencing stable element ids — not a fork of the full deconstruction text.

## Input

- Injected `{{deconstruction_json}}`: annotated neutral decon from A0 (`anchor`, `when`, `where`, `who`, `why`, `how`, `result`) with stable ids (`who-0`, `where-0`, `why-0`, `how-0`, `result-0`, …).
- Persona card (when present): emotion / value tendency for this Pearson archetype.
- **Forbidden in input:** any `alternatives`, `valence`, or replacement terms from A0 — A0 does not produce them (P-Source).

## Output format

Return **only** valid JSON (no markdown fences, no preamble):

```json
{
  "persona_id": "The-Ruler",
  "elements": [
    {
      "element_id": "who-0",
      "original_term": "<neutral label from decon who[0].text>",
      "alternatives": [
        { "term": "<positive framing>", "valence": "positive" },
        { "term": "<neutral synonym>", "valence": "neutral" },
        { "term": "<negative framing>", "valence": "negative" }
      ]
    }
  ]
}
```

## Rules (P-Source + P-Select)

1. **Full spectrum per element:** For each decon element you cover, supply **at least one** alternative per valence bucket: `positive`, `neutral`, `negative`. Additional terms in a bucket are allowed if still fact-entailed.
2. **Fact-entailed only:** Every `term` must be inferable from the neutral decon — especially `who.relations`, `why`, `how`, and stated roles. You may push value (e.g. rumor spreader when the article confirms false accusations spread) but **must not add events, actors, charges, or outcomes** not supported by the decon (no foreign agent, convicted criminal, secret plot, etc.).
3. **Select, not inject:** You are building a **pool** for downstream selection + tone (P-Tone). Do not write pseudo-overviews or narrative paragraphs here.
4. **Element ids:** `element_id` must match an id present in the injected JSON (`who-*`, `where-*`, `why-*`, `how-*`, `result-*`). Do not invent ids.
5. **original_term:** Copy the neutral surface form from the referenced element (`text` or `who`/`where` text field) — do not paraphrase into a new fact.
6. **Coverage:** Prefer covering all `who`, `why`, `how`, and `result` elements; include `where` when persona lens benefits. Skip only when no fact-entailed spectrum exists (rare); do not pad with fiction.
7. **No decon fork:** Do not echo the full deconstruction object, anchor block, or news body in your response — only `persona_id` + `elements[]` alt-pool rows.

## Valence guidance (persona-steered)

Weight which bucket gets the strongest terms toward the persona card’s value tendency (ADR-0004 / `docs/SSOT/personas-12.md`). Weak-fit personas still produce a pool (P-Force); downstream `fit` scores alignment.
