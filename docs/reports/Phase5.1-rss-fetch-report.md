# Phase 5.1 - RSS 抓取与 news payload 交付报告

## 1. 改动范围 (Scope)

- `scripts/fetch_news.py`：从 TODO 空壳实现为 RSS 抓取层（FEEDS 常量 + 抓取/规范化纯函数）。
- `tests/test_fetch_news.py`：新增 unittest 测试（6 用例，全部无真实网络请求）。
- 依赖：无新增。`feedparser>=6.0` 已在 `requirements.txt` 声明，仅确认可用。

## 2. 技术实现 (Implementation)

### 数据流向

```
FEEDS[str]  ──feedparser.parse──▶  parsed_feed
                                        │  (bozo / 异常 → 记 warning 返回 [])
                                        ▼
                              entries[]  ──_entry_to_payload──▶  news payload dict
                                                                   │ 缺必填字段 → None 丢弃
                                                                   ▼
                                                    {title, description, pub_time, source_name, url}
```

### 函数层（functional，纯函数 + 单一职责）

| 函数 | 职责 |
| --- | --- |
| `fetch_feed(feed_url) -> list[dict]` | 解析单源 → 规范化 payload 列表；网络/解析/bozo 失败**不抛**，返回 `[]` + warning |
| `fetch_all_entries(feeds=None) -> list[dict]` | 默认用 `FEEDS`，合并多源；单源失败不拖垮整批 |
| `_entry_to_payload(entry, source)` | 单条 entry → payload；缺 title/description/url 任一则返回 `None` |
| `_strip_html(text)` | `html.unescape` + 正则去标签 + 压平空白（无新依赖） |
| `_published_to_iso(published_parsed)` | `published_parsed` → UTC ISO8601 字符串，无则 `None` |
| `_source_name(feed, url)` | 优先 RSS 自带源名，回退 URL 域名 |
| `_get_value(obj, key)` | 兼容 feedparser 对象 / SimpleNamespace / dict 读取 |

### payload schema（对齐 `tests/sample_news.json`）

```json
{"title": str, "description": str, "pub_time": str|None, "source_name": str|None, "url": str}
```

必填字段：`title` / `description` / `url`（缺任一丢弃该条）；`pub_time` / `source_name` 可选。

### FEEDS（3 个中立跨领域国际源）

- `https://feeds.bbci.co.uk/news/world/rss.xml`
- `https://www.npr.org/rss/rss.php?id=1001`
- `https://www.aljazeera.com/xml/rss/all.xml`

## 3. 本地验证结果 (Verification)

新增测试（本 todo 范围）：

```text
python -m unittest tests.test_fetch_news
......
Ran 6 tests in 0.003s
OK
```

覆盖点：正常规范化 + HTML strip + pub_time ISO、缺必填字段丢弃、parse 异常返回空、bozo 返回空、多源合并且跳过失败源、验收 import + 五字段 keys。

全量测试 regression 核验（stash 对比法）：

- main 基线（无 5.1 改动）：`Ran 231 tests ... FAILED (failures=6, errors=2, skipped=1)`
- 应用 5.1 后：`Ran 237 tests ... FAILED (failures=6, errors=2, skipped=1)`

结论：**5.1 零 regression**。既有 6 failures + 2 errors 全部 pre-existing（集中在 `test_copywriter_review` 等，不 import `fetch_news`），与本 todo 无关；新增 6 用例全部通过（231→237）。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `fetch_all_entries()` 返回稳定五字段 dict 列表，5.2 可直接按 `url` / `title` 做去重消费，接口无需改动。
- 5.1 不触碰 `state/` / sqlite / 标题相似度 / CLI —— 边界与 5.2（去重）、5.3（CLI）清晰隔离。
- 对 bozo 解析结果采取**整源丢弃**的严格策略；若后续真实源偶发 bozo 但仍含可用条目导致召回过低，可在 5.3 或配置层再评估是否允许部分保留。
- 既有全量测试的 6 failures + 2 errors 为 pre-existing，不属于 Phase 5 范围，未处理。