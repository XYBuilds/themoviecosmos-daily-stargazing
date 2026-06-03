# Phase 3.6.3 - candidates 展示与命中分二级 交付报告

## 1. 改动范围 (Scope)

- `scripts/run_eval.py` — 候选 heading/字段/排序
- `scripts/score_eval_candidates.py` — 二级审阅键注释与双 bracket heading 解析
- `tests/test_run_eval_candidates.py` — 新增单测
- `.cursor/plans/Phase3.6-resonance-quality-gate.plan.md` — 3.6.3 标记 complete

无新增依赖包。

**分支**：`feat/phase3.6.3-candidates-display`（基于 `origin/main` @ PR #18 合并后，含 3.6.2 + 3.6.4）

## 2. 技术实现 (Implementation)

### run_eval.py

- **`_candidate_heading`**：从 `hit_sources` 列出全部命中 agent（含 A1）；优质候选追加 `[优质·多agent]`；移除 `[baseline only]` / 仅 creative 语义。
- **`_format_candidate_block`**：新增 `- **优质候选**`、`- **quality_candidate**`（供 `summarize_eval` 解析）、`- **distinct_agents**`。
- **`_sort_candidates_for_display`**：优质优先 → 组内按 fragment 计数 pseudo 命中分合计（二级）→ 相似度 → tmdb_id。

### score_eval_candidates.py

- 模块与 high-hit review 文案：pseudo命中分 明确为**二级审阅键**，非 D1 质量闸。
- `_agents_from_heading` / `_title_from_heading`：兼容 `[A2, A1] [优质·多agent]` 双 bracket。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_run_eval_candidates tests.test_retrieve_quality -v
# Ran 14 tests — OK
```

未执行 `run_eval` / `output/Eval` 全链路（按任务要求跳过 Eval 跑批）。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **3.6.5** 重跑 N=10 时须 `--out output/Eval/phase3.6/{run_id}`；本 todo 仅改展示契约。
- heading 中 agent 列表来自全部 `hit_sources`，与 D1 `distinct_agents`（过质量地板）可能不一致；闸门以 `- **quality_candidate**` 字段为准（3.6.4 已落地）。
- `also_baseline` 字段仍保留在块内，供对照/迁移；展示语义已不再依赖它。
