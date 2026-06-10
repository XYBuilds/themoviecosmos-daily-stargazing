"""Apply holdout human labels for prescreen workflow (Phase 3.10.7).

Labels only candidates that require human review under frozen ``judge≥1`` prescreen:
``manual_review`` pool (judge≥1) plus rejection-set audit samples (judge=0, k%).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts.apply_obs_fresh_labels_phase310 import (
    FreshLabel,
    _apply_labels_to_review,
    _update_rubric_header,
    call_editor_label,
)
from scripts.judge_prescreen import load_prescreen_report
from scripts.llm_judge import collect_judge_items
from scripts.resonance_rubric import validate_score_type_pair
from scripts.run_persona_batch import OBS_RUN_PREFIXES, split_obs_holdout

PHASE310 = _REPO_ROOT / "output" / "Eval" / "phase3.10"


def _holdout_run_ids(all_run_ids: list[str]) -> list[str]:
    _, holdout = split_obs_holdout(all_run_ids)
    return holdout


def _prescreen_label_keys(prescreen_json: Path) -> set[tuple[str, str]]:
    report = load_prescreen_report(prescreen_json)
    keys: set[tuple[str, str]] = set()
    for item in report.items:
        if not item.run_id.startswith(OBS_RUN_PREFIXES):
            if item.manual_review or item.rejection_audit_sampled:
                keys.add((item.run_id, item.tmdb_id))
    return keys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--eval-dir", type=Path, default=PHASE310)
    parser.add_argument(
        "--prescreen-json",
        type=Path,
        default=PHASE310 / "judge-prescreen.json",
    )
    parser.add_argument("--provider", default=None)
    parser.add_argument("--delay", type=float, default=0.5)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--apply-only",
        action="store_true",
        help="Patch review from existing holdout-fresh-labels.json",
    )
    parser.add_argument(
        "--human",
        action="store_true",
        help="Write scores/types (and optional human remark) to editor fields in review",
    )
    args = parser.parse_args(argv)

    eval_dir = args.eval_dir if args.eval_dir.is_absolute() else _REPO_ROOT / args.eval_dir
    review_path = eval_dir / "high-hit-score-review.md"
    audit_path = eval_dir / "holdout-fresh-labels.json"
    prescreen_path = (
        args.prescreen_json
        if args.prescreen_json.is_absolute()
        else _REPO_ROOT / args.prescreen_json
    )
    if not review_path.is_file():
        print(f"missing review: {review_path}", file=sys.stderr)
        return 1
    if not prescreen_path.is_file():
        print(f"missing prescreen: {prescreen_path}", file=sys.stderr)
        return 1

    label_keys = _prescreen_label_keys(prescreen_path)
    holdout_ids = _holdout_run_ids(
        sorted({rid for rid, _ in label_keys})
    )

    if args.apply_only:
        if not audit_path.is_file():
            print(f"missing audit: {audit_path}", file=sys.stderr)
            return 1
        prior = json.loads(audit_path.read_text(encoding="utf-8"))
        labels = {
            (row["run_id"], str(row["tmdb_id"])): FreshLabel(**row)
            for row in prior.get("labels") or []
        }
        review_text = _update_rubric_header(review_path.read_text(encoding="utf-8"))
        review_path.write_text(
            _apply_labels_to_review(review_text, labels, human_fields=args.human),
            encoding="utf-8",
        )
        mode = "human editor fields" if args.human else "no human fields (audit only)"
        print(f"applied {len(labels)} holdout labels to {review_path} ({mode})")
        return 0

    items = collect_judge_items(eval_dir, review_path=review_path, run_ids=holdout_ids)
    items = [i for i in items if (i.run_id, i.tmdb_id) in label_keys]
    for item in items:
        item.human_score = None
        item.human_resonance_type = None

    if not items:
        print("no holdout prescreen candidates found", file=sys.stderr)
        return 1

    print(
        f"labeling {len(items)} holdout prescreen candidates "
        f"(judge≥1 + rejection audit)",
        file=sys.stderr,
    )

    labels: dict[tuple[str, str], FreshLabel] = {}
    if audit_path.is_file():
        prior = json.loads(audit_path.read_text(encoding="utf-8"))
        for row in prior.get("labels") or []:
            labels[(row["run_id"], str(row["tmdb_id"]))] = FreshLabel(**row)

    for i, item in enumerate(items):
        key = (item.run_id, item.tmdb_id)
        if key in labels:
            print(
                f"  [{i + 1}/{len(items)}] skip (cached) {item.run_id} · {item.title}",
                file=sys.stderr,
            )
            continue
        print(f"  [{i + 1}/{len(items)}] {item.run_id} · {item.title}", file=sys.stderr)
        if args.dry_run:
            continue
        score, rtype, rationale, causal_test = call_editor_label(
            item, provider=args.provider
        )
        validate_score_type_pair(score, rtype)
        labels[key] = FreshLabel(
            run_id=item.run_id,
            tmdb_id=item.tmdb_id,
            title=item.title,
            score=score,
            resonance_type=rtype,
            causal_test=causal_test,
            rationale=rationale,
            labeled_at=datetime.now(UTC).isoformat(),
            source="llm",
        )
        audit = {
            "eval_phase": "3.10.7",
            "rubric": "dual-axis v2 (docs/eval-the-bet.md §4)",
            "holdout_run_ids": holdout_ids,
            "prescreen_pool": len(label_keys),
            "labeled_at": datetime.now(UTC).isoformat(),
            "count": len(labels),
            "labels": [asdict(v) for v in labels.values()],
        }
        audit_path.write_text(
            json.dumps(audit, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        if args.delay > 0 and i + 1 < len(items):
            time.sleep(args.delay)

    if args.dry_run:
        print("dry-run complete", file=sys.stderr)
        return 0

    missing = [k for k in label_keys if k not in labels]
    if missing:
        print(f"ERROR: {len(missing)} missing labels", file=sys.stderr)
        return 1

    review_text = _update_rubric_header(review_path.read_text(encoding="utf-8"))
    if args.human:
        review_path.write_text(
            _apply_labels_to_review(review_text, labels, human_fields=True),
            encoding="utf-8",
        )
    print(f"wrote {audit_path} ({len(labels)} labels)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
