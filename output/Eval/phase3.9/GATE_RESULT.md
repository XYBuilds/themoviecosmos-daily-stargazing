# Phase 3.9 · GATE 结论（Q1′/Q2/Q3 + 闸门 1 · ADR-0006 D5）

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

## Q1′ · 12 neutral n1 能否兜住 A1 人工 2 分（gate）

**问题（用户确认 · ADR D5）**：12 条 neutral `n1` 命中 union 能否覆盖全部 **A1_two**（A1 命中且人工共振分=2）？

**口径（per run）**：

- `A1_hit` ← `retrieve-a1.json` → `a1_oracle.hit_tmdb_ids`（fallback：`a1-baseline-meta.json`）
- `A1_two` = { tmdb_id ∈ A1_hit | 该 (run_id, tmdb_id) 在 review 中 **共振分=2** }
- `N` = `retrieve.json` `per_agent` 中 `role=neutral` 且 `pseudo_id=n1` 的命中 union（**非**候选池 neutral_union）
- **PASS（per run）**：`A1_two ⊆ N`（`A1_two` 空 → vacuous pass）
- **批次规则**：所有 **|A1_two|>0** 的 run 均 pass 才建议通过

### 批次汇总

| 指标 | 值 |
| --- | --- |
| 全批 A1_two（人工 2 分） | **10** 部（跨 8 runs） |
| \|A1_two\|>0 的 run 数 | **8** |
| per-run Q1′ 通过 | **6/8**（75%） |
| 全局 miss（A1_two ∖ N） | **2** |
| **Q1′ 批次判** | **FAIL** |

### 全局 miss 列表

| run_id | tmdb_id | 片名 |
| --- | --- | --- |
| 02-corporate-layoff | 209504 | Bounty Killer |
| 06-tech-monopoly | 320318 | The Clearstream Affair |

### per-run 明细

| run_id | A1_hit | A1_two | n1 union | misses | Q1′ |
| --- | --- | --- | --- | --- | --- |
| 01-grid-outage | 3 | 1 | 7 | 0 | ✓ |
| 02-corporate-layoff | 4 | 2 | 9 | 1 | ✗ |
| 03-election-upset | 3 | 2 | 7 | 0 | ✓ |
| 04-celebrity-scandal | 6 | 0 | 9 | 0 | ✓ (vacuous) |
| 05-climate-disaster | 5 | 1 | 16 | 0 | ✓ |
| 06-tech-monopoly | 5 | 1 | 12 | 1 | ✗ |
| 07-migration-border | 6 | 1 | 6 | 0 | ✓ |
| 08-sports-underdog | 4 | 1 | 12 | 0 | ✓ |
| 09-cultural-backlash | 5 | 1 | 16 | 0 | ✓ |
| 10-whistleblower-leak | 4 | 0 | 16 | 0 | ✓ (vacuous) |

**Q1′ 总判：FAIL** · `a1_deletion_eligible = false`（2 部人工认定的 A1 强共振未被任何 persona 的 neutral n1 召回）

---

## 诊断 / legacy · 旧 Q1 口径（非 gate fail）

> 全量 A1 superset 与 neutral 2-rate ≥ A1 **仅作诊断**，不参与 Q1′ gate。

### legacy 召回（候选池 neutral union ⊇ 全 A1_hit）

| 指标 | 值 |
| --- | --- |
| 全批 A1 唯一命中 | 44 tmdb_id |
| 候选池 neutral union 唯一命中 | 55 tmdb_id |
| A1 未被 neutral union 覆盖 | **22** |
| per-run superset 通过 | **1/10**（仅 `03-election-upset`） |

### legacy 质量（结构/双重 2 分率 · 已打分子集）

| 路径 | structural 2-rate | scored |
| --- | --- | --- |
| A1 命中候选（tmdb ∈ a1_hit） | **38.5%** | 26 |
| 中性 union 命中候选 | **24.1%** | 54 |

**legacy 诊断**：全量 superset 仍差（22 misses）；质量 neutral union 低于 A1（−14.4pp）。Q1′ 收窄到人工 2 分后 miss 仅 2 部，但批次规则仍不通过。

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
| **Q1′** 中性 n1 兜 A1 人工 2 分 | **FAIL** | 6/8 runs with A1_two pass；2 global misses（209504, 320318） |
| **Q2** 组合拳 | **机械 PASS / 效力弱** | combo 26% > pure_fact 0%（n=4）；holdout combo 18% ≪ obs 41% |
| **Q3** 情绪净加分 | **弱 PASS** | pure_emotion 不拖累；combo 有汇聚增量 |
| **闸门 1** | **PASS** | 90% batch |

### 总裁决（preliminary）

**GATE no-go（组合拳未成立）**

- **非** Q1′&Q2 双成立 → 不进入「组合拳成立」路径
- **非** 仅 Q1′ 成立 → 中性 n1 未完整兜住人工认定的 A1 强共振（2 misses）
- 对齐 ADR D5：**回 3.9.1/3.9.6 调 salience/契约，或启用 D6 plan B**；**不升 SSOT、不删 A1**
- `summarize_eval` 机械 `GATE_PASS`（Q2 combo>pure_fact + batch 90%）与产品裁决 **不一致** — 以本文件 Q1′ fail + Q2 小样本 + obs/holdout 裂口为准

### 一行摘要

**GATE no-go** — Q1′ fail（6/8；2 A1_two misses）；legacy superset 1/10；Q2 机械 pass 但 pure_fact n=4；holdout combo 2-rate 18% vs obs 41%；judge **采信**；人工 152/156。

---

## `[需人工验收]`

总编确认本 GATE 结论后输入 `approve` 再标 plan p39-8 complete / 写 3.9.8 report / 合并。
