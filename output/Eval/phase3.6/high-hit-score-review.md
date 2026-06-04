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

- **Generation date:** 2026-06-03
- **Total candidates (≥5):** 90
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

**Count:** 1 candidate(s)

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 11 -->
### Stranded (2021) [A2, A1] [优质·多agent]
- **tmdb_id**: 841793
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5777
- **genres** / **language**: Drama / pt
- **overview**: Tensions run high while food runs low as six influencers find themselves stranded on a secluded island after plans for a weekend escape go awry.
- **跳转**: https://themoviecosmos.com/movie/841793
- **also_baseline**: true
- **命中视角/碎片**:
  - A2/p1: fragments=[why-0, why-1, how-1] · sim=0.5777 · **命中分=3**
  - A2/p3: fragments=[result-0, result-1, how-2] · sim=0.5446 · **命中分=3**
  - A1/p2: fragments=[why-0, why-1, why-2, result-0, result-1] · sim=0.4782 · **命中分=5**
- **pseudo命中分合计**: 11
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

### 单 agent 命中

**Count:** 10 candidate(s)

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 12 -->
### Survival Family (2017) [A1]
- **tmdb_id**: 429918
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5253
- **genres** / **language**: Comedy, Drama, Adventure / ja
- **overview**: A world wide electrical outage occurs. Everything that requires electricity comes to a stop. Tokyo is nearly ruined. Yoshiyuki Suzuki decides to escape from Tokyo with his family.
- **跳转**: https://themoviecosmos.com/movie/429918
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.4985 · **命中分=7**
  - A1/p2: fragments=[why-0, why-1, why-2, result-0, result-1] · sim=0.5253 · **命中分=5**
- **pseudo命中分合计**: 12
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 效果相当好

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 10 -->
### Jupiter's Thunderballs (1903) [A4]
- **tmdb_id**: 190683
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5659
- **genres** / **language**: Comedy, Fantasy / fr
- **overview**: With godly entrapments, Zeus appears on the horizon, engages Hermes as an audience, and tries to throw some thunderbolts. They fizzle. Hephaestus tries to make some repairs but succeeds only in heating the bolts and burning Zeus's hands. Zeus conjures nine muses, but do their incantations help? He dismisses them as well as a visiting Pan, and his fits of pique become counter-productive. Can he get his powers back?
- **跳转**: https://themoviecosmos.com/movie/190683
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.5659 · **命中分=10**
- **pseudo命中分合计**: 10
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 只有宙斯和供电有一些联系，但是基本无关；怀疑太过受宙斯的概念影响

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 10 -->
### Ice Age: Collision Course (2016) [A4]
- **tmdb_id**: 278154
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5574
- **genres** / **language**: Adventure, Animation, Family, Comedy, Science Fiction / en
- **overview**: Set after the events of Continental Drift, Scrat's epic pursuit of his elusive acorn catapults him outside of Earth, where he accidentally sets off a series of cosmic events that transform and threaten the planet. To save themselves from peril, Manny, Sid, Diego, and the rest of the herd leave their home and embark on a quest full of thrills and spills, highs and lows, laughter and adventure while traveling to exotic new lands and locations.
- **跳转**: https://themoviecosmos.com/movie/278154
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, why-1, why-2, how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.5574 · **命中分=10**
- **pseudo命中分合计**: 10
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 9 -->
### The Quatermass Xperiment (1955) [A7]
- **tmdb_id**: 24580
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4445
- **genres** / **language**: Science Fiction, Horror / en
- **overview**: The first manned spacecraft, fired from an English launchpad, is first lost from radar, then roars back to Earth and crashes in a farmer's field, and is found to contain only one of the three men who took off in it; and he is unable to talk but appears to be undergoing a torturous physical and mental metamorphosis.
- **跳转**: https://themoviecosmos.com/movie/24580
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.4445 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 9 -->
### Summer Time Machine Blues (2005) [A7]
- **tmdb_id**: 26130
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4522
- **genres** / **language**: Comedy, Science Fiction / ja
- **overview**: The members of a sci-fi club accidentally spill Coke on the remote controller of an air-conditioner during summer and suddenly a time machine appears in their sweating bath-like clubroom.
- **跳转**: https://themoviecosmos.com/movie/26130
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.4522 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 9 -->
### The Last Voyage (1960) [A7]
- **tmdb_id**: 37605
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4658
- **genres** / **language**: Thriller, Drama, Action / en
- **overview**: The S. S. Claridon is scheduled for her five last voyages after thirty-eight years of service. After an explosion in the boiler room, Captain Robert Adams is reluctant to evacuate the steamship. While the crew fights to hold a bulkhead between the flooded boiler room and the engine room and avoid the sinking of the vessel, the passenger Cliff Henderson struggles against time trying to save his beloved wife Laurie Henderson, who is trapped under a steel beam in her cabin, with the support of the crew member Hank Lawson.
- **跳转**: https://themoviecosmos.com/movie/37605
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-0, why-2, how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.4658 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 结构  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 能看出资源短缺的环境是联系的纽带，但是效果不好

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 9 -->
### 97 Minutes (2023) [A7]
- **tmdb_id**: 940241
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4730
- **genres** / **language**: Action, Thriller, Drama / en
- **overview**: A hijacked 767 will crash in just 97 minutes when its fuel runs out. Against the strong will of NSA Deputy Toyin, NSA Director Hawkins prepares to have the plane shot down before it does any catastrophic damage on the ground, leaving the fate of the innocent passengers in the hands of Tyler, one of the alleged hijackers on board who is an undercover Interpol agent - or is he?
- **跳转**: https://themoviecosmos.com/movie/940241
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-0, why-2, how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.4730 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 7 -->
### Breathe (2024) [A1]
- **tmdb_id**: 720321
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4561
- **genres** / **language**: Action, Science Fiction, Mystery, Thriller / en
- **overview**: Air-supply is scarce in the near future, forcing a mother and daughter to fight for survival when two strangers arrive desperate for an oxygenated haven.
- **跳转**: https://themoviecosmos.com/movie/720321
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.4561 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 资源短缺的感觉挺优秀的，其实介于1和2之间

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Ivy (2015) [A2]
- **tmdb_id**: 312849
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4645
- **genres** / **language**: Drama, Fantasy, Thriller / tr
- **overview**: When the crew of a bankrupt cargo ship gets stuck on board for months, isolation breeds pressures that sink the men into a sea of madness and terror.
- **跳转**: https://themoviecosmos.com/movie/312849
- **also_baseline**: false
- **命中视角/碎片**:
  - A2/p2: fragments=[how-0, how-1, how-2, how-3, result-2] · sim=0.4645 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Contagion of Fear (2023) [A2]
