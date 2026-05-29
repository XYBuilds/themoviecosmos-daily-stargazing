# 评测 · regional-grid-operator-warns-of-rolling-outages-after-heat-w

## 元信息
- date: 2026-05-29
- news_url: https://example.com/article/1
- run_id: regional-grid-operator-warns-of-rolling-outages-after-heat-w

## 现实波澜
- **title**: Regional grid operator warns of rolling outages after heat wave strains power plants
- **source** / **pub_time**: Example Wire / 2026-05-29T12:00:00Z
- **summary**: Officials said several fossil-fuel units tripped offline during record demand, forcing utilities to ration electricity across major cities for the second night. Consumer groups demanded transparency on maintenance schedules while industrial lobbies pressed for emergency fuel imports.

## 伪剧情（英文）
- **A2** The Sociologist: Record heat does not distribute its punishment equally: those who labor under the sun receive it first, those who can afford the cold of private generators receive it last. The grid, built on decades of extraction and deferred repair, buckles under the very demand it was meant to serve — and when the machines trip offline, it is not the boardroom but the household that goes dark. Industrial lobbies, armed with lobbyists and emergency petitions, secure their fuel; consumer groups, armed with nothing but numbers, are offered only the word "transparency." In every blackout, a hierarchy is quietly preserved: power flows to those who already hold it, and rationing falls on those who never did.
- **A4** The Mythologist: They had built their nights upon a flame they believed inexhaustible — towers of light rising from a fire they claimed to have mastered. Then the great furnace above pressed down with its ancient, indifferent heat, and one by one the tributaries of borrowed fire sputtered and fell dark. In the second night of rationed light, those who had long consumed without question began to demand an accounting of the keepers, while others cried out for more fuel to be torn from the earth and carried in haste. But the sun does not bargain, and the flame has always remembered to whom it truly belongs.
- **A7** The Chaos Theorist: It all began when a maintenance summary — three pages, printed single-sided — was placed face-down on the wrong shelf in a regional dispatch room. The top page listed which fuel-burning units required inspection before peak summer. No one turned it over. Weeks later, the heat arrived and demand surged; the uninspected units did exactly what neglected machines do and tripped offline, one after another. For two consecutive nights, electricity was rationed across major cities while consumer groups and industrial lobbies argued over transparency no one could provide. Somewhere in that dispatch room, the unread page was still warm from the copier.
- **A1** The Reality Recorder (Baseline) `[baseline]`: A prolonged heat wave drives electricity demand to a record level. Several power-generating units shut down unexpectedly during the peak. The grid operator warns that rolling outages may follow. Utilities begin rationing electricity across large cities for a second consecutive night. Consumer groups request public disclosure of maintenance schedules. Industrial groups push for emergency fuel imports to restart offline capacity. The operator and utilities coordinate to bring the tripped units back online while managing limited supply.

## errors
（无）

## divergence
<details>
<summary>展开 JSON</summary>

```json
{
  "query_cosines": {
    "A2-A4": 0.4667190909385681,
    "A2-A7": 0.5121628046035767,
    "A1-A2": 0.5982682108879089,
    "A4-A7": 0.5142708420753479,
    "A1-A4": 0.44185882806777954,
    "A1-A7": 0.5544482469558716
  },
  "topk_jaccard": {
    "A2-A4": 0.0,
    "A2-A7": 0.0,
    "A1-A2": 0.0,
    "A4-A7": 0.0,
    "A1-A4": 0.0,
    "A1-A7": 0.0
  }
}
```

</details>

## 候选星轨（共 8 部）

### Survival Family (2017) [baseline only]
- **tmdb_id**: 429918
- **相似度**: 0.5987
- **genres** / **language**: Comedy, Drama, Adventure / ja
- **overview**: A world wide electrical outage occurs. Everything that requires electricity comes to a stop. Tokyo is nearly ruined. Yoshiyuki Suzuki decides to escape from Tokyo with his family.
- **跳转**: https://themoviecosmos.com/movie/429918
- **also_baseline**: true
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->

### The Towering Inferno (1974) [A4]
- **tmdb_id**: 5919
- **相似度**: 0.5751
- **genres** / **language**: Action, Drama, Thriller / en
- **overview**: At the opening party of a colossal—but poorly constructed—skyscraper, a massive fire breaks out, threatening to destroy the tower and everyone in it.
- **跳转**: https://themoviecosmos.com/movie/5919
- **also_baseline**: false
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->

### Pyromaniac (2016) [A4]
- **tmdb_id**: 390358
- **相似度**: 0.5701
- **genres** / **language**: Drama, Thriller / no
- **overview**: In the darkness of a peaceful village, a pyromaniac ignites his first fire. As more fires break out, the society panics. An inferno lurks under the surface as a local policeman uncovers the unthinkable truth...
- **跳转**: https://themoviecosmos.com/movie/390358
- **also_baseline**: false
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->

### Who Killed the Electric Car? (2006) [A7]
- **tmdb_id**: 13508
- **相似度**: 0.4773
- **genres** / **language**: Documentary / en
- **overview**: In 1996, electric cars began to appear on roads all over California. They were quiet and fast, produced no exhaust, and ran without gasoline... Ten years later, these cars were destroyed.
- **跳转**: https://themoviecosmos.com/movie/13508
- **also_baseline**: false
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->

### Steam Whistle (1904) [A7]
- **tmdb_id**: 318739
- **相似度**: 0.4673
- **genres** / **language**: Documentary / en
- **overview**: A closeup of the steam whistle blowing at the "Westinghouse works" complex of factories in Pennsylvania, probably at the Westinghouse Electric & Manufacturing Co.
- **跳转**: https://themoviecosmos.com/movie/318739
- **also_baseline**: false
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->

### I Told You So (2024) [baseline only]
- **tmdb_id**: 976854
- **相似度**: 0.4570
- **genres** / **language**: Drama / it
- **overview**: In Rome, during a January weekend a sudden heatwave arrives. The sun is initially pleasant, but the heat quickly escalates to a frightening degree, resulting in people and animals losing self-control.
- **跳转**: https://themoviecosmos.com/movie/976854
- **also_baseline**: true
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->

### The Steam Experiment (2009) [A2]
- **tmdb_id**: 20047
- **相似度**: 0.4564
- **genres** / **language**: Crime, Drama, Thriller / en
- **overview**: A deranged scientist locks 6 people in a steam room and threatens to turn up the heat if the local paper doesn't publish his story about global warming.
- **跳转**: https://themoviecosmos.com/movie/20047
- **also_baseline**: false
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->

### Rites of Spring (2012) [A2]
- **tmdb_id**: 92397
- **相似度**: 0.4427
- **genres** / **language**: Horror, Thriller, Drama / en
- **overview**: A ransom scheme turns into a nightmare for a group of kidnappers who become victims of a horrifying secret that must be paid every spring.
- **跳转**: https://themoviecosmos.com/movie/92397
- **also_baseline**: false
- **共振分**:   <!-- 总编填写 0 / 1 / 2 -->
