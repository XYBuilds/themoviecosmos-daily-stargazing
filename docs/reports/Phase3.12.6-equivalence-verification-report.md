# Phase 3.12.6 - 等价性验证 交付报告

## 1. 改动范围 (Scope)

- 新增 `scripts/verify_phase312_equivalence.py`：离线等价性重放对比工具。
- 新增 `output/Eval/phase3.12/equivalence-report.json`：N=10 逐条对比结果。
- 修改 `.cursor/plans/Phase3.12-code-doc-sync.plan.md`：3.12.6 标记 completed。
- 无新增/删除依赖包。

> **分支继承关系**：本 TODO 在 stacked 分支 `feat/phase3.12.5-eval-consumer-alignment` 上完成（继承自 3.12.4 → 3.12.3 → 3.12.2 → 3.12.1 链）。3.12 整包在 3.11.8 尚未合并 `main` 前，按「Phase 依赖与顺序执行」规则采用 stacked dev，整包待 3.12.6 GATE 通过后统一合并。

## 2. 技术实现 (Implementation)

**验证策略：离线重放（offline replay），零 LLM 成本。**

核心洞察：3.12 是纯重构（仅删除 ADR-0008 channel 诊断字段 + 独立 P-Expand pass），召回阶段是确定性的——输入相同的 `search_units` dict，经相同 embedding index（`paraphrase-multilingual-MiniLM-L12-v2`）做 top-k 余弦召回，结果必然 bit-parity。

数据流：
- 输入源：3.11.7 全批基线 `output/Eval/phase3.11/full-batch-20260613-3117/{01..10}/agents.json`，其中已含 `search_units` dict（与重构后 `retrieve.py` 消费键名完全一致）。
- 重放：把基线 `agents.json` 直接喂给重构后的 `retrieve.from_agents_json`。
- 对比基线：同目录下基线 `retrieve.json`。

逐条对比四个维度：
1. **候选集合** — `candidates[].tmdb_id` 的集合相等性（baseline_only / replay_only 应为空）。
2. **候选顺序** — convergent sort 排序后的 tmdb_id 序列相等性。
3. **search_unit_kind 分解** — `per_agent[].pseudos[].source.search_unit_kind` 三类计数相等性。
4. **A1 oracle** — held-out 基准命中集相等性。

工具入口 `python -m scripts.verify_phase312_equivalence`，PASS（全 parity）退出 0，DIVERGENT 退出 1。

## 3. 本地验证结果 (Verification)

```
python -m scripts.verify_phase312_equivalence --out output/Eval/phase3.12/equivalence-report.json
EQUIVALENCE: PASS (set=True order=True kind=True oracle=True)
```

`equivalence-report.json` summary：

| 维度 | 结果 |
|---|---|
| candidate_set_bit_parity | true（10/10，零 mismatch） |
| candidate_order_bit_parity | true（10/10） |
| kind_breakdown_parity | true（10/10） |
| a1_oracle_parity | true（10/10） |

10 条新闻每条候选数均为 19/19，`baseline_only` / `replay_only` 全空。

全量测试套件：

```
python -m unittest discover -s tests -p "test*.py"
Ran 194 tests in 18.049s
OK (skipped=1)
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **唯一可解释差异**：基线 `retrieve.json` 仍带 `channel_role` 诊断字段，重构后输出不再产出——这是 ADR-0009 口径下故意删除的项，不影响召回结果本身（候选集/顺序/kind 全等已证明）。
- **验证范围**：本验证覆盖 deconstruct → agents → retrieve 中**确定性的 retrieve 阶段**（重构改动集中处）。LLM 生成阶段（screenwriter search_units 产出）因 3.12.3 改了契约，无法用旧产物做 bit-parity；其正确性由 3.12.3 的 parser 单测 + 契约 schema 校验保证，不在本离线重放范围。
- **后续**：3.12.7 文档回填（ADR-0009 future-work / PRD §10 结构树 / workflow 残留引用）待办。3.12 整包合并 `main` 是本 GATE 通过后的动作。