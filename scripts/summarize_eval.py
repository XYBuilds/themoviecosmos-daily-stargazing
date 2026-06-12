"""summarize_eval.py · 解析已评分 Eval Markdown，汇总闸门指标."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from scripts.resonance_rubric import (
    STRUCTURAL_TYPES,
    parse_pov_transform,
    parse_resonance_type,
    validate_pov_transform_sub_label,
)
from scripts.run_persona_batch import OBS_RUN_PREFIXES

_REPO_ROOT = Path(__file__).resolve().parents[1]

_SCORE_LINE = re.compile(r"^-\s*\*\*共振分\*\*:\s*(.*)$", re.MULTILINE)
_RESONANCE_TYPE_LINE = re.compile(r"^-\s*\*\*共振类型\*\*:\s*(.*)$", re.MULTILINE)
_POV_TRANSFORM_LINE = re.compile(r"^-\s*\*\*POV变换\*\*:\s*(.*)$", re.MULTILINE)
_STRUCTURAL_TYPES = STRUCTURAL_TYPES | frozenset({"结构", "双重"})
_TMDB_LINE = re.compile(r"^-\s*\*\*tmdb_id\*\*:\s*(\S+)", re.MULTILINE)
_SIMILARITY_LINE = re.compile(r"^-\s*\*\*相似度\*\*:\s*([\d.]+)", re.MULTILINE)
_FIT_VALUE = re.compile(r"fit=([\d.]+)")
_ALSO_BASELINE_LINE = re.compile(
    r"^-\s*\*\*also_baseline\*\*:\s*(true|false)",
    re.MULTILINE | re.IGNORECASE,
)
_QUALITY_CANDIDATE_LINE = re.compile(
    r"^-\s*\*\*(?:quality_candidate|quality_candidate_annotation)\*\*:\s*(true|false)",
    re.MULTILINE | re.IGNORECASE,
)
_QUALITY_ZH_LINE = re.compile(
    r"^-\s*\*\*(?:优质候选|汇聚标注)\*\*:\s*(true|false)",
    re.MULTILINE | re.IGNORECASE,
)
_NEUTRAL_HIT_RATE_LINE = re.compile(
    r"^-\s*\*\*neutral_hit_rate\*\*:\s*([\d.]+)",
    re.MULTILINE,
)
_NEUTRAL_HITS_LINE = re.compile(
    r"^-\s*\*\*neutral_hits\*\*:\s*(\d+)",
    re.MULTILINE,
)
_NEUTRAL_TOTAL_LINE = re.compile(
    r"^-\s*\*\*neutral_total\*\*:\s*(\d+)",
    re.MULTILINE,
)
_DISTINCT_AGENTS_LINE = re.compile(
    r"^-\s*\*\*distinct_agents\*\*:\s*(\d+)",
    re.MULTILINE,
)
_JUDGE_SCORE_LINE = re.compile(r"^-\s*\*\*judge分\*\*:\s*(.*)$", re.MULTILINE)
_AUDIT_SAMPLED_LINE = re.compile(
    r"^-\s*\*\*prescreen_audit_sampled\*\*:\s*(true|false)",
    re.MULTILINE | re.IGNORECASE,
)
_AUDIT_SAMPLE_RATE_LINE = re.compile(
    r"^-\s*\*\*prescreen_audit_sample_rate\*\*:\s*([\d.]+)",
    re.MULTILINE,
)
_SIMILARITY_BINS: tuple[tuple[str, float, float], ...] = (
    ("low", 0.0, 0.45),
    ("mid", 0.45, 0.50),
    ("high", 0.50, 1.01),
)
_AGENTS_TAG = re.compile(r"\[([^\]]+)\]")
_BASELINE_ONLY_TAG = re.compile(r"baseline\s+only", re.IGNORECASE)
_RUN_ID_LINE = re.compile(r"^-\s*run_id:\s*(\S+)", re.MULTILINE)
_REVIEW_RUN_SECTION = re.compile(r"^## (\d{2}-[\w-]+)\s*$", re.MULTILINE)
_BASELINE_AGENT = "A1"
_PERSONA_AGENT_PREFIX = "THE-"
_GATE_BATCH_PASS_RATE = 0.60
_D5_LOAD_REDUCTION_TARGET = 0.50
_PERSONA_BUCKETS = ("baseline-only", "persona-only", "both")


@dataclass
class CandidateScore:
    title: str
    tmdb_id: str
    triggered_by: list[str]
    also_baseline: bool
    score: int | None  # None = missing
    resonance_type: str | None = None  # canonical 2×2 type; None = unset
    pov_transform: bool | None = None  # optional POV变换 sub-label (score 2 only)
    quality_candidate: bool | None = None  # None = infer from heading agents
    similarity: float | None = None
    max_fit: float | None = None
    neutral_hit_rate: float | None = None
    neutral_hits: int | None = None
    neutral_total: int | None = None
    distinct_agents: int | None = None
    judge_score: int | None = None
    audit_sampled: bool | None = None
    audit_sample_rate: float | None = None

    @property
    def fit_sim_score(self) -> float | None:
        if self.max_fit is not None and self.similarity is not None:
            return self.max_fit * self.similarity
        return None

    @property
    def max_similarity(self) -> float | None:
        """Candidate-level max similarity (similarity-controlled diagnostics)."""
        return self.similarity

    @property
    def toned_convergence(self) -> bool:
        """True when ≥1 toned agent above floor (retrieve ``distinct_agents``)."""
        if self.distinct_agents is not None:
            return self.distinct_agents >= 1
        return False

    @property
    def neutral_vote(self) -> bool:
        if self.neutral_hits is not None:
            return self.neutral_hits >= 1
        if self.neutral_hit_rate is not None:
            return self.neutral_hit_rate > 0.0
        return False

    @property
    def is_pure_fact(self) -> bool:
        """ADR-0006 bucket ①: neutral vote, no toned convergence."""
        return self.neutral_vote and not self.toned_convergence

    @property
    def is_pure_emotion(self) -> bool:
        """ADR-0006 bucket ②: toned convergence, no neutral vote."""
        return self.toned_convergence and not self.neutral_vote

    @property
    def is_combo(self) -> bool:
        """ADR-0006 bucket ③: neutral vote + ≥1 toned convergence."""
        return self.neutral_vote and self.toned_convergence

    @property
    def is_neutral_only(self) -> bool:
        """Alias for pure_fact (diagnostic ② / legacy key)."""
        return self.is_pure_fact

    def eval_bucket(self) -> str | None:
        if self.is_combo:
            return "combo"
        if self.is_pure_fact:
            return "pure_fact"
        if self.is_pure_emotion:
            return "pure_emotion"
        return None


@dataclass
class RunSummary:
    path: str
    run_id: str
    candidates: list[CandidateScore] = field(default_factory=list)

    @property
    def has_any_score_2(self) -> bool:
        return any(c.score == 2 for c in self.candidates)

    @property
    def missing_count(self) -> int:
        return sum(1 for c in self.candidates if c.score is None)


def _strip_html_comments(text: str) -> str:
    return re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)


def _parse_agents_from_heading(heading: str) -> list[str]:
    match = _AGENTS_TAG.search(heading)
    if not match:
        return []
    tag = match.group(1).strip()
    if _BASELINE_ONLY_TAG.search(tag):
        return []
    return [part.strip() for part in tag.split(",") if part.strip()]


def _parse_score(raw_line: str) -> int | None:
    cleaned = _strip_html_comments(raw_line).strip()
    match = re.search(r"\b([012])\b", cleaned)
    if match:
        return int(match.group(1))
    return None


def _parse_resonance_type(raw_line: str) -> str | None:
    return parse_resonance_type(raw_line)


def _is_structural_resonance(cand: CandidateScore) -> bool:
    return cand.score == 2 and cand.resonance_type in _STRUCTURAL_TYPES


def _is_multi_agent_candidate(cand: CandidateScore) -> bool:
    return len(cand.triggered_by) >= 2


def _agent_set(cand: CandidateScore) -> set[str]:
    return {a.upper() for a in cand.triggered_by}


def _has_persona_agent(cand: CandidateScore) -> bool:
    return any(a.upper().startswith(_PERSONA_AGENT_PREFIX) for a in cand.triggered_by)


def _uses_persona_gate(runs: list[RunSummary]) -> bool:
    return any(_has_persona_agent(c) for r in runs for c in r.candidates)


def _uses_phase38_gate(runs: list[RunSummary]) -> bool:
    """ADR-0005 dual-diagnostic mode when neutral channel fields are present."""
    return any(
        c.neutral_hit_rate is not None or c.neutral_hits is not None
        for r in runs
        for c in r.candidates
    )


def _pearson(xs: list[float], ys: list[float]) -> float | None:
    n = len(xs)
    if n < 2:
        return None
    mean_x = sum(xs) / n
    mean_y = sum(ys) / n
    num = sum((x - mean_x) * (y - mean_y) for x, y in zip(xs, ys, strict=True))
    den_x = math.sqrt(sum((x - mean_x) ** 2 for x in xs))
    den_y = math.sqrt(sum((y - mean_y) ** 2 for y in ys))
    if den_x == 0 or den_y == 0:
        return None
    return num / (den_x * den_y)


def _partial_correlation(
    xs: list[float], ys: list[float], zs: list[float]
) -> float | None:
    """Pearson r(xs, ys) partialled on zs (control variable)."""
    r_xy = _pearson(xs, ys)
    r_xz = _pearson(xs, zs)
    r_yz = _pearson(ys, zs)
    if r_xy is None or r_xz is None or r_yz is None:
        return None
    denom = math.sqrt(max(0.0, (1.0 - r_xz * r_xz) * (1.0 - r_yz * r_yz)))
    if denom == 0:
        return None
    return (r_xy - r_xz * r_yz) / denom


def _similarity_bin_label(sim: float) -> str:
    for label, low, high in _SIMILARITY_BINS:
        if low <= sim < high:
            return label
    return "high"


def _structural_2_rates(
    candidates: list[CandidateScore],
) -> tuple[float, float, dict[str, int]]:
    scored = 0
    twos = 0
    structural_twos = 0
    for cand in candidates:
        if cand.score is None:
            continue
        scored += 1
        if cand.score == 2:
            twos += 1
            if _is_structural_resonance(cand):
                structural_twos += 1
    total_rate = twos / scored if scored else 0.0
    structural_rate = structural_twos / scored if scored else 0.0
    return total_rate, structural_rate, {
        "scored": scored,
        "twos": twos,
        "structural_twos": structural_twos,
    }


def _has_prescreen_data(runs: list[RunSummary]) -> bool:
    return any(c.judge_score is not None for r in runs for c in r.candidates)


def _prescreen_effective_weight(cand: CandidateScore) -> float | None:
    """Weight for prescreen-aware bucket denominators (ADR-0007 D4/D5)."""
    if cand.judge_score is None:
        return 1.0
    if cand.judge_score >= 1:
        return 1.0
    if cand.audit_sampled:
        rate = cand.audit_sample_rate
        if rate is not None and rate > 0:
            return 1.0 / rate
    return None


def _weighted_2_rates(
    candidates: list[CandidateScore],
    *,
    use_prescreen: bool,
) -> dict[str, Any]:
    if not use_prescreen:
        total_rate, structural_rate, counts = _structural_2_rates(candidates)
        return {
            "total_2_rate": total_rate,
            "structural_2_rate": structural_rate,
            "effective_weight": float(counts["scored"]),
            "prescreen_reweighted": False,
            **counts,
        }

    effective_weight = 0.0
    twos_weight = 0.0
    structural_twos_weight = 0.0
    scored = 0
    for cand in candidates:
        if cand.score is None:
            continue
        weight = _prescreen_effective_weight(cand)
        if weight is None:
            continue
        scored += 1
        effective_weight += weight
        if cand.score == 2:
            twos_weight += weight
            if _is_structural_resonance(cand):
                structural_twos_weight += weight

    total_rate = twos_weight / effective_weight if effective_weight else 0.0
    structural_rate = (
        structural_twos_weight / effective_weight if effective_weight else 0.0
    )
    return {
        "total_2_rate": total_rate,
        "structural_2_rate": structural_rate,
        "scored": scored,
        "twos": int(round(twos_weight)),
        "structural_twos": int(round(structural_twos_weight)),
        "effective_weight": effective_weight,
        "prescreen_reweighted": True,
    }


def _focal_channel_lift(
    runs: list[RunSummary],
    *,
    use_structural: bool,
    use_prescreen: bool,
) -> dict[str, Any]:
    buckets = _bucket_candidates(runs)
    focal_rows = buckets["combo"] + buckets["pure_emotion"]
    neutral_diag_rates = _weighted_2_rates(
        buckets["pure_fact"], use_prescreen=use_prescreen
    )
    focal_rates = _weighted_2_rates(focal_rows, use_prescreen=use_prescreen)
    metric = "structural_2_rate" if use_structural else "total_2_rate"
    focal_rate = focal_rates[metric]
    focal_weight = focal_rates["effective_weight"]

    # n1 / neutral-only remains visible as diagnostics, but no longer defines a pass/fail baseline.
    lift_ok = focal_weight > 0 and focal_rate > 0.0

    return {
        "focal_channel_has_signal": lift_ok,
        "metric": metric,
        "focal_channel": focal_rates,
        "neutral_diagnostic": neutral_diag_rates,
        "prescreen_reweighted": use_prescreen,
    }


def _split_runs_obs_holdout(
    runs: list[RunSummary],
) -> tuple[list[RunSummary], list[RunSummary]]:
    obs = [r for r in runs if r.run_id.startswith(OBS_RUN_PREFIXES)]
    holdout = [r for r in runs if not r.run_id.startswith(OBS_RUN_PREFIXES)]
    return obs, holdout


def _obs_holdout_consistent(obs_lift: bool | None, holdout_lift: bool | None) -> bool:
    if obs_lift is None or holdout_lift is None:
        return True
    return obs_lift == holdout_lift


def _workflow_prescreen_metrics(
    runs: list[RunSummary],
    calibration: dict[str, Any] | None,
) -> dict[str, Any]:
    judged = [
        (run.run_id, cand)
        for run in runs
        for cand in run.candidates
        if cand.judge_score is not None
    ]
    if not judged:
        return {
            "status": "pending",
            "note": "No judge/prescreen fields in scored review",
            "load_reduction_rate": None,
            "load_reduction_target": _D5_LOAD_REDUCTION_TARGET,
            "load_reduction_ok": None,
            "zero_human_2_killed": None,
            "judge_calibration_trusted": None,
            "pass": None,
        }

    total = len(judged)
    human_review_pool = sum(
        1
        for _, cand in judged
        if cand.judge_score >= 1
        or (cand.judge_score == 0 and cand.audit_sampled)
    )
    load_reduction = 1.0 - human_review_pool / total if total else None

    human_twos = [cand for _, cand in judged if cand.score == 2]
    reject_pile_human_twos = [cand for cand in human_twos if cand.judge_score == 0]
    zero_human_2_killed = len(reject_pile_human_twos) == 0

    cal_trusted: bool | None = None
    if calibration is not None:
        trust = calibration.get("trust_status")
        cal_trusted = trust == "采信" or trust == "trusted"

    load_ok = (
        load_reduction is not None and load_reduction >= _D5_LOAD_REDUCTION_TARGET
    )
    workflow_pass = load_ok and zero_human_2_killed and cal_trusted is True

    return {
        "status": "available",
        "load_reduction_rate": load_reduction,
        "load_reduction_target": _D5_LOAD_REDUCTION_TARGET,
        "load_reduction_ok": load_ok,
        "judged_candidates": total,
        "human_review_pool": human_review_pool,
        "zero_human_2_killed": zero_human_2_killed,
        "reject_pile_human_2_count": len(reject_pile_human_twos),
        "judge_calibration_trusted": cal_trusted,
        "pass": workflow_pass,
    }


def _d5_success_criteria(
    runs: list[RunSummary],
    *,
    use_structural: bool,
    calibration: dict[str, Any] | None,
) -> dict[str, Any]:
    use_prescreen = _has_prescreen_data(runs)
    full = _focal_channel_lift(
        runs, use_structural=use_structural, use_prescreen=use_prescreen
    )
    obs_runs, holdout_runs = _split_runs_obs_holdout(runs)
    obs_signal: bool | None = None
    holdout_signal: bool | None = None
    if obs_runs:
        obs_signal = _focal_channel_lift(
            obs_runs, use_structural=use_structural, use_prescreen=use_prescreen
        )["focal_channel_has_signal"]
    if holdout_runs:
        holdout_signal = _focal_channel_lift(
            holdout_runs, use_structural=use_structural, use_prescreen=use_prescreen
        )["focal_channel_has_signal"]

    obs_holdout_consistent = _obs_holdout_consistent(obs_signal, holdout_signal)
    resonance_pass = full["focal_channel_has_signal"] and obs_holdout_consistent

    workflow = _workflow_prescreen_metrics(runs, calibration)
    workflow_pass = workflow.get("pass")
    reasons = []
    if not full["focal_channel_has_signal"]:
        reasons.append(
            f"resonance: focal channel {full['metric']} "
            f"{full['focal_channel'][full['metric']]:.1%} has no usable signal "
            "(n1/pure_fact is diagnostic-only; prescreen reweighted when present)"
        )
    if not obs_holdout_consistent:
        reasons.append(
            f"resonance: obs/holdout split inconsistent "
            f"(obs={obs_signal}, holdout={holdout_signal})"
        )

    if workflow_pass is None:
        overall_pass = False
        verdict = "GATE_FAIL"
        reasons.append(
            "workflow criterion pending (no prescreen/judge fields or calibration)"
        )
    else:
        overall_pass = resonance_pass and bool(workflow_pass)
        verdict = "GATE_PASS" if overall_pass else "GATE_FAIL"
        if workflow_pass is False:
            if workflow.get("load_reduction_ok") is False:
                reasons.append(
                    f"workflow: load reduction "
                    f"{workflow.get('load_reduction_rate', 0):.1%} "
                    f"< target {_D5_LOAD_REDUCTION_TARGET:.0%}"
                )
            if workflow.get("zero_human_2_killed") is False:
                reasons.append(
                    "workflow: human=2 found in judge=0 reject pile "
                    f"({workflow.get('reject_pile_human_2_count', 0)} cases)"
                )
            if workflow.get("judge_calibration_trusted") is False:
                reasons.append("workflow: judge calibration not trusted (采信)")

    return {
        "pass": overall_pass,
        "verdict": verdict,
        "reasons": reasons,
        "resonance": {
            "pass": resonance_pass,
            "focal_channel_has_signal": full["focal_channel_has_signal"],
            "n1_diagnostic_only": True,
            "similarity_controlled": True,
            "obs_holdout_consistent": obs_holdout_consistent,
            "obs_focal_channel_has_signal": obs_signal,
            "holdout_focal_channel_has_signal": holdout_signal,
            "full_batch": full,
            "prescreen_reweighted": use_prescreen,
        },
        "workflow": workflow,
    }


def _diagnostic_neutral_hit_rate(runs: list[RunSummary]) -> dict[str, Any]:
    """Diagnostic ①: neutral_hit_rate vs 共振分, controlling max_similarity."""
    rows: list[dict[str, Any]] = []
    for run in runs:
        for cand in run.candidates:
            if (
                cand.score is None
                or cand.neutral_hit_rate is None
                or cand.max_similarity is None
            ):
                continue
            rows.append(
                {
                    "run_id": run.run_id,
                    "tmdb_id": cand.tmdb_id,
                    "neutral_hit_rate": cand.neutral_hit_rate,
                    "score": float(cand.score),
                    "max_similarity": cand.max_similarity,
                    "bin": _similarity_bin_label(cand.max_similarity),
                }
            )

    rates = [r["neutral_hit_rate"] for r in rows]
    scores = [r["score"] for r in rows]
    sims = [r["max_similarity"] for r in rows]
    by_bin: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_bin.setdefault(row["bin"], []).append(row)

    bin_correlations: dict[str, float | None] = {}
    for label, bin_rows in by_bin.items():
        bin_correlations[label] = _pearson(
            [r["neutral_hit_rate"] for r in bin_rows],
            [r["score"] for r in bin_rows],
        )

    return {
        "n": len(rows),
        "pearson_neutral_hit_rate_vs_score": _pearson(rates, scores),
        "partial_corr_neutral_hit_rate_vs_score_given_similarity": _partial_correlation(
            rates, scores, sims
        ),
        "similarity_bins": {
            label: {
                "n": len(bin_rows),
                "pearson": bin_correlations.get(label),
            }
            for label, bin_rows in by_bin.items()
        },
        "rows": rows,
    }


_THREE_BUCKETS = ("pure_fact", "pure_emotion", "combo")


def _bucket_candidates(
    runs: list[RunSummary],
) -> dict[str, list[CandidateScore]]:
    buckets: dict[str, list[CandidateScore]] = {name: [] for name in _THREE_BUCKETS}
    for run in runs:
        for cand in run.candidates:
            if cand.score is None:
                continue
            label = cand.eval_bucket()
            if label is not None:
                buckets[label].append(cand)
    return buckets


def _three_bucket_rates(runs: list[RunSummary]) -> dict[str, Any]:
    """ADR-0006 D4: pure_fact / pure_emotion / combo 2-rates, similarity-controlled."""
    buckets = _bucket_candidates(runs)
    use_prescreen = _has_prescreen_data(runs)
    rates: dict[str, Any] = {}
    reweighted_rates: dict[str, Any] = {}
    for name in _THREE_BUCKETS:
        total_rate, structural_rate, counts = _structural_2_rates(buckets[name])
        rates[name] = {
            "total_2_rate": total_rate,
            "structural_2_rate": structural_rate,
            **counts,
        }
        if use_prescreen:
            reweighted_rates[name] = _weighted_2_rates(
                buckets[name], use_prescreen=True
            )

    by_bin: dict[str, dict[str, list[CandidateScore]]] = {}
    for name in _THREE_BUCKETS:
        for cand in buckets[name]:
            if cand.max_similarity is None:
                continue
            label = _similarity_bin_label(cand.max_similarity)
            by_bin.setdefault(label, {b: [] for b in _THREE_BUCKETS})
            by_bin[label][name].append(cand)

    similarity_bins: dict[str, dict[str, Any]] = {}
    for label, bin_buckets in by_bin.items():
        bin_rates: dict[str, Any] = {}
        for name in _THREE_BUCKETS:
            _, structural_rate, counts = _structural_2_rates(bin_buckets[name])
            bin_rates[name] = {
                "structural_2_rate": structural_rate,
                "scored": counts["scored"],
            }
        similarity_bins[label] = bin_rates

    combo = rates["combo"]
    pure_fact = rates["pure_fact"]
    q2_combo_lift_ok = False
    if combo["scored"] > 0 and pure_fact["scored"] > 0:
        q2_combo_lift_ok = combo["structural_2_rate"] > pure_fact["structural_2_rate"]
    elif combo["scored"] > 0 and pure_fact["scored"] == 0:
        q2_combo_lift_ok = combo["structural_2_rate"] > 0.0

    result: dict[str, Any] = {
        "buckets": rates,
        "similarity_bins": similarity_bins,
        "q2_combo_lift_ok": q2_combo_lift_ok,
        "neutral_only_scored": pure_fact["scored"],
        "prescreen_reweighted": use_prescreen,
    }
    if use_prescreen:
        result["buckets_reweighted"] = reweighted_rates
        rw_combo = reweighted_rates.get("combo", {})
        rw_pure = reweighted_rates.get("pure_fact", {})
        rw_lift = False
        if rw_combo.get("effective_weight", 0) > 0 and rw_pure.get(
            "effective_weight", 0
        ) > 0:
            rw_lift = rw_combo["structural_2_rate"] > rw_pure["structural_2_rate"]
        elif rw_combo.get("effective_weight", 0) > 0:
            rw_lift = rw_combo["structural_2_rate"] > 0.0
        result["q2_combo_lift_ok_reweighted"] = rw_lift
    return result


def _diagnostic_toned_convergence(runs: list[RunSummary]) -> dict[str, Any]:
    """Diagnostic ② / Q2: combo precision above pure_fact, controlling similarity."""
    buckets = _bucket_candidates(runs)
    combo_rows = buckets["combo"]
    pure_fact_rows = buckets["pure_fact"]
    partial_rows: list[dict[str, float]] = []

    for run in runs:
        for cand in run.candidates:
            if cand.score is None or cand.max_similarity is None:
                continue
            if cand.neutral_vote or cand.toned_convergence:
                partial_rows.append(
                    {
                        "toned": 1.0 if cand.toned_convergence else 0.0,
                        "score": float(cand.score),
                        "max_similarity": cand.max_similarity,
                    }
                )

    c_total, c_structural, c_counts = _structural_2_rates(combo_rows)
    f_total, f_structural, f_counts = _structural_2_rates(pure_fact_rows)

    by_bin: dict[str, dict[str, list[CandidateScore]]] = {}
    for cand in combo_rows + pure_fact_rows:
        if cand.max_similarity is None:
            continue
        label = _similarity_bin_label(cand.max_similarity)
        bucket = by_bin.setdefault(label, {"combo": [], "pure_fact": []})
        if cand.is_combo:
            bucket["combo"].append(cand)
        elif cand.is_pure_fact:
            bucket["pure_fact"].append(cand)

    bin_lifts: dict[str, dict[str, Any]] = {}
    for label, bucket in by_bin.items():
        _, c_bin_struct, c_bin_counts = _structural_2_rates(bucket["combo"])
        _, f_bin_struct, f_bin_counts = _structural_2_rates(bucket["pure_fact"])
        bin_lifts[label] = {
            "combo_structural_2_rate": c_bin_struct,
            "pure_fact_structural_2_rate": f_bin_struct,
            "combo_scored": c_bin_counts["scored"],
            "pure_fact_scored": f_bin_counts["scored"],
            # legacy keys (combo≈quality, pure_fact≈neutral_only)
            "quality_structural_2_rate": c_bin_struct,
            "neutral_only_structural_2_rate": f_bin_struct,
            "quality_scored": c_bin_counts["scored"],
            "neutral_only_scored": f_bin_counts["scored"],
        }

    partial_corr = None
    if len(partial_rows) >= 2:
        partial_corr = _partial_correlation(
            [r["toned"] for r in partial_rows],
            [r["score"] for r in partial_rows],
            [r["max_similarity"] for r in partial_rows],
        )

    precision_lift_ok = False
    if c_counts["scored"] > 0 and f_counts["scored"] > 0:
        precision_lift_ok = c_structural > f_structural
    elif c_counts["scored"] > 0 and f_counts["scored"] == 0:
        precision_lift_ok = c_structural > 0.0

    return {
        "combo_total_2_rate": c_total,
        "combo_structural_2_rate": c_structural,
        "pure_fact_total_2_rate": f_total,
        "pure_fact_structural_2_rate": f_structural,
        "pure_emotion_scored": _structural_2_rates(buckets["pure_emotion"])[2]["scored"],
        "precision_lift_ok": precision_lift_ok,
        "q2_combo_lift_ok": precision_lift_ok,
        "partial_corr_toned_vs_score_given_similarity": partial_corr,
        "similarity_bins": bin_lifts,
        **{f"combo_{k}": v for k, v in c_counts.items()},
        **{f"pure_fact_{k}": v for k, v in f_counts.items()},
        # legacy keys for downstream readers
        "quality_total_2_rate": c_total,
        "quality_structural_2_rate": c_structural,
        "neutral_only_total_2_rate": f_total,
        "neutral_only_structural_2_rate": f_structural,
        **{f"quality_{k}": v for k, v in c_counts.items()},
        **{f"neutral_only_{k}": v for k, v in f_counts.items()},
    }


def _run_dir_from_summary(run: RunSummary) -> Path | None:
    path = Path(run.path)
    if not path.is_absolute():
        path = _REPO_ROOT / path
    if path.name == "candidates.md":
        return path.parent
    if path.parent.name == run.run_id:
        return path.parent
    return None


def _load_a1_hit_tmdb_ids(run: RunSummary) -> tuple[list[int], str]:
    """A1_hit ← retrieve-a1.json ``a1_oracle.hit_tmdb_ids``; fallback meta only."""
    run_dir = _run_dir_from_summary(run)
    if run_dir is None:
        return [], "missing"
    a1_path = run_dir / "retrieve-a1.json"
    if a1_path.is_file():
        data = json.loads(a1_path.read_text(encoding="utf-8"))
        a1_oracle = data.get("a1_oracle") or {}
        hit_ids = a1_oracle.get("hit_tmdb_ids")
        if isinstance(hit_ids, list):
            return [int(x) for x in hit_ids], "retrieve-a1.json"
        comparison = data.get("oracle_comparison")
        if isinstance(comparison, dict):
            legacy_ids = comparison.get("a1_hit_tmdb_ids")
            if isinstance(legacy_ids, list):
                return [int(x) for x in legacy_ids], "retrieve-a1.json#oracle_comparison"
    retrieve_path = run_dir / "retrieve.json"
    if retrieve_path.is_file():
        data = json.loads(retrieve_path.read_text(encoding="utf-8"))
        comparison = data.get("oracle_comparison")
        if isinstance(comparison, dict):
            legacy_ids = comparison.get("a1_hit_tmdb_ids")
            if isinstance(legacy_ids, list):
                return [int(x) for x in legacy_ids], "retrieve.json#oracle_comparison"
        a1_oracle = data.get("a1_oracle") or {}
        hit_ids = a1_oracle.get("hit_tmdb_ids")
        if isinstance(hit_ids, list):
            return [int(x) for x in hit_ids], "retrieve.json#a1_oracle"
    meta_path = run_dir / "a1-baseline-meta.json"
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        hit_ids = meta.get("a1_hit_tmdb_ids")
        if isinstance(hit_ids, list):
            return [int(x) for x in hit_ids], "a1-baseline-meta.json"
    return [], "missing"


def _load_n1_neutral_union(run: RunSummary) -> set[int]:
    """Union of hits from 12 neutral ``n1`` pseudos in ``retrieve.json`` ``per_agent``."""
    run_dir = _run_dir_from_summary(run)
    if run_dir is None:
        return set()
    retrieve_path = run_dir / "retrieve.json"
    if not retrieve_path.is_file():
        return set()
    data = json.loads(retrieve_path.read_text(encoding="utf-8"))
    hits: set[int] = set()
    for agent in data.get("per_agent", []):
        if agent.get("role") != "neutral":
            continue
        for pseudo in agent.get("pseudos", []):
            if pseudo.get("pseudo_id") != "n1":
                continue
            for hit in pseudo.get("hits", []):
                tmdb_id = hit.get("tmdb_id")
                if tmdb_id is not None:
                    hits.add(int(tmdb_id))
    return hits


def _a1_two_for_run(run: RunSummary, a1_hit_ids: set[int]) -> set[int]:
    """Human 共振分=2 among A1_hit for this (run_id, tmdb_id)."""
    twos: set[int] = set()
    for cand in run.candidates:
        if cand.score != 2:
            continue
        try:
            tmdb_id = int(cand.tmdb_id)
        except (TypeError, ValueError):
            continue
        if tmdb_id in a1_hit_ids:
            twos.add(tmdb_id)
    return twos


def q1_prime_a1_two_neutral_coverage(
    runs: list[RunSummary],
) -> dict[str, Any]:
    """Q1′: 12 neutral n1 hits cover all A1 movies humans scored 2?"""
    per_run: list[dict[str, Any]] = []
    global_miss_list: list[dict[str, Any]] = []
    runs_with_a1_two = 0
    runs_with_a1_two_passed = 0

    for run in runs:
        a1_hit_ids, a1_source = _load_a1_hit_tmdb_ids(run)
        a1_hit_set = set(a1_hit_ids)
        n1_union = _load_n1_neutral_union(run)
        a1_two = _a1_two_for_run(run, a1_hit_set)
        misses = sorted(a1_two - n1_union)
        vacuous = len(a1_two) == 0
        passed = vacuous or not misses

        if not vacuous:
            runs_with_a1_two += 1
            if passed:
                runs_with_a1_two_passed += 1

        per_run.append(
            {
                "run_id": run.run_id,
                "a1_hit_source": a1_source,
                "a1_hit_tmdb_ids": sorted(a1_hit_set),
                "a1_hit_count": len(a1_hit_set),
                "a1_two_tmdb_ids": sorted(a1_two),
                "a1_two_count": len(a1_two),
                "n1_neutral_union_tmdb_ids": sorted(n1_union),
                "n1_neutral_union_count": len(n1_union),
                "misses_tmdb_ids": misses,
                "miss_count": len(misses),
                "vacuous_pass": vacuous,
                "q1_prime_pass": passed,
            }
        )
        for tmdb_id in misses:
            global_miss_list.append({"run_id": run.run_id, "tmdb_id": tmdb_id})

    per_run_pass_rate = (
        runs_with_a1_two_passed / runs_with_a1_two if runs_with_a1_two else None
    )
    batch_pass = (
        runs_with_a1_two_passed == runs_with_a1_two if runs_with_a1_two else True
    )

    return {
        "status": "available",
        "question": (
            "Can 12 neutral (n1) hits cover all A1 movies that humans scored 2?"
        ),
        "per_run": per_run,
        "runs_with_a1_two": runs_with_a1_two,
        "runs_with_a1_two_passed": runs_with_a1_two_passed,
        "per_run_pass_rate": per_run_pass_rate,
        "global_miss_list": global_miss_list,
        "global_miss_count": len(global_miss_list),
        "q1_prime_pass": batch_pass,
        "batch_rule": (
            "PASS if all runs with |A1_two|>0 satisfy A1_two ⊆ N "
            "(vacuous pass per run when A1_two empty)"
        ),
    }


def _legacy_candidate_neutral_union(run: RunSummary) -> set[int]:
    """Candidate-pool neutral union (neutral_hits≥1) for legacy Q1 diagnostic."""
    run_dir = _run_dir_from_summary(run)
    if run_dir is None:
        return set()
    retrieve_path = run_dir / "retrieve.json"
    if not retrieve_path.is_file():
        return set()
    data = json.loads(retrieve_path.read_text(encoding="utf-8"))
    ids: set[int] = set()
    for cand in data.get("candidates", []):
        if int(cand.get("neutral_hits") or 0) < 1:
            continue
        tmdb_id = cand.get("tmdb_id")
        if tmdb_id is not None:
            ids.add(int(tmdb_id))
    return ids


def _load_legacy_oracle_row(run: RunSummary) -> dict[str, Any] | None:
    """Legacy Q1 recall: candidate-pool neutral union ⊇ all A1 hits."""
    a1_hit_ids, a1_source = _load_a1_hit_tmdb_ids(run)
    if not a1_hit_ids and a1_source == "missing":
        return None
    a1_hit_set = set(a1_hit_ids)
    run_dir = _run_dir_from_summary(run)
    if run_dir is not None:
        retrieve_path = run_dir / "retrieve.json"
        if retrieve_path.is_file():
            data = json.loads(retrieve_path.read_text(encoding="utf-8"))
            comparison = data.get("oracle_comparison")
            if isinstance(comparison, dict) and comparison.get("a1_hit_tmdb_ids"):
                return {"run_id": run.run_id, "a1_hit_source": a1_source, **comparison}
    neutral_union = _legacy_candidate_neutral_union(run)
    if not a1_hit_set:
        superset: bool | None = True if neutral_union else None
    else:
        superset = a1_hit_set <= neutral_union
    return {
        "run_id": run.run_id,
        "a1_hit_source": a1_source,
        "a1_hit_tmdb_ids": sorted(a1_hit_set),
        "neutral_union_tmdb_ids": sorted(neutral_union),
        "shared_tmdb_ids": sorted(a1_hit_set & neutral_union),
        "a1_only_tmdb_ids": sorted(a1_hit_set - neutral_union),
        "neutral_only_tmdb_ids": sorted(neutral_union - a1_hit_set),
        "neutral_union_superset_of_a1_hits": superset,
        "a1_hit_count": len(a1_hit_set),
        "neutral_union_hit_count": len(neutral_union),
    }


def _a1_reference_diagnostics(
    runs: list[RunSummary],
    three_bucket: dict[str, Any] | None,
) -> dict[str, Any]:
    """A1 read-only quality reference (ADR-0007 D5) — not used in any gate."""
    q1_prime = q1_prime_a1_two_neutral_coverage(runs)

    legacy_per_run: list[dict[str, Any]] = []
    for run in runs:
        row = _load_legacy_oracle_row(run)
        if row is not None:
            legacy_per_run.append(row)

    if not legacy_per_run:
        q1_legacy: dict[str, Any] = {
            "status": "pending",
            "note": "No retrieve-a1.json / a1-baseline-meta in run dirs",
            "runs_with_oracle_data": 0,
            "neutral_union_superset_of_a1_hits": None,
            "q1_recall_superset_ok": None,
        }
    else:
        superset_flags = [
            row.get("neutral_union_superset_of_a1_hits")
            for row in legacy_per_run
            if row.get("neutral_union_superset_of_a1_hits") is not None
        ]
        q1_recall_ok = all(superset_flags) if superset_flags else None
        q1_legacy = {
            "status": "available",
            "runs_with_oracle_data": len(legacy_per_run),
            "per_run": legacy_per_run,
            "neutral_union_superset_of_a1_hits": q1_recall_ok,
            "q1_recall_superset_ok": q1_recall_ok,
            "note": (
                "Legacy diagnostic only (candidate-pool neutral union ⊇ all A1 hits)"
            ),
        }

    pure_fact = (three_bucket or {}).get("buckets", {}).get("pure_fact", {})
    combo = (three_bucket or {}).get("buckets", {}).get("combo", {})

    return {
        "status": "reference_only",
        "role": "read_only_quality_reference",
        "q1_prime_coverage": q1_prime,
        "q1_legacy_recall": q1_legacy,
        "runs_with_oracle_data": legacy_per_run and len(legacy_per_run) or 0,
        "neutral_union_superset_of_a1_hits": q1_legacy.get(
            "neutral_union_superset_of_a1_hits"
        ),
        "q1_recall_superset_ok": q1_legacy.get("q1_recall_superset_ok"),
        "pure_fact_structural_2_rate": pure_fact.get("structural_2_rate", 0.0),
        "combo_structural_2_rate": combo.get("structural_2_rate", 0.0),
        "note": (
            "A1 oracle metrics are read-only reference only (ADR-0007 D5). "
            "Not used in success criteria."
        ),
    }


def _a1_oracle_comparison(
    runs: list[RunSummary],
    three_bucket: dict[str, Any] | None,
) -> dict[str, Any]:
    """Backward-compatible alias for ``_a1_reference_diagnostics``."""
    ref = _a1_reference_diagnostics(runs, three_bucket)
    ref["q1_prime"] = ref["q1_prime_coverage"]
    return ref


def _classify_persona_bucket(cand: CandidateScore) -> str | None:
    agents = _agent_set(cand)
    has_baseline = _BASELINE_AGENT in agents
    has_persona = bool(agents) and any(
        a.startswith(_PERSONA_AGENT_PREFIX) for a in agents
    )
    if has_baseline and not has_persona:
        return "baseline-only"
    if has_persona and not has_baseline:
        return "persona-only"
    if has_baseline and has_persona:
        return "both"
    return None


def _split_candidate_blocks(text: str) -> list[tuple[str, str]]:
    """Return (heading_line, block_body) for each ### candidate section."""
    section_match = re.search(r"^##\s*候选星轨.*$", text, re.MULTILINE)
    section = text[section_match.start() :] if section_match else text

    parts = re.split(r"(?=^###\s+)", section, flags=re.MULTILINE)
    blocks: list[tuple[str, str]] = []
    for part in parts[1:]:
        lines = part.splitlines()
        if not lines:
            continue
        heading = lines[0]
        body = "\n".join(lines[1:])
        if not _TMDB_LINE.search(body):
            continue
        blocks.append((heading, body))
    return blocks


