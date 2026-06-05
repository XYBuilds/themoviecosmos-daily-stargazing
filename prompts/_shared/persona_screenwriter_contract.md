# Persona Screenwriter Contract (Phase 3.8 · ADR-0005)

> Extends `multi_pseudo_output_contract.md` for the second persona step: compose pseudo-overviews from the **alt-pool overlay** + fragment ids, with optional tone rephrase (P-Tone) and mandatory **fit** self-score (P-Force).

## Shared base

Follow all rules in:

- `prompts/_shared/multi_pseudo_output_contract.md` (1–3 pseudos, fragment ids, how contiguity, TMDB voice)
- `prompts/_shared/output_contract.md`
- `prompts/_shared/deentification_rules.md`

## Additional inputs

- `{{deconstruction_json}}`: verbatim decon (fragment ids only — for `source.fragments` provenance).
- `{{expansion_json}}` (when present): shared hypernym overlay — for objective-floor neutral pseudos and toned hypernym anchors.
- `{{alt_pool_json}}`: persona alt-pool overlay (`persona_id` + `elements[]` with `element_id`, `original_term`, `alternatives[]`). **Select terms from this pool** when wording entities; do not invent replacements outside the pool.
- Persona card (when present): steer tone and which valence bucket to favor.

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
   - **Neutral / objective-floor pseudo (if produced):** any neutral-channel pseudo uses **objective-floor terms only** — `surface` (verbatim) + uncontested `hypernym` (`provenance` = `surface`/`hypernym`). Do **not** pull `lens` terms (including the persona-midpoint neutral) into it; the neutral channel is persona-independent by design.
2. **fit (required):** Each pseudo must include `"fit": <number>` with **0 ≤ fit ≤ 1** — how well this pseudo reflects the persona lens on this event (1 = strong natural fit, 0 = forced but still fact-entailed). Do not abstain or omit pseudos (P-Force); use low `fit` when steering is weak.
3. **Fragments:** Same as base contract — only `why-*`, `how-*`, `result-*` in `source.fragments`; contiguous `how-*` blocks.
4. **Count:** 1–3 pseudos, unique `p1`/`p2`/`p3`, consecutive from `p1`.
5. **Variation:** When multiple pseudos, differ by fragment bundles and/or alt-pool choices, not mere paraphrase.
6. **No flavored decon fork:** Do not return the alt-pool or full deconstruction in this response — only `pseudos[]`.
