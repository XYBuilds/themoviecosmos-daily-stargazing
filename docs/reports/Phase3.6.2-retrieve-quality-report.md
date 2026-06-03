# Phase 3.6.2 - retrieve 质量地板 + D1 优质标记 交付报告

## 1. 改动范围 (Scope)

- `scripts/retrieve.py` — `--quality-floor` CLI（默认 0.40）、`quality_candidate` / `distinct_agents` / `quality_reason` 候选字段、广度优先 containment
- `tests/test_retrieve_quality.py` — 新建：地板计数、A1 平权、containment 优先级、集成 mock
- `tests/test_retrieve_multi_pseudo.py` — 断言新 quality 字段；containment fixture 补 `quality_candidate`
- 新增/删除的依赖包：无

## 2. 技术实现 (Implementation)

- **D1 优质判据**：对每个聚合候选，统计 `hit_sources` 中 `similarity >= quality_floor` 的不同 `agent_id` 数为 `distinct_agents`；`>= 2` 时 `quality_candidate=true`（A1 与创作 agent 同权计入）。
- **质量地板**：CLI `--quality-floor`（默认 `0.40`），写入 `meta.quality_floor`；低于地板的 hit 不参与 `distinct_agents`，防止注水 pseudo 伪造假多 agent。
- **广度优先 containment**：`_apply_containment` 先保留全部 `quality_candidate=true`，再按相似度填满 `max_candidates`。
- **`quality_reason`**：人类可读说明（如 `distinct_agents=2 (>=2): A2,A1` 或 `<2 required`）。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_retrieve_multi_pseudo tests.test_retrieve_quality -v
Ran 11 tests in 0.098s
OK
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `run_eval.py` 尚未显式传 `--quality-floor`；使用库默认值 0.40，3.6.5 可按实测调参。
- `triggered_by` / `also_baseline` 展示语义未改（3.6.3 负责 candidates 展示）；D1 字段已与展示解耦。
- 分支基于 `main` @ `46c112b`（PR #15 / 3.6.1 已合并）。
