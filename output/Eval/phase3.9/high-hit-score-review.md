# High Pseudo Hit Score — Unified Review

## Criteria

### Pseudo 命中分（二级审阅键 · 非质量闸）

**High-hit review** lists candidates with **pseudo命中分合计 ≥ 5**
or **pure-neutral** hits (`neutral_hits≥1` and `distinct_agents=0`, ADR-0006 D4).
Inclusion is **not** a quality gate; D1 `quality_candidate` is from retrieve.

For each hit line under **命中视角/碎片**, count entries in `fragments=[...]`
— **each fragment id = 1 point** for that pseudo.

- **Candidate 总分** (`pseudo命中分合计`) = sum of pseudo 命中分 across all hit lines.
- Shown inline per line, e.g. `A2/p1: fragments=[...] · sim=... · **命中分=3**`.

### Per-news layout

- News sections follow `tests/eval_news/batch-manifest.json` order (01–10).
- Each section opens with that run's `reality.md`.
- **多 agents 命中**: `quality_candidate` or ≥2 agents in heading / hit_sources.
- **单 agent 命中**: all other high-hit candidates.
- Within each subsection, sort by **pseudo命中分合计** descending.

### Sources

- **Primary:** `hit_sources` in each run's `retrieve.json` (fragment arrays).
- **LLM judge:** `llm-judge-scores.json` — trust_status=不采信 (screening only; inline judge fields per candidate)
- **Editor fields:** 共振分 / 共振类型 / 打分备注 are placeholders only (not filled by this script).

- **Generation date:** 2026-06-06
- **Total candidates (≥5):** 156
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

**Count:** 9 candidate(s)

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 159 -->
### Survival Family (2017) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-RULER, THE-SAGE, THE-JESTER, THE-MAGICIAN] [优质·多agent]
- **tmdb_id**: 429918
- **quality_candidate**: true
- **neutral_hits**: 10
- **neutral_total**: 12
- **neutral_hit_rate**: 0.8333
- **distinct_agents**: 12
- **优质候选**: true
- **distinct_agents**: 12
- **相似度**: 0.6144
- **genres** / **language**: Comedy, Drama, Adventure / ja
- **overview**: A world wide electrical outage occurs. Everything that requires electricity comes to a stop. Tokyo is nearly ruined. Yoshiyuki Suzuki decides to escape from Tokyo with his family.
- **跳转**: https://themoviecosmos.com/movie/429918
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[result-0, who-1, who-3, why-2, how-2] · sim=0.4477
  - THE-EVERYMAN/n1: fragments=[result-0, how-2, who-1, who-3, why-2] · sim=0.4696
  - THE-HERO/n1: fragments=[result-0, how-2, who-2, why-0, how-1] · sim=0.4875
  - THE-CAREGIVER/n1: fragments=[result-0, who-1, who-3, why-0, how-2] · sim=0.4896
  - THE-EXPLORER/n1: fragments=[how-2, result-0, who-0, who-2, why-2] · sim=0.3948
  - THE-OUTLAW/n1: fragments=[who-0, how-2, why-0, why-1, result-0] · sim=0.4884
  - THE-LOVER/n1: fragments=[result-0, why-2, who-3, how-2, why-0] · sim=0.4409
  - THE-CREATOR/n1: fragments=[how-1, how-2, why-0, who-0, result-0] · sim=0.4260
  - THE-RULER/n1: fragments=[result-0, who-0, how-0, why-0, how-1] · sim=0.4614
  - THE-SAGE/n1: fragments=[result-0, why-0, why-1, why-2, how-0] · sim=0.4978
  - THE-JESTER/n1: fragments=[how-2, result-0, why-2, who-0, how-1] · sim=0.4161
  - THE-EVERYMAN/p1: fragments=[why-0, how-1, how-2, result-0] · sim=0.5942 · **命中分=4**
  - THE-HERO/p1: fragments=[why-0, why-1, why-2, how-1, how-2, result-0] · sim=0.4889 · **命中分=6**
  - THE-CAREGIVER/p1: fragments=[why-0, how-1, how-2, result-0] · sim=0.5192 · **命中分=4**
  - THE-EXPLORER/p1: fragments=[why-0, how-1, how-2, result-0] · sim=0.5398 · **命中分=4**
  - THE-OUTLAW/p1: fragments=[why-0, how-1, result-0] · sim=0.5358 · **命中分=3**
  - THE-LOVER/p1: fragments=[why-0, how-1, result-0] · sim=0.6144 · **命中分=3**
  - THE-CREATOR/p1: fragments=[why-0, how-1, result-0] · sim=0.5608 · **命中分=3**
  - THE-RULER/p1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5003 · **命中分=5**
  - THE-MAGICIAN/p1: fragments=[why-0, why-1, why-2, how-1] · sim=0.5417 · **命中分=4**
  - THE-SAGE/p1: fragments=[why-0, why-2, how-1, how-2, result-0] · sim=0.4620 · **命中分=5**
  - THE-JESTER/p1: fragments=[why-2, why-0, how-1, how-2, result-0] · sim=0.5083 · **命中分=5**
  - THE-INNOCENT/p2: fragments=[why-0, why-1, how-0, how-1, result-0] · sim=0.5196 · **命中分=5**
  - THE-EVERYMAN/p2: fragments=[why-0, why-1, why-2, how-2, result-0] · sim=0.5348 · **命中分=5**
  - THE-HERO/p2: fragments=[why-0, why-2, how-1, how-2, result-0] · sim=0.5530 · **命中分=5**
  - THE-EXPLORER/p2: fragments=[why-1, how-1, how-2, result-0] · sim=0.5612 · **命中分=4**
  - THE-LOVER/p2: fragments=[why-2, how-2, result-0] · sim=0.5449 · **命中分=3**
  - THE-CREATOR/p2: fragments=[why-1, how-2, result-0] · sim=0.5285 · **命中分=3**
  - THE-RULER/p2: fragments=[why-1, why-2, why-0, how-1, how-2, result-0] · sim=0.5498 · **命中分=6**
  - THE-SAGE/p2: fragments=[why-1, how-0, how-1, how-2, result-0] · sim=0.5347 · **命中分=5**
  - THE-JESTER/p2: fragments=[why-0, why-2, how-1, result-0, how-2] · sim=0.5630 · **命中分=5**
  - THE-EVERYMAN/p3: fragments=[why-0, why-2, how-1, how-2, result-0] · sim=0.5923 · **命中分=5**
  - THE-EXPLORER/p3: fragments=[why-0, how-1, how-2, result-0] · sim=0.5548 · **命中分=4**
  - THE-CREATOR/p3: fragments=[why-0, how-2, result-0] · sim=0.4882 · **命中分=3**
  - THE-SAGE/p3: fragments=[why-0, why-2, how-1, how-2, result-0] · sim=0.5772 · **命中分=5**
- **pseudo命中分合计**: 159
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge分歧**: ⚠
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives hinge on electrical outages as a core concrete element (surface anchor), but the news focuses on technical crisis management in a specific region, while the film explores global collapse and personal survival, lacking isomorphic structural skeletons.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 38 -->
### Geostorm (2017) [THE-INNOCENT, THE-HERO, THE-LOVER, THE-EXPLORER, THE-CREATOR, THE-RULER, THE-EVERYMAN]
- **tmdb_id**: 274855
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 7
- **优质候选**: false
- **distinct_agents**: 7
- **相似度**: 0.5708
- **genres** / **language**: Action, Science Fiction, Thriller / en
- **overview**: After an unprecedented series of natural disasters threatened the planet, the world's leaders came together to create an intricate network of satellites to control the global climate and keep everyone safe. But now, something has gone wrong: the system built to protect Earth is attacking it, and it becomes a race against the clock to uncover the real threat before a worldwide geostorm wipes out everything and everyone along with it.
- **跳转**: https://themoviecosmos.com/movie/274855
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, why-2, how-1, how-2, result-0] · sim=0.5546 · **命中分=5**
  - THE-HERO/p1: fragments=[why-0, why-1, why-2, how-1, how-2, result-0] · sim=0.5021 · **命中分=6**
  - THE-LOVER/p1: fragments=[why-0, how-1, result-0] · sim=0.5708 · **命中分=3**
  - THE-EXPLORER/p2: fragments=[why-1, how-1, how-2, result-0] · sim=0.4893 · **命中分=4**
  - THE-CREATOR/p2: fragments=[why-1, how-2, result-0] · sim=0.4973 · **命中分=3**
  - THE-RULER/p2: fragments=[why-1, why-2, why-0, how-1, how-2, result-0] · sim=0.5401 · **命中分=6**
  - THE-EVERYMAN/p3: fragments=[why-0, why-2, how-1, how-2, result-0] · sim=0.5439 · **命中分=5**
  - THE-HERO/p3: fragments=[why-0, why-1, why-2, how-1, how-2, result-0] · sim=0.4896 · **命中分=6**
- **pseudo命中分合计**: 38
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 结构  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge分歧**: ⚠
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor; news focuses on electrical grid failure, while film centers on climate satellite malfunction. Structural themes of system failure exist but are not isomorphic due to different domains and scales.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 26 -->
### Blade Runner: Black Out 2022 (2017) [THE-EVERYMAN, THE-CAREGIVER, THE-MAGICIAN, THE-SAGE, THE-JESTER, THE-RULER]
- **tmdb_id**: 475946
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 6
- **优质候选**: false
- **distinct_agents**: 6
- **相似度**: 0.5683
- **genres** / **language**: Action, Animation, Science Fiction / en
- **overview**: This animated short revolves around the events causing an electrical systems failure on the west coast of the US. According to Blade Runner 2049’s official timeline, this failure leads to cities shutting down, financial and trade markets being thrown into chaos, and food supplies dwindling. There’s no proof as to what caused the blackouts, but Replicants — the bio-engineered robots featured in the original Blade Runner, are blamed.
- **跳转**: https://themoviecosmos.com/movie/475946
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[why-0, how-1, how-2, result-0] · sim=0.5196 · **命中分=4**
  - THE-CAREGIVER/p1: fragments=[why-0, how-1, how-2, result-0] · sim=0.5105 · **命中分=4**
  - THE-MAGICIAN/p2: fragments=[why-0, how-1, how-2, result-0] · sim=0.5683 · **命中分=4**
  - THE-SAGE/p2: fragments=[why-1, how-0, how-1, how-2, result-0] · sim=0.4747 · **命中分=5**
  - THE-JESTER/p2: fragments=[why-0, why-2, how-1, result-0, how-2] · sim=0.5230 · **命中分=5**
  - THE-RULER/p3: fragments=[how-0, how-1, how-2, result-0] · sim=0.5440 · **命中分=4**
- **pseudo命中分合计**: 26
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge分歧**: ⚠
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives share a load-bearing surface anchor of a power blackout central to their plots. However, the news focuses on operational grid management and immediate risk mitigation in a specific region, while the film explores dystopian societal collapse and mystery, so their thematic skeletons are not isomorphic.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 20 -->
### The Real Glory (1939) [THE-OUTLAW, THE-CREATOR, THE-RULER, THE-INNOCENT] [优质·多agent]
- **tmdb_id**: 111750
- **quality_candidate**: true
- **neutral_hits**: 3
- **neutral_total**: 12
- **neutral_hit_rate**: 0.2500
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.4792
- **genres** / **language**: Drama, War / en
- **overview**: Fort Mysang, southern Philippine Islands, under US rule, 1906. A small group of army officers and native troops resist the fierce and treacherous attacks of the ruthless Alisang and his fanatical followers.
- **跳转**: https://themoviecosmos.com/movie/111750
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/n1: fragments=[who-0, how-2, why-0, why-1, result-0] · sim=0.4340
  - THE-CREATOR/n1: fragments=[how-1, how-2, why-0, who-0, result-0] · sim=0.4138
  - THE-RULER/n1: fragments=[result-0, who-0, how-0, why-0, how-1] · sim=0.4209
  - THE-INNOCENT/p3: fragments=[why-0, why-1, why-2, how-2, result-0] · sim=0.4792 · **命中分=5**
- **pseudo命中分合计**: 20
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: Incidental overlap in Philippines setting without load-bearing surface anchor; structural skeletons differ (infrastructure crisis vs. military conflict).

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 16 -->
### Stranded (2021) [THE-MAGICIAN, THE-CAREGIVER, THE-LOVER] [优质·多agent]
- **tmdb_id**: 841793
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 3
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.5545
- **genres** / **language**: Drama / pt
- **overview**: Tensions run high while food runs low as six influencers find themselves stranded on a secluded island after plans for a weekend escape go awry.
- **跳转**: https://themoviecosmos.com/movie/841793
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/n1: fragments=[how-1, why-2, how-2, result-0, who-0] · sim=0.4517
  - THE-MAGICIAN/p1: fragments=[why-0, why-1, why-2, how-1] · sim=0.4877 · **命中分=4**
  - THE-CAREGIVER/p2: fragments=[why-2, how-0, how-1, result-0] · sim=0.5545 · **命中分=4**
  - THE-LOVER/p2: fragments=[why-2, how-2, result-0] · sim=0.5186 · **命中分=3**
- **pseudo命中分合计**: 16
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 结构  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge分歧**: ⚠
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor; the news focuses on power grid crisis and load shedding, while the film centers on island survival with food scarcity. Structural skeleton is not isomorphic: news involves systemic infrastructure failure, film involves interpersonal tensions in isolation. An unrelated news could equally explain the film.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 11 -->
### Contagion of Fear (2023) [THE-HERO, THE-SAGE]
- **tmdb_id**: 1223272
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.4887
- **genres** / **language**: Science Fiction, Thriller / en
- **overview**: A catastrophic train derailment sends the city spiraling into chaos. But the derailment is just the beginning. A biological gas attack sees crash survivors collapsing and dying within minutes. And the sickness is rapidly spreading.
- **跳转**: https://themoviecosmos.com/movie/1223272
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p3: fragments=[why-0, why-1, why-2, how-1, how-2, result-0] · sim=0.4887 · **命中分=6**
  - THE-SAGE/p3: fragments=[why-0, why-2, how-1, how-2, result-0] · sim=0.4622 · **命中分=5**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor; the news focuses on power grid failures and load shedding, while the film involves a train derailment and biological attack. Incidental thematic overlap in crisis escalation, but not structurally isomorphic, and an unrelated news (e.g., a terrorist attack) could explain the film equally.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 10 -->
### From What Is Before (2014) [THE-MAGICIAN, THE-INNOCENT] [优质·多agent]
- **tmdb_id**: 280492
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.4854
- **genres** / **language**: Drama / tl
- **overview**: The Philippines, 1972. Mysterious things are happening in a remote barrio. Wails are heard from the forest, cows are hacked to death, a man is found bleeding to death at the crossroad, and houses are burned. Ferdinand E. Marcos announces Proclamation No. 1081, putting the entire country under Martial Law.
- **跳转**: https://themoviecosmos.com/movie/280492
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/n1: fragments=[how-1, why-2, how-2, result-0, who-0] · sim=0.4142
  - THE-INNOCENT/p3: fragments=[why-0, why-1, why-2, how-2, result-0] · sim=0.4854 · **命中分=5**
- **pseudo命中分合计**: 10
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge分歧**: ⚠
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor: news focuses on power grid failures and blackouts in the Philippines, while film centers on Martial Law and mysterious barrio events with no concrete shared elements like electricity issues. Structural skeletons are not isomorphic: news depicts a technical/energy crisis with emergency load shedding, whereas film portrays political oppression and chaos from Martial Law, lacking a power/fate/theme skeleton alignment.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 9 -->
### Re-Generator (2010) [THE-HERO, THE-MAGICIAN]
- **tmdb_id**: 194834
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5447
- **genres** / **language**: Action, Science Fiction / en
- **overview**: A plane containing a highly classified government project crashes outside of a small town in the US. Realizing the level of danger, the government tries to secretly fix the problem. As tensions grow, the situation gets out of control, and civilians from the town find themselves facing their worst nightmare: a genetically enhanced killing machine that doesn't know how to stop.
- **跳转**: https://themoviecosmos.com/movie/194834
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p2: fragments=[why-0, why-2, how-1, how-2, result-0] · sim=0.5291 · **命中分=5**
  - THE-MAGICIAN/p2: fragments=[why-0, how-1, how-2, result-0] · sim=0.5447 · **命中分=4**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives share a structural skeleton of critical system failure (power grid vs. classified project) escalating into crises with emergency responses, but no load-bearing surface anchor exists as the film's focus on a biological threat has no concrete overlap with news about electrical blackouts.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 8 -->
### 2061 - Un anno eccezionale (2007) [THE-EXPLORER, THE-CAREGIVER]
- **tmdb_id**: 33495
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5445
- **genres** / **language**: Comedy, Science Fiction / it
- **overview**: In a post-apocalyptic future, the Italian peninsula is going through a dark moment due to a terrible energy crisis.
- **跳转**: https://themoviecosmos.com/movie/33495
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p1: fragments=[why-0, how-1, how-2, result-0] · sim=0.5391 · **命中分=4**
  - THE-CAREGIVER/p2: fragments=[why-2, how-0, how-1, result-0] · sim=0.5445 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 双重
- **judge采信**: 不采信 · screening only
- **judge理由**: Both the news and film feature an energy crisis as a load-bearing concrete element (surface anchor), with the news describing a specific power crunch leading to blackout risks and load shedding, and the film portraying a post-apocalyptic future due to a similar crisis. Thematically, the skeleton is isomorphic, as both narratives revolve around the consequences of energy scarcity on society and survival (structural isomorphism).

### 单 agent 命中

**Count:** 6 candidate(s)

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Get Smart, Again! (1989) [THE-SAGE]
- **tmdb_id**: 33787
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4567
- **genres** / **language**: Action, Comedy, Family, TV Movie, Science Fiction / en
- **overview**: KAOS has invented a weather machine so Maxwell Smart and Agent 99 are called back into action to foil this evil plan.
- **跳转**: https://themoviecosmos.com/movie/33787
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-SAGE/p1: fragments=[why-0, why-2, how-1, how-2, result-0] · sim=0.4567 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor: news focuses on power grid failures and emergency load shedding, while film centers on a weather machine plot. Structural skeletons are not isomorphic: news deals with real-world infrastructure crisis management, film is a comedic spy adventure with fantastical elements. Overlap is incidental.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Jet Stream (2013) [THE-JESTER]
- **tmdb_id**: 210219
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5053
- **genres** / **language**: Action, Adventure, Drama, Science Fiction, TV Movie / en
- **overview**: A TV weatherman tries to prove his theory that a series of unexplained catastrophes are the result of powerful winds found in the upper atmosphere coming down to ground level. His claims attract the attention of government scientists, who need his help to control the phenomena before it destroys all life on Earth (Locatetv.com)
- **跳转**: https://themoviecosmos.com/movie/210219
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1: fragments=[why-2, why-0, how-1, how-2, result-0] · sim=0.5053 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor: news focuses on electrical power grid failures and blackouts, while film centers on atmospheric jet stream causing catastrophes; structural themes of crisis response are not isomorphic due to fundamentally different domains (human infrastructure vs. natural phenomena).

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Stormageddon (2015) [THE-RULER]
- **tmdb_id**: 370097
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5302
- **genres** / **language**: Action, Drama, Thriller, Science Fiction / en
- **overview**: What happens when you ask the most powerful computer program, run by the most powerful computers, to follow, listen and predict human behavior? The program learns, becomes sentient and begins to behave like a human. When a master computer program, Echelon, takes over America's entire online system, our country is threatened to be brought to its knees. Hacking into DARPA, Echelon gains the ability to manipulate the weather, create earthquakes, and cause a level of destruction unlike anything the country could ever imagine. But how do you stop a computer program when it has control over any and every defense you have?
- **跳转**: https://themoviecosmos.com/movie/370097
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5302 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The news focuses on power grid failures due to plant outages and demand, with no concrete element matching the film's AI-driven disasters. The themes of infrastructure vulnerability vs. malicious AI lack structural isomorphism, making any overlap incidental.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### The Current War (2018) [THE-MAGICIAN]
- **tmdb_id**: 418879
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4912
- **genres** / **language**: Drama, History / en
- **overview**: Electricity titans Thomas Edison and George Westinghouse compete to create a sustainable system and market it to the American people.
- **跳转**: https://themoviecosmos.com/movie/418879
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p3: fragments=[why-2, how-0, how-1, how-2, result-0] · sim=0.4912 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge分歧**: ⚠
- **judge采信**: 不采信 · screening only
- **judge理由**: The news describes a modern operational power crisis in the Philippines, while the film is about historical electricity competition in the U.S. The shared theme of electricity is incidental and not load-bearing, and the structural skeletons are not isomorphic; any unrelated news about electricity could explain the film equally.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Trapped (2017) [THE-MAGICIAN]
- **tmdb_id**: 431892
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4764
- **genres** / **language**: Thriller, Drama / hi
- **overview**: A man gets stuck in an empty high rise without food, water or electricity.
- **跳转**: https://themoviecosmos.com/movie/431892
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p3: fragments=[why-2, how-0, how-1, how-2, result-0] · sim=0.4764 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The shared element of electricity loss is incidental; the film's focus on personal trapping is not isomorphic to the news's systemic power crunch, and an unrelated news about trapping could explain the film equally.

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Kaappaan (2019) [THE-INNOCENT]
- **tmdb_id**: 533885
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4972
- **genres** / **language**: Action, Thriller / ta
- **overview**: A Special Protection Group officer has to identify the threat to the prime minister, who he is protecting, and also the nation.
- **跳转**: https://themoviecosmos.com/movie/533885
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, why-2, how-1, how-2, result-0] · sim=0.4972 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No shared concrete elements; film involves political threats, news involves power infrastructure failure; structural skeletons not isomorphic under rubric.

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

**Count:** 12 candidate(s)

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 69 -->
### The Plan (2018) [THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-OUTLAW, THE-LOVER, THE-RULER, THE-CREATOR, THE-SAGE, THE-INNOCENT] [优质·多agent]
- **tmdb_id**: 619090
- **quality_candidate**: true
- **neutral_hits**: 6
- **neutral_total**: 12
- **neutral_hit_rate**: 0.5000
- **distinct_agents**: 6
- **优质候选**: true
- **distinct_agents**: 6
- **相似度**: 0.5661
- **genres** / **language**: Comedy, Drama / es
- **overview**: Three friends who have been fired from the company where they worked and are demoralized because of their unemployment status. In these circumstances, they meet to undertake the plan that mentions the title but there is a problem: the car with which they would travel has broken down and the crane must wait.
- **跳转**: https://themoviecosmos.com/movie/619090
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/n1: fragments=[result-1, who-2, result-3, how-1, who-0] · sim=0.4586
  - THE-HERO/n1: fragments=[who-2, result-0, result-1, how-1, why-1] · sim=0.4590
  - THE-CAREGIVER/n1: fragments=[result-0, who-2, result-3, how-1, how-0] · sim=0.4314
  - THE-OUTLAW/n1: fragments=[who-2, result-0, why-1, who-0, how-1] · sim=0.4309
  - THE-LOVER/n1: fragments=[who-2, result-0, result-3, how-1, how-2] · sim=0.4093
  - THE-RULER/n1: fragments=[result-0, result-1, how-0, why-0, how-1] · sim=0.4374
  - THE-CREATOR/p1: fragments=[why-0, how-0, how-1, how-2, result-1, result-3] · sim=0.4490 · **命中分=6**
  - THE-EVERYMAN/p2: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5608 · **命中分=6**
  - THE-OUTLAW/p2: fragments=[result-0, why-0, how-0, how-1, how-2, result-2] · sim=0.5144 · **命中分=6**
  - THE-SAGE/p2: fragments=[why-1, how-2, result-1, result-3] · sim=0.5259 · **命中分=4**
  - THE-INNOCENT/p3: fragments=[how-0, result-1, why-0, result-3, result-0] · sim=0.4980 · **命中分=5**
  - THE-HERO/p3: fragments=[why-1, how-0, how-1, how-2, result-1, result-2] · sim=0.5134 · **命中分=6**
  - THE-OUTLAW/p3: fragments=[how-0, why-1, result-1, how-1, result-1, how-2] · sim=0.5661 · **命中分=6**
