# 客观抽取 + 中性通道 + 撞车票：拆解 A0 的「单一中性源」，复活 ADR-0003 撞车判据

**Status**: **superseded**（2026-06-14；原为 `proposed`，3.8 GATE no-go 后从未升 accepted）

> **被取代说明**：Phase 3.8 于 2026-06-06 `GATE no-go`。本 ADR 的两条核心赌注归宿：
> - **「删 A1 / 中性 union 取代 A1」** → 被 [ADR-0006](0006-a1-as-held-out-oracle-per-persona-neutral-and-three-bucket-eval.md) D1 **推翻**（A1 转 held-out oracle、不删）。
> - **「客观地板中性 = 共享 · persona 无关」** → 被 ADR-0006 D2 改为「per-persona salience 选材 + persona 中立 wording」。
> - **管线四段 / 撞车票 / hypernym 锚 / 两个中性区分** → 概念保留，但通道结构（neutral/toned/fact-anchor query）整体被 [ADR-0009](0009-fragment-ladder-and-search-unit-architecture.md) 替换为 fragment ladder / search unit；hypernym 并入 ladder 的 objective levels，lens 并入 interpretive/perspective levels。
>
> **仍可参考**：A0 = verbatim-only + 客观扩展 pass 的职责切分思想，仍体现在 [`reality-deconstruction-contract.md`](../SSOT/reality-deconstruction-contract.md)（该契约本身待按 ADR-0009 同步，见 ADR-0009 §SSOT 待同步）。本 ADR 保留全文。

> **背景**：Phase 3.7 于 2026-06-05 `GATE_FAIL` 结案（见 [ADR-0004](0004-persona-emotional-diffusion.md) Outcome 与 [`output/Eval/phase3.7/GATE_RESULT.md`](../../output/Eval/phase3.7/GATE_RESULT.md)）。复盘硬数据：toned persona path 结构/双重 2 分率 **20.0%** vs A1 path **75.0%**（lift **−55.0%**）；`fit ↔ 共振` Pearson **r ≈ 0.14**（情绪滤镜**不**预测命中，**对题（topicality）**才预测）。本 ADR 是 **3.7 复盘后的重设计**，**取代 3.7 的部分做法**：3.7 让 A0 同时承担「中性事实源」与「中性替代词源」，复盘发现两条致命前提错误——**①原文文本本身已带价（valence），不存在真空中性源；②各 persona 对「什么算中性」本就不一致**。本 ADR 把 A0 被混为一谈的职责**拆成三件事**，并**复活 [ADR-0003](0003-multi-agent-resonance-quality-and-a1-as-peer.md) 的撞车主判据形状**（neutral + ≥1 creative）。
>
> **核心赌注（post-3.7）**：3.7 的失败不是「persona 没用」，而是「价值重构（valence reframing）把用词推离了对题嵌入所奖励的位置」。本 ADR 的对策——**强制 hypernym 锚 keep toned 对题**，并新增**中性通道**承担召回（recall），让 toned 只需在其上**加精度/加汇聚（precision/convergence）**。

## 决策（管线与判据 · 实现须一致）

### 管线四段（A0 → 客观扩展 → per-persona alt-creator → screenwriter）

| 代号 | 定稿 |
| --- | --- |
| **P-Extract（A0）** | A0 = **纯逐字抽取**（pure verbatim extraction）：who / where / when / why / how / result + `role` + `relations`。**逐字记录原文用词，把原文自带的价当作事实保留**。A0 **不产任何「中性」替代词、不做任何扩展**。新闻输入为 **英文**，A0 = 英进英出，**无翻译步骤** |
| **P-Expand（共享客观扩展 pass）** | **一份共享拷贝**（非 per-persona），**只产 `hypernym` 上位词梯**，受 **客观性试金石** 闸门约束（「A2 社会学家与 A4 神话学者会不会给出不同答案？会 → 它是 lens，不是 objective」）。**丢弃 inert 字段** `geocode` / `coordinates` / `scale` / `scene_archetype`（理由见 §为什么·惰性字段） |
| **P-Lens（per-persona alt-creator）** | 产 **valence spectrum，且 persona 相对（persona-relative）**：**每个 persona 的价值轴**定义其正/负；**同一元素**对一个 persona 为正、对另一个可为负（如 `rumor spreader`（负 · The-Ruler）vs `truth-teller against power`（正 · The-Outlaw））。**仅 fact-entailed**（事实蕴含）；**禁新增事件/人物/指控** |
| **P-Compose（screenwriter）** | 从 **三层溯源池（3-layer provenance pool）** 组装 pseudo：`surface`（逐字原文词）/ `hypernym`（客观共享桥）/ `lens`（persona 相对价）。**每层可含多个 fact-entailed 词** |

