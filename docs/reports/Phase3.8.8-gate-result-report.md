# Phase 3.8.8 - GATE 双诊断 + A1-superset 交付报告

## 1. 改动范围 (Scope)

- `output/Eval/phase3.8/GATE_RESULT.md` — 书面 GATE 结论（双诊断 ①②、闸门 1/2、A1-superset、总裁决 **no-go**）
- `output/Eval/phase3.8/gate-diagnostics.json` — `summarize_eval.py` 结构化诊断输出
- `.cursor/plans/Phase3.8-objective-extraction-neutral-channel.plan.md` — 3.8.8 complete（no-go）、3.8.9 cancelled、整体验收结案
- `docs/reports/Phase3.8-closure-no-go.md` — Phase 3.8 整阶段结案摘要
- 新增/删除的依赖包：无

**分支：** `feat/phase3.8.8-gate-result` @ `38eacc2`（基于 main @ df8c967，3.8.7 已合并）

## 2. 技术实现 (Implementation)

### GATE 数据源

| 来源 | 用途 |
| --- | --- |
| `high-hit-score-review.md` | review SSOT；155 scored / 174 high-hit（`01-grid-outage-rerun` 不计 manifest 闸） |
| `batch-run-summary.json` | 10-run 批量 + A1 并跑汇总 |
| 各 run `retrieve.json` + `retrieve-a1.json` + `a1-baseline-meta.json` | A1-superset 对照 |
| `scripts/summarize_eval.py` → `gate-diagnostics.json` | 双诊断与闸门口径 |

### 诊断 ① · neutral_hit_rate ↔ 共振（控 max_similarity）

- n=67；Pearson r=**0.173**；偏相关 r(nhr, score \| similarity)=**0.172**
- **结论：弱** — 中性广度不能单独作为产品排序主轴

### 诊断 ② · toned-convergence ↔ 共振

- quality_candidate 结构/双重 2 分率 **62.5%**（16 scored）vs 非 quality **10.8%**（139 scored）
- neutral-only 可打分样本 **0** — 无法做 ADR 定义的 toned 独立增量对照
- **结论：弱 / 不可分离**

### 闸门与 A1-superset

| 子闸 | 结果 |
| --- | --- |
| 闸门 1（batch ≥60%） | **PASS** — 80% (8/10) |
| 闸门 2（quality > neutral-only） | **PASS（机械）/ 效力不足（实质）** |
| A1-superset | **FAIL** — 31 A1 命中未被中性 union 覆盖；仅 1/10 run 通过 |
| ADR-0005 产品两诊断 | **①弱 ②弱** |

### 产品裁决（ADR-0005 §两诊断）

**GATE no-go** — persona 赌注未成立。

- **不执行** 3.8.9（SSOT 终态、删 A1）
- **ADR-0005** 保持 `proposed`
- **A1** 保留；并跑脚手架保留供后续迭代对照

### 建议下一迭代方向（plan §交给下一 Phase）

回 **3.8.2 / 3.8.6**：

1. 提升中性通道对 A1 的召回覆盖（superset）
2. 锚点契约与 screenwriter 硬化
3. 补「仅中性票、无 toned」可打分对照样本以分离诊断 ②

## 3. 本地验证结果 (Verification)

```text
# GATE 书面结论
output/Eval/phase3.8/GATE_RESULT.md — 总裁决 GATE no-go

# 关键数字（vs Phase 3.7 GATE_FAIL）
batch pass rate:     50% → 80% (+30pp)
quality structural:  20% → 62.5% (+42.5pp)
nhr↔共振（控 sim）:  r≈0.14 → r≈0.17（边际）
A1 superset:         n/a → FAIL (31 misses)

# 用户验收
approve GATE no-go — 2026-06-06
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **3.8.9 skipped：** PRD/CONTEXT 未升终态口径；代码与 SSOT contract 已按 ADR-0005 proposed 实现，但产品未 accept。
- **A1 双轨维护：** 中性通道与 A1 baseline 并存，后续调参须继续 A1 并跑对照。
- **neutral-only 对照缺失：** 诊断 ② 统计效力不足；下一轮设计须刻意产出可打分 neutral-only 样本。
- **Phase 4 gated：** 不因 3.8 管线改善而自动解封；须新一轮 GATE go 后再议。
