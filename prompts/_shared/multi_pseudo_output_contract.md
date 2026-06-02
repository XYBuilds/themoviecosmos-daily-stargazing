# Multi-Pseudo Output Contract (Phase 3.5)

> Each writer agent (A1 / A2 / A4 / A7) returns **exactly 3** pseudo-overviews per call, not one paragraph.

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

- **Count**: exactly **3** objects in `pseudos`, with ids `p1`, `p2`, `p3`.
- **Fragments**: every `source.fragments` entry must be a **`why-*`, `how-*`, or `result-*` id** from the injected JSON. Do **not** put section names (`when`, `where`, `who`) or tag text in `fragments` — use only narrative fragment ids.
- **How blocks**: if you use any `how-*` fragment, the set of `how-*` ids in one pseudo must be **contiguous** in step order (e.g. `how-0,how-1` OK; `how-0,how-2` without `how-1` not OK).
- **Variation across p1–p3**: the three pseudos must differ by **which fragments you combine**, not by paraphrasing the same bundle three times.
- **Text**: each `text` follows `output_contract.md` (English, single paragraph, 60–120 words, TMDB-overview voice).
- **De-entification**: follow `deentification_rules.md` (default abstract; **load-bearing** proper names or numbers may stay when removing them would erase the hook).
