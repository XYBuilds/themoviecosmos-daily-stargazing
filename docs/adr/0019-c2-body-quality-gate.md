# C2 正文质量闸门：唯一创作环节引入检测器 + 命中带反馈重试 + 不硬失败降级

**Status**: accepted（决策拍板于 Phase 12 需求讨论；物理落地随 Phase 12 各 TODO 分批实施——句式红线 / 幻觉判据 / 编排接入分别落 12.2 / 12.3 / 12.4，最终眼验冻结于 12.5 GATE）

> **本 ADR 的性质**：C2 唯一创作环节的**正文产出质量校验治理**。它承接 [ADR-0012](0012-compose-responsibility-split-and-db-fullcolumn-lookup.md)（发布稿 = 唯一创作环节）、[ADR-0013](0013-image-equality-creative-tone.md)（影像平权调性契约 = 正文红线的价值源）、[ADR-0015](0015-publish-platformization-and-element-checklist.md)（必含元素清单 + headline + 来源纪律）、[ADR-0017](0017-persona-perspective-c2-draft-pool.md)（persona 视角草稿池 = 扇出来源）；并与 [ADR-0018](0018-deterministic-movie-header-projection.md) **划清边界**：0018 管**抬头行**（确定性投影、代码拼装），本 ADR 只管**正文**（LLM 创作产物）的质量校验，两者互不重叠。

## 背景

Phase 4「影像平权」（[ADR-0013](0013-image-equality-creative-tone.md)）以来，C2 正文的调性红线（平视不排名 / 去态度盖章 / 数字文字化 / 来源纪律）一直靠 **prompt 表述 + 人工眼验**维系。Phase 12 追加一轮「去 AI 腔」重塑（拆四拍骨架 / 封说破盖章 / 禁编造 overview 没有的细节 / Persona ①偏② 显形 / 放开长度 / 3–4 段扫读），把这些规则又写进了 [prompts/compose_publish_xiaohongshu.md](../../prompts/compose_publish_xiaohongshu.md)。

但真重放 05 场景（AI / 广岛 +《The Creator》，见 `output/daily_batch/2026-07-06/05-ai-poses-hiroshima-style-threat-to-humanity_drafts_xiaohongshu.json`）显示违规几乎照旧：

- 硬转场「而这部…电影」
- 说破句「无论是…还是…同一种」（结尾盖章）
- 接受度单独成句
- 语义幻觉：编造「士兵穿过战火村庄」「扣扳机前犹豫」等 overview 没有的画面
- 导演名写错（Gareth Edwards → 盖瑞斯·埃文斯）

**已试 5 版 prompt 均失败**。根因不是「prompt 不够狠」，而是：**验收标准从未算子化**——红线只存在于 prompt 表述和人的眼睛里，主观、不可复现、无法写测试、无法在链路里拦截。同样的缺口在 [ADR-0015](0015-publish-platformization-and-element-checklist.md)「必含若可得＝静默降级 / 本期不加校验，日后需要再补 warning」里已被显式记为已知技术债；本 ADR 兑现其中一部分。

## 决策

### D0 · 能力边界与红线分工（先讲清「谁抓什么」）

正文违规分两类，用两种检测手段，边界不重叠：

| 违规类 | 例子 | 检测器 | 手段 |
| --- | --- | --- | --- |
| 句式类红线 | 硬转场 / 说破盖章 / 接受度单独成句 | `body_lint` | 确定性正则 |
| 语义幻觉 | overview 没有的画面 / 人物 / 数字 / 写错导演名 | `judge_body_fabrication` | LLM-judge |

`body_lint` **抓不住语义幻觉**（正则不懂语义）；LLM-judge **不承担句式红线**（确定性正则更稳更省）。两者互补、缺一漏网。

**两者都是「检测器（detector）」，不做编排**：只返回违规清单，不改文本、不决定是否重试。编排（拼反馈、重跑、降级）由 D3 的 `run_publish` 独立承担。这是本 ADR 最容易被后续 TODO 侵蚀的边界——把重试逻辑塞进检测器会让职责糊掉、可测性崩塌。

### D1 · body_lint = 纯函数 + DSL 红线表（复刻 render_movie_header 的 FP 哲学）

- 新增 [scripts/lib/body_lint.py](../../scripts/lib/body_lint.py)：一张模块级 `RULES` 表 `list[(rule_id, pattern, description)]` + 一个 `scan(body: str) -> list[Violation]` 纯函数。
- `scan` **只检测、不改文本、不调 LLM、零 IO**——与 [ADR-0018](0018-deterministic-movie-header-projection.md) D4 `render_movie_header` 同哲学：纯函数 → 每条红线正 / 反例单测锁死。
- 红线以 **DSL 声明式**组织：新增 / 调整红线 = 改 `RULES` 表一行，**不动 `scan` 逻辑**。`Violation` 携带 `rule_id` + 命中片段，供 D3 拼反馈。
- 初版覆盖：硬转场「而这部…电影」、说破句「(都|背后是)…(同一种|同一个)…」「无论是…还是…」、接受度单独成句。新违规样式后续往表里加行扩展。

### D2 · judge_body_fabrication = LLM-judge（overview 当唯一真值，llm_call 可注入）

