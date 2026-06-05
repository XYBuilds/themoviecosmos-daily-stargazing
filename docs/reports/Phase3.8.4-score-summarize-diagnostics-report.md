# Phase 3.8.4 - 打分/分析双诊断 + 闸门口径 交付报告

## 1. 改动范围 (Scope)

- `scripts/score_eval_candidates.py` — 从 `retrieve.json` 注入 `neutral_hits` / `neutral_total` / `neutral_hit_rate` / `distinct_agents` / `quality_candidate` 至候选 markdown
- `scripts/summarize_eval.py` — 诊断①②（分桶 + 偏相关控 `max_similarity`）、闸门 2 改 `quality_vs_neutral_only`、A1-superset 占位
- `tests/test_summarize_eval.py` — phase38 PASS/FAIL fixture + 相似度分桶断言
- `tests/test_score_eval_candidates.py` — retrieve 字段注入单测
- `tests/eval_fixtures/phase38-dual-diagnostic-{pass,fail}/` — 双诊断闸门 fixture
- `.cursor/plans/Phase3.8-objective-extraction-neutral-channel.plan.md` — 3.8.4 标记 complete

## 2. 技术实现 (Implementation)

- **诊断①**：对已打分候选计算 `neutral_hit_rate ↔ 共振分` 的 Pearson 与偏相关（控制 `max_similarity`），并按 low/mid/high 相似度分桶报告。
- **诊断②**：将候选分为 `quality_candidate`（中性票 + ≥1 toned）与 `neutral_only`（仅中性票），比较结构/双重 2 分率；偏相关检验 `toned_convergence ↔ 共振分 | similarity`。
- **闸门 1**：不变（≥60% batch 至少 1 个 2 分）。
- **闸门 2（3.8）**：`compare_mode=quality_vs_neutral_only`；通过条件为诊断② `precision_lift_ok`（优质候选结构/双重 2 分率 > 中性-only）。
- **A1-superset**：JSON/stdout 输出 `a1_superset.status=pending`，待 3.8.7 并跑后由 3.8.8 填 verdict。
- **score_eval**：`_load_retrieve_meta` 扩展 `RetrieveDiagnostics`；`score_candidates_md` 写回诊断字段供 summarize 解析。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_summarize_eval tests.test_score_eval_candidates -v
Ran 23 tests in ~1s — OK
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 诊断①② 依赖候选 markdown 含 retrieve 注入字段；仅 `retrieve.json` 而无打分 markdown 时 summarize 不会进入 phase38 模式。
- A1-superset 闸仍为占位；删 A1 决策阻塞于 3.8.7–3.8.8。
- 小样本下偏相关可能为 `None`；GATE 解读须结合 3.8.7 留出集体量。
