# 电影宇宙「每日星轨观测」系统 PRD

> **当前版本**：v0.5（12 Pearson persona · fragment ladder / search unit · 双轴共振 + judge 预筛）
> **更新日期**：2026-06-14
> **状态**：MVP 建造期 · **Phase 3 全部 GATE GO**（3.10 双轴 rubric + judge 预筛收敛 2026-06-10；3.11.8 fragment ladder / search unit 架构收敛 2026-06-13），**即将进入 Phase 4（呈现层 / 中文文案）**。
>
> **本版定位**：本 PRD 是项目 SSOT，登记**当前真实设计**。Phase 3 经历了从「A2/A4/A7 + A1 四 agent」到「12 Pearson 原型 persona」、从「pseudo 通道」到「fragment ladder / search unit」的两次大重构，散落在 [ADR-0004](../adr/0004-persona-emotional-diffusion.md) / [ADR-0007](../adr/0007-logic-resonance-judge-prescreen-and-pov-focalization.md) / [ADR-0008](../adr/0008-salience-driven-element-composition-and-multi-vantage-pov.md) / [ADR-0009](../adr/0009-fragment-ladder-and-search-unit-architecture.md) / [ADR-0010](../adr/0010-pseudo-drop-granularity-and-pipeline-first-derisking.md) 中。本版把这些决策收口进 SSOT。历史四 agent 写法（A1/A2/A4/A7）已**作废**，仅在历史报告中保留。
>
> **语种链**：电影库为全英文。**新闻输入 → 解构 → 扩展 → persona lens → search unit → 检索全程英文**（英进英出，无翻译步骤）。唯一中文化 = 召回后为候选写中文推荐文案给总编审核（Phase 4）；多平台多语言定稿在更下游。

---

## 1. 产品概述（Product Overview）

### 1.1 背景与痛点

