---
name: Phase9.8-panel-copy-regenerate-and-edit
overview: |
  给定稿界面（review_panel 定稿区）新增总编对成品稿的三种「定点操控」能力：
  ① 重生成正文（换一版创作）——重跑 C2 创作，只取新 body 覆盖当前稿；
  ② 重生成标题（body-aware）——以当前正文为输入，只重出一句 headline 覆盖当前稿；
  ③ 正文人工编辑——面板内直接改正文并存回成品稿。
  三种操作都遵循「覆盖当前稿」语义，**不新增版本层**（沿用 9.7.4 的 原版/去AI化版 二档模型）。
  提示词侧不做「前期工作流全拆」：monolithic 首发稿（headline+body 一次出）保留，只额外抽出
  body-aware 的 headline 模块 prompt，并把 headline 契约收敛为 `_shared` 单一事实源以消除双份漂移。
  核心改动：
  ① prompts：抽 `_shared/xiaohongshu_headline_contract.md` + 新 `compose_publish_xiaohongshu_headline.md`（body-aware）；
  ② compose：新增 `run_headline`（headline-only，输入含 current_body）+ body 重生成走 run_publish 取 body；
  ③ 新 `review_panel/regenerate_adapter.py`（`--target headline|body`，与 publish/rewrite adapter 同层）；
  ④ serve：`POST /api/regenerate` + `POST /api/edit-body`，并在 body 变更时失效陈旧 `_humanized.md`；
  ⑤ index.html：正文可编辑 textarea + 保存 + 「重生成标题」「重生成正文」按钮 + 覆盖后刷新；
  ⑥ ADR-0016 记录「定稿界面定点重生成/编辑 + 覆盖语义」决策；GATE 后同步 SSOT/PRD。
  发布仍全手动；只碰 xiaohongshu；不碰图片/其他平台/自动甄选。
todos:
  - id: p9.8.1-headline-prompt-split
    content: 9.8.1 · [prompt] 抽 _shared/xiaohongshu_headline_contract.md（headline 契约 SSOT）+ 新 compose_publish_xiaohongshu_headline.md（body-aware headline-only）+ monolithic 改引用共享契约（golden-snapshot 证等价）+ 写 ADR-0016
    status: complete
  - id: p9.8.2-compose-run-headline
    content: 9.8.2 · [compose] run_headline(candidate, news, current_body, ...) headline-only + 复用 parse_publish_output 的 headline 分支；body 重生成经 run_publish 取 body（不建独立 body prompt）
    status: complete
  - id: p9.8.3-regenerate-adapter
    content: 9.8.3 · [adapter] review_panel/regenerate_adapter.py（--target headline|body）：读当前 _copy_{platform}.md → 调 compose → 覆盖对应字段回写 + body 变更时删陈旧 _humanized.md
    status: complete
  - id: p9.8.4-backend-endpoints
    content: 9.8.4 · [面板] serve 新增 POST /api/regenerate（subprocess 调 regenerate_adapter）+ POST /api/edit-body（无 LLM，直接经 render_copy_markdown 写回 + 失效 humanized）
    status: complete
  - id: p9.8.5-frontend-edit-regenerate
    content: 9.8.5 · [面板] 定稿区正文改为可编辑 textarea + 保存；新增「重生成标题」「重生成正文」按钮；覆盖后刷新展示；理清与去AI化 toggle 的交互
    status: complete
  - id: p9.8.6-tests
    content: 9.8.6 · [测试] 覆盖 run_headline/regenerate_adapter/api regenerate/api edit-body/headline body-aware/humanized 失效
    status: todo
  - id: p9.8.7-gate-doc-sync
    content: 9.8.7 · [GATE] 真实重跑：三种操作面板验收（重生成正文/标题、正文编辑、覆盖语义、humanized 失效）；Go 后同步 SSOT/PRD 并引用 ADR-0016 收尾 [需人工验收]
    status: todo
isProject: true
---

