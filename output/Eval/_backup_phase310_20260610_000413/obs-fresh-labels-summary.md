# Phase 3.10.5 · obs 01–04 新定义鲜标摘要

- **eval_phase**: 3.10
- **rubric**: 双轴 v2（`docs/eval-the-bet.md` §4 / `prompts/_shared/resonance_definition_v2.md`）
- **observation runs**: `01-grid-outage`, `02-corporate-layoff`, `03-election-upset`, `04-celebrity-scandal`
- **labeled candidates**: 65（high-hit review 中 obs 段全部填分，无 missing）
- **holdout 05–10**: 未填分（留给 3.10.7）

## 共振分分布（obs 鲜标）

| 分 | 数量 |
| --- | --- |
| 0 | 22 |
| 1 | 34 |
| 2 | 9 |

## 产物路径

| 路径 | 说明 |
| --- | --- |
| `output/Eval/phase3.10/{run_id}/` | 10 条新闻全链产物（自 phase3.9 promote，生成侧未改） |
| `output/Eval/phase3.10/batch-run-summary.json` | 批次摘要 |
| `output/Eval/phase3.10/high-hit-score-review.md` | 统一 review（obs 已鲜标） |
| `output/Eval/phase3.10/obs-fresh-labels.json` | 鲜标审计 JSON（含 causal_test / remark） |

## 人工验收要点

1. 抽查 obs 鲜标是否符合双轴定义（尤其 0 分守门、因果反测句）
2. 确认未参考 phase3.9 旧分（remark 均标 `v2 fresh`）
3. holdout 段仍为占位，未提前填分
