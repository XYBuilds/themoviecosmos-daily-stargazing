# 现实解构 · 产出契约（v2 · ADR-0005 · verbatim + 客观扩展）

> 本文件是管线前两段——**P-Extract（A0）** 与 **P-Expand（共享客观扩展 pass）**——的产出契约 SSOT。决策来源：[ADR-0005](../adr/0005-objective-extraction-neutral-channel-and-collision-vote.md)。承接 [ADR-0002](../adr/0002-pivot-to-event-logic-resonance.md) 的对题召回前提；撞车形状见 [ADR-0003](../adr/0003-multi-agent-resonance-quality-and-a1-as-peer.md)（由 ADR-0005 复活「中性 + ≥1 toned」）。

> **定位**：pseudo 撰写**之前**的结构化素材层。**A0 只做逐字抽取**；**客观扩展 pass 只产 hypernym 梯**。persona 相对价（lens）与 pseudo 组装在下游（P-Lens / P-Compose），不在此层。

---

## 流程位置

```text
1. 网络接口收热点新闻（英文）     → reality.md（现实波澜，人类可读）
2. P-Extract · A0                → reality-deconstructed.json（逐字抽取）
3. P-Expand · 共享客观扩展 pass   → reality-expanded.json（hypernym 梯 overlay）
4. P-Lens · per-persona alt-creator → alt-pool（persona 相对 valence + 三层 provenance）
5. P-Compose · screenwriter      → pseudos（中性通道 + 语气通道）
6. 检索                          → 候选聚合
```

- **语言链**：新闻输入为**英文** → A0 → 扩展 → alt-pool → pseudo → 检索。**英进英出，无翻译步骤**（唯一中文化 = 最终推荐文案给总编）。
- **产物格式（双写）**：
  - `reality-deconstructed.json`：A0 契约本体，机器读。
  - `reality-deconstructed.md`：A0 的人类视图，供总编扫读。
  - `reality-expanded.json`（或等价 overlay）：扩展 pass 产出，附在稳定 element id 上。

---

## 0. 原则

1. **A0 = 逐字 only（P-Extract）**：只记录原文**怎么写**——who / where / when / why / how / result，外加 `role` 与 `relations`。**逐字保留原文用词与其自带价（source valence）**；A0 **不产**任何「中性」替代词、**不做** hypernym 扩展、**不**做视角框定。
2. **客观扩展 = hypernym only（P-Expand）**：**一份共享拷贝**（非 per-persona），为每个 element 产 **hypernym 上位词梯**，受**客观性试金石**约束：「**A2 社会学家与 A4 神话学者会不会给出不同答案？** 会 → 它是 lens，不是 objective；不会 → 可进客观地板。」
3. **三层 provenance（下游消费）**：screenwriter 从池组装 pseudo 时区分三层——`surface`（逐字原文词）/ `hypernym`（客观共享桥）/ `lens`（persona 相对价）。详见 §4 与 `prompts/_shared/persona_alt_creator_contract.md`。
4. **两个「中性」不可混用**：
   - **(a) 客观地板中性（objective-floor neutral）** = `surface` + `hypernym`，共享、persona 无关 → **中性通道**用它。
   - **(b) persona 中点中性（persona-midpoint neutral）** = 某 persona 价值轴的中点，仅活在其 lens spectrum 内 → **不进**中性通道。
5. **事实 vs 解读**：本两层（A0 + 扩展）只装**事实**与**原文断言**；解读、相对价、意味全是 P-Lens / P-Compose 的活。
6. **多值并存用 list**：`role`、`role_in_event`、`relations`、`modality` 等可并存的字段用 JSON 数组，不强制单选。

### 丢弃的惰性字段（inert fields）

`retrieve.py` 仅将 `pseudo.text` 送入嵌入（`QUERY_TEMPLATE.format(pseudo=...)`）。以下字段**从未进入嵌入**、对匹配完全惰性，故 **A0 与扩展 pass 均不再产出或维护**：

| 字段 | 原用途 | 丢弃理由 |
| --- | --- | --- |
| `geocode` | 国/省/市/区/POI 结构化地理 | 不进嵌入 |
| `coordinates` | 经纬度 | 不进嵌入 |
| `scale` | 局部/城市/全国/全球 | 不进嵌入 |
| `scene_archetype` | 场所类型标签 | 不进嵌入 |

地理与场所信息若对题面重要，以 **`where[].text` 逐字保留**于 A0；hypernym 扩展可从上位地名产梯（如 `Dharavi → Mumbai → India`），但**不**再维护独立 geocode 块。

### v1 废止项（勿再引用）

以下 v1 做法已由 ADR-0005 **废止**，本契约不再要求：

- 「全维度无损」式穷举（四级地理、经纬度、scene_archetype…）
- A0 内的**多分辨率标签梯**（`tags` 从具体到抽象）
- A0 承担「镜头中立 / 单一中性源」——中性改由**客观地板**（surface+hypernym）与**中性通道**承担

---

## 1. P-Extract（A0）输出数据结构

