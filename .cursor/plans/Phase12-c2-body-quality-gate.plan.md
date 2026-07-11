---
name: Phase12-c2-body-quality-gate
overview: |
  把 C2 小红书正文的「去 AI 腔」验收标准从肉眼主观判断算子化为红/绿信号：
  新增 body_lint 确定性句式校验器（纯函数 + DSL 红线表）+ LLM-judge 幻觉校验器
  （overview 当唯一真值），在唯一创作环节 run_publish 内接「命中即带反馈重试」编排
  （复刻 rewrite.py 的 repair_context 模式，上限 K 次），重试耗尽不硬失败、保留最后
  一版 + 挂 warnings 交人工兜底。架构主张：检测器（body_lint/judge）只返回违规清单、
  不做编排；编排（拼反馈/重跑/降级）由 run_publish 独立承担。设计决策已固化于
  docs/adr/0019-c2-body-quality-gate.md（本 Phase 前置落地），只管正文、不碰 ADR-0018
  的确定性抬头行。仅 xiaohongshu。
todos:
  - id: p12.1-land-structure-baseline
    content: 12.1 · [基线] 从最新 main 检出 feat/phase12.1-structure-and-neutral-default，将工作区三文件裸改（compose_publish_xiaohongshu.md 结构层去AI腔 + drafts_adapter.py 池首中性默认稿 + test_review_panel_drafts_adapter.py）规整提交；pytest 确认 panel 测试无 regression。仅锁存基线，正文眼验达标留到 12.5
    status: complete
  - id: p12.2-body-lint-syntax-gate
    content: 12.2 · [gate] body_lint 纯函数校验器 scripts/lib/body_lint.py：(rule_id, pattern, desc) 红线 DSL 表 + scan(body)->list[Violation] 纯函数（只检测/不改文本/不调 LLM/零 IO），覆盖硬转场/说破句/接受度单独成句；每条红线正反例单测；遵循已落地 ADR-0019 D0/D1
    status: complete
  - id: p12.3-hallucination-judge
    content: 12.3 · [gate] judge_body_fabrication(body, overview, *, llm_call)->list[Finding] 纯函数 + 配套 prompt：拿 DB overview 当唯一真值，判定 body 是否出现 overview 没写的电影细节/写错导演名；llm_call 可注入，单测用 stub
    status: complete
  - id: p12.4-lint-retry-orchestration
    content: 12.4 · [compose] 在 run_publish 的 clean_publish_body 后接闸门：body_lint.scan + judge_body_fabrication 命中→拼 repair_context 喂回 LLM 重生成（复刻 rewrite.py 模式，上限 K 次），仍失败保留最后一版 + 挂 warnings（不硬失败）；单测覆盖重试通过/耗尽 + golden-snapshot 零回归
    status: complete
  - id: p12.5-eyeball-gate-manual-approve
    content: 12.5 · [GATE] 真重放 05 场景（AI/广岛 + The Creator, tmdb 670292）跨 persona 出正文：body_lint 计数 + judge 结果 + 人工眼验三重确认句式红线归零/幻觉压住/Persona ①偏②显形/3-4段扫读密度；歪了回 12.2/12.3/12.4/prompt 迭代 [需人工验收]
    status: todo
isProject: true
---

# Phase 12 · C2 小红书正文质量闸门（body quality gate）

## 前置条件

| Phase / 前置 | 状态 | 判定依据 |
| --- | --- | --- |
| 11（11.1–11.7 全子计划） | complete 且已并入 `main` | `git log --oneline -15` 见 `d5657e2 Merge pull request #142 ... feat/phase11.7-gate`，p11.1–11.7 全部 merge commit 在链上 |
| 当前分支 | 从最新 `main` 检出 | 规则2：前置已并入 main → 从 main 检出，无 stacked 继承。`git branch -a` 无残留 `feat/phase12*` |
| 工作区 | 三文件未提交裸改（上个会话遗留，非本 agent 所为） | `git status -sb` = `## main...origin/main` + ` M prompts/compose_publish_xiaohongshu.md` / ` M review_panel/drafts_adapter.py` / ` M tests/test_review_panel_drafts_adapter.py`。由 12.1 规整进分支 |
| ADR-0019 | **已先行落地**（本 Phase 前置） | `docs/adr/0019-c2-body-quality-gate.md` 已写定 D0–D5；本 plan 各 TODO 只**引用**它，不再新开 |

