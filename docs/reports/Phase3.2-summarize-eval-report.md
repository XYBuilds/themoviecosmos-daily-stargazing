# Phase 3.2 - summarize_eval 评分汇总与闸门判定 交付报告

## 1. 改动范围 (Scope)

- `scripts/summarize_eval.py` — 新增 Eval Markdown 解析、指标汇总与 GATE 判定 CLI
- `tests/eval_fixtures/` — 3 份手工填分 fixture（run-alpha / run-beta / run-gamma）
- `.cursor/plans/Phase3-validation-gate-the-bet.plan.md` — Todo 3.2 标记 complete

无新增 Python 依赖。

## 2. 技术实现 (Implementation)

- **CLI**：positional `.md` 路径、`--dir output/Eval`、`--out report.json`
- **解析**：按 `run_eval.py` 输出格式，从每个 `###` 候选块读取 `tmdb_id`、`also_baseline`、标题 `[A2, A4]` / `[baseline only]` 标签，以及 `- **共振分**:` 后首个 `0`/`1`/`2`（HTML 注释内数字不计为已填）
- **指标**：
  - 每 run：`has_any_score_2`
  - 全局：`batch_pass_rate`（有 ≥1 个 2 分的 run / 总 run）
  - `baseline_2_rate` vs `creative_2_rate`（missing 不参与分母；有 `triggered_by` 归创作桶，仅 baseline 归基线桶）
- **闸门**：≥60% batch pass **且** `baseline_2_rate < creative_2_rate` → `GATE_PASS`（exit 0），否则 `GATE_FAIL`（exit 1）

## 3. 本地验证结果 (Verification)

```powershell
cd t:\themoviecosmos-daily-stargazing
python scripts/summarize_eval.py tests/eval_fixtures/run-alpha.md tests/eval_fixtures/run-beta.md tests/eval_fixtures/run-gamma.md
python scripts/summarize_eval.py --dir tests/eval_fixtures --out output/eval_fixture_report.json
```

**手算 vs 脚本（3 fixture runs）：**

| 指标 | 手算 | 脚本 |
|------|------|------|
| runs with score-2 | 2/3 (alpha, beta) | 2/3 |
| batch pass rate | 66.7% | 66.7% |
| baseline_2_rate | 0/2 = 0% | 0.0% |
| creative_2_rate | 2/4 = 50% | 50.0% |
| missing | 1 (gamma baseline) | 1 |
| gate | PASS | GATE_PASS (exit 0) |

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 闸门 60% 阈值与 N=10 约定写死在脚本常量 `_GATE_BATCH_PASS_RATE`；扩样时需同步文档
- 评分归属依赖标题 agent 标签与 `also_baseline` 字段，与 `run_eval.py` 渲染契约一致
- Phase 3.3 评测手册将引用本 CLI 与 rubric