每条新闻产出一个 JSON。字段缺信息则留空（`null` / `[]`）。**所有 `text` 类字段 = 原文措辞的逐字转录（英文）**，含原文自带的褒贬/框定用词（source valence），不在此层「纠正」为中性。

```json
{
  "anchor": {
    "dct": "publication/report time (ISO, for resolving relative time)",
    "report_locale": "dateline locale if stated (e.g. 'Reuters Seoul' → Seoul)"
  },

  "when": {
    "absolute":  ["May 31, 2026 8:15 PM", "2008"],
    "relative":  ["yesterday", "three months ago", "effective immediately"],
    "daypart":   ["morning", "afternoon", "predawn", "late night"],
    "season":    ["spring", "peak summer", "year-end"],
    "fuzzy_era": ["Cold War era", "AI boom"],
    "cultural":  ["Mid-Autumn Festival", "Singles' Day"],
    "anchored":  ["after the press conference", "at the moment of impact"],
    "duration":  ["lasting three hours", "over five years"],
    "recurrence":["daily", "annual"],
    "modality":  ["occurred|planned|hypothetical|cancelled-postponed — as stated in source"],
    "timezone":  ["EST", "UTC+8 Beijing", "local time"]
  },

  "where": [
    {
      "text": "Dharavi, Mumbai",
      "role": ["site of occurrence"],
      "relations": ["within Maharashtra", "on India's west coast"],
      "relative_pos": "north of city center by … (if stated)",
      "geopolitical": "South Asia / Indian Ocean coast (if stated)",
      "intended_destination": "stated intended arrival (if any; fact only)",
      "trajectory": "origin → via → destination (mobile subjects only)",
      "contested_name": "Dokdo (KR) / Takeshima (JP) (if disputed names appear)"
    }
  ],

  "who": [
    {
      "text": "central government energy ministry / tens of millions affected residents / …",
      "role_in_event": ["initiator-decision", "affected"],
      "relations": ["opposed to X", "subordinate to Y", "represents Z (only if explicitly stated)"]
    }
  ],

  "why":   [ { "text": "… (one stated cause per row, verbatim)" } ],
  "how":   [ { "step": 1, "text": "… (objective milestone, no dramatic labels)" } ],
  "result":[ { "text": "… (one stated outcome per row, verbatim)" } ]
}
```

> **A0 不产出**：`tags` 标签梯、`alternatives`、`valence`、`hypernym`、`skeleton`、`load_bearing`、`seeds`、共振类型，以及人物的权力/原型定性、起因的「核心赌注」、结果的「反讽」——均为下游 lens。

### 稳定 element id

下游引用须稳定。惯例（实现须一致）：

| 路径 | id 模式 |
| --- | --- |
| `who[i]` | `who-{i}` |
| `where[i]` | `where-{i}` |
| `why[i]` | `why-{i}` |
| `how[i]` | `how-{i}` |
| `result[i]` | `result-{i}` |

---

## 2. P-Expand（共享客观扩展 pass）

**输入**：`reality-deconstructed.json`（A0 逐字产出）。  
**输出**：`reality-expanded.json`——在同一 element id 上附加 **hypernym 梯**，**一份共享拷贝**，所有 persona 共用。

### 规则

1. **只产 `hypernym`**：每个覆盖的 element 提供从**较具体 → 较抽象**的上位词/类别词列表（英文）。例：`Dharavi → Mumbai → Maharashtra → India → South Asia`；`heatwave → extreme weather → climate hazard`。
2. **客观性试金石**：每条 hypernym 须通过——「A2 与 A4 会不会对此给出不同答案？」会 → **不得**写入 hypernym（那是 lens，留给 alt-creator）。
3. **fact-entailed**：hypernym 须可由 A0 逐字事实推出，**不新增**事件、人物、指控或因果。
4. **不重复 A0 表面词**：`surface` 层 = A0 的 `text`；扩展 pass 只添上位/generalization，不替代表述。
5. **共享、非 per-persona**：禁止为每个 persona 各跑一份扩展；persona 差异只在 P-Lens。

### 扩展产出示例（片段）

```json
{
  "elements": [
    {
      "element_id": "where-0",
      "surface": "central-northern India",
      "hypernyms": ["India", "South Asia", "inland region", "densely populated area"]
    },
    {
      "element_id": "who-0",
      "surface": "residents across central-northern India",
      "hypernyms": ["civilians", "affected population"]
    }
  ]
}
```

---

## 3. 字段说明（A0 各块）

### When

原文出现的任何时间信息按类填入对应数组（**逐字转录**）：

- **absolute** / **relative**（相对时间依赖 `anchor.dct` 换算）
- **daypart**、**season**、**fuzzy_era**、**cultural**、**anchored**、**duration**、**recurrence**
- **modality**：已发生 / 计划 / 假设 / 取消·推迟——**客观转述原文呈现的状态**
- **timezone**、**anchor.dct**

### Where

- **text**：地点/场所的原文表述（**含 source valence**）。
- **role**（list）：客观空间事实，如 `site of occurrence` / `area affected`。
- **relations**：仅当原文明确陈述的空间关系。
- **relative_pos** / **geopolitical** / **intended_destination** / **trajectory** / **contested_name**：原文有则填。

### Who

