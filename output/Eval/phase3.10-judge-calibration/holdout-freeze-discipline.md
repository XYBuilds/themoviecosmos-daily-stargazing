# Phase 3.10.6 · Holdout freeze discipline

**Generated:** 2026-06-09  
**Branch:** `feat/phase3.10.6-judge-recalibration-threshold-freeze`  
**Eval root:** `output/Eval/phase3.10/`  
**Human labels:** obs 01–04 v2 dual-axis fresh (`obs-fresh-labels.json`, 65 pairs)

## Split

| Set | Run IDs | Role |
| --- | --- | --- |
| **Observation** | `01-grid-outage`, `02-corporate-layoff`, `03-election-upset`, `04-celebrity-scandal` | Calibrate + threshold freeze |
| **Holdout** | `05-climate-disaster` … `10-whistleblower-leak` | Judge once after freeze (3.10.7) |

## Freeze protocol (ADR-0007 D4)

1. **Judge calibration (obs only)** — `scripts/run_phase39_judge_batch.py --obs-only` on 65 high-hit candidates with v2 rubric (`llm_judge.py` dual-axis).
2. **Threshold safety (obs)** — `scripts/judge_prescreen.py --min-judge-score 1` verifies zero human=2 killed.
3. **Threshold freeze** — `judge≥1` frozen (`threshold_frozen=true` in prescreen config); holdout scored once under same prompt + threshold without re-tuning.

## Observation calibration result (v2 fresh labels)

| Metric | Value | Threshold |
| --- | --- | --- |
| Calibration pairs | 65 | ≥ 5 |
| Exact agreement | **0.569** | ≥ 0.60 |
| Within-one agreement | **0.954** | — |
| Pearson r | **0.390** | ≥ 0.50 |
| **trust_status** | **不采信** | screening_only=true |

Judge scores retained for prescreen triage; calibration below pearson/exact gates — workflow criterion pending human review at GATE (3.10.8).

## Threshold safety (`judge≥1` on obs)

| Metric | Value |
| --- | --- |
| n_human_two | 9 |
| n_human_two_killed | **0** |
| pass_side_human_two_retention | **100%** |
| workload_reduction_rate | 21.5% (obs only) |
| **Verdict** | **SAFE TO FREEZE** |

Prescreen buckets (obs): downgrade=14 · manual=37 · highlight=14.

## Frozen constants

| Parameter | Frozen value |
| --- | --- |
| `min_judge_score` (prescreen) | **1** |
| `min_exact_agreement` (calibration) | 0.60 |
| `min_pearson` (calibration) | 0.50 |
| `min_pairs` | 5 |
| Judge rubric | `scripts/llm_judge.py` v3 dual-axis (`resonance_definition_v2.md`) |

## Artifacts

- `llm-judge-scores.json` / `llm-judge-scores.md` — obs judge corpus (65)
- `judge-prescreen.json` / `judge-prescreen.md` — bucketing + rejection audit scaffold
- `threshold-safety-report.md` — zero human-2-killed verification
- `obs-fresh-labels.json` — human ground truth (v2 fresh)

## Immutability

- phase3.6–3.9 eval dirs — not modified
- Holdout human scores — still blank until 3.10.7
