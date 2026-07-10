---
name: Phase10-persona-perspective-c2-draft-pool
overview: |
  把 persona 视角真正融入 C2 定稿——现状（Phase9 系列）里 run_publish 只吃
  news + selected_movie + judge_kernel，persona 从未进过 C2，样例稿的「视角感」
  实为 judge rationale 的回声。本 Phase 建「多 persona 扇出草稿池 + 总编指针选择」：
  ① 对选中候选的每个 triggered_by persona（无数量上限）各跑一版 C2，得到一个
     持久只读的草稿池 {slug}_drafts_{platform}.json（数组 {draft_id, headline, body}）；
  ② 总编「用眼睛挑」——选中 = 可变指针（selected_draft_id），不是搬运/消费：
     指针指向的草稿经 render_copy_markdown 派生为当前稿 {slug}_copy_{platform}.md；
  ③ 复数视角合并（上限 2）：把 ≤2 份蒸馏视角喂 C2 再出一版，append 进池（append-only）；
  ④ 人性化延后：草稿池是「正稿池」，总编选定后不满 AI 味再跑去AI化（沿用 rewrite 链路）。
  关键纪律：persona_card 满是内部行话（decon/P-Select/objective-floor…），**禁止**原样注入 C2；
  须蒸馏为中文可用视角指引 c2_perspective.md 再注入。本 Phase 显式推翻 ADR-0016 D4「二档、
  不加版本层」约束（记入 ADR-0017），但**不制造版本层爆炸**：草稿池 = 上游只读来源层，
  当前稿仍是唯一可编辑稿、去AI化版仍是其派生旁支——层级是「只读源池 → 当前稿 → 去AI化版」，
  不是 N 份可编辑版本。发布仍全手动；只碰 xiaohongshu；不碰图片/其他平台/自动甄选。
  合并两条路线（A=重跑 C2 合并视角、B=文本融合既有草稿）在**开发/评测期都实现**，靠 adapter 的
  `--combine-mode {A|B|both}` 开关；`both` 仅供 GATE 离线并列产两版给总编肉眼对比、二选一。
  **选定后生产工作流只走选中的那一条**（面板/serve 恒调单版），A/B 双版不进生产、不进面板 UI。
todos:
  - id: p10.1-distill-perspective-and-adr
    content: 10.1 · [asset] 蒸馏 12 份 prompts/personas/{Persona}/c2_perspective.md（中文视角指引，去行话）+ compose_publish_xiaohongshu.md 加 {{persona_perspective}} 段 + 写 ADR-0017（推翻 0016 D4 二档、立草稿池只读源层 + 指针派生模型）
    status: complete
  - id: p10.2-compose-persona-injection
    content: 10.2 · [compose] load_persona_perspective(persona_id)（THE-SAGE→The-Sage 归一化）+ run_publish 加 persona_perspective 参数 + render_c2_prompt 加 {{persona_perspective}} 占位符（沿用 headline_contract 的 no-op 向后兼容 + golden-snapshot 证空注入等价）
    status: complete
  - id: p10.3-drafts-adapter-fanout
    content: 10.3 · [adapter] review_panel/drafts_adapter.py：读 candidate.triggered_by 全量扇出 run_publish（各注入蒸馏视角）→ 写持久只读 {slug}_drafts_{platform}.json；含 --combine a,b（≤2）+ --combine-mode {A|B|both}（默认单版；both 仅 GATE 离线对照，产 #A/#B 两版 append）；复用 publish_adapter 的 locate/load/find；stderr 打 Wrote <path>
    status: complete
  - id: p10.4-backend-endpoints
    content: 10.4 · [面板] serve 新增 POST /api/generate-drafts（subprocess 扇出）+ POST /api/select-draft（指针派生当前稿 + 失效 humanized + 写 selected_draft_id）+ POST /api/combine-drafts（≤2 校验）+ route 注册 + _default_drafts_adapter_path 注入口
    status: complete
  - id: p10.5-frontend-draft-pool
    content: 10.5 · [面板] index.html 草稿池浏览区（每 persona 草稿 headline+body 卡片）+ 选主视角指针高亮 + 勾选 ≤2 合并 + 「生成草稿池」按钮 + 选中后流入既有 publish/去AI化工作流（复用 loading 锁与结果提示）
    status: complete
  - id: p10.6-tests
    content: 10.6 · [测试] 覆盖 persona 注入 run_publish/空注入 golden-snapshot/drafts_adapter 扇出与 combine≤2/api generate-drafts+select-draft+combine-drafts/指针派生失效 humanized/向后兼容（无 persona 时旧路径不回归）
    status: complete
  - id: p10.7-gate-doc-sync
    content: 10.7 · [GATE] 真实重跑全量扇出 + 面板验收（浏览池/选主视角/合并≤2/派生当前稿/失效 humanized）+ 离线 --combine-mode both 产 A/B 两版肉眼对比二选一 + 把选中路线设为生产默认（面板恒走单版）+ Go 后同步 SSOT/PRD 并引用 ADR-0017 收尾 [需人工验收]
    status: complete
