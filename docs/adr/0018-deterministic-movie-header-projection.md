# Deterministic movie header projection

**Status**: accepted

> 本 ADR 记录 Phase 11 把电影抬头行从 LLM 收回、改为代码确定性投影的边界与理由。它承接 [ADR-0012](0012-compose-responsibility-split-and-db-fullcolumn-lookup.md)、[ADR-0013](0013-image-equality-creative-tone.md)、[ADR-0015](0015-publish-platformization-and-element-checklist.md)、[ADR-0017](0017-persona-perspective-c2-draft-pool.md)，并明确：中文译名是独立增强层，留给 TODO-B；本 Phase 不引入 TMDB 在线依赖。

## Background

现有发布稿链路里，抬头行曾经和正文一起交给 LLM 处理。问题不在“写得像不像”，而在**字段选择本身不稳定**：同一部电影，LLM 会在 `title` 与 `original_title` 之间自由切换，导致同片跨草稿抬头不一致。

这和 `movie_url` 的历史演进很像：链接本来也是可由 LLM 顺手吐出来的东西，但最终被收回到代码侧，用确定性拼接追加。抬头行应当遵循同一条路：**render / projection 解耦，LLM 只负责正文**。

## Decision

### D0 · 冻结抬头模板

抬头行固定为：

- 片名：`「中文片名」/ original_title / title`
- 导演：原名
- 坐标：`[Y: YYYY, M: MM, D: DD]`
- 文明：`ISO639-1 大写 + 中文语言名`
- 类型：中文映射后用 `，` 连接
- 光度：`vote_average`
- 体积：`runtime`

中文片名是可插拔增强层，不是本 Phase 的必需输入；缺失时按 `drop_cn_seg` 退化。

### D1 · title / original 混用根因归位

抬头不稳定的根因不是数据缺失，而是职责混叠：LLM 在同一输出里既负责正文创作，又被允许决定哪一个片名字段更“顺眼”。这会把字段选择变成语言风格问题，直接破坏一致性。

### D2 · 类比 movie_url：由代码追加，不进创作自由度

`movie_url` 已经证明：像链接这种确定性产物，应该由代码在下游追加，而不是让 LLM 代写。抬头行同理，属于确定性投影，不是创作自由度。

### D3 · 中文译名留 TODO-B 插槽

中文片名译名需要独立增强层：如果后续要做，必须单独走 TODO-B 和独立 Phase，再引入外部 TMDB 依赖或缓存机制。本 Phase 只保留插槽，不做在线查询、不做回填，不破坏“纯本地静态库”边界。

### D4 · render / projection 解耦

- `build_header_projection(...)` 负责取数与装配。
- `render_movie_header(...)` 负责纯渲染。

两者拆开后，抬头的字段规则可单测，取数逻辑也能独立注入 stub。

### D5 · 语言/类型静态映射必须本地化

TMDB 类型与语言名都由本地静态表提供：

- `GENRE_EN_TO_ZH`：TMDB genre EN → 中文。
- `LANG_CODE_TO_ZH`：ISO639-1 → 中文语言名。

映射表必须零联网、可 import、可测试；表外值允许 fallback，但不能阻断渲染。

## Why

1. **一致性比“灵活”更重要**：抬头行的任务不是写得漂亮，而是每次都一样。
2. **职责边界更清楚**：正文是创作，抬头是投影；投影应该和 `movie_url` 一样可预测。
3. **可测性更好**：模板、映射、退化都能直接测，不需要跑 LLM 才知道结果。

## Consequences

- 本 Phase 只落地静态映射、契约文档与 ADR，不接 TMDB 在线服务。
- 后续 `scripts/compose.py` 可以直接 import 这些常量与契约。
- 若要补中文译名，必须另开 TODO-B，不在本 Phase 内扩展边界。