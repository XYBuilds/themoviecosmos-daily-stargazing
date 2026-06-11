# 共振双轴定义 · 唯一权威措辞源 (Resonance Double-Axis · Authoritative Wording v2)

> **角色（SSOT）**：本文件是 [ADR-0007](../../docs/adr/0007-logic-resonance-judge-prescreen-and-pov-focalization.md) **D1**「共振重定义为表层元素 + 底层逻辑（双轴）」的**唯一权威措辞源**。
> Phase 3.10.1（judge prompt）与 3.10.2（rubric 文档）**只逐字粘贴**下文的 judge-ready / rubric-ready 成稿，**禁止各自改写**——三处同源是防止「judge 与人类按不同尺子打分」（重蹈 3.9 的 14 例分歧）的硬性约束。
>
> **追认性质**：新定义不是放宽。总编自述「打分其实早按表层 + 底层逻辑打」——本文件是让白纸黑字的 rubric 与 judge 对齐人类**已在用**的标准。

---

## 1. 双轴定义（中文 · 权威口径）

共振分两层、按 **2×2 矩阵**评分（0/1/2）。两轴**相互独立**，分数 = 成立的轴数。

### 第一轴 · 表层元素 (Surface element)

**定义**：新闻与电影共享一个**具体、可命名**且在两边故事里都**承重**的元素——这个地点 / 这类职业 / 这种事件类型 / 这个设定题材。

- **判据（0 分守门）**：换一条**无关新闻**若同样能配上这部电影，则该共享元素**不承重** ⇒ 第一轴 = 无。承重表层锚点必须「换条无关新闻无法复用」。
- **归属铁律**：**抽象权力角色配对（权威↔受害者、领袖↔团队）不算表层元素，归底层逻辑轴**。它们过不了 0 分守门（换条无关机构新闻同样能套上）。

### 第二轴 · 底层逻辑 (Underlying logic) — 替换旧「结构性共振 / 骨架同构」

**定义**：新闻与电影**实例化同一个因果-赌注引擎**，且该引擎在 **POV（视角）/ 尺度变换下不变**。引擎是一句 **「X 在约束 Z 下驱动 Y」**（例：*系统性稀缺把普通人逼入求生模式*）。一个在**机构尺度**讲、一个在**个人尺度**讲，只要是同一句引擎，**仍算**逻辑共振。

- **可证伪反测句（防给分膨胀）**：必须能写出**一句**两边都字面成立的「X 在约束 Z 下驱动 Y」。**写不出 ⇒ 不算逻辑共振，退回 0/1**。
- **逻辑 0 分守门**：若该因果句对**无关新闻配上同一部电影**仍字面成立 ⇒ 第二轴 = 无 ⇒ **不可**给「深层共振（仅逻辑，无表层）」。
- **0/1 不确定时优先 0**。
- **宽窄边界**：「底层逻辑」比旧「骨架同构」**宽**（接纳 POV / 尺度变换），但因有反测句兜底，**不滑成「什么都给分」**。

### 2×2 矩阵（矩阵不变，仅换措辞）

措辞迁移：`结构性共振 → 逻辑共振`；`深层共振（仅结构，无表层）→ 深层共振（仅逻辑，无表层）`；`强共振（表层 + 结构）→ 强共振（表层 + 逻辑）`。**无表层 + 无逻辑 = 0 / 单轴 = 1 / 双轴 = 2**。

| 表层元素 | 底层逻辑 | 分 | 共振类型 |
|---|---|---|---|
| 无 | 否 | **0** | 无共振（偶然词面重叠） |
| 无 | 是 | **1** | 深层共振（仅逻辑，无表层） |
| 有 | 否 | **1** | 表层沾边 |
| 有 | 是 | **2** | 强共振（表层 + 逻辑） |

> **与 14 例分歧的收口**（ADR-0007「14 例分歧归因」）：Gap A（judge 见「表层沾边」、人见同一因果引擎只是视角/尺度变了）在新定义下 **→ 2**；Gap B（无具体锚点、仅靠抽象权力角色给分）在新定义下 **→ 1**（权威↔受害者归逻辑轴、过不了 0 分守门）。

---

## 2. judge-ready 成稿（英文 · 供 3.10.1 逐字粘贴进 `scripts/llm_judge.py`）

> **传播契约**：3.10.1 **逐字**用下列两段替换 `scripts/llm_judge.py` 的 `_JUDGE_SYSTEM` 与 `_JUDGE_RUBRIC`，**不得改写措辞**。两段沿用现有 f-string 形态，引用 `scripts/resonance_rubric.py` 的 `TYPE_*` 常量（常量更新见 §4 待改清单——3.10.1 先更新常量、再粘贴，即为机械传播）。

