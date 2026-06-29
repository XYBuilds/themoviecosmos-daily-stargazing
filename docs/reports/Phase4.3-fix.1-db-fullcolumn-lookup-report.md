# Phase 4.3-fix.1 - DB 全列 lookup 交付报告

## 1. 改动范围 (Scope)
- 新增 `scripts/movie_metadata.py`：提供按 `tmdb_id` 点查 `cleaned.csv` 全列明细的通路 B。
- 更新 `scripts/retrieve.py`：导出通路 B lookup 接口，检索热路径仍使用 `meta.parquet`。
- 新增 `tests/test_movie_metadata.py`：覆盖 28 列全量返回、`id`/`tmdb_id` 两种键列、`META_COLUMNS` 精简约束。
- 更新 `.cursor/plans/Phase4-copywriter-c1-c2.plan.md`：标记 4.3-fix.1 complete。
- 新增/删除依赖包：无。

## 2. 技术实现 (Implementation)
- 保持通路 A 不变：`scripts/build_index.py` 的 `META_COLUMNS` 仍为 9 列，未加入 director/评分/热度等重列。
- 新增通路 B：`get_movie_detail_by_tmdb_id()` / `get_movie_details_by_tmdb_ids()` 从 `data/output/cleaned.csv` 读取并缓存全列，按 `tmdb_id` 或现有 `id` 列点查。
- lookup 返回 JSON-safe 字典；缺失影片返回 `None`，不影响 retrieve 热路径。

## 3. 本地验证结果 (Verification)
- `python -m pytest tests/test_movie_metadata.py tests/test_retrieve_multi_pseudo.py tests/test_retrieve_funnel.py; python -c "from scripts.movie_metadata import get_movie_detail_by_tmdb_id; d=get_movie_detail_by_tmdb_id(157336); print(len(d) if d else 'missing'); print(d.get('director'), d.get('vote_average'))"`
  - 结果：`17 passed in 18.01s`
  - lookup 冒烟：`28`；`Christopher Nolan 8.5`
- 第一次运行同一命令时测试暴露 `id` 被索引规范化为字符串；已修复为只用字符串索引、不改原列值，第二次通过。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- 本分支从 `main` 检出，无前置开发分支继承。
- 通路 B 只开放能力，不决定决策卡/发布稿使用哪些字段；字段注入留给 4.3-fix.2 / 4.3-fix.3。
- 当前实现按需读取完整 CSV 并缓存，适合少量候选点查；若后续高频批量调用，可再评估轻量列式缓存。