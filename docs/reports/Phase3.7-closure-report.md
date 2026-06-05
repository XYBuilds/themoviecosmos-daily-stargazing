# Phase 3.7 - 12 原型情绪扩散 结案报告

**Status**: **GATE_FAIL · closed 2026-06-05**  
**User decision**: **No-Go** — skip 3.7.6 SSOT migration; defer future iteration

## Executive summary

Phase 3.7 bet: replace inject-style An (A2/A4/A7) with **12 Pearson personas = emotional diffusion of A1** — select + tone from fact-entailed alt-pools, no new events. The phase delivered full scaffolding, 12 persona cards, N=10 batch runs, and a persona-vs-baseline gate. **Evidence did not support the bet**: on partial editor scores (4/10 runs), persona path structural/dual 2-point rate was **20%** vs A1 path **75%** (**lift −55%**). Batch pass rate **50%** (below 60% threshold). User accepted **GATE_FAIL** and closed the phase without SSOT migration.

## Deliverables by todo

| Todo | Outcome | Key artifacts |
| --- | --- | --- |
| **3.7.0** baseline lift | **No-Go** (historical anchor) | `output/Eval/phase3.7/baseline-lift.md` — creative vs A1 lift −28% on phase3.6 data |
| **3.7.1** ADR + roster | Complete | `docs/adr/0004-persona-emotional-diffusion.md`, `docs/SSOT/personas-12.md`, holdout split 01–04 obs / 05–10 |
| **3.7.2** scaffold | Complete | `scripts/personas.py`, alt-creator/screenwriter contracts, `tests/test_personas.py` |
| **3.7.3** Ruler pilot | **Go** | `04-celebrity-scandal` end-to-end; steering/fit/P-Select verified |
| **3.7.4** 12 personas × N=10 | Complete (partial scoring) | `output/Eval/phase3.7/{run_id}/`, `high-hit-score-review.md`; scored runs **01, 02, 07, 09** |
| **3.7.5** gate analysis | **GATE_FAIL** | `scripts/summarize_eval.py` persona_vs_baseline; [`GATE_RESULT.md`](../output/Eval/phase3.7/GATE_RESULT.md) |
| **3.7.6** SSOT migration | **Skipped** | PRD / CONTEXT / contract unchanged; ADR-0004 stays **proposed** |

## Gate evidence (3.7.5)

See [`output/Eval/phase3.7/GATE_RESULT.md`](../output/Eval/phase3.7/GATE_RESULT.md).

1. **fit ↔ resonance**: weak (r ≈ 0.14); low-fit rows rarely hit 2 — abstain threshold not finalized
2. **persona vs A1**: persona path underperforms A1 by 55pp on structural/dual 2-rate; echoes 3.7.0 No-Go
3. **fit × similarity**: viable downstream triage axis; 2-point candidates cluster in upper fit×sim band

**Coverage caveat**: 62/150 high-hit candidates scored across 4/10 runs only. Focus subset (01+02+07+09) shows 100% batch pass but does not overturn full-batch GATE_FAIL.

## What was not done

- **3.7.6**: No PRD / `CONTEXT.md` / `reality-deconstruction-contract.md` updates
- **ADR-0004**: Not promoted to `accepted`
- **Phase 4**: Remains gated
- **Full holdout scoring**: Runs 05–06, 08, 10 unscored; obs 03–04 unscored

## Recommended future iteration hooks

1. **Retry 34 failed batch cells** — alt-creator missing valence bucket errors (`batch-run-summary.json`); re-run with `--no-skip-existing`
2. **Complete holdout scoring** — at minimum 05–10 per ADR discipline before re-gating; avoid overfitting on 01–04
3. **Contract tuning** — if revisiting persona steering: screenwriter selection rules, alt-creator spectrum quality, persona-specific weak-fit handling (Lover/Innocent rows scored 0–1)
4. **P-Abstain threshold** — only after sufficient low-fit + holdout labels; current n=3 too small
5. **Alternative directions** — 3.7.0 already showed inject-style creative loses to A1; next bet may need different steering mechanism than valence alt-pools alone

## Reports index

| Report | Path |
| --- | --- |
| 3.7.0 baseline lift | `docs/reports/Phase3.7.0-baseline-lift-report.md` |
| 3.7.1 ADR + personas | `docs/reports/Phase3.7.1-adr-personas-report.md` |
| 3.7.2 scaffold | `docs/reports/Phase3.7.2-persona-scaffold-report.md` |
| 3.7.3 Ruler pilot | `docs/reports/Phase3.7.3-ruler-04-pilot-report.md` |
| 3.7.5 gate analysis | `docs/reports/Phase3.7.5-gate-fit-analysis-report.md` |
| **Closure (this doc)** | `docs/reports/Phase3.7-closure-report.md` |

## Git / merge

- PR #26 merged to `main` (feat/phase3.7.5-gate-fit-analysis)
- Closure docs committed on `main` after merge
