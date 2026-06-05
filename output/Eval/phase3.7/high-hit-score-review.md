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

- **Generation date:** 2026-06-05
- **Total candidates (≥5):** 150
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
<!-- pseudo命中分合计: 77 -->
### Survival Family (2017) [A1, THE-EVERYMAN, THE-OUTLAW, THE-CREATOR, THE-MAGICIAN, THE-LOVER, THE-JESTER] [优质·多agent]
- **tmdb_id**: 429918
- **优质候选**: true
- **distinct_agents**: 7
- **相似度**: 0.6043
- **genres** / **language**: Comedy, Drama, Adventure / ja
- **overview**: A world wide electrical outage occurs. Everything that requires electricity comes to a stop. Tokyo is nearly ruined. Yoshiyuki Suzuki decides to escape from Tokyo with his family.
- **跳转**: https://themoviecosmos.com/movie/429918
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.4985 · **命中分=7**
  - A1/p2: fragments=[why-0, why-1, why-2, result-0, result-1] · sim=0.5253 · **命中分=5**
  - THE-EVERYMAN/p1 · fit=0.88: fragments=[how-0, how-1, how-2, how-3, why-1, result-0, result-1] · sim=0.5233 · **命中分=7**
  - THE-OUTLAW/p1 · fit=0.88: fragments=[why-0, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5368 · **命中分=8**
  - THE-CREATOR/p1 · fit=0.65: fragments=[how-0, how-1, how-2, how-3, result-1] · sim=0.5331 · **命中分=5**
  - THE-MAGICIAN/p1 · fit=0.85: fragments=[why-0, how-1, how-2, how-3, result-0] · sim=0.5707 · **命中分=5**
  - THE-EVERYMAN/p2 · fit=0.75: fragments=[why-2, why-0, how-1, how-2, result-1, result-2] · sim=0.6043 · **命中分=6**
  - THE-OUTLAW/p2 · fit=0.85: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, how-3, result-1, result-2] · sim=0.5038 · **命中分=9**
  - THE-LOVER/p2 · fit=0.42: fragments=[result-0, how-0, how-2, how-3, result-1, how-1] · sim=0.4998 · **命中分=6**
  - THE-CREATOR/p2 · fit=0.70: fragments=[why-2, how-2, why-0, result-2, result-1] · sim=0.5778 · **命中分=5**
  - THE-JESTER/p2 · fit=0.85: fragments=[why-0, how-1, how-2, how-3, why-1, result-1, result-0] · sim=0.5678 · **命中分=7**
  - THE-MAGICIAN/p3 · fit=0.92: fragments=[why-0, why-1, why-2, how-1, how-2, how-3, result-2] · sim=0.5791 · **命中分=7**
- **pseudo命中分合计**: 77
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 21 -->
### 2061 - Un anno eccezionale (2007) [THE-EXPLORER, THE-CAREGIVER, THE-CREATOR] [优质·多agent]
- **tmdb_id**: 33495
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.5773
- **genres** / **language**: Comedy, Science Fiction / it
- **overview**: In a post-apocalyptic future, the Italian peninsula is going through a dark moment due to a terrible energy crisis.
- **跳转**: https://themoviecosmos.com/movie/33495
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p1 · fit=0.85: fragments=[why-0, why-1, how-1, how-2, how-3] · sim=0.5210 · **命中分=5**
  - THE-CAREGIVER/p2 · fit=0.85: fragments=[result-0, how-3, why-0, why-1, why-2, result-1, result-2] · sim=0.5773 · **命中分=7**
  - THE-EXPLORER/p2 · fit=0.78: fragments=[how-0, how-1, result-0, result-1] · sim=0.5305 · **命中分=4**
  - THE-CREATOR/p2 · fit=0.70: fragments=[why-2, how-2, why-0, result-2, result-1] · sim=0.4783 · **命中分=5**
- **pseudo命中分合计**: 21
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 17 -->
### Stranded (2021) [A1, THE-EXPLORER, THE-CAREGIVER] [优质·多agent]
- **tmdb_id**: 841793
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.5874
- **genres** / **language**: Drama / pt
- **overview**: Tensions run high while food runs low as six influencers find themselves stranded on a secluded island after plans for a weekend escape go awry.
- **跳转**: https://themoviecosmos.com/movie/841793
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p2: fragments=[why-0, why-1, why-2, result-0, result-1] · sim=0.4782 · **命中分=5**
  - THE-EXPLORER/p1 · fit=0.85: fragments=[why-0, why-1, how-1, how-2, how-3] · sim=0.5076 · **命中分=5**
  - THE-CAREGIVER/p2 · fit=0.85: fragments=[result-0, how-3, why-0, why-1, why-2, result-1, result-2] · sim=0.5874 · **命中分=7**
- **pseudo命中分合计**: 17
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 结构  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 和现实原型扯得有点远

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 14 -->
### Breathe (2024) [A1, THE-EVERYMAN] [优质·多agent]
- **tmdb_id**: 720321
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.4561
- **genres** / **language**: Action, Science Fiction, Mystery, Thriller / en
- **overview**: Air-supply is scarce in the near future, forcing a mother and daughter to fight for survival when two strangers arrive desperate for an oxygenated haven.
- **跳转**: https://themoviecosmos.com/movie/720321
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.4561 · **命中分=7**
  - THE-EVERYMAN/p1 · fit=0.88: fragments=[how-0, how-1, how-2, how-3, why-1, result-0, result-1] · sim=0.4479 · **命中分=7**
- **pseudo命中分合计**: 14
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 结构  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 现实中的电力短缺与电影overview中的空气供应有微妙的共振，low 2

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 13 -->
### The Tunnel (2011) [THE-LOVER, THE-MAGICIAN] [优质·多agent]
- **tmdb_id**: 46221
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5327
- **genres** / **language**: Horror, Thriller, Mystery / en
- **overview**: An investigation into a government cover-up leads to a network of abandoned train tunnels deep beneath the heart of Sydney. As a journalist and her crew hunt for the story it quickly becomes clear the story is hunting them.
- **跳转**: https://themoviecosmos.com/movie/46221
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p2 · fit=0.42: fragments=[result-0, how-0, how-2, how-3, result-1, how-1] · sim=0.5327 · **命中分=6**
  - THE-MAGICIAN/p3 · fit=0.92: fragments=[why-0, why-1, why-2, how-1, how-2, how-3, result-2] · sim=0.4952 · **命中分=7**
- **pseudo命中分合计**: 13
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 13 -->
### Geostorm (2017) [THE-JESTER, THE-MAGICIAN] [优质·多agent]
- **tmdb_id**: 274855
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5594
- **genres** / **language**: Action, Science Fiction, Thriller / en
- **overview**: After an unprecedented series of natural disasters threatened the planet, the world's leaders came together to create an intricate network of satellites to control the global climate and keep everyone safe. But now, something has gone wrong: the system built to protect Earth is attacking it, and it becomes a race against the clock to uncover the real threat before a worldwide geostorm wipes out everything and everyone along with it.
- **跳转**: https://themoviecosmos.com/movie/274855
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1 · fit=0.78: fragments=[why-0, how-1, how-0, how-2, how-3, result-0, result-2] · sim=0.5594 · **命中分=7**
  - THE-MAGICIAN/p2 · fit=0.78: fragments=[why-0, why-1, how-0, how-1, how-2, how-3] · sim=0.5079 · **命中分=6**
- **pseudo命中分合计**: 13
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 结构  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 灾难感有点联系

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 11 -->
### Hurricane (1979) [THE-CAREGIVER, THE-LOVER] [优质·多agent]
- **tmdb_id**: 75162
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5433
- **genres** / **language**: Drama, Action, Romance / en
- **overview**: The story of the desperate love affair between a young Samoan chief and a beautiful American painter, against the will of her father, the powerful governor of the island. Amid this man-made tension comes a powerful hurricane so devastating, the lives of the lovers and the entire island are imperiled.
- **跳转**: https://themoviecosmos.com/movie/75162
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1 · fit=0.78: fragments=[why-0, how-1, how-2, how-0, result-1, how-3] · sim=0.4816 · **命中分=6**
  - THE-LOVER/p1 · fit=0.35: fragments=[why-0, how-1, why-1, result-0, why-2] · sim=0.5433 · **命中分=5**
- **pseudo命中分合计**: 11
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 结构  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 抓到了季节性气候导致灾难这个点

### 单 agent 命中

**Count:** 11 candidate(s)

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 15 -->
### From What Is Before (2014) [THE-OUTLAW]
- **tmdb_id**: 280492
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4802
- **genres** / **language**: Drama / tl
- **overview**: The Philippines, 1972. Mysterious things are happening in a remote barrio. Wails are heard from the forest, cows are hacked to death, a man is found bleeding to death at the crossroad, and houses are burned. Ferdinand E. Marcos announces Proclamation No. 1081, putting the entire country under Martial Law.
- **跳转**: https://themoviecosmos.com/movie/280492
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p1 · fit=0.88: fragments=[why-0, why-2, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4265 · **命中分=8**
  - THE-OUTLAW/p3 · fit=0.82: fragments=[why-0, why-1, why-2, how-0, how-1, result-0, result-2] · sim=0.4802 · **命中分=7**
- **pseudo命中分合计**: 15
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 只有菲律宾这个概念相关，low 1

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 9 -->
### The Edge of Democracy (2019) [THE-OUTLAW]
- **tmdb_id**: 566221
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5051
- **genres** / **language**: Documentary / pt
- **overview**: A cautionary tale for these times of democracy in crisis—the personal and political fuse to explore one of the most dramatic periods in Brazilian history. With unprecedented access to Presidents Dilma Rousseff and Lula da Silva, we witness their rise and fall and the tragically polarized nation that remains.
- **跳转**: https://themoviecosmos.com/movie/566221
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p2 · fit=0.85: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, how-3, result-1, result-2] · sim=0.5051 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 7 -->
### King of the Zombies (1941) [THE-JESTER]
- **tmdb_id**: 23104
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5572
- **genres** / **language**: Horror, Comedy / en
- **overview**: During World War II, a small plane somewhere over the Caribbean runs low on fuel and is blown off course by a storm. Guided by a faint radio signal, they crash-land on an island. The passenger, his manservant and the pilot take refuge in a mansion owned by a doctor. The quick-witted yet easily-frightened manservant soon becomes convinced the mansion is haunted by zombies and ghosts.
- **跳转**: https://themoviecosmos.com/movie/23104
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1 · fit=0.78: fragments=[why-0, how-1, how-0, how-2, how-3, result-0, result-2] · sim=0.5572 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 7 -->
### The Real Glory (1939) [THE-OUTLAW]
- **tmdb_id**: 111750
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4830
- **genres** / **language**: Drama, War / en
- **overview**: Fort Mysang, southern Philippine Islands, under US rule, 1906. A small group of army officers and native troops resist the fierce and treacherous attacks of the ruthless Alisang and his fanatical followers.
- **跳转**: https://themoviecosmos.com/movie/111750
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p3 · fit=0.82: fragments=[why-0, why-1, why-2, how-0, how-1, result-0, result-2] · sim=0.4830 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 菲律宾作为关键词有浅层联系 low 1

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 7 -->
### Contagion of Fear (2023) [THE-JESTER]
- **tmdb_id**: 1223272
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4730
- **genres** / **language**: Science Fiction, Thriller / en
- **overview**: A catastrophic train derailment sends the city spiraling into chaos. But the derailment is just the beginning. A biological gas attack sees crash survivors collapsing and dying within minutes. And the sickness is rapidly spreading.
- **跳转**: https://themoviecosmos.com/movie/1223272
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p2 · fit=0.85: fragments=[why-0, how-1, how-2, how-3, why-1, result-1, result-0] · sim=0.4730 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 6 -->
### Matango (1963) [THE-CAREGIVER]
- **tmdb_id**: 52302
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5079
- **genres** / **language**: Horror, Science Fiction, Thriller, Drama, Mystery, Fantasy / ja
- **overview**: Five vacationers and two crewmen become stranded on a tropical island near the equator. The island has little edible food for them to use as they try to live in a fungus covered hulk while repairing Kessei's yacht. Eventually they struggle over the food rations which were left behind by the former crew. Soon they discover something unfriendly there...
- **跳转**: https://themoviecosmos.com/movie/52302
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1 · fit=0.78: fragments=[why-0, how-1, how-2, how-0, result-1, how-3] · sim=0.5079 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 海岛和末日有点联系的感觉，low 1

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 6 -->
### Peasants (1935) [THE-MAGICIAN]
- **tmdb_id**: 266727
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5173
- **genres** / **language**: Drama / ru
- **overview**: The peaceful life of an exemplary collective farm is being rent asunder by shortages and dissent, and a commissar is sent to uncover the source of the problems, unaware that their is actual sabotage involved.
- **跳转**: https://themoviecosmos.com/movie/266727
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p2 · fit=0.78: fragments=[why-0, why-1, how-0, how-1, how-2, how-3] · sim=0.5173 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 6 -->
### Blade Runner: Black Out 2022 (2017) [THE-EVERYMAN]
- **tmdb_id**: 475946
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5480
- **genres** / **language**: Action, Animation, Science Fiction / en
- **overview**: This animated short revolves around the events causing an electrical systems failure on the west coast of the US. According to Blade Runner 2049’s official timeline, this failure leads to cities shutting down, financial and trade markets being thrown into chaos, and food supplies dwindling. There’s no proof as to what caused the blackouts, but Replicants — the bio-engineered robots featured in the original Blade Runner, are blamed.
- **跳转**: https://themoviecosmos.com/movie/475946
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p2 · fit=0.75: fragments=[why-2, why-0, how-1, how-2, result-1, result-2] · sim=0.5480 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 赛博朋克主题有启示感；且表层上讲的也是大停电，与新闻有关。

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Squirm (1976) [THE-MAGICIAN]
- **tmdb_id**: 25241
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4415
- **genres** / **language**: Horror / en
- **overview**: A violent electrical storm topples power lines into the rain soaked earth that is home for an aggressive breed of worms. The high voltage causes the worms to mutate into larger, hostile hordes of man-eating worms that lie in wait for the residents of Fly Creek.
- **跳转**: https://themoviecosmos.com/movie/25241
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1 · fit=0.85: fragments=[why-0, how-1, how-2, how-3, result-0] · sim=0.4415 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 只有一点点相关，low 1

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### The Current War (2018) [THE-CREATOR]
- **tmdb_id**: 418879
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4618
- **genres** / **language**: Drama, History / en
- **overview**: Electricity titans Thomas Edison and George Westinghouse compete to create a sustainable system and market it to the American people.
- **跳转**: https://themoviecosmos.com/movie/418879
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p1 · fit=0.65: fragments=[how-0, how-1, how-2, how-3, result-1] · sim=0.4618 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 电力系统相关，solid 1

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Free Rein: Valentine's Day (2019) [THE-LOVER]
- **tmdb_id**: 579450
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5241
- **genres** / **language**: Romance, Family / en
- **overview**: Love is in the air as Zoe and friends go on a quest to find a fabled Maid's Stone. But when rivalry blinds them to danger, it's Raven to the rescue!
- **跳转**: https://themoviecosmos.com/movie/579450
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1 · fit=0.35: fragments=[why-0, how-1, why-1, result-0, why-2] · sim=0.5241 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

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

