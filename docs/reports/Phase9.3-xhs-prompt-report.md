# Phase 9.3 · 新建 compose_publish_xiaohongshu.md — 交付报告

## 改动范围（Scope）

- 新增 `prompts/compose_publish_xiaohongshu.md`（小红书平台专用 C2 创作 prompt）。
- `prompts/compose_publish.md`：**本 todo 未改**（仍是活跃 loader 指向的文件）；其去留在 9.4 切 loader 时一并处理（见下）。

**分支继承**：`feat/phase9.3-xhs-prompt` 从 `feat/phase9.2-projection-country` 检出（9.2 未合并、PR #109）。链：9.1→9.2→9.3。

## 技术实现（Implementation）

以现 `compose_publish.md` 为基线，按 ADR-0015 D1–D6 重写为小红书版：

- **保留（ADR-0013 调性）**：平视身份、不排名/不盖章/数字文字化/不回显结构/不编造/禁内部术语；引用 ADR-0013。
- **D2 必含元素清单**替代「内容结构 1/2/3/4」：必含（新闻侧具体 / 关系侧 / 电影侧＝导演〔必含若可得〕＋上映年〔仅年份〕＋剧情）；可选（制作国家 / 市场反馈 / 热度vs评价 / 编剧主演片长自然带过）；顺序 / 篇幅 / 融合自由、克制简短。
- **D3 归属行**：正文首段第一行 `「片名」(YYYY) 导演名`，显式要求用直角引号「」而非《》（否则被 `clean_publish_body` 剥除），导演 DB 原文无「导演」前缀、缺则退化 `「片名」(YYYY)`。
- **D4 headline**：新增标题产物 + **sentinel 分隔契约** `【标题】…` / `【正文】…`（sentinel 由 9.4 代码剥离，不入成品）；标题守底线（不推荐/煽动、不剧透、不排名、不裸片名）。
- **D5 关系侧**：忠于 judge causal_test/rationale，改写读者语言，不暴露评审来源、不出现内部术语。
- **D6 来源纪律**：一切事实仅来自三个输入块，禁外部检索。
- **正/反例改造**：正例打乱顺序（新闻先于剧情、归属行独立成行「」、国家顺势提及），并显式标注「顺序自由」；反例补「漏归属行」「headline 裸片名/煽动」「固定三段式模板」。

placeholder 保持 `{{news_context}}` / `{{selected_movie}}` / `{{judge_kernel}}`，与 `render_c2_prompt`（平台无关）兼容。

## 本地验证结果（Verification）

内容契约自动检查（9 项全 OK）：三个 placeholder 均在；`【标题】`/`【正文】` sentinel 均在；归属行「片名」(YYYY) 导演名 在；无 `## 内容结构` 编号骨架；引用 ADR-0015 与 ADR-0013。

- prompt 无「内容结构 1/2/3/4」式顺序模板，必含元素以清单表达。✅
- 明确归属行「」格式与 headline sentinel 输出分隔契约。✅
- 正/反例不再暗示固定段序（正例显式声明「顺序自由」，反例列「固定三段式模板」为禁例）。✅

## 潜在影响或技术债（Technical Debt & Caveats）

- **旧 `compose_publish.md` 去留（交代）**：本 todo 只新增文件、未切 loader，故旧文件仍活跃、暂留。9.4 会把 `load_c2_template` 改为按 `compose_publish_{platform}.md` 选取（默认 xiaohongshu），届时旧 `compose_publish.md` 成为死文件，将在 9.4 删除（并在 9.4 报告交代）。
- **sentinel 脆弱性**：`【标题】`/`【正文】` 分隔比「首行即标题」稳，但仍依赖 LLM 守约。9.4 需实现解析兜底（body 为空 → 判失败，不静默出半稿）。
- **归属行「」易被误剥**：`_TITLE_LINE_RE` 只匹配《》(年)，prompt 已显式要求「」；9.5 需保证 clean 逻辑保留「」归属行——双向对齐点。
- **prompt 措辞后续可迭代**（沿用 Phase 4 纪律，prompt 措辞与代码 PR 分开）；headline 边界先试后调（ADR-0015 D4）。
