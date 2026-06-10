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
| n_human_labeled | 105 |
| n_human_two | 22 |
| n_human_two_on_pass_side | 17 |
| n_human_two_killed | 5 |
| zero_human_two_killed | **NO** |
| pass_side_human_two_retention | 77.3% |
| workload_reduction_rate | 41.0% |

## Killed human=2 items

- 05-climate-disaster / 257637: judge=0 human=2 — Poem of the Sea (1958) [THE-EXPLORER, THE-CREATOR, THE-MAGICIAN, THE-HERO, THE-CAREGIVER, THE-RULER, THE-OUTLAW, THE-SAGE, THE-JESTER, THE-EVERYMAN] [优质·多agent]
- 05-climate-disaster / 163293: judge=0 human=2 — Deluge (1933) [THE-LOVER, THE-EVERYMAN, THE-OUTLAW, THE-SAGE]
- 06-tech-monopoly / 13748: judge=0 human=2 — A Ticket to Space (2006) [THE-INNOCENT, THE-HERO, THE-CREATOR, THE-MAGICIAN, THE-JESTER] [优质·多agent]
- 06-tech-monopoly / 4959: judge=0 human=2 — The International (2009) [THE-LOVER, THE-OUTLAW, THE-EVERYMAN]
- 08-sports-underdog / 5693: judge=0 human=2 — Hoosiers (1986) [THE-OUTLAW, THE-CREATOR, THE-MAGICIAN, THE-JESTER, THE-INNOCENT, THE-CAREGIVER] [优质·多agent]

## Verdict: UNSAFE — relax threshold or fix rubric
