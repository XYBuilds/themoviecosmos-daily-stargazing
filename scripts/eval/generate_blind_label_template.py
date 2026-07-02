"""Generate blind human-label templates for Phase 5 judge calibration."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


DEFAULT_JSON_NAME = "blind_label_template.json"
DEFAULT_MD_NAME = "blind_label_template.md"
VALID_JUDGE_GLOB = "llm-judge-scores*.json"


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def json_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("scores", "items", "candidates", "news", "news_pool", "rows"):
            value = payload.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
    raise ValueError("input JSON must be a list or contain a list field")


def find_pool_json(directory: Path) -> Path | None:
    names = ("news_pool*.json", "*pool*.json", "reality.json")
    for pattern in names:
        matches = sorted(directory.glob(pattern))
        if matches:
            return matches[0]
    return None


def find_judge_jsons(path: Path) -> list[Path]:
    directory = path if path.is_dir() else path.parent
    return sorted(directory.glob(VALID_JUDGE_GLOB)) if directory.exists() else []


def load_judge_scores(path: Path) -> dict[int, int]:
    scores: dict[int, int] = {}
    for idx, row in enumerate(json_rows(read_json(path))):
        news_idx = parse_int(row.get("news_idx"), default=idx)
        judge_score = parse_int(row.get("judge_score", row.get("score")))
        if news_idx is not None and judge_score in {0, 1, 2}:
            scores[news_idx] = judge_score
    return scores


def load_all_judge_scores(paths: list[Path]) -> dict[int, int]:
    merged: dict[int, int] = {}
    for path in paths:
        merged.update(load_judge_scores(path))
    return merged


def parse_int(value: Any, default: int | None = None) -> int | None:
    if value is None:
        return default
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def source_rows(pool: Path) -> tuple[list[dict[str, Any]], Path]:
    if pool.is_dir():
        pool_json = find_pool_json(pool)
        if pool_json is not None:
            return json_rows(read_json(pool_json)), pool_json
        judge_jsons = find_judge_jsons(pool)
        if judge_jsons:
            return json_rows(read_json(judge_jsons[0])), judge_jsons[0]
        raise FileNotFoundError(f"no pool JSON or {VALID_JUDGE_GLOB} found in {pool}")
    return json_rows(read_json(pool)), pool


def template_row(index: int, row: dict[str, Any]) -> dict[str, Any]:
    news_idx = parse_int(row.get("news_idx"), default=index)
    return {
        "news_idx": news_idx,
        "title": str(row.get("title") or "").strip(),
        "url": str(row.get("url") or "").strip(),
        "human_score": None,
        "notes": "",
    }


def build_template(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [template_row(index, row) for index, row in enumerate(rows)]


def render_markdown(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Phase 5.4 盲标模板",
        "",
        "填写说明：只填 human_score（0/1/2）和 notes；不要参考 judge 分。",
        "",
    ]
    for row in rows:
        lines.extend(
            [
                f"## news_idx {row['news_idx']}",
                "",
                f"- title: {row['title']}",
                f"- url: {row['url']}",
                "- human_score: ",
                "- notes: ",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def write_outputs(rows: list[dict[str, Any]], out_dir: Path) -> tuple[Path, Path]:
    json_path = out_dir / DEFAULT_JSON_NAME
    md_path = out_dir / DEFAULT_MD_NAME
    write_json(json_path, rows)
    md_path.write_text(render_markdown(rows), encoding="utf-8")
    return json_path, md_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate blind Phase 5 human-label JSON/Markdown templates."
    )
    parser.add_argument(
        "--pool",
        required=True,
        type=Path,
        help="news_pool JSON file, or a directory containing pool/judge JSON files",
    )
    parser.add_argument(
        "--out-dir",
        required=True,
        type=Path,
        help="directory for blind_label_template.json and .md",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    rows, source = source_rows(args.pool)
    judge_scores = load_all_judge_scores(find_judge_jsons(args.pool))
    template = build_template(rows)
    json_path, md_path = write_outputs(template, args.out_dir)
    print(f"source: {source}")
    print(f"items: {len(template)}")
    print(f"judge_scores_loaded_blind_hidden: {len(judge_scores)}")
    print(f"wrote: {json_path}")
    print(f"wrote: {md_path}")
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()