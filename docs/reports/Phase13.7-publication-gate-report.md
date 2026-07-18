# Phase 13.7 · The Creator 发布包人工 Gate 报告

## 验收结论

- 人工结论：**Go**。
- Gate 对象：`2026-07-06 / 05-ai-poses-hiroshima-style-threat-to-humanity / The Creator / TMDB 670292`。
- 最终发布包：`output/publications/2026-07-06/670292-the-creator/`。
- `manifest.json` 最终状态为 `ready`；canonical plan 中 `p13.7-publication-gate` 已标记为 `complete`。

## 发布包结果

| 项目 | 结果 |
| --- | --- |
| 草稿池 | `ready`，Panel 可继续选型与微调 |
| 小红书当前稿 | `ready`，最终 `selected_draft_id` 为 `混合视角` |
| TMDB 海报 | `assets/poster-original.jpg`，Panel 预览与下载端点均返回 HTTP 200 |
| Bloom ON 星球 | `assets/planet.png`，3000×3000 RGBA PNG，透明通道验证通过 |
| 渲染元数据 | `assets/planet.png.render.json`，`data_version=2026.07.17.daily.112`、`bloom=on` |

星球渲染使用受信任的 Nightly 产物离线覆盖文件 `MOVIE_COSMOS_GALAXY_DATA_FILE`。原因是 R2 对象虽恢复可用，但响应未提供本地 Vite 读取所需的 CORS 头，且 Chronicle 仓库内置数据仍停留在旧版本。覆盖文件在使用前已完成 gzip 与数据校验；未修改 Daily Stargazing 的 `.env`，也未修改 Chronicle 配置或源码。

## 人工与故障恢复验收

- 选片只更新 selection，不触发草稿、海报或星球生成；点击“准备发布包”后才启动三个独立任务。
- Panel 左栏正确展示 2:3 海报和透明背景 1:1 星球；右侧选型、微调与去 AI 化操作按既有状态机工作。
- 海报和星球资产端点均可读取；Panel 发起的 `planet` 单项重试成功完成。
- 单项重试前后草稿池与海报哈希未变化，证明重试没有扩散到已完成 artifact。
- 改选时旧包保留并标记 `superseded`；重新选回 The Creator 后，旧包重新激活并按当前 selection 归并，不发生资产错配。
- 用户完成目视检查后明确回复 `go`。

## Gate 中修复的边界问题

- `drafts_adapter` 正确接收并转发 `--batch-root`。
- `publication_adapter.py` 可通过脚本路径直接启动，不再依赖调用方预置 Python import 路径。
- 重新选回旧电影时会重新激活并归并已有 manifest，不再永久停留在 `superseded`。
- 发布重试按稳定电影身份比较 selection，不把 `selected_at` 变化误判为选片错配。
- 星球渲染器从 Chronicle CLI stdout 的最后一个非空 JSON 行读取结果，可容忍 Vite/浏览器日志，同时保留路径、TMDB ID、PNG 和 metadata 校验。

## 自动验证

```text
python -m pytest tests/test_planet_renderer.py tests/test_publication_adapter.py tests/test_review_panel_serve.py tests/test_publication_bundle.py tests/test_review_panel_drafts_adapter.py
118 passed
```

一次更宽的 `python -m pytest` 在约 74% 处停滞于既有 `test_review_panel_publish_adapter.py`，已主动停止，因此本报告不把全量测试记为通过。Phase 13.7 以覆盖本次真实 Gate 修复边界的 118 项定向回归作为自动化证据。

未新增第三方依赖。