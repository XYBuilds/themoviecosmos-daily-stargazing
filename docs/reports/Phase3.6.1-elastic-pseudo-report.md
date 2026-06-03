# Phase 3.6.1 - 弹性 pseudo（D4-1）交付报告

## 1. 改动范围 (Scope)

- `scripts/agents.py`：`parse_pseudos_response` 接受 1–3 段；`MIN_PSEUDO_COUNT` / `MAX_PSEUDO_COUNT` / `VALID_PSEUDO_IDS`；移除「恰好 3 / missing ids」硬校验；保留 fragment / how 连续性校验
- `prompts/_shared/multi_pseudo_output_contract.md`：`exactly 3` → **up to 3（1–3）**；低适配宁可少写
- `prompts/A1_reality_recorder.md`、`A2_sociologist.md`、`A4_mythologist.md`、`A7_chaos_theorist.md`：数量契约改为 1–3（A1 baseline/control 顶部文案保留）
- `scripts/run_eval.py`：agent markdown 标题 `3 pseudos` → `1–3 pseudos`
- `tests/test_agents_p35.py`：1/2/3 段解析、0 段/重复 id/非法 fragment/超 3 段/非法 id 负例
- 无新增依赖包

## 2. 技术实现 (Implementation)

- **解析**：`len(pseudos)` 须在 `[1, 3]`；`id ∈ {p1,p2,p3}` 且唯一；不再要求必须出现 p2/p3
- **校验不变**：未知 fragment id、重复 id、空 text、how-* 非连续（修复失败时仍报错）
- **契约**：共享 `multi_pseudo_output_contract.md` 与四路 A* prompt、`run_eval` 展示文案与 ADR D4「选择优先、宁可少写」一致
- **兼容**：保留 `EXPECTED_PSEUDO_COUNT` / `EXPECTED_PSEUDO_IDS` 别名指向上限与合法 id 集合

## 3. 本地验证结果 (Verification)

```text
$ python tests/test_agents_p35.py
test_agents_p35 OK
```

覆盖：1/2/3 段 JSON 解析成功；0 段、>3 段、重复 id、未知 fragment、非法 id 均 `ValueError`。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **retrieve / eval**：单 agent 候选数可能少于 4×3；3.6.2 质量地板与 containment 需在新数量分布下验证
- **历史 Eval 产物**：`output/Eval/*/agents/*.md` 标题仍为旧「3 pseudos」，重跑 3.6.5 后自然更新
- **how 修复**：非连续 how-* 仍可能自动扩 span 并打 warning，非硬错（与 3.5 行为一致）
- **下游**：3.6.2 应从合并后的 `main` 检出 `feat/phase3.6.2-*`
