# A1 转 held-out oracle + per-persona 中性多样化 + 三桶对照度量：干净地重赌「组合拳」

**Status**: proposed

> **背景**：Phase 3.8 于 2026-06-06 `GATE no-go` 结案（见 [`output/Eval/phase3.8/GATE_RESULT.md`](../../output/Eval/phase3.8/GATE_RESULT.md)）。结案后复盘(逐 run 重算，数字与 GATE_RESULT 一致)发现：**3.8 的 no-go 性质不是「组合拳赌输」，而是「实验根本没跑成」**——两个核心赌注（中性通道多样召回、组合拳 > 纯事实）**一个都没被真正测到**。三条复盘硬证据：
>
> 1. **中性通道退化(执行缺陷，非概念失败)**：12 条「客观地板中性」pseudo **逐字雷同**(同一新闻下 The-Creator 与 The-Caregiver 的 `n1` 仅尾部 hypernym 标签差两词)。原因：persona 差异化只在 **toned** 通道落地，**neutral** 通道所有 persona 选了同一组碎片 `[why-0, how-0, how-1, how-2, result-0]` + 逐字照抄原文。结果 10–12 条中性在 `top_k=2` 下塌缩为 **2 部电影**(10 run 里 7 run 命中数=2)。ADR-0005 §风险预言的「12 条近重复 ⇒ 命中率退化」**实测发生**。
> 2. **A1 不是该删，而是质量最高**：按打分数据分三桶——**A1 命中 67%**(12/18 二分)、**中性涉及 62%**(10/16)、**纯情绪(toned-only，无中性支撑) 35%**(15/43)。A1 既召回最广(全局 44 唯一 vs 中性 union 26)又质量最高。ADR-0005「中性 union 取代/删除 A1」的赌注**双输**。
> 3. **GATE 在设计上无法回答诊断②**：`summarize_eval.py` 中 `is_neutral_only = neutral_vote and not toned_convergence`，而 `toned_convergence = distinct_agents>=1` 恒真；叠加 high-hit review 只收「≥5 命中分且命中分仅由 toned 行产生」——**纯中性候选在进打分池前就被筛掉**。故 `neutral_only_scored = 0` 是**结构性必然**，诊断②「弱/不可分离」是**度量伪命题**，不是反对 persona 的证据。
>
> **核心赌注（post-3.8）**：3.7→3.8 两轮都偏向「对题(topicality)才预测命中，情绪不预测」，但**「事实 + 情绪 = 表层 + 深层双重共振」这个组合拳从未被干净验证过**。本 ADR 不退守纯召回，而是**先把实验修成可跑、可测，再赌一次组合拳**——把 A1 从「待删的竞争者」改造成「不参与判断的 held-out 质量神谕(oracle)」，让 per-persona 中性腿真正站起来，并补齐三桶干净对照。

## 决策（管线与判据 · 实现须一致）

### D1 · 推翻 ADR-0005「删 A1」：A1 转 held-out oracle

| 条目 | 定稿 |
| --- | --- |
| **A1 不删** | 撤销 ADR-0005 §「A1 退场」。A1 baseline 检索保留 |
| **A1 不参与 3.9 判断** | A1 命中**不进候选池、不进撞车票、不进排序**。仅作**并跑基准** |
| **A1 = 质量/召回神谕** | A1 提供「正确答案集」的代理：**核心实验问题 = per-persona 多样化的 12 条中性，能否在召回(覆盖 A1 命中)与质量(2 分率 ≥ A1)上追平甚至超过 A1** |
| **删 A1 的前置不变但后置** | 仍遵 ADR-0005 纪律「不凭信仰删」；唯有 3.9 证明中性 ⊇ A1 召回且质量 ≥ A1 后，**未来某轮**才删。本轮只衡量、不删 |

### D2 · per-persona 中性多样化（修正 ADR-0005「客观地板中性=共享」）

