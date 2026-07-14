"""Visual-asset operations bound to one publication bundle."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from review_panel.publication_bundle import bundle_dir
from scripts.lib.planet_renderer import PlanetRenderResult, render_planet
from scripts.lib.poster_downloader import PosterDownloadResult, download_tmdb_poster


@dataclass(frozen=True)
class PublicationAssetResult:
    poster: PosterDownloadResult
    planet: PlanetRenderResult


def publication_asset_paths(
    batch_root: Path,
    *,
    date: str,
    tmdb_id: int,
    title: str,
) -> tuple[Path, Path]:
    """Return the canonical poster and single Bloom ON planet paths for a bundle."""
    assets_dir = bundle_dir(batch_root, date, tmdb_id, title) / "assets"
    return assets_dir / "poster-original.jpg", assets_dir / "planet.png"


def prepare_publication_assets(
    batch_root: Path,
    *,
    date: str,
    tmdb_id: int,
    title: str,
    poster_path: str,
) -> PublicationAssetResult:
    """Create one verified poster and one Bloom ON planet image for a selection."""
    poster_output, planet_output = publication_asset_paths(
        batch_root,
        date=date,
        tmdb_id=tmdb_id,
        title=title,
    )
    poster = download_tmdb_poster(poster_path, poster_output)
    planet = render_planet(tmdb_id, planet_output, bloom=True)
    return PublicationAssetResult(poster=poster, planet=planet)