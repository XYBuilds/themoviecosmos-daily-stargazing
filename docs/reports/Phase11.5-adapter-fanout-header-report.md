# Phase 11.5 - p11.5-adapter-fanout-header 交付报告

## 1. 改动范围 (Scope)
- `review_panel/publish_adapter.py`
- `review_panel/drafts_adapter.py`
- `tests/test_review_panel_publish_adapter.py`
- `tests/test_review_panel_drafts_adapter.py`
- `.cursor/plans/Phase11-deterministic-movie-header-projection.plan.md`

新增/删除依赖包：无。

## 2. 技术实现 (Implementation)
- 在 `publish_adapter` 增加 `_movie_header_for_candidate()` / `_attach_movie_header()`，让 C2 定稿在 adapter 层也能稳定复用 `scripts.compose.build_header_projection()` + `render_movie_header()` 生成的同一确定性抬头。
- 在 `drafts_adapter.run_fanout()` 对每份 persona 草稿补装同一抬头；`run_combine()` 的 B 路线也同步走同一装配边界，避免组合稿残留裸正文。
- 保持抬头来源只走候选投影，不复制一套数据访问逻辑；正文仍由 persona / publish 链路决定。
- 测试侧改为直接复用生产投影函数生成 expected header，避免手写标题与生产格式漂移。

## 3. 本地验证结果 (Verification)
- `py -m pytest tests/test_review_panel_publish_adapter.py::RunAdapterTests::test_writes_copy_md_with_body_and_links -q`
  - 通过，`1 passed in 8.38s`
- `py -m pytest tests/test_review_panel_drafts_adapter.py tests/test_review_panel_publish_adapter.py`
  - 通过，`30 passed in 27.25s`
- `py -m pytest tests/test_compose_publish.py`
  - 通过，`35 passed in 6.08s`

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- `publish_adapter` / `drafts_adapter` 现在都在 adapter 层再做一次抬头装配，和 `scripts.compose.run_publish()` 的产物形成双层防线；目前依靠“若已带同头则不重复 prepend”避免双抬头。
- `run_combine()` 的 B 路线仍是保守拼接策略，只解决抬头一致性，不处理正文风格融合质量。
- `drafts_adapter.py` 仍保留对 `publish_adapter` 内部 helper 的跨模块复用，后续可视需要再抽成更明确的共享工具函数。