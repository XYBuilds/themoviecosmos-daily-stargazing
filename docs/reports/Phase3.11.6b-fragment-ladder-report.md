# Phase 3.11.6b - Fragment ladder 架构迁移 + ADR-0009 交付报告

## 1. 改动范围 (Scope)

- `docs/adr/0009-fragment-ladder-and-search-unit-architecture.md` — 新增 ADR-0009，记录 fragment ladder / search unit 架构决策
- `docs/adr/0008-salience-driven-element-composition-and-multi-vantage-pov.md` — 标注通道结构、POV channel、双地板由 ADR-0009 接管
- `prompts/_shared/persona_screenwriter_contract.md` — 迁移为 ADR-0009 过渡契约：LLM 仍产中心化草稿，检索入口改为 search unit
- `prompts/_shared/persona_alt_creator_contract.md` — salience 与 alt-pool 改为 fragment ladder 输入口径
- `scripts/personas.py` — 生成 `fragment_ladders` 与 `search_units`，并保留旧 `pseudos` 兼容字段
- `scripts/run_phase311_pilot.py` — pilot 调用同步传入 deconstruction 以生成完整 ladder/search unit schema
- `scripts/retrieve.py` — 检索优先读取 `search_units`，排序迁移为 `search_unit_kind` 驱动的 convergent sort
- `tests/test_retrieve_funnel.py` — 新 convergent sort、search unit kind 池差分解测试
- `tests/test_retrieve_multi_pseudo.py`、`tests/test_retrieve_quality.py`、`tests/test_retrieve_neutral_collision.py` — 旧质量断言迁移到 `objective_match` / `persona_semantic_match` 口径
- `tests/test_judge_batch_parallel.py` — 补齐 checkpoint prompt version 参数，恢复全量 discover
- `.cursor/plans/Phase3.11-pov-focalization-additive.plan.md` — `p311-6b` 标记 completed 并勾选验收项
- 新增/删除的依赖包：无

## 2. 技术实现 (Implementation)

### fragment ladder

- 每个 deconstruction element 都生成统一 ladder。
- objective levels 用于事实检索入口；interpretive / perspective 用于 persona-semantic 表达。
- 旧 hypernym / alternative / lens 不再分散作为独立架构主语义。

### search unit

- `surface-fragment-bundle`：面向 `when / where / who` 的 objective recall。
- `event-fragment-bundle`：面向 `why / how / result` 的 objective recall。
- `persona-semantic`：绑定 `center_element` 与 `supporting_elements`，承载 persona 解释层。

### retrieve

- 主入口改为优先读取 `agents[].search_units`；旧 `pseudos[]` 只作为兼容层。
- 主排序信号改为：`surface_match`、`event_match`、`persona_semantic_match`、persona diversity、center dimension diversity、dense similarity。
- 旧 `neutral / toned / focalized` channel 字段保留为历史兼容展示，不再主导排序。
- A/B pool diff 新增 `search_unit_kind` 分解与 collision gain 输出。

## 3. 本地验证结果 (Verification)

```text
> python -m unittest tests.test_personas tests.test_retrieve_funnel

OK
```

```text
> python -m unittest tests.test_phase311_pilot tests.test_phase311_pretest tests.test_retrieve_multi_pseudo tests.test_retrieve_quality tests.test_retrieve_neutral_collision

Ran 32 tests in 0.353s

OK
```

```text
> python -m unittest tests.test_judge_batch_parallel

Ran 4 tests in 0.109s

OK
```

```text
> python -m unittest discover -s tests -p "test*.py"

Ran 256 tests in 19.257s

OK (skipped=1)
```

```text
> python -m scripts.personas --deconstruction-file "tests\fixtures\01-grid-outage-deconstructed.json" --persona-id The-Ruler --out "output\tmp-phase3116b-persona-schema.json"

成功生成临时 schema；结构包含 `fragment_ladders` 与 `search_units`。临时输出文件已删除，未纳入提交。
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `pseudos[]`、`channel_role`、`neutral / toned / focalized` 仍保留兼容路径，后续可在历史产物不再依赖后逐步收敛。
- 当前 hybrid recall 已完成 schema 与排序迁移；lexical / weighted ladder 子信号仍可在 3.11.7 调优阶段继续展开。
- 3.11.7 的归因口径应使用 `search_unit_kind`，不再按旧 channel 分解。
- 分支继承：`feat/phase3.11.6b-fragment-ladder` 从最新 `main` 检出，前置 3.11.6 已 completed 并合并。