isProject: true
---

# Phase 10 · persona 视角 C2 草稿池（多视角扇出 + 总编指针选择）

## 前置条件

| Phase                  | 状态                     | 判定依据                                                                                                          |
| ---------------------- | ------------------------ | --------------------------------------------------------------------------------------------------------------- |
| 9.8（9.8.1–9.8.7）     | complete 且已并入 `main` | `git log main` 见 PR #128 合并（`f9a8373`）、p9.8.7 report 提交 `f58e98c` 在 main；Phase9 收尾 `13efb25`/`9ab4143` |
| 9（含 9.1–9.8 全子计划）| complete 且已并入 `main` | `git log --oneline main..HEAD` 为空；`git status -sb` = `## main...origin/main`（工作区干净、无未合并 `feat/phase*`） |
| 当前分支               | `feat/phase10.1-...`     | 从最新 `main` 检出（规则2：前置已并入 main → 从 main 检出，无 stacked 继承）                                     |

## 背景

Phase 9 系列把 C2 做成了平台化定稿 + 面板（headline/body 重生成、正文编辑、去AI化）。但**上游 persona 视角从未进入 C2**——这是 Round1 数据流追踪确认的架构缺口：

```
现状 C2 输入（scripts/compose.py · run_publish）：
    news_context      ← news.json（标题/摘要/链接）
    selected_movie    ← retrieve.json candidate（TMDB DB 投影）
    judge_kernel      ← llm-judge-scores.json（judge rationale/causal_test）
    headline_contract ← _shared/xiaohongshu_headline_contract.md
    ────────────────────────────────────────────────
    persona           ← ✗ 从不传入

后果：样例稿里「个体衰老 vs 群体记忆流失」的视角感，实为 judge rationale 的回声
     （且 prompt 还要求改写得不像来自 review 阶段）。persona 的「共鸣视角」名存实亡。
```

fan-out 的**数据来源已就绪**（无需新采集）：`retrieve.json` 每个候选自带

```
candidates[].triggered_by : ["THE-INNOCENT","THE-EVERYMAN","THE-HERO",...]   # 命中该片的 persona 全集（本例 9 个）
candidates[].hit_sources[].agent_id                                          # build_data.py 已据此算 resonance_agents
```

**目标数据流演变**（本 Phase 要落地）：

```
选中候选 candidate
    │
    ├─ for persona in candidate.triggered_by:          # 全量扇出，无上限（Round4 决策②）
    │      perspective = load_persona_perspective(persona)   # 蒸馏中文视角，非原始 card
    │      draft = run_publish(candidate, news, judge, persona_perspective=perspective)
    │      → append {draft_id: persona, headline, body}
    │
    └─ 写 {slug}_drafts_{platform}.json                # 持久 · 只读 · 一次生成不再 mutate

总编在面板「用眼睛挑」：
    selected_draft_id ──(可变指针)──▶ 池中某 draft
                                       │
                                       └─ render_copy_markdown → {slug}_copy_{platform}.md（当前稿）
                                                                    │
                                                                    └─(不满 AI 味)─▶ 去AI化版（派生旁支，沿用 rewrite）
```

## 设计决策

### D0 · 澄清确认（来自 Round4–5 需求讨论）

