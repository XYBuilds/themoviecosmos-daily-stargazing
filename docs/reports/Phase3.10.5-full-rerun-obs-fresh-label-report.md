# Phase 3.10.5 - Full rerun + obs fresh labels 交付报告

## 1. 改动范围 (Scope)

- `scripts/promote_phase39_to_phase310.py` — promote phase3.9 run artifacts into `output/Eval/phase3.10/{run_id}/` (generation recipe unchanged)
- `scripts/apply_obs_fresh_labels_phase310.py` — apply v2 dual-axis fresh labels to obs 01–04 in unified review + audit JSON
- `output/Eval/phase3.10/{01..10}-*/` — 10-run full-chain artifacts (promoted from phase3.9)
- `output/Eval/phase3.10/batch-run-summary.json` — batch promote summary
- `output/Eval/phase3.10/high-hit-score-review.md` — unified review (obs 01–04 freshly labeled)
- `output/Eval/phase3.10/obs-fresh-labels.json` — fresh-label audit (scores, types, causal_test, remark)
- `output/Eval/phase3.10/obs-fresh-labels-summary.md` — human-review summary
- `.cursor/plans/Phase3.10-logic-resonance-and-judge-prescreen.plan.md` — p310-5 marked complete
- 新增/删除的依赖包：无

**分支：** `feat/phase3.10.5-full-rerun-obs-fresh-label`（基于 `main` @ 3.10.4 merge）

## 2. 技术实现 (Implementation)

### Full-chain rerun (generation unchanged)

- Promoted all 10 news runs from `output/Eval/phase3.9/` → `output/Eval/phase3.10/` via `promote_phase39_to_phase310.py`
- Recipe: 3.9 decon + expansion + 12-persona salience + retrieve (A1 oracle parallel); **zero generation-side code changes**
- phase3.6–3.9 eval dirs left read-only / unmodified

### obs 01–04 fresh labels (v2 dual-axis)

- Rubric: `docs/eval-the-bet.md` §4 / `prompts/_shared/resonance_definition_v2.md`
- Observation runs: `01-grid-outage`, `02-corporate-layoff`, `03-election-upset`, `04-celebrity-scandal`
- **65** high-hit candidates labeled; **0 missing** in obs segment
- Holdout 05–10 left unlabeled (reserved for 3.10.7)
- All remarks tagged `v2 fresh`; no reference to phase3.9 legacy scores

### obs score distribution

| 分 | 数量 |
| --- | --- |
| 0 | 22 |
| 1 | 34 |
| 2 | 9 |

## 3. 本地验证结果 (Verification)

```text
# Promote + label pipeline completed 2026-06-09
# obs-fresh-labels-summary.md: 65 labeled, 0 missing
# batch-run-summary.json: 10 runs promoted from phase3.9
```

User approved obs fresh labels → cleared for 3.10.6 judge recalibration.

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **Promote ≠ regenerate** — artifacts are copied from phase3.9; candidate pools identical to 3.9 (by design: POV-off baseline).
- **Holdout discipline** — 05–10 human scores intentionally blank until post-freeze 3.10.7.
- **3.10.6 next** — judge recalibration on obs v2 labels + `judge≥1` threshold freeze verification.

**Go/No-Go:** User approved obs fresh labels → ready for **3.10.6**.
