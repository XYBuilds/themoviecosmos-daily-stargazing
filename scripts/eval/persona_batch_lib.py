"""persona_batch_lib.py · Shared stateless eval helpers extracted from run_persona_batch.

NC round 3 (do_min): only patch-free, side-effect-free constants and pure functions
live here. Patched / IO-orchestrating half-pipeline functions stay in run_persona_batch.
run_persona_batch re-exports these names for backward compatibility, so downstream
scripts and tests that import them from scripts.run_persona_batch keep working.
"""

from __future__ import annotations

import asyncio
from typing import Any, Awaitable, Callable, TypeVar

OBS_RUN_PREFIXES = ("01-", "02-", "03-", "04-")

DEFAULT_CONCURRENCY = 3
LLM_BACKOFF_INITIAL_SEC = 2.0
LLM_BACKOFF_MAX_RETRIES = 4

_T = TypeVar("_T")


def split_obs_holdout(run_ids: list[str]) -> tuple[list[str], list[str]]:
    obs = [r for r in run_ids if r.startswith(OBS_RUN_PREFIXES)]
    holdout = [r for r in run_ids if r not in obs]
    return obs, holdout


def is_retryable_llm_error(exc: BaseException | str | None) -> bool:
    if exc is None:
        return False
    if isinstance(exc, TimeoutError):
        return True
    msg = str(exc).lower()
    return (
        "429" in msg
        or "rate limit" in msg
        or "rate_limit" in msg
        or "too many requests" in msg
        or "timed out" in msg
        or "timeout" in msg
    )


async def with_llm_backoff(
    fn: Callable[[], Awaitable[_T]],
    *,
    is_retryable: Callable[[BaseException | str | None], bool] = is_retryable_llm_error,
    max_retries: int = LLM_BACKOFF_MAX_RETRIES,
    initial_delay: float = LLM_BACKOFF_INITIAL_SEC,
) -> _T:
    """Exponential backoff for LLM 429 / timeout errors (raises from fn)."""
    delay = initial_delay
    for attempt in range(max_retries + 1):
        try:
            return await fn()
        except Exception as exc:
            if attempt >= max_retries or not is_retryable(exc):
                raise
            await asyncio.sleep(delay)
            delay *= 2
    raise RuntimeError("unreachable backoff state")


def reorder_persona_agents(
    persona_ids: list[str],
    persona_agents: dict[str, dict[str, Any]],
    *,
    prefix_agents: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Stable agents[] order matching persona_ids (candidates.json reproducibility)."""
    ordered: list[dict[str, Any]] = list(prefix_agents or [])
    for persona_id in persona_ids:
        agent = persona_agents.get(persona_id)
        if agent is not None:
            ordered.append(agent)
    return ordered