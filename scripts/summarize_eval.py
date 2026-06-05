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

_REPO_ROOT = Path(__file__).resolve().parents[1]

_SCORE_LINE = re.compile(r"^-\s*\*\*共振分\*\*:\s*(.*)$", re.MULTILINE)
_RESONANCE_TYPE_LINE = re.compile(r"^-\s*\*\*共振类型\*\*:\s*(.*)$", re.MULTILINE)
_STRUCTURAL_TYPES = frozenset({"结构", "双重"})
_TMDB_LINE = re.compile(r"^-\s*\*\*tmdb_id\*\*:\s*(\S+)", re.MULTILINE)
_SIMILARITY_LINE = re.compile(r"^-\s*\*\*相似度\*\*:\s*([\d.]+)", re.MULTILINE)
_FIT_VALUE = re.compile(r"fit=([\d.]+)")
_ALSO_BASELINE_LINE = re.compile(
    r"^-\s*\*\*also_baseline\*\*:\s*(true|false)",
    re.MULTILINE | re.IGNORECASE,
)
_QUALITY_CANDIDATE_LINE = re.compile(
    r"^-\s*\*\*quality_candidate\*\*:\s*(true|false)",
    re.MULTILINE | re.IGNORECASE,
)
_QUALITY_ZH_LINE = re.compile(
    r"^-\s*\*\*优质候选\*\*:\s*(true|false)",
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
_PERSONA_BUCKETS = ("baseline-only", "persona-only", "both")


@dataclass
class CandidateScore:
    title: str
    tmdb_id: str
    triggered_by: list[str]
    also_baseline: bool
    score: int | None  # None = missing
    resonance_type: str | None = None  # 表层 / 结构 / 双重; None = unset
    quality_candidate: bool | None = None  # None = infer from heading agents
    similarity: float | None = None
    max_fit: float | None = None
    neutral_hit_rate: float | None = None
    neutral_hits: int | None = None
    neutral_total: int | None = None
    distinct_agents: int | None = None

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
        if self.distinct_agents is not None:
            return self.distinct_agents >= 1
        if self.quality_candidate:
            return True
        return False

    @property
    def neutral_vote(self) -> bool:
        if self.neutral_hits is not None:
            return self.neutral_hits >= 1
        if self.neutral_hit_rate is not None:
            return self.neutral_hit_rate > 0.0
        return False

    @property
    def is_neutral_only(self) -> bool:
        return self.neutral_vote and not self.toned_convergence


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
    cleaned = _strip_html_comments(raw_line).strip()
    if not cleaned:
        return None
    for token in ("双重", "结构", "表层"):
        if token in cleaned:
            return token
    return None


def _is_structural_resonance(cand: CandidateScore) -> bool:
    return cand.score == 2 and cand.resonance_type in _STRUCTURAL_TYPES


def _is_multi_agent_candidate(cand: CandidateScore) -> bool:
    if cand.quality_candidate is not None:
        return cand.quality_candidate
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


def _diagnostic_toned_convergence(runs: list[RunSummary]) -> dict[str, Any]:
    """Diagnostic ②: toned-convergence precision above neutral, controlling similarity."""
    quality_rows: list[CandidateScore] = []
    neutral_only_rows: list[CandidateScore] = []
    partial_rows: list[dict[str, float]] = []

    for run in runs:
        for cand in run.candidates:
            if cand.score is None or cand.max_similarity is None:
                continue
            if cand.quality_candidate:
                quality_rows.append(cand)
            elif cand.is_neutral_only:
                neutral_only_rows.append(cand)
            if cand.neutral_vote:
                partial_rows.append(
                    {
                        "toned": 1.0 if cand.toned_convergence else 0.0,
                        "score": float(cand.score),
                        "max_similarity": cand.max_similarity,
                    }
                )

    q_total, q_structural, q_counts = _structural_2_rates(quality_rows)
    n_total, n_structural, n_counts = _structural_2_rates(neutral_only_rows)

    by_bin: dict[str, dict[str, list[CandidateScore]]] = {}
    for cand in quality_rows + neutral_only_rows:
        if cand.max_similarity is None:
            continue
        label = _similarity_bin_label(cand.max_similarity)
        bucket = by_bin.setdefault(label, {"quality": [], "neutral_only": []})
        if cand.quality_candidate:
            bucket["quality"].append(cand)
        elif cand.is_neutral_only:
            bucket["neutral_only"].append(cand)

    bin_lifts: dict[str, dict[str, Any]] = {}
    for label, bucket in by_bin.items():
        _, q_bin_struct, q_bin_counts = _structural_2_rates(bucket["quality"])
        _, n_bin_struct, n_bin_counts = _structural_2_rates(bucket["neutral_only"])
        bin_lifts[label] = {
            "quality_structural_2_rate": q_bin_struct,
            "neutral_only_structural_2_rate": n_bin_struct,
            "quality_scored": q_bin_counts["scored"],
            "neutral_only_scored": n_bin_counts["scored"],
        }

    partial_corr = None
    if len(partial_rows) >= 2:
        partial_corr = _partial_correlation(
            [r["toned"] for r in partial_rows],
            [r["score"] for r in partial_rows],
            [r["max_similarity"] for r in partial_rows],
        )

    precision_lift_ok = False
    if q_counts["scored"] > 0 and n_counts["scored"] > 0:
        precision_lift_ok = q_structural > n_structural
    elif q_counts["scored"] > 0 and n_counts["scored"] == 0:
        precision_lift_ok = q_structural > 0.0

    return {
        "quality_total_2_rate": q_total,
        "quality_structural_2_rate": q_structural,
        "neutral_only_total_2_rate": n_total,
        "neutral_only_structural_2_rate": n_structural,
        "precision_lift_ok": precision_lift_ok,
        "partial_corr_toned_vs_score_given_similarity": partial_corr,
        "similarity_bins": bin_lifts,
        **{f"quality_{k}": v for k, v in q_counts.items()},
        **{f"neutral_only_{k}": v for k, v in n_counts.items()},
    }


def _a1_superset_placeholder() -> dict[str, Any]:
    """3.8.8 GATE slot — filled after 3.8.7 A1 parallel batch."""
    return {
        "status": "pending",
        "note": "Requires 3.8.7 A1 parallel run; verdict in 3.8.8 GATE_RESULT",
        "neutral_union_superset_of_a1_hits": None,
        "quality_structural_2_rate_vs_a1": None,
        "a1_deletion_eligible": None,
    }


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

        score: int | None = None
        score_match = _SCORE_LINE.search(body)
        if score_match:
            score = _parse_score(score_match.group(1))

        resonance_type: str | None = None
        type_match = _RESONANCE_TYPE_LINE.search(body)
        if type_match:
            resonance_type = _parse_resonance_type(type_match.group(1))

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
                quality_candidate=quality_candidate,
                similarity=similarity,
                max_fit=max_fit,
                neutral_hit_rate=neutral_hit_rate,
                neutral_hits=neutral_hits,
                neutral_total=neutral_total,
                distinct_agents=distinct_agents,
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
                }
            )
    ranked.sort(key=lambda row: row["fit_sim_score"], reverse=True)
    return ranked


