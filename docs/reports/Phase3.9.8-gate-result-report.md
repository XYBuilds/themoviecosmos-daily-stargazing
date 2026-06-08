# Phase 3.9.8 - GATE 结论（Q1′/Q2/Q3）交付报告

## 1. 改动范围 (Scope)

- `output/Eval/phase3.9/GATE_RESULT.md` — 书面 GATE（Q1′ 主闸、Q2/Q3、闸门 1、obs/holdout、产品 **no-go**）
- `output/Eval/phase3.9/gate-diagnostics.json` — `summarize_eval` 批次诊断（含 Q1′ 机械字段）
- `scripts/summarize_eval.py` — Q1′（A1_two ⊆ neutral n1 union）与 legacy 诊断分离
- `tests/test_summarize_eval.py` + `tests/eval_fixtures/phase39-q1-prime*` — Q1′ pass/fail fixture
- `CONTEXT.md`、`docs/adr/0006-*.md` — Q1′ 口径与 ADR D5 对齐（prior commit）
- `.cursor/plans/Phase3.9-a1-oracle-per-persona-salience-three-bucket-eval.plan.md` — p39-8 `complete`；p39-9 `cancelled`（GATE no-go）
- `docs/reports/Phase3.9.8-gate-result-report.md` — 本报告

**分支：** `feat/phase3.9.8-gate-result` @ `b4b6cf6`（及本交付 commit）

**人工验收：** 用户 approve GATE 裁决 **no-go**（2026-06-09）

## 2. 技术实现 (Implementation)

### Q1′（gate · ADR-0006 D5）

- **A1_two** = A1 命中 ∩ 人工共振分 = 2；**N** = 12 persona 的 neutral `n1` 命中 union（per run）。
- 批次：所有 `|A1_two|>0` 的 run 须 pass（`A1_two ⊆ N`）。
- **结果：FAIL** — 6/8 非 vacuous runs pass；全局 2 miss（`02-corporate-layoff` / Bounty Killer；`06-tech-monopoly` / The Clearstream Affair）；`a1_deletion_eligible = false`。
- Legacy superset / neutral 2-rate vs A1 仅诊断，不参与 gate。

### Q2 / Q3 / 闸门 1

- **Q2：** `summarize_eval` 机械 **PASS**（combo structural 2-rate > pure_fact），但 pure_fact 已打分 n=4、holdout combo 18% vs obs 41%，产品侧标为 **弱/效力不足**。
- **Q3：** 条件 **PASS**（无「纯情绪拖累组合」的强反证）。
- **闸门 1：** **PASS**（90% batch runs ≥1 个 2 分候选）。

### 产品裁决（D5）

- **GATE no-go** — 不满足 Q1′&Q2 双成立；不进入 3.9.9（ADR accepted / A1 删除）。
- 下一动作（plan）：回到 3.9.1/3.9.6 salience/契约迭代或 **D6 plan B**；A1 保留并跑。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_summarize_eval -v
# Q1′ pass/fail fixtures OK

python scripts/summarize_eval.py --dir output/Eval/phase3.9 --out output/Eval/phase3.9/gate-diagnostics.json
# 152 scored; mechanical q2_combo_lift_ok; Q1′ batch fail per GATE_RESULT.md
```

证据 SSOT：`output/Eval/phase3.9/GATE_RESULT.md`、`high-hit-score-review.md`（152/156 scored）。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **3.9.9 skipped：** `p39-9` 在 plan 中标记 `cancelled`（GATE no-go）；ADR-0006 保持 `proposed`；不删 A1。
- **机械 `GATE_PASS` vs 产品 no-go：** `summarize_eval` 仍可能报 Q2+batch 机械通过；书面 GATE 与人工验收以 Q1′ fail + Q2 小样本为准。
- **Phase 4** 仍 gated；需新计划或 plan B 后再赌 GATE。