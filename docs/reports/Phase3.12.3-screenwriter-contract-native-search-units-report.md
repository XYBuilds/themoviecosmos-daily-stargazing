# Phase 3.12.3 - LLM 契约原生 search_units[] + parser 交付报告

> 账面说明：3.12.3 与 3.12.2 按方案 C（原子组合）合并实现。本报告覆盖 LLM 契约改写与 agents.py parser 新增；测试全绿的整体验证见 Phase3.12.2 报告（同一合并块末尾跑出）。

## 1. 改动范围 (Scope)

- `prompts/_shared/persona_screenwriter_contract.md`（重写）：输出根节点改 `search_units[]`。
- `prompts/_shared/multi_pseudo_output_contract.md`（修改）：补 ADR-0009 scope 说明，保留 A1/A2/A4/A7 news-writer 仍走 `pseudos[]` 的现状。
- `prompts/_shared/persona_alt_creator_contract.md`（修改）：移除外部 expansion pass 引用，通道表述中性化。
- `scripts/agents.py`（修改）：新增 `parse_search_units_response`。

依赖包：无新增/删除。

## 2. 技术实现 (Implementation)

**LLM 契约口径演变（screenwriter）**：

- 旧契约：返回 `{ pseudos: [{ id, text, fit, source: { channel: "toned", fragments } }] }`，强制每条带 hypernym anchor，输入含 `{{expansion_json}}`。
- 新契约：返回 `{ search_units: [{ id, center_element, supporting_elements[2-4], search_text, fit }] }`。去掉 `pseudos[]` wrapper、`channel` 字段、`{{expansion_json}}` 输入与强制 hypernym anchor；改以 salience ranking 引导 center 选择，objective anchor 由 ladder 侧自产。

**parser 数据结构映射**：`parse_search_units_response` 解析根节点 `search_units[]`，把每个 unit 整形为 `PseudoSegment`，使下游 `search_unit_from_pseudo` 无改动消费 —— `source.center` 存 center_element，`source.fragments` 存 supporting_elements。校验项：unit 数量 1–3、center 必填且在 known_elements 内、center 互斥（不可重复）、supporting 2–4 且全部已知、fit 必填（require_fit）。fit 解析逻辑复用既有 `_parse_fit_value`。

**契约分工边界**：`multi_pseudo_output_contract.md` 仍是 A1/A2/A4/A7 news-writer（经 `parse_pseudos_response` 走 `pseudos[]`）的基底，不在本次通道清除范围，仅补 scope 说明避免误删。screenwriter 专属的 search-unit 口径与 news-writer 的 pseudos 口径并存且互不干扰。

## 3. 本地验证结果 (Verification)

- parser 行为由 `tests/test_personas.py::NativeSearchUnitParserTests` 覆盖：正常解析、重复 center 拒绝、未知 center 拒绝、缺 fit 拒绝、supporting 超界拒绝。
- 整体全量测试 `Ran 212 tests, OK (skipped=1)`（详见 Phase3.12.2 报告）。
- Lint：改动文件无诊断。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 契约改动后，建议 3.12.3 之后跑单条真实 LLM smoke 验证模型输出可解析性（plan 风险项）；本地离线测试已覆盖 parser 解析路径，但未实跑 LLM。
- `parse_pseudos_response` 保留供 news-writer 使用，未删除。
- N=10 LLM 等价性重算留待 3.12.6（标 `[需人工验收]`）。