| 条目 | 定稿 |
| --- | --- |
| **salience 可 persona 化（架构强制）** | 每个 persona 按**自己的镜头**决定**强调哪些事实**——persona LLM **只输出既有 `element_id` 的有序列表**(`salience` 字段),取 Top-K 作为 `fragment_ids` 驱动中性碎片 SELECTION:如 The-Caregiver 更重 `result`(谁受影响)/`who`(脆弱群体)、The-Creator 更重 `how`(机制/设计)。salience **只重排/取子集既有 ids,不新增词** |
| **valence 不可 persona 化（架构强制，非 prompt 纪律）** | 中性句由**模板从所选碎片的 `surface`(逐字原文) + `hypernym`(客观地板)拼装**,**persona LLM 永不书写中性散文** ⇒ valence 在物理上无载体可渗入(**无 lens、无价**)。三层守卫:① 架构(只发 ids)② 来源(只取 surface+hypernym)③ 运行时守卫(拒 lens 词,已存在)。**「选材 persona 化、措辞中立」由架构保证,不靠 prompt 自律** |
| **对 ADR-0005 的修正** | ADR-0005 把客观地板中性定为「共享 · persona 无关」；本 ADR 改为 **persona 相对的 salience + persona 中立的 vocabulary**。目的：让 12 条中性**真正不同**，恢复召回多样性 |
| **唯一注入风险点** | salience/valence 边界即新防火墙焦点(3.8 已现 The-Lover 中性漏 lens 词报错)；pilot 必须专审此条 |

### D3 · 坚持情绪共振主轴（不退守纯召回）

- 维持 ADR-0004/0005 的 **persona 情绪共振赌注**：产品主轴仍是 persona，**不**降级为「中性召回 + 命中率排序」。
- 3.9 目标 = **第一次干净地验证组合拳**：`中性(事实联系) + toned(感受联系) = 表层 + 深层双重共振`，是否**优于纯事实**。

### D4 · 度量改造（让 3.8 测不出来的诊断②变可测）

| 条目 | 定稿 |
| --- | --- |
| **三桶可评对照** | 每个候选可归入并被打分：**① 纯事实(中性/oracle 命中、无 toned)**、**② 纯情绪(toned-only)**、**③ 组合(中性票 + ≥1 toned 汇聚)**。三桶 2 分率/双重率横向可比 |
| **纯中性候选必须能进打分池** | 取消「≥5 命中分且命中分仅由 toned 行产生」的过滤——否则诊断②对照组永远空。中性命中也计入打分入选 |
| **重定义 toned_convergence** | `distinct_agents>=1` 太松，使 neutral-only 恒空。改为**真实区分「有 toned 汇聚」vs「仅中性」** |
| **留出冻结纪律(enforced)** | **只在观察集调** prompt/阈值 → 冻结 → 留出集**只打一次分**。留出 ≈ 观察 ⇒ 提升为真；留出垮 ⇒ 过拟合 |
| **不扩 run · 纵向多打分** | **不扩语料**(观察/留出 run 数维持 3.8 规模)。改为**每条新闻多打分(纵向加深,非横向扩 run)**补统计力(诊断①② 样本单位 = per-candidate,多打分即增样)；**批次通过率闸仍按 run 计**。并由 **LLM-as-judge** 规模化打分、人工只复核分歧 |
| **LLM-as-judge** | 引入规模化评委;**以观察集人工分作校准/验证集**，judge 与人工对齐后方采信。突破人工瓶颈 |

### D5 · 裁决口径（本轮 GATE 该回答什么）

| 子问 | 通过条件 |
| --- | --- |
| **Q1 · 中性腿是否站起来** | per-persona 中性的召回覆盖 A1 命中(superset)且 2 分率 ≥ A1(oracle 对照) |
| **Q2 · 组合拳是否成立** | 组合桶(③) 双重/结构 2 分率 **显著 >** 纯事实桶(①)，控相似度后仍成立(真·诊断②) |
| **Q3 · 情绪是否净加分** | 纯情绪桶(②)即便低，也不拖累——组合相对纯事实的增量来自「汇聚」而非「漂移」 |

