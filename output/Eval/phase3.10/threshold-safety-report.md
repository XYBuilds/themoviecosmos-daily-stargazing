# Threshold Safety Verification

> ADR-0007 D4: ``min_judge_score`` must show zero human=2 killed on observation set before freeze.

## Configuration

| Field | Value |
| --- | --- |
| min_judge_score | 1 |
| threshold_frozen | True |
| rejection_sample_rate | 10% |

## Verification

| Metric | Value |
| --- | --- |
| n_scored | 156 |
| n_human_labeled | 123 |
| n_human_two | 19 |
| n_human_two_on_pass_side | 19 |
| n_human_two_killed | 0 |
| zero_human_two_killed | **YES** |
| pass_side_human_two_retention | 100.0% |
| workload_reduction_rate | 42.3% |

## Verdict: SAFE TO FREEZE

## Observation set (01–04)

| Metric | Value |
| --- | --- |
| n_scored | 65 |
| n_human_labeled | 65 |
| n_human_two | 9 |
| n_human_two_killed | 0 |
| zero_human_two_killed | **YES** |
| workload_reduction_rate | 23.1% |

## Holdout set (05–10)

| Metric | Value |
| --- | --- |
| n_scored | 91 |
| n_human_labeled | 58 |
| n_human_two | 10 |
| n_human_two_killed | 0 |
| zero_human_two_killed | **YES** |
| workload_reduction_rate | 63.8% |
