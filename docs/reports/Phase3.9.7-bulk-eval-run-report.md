# Phase 3.9.7 - 批量 run + 人工/judge 纵向打分 交付报告

## 1. 改动范围 (Scope)

- `output/Eval/phase3.9/high-hit-score-review.md` — 156 候选人工共振分（152 已填）+ judge 字段采信状态更新
- `output/Eval/phase3.9/llm-judge-scores.json` / `llm-judge-scores.md` — obs 校准重算（61 pairs）
- `.cursor/plans/Phase3.9-a1-oracle-per-persona-salience-three-bucket-eval.plan.md` — p39-7 complete

**分支：** `feat/phase3.9.7-bulk-eval-run` @ `bdde70f`

## 2. 技术实现 (Implementation)

### 人工分同步

- 数据源：`high-hit-score-review.md`（phase 3.9 统一 review SSOT；无 per-run `candidates.md`）
- `scripts/sync_review_scores_to_candidates.py` 对本 phase **不适用**（无 per-run candidates 文件）
- 解析结果：**152/156** 已填共振分；**4** 条空分（均在 `03-election-upset`：tmdb 10187, 64946, 878183, 91010）
- 分布：0 → 87，1 → 36，2 → 29

### Judge 校准（obs 01–04）

`python scripts/llm_judge.py --eval-dir output/Eval/phase3.9 --calibrate-only`

| 指标 | 重算后 | 阈值 |
| --- | --- | --- |
| n_pairs | 61 | ≥ 5 |
| exact_agreement | **0.639** | ≥ 0.60 |
| pearson_r | **0.743** | ≥ 0.50 |
| within_one | 1.000 | — |
| **trust_status** | **采信** | screening_only=false |

`--integrate-review` 已将采信状态写回 review 内联 judge 字段。

### 留出冻结

纪律记录：`output/Eval/phase3.9/holdout-freeze-discipline.md`（obs 调参 → 冻结阈值 → holdout 单次 judge）。

## 3. 本地验证结果 (Verification)

```text
python scripts/llm_judge.py --eval-dir output/Eval/phase3.9 --calibrate-only
# trust_status=采信 pairs=61 exact=0.639 pearson=0.743

python scripts/summarize_eval.py --dir output/Eval/phase3.9 --out output/Eval/phase3.9/gate-diagnostics.json
# 152 scored, 4 missing; batch 90% (9/10); GATE_PASS (mechanical Q2)
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **4 条未填分**：`03-election-upset` 低 pseudo 命中候选；不影响 obs 校准对数（61 pairs），但全批 GATE 覆盖率 97.4%
- **`summarize_eval` Q1 oracle**：脚本仍读 `retrieve.json` 内 `oracle_comparison`（本批为 null）；3.9.8 GATE 须用 `retrieve.json` + `a1-baseline-meta.json` 手算 Q1
- **下一 TODO**：3.9.8 书面 GATE（Q1/Q2/Q3 + obs/holdout 一致性）→ `[需人工验收]`
