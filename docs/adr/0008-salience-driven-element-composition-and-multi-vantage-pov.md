# salience 驱动的元素中心构图、valence 降级为元素层可选着色、多视角 POV 派生

**Status**: accepted（Phase 3.11.8 GATE go, 2026-06-13；D1 注意力清单 / D2 轴对齐 / D3 元素中心构图核心思想继续有效）；**supersedes ADR-0007 D6（单视角派生），修订 D7 通道结构（原则继承），D8 漏斗全量继承；通道结构 / POV channel / 双地板已由 [ADR-0009](0009-fragment-ladder-and-search-unit-architecture.md) supersede（Phase 3.11.6b）**

> **背景**：ADR-0007 D6–D8（`proposed`）原计划把 POV 作为「单一派生视角的追加通道」引入。Phase 3.11.0 v1 权威措辞（contract 内 12 persona 单 canonical vantage 表，搁置于 `feat/phase3.11.0-pov-wording-source` @ `834e788`）交人工验收时，总编对生成层架构做出更深的修订决定，本 ADR 把这次讨论的结论钉死。
>
> 触发讨论的四个观察：
>
> 1. **模糊地带是常态**：decon 元素中很多**无法被归入正/中/负两极轴**——逐元素供应 valence 光谱的期待（ADR-0005/0006 alt-pool 语义）对模糊元素构成「硬安极性」的压力。
> 2. **persona 的 Who 极本身是复合集**：The-Caregiver 正极 = 守护者**与**脆弱者、The-Outlaw 正极 = truth-teller / scapegoat / whistleblower——单 canonical vantage 浪费了清单的另一半。
> 3. **「pseudo 算正还是负」是不存在的问题**：The-Ruler 基于新闻完全可能写出 *authority（+）在 ungoverned zone（−）建立新秩序*——这恰是 Ruler 的**原型故事**（正极作用于负极），却无法被归类为正向或负向 pseudo。电影 overview 的语言天然如此（"a desperate father **(+)** fights a corrupt system **(−)**"）。persona-ness 的判据是**轴对齐**（每个元素被透过本 persona 价值轴框定），不是整体方向。
> 4. **变化应由元素中心性组织，而非 valence 覆盖**：系统已有逐新闻的 salience 排序（alt-creator 输出），它才是「本 persona 这条新闻最在意什么」的自然驱动器。
>
> **valence 考古结论**（修订前提）：正/中/负从来不是为了保证 pseudo 条数（那是 P-Force 的职责），它承担三个职能——① lens 着色的方向材料（ADR-0004 赌注本体：把 query 向量推向带价值框定的 overview 语言空间）；② 跨 persona 异号多样性；③ 「两个 neutral」隔离。salience 驱动构图替代的是**变化/覆盖**职能，替代不了**着色**职能——故 valence **降级**而非删除。

## 决策

### D1 · 注意力清单（attention inventory）——persona card 价值轴的重新定位

| 条目 | 定稿 |
| --- | --- |
| **清单化** | persona card `价值轴 (Value Axis)` 的 Who / Where / When 极重新定位为该 persona 的**叙事注意力清单**：它列出本 persona 叙事中重要的元素**原型**（人物类型 / 地点类型 / 时间面向），是 P-Select 中心化与 POV 视角派生的 **SSOT** |
| **极性降级为可选着色标注** | `valence`（positive / neutral / negative）退为 alt-pool 元素层的**可选**标注：lens 对该元素**真有立场才标**，模糊地带不标（用 surface / hypernym 白描）。**取消逐元素覆盖正中负光谱的期待**（修订 ADR-0005/0006 alt-pool 语义；schema 字段保留，向后兼容） |
| **着色职能保留** | 有立场的元素照常按价值轴框定措辞（P-Select 选词方向 + P-Tone 句级语气）——ADR-0004 的情绪扩散赌注不动 |
| **两个 neutral 不变** | objective-floor neutral 与 persona-midpoint 的隔离照旧；persona-midpoint 仍是 lens 光谱中段的可选标注 |

### D2 · pseudo 无极性，判据 = 轴对齐（axis-alignment）

| 条目 | 定稿 |
| --- | --- |
| **pseudo 层无极性概念** | 任何 pseudo 不被归类为正向/负向；**两极同场张力是欢迎的**（原型故事 = 正极对抗/作用于负极） |
| **轴对齐判据** | 一条 pseudo 属于某 persona 的判据：其中的元素被**逐个透过本 persona 价值轴框定**（authority→秩序守护者、那片地→失管地带），而非整体朝某方向倾斜 |
| **P-Select 引导改写** | screenwriter 契约的 "prefer alternatives that match this persona's value tendency"（读起来像要求整条 pseudo 单向倾斜）改为「**逐元素轴框定**；两极同场张力欢迎」 |
| **pseudo 必需声明** | 每条 pseudo 只须声明：**中心元素 id** + **通道类型**（neutral / toned 第三人称 / focalized）+ `fit`。无 pseudo 级极性字段 |