# Phase 9.8 · 定稿界面：正文/标题重生成 + 正文人工编辑

## 前置条件

| Phase | 状态 | 依据 |
| ----- | ---- | ---- |
| 9.7（含 9.7.1–9.7.7） | complete 且已并入 `main` | `git log main` 可见 PR #120/#121 合并；p9.7.6 标 complete、SSOT 同步提交 `edb61a4` 在 main；`main..HEAD` 为空 |
| 当前分支 | `feat/phase9.8-panel-copy-regenerate-and-edit` | 从最新 `main` 检出（规则2：前置已并入 main → 从 main 检出，无 stacked 继承） |

## 背景

9.1–9.7 落地了 C2 平台化（小红书 headline + 归属行 + 必含元素）与定稿面板（展示 + 移动预览 + avoid-ai-writing 可逆 toggle）。但面板对成品稿只能「整段重跑 publish」或「整段去AI化」，总编无法：

1. 只对**正文**换一版创作（不满意就重掷，但不想连标题一起换）；
2. 只对**标题**重出一句（且要贴合当前正文）；
3. 在面板内**直接微调正文**再定稿。

本 Phase 补齐这三种「定点操控」，且刻意**不做提示词前期全拆**——保留 monolithic 首发稿（一次出 headline+body，省一次调用），只额外抽一个 body-aware 的 headline 模块用于重生成。

## 设计决策

### D0 · 澄清确认（来自需求讨论）

| # | 决策 | 取值 |
| - | ---- | ---- |
| 1 | 「重生成正文」的语义 | **A：换一版创作**（重跑 C2 创作出新 body），**非** avoid-ai-writing 去AI化 |
| 2 | headline 重生成是否 body-aware | **是**——以当前正文为输入产标题 |
| 3 | 版本模型 | **覆盖当前稿**，不新增版本层 |
| 4 | 是否支持面板内人工编辑正文 | **要**——编辑后可再重生成标题使其贴合 |

### D1 · 提示词拆分方式：monolithic 保留 + headline 契约收敛为 SSOT

- **不拆首发稿**：`compose_publish_xiaohongshu.md`（一次出 headline+body）继续作为首发 publish，逻辑不动。
- **抽共享契约**：把 headline 的硬规则（≤10 中文字、不裸片名、不煽动/推荐词、不剧透、一句话、平视调性）从 monolithic 抽到 `prompts/_shared/xiaohongshu_headline_contract.md`，作为 headline 规则的**单一事实源**。
- **新增 headline 模块 prompt**：`prompts/compose_publish_xiaohongshu_headline.md`，输入 = `{{news_context}}` + `{{selected_movie}}` + `{{current_body}}`，引用共享契约，只产一句 headline。
- **monolithic 也改引用共享契约**（通过 `render_c2_prompt` 注入 `{{headline_contract}}`），消除「headline 规则两处各写一份」的漂移风险。
- **回归护栏**：加一个 golden-snapshot 测试，断言「抽取后 monolithic 的渲染结果」与「抽取前」在语义上一致（headline 段文本不丢），证明动 GATE 验过的首发 prompt 无回归。
  - 若 golden-snapshot 表明改动 monolithic 风险偏高：**降级方案**——monolithic 保留内联 headline 段，仅在段首注释指向 `_shared` SSOT，共享契约只被新 headline prompt 引用（接受一次性重复，漂移列为技术债）。此降级由 9.8.1 实现时按快照结果二选一，记入报告。

### D2 · 正文重生成：复用 run_publish 取 body（不建独立 body prompt）

- `--target body`：复用整条 `run_publish`（含 news + selected_movie + judge 全语境）→ **只取新 body 覆盖**，丢弃这次顺带产出的新 headline（YAGNI，不为 body-only 单独建 prompt）。
- **后果与不联动约定**：新 body 可能与旧 headline 不再匹配 → **不自动重生成标题**；由总编按需再点「重生成标题」重新对齐（保持 targeted/覆盖语义，避免隐式连锁）。