- **pseudo命中分合计**: 69
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge分歧**: ⚠
- **judge采信**: 不采信 · screening only
- **judge理由**: Job loss is shared but incidental; the film's personal demoralization and unrelated obstacle (broken car) do not align with the news's AI-driven corporate restructuring, and no structural isomorphism exists.

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 52 -->
### Cart (2014) [THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-OUTLAW, THE-LOVER] [优质·多agent]
- **tmdb_id**: 287647
- **quality_candidate**: true
- **neutral_hits**: 5
- **neutral_total**: 12
- **neutral_hit_rate**: 0.4167
- **distinct_agents**: 4
- **优质候选**: true
- **distinct_agents**: 4
- **相似度**: 0.6182
- **genres** / **language**: Drama / ko
- **overview**: In response to a sudden dismissal of staff, workers at a big retail store begin a protest against their employer's oppressive labor policies.
- **跳转**: https://themoviecosmos.com/movie/287647
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/n1: fragments=[result-1, who-2, result-3, how-1, who-0] · sim=0.4530
  - THE-HERO/n1: fragments=[who-2, result-0, result-1, how-1, why-1] · sim=0.4867
  - THE-CAREGIVER/n1: fragments=[result-0, who-2, result-3, how-1, how-0] · sim=0.4484
  - THE-OUTLAW/n1: fragments=[who-2, result-0, why-1, who-0, how-1] · sim=0.4756
  - THE-LOVER/n1: fragments=[who-2, result-0, result-3, how-1, how-2] · sim=0.4559
  - THE-EVERYMAN/p1: fragments=[why-0, how-0, result-0, result-1, result-3] · sim=0.4450 · **命中分=5**
  - THE-EVERYMAN/p2: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.6182 · **命中分=6**
  - THE-HERO/p2: fragments=[why-0, how-0, how-1, result-0, result-1, result-3] · sim=0.5426 · **命中分=6**
  - THE-CAREGIVER/p3: fragments=[how-0, result-0, result-3, why-1] · sim=0.4800 · **命中分=4**
  - THE-OUTLAW/p3: fragments=[how-0, why-1, result-1, how-1, result-1, how-2] · sim=0.5850 · **命中分=6**
- **pseudo命中分合计**: 52
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 双重
- **judge分歧**: ⚠
- **judge采信**: 不采信 · screening only
- **judge理由**: Both involve layoffs as a central event, with structural isomorphism in themes of power imbalance and fate of workers, though news emphasizes corporate restructuring for AI while film focuses on labor protest.

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 50 -->
### Bounty Killer (2013) [THE-INNOCENT, THE-HERO, THE-OUTLAW, THE-SAGE, THE-CAREGIVER, THE-EXPLORER, THE-MAGICIAN, THE-JESTER]
- **tmdb_id**: 209504
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 8
- **优质候选**: false
- **distinct_agents**: 8
- **相似度**: 0.5749
- **genres** / **language**: Action, Science Fiction / en
- **overview**: It’s been 20 years since the corporations took over the world’s governments. Their thirst for power and profits led to the Corporate Wars, a fierce global battle that laid waste to society as we know it. Born from the ash, the Council of Nine rose as a new law and order for this dark age. To avenge the corporations’ reckless destruction, the Council issues death warrants for all white collar criminals. Their hunters—the bounty killer. From amateur savage to graceful assassin, the bounty killers now compete for body count, fame and a fat stack of cash. They’re ending the plague of corporate greed and providing the survivors of the apocalypse with retribution. These are the new heroes. This is the age of the BOUNTY KILLER.
- **跳转**: https://themoviecosmos.com/movie/209504
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-1, how-0, result-0, result-3, why-0] · sim=0.5219 · **命中分=5**
  - THE-HERO/p1: fragments=[why-1, how-0, how-1, how-2, result-0, result-1, result-3] · sim=0.5657 · **命中分=7**
  - THE-OUTLAW/p1: fragments=[why-1, how-0, result-1, how-1] · sim=0.5117 · **命中分=4**
  - THE-SAGE/p1: fragments=[why-0, how-0, how-1, result-0] · sim=0.5252 · **命中分=4**
  - THE-HERO/p2: fragments=[why-0, how-0, how-1, result-0, result-1, result-3] · sim=0.5198 · **命中分=6**
  - THE-CAREGIVER/p2: fragments=[why-1, how-2, result-1, result-2] · sim=0.5093 · **命中分=4**
  - THE-EXPLORER/p2: fragments=[why-1, how-0, result-0, how-1, result-3, how-2] · sim=0.4642 · **命中分=6**
  - THE-MAGICIAN/p2: fragments=[why-1, how-0, how-1, how-2, result-1, result-3] · sim=0.5483 · **命中分=6**
  - THE-JESTER/p3: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2] · sim=0.5749 · **命中分=8**
- **pseudo命中分合计**: 50
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge分歧**: ⚠
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor or structural isomorphism; the news involves corporate job cuts for AI adaptation, while the film depicts a post-apocalyptic world with bounty killers targeting corporate criminals; any connection is incidental, as an unrelated news about corporate changes could equally explain the film.

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 32 -->
### The Seventh Company Outdoors (1977) [THE-EXPLORER, THE-CREATOR, THE-SAGE, THE-INNOCENT] [优质·多agent]
- **tmdb_id**: 56589
- **quality_candidate**: true
- **neutral_hits**: 3
- **neutral_total**: 12
- **neutral_hit_rate**: 0.2500
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.4964
- **genres** / **language**: Comedy / fr
- **overview**: The third part of Seventh Company adventures.
- **跳转**: https://themoviecosmos.com/movie/56589
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/n1: fragments=[why-0, how-0, who-0, result-0, how-2] · sim=0.4876
  - THE-CREATOR/n1: fragments=[why-0, how-0, how-2, result-1, result-0] · sim=0.4964
  - THE-SAGE/n1: fragments=[why-0, how-0, result-0, who-1, why-1] · sim=0.4639
  - THE-INNOCENT/p2: fragments=[how-0, how-1, how-2, why-0, result-0, result-3] · sim=0.4913 · **命中分=6**
  - THE-EXPLORER/p2: fragments=[why-1, how-0, result-0, how-1, result-3, how-2] · sim=0.4667 · **命中分=6**
  - THE-EXPLORER/p3: fragments=[how-2, how-0, result-1, result-0, how-1] · sim=0.4666 · **命中分=5**
- **pseudo命中分合计**: 32
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The news is about corporate layoffs and AI restructuring, while the film is a military adventure comedy; the shared word 'company' is incidental and not load-bearing, with no structural isomorphism in themes or power dynamics.

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 30 -->
### Corporate Animals (2019) [THE-LOVER, THE-CAREGIVER, THE-JESTER, THE-HERO]
- **tmdb_id**: 530076
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.5725
- **genres** / **language**: Horror, Comedy / en
- **overview**: Disaster strikes when the egotistical CEO of an edible cutlery company leads her long-suffering staff on a corporate team-building trip in New Mexico. Trapped underground, this mismatched and disgruntled group must pull together to survive.
- **跳转**: https://themoviecosmos.com/movie/530076
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1: fragments=[why-1, how-1, how-2, result-0] · sim=0.5010 · **命中分=4**
  - THE-CAREGIVER/p2: fragments=[why-1, how-2, result-1, result-2] · sim=0.5243 · **命中分=4**
  - THE-JESTER/p2: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2] · sim=0.5454 · **命中分=8**
  - THE-HERO/p3: fragments=[why-1, how-0, how-1, how-2, result-1, result-2] · sim=0.5596 · **命中分=6**
  - THE-JESTER/p3: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2] · sim=0.5725 · **命中分=8**
- **pseudo命中分合计**: 30
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge分歧**: ⚠
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor (generic corporate elements are incidental, not essential to both narratives), and structural skeletons are not isomorphic (news involves economic restructuring for AI, film focuses on physical survival during a team-building disaster; themes and outcomes diverge significantly).

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 27 -->
### Qwerty (2011) [THE-EXPLORER, THE-CREATOR, THE-SAGE, THE-JESTER, THE-HERO] [优质·多agent]
- **tmdb_id**: 750145
- **quality_candidate**: true
- **neutral_hits**: 4
- **neutral_total**: 12
- **neutral_hit_rate**: 0.3333
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.4902
- **genres** / **language**: Comedy / en
- **overview**: Conglomerated Assets, a brokerage firm is sinking fast as its CEO checks out and leaves the company to his inept film school drop out son. Enter Quincy, Waverly, Erica, Rudy, Tina and Yasmine. Team QWERTY--six sexy secretaries that must save the day.
- **跳转**: https://themoviecosmos.com/movie/750145
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/n1: fragments=[why-0, how-0, who-0, result-0, how-2] · sim=0.4680
  - THE-CREATOR/n1: fragments=[why-0, how-0, how-2, result-1, result-0] · sim=0.4685
  - THE-SAGE/n1: fragments=[why-0, how-0, result-0, who-1, why-1] · sim=0.4752
  - THE-JESTER/n1: fragments=[why-1, how-0, who-1, result-0, why-0] · sim=0.4584
  - THE-HERO/p1: fragments=[why-1, how-0, how-1, how-2, result-0, result-1, result-3] · sim=0.4902 · **命中分=7**
- **pseudo命中分合计**: 27
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface elements: news details specific layoffs and AI restructuring, while film focuses on secretaries saving a sinking firm from inept leadership. No structural isomorphism: news emphasizes top-down corporate change for efficiency, film depicts bottom-up rescue by underdogs.

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 26 -->
### The Factory (2018) [THE-CREATOR, THE-RULER, THE-INNOCENT, THE-EXPLORER]
- **tmdb_id**: 513349
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.5492
- **genres** / **language**: Thriller, Drama, Crime / ru
- **overview**: When a factory is bound to close, a group of workers decides to take action against the owner.
- **跳转**: https://themoviecosmos.com/movie/513349
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p2: fragments=[how-0, how-1, why-0, result-1, result-3] · sim=0.5371 · **命中分=5**
  - THE-RULER/p2: fragments=[how-2, why-0, why-1, result-2, how-1] · sim=0.4608 · **命中分=5**
  - THE-INNOCENT/p3: fragments=[how-0, result-1, why-0, result-3, result-0] · sim=0.5122 · **命中分=5**
  - THE-EXPLORER/p3: fragments=[how-2, how-0, result-1, result-0, how-1] · sim=0.5492 · **命中分=5**
  - THE-RULER/p3: fragments=[how-0, result-0, result-1, how-1, result-2, result-3] · sim=0.5262 · **命中分=6**
- **pseudo命中分合计**: 26
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge分歧**: ⚠
- **judge采信**: 不采信 · screening only
- **judge理由**: Both involve workers and job loss as a concrete surface element, but news focuses on corporate restructuring without worker resistance, while film centers on active opposition, making structural skeletons not isomorphic.

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 20 -->
### Mirreyes contra Godínez 2: El retiro (2022) [THE-INNOCENT, THE-OUTLAW, THE-RULER, THE-SAGE]
- **tmdb_id**: 1002695
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.5234
- **genres** / **language**: Comedy / es
- **overview**: A divided team heads to a corporate retreat after receiving an enticing proposal. During their time away, they must overcome their differences and find a way to reunite.
- **跳转**: https://themoviecosmos.com/movie/1002695
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-1, how-0, result-0, result-3, why-0] · sim=0.4928 · **命中分=5**
  - THE-OUTLAW/p2: fragments=[result-0, why-0, how-0, how-1, how-2, result-2] · sim=0.5234 · **命中分=6**
  - THE-RULER/p2: fragments=[how-2, why-0, why-1, result-2, how-1] · sim=0.5041 · **命中分=5**
  - THE-SAGE/p2: fragments=[why-1, how-2, result-1, result-3] · sim=0.4977 · **命中分=4**
- **pseudo命中分合计**: 20
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor (only incidental corporate setting overlap); no structural isomorphism (news themes of AI-driven restructuring and layoffs differ from film themes of team reconciliation during a retreat).

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 16 -->
### Winner Takes the Cake (2025) [THE-RULER, THE-EVERYMAN, THE-CREATOR] [优质·多agent]
- **tmdb_id**: 1233620
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.4636
- **genres** / **language**: Comedy / es
- **overview**: Sofía quits her job after confronting her misogynistic boss. Determined, she starts her own company to rival her former employer, igniting a David vs. Goliath showdown in the business world.
- **跳转**: https://themoviecosmos.com/movie/1233620
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/n1: fragments=[result-0, result-1, how-0, why-0, how-1] · sim=0.4499
  - THE-EVERYMAN/p1: fragments=[why-0, how-0, result-0, result-1, result-3] · sim=0.4513 · **命中分=5**
  - THE-CREATOR/p1: fragments=[why-0, how-0, how-1, how-2, result-1, result-3] · sim=0.4636 · **命中分=6**
- **pseudo命中分合计**: 16
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor (news focuses on AI-driven corporate layoffs; film centers on personal quitting and rivalry), and skeletons are not isomorphic (corporate restructuring vs. David vs. Goliath personal empowerment). Incidental word overlap on job-related themes without shared concrete elements.

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 12 -->
### Johnny Keep Walking! (2023) [THE-EXPLORER, THE-RULER]
- **tmdb_id**: 1173076
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5199
- **genres** / **language**: Drama, Comedy / zh
- **overview**: A simple technician at a rural factory is mistakenly promoted to a high-level managerial position at corporate headquarters due to a series of clerical errors and a bribery scheme gone wrong.
- **跳转**: https://themoviecosmos.com/movie/1173076
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p1: fragments=[why-0, how-0, result-0, result-1, result-3] · sim=0.5104 · **命中分=5**
  - THE-RULER/p1: fragments=[how-0, why-0, result-0, result-1, result-2, result-3, why-1] · sim=0.5199 · **命中分=7**
- **pseudo命中分合计**: 12
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: News focuses on corporate layoffs and AI-driven restructuring for reinvention, while film depicts a mistaken promotion due to clerical errors and bribery. No load-bearing surface elements (e.g., AI, specific job cuts) are shared, and the structural themes are not isomorphic: news involves intentional strategic change affecting employee fate negatively, whereas film involves accidental positive change from incompetence.

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 10 -->
### Another World (2022) [THE-MAGICIAN, THE-RULER]
- **tmdb_id**: 664506
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5487
- **genres** / **language**: Drama / fr
- **overview**: An executive manager, his wife and his family, at the point when his professional choices are about to overturn all their lives. Philippe Lemesle and his wife are separating, their love irretrievably damaged by pressures of work. A successful executive in industrial conglomerate, Philippe no longer knows how to respond to the contradictory demands of his bosses. Yesterday they wanted a manager, today an enforcer. Now he must decide what his life really means.
- **跳转**: https://themoviecosmos.com/movie/664506
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1: fragments=[why-0, how-0, how-1, result-0] · sim=0.5487 · **命中分=4**
  - THE-RULER/p3: fragments=[how-0, result-0, result-1, how-1, result-2, result-3] · sim=0.4853 · **命中分=6**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: Incidental overlap in corporate executive roles, but no load-bearing shared concrete elements (film does not involve layoffs or AI restructuring) and structural skeletons are not isomorphic (news focuses on company reinvention, film on personal crisis); many unrelated news stories could equally explain the film.

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 10 -->
### The Conference (2023) [THE-LOVER, THE-EVERYMAN]
- **tmdb_id**: 1161048
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5481
- **genres** / **language**: Horror, Comedy / sv
- **overview**: A ragtag group of public sector employees battle not only their own discord but also a bloodthirsty killer during a seemingly innocuous retreat.
- **跳转**: https://themoviecosmos.com/movie/1161048
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1: fragments=[why-1, how-1, how-2, result-0] · sim=0.4870 · **命中分=4**
  - THE-EVERYMAN/p3: fragments=[why-1, how-0, how-1, how-2, result-1, result-3] · sim=0.5481 · **命中分=6**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor: shared 'employees' element is incidental, with news focusing on layoffs/AI and film on a killer during a retreat. Structural skeletons are not isomorphic; corporate restructuring themes do not map to thriller survival dynamics.

### 单 agent 命中

**Count:** 5 candidate(s)

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 8 -->
### Gintama: The Movie (2010) [THE-JESTER]
- **tmdb_id**: 71172
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5115
- **genres** / **language**: Action, Science Fiction, Animation / ja
- **overview**: Odd Jobs Gin has taken on a lot of odd work in the past, and when you're a Jack of All Trades agency based in a feudal Japan that's been conquered and colonized by aliens, the term "Odd Jobs" means REALLY ODD jobs. But when some more than slightly suspicious secrets from the shadows of Gintoki Sakata's somewhat shady former samurai past and a new pair of odd jobs collide, the action is bound to get so wild and demented that only a feature film will do it justice!
- **跳转**: https://themoviecosmos.com/movie/71172
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1: fragments=[why-1, how-0, how-1, how-2, result-0, result-1, result-2, result-3] · sim=0.5115 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor (layoffs/corporate restructuring vs. samurai/comedy in alien-occupied Japan) and no structural isomorphism (corporate AI-driven change vs. past secrets/action in historical sci-fi); unrelated news could equally explain the film.

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 8 -->
### Redd Inc. (2012) [THE-JESTER]
- **tmdb_id**: 133463
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5228
- **genres** / **language**: Thriller, Horror, Comedy / en
- **overview**: Six captive office workers are literally chained to their desks by a demented, escaped serial killer; former regional manager Thomas Reddmann. He assigns his 'human resources' the impossible task of proving his innocence or suffering gruesome consequences.
- **跳转**: https://themoviecosmos.com/movie/133463
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p2: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-1, result-2] · sim=0.5228 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The surface element of office workers in corporate settings is incidental and not load-bearing, as the news focuses on economic restructuring and AI-driven layoffs, while the film centers on criminal captivity and forced labor. Structural themes of power and fate are not isomorphic; an unrelated news about layoffs would explain the film equally poorly, lacking core resonance.

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 6 -->
### Crazy People (1990) [THE-EVERYMAN]
- **tmdb_id**: 16814
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5577
- **genres** / **language**: Comedy, Romance / en
- **overview**: A bitter ad executive, who has reached his breaking point, finds himself in a mental institution, where his career actually begins to thrive with the help of the hospital's patients.
- **跳转**: https://themoviecosmos.com/movie/16814
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p3: fragments=[why-1, how-0, how-1, how-2, result-1, result-3] · sim=0.5577 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor (generic executive role) and skeleton not isomorphic (news: corporate AI-driven layoffs; film: personal mental health crisis leading to career reinvention).

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 6 -->
### The Floorwalker (1916) [THE-MAGICIAN]
- **tmdb_id**: 53416
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5198
- **genres** / **language**: Comedy / en
- **overview**: An impecunious customer creates chaos in a department store while the manager and his assistant plot to steal the money kept in the establishment's safe.
- **跳转**: https://themoviecosmos.com/movie/53416
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p2: fragments=[why-1, how-0, how-1, how-2, result-1, result-3] · sim=0.5198 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor or structural isomorphism; news focuses on corporate AI-driven job cuts, while film is a silent comedy about store theft and chaos, with only incidental thematic overlap.

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 5 -->
### At War (2018) [THE-CREATOR]
- **tmdb_id**: 485162
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5345
- **genres** / **language**: Drama / fr
- **overview**: After promising 1100 employees that they would protect their jobs, the managers of a factory decide to suddenly close up shop. Laurent takes the lead in a fight against this decision.
- **跳转**: https://themoviecosmos.com/movie/485162
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p2: fragments=[how-0, how-1, why-0, result-1, result-3] · sim=0.5345 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge采信**: 不采信 · screening only
- **judge理由**: Both involve mass layoffs as a load-bearing concrete element, but the film's skeleton includes broken promises and worker resistance absent in the news, lacking structural isomorphism.

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
<!-- pseudo命中分合计: 58 -->
### Lone Star (1952) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-RULER, THE-SAGE, THE-JESTER, THE-CREATOR] [优质·多agent]
- **tmdb_id**: 37593
- **quality_candidate**: true
- **neutral_hits**: 10
- **neutral_total**: 12
- **neutral_hit_rate**: 0.8333
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5461
- **genres** / **language**: Western / en
- **overview**: Cattle baron Devereaux Burke is enlisted by an aging Andrew Jackson to dissuade Sam Houston from establishing Texas as a republic. Burke must fight state senator Thomas Craden, in the process winning the heart of Craden's newspaper-editor girlfriend Martha Ronda.
- **跳转**: https://themoviecosmos.com/movie/37593
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[result-1, who-1, result-2, who-2, why-0] · sim=0.4756
  - THE-EVERYMAN/n1: fragments=[how-0, result-1, why-1, result-0, who-0] · sim=0.4753
  - THE-HERO/n1: fragments=[result-0, who-0, how-0, why-0, result-1] · sim=0.5090
  - THE-CAREGIVER/n1: fragments=[result-1, who-1, result-2, how-0, why-0] · sim=0.4850
  - THE-EXPLORER/n1: fragments=[result-0, result-1, how-0, why-0, who-0] · sim=0.5011
  - THE-OUTLAW/n1: fragments=[who-0, how-0, why-0, result-0, result-1] · sim=0.5043
  - THE-LOVER/n1: fragments=[who-0, who-1, result-1, how-0, why-0] · sim=0.4843
  - THE-RULER/n1: fragments=[result-0, who-0, how-0, why-0, result-1] · sim=0.5033
  - THE-SAGE/n1: fragments=[result-0, result-1, how-0, why-0, why-1] · sim=0.4947
  - THE-JESTER/n1: fragments=[result-1, who-0, how-0, result-0, who-1] · sim=0.4878
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, result-1] · sim=0.5461 · **命中分=3**
  - THE-CREATOR/p1: fragments=[how-0, why-0, why-1, result-0, result-1] · sim=0.5146 · **命中分=5**