- **tmdb_id**: 1223272
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4689
- **genres** / **language**: Science Fiction, Thriller / en
- **overview**: A catastrophic train derailment sends the city spiraling into chaos. But the derailment is just the beginning. A biological gas attack sees crash survivors collapsing and dying within minutes. And the sickness is rapidly spreading.
- **跳转**: https://themoviecosmos.com/movie/1223272
- **also_baseline**: false
- **命中视角/碎片**:
  - A2/p2: fragments=[how-0, how-1, how-2, how-3, result-2] · sim=0.4689 · **命中分=5**
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

**Count:** 1 candidate(s)

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 7 -->
### Bounty Killer (2013) [A2, A1] [优质·多agent]
- **tmdb_id**: 209504
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.4825
- **genres** / **language**: Action, Science Fiction / en
- **overview**: It’s been 20 years since the corporations took over the world’s governments. Their thirst for power and profits led to the Corporate Wars, a fierce global battle that laid waste to society as we know it. Born from the ash, the Council of Nine rose as a new law and order for this dark age. To avenge the corporations’ reckless destruction, the Council issues death warrants for all white collar criminals. Their hunters—the bounty killer. From amateur savage to graceful assassin, the bounty killers now compete for body count, fame and a fat stack of cash. They’re ending the plague of corporate greed and providing the survivors of the apocalypse with retribution. These are the new heroes. This is the age of the BOUNTY KILLER.
- **跳转**: https://themoviecosmos.com/movie/209504
- **also_baseline**: true
- **命中视角/碎片**:
  - A2/p1: fragments=[why-0, how-0, how-1] · sim=0.4743 · **命中分=3**
  - A1/p1: fragments=[why-0, how-0, how-1, how-2] · sim=0.4825 · **命中分=4**
- **pseudo命中分合计**: 7
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 效果不是特别好，low 2

### 单 agent 命中

**Count:** 4 candidate(s)

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 6 -->
### The Stenographer's Friend; Or, What Was Accomplished by an Edison Business Phonograph (1910) [A7]
- **tmdb_id**: 193982
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4491
- **genres** / **language**: Drama / en
- **overview**: It's a busy day at the office, and the stenographer is exhausted from trying to keep up with the demands on her skills. Even when she stays late, she cannot catch up with all of the work. But then a man comes into the office to demonstrate the many advantages of the Edison System, his company's new business phonograph.
- **跳转**: https://themoviecosmos.com/movie/193982
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-1] · sim=0.4491 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 一部老电影，overview中展现的新发明、繁荣反而与当下的裁员现状产生了对比

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 6 -->
### Million Dollar Madness (2025) [A7]
- **tmdb_id**: 1274837
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4422
- **genres** / **language**: Comedy / fr
- **overview**: Under immense pressure and amidst competition with a duplicitous colleague, Stan, the ambitious and very serious operations manager of a construction firm reaches breaking point when he learns that he’s been unfairly laid off by the company’s tyrannical CEO. He impulsively steals one million euros from the company’s vault, tosses away the key to the safe and hastily flees with his fiancée Marine… Before discovering that his termination was a mistake, and he is actually being promoted! Stan has until sunrise to return the money to the vault. But having thrown away his key, and with the only spare inside the CEO’s own apartment, he must reluctantly enlist the help of Hippolyte, Paris’s most unpredictable locksmith. The night promises to be full of twists and turns!
- **跳转**: https://themoviecosmos.com/movie/1274837
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-1] · sim=0.4422 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 5 -->
### Trespass (1992) [A7]
- **tmdb_id**: 22004
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4679
- **genres** / **language**: Action, Thriller, Crime / en
- **overview**: Two Arkansas firemen, Vince and Don, get hold of a map that leads to a cache of stolen gold in an abandoned factory in East St. Louis. What they don't know is that the factory is on the turf of a local gang, who come by to execute one of their enemies. Vince sees the shooting, the gang spots Vince, and extended mayhem ensues. As Vince and Don try to escape, gang leader King James argues with his subordinate Savon about how to get rid of the trespassers.
- **跳转**: https://themoviecosmos.com/movie/22004
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[why-0, how-2, how-3, result-2, result-3] · sim=0.4679 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 5 -->
### Reunión 10 años – No se aceptan devoluciones (2023) [A7]
- **tmdb_id**: 1186774
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4524
- **genres** / **language**: Comedy / es
- **overview**: Reunión 10 años – No se aceptan devoluciones
- **跳转**: https://themoviecosmos.com/movie/1186774
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[why-0, how-2, how-3, result-2, result-3] · sim=0.4524 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 不能把overview这么短的/或者因为没有overview所以用标题替代的电影放进候选 

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

**Count:** 2 candidate(s)

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 10 -->
### Lone Star (1952) [A2, A1] [优质·多agent]
- **tmdb_id**: 37593
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5242
- **genres** / **language**: Western / en
- **overview**: Cattle baron Devereaux Burke is enlisted by an aging Andrew Jackson to dissuade Sam Houston from establishing Texas as a republic. Burke must fight state senator Thomas Craden, in the process winning the heart of Craden's newspaper-editor girlfriend Martha Ronda.
- **跳转**: https://themoviecosmos.com/movie/37593
- **also_baseline**: true
- **命中视角/碎片**:
  - A2/p2: fragments=[why-0, result-1] · sim=0.5242 · **命中分=2**
  - A1/p1: fragments=[why-0, how-0, result-0, result-1, result-2] · sim=0.4990 · **命中分=5**
  - A1/p2: fragments=[why-0, result-0, result-1] · sim=0.5140 · **命中分=3**
- **pseudo命中分合计**: 10
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 5 -->
### Machete (2010) [A2, A1] [优质·多agent]
- **tmdb_id**: 23631
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5404
- **genres** / **language**: Action, Comedy, Thriller / en
- **overview**: After being set-up and betrayed by the man who hired him to assassinate a Texas Senator, an ex-Federale launches a brutal rampage of revenge against his former boss.
- **跳转**: https://themoviecosmos.com/movie/23631
- **also_baseline**: true
- **命中视角/碎片**:
  - A2/p2: fragments=[why-0, result-1] · sim=0.5404 · **命中分=2**
  - A1/p2: fragments=[why-0, result-0, result-1] · sim=0.4868 · **命中分=3**
- **pseudo命中分合计**: 5
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 很牵强。low 2

### 单 agent 命中

**Count:** 1 candidate(s)

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
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
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

**Count:** 0 candidate(s)

### 单 agent 命中

