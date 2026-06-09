# Phase 3.10.3 - summarize_eval D5 success criteria 交付报告

**分支**: `feat/phase3.10.3-summarize-eval-d5`（基于 `main` @ a3900dd，3.10.0/3.10.1 已合并）

## 1. 改动范围 (Scope)

- `scripts/summarize_eval.py` — 移除 Q1′ 删除闸；A1 降 `a1_reference` 只读参照；D5 两条成功标准（共振 + 工作流）；抽审样本按 `prescreen_audit_sample_rate` 回加权；`--calibration-json` CLI
- `tests/test_summarize_eval.py` — D5 / 回加权 / A1 参照单测
- `tests/eval_fixtures/phase310-prescreen-audit/`、`phase310-d5-workflow-pass/` — 新 fixture
- `.cursor/plans/Phase3.10-logic-resonance-and-judge-prescreen.plan.md` — p310-3 complete

`scripts/score_eval_candidates.py` 未改：judge 字段已由 `llm_judge.integrate_judge_into_review` 写入；抽审字段 `prescreen_audit_sampled` / `prescreen_audit_sample_rate` 由 3.10.4 预筛编排写入 review。

无新增依赖包。

## 2. 技术实现 (Implementation)

### D5 成功标准（ADR-0007 D5）

- **共振侧**：`combo` structural 2-rate **>** `pure_fact`（相似度分桶 + 可选 prescreen 回加权）；obs（01–04）/ holdout（05–10）lift 方向一致。
- **工作流侧**：judge 预筛减负率 ≥ 50%、reject 堆无 human=2、judge 校准 `trust_status=采信`（`--calibration-json`）。
- Phase38 路径闸门 compare_mode → `d5_success_criteria`；无 judge 字段时工作流 criterion 为 `pending` → `GATE_FAIL`（待 3.10.4+ 填数）。

### Q1′ / A1

- `q1_prime_a1_two_neutral_coverage` 保留为 `a1_reference.q1_prime_coverage` **只读诊断**。
- 删除 `a1_deletion_eligible`；stdout 不再输出 Q1′ 闸门行。

### 抽审回加权（ADR-0007 D4）

- `judge≥1` → 权重 1.0；`judge=0` 且 `prescreen_audit_sampled` → 权重 `1/sample_rate`；其余 reject 不进桶分母。
- `three_bucket.buckets_reweighted` + `q2_combo_lift_ok_reweighted` 可产出。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_summarize_eval -v
----------------------------------------------------------------------
Ran 17 tests in ~0.65s
OK
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **工作流闸 pending**：无 judge 分/校准 JSON 的批次必 `GATE_FAIL`（共振可过）；3.10.4 预筛编排 + 3.10.6 校准后才有完整 D5 通过路径。
- **legacy 键**：`a1_oracle` / `q1_prime` 别名保留供旧读者过渡。
- **3.10.4** 须在 review 写入 `prescreen_audit_sampled` / `prescreen_audit_sample_rate` 后回加权才在全链生效。