def _infer_run_id(path: Path, text: str) -> str:
    run_id_match = _RUN_ID_LINE.search(text)
    if run_id_match:
        return run_id_match.group(1)
    if path.name == "candidates.md" and path.parent.name != path.parent.parent.name:
        return path.parent.name
    return path.stem


def parse_eval_markdown(path: Path, text: str) -> RunSummary:
    run_id = _infer_run_id(path, text)

    candidates: list[CandidateScore] = []
    for heading, body in _split_candidate_blocks(text):
        title = heading.removeprefix("### ").strip()
        tmdb_match = _TMDB_LINE.search(body)
        tmdb_id = tmdb_match.group(1) if tmdb_match else ""
        baseline_match = _ALSO_BASELINE_LINE.search(body)
        also_baseline = (
            baseline_match.group(1).lower() == "true" if baseline_match else False
        )
        triggered_by = _parse_agents_from_heading(title)

        quality_candidate: bool | None = None
        quality_match = _QUALITY_CANDIDATE_LINE.search(body)
        if quality_match:
            quality_candidate = quality_match.group(1).lower() == "true"
        else:
            zh_match = _QUALITY_ZH_LINE.search(body)
            if zh_match:
                quality_candidate = zh_match.group(1).lower() == "true"

        neutral_hit_rate: float | None = None
        nhr_match = _NEUTRAL_HIT_RATE_LINE.search(body)
        if nhr_match:
            neutral_hit_rate = float(nhr_match.group(1))

        neutral_hits: int | None = None
        nh_match = _NEUTRAL_HITS_LINE.search(body)
        if nh_match:
            neutral_hits = int(nh_match.group(1))

        neutral_total: int | None = None
        nt_match = _NEUTRAL_TOTAL_LINE.search(body)
        if nt_match:
            neutral_total = int(nt_match.group(1))

        distinct_agents: int | None = None
        da_match = _DISTINCT_AGENTS_LINE.search(body)
        if da_match:
            distinct_agents = int(da_match.group(1))

        judge_score: int | None = None
        judge_match = _JUDGE_SCORE_LINE.search(body)
        if judge_match:
            judge_score = _parse_score(judge_match.group(1))

        audit_sampled: bool | None = None
        audit_match = _AUDIT_SAMPLED_LINE.search(body)
        if audit_match:
            audit_sampled = audit_match.group(1).lower() == "true"

        audit_sample_rate: float | None = None
        rate_match = _AUDIT_SAMPLE_RATE_LINE.search(body)
        if rate_match:
            audit_sample_rate = float(rate_match.group(1))

        score: int | None = None
        score_match = _SCORE_LINE.search(body)
        if score_match:
            score = _parse_score(score_match.group(1))

        resonance_type: str | None = None
        type_match = _RESONANCE_TYPE_LINE.search(body)
        if type_match:
            resonance_type = _parse_resonance_type(type_match.group(1))

        pov_transform: bool | None = None
        pov_match = _POV_TRANSFORM_LINE.search(body)
        if pov_match:
            pov_transform = parse_pov_transform(pov_match.group(1))
        if score is not None and resonance_type is not None:
            pov_transform = validate_pov_transform_sub_label(
                score, resonance_type, pov_transform
            )

        similarity: float | None = None
        sim_match = _SIMILARITY_LINE.search(body)
        if sim_match:
            similarity = float(sim_match.group(1))

        fits = [float(v) for v in _FIT_VALUE.findall(body)]
        max_fit = max(fits) if fits else None

        candidates.append(
            CandidateScore(
                title=title,
                tmdb_id=tmdb_id,
                triggered_by=triggered_by,
                also_baseline=also_baseline,
                score=score,
                resonance_type=resonance_type,
                pov_transform=pov_transform,
                quality_candidate=quality_candidate,
                similarity=similarity,
                max_fit=max_fit,
                neutral_hit_rate=neutral_hit_rate,
                neutral_hits=neutral_hits,
                neutral_total=neutral_total,
                distinct_agents=distinct_agents,
                judge_score=judge_score,
                audit_sampled=audit_sampled,
                audit_sample_rate=audit_sample_rate,
            )
        )

    return RunSummary(path=str(path), run_id=run_id, candidates=candidates)


