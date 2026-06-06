# Persona Alt-Creator Contract (Phase 3.9 · ADR-0006)

> **Role:** Per-persona step (P-Lens) after A0 verbatim extract + shared objective expansion pass. Input is **verbatim decon + expansion overlay** (no pre-built lens alternatives). Output is an **alt-pool overlay** referencing stable element ids **plus a `salience` ranking** — not a fork of the full deconstruction text.

## Input

- Injected `{{deconstruction_json}}`: verbatim decon from A0 (`anchor`, `when`, `where`, `who`, `why`, `how`, `result`) with stable ids (`who-0`, `where-0`, `why-0`, `how-0`, `result-0`, …). **Surface terms = verbatim source wording (incl. source valence).**
- Injected `{{expansion_json}}` (when present): shared **hypernym** ladder per `element_id` from P-Expand — persona-independent objective floor.
- Persona card (when present): emotion / value tendency for this Pearson archetype.
- **Forbidden in input:** any `alternatives`, `valence`, or replacement terms from A0 — A0 does not produce them (P-Source).

## Output format

Return **only** valid JSON (no markdown fences, no preamble):

```json
{
  "persona_id": "The-Ruler",
  "salience": ["result-0", "who-0", "how-0", "why-0", "how-1"],
  "elements": [
    {
      "element_id": "who-0",
      "original_term": "<neutral label from decon who[0].text>",
      "alternatives": [
        { "term": "<positive vs THIS persona's value axis>", "valence": "positive", "provenance": "lens" },
        { "term": "<persona-midpoint label>", "valence": "neutral", "provenance": "lens" },
        { "term": "<hypernym from shared expansion pass>", "valence": "neutral", "provenance": "hypernym" },
        { "term": "<negative vs THIS persona's value axis>", "valence": "negative", "provenance": "lens" }
      ]
    }
  ]
}
```

## Rules (P-Source + P-Select)

1. **Persona-relative spectrum per element:** Supply fact-entailed alternatives across valence buckets as appropriate for this persona (`positive`, `neutral`, `negative`). **All three buckets are not required** when a bucket has no defensible term — valence is **persona-relative** (this card's 价值轴 / Value Axis), **not absolute**. Additional terms per bucket are allowed. Here `neutral` in a lens bucket = **persona-midpoint** (middle of this persona's lens spectrum), **not** the objective-floor neutral used by the neutral channel (built downstream from `surface` + `hypernym` only).
2. **Fact-entailed only:** Every `term` must be inferable from the neutral decon — especially `who.relations`, `why`, `how`, and stated roles. You may push value (e.g. rumor spreader when the article confirms false accusations spread) but **must not add events, actors, charges, or outcomes** not supported by the decon (no foreign agent, convicted criminal, secret plot, etc.).
3. **Select, not inject:** You are building a **pool** for downstream selection + tone (P-Tone). Do not write pseudo-overviews or narrative paragraphs here.
4. **Element ids:** `element_id` must match an id present in the injected JSON (`who-*`, `where-*`, `why-*`, `how-*`, `result-*`). Do not invent ids.
5. **original_term:** Copy the neutral surface form from the referenced element (`text` or `who`/`where` text field) — do not paraphrase into a new fact.
6. **Coverage:** Prefer covering all `who`, `why`, `how`, and `result` elements; include `where` when persona lens benefits. Skip only when no fact-entailed spectrum exists (rare); do not pad with fiction.
7. **No decon fork:** Do not echo the full deconstruction object, anchor block, or news body in your response — only `persona_id` + `salience[]` + `elements[]` alt-pool rows.

## Salience (neutral-channel fragment SELECTION · ADR-0006 D6)

`salience` is a **top-level field** (sibling to `elements[]`). It expresses **which facts this persona cares about most** for the **neutral channel only** — it does **not** change how you build lens alternatives in `elements[]`.

### Field spec

| property | rule |
| --- | --- |
| **type** | ordered list of **existing** `element_id` strings |
| **order** | **most → least** important **for this persona's value axis** (价值轴) on this news |
| **membership** | **subset / permutation only** of ids present in the injected decon (`who-*`, `where-*`, `why-*`, `how-*`, `result-*`) |
| **forbidden** | inventing ids; adding words, labels, commentary, or prose; paraphrasing element text into `salience` |

### Iron rule: selection ≠ wording

**`salience` only drives neutral fragment SELECTION; it never affects wording.**

