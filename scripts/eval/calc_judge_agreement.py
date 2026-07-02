"""Calculate Phase 5 judge-vs-human score agreement."""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
from typing import Any


SCORES = (0, 1, 2)


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def json_rows(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict):
        for key in ("scores", "items", "candidates", "news", "news_pool", "rows"):
            value = payload.get(key)
            if isinstance(value, list):
                return [row for row in value if isinstance(row, dict)]
    raise ValueError("input JSON must be a list or contain a list field")


def parse_score(value: Any, label: str) -> int:
    try:
        score = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{label} must be 0, 1, or 2; got {value!r}") from exc
    if score not in SCORES:
        raise ValueError(f"{label} must be 0, 1, or 2; got {value!r}")
    return score


def parse_news_idx(value: Any, fallback: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return fallback


def human_scores(path: Path) -> dict[int, int]:
    out: dict[int, int] = {}
    for idx, row in enumerate(json_rows(read_json(path))):
        news_idx = parse_news_idx(row.get("news_idx"), idx)
        out[news_idx] = parse_score(row.get("human_score"), f"human_score for news_idx {news_idx}")
    return out


def judge_scores(path: Path) -> dict[int, int]:
    out: dict[int, int] = {}
    for idx, row in enumerate(json_rows(read_json(path))):
        news_idx = parse_news_idx(row.get("news_idx"), idx)
        raw_score = row.get("judge_score", row.get("score"))
        out[news_idx] = parse_score(raw_score, f"judge_score for news_idx {news_idx}")
    return out


def aligned_pairs(human: dict[int, int], judge: dict[int, int]) -> list[tuple[int, int, int]]:
    missing = sorted(set(human) - set(judge))
    if missing:
        preview = ", ".join(str(x) for x in missing[:10])
        suffix = "..." if len(missing) > 10 else ""
        raise ValueError(f"missing judge scores for news_idx: {preview}{suffix}")
    pairs = [(idx, human[idx], judge[idx]) for idx in sorted(human)]
    if not pairs:
        raise ValueError("no aligned human/judge scores found")
    return pairs


def confusion(pairs: list[tuple[int, int, int]]) -> Counter[tuple[int, int]]:
    return Counter((human, judge) for _, human, judge in pairs)


def pct(numerator: int, denominator: int) -> str:
    if denominator == 0:
        return "N/A"
    return f"{(numerator / denominator * 100):.1f}% ({numerator}/{denominator})"


def exact_match(pairs: list[tuple[int, int, int]]) -> tuple[int, int]:
    exact = sum(1 for _, human, judge in pairs if human == judge)
    return exact, len(pairs)


def precision_for_2(matrix: Counter[tuple[int, int]]) -> tuple[int, int]:
    true_positive = matrix[(2, 2)]
    predicted_2 = sum(matrix[(human, 2)] for human in SCORES)
    return true_positive, predicted_2


def recall_for_0(matrix: Counter[tuple[int, int]]) -> tuple[int, int]:
    true_zero = matrix[(0, 0)]
    human_zero = sum(matrix[(0, judge)] for judge in SCORES)
    return true_zero, human_zero


def render_matrix(matrix: Counter[tuple[int, int]]) -> list[str]:
    lines = [
        "| human \\ judge | 0 | 1 | 2 |",
        "| --- | ---: | ---: | ---: |",
    ]
    for human in SCORES:
        cells = " | ".join(str(matrix[(human, judge)]) for judge in SCORES)
        lines.append(f"| {human} | {cells} |")
    return lines


def render_report(pairs: list[tuple[int, int, int]]) -> str:
    matrix = confusion(pairs)
    exact, total = exact_match(pairs)
    p2_num, p2_den = precision_for_2(matrix)
    r0_num, r0_den = recall_for_0(matrix)
    lines = [
        "# Phase 5.4 Judge 一致率校准",
        "",
        f"- 样本数: {total}",
        f"- 总体一致率 exact match: {pct(exact, total)}",
        f"- judge=2 精度: {pct(p2_num, p2_den)}",
        f"- judge=0 漏杀率/召回（human=0 中 judge=0）: {pct(r0_num, r0_den)}",
        "",
        "## 混淆矩阵（human rows × judge cols）",
        "",
        *render_matrix(matrix),
        "",
        "## 裁决建议模板",
        "",
        "- 若总体一致率 ≥ ____% → 债2清。",
        "- 否则：需调整 judge 阈值 / 提示词 / 预筛口径后重跑校准。",
        "",
    ]
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Calculate exact agreement and confusion matrix for Phase 5 judge scores."
    )
    parser.add_argument("--human", required=True, type=Path, help="filled blind label JSON")
    parser.add_argument("--judge", required=True, type=Path, help="llm-judge-scores*.json")
    parser.add_argument("--out", type=Path, help="optional Markdown report output path")
    return parser


def run(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    pairs = aligned_pairs(human_scores(args.human), judge_scores(args.judge))
    report = render_report(pairs)
    print(report)
    if args.out is not None:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(report, encoding="utf-8")
    return 0


def main() -> None:
    raise SystemExit(run())


if __name__ == "__main__":
    main()