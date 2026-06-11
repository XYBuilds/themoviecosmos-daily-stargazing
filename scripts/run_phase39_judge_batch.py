"""Incremental LLM judge batch for Phase 3.9.7 (obs calibrate → freeze → holdout once).

Scores high-hit review candidates with resume support. Observation-set human scores
drive calibration; frozen thresholds apply to holdout without re-tuning.

Pair-level parallelism: use ``--workers N`` to score multiple (news, movie) pairs
concurrently (default 1 = serial). Checkpoint writes are thread-safe.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.eval_batch_manifest import load_manifest
from scripts.judge_batch_parallel import item_key, score_pending_pairs
from scripts.llm_judge import (
    call_llm_judge,
    collect_judge_items,
    score_items,
    write_judge_markdown,
)
from scripts.run_persona_batch import split_obs_holdout

DEFAULT_PROMPT_VERSION = "3.10.1b-logic-0-guard"


def _parse_run_ids(raw: str | None) -> list[str] | None:
    if not raw:
        return None
    ids = [part.strip() for part in raw.split(",") if part.strip()]
    return ids or None


def _load_partial(path: Path) -> dict[tuple[str, str], dict]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    partial: dict[tuple[str, str], dict] = {}
    for s in data.get("scores") or []:
        key = (s["run_id"], str(s["tmdb_id"]))
        partial[key] = {**s, "tmdb_id": str(s["tmdb_id"])}
    return partial


def run_incremental(
    eval_dir: Path,
    out_json: Path,
    out_md: Path,
    *,
    provider: str | None,
    obs_only: bool = False,
    holdout_only: bool = False,
    run_ids: list[str] | None = None,
    workers: int = 1,
    prompt_version: str = DEFAULT_PROMPT_VERSION,
    fresh: bool = False,
) -> int:
    all_run_ids = load_manifest()
    obs_ids, holdout_ids = split_obs_holdout(all_run_ids)
    if obs_only and holdout_only:
        print("error: --obs-only and --holdout-only are mutually exclusive", file=sys.stderr)
        return 2

    all_items = collect_judge_items(eval_dir)
    if run_ids is not None:
        allowed = set(run_ids)
        items = [i for i in all_items if i.run_id in allowed]
    elif obs_only:
        allowed = set(obs_ids)
        items = [i for i in all_items if i.run_id in allowed]
    elif holdout_only:
        allowed = set(holdout_ids)
        items = [i for i in all_items if i.run_id in allowed]
    else:
        items = all_items
    if not items:
        print("no judge items", file=sys.stderr)
        return 1

    partial = {} if fresh else _load_partial(out_json)
    pending = [i for i in items if item_key(i) not in partial]
    checkpoint_items = items
    print(
        f"items={len(items)} done={len(items)-len(pending)} pending={len(pending)} "
        f"workers={max(1, workers)} prompt_version={prompt_version}",
        flush=True,
    )

    def checkpoint() -> None:
        _write_checkpoint(
            out_json,
            out_md,
            checkpoint_items,
            partial,
            obs_ids,
            prompt_version=prompt_version,
        )

    def on_progress(idx: int, total: int, item) -> None:
        print(
            f"[{idx}/{total}] {item.run_id} {item.tmdb_id} {item.title[:40]}",
            flush=True,
        )

    score_pending_pairs(
        pending,
        partial=partial,
        provider=provider,
        workers=workers,
        checkpoint_fn=checkpoint,
        on_progress=on_progress,
    )

    if pending:
        checkpoint()
        scored = sum(1 for i in items if item_key(i) in partial)
        if scored != len(items):
            print(
                f"warning: expected {len(items)} scored pairs, checkpoint has {scored}",
                file=sys.stderr,
            )
            return 1
        backup = out_json.with_suffix(out_json.suffix + ".bak")
        shutil.copy2(out_json, backup)
        print(f"backup -> {backup}", flush=True)

    return 0


def _write_checkpoint(
    out_json: Path,
    out_md: Path,
    all_items,
    partial: dict[tuple[str, str], dict],
    obs_ids: list[str],
    *,
    prompt_version: str,
) -> None:
    scored_items = [i for i in all_items if item_key(i) in partial]

    def replay(item):
        row = partial[item_key(item)]
        return (
            int(row["judge_score"]),
            row.get("judge_resonance_type"),
            str(row.get("rationale") or ""),
            str(row.get("causal_test") or ""),
            row.get("judge_pov_transform"),
        )

    output = score_items(scored_items, replay, observation_run_ids=obs_ids)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    payload = output.to_dict()
    payload["prompt_version"] = prompt_version
    text = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    tmp = out_json.with_suffix(out_json.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(out_json)
    write_judge_markdown(out_md, output)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--eval-dir",
        type=Path,
        default=_REPO_ROOT / "output" / "Eval" / "phase3.9",
    )
    parser.add_argument(
        "--out-json",
        type=Path,
        default=None,
        help="Default: <eval-dir>/llm-judge-scores.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=None,
        help="Default: <eval-dir>/llm-judge-scores.md",
    )
    parser.add_argument("--provider", default=None)
    parser.add_argument("--obs-only", action="store_true")
    parser.add_argument("--holdout-only", action="store_true")
    parser.add_argument(
        "--run-ids",
        default=None,
        metavar="IDS",
        help="Comma-separated run_ids to score (e.g. 05-climate-disaster,06-tech-monopoly)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=1,
        metavar="N",
        help="Concurrent (news, movie) pair scorers (default: 1 = serial)",
    )
    parser.add_argument(
        "--prompt-version",
        default=DEFAULT_PROMPT_VERSION,
        help=f"Tag written into output JSON metadata (default: {DEFAULT_PROMPT_VERSION})",
    )
    parser.add_argument(
        "--fresh",
        action="store_true",
        help="Ignore existing partial checkpoint in --out-json (re-score all requested items)",
    )
    args = parser.parse_args(argv)

    if args.workers < 1:
        print("error: --workers must be >= 1", file=sys.stderr)
        return 2

    eval_dir = args.eval_dir if args.eval_dir.is_absolute() else _REPO_ROOT / args.eval_dir
    out_json = args.out_json or (eval_dir / "llm-judge-scores.json")
    out_md = args.out_md or (eval_dir / "llm-judge-scores.md")
    if not out_json.is_absolute():
        out_json = _REPO_ROOT / out_json
    if not out_md.is_absolute():
        out_md = _REPO_ROOT / out_md

    return run_incremental(
        eval_dir,
        out_json,
        out_md,
        provider=args.provider,
        obs_only=args.obs_only,
        holdout_only=args.holdout_only,
        run_ids=_parse_run_ids(args.run_ids),
        workers=args.workers,
        prompt_version=args.prompt_version,
        fresh=args.fresh,
    )


if __name__ == "__main__":
    raise SystemExit(main())
