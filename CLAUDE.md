# CLAUDE.md

本文件为 Claude Code（claude.ai/code）在本仓库工作时的指引。内容整合自 `.cursor/rules/*.mdc`（三条 `alwaysApply` 工作流规则）与项目文档（`README.md` / `CONTEXT.md` / `docs/`）。

---

## 项目是什么

**电影宇宙 · 每日星轨观测（Daily Stargazing）** —— 一个「数字文化天文台」。核心链路：

> 每日抓取新闻热点 → 多个人格各异的 LLM Agent（Persona）把新闻**去实体化**改写为**英文**「伪剧情简介」→ 在 **59,341 部**电影的纯文本向量库中召回与之「共振」的电影 → 用**中文**为候选写社媒审核文案供总编挑选 → 选定后按平台生成对应语言版本（MVP 仅中/英）→ 引流至 [themoviecosmos.com](https://themoviecosmos.com) 的 3D 电影宇宙。

- **SSOT（单一可信源）**：`docs/SSOT/电影宇宙「每日星轨观测」系统 PRD.md`
- **术语表**：`CONTEXT.md`（共振/去实体化/中性通道/Persona/热度池/片单 等核心概念，改动语义前必读）
- **架构决策**：`docs/adr/0001..0015`（每次重大设计变更都有对应 ADR）

**语种分层（重要设计约束）**：检索侧 = 英文（电影库全英文，pseudo 同分布召回更稳）；审核稿 = 中文；定稿 = 中+英。三层各司其职，勿混用。

---

## ⚠️ 工作流规则（来自 `.cursor/rules/`，始终生效）

本项目按 **Phase → TODO** 分解推进，以下三条规则对每个 TODO 无条件适用。

### 1. 单 TODO 标准流水线（6 步，按序执行）

对计划（`.cursor/plans/Phase*.md` / `.yaml`）中每个 TODO：

```
[1.Check&Branch] → [2.Code&Test] → [3.Commit] → [4.Update Plan] → [5.Write Report] → [6.Merge]
```

1. **分支管理**：命名 `feat/phase[N.N.N...]-[todo]`（例 `feat/phase5.3.2-fetch-news`）。检出来源见规则 2。
2. **执行与本地验证**：写符合架构、高内聚低耦合的代码；完成后**必须主动在终端运行**相关测试/构建命令（如 `pytest`），确认无 regression。
3. **提交（Conventional Commits）**：`<type>(<scope>): <pN.N>-<description>`
   - 例：`feat(news): p5.1-implement-custom-fetcher-for-rss-feeds` / `fix(validation): p3.2-correct-threshold-index-range`
4. **状态标记**：提交后立即改对应 `.cursor/plans/Phase*.plan.md` 的 frontmatter `todos:` 列表，把该项（按 `id: pN.N-slug` 定位）`status: todo` 改为 `status: complete`（是 YAML `status:` 字段，**非** `[ ]`/`[x]` 复选框）。此步 + 第 5 步通常合并为一个 `docs(<scope>): pN.N-...-report` 提交。
5. **交付报告**：写到 `docs/reports/Phase[N.N.N...]-[todo-name]-report.md`。模板四段：`改动范围(Scope) / 技术实现(Implementation) / 本地验证结果(Verification) / 潜在影响或技术债(Technical Debt & Caveats)`。
6. **合并主干（GitHub PR）**：`git push -u origin <branch>` → `gh pr create`（目标 `main`）→ 在 GitHub **Create a merge commit**（`--no-ff`，保留分支拓扑）→ **Delete branch** → 本地 `git checkout main && git pull` → `git branch -d <branch>`。
   - 第 4–6 步受下方「人工验收阻断」约束。

### 2. Phase 依赖与顺序执行

Phase 之间有依赖，**必须严格顺序**：

- 前一个 Phase 未**完全 complete** 且未**合并入 `main`** 之前，**禁止**启动或预研后续 Phase。
- **新 TODO 分支检出来源**：
  - 前置 Phase 已合并入 `main` → 从最新 `main` 检出。
  - 前置 Phase 已开发完但**尚未合并**（等待人工验收中）→ 为不阻塞，从前置 Phase 的**最新开发分支**检出，并在交付报告中**记录分支继承关系**（基于哪个分支、对应哪个 TODO）。

### 3. 暂停与人工验收阻断

遇到以下任一情况，**立即停止**自动化，**保留现场**，输出挂起信息并等待用户指令：

- **需要人工验收**：Plan 标注或执行中出现 `[需人工验收]` 步骤。人工通过前**不要标 complete、不要写 report、不要合并**。
- **非预期编译/测试错误**：尝试修复 **2 次**后仍未成功。
- **关键决策冲突**：Plan 要求与实际代码/已有 API 冲突，或 Plan 信息缺失、模糊。

**挂起输出格式（严格采用）**：

```
⚠️ [PAUSED] 任务已挂起，等待人工验收

当前状态：已完成 Phase [N.N.N...] 的 [TODO Name] 代码编写与本地测试。
改动分支：feat/phase[N.N.N...]-[todo-name]
待验收内容：[简述需要用户肉眼/手动测试的内容]

请输入指令：输入 "approve" 继续后续的"状态标记-报告生成-合并"流程，或输入你的调整意见。
```

收到 `approve` 后，继续流水线第 4–6 步（状态标记 → 报告 → 合并）。

---

## 环境与常用命令

**Python**：建议 3.11 ~ 3.12（`sentence-transformers` + `torch` 在更高版本 wheel 尚不稳）。Shell 为 **PowerShell（Windows）**。

```powershell
# 安装环境
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
# 或（带进度条，绕过 ExecutionPolicy）：install_env.cmd

# 环境变量：复制模板后填 MIMO_* 或 DEEPSEEK_* 的 API Key
Copy-Item .env.example .env
```

**测试**（无 pytest 配置文件，直接跑）：

```powershell
pytest                      # 全量
pytest tests/test_main_pipeline.py   # 单文件
```

**生产管线（日常只走 `main.py`）**：

```powershell
python scripts/main.py --pick 3                       # 从热度池按序号选一条跑
python scripts/main.py --news-file output/picked_news.json
python scripts/main.py --url <url> --title "..." --description "..."
python scripts/main.py publish --date 2026-07-04 --tmdb-id 157336   # 选定候选 → 多平台定稿(C2)
```

管线阶段：`resolve_news → deconstruct(A0) → expand → persona_pipeline×N → retrieve → compose.run_review(C1) → build_daily_briefing`。产物写 `output/Daily_Briefing/{date}.md` + `{date}_candidates.json`。

**开发/评测（The Bet 闸门，非生产）**：`python scripts/run_eval.py --news-file tests/sample_news.json` → `python scripts/summarize_eval.py --dir output/Eval`，产物写 `output/Eval/{run_id}/`。`run_eval.py` 与 `main.py` 共享底层管线，仅用途/产物目录不同。

**联调 plumbing（非日更，仅搭建期/首次跑一次）**：`build_index.py`（建 `data/index/`）、`smoke_llm.py`（测 Provider 连通）、`agents.py`（旧 4-persona 路径，DEAD FLOW，仅留作 fixture）、`retrieve.py --pseudo`（手工验召回）。

---

## 目录结构

```
.
├── .cursor/
│   ├── rules/        # 本文件顶部三条工作流规则的原始 .mdc（alwaysApply）
│   └── plans/        # Phase*.md/.yaml 计划：TODO 清单与状态标记
├── data/
│   ├── subsample/    # 20 行样本（跑通用）
│   ├── full/         # 60k 全量（gitignore）
│   └── index/        # embeddings.npy + meta.parquet（gitignore）
├── docs/
│   ├── SSOT/         # PRD 单一可信源 + 各契约
│   ├── adr/          # 0001..0015 架构决策记录
│   └── reports/      # 交付报告 Phase[N]-[todo]-report.md
├── prompts/
│   ├── _shared/      # 公共硬规则：去实体化/输出契约/编剧契约/共振定义
│   ├── personas/     # 12 荣格原型 Persona 卡（The-Hero、The-Sage…）
│   └── *.md          # 编排 prompt：extract(A0)/compose_review(C1)/compose_publish(C2)/baseline_oracle(A1)
├── scripts/          # 管线脚本；scripts/lib/ 为公共库(env/llm/paths/render_briefing/run_options)
├── review_panel/     # 总编审核面板（build_data/publish_adapter/serve + index.html）
├── output/           # 简报/评测产物（gitignore）
├── state/            # URL/标题去重状态、候选池 news_pool_*.json（gitignore）
└── tests/            # pytest；fixtures 在 tests/*_fixtures/、sample_news.json
```

---

## 设计原则备忘（改动前对照 `CONTEXT.md` 术语表）

- **embedding 不翻译**：直接用 TMDB 英文原文；检索侧 pseudo 也统一英文。
- **向量召回 = 表层匹配器**：检索被**有意**设计成只做表层相似度；系统的「智能」全在 Persona prompts。
- **去实体化是核心质量门**：所有 Persona 共享 `prompts/_shared/deentification_rules.md`。
- **不引入 FAISS**：6 万级 NumPy `@` + `argpartition` 已是毫秒级。
- **片单 = 检索宇宙**：只能召回 3D 站点收录的 59,341 部；召回片单外电影会造成 `/movie/{id}` 死链。
- **共振分两轴 2×2（0/1/2）**：表层元素 + 底层逻辑（POV/尺度不变的因果-赌注引擎），SSOT 为 `docs/eval-the-bet.md` §4 与 `prompts/_shared/resonance_definition_v2.md`。
- **人类总编不可替代**：MVP 不做自动甄选与自动发布，总编从中文文案勾选后再生成平台版本。
- **留出冻结纪律**：只在观察集调 prompt/阈值 → 冻结 → 留出集只打一次分；勿在留出集反复调参后宣称提升。

---

## 约定速查

| 事项 | 约定 |
|---|---|
| 分支命名 | `feat/phase[N.N.N...]-[todo]` |
| 提交信息 | `<type>(<scope>): <pN.N>-<description>`（Conventional Commits） |
| 合并方式 | GitHub PR，**Create a merge commit（--no-ff）**，合并后删远端与本地分支 |
| 计划位置 | `.cursor/plans/Phase*.plan.md`（YAML frontmatter `todos:`，`status: todo→complete`） |
| 报告位置 | `docs/reports/Phase[N]-[todo-name]-report.md` |
| 决策记录 | 重大设计变更写 `docs/adr/NNNN-*.md` |
| 挂起触发 | `[需人工验收]` / 修复报错 2 次未果 / Plan 与代码冲突 → 输出 `⚠️ [PAUSED]` 并等待 |
