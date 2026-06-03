# Phase 3.6.4 - summarize_eval multi-vs-single gate 交付报告

## 1. 改动范围 (Scope)

- `scripts/summarize_eval.py` — 分桶由 baseline/creative 改为 multi-agent / single-agent；解析 `quality_candidate` 字段或 heading ≥2 agent；闸门第 2 条 `single_* < multi_*`，`gate.compare_mode = multi_vs_single`
- `tests/test_summarize_eval.py` — 更新 legacy fixture 期望；新增 PASS/FAIL 与 `quality_candidate` 覆盖用例
- `tests/eval_fixtures/multi-vs-single-pass/candidates.md` — structural 闸门 PASS fixture
- `tests/eval_fixtures/multi-vs-single-fail/candidates.md` — structural 闸门 FAIL fixture
- `.cursor/plans/Phase3.6-resonance-quality-gate.plan.md` — 3.6.4 todo 标记 complete

无新增依赖包。

**分支：** `feat/phase3.6.4-summarize-multi-gate`（基于 `main` @ `74e41e4`）

## 2. 技术实现 (Implementation)

- **分桶规则（D1/D2）：** `_is_multi_agent_candidate()` 优先读 `**quality_candidate**: true|false`；未显式标记时 heading 中 agent 数 ≥2 为 multi，否则 single（含 `[baseline only]` / 单 agent）。
- **闸门第 1 条：** 保留 batch ≥60% 至少 1 个 2 分候选。
- **闸门第 2 条：** 已填 `共振类型` 时用 `single_structural_2_rate < multi_structural_2_rate`；未填时 fallback 为 `single_2_rate < multi_2_rate`（同 3.5.5 逻辑，桶名改为 multi/single）。`compare_mode` 恒为 `multi_vs_single`。
- **stdout：** 输出 `single_2_rate` / `multi_2_rate` 及 structural 对应项，并打印 `Gate line 2 compare: multi_vs_single`。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_summarize_eval -v
# Ran 4 tests in 0.088s — OK
```

覆盖：legacy 三 run fallback PASS、multi-vs-single structural PASS/FAIL、`quality_candidate` 字段优先于 heading agent 数。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `docs/eval-the-bet.md` / SSOT 闸门文案仍描述 baseline/creative，待 **3.6.6（GATE go）** 同步。
- `run_eval.py` 尚未在 `candidates.md` 写入 `quality_candidate`（**3.6.3**）；当前 summarize 可从 heading `[A2, A4]` 推断 multi，或与 retrieve.json 字段对齐后由 3.6.3 补全 markdown 字段。
- 未跑 `output/Eval` 真实批次（本 todo 范围外）。
