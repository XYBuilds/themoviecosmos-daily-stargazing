# Phase 7.4 - 集成冒烟测试 交付报告

## 1. 改动范围 (Scope)

- 本次交付不包含运行产物提交；`output/daily_batch/**`、`state/daily_batch_2026-07-06*.json` 仅用于本地验收。
- `p7.4-integration-smoke` 在计划文件中已处于 `completed`，未做无意义状态改动。
- 本次仅新增交付报告文件：`docs/reports/Phase7.4-integration-smoke-report.md`。

## 2. 技术实现 (Implementation)

- Phase 7.4 验收口径按 top-N 边界完成：日批次只处理选定的前 N 条，避免越界或回退到未选中项。
- Guardian 侧 429 韧性已补足：遇到限流时按降级/跳过策略收敛，避免把失败扩散到整批流程。
- `GUARDIAN_API_KEY_BACKUP` 仅作为本次运行环境输入参与验收，不纳入默认项目语义或配置约定。
- 对“已完成项”的判定已修复为要求 `last_completed_stage=compose`，防止把未完成 compose 的条目误判为完成。

## 3. 本地验证结果 (Verification)

- 测试命令：`python -m pytest tests/test_daily_batch.py tests/test_heat_pool.py tests/test_run_options.py -q`
  - 结果：`40 passed`
- full 验证结论：`state/daily_batch_2026-07-06.json` 中 10 个 item 均为 `status=done`，且 `last_completed_stage=compose`。
- 产物验证结论：`output/daily_batch/2026-07-06/` 存在，且每个 item 目录均具备 `news.json / deconstruct.json / expand.json / retrieve.json / briefing.md`。
- 这不是 smoke 验证；属于 Phase 7.4 的 full 后半段人工验收收尾。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `GUARDIAN_API_KEY_BACKUP` 不应进入默认项目语义、计划或报告正文以外的配置约定。
- `output/` 与 `state/` 下的真实运行产物保持本地可追踪，但不提交到仓库。