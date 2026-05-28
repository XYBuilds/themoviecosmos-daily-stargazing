# 电影宇宙 · 每日星轨观测（Daily Stargazing）

> 一个「数字文化天文台」：每日抓取新闻热点，由 7 个人格各异的 LLM Agent 改写为去实体化的「伪剧情简介」，在 6 万部电影的纯文本向量库中召回与之结构共振的电影，由人类总编在 Obsidian 中拍板，引流至 [themoviecosmos.com](https://themoviecosmos.com) 的 3D 电影宇宙。

PRD 见 [`docs/SSOT/电影宇宙「每日星轨观测」系统 PRD.md`](docs/SSOT/电影宇宙「每日星轨观测」系统%20PRD.md)。

---

## MVP 目标

> 验证「单条新闻 → 多 Agent 写 pseudo-overview → 向量召回电影」这条链是否可行。

MVP 范围内**只跑 3 个 Persona**（A2 社会学家 / A4 神话学者 / A7 混沌理论家），先看链路是否真有差异化召回价值，再扩到 7 个。

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
│   └── A*.md        # Persona 文档
├── scripts/         # build_index / fetch_news / agents / retrieve / main
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

1. **构建索引（先用 20 行样本）**
   ```powershell
   python scripts/build_index.py --csv data/subsample/TMDB_all_movies_random20.csv
   ```
   产物：`data/index/embeddings.npy` + `data/index/meta.parquet`。

2. **跑一次 Agent**（先手喂一条新闻 JSON）
   ```powershell
   python scripts/agents.py --news-file tests/sample_news.json
   ```
   肉眼检查 3 段 pseudo-overview 的"去实体化质量"与"风格差异度"。

3. **跑一次召回**
   ```powershell
   python scripts/retrieve.py --pseudo "..."
   ```
   肉眼检查匹配是否"有味道"。

4. **接 RSS**：`scripts/fetch_news.py`。

5. **端到端跑通**
   ```powershell
   python scripts/main.py --url <news_url>
   ```
   产物：`output/Daily_Briefing/2026-MM-DD.md`，在 Obsidian 中阅读。

6. **切全量索引**：把 `--csv` 换成 `data/full/TMDB_all_movies.csv`。

---

## 设计原则备忘

* **embedding 不翻译**：直接用 TMDB 原文，依赖多语言模型对齐。
* **不引入 FAISS**：6 万级 NumPy `@` + `argpartition` 已是毫秒级。
* **去实体化是核心质量门**：所有 Persona 共享 `prompts/_shared/deentification_rules.md`。
* **跨 Agent 撞车 = 强信号**：同一部电影被多个视角召回，要在简报里聚合展示。
* **人类总编不可替代**：MVP 不做自动甄选，简报最多列出候选 + 跳转链接。
