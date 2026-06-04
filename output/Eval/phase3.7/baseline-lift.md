# Phase 3.7.0 · Baseline vs Creative 2-Point Lift

- **Source:** `\\192.168.1.110\Hermes_Workspace\themoviecosmos-daily-stargazing\output\Eval\phase3.6`
- **Runs scanned:** 10
- **Scored candidates (excluded missing 共振分):** 57
- **Missing 共振分:** 118

## Buckets

| Bucket | Scored | 2-point | 2-point rate | 1-point | 0-point |
| --- | ---: | ---: | ---: | ---: | ---: |
| baseline-only | 8 | 3 | 37.5% | 4 | 1 |
| creative-only | 42 | 4 | 9.5% | 4 | 34 |
| both | 7 | 5 | 71.4% | 1 | 1 |

## Creative vs A1 neutral lift

- **baseline-only (A1 neutral):** 37.5% (3/8)
- **creative-only (A2/A4/A7, no A1):** 9.5% (4/42)
- **both (A1 + creative):** 71.4% (5/7)
- **creative-touched (creative-only + both):** 18.4% (9/49)

- **Lift (creative-only - baseline-only):** -28.0%
- **Lift (creative-touched - baseline-only):** -19.1%

## Go/No-Go: **No-Go**

creative-only vs A1 neutral lift ≈ 0 (-28.0%; creative-touched aggregate -19.1%); pause and re-evaluate whether emotion steering is worth pursuing before 3.7.1

### Interpretation

- **baseline-only:** candidate hit only via A1 faithful restatement.
- **creative-only:** hit via A2/A4/A7 injection-style agents without A1.
- **both:** A1 and at least one creative agent both contributed hits.
- Phase 3.7 bets on persona emotional diffusion *adding* resonance beyond A1; this anchor uses Phase 3.6 scored data as the pre-refactor baseline.
