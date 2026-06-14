# Phase 3.12.2 - personas.py 旧通道清除 交付报告

> 账面说明：3.12.2 与 3.12.3 因「契约 ↔ parser ↔ pipeline」三者强耦合，按已确认的方案 C（原子组合）合并实现，测试仅在合并块末尾要求全绿；账面仍按 plan TODO 边界拆成两次 commit + 两份报告。本报告覆盖 personas.py 旧通道清除与编排/测试对齐。

## 1. 改动范围 (Scope)

- `scripts/personas.py`（修改）：删除整个 ADR-0008 通道/dual-floor/composition-mode 函数群，收敛为单一 ladder→search_unit 路径。
- `scripts/run_persona_batch.py`（修改）：移除依赖旧通道的批量 diversity guard 及其辅助函数，清理对应 import。
- `tests/test_personas.py`（重写）：删除全部 channel/dual-floor/composition 用例，新增原生 search_unit 路径与 pipeline 用例。
- phase311 试点/预测集群（**删除** 9 文件）：`scripts/lib/phase311_pilot.py`、`scripts/lib/phase311_pretest.py`、`scripts/run_phase311_full_batch.py`、`scripts/run_phase311_pilot.py`、`scripts/run_phase311_pretest.py`、`scripts/audit_phase311_pilot.py`、`tests/test_phase311_pilot.py`、`tests/test_phase311_pretest.py`、`tests/test_phase3117_full_batch.py`。

依赖包：无新增/删除。

## 2. 技术实现 (Implementation)

**模块关系演变（旧 → 新）**：

- 旧态：screenwriter 产 `pseudos[] + channel`，personas.py 按 neutral/toned/focalized 三通道分别组装、跑 dual-floor 守卫、salience-rank 重排、hypernym anchor 强校验，再拼成 search_units。
- 新态：alt_creator → screenwriter（LLM 直接产 `search_units[]`）→ `parse_search_units_response` → `build_search_units_payload`（无 channel 过滤）→ search_units dict。中间不再有任何通道分流或 dual-floor 概念。

**删除的 ADR-0008 函数群**（已确认全部无外部活引用）：`build_objective_floor_neutral_pseudo`、`assemble_persona_channel_pseudos`、`assemble_adr8_channel_pseudos`、`validate_adr8_dual_floor`、`validate_adr8_fact_guard`、`validate_adr8_runtime_guards`、`parse_adr8_pseudos_response`、`filter_adr8_pseudos_individually`、`attach_adr8_provenance`、`validate_focalized_derivation`、`validate_toned_hypernym_anchor`、`validate_center_in_decon`、`validate_focal_char_in_decon_who`、`validate_supporting_element_cap`、`validate_center_mutual_exclusion`、`collect_hypernym_anchor_terms`、`collect_lens_terms`、`resolve_neutral_fragment_ids`、`fragment_ids_from_salience`、`validate_neutral_pseudo_batch_diversity`、`inject_adr8_composition_mode`、`composition_mode_active`、`derive_expected_channel` 等，连同孤立常量/正则/类型别名（`_CHANNEL_ROLES`、`_COMPOSITION_CHANNELS`、`Valence`、`Provenance`、`ChannelRole`、`CompositionChannel` 等）一并清除。

**保留收敛路径**：`build_fragment_ladders`（3.12.1 后自包含，objective 层内联折叠）、`build_fragment_bundle_search_units`、`search_unit_from_pseudo`、`validate_search_unit`、`build_search_units_payload`、`validate_salience`、`annotate_element_ids`。

**phase311 集群删除（已确认 delete_cluster）**：该集群业务逻辑即旧通道 firewall-audit 架构，与 ADR-0009 不兼容。删除前经 grep 验证 9 文件构成闭合的 import 闭包（`PHASE310_ROOT`/`PHASE311_ROOT`/`load_gap_a_samples`/`main_async` 等交叉引用全在集群内部）。

**关键不变量**：`build_search_units_payload` 持续输出稳定的 `search_units` dict，`retrieve.py` 优先消费该 dict —— 契约边界未变，retrieve 及其测试不受影响。

**run_persona_batch.py 对齐**：原 3.8/3.9 阶段的 neutral-pseudo 批量 diversity guard 依赖 `channel_role` 字段与 `NEUTRAL_PSEUDO_ID`，在 ADR-0009 下已无对应通道概念，属死逻辑，连同两个辅助函数一并移除。`run_batch_for_news` 主流程其余行为不变。

## 3. 本地验证结果 (Verification)

- 导入冒烟：`scripts.personas` / `scripts.agents` / `scripts.run_persona_batch` / `scripts.summarize_eval` 均 import OK。
- 全量测试：`python -m unittest discover -s tests -p "test*.py"` → `Ran 212 tests, OK (skipped=1)`，零 regression。
- Lint：改动文件无诊断。
- 残留扫描：仓库级 grep 确认 `scripts/` 下无 `assemble_adr8`/`composition_mode`/`channel_role`/`validate_adr8_`/`parse_adr8_pseudos`/`collect_lens_terms`/`validate_neutral_pseudo_batch_diversity` 等已删除符号的活引用（personas.py 仅余的命中是一条已更正的模块 docstring）。

> 测试数从 3.12.1 的 265 降至 212，系预期：删除 9 个 phase311 测试文件及 test_personas.py 中大批 ADR-0008 通道用例所致，非 regression。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `retrieve.py` 仍保留 neutral/toned/focalized 兼容分支与 `compare_pool_diff_by_channel`/`pool_diff_by_channel_to_dict`（被 `test_retrieve_funnel.py` 引用），属 3.12.4 范围，本 TODO 不动以隔离等价性门禁变量。
- N=10 LLM 等价性重算留待 3.12.6（标 `[需人工验收]`）。
- 历史报告（`Phase3.8.*`/`Phase3.11.*`）中对 phase311 文件与旧通道的引用属历史记录，不在本 TODO 回填范围。