```python
_JUDGE_SYSTEM = (
    "You are an expert resonance judge for a news-to-film matching eval. "
    "A match resonates on two independent axes: (1) surface element and "
    "(2) underlying logic. The score equals the number of axes that hold. "
    "Return only valid JSON matching the requested schema. "
    "Follow the decision tree: first assess 表层元素 (load-bearing concrete "
    "anchor, passes the 0-guard) yes/no; then assess 底层逻辑 (a causal-stakes "
    "engine invariant under POV/scale change) yes/no — this axis is GATED by a "
    "falsifiable causal counter-test: you MUST write one 'X, under constraint Z, "
    "drives Y' sentence that is literally true of BOTH the news and the film; "
    "if you cannot, 底层逻辑 = NO. Apply the logic 0-guard: if that sentence "
    "would still hold for an unrelated news item paired with the same film, "
    "底层逻辑 = NO. When uncertain between score 0 and 1, prefer 0. "
    "Then map to score and resonance_type."
)

_JUDGE_RUBRIC = f"""\
## Resonance score rubric (two independent axes, 2×2 matrix)

A news–film pair can resonate on two **independent** axes. score = number of axes that hold.

**Axis 1 — 表层元素 (surface element)**: Do the news and film share a
**concrete, nameable** element that is **load-bearing** in both stories
(this place / this kind of occupation / this type of event / this setting or subject-matter)?
- **0-guard**: if an unrelated news item could be paired with the same film equally well,
  the shared element is NOT load-bearing → Axis 1 = NO.
- **Abstract power-role pairings (authority↔victim, leader↔team) are NOT surface elements**
  — they belong to Axis 2 (they fail the 0-guard: an unrelated institutional news item fits them too).

**Axis 2 — 底层逻辑 (underlying logic)**: Do the news and film instantiate the
**same causal-stakes engine**, invariant under change of POV or scale? The engine is one
sentence of the form **"X, under constraint Z, drives Y"**
(e.g. *systemic scarcity forces ordinary people into survival mode*). An institutional-scale
telling and an individual-scale telling of the **same** engine still count as the same logic.
- **Falsifiable causal counter-test (anti-inflation)**: you MUST write a single
  "X under constraint Z drives Y" sentence that is literally true of **both** sides.
  If you cannot write one, Axis 2 = NO → fall back to score 0/1.
  ("Logic" is broader than rigid structural isomorphism because it admits POV/scale shifts,
  but it does not collapse into "everything resonates".)
- **Logic 0-guard**: if your causal_test sentence would remain literally true for an
  **unrelated news item** paired with the same film, the engine is NOT specific to this
  pair → Axis 2 = NO (you cannot assign score 1 via {{TYPE_DEEP}}).
- **Tie-break**: when uncertain between score 0 and 1, prefer 0.

| 表层元素 | 底层逻辑 | score | resonance_type |
|---|---|---|---|
| 无 | 否 | **0** | null |
| 无 | 是 | **1** | {{TYPE_DEEP}} |
| 有 | 否 | **1** | {{TYPE_SURFACE}} |
| 有 | 是 | **2** | {{TYPE_STRONG}} |

**0-guard restated**: if an unrelated news item could explain the film equally well
→ 无表层 + 无逻辑 → score 0 (resonance_type null; conceptually {{TYPE_NONE}}).

Output JSON. All fields required. `resonance_type` is null only at score 0.
`causal_test` is the bidirectional "X under constraint Z drives Y" sentence that holds for
BOTH news and film; set it to "" only when Axis 2 = NO. `rationale` is brief free text.
{{{{"score": 0|1|2, "resonance_type": {{TYPE_DEEP!r}}|{{TYPE_SURFACE!r}}|{{TYPE_STRONG!r}}|null, "causal_test": "X under constraint Z drives Y — true of both news and film, or \\"\\" if none", "rationale": "brief"}}}}
"""
```

> **粘贴说明（给 3.10.1 执行者）**：上面的 ``{{TYPE_DEEP}}`` / ``{{TYPE_NONE}}`` / ``{{...}}`` 是**本 markdown 为转义而双写的花括号**。粘进 `.py` 后应还原为**单花括号** f-string 占位：`{TYPE_DEEP}`、`{TYPE_SURFACE}`、`{TYPE_STRONG}`、`{TYPE_NONE}`、`{TYPE_DEEP!r}` 等，最外层 JSON 示例的字面花括号用 `{{` / `}}`。换言之，目标 `.py` 中的成品形态与现状 `_JUDGE_RUBRIC` 完全同构，只是文字内容换成双轴 + 新增 `causal_test` 字段。