### D3 · salience 驱动的元素中心构图（贪心声明式）

| 条目 | 定稿 |
| --- | --- |
| **salience 职责扩展** | 从「中性通道选材」扩展为「**全通道构图驱动**」：逐新闻 salience 排序（alt-creator 现有输出）决定 toned/POV pseudo 以哪个元素为中心 |
| **贪心声明式中心化** | 每条 toned/POV pseudo **显式声明 1 个中心元素 id**（+ 自然蕴含的 2–4 个支撑元素）；中心按 salience **自上而下**取——能以该元素为中心成稿就写，不能则顺延下一位；**各条 pseudo 中心互异** |
| **LLM 声明、代码记分** | 运行时 LLM 只负责声明中心；排序与预算由**代码侧**按「中心元素的 salience 名次」确定性计算（否决「重要度×使用元素数量」乘法自评分——塞词激励 + 自评不可信 + 重复计权） |
| **防塞词** | 60–120 词限制不变 + 支撑元素数上限（2–4）由守卫校验 |
| **铁律保留** | salience 仍**不影响中性通道 wording**——中性 n1 的模板拼装机制零改动（ADR-0007 D6 铁律中「中性通道不动」的部分**保留**；「alt-creator / salience 不动」的部分**废止**） |

### D4 · 多视角 POV 派生（supersede ADR-0007 D6 单视角）

| 条目 | 定稿 |
| --- | --- |
| **视角清单 SSOT = persona card** | 每 persona 的合法视角集 = card 注意力清单的 **Who 极原型**（复合集全量可用，不再收敛为单 canonical vantage）；contract 只留通用派生规则，**不再维护 12 行 directive 表**（v1 表作废） |
| **逐新闻落点由 salience 派生** | 当某条 pseudo 的**中心元素是 `who-*`** 且该角色**实例化清单中任一原型**时，该条写成 **focalized**（透过该角色的眼睛叙事）；否则写第三人称元素中心叙事。**不引入自由参数**——视角选择 = salience 排序 × 清单实例化，全程派生 |
| **共情座位原则** | 视角只从 Who 极中 persona **栖居**的原型派生；负极角色是 persona 审视的**对象**（被看），不是叙事座位（看出去）——透过对立面的眼睛叙事与 lens 立场打架，排除 |
| **硬守卫不变（继承 D6 铁律）** | focal 角色 ∈ decon 既有 `who-*`；只换「从谁的眼睛看」，**绝不新增内心戏/事件/因果/结果**；hypernym 锚保留；硬失败即重生成 |

### D5 · 双地板（继承 ADR-0007 D7 追加原则）

| 条目 | 定稿 |
| --- | --- |
| **地板一：中性 n1 零改动** | objective-floor 中性通道（题面召回地板）原样保留，3.10 已验证资产不动 |
| **地板二：≥1 条非聚焦第三人称 toned** | 每 persona 至少 1 条非 focalized 第三人称 toned pseudo——D7「追加不顶替」在新通道结构下的等价物，锁死匹配地板 |
| **focalized 纯增** | focalized pseudo 与第三人称 toned、中性 n1 并存检索，只增不减 |

### D6 · 打包归因 + provenance 标签分解（总编决策）

| 条目 | 定稿 |
| --- | --- |
| **打包归因** | 3.11 A/B（vs 3.10 基线）归因到**整个新生成设计**（元素中心构图 + 多视角 POV 一并），**推翻 ADR-0007「一次只动一个变量」对本轮的约束**——总编明确接受此代价，换取一次连贯的重设计而非两轮评测 |
| **provenance 标签** | 每条 pseudo 携带 provenance 标签（中心元素 id / 通道类型 neutral・toned・focalized / focal 角色 id），**池差按通道类型分解**，事后恢复粗粒度归因，不加跑次 |
| **度量=指南针（继承 D7）** | 度量仍为调优指南针非判决闸：POV-recalled 池差 + `POV变换` 子标签照旧 |
| **候选漏斗（继承 D8）** | 去重 → 汇聚排序 → judge 预筛 → 预算 top-N 四层全量继承；**绝不调高 judge 门槛控量**铁律不变 |

## 为什么这能解决问题

1. **模糊元素不再被硬安极性** ⇒ alt-pool 的事实蕴含压力下降，着色只发生在 lens 真有立场处——着色更准、幻觉面更小。
2. **轴对齐替代方向归类** ⇒ 「正极作用于负极」的原型故事获得一等地位，pseudo 更贴电影 overview 的天然语言形状。
3. **salience 中心化替代 valence 覆盖** ⇒ 变化由「persona 在意什么」组织，每条 pseudo 聚焦一个中心、query 向量更锐利；LLM 声明 + 代码记分保持可审计。
4. **多视角按 salience 派生** ⇒ 复合 Who 极的全量价值被使用，又不开放自由选择——D6「派生而非自由选」的精神在更宽的清单上成立。
5. **双地板 + 漏斗** ⇒ 匹配地板不塌、膨胀可控，与 0007 的安全结构无缝衔接。

