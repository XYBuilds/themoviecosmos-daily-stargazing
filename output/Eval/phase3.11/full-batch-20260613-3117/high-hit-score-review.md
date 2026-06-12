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
- **Editor fields:** 共振分 / 共振类型 / 打分备注 are placeholders only (not filled by this script).

- **Generation date:** 2026-06-13
- **Total candidates (≥5):** 110
- **Runs scanned:** 10

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
<!-- pseudo命中分合计: 54 -->
### Survival Family (2017) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-CREATOR] [汇聚标注]
- **tmdb_id**: 429918
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=false, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 302.6126
  - **persona_agent_count**: 9
  - **source_hits**: surface=0 / event=10 / persona=15
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic
  - **center_dimensions**: how, result, who, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=9: THE-HERO,THE-OUTLAW,THE-CAREGIVER,THE-MAGICIAN,THE-SAGE,THE-CREATOR,THE-INNOCENT,THE-EVERYMAN,THE-LOVER
- **相似度**: 0.6126
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
  - THE-CAREGIVER/su-persona-The-Caregiver-p1: fragments=[who-1, why-0, how-1, result-0] · sim=0.5918 · **命中分=4**
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[who-3, why-1, why-2, how-2] · sim=0.5140 · **命中分=4**
  - THE-CAREGIVER/su-persona-The-Caregiver-p3: fragments=[why-0, why-2, how-1] · sim=0.5396 · **命中分=3**
  - THE-CREATOR/su-persona-The-Creator-p1: fragments=[how-1, why-0, result-0] · sim=0.4734 · **命中分=3**
  - THE-EVERYMAN/su-persona-The-Everyman-p3: fragments=[who-1, why-0, why-1, result-0] · sim=0.4749 · **命中分=4**
  - THE-HERO/su-persona-The-Hero-p1: fragments=[result-0, how-2, why-0] · sim=0.5693 · **命中分=3**
  - THE-HERO/su-persona-The-Hero-p2: fragments=[how-1, why-1, why-0] · sim=0.4200 · **命中分=3**
  - THE-HERO/su-persona-The-Hero-p3: fragments=[why-0, how-1, result-0] · sim=0.6126 · **命中分=3**
  - THE-INNOCENT/su-persona-The-Innocent-p3: fragments=[how-2, why-0, why-2, result-0] · sim=0.5745 · **命中分=4**
  - THE-LOVER/su-persona-The-Lover-p1: fragments=[why-0, why-1, result-0] · sim=0.5580 · **命中分=3**
  - THE-MAGICIAN/su-persona-The-Magician-p1: fragments=[how-1, why-0, why-1, why-2, result-0] · sim=0.4797 · **命中分=5**
  - THE-MAGICIAN/su-persona-The-Magician-p3: fragments=[how-2, how-0, result-0] · sim=0.4865 · **命中分=3**
  - THE-OUTLAW/su-persona-The-Outlaw-p1: fragments=[how-2, why-0, how-1, result-0] · sim=0.4796 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p3: fragments=[who-0, how-1, how-2, result-0] · sim=0.5021 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p2: fragments=[why-0, why-1, why-2, how-0] · sim=0.4735 · **命中分=4**
- **pseudo命中分合计**: 54
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 14 -->
### 2061 - Un anno eccezionale (2007) [THE-CAREGIVER, THE-CREATOR, THE-EXPLORER]
- **tmdb_id**: 33495
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 138.5359
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5359
- **genres** / **language**: Comedy, Science Fiction / it
- **overview**: In a post-apocalyptic future, the Italian peninsula is going through a dark moment due to a terrible energy crisis.
- **跳转**: https://themoviecosmos.com/movie/33495
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[who-3, why-1, why-2, how-2] · sim=0.5359 · **命中分=4**
  - THE-CREATOR/su-persona-The-Creator-p3: fragments=[who-0, why-0, why-1, why-2, result-0] · sim=0.5030 · **命中分=5**
  - THE-EXPLORER/su-persona-The-Explorer-p2: fragments=[who-0, how-1, result-0, why-2, why-0] · sim=0.4694 · **命中分=5**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 14 -->
### Geostorm (2017) [THE-CREATOR, THE-MAGICIAN, THE-OUTLAW, THE-SAGE]
- **tmdb_id**: 274855
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 156.5268
  - **persona_agent_count**: 4
  - **source_hits**: surface=0 / event=0 / persona=4
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5268
- **genres** / **language**: Action, Science Fiction, Thriller / en
- **overview**: After an unprecedented series of natural disasters threatened the planet, the world's leaders came together to create an intricate network of satellites to control the global climate and keep everyone safe. But now, something has gone wrong: the system built to protect Earth is attacking it, and it becomes a race against the clock to uncover the real threat before a worldwide geostorm wipes out everything and everyone along with it.
- **跳转**: https://themoviecosmos.com/movie/274855
- **命中视角/碎片**:
  - THE-CREATOR/su-persona-The-Creator-p1: fragments=[how-1, why-0, result-0] · sim=0.4896 · **命中分=3**
  - THE-MAGICIAN/su-persona-The-Magician-p3: fragments=[how-2, how-0, result-0] · sim=0.5177 · **命中分=3**
  - THE-OUTLAW/su-persona-The-Outlaw-p3: fragments=[who-0, how-1, how-2, result-0] · sim=0.5268 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p3: fragments=[how-2, how-0, how-1, result-0] · sim=0.4663 · **命中分=4**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 11 -->
### Stranded (2021) [THE-HERO, THE-INNOCENT, THE-MAGICIAN]
- **tmdb_id**: 841793
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 146.5478
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5478
- **genres** / **language**: Drama / pt
- **overview**: Tensions run high while food runs low as six influencers find themselves stranded on a secluded island after plans for a weekend escape go awry.
- **跳转**: https://themoviecosmos.com/movie/841793
- **命中视角/碎片**:
  - THE-HERO/su-persona-The-Hero-p2: fragments=[how-1, why-1, why-0] · sim=0.4272 · **命中分=3**
  - THE-INNOCENT/su-persona-The-Innocent-p3: fragments=[how-2, why-0, why-2, result-0] · sim=0.4785 · **命中分=4**
  - THE-MAGICIAN/su-persona-The-Magician-p2: fragments=[why-2, why-0, why-1, result-0] · sim=0.5478 · **命中分=4**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 9 -->
### The Last Winter (2006) [THE-CREATOR, THE-MAGICIAN]
- **tmdb_id**: 15667
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.4807
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4807
- **genres** / **language**: Horror, Thriller / en
- **overview**: In the Arctic region of Northern Alaska, an oil company's advance team struggles to establish a drilling base that will forever alter the pristine land. After one team member is found dead, a disorientation slowly claims the sanity of the others as each of them succumbs to a mysterious fear.
- **跳转**: https://themoviecosmos.com/movie/15667
- **命中视角/碎片**:
  - THE-CREATOR/su-persona-The-Creator-p3: fragments=[who-0, why-0, why-1, why-2, result-0] · sim=0.4807 · **命中分=5**
  - THE-MAGICIAN/su-persona-The-Magician-p2: fragments=[why-2, why-0, why-1, result-0] · sim=0.4562 · **命中分=4**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 9 -->
### Blade Runner: Black Out 2022 (2017) [THE-MAGICIAN, THE-OUTLAW]
- **tmdb_id**: 475946
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.5191
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5191
- **genres** / **language**: Action, Animation, Science Fiction / en
- **overview**: This animated short revolves around the events causing an electrical systems failure on the west coast of the US. According to Blade Runner 2049’s official timeline, this failure leads to cities shutting down, financial and trade markets being thrown into chaos, and food supplies dwindling. There’s no proof as to what caused the blackouts, but Replicants — the bio-engineered robots featured in the original Blade Runner, are blamed.
- **跳转**: https://themoviecosmos.com/movie/475946
- **命中视角/碎片**:
  - THE-MAGICIAN/su-persona-The-Magician-p1: fragments=[how-1, why-0, why-1, why-2, result-0] · sim=0.4855 · **命中分=5**
  - THE-OUTLAW/su-persona-The-Outlaw-p2: fragments=[why-0, how-0, why-1, how-1] · sim=0.5191 · **命中分=4**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 6 -->
### The Trigger Effect (1996) [THE-CAREGIVER, THE-HERO]
- **tmdb_id**: 58770
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 128.5294
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5294
- **genres** / **language**: Drama, Thriller / en
- **overview**: A blackout leaves those affected to consider what is necessary, what is legal, and what is questionable, in order to survive in a predatory environment.
- **跳转**: https://themoviecosmos.com/movie/58770
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p3: fragments=[why-0, why-2, how-1] · sim=0.5294 · **命中分=3**
  - THE-HERO/su-persona-The-Hero-p3: fragments=[why-0, how-1, result-0] · sim=0.4750 · **命中分=3**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 3 candidate(s)

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Matango (1963) [THE-RULER]
- **tmdb_id**: 52302
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.4964
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4964
- **genres** / **language**: Horror, Science Fiction, Thriller, Drama, Mystery, Fantasy / ja
- **overview**: Five vacationers and two crewmen become stranded on a tropical island near the equator. The island has little edible food for them to use as they try to live in a fungus covered hulk while repairing Kessei's yacht. Eventually they struggle over the food rations which were left behind by the former crew. Soon they discover something unfriendly there...
- **跳转**: https://themoviecosmos.com/movie/52302
- **命中视角/碎片**:
  - THE-RULER/su-persona-The-Ruler-p2: fragments=[result-0, why-0, why-1, how-1, how-2] · sim=0.4964 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Back to 1942 (2012) [THE-RULER]
- **tmdb_id**: 139329
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.4831
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4831
- **genres** / **language**: War, Drama / zh
- **overview**: In 1942, Henan Province was devastated by one of the most tragic famines in modern Chinese history, resulting in the deaths of at least three million men, women and children. Although the primary cause of the famine was a severe drought, it was exacerbated by locusts, windstorms, earthquakes, epidemic disease and the corruption of the ruling Kuomintang government.
- **跳转**: https://themoviecosmos.com/movie/139329
- **命中视角/碎片**:
  - THE-RULER/su-persona-The-Ruler-p2: fragments=[result-0, why-0, why-1, how-1, how-2] · sim=0.4831 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### From What Is Before (2014) [THE-CREATOR, THE-EXPLORER] [汇聚标注]
- **tmdb_id**: 280492
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=false, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 198.4517
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=1 / persona=1
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=1: THE-EXPLORER
- **相似度**: 0.4517
- **genres** / **language**: Drama / tl
- **overview**: The Philippines, 1972. Mysterious things are happening in a remote barrio. Wails are heard from the forest, cows are hacked to death, a man is found bleeding to death at the crossroad, and houses are burned. Ferdinand E. Marcos announces Proclamation No. 1081, putting the entire country under Martial Law.
- **跳转**: https://themoviecosmos.com/movie/280492
- **命中视角/碎片**:
  - THE-CREATOR/su-event-1: fragments=[how-1, how-2, why-0, why-1, result-0, why-2, how-0] · sim=0.4464
  - THE-EXPLORER/su-persona-The-Explorer-p2: fragments=[who-0, how-1, result-0, why-2, why-0] · sim=0.4517 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

## 02-corporate-layoff

# 现实波澜 · 02-corporate-layoff

## 元信息
- date: 2026-05-20
- news_url: https://www.sec.gov/Archives/edgar/data/896878/000089687826000024/fy26q3-ex9902.htm
- run_id: 02-corporate-layoff

## 现实波澜
- **title**: Intuit to cut roughly 17% of workforce in AI-focused restructuring
- **source** / **pub_time**: SEC filing / company memo / 2026-05-20T09:00:00-07:00
- **summary**: Chief executive Sasan Goodarzi told staff the tax-software company will eliminate about 3,000 full-time roles to co-locate teams in strategic hubs and accelerate AI-driven product work. Affected U.S. employees were offered 16 weeks of base pay plus two weeks per year of tenure, with offices in Reno and Woodland Hills winding down. The company framed the move as a painful but necessary reinvention after months of internal review.

### 多 agents 命中

**Count:** 10 candidate(s)

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 31 -->
### Bounty Killer (2013) [THE-CREATOR, THE-EXPLORER, THE-HERO, THE-INNOCENT, THE-JESTER, THE-MAGICIAN, THE-RULER, THE-EVERYMAN] [汇聚标注]
- **tmdb_id**: 209504
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=true, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 254.5699
  - **persona_agent_count**: 7
  - **source_hits**: surface=1 / event=0 / persona=8
  - **search_unit_kinds**: persona-semantic, surface-fragment-bundle
  - **center_dimensions**: how, result, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=7: THE-HERO,THE-MAGICIAN,THE-CREATOR,THE-EXPLORER,THE-INNOCENT,THE-RULER,THE-JESTER
- **相似度**: 0.5699
- **genres** / **language**: Action, Science Fiction / en
- **overview**: It’s been 20 years since the corporations took over the world’s governments. Their thirst for power and profits led to the Corporate Wars, a fierce global battle that laid waste to society as we know it. Born from the ash, the Council of Nine rose as a new law and order for this dark age. To avenge the corporations’ reckless destruction, the Council issues death warrants for all white collar criminals. Their hunters—the bounty killer. From amateur savage to graceful assassin, the bounty killers now compete for body count, fame and a fat stack of cash. They’re ending the plague of corporate greed and providing the survivors of the apocalypse with retribution. These are the new heroes. This is the age of the BOUNTY KILLER.
- **跳转**: https://themoviecosmos.com/movie/209504
- **命中视角/碎片**:
  - THE-CREATOR/su-persona-The-Creator-p1: fragments=[why-0, how-0, result-1, result-0] · sim=0.5625 · **命中分=4**
  - THE-EXPLORER/su-persona-The-Explorer-p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4808 · **命中分=4**
  - THE-EXPLORER/su-persona-The-Explorer-p2: fragments=[how-0, why-1, how-1, result-3] · sim=0.5352 · **命中分=4**
  - THE-HERO/su-persona-The-Hero-p2: fragments=[result-0, why-0, how-0, result-1] · sim=0.4748 · **命中分=4**
  - THE-INNOCENT/su-persona-The-Innocent-p1: fragments=[result-3, why-1, how-0, how-1] · sim=0.5699 · **命中分=4**
  - THE-JESTER/su-persona-The-Jester-p2: fragments=[how-0, why-0, result-1, how-1] · sim=0.5686 · **命中分=4**
  - THE-MAGICIAN/su-persona-The-Magician-p1: fragments=[why-0, how-0, result-0] · sim=0.5315 · **命中分=3**
  - THE-RULER/su-persona-The-Ruler-p1: fragments=[result-0, why-0, how-0, result-3] · sim=0.4793 · **命中分=4**
  - THE-EVERYMAN/su-surface-1: fragments=[who-0, who-1, who-2, where-0, where-1] · sim=0.4774
- **pseudo命中分合计**: 31
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 29 -->
### Cart (2014) [THE-CAREGIVER, THE-EVERYMAN, THE-HERO, THE-OUTLAW, THE-SAGE]
- **tmdb_id**: 287647
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 174.5189
  - **persona_agent_count**: 5
  - **source_hits**: surface=0 / event=0 / persona=7
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5189
- **genres** / **language**: Drama / ko
- **overview**: In response to a sudden dismissal of staff, workers at a big retail store begin a protest against their employer's oppressive labor policies.
- **跳转**: https://themoviecosmos.com/movie/287647
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p1: fragments=[result-0, how-0, result-1, result-3] · sim=0.5029 · **命中分=4**
  - THE-EVERYMAN/su-persona-The-Everyman-p3: fragments=[result-3, how-1, result-1] · sim=0.5163 · **命中分=3**
  - THE-HERO/su-persona-The-Hero-p1: fragments=[who-2, how-0, how-1, result-0, result-1] · sim=0.5155 · **命中分=5**
  - THE-HERO/su-persona-The-Hero-p2: fragments=[result-0, why-0, how-0, result-1] · sim=0.5189 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p1: fragments=[who-2, why-1, how-0, result-0, result-1] · sim=0.4591 · **命中分=5**
  - THE-OUTLAW/su-persona-The-Outlaw-p2: fragments=[result-0, why-0, how-1, how-2, result-1] · sim=0.4888 · **命中分=5**
  - THE-SAGE/su-persona-The-Sage-p2: fragments=[how-1, how-0, result-1] · sim=0.4839 · **命中分=3**
