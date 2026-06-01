# Phase 3.5.1 - 定稿解构契约 + 下游消费决策 交付报告

## 1. 改动范围 (Scope)

- **新增** `docs/SSOT/reality-deconstruction-contract.md`（自 `docs/temp/news-analyze.md` 升格，含附录 B 下游决策）
- **删除** `docs/temp/news-analyze.md`
- **新增** `docs/temp/README.md`（指向 SSOT 契约）
- **更新** `.cursor/plans/Phase3.5-pivot-reality-deconstruction.plan.md`（todo `f35b1c2d-0001-4000-8035-000000000001` → complete，验收勾选，SSOT 表与 3.5.1 摘要表）
- **无** 代码 / 依赖变更

## 2. 技术实现 (Implementation)

### 2.1 Promote 契约

现实解构规格从临时目录迁入 `docs/SSOT/reality-deconstruction-contract.md`，保持 v3.1 解构层语义不变；§6 改为指向附录 B，不再写「另起 TODO」。

### 2.2 下游消费决策（附录 B）

| 决策域 | 结论 |
|--------|------|
| **碎片取舍** | 解构层不设上限；编剧**全量**读 JSON、**persona 自择**；单段 `why≤2`、`result≤2`、`how` 连续窗口 `≤3`；同行在同一 agent 多段中至多复用一次 |
| **每 agent 段数** | A1=1；A2/A4/A7 各≤3；全条≤10 pseudo |
| **抽象层级** | A1 L0 表层 / A2 L2 权力 / A4 L3 神话 / A7 L2–L3 系统；**固定档位**，禁止 agent×层级笛卡尔积 |
| **how 取用** | 连续子序列；A1/A2/A4 默认 0 步，A7 优先；弱匹配器，期望 ≤30% creative 段含 how |
| **召回聚合** | 每段 Top-K=2；`tmdb_id` 去重；候选≤24；撞车不含 A1 |

与 ADR-0002 对齐：表层合法、结构由 agent 再加工；解构层零解读；承重专名在 A1 档位配合后续 deentification 放宽。

### 2.3 agents.json 输出形状（3.5.3 预埋）

多段 pseudo 建议结构：`pseudos: [{ text, fragments: { why: [idx], how: [step], result: [idx] } }]`，便于 3.5.4 记录命中碎片来源。

## 3. 本地验证结果 (Verification)

```powershell
# 契约已离开 temp（仅 README 跳转）
Test-Path docs/temp/news-analyze.md          # False
Test-Path docs/SSOT/reality-deconstruction-contract.md  # True

# 仓库内无残留旧路径引用（除 plan 历史语境外）
rg "docs/temp/news-analyze" .
# （无匹配）

# 现有测试套件（无契约相关用例，确认无 regression）
python -m pytest tests/ -q
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **3.5.2** 须引用新 SSOT 路径实现 `A0` prompt 与 `deconstruct.py` 校验。
- **3.5.3** 须实现附录 B 段数/碎片/metadata；deentification 放宽另 todo。
- **3.5.4** 须实现 B.5 多段 retrieve + ≤24 候选硬顶。
- **候选≤24** 为产品拍板，若闸门总编仍觉负担大，可在 3.5.6 后下调 K 或 creative 段数，不改解构契约。
- PRD v0.4 / CONTEXT 新词条仍 gated 于 3.5.7（GATE_PASS 后）。
