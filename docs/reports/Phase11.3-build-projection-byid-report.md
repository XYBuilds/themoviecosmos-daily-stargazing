# Phase 11.3 - build-projection-byid 交付报告

## 1. 改动范围 (Scope)
- `scripts/compose.py`
- `tests/test_compose_publish.py`
- `.cursor/plans/Phase11-deterministic-movie-header-projection.plan.md`

新增/未新增依赖：无。

## 2. 技术实现 (Implementation)
- 新增 `build_header_projection(candidate, movie_detail_loader=None)`，统一把 retrieve candidate 的基础字段和 by-id 明细拼成 header projection。
- `movie_detail_loader` 可注入；默认才走 `get_movie_detail_by_tmdb_id`，测试可直接 stub，避免触碰真实 `cleaned.csv`。
- loader 异常、返回 `None`、查不到行时都会软降级；`zh_title` 固定留空，供后续 TODO-B 填槽。
- `render_movie_header` 保持纯渲染，不承担 IO；`format_selected_movie_block` 改为消费 projection。
- 补充测试覆盖：stub loader 成功、loader 抛错/None 降级、`id`/`tmdb_id` 兼容、projection 可直接喂给 `render_movie_header`。

## 3. 本地验证结果 (Verification)
- `python -m py_compile scripts/compose.py tests/test_compose_publish.py` ✅
- `python -m pytest tests/test_compose_publish.py -q` ✅
- 结果：`35 passed in 5.78s`

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- 当前 `build_header_projection` 仍是只负责投影装配；后续 11.4 还需要把头部真正接入 publish 产物。
- `render_movie_header` 现在可吃 projection，但 `zh_title` 仍为空，最终中文片名段要等 TODO-B。
- `format_selected_movie_block` 继续用于调试/预览，后续若 publish 链路改动，可能需要再收敛重复字段展示。