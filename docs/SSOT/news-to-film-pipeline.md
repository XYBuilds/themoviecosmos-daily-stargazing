# 新闻到电影候选管线：唯一 SSOT 与阶段命名权威

> **状态**：管线唯一权威文档（阶段命名权威 + 工作流设计 SSOT）。命名收敛依据 [ADR-0011](../adr/0011-pipeline-stage-naming-and-legacy-purge.md)，架构依据 [ADR-0009](../adr/0009-fragment-ladder-and-search-unit-architecture.md)（Phase 3.11.8 GATE go · 2026-06-13）。
>
> **定位**：本文件同时是【阶段命名权威】与【工作流设计 SSOT】。它登记从 intake/选材 到人工共振评审的完整链路口径，并钉死管线每一步的唯一主名（英文动词主名 + 中文别名，编号体系全废，依据 ADR-0011）。核心是移除 `lens / neutral / toned / focalized / fact-anchor query / 独立 hypernym` 这些高负担概念，改用更底层、更可解释的 `fragment ladder`、`search unit`、`center_element` 和 hybrid recall。extract/解构层契约见 [`reality-deconstruction-contract.md`](reality-deconstruction-contract.md)。
>
> **落地物偏差说明**：本轮命名收敛不改代码，磁盘上仍是旧文件名。下文凡涉及承载脚本与产物名，均按「目标名（当前实际：旧名）」格式标注偏差；偏差清单与清理债见 ADR-0011。

---

## 0. 阶段总表与命名映射（阶段命名权威）

> 本节为 ADR-0011 钉定的「一步一名」权威落地处：6 个生产阶段 + 1 个编排入口，每阶段唯一英文动词主名 + 唯一中文别名，编号体系全废。概念维度（阶段名 / 中文别名 / 处理 / 目的 / 边界）按目标态书写；落地物维度（承载脚本 / 产物名）暂标偏差。

### 0.1 阶段总表（输入 / 处理 / 目的 / 产出 / 边界）

| 阶段主名 · 中文别名 | 承载脚本（标偏差） | 产物名（标偏差） | 输入 | 处理 | 目的 | 产出 | 边界 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `intake` · 选材 | `fetch_news.py`（目标：`intake.py`） | `news.json`（当前实际：未实现） | 外部新闻源 | 拉取并固化一条新闻原文为 JSON 快照，不改写、不解释、不扩展 | 给后续全链提供稳定的事实原文与复盘入口 | 新闻快照（`reality.json` / `reality.md` 为当前快照产物） | 只固化原文，主链默认英文输入以避免与英文电影 overview 的分布偏移 |
| `extract` · 解构 | `deconstruct.py`（目标：`extract.py`） | `facts.json`（当前实际：`facts.json`） | 新闻快照 | 把新闻拆成 when/where/who/why/how/result 六类稳定 element，每块给稳定 `element_id` | 建立全链事实地基，防止下游伪造人物/事件/动机/因果/结果 | 结构化 element 集合（`facts.json` / `.md`） | 只记录新闻怎么说；不做上位扩展、人设、情绪、价值、共振解释，不新增未明说因果 |
| `expand` · 扩展 | `fragment_ladder.py`（目标：`expand.py`） | `bridges.json`（当前实际：`bridges.json`） | extract 的 element | 为每个 element 生成 fragment ladder（surface/alias/objective_*/interpretive/perspective），含距离权重；原 hypernym 并入 objective 层、原 lens/alternative 并入 interpretive/perspective 层 | 保留不同距离的可审计表达层级，供召回与诊断使用 | fragment ladder 集合（`fragment-ladders.json`） | 每项必须绑定既有 `element_id`；不新增事实；严格区分 objective 与 interpretive |
| `rewrite` · 改写 | `personas.py`（目标：`rewrite.py`） | `queries.json`（当前实际：`search-units.json` / `personas/*`） | element + fragment ladder + persona salience | 生成三类 search unit（surface-fragment-bundle / event-fragment-bundle / persona-semantic）；persona 结合 salience 与 interpretive/perspective 材料产 persona-semantic | 把碎片按用途组织成统一的可搜索单元 | search unit 集合（`search-units.json`） | 每条 search unit 必须绑定 source elements；persona-semantic 必须有 center_element 与 objective anchor，不新增事实 |
| `retrieve` · 召回 | `retrieve.py`（目标：`retrieve.py`） | `candidates.json`（当前实际：`candidates.json`） | search unit + 电影库 | hybrid recall（lexical/alias + weighted ladder + dense embedding）→ 候选漏斗（去重 / match 诊断 / 汇聚排序 / judge 预筛 / 人工预算） | 收敛出真正与新闻共振的候选电影 | 候选集合（`candidates.json`），含 surface/event/persona_semantic match 诊断 | 基线 oracle 旁挂评测专用，永不进 `candidates`；judge 只预筛不裁决 |
| `compose` · 文案 | `copywriter.py`（目标：`compose.py`） | `review.md` / `publish.md`（当前实际：daily batch 草稿池 + publication bundle） | 候选与人工评审结果 | 生成审核稿与定稿文案，分两个 stage：`compose --stage review` / `compose --stage publish`；`publish` 按 [ADR-0015](../adr/0015-publish-platformization-and-element-checklist.md) 每平台一个创作步骤（`--platform`），小红书首发，产出正文 + headline（≤10 中文字）+ 归属行 `「片名」(YYYY) 导演名`，正文只守必含元素清单（新闻侧/关系侧/电影侧），不规定顺序或段数。Persona 草稿池保留在 `daily_batch`；选定后的当前稿与去 AI 化派生稿写入 `output/publications/{date}/{tmdb_id}-{movie_slug}/copy/`，由 bundle `manifest.json` 保存平台状态与 `selected_draft_id` | 产出可供人工评审与对外发布的文案，并把最终稿纳入独立发布工作区 | 审核稿 `review.md`、只读草稿池、当前稿与去 AI 化派生稿；旧 `selection.json.copies` 和旧 daily_batch copy 仅兼容读取 | 文案承重元素须与事实锚点一致，不脱离声明来源；avoid-ai-writing 改写只生成派生产物，不覆盖原版定稿；selection 不承载发布状态 |
| `orchestrate` · 编排 | `main.py`（目标：`main.py`） | `Daily_Briefing/YYYY-MM-DD.md`（当前实际：未实现） | 全阶段 | 串联 intake→extract→expand→rewrite→retrieve→compose 的端到端编排入口 | 一次 run 跑通整条管线并产出每日简报 | 每日简报 `Daily_Briefing/YYYY-MM-DD.md` | 编排入口，不承载单阶段算法 |

