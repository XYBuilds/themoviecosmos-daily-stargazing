# Phase 7.1 - Heat Pool 采集与计分模块 交付报告

## 1. 改动范围 (Scope)

**新增文件**：
- `scripts/heat_pool.py` — 热度池采集、计分、去重过滤、fallback 补齐、正文富化、持久化的完整模块
- `tests/test_heat_pool.py` — 单元测试（11 个测试用例）

**修改文件**：
- `.cursor/plans/Phase7-heat-pool-daily-batch.plan.md` — p7.1-heat-pool status: `todo` → `completed`

**依赖包**：无新增依赖。复用现有 `requests`（已在 `fetch_news.py` 中使用）。

## 2. 技术实现 (Implementation)

### 核心设计思路

模块严格遵循 Phase 7 plan 给出的六函数流水线设计，数据从 Guardian 32 个 section 单向流向最终 `pool.json`：

```
fetch_heat_signals → score_and_rank → filter_seen → fallback_newest
  → enrich_descriptions → fetch_heat_pool(顶层入口, 负责 persist)
```

- **`fetch_heat_signals`**：逐 section 调 `GET /{section}?show-most-viewed=true&show-editors-picks=true`。
  用真实 API 探测确认了响应形状为 `response.mostViewed[]` / `response.editorsPicks[]`，每条含
  `webUrl` / `webTitle` / `webPublicationDate`。按数组下标算 1-based `rank_position`。单 section
  网络异常（`requests.RequestException` / `OSError`）或非 JSON 响应只跳过该 section，不影响其余
  31 个 section 的采集——与 `fetch_news.py::fetch_all_entries` 的单源容错模式保持一致。请求间插入
  `_SECTION_REQUEST_DELAY_SECONDS=0.1s` sleep，避免撞 Guardian 免费 tier 12 req/s 限速。

- **`score_and_rank`**：按 URL 聚合信号，`score = Σ(1/rank_position for mostViewed) + 0.5 × count(editorsPicks)`。
  同一 URL 跨 section 重合会累加两次贡献，天然实现"跨 section 重合加分"。返回 dict 含 `sources`
  数组记录每条信号的来源 section/type/rank，供 debug 复现。

- **`filter_seen`**：复用 `fetch_news.is_url_seen`，排序后再过滤（严格遵循 plan 中"排序后过滤"的设计决策，
  不在采集阶段过滤，保留完整分数分布用于 debug）。

- **`fallback_newest`**：`len(ranked) < min_count` 时才触发，调用 `fetch_news.fetch_guardian_api(order_by='newest')`
  补齐。跳过已在 `ranked` 中出现过的 URL 防重复；补齐条目标记 `fallback: True` 并沿用其自带的 `description`，
  跳过后续 `enrich_descriptions` 的重复抓取。

- **`enrich_descriptions`**：只对缺 `description` 的条目（纯热度信号来源）逐条调 Content API
  (`show-fields=bodyText,trailText&show-tags=all`)，用 `fetch_news.extract_guardian_description()`
  做 tone-driven 正文抽取。单条失败时 `description` 置空字符串，不中断整批。

- **`fetch_heat_pool`**：顶层入口，串联以上五步；`dry_run=True` 时跳过写盘（供 CLI `--dry-run` 使用）。

### 复用与新增边界

严格复用 `scripts/fetch_news.py` 的：`is_url_seen`、`extract_guardian_description`、
`fetch_guardian_api`（fallback 阶段延迟导入，避免与测试 mock 的循环依赖）、`_load_env_value`
（内部 API key 解析）。新增 `RANKED_SECTIONS` 常量与 `fetch_news.GUARDIAN_API_SECTIONS` 不同
（Phase 7.1 需求给出的 32-section 列表含 `animals-farmed`/`inequality`，不含 `travel`），两者独立
维护，未复用旧的 blacklist 过滤逻辑（`RANKED_SECTIONS` 本身已是精选列表）。

### CLI