- **pseudo命中分合计**: 58
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge分歧**: ⚠
- **judge采信**: 不采信 · screening only
- **judge理由**: Incidental overlap in Texas political settings; no load-bearing concrete surface element or structural isomorphism between modern Senate runoff and historical independence plot.

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 34 -->
### Swing Vote (2008) [THE-EVERYMAN, THE-OUTLAW, THE-RULER, THE-SAGE, THE-INNOCENT, THE-HERO, THE-LOVER, THE-MAGICIAN]
- **tmdb_id**: 10187
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 8
- **优质候选**: false
- **distinct_agents**: 8
- **相似度**: 0.5778
- **genres** / **language**: Comedy, Drama / en
- **overview**: In a remarkable turn of events, the result of the presidential election comes down to one man's vote.
- **跳转**: https://themoviecosmos.com/movie/10187
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[how-0, result-1, why-0, why-1, result-2] · sim=0.4920 · **命中分=5**
  - THE-OUTLAW/p2: fragments=[why-0, how-0, result-1] · sim=0.5678 · **命中分=3**
  - THE-RULER/p2: fragments=[why-0, how-0, result-0, result-2] · sim=0.5778 · **命中分=4**
  - THE-SAGE/p2: fragments=[result-0, how-0, result-1, result-2] · sim=0.4864 · **命中分=4**
  - THE-INNOCENT/p3: fragments=[why-0, result-0, result-1, result-2] · sim=0.5243 · **命中分=4**
  - THE-HERO/p3: fragments=[why-0, why-1, result-0, result-1, result-2] · sim=0.5319 · **命中分=5**
  - THE-LOVER/p3: fragments=[why-0, why-1, how-0, result-0, result-2] · sim=0.5247 · **命中分=5**
  - THE-MAGICIAN/p3: fragments=[why-0, how-0, result-0, result-2] · sim=0.5370 · **命中分=4**
- **pseudo命中分合计**: 34
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: Both involve elections, but there is no load-bearing concrete surface anchor (news is a Senate runoff with endorsements and vote percentages; film is a presidential election decided by one vote). The structural skeletons are not isomorphic—news focuses on political dynamics and endorsements, while film emphasizes individual fate and a unique voting scenario. An unrelated political news could equally explain the film, so incidental overlap only.

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 33 -->
### Gli onorevoli (1963) [THE-EVERYMAN, THE-CREATOR, THE-RULER, THE-HERO, THE-SAGE, THE-INNOCENT]
- **tmdb_id**: 64946
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 6
- **优质候选**: false
- **distinct_agents**: 6
- **相似度**: 0.6195
- **genres** / **language**: Comedy / it
- **overview**: Some political candidates are determined to win the electors' preference during an election campaign in Italy.
- **跳转**: https://themoviecosmos.com/movie/64946
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[how-0, result-1, why-0, why-1, result-2] · sim=0.5477 · **命中分=5**
  - THE-CREATOR/p1: fragments=[how-0, why-0, why-1, result-0, result-1] · sim=0.5271 · **命中分=5**
  - THE-RULER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5346 · **命中分=4**
  - THE-HERO/p2: fragments=[why-0, how-0, result-0, result-1, why-1, result-2] · sim=0.6195 · **命中分=6**
  - THE-SAGE/p2: fragments=[result-0, how-0, result-1, result-2] · sim=0.5375 · **命中分=4**
  - THE-INNOCENT/p3: fragments=[why-0, result-0, result-1, result-2] · sim=0.4769 · **命中分=4**
  - THE-HERO/p3: fragments=[why-0, why-1, result-0, result-1, result-2] · sim=0.5869 · **命中分=5**
- **pseudo命中分合计**: 33
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The shared theme of political elections is incidental and not load-bearing; the news details a specific U.S. runoff with endorsements and incumbent defeat, while the film depicts a generic Italian campaign without structural isomorphism in power or fate skeletons.

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 27 -->
### The Independent (2022) [THE-RULER, THE-SAGE, THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CREATOR]
- **tmdb_id**: 878183
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 6
- **优质候选**: false
- **distinct_agents**: 6
- **相似度**: 0.6226
- **genres** / **language**: Thriller, Mystery, Crime / en
- **overview**: It's the final weeks of the most consequential presidential election in history. America is poised to elect either its first female president or its first viable independent candidate. Reporting history as it's made, an idealistic young journalist teams up with her idol, legendary journalist Nick Booker, to uncover a conspiracy that places the fate of the election, and the country, in their hands.
- **跳转**: https://themoviecosmos.com/movie/878183
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5148 · **命中分=4**
  - THE-SAGE/p1: fragments=[how-0, why-0, why-1, result-1] · sim=0.5152 · **命中分=4**
  - THE-INNOCENT/p2: fragments=[why-1, why-0, result-0, result-1, result-2] · sim=0.5310 · **命中分=5**
  - THE-EVERYMAN/p2: fragments=[result-1, how-0, why-1, why-0, result-2] · sim=0.6001 · **命中分=5**
  - THE-HERO/p2: fragments=[why-0, how-0, result-0, result-1, why-1, result-2] · sim=0.6226 · **命中分=6**
  - THE-CREATOR/p2: fragments=[how-0, result-0, result-2] · sim=0.5632 · **命中分=3**
- **pseudo命中分合计**: 27
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: News is about a specific Texas Senate runoff with endorsement and incumbent loss; film is a fictional presidential election thriller with a conspiracy plot. Shared election theme is broad and incidental, with no load-bearing surface anchors or structural isomorphism.

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 24 -->
### Game Change (2012) [THE-INNOCENT, THE-CAREGIVER, THE-OUTLAW, THE-LOVER, THE-EXPLORER] [优质·多agent]
- **tmdb_id**: 91010
- **quality_candidate**: true
- **neutral_hits**: 4
- **neutral_total**: 12
- **neutral_hit_rate**: 0.3333
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5734
- **genres** / **language**: TV Movie, Drama, Comedy, History / en
- **overview**: During the Republican run of the 2008 Presidential election, candidate John McCain picks a relative unknown, Alaskan governor Sarah Palin, to be his running mate.  As the campaign kicks into high gear, her lack of experience, in both political and media savvy, becomes a drain upon McCain and his strategists.
- **跳转**: https://themoviecosmos.com/movie/91010
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[result-1, who-1, result-2, who-2, why-0] · sim=0.4750
  - THE-CAREGIVER/n1: fragments=[result-1, who-1, result-2, how-0, why-0] · sim=0.4575
  - THE-OUTLAW/n1: fragments=[who-0, how-0, why-0, result-0, result-1] · sim=0.4719
  - THE-LOVER/n1: fragments=[who-0, who-1, result-1, how-0, why-0] · sim=0.4646
  - THE-EXPLORER/p2: fragments=[why-1, how-0, result-1, result-0] · sim=0.5734 · **命中分=4**
- **pseudo命中分合计**: 24
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchors or structural skeleton isomorphism; only incidental overlap in broad political themes, with distinct contexts (Senate primary vs. presidential campaign) and no concrete shared elements.

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 22 -->
### Machete (2010) [THE-EXPLORER, THE-JESTER, THE-CAREGIVER, THE-INNOCENT] [优质·多agent]
- **tmdb_id**: 23631
- **quality_candidate**: true
- **neutral_hits**: 2
- **neutral_total**: 12
- **neutral_hit_rate**: 0.1667
- **distinct_agents**: 3
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.5566
- **genres** / **language**: Action, Comedy, Thriller / en
- **overview**: After being set-up and betrayed by the man who hired him to assassinate a Texas Senator, an ex-Federale launches a brutal rampage of revenge against his former boss.
- **跳转**: https://themoviecosmos.com/movie/23631
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/n1: fragments=[result-0, result-1, how-0, why-0, who-0] · sim=0.4371
  - THE-JESTER/n1: fragments=[result-1, who-0, how-0, result-0, who-1] · sim=0.4591
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, result-1] · sim=0.5495 · **命中分=3**
  - THE-INNOCENT/p2: fragments=[why-1, why-0, result-0, result-1, result-2] · sim=0.4943 · **命中分=5**
  - THE-EXPLORER/p2: fragments=[why-1, how-0, result-1, result-0] · sim=0.5566 · **命中分=4**
- **pseudo命中分合计**: 22
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge分歧**: ⚠
- **judge采信**: 不采信 · screening only
- **judge理由**: Both share a load-bearing surface element of a Texas Senator central to the plot, but the structural skeletons are not isomorphic: news involves political competition and electoral fate, while film centers on personal revenge and betrayal.

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 22 -->
### Long Live Freedom (2013) [THE-MAGICIAN, THE-OUTLAW, THE-RULER, THE-EXPLORER]
- **tmdb_id**: 167221
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.6525
- **genres** / **language**: Comedy, Drama / it
- **overview**: Elections are approaching and things don't look too good for the opposition. Their leader can't stand the pressure and disappears. To avoid a scandal, the upper echelons of the party concoct a risky plan: to replace him with his identical twin, a philosopher with BPD, whose eclectic ideas and direct approach unexpectedly make the party surge in the polls.
- **跳转**: https://themoviecosmos.com/movie/167221
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1: fragments=[why-0, why-1, how-0, result-0, result-2] · sim=0.6011 · **命中分=5**
  - THE-OUTLAW/p2: fragments=[why-0, how-0, result-1] · sim=0.6525 · **命中分=3**
  - THE-RULER/p2: fragments=[why-0, how-0, result-0, result-2] · sim=0.5918 · **命中分=4**
  - THE-MAGICIAN/p2: fragments=[why-0, why-1, result-0, result-1, result-2] · sim=0.5357 · **命中分=5**
  - THE-EXPLORER/p3: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5689 · **命中分=5**
- **pseudo命中分合计**: 22
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives are anchored by political elections as a concrete surface element, but the structural skeletons are not isomorphic: news depicts a real-world election upset driven by endorsement and spending, while film involves a fictional leadership crisis with an identical twin's psychological traits, leading to no thematic alignment beyond surface overlap.

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 20 -->
### The Campaign (2012) [THE-EVERYMAN, THE-SAGE, THE-HERO, THE-CAREGIVER] [优质·多agent]
- **tmdb_id**: 77953
- **quality_candidate**: true
- **neutral_hits**: 2
- **neutral_total**: 12
- **neutral_hit_rate**: 0.1667
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5462
- **genres** / **language**: Comedy / en
- **overview**: Two rival politicians compete to win an election to represent their small North Carolina congressional district in the United States House of Representatives.
- **跳转**: https://themoviecosmos.com/movie/77953
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/n1: fragments=[how-0, result-1, why-1, result-0, who-0] · sim=0.4537
  - THE-SAGE/n1: fragments=[result-0, result-1, how-0, why-0, why-1] · sim=0.4406
  - THE-HERO/p1: fragments=[why-0, how-0, result-0, result-1, result-2, why-1] · sim=0.5317 · **命中分=6**
  - THE-CAREGIVER/p2: fragments=[why-1, how-0, result-0, result-2] · sim=0.5462 · **命中分=4**
- **pseudo命中分合计**: 20
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The match is incidental, relying only on the broad theme of political elections; the film's generic overview could be equally explained by any unrelated news story about an election, failing the 0-guard test.

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 14 -->
### The Candidate (1972) [THE-CREATOR, THE-MAGICIAN, THE-CAREGIVER] [优质·多agent]
- **tmdb_id**: 21711
- **quality_candidate**: true
- **neutral_hits**: 2
- **neutral_total**: 12
- **neutral_hit_rate**: 0.1667
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5528
- **genres** / **language**: Comedy, Drama / en
- **overview**: Bill McKay is a candidate for the U.S. Senate from California. He has no hope of winning, so he is willing to tweak the establishment.
- **跳转**: https://themoviecosmos.com/movie/21711
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/n1: fragments=[how-0, who-0, why-0, result-1, result-2] · sim=0.4901
  - THE-MAGICIAN/n1: fragments=[why-0, how-0, result-2, who-0, who-2] · sim=0.5360
  - THE-CAREGIVER/p2: fragments=[why-1, how-0, result-0, result-2] · sim=0.5528 · **命中分=4**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives center on U.S. Senate elections with thematic isomorphism of underdog or insurgent candidates challenging the political establishment, though no specific concrete details (e.g., names, states) are shared.

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 10 -->
### People's Avengers (1943) [THE-JESTER, THE-LOVER]
- **tmdb_id**: 1168015
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5686
- **genres** / **language**: Documentary / ru
- **overview**: About the partisan movement during the Great Patriotic War.
- **跳转**: https://themoviecosmos.com/movie/1168015
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5686 · **命中分=5**
  - THE-LOVER/p3: fragments=[why-0, why-1, how-0, result-0, result-2] · sim=0.5382 · **命中分=5**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface elements (e.g., no shared concrete events, characters, or settings) and no structural isomorphism between the political news's electoral power shift and the film's WWII partisan resistance theme; an unrelated news story could explain the film equally.

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 9 -->
### Saratoga Trunk (1945) [THE-INNOCENT, THE-EXPLORER]
- **tmdb_id**: 46563
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5740
- **genres** / **language**: Drama, Romance, Western / en
- **overview**: An opportunistic Texas gambler and the exiled Creole daughter of an aristocratic family join forces to achieve justice from the society that has ostracized them.
- **跳转**: https://themoviecosmos.com/movie/46563
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[result-1, why-0, result-0, how-0] · sim=0.4718 · **命中分=4**
  - THE-EXPLORER/p1: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5740 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchors; Texas is incidental. Structural themes of challenging authority loosely align, but skeletons are not isomorphic, and unrelated news could equally explain the film.

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 9 -->
### Brexit: The Uncivil War (2019) [THE-LOVER, THE-RULER]
- **tmdb_id**: 536176
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5629
- **genres** / **language**: History, TV Movie, Drama / en
- **overview**: Political strategist Dominic Cummings leads a popular but controversial campaign to convince British voters to leave the European Union from 2015 up until the present day.
- **跳转**: https://themoviecosmos.com/movie/536176
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p2: fragments=[why-1, how-0, result-0, result-1] · sim=0.5238 · **命中分=4**
  - THE-RULER/p3: fragments=[why-0, why-1, how-0, result-1, result-2] · sim=0.5629 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives center on high-stakes political votes where underdog campaigns challenge established power, leading to significant political shifts; structural isomorphism exists in themes of political upheaval and voter persuasion, but no load-bearing concrete surface anchors are shared.

### 单 agent 命中

**Count:** 5 candidate(s)

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 9 -->
### Miller's Crossing (1990) [THE-LOVER]
- **tmdb_id**: 379
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5882
- **genres** / **language**: Drama, Thriller, Crime / en
- **overview**: Set in 1929, a political boss and his advisor have a parting of the ways when they both fall for the same woman.
- **跳转**: https://themoviecosmos.com/movie/379
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5882 · **命中分=5**
  - THE-LOVER/p2: fragments=[why-1, how-0, result-0, result-1] · sim=0.4961 · **命中分=4**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor; both involve political power struggles, but the film's core romantic catalyst is absent in the news, and structural isomorphism is weak as the catalysts differ (political defeat vs. love triangle).

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 5 -->
### Gabriel Over the White House (1933) [THE-MAGICIAN]
- **tmdb_id**: 100420
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5822
- **genres** / **language**: Drama, Fantasy, Romance / en
- **overview**: A political hack becomes President during the height of the Depression and undergoes a metamorphosis into an incorruptible statesman after a near-fatal accident.
- **跳转**: https://themoviecosmos.com/movie/100420
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1: fragments=[why-0, why-1, how-0, result-0, result-2] · sim=0.5822 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor or structural isomorphism; the news is about an election defeat and endorsement, while the film centers on a President's personal metamorphosis after an accident, with no shared concrete elements or aligned thematic skeletons.

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 5 -->
### 120 Seconds to Get Elected (2006) [THE-EVERYMAN]
- **tmdb_id**: 239070
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6241
- **genres** / **language**: Comedy / en
- **overview**: A politician has just a couple of minutes to convince people to vote for him, and tries to seduce his audience with promises he thinks they want to hear.
- **跳转**: https://themoviecosmos.com/movie/239070
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p2: fragments=[result-1, how-0, why-1, why-0, result-2] · sim=0.6241 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The film's focus on a generic politician persuading voters in a short time is incidental to the news's specific context of a Texas Senate runoff with factors like endorsement and spending; no load-bearing surface anchor or structural isomorphism exists, as unrelated political news could equally explain the film.

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 5 -->
### Kodi (2016) [THE-LOVER]
- **tmdb_id**: 376455
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6353
- **genres** / **language**: Action, Drama, Thriller / ta
- **overview**: A young politician finds himself in a position where he has to contest against his girlfriend, who is ambitious. Circumstances force his look-alike twin to also get involved in this political battle.
- **跳转**: https://themoviecosmos.com/movie/376455
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.6353 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The news involves a specific U.S. Senate primary runoff with details like endorsement and spending, while the film focuses on a personal political rivalry with a girlfriend and twin. The shared element of 'political election' is too broad and not load-bearing, as the film's plot lacks the concrete anchors from the news, and no structural isomorphism exists due to differing power dynamics and themes. An unrelated political news could equally explain the film's premise.

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 5 -->
### The Honest Candidate (2024) [THE-RULER]
- **tmdb_id**: 1278099
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5806
- **genres** / **language**: Comedy / es
- **overview**: A former idealistic leader turned corrupt politician is cursed by his grandmother on the eve of the presidential election, forcing him to be honest. Can he win without lies and what will be the conditions?
- **跳转**: https://themoviecosmos.com/movie/1278099
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p3: fragments=[why-0, why-1, how-0, result-1, result-2] · sim=0.5806 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: News reports a factual political runoff with endorsements and funding, while film centers on a supernatural honesty curse in a presidential election; shared election setting is incidental, not load-bearing, and structures differ without isomorphic themes.

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

**Count:** 12 candidate(s)

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 29 -->
### Hostage: Missing Celebrity (2021) [THE-HERO, THE-EXPLORER, THE-OUTLAW, THE-RULER, THE-MAGICIAN] [优质·多agent]
- **tmdb_id**: 602463
- **quality_candidate**: true
- **neutral_hits**: 5
- **neutral_total**: 12
- **neutral_hit_rate**: 0.4167
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5796
- **genres** / **language**: Action / ko
- **overview**: A box office star has to prove his action credentials in the real world when he's kidnapped and held for ransom.
- **跳转**: https://themoviecosmos.com/movie/602463
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/n1: fragments=[how-1, result-0, who-2, why-0, how-0] · sim=0.5796
  - THE-EXPLORER/n1: fragments=[how-0, how-1, who-0, result-0, why-0] · sim=0.5417
  - THE-OUTLAW/n1: fragments=[how-0, who-0, how-1, result-0, why-0] · sim=0.5375
  - THE-RULER/n1: fragments=[result-0, how-1, who-0, why-0, how-0] · sim=0.5444
  - THE-MAGICIAN/n1: fragments=[how-0, why-0, result-1, who-0, how-1] · sim=0.5551
  - THE-OUTLAW/p1: fragments=[how-0, how-1, result-0, result-1] · sim=0.5661 · **命中分=4**
- **pseudo命中分合计**: 29
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: News involves a scandal with false AI claims leading to arrest, while film centers on a celebrity kidnapped for ransom. Celebrity status is incidental, not a load-bearing shared element; no structural isomorphism in themes or plot skeleton.

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 25 -->
### U Turn (2016) [THE-RULER, THE-CREATOR, THE-MAGICIAN, THE-JESTER, THE-EXPLORER]
- **tmdb_id**: 397490
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 5
- **优质候选**: false
- **distinct_agents**: 5
- **相似度**: 0.6290
- **genres** / **language**: Mystery, Thriller, Crime, Horror / kn
- **overview**: A journalist who intents to write an article on traffic rule breakers gets dragged into a whirlpool of murder cases and deception.
- **跳转**: https://themoviecosmos.com/movie/397490
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6173 · **命中分=5**
  - THE-CREATOR/p2: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5324 · **命中分=5**
  - THE-MAGICIAN/p2: fragments=[how-0, why-0, result-1, how-1, result-0] · sim=0.6290 · **命中分=5**
  - THE-JESTER/p2: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6229 · **命中分=5**
  - THE-EXPLORER/p3: fragments=[how-0, why-0, how-1, result-0, result-1] · sim=0.6231 · **命中分=5**
- **pseudo命中分合计**: 25
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor: news involves AI-fabricated claims against a celebrity, while film focuses on a journalist investigating traffic rule breakers leading to murder—no shared concrete elements. No structural isomorphism: themes of deception differ in context and power dynamics, with news about digital misinformation and film about crime escalation. An unrelated news could equally explain the film.

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 22 -->
### One Way (2006) [THE-INNOCENT, THE-LOVER, THE-HERO, THE-RULER]
- **tmdb_id**: 7298
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.6279
- **genres** / **language**: Crime, Mystery, Thriller / en
- **overview**: To cover up his infidelities and protect his upcoming marriage, a star advertiser helps free an accused rapist by giving a false alibi and suffers the brutal revenge of the victim.
- **跳转**: https://themoviecosmos.com/movie/7298
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, how-0, result-0] · sim=0.5671 · **命中分=3**
  - THE-LOVER/p1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6134 · **命中分=5**
  - THE-HERO/p2: fragments=[how-0, how-1, result-0, result-1] · sim=0.6107 · **命中分=4**
  - THE-LOVER/p2: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6050 · **命中分=5**
  - THE-RULER/p2: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6279 · **命中分=5**
- **pseudo命中分合计**: 22
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both involve protagonists using deception (false claims vs. false alibi) for personal gain, leading to severe consequences, but no concrete surface elements like specific technologies or contexts are shared; the power/fate skeleton of lies backfiring is isomorphic.

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 22 -->
### Scandal (1950) [THE-CAREGIVER, THE-HERO, THE-SAGE, THE-JESTER]
- **tmdb_id**: 32690
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.6206
- **genres** / **language**: Drama / ja
- **overview**: A celebrity photograph sparks a court case as a tabloid magazine spins a scandalous yarn over a painter and a famous singer.
- **跳转**: https://themoviecosmos.com/movie/32690
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6100 · **命中分=5**
  - THE-HERO/p2: fragments=[how-0, how-1, result-0, result-1] · sim=0.6206 · **命中分=4**
  - THE-SAGE/p2: fragments=[why-0, how-1, result-1] · sim=0.6200 · **命中分=3**
  - THE-JESTER/p2: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5912 · **命中分=5**
  - THE-JESTER/p3: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5816 · **命中分=5**
