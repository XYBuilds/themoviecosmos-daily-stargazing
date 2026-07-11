"""tests/test_body_lint.py

按项目约定：纯 pytest，无 fixture 配置文件，直接 def test_xxx。
每条 rule_id 至少一个正例（真实草稿违规样本）+ 一个反例（合规写法）。
"""

from __future__ import annotations

import re

from scripts.lib.body_lint import RULES, Violation, scan


# ---------------------------------------------------------------------------
# hard_transition：硬转场「而这部…电影」
# ---------------------------------------------------------------------------


def test_hard_transition_hits_real_violation_sample_1() -> None:
    body = "而这恰好也是导演加里斯·爱德华斯在二零二三年的电影里铺设的未来图景："
    violations = scan(body)
    assert any(v.rule_id == "hard_transition" for v in violations)


def test_hard_transition_hits_real_violation_sample_2() -> None:
    body = "而这部 2023 年的电影，讲述了一场关于信任与背叛的故事。"
    violations = scan(body)
    assert any(v.rule_id == "hard_transition" for v in violations)


def test_hard_transition_does_not_hit_compliant_opening() -> None:
    body = "英国外交大臣今天警告，局势可能在未来数周内进一步恶化。"
    violations = scan(body)
    assert not any(v.rule_id == "hard_transition" for v in violations)


# ---------------------------------------------------------------------------
# parallel_dianpo：「无论是…还是…」并列点破
# ---------------------------------------------------------------------------


def test_parallel_dianpo_hits_real_violation_sample_1() -> None:
    body = "无论是哪一种画面，核心都悬在同一个问题上。"
    violations = scan(body)
    assert any(v.rule_id == "parallel_dianpo" for v in violations)


def test_parallel_dianpo_hits_real_violation_sample_2() -> None:
    body = (
        "无论是银幕上那个必须亲手去终结自己造物的人，"
        "还是现实中那份不断被追问的责任，背后都是同一种手足无措。"
    )
    violations = scan(body)
    assert any(v.rule_id == "parallel_dianpo" for v in violations)


def test_parallel_dianpo_does_not_hit_juxtaposition_without_pattern() -> None:
    body = "那颗火种一旦脱离管控，该由谁去扑灭，没人说得清楚。"
    violations = scan(body)
    assert not any(v.rule_id == "parallel_dianpo" for v in violations)


# ---------------------------------------------------------------------------
# verdict_stamp：「同一种/同一个」式论点盖章
# ---------------------------------------------------------------------------


def test_verdict_stamp_hits_real_violation_sample_1() -> None:
    body = "这种张力本质上源自同一种对失控力量的恐惧。"
    violations = scan(body)
    assert any(v.rule_id == "verdict_stamp" for v in violations)


def test_verdict_stamp_hits_real_violation_sample_2() -> None:
    body = "银幕内外，背后都是同一种手足无措。"
    violations = scan(body)
    assert any(v.rule_id == "verdict_stamp" for v in violations)


def test_verdict_stamp_does_not_hit_compliant_sentence() -> None:
    body = "那颗火种一旦脱离管控，该由谁去扑灭，没人说得清楚。"
    violations = scan(body)
    assert not any(v.rule_id == "verdict_stamp" for v in violations)


# ---------------------------------------------------------------------------
# acceptance_standalone：接受度单独成句
# ---------------------------------------------------------------------------


def test_acceptance_standalone_hits_real_violation_sample_1() -> None:
    body = "这部影片拥有一个稳定的观影群体，评价也停在中游。"
    violations = scan(body)
    assert any(v.rule_id == "acceptance_standalone" for v in violations)


def test_acceptance_standalone_hits_real_violation_sample_2() -> None:
    body = "电影在观众中口碑平稳，看过的人大多给出了温和的评价。"
    violations = scan(body)
    assert any(v.rule_id == "acceptance_standalone" for v in violations)


def test_acceptance_standalone_hits_real_violation_sample_3() -> None:
    body = "这部电影被很多人看过，评价停在中游，讨论它的人却不算多。"
    violations = scan(body)
    assert any(v.rule_id == "acceptance_standalone" for v in violations)


def test_acceptance_standalone_does_not_hit_when_folded_into_clause() -> None:
    # 接受度揉进更长句子的从句中间，句首不是「这部电影/这部影片/电影」，
    # 也没有以接受度小句独立收尾成句——不该被判定为「单独成句」。
    body = (
        "这颗行星的轨道正在缓慢偏移，天文学家仍在追踪它的去向；"
        "这片子看过的人不算少、评价停在中游，谈论它的却不多，"
        "但没人愿意就此下结论。"
    )
    violations = scan(body)
    assert not any(v.rule_id == "acceptance_standalone" for v in violations)


# ---------------------------------------------------------------------------
# 纯函数契约与 DSL 可扩展性
# ---------------------------------------------------------------------------


def test_scan_is_pure_and_does_not_mutate_input() -> None:
    body = "而这部 2023 年的电影，讲述了一场关于信任与背叛的故事。"
    original = str(body)
    scan(body)
    assert body == original


def test_scan_is_deterministic_same_input_same_output() -> None:
    body = "而这部 2023 年的电影，无论是哪一种画面，核心都悬在同一个问题上。"
    assert scan(body) == scan(body)


def test_rules_table_is_dsl_shaped_id_pattern_description_triples() -> None:
    """RULES 表结构断言：新增红线只需往表里加一个三元组，不用改 scan。"""
    assert isinstance(RULES, list)
    assert len(RULES) >= 4
    seen_ids: set[str] = set()
    for entry in RULES:
        assert len(entry) == 3
        rule_id, pattern, description = entry
        assert isinstance(rule_id, str) and rule_id
        assert isinstance(pattern, re.Pattern)
        assert isinstance(description, str) and description
        seen_ids.add(rule_id)
    # rule_id 唯一，供上游按 id 聚合违规。
    assert len(seen_ids) == len(RULES)


def test_violation_is_immutable_namedtuple_with_expected_fields() -> None:
    body = "而这部 2023 年的电影，讲述了一场关于信任与背叛的故事。"
    violations = scan(body)
    assert violations
    violation = violations[0]
    assert isinstance(violation, Violation)
    assert violation.rule_id
    assert violation.snippet
    assert violation.description
    # NamedTuple 天然不可变：没有可写属性/字典。
    assert not hasattr(violation, "__dict__")