## 背景

现状：C2 发布稿正文的「去 AI 腔」重塑（拆四拍骨架 / 封说破盖章 / 禁编造 overview 没有的细节 / Persona ①偏② 显形 / 放开长度 / 3–4 段扫读）在上一个会话中已把规则**写进 prompt**（[prompts/compose_publish_xiaohongshu.md](../../prompts/compose_publish_xiaohongshu.md)，正文语气契约沿用 ADR-0013 影像平权）。但眼验重放 [output/daily_batch/2026-07-06/05-ai-poses-hiroshima-style-threat-to-humanity_drafts_xiaohongshu.json](../../output/daily_batch/2026-07-06/05-ai-poses-hiroshima-style-threat-to-humanity_drafts_xiaohongshu.json) 显示违规几乎全在：

```
硬转场    「而这部…电影」
说破句    「无论是…还是…同一种」（结尾盖章）
接受度    单独成句
语义幻觉  编造「士兵穿过战火村庄」「扣扳机前犹豫」等 overview 没有的画面
导演名    写错（Gareth Edwards → 盖瑞斯·埃文斯）
```

**根因不是「prompt 不够狠」**（已试 5 版失败）——而是**验收标准没算子化**：红线只能肉眼看，主观、不可复现、无法写测试。本 Phase 用 L3（校验层 + 命中触发带反馈重试）+ LLM-judge 把验收变成红/绿信号。决策与理由固化于 [docs/adr/0019-c2-body-quality-gate.md](../../docs/adr/0019-c2-body-quality-gate.md)（已先行落地）。

**目标数据流演变：**

```
现状（一次生成即产出，靠 prompt 赌 + 事后肉眼看）:
    render_c2_prompt ─▶ LLM ─▶ parse_publish_output ─▶ clean_publish_body ─▶ 前置 movie_header
                                                          └─ 违规只能人工眼验，主观不可复现

目标（在唯一创作环节内加质量闸门 + 命中即带反馈重试）:
    render_c2_prompt ─▶ LLM ─▶ parse_publish_output ─▶ clean_publish_body ─┐
                        ▲                                                   ▼
                        │                                    ┌── body_lint.scan（句式红线，确定性）
              repair_context 带                              └── judge_body_fabrication（语义幻觉，LLM-judge）
              反馈重试(≤K 次) ◀── 命中 ──────────────────────────────┘
                        │                                    未命中 / 重试耗尽
                        └────────────────────────────────────────▶ 前置 movie_header ─▶ 成品
                                                     (耗尽仍违规 → 保留最后一版 + 挂 warnings，交人工兜底)
```

## 关键架构锚点（复用，不新造）

- **唯一创作环节**：[scripts/compose.py](../../scripts/compose.py) 的 `run_publish` → `render_c2_prompt` → LLM → `parse_publish_output` → `clean_publish_body` → 前置 `render_movie_header`。`clean_publish_body` 旁即质量闸门的天然挂载点。
- **重试先例**：[scripts/rewrite.py](../../scripts/rewrite.py) 的 `run_screenwriter` 已有 `repair_context` 带反馈重试模式（parse 失败 → 喂错误 → 重跑，上限 2 次），12.4 直接复刻这套模式，不发明新范式。
- **扇出消费方**：[review_panel/drafts_adapter.py](../../review_panel/drafts_adapter.py) 的 `run_fanout` 对每个 persona 各调一次 `run_publish`；闸门接在 `run_publish` 内 = 扇出的每一版都自动过闸。
- **素材真值来源**：`selected_movie` 块里的 DB overview 是「剧情简述」唯一授权来源，LLM-judge 拿它当基准查幻觉。

