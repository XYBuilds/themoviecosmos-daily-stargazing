# High Pseudo Hit Score — Unified Review

## Criteria

### Pseudo 命中分（二级审阅键 · 非质量闸）

**High-hit review** lists candidates with **pseudo命中分合计 ≥ 5**
as an editor triage aid. Inclusion here is **not** a quality gate; D1
`quality_candidate` (≥2 agents above floor) is computed in retrieve/run_eval.

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
- **Editor fields:** 共振分 / 共振类型 / 打分备注 are placeholders only (not filled by this script).

- **Generation date:** 2026-06-06
- **Total candidates (≥5):** 174
- **Runs scanned:** 11

## 留出集打分（3.8.7 · 总编必填）

Phase 3.8.8 GATE 前，请在**本文件**的留出集章节（`05-climate-disaster` … `10-whistleblower-leak`）中，对 **≥2 条**新闻各选至少 1 个候选，填写：

- **共振分**：`0` / `1` / `2`
- **共振类型**：`表层` / `结构` / `双重`（0 分留空）

观察集 `01`–`04` 可选填作对照。`01-grid-outage-rerun` 为 3.8.6 试点目录，**不计入** manifest 闸门统计。

### Past score backfill

- **Merged from:** phase3.5, phase3.6, phase3.7
- **Match key:** `tmdb_id` (primary), normalized movie title (fallback)
- **Conflict policy:** differing past scores kept in **历史打分**; phase 3.8 fields left blank for re-score

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

