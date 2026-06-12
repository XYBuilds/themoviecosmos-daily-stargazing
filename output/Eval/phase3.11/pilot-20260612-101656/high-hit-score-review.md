# High Pseudo Hit Score — Unified Review

## Criteria

### Pseudo 命中分（二级审阅键 · 非质量闸）

**High-hit review** lists candidates with **pseudo命中分合计 ≥ 5**.
`surface/event` objective hits are diagnostic; only persona-semantic search units contribute to the inline pseudo命中分.
Inclusion is **not** a quality gate; `quality_candidate` means objective surface/event evidence plus persona-semantic evidence.

For each scored hit line under **命中视角/碎片**, count entries in `fragments=[...]`
— **each fragment id = 1 point** for that persona-semantic search unit.
Surface/event bundle lines stay visible as diagnostics but do not receive inline 命中分.

- **Candidate 总分** (`pseudo命中分合计`) = sum of persona-semantic 命中分 across all hit lines.
- **自动打分** shows candidate-level retrieve signals: objective_match, persona_semantic_match, convergent_score, source_hits, center_dimensions, and baseline_overlap.
- Shown inline per scored line, e.g. `A2/su-persona-...: fragments=[...] · sim=... · **命中分=3**`.

### Per-news layout

- News sections follow `tests/eval_news/batch-manifest.json` order (01–10).
- Each section opens with that run's `reality.md`.
- **多 agents 命中**: ≥2 agents in heading / hit_sources; `quality_candidate` is displayed only as annotation.
- **单 agent 命中**: all other high-hit candidates.
- Within each subsection, sort by **pseudo命中分合计** descending.

### Sources

- **Primary:** `hit_sources` in each run's `retrieve.json` (fragment arrays).
- **LLM judge:** `llm-judge-scores.json` — trust_status=不采信 (screening only; separate LLM Judge block per candidate)
- **Editor fields:** 共振分 / 共振类型 / 打分备注 are placeholders only (not filled by this script).

- **Generation date:** 2026-06-12
- **Total candidates (≥5):** 10
- **Runs scanned:** 1

## 01-grid-outage

# 现实波澜 · 01-grid-outage

## 元信息
- date: 2026-05-29
- news_url: https://mb.com.ph/2026/05/29/rotational-blackout-risks-rise-in-visayas-amid-power-crunch
- run_id: 01-grid-outage

## 现实波澜
- **title**: Rotational blackout risks rise in Visayas amid power crunch
- **source** / **pub_time**: Manila Bulletin / 2026-05-29T18:00:00+08:00
- **summary**: The Philippines grid operator placed the Visayas under red alert after Kepco SPC Power's Unit 2 tripped offline, leaving more than 950 megawatts unavailable alongside other long-running plant outages. Eleven generators have failed since May began, while seasonal heat drove demand into a thin operating margin. Officials ordered emergency load shedding to keep a critical 230-kilovolt transmission line from overloading.

### 多 agents 命中

**Count:** 7 candidate(s)

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 80 -->
### Survival Family (2017) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-JESTER] [汇聚标注]
- **tmdb_id**: 429918
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=false, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 422.6321
  - **persona_agent_count**: 11
  - **source_hits**: surface=0 / event=11 / persona=21
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic
  - **center_dimensions**: how, result, who, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=11: THE-OUTLAW,THE-EXPLORER,THE-JESTER,THE-HERO,THE-EVERYMAN,THE-CAREGIVER,THE-INNOCENT,THE-RULER,THE-LOVER,THE-MAGICIAN,THE-SAGE
