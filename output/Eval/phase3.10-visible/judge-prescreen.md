# Judge Prescreen Report

- **min_judge_score**: 1 (frozen)
- **rejection_sample_rate**: 10%
- **random_seed**: 42
- **judge_trust_status**: 不采信
- **total_scored**: 156 (no physical deletion)

## Buckets

- **downgrade** (judge=0): 85
- **manual** (judge=1): 45
- **highlight** (judge=2): 26
- **pass threshold** (judge≥1): 71

## Rejection-set audit (per run)

- **01-grid-outage**: 1/4 sampled @ 10% (reweight×4.00)
- **02-corporate-layoff**: 1/6 sampled @ 10% (reweight×6.00)
- **03-election-upset**: 1/3 sampled @ 10% (reweight×3.00)
- **04-celebrity-scandal**: 1/2 sampled @ 10% (reweight×2.00)
- **05-climate-disaster**: 1/11 sampled @ 10% (reweight×11.00)
- **06-tech-monopoly**: 2/19 sampled @ 10% (reweight×9.50)
- **07-migration-border**: 1/6 sampled @ 10% (reweight×6.00)
- **08-sports-underdog**: 1/14 sampled @ 10% (reweight×14.00)
- **09-cultural-backlash**: 1/7 sampled @ 10% (reweight×7.00)
- **10-whistleblower-leak**: 1/13 sampled @ 10% (reweight×13.00)

## Threshold safety (verification slot)

- **zero human-2 killed**: PASS (0 killed)
- **human=2 retention on pass side**: 100.0% (19/19)
- **simulated workload reduction**: 42.3%
