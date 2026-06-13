# 失败粒度降到 pseudo 级、3.11 降维为「先跑通管线、候选质量后置」、容忍 replacement-over-additive

**Status**: accepted（追认 Phase 3.11.6–3.11.8 的执行口径；3.11.8 GATE go 2026-06-13）

> **本 ADR 的性质**：记账型。以下四条决策在 Phase 3.11.6b 降维讨论中拍板、并在 3.11.6/3.11.7/3.11.8 全程执行，原本只散落在临时决策记录（2026-06-11，已于本 ADR 落地后删除）与 [`docs/reports/Phase3.11.8-gate-result-report.md`](../reports/Phase3.11.8-gate-result-report.md) 中，从未进入任何 ADR。本 ADR 把它们钉成正式决策，使 ADR 序列与实际代码/闸门口径一致。
>
> 架构主线（fragment ladder / search unit）见 [ADR-0009](0009-fragment-ladder-and-search-unit-architecture.md)；本 ADR 只补它没覆盖的**执行纪律与失败处理**层面。

## 背景

ADR-0007 D6–D8 → ADR-0008 → ADR-0009 这条链负责生成/检索的**架构形态**。但 Phase 3.11.6 单点 pilot 暴露的真正阻塞不是架构，而是**概念与闸门过多**：12 persona 中只有 6/12 覆盖、6 个运行时守卫硬失败、focalized 通道 / 双地板 / baseline-lost 多重条件同时卡死，导致管线在「还没稳定产出物」之前就被一堆非核心验收项判 No-Go。

总编因此做出降维决定：把 3.11 近期目标从「验证 POV/focalized 是否有效」收敛为「先验证 element-centered 管线能否稳定跑通、进入全批数据阶段」。下列四条是这次降维的具体口径。

## 决策

### D1 · 失败粒度从 persona 降到 pseudo（「杀 pseudo 不杀 persona」）

| 条目 | 定稿 |
| --- | --- |
| **旧行为** | 单条 pseudo 违规 → 整个 persona pipeline 失败 → 该 persona `pseudos=[]`（一条坏 pseudo 拖垮整条创作路径，是 6/12 覆盖的主因） |
| **新行为** | 单条 pseudo 违规 → 只丢该条 → 保留同 persona 其余合法 pseudo → 只要剩 ≥1 条有效，该 persona 继续参与检索 |
| **覆盖的违规类型** | invented inner monologue / interiority、novel proper noun、supporting elements 超上限、非法 center / 非法 support、其他单条 pseudo 级事实守卫失败 |
| **非静默** | 丢弃必须记账，不得静默吞掉：记录 `kept_pseudos` / `dropped_pseudos` / `drop_reasons[{pseudo_id, reason}]` |

> 此口径与 ADR-0009 D4 的守卫清单是**互补**关系：D4 规定「什么算违规」，本 D1 规定「违规后丢多大粒度」。

### D2 · 3.11 跑通阶段只看管线指标，候选质量后置

| 条目 | 定稿 |
| --- | --- |
| **暂不阻塞** | net-new 是否 human=2、baseline 是否被替换、net-new 是否优于 baseline、who-centered 是否优于其他 center_kind、候选池主观质量 |
| **跑通阶段只看** | `persona_coverage`、`pseudo_survival_rate`、`valid_center_rate`、`drop_reasons`、retrieve 能否跑完、`pool_diff` 能否产出 |
| **Pipeline Go 条件** | 多数 persona 至少留 1 条有效 element-centered pseudo；所有保留 pseudo 的 center 来自 decon element ids；support_elements 可校验或可归一化；单条 pseudo 失败不拖垮 persona；retrieve 跑完；pool_diff 产出；drop_reasons 有记录 |
| **本质** | 先证明「链路能稳定产物、进入全批数据阶段」，不证明「3.11 效果好」。质量结论显式后移到 3.11.7/3.11.8 |

