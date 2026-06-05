# Phase 3.7 - 12 原型情绪扩散 结案报告

**状态**: **GATE_FAIL · 结案于 2026-06-05**  
**用户决策**: **No-Go** — 跳过 3.7.6 SSOT 迁移；后续迭代暂缓

## 执行摘要

Phase 3.7 假设：以 **12 个 Pearson persona（人格原型）作为 A1 的情绪扩散** 替代 inject 式 An（A2/A4/A7）——从事实可支撑的 alt-pool（备选池）中完成选择与语气调整，不引入新事件。本阶段完成了完整脚手架、12 张 persona 卡片、N=10 批量运行，以及 persona 与 baseline（基线）的门控对比。**证据未支持该假设**：在部分编辑评分（4/10 次运行）下，persona 路径的结构化/双 2 分率为 **20%**，A1 路径为 **75%**（**提升 −55%**）。批量通过率 **50%**（低于 60% 阈值）。用户接受 **GATE_FAIL** 并结案，未进行 SSOT 迁移。

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

## 未完成事项

- **3.7.6**: 未更新 PRD / `CONTEXT.md` / `reality-deconstruction-contract.md`
- **ADR-0004**: 未晋升为 `accepted`
- **Phase 4**: 仍受门控阻塞
- **完整 holdout 评分**: 运行 05–06、08、10 未评分；obs 03–04 未评分

## 建议的后续迭代切入点

1. **重试 34 个失败批量单元** — alt-creator 缺少 valence bucket 错误（`batch-run-summary.json`）；使用 `--no-skip-existing` 重新运行
2. **完成 holdout 评分** — 按 ADR 纪律至少对 05–10 评分后再重新门控；避免在 01–04 上过拟合
3. **合约调优** — 若重新审视 persona steering：screenwriter 选择规则、alt-creator 谱系质量、persona 专属弱 fit 处理（Lover/Innocent 行评分为 0–1）
4. **P-Abstain 阈值** — 仅在低 fit + holdout 标签充足后设定；当前 n=3 样本过小
5. **替代方向** — 3.7.0 已表明 inject 式 creative 不及 A1；下一假设可能需要不同于仅靠 valence alt-pool 的 steering 机制

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
