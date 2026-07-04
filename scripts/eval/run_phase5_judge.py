"""Phase 5.4 judge calibration driver (deterministic, resumable).

Reads per-run candidates from ``output/Eval/phase5/cal-0X/`` (reality.json +
candidates.json), scores every (news, film) pair with the LLM judge in
parallel (reusing ``judge_batch_parallel.score_pending_pairs`` with a
thread-safe checkpoint), then regenerates all Phase 5.4 downstream artifacts:

- ``llm-judge-scores.json``      standard JudgeOutput (score_items replay)
- ``llm-judge-scores.md``        human-readable judge summary
- ``llm-judge-scores-calibration.json``  per-news custom calibration list
- ``blind_label_template.json/.md``      shuffled blind human-label template
- ``phase5.4-judge-calibration-review.md``  per-news review with judge scores

Data flow (functional, single pass):

    cal dirs ──► load_runs ──► JudgeItem[]  ─score_pending_pairs(parallel)─►
        partial{(run_id,tmdb): row} ──► render_* ──► artifacts

Idempotent resume: existing ``llm-judge-scores.partial.json`` rows are reused;
only missing pairs call the LLM. Use ``--fresh`` to re-score everything.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.judge_batch_parallel import item_key, score_pending_pairs
from scripts.llm_judge import (
    JudgeItem,
    judge_run_metadata,
    score_items,
    write_judge_markdown,
)
from scripts.run_eval import _agents_from_hit_sources

DEFAULT_EVAL_DIR = _REPO_ROOT / "output" / "Eval" / "phase5"
DEFAULT_WORKERS = 4
DEFAULT_BLIND_SEED = 20260703
MOVIE_URL_BASE = "https://themoviecosmos.com/movie"

# Blind-label sampling: all score-2 + this many random score-1 + score-0.
BLIND_SCORE1_SAMPLE = 5
BLIND_SCORE0_SAMPLE = 10


# ── run discovery + JudgeItem construction ──────────────────────────────────


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def discover_cal_runs(eval_dir: Path) -> list[Path]:
    """Return sorted cal-0X run dirs that have both reality + candidates."""
    runs = []
    for run_dir in sorted(eval_dir.glob("cal-*")):
        if (run_dir / "reality.json").is_file() and (
            run_dir / "candidates.json"
        ).is_file():
            runs.append(run_dir)
    return runs


def _display_title(cand: dict[str, Any]) -> str:
    """Rebuild run_eval-style heading suffix: '<title> (<year>) [agents] [汇聚标注]'."""
    title = str(cand.get("title") or "Untitled")
    year = cand.get("release_year")
    year_part = f" ({year})" if year is not None else ""
    agents = _agents_from_hit_sources(cand)
    parts: list[str] = []
    if agents:
        parts.append(f"[{', '.join(agents)}]")
    if cand.get("quality_candidate"):
        parts.append("[汇聚标注]")
    suffix = f" {' '.join(parts)}" if parts else ""
    return f"{title}{year_part}{suffix}"


def build_items(runs: list[Path]) -> tuple[list[JudgeItem], dict[str, dict[str, Any]]]:
    """Build JudgeItems (run_id=cal-0X) and keep raw candidate context per key."""
    items: list[JudgeItem] = []
    context: dict[str, dict[str, Any]] = {}  # (run_id, tmdb) key -> render context
    for run_dir in runs:
        run_id = run_dir.name  # cal-01 ...
        reality = _read_json(run_dir / "reality.json")
        news_title = str(reality.get("title") or "")
        news_summary = str(reality.get("description") or reality.get("summary") or "")
        candidates = _read_json(run_dir / "candidates.json").get("candidates", [])
        for cand in candidates:
            tmdb_id = str(cand.get("tmdb_id"))
            items.append(
                JudgeItem(
                    run_id=run_id,
                    tmdb_id=tmdb_id,
                    title=_display_title(cand),
                    news_title=news_title,
                    news_summary=news_summary,
                    movie_overview=str(cand.get("overview") or ""),
                )
            )
            context[f"{run_id}::{tmdb_id}"] = {
                "run_dir": run_dir,
                "reality": reality,
                "cand": cand,
            }
    return items, context


# ── parallel judge scoring with resumable checkpoint ────────────────────────


def _load_partial(path: Path) -> dict[tuple[str, str], dict]:
    """Reload prior rows from partial JSON (list of row dicts) for resume."""
    if not path.is_file():
        return {}
    rows = _read_json(path)
    if isinstance(rows, dict):
        rows = rows.get("scores") or []
    partial: dict[tuple[str, str], dict] = {}
    for row in rows:
        key = (str(row["run_id"]), str(row["tmdb_id"]))
        partial[key] = {**row, "tmdb_id": str(row["tmdb_id"])}
    return partial


def _write_partial(path: Path, partial: dict[tuple[str, str], dict]) -> None:
    rows = list(partial.values())
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(
        json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    tmp.replace(path)


def score_all(
    items: list[JudgeItem],
    partial_path: Path,
    *,
    provider: str | None,
    mimo_thinking: str | None,
    workers: int,
    fresh: bool,
) -> dict[tuple[str, str], dict]:
    """Score every pair in parallel; checkpoint after each completion."""
    partial = {} if fresh else _load_partial(partial_path)
    pending = [i for i in items if item_key(i) not in partial]
    done0 = len(items) - len(pending)
    started = time.monotonic()
    print(
        f"items={len(items)} done={done0} pending={len(pending)} "
        f"workers={max(1, workers)}",
        flush=True,
    )

    def checkpoint() -> None:
        _write_partial(partial_path, partial)

    def on_progress(idx: int, total: int, item: JudgeItem) -> None:
        elapsed = time.monotonic() - started
        rate = idx / elapsed if elapsed > 0 else 0.0
        eta = (total - idx) / rate if rate > 0 else None
        eta_text = f" eta={eta:.0f}s" if eta is not None else ""
        print(
            f"progress={done0 + idx}/{len(items)} batch={idx}/{total} "
            f"elapsed={elapsed:.0f}s{eta_text} last={item.run_id}/{item.tmdb_id}",
            flush=True,
        )

    score_pending_pairs(
        pending,
        partial=partial,
        provider=provider,
        mimo_thinking=mimo_thinking,
        workers=workers,
        checkpoint_fn=checkpoint,
        on_progress=on_progress,
    )
    if pending:
        checkpoint()
    return partial


# ── artifact rendering ──────────────────────────────────────────────────────


def _replay_fn(partial: dict[tuple[str, str], dict]):
    """Replay judge_fn reading scored rows (no LLM calls) for score_items."""

    def replay(item: JudgeItem):
        row = partial[item_key(item)]
        return (
            int(row["judge_score"]),
            row.get("judge_resonance_type"),
            str(row.get("rationale") or ""),
            str(row.get("causal_test") or ""),
            row.get("judge_pov_transform"),
        )

    return replay


def write_standard_outputs(
    items: list[JudgeItem],
    partial: dict[tuple[str, str], dict],
    out_json: Path,
    out_md: Path,
    *,
    provider: str | None,
    mimo_thinking: str | None,
) -> None:
    """llm-judge-scores.json + .md via score_items replay (cal-* has no obs ids)."""
    output = score_items(items, _replay_fn(partial), observation_run_ids=[])
    run_metadata = judge_run_metadata(provider, mimo_thinking=mimo_thinking)
    payload = output.to_dict()
    payload["run_metadata"] = run_metadata
    out_json.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_judge_markdown(out_md, output, run_metadata=run_metadata)


def build_calibration(
    runs: list[Path],
    partial: dict[tuple[str, str], dict],
    context: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    """Per-news custom calibration list (news_idx/title/url/run_id/candidates)."""
    out: list[dict[str, Any]] = []
    for news_idx, run_dir in enumerate(runs, start=1):
        run_id = run_dir.name
        reality = _read_json(run_dir / "reality.json")
        cands = _read_json(run_dir / "candidates.json").get("candidates", [])
        rows = []
        for cand in cands:
            tmdb_id = str(cand.get("tmdb_id"))
            row = partial.get((run_id, tmdb_id))
            if row is None:
                continue
            rows.append(
                {
                    "tmdb_id": tmdb_id,
                    "title": _display_title(cand),
                    "judge_score": int(row["judge_score"]),
                    "resonance_type": row.get("judge_resonance_type") or "",
                }
            )
        out.append(
            {
                "news_idx": news_idx,
                "title": str(reality.get("title") or ""),
                "url": str(reality.get("url") or ""),
                "run_id": f"phase5-{run_id}",
                "candidates": rows,
            }
        )
    return out


def _sorted_scored(
    run_dir: Path, partial: dict[tuple[str, str], dict]
) -> list[tuple[dict[str, Any], dict]]:
    """Candidates joined with judge row, sorted by judge_score desc then similarity."""
    run_id = run_dir.name
    cands = _read_json(run_dir / "candidates.json").get("candidates", [])
    joined = []
    for cand in cands:
        row = partial.get((run_id, str(cand.get("tmdb_id"))))
        if row is not None:
            joined.append((cand, row))
    joined.sort(
        key=lambda cr: (-int(cr[1]["judge_score"]), -(cr[0].get("similarity") or 0.0))
    )
    return joined


def render_review(
    runs: list[Path], partial: dict[tuple[str, str], dict]
) -> str:
    lines = [
        "# Phase 5.4 · Judge 分布重对齐 · 审核稿",
        "",
        "> 请对每个「新闻×电影」候选填写 human_score（0/1/2），按 3.10 双轴 rubric。",
        "> - 0 = 无共振",
        "> - 1 = 弱共振 / 表面关联",
        "> - 2 = 强共振（结构性 / 深层映射）",
        "",
        "---",
        "",
    ]
    for news_idx, run_dir in enumerate(runs, start=1):
        reality = _read_json(run_dir / "reality.json")
        joined = _sorted_scored(run_dir, partial)
        lines += [
            f"## News {news_idx}: {reality.get('title') or ''}",
            "",
            f"**Source:** {reality.get('source_name') or ''} | "
            f"**Date:** {reality.get('pub_time') or ''}",
            f"**URL:** {reality.get('url') or ''}",
            "",
            f"> {reality.get('description') or reality.get('summary') or ''}",
            "",
            "### Candidates (judge 评分降序)",
            "",
            "| # | 电影 | judge | resonance_type | human_score |",
            "|---|------|-------|----------------|-------------|",
        ]
        for i, (cand, row) in enumerate(joined, start=1):
            year = cand.get("release_year")
            year_part = f" ({year})" if year is not None else ""
            name = f"{cand.get('title') or 'Untitled'}{year_part}"
            rtype = row.get("judge_resonance_type") or "—"
            lines.append(
                f"| {i} | {name} | {row['judge_score']} | {rtype} | ___ |"
            )
        lines += ["", "<details><summary>候选详情</summary>", ""]
        for i, (cand, row) in enumerate(joined, start=1):
            year = cand.get("release_year")
            year_part = f" ({year})" if year is not None else ""
            tmdb_id = cand.get("tmdb_id")
            agents = _agents_from_hit_sources(cand)
            lines += [
                f"#### {i}. {cand.get('title') or 'Untitled'}{year_part} ({tmdb_id})",
                f"- **Judge Score:** {row['judge_score']}",
                f"- **Resonance Type:** {row.get('judge_resonance_type') or '—'}",
                f"- **Overview:** {cand.get('overview') or ''}",
                f"- **Genres:** {cand.get('genres') or ''}",
                f"- **Similarity:** {(cand.get('similarity') or 0.0):.4f}",
                f"- **Convergent Score:** {(cand.get('convergent_score') or 0.0):.4f}",
                f"- **Triggered By:** {', '.join(agents)}",
                f"- **Movie URL:** {MOVIE_URL_BASE}/{tmdb_id}",
                "- **你的评分:** ___",
                "",
            ]
        lines += ["</details>", "", "---", ""]
    return "\n".join(lines).rstrip() + "\n"


def build_blind_label(
    runs: list[Path],
    partial: dict[tuple[str, str], dict],
    *,
    seed: int,
) -> list[dict[str, Any]]:
    """All score-2 + N random score-1 + M random score-0, shuffled, judge hidden."""
    rng = random.Random(seed)
    by_score: dict[int, list[dict[str, Any]]] = {0: [], 1: [], 2: []}
    for news_idx, run_dir in enumerate(runs, start=1):
        run_id = run_dir.name
        reality = _read_json(run_dir / "reality.json")
        cands = _read_json(run_dir / "candidates.json").get("candidates", [])
        for cand in cands:
            row = partial.get((run_id, str(cand.get("tmdb_id"))))
            if row is None:
                continue
            score = int(row["judge_score"])
            by_score.setdefault(score, []).append(
                {
                    "news_idx": news_idx,
                    "news_title": str(reality.get("title") or ""),
                    "movie_title": _display_title(cand),
                    "tmdb_id": str(cand.get("tmdb_id")),
                    "resonance_type": row.get("judge_resonance_type") or "",
                    "human_score": None,
                    "notes": "",
                }
            )
    sample = list(by_score[2])
    sample += rng.sample(by_score[1], min(BLIND_SCORE1_SAMPLE, len(by_score[1])))
    sample += rng.sample(by_score[0], min(BLIND_SCORE0_SAMPLE, len(by_score[0])))
    rng.shuffle(sample)
    return sample


def render_blind_label_md(rows: list[dict[str, Any]]) -> str:
    lines = [
        "# Phase 5.4 盲标模板",
        "",
        "填写说明：只填 human_score（0/1/2）和 notes；不要参考 judge 分。",
        "",
    ]
    for row in rows:
        lines += [
            f"## news_idx {row['news_idx']} · {row['movie_title']}",
            "",
            f"- news: {row['news_title']}",
            f"- tmdb_id: {row['tmdb_id']}",
            "- human_score: ",
            "- notes: ",
            "",
        ]
    return "\n".join(lines).rstrip() + "\n"


def _write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


# ── main ────────────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-dir", type=Path, default=DEFAULT_EVAL_DIR)
    parser.add_argument("--provider", default=None)
    parser.add_argument(
        "--mimo-thinking", choices=["disabled", "enabled"], default="enabled"
    )
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS)
    parser.add_argument("--blind-seed", type=int, default=DEFAULT_BLIND_SEED)
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Ignore partial checkpoint and re-score all pairs",
    )
    args = parser.parse_args(argv)
    if args.workers < 1:
        print("error: --workers must be >= 1", file=sys.stderr)
        return 2

    eval_dir = (
        args.eval_dir if args.eval_dir.is_absolute() else _REPO_ROOT / args.eval_dir
    )
    runs = discover_cal_runs(eval_dir)
    if not runs:
        print(f"no cal-* runs under {eval_dir}", file=sys.stderr)
        return 1

    items, context = build_items(runs)
    partial_path = eval_dir / "llm-judge-scores.partial.json"
    partial = score_all(
        items,
        partial_path,
        provider=args.provider,
        mimo_thinking=args.mimo_thinking,
        workers=args.workers,
        fresh=args.fresh,
    )

    write_standard_outputs(
        items,
        partial,
        eval_dir / "llm-judge-scores.json",
        eval_dir / "llm-judge-scores.md",
        provider=args.provider,
        mimo_thinking=args.mimo_thinking,
    )
    _write_json(
        eval_dir / "llm-judge-scores-calibration.json",
        build_calibration(runs, partial, context),
    )
    (eval_dir / "phase5.4-judge-calibration-review.md").write_text(
        render_review(runs, partial), encoding="utf-8"
    )
    blind = build_blind_label(runs, partial, seed=args.blind_seed)
    _write_json(eval_dir / "blind_label_template.json", blind)
    (eval_dir / "blind_label_template.md").write_text(
        render_blind_label_md(blind), encoding="utf-8"
    )

    dist = {k: sum(1 for r in partial.values() if int(r["judge_score"]) == k) for k in (0, 1, 2)}
    print(
        f"scored={len(partial)} dist={dist} runs={len(runs)} "
        f"blind_items={len(blind)}",
        flush=True,
    )
    print(f"wrote artifacts under {eval_dir}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())