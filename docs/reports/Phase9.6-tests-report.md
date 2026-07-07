# Phase 9.6 · 更新测试过绿 — 交付报告

## 改动范围（Scope）

- `tests/test_compose_decision_card.py`：`_DETAIL` 加 `production_countries`，断言其出现在决策卡投影。
- `tests/test_copywriter_review.py`：移除 8 个测「旧审核稿契约」的死测试，保留 17 个仍有效的测试。
- （9.4/9.5 已在各自 todo 内更新 `test_compose_publish.py` / `test_review_panel_publish_adapter.py`；9.1 已更新 `test_review_panel_serve.py`。）

**分支继承**：`feat/phase9.6-tests` 从 `feat/phase9.5-downstream-adapter` 检出（未合并、PR #112）。链：9.1→…→9.6。

## 技术实现（Implementation）

- **决策卡 production_countries 断言（D6）**：`test_prompt_candidate_block_uses_db_projection_and_judge_kernel` 增 `production_countries: …` 断言，锁定「C1 决策卡也带该列」的无害透传。
- **删死测试（用户决定 ②(c) 的忠实执行）**：跑全套 pytest 暴露 8 个失败，**全部**在 `test_copywriter_review.py`，且用 `origin/main` 的 `compose.py` 对真实 DB 跑**同样 8 个失败**——即先于 Phase 9 就红。根因：这些测试断言 ADR-0012 决策卡重构后**已移除的**旧 C1「审核稿」契约（`ReviewCopy.copy_text` / `.director`、`row["card"]`、`# 审核稿候选`、`### 《片名》(年) | headline`、`电影信息: 待补 | 年 | genres`）。
  - **未整文件删除的理由**：该文件是**混合体**——除 8 个死测试外，另有 17 个仍有效测试，且是 `representative_persona_semantic` / `split_into_paragraphs` / `map_paragraphs_to_candidates` / `load_judge_scores` / `filter_candidates_by_judge` / `parse_card_fields`(经 run_review) 这 6 个 live 函数的**唯一覆盖**（grep 确认无其它测试文件覆盖）。option (c) 的前置条件「若确认它已被 test_compose_decision_card.py 取代」**不成立**，故只删死契约测试、保留 live 覆盖。决策卡投影/渲染/payload 形态由 `test_compose_decision_card.py` 覆盖。

## 本地验证结果（Verification）

```
python -m pytest tests/test_copywriter_review.py -q     → 17 passed
python -m pytest <Phase-9 四文件> -q                    → 43 passed
python -m pytest -q                                     → 384 passed, 1 skipped, 0 failed (219s)
```

- 全套 pytest 绿；新增契约（headline+body、--platform、归属行「」、publish system message、production_countries、G8 删旧 copy）均有断言覆盖。✅
- 删死测试前后：393 test items（385 pass + 8 fail）→ 385 items（384 pass + 1 skip）；差额恰为移除的 8 个死测试。✅

## 潜在影响或技术债（Technical Debt & Caveats）

- **`test_copywriter_review.py` 命名**：文件名仍带「copywriter」历史包袱，实测的是 compose C1 辅助函数；未改名以缩小 diff，日后可随手更名。
- **`parse_card_fields` 直接覆盖变弱**：删死测试后其仅经 `run_review` 间接被 `test_compose_decision_card.py` 触达；若日后单独维护该解析器，建议补直接单测。
- **death-test 根因是 ADR-0012 重构遗留**，非本 Phase 引入；本 todo 顺带清理，使全套恢复绿。
