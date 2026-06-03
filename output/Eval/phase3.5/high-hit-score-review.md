# High Pseudo Hit Score — Unified Review

## Criteria

### Pseudo 命中分（准入）

Candidate **enters this review** when **pseudo命中分合计 ≥ 5**
(single-agent hits included; multi-agent filter does not apply).

For each hit line under **命中视角/碎片**, count entries in `fragments=[...]`
— **each fragment id = 1 point** for that pseudo.

- **Candidate 总分** (`pseudo命中分合计`) = sum of pseudo 命中分 across all hit lines.
- Shown inline per line, e.g. `A2/p1: fragments=[...] · sim=... · **命中分=3**`.

### Sources

- **Primary:** `hit_sources` in each run's `retrieve.json` (fragment arrays).
- **Editor fields:** 共振分 / 共振类型 are placeholders only (not filled by this script).

- **Generation date:** 2026-06-02
- **Total candidates (≥5):** 91
- **Runs scanned:** 10

## Summary table (sorted by pseudo命中分合计 ↓)

| rank | run_id | tmdb_id | title | 总分 | agents |
| ---: | --- | ---: | --- | ---: | --- |
| 1 | 01-grid-outage | 429918 | Survival Family | 17 | A7 |
| 2 | 06-tech-monopoly | 888917 | Lords of Scam | 17 | A1 |
| 3 | 08-sports-underdog | 32007 | Hurricane Season | 15 | A7 |
| 4 | 06-tech-monopoly | 1229915 | Dead Mail | 14 | A7 |
| 5 | 10-whistleblower-leak | 20777 | The Killing Room | 14 | A1 |
| 6 | 06-tech-monopoly | 30858 | Terra Nova | 13 | A4 |
| 7 | 01-grid-outage | 190738 | Assembling a Generator | 10 | A7 |
| 8 | 03-election-upset | 37593 | Lone Star | 9 | A1 |
| 9 | 05-climate-disaster | 19196 | The Wild Men of Kurdistan | 9 | A7 |
| 10 | 05-climate-disaster | 121676 | Inescapable | 9 | A7 |
| 11 | 08-sports-underdog | 444218 | Three Seconds | 9 | A1 |
| 12 | 09-cultural-backlash | 197796 | Beauty and the Beast | 9 | A4 |
| 13 | 09-cultural-backlash | 337191 | Alice's Adventures in Wonderland | 9 | A7 |
| 14 | 09-cultural-backlash | 1047128 | Apolonia, Apolonia | 9 | A1 |
| 15 | 01-grid-outage | 616180 | Jim Button and the Wild 13 | 8 | A4 |
| 16 | 01-grid-outage | 1028769 | Stormskerry Maja | 8 | A4 |
| 17 | 02-corporate-layoff | 79386 | Les Charlots en délire | 8 | A1 |
| 18 | 02-corporate-layoff | 1002695 | Mirreyes contra Godínez 2: El retiro | 8 | A2 |
| 19 | 03-election-upset | 9451 | Election | 8 | A1 |
| 20 | 03-election-upset | 23631 | Machete | 8 | A2 |
| 21 | 03-election-upset | 27993 | National Lampoon's Senior Trip | 8 | A7 |
| 22 | 08-sports-underdog | 5693 | Hoosiers | 8 | A1 |
| 23 | 01-grid-outage | 82887 | Air Collision | 7 | A1 |
| 24 | 01-grid-outage | 841793 | Stranded | 7 | A4 |
| 25 | 01-grid-outage | 976854 | I Told You So | 7 | A4 |
| 26 | 02-corporate-layoff | 5595 | Fermat's Room | 7 | A7 |
| 27 | 02-corporate-layoff | 56589 | The Seventh Company Outdoors | 7 | A1 |
| 28 | 02-corporate-layoff | 965244 | Ghost in the Shell: SAC_2045 Sustainable War | 7 | A7 |
| 29 | 03-election-upset | 2100 | The Last Castle | 7 | A4 |
| 30 | 03-election-upset | 8441 | The Man of the Year | 7 | A4 |
| 31 | 03-election-upset | 264518 | Judge Archer | 7 | A4 |
| 32 | 03-election-upset | 303657 | Red Hot Tires | 7 | A4 |
| 33 | 03-election-upset | 492606 | Game of Thrones - Conquest & Rebellion: An Animated History of the Seven Kingdoms | 7 | A4 |
| 34 | 03-election-upset | 929170 | Honor Society | 7 | A4 |
| 35 | 05-climate-disaster | 116333 | Bravo Two Zero | 7 | A7 |
| 36 | 05-climate-disaster | 257637 | Poem of the Sea | 7 | A2 |
| 37 | 05-climate-disaster | 512954 | Leaving Afghanistan | 7 | A7 |
| 38 | 06-tech-monopoly | 15152 | OSS 117: Cairo, Nest of Spies | 7 | A7 |
| 39 | 06-tech-monopoly | 40815 | On Guard | 7 | A4 |
| 40 | 06-tech-monopoly | 42658 | Helen of Troy | 7 | A4 |
| 41 | 06-tech-monopoly | 58926 | Speaking of Murder | 7 | A4 |
| 42 | 06-tech-monopoly | 193982 | The Stenographer's Friend; Or, What Was Accomplished by an Edison Business Phonograph | 7 | A7 |
| 43 | 06-tech-monopoly | 231131 | Intérieur d'une imprimerie (tirage d'une épreuve) | 7 | A7 |
| 44 | 06-tech-monopoly | 379088 | Attack on Titan: Crimson Bow and Arrow | 7 | A4 |
| 45 | 06-tech-monopoly | 463272 | Johnny English Strikes Again | 7 | A7 |
| 46 | 06-tech-monopoly | 595924 | Liberté | 7 | A4 |
| 47 | 01-grid-outage | 26130 | Summer Time Machine Blues | 6 | A7 |
| 48 | 01-grid-outage | 54801 | Night of the Big Heat | 6 | A4 |
| 49 | 01-grid-outage | 919873 | Arctic Void | 6 | A4 |
| 50 | 05-climate-disaster | 210219 | Jet Stream | 6 | A7 |
| 51 | 05-climate-disaster | 390281 | Ustica: The Missing Paper | 6 | A7 |
| 52 | 07-migration-border | 381018 | Transpecos | 6 | A2 |
| 53 | 08-sports-underdog | 13074 | Resurrecting the Champ | 6 | A7 |
| 54 | 08-sports-underdog | 27420 | Graduation Day | 6 | A7 |
| 55 | 08-sports-underdog | 126644 | By the Law | 6 | A7 |
| 56 | 09-cultural-backlash | 28468 | The Key | 6 | A7 |
| 57 | 09-cultural-backlash | 51477 | The Big Dream | 6 | A7 |
| 58 | 09-cultural-backlash | 193315 | Too Much Johnson | 6 | A7 |
| 59 | 09-cultural-backlash | 197082 | Venus in Fur | 6 | A7 |
| 60 | 09-cultural-backlash | 552687 | Wotakoi: Love is Hard for Otaku | 6 | A7 |
| 61 | 10-whistleblower-leak | 335490 | The Idealist | 6 | A7 |
| 62 | 10-whistleblower-leak | 1229915 | Dead Mail | 6 | A7 |
| 63 | 01-grid-outage | 678 | Out of the Past | 5 | A1 |
| 64 | 01-grid-outage | 398395 | Timecode | 5 | A7 |
| 65 | 01-grid-outage | 441894 | Baadshaho | 5 | A7 |
| 66 | 01-grid-outage | 477652 | The Miracles of the Namiya General Store | 5 | A7 |
| 67 | 02-corporate-layoff | 5630 | The Terrible People | 5 | A4 |
| 68 | 02-corporate-layoff | 11094 | Pepe, der Paukerschreck | 5 | A7 |
| 69 | 02-corporate-layoff | 57278 | The Hexer | 5 | A4 |
| 70 | 02-corporate-layoff | 60190 | Beyond Darkness | 5 | A4 |
| 71 | 02-corporate-layoff | 61933 | The Light Bulb Conspiracy | 5 | A4 |
| 72 | 02-corporate-layoff | 66878 | Home Made Home | 5 | A4 |
| 73 | 02-corporate-layoff | 209504 | Bounty Killer | 5 | A4 |
| 74 | 02-corporate-layoff | 1032394 | Stalled | 5 | A7 |
| 75 | 05-climate-disaster | 53151 | Joe the King | 5 | A2 |
| 76 | 05-climate-disaster | 58637 | Valley of the Wolves: Palestine | 5 | A1 |
| 77 | 05-climate-disaster | 260372 | Bermuda Tentacles | 5 | A1 |
| 78 | 05-climate-disaster | 514886 | Spitak | 5 | A2 |
| 79 | 06-tech-monopoly | 12592 | The Olsen Gang Goes to War | 5 | A1 |
| 80 | 07-migration-border | 14161 | 2012 | 5 | A4 |
| 81 | 07-migration-border | 212986 | Exploding Sun | 5 | A4 |
| 82 | 08-sports-underdog | 14120 | End of the Spear | 5 | A4 |
| 83 | 08-sports-underdog | 26130 | Summer Time Machine Blues | 5 | A7 |
| 84 | 08-sports-underdog | 122917 | The Hobbit: The Battle of the Five Armies | 5 | A4 |
| 85 | 08-sports-underdog | 146131 | Mammals | 5 | A4 |
| 86 | 08-sports-underdog | 372751 | Code Geass: Akito the Exiled 5: To Beloved Ones | 5 | A4 |
| 87 | 08-sports-underdog | 651249 | True: Winter Wishes | 5 | A4 |
| 88 | 08-sports-underdog | 1376412 | La Guerre des Prix | 5 | A4 |
| 89 | 09-cultural-backlash | 97481 | The Confession | 5 | A4 |
| 90 | 10-whistleblower-leak | 34044 | Waco: The Rules of Engagement | 5 | A7 |
| 91 | 10-whistleblower-leak | 1447971 | Scare Out | 5 | A7 |