- **text**：身份/机构的原文表述（**保留专名与原文框定词**；去实体化是下游的事）。
- **role_in_event**（list）：原文陈述的客观角色（发起·决策 / 执行 / 受影响 / 见证），可多值并存。
- **relations**：对立 / 依附 / 代表 / 同盟——**仅当原文明确陈述**，不推断。

### Why / How / Result

每条为可独立取用的客观碎片，**只记原文断言，不贴戏剧标签**：

- **why**：原文陈述的触发/背景（可多条）。
- **how**：按 `step` 排列的客观里程碑（不标「转折/高潮」）。
- **result**：伤亡/损失/判决/最新进展等已陈述事实（不记「反讽/代价」类解读）。

起因 / 经过 / 结果三类**对称、无主次**（切片对切片匹配）：任意一类碎片都可匹配某部 overview 的对应切片。

---

## 4. 三层 provenance（下游 · P-Lens / P-Compose）

本层不产出 provenance 标签，但契约规定下游语义，以便中性通道与语气通道口径一致：

| 层 | 来源 | 客观 vs lens | 用于 |
| --- | --- | --- | --- |
| **surface** | A0 逐字 `text` | 客观地板 | 中性通道；保留 source valence |
| **hypernym** | P-Expand 共享梯 | 客观地板 | 中性通道 + toned 的**题面锚** |
| **lens** | alt-creator persona 相对价 | lens | **语气通道** only；含 persona 中点中性 |

**中性通道（C-Neutral）**：每 persona **恰好 1 条** pseudo，仅用 `surface` + `hypernym`，**无 lens**。  
**语气通道（C-Toned）**：每条 toned pseudo = **hypernym 锚（留在题面）+ lens 倾斜**；发自己的 anchored 检索 query。

撞车主判据（ADR-0005）：中性通道整体算 **1 张去重 agent 票**（所有中性 pseudo 命中的 union）；**优质候选 = 中性票 + ≥1 toned lens 汇聚到同一部电影**。

---

## 5. 下游消费（备忘 · 不在此层产出）

- **碎片选取**：`why-*` / `result-*` 每行可单独成 pseudo；`how-*` 只能取**连续**多条。详见 persona screenwriter 契约。
- **A1 退场**：由**中性通道 union**取代；首轮验证须并跑 A1，证明中性 union ⊇ A1 命中且 2 分率 ≥ A1 后才删 A1（ADR-0005 §A1 退场）。
- **诊断**：`neutral_hit_rate = (命中该片的中性 pseudo 数) / (运行的 persona 数)`；须在控制 `max_similarity` 下解读（ADR-0005 §NEUTRAL HIT RATE）。

---

## 6. 联网补全（占位 · Post-基础版）

**本版不实现。** 仅当观察到「好片被漏，确因某条新闻**事实槽真的空了**」才考虑；触发条件是**槽位空缺**；补来的内容标注「背景·补充·未核实」、与原文事实分离。**只补事实，不补解读。**

---

## 附录 · worked example（India heatwave · English）

> Source summary: April–May 2026, a persistent high-pressure system drove record heat across central-northern India, with temperatures above 45°C nearing 48°C, tens of millions facing water/survival crisis, at least 37 dead, national power demand hit a record 270.8 GW.

### A0 · `reality-deconstructed.json`（节选）

```json
{
  "anchor": { "dct": "2026-05", "report_locale": null },
  "when": {
    "absolute": ["April 2026", "May 2026"],
    "relative": [], "daypart": [],
    "season": ["peak summer"],
    "fuzzy_era": [], "cultural": [], "anchored": [],
    "duration": ["roughly two-month heatwave"],
    "recurrence": [],
    "modality": ["occurred: ongoing disaster"],
    "timezone": []
  },
  "where": [{
    "text": "central-northern India",
    "role": ["site of occurrence"],
    "relations": [],
    "relative_pos": null,
    "geopolitical": "South Asia",
    "intended_destination": null,
    "trajectory": null,
    "contested_name": null
  }],
  "who": [
    { "text": "residents across central-northern India",
      "role_in_event": ["affected"], "relations": [] },
    { "text": "national power and water systems",
      "role_in_event": ["affected"], "relations": ["carrying nationwide demand"] }
  ],
  "why": [
    { "text": "a stubborn high-pressure system drove extreme sustained heat" }
  ],
  "how": [
    { "step": 1, "text": "multiple regions broke 45°C and neared 48°C" }
  ],
  "result": [
    { "text": "tens of millions faced survival and water crisis; at least 37 dead" },
    { "text": "national power demand reached a record 270.8 GW" }
  ]
}
```

### P-Expand · overlay（节选）

```json
{
  "elements": [
    { "element_id": "where-0", "surface": "central-northern India",
      "hypernyms": ["India", "South Asia", "inland region", "densely populated area"] },
    { "element_id": "who-0", "surface": "residents across central-northern India",
      "hypernyms": ["civilians", "affected population"] }
  ]
}
```

> A0 保留原文事实与措辞；「体制碾压边缘群体」类骨架属 persona lens，不在此层。「穷人买不起空调」若原文未陈述，亦不在此层。