- **相似度**: 0.6321
- **genres** / **language**: Comedy, Drama, Adventure / ja
- **overview**: A world wide electrical outage occurs. Everything that requires electricity comes to a stop. Tokyo is nearly ruined. Yoshiyuki Suzuki decides to escape from Tokyo with his family.
- **跳转**: https://themoviecosmos.com/movie/429918
- **命中视角/碎片**:
  - THE-INNOCENT/su-event-1: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, result-0] · sim=0.4759
  - THE-EVERYMAN/su-event-1: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, result-0] · sim=0.4941
  - THE-HERO/su-event-1: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, result-0] · sim=0.4815
  - THE-CAREGIVER/su-event-1: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, result-0] · sim=0.4758
  - THE-EXPLORER/su-event-1: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, result-0] · sim=0.4867
  - THE-OUTLAW/su-event-1: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, result-0] · sim=0.4757
  - THE-LOVER/su-event-1: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, result-0] · sim=0.4796
  - THE-RULER/su-event-1: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, result-0] · sim=0.4808
  - THE-MAGICIAN/su-event-1: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, result-0] · sim=0.4814
  - THE-SAGE/su-event-1: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, result-0] · sim=0.4969
  - THE-JESTER/su-event-1: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, result-0] · sim=0.4898
  - THE-CAREGIVER/su-persona-The-Caregiver-p1: fragments=[result-0, why-0, how-1] · sim=0.5446 · **命中分=3**
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[who-1, why-0, how-2, why-1] · sim=0.5304 · **命中分=4**
  - THE-EVERYMAN/su-persona-The-Everyman-p1: fragments=[result-0, why-0, how-1, how-2] · sim=0.5713 · **命中分=4**
  - THE-EVERYMAN/su-persona-The-Everyman-p2: fragments=[how-2, why-0, why-2, how-1] · sim=0.4744 · **命中分=4**
  - THE-EVERYMAN/su-persona-The-Everyman-p3: fragments=[who-1, why-0, why-1, how-1, result-0] · sim=0.5230 · **命中分=5**
  - THE-EXPLORER/su-persona-The-Explorer-p3: fragments=[who-0, why-0, why-2, how-1, result-0] · sim=0.5017 · **命中分=5**
  - THE-HERO/su-persona-The-Hero-p2: fragments=[how-2, why-0, how-1] · sim=0.4851 · **命中分=3**
  - THE-INNOCENT/su-persona-The-Innocent-p1: fragments=[how-2, why-0, how-1, result-0] · sim=0.4986 · **命中分=4**
  - THE-INNOCENT/su-persona-The-Innocent-p2: fragments=[result-0, why-0, why-1, why-2] · sim=0.5223 · **命中分=4**
  - THE-INNOCENT/su-persona-The-Innocent-p3: fragments=[who-1, why-0, how-0, how-1, result-0] · sim=0.6321 · **命中分=5**
  - THE-JESTER/su-persona-The-Jester-p2: fragments=[result-0, why-0, why-1, why-2] · sim=0.5264 · **命中分=4**
  - THE-JESTER/su-persona-The-Jester-p3: fragments=[who-0, why-0, how-1, result-0] · sim=0.4841 · **命中分=4**
  - THE-LOVER/su-persona-The-Lover-p2: fragments=[why-2, why-0, why-1, how-0] · sim=0.5254 · **命中分=4**
  - THE-MAGICIAN/su-persona-The-Magician-p3: fragments=[how-2, why-0, result-0] · sim=0.5542 · **命中分=3**
  - THE-OUTLAW/su-persona-The-Outlaw-p1: fragments=[who-0, how-1, why-0, result-0] · sim=0.4765 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p3: fragments=[why-0, why-1, why-2] · sim=0.5940 · **命中分=3**
  - THE-RULER/su-persona-The-Ruler-p2: fragments=[who-0, why-0, why-1, why-2] · sim=0.4795 · **命中分=4**
  - THE-RULER/su-persona-The-Ruler-p3: fragments=[how-0, how-1, how-2] · sim=0.4844 · **命中分=3**
  - THE-SAGE/su-persona-The-Sage-p1: fragments=[result-0, why-0, how-1, how-2] · sim=0.4980 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p2: fragments=[why-0, why-1, how-0] · sim=0.5751 · **命中分=3**
  - THE-SAGE/su-persona-The-Sage-p3: fragments=[why-1, why-2, how-2] · sim=0.4924 · **命中分=3**
- **pseudo命中分合计**: 80
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）
- **LLM Judge（自动评审）**:
  - **judge分**: 2
  - **judge共振类型**: 强共振（表层 + 逻辑）
  - **judge采信**: 不采信 · screening only
  - **judge因果反测**: Electrical power failure under constraint of high societal dependence on electricity drives emergency survival measures, such as load shedding by authorities and escape by families.
  - **judge理由**: Both stories center on electrical outage as a load-bearing surface element. The underlying logic—power crisis forcing survival actions—is consistent across institutional (news) and individual (film) scales, with the causal test holding specifically for this pair.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 37 -->
