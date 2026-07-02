# Phase 5.3 - CLI 与输出交付报告

## 1. 改动范围 (Scope)

- `scripts/fetch_news.py`：新增 argparse CLI 层（列表展示 / `--limit` / `--out` / `--pick` / `--out-json` / `--url` 旁路），纯逻辑函数 + 薄 `main()` 壳。
- `tests/test_fetch_news_cli.py`：新增 unittest（9 用例，全部 mock，无真实网络）。
- `README.md`：新增 `## 新闻抓取与手挑（fetch_news）` 一节。
- 依赖：无新增。

## 2. 技术实现 (Implementation)

### 数据流向

```
默认列表模式:
fetch_all_entries() ─▶ filter_new_entries(只URL去重) ─▶ sort_entries_by_pub_time(降序,None末尾)
       │                                                          │
       ├─ --out PATH ─▶ write_json(去重后完整候选池)              ▼
       └────────────────────────────────────────▶ render_news_list(带序号[N]+URL)

--pick N (1-based):
候选池[N-1] ─▶ emit_news_json(stdout 或 --out-json) ─▶ mark_selected(url+title 写库)

--url URL (旁路,不走RSS列表):
feedparser.parse(url) ─得到条目─▶ _entry_to_payload
       │ 解析不出必填字段
       ▼
--title/--description 兜底 ─▶ news JSON ─▶ emit + mark_selected
```

### 纯逻辑 / IO 分离（functional）

| 函数 | 职责 |
| --- | --- |
| `build_parser` / `parse_args` | argparse 定义；`--pick` 与 `--url` 互斥组；`_positive_int` 校验 ≥1 |
| `sort_entries_by_pub_time` | pub_time 降序，None/无效排最后，stable |
| `render_news_list` | 纯渲染带序号列表，标题 80 字温和截断，缺字段占位 |
| `build_url_news_payload` | 单 URL → payload，异常隔离，缺字段要求 `--title/--description` |
| `emit_news_json` / `write_json` | 输出单条 news JSON（stdout 或文件，父目录自动建） |
| `fetch_candidate_pool` | fetch → filter → sort 组合 |
| `run_cli(argv, *, db_path, stdout, stderr)` | 可注入 streams/db 的 CLI 主逻辑（便于单测） |
| `main` | `raise SystemExit(run_cli(argv))` 薄壳 |

### CLI 参数与默认值

| 参数 | 说明 | 默认 |
| --- | --- | --- |
| `--limit` | 列表展示上限（正整数） | 30 |
| `--out PATH` | 去重后完整候选池 JSON 落盘（`ensure_ascii=False, indent=2`） | 无 |
| `--pick N` | 1-based 序号，输出该条 news JSON 并 `mark_selected`；与 `--url` 互斥 | 无 |
| `--out-json PATH` | 选中条目写文件（父目录自动建），否则打印 stdout | 无 |
| `--url URL` | 单条 URL 旁路；与 `--pick` 互斥 | 无 |
| `--title/--description` | `--url` 解析失败时的兜底必填 | 无 |
| `--source-name/--pub-time` | `--url` 兜底可选字段 | 无 |

## 3. 本地验证结果 (Verification)

新增测试（本 todo 范围）：

```text
python -m unittest tests.test_fetch_news_cli
.........
Ran 9 tests in 0.061s
OK
```

覆盖点：pub_time 降序 + None 末尾 + 稳定；列表渲染含序号/URL/截断/占位；`--out` 落盘可 `json.load` 回读；`--pick N` 取第 N 条 + 五字段合法 + 触发 `mark_selected`（之后 `is_url_seen` 为 True）；`--pick` 越界非 0 退出；`--pick` 与 `--url` 互斥被拒；`--url` 兜底（有 title/description 成功、都无则 exit 1）。测试直接调 `run_cli` 注入临时 db/stream，不 subprocess、不联网。

全量 regression 核验：

- main 基线：`Ran 231 tests ... FAILED (failures=6, errors=2, skipped=1)`
- 应用 5.3 后：`Ran 251 tests ... FAILED (failures=6, errors=2, skipped=1)`

结论：**5.3 零 regression**。既有 6 failures + 2 errors 全部 pre-existing（集中在 `test_copywriter_review`），与本 todo 无关。

真实联网：未跑真实 `fetch_all_entries()`，以 mock 单测为准（避免网络不稳定影响验收）；CLI 逻辑经注入式单测充分覆盖。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **Phase 6 契约**：`--pick ... --out-json output/picked_news.json` 输出单个 dict（title/description/pub_time/source_name/url），与 `--news-file` / `tests/sample_news.json` 契约一致，可直接喂 `main.py`（Phase 6）/ `run_eval.py`。
- `--out state/news_pool_*.json` 输出候选**列表**，供总编浏览，不能直接当单条 `--news-file`。
- `state/*.json` 已 gitignore，落盘产物不入库。
- `--url` 旁路对真实文章页（非 RSS）解析能力有限，依赖 `--title/--description` 兜底——这是计划规定的最小实现，非缺陷。
- 既有全量 6 failures + 2 errors 为 pre-existing，不属于 Phase 5 范围，未处理。

## 5. Phase 5 状态

- 5.1（RSS 抓取）/ 5.2（去重状态）/ 5.3（CLI）已完成并可端到端跑：抓取 → URL 去重 → 序号列表 → `--pick` 产出合法 news JSON + 写 sqlite。
- **5.4（judge 分布重对齐）需真实 RSS 全链 LLM + 人工盲标，标记 `[需人工验收]`，按用户决策在 5.3 合并后停下汇报，不自动执行。**