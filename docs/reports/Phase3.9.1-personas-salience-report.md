# Phase 3.9.1 - personas salience neutral selection 交付报告

## 1. 改动范围 (Scope)

- `scripts/personas.py` — salience 解析/校验、Top-K `fragment_ids`、`resolve_neutral_fragment_ids`、移除 who/where 无条件追加、`validate_neutral_pseudo_batch_diversity`
- `tests/test_personas.py` — 新增 `PersonaSalienceTests`（10 项：正/负例解析、Top-K、who/where 可选、多样性守卫）
- `.cursor/plans/Phase3.9-a1-oracle-per-persona-salience-three-bucket-eval.plan.md` — p39-1 标 complete
- 新增/删除的依赖包：无

**分支继承**：基于 `main` @ `7bde53e`（含 3.9.0 契约 + 已合并的 3.9.2 oracle 改动；本 TODO 仅改 `personas.py` / 单测）。

## 2. 技术实现 (Implementation)

- **`AltPoolOverlay.salience`**：alt-creator JSON 顶层 `salience[]` 经 `validate_salience` 硬校验（subset/permutation、非法 id / 自由文本 / 重复即拒）后存入 overlay 并序列化。
- **Top-K 选材**：`fragment_ids_from_salience` / `resolve_neutral_fragment_ids` 取 salience 头部 4–5 个 id 传入 `build_objective_floor_neutral_pseudo(fragment_ids=...)`；无 salience 时回退 `_default_neutral_fragments`（兼容旧 fixture）。
- **who/where 可选**：删除 `build_objective_floor_neutral_pseudo` 中对全部 who/where 的无条件 `floor_terms` 追加；仅 salience 选中的 id 进入中性 pseudo。
- **多样性守卫**：`validate_neutral_pseudo_batch_diversity` 对一批中性 pseudo 两两检查——文本相似度 ≥ 0.92 **且** 碎片集合对称差 < 2 时抛出 `ValueError`（near-duplicate → 失败/可触发重生成）。
- **组装入口**：`assemble_persona_channel_pseudos` 经 `resolve_neutral_fragment_ids` 驱动 per-persona 中性选材，与 ADR-0006 D6 / alt-creator 契约「salience 只驱动 SELECTION、不碰 wording」一致。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_personas -v
Ran 39 tests in ~14s
OK
```

新增 `PersonaSalienceTests` 10 项全部通过；原有 29 项 regression 无失败。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **batch 层尚未接线**：`run_persona_batch.py` 尚未在 12 persona 跑完后调用 `validate_neutral_pseudo_batch_diversity`（留给 3.9.6 pilot 或后续 batch 集成）。
- **salience 仍为可选字段**：无 salience 的 alt-pool 仍走默认碎片（向后兼容）；生产路径依赖 alt-creator 契约输出 salience。
- **3.9.3+ 依赖本 TODO**：三桶度量与 pilot 需 per-persona 多样化中性 leg；后续 Phase 应基于本分支或已合并的 `main`。
