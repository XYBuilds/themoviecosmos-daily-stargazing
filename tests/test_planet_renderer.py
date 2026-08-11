"""Tests for the Chronicle planet-export subprocess adapter."""

from __future__ import annotations

import json
import os
import struct
import subprocess
import unittest
import zlib
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import Mock, patch

from scripts.lib.planet_renderer import (
    PLANET_PADDING,
    PlanetRenderError,
    _validate_rgba_png,
    render_planet,
)


def _png_chunk(chunk_type: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + chunk_type + payload + struct.pack(">I", zlib.crc32(chunk_type + payload))


def _write_rgba_png(path: Path, *, width: int, height: int, visible: bool = True) -> None:
    rows = []
    for y in range(height):
        row = bytearray()
        for x in range(width):
            alpha = 255 if visible and (x, y) == (width // 2, height // 2) else 0
            row.extend((40, 80, 120, alpha))
        rows.append(b"\x00" + bytes(row))
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + _png_chunk(b"IHDR", ihdr)
        + _png_chunk(b"IDAT", zlib.compress(b"".join(rows)))
        + _png_chunk(b"IEND", b"")
    )


class PlanetRendererTests(unittest.TestCase):
    def _create_chronicle_root(self, base: Path) -> Path:
        root = base / "chronicle project"
        root.mkdir()
        (root / "package.json").write_text(
            json.dumps({"scripts": {"planet:export": "tsx tools/planet-exporter/src/cli.ts"}}),
            encoding="utf-8",
        )
        return root

    def _write_valid_artifacts(
        self,
        output_path: Path,
        *,
        tmdb_id: int,
        bloom: str,
        provenance: dict | None = None,
    ) -> Path:
        _write_rgba_png(output_path, width=2, height=2)
        metadata_path = Path(f"{output_path}.render.json")
        payload = {
            "tmdb_id": tmdb_id,
            "resolution": 2,
            "padding": PLANET_PADDING,
            "bloom": bloom,
            "data_version": "fixture-v1",
            "manifest_url": None,
            "requested_focus_emission_profile": {"profile_id": "fixture-profile"},
            "focus_emission_profile": {"profile_id": "fixture-profile"},
            "chronicle_git_commit": "abc123",
        }
        if provenance:
            payload.update(provenance)
        metadata_path.write_text(json.dumps(payload), encoding="utf-8")
        return metadata_path

    def _offline_env(self, root: Path, data_file: Path) -> dict[str, str]:
        return {
            "MOVIE_COSMOS_GALAXY_ROOT": str(root),
            "MOVIE_COSMOS_GALAXY_DATA_FILE": str(data_file),
            "MOVIE_COSMOS_GALAXY_MANIFEST_URL": "",
        }

    def _write_galaxy_fixture(self, path: Path, *, movie_ids: list[int], data_version: str = "fixture-v1") -> Path:
        path.write_text(
            json.dumps(
                {
                    "meta": {"version": data_version, "count": len(movie_ids)},
                    "movies": [{"id": movie_id} for movie_id in movie_ids],
                }
            ),
            encoding="utf-8",
        )
        return path

    def test_render_builds_windows_safe_argument_array_and_verifies_artifacts(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
            data_file = self._write_galaxy_fixture(tmp_path / "galaxy.json", movie_ids=[157336])
            output_path = tmp_path / "output with spaces" / "planet.png"
            output_path.parent.mkdir()
            metadata_path = self._write_valid_artifacts(output_path, tmdb_id=157336, bloom="on")
            runner = Mock(
                return_value=subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout="[GalaxyData] loaded movies\n"
                    + json.dumps(
                        {"output": str(output_path), "metadata": str(metadata_path), "tmdb_id": 157336}
                    ),
                    stderr="",
                )
            )

            with (
                patch.dict(os.environ, self._offline_env(root, data_file), clear=False),
                patch("scripts.lib.planet_renderer.PLANET_RESOLUTION", 2),
            ):
                result = render_planet(157336, output_path, bloom=True, runner=runner)

            command = runner.call_args.args[0]
            expected_npm = "npm.cmd" if os.name == "nt" else "npm"
            self.assertEqual(command[0:5], (expected_npm, "--silent", "run", "planet:export", "--"))
            self.assertIn(str(output_path.resolve()), command)
            self.assertEqual(runner.call_args.kwargs["cwd"], root.resolve())
            self.assertEqual(result.alpha_bounds, (1, 1, 1, 1))
            self.assertEqual(result.metadata_path, metadata_path.resolve())
            self.assertEqual(result.observed_roster_count, 1)
            self.assertEqual(result.metadata["data_version"], "fixture-v1")

    def test_manifest_url_is_forwarded_to_chronicle(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
            output_path = tmp_path / "planet.png"
            manifest_url = "https://example.test/data/galaxy_assets_manifest.json"
            metadata_path = self._write_valid_artifacts(
                output_path,
                tmdb_id=157336,
                bloom="on",
                provenance={
                    "data_version": "nightly-2026-08-11",
                    "manifest_url": manifest_url,
                    "profile_url": "https://example.test/galaxy/focus-emission-profiles/rating-emission-2026-07.json",
                    "requested_focus_emission_profile": {"profile_id": "rating-emission-2026-07"},
                    "focus_emission_profile": {"profile_id": "rating-emission-2026-07"},
                },
            )
            runner = Mock(
                return_value=subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout=json.dumps(
                        {"output": str(output_path), "metadata": str(metadata_path), "tmdb_id": 157336}
                    ),
                    stderr="",
                )
            )
            roster = Mock(
                return_value=SimpleNamespace(
                    data_version="nightly-2026-08-11",
                    observed_count=2,
                    allowed_ids=frozenset({157336, 2}),
                )
            )

            with (
                patch.dict(
                    os.environ,
                    {
                        "MOVIE_COSMOS_GALAXY_ROOT": str(root),
                        "MOVIE_COSMOS_GALAXY_MANIFEST_URL": manifest_url,
                        "MOVIE_COSMOS_GALAXY_DATA_FILE": "",
                    },
                    clear=False,
                ),
                patch("scripts.lib.planet_renderer.PLANET_RESOLUTION", 2),
                patch("scripts.lib.planet_renderer.load_galaxy_roster", roster),
            ):
                result = render_planet(157336, output_path, bloom=True, runner=runner)

            command = runner.call_args.args[0]
            self.assertIn("--manifest-url", command)
            self.assertIn(manifest_url, command)
            self.assertNotIn("--data-file", command)
            self.assertEqual(result.observed_roster_count, 2)
            self.assertEqual(result.metadata["manifest_url"], manifest_url)

    def test_local_data_file_override_is_forwarded_to_chronicle(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
            data_file = self._write_galaxy_fixture(tmp_path / "galaxy.json", movie_ids=[157336])
            output_path = tmp_path / "planet.png"
            metadata_path = self._write_valid_artifacts(output_path, tmdb_id=157336, bloom="off")
            runner = Mock(
                return_value=subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout=json.dumps(
                        {"output": str(output_path), "metadata": str(metadata_path), "tmdb_id": 157336}
                    ),
                    stderr="",
                )
            )

            with (
                patch.dict(os.environ, self._offline_env(root, data_file), clear=False),
                patch("scripts.lib.planet_renderer.PLANET_RESOLUTION", 2),
            ):
                render_planet(157336, output_path, bloom=False, runner=runner)

            command = runner.call_args.args[0]
            self.assertEqual(
                command[-6:],
                ("--bloom", "off", "--size-root", "3", "--data-file", str(data_file.resolve())),
            )

    def test_release_input_requires_exactly_one_of_manifest_or_data_file(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
            data_file = self._write_galaxy_fixture(tmp_path / "galaxy.json", movie_ids=[1])
            runner = Mock()

            with patch.dict(
                os.environ,
                {
                    "MOVIE_COSMOS_GALAXY_ROOT": str(root),
                    "MOVIE_COSMOS_GALAXY_MANIFEST_URL": "",
                    "MOVIE_COSMOS_GALAXY_DATA_FILE": "",
                },
                clear=False,
            ):
                with self.assertRaisesRegex(PlanetRenderError, "manifest-url|--data-file|release input"):
                    render_planet(1, tmp_path / "planet.png", bloom=False, runner=runner)

            with patch.dict(
                os.environ,
                {
                    "MOVIE_COSMOS_GALAXY_ROOT": str(root),
                    "MOVIE_COSMOS_GALAXY_MANIFEST_URL": "https://example.test/data/galaxy_assets_manifest.json",
                    "MOVIE_COSMOS_GALAXY_DATA_FILE": str(data_file),
                },
                clear=False,
            ):
                with self.assertRaisesRegex(PlanetRenderError, "exactly one|manifest-url|--data-file"):
                    render_planet(1, tmp_path / "planet.png", bloom=False, runner=runner)

            runner.assert_not_called()

    def test_movie_absent_from_roster_fails_before_cli(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
            data_file = self._write_galaxy_fixture(tmp_path / "galaxy.json", movie_ids=[999])
            runner = Mock()
            with patch.dict(os.environ, self._offline_env(root, data_file), clear=False):
                with self.assertRaisesRegex(PlanetRenderError, "not in Chronicle Galaxy Roster"):
                    render_planet(1, tmp_path / "planet.png", bloom=False, runner=runner)
            runner.assert_not_called()

    def test_missing_chronicle_root_is_a_clear_error(self) -> None:
        with patch.dict(
            os.environ,
            {
                "MOVIE_COSMOS_GALAXY_ROOT": "",
                "MOVIE_COSMOS_GALAXY_DATA_FILE": "",
                "MOVIE_COSMOS_GALAXY_MANIFEST_URL": "https://example.test/data/galaxy_assets_manifest.json",
            },
            clear=False,
        ):
            with self.assertRaisesRegex(PlanetRenderError, "MOVIE_COSMOS_GALAXY_ROOT"):
                render_planet(1, Path("planet.png"), bloom=False, runner=Mock())

    def test_cli_failure_includes_stderr(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
            data_file = self._write_galaxy_fixture(tmp_path / "galaxy.json", movie_ids=[1])
            runner = Mock(return_value=subprocess.CompletedProcess(args=[], returncode=9, stdout="", stderr="WebGL failed"))
            with patch.dict(os.environ, self._offline_env(root, data_file), clear=False):
                with self.assertRaisesRegex(PlanetRenderError, "WebGL failed"):
                    render_planet(1, tmp_path / "planet.png", bloom=False, runner=runner)

    def test_invalid_cli_json_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
            data_file = self._write_galaxy_fixture(tmp_path / "galaxy.json", movie_ids=[1])
            runner = Mock(return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout="not-json", stderr=""))
            with patch.dict(os.environ, self._offline_env(root, data_file), clear=False):
                with self.assertRaisesRegex(PlanetRenderError, "invalid JSON"):
                    render_planet(1, tmp_path / "planet.png", bloom=False, runner=runner)

    def test_missing_or_invalid_png_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
            data_file = self._write_galaxy_fixture(tmp_path / "galaxy.json", movie_ids=[1])
            output_path = tmp_path / "planet.png"
            metadata_path = Path(f"{output_path}.render.json")
            runner = Mock(
                return_value=subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout=json.dumps({"output": str(output_path), "metadata": str(metadata_path), "tmdb_id": 1}),
                    stderr="",
                )
            )
            with patch.dict(os.environ, self._offline_env(root, data_file), clear=False):
                with self.assertRaisesRegex(PlanetRenderError, "missing or unreadable"):
                    render_planet(1, output_path, bloom=False, runner=runner)

    def test_metadata_mismatch_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
            data_file = self._write_galaxy_fixture(tmp_path / "galaxy.json", movie_ids=[1])
            output_path = tmp_path / "planet.png"
            metadata_path = self._write_valid_artifacts(output_path, tmdb_id=2, bloom="off")
            runner = Mock(
                return_value=subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout=json.dumps({"output": str(output_path), "metadata": str(metadata_path), "tmdb_id": 1}),
                    stderr="",
                )
            )
            with (
                patch.dict(os.environ, self._offline_env(root, data_file), clear=False),
                patch("scripts.lib.planet_renderer.PLANET_RESOLUTION", 2),
            ):
                with self.assertRaisesRegex(PlanetRenderError, "metadata tmdb_id"):
                    render_planet(1, output_path, bloom=False, runner=runner)

    def test_production_provenance_mismatch_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
            output_path = tmp_path / "planet.png"
            manifest_url = "https://example.test/data/galaxy_assets_manifest.json"
            metadata_path = self._write_valid_artifacts(
                output_path,
                tmdb_id=1,
                bloom="off",
                provenance={"manifest_url": "https://other.test/manifest.json", "data_version": "v1"},
            )
            runner = Mock(
                return_value=subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout=json.dumps({"output": str(output_path), "metadata": str(metadata_path), "tmdb_id": 1}),
                    stderr="",
                )
            )
            with (
                patch.dict(
                    os.environ,
                    {
                        "MOVIE_COSMOS_GALAXY_ROOT": str(root),
                        "MOVIE_COSMOS_GALAXY_MANIFEST_URL": manifest_url,
                        "MOVIE_COSMOS_GALAXY_DATA_FILE": "",
                    },
                    clear=False,
                ),
                patch("scripts.lib.planet_renderer.PLANET_RESOLUTION", 2),
                patch(
                    "scripts.lib.planet_renderer.load_galaxy_roster",
                    Mock(
                        return_value=SimpleNamespace(
                            data_version="v1",
                            observed_count=1,
                            allowed_ids=frozenset({1}),
                        )
                    ),
                ),
            ):
                with self.assertRaisesRegex(PlanetRenderError, "manifest_url"):
                    render_planet(1, output_path, bloom=False, runner=runner)

    def test_fully_transparent_png_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            png_path = Path(tmp) / "empty.png"
            _write_rgba_png(png_path, width=2, height=2, visible=False)
            with self.assertRaisesRegex(PlanetRenderError, "fully transparent"):
                _validate_rgba_png(png_path, expected_resolution=2)


if __name__ == "__main__":
    unittest.main()