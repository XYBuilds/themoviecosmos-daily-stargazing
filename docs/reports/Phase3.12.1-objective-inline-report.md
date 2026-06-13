# Phase 3.12.1 - objective 能力内联 交付报告

## 1. 改动范围 (Scope)

改动文件：

- `scripts/fragment_ladder.py`（**新增**）：承载内联后的客观展开能力。
- `scripts/objective_expansion.py`（**删除**）：原独立 P-Expand pass 文件。
- `prompts/_shared/objective_expansion_contract.md`（**删除**）：契约文本内联进新模块常量。
- `scripts/audit_phase38_pilot.py`（修改）：导入路径切到 `fragment_ladder`。
- `scripts/run_phase38_eval.py`（修改）：导入路径切到 `fragment_ladder`。
- `tests/test_deconstruct_expansion.py`（修改）：导入路径迁移 + 新增内联校验测试类。

依赖包：无新增/删除。

## 2. 技术实现 (Implementation)

执行前确认了一处计划内部歧义并与用户敲定方向（方案 A）：

- **数据结构与执行语义不变**：客观展开仍是「每条新闻跑一次」的 shared pass，对全部 12 个 persona 共享同一份 objective 输出。计划数据流图中「build_fragment_ladders 内联 objective 生成」按「消除独立 pass 文件这层结构」理解，而非「把 LLM 调用塞进逐 persona 的纯函数」（后者会造成 12× 成本回归并破坏 shared 语义、打不平 3.11.8 基线）。
- **模块关系演变**：原先 `personas.py`/测试/编排脚本都从 `scripts.objective_expansion` 取纯函数与 `run_expansion`；现在统一改为从 `scripts.fragment_ladder` 取。函数签名、行为、返回结构全部保持一致，仅文件边界迁移。
- **契约去文件化**：原 `.md` 契约文本作为模块常量内联，`load_expansion_contract()` 直接返回常量，不再读盘，消除对外部 `.md` 文件的运行时依赖。
- `build_fragment_ladders` 保持纯函数，继续接收 `expansion` 入参（这是方案 A 的直接含义；该入参在 personas.py 的进一步收敛属 3.12.2/3.12.5 范围）。

新增测试（`InlinedExpansionModuleTests`）：① 断言 `scripts.objective_expansion` 已不可导入；② 断言契约内联且外部 `.md` 不存在；③ 断言渲染提示自包含（无未替换占位符）。

## 3. 本地验证结果 (Verification)

- 导入冒烟：`scripts.fragment_ladder` / `audit_phase38_pilot` / `run_phase38_eval` 均 `IMPORTS_OK`。
- 全量测试：`python -m unittest discover -s tests -p "test*.py"` → `Ran 265 tests, OK (skipped=1)`（基线 262 + 新增 3，零 regression）。
- Lint：新增/改动文件无诊断。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **等价性验证范围**：本 TODO 仅做结构等价核验（单测全绿 + 产物 schema 不变）。完整 N=10 LLM 重算对比 3.11.8 基线留待 3.12.6（标 `[需人工验收]`），由用户手动触发，避免消耗 API 配额。
- **偏离计划字面一处**：`build_fragment_ladders` 未移除 `expansion` 入参（方案 A 选择），其入参收敛在后续 TODO 处理。
- **历史报告未改**：`docs/reports/Phase3.8.1-*.md` 等历史报告仍提及旧文件路径，属历史记录，不在本 TODO 回填范围（3.12.7 处理 SSOT/PRD）。