## Candidates (global sort by pseudo命中分合计 ↓)

**Count:** 91 candidate(s)

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 17 -->
### Survival Family (2017) [A7]
- **tmdb_id**: 429918
- **相似度**: 0.5681
- **genres** / **language**: Comedy, Drama, Adventure / ja
- **overview**: A world wide electrical outage occurs. Everything that requires electricity comes to a stop. Tokyo is nearly ruined. Yoshiyuki Suzuki decides to escape from Tokyo with his family.
- **跳转**: https://themoviecosmos.com/movie/429918
- **also_baseline**: true
- **命中视角/碎片**:
  - A7/p3: fragments=[how-4, how-5, result-0, result-1, result-2] · sim=0.4611 · **命中分=5**
  - A1/p1: fragments=[how-0, how-1, how-2, how-3, how-4] · sim=0.5681 · **命中分=5**
  - A1/p3: fragments=[how-0, how-1, how-2, how-3, how-4, how-5, result-0] · sim=0.4809 · **命中分=7**
- **pseudo命中分合计**: 17
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 17 -->
### Lords of Scam (2021) [baseline only]
- **tmdb_id**: 888917
- **相似度**: 0.4427
- **genres** / **language**: Documentary, Crime / fr
- **overview**: This documentary traces the rise and crash of scammers who conned the EU carbon quota system and pocketed millions before turning on one another.
- **跳转**: https://themoviecosmos.com/movie/888917
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0] · sim=0.4427 · **命中分=6**
  - A1/p2: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.4405 · **命中分=6**
  - A1/p3: fragments=[how-1, how-2, how-3, result-0, result-1] · sim=0.3835 · **命中分=5**
- **pseudo命中分合计**: 17
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 15 -->
### Hurricane Season (2010) [A7]
- **tmdb_id**: 32007
- **相似度**: 0.5082
- **genres** / **language**: Drama / en
- **overview**: Based on true events amid the wreckage and chaos dealt by Hurricane Katrina; one basketball coach in Marrero, Louisiana just will not give up. Coach Al Collins, gathers other players from hard-hit schools and builds a team actually worthy enough to go to the state playoffs.
- **跳转**: https://themoviecosmos.com/movie/32007
- **also_baseline**: true
- **命中视角/碎片**:
  - A7/p3: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5082 · **命中分=6**
  - A1/p2: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.5020 · **命中分=5**
  - A1/p3: fragments=[how-0, how-1, why-0, result-1] · sim=0.4986 · **命中分=4**
- **pseudo命中分合计**: 15
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 14 -->
### Dead Mail (2024) [A7]
- **tmdb_id**: 1229915
- **相似度**: 0.5284
- **genres** / **language**: Crime, Thriller, Music, Mystery, Horror / en
- **overview**: An ominous help note finds its way to a 1980s post office, connecting a dead letter investigator to a kidnapped keyboard technician.
- **跳转**: https://themoviecosmos.com/movie/1229915
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5284 · **命中分=7**
  - A7/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5050 · **命中分=7**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 14 -->
### The Killing Room (2009) [baseline only]
- **tmdb_id**: 20777
- **相似度**: 0.5313
- **genres** / **language**: Thriller, Drama / en
- **overview**: Four volunteers sign up for what initially appears to be a typical paid research study, only to discover that they've unwittingly become involved with a classified government program that was said to have been terminated nearly two decades ago.
- **跳转**: https://themoviecosmos.com/movie/20777
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, why-0, how-2, how-3, how-4] · sim=0.4537 · **命中分=6**
  - A1/p2: fragments=[why-0, result-0, result-1, result-2] · sim=0.5313 · **命中分=4**
  - A1/p3: fragments=[result-0, result-1, result-2, result-3] · sim=0.4241 · **命中分=4**
- **pseudo命中分合计**: 14
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 13 -->
### Terra Nova (2008) [A4]
- **tmdb_id**: 30858
- **相似度**: 0.5373
- **genres** / **language**: Drama, Thriller, Action / ru
- **overview**: A story, which takes place in 2013, describes the world overflowing with "dangerous" criminals due to the official termination of death penalty. The UN "blue helmets" under the directive from the central authority (i.e., One World Government) decided to conduct a social "experiment" by forcibly dumping the outlaws on the deserted island...
- **跳转**: https://themoviecosmos.com/movie/30858
- **also_baseline**: true
- **命中视角/碎片**:
  - A4/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5373 · **命中分=7**
  - A1/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0] · sim=0.4402 · **命中分=6**
- **pseudo命中分合计**: 13
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 10 -->
### Assembling a Generator (1904) [A7]
- **tmdb_id**: 190738
- **相似度**: 0.4605
- **genres** / **language**: Documentary / en
- **overview**: A group of men work on various parts of a large generator, assembling the pieces
- **跳转**: https://themoviecosmos.com/movie/190738
- **also_baseline**: true
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, how-2, how-3, how-4, how-5] · sim=0.3998 · **命中分=6**
  - A1/p2: fragments=[how-2, how-3, how-4, how-5] · sim=0.4605 · **命中分=4**
- **pseudo命中分合计**: 10
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 9 -->
### Lone Star (1952) [baseline only]
- **tmdb_id**: 37593
- **相似度**: 0.5149
- **genres** / **language**: Western / en
- **overview**: Cattle baron Devereaux Burke is enlisted by an aging Andrew Jackson to dissuade Sam Houston from establishing Texas as a republic. Burke must fight state senator Thomas Craden, in the process winning the heart of Craden's newspaper-editor girlfriend Martha Ronda.
- **跳转**: https://themoviecosmos.com/movie/37593
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[why-0, how-0, how-1, how-2] · sim=0.5149 · **命中分=4**
  - A1/p2: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5086 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 9 -->
### The Wild Men of Kurdistan (1965) [A7]
- **tmdb_id**: 19196
- **相似度**: 0.5399
- **genres** / **language**: Adventure / de
- **overview**: After dealing with the Shut in the Balkans, Kara Ben-Nemsi ('Karl the German') receives a firman (precious passport) from the padishah (Ottoman sultan) before he continues his travels through Kurdistan. Achmed El Corda, the son of Halef's Hadedhin Beduin tribe's sheik Mohammed Emin, has been captured by the machredsh (Turkish governor) of Mossul for resisting water seizure by his Turkish troops. Kara takes charge of the rescue.
- **跳转**: https://themoviecosmos.com/movie/19196
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-4, result-5] · sim=0.5399 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 9 -->
### Inescapable (2012) [A7]
- **tmdb_id**: 121676
- **相似度**: 0.5229
- **genres** / **language**: Thriller, Romance / en
- **overview**: Twenty-five years ago Adib, a promising young officer in the Syrian military police, suddenly left Damascus under suspicious circumstances. Abandoning the love of his life Fatima, he made his way to Canada and wiped the slate clean. When his daughter Muna suddenly disappears in Damascus, his past threatens to violently catch up to him. Teaming up with a Canadian emissary, Adib must now confront the turmoil he thought he left behind in order to find Muna.
- **跳转**: https://themoviecosmos.com/movie/121676
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1, result-4, result-5] · sim=0.5229 · **命中分=9**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 9 -->
### Three Seconds (2017) [baseline only]
- **tmdb_id**: 444218
- **相似度**: 0.4796
- **genres** / **language**: Drama / ru
- **overview**: The story is set at the 1972 Munich Olympics where the U.S. team lost the basketball championship for the first time in 36 years. The final moments of the final game have become one of the most controversial events in Olympic history. With play tied, the score table horn sounded during a second free throw attempt that put the U.S. ahead by one. But the Soviets claimed they had called for a time out before the basket and confusion ensued. The clock was set back by three seconds twice in a row and the Russians finally prevailed at the very last. The U.S. protested, but a jury decided in the USSR’s favor and Team USA voted unanimously to refuse its silver medals. The Soviet players have been treated as heroes at home.
- **跳转**: https://themoviecosmos.com/movie/444218
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.4796 · **命中分=4**
  - A1/p2: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.4466 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 9 -->
