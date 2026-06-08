# Phase 3.9 · GATE 结论（Q1/Q2/Q3 + 闸门 1 · ADR-0006 D5）

- **日期**: 2026-06-09
- **分支**: `feat/phase3.9.8-gate-result`（基于 `main` @ e5f2d9b，3.9.7 已合并）
- **数据源**:
  - `output/Eval/phase3.9/high-hit-score-review.md`（review SSOT；152 scored / 156 high-hit）
  - `output/Eval/phase3.9/batch-run-summary.json`（10 run × 12 persona + A1 并跑）
  - 各 run `retrieve.json` + `a1-baseline-meta.json` + `retrieve-a1.json`
  - `output/Eval/phase3.9/gate-diagnostics.json`（`scripts/summarize_eval.py`）
  - `output/Eval/phase3.9/llm-judge-scores.json`（judge 校准 · obs 01–04）
  - `output/Eval/phase3.9/holdout-freeze-discipline.md`
- **ADR-0006**: [docs/adr/0006-a1-as-held-out-oracle-per-persona-neutral-and-three-bucket-eval.md](../../docs/adr/0006-a1-as-held-out-oracle-per-persona-neutral-and-three-bucket-eval.md)
- **3.8 基线**: [output/Eval/phase3.8/GATE_RESULT.md](../phase3.8/GATE_RESULT.md)

## 打分覆盖（Coverage）

| 集合 | run_id | 已打分候选 | 备注 |
| --- | --- | --- | --- |
| 观察集 obs | 01–04 | 61 scored（4 missing） | missing 均在 `03-election-upset` |
| 留出集 holdout | 05–10 | 91 scored | 0 missing |
| manifest 全批 | 10 runs | **152 scored / 156 high-hit** | 覆盖率 97.4% |

人工共振分分布（152 已填）：0 → 87，1 → 36，2 → 29。

### LLM judge 校准（obs · 冻结后）

| 指标 | 值 | 阈值 |
| --- | --- | --- |
| n_pairs | 61 | ≥ 5 |
| exact_agreement | **0.639** | ≥ 0.60 |
| pearson_r | **0.743** | ≥ 0.50 |
| within_one | 1.000 | — |
| **trust_status** | **采信** | screening_only=false |

---

## Q1 · 中性腿是否站起来（vs A1 oracle）

**通过条件（ADR D5）**：per-persona 中性 union 召回 ⊇ A1 命中 **且** 结构/双重 2 分率 ≥ A1（oracle 对照）。

> **口径**：`a1_hit_tmdb_ids` ← `a1-baseline-meta.json`；中性 union ← `retrieve.json` 候选 `neutral_hits > 0`（非 `retrieve-a1.json` 内空 union）。

### 召回（superset）

| 指标 | 值 |
| --- | --- |
| 全批 A1 唯一命中 | 44 tmdb_id |
| 中性 union 唯一命中 | 55 tmdb_id |
| A1 未被中性 union 覆盖 | **22** |
| per-run superset 通过 | **1/10**（仅 `03-election-upset`） |

| run_id | A1 hits | neutral union | A1-only misses | superset |
| --- | --- | --- | --- | --- |
| 01-grid-outage | 3 | 4 | 1 | ✗ |
| 02-corporate-layoff | 4 | 5 | 2 | ✗ |
| 03-election-upset | 3 | 5 | 0 | ✓ |
| 04-celebrity-scandal | 6 | 5 | 4 | ✗ |
| 05-climate-disaster | 5 | 4 | 3 | ✗ |
| 06-tech-monopoly | 5 | 7 | 2 | ✗ |
| 07-migration-border | 6 | 6 | 3 | ✗ |
| 08-sports-underdog | 4 | 6 | 1 | ✗ |
| 09-cultural-backlash | 5 | 7 | 4 | ✗ |
| 10-whistleblower-leak | 4 | 6 | 3 | ✗ |

**Q1 召回：FAIL** — 中性 union 未 ⊇ A1（22 misses；仅 1/10 run 通过）。

### 质量（结构/双重 2 分率 · 已打分子集）

| 路径 | structural 2-rate | scored |
| --- | --- | --- |
| A1 命中候选（tmdb ∈ a1_hit） | **38.5%** | 26 |
| 中性 union 命中候选 | **24.1%** | 54 |

**Q1 质量：FAIL** — 中性 union 桶结构 2 分率 **低于** A1 命中桶（−14.4pp）。

**Q1 总判：FAIL** · `a1_deletion_eligible = false`

---

## Q2 · 组合拳是否成立（组合桶 vs 纯事实桶 · 控相似度）

**通过条件**：组合桶(③) 结构/双重 2 分率 **显著 >** 纯事实桶(①)，控 `max_similarity` 后仍成立。

