"""Verified TMDB poster downloads for publication-oriented workflows."""

from __future__ import annotations

import os
import tempfile
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Protocol

TMDB_POSTER_BASE_URL = "https://image.tmdb.org/t/p/original"
DEFAULT_TIMEOUT_SECONDS = 30.0
USER_AGENT = "themoviecosmos-poster-downloader/1.0"
_JPEG_MAGIC = b"\xff\xd8\xff"
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


class PosterDownloadError(RuntimeError):
    """Raised when a TMDB poster cannot be downloaded as a verified image."""


class _Response(Protocol):
    headers: Any

    def __enter__(self) -> _Response: ...

    def __exit__(self, exc_type: Any, exc_value: Any, traceback: Any) -> bool | None: ...

    def read(self) -> bytes: ...


UrlOpener = Callable[..., _Response]


@dataclass(frozen=True)
class PosterDownloadResult:
    source_url: str
    output_path: Path
    file_size: int
    content_type: str | None


def poster_source_url(poster_path: str) -> str:
    """Return the canonical TMDB original-image URL for one poster path."""
    normalized_path = poster_path.strip()
    if not normalized_path or not normalized_path.startswith("/") or normalized_path.startswith("//"):
        raise PosterDownloadError(f"poster_path must be a TMDB absolute path, got {poster_path!r}")
    return f"{TMDB_POSTER_BASE_URL}{normalized_path}"


def _content_type(response: _Response) -> str | None:
    raw_value = response.headers.get("Content-Type") if response.headers is not None else None
    if raw_value is None:
        return None
    return str(raw_value).split(";", 1)[0].strip().lower() or None


def _validate_image_payload(payload: bytes, *, source_url: str) -> None:
    if not payload:
        raise PosterDownloadError(f"TMDB poster response is empty: {source_url}")
    if not payload.startswith((_JPEG_MAGIC, _PNG_MAGIC)):
        raise PosterDownloadError(f"TMDB poster has unsupported image magic: {source_url}")


def _atomic_write(output_path: Path, payload: bytes) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.",
        suffix=".tmp",
        dir=output_path.parent,
    )
    temporary_path = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary_path, output_path)
    except BaseException:
        temporary_path.unlink(missing_ok=True)
        raise


def download_tmdb_poster(
    poster_path: str,
    output_path: Path,
    *,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
    opener: UrlOpener = urllib.request.urlopen,
) -> PosterDownloadResult:
    """Download one JPEG or PNG poster and atomically persist the validated bytes."""
    if timeout_seconds <= 0:
        raise ValueError(f"timeout_seconds must be positive, got {timeout_seconds}")

    source_url = poster_source_url(poster_path)
    request = urllib.request.Request(source_url, headers={"User-Agent": USER_AGENT})
    try:
        with opener(request, timeout=timeout_seconds) as response:
            payload = response.read()
            content_type = _content_type(response)
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise PosterDownloadError(f"failed to download TMDB poster from {source_url}: {exc}") from exc

    _validate_image_payload(payload, source_url=source_url)
    resolved_output = output_path.expanduser().resolve()
    _atomic_write(resolved_output, payload)
    print(
        f"[poster_downloader] complete source={source_url} bytes={len(payload)} "
        f"output={resolved_output}"
    )
    return PosterDownloadResult(
        source_url=source_url,
        output_path=resolved_output,
        file_size=len(payload),
        content_type=content_type,
    )