# Phase 3.9.5 - persona batch concurrency 交付报告

## 1. 改动范围 (Scope)

- `scripts/run_persona_batch.py` — 并发 persona 生成、原序重组、抖动、429/超时退避、`--concurrency`、`--eval-phase 3.9`
- `tests/test_run_persona_batch.py` — 新增 11 项离线单测
- `.cursor/plans/Phase3.9-a1-oracle-per-persona-salience-three-bucket-eval.plan.md` — p39-5 标 complete

新增/删除的依赖包：无

## 2. 技术实现 (Implementation)

- **`_run_personas_concurrent`**：`asyncio.Semaphore(concurrency)` + `asyncio.gather` 并行跑 persona；每个任务启动前 `startup_jitter_seconds()`（5–15s 均匀随机）错开到达。
- **`reorder_persona_agents`**：并发完成后按 `persona_ids` 原序重组 `agents[]`（3.7 仍前置 A1 baseline），保证 `retrieve.json` 稳定可复现。
- **`run_persona_for_news`**：对 `run_persona_pipeline` 返回的 429/timeout 类错误做指数退避重试（初始 2s，最多 4 次）；`with_llm_backoff` 供抛出型 LLM 错误复用。
- **CLI**：`--concurrency`（默认 3）；`--eval-phase 3.9` 只读 phase3.8 decon+expansion，写 `output/Eval/phase3.9/{run_id}/`（含 `_copy_phase38_static`）。
- **run 间串行**：`run_batch` 仍 `for run_id` 顺序执行各新闻 run。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_run_persona_batch -v
# Ran 11 tests in ~0.5s — OK
```

覆盖：原序重组、单 persona 失败隔离、pipeline 429 退避、`with_llm_backoff`、jitter 边界、`is_retryable_llm_error`。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 并发=3 + 5–15s 抖动为保守起点；大批量跑前建议小样实测 LLM 配额。
- `3.9` 依赖 phase3.8 已产出 decon+expansion；未改 A0/扩展 pass。
- 对后续 3.9.6 pilot / 3.9.7 批量：可直接 `--eval-phase 3.9 --concurrency 3` 加速 12 persona 生成。
