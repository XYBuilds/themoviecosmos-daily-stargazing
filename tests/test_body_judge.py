"""tests/test_body_judge.py

按项目约定：纯 pytest，无 fixture 配置文件，直接 def test_xxx。
llm_call 全程用 stub 注入，不真联网。body / overview 取自 05 场景真实草稿样本
（output/daily_batch/2026-07-06/05-ai-poses-hiroshima-style-threat-to-humanity_
drafts_xiaohongshu.json）与《The Creator》(2023, Gareth Edwards) 的 DB overview。
"""

from __future__ import annotations

from scripts.lib.body_judge import Finding, _parse_findings, judge_body_fabrication

# 05 场景真实幻觉样本："The-Lover" draft 正文片段：编造了 overview 没有的画面
# （士兵穿过战火村庄 / 扣扳机前犹豫），且部分草稿把导演写成「加里斯·爱德华斯」
# （音译近似 Edwards，但项目约定导演原名以英文 DB 字段为准做核查）。
_REAL_BODY_WITH_HALLUCINATION = (
    "加里斯·爱德华斯在二零二三年拍的电影，恰恰把这种恐惧放到了一场具体的战争里。"
    "故事里，人类与人工智能已经开战多年，一个因妻子失踪而心灰意冷的前特工，"
    "接到的任务是去刺杀那个设计出终极武器的“造物主”。"
    "电影里，士兵穿过被战火撕裂的村庄，远处是静默行走的AI造物；"
    "那个踏上寻猎之旅的男人，在扣下扳机前的一刻犹豫了。"
)

# 《The Creator》(2023) DB overview（TMDB 原文，英文，唯一授权真值）。
_REAL_OVERVIEW = (
    "Against the backdrop of a war between humans and artificial intelligence, "
    "former special forces agent Joshua is recruited to hunt down and kill the "
    "Creator, the elusive architect of advanced AI who has developed a "
    "mysterious weapon with the power to end the war...or mankind itself."
)

_REAL_DIRECTOR = "Gareth Edwards"


def _stub_returning(raw: str):
    """构造一个记录调用的 stub llm_call，返回固定 raw 文本。"""

    calls: list[str] = []

    def _stub(prompt: str) -> str:
        calls.append(prompt)
        return raw

    _stub.calls = calls  # type: ignore[attr-defined]
    return _stub


# ---------------------------------------------------------------------------
# 正例：stub 返回含 fabricated_detail + wrong_director 的 JSON 数组
# ---------------------------------------------------------------------------


def test_judge_returns_fabricated_detail_and_wrong_director() -> None:
    raw = """```json
[
  {"kind": "fabricated_detail", "quote": "电影里，士兵穿过被战火撕裂的村庄，远处是静默行走的AI造物", "reason": "overview 没有描述这一画面"},
  {"kind": "wrong_director", "quote": "加里斯·爱德华斯", "reason": "导演原名是 Gareth Edwards，与音译不符"}
]
```"""
    stub = _stub_returning(raw)

    findings = judge_body_fabrication(
        _REAL_BODY_WITH_HALLUCINATION,
        _REAL_OVERVIEW,
        llm_call=stub,
        director=_REAL_DIRECTOR,
    )

    assert len(findings) == 2
    fabricated = next(f for f in findings if f.kind == "fabricated_detail")
    assert fabricated.quote == "电影里，士兵穿过被战火撕裂的村庄，远处是静默行走的AI造物"
    assert "overview" in fabricated.reason or fabricated.reason

    wrong_director = next(f for f in findings if f.kind == "wrong_director")
    assert wrong_director.quote == "加里斯·爱德华斯"
    assert wrong_director.reason


# ---------------------------------------------------------------------------
# 反例：stub 返回空数组 —— body 只用 overview 授权信息
# ---------------------------------------------------------------------------


