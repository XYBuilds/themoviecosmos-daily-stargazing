---
name: Phase7-heat-pool-daily-batch
overview: |
  实现热度池 (Heat Pool) 自动选题 + daily_batch.py 批量编排器 + 断点续跑。
  让系统能"跑一次全量日批"：从 Guardian 32 个 section 拉 mostViewed + editorsPicks，
  按 composite score 排序选 top-N(≥10)，逐条喂入现有管线，stage+persona 级断点续跑。
todos:
  - id: p7.1-heat-pool
    content: "7.1 · Heat Pool 采集与计分模块（scripts/heat_pool.py）"
    status: completed
  - id: p7.2-daily-batch
    content: "7.2 · Daily Batch 编排器 + 断点续跑（scripts/daily_batch.py）"
    status: completed
  - id: p7.3-integration-smoke
    content: "7.3 · 集成冒烟测试 [需人工验收]"
    status: todo
isProject: true
---

# Phase 7 · Heat Pool + Daily Batch 编排

## 背景

Phase 6 完成了单条 news 的端到端管线（`main.py`）。本 Phase 将其升级为"日批量"模式：
自动从 Guardian 热度信号选题 → 批量跑管线 → 断点续跑。

## 前置条件

| Phase | 交付物 | 状态 |
|-------|--------|------|
| 5 | `fetch_news.py`（Guardian API + RSS + dedup） | ✅ merged |
| 6 | `main.py` 端到端管线 + `render_briefing` + `RunOptions` | ✅ merged |

## 设计决策（grill session 2026-07-05）

| 决策 | 结论 |
|------|------|
| 术语 | 热度池 (Heat Pool)，见 CONTEXT.md |
| 总编职责 | 退出选题环节，只审终稿（CONTEXT.md 已更新） |
| 架构 | 新增 `daily_batch.py` 编排器，`main.py` 保持单条语义 |
| 信号源 | mostViewed + editorsPicks，两信号独立入池 |
| 计分 | `sum(1/rank_per_section) + 0.5 * editorsPicks_count` |
| 正文补取 | rank 后 top-N 再逐条调 Content API 拿 bodyText |
| 断点粒度 | stage 级 + persona 内部 checkpoint |
| 产出目录 | `output/daily_batch/{date}/` 独立结构 |
| 不够时回退 | 用 `order-by=newest` 补齐到 min_count |
| sections | 32 个内容 section 全拉 |
| seen 过滤 | 排序后再过滤 |

## 模块关系

```
daily_batch.py (编排器)
  ├── heat_pool.py (采集 + 计分 + 持久化)
  │     └── fetch_news.py (复用: is_url_seen, mark_selected, extract_guardian_description)
  └── main.py::run_daily_pipeline() (单条管线，零改动)
```

## 数据流

```
[32 sections] → fetch_heat_signals → score_and_rank → filter_seen → fallback_newest
  → enrich_descriptions → persist pool.json
  → daily_batch loop:
      for each news in selected:
        deconstruct → expand → persona(×N, checkpoint each) → retrieve → compose
        → write checkpoint after each stage
```

---

## Todo 7.1 · Heat Pool 采集与计分模块

**目标**：新建 `scripts/heat_pool.py`，封装热度池采集、计分、补齐、正文富化的完整流程。

### 常量

```python
RANKED_SECTIONS: list[str] = [
    "animals-farmed", "artanddesign", "australia-news", "books",
    "business", "commentisfree", "culture", "education",
    "environment", "fashion", "film", "food",
    "football", "games", "global-development", "inequality",
    "law", "lifeandstyle", "media", "money",
    "music", "news", "politics", "science",
    "society", "sport", "stage", "technology",
    "tv-and-radio", "uk-news", "us-news", "world",
]
DEFAULT_MIN_COUNT = 10
```

### 函数设计

