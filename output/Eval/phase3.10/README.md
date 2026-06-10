# Phase 3.10 · Eval 产出（SSOT）

ADR-0007 双轴逻辑共振 + judge 预筛工作流。闸门结论见 [`GATE_RESULT.md`](GATE_RESULT.md)。

## 目录结构

```text
phase3.10/
├── README.md
├── GATE_RESULT.md              # 闸门书面结论
├── 01-grid-outage/ … 10-*/     # 10 条新闻全链 run 产物
├── obs-fresh-labels.json       # obs 01–04 鲜标审计
├── holdout-fresh-labels.json   # holdout prescreen 池鲜标
├── high-hit-score-review.md    # 统一人工审阅 + judge 注入
├── llm-judge-scores.json       # 156 对统一 judge corpus
├── judge-prescreen.json        # 冻结 judge≥1 预筛分档
├── threshold-safety-report.md  # 零 human-2 被杀核验
├── calibration/                # 3.10.6 obs judge 校准快照（历史）
└── _*.log                      # 批次运行日志
```

## 常用命令

```bash
python scripts/summarize_eval.py --dir output/Eval/phase3.10
python scripts/apply_obs_fresh_labels_phase310.py --apply-only --eval-dir output/Eval/phase3.10
python scripts/apply_holdout_prescreen_labels_phase310.py --apply-only --refresh-prescreen --eval-dir output/Eval/phase3.10
```

## 说明

2026-06-10 自 `phase3.10-visible`（NAS 镜像）与 `phase3.10-judge-calibration` 合并为本目录。此前 SMB 上 `phase3.10` 目录项曾损坏导致 Explorer 无法列出；合并后以本路径为唯一 SSOT。