**Count:** 8 candidate(s)

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 210 -->
### Survival Family (2017) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-CREATOR, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-JESTER] [优质·多agent]
- **tmdb_id**: 429918
- **quality_candidate**: true
- **neutral_hits**: 11
- **neutral_total**: 11
- **neutral_hit_rate**: 1.0000
- **distinct_agents**: 11
- **优质候选**: true
- **distinct_agents**: 11
- **相似度**: 0.6431
- **genres** / **language**: Comedy, Drama, Adventure / ja
- **overview**: A world wide electrical outage occurs. Everything that requires electricity comes to a stop. Tokyo is nearly ruined. Yoshiyuki Suzuki decides to escape from Tokyo with his family.
- **跳转**: https://themoviecosmos.com/movie/429918
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5023
  - THE-EVERYMAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5048
  - THE-HERO/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5048
  - THE-CAREGIVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5048
  - THE-EXPLORER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4968
  - THE-OUTLAW/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5015
  - THE-CREATOR/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5012
  - THE-RULER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5048
  - THE-MAGICIAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5048
  - THE-SAGE/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4974
  - THE-JESTER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4991
  - THE-INNOCENT/p1: fragments=[why-0, why-1, how-0, how-1, result-0, result-1] · sim=0.5437 · **命中分=6**
  - THE-EVERYMAN/p1: fragments=[why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5217 · **命中分=7**
  - THE-CAREGIVER/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5098 · **命中分=6**
  - THE-CREATOR/p1: fragments=[why-0, how-0, how-1, how-2, why-2, result-0, result-1] · sim=0.5255 · **命中分=7**
  - THE-RULER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5761 · **命中分=7**
  - THE-SAGE/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5139 · **命中分=7**
  - THE-JESTER/p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.4589 · **命中分=4**
  - THE-EVERYMAN/p2: fragments=[why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.6431 · **命中分=8**
  - THE-HERO/p2: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0] · sim=0.6045 · **命中分=7**
  - THE-EXPLORER/p2: fragments=[why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5675 · **命中分=8**
  - THE-OUTLAW/p2: fragments=[why-2, why-1, how-0, how-1, how-2, result-0, result-1] · sim=0.5079 · **命中分=7**
  - THE-RULER/p2: fragments=[why-1, why-2, how-1, how-2, how-3, result-0] · sim=0.5976 · **命中分=6**
  - THE-MAGICIAN/p2: fragments=[why-0, how-0, how-1, why-2, how-2, how-3, result-0, result-1] · sim=0.4718 · **命中分=8**
  - THE-SAGE/p2: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5111 · **命中分=9**
  - THE-JESTER/p2: fragments=[why-0, why-1, why-2, how-3, result-1] · sim=0.5773 · **命中分=5**
  - THE-INNOCENT/p3: fragments=[why-2, how-1, how-2, how-3, result-1] · sim=0.5157 · **命中分=5**
  - THE-EVERYMAN/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.6090 · **命中分=7**
  - THE-CAREGIVER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0] · sim=0.5824 · **命中分=6**
  - THE-EXPLORER/p3: fragments=[why-0, why-2, how-1, how-2, how-3, result-0, result-1] · sim=0.5546 · **命中分=7**
  - THE-OUTLAW/p3: fragments=[why-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5686 · **命中分=6**
  - THE-CREATOR/p3: fragments=[how-0, how-1, how-2, how-3, why-1, why-2, result-0, result-1] · sim=0.5338 · **命中分=8**
  - THE-MAGICIAN/p3: fragments=[why-0, why-1, why-2, how-3, result-0, result-1] · sim=0.4810 · **命中分=6**
  - THE-SAGE/p3: fragments=[why-0, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4470 · **命中分=8**
- **pseudo命中分合计**: 210
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 效果相当好
- **历史打分**: （phase3.5 / 2 / 双重） （phase3.6 / 2 / 双重 / 效果相当好） （phase3.7 / 2 / 双重）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 44 -->
### Geostorm (2017) [THE-HERO, THE-INNOCENT, THE-OUTLAW, THE-RULER, THE-MAGICIAN, THE-SAGE]
- **tmdb_id**: 274855
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 6
- **优质候选**: false
- **distinct_agents**: 6
- **相似度**: 0.5623
- **genres** / **language**: Action, Science Fiction, Thriller / en
- **overview**: After an unprecedented series of natural disasters threatened the planet, the world's leaders came together to create an intricate network of satellites to control the global climate and keep everyone safe. But now, something has gone wrong: the system built to protect Earth is attacking it, and it becomes a race against the clock to uncover the real threat before a worldwide geostorm wipes out everything and everyone along with it.
- **跳转**: https://themoviecosmos.com/movie/274855
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[why-0, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5623 · **命中分=8**
  - THE-INNOCENT/p2: fragments=[why-1, how-0, how-1, how-2, how-3, result-1] · sim=0.5245 · **命中分=6**
  - THE-INNOCENT/p3: fragments=[why-2, how-1, how-2, how-3, result-1] · sim=0.5061 · **命中分=5**
  - THE-OUTLAW/p3: fragments=[why-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4922 · **命中分=6**
  - THE-RULER/p3: fragments=[why-1, how-2, how-3, result-0, result-1] · sim=0.4663 · **命中分=5**
  - THE-MAGICIAN/p3: fragments=[why-0, why-1, why-2, how-3, result-0, result-1] · sim=0.4830 · **命中分=6**
  - THE-SAGE/p3: fragments=[why-0, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4510 · **命中分=8**
- **pseudo命中分合计**: 44
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 结构  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 灾难感有点联系

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 39 -->
### Blade Runner: Black Out 2022 (2017) [THE-INNOCENT, THE-RULER, THE-HERO, THE-CREATOR, THE-JESTER]
- **tmdb_id**: 475946
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 5
- **优质候选**: false
- **distinct_agents**: 5
- **相似度**: 0.5580
- **genres** / **language**: Action, Animation, Science Fiction / en
- **overview**: This animated short revolves around the events causing an electrical systems failure on the west coast of the US. According to Blade Runner 2049’s official timeline, this failure leads to cities shutting down, financial and trade markets being thrown into chaos, and food supplies dwindling. There’s no proof as to what caused the blackouts, but Replicants — the bio-engineered robots featured in the original Blade Runner, are blamed.
- **跳转**: https://themoviecosmos.com/movie/475946
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, why-1, how-0, how-1, result-0, result-1] · sim=0.4563 · **命中分=6**
  - THE-RULER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5107 · **命中分=7**
  - THE-HERO/p2: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0] · sim=0.5017 · **命中分=7**
  - THE-CREATOR/p2: fragments=[why-0, why-1, why-2, how-3, result-0, result-1] · sim=0.5580 · **命中分=6**
  - THE-CREATOR/p3: fragments=[how-0, how-1, how-2, how-3, why-1, why-2, result-0, result-1] · sim=0.5408 · **命中分=8**
  - THE-JESTER/p3: fragments=[why-0, why-1, how-0, how-1, result-0] · sim=0.4983 · **命中分=5**
- **pseudo命中分合计**: 39
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 赛博朋克主题有启示感；且表层上讲的也是大停电，与新闻有关。

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 33 -->
### From What Is Before (2014) [THE-MAGICIAN, THE-JESTER, THE-CAREGIVER, THE-HERO]
- **tmdb_id**: 280492
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.5264
- **genres** / **language**: Drama / tl
- **overview**: The Philippines, 1972. Mysterious things are happening in a remote barrio. Wails are heard from the forest, cows are hacked to death, a man is found bleeding to death at the crossroad, and houses are burned. Ferdinand E. Marcos announces Proclamation No. 1081, putting the entire country under Martial Law.
- **跳转**: https://themoviecosmos.com/movie/280492
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, how-3, result-1] · sim=0.4755 · **命中分=8**
  - THE-JESTER/p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.4439 · **命中分=4**
  - THE-CAREGIVER/p2: fragments=[why-1, why-2, how-2, how-3, result-1] · sim=0.5221 · **命中分=5**
  - THE-MAGICIAN/p2: fragments=[why-0, how-0, how-1, why-2, how-2, how-3, result-0, result-1] · sim=0.4854 · **命中分=8**
  - THE-HERO/p3: fragments=[why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5264 · **命中分=8**
- **pseudo命中分合计**: 33
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 只有菲律宾这个概念相关，low 1

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 22 -->
### Stranded (2021) [THE-EVERYMAN, THE-OUTLAW, THE-EXPLORER]
- **tmdb_id**: 841793
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5334
- **genres** / **language**: Drama / pt
- **overview**: Tensions run high while food runs low as six influencers find themselves stranded on a secluded island after plans for a weekend escape go awry.
- **跳转**: https://themoviecosmos.com/movie/841793
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p2: fragments=[why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5334 · **命中分=8**
  - THE-OUTLAW/p2: fragments=[why-2, why-1, how-0, how-1, how-2, result-0, result-1] · sim=0.4914 · **命中分=7**
  - THE-EXPLORER/p3: fragments=[why-0, why-2, how-1, how-2, how-3, result-0, result-1] · sim=0.5177 · **命中分=7**
- **pseudo命中分合计**: 22
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **历史打分**: （phase3.6 / 1 / 表层） （phase3.7 / 1 / 结构 / 和现实原型扯得有点远）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 13 -->
### Re-Generator (2010) [THE-CAREGIVER, THE-SAGE]
- **tmdb_id**: 194834
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.4857
- **genres** / **language**: Action, Science Fiction / en
- **overview**: A plane containing a highly classified government project crashes outside of a small town in the US. Realizing the level of danger, the government tries to secretly fix the problem. As tensions grow, the situation gets out of control, and civilians from the town find themselves facing their worst nightmare: a genetically enhanced killing machine that doesn't know how to stop.
- **跳转**: https://themoviecosmos.com/movie/194834
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4857 · **命中分=6**
  - THE-SAGE/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4404 · **命中分=7**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 13 -->
### The Current War (2018) [THE-EXPLORER, THE-CREATOR]
- **tmdb_id**: 418879
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5834
- **genres** / **language**: Drama, History / en
- **overview**: Electricity titans Thomas Edison and George Westinghouse compete to create a sustainable system and market it to the American people.
- **跳转**: https://themoviecosmos.com/movie/418879
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5157 · **命中分=6**
  - THE-CREATOR/p1: fragments=[why-0, how-0, how-1, how-2, why-2, result-0, result-1] · sim=0.5834 · **命中分=7**
- **pseudo命中分合计**: 13
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 电力系统相关，solid 1

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 12 -->
### Space/Time (2025) [THE-EXPLORER, THE-CREATOR]
- **tmdb_id**: 434853
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5321
- **genres** / **language**: Science Fiction, Action, Thriller / en
- **overview**: After a fatal test shuts down their project, a disgraced team of scientists enters the criminal underworld to rebuild a forbidden space-bending engine that could rescue humanity or annihilate it entirely.
- **跳转**: https://themoviecosmos.com/movie/434853
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5122 · **命中分=6**
  - THE-CREATOR/p2: fragments=[why-0, why-1, why-2, how-3, result-0, result-1] · sim=0.5321 · **命中分=6**
- **pseudo命中分合计**: 12
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 11 candidate(s)

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 8 -->
### 2061 - Un anno eccezionale (2007) [THE-EXPLORER]
- **tmdb_id**: 33495
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5648
- **genres** / **language**: Comedy, Science Fiction / it
- **overview**: In a post-apocalyptic future, the Italian peninsula is going through a dark moment due to a terrible energy crisis.
- **跳转**: https://themoviecosmos.com/movie/33495
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p2: fragments=[why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5648 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 8 -->
### Bataan (1943) [THE-HERO]
- **tmdb_id**: 43506
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5214
- **genres** / **language**: Action, Drama, War / en
- **overview**: During Japan's invasion of the Philippines in 1942, Capt. Henry Lassiter, Sgt. Bill Dane and a diverse group of American soldiers are ordered to destroy and hold a strategic bridge in order to delay the Japanese forces and allow Gen. MacArthur time to secure Bataan. When the Japanese soldiers begin to rebuild the bridge and advance, the group struggles with not only hunger, sickness and gunfire, but also the knowledge that there is likely no relief on the way.
- **跳转**: https://themoviecosmos.com/movie/43506
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p3: fragments=[why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5214 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 8 -->
### Black Noise (2023) [THE-HERO]
- **tmdb_id**: 1159518
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5958
- **genres** / **language**: Action, Science Fiction, Horror, Thriller / en
- **overview**: Members of an elite security team deployed to rescue a VIP on an exclusive island.The rescue mission becomes a desperate attempt to survive, escape the island and elude the sinister presence that seeks to harm them.
- **跳转**: https://themoviecosmos.com/movie/1159518
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[why-0, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5958 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 7 -->
### Pandora (2016) [THE-EVERYMAN]
- **tmdb_id**: 429450
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5221
- **genres** / **language**: Thriller, Drama, Action / ko
- **overview**: When an earthquake hits a Korean village housing a run-down nuclear power plant, a man risks his life to save the country from imminent disaster.
- **跳转**: https://themoviecosmos.com/movie/429450
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5221 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 7 -->
### Breathe (2024) [THE-EVERYMAN]
- **tmdb_id**: 720321
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4853
- **genres** / **language**: Action, Science Fiction, Mystery, Thriller / en
- **overview**: Air-supply is scarce in the near future, forcing a mother and daughter to fight for survival when two strangers arrive desperate for an oxygenated haven.
- **跳转**: https://themoviecosmos.com/movie/720321
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4853 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **历史打分**: （phase3.6 / 1 / 表层 / 资源短缺的感觉挺优秀的，其实介于1和2之间） （phase3.7 / 2 / 结构 / 现实中的电力短缺与电影overview中的空气供应有微妙的共振，low 2）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 6 -->
### Sarkar Raj (2008) [THE-CAREGIVER]
- **tmdb_id**: 14394
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5017
- **genres** / **language**: Action, Adventure, Crime, Drama / hi
- **overview**: When Anita Raja, CEO of Sheppard power plant, brings a power plant proposal to set up in rural Mahrashtra before the Nagres, insightful Shankar is quick to realise the benefits the power plant can bring to the people.
- **跳转**: https://themoviecosmos.com/movie/14394
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0] · sim=0.5017 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 6 -->
### Alien: Harvest (2019) [THE-INNOCENT]
- **tmdb_id**: 588209
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4962
- **genres** / **language**: Science Fiction, Horror / en
- **overview**: The surviving crew of a damaged space harvester has a motion sensor as their only navigation tool leading them to safety, while a creature in the shadows terrorizes them. However, the greatest threat might have been hiding in plain sight.
- **跳转**: https://themoviecosmos.com/movie/588209
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p2: fragments=[why-1, how-0, how-1, how-2, how-3, result-1] · sim=0.4962 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### The Towering Inferno (1974) [THE-JESTER]
- **tmdb_id**: 5919
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5071
- **genres** / **language**: Action, Drama, Thriller / en
- **overview**: At the opening party of a colossal—but poorly constructed—skyscraper, a massive fire breaks out, threatening to destroy the tower and everyone in it.
- **跳转**: https://themoviecosmos.com/movie/5919
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p2: fragments=[why-0, why-1, why-2, how-3, result-1] · sim=0.5071 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Fires on the Plain (2015) [THE-CAREGIVER]
- **tmdb_id**: 283710
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5217
- **genres** / **language**: War, Drama / ja
- **overview**: In the final days of World War II, occupying Japanese forces in the Philippines face resistance from the local population and the American offensive. The dwindling Japanese soldiers attempt to survive through the horrors of war.
- **跳转**: https://themoviecosmos.com/movie/283710
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p2: fragments=[why-1, why-2, how-2, how-3, result-1] · sim=0.5217 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Kaappaan (2019) [THE-RULER]
- **tmdb_id**: 533885
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4892
- **genres** / **language**: Action, Thriller / ta
- **overview**: A Special Protection Group officer has to identify the threat to the prime minister, who he is protecting, and also the nation.
- **跳转**: https://themoviecosmos.com/movie/533885
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p3: fragments=[why-1, how-2, how-3, result-0, result-1] · sim=0.4892 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Asteroid City (2023) [THE-JESTER]
- **tmdb_id**: 747188
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5068
- **genres** / **language**: Comedy, Drama / en
- **overview**: In an American desert town circa 1955, the itinerary of a Junior Stargazer/Space Cadet convention is spectacularly disrupted by world-changing events.
- **跳转**: https://themoviecosmos.com/movie/747188
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p3: fragments=[why-0, why-1, how-0, how-1, result-0] · sim=0.5068 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
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

**Count:** 11 candidate(s)

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 48 -->
### The Plan (2018) [THE-EVERYMAN, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-SAGE, THE-INNOCENT, THE-JESTER] [优质·多agent]
- **tmdb_id**: 619090
- **quality_candidate**: true
- **neutral_hits**: 5
- **neutral_total**: 12
- **neutral_hit_rate**: 0.4167
- **distinct_agents**: 4
- **优质候选**: true
- **distinct_agents**: 4
- **相似度**: 0.5312
- **genres** / **language**: Comedy, Drama / es
- **overview**: Three friends who have been fired from the company where they worked and are demoralized because of their unemployment status. In these circumstances, they meet to undertake the plan that mentions the title but there is a problem: the car with which they would travel has broken down and the crane must wait.
- **跳转**: https://themoviecosmos.com/movie/619090
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4296
  - THE-OUTLAW/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4296
  - THE-LOVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4239
  - THE-CREATOR/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4296
  - THE-SAGE/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4294
  - THE-INNOCENT/p2: fragments=[why-0, result-1, result-3] · sim=0.5281 · **命中分=3**
  - THE-EVERYMAN/p2: fragments=[why-0, how-1, result-1, result-3] · sim=0.5166 · **命中分=4**
  - THE-CREATOR/p2: fragments=[why-0, why-1, how-0, result-0, result-1, result-2, result-3] · sim=0.5011 · **命中分=7**
  - THE-JESTER/p2: fragments=[how-0, why-1, how-1, result-0, result-2] · sim=0.5312 · **命中分=5**
  - THE-EVERYMAN/p3: fragments=[why-0, why-1, how-0, result-1] · sim=0.4716 · **命中分=4**
- **pseudo命中分合计**: 48
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 42 -->
### Mirreyes contra Godínez 2: El retiro (2022) [THE-INNOCENT, THE-LOVER, THE-SAGE, THE-HERO, THE-OUTLAW, THE-EXPLORER]
- **tmdb_id**: 1002695
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 6
- **优质候选**: false
- **distinct_agents**: 6
- **相似度**: 0.6272
- **genres** / **language**: Comedy / es
- **overview**: A divided team heads to a corporate retreat after receiving an enticing proposal. During their time away, they must overcome their differences and find a way to reunite.
- **跳转**: https://themoviecosmos.com/movie/1002695
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-1, how-0, how-1, result-2] · sim=0.5202 · **命中分=4**
  - THE-LOVER/p1: fragments=[why-1, how-0, result-0, result-1, result-2] · sim=0.4949 · **命中分=5**
  - THE-SAGE/p1: fragments=[why-1, how-0, result-0] · sim=0.4868 · **命中分=3**
  - THE-INNOCENT/p2: fragments=[why-0, result-1, result-3] · sim=0.5063 · **命中分=3**
  - THE-HERO/p2: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.5136 · **命中分=5**
  - THE-OUTLAW/p2: fragments=[why-1, how-0, how-1, how-2, result-0, result-3] · sim=0.5381 · **命中分=6**
  - THE-LOVER/p2: fragments=[why-0, why-1, how-0, how-1, how-2, result-1, result-2] · sim=0.6272 · **命中分=7**
  - THE-HERO/p3: fragments=[why-1, how-0, how-1, result-1] · sim=0.5669 · **命中分=4**
  - THE-EXPLORER/p3: fragments=[why-1, how-0, how-1, how-2, result-1] · sim=0.5839 · **命中分=5**
- **pseudo命中分合计**: 42
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **历史打分**: （phase3.5 / 1 / 双重） （phase3.7 / 1 / 表层）

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 41 -->
### The Factory (2018) [THE-EVERYMAN, THE-CAREGIVER, THE-CREATOR, THE-RULER, THE-EXPLORER]
- **tmdb_id**: 513349
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 5
- **优质候选**: false
- **distinct_agents**: 5
- **相似度**: 0.5656
- **genres** / **language**: Thriller, Drama, Crime / ru
- **overview**: When a factory is bound to close, a group of workers decides to take action against the owner.
- **跳转**: https://themoviecosmos.com/movie/513349
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[why-1, how-0, result-0, result-2] · sim=0.5089 · **命中分=4**
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, result-0, how-1] · sim=0.5655 · **命中分=4**
  - THE-CAREGIVER/p2: fragments=[why-1, result-1, how-1, result-0] · sim=0.5440 · **命中分=4**
  - THE-CREATOR/p2: fragments=[why-0, why-1, how-0, result-0, result-1, result-2, result-3] · sim=0.5098 · **命中分=7**
  - THE-RULER/p2: fragments=[why-0, how-0, result-0, result-1, how-1, how-2] · sim=0.5311 · **命中分=6**
  - THE-EVERYMAN/p3: fragments=[why-0, why-1, how-0, result-1] · sim=0.5119 · **命中分=4**
  - THE-EXPLORER/p3: fragments=[why-1, how-0, how-1, how-2, result-1] · sim=0.5656 · **命中分=5**
  - THE-RULER/p3: fragments=[why-0, why-1, how-0, result-0, result-1, how-1, result-2] · sim=0.4925 · **命中分=7**
- **pseudo命中分合计**: 41
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 40 -->
### Bounty Killer (2013) [THE-CAREGIVER, THE-EXPLORER, THE-CREATOR, THE-RULER, THE-JESTER, THE-MAGICIAN] [优质·多agent]
- **tmdb_id**: 209504
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 5
- **优质候选**: true
- **distinct_agents**: 5
- **相似度**: 0.5748
- **genres** / **language**: Action, Science Fiction / en
- **overview**: It’s been 20 years since the corporations took over the world’s governments. Their thirst for power and profits led to the Corporate Wars, a fierce global battle that laid waste to society as we know it. Born from the ash, the Council of Nine rose as a new law and order for this dark age. To avenge the corporations’ reckless destruction, the Council issues death warrants for all white collar criminals. Their hunters—the bounty killer. From amateur savage to graceful assassin, the bounty killers now compete for body count, fame and a fat stack of cash. They’re ending the plague of corporate greed and providing the survivors of the apocalypse with retribution. These are the new heroes. This is the age of the BOUNTY KILLER.
- **跳转**: https://themoviecosmos.com/movie/209504
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4370
  - THE-EXPLORER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4749 · **命中分=4**
  - THE-CREATOR/p1: fragments=[why-0, why-1, how-0, how-1, how-2, result-0] · sim=0.5288 · **命中分=6**
  - THE-RULER/p1: fragments=[why-0, why-1, how-0, how-1, result-1, result-2] · sim=0.5747 · **命中分=6**
  - THE-JESTER/p1: fragments=[why-0, how-0, how-1, result-0] · sim=0.5748 · **命中分=4**
  - THE-RULER/p2: fragments=[why-0, how-0, result-0, result-1, how-1, how-2] · sim=0.5106 · **命中分=6**
  - THE-MAGICIAN/p2: fragments=[why-1, how-2, result-1, result-3] · sim=0.5079 · **命中分=4**
  - THE-JESTER/p3: fragments=[why-0, how-0, result-1, result-3, result-2] · sim=0.4848 · **命中分=5**
- **pseudo命中分合计**: 40
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 效果不是特别好，low 2
- **历史打分**: （phase3.6 / 2 / 双重 / 效果不是特别好，low 2） （phase3.7 / 2 / 双重）

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 30 -->
### The Seventh Company Outdoors (1977) [THE-INNOCENT, THE-CAREGIVER, THE-EXPLORER, THE-RULER, THE-MAGICIAN, THE-HERO] [优质·多agent]
- **tmdb_id**: 56589
- **quality_candidate**: true
- **neutral_hits**: 5
- **neutral_total**: 12
- **neutral_hit_rate**: 0.4167
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5271
- **genres** / **language**: Comedy / fr
- **overview**: The third part of Seventh Company adventures.
- **跳转**: https://themoviecosmos.com/movie/56589
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4336
  - THE-CAREGIVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4571
  - THE-EXPLORER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4422
  - THE-RULER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4226
  - THE-MAGICIAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4224
  - THE-HERO/p2: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.5271 · **命中分=5**
- **pseudo命中分合计**: 30
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: ！！！这个candidate需要注意：电影overview极短，完全没有参考价值，为什么会有那么多agents匹配到它？

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 29 -->
### Cart (2014) [THE-EVERYMAN, THE-CAREGIVER, THE-SAGE, THE-INNOCENT]
- **tmdb_id**: 287647
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.5564
- **genres** / **language**: Drama / ko
- **overview**: In response to a sudden dismissal of staff, workers at a big retail store begin a protest against their employer's oppressive labor policies.
- **跳转**: https://themoviecosmos.com/movie/287647
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[why-1, how-0, result-0, result-2] · sim=0.5332 · **命中分=4**
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, result-0, how-1] · sim=0.5564 · **命中分=4**
  - THE-EVERYMAN/p2: fragments=[why-0, how-1, result-1, result-3] · sim=0.5099 · **命中分=4**
  - THE-CAREGIVER/p2: fragments=[why-1, result-1, how-1, result-0] · sim=0.5413 · **命中分=4**
  - THE-SAGE/p2: fragments=[how-1, result-2, how-2] · sim=0.4627 · **命中分=3**
  - THE-INNOCENT/p3: fragments=[how-0, how-1, result-0] · sim=0.5413 · **命中分=3**
  - THE-CAREGIVER/p3: fragments=[how-2, result-0, result-2, result-3] · sim=0.4984 · **命中分=4**
  - THE-SAGE/p3: fragments=[how-0, result-1, why-0] · sim=0.5044 · **命中分=3**
- **pseudo命中分合计**: 29
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 17 -->
### Johnny Keep Walking! (2023) [THE-HERO, THE-MAGICIAN, THE-EXPLORER, THE-OUTLAW]
- **tmdb_id**: 1173076
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.5295
- **genres** / **language**: Drama, Comedy / zh
- **overview**: A simple technician at a rural factory is mistakenly promoted to a high-level managerial position at corporate headquarters due to a series of clerical errors and a bribery scheme gone wrong.
- **跳转**: https://themoviecosmos.com/movie/1173076
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[why-1, how-0, result-0] · sim=0.5201 · **命中分=3**
  - THE-MAGICIAN/p1: fragments=[why-0, how-0, how-1, result-0] · sim=0.5295 · **命中分=4**
  - THE-EXPLORER/p2: fragments=[why-1, how-2, result-0, result-3] · sim=0.5276 · **命中分=4**
  - THE-OUTLAW/p2: fragments=[why-1, how-0, how-1, how-2, result-0, result-3] · sim=0.4793 · **命中分=6**
- **pseudo命中分合计**: 17
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 15 -->
### Corporate Animals (2019) [THE-INNOCENT, THE-LOVER, THE-HERO]
- **tmdb_id**: 530076
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5720
- **genres** / **language**: Horror, Comedy / en
- **overview**: Disaster strikes when the egotistical CEO of an edible cutlery company leads her long-suffering staff on a corporate team-building trip in New Mexico. Trapped underground, this mismatched and disgruntled group must pull together to survive.
- **跳转**: https://themoviecosmos.com/movie/530076
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-1, how-0, how-1, result-2] · sim=0.4963 · **命中分=4**
  - THE-LOVER/p2: fragments=[why-0, why-1, how-0, how-1, how-2, result-1, result-2] · sim=0.5441 · **命中分=7**
  - THE-HERO/p3: fragments=[why-1, how-0, how-1, result-1] · sim=0.5720 · **命中分=4**
- **pseudo命中分合计**: 15
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 11 -->
### Let My Puppets Come (1976) [THE-JESTER, THE-CREATOR] [优质·多agent]
- **tmdb_id**: 223922
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0833
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5195
- **genres** / **language**: Comedy, Music / en
- **overview**: The three chief executives of Creative Concepts Systems &amp; Procedures Brothers Unlimited Inc. of New York are in hot water as their latest venture has been a huge failure, and their Mafia investor, "Mr. Big", wants his $500,000 within 24 hours, or else. So Jimmy, a courier who over hears their plight, suggests they make a porno movie as an easy way of getting back the lost money.
- **跳转**: https://themoviecosmos.com/movie/223922
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4235
  - THE-CREATOR/p1: fragments=[why-0, why-1, how-0, how-1, how-2, result-0] · sim=0.5195 · **命中分=6**
- **pseudo命中分合计**: 11
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 11 -->
### Another World (2022) [THE-MAGICIAN, THE-RULER]
- **tmdb_id**: 664506
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5138
- **genres** / **language**: Drama / fr
- **overview**: An executive manager, his wife and his family, at the point when his professional choices are about to overturn all their lives. Philippe Lemesle and his wife are separating, their love irretrievably damaged by pressures of work. A successful executive in industrial conglomerate, Philippe no longer knows how to respond to the contradictory demands of his bosses. Yesterday they wanted a manager, today an enforcer. Now he must decide what his life really means.
- **跳转**: https://themoviecosmos.com/movie/664506
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p2: fragments=[why-1, how-2, result-1, result-3] · sim=0.5138 · **命中分=4**
  - THE-RULER/p3: fragments=[why-0, why-1, how-0, result-0, result-1, how-1, result-2] · sim=0.5082 · **命中分=7**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 7 -->
### The Conference (2023) [THE-SAGE, THE-CAREGIVER]
- **tmdb_id**: 1161048
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5076
- **genres** / **language**: Horror, Comedy / sv
- **overview**: A ragtag group of public sector employees battle not only their own discord but also a bloodthirsty killer during a seemingly innocuous retreat.
- **跳转**: https://themoviecosmos.com/movie/1161048
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-SAGE/p2: fragments=[how-1, result-2, how-2] · sim=0.4613 · **命中分=3**
  - THE-CAREGIVER/p3: fragments=[how-2, result-0, result-2, result-3] · sim=0.5076 · **命中分=4**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 3 candidate(s)

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 6 -->
### Les SEGPA (2022) [THE-RULER]
- **tmdb_id**: 922705
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5325
- **genres** / **language**: Comedy / fr
- **overview**: SEGPAs are fired from their establishment. To their surprise, they joined the prestigious Franklin D. Roosevelt. The Principal, reluctant to see his school's reputation deteriorate, imagines a ploy to fire SEGPA while retaining aid.
- **跳转**: https://themoviecosmos.com/movie/922705
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p1: fragments=[why-0, why-1, how-0, how-1, result-1, result-2] · sim=0.5325 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 5 -->
### The Andromeda Strain (1971) [THE-JESTER]
- **tmdb_id**: 10514
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5043
- **genres** / **language**: Science Fiction, Thriller / en
- **overview**: When virtually all of the residents of Piedmont, New Mexico, are found dead after the return to Earth of a space satellite, the head of the US Air Force's Project Scoop declares an emergency. A group of eminent scientists led by Dr. Jeremy Stone scramble to a secure laboratory and try to first isolate the life form while determining why two people from Piedmont - an old alcoholic and a six-month-old baby - survived. The scientists methodically study the alien life form unaware that it has already mutated and presents a far greater danger in the lab, which is equipped with a nuclear self-destruct device designed to prevent the escape of dangerous biological agents.
- **跳转**: https://themoviecosmos.com/movie/10514
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p2: fragments=[how-0, why-1, how-1, result-0, result-2] · sim=0.5043 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 5 -->
### Discount (2014) [THE-JESTER]
- **tmdb_id**: 313055
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5116
- **genres** / **language**: Comedy / fr
- **overview**: To fight against the introduction of automatic checkouts that threaten their jobs, staff members at Hard Discounts secretly create their own "Alternative Discount" outlet by salvaging products that would otherwise have been wasted.
- **跳转**: https://themoviecosmos.com/movie/313055
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p3: fragments=[why-0, how-0, result-1, result-3, result-2] · sim=0.5116 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
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

**Count:** 10 candidate(s)

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 36 -->
### Election (1999) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-JESTER, THE-CREATOR] [优质·多agent]
- **tmdb_id**: 9451
- **quality_candidate**: true
- **neutral_hits**: 10
- **neutral_total**: 11
- **neutral_hit_rate**: 0.9091
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5783
- **genres** / **language**: Comedy, Drama / en
- **overview**: Tracy Flick is running unopposed for this year’s high school student election. But Jim McAllister has a different plan. Partly to establish a more democratic election, and partly to satisfy some deep personal anger toward Tracy, Jim talks football player Paul Metzler to run for president as well.
- **跳转**: https://themoviecosmos.com/movie/9451
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[why-0, how-0, result-0] · sim=0.4968
  - THE-EVERYMAN/n1: fragments=[why-0, how-0, result-0] · sim=0.4901
  - THE-HERO/n1: fragments=[why-0, how-0, result-0] · sim=0.4976
  - THE-CAREGIVER/n1: fragments=[why-0, how-0, result-0] · sim=0.4979
  - THE-EXPLORER/n1: fragments=[why-0, how-0, result-0] · sim=0.4932
  - THE-OUTLAW/n1: fragments=[why-0, how-0, result-0] · sim=0.4938
  - THE-RULER/n1: fragments=[why-0, how-0, result-0] · sim=0.4980
  - THE-MAGICIAN/n1: fragments=[why-0, how-0, result-0] · sim=0.4956
  - THE-SAGE/n1: fragments=[why-0, how-0, result-0] · sim=0.4933
  - THE-JESTER/n1: fragments=[why-0, how-0, result-0] · sim=0.4983
  - THE-CREATOR/p3: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5783 · **命中分=6**
- **pseudo命中分合计**: 36
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 32 -->
### Gli onorevoli (1963) [THE-INNOCENT, THE-EVERYMAN, THE-EXPLORER, THE-SAGE, THE-CAREGIVER, THE-RULER]
- **tmdb_id**: 64946
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 6
- **优质候选**: false
- **distinct_agents**: 6
- **相似度**: 0.5920
- **genres** / **language**: Comedy / it
- **overview**: Some political candidates are determined to win the electors' preference during an election campaign in Italy.
- **跳转**: https://themoviecosmos.com/movie/64946
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.4915 · **命中分=6**
  - THE-EVERYMAN/p1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5115 · **命中分=6**
  - THE-EXPLORER/p1: fragments=[why-0, why-1, how-0, result-1, result-2] · sim=0.5247 · **命中分=5**
  - THE-SAGE/p1: fragments=[why-1, how-0, result-0] · sim=0.5032 · **命中分=3**
  - THE-CAREGIVER/p2: fragments=[why-1, result-0, result-1, result-2] · sim=0.5298 · **命中分=4**
  - THE-RULER/p3: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5920 · **命中分=5**
  - THE-SAGE/p3: fragments=[why-0, why-1, result-0] · sim=0.5557 · **命中分=3**
- **pseudo命中分合计**: 32
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 27 -->
### Machete (2010) [THE-HERO, THE-RULER, THE-MAGICIAN, THE-JESTER, THE-INNOCENT]
- **tmdb_id**: 23631
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 5
- **优质候选**: false
- **distinct_agents**: 5
- **相似度**: 0.5632
- **genres** / **language**: Action, Comedy, Thriller / en
- **overview**: After being set-up and betrayed by the man who hired him to assassinate a Texas Senator, an ex-Federale launches a brutal rampage of revenge against his former boss.
- **跳转**: https://themoviecosmos.com/movie/23631
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[why-0, why-1, how-0, result-0, result-2] · sim=0.5283 · **命中分=5**
  - THE-RULER/p1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5632 · **命中分=6**
  - THE-MAGICIAN/p1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5546 · **命中分=6**
  - THE-JESTER/p1: fragments=[why-1, how-0, result-0, result-1, result-2] · sim=0.5599 · **命中分=5**
  - THE-INNOCENT/p2: fragments=[why-0, why-1, result-0, result-1, result-2] · sim=0.5435 · **命中分=5**
- **pseudo命中分合计**: 27
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 很牵强。low 2
- **历史打分**: （phase3.5 / 2 / 双重） （phase3.6 / 2 / 双重 / 很牵强。low 2）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 24 -->
### The Independent (2022) [THE-HERO, THE-MAGICIAN, THE-SAGE, THE-EXPLORER, THE-RULER]
- **tmdb_id**: 878183
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 5
- **优质候选**: false
- **distinct_agents**: 5
- **相似度**: 0.6334
- **genres** / **language**: Thriller, Mystery, Crime / en
- **overview**: It's the final weeks of the most consequential presidential election in history. America is poised to elect either its first female president or its first viable independent candidate. Reporting history as it's made, an idealistic young journalist teams up with her idol, legendary journalist Nick Booker, to uncover a conspiracy that places the fate of the election, and the country, in their hands.
- **跳转**: https://themoviecosmos.com/movie/878183
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p2: fragments=[why-1, how-0, result-0, result-1, result-2] · sim=0.6334 · **命中分=5**
  - THE-MAGICIAN/p2: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5470 · **命中分=6**
  - THE-SAGE/p2: fragments=[why-0, result-1, result-2] · sim=0.5149 · **命中分=3**
  - THE-EXPLORER/p3: fragments=[how-0, why-0, result-0, result-1, result-2] · sim=0.5657 · **命中分=5**
  - THE-RULER/p3: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5773 · **命中分=5**
- **pseudo命中分合计**: 24
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 20 -->
### Long Live Freedom (2013) [THE-CAREGIVER, THE-EXPLORER, THE-CREATOR, THE-RULER]
- **tmdb_id**: 167221
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.6135
- **genres** / **language**: Comedy, Drama / it
- **overview**: Elections are approaching and things don't look too good for the opposition. Their leader can't stand the pressure and disappears. To avoid a scandal, the upper echelons of the party concoct a risky plan: to replace him with his identical twin, a philosopher with BPD, whose eclectic ideas and direct approach unexpectedly make the party surge in the polls.
- **跳转**: https://themoviecosmos.com/movie/167221
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5544 · **命中分=4**
  - THE-EXPLORER/p2: fragments=[why-0, why-1, result-0, result-1, result-2] · sim=0.6135 · **命中分=5**
  - THE-CREATOR/p2: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5409 · **命中分=6**
  - THE-RULER/p2: fragments=[why-1, how-0, result-0, result-1, result-2] · sim=0.5576 · **命中分=5**
- **pseudo命中分合计**: 20
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 17 -->
### Swing Vote (2008) [THE-EVERYMAN, THE-MAGICIAN, THE-EXPLORER]
- **tmdb_id**: 10187
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5650
- **genres** / **language**: Comedy, Drama / en
- **overview**: In a remarkable turn of events, the result of the presidential election comes down to one man's vote.
- **跳转**: https://themoviecosmos.com/movie/10187
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.4923 · **命中分=6**
  - THE-MAGICIAN/p2: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5650 · **命中分=6**
  - THE-EXPLORER/p3: fragments=[how-0, why-0, result-0, result-1, result-2] · sim=0.5484 · **命中分=5**
- **pseudo命中分合计**: 17
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 15 -->
### Lone Star (1952) [THE-CREATOR, THE-INNOCENT, THE-RULER] [优质·多agent]
- **tmdb_id**: 37593
- **quality_candidate**: true
- **neutral_hits**: 1
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0909
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5900
- **genres** / **language**: Western / en
- **overview**: Cattle baron Devereaux Burke is enlisted by an aging Andrew Jackson to dissuade Sam Houston from establishing Texas as a republic. Burke must fight state senator Thomas Craden, in the process winning the heart of Craden's newspaper-editor girlfriend Martha Ronda.
- **跳转**: https://themoviecosmos.com/movie/37593
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/n1: fragments=[why-0, how-0, result-0] · sim=0.4952
  - THE-INNOCENT/p1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.4912 · **命中分=6**
  - THE-RULER/p1: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5900 · **命中分=6**
- **pseudo命中分合计**: 15
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 
- **历史打分**: （phase3.6 / 2 / 双重） （phase3.7 / 2 / 双重）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 15 -->
### The Campaign (2012) [THE-HERO, THE-CAREGIVER, THE-CREATOR]
- **tmdb_id**: 77953
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5654
- **genres** / **language**: Comedy / en
- **overview**: Two rival politicians compete to win an election to represent their small North Carolina congressional district in the United States House of Representatives.
- **跳转**: https://themoviecosmos.com/movie/77953
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p2: fragments=[why-1, how-0, result-0, result-1, result-2] · sim=0.5654 · **命中分=5**
  - THE-CAREGIVER/p2: fragments=[why-1, result-0, result-1, result-2] · sim=0.5411 · **命中分=4**
  - THE-CREATOR/p2: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5630 · **命中分=6**
- **pseudo命中分合计**: 15
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 15 -->
### Game Change (2012) [THE-CAREGIVER, THE-INNOCENT, THE-CREATOR]
- **tmdb_id**: 91010
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5899
- **genres** / **language**: TV Movie, Drama, Comedy, History / en
- **overview**: During the Republican run of the 2008 Presidential election, candidate John McCain picks a relative unknown, Alaskan governor Sarah Palin, to be his running mate.  As the campaign kicks into high gear, her lack of experience, in both political and media savvy, becomes a drain upon McCain and his strategists.
- **跳转**: https://themoviecosmos.com/movie/91010
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5899 · **命中分=4**
  - THE-INNOCENT/p2: fragments=[why-0, why-1, result-0, result-1, result-2] · sim=0.5532 · **命中分=5**
  - THE-CREATOR/p3: fragments=[why-0, why-1, how-0, result-0, result-1, result-2] · sim=0.5770 · **命中分=6**
- **pseudo命中分合计**: 15
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 10 -->
### Gabriel Over the White House (1933) [THE-EXPLORER, THE-JESTER]
- **tmdb_id**: 100420
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.6181
- **genres** / **language**: Drama, Fantasy, Romance / en
- **overview**: A political hack becomes President during the height of the Depression and undergoes a metamorphosis into an incorruptible statesman after a near-fatal accident.
- **跳转**: https://themoviecosmos.com/movie/100420
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p2: fragments=[why-0, why-1, result-0, result-1, result-2] · sim=0.6181 · **命中分=5**
  - THE-JESTER/p2: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.6104 · **命中分=5**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 4 candidate(s)

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 5 -->
### Man of the Year (2006) [THE-JESTER]
- **tmdb_id**: 9895
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5918
- **genres** / **language**: Comedy, Romance, Thriller / en
- **overview**: The irreverent host of a political satire talk show decides to run for president and expose corruption in Washington. His stunt goes further than he expects when he actually wins the election, but a software engineer suspects that a computer glitch is responsible for his surprising victory.
- **跳转**: https://themoviecosmos.com/movie/9895
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p2: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5918 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 5 -->
### Unlikely Revolutionaries (2010) [THE-JESTER]
- **tmdb_id**: 56041
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5925
- **genres** / **language**: Comedy / it
- **overview**: Five ordinary people disillusioned with politics—a perennial temp, a docker, a university professor, a TV reporter, and a convict—decide to kidnap a politician, to dispense justice and use the ransom money to compensate the family of a blue-collar worker who died in workplace accident.
- **跳转**: https://themoviecosmos.com/movie/56041
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p3: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5925 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 5 -->
### Koltuk Belası (1990) [THE-JESTER]
- **tmdb_id**: 436068
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6033
- **genres** / **language**: Comedy / tr
- **overview**: Political satire comedy featuring the memories of a red leather chair. He is aware that no matter who the next governor will be, more corrupted will the system get. But only until the last governor who decides to set him on fire.
- **跳转**: https://themoviecosmos.com/movie/436068
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p3: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.6033 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 5 -->
### The Honest Candidate (2024) [THE-RULER]
- **tmdb_id**: 1278099
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5883
- **genres** / **language**: Comedy / es
- **overview**: A former idealistic leader turned corrupt politician is cursed by his grandmother on the eve of the presidential election, forcing him to be honest. Can he win without lies and what will be the conditions?
- **跳转**: https://themoviecosmos.com/movie/1278099
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p2: fragments=[why-1, how-0, result-0, result-1, result-2] · sim=0.5883 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
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

**Count:** 8 candidate(s)

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 13 -->
### Scandal (1950) [THE-LOVER, THE-MAGICIAN, THE-SAGE]
- **tmdb_id**: 32690
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5880
- **genres** / **language**: Drama / ja
- **overview**: A celebrity photograph sparks a court case as a tabloid magazine spins a scandalous yarn over a painter and a famous singer.
- **跳转**: https://themoviecosmos.com/movie/32690
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p2: fragments=[why-0, how-0, how-1, result-0] · sim=0.5880 · **命中分=4**
  - THE-MAGICIAN/p3: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5754 · **命中分=5**
  - THE-SAGE/p3: fragments=[how-0, how-1, result-0, result-1] · sim=0.5629 · **命中分=4**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 13 -->
### The Hater (2020) [THE-EVERYMAN, THE-HERO, THE-CREATOR]
- **tmdb_id**: 590854
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.6054
- **genres** / **language**: Drama, Thriller / pl
- **overview**: A duplicitous young man finds success in the dark world of social media smear tactics — but his virtual vitriol soon has violent real-life consequences.
- **跳转**: https://themoviecosmos.com/movie/590854
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6020 · **命中分=5**
  - THE-HERO/p1: fragments=[why-0, how-0, how-1, result-0] · sim=0.6054 · **命中分=4**
  - THE-CREATOR/p3: fragments=[how-0, how-1, result-0, result-1] · sim=0.5777 · **命中分=4**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 10 -->
### Eternal Evil (1985) [THE-INNOCENT, THE-RULER]
- **tmdb_id**: 87110
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.6001
- **genres** / **language**: Horror, Science Fiction / en
- **overview**: A dissatisfied Montreal director of TV commercials is taught to astrally project himself by a mysterious woman. But soon he finds that he does it against his will when he sleeps, and while he does it, he commits savage acts against those in his life.
- **跳转**: https://themoviecosmos.com/movie/87110
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5755 · **命中分=5**
  - THE-RULER/p2: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6001 · **命中分=5**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 9 -->
### Cobweb (2023) [THE-LOVER, THE-SAGE]
- **tmdb_id**: 901121
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.6463
- **genres** / **language**: Comedy, Drama / ko
- **overview**: In the 1970s, Director Kim is obsessed by the desire to re-shoot the ending of his completed film Cobweb, but chaos and turmoil grip the set with interference from the censorship authorities, and the complaints of actors and producers who can't understand the re-written ending. Will Kim be able to find a way through this chaos to fulfill his artistic ambitions and complete his masterpiece?
- **跳转**: https://themoviecosmos.com/movie/901121
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1: fragments=[why-0, how-0, how-1, result-1] · sim=0.6463 · **命中分=4**
  - THE-SAGE/p1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5942 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 8 -->
### One Way (2006) [THE-CAREGIVER, THE-RULER]
- **tmdb_id**: 7298
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.6148
- **genres** / **language**: Crime, Mystery, Thriller / en
- **overview**: To cover up his infidelities and protect his upcoming marriage, a star advertiser helps free an accused rapist by giving a false alibi and suffers the brutal revenge of the victim.
- **跳转**: https://themoviecosmos.com/movie/7298
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p2: fragments=[why-0, how-0, result-1] · sim=0.5951 · **命中分=3**
  - THE-RULER/p2: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6148 · **命中分=5**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 8 -->
### I Like Mountain Music (1933) [THE-CREATOR, THE-JESTER]
- **tmdb_id**: 151913
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5901
- **genres** / **language**: Animation, Comedy, Family, Music / en
- **overview**: After hours, individuals on various magazine covers in a drugstore come to life and sing, speak, or perform. Caricature celebrity depictions include George Arliss, Eddie Cantor, Sonja Henie, Benito Mussolini, Ignacy Paderewski, Edward G. Robinson, Will Rogers, and Ed Wynn. A robbery sequence features bad guys breaking into the cash register and Sherlock Holmes and Dr. Watson on the case. King Kong also makes an appearance. A Merrie Melody cartoon.
- **跳转**: https://themoviecosmos.com/movie/151913
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p2: fragments=[why-0, how-0, how-1] · sim=0.5864 · **命中分=3**
  - THE-JESTER/p3: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5901 · **命中分=5**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 8 -->
### Restless (2022) [THE-EVERYMAN, THE-HERO]
- **tmdb_id**: 928381
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.6175
- **genres** / **language**: Action, Thriller, Crime / fr
- **overview**: After going to extremes to cover up an accident, a corrupt cop's life spirals out of control when he starts receiving threats from a mysterious witness.
- **跳转**: https://themoviecosmos.com/movie/928381
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p2: fragments=[why-0, how-0, how-1, result-0] · sim=0.5400 · **命中分=4**
  - THE-HERO/p2: fragments=[why-0, how-1, result-0, result-1] · sim=0.6175 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 8 -->
### Inside Man (2023) [THE-EVERYMAN, THE-HERO]
- **tmdb_id**: 1020662
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.6220
- **genres** / **language**: Crime, Thriller, Drama / en
- **overview**: Based on true events. A disgraced police detective seeking redemption goes undercover to expose a violent crime syndicate. But as he sinks deeper into the mob, the price for absolution may be higher than he can afford.
- **跳转**: https://themoviecosmos.com/movie/1020662
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p2: fragments=[why-0, how-0, how-1, result-0] · sim=0.5848 · **命中分=4**
  - THE-HERO/p2: fragments=[why-0, how-1, result-0, result-1] · sim=0.6220 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 7 candidate(s)

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### He Who Gets Slapped (1924) [THE-JESTER]
- **tmdb_id**: 27511
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6022
- **genres** / **language**: Drama, Thriller, Romance / en
- **overview**: After a baron steals his scientific discoveries, runs away with his wife, and slaps him in public, a man joins a Parisian circus sideshow as a clown whose act consists of being slapped repeatedly and becomes infatuated with a showgirl colleague whose father intends to marry her off to the baron.
- **跳转**: https://themoviecosmos.com/movie/27511
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6022 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### The Sinister Urge (1960) [THE-JESTER]
- **tmdb_id**: 31286
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5959
- **genres** / **language**: Crime, Thriller / en
- **overview**: A flunky for a porno movie ring starts murdering the smut films' lead actresses.
- **跳转**: https://themoviecosmos.com/movie/31286
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p3: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5959 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Natural Born Pranksters (2016) [THE-JESTER]
- **tmdb_id**: 383524
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6022
- **genres** / **language**: Comedy / en
- **overview**: The world’s three most notorious, ballsy, and outrageous pranksters come together for the first time to unleash the most epic pranks in an outrageous feature-film event. Jam-packed with cameos from some of YouTube’s biggest stars, watch as Roman Atwood, Dennis Roady, and Vitaly Zdorovetskiy take fearlessness and unbelievable social experiments to the next level.
- **跳转**: https://themoviecosmos.com/movie/383524
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6022 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Ex Libris: The New York Public Library (2017) [THE-EXPLORER]
- **tmdb_id**: 446173
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6137
- **genres** / **language**: Documentary / en
- **overview**: A documentary about how a dominant cultural and demographic institution both sustains their traditional activities and adapts to the digital revolution.
- **跳转**: https://themoviecosmos.com/movie/446173
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p2: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6137 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Kavan (2017) [THE-INNOCENT]
- **tmdb_id**: 449742
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6157
- **genres** / **language**: Thriller, Drama / ta
- **overview**: A budding journalist passionate about ethical, noble, hard-hitting journalism understands the more flourishing ghetto of sensationalism &amp; news fabrication that the Entertainment TV Channel he belongs to, thrives on. When caught in a dilemma of whether to hold for a while or rise in protest, a situation forces him to make a decision that puts him out of work but… there begins his work.
- **跳转**: https://themoviecosmos.com/movie/449742
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6157 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Fyre Fraud (2019) [THE-JESTER]
- **tmdb_id**: 575190
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6041
- **genres** / **language**: Documentary / en
- **overview**: A true-crime comedy exploring a failed music festival turned internet meme at the nexus of social media influence, late-stage capitalism, and morality in the post-truth era.
- **跳转**: https://themoviecosmos.com/movie/575190
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p2: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6041 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Black Money (2019) [THE-SAGE]
- **tmdb_id**: 603314
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6172
- **genres** / **language**: Crime, Drama, Thriller / ko
- **overview**: A prosecutor is falsely accused of sexual assault in a suicide note from a woman that he is convinced was actually murdered. As he investigates her death to clear his name, he realizes that the truth lies in a huge financial scandal.
- **跳转**: https://themoviecosmos.com/movie/603314
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-SAGE/p2: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.6172 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
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

**Count:** 10 candidate(s)

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 123 -->
### Flood (2007) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-JESTER] [优质·多agent]
- **tmdb_id**: 6309
- **quality_candidate**: true
- **neutral_hits**: 12
- **neutral_total**: 12
- **neutral_hit_rate**: 1.0000
- **distinct_agents**: 7
- **优质候选**: true
- **distinct_agents**: 7
- **相似度**: 0.5839
- **genres** / **language**: Drama, Action, Thriller / en
- **overview**: Timely yet terrifying, The Flood predicts the unthinkable. When a raging storm coincides with high seas it unleashes a colossal tidal surge, which travels mercilessly down England's East Coast and into the Thames Estuary. Overwhelming the Barrier, torrents of water pour into the city. The lives of millions of Londoners are at stake.
- **跳转**: https://themoviecosmos.com/movie/6309
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4579
  - THE-EVERYMAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4589
  - THE-HERO/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4598
  - THE-CAREGIVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4525
  - THE-EXPLORER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4598
  - THE-OUTLAW/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4559
  - THE-LOVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4617
  - THE-CREATOR/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4497
  - THE-RULER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4581
  - THE-MAGICIAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4569
  - THE-SAGE/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4635
  - THE-JESTER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4523
  - THE-INNOCENT/p1: fragments=[why-0, how-1, how-2, result-0, result-4, result-5] · sim=0.4962 · **命中分=6**
  - THE-EVERYMAN/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-1, result-3] · sim=0.5027 · **命中分=8**
  - THE-HERO/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1, result-5] · sim=0.5065 · **命中分=7**
  - THE-OUTLAW/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5320 · **命中分=6**
  - THE-RULER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, how-5, result-0, result-1, result-3, result-4, result-5] · sim=0.5403 · **命中分=12**
  - THE-SAGE/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4] · sim=0.5839 · **命中分=6**
  - THE-RULER/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-4] · sim=0.5417 · **命中分=9**
  - THE-JESTER/p2: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-1, result-4, result-5] · sim=0.5637 · **命中分=9**
