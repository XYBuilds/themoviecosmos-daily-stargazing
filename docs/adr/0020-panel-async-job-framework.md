# 面板长任务异步 job 框架：内存 JobStore + executor 注入 + 202/轮询契约

**Status**: accepted（决策拍板于 Phase 12.6 需求讨论；物理落地随 Phase 12.6 各 TODO 分批实施——JobStore 核心/D1/D2 落 12.6.1，route 改造/D3/D4/D5 落后续 TODO，D6 注入贯通随之落地）

> **本 ADR 的性质**：面板（`review_panel/serve.py`）6 个长 LLM 任务端点从「同步 HTTP 阻塞」改造为「后台 job + 前端轮询」的架构决策。它承接 [ADR-0016](0016-panel-editorial-regeneration-and-inline-edit.md)（面板编辑/再生成）、[ADR-0017](0017-persona-perspective-c2-draft-pool.md)（persona 视角草稿池）、[ADR-0019](0019-c2-body-quality-gate.md)（C2 正文质量闸门），这三份 ADR 引入或加长的长任务正是本次改造要收回的对象。

## 背景

面板的 6 个长任务端点（publish / rewrite / regenerate / generate-drafts / combine-drafts / retry-draft）原本是同步 HTTP：请求处理线程里 `subprocess.run(capture_output=True)` 阻塞到子进程跑完，才调 `_send_json` 回写响应。其中 retry + judge（[ADR-0019](0019-c2-body-quality-gate.md) 的带反馈重试闸门）最长，约 4 次串行 LLM 调用，实测耗时 ~132s。

浏览器/反向代理侧的连接往往等不到这么久，会在响应回来前把连接 abort；子进程在后台仍继续跑，跑完后 handler 线程想把结果写回一个已经死掉的 socket，抛 `ConnectionAbortedError`，把 `ThreadingHTTPServer` 的某个工作线程直接打崩一条 traceback。根因是「`ThreadingHTTPServer` + 请求线程内同步阻塞」这一模式本身撑不住分钟级任务，不是某个端点的实现细节问题。

改造方向：长任务改为「提交后台 job，立即 202 返回 job_id」，前端拿 job_id 轮询 `/api/job` 直到 done/error 再取结果。本 ADR 记录支撑这一改造的 6 条决策。

## 决策

### D1 · JobStore = 内存 dict + 锁

- 新增 [review_panel/job_store.py](../../review_panel/job_store.py)：`JobStore` 内部是 `dict[str, JobRecord]` + 一个 `threading.Lock`，保护所有读写；**无持久化**。
- **理由**：面板是单用户本地审核工具，不是多进程/多机部署的服务，进程重启期间没有并发用户在等结果，持久化收益为零、成本（选存储、迁移、清理策略）不为零。
- **技术债（已接受）**：进程重启会清空所有 job 记录，正在跑的后台任务失联（线程仍在跑，但没人能再查到它的 job_id）。因为任务本身仍会把落盘产物写到 `output/daily_batch/...`（各 `handle_*` 的既有行为不变，见 D3），重启造成的实际损失是「前端看不到这一条的最终状态」，不是数据丢失；可接受。

### D2 · executor 可注入（可测性命门）

- `JobStore.submit(work, kind, *, executor=_thread_executor)` 把「job 怎么被跑起来」抽成一个参数：
  - `_thread_executor`（默认）：`threading.Thread(target=fn, daemon=True).start()`，真起后台线程异步跑。
  - `_inline_executor`（测试注入）：直接 `fn()` 同步跑完，`submit` 返回时 job 已是 `done`/`error` 终态。
- **理由**：这守住了 [serve.py 模块 docstring](../../review_panel/serve.py) 已确立的可测性边界——`route()` 及其下的 `handle_*` 都是纯函数，单测直接调用，不必起真实端口/真实线程。若 `submit` 只有真线程一条路，测长任务改造后的 `route()` 就得在测试里睡等/轮询后台线程，脆弱且慢；`_inline_executor` 让「提交后立即拿到终态」在单测里是确定性的。

### D3 · handle_ 零改动

- 6 个长任务端点（publish / rewrite / regenerate / generate-drafts / combine-drafts / retry-draft）的业务逻辑（各自的 `handle_xxx` 函数）**不改一行**。
- `route()` 里原来直接调用并等待 `handle_xxx(...)` 返回 `(status, payload)` 的地方，改为 `job_store.submit(lambda: handle_xxx(...), kind=...)`，立即返回 `202 {ok, job_id, kind}`。
- **理由**：`handle_xxx` 已经是「输入 → `(http_status, payload)`」的纯函数形状（见 [serve.py docstring](../../review_panel/serve.py)），恰好与 `JobStore.submit` 要求的 `work: () -> (int, dict)` 契合，job 化只需在调用处包一层闸门，不用重写任何业务逻辑，回归面最小。

