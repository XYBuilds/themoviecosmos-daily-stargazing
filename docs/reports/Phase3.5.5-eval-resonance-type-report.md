# Phase 3.5.5 - 评测改造（共振类型 / structural_2_rate）交付报告

## 1. 改动范围 (Scope)

- `scripts/run_eval.py` — `candidates.md` 每候选新增 `- **共振类型**:` 占位行
- `scripts/summarize_eval.py` — 解析共振类型；输出 `baseline/creative_structural_2_rate`；闸门第 2 条优先 `structural_2_rate`，无标注时退回 `total_2_rate`
- `tests/test_summarize_eval.py` — 单元测试（legacy fallback + 手填 fixture）
- `tests/eval_fixtures/resonance-structural/candidates.md`
- `tests/eval_fixtures/resonance-mixed/candidates.md`
- `.cursor/plans/Phase3.5-pivot-reality-deconstruction.plan.md` — Todo 3.5.5 标记完成

**分支继承**：`feat/phase3.5-eval-resonance-type` 基于 `feat/phase3.5-retrieve-multi-pseudo`（3.5.4）。

## 2. 技术实现 (Implementation)

- **run_eval**：在 `- **共振分**:` 后追加 `- **共振类型**:`（注释提示：表层 / 结构 / 双重；0 分留空）。
- **summarize_eval**：
  - 解析 `共振类型` 为 `表层` / `结构` / `双重`（HTML 注释剥离后子串匹配）。
  - `structural_2_rate` = 桶内「共振分=2 且 类型∈{结构,双重}」÷ 桶内已评分候选数（与总 2 分率分母一致）。
  - 批次内**任一**候选填了共振类型 → 闸门第 2 条用 `baseline_structural_2_rate < creative_structural_2_rate`；否则退回 `baseline_2_rate < creative_2_rate`（兼容旧 10 份 Eval）。
  - JSON/stdout 增加 `resonance_types_filled`、`gate.compare_mode`。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_summarize_eval -v
# Ran 3 tests — OK

python -m scripts.summarize_eval tests/eval_fixtures/run-alpha.md tests/eval_fixtures/run-beta.md tests/eval_fixtures/run-gamma.md
# Gate line 2 compare: total_2_rate (fallback) → GATE_PASS

python -m scripts.summarize_eval tests/eval_fixtures/resonance-structural/candidates.md
# structural: baseline 0% vs creative 100% → GATE_PASS (total 2 率均为 100%，结构口径才拉开差距)

python -m scripts.summarize_eval tests/eval_fixtures/resonance-mixed/candidates.md
# structural: baseline 100% vs creative 0% → GATE_FAIL（与手算一致）
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 旧 `output/Eval/*/candidates.md` 需**重新 run_eval** 才会带共振类型占位行；未重跑者汇总仍走 total_2_rate fallback。
- 3.5.6 总编填分时应对 1/2 分候选标注共振类型，否则闸门第 2 条判别力弱。
- 下一 Todo：**3.5.6** 用新管线重跑 N=10 → 填分 + 类型 → `summarize_eval` → `GATE_RESULT.md`（需人工验收）。
