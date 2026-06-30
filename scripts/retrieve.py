"""retrieve.py · 跨类型纯文本召回.

输入: 优先读取 agents[].search_units；兼容旧 agents[].pseudos[] / agents[].text。
索引: data/index/embeddings.npy + data/index/meta.parquet.
模型: paraphrase-multilingual-MiniLM-L12-v2 (与 build_index 严格同模型).

输出: 每个 search unit Top-K（默认 2）→ 按 tmdb_id 聚合去重；
      候选漏斗（ADR-0009）: 去重 → match 诊断 → 新 convergent sort → 可选 judge 预筛 → 预算 top-N；
      预算以下 ``judge≥1`` 进 ``audit_pool``（抽审兜底，不靠调高 judge 门槛控量）。
      主排序信号来自 surface_match / event_match / persona_semantic_match / persona diversity /
      center dimension diversity / dense similarity（ADR-0009 search_unit_kind 口径）。
      A1 held-out oracle（ADR-0006）: A1/baseline 查询独立并跑 → ``a1_oracle``；
      不进 ``candidates`` / 撞车票 / 排序。

不做:
  - 相似度阈值过滤（quality_floor 仅用于 match 诊断/汇聚计数）
  - 评分 / 年代 / 成人内容过滤
  - 历史去重
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from scripts.lib.env import load_env
from scripts.lib.paths import embeddings_npy, meta_parquet
from scripts.movie_metadata import get_movie_detail_by_tmdb_id, get_movie_details_by_tmdb_ids

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
QUERY_TEMPLATE = "Overview: {pseudo}"
DEFAULT_TOP_K = 2
DEFAULT_MAX_CANDIDATES = 19
DEFAULT_HUMAN_BUDGET = 19
DEFAULT_QUALITY_FLOOR = 0.40
DEFAULT_MIN_JUDGE_SCORE = 1
DEFAULT_MOVIE_LINK_PREFIX = "https://themoviecosmos.com/movie/"

# Convergent-sort weights: match diagnostics + diversity + similarity.
_CONVERGENT_WEIGHT_SURFACE = 60
_CONVERGENT_WEIGHT_EVENT = 80
_CONVERGENT_WEIGHT_PERSONA_SEMANTIC = 100
_CONVERGENT_WEIGHT_PERSONA = 10
_CONVERGENT_WEIGHT_CENTER_DIMENSION = 8

_AGENT_ORDER: tuple[str, ...] = ("A2", "A4", "A7", "A1")

_ORACLE_AGENT_IDS: frozenset[str] = frozenset({"A1"})

_OBJECTIVE_UNIT_KINDS: frozenset[str] = frozenset(
    {"surface-fragment-bundle", "event-fragment-bundle"}
)
_SEARCH_UNIT_KINDS: frozenset[str] = frozenset(
    {"surface-fragment-bundle", "event-fragment-bundle", "persona-semantic"}
)

_ROLE_BY_AGENT: dict[str, str] = {
    "A1": "baseline",
    "A2": "toned",
    "A4": "toned",
    "A7": "toned",
}

_index_cache: tuple[np.ndarray, pd.DataFrame] | None = None
_model: SentenceTransformer | None = None


def _movie_link_prefix() -> str:
    load_env()
    prefix = os.getenv("MOVIE_LINK_PREFIX", DEFAULT_MOVIE_LINK_PREFIX).strip()
    return prefix or DEFAULT_MOVIE_LINK_PREFIX


def _movie_url(tmdb_id: int, prefix: str) -> str:
    return f"{prefix.rstrip('/')}/{tmdb_id}"


def _release_year(value: object) -> int | None:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    text = str(value).strip()
    if len(text) >= 4 and text[:4].isdigit():
        return int(text[:4])
    return None


def _str_field(value: object) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return ""
    return str(value).strip()


def _load_index() -> tuple[np.ndarray, pd.DataFrame]:
    global _index_cache
    if _index_cache is not None:
        return _index_cache

    emb_path = embeddings_npy()
    meta_path = meta_parquet()
    if not emb_path.is_file():
        raise FileNotFoundError(f"embeddings not found: {emb_path}")
    if not meta_path.is_file():
        raise FileNotFoundError(f"meta not found: {meta_path}")

    embeddings = np.load(emb_path)
    meta = pd.read_parquet(meta_path)
    if embeddings.shape[0] != len(meta):
        raise ValueError(
            f"row mismatch — embeddings={embeddings.shape[0]}, meta={len(meta)}"
        )

    _index_cache = (embeddings, meta)
    return _index_cache


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(MODEL_NAME)
    return _model


def _encode_query(pseudo: str, model: SentenceTransformer) -> np.ndarray:
    query_text = QUERY_TEMPLATE.format(pseudo=pseudo.strip())
    vector = model.encode(query_text, normalize_embeddings=True)
    return np.asarray(vector, dtype=np.float32)


def _top_k_indices(scores: np.ndarray, k: int) -> np.ndarray:
    n = scores.shape[0]
    k = min(k, n)
    if k <= 0:
        return np.array([], dtype=np.intp)
    if k >= n:
        idx = np.arange(n, dtype=np.intp)
        return idx[np.argsort(-scores[idx])]

    partition = np.argpartition(scores, -k)[-k:]
    return partition[np.argsort(-scores[partition])[::-1]]


def _per_agent_hit(
    row: pd.Series,
    similarity: float,
    link_prefix: str,
) -> dict[str, Any]:
    tmdb_id = int(row["id"])
    return {
        "tmdb_id": tmdb_id,
        "title": _str_field(row["title"]),
        "similarity": float(similarity),
        "movie_url": _movie_url(tmdb_id, link_prefix),
    }


def _candidate_fields(
    row: pd.Series,
    similarity: float,
    link_prefix: str,
) -> dict[str, Any]:
    tmdb_id = int(row["id"])
    return {
        "tmdb_id": tmdb_id,
        "title": _str_field(row["title"]),
        "overview": _str_field(row["overview"]),
        "genres": _str_field(row["genres"]),
        "release_year": _release_year(row["release_date"]),
        "language": _str_field(row["original_language"]),
        "poster_path": _str_field(row["poster_path"]),
        "movie_url": _movie_url(tmdb_id, link_prefix),
        "similarity": float(similarity),
    }


def retrieve_top_k(
    pseudo: str,
    *,
    top_k: int = DEFAULT_TOP_K,
    agent_id: str = "A2",
    role: str | None = None,
) -> dict[str, Any]:
    """Retrieve Top-K hits for a single pseudo-overview (debug / unit use)."""
    resolved_role = role or _ROLE_BY_AGENT.get(agent_id.upper(), "toned")
    return retrieve_from_agents(
        [
            {
                "agent_id": agent_id.upper(),
                "role": resolved_role,
                "text": pseudo,
            }
        ],
        [],
        top_k=top_k,
    )


def _error_agent_ids(errors: list[Any]) -> set[str]:
    ids: set[str] = set()
    for entry in errors:
        if isinstance(entry, dict) and entry.get("agent_id"):
            ids.add(str(entry["agent_id"]).upper())
    return ids


def _normalize_fragments(source: object) -> list[str]:
    if not isinstance(source, dict):
        return []
    fragments = source.get("fragments")
    if not isinstance(fragments, list):
        return []
    return [str(item).strip() for item in fragments if str(item).strip()]


def _resolve_unit_kind(
    agent: dict[str, Any],
    source: dict[str, Any],
    agent_id: str,
) -> str:
    """Map search-unit kind (ADR-0009). Kindless pseudos classify by agent role:

    A1/baseline → ``baseline`` (held-out oracle, excluded from candidates);
    A2/A4/A7 and other personas → ``persona-semantic``.
    """
    kind = str(source.get("kind") or source.get("search_unit_kind") or "").strip().lower()
    if kind in _SEARCH_UNIT_KINDS:
        return kind
    agent_role = str(agent.get("role") or _ROLE_BY_AGENT.get(agent_id, "toned")).strip().lower()
    if agent_role == "baseline" or agent_id in _ORACLE_AGENT_IDS:
        return "baseline"
    return "persona-semantic"


def _expand_retrieval_queries(
    agents: list[dict[str, Any]],
    errors: list[Any],
) -> list[dict[str, Any]]:
    """One retrieval query per pseudo segment (legacy: single agents[].text)."""
    failed = _error_agent_ids(errors)
    queries: list[dict[str, Any]] = []

    for agent in agents:
        agent_id = str(agent.get("agent_id", "")).upper()
        if not agent_id or agent_id in failed:
            continue
        agent_role = str(agent.get("role") or _ROLE_BY_AGENT.get(agent_id, "toned")).strip().lower()
        search_units = agent.get("search_units")
        if isinstance(search_units, dict):
            flat_units: list[dict[str, Any]] = []
            for key in (
                "surface_fragment_bundles",
                "event_fragment_bundles",
                "persona_semantic_units",
            ):
                rows = search_units.get(key)
                if isinstance(rows, list):
                    flat_units.extend(row for row in rows if isinstance(row, dict))
            if flat_units:
                for row in flat_units:
                    text = str(row.get("search_text") or row.get("text") or "").strip()
                    if not text:
                        continue
                    unit_id = str(row.get("id") or f"su{len(queries) + 1}").strip()
                    source_elements = row.get("source_elements")
                    if not isinstance(source_elements, list):
                        source_elements = []
                    source = {
                        "kind": str(row.get("kind") or "").strip().lower(),
                        "fragments": [str(item) for item in source_elements if str(item).strip()],
                    }
                    unit_kind = _resolve_unit_kind(agent, source, agent_id)
                    queries.append(
                        {
                            "agent_id": agent_id,
                            "role": agent_role,
                            "pseudo_id": unit_id,
                            "search_unit_id": unit_id,
                            "search_unit_kind": unit_kind,
                            "center_element": row.get("center_element"),
                            "text": text,
                            "source": {
                                "agent_id": agent_id,
                                "fragments": source["fragments"],
                                "search_unit_kind": unit_kind,
                                "center_element": row.get("center_element"),
                            },
                        }
                    )
                continue
        pseudos = agent.get("pseudos")
        if isinstance(pseudos, list) and pseudos:
            for row in pseudos:
                if not isinstance(row, dict):
                    continue
                text = str(row.get("text", "")).strip()
                if not text:
                    continue
                pseudo_id = str(row.get("id") or row.get("pseudo_id") or "").strip()
                if not pseudo_id:
                    pseudo_id = f"p{len(queries) + 1}"
                source = row.get("source") if isinstance(row.get("source"), dict) else {}
                unit_kind = _resolve_unit_kind(agent, source, agent_id)
                queries.append(
                    {
                        "agent_id": agent_id,
                        "role": agent_role,
                        "pseudo_id": pseudo_id,
                        "search_unit_kind": unit_kind,
                        "center_element": source.get("center_element"),
                        "text": text,
                        "source": {
                            "agent_id": agent_id,
                            "fragments": _normalize_fragments(source),
                            "search_unit_kind": unit_kind,
                            "center_element": source.get("center_element"),
                        },
                    }
                )
            continue

        text = str(agent.get("text", "")).strip()
        if not text:
            continue
        unit_kind = _resolve_unit_kind(agent, {}, agent_id)
        queries.append(
            {
                "agent_id": agent_id,
                "role": agent_role,
                "pseudo_id": "legacy",
                "search_unit_kind": unit_kind,
                "center_element": None,
                "text": text,
                "source": {
                    "agent_id": agent_id,
                    "fragments": [],
                    "search_unit_kind": unit_kind,
                    "center_element": None,
                },
            }
        )

    return queries


def _is_oracle_query(query: dict[str, Any]) -> bool:
    """True when query belongs to held-out A1/baseline oracle path (ADR-0006)."""
    agent_id = str(query.get("agent_id", "")).upper()
    if agent_id in _ORACLE_AGENT_IDS:
        return True
    kind = str(query.get("search_unit_kind") or "").strip().lower()
    return kind == "baseline"


def _split_oracle_judge_queries(
    queries: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    oracle: list[dict[str, Any]] = []
    judge: list[dict[str, Any]] = []
    for query in queries:
        if _is_oracle_query(query):
            oracle.append(query)
        else:
            judge.append(query)
    return oracle, judge


def _objective_union_tmdb_ids(
    candidates: list[dict[str, Any]],
    *,
    quality_floor: float,
) -> set[int]:
    """Distinct tmdb_ids with ≥1 objective-kind (surface/event) hit at or above floor."""
    ids: set[int] = set()
    for cand in candidates:
        if not _objective_hits_above_floor(cand, quality_floor=quality_floor):
            continue
        tmdb_id = cand.get("tmdb_id")
        if tmdb_id is not None:
            ids.add(int(tmdb_id))
    return ids


def _build_oracle_comparison(
    a1_hit_ids: set[int],
    candidates: list[dict[str, Any]],
    *,
    quality_floor: float,
) -> dict[str, Any]:
    objective_union = _objective_union_tmdb_ids(candidates, quality_floor=quality_floor)
    shared = sorted(a1_hit_ids & objective_union)
    a1_only = sorted(a1_hit_ids - objective_union)
    objective_only = sorted(objective_union - a1_hit_ids)
    if not a1_hit_ids:
        superset: bool | None = True if objective_union else None
    else:
        superset = a1_hit_ids <= objective_union
    return {
        "a1_hit_tmdb_ids": sorted(a1_hit_ids),
        "objective_union_tmdb_ids": sorted(objective_union),
        "shared_tmdb_ids": shared,
        "a1_only_tmdb_ids": a1_only,
        "objective_only_tmdb_ids": objective_only,
        "objective_union_superset_of_a1_hits": superset,
        "a1_hit_count": len(a1_hit_ids),
        "objective_union_hit_count": len(objective_union),
    }


def _build_a1_oracle_payload(
    per_pseudo: list[dict[str, Any]],
    *,
    raw_hit_count: int,
) -> dict[str, Any]:
    per_agent = _group_per_agent(per_pseudo)
    hit_tmdb_ids = sorted(
        {
            int(hit["tmdb_id"])
            for row in per_pseudo
            for hit in row.get("hits") or []
            if hit.get("tmdb_id") is not None
        }
    )
    return {
        "role": "held_out_oracle",
        "per_agent": per_agent,
        "hit_tmdb_ids": hit_tmdb_ids,
        "meta": {
            "query_count": len(per_pseudo),
            "raw_hit_count": raw_hit_count,
            "agent_ids": _sort_agent_ids(
                list({str(row["agent_id"]).upper() for row in per_pseudo})
            ),
        },
    }


def _count_persona_semantic_personas(queries: list[dict[str, Any]]) -> int:
    """Persona count emitting ≥1 persona-semantic search unit (diversity denominator)."""
    return len(
        {
            query["agent_id"]
            for query in queries
            if str(query.get("search_unit_kind") or "").strip().lower() == "persona-semantic"
        }
    )


def _append_hit_source(
    cand: dict[str, Any],
    query: dict[str, Any],
    similarity: float,
) -> None:
    search_unit_kind = str(
        query.get("search_unit_kind") or query["source"].get("search_unit_kind") or ""
    ).strip().lower()
    entry = {
        "agent_id": query["agent_id"],
        "pseudo_id": query["pseudo_id"],
        "search_unit_kind": search_unit_kind,
        "fragments": list(query["source"].get("fragments") or []),
        "similarity": float(similarity),
    }
    center_element = query.get("center_element") or query["source"].get("center_element")
    if center_element:
        entry["center_element"] = str(center_element)
    sources: list[dict[str, Any]] = cand.setdefault("hit_sources", [])
    for existing in sources:
        if (
            existing.get("agent_id") == entry["agent_id"]
            and existing.get("pseudo_id") == entry["pseudo_id"]
        ):
            existing["similarity"] = max(
                float(existing.get("similarity", 0.0)),
                entry["similarity"],
            )
            if entry["fragments"]:
                merged = list(existing.get("fragments") or [])
                for frag in entry["fragments"]:
                    if frag not in merged:
                        merged.append(frag)
                existing["fragments"] = merged
            return
    sources.append(entry)


def _hit_source_unit_kind(source: dict[str, Any]) -> str:
    """Resolve hit source search_unit_kind; kindless A1 maps to baseline, else persona-semantic."""
    kind = str(source.get("search_unit_kind") or "").strip().lower()
    if kind in _SEARCH_UNIT_KINDS:
        return kind
    agent_id = str(source.get("agent_id", "")).upper()
    if agent_id in _ORACLE_AGENT_IDS:
        return "baseline"
    return "persona-semantic"


def _hit_sources_above_floor(
    cand: dict[str, Any],
    *,
    quality_floor: float,
) -> list[dict[str, Any]]:
    return [
        source
        for source in cand.get("hit_sources") or []
        if float(source.get("similarity", 0.0)) >= quality_floor
    ]


def _objective_hits_above_floor(
    cand: dict[str, Any],
    *,
    quality_floor: float,
) -> set[tuple[str, str]]:
    """Distinct (agent_id, pseudo_id) surface/event-bundle hits at or above floor."""
    keys: set[tuple[str, str]] = set()
    for source in cand.get("hit_sources") or []:
        if _hit_source_unit_kind(source) not in _OBJECTIVE_UNIT_KINDS:
            continue
        if float(source.get("similarity", 0.0)) < quality_floor:
            continue
        agent_id = str(source.get("agent_id", "")).upper()
        pseudo_id = str(source.get("pseudo_id", "")).strip()
        if agent_id and pseudo_id:
            keys.add((agent_id, pseudo_id))
    return keys


def _distinct_personas_above_floor(
    cand: dict[str, Any],
    *,
    quality_floor: float,
) -> set[str]:
    """Distinct personas with a persona-semantic hit above floor."""
    personas: set[str] = set()
    for source in _hit_sources_above_floor(cand, quality_floor=quality_floor):
        if _hit_source_unit_kind(source) != "persona-semantic":
            continue
        agent_id = str(source.get("agent_id", "")).upper()
        if agent_id:
            personas.add(agent_id)
    return personas


def _search_unit_kinds_above_floor(
    cand: dict[str, Any],
    *,
    quality_floor: float,
) -> set[str]:
    kinds: set[str] = set()
    for source in _hit_sources_above_floor(cand, quality_floor=quality_floor):
        kind = _hit_source_unit_kind(source)
        if kind in _SEARCH_UNIT_KINDS:
            kinds.add(kind)
    return kinds


def _center_dimensions_above_floor(
    cand: dict[str, Any],
    *,
    quality_floor: float,
) -> set[str]:
    dims: set[str] = set()
    for source in _hit_sources_above_floor(cand, quality_floor=quality_floor):
        center = str(source.get("center_element") or "").strip()
        if "-" in center:
            dims.add(center.split("-", 1)[0])
    return dims


def _apply_match_diagnostics(
    cand: dict[str, Any],
    *,
    quality_floor: float,
) -> None:
    kinds = _search_unit_kinds_above_floor(cand, quality_floor=quality_floor)
    center_dims = _center_dimensions_above_floor(cand, quality_floor=quality_floor)
    cand["match_diagnostics"] = {
        "surface_match": "surface-fragment-bundle" in kinds,
        "event_match": "event-fragment-bundle" in kinds,
        "persona_semantic_match": "persona-semantic" in kinds,
        "search_unit_kinds": sorted(kinds),
        "center_dimensions": sorted(center_dims),
    }


def _apply_quality_fields(
    cand: dict[str, Any],
    *,
    quality_floor: float,
) -> None:
    objective_keys = _objective_hits_above_floor(cand, quality_floor=quality_floor)
    personas = _distinct_personas_above_floor(cand, quality_floor=quality_floor)
    kinds = _search_unit_kinds_above_floor(cand, quality_floor=quality_floor)
    objective_match = bool(_OBJECTIVE_UNIT_KINDS & kinds) or len(objective_keys) >= 1
    semantic_match = "persona-semantic" in kinds or len(personas) >= 1

    cand["objective_hits"] = len(objective_keys)
    cand["persona_count"] = len(personas)
    cand["quality_candidate"] = objective_match and semantic_match

    if cand["quality_candidate"]:
        agent_list = ",".join(_sort_agent_ids(list(personas)))
        cand["quality_reason"] = (
            "objective_match=1 + persona_semantic_match=1"
            + (f"; personas={len(personas)}: {agent_list}" if agent_list else "")
        )
    elif not objective_match and not semantic_match:
        cand["quality_reason"] = (
            "objective_match=0 + persona_semantic_match=0 "
            "(surface/event match + persona-semantic hit expected)"
        )
    elif not objective_match:
        cand["quality_reason"] = "objective_match=0 (surface/event match expected)"
    else:
        cand["quality_reason"] = "persona_semantic_match=0 (persona-semantic hit expected)"


def _apply_convergence_fields(
    cand: dict[str, Any],
    *,
    quality_floor: float,
) -> None:
    """Candidate funnel sort: surface/event/persona-semantic match + diversity."""
    personas = _distinct_personas_above_floor(cand, quality_floor=quality_floor)
    kinds = _search_unit_kinds_above_floor(cand, quality_floor=quality_floor)
    center_dims = _center_dimensions_above_floor(cand, quality_floor=quality_floor)
    persona_count = len(personas)
    surface_score = _CONVERGENT_WEIGHT_SURFACE if "surface-fragment-bundle" in kinds else 0
    event_score = _CONVERGENT_WEIGHT_EVENT if "event-fragment-bundle" in kinds else 0
    persona_semantic_score = (
        _CONVERGENT_WEIGHT_PERSONA_SEMANTIC if "persona-semantic" in kinds else 0
    )
    cand["convergence_persona_count"] = persona_count
    _apply_match_diagnostics(cand, quality_floor=quality_floor)
    cand["convergent_score"] = (
        surface_score
        + event_score
        + persona_semantic_score
        + persona_count * _CONVERGENT_WEIGHT_PERSONA
        + len(center_dims) * _CONVERGENT_WEIGHT_CENTER_DIMENSION
        + float(cand.get("similarity", 0.0))
    )


def _convergent_sort_key(cand: dict[str, Any]) -> tuple[Any, ...]:
    return (
        -int(cand.get("convergent_score", 0.0)),
        -float(cand.get("similarity", 0.0)),
        int(cand.get("tmdb_id", 0)),
    )


def _merge_hit_source_record(
    cand: dict[str, Any],
    source: dict[str, Any],
) -> None:
    query = {
        "agent_id": str(source.get("agent_id", "")).upper(),
        "pseudo_id": str(source.get("pseudo_id", "")).strip(),
        "search_unit_kind": _hit_source_unit_kind(source),
        "center_element": source.get("center_element"),
        "source": {
            "fragments": list(source.get("fragments") or []),
            "search_unit_kind": _hit_source_unit_kind(source),
            "center_element": source.get("center_element"),
        },
    }
    _append_hit_source(cand, query, float(source.get("similarity", 0.0)))


def dedupe_candidates_by_tmdb_id(
    candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Layer 1 funnel: merge rows sharing tmdb_id (hit_sources union, max similarity)."""
    merged: dict[int, dict[str, Any]] = {}
    for cand in candidates:
        tmdb_id = int(cand["tmdb_id"])
        if tmdb_id not in merged:
            merged[tmdb_id] = dict(cand)
            merged[tmdb_id]["hit_sources"] = list(cand.get("hit_sources") or [])
            merged[tmdb_id]["triggered_by"] = list(cand.get("triggered_by") or [])
            continue
        existing = merged[tmdb_id]
        existing["similarity"] = max(
            float(existing.get("similarity", 0.0)),
            float(cand.get("similarity", 0.0)),
        )
        for source in cand.get("hit_sources") or []:
            _merge_hit_source_record(existing, source)
        for agent_id in cand.get("triggered_by") or []:
            if agent_id not in existing["triggered_by"]:
                existing["triggered_by"].append(agent_id)
    return list(merged.values())


