# Phase 3.9.3 - 三桶度量 + 纯中性入打分池 交付报告

**分支**: `feat/phase3.9.3-three-bucket-metrics`（基于最新 `main`，3.9.0/3.9.1/3.9.2/3.9.5 已合并）

## 1. 改动范围 (Scope)

- `scripts/summarize_eval.py` — 三桶（pure_fact / pure_emotion / combo）、Q1 A1-oracle、Q2 combo vs pure_fact
- `scripts/score_eval_candidates.py` — 纯中性候选入 high-hit / 打分池
- `scripts/run_persona_batch.py` — `write_a1_parallel_baseline` 读 `a1_oracle.hit_tmdb_ids`
- `tests/test_summarize_eval.py`、`tests/test_score_eval_candidates.py`
- `tests/eval_fixtures/phase39-three-bucket/`、`tests/eval_fixtures/score_eval_review/neutral-only-batch/`
- `.cursor/plans/Phase3.9-a1-oracle-per-persona-salience-three-bucket-eval.plan.md` — p39-3 complete

无新增依赖包。

## 2. 技术实现 (Implementation)

### summarize_eval（ADR-0006 D4）

- **`toned_convergence`**：仅 `distinct_agents ≥ 1`（对齐 retrieve 的 toned 汇聚计数）；移除 `quality_candidate` 回退，避免 neutral-only 恒空。
- **三桶**：`is_pure_fact` / `is_pure_emotion` / `is_combo` + `eval_bucket()`；`three_bucket` 全局块含各桶 total/structural 2-rate 及 `similarity_bins`。
- **诊断② / Q2**：combo vs pure_fact（`q2_combo_lift_ok`）；闸门 compare_mode 改为 `combo_vs_pure_fact`。
- **Q1 A1-oracle**：从 run 目录 `retrieve.json` 的 `oracle_comparison` 或 `a1_oracle.hit_tmdb_ids`（回退 `a1-baseline-meta.json`）汇总 `q1_recall_superset_ok`。

### score_eval_candidates

- **`_eligible_for_scoring_pool`**：`pseudo命中分合计 ≥ 5` **或** `neutral_hits≥1` 且 `distinct_agents=0`（纯中性）进入 review / 打分池。

### run_persona_batch

- **`write_a1_parallel_baseline`**：优先 `retrieve_result.a1_oracle.hit_tmdb_ids`；A1-only oracle 路径下 `candidates` 为空时仍能写出命中集。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_summarize_eval tests.test_score_eval_candidates -v
----------------------------------------------------------------------
Ran 28 tests in ~1.2s
OK
```

要点：

- `neutral_only_scored > 0`（phase38 / phase39 fixtures）
- 三桶 structural 2-rate 与 similarity_bins 可产出
- Q1 superset 从 `retrieve.json` oracle_comparison 读取
- 纯中性 `total_score=1` 仍可进 high-hit review

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **Q1 质量对比**：`q1_quality_structural_2_rate_vs_a1` 仍为 placeholder，需 A1 命中行进入人工评分 review 后才能在 summarize 内自动对比 2 分率。
- **legacy 键**：`diagnostic_2` 保留 `quality_*` / `neutral_only_*` 别名，便于旧读者过渡。
- **3.9.4** LLM-judge 可消费 `three_bucket` / `a1_oracle` JSON 字段填 GATE_RESULT。
