# 每日星轨观测 · Daily Stargazing

一个「数字文化天文台」:把每日真实新闻经多 Agent 重塑后,在 6 万部电影的纯文本向量库里召回与之"共振"的电影,作为通往 3D 电影宇宙的引子。本文件是术语表,不是规格说明。

## Language

**共振 (Resonance)**:
现实新闻与召回电影之间值得展示的呼应,**分两层、评分(0/1/2)同时认可**:① **表层共振**——共享**承重的**具体元素(地点 / 人物类型 / 事件类型 / 设定),即该元素是两边故事的核心驱动,而非碰巧同一布景;② **结构性共振 (Structural Resonance)**——在抽象骨架(权力关系 / 命运结构 / 反讽落差)上同构,由 Persona 在改写阶段注入、表层题材是否相关无所谓。二者兼得最佳;**纯偶然、非承重的表层重叠不算共振(判 0)**。
_Avoid_: 相似、相关、匹配

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

**基线 (Baseline, A1)**:
现实记录员 Agent:只做去实体化白描、不注入任何隐喻,因此其伪剧情停留在题材平面。它是实验对照组,用来回答"创作视角是否真比平铺直叙更妙",**不计入跨 Agent 撞车统计**。
_Avoid_: 默认、基础

**撞车 (Cross-agent Collision · ADR-0005 形状)**:
优质候选主判据（复活 ADR-0003）：**中性通道整体 = 1 张去重 agent 票**（所有中性 pseudo 命中的 union）+ **≥1 语气通道（toned）汇聚到同一部电影**。防止 12 条近重复中性 pseudo 毒化信号，又不饿死召回。验证前 `retrieve.py` 仍可能用旧对称 `distinct_agents >= 2` 口径。
_Avoid_: 12 票饱和、纯 An+An 对称计票（旧口径）

**总编 (Editor-in-chief)**:
唯一的人类裁决者。负责:从抓取的新闻池手挑要跑的新闻、对候选电影评分(共振 0/1/2,见 `docs/eval-the-bet.md` §4 两轴 rubric)、从中文审核稿勾选定稿。
_Avoid_: 用户、审核员、运营

**片单 (Galaxy Roster)**:
3D 宇宙站点实际收录的 **59,341 部**清洗后电影(从 119 万行 Kaggle 原始表经去重 + 强制字段 + 按年份动态票数阈值筛出),与 `galaxy_data.json` 及深链 id 集合一一对齐。**检索宇宙必须等于片单**——召回片单外的电影会导致 `/movie/{id}` 死链,引流失效。冷门佳片若不在片单内,本系统设计上够不到。
_Avoid_: 全量、6 万、电影库

**伪剧情模板 (Pseudo-overview Template)**:
索引侧电影向量按 `Tagline: {tagline}\nOverview: {overview}`(无 tagline 时 `Overview: {overview}`)编码。查询侧 pseudo-overview **必须套同一模板**(`Overview: {pseudo}`)再 encode,以保证查询与索引同分布。作废 PRD §3.2 的裸拼接公式。

**现实解构 agent (Reality Deconstructor, A0 · P-Extract)**:
在编剧之前把**英文**新闻做**纯逐字抽取**（who/where/when/why/how/result + role + relations），产出 `reality-deconstructed.json`。**逐字保留原文用词与 source valence**；**不产**中性替代词、hypernym 梯或 persona 框定。共享 **客观扩展 pass（P-Expand）** 另产 hypernym 梯（`reality-expanded.json`）。契约见 `docs/SSOT/reality-deconstruction-contract.md`；决策见 `docs/adr/0005-objective-extraction-neutral-channel-and-collision-vote.md`。
_Avoid_: 新闻摘要、骨架综合、skeleton、标签梯、镜头中立（旧 v1 口径）

**客观地板中性 (Objective-floor neutral)**:
`surface`（A0 逐字词）+ `hypernym`（共享扩展梯）组成的 **persona 无关**客观底。**中性通道**只用这一层；与 persona 中点中性不同。
_Avoid_: 绝对中性、真空中性源

**persona 中点中性 (Persona-midpoint neutral)**:
某 persona **价值轴**的中点，仅活在该 persona 的 lens spectrum 内（alt-pool 的 `valence: neutral` + `provenance: lens`）。**不进**中性通道。
_Avoid_: 与客观地板混用

**中性通道 (Neutral channel · C-Neutral)**:
每 persona **恰好 1 条** pseudo，仅用客观地板（surface + hypernym，**无 lens**）。扛**题面召回**与度量基线；**取代 A1**（验证期仍并跑 A1）。见 ADR-0005。
_Avoid_: persona 语气 pseudo、A1 白描（退役方向）

**语气通道 (Toned channel · C-Toned)**:
每条 toned pseudo = **hypernym 锚（留在题面）+ lens 倾斜**；发自己的 anchored 检索 query，可与中性通道殊途同归到同一部电影。
_Avoid_: 纯 re-rank、无锚漂移

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
评测辅助指标:按 `retrieve.json` 的 `hit_sources` 统计每个候选被多少**解构碎片**命中(每 fragment id = 1 分)。由 `scripts/score_eval_candidates.py` 写入 `candidates.md`,并汇总 `output/Eval/<phase-dir>/high-hit-score-review.md`（Phase 3.5.6 对照：`phase3.5/`）。**不替代** 共振分 0/1/2 闸门。
_Avoid_: 共振分、向量相似度
