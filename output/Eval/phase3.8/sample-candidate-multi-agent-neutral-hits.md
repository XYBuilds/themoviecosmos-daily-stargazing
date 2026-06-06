# Sample Candidate: Multi-Agent + Neutral Hits

## Why This Candidate

Illustrative example drawn from `high-hit-score-review.md` for Phase 3.8 eval documentation. Chosen for **clarity over peak score**: moderate metrics, obvious news–film thematic link, and a mix of neutral-channel (`n1`) and toned-channel (`p2`/`p3`) pseudo hits.

### Criteria checklist

| Criterion | Required | This candidate |
|-----------|----------|----------------|
| **多 agent 命中** | `distinct_agents` ≥ 2, or multiple agents in pseudo hits, or `quality_candidate` with toned convergence | ✅ `quality_candidate: true`; `distinct_agents: 4`; 7 agents in heading; `triggered_by` lists 4 agents in `retrieve.json` |
| **neutral_hits > 0** | Field explicitly > 0 | ✅ `neutral_hits: 5` |

### Selection notes

- **Run**: `02-corporate-layoff` (observation set `02` in batch manifest)
- **Not chosen**: `Survival Family` / `Flood` — satisfy criteria but have near-saturated agent counts (11–12 neutral hits); less pedagogically clear
- **Editor score**: 共振分 2 / 双重 — already scored in review

---

## Identity

| Field | Value |
|-------|-------|
| **run_id** | `02-corporate-layoff` |
| **tmdb_id** | `619090` |
| **title** | The Plan (2018) |

### News context

**Intuit to cut roughly 17% of workforce in AI-focused restructuring** — CEO announces ~3,000 layoffs, severance packages, and office closures as part of an AI-focused reinvention.

---

## Key Metrics

| Metric | Value |
|--------|-------|
| `quality_candidate` | `true` |
| `quality_reason` | `neutral_vote=1 + toned_agents=4: THE-INNOCENT,THE-EVERYMAN,THE-CREATOR,THE-JESTER` |
| `distinct_agents` | `4` |
| `neutral_hits` | `5` |
| `neutral_total` | `12` |
| `neutral_hit_rate` | `0.4167` |
| `max_similarity` (相似度) | `0.5312` |
| `pseudo命中分合计` | `48` |
| `also_baseline` | `false` |
| `genres` / `language` | Comedy, Drama / `es` |
| **共振分** | `2` |
| **共振类型** | `双重` |

**Agents in review heading**: THE-EVERYMAN, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-SAGE, THE-INNOCENT, THE-JESTER

**`triggered_by` (retrieve.json)**: THE-INNOCENT, THE-EVERYMAN, THE-CREATOR, THE-JESTER

---

## Candidate Detail (from review)

### The Plan (2018) [THE-EVERYMAN, THE-OUTLAW, THE-LOVER, THE-CREATOR, THE-SAGE, THE-INNOCENT, THE-JESTER] [优质·多agent]

- **tmdb_id**: 619090
- **quality_candidate**: true
- **neutral_hits**: 5
- **neutral_total**: 12
- **neutral_hit_rate**: 0.4167
- **distinct_agents**: 4
- **优质候选**: true
- **相似度**: 0.5312
- **genres** / **language**: Comedy, Drama / es
- **overview**: Three friends who have been fired from the company where they worked and are demoralized because of their unemployment status. In these circumstances, they meet to undertake the plan that mentions the title but there is a problem: the car with which they would travel has broken down and the crane must wait.
- **跳转**: https://themoviecosmos.com/movie/619090
- **also_baseline**: false

#### 命中视角/碎片

**Neutral channel (`n1`)** — five agents hit on the same neutral pseudo (no 命中分; fragment overlap drives neutral union):

- THE-EVERYMAN/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4296
- THE-OUTLAW/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4296
- THE-LOVER/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4239
- THE-CREATOR/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4296
- THE-SAGE/n1: fragments=[why-0, how-0, how-1, how-2, result-0] · sim=0.4294

**Toned channel (`p2`/`p3`)** — four agents contribute scored pseudo hits:

