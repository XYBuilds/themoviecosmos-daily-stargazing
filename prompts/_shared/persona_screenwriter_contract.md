# Persona Screenwriter Contract (Phase 3.8 · ADR-0005)

> Extends `multi_pseudo_output_contract.md` for the second persona step: compose pseudo-overviews from the **alt-pool overlay** + fragment ids, with optional tone rephrase (P-Tone) and mandatory **fit** self-score (P-Force).

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

1. **Alt-pool selection (P-Select):** Prefer alternatives from the injected pool that match this persona’s value tendency. You may **rephrase tone** (P-Tone) — e.g. secured a warrant → moved to restore order — but must not add people, causal links, or events not entailed by the neutral decon + chosen pool terms. The pool's `valence` buckets are **persona-relative** (defined by the persona card's 价值轴 / Value Axis), not absolute — see `persona_alt_creator_contract.md`.
   - **Objective-floor neutral pseudo:** produced **downstream in code** (id `n1`, `channel_role: neutral`) from `surface` + `hypernym` only — **not** by this screenwriter step. Your `p1`–`p3` outputs are **toned** (`channel_role: toned`).
   - **Hypernym anchor (mandatory):** Each toned pseudo **must verbatim embed ≥1 phrase** from the pool/expansion hypernym vocabulary (case-insensitive substring match). Lens-only rephrase without any hypernym substring will be rejected. Pick a short hypernym phrase (e.g. `power grid`, `supply shortfall`) and weave it into the paragraph — do not rely on lens terms alone.
   - **High-lens personas (The-Hero, The-Lover, The-Jester):** Strong persona voice is allowed, but **every** toned pseudo still needs at least one hypernym anchor substring from `{{expansion_json}}` / pool `provenance: hypernym` terms. Dramatic lens wording does not replace the anchor.
2. **fit (required):** Each pseudo must include `"fit": <number>` with **0 ≤ fit ≤ 1** — how well this pseudo reflects the persona lens on this event (1 = strong natural fit, 0 = forced but still fact-entailed). Do not abstain or omit pseudos (P-Force); use low `fit` when steering is weak.
3. **Fragments:** Same as base contract — only `why-*`, `how-*`, `result-*` in `source.fragments`; contiguous `how-*` blocks. **Never** use `who-*` or `where-*` element ids here.
4. **Count:** 1–3 pseudos, unique `p1`/`p2`/`p3`, consecutive from `p1`.
5. **Variation:** When multiple pseudos, differ by fragment bundles and/or alt-pool choices, not mere paraphrase.
6. **No flavored decon fork:** Do not return the alt-pool or full deconstruction in this response — only `pseudos[]`.