### Beauty and the Beast (2014) [A4]
- **tmdb_id**: 197796
- **相似度**: 0.5944
- **genres** / **language**: Fantasy, Romance / fr
- **overview**: Forced to face the cruel side of life, a devastated, bankrupt merchant chances upon the enchanted castle of a hideous creature, the mere sight of it chills the bone to the marrow. There, a fate worse than death awaits the poor father-of-six, who, after plucking a sweet-scented rose from the repulsive master's verdant garden, must do the impossible: permit his compassionate daughter, Belle, to take his place and pay for the sins of her parent. Now, an impenetrable mystery shrouds the haunted mansion, and, as repugnance gradually turns into affection, only true love could break the spell.
- **跳转**: https://themoviecosmos.com/movie/197796
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, how-0, how-1, result-0] · sim=0.5788 · **命中分=4**
  - A4/p2: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5944 · **命中分=5**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 9 -->
### Alice's Adventures in Wonderland (1910) [A7]
- **tmdb_id**: 337191
- **相似度**: 0.6340
- **genres** / **language**: Adventure, Comedy, Fantasy / en
- **overview**: Made by the Edison Manufacturing Company and directed by Edwin S. Porter, the film starred Gladys Hulette as Alice. Being a silent film, naturally all of Lewis Carroll's nonsensical prose could not be used, and, being only a one-reel picture, most of Carroll's memorable characters in his original 1865 novel similarly could not be included. What was used in the film was faithful in spirit to Carroll, and in design to the original John Tenniel illustrations. Variety complimented the picture by comparing it favorably to the "foreign" film fantasies then flooding American cinemas.
- **跳转**: https://themoviecosmos.com/movie/337191
- **also_baseline**: true
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.6340 · **命中分=6**
  - A1/p1: fragments=[how-0, why-0, result-0] · sim=0.6042 · **命中分=3**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 9 -->
### Apolonia, Apolonia (2023) [baseline only]
- **tmdb_id**: 1047128
- **相似度**: 0.6170
- **genres** / **language**: Documentary / da
- **overview**: When Danish filmmaker Lea Glob first portrayed Apolonia Sokol in 2009, she appeared to be leading a storybook life. The talented Apolonia was born in an underground theater in Paris and grew up in an artists’ community—the ultimate bohemian existence. In her 20s, she studied at the Beaux-Arts de Paris, one of the most prestigious art academies in Europe. Over the years, Lea Glob kept returning to film the charismatic Apolonia and a special bond developed between the two young women.
- **跳转**: https://themoviecosmos.com/movie/1047128
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, why-0, result-0] · sim=0.6170 · **命中分=3**
  - A1/p2: fragments=[how-0, how-1, how-2] · sim=0.5425 · **命中分=3**
  - A1/p3: fragments=[how-0, why-1, result-0] · sim=0.5693 · **命中分=3**
- **pseudo命中分合计**: 9
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 8 -->
### Jim Button and the Wild 13 (2020) [A4]
- **tmdb_id**: 616180
- **相似度**: 0.5178
- **genres** / **language**: Adventure, Family, Fantasy / de
- **overview**: A year has gone by since Jim Button and his best friend, the engine driver Luke, returned from their dangerous adventure in Dragon City. Life on Morrowland goes its leisurely way again. Suddenly, dark clouds are gathering over the tranquil island of Morrowland: the notorious pirate gang "The Wild 13" has learned that the dragon Mrs Grindtooth has been conquered by Jim and Luke and now swears revenge.  To protect Morrowland from another threat, the two of them set off with their steam engines Emma and Molly on a dangerous journey where they meet old friends like princess Li Si, Mr. Tur Tur and Nepomuk and make new friends with Sursulapichi, a real mermaid. On their adventure, Jim's most fervent wish might also come true: to find out the truth about his mysterious origins.
- **跳转**: https://themoviecosmos.com/movie/616180
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p3: fragments=[how-0, how-1, how-2, how-3, how-4, result-0, result-1, result-2] · sim=0.5178 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 8 -->
### Stormskerry Maja (2024) [A4]
- **tmdb_id**: 1028769
- **相似度**: 0.5007
- **genres** / **language**: Drama / sv
- **overview**: Maja and Janne move to the barren and remote island of Stormskerry, where survival is a daily struggle. Growing up in a world of old values, Maja becomes aware of a new era: a woman can be an equal partner instead of a mere bystander. The couple have children, and life is good until trouble sets in: war arrives on the island, Janne is forced to flee from the English troops, and Maja and the children are imprisoned. The family also faces many financial difficulties and death. Years pass, but Maja remains strong and stays in Stormskerry despite all the hardships and difficulties.
- **跳转**: https://themoviecosmos.com/movie/1028769
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p3: fragments=[how-0, how-1, how-2, how-3, how-4, result-0, result-1, result-2] · sim=0.5007 · **命中分=8**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 8 -->
### Les Charlots en délire (1979) [baseline only]
- **tmdb_id**: 79386
- **相似度**: 0.4775
- **genres** / **language**: Action, Comedy / fr
- **overview**: Gérard, CEO of the factory "La voix du peuple", decides to close his factory by dismissing all his staff, starting with Jean Barbier, the chief of staff, and Phil Dechambre.
- **跳转**: https://themoviecosmos.com/movie/79386
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[why-2, how-0, how-1, how-2] · sim=0.4308 · **命中分=4**
  - A1/p3: fragments=[why-1, how-0, result-0, result-1] · sim=0.4775 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 8 -->
### Mirreyes contra Godínez 2: El retiro (2022) [A2]
- **tmdb_id**: 1002695
- **相似度**: 0.4955
- **genres** / **language**: Comedy / es
- **overview**: A divided team heads to a corporate retreat after receiving an enticing proposal. During their time away, they must overcome their differences and find a way to reunite.
- **跳转**: https://themoviecosmos.com/movie/1002695
- **also_baseline**: true
- **命中视角/碎片**:
  - A2/p1: fragments=[why-0, why-1, why-2] · sim=0.4955 · **命中分=3**
  - A2/p3: fragments=[result-0, result-1] · sim=0.4781 · **命中分=2**
  - A1/p2: fragments=[why-0, how-3, result-0] · sim=0.4797 · **命中分=3**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 8 -->
### Election (1999) [baseline only]
- **tmdb_id**: 9451
- **相似度**: 0.5539
- **genres** / **language**: Comedy, Drama / en
- **overview**: Tracy Flick is running unopposed for this year’s high school student election. But Jim McAllister has a different plan. Partly to establish a more democratic election, and partly to satisfy some deep personal anger toward Tracy, Jim talks football player Paul Metzler to run for president as well.
- **跳转**: https://themoviecosmos.com/movie/9451
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[why-0, how-0, how-1, how-2] · sim=0.4981 · **命中分=4**
  - A1/p3: fragments=[why-0, how-2, result-0, result-2] · sim=0.5539 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 8 -->
### Machete (2010) [A2]
- **tmdb_id**: 23631
- **相似度**: 0.4699
- **genres** / **language**: Action, Comedy, Thriller / en
- **overview**: After being set-up and betrayed by the man who hired him to assassinate a Texas Senator, an ex-Federale launches a brutal rampage of revenge against his former boss.
- **跳转**: https://themoviecosmos.com/movie/23631
- **also_baseline**: true
- **命中视角/碎片**:
  - A2/p3: fragments=[result-0, result-1, result-2] · sim=0.4699 · **命中分=3**
  - A1/p2: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.4548 · **命中分=5**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 8 -->
