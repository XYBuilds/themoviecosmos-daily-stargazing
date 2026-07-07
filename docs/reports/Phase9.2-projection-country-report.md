# Phase 9.2 · 投影加 production_countries — 交付报告

## 改动范围（Scope）

- `scripts/compose.py`：`_DB_PROJECTION_FIELDS` 在 `writers` 与 `vote_average` 之间插入 `production_countries`。

**分支继承**：`feat/phase9.2-projection-country` 从 `feat/phase9.1-panel-stale-copy-fix` 检出（9.1 已开发未合并、PR #108 等待人工验收）。对应 todo：9.1 G8 bugfix。

## 技术实现（Implementation）

按 ADR-0015 D6：`production_countries` 是 `cleaned.csv` 第 18 列（0-indexed 17），通路 B（`get_movie_detail_by_tmdb_id` 全列读取）已可得。仅需把它加入 `_DB_PROJECTION_FIELDS` 白名单，`_db_projection_for_candidate` / `_format_db_projection` / `render_review_copy_block` 均按该元组自动遍历渲染，无需额外改渲染函数。

该白名单为 C1 决策卡与 C2 发布稿**共用**，故 C1 决策卡也会多出此列——ADR-0015 判定为无害透传（编辑视图可接受）。

## 本地验证结果（Verification）

```
python -c "... _db_projection_for_candidate({'tmdb_id':'1379520'}) ..."
production_countries in projection: True -> United States of America
block has production_countries line: True

python -m pytest tests/test_compose_publish.py tests/test_compose_decision_card.py -q
8 passed in 7.21s
```

- `get_movie_detail_by_tmdb_id('1379520')` 投影含 `United States of America`。✅
- `format_selected_movie_block` 输出的 DB 字段含 `production_countries` 行。✅
- C1 `render_review_copy_block` 走同一元组遍历 → 决策卡自动带该列（无害透传）。✅
- 既有 compose 测试无 regression。

## 潜在影响或技术债（Technical Debt & Caveats）

- **副作用（已知、可接受）**：决策卡（C1）视图多一列 `production_countries`。ADR-0015 明确判定无害。
- **静默降级**：DB 该列缺失时 `_format_db_projection` 自动跳过（`value in (None, "")` 过滤），无 warning——与其它可选字段一致，符合 ADR-0015 G6「必含若可得＝静默降级，本期不加校验」。
- 无契约/接口变化，纯投影加列。
