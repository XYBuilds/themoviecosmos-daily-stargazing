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

3. **跑一次召回**
   ```powershell
   python scripts/retrieve.py --pseudo "..."
   ```
   肉眼检查匹配是否"有味道"。

4. **生成中文审核文案**
   ```powershell
   python scripts/copywriter.py --stage review --candidates <retrieve_output>
   ```
   为每部候选产出一段中文文案，写进简报供总编勾选。

5. **接 RSS**：`scripts/fetch_news.py`。

6. **端到端跑通**
   ```powershell
   python scripts/main.py --url <news_url>
   ```
   产物：`output/Daily_Briefing/2026-MM-DD.md`，在 Obsidian 中阅读、勾选文案。

7. **选定文案 → 多平台定稿（中/英）**
   ```powershell
   python scripts/copywriter.py --stage publish --selected <copy>
   ```
   产物：`output/Daily_Briefing/2026-MM-DD_copy.md`。

8. **切全量索引**：把 `--csv` 换成 `data/full/TMDB_all_movies.csv`。

---

## 设计原则备忘

* **embedding 不翻译**：直接用 TMDB 英文原文；库为全英文，故检索侧 pseudo 也统一英文，同分布召回更稳。
* **语种分层**：检索=英文，审核稿=中文，定稿=中+英（MVP）。三层各司其职，互不干扰。
* **不引入 FAISS**：6 万级 NumPy `@` + `argpartition` 已是毫秒级。
* **去实体化是核心质量门**：所有 Persona 共享 `prompts/_shared/deentification_rules.md`。
* **跨 Agent 撞车 = 强信号**：同一部电影被多个视角召回，要在简报里聚合展示。
* **人类总编不可替代**：MVP 不做自动甄选与自动发布，总编从中文文案里勾选后再生成平台版本。
