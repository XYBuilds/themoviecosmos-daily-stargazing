# Phase 7.3 - Mimo 2.5 Pro 并行设计与调优基线 交付报告

## 1. 改动范围 (Scope)
- `scripts/daily_batch.py`
- `scripts/lib/run_options.py`
- `.cursor/plans/Phase7-heat-pool-daily-batch.plan.md`
- `docs/reports/Phase7.3-mimo-parallel-baseline-report.md`
- 未新增/删除依赖包

## 2. 技术实现 (Implementation)
- 将 daily batch 的并行基线收敛为 SSOT 口径的默认值：`item=2`、`persona=4`、`global_llm=3`、`rpm=80`、`tpm=8_000_000`、`retry=4`、`backoff=exponential+jitter`。
- 在 `BatchState` 中增加 `parallel_baseline`，用于 resume 时回写并保留本次调度档位；日志中统一输出基线摘要，便于冒烟与故障定位。
- 仅收敛调度 / 恢复 / 观测口径，不改 `heat_pool` 语义、不改 prompt、不改 `retrieve` 排序。

## 3. 本地验证结果 (Verification)
- `python -m pytest tests/test_daily_batch.py tests/test_run_options.py -q`
- 结果：`21 passed in 19.38s`

## 4. 潜在影响或技术债 (Technical Debt & Caveats)
- 当前仅完成并行基线收敛与回归验证，未引入真正的全局 LLM limiter；后续若需要更严格的账号级预算控制，应在不改变业务语义的前提下继续补强。
- 冒烟脚本 `tests/smoke_daily_batch.py` 仍依赖真实 Guardian/LLM 环境，适合作为 Phase 7.4 的人工验证入口。