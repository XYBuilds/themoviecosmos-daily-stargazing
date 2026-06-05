# Phase 3.7 · GATE 结论（persona resonance）

- **日期**: 2026-06-05
- **数据源**: `//192.168.1.110/Hermes_Workspace/themoviecosmos-daily-stargazing/output/Eval/phase3.7/high-hit-score-review.md`（review SSOT；per-run `candidates.md` 已移除）
- **3.7.0 锚点**: `//192.168.1.110/Hermes_Workspace/themoviecosmos-daily-stargazing/output/Eval/phase3.7/baseline-lift.md` — Phase 3.6 注入式 creative vs A1 **No-Go**（lift −28%）
- **summarize_eval**: `persona_vs_baseline` · `GATE_FAIL`

## 打分覆盖（Coverage）

| 集合 | run_id | 已打分候选 | 备注 |
| --- | --- | --- | --- |
| 观察集 obs | 01, 02 | ✓ 总编已填 | 03–04 未填 |
| 留出集 holdout | 07, 09 | ✓ 总编已填 | 05–06, 08, 10 未填 |
| 全批 | 10 runs | 62 scored / 150 high-hit | 闸门用已填分候选 |

## 1. fit ↔ 共振（P-Abstain 探针）

- **已打分行（全批）**: n=62；Pearson(max_fit, 共振分) ≈ 0.13860319153618253
- **Focus 子集（01, 02, 07, 09）**: n=61；r ≈ 0.12156649685941782
- **低 fit (<0.55) 命中结构/双重 2 分**: 0/3 （支持暂不硬编码弃权）

趋势（focus 四条）：高 fit 与 2 分/双重共现多于低 fit；Lover 低 fit 行多 0–1 分。**P-Abstain 阈值留待补全留出集后定稿**.

## 2. persona steering vs A1（闸门 2 · 呼应 3.7.0）

| 指标 | 全批已打分 | 01+02+07+09 focus |
| --- | --- | --- |
| batch pass rate | 50.0% (5/10 runs) | 100.0% |
| A1 path structural 2-rate (also_baseline=true) | 75.0% (9/12) | 72.7% |
| persona path structural 2-rate (also_baseline=false) | 20.0% (10/50) | 20.0% |
| lift (persona path − A1 path) | -55.0% | -52.7% |

- **对比 3.7.0**：3.6 注入式 creative **低于** A1；本批 persona path（`also_baseline=false`）结构/双重 2 分率 **未高于** A1 path（`also_baseline=true`）桶 — 与 3.7 赌注反向（A1 仍占优），**batch 闸门未过**且仅 4/10 run 已打分.

## 3. fit × 相似度（候选排序/过滤）

下游建议：按 `fit_sim_score = max_fit × 相似度` 降序 triage（`summarize_eval` JSON `fit_sim_ranking`）。2 分候选多落在 fit×sim 上半区；0–1 分尾部可优先压人工体量.

## 4. 闸门裁决

- **脚本闸门**: **GATE_FAIL**
  - batch pass rate 50.0% < 60% (5/10 runs with >=1 score-2)
  - persona_path_structural_2_rate 20.0% not > a1_path_structural_2_rate 75.0%
- **3.7.6 SSOT 迁移**: **No-Go（跳过 3.7.6）**
- **`[需人工验收]`**：总编确认本文件结论后输入 `approve` 再标 plan complete / 写 3.7.5 report。

### 一行摘要

**GATE_FAIL** — persona structural lift -55.0% on scored subset; batch 50%; coverage 4/10 runs.
