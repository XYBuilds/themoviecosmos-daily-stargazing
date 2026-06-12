# Phase 3.11.6 - 单点 pilot A/B + 防火墙审计 交付报告

## 1. 改动范围 (Scope)

- `scripts/run_phase311_pilot.py` — pilot CLI 入口（单新闻全链 design-on + baseline 对照 + 审计）
- `scripts/audit_phase311_pilot.py` — 防火墙审计脚本（fact drift / center truthfulness / focal derivation / dual floor / funnel sort / weak-fit）
- `scripts/lib/phase311_pilot.py` — pilot 库（审计维度、pool-diff、Go/No-Go 启发式、audit markdown 渲染）
- `scripts/personas.py` — pseudo 过滤逻辑增强（supporting-element cap 硬守卫）、ADR-0008 dual-floor toggle、诊断标签注解更新
- `scripts/retrieve.py` — convergent sort 权重扩展（surface/event/persona-semantic + center_dimension）
- `scripts/llm_judge.py` — JSON extraction 增强、response handling 稳定性
- `tests/test_phase311_pilot.py` — pilot 单测（审计维度、pool-diff、Go/No-Go 路径）
- `output/Eval/phase3.11/pilot-20260612-101656/` — 最新有效 pilot 产物（SSOT）
- `.cursor/plans/Phase3.11-pov-focalization-additive.plan.md` — `p311-6` 标记 completed
- 新增/删除的依赖包：无

## 2. 技术实现 (Implementation)

### pilot pipeline

1. 单条新闻（`01-grid-outage`）跑完整 ADR-0008 design-on 管线：
   - A0 decon → P-Expand → 12 persona alt-pool → screenwriter（composition mode: ADR-0008）→ 守卫 → 检索 → 漏斗 → judge
2. 与 3.10 baseline 同新闻产物做 pool-diff：
   - `net_new_tmdb_ids` / `lost_tmdb_ids` / `by_channel` 通道分解
3. 自动审计 6 维度：
   - ① fact drift（regex + LLM check）
   - ② center declaration truthfulness（token overlap + stuffing risk）
   - ③ focalized derivation（diagnostic-only, warnings ≠ hard fail）
   - ④ dual floor（结构检查；hard guard env toggle `ADR8_DUAL_FLOOR_ENABLED`）
   - ⑤ funnel dedup / convergent sort（需人工 eyeball）
   - ⑥ weak-fit valence optionalization（fit range + channel 分布）
4. 输出 `pilot-audit.md` + `high-hit-score-review.md` + `llm-judge-scores.json/.md`

### 关键设计点

- **focalized 是 diagnostic explanation label**，不参与 Go/No-Go 判断（ADR-0008 D4）
- **toned = 元素中心构图** pseudo，默认 channel；判据是 axis-alignment
- **neutral n1 = objective-floor**，由代码从 surface+hypernym 组装，wording persona-neutral
- **dual floor = 结构存在性检查**（n1 + ≥1 non-focal toned）；hard guard 当前 env 默认 off
- **lost baseline ≠ dual floor failure**：pool-diff 置换是正常 A/B 行为，不等于安全性问题

## 3. 本地验证结果 (Verification)

```text
> python -m unittest tests.test_phase311_pilot tests.test_phase311_pretest tests.test_personas tests.test_retrieve_funnel tests.test_pov_transform_label tests.test_llm_judge

Ran 129 tests in 17.349s

OK
```

### pilot 自动指标（`pilot-20260612-101656`）

| 指标 | 值 | 判断 |
| --- | ---: | --- |
| persona_coverage | 12/12 | PASS |
| pseudo_survival_rate | 0.8857 | PASS |
| valid_center_rate | 1.0 | PASS |
| guard_hard_failures | 0 | PASS |
| fact_drift_fail | 0 | PASS |
| center_truthfulness_fail | 0 | PASS |
| focal_warnings | 4 | diagnostic-only |
| net_new_candidates | 5 | 有差集 |
| lost_baseline | 5 | 均为非 quality、无 human score |
| judge≥1 | 3 candidates | 有可审阅强候选 |
| pipeline_go (heuristic) | true | — |

### Go/No-Go 判定

**Go** — 进入 3.11.7 全批 A/B。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

1. **dual-floor hard guard env 默认 off**：结构存在性已验证；hard guard 强制失败路径未在本轮启用。3.11.7 全批前建议显式决定是否设 `ADR8_DUAL_FLOOR_ENABLED=true`。

2. **funnel sort 高汇聚噪声**：`Geostorm` 等 8-persona 汇聚但 judge=0 的候选排前。3.11.7 应关注排序权重是否需调优（`_CONVERGENT_WEIGHT_PERSONA_SEMANTIC` vs similarity 的平衡）。

3. **focalized 无 net-new 贡献（本轮单点）**：5 条 focalized 产出未独立命中差集候选（所有 net-new 来自 toned）。全批通道分解将给出更完整的 focalized 收益画像。

4. **pilot 只跑 1 条新闻**：`01-grid-outage` 为 Gap A 类（基础设施 / 机构新闻），对 celebrity / political / cultural 类新闻的泛化性尚待 3.11.7 验证。

5. **分支继承**：本分支 `feat/phase3.11.6-element-centered-pipeline` 从 `main` @ `d9d7e29` 检出（3.11.5 已合并后）。