def sort_candidates_convergent(
    candidates: list[dict[str, Any]],
    *,
    quality_floor: float,
) -> list[dict[str, Any]]:
    """Layer 2 funnel: convergent sort (multi-kind / multi-persona rank higher)."""
    enriched: list[dict[str, Any]] = []
    for cand in candidates:
        row = dict(cand)
        _apply_quality_fields(row, quality_floor=quality_floor)
        _apply_convergence_fields(row, quality_floor=quality_floor)
        enriched.append(row)
    return sorted(enriched, key=_convergent_sort_key)


def apply_candidate_funnel(
    candidates: list[dict[str, Any]],
    *,
    human_budget: int = DEFAULT_HUMAN_BUDGET,
    quality_floor: float = DEFAULT_QUALITY_FLOOR,
    judge_scores: dict[int, int] | None = None,
    min_judge_score: int = DEFAULT_MIN_JUDGE_SCORE,
) -> dict[str, Any]:
    """ADR-0007 D8 layers 2–4: convergent sort → judge prescreen → budget + audit pool."""
    if human_budget < 1:
        raise ValueError("human_budget must be >= 1")

    deduped = dedupe_candidates_by_tmdb_id(candidates)
    sorted_pool = sort_candidates_convergent(
        deduped,
        quality_floor=quality_floor,
    )

    for cand in sorted_pool:
        if judge_scores is not None:
            cand["judge_score"] = judge_scores.get(int(cand["tmdb_id"]))

    reviewable: list[dict[str, Any]] = []
    judge_zero: list[dict[str, Any]] = []
    for cand in sorted_pool:
        if judge_scores is None:
            reviewable.append(cand)
            continue
        score = judge_scores.get(int(cand["tmdb_id"]))
        if score is None:
            reviewable.append(cand)
        elif score >= min_judge_score:
            reviewable.append(cand)
        else:
            judge_zero.append(cand)

    human_candidates = reviewable[:human_budget]
    audit_pool: list[dict[str, Any]] = []
    if judge_scores is not None:
        for cand in reviewable[human_budget:]:
            score = judge_scores.get(int(cand["tmdb_id"]))
            if score is not None and score >= min_judge_score:
                audit_pool.append(cand)

    return {
        "sorted_candidates": sorted_pool,
        "human_candidates": human_candidates,
        "audit_pool": audit_pool,
        "judge_zero": judge_zero,
        "meta": {
            "human_budget": human_budget,
            "quality_floor": quality_floor,
            "min_judge_score": min_judge_score,
            "judge_prescreen_applied": judge_scores is not None,
            "deduped_count": len(deduped),
            "sorted_count": len(sorted_pool),
            "human_count": len(human_candidates),
            "audit_pool_count": len(audit_pool),
            "judge_zero_count": len(judge_zero),
        },
    }