### National Lampoon's Senior Trip (1995) [A7]
- **tmdb_id**: 27993
- **相似度**: 0.5227
- **genres** / **language**: Comedy / en
- **overview**: While on detention, a group of misfits and slackers have to write a letter to the President explaining what is wrong with the education system. There is only one problem, the President loves it! Hence, the group must travel to Washington to meet the Main Man.
- **跳转**: https://themoviecosmos.com/movie/27993
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-0, how-0, how-1, how-2] · sim=0.5227 · **命中分=4**
  - A7/p3: fragments=[why-0, how-0, how-1, how-2] · sim=0.5005 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 8 -->
### Hoosiers (1986) [baseline only]
- **tmdb_id**: 5693
- **相似度**: 0.5030
- **genres** / **language**: Drama, Family / en
- **overview**: Failed college coach Norman Dale gets a chance at redemption when he is hired to coach a high school basketball team in a tiny Indiana town. After a teacher persuades star player Jimmy Chitwood to quit and focus on his long-neglected studies, Dale struggles to develop a winning team in the face of community criticism for his temper and his unconventional choice of assistant coach: Shooter, a notorious alcoholic.
- **跳转**: https://themoviecosmos.com/movie/5693
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, result-0] · sim=0.4960 · **命中分=4**
  - A1/p3: fragments=[how-0, how-1, why-0, result-1] · sim=0.5030 · **命中分=4**
- **pseudo命中分合计**: 8
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 7 -->
### Air Collision (2012) [baseline only]
- **tmdb_id**: 82887
- **相似度**: 0.4525
- **genres** / **language**: Action, Thriller / en
- **overview**: When a solar storm wipes out the air traffic control system, Air Force One and a passenger jet liner are locked on a collision course in the skies above the midwest.
- **跳转**: https://themoviecosmos.com/movie/82887
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p3: fragments=[how-0, how-1, how-2, how-3, how-4, how-5, result-0] · sim=0.4525 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 7 -->
### Stranded (2021) [A4]
- **tmdb_id**: 841793
- **相似度**: 0.5137
- **genres** / **language**: Drama / pt
- **overview**: Tensions run high while food runs low as six influencers find themselves stranded on a secluded island after plans for a weekend escape go awry.
- **跳转**: https://themoviecosmos.com/movie/841793
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[why-0, how-1, how-2, how-3, how-4, how-5, why-2] · sim=0.5137 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 7 -->
### I Told You So (2024) [A4]
- **tmdb_id**: 976854
- **相似度**: 0.5176
- **genres** / **language**: Drama / it
- **overview**: In Rome, during a January weekend a sudden heatwave arrives. The sun is initially pleasant, but the heat quickly escalates to a frightening degree, resulting in people and animals losing self-control.
- **跳转**: https://themoviecosmos.com/movie/976854
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[why-0, how-1, how-2, how-3, how-4, how-5, why-2] · sim=0.5176 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 7 -->
### Fermat's Room (2007) [A7]
- **tmdb_id**: 5595
- **相似度**: 0.4736
- **genres** / **language**: Mystery, Thriller / es
- **overview**: Four mathematicians are imprisoned in a shrinking room; with the walls closing in, they must try anything to escape this fatal puzzle.
- **跳转**: https://themoviecosmos.com/movie/5595
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4736 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 7 -->
### The Seventh Company Outdoors (1977) [baseline only]
- **tmdb_id**: 56589
- **相似度**: 0.5012
- **genres** / **language**: Comedy / fr
- **overview**: The third part of Seventh Company adventures.
- **跳转**: https://themoviecosmos.com/movie/56589
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p2: fragments=[why-0, how-3, result-0] · sim=0.5012 · **命中分=3**
  - A1/p3: fragments=[why-1, how-0, result-0, result-1] · sim=0.4549 · **命中分=4**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 7 -->
### Ghost in the Shell: SAC_2045 Sustainable War (2021) [A7]
- **tmdb_id**: 965244
- **相似度**: 0.5089
- **genres** / **language**: Animation, Action, Science Fiction / ja
- **overview**: In the year 2045, after an economic disaster known as the Synchronized Global Default, rapid developments in AI propelled the world to enter a state of "Sustainable War". However, the public is not aware of the threat that AI has towards the human race.  A compilation film with newly added footage.
- **跳转**: https://themoviecosmos.com/movie/965244
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[why-1, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5089 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 7 -->
### The Last Castle (2001) [A4]
- **tmdb_id**: 2100
- **相似度**: 0.5605
- **genres** / **language**: Action, Drama, Thriller / en
- **overview**: A court-martialed general rallies together 1200 inmates to rise against the system that put him away.
- **跳转**: https://themoviecosmos.com/movie/2100
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p3: fragments=[why-0, how-0, how-1, how-2, result-0, result-1, result-2] · sim=0.5605 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 7 -->
### The Man of the Year (2003) [A4]
- **tmdb_id**: 8441
- **相似度**: 0.5428
- **genres** / **language**: Drama, Crime, Thriller / pt
- **overview**: Maiquél has lost a bet and dyed his hair blond. This  seemingly innocuous event triggers a head-on collision with destiny in which he goes from nobody to hero to outlaw — all in 24 hours.
- **跳转**: https://themoviecosmos.com/movie/8441
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[why-0, how-0, how-1, how-2, result-0, result-1, result-2] · sim=0.5428 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 7 -->
### Judge Archer (2016) [A4]
- **tmdb_id**: 264518
- **相似度**: 0.5332
- **genres** / **language**: Action, Drama / zh
- **overview**: The spear signifies political power, the arrow personal ambition. What happens when the two collide?
- **跳转**: https://themoviecosmos.com/movie/264518
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[why-0, how-0, how-1, how-2, result-0, result-1, result-2] · sim=0.5332 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 7 -->
### Red Hot Tires (1935) [A4]
- **tmdb_id**: 303657
- **相似度**: 0.5242
- **genres** / **language**: Drama, Crime, Romance / en
- **overview**: An escaped convict redeems himself by becoming an auto racing champion.
- **跳转**: https://themoviecosmos.com/movie/303657
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1, result-2] · sim=0.5242 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 7 -->
### Game of Thrones - Conquest & Rebellion: An Animated History of the Seven Kingdoms (2017) [A4]
- **tmdb_id**: 492606
- **相似度**: 0.5598
- **genres** / **language**: Animation, Fantasy, War / en
- **overview**: A powerful ruler from House Targaryen begins a campaign to unite a fractured continent ruled by seven competing families. With the aid of formidable dragons, the conquest reshapes the balance of power and leads to the creation of a single throne.
- **跳转**: https://themoviecosmos.com/movie/492606
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p3: fragments=[why-0, how-0, how-1, how-2, result-0, result-1, result-2] · sim=0.5598 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 03-election-upset -->
<!-- pseudo命中分合计: 7 -->
### Honor Society (2022) [A4]
- **tmdb_id**: 929170
- **相似度**: 0.5284
- **genres** / **language**: Comedy / en
- **overview**: Honor is an ambitious high school senior whose sole focus is getting into Harvard, assuming she can first score the coveted recommendation from her guidance counselor, Mr. Calvin. Willing to do whatever it takes, Honor concocts a Machiavellian-like plan to take down her top three student competitors, until things take a turn when she unexpectedly falls for her biggest competition, Michael.
- **跳转**: https://themoviecosmos.com/movie/929170
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1, result-2] · sim=0.5284 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 7 -->
### Bravo Two Zero (1999) [A7]
- **tmdb_id**: 116333
- **相似度**: 0.5065
- **genres** / **language**: War, Action, TV Movie / en
- **overview**: When an elite eight-man British SAS team is dropped behind enemy lines, their mission is clear: take out Saddam Hussein's SCUD missile systems. But when communications are cut and the team finds themselves surrounded by Saddam's army, their only hope is to risk capture and torture in a desperate 185-kilometer run to the Syrian border.  Based on the true story of a British Special Forces unit behind enemy lines during the Gulf War, Bravo Two Zero explores the tragedies and triumphs of men taken to the edge of survival in the Persian Gulf War.
- **跳转**: https://themoviecosmos.com/movie/116333
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[how-0, how-1, how-2, how-3, result-2, result-3, result-4] · sim=0.5065 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 7 -->
### Poem of the Sea (1958) [A2]
- **tmdb_id**: 257637
- **相似度**: 0.5439
- **genres** / **language**: Drama / ru
- **overview**: A Soviet dam project means that many old Ukrainian villages will end up under water. There are conflicts between the dam engineers and villagers who don't want to move.
- **跳转**: https://themoviecosmos.com/movie/257637
- **also_baseline**: true
- **命中视角/碎片**:
  - A2/p1: fragments=[why-0, how-0, result-1] · sim=0.5439 · **命中分=3**
  - A1/p3: fragments=[how-0, result-1, result-2, result-4] · sim=0.5202 · **命中分=4**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 7 -->
