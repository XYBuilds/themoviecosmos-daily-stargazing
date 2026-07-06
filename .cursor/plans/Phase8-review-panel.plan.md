---
name: Phase8-review-panel
overview: |
  实现每日审核面板（review_panel/）：独立、低耦合的轻量 Web 小部件，
  取代 md 文件的人肉眼审阅，从 output/daily_batch/{date}/ 的 JSON 产物
  聚合展示当天全部新闻与候选电影，让审核者全天挑 1 条新闻的 1 部电影，
  一键触发下游 C2 定稿（写推文），决策落 selection.json 单一事实来源。
todos:
  - id: p8.1-build-data
    content: 8.1 · build_data.py 数据聚合瘦身（review_panel/build_data.py）
    status: complete
  - id: p8.2-publish-adapter
    content: 8.2 · publish_adapter.py 薄适配脚本，解决 daily_batch 产物结构冲突
    status: complete
  - id: p8.3-serve
    content: 8.3 · serve.py 本地 stdlib HTTP 服务器 + 4 个 JSON API
    status: complete
  - id: p8.4-frontend
    content: 8.4 · index.html 单文件原生 JS 前端面板
    status: todo
  - id: p8.5-integration-smoke
    content: 8.5 · 集成冒烟测试 [需人工验收]
    status: todo
isProject: true
---

# Phase 8 · Review Panel（每日审核面板）

## 背景

Phase 7 让系统能「跑一次全量日批」，产出落在 `output/daily_batch/{date}/NN-slug/`（每条新闻一个目录，含 `news.json`/`retrieve.json`/`llm-judge-scores.json`），并拼出 `briefing.md`/`briefing.zh.md` 供人肉眼审阅。本 Phase 做一个**独立、低耦合的轻量审核面板**，取代 md 文件的审阅作用：清晰展示每条新闻与其候选电影全部信息，让审核者在当天 N 条新闻中**选定 1 部最终电影**，并一键触发下游「写推文」（C2 定稿）。md 保留不删。

## 核心约束（来自用户对齐）

- 数据源用 JSON 不用 md。
- 独立小部件，放 `review_panel/`，不侵入现有 `scripts/` 结构。
- 本地服务器（Python stdlib 零依赖）+ 单文件 HTML 前端（原生 JS，无框架无构建）。
- 审核粒度：**全天挑 1 条新闻的 1 部电影**发一条推文。
- 支持多日期切换（扫描 `output/daily_batch/` 下的日期目录）。
- 选择先落 `selection.json`（决策单一事实来源，幂等），再基于它触发 publish。

## 前置条件

| Phase | 交付物                                                        | 状态      |
| ----- | -------------------------------------------------------------- | --------- |
| 6     | `main.py` 端到端管线 + `compose.run_publish` + `render_briefing` | ✅ merged |
| 7     | `heat_pool.py` + `daily_batch.py`（`output/daily_batch/{date}/` 产物结构） | ✅ merged |

Phase 7 判定依据：`git log --oneline -20` 显示 `dc12935 Merge pull request #101 from XYBuilds/feat/phase7.4-integration-smoke`（合并 7.4 集成冒烟分支），其后 `81a1e62`/`c7964f3` 两个 batch 相关提交也已直接落在 `main` 上；`git branch -a` 无残留的 `feat/phase7.*` 未合并远端分支。故 Phase 7 判定为已完全合并入 main，本 Phase 从最新 `main` 检出新分支。

## 关键决策冲突与处置

`main.py publish` 消费 Phase6 单条模式产物 `output/Daily_Briefing/{date}.md` + `output/Daily_Briefing/{date}_candidates.json`，用 `find_candidate_by_tmdb_id` / `load_news_context_for_publish` 定位（详见 SSOT）。而 daily_batch 产物在 `output/daily_batch/{date}/NN-slug/`，结构不同且无这两个文件 → 现有 publish CLI **无法直接消费日批产物**。

