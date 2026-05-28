# 电影宇宙「每日星轨观测」系统 PRD

> **当前版本**：v0.2（MVP 决策落地版）
> **更新日期**：2026-05-29
> **状态**：MVP 建造期。**首要目标是验证「新闻输入 → 多 Agent 写 pseudo-overview → 向量召回电影」这条链是否可行**。所有非必要环节（自动发布、视觉切片、运维告警、内容过滤、历史去重等）均显式延后到 Post-MVP。

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
  * 输入：与原 3D 宇宙项目对齐，**直接使用 TMDB 原文（清洗后的 tagline + overview），不做机器翻译**，依靠多语言模型本身的对齐能力。
  * 输出：`embeddings.npy`（L2 归一化）+ `meta.parquet`（仅保留检索/渲染必需字段）。
  * 不做 UMAP / 不拼接 Genres / 不拼接 Language——**打破类型壁垒，纯粹基于剧情结构和隐喻做跨界检索**。
  * 数据规模：约 **60,000 部电影**，6 万级用 NumPy 矩阵乘法 + `argpartition` 毫秒级即可，**不引入 FAISS**。

---

## 3. 数据层规约（Data Contract）

### 3.1 源数据

* **来源 CSV schema**：见 `data/subsample/TMDB_all_movies_random20.csv`。
* **进入索引的必需字段**：`id, title, original_title, overview, tagline, genres, original_language, release_date, poster_path`。
* **数据库规模**：约 60k 行（MVP 用 20 行 subsample 跑通链路，再切全量）。

### 3.2 文本清洗与缺失值处理

按以下规则生成用于 embedding 的 `text_for_embedding` 字段：

| 情况 | 处理 |
| --- | --- |
| `tagline` 大量为空 | **接受**，embedding 降级为 `overview` only |
| `overview` 缺失 | 用 `title`（必要时加 `original_title`）回填 |
| `overview` 仍为空 | **剔除该行**（不进入索引） |
| 仅有原语种简介 | **保留原文**，依赖多语言模型对齐 |
| 字符串前后空白、HTML 残片、引号变体 | 统一清洗 |

embedding 输入文本拼接公式（建议）：

```
text = (f"{tagline.strip()}. " if tagline else "") + (overview or title).strip()
```

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
| A1 | 现实记录员 | 直译核心物理动作 |
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

**MVP 落地策略**：先实现差异度最大的 **A2 社会学家 / A4 神话学者 / A7 混沌理论家** 三个，跑通主链路、确认风格差异化有效后，再补齐剩余 4 个。**七个一开始全写容易风格趋同，且未验证 LLM 对人格设定的服从度。**

### 4.3 去实体化（De-entification）规则

**公共硬规则**（写入 `prompts/_shared/deentification_rules.md`，由所有 Persona 引用）：

1. 不得出现真实人名 → 替换为身份角色（"一位政治领袖" / "一名科技寡头" / "一名记者"）
2. 不得出现真实地名 / 国家 / 城市 → 替换为环境特征（"一个北方港口城市" / "一座内陆首都"）
3. 不得出现真实机构 / 品牌 / 政党 / 公司名 → 替换为类型（"一家跨国能源公司" / "一个执政党"）
4. 不得出现具体日期 / 精确金额 / 精确数字 → 模糊量级（"近期" / "巨额" / "数以千计"）
5. 不得出现新闻八股（"据报道" / "声明称" / "日前" / "本台讯"）
6. **输出语种 = 新闻原文语种**（中文新闻 → 中文 pseudo；英文新闻 → 英文 pseudo），以便多语言向量召回时跨语对齐由模型负责。

**软规则**（写电影简介的口吻）：

* 主语必须是"一个 / 某个 [角色]"，不是具名实体
* 优先现在时
* 长度 **80 ~ 150 字**，单段
* 末尾不要有"这是一部关于……的电影"之类的元描述

**few-shot 示例**（每个 Persona 自带 1 ~ 2 个，是对齐质量的关键）：

> 原新闻：Elon Musk announced on X that Tesla will lay off 10% of its global workforce.
>
> A2 社会学家输出：「一位技术先知在他亲手缔造的舆论广场上宣告：他的钢铁帝国将吐出十分之一的工人。曾被神话包裹的造梦机器，在一份冷漠的财报面前，露出它最古老的面孔——资本对劳动的清算。」

### 4.4 输出契约（Output Contract，MVP 极简版）

* 每个 Agent 返回**纯文本一段**，不强制 JSON，由 `agents.py` 做基础清洗（去多余空行 / 截断超长）。
* 失败/超时/格式异常 → **MVP 阶段允许跳过该 Agent**，主流程继续；记录到当日简报的 `errors` 节里。
* 重试与降级是工程问题，暂缓。

---

## 5. 检索与候选处理（Retrieval & Candidates）

### 5.1 召回

* 每段 pseudo-overview → 384 维向量（L2 归一化）。
* 在 `embeddings.npy` 上做余弦相似度（= 内积）。
* 每个 Agent 取 **Top 2**，7 Agent × 2 = **最多 14 部候选**。

