# 发布稿平台化与元素化：C2-小红书首发、从「规定结构」转向「必含元素 + 创作标题」

**Status**: accepted（决策拍板于 2026-07-07；物理落地随后续 plan 实施）

> **本 ADR 的性质**：创作环节的产物形态与结构契约治理。它承接 [ADR-0012](0012-compose-responsibility-split-and-db-fullcolumn-lookup.md)（把发布稿认定为唯一创作环节、DB 全列经通路 B 开放）与 [ADR-0013](0013-image-equality-creative-tone.md)（影像平权调性契约），在**不改算法口径**（双轴 judge / fragment ladder，见 [ADR-0009](0009-fragment-ladder-and-search-unit-architecture.md)、[ADR-0007](0007-logic-resonance-judge-prescreen-and-pov-focalization.md)）的前提下，重定义发布稿这一环节**产出什么、怎么组织**。调性口径全部沿用 0013，本 ADR 只在标题（headline）上开一处受约束的例外。

## 背景

[ADR-0012](0012-compose-responsibility-split-and-db-fullcolumn-lookup.md) D1 把发布稿收敛为「唯一创作环节」，并声明「本阶段暂不做平台变体：发布稿先产单一版本，平台分叉维持后移」。[ADR-0013](0013-image-equality-creative-tone.md) 落地了平视调性。基于二者产出的现行 `compose_publish.md` 跑通了完整流程（样例见 `output/daily_batch/2026-07-06/…_copy.md`，选定电影 Rule Breakers），复盘暴露三个问题：

1. **过度规定格式**：prompt 用「内容结构 1/2/3/4 + 正例」把行文写成了可填空的固定模板，LLM 据此产出僵化的「剧情→接受度→共振钩子」三段式。实际诉求是「点到该点的元素即可，行文顺序 / 格式无所谓」。
2. **必含元素缺位**：现行 prompt 把 director / 上映时间列为「可选，有则用无则省」，导致成稿**通篇不提任何主创**；「新闻侧」也从未被列为必含元素，只隐含在共振钩子里，具体度不足。
3. **平台变体已到落地时机**：0012「暂不做平台变体」是过渡态声明；小红书作为首个投放平台，需要一个平台专属的创作产物——尤其是**创作型标题**（小红书笔记标题），这是现行「不生成标题行」契约未覆盖的新创作元素。

同时确认了数据可得性（通路 B / `cleaned.csv`）：`director`、`release_date`、`production_countries` 对真实选定电影**均已填充**；`production_countries` 尚未进 `compose` 的投影白名单。

## 决策

### D1 · 发布稿「平台化」：每平台一个创作步骤，小红书首发（C2-小红书）

修订 [ADR-0012](0012-compose-responsibility-split-and-db-fullcolumn-lookup.md) D1「暂不做平台变体 / 单一版本」：发布稿从「平台中性单版」改为**每个投放平台一个创作步骤**，**小红书为首个**落地平台。

- **命名与通路**：新增平台维度参数 `--platform`（`compose.py --stage publish --platform xiaohongshu`），按平台选提示词；提示词文件 `prompts/compose_publish.md` → `prompts/compose_publish_xiaohongshu.md`。**stage 名不变**（仍是 `publish`）——未来加 X / Discord 只是多一个平台枚举值 + 一份 prompt，代码骨架不动。
- **定位**：小红书是第一个平台创作步骤，架构留口子、本次只建小红书。0012/0013 中「唯一创作环节 / 平台中性单版」的表述据此更新为「每平台一个创作步骤，共享同一份 0013 调性契约」。

### D2 · 正文契约从「规定结构」转向「必含元素清单 + 自由编排」

废除「内容结构 1/2/3/4」式的顺序化模板。正文只规定**必须点到哪些元素**，不规定顺序、篇幅、融合方式：

- **必含三类**（顺序 / 篇幅 / 揉法自由）：
  - **新闻侧**：一两句**具体**描述这条新闻（允许带新闻本身的专名 / 数字 / 事实——数字护栏只约束电影指标，不误伤新闻事实）。
  - **关系侧**：电影与新闻之间的联系（口径见 D5）。
  - **电影侧**：导演（**必含若可得**）＋ 上映年份 ＋ 剧情简述。
- **可选（值得才提，不硬凑）**：制作国家、市场反馈、热度 vs 评价。
- **唯一固定位**：D3 的归属行置于正文首段第一行；其余元素一律自由编排。
- **篇幅**：不限段数，但整体克制简短，贴合小红书阅读习惯（取代旧「2–4 段」硬约束）。
- **可选主创字段**：编剧 / 主演 / 片长等不设必含，允许自然带过、不刻意，不编造、不写「待补」。

### D3 · 电影真名以「归属行」承载：`「片名」(YYYY) 导演名`

电影字面标题不再交由下游拼接的机械标题行承载，而是落进正文本身：

- **位置**：正文**首段第一行**，独立成行。
- **格式**：`「片名」(YYYY) 导演名`，例：`「Rule Breakers」(2025) Bill Guttentag`。
  - 用**直角引号「」**，**不用书名号《》**——后者会被下游 `clean_publish_body`（[scripts/compose.py](../../scripts/compose.py)）当标题行剥除。
  - 导演名用 **DB 原文**，不硬译、不编造；**无「导演」前缀标签**（避免像字段堆砌）。
  - 导演缺失时该行退化为 `「片名」(YYYY)`（导演＝必含若可得）。