| #   | 决策                          | 取值                                                                                                  |
| --- | ----------------------------- | ----------------------------------------------------------------------------------------------------- |
| 1   | 二档约束（ADR-0016 D4）       | **推翻**——允许在「当前稿/去AI化版」之上加一层**只读草稿池**                                            |
| 2   | 扇出数量                      | **全量、无上限**——推文短、成本低，读起来快；不做「选 N 个 persona」的算法猜测                          |
| 3   | 是否带 persona card           | **带，但蒸馏**——绝不原样注入行话 card，须先蒸馏为中文视角指引                                          |
| 4   | 人性化时机                    | **延后**——草稿池是「正稿池」；总编选定一版后不满 AI 味再跑去AI化                                       |
| 5   | 复数视角合并                  | **上限 2**；A/B 两路线都实现，`--combine-mode both` 仅开发期离线对照选型，**生产只走选定单版**（Round6）  |
| 6   | 选中语义（Round5 修正）       | **可变指针，非搬运**——草稿池永不被消费/删除；总编可反悔、回看其它草稿，改指针即改当前稿                |

### D1 · persona 视角蒸馏：c2_perspective.md（中文，去行话）·【本 Phase 最大质量前提】

- **问题**：`prompts/personas/{Persona}/persona_card.md` 面向 pseudo/检索侧，满是内部行话
  （decon / P-Select / objective-floor neutral / focalized / fit / Who 正极负极 / alt-creator lens），
  直接注入 C2 会污染中文创作、泄露内部术语。
- **方案**：每个 persona 新增 `prompts/personas/{Persona}/c2_perspective.md`——把 card 的**创作可用内核**
  （核心情感、价值倾向、看待事件的镜头方向）蒸馏成**几句中文视角指引**，只讲「用什么眼光看这条新闻+这部电影」，
  不含任何术语。与 `persona_card.md` 同目录共置（沿用现有 persona 资产布局）。
  - 例（The-Sage）：`以求真、理性、辨识的眼光切入；关注证据与因果的清晰，克制而不煽情；`
    `在意「被验证的事实 vs 被制造的扭曲」的张力。`（对照原 card 的 decon/P-Select 行话——全部剥离）
- **单一事实源**：c2_perspective 是 C2 侧 persona 视角的 SSOT；persona_card 仍是检索侧 SSOT，两者各司其职不混用。

### D2 · C2 注入点：run_publish 加 persona_perspective 参数（sentinel 占位符 + no-op 向后兼容）

- `render_c2_prompt` 加 `{{persona_perspective}}` 占位符——**完全复刻 `{{headline_contract}}` 的 no-op 模式**：
  模板无此占位符或传空串时 `replace` 为 no-op，渲染结果与注入前逐字节一致（golden-snapshot 兜底）。
- `run_publish(..., persona_perspective: str = "")`：空串 = 现有行为（首发 publish / 9.8 重生成路径完全不受影响）。
- `compose_publish_xiaohongshu.md` 增一段「本条创作的主视角」注入 `{{persona_perspective}}`；
  与 judge_kernel 的关系写清：**persona 视角是「用什么眼光写」，judge 是「为什么共振」**，两者不冲突、不替代。
- **归一化**：`triggered_by` 是 `THE-SAGE` 大写连字符，persona 目录是 `The-Sage` 首字母大写；
  `load_persona_perspective` 内做 `THE-SAGE → The-Sage` 归一化（title-case per hyphen 段），缺文件 → 清晰报错。

### D3 · 草稿池 = 持久只读来源层（append-only，永不 mutate/消费）·【Round5 核心修正】

- 文件 `{slug}_drafts_{platform}.json` = 数组 `[{draft_id, headline, body}]`，`draft_id` = persona（如 `The-Sage`）
  或合并稿的 `The-Sage+The-Explorer`。
- **一次生成、只读**：`/api/generate-drafts` 全量扇出写一次；「选中」**不消费、不删除、不移动**任何草稿。
- **重新扇出 = 整份覆盖**（显式再生成动作，等价重掷全部 persona），合并稿 append 进池。
- 总编改主意时可回看其它草稿、改指针——这正是「草稿池不可丢弃」的动机（Round5）。