- **pseudo命中分合计**: 29
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 24 -->
### The Plan (2018) [THE-EVERYMAN, THE-LOVER, THE-OUTLAW, THE-SAGE]
- **tmdb_id**: 619090
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 164.5507
  - **persona_agent_count**: 4
  - **source_hits**: surface=0 / event=0 / persona=6
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5507
- **genres** / **language**: Comedy, Drama / es
- **overview**: Three friends who have been fired from the company where they worked and are demoralized because of their unemployment status. In these circumstances, they meet to undertake the plan that mentions the title but there is a problem: the car with which they would travel has broken down and the crane must wait.
- **跳转**: https://themoviecosmos.com/movie/619090
- **命中视角/碎片**:
  - THE-EVERYMAN/su-persona-The-Everyman-p1: fragments=[who-2, result-1, how-1, why-0] · sim=0.5507 · **命中分=4**
  - THE-EVERYMAN/su-persona-The-Everyman-p3: fragments=[result-3, how-1, result-1] · sim=0.4863 · **命中分=3**
  - THE-LOVER/su-persona-The-Lover-p1: fragments=[who-2, why-1, how-1, result-0] · sim=0.5214 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p1: fragments=[who-2, why-1, how-0, result-0, result-1] · sim=0.4709 · **命中分=5**
  - THE-OUTLAW/su-persona-The-Outlaw-p2: fragments=[result-0, why-0, how-1, how-2, result-1] · sim=0.4741 · **命中分=5**
  - THE-SAGE/su-persona-The-Sage-p2: fragments=[how-1, how-0, result-1] · sim=0.4443 · **命中分=3**
- **pseudo命中分合计**: 24
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 16 -->
### The Conference (2023) [THE-EVERYMAN, THE-HERO, THE-INNOCENT, THE-LOVER]
- **tmdb_id**: 1161048
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 148.5586
  - **persona_agent_count**: 4
  - **source_hits**: surface=0 / event=0 / persona=4
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5586
- **genres** / **language**: Horror, Comedy / sv
- **overview**: A ragtag group of public sector employees battle not only their own discord but also a bloodthirsty killer during a seemingly innocuous retreat.
- **跳转**: https://themoviecosmos.com/movie/1161048
- **命中视角/碎片**:
  - THE-EVERYMAN/su-persona-The-Everyman-p1: fragments=[who-2, result-1, how-1, why-0] · sim=0.5299 · **命中分=4**
  - THE-HERO/su-persona-The-Hero-p1: fragments=[who-2, how-0, how-1, result-0, result-1] · sim=0.5312 · **命中分=5**
  - THE-INNOCENT/su-persona-The-Innocent-p2: fragments=[who-2, result-0, why-0] · sim=0.5586 · **命中分=3**
  - THE-LOVER/su-persona-The-Lover-p1: fragments=[who-2, why-1, how-1, result-0] · sim=0.5311 · **命中分=4**
- **pseudo命中分合计**: 16
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 13 -->
### Mirreyes contra Godínez 2: El retiro (2022) [THE-EVERYMAN, THE-INNOCENT, THE-OUTLAW, THE-RULER]
- **tmdb_id**: 1002695
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 164.5509
  - **persona_agent_count**: 4
  - **source_hits**: surface=0 / event=0 / persona=4
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5509
- **genres** / **language**: Comedy / es
- **overview**: A divided team heads to a corporate retreat after receiving an enticing proposal. During their time away, they must overcome their differences and find a way to reunite.
- **跳转**: https://themoviecosmos.com/movie/1002695
- **命中视角/碎片**:
  - THE-EVERYMAN/su-persona-The-Everyman-p2: fragments=[result-0, why-0, why-1, how-0] · sim=0.5166 · **命中分=4**
  - THE-INNOCENT/su-persona-The-Innocent-p3: fragments=[how-2, why-1] · sim=0.4590 · **命中分=2**
  - THE-OUTLAW/su-persona-The-Outlaw-p3: fragments=[why-1, how-0, how-1, result-0] · sim=0.5509 · **命中分=4**
  - THE-RULER/su-persona-The-Ruler-p2: fragments=[how-1, why-1, how-2] · sim=0.4397 · **命中分=3**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 10 -->
### The Factory (2018) [THE-EVERYMAN, THE-EXPLORER, THE-SAGE]
- **tmdb_id**: 513349
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 146.5347
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5347
- **genres** / **language**: Thriller, Drama, Crime / ru
- **overview**: When a factory is bound to close, a group of workers decides to take action against the owner.
- **跳转**: https://themoviecosmos.com/movie/513349
- **命中视角/碎片**:
  - THE-EVERYMAN/su-persona-The-Everyman-p2: fragments=[result-0, why-0, why-1, how-0] · sim=0.5347 · **命中分=4**
  - THE-EXPLORER/su-persona-The-Explorer-p3: fragments=[how-2, why-1, result-2] · sim=0.4605 · **命中分=3**
  - THE-SAGE/su-persona-The-Sage-p3: fragments=[result-2, result-0, result-1] · sim=0.5002 · **命中分=3**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 9 -->
### Code 3 (2025) [THE-CAREGIVER, THE-HERO]
- **tmdb_id**: 1161617
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.5004
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5004
- **genres** / **language**: Comedy, Action, Drama / en
- **overview**: A burned-out paramedic tries to survive his last 24 hours on the job while training a new recruit.
- **跳转**: https://themoviecosmos.com/movie/1161617
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p3: fragments=[result-3, how-1, result-2, result-1] · sim=0.5004 · **命中分=4**
  - THE-HERO/su-persona-The-Hero-p3: fragments=[how-1, how-0, result-0, result-1, result-3] · sim=0.4738 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 6 -->
### The Seventh Company Outdoors (1977) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-JESTER] [汇聚标注]
- **tmdb_id**: 56589
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=true, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 276.5603
  - **persona_agent_count**: 2
  - **source_hits**: surface=2 / event=12 / persona=2
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic, surface-fragment-bundle
  - **center_dimensions**: how, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=2: THE-EXPLORER,THE-SAGE
- **相似度**: 0.5603
- **genres** / **language**: Comedy / fr
- **overview**: The third part of Seventh Company adventures.
- **跳转**: https://themoviecosmos.com/movie/56589
- **命中视角/碎片**:
  - THE-INNOCENT/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2, result-3] · sim=0.5351
  - THE-EVERYMAN/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2, result-3] · sim=0.5603
  - THE-HERO/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2, result-3] · sim=0.5335
  - THE-CAREGIVER/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2, result-3] · sim=0.5082
  - THE-EXPLORER/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2, result-3] · sim=0.5022
  - THE-OUTLAW/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2, result-3] · sim=0.5274
  - THE-LOVER/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2, result-3] · sim=0.5371
  - THE-CREATOR/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2, result-3] · sim=0.5465
  - THE-RULER/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2, result-3] · sim=0.5343
  - THE-MAGICIAN/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2, result-3] · sim=0.5254
  - THE-SAGE/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2, result-3] · sim=0.4986
  - THE-JESTER/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2, result-3] · sim=0.5046
  - THE-EXPLORER/su-persona-The-Explorer-p3: fragments=[how-2, why-1, result-2] · sim=0.4518 · **命中分=3**
  - THE-SAGE/su-persona-The-Sage-p1: fragments=[why-0, how-0, result-0] · sim=0.4710 · **命中分=3**
  - THE-EVERYMAN/su-surface-1: fragments=[who-0, who-1, who-2, where-0, where-1] · sim=0.4929
  - THE-RULER/su-surface-1: fragments=[who-0, who-1, who-2, where-0, where-1] · sim=0.4320
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 6 -->
### Camera Cafe: The Movie (2022) [THE-MAGICIAN, THE-SAGE]
- **tmdb_id**: 762823
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.4720
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4720
- **genres** / **language**: Comedy / es
- **overview**: Jesús Quesada, an incompetent executive, is appointed as the new director of a company in decline whose survival will now depend on both the ingenuity and ambition of his former colleagues.
- **跳转**: https://themoviecosmos.com/movie/762823
- **命中视角/碎片**:
  - THE-MAGICIAN/su-persona-The-Magician-p2: fragments=[how-0, result-0, why-1] · sim=0.4513 · **命中分=3**
  - THE-SAGE/su-persona-The-Sage-p1: fragments=[why-0, how-0, result-0] · sim=0.4720 · **命中分=3**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 5 -->
### Little Nothings (1992) [THE-MAGICIAN, THE-RULER]
- **tmdb_id**: 69896
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.5503
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5503
- **genres** / **language**: Comedy / fr
- **overview**: Lepetit, an ambitious and determined man, is named the new CEO of a department store. His mission is to improve the store's financial position. He decides that the human factor will be his catchword and introduces new methods, which he also applied to himself. But tensions slowly arise between members of the staff.
- **跳转**: https://themoviecosmos.com/movie/69896
- **命中视角/碎片**:
  - THE-MAGICIAN/su-persona-The-Magician-p1: fragments=[why-0, how-0, result-0] · sim=0.5503 · **命中分=3**
  - THE-RULER/su-persona-The-Ruler-p3: fragments=[how-0, why-0] · sim=0.4932 · **命中分=2**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 2 candidate(s)

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 9 -->
### Blood Is Dry (1960) [THE-CAREGIVER]
- **tmdb_id**: 88442
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 126.5870
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5870
- **genres** / **language**: Drama / ja
- **overview**: An employee in an assurance company threatens to commit suicide when management announces a massive layoff, the company uses this threat to its own advantage by turning the incident into an advertising campaign. With the success of the campaign, however, he is no longer a desperate man pointing a gun to his head, but a potential leader who wishes to take advantage of his failed suicide.
- **跳转**: https://themoviecosmos.com/movie/88442
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p1: fragments=[result-0, how-0, result-1, result-3] · sim=0.5473 · **命中分=4**
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[who-2, how-0, why-0, how-1, how-2] · sim=0.5870 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 5 -->
### The Second Tragic Fantozzi (1976) [THE-CAREGIVER]
- **tmdb_id**: 37769
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.5483
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5483
- **genres** / **language**: Comedy / it
- **overview**: The frustrating adventures of a humble employee who all the time has to fullfill the wishes and desires of his bosses.
- **跳转**: https://themoviecosmos.com/movie/37769
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[who-2, how-0, why-0, how-1, how-2] · sim=0.5483 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

## 03-election-upset

# 现实波澜 · 03-election-upset

## 元信息
- date: 2026-05-27
- news_url: https://www.aljazeera.com/news/2026/5/27/trump-backed-paxton-topples-senator-cornyn-in-texas-primary-run-off
- run_id: 03-election-upset

## 现实波澜
- **title**: Ken Paxton defeats John Cornyn in Texas Senate Republican runoff
- **source** / **pub_time**: Al Jazeera / 2026-05-27T03:00:00-05:00
- **summary**: Texas Attorney General Ken Paxton won about 64% of the vote to end Senator John Cornyn's bid for a fifth term, aided by a late endorsement from the sitting president. Cornyn became the first sitting Republican senator from Texas to lose renomination since 1970 despite substantially outraising and outspending his rival. Paxton will face Democratic state Representative James Talarico in November in a race that could reshape control of the U.S. Senate.

### 多 agents 命中

**Count:** 12 candidate(s)

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 25 -->
### Machete (2010) [THE-CAREGIVER, THE-EXPLORER, THE-HERO, THE-INNOCENT, THE-JESTER, THE-LOVER, THE-MAGICIAN]
- **tmdb_id**: 23631
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 186.5410
  - **persona_agent_count**: 7
  - **source_hits**: surface=0 / event=0 / persona=7
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5410
- **genres** / **language**: Action, Comedy, Thriller / en
- **overview**: After being set-up and betrayed by the man who hired him to assassinate a Texas Senator, an ex-Federale launches a brutal rampage of revenge against his former boss.
- **跳转**: https://themoviecosmos.com/movie/23631
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p1: fragments=[who-1, result-1, how-0, why-0] · sim=0.5071 · **命中分=4**
  - THE-EXPLORER/su-persona-The-Explorer-p2: fragments=[result-1, how-0, result-2] · sim=0.4903 · **命中分=3**
  - THE-HERO/su-persona-The-Hero-p3: fragments=[result-1, how-0, result-2] · sim=0.5000 · **命中分=3**
  - THE-INNOCENT/su-persona-The-Innocent-p1: fragments=[result-1, why-0, how-0, result-2] · sim=0.5356 · **命中分=4**
  - THE-JESTER/su-persona-The-Jester-p1: fragments=[result-1, why-1, how-0] · sim=0.5351 · **命中分=3**
  - THE-LOVER/su-persona-The-Lover-p2: fragments=[who-1, result-1, why-0, how-0] · sim=0.5410 · **命中分=4**
  - THE-MAGICIAN/su-persona-The-Magician-p3: fragments=[who-2, why-0, why-1, result-0] · sim=0.5241 · **命中分=4**
- **pseudo命中分合计**: 25
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 20 -->
### Swing Vote (2008) [THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-EXPLORER, THE-MAGICIAN, THE-SAGE, THE-INNOCENT, THE-JESTER] [汇聚标注]
- **tmdb_id**: 10187
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=true, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 324.6131
  - **persona_agent_count**: 6
  - **source_hits**: surface=11 / event=5 / persona=6
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic, surface-fragment-bundle
  - **center_dimensions**: how, who, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=6: THE-HERO,THE-MAGICIAN,THE-SAGE,THE-CREATOR,THE-EXPLORER,THE-EVERYMAN
- **相似度**: 0.6131
- **genres** / **language**: Comedy, Drama / en
- **overview**: In a remarkable turn of events, the result of the presidential election comes down to one man's vote.
- **跳转**: https://themoviecosmos.com/movie/10187
- **命中视角/碎片**:
  - THE-EVERYMAN/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5434
  - THE-HERO/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5250
  - THE-CAREGIVER/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.4842
  - THE-OUTLAW/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5235
  - THE-LOVER/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5021
  - THE-CREATOR/su-persona-The-Creator-p3: fragments=[why-0, result-0, result-2] · sim=0.5801 · **命中分=3**
  - THE-EVERYMAN/su-persona-The-Everyman-p2: fragments=[why-1, result-0, result-2] · sim=0.6131 · **命中分=3**
  - THE-EXPLORER/su-persona-The-Explorer-p3: fragments=[how-0, why-0, result-0, result-2] · sim=0.5372 · **命中分=4**
  - THE-HERO/su-persona-The-Hero-p2: fragments=[who-0, why-0, result-0, why-1] · sim=0.5728 · **命中分=4**
  - THE-MAGICIAN/su-persona-The-Magician-p3: fragments=[who-2, why-0, why-1, result-0] · sim=0.5184 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p3: fragments=[why-0, how-0] · sim=0.4666 · **命中分=2**
  - THE-INNOCENT/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5104
  - THE-EVERYMAN/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5487
  - THE-HERO/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5084
  - THE-CAREGIVER/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5605
  - THE-EXPLORER/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5411
  - THE-OUTLAW/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5181
  - THE-LOVER/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5081
  - THE-CREATOR/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5003
  - THE-MAGICIAN/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5211
  - THE-SAGE/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.4828
  - THE-JESTER/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5201
- **pseudo命中分合计**: 20
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 17 -->
### Long Live Freedom (2013) [THE-EVERYMAN, THE-MAGICIAN, THE-OUTLAW, THE-SAGE]
- **tmdb_id**: 167221
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 164.6310
  - **persona_agent_count**: 4
  - **source_hits**: surface=0 / event=0 / persona=5
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6310
- **genres** / **language**: Comedy, Drama / it
- **overview**: Elections are approaching and things don't look too good for the opposition. Their leader can't stand the pressure and disappears. To avoid a scandal, the upper echelons of the party concoct a risky plan: to replace him with his identical twin, a philosopher with BPD, whose eclectic ideas and direct approach unexpectedly make the party surge in the polls.
- **跳转**: https://themoviecosmos.com/movie/167221
- **命中视角/碎片**:
  - THE-EVERYMAN/su-persona-The-Everyman-p2: fragments=[why-1, result-0, result-2] · sim=0.6310 · **命中分=3**
  - THE-EVERYMAN/su-persona-The-Everyman-p3: fragments=[result-1, result-2] · sim=0.5464 · **命中分=2**
  - THE-MAGICIAN/su-persona-The-Magician-p1: fragments=[why-0, how-0, result-0, result-2] · sim=0.5870 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p1: fragments=[who-0, why-0, how-0, result-0, result-1] · sim=0.5490 · **命中分=5**
  - THE-SAGE/su-persona-The-Sage-p2: fragments=[result-1, why-1, result-2] · sim=0.5998 · **命中分=3**
- **pseudo命中分合计**: 17
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 14 -->
### The Independent (2022) [THE-CREATOR, THE-JESTER, THE-SAGE]
- **tmdb_id**: 878183
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 154.6578
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=0 / persona=5
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6578
- **genres** / **language**: Thriller, Mystery, Crime / en
- **overview**: It's the final weeks of the most consequential presidential election in history. America is poised to elect either its first female president or its first viable independent candidate. Reporting history as it's made, an idealistic young journalist teams up with her idol, legendary journalist Nick Booker, to uncover a conspiracy that places the fate of the election, and the country, in their hands.
- **跳转**: https://themoviecosmos.com/movie/878183
- **命中视角/碎片**:
  - THE-CREATOR/su-persona-The-Creator-p1: fragments=[how-0, why-0, why-1] · sim=0.5074 · **命中分=3**
  - THE-CREATOR/su-persona-The-Creator-p2: fragments=[result-1, result-2, how-0] · sim=0.6340 · **命中分=3**
  - THE-CREATOR/su-persona-The-Creator-p3: fragments=[why-0, result-0, result-2] · sim=0.6578 · **命中分=3**
  - THE-JESTER/su-persona-The-Jester-p3: fragments=[result-0, result-2] · sim=0.5419 · **命中分=2**
  - THE-SAGE/su-persona-The-Sage-p1: fragments=[result-0, how-0, result-1] · sim=0.4916 · **命中分=3**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 13 -->
