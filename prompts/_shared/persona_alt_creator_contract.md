# Persona Alt-Creator Contract (Phase 3.11.6b · ADR-0009 fragment ladder input)

> **Role:** Per-persona step after A0 verbatim extract + shared objective expansion pass. Output is an **alt-pool overlay** referencing stable element ids plus `salience`. Downstream folds `surface` / `hypernym` / persona alternatives into a unified `fragment ladder`; there is no longer a primary `neutral` / `toned` / `focalized` channel architecture.

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

1. **Optional persona-relative coloring (ADR-0008 D1 — supersedes the ≤3.10 spectrum expectation):** Polar tags are an **optional element-level annotation, not a coverage target**. Tag alternatives `positive` / `negative` **only where this persona's value axis (attention inventory, card 价值轴) has a genuine stance** on the element. For **fuzzy-zone elements** (no genuine stance — the common case for many decon elements), do **not** force a polarity: supply plain fact-entailed terms as `valence: "neutral"` with `provenance: "surface"` / `"hypernym"` (objective-floor wording). **There is no per-element expectation to cover the positive–neutral–negative spectrum.** Valence, when tagged, is **persona-relative**, **not absolute**. Additional terms per bucket are allowed. `neutral` with `provenance: "lens"` = **persona-midpoint** (middle of this persona's lens spectrum, itself optional) — **not** the objective-floor neutral used by the neutral channel (built downstream from `surface` + `hypernym` only).
2. **Fact-entailed only:** Every `term` must be inferable from the neutral decon — especially `who.relations`, `why`, `how`, and stated roles. You may push value (e.g. rumor spreader when the article confirms false accusations spread) but **must not add events, actors, charges, or outcomes** not supported by the decon (no foreign agent, convicted criminal, secret plot, etc.).
3. **Select, not inject:** You are building a **pool** for downstream selection + tone (P-Tone). Do not write pseudo-overviews or narrative paragraphs here.
4. **Element ids:** `element_id` must match an id present in the injected JSON (`who-*`, `where-*`, `why-*`, `how-*`, `result-*`). Do not invent ids.
5. **original_term:** Copy the neutral surface form from the referenced element (`text` or `who`/`where` text field) — do not paraphrase into a new fact.
6. **Coverage:** Prefer covering all `who`, `why`, `how`, and `result` elements **with at least objective-floor terms** (`surface` / `hypernym`); include `where` when persona lens benefits. Polar lens alternatives only where the axis has a genuine stance (rule 1) — never pad fuzzy elements with forced polarity or fiction.
7. **No decon fork:** Do not echo the full deconstruction object, anchor block, or news body in your response — only `persona_id` + `salience[]` + `elements[]` alt-pool rows.

## Salience (center_element priority · ADR-0009)

`salience` is a **top-level field** (sibling to `elements[]`). It expresses **which facts this persona cares about most** for this news item and drives downstream `persona-semantic` center selection.

### Field spec

| property | rule |
| --- | --- |
| **type** | ordered list of **existing** `element_id` strings |
| **order** | **most → least** important **for this persona's value axis** (价值轴) on this news |
| **membership** | **subset / permutation only** of ids present in the injected decon (`who-*`, `where-*`, `why-*`, `how-*`, `result-*`) |
| **forbidden** | inventing ids; adding words, labels, commentary, or prose; paraphrasing element text into `salience` |

### Iron rule: priority ≠ wording

**`salience` ranks element importance; it does not authorize new facts or free prose.**

- You **never** write search unit prose here.
- Downstream uses salience to choose `center_element` candidates for `persona-semantic` units.
- Objective recall is built separately from fragment ladders using `surface` / `alias` / `objective_*` levels.
- Valence remains only an element-level coloring annotation; it never gates eligibility, ranking, or candidate quality.

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

`valence` is annotation, not a selection gate. Use `positive` / `negative` only to label how a term sits relative to **this persona's value axis** (the 价值轴 / Value Axis section of the persona card). Because the axis differs per persona, **the same neutral element can earn opposite-signed framings across personas**:

- A YouTuber accused of spreading false claims → **negative** for **The-Ruler** (`rumor spreader`, disorder) but **positive** for **The-Outlaw** (`truth-teller against power`). Both are fact-entailed from the same decon; only the axis flipped the sign.

Valence does **not** decide objective-floor eligibility, channel role, ranking, or candidate quality. Only explicit `provenance` decides whether a term is objective-floor vocabulary (`surface` / `hypernym`) or lens vocabulary (`lens`). Weak-fit personas still produce a pool (P-Force); downstream `fit` scores alignment.

**Polarity is coloring, not eligibility (ADR-0008 D1/D2):** the card's value axis doubles as the persona's **attention inventory** — both poles name element archetypes the persona attends to, and **both are equally legitimate material** for downstream composition (the archetypal story frames a positive-pole and a negative-pole element in the same pseudo). Tagging an element negative does not demote it; leaving an element untagged (fuzzy zone) does not exclude it.

## Fragment ladder layers

Downstream folds this alt-pool plus shared expansion into a `fragment ladder` per element:

1. **Objective levels** = `surface`, `alias`, `objective_close`, `objective_mid`, `objective_broad`. They power `surface-fragment-bundle` and `event-fragment-bundle` and must remain fact-entailed.
2. **Interpretive / perspective levels** = persona-colored alternatives. They may influence `persona-semantic` wording, but still must bind to existing elements and must not invent facts.

The persona's value axis guides both `salience` and interpretive alternatives. It **must NOT redefine objective vocabulary**: surface/hypernym wording stays objective; only element priority and persona-colored terms differ per persona.

## Provenance layers

Each alternative carries an optional `provenance` tag (one of three layers). A layer **may hold multiple fact-entailed terms** — this absorbs the "multiple alternatives per element" requirement:

| `provenance` | meaning | objective vs lens | typical `valence` |
| --- | --- | --- | --- |
| `surface` | verbatim source term (= `original_term`) | objective floor | `neutral` |
| `hypernym` | objective generalization from the **shared expansion pass**; passes the 客观性试金石 (A2 & A4 would **not** disagree) | objective floor | `neutral` |
| `lens` | persona-relative valence (the persona-midpoint neutral, plus both poles) | lens | `positive` / `neutral` / `negative` |

`provenance` is **optional** (downstream ignores unknown keys). If omitted, downstream treats the term as `lens` for safety. `valence` is only an annotation and never infers objective-floor eligibility. Tag `provenance: "surface"` / `"hypernym"` explicitly when a term is objective-floor vocabulary so the neutral channel can select it; tag `provenance: "lens"` explicitly for persona-colored terms when useful.
