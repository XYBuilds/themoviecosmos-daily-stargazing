# Phase 3.9.6 - Single-point pilot + firewall audit 交付报告

## 1. 改动范围 (Scope)

- `scripts/personas.py` — surface sentence dedup in neutral body; option B diversity guard (hard-fail only when neutral **and** toned collide; neutral-only ⇒ warning)
- `scripts/run_persona_batch.py` — wire option B guard semantics into post-batch diversity check
- `tests/test_personas.py` — dedup + option B guard tests (neutral-only tolerance, neutral+toned hard-fail)
- `output/Eval/phase3.9/01-grid-outage/` — pilot rerun artifacts (`agents.json`, 12 × persona pipelines, `retrieve.json`, `pilot-notes.md`, `batch-run-meta.json`)
- `docs/adr/0006-a1-as-held-out-oracle-per-persona-neutral-and-three-bucket-eval.md` — option B guard + surface dedup semantics
- `CONTEXT.md` — `neutral diversity guard` glossary entry
- `.cursor/plans/Phase3.9-a1-oracle-per-persona-salience-three-bucket-eval.plan.md` — p39-6 marked complete
- 新增/删除的依赖包：无

**分支：** `feat/phase3.9.6-single-pilot`（基于 `main` @ PR #44 合并后）

**分支继承：** 首跑产物在 `0129e89` / `66037c6`；调试会话追加 dedup + option B 修复后全量 rerun 覆盖同目录 `01-grid-outage/`。

## 2. 技术实现 (Implementation)

### Code fixes (debug session)

1. **Surface sentence dedup** — `build_objective_floor_neutral_pseudo` deduplicates by normalized surface text so shared why/how fragments (e.g. Sage Kepco trip sentence) render once.
2. **Option B diversity guard** — `check_neutral_diversity_guard` hard-fails only when a persona pair has near-duplicate **both** neutral and toned pseudos; neutral-only collision logs warning and continues (toned + retrieval differentiate). No extra human gate — automatic per user approval.
3. **Batch wiring** — `run_persona_batch.py` invokes guard after all personas complete for eval-phase 3.9.

### Pilot rerun (`01-grid-outage`)

- **Pipeline:** phase3.8 decon+expansion (read-only) → 12 persona salience neutral+toned → retrieve with A1 held-out oracle (`retrieve-a1.json`)
- **Result:** 12/12 agents, 19 candidates, 0 errors
- **First pass:** 10/12 OK; Innocent lens guard + Ruler alt_creator parse error → retried both with `--no-skip-existing` → all 12 finalized

### Firewall audit (pilot-notes.md)

| Check | Result |
| --- | --- |
| 12/12 unique neutral fragment sets | **PASS** |
| salience≠valence (surface+hypernym only) | **PASS** |
| Option B diversity guard | **PASS** — 0 hard failures, 0 neutral-only warnings; mean n1 sim **0.391**, max **0.790** (Caregiver/Innocent) |
| Surface dedup (Sage) | **PASS** |
| Toned hypernym anchor | **PASS** |
| A1 not polluting candidates | **PASS** — 0 A1 rows in `agents.json` |

### Immutability

- `output/Eval/phase3.6`, `phase3.7`, `phase3.8` — not modified (read-only inputs)

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_personas tests.test_run_persona_batch -v
# Ran 53 tests in ~15s — OK (42 persona + 11 batch)
```

Pilot rerun stats (`batch-run-meta.json`):

- `persona_count`: 12
- `candidate_count`: 19
- `errors`: []
- `a1_parallel.candidate_count`: 0 (oracle isolated in `retrieve-a1.json`)

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **Embedding crowding persists** — `query_cosines` mean ≈ 0.84; toned legs differentiate retrieval (`topk_jaccard` mean ≈ 0.22, 0 pairs with jaccard = 1.0). Not a blocker for 3.9.7.
- **Option B is automatic** — neutral-only near-duplicate pairs emit warnings only; no human gate on guard behavior (user-approved).
- **3.9.7 next** — bulk run (obs 01–04 / holdout 05–10) × 12 persona with A1 oracle parallel, holdout freeze discipline, longitudinal scoring (human + judge).

**Go/No-Go:** User approved Combined Go → ready for **3.9.7**.
