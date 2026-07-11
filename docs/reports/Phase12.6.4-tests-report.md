# Phase 12.6.4 - job_store 单测 + serve route 四态测试 交付报告

## 1. 改动范围 (Scope)

- **改** `tests/test_review_panel_serve.py`（唯一改动文件）：文件末尾 `UnknownRouteTests` 之前新增 `JobRouteTests(unittest.TestCase)`，含 5 个测试方法，直接测 `GET /api/job` 经 `route()` 的四态（+102 行）。
- **未改** `tests/test_job_store.py`：12.6.1 已落地 6 个测试，覆盖 submit/get/异常落 error/inline+thread executor 各分支，无缺口，原样保留。
- 无生产代码 / 计划 / 依赖改动（plan 状态标记与本报告在独立 docs 提交）。

### 前置修复（方案 B，独立 PR #151，已并入 main）

12.6.4 开工前跑全量基线，发现 **main 上一个既有阻塞 bug**（非本 Phase 引入）：`scripts/compose.py` 缺 `import json`（连带 `argparse`/`time`），致 8 个用例红。经用户批准以独立分支 `fix/compose-restore-stdlib-imports` 修复（恢复 3 个被误删 stdlib import，commit `4613340`，PR #151 合并为 `01439df`），全量从 `533 passed, 8 failed` 回到 `541 passed, 1 skipped` 全绿后，12.6.4 才从修复后的 main 检出。详见「潜在影响」。

## 2. 技术实现 (Implementation)

`JobRouteTests` 逐一对齐 ADR-0020 D4 的 `handle_job` 四态契约：

| 测试方法 | 构造手段 | 断言 |
|---|---|---|
| `test_unknown_job_id_returns_404` | 空 `JobStore()` + 不存在的 job_id | `404` / `ok:False` / 有 `error` |
| `test_missing_job_id_param_returns_404` | query 无 `job_id`（rec 落 None 分支） | `404` / `ok:False` / 有 `error` |
| `test_running_job_returns_200_running_without_result` | `executor=lambda fn: None`（只捕获不执行，job 停在 submit 写入的 running 记录） | `200` / payload 恰为 `{ok:True, status:running}`（无 `result`） |
| `test_done_job_returns_200_done_with_result` | `executor=_inline_executor`，work 返回 `(202, {...})` | `200` / `status:done` / `result=={http_status:202, payload:{...}}` |
| `test_error_job_returns_200_error_with_stderr_traceback` | `_inline_executor`，work 抛 `ValueError("boom")` | `200` / `status:error` / `stderr` 含 `ValueError: boom` + `Traceback` |

关键设计：**running 态用「只捕获不执行的 executor」确定性构造**——`submit` 先写入 `status="running"` 记录，再把 `_runner` 交给 executor；传 `lambda fn: None` 令 runner 永不执行，job 稳定停在 running，无需真起线程、无时序抖动，守住 route() 单测「不起真实线程/端口」的既有边界（D2）。此前 `_run_job_and_get_result`/`_submit_async` 只间接覆盖 done 态，本类补齐 unknown/running/error 三态的专用直测。

## 3. 本地验证结果 (Verification)

- `python -m pytest tests/test_job_store.py tests/test_review_panel_serve.py -q` → **77 passed**（原 72 + 新增 5）。
- `python -m pytest -q`（全量，亲自复核）→ **546 passed, 1 skipped in 252.77s**（= 修复后全绿基线 541 + 新增 5，零 regression）。
- ReadLints：新增测试代码无 lint 告警。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **方案 B 引入一个计划外 fix PR（#151）**：`compose.py` 缺 import 是提交 `04288f3`（TMDB 中文片名集成，非标准流水线提交）重排 import 时误删所致，与 job 框架无关。修复为纯恢复 import、无行为变更；已把全量基线从 337（plan 旧记）实为的 8-red 状态扶正为 546-green。plan 12.6.4 验收「基线 337 passed / 1 xfailed」的数字已过时（项目测试量增长至 546），验收实质「全量无 regression」已达成。
- **`JobRouteTests` 是纯 route() 单测**：不起端口、不碰真实 LLM/subprocess；面板端到端异步闭环（POST 立即 202、轮询 loading、跑完刷新、server 无 `ConnectionAbortedError`）留 12.6.5 GATE 真实重跑肉眼验收。
- **分支继承**：从修复后的最新 `main`（`01439df`）检出 `feat/phase12.6.4-tests`，无 stacked 继承。
- Phase11 计划文件的裸改（工作区既有、与本任务无关）全程未触碰。