**Count:** 5 candidate(s)

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### The New Spirit (1942) [A7]
- **tmdb_id**: 64701
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4846
- **genres** / **language**: Animation / en
- **overview**: Animated documentary promoting timely filing and payment of Federal income taxes, demonstrated by Donald Duck's difficulties with his tax return.
- **跳转**: https://themoviecosmos.com/movie/64701
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4846 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Decoder (1984) [A7]
- **tmdb_id**: 90652
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5519
- **genres** / **language**: Horror, Mystery, Science Fiction / de
- **overview**: F.M. discovers that different sonic frequencies induce different patterns of behaviour in listeners, first in his own studio but later in the local "H-Burger" restaurant where the passive muzak appears to be wiping people's emotions.
- **跳转**: https://themoviecosmos.com/movie/90652
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.5519 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Why Try to Escape from That Which You Know You Can't Escape From? Because You Are a Coward (1970) [A4]
- **tmdb_id**: 261272
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5822
- **genres** / **language**: Mystery, Horror / da
- **overview**: A man is being haunted by a masked stranger.  The only language used in the movie comes from three (inter) title cards and a few sentences of sermon-like talk in Danish. Some of the talk is modified citations from the bible and similar sources.
- **跳转**: https://themoviecosmos.com/movie/261272
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5822 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Sound Test for Blackmail (1929) [A7]
- **tmdb_id**: 319841
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5665
- **genres** / **language**: Documentary / en
- **overview**: A brief sound test made during production of Blackmail (1929), featuring Alfred Hitchcock playfully teasing lead actress Anny Ondra as she struggles to respond on camera. Photographed by Jack E. Cox, the clip was shot to test the new sound recording system for what would become Hitchcock’s first talkie.
- **跳转**: https://themoviecosmos.com/movie/319841
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.5665 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 04-celebrity-scandal -->
<!-- pseudo命中分合计: 5 -->
### Queen of Spades: The Dark Rite (2015) [A4]
- **tmdb_id**: 358962
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5813
- **genres** / **language**: Horror / ru
- **overview**: There is an ancient ritual known to humankind for more than a hundred years...According to the legend, an ominous entity known as The Queen of Spades can be summoned by drawing a door and staircase on a mirror in the darkness, and by saying her name three times. The Queen of Spades gets her energy from reflective objects; she cuts locks of hair from those asleep, and those that see her go mad or die. Four teenagers decide to call The Queen of Spades as a joke. But when one of them dies of a sudden heart attack, the group realizes they are up against something inexplicable and deadly dangerous.
- **跳转**: https://themoviecosmos.com/movie/358962
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5813 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
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

**Count:** 1 candidate(s)

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 20 -->
### Poem of the Sea (1958) [A7, A1] [优质·多agent]
- **tmdb_id**: 257637
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5671
- **genres** / **language**: Drama / ru
- **overview**: A Soviet dam project means that many old Ukrainian villages will end up under water. There are conflicts between the dam engineers and villagers who don't want to move.
- **跳转**: https://themoviecosmos.com/movie/257637
- **also_baseline**: true
- **命中视角/碎片**:
  - A7/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, how-5, result-0, result-1, result-2, result-3, result-4, result-5] · sim=0.4068 · **命中分=13**
  - A1/p1: fragments=[how-0, how-1, how-2, how-3] · sim=0.5671 · **命中分=4**
  - A1/p2: fragments=[how-4, how-5, result-5] · sim=0.4654 · **命中分=3**
- **pseudo命中分合计**: 20
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 效果非常优秀

### 单 agent 命中

**Count:** 9 candidate(s)

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 13 -->
### Vajont (2001) [A7]
- **tmdb_id**: 48941
- **优质候选**: false
- **distinct_agents**: 0
- **相似度**: 0.3942
- **genres** / **language**: Drama / it
- **overview**: On October 9th, 1963, at 10:39 pm, 260 million cubic meters of rock fell down from Mount Toc to the artificial lake formed by the Vajont dam, the higher dam in the world. The landslide formed a 250-meters wave and 50 million cubic meters of water completely destroied all the below towns, killing more than 2000 people. Planned by engineer Semenza, Vajont dam (263 meters) had to carry the electricity in all the houses of the country. Tina Merlin, a journalist from 'L'Unitá', tried for years to denounce the danger to build a dam near the Mount Toc and expecially to denounce all the omissions by the corrupted politicians and workers in charge of the dam construction. They preferred to trust in old geologist Dal Piaz instead to hear engineer Semenza young son's alarming analysis. No one seemed to understand the high danger until that October fatal night.
- **跳转**: https://themoviecosmos.com/movie/48941
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, how-5, result-0, result-1, result-2, result-3, result-4, result-5] · sim=0.3942 · **命中分=13**
- **pseudo命中分合计**: 13
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 12 -->
### Flood (2007) [A4]
- **tmdb_id**: 6309
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5502
- **genres** / **language**: Drama, Action, Thriller / en
- **overview**: Timely yet terrifying, The Flood predicts the unthinkable. When a raging storm coincides with high seas it unleashes a colossal tidal surge, which travels mercilessly down England's East Coast and into the Thames Estuary. Overwhelming the Barrier, torrents of water pour into the city. The lives of millions of Londoners are at stake.
- **跳转**: https://themoviecosmos.com/movie/6309
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, how-5, result-0, result-1, result-2, result-3, result-5] · sim=0.5502 · **命中分=12**
- **pseudo命中分合计**: 12
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 12 -->
### Friday the Thirteenth (1933) [A4]
- **tmdb_id**: 50740
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5395
- **genres** / **language**: Comedy, Drama / en
- **overview**: It is pouring with rain at one minute to midnight on Friday the thirteenth, and the driver of a London bus is peering through his blurred windscreen as his vehicle sails down an empty road. Suddenly, lightning strikes, and a vast crane above topples into the path of the oncoming bus... Then Big Ben begins to wind backwards. Time recedes. And we discover the lives of all the passengers and the events that brought them to that late-night bus journey, from the con-man with a hundred-pound cheque to the businessman's distraught and elderly wife. Time flows on, inevitably, to the crash -- and past it, as some live and some die.
- **跳转**: https://themoviecosmos.com/movie/50740
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, how-0, how-1, how-2, how-3, how-4, how-5, result-0, result-1, result-2, result-3, result-5] · sim=0.5395 · **命中分=12**
- **pseudo命中分合计**: 12
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 9 -->
### Mutant Chronicles (2008) [A4]
- **tmdb_id**: 13256
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5021
- **genres** / **language**: Action, Adventure, Science Fiction / en
- **overview**: It's the year 2707. Earth's natural resources have all but been exhausted by mankind. Battles rage for the remainder between the competing Corporations. During one such battle the seal is broken and awakens an ancient and deadly machine that was once defeated thousands of years ago. The order that awaited its return must now lead a small group of soldiers to destroy it once and for all.
- **跳转**: https://themoviecosmos.com/movie/13256
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1, result-5] · sim=0.5021 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 9 -->
### Lyon: Quai de l'Archevêché (1896) [A4]
- **tmdb_id**: 190570
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5082
- **genres** / **language**: Documentary / fr
- **overview**: The floods of the Saône river during the first week of November, 1896.
- **跳转**: https://themoviecosmos.com/movie/190570
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[why-0, why-1, how-0, how-1, how-2, how-3, result-0, result-1, result-5] · sim=0.5082 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 一部很老的电影本身就会与眼下现实产生结构性共鸣

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 7 -->
### Golden Years (1991) [A7]
- **tmdb_id**: 36560
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4524
- **genres** / **language**: Science Fiction, Thriller, TV Movie, Horror / en
- **overview**: When an explosion at a top-secret government lab injures an elderly janitor, no one could have expected the terrifying results. Exposure to mysterious chemicals causes him to undergo a bizarre transformation. He is slowly... incredibly... growing younger every day. Now, a ruthless CIA assassin will stop at nothing to take him prisoner and turn him into a government guinea pig. With his future on the line, the janitor goes on the run with his wife and a feisty female agent. All the while, he continues to transform... into a being with powers that are as deadly as they are unimaginable.
- **跳转**: https://themoviecosmos.com/movie/36560
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4524 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 7 -->
### Tokio Jokio (1943) [A7]
- **tmdb_id**: 47463
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4101
- **genres** / **language**: Animation, Comedy / en
- **overview**: A "captured" Japanese newsreel. Civilian defense shows an aircraft spotter painting spots on aircraft and a fire prevention HQ that already burned down. Kitchen Hints shows the construction of a sandwich from bread and meat ration cards. Poisonalities in the News shows Yamamoto walking on stilts and boasting of plans for the White House, contrasted with the room reserved for him: an electric chair. A submarine, launched 3 weeks ahead of schedule, is still being built. A plane's new landing gear is a little man on a tricycle. A minesweeper uses a giant broom.
- **跳转**: https://themoviecosmos.com/movie/47463
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4101 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 5 -->
### The Rescue (2020) [A2]
- **tmdb_id**: 613658
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5552
- **genres** / **language**: Drama, Thriller, Action / zh
- **overview**: A rescue unit within the Chinese Coast Guard are forced to overcome their personal differences to resolve a crisis.
- **跳转**: https://themoviecosmos.com/movie/613658
- **also_baseline**: false
- **命中视角/碎片**:
  - A2/p2: fragments=[how-0, how-1, how-2, how-3, how-4] · sim=0.5552 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 5 -->
