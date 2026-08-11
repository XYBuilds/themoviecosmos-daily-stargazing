"""build_index.py · 构建纯文本检索索引（ADR-0001 复用模式）。

默认 --reuse：从 cleaned.csv 写 meta.parquet，并同步 cosmos 向量到 data/index/。
Post-MVP：--rebuild-embed 预留从 CSV 重算 embedding（本 Phase 未实现）。

用法:
  python scripts/build_index.py
  python scripts/build_index.py --reuse
  python scripts/build_index.py --csv PATH
  python scripts/build_index.py --rebuild-embed
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

import numpy as np
import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CSV = REPO_ROOT / "data" / "output" / "cleaned.csv"
DEFAULT_EMBEDDINGS_SOURCE = REPO_ROOT / "data" / "output" / "text_embeddings.npy"
EXPECTED_EMBEDDING_DIM = 384


META_COLUMNS = [
    "id",
    "title",
    "original_title",
    "overview",
    "tagline",
    "genres",
    "original_language",
    "release_date",
    "poster_path",
]


def _index_dir() -> Path:
    import os

    raw = os.getenv("INDEX_DIR", "data/index")
    path = Path(raw)
    if not path.is_absolute():
        path = REPO_ROOT / path
    return path


def _reuse(csv_path: Path, index_dir: Path, embeddings_source: Path) -> None:
    if not csv_path.is_file():
        print(f"error: CSV not found: {csv_path}", file=sys.stderr)
        sys.exit(1)
    if not embeddings_source.is_file():
        print(f"error: embeddings source not found: {embeddings_source}", file=sys.stderr)
        sys.exit(1)

    df = pd.read_csv(csv_path)
    row_count = len(df)
    print(f"[build_index] csv rows={row_count} path={csv_path}")

    missing_cols = [c for c in META_COLUMNS if c not in df.columns]
    if missing_cols:
        print(f"error: CSV missing columns: {missing_cols}", file=sys.stderr)
        sys.exit(1)

    meta = df[META_COLUMNS].copy()
    index_dir.mkdir(parents=True, exist_ok=True)

    meta_path = index_dir / "meta.parquet"
    meta.to_parquet(meta_path, index=False)

    embeddings = np.load(embeddings_source, mmap_mode="r")
    if embeddings.shape[0] != len(meta):
        print(
            f"error: row mismatch — meta={len(meta)}, embeddings={embeddings.shape[0]}",
            file=sys.stderr,
        )
        sys.exit(1)
    if embeddings.ndim != 2 or embeddings.shape[1] != EXPECTED_EMBEDDING_DIM:
        print(
            f"error: expected embeddings shape (N, {EXPECTED_EMBEDDING_DIM}), got {embeddings.shape}",
            file=sys.stderr,
        )
        sys.exit(1)
    print(
        f"[build_index] embeddings shape={embeddings.shape} "
        f"dtype={embeddings.dtype} rows={len(meta)}"
    )

    dest_embeddings = index_dir / "embeddings.npy"
    shutil.copy2(embeddings_source, dest_embeddings)

    written = np.load(dest_embeddings)
    if written.shape != embeddings.shape:
        print("error: embeddings copy verification failed", file=sys.stderr)
        sys.exit(1)

    print(f"rows: {len(meta)}")
    print(f"embedding shape: {written.shape}")
    print(f"index dir: {index_dir.resolve()}")
    print(f"meta: {meta_path.resolve()}")
    print(f"embeddings: {dest_embeddings.resolve()}")


def _rebuild_embed() -> None:
    print("error: --rebuild-embed is not implemented (Post-MVP)", file=sys.stderr)
    sys.exit(1)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Build text search index (meta.parquet + embeddings.npy)."
    )
    parser.add_argument(
        "--reuse",
        action="store_true",
        default=True,
        help="Reuse cosmos embeddings (default).",
    )
    parser.add_argument(
        "--csv",
        type=Path,
        default=DEFAULT_CSV,
        help=f"Source CSV for meta (default: {DEFAULT_CSV.relative_to(REPO_ROOT)}).",
    )
    parser.add_argument(
        "--embeddings-source",
        type=Path,
        default=DEFAULT_EMBEDDINGS_SOURCE,
        help="Source .npy for --reuse (default: data/output/text_embeddings.npy).",
    )
    parser.add_argument(
        "--rebuild-embed",
        action="store_true",
        help="Re-encode embeddings from CSV (Post-MVP; not implemented).",
    )
    args = parser.parse_args(argv)

    if args.rebuild_embed:
        _rebuild_embed()

    csv_path = args.csv if args.csv.is_absolute() else REPO_ROOT / args.csv
    emb_source = (
        args.embeddings_source
        if args.embeddings_source.is_absolute()
        else REPO_ROOT / args.embeddings_source
    )
    _reuse(csv_path, _index_dir(), emb_source)


if __name__ == "__main__":
    main()
