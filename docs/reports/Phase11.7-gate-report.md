# Phase 11.7 - GATE 交付报告

## 1. 改动范围 (Scope)
- `scripts/movie_metadata.py`
- `scripts/compose.py`
- `review_panel/drafts_adapter.py`
- `prompts/compose_publish_xiaohongshu.md`
- `tests/test_compose_publish.py`
- `tests/test_review_panel_drafts_adapter.py`
- `tests/test_review_panel_publish_adapter.py`
- `.env.example`
- `.cursor/plans/Phase11-deterministic-movie-header-projection.plan.md`
- `docs/reports/Phase11.7-gate-report.md`
- 未新增第三方依赖；TMDB 调用使用标准库 `urllib`。

## 2. 技术实现 (Implementation)
- 新增 TMDB 中文译名 helper：优先读取 `TMDB_API_KEY`，请求 `language=zh-CN` 的 movie details；无 key、网络失败或返回非中文标题时统一降级为空串，保证 `zh_title` 可选、不打断主流程。
- `build_header_projection(..., zh_title_loader=...)` 保持可注入，便于测试 stub 中文译名与 DB 投影；`render_movie_header` 继续由确定性 header 生成，`体积` 仅使用 `vote_count` 并按 `floor(log10(vote_count))` 显示数量级上角标。
- `clean_publish_body` 和发布 prompt 共同收口正文：即使 LLM 误吐 title/director/片名/元信息行，也会被剥除；正文只保留内容，确定性 header 由代码拼装且只出现一次。
- `drafts_adapter` 扇出时从 `hit_sources` 补齐 persona hits，避免 `triggered_by` 截断导致 8 persona 扇出缩水。

## 3. 本地验证结果 (Verification)
- 单测回归：`py -m pytest tests/test_compose_publish.py tests/test_review_panel_drafts_adapter.py tests/test_review_panel_publish_adapter.py`
  - 结果：`exit_code 0`
- TMDB smoke：
  - `tmdb_id=157336` → `星际穿越`（成功）
  - `tmdb_id=142887` → 空串（正常降级，数据无中文译名）
- 另行验证：`tests/test_compose_publish.py` 覆盖了 header 只出现一次、LLM 误吐元信息行清理、`vote_count` 体积显示、TMDB 注入/降级。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- `TMDB_API_KEY` 目前是可选增强；若 TMDB 对某些条目没有中文 title，系统会降级为空，不影响主链路，但中文抬头仍可能缺少中译段。
- 真实网络 smoke 依赖 TMDB 在线服务与当前数据覆盖；若后续想降低线上波动，可再加轻量缓存，但本次保持最小实现，未引入额外状态文件。
- 本次已通过人工验收，但 `11.7` 在计划语义上仍是 GATE 关注点的收尾记录，后续 Phase 不应回退到 LLM 自写元信息。