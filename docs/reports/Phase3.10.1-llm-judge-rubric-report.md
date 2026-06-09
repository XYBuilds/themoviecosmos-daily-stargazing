# Phase 3.10.1 - llm_judge.py 双轴 rubric 重写 交付报告

## 1. 改动范围 (Scope)

- `scripts/resonance_rubric.py` — `TYPE_DEEP`/`TYPE_STRONG` 措辞迁移（结构→逻辑）；legacy 全串解析顺序
- `scripts/llm_judge.py` — 逐字粘贴 3.10.0 judge-ready `_JUDGE_SYSTEM`/`_JUDGE_RUBRIC`；新增 `causal_test` 字段与校验；schema v3
- `scripts/run_phase39_judge_batch.py` — 批跑 checkpoint 写入 `causal_test`
- `tests/test_llm_judge.py` — 双轴 rubric 措辞、反测句校验、score↔type 矩阵单测
- `tests/test_resonance_rubric.py` — 新常量与 legacy 全串解析
- `.cursor/plans/Phase3.10-logic-resonance-and-judge-prescreen.plan.md` — p310-1 标 complete

无新增依赖包。

## 2. 技术实现 (Implementation)

- **权威措辞传播**：`_JUDGE_SYSTEM` 与 `_JUDGE_RUBRIC` 逐字来自 `prompts/_shared/resonance_definition_v2.md` §2 judge-ready；Step 1 表层元素 + 0 分守门，Step 2 POV/尺度不变因果引擎（替换骨架同构）。
- **因果反测句**：judge JSON 新增必填 `causal_test`（「X under constraint Z drives Y」双向映射句）；`score==2` 或 `TYPE_DEEP` 时非空，否则可 `""`；review 内联字段 `judge因果反测`。
- **常量迁移**：`深层共振（仅逻辑，无表层）` / `强共振（表层 + 逻辑）`；旧人工标注 `结构`/`双重`/全串仍经 `_LEGACY_TO_CANONICAL` 解析。
- **JudgeFn 签名**：`(score, type, rationale, causal_test)` 四元组贯穿 `score_items` / `call_llm_judge` / batch replay。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_llm_judge tests.test_resonance_rubric -v
# Ran 24 tests — OK

python -m unittest discover -s tests -p "test_*.py" -q
# Ran 159 tests — OK (skipped=1)
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `docs/eval-the-bet.md` §4 仍为旧措辞，待 3.10.2 rubric-ready 粘贴同步。
- 3.9 legacy `llm-judge-scores.json` 无 `causal_test` 字段；`load_judge_output` 默认 `""`，重校准须在 3.10.5+ 新跑 judge。
- `eval_editor_fields.py` / `backfill_review_scores.py` 注释仍写旧类型名，3.10.2 可连带。