```powershell
python scripts/heat_pool.py                    # 默认今天, min_count=10
python scripts/heat_pool.py --date 2026-07-05
python scripts/heat_pool.py --min-count 15
python scripts/heat_pool.py --dry-run           # 只打印不写文件
```

### 持久化

`output/daily_batch/{date}/pool.json` — 完整 ranked pool（含 score、sources、description）。

## 3. 本地验证结果 (Verification)

```powershell
pytest tests/test_heat_pool.py -v
```

```
tests/test_heat_pool.py::FetchHeatSignalsTests::test_fetch_heat_signals_maps_sections_and_rank_position PASSED
tests/test_heat_pool.py::FetchHeatSignalsTests::test_fetch_heat_signals_skips_failed_section_without_raising PASSED
tests/test_heat_pool.py::ScoreAndRankTests::test_score_and_rank_ignores_signals_without_url PASSED
tests/test_heat_pool.py::ScoreAndRankTests::test_score_and_rank_sums_cross_section_overlap PASSED
tests/test_heat_pool.py::FilterSeenTests::test_filter_seen_excludes_already_seen_urls PASSED
tests/test_heat_pool.py::FallbackNewestTests::test_fallback_newest_noop_when_already_enough PASSED
tests/test_heat_pool.py::FallbackNewestTests::test_fallback_newest_supplements_up_to_min_count PASSED
tests/test_heat_pool.py::EnrichDescriptionsTests::test_enrich_descriptions_fills_missing_description_via_content_api PASSED
tests/test_heat_pool.py::EnrichDescriptionsTests::test_enrich_descriptions_sets_empty_string_on_request_failure PASSED
tests/test_heat_pool.py::FetchHeatPoolTests::test_fetch_heat_pool_dry_run_skips_write_and_returns_pool PASSED
tests/test_heat_pool.py::FetchHeatPoolTests::test_fetch_heat_pool_writes_pool_json_when_not_dry_run PASSED

11 passed in 5.17s
```

另外运行了全量测试套件 `pytest -q` 做 regression check：299 passed, 8 failed, 1 skipped。
**8 个失败均在 `tests/test_copywriter_review.py`**，属于本分支未改动的既有文件（`scripts/compose.py`
的 `ReviewCopy`/渲染格式与测试期望的字段名/输出格式已经不一致，如 `copy_text` 属性缺失、
`db_projection` 嵌套结构与测试期望的扁平 `overview` 键不符），与本次 heat_pool 改动无关，为
Phase 7.1 之前遗留的技术债。未在本次范围内修复（超出 p7.1 scope）。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **对 Phase 7.2 的影响**：`fetch_heat_pool()` 是 daily_batch.py 编排器的直接依赖入口，其返回的
  pool item 形状（`url`/`title`/`pub_time`/`score`/`sources`/`description`）需要在 7.2 消费时
  转换为 `NewsItem`（`main.py::_news_from_dict` 要求 `title`/`description` 非空）。fallback 补齐
  条目额外带 `source_name`/`fallback` 字段，heat-signal 原生条目没有，7.2 编排器读取时需要做
  防御性 `.get()`。
- **未修复的既有测试失败**：`tests/test_copywriter_review.py` 的 8 个失败是 Phase 7.1 之前就存在的
  回归（与本模块无关），建议后续单独开一个 fix 分支处理，不应阻塞 Phase 7.1 合并。
- **未验证项**：受限于当前环境无真实 `GUARDIAN_API_KEY`，未执行 `python scripts/heat_pool.py --dry-run`
  的真实网络冒烟测试；已单独用真实 API 探测确认了 Guardian Section API 的 `mostViewed`/`editorsPicks`
  响应形状（见本报告 §2），并据此设计了 `fetch_heat_signals` 的解析逻辑与对应 mock 测试。真实端到端
  冒烟验证留给 Phase 7.3 [需人工验收]。
- **RANKED_SECTIONS 与 GUARDIAN_API_SECTIONS 并存**：两份 section 列表目的不同（热度信号采集 vs.
  RSS/newest fallback 的宽进黑名单过滤），未来如需统一维护建议在 ADR 中显式记录两者的语义边界，
  避免后续误合并导致行为漂移。