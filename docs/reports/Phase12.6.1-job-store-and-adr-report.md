# Phase 12.6.1 - job_store.py + ADR-0020 交付报告

## 1. 改动范围 (Scope)

- **新增** `review_panel/job_store.py`：面板长任务异步框架的内存存储层（`JobRecord` + `JobStore`）。
- **新增** `tests/test_job_store.py`：`JobStore` 单测 6 项。
- **新增** `docs/adr/0020-panel-async-job-framework.md`：记录 D1–D6 架构决策。
- **改** `.cursor/plans/Phase12.6-panel-async-job-framework.plan.md`（落地动作 A）：frontmatter 规范化 —— `name` 改 slug、`overview` 改块标量、填 `todos` 5 项列表、`isProject: true`。
- **改** `.cursor/plans/Phase12-c2-body-quality-gate.plan.md`（落地动作 B）：gate 的 `id` `p12.6-...`→`p12.end-...`、正文 `## Todo 12.6`→`## Todo 12.end`、依赖 `12.1–12.5`→`12.1–12.5 + 12.6.x`。
- 无新增/删除第三方依赖（纯标准库 `threading`/`uuid`/`time`/`traceback`/`dataclasses`）。

## 2. 技术实现 (Implementation)

- **`JobRecord`**（`@dataclass(frozen=True)`）：`job_id/status/http_status/payload/error/kind/created_at`，不可变快照。`status ∈ {running, done, error}`。
- **`JobStore`**：内部 `dict[str, JobRecord]` + `threading.Lock` 保护所有读写。
  - `submit(work, kind, *, executor=_thread_executor) -> str`：`uuid4().hex` 生成 `job_id`，先落 `running` 记录，再把内部 `_runner` 闭包交给 `executor` 跑，立即返回 `job_id`。`_runner` try/except 兜住 `work()`：成功落 `done`+`(http_status,payload)`，异常落 `error`+`traceback.format_exc()`，后台线程绝不裸崩。
  - `get(job_id) -> JobRecord | None`：加锁读，未知 id → `None`。
- **executor 可注入（ADR-0020 D2，可测性命门）**：默认 `_thread_executor`（`daemon` 线程真异步）；`_inline_executor`（同步立即跑）供单测注入，使 `submit` 返回时 job 已终态、无需起真实线程/端口。
- **模块级默认单例** `job_store`（别名 `_DEFAULT_JOB_STORE`），供 12.6.2 的 `serve.py` import 复用（D6 注入贯通的默认值来源）。
- `work` 契约返回 `(http_status: int, payload: dict)` —— 正是 `serve.py` 各 `handle_*` 的返回形状，job_store 与业务逻辑零耦合（D3 handle_ 零改动的前提）。

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_job_store.py -q
......                                                                   [100%]
6 passed in 2.67s
```

覆盖：inline 立即 `done`、`work` 抛异常落 `error`（含 traceback）、未知 id 返回 `None`、默认 thread executor 轮询到 `done`、`job_id` 唯一性、`_thread_executor` 可导入。`ReadLints` 无告警。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **内存不回收**：job record 只增不删，进程重启即清空（ADR-0020 D1 已记为技术债，MVP 单用户本地工具可接受）。
- **对后续 Phase 的前置**：12.6.2 依赖本模块的 `job_store` 单例与 `submit/get` 契约；12.6.4 会把 `_inline_executor` 注入进 `serve.route()` 测试。
- ADR-0020 一并记录了 D3–D6（后续 TODO 落地），本 TODO 只落地 D1/D2 的代码。
- 分支继承：本 TODO 从最新 `main` 检出 `feat/phase12.6.1-job-store-and-adr`，前置 12.1–12.5 已全部并入 main，无 stacked 继承。