### Leaving Afghanistan (2019) [A7]
- **tmdb_id**: 512954
- **相似度**: 0.4970
- **genres** / **language**: Drama, Action, War / ru
- **overview**: 1988-1989. The end of the Soviet-Afghan war. The USSR begins its withdrawal from Afghanistan. Soviet General Vasiliev's son - a pilot named Alexander gets kidnapped by the mujahideen after his airplane crashes. As a result the 108th motorized infantry division's long awaited return home gets put on hold for one last mission: bring the General's son back. Based on true events the previously untold story of the courageous and tragic withdrawal campaign (through the Salang pass) reveals the danger the horror and the complexity of human nature during wartime.
- **跳转**: https://themoviecosmos.com/movie/512954
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[how-0, how-1, how-2, how-3, result-2, result-3, result-4] · sim=0.4970 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### OSS 117: Cairo, Nest of Spies (2006) [A7]
- **tmdb_id**: 15152
- **相似度**: 0.4892
- **genres** / **language**: Crime, Action, Adventure, Comedy / fr
- **overview**: Set in 1955, French secret agent Hubert Bonisseur de La Bath/OSS 117 is sent to Cairo to investigate the disappearance of his best friend and fellow spy Jack Jefferson, only to stumble into a web of international intrigue.
- **跳转**: https://themoviecosmos.com/movie/15152
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4892 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### On Guard (1997) [A4]
- **tmdb_id**: 40815
- **相似度**: 0.5224
- **genres** / **language**: Adventure, Action, Drama / fr
- **overview**: France, 17th century, during the reign of Louis XIII. When a dear friend, the Duke of Nevers, is treacherously assassinated by a powerful relative, a skilled swordsman, the noble Henri de Lagardère, seeks his rightful vengeance as he tries to protect the innocent life of the duke's last heir.
- **跳转**: https://themoviecosmos.com/movie/40815
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5224 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### Helen of Troy (1956) [A4]
- **tmdb_id**: 42658
- **相似度**: 0.5542
- **genres** / **language**: Adventure, War, Romance, History / en
- **overview**: Prince Paris of Troy, shipwrecked on a mission to the king of Sparta, meets and falls for Queen Helen before he knows who she is. Rudely received by the royal Greeks, he must flee...but fate and their mutual passions lead him to take Helen along. This gives the Greeks just the excuse they need for much-desired war.
- **跳转**: https://themoviecosmos.com/movie/42658
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5542 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### Speaking of Murder (1957) [A4]
- **tmdb_id**: 58926
- **相似度**: 0.5323
- **genres** / **language**: Crime, Drama, Thriller / fr
- **overview**: Louis Bertain is the owner of a Paris garage which is the front for a robbery gang. He and his accomplices are careful to keep up a civic veneer by day, indulging in criminal activities only when "the red light is on" at night. This status quo is upset when one of the gang members becomes convinced that Louis' younger brother is a police informer.
- **跳转**: https://themoviecosmos.com/movie/58926
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5323 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### The Stenographer's Friend; Or, What Was Accomplished by an Edison Business Phonograph (1910) [A7]
- **tmdb_id**: 193982
- **相似度**: 0.4813
- **genres** / **language**: Drama / en
- **overview**: It's a busy day at the office, and the stenographer is exhausted from trying to keep up with the demands on her skills. Even when she stays late, she cannot catch up with all of the work. But then a man comes into the office to demonstrate the many advantages of the Edison System, his company's new business phonograph.
- **跳转**: https://themoviecosmos.com/movie/193982
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.4813 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### Intérieur d'une imprimerie (tirage d'une épreuve) (1899) [A7]
- **tmdb_id**: 231131
- **相似度**: 0.5195
- **genres** / **language**: Documentary / en
- **overview**: Within a printing (printing a test).
- **跳转**: https://themoviecosmos.com/movie/231131
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5195 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### Attack on Titan: Crimson Bow and Arrow (2014) [A4]
- **tmdb_id**: 379088
- **相似度**: 0.5312
- **genres** / **language**: Animation, Action, Adventure, Fantasy / ja
- **overview**: When man-eating Titans first appeared 100 years ago, humans found safety behind massive walls that stopped the giants in their tracks. But the safety they have had for so long is threatened when a colossal Titan smashes through the barriers, causing a flood of the giants into what had been the humans' safe zone.
- **跳转**: https://themoviecosmos.com/movie/379088
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5312 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### Johnny English Strikes Again (2018) [A7]
- **tmdb_id**: 463272
- **相似度**: 0.3999
- **genres** / **language**: Action, Adventure, Comedy / en
- **overview**: Disaster strikes when a criminal mastermind reveals the identities of all active undercover agents in Britain. The secret service can now rely on only one man - Johnny English. Currently teaching at a minor prep school, Johnny springs back into action to find the mysterious hacker. For this mission to succeed, he’ll need all of his skills - what few he has - as the man with yesterday’s analogue methods faces off against tomorrow’s digital technology.
- **跳转**: https://themoviecosmos.com/movie/463272
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.3999 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 7 -->
### Liberté (2019) [A4]
- **tmdb_id**: 595924
- **相似度**: 0.5346
- **genres** / **language**: Drama, History / fr
- **overview**: 1774, shortly before the French Revolution, somewhere between Potsdam and Berlin. Madame de Dumeval, the Duke de Tesis and the Duke de Wand, libertines expelled from the puritanical court of Louis XVI, seek the support of the legendary Duc de Walchen, German seducer and freethinker, lonely in a country where hypocrisy and false virtue reign. Their mission is to export libertinage, a philosophy of enlightenment founded on the rejection of moral boundaries and authorities, but moreover to find a safe place to pursue their errant games, where the quest for pleasure no longer obeys laws other than those dictated by unfulfilled desires.
- **跳转**: https://themoviecosmos.com/movie/595924
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p3: fragments=[why-0, how-0, how-1, how-2, how-3, result-0, result-1] · sim=0.5346 · **命中分=7**
- **pseudo命中分合计**: 7
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 6 -->
### Summer Time Machine Blues (2005) [A7]
- **tmdb_id**: 26130
- **相似度**: 0.3914
- **genres** / **language**: Comedy, Science Fiction / ja
- **overview**: The members of a sci-fi club accidentally spill Coke on the remote controller of an air-conditioner during summer and suddenly a time machine appears in their sweating bath-like clubroom.
- **跳转**: https://themoviecosmos.com/movie/26130
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, how-2, how-3, how-4, how-5] · sim=0.3914 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 6 -->
### Night of the Big Heat (1967) [A4]
- **tmdb_id**: 54801
- **相似度**: 0.5643
- **genres** / **language**: Science Fiction, Horror, Thriller / en
- **overview**: While mainland Britain shivers in deepest winter, the northern island of Fara bakes in the nineties, and the boys at the Met station have no more idea what is going on than the regulars at the Swan. Only a stand-offish visting scientist realizes space aliens are to blame.
- **跳转**: https://themoviecosmos.com/movie/54801
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[how-0, how-1, how-2, how-3, how-4, how-5] · sim=0.5643 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 6 -->
### Arctic Void (2022) [A4]
- **tmdb_id**: 919873
- **相似度**: 0.6125
- **genres** / **language**: Science Fiction, Thriller, Horror, Drama, Mystery / en
- **overview**: When the power mysteriously fails, and almost everyone vanishes from a small tourist vessel in the Arctic, fear becomes the master for the three who remain. Forced ashore, the men deteriorate in body and mind until a dark truth emerges that compels them to ally or perish.
- **跳转**: https://themoviecosmos.com/movie/919873
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[how-0, how-1, how-2, how-3, how-4, how-5] · sim=0.6125 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 6 -->
### Jet Stream (2013) [A7]
- **tmdb_id**: 210219
- **相似度**: 0.4985
- **genres** / **language**: Action, Adventure, Drama, Science Fiction, TV Movie / en
- **overview**: A TV weatherman tries to prove his theory that a series of unexplained catastrophes are the result of powerful winds found in the upper atmosphere coming down to ground level. His claims attract the attention of government scientists, who need his help to control the phenomena before it destroys all life on Earth (Locatetv.com)
- **跳转**: https://themoviecosmos.com/movie/210219
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[why-0, how-0, how-1, result-0, result-1, result-2] · sim=0.4985 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 6 -->
### Ustica: The Missing Paper (2016) [A7]
- **tmdb_id**: 390281
- **相似度**: 0.4963
- **genres** / **language**: Drama, History / it
- **overview**: On the evening of June 27, 1980, a DC9 of the private airline Itavia disappeared from radar screens without sending any emergency signal. The aircraft, stabilized in cruise at 7.600 meters above sea level, sank into the Tyrrhenian Trench, between Ponza and Ustica. 81 people lost their lives, including 14 children. There are three hypotheses about the disaster, but none has ever been proven, until the analysis of the findings and documentary material reveals a fourth, chilling possible cause of the disaster.
- **跳转**: https://themoviecosmos.com/movie/390281
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[why-0, how-0, how-1, result-0, result-1, result-2] · sim=0.4963 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 6 -->
### Transpecos (2016) [A2]
- **tmdb_id**: 381018
- **相似度**: 0.5000
- **genres** / **language**: Thriller / en
- **overview**: For three US Border Patrol agents, the contents of one car reveal an insidious plot within their own ranks. The next 24 hours may cost them their lives.
- **跳转**: https://themoviecosmos.com/movie/381018
- **also_baseline**: true
- **命中视角/碎片**:
  - A2/p2: fragments=[how-0, how-1] · sim=0.4354 · **命中分=2**
  - A1/p1: fragments=[how-0, how-1] · sim=0.5000 · **命中分=2**
  - A1/p3: fragments=[result-1, result-2] · sim=0.4925 · **命中分=2**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### Resurrecting the Champ (2007) [A7]