- 该行一次承载「片名 / 上映年 / 导演」三个必含项；片名 / 年 / 导演也**可在正文他处自然再现**。
- **下游随之调整**：不再向正文另拼一行 `《片名》(年份)` 标题（避免与归属行重复）；`clean_publish_body` 继续剥除 LLM 误吐的 `《片名》(年份)` 行与裸链接，但**保留** `「片名」(YYYY)` 归属行。

### D4 · 新增创作产物「小红书标题」（headline）

发布稿新增第二个创作产物：一句**描述电影且勾住新闻**的创作型标题（例：Rule Breakers →「逆风而行的她们」）。

- **本质**：它是「关系侧」的创作化压缩，由唯一创作环节铸造，不由下游拼接。
- **调性边界**（对 0013 的**受约束例外**）：可以比正文更凝练、更有画面 / 悬念；但仍守 0013 底线——**不用推荐 / 煽动词**（不容错过 / 催泪 / 必看）、**不剧透结局**、**不排名 / 不吹捧**、**不裸露字面片名**（片名由 D3 归属行承载）。
- **迭代姿态**：先按此边界试用，看真实产出再收紧 / 放松（本决策不追求一次到位）。
- **产物契约**：`run_publish` 返回结构从 `{tmdb_id, body}` 扩为 `{tmdb_id, headline, body}`；下游 `_copy.md` 渲染与各平台适配消费该字段。

### D5 · 关系侧忠于上游因果线，但不暴露评审来源

关系侧的**实质**取自上游 judge 已结构化存在的 `causal_test` / `rationale`（承接 [ADR-0012](0012-compose-responsibility-split-and-db-fullcolumn-lookup.md) D1「两环节向上游消费内核」），忠于那条因果线，不让创作环节另编一个「电影映照现实」式的镜像。

- 但**必须改写成读者语言**，**不暴露**它来自任何评审 / 打分环节，不出现内部术语（judge / resonance_type / causal_test / rationale 等）。
- 共振写法沿用 0013：电影与新闻**并置**、同记一种人类处境，时间维度可选。

### D6 · 来源纪律 + 制作国家经通路 B 加列

- **只用给定输入**：正文与标题的一切事实只能来自本环节的三个输入块（news_context / selected_movie / judge_kernel），**禁止外部检索或凭记忆补充**。
- **制作国家**：经 [ADR-0012](0012-compose-responsibility-split-and-db-fullcolumn-lookup.md) D3 通路 B「加列穿透」，把 `production_countries` 纳入 `compose` 的 DB 投影白名单（`_DB_PROJECTION_FIELDS`）。该白名单为 C1 决策卡与 C2 发布稿共用，故 C1 决策卡也会多出此列——无害透传。
- **数字文字化护栏不放松**（0013）：电影的评分 / 票数 / 热度 / 来源平台名仍不裸露、不用数据举证；只作定性判断依据。

## 为什么

1. **「元素」比「结构」更贴合诉求**：读者要的是信息点到位，不是固定骨架；规定元素、放开编排，既保证必含项不漏，又消除模板僵化。
2. **归属行一举三得**：`「片名」(YYYY) 导演名` 用一行自然承载三个必含项，避免把主创 / 年份写成字段堆砌，也把「电影真名」从下游机械拼接收回到唯一创作环节，口径更集中。
3. **平台化到了非做不可的点**：小红书标题是平台专属的创作元素，平台中性单版无法承载；用 `--platform` + per-platform prompt，落地首平台的同时把扩展成本压到「加一份 prompt」。
4. **调性不重造**：正文继续单一引用 0013；headline 只开一处**明确受约束**的例外，防止调性跨环节漂移。

## 后果 / 已知局限

- **修订 0012 / 推进 0013**：本 ADR 修订 [ADR-0012](0012-compose-responsibility-split-and-db-fullcolumn-lookup.md) D1「暂不做平台变体」；兑现 [ADR-0013](0013-image-equality-creative-tone.md) D3「未来各平台变体引用同一调性清单」——小红书为首个引用者，其正文受 0013 全约束，headline 受 D4 例外约束。
- **代码落地面**（随后续 plan 实施，非本 ADR 工单）：
  - `compose.py` 加 `--platform`、按平台选 prompt；prompt 文件改名为 `compose_publish_xiaohongshu.md`。
  - `_DB_PROJECTION_FIELDS` 增 `production_countries`（C1/C2 共用，副作用为决策卡多一列）。
  - `run_publish` 返回结构扩为 `{tmdb_id, headline, body}`；解析需从产出中分离 headline 与正文。
  - 下游 `review_panel/publish_adapter.py` 的 `_copy.md` 渲染消费 headline；不再另拼 `《片名》(年份)` 标题行；`clean_publish_body` 保留 `「片名」(YYYY)` 归属行。
- **必含若可得＝静默降级**：DB 缺导演时正文静默省略该项，且无法区分「模型漏写」与「数据缺失」；**本期不加校验**（避免过度工程），列为已知缺口，日后需要再补 warning。
- **测试与 SSOT 同步**：`tests/test_compose_publish.py` / `tests/test_compose_decision_card.py` 等需随契约与投影字段变更过绿；`news-to-film-pipeline.md` 的 compose 段在落地时同步平台化描述。
- **不属于本 ADR**：`review_panel` 「改选不清旧稿」的生命周期缺陷（改选后遗留陈旧 `_copy.md`）是 bug 修复（`handle_select` 改选时删旧 copy），单独走工单，不进本决策记录。
