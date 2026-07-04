---
name: Phase6-main-integration
overview: |
  实现 main.py 端到端管线与 render_briefing 共享渲染模块。
  重写说明（2026-07-04）：对齐当前实际代码架构 —— 生产管线走 rewrite.py (persona pipeline)
  而非 agents.py (DEAD FLOW)；C1/C2 在 compose.py 而非虚构的 copywriter.py。
  追加 Phase 5 遗留债务清理（开发开关、judge 分布对齐留口）。
todos:
  - id: p6-debt-dev-switch
    content: 6.0 · Phase5 债务：开发快捷开关（--personas N / --skip-expand / --judge-topk K）注入 run_eval + main 共用
    status: completed
  - id: p6-render-module
    content: 6.1 · 抽离 render_briefing.py：从 run_eval.py 提取可复用渲染函数（reality/candidates/errors/oracle），eval 与 main 单点维护
    status: pending
  - id: p6-main-pipeline
    content: 6.2 · main.py 日报管线：news → deconstruct → expand → persona_pipeline → retrieve → C1 → Daily_Briefing.md
    status: pending
  - id: p6-publish
    content: 6.3 · main publish 子命令：总编勾选后触发 C2 → YYYY-MM-DD_copy.md
    status: pending
  - id: p6-docs
    content: 6.4 · README 更新 + plumbing 说明 + run_eval 对齐 render_briefing 调用
    status: pending
isProject: true
---

# Phase 6 · Main（端到端集成） — 2026-07-04 重写

## 重写动因

旧计划（2026-06）基于以下错误假设：
1. 引用 `agents.py`（4 persona / A1-A7）作为生产管线 → **实际已 DEAD FLOW（ADR-0011 D3）**
2. 引用 `copywriter.py` → **不存在**，C1/C2 实际在 `compose.py`
3. 省略 `deconstruct`（A0）和 `expand` 步骤 → 真实管线必须走这两步
4. `render_briefing.py` 从未创建

本稿以 `run_eval.py`（679行，已验证可跑）的管线顺序为 SSOT，差异仅在输出目录和 C1/C2 追加。

---

## 前置条件

| Phase | 交付物                                           | 状态     |
| ----- | ------------------------------------------------ | -------- |
| 0     | 索引 + `scripts/lib`（paths / env / llm）        | ✅ merged |
| 1     | `personas.py` + `rewrite.py`（persona pipeline） | ✅ merged |
| 2     | `retrieve.py`（`retrieve_from_agents`）          | ✅ merged |
| 3     | `compose.py` C1/C2 + judge 闸门                  | ✅ merged |
| 5     | `fetch_news.py`（Guardian API + RSS）            | ✅ merged |

## 真实生产管线（对齐 run_eval.py）

```
                                      ┌──────────────────────────────┐
news(JSON) → deconstruct(A0) → expand → persona_pipeline(N persona) → retrieve → C1(compose.run_review) → render
                                      └──────────────────────────────┘
                                                  ↓
                                            Daily_Briefing.md
```

关键 import 路径（`run_eval.py` 已验证）：

```python
from scripts.agents import load_news_from_file, news_to_dict, annotate_fragment_ids, load_deconstruction_from_file
from scripts.expand import run_expansion
from scripts.extract import run_deconstruct
from scripts.retrieve import retrieve_from_agents
from scripts.rewrite import list_persona_ids, run_persona_pipeline, pipeline_result_to_dict
from scripts.compose import run_review, run_publish   # C1 / C2
```

## Phase 5 挂起债务（6.0 一并解决）

| 债务                    | 来源                         | 处置                                        |
| ----------------------- | ---------------------------- | ------------------------------------------- |
| `--personas N` 快跑开关 | Phase5 plan "小快灵开发开关" | 加到 run_eval + main 共用参数               |
| `--skip-expand`         | 同上                         | expand 步骤可选跳过（debug 用）             |
| `--judge-topk K`        | 同上                         | 限制 retrieve top-k（默认仍 2）             |
| judge 分布重对齐        | Phase5 plan                  | 留接口占位（`--judge-profile`），不实装逻辑 |