- You **never** write neutral pseudo prose here.
- Downstream takes **Top-K (4–5)** ids from `salience` (head of the list) as `fragment_ids` for `build_objective_floor_neutral_pseudo`.
- Neutral sentences are **always** assembled by template from selected fragments' **`surface`** (verbatim) + **`hypernym`** (objective floor) — persona-neutral vocabulary, **no lens**.
- Valence has **no carrier** in the neutral channel because the persona LLM never authors neutral wording — only ids.

### How to rank

Rank by **this persona's value axis** (see persona card `## 价值轴 (Value Axis)`): e.g. The-Caregiver tends toward `result-*` / `who-*` (who is harmed); The-Creator tends toward `how-*` (mechanism / design). **Who / where** remain in the pool and may appear in `salience` when this persona's lens would care — they are **not** auto-included; inclusion is your salience choice.

### Salience source (primary vs plan B)

| route | when | rule |
| --- | --- | --- |
| **(B) primary** | default for Phase 3.9 | **You** decide per-news `salience` dynamically from the injected decon + this persona's value axis |
| **(C) plan B fallback** | only if pilot shows salience too chaotic / unstable | downstream may inject **soft priors** from the persona card's **价值轴 (Value Axis)** (e.g. "tends to weight who-is-affected and outcomes") — **never** hard rules that fix specific fragment ids. **LLM still makes the final per-news choice** within those soft priors |

Persona cards (`prompts/personas/<id>/persona_card.md`) and `docs/SSOT/personas-12.md` are the **canonical source** for plan B soft preferences.

### Hard validation (downstream)

- `salience` must be a **subset/permutation** of decon element ids — illegal id ⇒ reject.
- No free-text tokens in `salience` — only known `element_id` strings.

## Persona-relative valence

The `valence` buckets are **persona-relative**, **not absolute**. `positive` / `negative` mean "relative to **this persona's value axis** (the 价值轴 / Value Axis section of the persona card)", which names both poles by element type (Who / Where / and, for some personas, When). Because the axis differs per persona, **the same neutral element can earn opposite-signed framings across personas**:

- A YouTuber accused of spreading false claims → **negative** for **The-Ruler** (`rumor spreader`, disorder) but **positive** for **The-Outlaw** (`truth-teller against power`). Both are fact-entailed from the same decon; only the axis flipped the sign.

Weight which bucket gets the strongest terms toward this persona's value tendency (ADR-0004 / `docs/SSOT/personas-12.md`). Weak-fit personas still produce a pool (P-Force); downstream `fit` scores alignment.

## Two neutrals (do not confuse)

There are **two distinct neutrals** — the contract and the cards keep them separate:

1. **Objective-floor neutral** = the surface verbatim term + uncontested `hypernym`. It passes the **客观性试金石** (objectivity touchstone): *would two different personas — e.g. A2 sociologist & A4 mythologist — disagree about it? If no → objective floor; if yes → it's a lens.* The **neutral CHANNEL pseudo** is built from **objective-floor vocabulary only** (surface + hypernym), **never** from a persona-midpoint. **Selection** of which fragments enter that pseudo is **persona-relative** via `salience`; **wording** stays persona-neutral (template-assembled).
2. **Persona-midpoint neutral** = the midpoint of **this persona's** value axis — private, just the middle of the lens spectrum. It is the `valence: "neutral"` bucket's lens-flavored option.

The persona's value axis describes the **lens spectrum (b)** and guides **`salience` ranking (a)**. It **must NOT redefine objective-floor vocabulary**: hypernym/surface wording stays objective; only **which** fragments are selected may differ per persona.

## Provenance layers

Each alternative carries an optional `provenance` tag (one of three layers). A layer **may hold multiple fact-entailed terms** — this absorbs the "multiple alternatives per element" requirement:

| `provenance` | meaning | objective vs lens | typical `valence` |
| --- | --- | --- | --- |
| `surface` | verbatim source term (= `original_term`) | objective floor | `neutral` |
| `hypernym` | objective generalization from the **shared expansion pass**; passes the 客观性试金石 (A2 & A4 would **not** disagree) | objective floor | `neutral` |
| `lens` | persona-relative valence (the persona-midpoint neutral, plus both poles) | lens | `positive` / `neutral` / `negative` |

`provenance` is **optional** (downstream ignores unknown keys). If omitted, treat `positive` / `negative` as `lens`, and `neutral` as the persona-midpoint (`lens`). Tag `provenance` when you also supply objective-floor terms (`surface` / `hypernym`) so the neutral channel can select **only** those.
