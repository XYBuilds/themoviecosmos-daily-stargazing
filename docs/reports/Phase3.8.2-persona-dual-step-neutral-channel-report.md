# Phase 3.8.2 - persona dual-step + neutral channel 交付报告

## 1. 改动范围 (Scope)

- `scripts/personas.py` — persona-relative valence 解析、`provenance` 三层、客观地板中性 pseudo 生成（`n1`）、`channel_role` neutral/toned、管道组装
- `prompts/_shared/persona_alt_creator_contract.md` — 三桶非强制、与 parser 对齐
- `prompts/_shared/persona_screenwriter_contract.md` — 中性 `n1` 由代码生成、toned 须 hypernym 锚
- `tests/test_personas.py` — provenance/中性通道/toned 锚校验；`list_persona_ids` 去重修复
- `.cursor/plans/Phase3.8-objective-extraction-neutral-channel.plan.md` — 3.8.2 标 complete

无新增依赖包。未改 `retrieve.py` / `score_eval`（留给 3.8.3/3.8.4）。

## 2. 技术实现 (Implementation)

- **`parse_alt_pool_response`**：不再强制 positive/neutral/negative 三桶齐全；解析可选 `provenance`（`surface`/`hypernym`/`lens`），省略时按 ADR-0005 默认（正/负 → lens）。
- **客观地板中性通道**：`build_objective_floor_neutral_pseudo` 从 alt-pool + expansion 仅取 surface/hypernym 组装 `n1`；`assemble_persona_channel_pseudos` 产出 `[neutral] + toned`，`source.channel_role` 标注 `neutral`/`toned`。
- **Toned 锚校验**：`validate_toned_hypernym_anchor` 要求每条 toned pseudo 文本含至少一个 pool/expansion hypernym。
- **`list_persona_ids`**：`dict.fromkeys` 去重 `personas-12.md` 双表重复行（24 → 12）。
- **`run_persona_pipeline`**：新增可选 `expansion` 入参，screenwriter 后自动组装双通道。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_personas -v
# Ran 21 tests — OK

python -m unittest tests.test_deconstruct_expansion tests.test_retrieve_multi_pseudo tests.test_retrieve_quality -v
# Ran 19 tests — OK (regression)
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 中性 pseudo 文本为**确定性拼装**（非 LLM），3.8.6 pilot 需人工核对碎片多样性与可读性。
- `retrieve.py` 尚未消费 `channel_role`；撞车新口径与 `neutral_hit_rate` 在 3.8.3 落地。
- `run_persona_batch.py` 仍标 `role: creative`；批量 runner 接 expansion + 双通道编排可后续补齐（3.8.5/3.8.7）。
