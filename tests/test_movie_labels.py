from scripts.lib.movie_labels import GENRE_EN_TO_ZH, LANG_CODE_TO_ZH


def test_genre_map_has_core_tmdb_keys() -> None:
    required = {
        "Action",
        "Adventure",
        "Animation",
        "Comedy",
        "Crime",
        "Documentary",
        "Drama",
        "Family",
        "Fantasy",
        "History",
        "Horror",
        "Music",
        "Mystery",
        "Romance",
        "Science Fiction",
        "TV Movie",
        "Thriller",
        "War",
        "Western",
    }

    assert required.issubset(GENRE_EN_TO_ZH)
    assert all(GENRE_EN_TO_ZH[key].strip() for key in required)


def test_language_map_covers_common_codes() -> None:
    required = {
        "en",
        "fr",
        "es",
        "ja",
        "de",
        "it",
        "zh",
        "ko",
        "ru",
        "pt",
        "nl",
        "tr",
        "ar",
        "hi",
        "sv",
        "no",
        "da",
        "fi",
        "pl",
    }

    assert required.issubset(LANG_CODE_TO_ZH)
    assert all(LANG_CODE_TO_ZH[key].strip() for key in required)


def test_static_maps_are_non_empty() -> None:
    assert GENRE_EN_TO_ZH
    assert LANG_CODE_TO_ZH
    assert all(key.strip() and value.strip() for key, value in GENRE_EN_TO_ZH.items())
    assert all(key.strip() and value.strip() for key, value in LANG_CODE_TO_ZH.items())