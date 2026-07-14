"""Chronicle planet-export CLI adapter.

This module owns the cross-repository process and artifact boundary only. Three.js,
WebGL, and visual parameters remain owned by Chronicle's ``planet:export`` CLI.
"""

from __future__ import annotations

import json
import os
import struct
import subprocess
import zlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
PLANET_RESOLUTION = 3000
PLANET_PADDING = 0.08


class PlanetRenderError(RuntimeError):
    """Raised when Chronicle cannot create a verified planet image artifact."""


@dataclass(frozen=True)
class PlanetRenderResult:
    tmdb_id: int
    output_path: Path
    metadata_path: Path
    file_size: int
    alpha_bounds: tuple[int, int, int, int]
    metadata: Mapping[str, Any]


def _resolve_chronicle_root() -> Path:
    configured_root = os.environ.get("MOVIE_COSMOS_GALAXY_ROOT", "").strip()
    if not configured_root:
        raise PlanetRenderError("MOVIE_COSMOS_GALAXY_ROOT is required to render a planet image")

    root = Path(configured_root).expanduser().resolve()
    package_path = root / "package.json"
    if not root.is_dir() or not package_path.is_file():
        raise PlanetRenderError(
            f"MOVIE_COSMOS_GALAXY_ROOT must point to a Chronicle repository with package.json: {root}"
        )

    try:
        package = json.loads(package_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PlanetRenderError(f"unable to read Chronicle package.json: {exc}") from exc

    scripts = package.get("scripts")
    if not isinstance(scripts, dict) or "planet:export" not in scripts:
        raise PlanetRenderError(f"Chronicle package.json has no planet:export script: {package_path}")
    return root


def _resolve_data_file_override() -> Path | None:
    configured_file = os.environ.get("MOVIE_COSMOS_GALAXY_DATA_FILE", "").strip()
    if not configured_file:
        return None

    data_file = Path(configured_file).expanduser().resolve()
    if not data_file.is_file():
        raise PlanetRenderError(f"MOVIE_COSMOS_GALAXY_DATA_FILE must point to an existing galaxy JSON file: {data_file}")
    return data_file


def _parse_cli_result(stdout: str, *, tmdb_id: int, output_path: Path) -> Path:
    try:
        payload = json.loads(stdout.strip())
    except json.JSONDecodeError as exc:
        raise PlanetRenderError(f"Chronicle CLI returned invalid JSON on stdout: {exc}") from exc

    if not isinstance(payload, dict):
        raise PlanetRenderError("Chronicle CLI stdout must be a JSON object")
    if payload.get("tmdb_id") != tmdb_id:
        raise PlanetRenderError(f"Chronicle CLI returned tmdb_id={payload.get('tmdb_id')!r}, expected {tmdb_id}")

    exported_path = Path(str(payload.get("output", ""))).resolve()
    if exported_path != output_path:
        raise PlanetRenderError(f"Chronicle CLI returned unexpected PNG path: {exported_path}")

    metadata_path = Path(str(payload.get("metadata", ""))).resolve()
    expected_metadata_path = Path(f"{output_path}.render.json")
    if metadata_path != expected_metadata_path:
        raise PlanetRenderError(f"Chronicle CLI returned unexpected metadata path: {metadata_path}")
    return metadata_path


def _paeth(left: int, above: int, upper_left: int) -> int:
    predictor = left + above - upper_left
    left_distance = abs(predictor - left)
    above_distance = abs(predictor - above)
    upper_left_distance = abs(predictor - upper_left)
    if left_distance <= above_distance and left_distance <= upper_left_distance:
        return left
    if above_distance <= upper_left_distance:
        return above
    return upper_left


def _validate_rgba_png(png_path: Path, *, expected_resolution: int) -> tuple[int, int, int, int]:
    try:
        payload = png_path.read_bytes()
    except OSError as exc:
        raise PlanetRenderError(f"planet PNG is missing or unreadable: {png_path}") from exc

    if not payload.startswith(PNG_SIGNATURE):
        raise PlanetRenderError(f"planet PNG has an invalid signature: {png_path}")

    offset = len(PNG_SIGNATURE)
    ihdr: tuple[int, int, int, int, int, int, int] | None = None
    idat_parts: list[bytes] = []
    while offset < len(payload):
        if offset + 12 > len(payload):
            raise PlanetRenderError("planet PNG has a truncated chunk")
        length = struct.unpack(">I", payload[offset : offset + 4])[0]
        chunk_type = payload[offset + 4 : offset + 8]
        chunk_end = offset + 12 + length
        if chunk_end > len(payload):
            raise PlanetRenderError("planet PNG declares a chunk beyond the file boundary")
        chunk_data = payload[offset + 8 : offset + 8 + length]
        if chunk_type == b"IHDR":
            if length != 13 or ihdr is not None:
                raise PlanetRenderError("planet PNG has an invalid IHDR chunk")
            ihdr = struct.unpack(">IIBBBBB", chunk_data)
        elif chunk_type == b"IDAT":
            idat_parts.append(chunk_data)
        elif chunk_type == b"IEND":
            break
        offset = chunk_end

    if ihdr is None or not idat_parts:
        raise PlanetRenderError("planet PNG is missing IHDR or image data")
    width, height, bit_depth, color_type, compression, filter_method, interlace = ihdr
    if (width, height) != (expected_resolution, expected_resolution):
        raise PlanetRenderError(
            f"planet PNG dimensions must be {expected_resolution}×{expected_resolution}, got {width}×{height}"
        )
    if (bit_depth, color_type, compression, filter_method, interlace) != (8, 6, 0, 0, 0):
        raise PlanetRenderError("planet PNG must be non-interlaced 8-bit RGBA")

    try:
        scanlines = zlib.decompress(b"".join(idat_parts))
    except zlib.error as exc:
        raise PlanetRenderError(f"planet PNG image data cannot be decompressed: {exc}") from exc

    stride = width * 4
    expected_bytes = height * (stride + 1)
    if len(scanlines) != expected_bytes:
        raise PlanetRenderError("planet PNG image data has an unexpected RGBA scanline length")

    visible_left = width
    visible_top = height
    visible_right = -1
    visible_bottom = -1
    previous = bytearray(stride)
    cursor = 0
    for y in range(height):
        filter_type = scanlines[cursor]
        cursor += 1
        encoded = scanlines[cursor : cursor + stride]
        cursor += stride
        row = bytearray(stride)
        for index, value in enumerate(encoded):
            left = row[index - 4] if index >= 4 else 0
            above = previous[index]
            upper_left = previous[index - 4] if index >= 4 else 0
            if filter_type == 0:
                row[index] = value
            elif filter_type == 1:
                row[index] = (value + left) & 0xFF
            elif filter_type == 2:
                row[index] = (value + above) & 0xFF
            elif filter_type == 3:
                row[index] = (value + ((left + above) // 2)) & 0xFF
            elif filter_type == 4:
                row[index] = (value + _paeth(left, above, upper_left)) & 0xFF
            else:
                raise PlanetRenderError(f"planet PNG uses unsupported filter type {filter_type}")

        for x in range(width):
            if row[x * 4 + 3] > 0:
                visible_left = min(visible_left, x)
                visible_top = min(visible_top, y)
                visible_right = max(visible_right, x)
                visible_bottom = max(visible_bottom, y)
        previous = row

    if visible_right < 0:
        raise PlanetRenderError("planet PNG is fully transparent")
    return visible_left, visible_top, visible_right, visible_bottom


def _read_metadata(metadata_path: Path, *, tmdb_id: int, bloom: bool) -> Mapping[str, Any]:
    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PlanetRenderError(f"planet render metadata is missing or invalid: {metadata_path}") from exc

    if not isinstance(metadata, dict):
        raise PlanetRenderError("planet render metadata must be a JSON object")
    expected_bloom = "on" if bloom else "off"
    if metadata.get("tmdb_id") != tmdb_id:
        raise PlanetRenderError(f"metadata tmdb_id={metadata.get('tmdb_id')!r}, expected {tmdb_id}")
    if metadata.get("resolution") != PLANET_RESOLUTION:
        raise PlanetRenderError(f"metadata resolution={metadata.get('resolution')!r}, expected {PLANET_RESOLUTION}")
    if metadata.get("padding") != PLANET_PADDING:
        raise PlanetRenderError(f"metadata padding={metadata.get('padding')!r}, expected {PLANET_PADDING}")
    if metadata.get("bloom") != expected_bloom:
        raise PlanetRenderError(f"metadata bloom={metadata.get('bloom')!r}, expected {expected_bloom!r}")
    return metadata


def render_planet(
    tmdb_id: int,
    output_path: Path,
    *,
    bloom: bool,
    runner: Any = subprocess.run,
) -> PlanetRenderResult:
    """Render one verified 3000×3000 RGBA planet PNG through Chronicle's CLI."""
    if tmdb_id <= 0:
        raise PlanetRenderError(f"tmdb_id must be a positive integer, got {tmdb_id}")

    root = _resolve_chronicle_root()
    data_file = _resolve_data_file_override()
    resolved_output = output_path.expanduser().resolve()
    resolved_output.parent.mkdir(parents=True, exist_ok=True)
    bloom_value = "on" if bloom else "off"
    npm_executable = "npm.cmd" if os.name == "nt" else "npm"
    command: Sequence[str] = (
        npm_executable,
        "--silent",
        "run",
        "planet:export",
        "--",
        "--movie-id",
        str(tmdb_id),
        "--output",
        str(resolved_output),
        "--resolution",
        str(PLANET_RESOLUTION),
        "--padding",
        str(PLANET_PADDING),
        "--bloom",
        bloom_value,
        "--size-root",
        "3",
    )
    if data_file is not None:
        command = (*command, "--data-file", str(data_file))
    print(f"[planet_renderer] tmdb_id={tmdb_id} bloom={bloom_value} output={resolved_output}")

    try:
        completed = runner(command, cwd=root, capture_output=True, text=True, check=False)
    except OSError as exc:
        raise PlanetRenderError(f"failed to start Chronicle CLI: {exc}") from exc

    if completed.returncode != 0:
        detail = completed.stderr.strip() or completed.stdout.strip() or "no CLI diagnostic"
        raise PlanetRenderError(f"Chronicle CLI failed with exit code {completed.returncode}: {detail}")

    metadata_path = _parse_cli_result(completed.stdout, tmdb_id=tmdb_id, output_path=resolved_output)
    alpha_bounds = _validate_rgba_png(resolved_output, expected_resolution=PLANET_RESOLUTION)
    metadata = _read_metadata(metadata_path, tmdb_id=tmdb_id, bloom=bloom)
    file_size = resolved_output.stat().st_size
    print(
        f"[planet_renderer] complete tmdb_id={tmdb_id} bytes={file_size} "
        f"alpha_bounds={alpha_bounds} metadata={metadata_path}"
    )
    return PlanetRenderResult(
        tmdb_id=tmdb_id,
        output_path=resolved_output,
        metadata_path=metadata_path,
        file_size=file_size,
        alpha_bounds=alpha_bounds,
        metadata=metadata,
    )