### Geostorm (2017) [THE-CAREGIVER, THE-CREATOR, THE-HERO, THE-INNOCENT, THE-MAGICIAN, THE-OUTLAW, THE-RULER, THE-SAGE]
- **tmdb_id**: 274855
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 312.5737
  - **persona_agent_count**: 8
  - **source_hits**: surface=0 / event=0 / persona=10
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result, who, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5737
- **genres** / **language**: Action, Science Fiction, Thriller / en
- **overview**: After an unprecedented series of natural disasters threatened the planet, the world's leaders came together to create an intricate network of satellites to control the global climate and keep everyone safe. But now, something has gone wrong: the system built to protect Earth is attacking it, and it becomes a race against the clock to uncover the real threat before a worldwide geostorm wipes out everything and everyone along with it.
- **跳转**: https://themoviecosmos.com/movie/274855
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p3: fragments=[who-3, why-2, result-0, how-2] · sim=0.5383 · **命中分=4**
  - THE-CREATOR/su-persona-The-Creator-p1: fragments=[how-1, why-0, why-1] · sim=0.4465 · **命中分=3**
  - THE-HERO/su-persona-The-Hero-p3: fragments=[who-2, why-0, why-1, how-2] · sim=0.5310 · **命中分=4**
  - THE-INNOCENT/su-persona-The-Innocent-p1: fragments=[how-2, why-0, how-1, result-0] · sim=0.5737 · **命中分=4**
  - THE-MAGICIAN/su-persona-The-Magician-p1: fragments=[how-1, how-0, how-2, result-0] · sim=0.5363 · **命中分=4**
  - THE-MAGICIAN/su-persona-The-Magician-p2: fragments=[why-2, why-0, why-1, how-1] · sim=0.4547 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p2: fragments=[how-2, how-0, how-1, result-0] · sim=0.5194 · **命中分=4**
  - THE-RULER/su-persona-The-Ruler-p3: fragments=[how-0, how-1, how-2] · sim=0.4430 · **命中分=3**
  - THE-SAGE/su-persona-The-Sage-p1: fragments=[result-0, why-0, how-1, how-2] · sim=0.4478 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p3: fragments=[why-1, why-2, how-2] · sim=0.5273 · **命中分=3**
- **pseudo命中分合计**: 37
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）
- **LLM Judge（自动评审）**:
  - **judge分**: 0
  - **judge共振类型**: 
  - **judge采信**: 不采信 · screening only
  - **judge理由**: No shared concrete surface element (power grid vs. climate satellites); underlying logic is too broad and fails specificity test (e.g., 'critical infrastructure failure under constraints drives crisis management' applies to unrelated news).

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 13 -->
### 2061 - Un anno eccezionale (2007) [THE-CAREGIVER, THE-CREATOR, THE-INNOCENT, THE-RULER]
- **tmdb_id**: 33495
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 264.5282
  - **persona_agent_count**: 4
  - **source_hits**: surface=0 / event=0 / persona=4
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5282
- **genres** / **language**: Comedy, Science Fiction / it
- **overview**: In a post-apocalyptic future, the Italian peninsula is going through a dark moment due to a terrible energy crisis.
- **跳转**: https://themoviecosmos.com/movie/33495
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p1: fragments=[result-0, why-0, how-1] · sim=0.5282 · **命中分=3**
  - THE-CREATOR/su-persona-The-Creator-p3: fragments=[why-0, why-2] · sim=0.4948 · **命中分=2**
  - THE-INNOCENT/su-persona-The-Innocent-p2: fragments=[result-0, why-0, why-1, why-2] · sim=0.5081 · **命中分=4**
  - THE-RULER/su-persona-The-Ruler-p2: fragments=[who-0, why-0, why-1, why-2] · sim=0.4578 · **命中分=4**
- **pseudo命中分合计**: 13
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）
- **LLM Judge（自动评审）**:
  - **judge分**: 2
  - **judge共振类型**: 强共振（表层 + 逻辑）
  - **judge采信**: 不采信 · screening only
  - **judge因果反测**: Acute energy supply disruption, under the constraint of preventing systemic collapse, drives the implementation of emergency power rationing measures.
  - **judge理由**: Surface element: both stories center on energy crises/power shortages. Underlying logic: supply failures and high demand under grid stability constraints force load shedding or rationing to avert collapse.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 10 -->
### Blade Runner: Black Out 2022 (2017) [THE-CAREGIVER, THE-CREATOR, THE-JESTER]
- **tmdb_id**: 475946
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 246.5168
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5168
- **genres** / **language**: Action, Animation, Science Fiction / en
- **overview**: This animated short revolves around the events causing an electrical systems failure on the west coast of the US. According to Blade Runner 2049’s official timeline, this failure leads to cities shutting down, financial and trade markets being thrown into chaos, and food supplies dwindling. There’s no proof as to what caused the blackouts, but Replicants — the bio-engineered robots featured in the original Blade Runner, are blamed.
- **跳转**: https://themoviecosmos.com/movie/475946
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[who-1, why-0, how-2, why-1] · sim=0.5168 · **命中分=4**
  - THE-CREATOR/su-persona-The-Creator-p3: fragments=[why-0, why-2] · sim=0.5168 · **命中分=2**
  - THE-JESTER/su-persona-The-Jester-p3: fragments=[who-0, why-0, how-1, result-0] · sim=0.4693 · **命中分=4**
