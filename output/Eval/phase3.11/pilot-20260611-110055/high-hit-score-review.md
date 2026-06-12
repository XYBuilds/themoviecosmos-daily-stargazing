# High Pseudo Hit Score — Unified Review

## Criteria

### Pseudo 命中分（二级审阅键 · 非质量闸）

**High-hit review** lists candidates with **pseudo命中分合计 ≥ 5**.
`neutral_hits` / n1 coverage are displayed as retrieve diagnostics only and do not include candidates by themselves.
Inclusion is **not** a quality gate; `quality_candidate` is a retrieve annotation only.

For each hit line under **命中视角/碎片**, count entries in `fragments=[...]`
— **each fragment id = 1 point** for that pseudo.

- **Candidate 总分** (`pseudo命中分合计`) = sum of pseudo 命中分 across all hit lines.
- Shown inline per line, e.g. `A2/p1: fragments=[...] · sim=... · **命中分=3**`.

### Per-news layout

- News sections follow `tests/eval_news/batch-manifest.json` order (01–10).
- Each section opens with that run's `reality.md`.
- **多 agents 命中**: ≥2 agents in heading / hit_sources; `quality_candidate` is displayed only as annotation.
- **单 agent 命中**: all other high-hit candidates.
- Within each subsection, sort by **pseudo命中分合计** descending.

### Sources

- **Primary:** `hit_sources` in each run's `retrieve.json` (fragment arrays).
- **Editor fields:** 共振分 / 共振类型 / 打分备注 are placeholders only (not filled by this script).

- **Generation date:** 2026-06-11
- **Total candidates (≥5):** 7
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
<!-- pseudo命中分合计: 53 -->
### Survival Family (2017) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-RULER, THE-SAGE, THE-JESTER] [汇聚标注]
- **tmdb_id**: 429918
- **quality_candidate**: true
- **neutral_hits**: 10
- **neutral_total**: 12
- **neutral_hit_rate**: 0.8333
- **distinct_agents**: 10
- **quality_candidate_annotation**: true
- **distinct_agents**: 10
- **相似度**: 0.6094
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
  - THE-EVERYMAN/p1: fragments=[how-1, how-2, result-0] · sim=0.5389 · **命中分=3**
  - THE-HERO/p1: fragments=[why-0, how-2, result-0] · sim=0.5311 · **命中分=3**
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, result-0] · sim=0.5732 · **命中分=3**
  - THE-CREATOR/p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.4690 · **命中分=4**
  - THE-RULER/p1: fragments=[why-0, how-1, result-0] · sim=0.6094 · **命中分=3**
  - THE-INNOCENT/p2: fragments=[how-0, why-2, how-1, how-2] · sim=0.5107 · **命中分=4**
  - THE-CAREGIVER/p2: fragments=[why-2, how-2, result-0] · sim=0.5378 · **命中分=3**
  - THE-EXPLORER/p2: fragments=[why-0, why-1, how-1, result-0] · sim=0.5283 · **命中分=4**
  - THE-OUTLAW/p2: fragments=[how-2, why-0, why-2] · sim=0.5076 · **命中分=3**
  - THE-LOVER/p2: fragments=[why-0, why-1, how-1] · sim=0.5793 · **命中分=3**
  - THE-SAGE/p2: fragments=[why-0, how-0, how-1] · sim=0.4934 · **命中分=3**
  - THE-HERO/p3: fragments=[why-1, how-0, how-1] · sim=0.4582 · **命中分=3**
  - THE-CAREGIVER/p3: fragments=[why-0, how-1, how-2] · sim=0.4927 · **命中分=3**
  - THE-OUTLAW/p3: fragments=[why-0, why-1, how-1, result-0] · sim=0.5788 · **命中分=4**
  - THE-LOVER/p3: fragments=[why-0, why-1, how-2] · sim=0.5700 · **命中分=3**
  - THE-CREATOR/p3: fragments=[why-0, how-1, how-2, result-0] · sim=0.5164 · **命中分=4**
- **pseudo命中分合计**: 53
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:  是 <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 12 -->
### Geostorm (2017) [THE-MAGICIAN, THE-RULER, THE-LOVER]
- **tmdb_id**: 274855
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **quality_candidate_annotation**: false
- **distinct_agents**: 3
- **相似度**: 0.5162
- **genres** / **language**: Action, Science Fiction, Thriller / en
- **overview**: After an unprecedented series of natural disasters threatened the planet, the world's leaders came together to create an intricate network of satellites to control the global climate and keep everyone safe. But now, something has gone wrong: the system built to protect Earth is attacking it, and it becomes a race against the clock to uncover the real threat before a worldwide geostorm wipes out everything and everyone along with it.
- **跳转**: https://themoviecosmos.com/movie/274855
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1: fragments=[how-1, how-2, why-1] · sim=0.4942 · **命中分=3**
  - THE-RULER/p2: fragments=[how-1, why-0, how-2] · sim=0.4889 · **命中分=3**
  - THE-LOVER/p3: fragments=[why-0, why-1, how-2] · sim=0.5162 · **命中分=3**
  - THE-MAGICIAN/p3: fragments=[how-1, why-0, how-2] · sim=0.4240 · **命中分=3**
