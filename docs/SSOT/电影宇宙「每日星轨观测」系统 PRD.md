# 电影宇宙「每日星轨观测」系统 PRD

> **当前版本**：v0.3（语种工作流落地版）
> **更新日期**：2026-05-29
> **状态**：MVP 建造期。**首要目标是验证「新闻输入 → 多 Agent 写英文 pseudo-overview → 向量召回电影 → 中文文案供审核」这条链是否可行**。所有非必要环节（自动发布、视觉切片、运维告警、内容过滤、历史去重等）均显式延后到 Post-MVP。
>
> **v0.3 工作流要点（语种）**：电影库为全英文，故 **Persona prompts 与 pseudo-overview 统一用英文**做检索；召回电影后**用中文为每部候选写社媒文案供总编挑选审核**；总编选定后再**按平台生成对应语言版本（MVP 仅中英两种）**。

---

## 1. 产品概述（Product Overview）

### 1.1 背景与痛点

已完成的核心资产是「基于 TMDB 与 UMAP 算法的 3D 电影宇宙」（[themoviecosmos.com](https://themoviecosmos.com)），它以中立、客观的视角收录了人类电影史的全量样本。但作为一个静态数字档案，它缺乏与真实世界的纽带，难以持续吸引具备探索欲的用户。

### 1.2 产品目标

打造一个「数字文化天文台」。以每日热点事件为引，挖掘现实事件与某一部电影之间绝妙的讽刺、反差或隐喻联系。

**核心理念**：推荐不是为了催促观看，而是展示「现实世界与数字宇宙的结构性共振」，以此满足好奇心并完成对 3D 电影宇宙的引流。

### 1.3 MVP 验证目标（v0.2 新增）

本阶段**只需要回答一个问题**：

> 在「单条新闻 → 7 个 Persona 视角的 pseudo-overview → 在 6 万部电影里做纯文本召回」的链路上，是否能稳定产出**至少 1 部具备「绝妙讽刺/宿命隐喻」感的候选电影**？

所有工程化、自动化、风控、UI 决策都让位于这个问题的回答。

---

## 2. 系统架构与技术栈（Architecture & Tech Stack）

* **大模型编剧室（Multi-Agent 架构）**：物理隔离的 Persona 工作流。每个 Agent 拥有独立的 Markdown 人格文档，由主控脚本异步并发调用。
* **LLM 提供方（MVP 决策）**：主用 **MiMo 2.5 / 2.5 Pro**（已持有 token）；备选 **DeepSeek**（成本低）。不做硬性 token 限制，按效果与用量动态调整。
* **信息源**：**RSS 订阅源**（Python `feedparser` 直接抓取）。MVP 阶段使用免费源，接受其延迟与质量限制。
* **总编与决策台（Human-in-the-Loop）**：当前项目根目录即 **Obsidian Vault**，每日简报落到 `output/Daily_Briefing/YYYY-MM-DD.md`，由人类总编在 Obsidian 中完成"火花甄别"。
* **核心检索基建（专项优化）**：构建独立的「纯文本搜索专用库（Search-only Index）」。
  * 模型：`paraphrase-multilingual-MiniLM-L12-v2`
  * 输入：与原 3D 宇宙项目对齐，**直接使用 TMDB 原文（清洗后的 tagline + overview），不做机器翻译**。库为**全英文**，故**检索侧（pseudo-overview）也统一用英文**，与索引同分布，召回更稳；多语言模型能力作为冗余保障。
  * 输出：`embeddings.npy`（L2 归一化）+ `meta.parquet`（仅保留检索/渲染必需字段）。
  * 不做 UMAP / 不拼接 Genres / 不拼接 Language——**打破类型壁垒，纯粹基于剧情结构和隐喻做跨界检索**。
  * 数据规模：**59,341 部**（3D 宇宙策展片单，从 119 万行 Kaggle 原始表清洗而来；非"全量"）。6 万级用 NumPy 矩阵乘法 + `argpartition` 毫秒级即可，**不引入 FAISS**。
  * **索引来源（ADR-0001）**：MVP **直接复用** 3D 宇宙项目产出的 `cleaned.csv` + `text_embeddings.npy`（同模型、同 384 维、已 L2 归一、行序对齐），不自建。详见 `docs/adr/0001-reuse-cosmos-text-embeddings.md`。`build_index.py` 重算逻辑降级为 Post-MVP 备用。

---

## 3. 数据层规约（Data Contract）

### 3.1 源数据

* **来源 CSV schema**：见 `data/subsample/TMDB_all_movies_random20.csv`。
* **进入索引的必需字段**：`id, title, original_title, overview, tagline, genres, original_language, release_date, poster_path`。
* **数据库规模**：**59,341 行**（策展片单 `cleaned.csv`）。20 行 subsample 仅用于验证管线（plumbing），**召回质量/评分只在全量片单上才算数**（见 ADR-0001 与 §10）。

### 3.2 文本清洗与缺失值处理

按以下规则生成用于 embedding 的 `text_for_embedding` 字段：

| 情况 | 处理 |
| --- | --- |
| `tagline` 大量为空 | **接受**，embedding 降级为 `overview` only |
| `overview` 缺失 | 用 `title`（必要时加 `original_title`）回填 |
| `overview` 仍为空 | **剔除该行**（不进入索引） |
| 仅有原语种简介 | **保留原文**，依赖多语言模型对齐 |
| 字符串前后空白、HTML 残片、引号变体 | 统一清洗 |

embedding 输入文本模板（**已对齐 3D 宇宙索引,ADR-0001**）：

```
有 tagline:  f"Tagline: {tagline}\nOverview: {overview}"
无 tagline:  f"Overview: {overview}"
```

> ⚠️ 此模板**同时约束查询侧**:`retrieve.py` 必须把每段 pseudo-overview 套成 `Overview: {pseudo}` 再 encode,保证查询与索引同分布。早期的裸拼接公式 `(tagline + ". ") + overview` **已作废**。

### 3.3 索引产物

| 产物 | 格式 | 用途 |
| --- | --- | --- |
| `data/index/embeddings.npy` | `float32 (N, 384)`，L2 归一化 | 余弦检索 |
| `data/index/meta.parquet` | `id, title, original_title, overview, tagline, genres, original_language, release_date, poster_path` | 渲染 Markdown / 拼跳转链接 |

### 3.4 索引更新策略

* **MVP**：全量重跑。
* **Post-MVP**：增量（按 TMDB `id` 比 diff，只对新增/修改行重新 embed 后 append/replace）。

---

## 4. 多智能体编剧室（Multi-Agent Screenwriting Room）

### 4.1 Persona 总览

| 代号 | 人格 | 核心动作 |
| --- | --- | --- |
| A1 | 现实记录员（**基线/对照**） | 去实体化白描核心物理动作，**不做隐喻** |
| A2 | 社会学家 | 寻找阶级撕裂与资源矛盾 |
| A3 | 心理医生 | 坍缩为个人心理创伤或偏执 |
| A4 | 神话学者 | 套用古典悲剧 / 史诗内核 |
| A5 | 边缘视界导演 | 边缘小人物视角的荒诞日常 |
| A6 | 视觉美学师 | 提炼纯粹的视听奇观与感官氛围 |
| A7 | 混沌理论家 | 倒推极其微小 / 荒谬的灾难起因 |

### 4.2 Persona 文件结构

每个 Persona = `prompts/AX_xxx.md`，统一结构：

```
# AX · 人格名

## 身份
## 哲学准则
## 写作风格
## 示例（few-shot：原新闻 → 你的输出）
## 当前任务（运行时由代码注入新闻字段）
```

**MVP 落地策略**：实现 **3 个创作视角（A2 社会学家 / A4 神话学者 / A7 混沌理论家）+ 1 个基线（A1 现实记录员）**。先跑通主链路、确认风格差异化有效后，再补齐剩余 Persona。**七个一开始全写容易风格趋同，且未验证 LLM 对人格设定的服从度。**

> **A1 的定位 = 实验对照组**：A1 只做去实体化白描、不做任何隐喻，输出最接近 TMDB overview 的中性分布。它存在的唯一目的，是回答 MVP 的核心问题——「创作视角召回的电影，是否真比平铺直叙更妙？」。因此 A1 **不算创作视角**，在简报里单独标 `[baseline]`，且**不计入 §5.2 的跨 Agent 撞车展示**（它是对照组，不是一条创作路径）。

### 4.3 去实体化（De-entification）规则

**公共硬规则**（写入 `prompts/_shared/deentification_rules.md`，由所有 Persona 引用）：

1. 不得出现真实人名 → 替换为身份角色（"一位政治领袖" / "一名科技寡头" / "一名记者"）
2. 不得出现真实地名 / 国家 / 城市 → 替换为环境特征（"一个北方港口城市" / "一座内陆首都"）
3. 不得出现真实机构 / 品牌 / 政党 / 公司名 → 替换为类型（"一家跨国能源公司" / "一个执政党"）
4. 不得出现具体日期 / 精确金额 / 精确数字 → 模糊量级（"近期" / "巨额" / "数以千计"）
5. 不得出现新闻八股（"据报道" / "声明称" / "日前" / "本台讯"）
6. **输出语种 = 英文（统一）**：无论新闻原文是中文还是英文，pseudo-overview 一律写**英文**。原因：电影库为全英文，英文查询与索引同分布，召回更稳；其他语种的展示/文案在下游阶段处理（见 §5.3 / §7.4）。

**软规则**（写电影简介的口吻）：

* 主语必须是"一个 / 某个 [角色]"，不是具名实体
* 优先现在时
* 长度 **60 ~ 120 words**，单段
* 末尾不要有"A film about…"之类的元描述

**few-shot 示例**（每个 Persona 自带 1 ~ 2 个，是对齐质量的关键）：

> 原新闻：Elon Musk announced on X that Tesla will lay off 10% of its global workforce.
>
> A2 社会学家输出（英文）：A prophet of technology proclaims, from the public square he himself built, that his empire of steel will spit out one in ten of its workers. The dream-machine, once wrapped in myth, shows its oldest face before a single cold earnings report — the reckoning of capital against labor.

### 4.4 输出契约（Output Contract，MVP 极简版）

* 每个 Agent 返回**纯文本一段**，不强制 JSON，由 `agents.py` 做基础清洗（去多余空行 / 截断超长）。
* 失败/超时/格式异常 → **MVP 阶段允许跳过该 Agent**，主流程继续；记录到当日简报的 `errors` 节里。
* 重试与降级是工程问题，暂缓。

---

## 5. 检索与候选处理（Retrieval & Candidates）

### 5.1 召回

* 每段**英文** pseudo-overview → 384 维向量（L2 归一化）。
* 在 `embeddings.npy` 上做余弦相似度（= 内积）。
* 每个 Agent 取 **Top 2**，7 Agent × 2 = **最多 14 部候选**。

### 5.2 候选处理（MVP 决策）

| 议题 | MVP 决策 |
| --- | --- |
| 跨 Agent 撞车（同一部电影被多个视角召回） | **仅作中性展示**：在 Markdown 里聚合标注「命中该电影的 Agent 视角列表」，**MVP 不据此加权或排序**。"撞车=强信号"的前提（多视角独立殊途同归）尚未验证，是否成立留待评测期观察。**A1 基线不计入此展示**（仅作对照）。 |
| 相似度下限 | 不设，先看效果 |
| 候选过滤（评分/年代/成人内容） | 不做，先看效果 |
| 历史去重（同一部电影不再推荐） | 不做（Post-MVP 必做） |
| 召回的额外 metadata（导演/演员等） | 不做，MVP 仅 `title / overview / genres / release_year / language / poster_path / tmdb_id` |

### 5.3 候选文案（中文审核稿）

召回得到候选电影后，**为每一部候选电影用中文写一段社媒文案**，供人类总编在简报中挑选审核。

* Prompt：`prompts/C1_copywriter_review.md`。
* 输入：新闻语境（英文 pseudo / 摘要）+ 候选列表（title / year / overview / 触发它的 Agent 视角 / tmdb 链接）。
* 输出：每部候选一段中文文案，写「现实 ↔ 这部电影」的共振点，**不剧透、不影评腔、不喊看片**。
* 这是**审核稿**，不带 hashtag、不分平台；总编只需从中勾选「有味道」的那条。
* 此阶段语种固定中文（总编母语审核）；与检索侧的英文互不影响。

---

## 6. 新闻源与新闻选择（News Source）

### 6.1 RSS 源策略

* **MVP**：暂用免费 RSS 源；具体清单未定，落到 `scripts/fetch_news.py` 的配置常量里，方便后续替换。
* 接受免费源的延迟和质量限制。

### 6.2 「最具张力的新闻」如何选

* **MVP 决策**：按**热度排序**取 Top 1。
* MVP 阶段允许人工挑选（即从拉取列表中手动指定一条 url 给主流程），把验证重心放在 Agent + 召回链路上。
* 自动化的"热度评分"算法（多源同事件计数 + 时间近端加权）放到 Post-MVP。

### 6.3 新闻字段（喂给 Agent 的 payload）

```
title          (必需)
description    (必需，RSS 自带摘要，200~500 字够用)
pub_time       (可选)
source_name    (可选)
```

**不爬全文**——RSS summary 已是浓缩信号，全文反而稀释焦点。

### 6.4 去重机制

* **URL 级去重**：规范化 url（剥 utm 参数）后落 `state/seen_news.sqlite`，跑过即跳过。
* **历史标题去重（轻量）**：保留过去 **14 天** 选过的标题，新选标题用 `difflib.SequenceMatcher` 比，相似度 ≥ 0.7 跳过。
* 不上语义级（embedding）去重。

### 6.5 内容过滤

* **MVP 阶段不在新闻源做内容过滤**。
* 内容把关由**人类总编在 Obsidian 简报阶段**或**社媒发布前**完成。
* 若上线后发现高频踩雷，再考虑在源头加过滤。

---

## 7. 简报与下游产物（Daily Dossier）

### 7.1 输出位置

* 项目根目录 = Obsidian Vault。
* 简报目录：`output/Daily_Briefing/YYYY-MM-DD.md`。
* Markdown 模板与归档结构细节先不固定，**等产出 3 ~ 5 份真实简报后再迭代模板**。

### 7.2 简报内容（最小骨架）

```markdown
# 每日星轨观测 · YYYY-MM-DD

## 现实波澜
- title / source / pub_time / url
- summary

## 伪剧情（去实体化 · 英文，用于检索）
- A2 The Sociologist: ...
- A4 The Mythologist: ...
- A7 The Chaos Theorist: ...
- A1 The Reality Recorder [baseline]: ...

## 候选星轨（共 N 部）
### 1. {Title} ({year}) [由 A2, A4 共同召回]
- 相似度: 0.xx
- Genres: ...
- Overview: ...
- 跳转: https://themoviecosmos.com/movie/{tmdb_id}
- 中文文案（审核稿，C1）: ...   ← 总编在此勾选「✅ 选用」
```

> 总编工作流：在「候选星轨」里勾选 1 条满意的中文文案，再交给 C2 生成各平台版本（见 §7.4）。

### 7.3 跳转链接

* 格式：`https://themoviecosmos.com/movie/{tmdb_id}`
* 简报里每部候选电影都附该链接，方便总编一键跳到 3D 宇宙。

### 7.4 文案定稿（多平台多语言）

总编从简报里勾选一条中文审核稿后，用 `prompts/C2_copywriter_multiplatform.md` 生成各平台发布版本：

* **MVP 范围：仅中、英两种语言**，分别适配一个中文平台（微博 / 小红书，≤140 字）与一个英文平台（X / Twitter，≤280 字符）。
* 英文版**非直译**：保留同一「现实 ↔ 电影」共振内核，用地道英文重写。
* 每版附跳转 `https://themoviecosmos.com/movie/{tmdb_id}` 与 0~2 个自然话题标签。
* 产物可落到简报同目录（如 `output/Daily_Briefing/YYYY-MM-DD_copy.md`）供复制发布。

### 7.5 视觉切片与发布

* `generate_planet.py`（生成星球视觉图）= **Post-MVP**。
* 更多平台 / 更多语言版本（Instagram、Threads、日韩语等）= **Post-MVP**。
* 社媒发布 = **始终先手动**，自动化是远期话题。

---

## 8. 自动化工作流（Workflow，MVP 范围）

整条自动化管线只跑到 Obsidian 归档：

| Step | 动作 | MVP 自动化级别 |
| --- | --- | --- |
| 1 | 拉取 RSS → 候选新闻列表 → 选 1 条 | 半自动（允许人工指定 url） |
| 2 | 异步并发调用 4 个 Agent（3 创作 A2/A4/A7 + 基线 A1，英文）→ 4 段英文 pseudo-overview | 自动 |
| 3 | 4 段英文文本 → 向量 → 在 npy 索引上召回 Top 2 × 4 = ≤ 8 部（A1 候选标 `[baseline]`） | 自动 |
| 4 | C1 为每部候选写中文审核文案 | 自动 |
| 5 | 渲染 Markdown 模板（含候选 + 中文文案）→ 写入 `output/Daily_Briefing/YYYY-MM-DD.md` | 自动 |
| 6 | 人类总编在 Obsidian 中勾选 1 条文案 | 人工 |
| 7 | C2 把选定文案改写为中/英平台版本 → `..._copy.md` | 自动（人工触发） |

> 注 1：MVP 跑 3 个创作 Persona（A2/A4/A7）+ 1 个基线（A1），待主链路稳定后再扩展到 7 个创作视角。
> 注 2：语种约定——Step 2/3（检索）走**英文**；Step 4（审核稿）走**中文**；Step 7（定稿）产出**中 + 英**两版。

---

## 9. 网页端承接能力（现有基础）

前端稳定深链入口为 **`/movie/{tmdb_id}`**（Phase 30 契约,分享/OG/`_redirects` 均以此为准）。`{tmdb_id}` = `cleaned.csv` 的 `id` 列（TMDB 数字 id,非 imdb_id）。可附 `?lang=` / `?theme=` / `?timeline=` 等 query。

> ⚠️ 旧版 PRD 写的 `?focus_movie=xxx` **当前代码库不存在该参数**,勿用。海报完整 URL = `https://image.tmdb.org/t/p/w780` + `poster_path`（MVP 简报不渲染图,低优先）。

---

## 10. 实施计划（Roadmap）

### Phase 1 · MVP 建造期（当前）

**执行顺序刻意从底向上、每步独立可验证；并显式区分「验证管线 plumbing」与「验证赌注 the bet」。**

> 关键原则:**召回质量只在全量片单(59,341)上才算数**;20 行 subsample 仅用于验证脚本能跑(plumbing),不看召回质量、不评分。

0. **[基建 · 索引复用,ADR-0001]** 把 cosmos 的 `cleaned.csv` + `text_embeddings.npy` 拷入 `data/output/`(已完成);`build_index.py` 仅负责:从 `cleaned.csv` 选 9 列生成 `meta.parquet`、把 `text_embeddings.npy` 接成索引、断言行数对齐(59,341,已实测)。从 CSV 重算的逻辑降级为 Post-MVP 备用。
1. **[地基校验]** **endpoint smoke test**:拿配好的 MiMo OpenAI 兼容 endpoint 打一句 trivial prompt,确认 auth + 模型名 + 协议三件事都通,再写正式逻辑。
2. **[Prompts]** `prompts/` **已写完**(公共去实体化规则 + 输出契约 + A1/A2/A4/A7 + C1/C2)。
3. **[Agents]** `scripts/agents.py`:加载 prompts,异步并发调用 MiMo(默认 provider),产 4 段英文 pseudo(A2/A4/A7 + 基线 A1)。手喂新闻肉眼验去实体化质量与风格差异。
4. **[Retrieve]** `scripts/retrieve.py`:每段 pseudo **套 `Overview: {pseudo}` 模板**(与索引同分布,ADR-0001)→ 召回 Top-2;**撞车仅作中性展示**(标命中视角列表,不加权);**可选**记一个发散度探针(查询两两余弦 + Top-K Jaccard)供观察。
5. **[★ 验证闸门 · The Bet]** 在**全量片单**上,从真实抓取(不挑源)的新闻里**手挑 N=10 条**跑链路,总编评分,分数写进简报。
   - **评分口径**:对每个去重后的 `(新闻, 电影)` 候选打**一次** 0/1/2 共振分(共振是 news↔电影 的属性,与召回它的 agent 无关),再把该分**归属给所有召回了它的视角**。
   - **通过线**:≥60% 批次至少出 1 个 2 分候选,**且** A1 基线候选集的 2 分率 < 创作视角(A2/A4/A7)合并候选集的 2 分率(看频率差,A1 偶中 2 分无妨)。
   - **没过 → 回到 step 3/4 调 prompt 或查召回,不要往下走。**
6. **[Copy · 闸门后]** `scripts/copywriter.py`:**闸门过了才接** C1(为候选批量生成中文审核文案);C2(中英多平台定稿)更靠后,依赖总编已勾选定稿。
7. **[News]** `scripts/fetch_news.py`:feedparser + **宽口径中立源(MVP 不对源做偏好)** + URL 去重 + 标题相似度去重;CLI 打印带序号清单 → 人工把选中 url 传给 main。
8. **[集成]** `scripts/main.py`:串起来 → 输出 `output/Daily_Briefing/2026-MM-DD.md`。

**该顺序的好处**:链路核心风险(LLM 输出质量、召回相关性)在花时间挑 RSS 源、写文案之前就会在 step 5 闸门处暴露。

### Phase 2 · Post-MVP（候选清单，按效果排期）

* 补齐 Persona 至 7 个
* 历史去重（电影维度、新闻维度）
* `generate_planet.py` 视觉切片
* C2 扩展更多平台 / 更多语言（Instagram、Threads、日韩语等；MVP 仅中英）
* 候选过滤策略（评分阈值 / 成人内容 / 冷门下限）
* 索引增量更新
* 运维：日志、失败告警、定时调度（cron / GitHub Actions）
* 自动化"热度评分"算法
* 自动发布到社媒

---

## 11. 项目结构（参考）

```
themoviecosmos-daily-stargazing/        ← Obsidian Vault Root
├── .obsidian/                          # Obsidian 配置
├── data/
│   ├── subsample/                      # 20 行样本（已有）
│   ├── full/                           # 60k 全量（gitignore）
│   └── index/                          # embeddings.npy + meta.parquet（gitignore）
├── docs/
│   └── SSOT/电影宇宙「每日星轨观测」系统 PRD.md
├── prompts/
│   ├── _shared/
│   │   ├── deentification_rules.md
│   │   └── output_contract.md
│   ├── A1_reality_recorder.md       # 英文基线/对照（不做隐喻）
│   ├── A2_sociologist.md            # 英文 Persona
│   ├── A4_mythologist.md            # 英文 Persona
│   ├── A7_chaos_theorist.md         # 英文 Persona
│   ├── C1_copywriter_review.md      # 中文审核文案
│   └── C2_copywriter_multiplatform.md  # 中英多平台定稿
├── scripts/
│   ├── build_index.py
│   ├── fetch_news.py
│   ├── agents.py
│   ├── retrieve.py
│   ├── copywriter.py               # C1 / C2 调用
│   └── main.py
├── output/
│   └── Daily_Briefing/                 # 每日简报（Obsidian 阅读入口）
├── state/
│   └── seen_news.sqlite                # URL/标题历史去重
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

---

## 12. 显式不在 MVP 内的事项（避免范围蔓延）

* 自动化"热度评分"挑新闻（手动指定 url 可绕过）
* 候选过滤（相似度阈值、评分、年代、成人内容）
* 历史去重（电影 / 新闻）
* 7 个创作 Persona 全量上线（MVP 只跑 A2/A4/A7 + 基线 A1）
* `generate_planet.py` 星球视觉
* C2 多平台 / 多语言扩展（MVP 仅中英两版，更多平台与语种留到 Post-MVP）
* 自动发布
* 索引增量更新
* 日志/监控/告警/定时调度
* RSS 源内容过滤
* JSON Schema 强约束 / 重试降级 / 模型路由
