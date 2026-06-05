# Phase 3.8.6.1 - screenwriter 契约/prompt 硬化 交付报告

## 1. 改动范围 (Scope)

- `prompts/_shared/persona_screenwriter_contract.md` — element_id vs fragment id 显式区分；带调句必嵌 hypernym 锚；高 lens persona 强调
- `scripts/personas.py` — `build_screenwriter_user_prompt` / `render_persona_prompt` / `run_screenwriter` 注入 `expansion_json`
- `tests/test_personas.py` — expansion 注入、element_id 负例、锚点正例
- `.cursor/plans/Phase3.8-objective-extraction-neutral-channel.plan.md` — 3.8.6.1 标 complete

## 2. 技术实现 (Implementation)

- Screenwriter prompt 新增 **Objective expansion** 区块，将 `expansion_json` 与 alt-pool 一并可见，消除「校验集 ⊃ prompt 可见词」不对称。
- 契约增加 id 对照表：`who-*`/`where-*` 仅用于 alt-pool element_id，禁止写入 `source.fragments`（仅 `why-*`/`how-*`/`result-*`）。
- 明确每条 toned pseudo 须 verbatim 嵌入 ≥1 pool/expansion hypernym；The-Hero / The-Lover / The-Jester 单独强调。
- `run_screenwriter` / `run_persona_pipeline` 将 expansion 传入 prompt 构建（为 3.8.6.2 repair 预留 `repair_context` 参数，本 TODO 未启用）。

## 3. 本地验证结果 (Verification)

```
python -m unittest tests.test_personas -v
# Ran 24 tests in 0.633s — OK
```

新增用例：`test_screenwriter_prompt_includes_expansion_hypernyms`、`test_parse_pseudos_rejects_element_ids_as_fragments`、`test_toned_with_hypernym_anchor_passes`。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- Repair/retry 与整句级 hypernym 过滤留待 3.8.6.2。
- 3.8.6 首跑 pilot 仍 pending 人工验收；本改动不自动标 3.8.6 complete。
