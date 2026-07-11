"""C2 正文语义幻觉检测器（ADR-0019 D0/D2）。

能力边界（务必对齐 ADR-0019 D0，不要在本模块内扩权）：
- 本模块只抓**语义类**红线（overview 没写的电影细节 / 写错的导演名），
  靠 LLM-judge 判断语义，不涉及任何确定性正则匹配。句式类红线（硬转场 /
  说破盖章 / 接受度单独成句）不归本模块，那是 `scripts.lib.body_lint.scan`
  的职责。两者互补、缺一漏网。
- `judge_body_fabrication` 是**检测器**，不是编排器：只返回违规清单
  （`Finding` 列表），不改写正文、不调用真实 LLM 客户端、不决定是否重试。
  是否重试、如何拼反馈，全部交给上游的 `run_publish`（ADR-0019 D3）。
- 本模块**零 IO 依赖**：不 import openai、不建任何 LLM client。`llm_call`
  由调用方依赖注入（复刻 `scripts/compose.py::run_publish` 的
  `llm_call: Any = None` 约定），真实 LLM 客户端的构造留给 12.4 的调用方。

真值纪律（ADR-0019 D2）：
- `overview`（DB 剧情简述）是本函数判定「编造」的**唯一授权真值**。body
  出现 overview 没写的电影具体情节 / 画面 / 角色 / 道具 / 结局，判定为
  `fabricated_detail`。
- `director`（DB 导演原名，可选）是判定「写错导演名」的唯一授权真值。未
  提供时跳过该项检查。

解析容错（judge 不硬失败，宁可漏判交人工）：
- LLM 原始返回按 ADR-0019 D2 约定应是包在 ```json 代码块``` 里的 JSON
  数组；`_parse_findings` 也容忍裸 JSON（无 fence）。解析失败或空返回时
  返回空列表，不抛异常——语义判据本身就有假阴/假阳，宁可漏判，也不能让
  一次 LLM 输出格式抖动砸掉整条 `run_publish` 编排。
"""

from __future__ import annotations

import json
import re
from typing import Any, Callable, NamedTuple

from scripts.lib.paths import repo_root

__all__ = ["Finding", "judge_body_fabrication"]

_PROMPT_REL = "prompts/_shared/body_fabrication_judge.md"

_JSON_FENCE = re.compile(r"```(?:json)?\s*(\[.*?\])\s*```", re.DOTALL)


class Finding(NamedTuple):
    """一次语义幻觉判据命中记录（不可变）。

    - `kind`：命中的判据类型，如 ``"fabricated_detail"`` / ``"wrong_director"``。
    - `quote`：body 里那句涉嫌编造 / 写错的原文，供上游拼 repair_context 时
      把「原文长这样」喂回 LLM 当反馈证据，而不是让 LLM 猜哪句话违规。
    - `reason`：为什么判定它是幻觉的简短中文说明。
    """

    kind: str
    quote: str
    reason: str


def _load_prompt_template() -> str:
    path = repo_root() / _PROMPT_REL
    if not path.is_file():
        raise FileNotFoundError(f"body fabrication judge prompt not found: {path}")
    return path.read_text(encoding="utf-8")


def _render_prompt(template: str, body: str, overview: str, director: str | None) -> str:
    rendered = template.replace("{{body}}", body or "")
    rendered = rendered.replace("{{overview}}", overview or "")
    rendered = rendered.replace("{{director}}", director or "（未提供）")
    return rendered


def _parse_findings(raw: str) -> list[Finding]:
    """把 LLM 原始返回解析成 `Finding` 列表，解析失败/空返回时返回空列表。

    纯函数：只读 `raw`，不做任何 IO / 网络调用。容忍两种形态：
    - 带 ```json 代码块``` 包裹的数组（ADR-0019 D2 约定的标准输出契约）；
    - 裸 JSON 数组（没有 fence，容错 LLM 偶尔漏加 fence 的情况）。
    非法 JSON / 空字符串 / 非数组结构，都判 0 条命中，不抛异常。
    """

    text = (raw or "").strip()
    if not text:
        return []

    fence_match = _JSON_FENCE.search(text)
    payload = fence_match.group(1) if fence_match else text

    try:
        parsed = json.loads(payload)
    except (json.JSONDecodeError, TypeError):
        return []

    if not isinstance(parsed, list):
        return []

    findings: list[Finding] = []
    for item in parsed:
        if not isinstance(item, dict):
            continue
        kind = str(item.get("kind") or "").strip()
        quote = str(item.get("quote") or "").strip()
        reason = str(item.get("reason") or "").strip()
        if not kind or not quote:
            continue
        findings.append(Finding(kind=kind, quote=quote, reason=reason))
    return findings


def judge_body_fabrication(
    body: str,
    overview: str,
    *,
    llm_call: Callable[[str], Any],
    director: str | None = None,
) -> list[Finding]:
    """对正文 `body` 做一次语义幻觉判据，overview 为唯一授权真值。

    契约：
    - 只读 `body` / `overview` / `director`，不修改、不返回改写后的文本；
    - 本函数自身不发起任何网络 / LLM 调用——渲染 prompt 后交给注入的
      `llm_call(prompt: str) -> str` 执行，测试可传 stub 免真联网；
    - `director` 为 `None` 时跳过导演名检查（prompt 里会体现为「未提供」）。

    行为：渲染 prompt（塞入 body / overview / director）→ 调
    `llm_call(prompt)` 拿原始返回 → 交给 `_parse_findings` 解析。解析失败
    或 LLM 返回异常时不抛出，返回空列表（宁可漏判，交人工兜底）。
    """

    template = _load_prompt_template()
    prompt = _render_prompt(template, body, overview, director)
    raw = str(llm_call(prompt) or "")
    return _parse_findings(raw)