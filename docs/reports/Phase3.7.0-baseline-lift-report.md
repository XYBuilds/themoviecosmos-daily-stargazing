# Phase 3.7.0 - baseline 增量统计 交付报告

## 1. 改动范围 (Scope)

- `scripts/analyze_baseline_lift.py`（新）：解析 `output/Eval/phase3.6/*/candidates.md`，按 baseline-only / creative-only / both 分桶，计算 2 分率与 Go/No-Go
- `tests/test_analyze_baseline_lift.py`（新）：分桶逻辑 + mini fixture 单测
- `tests/eval_fixtures/baseline_lift/`（新）：mini 分桶 fixture
- `output/Eval/phase3.7/baseline-lift.md`（新）：Phase 3.6 数据锚点与 **No-Go** 结论
- `.cursor/plans/Phase3.7-persona-resonance.plan.md`：3.7.0 todo 标 complete，注明 No-Go 暂停后续

无新增依赖包。

## 2. 技术实现 (Implementation)

- 复用 `scripts/summarize_eval.py` 的 `parse_eval_markdown` / `_collect_paths` 解析 `also_baseline`、heading agents、`共振分`
- 分桶规则：
  - **baseline-only**：`also_baseline=true` 且无 A2/A4/A7
  - **creative-only**：有 A2/A4/A7 且 `also_baseline=false`
  - **both**：A1 与 creative 同时命中
- Go/No-Go 主判据：**creative-only 2 分率 − baseline-only 2 分率** > 0 → Go；否则 No-Go（both 桶仅作对照，不驱动 verdict）

## 3. 本地验证结果 (Verification)

```text
python scripts/analyze_baseline_lift.py --dir output/Eval/phase3.6
# exit code 1 (No-Go)
# Wrote output/Eval/phase3.7/baseline-lift.md

python -m unittest tests.test_analyze_baseline_lift -v
# Ran 5 tests ... OK
```

**Phase 3.6 锚点数字（57 条已打分候选 / 10 runs）：**

| Bucket | Scored | 2-point rate |
| --- | ---: | ---: |
| baseline-only (A1) | 8 | 37.5% |
| creative-only (A2/A4/A7) | 42 | 9.5% |
| both | 7 | 71.4% |

- **Lift (creative-only − baseline-only): −28.0%**
- **Verdict: No-Go** — 当前注入式 creative 相对 A1 中性无正向 2 分增量；建议暂停 3.7.1+ 直至重审 steering 方向

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 118 条候选缺 `共振分`（主要为 08–10 留出集及部分 06–07），未纳入率计算；后续 3.7.4 重跑后样本会变化
- **both** 桶 71.4% 2 分率显示 A1+creative 共现时质量高，但无法隔离 creative 独立贡献；Phase 3.7 persona 设计需避免把 A1 信号误归因给情绪 steering
- No-Go 按 plan 依赖图应阻断 3.7.1；若用户仍想探索 persona 重构，需显式 override 本锚点
