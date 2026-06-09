# Phase 3.10.6 - Judge recalibration + threshold freeze 交付报告

## 1. 改动范围 (Scope)

- `scripts/run_phase39_judge_batch.py` — 修复 checkpoint replay 时 `causal_test` 四元组回放
- `output/Eval/phase3.10-judge-calibration/llm-judge-scores.json` / `.md` — obs 65 对 v2 双轴 judge 全量打分 + 校准
- `output/Eval/phase3.10-judge-calibration/judge-prescreen.json` / `.md` — 预筛分档（冻结 `judge≥1`）
- `output/Eval/phase3.10-judge-calibration/threshold-safety-report.md` — 零 human-2 被杀核验
- `docs/eval-phase3.10-holdout-freeze-discipline.md` — holdout 冻结纪律 SSOT
- `output/Eval/phase3.10/holdout-freeze-discipline.md` — eval 侧镜像
- `.cursor/plans/Phase3.10-logic-resonance-and-judge-prescreen.plan.md` — p310-6 标 complete
- 新增/删除的依赖包：无

**分支：** `feat/phase3.10.6-judge-recalibration-threshold-freeze`（基于 `main` @ 3.10.5 merge）

## 2. 技术实现 (Implementation)

### obs judge 重校准（v2 鲜标）

- 输入：`output/Eval/phase3.10/obs-fresh-labels.json` + `high-hit-score-review.md`（obs 01–04，65 对）
- 命令：`python scripts/run_phase39_judge_batch.py --eval-dir output/Eval/phase3.10 --obs-only`
- Rubric：`scripts/llm_judge.py` v3 双轴（`resonance_definition_v2.md`）

| 指标 | 值 | 阈值 |
| --- | --- | --- |
| n_pairs | 65 | ≥ 5 |
| exact_agreement | **0.585** | ≥ 0.60 |
| within_one_agreement | **0.954** | — |
| pearson_r | **0.411** | ≥ 0.50 |
| **trust_status** | **不采信** | screening_only=true |

校准未达 exact/pearson 门 → `trusted=false` / `screening_only=true`。Judge 分仍保留用于预筛分档；工作流侧「校准采信」留待 3.10.8 GATE 裁决。

### 阈值冻结（用户 approve despite 不采信）

- 预筛：`python scripts/judge_prescreen.py --judge-json output/Eval/phase3.10-judge-calibration/llm-judge-scores.json --min-judge-score 1 --threshold-frozen`
- obs 安全核验：

| 指标 | 值 |
| --- | --- |
| n_human_two | 9 |
| n_human_two_killed | **0** |
| pass_side_human_two_retention | **100%** |
| workload_reduction_rate | **21.5%**（obs only） |
| prescreen buckets | downgrade=14 · manual=37 · highlight=14 |
| **Verdict** | **SAFE TO FREEZE** |

**冻结常量：** `min_judge_score=1`，`threshold_frozen=true`，rubric v3 双轴；holdout 05–10 一次性打分，禁止再调参。

## 3. 本地验证结果 (Verification)

```text
python scripts/run_phase39_judge_batch.py --eval-dir output/Eval/phase3.10 --obs-only
# → 65 obs pairs scored; calibration written

python scripts/judge_prescreen.py \
  --judge-json output/Eval/phase3.10-judge-calibration/llm-judge-scores.json \
  --min-judge-score 1 --threshold-frozen
# → human2_killed=0 zero_killed=True
```

User approved threshold freeze **despite screening_only calibration** → cleared for **3.10.7** holdout prescreen.

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **校准不采信但阈值已冻** — 用户显式 approve；3.10.8 GATE 须诚实标注工作流侧「校准采信」可能 no-go。
- **obs 减负率仅 21.5%** — 低于 D5 ~50% 目标；holdout 全量后复检。
- **holdout 纪律** — 05–10 须在冻结 prompt + `judge≥1` 下一次性 judge；禁止用 holdout 调阈值。
- **3.10.7 next** — holdout 预筛 + 人工复核 `judge≥1` + 拒绝集抽审 + combo vs pure_fact 复检基线。

**Go/No-Go:** User approved freeze → ready for **3.10.7**.