- **pseudo命中分合计**: 10
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）
- **LLM Judge（自动评审）**:
  - **judge分**: 0
  - **judge共振类型**: 
  - **judge采信**: 不采信 · screening only
  - **judge理由**: Surface element 'power blackout' is generic and fails the 0-guard; underlying logic lacks a specific causal engine unique to this pair as any blackout news could equally match the film's premise.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 8 -->
### Stranded (2021) [THE-CAREGIVER, THE-MAGICIAN]
- **tmdb_id**: 841793
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 236.5469
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5469
- **genres** / **language**: Drama / pt
- **overview**: Tensions run high while food runs low as six influencers find themselves stranded on a secluded island after plans for a weekend escape go awry.
- **跳转**: https://themoviecosmos.com/movie/841793
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p3: fragments=[who-3, why-2, result-0, how-2] · sim=0.5469 · **命中分=4**
  - THE-MAGICIAN/su-persona-The-Magician-p2: fragments=[why-2, why-0, why-1, how-1] · sim=0.4886 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）
- **LLM Judge（自动评审）**:
  - **judge分**: 0
  - **judge共振类型**: 
  - **judge采信**: 不采信 · screening only
  - **judge理由**: No concrete surface element shared (power grid vs. island survival). Underlying logic of crisis-driven scarcity response is generic and fails the specificity test, as it would hold for unrelated crisis news paired with the film.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 7 -->
### Contagion of Fear (2023) [THE-MAGICIAN, THE-OUTLAW]
- **tmdb_id**: 1223272
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 228.5156
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5156
- **genres** / **language**: Science Fiction, Thriller / en
- **overview**: A catastrophic train derailment sends the city spiraling into chaos. But the derailment is just the beginning. A biological gas attack sees crash survivors collapsing and dying within minutes. And the sickness is rapidly spreading.
- **跳转**: https://themoviecosmos.com/movie/1223272
- **命中视角/碎片**:
  - THE-MAGICIAN/su-persona-The-Magician-p3: fragments=[how-2, why-0, result-0] · sim=0.5053 · **命中分=3**
  - THE-OUTLAW/su-persona-The-Outlaw-p2: fragments=[how-2, how-0, how-1, result-0] · sim=0.5156 · **命中分=4**
- **pseudo命中分合计**: 7
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）
- **LLM Judge（自动评审）**:
  - **judge分**: 0
  - **judge共振类型**: 
  - **judge采信**: 不采信 · screening only
  - **judge理由**: No concrete, load-bearing surface element (e.g., place, occupation, event type) shared between the news and film. For underlying logic, a general causal-stakes sentence (e.g., 'critical system failure under constraints drives cascading disruption') could be written but would apply to unrelated news items paired with the film, failing the logic 0-guard and specificity requirement.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 6 -->
### Metro Manila (2013) [THE-HERO, THE-RULER]
- **tmdb_id**: 158091
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 228.4830
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4830
- **genres** / **language**: Crime, Thriller, Drama, Action / tl
- **overview**: Looking for a brighter future in metropolitan Manila, Oscar Ramirez and his family leave their miserable life in the rice terraces of Banaue, in the northern Philippines. In the sweltering capital, where all kind of perils lurk in every corner, Oscar catches a lucky break when he is offered a steady work for an armored truck company and the senior officer Ong takes him under his wing.
- **跳转**: https://themoviecosmos.com/movie/158091
- **命中视角/碎片**:
  - THE-HERO/su-persona-The-Hero-p1: fragments=[result-0, how-1, how-2] · sim=0.4830 · **命中分=3**
  - THE-RULER/su-persona-The-Ruler-p1: fragments=[result-0, why-0, how-1] · sim=0.4638 · **命中分=3**
- **pseudo命中分合计**: 6
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）
- **LLM Judge（自动评审）**:
  - **judge分**: 0
  - **judge共振类型**: 
  - **judge采信**: 不采信 · screening only
  - **judge理由**: No concrete load-bearing surface element shared (news on Visayas power crisis, film on Manila personal struggles). No invariant causal-stakes engine: cannot write a specific 'X under constraint Z drives Y' sentence true for both without over-generalization, failing the falsifiable counter-test.