def parse_unified_review(path: Path, text: str) -> list[RunSummary]:
    """Parse phase3.7-style high-hit-score-review.md (one file, many runs)."""
    runs: list[RunSummary] = []
    matches = list(_REVIEW_RUN_SECTION.finditer(text))
    for index, match in enumerate(matches):
        run_id = match.group(1)
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        section = text[start:end]
        fake_path = path.parent / run_id / "candidates.md"
        run = parse_eval_markdown(fake_path, section)
        run.run_id = run_id
        run.path = str(fake_path)
        runs.append(run)
    return runs


def _any_resonance_types_filled(runs: list[RunSummary]) -> bool:
    return any(
        cand.resonance_type is not None
        for run in runs
        for cand in run.candidates
    )


def _bucket_rates(
    runs: list[RunSummary],
) -> tuple[float, float, float, float, dict[str, int]]:
    """Return single/multi total and structural 2-rates plus counts."""
    single_scored = 0
    single_twos = 0
    single_structural_twos = 0
    multi_scored = 0
    multi_twos = 0
    multi_structural_twos = 0

    for run in runs:
        for cand in run.candidates:
            if cand.score is None:
                continue
            multi = _is_multi_agent_candidate(cand)
            if multi:
                multi_scored += 1
                if cand.score == 2:
                    multi_twos += 1
                    if _is_structural_resonance(cand):
                        multi_structural_twos += 1
            else:
                single_scored += 1
                if cand.score == 2:
                    single_twos += 1
                    if _is_structural_resonance(cand):
                        single_structural_twos += 1

    single_rate = single_twos / single_scored if single_scored else 0.0
    multi_rate = multi_twos / multi_scored if multi_scored else 0.0
    single_structural_rate = (
        single_structural_twos / single_scored if single_scored else 0.0
    )
    multi_structural_rate = (
        multi_structural_twos / multi_scored if multi_scored else 0.0
    )
    counts = {
        "single_scored": single_scored,
        "single_twos": single_twos,
        "single_structural_twos": single_structural_twos,
        "multi_scored": multi_scored,
        "multi_twos": multi_twos,
        "multi_structural_twos": multi_structural_twos,
    }
    return (
        single_rate,
        multi_rate,
        single_structural_rate,
        multi_structural_rate,
        counts,
    )


