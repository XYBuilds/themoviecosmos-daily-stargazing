# Phase 3.9.6 · Single-point pilot notes

**run_id:** `01-grid-outage`  
**eval_phase:** 3.9  
**news:** observation set 01 (grid outage)  
**pipeline:** phase3.8 decon+expansion (read-only) → 12 persona salience neutral+toned → retrieve (A1 held-out oracle via `retrieve-a1.json`)  
**finished_at:** 2026-06-06 (rerun with guard + surface dedup)  
**branch:** `main` (post-fix)

## Execution notes

- **Rerun (2026-06-06):** full 12 persona regen with `--no-skip-existing` after code fixes (surface sentence dedup; diversity guard option B: hard-fail only when neutral **and** toned collide).
- First pass: 10/12 OK; `The-Innocent` lens guard (`officials` in neutral); `The-Ruler` alt_creator parse error.
- Retried Innocent + Ruler with `--no-skip-existing` (both succeeded).
- Re-finalized all 12 from disk (`skip_existing` default) → `agents=12`, `candidates=19`, `errors=0`.

## Firewall audit checklist

| # | Check | Result | Evidence |
|---|--------|--------|----------|
| 1 | Salience selection varies per persona | **PASS** | **12/12** unique neutral `fragments` sets (was 11/12 on first run). |
| 2 | salience≠valence (no emotion leak in neutral) | **PASS** | All 12 neutrals: `provenance_layers` = `surface`+`hypernym` only; lens guard blocked Innocent once, retry clean. |
| 3 | Diversity guard (option B) | **PASS** | 0 hard failures; 0 neutral-only warnings. Mean pairwise n1 sim **0.391**; max **0.790** (Caregiver/Innocent). No Explorer/Hero collision. |
| 4 | Neutral surface dedup | **PASS** | Sage n1: Kepco trip sentence appears once (was twice when how-0+why-0 shared surface). |
| 5 | Toned still has hypernym anchor | **PASS** | `validate_toned_hypernym_anchor` passed for all generated toned pseudos. |
| 6 | A1 not polluting candidates | **PASS** | `agents.json`: 0 A1 rows; candidates: 0 A1 `hit_sources`; oracle hits in `retrieve-a1.json`. |

## Retrieval divergence (post-rerun)

- `query_cosines` mean ≈ 0.84 (embedding space still crowded; toned legs differentiate).
- `topk_jaccard` mean ≈ 0.22; **0** pairs with jaccard = 1.0 (no top-k collapse).

## Go/No-Go pre-read

- **Salience leg stands up** vs 3.8: 12 distinct fragment sets, no 12-way verbatim clone.
- **Guard + dedup fixes validated** on live rerun; batch completes with 12/12 agents.
- Ready for human spot-check → 3.9.7 bulk if approved.

## Immutability

- `output/Eval/phase3.6`, `phase3.7`, `phase3.8` — not modified (read-only inputs).