### 5.2 候选处理（MVP 决策）

| 议题 | MVP 决策 |
| --- | --- |
| 跨 Agent 撞车（同一部电影被多个视角召回） | **强信号**，保留并在 Markdown 里聚合展示「触发该电影的 Agent 视角列表」。可视为加权推荐线索。 |
| 相似度下限 | 不设，先看效果 |
| 候选过滤（评分/年代/成人内容） | 不做，先看效果 |
| 历史去重（同一部电影不再推荐） | 不做（Post-MVP 必做） |
| 召回的额外 metadata（导演/演员等） | 不做，MVP 仅 `title / overview / genres / release_year / language / poster_path / tmdb_id` |

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

## 七视角伪剧情（去实体化）
- A2 社会学家: ...
- A4 神话学者: ...
- A7 混沌理论家: ...

## 候选星轨（共 N 部）
### 1. {Title} ({year}) [由 A2, A4 共同召回]
- 相似度: 0.xx
- Genres: ...
- Overview: ...
- 跳转: https://themoviecosmos.com/movie/{tmdb_id}
```

### 7.3 跳转链接

* 格式：`https://themoviecosmos.com/movie/{tmdb_id}`
* 简报里每部候选电影都附该链接，方便总编一键跳到 3D 宇宙。

### 7.4 视觉切片与发布

* `generate_planet.py`（生成星球视觉图）= **Post-MVP**。
* 两句冷峻观测短评 = LLM 撰写，长度匹配各社媒限制 = **Post-MVP**。
* 社媒发布 = **始终先手动**，自动化是远期话题。

---

## 8. 自动化工作流（Workflow，MVP 范围）

整条自动化管线只跑到 Obsidian 归档：

| Step | 动作 | MVP 自动化级别 |
| --- | --- | --- |
| 1 | 拉取 RSS → 候选新闻列表 → 选 1 条 | 半自动（允许人工指定 url） |
| 2 | 异步并发调用 3 个 Persona Agent（MVP）→ 3 段 pseudo-overview | 自动 |
| 3 | 3 段文本 → 向量 → 在 npy 索引上召回 Top 2 × 3 = ≤ 6 部 | 自动 |
| 4 | 渲染 Markdown 模板 → 写入 `output/Daily_Briefing/YYYY-MM-DD.md` | 自动 |
| 5 | 人类总编在 Obsidian 中拍板 | 人工 |

> 注：Persona 数量从 7 缩减为 3 是 MVP 内部的临时决策，待主链路稳定后再扩展到 7。

---

## 9. 网页端承接能力（现有基础）

前端已支持通过 URL `?focus_movie=xxx`（或 path `/movie/xxx`）自动深层链接跳转、相机飞跃动画、详细信息面板展开。无需改动。

---

## 10. 实施计划（Roadmap）

### Phase 1 · MVP 建造期（当前）

**执行顺序刻意从底向上、每步独立可验证：**

1. **[算法层 - 基建]** `scripts/build_index.py`：先在 `data/subsample/TMDB_all_movies_random20.csv` 上跑通 embedding + 落 `embeddings.npy` + `meta.parquet`；脚本设计成只换 csv 路径即可全量。
2. **[大模型层]** `prompts/`：编写公共去实体化规则、输出契约，以及 A2 / A4 / A7 三个 Persona。
3. **[逻辑层 - Agents]** `scripts/agents.py`：加载 prompts，异步并发调用 MiMo，手喂一段新闻验证 pseudo-overview 质量。
4. **[逻辑层 - Retrieve]** `scripts/retrieve.py`：3 段 pseudo → 召回候选，肉眼检查匹配是否"有味道"。
5. **[逻辑层 - News]** `scripts/fetch_news.py`：feedparser + URL 去重 + 标题相似度去重。
6. **[集成层]** `scripts/main.py`：串起来 → 输出 `output/Daily_Briefing/2026-MM-DD.md`。

**该顺序的好处**：链路核心风险（LLM 输出质量、召回相关性）在花时间挑 RSS 源之前就会暴露。

### Phase 2 · Post-MVP（候选清单，按效果排期）

* 补齐 Persona 至 7 个
* 历史去重（电影维度、新闻维度）
* `generate_planet.py` 视觉切片
* 社媒短评 LLM 生成器（多平台字数适配）
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
│   ├── A2_sociologist.md
│   ├── A4_mythologist.md
│   └── A7_chaos_theorist.md
├── scripts/
│   ├── build_index.py
│   ├── fetch_news.py
│   ├── agents.py
│   ├── retrieve.py
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
* 7 个 Persona 全量上线（MVP 只跑 3 个）
* `generate_planet.py` 星球视觉
* 短评 LLM 生成与社媒适配
* 自动发布
* 索引增量更新
* 日志/监控/告警/定时调度
* RSS 源内容过滤
* JSON Schema 强约束 / 重试降级 / 模型路由