### Lone Star (1952) [THE-INNOCENT, THE-CAREGIVER, THE-EXPLORER, THE-LOVER, THE-MAGICIAN, THE-EVERYMAN, THE-HERO, THE-SAGE] [汇聚标注]
- **tmdb_id**: 37593
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=false, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 244.5760
  - **persona_agent_count**: 4
  - **source_hits**: surface=0 / event=5 / persona=4
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic
  - **center_dimensions**: how, result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=4: THE-EVERYMAN,THE-HERO,THE-LOVER,THE-SAGE
- **相似度**: 0.5760
- **genres** / **language**: Western / en
- **overview**: Cattle baron Devereaux Burke is enlisted by an aging Andrew Jackson to dissuade Sam Houston from establishing Texas as a republic. Burke must fight state senator Thomas Craden, in the process winning the heart of Craden's newspaper-editor girlfriend Martha Ronda.
- **跳转**: https://themoviecosmos.com/movie/37593
- **命中视角/碎片**:
  - THE-INNOCENT/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5409
  - THE-CAREGIVER/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5064
  - THE-EXPLORER/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5394
  - THE-LOVER/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5329
  - THE-MAGICIAN/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5141
  - THE-EVERYMAN/su-persona-The-Everyman-p1: fragments=[how-0, result-0, result-1] · sim=0.5373 · **命中分=3**
  - THE-HERO/su-persona-The-Hero-p3: fragments=[result-1, how-0, result-2] · sim=0.4805 · **命中分=3**
  - THE-LOVER/su-persona-The-Lover-p1: fragments=[who-0, how-0, why-1, result-0] · sim=0.5760 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p1: fragments=[result-0, how-0, result-1] · sim=0.5051 · **命中分=3**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 13 -->
### Gli onorevoli (1963) [THE-CREATOR, THE-EXPLORER, THE-HERO, THE-SAGE]
- **tmdb_id**: 64946
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 164.6357
  - **persona_agent_count**: 4
  - **source_hits**: surface=0 / event=0 / persona=4
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6357
- **genres** / **language**: Comedy / it
- **overview**: Some political candidates are determined to win the electors' preference during an election campaign in Italy.
- **跳转**: https://themoviecosmos.com/movie/64946
- **命中视角/碎片**:
  - THE-CREATOR/su-persona-The-Creator-p1: fragments=[how-0, why-0, why-1] · sim=0.5746 · **命中分=3**
  - THE-EXPLORER/su-persona-The-Explorer-p3: fragments=[how-0, why-0, result-0, result-2] · sim=0.6357 · **命中分=4**
  - THE-HERO/su-persona-The-Hero-p1: fragments=[result-0, how-0, why-1, result-2] · sim=0.5684 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p3: fragments=[why-0, how-0] · sim=0.5006 · **命中分=2**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 11 -->
### Judge Archer (2016) [THE-CAREGIVER, THE-HERO, THE-OUTLAW]
- **tmdb_id**: 264518
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 154.5606
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5606
- **genres** / **language**: Action, Drama / zh
- **overview**: The spear signifies political power, the arrow personal ambition. What happens when the two collide?
- **跳转**: https://themoviecosmos.com/movie/264518
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[result-2, result-0, why-1] · sim=0.5606 · **命中分=3**
  - THE-HERO/su-persona-The-Hero-p2: fragments=[who-0, why-0, result-0, why-1] · sim=0.5439 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p3: fragments=[how-0, why-0, why-1, result-0] · sim=0.5293 · **命中分=4**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 9 -->
### Game Change (2012) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-EXPLORER, THE-OUTLAW, THE-CREATOR, THE-SAGE, THE-JESTER, THE-CAREGIVER, THE-LOVER, THE-MAGICIAN] [汇聚标注]
- **tmdb_id**: 91010
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=true, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 294.5721
  - **persona_agent_count**: 3
  - **source_hits**: surface=11 / event=8 / persona=3
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic, surface-fragment-bundle
  - **center_dimensions**: how, result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=3: THE-EXPLORER,THE-EVERYMAN,THE-OUTLAW
- **相似度**: 0.5721
- **genres** / **language**: TV Movie, Drama, Comedy, History / en
- **overview**: During the Republican run of the 2008 Presidential election, candidate John McCain picks a relative unknown, Alaskan governor Sarah Palin, to be his running mate.  As the campaign kicks into high gear, her lack of experience, in both political and media savvy, becomes a drain upon McCain and his strategists.
- **跳转**: https://themoviecosmos.com/movie/91010
- **命中视角/碎片**:
  - THE-INNOCENT/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5253
  - THE-EVERYMAN/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5323
  - THE-HERO/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5084
  - THE-EXPLORER/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5242
  - THE-OUTLAW/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5307
  - THE-CREATOR/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5362
  - THE-SAGE/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5398
  - THE-JESTER/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5402
  - THE-EVERYMAN/su-persona-The-Everyman-p1: fragments=[how-0, result-0, result-1] · sim=0.4773 · **命中分=3**
  - THE-EXPLORER/su-persona-The-Explorer-p2: fragments=[result-1, how-0, result-2] · sim=0.4910 · **命中分=3**
  - THE-OUTLAW/su-persona-The-Outlaw-p2: fragments=[who-1, how-0, result-1] · sim=0.4977 · **命中分=3**
  - THE-INNOCENT/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5343
  - THE-EVERYMAN/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5561
  - THE-HERO/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5530
  - THE-CAREGIVER/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5462
  - THE-EXPLORER/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5721
  - THE-OUTLAW/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5706
  - THE-LOVER/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5065
  - THE-CREATOR/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5430
  - THE-MAGICIAN/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5322
  - THE-SAGE/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5115
  - THE-JESTER/su-surface-1: fragments=[who-0, who-1, who-2, where-0] · sim=0.5546
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 8 -->
### The Distinguished Gentleman (1992) [THE-CAREGIVER, THE-INNOCENT]
- **tmdb_id**: 10411
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.5001
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5001
- **genres** / **language**: Comedy / en
- **overview**: A Florida con man uses the recent death of the long time Congressman from his district, who he just happens to share a last name with, to get elected to his version of paradise, the U.S. Congress, where the money flows from lobbyists.
- **跳转**: https://themoviecosmos.com/movie/10411
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p1: fragments=[who-1, result-1, how-0, why-0] · sim=0.5001 · **命中分=4**
  - THE-INNOCENT/su-persona-The-Innocent-p1: fragments=[result-1, why-0, how-0, result-2] · sim=0.4879 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 7 -->
### Avenging Force (1986) [THE-MAGICIAN, THE-OUTLAW]
- **tmdb_id**: 52657
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 128.5930
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5930
- **genres** / **language**: Action, Drama, Thriller / en
- **overview**: A senator is targeted by the Pentangle, a right wing paramilitary group. His pal, a former CIA agent and martial artist, tries to help him. The group kidnaps the agent's sister and tries to hunt him down, "The Most Dangerous Game" style.
- **跳转**: https://themoviecosmos.com/movie/52657
- **命中视角/碎片**:
  - THE-MAGICIAN/su-persona-The-Magician-p2: fragments=[who-1, why-1, how-0, result-1] · sim=0.5930 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p2: fragments=[who-1, how-0, result-1] · sim=0.5011 · **命中分=3**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 7 -->
### The Campaign (2012) [THE-CREATOR, THE-MAGICIAN, THE-SAGE, THE-JESTER, THE-HERO] [汇聚标注]
- **tmdb_id**: 77953
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=false, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 208.5956
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=4 / persona=2
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic
  - **center_dimensions**: result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=2: THE-SAGE,THE-HERO
- **相似度**: 0.5956
- **genres** / **language**: Comedy / en
- **overview**: Two rival politicians compete to win an election to represent their small North Carolina congressional district in the United States House of Representatives.
- **跳转**: https://themoviecosmos.com/movie/77953
- **命中视角/碎片**:
  - THE-CREATOR/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5419
  - THE-MAGICIAN/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5092
  - THE-SAGE/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5292
  - THE-JESTER/su-event-1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5421
  - THE-HERO/su-persona-The-Hero-p1: fragments=[result-0, how-0, why-1, result-2] · sim=0.5918 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p2: fragments=[result-1, why-1, result-2] · sim=0.5956 · **命中分=3**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 7 -->
### Chappaquiddick (2018) [THE-JESTER, THE-LOVER]
- **tmdb_id**: 432301
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.5354
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5354
- **genres** / **language**: History, Drama, Thriller / en
- **overview**: Ted Kennedy's life and political career become derailed in the aftermath of a fatal car accident in 1969 that claims the life of a young campaign strategist, Mary Jo Kopechne.
- **跳转**: https://themoviecosmos.com/movie/432301
- **命中视角/碎片**:
  - THE-JESTER/su-persona-The-Jester-p1: fragments=[result-1, why-1, how-0] · sim=0.5354 · **命中分=3**
  - THE-LOVER/su-persona-The-Lover-p2: fragments=[who-1, result-1, why-0, how-0] · sim=0.5312 · **命中分=4**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 1 candidate(s)

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 5 -->
### Days of '36 (1972) [THE-OUTLAW]
- **tmdb_id**: 114645
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.5567
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5567
- **genres** / **language**: Drama, History / el
- **overview**: The assassin of a prominent trade unionist takes a conservative MP hostage, throwing the government into a state of disarray.
- **跳转**: https://themoviecosmos.com/movie/114645
- **命中视角/碎片**:
  - THE-OUTLAW/su-persona-The-Outlaw-p1: fragments=[who-0, why-0, how-0, result-0, result-1] · sim=0.5567 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

## 04-celebrity-scandal

# 现实波澜 · 04-celebrity-scandal

## 元信息
- date: 2026-05-27
- news_url: https://www.bbc.co.uk/news/articles/c759y6pvezgo
- run_id: 04-celebrity-scandal

## 现实波澜
- **title**: YouTuber arrested over alleged AI-fabricated claims against Kim Soo-hyun
- **source** / **pub_time**: BBC News / 2026-05-27T09:00:00+09:00
- **summary**: Seoul police secured an arrest warrant for the operator of a channel with nearly one million subscribers who allegedly used AI-generated audio and manipulated chat screenshots to claim the actor dated a late co-star while she was a minor. Prosecutors say the influencer knew the relationship began only when she was an adult but spread false claims for financial gain. The scandal had halted the star's endorsements and public appearances since early 2025.

### 多 agents 命中

**Count:** 9 candidate(s)

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 25 -->
### Scandal (1950) [THE-CREATOR, THE-EVERYMAN, THE-INNOCENT, THE-LOVER, THE-MAGICIAN, THE-OUTLAW]
- **tmdb_id**: 32690
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 184.6635
  - **persona_agent_count**: 6
  - **source_hits**: surface=0 / event=0 / persona=6
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6635
- **genres** / **language**: Drama / ja
- **overview**: A celebrity photograph sparks a court case as a tabloid magazine spins a scandalous yarn over a painter and a famous singer.
- **跳转**: https://themoviecosmos.com/movie/32690
- **命中视角/碎片**:
  - THE-CREATOR/su-persona-The-Creator-p2: fragments=[result-1, how-1, result-0, why-0] · sim=0.5732 · **命中分=4**
  - THE-EVERYMAN/su-persona-The-Everyman-p3: fragments=[how-0, how-1, result-0] · sim=0.5937 · **命中分=3**
  - THE-INNOCENT/su-persona-The-Innocent-p1: fragments=[result-1, why-0, how-1, result-0] · sim=0.5841 · **命中分=4**
  - THE-LOVER/su-persona-The-Lover-p3: fragments=[result-1, why-0, how-0, how-1, result-0] · sim=0.6635 · **命中分=5**
  - THE-MAGICIAN/su-persona-The-Magician-p2: fragments=[why-0, result-1, result-0, how-0] · sim=0.5827 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p3: fragments=[how-1, how-0, why-0, result-0, result-1] · sim=0.5761 · **命中分=5**
- **pseudo命中分合计**: 25
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 18 -->
### Prophecy (2015) [THE-CAREGIVER, THE-OUTLAW, THE-LOVER, THE-RULER, THE-SAGE, THE-JESTER, THE-HERO, THE-INNOCENT] [汇聚标注]
- **tmdb_id**: 347483
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=false, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 244.5777
  - **persona_agent_count**: 4
  - **source_hits**: surface=0 / event=6 / persona=5
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic
  - **center_dimensions**: how, result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=4: THE-HERO,THE-CAREGIVER,THE-INNOCENT,THE-SAGE
- **相似度**: 0.5777
- **genres** / **language**: Mystery, Thriller / ja
- **overview**: The cyber crime investigation division at the Tokyo Metropolitan Police Department finds a video on website "YOURTUBE." In the video, a man covered by a newspaper, warns that a fire will be set at a food processing company. More crime notices are soon found involving violent crimes.  Geitsu is the main guy behind the group "Shinbunshi," which has posted the videos. He used to work as a temporary employee at an IT company, but was unfairly dismissed. He then begins doing manual labor work and meets the other members of "Shinbushi."
- **跳转**: https://themoviecosmos.com/movie/347483
- **命中视角/碎片**:
  - THE-CAREGIVER/su-event-1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5059
  - THE-OUTLAW/su-event-1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5046
  - THE-LOVER/su-event-1: fragments=[why-0, how-0, result-1, how-1, result-0] · sim=0.5000
  - THE-RULER/su-event-1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5047
  - THE-SAGE/su-event-1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5124
  - THE-JESTER/su-event-1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5152
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[who-0, how-0, how-1, result-0] · sim=0.5269 · **命中分=4**
  - THE-CAREGIVER/su-persona-The-Caregiver-p3: fragments=[how-1, how-0, result-0] · sim=0.5772 · **命中分=3**
  - THE-HERO/su-persona-The-Hero-p2: fragments=[result-0, why-0, how-0, how-1] · sim=0.5534 · **命中分=4**
  - THE-INNOCENT/su-persona-The-Innocent-p3: fragments=[result-0, why-0, how-0, how-1] · sim=0.4757 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p1: fragments=[how-0, how-1, result-0] · sim=0.5777 · **命中分=3**
- **pseudo命中分合计**: 18
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 13 -->
### I Like Mountain Music (1933) [THE-INNOCENT, THE-JESTER, THE-OUTLAW]
- **tmdb_id**: 151913
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 146.6037
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6037
- **genres** / **language**: Animation, Comedy, Family, Music / en
- **overview**: After hours, individuals on various magazine covers in a drugstore come to life and sing, speak, or perform. Caricature celebrity depictions include George Arliss, Eddie Cantor, Sonja Henie, Benito Mussolini, Ignacy Paderewski, Edward G. Robinson, Will Rogers, and Ed Wynn. A robbery sequence features bad guys breaking into the cash register and Sherlock Holmes and Dr. Watson on the case. King Kong also makes an appearance. A Merrie Melody cartoon.
- **跳转**: https://themoviecosmos.com/movie/151913
- **命中视角/碎片**:
  - THE-INNOCENT/su-persona-The-Innocent-p1: fragments=[result-1, why-0, how-1, result-0] · sim=0.5609 · **命中分=4**
  - THE-JESTER/su-persona-The-Jester-p1: fragments=[result-0, why-0, how-0, how-1, result-1] · sim=0.6037 · **命中分=5**
  - THE-OUTLAW/su-persona-The-Outlaw-p1: fragments=[who-0, how-0, how-1, result-0] · sim=0.5320 · **命中分=4**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 12 -->
### The Green Hornet (1940) [THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-LOVER, THE-CREATOR, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-JESTER] [汇聚标注]
- **tmdb_id**: 250332
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=true, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 206.5575
  - **persona_agent_count**: 3
  - **source_hits**: surface=12 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic, surface-fragment-bundle
  - **center_dimensions**: how, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=3: THE-EXPLORER,THE-CAREGIVER,THE-OUTLAW
