"""Publication bundle domain: path projection, manifest validation and atomic persistence.

All modules that need publication artifacts go through this boundary.  It prevents
``output/publications`` path rules and concurrent JSON writes from leaking into
HTTP handlers or adapters.
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import threading
import unicodedata
from collections.abc import Mapping
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Literal, TypedDict, cast

ManifestStatus = Literal["preparing", "partial", "ready", "superseded"]
ArtifactStatus = Literal["pending", "running", "ready", "failed"]
_SCHEMA_VERSION = 1
_SAFE_SLUG_RE = re.compile(r"[^a-z0-9]+")
_MANIFEST_LOCKS: dict[Path, threading.RLock] = {}
_MANIFEST_LOCKS_GUARD = threading.Lock()
_UNSET = object()


class Artifact(TypedDict, total=False):
    status: ArtifactStatus
    path: str | None
    metadata_path: str | None
    source_url: str | None
    error: str | None
    selected_draft_id: str | None
    copy_path: str | None
    humanized_path: str | None


class SelectionSnapshot(TypedDict):
    date: str
    news_slug: str
    tmdb_id: int
    title: str
    selected_at: str


class PublicationManifest(TypedDict):
    schema_version: int
    publication_id: str
    status: ManifestStatus
    selection: SelectionSnapshot
    artifacts: dict[str, Artifact | dict[str, Artifact]]


def publications_root(batch_root: Path) -> Path:
    """Return the sibling publications workspace for a daily_batch root."""
    return batch_root.parent / "publications"


def slugify_title(title: str) -> str:
    """Produce a deterministic Windows-safe ASCII slug, or an empty string."""
    normalized = unicodedata.normalize("NFKD", title).encode("ascii", "ignore").decode("ascii")
    slug = _SAFE_SLUG_RE.sub("-", normalized.lower()).strip("-")
    return slug


def _normalise_tmdb_id(tmdb_id: int | str) -> int:
    if isinstance(tmdb_id, bool):
        raise ValueError("tmdb_id must be an integer")
    try:
        value = int(tmdb_id)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"tmdb_id must be an integer: {tmdb_id!r}") from exc
    if value <= 0:
        raise ValueError(f"tmdb_id must be positive: {tmdb_id!r}")
    return value


def bundle_id(tmdb_id: int | str, title: str) -> str:
    """Return ``{tmdb_id}-{slug}``, falling back to just the TMDB id."""
    movie_id = _normalise_tmdb_id(tmdb_id)
    slug = slugify_title(title)
    return f"{movie_id}-{slug}" if slug else str(movie_id)


def publication_id(date: str, tmdb_id: int | str, title: str) -> str:
    """Return the stable logical publication identifier."""
    _validate_date_segment(date)
    return f"{date}/{bundle_id(tmdb_id, title)}"


def bundle_dir(batch_root: Path, date: str, tmdb_id: int | str, title: str) -> Path:
    """Project one selection into its publication bundle directory."""
    return publications_root(batch_root) / date / bundle_id(tmdb_id, title)


def manifest_path(batch_root: Path, date: str, tmdb_id: int | str, title: str) -> Path:
    return bundle_dir(batch_root, date, tmdb_id, title) / "manifest.json"


def _validate_date_segment(date: str) -> None:
    if not date or Path(date).name != date or date in {".", ".."}:
        raise ValueError(f"unsafe publication date segment: {date!r}")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _artifact(status: ArtifactStatus, path: str | None, **extra: Any) -> Artifact:
    return cast(Artifact, {"status": status, "path": path, "error": None, **extra})


def new_manifest(selection: Mapping[str, Any]) -> PublicationManifest:
    """Create a strict schema-v1 manifest from the selected candidate snapshot."""
    required = ("date", "news_slug", "tmdb_id", "title")
    missing = [key for key in required if not selection.get(key)]
    if missing:
        raise ValueError(f"selection missing required fields: {', '.join(missing)}")

    date = str(selection["date"])
    tmdb_id = _normalise_tmdb_id(selection["tmdb_id"])
    title = str(selection["title"]).strip()
    if not title:
        raise ValueError("selection title must not be empty")
    _validate_date_segment(date)
    selected_at = str(selection.get("selected_at") or _utc_now())

    manifest: PublicationManifest = {
        "schema_version": _SCHEMA_VERSION,
        "publication_id": publication_id(date, tmdb_id, title),
        "status": "preparing",
        "selection": {
            "date": date,
            "news_slug": str(selection["news_slug"]),
            "tmdb_id": tmdb_id,
            "title": title,
            "selected_at": selected_at,
        },
        "artifacts": {
            "drafts": _artifact("pending", None),
            "poster": _artifact("pending", "assets/poster-original.jpg", source_url=None),
            "planet": _artifact(
                "pending",
                "assets/planet.png",
                metadata_path="assets/planet.png.render.json",
            ),
            "copies": {
                "xiaohongshu": _artifact(
                    "pending",
                    None,
                    selected_draft_id=None,
                    copy_path="copy/xiaohongshu.md",
                    humanized_path="copy/xiaohongshu-humanized.md",
                )
            },
        },
    }
    validate_manifest(manifest)
    return manifest


def _iter_artifacts(
    artifacts: Mapping[str, Any], *, include_copies: bool = True
) -> list[Mapping[str, Any]]:
    result: list[Mapping[str, Any]] = []
    for name, artifact in artifacts.items():
        if name == "copies":
            if not isinstance(artifact, Mapping):
                raise ValueError("manifest artifacts.copies must be an object")
            if include_copies:
                result.extend(value for value in artifact.values() if isinstance(value, Mapping))
        elif isinstance(artifact, Mapping):
            result.append(artifact)
        else:
            raise ValueError(f"manifest artifact {name!r} must be an object")
    return result


def derive_status(artifacts: Mapping[str, Any], *, superseded: bool = False) -> ManifestStatus:
    """Merge preparation artifact states; editorial copies do not block preparation."""
    if superseded:
        return "superseded"
    entries = _iter_artifacts(artifacts, include_copies=False)
    if not entries:
        raise ValueError("manifest must contain preparation artifacts")
    statuses = [entry.get("status") for entry in entries]
    unknown = sorted({str(status) for status in statuses if status not in {"pending", "running", "ready", "failed"}})
    if unknown:
        raise ValueError(f"unknown artifact status: {', '.join(unknown)}")
    if any(status == "running" for status in statuses) or any(status == "pending" for status in statuses):
        return "preparing"
    if any(status == "failed" for status in statuses):
        return "partial"
    return "ready"


def _validate_relative_path(value: Any, field: str) -> None:
    if value is None:
        return
    if not isinstance(value, str) or not value:
        raise ValueError(f"manifest {field} must be a non-empty relative path or null")
    windows_path = PureWindowsPath(value)
    posix_path = PurePosixPath(value)
    if windows_path.is_absolute() or posix_path.is_absolute() or windows_path.drive or ".." in windows_path.parts or ".." in posix_path.parts:
        raise ValueError(f"manifest {field} escapes its publication bundle: {value!r}")


def validate_manifest(raw: Mapping[str, Any]) -> PublicationManifest:
    """Fail fast on incompatible schema, missing fields and unsafe artifact paths."""
    if raw.get("schema_version") != _SCHEMA_VERSION:
        raise ValueError(f"unsupported manifest schema_version: {raw.get('schema_version')!r}")
    for key in ("publication_id", "status", "selection", "artifacts"):
        if key not in raw:
            raise ValueError(f"manifest missing required field: {key}")
    if raw["status"] not in {"preparing", "partial", "ready", "superseded"}:
        raise ValueError(f"unknown manifest status: {raw['status']!r}")
    selection = raw["selection"]
    if not isinstance(selection, Mapping):
        raise ValueError("manifest selection must be an object")
    for key in ("date", "news_slug", "tmdb_id", "title", "selected_at"):
        if not selection.get(key):
            raise ValueError(f"manifest selection missing required field: {key}")
    expected_publication_id = publication_id(
        str(selection["date"]),
        selection["tmdb_id"],
        str(selection["title"]),
    )
    if raw["publication_id"] != expected_publication_id:
        raise ValueError("manifest publication_id does not match selection")
    for key in ("news_slug", "selected_at"):
        if not selection.get(key):
            raise ValueError(f"manifest selection missing required field: {key}")

    artifacts = raw["artifacts"]
    if not isinstance(artifacts, Mapping):
        raise ValueError("manifest artifacts must be an object")
    entries = _iter_artifacts(artifacts)
    if not entries:
        raise ValueError("manifest must contain artifacts")
    for artifact in entries:
        if artifact.get("status") not in {"pending", "running", "ready", "failed"}:
            raise ValueError(f"unknown artifact status: {artifact.get('status')!r}")
        for key, value in artifact.items():
            if key.endswith("_path") or key == "path":
                _validate_relative_path(value, key)
    derived_status = derive_status(artifacts, superseded=raw["status"] == "superseded")
    if raw["status"] != derived_status:
        raise ValueError(
            f"manifest status {raw['status']!r} does not match derived status {derived_status!r}"
        )
    return cast(PublicationManifest, deepcopy(dict(raw)))


def _lock_for(path: Path) -> threading.RLock:
    resolved = path.resolve()
    with _MANIFEST_LOCKS_GUARD:
        return _MANIFEST_LOCKS.setdefault(resolved, threading.RLock())


def read_manifest(path: Path) -> PublicationManifest:
    """Read and validate a persisted publication manifest."""
    with _lock_for(path):
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError as exc:
            raise ValueError(f"publication manifest not found: {path}") from exc
    if not isinstance(raw, Mapping):
        raise ValueError("manifest root must be an object")
    return validate_manifest(raw)


def write_manifest(path: Path, manifest: Mapping[str, Any]) -> PublicationManifest:
    """Validate and atomically replace a manifest under a per-bundle lock."""
    validated = validate_manifest(manifest)
    payload = json.dumps(validated, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    with _lock_for(path):
        fd, temporary_name = tempfile.mkstemp(prefix=".manifest-", suffix=".json", dir=path.parent, text=True)
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(payload)
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary_name, path)
        except BaseException:
            Path(temporary_name).unlink(missing_ok=True)
            raise
    return validated


def update_manifest(path: Path, mutate: Any) -> PublicationManifest:
    """Apply one locked mutation and recompute its derived top-level status."""
    with _lock_for(path):
        current = read_manifest(path)
        updated = mutate(deepcopy(current))
        if not isinstance(updated, Mapping):
            raise ValueError("manifest mutation must return an object")
        next_manifest = dict(updated)
        next_manifest["status"] = derive_status(
            cast(Mapping[str, Any], next_manifest.get("artifacts", {})),
            superseded=next_manifest.get("status") == "superseded",
        )
        return write_manifest(path, next_manifest)


def supersede_manifest(path: Path) -> PublicationManifest:
    """Retain an old bundle as immutable audit evidence after a changed selection."""
    return update_manifest(path, lambda manifest: {**manifest, "status": "superseded"})


def reactivate_manifest(path: Path) -> PublicationManifest:
    """Restore a retained bundle when its candidate becomes the active selection again."""
    return update_manifest(path, lambda manifest: {**manifest, "status": "preparing"})


def copy_artifact_paths(manifest: Mapping[str, Any], bundle_root: Path, platform: str) -> tuple[Path, Path]:
    """Resolve one platform's current and humanized copy paths inside its bundle."""
    copies = manifest.get("artifacts", {}).get("copies", {})
    artifact = copies.get(platform) if isinstance(copies, Mapping) else None
    if not isinstance(artifact, Mapping):
        raise ValueError(f"manifest missing copy artifact for platform {platform!r}")
    copy_path = artifact.get("copy_path")
    humanized_path = artifact.get("humanized_path")
    if not isinstance(copy_path, str) or not isinstance(humanized_path, str):
        raise ValueError(f"manifest copy artifact has invalid paths for platform {platform!r}")
    _validate_relative_path(copy_path, "copy_path")
    _validate_relative_path(humanized_path, "humanized_path")
    return bundle_root / copy_path, bundle_root / humanized_path


def update_copy_artifact(
    path: Path,
    platform: str,
    *,
    status: ArtifactStatus | None = None,
    selected_draft_id: str | None | object = _UNSET,
) -> PublicationManifest:
    """Persist editorial copy state without letting callers rewrite a manifest directly."""
    def mutate(manifest: PublicationManifest) -> PublicationManifest:
        copies = manifest["artifacts"].get("copies")
        artifact = copies.get(platform) if isinstance(copies, dict) else None
        if not isinstance(artifact, dict):
            raise ValueError(f"manifest missing copy artifact for platform {platform!r}")
        if status is not None:
            artifact["status"] = status
        if selected_draft_id is not _UNSET:
            artifact["selected_draft_id"] = selected_draft_id
        return manifest

    return update_manifest(path, mutate)