- **tmdb_id**: 13074
- **相似度**: 0.4849
- **genres** / **language**: Drama / en
- **overview**: Up-and-coming sports reporter rescues a homeless man ("Champ") only to discover that he is, in fact, a boxing legend believed to have passed away. What begins as an opportunity to resurrect Champ's story and escape the shadow of his father's success becomes a personal journey as the ambitious reporter reexamines his own life and his relationship with his family.
- **跳转**: https://themoviecosmos.com/movie/13074
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.4849 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### Graduation Day (1981) [A7]
- **tmdb_id**: 27420
- **相似度**: 0.5513
- **genres** / **language**: Horror / en
- **overview**: After the death of a high school track star during a race, a mysterious killer in a fencing mask begins murdering her friends and teachers.
- **跳转**: https://themoviecosmos.com/movie/27420
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5513 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 6 -->
### By the Law (1926) [A7]
- **tmdb_id**: 126644
- **相似度**: 0.5740
- **genres** / **language**: Drama, Western, Mystery, Action / ru
- **overview**: After a man kills two members of his Yukon gold prospecting team, the other two surviving members struggle to keep him subdued for the next several months until they can turn him over to the law. Based on Jack London's 'The Unexpected' (1905).
- **跳转**: https://themoviecosmos.com/movie/126644
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[why-0, how-0, how-1, how-2, result-0, result-1] · sim=0.5740 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### The Key (1983) [A7]
- **tmdb_id**: 28468
- **相似度**: 0.5658
- **genres** / **language**: Drama, Romance / it
- **overview**: In 1940s Venice, after twenty years' marriage, retired art critic Nino Rolfe and his younger wife Teresa feel their passion waning. To help her shed her inhibitions and rekindle their relationship, the professor records his sexual fantasies in a diary.
- **跳转**: https://themoviecosmos.com/movie/28468
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.5658 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### The Big Dream (2009) [A7]
- **tmdb_id**: 51477
- **相似度**: 0.5684
- **genres** / **language**: Drama, History, Romance / it
- **overview**: Italy, 1968. Aspiring actor Nicola enrolls in the police to pay for his studies, ending up undercover among college students protesting the government, the Vietnam War and the values of their parents' generation. However, he complicates his mission by falling for Laura, a bourgeois girl dreaming of a better world.
- **跳转**: https://themoviecosmos.com/movie/51477
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.5684 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### Too Much Johnson (1938) [A7]
- **tmdb_id**: 193315
- **相似度**: 0.5534
- **genres** / **language**: Comedy / en
- **overview**: This film was not intended to stand by itself, but was designed as the cinematic aspect of Welles' Mercury Theatre stage presentation of William Gillette's 1894 comedy about a New York playboy who flees from the violent husband of his mistress and borrows the identity of a plantation owner in Cuba who is expecting the arrival of a mail order bride. The film component of the performance was ultimately never screened due to the absence of projection facilities at the venue. Long-believed to be lost, a workprint was discovered in 2008 and the film had its premiere in 2013.
- **跳转**: https://themoviecosmos.com/movie/193315
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.5534 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### Venus in Fur (2013) [A7]
- **tmdb_id**: 197082
- **相似度**: 0.5443
- **genres** / **language**: Drama / fr
- **overview**: An enigmatic actress may have a hidden agenda when she auditions for a part in a misogynistic writer's play.
- **跳转**: https://themoviecosmos.com/movie/197082
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.5443 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 6 -->
### Wotakoi: Love is Hard for Otaku (2020) [A7]
- **tmdb_id**: 552687
- **相似度**: 0.5536
- **genres** / **language**: Comedy, Romance / ja
- **overview**: An effervescent musical about one of the most unlikely couples seen on screen: two Otaku intent on hiding their nerdiness from their colleagues!
- **跳转**: https://themoviecosmos.com/movie/552687
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[how-0, how-1, how-2, why-0, why-1, result-0] · sim=0.5536 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 6 -->
### The Idealist (2015) [A7]
- **tmdb_id**: 335490
- **相似度**: 0.4675
- **genres** / **language**: Thriller / da
- **overview**: A whistle blower attempts to reveal the secret behind a nuclear disaster that occurred during the height of the Cold War.
- **跳转**: https://themoviecosmos.com/movie/335490
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, result-0, result-1, result-2, result-3] · sim=0.4675 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 6 -->
### Dead Mail (2024) [A7]
- **tmdb_id**: 1229915
- **相似度**: 0.5471
- **genres** / **language**: Crime, Thriller, Music, Mystery, Horror / en
- **overview**: An ominous help note finds its way to a 1980s post office, connecting a dead letter investigator to a kidnapped keyboard technician.
- **跳转**: https://themoviecosmos.com/movie/1229915
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p1: fragments=[how-0, how-1, result-0, result-1, result-2, result-3] · sim=0.5471 · **命中分=6**
- **pseudo命中分合计**: 6
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Out of the Past (1947) [baseline only]
- **tmdb_id**: 678
- **相似度**: 0.4330
- **genres** / **language**: Crime, Thriller / en
- **overview**: The peaceful life of a gas station owner is disrupted when a man from his past arrives in town and forces him to return to the dark world he had tried to escape.
- **跳转**: https://themoviecosmos.com/movie/678
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p1: fragments=[how-0, how-1, how-2, how-3, how-4] · sim=0.4330 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Timecode (2016) [A7]
- **tmdb_id**: 398395
- **相似度**: 0.4368
- **genres** / **language**: Drama, Romance / es
- **overview**: Timecode is a 2016 Spanish live-action short film directed by Juanjo Giménez. Luna and Diego are the parking lot security guards. Diego does the night shift, and Luna works by day. One day, Luna's boss asks her to investigate a broken tail light. It won the Short Film Palme d'Or award at 69th annual Cannes Film Festival in 2016. It is also nominated for an Academy Award for Best Live Action Short Film at the 89th Academy Awards in 2017.
- **跳转**: https://themoviecosmos.com/movie/398395
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[how-4, how-5, result-0, result-1, result-2] · sim=0.4368 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### Baadshaho (2017) [A7]
- **tmdb_id**: 441894
- **相似度**: 0.4028
- **genres** / **language**: Action, Thriller / hi
- **overview**: Emergency has been declared in India. Maharani Gitanjali from one of Rajasthan's princely states has already lost her privy purse. Now, she fears that she will lose the last treasure chest of gold which has been forcibly taken away from her. So she asks her trusted lieutenant, Bhawani to step in and plan a heist.
- **跳转**: https://themoviecosmos.com/movie/441894
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-1, how-2, how-3, how-4, how-5] · sim=0.4028 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 01-grid-outage -->
<!-- pseudo命中分合计: 5 -->
### The Miracles of the Namiya General Store (2017) [A7]
- **tmdb_id**: 477652
- **相似度**: 0.4156
- **genres** / **language**: Fantasy, Drama, Mystery, Family / ja
- **overview**: In 2012, Atsuya and his 2 childhood friends do something bad and run into an old general store. They decide to stay there until the morning. Late into the night, Atsuya sees a letter in the mailbox. The letter is addressed to the Namiya General Store and the letter was written by someone to consult about worries. Incredibly, the letter was written 32 years ago. The mailbox is somehow connected to the year 1980. Atsuya and his friends decide to write a reply and place their letter in the mailbox.
- **跳转**: https://themoviecosmos.com/movie/477652
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-1, how-2, how-3, how-4, how-5] · sim=0.4156 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 5 -->
### The Terrible People (1960) [A4]
- **tmdb_id**: 5630
- **相似度**: 0.5246
- **genres** / **language**: Crime, Thriller / de
- **overview**: The ghost of a hanged man returns to fulfill his promise. All of his accusers must die!
- **跳转**: https://themoviecosmos.com/movie/5630
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[why-0, why-1, how-1, how-2, result-0] · sim=0.5246 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 5 -->
### Pepe, der Paukerschreck (1969) [A7]
- **tmdb_id**: 11094
- **相似度**: 0.4975
- **genres** / **language**: Comedy / de
- **overview**: Mommsen Gymnasium director Taft secretly places his nephew as a spy with the difficult class of Pepe Nietnagel. During the celebration for the 100th anniversary, a simulated fire forces the school to shut down for a week. The director's attempt to get a tough teacher assigned by the department of education results in the exact opposite because of Nietnagel's intervention.
- **跳转**: https://themoviecosmos.com/movie/11094
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-2, how-0, how-1, how-2, result-0] · sim=0.4975 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 5 -->
### The Hexer (2001) [A4]
- **tmdb_id**: 57278
- **相似度**: 0.5471
- **genres** / **language**: Adventure, Fantasy / pl
- **overview**: A heroic fantasy based on the famous novels by Polish writer Andrzej Sapkowski, "The Sword of Destiny" and "The Last Wish".  This film immerses us in a world inhabited by kings and knights, princesses and sorcerers, priests and magicians, where fire-breathing dragons guard untold treasures, and human greed leads to an endless struggle for power, cruelty, bloodshed, and violence. And this world has its own superheroes - fearless witchers, people with magical powers. Their mission is to protect the human race from any misfortune.  The witcher Geralt of Rivia must find the young princess Ciri, kidnapped by enemies. Only her return to the small kingdom of Cintra, which was attacked by aggressors, can restore peace and order there. The brave witcher sets off on a journey, long, distant and deadly.
- **跳转**: https://themoviecosmos.com/movie/57278
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[why-0, why-1, how-1, how-2, result-0] · sim=0.5471 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 5 -->
### Beyond Darkness (1990) [A4]
- **tmdb_id**: 60190
- **相似度**: 0.5883
- **genres** / **language**: Horror, Thriller / en
- **overview**: A priest and his family move into a new house, without knowing that it was built over the place where twenty witches were burnt at the stake.
- **跳转**: https://themoviecosmos.com/movie/60190
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-2, how-0, how-1, how-2, how-3] · sim=0.5883 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 5 -->
### The Light Bulb Conspiracy (2010) [A4]
- **tmdb_id**: 61933
- **相似度**: 0.4924
- **genres** / **language**: Documentary / fr
- **overview**: Once upon a time... consumer goods were built to last. Then, in the 1920’s, a group of businessmen realized that the longer their product lasted, the less money they made, thus Planned Obsolescence was born, and manufacturers have been engineering products to fail ever since.  Combining investigative research and rare archive footage with analysis by those working on ways to save both the economy and the environment, this documentary charts the creation of ‘engineering to fail’, its rise to prominence and its recent fall from grace.
- **跳转**: https://themoviecosmos.com/movie/61933
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p3: fragments=[why-2, how-0, how-1, how-2, result-1] · sim=0.4924 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 5 -->
### Home Made Home (1951) [A4]
- **tmdb_id**: 66878
- **相似度**: 0.5756
- **genres** / **language**: Animation / en
- **overview**: Goofy's building a house, and struggling with the blueprints, the window glass, the paint, and finally the house-warming guests.
- **跳转**: https://themoviecosmos.com/movie/66878
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-2, how-0, how-1, how-2, how-3] · sim=0.5756 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 5 -->
### Bounty Killer (2013) [A4]
- **tmdb_id**: 209504
- **相似度**: 0.5081
- **genres** / **language**: Action, Science Fiction / en
- **overview**: It’s been 20 years since the corporations took over the world’s governments. Their thirst for power and profits led to the Corporate Wars, a fierce global battle that laid waste to society as we know it. Born from the ash, the Council of Nine rose as a new law and order for this dark age. To avenge the corporations’ reckless destruction, the Council issues death warrants for all white collar criminals. Their hunters—the bounty killer. From amateur savage to graceful assassin, the bounty killers now compete for body count, fame and a fat stack of cash. They’re ending the plague of corporate greed and providing the survivors of the apocalypse with retribution. These are the new heroes. This is the age of the BOUNTY KILLER.
- **跳转**: https://themoviecosmos.com/movie/209504
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p3: fragments=[why-2, how-0, how-1, how-2, result-1] · sim=0.5081 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 02-corporate-layoff -->
<!-- pseudo命中分合计: 5 -->
### Stalled (2022) [A7]
- **tmdb_id**: 1032394
- **相似度**: 0.5032
- **genres** / **language**: Science Fiction, Thriller / en
- **overview**: Late for the most important meeting of his life, a toxic executive finds himself trapped in a time paradox within a public restroom.
- **跳转**: https://themoviecosmos.com/movie/1032394
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-2, how-0, how-1, how-2, result-0] · sim=0.5032 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 5 -->
### Joe the King (1999) [A2]
- **tmdb_id**: 53151
- **相似度**: 0.5232
- **genres** / **language**: Crime, Drama / en
- **overview**: A destitute 14-year-old struggles to keep his life together despite harsh abuse at his mother's hands, harsher abuse at his father's, and a growing separation from his slightly older brother.
- **跳转**: https://themoviecosmos.com/movie/53151
- **also_baseline**: false
- **命中视角/碎片**:
  - A2/p3: fragments=[result-0, result-1, result-3, result-4, result-5] · sim=0.5232 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 5 -->
