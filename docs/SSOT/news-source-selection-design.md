# 新闻源选择与格式感知抽取：设计 SSOT

> **状态**：`intake`/选材 阶段的抓取源设计权威（Phase 5.4 抓取源改进期）。产品/架构决策记账见 [ADR-0014](../adr/0014-news-source-selection-and-automation-boundary.md)；阶段命名与管线全景见 [`news-to-film-pipeline.md`](news-to-film-pipeline.md)（本文件是其 `intake` 阶段的下钻设计）。
>
> **定位**：承载与用户十几轮讨论敲定的「新闻源怎么选、怎么抽、自动化边界在哪」的完整共识。回答四个问题：①用什么源（Guardian Content API 替代 RSS）；②放行哪些 section（宽进黑名单制）；③每条新闻抽哪几段（tone 标签驱动的格式感知抽取）；④人工介入点在哪（新闻侧全自动，人工只在电影侧）。
>
> **落地物偏差**：承载脚本当前实际为 `scripts/fetch_news.py`（目标名 `intake.py`，偏差见 ADR-0011）。本文档凡涉及脚本/CLI，均按现状 `fetch_news.py` 书写。

---

## 0. 一句话概括

> 事件侧（新闻）**全自动**、**宽进**、**按体裁抽取**；筛选责任交给未来的**热度排序**，而不是 section 白名单或表层文本相似度。人工只在**电影侧**做最终挑选。

---

## 1. 背景：为什么要改抓取源

### 1.1 项目里新闻的唯一职责

本项目 = 给**当下最热的新闻事件**，找一部在**深层逻辑上共振**的老电影，人工总编从候选里挑最佳，LLM 写稿发社媒。

- **影像侧**已有自己的电影库（TMDB overview 向量），是被匹配的一端。
- **新闻侧**（Guardian）**只提供事件源**，是发起匹配的一端。

因此新闻源的设计目标只有一个：**稳定、高质量地固化"当下正在发生的事件原文"**，喂给下游 `extract → expand → rewrite → retrieve`。

### 1.2 RSS 效果不好的根因

当前 `fetch_news.py` 默认走 RSS，实测效果不好，根因有四：

| 问题 | RSS 现状 | 后果 |
| --- | --- | --- |
| 源太窄 | 仅 3 个宽泛 Guardian feed | 覆盖不到细分选题 |
| 无正文 | RSS 只给 summary | 下游 extract 缺料，解构质量差 |
| 无法选精 | 无 section / tag 维度 | 无法按体裁做差异化处理 |
| 无质量信号 | 无 tone / 结构信息 | 只能盲取前 N 段，信噪比不可控 |

**结论**：换用 Guardian Content API（key 已在 `.env` 的 `GUARDIAN_API_KEY`），拿到正文 + section + `tone/*` 标签，把「盲取」升级为「按体裁抽取」。

---

## 2. 决策 A · 抓取源：Guardian Content API

### 2.1 请求口径

```text
GET https://content.guardianapis.com/search
  ?api-key       = <GUARDIAN_API_KEY>       # 来自 .env
  &show-fields   = bodyText,trailText,...   # 拿纯文本正文
  &show-tags     = all                      # 关键：拿 tone/* 体裁标签
  &section       = <逗号分隔，见决策 B>       # 宽进，见黑名单
  &order-by      = newest                    # 见 §2.2：API 无热度维度
  &page-size     = <N>                       # 单 section 抓取量
```

`fetch_news.py` 里 Guardian API provider 已存在，本次只是把 **CLI 默认从 RSS 切到 API**，并接上 section 策略 + tone 抽取。

### 2.2 已验证的关键事实

- `show-tags=all` 返回 `tone/*` 标签：**实测 240 篇 / 8 section，233 篇有 tone 标签 = 97.1% 覆盖**；7 篇无标签；部分文章带多个 tone 标签。
  - 实例：honey brioche → `tone/recipes`；Switzerland 2-0 live → `tone/minutebyminute`；Taylor Swift → `tone/comment`。
- `order-by` **仅支持 `newest / oldest / relevance`**，**不提供热度 / popularity / most-viewed 维度**。→ 这直接决定了「热度排序」必须自研（决策 D）。

---

## 3. 决策 B · section 策略：宽进黑名单制

### 3.1 原则

> **默认全放行，只排除"结构性非内容"**。不再用白名单精选 section。

理由：section **不是**成本闸门也**不是**相关性闸门。匹配失败的成本很低（下游自然 miss），宁放勿缺。真正的选题闸门是**热度排序**（决策 D），不是 section。film/culture/education/food/sport 等全部放行——最坏情况只是下游匹配失败。

### 3.2 黑名单（只排除这五类）