## 设计决策（详见 ADR-0019，此处为落地索引）

### D0 · 能力边界与红线分工（ADR-0019 D0）

- `body_lint`（确定性正则）只抓**句式类红线**：硬转场「而这部…电影」、说破句「(都|背后是)…(同一种|同一个)…」「无论是…还是…」、接受度单独成句。**抓不住语义幻觉**。
- 语义幻觉（overview 没有的画面 / 人物 / 数字 / 写错导演名）→ `body_lint` 覆盖不到，交 **LLM-judge** 兜。
- 两者都是**检测器（detector）**，不做编排：只返回违规清单，不改文本、不决定重试。编排由 12.4 独立承担。

### D1 · body_lint = 纯函数 + DSL 红线表（ADR-0019 D1，FP 风格类比 render_movie_header）

- 新增 [scripts/lib/body_lint.py](../../scripts/lib/body_lint.py)：一张模块级 `RULES` 表 `list[(rule_id, pattern, description)]` + 一个 `scan(body: str) -> list[Violation]` 纯函数（**只检测、不改文本、不调 LLM、零 IO**）。
- 红线以 DSL 声明式组织：新增/调整红线 = 改表一行，不动 `scan` 逻辑；`Violation` 携带 `rule_id` + 命中片段，供 12.4 拼反馈。
- 与 Phase11 `render_movie_header` 同哲学：纯函数 → 每条红线正/反例单测锁死。

### D2 · judge_body_fabrication = LLM-judge（ADR-0019 D2）

- 新增纯函数 `judge_body_fabrication(body, overview, *, llm_call) -> list[Finding]` + 配套 prompt（[prompts/_shared/](../../prompts/_shared/) 或 [prompts/](../../prompts/)）：拿 DB overview 当唯一真值，判定 body 是否出现 overview 没写的电影细节 / 写错的导演名。
- `llm_call` 依赖注入：默认走项目 LLM 客户端，单测传 stub 免真联网。与 body_lint 同为「检测器」，不做编排。

### D3 · 命中即带反馈重试编排（ADR-0019 D3，复刻 rewrite.py，上限 K）

- 在 `run_publish` 的 `clean_publish_body` 之后接闸门：跑 `body_lint.scan` + `judge_body_fabrication`；命中则把「你违反了哪几条 + 原文片段」拼成 `repair_context` 喂回 LLM 重生成（**复刻 [scripts/rewrite.py](../../scripts/rewrite.py) 的 `repair_context` 模式**），上限 K 次。
- K 设小值（建议 1–2）。成本提醒：run_fanout 扇出 N 个 persona，接入后 LLM 调用量约 N ×（1 创作 + 1 judge + 至多 K 次重试）。

### D4 · 不硬失败：耗尽重试保留最后一版 + 挂 warnings（ADR-0019 D4）

- 重试 K 次仍违规 → **保留最后一版正文**，在 draft 里挂 `warnings`（记录剩余违规 rule_id / judge findings），**不硬失败**，交人工在面板兜底。
- 理由：正文质量是渐进优化，硬失败会阻断整条扇出；warnings 让残余问题可见、可追踪，同时 12.5 人工验收才是最终闸门。

### D5 · ADR-0019（已落地）

设计决策与理由固化于 [docs/adr/0019-c2-body-quality-gate.md](../../docs/adr/0019-c2-body-quality-gate.md)：在唯一创作环节 `run_publish` 引入正文质量闸门的理由（prompt 赌不住、验收标准需算子化）、body_lint（句式确定性）与 LLM-judge（语义幻觉）的能力边界分工（D0）、纯函数 + DSL 红线表设计（D1）、overview 作幻觉真值（D2）、复刻 rewrite.py 带反馈重试（D3）、不硬失败挂 warnings（D4）。引用 ADR-0013（影像平权语气）/ 0015（发布平台化元素清单）/ 0017（persona 视角草稿池）/ 0018（确定性抬头，闸门只管正文不碰抬头）。

