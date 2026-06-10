# Threshold Safety Verification

> ADR-0007 D4: ``min_judge_score`` must show zero human=2 killed on observation set before freeze.

## Configuration

| Field | Value |
| --- | --- |
| min_judge_score | 1 |
| threshold_frozen | False |
| rejection_sample_rate | 10% |

## Verification

| Metric | Value |
| --- | --- |
| n_scored | 156 |
| n_human_labeled | 152 |
| n_human_two | 29 |
| n_human_two_on_pass_side | 29 |
| n_human_two_killed | 0 |
| zero_human_two_killed | **YES** |
| pass_side_human_two_retention | 100.0% |
| workload_reduction_rate | 56.6% |

## Verdict: SAFE TO FREEZE
