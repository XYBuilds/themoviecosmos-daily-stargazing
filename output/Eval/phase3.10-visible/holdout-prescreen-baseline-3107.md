# Phase 3.10.7 · Holdout prescreen recheck baseline

**Generated:** 2026-06-10
**Frozen threshold:** judge≥1 (threshold_frozen=True)

## Prescreen buckets (full corpus 156)

- downgrade (judge=0): 85
- manual (judge=1): 45
- highlight (judge=2): 26

## Resonance recheck (dual-axis v2 · similarity-controlled)

| Metric | combo | pure_fact | lift? |
| --- | --- | --- | --- |
| structural_2_rate | 11.5% | 0.0% | YES |
| obs combo>pure_fact | True |
| holdout combo>pure_fact | True |
| obs/holdout consistent | True |

## Workflow safety

| Metric | Value |
| --- | --- |
| workload_reduction_rate | 39.8% |
| n_human_two | 19 |
| n_human_two_killed | 0 |
| zero_human_two_killed | **YES** |
| judge_calibration_trusted | False |

## Artifacts

- `llm-judge-scores.json` — full 156 judge corpus
- `judge-prescreen.json` / `threshold-safety-report.md`
- `holdout-fresh-labels.json` — prescreen-pool human labels
- `holdout-prescreen-baseline.json` — summarize_eval D5 export
