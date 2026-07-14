# Phase 13.1 · publication bundle 领域模型与 ADR 报告

## 交付

- 新增 `review_panel/publication_bundle.py`，集中管理 publication bundle ID、路径映射、schema-v1 manifest、状态归并、原子读写和 supersede。
- 新增 `docs/adr/0021-publication-bundle-lifecycle.md`，固化 selection/manifest SSOT 分工、显式准备、资产边界与非破坏性审计语义。
- 新增 `tests/test_publication_bundle.py`，覆盖安全 slug、相对路径、schema 与路径快速失败、状态归并、原子更新和 supersede。
- canonical plan 已将 `p13.1-publication-domain-and-adr` 标记为 `complete`。

## 验证

```text
python -m pytest tests/test_publication_bundle.py
6 passed
```

`review_panel/publication_bundle.py` 与对应测试文件的静态诊断无新增问题。