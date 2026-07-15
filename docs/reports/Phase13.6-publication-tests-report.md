# Phase 13.6 · publication 回归测试报告

## 交付

- 对齐 `test_review_panel_serve.py` 与 Phase 13 的 SSOT：新写入 selection 仅保存选择；当前稿、humanized 稿和草稿指针均断言写入 bundle `manifest.json`。
- 覆盖显式准备、同片幂等重选、改选 superseded 且保留旧包、单项 retry 参数约束、资产端点限制、legacy copy 只读回退与前端资产工作台状态。
- 测试 fixture 按每个 selection 的时间戳隔离共享 `output/publications` 投影，避免 Windows 临时目录同级 publications 工作区污染测试结果。
- canonical plan 已将 `p13.6-publication-tests` 标记为 `complete`。

## 验证

```text
python -m pytest tests/test_publication_bundle.py tests/test_publication_adapter.py tests/test_poster_downloader.py tests/test_publication_assets.py tests/test_publication_copy_migration.py tests/test_review_panel_serve.py tests/test_review_panel_frontend_state.py
100 passed

python -m pytest
586 passed, 1 skipped
```

已检查最近编辑的测试文件，未发现新增静态诊断问题。