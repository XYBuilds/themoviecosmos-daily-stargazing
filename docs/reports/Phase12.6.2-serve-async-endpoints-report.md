# Phase 12.6.2 - serve.py 异步化 6 端点 + /api/job 交付报告

## 1. 改动范围 (Scope)

- **改** `review_panel/serve.py`：
  - 新增 `handle_job(job_store, query)` + `GET /api/job` 路由分支（四态）。
  - `route()` 6 长任务端点改为 `job_store.submit(lambda: handle_xxx(...), kind=...)` + `202` 返回；新增 `job_store` 参数。
  - `make_handler_class` / `serve` 加 `job_store` 注入参数，`_dispatch` 透传。
  - `_send_json` / `_send_html` 写响应过程包 try/except 兜断连。
  - import `JobStore` / `job_store as _DEFAULT_JOB_STORE`。
- **改** `tests/test_review_panel_serve.py`：`_InlineJobStore`（覆写 executor 为 inline，生产零侵入）+ `_submit_async` 两段式辅助，6 类端点用例改造。
- `handle_*` 业务函数**一行未改**。无新增/删除依赖。

## 2. 技术实现 (Implementation)

- **D3 handle_ 零改动**：6 端点原 `return handle_xxx(...)` 改为提交 job；lambda 闭包前先算 `_xxx_adapter_path` 局部变量，规避默认值 fallback 的晚绑定问题。返回 `202, {ok, job_id, kind}`。
- **D4 /api/job 四态**：`handle_job` —— unknown id→`404 {ok:False,error}`；running→`200 {ok:True,status:"running"}`；done→`200 {ok:True,status:"done",result:{http_status,payload}}`（原 handle_* 同步返回原样透出）；error→`200 {ok:True,status:"error",stderr}`（字段名对齐既有 handle_* 失败的 `stderr` 习惯，前端复用同一套错误展示）。
- **D5 _send_json 兜断连**：整个「写响应」（send_response/headers/wfile.write）包 try/except 吞 `ConnectionAbortedError/BrokenPipeError/ConnectionResetError`，静默 return。`_send_html` 同样处理。
- **D6 注入贯通**：`job_store: JobStore = _DEFAULT_JOB_STORE` 穿 `route` / `make_handler_class` / `serve`，`_dispatch` 调 route 时透传——与既有 `run_subprocess` / `*_adapter_path` 注入同构。
- **测试同步适配**：`_InlineJobStore(JobStore)` 只覆写 `submit` 的 executor 默认值为 `_inline_executor`（不动生产 JobStore）；`_submit_async(tmp_path, path, body, expected_kind, run_subprocess=)` 提交 job（断言 202+kind）→ inline 同步跑完 → 轮询 `/api/job` 断言 done → 返回 `(result_http_status, result_payload)`，形状对齐原同步 `(status, payload)`，各用例原业务断言强度不减。失败路径（handle_* 内部返回 500）仍是 job `done`、`result.http_status==500`。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_review_panel_serve.py tests/test_job_store.py -q
........................................................................ [100%]
72 passed in 8.05s
```

基线对照：改造前 `test_review_panel_serve.py` 66 passed；改造后 66（serve）+ 6（job_store）= 72 passed，契约切换后既有语义全部保留。`ReadLints` 无告警。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **HTTP 契约变更**：这 6 端点由「同步 200/500」变「202+轮询」，属前后端内部契约，无外部消费者。**前端 12.6.3 必须配套改造**（submitJob/pollJob），否则面板功能断裂——这是紧后依赖。
- **`/api/job` 四态专项路由测试**（未知/running/done/error 独立断言）留 12.6.4 补齐；本 TODO 只保证既有 serve 测试绿 + 端点契约通过 `_submit_async` 间接覆盖。
- 快端点（`select`/`edit-body`/`select-draft`/所有 GET）保持同步不变。
- 分支继承：从最新 `main` 检出 `feat/phase12.6.2-serve-async-endpoints`（12.6.1 已并入 main）。