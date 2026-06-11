# Phase 3.11.2 - 元素中心构图 + 多视角 POV 交付报告

## 1. 改动范围 (Scope)

- **修改** `scripts/personas.py`：ADR-0008 生成层接线（`composition_mode_active`、`inject_adr8_composition_mode`、`build_adr8_screenwriter_user_prompt`、`parse_adr8_pseudos_response`、`assemble_adr8_channel_pseudos`）；贪心 salience 排序/预算；provenance 标签（`center` / `channel` / `focal` / `salience_rank` / `composition_mode`）；card 视角座位派生（`derive_expected_channel`）；`run_persona_pipeline` / `run_screenwriter` 在 `alt_pool.salience` 非空时自动启用 composition mode。
- **修改** `scripts/lib/phase311_pretest.py`：核心 ADR-0008 逻辑迁至 `personas.py`；保留 pretest 专用 `assemble_adr8_channel_pseudos_with_baseline_neutral`（复用 3.10 n1）。
- **修改** `scripts/run_phase311_pretest.py`：调用 pretest 装配包装函数。
- **修改** `tests/test_personas.py`：新增 `PersonaAdr8CompositionTests`（12 条）覆盖中心互异、贪心排序、预算双地板、focalized 派生、provenance 完整、中性 n1 零改动、第三人称 toned 保留。
- **修改** `.cursor/plans/Phase3.11-pov-focalization-additive.plan.md`：`p311-2` 标 complete。
- **新增/删除依赖**：无。

## 2. 技术实现 (Implementation)

- **激活条件**：`alt_pool.salience` 非空 ⇒ 注入 `Composition mode: ADR-0008` + salience JSON（引用 3.11.0 contract 措辞，不私自改写）。
- **解析**：`parse_adr8_pseudos_response` 校验 `center`/`channel`/`focal`、中心互异、双地板（≥1 非 focalized toned）。
- **代码侧贪心**：`rank_adr8_pseudos_by_salience` + `apply_adr8_pseudo_budget`（默认 top-3，裁剪时保留 ≥1 toned）。
- **装配**：`assemble_adr8_channel_pseudos` 用既有 `build_objective_floor_neutral_pseudo` 构建 n1（wording 不变）+ 预算后 toned/focalized 腿；hypernym 锚校验保留。
- **POV 派生**：`derive_expected_channel` 从 card Who 正极 + Lens Who 关键词匹配 decon `who-*` 文本，判定 focalized 资格（警告级，硬守卫留 3.11.3）。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_personas tests.test_phase311_pretest tests.test_agents_p35 tests.test_run_persona_batch
Ran 72 tests in 17.520s — OK
```

全量 `discover` 206 tests：1 个无关 `test_judge_batch_parallel` 环境错误（非本 TODO 引入）。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **3.11.3**：center/focal 硬守卫、支撑元素 2–4 上限、事实守卫、双地板硬失败尚待落地。
- **视角座位匹配**：当前为 card 关键词启发式；pilot 后可能需收紧或改为显式原型表。
- **pretest**：仍可通过 `neutral_override` 复用 3.10 基线 n1；主 pipeline 始终代码构建 n1（与 ADR-0008 D3 一致）。