### D4 · `/api/job` 轮询契约

新增端点 `GET /api/job?job_id=`：

| job 状态 | HTTP 状态 | 响应体 |
| --- | --- | --- |
| 未知 job_id | 404 | — |
| running | 200 | `{ok, status: "running"}` |
| done | 200 | `{ok, status: "done", result: {http_status, payload}}` |
| error | 200 | `{ok, status: "error", stderr}` |

- **理由**：轮询端点自身永远 200（除未知 id），把「job 本身跑成什么样」编码进响应体的 `status` 字段，而不是复用 HTTP 状态码去表达三态——HTTP 层只表达「这次轮询请求本身」的成败（找到/没找到这个 job_id），job 的业务态由 body 里的 `status` 表达，两层语义不混在一起。done 时把原 handler 会返回的 `(http_status, payload)` 原样透传在 `result` 里，前端拿到后按原来同步流程的逻辑处理即可，前端改动面最小。

### D5 · `_send_json` 兜断连

- `_send_json`（serve.py 里把 `(status, payload)` 序列化写回 socket 的传输层函数）包 try/except，吞掉 `ConnectionAbortedError` / `BrokenPipeError` / `ConnectionResetError`。
- **理由**：即便改成 job 轮询，轮询请求本身仍可能在写响应途中被客户端断开（用户关标签页/网络抖动），不吞就会在 server 线程里打一条无意义的 traceback。这是本次改造要修的直接症状（背景段描述的 `ConnectionAbortedError` 崩溃），但即便没有 job 化也该修——纯传输层健壮性问题，不是 job 框架专属，故仍记在本 ADR 因为它是同一次改造触发发现的。

### D6 · job_store 注入贯通

- `job_store` 参数沿调用链一路穿透：`route(..., job_store=...)` → `make_handler_class(..., job_store=...)` → `_dispatch(..., job_store=...)` → `serve(..., job_store=...)`，默认值统一取模块级单例 `review_panel.job_store._DEFAULT_JOB_STORE`。
- **理由**：与既有 `run_subprocess` 的注入方式同构（serve.py 现有的子进程调用点已经是「参数可注入、默认走真实实现」的形状），单测可以传一个测试专用的 `JobStore`（或同一个 store 但强制 `_inline_executor`），不共享全局可变状态、不依赖测试执行顺序。

## 为什么

1. **根因是传输模式，不是某个端点慢**：`ThreadingHTTPServer` + 同步阻塞模式撑不住分钟级任务，逐个端点加超时/重试治标不治本；提交 job + 轮询是这类本地工具面对长任务的标准形状。
2. **零重写业务逻辑，最小回归面**（D3）：`handle_xxx` 天然是 `work` 期望的形状，job 化只是在调用处包一层，不动任何已跑通的业务代码和既有测试。
3. **可测性优先于图省事**（D2）：executor 注入让「异步」这件事本身可以被单测同步地验证，避免长任务改造引入一批脆弱的睡眠等待型测试。
4. **不为不存在的需求生成复杂度**（D1）：单用户本地工具不需要持久化 job 队列，内存 dict + 锁是与当前规模匹配的最简实现。

## 后果 / 已知局限

- **进程重启丢失运行中 job 的可见性**（D1 技术债）：落盘产物不受影响，但前端会永久停在「running」直到用户刷新/重新触发；MVP 阶段可接受，若未来要多进程部署或需要「重启后仍能看到旧 job 状态」，需要重新评估持久化方案。
- **`job_store` 单例是进程内共享可变状态**：`ThreadingHTTPServer` 多线程并发访问，靠 `JobStore` 内部的 `threading.Lock` 保证安全；新增读写路径时必须走 `JobStore` 提供的方法，不能绕过锁直接摸内部 dict。
- **本 ADR 只记录 D1–D6 的架构决策，不重复各 TODO 的实现细节**：D1/D2（`JobStore` 本体、executor 注入）随 12.6.1 落地；D3–D6（route 改造、`/api/job` 端点、`_send_json` 兜断连、注入贯通）属后续 TODO，实现细节记录在各自的 `docs/reports/Phase12.6.*-report.md`。
- **测试策略**：`tests/test_job_store.py` 覆盖 `JobStore` 本体（inline 终态、异常落 error、未知 id、真实 thread executor 路径、job_id 唯一性）；后续 TODO 需补 `route()` 层用注入的测试 `JobStore`/inline executor 验证 202 立即返回与 `/api/job` 三态轮询契约，不依赖真实网络延时。
- **不属于本 ADR**：6 个 `handle_*` 业务逻辑本身的行为、`/api/job` 具体路由代码、前端轮询 UI 逻辑，均记录在各自 TODO 的交付报告中。