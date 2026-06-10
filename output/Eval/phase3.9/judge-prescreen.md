# Judge Prescreen Report

- **min_judge_score**: 1 (adjustable)
- **rejection_sample_rate**: 10%
- **random_seed**: 42
- **judge_trust_status**: 采信
- **total_scored**: 156 (no physical deletion)

## Buckets

- **downgrade** (judge=0): 87
- **manual** (judge=1): 49
- **highlight** (judge=2): 20
- **pass threshold** (judge≥1): 69

## Rejection-set audit (per run)

- **01-grid-outage**: 1/10 sampled @ 10% (reweight×10.00)
- **02-corporate-layoff**: 1/10 sampled @ 10% (reweight×10.00)
- **03-election-upset**: 1/6 sampled @ 10% (reweight×6.00)
- **04-celebrity-scandal**: 1/7 sampled @ 10% (reweight×7.00)
- **05-climate-disaster**: 1/10 sampled @ 10% (reweight×10.00)
- **06-tech-monopoly**: 1/14 sampled @ 10% (reweight×14.00)
- **07-migration-border**: 1/7 sampled @ 10% (reweight×7.00)
- **08-sports-underdog**: 1/7 sampled @ 10% (reweight×7.00)
- **09-cultural-backlash**: 1/8 sampled @ 10% (reweight×8.00)
- **10-whistleblower-leak**: 1/8 sampled @ 10% (reweight×8.00)

## Threshold safety (verification slot)

- **zero human-2 killed**: PASS (0 killed)
- **human=2 retention on pass side**: 100.0% (29/29)
- **simulated workload reduction**: 56.6%
