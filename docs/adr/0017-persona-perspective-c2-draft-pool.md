# persona 视角 C2 草稿池：多视角扇出 + 总编指针选择（推翻 0016 D4 二档约束）

**Status**: accepted（决策拍板于 Phase 10 Round1–6 需求讨论；物理落地随 Phase 10 各 TODO 分批实施，A/B 合并路线选型冻结于 10.7 GATE）

> **本 ADR 的性质**：C2 定稿链路的**上游视角来源治理**。它承接 [ADR-0013](0013-image-equality-creative-tone.md)（影像平权调性）、[ADR-0015](0015-publish-platformization-and-element-checklist.md)（平台化 + 元素清单 + headline）与 [ADR-0016](0016-panel-editorial-regeneration-and-inline-edit.md)（面板定点重生成 + 正文编辑），**显式推翻 0016 D4「原版 / 去AI化版二档、不加版本层」约束**：在其上加一层**只读草稿池**作为上游来源层，并把「选中」重新定义为**可变指针派生**，而非搬运 / 消费。

## 背景

Phase 9 系列把 C2 做成了平台化定稿 + 面板（headline/body 重生成、正文编辑、去AI化）。但 Round1 数据流追踪确认了一个架构缺口：**上游 persona 视角从未进入 C2**。

```
现状 C2 输入（scripts/compose.py · run_publish）：
    news_context      ← news.json（标题/摘要/链接）
    selected_movie    ← retrieve.json candidate（TMDB DB 投影）
    judge_kernel      ← llm-judge-scores.json（judge rationale / causal_test）
    headline_contract ← _shared/xiaohongshu_headline_contract.md
    persona           ← ✗ 从不传入
```

后果：样例稿里那种「视角感」实为 **judge rationale 的回声**——prompt 还要求把它改写得不像来自 review 阶段，persona 的「共鸣视角」名存实亡。

而 fan-out 的**数据来源已就绪**、无需新采集：`retrieve.json` 每个候选自带 `candidates[].triggered_by`（命中该片的 persona 全集，本例 9 个），`build_data.py` 已据此算 `resonance_agents`。

## 决策

### D0 · 澄清确认（Round4–6 需求讨论）

| # | 决策 | 取值 |
| - | ---- | ---- |
| 1 | 二档约束（ADR-0016 D4） | **推翻**——允许在「当前稿 / 去AI化版」之上加一层**只读草稿池** |
| 2 | 扇出数量 | **全量、无上限**——推文短、成本低；不做「选 N 个 persona」的算法猜测 |
| 3 | 是否带 persona card | **带，但蒸馏**——绝不原样注入行话 card，须先蒸馏为中文视角指引 |
| 4 | 人性化时机 | **延后**——草稿池是「正稿池」；总编选定一版后不满 AI 味再跑去AI化 |
| 5 | 复数视角合并 | **上限 2**；A/B 两路线都实现，`--combine-mode both` 仅开发期离线对照选型，生产只走选定单版 |
| 6 | 选中语义 | **可变指针，非搬运**——草稿池永不被消费 / 删除；改指针即改当前稿 |

### D1 · persona 视角蒸馏：c2_perspective.md（中文、去行话）·【本 Phase 最大质量前提】

- **问题**：`prompts/personas/{Persona}/persona_card.md` 面向 pseudo / 检索侧，满是内部行话（decon / P-Select / objective-floor neutral / focalized / fit / Who 正极负极 / alt-creator lens）。直接注入 C2 会**污染中文创作、泄露内部术语**，是质量事故。
- **方案**：每个 persona 新增 `prompts/personas/{Persona}/c2_perspective.md`——把 card 的**创作可用内核**（核心情感、价值倾向、看待事件的镜头方向）蒸馏成**几句中文视角指引**，只讲「用什么眼光看这条新闻 + 这部电影」，**不含任何术语**。与 `persona_card.md` 同目录共置。
- **单一事实源分层**：`c2_perspective.md` 是 **C2 侧** persona 视角的 SSOT；`persona_card.md` 仍是**检索侧**的 SSOT。两者各司其职、不混用——C2 加载路径**只认 c2_perspective.md，永不读 persona_card.md**。
- **可辨识性是硬验收**：12 份蒸馏视角必须**互相可区分**（10.7 GATE 逐份人读确认）；若蒸馏同质，扇出 N 版即失去意义。

### D2 · C2 注入点：run_publish 加 persona_perspective 参数（sentinel 占位符 + no-op 向后兼容）

