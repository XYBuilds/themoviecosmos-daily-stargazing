"""Tests for the publication preparation boundary and constrained HTTP endpoints."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace

from review_panel.job_store import JobStore, _inline_executor
from review_panel.publication_adapter import prepare_publication
from review_panel.publication_bundle import manifest_path, new_manifest, write_manifest
from review_panel.serve import PublicationAssetResponse, route, write_selection
from scripts.lib.planet_renderer import PlanetRenderResult
from scripts.lib.poster_downloader import PosterDownloadResult

_DATE = "2026-07-06"
_SLUG = "05-signal"
_TMDB_ID = 670292
_TITLE = "The Creator"


class _InlineJobStore(JobStore):
    def submit(self, work, kind, *, executor=_inline_executor):  # noqa: ANN001
        return super().submit(work, kind, executor=executor)


def _selection() -> dict[str, object]:
    return {
        "date": _DATE,
        "selected": {"news_slug": _SLUG, "tmdb_id": _TMDB_ID, "title": _TITLE},
        "selected_at": "2026-07-06T00:00:00Z",
        "copies": {},
    }


def _snapshot() -> dict[str, object]:
    return {
        "date": _DATE,
        "news_slug": _SLUG,
        "tmdb_id": _TMDB_ID,
        "title": _TITLE,
        "selected_at": "2026-07-06T00:00:00Z",
    }


class PublicationAdapterTests(unittest.TestCase):
    def test_failure_is_isolated_and_other_targets_remain_ready(self) -> None:
        with TemporaryDirectory() as tmp:
            batch_root = Path(tmp) / "daily_batch"
            calls: list[str] = []

            def run_drafts(root: Path, date: str, slug: str, tmdb_id: int) -> Path:
                calls.append("drafts")
                output = root / date / f"{slug}_drafts_xiaohongshu.json"
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text("[]", encoding="utf-8")
                return output

            def download_poster(_: str, __: Path) -> PosterDownloadResult:
                calls.append("poster")
                raise TimeoutError("TMDB unavailable")

            def render_planet(tmdb_id: int, output: Path, *, bloom: bool) -> PlanetRenderResult:
                calls.append("planet")
                self.assertTrue(bloom)
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b"png")
                metadata = Path(f"{output}.render.json")
                metadata.write_text("{}", encoding="utf-8")
                return PlanetRenderResult(tmdb_id, output, metadata, 3, (0, 0, 1, 1), {"bloom": "on"})

            manifest = prepare_publication(
                batch_root,
                _selection(),
                run_drafts=run_drafts,
                download_poster=download_poster,
                render_planet_image=render_planet,
                load_candidate=lambda *_: {"poster_path": "/poster.jpg"},
            )

            self.assertCountEqual(calls, ["drafts", "poster", "planet"])
            self.assertEqual(manifest["status"], "partial")
            self.assertEqual(manifest["artifacts"]["drafts"]["status"], "ready")
            self.assertEqual(manifest["artifacts"]["planet"]["status"], "ready")
            self.assertEqual(manifest["artifacts"]["poster"]["status"], "failed")
            self.assertIn("TimeoutError", manifest["artifacts"]["poster"]["error"])

    def test_single_target_retry_preserves_ready_siblings(self) -> None:
        with TemporaryDirectory() as tmp:
            batch_root = Path(tmp) / "daily_batch"

            def run_drafts(root: Path, date: str, slug: str, tmdb_id: int) -> Path:
                output = root / date / f"{slug}_drafts_xiaohongshu.json"
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_text("[]", encoding="utf-8")
                return output

            def render_planet(tmdb_id: int, output: Path, *, bloom: bool) -> PlanetRenderResult:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b"png")
                metadata = Path(f"{output}.render.json")
                metadata.write_text("{}", encoding="utf-8")
                return PlanetRenderResult(tmdb_id, output, metadata, 3, (0, 0, 1, 1), {})

            def download_poster(_: str, output: Path) -> PosterDownloadResult:
                output.parent.mkdir(parents=True, exist_ok=True)
                output.write_bytes(b"jpg")
                return PosterDownloadResult("https://tmdb.example/poster.jpg", output, 3, "image/jpeg")

            kwargs = {
                "run_drafts": run_drafts,
                "download_poster": download_poster,
                "render_planet_image": render_planet,
                "load_candidate": lambda *_: {"poster_path": "/poster.jpg"},
            }
            prepare_publication(batch_root, _selection(), **kwargs)
            manifest = prepare_publication(batch_root, _selection(), targets=("poster",), **kwargs)

            self.assertEqual(manifest["status"], "ready")
            self.assertEqual(manifest["artifacts"]["drafts"]["status"], "ready")
            self.assertEqual(manifest["artifacts"]["planet"]["status"], "ready")
            self.assertEqual(manifest["artifacts"]["poster"]["source_url"], "https://tmdb.example/poster.jpg")


class PublicationRouteTests(unittest.TestCase):
    def test_prepare_submits_job_and_passes_only_adapter_arguments(self) -> None:
        with TemporaryDirectory() as tmp:
            batch_root = Path(tmp)
            write_selection(batch_root, _DATE, _selection())
            calls: list[list[str]] = []

            def run_subprocess(command, capture_output, text):  # noqa: ANN001
                calls.append(command)
                return SimpleNamespace(returncode=0, stdout="", stderr="prepared")

            job_store = _InlineJobStore()
            status, payload = route(
                "POST",
                "/api/prepare-publication",
                {},
                {"date": _DATE},
                batch_root=batch_root,
                publication_adapter_path=Path("publication_adapter.py"),
                run_subprocess=run_subprocess,
                job_store=job_store,
            )

            self.assertEqual(status, 202)
            self.assertEqual(payload["kind"], "prepare-publication")
            _, job = route(
                "GET", "/api/job", {"job_id": payload["job_id"]}, None, batch_root=batch_root, job_store=job_store
            )
            self.assertEqual(job["result"]["http_status"], 200)
            self.assertEqual(calls[0][-2:], ["--batch-root", str(batch_root)])
            self.assertIn("--date", calls[0])

    def test_asset_endpoint_only_serves_registered_asset_inside_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            batch_root = Path(tmp)
            write_selection(batch_root, _DATE, _selection())
            path = manifest_path(batch_root, _DATE, _TMDB_ID, _TITLE)
            manifest = new_manifest(_snapshot())
            for key in ("drafts", "poster", "planet"):
                manifest["artifacts"][key]["status"] = "ready"
            manifest["status"] = "ready"
            write_manifest(path, manifest)
            poster = path.parent / "assets" / "poster-original.jpg"
            poster.parent.mkdir(parents=True, exist_ok=True)
            poster.write_bytes(b"jpg")

            status, payload = route(
                "GET", "/api/publication-asset", {"date": _DATE, "asset": "poster"}, None, batch_root=batch_root
            )
            self.assertEqual(status, 200)
            self.assertIsInstance(payload, PublicationAssetResponse)
            self.assertEqual(payload.path, poster.resolve())
            self.assertEqual(payload.content_type, "image/jpeg")

            denied_status, denied_payload = route(
                "GET", "/api/publication-asset", {"date": _DATE, "asset": "../manifest.json"}, None, batch_root=batch_root
            )
            self.assertEqual(denied_status, 400)
            self.assertIn("unknown publication asset", denied_payload["error"])


if __name__ == "__main__":
    unittest.main()