# Phase 3.11.0 - ADR-0008 权威措辞源 + 注意力清单 + CONTEXT 对齐 交付报告

> 对应计划：`.cursor/plans/Phase3.11-pov-focalization-additive.plan.md` · Todo 3.11.0
> 决策依据：[ADR-0008](../adr/0008-salience-driven-element-composition-and-multi-vantage-pov.md) D1–D5（注意力清单 / 轴对齐 / 元素中心构图 / 多视角 POV / 双地板）
> 分支：`feat/phase3.11.0-adr8-wording-source`（检出自已合入 ADR-0008 的 `main` @ `5cbfbe8`；前置决策层 PR #59）
> 人工验收：总编 `approve`（2026-06-11）

## 1. 改动范围 (Scope)

- **修改** `prompts/_shared/persona_screenwriter_contract.md`：P-Select 改**轴对齐**措辞；新增 §Element-centered composition & POV focalization（唯一规则权威源）——贪心声明式中心构图、多视角 POV 派生、双地板、composition mode 响应字段（`center`/`channel`/`focal`）、激活护栏（`Composition mode: ADR-0008` 标记，3.11.2 接线前运行时零变化）、传播契约。
- **修改** `prompts/_shared/persona_alt_creator_contract.md`：valence 降级为元素层**可选**着色标注；废止逐元素正中负光谱覆盖期待；salience 输出机制未动。
- **修改** `prompts/personas/*/persona_card.md`（12 张）：价值轴段加「注意力清单 / 视角座位」标注（Who 正极 = 共情座位；负极 = 被审视对象不作座位）。
- **修改** `CONTEXT.md`：补 8 条术语（注意力清单 / 轴对齐 / 元素中心构图・中心元素 / POV 聚焦・多视角派生 / 双地板 / 候选漏斗 / A/B 池差）。
- **本步状态标记**：`.cursor/plans/Phase3.11-pov-focalization-additive.plan.md`，frontmatter `p311-0` → `complete`，Todo 3.11.0 `### 验收` 四项 → `[x]`，Phase 整体验收首项 → `[x]`。
- **本报告**：`docs/reports/Phase3.11.0-adr8-authoritative-wording-report.md`（本文件）。
- **新增/删除依赖**：无。

> 代码改动（`scripts/personas.py` 中心声明解析、focalized 通道接线、provenance 标签、守卫、检索漏斗）按计划**不在本 TODO 落地**，交由 3.11.2–3.11.4 机械接线。

### 分支继承关系

| 分支 | 状态 | 说明 |
| --- | --- | --- |
| `feat/phase3.11-adr8-redesign` | 已合入 main（PR #59） | 决策层：ADR-0008 + plan 改写 |
| `feat/phase3.11.0-pov-wording-source` @ `834e788` | **搁置** | v1 单视角措辞（12 行 canonical 表），按 ADR-0008 作废，留考古 |
| `feat/phase3.11.0-adr8-wording-source` | 本交付 | 3.11.0 重做，基于 ADR-0008 口径 |

## 2. 技术实现 (Implementation)

### 轴对齐 P-Select（ADR-0008 D2）

- 删除旧引导 "prefer alternatives that match this persona's value tendency"（易被误读为整条 pseudo 单向倾斜）。
- 新引导：逐元素透过价值轴框定；**pseudo 层无极性**；两极同场张力欢迎（含 Ruler authority(+) × ungoverned zone(−) 原型故事例证）。

### 元素中心构图（ADR-0008 D3）

- 每条 toned/focalized pseudo 声明 **1 个中心元素 id** + 2–4 支撑元素。
- 中心按注入 `salience` **自上而下贪心**取、各条互异；**LLM 只声明，排序/预算由代码**（3.11.2 接线）。
- 激活护栏：`Composition mode: ADR-0008` 标记未注入前，screenwriter 行为与 3.10 基线一致。

### 多视角 POV 派生（ADR-0008 D4）

- 视角座位 SSOT = 各 persona card Who 正极（共情座位）；contract 不维护 12 行单 vantage 表。
- 中心是 `who-*` 且实例化 card 视角原型 ⇒ `channel: focalized`；否则 `channel: toned`。
- 铁律继承：focal ∈ decon `who-*`；只换视点、不新增内心戏/事件/因果/结果；hypernym 锚保留。

### 双地板（ADR-0008 D5）

- 中性 n1 wording 零改动（contract 声明，非本步实现）。
- 每 persona ≥1 条非聚焦第三人称 toned（contract 声明，3.11.2 装配 + 3.11.3 守卫）。

### alt-creator valence 降级（ADR-0008 D1）

- 极性标注仅限 lens 真有立场处；模糊元素用 surface/hypernym 白描。
- 明确「极性是着色非资格」：两极元素作为构图材料平等合法。

### 传播契约

3.11.1（预测试）/ 3.11.2（生成接线）只引用 contract 规则段 + card 注意力清单，禁止私自改写。

## 3. 本地验证结果 (Verification)

本 TODO 为措辞/文档源 + 契约对齐，未改动运行时代码；执行 personas 相关回归：

```text
> python -m unittest tests.test_personas tests.test_run_persona_batch
----------------------------------------------------------------------
Ran 53 tests in 2.166s
FAILED (errors=1)
```

- `tests.test_run_persona_batch`：11/11 OK。
- `tests.test_personas`：41/42 OK；唯一 error 为环境缺 `data/index/embeddings.npy`（`FileNotFoundError`），已在 `main` 上对照确认**预先存在**，与本次纯 markdown 改动无关，无 regression。

## 4. 潜在影响或技术债 (Technical Debt & Caveats)

### 3.11.2 待办（随权威措辞同步的代码改动）

- `scripts/personas.py`：注入 `Composition mode: ADR-0008` + salience；解析 `center`/`channel`/`focal`；provenance 标签；贪心记分排序；双地板装配。
- 配套单测：中心声明互异、贪心顺延、focalized 派生、第三人称保留、pseudo 计数。

### 3.11.3 待办（守卫）

- center ∈ decon ids；支撑元素 2–4 上限；focal ∈ who-*；事实守卫；双地板硬失败；hypernym 锚不被 POV 绕过。

### alt-creator 语义变更的存量冲击

- 按 valence 桶校验的存量单测/守卫需随 3.11.2/3.11.3 更新；schema 字段保留向后兼容。

### OPEN（ADR-0008 记账）

- **(c) 中心元素粒度**：`why-*`/`how-*`/`result-*` 与实体元素同权重参与贪心——3.11.1 预测试观察后定。
- **(d) valence 可选化后弱 fit persona 产出质量**——3.11.6 pilot 观察。

### 下一 TODO

**3.11.1 预测试**（Go/No-Go）：用本措辞驱动运行时 LLM 按新构图生成 pseudo 跑检索，核验差集是否有新共振片。
