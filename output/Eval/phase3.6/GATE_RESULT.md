# Phase 3.6 闸门结论 · The Bet（ADR-0003 管线重跑）

- **日期**：2026-06-04
- **对照基线**：[`output/Eval/phase3.5/GATE_RESULT.md`](../phase3.5/GATE_RESULT.md) · Phase 3.5.6（**GATE_FAIL · 发布**）
- **批次**：N=10（`tests/eval_news/01`–`10` → `output/Eval/phase3.6/{run_id}/`）
- **管线**：弹性 1–3 pseudo · `quality_candidate`（≥2 agents + `--quality-floor`）· multi-vs-single 闸门 · A1 平权计入 D1
- **评分范围**：总编在 `high-hit-score-review.md` 对 **pseudo命中分合计 ≥5** 的 **90** 个候选填分；已同步至各 run `candidates.md`（`scripts/sync_review_scores_to_candidates.py`）。全批次 **175** 候选中仍有 **118** 个未填共振分。
- **脚本自动结论**（同步后 · 仅已填分候选计入率）：

```text
python scripts/summarize_eval.py --dir output/Eval/phase3.6
→ GATE_PASS（70% batch pass; multi_structural_2_rate 71.4% > single 14.0%）
```

- **产品裁决（总编 / 人工验收）**：**no-go（发布）** — 记 **GATE_FAIL（发布）**；ADR-0003 代码层方向值得继续，但**未达发布标准**，且评测样本与代理指标不足以支撑发布闸门通过

---

## Verdict

| 口径 | 结果 |
|------|------|
| **发布闸门** | **GATE_FAIL（发布）** / **no-go** |
| **脚本（高命中子集 · 部分填分）** | `GATE_PASS` — **不可**单独作为发布依据（见下「为何否决脚本 PASS」） |
| **Phase 3.6.6（SSOT）** | **已取消** — 本轮 no-go，不同步 PRD / `CONTEXT.md` / `eval-the-bet.md` |
| **Phase 4（copywriter）** | **保持暂停** |

> 不得将本结论记为 `GATE_PASS（发布）`。3.6.1–3.6.4 已合并的代码改进 **不等于** 解封 Phase 4。

---

## Narrative（总编 / 产品判断）

1. **相对 Phase 3.5**：多 agent 优质标记、弹性 pseudo、命中分二级排序与审阅基建已落地；高命中子集上 multi-agent 结构/双重 2 分率明显高于 single-agent，与 ADR-0003 D2 **方向一致**。
2. **未达发布 / no-go 理由**：
   - **填分不完整**：仅 90/175 候选有共振分，08–10 等 run 大量候选未评；脚本 `GATE_PASS` 建立在**非全量、偏高命中子集**上，不满足 `eval-the-bet.md`「系统填分后再裁决」的精神。
   - **伪命中分不可作质量代理**：样本外检验证伪「高伪分 → 高共振」（如 The Killing Room 伪16→1、Dead Mail A7+A1 伪13→0）；D1「多 agent」不能替代**主题对题 / 关联性**判断。
   - **A1 信号 vs 架构增量**：含 A1 候选共振明显高于纯 An，但多数 2 分同时 `also_baseline=true`，多 agent 体系相对朴素语义检索的**独有增量**仍待 head-to-head 验证（见后续工作）。
   - **体量**：伪≥5 仍约 **9 条/新闻**，需更紧的低质过滤 + 未来多维筛选，而非单靠命中分压到可人工量级。
3. **目标口径调整**：抛弃以「讽刺」为产品目标；统一为 **「关联性」**（讽刺仅为关联子类之一）。12 原型设想 = **A1 的情绪化扩散**（Select+Tone 选碎片、禁止 Inject），待 rubric 与留出集验证后再铺开。

---

## summarize_eval 快照（2026-06-04 · 同步 90 条高分后）

```
Eval runs: 10
Batch pass rate: 70.0% (7/10 runs with >=1 score-2)
single_structural_2_rate: 14.0% (7/50 scored single-agent)
multi_structural_2_rate: 71.4% (5/7 scored multi-agent)
Gate line 2 compare: multi_vs_single (共振类型 present)
Missing scores (excluded from rates): 118

GATE_PASS (automated — partial scoring only)
```

**本 GATE 结论性质**：**editorial + product judgment（人工验收 no-go）**，辅以上述脚本快照；**不以**高命中子集上的自动 `GATE_PASS` 作为发布通过依据。

---

## 后续工作（来自总编会话 + 本批 review）

- **D1**：定义「关联性」分类与评分 rubric（字面同题 / 结构同构 / 情绪同频 / 时代映照等）；区分关联性 ≠ 推荐质量。
- **D2**：12 原型 = A1 情绪化扩散（Select+Tone，事实锁死 deconstructed）；试点 2–3 个 + prompt 骨架。
- **D3**：验证匹配轴（高共振是否偏 `why`/`result` vs 低质 `how` 链）。
- **D4**：命中分轻收紧（去低质、少错杀）；含 A1 优先保留，纯 An 辅以老片 / 高 sim 护栏 — **不作**发布精度闸。
- **D5**：固定 labeled 集 + 留出测试集，规律须样本外验证（本轮已证伪部分 01–07 拟合规律）。
- **D6（延后）**：PRD / CONTEXT / eval-the-bet SSOT 同步 — **本轮跳过（3.6.6 cancelled）**。
- **漏洞1**：`also_baseline` 对比 — 量化 multi-agent 相对纯 baseline 检索的增量后再决定是否加码 12 原型。
- **补全评测**：08–10 及未评低分候选；全量填分后重跑 `summarize_eval` 作量化对照。
- **迭代入口**：回 3.6.1/3.6.2（prompt、`--quality-floor`、containment）或新开 Phase 3.7 关联性/原型子阶段。

---

## Phase 3.6.6

**已取消（用户指令 · 2026-06-04）**。no-go 轮不同步 ADR-0003 待改清单至 PRD / `CONTEXT.md` / `docs/eval-the-bet.md`；待未来 **GATE_PASS（发布）** 后再执行 SSOT 对齐。

---

## Phase 4

**不解封。** `copywriter.py`（C1/C2）与 PRD §5.3 继续 gated，直至书面 **GATE_PASS（发布）**。