> **Phase 9.8 补充（`compose` 定稿面板能力，[ADR-0016](../adr/0016-panel-editorial-regeneration-and-inline-edit.md)）**：审核面板对 publication bundle 当前稿新增三种定点操控，均为**覆盖当前稿**，不新增版本层（仍是 原版 / 去AI化版 二档）。① 重生成正文：重跑 `run_publish`，只取新 body 覆盖，丢弃顺带产出的新 headline，headline 不自动联动；② 重生成标题：body-aware，以当前 body 为输入调 `run_headline`，只覆盖 headline，body/链接不动；③ 正文人工编辑：面板 textarea 直改正文，经 `render_copy_markdown` 无 LLM 写回原稿。三者中前两种改 body 的操作（①③）都会删除陈旧的 humanized 文件并清空 manifest 对应平台的 `humanized_path`，维持「humanized_path=null ⇔ 盘上无 humanized 稿」不变量；②不改 body，不触发失效。旧 `selection.json.copies` 和旧 `_copy_*.md` 只作为兼容读取来源。

> **Phase 10 补充（`compose` persona 视角 C2 草稿池，[ADR-0017](../adr/0017-persona-perspective-c2-draft-pool.md)）**：C2 定稿链路新增**上游 persona 视角来源治理**。① 视角注入：每个 persona 新增 `prompts/personas/{Persona}/c2_perspective.md`（**C2 侧视角 SSOT**，去行话中文蒸馏，与检索侧 `persona_card.md` 分层，C2 只读前者），`run_publish` 经 `{{persona_perspective}}` 占位符（no-op 向后兼容）注入。② 只读草稿池：`{slug}_drafts_{platform}.json` 按候选 `triggered_by` 全量扇出，append-only、永不消费/删除；「选中」= 可变指针 `selected_draft_id`，派生当前稿并失效 `_humanized.md`（沿用 9.8 D4 stale 不变量）。层级为 `只读草稿池 → 当前稿（唯一可编辑）→ 去AI化版`，可编辑面未变宽，故推翻 0016 D4 字面（严格二档）而不违其本意。③ 复数视角合并上限 2，A/B 双路线仅 `--combine-mode both` 开发期离线对照，生产恒单版。**10.7 GATE 选型冻结：路线 A（重跑 C2 合并视角）为生产默认**（路线 B 文本拼接实测出现片名/开头/数据重复且篇幅翻倍）；因 adapter `--combine-mode` argparse 默认即 `A`、`serve.handle_combine_drafts` 不传该参数，冻结为**纯文档、零代码改动**。serve 保持薄传输：generate/combine 经 subprocess 调 `drafts_adapter.py`，select-draft 为 serve 内无 LLM 派生。

