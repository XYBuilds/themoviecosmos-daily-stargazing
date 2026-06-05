# Phase 3.8.6.3 - 重跑单点 pilot 验证合规率 交付报告

## 1. 改动范围 (Scope)

- `output/Eval/phase3.8/01-grid-outage-rerun/` — 3.8.6.1/3.8.6.2 修复后全链重跑产物
  - `reality-deconstructed.json`, `reality-expanded.json`, `agents.json`, `retrieve.json`
  - 12 × `personas/{Persona}/persona-pipeline.json`
  - `pilot-audit.md`, `phase38-run-meta.json`
- `scripts/audit_phase38_pilot.py` — 与 3.8.6 首跑分支同源（若首跑 PR 已合并则为本 PR 无 diff）
- `.cursor/plans/Phase3.8-objective-extraction-neutral-channel.plan.md` — 3.8.6 / 3.8.6.3 标 complete
- 新增/删除的依赖包：无

**分支：** `feat/phase3.8.6.3-pilot-rerun` @ `54fe30f`（基于 main @ PR #34 合并后）

**分支继承：** 首跑产物 `01-grid-outage/` 在 `feat/phase3.8.6-single-pilot-firewall-audit`（`c98f3ce`）；本分支仅追加 `01-grid-outage-rerun/`，**未改写**首跑目录。

## 2. 技术实现 (Implementation)

- **重跑触发**：3.8.6 首跑 8/12 → 3.8.6.1 screenwriter 契约/prompt 硬化 + expansion 注入 → 3.8.6.2 channel_assembly 锚点鲁棒性 + 一次 repair/retry。
- **合规 before/after**（`phase38-run-meta.json`）：
  - **Before（首跑）**：8/12 — failures: Caregiver, Hero, Jester, Lover
  - **After（重跑）**：**11/12** — sole failure: **The-Lover**（中性 pseudo lens 泄漏：`unit 2 tripped offline`）
- **可接受下限**：用户 approve **11/12** 作为 Combined 3.8.6 Go 门槛（非 12/12 硬目标）；Combined Go → 可进 3.8.7。
- **审计摘要**（重跑 `pilot-audit.md`）：
  - A0 verbatim / 扩展 pass / toned 锚：自动化 PASS
  - 中性通道：11/12 neutrals；union_vote=True；1 quality candidate
  - 防火墙：The-Lover assembly rejected（已知残留，不阻断 Go）

## 3. 本地验证结果 (Verification)

```text
python scripts/audit_phase38_pilot.py output/Eval/phase3.8/01-grid-outage-rerun
# 重跑：11/12 neutrals；assembly errors=1（The-Lover neutral lens leak）
```

`phase38-run-meta.json`: `pilot_compliance_before=8/12`, `pilot_compliance_after=11/12`, `agent_count=11`.

首跑 `01-grid-outage/` 与 phase3.5/3.6/3.7 历史目录只读未改写。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **The-Lover 中性 lens 泄漏**：screenwriter 仍将 lens 词写入客观地板中性 pseudo；repair/retry 未能清除。后续批量 run（3.8.7）或单独 persona 契约微调时可再攻；当前不阻断 Combined Go。
- **双分支合并顺序**：须将 `feat/phase3.8.6-single-pilot-firewall-audit` 合并入 main（首跑 + audit 脚本），再合并本分支（重跑）；或两 PR 顺序合并。3.8.6.3  alone 不含首跑 artifacts。
- **3.8.7 未启动**：用户仅 approve 3.8.6/3.8.6.3；批量 run + A1 并跑待下一 TODO。

**Related branch decision：** `feat/phase3.8.6-single-pilot-firewall-audit` — **merge for history**（首跑 `01-grid-outage/` 仅在该分支）；合并后 close/delete，由 main 统一承载 audit + 双 run 目录。