**Count:** 7 candidate(s)

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 33 -->
### Bounty Killer (2013) [A1, THE-EVERYMAN, THE-LOVER, THE-JESTER, THE-CREATOR] [优质·多agent]
- **tmdb_id**: 209504
- **优质候选**: true
- **distinct_agents**: 5
- **相似度**: 0.6389
- **genres** / **language**: Action, Science Fiction / en
- **overview**: It’s been 20 years since the corporations took over the world’s governments. Their thirst for power and profits led to the Corporate Wars, a fierce global battle that laid waste to society as we know it. Born from the ash, the Council of Nine rose as a new law and order for this dark age. To avenge the corporations’ reckless destruction, the Council issues death warrants for all white collar criminals. Their hunters—the bounty killer. From amateur savage to graceful assassin, the bounty killers now compete for body count, fame and a fat stack of cash. They’re ending the plague of corporate greed and providing the survivors of the apocalypse with retribution. These are the new heroes. This is the age of the BOUNTY KILLER.
- **跳转**: https://themoviecosmos.com/movie/209504
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[why-0, how-0, how-1, how-2] · sim=0.4825 · **命中分=4**
  - THE-EVERYMAN/p1 · fit=0.85: fragments=[why-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4895 · **命中分=6**
  - THE-LOVER/p1 · fit=0.60: fragments=[why-0, how-0, how-1, result-0] · sim=0.6389 · **命中分=4**
  - THE-JESTER/p1 · fit=0.85: fragments=[how-0, why-0, how-1, result-1, result-0, result-2] · sim=0.5911 · **命中分=6**
  - THE-CREATOR/p2 · fit=0.85: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.5178 · **命中分=8**
  - THE-LOVER/p3 · fit=0.55: fragments=[how-1, how-2, how-3, result-1, result-3] · sim=0.5517 · **命中分=5**
- **pseudo命中分合计**: 33
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 28 -->
### The Seventh Company Outdoors (1977) [A1, THE-INNOCENT, THE-LOVER, THE-JESTER] [优质·多agent]
- **tmdb_id**: 56589
- **优质候选**: true
- **distinct_agents**: 4
- **相似度**: 0.5607
- **genres** / **language**: Comedy / fr
- **overview**: The third part of Seventh Company adventures.
- **跳转**: https://themoviecosmos.com/movie/56589
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p2: fragments=[how-1, result-0, result-3, result-2] · sim=0.4785 · **命中分=4**
  - THE-INNOCENT/p1 · fit=0.78: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-3] · sim=0.4863 · **命中分=9**
  - THE-INNOCENT/p2 · fit=0.85: fragments=[why-0, how-1, how-2, how-3, result-1, result-2, result-3] · sim=0.5065 · **命中分=7**
  - THE-LOVER/p2 · fit=0.65: fragments=[how-2, how-3, result-2] · sim=0.5607 · **命中分=3**
  - THE-JESTER/p3 · fit=0.72: fragments=[how-1, how-0, how-2, how-3, result-3] · sim=0.5607 · **命中分=5**
- **pseudo命中分合计**: 28
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: ！！！这个candidate需要注意：电影overview极短，完全没有参考价值，为什么会有那么多agents匹配到它？

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 20 -->
### Camera Cafe: The Movie (2022) [THE-EVERYMAN, THE-HERO, THE-EXPLORER] [优质·多agent]
- **tmdb_id**: 762823
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.4882
- **genres** / **language**: Comedy / es
- **overview**: Jesús Quesada, an incompetent executive, is appointed as the new director of a company in decline whose survival will now depend on both the ingenuity and ambition of his former colleagues.
- **跳转**: https://themoviecosmos.com/movie/762823
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1 · fit=0.85: fragments=[why-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4882 · **命中分=6**
  - THE-HERO/p2 · fit=0.65: fragments=[why-0, how-0, how-1, how-2, how-3] · sim=0.4342 · **命中分=5**
  - THE-EXPLORER/p2 · fit=0.65: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-3] · sim=0.4577 · **命中分=9**
- **pseudo命中分合计**: 20
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 将现实主义的新闻和一个看起来励志的overview联系，深层逻辑有点怪。low 2

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 19 -->
### Mirreyes contra Godínez 2: El retiro (2022) [THE-INNOCENT, THE-EXPLORER, THE-LOVER] [优质·多agent]
- **tmdb_id**: 1002695
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.5685
- **genres** / **language**: Comedy / es
- **overview**: A divided team heads to a corporate retreat after receiving an enticing proposal. During their time away, they must overcome their differences and find a way to reunite.
- **跳转**: https://themoviecosmos.com/movie/1002695
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p2 · fit=0.85: fragments=[why-0, how-1, how-2, how-3, result-1, result-2, result-3] · sim=0.5685 · **命中分=7**
  - THE-EXPLORER/p2 · fit=0.65: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-3] · sim=0.4980 · **命中分=9**
  - THE-LOVER/p2 · fit=0.65: fragments=[how-2, how-3, result-2] · sim=0.5425 · **命中分=3**
- **pseudo命中分合计**: 19
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 14 -->
### Corporate Animals (2019) [THE-LOVER, THE-JESTER] [优质·多agent]
- **tmdb_id**: 530076
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5821
- **genres** / **language**: Horror, Comedy / en
- **overview**: Disaster strikes when the egotistical CEO of an edible cutlery company leads her long-suffering staff on a corporate team-building trip in New Mexico. Trapped underground, this mismatched and disgruntled group must pull together to survive.
- **跳转**: https://themoviecosmos.com/movie/530076
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1 · fit=0.60: fragments=[why-0, how-0, how-1, result-0] · sim=0.5821 · **命中分=4**
  - THE-LOVER/p3 · fit=0.55: fragments=[how-1, how-2, how-3, result-1, result-3] · sim=0.5320 · **命中分=5**
  - THE-JESTER/p3 · fit=0.72: fragments=[how-1, how-0, how-2, how-3, result-3] · sim=0.5452 · **命中分=5**
- **pseudo命中分合计**: 14
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 11 -->
### Artificial Justice (2024) [THE-JESTER, THE-HERO] [优质·多agent]
- **tmdb_id**: 1209423
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5873
- **genres** / **language**: Thriller, Science Fiction / es
- **overview**: In the near future, the Government aims to replace judges with Artificial Intelligence software, pledging to effectively automate and depoliticize the justice system. Carmen Costa, a distinguished judge, has been invited to assess this new procedure. However, when the software’s creator is found dead, she realizes her life is in danger and that she will have to fight the powerful interests that are at play in the highest echelons of the State.
- **跳转**: https://themoviecosmos.com/movie/1209423
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1 · fit=0.85: fragments=[how-0, why-0, how-1, result-1, result-0, result-2] · sim=0.5873 · **命中分=6**
  - THE-HERO/p2 · fit=0.65: fragments=[why-0, how-0, how-1, how-2, how-3] · sim=0.4703 · **命中分=5**
- **pseudo命中分合计**: 11
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 抓到了人工智能取代现存职位的关键点

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 10 -->
### The Plan (2018) [A1, THE-EVERYMAN] [优质·多agent]
- **tmdb_id**: 619090
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.4894
- **genres** / **language**: Comedy, Drama / es
- **overview**: Three friends who have been fired from the company where they worked and are demoralized because of their unemployment status. In these circumstances, they meet to undertake the plan that mentions the title but there is a problem: the car with which they would travel has broken down and the crane must wait.
- **跳转**: https://themoviecosmos.com/movie/619090
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p2: fragments=[how-1, result-0, result-3, result-2] · sim=0.4635 · **命中分=4**
  - THE-EVERYMAN/p2 · fit=0.78: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4894 · **命中分=6**
- **pseudo命中分合计**: 10
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

### 单 agent 命中

**Count:** 10 candidate(s)

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 9 -->
### Let My Puppets Come (1976) [THE-INNOCENT]
- **tmdb_id**: 223922
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4932
- **genres** / **language**: Comedy, Music / en
- **overview**: The three chief executives of Creative Concepts Systems &amp; Procedures Brothers Unlimited Inc. of New York are in hot water as their latest venture has been a huge failure, and their Mafia investor, "Mr. Big", wants his $500,000 within 24 hours, or else. So Jimmy, a courier who over hears their plight, suggests they make a porno movie as an easy way of getting back the lost money.
- **跳转**: https://themoviecosmos.com/movie/223922
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1 · fit=0.78: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-3] · sim=0.4932 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 8 -->
### I Spy (2002) [THE-MAGICIAN]
- **tmdb_id**: 8427
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4731
- **genres** / **language**: Action, Adventure, Comedy, Thriller / en
- **overview**: When the Switchblade, the most sophisticated prototype stealth fighter created yet, is stolen from the U.S. government, one of the United States' top spies, Alex Scott, is called to action. What he doesn't expect is to get teamed up with a cocky civilian, World Class Boxing Champion Kelly Robinson, on a dangerous top secret espionage mission. Their assignment: using equal parts skill and humor, catch Arnold Gundars, one of the world's most successful arms dealers.
- **跳转**: https://themoviecosmos.com/movie/8427
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1 · fit=0.91: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-3] · sim=0.4731 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 8 -->
### An Eye for Beauty (2014) [THE-MAGICIAN]
- **tmdb_id**: 271826
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4930
- **genres** / **language**: Drama / fr
- **overview**: An architect and his wife see their relationship challenged.
- **跳转**: https://themoviecosmos.com/movie/271826
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p2 · fit=0.85: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-3] · sim=0.4930 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 8 -->
### Sharing Christmas (2017) [THE-MAGICIAN]
- **tmdb_id**: 483558
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4937
- **genres** / **language**: Romance, TV Movie / en
- **overview**: A real estate developer is given the opportunity of his career to transform an old shopping complex into a prime location. Unfortunately, there is one tenant who is holding out—the Christmas shop owner he met by happenstance just days ago.
- **跳转**: https://themoviecosmos.com/movie/483558
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p2 · fit=0.85: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-3] · sim=0.4937 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 8 -->
### The Factory (2018) [THE-CREATOR]
- **tmdb_id**: 513349
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5272
- **genres** / **language**: Thriller, Drama, Crime / ru
- **overview**: When a factory is bound to close, a group of workers decides to take action against the owner.
- **跳转**: https://themoviecosmos.com/movie/513349
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p2 · fit=0.85: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.5272 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 8 -->
### T.I.M. (2023) [THE-MAGICIAN]
- **tmdb_id**: 1040229
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4842
- **genres** / **language**: Science Fiction, Thriller, Horror / en
- **overview**: Prosthetics scientist Abi and her adulterous husband Paul adjust to life outside the city as Abi begins working for high-tech company Integrate, developing a humanoid AI - T.I.M.
- **跳转**: https://themoviecosmos.com/movie/1040229
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1 · fit=0.91: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-3] · sim=0.4842 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 很难判断是否有联系

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 6 -->
### The Jewel (2011) [THE-HERO]
- **tmdb_id**: 58060
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5109
- **genres** / **language**: Drama / it
- **overview**: Amanzio Rastelli appointed several of his relations to managerial positions in his firm. They decided to think internationally and now business is heavily in debt. Luckily for the Rastellis, Bolta the accountant uses all the tricks of his art to cook the books, but catastrophe awaits.
- **跳转**: https://themoviecosmos.com/movie/58060
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1 · fit=0.75: fragments=[why-0, how-0, how-1, how-2, how-3, result-0] · sim=0.5109 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 6 -->
### Don't Hug Me I'm Scared (2012) [THE-CREATOR]
- **tmdb_id**: 127144
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5155
- **genres** / **language**: Animation, Comedy, Horror, Music / en
- **overview**: A disturbing puppet short exploring the concept of creativity.
- **跳转**: https://themoviecosmos.com/movie/127144
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p1 · fit=0.78: fragments=[why-0, how-0, how-1, result-0, result-1, result-2] · sim=0.5155 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 6 -->
### Cart (2014) [THE-EVERYMAN]
- **tmdb_id**: 287647
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4991
- **genres** / **language**: Drama / ko
- **overview**: In response to a sudden dismissal of staff, workers at a big retail store begin a protest against their employer's oppressive labor policies.
- **跳转**: https://themoviecosmos.com/movie/287647
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p2 · fit=0.78: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4991 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 6 -->
### The Creative Brain (2019) [THE-CREATOR]
- **tmdb_id**: 595521
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5848
- **genres** / **language**: Documentary / en
- **overview**: Neuroscientist David Eagleman taps into the creative process of various inventors, while exploring brain-bending, risk-taking ways to spark creativity
- **跳转**: https://themoviecosmos.com/movie/595521
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p1 · fit=0.78: fragments=[why-0, how-0, how-1, result-0, result-1, result-2] · sim=0.5848 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
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

### 多 agents 命中

**Count:** 6 candidate(s)

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 32 -->
### Lone Star (1952) [A1, THE-INNOCENT, THE-HERO, THE-EXPLORER, THE-LOVER] [优质·多agent]
- **tmdb_id**: 37593
- **优质候选**: true
- **distinct_agents**: 5
- **相似度**: 0.5676
- **genres** / **language**: Western / en
- **overview**: Cattle baron Devereaux Burke is enlisted by an aging Andrew Jackson to dissuade Sam Houston from establishing Texas as a republic. Burke must fight state senator Thomas Craden, in the process winning the heart of Craden's newspaper-editor girlfriend Martha Ronda.
- **跳转**: https://themoviecosmos.com/movie/37593
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.4990 · **命中分=5**
  - A1/p2: fragments=[why-0, result-0, result-1] · sim=0.5140 · **命中分=3**
  - THE-INNOCENT/p1 · fit=0.75: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.4996 · **命中分=5**
  - THE-HERO/p1 · fit=0.90: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5196 · **命中分=5**
  - THE-EXPLORER/p1 · fit=0.85: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5665 · **命中分=5**
  - THE-LOVER/p1 · fit=0.75: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5433 · **命中分=5**
  - THE-INNOCENT/p2 · fit=0.68: fragments=[why-0, how-0, result-1, result-2] · sim=0.5676 · **命中分=4**
