# Phase 3.8 · GATE 结论（双诊断 + A1-superset）

- **日期**: 2026-06-06
- **分支**: `feat/phase3.8.8-gate-result`（基于 `main` @ df8c967，3.8.7 已合并）
- **数据源**:
  - `output/Eval/phase3.8/high-hit-score-review.md`（review SSOT；`01-grid-outage-rerun` **不计入** manifest 闸门）
  - `output/Eval/phase3.8/batch-run-summary.json`（3.8.7 批量 10 run + A1 并跑）
  - 各 run `retrieve.json` + `retrieve-a1.json` + `a1-baseline-meta.json`
  - `scripts/summarize_eval.py` → `output/Eval/phase3.8/gate-diagnostics.json`
- **ADR-0005**: [docs/adr/0005-objective-extraction-neutral-channel-and-collision-vote.md](../../docs/adr/0005-objective-extraction-neutral-channel-and-collision-vote.md)
- **3.7 基线**: [output/Eval/phase3.7/GATE_RESULT.md](../phase3.7/GATE_RESULT.md)

## 打分覆盖（Coverage）

| 集合 | run_id | 已打分候选 | 备注 |
| --- | --- | --- | --- |
| 观察集 obs | 01–04 | ✓ 部分已填 | 04 无 2 分候选 |
| 留出集 holdout | 05–10 | ✓ 已填 | 满足 3.8.7 ≥2 条留出要求 |
| manifest 全批 | 10 runs | **155 scored / 174 high-hit** | 19 条未填分；`01-grid-outage-rerun` 排除 |

---

## 1. 诊断 ① · neutral_hit_rate ↔ 共振（控 max_similarity）

**问题（ADR-0005）**：中性「广度」是不是真信号？

| 指标 | 值 | 解读 |
| --- | --- | --- |
| n（有 neutral_hit_rate 且已打分） | 67 | `summarize_eval` 解析行 |
| Pearson(neutral_hit_rate, 共振分) | **0.173** | 弱正相关 |
| 偏相关 r(nhr, score \| similarity) | **0.172** | 控相似度后仍弱 |
| 高相似度 bin (sim≥0.50) | n=64, r=**0.185** | 主质量落在高 sim 区 |

**结论：① 弱** — 控 `max_similarity` 后，neutral_hit_rate 与共振分仅有弱正相关（r≈0.17），略高于 3.7 的 fit↔共振 r≈0.14，但远未达到「强信号」门槛。中性广度**不能**单独作为产品排序主轴；仍须与相似度、toned 汇聚联读。

> 纪律提醒（ADR-0005）：未控相似度前不得把 neutral_hit_rate 当结论；本报告以偏相关为主口径。

---

## 2. 诊断 ② · toned-convergence ↔ 共振（控 max_similarity）

**问题（ADR-0005）**：lens 在中性之上是否加了精度？

| 桶 | 结构/双重 2 分率 | scored | structural 2s |
| --- | --- | --- | --- |
| **quality_candidate**（中性票 + ≥1 toned） | **62.5%** | 16 | 10 |
| neutral-only（有中性票、无 toned 汇聚） | — | **0** | 0 |
| 单 agent / 非 quality | **10.8%** | 139 | 15 |
| 偏相关 r(toned, score \| similarity) | null | — | 中性票行全进入 quality 桶，无法偏相关 |

`multi-agent-neutral-hits-review.md` 筛出 **17** 条「多 agent + neutral_hits>0」优质形态候选，与 quality 桶高度重合。

**结论：② 弱 / 不可分离** — 在已打分样本中，凡 `neutral_hits≥1` 的候选**全部**同时为 `quality_candidate`（neutral-only 可打分样本 = 0），无法做 ADR 定义的「toned 精度 − neutral-only」对照。侧面证据：quality 62.5% **远高于** 非 quality 10.8%，说明**撞车形态**（中性 + toned 汇聚）与高分强相关，但 toned 的**独立增量**未获干净证伪/证实。

---

## 3. 闸门 1 · batch pass rate（≥60% runs 含 ≥1 个 2 分候选）

| 口径 | pass rate | 明细 |
| --- | --- | --- |
| manifest 10 run（排除 rerun） | **80.0%** (8/10) | **PASS** |
| 含 `01-grid-outage-rerun` | 81.8% (9/11) | 参考 |

无 2 分 run：`04-celebrity-scandal`、`10-whistleblower-leak`。

**闸门 1：PASS**

---

## 4. 闸门 2 · quality vs neutral-only（结构/双重 2 分率 + 诊断 ②）

