"""Chronicle Galaxy Roster membership for Daily deep-link safety.

Loads the allowed TMDB identity set from the same explicit Chronicle release
input used for Planet Export (manifest URL or offline data-file override).
"""

from __future__ import annotations

import gzip
import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Literal
from urllib.parse import urlparse


class GalaxyRosterError(RuntimeError):
    """Raised when the Chronicle release input or galaxy artifact cannot be used."""


ReleaseKind = Literal["manifest_url", "data_file"]


@dataclass(frozen=True)
class ChronicleReleaseInput:
    kind: ReleaseKind
    manifest_url: str | None = None
    data_file: Path | None = None


@dataclass(frozen=True)
class GalaxyRoster:
    data_version: str
    observed_count: int
    allowed_ids: frozenset[int]
    source_label: str


FetchBytes = Callable[[str], bytes]


def resolve_chronicle_release_input() -> ChronicleReleaseInput:
    """Require exactly one of MANIFEST_URL (production) or DATA_FILE (offline/test)."""
    manifest_url = os.environ.get("MOVIE_COSMOS_GALAXY_MANIFEST_URL", "").strip()
    data_file_raw = os.environ.get("MOVIE_COSMOS_GALAXY_DATA_FILE", "").strip()

    if manifest_url and data_file_raw:
        raise GalaxyRosterError(
            "choose exactly one Chronicle release input: "
            "MOVIE_COSMOS_GALAXY_MANIFEST_URL or MOVIE_COSMOS_GALAXY_DATA_FILE"
        )
    if not manifest_url and not data_file_raw:
        raise GalaxyRosterError(
            "Chronicle release input required: set MOVIE_COSMOS_GALAXY_MANIFEST_URL "
            "(production) or MOVIE_COSMOS_GALAXY_DATA_FILE (offline/test)"
        )

    if manifest_url:
        _assert_http_json_url(manifest_url, "MOVIE_COSMOS_GALAXY_MANIFEST_URL")
        return ChronicleReleaseInput(kind="manifest_url", manifest_url=manifest_url)

    data_file = Path(data_file_raw).expanduser().resolve()
    if not data_file.is_file():
        raise GalaxyRosterError(
            f"MOVIE_COSMOS_GALAXY_DATA_FILE must point to an existing galaxy JSON file: {data_file}"
        )
    return ChronicleReleaseInput(kind="data_file", data_file=data_file)


def _assert_http_json_url(raw: str, label: str) -> None:
    try:
        parsed = urlparse(raw)
    except ValueError as exc:
        raise GalaxyRosterError(f"{label} is not a valid URL: {raw!r}") from exc
    if parsed.scheme not in {"http", "https"} or not parsed.netloc or parsed.username or parsed.password:
        raise GalaxyRosterError(f"{label} must be an http(s) URL without credentials: {raw!r}")
    if parsed.query or parsed.fragment:
        raise GalaxyRosterError(f"{label} must not include query or fragment: {raw!r}")
    if not parsed.path.lower().endswith(".json"):
        raise GalaxyRosterError(f"{label} must end with .json: {raw!r}")


def _default_fetch_bytes(url: str) -> bytes:
    try:
        with urllib.request.urlopen(url, timeout=60) as response:  # noqa: S310 - explicit release URLs only
            return response.read()
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise GalaxyRosterError(f"unable to fetch Chronicle release artifact: {url}: {exc}") from exc


def _maybe_gunzip(payload: bytes) -> bytes:
    if len(payload) >= 2 and payload[0] == 0x1F and payload[1] == 0x8B:
        try:
            return gzip.decompress(payload)
        except OSError as exc:
            raise GalaxyRosterError(f"galaxy artifact is not valid gzip: {exc}") from exc
    return payload


def _parse_galaxy_payload(payload: bytes, *, source_label: str) -> GalaxyRoster:
    try:
        text = _maybe_gunzip(payload).decode("utf-8")
        data = json.loads(text)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GalaxyRosterError(f"galaxy artifact is not valid JSON: {source_label}: {exc}") from exc

    if not isinstance(data, dict):
        raise GalaxyRosterError(f"galaxy artifact must be a JSON object: {source_label}")

    movies = data.get("movies")
    if not isinstance(movies, list) or not movies:
        raise GalaxyRosterError(f"galaxy artifact movies[] is missing or empty: {source_label}")

    allowed: set[int] = set()
    for index, movie in enumerate(movies):
        if not isinstance(movie, dict):
            raise GalaxyRosterError(f"galaxy artifact movies[{index}] must be an object: {source_label}")
        movie_id = movie.get("id")
        if isinstance(movie_id, bool) or not isinstance(movie_id, int) or movie_id <= 0:
            raise GalaxyRosterError(f"galaxy artifact movies[{index}].id is invalid: {movie_id!r}")
        allowed.add(movie_id)

    meta = data.get("meta") if isinstance(data.get("meta"), dict) else {}
    data_version = meta.get("version") if isinstance(meta, dict) else None
    if not isinstance(data_version, str) or not data_version.strip():
        raise GalaxyRosterError(f"galaxy artifact meta.version is required: {source_label}")

    observed_count = len(allowed)
    meta_count = meta.get("count") if isinstance(meta, dict) else None
    if isinstance(meta_count, int) and meta_count != observed_count:
        print(
            f"[galaxy_roster] warning: meta.count={meta_count} != distinct movie ids={observed_count} "
            f"source={source_label}"
        )

    print(
        f"[galaxy_roster] loaded source={source_label} data_version={data_version!r} "
        f"observed_count={observed_count} id_min={min(allowed)} id_max={max(allowed)}"
    )
    return GalaxyRoster(
        data_version=data_version.strip(),
        observed_count=observed_count,
        allowed_ids=frozenset(allowed),
        source_label=source_label,
    )


