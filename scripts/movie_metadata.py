"""Full-column movie metadata lookup by TMDB id (ADR-0012 path B).

This module is deliberately separate from the retrieval hot path.  Retrieval keeps
using ``meta.parquet`` (path A) with a small column whitelist; compose/review/publish
can call this path B by ``tmdb_id`` when they need richer movie facts from the
source ``cleaned.csv``.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Iterable
from urllib.error import URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from scripts.lib.paths import repo_root

DEFAULT_MOVIE_DETAILS_CSV = repo_root() / "data" / "output" / "cleaned.csv"
TMDB_API_BASE_URL = "https://api.themoviedb.org/3"

_DETAIL_CACHE: dict[Path, pd.DataFrame] = {}


def _resolve_csv_path(csv_path: Path | str | None = None) -> Path:
    path = Path(csv_path) if csv_path is not None else DEFAULT_MOVIE_DETAILS_CSV
    if not path.is_absolute():
        path = repo_root() / path
    return path


def _id_column(df: pd.DataFrame) -> str:
    if "tmdb_id" in df.columns:
        return "tmdb_id"
    if "id" in df.columns:
        return "id"
    raise ValueError("movie details CSV requires either 'tmdb_id' or 'id' column")


def _load_movie_details(csv_path: Path | str | None = None) -> pd.DataFrame:
    """Load and cache full-column movie details from ``cleaned.csv``.

    The returned frame keeps every source column intact and is indexed by the
    canonical TMDB id column for point lookup.
    """
    path = _resolve_csv_path(csv_path)
    cached = _DETAIL_CACHE.get(path)
    if cached is not None:
        return cached
    if not path.is_file():
        raise FileNotFoundError(f"movie details CSV not found: {path}")

    df = pd.read_csv(path)
    id_col = _id_column(df)
    indexed = df.copy()
    indexed.index = indexed[id_col].astype(str)
    _DETAIL_CACHE[path] = indexed
    return indexed


def _json_safe(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        try:
            return value.item()
        except ValueError:
            return value
    return value


def get_movie_detail_by_tmdb_id(
    tmdb_id: int | str,
    *,
    csv_path: Path | str | None = None,
) -> dict[str, Any] | None:
    """Return the full source row for one TMDB id, or ``None`` when absent."""
    df = _load_movie_details(csv_path)
    key = str(tmdb_id)
    if key not in df.index:
        return None
    row = df.loc[key]
    if isinstance(row, pd.DataFrame):
        row = row.iloc[0]
    return {str(column): _json_safe(row[column]) for column in df.columns}


def _tmdb_api_key(explicit_api_key: str | None = None) -> str:
    key = (explicit_api_key or os.getenv("TMDB_API_KEY", "")).strip()
    return key


def get_tmdb_zh_title_by_tmdb_id(
    tmdb_id: int | str,
    *,
    api_key: str | None = None,
    timeout: float = 5.0,
    opener=urlopen,
) -> str:
    """Fetch TMDB's zh-CN localized title for one movie id.

    The helper fails soft: missing key, HTTP/network errors, or empty/English-only
    responses all degrade to ``""`` so callers can keep ``zh_title`` empty and
    preserve the existing ``drop_cn_seg`` behavior.
    """
    key = _tmdb_api_key(api_key)
    if not key:
        return ""
    movie_id = str(tmdb_id).strip()
    if not movie_id:
        return ""

    query = urlencode({"api_key": key, "language": "zh-CN"})
    url = f"{TMDB_API_BASE_URL}/movie/{movie_id}?{query}"
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "themoviecosmos-daily-stargazing/1.0",
        },
    )
    try:
        with opener(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, URLError, ValueError, json.JSONDecodeError):
        return ""

    title = str(payload.get("title") or "").strip()
    if not title:
        return ""
    if not any("\u4e00" <= ch <= "\u9fff" for ch in title):
        return ""
    return title


def get_movie_details_by_tmdb_ids(
    tmdb_ids: Iterable[int | str],
    *,
    csv_path: Path | str | None = None,
) -> dict[str, dict[str, Any]]:
    """Batch wrapper preserving caller ids as string keys."""
    return {
        str(tmdb_id): detail
        for tmdb_id in tmdb_ids
        if (detail := get_movie_detail_by_tmdb_id(tmdb_id, csv_path=csv_path)) is not None
    }
