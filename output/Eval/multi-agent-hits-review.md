# Multi-Agent Screenplay Hits — Unified Review

## Criteria

### 多 agent 同时命中（准入门槛 · 已实现）

Candidate **enters this review** when **≥2 distinct `agent_id`s** among screenplay agents `{A1, A2, A4, A7}` contributed `hit_sources` for the same `tmdb_id` (existing retrieval aggregation rule).

### Pseudo 命中分

For each hit line under **命中视角/碎片**, count entries in `fragments=[...]` — **each fragment id = 1 point** for that pseudo.

- **Candidate 总分** (`pseudo命中分合计`) = sum of pseudo 命中分 across all qualifying hit lines.
- Shown inline per line, e.g. `A2/p1: fragments=[...] · sim=... · **命中分=3**`.

### Sources

- **Primary:** `hit_sources` in each run's `retrieve.json` (fragment arrays).
- **Cross-check:** `命中视角/碎片` in `candidates.md` when present.
- **Editor fields:** 共振分 / 共振类型 are placeholders only (not filled by this extract).

- **Generation date:** 2026-06-02
- **Total multi-agent candidates:** 9
- **Runs scanned:** 10 (01-grid-outage … 10-whistleblower-leak)

## Summary table (sorted by pseudo命中分合计 ↓)

| rank | run_id               | tmdb_id | title                                | agents | pseudo命中分合计 | per-agent   | overlap               |
| ---: | -------------------- | ------: | ------------------------------------ | ------ | ---------------: | ----------- | --------------------- |
|    1 | 01-grid-outage       |  429918 | Survival Family                      | A1, A7 |               17 | A1:12, A7:5 | A1 + creative (A4/A7) |
|    2 | 08-sports-underdog   |   32007 | Hurricane Season                     | A1, A7 |               15 | A1:9, A7:6  | A1 + creative (A4/A7) |
|    3 | 06-tech-monopoly     |   30858 | Terra Nova                           | A1, A4 |               13 | A1:6, A4:7  | A1 + creative (A4/A7) |
|    4 | 01-grid-outage       |  190738 | Assembling a Generator               | A1, A7 |               10 | A1:4, A7:6  | A1 + creative (A4/A7) |
|    5 | 09-cultural-backlash |  337191 | Alice's Adventures in Wonderland     | A1, A7 |                9 | A1:3, A7:6  | A1 + creative (A4/A7) |
|    6 | 02-corporate-layoff  | 1002695 | Mirreyes contra Godínez 2: El retiro | A1, A2 |                8 | A1:3, A2:5  | includes A2           |
|    7 | 03-election-upset    |   23631 | Machete                              | A1, A2 |                8 | A1:5, A2:3  | includes A2           |
|    8 | 05-climate-disaster  |  257637 | Poem of the Sea                      | A1, A2 |                7 | A1:4, A2:3  | includes A2           |
|    9 | 07-migration-border  |  381018 | Transpecos                           | A1, A2 |                6 | A1:4, A2:2  | includes A2           |

## Candidates (global sort by pseudo命中分合计 ↓)

**Count:** 9 multi-agent hit(s)

