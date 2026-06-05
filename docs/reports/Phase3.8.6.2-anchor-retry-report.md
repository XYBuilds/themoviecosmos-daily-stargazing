# Phase 3.8.6.2 - anchor set robustness + repair retry 交付报告

## 1. 改动范围 (Scope)

- `scripts/personas.py` — `_is_phrase_level_hypernym_anchor`；`collect_hypernym_anchor_terms` 过滤整句级 hypernym；`run_persona_pipeline` 一次 repair/retry；`PersonaPipelineResult.repair_retries`
- `scripts/run_phase38_eval.py` — `phase38-run-meta.json` 聚合 `repair_retries` / `repair_retry_count`
- `tests/test_personas.py` — 整句排除、parse/assembly repair mock、仍失败路径
- `.cursor/plans/Phase3.8-objective-extraction-neutral-channel.plan.md` — 3.8.6.2 标 complete

## 2. 技术实现 (Implementation)

- **锚点集启发式**（文档化常量）：剔除句末 `.`、词数 > 6、长度 > 60 的 hypernym，只保留短语级可嵌锚词。
- **一次 repair turn**：parse 失败 → 携错误重问 screenwriter 一次；若首轮 parse 成功但 `channel_assembly` 锚点失败且尚未 repair → 再携 assembly 错误重问一次（总计最多 1 次额外 LLM 调用）。
- **meta**：`persona-pipeline.json` 写入 `repair_retries`；`run_phase38_eval` 汇总至 `phase38-run-meta.json`。

## 3. 本地验证结果 (Verification)

```
python -m unittest tests.test_personas -v
# Ran 28 tests in 0.878s — OK
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 整句过滤为启发式，极端长短语可能仍漏网；未放宽 `validate_toned_hypernym_anchor`。
- 3.8.6.3 pilot rerun 将验证真实 LLM 合规率提升。