@dataclass
class PoolDiffBySearchUnitKind:
    """A/B pool diff (design-on ∖ baseline) with search-unit-kind decomposition."""

    run_id: str
    baseline_candidate_count: int
    design_candidate_count: int
    net_new_tmdb_ids: list[int]
    lost_tmdb_ids: list[int]
    overlap_count: int
    by_search_unit_kind: dict[str, list[int]] = field(default_factory=dict)
    collision_gain_tmdb_ids: list[int] = field(default_factory=list)
    net_new_details: list[dict[str, Any]] = field(default_factory=list)


def _search_unit_kinds_for_candidate(cand: dict[str, Any]) -> set[str]:
    kinds: set[str] = set()
    for source in cand.get("hit_sources") or []:
        kind = _hit_source_unit_kind(source)
        if kind in _SEARCH_UNIT_KINDS:
            kinds.add(kind)
    return kinds


def compare_pool_diff_by_search_unit_kind(
    *,
    run_id: str,
    baseline_retrieve: dict[str, Any],
    design_retrieve: dict[str, Any],
) -> PoolDiffBySearchUnitKind:
    """Net-new candidates decomposed by surface/event/persona-semantic search unit kind."""
    def _ids(payload: dict[str, Any]) -> set[int]:
        ids: set[int] = set()
        for row in payload.get("candidates") or []:
            if isinstance(row, dict) and row.get("tmdb_id") is not None:
                ids.add(int(row["tmdb_id"]))
        return ids

    base_ids = _ids(baseline_retrieve)
    design_ids = _ids(design_retrieve)
    net_new = sorted(design_ids - base_ids)
    lost = sorted(base_ids - design_ids)
    by_kind: dict[str, list[int]] = {kind: [] for kind in sorted(_SEARCH_UNIT_KINDS)}
    collision_gain: list[int] = []
    net_new_details: list[dict[str, Any]] = []

    design_index = {
        int(row["tmdb_id"]): row
        for row in design_retrieve.get("candidates") or []
        if isinstance(row, dict) and row.get("tmdb_id") is not None
    }

    for tmdb_id in net_new:
        cand = design_index.get(tmdb_id, {})
        kinds = sorted(_search_unit_kinds_for_candidate(cand))
        for kind in kinds:
            by_kind[kind].append(tmdb_id)
        if len(kinds) >= 2:
            collision_gain.append(tmdb_id)
        net_new_details.append(
            {
                "tmdb_id": tmdb_id,
                "title": cand.get("title"),
                "similarity": cand.get("similarity"),
                "quality_candidate": cand.get("quality_candidate"),
                "search_unit_kinds": kinds,
                "collision_gain": len(kinds) >= 2,
                "triggered_by": cand.get("triggered_by"),
                "match_diagnostics": cand.get("match_diagnostics"),
            }
        )

    return PoolDiffBySearchUnitKind(
        run_id=run_id,
        baseline_candidate_count=len(base_ids),
        design_candidate_count=len(design_ids),
        net_new_tmdb_ids=net_new,
        lost_tmdb_ids=lost,
        overlap_count=len(base_ids & design_ids),
        by_search_unit_kind=by_kind,
        collision_gain_tmdb_ids=collision_gain,
        net_new_details=net_new_details,
    )