- **pseudo命中分合计**: 22
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 双重
- **judge采信**: 不采信 · screening only
- **judge理由**: Both involve fabricated media-driven scandals (AI-generated claims vs. tabloid yarn) leading to legal consequences and career impacts for celebrities, with shared thematic structure of deception and media manipulation.

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 20 -->
### Prophecy (2015) [THE-HERO, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-EVERYMAN] [优质·多agent]
- **tmdb_id**: 347483
- **quality_candidate**: true
- **neutral_hits**: 2
- **neutral_total**: 12
- **neutral_hit_rate**: 0.1667
- **distinct_agents**: 3
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.5817
- **genres** / **language**: Mystery, Thriller / ja
- **overview**: The cyber crime investigation division at the Tokyo Metropolitan Police Department finds a video on website "YOURTUBE." In the video, a man covered by a newspaper, warns that a fire will be set at a food processing company. More crime notices are soon found involving violent crimes.  Geitsu is the main guy behind the group "Shinbunshi," which has posted the videos. He used to work as a temporary employee at an IT company, but was unfairly dismissed. He then begins doing manual labor work and meets the other members of "Shinbushi."
- **跳转**: https://themoviecosmos.com/movie/347483
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/n1: fragments=[how-1, result-0, who-2, why-0, how-0] · sim=0.5008
  - THE-RULER/n1: fragments=[result-0, how-1, who-0, why-0, how-0] · sim=0.4917
  - THE-MAGICIAN/p1: fragments=[why-0, how-0, result-1] · sim=0.5561 · **命中分=3**
  - THE-SAGE/p1: fragments=[how-0, how-1, result-0] · sim=0.5817 · **命中分=3**
  - THE-EVERYMAN/p3: fragments=[how-0, how-1, result-0, result-1] · sim=0.5529 · **命中分=4**
- **pseudo命中分合计**: 20
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 双重
- **judge采信**: 不采信 · screening only
- **judge理由**: Both the news and film feature online video platforms (YouTube/YouTube-like) as load-bearing anchors for deceptive digital content that triggers criminal investigations and real-world consequences, with structural isomorphism in themes of technology misuse, law enforcement response, and societal impact.

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 20 -->
### Cobweb (2023) [THE-INNOCENT, THE-EVERYMAN, THE-CAREGIVER, THE-MAGICIAN]
- **tmdb_id**: 901121
- **quality_candidate**: false
- **neutral_hits**: 4
- **neutral_total**: 12
- **neutral_hit_rate**: 0.3333
- **distinct_agents**: 0
- **优质候选**: false
- **distinct_agents**: 0
- **相似度**: 0.6044
- **genres** / **language**: Comedy, Drama / ko
- **overview**: In the 1970s, Director Kim is obsessed by the desire to re-shoot the ending of his completed film Cobweb, but chaos and turmoil grip the set with interference from the censorship authorities, and the complaints of actors and producers who can't understand the re-written ending. Will Kim be able to find a way through this chaos to fulfill his artistic ambitions and complete his masterpiece?
- **跳转**: https://themoviecosmos.com/movie/901121
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[result-1, who-1, result-0, why-0, how-0] · sim=0.5837
  - THE-EVERYMAN/n1: fragments=[result-1, who-0, how-0, why-0, result-0] · sim=0.5790
  - THE-CAREGIVER/n1: fragments=[result-1, who-1, how-0, why-0, how-1] · sim=0.6044
  - THE-MAGICIAN/n1: fragments=[how-0, why-0, result-1, who-0, how-1] · sim=0.5483
- **pseudo命中分合计**: 20
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing shared concrete element or structural isomorphism; news involves modern AI-fabricated scandal affecting an actor, while film focuses on 1970s artistic struggle with censorship, with only incidental overlap in Korean entertainment setting.

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 11 -->
### The Green Hornet (1940) [THE-EVERYMAN, THE-MAGICIAN, THE-SAGE]
- **tmdb_id**: 250332
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.6114
- **genres** / **language**: Adventure, Crime, Science Fiction / en
- **overview**: A newspaper publisher and his Korean servant fight crime as vigilantes who pose as a notorious masked gangster and his aide.
- **跳转**: https://themoviecosmos.com/movie/250332
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5247 · **命中分=5**
  - THE-MAGICIAN/p1: fragments=[why-0, how-0, result-1] · sim=0.6114 · **命中分=3**
  - THE-SAGE/p1: fragments=[how-0, how-1, result-0] · sim=0.5580 · **命中分=3**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor shared; incidental overlaps (e.g., media, Korean elements) are not concrete or critical. Structural skeletons are not isomorphic: news focuses on AI fabrication and legal consequences, while film on vigilante deception for justice.

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 10 -->
### Fairy in a Cage (1977) [THE-RULER, THE-MAGICIAN]
- **tmdb_id**: 140785
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.6138
- **genres** / **language**: Drama, Horror / ja
- **overview**: During World War II a moral corrupt judge uses the military police to falsely accuse and imprison a high class business woman who captures his eye at a party. In his personal underground dungeon he subjects her to various humiliations and sexual abuse.
- **跳转**: https://themoviecosmos.com/movie/140785
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p2: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6138 · **命中分=5**
  - THE-MAGICIAN/p3: fragments=[why-0, how-0, result-1, how-1, result-0] · sim=0.5362 · **命中分=5**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 双重
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives feature false accusations as a load-bearing surface anchor: in the news, AI-fabricated claims target an actor, while in the film, false accusations by a corrupt judge imprison a business woman. Structurally, there is isomorphism in themes of power abuse and exploitation for personal gain (financial in news, sexual/control in film), leading to severe consequences for the victim.

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 10 -->
### Peligro en tu mirada (2021) [THE-EXPLORER, THE-LOVER] [优质·多agent]
- **tmdb_id**: 841297
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.6151
- **genres** / **language**: Drama, Thriller / es
- **overview**: A female photographer is coerced into spying on the affaire of a political candidate, becoming the sole witness of a crime of which he is falsely accused
- **跳转**: https://themoviecosmos.com/movie/841297
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/n1: fragments=[how-0, how-1, who-0, result-0, why-0] · sim=0.5237
  - THE-LOVER/p3: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6151 · **命中分=5**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: Shared theme of false accusations is incidental; news involves AI-fabricated celebrity gossip for financial gain, while film focuses on political coercion and crime with no load-bearing concrete elements or structural isomorphism.

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 9 -->
### The Roundup 3: No Way Out (2023) [THE-CAREGIVER, THE-OUTLAW] [优质·多agent]
- **tmdb_id**: 955555
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.6012
- **genres** / **language**: Action, Crime, Comedy, Thriller / ko
- **overview**: Detective Ma Seok-do changes his affiliation from the Geumcheon Police Station to the Metropolitan Investigation Team, in order to eradicate Japanese gangsters who enter Korea to commit heinous crimes.
- **跳转**: https://themoviecosmos.com/movie/955555
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/n1: fragments=[result-1, who-1, how-0, why-0, how-1] · sim=0.5839
  - THE-OUTLAW/p1: fragments=[how-0, how-1, result-0, result-1] · sim=0.6012 · **命中分=4**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing shared concrete element; news involves AI fabrication and celebrity defamation, while film focuses on detective combating physical gangsters; structural themes of justice differ (cybercrime vs. organized crime), and an unrelated crime news could equally explain the film.

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 8 -->
### Black Money (2019) [THE-SAGE, THE-LOVER]
- **tmdb_id**: 603314
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.6324
- **genres** / **language**: Crime, Drama, Thriller / ko
- **overview**: A prosecutor is falsely accused of sexual assault in a suicide note from a woman that he is convinced was actually murdered. As he investigates her death to clear his name, he realizes that the truth lies in a huge financial scandal.
- **跳转**: https://themoviecosmos.com/movie/603314
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-SAGE/p2: fragments=[why-0, how-1, result-1] · sim=0.6324 · **命中分=3**
  - THE-LOVER/p3: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6233 · **命中分=5**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives center on false accusations that damage reputations and lead to investigations uncovering financial scandals, with isomorphic thematic skeletons but no load-bearing shared concrete surface elements.

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 8 -->
### AK vs AK (2020) [THE-CAREGIVER, THE-INNOCENT]
- **tmdb_id**: 735919
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.6024
- **genres** / **language**: Comedy, Action, Drama, Crime / hi
- **overview**: After a public spat with a movie star,  a disgraced director retaliates by kidnapping the actor's daughter, filming the search for her in real-time.
- **跳转**: https://themoviecosmos.com/movie/735919
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6024 · **命中分=5**
  - THE-INNOCENT/p2: fragments=[how-1, result-1, why-0] · sim=0.5896 · **命中分=3**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The news centers on AI-fabricated defamation and arrest, while the film involves kidnapping and real-time filming for retaliation. The shared element of an actor facing disruption is incidental, with no load-bearing surface anchor or structural isomorphism in theme or power dynamics.

### 单 agent 命中

**Count:** 4 candidate(s)

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 8 -->
### Inside Man (2023) [THE-HERO]
- **tmdb_id**: 1020662
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6058
- **genres** / **language**: Crime, Thriller, Drama / en
- **overview**: Based on true events. A disgraced police detective seeking redemption goes undercover to expose a violent crime syndicate. But as he sinks deeper into the mob, the price for absolution may be higher than he can afford.
- **跳转**: https://themoviecosmos.com/movie/1020662
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[why-0, how-0, how-1, result-0] · sim=0.6058 · **命中分=4**
  - THE-HERO/p3: fragments=[why-0, how-0, how-1, result-1] · sim=0.5951 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface elements shared; news involves AI scandal and celebrity defamation, film centers on undercover crime syndicate operations. Thematic overlaps in deception and consequences are incidental and not structurally isomorphic, as power dynamics and core fates diverge.

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Te rompo el rating (1981) [THE-MAGICIAN]
- **tmdb_id**: 369384
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5994
- **genres** / **language**: Comedy / es
- **overview**: A television network infiltrates an inept employee (Porcel) in the competition and he begins to ruin all the programs but, instead of subtracting audience, he only managed to improve it.
- **跳转**: https://themoviecosmos.com/movie/369384
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p2: fragments=[how-0, why-0, result-1, how-1, result-0] · sim=0.5994 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor: news involves AI-fabricated claims and arrest in social media, while film centers on TV network sabotage and audience ratings; concrete elements do not share core essence. No structural isomorphism: news theme is deception with harmful consequences, film theme is sabotage with beneficial outcomes; skeletons are not aligned.

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Diamantino (2018) [THE-LOVER]
- **tmdb_id**: 518495
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6146
- **genres** / **language**: Comedy, Science Fiction, Fantasy / pt
- **overview**: A disgraced soccer star seeks redemption but is exploited by a variety of causes hoping to capitalize on his celebrity.
- **跳转**: https://themoviecosmos.com/movie/518495
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p2: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6146 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: Both involve celebrity exploitation, but there is no load-bearing concrete element (e.g., AI fabrication, YouTuber, or specific scandal) shared, and the structural skeletons are not isomorphic; the news focuses on financial fraud via false claims, while the film is a satirical exploration of ideological exploitation, making the overlap incidental.

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Impulse (2023) [THE-EXPLORER]
- **tmdb_id**: 1262124
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6145
- **genres** / **language**: Thriller, Action / en
- **overview**: A young journalist is pulled into the orbit of a string of murders that connects media moguls, politicians, and Hollywood elites - setting off on the impossible task of taking them down.
- **跳转**: https://themoviecosmos.com/movie/1262124
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p3: fragments=[how-0, why-0, how-1, result-0, result-1] · sim=0.6145 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor; incidental overlap only in broad media theme without specific shared concrete elements. Structural themes not isomorphic: news involves false accusations and AI-driven scandal, while film involves murder investigations and elite corruption.

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

**Count:** 10 candidate(s)

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 77 -->
### Poem of the Sea (1958) [THE-EXPLORER, THE-CREATOR, THE-MAGICIAN, THE-HERO, THE-CAREGIVER, THE-RULER, THE-OUTLAW, THE-SAGE, THE-JESTER, THE-EVERYMAN] [优质·多agent]
- **tmdb_id**: 257637
- **quality_candidate**: true
- **neutral_hits**: 3
- **neutral_total**: 12
- **neutral_hit_rate**: 0.2500
- **distinct_agents**: 9
- **优质候选**: true
- **distinct_agents**: 9
- **相似度**: 0.5911
- **genres** / **language**: Drama / ru
- **overview**: A Soviet dam project means that many old Ukrainian villages will end up under water. There are conflicts between the dam engineers and villagers who don't want to move.
- **跳转**: https://themoviecosmos.com/movie/257637
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/n1: fragments=[how-0, how-1, how-2, how-3, how-4] · sim=0.5581
  - THE-CREATOR/n1: fragments=[how-1, how-0, how-2, result-2, how-3] · sim=0.5911
  - THE-MAGICIAN/n1: fragments=[how-5, who-3, how-0, why-0, how-1] · sim=0.5125
  - THE-HERO/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1, result-3, result-4] · sim=0.5319 · **命中分=8**
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4946 · **命中分=7**
  - THE-EXPLORER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4] · sim=0.5746 · **命中分=6**
  - THE-CREATOR/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-2, result-3, result-5] · sim=0.5137 · **命中分=9**
  - THE-RULER/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5101 · **命中分=6**
  - THE-OUTLAW/p2: fragments=[how-1, how-2, how-3, how-4, how-5, result-1, result-5] · sim=0.5598 · **命中分=7**
  - THE-SAGE/p2: fragments=[how-0, how-1, how-2, how-3, how-4] · sim=0.4954 · **命中分=5**
  - THE-JESTER/p2: fragments=[how-1, how-2, how-3, how-4, how-5, result-0, result-1, result-4] · sim=0.5704 · **命中分=8**
  - THE-EVERYMAN/p3: fragments=[why-0, how-3, result-1, result-3, result-4, result-5] · sim=0.5639 · **命中分=6**
- **pseudo命中分合计**: 77
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge采信**: 不采信 · screening only
- **judge理由**: Shared concrete element of dams and water management (surface anchor), but news emphasizes natural disaster response without conflict, while film centers on displacement resistance, so structural skeleton not isomorphic.

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 48 -->
### Raining Cats and Frogs (2003) [THE-HERO, THE-EXPLORER, THE-INNOCENT, THE-CREATOR, THE-OUTLAW]
- **tmdb_id**: 22624
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 5
- **优质候选**: false
- **distinct_agents**: 5
- **相似度**: 0.5940
- **genres** / **language**: Animation, Fantasy, Adventure / fr
- **overview**: It's a catastrophe! A flood has hit our planet and an unusual group of people are all that remains. Led by Ferdinand, a modern day Noah, this little group have managed to defy the furiously raging elements. People and animals alike are dragged through this incredible whirlpool of an adventure.
- **跳转**: https://themoviecosmos.com/movie/22624
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1, result-3, result-4] · sim=0.5347 · **命中分=8**
  - THE-EXPLORER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4] · sim=0.5940 · **命中分=6**
  - THE-INNOCENT/p2: fragments=[why-0, how-1, how-2, result-0, result-1, result-3, result-4] · sim=0.5116 · **命中分=7**
  - THE-CREATOR/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-1, result-2, result-3, result-4] · sim=0.5630 · **命中分=9**
  - THE-INNOCENT/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-3, result-4, result-5] · sim=0.5016 · **命中分=10**
  - THE-OUTLAW/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-1, result-0] · sim=0.5213 · **命中分=8**
- **pseudo命中分合计**: 48
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge采信**: 不采信 · screening only
- **judge理由**: Both share the concrete element of a flood disaster as a load-bearing anchor, but the structural skeletons are not isomorphic: the news emphasizes real-world consequences, government response, and tragedy, while the film is a fictional adventure centered on group survival against the elements.

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 43 -->
### Flood (2007) [THE-SAGE, THE-INNOCENT, THE-EVERYMAN, THE-CAREGIVER, THE-LOVER] [优质·多agent]
- **tmdb_id**: 6309
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 5
- **优质候选**: true
- **distinct_agents**: 5
- **相似度**: 0.5779
- **genres** / **language**: Drama, Action, Thriller / en
- **overview**: Timely yet terrifying, The Flood predicts the unthinkable. When a raging storm coincides with high seas it unleashes a colossal tidal surge, which travels mercilessly down England's East Coast and into the Thames Estuary. Overwhelming the Barrier, torrents of water pour into the city. The lives of millions of Londoners are at stake.
- **跳转**: https://themoviecosmos.com/movie/6309
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-SAGE/n1: fragments=[result-0, why-0, how-0, how-1, how-2] · sim=0.4847
  - THE-INNOCENT/p1: fragments=[why-0, how-1, how-2, how-3, how-4, how-5, result-0, result-5] · sim=0.5271 · **命中分=8**
  - THE-EVERYMAN/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, how-5, result-0, result-3] · sim=0.5487 · **命中分=9**
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5449 · **命中分=7**
  - THE-LOVER/p1: fragments=[why-0, how-2, result-0, result-1] · sim=0.5273 · **命中分=4**
  - THE-SAGE/p1: fragments=[why-0, how-1, result-0, result-1, result-5] · sim=0.5779 · **命中分=5**
  - THE-EVERYMAN/p2: fragments=[why-0, result-1, result-2, result-3, result-5] · sim=0.5723 · **命中分=5**
- **pseudo命中分合计**: 43
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: Incidental overlap only; both involve flooding, but no load-bearing concrete surface anchor (e.g., specific shared details like settings, characters, or events) and structural skeletons are not isomorphic (river flood from rains in Syria vs. tidal surge overwhelming a barrier in London).

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 28 -->
### Deluge (1933) [THE-LOVER, THE-EVERYMAN, THE-OUTLAW, THE-SAGE]
- **tmdb_id**: 163293
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.6064
- **genres** / **language**: Science Fiction, Drama, Thriller / en
- **overview**: A massive earthquake strikes the United States, which destroys the West Coast and unleashes a massive flood that threatens to destroy the East Coast as well.
- **跳转**: https://themoviecosmos.com/movie/163293
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p2: fragments=[how-0, how-1, how-2, how-3, how-4, result-2, result-3, result-1] · sim=0.6064 · **命中分=8**
  - THE-EVERYMAN/p3: fragments=[why-0, how-3, result-1, result-3, result-4, result-5] · sim=0.5576 · **命中分=6**
  - THE-OUTLAW/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-1, result-0] · sim=0.5092 · **命中分=8**
  - THE-SAGE/p3: fragments=[how-2, how-3, how-4, how-5, result-4, result-5] · sim=0.5139 · **命中分=6**
- **pseudo命中分合计**: 28
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The shared element of 'flood' is incidental and not load-bearing, as the news details a specific rain-induced flood in Syria with political and social responses, while the film depicts an earthquake-triggered apocalyptic flood in the US. No concrete elements align, and the thematic skeletons differ in context and scale, making an unrelated flood news equally plausible for the film.

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 27 -->
### The Whole Dam Family and the Dam Dog (1905) [THE-EXPLORER, THE-CREATOR, THE-JESTER] [优质·多agent]
- **tmdb_id**: 44325
- **quality_candidate**: true
- **neutral_hits**: 2
- **neutral_total**: 12
- **neutral_hit_rate**: 0.1667
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5944
- **genres** / **language**: Family, Comedy / en
- **overview**: A portrait of the Dam family.
- **跳转**: https://themoviecosmos.com/movie/44325
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/n1: fragments=[how-0, how-1, how-2, how-3, how-4] · sim=0.5355
  - THE-CREATOR/n1: fragments=[how-1, how-0, how-2, result-2, how-3] · sim=0.5686
  - THE-JESTER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-5] · sim=0.5944 · **命中分=9**
  - THE-JESTER/p2: fragments=[how-1, how-2, how-3, how-4, how-5, result-0, result-1, result-4] · sim=0.5654 · **命中分=8**
- **pseudo命中分合计**: 27
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The word 'dam' appears in both but is incidental; the film's overview as a family portrait lacks load-bearing concrete elements or structural isomorphism with the news's flood crisis themes.

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 24 -->
### Water Wrackets (1978) [THE-JESTER, THE-MAGICIAN, THE-HERO]
- **tmdb_id**: 249011
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.6215
- **genres** / **language**: Fantasy / en
- **overview**: Multifarious images of a lake are overlaid with water effects and a narrated history of the campaigns fought by the fictional water-wracket army.
- **跳转**: https://themoviecosmos.com/movie/249011
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-5] · sim=0.6215 · **命中分=9**
  - THE-MAGICIAN/p2: fragments=[how-5, how-4, how-3, result-5, result-4] · sim=0.5263 · **命中分=5**
  - THE-HERO/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, how-5, result-0, result-1, result-5] · sim=0.5378 · **命中分=10**
- **pseudo命中分合计**: 24
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: Incidental water overlap; news is about real flood disaster and government response, film is about fictional military campaigns with no structural isomorphism or specific concrete anchor.

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 17 -->
### Dry (2022) [THE-INNOCENT, THE-EVERYMAN]
- **tmdb_id**: 797840
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5699
- **genres** / **language**: Drama, Comedy, Science Fiction / it
- **overview**: In Rome it hasn’t rained for three years and the lack of water is overturning rules and habits. Through the city dying of thirst and prohibitions moves a chorus of people, young and old, marginalised and successful, victims and profiteers. Their lives are linked in a single design, while each seeks his or her deliverance.
- **跳转**: https://themoviecosmos.com/movie/797840
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, how-1, how-2, how-3, how-4, how-5, result-0, result-5] · sim=0.5401 · **命中分=8**
  - THE-EVERYMAN/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, how-5, result-0, result-3] · sim=0.5699 · **命中分=9**
- **pseudo命中分合计**: 17
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives center on a water-related environmental crisis (flooding in news, drought in film) leading to societal upheaval, with themes of fate, authority response, and human deliverance, showing thematic skeleton isomorphism without a load-bearing shared concrete element.

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 15 -->
### Piranha 3D (2010) [THE-SAGE, THE-HERO] [优质·多agent]
- **tmdb_id**: 43593
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5408
- **genres** / **language**: Comedy, Horror / en
- **overview**: Each year the population of sleepy Lake Victoria, Arizona explodes from 5,000 to 50,000 residents for the annual Spring Break celebration. But then, an earthquake opens an underwater chasm, releasing an enormous swarm of ancient Piranha that have been dormant for thousands of years, now with a taste for human flesh. This year, there's something more to worry about than the usual hangovers and complaints from locals, a new type of terror is about to be cut loose on Lake Victoria.
- **跳转**: https://themoviecosmos.com/movie/43593
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-SAGE/n1: fragments=[result-0, why-0, how-0, how-1, how-2] · sim=0.4930
  - THE-HERO/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, how-5, result-0, result-1, result-5] · sim=0.5408 · **命中分=10**
- **pseudo命中分合计**: 15
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: Incidental water theme; no load-bearing surface anchor (flood vs. piranha attack) and no structural isomorphism (news focuses on natural disaster response; film on creature horror survival).

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 14 -->
### Jet Stream (2013) [THE-MAGICIAN, THE-CAREGIVER]
- **tmdb_id**: 210219
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5645
- **genres** / **language**: Action, Adventure, Drama, Science Fiction, TV Movie / en
- **overview**: A TV weatherman tries to prove his theory that a series of unexplained catastrophes are the result of powerful winds found in the upper atmosphere coming down to ground level. His claims attract the attention of government scientists, who need his help to control the phenomena before it destroys all life on Earth (Locatetv.com)
- **跳转**: https://themoviecosmos.com/movie/210219
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, how-5, result-0] · sim=0.5401 · **命中分=8**
  - THE-CAREGIVER/p2: fragments=[why-0, how-0, how-1, how-2, result-0, result-4] · sim=0.5645 · **命中分=6**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: Incidental overlap in broad disaster themes, but no load-bearing surface anchor (floods vs. wind catastrophes) and structural skeletons are not isomorphic (reactive government response vs. proactive individual theory-driven prevention).

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 11 -->
### Seattle Superstorm (2012) [THE-EVERYMAN, THE-CAREGIVER]
- **tmdb_id**: 107100
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.6078
- **genres** / **language**: Action, Science Fiction, TV Movie / en
- **overview**: An object is shot down over Seattle and the debris begins to affect the local weather, ultimately threatening the whole world.
- **跳转**: https://themoviecosmos.com/movie/107100
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p2: fragments=[why-0, result-1, result-2, result-3, result-5] · sim=0.5926 · **命中分=5**
  - THE-CAREGIVER/p2: fragments=[why-0, how-0, how-1, how-2, result-0, result-4] · sim=0.6078 · **命中分=6**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives center on catastrophic weather disasters (flooding and superstorm) as load-bearing concrete elements, but the news focuses on natural disaster response and political leadership, while the film involves a sci-fi technological accident with global threats, showing no structural isomorphism.

