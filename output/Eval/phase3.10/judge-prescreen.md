# Judge Prescreen Report

- **min_judge_score**: 1 (frozen)
- **rejection_sample_rate**: 10%
- **random_seed**: 42
- **judge_trust_status**: 不采信
- **total_scored**: 156 (no physical deletion)

## Buckets

- **downgrade** (judge=0): 29
- **manual** (judge=1): 99
- **highlight** (judge=2): 28
- **pass threshold** (judge≥1): 127

## Rejection-set audit (per run)

- **01-grid-outage**: 1/4 sampled @ 10% (reweight×4.00)
- **02-corporate-layoff**: 1/6 sampled @ 10% (reweight×6.00)
- **03-election-upset**: 1/3 sampled @ 10% (reweight×3.00)
- **04-celebrity-scandal**: 1/2 sampled @ 10% (reweight×2.00)
- **05-climate-disaster**: 1/3 sampled @ 10% (reweight×3.00)
- **06-tech-monopoly**: 1/4 sampled @ 10% (reweight×4.00)
- **07-migration-border**: 1/4 sampled @ 10% (reweight×4.00)
- **08-sports-underdog**: 1/2 sampled @ 10% (reweight×2.00)
- **09-cultural-backlash**: 0/0 sampled @ 10% (reweight×1.00)
- **10-whistleblower-leak**: 1/1 sampled @ 10% (reweight×1.00)

## Threshold safety (verification slot)

- **zero human-2 killed**: PASS (0 killed)
- **human=2 retention on pass side**: 100.0% (9/9)
- **simulated workload reduction**: 23.1%