### Risen (2021) [A2]
- **tmdb_id**: 850099
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5341
- **genres** / **language**: Science Fiction, Drama, Thriller / en
- **overview**: Disaster unfolds when a meteor strikes a small town, turning the environment uninhabitable and killing everything in the surrounding area. Exobiologist Lauren Stone is called to find answers to the unearthly event. As she begins to uncover the truth, imminent danger awakens and it becomes a race against time to save mankind.
- **跳转**: https://themoviecosmos.com/movie/850099
- **also_baseline**: false
- **命中视角/碎片**:
  - A2/p2: fragments=[how-0, how-1, how-2, how-3, how-4] · sim=0.5341 · **命中分=5**
- **pseudo命中分合计**: 5
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

### 多 agents 命中

**Count:** 0 candidate(s)

### 单 agent 命中

**Count:** 7 candidate(s)

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### Lords of Scam (2021) [A1]
- **tmdb_id**: 888917
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4472
- **genres** / **language**: Documentary, Crime / fr
- **overview**: This documentary traces the rise and crash of scammers who conned the EU carbon quota system and pocketed millions before turning on one another.
- **跳转**: https://themoviecosmos.com/movie/888917
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.4068 · **命中分=4**
  - A1/p2: fragments=[why-0, how-1, result-0] · sim=0.4472 · **命中分=3**
- **pseudo命中分合计**: 7
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 结构和表层好像都有一些联系，但是都不太紧密

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 6 -->
### Cheaters (2000) [A7]
- **tmdb_id**: 15869
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4197
- **genres** / **language**: Drama, TV Movie / en
- **overview**: In the fall of 1994, a teacher at Chicago's run-down Steinmetz High conspires with the school's academic decathlon team to cheat on an academic competition.
- **跳转**: https://themoviecosmos.com/movie/15869
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.4197 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 6 -->
### The Clock-Maker's Secret (1907) [A4]
- **tmdb_id**: 332985
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5016
- **genres** / **language**: Horror, Drama, Fantasy / fr
- **overview**: The town-crier summons the inhabitants of the town and they read a manifesto which is posted on a wall announcing the fact that at 4 o'clock on that day the Lord Mayor will receive bids for the building of a town clock.
- **跳转**: https://themoviecosmos.com/movie/332985
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[how-0, how-1, how-2, result-0, result-1, why-0] · sim=0.5016 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 6 -->
### A Werewolf in England (2020) [A4]
- **tmdb_id**: 710217
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4773
- **genres** / **language**: Horror, Comedy / en
- **overview**: In Victorian-Era England, a Parish Councillor and criminal take refuge from a storm, at a remote countryside Inn. Forced to stay the night, they soon uncover a deadly pact between the strange Innkeepers and the flesh-hungry werewolves that inhabit the surrounding woodlands... now, as the werewolves close in, the guests must band together and fight tooth and nail to survive the night!
- **跳转**: https://themoviecosmos.com/movie/710217
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[how-0, how-1, how-2, result-0, result-1, why-0] · sim=0.4773 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 6 -->
### Johnny Keep Walking! (2023) [A7]
- **tmdb_id**: 1173076
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4117
- **genres** / **language**: Drama, Comedy / zh
- **overview**: A simple technician at a rural factory is mistakenly promoted to a high-level managerial position at corporate headquarters due to a series of clerical errors and a bribery scheme gone wrong.
- **跳转**: https://themoviecosmos.com/movie/1173076
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.4117 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### Psycho-Pass: Providence (2023) [A7]
- **tmdb_id**: 1012652
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4246
- **genres** / **language**: Animation, Crime, Mystery, Thriller / ja
- **overview**: While attending a meeting as a Chief Inspector of the Public Security Bureau, Akane Tsunemori received a report that an incident had occurred on a foreign vessel , and this was the beginning of a big and unexpected case.
- **跳转**: https://themoviecosmos.com/movie/1012652
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.4246 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### Dead Mail (2024) [A7]
- **tmdb_id**: 1229915
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4495
- **genres** / **language**: Crime, Thriller, Music, Mystery, Horror / en
- **overview**: An ominous help note finds its way to a 1980s post office, connecting a dead letter investigator to a kidnapped keyboard technician.
- **跳转**: https://themoviecosmos.com/movie/1229915
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.4495 · **命中分=5**
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

