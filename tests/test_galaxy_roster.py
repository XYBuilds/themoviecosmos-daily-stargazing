"""Tests for Chronicle Galaxy Roster membership loading."""

from __future__ import annotations

import gzip
import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from scripts.lib.galaxy_roster import (
    GalaxyRosterError,
    assert_in_galaxy_roster,
    load_galaxy_roster,
    resolve_chronicle_release_input,
)


class GalaxyRosterTests(unittest.TestCase):
    def test_offline_data_file_loads_allowed_ids_and_version(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "galaxy.json"
            path.write_text(
                json.dumps(
                    {
                        "meta": {"version": "fixture-v1", "count": 2},
                        "movies": [{"id": 10}, {"id": 20}],
                    }
                ),
                encoding="utf-8",
            )
            with patch.dict(
                os.environ,
                {
                    "MOVIE_COSMOS_GALAXY_DATA_FILE": str(path),
                    "MOVIE_COSMOS_GALAXY_MANIFEST_URL": "",
                },
                clear=False,
            ):
                roster = load_galaxy_roster()

            self.assertEqual(roster.data_version, "fixture-v1")
            self.assertEqual(roster.observed_count, 2)
            self.assertEqual(roster.allowed_ids, frozenset({10, 20}))
            assert_in_galaxy_roster(10, roster)
            with self.assertRaisesRegex(GalaxyRosterError, "not in Chronicle Galaxy Roster"):
                assert_in_galaxy_roster(99, roster)

    def test_gzip_data_file_is_accepted(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "galaxy.json.gz"
            payload = json.dumps(
                {"meta": {"version": "gz-v1", "count": 1}, "movies": [{"id": 7}]}
            ).encode("utf-8")
            path.write_bytes(gzip.compress(payload))
            with patch.dict(
                os.environ,
                {
                    "MOVIE_COSMOS_GALAXY_DATA_FILE": str(path),
                    "MOVIE_COSMOS_GALAXY_MANIFEST_URL": "",
                },
                clear=False,
            ):
                roster = load_galaxy_roster()
            self.assertEqual(roster.allowed_ids, frozenset({7}))

    def test_manifest_url_loads_galaxy_from_manifest_pointer(self) -> None:
        manifest_url = "https://example.test/data/galaxy_assets_manifest.json"
        galaxy_url = "https://example.test/data/galaxy_data.json.gz"
        fetches: list[str] = []

        def fetch_bytes(url: str) -> bytes:
            fetches.append(url)
            if url == manifest_url:
                return json.dumps(
                    {
                        "galaxy_data_gzip_url": galaxy_url,
                        "data_version": "nightly-v1",
                        "focus_emission_profile": {"status": "active", "profile_id": "p1"},
                        "focus_emission_profile_url": (
                            "https://example.test/galaxy/focus-emission-profiles/p1.json"
                        ),
                    }
                ).encode("utf-8")
            if url == galaxy_url:
                return json.dumps(
                    {
                        "meta": {"version": "nightly-v1", "count": 2},
                        "movies": [{"id": 1}, {"id": 2}],
                    }
                ).encode("utf-8")
            raise AssertionError(f"unexpected url {url}")

        with patch.dict(
            os.environ,
            {
                "MOVIE_COSMOS_GALAXY_MANIFEST_URL": manifest_url,
                "MOVIE_COSMOS_GALAXY_DATA_FILE": "",
            },
            clear=False,
        ):
            roster = load_galaxy_roster(fetch_bytes=fetch_bytes)

        self.assertEqual(fetches, [manifest_url, galaxy_url])
        self.assertEqual(roster.data_version, "nightly-v1")
        self.assertEqual(roster.observed_count, 2)
        self.assertEqual(roster.source_label, manifest_url)

    def test_release_input_is_exclusive(self) -> None:
        with patch.dict(
            os.environ,
            {
                "MOVIE_COSMOS_GALAXY_MANIFEST_URL": "",
                "MOVIE_COSMOS_GALAXY_DATA_FILE": "",
            },
            clear=False,
        ):
            with self.assertRaisesRegex(GalaxyRosterError, "release input required"):
                resolve_chronicle_release_input()

        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "galaxy.json"
            path.write_text("{}", encoding="utf-8")
            with patch.dict(
                os.environ,
                {
                    "MOVIE_COSMOS_GALAXY_MANIFEST_URL": "https://example.test/data/galaxy_assets_manifest.json",
                    "MOVIE_COSMOS_GALAXY_DATA_FILE": str(path),
                },
                clear=False,
            ):
                with self.assertRaisesRegex(GalaxyRosterError, "exactly one"):
                    resolve_chronicle_release_input()

    def test_movie_url_gate_skips_when_release_unset(self) -> None:
        with patch.dict(
            os.environ,
            {
                "MOVIE_COSMOS_GALAXY_MANIFEST_URL": "",
                "MOVIE_COSMOS_GALAXY_DATA_FILE": "",
            },
            clear=False,
        ):
            from scripts.lib.galaxy_roster import assert_movie_url_allowed

            self.assertEqual(
                assert_movie_url_allowed(42, prefix="https://themoviecosmos.com/movie/"),
                "https://themoviecosmos.com/movie/42",
            )

    def test_movie_url_gate_fails_for_off_roster_id(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "galaxy.json"
            path.write_text(
                json.dumps({"meta": {"version": "v1", "count": 1}, "movies": [{"id": 1}]}),
                encoding="utf-8",
            )
            with patch.dict(
                os.environ,
                {
                    "MOVIE_COSMOS_GALAXY_DATA_FILE": str(path),
                    "MOVIE_COSMOS_GALAXY_MANIFEST_URL": "",
                },
                clear=False,
            ):
                from scripts.lib.galaxy_roster import assert_movie_url_allowed

                with self.assertRaisesRegex(GalaxyRosterError, "not in Chronicle Galaxy Roster"):
                    assert_movie_url_allowed(99, prefix="https://themoviecosmos.com/movie/")


if __name__ == "__main__":
    unittest.main()
