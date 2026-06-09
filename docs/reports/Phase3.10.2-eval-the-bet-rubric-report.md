# Phase 3.10.2 - eval-the-bet rubric 交付报告

## 1. 改动范围 (Scope)

- `docs/eval-the-bet.md` — §4 共振 rubric 双轴化（逐字粘贴 `prompts/_shared/resonance_definition_v2.md` §3 rubric-ready）；§5.1 第 2 条共振类型枚举措辞同步
- `.cursor/plans/Phase3.10-logic-resonance-and-judge-prescreen.plan.md` — p310-2 标 complete
- 新增/删除的依赖包：无

## 2. 技术实现 (Implementation)

- **传播契约**：从 3.10.0 权威措辞源 `prompts/_shared/resonance_definition_v2.md` §3 rubric-ready **逐字**替换 `docs/eval-the-bet.md` §4 的两层定义、2×2 表与共振类型标注示例
- **双轴措辞**：`表层共振/结构性共振` → `第一轴·表层元素/第二轴·底层逻辑`；表头 `承重表层锚点|骨架同构` → `表层元素|底层逻辑`
- **共振类型迁移**：`深层共振（仅结构，无表层）` → `深层共振（仅逻辑，无表层）`；`强共振（表层 + 结构）` → `强共振（表层 + 逻辑）`
- **连带同步**：§5.1 第 2 条枚举同步新措辞；judge 输出说明增 `causal_test`（因果反测句）
- **归属规则**：§4 末尾 `(新闻, tmdb_id)` 单次打分 / `triggered_by` 桶 / baseline-only 规则 **未改动**

## 3. 本地验证结果 (Verification)

```text
python -m unittest discover -s tests -p "test_*.py" -v
Ran 159 tests in 17.541s
OK (skipped=1)
```

- §4 措辞与 `resonance_definition_v2.md` rubric-ready 逐字一致（人工 diff 核对）
- 2×2 映射与共振类型示例已更新

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- `summarize_eval.py` / `score_eval_candidates.py` 仍引用旧「仅结构」常量解析 legacy 标注（3.10.1 已在 `resonance_rubric.py` 更新常量；3.10.3 将砍 Q1'/A1 闸并收敛成功标准）
- 3.9 及更早人工标注的 `共振类型` 文本为 legacy 措辞，ADR-0007 D2 已冻结不可比；脚本通过 `_LEGACY_TO_CANONICAL` 兼容解析
- 下游 3.10.5 obs 鲜标须按新 rubric 重新打分，勿参考旧分
