# Phase 3.11.1 - 预测试 (pretest) 交付报告

## 1. 改动范围 (Scope)

- `scripts/lib/phase311_pretest.py` — ADR-0008 预测试库（manifest、Gap A 样本、池差、ADR-0008 pseudo 解析与注入、Go/No-Go 启发式）
- `scripts/run_phase311_pretest.py` — CLI 入口（dry-run / live 检索、按 run 落盘）
- `tests/test_phase311_pretest.py` — 7 项单元测试
- `output/Eval/phase3.11/pretest-manifest.json` — 预测试脚手架 manifest（5 runs × Gap A 类新闻）
- `.cursor/plans/Phase3.11-pov-focalization-additive.plan.md` — `p311-1` 标记 completed
- 新增/删除的依赖包：无

## 2. 技术实现 (Implementation)

- 用 3.11.0 权威措辞在运行时注入 **ADR-0008 composition mode**，驱动 LLM 按元素中心 + focalized 通道生成 pseudo，再对同一新闻跑 3.10 基线 vs 新构图检索并做 **池差 (pool-diff)**。
- 脚手架覆盖 5 条 Gap A 类 run（`01-grid-outage` … `09-cultural-backlash`），输出 `retrieve.json`、`pool-diff.json`、`agents.json`、`center-granularity.json`、按 persona 的 `persona-pipeline.json`。
- **Live 权威 run**：`output/Eval/phase3.11/pretest-20260610-211857/`（`summary.json`、`pool-diff-report.md`）。
- 解析修复（commit `7993eae`）：focalized POV（`who-*`）可与非 who 中心元素并存；toned 通道误带 focal 时告警并剥离，避免 live 批量失败。

### Go/No-Go 结论（用户已 approve）

**Conditional Go** → 进入 3.11.2。

| 信号 | 结果 |
|------|------|
| 五 run 池差 **net-new** 合计 | **40** 部（相对 3.10 基线） |
| Gap A 目标片 net-new 召回 | **0**（目标 TMDB id 已在各 run 基线池中） |
| 差集是否含潜在新共振 | 是（net-new > 0）；需 3.11.2+ 人工/judge 判精度，非预测试范围 |

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_phase311_pretest -v
# Ran 7 tests in 0.059s — OK
```

- Live 预测试产物目录：`output/Eval/phase3.11/pretest-20260610-211857/`
- Dry-run 脚手架参考：`output/Eval/phase3.11/pretest-dry-run-scaffold/`

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **Conditional Go**：Gap A 锚点片已在基线，无法用 net-new 直接证明 POV 召回；40 net-new 需后续生成层与漏斗阶段验证是否真为「新共振」而非噪声。
- Live 输出目录（含多次试跑）未纳入 git；仅 manifest 与代码在仓库内。
- 3.11.2 须继续引用 3.11.0 措辞源，不得私自改写 contract/card。

**分支继承**：`feat/phase3.11.1-pretest` 基于 `main`（含已合并的 3.11.0 措辞）。