- **pseudo命中分合计**: 123
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 66 -->
### The Ice Storm (1997) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-JESTER] [优质·多agent]
- **tmdb_id**: 68924
- **quality_candidate**: true
- **neutral_hits**: 12
- **neutral_total**: 12
- **neutral_hit_rate**: 1.0000
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5100
- **genres** / **language**: Drama / en
- **overview**: In the weekend after thanksgiving 1973 the Hood family is skidding out of control. Then an ice storm hits, the worst in a century.
- **跳转**: https://themoviecosmos.com/movie/68924
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4628
  - THE-EVERYMAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4603
  - THE-HERO/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4635
  - THE-CAREGIVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4588
  - THE-EXPLORER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4635
  - THE-OUTLAW/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4619
  - THE-LOVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4623
  - THE-CREATOR/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4576
  - THE-RULER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4581
  - THE-MAGICIAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4603
  - THE-SAGE/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4640
  - THE-JESTER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4563
  - THE-SAGE/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4] · sim=0.5100 · **命中分=6**
- **pseudo命中分合计**: 66
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 29 -->
### The Rescue (2020) [THE-CAREGIVER, THE-CREATOR, THE-EVERYMAN]
- **tmdb_id**: 613658
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.6441
- **genres** / **language**: Drama, Thriller, Action / zh
- **overview**: A rescue unit within the Chinese Coast Guard are forced to overcome their personal differences to resolve a crisis.
- **跳转**: https://themoviecosmos.com/movie/613658
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p2: fragments=[how-3, how-4, result-1, result-2, result-3] · sim=0.6441 · **命中分=5**
  - THE-CREATOR/p2: fragments=[how-1, how-2, how-3, how-4, how-5, result-3, result-4] · sim=0.5228 · **命中分=7**
  - THE-EVERYMAN/p3: fragments=[how-2, how-3, how-4, how-5, result-3, result-5, result-4, result-1] · sim=0.5100 · **命中分=8**
  - THE-CREATOR/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-1, result-3, result-4] · sim=0.6213 · **命中分=9**
