# 每日星轨观测 · Daily Stargazing

一个「数字文化天文台」:把每日真实新闻经多 Agent 重塑后,在 6 万部电影的纯文本向量库里召回与之"共振"的电影,作为通往 3D 电影宇宙的引子。本文件是术语表,不是规格说明。

## Language

**共振 (Resonance)**:
现实新闻与召回电影之间值得展示的呼应,**分两层(双轴)、按 2×2 矩阵评分(0/1/2)**:① **表层元素**——共享**具体、可命名且承重**的元素(地点 / 人物类型 / 事件类型 / 设定);② **底层逻辑**——POV/尺度不变的因果-赌注引擎同构(替换旧「骨架同构」)。权威措辞源 `prompts/_shared/resonance_definition_v2.md`(ADR-0007 D1);矩阵 SSOT `docs/eval-the-bet.md` §4 — 0=无共振(偶然词面重叠); 1=深层共振(仅逻辑,无表层)或表层沾边; 2=强共振(表层+逻辑)。**纯偶然、非承重的表层重叠不算共振(判 0)**。
_Avoid_: 相似、相关、匹配、骨架同构(旧 ≤3.9 口径)

**表层元素 (Surface element · ADR-0007 D1 第一轴)**:
新闻与电影共享的**具体、可命名且在两边都承重**的元素(这个地点 / 这类职业 / 这种事件类型 / 这个设定题材)。判据=**0 分守门**:换一条无关新闻若同样能配上这部片,则该元素不承重,判 0。**抽象权力角色配对(权威↔受害者、领袖↔团队)不算表层元素,归底层逻辑轴**(过不了 0 分守门)。
_Avoid_: 承重表层锚点(旧措辞)、把权力角色当表层

**底层逻辑 / POV 不变因果引擎 (Underlying logic · ADR-0007 D1 第二轴)**:
新闻与电影**实例化同一句「X 在约束 Z 下驱动 Y」**因果-赌注引擎,且该引擎在 **POV(视角)/ 尺度变换下不变**——机构尺度↔个人尺度讲同一引擎仍算共振。替换旧「结构性共振 / 骨架同构」;比旧口径**宽**(纳 POV/尺度变换),但由因果反测句兜底,不滑成「什么都给分」。
_Avoid_: 骨架同构、结构性共振(旧 ≤3.9 口径)

**因果反测句 (Causal counter-test · ADR-0007 D1)**:
底层逻辑轴的**可证伪闸**:必须能写出**一句**两边都字面成立的「X 在约束 Z 下驱动 Y」(如*系统性稀缺把普通人逼入求生*)。**写不出 ⇒ 不算逻辑共振,退回 0/1**。LLM judge 须在输出 `causal_test` 字段给出该双向映射句(防给分膨胀)。
_Avoid_: 仅凭抽象角色配对给逻辑分(无反测句)

**judge 预筛 (Judge pre-screen · ADR-0007 D4)**:
LLM-judge 从「打分裁判」转为**评测打分循环的预筛器**:全量打分、**物理一个不删**;分档 `judge=0` 降级堆(默认不进人工) / `judge≥1` 进人工复核(省人工) / `judge=2` 高亮优先。阈值 `judge≥1` 须在 obs 新定义验证「零 human-2 被杀」才冻结。仅减评测人工负担,**不碰生产日报选片**。
_Avoid_: judge 当终判、靠调高门槛控候选膨胀

**拒绝集抽审 (Rejection-pile spot-check · ADR-0007 D4)**:
预筛上线后**唯一**持续监控「100% 留存」的手段:每 run 人工额外**盲评 `judge=0` 堆随机 k%**;一旦捞到 `human=2` ⇒ 门槛不安全,放宽。闸门分母在「放行 + 抽审样本」集上算,抽审样本按抽样率回加权。
_Avoid_: 只看放行侧、抽审样本不回加权

**伪剧情 (Pseudo-overview)**:
某个 Persona 把一条新闻解构后重塑成的、写成电影简介口吻的一段英文故事。它是"共振"的载体:把新闻的抽象骨架再具象化为可被表层向量检索命中的文本。
_Avoid_: 改写、摘要、梗概

**去实体化 (De-entification)**:
改写时剥除所有真实专名(人名/地名/机构/精确数字/新闻八股)、只保留角色与结构的硬规则。目的是让伪剧情落在"电影简介"的分布上,而非"新闻播报"。
_Avoid_: 匿名化、脱敏

