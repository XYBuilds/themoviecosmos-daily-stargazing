# Phase 3.9.7 · Holdout freeze discipline

**Generated:** 2026-06-06  
**Branch:** `feat/phase3.9.7-bulk-eval-run`  
**Eval root:** `output/Eval/phase3.9/`

## Split

| Set | Run IDs | Role |
| --- | --- | --- |
| **Observation** | `01-grid-outage`, `02-corporate-layoff`, `03-election-upset`, `04-celebrity-scandal` | Tune / calibrate only |
| **Holdout** | `05-climate-disaster` … `10-whistleblower-leak` | Score once after freeze |

## Freeze protocol (ADR-0006 D4)

1. **Bulk persona + retrieve** — all 10 runs × 12 persona (salience neutral + toned), A1 oracle parallel (`retrieve-a1.json`). Phase 3.8 decon+expansion read-only; phase 3.6/3.7/3.8 not modified.
2. **Observation scoring** — `score_eval_candidates` → `high-hit-score-review.md`; human 共振分 backfilled from phase 3.8 obs blocks (16 matched candidates, plain scores only).
3. **Judge calibration (obs only)** — `scripts/run_phase39_judge_batch.py --obs-only` on 65 high-hit / pure-neutral candidates.
4. **Threshold freeze** — constants from `scripts/llm_judge.py` (not adjusted after holdout peek):

   | Parameter | Frozen value |
   | --- | --- |
   | `min_exact_agreement` | 0.60 |
   | `min_pearson` | 0.50 |
   | `min_pairs` | 5 |

5. **Holdout judge (once)** — `--holdout-only` after freeze; same thresholds, no re-tuning on holdout human scores.

## Observation calibration result

| Metric | Value |
| --- | --- |
| Calibration pairs (obs, human+judge) | 16 |
| Exact agreement | 0.188 |
| Within-one agreement | (see `llm-judge-scores.json`) |
| Pearson r | 0.381 |
| **trust_status** | **不采信** (screening_only=true) |

Judge scores are retained for triage but **not trusted** for GATE until human re-calibration or rubric alignment improves. Human 共振分 on obs remain the primary longitudinal anchor; judge flags disagreements only.

**Final merged judge corpus:** 156 candidates (65 obs + 91 holdout), all scored once under frozen thresholds.

## Artifacts

- `batch-run-summary.json` — 10/10 runs, 12/12 personas each, 0 errors
- `high-hit-score-review.md` — 156 candidates (≥5 pseudo hit or pure-neutral)
- `llm-judge-scores.json` / `llm-judge-scores.md` — incremental judge output
- Per-run `{run_id}/retrieve.json`, `retrieve-a1.json`, `agents.json`, persona pipelines

## Immutability

- `output/Eval/phase3.6`, `phase3.7`, `phase3.8` — **not modified** (verified via git status)
