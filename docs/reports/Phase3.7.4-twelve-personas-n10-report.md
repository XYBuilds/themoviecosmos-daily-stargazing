# Phase 3.7.4 - 12 原型 × N=10 重跑 交付报告

## 1. 改动范围 (Scope)

- `prompts/personas/<11 原型>/persona_card.md` — 补齐除 The-Ruler 外 11 张 persona card
- `scripts/run_persona_batch.py` — 12 原型 × `tests/eval_news/01..10` 批跑（含 A1 中性基线 retrieve）
- `output/Eval/phase3.7/{run_id}/` — 10 条新闻 × 12 persona 管线产物（overlay、persona-pipeline、retrieve.json、agents.json 等）
- `output/Eval/phase3.7/runs-completed-matrix.md` — 86/120 persona×run 矩阵（部分 cell `err`）
- `output/Eval/phase3.7/high-hit-score-review.md` — **评分 SSOT**（`score_eval_candidates` 自 retrieve 生成；per-run `candidates.md` 已移除）
- `output/Eval/phase3.7/high-hit-score-review.md`（总编局部打分）— **观察集 01、02** + **留出集 07、09** 已填 `共振分`/`共振类型`（趋势供 3.7.5 分析；其余 run 待续）
- 删除冗余 per-run `candidates.md`（review 为唯一编辑面）
- 新增/删除的依赖包：无

**合并：** PR [#25](https://github.com/XYBuilds/themoviecosmos-daily-stargazing/pull/25) → `main` @ `bb2e941fb3c02f5de7d429ed564ecba57a030277`（merge commit）

## 2. 技术实现 (Implementation)

- **批跑**：`run_persona_batch.py` 对 manifest 01–10 各 run 跑 12 persona + A1 baseline retrieve；失败 cell 记入 `runs-completed-matrix.md`（86 ok / 120 计划格）。
- **Review SSOT**：Phase 3.7 不再写 per-run `candidates.md`；`score_eval_candidates.py --dir output/Eval/phase3.7` 产出统一 `high-hit-score-review.md`（≥5 命中分候选 + 总编字段占位）。
- **局部打分（人工）**：用户在 review 中完成 **01-grid-outage、02-corporate-layoff**（观察集）与 **07-migration-border、09-cultural-backlash**（留出集）的 `共振分`/`共振类型`；05–10 其余留出新闻与 03–06、08、10 待后续轮次。
- **分支继承**：自 `main`（3.7.3 已合并）检出 `feat/phase3.7.4-twelve-personas-n10`。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_personas -v
# (3.7.4 分支期间) 12 tests OK

# 批跑矩阵
# output/Eval/phase3.7/runs-completed-matrix.md → 86/120 persona cells ok
```

Review 生成与局部打分已提交至 `high-hit-score-review.md`（commit `197d3de` on feature branch，已随 PR #25 合并）。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **打分覆盖不足**：闸门 2 / P-Abstain 正式判定依赖 3.7.5；当前仅 4/10 run 有总编共振分，其中 2 条为留出集（07、09）。
- **矩阵空洞**：14 persona×run 为 `err`，可能影响 per-run 候选体量与 A1 对照完整性。
- **3.7.0 锚点仍为 No-Go**（注入式 creative −28% lift）；persona 赌注须在 3.7.5 `GATE_RESULT.md` 用 `persona_vs_baseline` 重新裁决。
- 下游 **3.7.5** 须让 `summarize_eval` 可读 review SSOT（无 per-run `candidates.md`）。