**Count:** 1 candidate(s)

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 10 -->
### Transpecos (2016) [A2, A1] [优质·多agent]
- **tmdb_id**: 381018
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5087
- **genres** / **language**: Thriller / en
- **overview**: For three US Border Patrol agents, the contents of one car reveal an insidious plot within their own ranks. The next 24 hours may cost them their lives.
- **跳转**: https://themoviecosmos.com/movie/381018
- **also_baseline**: true
- **命中视角/碎片**:
  - A2/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.4525 · **命中分=6**
  - A2/p2: fragments=[how-4, result-2] · sim=0.5027 · **命中分=2**
  - A1/p1: fragments=[how-0, how-1] · sim=0.5087 · **命中分=2**
- **pseudo命中分合计**: 10
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 在事实和情节层面上联系有些不太紧密

### 单 agent 命中

**Count:** 13 candidate(s)

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 7 -->
### Manhunt (2008) [A7]
- **tmdb_id**: 11927
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4184
- **genres** / **language**: Horror / no
- **overview**: Its the summer of 1974. Four friends have planned a recreational weekend hiking and camping in the forest. At a remote truck stop they pick up an anxious hitchhiker who only after a short ride demands they stop the vehicle. She is clearly frightened of somethingbut what she cant begin to describe in her carsick terror. Suddenly the group are ambushed and left unconscious.
- **跳转**: https://themoviecosmos.com/movie/11927
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, how-2, how-3, how-4, result-0, result-2] · sim=0.4184 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 7 -->
### French Roast (2008) [A7]
- **tmdb_id**: 37845
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4781
- **genres** / **language**: Animation / fr
- **overview**: In a fancy Parisian Café, an uptight businessman discovers he forgot to bring his wallet and bides his time by ordering more coffee.
- **跳转**: https://themoviecosmos.com/movie/37845
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[how-1, how-2, how-3, how-4, result-0, result-1, result-2] · sim=0.4781 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 7 -->
### The Trial of Donald Duck (1948) [A7]
- **tmdb_id**: 67603
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4721
- **genres** / **language**: Animation, Comedy / en
- **overview**: Donald is caught in the rain while eating his lunch. He ducks into a restaurant for a cup of coffee, but Chez Pierre is a very ritzy place, and by the time all is said and done, he's facing a bill for $35.99, and he only got a drop of coffee, and he only has a nickel. Pierre takes him to court, where this story is told, and is ordered to pay $10 or wash dishes for ten days.
- **跳转**: https://themoviecosmos.com/movie/67603
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[how-1, how-2, how-3, how-4, result-0, result-1, result-2] · sim=0.4721 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 7 -->
### The Ice Storm (1997) [A7]
- **tmdb_id**: 68924
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4457
- **genres** / **language**: Drama / en
- **overview**: In the weekend after thanksgiving 1973 the Hood family is skidding out of control. Then an ice storm hits, the worst in a century.
- **跳转**: https://themoviecosmos.com/movie/68924
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, how-2, how-3, how-4, result-0, result-2] · sim=0.4457 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 6 -->
### The Tunnel (2011) [A2]
- **tmdb_id**: 46221
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5141
- **genres** / **language**: Horror, Thriller, Mystery / en
- **overview**: An investigation into a government cover-up leads to a network of abandoned train tunnels deep beneath the heart of Sydney. As a journalist and her crew hunt for the story it quickly becomes clear the story is hunting them.
- **跳转**: https://themoviecosmos.com/movie/46221
- **also_baseline**: false
- **命中视角/碎片**:
  - A2/p3: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5141 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 6 -->
### In Dubious Battle (2016) [A2]
- **tmdb_id**: 337844
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4332
- **genres** / **language**: Drama / en
- **overview**: In the California apple country, 900 migratory workers rise 'in dubious battle' against the landowners. The group takes on a life of its own—stronger than its individual members, and more frightening. Led by the doomed Jim Nolan, the strike is founded on his tragic idealism—'courage, never submit, or yield'.
- **跳转**: https://themoviecosmos.com/movie/337844
- **also_baseline**: false
- **命中视角/碎片**:
  - A2/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.4332 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 结构  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 加州这个地理位置共振感强

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 6 -->
### Fate/Grand Order the Movie: Divine Realm of the Round Table: Camelot 1 Wandering; Agateram (2020) [A4]
- **tmdb_id**: 637202
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5420
- **genres** / **language**: Animation, Action, Adventure, History, Drama, Fantasy / ja
- **overview**: The wandering knight, Bedivere, reaches the end of his journey. It is A.D. 1273 in Jerusalem. The Holy Land has been transformed into a massive desert and its people have been forced out of their homes as three major powers wage war with each other in this wasteland. The Knights of the Round Table come together to protect the Holy City and their Lion King. With the whole of his kingdom summoned into a strange land, Ozymandias, the Sun King, quietly plots against the tyranny of this bizarre realm. The mountain people, protectors of those who were stripped of their land, await their chance at rebellion. In order to fulfill his mission, Bedivere heads for the Holy City where the Lion King rules. There he meets humanity’s final Master, Ritsuka Fujimaru, who has come to Jerusalem, accompanied by his Demi-Servant, Mash Kyrielight, in their quest to restore human history.
- **跳转**: https://themoviecosmos.com/movie/637202
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[how-0, how-1, how-2, how-3, why-0, result-0] · sim=0.5420 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 6 -->
### Stranded (2021) [A2]
- **tmdb_id**: 841793
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5111
- **genres** / **language**: Drama / pt
- **overview**: Tensions run high while food runs low as six influencers find themselves stranded on a secluded island after plans for a weekend escape go awry.
- **跳转**: https://themoviecosmos.com/movie/841793
- **also_baseline**: false
- **命中视角/碎片**:
  - A2/p3: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5111 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 6 -->