def _persona_bucket_rates(
    runs: list[RunSummary],
) -> tuple[float, float, float, float, dict[str, int]]:
    """Baseline vs persona structural/total 2-rates (Phase 3.7 gate 2).

    Gate comparison uses ``also_baseline`` (A1 retrieve path) vs persona-exclusive
    hits — matches retrieve semantics when review scores are mostly multi-agent.
    Agent-heading buckets (baseline-only / persona-only / both) are reported
    separately for diagnostics.
    """
    stats = {name: {"scored": 0, "twos": 0, "structural_twos": 0} for name in _PERSONA_BUCKETS}
    a1_path = {"scored": 0, "twos": 0, "structural_twos": 0}
    persona_path = {"scored": 0, "twos": 0, "structural_twos": 0}

    for run in runs:
        for cand in run.candidates:
            if cand.score is None:
                continue
            bucket = _classify_persona_bucket(cand)
            if bucket is not None:
                row = stats[bucket]
                row["scored"] += 1
                if cand.score == 2:
                    row["twos"] += 1
                    if _is_structural_resonance(cand):
                        row["structural_twos"] += 1

            path_row = a1_path if cand.also_baseline else persona_path
            path_row["scored"] += 1
            if cand.score == 2:
                path_row["twos"] += 1
                if _is_structural_resonance(cand):
                    path_row["structural_twos"] += 1

    baseline = stats["baseline-only"]
    persona_only = stats["persona-only"]
    both = stats["both"]

    baseline_2_rate = a1_path["twos"] / a1_path["scored"] if a1_path["scored"] else 0.0
    persona_2_rate = (
        persona_path["twos"] / persona_path["scored"] if persona_path["scored"] else 0.0
    )
    baseline_structural_rate = (
        a1_path["structural_twos"] / a1_path["scored"] if a1_path["scored"] else 0.0
    )
    persona_structural_rate = (
        persona_path["structural_twos"] / persona_path["scored"]
        if persona_path["scored"]
        else 0.0
    )
    counts = {
        "baseline_only_scored": baseline["scored"],
        "baseline_only_twos": baseline["twos"],
        "baseline_only_structural_twos": baseline["structural_twos"],
        "persona_only_scored": persona_only["scored"],
        "persona_only_twos": persona_only["twos"],
        "persona_only_structural_twos": persona_only["structural_twos"],
        "both_scored": both["scored"],
        "both_twos": both["twos"],
        "both_structural_twos": both["structural_twos"],
        "a1_path_scored": a1_path["scored"],
        "a1_path_twos": a1_path["twos"],
        "a1_path_structural_twos": a1_path["structural_twos"],
        "persona_path_scored": persona_path["scored"],
        "persona_path_twos": persona_path["twos"],
        "persona_path_structural_twos": persona_path["structural_twos"],
        "persona_touched_scored": persona_only["scored"] + both["scored"],
        "persona_touched_twos": persona_only["twos"] + both["twos"],
        "persona_touched_structural_twos": (
            persona_only["structural_twos"] + both["structural_twos"]
        ),
    }
    return (
        baseline_2_rate,
        persona_2_rate,
        baseline_structural_rate,
        persona_structural_rate,
        counts,
    )


