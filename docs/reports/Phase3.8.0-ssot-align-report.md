# Phase 3.8.0 - SSOT 对齐 ADR-0005 交付报告

## 1. 改动范围 (Scope)

- `docs/SSOT/reality-deconstruction-contract.md` — v2 重写：A0 = P-Extract verbatim only；新增 P-Expand（hypernym 梯 + 客观性试金石）；三层 provenance；废止 v1 标签梯/geocode/scale/scene_archetype 等 inert 字段
- `CONTEXT.md` — 补术语（客观地板中性 / persona 中点中性 / 中性通道 / 语气通道 / neutral hit rate / 三层 provenance）；收窄现实解构 agent 职责；撞车形状对齐 ADR-0005
- `prompts/_shared/persona_alt_creator_contract.md` — persona-relative valence、两中性区分、三层 provenance prose 与 ADR-0005 对齐
- `prompts/_shared/persona_screenwriter_contract.md` — 中性通道 = 客观地板（surface+hypernym，无 lens）；toned = hypernym 锚 + lens
- `.cursor/plans/Phase3.8-objective-extraction-neutral-channel.plan.md` — todo `f38c1d3e-0001-4000-8038-000000000000` → `completed`

**分支**：`feat/phase3.8.0-ssot-align`（基于 `main` 上 3.7-review persona card 提交）

**用户验收**：2026-06-05 用户回复「通过」→ approve 3.8.0 契约口径，可进 3.8.1

## 2. 技术实现 (Implementation)

- **reality-deconstruction-contract v2** 将 A0 被混为一谈的职责拆为 P-Extract（逐字 who/where/when/why/how/result + role + relations，保留 source valence）与 P-Expand（一份共享 hypernym 梯，客观性试金石：A2&A4 不吵才留）。下游 P-Lens / P-Compose 消费三层 provenance（surface / hypernym / lens）。
- **两个中性** 在 contract 与 CONTEXT 中明列：(a) 客观地板中性 = surface+hypernym，进中性通道；(b) persona 中点中性仅活于 lens spectrum，不进通道。
- **inert 字段丢弃** 理由写死：`retrieve.py` 只嵌 `pseudo.text`，geocode/coordinates/scale/scene_archetype 从未进嵌入。
- **persona 契约** 与 3.7-review 已落地的价值轴 prose 交叉校对；alt-creator / screenwriter 共享契约补充中性通道与 toned 锚表述，与 ADR-0005 C-Neutral / C-Toned 一致。
- **本 TODO 仅 SSOT/契约层**；`scripts/deconstruct.py`、`scripts/personas.py`、`scripts/retrieve.py` 代码实现留 3.8.1–3.8.3。

## 3. 本地验证结果 (Verification)

- `rg -i "标签梯|geocode|scene_archetype|全维度无损" docs/SSOT/reality-deconstruction-contract.md` — 仅出现在「v1 废止项」说明节，无现行要求残留
- `rg "客观地板中性|persona 中点中性|neutral hit rate|三层 provenance" CONTEXT.md` — 四条术语均已落盘
- ADR-0005 §P-Extract/P-Expand/P-Lens/P-Compose、两中性、C-Neutral/C-Toned、撞车主判据 — 与 contract §0 原则及 CONTEXT 撞车/通道条目逐条对照，无冲突
- 无运行时脚本变更；未跑 `unittest`（本 TODO 仅文档/SSOT）

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **3.8.1+** 须从合并后的 `main` 检出新分支；实现 A0 verbatim 瘦身与客观扩展 pass 时以本 contract 为唯一 SSOT
- **代码仍处旧口径**：`deconstruct.py` / `retrieve.py` 仍产 inert 字段、仍用对称 `distinct_agents>=2`；须在 3.8.1–3.8.3 一次性切换，避免新旧混用（ADR-0005 §后果）
- **ADR-0005 Status** 保持 `proposed` 至 3.8.8 GATE go；3.8.9 再升 `accepted`
- **A1** 文档已标「取代方向」但代码未删；删 A1 前置 A1-superset 闸（3.8.7 并跑 + 3.8.8 验证）
