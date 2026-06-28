# 命名收敛重构 #2（agents.py 死流程清理 · A 方案）交付报告

## 1. 改动范围 (Scope)

- 修改 `tests/test_agents_p35.py`：删除 11 行——移除死测试 `test_render_prompt`，并从 import 块移除仅该测试独占的 `load_personas` / `render_prompt` 两个名字，删除 `__main__` 块内对应的调用行。
- 无其它源码改动：`scripts/agents.py` / `scripts/retrieve.py` / `scripts/run_eval.py` 均未改动。
- 无新增 / 删除依赖。

## 2. 技术实现 (Implementation)

**为什么删 `test_render_prompt`**：该测试通过 `load_personas` 加载 A1/A2/A4/A7 persona prompt，再走 `render_prompt`。但这些 prompt 文件在磁盘上已不存在——`load_personas` 测的是 ADR-0011 已废弃的「多 agent pseudos」路径残留的死功能。测试因依赖不存在的文件而恒定失败（基线那条唯一 failed 即此），是一条无价值的死测试。

**为什么「整条删」而非 `skip` / `xfail`**：死功能应当移除而非掩盖。`skip`/`xfail` 只会把一条已无对应能力的测试长期挂在套件里，掩盖问题、积累噪音；既然被测能力已废弃，正确做法是连同测试一并删除。

**为什么 import 块只移除 `load_personas` / `render_prompt`**：核查后确认这两个名字仅被 `test_render_prompt` 独占引用；import 块里其余名字仍被本文件的活跃用例共享，必须保留。因此只精准摘除这两个失效引用，避免误伤其它绿测试。

**本轮明确未动 `agents.py` / `retrieve.py` / `run_eval.py` 源码**：A 方案为最小安全方案。`agents.py` 中 `run_all` / `RUN_ORDER` / `agent_to_dict` 等符号仍被 `run_eval` 评测链活跃 `import`，此刻删除会直接破坏 import 链并打挂既有绿测试。故本轮只清理已彻底失活的测试，源码侧的 pseudos 死代码留待后续评测链重构再处理（见第 4 节）。

## 3. 本地验证结果 (Verification)

- 单文件：`pytest tests/test_agents_p35.py -q` → 9 passed。
- 全量：`pytest tests/ -q` → 228 passed / 1 skipped / 0 failed。对比基线（删除前）的那条唯一 `1 failed`（即 `test_render_prompt`）已消失，passed 数量不减，无新增失败。
- import 健康：`python -c "import scripts.run_eval"` → 成功（确认未破坏评测入口的 import 链）。
- golden 不适用：本轮零生产逻辑改动（仅删一条死测试），不涉及产物比对。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

- **pseudos 死代码路径保留未清**：`agents.py` 的 `PERSONA_FILENAMES` 中 A2/A4/A7 的死引用、以及 `load_personas` / `run_all` 等符号本轮**刻意保留**，原因是它们仍被 `run_eval` 评测链活跃依赖。要彻底清除，须先改造 `run_eval` 的 agents→retrieve 评测链——属更大范围的重构，已记为后续待办，不在本轮 A 方案范围内。
- **与 #1 的串行依赖**：后续命名收敛 #1（JSON 产物改名）与本项在 `run_eval.py` / `retrieve.py` 上存在改动重叠，二者必须串行——本项（#2）合入 `main` 后再启动 #1，避免冲突。
- **计划状态标记**：本轮未在 `.cursor/plans` 中定位到与本 TODO 明确对应的计划条目，故未改动任何 plan 文件；状态标记由用户 / 后续处理，此处仅作记录说明。