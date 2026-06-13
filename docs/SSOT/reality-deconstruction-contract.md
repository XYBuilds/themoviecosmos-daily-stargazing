# 现实解构 · 产出契约（A0 抽取层 · verbatim）

> **当前状态（2026-06-14）**：本文件中 **P-Extract（A0）逐字抽取契约仍是 SSOT**，fragment ladder 的 `surface` 层与所有 element 引用都依赖它。
>
> **已被取代的部分**：原 **P-Expand 独立 hypernym 层（`reality-expanded.json`）、三层 provenance（surface/hypernym/lens）、中性通道 / 语气通道、撞车票** 已由 [ADR-0009](../adr/0009-fragment-ladder-and-search-unit-architecture.md) 的 **fragment ladder / search unit** 整体替换——hypernym 并入 ladder 的 `objective_*` 层，lens 并入 `interpretive / perspective` 层，召回改由 surface/event/persona search unit 承担。工作流权威源见 [`docs/SSOT/simplified-news-to-film-workflow.md`](simplified-news-to-film-workflow.md)。
>
> 决策来源：[ADR-0005](../adr/0005-objective-extraction-neutral-channel-and-collision-vote.md)（已 superseded，A0 抽取部分被本契约延续）。承接 [ADR-0002](../adr/0002-pivot-to-event-logic-resonance.md) 的对题召回前提。

> **定位**：fragment ladder 生成**之前**的结构化素材层。**A0 只做逐字抽取**；persona 相对价与 ladder/search unit 组装在下游（见工作流文档 §3.4 起），不在此层。

---

## 流程位置

```text
1. 网络接口收热点新闻（英文）     → reality.md（现实波澜，人类可读）
2. P-Extract · A0                → reality-deconstructed.json（逐字抽取）
3. Fragment ladder + search unit  → 见 simplified-news-to-film-workflow.md §3.4 起
4. Hybrid recall                 → 候选聚合
```

- **本契约只覆盖第 2 段（A0）**。第 3 段起（fragment ladder 生成、search unit、hybrid recall、候选漏斗）以 [`simplified-news-to-film-workflow.md`](simplified-news-to-film-workflow.md) 为权威源。
- **语言链**：新闻输入为**英文** → A0 → ladder → search unit → 检索。**英进英出，无翻译步骤**（唯一中文化 = 最终推荐文案给总编）。
- **A0 产物（双写）**：
  - `reality-deconstructed.json`：A0 契约本体，机器读。
  - `reality-deconstructed.md`：A0 的人类视图，供总编扫读。

---

## 0. 原则

1. **A0 = 逐字 only（P-Extract）**：只记录原文**怎么写**——who / where / when / why / how / result，外加 `role` 与 `relations`。**逐字保留原文用词与其自带价（source valence）**；A0 **不产**任何「中性」替代词、**不做** hypernym 扩展、**不**做视角框定。
2. **事实 vs 解读**：本层只装**事实**与**原文断言**；解读、相对价、意味全是下游 fragment ladder（`interpretive / perspective` 层）的活。
3. **多值并存用 list**：`role`、`role_in_event`、`relations`、`modality` 等可并存的字段用 JSON 数组，不强制单选。

> **下游接口（已迁移，不在本层）**：原 hypernym 扩展、三层 provenance（surface/hypernym/lens）、中性/语气通道、撞车票均已被 ADR-0009 的 fragment ladder / search unit 取代。本契约不再维护这些概念；fragment ladder 直接消费 A0 的 element 与 `element_id`。

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

## 2. 客观扩展 / hypernym（已迁移 · 不在本契约）

> 原 **P-Expand 共享客观扩展 pass（`reality-expanded.json` · hypernym 梯）已被 [ADR-0009](../adr/0009-fragment-ladder-and-search-unit-architecture.md) 取代**。hypernym 能力并入每个 element 的 **fragment ladder 的 `objective_close / objective_mid / objective_broad` 层**，不再作为独立 overlay 维护。生成规则、客观性试金石、fact-entailed 约束均迁移至 [`simplified-news-to-film-workflow.md`](simplified-news-to-film-workflow.md) §2.3 / §3.4。本契约只保证 A0 产出稳定的 element 与 `element_id` 供 ladder 消费。

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

## 4. 下游消费（已迁移 · 不在本契约）

> 原 §4 三层 provenance（surface/hypernym/lens）、中性通道 / 语气通道、§5 撞车票与 A1 退场口径**均已被 [ADR-0009](../adr/0009-fragment-ladder-and-search-unit-architecture.md) 取代**，当前架构对照如下（权威定义见 [`simplified-news-to-film-workflow.md`](simplified-news-to-film-workflow.md) §9 新旧映射）：

| 旧概念（本契约 v2） | 新位置（ADR-0009） |
| --- | --- |
| `surface` 层 | fragment ladder `surface`（仍来自 A0 逐字 `text`） |
| `hypernym` 层 | fragment ladder `objective_close / objective_mid / objective_broad` |
| `lens` 层 | fragment ladder `interpretive / perspective` |
| 中性通道（C-Neutral）/ n1 | 下线；事实参照由 surface/event fragment bundle 承担 |
| 语气通道（C-Toned）| 下线；电影化表达并入 persona-semantic search unit |
| 撞车票 / `quality_candidate` | 改为 `surface_match / event_match / persona_semantic_match` 收敛诊断 |
| A1 退场 / 中性 union | A1 已 diagnostic-only 退场；中性基线只读参照，不进任何闸 |

- **碎片选取惯例（仍有效）**：`why-*` / `result-*` 每行可单独成搜索碎片；`how-*` 只能取**连续**多条。
- **A0 的下游唯一职责**：提供稳定 element 与 `element_id`，供 fragment ladder 绑定。

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

> A0 保留原文事实与措辞；「体制碾压边缘群体」类骨架属下游 fragment ladder 的 interpretive 层，不在此层。「穷人买不起空调」若原文未陈述，亦不在此层。fragment ladder 如何在这些 element 上展开 objective / interpretive 层，见 [`simplified-news-to-film-workflow.md`](simplified-news-to-film-workflow.md) §2.2。