**向量召回 = 表层匹配器 (Surface Matcher)**:
检索阶段被**有意**设计成只做表层话题/词汇相似度计算。系统的"智能"全部位于 Persona prompts;模型的笨是设计而非缺陷。因此召回电影与伪剧情表层相似是预期行为。

**Persona / 创作视角**:
一个拥有独立人格文档、负责从某一角度重塑新闻的 Agent。MVP 跑 A2 社会学家 / A4 神话学者 / A7 混沌理论家。
_Avoid_: 角色、机器人

**基线 / held-out oracle (Baseline, A1 · ADR-0006)**:
现实记录员 Agent:只做去实体化白描、不注入任何隐喻,因此其伪剧情停留在题材平面。Phase 3.9 起 A1 **并跑但不参与判断**——**不进候选池、不进撞车票、不进排序**;仅作**召回与质量神谕**(正确答案集代理),供 per-persona 中性腿对照「能否追平 A1」。删 A1 须待 GATE **Q1′** 证明 12 条 neutral n1 命中 union **⊇ A1_two**（A1 命中且人工共振分=2）后再议；全量 A1 superset / 质量对比仅为 legacy 诊断。
_Avoid_: 默认、基础、平权竞争者(ADR-0003 旧口径)

**撞车 (Cross-agent Collision · diagnostic annotation)**:
撞车现在只作为**检索汇聚诊断标注**，不是质量判据：**中性通道整体 = 1 张去重 agent 票**（所有中性 pseudo 命中的 union）+ **≥1 toned/focalized 通道汇聚到同一部电影**时，`retrieve.py` 可标出 `quality_candidate=true` / `quality_reason`。该字段仅用于解释候选来源，不进排序、不进截断、不进三桶分桶、不进 Go/No-Go；当前结果解读不得把它当「优质候选」。`positive` / `negative` / `neutral` 也同理仅是 persona-relative annotation，客观/中性资格只看显式 `provenance: surface|hypernym`。
_Avoid_: 12 票饱和、纯 An+An 对称计票（旧口径）、把 `quality_candidate` 当判据或质量分

**总编 (Editor-in-chief)**:
唯一的人类裁决者。负责:从抓取的新闻池手挑要跑的新闻、对候选电影评分(共振 0/1/2,见 `docs/eval-the-bet.md` §4 两轴 rubric)、从中文审核稿勾选定稿。
_Avoid_: 用户、审核员、运营

**片单 (Galaxy Roster)**:
3D 宇宙站点实际收录的 **59,341 部**清洗后电影(从 119 万行 Kaggle 原始表经去重 + 强制字段 + 按年份动态票数阈值筛出),与 `galaxy_data.json` 及深链 id 集合一一对齐。**检索宇宙必须等于片单**——召回片单外的电影会导致 `/movie/{id}` 死链,引流失效。冷门佳片若不在片单内,本系统设计上够不到。
_Avoid_: 全量、6 万、电影库

**伪剧情模板 (Pseudo-overview Template)**:
索引侧电影向量按 `Tagline: {tagline}\nOverview: {overview}`(无 tagline 时 `Overview: {overview}`)编码。查询侧 pseudo-overview **必须套同一模板**(`Overview: {pseudo}`)再 encode,以保证查询与索引同分布。作废 PRD §3.2 的裸拼接公式。

**现实解构 agent (Reality Deconstructor, A0 · P-Extract)**:
在编剧之前把**英文**新闻做**纯逐字抽取**（who/where/when/why/how/result + role + relations），产出 `facts.json`。**逐字保留原文用词与 source valence**；**不产**中性替代词、hypernym 梯或 persona 框定。共享 **客观扩展 pass（P-Expand）** 另产 hypernym 梯（`bridges.json`）。契约见 `docs/SSOT/reality-deconstruction-contract.md`；决策见 `docs/adr/0005-objective-extraction-neutral-channel-and-collision-vote.md`。
_Avoid_: 新闻摘要、骨架综合、skeleton、标签梯、镜头中立（旧 v1 口径）

**客观地板中性 (Objective-floor neutral)**:
`surface`（A0 逐字词）+ `hypernym`（共享扩展梯）组成的客观底。**措辞** persona 无关(模板拼装);**选材**可 persona 相对(见 per-persona salience)。**中性通道**只用这一层 vocabulary；与 persona 中点中性不同。
_Avoid_: 绝对中性、真空中性源、persona 书写中性散文