- **pseudo命中分合计**: 32
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 27 -->
### Machete (2010) [A1, THE-HERO, THE-EXPLORER, THE-LOVER, THE-JESTER] [优质·多agent]
- **tmdb_id**: 23631
- **优质候选**: true
- **distinct_agents**: 5
- **相似度**: 0.5642
- **genres** / **language**: Action, Comedy, Thriller / en
- **overview**: After being set-up and betrayed by the man who hired him to assassinate a Texas Senator, an ex-Federale launches a brutal rampage of revenge against his former boss.
- **跳转**: https://themoviecosmos.com/movie/23631
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p2: fragments=[why-0, result-0, result-1] · sim=0.4868 · **命中分=3**
  - THE-HERO/p1 · fit=0.90: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5076 · **命中分=5**
  - THE-EXPLORER/p1 · fit=0.85: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5557 · **命中分=5**
  - THE-LOVER/p1 · fit=0.75: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5329 · **命中分=5**
  - THE-JESTER/p1 · fit=0.90: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5642 · **命中分=5**
  - THE-HERO/p2 · fit=0.75: fragments=[result-1, how-0, why-0, result-2] · sim=0.5292 · **命中分=4**
- **pseudo命中分合计**: 27
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 24 -->
### Long Live Freedom (2013) [THE-CREATOR, THE-RULER, THE-HERO, THE-LOVER] [优质·多agent]
- **tmdb_id**: 167221
- **优质候选**: true
- **distinct_agents**: 4
- **相似度**: 0.6605
- **genres** / **language**: Comedy, Drama / it
- **overview**: Elections are approaching and things don't look too good for the opposition. Their leader can't stand the pressure and disappears. To avoid a scandal, the upper echelons of the party concoct a risky plan: to replace him with his identical twin, a philosopher with BPD, whose eclectic ideas and direct approach unexpectedly make the party surge in the polls.
- **跳转**: https://themoviecosmos.com/movie/167221
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p1 · fit=0.91: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5662 · **命中分=5**
  - THE-RULER/p1 · fit=0.78: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5359 · **命中分=5**
  - THE-HERO/p2 · fit=0.75: fragments=[result-1, how-0, why-0, result-2] · sim=0.5089 · **命中分=4**
  - THE-LOVER/p2 · fit=0.65: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.6089 · **命中分=5**
  - THE-LOVER/p3 · fit=0.55: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.6605 · **命中分=5**
- **pseudo命中分合计**: 24
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 14 -->
### Swing Vote (2008) [THE-EVERYMAN, THE-LOVER] [优质·多agent]
- **tmdb_id**: 10187
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.6188
- **genres** / **language**: Comedy, Drama / en
- **overview**: In a remarkable turn of events, the result of the presidential election comes down to one man's vote.
- **跳转**: https://themoviecosmos.com/movie/10187
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1 · fit=0.85: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5304 · **命中分=5**
  - THE-EVERYMAN/p2 · fit=0.78: fragments=[why-0, how-0, result-1, result-2] · sim=0.6188 · **命中分=4**
  - THE-LOVER/p2 · fit=0.65: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.6073 · **命中分=5**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 14 -->
### Gli onorevoli (1963) [THE-INNOCENT, THE-EVERYMAN] [优质·多agent]
- **tmdb_id**: 64946
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5872
- **genres** / **language**: Comedy / it
- **overview**: Some political candidates are determined to win the electors' preference during an election campaign in Italy.
- **跳转**: https://themoviecosmos.com/movie/64946
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1 · fit=0.75: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5214 · **命中分=5**
  - THE-EVERYMAN/p1 · fit=0.85: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5398 · **命中分=5**
  - THE-EVERYMAN/p2 · fit=0.78: fragments=[why-0, how-0, result-1, result-2] · sim=0.5872 · **命中分=4**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 10 -->
### Horizons West (1952) [THE-RULER, THE-JESTER] [优质·多agent]
- **tmdb_id**: 60535
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5725
- **genres** / **language**: Western / en
- **overview**: Brothers Dan and Neil Hammond return to Texas after the Civil War. Ambitious Dan turns to rustling and then shady land deals to build an empire. Being held for a murder, he is rescued from a lynch mob by Neil, who is now the Marshal, but there is eventually a falling out between the brothers, good triumphing over evil.
- **跳转**: https://themoviecosmos.com/movie/60535
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p1 · fit=0.78: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5363 · **命中分=5**
  - THE-JESTER/p1 · fit=0.90: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5725 · **命中分=5**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

### 单 agent 命中

**Count:** 5 candidate(s)

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 5 -->
### The Candidate (1972) [A1]
- **tmdb_id**: 21711
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5009
- **genres** / **language**: Comedy, Drama / en
- **overview**: Bill McKay is a candidate for the U.S. Senate from California. He has no hope of winning, so he is willing to tweak the establishment.
- **跳转**: https://themoviecosmos.com/movie/21711
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5009 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 5 -->
### Colosio (2012) [THE-EXPLORER]
- **tmdb_id**: 151708
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5711
- **genres** / **language**: Crime, Drama, Thriller / es
- **overview**: It's 1994 in Mexico, the nation was witnessing a turbulent year since its beginnings. An indigenous rebellion shakes the country. Three months later, the ruling party's presidential candidate is brutally murdered during a rally in Tijuana. The country is concerned. Nobody knows who's behind this event, it all points to a conspiracy. Andrés Vázquez, an intelligence expert, is commissioned to lead a secret investigation parallel to the official government issued one. But another expert agent, el Seco, has received orders to wipe out all witnesses and get rid of the evidence surrounding the candidate's murder. As Andrés begins putting the pieces of this intricate puzzle together and comes closer to the truth, he realizes he's also putting his life and that of his loved ones in peril.
- **跳转**: https://themoviecosmos.com/movie/151708
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p2 · fit=0.65: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5711 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 5 -->
### 120 Seconds to Get Elected (2006) [THE-LOVER]
- **tmdb_id**: 239070
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6272
- **genres** / **language**: Comedy / en
- **overview**: A politician has just a couple of minutes to convince people to vote for him, and tries to seduce his audience with promises he thinks they want to hear.
- **跳转**: https://themoviecosmos.com/movie/239070
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p3 · fit=0.55: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.6272 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 5 -->
### 2000 Mules (2022) [THE-CREATOR]
- **tmdb_id**: 933554
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5148
- **genres** / **language**: Documentary / en
- **overview**: Bestselling author and award-winning filmmaker, Dinesh D’Souza, exposes widespread coordinated voter fraud in the 2020 election sufficient to change the overall outcome. Drawing on research provided by the election integrity group, True the Vote, “2000 Mules” offers two types of evidence: geotracking and video. The geotracking evidence, based on a database of ten trillion cell phone pings, exposes an elaborate network of professional operatives, called mules, delivering fraudulent votes to mail-in boxes in the five key states where the election was decided. Video evidence obtained from official surveillance cameras corroborates the cellular positioning data. The film concludes by exploring ways to assist in the prevention of election fraud in future democratic elections.
- **跳转**: https://themoviecosmos.com/movie/933554
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p1 · fit=0.91: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5148 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 5 -->
### People's Avengers (1943) [THE-EXPLORER]
- **tmdb_id**: 1168015
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5761
- **genres** / **language**: Documentary / ru
- **overview**: About the partisan movement during the Great Patriotic War.
- **跳转**: https://themoviecosmos.com/movie/1168015
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p2 · fit=0.65: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.5761 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

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

**Count:** 4 candidate(s)

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 15 -->
### Scandal (1950) [THE-RULER, THE-CREATOR, THE-JESTER] [优质·多agent]
- **tmdb_id**: 32690
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.6828
- **genres** / **language**: Drama / ja
- **overview**: A celebrity photograph sparks a court case as a tabloid magazine spins a scandalous yarn over a painter and a famous singer.
- **跳转**: https://themoviecosmos.com/movie/32690
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p1 · fit=0.88: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5883 · **命中分=5**
  - THE-CREATOR/p2 · fit=0.82: fragments=[how-0, how-1, result-0, result-1] · sim=0.6828 · **命中分=4**
  - THE-JESTER/p2 · fit=0.78: fragments=[why-0, how-0, how-1, how-2, result-1, result-0] · sim=0.6427 · **命中分=6**
- **pseudo命中分合计**: 15
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 11 -->
### I Like Mountain Music (1933) [THE-RULER, THE-JESTER] [优质·多agent]
- **tmdb_id**: 151913
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.6520
- **genres** / **language**: Animation, Comedy, Family, Music / en
- **overview**: After hours, individuals on various magazine covers in a drugstore come to life and sing, speak, or perform. Caricature celebrity depictions include George Arliss, Eddie Cantor, Sonja Henie, Benito Mussolini, Ignacy Paderewski, Edward G. Robinson, Will Rogers, and Ed Wynn. A robbery sequence features bad guys breaking into the cash register and Sherlock Holmes and Dr. Watson on the case. King Kong also makes an appearance. A Merrie Melody cartoon.
- **跳转**: https://themoviecosmos.com/movie/151913
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p1 · fit=0.88: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5791 · **命中分=5**
  - THE-JESTER/p2 · fit=0.78: fragments=[why-0, how-0, how-1, how-2, result-1, result-0] · sim=0.6520 · **命中分=6**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 9 -->
### One Way (2006) [THE-LOVER, THE-CREATOR] [优质·多agent]
- **tmdb_id**: 7298
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.6230
- **genres** / **language**: Crime, Mystery, Thriller / en
- **overview**: To cover up his infidelities and protect his upcoming marriage, a star advertiser helps free an accused rapist by giving a false alibi and suffers the brutal revenge of the victim.
- **跳转**: https://themoviecosmos.com/movie/7298
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1 · fit=0.90: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6230 · **命中分=5**
  - THE-CREATOR/p3 · fit=0.75: fragments=[why-0, how-0, how-1, result-0] · sim=0.5398 · **命中分=4**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 8 -->
### The Roundup 3: No Way Out (2023) [A1, THE-HERO] [优质·多agent]
- **tmdb_id**: 955555
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.6006
- **genres** / **language**: Action, Crime, Comedy, Thriller / ko
- **overview**: Detective Ma Seok-do changes his affiliation from the Geumcheon Police Station to the Metropolitan Investigation Team, in order to eradicate Japanese gangsters who enter Korea to commit heinous crimes.
- **跳转**: https://themoviecosmos.com/movie/955555
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p3: fragments=[how-1, result-1, how-2] · sim=0.5008 · **命中分=3**
  - THE-HERO/p1 · fit=0.95: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6006 · **命中分=5**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

### 单 agent 命中

**Count:** 8 candidate(s)

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 6 -->
### This Film Is Not Yet Rated (2006) [THE-OUTLAW]
- **tmdb_id**: 16070
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6074
- **genres** / **language**: Documentary / en
- **overview**: Kirby Dick's provocative documentary investigates the secretive and inconsistent process by which the Motion Picture Association of America rates films, revealing the organization's underhanded efforts to control culture. Dick questions whether certain studios get preferential treatment and exposes the discrepancies in how the MPAA views sex and violence.
- **跳转**: https://themoviecosmos.com/movie/16070
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p1 · fit=0.78: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.6074 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 6 -->
### Eye of the Beholder (1999) [THE-MAGICIAN]
- **tmdb_id**: 18681
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6174
- **genres** / **language**: Mystery, Thriller / en
- **overview**: A reclusive surveillance expert is hired to spy on a mysterious blackmailer, who just may be a serial killer.
- **跳转**: https://themoviecosmos.com/movie/18681
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1 · fit=0.90: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.6174 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 6 -->
### The Prince of Magicians (1901) [THE-MAGICIAN]
- **tmdb_id**: 107269
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6046
- **genres** / **language**: Fantasy, Comedy / fr
- **overview**: A magician does tricks with the aid of his assistant, the Human Pump.
- **跳转**: https://themoviecosmos.com/movie/107269
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1 · fit=0.90: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.6046 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Prophecy (2015) [THE-HERO]
- **tmdb_id**: 347483
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5918
- **genres** / **language**: Mystery, Thriller / ja
- **overview**: The cyber crime investigation division at the Tokyo Metropolitan Police Department finds a video on website "YOURTUBE." In the video, a man covered by a newspaper, warns that a fire will be set at a food processing company. More crime notices are soon found involving violent crimes.  Geitsu is the main guy behind the group "Shinbunshi," which has posted the videos. He used to work as a temporary employee at an IT company, but was unfairly dismissed. He then begins doing manual labor work and meets the other members of "Shinbushi."
- **跳转**: https://themoviecosmos.com/movie/347483
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1 · fit=0.95: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5918 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Kavan (2017) [THE-CREATOR]
- **tmdb_id**: 449742
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6451
- **genres** / **language**: Thriller, Drama / ta
- **overview**: A budding journalist passionate about ethical, noble, hard-hitting journalism understands the more flourishing ghetto of sensationalism &amp; news fabrication that the Entertainment TV Channel he belongs to, thrives on. When caught in a dilemma of whether to hold for a while or rise in protest, a situation forces him to make a decision that puts him out of work but… there begins his work.
- **跳转**: https://themoviecosmos.com/movie/449742
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p1 · fit=0.88: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.6451 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Fyre Fraud (2019) [THE-JESTER]
- **tmdb_id**: 575190
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5889
- **genres** / **language**: Documentary / en
- **overview**: A true-crime comedy exploring a failed music festival turned internet meme at the nexus of social media influence, late-stage capitalism, and morality in the post-truth era.
- **跳转**: https://themoviecosmos.com/movie/575190
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1 · fit=0.91: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5889 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Night in Paradise (2020) [THE-HERO]
- **tmdb_id**: 606523
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5882
- **genres** / **language**: Crime, Thriller, Action / ko
- **overview**: An assassin named Tae-goo is offered a chance to switch sides with his rival Bukseong gang, headed by Chairman Doh. Tae-goo rejects the offer that results in the murder of his sister and niece. In revenge, Tae-goo brutally kills Chairman Doh and his men and flees to Jeju Island where he meets Jae-yeon, a terminally ill woman. Though, the henchman of the Bukseong gang, Executive Ma is mercilessly hunting Tae-goo to take revenge.
- **跳转**: https://themoviecosmos.com/movie/606523
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p2 · fit=0.88: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.5882 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Cobweb (2023) [THE-HERO]
- **tmdb_id**: 901121
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6107
- **genres** / **language**: Comedy, Drama / ko
- **overview**: In the 1970s, Director Kim is obsessed by the desire to re-shoot the ending of his completed film Cobweb, but chaos and turmoil grip the set with interference from the censorship authorities, and the complaints of actors and producers who can't understand the re-written ending. Will Kim be able to find a way through this chaos to fulfill his artistic ambitions and complete his masterpiece?
- **跳转**: https://themoviecosmos.com/movie/901121
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p2 · fit=0.88: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.6107 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
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