处置：新增薄适配脚本 `review_panel/publish_adapter.py`，从 daily_batch 目录直接取 `news.json` + `retrieve.json` 里的 candidate，import 稳定的 `compose.run_publish(candidate, news)` 产出定稿 `_copy.md`。耦合收敛在 adapter 单文件；`serve.py` 只以 subprocess 调它，HTML 前端与服务器对项目核心零 import。理由：比「伪造 Phase6 中间文件再调 main.py publish」更干净，不产生脏中间产物。

## 设计决策

| 决策         | 结论                                                             |
| ------------ | ---------------------------------------------------------------- |
| 形态         | 本地 stdlib HTTP server + 单文件原生 JS HTML                    |
| 目录         | 独立 `review_panel/`，不改 scripts/                              |
| 数据源       | `build_data.py` 聚合瘦身出 `panel.json`，前端只读它；服务器按需重建 |
| 审核粒度     | 全天 1 条新闻 × 1 部电影                                          |
| 多日期       | 扫描 `output/daily_batch/*/` 提供日期列表                        |
| 决策落盘     | `output/daily_batch/{date}/selection.json`（幂等，先落盘后触发） |
| 触发下游     | `serve.py` subprocess 调 `publish_adapter.py`；不 import 项目内部模块 |
| publish 耦合 | 仅 `publish_adapter.py` import `compose.run_publish`，收敛耦合    |
| 依赖         | 零第三方依赖（Python 标准库 + 原生前端）                          |

## 模块关系

```
review_panel/  (独立小部件，不改 scripts/)
  ├── build_data.py      读 output/daily_batch/{date}/*/ 的 news/retrieve/llm-judge-scores
  │                        → 瘦身聚合 panel.json（只留前端要显示的字段）
  ├── serve.py           stdlib http.server：静态托管 index.html + 4 个 JSON API
  │     └─(subprocess)→ publish_adapter.py
  ├── publish_adapter.py 从 daily_batch 目录取 news+candidate
  │     └─(import)────→ scripts.compose.run_publish  (唯一耦合点)
  ├── index.html         单文件前端（原生 JS）
  └── README.md
```

## 数据流

```
[扫描 daily_batch/*/]        → GET /api/dates → 日期下拉
[选定 date]                  → build_data(date) → panel.json → GET /api/data → 渲染新闻+候选
[审核勾选 1 新闻 1 电影]     → POST /api/select → 写 {date}/selection.json（幂等）
[点“写推文”]                → POST /api/publish → subprocess publish_adapter.py
                                → compose.run_publish → 写 {date}/{slug}_copy.md
                                → 回显产出路径 / 错误
```

## panel.json schema

字段来自 `retrieve.json` 的 `candidates[]` 瘦身：`tmdb_id`/`title`/`release_year`/`overview`/`genres`/`language`/`similarity`/`movie_url`、`hit_sources` 里去重的共振 agents 列表、以及 `llm-judge-scores.json` 按 `tmdb_id` join 进来的 `judge_score`/`judge_resonance_type`/`rationale`/`causal_test`。

```json
{
  "date": "2026-07-06",
  "generated_at": "<iso8601>",
  "news_items": [
    {
      "index": 1,
      "slug": "01-unacceptable-review-...",
      "news": { "title": "...", "description": "...", "source_name": "...", "pub_time": "...", "url": "..." },
      "candidates": [
        {
          "tmdb_id": 383682,
          "title": "Planet Single",
          "release_year": 2016,
          "overview": "...",
          "genres": "...",
          "language": "...",
          "similarity": 0.42,
          "movie_url": "...",
          "resonance_agents": ["THE-LOVER", "THE-HERO"],
          "judge_score": 1,
          "judge_resonance_type": "表层沾边",
          "judge_rationale": "...",
          "causal_test": ""
        }
      ]
    }
  ]
}
```

## selection.json schema

```json
{
  "date": "2026-07-06",
  "selected": {
    "news_slug": "09-pioneer-of-extreme-male-brain-theory",
    "tmdb_id": 33602,
    "title": "Temple Grandin"
  },
  "selected_at": "<iso8601>",
  "published": false,
  "copy_path": null
}
```

## API 契约

