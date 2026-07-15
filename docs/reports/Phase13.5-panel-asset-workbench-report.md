# Phase 13.5 · 发布包视觉资产工作台报告

## 完成内容

- 顶栏将“生成草稿池”替换为显式“准备发布包”动作；选片仅写入 selection，不会发起草稿、海报或星球生成。
- 前端通过 `POST /api/prepare-publication` 与既有 `JobStore` 提交任务，同时轮询 `/api/job` 和 `/api/publication`，以 manifest 投影任务进度与草稿就绪状态。
- 在 pick/refine 工作台增加视觉资产栏：TMDB 海报（2:3）、Bloom ON 星球（1:1 透明棋盘格）、独立状态、下载和失败后的单项重试。
- 使用受限 `/api/publication-asset` URL 加载图片；前端不接收或拼接任意文件路径。
- 窄屏时资产栏先于文案区折叠为单列，保留现有草稿选型、合并、微调、去 AI 化和移动宽度预览流程。

## 验证

- `python -m pytest tests/test_review_panel_frontend_state.py`：5 passed。
- 本地浏览器烟测：已选候选进入 pick 后显示“准备发布包”和两张独立资产占位卡；未准备时未请求视觉资产。
- `python -m pytest tests/test_review_panel_frontend_state.py tests/test_publication_copy_migration.py tests/test_review_panel_serve.py tests/test_publication_adapter.py`：62 passed，21 failed。
  - 失败均位于未改动的 13.4 selection/copy 旧格式断言（`selection.copies`、旧 copy 路径与已移除的清理语义），不由本 TODO 的前端 diff 引入，留待 13.6 统一收敛。

## 变更边界

- 未自动发布到任何平台。
- 未触碰 publication manifest、路径模型或服务端 API 实现。
- 未执行真实 The Creator 发布包生成；该人工 Gate 属于 13.7。