### Valley of the Wolves: Palestine (2011) [baseline only]
- **tmdb_id**: 58637
- **相似度**: 0.4783
- **genres** / **language**: Action, Drama, War / tr
- **overview**: After the Freedom Flotilla attempts to bring humanitarian assistance to Gaza refuses to turn back, it is attacked by the Israeli military. In a dramatic battle scene, activists resist and are killed by the Israeli soldiers. A Turkish commando team led by Polat Alemdar (Necati Şaşmaz) travels to West Bank in Palestine, where they launch a campaign against Israeli military personnel in an attempt to track down and eliminate an Israeli general, leader Moşe Ben Eliyezer (Erdal Beşikçioğlu), who is the responsible for the flotilla raid.
- **跳转**: https://themoviecosmos.com/movie/58637
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p2: fragments=[how-0, how-1, how-2, how-3, result-5] · sim=0.4783 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 5 -->
### Bermuda Tentacles (2014) [baseline only]
- **tmdb_id**: 260372
- **相似度**: 0.4617
- **genres** / **language**: Science Fiction / en
- **overview**: After Air Force One goes down during a storm over the Bermuda Triangle, the United States Navy is dispatched to find the escape pod holding the President. A giant monster beneath the ocean awakens and attacks the fleet.
- **跳转**: https://themoviecosmos.com/movie/260372
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p2: fragments=[how-0, how-1, how-2, how-3, result-5] · sim=0.4617 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 05-climate-disaster -->
<!-- pseudo命中分合计: 5 -->
### Spitak (2018) [A2]
- **tmdb_id**: 514886
- **相似度**: 0.5322
- **genres** / **language**: Drama, Action / hy
- **overview**: «Spitak» tells the story of the most devastating and largest (in terms of casualties) Armenian earthquake that happened on December 7, 1988. This day went down in history as the day of a horrible disaster, which claimed the lives of over 25,000 lives and left more than half a million people homeless. The film «Spitak» is the story of Gor, who left Armenia in search of a better life but now returns back after the earthquake in order to find his home. His family. But it's too late. Everything is destroyed by the disaster. and he has to re-learn to love what he destroyed himself. Film-Requiem.
- **跳转**: https://themoviecosmos.com/movie/514886
- **also_baseline**: false
- **命中视角/碎片**:
  - A2/p3: fragments=[result-0, result-1, result-3, result-4, result-5] · sim=0.5322 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 06-tech-monopoly -->