### 多 agents 命中

**Count:** 8 candidate(s)

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 43 -->
### Raining Cats and Frogs (2003) [THE-HERO, THE-MAGICIAN, THE-JESTER] [优质·多agent]
- **tmdb_id**: 22624
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.6122
- **genres** / **language**: Animation, Fantasy, Adventure / fr
- **overview**: It's a catastrophe! A flood has hit our planet and an unusual group of people are all that remains. Led by Ferdinand, a modern day Noah, this little group have managed to defy the furiously raging elements. People and animals alike are dragged through this incredible whirlpool of an adventure.
- **跳转**: https://themoviecosmos.com/movie/22624
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1 · fit=0.88: fragments=[why-0, how-2, how-3, how-4, result-0, result-5] · sim=0.5258 · **命中分=6**
  - THE-MAGICIAN/p1 · fit=0.75: fragments=[why-0, how-1, how-2, how-3, how-4, how-5, result-0, result-5] · sim=0.5124 · **命中分=8**
  - THE-JESTER/p1 · fit=0.75: fragments=[why-1, how-0, how-1, how-2, how-3, how-4, result-0, result-1, result-2, how-5] · sim=0.6122 · **命中分=10**
  - THE-JESTER/p2 · fit=0.68: fragments=[why-0, why-1, how-2, how-3, how-4, how-5, result-0, result-1, result-5] · sim=0.5006 · **命中分=9**
  - THE-MAGICIAN/p3 · fit=0.82: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, why-1, result-0, result-1, result-3] · sim=0.5530 · **命中分=10**
- **pseudo命中分合计**: 43
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 36 -->
### World Gone Wild (1987) [THE-OUTLAW, THE-HERO, THE-MAGICIAN] [优质·多agent]
- **tmdb_id**: 38141
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.6195
- **genres** / **language**: Action, Science Fiction / en
- **overview**: In the nuclear ravaged wasteland of Earth 2087 water is as precious as life itself. The isolated Lost Wells outpost survived the holocaust and the inhabitants guard the source of their existence. Now an evil cult of renegades want control of their valuable water supply. And the villagers are no match for such brute military force. Only one man can help the stricken community - a mercenary living in a distance cannibal city. But even he, and his strange henchmen, may not be able to survive in the world gone wild.
- **跳转**: https://themoviecosmos.com/movie/38141
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p1 · fit=0.91: fragments=[why-0, how-1, how-2, how-3, how-4, result-0, result-3, result-5] · sim=0.5482 · **命中分=8**
  - THE-HERO/p2 · fit=0.85: fragments=[why-1, how-0, result-0, result-1, result-3] · sim=0.6195 · **命中分=5**
  - THE-OUTLAW/p2 · fit=0.88: fragments=[why-1, how-0, how-1, how-2, how-3, how-4, result-0, result-5] · sim=0.5153 · **命中分=8**
  - THE-MAGICIAN/p2 · fit=0.68: fragments=[how-0, how-1, how-2, how-3, how-4, how-5, why-0, result-5] · sim=0.5044 · **命中分=8**
  - THE-OUTLAW/p3 · fit=0.85: fragments=[why-1, how-0, how-1, how-2, how-3, result-0, result-3] · sim=0.5561 · **命中分=7**
- **pseudo命中分合计**: 36
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 30 -->
### Poem of the Sea (1958) [A1, THE-EVERYMAN, THE-SAGE, THE-OUTLAW] [优质·多agent]
- **tmdb_id**: 257637
- **优质候选**: true
- **distinct_agents**: 4
- **相似度**: 0.5671
- **genres** / **language**: Drama / ru
- **overview**: A Soviet dam project means that many old Ukrainian villages will end up under water. There are conflicts between the dam engineers and villagers who don't want to move.
- **跳转**: https://themoviecosmos.com/movie/257637
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, how-3] · sim=0.5671 · **命中分=4**
  - A1/p2: fragments=[how-4, how-5, result-5] · sim=0.4654 · **命中分=3**
  - THE-EVERYMAN/p1 · fit=0.75: fragments=[why-0, why-1, how-1, how-2, how-3, how-4] · sim=0.5489 · **命中分=6**
  - THE-SAGE/p1 · fit=0.88: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5299 · **命中分=5**
  - THE-EVERYMAN/p2 · fit=0.68: fragments=[result-0, result-1, result-3, result-4, result-5] · sim=0.5044 · **命中分=5**
  - THE-OUTLAW/p3 · fit=0.85: fragments=[why-1, how-0, how-1, how-2, how-3, result-0, result-3] · sim=0.5614 · **命中分=7**
- **pseudo命中分合计**: 30
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 24 -->
### Flood (2007) [THE-EVERYMAN, THE-SAGE, THE-MAGICIAN] [优质·多agent]
- **tmdb_id**: 6309
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.5888
- **genres** / **language**: Drama, Action, Thriller / en
- **overview**: Timely yet terrifying, The Flood predicts the unthinkable. When a raging storm coincides with high seas it unleashes a colossal tidal surge, which travels mercilessly down England's East Coast and into the Thames Estuary. Overwhelming the Barrier, torrents of water pour into the city. The lives of millions of Londoners are at stake.
- **跳转**: https://themoviecosmos.com/movie/6309
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1 · fit=0.75: fragments=[why-0, why-1, how-1, how-2, how-3, how-4] · sim=0.5381 · **命中分=6**
  - THE-SAGE/p2 · fit=0.76: fragments=[why-1, how-1, how-2, how-3, how-4, how-5, result-0, result-4] · sim=0.5888 · **命中分=8**
  - THE-MAGICIAN/p3 · fit=0.82: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, why-1, result-0, result-1, result-3] · sim=0.5475 · **命中分=10**
- **pseudo命中分合计**: 24
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 15 -->
### Disaster Wars: Earthquake vs. Tsunami (2013) [THE-SAGE, THE-CAREGIVER] [优质·多agent]
- **tmdb_id**: 289214
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.6121
- **genres** / **language**: Thriller, Action, Drama, Science Fiction / en
- **overview**: Deep underwater in the Marianas Trench an accident results in a devastating Tsunami that destroys the Hawaiian Islands as it continues toward the west coast. Panic ensues all up and down the western coast of North and South America. In an attempt to lessen its impact, scientists launch an underwater explosion that inadvertently makes the tsunami more powerful and focused on Los Angeles. Scientists rush to a solution while the military begins planning for the worst. Los Angeles begins emergency evacuation. Lives and loves are lost even as a brash young grad student comes up with a solution: start the mother of all earthquakes to counter the rushing torrent and raise the continental shelf off the coast of the United States.
- **跳转**: https://themoviecosmos.com/movie/289214
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-SAGE/p2 · fit=0.76: fragments=[why-1, how-1, how-2, how-3, how-4, how-5, result-0, result-4] · sim=0.6121 · **命中分=8**
  - THE-CAREGIVER/p3 · fit=0.78: fragments=[how-1, how-2, how-3, how-4, how-5, result-0, result-2] · sim=0.5802 · **命中分=7**
- **pseudo命中分合计**: 15
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 14 -->
### Road Wars (2015) [THE-HERO, THE-LOVER] [优质·多agent]
- **tmdb_id**: 333545
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.6080
- **genres** / **language**: Science Fiction, Action / en
- **overview**: After the earth’s water supply is depleted, the survivors form roving road gangs, armed to the teeth and desperate to find and protect water supplies. But when a new breed of blood-drinking humans emerges, the survivors must contend with a whole new threat to their existence.
- **跳转**: https://themoviecosmos.com/movie/333545
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p2 · fit=0.85: fragments=[why-1, how-0, result-0, result-1, result-3] · sim=0.6080 · **命中分=5**
  - THE-LOVER/p2 · fit=0.72: fragments=[why-1, how-1, how-2, how-3, how-4, how-5, result-0, result-3, result-4] · sim=0.5124 · **命中分=9**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 13 -->
### Vajont (2001) [THE-CREATOR, THE-SAGE] [优质·多agent]
- **tmdb_id**: 48941
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5261
- **genres** / **language**: Drama / it
- **overview**: On October 9th, 1963, at 10:39 pm, 260 million cubic meters of rock fell down from Mount Toc to the artificial lake formed by the Vajont dam, the higher dam in the world. The landslide formed a 250-meters wave and 50 million cubic meters of water completely destroied all the below towns, killing more than 2000 people. Planned by engineer Semenza, Vajont dam (263 meters) had to carry the electricity in all the houses of the country. Tina Merlin, a journalist from 'L'Unitá', tried for years to denounce the danger to build a dam near the Mount Toc and expecially to denounce all the omissions by the corrupted politicians and workers in charge of the dam construction. They preferred to trust in old geologist Dal Piaz instead to hear engineer Semenza young son's alarming analysis. No one seemed to understand the high danger until that October fatal night.
- **跳转**: https://themoviecosmos.com/movie/48941
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p1 · fit=0.65: fragments=[why-0, how-1, how-2, how-3, result-1, result-2, how-4, result-0] · sim=0.5261 · **命中分=8**
  - THE-SAGE/p1 · fit=0.88: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5047 · **命中分=5**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 11 -->
### The Sweet Hereafter (1997) [THE-EVERYMAN, THE-CAREGIVER] [优质·多agent]
- **tmdb_id**: 10217
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5512
- **genres** / **language**: Drama / en
- **overview**: A small mountain community in Canada is devastated when a school bus accident leaves more than a dozen of its children dead. A big-city lawyer arrives to help the survivors' and victims' families prepare a class-action suit, but his efforts only seem to push the townspeople further apart. At the same time, one teenage survivor of the accident has to reckon with the loss of innocence brought about by a different kind of damage.
- **跳转**: https://themoviecosmos.com/movie/10217
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p2 · fit=0.68: fragments=[result-0, result-1, result-3, result-4, result-5] · sim=0.5417 · **命中分=5**
  - THE-CAREGIVER/p2 · fit=0.85: fragments=[why-1, how-1, how-2, how-3, result-0, result-5] · sim=0.5512 · **命中分=6**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

### 单 agent 命中

**Count:** 11 candidate(s)

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 10 -->
### Water Wrackets (1978) [THE-JESTER]
- **tmdb_id**: 249011
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5732
- **genres** / **language**: Fantasy / en
- **overview**: Multifarious images of a lake are overlaid with water effects and a narrated history of the campaigns fought by the fictional water-wracket army.
- **跳转**: https://themoviecosmos.com/movie/249011
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1 · fit=0.75: fragments=[why-1, how-0, how-1, how-2, how-3, how-4, result-0, result-1, result-2, how-5] · sim=0.5732 · **命中分=10**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 9 -->
### Tidal Wave (2009) [THE-LOVER]
- **tmdb_id**: 33196
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5538
- **genres** / **language**: Action, Drama, Thriller / ko
- **overview**: On Haeundae Beach, a guilt-ridden fisherman takes care of a woman whose father accidentally got killed. A scientist reunites with his ex-wife and a daughter who doesn't even remember his face. And a poor rescue worker falls in love with a rich city girl. When they all find out a gigantic tsunami will hit the beach, they realize they only have 10 minutes to escape.
- **跳转**: https://themoviecosmos.com/movie/33196
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p2 · fit=0.72: fragments=[why-1, how-1, how-2, how-3, how-4, how-5, result-0, result-3, result-4] · sim=0.5538 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 9 -->
### Deluge (1933) [THE-LOVER]
- **tmdb_id**: 163293
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5334
- **genres** / **language**: Science Fiction, Drama, Thriller / en
- **overview**: A massive earthquake strikes the United States, which destroys the West Coast and unleashes a massive flood that threatens to destroy the East Coast as well.
- **跳转**: https://themoviecosmos.com/movie/163293
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1 · fit=0.65: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-1, result-2, result-5] · sim=0.5334 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 9 -->
### Quel maledetto ponte sull'Elba (1969) [THE-LOVER]
- **tmdb_id**: 285427
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5532
- **genres** / **language**: War / it
- **overview**: Quel maledetto ponte sull'Elba
- **跳转**: https://themoviecosmos.com/movie/285427
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1 · fit=0.65: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-1, result-2, result-5] · sim=0.5532 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 8 -->
### Left Behind: World at War (2005) [THE-CREATOR]
- **tmdb_id**: 38828
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5666
- **genres** / **language**: Action, Adventure, Fantasy, Science Fiction, Thriller / en
- **overview**: A year and a half ago, the globe was hit with the biggest catastrophe it had ever seen. Without warning and without explanation, hundreds of millions simply vanished off the face of the Earth. The world was in chaos like never before. Yet somehow one man seemed to rise to the challenge. One man had the strength and conviction to unite a shattered world. One man gave the world hope. That man was Nicolae Carpathia, who now rules the entire world.
- **跳转**: https://themoviecosmos.com/movie/38828
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p1 · fit=0.65: fragments=[why-0, how-1, how-2, how-3, result-1, result-2, how-4, result-0] · sim=0.5666 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 8 -->
### The Windermere Children (2020) [THE-CAREGIVER]
- **tmdb_id**: 664423
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5510
- **genres** / **language**: Drama, War, History / en
- **overview**: The story of the pioneering project to rehabilitate child survivors of the Holocaust on the shores of Lake Windermere.
- **跳转**: https://themoviecosmos.com/movie/664423
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1 · fit=0.91: fragments=[why-0, why-1, how-0, how-1, how-2, result-0, result-2, result-3] · sim=0.5510 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 8 -->
### Bloat (2025) [THE-OUTLAW]
- **tmdb_id**: 937393
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5334
- **genres** / **language**: Horror / en
- **overview**: After a near-death drowning accident, a young boy's family is horrified to discover he has become possessed by a legendary demon from the depths of the lake. As the family races against time to save the boy's soul, the evil monster inside the child tears the family apart as it seeks to destroy everyone in its path.
- **跳转**: https://themoviecosmos.com/movie/937393
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p1 · fit=0.91: fragments=[why-0, how-1, how-2, how-3, how-4, result-0, result-3, result-5] · sim=0.5334 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 7 -->
### Reap the Wild Wind (1942) [THE-HERO]
- **tmdb_id**: 63617
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5619
- **genres** / **language**: Adventure, Action, Romance / en
- **overview**: The Florida Keys in 1840, where the implacable hurricanes of the Caribbean scream, where the salvagers of Key West, like the intrepid and beautiful Loxi Claiborne and her crew, reap, aboard frail schooners, the harvest of the wild wind, facing the shark teeth of the reefs to rescue the sailors and the cargo from the shipwrecks caused by the scavengers of the sea.
- **跳转**: https://themoviecosmos.com/movie/63617
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p3 · fit=0.82: fragments=[why-0, how-1, how-2, how-3, how-4, result-2, result-3] · sim=0.5619 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 7 -->
### Divers at Work on the Wreck of the "Maine" (1898) [THE-HERO]
- **tmdb_id**: 104480
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5709
- **genres** / **language**: Documentary / fr
- **overview**: Divers go to work on a wrecked ship (the battleship Maine that was blown up in Havana harbour during the Spanish-American War), surrounded by curiously disproportionate fish.
- **跳转**: https://themoviecosmos.com/movie/104480
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p3 · fit=0.82: fragments=[why-0, how-1, how-2, how-3, how-4, result-2, result-3] · sim=0.5709 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 7 -->
### The Rescue (2020) [THE-CAREGIVER]
- **tmdb_id**: 613658
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5946
- **genres** / **language**: Drama, Thriller, Action / zh
- **overview**: A rescue unit within the Chinese Coast Guard are forced to overcome their personal differences to resolve a crisis.
- **跳转**: https://themoviecosmos.com/movie/613658
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p3 · fit=0.78: fragments=[how-1, how-2, how-3, how-4, how-5, result-0, result-2] · sim=0.5946 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 6 -->
### The Storm (2009) [THE-CAREGIVER]
- **tmdb_id**: 29602
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5379
- **genres** / **language**: Drama / nl
- **overview**: A fictional story within the historical context of the disastrous flood that engulfed the Dutch coastal province of Zeeland in 1953. When their farmhouse is destroyed by the flood, teenage mother Julia gets separated from her baby boy, whom she kept hidden in a box. She is saved from drowning by a young air force lieutenant, who agrees to go help looking for Julia's little son.
- **跳转**: https://themoviecosmos.com/movie/29602
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p2 · fit=0.85: fragments=[why-1, how-1, how-2, how-3, result-0, result-5] · sim=0.5379 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
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

