# Phase 3.5 闸门结论 · The Bet（新管线重跑）

- **日期**：2026-06-02
- **批次**：N=10（`tests/eval_news/01`–`10` → `output/Eval/phase3.5/{run_id}/`）
- **管线**：`deconstruct.py` → `agents.py`（多段 pseudo）→ `retrieve.py`（聚合 + containment）→ `run_eval.py` → 总编评分 / 辅助审阅
- **脚本自动结论**：`python scripts/summarize_eval.py --dir output/Eval/phase3.5` → **GATE_FAIL**（共振分未系统填完，见下）
- **产品裁决（总编 / 人工验收）**：**GATE_FAIL（发布）** — 新管线**效果明显提升**，方向验证成立，但**尚未达到发布标准**

---

## Verdict

| 口径 | 结果 |
|------|------|
| **发布闸门** | **GATE_FAIL** |
| **方向 / Pivot** | **Validated directionally** — 现实解构 + 多 pseudo + 聚合召回值得继续迭代 |
| **Phase 4（copywriter）** | **保持暂停**，直至未来某轮评测 **GATE_PASS（发布）** |

> 不得将本结论记为 `GATE_PASS`。SSOT v0.4 与代码改进已按人工指令同步，**不等于**解封 Phase 4。

---

## Narrative（总编 / 产品判断）

1. **相对 Phase 3 旧管线**：候选更丰富、碎片溯源可解释、创作视角 pseudo 与 overview 的「切片对切片」对齐感更强；`pseudo命中分` / `high-hit-score-review.md` 显示多 agent、多碎片路径能聚到同一部片（如 `01-grid-outage` · Survival Family 合计 17 分）。
2. **未达发布标准**：尚未在 N=10 上稳定满足 `eval-the-bet.md §5.1` 两条发布线（尤其第 2 条：创作视角相对 A1 基线的结构/双重 2 分优势）。总编未在全部 `candidates.md` 中完成 `共振分` + `共振类型` 系统填分，**不能**用 `summarize_eval` 单独宣称通过。
3. **建议后续**：
   - 调 prompt / 契约（3.5.1、3.5.3）或收紧 containment / 碎片组合策略；
   - 补全 10 份 `candidates.md` 共振分后重跑 `summarize_eval` 作量化对照；
   - **在再次 GATE_PASS 之前不要启动 Phase 4**；可考虑 Phase 4 前再跑一轮 N=10。

---

## 新管线（已实现）

```text
新闻 JSON
  → A0 现实解构 (deconstruct.py)     → reality-deconstructed.json / .md
  → A1/A2/A4/A7 (agents.py)          → 每 agent 3× pseudo，带 source 碎片 id
  → retrieve.py                      → 每 pseudo Top-2，按 tmdb_id 聚合，containment
  → run_eval.py                      → candidates.md（共振分/类型占位 + 命中溯源）
  → 可选 score_eval_candidates.py    → pseudo命中分、high-hit-score-review.md
  → summarize_eval.py                → 批次通过率 + baseline vs creative（含 structural_2_rate）
```

**契约 SSOT**：`docs/SSOT/reality-deconstruction-contract.md`  
**评测口径**：`docs/eval-the-bet.md` §4–§5.1（ADR-0002 转向后闸门重心在第 2 条）

---

## 评分与工具状态

| 项目 | 状态 |
|------|------|
| `candidates.md` · **共振分** | **未系统填写**（184 个候选 `missing`；`summarize_eval` 自动 GATE_FAIL） |
| `candidates.md` · **共振类型** | 同上（闸门第 2 条 structural 口径未启用） |
| **pseudo命中分** | 已由 `scripts/score_eval_candidates.py` 写入各 run；`output/Eval/phase3.5/high-hit-score-review.md`（≥5 分，91 候选） |
| **multi-agent-hits-review.md** | 多 agent 专审（≥2 agents） |

**本 GATE 结论性质**：在 `summarize_eval` 未完整填分的前提下，结论为 **editorial + product judgment（人工验收）**，辅以命中分审阅与管线肉眼验收；不以脚本输出 alone 作为发布通过依据。

---

## summarize_eval 快照（仅作参考，非发布依据）

```
Batch pass rate: 0.0% (0/10 eval runs with >=1 score-2; 3 non-run md files excluded in dir scan)
baseline_2_rate / creative_2_rate: N/A (0 scored)
→ GATE_FAIL (automated, all scores missing)
```

---

## 堆叠 PR 状态（#10–#14）

| PR | 分支 | 状态（2026-06-02） |
|----|------|-------------------|
| [#10](https://github.com/XYBuilds/themoviecosmos-daily-stargazing/pull/10) | `feat/phase3.5-deconstruct-agent` | OPEN（#9 已 MERGED 同主题） |
| [#11](https://github.com/XYBuilds/themoviecosmos-daily-stargazing/pull/11) | `feat/phase3.5-rewrite-agents` | OPEN |
| [#12](https://github.com/XYBuilds/themoviecosmos-daily-stargazing/pull/12) | `feat/phase3.5-retrieve-multi-pseudo` | OPEN |
| [#13](https://github.com/XYBuilds/themoviecosmos-daily-stargazing/pull/13) | `feat/phase3.5-eval-resonance-type` | OPEN |
| [#14](https://github.com/XYBuilds/themoviecosmos-daily-stargazing/pull/14) | `feat/phase3.5-rerun-the-bet` | OPEN（含 N=10 产出与命中分工具） |

合并顺序建议：#10 → #11 → #12 → #13 → #14（或 rebase 栈后单 PR closeout）。本 closeout 提交目标分支：`feat/phase3.5-rerun-the-bet`。

---

## Phase 4

**不解封。** `copywriter.py`（C1/C2）与 PRD §5.3 自动化文案阶段继续 gated，直至书面 **GATE_PASS（发布）**。
