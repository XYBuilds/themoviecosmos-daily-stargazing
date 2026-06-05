# Phase 3.8.1 - A0 verbatim + objective expansion pass 交付报告

## 1. 改动范围 (Scope)

- `prompts/A0_reality_deconstructor.md` — P-Extract 纯逐字抽取、英进英出、禁止 inert/hypernym
- `scripts/deconstruct.py` — 校验/剥离 inert 字段；英文 system message；markdown 视图瘦身
- `prompts/_shared/objective_expansion_contract.md` — **新增** P-Expand 共享契约
- `scripts/objective_expansion.py` — **新增** 客观扩展 pass CLI + 试金石过滤
- `tests/test_deconstruct_expansion.py` — **新增** A0 + 扩展单测
- `tests/fixtures/01-grid-outage-deconstructed.json` — v2 verbatim 英文 fixture
- `tests/fixtures/india-heatwave-deconstructed.json` — v2 verbatim 英文 fixture
- `tests/fixtures/slum-expansion-sample.json` — **新增** 试金石正负例 fixture
- `.cursor/plans/Phase3.8-objective-extraction-neutral-channel.plan.md` — 3.8.1 标 complete

无新增依赖包。

## 2. 技术实现 (Implementation)

- **A0（P-Extract）**：prompt 与 `validate_deconstruction` 对齐 ADR-0005 / contract v2；拒绝 `tags`/`geocode`/`coordinates`/`scale`/`scene_archetype`/`hypernym`；`strip_inert_fields` 在 LLM 返回后兜底剥离。
- **P-Expand**：`scripts/objective_expansion.py` 读取 A0 JSON → 渲染 `objective_expansion_contract.md` → LLM → `reality-expanded.json`；`passes_objectivity_touchstone` / `filter_hypernyms` 实现「A2&A4 不吵」启发式闸（保留 `slum`/`Mumbai`，拒绝 `destiny's cage`/`宿命的牢笼`）。
- **稳定 element id**：`who-{i}` / `where-{i}` / `why-{i}` / `how-{i}` / `result-{i}`，与 SSOT 一致。

## 3. 本地验证结果 (Verification)

```text
python -m unittest tests.test_deconstruct_expansion tests.test_retrieve_multi_pseudo tests.test_retrieve_quality tests.test_summarize_eval -v
# Ran 25 tests — OK (8 × 3.8.1 + 17 regression)

python tests/test_agents_p35.py
# test_agents_p35 OK (fixture 英文迁移后 agents 离线用例通过)
```

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 试金石为**启发式子串闸**，非 LLM 二次裁决；3.8.6 pilot 人工审计仍必要。
- `personas.py` / `retrieve.py` **未改**（留给 3.8.2+）。
- `tests/test_personas.py` 中 `list_persona_ids` 因 `personas-12.md` 重复行报 24 id（既有债，非本 TODO 引入）。