### 单 agent 命中

**Count:** 7 candidate(s)

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 15 -->
### World Gone Wild (1987) [THE-OUTLAW]
- **tmdb_id**: 38141
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5797
- **genres** / **language**: Action, Science Fiction / en
- **overview**: In the nuclear ravaged wasteland of Earth 2087 water is as precious as life itself. The isolated Lost Wells outpost survived the holocaust and the inhabitants guard the source of their existence. Now an evil cult of renegades want control of their valuable water supply. And the villagers are no match for such brute military force. Only one man can help the stricken community - a mercenary living in a distance cannibal city. But even he, and his strange henchmen, may not be able to survive in the world gone wild.
- **跳转**: https://themoviecosmos.com/movie/38141
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0, result-1] · sim=0.5797 · **命中分=8**
  - THE-OUTLAW/p2: fragments=[how-1, how-2, how-3, how-4, how-5, result-1, result-5] · sim=0.5417 · **命中分=7**
- **pseudo命中分合计**: 15
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: Both the news and film involve water as a central element, but the contexts are inversely opposed: the news describes water excess causing deadly floods and government response, while the film focuses on water scarcity and conflict over control in a post-apocalyptic setting. There is no load-bearing shared concrete element (e.g., specific events or settings), and the structural themes (disaster response vs. resource conflict) are not isomorphic, resulting in incidental overlap only.

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 9 -->
### The Sweet Hereafter (1997) [THE-JESTER]
- **tmdb_id**: 10217
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5765
- **genres** / **language**: Drama / en
- **overview**: A small mountain community in Canada is devastated when a school bus accident leaves more than a dozen of its children dead. A big-city lawyer arrives to help the survivors' and victims' families prepare a class-action suit, but his efforts only seem to push the townspeople further apart. At the same time, one teenage survivor of the accident has to reckon with the loss of innocence brought about by a different kind of damage.
- **跳转**: https://themoviecosmos.com/movie/10217
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p3: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-5, result-4] · sim=0.5765 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives share a structural skeleton of community tragedy involving child deaths, leading to themes of external intervention (president/lawyer), communal division, and personal reckoning with loss and fate, but no specific surface elements like flood or bus accident are directly shared.

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 9 -->
### Ju-On: White Ghost (2009) [THE-JESTER]
- **tmdb_id**: 26693
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5822
- **genres** / **language**: Fantasy, Horror / ja
- **overview**: An apparitions of a young schoolgirl in a yellow rain hat, a family massacre, and a law student's suicide after he fails his bar exam are linked by the ominous recordings discovered on an audio cassette.
- **跳转**: https://themoviecosmos.com/movie/26693
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p3: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-5, result-4] · sim=0.5822 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface elements: news focuses on real-world floods and drowning, while film's rain hat is incidental to supernatural horror themes. No structural isomorphism: news involves natural disasters and political response, film involves curses and hauntings, with no shared power or fate skeleton. An unrelated news (e.g., a crime story) could explain the film equally, triggering the 0-guard.

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 9 -->
### The Storm (2009) [THE-EXPLORER]
- **tmdb_id**: 29602
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6144
- **genres** / **language**: Drama / nl
- **overview**: A fictional story within the historical context of the disastrous flood that engulfed the Dutch coastal province of Zeeland in 1953. When their farmhouse is destroyed by the flood, teenage mother Julia gets separated from her baby boy, whom she kept hidden in a box. She is saved from drowning by a young air force lieutenant, who agrees to go help looking for Julia's little son.
- **跳转**: https://themoviecosmos.com/movie/29602
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p2: fragments=[how-2, how-3, how-4, how-5, result-0, result-1, result-2, result-3, result-4] · sim=0.6144 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: Both involve flood disasters, but the shared element is incidental without load-bearing concrete anchors or structural isomorphism; the news focuses on macro response, while the film centers on personal drama.

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 9 -->
### Tidal Wave (2009) [THE-EXPLORER]
- **tmdb_id**: 33196
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6289
- **genres** / **language**: Action, Drama, Thriller / ko
- **overview**: On Haeundae Beach, a guilt-ridden fisherman takes care of a woman whose father accidentally got killed. A scientist reunites with his ex-wife and a daughter who doesn't even remember his face. And a poor rescue worker falls in love with a rich city girl. When they all find out a gigantic tsunami will hit the beach, they realize they only have 10 minutes to escape.
- **跳转**: https://themoviecosmos.com/movie/33196
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p2: fragments=[how-2, how-3, how-4, how-5, result-0, result-1, result-2, result-3, result-4] · sim=0.6289 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives are centered on catastrophic water disasters (river flooding vs. tsunami), providing a load-bearing surface anchor. However, the news emphasizes governmental response and community impact, while the film focuses on personal melodrama and immediate escape, lacking structural isomorphism.

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 9 -->
### Disaster Wars: Earthquake vs. Tsunami (2013) [THE-CREATOR]
- **tmdb_id**: 289214
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5595
- **genres** / **language**: Thriller, Action, Drama, Science Fiction / en
- **overview**: Deep underwater in the Marianas Trench an accident results in a devastating Tsunami that destroys the Hawaiian Islands as it continues toward the west coast. Panic ensues all up and down the western coast of North and South America. In an attempt to lessen its impact, scientists launch an underwater explosion that inadvertently makes the tsunami more powerful and focused on Los Angeles. Scientists rush to a solution while the military begins planning for the worst. Los Angeles begins emergency evacuation. Lives and loves are lost even as a brash young grad student comes up with a solution: start the mother of all earthquakes to counter the rushing torrent and raise the continental shelf off the coast of the United States.
- **跳转**: https://themoviecosmos.com/movie/289214
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-1, result-2, result-3, result-4] · sim=0.5595 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge采信**: 不采信 · screening only
- **judge理由**: Both center on water-based natural disasters (flood/tsunami) causing evacuations and destruction, but the news lacks the film's structural escalation from failed human mitigation.

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 8 -->
### Geostorm (2017) [THE-OUTLAW]
- **tmdb_id**: 274855
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5482
- **genres** / **language**: Action, Science Fiction, Thriller / en
- **overview**: After an unprecedented series of natural disasters threatened the planet, the world's leaders came together to create an intricate network of satellites to control the global climate and keep everyone safe. But now, something has gone wrong: the system built to protect Earth is attacking it, and it becomes a race against the clock to uncover the real threat before a worldwide geostorm wipes out everything and everyone along with it.
- **跳转**: https://themoviecosmos.com/movie/274855
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0, result-1] · sim=0.5482 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: News focuses on natural flooding on the Euphrates, while film centers on artificial climate control causing global disasters; overlap is incidental without load-bearing surface anchors or structural isomorphism, and unrelated news about natural disasters could equally explain the film.

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

**Count:** 14 candidate(s)

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 39 -->
### Lords of Scam (2021) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-OUTLAW, THE-CREATOR, THE-LOVER] [优质·多agent]
- **tmdb_id**: 888917
- **quality_candidate**: true
- **neutral_hits**: 3
- **neutral_total**: 12
- **neutral_hit_rate**: 0.2500
- **distinct_agents**: 3
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.4920
- **genres** / **language**: Documentary, Crime / fr
- **overview**: This documentary traces the rise and crash of scammers who conned the EU carbon quota system and pocketed millions before turning on one another.
- **跳转**: https://themoviecosmos.com/movie/888917
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[who-2, result-0, who-0, why-0, how-1] · sim=0.4223
  - THE-EVERYMAN/n1: fragments=[result-0, who-2, how-2, why-0, how-1] · sim=0.4558
  - THE-HERO/n1: fragments=[who-0, how-1, why-0, how-2, result-0] · sim=0.4711
  - THE-OUTLAW/n1: fragments=[who-1, result-1, who-2, why-0, how-1] · sim=0.3723
  - THE-CREATOR/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.4390 · **命中分=6**
  - THE-OUTLAW/p2: fragments=[why-0, why-1, how-0, how-1, how-2, result-0] · sim=0.4920 · **命中分=6**
  - THE-LOVER/p2: fragments=[why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4455 · **命中分=7**
- **pseudo命中分合计**: 39
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor or structural isomorphism. The news concerns EU regulatory fines for Google's anti-competitive behavior in digital markets, while the film depicts criminal fraud in the EU carbon quota system. The EU context is incidental, and the core elements (regulatory enforcement vs. criminal scam) and themes do not share a concrete or thematic skeleton.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 37 -->
### The Cop (1970) [THE-INNOCENT, THE-CAREGIVER, THE-RULER, THE-EVERYMAN, THE-CREATOR, THE-SAGE]
- **tmdb_id**: 94376
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 6
- **优质候选**: false
- **distinct_agents**: 6
- **相似度**: 0.5776
- **genres** / **language**: Drama, Crime, Thriller / fr
- **overview**: A crackdown on drugs leads a burned out cop to take the law into his own hands and seek revenge against villainous drug dealers. Word comes down from above that the United States feels French authorities have been lax on their arrests of the dealers. A violent action feature finds the harried inspector battling his colleagues as much as the criminal element targeted for extermination.
- **跳转**: https://themoviecosmos.com/movie/94376
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, how-1, result-0] · sim=0.4519 · **命中分=3**
  - THE-CAREGIVER/p1: fragments=[why-0, how-1, result-0, result-1] · sim=0.5722 · **命中分=4**
  - THE-RULER/p1: fragments=[why-0, how-1, how-2, how-3, result-1] · sim=0.4543 · **命中分=5**
  - THE-EVERYMAN/p2: fragments=[why-1, how-1, how-2, result-0, result-1] · sim=0.4910 · **命中分=5**
  - THE-CREATOR/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5496 · **命中分=7**
  - THE-RULER/p2: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5776 · **命中分=6**
  - THE-SAGE/p2: fragments=[how-0, how-1, how-2, how-3, why-0, result-0, result-1] · sim=0.4788 · **命中分=7**
- **pseudo命中分合计**: 37
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchors (news about EU fines for Google's search self-preferencing vs. film about a cop's vigilante revenge on drug dealers). Structural skeletons are not isomorphic: news involves institutional regulatory action, while film depicts personal extralegal enforcement with internal conflict. An unrelated news (e.g., police corruption) could explain the film equally.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 36 -->
### Special Section (1975) [THE-EVERYMAN, THE-EXPLORER, THE-CREATOR, THE-RULER, THE-SAGE, THE-LOVER] [优质·多agent]
- **tmdb_id**: 79921
- **quality_candidate**: true
- **neutral_hits**: 5
- **neutral_total**: 12
- **neutral_hit_rate**: 0.4167
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5469
- **genres** / **language**: Drama, History, Thriller / fr
- **overview**: In Nazi-occupied France, a German officer is assassinated. The Germans demand justice, and the Vichy government is quick to capitulate. Unable to apprehend the actual culprits, Minister of Justice Joseph Barthélémy decides the execution of token Frenchmen will suffice, but the problem is finding judges and jurors eager to participate in a sham trial of innocent men. The solution is a Special Section, a court comprised of individuals handpicked for this exact purpose.
- **跳转**: https://themoviecosmos.com/movie/79921
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/n1: fragments=[result-0, who-2, how-2, why-0, how-1] · sim=0.4814
  - THE-EXPLORER/n1: fragments=[how-1, how-0, why-1, result-0, who-0] · sim=0.4878
  - THE-CREATOR/n1: fragments=[how-0, how-1, how-2, how-3, why-0] · sim=0.5035
  - THE-RULER/n1: fragments=[result-0, who-0, how-1, how-2, why-0] · sim=0.4807
  - THE-SAGE/n1: fragments=[result-0, how-0, why-0, who-0, how-1] · sim=0.4762
  - THE-RULER/p2: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5469 · **命中分=6**
  - THE-LOVER/p3: fragments=[why-0, how-2, how-3, result-0, result-1] · sim=0.4508 · **命中分=5**
- **pseudo命中分合计**: 36
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: News involves EU regulatory fine for Google's anti-competitive practices, while film depicts a sham judicial system in Nazi-occupied France. No load-bearing concrete element (e.g., specific entities or events) is shared, and structural skeletons (power dynamics: corporate regulation vs. wartime oppression; themes: competition law vs. political scapegoating) are not isomorphic. An unrelated news could explain the film equally.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 31 -->
### A Ticket to Space (2006) [THE-INNOCENT, THE-HERO, THE-CREATOR, THE-MAGICIAN, THE-JESTER] [优质·多agent]
- **tmdb_id**: 13748
- **quality_candidate**: true
- **neutral_hits**: 5
- **neutral_total**: 12
- **neutral_hit_rate**: 0.4167
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.4994
- **genres** / **language**: Comedy, Science Fiction / fr
- **overview**: Face à l'incompréhension de la population française quant au montant des crédits alloués à la recherche spatiale, le gouvernement lance une vaste opération de communication. En partenariat avec le Centre spatial français, un grand jeu est organisé. "Le ticket pour l'espace", un jeu à gratter, va permettre à deux civils de séjourner dans la station orbitale européenne.
- **跳转**: https://themoviecosmos.com/movie/13748
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[who-2, result-0, who-0, why-0, how-1] · sim=0.4076
  - THE-HERO/n1: fragments=[who-0, how-1, why-0, how-2, result-0] · sim=0.4540
  - THE-CREATOR/n1: fragments=[how-0, how-1, how-2, how-3, why-0] · sim=0.4994
  - THE-MAGICIAN/n1: fragments=[who-0, how-0, why-0, how-1, who-1] · sim=0.4692
  - THE-JESTER/n1: fragments=[how-3, how-1, result-0, who-1, why-0] · sim=0.4529
  - THE-MAGICIAN/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.4478 · **命中分=6**
- **pseudo命中分合计**: 31
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor or structural isomorphism; news is about antitrust fines for corporate self-preferencing, film is about government promotional game for space tourism.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 27 -->
### Gabbar Is Back (2015) [THE-HERO, THE-CAREGIVER, THE-EVERYMAN, THE-EXPLORER, THE-CREATOR]
- **tmdb_id**: 337876
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 5
- **优质候选**: false
- **distinct_agents**: 5
- **相似度**: 0.5411
- **genres** / **language**: Drama, Action / hi
- **overview**: A vigilante network taking out corrupt officials draws the notice of the authorities.
- **跳转**: https://themoviecosmos.com/movie/337876
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5268 · **命中分=5**
  - THE-CAREGIVER/p1: fragments=[why-0, how-1, result-0, result-1] · sim=0.5411 · **命中分=4**
  - THE-EVERYMAN/p2: fragments=[why-1, how-1, how-2, result-0, result-1] · sim=0.4794 · **命中分=5**
  - THE-CAREGIVER/p3: fragments=[why-1, how-1, result-0] · sim=0.4874 · **命中分=3**
  - THE-EXPLORER/p3: fragments=[how-2, how-1, how-0, how-3] · sim=0.4667 · **命中分=4**
  - THE-CREATOR/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0] · sim=0.4741 · **命中分=6**
- **pseudo命中分合计**: 27
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor exists between the news (EU fine on Google for self-preferencing) and film (vigilante network targeting corrupt officials); structural skeleton (power/fate/theme) is not isomorphic, as news involves legal regulatory action while film involves extra-legal vigilante justice; an unrelated news story could explain the film equally, failing the 0-guard.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 19 -->
### The International (2009) [THE-LOVER, THE-OUTLAW, THE-EVERYMAN]
- **tmdb_id**: 4959
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5193
- **genres** / **language**: Action, Thriller, Crime, Mystery / en
- **overview**: An interpol agent and an attorney are determined to bring one of the world's most powerful banks to justice. Uncovering money laundering, arms trading, and conspiracy to destabilize world governments, their investigation takes them from Berlin, Milan, New York and Istanbul. Finding themselves in a chase across the globe, their relentless tenacity puts their own lives at risk.
- **跳转**: https://themoviecosmos.com/movie/4959
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4595 · **命中分=7**
  - THE-OUTLAW/p2: fragments=[why-0, why-1, how-0, how-1, how-2, result-0] · sim=0.4996 · **命中分=6**
  - THE-EVERYMAN/p3: fragments=[why-0, why-1, how-3, how-2, result-0, result-1] · sim=0.5193 · **命中分=6**
- **pseudo命中分合计**: 19
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: News details EU regulatory fine for Google's anti-competitive search practices, while film depicts a thriller about investigating a bank's criminal activities; no specific concrete shared element and skeletons differ (regulatory vs. criminal investigation), with only incidental thematic overlap.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 19 -->
### The Clearstream Affair (2015) [THE-EVERYMAN, THE-HERO, THE-MAGICIAN]
- **tmdb_id**: 320318
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5316
- **genres** / **language**: Thriller, Drama / fr
- **overview**: Journalist Denis Robert sparked a storm in the world of European finance by denouncing the murky operations of banking firm Clearstream. His quest to reveal the truth behind a secret world of shadowy multinational banking puts him in contact with an ever-expanding anti-corruption investigation carried out by Judge Renaud Van Ruymbeke. Their paths will lead them to the heart of a political/financial intrigue, which will rock the foundations of Europe and the French government itself.
- **跳转**: https://themoviecosmos.com/movie/320318
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4913 · **命中分=8**
  - THE-HERO/p1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5316 · **命中分=5**
  - THE-MAGICIAN/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.4343 · **命中分=6**
- **pseudo命中分合计**: 19
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives involve European institutional power uncovering hidden misconduct by large organizations, leading to significant legal or political consequences, but lack a specific shared concrete element (e.g., same company, law, or event) for a surface anchor.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 13 -->
### Taxi 4 (2007) [THE-SAGE, THE-EVERYMAN] [优质·多agent]
- **tmdb_id**: 2335
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5017
- **genres** / **language**: Action, Comedy, Crime / fr
- **overview**: Before being extradited to Africa to stand trial, a notorious Belgian criminal is entrusted to the Marseilles police department for less than 24 hours. But the wily crook convinces bumbling policeman Emilien he's a lowly Belgian embassy employee who got railroaded by the brilliant master criminal.
- **跳转**: https://themoviecosmos.com/movie/2335
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-SAGE/n1: fragments=[result-0, how-0, why-0, who-0, how-1] · sim=0.4546
  - THE-EVERYMAN/p1: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5017 · **命中分=8**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface elements shared; news focuses on EU regulatory fines for Google's search practices, while film is a crime comedy about police deception in Marseilles, with no concrete or thematic overlap.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 12 -->
### Nothing to Declare (2010) [THE-EXPLORER, THE-CREATOR] [优质·多agent]
- **tmdb_id**: 52077
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5544
- **genres** / **language**: Comedy / fr
- **overview**: During the elimination of the Belgian/French border in the 90s, a Belgian customs officer is forced to team up with one of his French counterparts.
- **跳转**: https://themoviecosmos.com/movie/52077
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/n1: fragments=[how-1, how-0, why-1, result-0, who-0] · sim=0.4830
  - THE-CREATOR/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5544 · **命中分=7**
- **pseudo命中分合计**: 12
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor exists; news involves EU fines on Google for self-preferencing, while film centers on customs officers cooperating after border elimination, with no shared concrete elements. Structural skeletons are not isomorphic; themes of antitrust enforcement and regulatory power in news do not align with themes of personal rivalry and collaboration in film. An unrelated news could explain the film equally, as the film's narrative does not depend on specific elements from this news.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 12 -->
### Speaking of Murder (1957) [THE-OUTLAW, THE-JESTER]
- **tmdb_id**: 58926
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5422
- **genres** / **language**: Crime, Drama, Thriller / fr
- **overview**: Louis Bertain is the owner of a Paris garage which is the front for a robbery gang. He and his accomplices are careful to keep up a civic veneer by day, indulging in criminal activities only when "the red light is on" at night. This status quo is upset when one of the gang members becomes convinced that Louis' younger brother is a police informer.
- **跳转**: https://themoviecosmos.com/movie/58926
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p1: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.5244 · **命中分=5**
  - THE-JESTER/p1: fragments=[how-0, how-1, how-2, how-3, why-0, result-0, result-1] · sim=0.5422 · **命中分=7**
- **pseudo命中分合计**: 12
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor; thematic overlap (e.g., abuse of power, façade) is incidental and not isomorphic in skeleton, as news involves external regulatory action while film centers on internal betrayal; an unrelated news could explain the film equally.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 12 -->
### The Cat (1988) [THE-RULER, THE-LOVER] [优质·多agent]
- **tmdb_id**: 148866
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.4622
- **genres** / **language**: Thriller, Crime / de
- **overview**: Two bank robbers hold the clerks hostage and demand 3 million German marks as ransom. What the police do not realize is that the true criminal mastermind watches them from outside the bank, anticipating every move.
- **跳转**: https://themoviecosmos.com/movie/148866
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/n1: fragments=[result-0, who-0, how-1, how-2, why-0] · sim=0.4580
  - THE-LOVER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4622 · **命中分=7**
- **pseudo命中分合计**: 12
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The news involves corporate antitrust fines in digital markets, while the film is a physical bank robbery crime thriller. No load-bearing shared concrete elements exist, and the structural skeletons are not isomorphic—the news focuses on regulatory enforcement against a corporation, whereas the film centers on a hostage situation with a hidden mastermind. An unrelated news about a heist or police standoff would explain the film equally well.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 12 -->
### Your Lucky Day (2023) [THE-LOVER, THE-JESTER]
- **tmdb_id**: 923993
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5134
- **genres** / **language**: Thriller, Crime, Action / en
- **overview**: After a dispute over a winning lottery ticket turns into a deadly hostage situation, the witnesses must decide exactly how far they’ll go—and how much blood they’re willing to spill—for a cut of the $156 million.
- **跳转**: https://themoviecosmos.com/movie/923993
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/n1: fragments=[result-1, result-0, who-1, who-2, why-0] · sim=0.3995
  - THE-JESTER/p2: fragments=[how-0, how-1, how-2, how-3, why-0, result-0, result-1] · sim=0.5134 · **命中分=7**
