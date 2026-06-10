# Phase 3.10.7 · Pre-approve checklist

**Generated:** 2026-06-10  
**Branch:** `feat/phase3.10.7-holdout-full-rerun`  
**eval_dir:** `output/Eval/phase3.10`

## 1. Label sync (from `high-hit-score-review.md`)

### Observation (01–04) · `obs-fresh-labels.json`

| Run | Synced |
| --- | --- |
| 01-grid-outage | 15 |
| 02-corporate-layoff | 17 |
| 03-election-upset | 17 |
| 04-celebrity-scandal | 16 |
| **Total** | **65 / 65** |

### Holdout prescreen pool (judge≥1 + rejection audit) · `holdout-fresh-labels.json`

| Run | Synced in pool |
| --- | --- |
| 05-climate-disaster | 7 |
| 06-tech-monopoly | 2 |
| 07-migration-border | 4 |
| 08-sports-underdog | 3 |
| 09-cultural-backlash | 6 |
| 10-whistleblower-leak | 2 |
| **Pool total** | **24 / 28** labeled |

**Prescreen pool:** 28 keys (21 manual judge≥1 + 7 rejection audit).  
**Skipped:** 63 holdout blocks outside pool; 4 pool items still **blank** editor 共振分 in review:

| run | tmdb_id | bucket |
| --- | --- | --- |
| 05-climate-disaster | 107100 | rejection_audit |
| 07-migration-border | 151708 | rejection_audit |
| 08-sports-underdog | 232679 | rejection_audit |
| 09-cultural-backlash | 86962 | rejection_audit |

**Optional holdout (judge=0, not in pool):** 38 blanks may skip per plan.

### Full review human coverage

- **118** pairs with editor 共振分 in review (65 obs + 53 holdout optional/extra).

---

## 2. Threshold safety (`threshold-safety-report.md` · 3.10.1b prescreen)

| Slice | n_human_labeled | n_human_two | n_human_two_killed | Verdict |
| --- | --- | --- | --- | --- |
| **Full corpus (156)** | 118 | 19 | **0** | SAFE TO FREEZE |
| **Obs 01–04** | 65 | 9 | **0** | PASS |
| **Holdout 05–10** | 53 | 10 | **0** | PASS |

- Full workload_reduction_rate: **39.8%**
- Obs workload_reduction_rate: **23.1%**
- Holdout workload_reduction_rate: **60.4%**

### Prior audit · 5 pairs with stale `human=2` in judge JSON (now resolved in review)

Under **old** embedded judge human scores, these judge=0 pairs registered as human=2 killed. **Current review editor scores** no longer assign human=2:

| run | tmdb_id | judge | review human now |
| --- | --- | --- | --- |
| 05-climate-disaster | 257637 | 0 | **1** |
| 05-climate-disaster | 163293 | 0 | **1** |
| 06-tech-monopoly | 13748 | 0 | **0** |
| 06-tech-monopoly | 4959 | 0 | **0** |
| 08-sports-underdog | 5693 | 0 | **1** |

No action required unless you intend to restore human=2 on any of these.

---

## 3. Baseline combo vs pure_fact (`holdout-prescreen-baseline-3107.md`)

| Metric | Value |
| --- | --- |
| combo structural_2_rate | **11.5%** |
| pure_fact structural_2_rate | **0.0%** |
| combo > pure_fact (full) | **YES** |
| obs combo > pure_fact | **True** |
| holdout combo > pure_fact | **True** |
| obs/holdout consistent | **True** |
| judge_calibration_trusted | **False** |

Prescreen buckets (156): downgrade **85** · manual **45** · highlight **26**

---

## 4. Artifacts updated

- [x] `obs-fresh-labels.json` (65)
- [x] `holdout-fresh-labels.json` (24 in pool)
- [x] `judge-prescreen.json` / `judge-prescreen.md` (human_score from review)
- [x] `threshold-safety-report.md` (full + obs + holdout sections)
- [x] `holdout-prescreen-baseline-3107.md` + `holdout-prescreen-baseline.json`

---

## 5. Approve gate

| Check | Status |
| --- | --- |
| Obs 65/65 labeled | ✅ |
| Holdout mandatory pool 28/28 | ⚠️ **24/28** — 4 rejection-audit blanks |
| Threshold zero human-2-killed (obs + holdout) | ✅ (with current review scores) |
| combo > pure_fact lift | ✅ |
| judge_calibration_trusted | ❌ False |

**Recommendation:** ⚠️ **PAUSED** — fill 4 blank rejection-audit 共振分 (or confirm skip), then `approve` to mark p310-7 complete / merge.