def pool_diff_by_search_unit_kind_to_dict(result: PoolDiffBySearchUnitKind) -> dict[str, Any]:
    return {
        "run_id": result.run_id,
        "baseline_candidate_count": result.baseline_candidate_count,
        "design_candidate_count": result.design_candidate_count,
        "overlap_count": result.overlap_count,
        "net_new_tmdb_ids": result.net_new_tmdb_ids,
        "lost_tmdb_ids": result.lost_tmdb_ids,
        "by_search_unit_kind": result.by_search_unit_kind,
        "collision_gain_tmdb_ids": result.collision_gain_tmdb_ids,
        "net_new_details": result.net_new_details,
    }


def _apply_containment(
    candidates: list[dict[str, Any]],
    *,
    max_candidates: int,
) -> list[dict[str, Any]]:
    if max_candidates <= 0 or len(candidates) <= max_candidates:
        return candidates
    return sorted(
        candidates,
        key=lambda item: (-float(item.get("similarity", 0.0)), int(item.get("tmdb_id", 0))),
    )[:max_candidates]


def _group_per_agent(per_pseudo: list[dict[str, Any]]) -> list[dict[str, Any]]:
    buckets: dict[str, dict[str, Any]] = {}
    for row in per_pseudo:
        agent_id = row["agent_id"]
        if agent_id not in buckets:
            buckets[agent_id] = {
                "agent_id": agent_id,
                "role": row["role"],
                "pseudos": [],
            }
        buckets[agent_id]["pseudos"].append(
            {
                "pseudo_id": row["pseudo_id"],
                "pseudo": row["text"],
                "source": row["source"],
                "hits": row["hits"],
            }
        )

    return [buckets[aid] for aid in _sort_agent_ids(list(buckets.keys()))]


