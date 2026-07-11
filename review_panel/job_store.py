"""review_panel.job_store · Phase 12.6.1 · 面板长任务的后台 job 内存存储（ADR-0020 D1/D2）。

职责：把「提交一个耗时任务」与「稍后查询它的结果」解耦成两个动作——`submit`
立即返回一个 `job_id`，任务本身在后台异步跑；`get` 用 `job_id` 查当前状态/结果。
这是面板长 LLM 任务从「同步 HTTP 阻塞到跑完」改造为「提交 job + 前端轮询」的
核心存储层，serve.py 的 `route()` 后续会 import 本模块的 `_DEFAULT_JOB_STORE`。

能力边界（ADR-0020）：
- `JobStore` 只是一个内存 dict + 锁，**无持久化**——单用户本地工具，进程重启
  即清空，是已接受的技术债（D1）。
- `submit` 的 `executor` 参数可注入（D2）：默认 `_thread_executor` 真起后台
  线程；单测注入 `_inline_executor` 让任务同步立即跑完，`submit` 返回时
  job 已是终态，不必在测试里等线程、不必起真实端口。
- 本模块不关心 `work` 的业务语义，只认它的返回形状
  `(http_status: int, payload: dict)`——这正是 serve.py 里 `handle_*` 函数
  的返回形状，job_store 与业务逻辑之间零耦合。
"""

from __future__ import annotations

import threading
import time
import traceback
import uuid
from dataclasses import dataclass
from typing import Callable

__all__ = ["JobRecord", "JobStore", "job_store"]

Work = Callable[[], tuple[int, dict]]
Executor = Callable[[Callable[[], None]], None]


@dataclass(frozen=True)
class JobRecord:
    """一个 job 在某一时刻的不可变快照。

    `status` 取值 `"running"` / `"done"` / `"error"`：running 时
    `http_status`/`payload`/`error` 均为 `None`；done 时 `http_status`/
    `payload` 回填、`error` 为 `None`；error 时 `error` 回填、
    `http_status`/`payload` 为 `None`。
    """

    job_id: str
    status: str
    http_status: int | None
    payload: dict | None
    error: str | None
    kind: str
    created_at: float


def _thread_executor(fn: Callable[[], None]) -> None:
    threading.Thread(target=fn, daemon=True).start()


def _inline_executor(fn: Callable[[], None]) -> None:
    fn()


class JobStore:
    """`dict[str, JobRecord]` + 锁，供并发 HTTP 请求线程安全地提交/查询 job。"""

    def __init__(self) -> None:
        self._records: dict[str, JobRecord] = {}
        self._lock = threading.Lock()

    def submit(
        self,
        work: Work,
        kind: str,
        *,
        executor: Executor = _thread_executor,
    ) -> str:
        """记一条 `status="running"` 的 job，交给 `executor` 跑，立即返回 `job_id`。

        `work` 无参、返回 `(http_status, payload)`；跑完/跑挂由内部 `_runner`
        闭包兜住并把终态写回 store，调用方（HTTP handler）不需要 try/except。
        """
        job_id = uuid.uuid4().hex
        with self._lock:
            self._records[job_id] = JobRecord(
                job_id=job_id,
                status="running",
                http_status=None,
                payload=None,
                error=None,
                kind=kind,
                created_at=time.time(),
            )

        def _runner() -> None:
            try:
                http_status, payload = work()
            except Exception:  # noqa: BLE001 - 后台线程绝不能裸崩
                self._finish_error(job_id, traceback.format_exc())
            else:
                self._finish_done(job_id, http_status, payload)

        executor(_runner)
        return job_id

    def get(self, job_id: str) -> JobRecord | None:
        with self._lock:
            return self._records.get(job_id)

    def _finish_done(self, job_id: str, http_status: int, payload: dict) -> None:
        with self._lock:
            current = self._records[job_id]
            self._records[job_id] = JobRecord(
                job_id=current.job_id,
                status="done",
                http_status=http_status,
                payload=payload,
                error=None,
                kind=current.kind,
                created_at=current.created_at,
            )

    def _finish_error(self, job_id: str, error: str) -> None:
        with self._lock:
            current = self._records[job_id]
            self._records[job_id] = JobRecord(
                job_id=current.job_id,
                status="error",
                http_status=None,
                payload=None,
                error=error,
                kind=current.kind,
                created_at=current.created_at,
            )


# 供 serve.py 后续 import 复用的模块级默认单例（D6 注入贯通的默认值来源）。
job_store = JobStore()
_DEFAULT_JOB_STORE = job_store