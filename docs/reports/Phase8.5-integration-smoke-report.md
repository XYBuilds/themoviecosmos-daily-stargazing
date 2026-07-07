# Phase 8.5 - 集成冒烟测试 交付报告

## 1. 改动范围 (Scope)
- `.cursor/plans/Phase8-review-panel.plan.md`
  - 将 `p8.5-integration-smoke` 状态从 `todo` 标记为 `complete`。
- `docs/reports/Phase8.5-integration-smoke-report.md`
  - 新增本交付报告。

新增/删除的依赖包：无。

说明：本 TODO 是集成冒烟与人工验收节点，不引入源码改动。运行过程中产生的 `selection.json` 与 `_copy.md` 位于 `output/`，该目录已 gitignore，不纳入提交。

## 2. 技术实现 (Implementation)
- 启动本地 review panel，基于 `output/daily_batch/2026-07-06/` 的真实日批数据完成端到端审核流程。
- 验证链路：
  1. `/api/dates` 加载可用日期。
  2. `/api/data?date=2026-07-06` 聚合并渲染 panel 数据。
  3. 前端选择单个 candidate，`/api/select` 写入 `selection.json`。
  4. 点击「写推文」，`/api/publish` 读取 selection 并调用 `review_panel/publish_adapter.py`。
  5. `publish_adapter.py` 调用 `scripts.compose.run_publish`，产出 `{slug}_copy.md`。
- 本次人工验收选中：
  - news slug：`10-overseas-education-project-for-women-and`
  - candidate：`Rule Breakers`
  - tmdb_id：`1379520`

## 3. 本地验证结果 (Verification)
- 自动端到端冒烟曾通过：
  - dates → data → select → `selection.json`
  - 重复选择幂等验证
  - 真实 LLM publish 生成 `_copy.md`
- 人工浏览器验收已通过，用户输入 `approve`。
- 本次实际产物：

```text
output/daily_batch/2026-07-06/10-overseas-education-project-for-women-and_copy.md
```

对应 `selection.json` 状态：

```json
{
  "date": "2026-07-06",
  "selected": {
    "news_slug": "10-overseas-education-project-for-women-and",
    "tmdb_id": "1379520",
    "title": "Rule Breakers"
  },
  "published": true
}
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- `output/` 下的 smoke 产物用于人工验收与复现，不纳入 git。
- 8.5 分支在收尾前已快进到最新 `main`，因此本次验收覆盖 8.6 已合入的最终 review panel UI/数据口径。
- 历史日期的 `news_title` 中译依赖 `briefing.zh.translations.json` 是否已包含 `news_title` 分组；缺失时前端按设计回退英文。