### Meteor: First Impact (2022) [A4]
- **tmdb_id**: 1077596
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5236
- **genres** / **language**: Action, Thriller / en
- **overview**: A scientist races the clock in an attempt to save Earth from a series of deadly meteor attacks.
- **跳转**: https://themoviecosmos.com/movie/1077596
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[how-0, how-1, how-2, how-3, why-0, result-0] · sim=0.5236 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 5 -->
### The Andromeda Strain (1971) [A7]
- **tmdb_id**: 10514
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4648
- **genres** / **language**: Science Fiction, Thriller / en
- **overview**: When virtually all of the residents of Piedmont, New Mexico, are found dead after the return to Earth of a space satellite, the head of the US Air Force's Project Scoop declares an emergency. A group of eminent scientists led by Dr. Jeremy Stone scramble to a secure laboratory and try to first isolate the life form while determining why two people from Piedmont - an old alcoholic and a six-month-old baby - survived. The scientists methodically study the alien life form unaware that it has already mutated and presents a far greater danger in the lab, which is equipped with a nuclear self-destruct device designed to prevent the escape of dangerous biological agents.
- **跳转**: https://themoviecosmos.com/movie/10514
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.4648 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 5 -->
### Act of Valor (2012) [A7]
- **tmdb_id**: 75674
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4675
- **genres** / **language**: Action, Thriller, War / en
- **overview**: When a covert mission to rescue a kidnapped CIA operative uncovers a chilling plot, an elite, highly trained U.S. SEAL team speeds to hotspots around the globe, racing against the clock to stop a deadly terrorist attack.
- **跳转**: https://themoviecosmos.com/movie/75674
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[how-0, how-1, how-2, result-0, result-1] · sim=0.4675 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 5 -->
### Father Noah's Ark (1933) [A4]
- **tmdb_id**: 107511
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5113
- **genres** / **language**: Animation / en
- **overview**: Noah, his family (wife, 3 sons, their wives), and various animals all help build the ark. The rains come, and the skunks barely miss the boat (not that anyone was particularly looking for them), but they manage to swim to it. After the rain and many lamentations by the humans, the sun returns, to the great joy of all. The ground appears, and the animals (and many new babies) disembark.
- **跳转**: https://themoviecosmos.com/movie/107511
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[how-0, how-1, how-2, how-3, result-1] · sim=0.5113 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 5 -->
### The Sunshine Makers (1935) [A4]
- **tmdb_id**: 184664
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5202
- **genres** / **language**: Family, Animation / en
- **overview**: Happy sunshine-bottling gnomes battle gloomy swamp-dwellers.
- **跳转**: https://themoviecosmos.com/movie/184664
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[how-0, how-1, how-2, how-3, result-1] · sim=0.5202 · **命中分=5**
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

**Count:** 0 candidate(s)

### 单 agent 命中

**Count:** 11 candidate(s)

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 11 -->
### Hoosiers (1986) [A1]
- **tmdb_id**: 5693
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4978
- **genres** / **language**: Drama, Family / en
- **overview**: Failed college coach Norman Dale gets a chance at redemption when he is hired to coach a high school basketball team in a tiny Indiana town. After a teacher persuades star player Jimmy Chitwood to quit and focus on his long-neglected studies, Dale struggles to develop a winning team in the face of community criticism for his temper and his unconventional choice of assistant coach: Shooter, a notorious alcoholic.
- **跳转**: https://themoviecosmos.com/movie/5693
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4978 · **命中分=6**
  - A1/p3: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.4861 · **命中分=5**
- **pseudo命中分合计**: 11
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 11 -->
### Hockey Homicide (1945) [A1]
- **tmdb_id**: 66876
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5831
- **genres** / **language**: Animation, Comedy / en
- **overview**: A crowd gathers at the skating rink to watch the big championship hockey game of the Pelicans versus the Aardvarks. Although referee "Clean Game" Kinney does his best to supervise, the hockey game really gets out of hand eventually. Two star players, Bertino and Ferguson, are so anxious, they never get let out of the penalty box, referee Kinney is never able to drop the puck without being physically hurt somehow, and the spectators themselves are so worked into the game, they take out their aggression on the ice while the players relax in the bleachers.
- **跳转**: https://themoviecosmos.com/movie/66876
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5622 · **命中分=6**
  - A1/p3: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.5831 · **命中分=5**
- **pseudo命中分合计**: 11
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 7 -->
### Tactical Force (2011) [A7]
- **tmdb_id**: 70008
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5286
- **genres** / **language**: Action, Thriller, Comedy, Crime / en
- **overview**: A training exercise for the LAPD SWAT Team goes terribly wrong when they find themselves pitted against two rival gangs while trapped in an abandoned Hangar, armed with nothing but blanks.
- **跳转**: https://themoviecosmos.com/movie/70008
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5286 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### Run Silent, Run Deep (1958) [A4]
- **tmdb_id**: 18784
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5761
- **genres** / **language**: Drama, War / en
- **overview**: The captain of a submarine sunk by the Japanese during WWII is finally given a chance to skipper another sub after a year of working a desk job. His singleminded determination for revenge against the destroyer that sunk his previous vessel puts his new crew in unneccessary danger.
- **跳转**: https://themoviecosmos.com/movie/18784
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-1] · sim=0.5761 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### Last Knights (2015) [A4]
- **tmdb_id**: 308504
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5729
- **genres** / **language**: Action, Adventure / en
- **overview**: When an evil emperor executes their leader, his band of knights – bound by duty and honour – embarks on a journey of vengeance that will not come to an end until they've destroyed their mortal foe.
- **跳转**: https://themoviecosmos.com/movie/308504
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-1] · sim=0.5729 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 5 -->
### That Night of Varennes (1982) [A7]
- **tmdb_id**: 42131
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4846
- **genres** / **language**: History, Comedy, Drama / fr
- **overview**: During the French Revolution, a surprising company shares a coach, trying to catch up something - the time itself, perhaps.
- **跳转**: https://themoviecosmos.com/movie/42131
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[how-0, how-1, how-2, how-3, result-1] · sim=0.4846 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 5 -->
### The Hobbit: The Battle of the Five Armies (2014) [A4]
- **tmdb_id**: 122917
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5256
- **genres** / **language**: Action, Adventure, Fantasy / en
- **overview**: Following Smaug's attack on Laketown, Bilbo and the dwarves try to defend Erebor's mountain of treasure from others who claim it: the men of the ruined Laketown and the elves of Mirkwood. Meanwhile an army of Orcs led by Azog the Defiler is marching on Erebor, fueled by the rise of the dark lord Sauron. Dwarves, elves and men must unite, and the hope for Middle-Earth falls into Bilbo's hands.
- **跳转**: https://themoviecosmos.com/movie/122917
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p3: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.5256 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 5 -->
### Time Travel Mater (2012) [A7]
- **tmdb_id**: 141528
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4849
- **genres** / **language**: Animation, Family, Science Fiction, Comedy / en
- **overview**: When a clock lands on Mater's engine, he travels back in time to 1909 where he meets Stanley, an ambitious young car on his way to California. With the help of Lightning McQueen, Mater alters history by convincing Stanley to stay and build Radiator Springs. Stanley meets Lizzie and they commemorate the opening of the new courthouse with their wedding.
- **跳转**: https://themoviecosmos.com/movie/141528
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[why-0, how-2, how-3, result-0, result-1] · sim=0.4849 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 5 -->
### Champions (2018) [A7]
- **tmdb_id**: 456929
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4861
- **genres** / **language**: Comedy, Family, Drama / es
- **overview**: A disgraced basketball coach is given the chance to coach Los Amigos, a team of players who are intellectually disabled, and soon realizes they just might have what it takes to make it to the national championships.
- **跳转**: https://themoviecosmos.com/movie/456929
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[how-0, how-1, how-2, how-3, result-1] · sim=0.4861 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 5 -->
### Driven (2019) [A7]
- **tmdb_id**: 587138
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4890
- **genres** / **language**: Comedy, Horror, Thriller / en
- **overview**: Emerson Graham's nights as a cab driver are filled with annoyances and inconveniences, but until tonight, never attacks and disappearances. After picking up a mysterious passenger her evening goes from working a job to performing a quest as they must race against the clock to defeat a force of evil. The meter is running.
- **跳转**: https://themoviecosmos.com/movie/587138
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[why-0, how-2, how-3, result-0, result-1] · sim=0.4890 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 5 -->
### 1212. The Battle of Las Navas de Tolosa (2023) [A4]
- **tmdb_id**: 1192043
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5332
- **genres** / **language**: Documentary, History, War / es
- **overview**: On 16 July 1212, a Crusader army made up of Castilians, Aragonese and Navarrese (but also French, English and Germans) confronted the army of the Almohad Caliph an-Nasir at the foot of the Sierra Morena mountain range. The Battle of Las Navas de Tolosa, as the battle is known, is considered the most important battle of the Middle Ages on the Iberian Peninsula and is a key event in the history of Spain. More than 800 years later, a group of archaeologists and specialists have begun an archaeological study of the battlefield. Is everything that has been said about the battle true? What secrets does the terrain hide? And, above all, what can we learn today about events that took place hundreds of years ago and that pitted tens of thousands of people against each other in the south of our country?
- **跳转**: https://themoviecosmos.com/movie/1192043
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p3: fragments=[how-0, how-1, how-2, how-3, result-0] · sim=0.5332 · **命中分=5**
- **pseudo命中分合计**: 5
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