### 多 agents 命中

**Count:** 6 candidate(s)

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 37 -->
### Lords of Scam (2021) [A1, THE-EXPLORER, THE-OUTLAW, THE-CREATOR, THE-SAGE] [优质·多agent]
- **tmdb_id**: 888917
- **优质候选**: true
- **distinct_agents**: 5
- **相似度**: 0.5150
- **genres** / **language**: Documentary, Crime / fr
- **overview**: This documentary traces the rise and crash of scammers who conned the EU carbon quota system and pocketed millions before turning on one another.
- **跳转**: https://themoviecosmos.com/movie/888917
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.4068 · **命中分=4**
  - A1/p2: fragments=[why-0, how-1, result-0] · sim=0.4472 · **命中分=3**
  - THE-EXPLORER/p1 · fit=0.91: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5036 · **命中分=6**
  - THE-OUTLAW/p1 · fit=0.85: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5150 · **命中分=6**
  - THE-CREATOR/p1 · fit=0.78: fragments=[why-0, how-1, result-0] · sim=0.5044 · **命中分=3**
  - THE-SAGE/p1 · fit=0.85: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4640 · **命中分=5**
  - THE-CREATOR/p2 · fit=0.85: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.4595 · **命中分=5**
  - THE-SAGE/p3 · fit=0.82: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.4706 · **命中分=5**
- **pseudo命中分合计**: 37
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 20 -->
### The Clearstream Affair (2015) [A1, THE-OUTLAW, THE-SAGE, THE-MAGICIAN] [优质·多agent]
- **tmdb_id**: 320318
- **优质候选**: true
- **distinct_agents**: 4
- **相似度**: 0.5319
- **genres** / **language**: Thriller, Drama / fr
- **overview**: Journalist Denis Robert sparked a storm in the world of European finance by denouncing the murky operations of banking firm Clearstream. His quest to reveal the truth behind a secret world of shadowy multinational banking puts him in contact with an ever-expanding anti-corruption investigation carried out by Judge Renaud Van Ruymbeke. Their paths will lead them to the heart of a political/financial intrigue, which will rock the foundations of Europe and the French government itself.
- **跳转**: https://themoviecosmos.com/movie/320318
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.4122 · **命中分=4**
  - THE-OUTLAW/p1 · fit=0.85: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.4883 · **命中分=6**
  - THE-SAGE/p1 · fit=0.85: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4502 · **命中分=5**
  - THE-MAGICIAN/p3 · fit=0.72: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5319 · **命中分=5**
- **pseudo命中分合计**: 20
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 19 -->
### BLAME! (2017) [THE-CAREGIVER, THE-MAGICIAN, THE-EXPLORER] [优质·多agent]
- **tmdb_id**: 409421
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.5307
- **genres** / **language**: Action, Drama, Science Fiction, Animation / ja
- **overview**: In the distant technological future, civilization has reached its ultimate Net-based form. An "infection" in the past caused the automated systems to spiral out of order, resulting in a multi-leveled city structure that replicates itself infinitely in all directions. Now humanity has lost access to the city's controls, and is hunted down and purged by the defense system known as the Safeguard. In a tiny corner of the city, a little enclave known as the Electro-Fishers is facing eventual extinction, trapped between the threat of the Safeguard and dwindling food supplies. A girl named Zuru goes on a journey to find food for her village, only to inadvertently cause doom when an observation tower senses her and summons a Safeguard pack to eliminate the threat. With her companions dead and all escape routes blocked, the only thing that can save her now is the sudden arrival of Killy the Wanderer, on his quest for the Net Terminal Genes, the key to restoring order to the world.
- **跳转**: https://themoviecosmos.com/movie/409421
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CAREGIVER/p1 · fit=0.75: fragments=[why-0, how-0, how-1, result-0] · sim=0.4374 · **命中分=4**
  - THE-MAGICIAN/p1 · fit=0.85: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5307 · **命中分=5**
  - THE-EXPLORER/p2 · fit=0.85: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.5205 · **命中分=5**
  - THE-MAGICIAN/p3 · fit=0.72: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5214 · **命中分=5**
- **pseudo命中分合计**: 19
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 12 -->
### The Cop (1970) [THE-CREATOR, THE-MAGICIAN, THE-SAGE] [优质·多agent]
- **tmdb_id**: 94376
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.5051
- **genres** / **language**: Drama, Crime, Thriller / fr
- **overview**: A crackdown on drugs leads a burned out cop to take the law into his own hands and seek revenge against villainous drug dealers. Word comes down from above that the United States feels French authorities have been lax on their arrests of the dealers. A violent action feature finds the harried inspector battling his colleagues as much as the criminal element targeted for extermination.
- **跳转**: https://themoviecosmos.com/movie/94376
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p1 · fit=0.78: fragments=[why-0, how-1, result-0] · sim=0.5051 · **命中分=3**
  - THE-MAGICIAN/p2 · fit=0.78: fragments=[how-1, how-2, result-0, result-1] · sim=0.4944 · **命中分=4**
  - THE-SAGE/p2 · fit=0.78: fragments=[why-0, how-1, how-2, result-0, result-1] · sim=0.4649 · **命中分=5**
- **pseudo命中分合计**: 12
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 11 -->
### Smoke Signals (2024) [THE-INNOCENT, THE-RULER] [优质·多agent]
- **tmdb_id**: 1001028
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5034
- **genres** / **language**: Thriller, Drama / fr
- **overview**: 2012, John Dalli, the European Commissioner for Health, is accused of corruption and influence peddling related to the tobacco industry. French Member of the European Parliament José Bové, maverick politician and prominent figure of the environmental party, suspects a setup by the tobacco manufacturer Swedish Match, potentially involving the President of the European Commission, José Barroso. Standing alone against all odds, he decides to investigate and unravel this story, which shook the foundations of the entire European institutions.
- **跳转**: https://themoviecosmos.com/movie/1001028
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1 · fit=0.75: fragments=[why-0, how-1, how-2, result-0, result-1] · sim=0.4550 · **命中分=5**
  - THE-RULER/p1 · fit=0.88: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5034 · **命中分=6**
- **pseudo命中分合计**: 11
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### Special Section (1975) [A1, THE-INNOCENT] [优质·多agent]
- **tmdb_id**: 79921
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.4717
- **genres** / **language**: Drama, History, Thriller / fr
- **overview**: In Nazi-occupied France, a German officer is assassinated. The Germans demand justice, and the Vichy government is quick to capitulate. Unable to apprehend the actual culprits, Minister of Justice Joseph Barthélémy decides the execution of token Frenchmen will suffice, but the problem is finding judges and jurors eager to participate in a sham trial of innocent men. The solution is a Special Section, a court comprised of individuals handpicked for this exact purpose.
- **跳转**: https://themoviecosmos.com/movie/79921
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p3: fragments=[result-0, result-1] · sim=0.4717 · **命中分=2**
  - THE-INNOCENT/p1 · fit=0.75: fragments=[why-0, how-1, how-2, result-0, result-1] · sim=0.4470 · **命中分=5**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

### 单 agent 命中

**Count:** 12 candidate(s)

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 6 -->
### Nothing to Declare (2010) [THE-EXPLORER]
- **tmdb_id**: 52077
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4735
- **genres** / **language**: Comedy / fr
- **overview**: During the elimination of the Belgian/French border in the 90s, a Belgian customs officer is forced to team up with one of his French counterparts.
- **跳转**: https://themoviecosmos.com/movie/52077
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p1 · fit=0.91: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.4735 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 6 -->
### Speaking of Murder (1957) [THE-OUTLAW]
- **tmdb_id**: 58926
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4929
- **genres** / **language**: Crime, Drama, Thriller / fr
- **overview**: Louis Bertain is the owner of a Paris garage which is the front for a robbery gang. He and his accomplices are careful to keep up a civic veneer by day, indulging in criminal activities only when "the red light is on" at night. This status quo is upset when one of the gang members becomes convinced that Louis' younger brother is a police informer.
- **跳转**: https://themoviecosmos.com/movie/58926
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p2 · fit=0.65: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.4929 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 6 -->
### The Last One of the Six (1941) [THE-RULER]
- **tmdb_id**: 142977
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5011
- **genres** / **language**: Drama, Mystery, Thriller / fr
- **overview**: Paris, France. Commissaire Wens is put in charge of the investigation into the murder of one of six friends who, in the past, made a very profitable promise.
- **跳转**: https://themoviecosmos.com/movie/142977
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p1 · fit=0.88: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5011 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 6 -->
### Bullet Train Down (2022) [THE-OUTLAW]
- **tmdb_id**: 1006540
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4800
- **genres** / **language**: Action / en
- **overview**: On its maiden run, the world's fastest bullet train is rigged with a bomb that will explode if it dips below 200 mph.
- **跳转**: https://themoviecosmos.com/movie/1006540
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p2 · fit=0.65: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.4800 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### Moon 44 (1990) [THE-EXPLORER]
- **tmdb_id**: 2927
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5294
- **genres** / **language**: Science Fiction / en
- **overview**: Year 2038: The mineral resources of the earth are drained, in space there are fights for the last deposits on other planets and satellites. This is the situation when one of the bigger mining corporations has lost all but one mineral moons and many of their fully automatic mining robots are disappearing on their flight home. Since nobody else wants the job, they send prisoners to defend the mining station. Among them undercover agent Stone, who shall clear the whereabouts of the expensive robots. In an atmosphere of corruption, fear and hatred he gets between the fronts of rivaling groups.
- **跳转**: https://themoviecosmos.com/movie/2927
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p2 · fit=0.85: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.5294 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### Antitrust (2001) [THE-LOVER]
- **tmdb_id**: 9989
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4789
- **genres** / **language**: Action, Crime, Drama / en
- **overview**: A computer programmer's dream job at a hot Portland-based firm turns nightmarish when he discovers his boss has a secret and ruthless means of dispatching anti-trust problems.
- **跳转**: https://themoviecosmos.com/movie/9989
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p3 · fit=0.42: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.4789 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### Future X-Cops (2010) [THE-RULER]
- **tmdb_id**: 41535
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5326
- **genres** / **language**: Action, Science Fiction / zh
- **overview**: A cop travels back in time to take on a corporation that's out to eliminate a doctor who has created a new technology which can break up the monopoly on a energy resources.
- **跳转**: https://themoviecosmos.com/movie/41535
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p2 · fit=0.82: fragments=[why-0, how-1, how-2, result-0, result-1] · sim=0.5326 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### Gog (1954) [THE-RULER]
- **tmdb_id**: 63333
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4914
- **genres** / **language**: Thriller, Science Fiction, Horror / en
- **overview**: A mechanical brain is programmed to sabotage the government's secret lab while working on the first space station.
- **跳转**: https://themoviecosmos.com/movie/63333
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p2 · fit=0.82: fragments=[why-0, how-1, how-2, result-0, result-1] · sim=0.4914 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### Lilly Turner (1933) [THE-LOVER]
- **tmdb_id**: 96170
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5145
- **genres** / **language**: Drama / en
- **overview**: One woman faces many trials on the road to romance after unwittingly marrying a bigamist, then a carnival barker, and then falling for a young engineer.
- **跳转**: https://themoviecosmos.com/movie/96170
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p2 · fit=0.38: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.5145 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### Bounty Killer (2013) [THE-LOVER]
- **tmdb_id**: 209504
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4836
- **genres** / **language**: Action, Science Fiction / en
- **overview**: It’s been 20 years since the corporations took over the world’s governments. Their thirst for power and profits led to the Corporate Wars, a fierce global battle that laid waste to society as we know it. Born from the ash, the Council of Nine rose as a new law and order for this dark age. To avenge the corporations’ reckless destruction, the Council issues death warrants for all white collar criminals. Their hunters—the bounty killer. From amateur savage to graceful assassin, the bounty killers now compete for body count, fame and a fat stack of cash. They’re ending the plague of corporate greed and providing the survivors of the apocalypse with retribution. These are the new heroes. This is the age of the BOUNTY KILLER.
- **跳转**: https://themoviecosmos.com/movie/209504
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p3 · fit=0.42: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.4836 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### Gabbar Is Back (2015) [THE-SAGE]
- **tmdb_id**: 337876
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4742
- **genres** / **language**: Drama, Action / hi
- **overview**: A vigilante network taking out corrupt officials draws the notice of the authorities.
- **跳转**: https://themoviecosmos.com/movie/337876
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-SAGE/p2 · fit=0.78: fragments=[why-0, how-1, how-2, result-0, result-1] · sim=0.4742 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### The Desired War (2022) [THE-LOVER]
- **tmdb_id**: 852756
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5250
- **genres** / **language**: War, Comedy, Romance / it
- **overview**: A diplomatic incident threatens to break out a war inside Europe that only an unlikely couple of bickering lovers seems able to stop.
- **跳转**: https://themoviecosmos.com/movie/852756
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p2 · fit=0.38: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.5250 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

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