### 两个「中性」（必须区分清楚，否则度量失真）

| 中性 | 定义 | 作用域 | 用在哪 |
| --- | --- | --- | --- |
| **(a) OBJECTIVE-FLOOR neutral（客观地板中性）** | `surface` + `hypernym` | **共享 · persona 无关** | **中性通道**用它，保证通道留在题面（topical）、命中率（hit-rate）指标可横向比较 |
| **(b) PERSONA-MIDPOINT neutral（persona 中点中性）** | 某 persona 价值轴的**中点** | **私有 · 仅活在该 persona 的 lens spectrum 内** | 仅 lens 内部参照（即现 alt-pool 的 `valence: neutral` 桶），**不**进中性通道 |

> 这是本 ADR 最易被实现者混淆的点：中性通道走 **(a)**，**不是** **(b)**。走 (a) 才能让 12 条中性 pseudo 落在同一客观地板上，hit-rate 分母与口径才一致。

### 两通道 + 撞车计分

| 代号 | 定稿 |
| --- | --- |
| **C-Neutral（中性通道）** | 每 persona 发**恰好 1 条**中性 pseudo（客观地板：`surface`+`hypernym`，**无 lens**）。角色 = **题面召回骨架（topical recall backbone）+ 度量基线**。**本通道取代 A1** |
| **C-Toned（语气通道）** | 每条 toned pseudo = **hypernym 锚（留在题面）+ lens 倾斜**；它**发自己的 anchored 检索 query**（故能与中性「殊途同归」汇聚到同一部电影） |
| **撞车主判据（复活 ADR-0003 形状）** | 中性通道整体算 **1 张去重 agent 票**（union of all neutral pseudos' hits）。**优质候选 = 中性票 + ≥1 toned lens 汇聚到同一部电影**。如此既防 **12 条近重复中性 pseudo 饱和/毒化撞车信号**，又不饿死它 |

### 新诊断指标 · NEUTRAL HIT RATE

- **定义**：每部电影的 `neutral_hit_rate = (命中该片的中性 pseudo 数) / (运行的 persona 数)`。**分母固定 = persona 数**（因每 persona 恰 1 条中性 pseudo）。
- **命中口径复用** `retrieve.py`：`top_k = 2` + `quality_floor = 0.40`。
- **目的**：检验假设「**中性命中率越高 ⇒ 越共振？**」。
- **纪律**：**必须在控制 `max_similarity` 的前提下分析**，否则它只是相似度的代理（similarity proxy）。**注意它 top-k 敏感**。

### A1 退场（不凭信仰删除）

- A1 **退役**，由**中性通道 union** 取代。
- **但**：**首轮验证 run 必须并跑 A1**，证明 **中性 union 检索出 A1 命中的超集（superset）、且 2 分率 ≥ A1** 之后，**才**删 A1。**不凭信仰删除**。

## 为什么这能打败 3.7 的失败

1. **3.7 根因 = 对题漂移**：valence reframing 把用词推离对题嵌入所奖励的位置（toned 20% vs A1 75%，lift −55%；`fit↔共振 r≈0.14`）。
2. **强制 hypernym 锚**：toned pseudo 必带 hypernym 锚 → 留在题面，截断漂移。
3. **中性通道扛召回**：召回由中性通道承担，**toned 只需加精度/加汇聚**，不必独自背对题责任——这正是 3.7 压垮 toned 的负担。
4. **复活 ADR-0003 撞车**：把「优质 = 多镜头交汇」重新立为主判据，与命中分（二级排序）解耦。

### 惰性字段（justify P-Expand 丢弃）

`retrieve.py` 只把 `pseudo.text` 送进嵌入（`QUERY_TEMPLATE.format(pseudo=...)`，匹配 `agents[].pseudos[].text`）。`geocode` / `coordinates` / `scale` / `scene_archetype` **从未进入嵌入**、对匹配**完全惰性（inert）**，故客观扩展 pass 直接丢弃，不再为它们花抽取/维护成本。

## 两个互补诊断回答「产品到底是谁」

| 诊断 | 问题 | 控制变量 |
| --- | --- | --- |
| **① neutral-hit-rate vs 共振** | 中性「广度」是不是真信号？ | 控制 `max_similarity` |
| **② toned-convergence vs 共振** | lens 是否在中性之上**加了精度**？ | 控制 `max_similarity` |

- **①强 ②弱** ⇒ 产品是「**中性召回 + 命中率排序**」，persona **降级为解读者（interpreters）**。
- **①&② 双强** ⇒ **persona 赌注成立**。

## 语言（English-only chain）+ 防火墙