### D6 · 中性通道 salience 选材机制（架构强制 · 3.9 执行）

> **已决(2026-06-06)**。D2 把「选材 persona 化、措辞中立」定为铁律；D6 给出**如何实现**该铁律的落地机制。核心原则 = **「选哪些事实(salience)」与「用什么措辞(valence/wording)」拆开，靠架构而非 prompt 纪律强制**。

| 条目 | 定稿 |
| --- | --- |
| **架构拆分** | persona LLM(既有 per-persona alt-creator 调用)**只输出一个排序的既有 `element_id` 列表**(新增 `salience` 字段)表达「本 persona 最在意哪些事实」；它**绝不书写中性散文**。中性句仍由模板从所选碎片的 `surface`(逐字原文) + `hypernym`(客观地板)**拼装**(`build_objective_floor_neutral_pseudo`)。因 persona 永不书写中性措辞，valence 在物理上无法渗入 |
| **prompt = salience 选材指令** | 加入 alt-creator 契约:返回 `salience` = 本 persona 价值轴最关注的**既有 `element_id` 有序列表(最→次)**;**只重排/取子集既有 element_ids,不新增词、不写评注**。取 **Top-K(建议 4–5)** 个最显著碎片作为 `fragment_ids` 传给 `build_objective_floor_neutral_pseudo` |
| **校验(硬约束)** | `salience` **必须是既有 element_ids 的子集/排列**(subset/permutation)——代码侧硬校验,非法 id 或新增词即拒 |
| **现状只差一步** | 客观地板中性**本就不是 LLM 写的**——`build_objective_floor_neutral_pseudo` 对一组**固定默认碎片**(`_default_neutral_fragments`:首 `why` + 前 3 `how` + 首 1 `result`,对每个 persona 都一样)拼接逐字 `surface` + 客观 `hypernym`。措辞客观性**已由结构保证**;唯一缺的就是 **per-persona 的碎片 SELECTION**——而该函数已接受 `fragment_ids` 参数,只是从未 per-persona 传入 |

**三层边界强制(强→弱)**：

1. **架构**：persona 只发 `element_id`、不发中性散文 ⇒ valence 无载体。
2. **来源(provenance)**：拼装只取 surface+hypernym 词,lens 词在结构上被排除。
3. **运行时守卫(已存在)**：「中性 pseudo 不得含 lens 词 / lens provenance」⇒ 硬失败 + 修复。

**两个子决策(已决)**：

| 子决策 | 定稿 |
| --- | --- |
| **① salience 来源** | **主选 (B) 由 alt-creator LLM 按新闻动态决定 salience**(从此起步)。**回退 (C) 混合**——仅当 3.9 pilot 显示太乱/不稳时启用,且混合**必须保留 LLM 自由**:只手写 per-persona 的**软偏好/先验**(如「The-Caregiver 倾向关注 who-is-affected 与 outcomes」),**绝不**写死决定具体碎片的硬规则;LLM 仍在软先验内做最终的 per-news 选择 |
| **② who/where(人物/地点)** | 每个 persona **可访问全部 who/where 元素**(它们留在可选池中),但**各 persona 自行决定是否使用**——**不再无条件注入**。即现行代码(`personas.py` 约 346–350 行:无条件把所有 `who-`/`where-` 词追加进每条中性 pseudo)须改:who/where 变为**可被 salience 选取的候选**,而非强制纳入 |

**多样性守卫(pilot)**：批内两两检查中性 pseudo 是否近重复(高文本相似度 **且** 所选碎片集合差异低于下限)。**硬失败**仅当**中性与 toned 均近重复**;若仅中性撞车而 toned 仍各异,则**降级为 warning 并继续**(差异化由 toned 通道 + 检索兜底)。中性句内同一 surface 文本只渲染一次(按归一化 surface 去重,非仅 element_id)。