def _pair_key(a: str, b: str) -> str:
    left, right = sorted((a, b))
    return f"{left}-{right}"


def _jaccard(a: set[int], b: set[int]) -> float:
    if not a and not b:
        return 1.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


def _sort_agent_ids(agent_ids: list[str]) -> list[str]:
    order = {aid: idx for idx, aid in enumerate(_AGENT_ORDER)}
    return sorted(agent_ids, key=lambda aid: order.get(aid, 99))


def _compute_divergence_from_agents(
    per_agent: list[dict[str, Any]],
    query_vectors: dict[str, np.ndarray],
    agent_topk_sets: dict[str, set[int]],
) -> dict[str, dict[str, float]]:
    """Divergence probe uses first pseudo query vector per agent (see ADR-0001)."""
    agent_ids = [entry["agent_id"] for entry in per_agent]

    query_cosines: dict[str, float] = {}
    topk_jaccard: dict[str, float] = {}

    for i, left_id in enumerate(agent_ids):
        for right_id in agent_ids[i + 1 :]:
            key = _pair_key(left_id, right_id)
            query_cosines[key] = float(
                np.dot(query_vectors[left_id], query_vectors[right_id])
            )
            set_left = agent_topk_sets.get(left_id, set())
            set_right = agent_topk_sets.get(right_id, set())
            topk_jaccard[key] = _jaccard(set_left, set_right)

    return {"query_cosines": query_cosines, "topk_jaccard": topk_jaccard}


