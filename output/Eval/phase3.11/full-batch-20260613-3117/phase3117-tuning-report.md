# Phase 3.11.7 Full-batch A/B 调优记录

- **Output dir**: `\\192.168.1.110\Hermes_Workspace\themoviecosmos-daily-stargazing\output\Eval\phase3.11\full-batch-20260613-3117`
- **Baseline dir**: `output\Eval\phase3.10`
- **Runs**: 10

## 1. A/B 池差总览

- baseline candidates: 190
- design candidates: 190
- net-new candidates: 102
- lost candidates: 102
- automated pass runs: 0 / 10
- guard hard failures: 0

## 2. search_unit_kind 分解

- any-kind counts: `{'event-fragment-bundle': 11, 'persona-semantic': 100, 'surface-fragment-bundle': 1}`
- exclusive counts: `{'event-fragment-bundle': 0, 'persona-semantic': 89, 'surface-fragment-bundle': 0}`
- collision gain count: 12
- collision gain tmdb_ids: `[1647, 20777, 28498, 30706, 47291, 53416, 56971, 68924, 248556, 382220, 720321, 1047128]`

## 3. 调优指南针

- persona net-new counts: `{'THE-INNOCENT': 17, 'THE-CAREGIVER': 15, 'THE-CREATOR': 15, 'THE-LOVER': 15, 'THE-EXPLORER': 14, 'THE-HERO': 12, 'THE-RULER': 12, 'THE-OUTLAW': 11, 'THE-MAGICIAN': 10, 'THE-EVERYMAN': 8, 'THE-JESTER': 8, 'THE-SAGE': 8}`
- center dimension net-new counts: `{'who': 47, 'result': 42, 'how': 28, 'why': 15, 'where': 1}`
- budget N: `{'per_run_human_budget': [19, 19, 19, 19, 19, 19, 19, 19, 19, 19], 'per_run_human_count': [19, 19, 19, 19, 19, 19, 19, 19, 19, 19], 'min_human_count': 19, 'max_human_count': 19}`

## 4. POV变换 分布

- human: `{'true': 0, 'false': 0, 'unknown': 110}`
- judge: `{'true': 2, 'false': 108, 'unknown': 0}`
- source: `output/Eval/phase3.11/full-batch-20260613-3117/llm-judge-scores.json`
- prompt_version: `3.11.7-mimo-v2.5-pro-thinking-disabled`
- run_metadata: `{'provider': 'mimo', 'request_options': {'max_completion_tokens': 1024, 'extra_body': {'thinking': {'type': 'disabled'}}}, 'thinking_mode': 'disabled', 'judge_condition_note': 'MiMo judge run with thinking disabled; not directly comparable to MiMo runs where thinking was enabled or unspecified.'}`

## 5. 拒绝集 / human-2 监控

- zero human-2 killed by judge_zero: True
- human-2 in judge_zero: `[]`
- human-2 missing from design review: `[{'run_id': '01-grid-outage', 'tmdb_ids': [431892]}, {'run_id': '02-corporate-layoff', 'tmdb_ids': [485162]}, {'run_id': '05-climate-disaster', 'tmdb_ids': [33196]}, {'run_id': '06-tech-monopoly', 'tmdb_ids': [13748]}, {'run_id': '08-sports-underdog', 'tmdb_ids': [248555]}]`
- note: judge_zero exists only when retrieve was run with judge_scores; missing_from_design_review is a review-pool retention warning, not final GATE裁决。

## 6. 人工抽审入口

- `high-hit-score-review.md`：统一候选抽审表，含 `POV变换` 人工字段。
- 每个 run 的 `pool-diff-search-unit-kind.json`：池差分解原始数据。
- 每个 run 的 `audit.json`：自动守卫与 pipeline 审计。