### D3 · 标题重生成：body-aware

- `--target headline`：读当前 `_copy_{platform}.md` 的 **body**（可能已被人工编辑，见 D5）→ `run_headline(current_body)` → **只覆盖 headline**，body/链接不动。
- headline 的 body 输入取**原稿 body（`_copy_{platform}.md`）**，不取 humanized body（保持单一事实源；去AI化版是派生只读，见 D4）。

### D4 · 覆盖语义 + 与「去AI化版」的关系（关键）

- 重生成/编辑只改 `_copy_{platform}.md`（原稿），**不新增版本层**；面板仍只有 原版 / 去AI化版 二档。
- `_humanized.md` 是从 body 派生的旁支。**任何改动 body 的操作（重生成正文 / 人工编辑正文）都会使旧 humanized 陈旧** → **同步删除 `_humanized.md`**，回到「未去AI化」态，并清空 selection.json 对应 `copies.{platform}.humanized_path`（复用 9.1 stale-copy 清理思路，保「humanized_path=null ⇔ 盘上无 _humanized.md」不变量）。
- **重生成标题不动 body → 不失效 humanized**（headline 本就不参与 toggle）。

### D5 · 正文人工编辑

- 前端：定稿区正文由只读改为**可编辑 textarea + 保存**按钮（编辑态/展示态切换）。
- 后端 `POST /api/edit-body`：把编辑后的 body 经 `publish_adapter.render_copy_markdown` **写回原稿**（headline + 链接保持），并按 D4 失效 humanized。**无 LLM**，serve 直接写文件。
- **编辑只作用于原稿 body**；去AI化版是派生只读、不可直接编辑（要改就改原稿再重新去AI化）。

### D6 · 后端/adapter 形态（沿用既有约定）

- 新 `review_panel/regenerate_adapter.py`：与 `publish_adapter.py` / `rewrite_adapter.py` **同层**，`--date/--slug/--platform/--target headline|body`；耦合止于 `scripts.compose` + `scripts.lib.*`；stderr 打印 `Wrote <path>` 供 serve 解析。
- `POST /api/regenerate`（body `{date, slug?, platform, target}`）→ subprocess 调 regenerate_adapter（同 handle_publish/handle_rewrite 模式）。
- `POST /api/edit-body`（`{date, slug?, platform, body}`）→ 无 LLM，serve 复用 `render_copy_markdown` 直接写回。
- 复用现有 `_parse_wrote_path` / selection.json copies 读写 / `_delete_copy_if_exists` 等既有工具，不重造。

### D7 · ADR-0016

新开 `docs/adr/0016-panel-editorial-regeneration-and-inline-edit.md`，记录：定点重生成（headline/body 分开、body-aware headline）、覆盖语义（不加版本层）、body 变更即失效 humanized、面板内正文编辑边界（原稿可编辑 / 去AI化版只读）。引用 ADR-0013（调性）/ADR-0015（平台化 + 元素清单）。

---

## Todo 9.8.1 · [prompt] headline 契约 SSOT + body-aware headline prompt + ADR-0016

**依赖：** 无（可先做）

**改动：**
- `prompts/_shared/xiaohongshu_headline_contract.md`：[新] 从 `compose_publish_xiaohongshu.md` §headline 抽出 headline 硬规则（≤10 中文字、不裸片名、不煽动、不剧透、一句话、平视调性）
- `prompts/compose_publish_xiaohongshu_headline.md`：[新] body-aware headline-only prompt，占位符 `{{news_context}}` / `{{selected_movie}}` / `{{current_body}}` / `{{headline_contract}}`，sentinel 复用 `【标题】`（headline-only，无 `【正文】`）
- `prompts/compose_publish_xiaohongshu.md`：headline 段改为 `{{headline_contract}}` 注入（或降级方案：保留内联 + 注释指向 SSOT）
- `docs/adr/0016-panel-editorial-regeneration-and-inline-edit.md`：[新] 记录 D1–D7 决策