| 类别 | 排除项 | 为什么排 |
| --- | --- | --- |
| ① 行业垂直 / B2B | 所有 `*-network`、`*professional` 后缀 | 面向从业者的商业内容，非公共事件 |
| ② Guardian meta / 工具页 | about, community, crosswords, extra, guardian-foundation, help, info, jobsadvice, katine, membership, search, theguardian, theobserver, thefilter, thefilter-us | 站务/工具页，无事件内容 |
| ③ 纯功能页 | weather, travel-offers | 服务信息，非事件 |
| ④ 地方新闻 | local, cardiff, edinburgh, leeds, cities | 地方性过强，共振受众面窄 |
| ⑤ 低事件旅行内容 | travel | 以游记散文/攻略服务为主，极少完整公共事件，个性化强、难形成共鸣 |

其余全部放行。`culture` / `film` 等混合 section 不在 section 层处理：其中既有文化事件也有个性化随笔，后者属于 D4 热度排序的语义价值判断，不用 tone 或相似度提前处理。黑名单以常量形式集中维护，便于审计增删。

---

## 4. 决策 C · 格式感知抽取：tone 标签驱动

### 4.1 为什么不能盲取前 N 段

不同体裁文章**结构不同**，"取前 5 段"对不同结构效果相反：

| 结构类型 | 代表体裁 | 前 5 段 |
| --- | --- | --- |
| 倒金字塔（硬新闻） | `tone/news` | ✅ 增益：核心事实在前 |
| 平铺 / 列表 / 论述 | `tone/recipes` | ❌ 噪声：前几段可能是配料/步骤铺陈，核心分散 |
| 即时 / 非事件体裁 | `tone/minutebyminute`、`tone/letters`、`tone/competitions` | 🚫 整条丢弃：直播流水/读者来信/投稿征集缺少完整起因-经过-结果叙事结构 |

已实证（`state/guardian_3v5_comparison.md`）：软文（菜谱等）取前 5 段明显被污染，只取 lede 更干净。

**硬/软的本质是结构（倒金字塔 vs 平铺），不是话题严肃度。**

### 4.2 抽取路由（DROP 优先，然后 tone 优先级有序查表）

```text
输入：article.tags (含 0..n 个 tone/*)、article.bodyText
输出：DROP 或抽取策略 → 取哪几段

# 决策优先级（自上而下，命中即停）
route(article):
    tones = [t for t in article.tags if t.startswith("tone/")]

    # (0) tone DROP 黑名单优先于一切仲裁：任意命中即整条丢弃
    #     即使同一篇同时带 tone/minutebyminute + tone/news，也不能被 news 救回。
    if any(t in TONE_DROP_BLACKLIST for t in tones):
        return DROP

    # (1) 具体体裁优先于泛化体裁：多 tone 时按"具体度"仲裁
    #     具体度高 = 结构强绑定抽取策略（recipes/reviews/interview...）
    #     具体度低 = 泛化（news/features/analysis）
    for tone in sort_by_specificity(tones):     # 具体 → 泛化
        if tone in EXTRACTION_TABLE:
            return EXTRACTION_TABLE[tone]         # 命中即返回该体裁策略

    # (2) tone/features 是"体裁黑洞"（实测占比最高 107/240）
    #     标签本身无法判定结构 → 回退到"段长衰减比"启发式
    if "tone/features" in tones:
        return heuristic_by_paragraph_decay(article.bodyText)

    # (3) 无 tone 标签（约 3%）→ 保守默认取前 3 段
    return take_front(3)
```

### 4.2.1 tone DROP 黑名单（整条丢弃，不是抽几段）

| tone | DROP 理由 |
| --- | --- |
| `tone/minutebyminute` | 即时直播流水，缺少稳定的起因-经过-结果叙事结构 |
| `tone/letters` | 读者来信/回信体，核心是个人意见与寒暄，不是完整公共事件 |
| `tone/competitions` | 投稿/征集/活动通知，通常不是事件叙事 |

边界：

- **section 黑名单（§3）**：结构性排除整个 section，例如 meta、功能页、地方性过强或 `travel` 低事件 section。
- **tone DROP 黑名单（本节）**：在文章层按体裁结构整条丢弃，只针对明显没有完整事件叙事结构的 tone。
- **EXTRACTION_TABLE（§4.3）**：只决定保留几段，**不再承担整条丢弃职责**。
- **热度排序 D4（§6）**：负责语义级选题价值，例如个性化随笔是否低共鸣；不得用 tone 或表层相似度冒充 D4。

### 4.3 EXTRACTION_TABLE 初始映射（可迭代）

| tone | 结构 | 策略 |
| --- | --- | --- |
| `tone/news` | 倒金字塔 | 前 5 段 |
| `tone/analysis`、`tone/comment` | 论点先行 | 前 4 段 |
| `tone/recipes` | 配料+步骤 | 仅标题 + lede（1 段） |
| `tone/reviews`、`tone/interview` | 平铺论述 | 前 3 段 |
| `tone/features` | 不定 | → 段长衰减启发式（见 4.2） |
| （无 / 未知） | — | 前 3 段（保守默认） |

> 表格是**初始猜测**，允许随实测迭代。工程上以数据表驱动（DSL 化查表），新增体裁只加行不改逻辑。

### 4.4 灵魂红线：绝不用表层相似度筛选

> **严禁**用"新闻原文表层文本相似度"做任何预筛 / 打分 / 排序。

