# Phase 7.3 - 集成冒烟测试 交付报告

## 1. 改动范围 (Scope)

- 更新 `scripts/daily_batch.py`，补齐 smoke 所需的 `provider` 透传与运行参数兼容。
- 更新 `tests/smoke_daily_batch.py`，补齐冒烟脚本 CLI 参数，保证与 `run_daily_batch()` 入口一致。
- 更新 `.cursor/plans/Phase7-heat-pool-daily-batch.plan.md`，将 `p7.4-integration-smoke` 标记为 `completed`。
- 新增 `.cursor/plans/ssot/mimo-2.5-pro-parallelism.md` 作为 Phase 7.3/7.4 并行参数与恢复口径 SSOT。
- 新增 `docs/reports/Phase7.3-integration-smoke-report.md`。

## 2. 技术实现 (Implementation)

- smoke 入口保留最小参数集：`--date / --min-count / --max-items / --personas / --persona-concurrency / --provider`，并通过 `RunOptions` 传给 daily batch。
- `run_daily_batch()` 侧补齐对 `provider` 的兼容处理，避免 smoke 脚本在只传 `RunOptions` 时出现属性缺失。
- 验证路径保持“单 item、小批量、单 persona”模式，便于在真实网络与 LLM 调用下快速完成收尾验收。

## 3. 本地验证结果 (Verification)

- `python -m pytest tests/test_daily_batch.py -v`
  - 结果：`16 passed in 17.50s`
- `python tests/smoke_daily_batch.py --date 2026-07-05-smoke-final-4 --min-count 1 --max-items 1 --personas 1`
  - 结果：`[PASS] 冒烟测试全部通过`
  - 总耗时：`185511 ms`
  - 关键产物路径：
    - `output/daily_batch/2026-07-05-smoke-final-4/pool.json`
    - `state/daily_batch_2026-07-05-smoke-final-4.json`
    - `output/daily_batch/2026-07-05-smoke-final-4/01-animals-farmed-airport-patrol-pigs-male/briefing.md`

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 这次 smoke 验证使用真实 API / LLM 路径，执行时间较长；后续若要更快收尾，可再压缩默认 persona 数或增加更轻量的验证档位。
- `output/` 与 `state/` 产物已保留，便于后续复盘与追踪，不做清理。