- **相似度**: 0.5575
- **genres** / **language**: Adventure, Crime, Science Fiction / en
- **overview**: A newspaper publisher and his Korean servant fight crime as vigilantes who pose as a notorious masked gangster and his aide.
- **跳转**: https://themoviecosmos.com/movie/250332
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[who-0, how-0, how-1, result-0] · sim=0.5402 · **命中分=4**
  - THE-EXPLORER/su-persona-The-Explorer-p1: fragments=[how-0, why-0, how-1, result-0] · sim=0.5575 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p1: fragments=[who-0, how-0, how-1, result-0] · sim=0.5252 · **命中分=4**
  - THE-INNOCENT/su-surface-1: fragments=[who-0, who-1, who-2, where-0, who-3] · sim=0.4682
  - THE-EVERYMAN/su-surface-1: fragments=[who-0, who-1, where-0, who-2, who-3] · sim=0.5018
  - THE-HERO/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.4453
  - THE-CAREGIVER/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.4651
  - THE-EXPLORER/su-surface-1: fragments=[who-0, where-0, who-1, who-2, who-3] · sim=0.4689
  - THE-OUTLAW/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.4653
  - THE-LOVER/su-surface-1: fragments=[who-0, who-1, where-0, who-2, who-3] · sim=0.4676
  - THE-CREATOR/su-surface-1: fragments=[who-0, where-0, who-1, who-2, who-3] · sim=0.4672
  - THE-RULER/su-surface-1: fragments=[who-0, who-2, who-3, where-0, who-1] · sim=0.4629
  - THE-MAGICIAN/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.4602
  - THE-SAGE/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.4653
  - THE-JESTER/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.4688
- **pseudo命中分合计**: 12
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 11 -->
### Master (2016) [THE-INNOCENT, THE-HERO, THE-CAREGIVER, THE-OUTLAW, THE-RULER, THE-MAGICIAN, THE-JESTER, THE-CREATOR, THE-EXPLORER, THE-SAGE] [汇聚标注]
- **tmdb_id**: 382220
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=false, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 226.5767
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=7 / persona=3
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic
  - **center_dimensions**: how, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=3: THE-EXPLORER,THE-CREATOR,THE-SAGE
- **相似度**: 0.5767
- **genres** / **language**: Crime, Action / ko
- **overview**: Korea’s biggest network marketing scam reveals a far greater network of corruption and conspiracy lurking underneath.
- **跳转**: https://themoviecosmos.com/movie/382220
- **命中视角/碎片**:
  - THE-INNOCENT/su-event-1: fragments=[why-0, how-0, result-0, result-1, how-1] · sim=0.5063
  - THE-HERO/su-event-1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.4934
  - THE-CAREGIVER/su-event-1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5067
  - THE-OUTLAW/su-event-1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5006
  - THE-RULER/su-event-1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5200
  - THE-MAGICIAN/su-event-1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.4977
  - THE-JESTER/su-event-1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5142
  - THE-CREATOR/su-persona-The-Creator-p3: fragments=[who-0, why-0, how-0, result-0] · sim=0.5767 · **命中分=4**
  - THE-EXPLORER/su-persona-The-Explorer-p1: fragments=[how-0, why-0, how-1, result-0] · sim=0.5757 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p1: fragments=[how-0, how-1, result-0] · sim=0.5456 · **命中分=3**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 9 -->
### Panama (2015) [THE-INNOCENT, THE-LOVER]
- **tmdb_id**: 336200
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.6032
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6032
- **genres** / **language**: Thriller, Drama / sr
- **overview**: A thriller that depicts how digital communication, pornography and vanity obstruct true emotions and love.
- **跳转**: https://themoviecosmos.com/movie/336200
- **命中视角/碎片**:
  - THE-INNOCENT/su-persona-The-Innocent-p2: fragments=[who-1, why-0, how-0, result-1] · sim=0.5597 · **命中分=4**
  - THE-LOVER/su-persona-The-Lover-p3: fragments=[result-1, why-0, how-0, how-1, result-0] · sim=0.6032 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 9 -->
### U Turn (2016) [THE-EVERYMAN, THE-JESTER]
- **tmdb_id**: 397490
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.5633
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5633
- **genres** / **language**: Mystery, Thriller, Crime, Horror / kn
- **overview**: A journalist who intents to write an article on traffic rule breakers gets dragged into a whirlpool of murder cases and deception.
- **跳转**: https://themoviecosmos.com/movie/397490
- **命中视角/碎片**:
  - THE-EVERYMAN/su-persona-The-Everyman-p1: fragments=[result-1, why-0, how-0, result-0] · sim=0.5509 · **命中分=4**
  - THE-JESTER/su-persona-The-Jester-p2: fragments=[who-0, how-0, why-0, how-1, result-0] · sim=0.5633 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 9 -->
### Diamantino (2018) [THE-LOVER, THE-MAGICIAN]
- **tmdb_id**: 518495
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.5964
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5964
- **genres** / **language**: Comedy, Science Fiction, Fantasy / pt
- **overview**: A disgraced soccer star seeks redemption but is exploited by a variety of causes hoping to capitalize on his celebrity.
- **跳转**: https://themoviecosmos.com/movie/518495
- **命中视角/碎片**:
  - THE-LOVER/su-persona-The-Lover-p2: fragments=[who-1, why-0, how-0, how-1, result-1] · sim=0.5964 · **命中分=5**
  - THE-MAGICIAN/su-persona-The-Magician-p2: fragments=[why-0, result-1, result-0, how-0] · sim=0.5766 · **命中分=4**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 7 -->
### One Way (2006) [THE-LOVER, THE-SAGE]
- **tmdb_id**: 7298
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.6283
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6283
- **genres** / **language**: Crime, Mystery, Thriller / en
- **overview**: To cover up his infidelities and protect his upcoming marriage, a star advertiser helps free an accused rapist by giving a false alibi and suffers the brutal revenge of the victim.
- **跳转**: https://themoviecosmos.com/movie/7298
- **命中视角/碎片**:
  - THE-LOVER/su-persona-The-Lover-p2: fragments=[who-1, why-0, how-0, how-1, result-1] · sim=0.5953 · **命中分=5**
  - THE-SAGE/su-persona-The-Sage-p2: fragments=[why-0, result-1] · sim=0.6283 · **命中分=2**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 1 candidate(s)

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 7 -->
### Peligro en tu mirada (2021) [THE-EVERYMAN, THE-EXPLORER, THE-LOVER, THE-CREATOR] [汇聚标注]
- **tmdb_id**: 841297
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=false, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 206.6109
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=4 / persona=2
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic
  - **center_dimensions**: how, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=1: THE-EVERYMAN
- **相似度**: 0.6109
- **genres** / **language**: Drama, Thriller / es
- **overview**: A female photographer is coerced into spying on the affaire of a political candidate, becoming the sole witness of a crime of which he is falsely accused
- **跳转**: https://themoviecosmos.com/movie/841297
- **命中视角/碎片**:
  - THE-EVERYMAN/su-event-1: fragments=[why-0, how-0, result-0, result-1, how-1] · sim=0.5057
  - THE-EXPLORER/su-event-1: fragments=[how-0, how-1, result-0, why-0, result-1] · sim=0.5095
  - THE-LOVER/su-event-1: fragments=[why-0, how-0, result-1, how-1, result-0] · sim=0.4949
  - THE-CREATOR/su-event-1: fragments=[why-0, how-0, result-0, result-1, how-1] · sim=0.5038
  - THE-EVERYMAN/su-persona-The-Everyman-p2: fragments=[who-0, how-0, why-0, how-1] · sim=0.6109 · **命中分=4**
  - THE-EVERYMAN/su-persona-The-Everyman-p3: fragments=[how-0, how-1, result-0] · sim=0.5423 · **命中分=3**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

## 05-climate-disaster

# 现实波澜 · 05-climate-disaster

## 元信息
- date: 2026-05-29
- news_url: https://www.thenationalnews.com/news/mena/2026/05/29/al-shara-visits-syrias-flood-zones-after-week-of-mayhem-on-the-euphrates/
- run_id: 05-climate-disaster

## 现实波澜
- **title**: Syria's president visits Euphrates flood zones after week of deadly high water
- **source** / **pub_time**: The National / 2026-05-29T12:00:00+04:00
- **summary**: Surging flows on the Euphrates flooded homes, farms, and schools in Deir Ezzor and Raqqa after one of the heaviest rainy seasons in three decades, with several children drowning despite official warnings. An earthen bridge collapsed, the navy deployed boats for evacuations, and Turkey agreed to reduce upstream releases. Reservoirs filled beyond 97% capacity before dam operations and seasonal rains pushed the river past protective embankments.

### 多 agents 命中

**Count:** 7 candidate(s)

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 17 -->
### Bloat (2025) [THE-CAREGIVER, THE-INNOCENT, THE-LOVER]
- **tmdb_id**: 937393
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 146.6060
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=0 / persona=4
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6060
- **genres** / **language**: Horror / en
- **overview**: After a near-death drowning accident, a young boy's family is horrified to discover he has become possessed by a legendary demon from the depths of the lake. As the family races against time to save the boy's soul, the evil monster inside the child tears the family apart as it seeks to destroy everyone in its path.
- **跳转**: https://themoviecosmos.com/movie/937393
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p1: fragments=[who-1, result-0, why-0, how-0, result-1] · sim=0.5393 · **命中分=5**
  - THE-INNOCENT/su-persona-The-Innocent-p1: fragments=[result-0, why-0, how-1] · sim=0.5538 · **命中分=3**
  - THE-LOVER/su-persona-The-Lover-p1: fragments=[result-0, why-0, how-1, how-2] · sim=0.5901 · **命中分=4**
  - THE-LOVER/su-persona-The-Lover-p2: fragments=[who-1, why-0, how-2, result-0, result-1] · sim=0.6060 · **命中分=5**
- **pseudo命中分合计**: 17
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 15 -->
### Poem of the Sea (1958) [THE-MAGICIAN, THE-EXPLORER, THE-OUTLAW] [汇聚标注]
- **tmdb_id**: 257637
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=false, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 226.5635
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=1 / persona=4
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic
  - **center_dimensions**: how, result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=3: THE-EXPLORER,THE-MAGICIAN,THE-OUTLAW
- **相似度**: 0.5635
- **genres** / **language**: Drama / ru
- **overview**: A Soviet dam project means that many old Ukrainian villages will end up under water. There are conflicts between the dam engineers and villagers who don't want to move.
- **跳转**: https://themoviecosmos.com/movie/257637
- **命中视角/碎片**:
  - THE-MAGICIAN/su-event-1: fragments=[why-0, how-0, how-1, how-5, result-0, result-4, result-5, how-2, how-3, how-4, result-1, result-2, result-3] · sim=0.4328
  - THE-EXPLORER/su-persona-The-Explorer-p1: fragments=[how-0, why-0, how-1] · sim=0.5467 · **命中分=3**
  - THE-MAGICIAN/su-persona-The-Magician-p1: fragments=[how-5, why-0, how-0, how-1] · sim=0.5635 · **命中分=4**
  - THE-MAGICIAN/su-persona-The-Magician-p3: fragments=[how-0, why-0, how-1, result-0] · sim=0.5348 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p1: fragments=[result-0, why-0, how-0, how-1] · sim=0.5311 · **命中分=4**
- **pseudo命中分合计**: 15
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 12 -->
### Flood (2007) [THE-LOVER, THE-CAREGIVER, THE-CREATOR, THE-MAGICIAN] [汇聚标注]
- **tmdb_id**: 6309
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=false, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 226.5504
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=1 / persona=3
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic
  - **center_dimensions**: how, result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=3: THE-CREATOR,THE-CAREGIVER,THE-MAGICIAN
- **相似度**: 0.5504
- **genres** / **language**: Drama, Action, Thriller / en
- **overview**: Timely yet terrifying, The Flood predicts the unthinkable. When a raging storm coincides with high seas it unleashes a colossal tidal surge, which travels mercilessly down England's East Coast and into the Thames Estuary. Overwhelming the Barrier, torrents of water pour into the city. The lives of millions of Londoners are at stake.
- **跳转**: https://themoviecosmos.com/movie/6309
- **命中视角/碎片**:
  - THE-LOVER/su-event-1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, how-5, result-0, result-1, result-2, result-3, result-4, result-5] · sim=0.4585
  - THE-CAREGIVER/su-persona-The-Caregiver-p3: fragments=[how-2, why-0, how-1, how-3] · sim=0.5289 · **命中分=4**
  - THE-CREATOR/su-persona-The-Creator-p2: fragments=[result-0, why-0, how-1, result-2] · sim=0.5504 · **命中分=4**
  - THE-MAGICIAN/su-persona-The-Magician-p3: fragments=[how-0, why-0, how-1, result-0] · sim=0.5413 · **命中分=4**
- **pseudo命中分合计**: 12
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 9 -->
### Disaster Wars: Earthquake vs. Tsunami (2013) [THE-HERO, THE-RULER]
- **tmdb_id**: 289214
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.6032
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6032
- **genres** / **language**: Thriller, Action, Drama, Science Fiction / en
- **overview**: Deep underwater in the Marianas Trench an accident results in a devastating Tsunami that destroys the Hawaiian Islands as it continues toward the west coast. Panic ensues all up and down the western coast of North and South America. In an attempt to lessen its impact, scientists launch an underwater explosion that inadvertently makes the tsunami more powerful and focused on Los Angeles. Scientists rush to a solution while the military begins planning for the worst. Los Angeles begins emergency evacuation. Lives and loves are lost even as a brash young grad student comes up with a solution: start the mother of all earthquakes to counter the rushing torrent and raise the continental shelf off the coast of the United States.
- **跳转**: https://themoviecosmos.com/movie/289214
- **命中视角/碎片**:
  - THE-HERO/su-persona-The-Hero-p1: fragments=[result-0, why-0, how-2, result-5] · sim=0.5717 · **命中分=4**
  - THE-RULER/su-persona-The-Ruler-p2: fragments=[how-4, how-2, how-3, result-0, result-2] · sim=0.6032 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 8 -->
### The Sweet Hereafter (1997) [THE-EXPLORER, THE-LOVER]
- **tmdb_id**: 10217
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.6030
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6030
- **genres** / **language**: Drama / en
- **overview**: A small mountain community in Canada is devastated when a school bus accident leaves more than a dozen of its children dead. A big-city lawyer arrives to help the survivors' and victims' families prepare a class-action suit, but his efforts only seem to push the townspeople further apart. At the same time, one teenage survivor of the accident has to reckon with the loss of innocence brought about by a different kind of damage.
- **跳转**: https://themoviecosmos.com/movie/10217
- **命中视角/碎片**:
  - THE-EXPLORER/su-persona-The-Explorer-p3: fragments=[result-0, how-5, result-4] · sim=0.5607 · **命中分=3**
  - THE-LOVER/su-persona-The-Lover-p2: fragments=[who-1, why-0, how-2, result-0, result-1] · sim=0.6030 · **命中分=5**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 8 -->
### The Storm (2009) [THE-CAREGIVER, THE-EXPLORER]
- **tmdb_id**: 29602
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.5821
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5821
- **genres** / **language**: Drama / nl
- **overview**: A fictional story within the historical context of the disastrous flood that engulfed the Dutch coastal province of Zeeland in 1953. When their farmhouse is destroyed by the flood, teenage mother Julia gets separated from her baby boy, whom she kept hidden in a box. She is saved from drowning by a young air force lieutenant, who agrees to go help looking for Julia's little son.
- **跳转**: https://themoviecosmos.com/movie/29602
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p1: fragments=[who-1, result-0, why-0, how-0, result-1] · sim=0.5501 · **命中分=5**
  - THE-EXPLORER/su-persona-The-Explorer-p3: fragments=[result-0, how-5, result-4] · sim=0.5821 · **命中分=3**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 8 -->
### Global Meltdown (2017) [THE-HERO, THE-OUTLAW]
- **tmdb_id**: 514690
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.5490
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5490
- **genres** / **language**: Action, Science Fiction, Thriller, TV Movie / en
- **overview**: A helicopter pilot and an environmental scientist lead a exodus of survivors in a search for a safe haven after a catastrophic tectonic event causes the crust of the earth to break apart.
- **跳转**: https://themoviecosmos.com/movie/514690
- **命中视角/碎片**:
  - THE-HERO/su-persona-The-Hero-p1: fragments=[result-0, why-0, how-2, result-5] · sim=0.5490 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p2: fragments=[who-1, why-0, how-2, result-1] · sim=0.5396 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 1 candidate(s)

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 5 -->
### Malibu Shark Attack (2009) [THE-RULER]
- **tmdb_id**: 53080
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.5748
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5748
- **genres** / **language**: Horror, Action, TV Movie / en
- **overview**: An underwater earthquake generates a tsunami that strikes Malibu, bringing a hunting pack of prehistoric-looking goblin sharks to the surface. Although the beach is evacuated before the big wave strikes, a group of lifeguards and a crew of construction workers are stranded in the high water and have to fight the sharks to get to dry land.
- **跳转**: https://themoviecosmos.com/movie/53080
- **命中视角/碎片**:
  - THE-RULER/su-persona-The-Ruler-p2: fragments=[how-4, how-2, how-3, result-0, result-2] · sim=0.5748 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

## 06-tech-monopoly

# 现实波澜 · 06-tech-monopoly