> **Phase 13 补充（publication bundle 与视觉资产，[ADR-0021](../adr/0021-publication-bundle-lifecycle.md)）**：`compose` 之后新增发布工作区边界，但不新增自动发布阶段。`selection.json` 只保存当前选择；`daily_batch` 保留日批证据与只读 persona 草稿池；`output/publications/{date}/{tmdb_id}-{movie_slug}/manifest.json` 统一登记当前稿、去 AI 化稿、TMDB original poster 和 3000×3000 RGBA Bloom ON 星球图。准备动作必须由总编显式触发，drafts/poster/planet 并行运行并独立记录 `running/ready/failed`；失败项可单独重试，不重跑其他 artifact。改选把旧包标记为 `superseded` 而不删除；重新选回按稳定电影身份激活已有包。Phase 13.7 已用 The Creator（TMDB 670292）完成真实运行、故障恢复和 Panel 人工 Gate，结论为 Go。

### 0.2 命名映射表（旧编号/旧名 → 唯一主名 / 归属）

> 本表只做「阶段与编号」层面的命名映射，与 §9「新旧概念映射」（概念级：lens/neutral/toned/focalized/hypernym/fact-anchor 等）互补，不重复。概念级映射请直接见 §9。

| 旧名 | 唯一主名 / 归属 |
| --- | --- |
| `A0`（现实解构） | `extract` / 解构 |
| `P-Extract` | 归入 `extract` / 解构 |
| `P-Expand` | 归入 `expand` / 扩展 |
| `P-Select` | 归入 `rewrite` / 改写 |
| `P-Tone` | 归入 `rewrite` / 改写 |
| `C1`（审核稿） | `compose --stage review` |
| `C2`（定稿） | `compose --stage publish` |
| 创作视角编号 `A2` | 视角名「社会学家」（编号仅允许在 `rewrite` 内部保留，因 `prompts/A2_*.md` 文件名暂不改） |
| 创作视角编号 `A4` | 视角名「神话学者」（编号仅 rewrite 内部保留） |
| 创作视角编号 `A7` | 视角名「混沌理论家」（编号仅 rewrite 内部保留） |
| `A1` 四重身份（基线 / held-out oracle / baseline / 现实记录员） | 统一称「基线 oracle」；不属于 6 生产阶段，是 `retrieve` 旁挂的评测专用神谕 |

> 概念级旧名（`lens` / `neutral` / `toned` / `focalized` / `hypernym` / `fact-anchor`）的映射见 §9，本表不重复。

---

## 1. 一句话总览

新版 workflow 不再把新闻事实先揉成固定 pseudo 通道，而是先保留碎片，再把碎片按用途组织成可搜索单元。

```text
事实层：新闻被拆成稳定 element
扩展层：每个 element 生成 fragment ladder，吸收原 hypernym / alternative 能力
召回层：surface / event / persona semantic search units 进入 hybrid recall
候选层：按 surface_match / event_match / persona_semantic_match 收敛
评审层：继续用“表层元素 + 底层逻辑”双轴人工判断
```

整体链路：

```text
新闻输入
→ 1. 新闻快照
→ 2. extract / 解构：生成 element
→ 3. Fragment ladder：生成 surface / alias / objective / interpretive / perspective 层级
→ 4. Persona salience：决定 persona 看重哪些 element
→ 5. Search unit 生成
   → 5.1 surface-fragment-bundle
   → 5.2 event-fragment-bundle
   → 5.3 persona-semantic
→ 6. 运行时守卫
→ 7. Hybrid recall
   → lexical exact / alias recall
   → weighted ladder recall
   → dense embedding recall
→ 8. 候选漏斗
   → 8.1 去重
   → 8.2 match 诊断
   → 8.3 汇聚排序
   → 8.4 judge 预筛
   → 8.5 人工预算 / audit pool
→ 9. 人工共振评审 / GATE
```

核心变化：