| Method | Path                     | 入参                                                | 返回                                    | 说明                                                    |
| ------ | ------------------------ | --------------------------------------------------- | --------------------------------------- | --------------------------------------------------------- |
| GET    | `/api/dates`             | 无                                                   | `{dates:[...]}`                        | 扫描 daily_batch 子目录，倒序                              |
| GET    | `/api/data?date=YYYY-MM-DD` | query: `date`                                   | panel.json 内容                        | 服务器按需调 build_data 重建                               |
| POST   | `/api/select`            | body `{date, news_slug, tmdb_id, title}`            | 落盘结果                                | 写 selection.json，幂等覆盖                                |
| POST   | `/api/publish`           | body `{date}`                                       | `{ok, copy_path, stderr}`              | 读 selection.json，subprocess 调 publish_adapter           |

---

## Todo 8.1 · build_data.py 数据聚合瘦身

**依赖**：无

### 设计

```python
def build_panel_data(date: str, batch_root: Path | None = None) -> dict:
    """聚合返回 panel dict（结构见 panel.json schema）。"""

def write_panel_json(date: str, batch_root: Path | None = None) -> Path:
    """调 build_panel_data 并写 output/daily_batch/{date}/panel.json，返回路径。"""

def list_available_dates(batch_root: Path | None = None) -> list[str]:
    """扫描 output/daily_batch/*/ 提取日期目录名，倒序返回。"""

def _join_judge_scores(candidates: list[dict], judge_scores: dict) -> list[dict]:
    """按 tmdb_id 把 llm-judge-scores.json 的评分字段 join 进 candidates。"""

def _extract_resonance_agents(hit_sources: list[dict]) -> list[str]:
    """从 hit_sources 提取去重后的共振 agent_id 列表。"""
```

### 测试

`tests/test_review_panel_build_data.py`：用 `tests/fixtures` 或临时目录造 mini daily_batch（1-2 新闻、含 retrieve+judge），验证：
- join 正确（tmdb_id 匹配到对应 judge 分数）
- 字段瘦身正确（只保留 panel.json schema 声明的字段）
- 缺 judge 分数时容错为空（不抛异常）
- `list_available_dates` 倒序返回

### 验收

```powershell
pytest tests/test_review_panel_build_data.py -v
python review_panel/build_data.py --date 2026-07-06 --dry-run
# 打印新闻数与候选数
```

---

## Todo 8.2 · publish_adapter.py（解决产物结构冲突）

**依赖**：8.1 的目录约定

### CLI

```text
python review_panel/publish_adapter.py --date YYYY-MM-DD --news-slug <slug> --tmdb-id <id>
```

### 逻辑

1. 定位 `output/daily_batch/{date}/{slug}/news.json` 读 news
2. `retrieve.json` 的 candidates 里按 tmdb_id 找 candidate
3. 调 `compose.run_publish(candidate, news)`
4. 产出 `output/daily_batch/{date}/{slug}_copy.md`（复用 `main.py` 的 `build_copy_markdown` 风格或自带轻量渲染）
5. 找不到 tmdb_id/slug 要报清晰错误并非零退出

### 测试

`tests/test_review_panel_publish_adapter.py`：monkeypatch `compose.run_publish`（不真调 LLM），验证：
- candidate/news 定位正确
- `_copy.md` 产出
- 错误路径非零退出

### 验收

```powershell
pytest tests/test_review_panel_publish_adapter.py -v
# 用 fixture 干跑（stub LLM）产出 _copy.md
```

### 技术债

与 `main.py publish` 存在两套 publish 入口，长期可考虑让 `main.py publish` 支持 `--from-daily-batch` 统一，本 Phase 不做。

---

## Todo 8.3 · serve.py 本地服务器

**依赖**：8.1、8.2

### 设计

stdlib `http.server`（`ThreadingHTTPServer` + `BaseHTTPRequestHandler`），零依赖。实现上面 4 个端点 + 静态托管 `index.html`。`POST /api/publish` 用 `subprocess.run([sys.executable, ".../publish_adapter.py", ...])` 调用，回传 returncode/stderr。

