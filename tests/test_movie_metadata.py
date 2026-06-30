from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from scripts.build_index import META_COLUMNS
from scripts.movie_metadata import (
    _DETAIL_CACHE,
    get_movie_detail_by_tmdb_id,
    get_movie_details_by_tmdb_ids,
)


class MovieMetadataLookupTests(unittest.TestCase):
    def setUp(self) -> None:
        _DETAIL_CACHE.clear()

    def test_tmdb_id_lookup_returns_every_source_column(self) -> None:
        with TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "cleaned.csv"
            columns = ["id", "director", "vote_average", *[f"col_{i}" for i in range(1, 26)]]
            pd.DataFrame(
                [
                    {
                        **{column: f"value-{column}" for column in columns},
                        "id": 157336,
                        "director": "Christopher Nolan",
                        "vote_average": 8.4,
                    }
                ]
            ).to_csv(csv_path, index=False)

            detail = get_movie_detail_by_tmdb_id(157336, csv_path=csv_path)

        self.assertIsNotNone(detail)
        assert detail is not None
        self.assertEqual(len(detail), 28)
        self.assertEqual(detail["id"], 157336)
        self.assertEqual(detail["director"], "Christopher Nolan")
        self.assertEqual(detail["vote_average"], 8.4)

    def test_tmdb_id_column_is_supported_as_canonical_key(self) -> None:
        with TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "cleaned.csv"
            pd.DataFrame(
                [
                    {"tmdb_id": 1, "title": "A"},
                    {"tmdb_id": 2, "title": "B"},
                ]
            ).to_csv(csv_path, index=False)

            details = get_movie_details_by_tmdb_ids([1, "2", 3], csv_path=csv_path)

        self.assertEqual(set(details), {"1", "2"})
        self.assertEqual(details["2"]["title"], "B")

    def test_retrieval_meta_columns_stay_lean(self) -> None:
        self.assertEqual(
            META_COLUMNS,
            [
                "id",
                "title",
                "original_title",
                "overview",
                "tagline",
                "genres",
                "original_language",
                "release_date",
                "poster_path",
            ],
        )
        self.assertNotIn("director", META_COLUMNS)
        self.assertNotIn("vote_average", META_COLUMNS)


if __name__ == "__main__":
    unittest.main()