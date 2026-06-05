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
        { "term": "<positive vs THIS persona's value axis>", "valence": "positive", "provenance": "lens" },
        { "term": "<persona-midpoint label>", "valence": "neutral", "provenance": "lens" },
        { "term": "<objective generalization from tag ladder>", "valence": "neutral", "provenance": "hypernym" },
        { "term": "<negative vs THIS persona's value axis>", "valence": "negative", "provenance": "lens" }
      ]
    }
  ]
}
```

## Rules (P-Source + P-Select)

1. **Full spectrum per element:** For each decon element you cover, supply **at least one** alternative per valence bucket: `positive`, `neutral`, `negative`. Additional terms in a bucket are allowed if still fact-entailed. The buckets are **persona-relative** (defined by this persona card's 价值轴 / Value Axis), **not absolute** — see "Persona-relative valence" below. Here `neutral` = **persona-midpoint** (the middle of this persona's lens spectrum), **not** the objective-floor neutral used by the neutral channel.
2. **Fact-entailed only:** Every `term` must be inferable from the neutral decon — especially `who.relations`, `why`, `how`, and stated roles. You may push value (e.g. rumor spreader when the article confirms false accusations spread) but **must not add events, actors, charges, or outcomes** not supported by the decon (no foreign agent, convicted criminal, secret plot, etc.).
3. **Select, not inject:** You are building a **pool** for downstream selection + tone (P-Tone). Do not write pseudo-overviews or narrative paragraphs here.
4. **Element ids:** `element_id` must match an id present in the injected JSON (`who-*`, `where-*`, `why-*`, `how-*`, `result-*`). Do not invent ids.
5. **original_term:** Copy the neutral surface form from the referenced element (`text` or `who`/`where` text field) — do not paraphrase into a new fact.
6. **Coverage:** Prefer covering all `who`, `why`, `how`, and `result` elements; include `where` when persona lens benefits. Skip only when no fact-entailed spectrum exists (rare); do not pad with fiction.
7. **No decon fork:** Do not echo the full deconstruction object, anchor block, or news body in your response — only `persona_id` + `elements[]` alt-pool rows.

## Persona-relative valence

The `valence` buckets are **persona-relative**, **not absolute**. `positive` / `negative` mean "relative to **this persona's value axis** (the 价值轴 / Value Axis section of the persona card)", which names both poles by element type (Who / Where / and, for some personas, When). Because the axis differs per persona, **the same neutral element can earn opposite-signed framings across personas**:

- A YouTuber accused of spreading false claims → **negative** for **The-Ruler** (`rumor spreader`, disorder) but **positive** for **The-Outlaw** (`truth-teller against power`). Both are fact-entailed from the same decon; only the axis flipped the sign.

Weight which bucket gets the strongest terms toward this persona's value tendency (ADR-0004 / `docs/SSOT/personas-12.md`). Weak-fit personas still produce a pool (P-Force); downstream `fit` scores alignment.

## Two neutrals (do not confuse)

There are **two distinct neutrals** — the contract and the cards keep them separate:

1. **Objective-floor neutral** = the surface verbatim term + uncontested `hypernym` (shared, **persona-independent**). It passes the **客观性试金石** (objectivity touchstone): *would two different personas — e.g. A2 sociologist & A4 mythologist — disagree about it? If no → objective floor; if yes → it's a lens.* The **neutral CHANNEL pseudo** is built from **objective-floor only** (surface + hypernym), **never** from a persona-midpoint.
2. **Persona-midpoint neutral** = the midpoint of **this persona's** value axis — private, just the middle of the lens spectrum. It is the `valence: "neutral"` bucket's lens-flavored option.

The persona's value axis describes the **lens spectrum (b)**. It **must NOT redefine the objective floor (a)**: the floor stays persona-independent.

## Provenance layers

Each alternative carries an optional `provenance` tag (one of three layers). A layer **may hold multiple fact-entailed terms** — this absorbs the "multiple alternatives per element" requirement:

| `provenance` | meaning | objective vs lens | typical `valence` |
| --- | --- | --- | --- |
| `surface` | verbatim source term (= `original_term`) | objective floor | `neutral` |
| `hypernym` | objective generalization from the tag ladder; passes the 客观性试金石 (A2 & A4 would **not** disagree) | objective floor | `neutral` |
| `lens` | persona-relative valence (the persona-midpoint neutral, plus both poles) | lens | `positive` / `neutral` / `negative` |

`provenance` is **optional** (downstream ignores unknown keys). If omitted, treat `positive` / `negative` as `lens`, and `neutral` as the persona-midpoint (`lens`). Tag `provenance` when you also supply objective-floor terms (`surface` / `hypernym`) so the neutral channel can select **only** those.