```text
hypernym → 合并进 fragment ladder 的 objective levels
lens → 合并进 fragment ladder 的 interpretive / perspective levels
neutral → 删除；由 surface/event fragment bundles 承担事实参照和漂移诊断
fact-anchor query → 删除；只是旧召回接口下的临时自然语言包装
toned → 变成 persona-semantic search unit 的默认质量要求
focalized / POV → 删除；改为通用 center_element 机制
```

---

## 2. 核心概念

## 2.1 element

`element` 是新闻被拆解后的稳定事实块。

来源：`facts.json`。

类型：

```text
when / where / who / why / how / result
```

作用：

- 提供事实边界。
- 给 fragment ladder、search unit、候选解释提供引用锚点。
- 防止 persona 生成伪造新人物、新事件、新动机、新因果、新结果。

基本原则：

```text
后续所有表达都必须能回指到已有 element。
```

---

## 2.2 fragment ladder

`fragment ladder` 是每个 element 的多层表达结构。

它替代原来的：

```text
hypernym
alternative
lens
```

一个 ladder 不只是“同义词列表”，而是带距离、用途和权重的表达层级。

示例：`who-1 = Osama bin Laden`

```json
{
  "element_id": "who-1",
  "dimension": "who",
  "surface": [
    { "text": "Osama bin Laden", "weight": 1.0 }
  ],
  "aliases": [
    { "text": "bin Laden", "weight": 0.95 },
    { "text": "本拉登", "weight": 0.95 }
  ],
  "objective_close": [
    { "text": "terrorist leader", "weight": 0.85 },
    { "text": "al-Qaeda leader", "weight": 0.85 },
    { "text": "militant leader", "weight": 0.75 }
  ],
  "objective_mid": [
    { "text": "organization leader", "weight": 0.55 },
    { "text": "high-value target", "weight": 0.5 }
  ],
  "objective_broad": [
    { "text": "public figure", "weight": 0.3 },
    { "text": "target figure", "weight": 0.3 }
  ],
  "interpretive": [
    { "text": "symbol of terror", "weight": 0.35 },
    { "text": "enemy figure", "weight": 0.3 }
  ]
}
```

这能表达搜索距离：

```text
Osama bin Laden / bin Laden
> terrorist leader / al-Qaeda leader
> organization leader / high-value target
> public figure / target figure
```

---

## 2.3 objective vs interpretive

`fragment ladder` 内部必须区分客观扩展和解释性表达。

### objective levels

用于事实接近度、表层 match、event match、baseline 召回。

```text
surface
aliases
objective_close
objective_mid
objective_broad
```

要求：

- 必须由 element 事实推出。
- 不包含价值判断、隐喻、戏剧化表达。
- 可用于 surface-fragment-bundle 和 event-fragment-bundle。

### interpretive / perspective levels

用于 persona semantic search，不用于事实锚点。

```text
interpretive
perspective
persona_relative
```

要求：

- 必须绑定已有 element。
- 不新增人物、事件、动机、因果、结果。
- 只改变表达角度，不改变事实。

示例：`how-1 = emergency load shedding`

```text
surface:
- emergency load shedding

objective_close:
- power rationing
- electricity cuts

objective_mid:
- grid management action
- emergency infrastructure response

interpretive:
- managed scarcity
- infrastructure fragility
- public vulnerability
```

---

## 2.4 salience

`salience` 是某个 persona 对新闻元素的重要性排序。

它回答：

```text
这个 persona 最自然会看重哪些 element？
```

示例：

```text
persona A:
1. result-1
2. how-1
3. why-1
4. where-1

persona B:
1. where-1
2. result-1
3. who-1
4. how-1
```

作用：

- 控制 persona-semantic search unit 的选材顺序。
- 决定不同 persona 的 center_element 倾向。
- 让同一条新闻产生多个有事实支撑的电影化入口。

---

## 2.5 center_element

`center_element` 是每条 persona-semantic search unit 的主要承重元素。

它替代旧的 `focal / focalized` 概念。

旧规则的问题：

```text
focal 只能引用 who-*，过窄。
```

新版规则：

```text
center_element 可以来自任意 element 类型：
when / where / who / why / how / result
```

示例：

```text
center = where-1
A coastal city becomes the pressure chamber for an infrastructure failure.

center = result-1
A wave of public disruption exposes everyday dependence on fragile public systems.

center = how-1
Forced rationing becomes the mechanism through which a city confronts scarcity.
```

---

## 2.6 search unit

`search unit` 是进入召回层的统一单位。

新版不再区分：

```text
neutral query
fact-anchor query
toned pseudo
focalized pseudo
```

统一为：

```text
search unit
```

