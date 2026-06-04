# Phase 3.7 eval output (`output/Eval/phase3.7`)

## Run layout

Each `run_id` matches [`tests/eval_news/batch-manifest.json`](../../tests/eval_news/batch-manifest.json):

| Split | run_ids | Scoring for gates |
| --- | --- | --- |
| **观察集 (observation)** | `01-grid-outage` … `04-celebrity-scandal` | Optional 共振分; **not** used for ADR-0004 gates |
| **留出集 (holdout)** | `05-climate-disaster` … `10-whistleblower-leak` | **Required** for 闸门 1/2 & P-Abstain (≥2 runs per review round) |

## Per-run artifacts

```
output/Eval/phase3.7/{run_id}/
  reality.json / reality-deconstructed.json   # copied from phase3.6 (read-only source)
  personas/{persona_id}/alt-pool-overlay.json
  personas/{persona_id}/persona-pipeline.json
  agents.json                                 # A1 + all persona agents
  retrieve.json
  candidates.md                               # 总编填 共振分 / 共振类型
  batch-run-meta.json
```

**Do not modify** `output/Eval/phase3.5/` or `phase3.6/`.

## Batch driver

```bash
python scripts/run_persona_batch.py                    # all 10 × 12 personas
python scripts/run_persona_batch.py --holdout-only       # 05–10 only
python scripts/run_persona_batch.py --run-ids 05-climate-disaster --personas The-Sage
```

Neutral decon: read-only from `output/Eval/phase3.6/{run_id}/reality-deconstructed.json`.  
A1 baseline: pseudos reused from phase3.6 `retrieve.json` (same-run gate-2 comparison).

## Scoring

```bash
python scripts/score_eval_candidates.py --dir output/Eval/phase3.7 --review-out output/Eval/phase3.7/high-hit-score-review.md
```

Fill `共振分` / `共振类型` in each run's `candidates.md`. Holdout **05–10** is mandatory for 3.7.5; observation **01–04** optional.

## Completion matrix

See [`runs-completed-matrix.md`](runs-completed-matrix.md) and [`batch-run-summary.json`](batch-run-summary.json) for per-run errors (mostly alt-creator missing valence bucket). Re-run failed cells with:

```bash
python scripts/run_persona_batch.py --run-ids <run_id> --personas <persona_id> --no-skip-existing
```

## Pilot legacy (3.7.3)

`04-celebrity-scandal/` may still contain root-level `persona-pipeline.json` from the single-persona pilot. Batch re-runs use `personas/The-Ruler/`; pilot files are preserved for audit.
