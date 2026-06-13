"""Parallel (news, movie) pair scoring for LLM judge batch runs.

Scores multiple candidate pairs concurrently via ``ThreadPoolExecutor`` while
keeping checkpoint writes thread-safe. Used by ``run_phase39_judge_batch.py``
and Phase 3.10 holdout orchestration.
"""

from __future__ import annotations

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

from scripts.llm_judge import JudgeItem, call_llm_judge

JudgeScoreFn = Callable[[JudgeItem], tuple[int, str | None, str, str, bool | None]]
CheckpointFn = Callable[[], None]


def item_key(item: JudgeItem) -> tuple[str, str]:
    return item.run_id, str(item.tmdb_id)


def sort_pending(items: list[JudgeItem]) -> list[JudgeItem]:
    """Deterministic pending order for reproducible resume."""
    return sorted(items, key=lambda i: (i.run_id, i.tmdb_id))


def pair_result_row(
    item: JudgeItem,
    judge_score: int,
    judge_type: str | None,
    rationale: str,
    causal_test: str,
    pov_transform: bool | None = None,
) -> dict:
    return {
        "run_id": item.run_id,
        "tmdb_id": str(item.tmdb_id),
        "title": item.title,
        "judge_score": judge_score,
        "judge_resonance_type": judge_type,
        "judge_pov_transform": pov_transform,
        "rationale": rationale,
        "causal_test": causal_test,
        "human_score": item.human_score,
        "human_resonance_type": item.human_resonance_type,
        "human_pov_transform": item.human_pov_transform,
        "disagreement": item.human_score is not None and item.human_score != judge_score,
    }


def score_pending_pairs(
    pending: list[JudgeItem],
    *,
    partial: dict[tuple[str, str], dict],
    score_fn: JudgeScoreFn | None = None,
    provider: str | None = None,
    mimo_thinking: str | None = None,
    workers: int = 1,
    checkpoint_fn: CheckpointFn | None = None,
    on_progress: Callable[[int, int, JudgeItem], None] | None = None,
) -> None:
    """Score *pending* pairs; update *partial* and call *checkpoint_fn* after each."""
    if not pending:
        return

    ordered = sort_pending(pending)
    workers = max(1, workers)
    lock = threading.Lock()

    def _score_one(item: JudgeItem) -> tuple[JudgeItem, dict]:
        if score_fn is not None:
            judge_score, judge_type, rationale, causal_test, pov_transform = score_fn(
                item
            )
        else:
            judge_score, judge_type, rationale, causal_test, pov_transform = (
                call_llm_judge(item, provider=provider, mimo_thinking=mimo_thinking)
            )
        row = pair_result_row(
            item, judge_score, judge_type, rationale, causal_test, pov_transform
        )
        return item, row

    def _commit(item: JudgeItem, row: dict, idx: int, *, flush: bool) -> None:
        with lock:
            partial[item_key(item)] = row
            if flush and checkpoint_fn is not None:
                checkpoint_fn()
        if on_progress is not None:
            on_progress(idx, len(ordered), item)

    if workers == 1:
        for idx, item in enumerate(ordered, start=1):
            _, row = _score_one(item)
            _commit(item, row, idx, flush=True)
        return

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_score_one, item): item for item in ordered}
        done = 0
        for future in as_completed(futures):
            item, row = future.result()
            done += 1
            _commit(item, row, done, flush=True)
