# Fragment ladder / search unit 架构迁移

**Status**: accepted（Phase 3.11.8 GATE go, 2026-06-13）；**supersedes ADR-0008 的通道结构部分**（D3 保留元素中心思想；D4 POV 下线为通用 `center_element`；D5 双地板下线；D6 provenance 粗归因改为 `search_unit_kind` 分解；D8 漏斗改为 match 诊断 + 新 convergent sort）

> 权威设计源：[`docs/temp/simplified-news-to-film-workflow.md`](../temp/simplified-news-to-film-workflow.md)。本 ADR 把 3.11.6b 的工程迁移决策钉成可执行口径。

## 背景

ADR-0008 把生成层从 valence 覆盖迁移到元素中心构图，并添加 `neutral / toned / focalized` 三通道 provenance。3.11.6 pilot 后，总编决定继续下探一层：候选召回不应围绕“pseudo 通道”组织，而应围绕新闻 element 的可审计碎片和搜索用途组织。

旧三通道的主要负担：

- `neutral` 同时承担事实地板、诊断和召回入口，语义过载。
- `toned` / `focalized` 把表达风格误升为检索架构，导致 POV 被当成独立通道维护。
- `hypernym` / `alternative` / `lens` 分散在不同结构里，难以解释“同一 element 的距离层级”。
- 汇聚排序依赖 `channel_count`，容易奖励旧 channel 撞车，而不是奖励 surface/event/persona 语义的真实收敛。

## 决策

### D1 · Fragment ladder 替代 hypernym / alternative / lens 分散结构

每个 decon element 生成一个 `fragment ladder`，层级固定为：

```text
surface / alias / objective_close / objective_mid / objective_broad / interpretive / perspective
```

- `surface` 来自 A0 原文。
- `alias` / `objective_*` 吸收原 shared hypernym / objective expansion 能力。
- `interpretive` / `perspective` 吸收 persona alternative / lens 能力。
- 每个 fragment 必须绑定已有 `element_id`，不得新增人物、事件、因果、结果。

### D2 · Search unit 成为唯一召回入口

旧 `neutral / toned / focalized / fact-anchor query` 下线，统一为三类 search unit：

```text
surface-fragment-bundle
event-fragment-bundle
persona-semantic
```

- `surface-fragment-bundle`：来自 `when / where / who`，只用 objective levels，提供 `surface_match`。
- `event-fragment-bundle`：来自 `why / how / result`，只用 objective levels，提供 `event_match`。
- `persona-semantic`：由 persona 结合 salience 与 interpretive/perspective 材料生成，绑定 `center_element` + `supporting_elements`，提供 `persona_semantic_match`。

当前代码仍保留 `pseudos[]` wrapper 作为 LLM/parser 兼容层，但检索优先读取 `agents[].search_units`。

### D3 · POV 下线为通用 center_element

`focalized` 不再是运行时主通道。视角/尺度变换仍可作为文本效果和人工 `POV变换` 子标签存在，但生成与检索层不再维护单独 POV channel。

通用规则：

```text
persona-semantic.center_element = 任意既有 element id
supporting_elements = 1–4 个既有 element id
```

### D4 · 守卫迁移

- fragment bundle 只能使用 objective levels。
- fragment bundle 不绑定 persona。
- persona-semantic 必须有 `persona_id`、`center_element`、`supporting_elements`。
- persona-semantic 必须有至少一个 objective anchor，避免纯 interpretive 漂移。
- 所有 source elements 必须来自 decon element ids。
- 旧 dual-floor / neutral-n1 / focalized hard guard 下线。

### D5 · 新 convergent sort

旧排序：

```text
channel_count * 100 + persona_count * 10 + similarity
```

新排序：

```text
surface_match_score
+ event_match_score
+ persona_semantic_match_score
+ persona_diversity_weight
+ center_dimension_diversity_weight
+ dense_similarity
```

核心解释字段：

```text
surface_match
event_match
persona_semantic_match
search_unit_kinds
center_dimensions
triggered_by
```

`quality_candidate` 改成观察字段：

```text
(surface_match OR event_match) + persona_semantic_match
```

不作为硬闸。

### D6 · A/B 分解口径改为 search_unit_kind

3.11.7 / 3.11.8 不再按 `neutral / toned / focalized` 分解池差，改为：

```text
surface-fragment-bundle 独家
event-fragment-bundle 独家
persona-semantic 独家
撞车增益（>=2 类 search unit 同命中）
```

`POV变换` 仍留在人工/judge 评审字段中，用于解释强共振是否依赖视角/尺度转换。

## 后果 / 已知局限

- 旧产物和历史测试仍含 `neutral / toned / focalized` 字段；这些字段仅作为兼容层存在，不再驱动主路径排序。
- 当前 hybrid recall 的 lexical / weighted ladder 子信号还未完全展开；本轮先把 search unit schema、match 诊断和 convergent sort 接入，dense embedding 仍保留为召回底座。
- LLM screenwriter 仍返回 `pseudos[]`，代码再映射到 `persona-semantic`；后续可把输出 contract 原生改成 `search_units[]`。
- 3.10 基线仍按历史 pseudo 产物对照；3.11.7 归因必须写明这是 ADR-0009 整包设计-on。

## SSOT 待同步

- [`scripts/personas.py`](../../scripts/personas.py)：fragment ladder / search unit 生成与守卫。
- [`scripts/retrieve.py`](../../scripts/retrieve.py)：search unit 优先检索、新 convergent sort、`search_unit_kind` 池差分解。
- [`prompts/_shared/persona_screenwriter_contract.md`](../../prompts/_shared/persona_screenwriter_contract.md)：persona-semantic 草稿契约。
- [`prompts/_shared/persona_alt_creator_contract.md`](../../prompts/_shared/persona_alt_creator_contract.md)：alt-pool 作为 fragment ladder 输入。
- [`docs/temp/simplified-news-to-film-workflow.md`](../temp/simplified-news-to-film-workflow.md)：工作流说明源。
- [ADR-0008](0008-salience-driven-element-composition-and-multi-vantage-pov.md)：标注通道结构被本 ADR supersede。

## 相关 ADR / 文档

- [ADR-0008](0008-salience-driven-element-composition-and-multi-vantage-pov.md) — 元素中心构图与 POV 追加通道；本 ADR supersede 其通道结构与双地板。
- [ADR-0007](0007-logic-resonance-judge-prescreen-and-pov-focalization.md) — 双轴 rubric 与 judge 预筛继续有效。
- [`docs/temp/simplified-news-to-film-workflow.md`](../temp/simplified-news-to-film-workflow.md) — fragment ladder 精简版工作流草案。