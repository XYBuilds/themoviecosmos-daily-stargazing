# Phase 3.6.5 - 重跑 The Bet 交付报告

## 1. 改动范围 (Scope)

- `output/Eval/phase3.6/{01..10}-*/` — N=10 ADR-0003 管线完整产出（`reality-deconstructed.*`、`agents/*.md`、`retrieve.json` 含 `quality_candidate`、`candidates.md`）
- `output/Eval/phase3.6/high-hit-score-review.md` — 总编对 pseudo≥5 的 90 候选填分
- `output/Eval/phase3.6/GATE_RESULT.md` — 书面闸门（**GATE_FAIL · 发布 / no-go**）
- `scripts/sync_review_scores_to_candidates.py` — 审阅分同步至各 run `candidates.md`
- `scripts/summarize_eval.py` — 汇总时排除 `high-hit-score-review.md` 等非 run 文件
- `.cursor/plans/Phase3.6-resonance-quality-gate.plan.md` — 3.6.5 complete；3.6.6 cancelled

**分支**：`feat/phase3.6.5-closeout-nogo`（自 `main` + 合并 `feat/phase3.6.5-review-format` 评测基建与 N=10 产物）

## 2. 技术实现 (Implementation)

- **管线**：`run_eval_batch.ps1` / `run_eval.py --out output/Eval/phase3.6/{run_id}`；弹性 1–3 pseudo；retrieve 质量地板 + D1 优质标记；candidates 优质优先排序 + 全 agent heading。
- **闸门**：`summarize_eval.py` multi_vs_single（`single_structural_2_rate` vs `multi_structural_2_rate`）。
- **填分工作流**：总编在 `high-hit-score-review.md` 填写 → `sync_review_scores_to_candidates.py` → `summarize_eval --dir output/Eval/phase3.6`。
- **发布裁决**：脚本在高命中子集（90/175 已填）上输出 `GATE_PASS`；总编 **no-go** → 书面 **GATE_FAIL（发布）**（与 3.5.6 同模式：人工验收优先于部分填分下的自动 PASS）。
- **3.6.6**：按 no-go 指令 **取消**，未改 PRD / CONTEXT / eval-the-bet。

## 3. 本地验证结果 (Verification)

```text
python scripts/sync_review_scores_to_candidates.py
# → 90 candidate block(s) updated across 10 run(s)

python scripts/summarize_eval.py --dir output/Eval/phase3.6
Eval runs: 10
Batch pass rate: 70.0% (7/10 runs with >=1 score-2)
single_structural_2_rate: 14.0% (7/50 scored single-agent)
multi_structural_2_rate: 71.4% (5/7 scored multi-agent)
Gate line 2 compare: multi_vs_single (共振类型 present)
Missing scores (excluded from rates): 118

GATE_PASS
  - batch pass rate >= 60%; single_structural_2_rate < multi_structural_2_rate
```

**人工验收（2026-06-04）**：总编 **no-go** → `output/Eval/phase3.6/GATE_RESULT.md` 记 **GATE_FAIL（发布）**；Phase 4 保持暂停；3.6.6 SSOT 跳过。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **共振分 backlog**：118/175 候选仍缺分；全量填分后需重跑 `summarize_eval`，自动结论可能变化。
- **伪命中分**：不宜作发布闸或质量代理；需语义/关联性维度与多维筛选。
- **baseline 增量未证**：`also_baseline` 对比与 12 原型（Select+Tone）待独立 Phase。
- **下一动作**：D1 关联性 rubric、D5 留出集、补全 08–10 评分；**不要**在 GATE_PASS（发布）前启动 Phase 4 或 3.6.6 SSOT。
