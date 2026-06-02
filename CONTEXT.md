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

**撞车 (Cross-agent Collision)**:
同一部电影被多个**创作视角**召回的现象。简报里**仅作中性展示**(标注命中它的视角列表),**MVP 不据此加权或排序**——因为"多视角独立殊途同归"的前提尚未验证(视角可能在向量空间塌缩,使撞车沦为假象)。它是否构成真信号,留待评测期观察。基线 A1 不参与该展示。
_Avoid_: 强信号、加权推荐、重复、冲突

**总编 (Editor-in-chief)**:
唯一的人类裁决者。负责:从抓取的新闻池手挑要跑的新闻、对候选电影评分(共振 0/1/2,见 `docs/eval-the-bet.md` §4 两轴 rubric)、从中文审核稿勾选定稿。
_Avoid_: 用户、审核员、运营

**片单 (Galaxy Roster)**:
3D 宇宙站点实际收录的 **59,341 部**清洗后电影(从 119 万行 Kaggle 原始表经去重 + 强制字段 + 按年份动态票数阈值筛出),与 `galaxy_data.json` 及深链 id 集合一一对齐。**检索宇宙必须等于片单**——召回片单外的电影会导致 `/movie/{id}` 死链,引流失效。冷门佳片若不在片单内,本系统设计上够不到。
_Avoid_: 全量、6 万、电影库

**伪剧情模板 (Pseudo-overview Template)**:
索引侧电影向量按 `Tagline: {tagline}\nOverview: {overview}`(无 tagline 时 `Overview: {overview}`)编码。查询侧 pseudo-overview **必须套同一模板**(`Overview: {pseudo}`)再 encode,以保证查询与索引同分布。作废 PRD §3.2 的裸拼接公式。

**现实解构 agent (Reality Deconstructor, A0)**:
在编剧之前把新闻拆成**纯客观、镜头中立**的结构化素材(`reality-deconstructed.json`)。产出起因/经过/结果碎片与实体**标签梯**,不做去实体化、不预选承重、不标共振类型。契约见 `docs/SSOT/reality-deconstruction-contract.md`。
_Avoid_: 新闻摘要、骨架综合、skeleton

**现实波澜 (Reality Ripple)**:
单条热点新闻的人类可读快照(`reality.md` / Eval 内 `reality.json`),含 title、source、summary。解构前的「原文锚点」,与解构产物并列供总编扫读。
_Avoid_: 解构 JSON、pseudo

**标签梯 (Tag Ladder)**:
现实解构层为地点/人物等实体挂的**从具体到抽象**的客观标签列表(如地理上位词 + 内在属性)。本层**穷举客观属性、不精选**;「挑哪一层来共振」是下游 Persona 的镜头。
_Avoid_: 精选标签、主题框定

**镜头中立 (Lens-neutral)**:
现实解构层的铁律:不产出权力定性、反讽意味、戏剧 beat 等「换 persona 答案会变」的框定;那些全部下放给 A2/A4/A7。
_Avoid_: 中立报道、客观新闻(此处指**结构化契约**,非媒体口吻)

**pseudo命中分 (Pseudo Hit Score)**:
评测辅助指标:按 `retrieve.json` 的 `hit_sources` 统计每个候选被多少**解构碎片**命中(每 fragment id = 1 分)。由 `scripts/score_eval_candidates.py` 写入 `candidates.md`,并汇总 `output/Eval/high-hit-score-review.md`。**不替代** 共振分 0/1/2 闸门。
_Avoid_: 共振分、向量相似度
