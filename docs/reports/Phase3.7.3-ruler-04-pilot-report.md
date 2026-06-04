# Phase 3.7.3 - The Ruler persona card + 04 单点 pilot 交付报告

## 1. 改动范围 (Scope)

- `prompts/personas/The-Ruler/persona_card.md` — 秩序/控制情绪、负向捍卫秩序、alt-creator / screenwriter 透镜与 P-Select 约束
- `scripts/run_persona_pilot.py` — 单 run 端到端：`phase3.6` 中性 decon → alt-creator → screenwriter → retrieve → `output/Eval/phase3.7/{run_id}/`
- `output/Eval/phase3.7/04-celebrity-scandal/` — pilot 产物：
  - `alt-pool-overlay.json`, `persona-pipeline.json`, `agents/The-Ruler.md`, `agents.json`
  - `retrieve.json`（6 候选）, `candidates.md`, `pilot-notes.md`
- `tests/test_personas.py` — `test_load_persona_card_ruler`
- `.cursor/plans/Phase3.7-persona-resonance.plan.md` — 分支内 pilot 路径说明（合并后本报告完成 post-approve 状态标记）
- 新增/删除的依赖包：无

**合并：** PR [#24](https://github.com/XYBuilds/themoviecosmos-daily-stargazing/pull/24) → `main` @ `fadf7779c94646e3959ac3949aa9862b889aef17`（merge commit）

## 2. 技术实现 (Implementation)

- **The-Ruler card**：`persona_id=The-Ruler`；核心情绪为秩序/控制/稳定；价值倾向为负向捍卫秩序（谴责破坏秩序者、强调司法/执法恢复控制）。alt-creator 覆盖 who/why/how/result（及必要时 where）；screenwriter 在 P-Tone 下选池词并重配语气，强制 `fit` 自评。
- **`run_persona_pilot.py`**：默认读 `output/Eval/phase3.6/04-celebrity-scandal/reality-deconstructed.json`（只读）；调用 `run_persona_pipeline` + `retrieve_from_agents`；写出 overlay、pseudos、retrieve 与 `candidates.md` / `pilot-notes.md`（含与 A1 baseline retrieve 对照摘要）。
- **04 单点 pilot 结论（人工四项核查 · Go）**：
  1. **格式/匹配**：3 段 pseudos（p1–p3）均带 `fit` 与 fragment 引用；retrieve 产出 6 部候选，`candidates.md` 可填共振分。
  2. **steering vs A1**：A1（phase3.6）同 run 19 部、偏中性 faithful recap（如 *Internet - The Movie*, *Date with Love*）；Ruler 6 部偏向 scandal / crime / legal containment（*Scandal*, *Blackmail*, *Long Arm of the Law*, *Gabbar Is Back* 等）— 见 `pilot-notes.md`。
  3. **fit**：p1=0.88, p2=0.82, p3=0.75（均在计划预期 0.75–0.88 区间）。
  4. **无注入（P-Select）**：`alt-pool-overlay.json` 每词可由 decon 事实推出（如 rumor spreader / arrest warrant / targeted public figure）；无新增人物或指控。
- **Go/No-Go**：**Go** → 交由 Phase 3.7.4 扩至余下 11 原型 × N=10（本 Phase 不启动 3.7.4）。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_personas -v
Ran 12 tests in 0.182s
OK
```

Pilot 产物已检入 `output/Eval/phase3.7/04-celebrity-scandal/`（由 `run_persona_pilot.py` 在 approve 前生成）。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 单点 pilot 仅覆盖 **04 × The-Ruler**；steering / fit 规律须在 3.7.4 N=10 + 留出集打分后由 3.7.5 量化（persona vs A1、`fit↔共振`）。
- 6 候选均 `quality_candidate=false`（`distinct_agents=1`）；与 A1 19 候选体量差异大，扩跑时需观察闸门体量与 `fit × 相似度` 过滤。
- `candidates.md` 中总编共振分仅 Scandal 标 2（双重），其余待 3.7.4 统一评分纪律；不影响 3.7.3 Go。
- 分支继承：自 `main`（3.7.2 已合并）检出 `feat/phase3.7.3-ruler-04-pilot`；合并后远端 feature 分支已删除。
