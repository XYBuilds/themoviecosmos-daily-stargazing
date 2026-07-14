"""Tests for verified TMDB poster downloads."""

from __future__ import annotations

import urllib.error
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts.lib.poster_downloader import (
    PosterDownloadError,
    download_tmdb_poster,
    poster_source_url,
)
from scripts.publish_discord import write_outputs


class _StubResponse:
    def __init__(self, payload: bytes, *, content_type: str = "image/jpeg") -> None:
        self._payload = payload
        self.headers = {"Content-Type": content_type}

    def __enter__(self) -> _StubResponse:
        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> bool:
        return False

    def read(self) -> bytes:
        return self._payload


class PosterDownloaderTests(unittest.TestCase):
    def test_downloads_and_atomically_writes_verified_jpeg(self) -> None:
        with TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "assets" / "poster-original.jpg"

            def opener(request: object, *, timeout: float) -> _StubResponse:
                self.assertEqual(timeout, 30.0)
                self.assertEqual(request.full_url, "https://image.tmdb.org/t/p/original/poster.jpg")
                return _StubResponse(b"\xff\xd8\xff\xe0valid-jpeg", content_type="image/jpeg; charset=binary")

            result = download_tmdb_poster("/poster.jpg", output_path, opener=opener)

            self.assertEqual(result.source_url, "https://image.tmdb.org/t/p/original/poster.jpg")
            self.assertEqual(result.content_type, "image/jpeg")
            self.assertEqual(result.file_size, 14)
            self.assertEqual(output_path.read_bytes(), b"\xff\xd8\xff\xe0valid-jpeg")
            self.assertFalse(list(output_path.parent.glob("*.tmp")))

    def test_accepts_png_magic(self) -> None:
        with TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "poster-original.jpg"
            result = download_tmdb_poster(
                "/poster.png",
                output_path,
                opener=lambda request, timeout: _StubResponse(b"\x89PNG\r\n\x1a\npayload", content_type="image/png"),
            )

            self.assertEqual(result.content_type, "image/png")
            self.assertTrue(output_path.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"))

    def test_http_failure_leaves_no_partial_file(self) -> None:
        with TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "poster-original.jpg"

            def opener(request: object, *, timeout: float) -> _StubResponse:
                raise urllib.error.HTTPError(request.full_url, 404, "not found", {}, None)

            with self.assertRaisesRegex(PosterDownloadError, "failed to download"):
                download_tmdb_poster("/missing.jpg", output_path, opener=opener)
            self.assertFalse(output_path.exists())

    def test_timeout_leaves_no_partial_file(self) -> None:
        with TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "poster-original.jpg"
            with self.assertRaisesRegex(PosterDownloadError, "failed to download"):
                download_tmdb_poster(
                    "/slow.jpg",
                    output_path,
                    opener=lambda request, timeout: (_ for _ in ()).throw(TimeoutError("timed out")),
                )
            self.assertFalse(output_path.exists())

    def test_empty_or_non_image_response_leaves_no_partial_file(self) -> None:
        with TemporaryDirectory() as tmp:
            empty_output = Path(tmp) / "empty.jpg"
            invalid_output = Path(tmp) / "invalid.jpg"
            with self.assertRaisesRegex(PosterDownloadError, "empty"):
                download_tmdb_poster(
                    "/empty.jpg",
                    empty_output,
                    opener=lambda request, timeout: _StubResponse(b""),
                )
            with self.assertRaisesRegex(PosterDownloadError, "magic"):
                download_tmdb_poster(
                    "/not-an-image.jpg",
                    invalid_output,
                    opener=lambda request, timeout: _StubResponse(b"<html>error</html>"),
                )
            self.assertFalse(empty_output.exists())
            self.assertFalse(invalid_output.exists())

    def test_discord_output_reuses_verified_downloader_and_preserves_names(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            with (
                patch("scripts.publish_discord.repo_root", return_value=root),
                patch("scripts.publish_discord.download_tmdb_poster") as download,
            ):
                markdown_path, poster_path = write_outputs(
                    "2026-07-06",
                    "670292",
                    "Discord body\n",
                    {"poster_path": "/creator.jpg"},
                )

            self.assertEqual(markdown_path, root / "output" / "discord" / "2026-07-06-discord-670292.md")
            self.assertEqual(poster_path, root / "output" / "discord" / "2026-07-06-discord-670292-poster.jpg")
            self.assertEqual(markdown_path.read_text(encoding="utf-8"), "Discord body\n")
            download.assert_called_once_with("/creator.jpg", poster_path)

    def test_rejects_unsafe_or_empty_poster_paths(self) -> None:
        for poster_path in ("", "poster.jpg", "//other-host/poster.jpg"):
            with self.subTest(poster_path=poster_path):
                with self.assertRaises(PosterDownloadError):
                    poster_source_url(poster_path)


if __name__ == "__main__":
    unittest.main()