```python
def fetch_heat_signals(
    sections: list[str] = RANKED_SECTIONS,
    *,
    api_key: str | None = None,
) -> list[dict]:
    """遍历 sections，每个调 GET /{section}?show-most-viewed=true&show-editors-picks=true。
    返回 raw signal list: [{url, title, pub_time, section, signal_type, rank_position}, ...]
    """

def score_and_rank(signals: list[dict]) -> list[dict]:
    """按 URL 去重聚合，计算 composite score:
      score = sum(1/rank for mostViewed appearances) + 0.5 * count(editorsPicks appearances)
    返回 [{url, title, pub_time, score, sources: [...], ...}] 按 score DESC 排序。
    """

def filter_seen(ranked: list[dict], *, db_path: Path | None = None) -> list[dict]:
    """排序后过滤 seen_news.sqlite 已跑过的 URL。"""

def fallback_newest(
    ranked: list[dict],
    *,
    min_count: int = DEFAULT_MIN_COUNT,
    db_path: Path | None = None,
    api_key: str | None = None,
) -> list[dict]:
    """ranked 不够 min_count 时，用 fetch_guardian_api(order_by='newest') 补齐。"""

def enrich_descriptions(
    selected: list[dict],
    *,
    api_key: str | None = None,
) -> list[dict]:
    """对每条调 Content API (show-fields=bodyText,trailText) 拿正文，
    用 extract_guardian_description() 提取 description 字段。"""

def fetch_heat_pool(
    *,
    date: str | None = None,
    min_count: int = DEFAULT_MIN_COUNT,
    db_path: Path | None = None,
    api_key: str | None = None,
) -> list[dict]:
    """顶层入口：fetch → score → filter → fallback → enrich → persist pool.json。"""
```

### 持久化

```
output/daily_batch/{date}/pool.json
```

内容：完整 ranked pool（含 score、signal sources），用于复现和 debug。

### CLI

```text
python scripts/heat_pool.py                         # 默认今天，min_count=10
python scripts/heat_pool.py --date 2026-07-05       # 指定日期
python scripts/heat_pool.py --min-count 15          # 至少 15 条
python scripts/heat_pool.py --dry-run               # 只打印 ranked list 不写文件
```

### 测试

`tests/test_heat_pool.py`：
- mock section API response（含 mostViewed + editorsPicks）
- 验证 score 计算正确（跨 section 重合加分）
- 验证 filter_seen 正确过滤
- 验证 fallback_newest 补齐逻辑
- 验证 enrich_descriptions 调用并填充 description

### 验收

```powershell
pytest tests/test_heat_pool.py -v
python scripts/heat_pool.py --dry-run
# 应打印 10+ 条 ranked news，含 score 和来源 section 列表
```

---

## Todo 7.2 · Daily Batch 编排器 + 断点续跑

**依赖**：7.1

**目标**：新建 `scripts/daily_batch.py`，管理批量管线执行和 stage+persona 级断点。

### 状态机

```json
// state/daily_batch_{date}.json
{
  "date": "2026-07-05",
  "pool_file": "output/daily_batch/2026-07-05/pool.json",
  "created_at": "2026-07-05T08:00:00Z",
  "items": [
    {
      "index": 0,
      "url": "https://...",
      "title": "...",
      "slug": "england-world-cup",
      "status": "done",
      "last_completed_stage": "compose",
      "completed_personas": ["The-Hero", "The-Sage", ...]
    },
    {
      "index": 1,
      "url": "https://...",
      "title": "...",
      "slug": "heatwave-england",
      "status": "persona",
      "last_completed_stage": "expand",
      "completed_personas": ["The-Hero", "The-Sage", "The-Explorer"]
    },
    {
      "index": 2,
      "url": "https://...",
      "title": "...",
      "slug": "byzantine-city",
      "status": "pending",
      "last_completed_stage": null,
      "completed_personas": []
    }
  ]
}
```

状态值：`pending` → `deconstruct` → `expand` → `persona` → `retrieve` → `compose` → `done`

### 产出目录