## 元信息
- date: 2026-05-27
- news_url: https://thenextweb.com/news/eu-google-dma-fine-search-self-preferencing
- run_id: 06-tech-monopoly

## 现实波澜
- **title**: EU poised to hit Google with record Digital Markets Act fine over search self-preferencing
- **source** / **pub_time**: The Next Web / 2026-05-27T12:00:00+02:00
- **summary**: European regulators are finalizing a penalty expected to reach the high hundreds of millions of euros for ranking Google's own shopping, flight, and hotel units above rival comparison services in search results. Brussels rejected the company's remedy proposals after more than two years of proceedings under the bloc's gatekeeper rules. A formal decision is expected before the Commission's August recess, adding to more than a decade of accumulated competition fines against Alphabet.

### 多 agents 命中

**Count:** 8 candidate(s)

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 16 -->
### The Cop (1970) [THE-CAREGIVER, THE-CREATOR, THE-EXPLORER, THE-SAGE]
- **tmdb_id**: 94376
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 164.5211
  - **persona_agent_count**: 4
  - **source_hits**: surface=0 / event=0 / persona=4
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5211
- **genres** / **language**: Drama, Crime, Thriller / fr
- **overview**: A crackdown on drugs leads a burned out cop to take the law into his own hands and seek revenge against villainous drug dealers. Word comes down from above that the United States feels French authorities have been lax on their arrests of the dealers. A violent action feature finds the harried inspector battling his colleagues as much as the criminal element targeted for extermination.
- **跳转**: https://themoviecosmos.com/movie/94376
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p1: fragments=[who-2, why-0, how-1, result-0] · sim=0.4501 · **命中分=4**
  - THE-CREATOR/su-persona-The-Creator-p3: fragments=[how-2, how-0, how-1, why-1] · sim=0.5211 · **命中分=4**
  - THE-EXPLORER/su-persona-The-Explorer-p2: fragments=[result-0, why-0, how-0, why-1] · sim=0.5175 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p1: fragments=[how-0, how-1, result-0, result-1] · sim=0.4325 · **命中分=4**
- **pseudo命中分合计**: 16
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 14 -->
### The Floorwalker (1916) [THE-EVERYMAN, THE-HERO, THE-OUTLAW, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-INNOCENT]
- **tmdb_id**: 53416
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 146.4934
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=6 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4934
- **genres** / **language**: Comedy / en
- **overview**: An impecunious customer creates chaos in a department store while the manager and his assistant plot to steal the money kept in the establishment's safe.
- **跳转**: https://themoviecosmos.com/movie/53416
- **命中视角/碎片**:
  - THE-EVERYMAN/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.3897
  - THE-HERO/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, how-3] · sim=0.3901
  - THE-OUTLAW/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.3852
  - THE-RULER/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.3860
  - THE-MAGICIAN/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.3585
  - THE-SAGE/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.3844
  - THE-EVERYMAN/su-persona-The-Everyman-p2: fragments=[who-2, why-1, how-2, result-0, result-1] · sim=0.4934 · **命中分=5**
  - THE-INNOCENT/su-persona-The-Innocent-p2: fragments=[who-2, why-0, why-1, result-0, result-1] · sim=0.4218 · **命中分=5**
  - THE-RULER/su-persona-The-Ruler-p1: fragments=[result-0, how-0, how-1, how-2] · sim=0.4618 · **命中分=4**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 13 -->
### Gabbar Is Back (2015) [THE-CAREGIVER, THE-EVERYMAN, THE-OUTLAW]
- **tmdb_id**: 337876
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 146.5231
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5231
- **genres** / **language**: Drama, Action / hi
- **overview**: A vigilante network taking out corrupt officials draws the notice of the authorities.
- **跳转**: https://themoviecosmos.com/movie/337876
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[result-1, why-0, how-0] · sim=0.4790 · **命中分=3**
  - THE-EVERYMAN/su-persona-The-Everyman-p2: fragments=[who-2, why-1, how-2, result-0, result-1] · sim=0.5231 · **命中分=5**
  - THE-OUTLAW/su-persona-The-Outlaw-p2: fragments=[who-2, why-0, why-1, how-3, result-1] · sim=0.4439 · **命中分=5**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 9 -->
### To Skin a Spy (1966) [THE-EXPLORER, THE-SAGE]
- **tmdb_id**: 82098
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.5513
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5513
- **genres** / **language**: Thriller / fr
- **overview**: A French secret agent gets a license to kill when he is sent to Vienna to plug a security leak in this routine spy saga. He is caught in the crossfire of international enemy agents trying to eliminate the French.
- **跳转**: https://themoviecosmos.com/movie/82098
- **命中视角/碎片**:
  - THE-EXPLORER/su-persona-The-Explorer-p1: fragments=[how-1, how-0, result-0, result-1] · sim=0.4824 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p3: fragments=[who-0, result-0, how-1, result-1, why-1] · sim=0.5513 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 8 -->
### Taxi 4 (2007) [THE-EXPLORER, THE-SAGE]
- **tmdb_id**: 2335
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 128.4866
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4866
- **genres** / **language**: Action, Comedy, Crime / fr
- **overview**: Before being extradited to Africa to stand trial, a notorious Belgian criminal is entrusted to the Marseilles police department for less than 24 hours. But the wily crook convinces bumbling policeman Emilien he's a lowly Belgian embassy employee who got railroaded by the brilliant master criminal.
- **跳转**: https://themoviecosmos.com/movie/2335
- **命中视角/碎片**:
  - THE-EXPLORER/su-persona-The-Explorer-p1: fragments=[how-1, how-0, result-0, result-1] · sim=0.4623 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p1: fragments=[how-0, how-1, result-0, result-1] · sim=0.4866 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 8 -->
### Chicken and Duck Talk (1988) [THE-RULER, THE-EXPLORER, THE-HERO]
- **tmdb_id**: 47291
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.4993
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=1 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4993
- **genres** / **language**: Comedy / cn
- **overview**: A witty and thoroughly engaging send-up of both the fast food business and the cut-throat techniques often employed by conglomerates to crush independent competition.
- **跳转**: https://themoviecosmos.com/movie/47291
- **命中视角/碎片**:
  - THE-RULER/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.3690
  - THE-EXPLORER/su-persona-The-Explorer-p3: fragments=[who-0, why-1, result-0, how-3] · sim=0.4949 · **命中分=4**
  - THE-HERO/su-persona-The-Hero-p3: fragments=[why-0, how-2, result-0, result-1] · sim=0.4993 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 8 -->
### Capital (2012) [THE-CREATOR, THE-RULER]
- **tmdb_id**: 121793
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.4985
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4985
- **genres** / **language**: Drama, Thriller / fr
- **overview**: The head of a giant European investment bank desperately clings to power when an American hedge fund company tries to buy them out.
- **跳转**: https://themoviecosmos.com/movie/121793
- **命中视角/碎片**:
  - THE-CREATOR/su-persona-The-Creator-p3: fragments=[how-2, how-0, how-1, why-1] · sim=0.4985 · **命中分=4**
  - THE-RULER/su-persona-The-Ruler-p3: fragments=[why-0, why-1, how-3, result-0] · sim=0.4223 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### Your Lucky Day (2023) [THE-JESTER, THE-LOVER]
- **tmdb_id**: 923993
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 128.5627
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5627
- **genres** / **language**: Thriller, Crime, Action / en
- **overview**: After a dispute over a winning lottery ticket turns into a deadly hostage situation, the witnesses must decide exactly how far they’ll go—and how much blood they’re willing to spill—for a cut of the $156 million.
- **跳转**: https://themoviecosmos.com/movie/923993
- **命中视角/碎片**:
  - THE-JESTER/su-persona-The-Jester-p3: fragments=[result-0, why-0, how-2, how-3, result-1] · sim=0.4908 · **命中分=5**
  - THE-LOVER/su-persona-The-Lover-p2: fragments=[result-0, why-0] · sim=0.5627 · **命中分=2**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 3 candidate(s)

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### Speaking of Murder (1957) [THE-JESTER]
- **tmdb_id**: 58926
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.5251
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5251
- **genres** / **language**: Crime, Drama, Thriller / fr
- **overview**: Louis Bertain is the owner of a Paris garage which is the front for a robbery gang. He and his accomplices are careful to keep up a civic veneer by day, indulging in criminal activities only when "the red light is on" at night. This status quo is upset when one of the gang members becomes convinced that Louis' younger brother is a police informer.
- **跳转**: https://themoviecosmos.com/movie/58926
- **命中视角/碎片**:
  - THE-JESTER/su-persona-The-Jester-p1: fragments=[how-3, how-0, how-1, how-2, result-0] · sim=0.5251 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### Special Section (1975) [THE-SAGE]
- **tmdb_id**: 79921
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.5101
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5101
- **genres** / **language**: Drama, History, Thriller / fr
- **overview**: In Nazi-occupied France, a German officer is assassinated. The Germans demand justice, and the Vichy government is quick to capitulate. Unable to apprehend the actual culprits, Minister of Justice Joseph Barthélémy decides the execution of token Frenchmen will suffice, but the problem is finding judges and jurors eager to participate in a sham trial of innocent men. The solution is a Special Section, a court comprised of individuals handpicked for this exact purpose.
- **跳转**: https://themoviecosmos.com/movie/79921
- **命中视角/碎片**:
  - THE-SAGE/su-persona-The-Sage-p3: fragments=[who-0, result-0, how-1, result-1, why-1] · sim=0.5101 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### Stolen: Heist of the Century (2025) [THE-JESTER]
- **tmdb_id**: 1513598
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.5186
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5186
- **genres** / **language**: Documentary, Crime / en
- **overview**: Antwerp, 2003. A gang of thieves rob the impenetrable Diamond Center. Who was behind one of the world's biggest heists - and how did they pull it off?
- **跳转**: https://themoviecosmos.com/movie/1513598
- **命中视角/碎片**:
  - THE-JESTER/su-persona-The-Jester-p1: fragments=[how-3, how-0, how-1, how-2, result-0] · sim=0.5186 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

## 07-migration-border

# 现实波澜 · 07-migration-border

## 元信息
- date: 2026-04-03
- news_url: https://www.wola.org/2026/04/u-s-mexico-border-update-border-data-reconciliation-bill-dhs-transition-ice-detention-wall-migration-route/
- run_id: 07-migration-border

## 现实波澜
- **title**: Border apprehensions tick up 25% as seasonal migration meets hardened enforcement
- **source** / **pub_time**: WOLA / 2026-04-03T12:00:00-04:00
- **summary**: U.S. Border Patrol apprehended 8,268 people along the southwest border in March 2026, up from 6,598 in February, even as year-to-date crossings remain near multi-decade lows under asylum shutdown and deportation policies. Analysts attribute the month-on-month rise to milder spring weather rather than a reversal of the broader collapse in unauthorized crossings since 2024. Lawmakers remain deadlocked over separate funding for immigration enforcement agencies in a pending reconciliation package.

### 多 agents 命中

**Count:** 11 candidate(s)

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 93 -->
### Transpecos (2016) [THE-CAREGIVER, THE-CREATOR, THE-EVERYMAN, THE-EXPLORER, THE-HERO, THE-INNOCENT, THE-JESTER, THE-LOVER, THE-MAGICIAN, THE-OUTLAW, THE-RULER, THE-SAGE]
- **tmdb_id**: 381018
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 260.6271
  - **persona_agent_count**: 12
  - **source_hits**: surface=0 / event=0 / persona=25
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result, where, who, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6271
- **genres** / **language**: Thriller / en
- **overview**: For three US Border Patrol agents, the contents of one car reveal an insidious plot within their own ranks. The next 24 hours may cost them their lives.
- **跳转**: https://themoviecosmos.com/movie/381018
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[result-1, how-0, result-0] · sim=0.5822 · **命中分=3**
  - THE-CAREGIVER/su-persona-The-Caregiver-p3: fragments=[result-0, why-0, how-0, result-1] · sim=0.4836 · **命中分=4**
  - THE-CREATOR/su-persona-The-Creator-p1: fragments=[how-0, why-0, result-0, result-1] · sim=0.5654 · **命中分=4**
  - THE-CREATOR/su-persona-The-Creator-p3: fragments=[who-0, how-0, why-0, result-0] · sim=0.4971 · **命中分=4**
  - THE-EVERYMAN/su-persona-The-Everyman-p2: fragments=[result-0, how-0, result-1] · sim=0.5332 · **命中分=3**
  - THE-EXPLORER/su-persona-The-Explorer-p1: fragments=[where-0, why-0, how-0, result-0] · sim=0.4975 · **命中分=4**
  - THE-EXPLORER/su-persona-The-Explorer-p2: fragments=[who-1, how-0, result-0] · sim=0.5497 · **命中分=3**
  - THE-EXPLORER/su-persona-The-Explorer-p3: fragments=[why-0, how-0, result-1] · sim=0.4645 · **命中分=3**
  - THE-HERO/su-persona-The-Hero-p2: fragments=[result-0, why-0, how-0, result-1] · sim=0.4917 · **命中分=4**
  - THE-HERO/su-persona-The-Hero-p3: fragments=[how-0, why-0, result-0, result-1] · sim=0.4867 · **命中分=4**
  - THE-INNOCENT/su-persona-The-Innocent-p2: fragments=[result-0, how-0, why-0, result-1] · sim=0.4819 · **命中分=4**
  - THE-INNOCENT/su-persona-The-Innocent-p3: fragments=[result-1, why-0, how-0, result-0] · sim=0.5225 · **命中分=4**
  - THE-JESTER/su-persona-The-Jester-p1: fragments=[result-1, why-0, how-0, result-0] · sim=0.4831 · **命中分=4**
  - THE-JESTER/su-persona-The-Jester-p3: fragments=[how-0, why-0, result-0, result-1] · sim=0.4939 · **命中分=4**
  - THE-LOVER/su-persona-The-Lover-p2: fragments=[result-0, how-0, result-1] · sim=0.6220 · **命中分=3**
  - THE-LOVER/su-persona-The-Lover-p3: fragments=[how-0, result-0, result-1] · sim=0.6271 · **命中分=3**
  - THE-MAGICIAN/su-persona-The-Magician-p1: fragments=[result-0, how-0, why-0, result-1] · sim=0.5167 · **命中分=4**
  - THE-MAGICIAN/su-persona-The-Magician-p3: fragments=[result-1, result-0, why-0, how-0] · sim=0.5308 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p1: fragments=[who-1, why-0, how-0, result-0, result-1] · sim=0.4823 · **命中分=5**
  - THE-OUTLAW/su-persona-The-Outlaw-p2: fragments=[result-0, why-0, how-0, result-1] · sim=0.4855 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p3: fragments=[who-0, how-0, result-0, result-1] · sim=0.5266 · **命中分=4**
  - THE-RULER/su-persona-The-Ruler-p1: fragments=[result-0, how-0, result-1] · sim=0.5685 · **命中分=3**
  - THE-RULER/su-persona-The-Ruler-p2: fragments=[who-0, how-0, why-0, result-0, result-1] · sim=0.5226 · **命中分=5**
  - THE-SAGE/su-persona-The-Sage-p2: fragments=[how-0, result-0, why-0] · sim=0.4698 · **命中分=3**
  - THE-SAGE/su-persona-The-Sage-p3: fragments=[result-1, how-0, result-0] · sim=0.4604 · **命中分=3**
- **pseudo命中分合计**: 93
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 42 -->
### Open the Wall (2014) [THE-EVERYMAN, THE-CAREGIVER, THE-CREATOR, THE-EXPLORER, THE-HERO, THE-JESTER, THE-LOVER, THE-RULER] [汇聚标注]
- **tmdb_id**: 301633
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=true, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 334.6276
  - **persona_agent_count**: 7
  - **source_hits**: surface=1 / event=1 / persona=11
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic, surface-fragment-bundle
  - **center_dimensions**: how, result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=7: THE-EXPLORER,THE-JESTER,THE-RULER,THE-HERO,THE-LOVER,THE-CREATOR,THE-CAREGIVER