def _fit_sim_ranking(runs: list[RunSummary]) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for run in runs:
        for cand in run.candidates:
            if cand.fit_sim_score is None:
                continue
            ranked.append(
                {
                    "run_id": run.run_id,
                    "tmdb_id": cand.tmdb_id,
                    "title": cand.title,
                    "max_fit": cand.max_fit,
                    "similarity": cand.similarity,
                    "fit_sim_score": round(cand.fit_sim_score, 4),
                    "score": cand.score,
                    "resonance_type": cand.resonance_type,
                    "pov_transform": cand.pov_transform,
                }
            )
    ranked.sort(key=lambda row: row["fit_sim_score"], reverse=True)
    return ranked


def summarize_runs(
    runs: list[RunSummary],
    *,
    calibration: dict[str, Any] | None = None,
) -> dict[str, Any]:
    total_runs = len(runs)
    runs_with_2 = sum(1 for r in runs if r.has_any_score_2)
    batch_pass_rate = runs_with_2 / total_runs if total_runs else 0.0
    (
        single_2_rate,
        multi_2_rate,
        single_structural_2_rate,
        multi_structural_2_rate,
        bucket_counts,
    ) = _bucket_rates(runs)
    missing_total = sum(r.missing_count for r in runs)
    use_structural_gate = _any_resonance_types_filled(runs)
    phase38_gate = _uses_phase38_gate(runs)
    persona_gate = _uses_persona_gate(runs) and not phase38_gate
    gate_compare_mode = (
        "combo_vs_pure_fact"
        if phase38_gate
        else ("persona_vs_baseline" if persona_gate else "multi_vs_single")
    )

    persona_counts: dict[str, int] = {}
    baseline_2_rate = 0.0
    persona_2_rate = 0.0
    baseline_structural_2_rate = 0.0
    persona_structural_2_rate = 0.0
    if persona_gate:
        (
            baseline_2_rate,
            persona_2_rate,
            baseline_structural_2_rate,
            persona_structural_2_rate,
            persona_counts,
        ) = _persona_bucket_rates(runs)

    diagnostic_1 = _diagnostic_neutral_hit_rate(runs) if phase38_gate else None
    diagnostic_2 = _diagnostic_toned_convergence(runs) if phase38_gate else None
    three_bucket = _three_bucket_rates(runs) if phase38_gate else None
    a1_reference = (
        _a1_reference_diagnostics(runs, three_bucket) if phase38_gate else None
    )
    d5_criteria = (
        _d5_success_criteria(
            runs,
            use_structural=use_structural_gate,
            calibration=calibration,
        )
        if phase38_gate
        else None
    )

    gate_reasons: list[str] = []
    batch_ok = batch_pass_rate >= _GATE_BATCH_PASS_RATE

    if phase38_gate and d5_criteria is not None:
        rate_ok = bool(d5_criteria["resonance"]["focal_channel_has_signal"])
        baseline_gate_rate = d5_criteria["resonance"]["full_batch"]["neutral_diagnostic"][
            d5_criteria["resonance"]["full_batch"]["metric"]
        ]
        persona_gate_rate = d5_criteria["resonance"]["full_batch"]["focal_channel"][
            d5_criteria["resonance"]["full_batch"]["metric"]
        ]
        rate_metric = d5_criteria["resonance"]["full_batch"]["metric"]
        gate_pass = bool(d5_criteria["pass"])
        gate_reasons = list(d5_criteria["reasons"])
    elif persona_gate:
        if use_structural_gate:
            rate_ok = persona_structural_2_rate > baseline_structural_2_rate
            baseline_gate_rate = baseline_structural_2_rate
            persona_gate_rate = persona_structural_2_rate
            rate_metric = "structural_2_rate"
        else:
            rate_ok = persona_2_rate > baseline_2_rate
            baseline_gate_rate = baseline_2_rate
            persona_gate_rate = persona_2_rate
            rate_metric = "total_2_rate"
    elif use_structural_gate:
        rate_ok = single_structural_2_rate < multi_structural_2_rate
        baseline_gate_rate = single_structural_2_rate
        persona_gate_rate = multi_structural_2_rate
        rate_metric = "structural_2_rate"
    else:
        rate_ok = single_2_rate < multi_2_rate
        baseline_gate_rate = single_2_rate
        persona_gate_rate = multi_2_rate
        rate_metric = "total_2_rate"

    if phase38_gate and d5_criteria is not None:
        pass
    else:
        if not batch_ok:
            gate_reasons.append(
                f"batch pass rate {batch_pass_rate:.1%} < {_GATE_BATCH_PASS_RATE:.0%} "
                f"({runs_with_2}/{total_runs} runs with >=1 score-2)"
            )
        if not rate_ok:
            if persona_gate:
                gate_reasons.append(
                    f"persona_path_{rate_metric} {persona_gate_rate:.1%} not > "
                    f"a1_path_{rate_metric} {baseline_gate_rate:.1%}"
                )
            else:
                gate_reasons.append(
                    f"single_{rate_metric} {baseline_gate_rate:.1%} not < "
                    f"multi_{rate_metric} {persona_gate_rate:.1%}"
                )
        gate_pass = batch_ok and rate_ok

    global_block: dict[str, Any] = {
        "total_runs": total_runs,
        "runs_with_score_2": runs_with_2,
        "batch_pass_rate": batch_pass_rate,
        "missing_scores_total": missing_total,
        "single_2_rate": single_2_rate,
        "multi_2_rate": multi_2_rate,
        "single_structural_2_rate": single_structural_2_rate,
        "multi_structural_2_rate": multi_structural_2_rate,
        "resonance_types_filled": use_structural_gate,
        "phase38_gate": phase38_gate,
        "persona_gate": persona_gate,
        "baseline_2_rate": baseline_2_rate,
        "persona_touched_2_rate": persona_2_rate,
        "baseline_structural_2_rate": baseline_structural_2_rate,
        "persona_touched_structural_2_rate": persona_structural_2_rate,
        **bucket_counts,
        **persona_counts,
    }
    if diagnostic_1 is not None:
        global_block["diagnostic_1_neutral_hit_rate"] = diagnostic_1
    if diagnostic_2 is not None:
        global_block["diagnostic_2_toned_convergence"] = diagnostic_2
    if three_bucket is not None:
        global_block["three_bucket"] = three_bucket
    if d5_criteria is not None:
        global_block["d5_success_criteria"] = d5_criteria

    result: dict[str, Any] = {
        "runs": [
            {
                "path": r.path,
                "run_id": r.run_id,
                "has_any_score_2": r.has_any_score_2,
                "missing_count": r.missing_count,
                "candidate_count": len(r.candidates),
            }
            for r in runs
        ],
        "global": global_block,
        "fit_sim_ranking": _fit_sim_ranking(runs),
        "gate": {
            "pass": gate_pass,
            "verdict": "GATE_PASS" if gate_pass else "GATE_FAIL",
            "compare_mode": gate_compare_mode,
            "rate_metric": rate_metric,
            "reasons": gate_reasons,
        },
    }
    if d5_criteria is not None:
        result["success_criteria"] = d5_criteria
        result["gate"]["verdict"] = d5_criteria["verdict"]
        result["gate"]["pass"] = d5_criteria["pass"]
        result["gate"]["compare_mode"] = "d5_success_criteria"
    if a1_reference is not None:
        result["a1_reference"] = a1_reference
        result["a1_oracle"] = _a1_oracle_comparison(runs, three_bucket)
        result["a1_superset"] = result["a1_oracle"]
    return result


