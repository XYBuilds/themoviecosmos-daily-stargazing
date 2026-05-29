"""Repository path helpers (resolved from repo root via pathlib)."""

from __future__ import annotations

import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]


def repo_root() -> Path:
    """Absolute path to the repository root."""
    return _REPO_ROOT


def _resolve_path(env_var: str, default: str) -> Path:
    raw = os.getenv(env_var, default)
    path = Path(raw)
    if not path.is_absolute():
        path = _REPO_ROOT / path
    return path


def cleaned_csv() -> Path:
    """SSOT movie list (cosmos cleaned export)."""
    return _resolve_path("CLEANED_CSV", "data/output/cleaned.csv")


def embeddings_source_npy() -> Path:
    """Cosmos text embeddings source (read-only; ADR-0001)."""
    return _resolve_path("EMBEDDINGS_SOURCE", "data/output/text_embeddings.npy")


def index_dir() -> Path:
    """Directory for index artifacts (meta.parquet, embeddings.npy)."""
    return _resolve_path("INDEX_DIR", "data/index")


def embeddings_npy() -> Path:
    """Retrieval embeddings entry under index_dir."""
    return index_dir() / "embeddings.npy"


def meta_parquet() -> Path:
    """Retrieval metadata under index_dir."""
    return index_dir() / "meta.parquet"