当前建议三类：

```text
surface-fragment-bundle
event-fragment-bundle
persona-semantic
```

---

## 3. 分层明细

## 3.1 新闻输入层

输入是一条新闻 JSON。

推荐字段：

```text
title
description
pub_time
source_name
url
```

主链路默认英文输入，避免和英文电影 overview 产生分布偏移。

---

## 3.2 新闻快照层

产物：

```text
reality.json
reality.md
```

作用：

- 固化一次 run 的新闻原文。
- 作为后续事实引用和复盘入口。
- 不改写、不解释、不扩展。

---

## 3.3 extract / 解构层

产物：

```text
facts.json
facts.md
```

> 落地物偏差：目标产物 `facts.json`（当前实际：`facts.json`）；承载脚本目标 `extract.py`（当前实际：`deconstruct.py`）。

结构：

```text
when / where / who / why / how / result
```

处理标准：

- 只记录新闻怎么说。
- 不做上位概念扩展。
- 不做人设、情绪、价值、共振解释。
- 不新增新闻没有明说的因果。
- 每个可引用事实块都有稳定 `element_id`。

这一层是全链事实地基。

---

## 3.4 Fragment ladder 层

产物：

```text
fragment-ladders.json
```

处理标准：

- 为每个 element 生成 ladder。
- ladder 包含 surface / alias / objective / interpretive / perspective 层级。
- 原 `hypernym` 能力合并进 objective levels。
- 原 `lens / alternatives` 能力合并进 interpretive / perspective levels。
- 每一项都必须绑定已有 `element_id`。
- 每一项都必须标注层级和建议权重。

建议层级：

```text
surface: 1.00
alias: 0.90–0.98
objective_close: 0.70–0.90
objective_mid: 0.45–0.70
objective_broad: 0.20–0.45
interpretive: 0.20–0.50
perspective: 0.20–0.50
```

注意：

```text
权重不是最终评分，只是召回和诊断的初始距离提示。
```

这一层不需要新增“fact-anchor agent”。更适合是一个受约束的 ladder builder：

```text
输入：element
输出：分层表达 + 权重 + 使用边界
禁止：新增事实、混淆 objective 与 interpretive
```

---

## 3.5 Persona salience 层

产物：

```text
persona-salience.json
```

处理标准：

- 每个 persona 基于同一份 element + fragment ladder 判断关注顺序。
- persona 的价值轴作为注意力清单，而不是事实改写器。
- salience 表示该 persona 对新闻元素的重要性排序。
- weak-fit persona 可以少产，不强迫覆盖。

这一层决定：

```text
每个 persona 看重哪些 element，以及更可能以哪个 center_element 组织 search unit。
```

---

## 4. Search unit 生成层

新版搜索入口分三类。

```text
surface-fragment-bundle
event-fragment-bundle
persona-semantic
```

不再使用：

```text
neutral
fact-anchor query
toned
focalized
```

---

## 4.1 surface-fragment-bundle

`surface-fragment-bundle` 用于表层元素召回和诊断。

来源：

```text
when / where / who
```

作用：

- 判断候选是否在表层接近原新闻。
- 捕捉专名、别名、角色类型、地点类型、时间类型。
- 提供 surface_match 信号。

示例：

```json
{
  "id": "su-surface-1",
  "kind": "surface-fragment-bundle",
  "source_elements": ["who-1", "where-1"],
  "fragments": [
    { "element_id": "who-1", "level": "surface", "text": "Osama bin Laden", "weight": 1.0 },
    { "element_id": "who-1", "level": "alias", "text": "bin Laden", "weight": 0.95 },
    { "element_id": "who-1", "level": "objective_close", "text": "terrorist leader", "weight": 0.85 },
    { "element_id": "where-1", "level": "objective_mid", "text": "foreign compound", "weight": 0.55 }
  ],
  "search_text": "Osama bin Laden; bin Laden; terrorist leader; foreign compound"
}
```

`search_text` 只是 fragment bundle 的召回投影，不是新的事实来源。

---

## 4.2 event-fragment-bundle

`event-fragment-bundle` 用于事件结构召回和诊断。

来源：

```text
why / how / result
```

作用：

- 判断候选是否接近新闻的起因、经过、结果。
- 捕捉事件机制，而不只是专名。
- 提供 event_match 信号。

示例：

