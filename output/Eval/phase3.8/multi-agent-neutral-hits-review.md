# Multi-Agent + Neutral Hits — Filtered Review

## Filter summary

- **Source:** `output/Eval/phase3.8/high-hit-score-review.md`
- **Filter criteria (ALL must match):**
  1. **多 agent 命中** — `distinct_agents` ≥ 2, or ≥2 agents in heading / hit lines, or `quality_candidate` with multi-agent convergence
  2. **neutral_hits > 0** — `neutral_hits` > 0, or `neutral_hit_rate` > 0 when hits field absent
- **Generated:** 2026-06-06 07:15 UTC
- **Total matching candidates:** 17
- **Runs with matches:** 9

### Count by run_id

| run_id | count |
| --- | ---: |
| 01-grid-outage | 1 |
| 01-grid-outage-rerun | 1 |
| 02-corporate-layoff | 4 |
| 03-election-upset | 2 |
| 05-climate-disaster | 2 |
| 06-tech-monopoly | 2 |
| 07-migration-border | 1 |
| 08-sports-underdog | 2 |
| 09-cultural-backlash | 2 |

---

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

### 多 agents 命中 · neutral channel

**Count:** 1 candidate(s)

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

### 多 agents 命中 · neutral channel

**Count:** 4 candidate(s)

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

### 多 agents 命中 · neutral channel

**Count:** 2 candidate(s)

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

### 多 agents 命中 · neutral channel

**Count:** 2 candidate(s)

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

### 多 agents 命中 · neutral channel

**Count:** 2 candidate(s)

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

### 多 agents 命中 · neutral channel

**Count:** 1 candidate(s)

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
- **共振分**: 1（phase3.6: 1；phase3.7: 1）  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层（phase3.6） / 结构（phase3.7）  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: phase3.6: （无）；phase3.7: 和现实原型扯得有点远

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

### 多 agents 命中 · neutral channel

**Count:** 2 candidate(s)

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

### 多 agents 命中 · neutral channel

**Count:** 2 candidate(s)

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

### 多 agents 命中 · neutral channel

**Count:** 1 candidate(s)

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