**Count:** 2 candidate(s)

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 9 -->
### Venus in Fur (2013) [A2, A1] [优质·多agent]
- **tmdb_id**: 197082
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.6666
- **genres** / **language**: Drama / fr
- **overview**: An enigmatic actress may have a hidden agenda when she auditions for a part in a misogynistic writer's play.
- **跳转**: https://themoviecosmos.com/movie/197082
- **also_baseline**: true
- **命中视角/碎片**:
  - A2/p1: fragments=[why-0, why-1] · sim=0.5797 · **命中分=2**
  - A1/p2: fragments=[how-1, how-2, why-0, why-1] · sim=0.6666 · **命中分=4**
  - A1/p3: fragments=[how-0, how-1, result-0] · sim=0.5997 · **命中分=3**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: overview太短很难判断，题材可能有点危险（厌女，性别议题）

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### The Scenic Route (1978) [A2, A1] [优质·多agent]
- **tmdb_id**: 128042
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.5604
- **genres** / **language**: Drama / en
- **overview**: An experimental drama that spins the tale of a woman, her sister, and the man who completes the triangle. Told through such fertile sources as grand opera, classical painting, and Victorian melodrama.
- **跳转**: https://themoviecosmos.com/movie/128042
- **also_baseline**: true
- **命中视角/碎片**:
  - A2/p3: fragments=[result-0, why-1] · sim=0.4981 · **命中分=2**
  - A1/p3: fragments=[how-0, how-1, result-0] · sim=0.5604 · **命中分=3**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

### 单 agent 命中

**Count:** 12 candidate(s)

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### Lovecraft: Fear of the Unknown (2008) [A4]
- **tmdb_id**: 44038
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5749
- **genres** / **language**: Documentary / en
- **overview**: A chronicle of the life, work and mind that created the Cthulhu mythos.
- **跳转**: https://themoviecosmos.com/movie/44038
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.5749 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### Beyond Darkness (1990) [A4]
- **tmdb_id**: 60190
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5476
- **genres** / **language**: Horror, Thriller / en
- **overview**: A priest and his family move into a new house, without knowing that it was built over the place where twenty witches were burnt at the stake.
- **跳转**: https://themoviecosmos.com/movie/60190
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.5476 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### Maddalena, Zero for Conduct (1940) [A7]
- **tmdb_id**: 61464
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4825
- **genres** / **language**: Comedy, Romance / it
- **overview**: A young woman teaches commercial writing and makes her students practice by writing letters addressed to an imaginary recipient from Vienna. One day, the love letter the woman writes to this non-existent man is accidentally sent by one of her students –and falls into the hands of a real person.
- **跳转**: https://themoviecosmos.com/movie/61464
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.4825 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### Chess of the Wind (1976) [A4]
- **tmdb_id**: 194088
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5502
- **genres** / **language**: Drama, Mystery, Thriller / fa
- **overview**: The first lady of a noble house has died and now there is conflict between the remainders for taking over her heritage.
- **跳转**: https://themoviecosmos.com/movie/194088
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.5502 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### Beauty and the Beast (2014) [A4]
- **tmdb_id**: 197796
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5629
- **genres** / **language**: Fantasy, Romance / fr
- **overview**: Forced to face the cruel side of life, a devastated, bankrupt merchant chances upon the enchanted castle of a hideous creature, the mere sight of it chills the bone to the marrow. There, a fate worse than death awaits the poor father-of-six, who, after plucking a sweet-scented rose from the repulsive master's verdant garden, must do the impossible: permit his compassionate daughter, Belle, to take his place and pay for the sins of her parent. Now, an impenetrable mystery shrouds the haunted mansion, and, as repugnance gradually turns into affection, only true love could break the spell.
- **跳转**: https://themoviecosmos.com/movie/197796
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.5629 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### Dead Mail (2024) [A7]
- **tmdb_id**: 1229915
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5224
- **genres** / **language**: Crime, Thriller, Music, Mystery, Horror / en
- **overview**: An ominous help note finds its way to a 1980s post office, connecting a dead letter investigator to a kidnapped keyboard technician.
- **跳转**: https://themoviecosmos.com/movie/1229915
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.5224 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### L'Odissea (1911) [A1]
- **tmdb_id**: 194224
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6236
- **genres** / **language**: Drama, Adventure / it
- **overview**: Film adaptation of Homer's 'The Odyssey.'
- **跳转**: https://themoviecosmos.com/movie/194224
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, why-0, why-1] · sim=0.6236 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 奥德赛的老电影，有历史加成。

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### You're a Sweetheart (1937) [A7]
- **tmdb_id**: 218347
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5949
- **genres** / **language**: Romance, Music / en
- **overview**: A Broadway producer is in a quandary when he discovers that the opening of his newest big production coincides with that of a major charity event. He despairs that the show will close after opening night until an ingenious writer suggests that he simply give the production snob-appeal by making the tickets nearly impossible to get by fabricating a story that they were all purchased by a flamboyant Texas oil baron who is totally besotted by the show's star.
- **跳转**: https://themoviecosmos.com/movie/218347
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[how-0, how-1, why-0, why-1, result-0] · sim=0.5949 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Les Misérables (1913) [A1]
- **tmdb_id**: 285232
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5770
- **genres** / **language**: Drama / fr
- **overview**: Directed by Albert Capellani.
- **跳转**: https://themoviecosmos.com/movie/285232
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, why-0, why-1] · sim=0.5770 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### La cigüeña distraída (1966) [A7]
- **tmdb_id**: 404524
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4840
- **genres** / **language**: Family, Comedy / es
- **overview**: La cigüeña distraída
- **跳转**: https://themoviecosmos.com/movie/404524
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, why-0, why-1, result-0] · sim=0.4840 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Kuleshov Effect (1919) [A7]
- **tmdb_id**: 462602
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4562
- **genres** / **language**: Drama / xx
- **overview**: An experiment in editing. This entry refers to both the initial, likely lost 1919 experiment, created using footage of Ivan Mosjoukine, and the later surviving recreation featuring two unknown actors.
- **跳转**: https://themoviecosmos.com/movie/462602
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, why-0, why-1, result-0] · sim=0.4562 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### Theatre: A Love Story (2020) [A7]
- **tmdb_id**: 617397
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6515
- **genres** / **language**: Drama, Romance / ja
- **overview**: The director of a theatre company is in crisis and his actors have lost confidence in him. One day he meets a woman wearing the same shoes as him, immediately sparking chemistry between the two.
- **跳转**: https://themoviecosmos.com/movie/617397
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[how-0, how-1, why-0, why-1, result-0] · sim=0.6515 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
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