<!-- pseudo命中分合计: 5 -->
### The Olsen Gang Goes to War (1978) [baseline only]
- **tmdb_id**: 12592
- **相似度**: 0.3995
- **genres** / **language**: Family, Comedy, Crime / da
- **overview**: Some criminal EU ministers plan to turn Denmark into a gigantic fair ground and holiday paradise. Egon gets his hand at some important documents which could both make him rich and take care of Denmark's future.
- **跳转**: https://themoviecosmos.com/movie/12592
- **also_baseline**: true
- **命中视角/碎片**:
  - A1/p3: fragments=[how-1, how-2, how-3, result-0, result-1] · sim=0.3995 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 5 -->
### 2012 (2009) [A4]
- **tmdb_id**: 14161
- **相似度**: 0.5710
- **genres** / **language**: Action, Adventure, Science Fiction / en
- **overview**: Dr. Adrian Helmsley, part of a worldwide geophysical team investigating the effect on the earth of radiation from unprecedented solar storms, learns that the earth's core is heating up. He warns U.S. President Thomas Wilson that the crust of the earth is becoming unstable and that without proper preparations for saving a fraction of the world's population, the entire race is doomed. Meanwhile, writer Jackson Curtis stumbles on the same information. While the world's leaders race to build "arks" to escape the impending cataclysm, Curtis struggles to find a way to save his family. Meanwhile, volcanic eruptions and earthquakes of unprecedented strength wreak havoc around the world.
- **跳转**: https://themoviecosmos.com/movie/14161
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5710 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 07-migration-border -->
<!-- pseudo命中分合计: 5 -->
### Exploding Sun (2013) [A4]
- **tmdb_id**: 212986
- **相似度**: 0.5532
- **genres** / **language**: Science Fiction / en
- **overview**: The world watches in awe as the Roebling Clipper is launched into space. Using state-of-the-art scalar engines to fly around the Moon and back in just hours, the maiden voyage of the first-ever trans-lunar passenger ship is about to make history. Among those on board: First Lady Simone Mathany, space-exploration entrepreneur Steve Roebling, Dr. Denise Balaban, pilot Fiona Henslaw, and a very lucky lottery winner. But while en route, a massive solar flare sparks a cosmic-ray burst that accelerates Aurora’s engine and blows the ship away from Earth’s orbit.  Now out of control, it’s hurtling straight for the sun.
- **跳转**: https://themoviecosmos.com/movie/212986
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, how-0, how-1, result-0, result-1] · sim=0.5532 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 5 -->
### End of the Spear (2005) [A4]
- **tmdb_id**: 14120
- **相似度**: 0.6011
- **genres** / **language**: Adventure, Drama, History / en
- **overview**: "End of the Spear" is the story of Mincayani, a Waodani tribesman from the jungles of Ecuador. When five young missionaries, among them Jim Elliot and Nate Saint, are speared to death by the Waodani in 1956, a series of events unfold to change the lives of not only the slain missionaries' families, but also Mincayani and his people.
- **跳转**: https://themoviecosmos.com/movie/14120
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p3: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.6011 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 5 -->
### Summer Time Machine Blues (2005) [A7]
- **tmdb_id**: 26130
- **相似度**: 0.5322
- **genres** / **language**: Comedy, Science Fiction / ja
- **overview**: The members of a sci-fi club accidentally spill Coke on the remote controller of an air-conditioner during summer and suddenly a time machine appears in their sweating bath-like clubroom.
- **跳转**: https://themoviecosmos.com/movie/26130
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p2: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.5322 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 5 -->
### The Hobbit: The Battle of the Five Armies (2014) [A4]
- **tmdb_id**: 122917
- **相似度**: 0.5854
- **genres** / **language**: Action, Adventure, Fantasy / en
- **overview**: Following Smaug's attack on Laketown, Bilbo and the dwarves try to defend Erebor's mountain of treasure from others who claim it: the men of the ruined Laketown and the elves of Mirkwood. Meanwhile an army of Orcs led by Azog the Defiler is marching on Erebor, fueled by the rise of the dark lord Sauron. Dwarves, elves and men must unite, and the hope for Middle-Earth falls into Bilbo's hands.
- **跳转**: https://themoviecosmos.com/movie/122917
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p3: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.5854 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 5 -->
### Mammals (1962) [A4]
- **tmdb_id**: 146131
- **相似度**: 0.5499
- **genres** / **language**: Comedy / pl
- **overview**: "Waiting for Godot" on ice and snow, without words. Against a barren winter landscape, a figure approaches: it's a man, pulling a small sleigh on which another man sits, plucking a dead bird. They stop to trade places; the one now on the sleigh takes out his knitting. Accidents, misunderstandings, disagreements, and an outright fight await our absurd protagonists as their trip to nowhere continues, first with one pulling, then the other. What if they were to lose the sleigh? What rules of civilization and partnership would guide them then?
- **跳转**: https://themoviecosmos.com/movie/146131
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.5499 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 5 -->
### Code Geass: Akito the Exiled 5: To Beloved Ones (2016) [A4]
- **tmdb_id**: 372751
- **相似度**: 0.5368
- **genres** / **language**: Action, Animation, Science Fiction / ja
- **overview**: The Ark Fleet has been destroyed, and a significant number of the enemy's troops have been wiped out due to its crash landing. As the remaining forces of the Holy Order of Michael regroup in order to launch a final assault on Weiswolf Castle, the wZERO unit, along with their new ally Ashley Ashra, stand ready to intercept them. Meanwhile, with his Geass out of control, Shin moves to erase his younger brother's existence once and for all. But Akito, having promised Leila that he will come back alive, refuses to accept such a fate, and the two clash in their final battle.
- **跳转**: https://themoviecosmos.com/movie/372751
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.5368 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 5 -->
### True: Winter Wishes (2019) [A4]
- **tmdb_id**: 651249
- **相似度**: 0.5439
- **genres** / **language**: Animation, Adventure, Family / en
- **overview**: An ice crystal from a frosty realm is freezing everything in the Rainbow Kingdom, its citizens too! Can True save Winter Wishfest -- and her friends?
- **跳转**: https://themoviecosmos.com/movie/651249
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p1: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.5439 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 08-sports-underdog -->
<!-- pseudo命中分合计: 5 -->
### La Guerre des Prix (2026) [A4]
- **tmdb_id**: 1376412
- **相似度**: 0.5248
- **genres** / **language**: Drama, Thriller / fr
- **overview**: La Guerre des Prix
- **跳转**: https://themoviecosmos.com/movie/1376412
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[why-0, how-0, how-1, how-2, result-1] · sim=0.5248 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 09-cultural-backlash -->
<!-- pseudo命中分合计: 5 -->
### The Confession (2011) [A4]
- **tmdb_id**: 97481
- **相似度**: 0.5872
- **genres** / **language**: Crime, Drama / en
- **overview**: A unique story of redemption and an exploration of good and evil featuring a hit man and a priest.
- **跳转**: https://themoviecosmos.com/movie/97481
- **also_baseline**: false
- **命中视角/碎片**:
  - A4/p2: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.5872 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 5 -->
### Waco: The Rules of Engagement (1997) [A7]
- **tmdb_id**: 34044
- **相似度**: 0.5470
- **genres** / **language**: Documentary / en
- **overview**: In one of the most tragic face-offs in the history of law enforcement, the deadly debacle at Waco pitted the Branch Davidian sect against the FBI in an all-out war. This documentary makes the most of footage and recordings to examine how the events that led to the tragedy of April 19, 1993, unfolded, and how the FBI's unrelenting approach made what was already a bad situation much worse.
- **跳转**: https://themoviecosmos.com/movie/34044
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[why-0, how-2, result-0, result-1, result-3] · sim=0.5470 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

<!-- run_id: 10-whistleblower-leak -->
<!-- pseudo命中分合计: 5 -->
### Scare Out (2026) [A7]
- **tmdb_id**: 1447971
- **相似度**: 0.5544
- **genres** / **language**: Crime, Thriller, Action / zh
- **overview**: After a critical intelligence leak, a national security unit launches an intensive investigation. But successive setbacks in their arrest operations reveal a shocking truth: the trail leads back to within the unit itself. Amidst a storm of trust and betrayal, a silent battle begins to unfold...
- **跳转**: https://themoviecosmos.com/movie/1447971
- **also_baseline**: false
- **命中视角/碎片**:
  - A7/p3: fragments=[why-0, how-2, result-0, result-1, result-3] · sim=0.5544 · **命中分=5**
- **pseudo命中分合计**: 5
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
- **共振类型**:   <!-- 表层 / 结构 / 双重；0 分留空 -->

