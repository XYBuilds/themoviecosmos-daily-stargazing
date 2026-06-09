# Phase 3.10.4 - Judge Prescreen Orchestration 交付报告

## 1. 改动范围 (Scope)

- `scripts/judge_prescreen.py` — 新增 judge 预筛编排：全量打分（物理不删）、分档（0 降级 / ≥1 人工 / 2 高亮）、拒绝集 k% 抽审脚手架、阈值纪律（默认 `judge≥1`）与「零 human-2 被杀」核验报告位
- `tests/test_judge_prescreen.py` — 分档逻辑、可复现抽样、阈值安全断言（human=2 落在放行侧）
- `.cursor/plans/Phase3.10-logic-resonance-and-judge-prescreen.plan.md` — p310-4 标 complete

新增依赖：无

## 2. 技术实现 (Implementation)

- **`PrescreenConfig`**：参数化 `min_judge_score`（默认 1）、`rejection_sample_rate`（默认 10%）、`random_seed`、`threshold_frozen`
- **`classify_prescreen_bucket`**：`0→downgrade`，`1→manual`，`2→highlight`；`passes_threshold` 由 `min_judge_score` 决定人工复核队列
- **`sample_rejection_audit_keys`**：每 run 对 `judge=0` 堆可复现随机抽样；记录 `reweight_factor` 供下游诚实分母
- **`compute_threshold_safety`**：统计 human=2 在阈值放行侧留存与 killed 列表；产出 `threshold-safety-report.md` 冻结闸门位
- **CLI**：`python scripts/judge_prescreen.py --judge-json <eval>/llm-judge-scores.json` → `judge-prescreen.json` / `.md` / `threshold-safety-report.md`
- 集成：消费 `scripts/llm_judge.py` 的 `JudgeOutput` / `load_judge_output`，与 `run_phase39_judge_batch.py` 打分产物对接

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_judge_prescreen -v
# Ran 13 tests — OK

python scripts/judge_prescreen.py --judge-json output/Eval/phase3.9/llm-judge-scores.json
# buckets downgrade=87 manual=49 highlight=20
# threshold≥1 human2_killed=0 zero_killed=True
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 抽审回加权计入桶分母的统计消费留给 3.10.3 `summarize_eval.py`；本模块仅产出 `reweight_factor` 脚手架
- `threshold_frozen` 为标记位；实际 obs 冻结流程在 3.10.6 人工验收后执行
- 3.10.5+ 全链重跑时将把本 CLI 作为 holdout 预筛标准入口