- **相似度**: 0.6276
- **genres** / **language**: Drama, Comedy / de
- **overview**: A lighthearted look at the opening of the border crossing of Bornholmer Straße in Berlin from the point of view of the confused border guards.
- **跳转**: https://themoviecosmos.com/movie/301633
- **命中视角/碎片**:
  - THE-EVERYMAN/su-event-1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4142
  - THE-CAREGIVER/su-persona-The-Caregiver-p3: fragments=[result-0, why-0, how-0, result-1] · sim=0.5020 · **命中分=4**
  - THE-CREATOR/su-persona-The-Creator-p1: fragments=[how-0, why-0, result-0, result-1] · sim=0.4859 · **命中分=4**
  - THE-CREATOR/su-persona-The-Creator-p3: fragments=[who-0, how-0, why-0, result-0] · sim=0.4836 · **命中分=4**
  - THE-EXPLORER/su-persona-The-Explorer-p2: fragments=[who-1, how-0, result-0] · sim=0.5778 · **命中分=3**
  - THE-HERO/su-persona-The-Hero-p2: fragments=[result-0, why-0, how-0, result-1] · sim=0.5201 · **命中分=4**
  - THE-JESTER/su-persona-The-Jester-p1: fragments=[result-1, why-0, how-0, result-0] · sim=0.4892 · **命中分=4**
  - THE-JESTER/su-persona-The-Jester-p3: fragments=[how-0, why-0, result-0, result-1] · sim=0.5651 · **命中分=4**
  - THE-LOVER/su-persona-The-Lover-p1: fragments=[who-1, why-0, how-0, result-0] · sim=0.4821 · **命中分=4**
  - THE-LOVER/su-persona-The-Lover-p2: fragments=[result-0, how-0, result-1] · sim=0.5231 · **命中分=3**
  - THE-LOVER/su-persona-The-Lover-p3: fragments=[how-0, result-0, result-1] · sim=0.6276 · **命中分=3**
  - THE-RULER/su-persona-The-Ruler-p2: fragments=[who-0, how-0, why-0, result-0, result-1] · sim=0.4681 · **命中分=5**
  - THE-EXPLORER/su-surface-1: fragments=[where-0, who-0, who-1, who-2, who-3] · sim=0.4611
- **pseudo命中分合计**: 42
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 15 -->
### Sleep Dealer (2008) [THE-EVERYMAN, THE-EXPLORER, THE-INNOCENT, THE-LOVER]
- **tmdb_id**: 20764
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 164.4970
  - **persona_agent_count**: 4
  - **source_hits**: surface=0 / event=0 / persona=4
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, where, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4970
- **genres** / **language**: Drama, Science Fiction, Thriller / en
- **overview**: Set in a near-future, militarized world marked by closed borders, virtual labor and a global digital network that joins minds and experiences, three strangers risk their lives to connect with each other and break the barriers of technology.
- **跳转**: https://themoviecosmos.com/movie/20764
- **命中视角/碎片**:
  - THE-EVERYMAN/su-persona-The-Everyman-p2: fragments=[result-0, how-0, result-1] · sim=0.4970 · **命中分=3**
  - THE-EXPLORER/su-persona-The-Explorer-p1: fragments=[where-0, why-0, how-0, result-0] · sim=0.4855 · **命中分=4**
  - THE-INNOCENT/su-persona-The-Innocent-p2: fragments=[result-0, how-0, why-0, result-1] · sim=0.4908 · **命中分=4**
  - THE-LOVER/su-persona-The-Lover-p1: fragments=[who-1, why-0, how-0, result-0] · sim=0.4731 · **命中分=4**
- **pseudo命中分合计**: 15
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 9 -->
### Union Pacific (1939) [THE-INNOCENT, THE-JESTER]
- **tmdb_id**: 43837
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.5663
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5663
- **genres** / **language**: Drama, Western / en
- **overview**: One of the last bills signed by President Lincoln authorizes pushing the Union Pacific Railroad across the wilderness to California. But financial opportunist Asa Barrows hopes to profit from obstructing it. Chief troubleshooter Jeff Butler has his hands full fighting Barrows' agent, gambler Sid Campeau; Campeau's partner Dick Allen is Jeff's war buddy and rival suitor for engineer's daughter Molly Monahan. Who will survive the effort to push the railroad through at any cost?
- **跳转**: https://themoviecosmos.com/movie/43837
- **命中视角/碎片**:
  - THE-INNOCENT/su-persona-The-Innocent-p3: fragments=[result-1, why-0, how-0, result-0] · sim=0.5407 · **命中分=4**
  - THE-JESTER/su-persona-The-Jester-p2: fragments=[who-3, why-0, how-0, result-0, result-1] · sim=0.5663 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 9 -->
### Colosio (2012) [THE-INNOCENT, THE-RULER]
- **tmdb_id**: 151708
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.5014
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5014
- **genres** / **language**: Crime, Drama, Thriller / es
- **overview**: It's 1994 in Mexico, the nation was witnessing a turbulent year since its beginnings. An indigenous rebellion shakes the country. Three months later, the ruling party's presidential candidate is brutally murdered during a rally in Tijuana. The country is concerned. Nobody knows who's behind this event, it all points to a conspiracy. Andrés Vázquez, an intelligence expert, is commissioned to lead a secret investigation parallel to the official government issued one. But another expert agent, el Seco, has received orders to wipe out all witnesses and get rid of the evidence surrounding the candidate's murder. As Andrés begins putting the pieces of this intricate puzzle together and comes closer to the truth, he realizes he's also putting his life and that of his loved ones in peril.
- **跳转**: https://themoviecosmos.com/movie/151708
- **命中视角/碎片**:
  - THE-INNOCENT/su-persona-The-Innocent-p1: fragments=[who-1, why-0, how-0, result-0, result-1] · sim=0.4666 · **命中分=5**
  - THE-RULER/su-persona-The-Ruler-p3: fragments=[result-1, how-0, why-0, result-0] · sim=0.5014 · **命中分=4**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 9 -->
### Broken Horses (2015) [THE-HERO, THE-RULER]
- **tmdb_id**: 319910
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.5040
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5040
- **genres** / **language**: Thriller, Mystery, Drama, Crime / en
- **overview**: The bonds of brotherhood, the laws of loyalty, and the futility of violence in the shadows of the US Mexico border gang wars.
- **跳转**: https://themoviecosmos.com/movie/319910
- **命中视角/碎片**:
  - THE-HERO/su-persona-The-Hero-p1: fragments=[who-0, why-0, how-0, result-0, result-1] · sim=0.5040 · **命中分=5**
  - THE-RULER/su-persona-The-Ruler-p3: fragments=[result-1, how-0, why-0, result-0] · sim=0.4999 · **命中分=4**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 8 -->
### If It's Tuesday, This Must Be Belgium (1969) [THE-CAREGIVER, THE-EVERYMAN]
- **tmdb_id**: 11643
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 128.5350
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5350
- **genres** / **language**: Romance, Comedy, Adventure / en
- **overview**: A group of travelers from the United States race through seven European countries in 18 days.
- **跳转**: https://themoviecosmos.com/movie/11643
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p1: fragments=[who-1, why-0, how-0, result-0] · sim=0.5350 · **命中分=4**
  - THE-EVERYMAN/su-persona-The-Everyman-p1: fragments=[who-1, why-0, how-0, result-1] · sim=0.4186 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 7 -->
### Absolute Zero (2006) [THE-EVERYMAN, THE-EXPLORER]
- **tmdb_id**: 25012
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.4581
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4581
- **genres** / **language**: Action, Science Fiction, TV Movie / en
- **overview**: INTER SCI climatologist Dr. David Kotzman has evidence that a shift in the Earth's polarity triggered the last Ice Age...in a single day. Now, it's happening again, and there's no time to escape. As the temperature plummets, Miami is blasted with snow and ice. Evacuation routes are jammed. The only chance David, his old flame Bryn, and a few other hopeful survivors have is to hole themselves up in a special chamber at INTER SCI. A desperate race for survival is ignited as nature's fury rages and the temperature plunges toward -459.67° F...ABSOLUTE ZERO!
- **跳转**: https://themoviecosmos.com/movie/25012
- **命中视角/碎片**:
  - THE-EVERYMAN/su-persona-The-Everyman-p1: fragments=[who-1, why-0, how-0, result-1] · sim=0.4270 · **命中分=4**
  - THE-EXPLORER/su-persona-The-Explorer-p3: fragments=[why-0, how-0, result-1] · sim=0.4581 · **命中分=3**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 7 -->
### The Ice Storm (1997) [THE-MAGICIAN, THE-SAGE]
- **tmdb_id**: 68924
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.4452
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4452
- **genres** / **language**: Drama / en
- **overview**: In the weekend after thanksgiving 1973 the Hood family is skidding out of control. Then an ice storm hits, the worst in a century.
- **跳转**: https://themoviecosmos.com/movie/68924
- **命中视角/碎片**:
  - THE-MAGICIAN/su-persona-The-Magician-p2: fragments=[how-0, why-0, result-0, result-1] · sim=0.4452 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p1: fragments=[result-0, why-0, how-0] · sim=0.4073 · **命中分=3**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 7 -->
### Blood Glacier (2013) [THE-MAGICIAN, THE-SAGE]
- **tmdb_id**: 210913
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.4574
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4574
- **genres** / **language**: Horror / de
- **overview**: At a climate research station in the Alps, the scientists are stunned as the nearby melting glacier is leaking a red liquid. It quickly turns to be very special juice — with unexpected genetic effects on the local wildlife.
- **跳转**: https://themoviecosmos.com/movie/210913
- **命中视角/碎片**:
  - THE-MAGICIAN/su-persona-The-Magician-p2: fragments=[how-0, why-0, result-0, result-1] · sim=0.4574 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p1: fragments=[result-0, why-0, how-0] · sim=0.4040 · **命中分=3**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 6 -->
### Sicario (2015) [THE-CAREGIVER, THE-RULER, THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-MAGICIAN, THE-SAGE, THE-JESTER] [汇聚标注]
- **tmdb_id**: 273481
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=true, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 188.5525
  - **persona_agent_count**: 2
  - **source_hits**: surface=12 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic, surface-fragment-bundle
  - **center_dimensions**: result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=2: THE-RULER,THE-CAREGIVER
- **相似度**: 0.5525
- **genres** / **language**: Action, Crime, Thriller / en
- **overview**: An idealistic FBI agent is enlisted by a government task force to aid in the escalating war against drugs at the border area between the U.S. and Mexico.
- **跳转**: https://themoviecosmos.com/movie/273481
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[result-1, how-0, result-0] · sim=0.5300 · **命中分=3**
  - THE-RULER/su-persona-The-Ruler-p1: fragments=[result-0, how-0, result-1] · sim=0.5525 · **命中分=3**
  - THE-INNOCENT/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.4726
  - THE-EVERYMAN/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.5419
  - THE-HERO/su-surface-1: fragments=[who-0, who-1, who-3, where-0, who-2] · sim=0.5254
  - THE-CAREGIVER/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.5218
  - THE-EXPLORER/su-surface-1: fragments=[where-0, who-0, who-1, who-2, who-3] · sim=0.4773
  - THE-OUTLAW/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.4799
  - THE-LOVER/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.4787
  - THE-CREATOR/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.4955
  - THE-RULER/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.4695
  - THE-MAGICIAN/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.4844
  - THE-SAGE/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.4954
  - THE-JESTER/su-surface-1: fragments=[who-0, who-1, who-2, who-3, where-0] · sim=0.5023
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 4 candidate(s)

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 13 -->
### Trade (2007) [THE-OUTLAW]
- **tmdb_id**: 4170
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 126.5206
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5206
- **genres** / **language**: Thriller / en
- **overview**: A Texas cop, whose own daughter might have been forced into sexual slavery, joins forces with a Mexican youth to find the boy's sister, who was abducted and forced into prostitution. Meanwhile, a Polish woman who was promised a better life in America also becomes a victim.
- **跳转**: https://themoviecosmos.com/movie/4170
- **命中视角/碎片**:
  - THE-OUTLAW/su-persona-The-Outlaw-p1: fragments=[who-1, why-0, how-0, result-0, result-1] · sim=0.5037 · **命中分=5**
  - THE-OUTLAW/su-persona-The-Outlaw-p2: fragments=[result-0, why-0, how-0, result-1] · sim=0.4594 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p3: fragments=[who-0, how-0, result-0, result-1] · sim=0.5206 · **命中分=4**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 5 -->
### The Life and Times of Judge Roy Bean (1972) [THE-JESTER]
- **tmdb_id**: 33638
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.5642
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5642
- **genres** / **language**: Western, Comedy / en
- **overview**: Outlaw and self-appointed lawmaker Judge Roy Bean rules over an empty stretch of the West that gradually grows, under his iron fist, into a thriving town, while dispensing his his own quirky brand of frontier justice upon strangers passing by.
- **跳转**: https://themoviecosmos.com/movie/33638
- **命中视角/碎片**:
  - THE-JESTER/su-persona-The-Jester-p2: fragments=[who-3, why-0, how-0, result-0, result-1] · sim=0.5642 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 5 -->
### Danger Close: The Battle of Long Tan (2019) [THE-HERO]
- **tmdb_id**: 508664
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.5033
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5033
- **genres** / **language**: War, Action, Drama, History / en
- **overview**: Vietnam War, 1966. Australia and New Zealand send troops to support the United States and South Vietnamese in their fight against the communist North. Soldiers are very young men, recruits and volunteers who have never been involved in a combat. On August 18th, members of Delta Company will face the true horror of a ruthless battle among the trees of a rubber plantation called Long Tân. They are barely a hundred. The enemy is a human wave ready to destroy them.
- **跳转**: https://themoviecosmos.com/movie/508664
- **命中视角/碎片**:
  - THE-HERO/su-persona-The-Hero-p1: fragments=[who-0, why-0, how-0, result-0, result-1] · sim=0.5033 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 5 -->
### Stranded (2021) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-JESTER] [汇聚标注]
- **tmdb_id**: 841793
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=false, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 198.4923
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=12 / persona=1
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=1: THE-INNOCENT
- **相似度**: 0.4923
- **genres** / **language**: Drama / pt
- **overview**: Tensions run high while food runs low as six influencers find themselves stranded on a secluded island after plans for a weekend escape go awry.
- **跳转**: https://themoviecosmos.com/movie/841793
- **命中视角/碎片**:
  - THE-INNOCENT/su-event-1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4123
  - THE-EVERYMAN/su-event-1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4054
  - THE-HERO/su-event-1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4265
  - THE-CAREGIVER/su-event-1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4184
  - THE-EXPLORER/su-event-1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4028
  - THE-OUTLAW/su-event-1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4214
  - THE-LOVER/su-event-1: fragments=[why-0, how-0, result-0, result-1] · sim=0.3970
  - THE-CREATOR/su-event-1: fragments=[how-0, why-0, result-0, result-1] · sim=0.4153
  - THE-RULER/su-event-1: fragments=[how-0, why-0, result-0, result-1] · sim=0.4046
  - THE-MAGICIAN/su-event-1: fragments=[why-0, how-0, result-0, result-1] · sim=0.3918
  - THE-SAGE/su-event-1: fragments=[why-0, how-0, result-0, result-1] · sim=0.3726
  - THE-JESTER/su-event-1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4146
  - THE-INNOCENT/su-persona-The-Innocent-p1: fragments=[who-1, why-0, how-0, result-0, result-1] · sim=0.4923 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

## 08-sports-underdog

# 现实波澜 · 08-sports-underdog

## 元信息
- date: 2026-05-27
- news_url: https://www.bostonglobe.com/2026/05/27/sports/nhl-playoffs-golden-knights-avalanche-game-4-score/
- run_id: 08-sports-underdog

## 现实波澜
- **title**: Golden Knights sweep Presidents' Trophy Avalanche to reach Stanley Cup Final
- **source** / **pub_time**: Boston Globe / 2026-05-27T06:00:00-07:00
- **summary**: Vegas scored twice and held Colorado's league-leading offense to one goal in Game 4, completing a four-game Western Conference Final sweep on May 26. The franchise fired its coach with eight regular-season games left before John Tortorella guided a 7-0-1 close and playoff runs past Utah and Anaheim. Colorado entered the series as heavy favorites after dominating the regular season but lost top stars Cale Makar and Nathan MacKinnon to injuries.

### 多 agents 命中

**Count:** 6 candidate(s)

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 16 -->
### Three Seconds (2017) [THE-EVERYMAN, THE-LOVER, THE-MAGICIAN, THE-OUTLAW]
- **tmdb_id**: 444218
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 156.5397
  - **persona_agent_count**: 4
  - **source_hits**: surface=0 / event=0 / persona=4
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5397
- **genres** / **language**: Drama / ru
- **overview**: The story is set at the 1972 Munich Olympics where the U.S. team lost the basketball championship for the first time in 36 years. The final moments of the final game have become one of the most controversial events in Olympic history. With play tied, the score table horn sounded during a second free throw attempt that put the U.S. ahead by one. But the Soviets claimed they had called for a time out before the basket and confusion ensued. The clock was set back by three seconds twice in a row and the Russians finally prevailed at the very last. The U.S. protested, but a jury decided in the USSR’s favor and Team USA voted unanimously to refuse its silver medals. The Soviet players have been treated as heroes at home.
- **跳转**: https://themoviecosmos.com/movie/444218
- **命中视角/碎片**:
  - THE-EVERYMAN/su-persona-The-Everyman-p1: fragments=[who-1, why-0, how-4, result-0] · sim=0.4858 · **命中分=4**
  - THE-LOVER/su-persona-The-Lover-p2: fragments=[who-1, why-0, how-3, how-4, result-0] · sim=0.5397 · **命中分=5**
  - THE-MAGICIAN/su-persona-The-Magician-p3: fragments=[result-0, how-3, how-4] · sim=0.5124 · **命中分=3**
  - THE-OUTLAW/su-persona-The-Outlaw-p2: fragments=[result-0, why-0, how-3, how-4] · sim=0.5064 · **命中分=4**
