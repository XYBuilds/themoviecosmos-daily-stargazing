# Phase 9.1 · G8 面板改选不清旧稿 bugfix — 交付报告

## 改动范围（Scope）

- `review_panel/serve.py`：`handle_select` 变体 A——改选时删除遗留 `{slug}_copy.md`；新增 `_delete_copy_if_exists` 助手。
- `tests/test_review_panel_serve.py`：新增 `SelectDeletesStaleCopyTests`（3 例）；顺带修 `_make_batch` fixture（补 judge scores）修复预存在的 `DataRouteTests` 失败。

依赖：无（独立于主线，Phase 9 首步）。分支 `feat/phase9.1-panel-stale-copy-fix` 从最新 `main` 检出。

## 技术实现（Implementation）

**Bug**：`handle_select` 整份覆盖 selection.json 并重置 `published:false / copy_path:null`，但不删上一次选片留下的 `{slug}_copy.md`，破坏「`selection.copy_path=null` ⇔ 磁盘无对应 `_copy.md`」不变量。改选到另一条新闻时，旧稿（如 Rule Breakers `10-…_copy.md`）成为孤儿，与新选片（如 The Girl）对不上。

**修复（变体 A）**：写入新 selection 前，删两处（均「存在才删」，幂等）：
1. **上一份 selection 指向的旧 slug 稿**——通过 `read_selection` 读旧 selection 取 `selected.news_slug`，删其 `_copy.md`。这是跨新闻改选场景的孤儿稿，是本 bug 的核心。
2. **本次 slug 稿**——重复选同片时强制重新 publish（稿可再生，安全），对齐 plan「每次 select 都删」。

删除逻辑收敛在 `_delete_copy_if_exists(path) -> bool`，与 `write_selection` 同层。未改动 `handle_publish`/`route`，无传输层改动。

## 本地验证结果（Verification）

```
python -m pytest tests/test_review_panel_serve.py -q
14 passed in 4.62s
```

- `test_reselect_other_slug_deletes_previous_orphan_copy`：选 09-slug→模拟出稿→改选 10-slug，旧 `09-slug_copy.md` 被删、selection 切到 10-slug 且 `copy_path=None`。✅
- `test_reselect_same_slug_deletes_its_copy`：重复选同片，其稿被删（强制重新 publish）。✅
- `test_select_without_existing_copy_is_idempotent`：无旧稿时 select 返回 200，不报错。✅
- 预存在失败 `DataRouteTests::test_returns_panel_dict_with_news_items` 随 fixture 修复转绿。

## 潜在影响或技术债（Technical Debt & Caveats）

- **fixture 修复的性质**：`build_data._join_judge_scores` 按 briefing 口径过滤 `judge_score∈{None,0}` 的候选是**有意行为**；原 serve 测试 fixture 缺 judge scores 属测试侧遗漏，本次补齐（与 `test_review_panel_publish_adapter.py` 的 `_write_judge_scores` 对齐），非改产品逻辑。
- **单选模型假设**：selection.json 每日仅一条选择，故只需清「上一份 + 本次」两处稿。若未来支持多选并存，删除策略需重估。
- **不回溯历史**：2026-07-06 遗留态已手工归位（Rule Breakers/published:true），本 todo 只修复发机制，不动历史文件（对齐 plan 注）。
