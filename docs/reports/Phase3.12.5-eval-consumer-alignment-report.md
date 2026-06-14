# Phase 3.12.5 - 编排入口与 eval 消费层对齐 交付报告

## 1. 改动范围 (Scope)

eval-consumer 侧（本 commit，3.12.4 原子块的账面第二部分）：

- `scripts/score_eval_candidates.py`：`HitScore.channel_role`→`search_unit_kind`；`RetrieveDiagnostics` 字段 `neutral_hits/neutral_total/neutral_hit_rate/distinct_agents`→`objective_hits/persona_count`；`_is_pure_neutral_candidate`→`_is_objective_only_candidate`；diagnostic 命中由 surface/event fragment bundle 判定；`_AUTO_SCORE_TOP_LEVEL_FIELDS` 保留旧字段名仅用于剥离历史产物。
- `scripts/summarize_eval.py`：删除 4 个 channel 输入正则、`CandidateScore` 4 个 channel 字段及派生属性、`_uses_phase38_gate`、整条 phase38/ADR-0006/0008 诊断臂（_pearson 之外的 _partial_correlation/three_bucket/d5_success/a1_oracle_comparison 等死代码），`_format_stdout` 删 `phase38_gate` 分支与 `d5_success_criteria` 死分支；保留 `_pearson`（judge calibration 通用统计依赖）、persona_gate / multi_vs_single 主框架。
- `scripts/run_eval.py`：移除 `distinct_agents` 回退。
- `scripts/filter_review_candidates.py`：移除从 summarize_eval 导入的 3 个已删正则及死函数 `_has_neutral_hits`，过滤口径收敛为 heading/hit-line agent 计数。
- `scripts/audit_phase38_pilot.py`：删除（依赖已删的 reality-expanded.json + neutral channel，ADR-0009 下无法运行；仅历史报告引用，无代码/测试依赖）。
- `tests/test_score_eval_candidates.py`、`tests/test_summarize_eval.py`：改写为 ADR-0009 口径，删除 phase38/three_bucket/D5/q1_prime 死机制用例。

无新增/删除依赖包。

## 2. 技术实现 (Implementation)

- 命名口径统一到 ADR-0009：objective_union / persona_count / objective_hits / search_unit_kind。
- summarize_eval 的 GATE 主框架（persona_vs_baseline + multi_vs_single）channel-independent，整体保留；仅裁掉由 `_uses_phase38_gate` 驱动的 channel 诊断臂。
- `calibration` 入参保留为 no-op shim，确保 llm_judge 等调用方签名兼容。

## 3. 本地验证结果 (Verification)

- 相关模块单独验证：`tests.test_summarize_eval` + `tests.test_score_eval_candidates` + `tests.test_pov_transform_label` → 37 tests OK。
- 全量回归：`python -m unittest discover -s tests -p "test*.py"` → Ran 194 tests, OK (skipped=1)。
- 5 个 eval-consumer 脚本 grep 确认无残留 channel 诊断符号（`_distinct_agents_in_hits` 为局部 agent 计数助手、`_AUTO_SCORE_TOP_LEVEL_FIELDS` 旧字段名仅作历史产物剥离，均为合法保留）；lint clean。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 3.12.4 + 3.12.5 为同一原子块，分两次 commit + 两份报告记账；本分支 `feat/phase3.12.5-eval-consumer-alignment` 堆叠于 `feat/phase3.12.4-retrieve-channel-cleanup`。
- GATE 等价性对照（3.11.8 基线 vs ADR-0009 full_both 口径）在 3.12.6 人工验收门重建运行，本 commit 不含运行结果。
- 整个 3.12.2~3.12.5 bundle 仅在 3.12.6 人工验收通过后才合并入 main（需人工验收）。