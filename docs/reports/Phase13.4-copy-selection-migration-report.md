# Phase 13.4 · Copy Selection Migration Report

## 完成内容

- `selection.json` 新写入仅保存选择快照；重复选择幂等，改选只将已有发布包标为 `superseded`，不删除历史产物。
- 当前稿、人工正文编辑、重生成和去 AI 化稿均通过 `manifest.json` 的相对路径定位到 publication bundle。
- 旧 `selection.json.copies` 与旧 `daily_batch` 稿件继续以只读回退方式兼容。
- 增加发布包内文案路径、主视角指针保留、humanized 失效和 superseded 审计保留的回归覆盖。

## 验证

- `python -m pytest -q`
- `python -m pytest tests/test_publication_bundle.py tests/test_publication_copy_migration.py tests/test_review_panel_publish_adapter.py tests/test_review_panel_rewrite_adapter.py tests/test_review_panel_regenerate_adapter.py -q`