- **pseudo命中分合计**: 29
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 27 -->
### Road Wars (2015) [THE-EXPLORER, THE-LOVER, THE-INNOCENT]
- **tmdb_id**: 333545
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.6312
- **genres** / **language**: Science Fiction, Action / en
- **overview**: After the earth’s water supply is depleted, the survivors form roving road gangs, armed to the teeth and desperate to find and protect water supplies. But when a new breed of blood-drinking humans emerges, the survivors must contend with a whole new threat to their existence.
- **跳转**: https://themoviecosmos.com/movie/333545
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-1, result-2, result-3, result-4] · sim=0.6312 · **命中分=10**
  - THE-LOVER/p1: fragments=[why-0, how-1, how-2, how-3, how-4, how-5, result-0, result-1, result-2, result-3, result-4, result-5] · sim=0.6023 · **命中分=12**
  - THE-INNOCENT/p2: fragments=[how-0, how-1, how-2, how-3, result-3] · sim=0.5803 · **命中分=5**
- **pseudo命中分合计**: 27
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 24 -->
### Deluge (1933) [THE-HERO, THE-INNOCENT, THE-LOVER]
- **tmdb_id**: 163293
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5603
- **genres** / **language**: Science Fiction, Drama, Thriller / en
- **overview**: A massive earthquake strikes the United States, which destroys the West Coast and unleashes a massive flood that threatens to destroy the East Coast as well.
- **跳转**: https://themoviecosmos.com/movie/163293
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p2: fragments=[how-3, how-4, how-5, result-2, result-3, result-4] · sim=0.5603 · **命中分=6**
  - THE-INNOCENT/p3: fragments=[how-2, result-1, result-2, result-4, result-5] · sim=0.5253 · **命中分=5**
  - THE-LOVER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, how-5, result-0, result-1, result-2, result-3, result-4, result-5] · sim=0.5134 · **命中分=13**
- **pseudo命中分合计**: 24
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 19 -->
### Water Wrackets (1978) [THE-RULER, THE-JESTER]
- **tmdb_id**: 249011
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5536
- **genres** / **language**: Fantasy / en
- **overview**: Multifarious images of a lake are overlaid with water effects and a narrated history of the campaigns fought by the fictional water-wracket army.
- **跳转**: https://themoviecosmos.com/movie/249011
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, how-5, result-3, result-5] · sim=0.5536 · **命中分=9**
  - THE-JESTER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-3, result-4, result-5] · sim=0.5499 · **命中分=10**
- **pseudo命中分合计**: 19
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 19 -->
### Disaster Wars: Earthquake vs. Tsunami (2013) [THE-HERO, THE-LOVER]
- **tmdb_id**: 289214
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5594
- **genres** / **language**: Thriller, Action, Drama, Science Fiction / en
- **overview**: Deep underwater in the Marianas Trench an accident results in a devastating Tsunami that destroys the Hawaiian Islands as it continues toward the west coast. Panic ensues all up and down the western coast of North and South America. In an attempt to lessen its impact, scientists launch an underwater explosion that inadvertently makes the tsunami more powerful and focused on Los Angeles. Scientists rush to a solution while the military begins planning for the worst. Los Angeles begins emergency evacuation. Lives and loves are lost even as a brash young grad student comes up with a solution: start the mother of all earthquakes to counter the rushing torrent and raise the continental shelf off the coast of the United States.
- **跳转**: https://themoviecosmos.com/movie/289214
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p2: fragments=[how-3, how-4, how-5, result-2, result-3, result-4] · sim=0.5594 · **命中分=6**
  - THE-LOVER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, how-5, result-0, result-1, result-2, result-3, result-4, result-5] · sim=0.5059 · **命中分=13**
- **pseudo命中分合计**: 19
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 17 -->
### Raining Cats and Frogs (2003) [THE-LOVER, THE-CREATOR]
- **tmdb_id**: 22624
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5674
- **genres** / **language**: Animation, Fantasy, Adventure / fr
- **overview**: It's a catastrophe! A flood has hit our planet and an unusual group of people are all that remains. Led by Ferdinand, a modern day Noah, this little group have managed to defy the furiously raging elements. People and animals alike are dragged through this incredible whirlpool of an adventure.
- **跳转**: https://themoviecosmos.com/movie/22624
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1: fragments=[why-0, how-1, how-2, how-3, how-4, how-5, result-0, result-1, result-2, result-3, result-4, result-5] · sim=0.5674 · **命中分=12**
  - THE-CREATOR/p1: fragments=[why-0, how-2, result-0, result-1, result-5] · sim=0.5281 · **命中分=5**
- **pseudo命中分合计**: 17
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 14 -->
### The Storm (2009) [THE-CAREGIVER, THE-EXPLORER]
- **tmdb_id**: 29602
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5851
- **genres** / **language**: Drama / nl
- **overview**: A fictional story within the historical context of the disastrous flood that engulfed the Dutch coastal province of Zeeland in 1953. When their farmhouse is destroyed by the flood, teenage mother Julia gets separated from her baby boy, whom she kept hidden in a box. She is saved from drowning by a young air force lieutenant, who agrees to go help looking for Julia's little son.
- **跳转**: https://themoviecosmos.com/movie/29602
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5305 · **命中分=6**
  - THE-EXPLORER/p3: fragments=[why-0, how-1, how-2, how-3, how-4, result-0, result-1, result-4] · sim=0.5851 · **命中分=8**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 13 -->
### Jet Stream (2013) [THE-EVERYMAN, THE-SAGE]
- **tmdb_id**: 210219
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.6179
- **genres** / **language**: Action, Adventure, Drama, Science Fiction, TV Movie / en
- **overview**: A TV weatherman tries to prove his theory that a series of unexplained catastrophes are the result of powerful winds found in the upper atmosphere coming down to ground level. His claims attract the attention of government scientists, who need his help to control the phenomena before it destroys all life on Earth (Locatetv.com)
- **跳转**: https://themoviecosmos.com/movie/210219
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p2: fragments=[why-0, how-3, how-4, how-5, result-2, result-0, result-5, result-4] · sim=0.6179 · **命中分=8**
  - THE-SAGE/p3: fragments=[how-1, result-1, result-2, result-3, result-4] · sim=0.5230 · **命中分=5**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 7 candidate(s)

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 18 -->
### Quel maledetto ponte sull'Elba (1969) [THE-JESTER]
- **tmdb_id**: 285427
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5666
- **genres** / **language**: War / it
- **overview**: Quel maledetto ponte sull'Elba
- **跳转**: https://themoviecosmos.com/movie/285427
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0, result-4, result-5] · sim=0.5666 · **命中分=9**
  - THE-JESTER/p2: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-1, result-4, result-5] · sim=0.5086 · **命中分=9**
- **pseudo命中分合计**: 18
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 10 -->
### Animals United (2010) [THE-EXPLORER]
- **tmdb_id**: 50135
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5918
- **genres** / **language**: Animation, Family, Comedy / de
- **overview**: A group of animals waiting for the annual flood they rely on for food and water discover that the humans, who have been destroying their habitats have built a dam for a leisure resort. The animals endeavour to save the delta and send a message to the humans not to interfere with nature.
- **跳转**: https://themoviecosmos.com/movie/50135
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-1, result-2, result-3, result-4] · sim=0.5918 · **命中分=10**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 10 -->
### Tacoma Narrows Bridge Collapse (1940) [THE-JESTER]
- **tmdb_id**: 147016
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5586
- **genres** / **language**: Documentary / en
- **overview**: The collapse of the bridge was recorded on film by Barney Elliott, owner of a local camera shop. The film shows Leonard Coatsworth leaving the bridge after exiting his car. In 1998, The Tacoma Narrows Bridge Collapse was selected for preservation in the United States National Film Registry by the Library of Congress as being culturally, historically, or aesthetically significant. This footage is still shown to engineering, architecture, and physics students as a cautionary tale. Elliott's original film of the construction and collapse of the bridge was shot at 16 frames a second, on 16mm Kodachrome film, but most copies in circulation are in black and white because newsreels of the day copied the film onto 35 mm black-and-white stock (not to mention, often showed the film at the wrong speed).
- **跳转**: https://themoviecosmos.com/movie/147016
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-3, result-4, result-5] · sim=0.5586 · **命中分=10**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 9 -->
### Morning Departure (1950) [THE-CREATOR]
- **tmdb_id**: 39288
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5700
- **genres** / **language**: Drama / en
- **overview**: The crew of a submarine is trapped on the sea floor when it sinks. How can they be rescued before they run out of air?
- **跳转**: https://themoviecosmos.com/movie/39288
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-1, result-3, result-4] · sim=0.5700 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 8 -->
### I Know What You Did Last Summer (1997) [THE-EXPLORER]
- **tmdb_id**: 3597
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5764
- **genres** / **language**: Horror, Thriller, Mystery / en
- **overview**: After an accident on a winding road, four teens make the fatal mistake of dumping their victim's body into the sea. Exactly one year later, the deadly secret resurfaces as they're stalked by a hook-handed figure.
- **跳转**: https://themoviecosmos.com/movie/3597
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p3: fragments=[why-0, how-1, how-2, how-3, how-4, result-0, result-1, result-4] · sim=0.5764 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 8 -->
### Seattle Superstorm (2012) [THE-EVERYMAN]
- **tmdb_id**: 107100
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6018
- **genres** / **language**: Action, Science Fiction, TV Movie / en
- **overview**: An object is shot down over Seattle and the debris begins to affect the local weather, ultimately threatening the whole world.
- **跳转**: https://themoviecosmos.com/movie/107100
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p2: fragments=[why-0, how-3, how-4, how-5, result-2, result-0, result-5, result-4] · sim=0.6018 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 5 -->
### The Great Raid (2005) [THE-CAREGIVER]
- **tmdb_id**: 13922
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6193
- **genres** / **language**: Action, History, War / en
- **overview**: As World War II rages, the elite Sixth Ranger Battalion is given a mission of heroic proportions: push 30 miles behind enemy lines and liberate over 500 American prisoners of war.
- **跳转**: https://themoviecosmos.com/movie/13922
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p2: fragments=[how-3, how-4, result-1, result-2, result-3] · sim=0.6193 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
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

**Count:** 7 candidate(s)

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 78 -->
### Lords of Scam (2021) [THE-INNOCENT, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-RULER, THE-SAGE, THE-JESTER] [优质·多agent]
- **tmdb_id**: 888917
- **quality_candidate**: true
- **neutral_hits**: 10
- **neutral_total**: 10
- **neutral_hit_rate**: 1.0000
- **distinct_agents**: 4
- **优质候选**: true
- **distinct_agents**: 4
- **相似度**: 0.5298
- **genres** / **language**: Documentary, Crime / fr
- **overview**: This documentary traces the rise and crash of scammers who conned the EU carbon quota system and pocketed millions before turning on one another.
- **跳转**: https://themoviecosmos.com/movie/888917
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4526
  - THE-HERO/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4496
  - THE-CAREGIVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4566
  - THE-EXPLORER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4565
  - THE-OUTLAW/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4638
  - THE-LOVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4468
  - THE-CREATOR/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4512
  - THE-RULER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4667
  - THE-SAGE/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4504
  - THE-JESTER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4440
  - THE-RULER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4932 · **命中分=7**
  - THE-EXPLORER/p2: fragments=[why-0, why-1, how-2, how-3, result-0] · sim=0.5027 · **命中分=5**
  - THE-CREATOR/p2: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5298 · **命中分=8**
  - THE-OUTLAW/p3: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4754 · **命中分=8**
- **pseudo命中分合计**: 78
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 结构和表层好像都有一些联系，但是都不太紧密

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 55 -->
### A Ticket to Space (2006) [THE-INNOCENT, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-RULER, THE-SAGE, THE-JESTER] [优质·多agent]
- **tmdb_id**: 13748
- **quality_candidate**: true
- **neutral_hits**: 10
- **neutral_total**: 10
- **neutral_hit_rate**: 1.0000
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.5305
- **genres** / **language**: Comedy, Science Fiction / fr
- **overview**: Face à l'incompréhension de la population française quant au montant des crédits alloués à la recherche spatiale, le gouvernement lance une vaste opération de communication. En partenariat avec le Centre spatial français, un grand jeu est organisé. "Le ticket pour l'espace", un jeu à gratter, va permettre à deux civils de séjourner dans la station orbitale européenne.
- **跳转**: https://themoviecosmos.com/movie/13748
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4595
  - THE-HERO/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4605
  - THE-CAREGIVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4682
  - THE-EXPLORER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4683
  - THE-OUTLAW/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4714
  - THE-LOVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4528
  - THE-CREATOR/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4634
  - THE-RULER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4664
  - THE-SAGE/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4618
  - THE-JESTER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4632
  - THE-EXPLORER/p2: fragments=[why-0, why-1, how-2, how-3, result-0] · sim=0.5305 · **命中分=5**
- **pseudo命中分合计**: 55
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 34 -->
### The Floorwalker (1916) [THE-CAREGIVER, THE-CREATOR, THE-RULER, THE-INNOCENT, THE-SAGE]
- **tmdb_id**: 53416
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 5
- **优质候选**: false
- **distinct_agents**: 5
- **相似度**: 0.5447
- **genres** / **language**: Comedy / en
- **overview**: An impecunious customer creates chaos in a department store while the manager and his assistant plot to steal the money kept in the establishment's safe.
- **跳转**: https://themoviecosmos.com/movie/53416
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4555 · **命中分=7**
  - THE-CREATOR/p1: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5447 · **命中分=8**
  - THE-RULER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4248 · **命中分=7**
  - THE-INNOCENT/p2: fragments=[why-1, how-0, how-1, how-2, how-3, result-0] · sim=0.4702 · **命中分=6**
  - THE-SAGE/p2: fragments=[how-0, how-1, how-2, why-0, why-1, result-1] · sim=0.4552 · **命中分=6**