<!-- run_id: 01-grid-outage -->
<!-- retrieve: A1, A7 -->
<!-- overlap: A1 + creative (A4/A7) -->
<!-- pseudo命中分合计: 17 -->
### Survival Family (2017) [A7]
- **tmdb_id**: 429918
- **run_id**: 01-grid-outage
- **pseudo命中分合计**: 17
- **per-agent 命中分**: A1:12, A7:5
- **相似度**: 0.5681
- **genres** / **language**: Comedy, Drama, Adventure / ja
- **overview**: A world wide electrical outage occurs. Everything that requires electricity comes to a stop. Tokyo is nearly ruined. Yoshiyuki Suzuki decides to escape from Tokyo with his family.
- **跳转**: https://themoviecosmos.com/movie/429918
- **also_baseline**: true
- **命中视角/碎片**:
  - A7/p3: fragments=[how-4, how-5, result-0, result-1, result-2] · sim=0.4611 · **命中分=5**
  - A1/p1: fragments=[how-0, how-1, how-2, how-3, how-4] · sim=0.5681 · **命中分=5**
  - A1/p3: fragments=[how-0, how-1, how-2, how-3, how-4, how-5, result-0] · sim=0.4809 · **命中分=7**
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 08-sports-underdog -->
<!-- retrieve: A1, A7 -->
<!-- overlap: A1 + creative (A4/A7) -->
<!-- pseudo命中分合计: 15 -->
### Hurricane Season (2010) [A7]
- **tmdb_id**: 32007
- **run_id**: 08-sports-underdog
- **pseudo命中分合计**: 15
- **per-agent 命中分**: A1:9, A7:6
- **相似度**: 0.5082
- **genres** / **language**: Drama / en
- **overview**: Based on true events amid the wreckage and chaos dealt by Hurricane Katrina; one basketball coach in Marrero, Louisiana just will not give up. Coach Al Collins, gathers other players from hard-hit schools and builds a team actually worthy enough to go to the state playoffs.
- **跳转**: https://themoviecosmos.com/movie/32007
- **also_baseline**: true
- **命中视角/碎片**:
  - A7/p3: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5082 · **命中分=6**
  - A1/p2: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.5020 · **命中分=5**
  - A1/p3: fragments=[how-0, how-1, why-0, result-1] · sim=0.4986 · **命中分=4**
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 表层  <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 06-tech-monopoly -->
<!-- retrieve: A1, A4 -->
<!-- overlap: A1 + creative (A4/A7) -->
<!-- pseudo命中分合计: 13 -->
### Terra Nova (2008) [A4]
- **tmdb_id**: 30858
- **run_id**: 06-tech-monopoly
- **pseudo命中分合计**: 13
- **per-agent 命中分**: A1:6, A4:7
- **相似度**: 0.5373
- **genres** / **language**: Drama, Thriller, Action / ru
- **overview**: A story, which takes place in 2013, describes the world overflowing with "dangerous" criminals due to the official termination of death penalty. The UN "blue helmets" under the directive from the central authority (i.e., One World Government) decided to conduct a social "experiment" by forcibly dumping the outlaws on the deserted island...
- **跳转**: https://themoviecosmos.com/movie/30858
- **also_baseline**: true
- **命中视角/碎片**:
  - A4/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5373 · **命中分=7**
  - A1/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0] · sim=0.4402 · **命中分=6**
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 01-grid-outage -->
<!-- retrieve: A1, A7 -->
<!-- overlap: A1 + creative (A4/A7) -->
<!-- pseudo命中分合计: 10 -->
### Assembling a Generator (1904) [A7]
- **tmdb_id**: 190738
- **run_id**: 01-grid-outage
- **pseudo命中分合计**: 10
- **per-agent 命中分**: A1:4, A7:6
- **相似度**: 0.4605
- **genres** / **language**: Documentary / en
- **overview**: A group of men work on various parts of a large generator, assembling the pieces
- **跳转**: https://themoviecosmos.com/movie/190738
- **also_baseline**: true
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, how-2, how-3, how-4, how-5] · sim=0.3998 · **命中分=6**
  - A1/p2: fragments=[how-2, how-3, how-4, how-5] · sim=0.4605 · **命中分=4**
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 09-cultural-backlash -->
<!-- retrieve: A1, A7 -->
<!-- overlap: A1 + creative (A4/A7) -->
<!-- pseudo命中分合计: 9 -->
### Alice's Adventures in Wonderland (1910) [A7]
- **tmdb_id**: 337191
- **run_id**: 09-cultural-backlash
- **pseudo命中分合计**: 9
- **per-agent 命中分**: A1:3, A7:6
- **相似度**: 0.6340
- **genres** / **language**: Adventure, Comedy, Fantasy / en
- **overview**: Made by the Edison Manufacturing Company and directed by Edwin S. Porter, the film starred Gladys Hulette as Alice. Being a silent film, naturally all of Lewis Carroll's nonsensical prose could not be used, and, being only a one-reel picture, most of Carroll's memorable characters in his original 1865 novel similarly could not be included. What was used in the film was faithful in spirit to Carroll, and in design to the original John Tenniel illustrations. Variety complimented the picture by comparing it favorably to the "foreign" film fantasies then flooding American cinemas.
- **跳转**: https://themoviecosmos.com/movie/337191
- **also_baseline**: true
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.6340 · **命中分=6**
  - A1/p1: fragments=[how-0, why-0, result-0] · sim=0.6042 · **命中分=3**