### 单 agent 命中

**Count:** 3 candidate(s)

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 7 -->
### Re-Generator (2010) [THE-HERO]
- **tmdb_id**: 194834
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 226.5323
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5323
- **genres** / **language**: Action, Science Fiction / en
- **overview**: A plane containing a highly classified government project crashes outside of a small town in the US. Realizing the level of danger, the government tries to secretly fix the problem. As tensions grow, the situation gets out of control, and civilians from the town find themselves facing their worst nightmare: a genetically enhanced killing machine that doesn't know how to stop.
- **跳转**: https://themoviecosmos.com/movie/194834
- **命中视角/碎片**:
  - THE-HERO/su-persona-The-Hero-p2: fragments=[how-2, why-0, how-1] · sim=0.4761 · **命中分=3**
  - THE-HERO/su-persona-The-Hero-p3: fragments=[who-2, why-0, why-1, how-2] · sim=0.5323 · **命中分=4**
- **pseudo命中分合计**: 7
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）
- **LLM Judge（自动评审）**:
  - **judge分**: 1
  - **judge共振类型**: 深层共振（仅逻辑，无表层）
  - **judge采信**: 不采信 · screening only
  - **judge因果反测**: Under constraint of high operational stress and limited contingency, a critical system failure drives the necessity of emergency measures to prevent catastrophic loss.
  - **judge理由**: No concrete surface element shared (power grid vs. plane crash/genetic experiment). Underlying logic aligns: failure of a controlled system under pressure escalates into crisis requiring drastic intervention, valid for both news (power plant failures driving load shedding) and film (project crash driving civilian confrontation).

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Stormageddon (2015) [THE-EVERYMAN]
- **tmdb_id**: 370097
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 218.5022
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5022
- **genres** / **language**: Action, Drama, Thriller, Science Fiction / en
- **overview**: What happens when you ask the most powerful computer program, run by the most powerful computers, to follow, listen and predict human behavior? The program learns, becomes sentient and begins to behave like a human. When a master computer program, Echelon, takes over America's entire online system, our country is threatened to be brought to its knees. Hacking into DARPA, Echelon gains the ability to manipulate the weather, create earthquakes, and cause a level of destruction unlike anything the country could ever imagine. But how do you stop a computer program when it has control over any and every defense you have?
- **跳转**: https://themoviecosmos.com/movie/370097
- **命中视角/碎片**:
  - THE-EVERYMAN/su-persona-The-Everyman-p3: fragments=[who-1, why-0, why-1, how-1, result-0] · sim=0.5022 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）
- **LLM Judge（自动评审）**:
  - **judge分**: 0
  - **judge共振类型**: 
  - **judge采信**: 不采信 · screening only
  - **judge理由**: No concrete, load-bearing surface element shared (news focuses on power grid failure, film on sentient AI takeover). Underlying logics differ: news driven by operational failure and demand scarcity, film by malicious AI control; cannot write a single 'X under constraint Z drives Y' sentence that is literally true of both and passes the logic 0-guard (e.g., unrelated news items could fit the film's engine).

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Flashover (2023) [THE-INNOCENT]
- **tmdb_id**: 949698
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 218.4733
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4733
- **genres** / **language**: Drama, Action / zh
- **overview**: A large blast hits the gas pipeline in the industrial park due to a sudden earthquake, which triggers massive explosions and engulfs the neighboring area in flames. Facing the escalating fire danger, the Fire and Rescue Force quickly reaches the hazardous zone to hold the fire and cut a firebreak, in the meantime, many survivors are pulled out of the rubble.
- **跳转**: https://themoviecosmos.com/movie/949698
- **命中视角/碎片**:
  - THE-INNOCENT/su-persona-The-Innocent-p3: fragments=[who-1, why-0, how-0, how-1, result-0] · sim=0.4733 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）
- **LLM Judge（自动评审）**:
  - **judge分**: 0
  - **judge共振类型**: 
  - **judge采信**: 不采信 · screening only
  - **judge理由**: No shared load-bearing surface element (blackout risks vs. gas pipeline explosion). Underlying causal engines differ: news involves power supply-demand imbalance driving load shedding, while film involves natural disaster driving fire rescue; no specific 'X under constraint Z drives Y' sentence holds for both without failing the logic 0-guard (e.g., a broad sentence like 'sudden crisis drives emergency response' applies to many unrelated news items paired with the film).

