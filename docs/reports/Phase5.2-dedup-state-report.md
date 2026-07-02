# Phase 5.2 - 去重状态交付报告

## 1. 改动范围 (Scope)

- `scripts/fetch_news.py`：新增去重状态层（URL 规范化 + `seen_news.sqlite` 读写 + 14 天标题相似度 + 组合便捷函数）。
- `scripts/lib/paths.py`：新增 `state_dir()` / `seen_news_db()` 两个路径 helper。
- `tests/test_fetch_news_dedup.py`：新增 unittest 测试（5 用例，全部用临时 sqlite，无网络）。
- 依赖：无新增（`sqlite3` / `difflib` / `datetime` 均标准库）。

## 2. 技术实现 (Implementation)

### paths.py 新增

| helper | 默认值 | env 覆盖 |
| --- | --- | --- |
| `state_dir() -> Path` | `state/` | `STATE_DIR` |
| `seen_news_db() -> Path` | `state_dir() / "seen_news.sqlite"` | `SEEN_NEWS_DB` |

均复用既有 `_resolve_path(env_var, default)` 风格，与 `cleaned_csv` / `index_dir` 一致。

### 数据流向与语义边界

```
抓取阶段 (5.3 fetch)                      选用阶段 (5.3 --pick)
─────────────────                        ─────────────────
fetch_all_entries()                      mark_selected(entry)
      │                                        │
      ▼                                  ┌──────┴───────┐
filter_new_entries()                     ▼              ▼
  只读 seen_urls                    mark_url_seen   mark_title_seen
  仅按 URL 已见过滤                  (INSERT OR      (INSERT into
  不写库 / 不按标题过滤               IGNORE)         seen_titles)
      │
      ▼
未见过的候选 (保序)
```

- **抓取阶段只做 URL 去重**：`filter_new_entries` 仅读 `seen_urls`，不写库，不因标题相似而丢弃。
- **标题相似度留给选用阶段**：`is_title_similar` 供 5.3 UI 标注/展示，14 天窗口 + `SequenceMatcher.ratio() >= 0.7`。
- **写库只发生在选用**：`mark_selected` 用同一时间戳同时写 URL + title。

### 函数层（functional，纯函数 + 显式 db_path 注入）

| 函数 | 职责 |
| --- | --- |
| `normalize_url(url)` | 剥 `utm_*`/`fbclid` 等跟踪参数、scheme/host 小写、去 fragment、保留正常 query；幂等 |
| `is_url_seen / mark_url_seen` | `seen_urls(url_norm PRIMARY KEY, seen_at)` 查/写（`INSERT OR IGNORE`） |
| `is_title_similar / mark_title_seen` | `seen_titles(title, seen_at)`；相似度按 14 天窗口 + 阈值 0.7；`now` 可注入 |
| `filter_new_entries(entries)` | 抓取阶段：仅按 URL 已见过滤，保序，不写库 |
| `mark_selected(entry)` | 选用阶段：一次性写 URL + title（供 5.3 `--pick`） |
| `_connect / _ensure_schema` | 首次访问自动建表；`db_path.parent.mkdir` 保证目录存在；建表幂等 |

所有查/写函数接受 `db_path: Path | None = None`（None 时用 `seen_news_db()`），便于测试注入临时文件。

## 3. 本地验证结果 (Verification)

新增测试（本 todo 范围）：

```text
python -m unittest tests.test_fetch_news_dedup
.....
Ran 5 tests in 0.065s
OK
```

覆盖点：URL 规范化（剥 utm_/fbclid、小写 host/scheme、去 fragment、保留正常 query、幂等）；URL 去重（含不同 utm 同实际 URL 视为已见）；标题相似度（近似判 True、差异判 False、超 14 天窗口不参与比对）；`filter_new_entries`（URL 已见过滤、未见保留、保序、不因标题相似过滤）；建表幂等。

全量 regression 核验：

- main 基线：`Ran 231 tests ... FAILED (failures=6, errors=2, skipped=1)`
- 应用 5.2 后：`Ran 242 tests ... FAILED (failures=6, errors=2, skipped=1)`

结论：**5.2 零 regression**。既有 6 failures + 2 errors 全部 pre-existing（集中在 `test_copywriter_review`，不 import `fetch_news`），与本 todo 无关。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `state/*.sqlite` 已在 `.gitignore`，运行时产物不会误入库。
- `filter_new_entries` 保留了 `title_threshold` / `within_days` / `now` 三个当前用 `del` 丢弃的参数，是为 5.3 选用阶段签名预留；若 5.3 最终不需要可再收敛。
- 5.3 接口就绪：抓取用 `filter_new_entries`，选用用 `mark_selected`，标注用 `is_title_similar`，无需回改 5.2。
- 标题窗口比较依赖 helper 写入的 ISO UTC 时间格式；外部若直接写库须保持同一格式。
- 既有全量测试的 6 failures + 2 errors 为 pre-existing，不属于 Phase 5 范围，未处理。