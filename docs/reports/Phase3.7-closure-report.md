# Phase 3.7 - 12 原型情绪扩散 结案报告

**状态**: **GATE_FAIL · 结案于 2026-06-05**  
**用户决策**: **No-Go** — 跳过 3.7.6 SSOT 迁移；后续迭代暂缓

## 执行摘要

Phase 3.7 假设：以 **12 个 Pearson persona（人格原型）作为 A1 的情绪扩散** 替代 inject 式 An（A2/A4/A7）——从事实可支撑的 alt-pool（备选池）中完成选择与语气调整，不引入新事件。本阶段完成了完整脚手架、12 张 persona 卡片、N=10 批量运行，以及 persona 与 baseline（基线）的门控对比。**脚本闸门未支持该假设**：在部分编辑评分（4/10 次运行）下，persona 路径的结构化/双 2 分率为 **20%**，A1 路径为 **75%**（**提升 −55%**）。批量通过率 **50%**（低于 60% 阈值）。用户接受 **GATE_FAIL** 并结案，未进行 SSOT 迁移。

**体感与正式闸门分层**：总编审稿体验上，Phase 3.7 相对 3.6 inject 时代**提升很大**；但正式 `GATE_FAIL` 裁决仍基于 structural 2-rate 与 batch 50% 阈值（见下文「门控口径复盘」）。二者不矛盾——闸门度量的是 head-to-head 路径对比，均分视角则支持「整体大幅优于 3.6」。

## 各 TODO 交付物

| Todo | 结果 | 关键产物 |
| --- | --- | --- |
| **3.7.0** baseline lift（基线提升） | **No-Go**（历史锚点） | `output/Eval/phase3.7/baseline-lift.md` — 基于 phase3.6 数据，creative 相对 A1 提升 −28% |
| **3.7.1** ADR + roster（名册） | Complete | `docs/adr/0004-persona-emotional-diffusion.md`, `docs/SSOT/personas-12.md`, holdout 划分 01–04 obs / 05–10 |
| **3.7.2** scaffold（脚手架） | Complete | `scripts/personas.py`, alt-creator/screenwriter 合约, `tests/test_personas.py` |
| **3.7.3** Ruler pilot（标尺试点） | **Go** | `04-celebrity-scandal` 端到端；steering/fit/P-Select 已验证 |
| **3.7.4** 12 personas × N=10 | Complete（部分评分） | `output/Eval/phase3.7/{run_id}/`, `high-hit-score-review.md`；已评分运行 **01, 02, 07, 09** |
| **3.7.5** gate analysis（门控分析） | **GATE_FAIL** | `scripts/summarize_eval.py` persona_vs_baseline；[`GATE_RESULT.md`](../output/Eval/phase3.7/GATE_RESULT.md) |
| **3.7.6** SSOT migration（SSOT 迁移） | **Skipped** | PRD / CONTEXT / 合约未变更；ADR-0004 保持 **proposed** |

## 门控证据（3.7.5）

详见 [`output/Eval/phase3.7/GATE_RESULT.md`](../output/Eval/phase3.7/GATE_RESULT.md)。

1. **fit（适配度）↔ resonance（共鸣）**: 弱相关（r ≈ 0.14）；低 fit 行很少达到 2 分 — abstain（弃权）阈值尚未定稿
2. **persona vs A1**: persona 路径在结构化/双 2 分率上较 A1 低 55 个百分点；与 3.7.0 No-Go 结论一致
3. **fit × similarity（相似度）**: 可行的下游分流轴；2 分候选集中在上层 fit×sim 区间

**覆盖度说明**: 150 个 high-hit 候选中仅 62 个已评分，覆盖 4/10 次运行。聚焦子集（01+02+07+09）批量通过率 100%，但不足以推翻全批量 GATE_FAIL 结论。

## 门控口径复盘

> ¹ 本节回应 2026-06 总编与 agent 关于门控口径的对话（「A1 路径 75% 怎么来的」「闸门能否反映体感」）。

### A. 闸门指标说明（回应「A1 路径 75%」）

**75% = 9/12**，不是 9/62。

| 指标 | 分子 | 分母 | 结果 | 回答的问题 |
| --- | --- | --- | --- | --- |
| **A1 path structural 2-rate** | 9（结构/双重 2 分） | 12（已打分且 `also_baseline=true`） | **75.0%** | A1 retrieve 也命中的电影里，结构共鸣 2 分占比 |
| **Persona path structural 2-rate** | 10 | 50（已打分且 `also_baseline=false`） | **20.0%** | persona-exclusive 候选里，结构共鸣 2 分占比 |
| **全批 A1 structural 占比**（不同问题） | 9 | 62（全批已打分） | **≈14.5%** | 所有已填电影里 A1 路径 structural 2 的份额 |

计算逻辑见 `scripts/summarize_eval.py` 中 `_persona_bucket_rates`：按 `also_baseline` 将已打分候选划入 **A1 path**（`true`）或 **Persona path**（`false`），再各自统计 structural/dual 2 分率。完整闸门输出见 [`output/Eval/phase3.7/GATE_RESULT.md`](../output/Eval/phase3.7/GATE_RESULT.md) 第 2 节。

