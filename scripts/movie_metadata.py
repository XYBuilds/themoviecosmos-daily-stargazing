"""Full-column movie metadata lookup by TMDB id (ADR-0012 path B).

This module is deliberately separate from the retrieval hot path.  Retrieval keeps
using ``meta.parquet`` (path A) with a small column whitelist; compose/review/publish
can call this path B by ``tmdb_id`` when they need richer movie facts from the
source ``cleaned.csv``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Iterable

import pandas as pd

from scripts.lib.paths import repo_root

DEFAULT_MOVIE_DETAILS_CSV = repo_root() / "data" / "output" / "cleaned.csv"

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