def _format_stdout(report: dict[str, Any]) -> str:
    lines: list[str] = []
    g = report["global"]
    lines.append(f"Eval runs: {g['total_runs']}")
    lines.append("")

    for run in report["runs"]:
        flag = "yes" if run["has_any_score_2"] else "no"
        missing_note = (
            f", {run['missing_count']} missing" if run["missing_count"] else ""
        )
        lines.append(
            f"  {run['run_id']}: has_any_score_2={flag}"
            f" ({run['candidate_count']} candidates{missing_note})"
        )

    lines.append("")
    lines.append(
        f"Batch pass rate: {g['batch_pass_rate']:.1%} "
        f"({g['runs_with_score_2']}/{g['total_runs']} runs with >=1 score-2)"
    )

    compare_mode = report["gate"].get("compare_mode", "multi_vs_single")
    if g.get("phase38_gate"):
        d1 = g.get("diagnostic_1_neutral_hit_rate") or {}
        d2 = g.get("diagnostic_2_toned_convergence") or {}
        tb = g.get("three_bucket") or {}
        lines.append(
            "Diagnostic ① (neutral_hit_rate vs 共振 · max_similarity controlled): "
            f"n={d1.get('n', 0)}"
        )
        pc = d1.get("partial_corr_neutral_hit_rate_vs_score_given_similarity")
        if pc is not None:
            lines.append(
                f"  partial r(neutral_hit_rate, score | similarity)={pc:.4f}"
            )
        else:
            lines.append("  partial r(neutral_hit_rate, score | similarity)=insufficient n")
        pf_scored = tb.get("neutral_only_scored", d2.get("pure_fact_scored", 0))
        lines.append(
            "Diagnostic ② / Q2 (combo vs pure_fact · max_similarity controlled): "
            f"combo structural 2-rate {d2.get('combo_structural_2_rate', 0):.1%} "
            f"({d2.get('combo_structural_twos', 0)}/{d2.get('combo_scored', 0)}) vs "
            f"pure-fact {d2.get('pure_fact_structural_2_rate', 0):.1%} "
            f"({d2.get('pure_fact_structural_twos', 0)}/{pf_scored})"
        )
        pt = d2.get("partial_corr_toned_vs_score_given_similarity")
        if pt is not None:
            lines.append(f"  partial r(toned, score | similarity)={pt:.4f}")
        bucket_rates = tb.get("buckets") or {}
        if bucket_rates:
            lines.append("Three-bucket structural 2-rates:")
            for name in _THREE_BUCKETS:
                row = bucket_rates.get(name, {})
                lines.append(
                    f"  {name}: {row.get('structural_2_rate', 0):.1%} "
                    f"({row.get('structural_twos', 0)}/{row.get('scored', 0)} scored)"
                )
        d5 = report.get("success_criteria") or g.get("d5_success_criteria") or {}
        res = d5.get("resonance") or {}
        wf = d5.get("workflow") or {}
        lines.append("D5 success · resonance: focal channel signal (n1 diagnostic-only)")
        if res:
            full = res.get("full_batch") or {}
            metric = full.get("metric", "structural_2_rate")
            focal_r = (full.get("focal_channel") or {}).get(metric, 0)
            neutral_r = (full.get("neutral_diagnostic") or {}).get(metric, 0)
            rw_note = (
                " · prescreen reweighted"
                if res.get("prescreen_reweighted")
                else ""
            )
            lines.append(
                f"  {metric}: focal channel {focal_r:.1%}; "
                f"n1 neutral diagnostic {neutral_r:.1%}"
                f"{rw_note} · pass={res.get('focal_channel_has_signal')}"
            )
            lines.append(
                f"  obs/holdout consistent: {res.get('obs_holdout_consistent')} "
                f"(obs={res.get('obs_focal_channel_has_signal')}, "
                f"holdout={res.get('holdout_focal_channel_has_signal')})"
            )
        lines.append(
            "D5 success · workflow: load reduction & zero human-2 killed & calibration"
        )
        if wf.get("status") == "pending":
            lines.append(f"  workflow: pending ({wf.get('note', '')})")
        else:
            lr = wf.get("load_reduction_rate")
            lr_txt = f"{lr:.1%}" if lr is not None else "n/a"
            lines.append(
                f"  load reduction {lr_txt} "
                f"(target {wf.get('load_reduction_target', 0):.0%}) · "
                f"ok={wf.get('load_reduction_ok')}"
            )
            lines.append(
                f"  zero human-2 killed: {wf.get('zero_human_2_killed')} · "
                f"judge calibration trusted: {wf.get('judge_calibration_trusted')}"
            )
        a1_ref = report.get("a1_reference") or {}
        if a1_ref:
            lines.append("A1 reference (read-only · not a gate):")
            if a1_ref.get("note"):
                lines.append(f"  {a1_ref['note']}")
        tb_rw = tb.get("buckets_reweighted")
        if tb_rw:
            lines.append("Three-bucket prescreen-reweighted structural 2-rates:")
            for name in _THREE_BUCKETS:
                row = tb_rw.get(name, {})
                lines.append(
                    f"  {name}: {row.get('structural_2_rate', 0):.1%} "
                    f"(effective_weight={row.get('effective_weight', 0):.2f})"
                )
    elif g.get("persona_gate"):
        lines.append(
            f"baseline_structural_2_rate: {g['baseline_structural_2_rate']:.1%} "
            f"({g['a1_path_structural_twos']}/{g['a1_path_scored']} also_baseline=true)"
        )
        lines.append(
            f"persona_path_structural_2_rate: {g['persona_touched_structural_2_rate']:.1%} "
            f"({g['persona_path_structural_twos']}/{g['persona_path_scored']} "
            "also_baseline=false)"
        )
        lines.append(
            f"baseline_2_rate: {g['baseline_2_rate']:.1%} "
            f"({g['a1_path_twos']}/{g['a1_path_scored']} also_baseline=true)"
        )
        lines.append(
            f"persona_path_2_rate: {g['persona_touched_2_rate']:.1%} "
            f"({g['persona_path_twos']}/{g['persona_path_scored']} also_baseline=false)"
        )
    else:
        lines.append(
            f"single_2_rate: {g['single_2_rate']:.1%} "
            f"({g['single_twos']}/{g['single_scored']} scored single-agent candidates)"
        )
        lines.append(
            f"multi_2_rate: {g['multi_2_rate']:.1%} "
            f"({g['multi_twos']}/{g['multi_scored']} scored multi-agent candidates)"
        )
        lines.append(
            f"single_structural_2_rate: {g['single_structural_2_rate']:.1%} "
            f"({g['single_structural_twos']}/{g['single_scored']} scored single-agent; "
            "type in 深层共振|强共振)"
        )
        lines.append(
            f"multi_structural_2_rate: {g['multi_structural_2_rate']:.1%} "
            f"({g['multi_structural_twos']}/{g['multi_scored']} scored multi-agent; "
            "type in 深层共振|强共振)"
        )

    if compare_mode == "d5_success_criteria":
        lines.append("Gate: D5 success criteria (resonance + workflow)")
    else:
        lines.append(
            f"Gate line 2 compare: {compare_mode}"
            + (
                " (共振类型 present)"
                if g.get("resonance_types_filled")
                else " (fallback: no 共振类型)"
            )
        )
    ranking = report.get("fit_sim_ranking") or []
    if ranking:
        top = ranking[0]
        lines.append(
            f"fit×sim ranking: {len(ranking)} candidates with fit+sim; "
            f"top={top['fit_sim_score']} ({top['run_id']} tmdb {top['tmdb_id']})"
        )
    if g["missing_scores_total"]:
        lines.append(f"Missing scores (excluded from rates): {g['missing_scores_total']}")

    lines.append("")
    gate = report["gate"]
    lines.append(gate["verdict"])
    if gate["reasons"]:
        for reason in gate["reasons"]:
            lines.append(f"  - {reason}")
    elif gate["pass"]:
        metric = gate.get("rate_metric", "total_2_rate")
        if gate.get("compare_mode") == "d5_success_criteria":
            lines.append(
                "  - D5 resonance: focal channel has signal; n1/pure_fact diagnostic-only; "
                "obs/holdout consistent; workflow: load reduction + safety + calibration"
            )
        elif g.get("persona_gate"):
            lines.append(
                f"  - batch pass rate >= {_GATE_BATCH_PASS_RATE:.0%}; "
                f"persona_path_{metric} > a1_path_{metric}"
            )
        else:
            lines.append(
                f"  - batch pass rate >= {_GATE_BATCH_PASS_RATE:.0%}; "
                f"single_{metric} < multi_{metric}"
            )

    return "\n".join(lines)


