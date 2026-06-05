"""Shared N=10 eval batch manifest (Phase 3.6.5+). Used by tests and batch-manifest.json."""

from __future__ import annotations

import json
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
_MANIFEST_PATH = _REPO_ROOT / "tests" / "eval_news" / "batch-manifest.json"


def load_manifest(path: Path | None = None) -> list[str]:
    manifest_path = path or _MANIFEST_PATH
    data = json.loads(manifest_path.read_text(encoding="utf-8"))
    run_ids = data.get("run_ids")
    if not isinstance(run_ids, list) or not run_ids:
        raise ValueError(f"invalid run_ids in {manifest_path}")
    return [str(rid) for rid in run_ids]


def news_file_for_run_id(run_id: str, repo_root: Path | None = None) -> Path:
    root = repo_root or _REPO_ROOT
    return root / "tests" / "eval_news" / f"{run_id}.json"


def run_out_dir(run_id: str, phase_dir: str = "output/Eval/phase3.6") -> str:
    return f"{phase_dir.rstrip('/')}/{run_id}"


def validate_manifest(repo_root: Path | None = None) -> list[str]:
    """Return human-readable errors; empty list means OK."""
    root = repo_root or _REPO_ROOT
    errors: list[str] = []
    try:
        run_ids = load_manifest()
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return [str(exc)]

    if len(run_ids) != 10:
        errors.append(f"expected 10 run_ids, got {len(run_ids)}")

    seen: set[str] = set()
    for rid in run_ids:
        if rid in seen:
            errors.append(f"duplicate run_id: {rid}")
        seen.add(rid)
        news = news_file_for_run_id(rid, root)
        if not news.is_file():
            errors.append(f"missing news file: {news.relative_to(root)}")
    return errors
