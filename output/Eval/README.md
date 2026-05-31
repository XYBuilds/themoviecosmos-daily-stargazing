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
