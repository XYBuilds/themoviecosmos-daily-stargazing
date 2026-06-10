# Phase 3.10.7 - Holdout prescreen baseline 交付报告

## 1. 改动范围 (Scope)

- `output/Eval/phase3.10-visible/llm-judge-scores-holdout-3107.json` — holdout 05–10 全量 3.10.1b logic-0-guard judge 重跑
- `output/Eval/phase3.10-visible/llm-judge-scores.json` — 统一 156 对 judge corpus（obs 校准 + holdout 重跑合并）
- `output/Eval/phase3.10-visible/judge-prescreen.json` / `.md` — 冻结 `judge≥1` 预筛分档 + 拒绝集 10% 抽审
- `output/Eval/phase3.10-visible/threshold-safety-report.md` — 全量 + obs/holdout 分段阈值安全
- `output/Eval/phase3.10-visible/holdout-fresh-labels.json` — prescreen pool 人工鲜标审计
- `output/Eval/phase3.10-visible/holdout-prescreen-baseline-3107.md` / `.json` — D5 复检基线（summarize_eval 导出）
- `output/Eval/phase3.10-visible/high-hit-score-review.md` — holdout 拒绝集抽审 + prescreen pool 人工标注
- `output/Eval/phase3.10-visible/holdout-3107-rerun-summary.md` — 3.10.1b holdout 重跑对照
- `scripts/apply_holdout_prescreen_labels_phase310.py` / `phase3107_preapprove_finalize.py` 等编排脚本
- `.cursor/plans/Phase3.10-logic-resonance-and-judge-prescreen.plan.md` — p310-7 标 complete
- 新增/删除的依赖包：无

**分支：** `feat/phase3.10.7-holdout-full-rerun`（基于 `main` @ 3.10.6 merge 后）

## 2. 技术实现 (Implementation)

### Holdout 3.10.1b 全量 judge 重跑

- 输入：holdout 05–10（91 对），`prompt_version=3.10.1b-logic-0-guard`
- 与 obs 校准分合并为 `llm-judge-scores.json`（156 对）
- 分布剧变摘要见 `holdout-3107-rerun-summary.md`（例：1→0 共 46 对，logic 0-guard 显著收紧）

### Prescreen pool 人工鲜标（holdout workflow）

- Pool 定义：`manual_review`（judge≥1）+ `rejection_audit_sampled`（judge=0 抽审 10%）
- Pool 规模：**28** 对（holdout 05–10）
- 人工标注：**27/28**（`holdout-fresh-labels.json` 同步 26 条；review 解析 27 条）
- **未标 1 条：** `08-sports-underdog` / `232679`（拒绝集抽审；共振分仍空）
- 用户 **approve** 时声明已完成剩余 4 条拒绝集抽审标注；接受 judge **仅作预筛**（`screening_only`，`judge_calibration_trusted=False`）

### 阈值安全（冻结 `judge≥1`）

| 切片 | n_scored | n_human_two | killed | zero_killed | workload_reduction |
| --- | --- | --- | --- | --- | --- |
| 全量 156 | 156 | 19 | 0 | **YES** | 41.8% |
| obs 01–04 | 65 | 9 | 0 | **YES** | 23.1% |
| holdout 05–10 | 91 | 10 | 0 | **YES** | **63.2%** |

**Verdict:** **SAFE TO FREEZE**（`threshold-safety-report.md`）

### 共振复检（dual-axis v2 · D5）

| 指标 | combo | pure_fact | lift |
| --- | --- | --- | --- |
| structural_2_rate | 11.5% | 0.0% | **YES** |
| obs combo>pure_fact | True | | |
| holdout combo>pure_fact | True | | |
| obs/holdout consistent | True | | |

### 用户决策（approve 附带条件）

- LLM judge 角色：**prescreen only**（分档 + 减负 + 拒绝集抽审）
- 校准门：**不采信**（`judge_calibration_trusted=False`）— 与 3.10.6 obs 结论一致，工作流侧不在此 Phase 要求采信

## 3. 本地验证结果 (Verification)

```text
python scripts/apply_obs_fresh_labels_phase310.py --apply-only --eval-dir output/Eval/phase3.10-visible
# → synced 65 human labels to obs-fresh-labels.json

python scripts/apply_holdout_prescreen_labels_phase310.py --apply-only --refresh-prescreen --eval-dir output/Eval/phase3.10-visible
# → prescreen pool 28, labeled 26–27; refreshed prescreen human_labeled=122 human_two=19 killed=0

python scripts/phase3107_preapprove_finalize.py
# → obs killed=0 holdout killed=0; combo=11.5% pure=0.0%
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- Prescreen pool **27/28** 已标；`232679` 可在 3.10.8 GATE 前补标，但不阻塞本 Phase 结案（用户已 approve）。
- Holdout judge 3.10.1b 重跑后 downgrade 桶膨胀（85/156），预筛减负率 holdout 侧 ~63%（高于 obs ~23%），符合 logic 0-guard 收紧预期。
- **3.10.8 GATE** 尚未执行；须单独人工验收两条成功标准（共振 + 工作流）并产出 `GATE_RESULT.md`。
- `judge_calibration_trusted=False` 已在用户决策中接受；GATE 工作流侧应记录为「预筛可用、校准不采信」而非 fail。