### D4 · 选中 = 可变指针 selected_draft_id（派生当前稿，非搬运）

- selection.json 的平台 copies 条目加 `selected_draft_id` 字段（可变指针）。
- `/api/select-draft`：把指针指向的池内草稿经 `render_copy_markdown` **派生**为 `{slug}_copy_{platform}.md`（当前稿），
  并**失效 humanized**（改指针 ⇒ body 变 ⇒ 旧去AI化稿过期，删 `_humanized.md` + 清 `humanized_path`，
  复用 9.8 D4 / 9.1 stale 清理不变量）。
- 层级清单（**不是版本层爆炸**）：`只读草稿池（N 版来源）→ 当前稿（唯一可编辑）→ 去AI化版（当前稿派生旁支）`。
  9.8 的正文编辑 / 标题重生成 / 去AI化全部**只作用于「当前稿」**，语义不变——草稿池纯上游、不可编辑。

### D5 · 复数视角合并（上限 2）· 开发期 A/B 对照，生产期单版

**核心区分（Round6 修正）：A/B 双版只是「开发/评测期的选型对照」，不是生产形态。**

- **两条路线都实现**（都要写出可运行代码，供选型）：
  - **路线 A（重跑 C2 合并视角）**：把 ≤2 份蒸馏视角拼成一个复合 `persona_perspective` 再跑一次 `run_publish`——
    与单视角同一条创作管线，主视角是复合的，出稿浑然一体但多花一次 LLM 调用。
  - **路线 B（文本融合既有草稿）**：直接拿池内那两份既有 body 做文本融合纯函数——不重跑、省一次调用，
    但接缝与调性一致性存疑。
- **`--combine-mode {A|B|both}` 开关控制产出**：
  - `both`（**仅 GATE 离线用**）：一次产 `a+b#A` + `a+b#B` 两版 append 进池，供总编肉眼并列对比、二选一。
  - `A` / `B`（**生产默认**）：只产选中那一版，`draft_id = "a+b"`（无 `#A/#B` 后缀），append 进池。
- **选型冻结即生产纪律**：GATE 选定后，把中选路线设为 `--combine-mode` 生产默认；
  `/api/combine-drafts` **恒调单版**（`{date, slug?, platform, draft_ids:[a,b]}` → adapter `--combine a,b`，不带 both）。
  面板/serve/生产链路**永不产双版**——A/B 对照的复杂度全部留在开发期 CLI，不外泄到 UI 与产物。
- 合并稿 append 进池（D3），与单视角草稿平权、可被指针选中。

### D6 · 后端/adapter 形态（沿用 9.8 既有约定）

- 新 `review_panel/drafts_adapter.py`：与 publish/rewrite/regenerate adapter **同层**，唯一 import `scripts.compose` 之一；
  复用 publish_adapter 的 `locate_news_dir/load_news/find_candidate/load_judge_entry/render_copy_markdown`；
  stderr 打 `Wrote <path>` 供 serve 解析；`run_publish` 可注入（测试 stub 免真调 LLM）。
- `POST /api/generate-drafts`（`{date, slug?, platform}`）→ subprocess 扇出（同 handle_publish/regenerate 模式）。
- `POST /api/select-draft`（`{date, slug?, platform, draft_id}`）→ 派生当前稿（可无 LLM，直接读池 + render + 失效 humanized）。
- `POST /api/combine-drafts`（`{date, slug?, platform, draft_ids}`）→ subprocess `--combine`。
- slug/tmdb_id 缺省时从 selection.json 兜底（读经 D4 迁移只见 `copies` dict）；复用 `_parse_wrote_path`/`_delete_copy_if_exists`。

### D7 · ADR-0017

新开 `docs/adr/0017-persona-perspective-c2-draft-pool.md`，记录：推翻 0016 D4 二档约束的理由与边界、
草稿池只读来源层 + 指针派生模型（区别于「N 份可编辑版本」）、persona 视角蒸馏（c2_perspective 为 C2 侧 SSOT、
禁注入原始 card）、合并上限 2 且 A/B 两路线开发期离线对照选型、生产冻结为单版。引用 ADR-0013（调性）/0015（平台化）/0016（重生成与二档，被本 ADR 部分推翻）。