**例**：The-Caregiver 应**选** result/who 碎片(谁受影响)但**写**成中性「居民受停电影响」,而非带价的「脆弱家庭陷入危险」——因措辞由模板从 surface+hypernym 拼装,带价表述无从产生。3.9 pilot 须专审此边界。

## 为什么这能修好 3.8 的「实验没跑成」

1. **A1 当尺子不当选手** ⇒ 「中性能否替代 A1」第一次有**干净、外部的正确答案集**可比，不再自证。
2. **per-persona salience** ⇒ 中性 12 条真正各异，恢复召回多样性，**中性腿站起来**，组合拳的一半才有力。
3. **三桶可评 + 纯中性入池** ⇒ 诊断②第一次有**非空对照组**，「组合拳 > 纯事实」可被证实/证伪。
4. **留出冻结 + 扩样** ⇒ GATE 数字第一次**诚实且有统计力**。

## 后果 / 已知局限（诚实记录）

- **route (a) 是更难的路**：per-persona salience 而非 ADR-0005 的共享地板——salience/valence 泄漏是主要失败模式，靠硬契约 + pilot 审计兜底；若 pilot 反复泄漏，回退到「2~3 条多视角共享客观 pseudo(A1 配方)」为 plan B。
- **A1 并跑成本保留**：A1 不删 ⇒ 每 run 仍并跑 A1，retrieve-a1 脚手架维持。
- **人工打分仍是瓶颈**：3.9 不扩 run 但要纵向多打分，瓶颈靠 **LLM-as-judge**(已决引入)缓解；judge 须先用观察集人工分校准对齐，否则其分不采信。
- **neutral_hit_rate 仍是诊断非闸门**：未控相似度不得当结论；top-k 敏感(承接 ADR-0005)。
- **不解封 Phase 4**；本 ADR **仅记录决策**，不改契约/卡/代码(另列任务，Phase 3.9 gated)。

## OPEN ITEMS（显式留待）

> 已决条目已迁出本节：扩样/纵向多打分 → **D4**；LLM-as-judge → **D4**；salience 选材机制(原 (d)) → **D6**。本节仅保留**真正未决**项。

- **(c) 第二匹配轴(延后但登记)**：alt_pool 的 hypernym/alternatives ↔ 电影 `genres`/`keywords` 结构化匹配，可能是「深层共振」真正来源，超出纯向量相似度。3.9 暂不做，记为后续候选。
- **(e) P-Abstain fit 阈值**：仍由留出集数据驱动，不硬编码(承接 ADR-0004/0005)。

## SSOT 待改清单（Phase 3.9 · gated）

> **Phase 3.9 仍 gated**；以下仅记账，**GATE go 前不执行**，且属**另一任务**(本任务只建本 ADR)。

- [`scripts/personas.py`](../../scripts/personas.py)：中性通道碎片选择改 **per-persona salience**(镜头驱动选材、措辞守客观地板)；硬约束 salience≠valence。具体(承接 **D6**):
  - 用 **per-persona salience 驱动的 `fragment_ids`** 取代 `_default_neutral_fragments` 的固定默认碎片用法——把 persona `salience` 的 Top-K(4–5) 传入 `build_objective_floor_neutral_pseudo(fragment_ids=...)`(该参数已存在,只是从未 per-persona 传)。
  - who/where 改为**可选 salience 候选,不再强制追加**:删除/收口 `build_objective_floor_neutral_pseudo` 约 346–350 行「无条件把所有 `who-`/`where-` 元素追加进 floor_terms」的逻辑,改由 salience 选取决定是否纳入(全部 who/where 仍留在可选池中)。
  - 新增**多样性守卫**:断言一批 12 条中性 pseudo 不近重复(两两文本相似度 < 阈值 **或** 所选碎片集合差异 ≥ 最小值);退化 ⇒ 失败/重生成。