### judge-ready 配套（强制因果反测句 → schema 字段）

- judge 输出**新增必填字段 `causal_test`**：即第二轴的「X 在约束 Z 下驱动 Y」双向映射句；写不出（Axis 2 = NO）时置 `""`。
- 校验口径：`score == 2` ⇒ `causal_test` 非空（双轴成立必有逻辑句）；`resonance_type == 深层共振（仅逻辑，无表层）` ⇒ `causal_test` 非空；其余沿用现有 `validate_score_type_pair` 矩阵约束。
- 上述字段解析/断言属**代码改动**，在 3.10.1 落地（见 §4 待改清单），本 TODO 不动 `llm_judge.py`。

---

## 3. rubric-ready 成稿（中文 · 供 3.10.2 逐字粘贴进 `docs/eval-the-bet.md` §4）

> **传播契约**：3.10.2 **逐字**用下列内容替换 `docs/eval-the-bet.md` §4 的两层定义、2×2 表与共振类型标注示例，**不得改写措辞**；归属规则不变。

---8<--- rubric-ready 起 ---8<---

共振有**两层**，本 rubric **同时拥抱**二者（与 [`CONTEXT.md`](../CONTEXT.md) 中 **共振 (Resonance)** 一致）。**验收目标统一为「关联 / 共振」**——不单独追求讽刺、反讽或荒诞作为产品指标；后者仅可作为底层逻辑或双重共振的**子类**出现。

- **第一轴 · 表层元素 (Surface)**：候选与新闻共享**具体、可命名且承重**的元素——地点 / 人物类型 / 事件类型 / 设定 / 题材。关键在「**承重**」：换一条无关新闻**无法**复用该元素。**抽象权力角色配对（权威↔受害者、领袖↔团队）不算表层元素，归底层逻辑轴**。
- **第二轴 · 底层逻辑 (Underlying logic)**：新闻与电影**实例化同一个因果-赌注引擎**，且该引擎在 **POV / 尺度变换下不变**——一句 **「X 在约束 Z 下驱动 Y」**（如*系统性稀缺把普通人逼入求生*），机构尺度↔个人尺度也算。**可证伪反测**：写不出一句两边都成立的因果句 ⇒ 不算逻辑共振，退回 0/1。**逻辑 0 分守门**：若该因果句对无关新闻配上同一部电影仍字面成立 ⇒ 第二轴 = 无 ⇒ 不可给「深层共振（仅逻辑，无表层）」。**0/1 不确定时优先 0**。

按两轴定分（**先判承重表层元素，再判 POV/尺度不变因果引擎**）：

| 表层元素 | 底层逻辑 | 分 | 共振类型 |
|---|---|---|---|
| 无 | 否 | **0** | 无共振（偶然词面重叠） |
| 无 | 是 | **1** | 深层共振（仅逻辑，无表层） |
| 有 | 否 | **1** | 表层沾边 |
| 有 | 是 | **2** | 强共振（表层 + 逻辑） |

> **0 分守门**：别让「拥抱表层」滑成「什么都给分」。**纯偶然、非承重的表层重叠仍判 0**——判据不变：「换一条无关新闻同样能解释这部片」= 0。

**共振类型标注（总编打分时填，最小体温计）**：`共振分` 与 `共振类型` **必须**按上表一致；打 1 / 2 分时标对应类型，0 分留空。用于诊断「创作视角的强共振 vs 仅逻辑 / 仅表层」（直接喂 §5.1 第 2 条；见 ADR-0002 / ADR-0007）。LLM judge 同样输出 `score` + `resonance_type` + `causal_test`（因果反测句），校验同一矩阵。

**可选子标签 · POV变换**（ADR-0007 D7 / Phase 3.11.5）：仅 score 2 时可标；表示强共振靠 POV/尺度变换才可见。judge 输出 `pov_transform: true|false`；人工侧 `- **POV变换**: 是`。

```markdown
- **共振分**: 2
- **共振类型**: 强共振（表层 + 逻辑）    <!-- 0 分留空；1→深层共振（仅逻辑，无表层）|表层沾边；2→强共振（表层 + 逻辑） -->
- **POV变换**: 是    <!-- 可选；仅 score 2 -->
```

---8<--- rubric-ready 止 ---8<---

