# Phase 3.7.5 - gate fit analysis 交付报告

## 1. 改动范围 (Scope)

- `scripts/summarize_eval.py`：新增 `persona_vs_baseline` 闸门模式；fit×相似度排序维度；persona/A1 path 分桶统计
- `scripts/write_phase37_gate_result.py`（新）：从 `high-hit-score-review.md` 生成 `GATE_RESULT.md`
- `output/Eval/phase3.7/GATE_RESULT.md`（新）：三问结论 + **GATE_FAIL** 裁决
- `tests/eval_fixtures/persona-vs-baseline-{pass,fail}/`（新）：闸门 fixture
- `tests/test_summarize_eval.py`：persona_vs_baseline 单测扩展
- `.cursor/plans/Phase3.7-persona-resonance.plan.md`：3.7.5 todo complete；3.7.6 cancelled
- `docs/adr/0004-persona-emotional-diffusion.md`：Outcome 节

无新增 Python 依赖包。

## 2. 技术实现 (Implementation)

### 闸门 2（persona vs A1）

- **A1 path**：`also_baseline=true` 候选的结构/双重 2 分率
- **Persona path**：`also_baseline=false` 且非 3.6 注入式 An 的 persona 候选
- **Lift**：persona path 2-rate − A1 path 2-rate；须 **>** 0 才过闸门 2

### fit ↔ 共振（P-Abstain 探针）

- Pearson(max_fit, 共振分) 在全批与 focus 子集上计算
- 低 fit (<0.55) 命中结构/双重 2 分计数 → 判断是否硬编码弃权阈值

### fit × 相似度

- `fit_sim_score = max_fit × 相似度` 降序 triage；JSON 输出 `fit_sim_ranking` 供下游压人工体量

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_summarize_eval -v
# persona_vs_baseline pass/fail fixtures — OK

python scripts/write_phase37_gate_result.py
# Wrote output/Eval/phase3.7/GATE_RESULT.md
```

## 4. GATE 结论（partial scoring · 01/02/07/09）

**数据源**：`output/Eval/phase3.7/high-hit-score-review.md`（62 scored / 150 high-hit；4/10 runs）

| 指标 | 全批已打分 | focus (01+02+07+09) |
| --- | --- | --- |
| batch pass rate | 50.0% (5/10) | 100.0% |
| A1 path structural 2-rate | 75.0% (9/12) | 72.7% |
| persona path structural 2-rate | 20.0% (10/50) | 20.0% |
| **lift** | **−55.0%** | **−52.7%** |
| fit↔共振 Pearson r | 0.139 (n=62) | 0.122 (n=61) |
| 低 fit (<0.55) → 结构/双重 2 分 | 0/3 | — |

**脚本裁决**：**GATE_FAIL**

- batch pass rate 50% < 60%
- persona path 2-rate 20% not > A1 path 75%

**用户决策（2026-06-05）**：**No-Go** — 接受 GATE_FAIL，关闭 Phase 3.7，**跳过 3.7.6** SSOT 迁移。

## 5. 潜在影响或技术债 (Technical Debt & Caveats)

- **部分打分**：仅 4/10 runs 有共振分；focus 子集 batch pass 100% 但全批 50%，结论保守
- **P-Abstain 未定稿**：fit 弱相关，低 fit 样本仅 3 条；需补全留出集后再定阈值
- **34 failed cells**：alt-creator valence bucket 缺失（见 `batch-run-summary.json`）；未来迭代应重跑
- **ADR-0004 保持 proposed**：未升 accepted；PRD/CONTEXT/contract 未改
