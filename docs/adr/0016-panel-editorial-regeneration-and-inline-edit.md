# 定稿界面定点重生成（标题/正文分离）与正文人工编辑：覆盖语义 + headline 契约 SSOT

**Status**: accepted（决策拍板于 2026-07-09；物理落地随 Phase 9.8 各 TODO 分批实施）

> **本 ADR 的性质**：定稿面板（review_panel）对成品稿的编辑能力治理。它承接 [ADR-0013](0013-image-equality-creative-tone.md)（影像平权调性契约）与 [ADR-0015](0015-publish-platformization-and-element-checklist.md)（平台化 + 元素清单 + headline 创作产物），在**不新增版本层、不改算法口径**的前提下，为总编补齐「只换正文」「只换标题（贴合当前正文）」「面板内直接编辑正文」三种定点操控。

## 背景

9.1–9.7 落地了 C2 平台化（小红书 headline + 归属行 + 必含元素）与定稿面板（展示 + 移动预览 + avoid-ai-writing 可逆 toggle）。但面板对成品稿只能「整段重跑 publish」或「整段去AI化」，总编无法：

1. 只对**正文**换一版创作（不满意就重掷，但不想连标题一起换）；
2. 只对**标题**重出一句（且要贴合当前正文，而非重新脑补一条与正文脱节的标题）；
3. 在面板内**直接微调正文**再定稿。

## 决策

### D0 · 澄清确认

| # | 决策 | 取值 |
| - | ---- | ---- |
| 1 | 「重生成正文」的语义 | **A：换一版创作**（重跑 C2 创作出新 body），非 avoid-ai-writing 去AI化 |
| 2 | headline 重生成是否 body-aware | **是**——以当前正文为输入产标题 |
| 3 | 版本模型 | **覆盖当前稿**，不新增版本层 |
| 4 | 是否支持面板内人工编辑正文 | **要**——编辑后可再重生成标题使其贴合 |

### D1 · 提示词拆分方式：monolithic 保留 + headline 契约收敛为 SSOT

- **不拆首发稿**：`compose_publish_xiaohongshu.md`（一次出 headline+body）继续作为首发 publish，逻辑不动，只省一次调用的诉求不变。
- **抽共享契约**：把 headline 的硬规则（≤10 中文字、不裸片名、不煽动 / 推荐词、不剧透、一句话、平视调性）从 monolithic 抽到 `prompts/_shared/xiaohongshu_headline_contract.md`，作为 headline 规则的**单一事实源**。
- **新增 headline 模块 prompt**：`prompts/compose_publish_xiaohongshu_headline.md`，输入 = `{{news_context}}` + `{{selected_movie}}` + `{{current_body}}`，引用共享契约，只产一句 headline（sentinel 复用 `【标题】`，无 `【正文】`）。
- **monolithic 也改引用共享契约**：通过 `render_c2_prompt` 新增的 `headline_contract` 参数注入 `{{headline_contract}}`，消除「headline 规则两处各写一份」的漂移风险。占位符缺省时 `.replace()` 为 no-op，向后兼容。
- **回归护栏**：golden-snapshot 测试断言「抽取后 monolithic 的渲染结果」不丢失任一条 headline 硬规则文本，证明动过 GATE 验过的首发 prompt 无回归。

### D2 · 正文重生成：复用 run_publish 取 body（不建独立 body prompt）

- `--target body`：复用整条 `run_publish`（含 news + selected_movie + judge 全语境）→ **只取新 body 覆盖**，丢弃这次顺带产出的新 headline（YAGNI，不为 body-only 单独建 prompt）。
- **后果与不联动约定**：新 body 可能与旧 headline 不再匹配 → **不自动重生成标题**；由总编按需再点「重生成标题」重新对齐（保持 targeted / 覆盖语义，避免隐式连锁）。

### D3 · 标题重生成：body-aware

- `--target headline`：读当前 `_copy_{platform}.md` 的 **body**（可能已被人工编辑，见 D5）→ `run_headline(current_body)` → **只覆盖 headline**，body / 链接不动。
- headline 的 body 输入取**原稿 body（`_copy_{platform}.md`）**，不取 humanized body（保持单一事实源；去AI化版是派生只读，见 D4）。

### D4 · 覆盖语义 + 与「去AI化版」的关系

- 重生成 / 编辑只改 `_copy_{platform}.md`（原稿），**不新增版本层**；面板仍只有 原版 / 去AI化版 二档。
- `_humanized.md` 是从 body 派生的旁支。**任何改动 body 的操作（重生成正文 / 人工编辑正文）都会使旧 humanized 陈旧** → **同步删除 `_humanized.md`**，回到「未去AI化」态，并清空 `selection.json` 对应 `copies.{platform}.humanized_path`（复用 9.1 stale-copy 清理思路，保「humanized_path=null ⇔ 盘上无 _humanized.md」不变量）。
- **重生成标题不动 body → 不失效 humanized**（headline 本就不参与 toggle）。