### D3 · 容忍 replacement-over-additive（暂不强制 additive）

| 条目 | 定稿 |
| --- | --- |
| **观察事实** | 3.11 pilot 呈现 replacement 特征而非严格 additive（典型一轮：baseline 19 / design 19 / overlap 9 / net-new 10 / lost 10），与 ADR-0007 D7「POV 纯增召回、锁死匹配地板」的原始期待**偏离** |
| **本轮口径** | 不把 `lost baseline candidates` 当 No-Go；改为只记录 `overlap_count` / `net_new_count` / `lost_count` / `net_new_by_center_kind` / `lost_from_baseline` |
| **遗留到质量评估阶段再定** | 是否恢复 additive 口径；是否扩预算保 baseline；是否接受 replacement 作为产品策略 |
| **3.11.8 实际结果** | net-new 2-rate 15.9% ≥ baseline retained 13.6%，replacement 未损精度，GATE 据此放行；**但仍有 5 条 baseline human-2 因新 convergent sort 落出预算（非 judge-kill）**，登记为已知债 |

### D4 · 已知技术债（GATE go 时显式记录、未清）

- **baseline human-2 落出**：5 条 baseline 强共振候选被新排序挤出 top-N 预算（非守卫拒绝、非 judge 拒绝）。可经 `baseline_overlap` retention floor 调优恢复；非阻塞，留待 Phase 4 前后处理。
- **judge 仍为 `screening-only`（不采信为真值）**：3.11.8 GATE 依据 judge proxy 放行，人工打分尚未覆盖净新增候选。接 RSS（Phase 5）新分布前须补人工校准（与 ADR-0007 D4 阈值纪律、分布漂移条目一致）。

## 为什么

1. **杀 pseudo 不杀 persona**：把 persona 覆盖率从生成质量的人质中解放出来——一条坏 pseudo 不该让一整条创作视角在检索里消失。这是 6/12 → 接近 12/12 覆盖的直接杠杆。
2. **管线优先、质量后置**：3.8/3.9/3.11.0 反复栽在「一次验证太多、分不清谁起作用」。先拿到稳定产物与干净 pool_diff，质量判断才有可信分母。
3. **容忍 replacement**：与其为「保住每一条 baseline」在没跑通时就加约束，不如先放行、用 3.11.7/3.11.8 的真实 A/B 数据决定要不要把 additive 拉回来。

## 后果 / 已知局限

- **drop 记账带来产物字段膨胀**：pseudo 级 drop_reasons 进入每轮 audit，是可接受的诊断成本。
- **replacement 容忍是一次性豁免**：D3 只对 3.11 评测期有效；产品化（Phase 4/5）前必须就「additive vs replacement」给最终口径，否则 baseline 流失会变成隐性回归。
- **D4 两项债未清即放行**：GATE go 是「架构调优收敛」的裁决，不等于质量验收完成；judge 未采信 + baseline 落出都需在进入呈现层/生产前回头处理。

## 相关 ADR / 文档

- [ADR-0009](0009-fragment-ladder-and-search-unit-architecture.md) — fragment ladder / search unit 架构；本 ADR 补其失败粒度与执行纪律。
- [ADR-0008](0008-salience-driven-element-composition-and-multi-vantage-pov.md) — 元素中心构图；D2 跑通门以 element-centered pseudo 为主身份。
- [ADR-0007](0007-logic-resonance-judge-prescreen-and-pov-focalization.md) — 双轴 rubric 与 judge 预筛；本 ADR D3/D4 与其 D7 additive 期待、D4 阈值纪律对账。
- 本 ADR 四条决策的原始临时记录（`docs/temp/phase3.11-element-centered-pipeline-decision.md`）已在落地后删除，内容全部收编进本文档。
- [`docs/reports/Phase3.11.8-gate-result-report.md`](../reports/Phase3.11.8-gate-result-report.md) — GATE go 裁决与 D4 技术债来源。