def _run_query_batch(
    queries: list[dict[str, Any]],
    *,
    top_k: int,
    quality_floor: float,
    aggregate_candidates: bool,
) -> tuple[
    list[dict[str, Any]],
    dict[int, dict[str, Any]],
    dict[str, np.ndarray],
    dict[str, set[int]],
    int,
]:
    """Encode queries and optionally aggregate judge-path candidates."""
    if not queries:
        return [], {}, {}, {}, 0

    embeddings, meta = _load_index()
    model = _get_model()
    link_prefix = _movie_link_prefix()

    per_pseudo: list[dict[str, Any]] = []
    query_vectors: dict[str, np.ndarray] = {}
    agent_topk_sets: dict[str, set[int]] = {}
    candidate_map: dict[int, dict[str, Any]] = {}
    raw_hit_count = 0

    for query in queries:
        agent_id = query["agent_id"]
        pseudo = query["text"]

        query_vec = _encode_query(pseudo, model)
        if agent_id not in query_vectors:
            query_vectors[agent_id] = query_vec
        scores = query_vec @ embeddings.T
        indices = _top_k_indices(scores, top_k)

        hits: list[dict[str, Any]] = []
        topk_ids: set[int] = agent_topk_sets.setdefault(agent_id, set())
        for idx in indices:
            row = meta.iloc[int(idx)]
            similarity = float(scores[int(idx)])
            hit = _per_agent_hit(row, similarity, link_prefix)
            hits.append(hit)
            raw_hit_count += 1

            tmdb_id = int(hit["tmdb_id"])
            topk_ids.add(tmdb_id)
            if not aggregate_candidates:
                continue

            if tmdb_id not in candidate_map:
                fields = _candidate_fields(row, similarity, link_prefix)
                fields["triggered_by"] = []
                fields["also_baseline"] = False
                fields["hit_sources"] = []
                candidate_map[tmdb_id] = fields
            else:
                cand = candidate_map[tmdb_id]
                cand["similarity"] = max(cand["similarity"], similarity)

            cand = candidate_map[tmdb_id]
            _append_hit_source(cand, query, similarity)
            search_unit_kind = str(query.get("search_unit_kind") or "").strip().lower()
            if search_unit_kind == "persona-semantic" and agent_id not in cand["triggered_by"]:
                cand["triggered_by"].append(agent_id)

        per_pseudo.append({**query, "hits": hits})

    if aggregate_candidates:
        for cand in candidate_map.values():
            cand["triggered_by"] = _sort_agent_ids(cand["triggered_by"])
            cand["hit_sources"] = sorted(
                cand.get("hit_sources") or [],
                key=lambda item: (
                    _AGENT_ORDER.index(item["agent_id"])
                    if item.get("agent_id") in _AGENT_ORDER
                    else 99,
                    str(item.get("pseudo_id", "")),
                ),
            )
            _apply_quality_fields(
                cand,
                quality_floor=quality_floor,
            )

    return (
        per_pseudo,
        candidate_map,
        query_vectors,
        agent_topk_sets,
        raw_hit_count,
    )


