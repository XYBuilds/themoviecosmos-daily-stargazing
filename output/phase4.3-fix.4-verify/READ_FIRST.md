# Phase 4.3-fix.4 MVP GATE 人工审核导航

> 说明：本文件只是人工肉眼审核导航页，不是交付报告；未做 Go/No-Go 判定。

## 使用的真实新闻
- 批次：`output/Eval/phase3.11/full-batch-20260613-3117/`
- 新闻目录：`01-grid-outage`
- 候选输入：`output/Eval/phase3.11/full-batch-20260613-3117/01-grid-outage/retrieve.json`
- Judge 分数：`output/Eval/phase3.11/full-batch-20260613-3117/llm-judge-scores-thinking-enabled.json`

## 决策卡产物
- JSON：`output/phase4.3-fix.4-verify/decision_card.json`
- Markdown：`output/phase4.3-fix.4-verify/decision_card.md`
- 运行结果：`judge filter: min_judge=1 kept=5 dropped=14`

## 模拟总编选片
- 选定电影：`Survival Family` / `サバイバルファミリー`（2017）
- TMDB ID：`429918`
- 选择理由：决策卡中 judge_score 最高为 2；本片为最高分组中的首个候选，且触发视角覆盖较多。

## 发布稿产物
- Markdown：`output/phase4.3-fix.4-verify/publish_draft.md`

## 运行命令清单（PowerShell）

```powershell
git branch --show-current
git status --short
python scripts/compose.py --help
python scripts/compose.py --stage review --retrieve-json "output/Eval/phase3.11/full-batch-20260613-3117/01-grid-outage/retrieve.json" --judge-scores "output/Eval/phase3.11/full-batch-20260613-3117/llm-judge-scores-thinking-enabled.json" --run-id "01-grid-outage" --out "output/phase4.3-fix.4-verify/decision_card.json" --md-out "output/phase4.3-fix.4-verify/decision_card.md"
python scripts/compose.py --stage publish --retrieve-json "output/Eval/phase3.11/full-batch-20260613-3117/01-grid-outage/retrieve.json" --judge-scores "output/Eval/phase3.11/full-batch-20260613-3117/llm-judge-scores-thinking-enabled.json" --run-id "01-grid-outage" --tmdb-id 429918 --out "output/phase4.3-fix.4-verify/publish_draft.md"
git status --short
```

## 审核提示
- 请先看 `decision_card.md`：确认是否满足“面向总编的选片决策卡”。
- 再看 `publish_draft.md`：确认是否满足“选定单片发布稿”。
- 本次只生成审核产物；验收通过后再由后续流水线处理 plan 状态、交付报告与合并。