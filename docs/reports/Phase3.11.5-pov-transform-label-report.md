# Phase 3.11.5 - POV变换 共振子标签 交付报告

## 1. 改动范围 (Scope)

- `scripts/resonance_rubric.py` — `SUB_LABEL_POV_TRANSFORM`、`parse_pov_transform`、`validate_pov_transform_sub_label`
- `scripts/llm_judge.py` — judge schema v4、`pov_transform` 字段、rubric、review 集成
- `scripts/eval_editor_fields.py` — 人工打分占位行 `POV变换`
- `scripts/summarize_eval.py` — `CandidateScore.pov_transform` 解析与导出
- `scripts/judge_batch_parallel.py` — 并行打分行含 `judge_pov_transform`
- `prompts/_shared/resonance_definition_v2.md`、`docs/eval-the-bet.md` — 子标签口径
- `tests/test_pov_transform_label.py`（新增）
- `tests/test_llm_judge.py`、`tests/test_judge_batch_parallel.py` — 适配 5-tuple judge 返回

## 2. 技术实现 (Implementation)

- **2×2 矩阵不变**：`resonance_type` 仍仅取四种 canonical 类型；`POV变换` 为 score=2 时的可选布尔子标签。
- **Judge**：JSON 新增 `pov_transform: true|false`；schema version 升至 4；review 内联 `- **judge POV变换**: 是`。
- **人工**：`- **POV变换**: 是` 行；`append_resonance_editor_lines` 自动生成占位。
- **校验**：`validate_pov_transform_sub_label` 仅在 `score==2` 且 `resonance_type==强共振` 时允许 `true`。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_pov_transform_label -v
Ran 12 tests in 0.001s — OK
```

相关 judge 回归：`tests.test_llm_judge` 33 tests OK。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 存量 `llm-judge-scores.json`（version 3）无 `judge_pov_transform` 字段；`load_judge_output` 向后兼容（默认 `None`）。
- 3.11.6+ A/B 调优可开始统计 `POV变换` 分布；历史 eval 需人工补标才有完整分布。
