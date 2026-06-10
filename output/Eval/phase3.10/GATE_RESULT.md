# Phase 3.10 · GATE 结论（ADR-0007 D5 双轴 + 预筛工作流）

- **日期**: 2026-06-10
- **分支**: `feat/phase3.10.8-gate-result`（基于 `main` @ def2379，PR #56 已合并）
- **主数据源（NAS-safe）**: `output/Eval/phase3.10-visible/`
- **镜像说明**: 本文件同时写入 `output/Eval/phase3.10/GATE_RESULT.md`；评测 SSOT 以 **phase3.10-visible** 为准（`phase3.10/` 为开发期镜像，部分脚本默认 `--prescreen-json` 指向后者——同步时需显式传 visible 路径）。
- **ADR-0007**: [docs/adr/0007-logic-resonance-judge-prescreen-and-pov-focalization.md](../../docs/adr/0007-logic-resonance-judge-prescreen-and-pov-focalization.md)
- **3.9 结案**: [output/Eval/phase3.9/GATE_RESULT.md](../phase3.9/GATE_RESULT.md)（legacy · no-go）

## 打分覆盖（Coverage）

| 集合 | run_id | 已打分候选 | 人工标注 | 备注 |
| --- | --- | --- | --- | --- |
| 观察集 obs | 01–04 | 65 | **65 / 65** | obs-fresh-labels 满标 |
| 留出集 holdout | 05–10 | 91 | 58（全批 optional） | prescreen 强制池 **28 / 28** |
| manifest 全批 | 10 runs | **156** judge-scored | **123** human-labeled | 覆盖率 78.8%（obs 满标 + holdout 预筛池满标） |

人工共振分分布（123 已填）：0 → 94，1 → 20，2 → 9（新双轴定义 · 与 3.9 legacy **不可比**）。

### 拒绝集抽审（rejection audit · holdout）

| 指标 | 值 |
| --- | --- |
| prescreen 强制池 | **28**（21 manual judge≥1 + 7 rejection audit） |
| 池内人工标注 | **28 / 28**（含 `08-sports-underdog` / tmdb `232679` → human=1） |
| audit 样本 human=2 | **0** |
| 零误杀（reject pile） | **YES** |

---

## D5 · 共振侧：combo > pure_fact（新双轴 · 控相似度 · obs/holdout 不裂口）

**口径**：结构/双重 2 分率（`structural_2_rate`）；预筛抽审样本按 `reweight_factor` 回加权（`prescreen_reweighted=true`）。

### 全批（reweighted · GATE 主口径）

| 桶 | structural 2-rate | scored | structural 2s |
| --- | --- | --- | --- |
| **pure_fact**（① 纯事实） | **0.0%** | 1 | 0 |
| **pure_emotion**（② 纯情绪） | 5.6% | 62 (eff.wt 179) | — |
| **combo**（③ 组合） | **11.5%** | 25 (eff.wt 61) | 7 |

控相似度（sim≥0.50 high bin）：combo **23.3%** (7/30 eff.) vs pure_fact **0.0%** (0/1)。

`summarize_eval` `combo_gt_pure_fact`: **true** · `obs_holdout_consistent`: **true**

### 原始已打分子集（未回加权 · 诊断）

| 桶 | structural 2-rate | scored |
| --- | --- | --- |
| pure_fact | 0.0% | 1 |
| combo | **17.5%** | 40 |

**效力 caveat**：pure_fact 仅 **1** 条可打分样本（较 3.9 的 4 更差）；「显著」统计效力不足。机械 lift 依赖「combo>0 且 pure_fact=0」的 vacuous 情形。

### obs vs holdout 一致性

| 切片 | combo struct. 2-rate (raw) | combo n | pure_fact n | combo>pure? |
| --- | --- | --- | --- | --- |
| **obs** 01–04 | **22.2%** | 18 | 1 | ✓ |
| **holdout** 05–10 | **13.6%** | 22 | 0 | ✓ (vacuous) |
| **Δ** | −8.6pp | — | — | 同向（均 true） |

reweighted：obs combo **9.1%** (n=17) · holdout combo **17.6%** (n=8) — 方向与 3.9（obs 41% vs holdout 18% 裂口）**不同**，本次 **不裂口**。

**共振侧机械判：PASS（弱）** — combo>pure_fact 在 obs/holdout 均成立；绝对 2 分率偏低；pure_fact n=1。

---

## D5 · 工作流侧：预筛减负 + 零 human-2 误杀 + judge 校准

### 阈值安全（judge≥1 · frozen · 3.10.1b logic 0-guard 后）

| 切片 | n_human_two | n_human_two_killed | workload_reduction |
| --- | --- | --- | --- |
| **全批 156** | 19 | **0** | **42.3%** |
| **obs 01–04** | 9 | **0** | 23.1% |
| **holdout 05–10** | 10 | **0** | **63.8%** |

- `zero_human_two_killed`: **YES**（obs 冻结验证 + holdout 抽审 28/28 无 human=2 落入 judge=0 堆）
- 预筛分档（156）：downgrade **85** · manual **45** · highlight **26**
- human=2 留存：19/19 = **100%**

### LLM judge 校准（obs 01–04 · 新双轴鲜标）

| 指标 | 值 | 阈值 |
| --- | --- | --- |
| n_pairs | 65 | ≥ 5 |
| exact_agreement | **0.585** | ≥ 0.60 |
| pearson_r | **0.411** | ≥ 0.50 |
| within_one | 0.954 | — |
| **trust_status** | **不采信** | screening_only=**true** |

**3.10.7 总编裁决**：judge 角色 = **预筛 only**（`screening_only` 接受；校准不达标 **不阻塞** 预筛上线，但 **不得** 将 judge 分当共振真值）。

