"""RunOptions · 开发快捷开关（纯数据，不改变现有管线函数签名）.

调用方（run_eval.py / main.py）从 CLI 解析后构造此对象，在调用 persona
pipeline / expand / retrieve 的地方自行做 slice / skip / topk 替换。
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RunOptions:
    """开发/CI 用快捷开关，默认值保持生产管线原有行为不变。"""

    persona_limit: int | None = None  # --personas N：只跑前 N 个 persona
    skip_expand: bool = False  # --skip-expand：跳过 P-Expand
    judge_topk: int = 2  # --judge-topk K：retrieve top_k 覆盖
    force: bool = False  # --force：覆盖已有同日输出