### 验收
- [ ] `_shared/xiaohongshu_headline_contract.md` 含全部 headline 硬规则
- [ ] 新 headline prompt 只要求产一句标题、含 `{{current_body}}` 输入
- [ ] monolithic 渲染 golden-snapshot 证等价（或降级方案已在报告说明理由）
- [ ] ADR-0016 落地并被 plan 引用

---

## Todo 9.8.2 · [compose] run_headline + body 重生成路径

**依赖：** 9.8.1

**改动：**
- `scripts/compose.py`：
  - 新 `load_headline_template(platform, prompts_dir)` + `render_headline_prompt(template, news_context, selected_movie, current_body, headline_contract)`
  - 新 `run_headline(candidate, news, current_body, *, provider, judge=None, platform, prompts_dir=None, llm_call=None) -> dict`（返回 `{tmdb_id, headline}`）；解析复用 `parse_publish_output` 的 headline 分支（仅 `【标题】` 时取首行）
  - headline system message 复用/微调 `_PUBLISH_SYSTEM_MESSAGE`（只产标题一行）
  - body 重生成不新增函数：adapter 直接调 `run_publish` 取 `body`

### 验收
- [ ] `run_headline` 以注入 `llm_call` 可离线单测，返回 `{tmdb_id, headline}`
- [ ] headline 解析对「只有 `【标题】` 一行」稳健（不吐 body）
- [ ] `run_publish` 未被破坏（既有 publish 测试仍绿）

---

## Todo 9.8.3 · [adapter] regenerate_adapter.py

**依赖：** 9.8.2

**改动：**
- `review_panel/regenerate_adapter.py`：[新]
  - `--target body`：读 `_copy_{platform}.md` 取 candidate/news/judge（经 publish_adapter 的 locate/find/load 复用）→ `run_publish` 取 body → 经 `render_copy_markdown` **保留现 headline + 链接、覆盖 body** 回写 → 删 `_humanized.md`
  - `--target headline`：读现 body → `run_headline(current_body)` → **保留 body + 链接、覆盖 headline** 回写（不删 humanized）
  - stderr 打印 `Wrote <path>`
- 复用 publish_adapter 的 `locate_news_dir/load_news/find_candidate/load_judge_entry/render_copy_markdown`；耦合止于 `scripts.compose` + `scripts.lib`

### 验收
- [ ] `--target body` 覆盖 body、保留 headline/链接、删除 `_humanized.md`
- [ ] `--target headline` 覆盖 headline、保留 body/链接、不动 humanized
- [ ] adapter 可独立 CLI 运行并打印 `Wrote <path>`

---

## Todo 9.8.4 · [面板] serve 端点 /api/regenerate + /api/edit-body

**依赖：** 9.8.3

**改动：**
- `review_panel/serve.py`：
  - `handle_regenerate`：subprocess 调 regenerate_adapter（`--target`）；`target=body` 成功后清 selection.json 的 `humanized_path`；返回新 headline 或 body
  - `handle_edit_body`：无 LLM，校验 body → 复用 `render_copy_markdown` 写回 `_copy_{platform}.md` → 删 `_humanized.md` + 清 `humanized_path`；slug 未传时从 selection 兜底
  - `route()` 注册 `POST /api/regenerate`、`POST /api/edit-body`
  - `_default_regenerate_adapter_path()` + 注入口（同 publish/rewrite adapter 注入模式）

### 验收
- [ ] `/api/regenerate` target=headline/body 分别返回覆盖后的字段
- [ ] `/api/edit-body` 写回成功、headline/链接不变、humanized 被失效
- [ ] slug 缺省时从 selection.json 兜底；缺 selection/字段有清晰 4xx

---

## Todo 9.8.5 · [面板] 前端：正文编辑 + 重生成按钮

**依赖：** 9.8.4

