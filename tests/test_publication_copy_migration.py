"""Regression tests for Phase 13.4 publication-copy migration."""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from review_panel.publication_bundle import manifest_path, new_manifest, read_manifest, write_manifest
from review_panel.serve import read_selection, route


class PublicationCopyMigrationTests(unittest.TestCase):
    date = "2026-07-06"
    slug = "05-ai"
    tmdb_id = 670292
    title = "The Creator"

    def _write_batch(self, root: Path) -> None:
        news_dir = root / self.date / self.slug
        news_dir.mkdir(parents=True)
        (news_dir / "news.json").write_text(
            json.dumps({"url": "https://example.test/news"}), encoding="utf-8"
        )
        (news_dir / "retrieve.json").write_text(
            json.dumps(
                {"candidates": [{"tmdb_id": self.tmdb_id, "movie_url": "https://example.test/movie"}]}
            ),
            encoding="utf-8",
        )
        (root / self.date / f"{self.slug}_drafts_xiaohongshu.json").write_text(
            json.dumps([{"draft_id": "The-Sage", "headline": "标题", "body": "第一版正文"}]),
            encoding="utf-8",
        )

    def _select_and_prepare_manifest(self, root: Path) -> Path:
        status, _ = route(
            "POST",
            "/api/select",
            {},
            {"date": self.date, "news_slug": self.slug, "tmdb_id": self.tmdb_id, "title": self.title},
            batch_root=root,
        )
        self.assertEqual(status, 200)
        selection = read_selection(root, self.date)
        assert selection is not None
        path = manifest_path(root, self.date, self.tmdb_id, self.title)
        write_manifest(
            path,
            new_manifest(
                {
                    "date": self.date,
                    "news_slug": self.slug,
                    "tmdb_id": self.tmdb_id,
                    "title": self.title,
                    "selected_at": selection["selected_at"],
                }
            ),
        )
        return path

    def test_new_selection_is_slim_and_same_selection_is_idempotent(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_batch(root)
            self._select_and_prepare_manifest(root)
            first = read_selection(root, self.date)
            assert first is not None
            status, payload = route(
                "POST",
                "/api/select",
                {},
                {"date": self.date, "news_slug": self.slug, "tmdb_id": self.tmdb_id, "title": self.title},
                batch_root=root,
            )
            self.assertEqual(status, 200)
            self.assertEqual(payload["selection"], first)
            self.assertEqual(set(first), {"date", "selected", "selected_at"})

    def test_selected_draft_and_body_edit_stay_inside_bundle(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_batch(root)
            manifest_file = self._select_and_prepare_manifest(root)

            status, payload = route(
                "POST", "/api/select-draft", {}, {"date": self.date, "draft_id": "The-Sage"}, batch_root=root
            )
            self.assertEqual(status, 200)
            copy_path = manifest_file.parent / "copy" / "xiaohongshu.md"
            self.assertTrue(copy_path.is_file())
            self.assertFalse((root / self.date / f"{self.slug}_copy_xiaohongshu.md").exists())
            self.assertEqual(
                read_manifest(manifest_file)["artifacts"]["copies"]["xiaohongshu"]["selected_draft_id"],
                "The-Sage",
            )

            status, payload = route(
                "POST", "/api/edit-body", {}, {"date": self.date, "body": "人工改写后的正文"}, batch_root=root
            )
            self.assertEqual(status, 200)
            self.assertIn("人工改写后的正文", copy_path.read_text(encoding="utf-8"))

    def test_changed_selection_supersedes_existing_bundle_without_deleting_it(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            self._write_batch(root)
            manifest_file = self._select_and_prepare_manifest(root)
            (manifest_file.parent / "copy").mkdir(parents=True)
            copy_path = manifest_file.parent / "copy" / "xiaohongshu.md"
            copy_path.write_text("审计保留", encoding="utf-8")

            status, _ = route(
                "POST",
                "/api/select",
                {},
                {"date": self.date, "news_slug": "06-other", "tmdb_id": 1, "title": "Other"},
                batch_root=root,
            )
            self.assertEqual(status, 200)
            self.assertEqual(read_manifest(manifest_file)["status"], "superseded")
            self.assertEqual(copy_path.read_text(encoding="utf-8"), "审计保留")


if __name__ == "__main__":
    unittest.main()