- `render_c2_prompt` 加 `{{persona_perspective}}` 占位符——**完全复刻 `{{headline_contract}}` 的 no-op 模式**：模板无此占位符或传空串时 `replace` 为 no-op，渲染结果与注入前一致（golden-snapshot 兜底）。
- `run_publish(..., persona_perspective: str = "")`：空串 = 现有行为（首发 publish / 9.8 重生成路径**零回归**）。
- `compose_publish_xiaohongshu.md` 增「本条创作的主视角」段注入 `{{persona_perspective}}`，并写清与 judge 的分工：**persona 视角是「用什么眼光写」，judge 是「为什么共振」**，两者互补、不冲突、不替代；视角**绝不覆盖**去实体化 / 平视不排名 / 数字文字化 / 来源纪律等硬规则。
- **归一化**：`triggered_by` 是 `THE-SAGE` 大写连字符，persona 目录是 `The-Sage` 首字母大写；`load_persona_perspective` 内做 `THE-SAGE → The-Sage` 归一化（title-case per hyphen 段），缺文件 → 清晰报错。

### D3 · 草稿池 = 持久只读来源层（append-only，永不 mutate / 消费）

- 文件 `{slug}_drafts_{platform}.json` = 数组 `[{draft_id, headline, body}]`，`draft_id` = persona（如 `The-Sage`）或合并稿的 `The-Sage+The-Explorer`。
- **一次生成、只读**：`/api/generate-drafts` 全量扇出写一次；「选中」**不消费、不删除、不移动**任何草稿。
- **重新扇出 = 整份覆盖**（显式再生成动作，等价重掷全部 persona）；合并稿 append 进池。
- 总编改主意时可回看其它草稿、改指针——这正是「草稿池不可丢弃」的动机。

### D4 · 选中 = 可变指针 selected_draft_id（派生当前稿，非搬运）

- `selection.json` 的平台 copies 条目加 `selected_draft_id` 字段（可变指针；旧条目无此字段视为 `None`，向后兼容）。
- `/api/select-draft`：把指针指向的池内草稿经 `render_copy_markdown` **派生**为 `{slug}_copy_{platform}.md`（当前稿），并**失效 humanized**（body 变 ⇒ 旧去AI化稿过期，删 `_humanized.md` + 清 `humanized_path`，复用 9.8 D4 / 9.1 stale 清理不变量）。
- **层级清单（不是版本层爆炸）**：`只读草稿池（N 版来源）→ 当前稿（唯一可编辑）→ 去AI化版（当前稿派生旁支）`。9.8 的正文编辑 / 标题重生成 / 去AI化**全部只作用于「当前稿」**，语义不变——草稿池纯上游、不可编辑。

### D5 · 复数视角合并（上限 2）· 开发期 A/B 对照，生产期单版

**核心区分：A/B 双版只是「开发 / 评测期的选型对照」，不是生产形态。**

- **两条路线都实现**（供选型）：
  - **路线 A（重跑 C2 合并视角）**：把 ≤2 份蒸馏视角拼成一个复合 `persona_perspective` 再跑一次 `run_publish`——同一条创作管线，出稿浑然一体但多花一次 LLM 调用。
  - **路线 B（文本融合既有草稿）**：拿池内两份既有 body 做文本融合纯函数——不重跑、省一次调用，但接缝与调性一致性存疑。
- **`--combine-mode {A|B|both}` 开关控制产出**：
  - `both`（**仅 GATE 离线用**）：一次产 `a+b#A` + `a+b#B` 两版 append 进池，供肉眼并列对比、二选一。
  - `A` / `B`（**生产默认**）：只产选中那一版，`draft_id = "a+b"`（无 `#A/#B` 后缀）。
- **选型冻结即生产纪律**：GATE 选定后把中选路线设为 `--combine-mode` 生产默认；`/api/combine-drafts` **恒调单版**（不带 `both`）。面板 / serve / 生产链路**永不产双版**——A/B 对照的复杂度全部留在开发期 CLI，不外泄到 UI 与产物。

#### 10.7 GATE 选型冻结结论（2026-07-06 真实批次实测）

**冻结：路线 A（重跑 C2 合并视角）为生产默认。**

- **对照材料**：对候选 `02-learning-another-language-appears-to-slow`（tmdb 355196）离线跑 `--combine The-Sage,The-Outlaw --combine-mode both`，产 `The-Sage+The-Outlaw#A`（路线 A）/ `#B`（路线 B）两版肉眼对比。
- **判定**：路线 A 出稿单篇浑然一体、篇幅适配小红书、Sage 理性辨识与 Outlaw 抗争坠落两种镜头真正交织；路线 B（文本拼接）出现**电影名重复 2 次、开头「今天…研究」重复、关键数据重复陈述、篇幅近乎翻倍**，实证了 D5 对路线 B「接缝与调性一致性存疑」的先验判断。路线 B 唯一优势（省 1 次 LLM 调用）不足以抵偿其质量缺陷。
- **零代码改动即冻结**：`drafts_adapter._build_parser()` 的 `--combine-mode` argparse 默认本就是 `"A"`，且 `serve.handle_combine_drafts` 的 subprocess 命令**不传 `--combine-mode`**（落 adapter 默认）。因此「路线 A = 生产默认 + serve 恒单版」在既有代码里已然成立，冻结 = 记录，无需改动。
- **复跑实证**：清理对照稿后以生产模式（不传 `--combine-mode`）复跑，池仅 append 一条 `The-Sage+The-Outlaw`（**无 `#` 后缀**），确认双版逻辑不外泄生产。

