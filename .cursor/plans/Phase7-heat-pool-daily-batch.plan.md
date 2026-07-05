---
name: Phase7-heat-pool-daily-batch
overview: |
  实现热度池 (Heat Pool) 自动选题 + daily_batch.py 批量编排器 + 断点续跑。
  让系统能"跑一次全量日批"：从 Guardian 32 个 section 拉 mostViewed + editorsPicks，
  按 composite score 排序选 top-N(≥10)，逐条喂入现有管线，stage+persona 级断点续跑。
todos:
  - id: p7.1-heat-pool
    content: 7.1 · Heat Pool 采集与计分模块（scripts/heat_pool.py）
    status: completed
  - id: p7.2-daily-batch
    content: 7.2 · Daily Batch 编排器 + 断点续跑（scripts/daily_batch.py）
    status: completed
  - id: p7.3-mimo-parallel-baseline
    content: 7.3 · Mimo 2.5 Pro 并行设计与调优基线
    status: todo
  - id: p7.4-integration-smoke
    content: 7.4 · 集成冒烟测试 [需人工验收]
    status: completed
isProject: true
---

# Phase 7 · Heat Pool + Daily Batch 编排

## 背景

Phase 6 完成了单条 news 的端到端管线（`main.py`）。本 Phase 将其升级为"日批量"模式：
自动从 Guardian 热度信号选题 → 批量跑管线 → 断点续跑。

## 前置条件

| Phase | 交付物                                                  | 状态     |
| ----- | ------------------------------------------------------- | -------- |
| 5     | `fetch_news.py`（Guardian API + RSS + dedup）           | ✅ merged |
| 6     | `main.py` 端到端管线 + `render_briefing` + `RunOptions` | ✅ merged |

## 设计决策（grill session 2026-07-05）

| 决策       | 结论                                                 |
| ---------- | ---------------------------------------------------- |
| 术语       | 热度池 (Heat Pool)，见 CONTEXT.md                    |
| 总编职责   | 退出选题环节，只审终稿（CONTEXT.md 已更新）          |
| 架构       | 新增 `daily_batch.py` 编排器，`main.py` 保持单条语义 |
| 信号源     | mostViewed + editorsPicks，两信号独立入池            |
| 计分       | `sum(1/rank_per_section) + 0.5 * editorsPicks_count` |
| 正文补取   | rank 后 top-N 再逐条调 Content API 拿 bodyText       |
| 断点粒度   | stage 级 + persona 内部 checkpoint                   |
| 产出目录   | `output/daily_batch/{date}/` 独立结构                |
| 不够时回退 | 用 `order-by=newest` 补齐到 min_count                |
| sections   | 32 个内容 section 全拉                               |
| seen 过滤  | 排序后再过滤                                         |

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

## Todo 7.3 · 并行设计与调优基线

**依赖**：7.2

**SSOT**：执行本 TODO 前必须阅读 `docs/SSOT/mimo-2.5-pro-parallelism.md`，并以该文档作为参数、调参、恢复与验证口径的唯一来源。

**目标**：固化 daily_batch 的并行实现边界与默认值，确认 item / persona / 全局限流的分工与 baseline；不改 `heat_pool` 语义、不改 prompt、不改 `retrieve` 排序。

**执行边界**：仅收敛并行调度、恢复与观测口径；具体参数、测试矩阵、降级顺序、错误字段和命令以 SSOT 为准。

**验收口径**：完成后应能明确 baseline 拓扑、默认并发档位、恢复边界与需要记录的关键状态；不要求在本 TODO 内重复维护完整矩阵。

**人工验收阻断说明**：无人工验收阻断；若后续 smoke/tuning 需要人工确认，再按 7.4 处理。

---

## Todo 7.4 · 集成冒烟测试 [需人工验收]

**依赖**：7.3

**SSOT**：执行本 TODO 前必须先读 `7.3` 与 `docs/SSOT/mimo-2.5-pro-parallelism.md`，冒烟命令、矩阵、降级与恢复口径均以 SSOT 为准。

**目标**：用真实 API key 跑一次小批量，验证端到端与断点恢复；本 TODO 仅做冒烟确认，不扩写参数细节。

**执行边界**：冒烟执行前必须参考 7.3 与 SSOT；若出现 429 / timeout / retry 异常，按 SSOT 口径处理。

**验收口径**：能完成小批量跑通、产出文件齐全、`resume` 可从稳定 checkpoint 继续；冒烟命令与阈值不在 plan 内重复展开。

**人工验收阻断说明**：此 TODO 为 `[需人工验收]`；在人工验收通过前，不要标 complete、不要写 report、不要 merge。