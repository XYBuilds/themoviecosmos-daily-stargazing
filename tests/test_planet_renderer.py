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

    def _write_valid_artifacts(self, output_path: Path, *, tmdb_id: int, bloom: str) -> Path:
        _write_rgba_png(output_path, width=2, height=2)
        metadata_path = Path(f"{output_path}.render.json")
        metadata_path.write_text(
            json.dumps(
                {
                    "tmdb_id": tmdb_id,
                    "resolution": 2,
                    "padding": PLANET_PADDING,
                    "bloom": bloom,
                }
            ),
            encoding="utf-8",
        )
        return metadata_path

    def test_render_builds_windows_safe_argument_array_and_verifies_artifacts(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
            output_path = tmp_path / "output with spaces" / "planet.png"
            output_path.parent.mkdir()
            metadata_path = self._write_valid_artifacts(output_path, tmdb_id=157336, bloom="on")
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
                patch.dict(os.environ, {"MOVIE_COSMOS_GALAXY_ROOT": str(root)}, clear=False),
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

    def test_local_data_file_override_is_forwarded_to_chronicle(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
            data_file = tmp_path / "galaxy.json.gz"
            data_file.write_bytes(b"fixture")
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
                patch.dict(
                    os.environ,
                    {
                        "MOVIE_COSMOS_GALAXY_ROOT": str(root),
                        "MOVIE_COSMOS_GALAXY_DATA_FILE": str(data_file),
                    },
                    clear=False,
                ),
                patch("scripts.lib.planet_renderer.PLANET_RESOLUTION", 2),
            ):
                render_planet(157336, output_path, bloom=False, runner=runner)

            command = runner.call_args.args[0]
            self.assertEqual(command[-6:], ("--bloom", "off", "--size-root", "3", "--data-file", str(data_file.resolve())))

    def test_missing_chronicle_root_is_a_clear_error(self) -> None:
        with patch.dict(os.environ, {"MOVIE_COSMOS_GALAXY_ROOT": ""}, clear=False):
            with self.assertRaisesRegex(PlanetRenderError, "MOVIE_COSMOS_GALAXY_ROOT"):
                render_planet(1, Path("planet.png"), bloom=False, runner=Mock())

    def test_cli_failure_includes_stderr(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
            runner = Mock(return_value=subprocess.CompletedProcess(args=[], returncode=9, stdout="", stderr="WebGL failed"))
            with patch.dict(os.environ, {"MOVIE_COSMOS_GALAXY_ROOT": str(root)}, clear=False):
                with self.assertRaisesRegex(PlanetRenderError, "WebGL failed"):
                    render_planet(1, tmp_path / "planet.png", bloom=False, runner=runner)

    def test_invalid_cli_json_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
            runner = Mock(return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout="not-json", stderr=""))
            with patch.dict(os.environ, {"MOVIE_COSMOS_GALAXY_ROOT": str(root)}, clear=False):
                with self.assertRaisesRegex(PlanetRenderError, "invalid JSON"):
                    render_planet(1, tmp_path / "planet.png", bloom=False, runner=runner)

    def test_missing_or_invalid_png_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
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
            with patch.dict(os.environ, {"MOVIE_COSMOS_GALAXY_ROOT": str(root)}, clear=False):
                with self.assertRaisesRegex(PlanetRenderError, "missing or unreadable"):
                    render_planet(1, output_path, bloom=False, runner=runner)

    def test_metadata_mismatch_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            root = self._create_chronicle_root(tmp_path)
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
                patch.dict(os.environ, {"MOVIE_COSMOS_GALAXY_ROOT": str(root)}, clear=False),
                patch("scripts.lib.planet_renderer.PLANET_RESOLUTION", 2),
            ):
                with self.assertRaisesRegex(PlanetRenderError, "metadata tmdb_id"):
                    render_planet(1, output_path, bloom=False, runner=runner)

    def test_fully_transparent_png_is_rejected(self) -> None:
        with TemporaryDirectory() as tmp:
            png_path = Path(tmp) / "empty.png"
            _write_rgba_png(png_path, width=2, height=2, visible=False)
            with self.assertRaisesRegex(PlanetRenderError, "fully transparent"):
                _validate_rgba_png(png_path, expected_resolution=2)


if __name__ == "__main__":
    unittest.main()