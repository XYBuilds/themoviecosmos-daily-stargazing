# Phase 3.12.4 - retrieve.py 旧 channel 诊断清除 交付报告

## 1. 改动范围 (Scope)

retrieve 侧（本 commit）：

- `scripts/retrieve.py`：删除 `neutral/toned/focalized` channel 兼容分支、`neutral_hit_rate` / `neutral_hits` / `neutral_total` 输出、`distinct_agents` 字段、A1 oracle 诊断；保留 `search_unit_kind` 分解、convergent sort、surface/event/persona_semantic_match、quality floor / D1 标记、A1 oracle 候选排除。
- `tests/test_retrieve_a1_oracle.py`：改写为 ADR-0009 口径（保留 oracle 排除，去 channel 诊断断言）。
- `tests/test_retrieve_quality.py`：改写为 objective/persona 口径。
- `tests/test_retrieve_multi_pseudo.py`：改写。
- `tests/test_retrieve_funnel.py`：改写。
- `tests/test_retrieve_neutral_collision.py`：删除（neutral channel 概念随 ADR-0009 消失）。

无新增/删除依赖包。

## 2. 技术实现 (Implementation)

- retrieve.py 以 `search_units` dict 为稳定契约边界优先消费，旧 `pseudos[]` 仅作兼容回退。
- channel 信号轴整体由 `channel_role` 迁移到 `search_unit_kind`（surface-fragment-bundle / event-fragment-bundle / persona-semantic）。
- 命中分解口径：`neutral_hits`→`objective_hits`、`distinct_agents`→`persona_count`；删除 `neutral_hit_rate` / `neutral_total` 派生量。
- A1 oracle 仅保留候选**排除**逻辑（keep_exclusion），删除其 channel 诊断对比输出。

## 3. 本地验证结果 (Verification)

- retrieve 相关测试改写后单独验证：26 tests OK。
- 全量回归（含后续 eval-consumer 改动）：`python -m unittest discover -s tests -p "test*.py"` → Ran 194 tests, OK (skipped=1)。
- `scripts/retrieve.py` grep 确认零残留 channel 符号；lint clean。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 本 TODO 与 3.12.5（eval-consumer 对齐）构成一个原子块；测试仅在原子块末尾要求全绿，故 retrieve 侧独立 commit 时若单跑全量可能依赖 3.12.5 的消费者改动一并落地。两者按账面拆分为两次 commit + 两份报告。
- `search_units` dict 输出在整个重构期间保持稳定，未改变 retrieve 的对外契约边界。
- 等价性对照（与 3.11.8 基线）按 ADR-0009 新口径（full_both）在 3.12.6 人工验收门重建，本 commit 不含运行结果。