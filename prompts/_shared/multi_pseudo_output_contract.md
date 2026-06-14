# Multi-Pseudo Output Contract (Phase 3.5+)

> Each writer agent (A1 / A2 / A4 / A7) returns **up to 3** pseudo-overviews per call (1–3), not one paragraph.
>
> **Scope (ADR-0009):** this `pseudos[]` contract governs the A1/A2/A4/A7 news writer agents only. The persona drafting step does **not** use this shape — it emits `search_units[]` (see `persona_screenwriter_contract.md`).

## Response format

Return **only** valid JSON (no markdown fences, no preamble). Shape:

```json
{
  "pseudos": [
    {
      "id": "p1",
      "text": "<single English paragraph, 60–120 words>",
      "source": {
        "fragments": ["why-0", "how-1", "result-0"]
      }
    },
    {
      "id": "p2",
      "text": "...",
      "source": { "fragments": ["result-1"] }
    },
    {
      "id": "p3",
      "text": "...",
      "source": { "fragments": ["why-0", "how-0", "how-1"] }
    }
  ]
}
```

## Rules

- **Count**: **1–3** objects in `pseudos`, each with a unique id from `p1`, `p2`, `p3` (use consecutive ids starting at `p1`; do not skip ids within your set). If the event is a poor fit for extra angles, write **fewer** pseudos rather than padding weak ones.
- **Fragments**: every `source.fragments` entry must be a **`why-*`, `how-*`, or `result-*` id** from the injected JSON. Do **not** put section names (`when`, `where`, `who`) or tag text in `fragments` — use only narrative fragment ids.
- **How blocks**: if you use any `how-*` fragment, the set of `how-*` ids in one pseudo must be **contiguous** in step order (e.g. `how-0,how-1` OK; `how-0,how-2` without `how-1` not OK).
- **Variation across pseudos**: when you write more than one pseudo, they must differ by **which fragments you combine**, not by paraphrasing the same bundle.
- **Text**: each `text` follows `output_contract.md` (English, single paragraph, 60–120 words, TMDB-overview voice).
- **De-entification**: follow `deentification_rules.md` (default abstract; **load-bearing** proper names or numbers may stay when removing them would erase the hook).