### D5 · 正文人工编辑

- 前端：定稿区正文由只读改为**可编辑 textarea + 保存**按钮（编辑态 / 展示态切换）。
- 后端 `POST /api/edit-body`：把编辑后的 body 经 `publish_adapter.render_copy_markdown` **写回原稿**（headline + 链接保持），并按 D4 失效 humanized。**无 LLM**，serve 直接写文件。
- **编辑只作用于原稿 body**；去AI化版是派生只读、不可直接编辑（要改就改原稿再重新去AI化）。

### D6 · 后端 / adapter 形态（沿用既有约定）

- 新 `review_panel/regenerate_adapter.py`：与 `publish_adapter.py` / `rewrite_adapter.py` **同层**，`--date/--slug/--platform/--target headline|body`；耦合止于 `scripts.compose` + `scripts.lib.*`；stderr 打印 `Wrote <path>` 供 serve 解析。
- `POST /api/regenerate`（body `{date, slug?, platform, target}`）→ subprocess 调 regenerate_adapter（同 `handle_publish` / `handle_rewrite` 模式）。
- `POST /api/edit-body`（`{date, slug?, platform, body}`）→ 无 LLM，serve 复用 `render_copy_markdown` 直接写回。
- 复用现有 `_parse_wrote_path` / `selection.json` copies 读写 / `_delete_copy_if_exists` 等既有工具，不重造。

### D7 · 本 ADR 的记录范围

本 ADR 记录 D1–D6 的决策与理由；物理落地随 Phase 9.8 各 TODO（9.8.1–9.8.7）分批实施并各自过 pytest/GATE。本 ADR 不重复各 TODO 的实现细节，只固化跨 TODO 的架构约束。

## 为什么

1. **不拆 monolithic 首发稿**：首发场景（headline+body 一次出）省一次 LLM 调用，且已过 GATE 验收，拆开重构风险大于收益；只抽共享契约就能同时解决「漂移」与「headline-only 重生成」两个诉求。
2. **headline 契约单一事实源**：两份 prompt 各写一份规则是典型的双份维护成本，未来任何一次调整 headline 硬规则（比如放宽字数）都要记得改两处——收敛为 `_shared` 契约 + 占位符注入，从架构上消除这个人力依赖点。
3. **覆盖而非叠版本**：面板已有「原版 / 去AI化版」二档模型，重生成再引入第三档（如「重生成版」）会显著推高 UI 复杂度且与 humanized 派生关系纠缠不清；覆盖语义把心智模型维持在「一份正稿 + 一份只读派生」。
4. **headline↔body 不自动联动**：如果重生成 body 自动带动重生成 headline，会产生隐式连锁调用与 token 浪费，且总编可能只想换正文不想动已经满意的标题；显式操作把控制权交还总编。

## 后果 / 已知局限

- **修订面**：ADR-0015 D4 的 headline 硬规则文本物理位置从 monolithic 内联迁移至 `prompts/_shared/xiaohongshu_headline_contract.md`；ADR-0015 本身的决策内容不变，只是规则的存放单一化。
- **`render_c2_prompt` 签名变化**：新增可选参数 `headline_contract: str = ""`，默认值保证旧调用点（若存在）行为不变；`run_publish` 内部改为固定加载并传入该契约。
- **正文调性仍单一引用 ADR-0013**；headline 仍是 ADR-0015 D4 定义的「受约束例外」，本 ADR 不改变该例外的边界，只改变它的存放与复用方式。
- **`_humanized.md` 失效不变量的扩面**：重生成正文 / 编辑正文 / 改选（9.1 已覆盖）三处都必须删 `_humanized.md` 并清 `humanized_path`，否则陈旧 humanized 与新 body 对不上——本 ADR 的 D4 是该不变量在新增两条改动路径上的延伸，非新规则。
- **测试与 SSOT 同步**：`tests/test_compose_publish.py` 需新增 golden-snapshot 证「抽取后 monolithic 渲染结果不丢 headline 规则文本」；`docs/SSOT/news-to-film-pipeline.md` 的 compose 段将在 Phase 9.8 GATE（9.8.7）后同步引用本 ADR。
- **不属于本 ADR**：`run_headline` / adapter / serve 端点 / 前端交互的具体实现细节记录在各 TODO 的交付报告（`docs/reports/Phase9.8.*-report.md`），本 ADR 只固化跨 TODO 的架构决策。