---

## Todo 6.0 · 开发快捷开关

**目标**：在不增加模块耦合的前提下，让管线可以被截断/加速，服务于日常开发和 CI。

### 设计

```python
# scripts/lib/run_options.py（新增，纯数据 dataclass）
@dataclass(frozen=True)
class RunOptions:
    persona_limit: int | None = None      # --personas N：只跑前 N 个 persona
    skip_expand: bool = False             # --skip-expand：跳过 P-Expand
    judge_topk: int = 2                   # --judge-topk K
    force: bool = False                   # --force：覆盖已有同日输出
```

- `run_eval.py` 和 `main.py` 都从 CLI 解析后传入此对象
- 不改变现有函数签名，仅在调用方做 slice/skip

### 验收

```powershell
python scripts/run_eval.py --news-file tests/sample_news.json --personas 2 --skip-expand
# 应 skip expand，只跑 2 个 persona，正常产出 candidates
```

---

## Todo 6.1 · `render_briefing.py`

**目标**：从 `run_eval.py` 的 `_format_*` 函数族抽取为共享模块，main 和 eval 各自调用、单点维护。

### 模块边界

```python
# scripts/lib/render_briefing.py

def render_reality(news: dict, run_id: str) -> str: ...
def render_candidates(candidates: list[dict], *, include_score=False, copies: dict|None=None) -> str: ...
def render_errors(errors: list[dict]) -> str: ...
def render_oracle_appendix(a1_oracle: dict, oracle_comparison: dict) -> str: ...
def render_funnel(funnel: dict) -> str: ...
def render_meta_footer(meta: dict) -> str: ...

# 组合入口
def render_daily_briefing(
    news: dict,
    retrieve_payload: dict,
    *,
    review_copies: list[dict] | None = None,  # C1 输出
    mode: Literal["prod", "eval"] = "prod",
    run_id: str = "",
) -> str: ...
```

### 改动范围

1. 新建 `scripts/lib/render_briefing.py`
2. `run_eval.py` 的 `_format_reality_body` / `_format_candidates_markdown` / `_format_errors` 等迁入，原位替换为 import
3. 候选渲染新增 `copies` 参数槽位（eval 模式不传、prod 模式传 C1 结果）
4. **顺带修复**：`_format_run_index`（→ `render_run_index`）硬编码 `[[agents/A2]] [[agents/A4]] [[agents/A7]] [[agents/A1]]` 四行死链（实测基线 `run.md` 已验证，指向不存在的 12-persona 产物），改为按实际 `outputs`/`persona_payloads` 动态生成 persona 链接列表

### 验收

```powershell
python scripts/run_eval.py --news-file tests/sample_news.json
# 与基线 diff：output/Eval/phase6-baseline/（2026-07-04 实跑，12 persona 全部成功，19 候选，exit_code 0）
# candidates.md / reality.md / facts.md 应 bit-for-bit 一致
# run.md 的 persona 链接应改为实际 12 persona 列表（非 A2/A4/A7/A1 死链）
```

---

## Todo 6.2 · `main.py` 日报管线

**依赖**：6.0 + 6.1

### CLI 设计

```text
python scripts/main.py --news-file output/picked_news.json
python scripts/main.py --url https://... --title "..." --description "..."
python scripts/main.py --pick 3                        # 调 fetch_news 选第3条
python scripts/main.py --news-file ... --date 2026-07-04
python scripts/main.py --news-file ... --no-copy       # 跳过 C1（调试）
python scripts/main.py --news-file ... --personas 2    # 开发快捷开关
```

无参数时打印用法退出。

### 管线步骤

```
1. 解析 news → news dict
2. deconstruct(A0)                  # 可选读缓存 state/decon/{date}.json
3. expand（可 --skip-expand）
4. persona_pipeline × N             # 可 --personas 限制
5. retrieve_from_agents
6. if not --no-copy: compose.run_review(retrieve, news)  →  review_copies
7. render_daily_briefing(news, retrieve, copies)  →  output/Daily_Briefing/{date}.md
```

