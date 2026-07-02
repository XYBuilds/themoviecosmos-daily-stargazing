---
name: Phase5-fetch-news
overview: 实现 fetch_news.py：宽口径 RSS 抓取、URL/标题去重、CLI 序号列表供手挑；输出标准 news JSON 供 `orchestrate`(`main.py`) / `run_eval.py --news-file` 使用。RSS 部分与新架构无强耦合，原设计基本保留。新增 5.4：RSS 真实分布上线后对 llm_judge 做一次轻量分布重对齐（清 ADR-0010 D4 债2）。可与 Phase 1–4 并行开发其余 todo，但 5.4 必须在能跑出真实 RSS 候选后做。
todos:
  - id: f5a1b2c3-0001-4000-8005-000000000001
    content: 5.1 · RSS 抓取与 news payload：feedparser、FEEDS 常量、规范化字段
    status: completed
  - id: f5a1b2c3-0001-4000-8005-000000000002
    content: 5.2 · 去重状态：seen_news.sqlite（URL）+ 14 天标题相似度（依赖 5.1）
    status: pending
  - id: f5a1b2c3-0001-4000-8005-000000000003
    content: 5.3 · CLI：打印序号列表、--pick / --url、news_pool JSON、README（依赖 5.1、5.2）
    status: pending
  - id: f5a1b2c3-0001-4000-8005-000000000004
    content: 5.4 · judge 分布重对齐（清债2）：RSS 真实分布跑出候选 → 盲标 20–30 条 → 算 judge 一致率 → 达标继续信/不达标才调 [需人工验收]
    status: pending
isProject: true
---

# Phase 5 · News（RSS 抓取）+ judge 分布重对齐

**重写说明（2026-06）**：5.1–5.3 的 RSS 设计与 Phase 3 的 fragment ladder / search unit 架构**无强耦合**，原设计基本保留。本稿主要新增 **5.4**——承接 [ADR-0010](../../docs/adr/0010-pseudo-drop-granularity-and-pipeline-first-derisking.md) D4 债2：judge 当前是 screening-only，且在「手挑 10 条高张力新闻」上校准；RSS 接入后新闻分布会变，须在真实分布上做一次轻量重对齐才能继续把 judge 当预筛信号。

## Todo 依赖关系

```mermaid
flowchart LR
  P0["Phase 0 paths"]
  T51["5.1 RSS"]
  T52["5.2 去重"]
  T53["5.3 CLI"]
  T54["5.4 judge 重对齐"]

  P0 --> T51
  T51 --> T52
  T52 --> T53
  T53 --> T54
```

- **5.1** `state/` 路径策略：优先在 `scripts/lib/paths.py` 新增 `state_dir()` / `seen_news_db()` helper；若不改 paths，则在 `fetch_news.py` 内用 `repo_root() / "state"`。当前 paths.py 尚无 state helper，本 Phase 需自行补齐或本地构造
- **5.2** 依赖 **5.1**；**5.3** 依赖 **5.1**、**5.2**
- **5.4** 依赖 **5.3**（要能跑出真实 RSS 候选）+ `extract → expand → rewrite → retrieve → compose` 链路可跑
- 5.1–5.3 与 Phase 1–4 **无硬依赖**，可并行；Phase 6 集成时需要本 Phase 完成

## Scope

### In scope

- 实现 `scripts/fetch_news.py`（替换 TODO 空壳）
- **宽口径中立 RSS**（MVP **不对源做偏好**；`FEEDS` 常量可含多类国际源）
- 输出 PRD §6.3 payload + `url`
- URL 去重 + 14 天标题 `difflib` 相似度 ≥0.7 跳过
- CLI：**打印带序号列表** → 用户手挑
- `--url` 旁路：单条 URL 解析/抓取为 news dict（供 `orchestrate`(`main.py`) `--url`）
- 池子落盘：`state/news_pool_YYYY-MM-DD.json`（可选）
- **5.4 · judge 分布重对齐**（轻量、一次性）

### Out of scope

- 全文爬虫
- RSS **内容过滤**（政治敏感等）
- Post-MVP **热度算法**（多源同事件计数 + 时间加权）
- `orchestrate`(`main.py`) 集成（Phase 6）
- 自动选 Top1（可保留 `--auto-top1` 调试开关，**非**默认）
- **judge rubric / 阈值机制改动**（5.4 只做校准对账，不改 rubric）
- **常态化人工标注**（5.4 是一次性保险，不是持续负担）