def _load_manifest_galaxy(manifest_url: str, *, fetch_bytes: FetchBytes) -> GalaxyRoster:
    try:
        manifest = json.loads(fetch_bytes(manifest_url).decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise GalaxyRosterError(f"unable to parse Chronicle manifest JSON: {manifest_url}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise GalaxyRosterError(f"Chronicle manifest must be a JSON object: {manifest_url}")

    galaxy_url = manifest.get("galaxy_data_gzip_url")
    if not isinstance(galaxy_url, str) or not galaxy_url.strip():
        raise GalaxyRosterError(f"Chronicle manifest missing galaxy_data_gzip_url: {manifest_url}")
    data_version = manifest.get("data_version")
    if not isinstance(data_version, str) or not data_version.strip():
        raise GalaxyRosterError(f"Chronicle manifest missing data_version: {manifest_url}")
    profile = manifest.get("focus_emission_profile")
    if not isinstance(profile, dict) or profile.get("status") != "active":
        raise GalaxyRosterError(f"Chronicle manifest missing active focus_emission_profile: {manifest_url}")
    profile_url = manifest.get("focus_emission_profile_url")
    if not isinstance(profile_url, str) or not profile_url.strip():
        raise GalaxyRosterError(f"Chronicle manifest missing focus_emission_profile_url: {manifest_url}")

    roster = _parse_galaxy_payload(fetch_bytes(galaxy_url.strip()), source_label=galaxy_url.strip())
    if roster.data_version != data_version.strip():
        raise GalaxyRosterError(
            f"galaxy data_version {roster.data_version!r} does not match manifest "
            f"data_version {data_version.strip()!r}"
        )
    return GalaxyRoster(
        data_version=roster.data_version,
        observed_count=roster.observed_count,
        allowed_ids=roster.allowed_ids,
        source_label=manifest_url,
    )


def load_galaxy_roster(
    *,
    release: ChronicleReleaseInput | None = None,
    fetch_bytes: FetchBytes = _default_fetch_bytes,
) -> GalaxyRoster:
    """Load allowed TMDB ids from the explicit Chronicle release selected for this run."""
    selected = release or resolve_chronicle_release_input()
    if selected.kind == "data_file":
        assert selected.data_file is not None
        try:
            payload = selected.data_file.read_bytes()
        except OSError as exc:
            raise GalaxyRosterError(f"unable to read MOVIE_COSMOS_GALAXY_DATA_FILE: {exc}") from exc
        return _parse_galaxy_payload(payload, source_label=str(selected.data_file))

    assert selected.manifest_url is not None
    return _load_manifest_galaxy(selected.manifest_url, fetch_bytes=fetch_bytes)


def assert_in_galaxy_roster(tmdb_id: int, roster: GalaxyRoster) -> None:
    """Fail closed when a Daily movie is absent from the selected Chronicle roster."""
    if tmdb_id <= 0:
        raise GalaxyRosterError(f"tmdb_id must be a positive integer, got {tmdb_id}")
    if tmdb_id not in roster.allowed_ids:
        raise GalaxyRosterError(
            f"tmdb_id {tmdb_id} is not in Chronicle Galaxy Roster "
            f"(data_version={roster.data_version!r}, observed_count={roster.observed_count}, "
            f"source={roster.source_label})"
        )


def assert_movie_url_allowed(tmdb_id: int, *, prefix: str) -> str:
    """Build ``/movie/{id}`` only when the id belongs to the configured Chronicle roster.

    When no Chronicle release input is configured, returns the URL unchecked (eval/offline
    paths). Production publication must configure the release and will fail closed earlier.
    """
    url = f"{prefix.rstrip('/')}/{tmdb_id}"
    try:
        roster = load_galaxy_roster()
    except GalaxyRosterError as exc:
        if "release input required" in str(exc):
            return url
        raise
    assert_in_galaxy_roster(tmdb_id, roster)
    return url


def profile_id_from_metadata(metadata: Any) -> str | None:
    """Extract a profile id from Chronicle planet render sidecar fields when present."""
    if not isinstance(metadata, dict):
        return None
    for key in ("focus_emission_profile", "requested_focus_emission_profile"):
        value = metadata.get(key)
        if isinstance(value, dict):
            profile_id = value.get("profile_id")
            if isinstance(profile_id, str) and profile_id.strip():
                return profile_id.strip()
    return None
