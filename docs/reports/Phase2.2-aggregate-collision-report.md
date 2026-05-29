# Phase 2.2 - 候选聚合与撞车展示 交付报告

## 1. 改动范围 (Scope)

- `scripts/retrieve.py` — `candidates` 去重、`triggered_by` / `also_baseline`、`divergence`

## 2. 技术实现 (Implementation)

- 按 `tmdb_id` 聚合；`similarity` 取各 agent 命中中的 max
- `triggered_by` 仅收录 `role=creative` 的 agent；A1 命中写 `also_baseline=true`
- 撞车仅展示字段，不参与排序加权
- `divergence`：agent 查询向量两两余弦 + Top-K `tmdb_id` 集合 Jaccard

## 3. 本地验证结果 (Verification)

`output/phase2_retrieve.json`（8 candidates，4 agents × Top-2）：

- `triggered_by` 样例：`['A4']`（创作视角列表）
- 创作视角与基线分离逻辑在 `retrieve_from_agents` 聚合循环中验收

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 当前样本新闻下跨创作视角撞车较少；评测期再观察 `divergence` 与撞车率
