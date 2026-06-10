# Phase 3.10.7 · Holdout full judge rerun summary (3.10.1b)

**Generated:** 2026-06-10 11:23 UTC
**prompt_version (holdout):** 3.10.1b-logic-0-guard
**eval_dir:** `output/Eval/phase3.10`

## Holdout judge distribution (before → after)

| run | before (0/1/2) | after (0/1/2) |
| --- | --- | --- |
| 05-climate-disaster | {0: 3, 1: 7, 2: 7} | {0: 11, 1: 2, 2: 4} |
| 06-tech-monopoly | {0: 4, 1: 15} | {0: 19} |
| 07-migration-border | {0: 4, 1: 3, 2: 3} | {0: 6, 1: 1, 2: 3} |
| 08-sports-underdog | {0: 1, 1: 12, 2: 4} | {0: 14, 1: 1, 2: 2} |
| 09-cultural-backlash | {0: 1, 1: 11, 2: 1} | {0: 7, 1: 4, 2: 2} |
| 10-whistleblower-leak | {0: 4, 1: 8, 2: 1} | {0: 13, 1: 1, 2: 1} |

## Transition counts (pre-rerun → 3.10.1b)

- 0→0: **17**
- 1→0: **46**
- 1→1: **5**
- 1→2: **5**
- 2→0: **5**
- 2→1: **4**
- 2→2: **7**

## Prescreen (frozen threshold judge≥1)

- **holdout pairs scored:** 91
- **holdout judge≥1 pool:** 21
- **holdout workload_reduction:** 76.9%
- downgrade: 70
- manual: 9
- highlight: 12

## Full corpus prescreen buckets (156)

- downgrade: 85
- manual: 45
- highlight: 26

## Obs threshold safety (obs 01–04 · obs-fresh-labels via calibration JSON)

- obs n_human_labeled: 65
- obs n_human_two_killed: **0**
- obs zero_human_two_killed: **YES** (frozen threshold still safe on observation set)

> Full-corpus report includes 40 holdout pairs with partial human labels from review; 5 holdout human=2 pairs demoted to judge=0 under 3.10.1b (see threshold-safety-report.md §Killed).

## Artifacts

- `llm-judge-scores-holdout-pre-3107.bak.json` — pre-rerun holdout baseline
- `llm-judge-scores-holdout-3107.json` — 3.10.1b holdout rerun
- `llm-judge-scores.json` — unified 156-pair corpus
- `judge-prescreen.json` / `judge-prescreen.md`
- `threshold-safety-report.md`