```json
{
  "id": "su-event-1",
  "kind": "event-fragment-bundle",
  "source_elements": ["why-1", "how-1", "result-1"],
  "fragments": [
    { "element_id": "why-1", "level": "objective_close", "text": "infrastructure failure", "weight": 0.8 },
    { "element_id": "how-1", "level": "objective_close", "text": "power rationing", "weight": 0.8 },
    { "element_id": "result-1", "level": "objective_mid", "text": "public utility disruption", "weight": 0.6 }
  ],
  "search_text": "infrastructure failure causing power rationing and public utility disruption"
}
```

`event-fragment-bundle` 是原 `fact-anchor query` 的替代物。区别是：

```text
fact-anchor query 把事实揉成一句话；
event-fragment-bundle 保留碎片和层级，只把 search_text 当作召回投影。
```

---

## 4.3 persona-semantic

`persona-semantic` 是 persona 基于 salience 和 interpretive / perspective ladder 生成的电影化 search unit。

它替代旧的 `toned / focalized`。

默认质量要求：

- 英文。
- 1–2 句。
- 建议 20–60 words。
- 80 words hard max。
- 不设 60 words 下限。
- 有事实锚点。
- 有 persona 视角。
- 有自然叙事张力。
- 不新增人物、事件、动机、因果、结果。
- 每条绑定 `center_element` 和 `supporting_elements`。

建议结构：

```json
{
  "id": "su-persona-a2-1",
  "kind": "persona-semantic",
  "persona_id": "a2",
  "center_element": "result-1",
  "supporting_elements": ["why-1", "how-1", "where-1"],
  "search_text": "A city faces managed scarcity after an infrastructure failure turns emergency power rationing into public disruption.",
  "fit": "strong",
  "source_fragments": ["result-1", "why-1", "how-1", "where-1"]
}
```

不同 persona-semantic search unit 应围绕不同 center 或事实束变化，而不是简单改写同一句。

允许的 center：

```text
when-*
where-*
who-*
why-*
how-*
result-*
```

---

## 5. 运行时守卫层

在 search unit 进入召回前执行校验。

### 5.1 通用守卫

所有 search unit 必须满足：

- `source_elements` / `source_fragments` 必须引用已有 element。
- 所有 fragment 必须来自对应 element 的 fragment ladder。
- 不允许 invented event。
- 不允许 invented causality。
- 不允许 invented outcome。
- 不允许 invented inner monologue。
- 不允许正文承重元素和声明来源脱节。

---

### 5.2 fragment-bundle 守卫

`surface-fragment-bundle` 和 `event-fragment-bundle` 必须满足：

- 只使用 `surface / alias / objective_*` 层级。
- 不使用 `interpretive / perspective` 层级。
- 不绑定 persona。
- `search_text` 只能由 fragments 组装，不新增含义。

---

### 5.3 persona-semantic 守卫

`persona-semantic` 必须满足：

- 必须有 `persona_id`。
- 必须有 `center_element`。
- `center_element` 必须引用已有 element。
- `supporting_elements` 建议 1–4 个。
- 正文主承重必须和 `center_element` 一致。
- 至少包含一个 objective anchor，避免纯 interpretive 漂移。
- weak-fit persona 可以少产，不强迫写满。

不再需要这些旧规则：

```text
neutral n1 必须存在
至少保留一条非 POV 的 toned pseudo
focal 只能引用 who-*
channel: focalized
fact-anchor query 至少 1 条
```

---

## 6. Hybrid recall 层

当前纯向量召回不能稳定表达以下层级：

```text
Osama bin Laden / bin Laden
> terrorist leader / al-Qaeda leader
> organization leader / high-value target
> public figure / target figure
```

所以新版召回建议使用 hybrid recall。

### 6.1 lexical exact / alias recall

用于强匹配：

```text
surface
alias
```

例如 overview 中出现：

```text
Osama bin Laden
bin Laden
本拉登
```

应给最高匹配信号。

### 6.2 weighted ladder recall

用于中间层匹配：

```text
objective_close
objective_mid
objective_broad
```

例如 overview 中出现：

```text
terrorist leader
militant leader
organization leader
high-value target
public figure
```

根据 ladder 层级给不同权重。

### 6.3 dense embedding recall

用于捕捉非字面但语义接近的候选。

默认仍可使用：

```text
sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
```

但它不再单独决定“谁最贴”，而是作为 hybrid signal 的一部分。

### 6.4 召回层输出

每个候选应保留命中解释：