- **pseudo命中分合计**: 34
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 34 -->
### The Cop (1970) [THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-CREATOR, THE-SAGE]
- **tmdb_id**: 94376
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 5
- **优质候选**: false
- **distinct_agents**: 5
- **相似度**: 0.5873
- **genres** / **language**: Drama, Crime, Thriller / fr
- **overview**: A crackdown on drugs leads a burned out cop to take the law into his own hands and seek revenge against villainous drug dealers. Word comes down from above that the United States feels French authorities have been lax on their arrests of the dealers. A violent action feature finds the harried inspector battling his colleagues as much as the criminal element targeted for extermination.
- **跳转**: https://themoviecosmos.com/movie/94376
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5873 · **命中分=5**
  - THE-CAREGIVER/p2: fragments=[why-1, how-0, how-1, how-2, result-1] · sim=0.4830 · **命中分=5**
  - THE-HERO/p3: fragments=[how-2, result-0, result-1, why-1] · sim=0.5496 · **命中分=4**
  - THE-EXPLORER/p3: fragments=[why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4801 · **命中分=7**
  - THE-CREATOR/p3: fragments=[why-0, why-1, how-1, how-2, how-3, result-0, result-1] · sim=0.5473 · **命中分=7**
  - THE-SAGE/p3: fragments=[how-2, why-0, result-0, how-3, result-1, how-1] · sim=0.4803 · **命中分=6**
- **pseudo命中分合计**: 34
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 28 -->
### Taxi 4 (2007) [THE-SAGE, THE-INNOCENT, THE-CAREGIVER, THE-CREATOR]
- **tmdb_id**: 2335
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.5164
- **genres** / **language**: Action, Comedy, Crime / fr
- **overview**: Before being extradited to Africa to stand trial, a notorious Belgian criminal is entrusted to the Marseilles police department for less than 24 hours. But the wily crook convinces bumbling policeman Emilien he's a lowly Belgian embassy employee who got railroaded by the brilliant master criminal.
- **跳转**: https://themoviecosmos.com/movie/2335
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-SAGE/p1: fragments=[how-0, how-1, how-2, how-3, why-1, why-0, result-0, result-1] · sim=0.4514 · **命中分=8**
  - THE-INNOCENT/p3: fragments=[why-1, how-0, how-1, how-2, how-3, result-0] · sim=0.5164 · **命中分=6**
  - THE-CAREGIVER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4540 · **命中分=7**
  - THE-CREATOR/p3: fragments=[why-0, why-1, how-1, how-2, how-3, result-0, result-1] · sim=0.5030 · **命中分=7**
- **pseudo命中分合计**: 28
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 26 -->
### Special Section (1975) [THE-OUTLAW, THE-LOVER, THE-INNOCENT, THE-CAREGIVER]
- **tmdb_id**: 79921
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.5226
- **genres** / **language**: Drama, History, Thriller / fr
- **overview**: In Nazi-occupied France, a German officer is assassinated. The Germans demand justice, and the Vichy government is quick to capitulate. Unable to apprehend the actual culprits, Minister of Justice Joseph Barthélémy decides the execution of token Frenchmen will suffice, but the problem is finding judges and jurors eager to participate in a sham trial of innocent men. The solution is a Special Section, a court comprised of individuals handpicked for this exact purpose.
- **跳转**: https://themoviecosmos.com/movie/79921
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p2: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5015 · **命中分=8**
  - THE-LOVER/p2: fragments=[why-0, why-1, how-3, result-0, result-1] · sim=0.5226 · **命中分=5**
  - THE-INNOCENT/p3: fragments=[why-1, how-0, how-1, how-2, how-3, result-0] · sim=0.5105 · **命中分=6**
  - THE-CAREGIVER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4407 · **命中分=7**
- **pseudo命中分合计**: 26
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 11 -->
### Gabbar Is Back (2015) [THE-CAREGIVER, THE-JESTER]
- **tmdb_id**: 337876
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5409
- **genres** / **language**: Drama, Action / hi
- **overview**: A vigilante network taking out corrupt officials draws the notice of the authorities.
- **跳转**: https://themoviecosmos.com/movie/337876
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p2: fragments=[why-1, how-0, how-1, how-2, result-1] · sim=0.4475 · **命中分=5**
  - THE-JESTER/p2: fragments=[why-0, why-1, how-2, how-3, result-0, result-1] · sim=0.5409 · **命中分=6**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 10 candidate(s)

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 8 -->
### 711 Ocean Drive (1950) [THE-CREATOR]
- **tmdb_id**: 37087
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5251
- **genres** / **language**: Crime / en
- **overview**: A telephone repairman in Los Angeles uses his knowledge of electronics to help a bookie set up a betting operation. After the bookie is murdered, the greedy technician takes over his business. He ruthlessly climbs his way to the top of the local crime syndicate, but then gangsters from a big East Coast mob show up wanting a piece of his action.
- **跳转**: https://themoviecosmos.com/movie/37087
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p1: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5251 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 8 -->
### Do Detectives Think? (1927) [THE-JESTER]
- **tmdb_id**: 50868
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5605
- **genres** / **language**: Comedy / en
- **overview**: An escaped convict is out to kill the judge who sentenced him. Two inept detectives are hired to guard the judge.
- **跳转**: https://themoviecosmos.com/movie/50868
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p3: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5605 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 8 -->
### Bounty Killer (2013) [THE-OUTLAW]
- **tmdb_id**: 209504
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5348
- **genres** / **language**: Action, Science Fiction / en
- **overview**: It’s been 20 years since the corporations took over the world’s governments. Their thirst for power and profits led to the Corporate Wars, a fierce global battle that laid waste to society as we know it. Born from the ash, the Council of Nine rose as a new law and order for this dark age. To avenge the corporations’ reckless destruction, the Council issues death warrants for all white collar criminals. Their hunters—the bounty killer. From amateur savage to graceful assassin, the bounty killers now compete for body count, fame and a fat stack of cash. They’re ending the plague of corporate greed and providing the survivors of the apocalypse with retribution. These are the new heroes. This is the age of the BOUNTY KILLER.
- **跳转**: https://themoviecosmos.com/movie/209504
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p1: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5348 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 效果不是特别好，low 2
- **历史打分**: （phase3.6 / 2 / 双重 / 效果不是特别好，low 2） （phase3.7 / 2 / 双重）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 8 -->
### Vanguard (2020) [THE-OUTLAW]
- **tmdb_id**: 604822
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5178
- **genres** / **language**: Action, Adventure, Comedy, Crime, Thriller / zh
- **overview**: Covert security company Vanguard is the last hope of survival for an accountant after he is targeted by the world's deadliest mercenary organization.
- **跳转**: https://themoviecosmos.com/movie/604822
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p2: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5178 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 8 -->
### C’era una volta il crimine (2022) [THE-JESTER]
- **tmdb_id**: 790529
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5409
- **genres** / **language**: Comedy / it
- **overview**: C’era una volta il crimine
- **跳转**: https://themoviecosmos.com/movie/790529
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p3: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5409 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 这种因为overview缺失所以用标题填补的是要直接抛弃的

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### ATM (2012) [THE-LOVER]
- **tmdb_id**: 104651
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5243
- **genres** / **language**: Romance, Comedy / th
- **overview**: Two enamoured employees in a bank with no fraternization policy must recover their company's lost money while trying to keep their relationship a secret.
- **跳转**: https://themoviecosmos.com/movie/104651
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5243 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### Pretty Thing (2025) [THE-LOVER]
- **tmdb_id**: 1223690
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5221
- **genres** / **language**: Thriller, Drama / en
- **overview**: A successful executive fights back when a scorned young lover takes his obsession too far.
- **跳转**: https://themoviecosmos.com/movie/1223690
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5221 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 6 -->
### No One Will Know (2025) [THE-JESTER]
- **tmdb_id**: 1205648
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5151
- **genres** / **language**: Drama, Thriller / fr
- **overview**: All begins in a rundown bar outside of Paris where a regular man realizes he has a winning lottery ticket only to be shot in a crime that needs to be quickly covered up.
- **跳转**: https://themoviecosmos.com/movie/1205648
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-1] · sim=0.5151 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### Runaway Jury (2003) [THE-HERO]
- **tmdb_id**: 11329
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5252
- **genres** / **language**: Drama, Thriller / en
- **overview**: After a workplace shooting in New Orleans, a trial against the gun manufacturer pits lawyer Wendell Rohr against shady jury consultant Rankin Fitch, who uses illegal means to stack the jury with people sympathetic to the defense. But when juror Nicholas Easter and his girlfriend Marlee reveal their ability to sway the jury into delivering any verdict they want, a high-stakes cat-and-mouse game begins.
- **跳转**: https://themoviecosmos.com/movie/11329
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5252 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### Don't. Get. Out! (2018) [THE-LOVER]
- **tmdb_id**: 497223
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5313
- **genres** / **language**: Thriller / de
- **overview**: Taking his kids to school with the car, Berlin real estate developer Karl gets a call from a blackmailer: If he doesn’t pay up, the car will blow up. A deadly race against time begins.
- **跳转**: https://themoviecosmos.com/movie/497223
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p2: fragments=[why-0, why-1, how-3, result-0, result-1] · sim=0.5313 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
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

**Count:** 9 candidate(s)

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 80 -->
### Transpecos (2016) [THE-EVERYMAN, THE-HERO, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-CAREGIVER]
- **tmdb_id**: 381018
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 10
- **优质候选**: false
- **distinct_agents**: 10
- **相似度**: 0.5895
- **genres** / **language**: Thriller / en
- **overview**: For three US Border Patrol agents, the contents of one car reveal an insidious plot within their own ranks. The next 24 hours may cost them their lives.
- **跳转**: https://themoviecosmos.com/movie/381018
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4762 · **命中分=4**
  - THE-HERO/p1: fragments=[why-0, how-0, result-0] · sim=0.5490 · **命中分=3**
  - THE-EXPLORER/p1: fragments=[why-0, how-0, result-0] · sim=0.4839 · **命中分=3**
  - THE-OUTLAW/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5211 · **命中分=4**
  - THE-LOVER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5719 · **命中分=4**
  - THE-CREATOR/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5022 · **命中分=4**
  - THE-RULER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4831 · **命中分=4**
  - THE-MAGICIAN/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4720 · **命中分=4**
  - THE-SAGE/p1: fragments=[why-0, how-0, result-0] · sim=0.4831 · **命中分=3**
  - THE-EVERYMAN/p2: fragments=[why-0, how-0, result-0, result-1] · sim=0.5118 · **命中分=4**
  - THE-HERO/p2: fragments=[how-0, result-0, result-1] · sim=0.5496 · **命中分=3**
  - THE-CAREGIVER/p2: fragments=[why-0, how-0, result-1] · sim=0.5810 · **命中分=3**
  - THE-EXPLORER/p2: fragments=[why-0, how-0, result-1] · sim=0.5078 · **命中分=3**
  - THE-OUTLAW/p2: fragments=[how-0, result-1] · sim=0.5715 · **命中分=2**
  - THE-CREATOR/p2: fragments=[why-0, how-0, result-0, result-1] · sim=0.5895 · **命中分=4**
  - THE-RULER/p2: fragments=[why-0, how-0, result-0, result-1] · sim=0.5147 · **命中分=4**
  - THE-MAGICIAN/p2: fragments=[how-0, result-0, result-1] · sim=0.5296 · **命中分=3**
  - THE-SAGE/p2: fragments=[how-0, result-0, result-1] · sim=0.5451 · **命中分=3**
  - THE-CAREGIVER/p3: fragments=[why-0, how-0, result-0, result-1] · sim=0.4426 · **命中分=4**
  - THE-EXPLORER/p3: fragments=[how-0, result-0, result-1] · sim=0.4830 · **命中分=3**
  - THE-RULER/p3: fragments=[why-0, how-0, result-0, result-1] · sim=0.4566 · **命中分=4**
  - THE-MAGICIAN/p3: fragments=[why-0, how-0, result-0, result-1] · sim=0.5709 · **命中分=4**
  - THE-SAGE/p3: fragments=[why-0, how-0, result-1] · sim=0.4792 · **命中分=3**
- **pseudo命中分合计**: 80
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 在事实和情节层面上联系有些不太紧密
- **历史打分**: （phase3.5 / 2 / 双重） （phase3.6 / 2 / 双重 / 在事实和情节层面上联系有些不太紧密） （phase3.7 / 2 / 双重）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 40 -->
### Stranded (2021) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-JESTER] [优质·多agent]
- **tmdb_id**: 841793
- **quality_candidate**: true
- **neutral_hits**: 12
- **neutral_total**: 12
- **neutral_hit_rate**: 1.0000
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.4772
- **genres** / **language**: Drama / pt
- **overview**: Tensions run high while food runs low as six influencers find themselves stranded on a secluded island after plans for a weekend escape go awry.
- **跳转**: https://themoviecosmos.com/movie/841793
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[why-0, how-0, result-0] · sim=0.4331
  - THE-EVERYMAN/n1: fragments=[why-0, how-0, result-0] · sim=0.4292
  - THE-HERO/n1: fragments=[why-0, how-0, result-0] · sim=0.4366
  - THE-CAREGIVER/n1: fragments=[why-0, how-0, result-0] · sim=0.4331
  - THE-EXPLORER/n1: fragments=[why-0, how-0, result-0] · sim=0.4345
  - THE-OUTLAW/n1: fragments=[why-0, how-0, result-0] · sim=0.4345
  - THE-LOVER/n1: fragments=[why-0, how-0, result-0] · sim=0.4375
  - THE-CREATOR/n1: fragments=[why-0, how-0, result-0] · sim=0.4395
  - THE-RULER/n1: fragments=[why-0, how-0, result-0] · sim=0.4351
  - THE-MAGICIAN/n1: fragments=[why-0, how-0, result-0] · sim=0.4288
  - THE-SAGE/n1: fragments=[why-0, how-0, result-0] · sim=0.4356
  - THE-JESTER/n1: fragments=[why-0, how-0, result-0] · sim=0.4319
  - THE-LOVER/p2: fragments=[why-0, how-0, result-0, result-1] · sim=0.4772 · **命中分=4**
- **pseudo命中分合计**: 40
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **历史打分**: （phase3.6 / 1 / 表层） （phase3.7 / 1 / 结构 / 和现实原型扯得有点远）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 24 -->
### Open the Wall (2014) [THE-INNOCENT, THE-HERO, THE-OUTLAW, THE-LOVER, THE-EXPLORER, THE-SAGE, THE-JESTER]
- **tmdb_id**: 301633
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 7
- **优质候选**: false
- **distinct_agents**: 7
- **相似度**: 0.5496
- **genres** / **language**: Drama, Comedy / de
- **overview**: A lighthearted look at the opening of the border crossing of Bornholmer Straße in Berlin from the point of view of the confused border guards.
- **跳转**: https://themoviecosmos.com/movie/301633
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, how-0, result-0] · sim=0.5327 · **命中分=3**
  - THE-HERO/p1: fragments=[why-0, how-0, result-0] · sim=0.5496 · **命中分=3**
  - THE-OUTLAW/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4861 · **命中分=4**
  - THE-LOVER/p2: fragments=[why-0, how-0, result-0, result-1] · sim=0.4864 · **命中分=4**
  - THE-EXPLORER/p3: fragments=[how-0, result-0, result-1] · sim=0.4723 · **命中分=3**
  - THE-SAGE/p3: fragments=[why-0, how-0, result-1] · sim=0.4646 · **命中分=3**
  - THE-JESTER/p3: fragments=[why-0, how-0, result-0, result-1] · sim=0.5093 · **命中分=4**
- **pseudo命中分合计**: 24
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 18 -->
### A Lien (2023) [THE-EVERYMAN, THE-SAGE, THE-CAREGIVER]
- **tmdb_id**: 1118941
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5123
- **genres** / **language**: Drama / en
- **overview**: On the day of their green card interview, a young couple confronts a dangerous immigration process.
- **跳转**: https://themoviecosmos.com/movie/1118941
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4617 · **命中分=4**
  - THE-SAGE/p1: fragments=[why-0, how-0, result-0] · sim=0.4344 · **命中分=3**
  - THE-EVERYMAN/p2: fragments=[why-0, how-0, result-0, result-1] · sim=0.4846 · **命中分=4**
  - THE-CAREGIVER/p2: fragments=[why-0, how-0, result-1] · sim=0.5123 · **命中分=3**
  - THE-CAREGIVER/p3: fragments=[why-0, how-0, result-0, result-1] · sim=0.4414 · **命中分=4**
- **pseudo命中分合计**: 18
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 10 -->
### Gabbar Is Back (2015) [THE-MAGICIAN, THE-SAGE]
- **tmdb_id**: 337876
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5391
- **genres** / **language**: Drama, Action / hi
- **overview**: A vigilante network taking out corrupt officials draws the notice of the authorities.
- **跳转**: https://themoviecosmos.com/movie/337876
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p2: fragments=[how-0, result-0, result-1] · sim=0.5391 · **命中分=3**
  - THE-SAGE/p2: fragments=[how-0, result-0, result-1] · sim=0.4968 · **命中分=3**
  - THE-MAGICIAN/p3: fragments=[why-0, how-0, result-0, result-1] · sim=0.4969 · **命中分=4**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 9 -->
### Sleep Dealer (2008) [THE-INNOCENT, THE-EXPLORER]
- **tmdb_id**: 20764
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5373
- **genres** / **language**: Drama, Science Fiction, Thriller / en
- **overview**: Set in a near-future, militarized world marked by closed borders, virtual labor and a global digital network that joins minds and experiences, three strangers risk their lives to connect with each other and break the barriers of technology.
- **跳转**: https://themoviecosmos.com/movie/20764
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, how-0, result-0] · sim=0.5373 · **命中分=3**
  - THE-EXPLORER/p1: fragments=[why-0, how-0, result-0] · sim=0.5061 · **命中分=3**
  - THE-EXPLORER/p2: fragments=[why-0, how-0, result-1] · sim=0.5072 · **命中分=3**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 8 -->
### The Weather Underground (2002) [THE-JESTER, THE-CREATOR]
- **tmdb_id**: 14108
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5382
- **genres** / **language**: Documentary / en
- **overview**: The remarkable story of The Weather Underground, radical activists of the 1970s, and of radical politics at its best and most disastrous.
- **跳转**: https://themoviecosmos.com/movie/14108
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p2: fragments=[why-0, how-0, result-0, result-1] · sim=0.5213 · **命中分=4**
  - THE-CREATOR/p3: fragments=[why-0, how-0, result-0, result-1] · sim=0.5382 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 8 -->