---

## Todo 10.1 · [asset] 蒸馏 12 份 c2_perspective.md + C2 prompt 加视角段 + ADR-0017

**依赖：** 无（可先做）

**改动：**
- `prompts/personas/{Persona}/c2_perspective.md`：[新 ×12] 从各 `persona_card.md` 蒸馏中文视角指引（去行话，见 D1），
  统一模板：`核心眼光 / 关注张力 / 调性`三句内，无术语、无极性符号、不泄露内部机制。
- `prompts/compose_publish_xiaohongshu.md`：加「本条创作的主视角」段，注入 `{{persona_perspective}}`，
  并写清与 `{{judge_kernel}}` 的分工（视角=用什么眼光写；judge=为什么共振）。
- `docs/adr/0017-persona-perspective-c2-draft-pool.md`：[新] 记录 D1–D7。

### 验收
- [ ] 12 份 c2_perspective.md 齐全，逐份人读无内部术语（decon/P-Select/focalized… 全无）
- [ ] C2 prompt 含 `{{persona_perspective}}` 段且分工表述清晰
- [ ] ADR-0017 落地并被本 plan 引用；明确「推翻 0016 D4」的边界

---

## Todo 10.2 · [compose] load_persona_perspective + run_publish 注入 + render 占位符

**依赖：** 10.1

**改动：**
- `scripts/compose.py`：
  - 新 `load_persona_perspective(persona_id, prompts_dir=None) -> str`：`THE-SAGE→The-Sage` 归一化，
    读 `prompts/personas/{Persona}/c2_perspective.md`；缺文件清晰报错（不静默空串，避免掩盖扇出配置错误）。
  - `run_publish(..., persona_perspective: str = "")`：透传给 render；空串 = 现有行为（默认不破坏）。
  - `render_c2_prompt(..., persona_perspective: str = "")`：加 `{{persona_perspective}}` replace（no-op 向后兼容）。

### 验收
- [ ] `load_persona_perspective("THE-SAGE")` 命中 `The-Sage/c2_perspective.md`；缺文件抛清晰异常
- [ ] `run_publish` 注入非空视角时 prompt 含该段；传空串时渲染与注入前逐字节一致（golden-snapshot）
- [ ] 既有 publish/headline 测试全绿（run_publish 默认签名向后兼容）

---

## Todo 10.3 · [adapter] drafts_adapter.py：全量扇出 + combine≤2 · 写只读草稿池

**依赖：** 10.2

**改动：**
- `review_panel/drafts_adapter.py`：[新]
  - 默认：读 `find_candidate(...).triggered_by` **全量**，对每个 persona 调 `run_publish(persona_perspective=load_persona_perspective(p))`，
    收集 `[{draft_id: persona, headline, body}]` → 写 `{slug}_drafts_{platform}.json`（覆盖语义 = 显式再扇出）。
  - `--combine a,b`（argparse 解析逗号列表，**校验 ≤2 否则报错退出**）+ `--combine-mode {A|B|both}`（默认 A，见 D5）：
    - 路线 A（合并稿走 `run_publish`）：≤2 蒸馏视角拼成复合 `persona_perspective` 调 `run_publish`。
    - 路线 B（合并稿走文本融合纯函数）：读池内 a、b 两份既有 body 融合，不调 `run_publish`。
    - `mode=A`/`mode=B`：产**一条** `draft_id="a+b"`（生产形态，无后缀）；`mode=both`：产**两条** `a+b#A`+`a+b#B`（仅 GATE 离线对照）。
    - 一律 **append** 进现有池（读→append→写，不动其它草稿）。
    - 融合函数独立可测（纯函数：两份 body → 融合 body），便于 GATE 迭代融合策略。
  - 复用 publish_adapter 的 `locate_news_dir/load_news/find_candidate/load_judge_entry/render_copy_markdown`；
    `run_publish`/`load_persona_perspective` 可注入；stderr 打 `Wrote <path>`。