### Markdown 输出模板

```markdown
# 每日星轨观测 · {date}

## 现实波澜
- **title**: ...
- **source** / **pub_time**: ... / ...
- **summary**: ...

## 候选星轨（共 N 部）
### {title} ({release_year})  ·  命中视角 [{triggered_by}]
- **相似度**: 0.xx
- **genres** / **language**: ... / ...
- **overview**: ...
- **命中来源**: {search_unit_kinds}
- **跳转**: {movie_url}
- **中文文案（C1 审核稿）**: ...     <!-- 有 copy 时 -->
- **选用**: ☐

## errors
...

## 附录 · A1 Reality Recorder（held-out oracle）
- A1 召回但未进生产池: ...
- 生产池独有: ...

## 脚注
- meta: ...
```

### 关键约束

- `movie_url` 直接用 retrieve 输出，**不手拼**
- A1 **严格隔离**：只出现在 oracle 附录，不进候选、不给 C1、不可勾选
- candidate 字段容错（poster_path/overview 可为空）

### 验收

```powershell
python scripts/main.py --news-file tests/sample_news.json --no-copy --personas 2
# 检查 output/Daily_Briefing/<today>.md 结构正确
python scripts/main.py --news-file tests/sample_news.json --personas 2
# C1 文案出现在候选下
```

---

## Todo 6.3 · `publish` 子命令

**依赖**：6.2

### CLI

```text
python scripts/main.py publish --date 2026-07-04 --tmdb-id 157336 --selected-file path.txt
python scripts/main.py publish --date 2026-07-04 --selected-copy "《...》..."
```

### 实现

1. 从 `output/Daily_Briefing/{date}.md` 或 `--news-file` 加载当日语境
2. 从 candidates.json（写在日报同目录）定位 tmdb_id 对应的 candidate
3. 调 `compose.run_publish(candidate, news)` → C2 定稿
4. 写 `output/Daily_Briefing/{date}_copy.md`

### 验收

- `_copy.md` 含中英文两节 + 链接
- 与 Phase 4 C2 输出口径一致

---

## Todo 6.4 · 文档与对齐

**依赖**：6.2

### 交付

1. `README.md` 更新「端到端工作流」：
   ```
   fetch_news → 手挑 --pick N
   main.py --pick N (或 --news-file)
   # Obsidian 勾选候选
   main.py publish --date ... --tmdb-id ...
   ```
2. 说明 `run_eval.py` vs `main.py` 区别（eval 写 output/Eval/，生产写 Daily_Briefing/）
3. `run_eval.py` 改用 `render_briefing` 模块后删除内联渲染函数（6.1 完成时已做）
4. plumbing 注释：小索引仅测通，非日更

---

## 风险与约束

| 风险                                | 缓解                                               |
| ----------------------------------- | -------------------------------------------------- |
| 12 persona + C1 全跑费时费钱        | `--personas N` + `--no-copy` 开发开关              |
| 同日重复跑覆盖                      | `--force` 或默认报错提示                           |
| A1 泄入生产候选                     | retrieve 代码层已硬隔离，render 侧再做 filter 断言 |
| 渲染迁移后 eval 回归                | 6.1 验收要求 bit-parity                            |
| compose.run_review 对 news 格式敏感 | 走 `news_to_dict` 统一输出                         |

## SSOT

| 文档                                              | 用途                                 |
| ------------------------------------------------- | ------------------------------------ |
| `scripts/run_eval.py`                             | 管线步骤和 import 路径的唯一参考实现 |
| `scripts/retrieve.py` `retrieve_from_agents`      | 输出契约真实来源                     |
| `scripts/compose.py` `run_review` / `run_publish` | C1/C2 接口                           |
| ADR-0009                                          | search unit / candidate 字段口径     |
| ADR-0011                                          | agents.py DEAD FLOW 定性             |