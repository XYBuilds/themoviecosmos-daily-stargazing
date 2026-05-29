# Phase 3.3 - 评测手册（The Bet）交付报告

## 1. 改动范围 (Scope)

- `docs/eval-the-bet.md` — Phase 3 验证闸门主手册（N=10 流程、rubric、闸门线、回流路径）
- `tests/eval_news/README.md` — 10 条占位文件名与批量运行示例
- `README.md` — MVP 步骤 4 增加「验证闸门」指针与 CLI 示例
- `.cursor/plans/Phase3-validation-gate-the-bet.plan.md` — Todo 3.3 标记 complete

无新增 Python 依赖或脚本。

## 2. 技术实现 (Implementation)

手册覆盖 Phase 3 plan 要求的六项交付：

1. 前置 Phase 0–2 验收表
2. N=10 新闻 JSON 准备（手写 / Phase 5 RSS 手挑）
3. `run_eval.py` 循环与 Obsidian 填分流程（对齐 `scripts/run_eval.py` 实际 CLI）
4. `summarize_eval.py --dir output/Eval` 闸门汇总（标注 3.2 未合并时为预期接口）
5. 共振分 0/1/2 rubric，与 `CONTEXT.md` 结构性共振一致
6. GATE_FAIL 回流 Phase 1 prompt 或 Phase 2 retrieve

人类工作流附录：手挑 10 → run_eval ×10 → 填分 → summarize_eval → `output/Eval/GATE_RESULT.md`。

## 3. 本地验证结果 (Verification)

- 文档内 CLI 与 `scripts/run_eval.py` 参数（`--news-file`、`--run-id`、`--out`、`--provider`）交叉核对一致
- 闸门定义与 `.cursor/plans/Phase3-validation-gate-the-bet.plan.md` §闸门定义一致（60% 批次 + baseline vs creative 2 分率）
- `README.md` 步骤编号 4–9 连续，链接 `docs/eval-the-bet.md` 有效

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `summarize_eval.py` 由 Todo 3.2 交付；手册已说明 PR 未合并时命令为预期接口
- `tests/eval_news/*.json` 内容由总编自行填充，未提交占位 JSON 正文
- `output/Eval/GATE_RESULT.md` 为人工维护，非脚本产物
