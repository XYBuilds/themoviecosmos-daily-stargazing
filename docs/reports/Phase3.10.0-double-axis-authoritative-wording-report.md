# Phase 3.10.0 - 双轴定义权威措辞源 + CONTEXT 对齐 交付报告

> 对应计划：`.cursor/plans/Phase3.10-logic-resonance-and-judge-prescreen.plan.md` · Todo 3.10.0
> 决策依据：[ADR-0007](../adr/0007-logic-resonance-judge-prescreen-and-pov-focalization.md) D1（共振重定义为「表层元素 + 底层逻辑」双轴）
> 分支：`feat/phase3.10.0-double-axis-authoritative-wording`（检出自最新 `main`，无继承关系）

## 1. 改动范围 (Scope)

- **新建** `prompts/_shared/resonance_definition_v2.md`：双轴定义的**唯一权威措辞源**（含 judge-ready / rubric-ready 两份逐字粘贴成稿、3.10.1/3.10.2 待改清单、硬性传播契约）。
- **修改** `CONTEXT.md`：「共振 (Resonance)」条目改为双轴口径，并补齐 5 个术语（表层元素 / 底层逻辑 / POV 不变因果引擎 / judge 预筛 / 拒绝集抽审；含因果反测句）。
- **本步状态标记**：`.cursor/plans/Phase3.10-logic-resonance-and-judge-prescreen.plan.md`，frontmatter `p310-0` 由 `status: todo` 改为 `status: complete`，正文 Todo 3.10.0 `### 验收` 三项 `- [ ]` 改为 `- [x]`。
- **本报告**：`docs/reports/Phase3.10.0-double-axis-authoritative-wording-report.md`（本文件）。
- **新增/删除依赖**：无。

> 代码改动（`scripts/llm_judge.py`、`scripts/resonance_rubric.py`、`docs/eval-the-bet.md`）按计划**不在本 TODO 落地**，已在权威措辞源 §4「待改清单」记账，交由 3.10.1 / 3.10.2 机械传播。

## 2. 技术实现 (Implementation)

### 双轴定义（ADR-0007 D1）

共振按 **2×2 矩阵**评分（0/1/2），两轴相互独立，分数 = 成立的轴数：

- **第一轴 · 表层元素**：新闻与电影共享一个**具体、可命名且承重**的元素（地点 / 职业 / 事件类型 / 设定题材）。**0 分守门**：换一条无关新闻若同样能配上则不承重。**归属铁律**：抽象权力角色配对（权威↔受害者、领袖↔团队）不算表层元素，归底层逻辑轴。
- **第二轴 · 底层逻辑**（替换旧「结构性共振 / 骨架同构」）：新闻与电影**实例化同一个因果-赌注引擎**，且该引擎在 **POV（视角）/ 尺度变换下不变**。引擎是一句 **「X 在约束 Z 下驱动 Y」**——机构尺度↔个人尺度只要同一句引擎仍算逻辑共振。
- **可证伪因果反测句**（防给分膨胀）：必须能写出一句两边都字面成立的「X 在约束 Z 下驱动 Y」；写不出 ⇒ 不算逻辑共振，退回 0/1。
- **2×2 措辞迁移**（矩阵不变只换措辞）：`结构性共振 → 逻辑共振`、`深层共振（仅结构，无表层）→ 深层共振（仅逻辑，无表层）`、`强共振（表层 + 结构）→ 强共振（表层 + 逻辑）`。

### 两份成稿（让下游变纯粘贴）

- **judge-ready 段**（§2，英文）：直接替换 `scripts/llm_judge.py` 的 `_JUDGE_SYSTEM` / `_JUDGE_RUBRIC`，含 Step1（表层 + 0 分守门）/ Step2（POV/尺度不变因果引擎）决策树、强制因果反测句、JSON schema（新增 `causal_test` 必填字段）。
- **rubric-ready 段**（§3，中文）：直接替换 `docs/eval-the-bet.md` §4 的两层定义、2×2 表与共振类型标注示例，并连带同步 §5.1 第 2 条枚举措辞。

### 设计升级 · 因果反测句落为 schema 必填字段

总编认可：因果反测句不只是 rationale 自由文本，而是落为 judge 输出的**必填字段 `causal_test`**——即第二轴的「X 在约束 Z 下驱动 Y」双向映射句。校验口径：`score == 2` ⇒ `causal_test` 非空；`resonance_type == 深层共振（仅逻辑，无表层）` ⇒ `causal_test` 非空。该解析/断言为代码改动，在 3.10.1 落地。

### 传播契约（硬性）

权威措辞源声明：3.10.1（judge prompt）/ 3.10.2（rubric 文档）**只逐字粘贴**对应成稿，禁止各自改写。三处同源是防止「judge 与人类按不同尺子打分」（重蹈 3.9 的 14 例分歧）的硬性约束；如需调整措辞，须先改本权威源再向下游重新传播。

## 3. 本地验证结果 (Verification)

本 TODO 为措辞/文档源 + 契约对齐，未改动运行时代码；执行回归确认对既有 judge / rubric / summarize 测试无破坏：

```text
> python -m unittest tests.test_llm_judge tests.test_resonance_rubric tests.test_summarize_eval
................................
----------------------------------------------------------------------
Ran 32 tests in 0.710s

OK
```

32 tests OK，无 regression。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

### 3.10.1 待办（随权威措辞同步的代码改动）

- **(a) `scripts/resonance_rubric.py` TYPE_* 常量改名**（结构 → 逻辑措辞）：`TYPE_DEEP` → `"深层共振（仅逻辑，无表层）"`、`TYPE_STRONG` → `"强共振（表层 + 逻辑）"`；`TYPE_SURFACE` / `TYPE_NONE` 不变。需确认 `_LEGACY_TO_CANONICAL` / 旧标注解析层不因 3.9 legacy 文本崩溃（ADR-0007 D2 已冻结 3.9 为不可比 legacy，无需回溯重写历史文件，仅保证脚本不崩）。
- **(b) `scripts/llm_judge.py` 新增 `causal_test` 必填字段的解析与校验**：`validate_judge_payload` 增字段；断言 `score == 2`（强共振）或 `resonance_type == 深层共振（仅逻辑，无表层）` ⇒ `causal_test` 非空；`JudgeResult` / `parse_judge_response` / `write_judge_markdown` / `format_judge_block_lines` / `load_judge_output` 一并补该字段读写；逐字粘贴 judge-ready 两段（还原单花括号 f-string 形态）。
- 配套单测：双轴 rubric 解析、`causal_test` 必填校验、score↔type 矩阵一致（新常量）。

### 跨 Phase 短暂不一致（plan 设计内）

- `CONTEXT.md`「共振」条目**已改双轴**，但 `docs/eval-the-bet.md` §4 仍是旧措辞（表层 + 结构性），须由 **3.10.2** 逐字粘贴 rubric-ready 成稿同步。此为 plan 拆分设计内的短暂不一致——权威源已定稿，下游传播为机械步骤。