| 指标 | 值 |
| --- | --- |
| quality structural 2-rate | **64.7%** (11/17) — `summarize_eval` 全 review 含 rerun |
| manifest quality structural 2-rate | **62.5%** (10/16) |
| neutral-only structural 2-rate | **0%** (0/0) — 无对照样本 |
| `precision_lift_ok`（脚本） | true（vacuous） |

**闸门 2（机械）**：`summarize_eval` 报 **PASS**（quality > neutral-only），但 neutral-only 分母为 0，**统计效力不足**。

**闸门 2（实质）**：quality 路径 62.5% 显著高于单 agent 10.8%，但**不能**归因于 toned 独立贡献。

---

## 5. A1-superset 验证（3.8.7 并跑 · 删 A1 前置）

对照各 run `a1-baseline-meta.json` 的 `a1_hit_tmdb_ids` 与 `retrieve.json` 中性通道 union 命中：

| 指标 | 值 |
| --- | --- |
| 全批 A1 唯一命中 | 44 tmdb_id |
| 中性 union 唯一命中 | 26 tmdb_id |
| **中性 union ⊇ A1？** | **否** — 31 个 A1 命中未被中性 union 覆盖 |
| per-run superset 通过 | **1/10**（仅 `02-corporate-layoff`） |
| 失败 run | 01, 03, 04, 05, 06, 07, 08, 09, 10 |

已打分候选结构/双重 2 分率对照：

| 路径 | structural 2-rate | scored |
| --- | --- | --- |
| A1 命中候选（tmdb ∈ a1_hit） | **60.0%** | 20 |
| quality_candidate | **62.5%** | 16 |
| neutral union 命中候选 | **62.5%** | 16 |

**A1 可删？→ 否** — superset 闸**未过**（`a1_deletion_eligible = false`）。quality 2 分率虽略高于 A1 命中桶（+2.5pp），但**召回不覆盖** A1，不满足 ADR-0005「中性 union 取代 A1」的删除条件。

---

## 6. 产品裁决（ADR-0005 §两诊断）

| 诊断 | 强度 | 依据 |
| --- | --- | --- |
| ① neutral 广度 | **弱** | 偏相关 r≈0.17（控 sim） |
| ② toned 精度 | **弱 / 不可分离** | neutral-only 可打分 n=0；quality vs 单 agent 差距大但混杂 |

**裁决：①弱 ②弱 → 产品 no-go（persona 赌注未成立）**

- **不是** ①强②弱（中性召回 + 命中率排序）— ① 未达「强」
- **不是** ①&②双强（persona 赌注成立）
- **不执行** 3.8.9（SSOT 终态 / 删 A1）；ADR-0005 保持 `proposed`

若未来继续迭代，优先方向：提升中性通道对 A1 的召回覆盖（superset），并补「仅中性票、无 toned」可打分对照样本以分离诊断 ②。

---

## 7. 对比 Phase 3.7 GATE_FAIL 基线

| 指标 | Phase 3.7 | Phase 3.8 | Δ |
| --- | --- | --- | --- |
| batch pass rate | 50% (5/10) | **80%** (8/10) | **+30pp** |
| 主路径 structural 2-rate | persona path **20%** (10/50) | quality path **62.5%** (10/16) | **+42.5pp** |
| vs A1 path structural 2-rate | A1 **75%** (9/12) | A1 命中桶 **60%** (12/20) | 仍低于 3.7 A1 桶 |
| 相关探针 | fit↔共振 r≈**0.14** | nhr↔共振 r≈**0.17**（控 sim） | 边际改善 |
| A1 superset | n/a | **FAIL** (31 misses) | 新增硬闸未过 |

**解读**：3.8 相对 3.7 在 batch 通过率与 quality 路径命中率上**显著改善**（中性通道 + hypernym 锚 + 撞车新形状有效），但整体 **GATE no-go** — ①② 双诊断未达产品门槛，且 **A1 不能被中性 union 替代**。

---

## 8. 综合闸门裁决

| 子闸 | 结果 |
| --- | --- |
| 闸门 1（batch ≥60%） | **PASS** |
| 闸门 2（quality > neutral-only + ②） | **PASS（机械）/ 效力不足（实质）** |
| A1-superset | **FAIL** |
| ADR-0005 产品两诊断 | **①弱 ②弱** |
| `summarize_eval` 脚本 | `GATE_PASS`（未含 A1-superset） |

### 总裁决：**GATE no-go**

- **不推进** 3.8.9（SSOT accepted、删 A1）
- **建议回** 3.8.2 / 3.8.6：中性召回覆盖、锚点契约、neutral-only 对照可评性
- **保留** 3.8 管线成果（三分通道、撞车新口径、batch 基础设施）供下一轮调参

### 一行摘要

**GATE no-go** — batch 80% & quality 62.5% beat 3.7, but diagnostic ①② weak, A1-superset FAIL (31 misses); do not delete A1.
