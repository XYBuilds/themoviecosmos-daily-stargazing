# Persona Screenwriter Contract (Phase 3.11.6b · ADR-0009 fragment ladder / search unit)

> Extends `multi_pseudo_output_contract.md` for the persona semantic drafting step. The LLM drafts compact, fact-entailed persona-semantic text around `center_element`; downstream code converts it into `search_units.persona_semantic_units`. `toned` / `focalized` / `neutral` are legacy compatibility labels only and are not the runtime retrieval architecture.

## Shared base

Follow all rules in:

- `prompts/_shared/multi_pseudo_output_contract.md` (1–3 pseudos, fragment ids, how contiguity, TMDB voice)
- `prompts/_shared/output_contract.md`
- `prompts/_shared/deentification_rules.md`

## Additional inputs

- `{{deconstruction_json}}`: verbatim decon (fragment ids only — for `source.fragments` provenance).
- `{{expansion_json}}` (when present): shared hypernym overlay — **visible anchor vocabulary** for toned pseudos; use these hypernyms verbatim in toned text.
- `{{alt_pool_json}}`: persona alt-pool overlay (`persona_id` + `elements[]` with `element_id`, `original_term`, `alternatives[]`). **Select terms from this pool** when wording entities; do not invent replacements outside the pool.
- Persona card (when present): steer tone and attention inventory; `valence` tags in the pool are annotations only, not selection priority.

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
5. **Variation:** When multiple pseudos, differ by center element and/or fact bundle, not mere paraphrase. In ADR-0009 runtime these drafts become `persona-semantic` search units.
6. **No flavored decon fork:** Do not return the alt-pool or full deconstruction in this response — only `pseudos[]`.

## Persona-semantic search unit drafting (Phase 3.11.6b · ADR-0009)

> **Runtime status:** retrieval no longer runs `neutral` / `toned` / `focalized` as primary channels. Code builds `surface-fragment-bundle` and `event-fragment-bundle` from objective fragment ladders, then converts your center-based drafts into `persona-semantic` search units. The `pseudos[]` wrapper remains only because the current parser expects it.

### Centered semantic drafting

1. **One declared center per draft.** Each draft is composed around exactly one `center` element id (`when-*`, `where-*`, `who-*`, `why-*`, `how-*`, `result-*`) and 1–4 naturally entailed supporting elements in `source.fragments`.
2. **Greedy salience.** Use the injected salience ranking top-down. Prefer distinct centers across drafts. If a high-ranked element cannot support a fact-entailed 20–80 word semantic unit, move down.
3. **Objective anchor required.** Each draft must include at least one objective phrase from the expansion / fragment ladder vocabulary (`surface`, alias, or objective hypernym). Persona language may add interpretive framing, but cannot float without an objective anchor.
4. **No free facts.** Do not add invented inner monologue, feelings, events, causal links, motives, actors, or outcomes. Only change attention, scale, and phrasing.
5. **POV downshift.** Do not optimize for `focalized` or `focal`. If a viewpoint read naturally appears, it may remain in prose, but runtime treats it as generic `center_element` semantics, not a separate channel.
6. **No dual-floor rule.** The old `neutral n1` and non-POV toned floor are replaced by objective fragment bundles plus persona-semantic search units.

### Response additions in compatibility mode

Each pseudo object additionally declares fields that downstream maps to `persona-semantic`:

```json
{
  "id": "p1",
  "text": "<single English paragraph, 20–80 words>",
  "fit": 0.82,
  "center": "who-1",
  "channel": "toned",
  "source": { "fragments": ["why-0", "how-1", "result-0"] }
}
```

- `center` (required): becomes `center_element`.
- `source.fragments` (required): becomes `supporting_elements`; use existing element ids only.
- `channel` (compatibility): use `"toned"`. `"focalized"` is accepted only for legacy parser compatibility and must not imply a separate runtime path.
- `fit` (required): 0–1 natural fit score for this persona on this event.
- No pseudo-level valence field exists.

### Propagation contract

- ADR-0009 architecture lives in this section, `docs/adr/0009-*.md`, and `docs/temp/simplified-news-to-film-workflow.md`.
- Any future change to search unit kinds, center/supporting rules, or objective-anchor semantics must update those three sources together.
