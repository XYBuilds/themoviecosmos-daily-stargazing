# Phase 3.12.7 - 文档回填 交付报告

## 1. 改动范围 (Scope)

- 修改 `docs/adr/0009-fragment-ladder-and-search-unit-architecture.md`：「后果/已知局限」+「SSOT 待同步」两段按 3.12 落地结果更新。
- 修改 `docs/SSOT/电影宇宙「每日星轨观测」系统 PRD.md`：§10 项目结构树移除已删文件、补入新模块。
- 修改 `.cursor/plans/Phase3.12-code-doc-sync.plan.md`：3.12.7 标记 completed。
- 无代码改动，无依赖变更。

> **分支继承关系**：在 stacked 分支 `feat/phase3.12.5-eval-consumer-alignment` 上完成（3.12.1→…→3.12.6 同链）。

## 2. 技术实现 (Implementation)

文档回填三处，使文档与 3.12 代码现状一致：

**ADR-0009「后果/已知局限」**：原列三条 future-work（channel 仅兼容层 / screenwriter 仍返回 pseudos / objective 靠外部 pass）。逐条更新为已落地状态：
- channel 分支已在 3.12.4/3.12.5 从运行时彻底移除，仅历史 eval 产物保留为静态记录。
- screenwriter 契约已在 3.12.3 原生改 `search_units[]`，`pseudos[]` 降为 news-writer 兼容层与历史回放路径。
- objective 能力已在 3.12.1 内联进 `fragment_ladder.py`，独立 pass + contract + `reality-expanded.json` 产物删除。
- 新增 3.12.6 等价性验证结论（N=10 全 bit-parity）作为重构无副作用的佐证。

**ADR-0009「SSOT 待同步」→「SSOT 落地处」**：标题改名（代码已对齐，不再是"待同步"），逐条标注落地 TODO 编号，补入 `scripts/fragment_ladder.py`。

**PRD §10 项目结构树**：
- `prompts/_shared/` 移除 `objective_expansion_contract.md`。
- `scripts/` 移除 `objective_expansion.py`，补入 `fragment_ladder.py`（含内联 objective 生成 + 客观性试金石说明）。

**`docs/temp` 残留清理**：核查后确认活 SSOT 文档（`simplified-news-to-film-workflow.md` / `reality-deconstruction-contract.md`）已无指向 `docs/temp/` 的 propagation 引用，相关能力已正确标注被 ADR-0009 取代。剩余 `docs/temp` 字样仅存在于历史 plan 记录与 ADR-0010「已删除临时记录」说明中，属正确的历史归档，不修改。

## 3. 本地验证结果 (Verification)

纯文档改动。回归确认：

```
python -m unittest discover -s tests -p "test*.py"
Ran 194 tests in 18.196s
OK (skipped=1)
```

残留引用核查（`reality-expanded` / `objective_expansion` / `docs/temp`）：所有命中均落在历史交付报告（Phase3.8.x / 3.12.1 / 3.12.5）与历史 plan，均为正确的存档记录，无活文档误引。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- 历史交付报告（Phase3.8.x 等）仍提及已删除的 `objective_expansion.py` / `reality-expanded.json`，这是当时的真实交付记录，刻意保留不改。
- ADR-0009 仍存一条真实局限：hybrid recall 的 lexical / weighted ladder 子信号尚未完全展开，dense embedding 仍为召回底座——已在「后果」段标注「仍为局限」，留待后续 Phase。
- 至此 Phase 3.12 全部 7 个 TODO 完成。整个 stacked bundle（3.12.1~3.12.7）等待合并入 `main`。