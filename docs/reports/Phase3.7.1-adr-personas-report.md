# Phase 3.7.1 - ADR-0004 + 12 原型清单 + 留出集 交付报告

## 1. 改动范围 (Scope)

- `docs/adr/0004-persona-emotional-diffusion.md` — P-Source … P-Cost、闸门 1/2、12 原型 roster 引用、**观察集 01–04 / 留出集 05–10**、多轮打分纪律（每轮 ≥2 条留出新闻）
- `docs/SSOT/personas-12.md` — **canonical** 12 原型 SSOT（persona_id、情绪、价值倾向、04 示例列）
- `docs/eval-the-bet.md` — §4 关联/共振 rubric 去「讽刺」独立目标；新增 Phase 3.7 观察/留出集表
- `.cursor/plans/Phase3.7-persona-resonance.plan.md` — todo `f37b1c2d-0001-4000-8037-000000000001` → `completed`；3.7.4/3.7.5/风险节 holdout 措辞对齐

**分支**：`feat/phase3.7.1-adr-personas` → PR [#22](https://github.com/XYBuilds/themoviecosmos-daily-stargazing/pull/22) merge commit `649b361` on `main`

**用户 override（本交付采纳）**：

| 项 | 定稿 |
| --- | --- |
| ADR-0004 | 保留；`Status: proposed` 至 3.7.5 GATE |
| 12 原型 | `docs/SSOT/personas-12.md` 为唯一 SSOT；**不**在新代码/文档中引用 `docs/temp/12原型视角、追求与双面设定集.md` |
| 留出集 | **观察** `01`–`04`；**留出** `05`–`10`（非草案 01–07/08–10） |
| 多轮 | 每轮至少在留出集上填 **2** 条新闻的共振分 |

## 2. 技术实现 (Implementation)

- **ADR-0004** 固化 Phase 3.7 赌注：A0 只解构；per-persona alt-creator 自产 valence spectrum；screenwriter Select+Tone；1 份中性 decon + overlay；`fit` 自评；闸门 2 = persona 结构/双重 2 分率 > A1 中性基线。
- **personas-12.md** 提供 `The-Ruler` … `The-Jester` 共 12 行 roster，与 `prompts/personas/<persona_id>/` 命名约定一致；Pilot 首卡仍为 `04-celebrity-scandal` × The-Ruler。
- **留出集纪律** 与 `tests/eval_news/batch-manifest.json` run_id 对齐；`summarize_eval` / 3.7.5 须仅统计留出集已打分 run（实现留 3.7.5）。
- **3.7.0 No-Go** 仍为历史锚（creative lift −28%）；用户 `continue` 覆盖后推进 3.7.1+，须在留出集独立验证 persona 增量。

## 3. 本地验证结果 (Verification)

- 文档一致性审阅：ADR、`eval-the-bet.md`、plan 3.7.1/3.7.4/3.7.5 中 holdout 均为 01–04 / 05–10；`personas-12.md` 无 temp 设定集交叉引用。
- PR #22：`mergeable` → **merged**（merge commit，远端 `feat/phase3.7.1-adr-personas` 已删除）。
- 无运行时脚本变更；未跑 `unittest`（本 TODO 仅文档/ADR）。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **3.7.2+** 须从 `main` 检出新分支；实现 `scripts/personas.py` 时只读 `docs/SSOT/personas-12.md`。
- **3.7.5** 需扩展 `summarize_eval` 按观察/留出集分桶；多轮打分需记录每轮已评留出 run_id。
- **历史 eval 文案**（`output/Eval/phase3.6/GATE_RESULT.md` 等）仍写 01–07/08–10，为 3.6 快照，不 retro-edit。
- **ADR Status** 在 3.7.5 GATE go 前保持 `proposed`；3.7.6 再升 `accepted` 并改 PRD/CONTEXT/contract。