> 编号说明：`0018` 已被 Phase11（确定性抬头投影）占用，故本 Phase 用 `0019`。本 ADR 已在 plan 落地前先行写定，各 TODO 只引用、不再新开。

---

## Todo 12.1 · [基线] 落地现有结构层基线（prompt + 池首中性默认稿 + tests）

**依赖：** 无（可先做）

**改动：**
- 从最新 `main` 检出 `feat/phase12.1-structure-and-neutral-default`，将工作区三文件裸改规整提交：
  - [prompts/compose_publish_xiaohongshu.md](../../prompts/compose_publish_xiaohongshu.md)（结构层去 AI 腔规则，上个会话所写）
  - [review_panel/drafts_adapter.py](../../review_panel/drafts_adapter.py)（池首中性默认稿）
  - [tests/test_review_panel_drafts_adapter.py](../../tests/test_review_panel_drafts_adapter.py)（配套测试）
- **注意**：本 TODO 只锁存既成基线，prompt 眼验尚未达标（那是 12.5）。

### 验收
- [ ] `pytest tests/test_review_panel_drafts_adapter.py` 全绿（chat 记录 100 panel 测试已过），无 regression
- [ ] 三文件裸改完整规整进 `feat/phase12.1-*` 分支，工作区回到干净
- [ ] 明确标注「仅基线锁存，正文质量达标留 12.5」，不误判为已完成去 AI 腔目标

---

## Todo 12.2 · [gate] body_lint 确定性句式校验器（纯函数 + DSL 红线表 + 单测）

**依赖：** 12.1

**改动：**
- 新增 [scripts/lib/body_lint.py](../../scripts/lib/body_lint.py)：
  - 模块级 `RULES: list[(rule_id, pattern, description)]` 红线 DSL 表。
  - `scan(body: str) -> list[Violation]` 纯函数（只检测、不改文本、不调 LLM、零 IO）。
  - `Violation` 携带 `rule_id` + 命中片段（供 12.4 拼 `repair_context`）。
  - 覆盖：硬转场「而这部…电影」、说破句「(都|背后是)…(同一种|同一个)…」「无论是…还是…」、接受度单独成句。
- 实现须遵循已落地的 [docs/adr/0019-c2-body-quality-gate.md](../../docs/adr/0019-c2-body-quality-gate.md) D0/D1（本 TODO **不再新开 ADR**）。

### 验收
- [ ] 每条红线有正例（应命中）+ 反例（不应命中）单测，全绿
- [ ] `scan` 为纯函数：不读文件、不查库、不调 LLM
- [ ] 新增红线 = 改 `RULES` 表一行，无需动 `scan` 逻辑（DSL 可扩展性验证）
- [ ] 实现与 ADR-0019 D0/D1 一致（检测器不做编排、句式红线不越界抓语义）

---

## Todo 12.3 · [gate] LLM-judge 幻觉校验器（overview 对正文查凭空细节）

**依赖：** 12.1（可与 12.2 并行）

**改动：**
- [scripts/compose.py](../../scripts/compose.py)（或 `scripts/lib/`）新增纯函数 `judge_body_fabrication(body, overview, *, llm_call) -> list[Finding]`：拿 DB overview 当唯一真值，判定 body 是否出现 overview 没写的电影细节 / 写错的导演名。
- 新增配套 prompt（[prompts/_shared/](../../prompts/_shared/) 或 [prompts/](../../prompts/)）。
- `llm_call` 依赖注入，单测用 stub 免真联网。遵循 ADR-0019 D2。

### 验收
- [ ] 注入 stub 时不真联网即可产出 `Finding` 清单
- [ ] 正例：body 编造 overview 没有的画面/人物/数字/错导演名 → 被判出
- [ ] 反例：body 只用 overview 授权信息 → 零 finding
- [ ] 与 body_lint 同为检测器，不做编排（不改文本、不决定重试）