| 桶 | 结构/双重 2 分率 | scored | structural 2s |
| --- | --- | --- | --- |
| **pure_fact**（① 纯事实） | **0.0%** | 4 | 0 |
| **pure_emotion**（② 纯情绪） | 16.3% | 98 | 16 |
| **combo**（③ 组合） | **26.0%** | 50 | 13 |

控相似度（sim≥0.50 bin）：combo **31.6%** (12/38) vs pure_fact **0.0%** (0/3)。

`summarize_eval` `q2_combo_lift_ok`: **true**（combo > pure_fact）。

**Q2 机械判：PASS** — 组合桶高于纯事实桶。

**效力 caveat**：纯事实桶仅 **4** 条可打分样本（较 3.8 的 0 有改善，但仍极小）；「显著」统计效力不足。高 sim bin 内 pure_fact n=3。

---

## Q3 · 情绪是否净加分（汇聚 vs 漂移）

| 对比 | 结构/双重 2 分率 |
| --- | --- |
| pure_fact | 0.0% |
| pure_emotion | 16.3% |
| combo | 26.0% |

- 纯情绪桶 **未拖累**（16.3% > 0% pure_fact）。
- 组合相对纯事实增量 **+26.0pp**；相对纯情绪 **+9.7pp** — 增量更多来自「中性+toned 汇聚」形态，而非纯情绪漂移 alone。

**Q3：PASS（弱）** — 无「纯情绪拖累」证据；汇聚形态有增量，但受 Q2 小样本约束。

---

## 闸门 1 · batch pass rate（≥60% runs 含 ≥1 个 2 分候选）

| 口径 | pass rate | 明细 |
| --- | --- | --- |
| manifest 10 run | **90.0%** (9/10) | **PASS** |
| obs 01–04 | 100% (4/4) | — |
| holdout 05–10 | 83.3% (5/6) | — |

无 2 分 run：`10-whistleblower-leak`。

**闸门 1：PASS**

---

## obs vs holdout 一致性（过拟合检验）

| 指标 | obs (01–04) | holdout (05–10) | Δ |
| --- | --- | --- | --- |
| batch pass rate | 100% | 83.3% | −16.7pp |
| combo structural 2-rate | **41.2%** | **18.2%** | **−23.0pp** |
| pure_emotion structural 2-rate | 20.9% | 12.7% | −8.2pp |
| diagnostic① partial r (nhr\|sim) | 0.265 | 0.175 | −0.09 |

**一致性：弱 / 有 overfit 信号** — holdout combo 结构 2 分率约为 obs 的一半；须在总裁决中降权 Q2 机械 PASS。

---

## 诊断 ① · neutral_hit_rate ↔ 共振（控 max_similarity）

| 指标 | 值 |
| --- | --- |
| n | 152 |
| 偏相关 r(nhr, score \| similarity) | **0.218** |
| 高 sim bin (≥0.50) | n=132, r=0.262 |

**结论：弱正相关** — 与 3.8 (r≈0.17) 同量级，中性广度仍非强排序主轴。

---

## 产品裁决（ADR-0006 D5）

| 子问 | 结果 | 依据 |
| --- | --- | --- |
| **Q1** 中性腿 | **FAIL** | superset 1/10；A1 2-rate 38.5% > neutral union 24.1% |
| **Q2** 组合拳 | **机械 PASS / 效力弱** | combo 26% > pure_fact 0%（n=4）；holdout combo 18% ≪ obs 41% |
| **Q3** 情绪净加分 | **弱 PASS** | pure_emotion 不拖累；combo 有汇聚增量 |
| **闸门 1** | **PASS** | 90% batch |

### 总裁决（preliminary）

**GATE no-go（组合拳未成立）**

- **非** Q1&Q2 双成立 → 不进入「组合拳成立」路径
- **非** 仅 Q1 成立 → 中性腿未站起来
- 对齐 ADR D5：**回 3.9.1/3.9.6 调 salience/契约，或启用 D6 plan B**；**不升 SSOT、不删 A1**
- `summarize_eval` 机械 `GATE_PASS`（Q2 combo>pure_fact + batch 90%）与产品裁决 **不一致** — 以本文件 Q1 fail + Q2 小样本 + obs/holdout 裂口为准

### 一行摘要

**GATE no-go** — Q1 fail（22 A1 misses；质量 −14pp）；Q2 机械 pass 但 pure_fact n=4；holdout combo 2-rate 18% vs obs 41%；judge **采信**；人工 152/156。

---

## `[需人工验收]`

总编确认本 GATE 结论后输入 `approve` 再标 plan p39-8 complete / 写 3.9.8 report / 合并。
