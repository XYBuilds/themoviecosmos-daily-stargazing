# Eval 产出目录

每条 `run_eval` 写入 `output/Eval/{run_id}/`：

```text
{run_id}/
├── run.md           # Obsidian 索引
├── reality.json     # 新闻快照（JSON）
├── reality.md       # 现实波澜
├── retrieve.json    # 完整 retrieve（含 divergence）
├── errors.md
├── candidates.md    # 总编填共振分
└── agents/A2.md … A1.md
```

汇总闸门：`python scripts/summarize_eval.py --dir output/Eval`

**Pseudo 命中分**（`retrieve.json` → `candidates.md` 原地追加 `命中分` / `pseudo命中分合计`；不填共振分）：

```bash
python scripts/score_eval_candidates.py
```

产出 `output/Eval/high-hit-score-review.md`（`pseudo命中分合计 ≥ 5`，全 run 汇总）。多 agent 专审见 `multi-agent-hits-review.md`（≥2 agents 准入，单独生成）。

**闸门结论**：见 [`GATE_RESULT.md`](GATE_RESULT.md)（Phase 3.5：**GATE_FAIL · 发布**；Phase 4 暂停）。口径 SSOT：`docs/eval-the-bet.md` §5.1；产品规格 PRD **v0.4**。
