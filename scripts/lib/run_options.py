"""RunOptions · 开发快捷开关（纯数据，不改变现有管线函数签名）.

调用方（run_eval.py / main.py / daily_batch.py）从 CLI 解析后构造此对象，在调用 persona
pipeline / expand / retrieve / 调度的地方自行做 slice / skip / topk / concurrency
替换。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RunOptions:
    """开发/CI 用快捷开关，默认值保持生产管线原有行为不变。"""

    persona_limit: int | None = None  # --personas N：只跑前 N 个 persona
    persona_concurrency: int = 4  # --persona-concurrency N：persona stage 并发上限
    item_concurrency: int = 2  # --item-concurrency N：item 调度并发上限
    global_llm_concurrency: int = 3  # --global-llm-concurrency N：全局 LLM 预算池并发
    global_rpm_budget: int = 80  # --global-rpm-budget N：账号级 RPM 预算
    global_tpm_budget: int = 8_000_000  # --global-tpm-budget N：账号级 TPM 预算
    retry_attempts: int = 4  # --retry-attempts N：重试上限
    backoff: str = "exponential+jitter"  # --backoff：默认回退策略
    skip_expand: bool = False  # --skip-expand：跳过 P-Expand
    judge_topk: int = 2  # --judge-topk K：retrieve top_k 覆盖
    force: bool = False  # --force：覆盖已有同日输出
