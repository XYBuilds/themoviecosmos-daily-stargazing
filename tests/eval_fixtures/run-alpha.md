# 评测 · run-alpha

## 元信息
- date: 2026-05-29
- news_url: https://example.com/alpha
- run_id: run-alpha

## 现实波澜
- **title**: Fixture alpha news
- **source** / **pub_time**: Test / 2026-05-29
- **summary**: Synthetic fixture for summarize_eval gate check.

## 伪剧情（英文）
- **A2** The Sociologist: (fixture)
- **A4** The Mythologist: (fixture)
- **A7** The Chaos Theorist: (fixture)
- **A1** The Reality Recorder `[baseline]`: (fixture)

## errors
（无）

## 候选星轨（共 3 部）

### Baseline Film (2020) [baseline only]
- **tmdb_id**: 100001
- **相似度**: 0.5500
- **genres** / **language**: Drama / en
- **overview**: A baseline-only candidate.
- **跳转**: https://themoviecosmos.com/movie/100001
- **also_baseline**: true
- **共振分**: 1

### Creative Hit (2019) [A2]
- **tmdb_id**: 100002
- **相似度**: 0.5400
- **genres** / **language**: Thriller / en
- **overview**: Creative agent A2 recall with structural resonance.
- **跳转**: https://themoviecosmos.com/movie/100002
- **also_baseline**: false
- **共振分**: 2

### Creative Miss (2018) [A4]
- **tmdb_id**: 100003
- **相似度**: 0.5300
- **genres** / **language**: Comedy / en
- **overview**: Creative agent A4 recall without resonance.
- **跳转**: https://themoviecosmos.com/movie/100003
- **also_baseline**: false
- **共振分**: 0