**persona 中点中性 (Persona-midpoint neutral)**:
某 persona **价值轴**的中点，仅活在该 persona 的 lens spectrum 内（alt-pool 的 `valence: neutral` + `provenance: lens`）。**不进**中性通道。
_Avoid_: 与客观地板混用

**中性通道 (Neutral channel · C-Neutral · diagnostic-only)**:
每 persona **恰好 1 条** pseudo（通常 `n1`），仅用客观地板 vocabulary（surface + hypernym，**无 lens**），由 **per-persona salience** 选 Top-K 碎片驱动选材。现在只承担**诊断覆盖 / 召回解释 / A1 只读对照**：`neutral_hits`、`neutral_hit_rate`、`n1` union、pure_fact/three-bucket 都保留输出，但不进候选质量、排序、截断、high-hit 纳入、Go/No-Go 或 D5 成功判据。
_Avoid_: persona 语气 pseudo、共享固定碎片(3.8 退化模式)、把 `n1` 当质量腿或 gate 基线

**per-persona salience**:
alt-creator 输出的 **既有 `element_id` 有序列表**(最→次),表达本 persona 价值轴最关注哪些事实。**只重排/取子集既有 ids,不新增词、不写评注**;下游取 Top-K(4–5) 作中性碎片 SELECTION。**铁律:salience 只驱动选材,绝不影响 wording**(中性句由模板从 surface+hypernym 拼装)。主选:LLM 按新闻动态决定;plan B 回退:persona card **价值轴**作软先验(非硬规则)。见 ADR-0006 D6。

**neutral diversity guard**:
批内 12 条中性 pseudo 两两检查近重复。**硬失败**仅当该对的中性与 toned 均近重复;若仅中性撞车而 toned 仍各异,记 warning 并继续(差异化由 toned + 检索兜底)。中性 body 对同一 surface 文本只渲染一次。
_Avoid_: salience 写散文、salience 渗入 valence

**三桶诊断 (Three-bucket diagnostics · ADR-0006 legacy shape)**:
评测候选仍可按来源诊断性归入三桶:**① 纯事实**(中性/oracle 命中、无 toned 汇聚)、**② 纯情绪**(toned-only)、**③ 组合**(中性票 + ≥1 toned 汇聚)。该三桶现在只用于观察 `n1` 覆盖与通道交互，不再作为 Go/No-Go 或 D5 成功判据。
_Avoid_: neutral_only 恒空(3.8 结构性缺陷)、无控相似度结论、把 combo>pure_fact 当当前 gate


**留出冻结 (Holdout-freeze discipline · ADR-0006)**:
只在**观察集**调 prompt/阈值 → **冻结** → **留出集只打一次分**。留出 ≈ 观察 ⇒ 提升为真;留出垮 ⇒ 过拟合。评测编排纪律,非产品功能。
_Avoid_: 在留出集反复调参后宣称提升

**语气通道 (Toned channel · C-Toned)**:
每条 toned pseudo = **hypernym 锚（留在题面）+ lens 倾斜**；发自己的 anchored 检索 query，可与中性通道殊途同归到同一部电影。
_Avoid_: 纯 re-rank、无锚漂移

**注意力清单 (Attention inventory · ADR-0008 D1)**:
persona card **价值轴**的重新定位：Who/Where/When 极列出本 persona 叙事在意的元素**原型**，是 P-Select 中心化与 POV 视角派生的 SSOT。valence 降级为元素层**可选**着色标注——lens 真有立场才标，模糊元素白描（surface/hypernym），**取消逐元素正中负光谱覆盖期待**。两极元素作为构图材料**平等合法**。
_Avoid_: 逐元素光谱覆盖（旧 ≤3.10 口径）、把极性当资格门槛

**轴对齐 (Axis-alignment · ADR-0008 D2)**:
一条 pseudo 属于某 persona 的判据：其中元素被**逐个**透过本 persona 价值轴框定，而非整体朝某方向倾斜。**pseudo 层无极性概念**；两极同场张力是欢迎的——原型故事正是正极作用于负极（如 Ruler 的 authority(+) 在 ungoverned zone(−) 建立新秩序）。
_Avoid_: 给 pseudo 归类正/负向、要求整条单向倾斜

**元素中心构图 / 中心元素 (Element-centered composition · ADR-0008 D3)**:
toned/focalized pseudo 的变化组织原则：每条**显式声明 1 个中心元素 id**（+2–4 支撑元素），中心按本 persona 逐新闻 `salience` **自上而下贪心**取、各条互异；**LLM 只声明，排序/预算由代码**按中心 salience 名次确定性计算。salience 职责由「中性通道选材」扩展为「全通道构图驱动」，但**不影响中性 n1 wording**（模板拼装零改动）。
_Avoid_: LLM 自评分挑选、重要度×元素数乘法记分（塞词激励）、中心声明名不副实