> **§5.1 第 2 条口径同步提示（给 3.10.2 执行者）**：§5.1 第 2 条现有口径写「`共振类型 ∈ {深层共振（仅结构，无表层）, 强共振（表层 + 结构）}`」与「单独比 `强共振（表层 + 结构）` 的 2 分率」。逐字替换为新措辞 `深层共振（仅逻辑，无表层）` / `强共振（表层 + 逻辑）`。此为 §4 之外的连带措辞同步，仍属 3.10.2 范围。

---

## 4. 3.10.1 / 3.10.2 待改清单（本 TODO 只记账，不动代码/正文）

> 以下条目记录「随权威措辞同步必须改动」之处，**由 3.10.1 / 3.10.2 执行**。本 TODO（3.10.0）一律不动这些文件。

### 给 3.10.1（`scripts/llm_judge.py` + `scripts/resonance_rubric.py` + 单测）

1. **`scripts/resonance_rubric.py` 常量改名（措辞迁移）**：
   - `TYPE_DEEP`：`"深层共振（仅结构，无表层）"` → **`"深层共振（仅逻辑，无表层）"`**
   - `TYPE_STRONG`：`"强共振（表层 + 结构）"` → **`"强共振（表层 + 逻辑）"`**
   - `TYPE_SURFACE`（`"表层沾边"`）、`TYPE_NONE`（`"无共振（偶然词面重叠）"`）**不变**。
   - **兼容性注意**：`_LEGACY_TO_CANONICAL` 现把旧人工标注 `结构→TYPE_DEEP`、`双重→TYPE_STRONG` 映射到上述常量；改名后这些旧标注会自动落到新措辞常量。需在 `_TYPE_PARSE_ORDER` / 旧标注解析层确认：3.9 legacy 文本里若直接出现「仅结构」「表层 + 结构」整串，是否仍能解析（ADR-0007 D2 已冻结 3.9 为 legacy、不可比，故无需回溯重写历史文件；仅保证脚本不崩）。`validate_score_type_pair` 的矩阵约束按常量自动随动，无需改逻辑。
2. **`_JUDGE_SYSTEM` / `_JUDGE_RUBRIC`**：逐字粘贴 §2 judge-ready 两段（还原单花括号 f-string 形态）。
3. **新增 `causal_test` 字段解析与校验**：
   - `validate_judge_payload` 增 `causal_test`（str，可空）；返回值或下游结构携带之。
   - 断言：`score == 2` ⇒ `causal_test` 非空；`judge_resonance_type == TYPE_DEEP` ⇒ `causal_test` 非空。
   - `JudgeResult` 增 `causal_test` 字段；`parse_judge_response` 一并返回；`write_judge_markdown` / `format_judge_block_lines` / `load_judge_output` 补该字段的读写。
4. **单测**：双轴 rubric 解析、`causal_test` 必填校验（缺失即失败）、score↔type 矩阵一致（新常量）、强制因果反测句字段存在。

### 给 3.10.2（`docs/eval-the-bet.md` §4 + 连带措辞）

1. 逐字替换 §4 两层定义、2×2 表、共振类型标注示例为 §3 rubric-ready 成稿。
2. 同步 §5.1 第 2 条的共振类型枚举措辞（`深层共振（仅逻辑，无表层）` / `强共振（表层 + 逻辑）`）。
3. 归属规则（每 `(新闻, tmdb_id)` 打一次分、计入 `triggered_by` 的创作视角桶、仅 A1 命中计 baseline 桶）**不变**。

### 通用

- `CONTEXT.md`：术语已在本 TODO 同步（表层元素 / 底层逻辑 / POV 不变因果引擎 / 因果反测句 / judge 预筛 / 拒绝集抽审）。

---

## 5. 传播契约声明（硬性）

1. **本文件是双轴定义的唯一权威措辞源**；ADR-0007 D1 为决策依据，本文件为可粘贴落地措辞。
2. **3.10.1 只逐字粘贴 §2 judge-ready 段**（还原 f-string 单花括号），**禁止改写**任何措辞；仅做 §4 待改清单列出的机械代码改动（常量改名、`causal_test` 字段、单测）。
3. **3.10.2 只逐字粘贴 §3 rubric-ready 段**，**禁止改写**任何措辞；连带同步 §5.1 第 2 条枚举。
4. **任何一处措辞漂移 = 重蹈 3.9 的 14 例分歧**（judge 与人类按不同尺子打分）。如需调整措辞，**改本文件**后再向下游重新传播，不得在下游就地修改。
