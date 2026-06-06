# Phase 3.9.0 - 契约/CONTEXT 对齐 ADR-0006 交付报告

## 1. 改动范围 (Scope)

- `prompts/_shared/persona_alt_creator_contract.md` — 新增 `salience` 字段规格、选材≠措辞铁律、D6 校验与 plan B 回退说明
- `CONTEXT.md` — 补齐 held-out oracle、per-persona salience、三桶对照、留出冻结等术语，并与中性通道「选材 persona 化 / 措辞中立」口径对齐
- `.cursor/plans/Phase3.9-a1-oracle-per-persona-salience-three-bucket-eval.plan.md` — 将 todo `p39-0` 标为 complete（本交付步骤）
- 新增依赖包：无

## 2. 技术实现 (Implementation)

- **Salience 规格**：在 alt-creator 契约中定义顶层 `salience[]` 为既有 `element_id` 的有序列表（最→次），仅 subset/permutation、禁止造 id 或自由文本；下游取 Top-K(4–5) 作为 `fragment_ids` 驱动 `build_objective_floor_neutral_pseudo`。
- **选材≠措辞铁律**：契约明确 `salience` 只驱动中性碎片 SELECTION，persona LLM 不写中性散文；措辞由模板从所选碎片的 `surface` + `hypernym` 拼装，与 ADR-0006 D2/D6 架构拆分一致。
- **CONTEXT 术语**：文档化 held-out oracle (A1)、per-persona salience、三桶可评对照、留出冻结纪律，并区分 objective-floor neutral 与 lens 通道。
- **Plan B**：主路径为 (B) 每新闻动态 salience；若 pilot 不稳可启用 (C) 混合——persona card **价值轴**仅作软偏好先验，禁止硬编码碎片 id，LLM 仍做最终 per-news 选择（ADR-0006 D6 子决策①）。

## 3. 本地验证结果 (Verification)

- 文档对照 **ADR-0006 D6** 逐条核对：架构拆分（只发 id）、prompt 选材指令、subset/permutation 硬校验、who/where 可选纳入、多样性守卫在 plan 中留给 3.9.1/pilot — 契约与 CONTEXT 表述一致。
- 人工验收：用户已 approve Phase 3.9.0（p39-0）；未运行代码单测（本 todo 为文档/契约对齐，实现落在 3.9.1+）。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **3.9.1 须落地**：`personas.py` 尚未接入 `salience`；在代码实现前，运行时仍使用固定 `_default_neutral_fragments`。
- **Salience/valence 边界**：契约与 ADR 已声明防火墙焦点；3.9.6 pilot 须专审泄漏与 near-duplicate。
- **Plan B 未实现**：仅文档约定；若 pilot No-Go，需在 3.9.1 或后续迭代注入软先验逻辑。
- ADR-0006 仍为 `proposed`；待 GATE go 后由 3.9.9 升格 SSOT。