def _collect_paths(args: argparse.Namespace) -> list[Path]:
    paths: list[Path] = []
    if args.dir:
        dir_path = Path(args.dir)
        if not dir_path.is_absolute():
            dir_path = _REPO_ROOT / dir_path
        if not dir_path.is_dir():
            raise FileNotFoundError(f"directory not found: {dir_path}")
        paths.extend(sorted(dir_path.glob("*/candidates.md")))
        paths.extend(sorted(dir_path.glob("*.md")))
    paths.extend(Path(p) for p in args.files)

    resolved: list[Path] = []
    seen: set[Path] = set()
    for p in paths:
        path = p if p.is_absolute() else _REPO_ROOT / p
        path = path.resolve()
        if path.is_dir():
            candidate = path / "candidates.md"
            if candidate.is_file():
                path = candidate
            else:
                continue
        if path.suffix.lower() != ".md" or not path.is_file():
            continue
        if path.name in {
            "GATE_RESULT.md",
            "high-hit-score-review.md",
            "multi-agent-hits-review.md",
        }:
            continue
        if path not in seen:
            seen.add(path)
            resolved.append(path)

    if not resolved:
        raise FileNotFoundError(
            "no eval candidates markdown found (expected */candidates.md, "
            "--review high-hit-score-review.md, or fixture *.md)"
        )
    return resolved


