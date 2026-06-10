# Persona Screenwriter Contract (Phase 3.8 · ADR-0005; element-centered composition & POV Phase 3.11 · ADR-0008)

> Extends `multi_pseudo_output_contract.md` for the second persona step: compose pseudo-overviews from the **alt-pool overlay** + fragment ids, with optional tone rephrase (P-Tone) and mandatory **fit** self-score (P-Force). §「Element-centered composition & POV focalization」 below is the **single authoritative rule source** for the ADR-0008 composition mode (per-persona vantage seats live in each persona card's attention inventory).

## Shared base

Follow all rules in:

- `prompts/_shared/multi_pseudo_output_contract.md` (1–3 pseudos, fragment ids, how contiguity, TMDB voice)
- `prompts/_shared/output_contract.md`
- `prompts/_shared/deentification_rules.md`

## Additional inputs

- `{{deconstruction_json}}`: verbatim decon (fragment ids only — for `source.fragments` provenance).
- `{{expansion_json}}` (when present): shared hypernym overlay — **visible anchor vocabulary** for toned pseudos; use these hypernyms verbatim in toned text.
- `{{alt_pool_json}}`: persona alt-pool overlay (`persona_id` + `elements[]` with `element_id`, `original_term`, `alternatives[]`). **Select terms from this pool** when wording entities; do not invent replacements outside the pool.
- Persona card (when present): steer tone and which valence bucket to favor.

## Critical id distinction (do not mix)

| Id kind | Examples | Used in |
| --- | --- | --- |
| **element_id** | `who-0`, `where-0`, `why-0` | Alt-pool `elements[].element_id` only — **never** in `source.fragments` |
| **fragment id** | `why-0`, `how-1`, `result-0` | `source.fragments` only — decon **why / how / result** spans |

`who-*` and `where-*` are **element ids**, not fragment ids. Putting `who-0` or `where-0` in `source.fragments` will fail validation.

**Valid fragment example:** `["why-0", "how-0", "result-0"]`  
**Invalid fragment example:** `["who-0", "where-0"]` — use those only via alt-pool term selection, not as fragments.

## Response format

Return **only** valid JSON:

```json
{
  "pseudos": [
    {
      "id": "p1",
      "text": "<single English paragraph, 60–120 words>",
      "fit": 0.82,
      "source": {
        "fragments": ["why-0", "how-1", "result-0"]
      }
    }
  ]
}
```

## Rules beyond multi-pseudo contract

1. **Alt-pool selection (P-Select · axis-alignment, ADR-0008 D2):** Frame **each element** through this persona's value axis (the persona card's 价值轴 / attention inventory): where the lens has a genuine stance on an element, select the pool term carrying that framing; where it does not (fuzzy zone), keep plain `surface` / `hypernym` wording. **Do not aim the pseudo as a whole in one direction — pseudos have no valence.** Pole-versus-pole tension inside one pseudo is welcome; it is the archetypal story shape (e.g. The-Ruler: *authority* (positive pole) *restoring order in an ungoverned zone* (negative pole), in the same sentence). You may **rephrase tone** (P-Tone) — e.g. secured a warrant → moved to restore order — but must not add people, causal links, or events not entailed by the neutral decon + chosen pool terms. Pool `valence` tags, when present, are **persona-relative** (defined by the persona card's value axis) and **optional** — see `persona_alt_creator_contract.md`.
   - **Objective-floor neutral pseudo:** produced **downstream in code** (id `n1`, `channel_role: neutral`) from `surface` + `hypernym` only — **not** by this screenwriter step. Your `p1`–`p3` outputs are **toned** (`channel_role: toned`).
   - **Hypernym anchor (mandatory):** Each toned pseudo **must verbatim embed ≥1 phrase** from the pool/expansion hypernym vocabulary (case-insensitive substring match). Lens-only rephrase without any hypernym substring will be rejected. Pick a short hypernym phrase (e.g. `power grid`, `supply shortfall`) and weave it into the paragraph — do not rely on lens terms alone.
   - **High-lens personas (The-Hero, The-Lover, The-Jester):** Strong persona voice is allowed, but **every** toned pseudo still needs at least one hypernym anchor substring from `{{expansion_json}}` / pool `provenance: hypernym` terms. Dramatic lens wording does not replace the anchor.
2. **fit (required):** Each pseudo must include `"fit": <number>` with **0 ≤ fit ≤ 1** — how well this pseudo reflects the persona lens on this event (1 = strong natural fit, 0 = forced but still fact-entailed). Do not abstain or omit pseudos (P-Force); use low `fit` when steering is weak.
3. **Fragments:** Same as base contract — only `why-*`, `how-*`, `result-*` in `source.fragments`; contiguous `how-*` blocks. **Never** use `who-*` or `where-*` element ids here.
4. **Count:** 1–3 pseudos, unique `p1`/`p2`/`p3`, consecutive from `p1`.
5. **Variation:** When multiple pseudos, differ by fragment bundles and/or alt-pool choices, not mere paraphrase. (In ADR-0008 composition mode, variation is organized by **distinct center elements** — see below.)
6. **No flavored decon fork:** Do not return the alt-pool or full deconstruction in this response — only `pseudos[]`.

## Element-centered composition & POV focalization (Phase 3.11 · ADR-0008 — authoritative rule source)

> **Status & activation:** This section is the **single authoritative rule source** for the ADR-0008 composition mode. It applies **only when the prompt assembly explicitly injects the marker `Composition mode: ADR-0008`** together with this persona's `salience` ranking (wired by code in 3.11.2). Absent that marker, ignore this section entirely — your output rules are unchanged. Downstream consumers (3.11.1 pre-test scaffolding, 3.11.2 generation wiring) must **quote this section verbatim**; per-persona vantage seats are **not** listed here — their SSOT is each persona card's attention inventory (价值轴 Who 正极, marked 视角座位).

### Element-centered composition (ADR-0008 D3)

Variation is organized by **which element each pseudo is built around**, not by valence coverage:

1. **One declared center per pseudo.** Each toned/focalized pseudo is composed **around exactly one center element** (any decon element id: `who-*`, `where-*`, `why-*`, `how-*`, `result-*`), supported by **2–4 supporting elements** naturally entailed alongside it.
2. **Greedy top-down centering.** Take this persona's injected `salience` ranking from the top: if a fact-entailed 60–120 word pseudo can be composed **with that element as its center**, write it; otherwise move down to the next element. **Centers must be distinct across your pseudos.**
3. **Declare, don't score.** You only **declare** each pseudo's center; ranking and budgeting are computed downstream in code from the center's salience rank. Do not self-score, reorder, or pad elements to game importance — element stuffing degrades the overview voice and will be rejected (supporting-element cap enforced).

### POV focalization (ADR-0008 D4)

A **focalized pseudo** retells the event **through the eyes of one character already present in the decon** — focalization (vantage), not just tone.

- **Derivation (no free choice):** When a pseudo's center element is a `who-*` **and** that character instantiates one of the **vantage seats** in this persona's card (attention inventory → Who 正极, marked 视角座位), write that pseudo **focalized through that character**. Otherwise write it as third-person element-centered prose. You never freely pick an interesting character: vantage = salience-derived center × card vantage-seat instantiation.
- **Empathy-seat principle:** Vantage seats are only the Who archetypes this persona **inhabits** (its positive pole). Negative-pole characters are what the persona **watches and opposes** — they are seen, never seen through.
- **Only the eyes change (iron rules — violation = hard fail, regenerate):** The focal character **must be an existing decon `who-*` element**. Focalization changes **from whose vantage the event is seen** — what is near or far, what is at stake *for them*, the order in which the event reaches them. It must **not add anything**: no invented inner monologue or feelings beyond what the decon entails, no new events, no new causal links, no new outcomes.
- **Hypernym anchor retained:** Like every toned pseudo, a focalized pseudo **must verbatim embed ≥1 hypernym anchor phrase** from `{{expansion_json}}` / pool `provenance: hypernym` terms (case-insensitive substring). Focalized wording does not replace the anchor.
- **Third-person grammar is fine:** Focalization is about vantage, not pronouns. Close third person ("she watches the floodwater climb the stairs") is preferred; first person is allowed but never required. De-entification rules apply unchanged.

### Dual floor (ADR-0008 D5 — mandatory)

- The code-built neutral `n1` is untouched by this mode (not your concern, stated for completeness).
- **At least one of your pseudos must be a non-focalized third-person toned pseudo.** Focalized pseudos are additive — they never replace the third-person channel.

### Response additions in composition mode

Each pseudo object additionally declares (base format otherwise unchanged — fragments / fit / 60–120 words / TMDB voice all still apply):

```json
{
  "id": "p1",
  "text": "<single English paragraph, 60–120 words>",
  "fit": 0.82,
  "center": "who-1",
  "channel": "focalized",
  "focal": "who-1",
  "source": { "fragments": ["why-0", "how-1", "result-0"] }
}
```

- `center` (required): the declared center element id (must exist in the injected decon/pool).
- `channel` (required): `"toned"` (third-person) or `"focalized"`.
- `focal` (required iff `channel: "focalized"`): the focal character's `who-*` id; must equal `center` and satisfy the derivation rule.
- **No pseudo-level valence field exists** — pseudos have no polarity (axis-alignment is the persona-ness criterion, see rule 1).

### Propagation contract

- This section (rules) + persona card attention inventories (vantage seats) are the **only** places ADR-0008 composition wording lives. 3.11.1 (pre-test) and 3.11.2 (generation wiring) **reference and inject them verbatim** — no private copies or rewordings.
- Any change to composition rules, the facticity guard, or vantage-seat semantics is an edit **to this section / the cards** (authoritative-wording change discipline applies, see Phase 3.11 plan).
