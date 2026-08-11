"""Tests for publication-bundle visual asset operations."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock, patch

from review_panel.publication_assets import prepare_publication_assets, publication_asset_paths
from scripts.lib.planet_renderer import PlanetRenderResult
from scripts.lib.poster_downloader import PosterDownloadResult


class PublicationAssetTests(unittest.TestCase):
    def test_asset_paths_are_projected_under_the_bundle(self) -> None:
        with TemporaryDirectory() as tmp:
            poster_path, planet_path = publication_asset_paths(
                Path(tmp) / "daily_batch",
                date="2026-07-06",
                tmdb_id=670292,
                title="The Creator",
            )

            self.assertEqual(
                poster_path,
                Path(tmp) / "publications" / "2026-07-06" / "670292-the-creator" / "assets" / "poster-original.jpg",
            )
            self.assertEqual(planet_path.name, "planet.png")

    def test_prepare_creates_one_poster_and_one_bloom_on_planet(self) -> None:
        with TemporaryDirectory() as tmp:
            batch_root = Path(tmp) / "daily_batch"
            poster_result = PosterDownloadResult(
                source_url="https://image.tmdb.org/t/p/original/poster.jpg",
                output_path=Path(tmp) / "poster-original.jpg",
                file_size=5,
                content_type="image/jpeg",
            )
            planet_result = PlanetRenderResult(
                tmdb_id=670292,
                output_path=Path(tmp) / "planet.png",
                metadata_path=Path(tmp) / "planet.png.render.json",
                file_size=9,
                alpha_bounds=(1, 1, 2, 2),
                metadata={"bloom": "on", "data_version": "fixture-v1"},
                observed_roster_count=1,
                roster_data_version="fixture-v1",
            )
            download = Mock(return_value=poster_result)
            render = Mock(return_value=planet_result)

            with (
                patch("review_panel.publication_assets.download_tmdb_poster", download),
                patch("review_panel.publication_assets.render_planet", render),
            ):
                result = prepare_publication_assets(
                    batch_root,
                    date="2026-07-06",
                    tmdb_id=670292,
                    title="The Creator",
                    poster_path="/poster.jpg",
                )

            expected_assets = batch_root.parent / "publications" / "2026-07-06" / "670292-the-creator" / "assets"
            download.assert_called_once_with("/poster.jpg", expected_assets / "poster-original.jpg")
            render.assert_called_once_with(670292, expected_assets / "planet.png", bloom=True)
            self.assertIs(result.poster, poster_result)
            self.assertIs(result.planet, planet_result)


if __name__ == "__main__":
    unittest.main()