### Broken Horses (2015) [THE-LOVER, THE-RULER]
- **tmdb_id**: 319910
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5600
- **genres** / **language**: Thriller, Mystery, Drama, Crime / en
- **overview**: The bonds of brotherhood, the laws of loyalty, and the futility of violence in the shadows of the US Mexico border gang wars.
- **跳转**: https://themoviecosmos.com/movie/319910
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5600 · **命中分=4**
  - THE-RULER/p2: fragments=[why-0, how-0, result-0, result-1] · sim=0.4705 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 8 -->
### 2073 (2024) [THE-MAGICIAN, THE-JESTER]
- **tmdb_id**: 1023915
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5186
- **genres** / **language**: Thriller, Science Fiction / en
- **overview**: Inspired by Chris Marker's iconic 1962 featurette La Jetée; the year is 2073—a not-so-distant dystopian future—and the setting is New San Francisco, the scorched-earth tech-dominant police state where democracy and personal freedom have been well and truly obliterated.
- **跳转**: https://themoviecosmos.com/movie/1023915
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.4653 · **命中分=4**
  - THE-JESTER/p2: fragments=[why-0, how-0, result-0, result-1] · sim=0.5186 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 1 candidate(s)

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 8 -->
### Trade (2007) [THE-RULER]
- **tmdb_id**: 4170
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5217
- **genres** / **language**: Thriller / en
- **overview**: A Texas cop, whose own daughter might have been forced into sexual slavery, joins forces with a Mexican youth to find the boy's sister, who was abducted and forced into prostitution. Meanwhile, a Polish woman who was promised a better life in America also becomes a victim.
- **跳转**: https://themoviecosmos.com/movie/4170
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p1: fragments=[why-0, how-0, result-0, result-1] · sim=0.5217 · **命中分=4**
  - THE-RULER/p3: fragments=[why-0, how-0, result-0, result-1] · sim=0.4092 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 很难评价关联性，且话题敏感。现在看来是一个wobbly 2

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

**Count:** 7 candidate(s)

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 105 -->
### Hurricane Season (2010) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-RULER, THE-MAGICIAN, THE-SAGE] [优质·多agent]
- **tmdb_id**: 32007
- **quality_candidate**: true
- **neutral_hits**: 11
- **neutral_total**: 11
- **neutral_hit_rate**: 1.0000
- **distinct_agents**: 6
- **优质候选**: true
- **distinct_agents**: 6
- **相似度**: 0.5742
- **genres** / **language**: Drama / en
- **overview**: Based on true events amid the wreckage and chaos dealt by Hurricane Katrina; one basketball coach in Marrero, Louisiana just will not give up. Coach Al Collins, gathers other players from hard-hit schools and builds a team actually worthy enough to go to the state playoffs.
- **跳转**: https://themoviecosmos.com/movie/32007
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5373
  - THE-EVERYMAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5338
  - THE-HERO/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5331
  - THE-CAREGIVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5315
  - THE-EXPLORER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5338
  - THE-OUTLAW/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5434
  - THE-LOVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5326
  - THE-CREATOR/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5335
  - THE-RULER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5338
  - THE-MAGICIAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5369
  - THE-SAGE/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5335
  - THE-EVERYMAN/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5515 · **命中分=7**
  - THE-CAREGIVER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5619 · **命中分=7**
  - THE-CREATOR/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5047 · **命中分=7**
  - THE-RULER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5742 · **命中分=7**
  - THE-EVERYMAN/p2: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5627 · **命中分=6**
  - THE-RULER/p2: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5376 · **命中分=7**
  - THE-SAGE/p2: fragments=[why-0, how-3, how-4, result-0] · sim=0.5719 · **命中分=4**
  - THE-EXPLORER/p3: fragments=[why-0, how-1, how-2, how-3, result-0] · sim=0.5476 · **命中分=5**
- **pseudo命中分合计**: 105
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 66 -->
### Fatal Games (1984) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-RULER, THE-MAGICIAN, THE-SAGE] [优质·多agent]
- **tmdb_id**: 30706
- **quality_candidate**: true
- **neutral_hits**: 11
- **neutral_total**: 11
- **neutral_hit_rate**: 1.0000
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.6033
- **genres** / **language**: Horror, Thriller / en
- **overview**: The young athletes of Falcon Academy are training hard to earn their place in the nationals. But when these burgeoning sports stars start disappearing one after the other, Dr. Jordine and his team - who’ve started plying their athletes with new and untested performance-enhancing drugs - are baffled.
- **跳转**: https://themoviecosmos.com/movie/30706
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4913
  - THE-EVERYMAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4847
  - THE-HERO/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4888
  - THE-CAREGIVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4976
  - THE-EXPLORER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4847
  - THE-OUTLAW/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4906
  - THE-LOVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4940
  - THE-CREATOR/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4929
  - THE-RULER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4847
  - THE-MAGICIAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4926
  - THE-SAGE/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4931
  - THE-SAGE/p2: fragments=[why-0, how-3, how-4, result-0] · sim=0.5440 · **命中分=4**
  - THE-CAREGIVER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.6033 · **命中分=7**
- **pseudo命中分合计**: 66
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 39 -->
### Hockey Homicide (1945) [THE-LOVER, THE-CREATOR, THE-MAGICIAN, THE-OUTLAW, THE-RULER, THE-SAGE]
- **tmdb_id**: 66876
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 6
- **优质候选**: false
- **distinct_agents**: 6
- **相似度**: 0.6576
- **genres** / **language**: Animation, Comedy / en
- **overview**: A crowd gathers at the skating rink to watch the big championship hockey game of the Pelicans versus the Aardvarks. Although referee "Clean Game" Kinney does his best to supervise, the hockey game really gets out of hand eventually. Two star players, Bertino and Ferguson, are so anxious, they never get let out of the penalty box, referee Kinney is never able to drop the puck without being physically hurt somehow, and the spectators themselves are so worked into the game, they take out their aggression on the ice while the players relax in the bleachers.
- **跳转**: https://themoviecosmos.com/movie/66876
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p2: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5622 · **命中分=7**
  - THE-CREATOR/p2: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5223 · **命中分=6**
  - THE-MAGICIAN/p2: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5466 · **命中分=6**
  - THE-OUTLAW/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5383 · **命中分=7**
  - THE-RULER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.6576 · **命中分=7**
  - THE-SAGE/p3: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.4993 · **命中分=6**
- **pseudo命中分合计**: 39
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 28 -->
### Hoosiers (1986) [THE-RULER, THE-SAGE, THE-INNOCENT, THE-HERO, THE-CREATOR]
- **tmdb_id**: 5693
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 5
- **优质候选**: false
- **distinct_agents**: 5
- **相似度**: 0.5625
- **genres** / **language**: Drama, Family / en
- **overview**: Failed college coach Norman Dale gets a chance at redemption when he is hired to coach a high school basketball team in a tiny Indiana town. After a teacher persuades star player Jimmy Chitwood to quit and focus on his long-neglected studies, Dale struggles to develop a winning team in the face of community criticism for his temper and his unconventional choice of assistant coach: Shooter, a notorious alcoholic.
- **跳转**: https://themoviecosmos.com/movie/5693
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5459 · **命中分=7**
  - THE-SAGE/p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.4845 · **命中分=4**
  - THE-INNOCENT/p2: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5625 · **命中分=7**
  - THE-HERO/p2: fragments=[how-0, how-1, how-2, result-0] · sim=0.5599 · **命中分=4**
  - THE-CREATOR/p2: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5439 · **命中分=6**
- **pseudo命中分合计**: 28
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 21 -->
### Champions (2018) [THE-INNOCENT, THE-RULER, THE-OUTLAW]
- **tmdb_id**: 456929
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.6100
- **genres** / **language**: Comedy, Family, Drama / es
- **overview**: A disgraced basketball coach is given the chance to coach Los Amigos, a team of players who are intellectually disabled, and soon realizes they just might have what it takes to make it to the national championships.
- **跳转**: https://themoviecosmos.com/movie/456929
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.6100 · **命中分=7**
  - THE-RULER/p2: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.4769 · **命中分=7**
  - THE-OUTLAW/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5245 · **命中分=7**
- **pseudo命中分合计**: 21
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 19 -->
### Goal! Goal! (1964) [THE-LOVER, THE-EXPLORER, THE-RULER]
- **tmdb_id**: 248556
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.6025
- **genres** / **language**: Animation / ru
- **overview**: Two teams, quite different by their techniques, meet in a hockey match.
- **跳转**: https://themoviecosmos.com/movie/248556
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p2: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5509 · **命中分=7**
  - THE-EXPLORER/p3: fragments=[why-0, how-1, how-2, how-3, result-0] · sim=0.5564 · **命中分=5**
  - THE-RULER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.6025 · **命中分=7**
- **pseudo命中分合计**: 19
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 13 -->
### Three Seconds (2017) [THE-MAGICIAN, THE-INNOCENT]
- **tmdb_id**: 444218
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5560
- **genres** / **language**: Drama / ru
- **overview**: The story is set at the 1972 Munich Olympics where the U.S. team lost the basketball championship for the first time in 36 years. The final moments of the final game have become one of the most controversial events in Olympic history. With play tied, the score table horn sounded during a second free throw attempt that put the U.S. ahead by one. But the Soviets claimed they had called for a time out before the basket and confusion ensued. The clock was set back by three seconds twice in a row and the Russians finally prevailed at the very last. The U.S. protested, but a jury decided in the USSR’s favor and Team USA voted unanimously to refuse its silver medals. The Soviet players have been treated as heroes at home.
- **跳转**: https://themoviecosmos.com/movie/444218
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p2: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5419 · **命中分=6**
  - THE-INNOCENT/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5560 · **命中分=7**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 11 candidate(s)

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 7 -->
### Facing the Giants (2006) [THE-INNOCENT]
- **tmdb_id**: 18925
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5550
- **genres** / **language**: Drama / en
- **overview**: A losing coach with an underdog football team faces their giants of fear and failure on and off the field to surprising results.
- **跳转**: https://themoviecosmos.com/movie/18925
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p2: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5550 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 7 -->
### The Two Wizards of the Ball (1970) [THE-INNOCENT]
- **tmdb_id**: 41612
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5645
- **genres** / **language**: Comedy / it
- **overview**: The manager of a football team wants to hire a coach. Luckily the team begin to win but on the eve of an important match the opposing team has their best scorer kidnapped. Will they win the match all the same?
- **跳转**: https://themoviecosmos.com/movie/41612
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5645 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 7 -->
### War of the Dead (2011) [THE-OUTLAW]
- **tmdb_id**: 77068
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5745
- **genres** / **language**: Horror, Action, Adventure / en
- **overview**: Captain Martin Stone is leading a finely-trained, elite platoon of Allied soldiers as they attack an enemy bunker. Underestimating their enemy's strength, they are quickly beaten back into the forest. As they try to regroup, they are suddenly attacked by the same soldiers they had just killed a few minutes earlier. Forced to flee deeper into Russian territory, they discover one of war's most terrifying secrets and realize they have woken up a far more deadlier enemy.
- **跳转**: https://themoviecosmos.com/movie/77068
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p2: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5745 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 7 -->
### Many Wars Ago (1970) [THE-OUTLAW]
- **tmdb_id**: 78101
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5576
- **genres** / **language**: Drama, War / it
- **overview**: Time after time, soldiers of the Italian Army are forced to leave their mountain trenches in attempts to storm an enemy fortress, always with the same disastrous results. As casualties mount, indignation spreads among the rank and file. Disturbed by his superiors' decisions, Lieutenant Sassu is led to question the purpose of war and reconsider where his real duties lie.
- **跳转**: https://themoviecosmos.com/movie/78101
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p2: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5576 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 7 -->
### One Piece: Dream Soccer King! (2002) [THE-INNOCENT]
- **tmdb_id**: 464198
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5490
- **genres** / **language**: Fantasy, Comedy, Animation / ja
- **overview**: At a huge pillar stadium, the Grand Line Cup Final is being held. The "Straw Hat Pirate Team"(Luffy, Zoro, Usopp, Sanji, and Chopper) are having a tie breaker shoot out against the "Villian All Star Team"(Buggy, Bon Clay, Jango, Hatchan, and a soccer like head player named Odacchi). Everyone of them gets a turn in kicking the ball to the goal. While Coby is taking the goalie position, and isn't doing too good in blocking the goal. One after another, the game eventually comes to a sudden death match. Which team will win the Grand Line Cup?
- **跳转**: https://themoviecosmos.com/movie/464198
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5490 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 7 -->
### Bad Boy (2020) [THE-MAGICIAN]
- **tmdb_id**: 674358
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5736
- **genres** / **language**: Action, Crime / pl
- **overview**: The rise and fall of a soccer club owner, discovering the harsh reality of the sport, often connected with crime and fraud.
- **跳转**: https://themoviecosmos.com/movie/674358
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5736 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 7 -->
### Balls Up (2026) [THE-MAGICIAN]
- **tmdb_id**: 1084577
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5901
- **genres** / **language**: Comedy, Action, Adventure / en
- **overview**: Two marketing executives go "balls out" and pitch a bold full‑coverage condom sponsorship with the World Cup. After their drunken celebration in Brazil sparks a global scandal, they must outrun furious fans, criminals, and power-hungry officials to salvage their careers and make it home alive.
- **跳转**: https://themoviecosmos.com/movie/1084577
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p3: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5901 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 7 -->
### Eephus (2025) [THE-CAREGIVER]
- **tmdb_id**: 1226777
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5481
- **genres** / **language**: Drama, Comedy / en
- **overview**: As an imminent construction project looms over their beloved small-town baseball field, a pair of New England rec-league teams face off for the last time. Tensions flare up and ceremonial laughs are shared as an era of camaraderie and escapism fades into an uncertain future.
- **跳转**: https://themoviecosmos.com/movie/1226777
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p2: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5481 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### Butterfly and Sword (1993) [THE-OUTLAW]
- **tmdb_id**: 40166
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5865
- **genres** / **language**: Fantasy, Action, Adventure / cn
- **overview**: A loyalist attempts to keep the King's empire from being overthrown by a revolutionary group.
- **跳转**: https://themoviecosmos.com/movie/40166
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p1: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5865 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### Urotsukidōji III: Return of the Overfiend (1993) [THE-OUTLAW]
- **tmdb_id**: 48628
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6106
- **genres** / **language**: Animation, Horror, Fantasy / ja
- **overview**: As the Overfiend slumbers, the mad emperor Caesar rises to power, enslaving a new race of demon beasts. Into this cruel existence is born the Lord of Chaos, the Overfiend's nemesis. As the blood-thirsty beasts capture the tyrant's daughter in a brutal coup, the Overfiend must awaken to an apocalyptic battle of the Gods.
- **跳转**: https://themoviecosmos.com/movie/48628
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p1: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.6106 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### Your Host (2025) [THE-LOVER]
- **tmdb_id**: 1372260
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5641
- **genres** / **language**: Horror / en
- **overview**: Four friends get trapped in a sadistic game show, forced to outwit a twisted serial killer while racing against time. Every move brings them closer to freedom or a gruesome fate.
- **跳转**: https://themoviecosmos.com/movie/1372260
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p3: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.5641 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

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

**Count:** 6 candidate(s)

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 60 -->
### L'Odissea (1911) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-OUTLAW, THE-LOVER, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-JESTER] [优质·多agent]
- **tmdb_id**: 194224
- **quality_candidate**: true
- **neutral_hits**: 10
- **neutral_total**: 10
- **neutral_hit_rate**: 1.0000
- **distinct_agents**: 2
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.6132
- **genres** / **language**: Drama, Adventure / it
- **overview**: Film adaptation of Homer's 'The Odyssey.'
- **跳转**: https://themoviecosmos.com/movie/194224
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6074
  - THE-EVERYMAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6122
  - THE-HERO/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6132
  - THE-CAREGIVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6123
  - THE-OUTLAW/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6041
  - THE-LOVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6108
  - THE-RULER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6104
  - THE-MAGICIAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6073
  - THE-SAGE/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6130
  - THE-JESTER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6096
  - THE-INNOCENT/p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.5609 · **命中分=4**
  - THE-EVERYMAN/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5625 · **命中分=6**
- **pseudo命中分合计**: 60
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 奥德赛的老电影，有历史加成。
- **历史打分**: （phase3.6 / 2 / 双重 / 奥德赛的老电影，有历史加成。） （phase3.7 / 2 / 双重）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 57 -->
### Don't Leave Home (2018) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-OUTLAW, THE-LOVER, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-JESTER] [优质·多agent]
- **tmdb_id**: 502167
- **quality_candidate**: true
- **neutral_hits**: 10
- **neutral_total**: 10
- **neutral_hit_rate**: 1.0000
- **distinct_agents**: 1
- **优质候选**: true
- **distinct_agents**: 1
- **相似度**: 0.6088
- **genres** / **language**: Thriller, Mystery / en
- **overview**: An American artist's obsession with a disturbing urban legend leads her to an investigation of the story's origins at the crumbling estate of a reclusive painter in Ireland.
- **跳转**: https://themoviecosmos.com/movie/502167
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6088
  - THE-EVERYMAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6067
  - THE-HERO/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6062
  - THE-CAREGIVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6056
  - THE-OUTLAW/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6040
  - THE-LOVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6073
  - THE-RULER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6061
  - THE-MAGICIAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6066
  - THE-SAGE/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6071
  - THE-JESTER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6074
  - THE-OUTLAW/p2: fragments=[how-0, how-1, how-2, how-3, why-0, result-0, result-1] · sim=0.5577 · **命中分=7**
- **pseudo命中分合计**: 57
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 14 -->
### Jesus of Montreal (1989) [THE-INNOCENT, THE-HERO, THE-LOVER]
- **tmdb_id**: 4486
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.6348
- **genres** / **language**: Drama, Comedy, Romance / fr
- **overview**: A group of actors putting on an interpretive Passion Play in Montreal begin to experience a meshing of their characters and their private lives as the production takes form against the growing opposition of the Catholic church.
- **跳转**: https://themoviecosmos.com/movie/4486
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p2: fragments=[how-1, how-2, how-3, result-1] · sim=0.5481 · **命中分=4**
  - THE-HERO/p2: fragments=[how-0, how-2, how-3, how-1, result-1, result-0] · sim=0.6348 · **命中分=6**
  - THE-LOVER/p2: fragments=[how-0, how-1, how-2, result-0] · sim=0.6257 · **命中分=4**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 11 -->