## SSOT

| 文档                                                                                       | 用途                                                                                                                                                                                                 |
| ------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| PRD §6.1–6.5                                                                               | 字段、去重、不过滤                                                                                                                                                                                   |
| Phase 1 plan                                                                               | `NewsItem` / `sample_news.json` schema；字段（title/description/pub_time/source_name/url）仍可用且 `run_eval.py --news-file` 兼容；架构阶段名以 ADR-0011 为准，不以 `agents.py` 作为当前生产阶段权威 |
| [ADR-0007](../../docs/adr/0007-logic-resonance-judge-prescreen-and-pov-focalization.md) D4 | judge 阈值纪律 / 分布漂移条目（5.4 依据）                                                                                                                                                            |
| [ADR-0010](../../docs/adr/0010-pseudo-drop-granularity-and-pipeline-first-derisking.md) D4 | 债2 来源（judge screening-only + RSS 新分布须重对齐）                                                                                                                                                |
| [docs/eval-the-bet.md](../../docs/eval-the-bet.md)                                         | 共振 rubric / judge 工作流                                                                                                                                                                           |

---

## Todo 5.1 · RSS 抓取与 payload

**依赖：** Phase 0 `paths`（建议）；`state/` 路径策略：优先在 `scripts/lib/paths.py` 新增 `state_dir()` / `seen_news_db()` helper；若不改 paths，则在 `fetch_news.py` 内用 `repo_root() / "state"`。当前 paths.py 尚无 state helper，本 Phase 需自行补齐或本地构造

### `FEEDS` 常量

- 在 `fetch_news.py` 顶部 `FEEDS: list[str]`
- **原则**：多源、跨领域、免费可访问；**不**在代码注释里写「高张力源优先」
- 至少 **3** 个 feed；解析失败不拖垮整批

### 抓取逻辑

- `feedparser.parse` 拉取各源，合并条目
- 字段映射：
  - `title` ← entry.title（必填，否则丢弃）
  - `description` ← summary / description（必填；strip HTML 标签）
  - `pub_time` ← published_parsed → ISO 字符串（可选）
  - `source_name` ← feed.title 或域名（可选）
  - `url` ← link（必填）
- **news payload 必填口径**：`url` 对 RSS 抓取 / 去重 / 溯源是必填；`title`、`description` 是下游最低必填；`pub_time`、`source_name` 可选。
- **不爬全文**

### 验收

```powershell
python -c "from scripts.fetch_news import fetch_all_entries; e=fetch_all_entries(); print(len(e), e[0].keys() if e else None)"
```

---

## Todo 5.2 · 去重状态

**依赖：** **5.1**

### URL 去重

- DB：`state/seen_news.sqlite`
- 表：`seen_urls(url_norm TEXT PRIMARY KEY, seen_at TEXT)`
- 规范化：剥 `utm_*`、`fbclid` 等 query；统一 scheme/host 大小写策略写清

### 标题相似度

- 表：`seen_titles(title TEXT, seen_at TEXT)` 或复用一张表
- 保留 **14 天**内「已选用」标题（在 **5.3 `--pick`** 或 `--mark-seen` 时写入）
- 新条目与历史比 `SequenceMatcher.ratio()`，≥ **0.7** → 标注 `skipped_title_dup` 或不展示

### 行为

- **抓取阶段**：仅 URL 已在 `seen_urls` 的跳过
- **选用阶段**：写 url + title 进 sqlite

### 验收

- [ ] 同一 url 二次抓取不出现
- [ ] 近似标题（手测两条）被过滤或标记

---

## Todo 5.3 · CLI 与输出

**依赖：** **5.1**、**5.2**

### CLI

```text
python scripts/fetch_news.py
python scripts/fetch_news.py --limit 30
python scripts/fetch_news.py --out state/news_pool_2026-05-29.json
python scripts/fetch_news.py --pick 3
python scripts/fetch_news.py --pick 3 --out-json output/selected_news.json
python scripts/fetch_news.py --url https://example.com/article
```

### 默认：`fetch` 子命令或无子命令

