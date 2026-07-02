"""Build Discord publish assets from a publish draft and movie metadata."""

from __future__ import annotations

import argparse
import os
import sys
import urllib.error
import urllib.request
from datetime import date, datetime
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.lib.env import load_env, default_llm_provider
from scripts.lib.llm import get_llm_client
from scripts.lib.paths import repo_root
from scripts.movie_metadata import get_movie_detail_by_tmdb_id

POSTER_BASE_URL = "https://image.tmdb.org/t/p/original"
MOVIE_URL_BASE = "https://themoviecosmos.com/movie"


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create Discord markdown and poster assets from a publish draft."
    )
    parser.add_argument(
        "--draft",
        required=True,
        type=Path,
        help="Path to the publish_draft markdown file.",
    )
    parser.add_argument(
        "--date",
        default=date.today().isoformat(),
        help="Publish date in YYYY-MM-DD format. Defaults to today.",
    )
    return parser.parse_args(argv)


def validate_date(value: str) -> str:
    try:
        datetime.strptime(value, "%Y-%m-%d")
    except ValueError as exc:
        raise RuntimeError(f"invalid --date {value!r}; expected YYYY-MM-DD") from exc
    return value


def read_draft(draft_path: Path) -> str:
    if not draft_path.is_file():
        raise RuntimeError(f"draft file not found: {draft_path}")
    return draft_path.read_text(encoding="utf-8")


def extract_draft_parts(draft_text: str) -> tuple[str, str]:
    lines = draft_text.strip().splitlines()
    if len(lines) < 3:
        raise RuntimeError("draft is too short; expected title, body, and movie URL")

    url_line = lines[-1].strip()
    tmdb_id = url_line.rstrip("/").split("/")[-1].strip()
    if not tmdb_id.isdigit():
        raise RuntimeError(f"could not extract numeric tmdb_id from URL: {url_line}")

    body = "\n".join(lines[2:-1]).strip()
    if not body:
        raise RuntimeError("draft body is empty")

    return tmdb_id, body


def require_text(meta: dict[str, Any], field: str, tmdb_id: str) -> str:
    value = meta.get(field)
    if value is None or str(value).strip() == "":
        raise RuntimeError(f"movie {tmdb_id} is missing required field: {field}")
    return str(value).strip()


def load_movie_meta(tmdb_id: str) -> dict[str, Any]:
    try:
        meta = get_movie_detail_by_tmdb_id(tmdb_id)
    except FileNotFoundError as exc:
        raise RuntimeError(str(exc)) from exc
    except Exception as exc:
        raise RuntimeError(f"failed to load movie metadata for {tmdb_id}: {exc}") from exc

    if meta is None:
        raise RuntimeError(f"tmdb_id not found in movie metadata CSV: {tmdb_id}")
    return meta


_MODEL_ENV: dict[str, str] = {
    "mimo": "MIMO_MODEL",
    "deepseek": "DEEPSEEK_MODEL",
}


def _strip_label(text: str) -> str:
    """Remove common LLM label prefixes like '1. 电影名称：《...》'."""
    import re
    # Remove leading numbering: "1. " / "2. "
    text = re.sub(r"^\d+\.\s*", "", text)
    # Remove label prefixes: "电影名称：" / "导演姓名：" / "标题:" etc.
    text = re.sub(r"^[\u4e00-\u9fff]+[：:]\s*", "", text)
    # Remove book title marks: 《》
    text = text.strip("《》")
    return text.strip()


def translate_meta_to_chinese(title: str, director: str) -> tuple[str, str]:
    """Translate movie title and director name to Simplified Chinese via LLM."""
    load_env()
    provider = default_llm_provider()
    model_env_key = _MODEL_ENV.get(provider, "DEEPSEEK_MODEL")
    model = os.environ.get(model_env_key, "deepseek-chat")
    client = get_llm_client()

    prompt = (
        "Please translate into Simplified Chinese:\n"
        f"1. Movie title: {title}\n"
        f"2. Director name: {director}"
    )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1,
        max_tokens=200,
    )

    result = response.choices[0].message.content.strip()
    if not result:
        # LLM returned empty — fallback to original
        return title, director

    lines = [ln for ln in result.splitlines() if ln.strip()]
    if len(lines) >= 2:
        return _strip_label(lines[0]), _strip_label(lines[1])
    elif len(lines) == 1:
        return _strip_label(lines[0]), director
    return title, director


def build_discord_markdown(tmdb_id: str, body: str, meta: dict[str, Any]) -> str:
    title_en = require_text(meta, "title", tmdb_id)
    original_title = require_text(meta, "original_title", tmdb_id)
    release_date = require_text(meta, "release_date", tmdb_id)
    director_en = require_text(meta, "director", tmdb_id)

    year = release_date[:4]
    if len(year) != 4 or not year.isdigit():
        raise RuntimeError(
            f"movie {tmdb_id} has invalid release_date for year extraction: {release_date}"
        )

    # Translate title and director to Chinese
    localized_title, localized_director = translate_meta_to_chinese(title_en, director_en)

    return (
        f"{localized_title} / {original_title} / {year} / {localized_director}\n\n"
        f"{body}\n\n"
        f"{MOVIE_URL_BASE}/{tmdb_id}\n"
    )


def download_poster(tmdb_id: str, poster_path: str, output_path: Path) -> None:
    poster_url = f"{POSTER_BASE_URL}{poster_path}"
    request = urllib.request.Request(
        poster_url,
        headers={"User-Agent": "themoviecosmos-publish-discord/1.0"},
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            output_path.write_bytes(response.read())
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RuntimeError(f"failed to download poster from {poster_url}: {exc}") from exc


def write_outputs(publish_date: str, tmdb_id: str, markdown: str, meta: dict[str, Any]) -> tuple[Path, Path]:
    output_dir = repo_root() / "output" / "discord"
    output_dir.mkdir(parents=True, exist_ok=True)

    markdown_path = output_dir / f"{publish_date}-discord-{tmdb_id}.md"
    poster_path = output_dir / f"{publish_date}-discord-{tmdb_id}-poster.jpg"

    poster_source_path = require_text(meta, "poster_path", tmdb_id)
    markdown_path.write_text(markdown, encoding="utf-8")
    download_poster(tmdb_id, poster_source_path, poster_path)

    return markdown_path, poster_path


def run(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    publish_date = validate_date(args.date)
    draft_text = read_draft(args.draft)
    tmdb_id, body = extract_draft_parts(draft_text)
    meta = load_movie_meta(tmdb_id)
    markdown = build_discord_markdown(tmdb_id, body, meta)
    markdown_path, poster_path = write_outputs(publish_date, tmdb_id, markdown, meta)

    print(f"Discord markdown written: {markdown_path}")
    print(f"Poster downloaded: {poster_path}")
    return 0


def main() -> int:
    try:
        return run()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())