### Venus in Fur (2013) [THE-HERO, THE-CAREGIVER]
- **tmdb_id**: 197082
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.6084
- **genres** / **language**: Drama / fr
- **overview**: An enigmatic actress may have a hidden agenda when she auditions for a part in a misogynistic writer's play.
- **跳转**: https://themoviecosmos.com/movie/197082
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p2: fragments=[how-0, how-2, how-3, how-1, result-1, result-0] · sim=0.5456 · **命中分=6**
  - THE-CAREGIVER/p3: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.6084 · **命中分=5**
- **pseudo命中分合计**: 11
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 10 -->
### W's Tragedy (1984) [THE-INNOCENT, THE-CAREGIVER]
- **tmdb_id**: 326598
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.6078
- **genres** / **language**: Drama, Mystery / ja
- **overview**: A young theatre actress fights for her uncertain career while having to confront the personal sacrifices that will arise from it.
- **跳转**: https://themoviecosmos.com/movie/326598
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p3: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.6019 · **命中分=5**
  - THE-CAREGIVER/p3: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.6078 · **命中分=5**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 10 -->
### Theatre: A Love Story (2020) [THE-CAREGIVER, THE-EVERYMAN]
- **tmdb_id**: 617397
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.6270
- **genres** / **language**: Drama, Romance / ja
- **overview**: The director of a theatre company is in crisis and his actors have lost confidence in him. One day he meets a woman wearing the same shoes as him, immediately sparking chemistry between the two.
- **跳转**: https://themoviecosmos.com/movie/617397
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p2: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.5921 · **命中分=5**
  - THE-EVERYMAN/p3: fragments=[how-0, how-1, why-0, result-0, result-1] · sim=0.6270 · **命中分=5**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 9 candidate(s)

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### Tickled (2016) [THE-JESTER]
- **tmdb_id**: 373072
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5958
- **genres** / **language**: Documentary / en
- **overview**: Journalist David Farrier stumbles upon a mysterious tickling competition online. As he delves deeper he comes up against fierce resistance, but that doesn’t stop him getting to the bottom of a story stranger than fiction.
- **跳转**: https://themoviecosmos.com/movie/373072
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p3: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5958 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### The Exorcism (2024) [THE-JESTER]
- **tmdb_id**: 646683
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6115
- **genres** / **language**: Horror, Thriller / en
- **overview**: A troubled actor begins to unravel while shooting a supernatural horror film, leading his estranged daughter to wonder if he's slipping back into his past addictions or if there's something more sinister at play.
- **跳转**: https://themoviecosmos.com/movie/646683
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p3: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.6115 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Beyaz Melek (2007) [THE-LOVER]
- **tmdb_id**: 27947
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6412
- **genres** / **language**: Drama / tr
- **overview**: The film is a love story. However, it is not a story about the love between two people, but rather a story about the love and affection that a group of people feel for life and for each other. The film depicts all kinds of love, from east to west, from schoolchildren to villagers, from young to old, in both an emotional and humorous way.
- **跳转**: https://themoviecosmos.com/movie/27947
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.6412 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Sweet Dreams (1981) [THE-INNOCENT]
- **tmdb_id**: 57967
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6263
- **genres** / **language**: Comedy, Drama / it
- **overview**: Michele criticizes the film industry and its inhabitants, and is particularly embattled with a Neapolitan director making a musical about the 1968 student demonstrations. At the same time, Michele has a creative block and struggles to finish his film titled "Freud’s Mother." Nanni Moretti’s self-inquiry into filmmaking, political ennui, and men’s relations with their mothers.
- **跳转**: https://themoviecosmos.com/movie/57967
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p3: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.6263 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 现有overview很难判断，感觉有2的潜力，wobbly 2

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Hold Me While I'm Naked (1966) [THE-HERO]
- **tmdb_id**: 86811
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5998
- **genres** / **language**: Comedy, Drama / en
- **overview**: Presented as loosely autobiographical, Hold Me While I’m Naked centres on the tribulations of an independent filmmaker, frustrated at every turn as he tries to make a film that pretends to artistic merit.
- **跳转**: https://themoviecosmos.com/movie/86811
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.5998 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Viva Erotica (1996) [THE-HERO]
- **tmdb_id**: 118379
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6085
- **genres** / **language**: Comedy, Drama / cn
- **overview**: Struggling director Sing is forced to make a Category III film for a triad boss who wants his girlfriend to star, leading to conflicts over artistic integrity, nudity, and his relationship with his own girlfriend.
- **跳转**: https://themoviecosmos.com/movie/118379
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.6085 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Can You Ever Forgive Me? (2018) [THE-CAREGIVER]
- **tmdb_id**: 401847
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6193
- **genres** / **language**: Drama, Crime, Comedy / en
- **overview**: When a bestselling celebrity biographer is no longer able to get published because she has fallen out of step with current tastes, she turns her art form to deception.
- **跳转**: https://themoviecosmos.com/movie/401847
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.6193 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Lovers (2018) [THE-LOVER]
- **tmdb_id**: 492495
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6371
- **genres** / **language**: Comedy, Drama, Romance / en
- **overview**: Four different love stories are intertwined and played by the same cast
- **跳转**: https://themoviecosmos.com/movie/492495
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.6371 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Follow Her (2022) [THE-CAREGIVER]
- **tmdb_id**: 943919
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 10
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6384
- **genres** / **language**: Thriller, Horror, Mystery, Drama / en
- **overview**: An aspiring actress responds to a mysterious classified ad and finds herself trapped in her new boss's twisted revenge fantasy.
- **跳转**: https://themoviecosmos.com/movie/943919
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.6384 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
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

**Count:** 10 candidate(s)

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 46 -->
### Black Dossier (1955) [THE-SAGE, THE-CREATOR, THE-INNOCENT, THE-HERO, THE-OUTLAW, THE-RULER]
- **tmdb_id**: 199252
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 6
- **优质候选**: false
- **distinct_agents**: 6
- **相似度**: 0.6306
- **genres** / **language**: Crime, Drama / fr
- **overview**: In the 1950s, in a small provincial town, a young inexperienced judge clashes with an influential notable during an investigation into a suspicious death. His perseverance to get to the truth will cause a huge scandal.
- **跳转**: https://themoviecosmos.com/movie/199252
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-SAGE/p1: fragments=[why-0, how-1, how-2, result-0, result-2] · sim=0.4601 · **命中分=5**
  - THE-CREATOR/p2: fragments=[how-0, how-1, how-2, how-3, why-0, result-0, result-2] · sim=0.4907 · **命中分=7**
  - THE-SAGE/p2: fragments=[how-0, how-1, how-2, how-3, result-1] · sim=0.4563 · **命中分=5**
  - THE-INNOCENT/p3: fragments=[how-0, how-1, how-2, result-0, result-2] · sim=0.5197 · **命中分=5**
  - THE-HERO/p3: fragments=[why-0, how-2, how-3, result-0, result-2] · sim=0.6306 · **命中分=5**
  - THE-OUTLAW/p3: fragments=[how-0, why-0, how-1, how-2, how-3, result-1, result-2] · sim=0.5291 · **命中分=7**
  - THE-RULER/p3: fragments=[how-0, how-1, how-2, how-3, why-0, result-0, result-2] · sim=0.4954 · **命中分=7**
  - THE-SAGE/p3: fragments=[why-0, how-2, how-3, result-0, result-2] · sim=0.5103 · **命中分=5**
- **pseudo命中分合计**: 46
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 41 -->
### Gabbar Is Back (2015) [THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-INNOCENT, THE-EVERYMAN, THE-RULER]
- **tmdb_id**: 337876
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 6
- **优质候选**: false
- **distinct_agents**: 6
- **相似度**: 0.5925
- **genres** / **language**: Drama, Action / hi
- **overview**: A vigilante network taking out corrupt officials draws the notice of the authorities.
- **跳转**: https://themoviecosmos.com/movie/337876
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1: fragments=[why-0, how-1, how-2, how-3, result-0, result-2] · sim=0.5527 · **命中分=6**
  - THE-EXPLORER/p1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5403 · **命中分=5**
  - THE-OUTLAW/p1: fragments=[why-0, how-1, how-2, how-3, result-0, result-2] · sim=0.5541 · **命中分=6**
  - THE-INNOCENT/p2: fragments=[why-0, how-3, result-1, result-2] · sim=0.5391 · **命中分=4**
  - THE-EVERYMAN/p2: fragments=[why-0, how-2, how-3, result-1] · sim=0.5687 · **命中分=4**
  - THE-OUTLAW/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-2] · sim=0.5925 · **命中分=6**
  - THE-RULER/p2: fragments=[how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.4819 · **命中分=6**
  - THE-CAREGIVER/p3: fragments=[why-0, how-3, result-0, result-2] · sim=0.5277 · **命中分=4**
- **pseudo命中分合计**: 41
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 27 -->
### I Flunked, But... (1930) [THE-EXPLORER, THE-LOVER, THE-CREATOR, THE-INNOCENT, THE-EVERYMAN]
- **tmdb_id**: 88269
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 5
- **优质候选**: false
- **distinct_agents**: 5
- **相似度**: 0.5802
- **genres** / **language**: Comedy / ja
- **overview**: After the plans of a group of college students to cheat on their final exams goes awry, they're left to reassess their lives and educations and get back on track.
- **跳转**: https://themoviecosmos.com/movie/88269
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p2: fragments=[how-4, result-0, how-1, how-2, how-3, why-0, result-2] · sim=0.4427 · **命中分=7**
  - THE-LOVER/p2: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.4568 · **命中分=5**
  - THE-CREATOR/p2: fragments=[how-0, how-1, how-2, how-3, why-0, result-0, result-2] · sim=0.4642 · **命中分=7**
  - THE-INNOCENT/p3: fragments=[how-0, how-1, how-2, result-0, result-2] · sim=0.5623 · **命中分=5**
  - THE-EVERYMAN/p3: fragments=[result-0, how-4, result-2] · sim=0.5802 · **命中分=3**
- **pseudo命中分合计**: 27
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 26 -->
### L'Entente cordiale (2006) [THE-HERO, THE-CAREGIVER, THE-MAGICIAN, THE-OUTLAW, THE-JESTER]
- **tmdb_id**: 21774
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 5
- **优质候选**: false
- **distinct_agents**: 5
- **相似度**: 0.5673
- **genres** / **language**: Comedy / fr
- **overview**: The upper-class secret agent teaming up accidentally with an easily-corrupted, sly interpreter...
- **跳转**: https://themoviecosmos.com/movie/21774
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[why-0, how-1, how-2, how-3, result-0, result-2] · sim=0.5259 · **命中分=6**
  - THE-CAREGIVER/p1: fragments=[why-0, how-1, how-2, how-3, result-0, result-2] · sim=0.5127 · **命中分=6**
  - THE-MAGICIAN/p1: fragments=[why-0, how-1, how-2, result-0] · sim=0.4611 · **命中分=4**
  - THE-OUTLAW/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-2] · sim=0.5673 · **命中分=6**
  - THE-JESTER/p3: fragments=[why-0, how-2, result-0, result-2] · sim=0.5314 · **命中分=4**
- **pseudo命中分合计**: 26
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 20 -->
### Test (2006) [THE-INNOCENT, THE-CAREGIVER, THE-SAGE]
- **tmdb_id**: 887697
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5212
- **genres** / **language**: Animation, Drama / cs
- **overview**: Test
- **跳转**: https://themoviecosmos.com/movie/887697
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-2] · sim=0.4786 · **命中分=6**
  - THE-CAREGIVER/p2: fragments=[how-1, how-2, result-1, result-0, result-2] · sim=0.5212 · **命中分=5**
  - THE-SAGE/p2: fragments=[how-0, how-1, how-2, how-3, result-1] · sim=0.5033 · **命中分=5**
  - THE-CAREGIVER/p3: fragments=[why-0, how-3, result-0, result-2] · sim=0.5151 · **命中分=4**
