# Eval 产出目录

按 Phase 分子目录，避免重跑覆盖历史批次：

| 批次 | 路径 | 说明 |
| --- | --- | --- |
| Phase 3.5.6（只读对照） | `output/Eval/phase3.5/` | N=10 新管线闸门；**勿覆盖** |
| Phase 3.6+ | `output/Eval/phase3.6/` | 3.6 管线重跑与书面闸门 |

每条 `run_eval` 写入 `output/Eval/<phase-dir>/{run_id}/`（3.6.5 须显式 `--out`，见 Phase 3.6 plan）：

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

**Phase 3.5.6 汇总**（只读对照批次）：

```bash
python scripts/summarize_eval.py --dir output/Eval/phase3.5
```

**Phase 3.6 汇总**（当前开发批次）：

```bash
python scripts/summarize_eval.py --dir output/Eval/phase3.6
```

**Pseudo 命中分**（`retrieve.json` → `candidates.md` 原地追加 `命中分` / `pseudo命中分合计`；不填共振分）：

```bash
python scripts/score_eval_candidates.py --dir output/Eval/phase3.6 --review-out output/Eval/phase3.6/high-hit-score-review.md
```

产出 `high-hit-score-review.md` 于对应 `--dir` 批次根（3.5 对照见 `phase3.5/high-hit-score-review.md`）。多 agent 专审见 `phase3.5/multi-agent-hits-review.md`。

### Phase 3.6.5 并行批量（推荐）

从仓库根目录、PowerShell 7+：

```powershell
# 预览命令（不调 LLM）；需安装 PowerShell 7+（pwsh）
pwsh -NoProfile -File scripts/run_eval_batch.ps1 -WhatIf

# 正式：10 路并行，ThrottleLimit=3，每任务前随机 sleep 5–15s
pwsh -NoProfile -File scripts/run_eval_batch.ps1
```

- 写入 **`output/Eval/phase3.6/{run_id}/`**；日志 **`output/Eval/phase3.6/_logs/{run_id}.log`**；摘要 **`_logs/batch-summary.json`**
- **10 条全部成功**后自动跑 `score_eval_candidates.py`（带 `--review-out`，不写 `output/Eval/` 根）
- **不**跑 `summarize_eval`；**不**覆盖 `phase3.5/`
- 429 重试：`pwsh -File scripts/run_eval_batch.ps1 -RetryFailed`（仅失败 run_id，**K=4** 并行）

环境：`.env` 中 LLM 密钥 + `python scripts/smoke_llm.py` 通过；索引已构建（见 `docs/eval-the-bet.md` §1）。

**闸门结论**：Phase 3.5.6 → [`phase3.5/GATE_RESULT.md`](phase3.5/GATE_RESULT.md)（**GATE_FAIL · 发布**）；Phase 3.6 → `phase3.6/GATE_RESULT.md`（重跑后维护）。口径 SSOT：`docs/eval-the-bet.md` §5.1；产品规格 PRD **v0.4**。