---

## Todo 12.4 · [compose] 命中即带反馈重试编排（接进 run_publish）

**依赖：** 12.2 + 12.3

**改动：**
- [scripts/compose.py](../../scripts/compose.py) `run_publish`：在 `clean_publish_body` 之后接闸门：
  - 跑 `body_lint.scan` + `judge_body_fabrication`；命中则拼「违反哪几条 + 原文片段」为 `repair_context` 喂回 LLM 重生成（复刻 [scripts/rewrite.py](../../scripts/rewrite.py) 模式，上限 K 次，K 建议 1–2）。
  - 重试耗尽仍违规 → 保留最后一版 + draft 挂 `warnings`（不硬失败，ADR-0019 D4）。
- 单测：stub LLM 模拟「首次违规 + 重试通过」/「重试耗尽」两条路径。

### 验收
- [ ] 单测覆盖「重试通过」与「重试耗尽挂 warnings」两条路径，全绿
- [ ] 闸门接在 `run_publish` 内 → run_fanout 每份 persona 草稿自动过闸
- [ ] `llm_call` 注入路径与现有 golden-snapshot 测试**零回归**
- [ ] 重试耗尽不硬失败：产物保留最后一版且 `warnings` 可见

---

## Todo 12.5 · [GATE] 眼验迭代闸门 [需人工验收]

**依赖：** 12.1–12.4 全部

**执行顺序：**
1. 真重放 05 场景（AI/广岛 +《The Creator》，tmdb 670292）跨 persona 出正文（不写 report、不合并）。
2. 三重确认：`body_lint` 计数（句式红线归零）+ `judge` 结果（幻觉压住）+ 人工眼验（Persona ①偏② 显形、3–4 段扫读密度）。
3. 等待人工 Go/No-Go；No-Go 回 12.2 / 12.3 / 12.4 / prompt 迭代。

**人工验收阻断说明：** 正文质量为主观判断，本 TODO 天然是人工验收阻断点。达标（Go）前**不标 complete、不写最终报告、不合并**；触发挂起须按规则输出 `⚠️ [PAUSED]` 并等待 `approve`。

**验收项：**
- [ ] 句式红线 `body_lint` 计数归零
- [ ] `judge` 幻觉 findings 压住（无编造画面/人物/数字、导演名正确）
- [ ] Persona ①偏② 显形、3–4 段扫读密度达标
- [ ] `[需人工验收 · Go/No-Go]`：达标前不标 complete、不写最终报告、不合并

---

## 风险与约束

- **能力边界必须讲清**：`body_lint` 只抓句式红线、抓不住语义幻觉；语义幻觉全靠 LLM-judge。两者互补，缺一漏网。
- **成本**：run_fanout 扇出 N persona，接入 judge + 重试后 LLM 调用量约 N ×（1 创作 + 1 judge + ≤K 重试）。K 必须设小值（1–2），否则扇出成本线性放大。
- **不硬失败纪律**：闸门是渐进优化器不是拦截器；重试耗尽保留最后一版 + 挂 warnings，交 12.5 人工兜底，绝不因正文违规阻断整条扇出。
- **零回归**：闸门接进 `run_publish` 会经过既有 golden-snapshot 路径；12.4 必须保证 `llm_call` 注入路径与现有测试零回归。
- **范围纪律**：本 Phase 只管**正文质量**，不碰 Phase11 已确定性投影的**抬头行**（ADR-0018 边界）；prompt 只改正文语气契约相关段。
- **基线与目标分离**：12.1 落地的 prompt 裸改是既成基线、眼验未达标；真正达标判定在 12.5，勿把 12.1 完成误判为去 AI 腔目标达成。
- **ADR 已先行落地**：`docs/adr/0019-c2-body-quality-gate.md` 在 plan 之前写定；各 TODO 只引用、不再新开 ADR。若实现中发现与 ADR 决策冲突，按「关键决策冲突」挂起并回改 ADR，不得静默偏离。