下游召回用 MiniLM（paraphrase 模型）从电影 overview 召回——它**不做隐喻跳跃**。若在新闻侧加"新闻原文 → embedding → 预检"，测的是**表层话题相似度**，与项目"深层共振、非字面联想"的灵魂**直接冲突**。格式感知抽取只改**每条的正文质量**；tone DROP 只按体裁结构排除缺少完整事件叙事的少数类型。二者都不得引入任何相似度判断或语义价值打分。

### 4.5 边界澄清：抽取 ≠ 条数控制；DROP 是独立结构闸门

格式感知抽取改变的是**单条新闻的描述质量**；它本身**不改变**流入 agents 的**新闻条数**。tone DROP 是新增的文章层结构闸门，只丢弃 `minutebyminute` / `letters` / `competitions` 这类无完整事件叙事结构的条目。其余条数仍由 `page-size / min_body_len / 去重 / --limit` 控制（不同的管线位置）。两者不要混淆。

---

## 5. 决策 D · 自动化边界：新闻侧全自动

### 5.1 硬约束

> **新闻侧全自动，流程中段禁止人工审核新闻。** 人工唯一介入点在**电影侧**：总编从「已召回并打好分的候选电影」里挑 1 部，或选择不发。

### 5.2 `--pick` 降级

此前 Phase5/6 把 `fetch_news --pick`（人工挑新闻）写成默认入口，与硬约束冲突，也偏离了 PRD §6 原意（"选新闻：按热度 Top1；评测期允许人工指定"）。

**本次修正**：`--pick` 从"默认入口"降级为"评测 / 调试开关"，非生产默认。这是**回归 PRD 原意**，不是新发明。

### 5.3 `--pick` 留下的成本窟窿由热度（决策 D-下）填

`--pick` 原本兼职做成本闸门（人工只挑几条，天然收敛喂给 agents 的条数）。移除后成本窟窿需由**自动机制**补上 = **热度排序取 Top-N**（下节）。热度未落地前，初期接受全量高成本跑通（见 §6）。

---

## 6. 决策 E · 热度排序（核心选题机制，Post-MVP）

### 6.1 定位

产品核心 = "给**最热**的几条新闻找共振电影"。只有热新闻才有读者。因此热度排序是**核心选题机制**，不是可选项。

### 6.2 为什么本 Phase 不做

Guardian API 无热度维度（§2.2）→ 必须自研。PRD §6 已规划思路："多源同事件计数 + 时间近端加权"。此机制是 **Post-MVP**，**本 Phase 5.4 挂起不做**（用户已确认：先挂起）。

### 6.3 落地后的三重职责

| 职责 | 作用 |
| --- | --- |
| 产品 | 只推最热选题，保证读者相关性 |
| 开发 | 取 Top-N 即"小快灵"快速迭代 |
| 成本 | 天然收敛喂给 agents 的条数 |

---

## 7. 成本与开发期节流（背景，非本 Phase 交付）

### 7.1 单条成本画像

单条新闻走完整链路 ≈ **46 次 LLM 调用**（走到 C1 审核稿；若最终 pick 再出 C2 定稿则 47 次）。两大成本头：

- 12 persona × 2 步 = **24 次**
- judge 逐候选打分 ≈ **19 次**（默认 thinking 模式）——这是与 persona **几乎同量级的隐藏成本头**，未来压成本时 judge 和 persona 同等重要。

每日全量 20–25 条 ≈ 920–1150 次调用/天。**初期接受此成本**先跑通（用户价值观：人力最贵，先牺牲钱/时间换端到端可用）。

### 7.2 "小快灵"是开发者工具（与产品语义无关）

迭代慢有两层根因：①新闻条数多（`--limit` 可解）；②单条内部 46 次**串行** LLM 调用（即使只跑 1 条仍慢）。

潜在开发开关（**本 Phase 只登记方向，不实现**）：`--limit`（砍条数）、`--personas N`（只跑少数 persona）、`--judge-topk`（限 judge 候选数）、persona 并行化、上游产物缓存（复用 extract/expand 结果）。这些属**开发者体验**，不改产品语义。

---

## 8. 本 Phase 5.4 交付边界

| 交付 | 状态 |
| --- | --- |
| Guardian API 设为默认源（决策 A） | ✅ 本 Phase |
| section 宽进黑名单制（决策 B） | ✅ 本 Phase |
| tone 驱动格式感知抽取 + 多 tone / 无 tone 回退（决策 C） | ✅ 本 Phase |
| `--pick` 降级为调试开关，新闻侧全自动（决策 D） | ✅ 本 Phase |
| 扩展 `tests/test_fetch_news.py` 覆盖上述 | ✅ 本 Phase |
| 更新 Phase5 计划 5.4 定义 | ✅ 本 Phase |
| 热度排序（决策 E） | ⏸ 挂起（Post-MVP） |
| 小快灵开发开关（§7.2） | ⏸ 仅登记方向 |
| judge 分布校准（原 plan 5.4） | ⏸ 分布未定，挂起 |