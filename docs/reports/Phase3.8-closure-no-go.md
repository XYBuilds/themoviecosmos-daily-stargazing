# Phase 3.8 结案摘要 — GATE no-go

- **日期**: 2026-06-06
- **分支**: `feat/phase3.8.8-gate-result` @ `38eacc2`
- **ADR-0005**: 保持 `proposed`（未 accept）
- **总裁决**: **GATE no-go**

## 做了什么

Phase 3.8 按 ADR-0005 重设计管线，将 A0 职责拆为 verbatim 抽取 / 客观扩展 / persona 价值三层，落地：

- A0 verbatim 瘦身 + 共享客观扩展 pass（hypernym 梯）
- 每 persona 客观地板中性 pseudo + toned 锚定 query
- retrieve 撞车新口径（中性 union 1 票 + ≥1 toned 汇聚）+ `neutral_hit_rate`
- 控相似度双诊断与闸门口径（summarize_eval）
- 英文评测语料 + 单点 pilot（11/12 合规）+ 10-run 批量（A1 并跑）

## 相对 Phase 3.7 的改善

| 指标 | 3.7 | 3.8 | Δ |
| --- | --- | --- | --- |
| batch pass rate | 50% | **80%** | +30pp |
| 主路径 structural 2-rate | persona 20% | quality **62.5%** | +42.5pp |
| fit/nhr ↔ 共振（控 sim） | r≈0.14 | r≈0.17 | 边际 |

中性通道 + hypernym 锚 + 撞车新形状**有效提升了批量通过与 quality 路径命中率**。

## 为何 no-go

| 诊断 | 强度 | 要点 |
| --- | --- | --- |
| ① neutral 广度 | **弱** | 偏相关 r≈0.17；不能作排序主轴 |
| ② toned 精度 | **弱 / 不可分离** | neutral-only 可打分 n=0 |
| A1-superset | **FAIL** | 31 A1 命中未被中性 union 覆盖 |

**persona 赌注未成立** — 不是 ①强②弱（中性召回产品），也不是 ①&②双强（persona 产品）。

## 未执行项

- **3.8.9 skipped** — 未升 PRD/CONTEXT 终态、未删 A1
- **Phase 4** — 不启动
- **ADR-0005** — 不升 `accepted`

## 保留资产

- 三分通道管线代码与单测
- 撞车新口径与 `neutral_hit_rate` 诊断基础设施
- `output/Eval/phase3.8/` 全批 eval 产物 + A1 并跑对照
- screenwriter 硬化与 anchor repair/retry（3.8.6.x）

## 建议下一动作

回 **3.8.2 / 3.8.6** 迭代：

1. 中性通道召回覆盖 A1 superset
2. 锚点契约与 lens 泄漏治理
3. 设计 neutral-only 可打分对照以分离诊断 ②

待新一轮证据满足 ADR-0005 产品门槛后，再议 3.8.9 与 Phase 4 解封。

## Todo 终态

| Todo | 状态 |
| --- | --- |
| 3.8.0–3.8.5 | completed |
| 3.8.6 / 3.8.6.1–3.8.6.3 | completed（pilot Go） |
| 3.8.7 | completed |
| 3.8.8 | completed — **GATE no-go** |
| 3.8.9 | **cancelled** — skipped |