- **pseudo命中分合计**: 12
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: Shared 'large money' element is incidental; no concrete surface anchor (e.g., lottery vs. fine) and no structural isomorphism in power/fate/theme skeleton. Unrelated news could equally explain the film.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 9 -->
### To Skin a Spy (1966) [THE-MAGICIAN, THE-CAREGIVER] [优质·多agent]
- **tmdb_id**: 82098
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5027
- **genres** / **language**: Thriller / fr
- **overview**: A French secret agent gets a license to kill when he is sent to Vienna to plug a security leak in this routine spy saga. He is caught in the crossfire of international enemy agents trying to eliminate the French.
- **跳转**: https://themoviecosmos.com/movie/82098
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/n1: fragments=[who-0, how-0, why-0, how-1, who-1] · sim=0.4395
  - THE-CAREGIVER/p2: fragments=[why-0, how-0, how-1, result-1] · sim=0.5027 · **命中分=4**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchors (e.g., Google, fines, search engines vs. spies, Vienna) and no structural isomorphism; news is corporate regulatory conflict, film is generic espionage plot. Incidental word overlap (e.g., 'leak') is not load-bearing, and unrelated news could explain the film equally.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### Giovannona Long-Thigh (1973) [THE-INNOCENT, THE-CAREGIVER]
- **tmdb_id**: 121342
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5171
- **genres** / **language**: Comedy / it
- **overview**: When a judge shuts down a high profile cheese factory for violating pollution standards, the owner bribes a monsignor to fix the problem. After they discover the judge has a predilection for married women, the owner employs a prostitute to pose as his wife in an attempt to seduce the judge.
- **跳转**: https://themoviecosmos.com/movie/121342
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, how-1, result-0] · sim=0.4669 · **命中分=3**
  - THE-CAREGIVER/p2: fragments=[why-0, how-0, how-1, result-1] · sim=0.5171 · **命中分=4**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing shared concrete elements (e.g., EU/Google vs. judge/cheese factory) and structural skeletons are not isomorphic; news focuses on regulatory fines for corporate self-preferencing, while film centers on personal corruption via seduction and bribery, with no deep thematic alignment.

### 单 agent 命中

**Count:** 5 candidate(s)

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 10 -->
### The Last One of the Six (1941) [THE-SAGE]
- **tmdb_id**: 142977
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5277
- **genres** / **language**: Drama, Mystery, Thriller / fr
- **overview**: Paris, France. Commissaire Wens is put in charge of the investigation into the murder of one of six friends who, in the past, made a very profitable promise.
- **跳转**: https://themoviecosmos.com/movie/142977
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-SAGE/p1: fragments=[how-0, why-0, how-1, result-0, result-1] · sim=0.4997 · **命中分=5**
  - THE-SAGE/p3: fragments=[how-0, why-0, how-1, how-2, how-3] · sim=0.5277 · **命中分=5**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface elements (e.g., news involves corporate fines for search self-preferencing; film involves murder investigation from a past promise). Structural skeletons differ: regulatory antitrust action vs. personal crime drama with no isomorphic power/fate/theme.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 10 -->
### The Cost of Deception (2021) [THE-SAGE]
- **tmdb_id**: 876671
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5179
- **genres** / **language**: Crime, Drama / hu
- **overview**: When a young, ambitious market researcher finds out her boss is involved in the leaking of a scandalous Prime Minister speech, she decides to investigate the case to gain a position among the big-shots. Based on actual events.
- **跳转**: https://themoviecosmos.com/movie/876671
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-SAGE/p1: fragments=[how-0, why-0, how-1, result-0, result-1] · sim=0.5123 · **命中分=5**
  - THE-SAGE/p3: fragments=[how-0, why-0, how-1, how-2, how-3] · sim=0.5179 · **命中分=5**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor (news: antitrust fine for search self-preferencing; film: investigation of political scandal leak) and skeleton not isomorphic (themes of deception incidental without specific power/fate match).

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### Dead Weight (2002) [THE-JESTER]
- **tmdb_id**: 18457
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5239
- **genres** / **language**: Comedy / fr
- **overview**: After winning the lottery, a convict must chase down the warden who has his winning ticket.
- **跳转**: https://themoviecosmos.com/movie/18457
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p2: fragments=[how-0, how-1, how-2, how-3, why-0, result-0, result-1] · sim=0.5239 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing shared concrete elements: news involves EU regulatory fine for corporate self-preferencing, film centers on a personal chase for a lottery ticket. Skeletons are not isomorphic; news themes focus on systemic regulation and corporate accountability, while film themes revolve around individual fate and pursuit.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 6 -->
### The Prison (2017) [THE-EXPLORER]
- **tmdb_id**: 438798
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5132
- **genres** / **language**: Crime, Action / ko
- **overview**: An imprisoned ex-police inspector discovers that the entire penitentiary is controlled by an inmate running a crime syndicate and becomes part of the crime empire.
- **跳转**: https://themoviecosmos.com/movie/438798
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p1: fragments=[how-0, how-1, how-2, how-3, why-0, result-1] · sim=0.5132 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface elements shared; structural skeletons not isomorphic—news centers on regulatory action against corporate self-preferencing, while film involves a protagonist integrating into a prison crime empire, with divergent themes and power outcomes.

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### Stolen: Heist of the Century (2025) [THE-OUTLAW]
- **tmdb_id**: 1513598
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5311
- **genres** / **language**: Documentary, Crime / en
- **overview**: Antwerp, 2003. A gang of thieves rob the impenetrable Diamond Center. Who was behind one of the world's biggest heists - and how did they pull it off?
- **跳转**: https://themoviecosmos.com/movie/1513598
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p1: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.5311 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing shared concrete elements (news is about EU regulatory fine on Google for digital market practices, film is about a diamond heist in Antwerp); no structural isomorphism (themes of corporate competition vs. criminal robbery are not analogous, and an unrelated news about any crime could equally explain the film).

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

**Count:** 9 candidate(s)

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 102 -->
### Transpecos (2016) [THE-HERO, THE-CREATOR, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-JESTER, THE-INNOCENT, THE-CAREGIVER, THE-EXPLORER, THE-LOVER, THE-EVERYMAN, THE-OUTLAW] [优质·多agent]
- **tmdb_id**: 381018
- **quality_candidate**: true
- **neutral_hits**: 6
- **neutral_total**: 12
- **neutral_hit_rate**: 0.5000
- **distinct_agents**: 12
- **优质候选**: true
- **distinct_agents**: 12
- **相似度**: 0.6127
- **genres** / **language**: Thriller / en
- **overview**: For three US Border Patrol agents, the contents of one car reveal an insidious plot within their own ranks. The next 24 hours may cost them their lives.
- **跳转**: https://themoviecosmos.com/movie/381018
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/n1: fragments=[who-0, result-0, how-0, why-0, result-1] · sim=0.5594
  - THE-CREATOR/n1: fragments=[how-0, result-1, who-0, result-0, who-1] · sim=0.5198
  - THE-RULER/n1: fragments=[result-0, who-0, how-0, result-1, why-0] · sim=0.5565
  - THE-MAGICIAN/n1: fragments=[result-0, how-0, result-1, why-0, who-0] · sim=0.5037
  - THE-SAGE/n1: fragments=[result-0, how-0, who-2, result-1, why-0] · sim=0.4899
  - THE-JESTER/n1: fragments=[result-1, who-3, how-0, result-0, who-0] · sim=0.5496
  - THE-INNOCENT/p1: fragments=[why-0, how-0, result-0] · sim=0.4341 · **命中分=3**
  - THE-HERO/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4777 · **命中分=4**
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5398 · **命中分=4**
  - THE-EXPLORER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5340 · **命中分=4**
  - THE-LOVER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5722 · **命中分=4**
  - THE-CREATOR/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5506 · **命中分=4**
  - THE-RULER/p1: fragments=[why-0, how-0, result-0] · sim=0.5434 · **命中分=3**
  - THE-MAGICIAN/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4702 · **命中分=4**
  - THE-SAGE/p1: fragments=[why-0, how-0, result-0] · sim=0.5100 · **命中分=3**
  - THE-JESTER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4989 · **命中分=4**
  - THE-EVERYMAN/p2: fragments=[how-0, why-0, result-0, result-1] · sim=0.6127 · **命中分=4**
  - THE-HERO/p2: fragments=[why-0, how-0, result-0, result-1] · sim=0.4784 · **命中分=4**
  - THE-CAREGIVER/p2: fragments=[why-0, how-0, result-1] · sim=0.5660 · **命中分=3**
  - THE-OUTLAW/p2: fragments=[how-0, result-0, result-1] · sim=0.4653 · **命中分=3**
  - THE-LOVER/p2: fragments=[why-0, how-0, result-0, result-1] · sim=0.5208 · **命中分=4**
  - THE-MAGICIAN/p2: fragments=[how-0, result-0, result-1] · sim=0.5233 · **命中分=3**
  - THE-JESTER/p2: fragments=[how-0, result-0, result-1] · sim=0.5157 · **命中分=3**
  - THE-EVERYMAN/p3: fragments=[why-0, how-0, result-0, result-1] · sim=0.5130 · **命中分=4**
  - THE-OUTLAW/p3: fragments=[result-0, how-0, result-1] · sim=0.5112 · **命中分=3**
  - THE-LOVER/p3: fragments=[why-0, how-0, result-0, result-1] · sim=0.5030 · **命中分=4**
- **pseudo命中分合计**: 102
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge采信**: 不采信 · screening only
- **judge理由**: Shared Border Patrol setting is a load-bearing surface anchor, but the news focuses on external migration statistics and policy, while the film's plot revolves around internal corruption and personal danger, lacking structural isomorphism.

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 59 -->
### Open the Wall (2014) [THE-HERO, THE-EXPLORER, THE-CREATOR, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-LOVER, THE-EVERYMAN, THE-JESTER, THE-OUTLAW] [优质·多agent]
- **tmdb_id**: 301633
- **quality_candidate**: true
- **neutral_hits**: 6
- **neutral_total**: 12
- **neutral_hit_rate**: 0.5000
- **distinct_agents**: 6
- **优质候选**: true
- **distinct_agents**: 6
- **相似度**: 0.5899
- **genres** / **language**: Drama, Comedy / de
- **overview**: A lighthearted look at the opening of the border crossing of Bornholmer Straße in Berlin from the point of view of the confused border guards.
- **跳转**: https://themoviecosmos.com/movie/301633
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/n1: fragments=[who-0, result-0, how-0, why-0, result-1] · sim=0.5100
  - THE-EXPLORER/n1: fragments=[where-0, who-1, how-0, result-0, why-0] · sim=0.4725
  - THE-CREATOR/n1: fragments=[how-0, result-1, who-0, result-0, who-1] · sim=0.4550
  - THE-RULER/n1: fragments=[result-0, who-0, how-0, result-1, why-0] · sim=0.5166
  - THE-MAGICIAN/n1: fragments=[result-0, how-0, result-1, why-0, who-0] · sim=0.4892
  - THE-SAGE/n1: fragments=[result-0, how-0, who-2, result-1, why-0] · sim=0.4921
  - THE-LOVER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5899 · **命中分=4**
  - THE-RULER/p1: fragments=[why-0, how-0, result-0] · sim=0.4958 · **命中分=3**
  - THE-EVERYMAN/p2: fragments=[how-0, why-0, result-0, result-1] · sim=0.5612 · **命中分=4**
  - THE-LOVER/p2: fragments=[why-0, how-0, result-0, result-1] · sim=0.5462 · **命中分=4**
  - THE-JESTER/p2: fragments=[how-0, result-0, result-1] · sim=0.5213 · **命中分=3**
  - THE-EVERYMAN/p3: fragments=[why-0, how-0, result-0, result-1] · sim=0.5024 · **命中分=4**
  - THE-HERO/p3: fragments=[why-0, how-0, result-0, result-1] · sim=0.5272 · **命中分=4**
  - THE-OUTLAW/p3: fragments=[result-0, how-0, result-1] · sim=0.4605 · **命中分=3**
- **pseudo命中分合计**: 59
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: Shared border theme is incidental; news focuses on U.S. enforcement and apprehensions, while film depicts Berlin Wall opening lightheartedly. No load-bearing surface anchor or structural isomorphism.

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 33 -->
### If It's Tuesday, This Must Be Belgium (1969) [THE-INNOCENT, THE-EVERYMAN, THE-CAREGIVER, THE-OUTLAW, THE-LOVER, THE-EXPLORER] [优质·多agent]
- **tmdb_id**: 11643
- **quality_candidate**: true
- **neutral_hits**: 5
- **neutral_total**: 12
- **neutral_hit_rate**: 0.4167
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5129
- **genres** / **language**: Romance, Comedy, Adventure / en
- **overview**: A group of travelers from the United States race through seven European countries in 18 days.
- **跳转**: https://themoviecosmos.com/movie/11643
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[who-1, result-0, how-0, result-1, why-0] · sim=0.4820
  - THE-EVERYMAN/n1: fragments=[who-1, result-0, how-0, result-1, who-0] · sim=0.4896
  - THE-CAREGIVER/n1: fragments=[who-1, result-0, how-0, result-1, why-0] · sim=0.4920
  - THE-OUTLAW/n1: fragments=[who-1, result-0, how-0, result-1, who-0] · sim=0.4935
  - THE-LOVER/n1: fragments=[who-1, result-0, how-0, why-0, result-1] · sim=0.4822
  - THE-EVERYMAN/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4409 · **命中分=4**
  - THE-EXPLORER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5129 · **命中分=4**
- **pseudo命中分合计**: 33
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: News focuses on U.S. border immigration enforcement and seasonal migration, while film depicts European tourism and travel; no load-bearing surface anchors or structural isomorphism in themes or power dynamics.

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 27 -->
### Trade (2007) [THE-INNOCENT, THE-EVERYMAN, THE-EXPLORER, THE-OUTLAW, THE-CAREGIVER, THE-SAGE] [优质·多agent]
- **tmdb_id**: 4170
- **quality_candidate**: true
- **neutral_hits**: 4
- **neutral_total**: 12
- **neutral_hit_rate**: 0.3333
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5527
- **genres** / **language**: Thriller / en
- **overview**: A Texas cop, whose own daughter might have been forced into sexual slavery, joins forces with a Mexican youth to find the boy's sister, who was abducted and forced into prostitution. Meanwhile, a Polish woman who was promised a better life in America also becomes a victim.
- **跳转**: https://themoviecosmos.com/movie/4170
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[who-1, result-0, how-0, result-1, why-0] · sim=0.4853
  - THE-EVERYMAN/n1: fragments=[who-1, result-0, how-0, result-1, who-0] · sim=0.5113
  - THE-EXPLORER/n1: fragments=[where-0, who-1, how-0, result-0, why-0] · sim=0.4595
  - THE-OUTLAW/n1: fragments=[who-1, result-0, how-0, result-1, who-0] · sim=0.5133
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5389 · **命中分=4**
  - THE-SAGE/p1: fragments=[why-0, how-0, result-0] · sim=0.5527 · **命中分=3**
- **pseudo命中分合计**: 27
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge采信**: 不采信 · screening only
- **judge理由**: Both share concrete elements like the U.S.-Mexico border and immigration enforcement, but the news is about policy and seasonal migration patterns, while the film focuses on human trafficking and personal rescue narratives, with no isomorphic power/fate/theme skeleton.

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 11 -->
### Sicario (2015) [THE-JESTER, THE-INNOCENT, THE-CAREGIVER] [优质·多agent]
- **tmdb_id**: 273481
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5539
- **genres** / **language**: Action, Crime, Thriller / en
- **overview**: An idealistic FBI agent is enlisted by a government task force to aid in the escalating war against drugs at the border area between the U.S. and Mexico.
- **跳转**: https://themoviecosmos.com/movie/273481
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/n1: fragments=[result-1, who-3, how-0, result-0, who-0] · sim=0.4465
  - THE-INNOCENT/p2: fragments=[why-0, result-0, result-1] · sim=0.5539 · **命中分=3**
  - THE-CAREGIVER/p2: fragments=[why-0, how-0, result-1] · sim=0.5524 · **命中分=3**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The news discusses border apprehensions related to migration, while the film Sicario focuses on the drug war at the border. No load-bearing surface anchor exists as the core concrete elements differ, and the structural skeletons are not isomorphic; an unrelated news about drug enforcement would equally explain the film, triggering the 0-guard.

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 10 -->
### Chariot (2013) [THE-CAREGIVER, THE-LOVER]
- **tmdb_id**: 252990
- **quality_candidate**: false
- **neutral_hits**: 2
- **neutral_total**: 12
- **neutral_hit_rate**: 0.1667
- **distinct_agents**: 0
- **优质候选**: false
- **distinct_agents**: 0
- **相似度**: 0.4862
- **genres** / **language**: Thriller, Drama / en
- **overview**: Seven strangers find themselves unwitting participants in a U.S. government evacuation program gone horribly wrong.
- **跳转**: https://themoviecosmos.com/movie/252990
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/n1: fragments=[who-1, result-0, how-0, result-1, why-0] · sim=0.4862
  - THE-LOVER/n1: fragments=[who-1, result-0, how-0, why-0, result-1] · sim=0.4773
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor; the shared element of U.S. government involvement is too broad and not concrete enough to be load-bearing. Structural themes do not show strong isomorphism: the news focuses on immigration enforcement and seasonal factors, while the film's evacuation program is generic and could be explained by unrelated government programs, triggering the 0-guard.

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 9 -->
### Union Pacific (1939) [THE-JESTER, THE-INNOCENT, THE-RULER]
- **tmdb_id**: 43837
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5088
- **genres** / **language**: Drama, Western / en
- **overview**: One of the last bills signed by President Lincoln authorizes pushing the Union Pacific Railroad across the wilderness to California. But financial opportunist Asa Barrows hopes to profit from obstructing it. Chief troubleshooter Jeff Butler has his hands full fighting Barrows' agent, gambler Sid Campeau; Campeau's partner Dick Allen is Jeff's war buddy and rival suitor for engineer's daughter Molly Monahan. Who will survive the effort to push the railroad through at any cost?
- **跳转**: https://themoviecosmos.com/movie/43837
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4502 · **命中分=4**
  - THE-INNOCENT/p2: fragments=[why-0, result-0, result-1] · sim=0.4856 · **命中分=3**
  - THE-RULER/p3: fragments=[how-0, result-1] · sim=0.5088 · **命中分=2**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: News focuses on border enforcement and migration, while film centers on railroad construction and personal rivalries; no shared concrete element or thematic skeleton isomorphism.

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 8 -->
### Stranded (2021) [THE-HERO, THE-CREATOR]
- **tmdb_id**: 841793
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.4840
- **genres** / **language**: Drama / pt
- **overview**: Tensions run high while food runs low as six influencers find themselves stranded on a secluded island after plans for a weekend escape go awry.
- **跳转**: https://themoviecosmos.com/movie/841793
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4840 · **命中分=4**
  - THE-CREATOR/p2: fragments=[why-0, how-0, result-0, result-1] · sim=0.4666 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor (concrete elements differ: border apprehensions vs. influencers stranded on an island) and no structural isomorphism (thematic skeletons do not align; news focuses on policy and seasonal migration, film on survival and group tension in isolation).

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 7 -->
### Scare Out (2026) [THE-HERO, THE-SAGE]
- **tmdb_id**: 1447971
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5505
- **genres** / **language**: Crime, Thriller, Action / zh
- **overview**: After a critical intelligence leak, a national security unit launches an intensive investigation. But successive setbacks in their arrest operations reveal a shocking truth: the trail leads back to within the unit itself. Amidst a storm of trust and betrayal, a silent battle begins to unfold...
- **跳转**: https://themoviecosmos.com/movie/1447971
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p3: fragments=[why-0, how-0, result-0, result-1] · sim=0.5505 · **命中分=4**
  - THE-SAGE/p3: fragments=[result-1, how-0, result-0] · sim=0.5000 · **命中分=3**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor: news details border apprehensions and political deadlock, film focuses on intelligence leak and internal betrayal, with no concrete shared elements. Structural isomorphism absent: news themes are external migration and policy analysis, film themes are internal trust and betrayal, not skeleton isomorphic. Unrelated news could equally explain the film.

### 单 agent 命中

**Count:** 1 candidate(s)

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 8 -->
### Colosio (2012) [THE-MAGICIAN]
- **tmdb_id**: 151708
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4862
- **genres** / **language**: Crime, Drama, Thriller / es
- **overview**: It's 1994 in Mexico, the nation was witnessing a turbulent year since its beginnings. An indigenous rebellion shakes the country. Three months later, the ruling party's presidential candidate is brutally murdered during a rally in Tijuana. The country is concerned. Nobody knows who's behind this event, it all points to a conspiracy. Andrés Vázquez, an intelligence expert, is commissioned to lead a secret investigation parallel to the official government issued one. But another expert agent, el Seco, has received orders to wipe out all witnesses and get rid of the evidence surrounding the candidate's murder. As Andrés begins putting the pieces of this intricate puzzle together and comes closer to the truth, he realizes he's also putting his life and that of his loved ones in peril.
- **跳转**: https://themoviecosmos.com/movie/151708
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4181 · **命中分=4**
  - THE-MAGICIAN/p3: fragments=[why-0, how-0, result-0, result-1] · sim=0.4862 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The news concerns U.S. border enforcement and migration patterns, while the film depicts a political assassination and conspiracy in 1994 Mexico. There is no load-bearing surface anchor shared, and the structural skeletons differ: the news is about policy and seasonal factors, whereas the film is about crime and investigation. An unrelated border news could equally explain the film's context without core resonance.

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

**Count:** 11 candidate(s)

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 90 -->
### Hurricane Season (2010) [THE-INNOCENT, THE-EVERYMAN, THE-CAREGIVER, THE-OUTLAW, THE-RULER, THE-SAGE, THE-JESTER, THE-EXPLORER, THE-LOVER, THE-MAGICIAN, THE-CREATOR] [优质·多agent]
- **tmdb_id**: 32007
- **quality_candidate**: true
- **neutral_hits**: 7
- **neutral_total**: 12
- **neutral_hit_rate**: 0.5833
- **distinct_agents**: 8
- **优质候选**: true
- **distinct_agents**: 8
- **相似度**: 0.5929
- **genres** / **language**: Drama / en
- **overview**: Based on true events amid the wreckage and chaos dealt by Hurricane Katrina; one basketball coach in Marrero, Louisiana just will not give up. Coach Al Collins, gathers other players from hard-hit schools and builds a team actually worthy enough to go to the state playoffs.
- **跳转**: https://themoviecosmos.com/movie/32007
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[who-2, why-0, who-3, who-4, result-0] · sim=0.4637
  - THE-EVERYMAN/n1: fragments=[result-0, who-0, who-1, why-0, how-0] · sim=0.4951
  - THE-CAREGIVER/n1: fragments=[why-0, who-1, who-3, who-4, result-0] · sim=0.4274
  - THE-OUTLAW/n1: fragments=[how-0, result-0, who-0, why-0, how-1] · sim=0.5263
  - THE-RULER/n1: fragments=[result-0, how-0, who-0, why-0, how-1] · sim=0.5300
  - THE-SAGE/n1: fragments=[why-0, how-0, how-3, result-0, how-1] · sim=0.5404
  - THE-JESTER/n1: fragments=[how-0, who-2, who-1, why-0, how-1] · sim=0.4980
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5685 · **命中分=7**
  - THE-EXPLORER/p1: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5224 · **命中分=6**
  - THE-OUTLAW/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5339 · **命中分=7**
  - THE-LOVER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5929 · **命中分=7**
  - THE-MAGICIAN/p1: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.4559 · **命中分=6**
  - THE-SAGE/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0] · sim=0.5450 · **命中分=6**
  - THE-RULER/p2: fragments=[how-3, how-4, result-0] · sim=0.4306 · **命中分=3**
  - THE-LOVER/p3: fragments=[why-0, how-4, result-0] · sim=0.5363 · **命中分=3**
  - THE-CREATOR/p3: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5027 · **命中分=6**
  - THE-RULER/p3: fragments=[why-0, how-3, how-4, result-0] · sim=0.5537 · **命中分=4**
