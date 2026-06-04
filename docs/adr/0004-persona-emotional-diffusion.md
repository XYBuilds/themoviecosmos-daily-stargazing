# 12 原型情绪化扩散：从注入式 An 到 A1 的情绪滤镜

**Status**: proposed

> **背景**：Phase 3.6 `GATE_FAIL（发布）`；总编复盘见 `output/Eval/phase3.6/high-hit-score-review.md`。A1（忠实复述）是最强单一信号；当前 A2/A4/A7 靠 prompt 级 **Inject**（虚构关联、神话化、微因果发明）在样本外产生流畅伪关联（如 Dead Mail）。本 ADR 记录 Phase 3.7 的赌注：**12 Pearson 原型 = A1 的情绪化扩散**——只从现实里 **Select + 重配语气**，不注入新事实。
>
> **3.7.0 锚点（No-Go，用户 override）**：`output/Eval/phase3.7/baseline-lift.md` 显示 creative-only 2 分率 9.5% vs baseline-only 37.5%，lift **−28.0%** → 脚本结论 **No-Go**。用户以 **`continue`** 覆盖暂停，**仍推进 3.7.1+**；本 Phase 须在留出集上独立验证 persona 相对 A1 中性基线的增量（闸门 2），不得用 3.6 注入式 An 结论替代。

## 决策（判据与闸门 · 实现须一致）

| 代号 | 定稿 |
| --- | --- |
| **P-Source** | **A0 只拆解，不产任何替代词（含中性）**。全部替代词由 **per-persona alt-creator** 自产：每 element 生成 **正向–中性–负面整条 spectrum**，再按本 persona 偏好取舍 |
| **P-Select** | alt-creator / screenwriter 只能 **Select + 重配语气**，**禁 Inject 事件**。spectrum 上每个替换词必须 **事实蕴含**（可从中性 decon，尤其 `who.relations` / `why` / `how` 推出）；可激进推正/负价值（如 rumor spreader ✓）；**禁 fact-additive**（如 foreign agent / convicted criminal ✗） |
| **P-SSOT** | **1 份中性 decon** = 单一事实源；每 persona 仅产出 **alt-pool overlay**（引用同一 element/fragment id）。**不 fork 12 份全文** |
| **P-Tone** | screenwriter 可调措辞/语域/语气（如 secured a warrant → moved to restore order），但 **不得新增人物/因果/事件** |
| **P-Force** | **强迫生产 + 不硬弃权**：被运行的 persona 都产出 pseudo；每 pseudo 附 **`fit` 自评（0–1）**；过滤交给下游 `fit × 相似度`，不在上游硬丢 |
| **P-Abstain** | 是否加弃权阈值 = **留出集打分后用数据决定**（低 fit 是否从不命中 2 分）；本 Phase 不硬编码 |
| **P-Match** | 匹配不变：pseudo prose ↔ overview embedding。A1（中性拼接、无 alternatives）= 干净消融基线 |
| **P-Cost** | 表达强度优先：alt-creator 每 persona 专属（成本经测可忽略） |

### 闸门

| 闸门 | 定稿 |
| --- | --- |
| **闸门 1** | 保留：≥60% 批次至少 1 个 2 分候选（必要下限，证明力弱） |
| **闸门 2（Phase 3.7 新）** | persona 候选的结构/双重 2 分率 **>** **A1 中性基线**（验证情绪 steering 增量；须同跑 A1） |

## 12 原型 roster

权威清单见 [`docs/SSOT/personas-12.md`](../SSOT/personas-12.md)（与 `docs/temp/12原型视角、追求与双面设定集.md` 对齐）。`persona_id` 与 `prompts/personas/<persona_id>/` 目录名一致。

Pilot 首卡：**The-Ruler**（`04-celebrity-scandal`）。

## 评测留出集纪律

防止观察集规律被样本外推翻（Phase 3.6 已演示过拟合）：

| 集合 | `tests/eval_news/` run_id | 用途 |
| --- | --- | --- |
| **观察集** | `01`–`07` | 开发、契约迭代、pilot 调试；总编可选填分 |
| **留出集** | `08`–`10` | **仅在此填共振分**做 3.7.4/3.7.5 闸门与 P-Abstain 判定；不在观察集上自证 |

与现有 N=10 打分目录一致；`run_eval` 输出写 `output/Eval/phase3.7/{run_id}/`，**只读** `phase3.5` / `phase3.6`。

## 共振 rubric（与 eval-the-bet 对齐）

- 产品验收目标统一为 **关联 / 共振**（表层 + 结构 + 双重），见 `docs/eval-the-bet.md` §4。
- **反讽 / 讽刺 / 荒诞落差** 等仅作为 **结构性或双重共振的子类**，不单列为 prompt 或闸门要「追求」的独立目标（Jester 等 persona 仍可在 tone 上偏荒诞，但不改变 rubric 主目标）。

## 为什么（相对 Phase 3.6 An）

1. **A1 信号强**：含 A1 候选共振均值远高于纯创作 An（复盘）。
2. **Inject 代价高**：流畅伪关联（伪分高、共振 0）是人工审核最贵错误。
3. **赌注**：在保住 A1「对题」前提下，用 12 情绪滤镜做 **可审计的** 价值重配（alt-pool + P-Select），替代不可审计的注入。

## 后果 / 已知局限

- **3.7.0 No-Go 仍成立为历史锚**；继续推进是 **显式产品赌注**，须在 3.7.5 `GATE_RESULT.md` 用 persona vs A1 重新裁决。
- **小样本**：留出集仅 3 条；结论按 per-candidate 对照，必要时扩样。
- **P-Select 边界**：alt-creator 是唯一注入风险点；契约 + pilot 人工双重核查。
- **不解封 Phase 4**；**不改 PRD/CONTEXT/contract** 直至 3.7.5 GATE go → 3.7.6。
- **SSOT 待改清单（3.7.6 · GATE go 后）**：`reality-deconstruction-contract.md`（alternatives/overlay）；`PRD` / `CONTEXT.md`（12 原型、An 退场、`fit`、闸门 2）；本 ADR `Status` → `accepted`。

## 相关 ADR / 文档

- [ADR-0002](0002-pivot-to-event-logic-resonance.md) — 表层合法、事件逻辑解构
- [ADR-0003](0003-multi-agent-resonance-quality-and-a1-as-peer.md) — A1 平权、优质候选（闸门口径待 3.7.5 接 persona_vs_baseline）
- [`docs/eval-the-bet.md`](../eval-the-bet.md) §4 / §5.1 — 共振 rubric（3.7.1 去「讽刺/反讽」为独立目标）
- [`output/Eval/phase3.7/baseline-lift.md`](../../output/Eval/phase3.7/baseline-lift.md) — 3.7.0 数字锚
