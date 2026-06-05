# Phase 3.8.3 - retrieve.py 撞车口径改造 + neutral_hit_rate 交付报告

## 1. 改动范围 (Scope)

- `scripts/retrieve.py` — 中性 union 撞车票、channel_role 解析、neutral_hit_rate 字段
- `tests/test_retrieve_neutral_collision.py` — 新增 3.8.3 专项单测
- `tests/test_retrieve_quality.py` — 更新 quality 判据断言
- `tests/test_retrieve_multi_pseudo.py` — 更新 toned/neutral 通道断言
- `.cursor/plans/Phase3.8-objective-extraction-neutral-channel.plan.md` — 3.8.3 标记 complete

无新增依赖包。

## 2. 技术实现 (Implementation)

- **`_resolve_channel_role`**：从 pseudo `source.channel_role` 解析 `neutral` / `toned`；A1 保留 `baseline` 并跑路径；legacy `creative` 映射为 `toned`。
- **撞车主判据（ADR-0005）**：`quality_candidate = neutral_vote（≥1 中性 pseudo 过 floor） AND toned_converge（≥1 toned agent 过 floor）`；12 条中性撞同片只贡献 1 张 union 票，不再对称计 `distinct_agents>=2`。
- **新候选字段**：`neutral_hits`（过 floor 的中性 pseudo 数）、`neutral_total`（运行 persona 数）、`neutral_hit_rate = neutral_hits / neutral_total`；命中口径复用 `top_k=2` + `quality_floor=0.40`。
- **`distinct_agents`**：现为 toned agent 计数（供下游过渡）；`triggered_by` 仅含 toned 通道。

## 3. 本地验证结果 (Verification)

```text
python -m unittest discover -s tests -q
Ran 81 tests in 2.074s
OK (skipped=1)

python -m unittest tests.test_retrieve_neutral_collision tests.test_retrieve_quality tests.test_retrieve_multi_pseudo -v
Ran 16 tests — OK
```

关键用例：
- 12 neutrals → 同片 `neutral_hits=12`、`neutral_hit_rate=1.0`、`quality_candidate=False`
- +1 toned 汇聚 → `quality_candidate=True`
- 6/12 中性过 floor → `neutral_hit_rate=0.5`

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `score_eval_candidates.py` / `summarize_eval.py` 仍读旧 `distinct_agents` 语义 — **3.8.4** 需改双诊断与闸门 2。
- 无 `channel_role` 的 legacy payload 将 agent 默认视为 `toned`（A1 仍为 `baseline`）；3.8.7 A1 并跑对照不受影响。
- `neutral_hit_rate` 为诊断字段，分析前须控 `max_similarity`（ADR-0005 纪律）。
