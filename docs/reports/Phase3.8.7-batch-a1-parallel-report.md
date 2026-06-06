# Phase 3.8.7 - 批量 run（A1 并跑）+ 留出集打分 交付报告

## 1. 改动范围 (Scope)

- `scripts/run_phase38_batch.py` — 10-run 批量编排（观察 01–04 / 留出 05–10），每 run 双通道 persona + A1 并跑
- `scripts/run_persona_batch.py` — batch runner 集成 A1 parallel 钩子
- `scripts/run_phase38_eval.py` — eval 路径扩展
- `scripts/backfill_review_scores.py` — phase3.5/3.6/3.7 历史共振分回填至 review 字段
- `scripts/filter_review_candidates.py` — 多 agent + neutral_hits>0 候选过滤
- `tests/test_personas.py` — batch 相关回归
- `output/Eval/phase3.8/` — 10 条批量产物（`01-grid-outage` … `10-whistleblower-leak`），各含 `retrieve.json` + `retrieve-a1.json` + `a1-baseline-meta.json`
- `output/Eval/phase3.8/batch-run-summary.json` — 批量汇总与 persona 失败计数
- `output/Eval/phase3.8/high-hit-score-review.md` — 统一 high-hit review（174 候选，11 runs 扫描含 pilot rerun）
- `output/Eval/phase3.8/multi-agent-neutral-hits-review.md` — 17 条多 agent + neutral 子集 review
- `.cursor/plans/Phase3.8-objective-extraction-neutral-channel.plan.md` — 3.8.7 标 complete
- 删除 `output/Eval/phase3.8/sample-candidate-multi-agent-neutral-hits.md`（已由 filtered review 取代）
- 新增/删除的依赖包：无

**分支：** `feat/phase3.8.7-batch-a1-parallel` @ `1c5c0cc`+（基于 main 合并 3.8.6 链后）

**分支继承：** 基于已合并入 main 的 3.8.6 试点链；`01-grid-outage-rerun/` 为 3.8.6 目录，批量重跑覆盖 `01-grid-outage/` 并新增 02–10。

## 2. 技术实现 (Implementation)

### 批量 run（10 × 12 persona + A1 并跑）

- **Run IDs：** `01-grid-outage`, `02-corporate-layoff`, `03-election-upset`, `04-celebrity-scandal`, `05-climate-disaster`, `06-tech-monopoly`, `07-migration-border`, `08-sports-underdog`, `09-cultural-backlash`, `10-whistleblower-leak`
- **Split：** 观察 01–04 / 留出 05–10（见 `batch-run-summary.json`）
- **A1 并跑：** 10/10 runs `retrieve_a1=true`、`a1_meta=true`（`all_a1_parallel_ok=true`）
- **Retrieve：** 10/10 `all_retrieve_ok=true`；每 run 19 candidates
- **Agent 合规：** 108/120 persona-slots 成功（90%）；8 次 assembly/parse 失败跨 6 runs（repair/retry 已记录于各 `phase38-run-meta.json`）

### Persona 失败摘要（`batch-run-summary.json`）

| Persona | 失败次数 | 典型原因 |
| --- | ---: | --- |
| The-Lover | 2 | 中性 pseudo lens 泄漏（01）；toned 缺 hypernym 锚（03） |
| The-Outlaw | 1 | 中性 pseudo 含 lens term `actor`（04） |
| The-Everyman | 1 | 中性 pseudo lens 泄漏（06，retry 后仍失败） |
| The-Magician | 1 | alt_creator JSON parse_error（06） |
| The-Jester | 1 | alt_creator JSON parse_error（08） |
| The-Explorer | 1 | 中性 pseudo lens 泄漏 `accusations`（09） |
| The-Creator | 1 | 中性 pseudo lens 泄漏 `the production`（09） |

未失败 persona：The-Innocent, The-Hero, The-Caregiver, The-Ruler, The-Sage（全批量 10/10 通过）。

### Review 与留出集打分

- `score_eval_candidates` → `high-hit-score-review.md`（pseudo命中分合计 ≥5 的 174 候选）
- **留出集打分（用户 approve）：** `07-migration-border`（例：Transpecos 共振分 2 / 双重；Stranded 1 / 结构）与 `09-cultural-backlash`（例：L'Odissea 2 / 双重；Jesus of Montreal 2 / 双重）等 holdout 章节已填共振分/类型；满足「≥2 条留出」门槛
- **多 agent + neutral 子集：** `multi-agent-neutral-hits-review.md` — **17/17** 候选均已填共振分（含 Hurricane Season 冲突同步为单一 `共振分: 2`）
- 历史分回填：phase3.5/3.6/3.7 按 tmdb_id 内联至 editor 字段，冲突 policy 见 review 头部说明

## 3. 本地验证结果 (Verification)

```text
# 批量汇总（batch-run-summary.json）
run_ids: 10
all_retrieve_ok: true
all_a1_parallel_ok: true
persona_failure_counts: 8 failures across 7 personas

# Review 产物
high-hit-score-review.md: 174 candidates, 11 runs scanned
multi-agent-neutral-hits-review.md: 17 candidates, 17/17 scored

# 单测（分支内已有）
python -m unittest tests.test_personas -v  # batch 相关用例通过
```

`phase3.5/3.6/3.7` 历史 eval 目录只读未改写。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **Persona 失败率 ~10%：** 仍以中性 lens 泄漏与 alt_creator JSON 解析为主；3.8.8 GATE 可并行，但批量合规若影响 neutral_hit_rate 诊断须记小样本偏差。
- **The-Lover 中性泄漏：** 自 3.8.6 pilot 残留，批量 01 仍复现；非 3.8.7 阻断项。
- **3.8.8 未启动：** 用户仅 approve 3.8.7；GATE_RESULT（双诊断 + A1-superset）待下一 TODO。
- **A1 未删：** superset 验证在 3.8.8 书面 GATE 中裁决。
