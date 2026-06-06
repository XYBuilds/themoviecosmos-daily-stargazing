# Phase 3.9.4 - LLM-as-judge 交付报告

## 1. 改动范围 (Scope)

- `scripts/llm_judge.py` — 新增 LLM 共振评委：按 `docs/eval-the-bet.md` §4 打 0/1/2 + 共振类型；观察集（01–04）人工分校准；未达阈值标 **不采信**（仅初筛）
- `tests/test_llm_judge.py` — schema、校准指标、降级行为单测
- `tests/judge_fixtures/obs_calibration/high-hit-score-review.md` — 校准 fixture
- `.cursor/plans/Phase3.9-a1-oracle-per-persona-salience-three-bucket-eval.plan.md` — p39-4 标 complete

新增依赖：无（复用 `scripts/lib/llm.py` 与 `summarize_eval._pearson`）。

## 2. 技术实现 (Implementation)

- **`scripts/llm_judge.py`**
  - 从 `high-hit-score-review.md` 或各 run `candidates.md` 收集候选（新闻 + overview + 人工分）
  - LLM 返回 JSON：`score` / `resonance_type` / `rationale`；`validate_judge_payload` 硬校验 rubric 一致性（如 1→表层、2→结构/双重、0→无类型）
  - **校准**：观察集 run（`01-`–`04-`）上配对 judge vs 人工分，计算 `exact_agreement`、`within_one_agreement`、`pearson_r`
  - **阈值门**（默认）：`exact_agreement ≥ 0.60` 且 `pearson_r ≥ 0.50` 且 `n_pairs ≥ 5` → `trust_status=采信`；否则 `不采信` + `screening_only=true`，各候选 `trusted=false`
  - 输出：`llm-judge-scores.json` + `llm-judge-scores.md`（含分歧标记 ⚠）
  - CLI：`python scripts/llm_judge.py --eval-dir output/Eval/phase3.8`（`--calibrate-only` 可重放已有 JSON）

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_llm_judge -v
# Ran 10 tests — OK

python -m unittest discover -s tests -p "test_*.py"
# Ran 140 tests — OK (skipped=1)
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 校准阈值（0.60 / 0.50 / min 5 pairs）为 Phase 3.9 默认；3.9.7 批量前应在观察集实跑 LLM 后按数据微调
- 全量 judge 调用 LLM，成本与 3.9.7 批量编排相关；当前未接入 `run_persona_batch` 自动链
- `high-hit-score-review` 中带 backfill 内联的人工分（含 `（phase3.x）`）不参与校准配对