- **pseudo命中分合计**: 12
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层元素  <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 11 -->
### The Current War (2018) [THE-CAREGIVER, THE-CREATOR]
- **tmdb_id**: 418879
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **quality_candidate_annotation**: false
- **distinct_agents**: 2
- **相似度**: 0.5429
- **genres** / **language**: Drama, History / en
- **overview**: Electricity titans Thomas Edison and George Westinghouse compete to create a sustainable system and market it to the American people.
- **跳转**: https://themoviecosmos.com/movie/418879
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p2: fragments=[why-2, how-2, result-0] · sim=0.5256 · **命中分=3**
  - THE-CREATOR/p2: fragments=[why-0, why-1, how-2, result-0] · sim=0.5429 · **命中分=4**
  - THE-CREATOR/p3: fragments=[why-0, how-1, how-2, result-0] · sim=0.4502 · **命中分=4**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 9 -->
### Blade Runner: Black Out 2022 (2017) [THE-CAREGIVER, THE-RULER, THE-SAGE]
- **tmdb_id**: 475946
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **quality_candidate_annotation**: false
- **distinct_agents**: 3
- **相似度**: 0.5161
- **genres** / **language**: Action, Animation, Science Fiction / en
- **overview**: This animated short revolves around the events causing an electrical systems failure on the west coast of the US. According to Blade Runner 2049’s official timeline, this failure leads to cities shutting down, financial and trade markets being thrown into chaos, and food supplies dwindling. There’s no proof as to what caused the blackouts, but Replicants — the bio-engineered robots featured in the original Blade Runner, are blamed.
- **跳转**: https://themoviecosmos.com/movie/475946
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, result-0] · sim=0.5161 · **命中分=3**
  - THE-RULER/p1: fragments=[why-0, how-1, result-0] · sim=0.4709 · **命中分=3**
  - THE-SAGE/p2: fragments=[why-0, how-0, how-1] · sim=0.4464 · **命中分=3**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 6 -->
### Pulse (1988) [THE-EVERYMAN, THE-LOVER]
- **tmdb_id**: 32033
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **quality_candidate_annotation**: false
- **distinct_agents**: 2
- **相似度**: 0.5131
- **genres** / **language**: Horror, Science Fiction / en
- **overview**: An intelligent pulse of electricity moves from house to house, terrorizing occupants through their own appliances. Having already destroyed one household in a quiet neighborhood, the pulse finds itself in the home of a boy and his divorced father.
- **跳转**: https://themoviecosmos.com/movie/32033
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[how-1, how-2, result-0] · sim=0.4381 · **命中分=3**
  - THE-LOVER/p2: fragments=[why-0, why-1, how-1] · sim=0.5131 · **命中分=3**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 6 -->
### Gabbar Is Back (2015) [THE-OUTLAW, THE-HERO]
- **tmdb_id**: 337876
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **quality_candidate_annotation**: false
- **distinct_agents**: 2
- **相似度**: 0.4816
- **genres** / **language**: Drama, Action / hi
- **overview**: A vigilante network taking out corrupt officials draws the notice of the authorities.
- **跳转**: https://themoviecosmos.com/movie/337876
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p2: fragments=[how-2, why-0, why-2] · sim=0.4816 · **命中分=3**
  - THE-HERO/p3: fragments=[why-1, how-0, how-1] · sim=0.4666 · **命中分=3**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 6 -->
### Stranded (2021) [THE-MAGICIAN, THE-LOVER] [汇聚标注]
- **tmdb_id**: 841793
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 2
- **quality_candidate_annotation**: true
- **distinct_agents**: 2
- **相似度**: 0.5376
- **genres** / **language**: Drama / pt
- **overview**: Tensions run high while food runs low as six influencers find themselves stranded on a secluded island after plans for a weekend escape go awry.
- **跳转**: https://themoviecosmos.com/movie/841793
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/n1: fragments=[how-1, why-2, how-2, result-0, who-0] · sim=0.4517
  - THE-LOVER/p1: fragments=[why-2, why-1, result-0] · sim=0.5376 · **命中分=3**
  - THE-MAGICIAN/p2: fragments=[why-2, how-0, result-0] · sim=0.4679 · **命中分=3**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 0 留空；1→深层共振（仅结构，无表层）|表层沾边；2→强共振（表层 + 结构） -->
- **POV变换**:   <!-- 可选；仅 score 2 时填 是，标记靠视角/尺度变换才看得出的强共振 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 0 candidate(s)

