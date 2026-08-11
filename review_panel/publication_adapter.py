"""Prepare one publication bundle without coupling the HTTP server to heavy capabilities.

The adapter owns the concurrency boundary.  Each selected preparation target first
claims its manifest state, then runs independently; a failed target never cancels
its siblings.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Literal

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from review_panel.publication_bundle import (
    PublicationManifest,
    manifest_path,
    new_manifest,
    read_manifest,
    update_manifest,
    write_manifest,
)
from scripts.lib.galaxy_roster import GalaxyRosterError, assert_in_galaxy_roster, load_galaxy_roster, profile_id_from_metadata
from scripts.lib.planet_renderer import PlanetRenderResult, render_planet
from scripts.lib.poster_downloader import PosterDownloadResult, download_tmdb_poster

PreparationTarget = Literal["drafts", "poster", "planet"]
_PREPARATION_TARGETS: frozenset[PreparationTarget] = frozenset({"drafts", "poster", "planet"})

DraftsRunner = Callable[[Path, str, str, int], Path]
PosterRunner = Callable[[str, Path], PosterDownloadResult]
PlanetRunner = Callable[[int, Path], PlanetRenderResult]
CandidateLoader = Callable[[Path, str, str, int], dict[str, Any]]


def _default_batch_root() -> Path:
    return Path(__file__).resolve().parents[1] / "output" / "daily_batch"


def _adapter_path() -> Path:
    return Path(__file__).resolve().parent / "drafts_adapter.py"


def _load_candidate(batch_root: Path, date: str, news_slug: str, tmdb_id: int) -> dict[str, Any]:
    """Read exactly one retrieved candidate without importing the copy/LLM adapter."""
    path = batch_root / date / news_slug / "retrieve.json"
    if not path.is_file():
        raise ValueError(f"retrieve.json not found: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    candidates = raw.get("candidates") if isinstance(raw, Mapping) else None
    if not isinstance(candidates, list):
        raise ValueError(f"retrieve.json candidates must be an array: {path}")
    match = next(
        (
            candidate
            for candidate in candidates
            if isinstance(candidate, dict) and str(candidate.get("tmdb_id")) == str(tmdb_id)
        ),
        None,
    )
    if match is None:
        raise ValueError(f"tmdb_id {tmdb_id!r} not found in {path}")
    return match


def _run_drafts(batch_root: Path, date: str, news_slug: str, tmdb_id: int) -> Path:
    """Run the existing isolated draft-pool adapter and verify its reported output."""
    result = subprocess.run(
        [
            sys.executable,
            str(_adapter_path()),
            "--date",
            date,
            "--news-slug",
            news_slug,
            "--tmdb-id",
            str(tmdb_id),
            "--platform",
            "xiaohongshu",
            "--batch-root",
            str(batch_root),
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "draft generation failed"
        raise RuntimeError(detail)
    path = batch_root / date / f"{news_slug}_drafts_xiaohongshu.json"
    if not path.is_file():
        raise RuntimeError(f"draft adapter completed without producing pool: {path}")
    return path


def _selection_snapshot(selection: Mapping[str, Any]) -> dict[str, Any]:
    selected = selection.get("selected")
    if not isinstance(selected, Mapping):
        raise ValueError("selection.json missing selected object")
    required = {
        "date": selection.get("date"),
        "news_slug": selected.get("news_slug"),
        "tmdb_id": selected.get("tmdb_id"),
        "title": selected.get("title"),
        "selected_at": selection.get("selected_at"),
    }
    missing = [key for key, value in required.items() if value in (None, "")]
    if missing:
        raise ValueError(f"selection.json missing required fields: {', '.join(missing)}")
    tmdb_id = selected.get("tmdb_id")
    if isinstance(tmdb_id, bool):
        raise ValueError("selection.json tmdb_id must be an integer")
    try:
        normalized_tmdb_id = int(tmdb_id)
    except (TypeError, ValueError) as exc:
        raise ValueError("selection.json tmdb_id must be an integer") from exc
    if normalized_tmdb_id <= 0:
        raise ValueError("selection.json tmdb_id must be positive")
    return {
        "date": str(required["date"]),
        "news_slug": str(required["news_slug"]),
        "tmdb_id": normalized_tmdb_id,
        "title": str(required["title"]),
        "selected_at": str(required["selected_at"]),
    }


def _parse_targets(targets: Sequence[str]) -> tuple[PreparationTarget, ...]:
    normalized = tuple(target.strip() for target in targets if target.strip())
    if not normalized:
        raise ValueError("at least one preparation target is required")
    unknown = sorted(set(normalized) - _PREPARATION_TARGETS)
    if unknown:
        raise ValueError(f"unknown publication target(s): {', '.join(unknown)}")
    return tuple(dict.fromkeys(normalized))  # type: ignore[return-value]


def _update_artifact(
    path: Path,
    target: PreparationTarget,
    *,
    status: Literal["pending", "running", "ready", "failed"],
    error: str | None = None,
    **fields: Any,
) -> PublicationManifest:
    def mutate(manifest: PublicationManifest) -> PublicationManifest:
        artifacts = manifest["artifacts"]
        artifact = artifacts.get(target)
        if not isinstance(artifact, dict):
            raise ValueError(f"manifest missing {target} artifact")
        artifact.update({"status": status, "error": error, **fields})
        return manifest

    return update_manifest(path, mutate)


def _selection_identity(selection: Mapping[str, Any]) -> tuple[str, str, int, str]:
    return (
        str(selection["date"]),
        str(selection["news_slug"]),
        int(selection["tmdb_id"]),
        str(selection["title"]),
    )


def _initialize_manifest(path: Path, selection: Mapping[str, Any]) -> PublicationManifest:
    snapshot = _selection_snapshot(selection)
    if not path.is_file():
        return write_manifest(path, new_manifest(snapshot))
    manifest = read_manifest(path)
    if _selection_identity(manifest["selection"]) != _selection_identity(snapshot):
        raise ValueError("existing publication manifest selection does not match selection.json")
    return manifest


def _assert_selected_deep_link_safe(tmdb_id: int) -> None:
    """Fail closed when a Chronicle release is configured and the selection is off-roster."""
    try:
        roster = load_galaxy_roster()
    except GalaxyRosterError as exc:
        message = str(exc)
        if "release input required" in message:
            return
        raise ValueError(message) from exc
    try:
        assert_in_galaxy_roster(tmdb_id, roster)
    except GalaxyRosterError as exc:
        raise ValueError(str(exc)) from exc
    print(
        f"[publication_adapter] deep-link gate ok tmdb_id={tmdb_id} "
        f"data_version={roster.data_version!r} observed_count={roster.observed_count}"
    )


def prepare_publication(
    batch_root: Path,
    selection: Mapping[str, Any],
    *,
    targets: Sequence[str] = ("drafts", "poster", "planet"),
    run_drafts: DraftsRunner = _run_drafts,
    download_poster: PosterRunner = download_tmdb_poster,
    render_planet_image: PlanetRunner = render_planet,
    load_candidate: CandidateLoader = _load_candidate,
) -> PublicationManifest:
    """Prepare independent bundle artifacts in parallel and return final manifest.

    State is persisted before workers start and after every worker terminates.  This
    makes polling deterministic even when one capability raises before its peers.
    """
    selected_targets = _parse_targets(targets)
    snapshot = _selection_snapshot(selection)
    tmdb_id = int(snapshot["tmdb_id"])
    _assert_selected_deep_link_safe(tmdb_id)
    date = str(snapshot["date"])
    news_slug = str(snapshot["news_slug"])
    title = str(snapshot["title"])
    path = manifest_path(batch_root, date, tmdb_id, title)
    manifest = _initialize_manifest(path, selection)

    for target in selected_targets:
        _update_artifact(path, target, status="running")

    def run_target(target: PreparationTarget) -> None:
        bundle = path.parent
        if target == "drafts":
            run_drafts(batch_root, date, news_slug, tmdb_id)
            _update_artifact(path, target, status="ready")
            return
        if target == "poster":
            candidate = load_candidate(batch_root, date, news_slug, tmdb_id)
            poster_path = str(candidate.get("poster_path") or "").strip()
            if not poster_path:
                raise ValueError(f"selected candidate {tmdb_id} has no poster_path")
            result = download_poster(poster_path, bundle / "assets" / "poster-original.jpg")
            _update_artifact(
                path,
                target,
                status="ready",
                source_url=result.source_url,
            )
            return
        result = render_planet_image(tmdb_id, bundle / "assets" / "planet.png", bloom=True)
        if result.output_path.name != "planet.png" or result.metadata_path.name != "planet.png.render.json":
            raise RuntimeError("planet renderer returned unexpected publication artifact paths")
        _update_artifact(
            path,
            target,
            status="ready",
            metadata_path="assets/planet.png.render.json",
            data_version=result.roster_data_version,
            manifest_url=result.metadata.get("manifest_url"),
            profile_id=profile_id_from_metadata(result.metadata),
            profile_url=result.metadata.get("profile_url"),
            observed_roster_count=result.observed_roster_count,
            chronicle_git_commit=result.metadata.get("chronicle_git_commit"),
        )

    with ThreadPoolExecutor(max_workers=len(selected_targets), thread_name_prefix="publication") as executor:
        futures = {executor.submit(run_target, target): target for target in selected_targets}
        for future in as_completed(futures):
            target = futures[future]
            try:
                future.result()
            except Exception as exc:  # noqa: BLE001 - failure must remain isolated per artifact
                _update_artifact(path, target, status="failed", error=f"{type(exc).__name__}: {exc}")

    return read_manifest(path)


def prepare_publication_for_date(
    batch_root: Path,
    date: str,
    *,
    targets: Sequence[str] = ("drafts", "poster", "planet"),
) -> PublicationManifest:
    """CLI-facing wrapper that resolves the date's current selection."""
    selection_path = batch_root / date / "selection.json"
    if not selection_path.is_file():
        raise ValueError(f"selection.json not found for date {date!r}; select a candidate first")
    raw = json.loads(selection_path.read_text(encoding="utf-8"))
    if not isinstance(raw, Mapping):
        raise ValueError("selection.json must be an object")
    return prepare_publication(batch_root, raw, targets=targets)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Prepare independent artifacts for one publication bundle.")
    parser.add_argument("--date", required=True, help="selected daily batch date, e.g. 2026-07-06")
    parser.add_argument("--batch-root", type=Path, default=_default_batch_root())
    parser.add_argument(
        "--targets",
        default="drafts,poster,planet",
        help="comma-separated subset of drafts,poster,planet",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)
    targets = [target.strip() for target in args.targets.split(",")]
    try:
        manifest = prepare_publication_for_date(args.batch_root, args.date, targets=targets)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(manifest, ensure_ascii=False), file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())