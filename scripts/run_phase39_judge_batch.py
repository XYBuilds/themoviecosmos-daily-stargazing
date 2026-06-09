"""Incremental LLM judge batch for Phase 3.9.7 (obs calibrate → freeze → holdout once).

Scores high-hit review candidates with resume support. Observation-set human scores
drive calibration; frozen thresholds apply to holdout without re-tuning.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.eval_batch_manifest import load_manifest
from scripts.llm_judge import (
    JudgeOutput,
    JudgeResult,
    call_llm_judge,
    collect_judge_items,
    compute_calibration,
    score_items,
    write_judge_markdown,
)
from scripts.run_persona_batch import split_obs_holdout


def _item_key(item) -> tuple[str, str]:
    return item.run_id, item.tmdb_id


def _load_partial(path: Path) -> dict[tuple[str, str], dict]:
    if not path.is_file():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        (s["run_id"], str(s["tmdb_id"])): s for s in data.get("scores") or []
    }


def run_incremental(
    eval_dir: Path,
    out_json: Path,
    out_md: Path,
    *,
    provider: str | None,
    obs_only: bool = False,
    holdout_only: bool = False,
) -> int:
    all_run_ids = load_manifest()
    obs_ids, holdout_ids = split_obs_holdout(all_run_ids)
    if obs_only and holdout_only:
        print("error: --obs-only and --holdout-only are mutually exclusive", file=sys.stderr)
        return 2

    all_items = collect_judge_items(eval_dir)
    if obs_only:
        run_filter = obs_ids
    elif holdout_only:
        run_filter = holdout_ids
    else:
        run_filter = None

    items = all_items
    if run_filter is not None:
        allowed = set(run_filter)
        items = [i for i in all_items if i.run_id in allowed]
    if not items:
        print("no judge items", file=sys.stderr)
        return 1

    partial = _load_partial(out_json)
    pending = [i for i in items if _item_key(i) not in partial]
    print(f"items={len(items)} done={len(items)-len(pending)} pending={len(pending)}")

    for idx, item in enumerate(pending, start=1):
        print(f"[{idx}/{len(pending)}] {item.run_id} {item.tmdb_id} {item.title[:40]}", flush=True)
        judge_score, judge_type, rationale, causal_test = call_llm_judge(
            item, provider=provider
        )
        partial[_item_key(item)] = {
            "run_id": item.run_id,
            "tmdb_id": item.tmdb_id,
            "title": item.title,
            "judge_score": judge_score,
            "judge_resonance_type": judge_type,
            "rationale": rationale,
            "causal_test": causal_test,
            "human_score": item.human_score,
            "human_resonance_type": item.human_resonance_type,
            "disagreement": item.human_score is not None and item.human_score != judge_score,
        }
        _write_checkpoint(out_json, out_md, all_items, partial, obs_ids)

    return 0


def _write_checkpoint(
    out_json: Path,
    out_md: Path,
    all_items,
    partial: dict[tuple[str, str], dict],
    obs_ids: list[str],
) -> None:
    scored_items = [i for i in all_items if _item_key(i) in partial]

    def replay(item):
        row = partial[_item_key(item)]
        return (
            int(row["judge_score"]),
            row.get("judge_resonance_type"),
            str(row.get("rationale") or ""),
        )

    output = score_items(scored_items, replay, observation_run_ids=obs_ids)
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps(output.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
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
    args = parser.parse_args(argv)

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
    )


if __name__ == "__main__":
    raise SystemExit(main())