```
output/daily_batch/2026-07-05/
  ├── pool.json                        # 7.1 产出
  ├── 01-england-world-cup/
  │   ├── news.json
  │   ├── deconstruct.json
  │   ├── expand.json
  │   ├── personas/
  │   │   ├── The-Hero.json
  │   │   ├── The-Sage.json
  │   │   └── ...
  │   ├── retrieve.json
  │   └── briefing.md
  ├── 02-heatwave-england/
  │   └── ...
  └── ...
```

### 核心逻辑

```python
def run_daily_batch(
    *,
    date: str | None = None,
    resume: bool = False,
    min_count: int = DEFAULT_MIN_COUNT,
    run_options: RunOptions | None = None,
) -> None:
    """
    - 非 resume：调 fetch_heat_pool() → 初始化 batch_state → 开始逐条执行
    - resume：加载已有 batch_state，跳过 done 的 items，从断点继续
    - 每完成一个 stage 立即写 checkpoint
    - persona 阶段每完成一个 persona 更新 completed_personas
    """
```

### 恢复逻辑

1. 加载 `state/daily_batch_{date}.json`
2. 跳过 `status == "done"` 的 items
3. 对 `status != "pending"` 的 item：从 `last_completed_stage` 的下一个 stage 开始
4. persona stage：跳过 `completed_personas` 中已有的 persona

### CLI

```text
python scripts/daily_batch.py                           # 默认今天
python scripts/daily_batch.py --date 2026-07-05         # 指定日期
python scripts/daily_batch.py --resume                  # 断点恢复
python scripts/daily_batch.py --min-count 5             # 调整条数
python scripts/daily_batch.py --personas 2              # 开发模式（只跑 2 persona）
python scripts/daily_batch.py --skip-expand             # 跳过 expand
```

### 测试

`tests/test_daily_batch.py`：
- mock `run_daily_pipeline`（不真调 LLM）
- 验证初始化 batch_state 结构正确
- 验证正常执行后 checkpoint 更新
- **核心**：模拟中断（第 2 条 news 的 persona stage 挂掉），验证 resume 后从正确位置继续
- 验证 persona 级 checkpoint（跳过已完成的 persona）

### 验收

```powershell
pytest tests/test_daily_batch.py -v
# 断点恢复测试通过
```

---

## Todo 7.3 · 集成冒烟测试 [需人工验收]

**依赖**：7.2

**目标**：用真实 API key 跑一次小批量，验证端到端。

### 测试流程

1. 跑一次小批量：
   ```powershell
   python scripts/daily_batch.py --min-count 3 --personas 2
   ```

2. 验证产出：
   - `output/daily_batch/{date}/pool.json` 存在且含 score
   - `state/daily_batch_{date}.json` 所有 items status == "done"
   - 至少 1 条 news 产出了完整的 `briefing.md`

3. 断点恢复测试：
   - 跑到一半 Ctrl+C
   - 再 `python scripts/daily_batch.py --resume`
   - 验证从断点继续，不重跑已完成的

### 验收

人工检查 pool.json 的新闻质量（是否确实是热门新闻）+ briefing.md 内容合理性。

---

## 风险与约束

| 风险 | 缓解 |
|------|------|
| Guardian 免费 tier rate limit (12 req/s) | 32 section 请求间加 100ms sleep |
| mostViewed 全是老新闻，filter_seen 后为空 | fallback_newest 兜底 |
| 批量跑 10 条 × 12 persona = 120 次 LLM 调用 | `--personas N` 开发开关控成本 |
| 断点 state 文件损坏 | 每次写 checkpoint 先写 .tmp 再 rename |
| 现有 main.py 接口不够 | 只调 `run_daily_pipeline()` 函数，不走 CLI |

## SSOT

| 文档 | 用途 |
|------|------|
| `CONTEXT.md` | 热度池术语定义 + 总编职责更新 |
| `scripts/main.py::run_daily_pipeline()` | 单条管线接口（零改动） |
| `scripts/fetch_news.py` | 复用 `is_url_seen`, `mark_selected`, `extract_guardian_description` |
| Guardian Section API | `show-most-viewed=true` + `show-editors-picks=true` 返回格式 |