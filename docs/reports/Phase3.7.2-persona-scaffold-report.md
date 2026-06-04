# Phase 3.7.2 - 双步 persona 管线脚手架 交付报告

## 1. 改动范围 (Scope)

- `prompts/_shared/persona_alt_creator_contract.md`（新建）
- `prompts/_shared/persona_screenwriter_contract.md`（新建）
- `scripts/personas.py`（新建）：`decon → alt_creator → screenwriter → pseudos(+fit)`，flavored-decon overlay
- `scripts/agents.py`：`PseudoSegment.fit`、`parse_pseudos_response(..., require_fit=)`、`pseudo_to_dict` 含 fit
- `tests/test_personas.py`（新建）
- `.cursor/plans/Phase3.7-persona-resonance.plan.md`：todo `f37b1c2d-0001-4000-8037-000000000002` → completed
- 无新增 Python 依赖包

## 2. 技术实现 (Implementation)

- **P-Source / P-Select**：alt-creator 契约要求每 element 正–中–负全谱 + `original_term`；解析器校验 `element_id` 归属中性 decon、`valence` 三桶齐全。
- **P-SSOT**：`build_alt_pool_overlay` + `overlay_forbids_decon_fork` 禁止 overlay 嵌入 `anchor`/`who`/全文 decon；screenwriter 仍注入带 fragment id 的 decon 供 `source.fragments`，但持久化 overlay 仅 `persona_id` + `alt_pool.elements[]`。
- **P-Tone / P-Force**：screenwriter 契约扩展 `multi_pseudo_output_contract`，强制每 pseudo `fit ∈ [0,1]`；`parse_pseudos_response(..., require_fit=True)` 供 persona 路径使用。
- **管线**：`run_persona_pipeline` 串联 `run_alt_creator` → `run_screenwriter`；CLI：`python scripts/personas.py --deconstruction-file … --persona-id The-Ruler`。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_personas -v
# Ran 11 tests in 0.148s — OK
```

覆盖：element id 标注、alt-pool 解析、valence/unknown id 错误、overlay 防 fork、fit 解析与边界、screenwriter prompt 含 overlay。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **3.7.3**：需 `prompts/personas/The-Ruler/persona_card.md` 与 04 端到端 LLM pilot；脚手架已预留 `load_persona_card`。
- **retrieve / run_eval**：尚未接线 persona 输出；留待 3.7.3+。
- `test_agents_p35.py` 仍为函数式用例，`-m unittest` 不自动发现（既有债）；persona 单测已用 `TestCase`。
- A1 路径 `require_fit=False` 默认，行为与 Phase 3.6 兼容。
