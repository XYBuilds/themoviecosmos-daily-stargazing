# Eval 新闻集 · N=10 占位

Phase 3 **验证闸门（The Bet）** 用手挑的 10 条新闻 JSON。总编自行填充内容；本目录仅约定文件名与格式。

**格式**：与 [`../sample_news.json`](../sample_news.json) 相同（`title`、`description` 必填；`pub_time`、`source_name`、`url` 推荐）。

**用法**：见 [`docs/eval-the-bet.md`](../../docs/eval-the-bet.md)。

## 占位文件名（请创建并填写）

| # | 文件名 | 建议 run_id | 备注 |
|---|--------|-------------|------|
| 1 | `01-grid-outage.json` | `01-grid-outage` | 基础设施 / 公共危机 |
| 2 | `02-corporate-layoff.json` | `02-corporate-layoff` | 商业 / 劳资 |
| 3 | `03-election-upset.json` | `03-election-upset` | 政治 / 权力更迭 |
| 4 | `04-celebrity-scandal.json` | `04-celebrity-scandal` | 舆论 / 道德反讽 |
| 5 | `05-climate-disaster.json` | `05-climate-disaster` | 环境 / 命运共同体 |
| 6 | `06-tech-monopoly.json` | `06-tech-monopoly` | 科技 / 垄断与监管 |
| 7 | `07-migration-border.json` | `07-migration-border` | 移民 / 边界政治 |
| 8 | `08-sports-underdog.json` | `08-sports-underdog` | 体育 / 逆袭叙事 |
| 9 | `09-cultural-backlash.json` | `09-cultural-backlash` | 文化战争 / 身份 |
| 10 | `10-whistleblower-leak.json` | `10-whistleblower-leak` | 吹哨 / 真相与体制 |

## 批量运行示例

```powershell
# 逐条（推荐：便于观察 errors）
python scripts/run_eval.py --news-file tests/eval_news/01-grid-outage.json --run-id 01-grid-outage

# 或简单循环（PowerShell）
1..10 | ForEach-Object {
  $n = "{0:D2}" -f $_
  $files = Get-ChildItem "tests/eval_news/$n-*.json" -ErrorAction SilentlyContinue
  if ($files) {
    python scripts/run_eval.py --news-file $files[0].FullName --run-id ($files[0].BaseName)
  }
}
```

产物默认写入 `output/Eval/{run_id}.md`。
