# Phase 3.5.6 - 重跑 The Bet 交付报告

## 1. 改动范围 (Scope)

- `output/Eval/01-grid-outage` … `10-whistleblower-leak/` — N=10 新管线完整产出（含 `reality-deconstructed.*`、`agents/*.md`、`retrieve.json`、`candidates.md`）
- `scripts/score_eval_candidates.py` — pseudo 命中分写入 `candidates.md`；汇总 `high-hit-score-review.md`
- `output/Eval/GATE_RESULT.md` — 书面闸门结论（**GATE_FAIL · 发布**）
- `.cursor/plans/Phase3.5-pivot-reality-deconstruction.plan.md` — 3.5.6 及全 Phase closeout 标记

**分支**：`feat/phase3.5-rerun-the-bet`（栈顶；继承 #10–#13 能力）

## 2. 技术实现 (Implementation)

- **管线**：`run_eval.py` 串联 `deconstruct` → `agents`（`pseudos[]` + `source`）→ `retrieve`（按 `tmdb_id` 聚合、`hit_sources`）→ Eval 目录。
- **候选规模**：约 15–19 候选/条（4 agents × 3 pseudos × Top-2，聚合去重后）；containment 防止爆炸。
- **评测占位**：`candidates.md` 含 `共振分`、`共振类型`；`score_eval_candidates.py` 追加 `命中分` / `pseudo命中分合计`（不替代共振分）。
- **闸门**：`summarize_eval.py` 支持 `structural_2_rate`；本批次共振分未填完 → 脚本自动 **GATE_FAIL**；**发布结论**依人工验收记 **GATE_FAIL**（方向 OK，未达发布线）。

## 3. 本地验证结果 (Verification)

```text
# N=10（评测期已跑，产物在 output/Eval/）
python scripts/run_eval.py --news-file tests/eval_news/01-grid-outage.json --run-id 01-grid-outage
# … 01–10 均已产出

python scripts/score_eval_candidates.py
# → output/Eval/high-hit-score-review.md（91 candidates ≥5 pseudo hit）

python -m scripts.summarize_eval --dir output/Eval
# → GATE_FAIL (184 missing 共振分; 0/10 batch pass)
```

**人工验收（2026-06-02）**：总编确认新管线**效果明显提升**，但**未达发布标准** → `output/Eval/GATE_RESULT.md` 记 **GATE_FAIL（发布）**；Phase 4 保持暂停。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **共振分 backlog**：需总编补填 10× `candidates.md` 后重跑 `summarize_eval` 才有可比的 baseline/creative 率。
- **PR 栈 #10–#14**：仍 OPEN，closeout 文档/SSOT 在本分支；合并后 `main` 才含完整 3.5 代码。
- **下一动作**：调 3.5.1/3.5.3 prompt 或再跑一轮 N=10；**不要**在 GATE_PASS 前启动 Phase 4。
- **3.5.7**：按用户指令，**尽管 GATE_FAIL** 仍执行 SSOT v0.4 同步（见 `Phase3.5.7-ssot-v04-report.md`）。