### 验收
- [ ] 默认扇出生成条数 == `candidate.triggered_by` 去重数；每条 draft_id 对应一个 persona
- [ ] `--combine A,B`（默认 mode=A）append **一条** `A+B`；`--combine-mode both` append **两条** `A+B#A`/`A+B#B`；均保留原有草稿
- [ ] 传 3 个 combine 目标 → 非零退出 + 清晰报错
- [ ] 路线 A 走 `run_publish`（可 stub 验证被调用）、路线 B 走文本融合纯函数（不调 LLM）
- [ ] adapter 可独立 CLI 运行并打印 `Wrote <path>`；注入 stub 可离线单测

---

## Todo 10.4 · [面板] serve 端点 /api/generate-drafts + /api/select-draft + /api/combine-drafts

**依赖：** 10.3

**改动：**
- `review_panel/serve.py`：
  - `handle_generate_drafts`：subprocess 调 drafts_adapter 全量扇出；slug/tmdb_id 从 selection.json 兜底；返回池路径 + 草稿列表。
  - `handle_select_draft`：读 `{slug}_drafts_{platform}.json` 取指定 `draft_id` → `render_copy_markdown` 派生当前稿 →
    删 `_humanized.md` + 清 `humanized_path` + 写 `selected_draft_id`（D4）。无 LLM，serve 直接读池写文件。
  - `handle_combine_drafts`：校验 `draft_ids` ≤2 → subprocess `--combine`（**恒单版**，不传 `--combine-mode both`；
    生产走 GATE 选定的路线）；成功后草稿列表回传（不自动切指针）。`both` 只在开发期手动跑 CLI，serve 不暴露。
  - `route()` 注册三个 `POST`；`_default_drafts_adapter_path()` + 注入口（同 publish/regenerate adapter 注入模式）。
  - selection.json copies 条目扩 `selected_draft_id`（向后兼容：旧条目无此字段视为 None，D4 迁移处一并兜底）。

### 验收
- [ ] `/api/generate-drafts` 返回全量草稿；缺 selection 有清晰 4xx
- [ ] `/api/select-draft` 派生当前稿、写 `selected_draft_id`、失效 humanized；draft_id 不存在 → 4xx
- [ ] `/api/combine-drafts` ≤2 通过并 append **单条**合并稿（不产双版）；>2 → 4xx；slug 缺省从 selection 兜底
- [ ] 既有 /api/publish、/api/regenerate、/api/edit-body、/api/rewrite 无回归

---

## Todo 10.5 · [面板] 前端：草稿池浏览 + 选主视角指针 + 合并 ≤2

**依赖：** 10.4

**改动：**
- `review_panel/index.html`：
  - 「生成草稿池」按钮 → `POST /api/generate-drafts`，成功后渲染草稿池区。
  - 草稿池区：每 persona 一张卡片（persona 名 + headline + body 预览）；单选高亮 = 主视角指针 → `POST /api/select-draft`，
    成功后当前稿刷新（复用 `/api/copy`）、去AI化 toggle 复位（body 已变）。
  - 勾选（≤2，超限禁用）+「合并生成」→ `POST /api/combine-drafts`，成功后池**追加一张合并卡片**（`a+b`，
    走 GATE 选定的生产路线）；可像普通草稿一样被点选为当前稿。（A/B 对照是开发期 CLI 的事，面板不出双版）
  - 选中主视角后**流入既有 publish/去AI化工作流**（正文编辑、标题重生成、去AI化按钮语义不变，作用于当前稿）。
  - 交互护栏：LLM 进行中禁用按钮（复用 9.8 loading 锁）+ 结果/失败提示；合并勾选超 2 个即禁用「合并生成」。

### 验收
- [ ] 点「生成草稿池」列出全部 persona 草稿；点某卡即成为当前稿、可继续 publish/编辑/去AI化
- [ ] 改选另一张卡 → 当前稿随之变、去AI化版复位；回看其它草稿不丢失（池只读）
- [ ] 勾 2 张合并**追加一张合并卡**入池、可点选为当前稿；勾第 3 张被拦
- [ ] 移动/桌面预览、platform tab、既有 9.8 能力不回归

---

## Todo 10.6 · [测试] 覆盖新链路

**依赖：** 10.5