**Count:** 5 candidate(s)

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 54 -->
### Transpecos (2016) [A1, THE-INNOCENT, THE-EVERYMAN, THE-EXPLORER, THE-CREATOR, THE-SAGE] [优质·多agent]
- **tmdb_id**: 381018
- **优质候选**: true
- **distinct_agents**: 6
- **相似度**: 0.5419
- **genres** / **language**: Thriller / en
- **overview**: For three US Border Patrol agents, the contents of one car reveal an insidious plot within their own ranks. The next 24 hours may cost them their lives.
- **跳转**: https://themoviecosmos.com/movie/381018
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1] · sim=0.5087 · **命中分=2**
  - THE-INNOCENT/p1 · fit=0.65: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5391 · **命中分=6**
  - THE-EVERYMAN/p1 · fit=0.85: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.5165 · **命中分=5**
  - THE-EXPLORER/p1 · fit=0.85: fragments=[why-0, how-0, how-1, how-2, how-3] · sim=0.4900 · **命中分=5**
  - THE-CREATOR/p1 · fit=0.75: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0, result-2] · sim=0.5117 · **命中分=8**
  - THE-SAGE/p1 · fit=0.90: fragments=[how-0, how-1, how-2, how-3] · sim=0.5211 · **命中分=4**
  - THE-INNOCENT/p2 · fit=0.70: fragments=[how-0, how-1, how-2, how-3, how-4, result-0, result-1, result-2] · sim=0.5419 · **命中分=8**
  - THE-EVERYMAN/p2 · fit=0.78: fragments=[how-0, how-1, how-2, how-3, how-4, result-1, result-2] · sim=0.5404 · **命中分=7**
  - THE-EXPLORER/p2 · fit=0.78: fragments=[how-4, result-0, result-1] · sim=0.5072 · **命中分=3**
  - THE-EVERYMAN/p3 · fit=0.80: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.4996 · **命中分=6**
- **pseudo命中分合计**: 54
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 38 -->
### Trade (2007) [A1, THE-INNOCENT, THE-EVERYMAN, THE-SAGE] [优质·多agent]
- **tmdb_id**: 4170
- **优质候选**: true
- **distinct_agents**: 4
- **相似度**: 0.5398
- **genres** / **language**: Thriller / en
- **overview**: A Texas cop, whose own daughter might have been forced into sexual slavery, joins forces with a Mexican youth to find the boy's sister, who was abducted and forced into prostitution. Meanwhile, a Polish woman who was promised a better life in America also becomes a victim.
- **跳转**: https://themoviecosmos.com/movie/4170
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1] · sim=0.5097 · **命中分=2**
  - THE-INNOCENT/p1 · fit=0.65: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5031 · **命中分=6**
  - THE-EVERYMAN/p1 · fit=0.85: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.5398 · **命中分=5**
  - THE-SAGE/p1 · fit=0.90: fragments=[how-0, how-1, how-2, how-3] · sim=0.5087 · **命中分=4**
  - THE-INNOCENT/p2 · fit=0.70: fragments=[how-0, how-1, how-2, how-3, how-4, result-0, result-1, result-2] · sim=0.4458 · **命中分=8**
  - THE-EVERYMAN/p2 · fit=0.78: fragments=[how-0, how-1, how-2, how-3, how-4, result-1, result-2] · sim=0.4870 · **命中分=7**
  - THE-EVERYMAN/p3 · fit=0.80: fragments=[how-0, how-1, how-2, how-3, how-4, result-0] · sim=0.4986 · **命中分=6**
- **pseudo命中分合计**: 38
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 很难评价关联性，且话题敏感。现在看来是一个wobbly 2

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 13 -->
### Punishment Park (1971) [THE-CREATOR, THE-OUTLAW] [优质·多agent]
- **tmdb_id**: 26513
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5853
- **genres** / **language**: Drama, Thriller / en
- **overview**: In this fictional documentary, U.S. prisons are at capacity, and President Nixon declares a state of emergency. All new prisoners, most of whom are connected to the antiwar movement, are now given the choice of jail time or spending three days in Punishment Park, where they will be hunted for sport by federal authorities. The prisoners invariably choose the latter option, but learn that, between the desert heat and the brutal police officers, their chances of survival are slim.
- **跳转**: https://themoviecosmos.com/movie/26513
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p2 · fit=0.68: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5373 · **命中分=6**
  - THE-OUTLAW/p3 · fit=0.80: fragments=[how-0, how-1, how-2, how-3, how-4, result-0, result-2] · sim=0.5853 · **命中分=7**
- **pseudo命中分合计**: 13
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 原新闻可能移民/边境的概念更重，不过这个overview中的监狱/警察概念也算相关

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 11 -->
### Colosio (2012) [THE-CREATOR, THE-EXPLORER] [优质·多agent]
- **tmdb_id**: 151708
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5161
- **genres** / **language**: Crime, Drama, Thriller / es
- **overview**: It's 1994 in Mexico, the nation was witnessing a turbulent year since its beginnings. An indigenous rebellion shakes the country. Three months later, the ruling party's presidential candidate is brutally murdered during a rally in Tijuana. The country is concerned. Nobody knows who's behind this event, it all points to a conspiracy. Andrés Vázquez, an intelligence expert, is commissioned to lead a secret investigation parallel to the official government issued one. But another expert agent, el Seco, has received orders to wipe out all witnesses and get rid of the evidence surrounding the candidate's murder. As Andrés begins putting the pieces of this intricate puzzle together and comes closer to the truth, he realizes he's also putting his life and that of his loved ones in peril.
- **跳转**: https://themoviecosmos.com/movie/151708
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p1 · fit=0.75: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0, result-2] · sim=0.5161 · **命中分=8**
  - THE-EXPLORER/p2 · fit=0.78: fragments=[how-4, result-0, result-1] · sim=0.4784 · **命中分=3**
- **pseudo命中分合计**: 11
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 只和墨西哥相关了

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 10 -->
### Union Pacific (1939) [A1, THE-JESTER] [优质·多agent]
- **tmdb_id**: 43837
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5910
- **genres** / **language**: Drama, Western / en
- **overview**: One of the last bills signed by President Lincoln authorizes pushing the Union Pacific Railroad across the wilderness to California. But financial opportunist Asa Barrows hopes to profit from obstructing it. Chief troubleshooter Jeff Butler has his hands full fighting Barrows' agent, gambler Sid Campeau; Campeau's partner Dick Allen is Jeff's war buddy and rival suitor for engineer's daughter Molly Monahan. Who will survive the effort to push the railroad through at any cost?
- **跳转**: https://themoviecosmos.com/movie/43837
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p3: fragments=[how-4, result-2] · sim=0.5910 · **命中分=2**
  - THE-JESTER/p1 · fit=0.88: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, result-0, result-2] · sim=0.4598 · **命中分=8**
- **pseudo命中分合计**: 10
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

### 单 agent 命中

**Count:** 9 candidate(s)

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 8 -->
### Ghost in the Shell: S.A.C. 2nd GIG - Individual Eleven (2006) [THE-OUTLAW]
- **tmdb_id**: 111224
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5705
- **genres** / **language**: Animation, Science Fiction / ja
- **overview**: The year is 2030, and an influx of refuges have effortlessly transformed themselves into a terrorist organization known as the "Individual Eleven." With a sadistic intent of mass destruction, will they triumph in victory or discover the gloomy pitfalls of defeat?
- **跳转**: https://themoviecosmos.com/movie/111224
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p1 · fit=0.90: fragments=[how-0, how-1, how-2, how-3, how-4, result-0, result-1, result-2] · sim=0.5705 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 8 -->
### Transport de la cloche de l'indépendance (1896) [THE-JESTER]
- **tmdb_id**: 231035
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5022
- **genres** / **language**: Documentary / en
- **overview**: The parade occupies only a small portion of the screen, the crowds are a seething mass that do really move and the Independence Bell is nowhere to be seen.
- **跳转**: https://themoviecosmos.com/movie/231035
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p2 · fit=0.82: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.5022 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 8 -->
### A Dragon Arrives! (2016) [THE-OUTLAW]
- **tmdb_id**: 377150
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5825
- **genres** / **language**: Drama, Mystery, Horror / fa
- **overview**: On Jan. 22, 1965, the day before the Iranian prime minister is assassinated, a car drives up to a shipwreck. Inside the wreck, a banished political prisoner has hung himself and the walls are covered in diary entries, literary quotes, and strange symbols. Fifty years later, the evidence, including intelligence tape recordings, is found in a box. The contents attest to the fact that the inspector and his colleagues were arrested, but why?
- **跳转**: https://themoviecosmos.com/movie/377150
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p1 · fit=0.90: fragments=[how-0, how-1, how-2, how-3, how-4, result-0, result-1, result-2] · sim=0.5825 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 7 -->
### Crossing Over (2009) [THE-JESTER]
- **tmdb_id**: 15577
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4868
- **genres** / **language**: Crime, Drama / en
- **overview**: Immigrants from around the world enter Los Angeles every day, with hopeful visions of a better life, but little notion of what that life may cost. Their desperate scenarios test the humanity of immigration enforcement officers. In Crossing Over, writer-director Wayne Kramer explores the allure of the American dream, and the reality that immigrants find – and create -- in 21st century L.A.
- **跳转**: https://themoviecosmos.com/movie/15577
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p3 · fit=0.75: fragments=[how-0, how-1, how-2, how-3, how-4, result-0, result-2] · sim=0.4868 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 其实和原新闻共鸣非常强

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 7 -->
### The Purge (2013) [THE-OUTLAW]
- **tmdb_id**: 158015
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5143
- **genres** / **language**: Science Fiction, Horror, Thriller / en
- **overview**: Given the country's overcrowded prisons, the U.S. government begins to allow 12-hour periods of time in which all illegal activity is legal. During one of these free-for-alls, a family must protect themselves from a home invasion.
- **跳转**: https://themoviecosmos.com/movie/158015
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p2 · fit=0.85: fragments=[how-0, how-1, how-2, how-3, how-4, result-0, result-1] · sim=0.5143 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 电影overview和新闻主题偏离较多，但是也可能有某些共鸣，无法判断

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 7 -->
### C’era una volta il crimine (2022) [THE-OUTLAW]
- **tmdb_id**: 790529
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5201
- **genres** / **language**: Comedy / it
- **overview**: C’era una volta il crimine
- **跳转**: https://themoviecosmos.com/movie/790529
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p2 · fit=0.85: fragments=[how-0, how-1, how-2, how-3, how-4, result-0, result-1] · sim=0.5201 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 这种因为overview缺失所以用标题填补的是要直接抛弃的

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 7 -->
### Attica (2021) [THE-OUTLAW]
- **tmdb_id**: 858059
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5638
- **genres** / **language**: Documentary / en
- **overview**: Follows the largest prison uprising in US history, conducting dozens of new interviews with inmates, journalists, and other witnesses.
- **跳转**: https://themoviecosmos.com/movie/858059
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p3 · fit=0.80: fragments=[how-0, how-1, how-2, how-3, how-4, result-0, result-2] · sim=0.5638 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 结构  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 为什么会匹配到这么多关于监狱概念的电影？

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 6 -->
### The First Purge (2018) [THE-CREATOR]
- **tmdb_id**: 442249
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5980
- **genres** / **language**: Action, Horror, Thriller / en
- **overview**: To push the crime rate below one percent for the rest of the year, the New Founding Fathers of America test a sociological theory that vents aggression for one night in one isolated community. But when the violence of oppressors meets the rage of the others, the contagion will explode from the trial-city borders and spread across the nation.
- **跳转**: https://themoviecosmos.com/movie/442249
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p2 · fit=0.68: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5980 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 移民和边境控制与overview中的压迫和被压迫者之间的愤怒能产生联系

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 5 -->
### Alma & the Wolf (2025) [THE-MAGICIAN]
- **tmdb_id**: 1328956
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4884
- **genres** / **language**: Horror, Mystery, Thriller / en
- **overview**: After a violent animal attack, paranoia spreads through Spiral Creek. But when Deputy Ren Accord gets too close, his son vanishes, and reality begins to fracture.
- **跳转**: https://themoviecosmos.com/movie/1328956
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p2 · fit=0.78: fragments=[how-0, how-1, result-0, result-1, result-2] · sim=0.4884 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

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

**Count:** 8 candidate(s)

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 60 -->
### Hurricane Season (2010) [A1, THE-INNOCENT, THE-EVERYMAN, THE-OUTLAW, THE-LOVER, THE-MAGICIAN, THE-SAGE, THE-HERO, THE-EXPLORER] [优质·多agent]
- **tmdb_id**: 32007
- **优质候选**: true
- **distinct_agents**: 9
- **相似度**: 0.6056
- **genres** / **language**: Drama / en
- **overview**: Based on true events amid the wreckage and chaos dealt by Hurricane Katrina; one basketball coach in Marrero, Louisiana just will not give up. Coach Al Collins, gathers other players from hard-hit schools and builds a team actually worthy enough to go to the state playoffs.
- **跳转**: https://themoviecosmos.com/movie/32007
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p2: fragments=[why-0, how-2, how-3] · sim=0.4197 · **命中分=3**
  - THE-INNOCENT/p1 · fit=0.88: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.6056 · **命中分=7**
  - THE-EVERYMAN/p1 · fit=0.75: fragments=[why-0, how-0, how-1, how-2, how-3, result-1] · sim=0.5303 · **命中分=6**
  - THE-OUTLAW/p1 · fit=0.88: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5434 · **命中分=7**
  - THE-LOVER/p1 · fit=0.85: fragments=[how-0, how-1, why-0, how-2, how-3, result-0] · sim=0.5844 · **命中分=6**
  - THE-MAGICIAN/p1 · fit=0.85: fragments=[why-0, how-0, how-1, how-2, how-3, result-0] · sim=0.5388 · **命中分=6**
  - THE-SAGE/p1 · fit=0.78: fragments=[how-0, how-1, why-0, how-2, how-3, result-0] · sim=0.5185 · **命中分=6**
  - THE-HERO/p2 · fit=0.75: fragments=[why-0, result-1] · sim=0.5193 · **命中分=2**
  - THE-EXPLORER/p2 · fit=0.68: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4845 · **命中分=7**
  - THE-LOVER/p2 · fit=0.78: fragments=[result-1, why-0, how-0, how-1, how-2, how-3] · sim=0.5220 · **命中分=6**
  - THE-MAGICIAN/p2 · fit=0.78: fragments=[why-0, how-2, how-3, result-1] · sim=0.5232 · **命中分=4**