```306:335:scripts/summarize_eval.py
    """Baseline vs persona structural/total 2-rates (Phase 3.7 gate 2).

    Gate comparison uses ``also_baseline`` (A1 retrieve path) vs persona-exclusive
    hits — matches retrieve semantics when review scores are mostly multi-agent.
    ...
            path_row = a1_path if cand.also_baseline else persona_path
            path_row["scored"] += 1
            if cand.score == 2:
                path_row["twos"] += 1
                if _is_structural_resonance(cand):
                    path_row["structural_twos"] += 1
```

### B. 闸门设计的局限

1. **cohort 不对称**：A1 path（n=12）≈ agent-heading 的 **both** 桶（A1 与 persona 共命中）；Persona path（n=50）= persona-exclusive，其中含 **37 个 single-agent** 候选，拉低 structural 2-rate。
2. **structural 2-rate 把 1 分与 0 分等同**：Persona path 有 **21 个 1 分**（「有共鸣但不够 2」）被闸门完全忽略；A1 path 仅 2 个 1 分。
3. **本批 0 个 pure baseline-only 被评分**：A1 路径实际测的是「共命中」子集，而非独立 A1-only 检索质量。
4. **收窄 Persona 分母后的敏感性**：若 Persona 分母收窄为 **multi-agent only**（约 13 部），structural 2-rate 约 **38%**（5/13），仍低于 A1 的 75%，但 lift 从 **−55%** 缩至约 **−37%**。

### C. 补充指标：已填电影平均分

总编提议：用「所有已填写电影的平均分」衡量整体体感。基于 `high-hit-score-review.md` 中 **62 部已打分**候选（与 `summarize_eval.py` 解析一致）：

| 口径 | n | 平均分 | 备注 |
| --- | --- | --- | --- |
| Phase 3.7 全批已填 | 62 | **0.98** | vs 3.6 **0.58**（**+0.40**） |
| A1 path | 12 | 1.67 | `also_baseline=true` |
| Persona path | 50 | 0.82 | 含大量 single-agent |
| multi-agent | 25 | **1.80** | **高于** A1 共命中 1.67 |
| Phase 3.6 对照 | 57 | 0.58 | inject 式 creative 时代 |

**解读**：正式 `GATE_FAIL` 主要来自 structural 2-rate head-to-head（20% vs 75%）+ batch 50%。**平均分视角支持「相对 3.6 整体大幅提升」**，更贴近总编体感；multi-agent 子集（1.80）甚至略高于 A1 共命中子集（1.67），提示 persona steering 在「多 agent 共识」候选上表现更好，但被 single-agent 长尾稀释。

### D. 结案立场（定稿）

| 维度 | 结论 |
| --- | --- |
| **正式裁决** | **GATE_FAIL · No-Go · 跳过 3.7.6**（不变） |
| **体感与证据** | 脚本闸门未过，但审稿体验与均分/多 agent 指标显示 3.7 相对 3.6 inject 时代**显著提升** |
| **下一轮迭代** | **在 3.7 已交付的脚手架/管线基础上继续**，而非推倒重来：`personas.py`、12 cards、batch runner、`high-hit-score-review` 工作流均可复用 |

建议后续重设闸门指标（均分 / multi-agent cohort）、补全 holdout 评分、重跑 34 失败格后再做新一轮门控。

## 未完成事项

- **3.7.6**: 未更新 PRD / `CONTEXT.md` / `reality-deconstruction-contract.md`
- **ADR-0004**: 未晋升为 `accepted`
- **Phase 4**: 仍受门控阻塞
- **完整 holdout 评分**: 运行 05–06、08、10 未评分；obs 03–04 未评分

## 建议的后续迭代切入点

1. **在 3.7 脚手架/管线基础上迭代** — 保留 `personas.py`、12 cards、batch runner、`high-hit-score-review` 工作流；重设闸门（建议纳入均分、multi-agent cohort）；补全 holdout 评分后重跑门控
2. **重试 34 个失败批量单元** — alt-creator 缺少 valence bucket 错误（`batch-run-summary.json`）；使用 `--no-skip-existing` 重新运行
3. **完成 holdout 评分** — 按 ADR 纪律至少对 05–10 评分后再重新门控；避免在 01–04 上过拟合
4. **合约调优** — screenwriter 选择规则、alt-creator 谱系质量、persona 专属弱 fit 处理（Lover/Innocent 行评分为 0–1）
5. **P-Abstain 阈值** — 仅在低 fit + holdout 标签充足后设定；当前 n=3 样本过小

## 报告索引

| 报告 | 路径 |
| --- | --- |
| 3.7.0 baseline lift | `docs/reports/Phase3.7.0-baseline-lift-report.md` |
| 3.7.1 ADR + personas | `docs/reports/Phase3.7.1-adr-personas-report.md` |
| 3.7.2 scaffold | `docs/reports/Phase3.7.2-persona-scaffold-report.md` |
| 3.7.3 Ruler pilot | `docs/reports/Phase3.7.3-ruler-04-pilot-report.md` |
| 3.7.5 gate analysis | `docs/reports/Phase3.7.5-gate-fit-analysis-report.md` |
| **结案（本文档）** | `docs/reports/Phase3.7-closure-report.md` |

## Git / 合并

- PR #26 已合并至 `main`（feat/phase3.7.5-gate-fit-analysis）
- 合并后结案文档已提交至 `main`