1. 拉取 → 去重 → 按 `pub_time` **降序**
2. 终端打印：

```text
[1] 2026-05-29 · Source · Title…
    https://...
[2] ...
```

3. `--pick N`：输出第 N 条的 **news JSON** 到 stdout 或 `--out-json`；并 **mark seen**（url + title）

### `--url` 旁路

- 不经过 RSS 列表；尝试 feedparser/简单 GET+解析，**或**要求用户同时提供 `--title` `--description`
- 最小实现：无法解析时打印说明并 exit 1；推荐配合 `--title` / `--description`

### news JSON（与 Phase 1 一致）

```json
{
  "title": "...",
  "description": "...",
  "pub_time": "...",
  "source_name": "...",
  "url": "..."
}
```

### README

- 手挑流程：`fetch_news` → 记下序号 → `main.py --news-file` / `main.py --url`（Phase 6）或 `run_eval.py --news-file`

### 验收

```powershell
python scripts/fetch_news.py --limit 10
python scripts/fetch_news.py --pick 1 --out-json output/picked_news.json
python -c "import json; json.load(open('output/picked_news.json')); print('ok')"
```

---

## Todo 5.4 · judge 分布重对齐（清债2）[需人工验收]

**依赖：** **5.3** + `extract → expand → rewrite → retrieve → compose` 链路可跑

**背景**：judge（MiMo, thinking-enabled）当前是 **screening-only**，且校准基线是「手挑 10 条高张力新闻」。RSS 进来的是真实随机新闻流（赛果/任命/产品发布/地方琐事等），分布与测试集不同。本 todo 验证 judge 在真实分布上是否仍可信，**而非**重做 rubric。

### 做法（轻量、一次性）

1. 用 5.3 的 RSS 跑出 ≥ **20–30 条真实新闻**的候选池（走 `extract → expand → rewrite → retrieve` 链路，并执行 `judge_prescreen` / `llm_judge` 预筛）。
2. 人工**盲标**这些候选的共振分（0/1/2，按 3.10 双轴 rubric），不看 judge 分。
3. 算 judge 分与人工分的**一致率 / 混淆矩阵**（重点看 judge=2 的精度、judge=0 的漏杀率）。
4. 裁决：
   - **达标**（一致率不显著低于 3.10 校准基线）⇒ judge 继续作为 RSS 分布下的预筛信号，债2 清。
   - **不达标** ⇒ 登记偏差方向，决定是否调 judge prompt / 阈值（仅此时才动），或人工接管预筛。

### 产出

- `output/Eval/phase5/judge-realdist-calibration.md`：盲标集、一致率、混淆矩阵、裁决
- 更新 PRD §8.3 / ADR-0010 D4：债2 状态从「未清」改为「RSS 分布已对齐」或「需调整」

### 验收

- [ ] 盲标 ≥20 条，一致率/混淆矩阵在案
- [ ] 给出「继续信 / 需调整」裁决
- [ ] `[需人工验收]`：用户确认裁决 → 债2 闭环

---

## Phase 5 整体验收

- [ ] 能从真实 RSS 拉到 ≥1 条可喂 `extract → expand → rewrite → retrieve → compose` 链路的条目
- [ ] `--pick` 产出合法 news JSON
- [ ] `state/seen_news.sqlite` 产生且可重复运行
- [ ] 5.4 judge 重对齐裁决在案（债2 闭环）

## 交给 Phase 6

| 产出               | 用途                                    |
| ------------------ | --------------------------------------- |
| `fetch_news.py`    | `orchestrate`(`main.py`) 默认入口拉新闻 |
| `picked_news.json` | 与 `--news-file` 相同契约               |
| `news_pool_*.json` | 总编浏览候选池                          |
| judge 重对齐裁决   | 确认 RSS 分布下 judge 预筛可信度        |

## 风险与约束

- 免费 RSS 不稳定：解析失败要可见（logging/warning）
- **勿**在 MVP 实现源偏好或内容审查
- `state/*.sqlite` 可 gitignore；`news_pool_*.json` 视需要 ignore
- 中国网络环境部分 feed 可能超时——README 注明可换 feed 或用手喂 JSON
- 5.4 是**一次性保险**，不是常态化人工标注；若 RSS 分布后续大幅漂移，再触发新一轮（Post-MVP）