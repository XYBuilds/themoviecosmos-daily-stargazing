"""tests/test_job_store.py · Phase 12.6.1 · JobStore 单测（ADR-0020 D1/D2）。"""

from __future__ import annotations

import time

import pytest

from review_panel.job_store import JobStore, _inline_executor, _thread_executor


def test_submit_inline_executor_done_immediately() -> None:
    store = JobStore()

    def work() -> tuple[int, dict]:
        return 200, {"ok": True, "value": 42}

    job_id = store.submit(work, kind="test-kind", executor=_inline_executor)
    record = store.get(job_id)

    assert record is not None
    assert record.status == "done"
    assert record.http_status == 200
    assert record.payload == {"ok": True, "value": 42}
    assert record.error is None
    assert record.kind == "test-kind"


def test_submit_inline_executor_work_raises_becomes_error() -> None:
    store = JobStore()

    def work() -> tuple[int, dict]:
        raise ValueError("boom")

    job_id = store.submit(work, kind="test-kind", executor=_inline_executor)
    record = store.get(job_id)

    assert record is not None
    assert record.status == "error"
    assert record.http_status is None
    assert record.payload is None
    assert record.error is not None
    assert "ValueError: boom" in record.error
    assert "Traceback" in record.error


def test_get_unknown_job_id_returns_none() -> None:
    store = JobStore()
    assert store.get("does-not-exist") is None


def test_submit_default_thread_executor_eventually_done() -> None:
    store = JobStore()

    def work() -> tuple[int, dict]:
        time.sleep(0.05)
        return 202, {"ok": True, "kind": "thread"}

    job_id = store.submit(work, kind="thread-test")

    deadline = time.time() + 5.0
    record = store.get(job_id)
    while record is not None and record.status == "running" and time.time() < deadline:
        time.sleep(0.01)
        record = store.get(job_id)

    assert record is not None
    assert record.status == "done"
    assert record.http_status == 202
    assert record.payload == {"ok": True, "kind": "thread"}


def test_submit_returns_unique_job_ids() -> None:
    store = JobStore()

    def work() -> tuple[int, dict]:
        return 200, {}

    job_id_1 = store.submit(work, kind="k", executor=_inline_executor)
    job_id_2 = store.submit(work, kind="k", executor=_inline_executor)

    assert job_id_1 != job_id_2


def test_default_thread_executor_is_importable() -> None:
    assert callable(_thread_executor)