- **pseudo命中分合计**: 20
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 18 -->
### Discount (2014) [THE-RULER, THE-CREATOR, THE-SAGE]
- **tmdb_id**: 313055
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5299
- **genres** / **language**: Comedy / fr
- **overview**: To fight against the introduction of automatic checkouts that threaten their jobs, staff members at Hard Discounts secretly create their own "Alternative Discount" outlet by salvaging products that would otherwise have been wasted.
- **跳转**: https://themoviecosmos.com/movie/313055
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p2: fragments=[how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.4720 · **命中分=6**
  - THE-CREATOR/p3: fragments=[why-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.5299 · **命中分=7**
  - THE-SAGE/p3: fragments=[why-0, how-2, how-3, result-0, result-2] · sim=0.4950 · **命中分=5**
- **pseudo命中分合计**: 18
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 18 -->
### Lie Detector (2011) [THE-CREATOR, THE-INNOCENT]
- **tmdb_id**: 375384
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5526
- **genres** / **language**: Comedy / en
- **overview**: A job interview takes an awkward turn when a lie detector reveals the unfiltered truths and hidden feelings of everyone involved.
- **跳转**: https://themoviecosmos.com/movie/375384
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p1: fragments=[why-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.5526 · **命中分=7**
  - THE-INNOCENT/p2: fragments=[why-0, how-3, result-1, result-2] · sim=0.5295 · **命中分=4**
  - THE-CREATOR/p3: fragments=[why-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.5069 · **命中分=7**
- **pseudo命中分合计**: 18
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 14 -->
### The Stanford Prison Experiment (2015) [THE-HERO, THE-MAGICIAN, THE-EVERYMAN]
- **tmdb_id**: 308032
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5364
- **genres** / **language**: Thriller, Drama, History / en
- **overview**: In 1971, Stanford's Professor Philip Zimbardo conducts a controversial psychology experiment in which college students pretend to be either prisoners or guards, but the proceedings soon get out of hand. Based on a true story.
- **跳转**: https://themoviecosmos.com/movie/308032
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p2: fragments=[how-0, how-1, how-2, how-3, result-1, result-2] · sim=0.4806 · **命中分=6**
  - THE-MAGICIAN/p2: fragments=[how-0, how-1, how-2, result-0, result-2] · sim=0.4308 · **命中分=5**
  - THE-EVERYMAN/p3: fragments=[result-0, how-4, result-2] · sim=0.5364 · **命中分=3**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 9 -->
### Kingdom (2025) [THE-HERO, THE-LOVER]
- **tmdb_id**: 1124838
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5315
- **genres** / **language**: Action, Thriller, Drama / te
- **overview**: Soori, a modest police constable, is unintentionally dragged into a dangerous undercover spy operation in Sri Lanka for the Indian government. His journey is intimately linked to his estranged brother Siva, and the risks involved on their reunion.
- **跳转**: https://themoviecosmos.com/movie/1124838
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[why-0, how-1, how-2, how-3, result-0, result-2] · sim=0.5315 · **命中分=6**
  - THE-LOVER/p3: fragments=[how-2, result-1, result-2] · sim=0.5051 · **命中分=3**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 9 -->
### Dead Mail (2024) [THE-MAGICIAN, THE-JESTER]
- **tmdb_id**: 1229915
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5549
- **genres** / **language**: Crime, Thriller, Music, Mystery, Horror / en
- **overview**: An ominous help note finds its way to a 1980s post office, connecting a dead letter investigator to a kidnapped keyboard technician.
- **跳转**: https://themoviecosmos.com/movie/1229915
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1: fragments=[why-0, how-1, how-2, result-0] · sim=0.5549 · **命中分=4**
  - THE-JESTER/p2: fragments=[how-1, why-0, how-2, result-2, how-3] · sim=0.4834 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 基本完全无关，可能是将举报信和overview中的求助纸条关联了？

### 单 agent 命中

**Count:** 6 candidate(s)

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 6 -->
### Chain Reaction (1996) [THE-MAGICIAN]
- **tmdb_id**: 12123
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4982
- **genres** / **language**: Thriller, Action, Science Fiction / en
- **overview**: At the University of Chicago, a research team that includes brilliant student machinist Eddie Kasalivich experiences a breakthrough: a stable form of fusion that may lead to a waste-free energy source. However, a private company wants to exploit the technology, so Kasalivich and physicist Dr. Lily Sinclair are framed for murder, and the fusion device is stolen. On the run from the FBI, they must recover the technology and exonerate themselves.
- **跳转**: https://themoviecosmos.com/movie/12123
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p3: fragments=[why-0, how-1, how-2, how-3, result-1, result-2] · sim=0.4982 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 6 -->
### High School (2010) [THE-EVERYMAN]
- **tmdb_id**: 27584
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5116
- **genres** / **language**: Comedy / en
- **overview**: A high school valedictorian who gets baked with the local stoner finds himself the subject of a drug test. The situation causes him to concoct an ambitious plan to get his entire graduating class to face the same fate, and fail.
- **跳转**: https://themoviecosmos.com/movie/27584
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-2] · sim=0.5116 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 6 -->
### Fairy in a Cage (1977) [THE-OUTLAW]
- **tmdb_id**: 140785
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5405
- **genres** / **language**: Drama, Horror / ja
- **overview**: During World War II a moral corrupt judge uses the military police to falsely accuse and imprison a high class business woman who captures his eye at a party. In his personal underground dungeon he subjects her to various humiliations and sexual abuse.
- **跳转**: https://themoviecosmos.com/movie/140785
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p1: fragments=[why-0, how-1, how-2, how-3, result-0, result-2] · sim=0.5405 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 6 -->
### D-Day (2013) [THE-EXPLORER]
- **tmdb_id**: 206851
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5109
- **genres** / **language**: Action, Thriller / hi
- **overview**: Four Indian agents spend nine years under cover to track down India's most wanted criminal.
- **跳转**: https://themoviecosmos.com/movie/206851
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p3: fragments=[how-0, how-1, how-2, how-3, result-0, result-2] · sim=0.5109 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 5 -->
### The Tunnel (2011) [THE-EXPLORER]
- **tmdb_id**: 46221
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5275
- **genres** / **language**: Horror, Thriller, Mystery / en
- **overview**: An investigation into a government cover-up leads to a network of abandoned train tunnels deep beneath the heart of Sydney. As a journalist and her crew hunt for the story it quickly becomes clear the story is hunting them.
- **跳转**: https://themoviecosmos.com/movie/46221
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5275 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 5 -->
### Jana Gana Mana (2022) [THE-HERO]
- **tmdb_id**: 792358
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 12
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5463
- **genres** / **language**: Crime, Thriller, Drama / ml
- **overview**: After the mysterious death of a college professor triggers nationwide protests, a police officer’s pursuit of justice unravels layers of political manipulation and moral conflict, exposing how truth and power collide in the pursuit of justice.
- **跳转**: https://themoviecosmos.com/movie/792358
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p3: fragments=[why-0, how-2, how-3, result-0, result-2] · sim=0.5463 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

## 01-grid-outage-rerun

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

**Count:** 8 candidate(s)

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 210 -->
### Survival Family (2017) [THE-INNOCENT, THE-EVERYMAN, THE-HERO, THE-CAREGIVER, THE-EXPLORER, THE-OUTLAW, THE-CREATOR, THE-RULER, THE-MAGICIAN, THE-SAGE, THE-JESTER] [优质·多agent]
- **tmdb_id**: 429918
- **quality_candidate**: true
- **neutral_hits**: 11
- **neutral_total**: 11
- **neutral_hit_rate**: 1.0000
- **distinct_agents**: 11
- **优质候选**: true
- **distinct_agents**: 11
- **相似度**: 0.6431
- **genres** / **language**: Comedy, Drama, Adventure / ja
- **overview**: A world wide electrical outage occurs. Everything that requires electricity comes to a stop. Tokyo is nearly ruined. Yoshiyuki Suzuki decides to escape from Tokyo with his family.
- **跳转**: https://themoviecosmos.com/movie/429918
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5023
  - THE-EVERYMAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5048
  - THE-HERO/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5048
  - THE-CAREGIVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5048
  - THE-EXPLORER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4968
  - THE-OUTLAW/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5015
  - THE-CREATOR/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5012
  - THE-RULER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5048
  - THE-MAGICIAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5048
  - THE-SAGE/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4974
  - THE-JESTER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4991
  - THE-INNOCENT/p1: fragments=[why-0, why-1, how-0, how-1, result-0, result-1] · sim=0.5437 · **命中分=6**
  - THE-EVERYMAN/p1: fragments=[why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5217 · **命中分=7**
  - THE-CAREGIVER/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5098 · **命中分=6**
  - THE-CREATOR/p1: fragments=[why-0, how-0, how-1, how-2, why-2, result-0, result-1] · sim=0.5255 · **命中分=7**
  - THE-RULER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5761 · **命中分=7**
  - THE-SAGE/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5139 · **命中分=7**
  - THE-JESTER/p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.4589 · **命中分=4**
  - THE-EVERYMAN/p2: fragments=[why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.6431 · **命中分=8**
  - THE-HERO/p2: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0] · sim=0.6045 · **命中分=7**
  - THE-EXPLORER/p2: fragments=[why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5675 · **命中分=8**
  - THE-OUTLAW/p2: fragments=[why-2, why-1, how-0, how-1, how-2, result-0, result-1] · sim=0.5079 · **命中分=7**
  - THE-RULER/p2: fragments=[why-1, why-2, how-1, how-2, how-3, result-0] · sim=0.5976 · **命中分=6**
  - THE-MAGICIAN/p2: fragments=[why-0, how-0, how-1, why-2, how-2, how-3, result-0, result-1] · sim=0.4718 · **命中分=8**
  - THE-SAGE/p2: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5111 · **命中分=9**
  - THE-JESTER/p2: fragments=[why-0, why-1, why-2, how-3, result-1] · sim=0.5773 · **命中分=5**
  - THE-INNOCENT/p3: fragments=[why-2, how-1, how-2, how-3, result-1] · sim=0.5157 · **命中分=5**
  - THE-EVERYMAN/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.6090 · **命中分=7**
  - THE-CAREGIVER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0] · sim=0.5824 · **命中分=6**
  - THE-EXPLORER/p3: fragments=[why-0, why-2, how-1, how-2, how-3, result-0, result-1] · sim=0.5546 · **命中分=7**
  - THE-OUTLAW/p3: fragments=[why-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5686 · **命中分=6**
  - THE-CREATOR/p3: fragments=[how-0, how-1, how-2, how-3, why-1, why-2, result-0, result-1] · sim=0.5338 · **命中分=8**
  - THE-MAGICIAN/p3: fragments=[why-0, why-1, why-2, how-3, result-0, result-1] · sim=0.4810 · **命中分=6**
  - THE-SAGE/p3: fragments=[why-0, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4470 · **命中分=8**
- **pseudo命中分合计**: 210
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 效果相当好
- **历史打分**: （phase3.5 / 2 / 双重） （phase3.6 / 2 / 双重 / 效果相当好） （phase3.7 / 2 / 双重）

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 44 -->
### Geostorm (2017) [THE-HERO, THE-INNOCENT, THE-OUTLAW, THE-RULER, THE-MAGICIAN, THE-SAGE]
- **tmdb_id**: 274855
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 6
- **优质候选**: false
- **distinct_agents**: 6
- **相似度**: 0.5623
- **genres** / **language**: Action, Science Fiction, Thriller / en
- **overview**: After an unprecedented series of natural disasters threatened the planet, the world's leaders came together to create an intricate network of satellites to control the global climate and keep everyone safe. But now, something has gone wrong: the system built to protect Earth is attacking it, and it becomes a race against the clock to uncover the real threat before a worldwide geostorm wipes out everything and everyone along with it.
- **跳转**: https://themoviecosmos.com/movie/274855
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[why-0, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5623 · **命中分=8**
  - THE-INNOCENT/p2: fragments=[why-1, how-0, how-1, how-2, how-3, result-1] · sim=0.5245 · **命中分=6**
  - THE-INNOCENT/p3: fragments=[why-2, how-1, how-2, how-3, result-1] · sim=0.5061 · **命中分=5**
  - THE-OUTLAW/p3: fragments=[why-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4922 · **命中分=6**
  - THE-RULER/p3: fragments=[why-1, how-2, how-3, result-0, result-1] · sim=0.4663 · **命中分=5**
  - THE-MAGICIAN/p3: fragments=[why-0, why-1, why-2, how-3, result-0, result-1] · sim=0.4830 · **命中分=6**
  - THE-SAGE/p3: fragments=[why-0, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4510 · **命中分=8**
- **pseudo命中分合计**: 44
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 结构  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 灾难感有点联系

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 39 -->
### Blade Runner: Black Out 2022 (2017) [THE-INNOCENT, THE-RULER, THE-HERO, THE-CREATOR, THE-JESTER]
- **tmdb_id**: 475946
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 5
- **优质候选**: false
- **distinct_agents**: 5
- **相似度**: 0.5580
- **genres** / **language**: Action, Animation, Science Fiction / en
- **overview**: This animated short revolves around the events causing an electrical systems failure on the west coast of the US. According to Blade Runner 2049’s official timeline, this failure leads to cities shutting down, financial and trade markets being thrown into chaos, and food supplies dwindling. There’s no proof as to what caused the blackouts, but Replicants — the bio-engineered robots featured in the original Blade Runner, are blamed.
- **跳转**: https://themoviecosmos.com/movie/475946
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1: fragments=[why-0, why-1, how-0, how-1, result-0, result-1] · sim=0.4563 · **命中分=6**
  - THE-RULER/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5107 · **命中分=7**
  - THE-HERO/p2: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0] · sim=0.5017 · **命中分=7**
  - THE-CREATOR/p2: fragments=[why-0, why-1, why-2, how-3, result-0, result-1] · sim=0.5580 · **命中分=6**
  - THE-CREATOR/p3: fragments=[how-0, how-1, how-2, how-3, why-1, why-2, result-0, result-1] · sim=0.5408 · **命中分=8**
  - THE-JESTER/p3: fragments=[why-0, why-1, how-0, how-1, result-0] · sim=0.4983 · **命中分=5**
- **pseudo命中分合计**: 39
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 赛博朋克主题有启示感；且表层上讲的也是大停电，与新闻有关。

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 33 -->
### From What Is Before (2014) [THE-MAGICIAN, THE-JESTER, THE-CAREGIVER, THE-HERO]
- **tmdb_id**: 280492
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 4
- **优质候选**: false
- **distinct_agents**: 4
- **相似度**: 0.5264
- **genres** / **language**: Drama / tl
- **overview**: The Philippines, 1972. Mysterious things are happening in a remote barrio. Wails are heard from the forest, cows are hacked to death, a man is found bleeding to death at the crossroad, and houses are burned. Ferdinand E. Marcos announces Proclamation No. 1081, putting the entire country under Martial Law.
- **跳转**: https://themoviecosmos.com/movie/280492
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, how-3, result-1] · sim=0.4755 · **命中分=8**
  - THE-JESTER/p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.4439 · **命中分=4**
  - THE-CAREGIVER/p2: fragments=[why-1, why-2, how-2, how-3, result-1] · sim=0.5221 · **命中分=5**
  - THE-MAGICIAN/p2: fragments=[why-0, how-0, how-1, why-2, how-2, how-3, result-0, result-1] · sim=0.4854 · **命中分=8**
  - THE-HERO/p3: fragments=[why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5264 · **命中分=8**
- **pseudo命中分合计**: 33
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 只有菲律宾这个概念相关，low 1

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 22 -->
### Stranded (2021) [THE-EVERYMAN, THE-OUTLAW, THE-EXPLORER]
- **tmdb_id**: 841793
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 3
- **优质候选**: false
- **distinct_agents**: 3
- **相似度**: 0.5334
- **genres** / **language**: Drama / pt
- **overview**: Tensions run high while food runs low as six influencers find themselves stranded on a secluded island after plans for a weekend escape go awry.
- **跳转**: https://themoviecosmos.com/movie/841793
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p2: fragments=[why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5334 · **命中分=8**
  - THE-OUTLAW/p2: fragments=[why-2, why-1, how-0, how-1, how-2, result-0, result-1] · sim=0.4914 · **命中分=7**
  - THE-EXPLORER/p3: fragments=[why-0, why-2, how-1, how-2, how-3, result-0, result-1] · sim=0.5177 · **命中分=7**
- **pseudo命中分合计**: 22
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **历史打分**: （phase3.6 / 1 / 表层） （phase3.7 / 1 / 结构 / 和现实原型扯得有点远）

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 13 -->
### Re-Generator (2010) [THE-CAREGIVER, THE-SAGE]
- **tmdb_id**: 194834
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.4857
- **genres** / **language**: Action, Science Fiction / en
- **overview**: A plane containing a highly classified government project crashes outside of a small town in the US. Realizing the level of danger, the government tries to secretly fix the problem. As tensions grow, the situation gets out of control, and civilians from the town find themselves facing their worst nightmare: a genetically enhanced killing machine that doesn't know how to stop.
- **跳转**: https://themoviecosmos.com/movie/194834
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4857 · **命中分=6**
  - THE-SAGE/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4404 · **命中分=7**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 13 -->
### The Current War (2018) [THE-EXPLORER, THE-CREATOR]
- **tmdb_id**: 418879
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5834
- **genres** / **language**: Drama, History / en
- **overview**: Electricity titans Thomas Edison and George Westinghouse compete to create a sustainable system and market it to the American people.
- **跳转**: https://themoviecosmos.com/movie/418879
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5157 · **命中分=6**
  - THE-CREATOR/p1: fragments=[why-0, how-0, how-1, how-2, why-2, result-0, result-1] · sim=0.5834 · **命中分=7**
- **pseudo命中分合计**: 13
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 电力系统相关，solid 1

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 12 -->
### Space/Time (2025) [THE-EXPLORER, THE-CREATOR]
- **tmdb_id**: 434853
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 2
- **优质候选**: false
- **distinct_agents**: 2
- **相似度**: 0.5321
- **genres** / **language**: Science Fiction, Action, Thriller / en
- **overview**: After a fatal test shuts down their project, a disgraced team of scientists enters the criminal underworld to rebuild a forbidden space-bending engine that could rescue humanity or annihilate it entirely.
- **跳转**: https://themoviecosmos.com/movie/434853
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5122 · **命中分=6**
  - THE-CREATOR/p2: fragments=[why-0, why-1, why-2, how-3, result-0, result-1] · sim=0.5321 · **命中分=6**
- **pseudo命中分合计**: 12
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

### 单 agent 命中

**Count:** 11 candidate(s)

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 8 -->
### 2061 - Un anno eccezionale (2007) [THE-EXPLORER]
- **tmdb_id**: 33495
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5648
- **genres** / **language**: Comedy, Science Fiction / it
- **overview**: In a post-apocalyptic future, the Italian peninsula is going through a dark moment due to a terrible energy crisis.
- **跳转**: https://themoviecosmos.com/movie/33495
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p2: fragments=[why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5648 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 8 -->
### Bataan (1943) [THE-HERO]
- **tmdb_id**: 43506
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5214
- **genres** / **language**: Action, Drama, War / en
- **overview**: During Japan's invasion of the Philippines in 1942, Capt. Henry Lassiter, Sgt. Bill Dane and a diverse group of American soldiers are ordered to destroy and hold a strategic bridge in order to delay the Japanese forces and allow Gen. MacArthur time to secure Bataan. When the Japanese soldiers begin to rebuild the bridge and advance, the group struggles with not only hunger, sickness and gunfire, but also the knowledge that there is likely no relief on the way.
- **跳转**: https://themoviecosmos.com/movie/43506
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p3: fragments=[why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5214 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 8 -->
### Black Noise (2023) [THE-HERO]
- **tmdb_id**: 1159518
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5958
- **genres** / **language**: Action, Science Fiction, Horror, Thriller / en
- **overview**: Members of an elite security team deployed to rescue a VIP on an exclusive island.The rescue mission becomes a desperate attempt to survive, escape the island and elude the sinister presence that seeks to harm them.
- **跳转**: https://themoviecosmos.com/movie/1159518
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1: fragments=[why-0, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5958 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 7 -->
### Pandora (2016) [THE-EVERYMAN]
- **tmdb_id**: 429450
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5221
- **genres** / **language**: Thriller, Drama, Action / ko
- **overview**: When an earthquake hits a Korean village housing a run-down nuclear power plant, a man risks his life to save the country from imminent disaster.
- **跳转**: https://themoviecosmos.com/movie/429450
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5221 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 7 -->
### Breathe (2024) [THE-EVERYMAN]
- **tmdb_id**: 720321
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4853
- **genres** / **language**: Action, Science Fiction, Mystery, Thriller / en
- **overview**: Air-supply is scarce in the near future, forcing a mother and daughter to fight for survival when two strangers arrive desperate for an oxygenated haven.
- **跳转**: https://themoviecosmos.com/movie/720321
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1: fragments=[why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4853 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）
- **历史打分**: （phase3.6 / 1 / 表层 / 资源短缺的感觉挺优秀的，其实介于1和2之间） （phase3.7 / 2 / 结构 / 现实中的电力短缺与电影overview中的空气供应有微妙的共振，low 2）

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 6 -->
### Sarkar Raj (2008) [THE-CAREGIVER]
- **tmdb_id**: 14394
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5017
- **genres** / **language**: Action, Adventure, Crime, Drama / hi
- **overview**: When Anita Raja, CEO of Sheppard power plant, brings a power plant proposal to set up in rural Mahrashtra before the Nagres, insightful Shankar is quick to realise the benefits the power plant can bring to the people.
- **跳转**: https://themoviecosmos.com/movie/14394
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0] · sim=0.5017 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 6 -->
### Alien: Harvest (2019) [THE-INNOCENT]
- **tmdb_id**: 588209
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4962
- **genres** / **language**: Science Fiction, Horror / en
- **overview**: The surviving crew of a damaged space harvester has a motion sensor as their only navigation tool leading them to safety, while a creature in the shadows terrorizes them. However, the greatest threat might have been hiding in plain sight.
- **跳转**: https://themoviecosmos.com/movie/588209
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p2: fragments=[why-1, how-0, how-1, how-2, how-3, result-1] · sim=0.4962 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 5 -->
### The Towering Inferno (1974) [THE-JESTER]
- **tmdb_id**: 5919
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5071
- **genres** / **language**: Action, Drama, Thriller / en
- **overview**: At the opening party of a colossal—but poorly constructed—skyscraper, a massive fire breaks out, threatening to destroy the tower and everyone in it.
- **跳转**: https://themoviecosmos.com/movie/5919
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p2: fragments=[why-0, why-1, why-2, how-3, result-1] · sim=0.5071 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 5 -->
### Fires on the Plain (2015) [THE-CAREGIVER]
- **tmdb_id**: 283710
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5217
- **genres** / **language**: War, Drama / ja
- **overview**: In the final days of World War II, occupying Japanese forces in the Philippines face resistance from the local population and the American offensive. The dwindling Japanese soldiers attempt to survive through the horrors of war.
- **跳转**: https://themoviecosmos.com/movie/283710
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p2: fragments=[why-1, why-2, how-2, how-3, result-1] · sim=0.5217 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 5 -->
### Kaappaan (2019) [THE-RULER]
- **tmdb_id**: 533885
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4892
- **genres** / **language**: Action, Thriller / ta
- **overview**: A Special Protection Group officer has to identify the threat to the prime minister, who he is protecting, and also the nation.
- **跳转**: https://themoviecosmos.com/movie/533885
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p3: fragments=[why-1, how-2, how-3, result-0, result-1] · sim=0.4892 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

<!-- run_id: 01-grid-outage-rerun -->
<!-- pseudo命中分合计: 5 -->
### Asteroid City (2023) [THE-JESTER]
- **tmdb_id**: 747188
- **quality_candidate**: false
- **neutral_hits**: 0
- **neutral_total**: 11
- **neutral_hit_rate**: 0.0000
- **distinct_agents**: 1
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5068
- **genres** / **language**: Comedy, Drama / en
- **overview**: In an American desert town circa 1955, the itinerary of a Junior Stargazer/Space Cadet convention is spectacularly disrupted by world-changing events.
- **跳转**: https://themoviecosmos.com/movie/747188
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p3: fragments=[why-0, why-1, how-0, how-1, result-0] · sim=0.5068 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: （可选）

