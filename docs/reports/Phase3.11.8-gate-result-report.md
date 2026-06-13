# Phase 3.11.8 - GATE Result 交付报告

## 1. 改动范围 (Scope)

- `output/Eval/phase3.11/GATE_RESULT.md` — 新增 GATE 裁决文档
- `docs/adr/0009-fragment-ladder-and-search-unit-architecture.md` — Status: proposed → accepted
- `docs/adr/0008-salience-driven-element-composition-and-multi-vantage-pov.md` — Status: proposed → accepted
- `.cursor/plans/Phase3.11-pov-focalization-additive.plan.md` — p311-8 status → completed

无新增/删除依赖包。

## 2. 技术实现 (Implementation)

GATE 3.11.8 是 Phase 3.11 的终审裁决节点，基于 3.11.7 全批 A/B 数据产出四条指南针口径判定：

| 口径 | 证据 | 判定 |
|------|------|------|
| ① 池差净新增 human-2 > 0 | 7 条 net-new judge=2 (2-rate 15.9%) | PASS |
| ② 精度不崩 | net-new 15.9% ≥ baseline retained 13.6% | PASS |
| ③ 守卫零硬失败 | 0/10 runs | PASS |
| ④ human-2 不丢 | 零 judge-kill; 5 条 sort 落出(非 reject) | CONDITIONAL PASS |

**总裁决: GATE GO** — fragment ladder + search unit 架构调优收敛。

ADR 状态升级：
- ADR-0009: `proposed` → `accepted`（Phase 3.11.8 GATE go, 2026-06-13）
- ADR-0008: `proposed` → `accepted`（核心决策 D1/D2/D3 继续有效）

## 3. 本地验证结果 (Verification)

数据验证通过 Python 脚本对 `llm-judge-scores-thinking-enabled.json` 和 `phase3117-summary.json` 交叉计算：

```
=== Net-new candidates ===
Net-new scored: 44
Score dist: {0: 34, 1: 3, 2: 7}
2-rate: 15.9%
POV transform in net-new: 4

=== Baseline (retained) candidates ===
Baseline scored: 66
Score dist: {0: 45, 1: 12, 2: 9}
2-rate: 13.6%
```

Guard hard failures = 0（来自 phase3117-summary.json 所有 10 个 run）。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **5 条 baseline human-2 sort 落出**：已知代价，可通过 `baseline_overlap` retention floor 调优恢复。非阻塞项。
- **Judge 仍为 screening-only（不采信）**：人工打分尚未覆盖净新增候选，GATE 依据 judge proxy。后续可补人工校准。
- **Phase 3.11 全部 complete**：本 Phase 无后续 TODO。下游考虑：呈现层 POV（OPEN a）、event-fragment-bundle 组合扩展、baseline retention 调优。