- **pseudo命中分合计**: 90
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives share a structural skeleton of an underdog sports team guided by a coach to playoff success despite significant adversity (injuries/coaching change vs. natural disaster), but lack load-bearing surface anchors due to different sports contexts and specific concrete elements.

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 36 -->
### Hoosiers (1986) [THE-OUTLAW, THE-CREATOR, THE-MAGICIAN, THE-JESTER, THE-INNOCENT, THE-CAREGIVER] [优质·多agent]
- **tmdb_id**: 5693
- **quality_candidate**: true
- **neutral_hits**: 4
- **neutral_total**: 12
- **neutral_hit_rate**: 0.3333
- **distinct_agents**: 3
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.5905
- **genres** / **language**: Drama, Family / en
- **overview**: Failed college coach Norman Dale gets a chance at redemption when he is hired to coach a high school basketball team in a tiny Indiana town. After a teacher persuades star player Jimmy Chitwood to quit and focus on his long-neglected studies, Dale struggles to develop a winning team in the face of community criticism for his temper and his unconventional choice of assistant coach: Shooter, a notorious alcoholic.
- **跳转**: https://themoviecosmos.com/movie/5693
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/n1: fragments=[how-0, result-0, who-0, why-0, how-1] · sim=0.4940
  - THE-CREATOR/n1: fragments=[how-0, how-1, how-2, result-0, who-0] · sim=0.4973
  - THE-MAGICIAN/n1: fragments=[how-0, how-1, how-2, result-0, who-2] · sim=0.5146
  - THE-JESTER/n1: fragments=[how-0, who-2, who-1, why-0, how-1] · sim=0.4899
  - THE-INNOCENT/p2: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5716 · **命中分=6**
  - THE-CAREGIVER/p2: fragments=[why-0, how-0, how-1, how-2, how-3, how-4] · sim=0.5905 · **命中分=6**
  - THE-OUTLAW/p2: fragments=[how-0, how-1, how-2, why-0] · sim=0.5822 · **命中分=4**
- **pseudo命中分合计**: 36
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives share a thematic skeleton of underdog triumph through coaching redemption, with structural isomorphism in power/fate themes, but lack load-bearing surface anchors due to differences in sport and specific concrete elements.

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 20 -->
### A Match Revenge (1968) [THE-INNOCENT, THE-EVERYMAN, THE-CAREGIVER]
- **tmdb_id**: 248555
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5871
- **genres** / **language**: Animation / ru
- **overview**: Ice team is fighting hard. We believe in the courage of the desperate guys. Real men play hockey. Coward does not play hockey.
- **跳转**: https://themoviecosmos.com/movie/248555
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5871 · **命中分=7**
  - THE-EVERYMAN/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5400 · **命中分=7**
  - THE-CAREGIVER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4] · sim=0.5589 · **命中分=6**
- **pseudo命中分合计**: 20
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge采信**: 不采信 · screening only
- **judge理由**: Hockey is a load-bearing shared concrete element, as both narratives center on ice hockey teams. However, the news's specific plot about a playoff sweep and overcoming injuries lacks clear isomorphism with the film's vague themes of courage and desperation, preventing structural resonance.

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 17 -->
### In Which We Serve (1942) [THE-CREATOR, THE-HERO, THE-OUTLAW]
- **tmdb_id**: 28093
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.6220
- **genres** / **language**: Drama, War / en
- **overview**: The story of the HMS Torrin, from its construction to its sinking in the Mediterranean during action in World War II. The ship’s first and only commanding officer is Captain E.V. Kinross, who trains his men not only to be loyal to him and the country, but—most importantly—to themselves.
- **跳转**: https://themoviecosmos.com/movie/28093
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.4923 · **命中分=7**
  - THE-HERO/p2: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.6220 · **命中分=6**
  - THE-OUTLAW/p2: fragments=[how-0, how-1, how-2, why-0] · sim=0.5610 · **命中分=4**
- **pseudo命中分合计**: 17
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing shared concrete elements between hockey playoffs and WWII warship narrative; thematic overlap is incidental and not isomorphic, as an unrelated news could equally explain the film.

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 17 -->
### Three Seconds (2017) [THE-RULER, THE-EVERYMAN, THE-MAGICIAN] [优质·多agent]
- **tmdb_id**: 444218
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5215
- **genres** / **language**: Drama / ru
- **overview**: The story is set at the 1972 Munich Olympics where the U.S. team lost the basketball championship for the first time in 36 years. The final moments of the final game have become one of the most controversial events in Olympic history. With play tied, the score table horn sounded during a second free throw attempt that put the U.S. ahead by one. But the Soviets claimed they had called for a time out before the basket and confusion ensued. The clock was set back by three seconds twice in a row and the Russians finally prevailed at the very last. The U.S. protested, but a jury decided in the USSR’s favor and Team USA voted unanimously to refuse its silver medals. The Soviet players have been treated as heroes at home.
- **跳转**: https://themoviecosmos.com/movie/444218
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/n1: fragments=[result-0, how-0, who-0, why-0, how-1] · sim=0.5038
  - THE-EVERYMAN/p3: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5215 · **命中分=6**
  - THE-MAGICIAN/p3: fragments=[why-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5102 · **命中分=6**
- **pseudo命中分合计**: 17
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both stories share a structural isomorphism: favored teams (Avalanche in hockey, U.S. in basketball) experience unexpected defeats due to external factors (injuries/coach change vs. time controversy/jury decision), emphasizing themes of fate and upset in competitive sports. No load-bearing surface anchor exists as concrete elements differ.

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 15 -->
### One Piece: Dream Soccer King! (2002) [THE-EXPLORER, THE-JESTER, THE-EVERYMAN] [优质·多agent]
- **tmdb_id**: 464198
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5398
- **genres** / **language**: Fantasy, Comedy, Animation / ja
- **overview**: At a huge pillar stadium, the Grand Line Cup Final is being held. The "Straw Hat Pirate Team"(Luffy, Zoro, Usopp, Sanji, and Chopper) are having a tie breaker shoot out against the "Villian All Star Team"(Buggy, Bon Clay, Jango, Hatchan, and a soccer like head player named Odacchi). Everyone of them gets a turn in kicking the ball to the goal. While Coby is taking the goalie position, and isn't doing too good in blocking the goal. One after another, the game eventually comes to a sudden death match. Which team will win the Grand Line Cup?
- **跳转**: https://themoviecosmos.com/movie/464198
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/n1: fragments=[how-4, how-1, how-2, who-0, result-0] · sim=0.4694
  - THE-JESTER/p2: fragments=[why-0, how-3, how-4, result-0] · sim=0.5124 · **命中分=4**
  - THE-EVERYMAN/p3: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5398 · **命中分=6**
- **pseudo命中分合计**: 15
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor or structural isomorphism; both involve a sports final, but this is generic overlap, and an unrelated sports news could explain the film equally.

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 13 -->
### The Two Wizards of the Ball (1970) [THE-EVERYMAN, THE-MAGICIAN]
- **tmdb_id**: 41612
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5822
- **genres** / **language**: Comedy / it
- **overview**: The manager of a football team wants to hire a coach. Luckily the team begin to win but on the eve of an important match the opposing team has their best scorer kidnapped. Will they win the match all the same?
- **跳转**: https://themoviecosmos.com/movie/41612
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p2: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5822 · **命中分=6**
  - THE-MAGICIAN/p2: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.4984 · **命中分=7**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge采信**: 不采信 · screening only
- **judge理由**: Both stories share a load-bearing surface anchor: a sports team facing the loss of a key player (injuries in news, kidnapping in film) that critically affects their performance. However, the structural skeletons are not isomorphic—the news involves a favored team's decline due to injuries and a sweep by an opponent, while the film focuses on overcoming direct sabotage, with differing power dynamics and fate trajectories.

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 12 -->
### Champions (2018) [THE-INNOCENT, THE-CAREGIVER]
- **tmdb_id**: 456929
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5666
- **genres** / **language**: Comedy, Family, Drama / es
- **overview**: A disgraced basketball coach is given the chance to coach Los Amigos, a team of players who are intellectually disabled, and soon realizes they just might have what it takes to make it to the national championships.
- **跳转**: https://themoviecosmos.com/movie/456929
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p2: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5666 · **命中分=6**
  - THE-CAREGIVER/p2: fragments=[why-0, how-0, how-1, how-2, how-3, how-4] · sim=0.5635 · **命中分=6**
- **pseudo命中分合计**: 12
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both stories share an isomorphic structural theme of a coach with a troubled past leading an underdog sports team to overcome odds and achieve or aim for high success, but lack specific load-bearing surface-level concrete elements due to differences in sports (hockey vs. basketball) and unique aspects like intellectual disability in the film.

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 11 -->
### Hockey Homicide (1945) [THE-EXPLORER, THE-CAREGIVER] [优质·多agent]
- **tmdb_id**: 66876
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5813
- **genres** / **language**: Animation, Comedy / en
- **overview**: A crowd gathers at the skating rink to watch the big championship hockey game of the Pelicans versus the Aardvarks. Although referee "Clean Game" Kinney does his best to supervise, the hockey game really gets out of hand eventually. Two star players, Bertino and Ferguson, are so anxious, they never get let out of the penalty box, referee Kinney is never able to drop the puck without being physically hurt somehow, and the spectators themselves are so worked into the game, they take out their aggression on the ice while the players relax in the bleachers.
- **跳转**: https://themoviecosmos.com/movie/66876
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/n1: fragments=[how-4, how-1, how-2, who-0, result-0] · sim=0.4404
  - THE-CAREGIVER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4] · sim=0.5813 · **命中分=6**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The shared hockey element is incidental and not load-bearing; the news narrative centers on competitive playoff success and team dynamics, while the film depicts chaotic, comedic disorder without structural isomorphism to power/fate themes.

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 11 -->
### When the Game Stands Tall (2014) [THE-MAGICIAN, THE-CREATOR] [优质·多agent]
- **tmdb_id**: 232679
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.4999
- **genres** / **language**: Drama / en
- **overview**: A young coach turns a losing high school football program around to go undefeated for 12 consecutive seasons.
- **跳转**: https://themoviecosmos.com/movie/232679
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/n1: fragments=[how-0, how-1, how-2, result-0, who-2] · sim=0.4999
  - THE-CREATOR/p3: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.4681 · **命中分=6**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor; incidental overlap in sports and coaching themes without specific shared elements. Structural skeletons differ: news involves playoff upset due to injuries, while film focuses on long-term transformation.

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 9 -->
### The World Champion (2021) [THE-HERO, THE-LOVER]
- **tmdb_id**: 589752
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5717
- **genres** / **language**: Drama / ru
- **overview**: Some sporting victories are about more than just claiming a title. Some of them go down in history. The film follows the most dramatic and legendary showdown in the history of chess – the match between Anatoly Karpov, then world champion, and Viktor Korchnoi, a recent emigrant from the USSR. In this battle between two outstanding chess players, a duel of personalities under immense psychological pressure, the stakes are incomprehensibly high.
- **跳转**: https://themoviecosmos.com/movie/589752
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[how-3, how-4, result-0] · sim=0.4773 · **命中分=3**
  - THE-LOVER/p2: fragments=[why-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5717 · **命中分=6**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor or structural isomorphism; incidental overlap in broad competition themes, and an unrelated sports underdog news could explain the film equally.

### 单 agent 命中

**Count:** 6 candidate(s)

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 7 -->
### Hang 'em High (1968) [THE-JESTER]
- **tmdb_id**: 4929
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5493
- **genres** / **language**: Western, Drama / en
- **overview**: Marshall Jed Cooper survives a hanging, vowing revenge on the lynch mob that left him dangling. To carry out his oath for vengeance, he returns to his former job as a lawman. Before long, he's caught up with the nine men on his hit list and starts dispensing his own brand of Wild West justice.
- **跳转**: https://themoviecosmos.com/movie/4929
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p3: fragments=[how-0, how-1, how-2, how-3, how-4, why-0, result-0] · sim=0.5493 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor (sports sweep vs. revenge plot) and structural skeletons not isomorphic (team overcoming odds vs. individual vengeance); incidental overlap only, fitting the 0-guard.

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### Run Silent, Run Deep (1958) [THE-HERO]
- **tmdb_id**: 18784
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5541
- **genres** / **language**: Drama, War / en
- **overview**: The captain of a submarine sunk by the Japanese during WWII is finally given a chance to skipper another sub after a year of working a desk job. His singleminded determination for revenge against the destroyer that sunk his previous vessel puts his new crew in unneccessary danger.
- **跳转**: https://themoviecosmos.com/movie/18784
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p2: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5541 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives share a structural skeleton where protagonists experience a defeat (coach firing/team setback; submarine sinking), gain a second chance, and pursue revenge or victory against formidable opponents (favored team; enemy destroyer), with themes of overcoming adversity and leadership.

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### Paterno (2018) [THE-RULER]
- **tmdb_id**: 467867
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5503
- **genres** / **language**: Drama, TV Movie / en
- **overview**: After becoming the winningest coach in college football history, Joe Paterno is embroiled in Penn State's Jerry Sandusky sexual abuse scandal, challenging his legacy and forcing him to face questions of institutional failure regarding the victims.
- **跳转**: https://themoviecosmos.com/movie/467867
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4] · sim=0.5503 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor: news focuses on hockey team success despite adversity, while film centers on a football coach's scandal and institutional failure, with no shared critical elements. Structural themes are not isomorphic: news is about triumph, film is about moral downfall.

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### Heart of Champions (2021) [THE-LOVER]
- **tmdb_id**: 647581
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5652
- **genres** / **language**: Drama / en
- **overview**: During their last year at an Ivy League college in 1999, a group of friends and crew teammates' lives are changed forever when an army vet takes over as coach of their dysfunctional rowing team.
- **跳转**: https://themoviecosmos.com/movie/647581
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p2: fragments=[why-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5652 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 双重
- **judge采信**: 不采信 · screening only
- **judge理由**: Both stories center on a transformative coach (Tortorella in news, army vet in film) taking over a struggling team, leading to a turnaround and success, sharing surface anchor and structural skeleton of team revival through leadership.

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### Sitaare Zameen Par (2025) [THE-RULER]
- **tmdb_id**: 1190511
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5757
- **genres** / **language**: Comedy, Drama / hi
- **overview**: A disgraced basketball coach is given the chance to coach a team of players who are intellectually disabled as part of community services. Gulshan has apprehensions at first and feels out of place but soon realizes they just might have what it takes to make it to the national championships.
- **跳转**: https://themoviecosmos.com/movie/1190511
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4] · sim=0.5757 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 双重
- **judge采信**: 不采信 · screening only
- **judge理由**: Both stories feature a disgraced coach who redeems themselves by leading an underdog team to championship success, with load-bearing surface elements of coach disgrace and underdog victory, and isomorphic structural themes of redemption and overcoming adversity.

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### Lady Ballers (2023) [THE-EVERYMAN]
- **tmdb_id**: 1210646
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5836
- **genres** / **language**: Comedy / en
- **overview**: A once-great basketball coach is on a journey back to victory by reuniting his former high school championship basketball team, but this time, he’s challenging them to play like girls.
- **跳转**: https://themoviecosmos.com/movie/1210646
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p2: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5836 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge采信**: 不采信 · screening only
- **judge理由**: Both stories center on a coach guiding a sports team to victory after setbacks (coaching change in news, reuniting team in film), providing a load-bearing surface anchor. However, the structural skeletons are not isomorphic: the news focuses on overcoming injuries and competitive sweeps, while the film emphasizes an unconventional 'play like girls' challenge, leading to thematic divergence.

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

**Count:** 10 candidate(s)

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 38 -->
### L'Odissea (1911) [THE-EXPLORER, THE-LOVER, THE-CREATOR, THE-MAGICIAN, THE-HERO] [优质·多agent]
- **tmdb_id**: 194224
- **quality_candidate**: true
- **neutral_hits**: 4
- **neutral_total**: 12
- **neutral_hit_rate**: 0.3333
- **distinct_agents**: 3
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.6737
- **genres** / **language**: Drama, Adventure / it
- **overview**: Film adaptation of Homer's 'The Odyssey.'
- **跳转**: https://themoviecosmos.com/movie/194224
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/n1: fragments=[how-0, how-3, result-0, who-1, why-1] · sim=0.6005
  - THE-LOVER/n1: fragments=[who-1, how-0, who-3, who-4, why-0] · sim=0.6359
  - THE-CREATOR/n1: fragments=[how-0, result-0, who-0, who-4, how-3] · sim=0.6175
  - THE-MAGICIAN/n1: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.6186
  - THE-HERO/p1: fragments=[how-0, how-1, how-2, how-3, why-0, why-1, result-0, result-1] · sim=0.5859 · **命中分=8**
  - THE-MAGICIAN/p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.5568 · **命中分=4**
  - THE-EXPLORER/p2: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.6737 · **命中分=6**
- **pseudo命中分合计**: 38
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge采信**: 不采信 · screening only
- **judge理由**: Both the news and film share a load-bearing surface anchor in being adaptations of Homer's Odyssey, but the news's culture-war theme over representation is not structurally isomorphic to the film's classical epic narrative.

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 26 -->
### Don't Leave Home (2018) [THE-INNOCENT, THE-EXPLORER, THE-MAGICIAN, THE-SAGE] [优质·多agent]
- **tmdb_id**: 502167
- **quality_candidate**: true
- **neutral_hits**: 3
- **neutral_total**: 12
- **neutral_hit_rate**: 0.2500
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5912
- **genres** / **language**: Thriller, Mystery / en
- **overview**: An American artist's obsession with a disturbing urban legend leads her to an investigation of the story's origins at the crumbling estate of a reclusive painter in Ireland.
- **跳转**: https://themoviecosmos.com/movie/502167
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[result-0, who-1, how-0, why-1, result-1] · sim=0.5842
  - THE-EXPLORER/n1: fragments=[how-0, how-3, result-0, who-1, why-1] · sim=0.5443
  - THE-MAGICIAN/n1: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.5912
  - THE-SAGE/p1: fragments=[how-0, how-1, how-2, why-0, result-0] · sim=0.5077 · **命中分=5**
  - THE-EXPLORER/p2: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5107 · **命中分=6**
- **pseudo命中分合计**: 26
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor or structural isomorphism; news centers on casting debates in classical mythology, while film focuses on obsession with an urban legend in art, with no directly shared elements that carry narrative weight.

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 23 -->
### Venus in Fur (2013) [THE-INNOCENT, THE-EVERYMAN, THE-CAREGIVER]
- **tmdb_id**: 197082
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.6585
- **genres** / **language**: Drama / fr
- **overview**: An enigmatic actress may have a hidden agenda when she auditions for a part in a misogynistic writer's play.
- **跳转**: https://themoviecosmos.com/movie/197082
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[how-0, how-1, how-2, how-3, why-0, result-0] · sim=0.6036 · **命中分=6**
  - THE-EVERYMAN/p1: fragments=[how-0, how-1, result-0] · sim=0.6585 · **命中分=3**
  - THE-CAREGIVER/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.6216 · **命中分=6**
  - THE-CAREGIVER/p3: fragments=[how-0, how-1, how-2, how-3, why-0, why-1, result-0, result-1] · sim=0.6009 · **命中分=8**
- **pseudo命中分合计**: 23
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge采信**: 不采信 · screening only
- **judge理由**: Both involve casting disputes in adaptations (news: film casting; film: play audition), providing a load-bearing surface anchor, but the structural themes diverge: news centers on cultural identity politics, while film focuses on personal power dynamics and gender manipulation.

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 19 -->
### Panama (2015) [THE-CAREGIVER, THE-HERO] [优质·多agent]
- **tmdb_id**: 336200
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5970
- **genres** / **language**: Thriller, Drama / sr
- **overview**: A thriller that depicts how digital communication, pornography and vanity obstruct true emotions and love.
- **跳转**: https://themoviecosmos.com/movie/336200
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/n1: fragments=[who-1, how-1, result-0, who-0, result-1] · sim=0.5941
  - THE-HERO/p2: fragments=[how-1, how-2, how-3, why-0, why-1, result-0, result-1] · sim=0.5682 · **命中分=7**
  - THE-CAREGIVER/p2: fragments=[how-0, how-1, how-2, why-0, why-1, result-0, result-1] · sim=0.5970 · **命中分=7**
- **pseudo命中分合计**: 19
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor: the news focuses on casting controversy and cultural identity in a mythic epic, while the film is a thriller about digital distractions and emotional barriers. No structural isomorphism: themes of representation and heritage do not align with themes of modern vices obstructing love.

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 19 -->
### Ex Libris: The New York Public Library (2017) [THE-HERO, THE-OUTLAW, THE-RULER, THE-MAGICIAN]
- **tmdb_id**: 446173
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.6205
- **genres** / **language**: Documentary / en
- **overview**: A documentary about how a dominant cultural and demographic institution both sustains their traditional activities and adapts to the digital revolution.
- **跳转**: https://themoviecosmos.com/movie/446173
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p2: fragments=[how-1, how-2, how-3, why-0, why-1, result-0, result-1] · sim=0.6033 · **命中分=7**
  - THE-OUTLAW/p2: fragments=[how-1, how-2, how-3, result-0] · sim=0.6205 · **命中分=4**
  - THE-RULER/p2: fragments=[why-0, why-1, how-1, result-0, result-1] · sim=0.5988 · **命中分=5**
  - THE-MAGICIAN/p2: fragments=[why-1, how-3, result-1] · sim=0.5566 · **命中分=3**
- **pseudo命中分合计**: 19
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor or structural isomorphism; the news is about film casting controversy and cultural identity, while the film is a documentary on institutional adaptation with only incidental thematic overlap.

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 15 -->
### Scandal (1950) [THE-EVERYMAN, THE-RULER] [优质·多agent]
- **tmdb_id**: 32690
- **quality_candidate**: true
- **neutral_hits**: 2
- **neutral_total**: 12
- **neutral_hit_rate**: 0.1667
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.6004
- **genres** / **language**: Drama / ja
- **overview**: A celebrity photograph sparks a court case as a tabloid magazine spins a scandalous yarn over a painter and a famous singer.
- **跳转**: https://themoviecosmos.com/movie/32690
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/n1: fragments=[result-0, who-1, who-4, how-1, why-0] · sim=0.5776
  - THE-RULER/n1: fragments=[result-0, who-0, how-1, why-0, result-1] · sim=0.5954
  - THE-RULER/p3: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.6004 · **命中分=5**