def _load_runs(args: argparse.Namespace) -> list[RunSummary]:
    if args.review:
        review_path = Path(args.review)
        if not review_path.is_absolute():
            review_path = _REPO_ROOT / review_path
        if not review_path.is_file():
            raise FileNotFoundError(f"review file not found: {review_path}")
        return parse_unified_review(
            review_path, review_path.read_text(encoding="utf-8")
        )

    if args.dir:
        dir_path = Path(args.dir)
        if not dir_path.is_absolute():
            dir_path = _REPO_ROOT / dir_path
        review_path = dir_path / "high-hit-score-review.md"
        has_per_run = any(dir_path.glob("*/candidates.md"))
        if review_path.is_file() and not has_per_run:
            return parse_unified_review(
                review_path, review_path.read_text(encoding="utf-8")
            )

    paths = _collect_paths(args)
    runs: list[RunSummary] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        runs.append(parse_eval_markdown(path, text))
    return runs


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Summarize scored Eval Markdown files and check validation gate.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        help="candidates.md path(s), run dir(s), or legacy fixture .md",
    )
    parser.add_argument(
        "--dir",
        help="Scan for */candidates.md (e.g. output/Eval) or top-level fixture .md",
    )
    parser.add_argument(
        "--review",
        help="Unified high-hit-score-review.md (phase3.7 SSOT when per-run candidates absent)",
    )
    parser.add_argument(
        "--out",
        help="Optional JSON report path.",
    )
    parser.add_argument(
        "--calibration-json",
        help="Optional llm-judge-scores.json for D5 workflow calibration criterion.",
    )
    args = parser.parse_args(argv)

    try:
        runs = _load_runs(args)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not runs:
        print("error: no runs parsed", file=sys.stderr)
        return 2

    calibration: dict[str, Any] | None = None
    if args.calibration_json:
        cal_path = Path(args.calibration_json)
        if not cal_path.is_absolute():
            cal_path = _REPO_ROOT / cal_path
        if cal_path.is_file():
            calibration = json.loads(cal_path.read_text(encoding="utf-8"))
        else:
            print(f"warning: calibration JSON not found: {cal_path}", file=sys.stderr)

    report = summarize_runs(runs, calibration=calibration)
    output = _format_stdout(report)
    print(output)

    if args.out:
        out_path = Path(args.out)
        if not out_path.is_absolute():
            out_path = _REPO_ROOT / out_path
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Wrote {out_path.resolve()}", file=sys.stderr)

    return 0 if report["gate"]["pass"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
