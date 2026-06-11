# Phase 3.11.4 - 候选漏斗 + 池差通道分解 交付报告

## 1. 改动范围 (Scope)

- `scripts/retrieve.py` — ADR-0007 D8 四层漏斗：`dedupe_candidates_by_tmdb_id`、`sort_candidates_convergent`、`apply_candidate_funnel`；扩展撞车票（toned+focalized composition agents）；`compare_pool_diff_by_channel` / `pool_diff_by_channel_to_dict`；`retrieve_from_agents` 输出 `human_candidates` / `audit_pool` / `funnel`
- `scripts/lib/phase311_pretest.py` — `compare_pool_diff` 附带 `by_channel` 分解
- `tests/test_retrieve_funnel.py` — 去重、汇聚权重、预算上限、audit pool、池差通道分解、扩展撞车票
- `tests/test_retrieve_quality.py`、`tests/test_retrieve_neutral_collision.py` — `composition_agents` 措辞对齐
- `.cursor/plans/Phase3.11-pov-focalization-additive.plan.md` — 3.11.4 标 complete

## 2. 技术实现 (Implementation)

- **Layer 1 去重**：按 `tmdb_id` 合并 `hit_sources`，取 max similarity
- **Layer 2 汇聚排序**：`convergent_score = 100×通道数 + 10×persona 数 + similarity`；`quality_candidate` 优先；撞车票扩展为 neutral union + ≥1 toned/focalized
- **Layer 3–4 预算**：`human_budget`（默认 19）截断人工池；提供 `judge_scores` 时滤 `judge=0`，预算以下 `judge≥1` 进 `audit_pool`（不靠调高 judge 门槛控量）
- **A/B 池差**：`compare_pool_diff_by_channel` 对 net-new 按 neutral / toned / focalized provenance 分解

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_retrieve_funnel tests.test_retrieve_multi_pseudo tests.test_retrieve_quality tests.test_retrieve_neutral_collision tests.test_retrieve_a1_oracle tests.test_phase311_pretest -v
# Ran 43 tests — OK
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `candidates` 现为漏斗后 `human_candidates`（汇聚排序 + 预算），与旧版纯 similarity 排序顺序可能不同；`funnel.sorted_candidates` 在 `apply_candidate_funnel` 返回值中可拿全量排序池
- 检索时无 judge 分则 `audit_pool` 为空；评测链需在 judge 打分后二次调用 `apply_candidate_funnel(..., judge_scores=...)` 或后续编排脚本接线
- 全量 `python -m unittest discover` 在 main 上另有 3 个与 3.11.5 judge 并行相关的既有失败（非本 TODO 范围）