- [`prompts/_shared/persona_screenwriter_contract.md`](../../prompts/_shared/persona_screenwriter_contract.md) + [`prompts/_shared/persona_alt_creator_contract.md`](../../prompts/_shared/persona_alt_creator_contract.md)：写入「中性 = persona 相对 salience + persona 中立 vocabulary」铁律。具体:在 alt-creator 契约新增 **`salience` 字段规格**——本 persona 价值轴关注的**既有 `element_id` 有序列表(最→次)**,**只重排/取子集既有 ids、不新增词、不写散文/评注**;并明确规则「**salience 只驱动中性碎片 SELECTION,绝不影响 wording**」(中性措辞永由模板从 surface+hypernym 拼装)。
- **验证(校验)**：`salience` **必须是既有 `element_id` 的子集/排列**(subset/permutation)——代码侧硬校验,非法 id 或新增词即拒。
- [`scripts/retrieve.py`](../../scripts/retrieve.py)：A1 **仅并跑、不进候选/撞车/排序**(held-out oracle)；保留 superset/质量对照输出。
- [`scripts/score_eval_candidates.py`](../../scripts/score_eval_candidates.py)：**纯中性候选入打分池**(取消「命中分仅 toned」过滤)。
- [`scripts/summarize_eval.py`](../../scripts/summarize_eval.py)：重定义 `toned_convergence`/`is_neutral_only`，产**三桶(纯事实/纯情绪/组合)** 对照口径；A1 = oracle 对照(非 deletion 闸)。
- 评测编排/manifest：**不扩 run** + **纵向多打分** + **留出冻结纪律**(观察调参→冻结→留出一次性打分)。
- 新增 **LLM-as-judge** 打分器(新脚本)：规模化评分，**以观察集人工分校准/验证**，人工只复核分歧。
- [`scripts/run_persona_batch.py`](../../scripts/run_persona_batch.py)：persona 生成**并发化**(现为假串行 async)——`Semaphore(N=3)` + `gather` + 原序重组 + 启动抖动 sleep 5–15s + 429 退避重试 + `--concurrency` 参数(效率优化，非判据)。
- [`CONTEXT.md`](../../CONTEXT.md)：补术语(held-out oracle / per-persona salience / 三桶对照 / 留出冻结)。
- **本 ADR `Status` → `accepted`** 仅在 Phase 3.9 GATE go 后。

## 相关 ADR / 文档

- [ADR-0005](0005-objective-extraction-neutral-channel-and-collision-vote.md) — 客观抽取 + 中性通道 + 撞车票；**本 ADR 推翻其「删 A1」与「客观地板中性=共享」，保留其管线四段/撞车形状/hypernym 锚**；ADR-0005 保持 `proposed`(3.8 GATE no-go，未升 accepted)。
- [ADR-0004](0004-persona-emotional-diffusion.md) — Phase 3.7 情绪化扩散赌注(`GATE_FAIL`)；本 ADR 延续其 persona 情绪共振主轴。
- [ADR-0003](0003-multi-agent-resonance-quality-and-a1-as-peer.md) — 多 agent 撞车主判据 / A1 平权(本 ADR 沿用撞车形状，A1 改 oracle 角色)。
- [ADR-0002](0002-pivot-to-event-logic-resonance.md) — 表层共振合法、对题召回前提。
- [`output/Eval/phase3.8/GATE_RESULT.md`](../../output/Eval/phase3.8/GATE_RESULT.md) — 3.8 结案(batch 80% / quality 62.5% / A1-superset 1/10 / 诊断①② 弱)。
- 3.8 复盘三桶数据(本 ADR §背景)：A1 67% / 中性 62% / 纯情绪 35%；中性 union 26 vs A1 44；中性 12 条逐字雷同实证。