- **共振分**: 0  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 02-corporate-layoff -->
<!-- retrieve: A1, A2 -->
<!-- overlap: includes A2 -->
<!-- pseudo命中分合计: 8 -->
### Mirreyes contra Godínez 2: El retiro (2022) [A2]
- **tmdb_id**: 1002695
- **run_id**: 02-corporate-layoff
- **pseudo命中分合计**: 8
- **per-agent 命中分**: A1:3, A2:5
- **相似度**: 0.4955
- **genres** / **language**: Comedy / es
- **overview**: A divided team heads to a corporate retreat after receiving an enticing proposal. During their time away, they must overcome their differences and find a way to reunite.
- **跳转**: https://themoviecosmos.com/movie/1002695
- **also_baseline**: true
- **命中视角/碎片**:
  - A2/p1: fragments=[why-0, why-1, why-2] · sim=0.4955 · **命中分=3**
  - A2/p3: fragments=[result-0, result-1] · sim=0.4781 · **命中分=2**
  - A1/p2: fragments=[why-0, how-3, result-0] · sim=0.4797 · **命中分=3**
- **共振分**: 1  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 03-election-upset -->
<!-- retrieve: A1, A2 -->
<!-- overlap: includes A2 -->
<!-- pseudo命中分合计: 8 -->
### Machete (2010) [A2]
- **tmdb_id**: 23631
- **run_id**: 03-election-upset
- **pseudo命中分合计**: 8
- **per-agent 命中分**: A1:5, A2:3
- **相似度**: 0.4699
- **genres** / **language**: Action, Comedy, Thriller / en
- **overview**: After being set-up and betrayed by the man who hired him to assassinate a Texas Senator, an ex-Federale launches a brutal rampage of revenge against his former boss.
- **跳转**: https://themoviecosmos.com/movie/23631
- **also_baseline**: true
- **命中视角/碎片**:
  - A2/p3: fragments=[result-0, result-1, result-2] · sim=0.4699 · **命中分=3**
  - A1/p2: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.4548 · **命中分=5**
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 05-climate-disaster -->
<!-- retrieve: A1, A2 -->
<!-- overlap: includes A2 -->
<!-- pseudo命中分合计: 7 -->
### Poem of the Sea (1958) [A2]
- **tmdb_id**: 257637
- **run_id**: 05-climate-disaster
- **pseudo命中分合计**: 7
- **per-agent 命中分**: A1:4, A2:3
- **相似度**: 0.5439
- **genres** / **language**: Drama / ru
- **overview**: A Soviet dam project means that many old Ukrainian villages will end up under water. There are conflicts between the dam engineers and villagers who don't want to move.
- **跳转**: https://themoviecosmos.com/movie/257637
- **also_baseline**: true
- **命中视角/碎片**:
  - A2/p1: fragments=[why-0, how-0, result-1] · sim=0.5439 · **命中分=3**
  - A1/p3: fragments=[how-0, result-1, result-2, result-4] · sim=0.5202 · **命中分=4**
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 07-migration-border -->
<!-- retrieve: A1, A2 -->
<!-- overlap: includes A2 -->
<!-- pseudo命中分合计: 6 -->
### Transpecos (2016) [A2]
- **tmdb_id**: 381018
- **run_id**: 07-migration-border
- **pseudo命中分合计**: 6
- **per-agent 命中分**: A1:4, A2:2
- **相似度**: 0.5000
- **genres** / **language**: Thriller / en
- **overview**: For three US Border Patrol agents, the contents of one car reveal an insidious plot within their own ranks. The next 24 hours may cost them their lives.
- **跳转**: https://themoviecosmos.com/movie/381018
- **also_baseline**: true
- **命中视角/碎片**:
  - A2/p2: fragments=[how-0, how-1] · sim=0.4354 · **命中分=2**
  - A1/p1: fragments=[how-0, how-1] · sim=0.5000 · **命中分=2**
  - A1/p3: fragments=[result-1, result-2] · sim=0.4925 · **命中分=2**
- **共振分**: 2  <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**: 双重  <!-- 表层 / 结构 / 双重；0 分留空 -->