- **pseudo命中分合计**: 16
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 10 -->
### One Piece: Dream Soccer King! (2002) [THE-INNOCENT, THE-MAGICIAN, THE-OUTLAW]
- **tmdb_id**: 464198
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 146.5460
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5460
- **genres** / **language**: Fantasy, Comedy, Animation / ja
- **overview**: At a huge pillar stadium, the Grand Line Cup Final is being held. The "Straw Hat Pirate Team"(Luffy, Zoro, Usopp, Sanji, and Chopper) are having a tie breaker shoot out against the "Villian All Star Team"(Buggy, Bon Clay, Jango, Hatchan, and a soccer like head player named Odacchi). Everyone of them gets a turn in kicking the ball to the goal. While Coby is taking the goalie position, and isn't doing too good in blocking the goal. One after another, the game eventually comes to a sudden death match. Which team will win the Grand Line Cup?
- **跳转**: https://themoviecosmos.com/movie/464198
- **命中视角/碎片**:
  - THE-INNOCENT/su-persona-The-Innocent-p2: fragments=[why-0, how-3, how-4] · sim=0.5460 · **命中分=3**
  - THE-MAGICIAN/su-persona-The-Magician-p3: fragments=[result-0, how-3, how-4] · sim=0.4761 · **命中分=3**
  - THE-OUTLAW/su-persona-The-Outlaw-p2: fragments=[result-0, why-0, how-3, how-4] · sim=0.5446 · **命中分=4**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 8 -->
### In Which We Serve (1942) [THE-CAREGIVER, THE-HERO]
- **tmdb_id**: 28093
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 128.6242
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6242
- **genres** / **language**: Drama, War / en
- **overview**: The story of the HMS Torrin, from its construction to its sinking in the Mediterranean during action in World War II. The ship’s first and only commanding officer is Captain E.V. Kinross, who trains his men not only to be loyal to him and the country, but—most importantly—to themselves.
- **跳转**: https://themoviecosmos.com/movie/28093
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[who-2, how-0, how-1, how-2] · sim=0.6242 · **命中分=4**
  - THE-HERO/su-persona-The-Hero-p2: fragments=[who-2, how-2, how-3, how-4] · sim=0.5039 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 8 -->
### By the Law (1926) [THE-HERO, THE-LOVER]
- **tmdb_id**: 126644
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 128.5263
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5263
- **genres** / **language**: Drama, Western, Mystery, Action / ru
- **overview**: After a man kills two members of his Yukon gold prospecting team, the other two surviving members struggle to keep him subdued for the next several months until they can turn him over to the law. Based on Jack London's 'The Unexpected' (1905).
- **跳转**: https://themoviecosmos.com/movie/126644
- **命中视角/碎片**:
  - THE-HERO/su-persona-The-Hero-p3: fragments=[who-1, why-0, how-4] · sim=0.5263 · **命中分=3**
  - THE-LOVER/su-persona-The-Lover-p2: fragments=[who-1, why-0, how-3, how-4, result-0] · sim=0.4860 · **命中分=5**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 7 -->
### Hoosiers (1986) [THE-OUTLAW, THE-CAREGIVER, THE-EVERYMAN] [汇聚标注]
- **tmdb_id**: 5693
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=false, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 216.5343
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=1 / persona=2
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic
  - **center_dimensions**: how, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=2: THE-CAREGIVER,THE-EVERYMAN
- **相似度**: 0.5343
- **genres** / **language**: Drama, Family / en
- **overview**: Failed college coach Norman Dale gets a chance at redemption when he is hired to coach a high school basketball team in a tiny Indiana town. After a teacher persuades star player Jimmy Chitwood to quit and focus on his long-neglected studies, Dale struggles to develop a winning team in the face of community criticism for his temper and his unconventional choice of assistant coach: Shooter, a notorious alcoholic.
- **跳转**: https://themoviecosmos.com/movie/5693
- **命中视角/碎片**:
  - THE-OUTLAW/su-event-1: fragments=[how-0, how-1, how-2, how-3, how-4, why-0, result-0] · sim=0.5305
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[who-2, how-0, how-1, how-2] · sim=0.5315 · **命中分=4**
  - THE-EVERYMAN/su-persona-The-Everyman-p3: fragments=[how-0, how-1, how-2] · sim=0.5343 · **命中分=3**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 7 -->
### The Wild Soccer Bunch 2 (2005) [THE-CREATOR, THE-INNOCENT]
- **tmdb_id**: 8344
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 128.5514
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5514
- **genres** / **language**: Adventure, Family, Comedy / de
- **overview**: An unsupervised junior soccer team loses its ace player to the leader of a rival gang. Since only an entire team can win, they must have her back to be able to win the game against the national team. The existence of The Wild Soccer Bunch is at stake ...
- **跳转**: https://themoviecosmos.com/movie/8344
- **命中视角/碎片**:
  - THE-CREATOR/su-persona-The-Creator-p2: fragments=[why-0, how-3, how-4, result-0] · sim=0.5170 · **命中分=4**
  - THE-INNOCENT/su-persona-The-Innocent-p2: fragments=[why-0, how-3, how-4] · sim=0.5514 · **命中分=3**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 0 candidate(s)

## 09-cultural-backlash

# 现实波澜 · 09-cultural-backlash

## 元信息
- date: 2026-05-25
- news_url: https://quillette.com/2026/05/25/homeric-heresies-christopher-nolan-odyssey-lupita-nyongo/
- run_id: 09-cultural-backlash

## 现实波澜
- **title**: Nolan's Odyssey casting of Black actress as Helen of Troy ignites culture-war fight
- **source** / **pub_time**: Quillette / 2026-05-25T12:00:00+01:00
- **summary**: Christopher Nolan's upcoming Homer adaptation drew fierce online attacks after Lupita Nyong'o was cast as Helen of Troy and Clytemnestra, with prominent commentators accusing the production of erasing European history. Defenders argued diverse casting treats the Western canon as shared civilizational heritage rather than racial gatekeeping. The dispute has turned a mythic epic into a flashpoint over identity, belonging, and who may claim classical stories in mass-market film.

### 多 agents 命中

**Count:** 11 candidate(s)

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 30 -->
### Don't Leave Home (2018) [THE-MAGICIAN, THE-SAGE, THE-CAREGIVER, THE-CREATOR, THE-EXPLORER, THE-HERO] [汇聚标注]
- **tmdb_id**: 502167
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=false, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 254.6509
  - **persona_agent_count**: 5
  - **source_hits**: surface=0 / event=2 / persona=7
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic
  - **center_dimensions**: how, result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=5: THE-SAGE,THE-HERO,THE-EXPLORER,THE-CREATOR,THE-CAREGIVER
- **相似度**: 0.6509
- **genres** / **language**: Thriller, Mystery / en
- **overview**: An American artist's obsession with a disturbing urban legend leads her to an investigation of the story's origins at the crumbling estate of a reclusive painter in Ireland.
- **跳转**: https://themoviecosmos.com/movie/502167
- **命中视角/碎片**:
  - THE-MAGICIAN/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5173
  - THE-SAGE/su-event-1: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4917
  - THE-CAREGIVER/su-persona-The-Caregiver-p1: fragments=[who-1, how-0, how-1, how-2, result-0] · sim=0.5822 · **命中分=5**
  - THE-CREATOR/su-persona-The-Creator-p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.5713 · **命中分=4**
  - THE-CREATOR/su-persona-The-Creator-p3: fragments=[who-0, how-1, how-2, how-3, result-0] · sim=0.6509 · **命中分=5**
  - THE-EXPLORER/su-persona-The-Explorer-p1: fragments=[how-0, how-1, how-2, how-3] · sim=0.5109 · **命中分=4**
  - THE-HERO/su-persona-The-Hero-p2: fragments=[result-0, why-1, how-1, result-1] · sim=0.5158 · **命中分=4**
  - THE-HERO/su-persona-The-Hero-p3: fragments=[how-3, how-2, why-1, result-0] · sim=0.5124 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p3: fragments=[how-3, why-0, why-1, result-1] · sim=0.4616 · **命中分=4**
- **pseudo命中分合计**: 30
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 21 -->
### Venus in Fur (2013) [THE-EVERYMAN, THE-EXPLORER, THE-INNOCENT, THE-MAGICIAN]
- **tmdb_id**: 197082
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 164.6850
  - **persona_agent_count**: 4
  - **source_hits**: surface=0 / event=0 / persona=5
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6850
- **genres** / **language**: Drama / fr
- **overview**: An enigmatic actress may have a hidden agenda when she auditions for a part in a misogynistic writer's play.
- **跳转**: https://themoviecosmos.com/movie/197082
- **命中视角/碎片**:
  - THE-EVERYMAN/su-persona-The-Everyman-p1: fragments=[who-1, how-0, how-1, result-0, result-1] · sim=0.6467 · **命中分=5**
  - THE-EXPLORER/su-persona-The-Explorer-p3: fragments=[who-1, how-0, how-1, how-2, why-0] · sim=0.6115 · **命中分=5**
  - THE-INNOCENT/su-persona-The-Innocent-p1: fragments=[result-0, how-0, how-1, why-1] · sim=0.6850 · **命中分=4**
  - THE-INNOCENT/su-persona-The-Innocent-p2: fragments=[who-1, how-0, how-1, how-2, how-3] · sim=0.5841 · **命中分=5**
  - THE-MAGICIAN/su-persona-The-Magician-p1: fragments=[how-0, how-1] · sim=0.5516 · **命中分=2**
- **pseudo命中分合计**: 21
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 14 -->
### W's Tragedy (1984) [THE-EVERYMAN, THE-INNOCENT]
- **tmdb_id**: 326598
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.6071
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6071
- **genres** / **language**: Drama, Mystery / ja
- **overview**: A young theatre actress fights for her uncertain career while having to confront the personal sacrifices that will arise from it.
- **跳转**: https://themoviecosmos.com/movie/326598
- **命中视角/碎片**:
  - THE-EVERYMAN/su-persona-The-Everyman-p1: fragments=[who-1, how-0, how-1, result-0, result-1] · sim=0.5885 · **命中分=5**
  - THE-INNOCENT/su-persona-The-Innocent-p1: fragments=[result-0, how-0, how-1, why-1] · sim=0.6015 · **命中分=4**
  - THE-INNOCENT/su-persona-The-Innocent-p2: fragments=[who-1, how-0, how-1, how-2, how-3] · sim=0.6071 · **命中分=5**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 13 -->
### Breakdown: 1975 (2025) [THE-EVERYMAN, THE-JESTER, THE-RULER]
- **tmdb_id**: 1584125
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 146.6177
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6177
- **genres** / **language**: Documentary / en
- **overview**: In 1975, as America faced social and political upheaval, filmmakers turned chaos into art.
- **跳转**: https://themoviecosmos.com/movie/1584125
- **命中视角/碎片**:
  - THE-EVERYMAN/su-persona-The-Everyman-p2: fragments=[who-4, why-0, how-1, how-2, result-1] · sim=0.5948 · **命中分=5**
  - THE-JESTER/su-persona-The-Jester-p2: fragments=[how-1, how-0, why-0, result-0] · sim=0.5447 · **命中分=4**
  - THE-RULER/su-persona-The-Ruler-p2: fragments=[who-0, how-0, how-1, how-2] · sim=0.6177 · **命中分=4**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 10 -->
### Ben-Hur (1959) [THE-EXPLORER, THE-MAGICIAN, THE-OUTLAW]
- **tmdb_id**: 665
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 154.5413
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5413
- **genres** / **language**: History, Drama, Adventure / en
- **overview**: In ancient Judea, a Jewish aristocrat opposing Roman occupation of his homeland reunites with his childhood friend, now a Roman commander — setting in motion a saga of betrayal, adventure, tragedy, revenge, and faith.
- **跳转**: https://themoviecosmos.com/movie/665
- **命中视角/碎片**:
  - THE-EXPLORER/su-persona-The-Explorer-p2: fragments=[result-0, why-0, how-2, how-3] · sim=0.5413 · **命中分=4**
  - THE-MAGICIAN/su-persona-The-Magician-p2: fragments=[how-2, how-3] · sim=0.4945 · **命中分=2**
  - THE-OUTLAW/su-persona-The-Outlaw-p3: fragments=[why-0, how-2, why-1, how-3] · sim=0.4741 · **命中分=4**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 10 -->
### L'Odissea (1911) [THE-CREATOR, THE-EXPLORER, THE-MAGICIAN] [汇聚标注]
- **tmdb_id**: 194224
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=false, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 218.6123
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=1 / persona=3
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic
  - **center_dimensions**: how
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=3: THE-EXPLORER,THE-CREATOR,THE-MAGICIAN
- **相似度**: 0.6123
- **genres** / **language**: Drama, Adventure / it
- **overview**: Film adaptation of Homer's 'The Odyssey.'
- **跳转**: https://themoviecosmos.com/movie/194224
- **命中视角/碎片**:
  - THE-CREATOR/su-event-1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, why-0, why-1] · sim=0.5715
  - THE-CREATOR/su-persona-The-Creator-p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.5990 · **命中分=4**
  - THE-EXPLORER/su-persona-The-Explorer-p1: fragments=[how-0, how-1, how-2, how-3] · sim=0.5817 · **命中分=4**
  - THE-MAGICIAN/su-persona-The-Magician-p1: fragments=[how-0, how-1] · sim=0.6123 · **命中分=2**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 9 -->
### Phantom of the Opera (1943) [THE-CAREGIVER, THE-JESTER]
- **tmdb_id**: 15855
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.5806
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5806
- **genres** / **language**: Horror, Romance / en
- **overview**: Following a tragic accident that leaves him disfigured, crazed composer Erique Claudin transformed into a masked phantom who schemes to make beautiful young soprano Christine Dubois the star of the opera and wreak revenge on those who stole his music.
- **跳转**: https://themoviecosmos.com/movie/15855
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p1: fragments=[who-1, how-0, how-1, how-2, result-0] · sim=0.5806 · **命中分=5**
  - THE-JESTER/su-persona-The-Jester-p1: fragments=[result-1, how-0, how-1, how-2] · sim=0.5338 · **命中分=4**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 9 -->
### Panama (2015) [THE-LOVER, THE-SAGE]
- **tmdb_id**: 336200
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.6459
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6459
- **genres** / **language**: Thriller, Drama / sr
- **overview**: A thriller that depicts how digital communication, pornography and vanity obstruct true emotions and love.
- **跳转**: https://themoviecosmos.com/movie/336200
- **命中视角/碎片**:
  - THE-LOVER/su-persona-The-Lover-p1: fragments=[who-1, how-0, how-1, why-0, why-1] · sim=0.6459 · **命中分=5**
  - THE-SAGE/su-persona-The-Sage-p2: fragments=[why-0, how-1, why-1, result-1] · sim=0.5372 · **命中分=4**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 9 -->
### Apolonia, Apolonia (2023) [THE-CREATOR, THE-EXPLORER, THE-OUTLAW] [汇聚标注]
- **tmdb_id**: 1047128
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=false, event=true)
  - **persona_semantic_match**: true
  - **convergent_score**: 216.6034
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=1 / persona=2
  - **search_unit_kinds**: event-fragment-bundle, persona-semantic
  - **center_dimensions**: result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=2: THE-EXPLORER,THE-OUTLAW
- **相似度**: 0.6034
- **genres** / **language**: Documentary / da
- **overview**: When Danish filmmaker Lea Glob first portrayed Apolonia Sokol in 2009, she appeared to be leading a storybook life. The talented Apolonia was born in an underground theater in Paris and grew up in an artists’ community—the ultimate bohemian existence. In her 20s, she studied at the Beaux-Arts de Paris, one of the most prestigious art academies in Europe. Over the years, Lea Glob kept returning to film the charismatic Apolonia and a special bond developed between the two young women.
- **跳转**: https://themoviecosmos.com/movie/1047128
- **命中视角/碎片**:
  - THE-CREATOR/su-event-1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, why-0, why-1] · sim=0.5551
  - THE-EXPLORER/su-persona-The-Explorer-p3: fragments=[who-1, how-0, how-1, how-2, why-0] · sim=0.6034 · **命中分=5**
  - THE-OUTLAW/su-persona-The-Outlaw-p1: fragments=[result-0, how-0, how-1, how-2] · sim=0.5682 · **命中分=4**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 8 -->