**改动：**
- `tests/test_compose.py`：`load_persona_perspective` 归一化/缺文件；`run_publish` 注入视角 + 空注入 golden-snapshot 等价。
- `tests/test_review_panel_drafts_adapter.py`：[新] 全量扇出条数、`--combine-mode A|B` 各产单条、`both` 产 `#A/#B` 两条、路线 A 走 run_publish / 路线 B 走文本融合纯函数、combine>2 报错、append 语义、stub 注入。
- `tests/test_review_panel_serve.py`：`/api/generate-drafts`+`/api/select-draft`+`/api/combine-drafts`；指针派生失效 humanized；
  `selected_draft_id` 写入 + 向后兼容（旧 selection 无字段）；slug 兜底。

### 验收
- [ ] `pytest tests/test_compose.py tests/test_review_panel_drafts_adapter.py tests/test_review_panel_serve.py tests/test_review_panel_publish_adapter.py` 全绿
- [ ] 既有 publish/regenerate/rewrite/copy 测试无回归

---

## Todo 10.7 · [GATE] 真实重跑 + 面板验收 + A/B 选型冻结 + 文档同步 [需人工验收]

**依赖：** 10.1–10.6 全部

**执行顺序：**
1. 先真实全量扇出重跑 + 面板验收（不写 report、不合并）。
2. **离线**跑 `--combine-mode both` 产 `a+b#A`/`a+b#B` 两版，肉眼并列对比、**二选一**。
3. 把中选路线**冻结为生产默认**（adapter 默认 mode + serve 恒调单版），复跑确认面板合并只出单版。
4. 等待人工 Go/No-Go；No-Go 回到对应实现 TODO 修正。
5. Go 后再同步 SSOT/PRD 并收尾。

**验收项：**
- [ ] 全量扇出对真实候选生成 N=triggered_by 数的草稿，逐版 persona 视角**可辨识**（不再是 judge 回声）
- [ ] 面板浏览池 / 选主视角 / 改选回看 / 合并≤2（**单版**）/ 派生当前稿 / 失效 humanized 全部正确
- [ ] 离线 `--combine-mode both` 产 A/B 两版肉眼对比、**二选一**；中选路线**冻结为生产默认**，写入报告与 ADR-0017
- [ ] 冻结后复跑面板合并**只出单版**（`a+b`，无 `#A/#B`），确认双版逻辑不外泄生产
- [ ] 选定草稿后走通「不满 AI 味 → 去AI化」延后人性化链路
- [ ] Go 后同步 `docs/SSOT/...` compose 段 + PRD，引用 ADR-0017
- [ ] `[需人工验收 · Go/No-Go]`

---

## 风险与约束

- **蒸馏质量是命门（D1）**：c2_perspective 蒸馏不到位会让扇出 N 版稿「视角同质」，扇出即失去意义；
  10.1 蒸馏后须人读逐份确认「眼光可区分」，这是 10.7 GATE 的核心验收点。
- **禁注入原始 card**：persona_card 行话若泄漏进 C2 中文稿即为质量事故；load 路径只认 c2_perspective.md。
- **版本层别爆炸（推翻 0016 D4 的边界）**：严守「只读草稿池 → 唯一可编辑当前稿 → 去AI化派生」三层；
  草稿池不可编辑、指针可变但不搬运——这是本 Phase 最大的架构复杂度风险源（D3/D4）。
- **body 变 ⇔ humanized 失效不变量**：改指针 / 重生成 / 编辑正文 / 改选片四处都必须删 `_humanized.md` 并清 `humanized_path`。
- **向后兼容**：`run_publish(persona_perspective="")` = 现有行为；旧 selection.json 无 `selected_draft_id` 视为 None；
  首发 publish / 9.8 重生成路径零回归（golden-snapshot + 既有测试兜底）。
- **成本**：全量扇出 = triggered_by 数次 LLM 调用（本例 9 次/候选）；用户已确认可接受（推文短、成本低）。
- **serve.py 保持薄传输层**：generate/combine 走 subprocess adapter（LLM 隔离）；select-draft 无 LLM 才允许 serve 直接读池写文件。
- **平台范围**：仅 xiaohongshu；X/Reddit tab 仍灰置。
- **人类总编不可替代**：仍全手动，无自动甄选/自动发布——扇出只是「把 N 版摆出来给总编用眼睛挑」。
