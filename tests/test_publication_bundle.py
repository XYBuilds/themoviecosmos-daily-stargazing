"""Tests for the publication-bundle domain boundary."""

from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path
from tempfile import TemporaryDirectory

from review_panel.publication_bundle import (
    bundle_dir,
    bundle_id,
    derive_status,
    manifest_path,
    new_manifest,
    read_manifest,
    supersede_manifest,
    update_manifest,
    validate_manifest,
    write_manifest,
)


class BundleIdTests(unittest.TestCase):
    def test_slug_is_deterministic_ascii_and_windows_safe(self) -> None:
        self.assertEqual(bundle_id(670292, "The Creator: A Film?"), "670292-the-creator-a-film")
        self.assertEqual(bundle_id(670292, "<>:\\|?*"), "670292")
        self.assertEqual(bundle_id("670292", "Crème brûlée"), "670292-creme-brulee")

    def test_path_projection_stays_under_publications_workspace(self) -> None:
        root = Path("C:/work/output/daily_batch")
        expected = root.parent / "publications" / "2026-07-06" / "670292-the-creator"
        self.assertEqual(bundle_dir(root, "2026-07-06", 670292, "The Creator"), expected)
        self.assertEqual(manifest_path(root, "2026-07-06", 670292, "The Creator"), expected / "manifest.json")


class ManifestValidationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = new_manifest(
            {
                "date": "2026-07-06",
                "news_slug": "05-ai-poses-hiroshima-style-threat-to-humanity",
                "tmdb_id": 670292,
                "title": "The Creator",
                "selected_at": "2026-07-06T00:00:00Z",
            }
        )

    def test_new_manifest_only_uses_bundle_relative_paths(self) -> None:
        validated = validate_manifest(self.manifest)
        self.assertEqual(validated["publication_id"], "2026-07-06/670292-the-creator")
        self.assertEqual(validated["artifacts"]["poster"]["path"], "assets/poster-original.jpg")
        self.assertEqual(validated["artifacts"]["planet"]["metadata_path"], "assets/planet.png.render.json")

    def test_rejects_unknown_version_missing_fields_and_escape_path(self) -> None:
        unknown = deepcopy(self.manifest)
        unknown["schema_version"] = 2
        with self.assertRaisesRegex(ValueError, "schema_version"):
            validate_manifest(unknown)

        missing = deepcopy(self.manifest)
        del missing["selection"]["title"]
        with self.assertRaisesRegex(ValueError, "title"):
            validate_manifest(missing)

        escaped = deepcopy(self.manifest)
        escaped["artifacts"]["poster"]["path"] = "../secret.jpg"
        with self.assertRaisesRegex(ValueError, "escapes"):
            validate_manifest(escaped)

        absolute = deepcopy(self.manifest)
        absolute["artifacts"]["poster"]["path"] = "C:/secret.jpg"
        with self.assertRaisesRegex(ValueError, "escapes"):
            validate_manifest(absolute)


class StatusAggregationTests(unittest.TestCase):
    def _artifacts(self, status: str) -> dict[str, object]:
        return {
            "drafts": {"status": status},
            "poster": {"status": status},
            "planet": {"status": status},
            "copies": {"xiaohongshu": {"status": "pending"}},
        }

    def test_derives_preparing_partial_ready_and_superseded(self) -> None:
        self.assertEqual(derive_status(self._artifacts("running")), "preparing")
        partial = self._artifacts("ready")
        partial["poster"] = {"status": "failed"}
        self.assertEqual(derive_status(partial), "partial")
        self.assertEqual(derive_status(self._artifacts("ready")), "ready")
        self.assertEqual(derive_status(self._artifacts("failed"), superseded=True), "superseded")


class PersistenceTests(unittest.TestCase):
    def test_writes_reads_updates_and_supersedes_atomically(self) -> None:
        manifest = new_manifest(
            {
                "date": "2026-07-06",
                "news_slug": "05-ai",
                "tmdb_id": 670292,
                "title": "The Creator",
                "selected_at": "2026-07-06T00:00:00Z",
            }
        )
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "publication" / "manifest.json"
            write_manifest(path, manifest)
            parsed = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(parsed["schema_version"], 1)
            self.assertEqual(read_manifest(path)["publication_id"], manifest["publication_id"])

            def mark_prepared(current: dict[str, object]) -> dict[str, object]:
                artifacts = current["artifacts"]
                assert isinstance(artifacts, dict)
                for name in ("drafts", "poster", "planet"):
                    entry = artifacts[name]
                    assert isinstance(entry, dict)
                    entry["status"] = "ready"
                return current

            updated = update_manifest(path, mark_prepared)
            self.assertEqual(updated["status"], "ready")
            self.assertEqual(supersede_manifest(path)["status"], "superseded")
            self.assertEqual(read_manifest(path)["status"], "superseded")
            self.assertEqual(list(path.parent.glob(".manifest-*.json")), [])


class CopyArtifactTests(unittest.TestCase):
    def test_resolves_bundle_paths_and_preserves_pointer_when_editing(self) -> None:
        from review_panel.publication_bundle import copy_artifact_paths, update_copy_artifact

        selection = {
            "date": "2026-07-06",
            "news_slug": "05-ai",
            "tmdb_id": 670292,
            "title": "The Creator",
            "selected_at": "2026-07-06T00:00:00Z",
        }
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "manifest.json"
            write_manifest(path, new_manifest(selection))
            copy_path, humanized_path = copy_artifact_paths(read_manifest(path), path.parent, "xiaohongshu")
            self.assertEqual(copy_path, path.parent / "copy" / "xiaohongshu.md")
            self.assertEqual(humanized_path, path.parent / "copy" / "xiaohongshu-humanized.md")

            update_copy_artifact(path, "xiaohongshu", status="ready", selected_draft_id="The-Sage")
            update_copy_artifact(path, "xiaohongshu", status="ready")
            copy_artifact = read_manifest(path)["artifacts"]["copies"]["xiaohongshu"]
            self.assertEqual(copy_artifact["selected_draft_id"], "The-Sage")
