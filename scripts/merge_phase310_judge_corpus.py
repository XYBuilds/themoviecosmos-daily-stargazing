"""Merge obs calibration judge scores with holdout one-shot scores (Phase 3.10.7)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.llm_judge import write_judge_markdown, load_judge_output


def merge_corpus(obs_json: Path, holdout_json: Path, out_json: Path, out_md: Path) -> int:
    obs = load_judge_output(obs_json)
    holdout = load_judge_output(holdout_json)
    obs_keys = {(s.run_id, str(s.tmdb_id)) for s in obs.scores}
    holdout_only = [
        s for s in holdout.scores if (s.run_id, str(s.tmdb_id)) not in obs_keys
    ]
    merged_scores = list(obs.scores) + holdout_only
    merged = type(obs)(
        version=obs.version,
        calibration=obs.calibration,
        scores=merged_scores,
    )
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(
        json.dumps(merged.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_judge_markdown(out_md, merged)
    print(
        f"merged obs={len(obs.scores)} holdout={len(holdout_only)} "
        f"total={len(merged_scores)} -> {out_json}"
    )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--obs-json",
        type=Path,
        default=_REPO_ROOT / "output/Eval/phase3.10-judge-calibration/llm-judge-scores.json",
    )
    parser.add_argument("--holdout-json", type=Path, required=True)
    parser.add_argument(
        "--out-json",
        type=Path,
        default=_REPO_ROOT / "output/Eval/phase3.10/llm-judge-scores.json",
    )
    parser.add_argument(
        "--out-md",
        type=Path,
        default=_REPO_ROOT / "output/Eval/phase3.10/llm-judge-scores.md",
    )
    args = parser.parse_args(argv)
    for p in (args.obs_json, args.holdout_json):
        path = p if p.is_absolute() else _REPO_ROOT / p
        if not path.is_file():
            print(f"missing: {path}", file=sys.stderr)
            return 1
    out_json = args.out_json if args.out_json.is_absolute() else _REPO_ROOT / args.out_json
    out_md = args.out_md if args.out_md.is_absolute() else _REPO_ROOT / args.out_md
    obs_json = args.obs_json if args.obs_json.is_absolute() else _REPO_ROOT / args.obs_json
    holdout_json = (
        args.holdout_json
        if args.holdout_json.is_absolute()
        else _REPO_ROOT / args.holdout_json
    )
    return merge_corpus(obs_json, holdout_json, out_json, out_md)


if __name__ == "__main__":
    raise SystemExit(main())