def retrieve_from_agents(
    agents: list[dict[str, Any]],
    errors: list[Any],
    *,
    top_k: int = DEFAULT_TOP_K,
    max_candidates: int = DEFAULT_MAX_CANDIDATES,
    human_budget: int | None = None,
    quality_floor: float = DEFAULT_QUALITY_FLOOR,
    judge_scores: dict[int, int] | None = None,
    min_judge_score: int = DEFAULT_MIN_JUDGE_SCORE,
) -> dict[str, Any]:
    """Run retrieval for agent pseudos; returns per_agent, candidates, divergence."""
    budget = human_budget if human_budget is not None else max_candidates
    queries = _expand_retrieval_queries(agents, errors)
    oracle_queries, judge_queries = _split_oracle_judge_queries(queries)

    empty_meta = {
        "query_count": 0,
        "raw_hit_count": 0,
        "candidate_count": 0,
        "max_candidates": max_candidates,
        "quality_floor": quality_floor,
        "oracle_query_count": 0,
        "judge_query_count": 0,
    }
    if not queries:
        empty_funnel = {
            "human_budget": budget,
            "quality_floor": quality_floor,
            "min_judge_score": min_judge_score,
            "judge_prescreen_applied": judge_scores is not None,
            "deduped_count": 0,
            "sorted_count": 0,
            "human_count": 0,
            "audit_pool_count": 0,
            "judge_zero_count": 0,
        }
        return {
            "per_agent": [],
            "candidates": [],
            "human_candidates": [],
            "audit_pool": [],
            "funnel": empty_funnel,
            "a1_oracle": None,
            "oracle_comparison": None,
            "divergence": {"query_cosines": {}, "topk_jaccard": {}},
            "meta": {**empty_meta, "human_budget": budget, **empty_funnel},
        }

    (
        judge_per_pseudo,
        candidate_map,
        query_vectors,
        agent_topk_sets,
        judge_raw_hits,
    ) = _run_query_batch(
        judge_queries,
        top_k=top_k,
        quality_floor=quality_floor,
        aggregate_candidates=True,
    )

    oracle_per_pseudo: list[dict[str, Any]] = []
    oracle_raw_hits = 0
    if oracle_queries:
        oracle_per_pseudo, _, _, _, oracle_raw_hits = _run_query_batch(
            oracle_queries,
            top_k=top_k,
            quality_floor=quality_floor,
            aggregate_candidates=False,
        )

    funnel = apply_candidate_funnel(
        list(candidate_map.values()),
        human_budget=budget,
        quality_floor=quality_floor,
        judge_scores=judge_scores,
        min_judge_score=min_judge_score,
    )
    candidates = funnel["human_candidates"]

    per_agent = _group_per_agent(judge_per_pseudo)
    divergence = _compute_divergence_from_agents(per_agent, query_vectors, agent_topk_sets)

    a1_oracle = (
        _build_a1_oracle_payload(oracle_per_pseudo, raw_hit_count=oracle_raw_hits)
        if oracle_per_pseudo
        else None
    )
    a1_hit_ids = set(a1_oracle["hit_tmdb_ids"]) if a1_oracle else set()
    oracle_comparison = (
        _build_oracle_comparison(a1_hit_ids, candidates, quality_floor=quality_floor)
        if a1_oracle is not None
        else None
    )

    return {
        "per_agent": per_agent,
        "candidates": candidates,
        "human_candidates": funnel["human_candidates"],
        "audit_pool": funnel["audit_pool"],
        "funnel": funnel["meta"],
        "a1_oracle": a1_oracle,
        "oracle_comparison": oracle_comparison,
        "divergence": divergence,
        "meta": {
            "query_count": len(queries),
            "raw_hit_count": judge_raw_hits + oracle_raw_hits,
            "candidate_count": len(candidates),
            "max_candidates": max_candidates,
            "human_budget": budget,
            "quality_floor": quality_floor,
            "oracle_query_count": len(oracle_queries),
            "judge_query_count": len(judge_queries),
            **funnel["meta"],
        },
    }