### 3.10.1b logic 0-guard 影响（pilot 05/06）

- prompt `3.10.1b-logic-0-guard`：Axis 2 追加反测/0-guard → judge=0 堆膨胀（05: 3→9 个 0；06: 4→17 个 0）
- 效果：预筛 **更保守**（holdout 减负 ↑），校准 **更难**（exact/pearson 下降）
- 与 D4 铁律一致：**靠抽审监控误杀，不靠调高门槛控量**

### 工作流机械判（`summarize_eval` D5）

| 子项 | 结果 | 说明 |
| --- | --- | --- |
| 零 human-2 误杀 | **PASS** | killed=0 |
| 减负 ~50%+ | **FAIL（全批）** | 42.3% < 50%；holdout 63.8% 达标 |
| judge 校准采信 | **FAIL** | 用户 **豁免**（screening_only） |

**工作流侧产品判：PASS（条件）** — 安全成立 + 预筛 approved；全批减负未达 ADR 50% 目标；校准不采信已备案。

---

## A1 · 只读参照（诊断 · 非闸）

> ADR-0007 D5：Q1′ 删除闸已砍；以下 **不参与** GATE pass/fail。

### Q1′ 覆盖（新定义人工 2 分 · 诊断）

| 指标 | 值 |
| --- | --- |
| \|A1_two\|>0 的 run | 5 |
| per-run Q1′ 通过 | **5/5** |
| global miss | **0** |
| **诊断结论** | 新定义下 neutral n1 **覆盖**全部 A1 人工 2 分（与 3.9 2-miss 不同 — **定义不可比**） |

### legacy 质量（A1 vs neutral union · 诊断）

| 路径 | structural 2-rate | scored |
| --- | --- | --- |
| A1 命中候选 | 见 `holdout-prescreen-baseline.json` `a1_reference` | — |
| 批次 pass rate（≥1 个 2 分 run） | **80%** (8/10) | — |

---

## obs / holdout 汇总表

| 指标 | obs (01–04) | holdout (05–10) | 全批 |
| --- | --- | --- | --- |
| 人工标注 | 65/65 | 58（池 28/28） | 123 |
| human=2 | 9 | 10 | 19 |
| human=2 killed | 0 | 0 | 0 |
| workload_reduction | 23.1% | **63.8%** | **42.3%** |
| combo struct. 2-rate (raw) | 22.2% | 13.6% | 17.5% |
| combo>pure_fact | ✓ | ✓ | ✓ |
| batch pass (≥1 个 2 分) | 4/4 | 4/6 | 8/10 |

---

## 产品裁决（ADR-0007 D5 → Phase 3.11）

| 子问 | 机械结果 | 产品权重 |
| --- | --- | --- |
| **共振侧** combo>pure_fact + 不裂口 | **PASS（弱）** | pure_fact n=1；绝对率偏低 |
| **工作流侧** 零误杀 + 减负 + 校准 | **PARTIAL** | 误杀✓；全批减负 42%<50%；校准不采信（已豁免） |
| **3.10 POV-off 基线** | **可用** | 可作 3.11 对照臂 |
| **ADR D1–D5** | **条件接受** | 见下 |

### 总裁决

**GATE · conditional go（条件通过 → 可启动 Phase 3.11 POV-on）**

**理由（go）**

1. 新双轴定义下 **combo>pure_fact** 在 obs/holdout **同向成立**，无 3.9 式 overfit 裂口。
2. 预筛 **零 human-2 误杀**；拒绝集抽审池 **28/28** 满标；`232679` audit 为 human=1 / judge=0（安全）。
3. 总编已接受 **screening_only**：judge 仅作预筛，校准不达标 **不阻塞** 工作流。
4. holdout 减负 **63.8%** 证明预筛在评测主战场有效；全批 42.3% 受 obs 满标（低减负）拉低。

**条件（honest caveats）**

1. **全批减负 42.3% < ADR ~50%** — 3.11 漏斗（D8）须继续吸收候选膨胀，不靠调高 judge 门槛。
2. **pure_fact n=1** — 组合拳 lift 统计效力不足；不以绝对 2 分率与 3.8/3.9 legacy 比较。
3. **judge_calibration_trusted=False** — 预筛可用，judge 分 **不得** 写入 SSOT 或替代人工共振裁决。
4. **3.10.1b logic 0-guard** 使 judge 更严 — 持续用拒绝集抽审监控；接 RSS（Phase 5）须重测分布。

**非 go 路径**：若总编否决 conditional go → 回 3.10.1b 调 rubric/阈值或扩 obs 校准集，**不升** POV（3.11）。

### 一行摘要

**conditional go** — 共振机械 pass（弱；combo 11.5% vs pure 0%）；工作流安全 pass + screening_only；全批减负 42%；holdout 64%；校准不采信；池 28/28；human 123/156。

---

## ADR-0007 状态

| 决策 | GATE 后状态 |
| --- | --- |
| D1 双轴定义 | **accepted**（conditional） |
| D2 新基线起算 | **accepted** |
| D3 分两步 / 3.10 POV-off | **accepted** — 基线已产出 |
| D4 judge 预筛 | **accepted（screening_only）** — 校准不采信 |
| D5 成功标准 + 砍 Q1′ | **accepted（conditional go）** |
| D6–D8 POV | **pending** → Phase 3.11 |

> 本 ADR `Status: proposed` → 总编 **approve** 本 GATE 后由维护者改为 `accepted`（D1–D5）。

---

## `[需人工验收]`

总编确认本 GATE **conditional go** 裁决后输入 `approve`，再执行：标 plan p310-8 complete · 写 3.10.8 report · **合并 PR** · 启动 Phase 3.11。
