# Phase 7.2 - Daily Batch 编排器 + 断点续跑 交付报告

## 1. 改动范围 (Scope)

- 新增 `scripts/daily_batch.py`：Daily Batch 编排器，stage+persona 级断点续跑。
- 新增 `tests/test_daily_batch.py`：单元测试，覆盖初始化、正常执行、中断续跑、persona 级断点、slug 生成。
- 无新增/删除依赖包（复用现有 `scripts/main.py`、`scripts/heat_pool.py` 的下层函数与
  `scripts/lib/run_options.py::RunOptions`）。

## 2. 技术实现 (Implementation)

### 核心设计

- 编排器直接调用下层 stage 函数（`run_deconstruct` / `run_expansion` / `run_persona_pipeline` /
  `retrieve_from_agents` / `compose.run_review`），与 `main.py::run_daily_pipeline` 相同做法，
  不改动 `main.py` 任何一行。
- 断点粒度：item 级（`status == "done"` 直接跳过）+ stage 级（每个 stage 产物文件存在即跳过
  重跑，从磁盘加载）+ persona 级（`personas/{id}.json` 存在且 persona_id 已在
  `completed_personas` 中即跳过，只补跑剩余 persona）。
- Checkpoint 原子写：`_atomic_write_json` 先写 `.tmp` 再 `os.replace`，避免进程中断产出半截
  state 文件。

### 新增 API

- `BatchItemState` / `BatchState`（dataclass）：state 结构的 Python 表示，`to_dict/from_dict`
  与 `state/daily_batch_{date}.json` 的 JSON 结构一一对应。
- `slugify(title)`：title → lowercase → 去标点 → 取前 6 个词 → 连字符连接；空标题/纯标点回退
  为 `"untitled"`。
- `init_batch_state(date, pool, pool_file)`：从 heat_pool 的 ranked pool 构造全 `pending` 的
  初始 state。
- `run_daily_batch(*, date, resume, min_count, run_options, provider, out_dir, base_state_dir)`：
  顶层入口。非 resume 时调 `heat_pool.fetch_heat_pool()` 选题并落盘初始 state；resume 时从
  `state/daily_batch_{date}.json` 加载已有 state 和 `pool.json`，跳过 `done` 的 item。
- `_process_item(...)`：单条 news 的完整 stage 链，每个 stage / persona 完成后立即调
  `batch_state.save(state_file)` 落盘。

### 状态流转与产出目录

严格遵循 Plan 里定义的：

```
pending → deconstruct → expand → persona → retrieve → compose → done
```

产出目录 `output/daily_batch/{date}/{NN}-{slug}/`（`out_dir` 参数语义对齐
`heat_pool.pool_output_path`：`base = out_dir or repo_root()/output/daily_batch`，
`item_dir = base/date/{NN}-{slug}`，两者共享同一个 base 约定，方便测试用同一个临时目录
覆盖两者）。

### CLI

```
python scripts/daily_batch.py                      # 今天
python scripts/daily_batch.py --date 2026-07-05
python scripts/daily_batch.py --resume
python scripts/daily_batch.py --min-count 5
python scripts/daily_batch.py --personas 2
python scripts/daily_batch.py --skip-expand
```

## 3. 本地验证结果 (Verification)

```
python -m pytest tests/test_daily_batch.py -v
======================== 8 passed in 26.00s ========================
```

8 个测试全部通过，覆盖：
- `SlugifyTests` × 3：小写化 / 去标点 / 截词 / 空标题回退。
- `InitBatchStateTests` × 2：初始化结构正确 + dict 往返一致。
- `RunDailyBatchCheckpointTests` × 1：全量正常执行后所有 item 变为 `done`，checkpoint 文件
  和各阶段产物（deconstruct.json / retrieve.json / briefing.md / personas/*.json）均正确落盘。
- `ResumeAfterInterruptionTests` × 1（核心场景）：在 item 1 的第二个 persona 上模拟崩溃
  （`RuntimeError`），验证崩溃后 item 0 已 `done`、item 1 停在 `persona` 状态且只完成了
  `The-Hero`；resume 后只重跑剩余的 `The-Sage`，不重跑已完成的 item 0 和 item 1 的
  `The-Hero`，最终两条 item 都变为 `done`。
- `PersonaLevelCheckpointTests` × 1：手工构造一个"已完成 1 个 persona"的中间态 state +
  磁盘产物，resume 后只调用剩余 persona 的 pipeline，验证 persona 级断点独立于整体崩溃场景
  也能生效。

全仓库回归：

```
python -m pytest tests/ -q
8 failed, 307 passed, 1 skipped in 45.20s
```

8 个失败全部在 `tests/test_copywriter_review.py`（`copy_text` 属性缺失 / 中文字符串编码
乱码断言），与本次改动无关；已在 `main` 分支上单独验证同样的 8 个测试同样失败，确认是
Phase 7.2 之前就存在的问题，不属于本次改动引入的 regression。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `_process_item` 目前每条 item 串行执行（不并发跑多条 news），符合 Plan 里"逐条处理"的
  设计意图，但如果未来要支持并发批处理，需要重新设计 checkpoint 写入的并发安全性（当前
  `_atomic_write_json` 只保证单进程内的原子性，不是多进程/多协程安全）。
- persona 结果落盘的 `personas/{id}.json` 里存的是 `pipeline_result_to_dict()` 输出的
  `agent` 视图（而非完整的 `PersonaPipelineResult` 对象），resume 时直接把这个视图喂回
  `agents_list`。这个决定是为了避免序列化 `PersonaPipelineResult`（含 `AltPoolOverlay` /
  `PseudoSegment` 等 dataclass）的复杂度，但意味着如果后续 `retrieve_from_agents` 需要更多
  `PersonaPipelineResult` 特有字段（目前它只需要 `pseudos`/`search_units`/`fragment_ladders`/
  `warnings`），需要同步扩充落盘的 agent 视图。
- `_build_item_briefing` 是简化版 Markdown（不是 `main.py::build_daily_briefing` 的完整格式），
  因为 daily_batch 场景下是"一条 news 一个文件"而不是 main.py 的"单条 news 单份完整简报"。
  如果未来需要日批量的汇总简报（把 N 条 item 的候选拼成一份总览），需要新增一个汇总步骤，
  这不在本 Todo 范围内。
- 对 Phase 7.3（集成冒烟测试）无阻塞：`daily_batch.py` 的 CLI 参数（`--date` / `--resume` /
  `--min-count` / `--personas` / `--skip-expand`）已按 Plan 要求实现，可直接用于 7.3 的真实
  API smoke test。