## 后果 / 已知局限（诚实记录）

- **A/B 归因变粗**：vs 3.10 的差异是整包新设计；provenance 分解只能恢复通道级粗归因，无法严格隔离「构图改变」与「POV」各自的净效应。此为总编显式接受的代价。
- **alt-creator 契约语义变化**：取消光谱覆盖期待后，存量单测/守卫中按桶校验的部分需随 3.11 todos 更新；schema 字段保留保证向后兼容。
- **judge 不受影响**：judge 只看 news summary + movie overview（ADR-0007 已记），生成侧重构不触碰 3.10 校准资产。
- **塞词与中心声明真实性**：中心声明可能名不副实（声明 A 实写 B）——pilot 审计须专项核查（3.11.6）。
- **POV 事实漂移**：主要失败模式不变，仍靠硬守卫 + pilot 专审 + 运行时守卫三层兜底。
- **v1 措辞作废**：`feat/phase3.11.0-pov-wording-source` @ `834e788` 的 12 行 canonical 表按本 ADR 作废；其 CONTEXT 术语（候选漏斗 / POV-recalled）部分可回收。

## OPEN ITEMS（显式留待）

- **(a) 呈现层 POV**（继承 0007 OPEN a）：Phase 4 文案是否做 POV 聚焦。
- **(b) 预算上限 N**（继承 0007 OPEN d）：漏斗第 4 层 top-N 待 3.11 pilot 定。
- **(c) 中心元素粒度**：中心是否允许 `why-*`/`how-*`/`result-*` 等事件性元素与 `who-*`/`where-*` 实体元素同权重参与贪心——3.11.1 预测试观察后定。
- **(d) valence 可选化后的 P-Force 语义**：弱 fit persona 在无立场元素居多的新闻上如何保证产出质量——pilot 观察。

## SSOT 待改清单（gated · 3.11 各 todo 内执行）

- [`prompts/_shared/persona_screenwriter_contract.md`](../../prompts/_shared/persona_screenwriter_contract.md)：P-Select 改轴对齐措辞；元素中心构图规则；POV 派生规则（引 card 清单）；删 v1 单 vantage 表。
- [`prompts/_shared/persona_alt_creator_contract.md`](../../prompts/_shared/persona_alt_creator_contract.md)：valence 降级为可选标注、取消光谱覆盖期待。
- `prompts/personas/*/persona_card.md`（12 张）：价值轴段重定位为注意力清单 + 视角原型标注。
- [`scripts/personas.py`](../../scripts/personas.py)：中心声明解析、focalized 通道、provenance 标签、贪心排序记分。
- 运行时守卫：center ∈ decon ids、focal ∈ who-*、支撑元素上限、双地板校验。
- [`scripts/retrieve.py`](../../scripts/retrieve.py)：候选漏斗 + 池差按通道分解（继承 0007 清单）。
- 打分 schema：`POV变换` 子标签（继承 0007 清单）。
- [`CONTEXT.md`](../../CONTEXT.md)：补术语（注意力清单 / 轴对齐 / 元素中心构图・中心元素 / POV 聚焦・多视角派生 / 双地板 / 候选漏斗 / POV-recalled）。
- [ADR-0007](0007-logic-resonance-judge-prescreen-and-pov-focalization.md) 状态行：D6–D8 标注 superseded/revised by 本 ADR。
- **本 ADR `Status` → `accepted`** 待 3.11 GATE go。

## 相关 ADR / 文档

- [ADR-0007](0007-logic-resonance-judge-prescreen-and-pov-focalization.md) — D1–D5（新双轴定义 + judge 预筛）`accepted` 不动，是本 ADR 的尺子与对照臂来源；D6 被 supersede、D7 原则继承通道结构修订、D8 全量继承。
- [ADR-0004](0004-persona-emotional-diffusion.md) — 情绪扩散主轴；本 ADR 保留其着色赌注（valence 降级不删除），POV 是 lens 从 valence 到 vantage 的延伸。
- [ADR-0005](0005-objective-extraction-neutral-channel-and-collision-vote.md) / [ADR-0006](0006-a1-as-held-out-oracle-per-persona-neutral-and-three-bucket-eval.md) — alt-pool 光谱语义与 salience「仅中性选材」边界被本 ADR 修订；中性通道、两个 neutral、客观地板架构不动。
- [docs/SSOT/personas-12.md](../SSOT/personas-12.md) — 12 persona 价值轴速览（注意力清单的 roster 级 SSOT）。
- `feat/phase3.11.0-pov-wording-source` @ `834e788` — 被本 ADR 作废的 v1 单视角权威措辞（搁置分支，留考古）。