已完成的核心资产是「基于 TMDB 与 UMAP 算法的 3D 电影宇宙」（[themoviecosmos.com](https://themoviecosmos.com)），它以中立、客观的视角收录了人类电影史的全量样本。但作为一个静态数字档案，它缺乏与真实世界的纽带，难以持续吸引具备探索欲的用户。

### 1.2 产品目标

打造一个「数字文化天文台」。以每日热点事件为引，挖掘现实事件与某一部电影之间的**共振**。

**共振的定义已定稿为双轴**（[ADR-0007](../adr/0007-logic-resonance-judge-prescreen-and-pov-focalization.md) D1，[`docs/eval-the-bet.md`](../eval-the-bet.md) §4）：

- **第一轴 · 表层元素**：候选与新闻共享**具体、可命名、承重**的元素（地点 / 人物类型 / 事件类型 / 设定 / 题材）。判据：换条无关新闻无法复用 = 承重。
- **第二轴 · 底层逻辑**：新闻与电影实例化**同一个在 POV / 尺度变换下不变的因果-赌注引擎**（一句「X 在约束 Z 下驱动 Y」，机构尺度 ↔ 个人尺度也算），附**因果反测句**防给分膨胀。

两轴都无 = 0；单轴 = 1；双轴 = 2。**表层与结构共振均合法**（[ADR-0002](../adr/0002-pivot-to-event-logic-resonance.md)），不再把「绝妙的、非显然的隐喻」作为唯一产品标准。

**核心理念**：推荐不是为了催促观看，而是展示「现实世界与数字宇宙的共振」，以此满足好奇心并完成对 3D 电影宇宙的引流。

**产品价值观 · 影像平权**（[ADR-0013](../adr/0013-image-equality-creative-tone.md)）：随刊文案以一种**平视**的目光对待每一部影像作品——不因它热度高低、评价好坏、年代远近而改变语气，不给电影排名、不找补、不吹捧。读者应能感到一部电影的传播广窄与口碑形态（数据影响保留），但正文只平静呈现它是什么、被怎样接受、以及它和新闻触到同一种什么样的人类处境，**不替读者下「它好/不好、值不值得看」的判断**。对外品牌叙事可表述为「未来考古主义」；对内则以「影像平权 / 无差别的注视」作为可执行口径。

### 1.3 MVP 验证目标

本阶段要回答的核心问题（[`docs/eval-the-bet.md`](../eval-the-bet.md) §5.1）：

> 在「单条新闻 → 现实解构 → 客观扩展 → 12 persona 各自构图 → fragment ladder / search unit 多路召回聚合 → 人类双轴共振评分」的链路上，是否能稳定产出**值得展示的共振候选**，且**12 个原型 persona 的创作视角相对中性基线带来可测量的关联增量**？

所有工程化、自动化、风控、UI 决策都让位于这个问题的回答。

---

## 2. 系统架构与技术栈（Architecture & Tech Stack）

* **大模型编剧室（Multi-Agent 架构）**：12 个 Pearson 原型 persona（见 §4），每个 persona 拥有独立的 `persona_card.md`，由主控脚本异步并发调用。
* **LLM 提供方（MVP 决策）**：主用 **MiMo 2.5 / 2.5 Pro**（已持有 token）；备选 **DeepSeek**（成本低）。`scripts/lib/llm.py` 统一封装，`--provider` 可切换。不做硬性 token 限制，按效果与用量动态调整。
* **LLM-judge（评测预筛）**：独立 judge（`scripts/llm_judge.py` / `judge_prescreen.py`）用双轴 rubric 给全部候选打分，**物理上一个不删**，仅分档分流（`judge=0` 降级堆 / `judge≥1` 进人工 / `judge=2` 高亮）。当前为 `screening-only`，尚未采信为共振真值。
* **信息源**：**RSS 订阅源**（Python `feedparser`），Phase 5 接入；评测期用手挑/手写 JSON。
* **总编与决策台（Human-in-the-Loop）**：项目根目录即 **Obsidian Vault**，评测产物落 `output/Eval/{run_id}/`，正式日报落 `output/Daily_Briefing/YYYY-MM-DD.md`，由人类总编在 Obsidian 中完成「火花甄别」与共振评分。
* **核心检索基建**：
  * 模型：`paraphrase-multilingual-MiniLM-L12-v2`（与 3D 宇宙索引同模型、同 384 维）。
  * 输入：与 3D 宇宙对齐，**直接使用 TMDB 原文（清洗后的 tagline + overview），不做机器翻译**；库为全英文，故检索侧 search unit 文本也统一英文，同分布召回更稳。
  * 输出：`embeddings.npy`（L2 归一化）+ `meta.parquet`。
  * 不做 UMAP / 不拼接 Genres / 不拼接 Language——纯粹基于剧情结构与隐喻做跨界检索。
  * 数据规模：**59,341 部**（3D 宇宙策展片单）。6 万级用 NumPy 矩阵乘法 + `argpartition` 毫秒级即可，**不引入 FAISS**。
  * **索引来源（[ADR-0001](../adr/0001-reuse-cosmos-text-embeddings.md)）**：MVP **直接复用** 3D 宇宙项目产出的 `cleaned.csv` + `text_embeddings.npy`（同模型、384 维、已 L2 归一、行序对齐），不自建。`build_index.py` 重算逻辑降级为 Post-MVP 备用。
  * **召回底座**：当前 dense embedding 余弦检索为主；hybrid recall 的 lexical / weighted ladder 子信号尚未完全展开（[ADR-0009](../adr/0009-fragment-ladder-and-search-unit-architecture.md) 已知局限）。

---

## 3. 数据层规约（Data Contract）

### 3.1 源数据与规模

* **进入索引的必需字段**：`id, title, original_title, overview, tagline, genres, original_language, release_date, poster_path`。
* **数据库规模**：**59,341 行**（策展片单 `cleaned.csv`）。subsample 仅用于验证管线（plumbing），**召回质量/评分只在全量片单上才算数**（[ADR-0001](../adr/0001-reuse-cosmos-text-embeddings.md)）。

### 3.2 文本清洗与缺失值处理

| 情况 | 处理 |
| --- | --- |
| `tagline` 大量为空 | 接受，embedding 降级为 `overview` only |
| `overview` 缺失 | 用 `title`（必要时加 `original_title`）回填 |
| `overview` 仍为空 | 剔除该行（不进入索引） |
| 仅有原语种简介 | 保留原文，依赖多语言模型对齐 |
| 字符串前后空白、HTML 残片、引号变体 | 统一清洗 |

embedding 输入文本模板（**已对齐 3D 宇宙索引**，ADR-0001）：

```
有 tagline:  f"Tagline: {tagline}\nOverview: {overview}"
无 tagline:  f"Overview: {overview}"
```

> ⚠️ 此模板**同时约束查询侧**：`retrieve.py` 必须把每条 search unit 文本套成 `Overview: {text}` 再 encode，保证查询与索引同分布。早期裸拼接公式已作废。

### 3.3 索引产物

| 产物 | 格式 | 用途 |
| --- | --- | --- |
| `data/index/embeddings.npy` | `float32 (N, 384)`，L2 归一化 | 余弦检索 |
| `data/index/meta.parquet` | 上述 9 列 | 渲染 Markdown / 拼跳转链接 |

### 3.4 索引更新策略

* **MVP**：全量重跑（实为复用 cosmos 产物）。
* **Post-MVP**：增量（按 TMDB `id` diff，只对新增/修改行重 embed）。

---

## 4. 多智能体编剧室（Multi-Agent Screenwriting Room）

> 管线的结构化素材层契约 SSOT：[`docs/SSOT/reality-deconstruction-contract.md`](reality-deconstruction-contract.md)（A0 逐字抽取）、[`docs/SSOT/personas-12.md`](personas-12.md)（12 persona roster）；完整 workflow 见 [`docs/SSOT/news-to-film-pipeline.md`](news-to-film-pipeline.md)（fragment ladder / search unit）。

### 4.0 五段流水（当前架构 · ADR-0009）

```text
1. 网络接口收热点新闻（英文）        → reality.md（人类可读）
2. A0 现实解构                      → reality-deconstructed.json（逐字抽取，稳定 element id）
3. Fragment ladder                 → 每个 element 展开 surface/alias/objective_*/interpretive/perspective 层
4. Persona salience + search unit   → surface/event fragment bundle + persona-semantic（绑定 center_element）
5. Hybrid recall + 候选漏斗          → 候选聚合 + convergent sort + judge 预筛
```

| 段 | 脚本 / 契约 | 铁律 |
| --- | --- | --- |
| **A0 现实解构** | `prompts/A0_reality_deconstructor.md` · `scripts/deconstruct.py` | **只做逐字抽取**（who/where/when/why/how/result + role + relations）；保留原文用词与 source valence；不产中性替代、不做视角框定 |
| **Fragment ladder** | `prompts/_shared/persona_alt_creator_contract.md` · `scripts/personas.py` | 每 element 展开 ladder：`surface`(A0 原文) / `alias` / `objective_*`(吸收原 hypernym 客观扩展) / `interpretive`+`perspective`(吸收 persona lens)；每个 fragment 绑定既有 `element_id`，不新增人物/事件/因果/结果 |
| **Search unit** | `prompts/_shared/persona_screenwriter_contract.md` · `scripts/personas.py` | 三类召回入口：`surface-fragment-bundle` / `event-fragment-bundle`（只用 objective 层、不绑 persona）+ `persona-semantic`（绑 `persona_id` + `center_element` + `supporting_elements`，须有 objective anchor）；`valence` 退为可选着色标注 |

### 4.1 Persona 总览（12 Pearson 原型）

历史的 A1/A2/A4/A7 四 agent 设计已**作废**。当前为 **12 个 Pearson 原型 persona**（[ADR-0004](../adr/0004-persona-emotional-diffusion.md)，roster SSOT 见 [`personas-12.md`](personas-12.md)）：

| persona_id | 名称 | 核心情绪 |
| --- | --- | --- |
| The-Innocent | 天真者 | 希望 / 信任 / 幻灭 |
| The-Everyman | 凡人 / 孤儿 | 归属 / 平等 / 不安 |
| The-Hero | 英雄 / 战士 | 抗争 / 正义 / 尊严 |
| The-Caregiver | 照护者 | 保护 / 受害 / 滋养 |
| The-Explorer | 探索者 | 自由 / 越界 / 求真 |
| The-Outlaw | 反叛者 | 反抗 / 颠覆 / 解放 |
| The-Lover | 情人 | 亲密 / 背叛 / 美感 |
| The-Creator | 创造者 | 造物 / 表达 / 失控 |
| The-Ruler | 统治者 | 秩序 / 控制 / 稳定 |
| The-Magician | 魔法师 | 转化 / 操纵 / 范式转移 |
| The-Sage | 智者 | 真相 / 理性 / 辨识 |
| The-Jester | 愚者 / 狂欢者 | 荒诞 / 当下 / 释放 |

* **persona-relative valence**：每个 persona 的「正极 / 负极」只相对**自己的价值轴**，非绝对褒贬。同一中性元素在不同 persona 可得相反符号（被控造谣者：对 The-Ruler 是「造谣者」负，对 The-Outlaw 是「揭真者」正）。
* **persona card** = `prompts/personas/<persona_id>/persona_card.md`，其 `价值轴 (Value Axis)` 是 **注意力清单**（叙事中重要的元素原型），是 P-Select 中心化与视角派生的 SSOT。
* **中性基线取代 A1**：旧 A1「现实记录员」对照组已由**中性通道 union**（surface + hypernym，无 lens）取代，作为只读质量参照，不进任何闸。

### 4.2 Fragment ladder / search unit（当前生成-检索架构，[ADR-0009](../adr/0009-fragment-ladder-and-search-unit-architecture.md)）

旧的 `neutral / toned / focalized` 三通道已**下线**。当前每个 decon element 生成一个 **fragment ladder**，检索围绕 **search unit** 组织：

```text
fragment ladder（每 element）：
  surface / alias / objective_close / objective_mid / objective_broad / interpretive / perspective

search unit（唯一召回入口，三类）：
  surface-fragment-bundle   ← when/where/who，仅 objective levels，提供 surface_match
  event-fragment-bundle     ← why/how/result，仅 objective levels，提供 event_match
  persona-semantic          ← persona 结合 salience + interpretive/perspective，
                              绑定 center_element + supporting_elements，提供 persona_semantic_match
```

* `surface` 来自 A0 原文；`alias / objective_*` 吸收原 hypernym / 客观扩展；`interpretive / perspective` 吸收 persona alternative / lens。
* 每个 fragment 必须绑定既有 `element_id`，**不得新增人物 / 事件 / 因果 / 结果**。
* **POV 下线为通用 center_element**：视角/尺度变换不再是运行时主通道，仍可作文本效果与人工 `POV变换` 子标签存在。`persona-semantic.center_element` = 任意既有 element id，`supporting_elements` = 1–4 个既有 element id。
* **兼容层**：LLM screenwriter 当前仍返回 `pseudos[]`，代码映射到 `persona-semantic`；检索优先读 `agents[].search_units`。旧产物里的 `neutral/toned/focalized` 字段仅作兼容层，不再驱动排序。

### 4.3 去实体化（De-entification）规则

公共硬规则（`prompts/_shared/deentification_rules.md`，所有 persona 引用）：

1. 不得出现真实人名 → 替换为身份角色。
2. **地名**：默认抽象为环境特征；**承重时可有意识保留专名**（孟买热浪 → Mumbai），见规则 2（[ADR-0002](../adr/0002-pivot-to-event-logic-resonance.md) 放宽）。
3. 不得出现真实机构 / 品牌 / 政党 / 公司名 → 替换为类型。
4. **数字/日期**：默认模糊量级；**承重时可保留**（伤亡、温度记录等）。
5. 不得出现新闻八股（"据报道" / "声明称"）。
6. **输出语种 = 英文（统一）**：无论新闻原文语种，生成侧一律英文。

软规则：主语是「一个/某个 [角色]」非具名实体；优先现在时；单段 60~120 words；末尾不要「A film about…」元描述。

### 4.4 失败处理（[ADR-0010](../adr/0010-pseudo-drop-granularity-and-pipeline-first-derisking.md)）

* **失败粒度 = pseudo 级（杀 pseudo 不杀 persona）**：单条 pseudo 违规（invented interiority / novel proper noun / supporting elements 超上限 / 非法 center 或 support / 事实守卫失败）→ 只丢该条，保留同 persona 其余合法 pseudo；剩 ≥1 条该 persona 继续参与检索。
* **非静默**：必须记账 `kept_pseudos` / `dropped_pseudos` / `drop_reasons[{pseudo_id, reason}]`。
* LLM 调用失败/超时/格式异常 → 评测期允许跳过，主流程继续，记录到 `errors.md`。

---

## 5. 检索与候选处理（Retrieval & Candidates）

### 5.1 召回与排序（convergent sort，[ADR-0009](../adr/0009-fragment-ladder-and-search-unit-architecture.md) D5）

* 每条 search unit 文本（`Overview: {text}` 模板）→ 384 维向量（L2 归一化）→ Top-K 召回。
* 按 `tmdb_id` 聚合去重，合并 `triggered_by` / `hit_sources`。
* **新排序**（替代旧 `channel_count*100 + persona_count*10 + similarity`）：

```text
surface_match_score + event_match_score + persona_semantic_match_score
+ persona_diversity_weight + center_dimension_diversity_weight + dense_similarity
```

* 核心解释字段：`surface_match` / `event_match` / `persona_semantic_match` / `search_unit_kinds` / `center_dimensions` / `triggered_by`。
* `quality_candidate = (surface_match OR event_match) + persona_semantic_match`，**仅观察字段，不作硬闸**。

### 5.2 候选漏斗（[ADR-0007](../adr/0007-logic-resonance-judge-prescreen-and-pov-focalization.md) D8）

| 层 | 机制 |
| --- | --- |
| **1 去重** | 按 `tmdb_id` 合并多 search unit 命中的同一片 |
| **2 汇聚排序** | 被多类 search unit / 多 persona 同时命中的片排前（经得起换视角看 = 精度信号） |
| **3 judge 预筛** | 滤掉放大池里 `judge=0`（降级堆，默认不进人工） |
| **4 硬预算上限** | 排序 + 预筛后只给人工 top-N |

**铁律**：**绝不靠调高 judge 门槛控膨胀**——那会威胁「零 human-2 被杀」。控量用排序+预算，保安全用门槛+抽审（`judge=0` 堆随机抽 k% 盲评监控漏杀）。

### 5.3 候选展示（评测期中性口径）

| 议题 | 决策 |
| --- | --- |
| 多视角撞车 | 仅作中性展示（标命中的 search unit / persona / element 来源），MVP 不据此加权排序之外的产品决策 |
| 相似度下限 | 不设，先看效果 |
| 候选过滤（评分/年代/成人内容） | 不做，先看效果 |
| 历史去重（同片不再推荐） | 不做（Post-MVP 必做） |
| 额外 metadata（导演/演员） | 不做，仅 `title / overview / genres / release_year / language / poster_path / tmdb_id` |

### 5.4 候选文案（中文审核稿 · Phase 4 gated）

召回后为每部候选用中文写一段社媒文案（`prompts/C1_copywriter_review.md`），供总编审核。写「现实 ↔ 电影」共振点，不剧透、不影评腔、不喊看片；不带 hashtag、不分平台。**须 GATE_PASS 后才接**（当前 Phase 3 已 GO，Phase 4 即将启动）。

---

## 6. 新闻源与新闻选择（News Source · Phase 5）

* **MVP**：暂用免费 RSS 源（`scripts/fetch_news.py`，feedparser），清单落配置常量。
* **选新闻**：按热度排序取 Top 1；评测期允许人工指定一条。自动热度评分算法（多源同事件计数 + 时间近端加权）= Post-MVP。
* **新闻字段**：`title`（必需）/ `description`（必需，RSS 摘要）/ `pub_time`（可选）/ `source_name`（可选）。**不爬全文**。
* **去重**：URL 级（规范化后落 `state/seen_news.sqlite`）+ 历史标题（14 天，`difflib` 相似度 ≥ 0.7 跳过）。不上语义级去重。
* **内容过滤**：MVP 不在源做过滤，由人类总编在简报阶段或发布前把关。

---

## 7. 简报与下游产物（Daily Dossier）

### 7.1 输出位置

* 评测产物：`output/Eval/{run_id}/`（与正式日报分离），结构见 [`docs/eval-the-bet.md`](../eval-the-bet.md) §3.3。
* 正式日报：`output/Daily_Briefing/YYYY-MM-DD.md`。模板待产出 3~5 份真实简报后再迭代。

### 7.2 跳转链接

* 前端稳定深链：`https://themoviecosmos.com/movie/{tmdb_id}`（Phase 30 契约，分享/OG/`_redirects` 均以此为准）。`{tmdb_id}` = `cleaned.csv` 的 `id` 列（TMDB 数字 id）。
* 可附 `?lang=` / `?theme=` / `?timeline=` query。旧版 `?focus_movie=xxx` **当前代码库不存在，勿用**。

### 7.3 文案定稿（平台增量 · Phase 4 Stage 1 gated）

> **MVP 边界（2026-06-14 收窄）**：Phase 4 MVP **只产出中文审核稿文本并落 Obsidian 供总编肉眼审核**（§5.4），**不含任何平台定稿 / 中英双语 / 图片**。文本质量过 GATE 后才解封下方定稿。

总编在 Obsidian 勾选一条审核稿后，按 [ADR-0015](../adr/0015-publish-platformization-and-element-checklist.md) 生成平台发布版本：每平台一个创作步骤（`compose --stage publish --platform xiaohongshu`），MVP 小红书首发，X / Reddit 预留；产出正文（必含新闻侧/关系侧/电影侧三类元素，顺序自由）+ headline（≤10 中文字）+ 归属行 `「片名」(YYYY) 导演名`。

* **从最简单平台起步、增量扩展**（小红书 → X → discord），不一次性铺全平台。
* 每平台一个 profile（语言 / 长度 / 结构约定 / hashtag / 转贴 / 图片字段占位）：小红书=中文 + hashtag 关联新闻；X=英文 + 引用新闻原帖（需源 URL，缺失则后置）；discord=最简纯文本。
* 每版附跳转链接 + 0~2 个自然话题标签；`image_ref` 仅占位，本 Phase 不生成图片。

### 7.4 视觉切片与发布

* **图片生成**：独立**视觉生成层 Phase**（先定义与主项目 og 图共用的一套设计逻辑）；Phase 4 仅在 profile 占位 `image_ref`，不生成。
* `generate_planet.py`（星球视觉）、更多平台/语种、社媒自动发布 = **Post-MVP**；社媒发布始终先手动（discord 因无注册/审核门槛，为未来首个自动发布试点）。

---

## 8. 验证闸门（The Bet）与 Phase 3 结果

> 完整手册：[`docs/eval-the-bet.md`](../eval-the-bet.md)。留出集纪律：[`docs/eval-phase3.10-holdout-freeze-discipline.md`](../eval-phase3.10-holdout-freeze-discipline.md)。

### 8.1 共振评分 Rubric（双轴 0/1/2）

| 表层元素 | 底层逻辑 | 分 | 共振类型 |
| --- | --- | --- | --- |
| 无 | 否 | **0** | 无共振 |
| 无 | 是 | **1** | 深层共振（仅逻辑，无表层） |
| 有 | 否 | **1** | 表层沾边 |
| 有 | 是 | **2** | 强共振（表层 + 逻辑） |

* **0 分守门**：纯偶然、非承重的表层重叠判 0（「换条无关新闻同样能解释这部片」= 0）。
* **可选子标签 POV变换**：仅 `共振分 = 2` 时可标，表示该强共振靠视角/尺度变换才看得出来（Gap A 模式）。
* LLM judge 输出 `score + resonance_type + causal_test`（因果反测句），校验同一矩阵。

### 8.2 通过线（N=10）

1. **批次通过率 ≥ 60%**（必要下限，证明力弱）。
2. **关联增量优于基线（验收核心）**：中性基线候选集 2 分率 **<** 创作侧（12 persona 合并）候选集 2 分率。优先比 `共振类型 ∈ {深层共振, 强共振}` 的率或单独比强共振 2 分率。

### 8.3 Phase 3 闸门结果（截至 2026-06-14）

| Phase | 主题 | 结果 |
| --- | --- | --- |
| 3.5 / 3.6 | 现实解构 + 多 pseudo 管线 | 方向成立、未达发布标准（历史 GATE_FAIL） |
| 3.7 | 12 persona 落地 | 结案 No-Go（[Phase3.7-closure-report](../reports/Phase3.7-closure-report.md)） |
| 3.8 / 3.9 | A0 逐字 + 客观扩展 + 中性通道 + 三桶 + LLM-judge | 3.9 GATE no-go；judge 校准达标采信为预筛 |
| **3.10** | 双轴 rubric + judge 转评测预筛 | **GATE GO**（2026-06-10，D1–D5） |
| **3.11.8** | fragment ladder / search unit 架构 | **GATE GO**（2026-06-13；net-new 2-rate 15.9% ≥ baseline 13.6%，守卫零硬失败） |

**当前结论**：架构链路已收敛、闸门 GO，可进入 Phase 4。**遗留技术债**（[ADR-0010](../adr/0010-pseudo-drop-granularity-and-pipeline-first-derisking.md) D4）：① 5 条 baseline human-2 因新排序落出预算——经复盘 **接受**这是顶替式（replacement-over-additive）排序策略下的正常代价（其中 4 条属可接受的正常流失，1 条 `A Ticket to Space`（judge=0）本就该掉出），**不**做 retention floor 调优；② judge 仍 screening-only，人工打分未覆盖净新增候选，接 RSS 新分布前须补一次轻量校准（见 Phase 5 todo 5.4）。

---

## 9. 实施计划（Roadmap）

### 已完成（Phase 0–3）

* 索引复用（ADR-0001）、endpoint smoke test、prompts、agents/personas、retrieve、五段流水、双轴 rubric、judge 预筛、fragment ladder / search unit。Phase 3 全部 GATE GO。

### Phase 4 · 呈现层 / 中文文案（即将启动）

* C1 中文审核文案（batch 生成）；C2 中英多平台定稿。
* **OPEN（[ADR-0007](../adr/0007-logic-resonance-judge-prescreen-and-pov-focalization.md) a）**：是否在 reader-facing 文案做 POV 聚焦（被击中的最强位置）——本 PRD 登记为待决。
* 债1（baseline 顶替流失）**接受为正常代价**，不做 retention 调优；债2（judge 校准）移至 Phase 5 todo 5.4 在 RSS 真实分布上补齐。

### Phase 5 · 新闻接入

* `fetch_news.py` RSS 接入 + 去重；judge 在 RSS 新分布重测对齐后才当预筛。

### Post-MVP（按效果排期）

* 历史去重（电影/新闻维度）、`generate_planet.py` 视觉、C2 更多平台/语种、候选过滤策略、索引增量更新、运维（日志/告警/调度）、自动热度评分、自动发布、hybrid recall 子信号展开、additive vs replacement 最终口径。

---

## 10. 项目结构（参考）

```
themoviecosmos-daily-stargazing/        ← Obsidian Vault Root
├── data/
│   ├── index/                          # embeddings.npy + meta.parquet（gitignore）
│   └── output/                         # 复用 cosmos 的 cleaned.csv + text_embeddings.npy
├── docs/
│   ├── adr/                            # 0001–0010 架构决策
│   ├── reports/                        # 各 Phase 交付报告
│   ├── eval-the-bet.md                 # 验证闸门手册
│   ├── eval-phase3.10-holdout-freeze-discipline.md
│   └── SSOT/
│       ├── 电影宇宙「每日星轨观测」系统 PRD.md   # 本文件
│       ├── personas-12.md              # 12 persona roster
│       ├── news-to-film-pipeline.md  # fragment ladder 精简版工作流
│       └── reality-deconstruction-contract.md  # A0 逐字抽取契约
├── prompts/
│   ├── _shared/
│   │   ├── deentification_rules.md
│   │   ├── persona_alt_creator_contract.md
│   │   ├── persona_screenwriter_contract.md
│   │   ├── resonance_definition_v2.md
│   │   ├── multi_pseudo_output_contract.md
│   │   └── output_contract.md
│   ├── personas/<persona_id>/persona_card.md   # 12 张（The-Innocent … The-Jester）
│   ├── A0_reality_deconstructor.md
│   ├── C1_copywriter_review.md
│   └── C2_copywriter_multiplatform.md
│   # 注：A1/A2/A4/A7 prompt 为历史四 agent 遗留，已被 12 persona 取代
├── scripts/
│   ├── lib/                            # env / llm / paths / phase311_pilot 等
│   ├── deconstruct.py                  # A0
│   ├── fragment_ladder.py              # fragment ladder + 内联 objective 生成 + 客观性试金石
│   ├── personas.py                     # P-Lens / P-Compose / fragment ladder / search unit
│   ├── retrieve.py                     # 召回 + convergent sort + 池差分解
│   ├── llm_judge.py / judge_prescreen.py
│   ├── resonance_rubric.py
│   ├── run_eval.py / summarize_eval.py / score_eval_candidates.py
│   ├── build_index.py
│   ├── fetch_news.py                   # Phase 5
│   └── main.py
├── output/
│   ├── Eval/                           # 评测产物（phase3.x 子目录）
│   └── Daily_Briefing/                 # 正式日报
├── state/seen_news.sqlite
├── CONTEXT.md                          # 术语 SSOT
└── requirements.txt
```

---

## 11. 显式不在 MVP 内的事项（避免范围蔓延）

* 自动化热度评分挑新闻（手动指定 url 可绕过）
* 候选过滤（相似度阈值、评分、年代、成人内容）
* 历史去重（电影 / 新闻）
* `generate_planet.py` 星球视觉
* C2 平台定稿 / 中英双语（属 Phase 4 Stage 1，MVP GATE 通过后才解封；MVP 只产中文审核稿落 Obsidian）
* 自动发布、索引增量更新、日志/监控/告警/定时调度
* RSS 源内容过滤
* hybrid recall 的 lexical / weighted ladder 子信号全展开
* additive vs replacement 的产品化最终口径（[ADR-0010](../adr/0010-pseudo-drop-granularity-and-pipeline-first-derisking.md) D3 遗留）