- **pseudo命中分合计**: 60
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 20 -->
### One Piece: Dream Soccer King! (2002) [THE-JESTER, THE-EVERYMAN, THE-SAGE] [优质·多agent]
- **tmdb_id**: 464198
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.6031
- **genres** / **language**: Fantasy, Comedy, Animation / ja
- **overview**: At a huge pillar stadium, the Grand Line Cup Final is being held. The "Straw Hat Pirate Team"(Luffy, Zoro, Usopp, Sanji, and Chopper) are having a tie breaker shoot out against the "Villian All Star Team"(Buggy, Bon Clay, Jango, Hatchan, and a soccer like head player named Odacchi). Everyone of them gets a turn in kicking the ball to the goal. While Coby is taking the goalie position, and isn't doing too good in blocking the goal. One after another, the game eventually comes to a sudden death match. Which team will win the Grand Line Cup?
- **跳转**: https://themoviecosmos.com/movie/464198
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1 · fit=0.85: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5032 · **命中分=7**
  - THE-EVERYMAN/p2 · fit=0.85: fragments=[how-2, how-3, result-0] · sim=0.6031 · **命中分=3**
  - THE-SAGE/p2 · fit=0.85: fragments=[why-0, how-2, result-1, result-0] · sim=0.4802 · **命中分=4**
  - THE-JESTER/p3 · fit=0.72: fragments=[why-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4835 · **命中分=6**
- **pseudo命中分合计**: 20
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 17 -->
### Hoosiers (1986) [A1, THE-SAGE] [优质·多agent]
- **tmdb_id**: 5693
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5365
- **genres** / **language**: Drama, Family / en
- **overview**: Failed college coach Norman Dale gets a chance at redemption when he is hired to coach a high school basketball team in a tiny Indiana town. After a teacher persuades star player Jimmy Chitwood to quit and focus on his long-neglected studies, Dale struggles to develop a winning team in the face of community criticism for his temper and his unconventional choice of assistant coach: Shooter, a notorious alcoholic.
- **跳转**: https://themoviecosmos.com/movie/5693
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4978 · **命中分=6**
  - A1/p3: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.4861 · **命中分=5**
  - THE-SAGE/p1 · fit=0.78: fragments=[how-0, how-1, why-0, how-2, how-3, result-0] · sim=0.5365 · **命中分=6**
- **pseudo命中分合计**: 17
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 17 -->
### Hockey Homicide (1945) [A1, THE-JESTER] [优质·多agent]
- **tmdb_id**: 66876
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5831
- **genres** / **language**: Animation, Comedy / en
- **overview**: A crowd gathers at the skating rink to watch the big championship hockey game of the Pelicans versus the Aardvarks. Although referee "Clean Game" Kinney does his best to supervise, the hockey game really gets out of hand eventually. Two star players, Bertino and Ferguson, are so anxious, they never get let out of the penalty box, referee Kinney is never able to drop the puck without being physically hurt somehow, and the spectators themselves are so worked into the game, they take out their aggression on the ice while the players relax in the bleachers.
- **跳转**: https://themoviecosmos.com/movie/66876
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5622 · **命中分=6**
  - A1/p3: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.5831 · **命中分=5**
  - THE-JESTER/p3 · fit=0.72: fragments=[why-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4983 · **命中分=6**
- **pseudo命中分合计**: 17
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 14 -->
### Step Up All In (2014) [THE-HERO, THE-EXPLORER] [优质·多agent]
- **tmdb_id**: 243683
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5896
- **genres** / **language**: Romance, Drama, Music / en
- **overview**: All-stars from previous installments convene in glittering Las Vegas, battling for a victory that could define their dreams and their careers.
- **跳转**: https://themoviecosmos.com/movie/243683
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1 · fit=0.88: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.5896 · **命中分=5**
  - THE-EXPLORER/p1 · fit=0.75: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5723 · **命中分=6**
  - THE-HERO/p3 · fit=0.82: fragments=[how-2, how-3, result-0] · sim=0.5502 · **命中分=3**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 14 -->
### Three Seconds (2017) [THE-JESTER, THE-EVERYMAN, THE-SAGE] [优质·多agent]
- **tmdb_id**: 444218
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.5766
- **genres** / **language**: Drama / ru
- **overview**: The story is set at the 1972 Munich Olympics where the U.S. team lost the basketball championship for the first time in 36 years. The final moments of the final game have become one of the most controversial events in Olympic history. With play tied, the score table horn sounded during a second free throw attempt that put the U.S. ahead by one. But the Soviets claimed they had called for a time out before the basket and confusion ensued. The clock was set back by three seconds twice in a row and the Russians finally prevailed at the very last. The U.S. protested, but a jury decided in the USSR’s favor and Team USA voted unanimously to refuse its silver medals. The Soviet players have been treated as heroes at home.
- **跳转**: https://themoviecosmos.com/movie/444218
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1 · fit=0.85: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4837 · **命中分=7**
  - THE-EVERYMAN/p2 · fit=0.85: fragments=[how-2, how-3, result-0] · sim=0.5766 · **命中分=3**
  - THE-SAGE/p2 · fit=0.85: fragments=[why-0, how-2, result-1, result-0] · sim=0.5406 · **命中分=4**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 13 -->
### By the Law (1926) [THE-OUTLAW, THE-HERO, THE-MAGICIAN] [优质·多agent]
- **tmdb_id**: 126644
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.5437
- **genres** / **language**: Drama, Western, Mystery, Action / ru
- **overview**: After a man kills two members of his Yukon gold prospecting team, the other two surviving members struggle to keep him subdued for the next several months until they can turn him over to the law. Based on Jack London's 'The Unexpected' (1905).
- **跳转**: https://themoviecosmos.com/movie/126644
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p1 · fit=0.88: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5107 · **命中分=7**
  - THE-HERO/p2 · fit=0.75: fragments=[why-0, result-1] · sim=0.5323 · **命中分=2**
  - THE-MAGICIAN/p2 · fit=0.78: fragments=[why-0, how-2, how-3, result-1] · sim=0.5437 · **命中分=4**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 13 -->
### Ray Donovan: The Movie (2022) [THE-EXPLORER, THE-LOVER] [优质·多agent]
- **tmdb_id**: 800425
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5214
- **genres** / **language**: Crime, Drama, TV Movie / en
- **overview**: A showdown decades in the making brings the Donovan family legacy full circle. As the events that made Ray who he is today finally come to light, the Donovans find themselves drawn back to Boston to face the past. Each of them struggles to overcome their violent upbringing, but destiny dies hard, and only their fierce love for each other keeps them in the fight.
- **跳转**: https://themoviecosmos.com/movie/800425
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p2 · fit=0.68: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4918 · **命中分=7**
  - THE-LOVER/p2 · fit=0.78: fragments=[result-1, why-0, how-0, how-1, how-2, how-3] · sim=0.5214 · **命中分=6**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

### 单 agent 命中

**Count:** 10 candidate(s)

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 7 -->
### Crows Zero II (2009) [THE-OUTLAW]
- **tmdb_id**: 25716
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5082
- **genres** / **language**: Action, Adventure, Crime, Comedy / ja
- **overview**: Genji and his victorious G.P.S. alliance find themselves facing down a new challenge by the students of Hosen Academy, feared by everyone as 'The Army of Killers.' The two schools, in fact, have a history of bad blood between them. And the simmering embers of hatred are about to flare up again, burning away any last remnants of the truce they had so rigorously observed until now.
- **跳转**: https://themoviecosmos.com/movie/25716
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p3 · fit=0.82: fragments=[how-0, how-1, why-0, how-2, how-3, result-0, result-1] · sim=0.5082 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 7 -->
### Tekken (2010) [THE-OUTLAW]
- **tmdb_id**: 42194
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5178
- **genres** / **language**: Crime, Drama, Action, Thriller, Science Fiction / en
- **overview**: In the year of 2039, after World Wars destroy much of the civilization as we know it, territories are no longer run by governments, but by corporations; the mightiest of which is the Mishima Zaibatsu. In order to placate the seething masses of this dystopia, Mishima sponsors Tekken, a tournament in which fighters battle until only one is left standing.
- **跳转**: https://themoviecosmos.com/movie/42194
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p3 · fit=0.82: fragments=[how-0, how-1, why-0, how-2, how-3, result-0, result-1] · sim=0.5178 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 7 -->
### Eddie the Eagle (2016) [THE-INNOCENT]
- **tmdb_id**: 319888
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5584
- **genres** / **language**: Comedy, Drama, History, Adventure / en
- **overview**: The feel-good story of Michael 'Eddie' Edwards, an unlikely but courageous British ski-jumper who never stopped believing in himself—even as an entire nation was counting him out. With the help of a rebellious and charismatic coach, Eddie takes on the establishment and wins the hearts of sports fans around the world by making an improbable and historic showing at the 1988 Calgary Winter Olympics.
- **跳转**: https://themoviecosmos.com/movie/319888
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1 · fit=0.88: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5584 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### 3000 Miles to Graceland (2001) [THE-JESTER]
- **tmdb_id**: 12138
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5541
- **genres** / **language**: Action, Adventure, Comedy, Crime, Thriller / en
- **overview**: It was an ingenious enough plan: rob the Riviera Casino's count room during an Elvis impersonator convention. But Thomas Murphy decided to keep all the money for himself and shot all his partners, including recently-freed ex-con Michael Zane. With $3.2 million at stake, the Marshals Service closing in, Michael must track down Murphy.
- **跳转**: https://themoviecosmos.com/movie/12138
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p2 · fit=0.78: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5541 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### The Mad Magician (1954) [THE-JESTER]
- **tmdb_id**: 28363
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5529
- **genres** / **language**: Thriller, Crime, Mystery, Horror / en
- **overview**: Don Gallico is an inventor of stage magic effects who aspires to become a star in his own right. Just before his first performance his act is shut down by capricious manager Ross Ormond who wants Gallico's brilliant buzz saw effect for the act of The Great Rinaldi, an established star. With this defeat, and the humiliation of having already lost his wife Claire to Ormond, Gallico decides it is time to take matters into his own hands.
- **跳转**: https://themoviecosmos.com/movie/28363
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p2 · fit=0.78: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5529 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### 4 Crazy Draftees at the Army (1974) [THE-OUTLAW]
- **tmdb_id**: 61301
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5571
- **genres** / **language**: Comedy / it
- **overview**: Our four incompetent types thrown into the field whether they liked it or not....They preferred to run the other way, but can never get there act together! How will they win the war' How can they get out of this mess'
- **跳转**: https://themoviecosmos.com/movie/61301
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p2 · fit=0.75: fragments=[why-0, how-0, how-1, how-2, how-3, result-0] · sim=0.5571 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### They Came to Rob Las Vegas (1968) [THE-EXPLORER]
- **tmdb_id**: 124807
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5320
- **genres** / **language**: Drama, Crime / es
- **overview**: After successfully assaulting an armored car between Las Vegas and Los Angeles, the ambitions of the diverse members of the intrepid criminal gang collide, causing undesirable consequences.
- **跳转**: https://themoviecosmos.com/movie/124807
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p1 · fit=0.75: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5320 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### Magic Mike XXL (2015) [THE-MAGICIAN]
- **tmdb_id**: 264999
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5189
- **genres** / **language**: Comedy, Drama / en
- **overview**: Three years after Mike bowed out of the stripper life at the top of his game, he and the remaining Kings of Tampa hit the road to Myrtle Beach to put on one last blow-out performance.
- **跳转**: https://themoviecosmos.com/movie/264999
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-MAGICIAN/p1 · fit=0.85: fragments=[why-0, how-0, how-1, how-2, how-3, result-0] · sim=0.5189 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### This Magic Moment (2016) [THE-LOVER]
- **tmdb_id**: 377460
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5430
- **genres** / **language**: Documentary / en
- **overview**: In the mid-1990s, Orlando was the center of excitement in the NBA. The young franchise, led by mega-stars Shaquille O'Neal and Penny Hardaway, beat the mighty Bulls en route to the 1995 NBA Finals. While it was clear Orlando was a dynasty in the making, the Magic's moment on top was never fully realized.
- **跳转**: https://themoviecosmos.com/movie/377460
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1 · fit=0.85: fragments=[how-0, how-1, why-0, how-2, how-3, result-0] · sim=0.5430 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### Heart of Champions (2021) [THE-OUTLAW]
- **tmdb_id**: 647581
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5308
- **genres** / **language**: Drama / en
- **overview**: During their last year at an Ivy League college in 1999, a group of friends and crew teammates' lives are changed forever when an army vet takes over as coach of their dysfunctional rowing team.
- **跳转**: https://themoviecosmos.com/movie/647581
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-OUTLAW/p2 · fit=0.75: fragments=[why-0, how-0, how-1, how-2, how-3, result-0] · sim=0.5308 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

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

**Count:** 5 candidate(s)

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 16 -->
### L'Odissea (1911) [A1, THE-HERO, THE-SAGE] [优质·多agent]
- **tmdb_id**: 194224
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.7279
- **genres** / **language**: Drama, Adventure / it
- **overview**: Film adaptation of Homer's 'The Odyssey.'
- **跳转**: https://themoviecosmos.com/movie/194224
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, why-0, why-1] · sim=0.6236 · **命中分=5**
  - THE-HERO/p1 · fit=0.88: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.5725 · **命中分=6**
  - THE-SAGE/p1 · fit=0.78: fragments=[how-0, how-1, why-0, why-1, result-0] · sim=0.7279 · **命中分=5**
- **pseudo命中分合计**: 16
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 13 -->
### Venus in Fur (2013) [A1, THE-EVERYMAN] [优质·多agent]
- **tmdb_id**: 197082
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.6666
- **genres** / **language**: Drama / fr
- **overview**: An enigmatic actress may have a hidden agenda when she auditions for a part in a misogynistic writer's play.
- **跳转**: https://themoviecosmos.com/movie/197082
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p2: fragments=[how-1, how-2, why-0, why-1] · sim=0.6666 · **命中分=4**
  - A1/p3: fragments=[how-0, how-1, result-0] · sim=0.5997 · **命中分=3**
  - THE-EVERYMAN/p1 · fit=0.65: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.5540 · **命中分=6**
- **pseudo命中分合计**: 13
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 12 -->
### Sweet Dreams (1981) [THE-HERO, THE-SAGE] [优质·多agent]
- **tmdb_id**: 57967
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.6002
- **genres** / **language**: Comedy, Drama / it
- **overview**: Michele criticizes the film industry and its inhabitants, and is particularly embattled with a Neapolitan director making a musical about the 1968 student demonstrations. At the same time, Michele has a creative block and struggles to finish his film titled "Freud’s Mother." Nanni Moretti’s self-inquiry into filmmaking, political ennui, and men’s relations with their mothers.
- **跳转**: https://themoviecosmos.com/movie/57967
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p2 · fit=0.75: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.6002 · **命中分=6**
  - THE-SAGE/p3 · fit=0.65: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.5790 · **命中分=6**
- **pseudo命中分合计**: 12
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 现有overview很难判断，感觉有2的潜力，wobbly 2

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 12 -->
### X-Rated: The Greatest Adult Movies of All Time (2015) [THE-EVERYMAN, THE-EXPLORER] [优质·多agent]
- **tmdb_id**: 324558
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5636
- **genres** / **language**: Documentary / en
- **overview**: The evolution of adult cinema through the most influential films in history, a journey that begins in the 1970s and ends nowadays. An in-depth analysis of the success of the most prestigious erotic films, their impact on industry and society, and their influence on cinema and contemporary culture.
- **跳转**: https://themoviecosmos.com/movie/324558
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p1 · fit=0.65: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.5636 · **命中分=6**
  - THE-EXPLORER/p2 · fit=0.75: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.5551 · **命中分=6**
- **pseudo命中分合计**: 12
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 10 -->
### Don't Leave Home (2018) [THE-LOVER, THE-SAGE] [优质·多agent]
- **tmdb_id**: 502167
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5980
- **genres** / **language**: Thriller, Mystery / en
- **overview**: An American artist's obsession with a disturbing urban legend leads her to an investigation of the story's origins at the crumbling estate of a reclusive painter in Ireland.
- **跳转**: https://themoviecosmos.com/movie/502167
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1 · fit=0.78: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5980 · **命中分=5**
  - THE-SAGE/p1 · fit=0.78: fragments=[how-0, how-1, why-0, why-1, result-0] · sim=0.5790 · **命中分=5**
- **pseudo命中分合计**: 10
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

### 单 agent 命中

**Count:** 7 candidate(s)

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### Apolonia, Apolonia (2023) [THE-HERO]
- **tmdb_id**: 1047128
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6070
- **genres** / **language**: Documentary / da
- **overview**: When Danish filmmaker Lea Glob first portrayed Apolonia Sokol in 2009, she appeared to be leading a storybook life. The talented Apolonia was born in an underground theater in Paris and grew up in an artists’ community—the ultimate bohemian existence. In her 20s, she studied at the Beaux-Arts de Paris, one of the most prestigious art academies in Europe. Over the years, Lea Glob kept returning to film the charismatic Apolonia and a special bond developed between the two young women.
- **跳转**: https://themoviecosmos.com/movie/1047128
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p1 · fit=0.88: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.6070 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 与新闻中“选角”概念相关，可以是一个high 1 但是达不到low2

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### Kaantha (2025) [THE-HERO]
- **tmdb_id**: 1250508
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6045
- **genres** / **language**: History, Crime, Drama / ta
- **overview**: Set in the backdrop of a film set, in the 1950’s in post colonial Madras, the film is centred around the professional rivalry between a film-maker trying to make his seminal film and the top reigning actor who the director once introduced. The rivalry spirals around the leading actress, a debutante and as the relationship between the three.
- **跳转**: https://themoviecosmos.com/movie/1250508
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p2 · fit=0.75: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.6045 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 导演与选角、演员之间的故事挺贴的，high 1

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Holiday for Henrietta (1952) [THE-INNOCENT]
- **tmdb_id**: 4709
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6228
- **genres** / **language**: Comedy / fr
- **overview**: Two scriptwriters argue about the fate of Henrietta, a charming and gamine shopgirl. One favors a comical path for their heroine, who is overcome with sentimental love for a young photographer on Bastille Day. The other has a more thrilling and dastardly fate in mind for her. Among the film's irresistible conceits is Hildegarde Neff as an oversexed circus bareback rider.
- **跳转**: https://themoviecosmos.com/movie/4709
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1 · fit=0.45: fragments=[how-0, how-1, how-2, why-0, result-0] · sim=0.6228 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 导演与选角、演员之间的故事挺贴的，high 1

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### The Mad Magician (1954) [THE-JESTER]
- **tmdb_id**: 28363
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6091
- **genres** / **language**: Thriller, Crime, Mystery, Horror / en
- **overview**: Don Gallico is an inventor of stage magic effects who aspires to become a star in his own right. Just before his first performance his act is shut down by capricious manager Ross Ormond who wants Gallico's brilliant buzz saw effect for the act of The Great Rinaldi, an established star. With this defeat, and the humiliation of having already lost his wife Claire to Ormond, Gallico decides it is time to take matters into his own hands.
- **跳转**: https://themoviecosmos.com/movie/28363
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1 · fit=0.85: fragments=[how-0, how-1, why-0, how-2, result-0] · sim=0.6091 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: low 1

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Three Cases of Murder (1955) [THE-INNOCENT]
- **tmdb_id**: 45577
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6042
- **genres** / **language**: Mystery, Horror / en
- **overview**: An atmospheric British omnibus film presenting three tales of murder and the supernatural. In “In the Picture,” a museum attendant is drawn into the eerie world within a painting. In “You Killed Elizabeth,” two lifelong friends become suspects when the woman they both love is murdered. In “Lord Mountdrago,” a disgraced politician seeks revenge on a powerful statesman by exploiting his dreams. Linked by a recurring figure, the film blends psychological horror, mystery, and fantasy across its three interconnected stories.
- **跳转**: https://themoviecosmos.com/movie/45577
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p1 · fit=0.45: fragments=[how-0, how-1, how-2, why-0, result-0] · sim=0.6042 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### The Firefall (1904) [THE-JESTER]
- **tmdb_id**: 190725
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6009
- **genres** / **language**: Fantasy / fr
- **overview**: A magic show.
- **跳转**: https://themoviecosmos.com/movie/190725
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1 · fit=0.85: fragments=[how-0, how-1, why-0, how-2, result-0] · sim=0.6009 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: overview过短 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Enoch Arden (1911) [THE-LOVER]
- **tmdb_id**: 483341
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5981
- **genres** / **language**: Drama / en
- **overview**: Moving Picture World described the film: "There is a small need to describe this subject as the poem of Lord Tennyson is so well known, so suffice it to say that this Biograph subject is an unusually faithful portrayal of that beautiful romance of Enoch Arden, Annie Lee and Philip Ray, taken in scenes of rare beauty". This is the combined feature version of Enoch Arden Parts I and II.
- **跳转**: https://themoviecosmos.com/movie/483341
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p1 · fit=0.78: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5981 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

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

**Count:** 7 candidate(s)

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 26 -->
### The Killing Room (2009) [A1, THE-EVERYMAN, THE-CREATOR] [优质·多agent]
- **tmdb_id**: 20777
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.4765
- **genres** / **language**: Thriller, Drama / en
- **overview**: Four volunteers sign up for what initially appears to be a typical paid research study, only to discover that they've unwittingly become involved with a classified government program that was said to have been terminated nearly two decades ago.
- **跳转**: https://themoviecosmos.com/movie/20777
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-3] · sim=0.4028 · **命中分=9**
  - A1/p2: fragments=[why-0, how-1, how-2] · sim=0.4645 · **命中分=3**
  - A1/p3: fragments=[how-3, result-0, result-2, result-3] · sim=0.4088 · **命中分=4**
  - THE-EVERYMAN/p1 · fit=0.85: fragments=[why-0, how-1, result-0, result-1, result-2, result-3] · sim=0.4630 · **命中分=6**
  - THE-CREATOR/p1 · fit=0.85: fragments=[why-0, how-1, result-0, result-1] · sim=0.4765 · **命中分=4**