- 新增纯函数 `judge_body_fabrication(body, overview, *, llm_call) -> list[Finding]` + 配套 prompt。
- **真值源**：拿 `selected_movie` 块里的 DB `overview` 当「剧情简述」唯一授权来源（沿用 [ADR-0015](0015-publish-platformization-and-element-checklist.md) D6 来源纪律），判定 body 是否出现 overview 没写的电影细节 / 写错的导演名。
- `llm_call` **依赖注入**（复刻 [ADR-0017](0017-persona-perspective-c2-draft-pool.md) D6「run_publish / load_persona_perspective 可注入」的可测性约定）：默认走项目 LLM 客户端，单测传 stub 免真联网。与 body_lint 同为检测器，不做编排。

### D3 · 命中即带反馈重试编排（复刻 rewrite.py 的 repair_context 模式，上限 K）

- 在 [scripts/compose.py](../../scripts/compose.py) `run_publish` 的 `clean_publish_body` 之后接闸门：跑 `body_lint.scan` + `judge_body_fabrication`；命中则把「违反哪几条 + 原文片段」拼成 `repair_context` 喂回 LLM 重生成。
- **复刻既有先例**：[scripts/rewrite.py](../../scripts/rewrite.py) `run_screenwriter` 已有「parse 失败 → 喂错误 → 重跑，上限 2 次」的 `repair_context` 带反馈重试模式。本 ADR 直接复用这套范式，不发明新机制。
- K 设小值（建议 1–2）。**成本**：[review_panel/drafts_adapter.py](../../review_panel/drafts_adapter.py) `run_fanout` 扇出 N 个 persona，接入后 LLM 调用量约 `N ×（1 创作 + 1 judge + 至多 K 次重试）`——K 必须小，否则扇出成本线性放大。
- 闸门接在 `run_publish` **内** = 扇出的每一版 persona 草稿都自动过闸，无需在 adapter 层重复接线。

### D4 · 不硬失败：重试耗尽保留最后一版 + 挂 warnings

- 重试 K 次仍违规 → **保留最后一版正文**，在 draft 里挂 `warnings`（记录剩余违规 `rule_id` / judge findings），**不硬失败**。
- **理由与先例**：闸门是**渐进优化器不是拦截器**。正文质量硬失败会阻断整条扇出（[ADR-0017](0017-persona-perspective-c2-draft-pool.md) 全量扇出 = N 版并列给总编挑，砸一版即砸整批）。warnings 让残余问题可见、可追踪，最终由 D5 / 12.5 人工验收兜底——延续 [ADR-0015](0015-publish-platformization-and-element-checklist.md)「日后需要再补 warning」的降级姿态，且 [ADR-0013](0013-image-equality-creative-tone.md) 早已确立「人类总编不可替代」。

### D5 · 本 ADR 的记录范围

本 ADR 记录 D0–D4 的决策与理由；物理落地随 Phase 12 各 TODO 分批实施（12.2 body_lint / 12.3 judge / 12.4 编排接入 / 12.5 眼验 GATE）并各自过 pytest / GATE。本 ADR 不重复各 TODO 的实现细节，只固化跨 TODO 的架构约束（检测器不做编排 / 能力边界分工 / 不硬失败挂 warnings）。

## 为什么

1. **prompt 赌不住，必须算子化**：5 版 prompt 实证「把红线写进 prompt」既拦不住违规、也无法复现验收。把红线变成正则与判据，才有红 / 绿信号、才能写测试、才能在链路里当场拦截并反馈重试。
2. **确定性归确定性、语义归 LLM**：句式模式匹配用正则更稳、更省、可单测；语义幻觉是理解问题，只能交 LLM-judge。分工既压成本又提可靠性。
3. **复刻既有先例，不造新范式**：带反馈重试（rewrite.py）、依赖注入可测（0017 D6）、纯函数可测（0018 D4）都是项目已验证的模式，本 ADR 只是把它们组合到正文校验场景。
4. **渐进优化优于硬闸**：全量扇出下任一版硬失败都会砸掉整批草稿；渐进优化 + warnings + 人工终审，才契合 MVP「人类总编用眼睛挑」的纪律。

## 后果 / 已知局限

- **`run_publish` 内部流程延长**：`clean_publish_body` 后新增闸门 + 可能的重试循环；须保证 `llm_call` 注入路径与现有 golden-snapshot 测试**零回归**（12.4 验收项）。
- **成本随扇出线性放大**：见 D3；K 与 judge 调用是新增 LLM 开销，K 必须设小值（1–2）。
- **LLM-judge 有假阴 / 假阳**：judge 不是真值裁判，只降低人工负担；最终质量仍由 12.5 人工眼验 GATE 把关，不得以 judge 通过替代人工验收。
- **body_lint 初版红线不完备**：只覆盖已观察到的句式违规；新样式靠往 `RULES` 表加行迭代，属预期演进而非缺陷。
- **边界纪律**：本 ADR 只管**正文**，不碰 [ADR-0018](0018-deterministic-movie-header-projection.md) 已确定性投影的**抬头行**；prompt 只改正文语气契约相关段。
- **测试与 SSOT 同步**：`tests/` 新增 body_lint 正 / 反例、judge stub、run_publish 重试通过 / 耗尽两路径用例；`docs/SSOT/...` 与 PRD 的 compose 段在 12.5 GATE（Go 后）同步引用本 ADR。
- **不属于本 ADR**：`body_lint` / `judge_body_fabrication` / `run_publish` 编排的具体实现细节记录在各 TODO 的交付报告（`docs/reports/Phase12.*-report.md`）。