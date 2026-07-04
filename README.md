# 电影宇宙 · 每日星轨观测（Daily Stargazing）

> 一个「数字文化天文台」：每日抓取新闻热点，由 7 个人格各异的 LLM Agent 改写为去实体化的**英文**「伪剧情简介」，在 6 万部电影的纯文本向量库中召回与之结构共振的电影；再**用中文为每部候选写社媒文案供总编挑选审核**，选定后**按平台生成对应语言版本（MVP 仅中英）**，引流至 [themoviecosmos.com](https://themoviecosmos.com) 的 3D 电影宇宙。

PRD 见 [`docs/SSOT/电影宇宙「每日星轨观测」系统 PRD.md`](docs/SSOT/电影宇宙「每日星轨观测」系统%20PRD.md)。

---

## MVP 目标

> 验证「单条新闻 → 多 Agent 写英文 pseudo-overview → 向量召回电影 → 中文文案供审核」这条链是否可行。
>
> **语种约定**：电影库为全英文，故检索侧（Persona prompts + pseudo）统一用英文；召回后用中文写审核文案；定稿按平台产出中、英两版。

MVP 范围内跑 **3 个创作 Persona**（A2 社会学家 / A4 神话学者 / A7 混沌理论家）**+ 1 个基线 A1 现实记录员（对照组）**。A1 只做去实体化白描、不做隐喻，用来回答「创作视角召回的电影是否真比平铺直叙更妙」；它在简报里标 `[baseline]`，不计入跨 Agent 撞车强信号。确认有差异化召回价值后再扩到 7 个创作视角。

非 MVP 事项见 PRD §12。

---

## 目录结构

```
.
├── data/
│   ├── subsample/   # 20 行样本（已有，跑通用）
│   ├── full/        # 60k 全量（gitignore）
│   └── index/       # embeddings.npy + meta.parquet（gitignore）
├── docs/SSOT/       # PRD 单一可信源
├── prompts/
│   ├── _shared/     # 公共硬规则 + 输出契约
│   ├── A*.md        # 英文 Persona：A1 基线 + A2/A4/A7 创作视角
│   └── C*.md        # 文案：C1 中文审核稿 / C2 中英多平台定稿
├── scripts/         # build_index / fetch_news / agents / retrieve / copywriter / main
├── output/Daily_Briefing/   # 每日简报（Obsidian 阅读入口）
└── state/           # URL/标题去重状态
```

---

## 环境准备

### 1. Python 与虚拟环境

建议 Python 3.11 ~ 3.12（`sentence-transformers` + `torch` 在 3.14 上的 wheel 还不稳定，等生态跟上再升）。

```powershell
# 用 py launcher 指定版本
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**带进度条 + 粗略 ETA（推荐）**

若直接运行 `.ps1` 报「未数字签名 / ExecutionPolicy」错误，请用下面任一方式（**不要改全局策略也可用**）：

```cmd
install_env.cmd
```

或：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_env.ps1
```

仅当前 PowerShell 窗口临时放开（关闭终端后失效）：

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\scripts\install_env.ps1
```

监视模式（另开终端跑 `pip` 时，看包清单 + 粗略 ETA）：

```cmd
install_env.cmd -MonitorOnly
```

> 如果暂时只装了 3.14，先用它装；若安装 `sentence-transformers` / `torch` 失败，再切到 3.12。

### 2. 环境变量

```powershell
Copy-Item .env.example .env
# 编辑 .env，填入 MIMO_* 或 DEEPSEEK_* 的 API Key
```

---

## MVP 执行顺序（每步独立可验证）

1. **构建索引（全量片单，ADR-0001 复用向量）**
   ```powershell
   python scripts/build_index.py
   ```
   产物：`data/index/embeddings.npy` + `data/index/meta.parquet`（59,341 行）。  
   仅调试索引管线时可用 `--csv data/subsample/TMDB_all_movies_random20.csv`。

2. **跑一次 Agent**（从仓库根目录；需已配置 `.env` 中 `MIMO_*` 或 `DEEPSEEK_*`）
   ```powershell
   python scripts/smoke_llm.py --provider mimo
   python scripts/agents.py --news-file tests/sample_news.json
   python scripts/agents.py --news-file tests/sample_news.json --out output/phase1_agents.json
   python scripts/agents.py --news-file tests/sample_news.json --agents A2,A4
   ```
   肉眼检查：4 段**英文单段** pseudo-overview（A2/A4/A7 + 基线 A1）；A1 更平实、创作视角口吻可区分；无明显未去实体化专名（或 JSON 中已有 `deentify_warning`）。

3. **跑一次召回**（依赖步骤 1 索引 + 步骤 2 `phase1_agents.json`）
   ```powershell
   python scripts/retrieve.py --pseudo "A heat wave strains the grid..." --agent-id A2
   python scripts/retrieve.py --agents-json output/phase1_agents.json --out output/phase2_retrieve.json
   python -c "import json; d=json.load(open('output/phase2_retrieve.json')); print(len(d['candidates']), 'candidates')"
   ```
   在全量 59,341 索引上肉眼检查：候选与 pseudo 至少有表层相关，便于进入 Phase 3 闸门评分。

4. **验证闸门（The Bet）** — N=10 手挑新闻、填共振分、汇总判定；详见 [`docs/eval-the-bet.md`](docs/eval-the-bet.md)。
   ```powershell
   python scripts/run_eval.py --news-file tests/sample_news.json
   python scripts/summarize_eval.py --dir output/Eval
   ```

5. **生成中文审核文案（C1 审核稿）**
   ```powershell
   python scripts/compose.py --stage review `
     --retrieve-json output/phase2_retrieve.json `
     --news-file output/Eval/phase3.11/full-batch-20260613-3117/01-grid-outage/reality.json `
     --judge-scores output/Eval/phase3.11/full-batch-20260613-3117/llm-judge-scores-thinking-enabled.json `
     --out output/copy_review.json
   ```
   为每部候选产出一段中文文案。产物：`output/copy_review.json`（结构化）+ `output/copy_review.md`（Obsidian 可读候选块，默认与 `--out` 同名 `.md`；也可用 `--md-out` 显式指定）。总编在 Obsidian 中肉眼审核、手动勾选 `✅ 选用`（A1/oracle 不入候选）。

6. **接 RSS / Guardian API**：`scripts/fetch_news.py`（默认 `--provider guardian-api`，Guardian 各 section 默认全放行，不需要手挑）。

7. **端到端跑通（`main.py` 生产管线）**
   ```powershell
   python scripts/main.py --pick 3
   # 或
   python scripts/main.py --news-file output/picked_news.json
   # 或
   python scripts/main.py --url <news_url> --title "..." --description "..."
   ```
   管线：`resolve_news → deconstruct(A0) → expand(可 --skip-expand) → persona_pipeline×N(可 --personas 限制) → retrieve → (可选 --no-copy) compose.run_review(C1) → build_daily_briefing`。  
   产物：`output/Daily_Briefing/{date}.md` + 同目录 `{date}_candidates.json`（date 默认今天 UTC，可用 `--date` 覆盖；同日重复跑默认报错，需 `--force` 覆盖）。在 Obsidian 中阅读 `.md`、人工审阅候选与 C1 中文文案。

8. **选定文案 → 多平台定稿（中/英）**
   ```powershell
   python scripts/main.py publish --date 2026-07-04 --tmdb-id 157336
   ```
   从 `{date}_candidates.json` 按 `tmdb_id` 定位候选，调用 `compose.run_publish()`（C2）生成中文发布正文，与原始英文新闻源配对写入产物（C2 按设计只产出单语中文正文，不做英文回译）。产物：`output/Daily_Briefing/{date}_copy.md`。（`main.py publish` 子命令已由 Phase 6.3 交付合并，参数以 `python scripts/main.py publish --help` 为准。）

9. **切全量索引**：把 `--csv` 换成 `data/full/TMDB_all_movies.csv`。

---

## `run_eval.py` vs `main.py`

两者共享同一条底层管线（`deconstruct → expand → persona_pipeline → retrieve`），也共享 `scripts/lib/render_briefing.py` 里的候选/现实波澜/errors 渲染函数（Phase 6.1 从 `run_eval.py` 抽出，`run_eval.py` 现在从该模块 import，未再内联维护这些渲染逻辑），但用途和产物目录不同：

- **`run_eval.py`**：面向开发调试与回归验证，产物写 `output/Eval/{run_id}/`（`reality.md`/`facts.md`/`candidates.md`/`errors.md`/`run.md` 等一组文档），用于「验证闸门（The Bet）」之类的离线评测，不进入生产日报流程。`run.md` 里的 persona 链接是按当次运行实际参与的 persona 列表动态生成的。
- **`main.py`**：面向生产日报流程，产物写 `output/Daily_Briefing/{date}.md` + `{date}_candidates.json`，并额外接入 C1 中文审核文案（`--no-copy` 可跳过调试）和 A1 held-out oracle 附录。

两者都支持 `--personas N`（只跑前 N 个 persona）/ `--skip-expand`（跳过 P-Expand）/ `--judge-topk K`（retrieve 阶段每个 pseudo 的 top-k）/ `--force`（覆盖已有同 run/同日产物）这组 Phase 6.0 引入的开发快捷开关。

## plumbing 说明：索引/小规模脚本仅用于测通

以下脚本是管线搭建期的联调/验证工具，**不是日更生产脚本**，日常生产只走 `scripts/main.py`：

- `scripts/build_index.py`：构建 `data/index/embeddings.npy` + `meta.parquet`，只在索引改动或首次搭建环境时跑一次；日常生产不重复调用。
- `scripts/smoke_llm.py`：仅测试 LLM Provider（MIMO/DeepSeek）连通性，不产出任何业务数据。
- `scripts/agents.py`：旧版 4-persona（A1/A2/A4/A7）pseudo 生成路径，已被 `personas.py` + `rewrite.py` 的 persona pipeline 取代（ADR-0011 D3 判定为 DEAD FLOW），仅保留用于历史对照/测试 fixture，不接入 `main.py`。
- `scripts/retrieve.py --pseudo ...` 单条命令行调用：仅用于手工验证召回是否连通，生产链路走 `retrieve_from_agents()` 函数调用，不走这个 CLI 入口。

---

## 新闻抓取与手挑（fetch_news）

`fetch_news.py` 默认 `--provider guardian-api`：按黑名单过滤后的一批宽泛 section（`GUARDIAN_API_SECTIONS`，剔除 about/help/weather 等非事件类栏目）自动拉取候选，**不需要总编逐条手挑才能继续**——`main.py --pick N` 可以直接从这批自动放行的候选里按序号选一条进入生产管线。

`--pick` 更多用作调试期的手工干预开关：查看/临时锁定某一条候选、或在自动化之外做人工复核时使用：

1. 查看带序号候选列表：
   ```powershell
   python scripts/fetch_news.py
   ```
2. 记下要使用的序号，例如 `N`。
3. 导出选中的单条新闻：
   ```powershell
   python scripts/fetch_news.py --pick N --out-json output/picked_news.json
   ```
4. 将 `output/picked_news.json` 交给后续链路：
   ```powershell
   python scripts/main.py --news-file output/picked_news.json
   python scripts/run_eval.py --news-file output/picked_news.json
   ```

也可以跳过导出 JSON 这一步，让 `main.py`/`fetch_news.py` 各自直连 Guardian API 按序号选取：
```powershell
python scripts/main.py --pick 3
```

需要留档候选池给总编浏览时，可把去重后的完整候选列表写到 `state/`：

```powershell
python scripts/fetch_news.py --out state/news_pool_2026-05-29.json
```

`state/news_pool_*.json` 是候选列表；`output/picked_news.json` 是单条 news JSON，字段与 `--news-file` 契约一致：`title`、`description`、`pub_time`、`source_name`、`url`。

若 RSS 不可用或要临时旁路某条链接，可直接提供 URL：

```powershell
python scripts/fetch_news.py --url https://example.com/article --title "新闻标题" --description "新闻摘要" --out-json output/picked_news.json
```

`--url` 会先尝试解析链接；解析不出必填字段时，需要同时补 `--title` 与 `--description`，可选补 `--source-name`、`--pub-time`。中国网络环境下部分 feed 可能超时；可换 feed、使用 `--url` 旁路，或手工准备同契约 JSON 后交给 `main.py --news-file` / `run_eval.py --news-file`。

---

## 设计原则备忘

* **embedding 不翻译**：直接用 TMDB 英文原文；库为全英文，故检索侧 pseudo 也统一英文，同分布召回更稳。
* **语种分层**：检索=英文，审核稿=中文，定稿=中+英（MVP）。三层各司其职，互不干扰。
* **不引入 FAISS**：6 万级 NumPy `@` + `argpartition` 已是毫秒级。
* **去实体化是核心质量门**：所有 Persona 共享 `prompts/_shared/deentification_rules.md`。
* **跨 Agent 撞车 = 强信号**：同一部电影被多个视角召回，要在简报里聚合展示。
* **人类总编不可替代**：MVP 不做自动甄选与自动发布，总编从中文文案里勾选后再生成平台版本。