- **pseudo命中分合计**: 26
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 25 -->
### Black Dossier (1955) [THE-JESTER, THE-INNOCENT, THE-HERO] [优质·多agent]
- **tmdb_id**: 199252
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.5193
- **genres** / **language**: Crime, Drama / fr
- **overview**: In the 1950s, in a small provincial town, a young inexperienced judge clashes with an influential notable during an investigation into a suspicious death. His perseverance to get to the truth will cause a huge scandal.
- **跳转**: https://themoviecosmos.com/movie/199252
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-JESTER/p1 · fit=0.88: fragments=[how-1, how-2, how-3, result-0] · sim=0.5193 · **命中分=4**
  - THE-INNOCENT/p2 · fit=0.85: fragments=[why-0, how-2, how-3, result-0, how-4] · sim=0.4984 · **命中分=5**
  - THE-HERO/p2 · fit=0.85: fragments=[why-0, how-2, how-3, result-0, result-3] · sim=0.4870 · **命中分=5**
  - THE-JESTER/p2 · fit=0.85: fragments=[why-0, how-1, how-2, how-3, result-0, result-3] · sim=0.5143 · **命中分=6**
  - THE-HERO/p3 · fit=0.80: fragments=[how-1, how-2, how-3, result-0, how-4] · sim=0.4872 · **命中分=5**
- **pseudo命中分合计**: 25
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 19 -->
### Test (2006) [THE-CREATOR, THE-EVERYMAN, THE-HERO] [优质·多agent]
- **tmdb_id**: 887697
- **优质候选**: true
- **distinct_agents**: 3
- **相似度**: 0.5141
- **genres** / **language**: Animation, Drama / cs
- **overview**: Test
- **跳转**: https://themoviecosmos.com/movie/887697
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p1 · fit=0.85: fragments=[why-0, how-1, result-0, result-1] · sim=0.5141 · **命中分=4**
  - THE-EVERYMAN/p2 · fit=0.72: fragments=[how-1, how-2, result-0, result-2, result-3] · sim=0.4704 · **命中分=5**
  - THE-HERO/p3 · fit=0.80: fragments=[how-1, how-2, how-3, result-0, how-4] · sim=0.4923 · **命中分=5**
  - THE-CREATOR/p3 · fit=0.78: fragments=[result-0, result-1, result-2, how-4, result-3] · sim=0.4735 · **命中分=5**
- **pseudo命中分合计**: 19
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 14 -->
### CNCO: los últimos cinco días (2022) [A1, THE-EXPLORER] [优质·多agent]
- **tmdb_id**: 1030206
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5151
- **genres** / **language**: Music, Documentary / es
- **overview**: CNCO: los últimos cinco días
- **跳转**: https://themoviecosmos.com/movie/1030206
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-3] · sim=0.4196 · **命中分=9**
  - THE-EXPLORER/p1 · fit=0.85: fragments=[why-0, how-1, how-2, how-3, result-0] · sim=0.5151 · **命中分=5**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 9 -->
### I Flunked, But... (1930) [THE-RULER, THE-LOVER] [优质·多agent]
- **tmdb_id**: 88269
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.4975
- **genres** / **language**: Comedy / ja
- **overview**: After the plans of a group of college students to cheat on their final exams goes awry, they're left to reassess their lives and educations and get back on track.
- **跳转**: https://themoviecosmos.com/movie/88269
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-RULER/p1 · fit=0.85: fragments=[why-0, how-2, how-3, result-2] · sim=0.4444 · **命中分=4**
  - THE-LOVER/p2 · fit=0.68: fragments=[how-3, how-4, result-0, result-1, result-3] · sim=0.4975 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 8 -->
### Bad Kids Go to Hell (2012) [THE-LOVER, THE-CAREGIVER] [优质·多agent]
- **tmdb_id**: 138372
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.6239
- **genres** / **language**: Comedy, Mystery, Thriller, Horror / en
- **overview**: On a stormy Saturday afternoon, six students from Crestview Academy begin to meet horrible fates as they serve detention. Is a fellow student to blame, or perhaps Crestview's alleged ghosts are behind the terrible acts?
- **跳转**: https://themoviecosmos.com/movie/138372
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-LOVER/p2 · fit=0.68: fragments=[how-3, how-4, result-0, result-1, result-3] · sim=0.5166 · **命中分=5**
  - THE-CAREGIVER/p3 · fit=0.80: fragments=[result-0, how-2, how-3] · sim=0.6239 · **命中分=3**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 7 -->
### Space/Time (2025) [THE-CREATOR, THE-CAREGIVER] [优质·多agent]
- **tmdb_id**: 434853
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5418
- **genres** / **language**: Science Fiction, Action, Thriller / en
- **overview**: After a fatal test shuts down their project, a disgraced team of scientists enters the criminal underworld to rebuild a forbidden space-bending engine that could rescue humanity or annihilate it entirely.
- **跳转**: https://themoviecosmos.com/movie/434853
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-CREATOR/p2 · fit=0.82: fragments=[result-0, how-2, how-3, result-2] · sim=0.4957 · **命中分=4**
  - THE-CAREGIVER/p3 · fit=0.80: fragments=[result-0, how-2, how-3] · sim=0.5418 · **命中分=3**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

### 单 agent 命中

**Count:** 4 candidate(s)

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 5 -->
### Aarakshan (2011) [THE-INNOCENT]
- **tmdb_id**: 72152
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4933
- **genres** / **language**: Drama, Thriller / hi
- **overview**: The decision by India's supreme court to establish caste-based reservations for jobs in education causes conflict between a teacher and his mentor.
- **跳转**: https://themoviecosmos.com/movie/72152
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-INNOCENT/p2 · fit=0.85: fragments=[why-0, how-2, how-3, result-0, how-4] · sim=0.4933 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 5 -->
### Banshee Chapter (2013) [THE-EXPLORER]
- **tmdb_id**: 207769
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5017
- **genres** / **language**: Horror, Thriller / en
- **overview**: On the trail of a missing friend who had been experimenting with mind-altering drugs, a young journalist - aided by a rogue counter-culture writer, finds herself drawn into the dangerous world of top-secret government chemical research and the mystery of a disturbing radio signal of unknown origin.
- **跳转**: https://themoviecosmos.com/movie/207769
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EXPLORER/p1 · fit=0.85: fragments=[why-0, how-1, how-2, how-3, result-0] · sim=0.5017 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 5 -->
### Lie Detector (2011) [THE-EVERYMAN]
- **tmdb_id**: 375384
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4881
- **genres** / **language**: Comedy / en
- **overview**: A job interview takes an awkward turn when a lie detector reveals the unfiltered truths and hidden feelings of everyone involved.
- **跳转**: https://themoviecosmos.com/movie/375384
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-EVERYMAN/p2 · fit=0.72: fragments=[how-1, how-2, result-0, result-2, result-3] · sim=0.4881 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 5 -->
### Scare Out (2026) [THE-HERO]
- **tmdb_id**: 1447971
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5158
- **genres** / **language**: Crime, Thriller, Action / zh
- **overview**: After a critical intelligence leak, a national security unit launches an intensive investigation. But successive setbacks in their arrest operations reveal a shocking truth: the trail leads back to within the unit itself. Amidst a storm of trust and betrayal, a silent battle begins to unfold...
- **跳转**: https://themoviecosmos.com/movie/1447971
- **also_baseline**: false
- **命中视角/碎片**:
  - THE-HERO/p2 · fit=0.85: fragments=[why-0, how-2, how-3, result-0, result-3] · sim=0.5158 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

