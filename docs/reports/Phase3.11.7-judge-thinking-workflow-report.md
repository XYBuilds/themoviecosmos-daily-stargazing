# Phase 3.11.7 - LLM Judge Thinking Workflow 交付报告

## 1. 改动范围 (Scope)

- `scripts/llm_judge.py` — thinking mode 默认切到 enabled，新增 `normalize_mimo_thinking_mode()`，token 预算 4096
- `scripts/run_phase39_judge_batch.py` — 默认 workers=4、`--mimo-thinking` CLI 参数、progress 打印（elapsed/eta/pending）
- `scripts/run_phase310_holdout_prescreen.py` — 引用 `DEFAULT_JUDGE_WORKERS`，传递 `--mimo-thinking enabled`
- `scripts/judge_batch_parallel.py` — `mimo_thinking` 参数穿透到 `call_llm_judge`
- `scripts/judge_prescreen.py` — 新增 `integrate_prescreen_into_review()` 与 `compute_threshold_safety` 导出
- `tests/test_llm_judge.py` — 验证默认 thinking-on、legacy disabled 路径
- `tests/test_judge_batch_parallel.py` — checkpoint 验证 thinking_mode 写入 metadata
- `tests/test_judge_prescreen.py` — 补齐 `compute_threshold_safety` import
- `.cursor/plans/Phase3.11-pov-focalization-additive.plan.md` — 新增 judge 工作流口径与验收项

无新增/删除依赖包。

## 2. 技术实现 (Implementation)

核心变更：

- `_MIMO_DEFAULT_THINKING_MODE = "enabled"`：MiMo judge 默认走 thinking-on 路径，completion token 预算 4096
- `normalize_mimo_thinking_mode(mode)` 统一处理 CLI 传入的 enabled/disabled/on/off 等别名
- `_judge_request_options` 和 `judge_run_metadata` 均接受 `mimo_thinking` 关键字参数，按 mode 动态切换请求参数和 condition_note
- batch runner 启动时打印摘要：`items/done/pending/workers/mimo_thinking/prompt_version`
- 每个 pair 完成后打印：`progress/pending/batch/elapsed/eta/last`，支持长时间任务终端实时观测
- 默认并行度从 1 提升到 4（`DEFAULT_JUDGE_WORKERS = 4`），holdout prescreen 同步引用

## 3. 本地验证结果 (Verification)

```
python -m unittest tests.test_llm_judge tests.test_judge_prescreen tests.test_judge_batch_parallel
----------------------------------------------------------------------
Ran 44 tests in 0.278s

OK
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- thinking-on 每个 pair 的 token 消耗约为 disabled 的 3–4 倍；大批量时注意 MiMo API rate limit，必要时降 workers
- `DEFAULT_PROMPT_VERSION` 已更新为 `3.11.7-mimo-v2.5-pro-thinking-enabled`；旧版 thinking-disabled 产物保留为历史对照，不影响新筛选
- Phase 3.11.7 的其余验收项（池差分解、调优、抽审）在本次工作流变更之外，需后续独立完成