**POV 聚焦 (Focalization · ADR-0008 D4)**:
persona lens 从 valence 到 **vantage（从谁的眼睛看）** 的更深表达：透过 decon 既有 `who-*` 角色的视点重述事件。**多视角派生**：合法视角集 = persona card Who 正极原型（**共情座位**；负极是被审视的对象，不作座位），逐新闻落点由 salience 派生——中心元素是 who-* 且实例化原型 ⇒ 该条写成 focalized，**不引入自由参数**。铁律：只换"从谁的眼睛看"，**绝不新增内心戏/事件/因果/结果**；hypernym 锚保留；硬失败即重生成。规则权威源 `prompts/_shared/persona_screenwriter_contract.md` §Element-centered composition & POV focalization。
_Avoid_: 自由选视角、单 canonical 视角表（v1 已作废）、第一人称硬性要求、语气改写（那是 P-Tone）

**双地板 (Dual floor · ADR-0008 D5)**:
匹配下限的两道锁：① 中性 n1 的 wording/模板机制**零改动**（3.10 已验证资产）；② 每 persona **≥1 条非聚焦第三人称 toned** pseudo。focalized 与元素中心 pseudo **纯增不减**——缺任一地板即硬失败。
_Avoid_: 顶替式 POV（已否决）、砍第三人称通道

**候选漏斗 (Candidate funnel · ADR-0007 D8 · ADR-0008 继承)**:
吸收追加式候选膨胀的四层分层：**① 去重**（按 `tmdb_id` 合并多通道同命中）→ **② 汇聚排序**（多通道/多 persona 同时命中排前，扩展撞车票）→ **③ judge 预筛**（滤 `judge=0`）→ **④ 硬预算 top-N** 给人工。上限以下 `judge≥1` 进拒绝集抽审池。**铁律：控量用排序+预算，保安全用门槛+抽审，绝不靠调高 judge 门槛控膨胀**。
_Avoid_: 调高 judge 门槛控量、控量与保安全混用一套旋钮

**A/B 池差 (Pool diff · ADR-0008 D6)**:
新设计-on（3.11）召回 ∖ 3.10 基线同新闻召回 的差集，**按 provenance 通道类型分解**（neutral / toned / focalized）。其新定义 2 分率 + `POV变换` 子标签分布 = **调优指南针**（哪 persona / 哪类中心 / 哪类视角有用、往哪调），**非判决闸**。**打包归因**：与基线的差异 = 整包新设计（总编显式接受），通道分解只恢复粗归因，**不得**事后宣称单变量净效应。
_Avoid_: 当判决闸、宣称 POV 单变量净效应、与混入其他变量的对照比较（须同新闻同 def 同 judge）

**neutral hit rate**:
每部电影 `neutral_hit_rate = (命中该片的中性 pseudo 数) / (运行的 persona 数)`。分母固定 = persona 数。诊断指标（**非闸门**）；须在控制 `max_similarity` 下解读。见 ADR-0005。
_Avoid_: 共振分、相似度代理（未控变量时）

**三层 provenance (3-layer provenance)**:
下游组装 pseudo 时的词源分层：**surface**（逐字）/ **hypernym**（客观共享桥）/ **lens**（persona 相对价）。中性通道禁 lens；语气通道必带 hypernym 锚 + lens。
_Avoid_: 单层中性池、A0 内嵌 alternatives

**现实波澜 (Reality Ripple)**:
单条热点新闻的人类可读快照(`reality.md` / Eval 内 `reality.json`),含 title、source、summary。解构前的「原文锚点」,与解构产物并列供总编扫读。
_Avoid_: 解构 JSON、pseudo

**pseudo命中分 (Pseudo Hit Score)**:
评测辅助指标:按 `candidates.json` 的 `hit_sources` 统计每个候选被多少**解构碎片**命中(每 fragment id = 1 分)。由 `scripts/score_eval_candidates.py` 写入 `candidates.md`,并汇总 `output/Eval/<phase-dir>/high-hit-score-review.md`（Phase 3.5.6 对照：`phase3.5/`）。**不替代** 共振分 0/1/2 闸门。
_Avoid_: 共振分、向量相似度