- **pseudo命中分合计**: 15
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor or structural isomorphism; news focuses on cultural identity in casting, while film involves a tabloid scandal and court case, with only incidental overlap in media controversy themes.

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 14 -->
### There Be Dragons (2011) [THE-HERO, THE-SAGE, THE-CREATOR] [优质·多agent]
- **tmdb_id**: 45054
- **quality_candidate**: true
- **neutral_hits**: 2
- **neutral_total**: 12
- **neutral_hit_rate**: 0.1667
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5332
- **genres** / **language**: War, History, Drama / en
- **overview**: Arising out of the horror of the Spanish Civil War, a candidate for canonization is investigated by a journalist who discovers his own estranged father had a deep, dark and devastating connection to the saint's life.While researching the life of Josemaria Escriva, the controversial founder of Opus Dei, the young journalist Robert uncovers hidden stories of his estranged father Manolo, and is taken on a journey through the dark, terrible secrets of his family’s past.
- **跳转**: https://themoviecosmos.com/movie/45054
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/n1: fragments=[who-3, result-0, how-3, why-1, how-1] · sim=0.5332
  - THE-SAGE/n1: fragments=[how-2, why-0, how-3, why-1, result-0] · sim=0.5015
  - THE-CREATOR/p2: fragments=[how-3, how-2, why-1, result-1] · sim=0.5151 · **命中分=4**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor (different subjects: casting controversy vs. historical religious drama) and no structural isomorphism (news focuses on cultural identity conflicts; film on personal and moral revelations); unrelated news could explain the film equally.

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 10 -->
### Sullivan's Travels (1941) [THE-CREATOR, THE-RULER] [优质·多agent]
- **tmdb_id**: 16305
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5940
- **genres** / **language**: Comedy, Romance, Adventure / en
- **overview**: Successful movie director John L. Sullivan, convinced he won't be able to film his ambitious masterpiece until he has suffered, dons a hobo disguise and sets off on a journey, aiming to "know trouble" first-hand. When all he finds is a train ride back to Hollywood and a beautiful blonde companion, he redoubles his efforts, managing to land himself in more trouble than he bargained for when he loses his memory and ends up a prisoner on a chain gang.
- **跳转**: https://themoviecosmos.com/movie/16305
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/n1: fragments=[how-0, result-0, who-0, who-4, how-3] · sim=0.5651
  - THE-RULER/p1: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.5940 · **命中分=5**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The news centers on cultural conflict over casting in a film adaptation, while the film depicts a director's personal journey for authenticity; no load-bearing surface elements or thematic skeleton isomorphism exists, and an unrelated news item could equally explain the film's themes.

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 10 -->
### Breakdown: 1975 (2025) [THE-JESTER, THE-MAGICIAN]
- **tmdb_id**: 1584125
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.6506
- **genres** / **language**: Documentary / en
- **overview**: In 1975, as America faced social and political upheaval, filmmakers turned chaos into art.
- **跳转**: https://themoviecosmos.com/movie/1584125
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p2: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.6422 · **命中分=6**
  - THE-MAGICIAN/p3: fragments=[why-0, how-1, result-0, result-1] · sim=0.6506 · **命中分=4**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor: news focuses on specific casting controversy and cultural debates in a film adaptation, while film candidate is broadly about filmmakers responding to 1975 societal upheaval. Structural themes (conflict and art) are present but not isomorphic in skeleton; an unrelated news about 1975 could equally explain the film.

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 9 -->
### The Phantom of the Opera (1989) [THE-LOVER, THE-MAGICIAN] [优质·多agent]
- **tmdb_id**: 86962
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5615
- **genres** / **language**: Horror, Romance / en
- **overview**: An aspiring opera singer finds herself transported back to Victorian-era London -- and into the arms of a reclusive, disfigured maestro determined to make her a star.
- **跳转**: https://themoviecosmos.com/movie/86962
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/n1: fragments=[who-1, how-0, who-3, who-4, why-0] · sim=0.5615
  - THE-MAGICIAN/p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.5596 · **命中分=4**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing shared concrete elements; news focuses on modern casting debates for a mythic epic, while film is a Victorian-era romantic drama. Structural skeletons are not isomorphic: news involves societal power over cultural identity, film centers on personal power in artistic obsession. Incidental thematic overlap only.

### 单 agent 命中

**Count:** 3 candidate(s)

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### The Conspiracy (2012) [THE-JESTER]
- **tmdb_id**: 133369
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6105
- **genres** / **language**: Thriller, Horror / en
- **overview**: A documentary about conspiracy theories takes a horrific turn after the filmmakers uncover an ancient and dangerous secret society.
- **跳转**: https://themoviecosmos.com/movie/133369
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p2: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.6105 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor; news focuses on casting controversy and identity politics in a film adaptation, while film involves uncovering secret societies in a conspiracy documentary—no concrete shared elements or thematic skeleton isomorphism.

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### Chained for Life (2019) [THE-INNOCENT]
- **tmdb_id**: 525825
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6088
- **genres** / **language**: Drama / en
- **overview**: A beautiful actress struggles to connect with her disfigured co-star on the set of a European auteur's English-language debut.
- **跳转**: https://themoviecosmos.com/movie/525825
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[how-0, how-1, how-2, how-3, why-0, result-0] · sim=0.6088 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 1
- **judge共振类型**: 表层
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives center on film sets where actors' appearances (race in news, disfigurement in film) are load-bearing concrete elements driving conflict, but the structural themes diverge: news focuses on macro-level culture wars over identity and heritage in mass media, while film explores micro-level personal struggles and prejudice in artistic collaboration, lacking full skeleton isomorphism.

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Viva Erotica (1996) [THE-INNOCENT]
- **tmdb_id**: 118379
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6071
- **genres** / **language**: Comedy, Drama / cn
- **overview**: Struggling director Sing is forced to make a Category III film for a triad boss who wants his girlfriend to star, leading to conflicts over artistic integrity, nudity, and his relationship with his own girlfriend.
- **跳转**: https://themoviecosmos.com/movie/118379
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p2: fragments=[how-0, how-1, how-2, result-1, why-1] · sim=0.6071 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor (news is about casting in mythic adaptation, film is about erotic film production) and skeleton not isomorphic (cultural identity debate vs. artistic integrity under criminal pressure).

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
<!-- pseudo命中分合计: 60 -->
### Gabbar Is Back (2015) [THE-HERO, THE-OUTLAW, THE-RULER, THE-LOVER, THE-MAGICIAN, THE-INNOCENT, THE-CAREGIVER, THE-EXPLORER] [优质·多agent]
- **tmdb_id**: 337876
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 8
- **优质候选**: true
- **distinct_agents**: 8
- **相似度**: 0.6434
- **genres** / **language**: Drama, Action / hi
- **overview**: A vigilante network taking out corrupt officials draws the notice of the authorities.
- **跳转**: https://themoviecosmos.com/movie/337876
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/n1: fragments=[who-0, who-3, how-3, result-0, why-0] · sim=0.4457
  - THE-OUTLAW/p1: fragments=[why-0, how-1, how-2, result-0] · sim=0.5477 · **命中分=4**
  - THE-RULER/p1: fragments=[why-0, how-1, how-2, result-0] · sim=0.6126 · **命中分=4**
  - THE-HERO/p2: fragments=[how-1, how-2, how-3, result-1, result-0, result-2] · sim=0.5054 · **命中分=6**
  - THE-LOVER/p2: fragments=[how-2, how-3, result-1] · sim=0.6434 · **命中分=3**
  - THE-MAGICIAN/p2: fragments=[how-1, how-2, how-3, result-0, result-2] · sim=0.5791 · **命中分=5**
  - THE-INNOCENT/p3: fragments=[why-0, how-1, how-2, how-3, how-4, result-2] · sim=0.4886 · **命中分=6**
  - THE-HERO/p3: fragments=[why-0, how-2, how-3, result-0, result-2] · sim=0.5357 · **命中分=5**
  - THE-CAREGIVER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0, result-1] · sim=0.5916 · **命中分=8**
  - THE-EXPLORER/p3: fragments=[why-0, how-2, how-3, result-0] · sim=0.5155 · **命中分=4**
  - THE-RULER/p3: fragments=[how-1, how-2, how-3, result-0, result-2] · sim=0.5069 · **命中分=5**
  - THE-MAGICIAN/p3: fragments=[how-1, how-2, how-3, result-0, result-2] · sim=0.5485 · **命中分=5**
- **pseudo命中分合计**: 60
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing shared concrete element (whistleblower vs. vigilante is not the same, and authorities acting is generic); structural skeleton not isomorphic (news focuses on authority-led exposure of exam corruption, while film features vigilante-driven action against officials, with different power dynamics and themes). Incidental overlap without unique resonance.

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 31 -->
### CNCO: los últimos cinco días (2022) [THE-EXPLORER, THE-CREATOR, THE-MAGICIAN, THE-SAGE] [优质·多agent]
- **tmdb_id**: 1030206
- **quality_candidate**: true
- **neutral_hits**: 3
- **neutral_total**: 12
- **neutral_hit_rate**: 0.2500
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.4566
- **genres** / **language**: Music, Documentary / es
- **overview**: CNCO: los últimos cinco días
- **跳转**: https://themoviecosmos.com/movie/1030206
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/n1: fragments=[why-0, result-0, who-0, how-1, how-2] · sim=0.4063
  - THE-CREATOR/n1: fragments=[result-0, how-1, how-0, why-0, result-2] · sim=0.4566
  - THE-MAGICIAN/n1: fragments=[result-0, why-0, how-1, who-0, how-3] · sim=0.3916
  - THE-SAGE/n1: fragments=[why-0, how-1, who-0, how-0, result-0] · sim=0.4193
  - THE-CREATOR/p1: fragments=[why-0, how-1, result-0, result-2] · sim=0.4408 · **命中分=4**
  - THE-SAGE/p1: fragments=[why-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.4243 · **命中分=7**
- **pseudo命中分合计**: 31
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface elements shared between news and film; news involves exam fraud and whistleblower scandal, while film is about a music band's final days, with no concrete overlap. Structural themes differ significantly, so an unrelated news could equally explain the film.

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 28 -->
### Kindergarten Cop 2 (2016) [THE-EVERYMAN, THE-HERO, THE-OUTLAW, THE-CAREGIVER]
- **tmdb_id**: 383121
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.6013
- **genres** / **language**: Comedy / en
- **overview**: Assigned to recover sensitive stolen data, a gruff FBI agent goes undercover as a kindergarten teacher, but the school's liberal, politically correct environment is more than he bargained for.
- **跳转**: https://themoviecosmos.com/movie/383121
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p2: fragments=[why-0, how-2, result-0, result-1, result-2] · sim=0.5174 · **命中分=5**
  - THE-HERO/p2: fragments=[how-1, how-2, how-3, result-1, result-0, result-2] · sim=0.5040 · **命中分=6**
  - THE-OUTLAW/p2: fragments=[how-1, how-2, how-3, result-1] · sim=0.5883 · **命中分=4**
  - THE-HERO/p3: fragments=[why-0, how-2, how-3, result-0, result-2] · sim=0.5575 · **命中分=5**
  - THE-CAREGIVER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0, result-1] · sim=0.6013 · **命中分=8**
- **pseudo命中分合计**: 28
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor: news involves exam fraud and whistleblower, film features FBI undercover in kindergarten with stolen data—no shared concrete elements. Structural themes diverge: news focuses on institutional corruption and justice, film on comedic adaptation and undercover mission. An unrelated news (e.g., school security or undercover ops) could equally explain the film.

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 17 -->
### Assassination Classroom the Movie: 365 Days' Time (2016) [THE-EVERYMAN, THE-CAREGIVER, THE-RULER, THE-OUTLAW] [优质·多agent]
- **tmdb_id**: 431808
- **quality_candidate**: true
- **neutral_hits**: 3
- **neutral_total**: 12
- **neutral_hit_rate**: 0.2500
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.4676
- **genres** / **language**: Action, Animation, Comedy, Drama / ja
- **overview**: The killer class is back in session—sort of. Relive every moment through the eyes of the top two students: Nagisa and Karma!
- **跳转**: https://themoviecosmos.com/movie/431808
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/n1: fragments=[result-0, who-5, who-2, how-4, why-0] · sim=0.4624
  - THE-CAREGIVER/n1: fragments=[result-0, who-2, result-2, how-0, who-5] · sim=0.4150
  - THE-RULER/n1: fragments=[result-0, result-1, who-3, who-1, how-2] · sim=0.4096
  - THE-OUTLAW/p3: fragments=[result-0, result-2] · sim=0.4676 · **命中分=2**
- **pseudo命中分合计**: 17
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: News focuses on an exam leak and whistleblower exposure, while the film centers on an assassination classroom with students targeting a teacher. The shared 'classroom' or 'student' elements are incidental and not load-bearing to both narratives, and there is no structural isomorphism in power, fate, or theme skeletons.

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 16 -->
### Black Dossier (1955) [THE-INNOCENT, THE-EVERYMAN, THE-SAGE]
- **tmdb_id**: 199252
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5597
- **genres** / **language**: Crime, Drama / fr
- **overview**: In the 1950s, in a small provincial town, a young inexperienced judge clashes with an influential notable during an investigation into a suspicious death. His perseverance to get to the truth will cause a huge scandal.
- **跳转**: https://themoviecosmos.com/movie/199252
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p2: fragments=[how-2, how-3, result-0, result-1] · sim=0.5597 · **命中分=4**
  - THE-EVERYMAN/p2: fragments=[why-0, how-2, result-0, result-1, result-2] · sim=0.5038 · **命中分=5**
  - THE-SAGE/p2: fragments=[how-0, why-0, how-1, how-2, how-3, result-0, result-2] · sim=0.4864 · **命中分=7**
- **pseudo命中分合计**: 16
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both news and film share a structural skeleton: an individual (whistleblower in news, judge in film) challenges powerful entities to uncover truth, leading to scandal and pursuit of justice, with isomorphic themes of power conflict and perseverance.

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 15 -->
### Lie Detector (2011) [THE-EVERYMAN, THE-EXPLORER, THE-OUTLAW]
- **tmdb_id**: 375384
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5492
- **genres** / **language**: Comedy / en
- **overview**: A job interview takes an awkward turn when a lie detector reveals the unfiltered truths and hidden feelings of everyone involved.
- **跳转**: https://themoviecosmos.com/movie/375384
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[why-0, how-1, how-2, how-3, result-0, result-2] · sim=0.4425 · **命中分=6**
  - THE-EXPLORER/p1: fragments=[why-0, how-1, how-2, result-0, result-2] · sim=0.5492 · **命中分=5**
  - THE-OUTLAW/p1: fragments=[why-0, how-1, how-2, result-0] · sim=0.5452 · **命中分=4**
- **pseudo命中分合计**: 15
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor; the news involves exam fraud via whistleblower tip, while the film centers on a lie detector in a job interview, with only incidental thematic overlap in truth-revelation. Structural skeletons are not isomorphic.

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 11 -->
### The Gracefield Incident (2017) [THE-OUTLAW, THE-HERO] [优质·多agent]
- **tmdb_id**: 327253
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.4375
- **genres** / **language**: Horror, Science Fiction, Action, Mystery / en
- **overview**: On August 16, 2013, the Supreme Court mandated the CIA to declassify files that had been kept secret for the past 75 years. Visual records of documented paranormal events were released to the public. The following incident took place in Gracefield, Quebec.
- **跳转**: https://themoviecosmos.com/movie/327253
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/n1: fragments=[who-0, why-0, how-1, result-0, who-4] · sim=0.4059
  - THE-HERO/p1: fragments=[how-1, why-0, how-2, how-3, result-0, how-4] · sim=0.4375 · **命中分=6**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchors or structural isomorphism; news about exam scandal in India has no concrete or thematic overlap with film about paranormal events in Quebec.

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 10 -->
### Le Brio (2017) [THE-EVERYMAN, THE-LOVER]
- **tmdb_id**: 452187
- **quality_candidate**: false
- **neutral_hits**: 2
- **neutral_total**: 12
- **neutral_hit_rate**: 0.1667
- **distinct_agents**: 0
- **优质候选**: false
- **distinct_agents**: 0
- **相似度**: 0.5590
- **genres** / **language**: Drama, Comedy / fr
- **overview**: After an incident, a brilliant professor known for his outbursts is forced to mentor the student he wronged for a speech contest.
- **跳转**: https://themoviecosmos.com/movie/452187
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/n1: fragments=[result-0, who-5, who-2, how-4, why-0] · sim=0.4690
  - THE-LOVER/n1: fragments=[who-5, who-4, who-2, result-0, result-1] · sim=0.5590
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchors; news involves exam leak and whistleblower, film is about mentorship in speech contest. Structural themes differ: systemic corruption vs. personal redemption.

### 单 agent 命中

**Count:** 7 candidate(s)

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 15 -->
### Bad Kids Go to Hell (2012) [THE-CAREGIVER]
- **tmdb_id**: 138372
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5961
- **genres** / **language**: Comedy, Mystery, Thriller, Horror / en
- **overview**: On a stormy Saturday afternoon, six students from Crestview Academy begin to meet horrible fates as they serve detention. Is a fellow student to blame, or perhaps Crestview's alleged ghosts are behind the terrible acts?
- **跳转**: https://themoviecosmos.com/movie/138372
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.5961 · **命中分=8**
  - THE-CAREGIVER/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-2] · sim=0.5843 · **命中分=7**
- **pseudo命中分合计**: 15
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing shared concrete elements (e.g., exam leak, whistleblowing vs. detention and supernatural fates) and no structural isomorphism in themes (institutional corruption vs. individual horror). An unrelated news could explain the film equally.

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 15 -->
### Haraamkhor (2015) [THE-CAREGIVER]
- **tmdb_id**: 314690
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5576
- **genres** / **language**: Drama / hi
- **overview**: When a vulnerable new student finds comfort in her brash teacher, their academic relationship takes a manipulative and troubling turn.
- **跳转**: https://themoviecosmos.com/movie/314690
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.5547 · **命中分=8**
  - THE-CAREGIVER/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-2] · sim=0.5576 · **命中分=7**
- **pseudo命中分合计**: 15
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: No load-bearing surface anchor; concrete elements differ (exam leak vs. personal manipulation); structural themes of power/betrayal are too vague and not isomorphic; unrelated news could equally explain the film.

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 11 -->
### The Cost of Deception (2021) [THE-EXPLORER]
- **tmdb_id**: 876671
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5744
- **genres** / **language**: Crime, Drama / hu
- **overview**: When a young, ambitious market researcher finds out her boss is involved in the leaking of a scandalous Prime Minister speech, she decides to investigate the case to gain a position among the big-shots. Based on actual events.
- **跳转**: https://themoviecosmos.com/movie/876671
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p2: fragments=[how-0, how-1, how-2, how-3, how-4, result-1, result-2] · sim=0.5744 · **命中分=7**
  - THE-EXPLORER/p3: fragments=[why-0, how-2, how-3, result-0] · sim=0.5321 · **命中分=4**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The news centers on an exam paper leak in education with whistleblowing for justice, while the film involves a political speech leak investigated for personal career gain. No load-bearing concrete anchor exists (leaks are generic and contextually distinct), and no structural isomorphism in power/fate/theme (motivations and domains differ). An unrelated news about political leaks could explain the film equally.

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 9 -->
### Scare Out (2026) [THE-RULER]
- **tmdb_id**: 1447971
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5469
- **genres** / **language**: Crime, Thriller, Action / zh
- **overview**: After a critical intelligence leak, a national security unit launches an intensive investigation. But successive setbacks in their arrest operations reveal a shocking truth: the trail leads back to within the unit itself. Amidst a storm of trust and betrayal, a silent battle begins to unfold...
- **跳转**: https://themoviecosmos.com/movie/1447971
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p1: fragments=[why-0, how-1, how-2, result-0] · sim=0.5469 · **命中分=4**
  - THE-RULER/p3: fragments=[how-1, how-2, how-3, result-0, result-2] · sim=0.5353 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both the news and film share a structural isomorphism: a leak (exam questions in news, intelligence in film) triggers an investigation that reveals internal involvement, leading to a crisis of trust and betrayal. No load-bearing surface anchors exist as the concrete elements differ (educational scandal vs. national security), but the power and fate skeletons align.

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 7 -->
### Who Killed Cock Robin (2017) [THE-EXPLORER]
- **tmdb_id**: 448337
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5716
- **genres** / **language**: Mystery, Thriller, Crime / zh
- **overview**: An ambitious journalist who witnessed a hit-and-run years ago reboots his investigation led by newly emerged clues. As he beats the clock to save the only survivor after her sudden disappearance, layers of unimaginable dark truths around a corrupted system start peeling.
- **跳转**: https://themoviecosmos.com/movie/448337
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p2: fragments=[how-0, how-1, how-2, how-3, how-4, result-1, result-2] · sim=0.5716 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: The news focuses on an exam paper leak exposed by a whistleblower, while the film centers on a journalist investigating a hit-and-run. Although both involve uncovering corruption, the concrete elements differ significantly, and the thematic overlap is too broad—an unrelated news with similar themes could equally explain the film, making the resonance incidental and not load-bearing.

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 5 -->
### Bespredel (1989) [THE-MAGICIAN]
- **tmdb_id**: 75649
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5577
- **genres** / **language**: Drama, Crime / ru
- **overview**: Using an elaborate system of denunciation, the chief of the Zone keeps his prisoners in check. A new inmate, allegedly imprisoned for speculating on postage stamps, tries to rebel against the system.
- **跳转**: https://themoviecosmos.com/movie/75649
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p3: fragments=[how-1, how-2, how-3, result-0, result-2] · sim=0.5577 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 2
- **judge共振类型**: 结构
- **judge采信**: 不采信 · screening only
- **judge理由**: Both narratives center on a corrupt system of control (exam testing agency vs. prison Zone) and an individual challenging it (whistleblower vs. rebel inmate), showing thematic isomorphism in power and rebellion, but no shared concrete surface elements.

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 5 -->
### Hell's House (1932) [THE-LOVER]
- **tmdb_id**: 136116
- **quality_candidate**: false
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 0
- **优质候选**: false
- **distinct_agents**: 0
- **相似度**: 0.5577
- **genres** / **language**: Drama / en
- **overview**: A teenager lands in a brutal reform school for refusing to squeal on his bootlegger boss.
- **跳转**: https://themoviecosmos.com/movie/136116
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/n1: fragments=[who-5, who-4, who-2, result-0, result-1] · sim=0.5577
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **judge分**: 0
- **judge共振类型**: 
- **judge采信**: 不采信 · screening only
- **judge理由**: News involves whistleblowing to expose academic corruption, whereas film depicts a teenager refusing to inform on a criminal boss, resulting in punishment. No load-bearing surface anchor (e.g., 'whistleblower' vs. 'refusal to squeal' are contrasting, not shared) and skeletons are not isomorphic (exposure leading to justice vs. loyalty leading to brutality). Incidental word overlap does not constitute resonance.