### D6 · 后端 / adapter 形态（沿用 9.8 既有约定）

- 新 `review_panel/drafts_adapter.py`：与 publish / rewrite / regenerate adapter **同层**，唯一 import `scripts.compose` 之一；复用 publish_adapter 的 `locate_news_dir / load_news / find_candidate / load_judge_entry / render_copy_markdown`；stderr 打 `Wrote <path>` 供 serve 解析；`run_publish` / `load_persona_perspective` 可注入（测试 stub 免真调 LLM）。
- `POST /api/generate-drafts` → subprocess 扇出；`POST /api/select-draft` → 派生当前稿（**无 LLM**，serve 直接读池 + render + 失效 humanized）；`POST /api/combine-drafts` → subprocess `--combine`（恒单版）。
- slug / tmdb_id 缺省时从 selection.json 兜底；复用 `_parse_wrote_path` / `_delete_copy_if_exists`。

### D7 · 本 ADR 的记录范围

本 ADR 记录 D1–D6 的决策与理由；物理落地随 Phase 10 各 TODO（10.1–10.7）分批实施并各自过 pytest / GATE。A/B 合并路线的**最终生产选型冻结于 10.7 GATE**，冻结结果写入本 ADR 与 10.7 交付报告。本 ADR 不重复各 TODO 的实现细节，只固化跨 TODO 的架构约束。

## 为什么

1. **推翻 0016 D4 是有边界的**：0016 D4 立「原版 / 去AI化版二档、不加版本层」是为了防 UI 复杂度爆炸。本 Phase 新增的**只读草稿池不是「第三种可编辑版本」**——它是**上游只读来源层**，唯一可编辑稿仍是「当前稿」，去AI化仍是当前稿的派生旁支。层级从「当前稿 → 去AI化」变为「只读草稿池 → 当前稿 → 去AI化」，可编辑面并未变宽，故不违背 0016 D4 的**本意**（防可编辑版本爆炸），只推翻其**字面**（严格二档）。
2. **视角必须蒸馏、不能直灌**：persona_card 是检索侧资产，行话密度高；直接注入 C2 既污染中文创作又泄露内部术语。蒸馏为 c2_perspective 把「检索侧 SSOT」与「C2 侧 SSOT」彻底分层，是本 Phase 的最大质量前提。
3. **指针而非搬运**：若「选中」= 把草稿搬进当前稿并从池中消费，总编就无法反悔 / 回看其它视角。可变指针让草稿池成为**可反复回看的只读来源**，选择成本趋近于零，契合「人类总编用眼睛挑」的 MVP 纪律。
4. **A/B 只在开发期对照**：两条合并路线的取舍（重跑保调性一致 vs 文本融合省调用）无法先验判定，须靠真实稿肉眼比。但把双版逻辑带进生产会让面板 / 产物复杂度翻倍——故 `both` 严格限定在开发期 CLI，GATE 选定后冻结为单版生产默认。

## 后果 / 已知局限

- **修订面**：**显式推翻 ADR-0016 D4** 的「严格二档」字面约束（见上「为什么」§1 的边界说明）；ADR-0016 其余决策（D1–D3、D5–D6）不受影响。
- **`render_c2_prompt` / `run_publish` 签名变化**：新增可选参数 `persona_perspective: str = ""`，默认值保证首发 publish / 9.8 重生成路径**零回归**（golden-snapshot + 既有测试兜底）。
- **`_humanized.md` 失效不变量再扩面**：改指针（select-draft）成为**第四条**改动 body 的路径（前三条：重生成正文 / 编辑正文 / 改选片），同样必须删 `_humanized.md` 并清 `humanized_path`。
- **成本**：全量扇出 = `triggered_by` 数次 LLM 调用（本例 9 次 / 候选）；用户已确认可接受（推文短、成本低）。
- **平台范围**：仅 xiaohongshu；X / Reddit 仍灰置。**人类总编不可替代**：仍全手动、无自动甄选 / 自动发布——扇出只是「把 N 版摆出来给总编用眼睛挑」。
- **测试与 SSOT 同步**：`tests/test_compose_publish.py` / `test_review_panel_drafts_adapter.py` / `test_review_panel_serve.py` 覆盖新链路；`docs/SSOT/...` compose 段与 PRD 将在 10.7 GATE（Go 后）同步引用本 ADR。
- **不属于本 ADR**：`load_persona_perspective` / `drafts_adapter` / serve 端点 / 前端交互的具体实现细节记录在各 TODO 的交付报告（`docs/reports/Phase10.*-report.md`）。