```json
{
  "tmdb_id": 123,
  "matched_fragments": [
    {
      "element_id": "who-1",
      "dimension": "who",
      "level": "alias",
      "query_text": "bin Laden",
      "matched_text": "bin Laden",
      "match_type": "lexical",
      "weight": 0.95
    },
    {
      "element_id": "who-1",
      "dimension": "who",
      "level": "objective_close",
      "query_text": "terrorist leader",
      "matched_text": "terrorist leader",
      "match_type": "lexical_or_semantic",
      "weight": 0.85
    }
  ]
}
```

---

## 7. 候选漏斗层

## 7.1 去重

同一 `tmdb_id` 被多个 search unit 命中时合并。

保留：

```text
最高 similarity
hit_sources
matched_search_unit_ids
matched_personas
matched_center_elements
matched_center_dimensions
matched_fragments
surface_match
event_match
persona_semantic_match
```

---

## 7.2 match 诊断

新版候选解释不再依赖旧 channel，而是回到 fragment 覆盖。

### surface_match

来源：

```text
when / where / who
```

含义：

```text
候选在时间、地点、人物、角色类型上离新闻有多近。
```

### event_match

来源：

```text
why / how / result
```

含义：

```text
候选是否覆盖新闻的起因、经过、结果或事件机制。
```

### persona_semantic_match

来源：

```text
persona-semantic search units
```

含义：

```text
候选是否被某些 persona 的电影化表达命中，以及它是从哪个 center_element、哪些 interpretive / perspective fragments 命中的。
```

说明：

```text
persona_semantic_match 是第三类主 match。
persona_id、center_element、matched_interpretive_fragments 都是它的解释字段，不再单独并列 persona_match。
```

示例：

```json
{
  "surface_match": {
    "who": ["terrorist leader"],
    "where": ["foreign compound"],
    "when": []
  },
  "event_match": {
    "why": ["intelligence pursuit"],
    "how": ["targeted raid"],
    "result": ["death of a high-value target"]
  },
  "persona_semantic_match": {
    "personas": ["a2"],
    "center_elements": ["result-1"],
    "center_dimensions": ["result"],
    "matched_interpretive_fragments": ["state violence", "enemy figure"]
  }
}
```

---

## 7.3 汇聚排序

旧排序依赖：

```text
channel_count
persona_count
similarity
```

新版建议改为：

```text
convergent_score
= surface_match_score
+ event_match_score
+ persona_semantic_match_score
+ persona_diversity_weight
+ center_dimension_diversity_weight
+ dense_similarity
```

核心信号：

```text
surface_match：候选是否表层接近
event_match：候选是否事件机制接近
persona_semantic_match：候选是否被 persona 的电影化语义入口命中
persona diversity：多个 persona 是否从不同角度命中
center diversity：候选是否不是只靠一个元素偶然撞上
dense similarity：局部语义相似度
```

不再使用：

```text
neutral / toned / focalized channel_count
fact_anchor_hit_weight
```

`quality_candidate` 可以改成观察字段：

```text
surface_match 或 event_match 至少一项成立
+
persona-semantic hit ≥ 1
```

但它仍不建议作为硬闸。

---

## 7.4 judge 预筛

继续使用 0/1/2 双轴 rubric。

| 表层元素 | 底层逻辑 | 分数 |
| --- | --- | --- |
| 无 | 否 | 0 |
| 无 | 是 | 1 |
| 有 | 否 | 1 |
| 有 | 是 | 2 |

表层元素标准：

- 具体、可命名、承重。
- 换一条无关新闻不能同样成立。
- 抽象权力角色不算表层，归到底层逻辑。

底层逻辑标准：

```text
新闻和电影共享同一个因果-赌注引擎。
```

必须能写出一句：

```text
X 在约束 Z 下驱动 Y
```

这句话要同时适用于新闻和电影。

预筛动作：

```text
judge = 0  → downgrade
judge ≥ 1 → manual review
judge = 2 → highlight
```

judge 仍只做预筛，不做最终裁决。

---

## 7.5 人工预算 / audit pool

进入人工视野的候选由预算控制。

默认口径可沿用：

```text
human budget / max candidates = 19
judge ≥ 1 进入人工候选池
超出预算但 judge 通过的候选进入 audit_pool
judge = 0 堆按比例抽审
```

禁止靠提高 judge 阈值硬控量。

---

## 8. 人工共振评审 / GATE 层

人工主分继续使用：

```text
共振分: 0 / 1 / 2
```

### 0 分

无承重表层，也无可证伪底层逻辑。

通常是：

```text
偶然词面重叠
泛泛主题相似
换一条新闻也能解释这部片
```

