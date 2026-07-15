# Phase 13.3 · 发布包编排与 API 报告

- **TODO**: `p13.3-publication-orchestration-api`
- **状态**: complete
- **分支**: `feat/p13.3-publication-orchestration-api`

## 交付

- 新增 `review_panel/publication_adapter.py`：初始化/复用 manifest 后，并行准备草稿池、TMDB 海报和 Bloom ON 星球图；每项独立记录 `running`、`ready` 或 `failed`，支持 `--targets` 单项重试。
- `review_panel/serve.py` 新增异步 `prepare-publication` 与 `retry-publication-artifact` 路由，复用既有 `JobStore`；服务层仅通过子进程触发编排器，不直接耦合 LLM 或渲染实现。
- 新增 manifest 查询与枚举式视觉资产端点。资产只能从 manifest 注册的 bundle 内相对路径解析，拒绝任意路径和目录穿越。
- 新增 `tests/test_publication_adapter.py`，覆盖并行部分失败、单项重试、异步 job 提交，以及受限资产读取。

## 验证

```text
python -m pytest tests/test_publication_adapter.py tests/test_publication_bundle.py tests/test_publication_assets.py tests/test_review_panel_serve.py
83 passed in 14.60s
```