### William Tell (2025) [THE-EXPLORER, THE-OUTLAW]
- **tmdb_id**: 1195631
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.5740
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5740
- **genres** / **language**: Action, Adventure, Drama, History / en
- **overview**: The narrative unfolds in the 14th Century, when the European nations vie for supremacy within the Holy Roman Empire. The ambitious Austrian Empire, desiring more land, invades neighbouring Switzerland, a serene and pastoral nation. Protagonist William Tell, a formerly peaceful hunter, finds himself forced to take action as his family and homeland come under threat from the oppressive Austrian King and his ruthless warlords.
- **跳转**: https://themoviecosmos.com/movie/1195631
- **命中视角/碎片**:
  - THE-EXPLORER/su-persona-The-Explorer-p2: fragments=[result-0, why-0, how-2, how-3] · sim=0.5740 · **命中分=4**
  - THE-OUTLAW/su-persona-The-Outlaw-p3: fragments=[why-0, how-2, why-1, how-3] · sim=0.4772 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 7 -->
### Jesus of Montreal (1989) [THE-CREATOR, THE-HERO]
- **tmdb_id**: 4486
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 128.5353
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5353
- **genres** / **language**: Drama, Comedy, Romance / fr
- **overview**: A group of actors putting on an interpretive Passion Play in Montreal begin to experience a meshing of their characters and their private lives as the production takes form against the growing opposition of the Catholic church.
- **跳转**: https://themoviecosmos.com/movie/4486
- **命中视角/碎片**:
  - THE-CREATOR/su-persona-The-Creator-p2: fragments=[result-0, how-3, result-1] · sim=0.4699 · **命中分=3**
  - THE-HERO/su-persona-The-Hero-p2: fragments=[result-0, why-1, how-1, result-1] · sim=0.5353 · **命中分=4**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 3 candidate(s)

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Just a Little Chemistry (2015) [THE-LOVER]
- **tmdb_id**: 277387
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.6226
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6226
- **genres** / **language**: Comedy, Romance / es
- **overview**: Fan girl finds herself torn between the attraction for her film idol and her best male friend.
- **跳转**: https://themoviecosmos.com/movie/277387
- **命中视角/碎片**:
  - THE-LOVER/su-persona-The-Lover-p1: fragments=[who-1, how-0, how-1, why-0, why-1] · sim=0.6226 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### At the Cinema Show (1912) [THE-RULER]
- **tmdb_id**: 347148
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.6155
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6155
- **genres** / **language**: Comedy / it
- **overview**: A cinema becomes the site of sexual intrigue when a man looking for romance in the dark follows a woman into the movies and finds himself molesting her husband instead.
- **跳转**: https://themoviecosmos.com/movie/347148
- **命中视角/碎片**:
  - THE-RULER/su-persona-The-Ruler-p3: fragments=[result-1, result-0, how-1, how-2, how-3] · sim=0.6155 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Be Somebody (2021) [THE-RULER]
- **tmdb_id**: 895435
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.6354
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6354
- **genres** / **language**: Comedy, Mystery, Drama / zh
- **overview**: During the Republican era, a group of frustrated people from the movie industry is invited in a luxurious mansion to make a movie out of a gruesome case that has recently rattled the city of Shanghai, in the hopes that it would turn into a huge sensation and make them famous. However, they never expected that the murderer would be in their midst and that the truth behind the case would be far more bizarre than their fictional movie plot.
- **跳转**: https://themoviecosmos.com/movie/895435
- **命中视角/碎片**:
  - THE-RULER/su-persona-The-Ruler-p3: fragments=[result-1, result-0, how-1, how-2, how-3] · sim=0.6354 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

## 10-whistleblower-leak

# 现实波澜 · 10-whistleblower-leak

## 元信息
- date: 2026-05-16
- news_url: https://www.timesnownews.com/education/how-nta-discovered-neet-ug-2026-chemistry-paper-leak-and-traced-it-to-its-own-system-article-154364673
- run_id: 10-whistleblower-leak

## 现实波澜
- **title**: Whistleblower tip led NTA to cancel NEET-UG 2026 after full chemistry paper match
- **source** / **pub_time**: Times Now / 2026-05-16T18:00:00+05:30
- **summary**: Four days after the May 3 medical entrance exam, India's National Testing Agency received an email from a whistleblower in Sikar with PDFs that matched 100% of the chemistry questions and part of biology. NTA referred 26–27 paper setters and translators to the CBI; thirteen people have been arrested, including a coaching figure who had publicly championed student justice during the 2024 leak scandal. A re-examination is scheduled for June 21.

### 多 agents 命中

**Count:** 8 candidate(s)

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 33 -->
### Gabbar Is Back (2015) [THE-CAREGIVER, THE-INNOCENT, THE-LOVER, THE-MAGICIAN, THE-RULER, THE-EVERYMAN, THE-HERO, THE-EXPLORER, THE-OUTLAW, THE-CREATOR, THE-SAGE, THE-JESTER] [汇聚标注]
- **tmdb_id**: 337876
- **自动打分**:
  - **quality_candidate**: true
  - **objective_match**: true (surface=true, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 234.6323
  - **persona_agent_count**: 5
  - **source_hits**: surface=12 / event=0 / persona=8
  - **search_unit_kinds**: persona-semantic, surface-fragment-bundle
  - **center_dimensions**: how, result, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=1 + persona_semantic_match=1; composition_agents=5: THE-CAREGIVER,THE-INNOCENT,THE-LOVER,THE-RULER,THE-MAGICIAN
- **相似度**: 0.6323
- **genres** / **language**: Drama, Action / hi
- **overview**: A vigilante network taking out corrupt officials draws the notice of the authorities.
- **跳转**: https://themoviecosmos.com/movie/337876
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[who-2, how-1, how-2, how-3, result-1] · sim=0.5826 · **命中分=5**
  - THE-INNOCENT/su-persona-The-Innocent-p2: fragments=[who-0, why-0, how-1, how-2] · sim=0.6000 · **命中分=4**
  - THE-LOVER/su-persona-The-Lover-p3: fragments=[who-0, why-0, how-1, how-2] · sim=0.6323 · **命中分=4**
  - THE-MAGICIAN/su-persona-The-Magician-p2: fragments=[how-1, how-2, how-3, result-2] · sim=0.5270 · **命中分=4**
  - THE-MAGICIAN/su-persona-The-Magician-p3: fragments=[how-2, result-0, result-2] · sim=0.4847 · **命中分=3**
  - THE-RULER/su-persona-The-Ruler-p1: fragments=[result-0, why-0, how-2, how-3, result-2] · sim=0.4313 · **命中分=5**
  - THE-RULER/su-persona-The-Ruler-p2: fragments=[how-3, why-0, how-1, how-2] · sim=0.6302 · **命中分=4**
  - THE-RULER/su-persona-The-Ruler-p3: fragments=[how-2, why-0, how-1, result-0] · sim=0.4691 · **命中分=4**
  - THE-INNOCENT/su-surface-1: fragments=[who-0, who-1, who-2, who-3, who-4, who-5, where-0, where-1] · sim=0.4931
  - THE-EVERYMAN/su-surface-1: fragments=[who-0, who-1, who-2, who-3, who-4, who-5, where-0, where-1] · sim=0.4966
  - THE-HERO/su-surface-1: fragments=[who-0, who-1, who-2, who-3, who-4, who-5, where-0, where-1] · sim=0.4864
  - THE-CAREGIVER/su-surface-1: fragments=[who-0, who-1, who-2, who-3, who-4, who-5, where-0, where-1] · sim=0.5225
  - THE-EXPLORER/su-surface-1: fragments=[who-0, who-1, who-2, who-3, who-4, who-5, where-0, where-1] · sim=0.5041
  - THE-OUTLAW/su-surface-1: fragments=[who-0, who-1, who-2, who-3, who-4, who-5, where-0, where-1] · sim=0.4842
  - THE-LOVER/su-surface-1: fragments=[who-0, who-1, who-2, who-3, who-4, who-5, where-0, where-1] · sim=0.5308
  - THE-CREATOR/su-surface-1: fragments=[who-0, who-1, who-2, who-3, who-4, who-5, where-0, where-1] · sim=0.4864
  - THE-RULER/su-surface-1: fragments=[who-0, who-1, who-2, who-3, who-4, who-5, where-0, where-1] · sim=0.5032
  - THE-MAGICIAN/su-surface-1: fragments=[who-0, who-1, who-2, who-3, who-4, who-5, where-0, where-1] · sim=0.4986
  - THE-SAGE/su-surface-1: fragments=[who-0, who-1, who-3, who-4, who-5, where-0, where-1, who-2] · sim=0.5270
  - THE-JESTER/su-surface-1: fragments=[who-0, who-1, who-2, who-3, who-4, who-5, where-0, where-1] · sim=0.5126
- **pseudo命中分合计**: 33
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 12 -->
### Test (2006) [THE-CAREGIVER, THE-RULER, THE-SAGE]
- **tmdb_id**: 887697
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 154.5034
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5034
- **genres** / **language**: Animation, Drama / cs
- **overview**: Test
- **跳转**: https://themoviecosmos.com/movie/887697
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p1: fragments=[result-0, how-0, how-1, result-2] · sim=0.4930 · **命中分=4**
  - THE-RULER/su-persona-The-Ruler-p3: fragments=[how-2, why-0, how-1, result-0] · sim=0.4730 · **命中分=4**
  - THE-SAGE/su-persona-The-Sage-p1: fragments=[why-0, how-1, how-2, result-0] · sim=0.5034 · **命中分=4**
- **pseudo命中分合计**: 12
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 11 -->
### Discount (2014) [THE-CAREGIVER, THE-CREATOR, THE-MAGICIAN]
- **tmdb_id**: 313055
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 146.5932
  - **persona_agent_count**: 3
  - **source_hits**: surface=0 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5932
- **genres** / **language**: Comedy / fr
- **overview**: To fight against the introduction of automatic checkouts that threaten their jobs, staff members at Hard Discounts secretly create their own "Alternative Discount" outlet by salvaging products that would otherwise have been wasted.
- **跳转**: https://themoviecosmos.com/movie/313055
- **命中视角/碎片**:
  - THE-CAREGIVER/su-persona-The-Caregiver-p2: fragments=[who-2, how-1, how-2, how-3, result-1] · sim=0.5932 · **命中分=5**
  - THE-CREATOR/su-persona-The-Creator-p2: fragments=[how-1, how-0, why-0] · sim=0.5638 · **命中分=3**
  - THE-MAGICIAN/su-persona-The-Magician-p3: fragments=[how-2, result-0, result-2] · sim=0.4776 · **命中分=3**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 9 -->
### Black Dossier (1955) [THE-OUTLAW, THE-SAGE]
- **tmdb_id**: 199252
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.6116
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, why
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6116
- **genres** / **language**: Crime, Drama / fr
- **overview**: In the 1950s, in a small provincial town, a young inexperienced judge clashes with an influential notable during an investigation into a suspicious death. His perseverance to get to the truth will cause a huge scandal.
- **跳转**: https://themoviecosmos.com/movie/199252
- **命中视角/碎片**:
  - THE-OUTLAW/su-persona-The-Outlaw-p2: fragments=[why-0, how-2, how-3, result-1, result-2] · sim=0.6116 · **命中分=5**
  - THE-SAGE/su-persona-The-Sage-p2: fragments=[how-1, how-2, how-3, result-0] · sim=0.4794 · **命中分=4**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 9 -->
### Le Brio (2017) [THE-EVERYMAN, THE-LOVER]
- **tmdb_id**: 452187
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 128.6388
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6388
- **genres** / **language**: Drama, Comedy / fr
- **overview**: After an incident, a brilliant professor known for his outbursts is forced to mentor the student he wronged for a speech contest.
- **跳转**: https://themoviecosmos.com/movie/452187
- **命中视角/碎片**:
  - THE-EVERYMAN/su-persona-The-Everyman-p2: fragments=[who-5, how-2, how-3, result-0] · sim=0.6388 · **命中分=4**
  - THE-LOVER/su-persona-The-Lover-p1: fragments=[who-5, why-0, how-1, how-2, result-1] · sim=0.5837 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 8 -->
### I Flunked, But... (1930) [THE-HERO, THE-INNOCENT]
- **tmdb_id**: 88269
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.4919
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=3
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4919
- **genres** / **language**: Comedy / ja
- **overview**: After the plans of a group of college students to cheat on their final exams goes awry, they're left to reassess their lives and educations and get back on track.
- **跳转**: https://themoviecosmos.com/movie/88269
- **命中视角/碎片**:
  - THE-HERO/su-persona-The-Hero-p3: fragments=[result-2, result-0] · sim=0.4616 · **命中分=2**
  - THE-INNOCENT/su-persona-The-Innocent-p1: fragments=[result-0, why-0, how-1] · sim=0.4303 · **命中分=3**
  - THE-INNOCENT/su-persona-The-Innocent-p3: fragments=[how-4, result-0, result-2] · sim=0.4919 · **命中分=3**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 7 -->
### The Last Judgment (1961) [THE-INNOCENT, THE-JESTER]
- **tmdb_id**: 58185
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 136.4552
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: how, result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4552
- **genres** / **language**: Comedy / it
- **overview**: In Naples, a voice from the skies announces one morning that the final judgment will be at 6 p.m. on that day. What follows is a series of vignettes depicting various people's reactions (or lack thereof) to the announcement.
- **跳转**: https://themoviecosmos.com/movie/58185
- **命中视角/碎片**:
  - THE-INNOCENT/su-persona-The-Innocent-p3: fragments=[how-4, result-0, result-2] · sim=0.4552 · **命中分=3**
  - THE-JESTER/su-persona-The-Jester-p3: fragments=[result-2, how-0, how-1, how-2] · sim=0.4471 · **命中分=4**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 7 -->
### Attitude Test (2016) [THE-CREATOR, THE-JESTER]
- **tmdb_id**: 427557
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 128.4705
  - **persona_agent_count**: 2
  - **source_hits**: surface=0 / event=0 / persona=2
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: result
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.4705
- **genres** / **language**: Comedy / es
- **overview**: Four high school seniors steal an important college entrance exam and go on vacation to "study," but accidentally lose the exam while partying.
- **跳转**: https://themoviecosmos.com/movie/427557
- **命中视角/碎片**:
  - THE-CREATOR/su-persona-The-Creator-p1: fragments=[result-0, why-0, how-1, result-2] · sim=0.4613 · **命中分=4**
  - THE-JESTER/su-persona-The-Jester-p1: fragments=[result-0, why-0, how-1] · sim=0.4705 · **命中分=3**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 3 candidate(s)

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 5 -->
### The Gracefield Incident (2017) [THE-INNOCENT, THE-MAGICIAN, THE-EXPLORER]
- **tmdb_id**: 327253
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.5914
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=2 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5914
- **genres** / **language**: Horror, Science Fiction, Action, Mystery / en
- **overview**: On August 16, 2013, the Supreme Court mandated the CIA to declassify files that had been kept secret for the past 75 years. Visual records of documented paranormal events were released to the public. The following incident took place in Gracefield, Quebec.
- **跳转**: https://themoviecosmos.com/movie/327253
- **命中视角/碎片**:
  - THE-INNOCENT/su-event-1: fragments=[why-0, how-0, how-1, how-4, result-0, result-1, result-2, how-2, how-3] · sim=0.3945
  - THE-MAGICIAN/su-event-1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0, result-1, result-2] · sim=0.3821
  - THE-EXPLORER/su-persona-The-Explorer-p2: fragments=[who-0, why-0, how-1, how-2, result-1] · sim=0.5914 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 5 -->
### Lie Detector (2011) [THE-EXPLORER]
- **tmdb_id**: 375384
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.6137
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.6137
- **genres** / **language**: Comedy / en
- **overview**: A job interview takes an awkward turn when a lie detector reveals the unfiltered truths and hidden feelings of everyone involved.
- **跳转**: https://themoviecosmos.com/movie/375384
- **命中视角/碎片**:
  - THE-EXPLORER/su-persona-The-Explorer-p2: fragments=[who-0, why-0, how-1, how-2, result-1] · sim=0.6137 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 5 -->
### Por Thozhil (2023) [THE-LOVER]
- **tmdb_id**: 1115239
- **自动打分**:
  - **quality_candidate**: false
  - **objective_match**: false (surface=false, event=false)
  - **persona_semantic_match**: true
  - **convergent_score**: 118.5690
  - **persona_agent_count**: 1
  - **source_hits**: surface=0 / event=0 / persona=1
  - **search_unit_kinds**: persona-semantic
  - **center_dimensions**: who
  - **baseline_overlap**: false
  - **quality_reason**: objective_match=0 (surface/event match expected)
- **相似度**: 0.5690
- **genres** / **language**: Crime, Thriller, Action / ta
- **overview**: Loganathan, a senior cop is asked to mentor Prakash, an academically bright but faint-hearted rookie and this unlikely duo team up to investigate a series of murder cases, and realize all of them are interlinked and that a psychopath serial killer is on the run.
- **跳转**: https://themoviecosmos.com/movie/1115239
- **命中视角/碎片**:
  - THE-LOVER/su-persona-The-Lover-p1: fragments=[who-5, why-0, how-1, how-2, result-1] · sim=0.5690 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

