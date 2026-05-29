"""retrieve.py · 跨类型纯文本召回.

输入: 各 Agent 的 pseudo-overview 文本.
索引: data/index/embeddings.npy + data/index/meta.parquet.
模型: paraphrase-multilingual-MiniLM-L12-v2 (与 build_index 严格同模型).

输出: 每个 Agent 一组 Top-K (MVP K=2), 同时给一个聚合视图 (跨 Agent 撞车标识为强信号).

不做:
  - 相似度阈值过滤
  - 评分 / 年代 / 成人内容过滤
  - 历史去重
"""

from __future__ import annotations

import argparse
import json
import os
import sys
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

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
QUERY_TEMPLATE = "Overview: {pseudo}"
DEFAULT_TOP_K = 2
DEFAULT_MOVIE_LINK_PREFIX = "https://themoviecosmos.com/movie/"

_AGENT_ORDER: tuple[str, ...] = ("A2", "A4", "A7", "A1")

_ROLE_BY_AGENT: dict[str, str] = {
    "A1": "baseline",
    "A2": "creative",
    "A4": "creative",
    "A7": "creative",
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
    resolved_role = role or _ROLE_BY_AGENT.get(agent_id.upper(), "creative")
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


def _eligible_agents(
    agents: list[dict[str, Any]],
    errors: list[Any],
) -> list[dict[str, Any]]:
    failed = _error_agent_ids(errors)
    eligible: list[dict[str, Any]] = []
    for agent in agents:
        agent_id = str(agent.get("agent_id", "")).upper()
        if not agent_id or agent_id in failed:
            continue
        if not str(agent.get("text", "")).strip():
            continue
        eligible.append(agent)
    return eligible


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


def _compute_divergence(
    per_agent: list[dict[str, Any]],
    query_vectors: dict[str, np.ndarray],
) -> dict[str, dict[str, float]]:
    agent_ids = [entry["agent_id"] for entry in per_agent]
    hits_by_agent = {entry["agent_id"]: entry["hits"] for entry in per_agent}

    query_cosines: dict[str, float] = {}
    topk_jaccard: dict[str, float] = {}

    for i, left_id in enumerate(agent_ids):
        for right_id in agent_ids[i + 1 :]:
            key = _pair_key(left_id, right_id)
            query_cosines[key] = float(
                np.dot(query_vectors[left_id], query_vectors[right_id])
            )
            set_left = {int(h["tmdb_id"]) for h in hits_by_agent[left_id]}
            set_right = {int(h["tmdb_id"]) for h in hits_by_agent[right_id]}
            topk_jaccard[key] = _jaccard(set_left, set_right)

    return {"query_cosines": query_cosines, "topk_jaccard": topk_jaccard}


def retrieve_from_agents(
    agents: list[dict[str, Any]],
    errors: list[Any],
    *,
    top_k: int = DEFAULT_TOP_K,
) -> dict[str, Any]:
    """Run retrieval for Phase 1 agent rows; returns per_agent, candidates, divergence."""
    eligible = _eligible_agents(agents, errors)
    if not eligible:
        return {
            "per_agent": [],
            "candidates": [],
            "divergence": {"query_cosines": {}, "topk_jaccard": {}},
        }

    embeddings, meta = _load_index()
    model = _get_model()
    link_prefix = _movie_link_prefix()

    per_agent: list[dict[str, Any]] = []
    query_vectors: dict[str, np.ndarray] = {}
    candidate_map: dict[int, dict[str, Any]] = {}

    for agent in eligible:
        agent_id = str(agent["agent_id"]).upper()
        role = str(agent.get("role") or _ROLE_BY_AGENT.get(agent_id, "creative"))
        pseudo = str(agent["text"]).strip()

        query_vec = _encode_query(pseudo, model)
        query_vectors[agent_id] = query_vec
        scores = query_vec @ embeddings.T
        indices = _top_k_indices(scores, top_k)

        hits: list[dict[str, Any]] = []
        for idx in indices:
            row = meta.iloc[int(idx)]
            similarity = float(scores[int(idx)])
            hit = _per_agent_hit(row, similarity, link_prefix)
            hits.append(hit)

            tmdb_id = int(hit["tmdb_id"])
            if tmdb_id not in candidate_map:
                fields = _candidate_fields(row, similarity, link_prefix)
                fields["triggered_by"] = []
                fields["also_baseline"] = False
                candidate_map[tmdb_id] = fields
            else:
                cand = candidate_map[tmdb_id]
                cand["similarity"] = max(cand["similarity"], similarity)

            cand = candidate_map[tmdb_id]
            if role == "creative" and agent_id not in cand["triggered_by"]:
                cand["triggered_by"].append(agent_id)
            if role == "baseline":
                cand["also_baseline"] = True

        per_agent.append(
            {
                "agent_id": agent_id,
                "role": role,
                "pseudo": pseudo,
                "hits": hits,
            }
        )

    for cand in candidate_map.values():
        cand["triggered_by"] = _sort_agent_ids(cand["triggered_by"])

    candidates = sorted(
        candidate_map.values(),
        key=lambda item: (-item["similarity"], item["tmdb_id"]),
    )

    divergence = _compute_divergence(per_agent, query_vectors)

    return {
        "per_agent": per_agent,
        "candidates": candidates,
        "divergence": divergence,
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
) -> dict[str, Any]:
    """Public API: Phase 1 JSON (path or dict) → retrieve result."""
    data = _load_agents_payload(payload)
    agents = data.get("agents", [])
    if not isinstance(agents, list):
        raise ValueError("agents JSON requires an 'agents' array")
    errors = data.get("errors", [])
    if errors is None:
        errors = []
    if not isinstance(errors, list):
        raise ValueError("agents JSON 'errors' must be an array when present")
    return retrieve_from_agents(agents, errors, top_k=top_k)


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
        payload = from_agents_json(agents_path, top_k=top_k)
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
        help="Phase 1 agents JSON (reads agents[].text; skips errors[] and empty text).",
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