def summarize_runs(runs: list[RunSummary]) -> dict[str, Any]:
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
        "quality_vs_neutral_only"
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
    a1_superset = _a1_superset_placeholder() if phase38_gate else None

    gate_reasons: list[str] = []
    batch_ok = batch_pass_rate >= _GATE_BATCH_PASS_RATE

    if phase38_gate and diagnostic_2 is not None:
        if use_structural_gate:
            rate_ok = bool(diagnostic_2["precision_lift_ok"])
            baseline_gate_rate = diagnostic_2["neutral_only_structural_2_rate"]
            persona_gate_rate = diagnostic_2["quality_structural_2_rate"]
            rate_metric = "quality_structural_2_rate"
        else:
            rate_ok = diagnostic_2["quality_total_2_rate"] > diagnostic_2[
                "neutral_only_total_2_rate"
            ]
            baseline_gate_rate = diagnostic_2["neutral_only_total_2_rate"]
            persona_gate_rate = diagnostic_2["quality_total_2_rate"]
            rate_metric = "quality_total_2_rate"
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

    if not batch_ok:
        gate_reasons.append(
            f"batch pass rate {batch_pass_rate:.1%} < {_GATE_BATCH_PASS_RATE:.0%} "
            f"({runs_with_2}/{total_runs} runs with >=1 score-2)"
        )
    if not rate_ok:
        if phase38_gate:
            gate_reasons.append(
                f"quality_{rate_metric} {persona_gate_rate:.1%} not > "
                f"neutral_only_{rate_metric} {baseline_gate_rate:.1%} "
                "(diagnostic ② · similarity-controlled)"
            )
        elif persona_gate:
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
    if a1_superset is not None:
        result["a1_superset"] = a1_superset
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
        lines.append(
            "Diagnostic ② (toned-convergence precision above neutral): "
            f"quality structural 2-rate {d2.get('quality_structural_2_rate', 0):.1%} "
            f"({d2.get('quality_structural_twos', 0)}/{d2.get('quality_scored', 0)}) vs "
            f"neutral-only {d2.get('neutral_only_structural_2_rate', 0):.1%} "
            f"({d2.get('neutral_only_structural_twos', 0)}/{d2.get('neutral_only_scored', 0)})"
        )
        pt = d2.get("partial_corr_toned_vs_score_given_similarity")
        if pt is not None:
            lines.append(f"  partial r(toned, score | similarity)={pt:.4f}")
        a1s = report.get("a1_superset") or {}
        lines.append(f"A1-superset check: {a1s.get('status', 'n/a')} — {a1s.get('note', '')}")
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
            "type in 结构|双重)"
        )
        lines.append(
            f"multi_structural_2_rate: {g['multi_structural_2_rate']:.1%} "
            f"({g['multi_structural_twos']}/{g['multi_scored']} scored multi-agent; "
            "type in 结构|双重)"
        )

    lines.append(
        f"Gate line 2 compare: {compare_mode}"
        + (" (共振类型 present)" if g.get("resonance_types_filled") else " (fallback: no 共振类型)")
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
        if g.get("phase38_gate"):
            lines.append(
                f"  - batch pass rate >= {_GATE_BATCH_PASS_RATE:.0%}; "
                f"quality_{metric} > neutral_only_{metric} (diagnostic ②)"
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
    args = parser.parse_args(argv)

    try:
        runs = _load_runs(args)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if not runs:
        print("error: no runs parsed", file=sys.stderr)
        return 2

    report = summarize_runs(runs)
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