def test_judge_returns_empty_when_body_only_uses_overview_facts() -> None:
    compliant_body = (
        "Gareth Edwards 执导的这部电影讲述了人类与人工智能之间的战争，"
        "一名前特种部队特工被派去追猎设计出终极武器的“造物者”。"
    )
    stub = _stub_returning("```json\n[]\n```")

    findings = judge_body_fabrication(
        compliant_body,
        _REAL_OVERVIEW,
        llm_call=stub,
        director=_REAL_DIRECTOR,
    )

    assert findings == []


# ---------------------------------------------------------------------------
# 解析容错：_parse_findings 单测
# ---------------------------------------------------------------------------


def test_parse_findings_with_json_fence() -> None:
    raw = """```json
[{"kind": "fabricated_detail", "quote": "某句", "reason": "理由"}]
```"""
    findings = _parse_findings(raw)
    assert findings == [Finding(kind="fabricated_detail", quote="某句", reason="理由")]


def test_parse_findings_with_bare_json_no_fence() -> None:
    raw = '[{"kind": "wrong_director", "quote": "某导演名", "reason": "写错了"}]'
    findings = _parse_findings(raw)
    assert findings == [Finding(kind="wrong_director", quote="某导演名", reason="写错了")]


def test_parse_findings_with_invalid_json_returns_empty() -> None:
    raw = "这不是 JSON，只是 LLM 瞎说的一段话"
    assert _parse_findings(raw) == []


def test_parse_findings_with_empty_string_returns_empty() -> None:
    assert _parse_findings("") == []
    assert _parse_findings("   ") == []


# ---------------------------------------------------------------------------
# 检测器不做编排：不改 body；stub 真的被调用（走注入而非真实客户端）
# ---------------------------------------------------------------------------


def test_judge_does_not_mutate_body() -> None:
    body = str(_REAL_BODY_WITH_HALLUCINATION)
    original = str(body)
    stub = _stub_returning("[]")

    judge_body_fabrication(body, _REAL_OVERVIEW, llm_call=stub, director=_REAL_DIRECTOR)

    assert body == original


def test_judge_calls_injected_llm_call_not_real_client() -> None:
    stub = _stub_returning("[]")

    judge_body_fabrication(
        _REAL_BODY_WITH_HALLUCINATION,
        _REAL_OVERVIEW,
        llm_call=stub,
        director=_REAL_DIRECTOR,
    )

    assert len(stub.calls) == 1  # type: ignore[attr-defined]


def test_judge_prompt_contains_overview_and_body() -> None:
    stub = _stub_returning("[]")

    judge_body_fabrication(
        _REAL_BODY_WITH_HALLUCINATION,
        _REAL_OVERVIEW,
        llm_call=stub,
        director=_REAL_DIRECTOR,
    )

    prompt = stub.calls[0]  # type: ignore[attr-defined]
    assert _REAL_OVERVIEW in prompt
    assert _REAL_BODY_WITH_HALLUCINATION in prompt


# ---------------------------------------------------------------------------
# director 缺省：不传时跳过导演检查，只返回 fabricated_detail
# ---------------------------------------------------------------------------


def test_judge_without_director_only_returns_fabricated_detail() -> None:
    raw = """```json
[{"kind": "fabricated_detail", "quote": "在扣下扳机前的一刻犹豫了", "reason": "overview 没有这一情节"}]
```"""
    stub = _stub_returning(raw)

    findings = judge_body_fabrication(
        _REAL_BODY_WITH_HALLUCINATION,
        _REAL_OVERVIEW,
        llm_call=stub,
    )

    assert len(findings) == 1
    assert findings[0].kind == "fabricated_detail"

    prompt = stub.calls[0]  # type: ignore[attr-defined]
    assert "未提供" in prompt


# ---------------------------------------------------------------------------
# Finding 不可变性
# ---------------------------------------------------------------------------


def test_finding_is_immutable_namedtuple_with_expected_fields() -> None:
    finding = Finding(kind="fabricated_detail", quote="某句", reason="理由")
    assert finding.kind == "fabricated_detail"
    assert finding.quote == "某句"
    assert finding.reason == "理由"
    assert not hasattr(finding, "__dict__")