- THE-INNOCENT/p2: fragments=[why-0, result-1, result-3] · sim=0.5281 · **命中分=3**
- THE-EVERYMAN/p2: fragments=[why-0, how-1, result-1, result-3] · sim=0.5166 · **命中分=4**
- THE-CREATOR/p2: fragments=[why-0, why-1, how-0, result-0, result-1, result-2, result-3] · sim=0.5011 · **命中分=7**
- THE-JESTER/p2: fragments=[how-0, why-1, how-1, result-0, result-2] · sim=0.5312 · **命中分=5**
- THE-EVERYMAN/p3: fragments=[why-0, why-1, how-0, result-1] · sim=0.4716 · **命中分=4**

- **pseudo命中分合计**: 48
- **共振分**: 2
- **共振类型**: 双重

---

## retrieve.json excerpt

Source: `output/Eval/phase3.8/02-corporate-layoff/retrieve.json` — `candidates[]` entry for `tmdb_id: 619090`

```json
{
  "tmdb_id": 619090,
  "title": "The Plan",
  "similarity": 0.5311629772186279,
  "triggered_by": [
    "THE-INNOCENT",
    "THE-EVERYMAN",
    "THE-CREATOR",
    "THE-JESTER"
  ],
  "hit_sources": [
    {
      "agent_id": "THE-EVERYMAN",
      "pseudo_id": "n1",
      "channel_role": "neutral",
      "fragments": ["why-0", "how-0", "how-1", "how-2", "result-0"],
      "similarity": 0.4296417236328125
    },
    {
      "agent_id": "THE-OUTLAW",
      "pseudo_id": "n1",
      "channel_role": "neutral",
      "fragments": ["why-0", "how-0", "how-1", "how-2", "result-0"],
      "similarity": 0.4296417236328125
    },
    {
      "agent_id": "THE-LOVER",
      "pseudo_id": "n1",
      "channel_role": "neutral",
      "fragments": ["why-0", "how-0", "how-1", "how-2", "result-0"],
      "similarity": 0.4238588809967041
    },
    {
      "agent_id": "THE-CREATOR",
      "pseudo_id": "n1",
      "channel_role": "neutral",
      "fragments": ["why-0", "how-0", "how-1", "how-2", "result-0"],
      "similarity": 0.4296417236328125
    },
    {
      "agent_id": "THE-SAGE",
      "pseudo_id": "n1",
      "channel_role": "neutral",
      "fragments": ["why-0", "how-0", "how-1", "how-2", "result-0"],
      "similarity": 0.42940378189086914
    },
    {
      "agent_id": "THE-INNOCENT",
      "pseudo_id": "p2",
      "channel_role": "toned",
      "fragments": ["why-0", "result-1", "result-3"],
      "similarity": 0.5281348824501038
    },
    {
      "agent_id": "THE-EVERYMAN",
      "pseudo_id": "p2",
      "channel_role": "toned",
      "fragments": ["why-0", "how-1", "result-1", "result-3"],
      "similarity": 0.5165668725967407
    },
    {
      "agent_id": "THE-CREATOR",
      "pseudo_id": "p2",
      "channel_role": "toned",
      "fragments": ["why-0", "why-1", "how-0", "result-0", "result-1", "result-2", "result-3"],
      "similarity": 0.5011141300201416
    },
    {
      "agent_id": "THE-JESTER",
      "pseudo_id": "p2",
      "channel_role": "toned",
      "fragments": ["how-0", "why-1", "how-1", "result-0", "result-2"],
      "similarity": 0.5311629772186279
    },
    {
      "agent_id": "THE-EVERYMAN",
      "pseudo_id": "p3",
      "channel_role": "toned",
      "fragments": ["why-0", "why-1", "how-0", "result-1"],
      "similarity": 0.4716404676437378
    }
  ],
  "neutral_hits": 5,
  "neutral_total": 12,
  "neutral_hit_rate": 0.4166666666666667,
  "distinct_agents": 4,
  "quality_candidate": true,
  "quality_reason": "neutral_vote=1 + toned_agents=4: THE-INNOCENT,THE-EVERYMAN,THE-CREATOR,THE-JESTER"
}
```