### CLI

```text
python review_panel/serve.py --port 8770 [--batch-root ...]
```

### 安全提示

仅绑 `127.0.0.1`；这是**无鉴权的本地面板**，不可暴露到公网。

### 测试

`tests/test_review_panel_serve.py`：用 `http.client` 或 `TestCase` 起服务器打端点，monkeypatch publish 子进程，验证 `/api/dates`、`/api/data`、`/api/select` 落盘、`/api/publish` 分发。

### 验收

```powershell
pytest tests/test_review_panel_serve.py -v
python review_panel/serve.py --port 8770
# 手动打开验证
```

---

## Todo 8.4 · index.html 前端面板

**依赖**：8.3

### 设计

单文件原生 JS（fetch 调 API，无框架、无构建、无 CDN 依赖）。布局：

- 顶部日期下拉（`/api/dates`）
- 主区按新闻分组卡片，每条新闻显示 title/source/pub_time/url/正文 + 其候选电影列表（片名年份、相似度、genres/language、共振 agents 徽章、judge_score 高亮、rationale/causal_test、overview、跳转链接）
- 每部候选一个「选为今日之选」单选（全天唯一）
- 选定后「写推文」按钮触发 `/api/publish`，展示 loading 与产出路径/错误

清晰可读优先。

### 测试

前端以人工冒烟为主（列在 8.5）；可选加一个 HTML 结构 smoke（检查关键元素 id 存在）。

### 验收

浏览器打开，完整走查一遍展示与选择交互。

---

## Todo 8.5 · 集成冒烟测试 [需人工验收]

**依赖**：8.1-8.4

**目标**：真实起 `serve.py`，用 2026-07-06 数据端到端：切日期 → 看新闻候选 → 选 1 部 → 落 selection.json → 触发 publish → 检查 `_copy.md`。

**人工验收清单**：

- 展示完整性（新闻与候选信息齐全无缺漏）
- 选择幂等（重复选择/切换不产生脏数据）
- publish 产出正确（`_copy.md` 内容与所选候选一致）
- 错误可见（异常路径在前端有清晰提示）

**人工验收阻断说明**：标注 `[需人工验收]`，人工通过前不标 complete、不写 report、不 merge。

---

## 风险与约束

| 风险                              | 缓解                                                        |
| --------------------------------- | ------------------------------------------------------------- |
| 无鉴权本地面板不可公网暴露        | `serve.py` 仅绑 `127.0.0.1`，plan 与 README 中明确标注安全边界 |
| 两套 publish 入口（main.py / adapter）的技术债 | 8.2 已注明技术债，长期考虑 `main.py publish --from-daily-batch` 统一 |
| panel.json 重建性能（retrieve.json 数千行） | `build_data.py` 只做按需重建，避免不必要的全量重算            |
| selection 幂等覆盖语义            | 每次 `/api/select` 直接覆盖写 selection.json，明确「最后一次选择生效」 |
| 前端零依赖约束                    | 原生 JS 无框架无构建，避免引入前端工具链耦合                  |

## SSOT

| 文档                                                                 | 用途                                                           |
| ---------------------------------------------------------------------- | ---------------------------------------------------------------- |
| `scripts/compose.py` `run_publish`（line ~404）                        | C2 定稿唯一入口，`publish_adapter.py` 的耦合点                  |
| `scripts/main.py` `_run_publish_cli` / `find_candidate_by_tmdb_id` / `load_news_context_for_publish`（line ~324-410） | 佐证 publish 依赖 `Daily_Briefing/{date}.md` + `{date}_candidates.json`，与 daily_batch 产物结构不一致 |
| `scripts/lib/render_briefing.py`                                        | Phase6 渲染模块参考，本 Phase 前端不复用其渲染逻辑，仅参考字段口径 |
| `output/daily_batch/{date}/` 产物契约                                    | Phase7 定义的日批目录结构（news.json/retrieve.json/llm-judge-scores.json） |
| ADR-0009                                                                | candidate 字段口径（tmdb_id/title/release_year/overview/genres/language/similarity/movie_url 等） |