### 1 分

只中一轴：

```text
仅表层沾边
或
仅底层逻辑成立
```

### 2 分

表层元素和底层逻辑同时成立。

```text
具体元素像
+
因果-赌注引擎也像
```

### 视角 / 尺度变化

旧的 `POV变换` 不再和 `focalized` channel 绑定。

它可以作为人工子标签保留：

```text
这条强共振是否需要通过视角或尺度变化才看得出来？
```

例如：

```text
机构级新闻 ↔ 个人级电影
城市级事件 ↔ 家庭级故事
短期新闻事件 ↔ 长期命运结构
```

该标签只在 `共振分 = 2` 时有意义，不作为硬闸。

---

## 9. 新旧概念映射

| 旧概念 | 新位置 | 处理方式 |
| --- | --- | --- |
| `hypernym` | `fragment ladder.objective_*` | 删除独立层，保留客观上位能力 |
| `lens` | `fragment ladder.interpretive / perspective` | 删除独立概念，保留解释性表达能力 |
| `alternative` | `fragment ladder` | 不再单独散落，进入统一 ladder |
| `neutral` | `surface/event fragment bundles` | 删除 per persona channel，用 fragment 搜索承担事实参照 |
| `fact-anchor query` | `event-fragment-bundle.search_text` | 删除核心概念，只保留 bundle 的召回投影 |
| `toned` | `persona-semantic` 的默认质量要求 | 删除 channel，保留电影化表达 |
| `focalized` | `center_element` | 删除 who-only POV 概念，改成任意 element 可成为中心 |
| `focal` | `center_element` | 不再限制为 `who-*` |
| `channel_count` | surface/event/persona-semantic + persona/center diversity | 不再按旧 channel 汇聚 |
| `POV变换` | 人工评审子标签 | 和生成通道解耦 |

---

## 10. 新版 workflow 的核心判断句

新版处理标准可以压缩成一句话：

> 先用 element 固定事实边界，再用 fragment ladder 保留不同距离的表达层级，用 surface/event/persona search units 做 hybrid recall，最后通过 surface_match、event_match、persona_semantic_match、judge 和人工双轴评审收敛到真正共振的电影。

---

## 11. 推荐的最小产物集合

一次 run 最小需要这些产物：

```text
reality.json
facts.json
fragment-ladders.json
persona-salience.json
search-units.json
recall-results.json
candidates.json
judge-results.json
manual-review.md / manual-review.json
```

`search-units.json` 建议结构：

```json
{
  "surface_fragment_bundles": [
    {
      "id": "su-surface-1",
      "kind": "surface-fragment-bundle",
      "source_elements": ["who-1", "where-1"],
      "search_text": "Osama bin Laden; bin Laden; terrorist leader; foreign compound"
    }
  ],
  "event_fragment_bundles": [
    {
      "id": "su-event-1",
      "kind": "event-fragment-bundle",
      "source_elements": ["why-1", "how-1", "result-1"],
      "search_text": "infrastructure failure causing power rationing and public utility disruption"
    }
  ],
  "persona_semantic_units": [
    {
      "id": "su-persona-a2-1",
      "kind": "persona-semantic",
      "persona_id": "a2",
      "center_element": "result-1",
      "supporting_elements": ["why-1", "how-1", "where-1"],
      "search_text": "A city faces managed scarcity after an infrastructure failure turns emergency power rationing into public disruption.",
      "fit": "strong",
      "source_fragments": ["result-1", "why-1", "how-1", "where-1"]
    }
  ]
}
```

---

## 12. 不建议再保留的旧约束

以下旧约束建议删除：

```text
独立 reality-expanded / hypernym 层
每个 persona 必须有 neutral n1
neutral / toned / focalized 三通道并列
fact-anchor query 至少 1 条
focal 只能引用 who-*
至少保留一条非 POV 的 toned pseudo
channel_count 作为核心汇聚维度
neutral coverage 作为独立质量指标
60–120 words 硬长度要求
```

替代约束：

```text
每个 element 必须有 fragment ladder
ladder 必须区分 objective 和 interpretive / perspective
surface/event fragment bundles 只能使用 objective levels
persona-semantic 必须有 center_element
center_element 可来自任意 element 类型
每条 search unit 必须绑定 source elements
persona-semantic 必须有 objective anchor
persona-semantic 建议 20–60 words，80 words hard max，不设最低 60 words
候选排序关注 surface_match、event_match、persona_semantic_match、persona diversity、center diversity 和 dense similarity
```