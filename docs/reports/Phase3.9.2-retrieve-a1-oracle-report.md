# Phase 3.9.2 - retrieve A1 held-out oracle 交付报告

**分支**: `feat/phase3.9.2-retrieve-a1-oracle`（继承自 `fea3cc2` / Phase 3.9.0，main 尚未合并 3.9.0）

## 1. 改动范围 (Scope)

- `scripts/retrieve.py` — A1/baseline 查询拆至 held-out oracle 路径
- `tests/test_retrieve_a1_oracle.py` — 新增 oracle 隔离与 superset 对照单测
- `.cursor/plans/Phase3.9-a1-oracle-per-persona-salience-three-bucket-eval.plan.md` — p39-2 标 complete

无新增依赖包。

## 2. 技术实现 (Implementation)

按 ADR-0006 D1，`retrieve_from_agents` 将查询分为 **judge**（neutral/toned persona）与 **oracle**（A1 / `channel_role=baseline`）两路：

| 输出键 | 内容 |
| --- | --- |
| `candidates` / `per_agent` / `divergence` | 仅 judge 路径；无 A1 `hit_sources`、`triggered_by`、`also_baseline` |
| `a1_oracle` | `role=held_out_oracle`、`per_agent`、`hit_tmdb_ids`、`meta` |
| `oracle_comparison` | A1 vs 中性 union 的 superset 对照（`neutral_union_superset_of_a1_hits`、shared/a1_only/neutral_only） |
| `meta` | 新增 `oracle_query_count` / `judge_query_count` |

内部 `_run_query_batch(..., aggregate_candidates=False)` 供 oracle 路只编码命中、不写候选池。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_retrieve_multi_pseudo tests.test_retrieve_quality tests.test_retrieve_neutral_collision tests.test_retrieve_a1_oracle -v
----------------------------------------------------------------------
Ran 22 tests in 0.059s
OK
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **`write_a1_parallel_baseline`**（`run_persona_batch.py`）仍从 `candidates` 取 `a1_hit_tmdb_ids`；A1-only 检索后 `candidates` 为空，应在后续任务改为读 `a1_oracle.hit_tmdb_ids`（建议 3.9.3 或 batch 小修）。
- **3.9.3** 可消费 `oracle_comparison` 填 Q1 口径；`summarize_eval` 的 `also_baseline` 字段在 persona retrieve 路径上将恒为 `false`。
- 分支基于 Phase 3.9.0 提交，待 3.9.0 合并 main 后后续 Phase 应从最新 main 检出。