**改动：**
- `review_panel/index.html`：
  - 定稿区正文：只读 ↔ 可编辑 textarea 切换 + 「保存」→ `POST /api/edit-body`，成功后刷新 `/api/copy`
  - 新增「重生成正文」「重生成标题」按钮 → `POST /api/regenerate`，成功后覆盖内存态并刷新
  - 覆盖语义 UI：重生成/编辑后，若 body 变更则去AI化 toggle 复位到「原版」（humanized 已失效）
  - 交互护栏：LLM 进行中禁用按钮 + 结果/失败提示（复用 humanize-result 样式约定）

### 验收
- [ ] 可编辑正文并保存，刷新后展示更新、headline 不变
- [ ] 「重生成正文」换一版 body、headline 不变；「重生成标题」贴合当前正文、body 不变
- [ ] body 变更后去AI化版复位、需重新「去AI化」
- [ ] 移动/桌面预览、platform tab 等既有能力不回归

---

## Todo 9.8.6 · [测试] 覆盖新链路

**依赖：** 9.8.5

**改动：**
- `tests/test_compose.py`（或新增）：`run_headline` body-aware + headline-only 解析
- `tests/test_review_panel_regenerate_adapter.py`：[新] `--target body|headline` 覆盖 + humanized 失效
- `tests/test_review_panel_serve.py`：`/api/regenerate` + `/api/edit-body` + humanized 失效 + slug 兜底 + 向后兼容
- monolithic prompt golden-snapshot（9.8.1 若走注入方案）

### 验收
- [ ] `pytest tests/test_compose.py tests/test_review_panel_regenerate_adapter.py tests/test_review_panel_serve.py tests/test_review_panel_publish_adapter.py` 全绿
- [ ] 既有 publish/rewrite/copy 测试无回归

---

## Todo 9.8.7 · [GATE] 真实重跑 + 面板验收 + 文档同步 [需人工验收]

**依赖：** 9.8.1–9.8.6 全部

**执行顺序：**
1. 先真实重跑 + 面板验收三种操作。
2. 等待人工 Go/No-Go；No-Go 回到对应实现 TODO 修正。
3. Go 后再同步 SSOT/PRD 并收尾。

**验收项：**
- [ ] 「重生成正文」换一版 body、headline 保持；反复点覆盖上一版
- [ ] 「重生成标题」贴合当前（含人工编辑后的）正文、body 保持
- [ ] 面板编辑正文并保存，成品稿正确更新
- [ ] body 变更后 `_humanized.md` 被失效、selection.json `humanized_path` 归 null
- [ ] 覆盖语义无「幽灵版本」；去AI化 toggle 行为正确
- [ ] Go 后同步 `docs/SSOT/news-to-film-pipeline.md` compose 段 + PRD，引用 ADR-0016
- [ ] `[需人工验收 · Go/No-Go]`

---

## 风险与约束

- **动 GATE 验过的 monolithic prompt**：D1 抽 headline 契约会改首发 prompt，用 golden-snapshot 兜底；风险偏高则走降级方案（内联保留 + 注释指向 SSOT），二选一记入 9.8.1 报告。
- **版本模型别膨胀**：严守「覆盖 + 原版/去AI化版二档」，不引入「重生成版」第三档——这是本 Phase 最大的 UI 复杂度风险源（D4）。
- **body 变更 ⇔ humanized 失效不变量**：重生成正文 / 编辑正文 / 改选（9.1 已覆盖）三处都必须删 `_humanized.md` 并清 `humanized_path`，否则陈旧 humanized 与新 body 对不上。
- **headline↔body 不自动联动**：重生成 body 不自动重生成 headline（D2）；由总编显式操作，避免隐式连锁与 token 浪费。
- **serve.py 保持薄传输层**：regenerate 走 subprocess adapter（LLM 隔离）；edit-body 无 LLM 才允许 serve 直接写文件。
- **平台范围**：仅 xiaohongshu；X/Reddit 的 tab 仍灰置。
- **人类总编不可替代**：仍全手动，无自动甄选/自动发布。