- **整条机器链全英文**：输入英文新闻 → A0 → alt-pool → pseudo → 检索 → 候选。**唯一翻译** = 最终推荐文案 → 中文（给总编）。
- **单语链 = 防火墙收益**：P-Select 的 **事实蕴含审计在单一语言内完成**（跨语言 entailment 正是注入藏身处）。

## 后果 / 已知局限

- **防火墙保证由强变弱（诚实记录）**：反注入从「**封闭世界**（是否在 decon 里？）」弱化为「**分层类型闸（typed-layer gates）**」：`surface` 逐字 / `hypernym` 过客观性试金石 / `lens` 须 fact-entailed。
- **alt-creator = 唯一注入风险点**：需 **pilot 人工审计** hypernym-vs-lens 分层是否被混用/越界。
- **neutral_hit_rate 是诊断、非闸门**：未经控相似度前不得当结论；top-k 敏感。
- **撞车票形状与现 `retrieve.py` 不同**：现实现是对称的 `distinct_agents >= 2`（A1 baseline 不进 `triggered_by`）；本 ADR 改为**非对称**「中性 union 1 票 + ≥1 toned」，须改码（见 §SSOT 待改清单），实现前勿混用旧口径。
- **不解封 Phase 4**；本 ADR **仅记录决策**，不改契约/卡/代码（另列任务）。

## OPEN ITEMS（显式留待）

- **(a) toned 的检索形态**：「**发自己的 anchored query**」（默认，由汇聚判据隐含）vs 纯 re-ranker —— **锁定为「发 anchored query」**，除非后续显式重启讨论。
- **(b) P-Abstain fit 阈值**：仍**由留出集数据驱动**，不硬编码（承接 ADR-0004 P-Abstain）。
- **(c) 价值轴写法**：如何把 persona 相对价值轴写进 12 张 persona 卡（实现细节）。
- **(d) 防火墙人工审计**：pilot 审计 hypernym-vs-lens 分层。**（翻译保真项已 moot——输入即英文，无 cross-lingual 步骤，故删除该 open item）**

## SSOT 待改清单（Phase 3.8 · gated）

> **Phase 3.8 仍 gated**；以下仅记账，**GATE go 前不执行**，且属**另一任务**（本任务只建本 ADR）。

- [`docs/SSOT/reality-deconstruction-contract.md`](../SSOT/reality-deconstruction-contract.md)：A0 = **verbatim only**；新增**客观扩展 pass**（只产 hypernym 梯）；引入**三层 provenance**（surface/hypernym/lens）；**丢弃 inert 字段**（geocode/coordinates/scale/scene_archetype）。
- [`docs/SSOT/personas-12.md`](../SSOT/personas-12.md) + 各 `prompts/personas/<id>/persona_card.md`：写入 **persona 相对价值轴（persona-relative value axis）**。
- [`prompts/_shared/persona_alt_creator_contract.md`](../../prompts/_shared/persona_alt_creator_contract.md) + [`prompts/_shared/persona_screenwriter_contract.md`](../../prompts/_shared/persona_screenwriter_contract.md)：persona 相对 valence、**两个中性的区分**、三层 provenance。
- [`scripts/retrieve.py`](../../scripts/retrieve.py) + `scripts/score_eval_candidates.py` + `scripts/summarize_eval.py`：**中性通道 = 1 张去重票**、新增 `neutral_hit_rate` 字段、**控相似度（similarity-controlled）的分析**口径。
- [`CONTEXT.md`](../../CONTEXT.md)：补术语（客观地板中性 / persona 中点中性 / 中性通道 / 语气通道 / neutral hit rate / 三层 provenance）。
- **本 ADR `Status` → `accepted`** 仅在 Phase 3.8 GATE go 后。

## 相关 ADR / 文档

- [ADR-0002](0002-pivot-to-event-logic-resonance.md) — 表层共振合法、事件逻辑解构（本 ADR 的对题召回前提）。
- [ADR-0003](0003-multi-agent-resonance-quality-and-a1-as-peer.md) — 多 agent 撞车主判据 / A1 平权（**本 ADR 复活其「中性 + ≥1 creative」撞车形状**）。
- [ADR-0004](0004-persona-emotional-diffusion.md) — Phase 3.7 情绪化扩散赌注；**2026-06-05 `GATE_FAIL`**，本 ADR 取代其「A0 单一中性源」做法。
- [`docs/eval-the-bet.md`](../eval-the-bet.md) §4 / §5.1 — 共振 rubric。
- [`output/Eval/phase3.7/GATE_RESULT.md`](../../output/Eval/phase3.7/GATE_RESULT.md) — 3.7 结案数字（20% vs 75%、lift −55%、r≈0.14）。
