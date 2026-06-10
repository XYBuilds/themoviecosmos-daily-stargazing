# Phase 3.10.7 · Holdout prescreen recheck baseline

**Generated:** 2026-06-09
**Frozen threshold:** judge≥1 (threshold_frozen=True)

## Prescreen buckets (full corpus 156)

- downgrade (judge=0): 29
- manual (judge=1): 99
- highlight (judge=2): 28

## Resonance recheck (dual-axis v2 · similarity-controlled)

| Metric | combo | pure_fact | lift? |
| --- | --- | --- | --- |
| structural_2_rate | 0.0% | 0.0% | NO |
| obs combo>pure_fact | None |
| holdout combo>pure_fact | None |
| obs/holdout consistent | None |

## Workflow safety

| Metric | Value |
| --- | --- |
| workload_reduction_rate | 23.1% |
| n_human_two | 9 |
| n_human_two_killed | 0 |
| zero_human_two_killed | **YES** |
| judge_calibration_trusted | None |

## Artifacts

- `llm-judge-scores.json` — full 156 judge corpus
- `judge-prescreen.json` / `threshold-safety-report.md`
- `holdout-fresh-labels.json` — prescreen-pool human labels
- `holdout-prescreen-baseline.json` — summarize_eval D5 export