def _load_agents_payload(payload: dict[str, Any] | str | Path) -> dict[str, Any]:
    if isinstance(payload, dict):
        return payload
    path = Path(payload)
    if not path.is_file():
        raise FileNotFoundError(f"agents JSON not found: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("agents JSON must be a top-level object")
    return data


def from_agents_json(
    payload: dict[str, Any] | str | Path,
    *,
    top_k: int = DEFAULT_TOP_K,
    max_candidates: int = DEFAULT_MAX_CANDIDATES,
    human_budget: int | None = None,
    quality_floor: float = DEFAULT_QUALITY_FLOOR,
    judge_scores: dict[int, int] | None = None,
    min_judge_score: int = DEFAULT_MIN_JUDGE_SCORE,
) -> dict[str, Any]:
    """Public API: agents JSON (path or dict) → retrieve result."""
    data = _load_agents_payload(payload)
    agents = data.get("agents", [])
    if not isinstance(agents, list):
        raise ValueError("agents JSON requires an 'agents' array")
    errors = data.get("errors", [])
    if errors is None:
        errors = []
    if not isinstance(errors, list):
        raise ValueError("agents JSON 'errors' must be an array when present")
    return retrieve_from_agents(
        agents,
        errors,
        top_k=top_k,
        max_candidates=max_candidates,
        human_budget=human_budget,
        quality_floor=quality_floor,
        judge_scores=judge_scores,
        min_judge_score=min_judge_score,
    )


def _write_json(payload: dict[str, Any], out: Path | None) -> None:
    serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if out is not None:
        if not out.is_absolute():
            out = _REPO_ROOT / out
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(serialized, encoding="utf-8")
        print(f"Wrote {out.resolve()}", file=sys.stderr)
    else:
        sys.stdout.buffer.write(serialized.encode("utf-8"))


def _run_cli(args: argparse.Namespace) -> int:
    top_k = args.top_k

    if args.pseudo is not None:
        if not args.agent_id:
            print("error: --agent-id is required with --pseudo", file=sys.stderr)
            return 2
        if not args.pseudo.strip():
            print("error: --pseudo must be non-empty", file=sys.stderr)
            return 2
        payload = retrieve_top_k(
            args.pseudo,
            top_k=top_k,
            agent_id=args.agent_id,
        )
        _write_json(payload, Path(args.out) if args.out else None)
        return 0

    if not args.agents_json:
        print("error: provide --agents-json or --pseudo with --agent-id", file=sys.stderr)
        return 2

    agents_path = Path(args.agents_json)
    if not agents_path.is_file():
        print(f"error: agents JSON not found: {agents_path}", file=sys.stderr)
        return 2

    try:
        payload = from_agents_json(
            agents_path,
            top_k=top_k,
            max_candidates=args.max_candidates,
            quality_floor=args.quality_floor,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    _write_json(payload, Path(args.out) if args.out else None)

    if not payload["per_agent"]:
        print("warning: no eligible agents to retrieve", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Retrieve Top-K movie candidates from pseudo-overviews "
            "(Overview query template, cosine on index embeddings)."
        ),
    )
    parser.add_argument(
        "--agents-json",
        help=(
            "Agents JSON (reads agents[].pseudos[]; legacy agents[].text; "
            "skips errors[] and empty segments)."
        ),
    )
    parser.add_argument(
        "--max-candidates",
        type=int,
        default=DEFAULT_MAX_CANDIDATES,
        help=(
            f"After tmdb_id dedupe, cap aggregated candidates "
            f"(default: {DEFAULT_MAX_CANDIDATES}, plan ~15–19/news)."
        ),
    )
    parser.add_argument(
        "--quality-floor",
        type=float,
        default=DEFAULT_QUALITY_FLOOR,
        dest="quality_floor",
        help=(
            f"Similarity floor for neutral/toned collision counting "
            f"(default: {DEFAULT_QUALITY_FLOOR}; top_k={DEFAULT_TOP_K})."
        ),
    )
    parser.add_argument(
        "--pseudo",
        help="Single pseudo-overview text (debug; requires --agent-id).",
    )
    parser.add_argument(
        "--agent-id",
        help="Agent id for --pseudo mode, e.g. A2.",
    )
    parser.add_argument(
        "--out",
        help="Write JSON result to this path; otherwise print UTF-8 JSON to stdout.",
    )
    parser.add_argument(
        "--top-k",
        type=int,
        default=DEFAULT_TOP_K,
        help=f"Top-K hits per agent (default: {DEFAULT_TOP_K}).",
    )
    args = parser.parse_args(argv)

    if args.top_k < 1:
        print("error: --top-k must be >= 1", file=sys.stderr)
        return 2
    if args.max_candidates < 1:
        print("error: --max-candidates must be >= 1", file=sys.stderr)
        return 2
    if args.quality_floor < 0.0 or args.quality_floor > 1.0:
        print("error: --quality-floor must be in [0.0, 1.0]", file=sys.stderr)
        return 2

    try:
        return _run_cli(args)
    except FileNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
