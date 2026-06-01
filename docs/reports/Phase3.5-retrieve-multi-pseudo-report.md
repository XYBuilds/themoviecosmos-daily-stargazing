# Phase 3.5.4 - retrieve 多路召回聚合 交付报告

## 1. 改动范围 (Scope)

- `scripts/retrieve.py` — 遍历 `agents[].pseudos[]`（legacy 回退 `text`）、每段 Top-2、`tmdb_id` 聚合、`hit_sources`、containment（默认 19）、`meta` 统计
- `scripts/run_eval.py` — `candidates.md` 展示命中视角/碎片；agent 文档按 pseudo 展示召回
- `tests/test_retrieve_multi_pseudo.py` — 查询展开、containment、聚合与 A1 撞车规则单测
- `.cursor/plans/Phase3.5-pivot-reality-deconstruction.plan.md` — 3.5.4 标 complete

**分支继承：** `feat/phase3.5-retrieve-multi-pseudo` ← `feat/phase3.5-rewrite-agents`（PR #11，基于 `feat/phase3.5-deconstruct-agent`）

**新增依赖：** 无

## 2. 技术实现 (Implementation)

- **`_expand_retrieval_queries`**：每 agent 每段 pseudo 一条查询；`errors[]` 跳过；无 `pseudos` 时用 `text` + `pseudo_id=legacy`
- **召回**：`Overview: {pseudo}` → 余弦 Top-K（默认 2，ADR-0001）
- **聚合**：按 `tmdb_id` 去重；`hit_sources[]` 记录 `{agent_id, pseudo_id, fragments, similarity}`；`triggered_by` 仅 creative（**不含 A1**），`also_baseline` 标基线命中
- **containment**：去重后按 `similarity` 排序，截断至 `--max-candidates`（默认 19，对齐 plan ~15–19/条）
- **输出**：`per_agent[].pseudos[]` 每段独立 `hits`；顶层 `meta` 含 `query_count` / `raw_hit_count` / `candidate_count`
- **发散度探针**：仍按 agent 首段 pseudo 的查询向量 + 各 agent Top-K 并集 Jaccard

## 3. 本地验证结果 (Verification)

```powershell
python -m unittest tests.test_retrieve_multi_pseudo -v
# Ran 5 tests in 0.089s — OK

python scripts/retrieve.py --agents-json output/test-p35-agents-all-india.json --out output/test-p35-retrieve-india.json
# queries=6, raw_hits=12, candidates=12 (≤19)

python scripts/retrieve.py --agents-json output/phase1_agents.json --out output/test-legacy-retrieve.json
# queries=4 (legacy), candidates=8
```

- 样例 `hit_sources`：`A7/p1` → `fragments=[why-0, how-0, result-0, result-1]`
- `triggered_by` 不含 A1；仅基线命中走 `also_baseline`

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **3.5.5** 依赖本契约：`candidates.md` 已展示 `hit_sources`，`共振类型` 占位与 `summarize_eval` 解析待 3.5.5 实现
- **divergence** 仍用每 agent 首段 pseudo 向量，多 pseudo 下仅为探针近似
- 全量 4×3×3 成功时 raw 24 路；containment 19 可能裁掉尾部相似度候选，需在 The Bet 重跑时观察总编负荷
- `run_eval` agent 文档标题仍写「3 pseudos」，与部分 agent 失败/空段并存时以实际 `pseudos` 为准
