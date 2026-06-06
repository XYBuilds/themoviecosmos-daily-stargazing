# Phase 3.9.6 · Single-point pilot notes

**run_id:** `01-grid-outage`  
**eval_phase:** 3.9  
**news:** observation set 01 (grid outage)  
**pipeline:** phase3.8 decon+expansion (read-only) → 12 persona salience neutral+toned → retrieve (A1 held-out oracle via `retrieve-a1.json`)  
**finished_at:** 2026-06-06  
**branch:** `feat/phase3.9.6-single-pilot`

## Execution notes

- First full run: 10/12 personas OK; `The-Hero` failed lens guard (`visayas` in neutral); `The-Lover` alt_creator parse error.
- Retried `The-Hero` + `The-Lover` with `--no-skip-existing` (both succeeded).
- Re-finalized all 12 from disk (`skip_existing` default) → `agents=12`, `candidates=19`, `errors=0`.
- Diversity guard wired into `run_persona_batch.py` **after** this pilot artifact run (see code commit on branch).

## Firewall audit checklist

| # | Check | Result | Evidence |
|---|--------|--------|----------|
| 1 | Salience selection varies per persona | **PASS** | 11/12 unique neutral `fragments` sets; salience in each `persona-pipeline.json` `overlay.salience` drives Top-K (e.g. Creator: `result-0,how-0,…` vs Innocent: `who-1,who-3,…`). |
| 2 | salience≠valence (no emotion leak in neutral) | **PASS** (final) | All 12 neutrals: `provenance_layers` = `surface`+`hypernym` only; no lens terms in neutral text. First Hero attempt failed runtime lens guard — retried clean. |
| 3 | 12 neutrals non-identical (diversity guard) | **FAIL (post-hoc)** | 12 unique texts, but `The-Explorer` vs `The-Hero`: same fragment set, text similarity **0.935** ≥ threshold 0.92 → guard would reject. Pilot completed before guard was wired in batch. |
| 4 | Toned still has hypernym anchor | **PASS** | Pipeline `validate_toned_hypernym_anchor` passed for all generated toned pseudos; hypernym terms present in toned text (e.g. `power shortage`, `generation capacity shortfall`). |
| 5 | A1 not polluting candidates | **PASS** | `agents.json`: 0 A1 rows; `retrieve.json` candidates: 0 A1 `hit_sources`; oracle hits isolated in `retrieve-a1.json` (`a1_hit_tmdb_ids`: 429918, 720321, 841793). |

## Go/No-Go pre-read

- **Salience leg stands up** vs 3.8 (per-persona fragment sets, no 12-way verbatim clone).
- **Diversity guard gap**: Explorer/Hero collision + guard not enforced at batch time during this run → recommend human review before 3.9.7 bulk; may need salience/plan-B tuning or re-pilot after guard wiring.

## Immutability

- `output/Eval/phase3.6`, `phase3.7`, `phase3.8` — not modified (read-only inputs).