**Count:** 1 candidate(s)

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 13 -->
### Dead Mail (2024) [A7, A1] [优质·多agent]
- **tmdb_id**: 1229915
- **优质候选**: true
- **distinct_agents**: 2
- **相似度**: 0.4862
- **genres** / **language**: Crime, Thriller, Music, Mystery, Horror / en
- **overview**: An ominous help note finds its way to a 1980s post office, connecting a dead letter investigator to a kidnapped keyboard technician.
- **跳转**: https://themoviecosmos.com/movie/1229915
- **also_baseline**: true
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, why-0, how-2, how-3, result-0, result-1, result-2, result-3, how-4] · sim=0.4862 · **命中分=10**
  - A1/p2: fragments=[why-0, how-1, how-2] · sim=0.4541 · **命中分=3**
- **pseudo命中分合计**: 13
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 基本完全无关，可能是将举报信和overview中的求助纸条关联了？

### 单 agent 命中

**Count:** 9 candidate(s)

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 16 -->
### The Killing Room (2009) [A1]
- **tmdb_id**: 20777
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4645
- **genres** / **language**: Thriller, Drama / en
- **overview**: Four volunteers sign up for what initially appears to be a typical paid research study, only to discover that they've unwittingly become involved with a classified government program that was said to have been terminated nearly two decades ago.
- **跳转**: https://themoviecosmos.com/movie/20777
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-3] · sim=0.4028 · **命中分=9**
  - A1/p2: fragments=[why-0, how-1, how-2] · sim=0.4645 · **命中分=3**
  - A1/p3: fragments=[how-3, result-0, result-2, result-3] · sim=0.4088 · **命中分=4**
- **pseudo命中分合计**: 16
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 基本不相干

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 10 -->
### Panic in the Mailroom (2013) [A7]
- **tmdb_id**: 229405
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4843
- **genres** / **language**: Animation, Family, Comedy, Science Fiction / en
- **overview**: Two Minions are busy at work in the mailroom. One of them, bored, decides to throw a box of expired PX-41 samples into its designated chute.
- **跳转**: https://themoviecosmos.com/movie/229405
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, why-0, how-2, how-3, result-0, result-1, result-2, result-3, how-4] · sim=0.4843 · **命中分=10**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 9 -->
### CNCO: los últimos cinco días (2022) [A1]
- **tmdb_id**: 1030206
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4196
- **genres** / **language**: Music, Documentary / es
- **overview**: CNCO: los últimos cinco días
- **跳转**: https://themoviecosmos.com/movie/1030206
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-3] · sim=0.4196 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 8 -->
### Swordsman (1990) [A4]
- **tmdb_id**: 18860
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.6518
- **genres** / **language**: Action, Adventure / cn
- **overview**: A kung-fu manual known as the Sacred Scroll is stolen from the Emperor's library. An army detachment is sent to recover it. Meanwhile, a young swordsman and his fellow disciple are accidentally drawn into the chaos.
- **跳转**: https://themoviecosmos.com/movie/18860
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-3] · sim=0.6518 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 8 -->
### Viking Legacy (2016) [A4]
- **tmdb_id**: 416777
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.5789
- **genres** / **language**: Action, Adventure / en
- **overview**: In ancient times, there were seven sacred scrolls believed to grant power and prosperity to those who possessed them. Prophecy told that a child born in pure Royal blood would one day harness power and rule over the nations. As men fought to claim the scrolls, Europe was pushed to the brink of war. In order to maintain peace, a Celtic King, the Father of a pure blood child, obtained the scrolls and gave them to the Christian Council for safe keeping. As word of the King’s actions spread, a warlord hell – bent on finding the scrolls murdered him in cold blood. And so, the King’s Daughter, like the scrolls, was taken into hiding until the day that the prophecy could be fulfilled ...
- **跳转**: https://themoviecosmos.com/movie/416777
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, result-2, result-3] · sim=0.5789 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 7 -->
### 6 Hours to Live (1932) [A4]
- **tmdb_id**: 248129
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4779
- **genres** / **language**: Science Fiction, Drama, Mystery / en
- **overview**: The victim of a political assassination is brought back to life by a scientific experiment. However, the effects only last for six hours, and he must find his killer in that time.
- **跳转**: https://themoviecosmos.com/movie/248129
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.4779 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 7 -->
### The Stanford Prison Experiment (2015) [A4]
- **tmdb_id**: 308032
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4873
- **genres** / **language**: Thriller, Drama, History / en
- **overview**: In 1971, Stanford's Professor Philip Zimbardo conducts a controversial psychology experiment in which college students pretend to be either prisoners or guards, but the proceedings soon get out of hand. Based on a true story.
- **跳转**: https://themoviecosmos.com/movie/308032
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[how-0, how-1, how-2, how-3, result-0, result-1, result-2] · sim=0.4873 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 6 -->
### Jenaro, el de los 14 (1974) [A7]
- **tmdb_id**: 176116
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4358
- **genres** / **language**: Comedy / es
- **overview**: Jenaro, el de los 14
- **跳转**: https://themoviecosmos.com/movie/176116
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.4358 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 6 -->
### La cigüeña distraída (1966) [A7]
- **tmdb_id**: 404524
- **优质候选**: false
- **distinct_agents**: 1
- **相似度**: 0.4577
- **genres** / **language**: Family, Comedy / es
- **overview**: La cigüeña distraída
- **跳转**: https://themoviecosmos.com/movie/404524
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.4577 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->
- **打分备注**: 

