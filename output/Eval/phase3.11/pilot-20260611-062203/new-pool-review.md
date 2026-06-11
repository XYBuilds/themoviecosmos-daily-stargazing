# Net-New Pool Review · Pilot `pilot-20260611-062203` / `01-grid-outage`

**Purpose:** Manual quality review of films that appear in the Phase 3.11 design-on candidate pool but **not** in the Phase 3.10 baseline for the same news story.

**Context:** Design-on and baseline each surfaced **19** candidates with **9** overlap. This run introduced **10 net-new** tmdb_ids and dropped **10** baseline-only films. Per product guidance: **if these 10 replacements are thematically acceptable, losing the 10 baseline films is an acceptable trade** for the POV/focalization experiment.

| Metric | Value |
|--------|-------|
| Baseline candidates | 19 |
| Design-on candidates | 19 |
| Overlap | 9 |
| Net-new | 10 |
| Lost from baseline | 10 |

**Channel breakdown (net-new only):**

| Channel | Count | tmdb_ids |
|---------|-------|----------|
| focalized | 4 | 6499, 63333, 949698, 969686 |
| neutral (n1) | 1 | 720321 |
| toned | 5 | 2154, 14161, 43552, 58770, 158091 |

---

## Films to review (net-new)

### 1. Turbo: A Power Rangers Movie (1997) · tmdb `6499` · **focalized**

| Field | Value |
|-------|-------|
| **Year** | 1997 |
| **Genres** | Action, Adventure, Family, Fantasy, Science Fiction |
| **Recalled by** | The-Hero (`p3`, focalized) |
| **Similarity** | 0.518 |
| **Plot** | The Power Rangers must stop Divatox from releasing Maligore, racing to Muranthias with new Turbo powers. |

**Triggering pseudo** (The-Hero · `p3` · focalized):

> The grid guardians moved to restore order on the frontline of the power crisis. When the critical system failure of a key power plant component struck, they raised the alarm with a high-level warning and initiated operational procedures to avoid overload, confronting the challenge of increased electricity consumption due to high temperatures.

- Pipeline: [`01-grid-outage/personas/The-Hero/persona-pipeline.json`](01-grid-outage/personas/The-Hero/persona-pipeline.json)
- Movie: https://themoviecosmos.com/movie/6499

**Review note:** Thematic stretch (superhero fantasy vs grid outage); check whether focalized hero framing is pulling adventure-rescue tropes.

---

### 2. Gog (1954) · tmdb `63333` · **focalized**

| Field | Value |
|-------|-------|
| **Year** | 1954 |
| **Genres** | Thriller, Science Fiction, Horror |
| **Recalled by** | The-Creator (`p3`, focalized) |
| **Similarity** | 0.480 |
| **Plot** | A mechanical brain is programmed to sabotage a government secret lab while work continues on the first space station. |

**Triggering pseudo** (The-Creator · `p3` · focalized):

> *(see persona-pipeline — creator focal leg on equipment / system failure framing)*

- Pipeline: [`01-grid-outage/personas/The-Creator/persona-pipeline.json`](01-grid-outage/personas/The-Creator/persona-pipeline.json)
- Movie: https://themoviecosmos.com/movie/63333

**Review note:** Cold-war tech-sabotage; may resonate with “grid incident / hidden lever” creator lens.

---

### 3. Flashover (2023) · tmdb `949698` · **focalized**

| Field | Value |
|-------|-------|
| **Year** | 2023 |
| **Genres** | Drama, Action |
| **Recalled by** | The-Explorer (`p3`, focalized) |
| **Similarity** | 0.459 |
| **Plot** | After an earthquake ruptures a gas pipeline, firefighters battle escalating blazes and rescue survivors from the rubble. |

**Triggering pseudo** (The-Explorer · `p3` · focalized):

> The power system operator watches as the consequences of a power outage ripple across the grid. The grid incident began when a generating unit tripped offline, joining a series of maintenance shutdowns that had already stressed the system. This event, combined with an energy demand spike from the heatwave, forced an emergency response: authorities placed the region under a red alert and ordered load shedding to protect a critical transmission line. From this vantage, the operator sees the direct outcome: a capacity loss leaving the island group short of over 950 megawatts of needed power.

- Pipeline: [`01-grid-outage/personas/The-Explorer/persona-pipeline.json`](01-grid-outage/personas/The-Explorer/persona-pipeline.json)
- Movie: https://themoviecosmos.com/movie/949698

**Review note:** Strong thematic fit — industrial disaster, emergency response, cascade failure.

---

### 4. 4 Horsemen: Apocalypse (2022) · tmdb `969686` · **focalized**

| Field | Value |
|-------|-------|
| **Year** | 2022 |
| **Genres** | Science Fiction, Horror |
| **Recalled by** | The-Magician (`p3`, focalized) |
| **Similarity** | 0.537 |
| **Plot** | Scientists race to stop a cascade of global disasters that may signal the apocalypse. |

**Triggering pseudo** (The-Magician · `p3` · focalized):

> I watch the crisis unfold from my control room. The cascading network of generators is failing, one by one, as the seasonal heat drives demand past any safe threshold. My instruments show the critical pressure point—Visayas—flashing red. We have no choice but to execute a deliberate, surgical unloading of the grid, an emergency measure to keep the 230-kilovolt line from overloading. The energy deficit we create is a calculated sacrifice to prevent total collapse.

- Pipeline: [`01-grid-outage/personas/The-Magician/persona-pipeline.json`](01-grid-outage/personas/The-Magician/persona-pipeline.json)
- Movie: https://themoviecosmos.com/movie/969686

**Review note:** First-person focalized control-room POV; apocalypse-cascade metaphor may be heavy-handed.

---

### 5. Breathe (2024) · tmdb `720321` · **neutral (n1)**

| Field | Value |
|-------|-------|
| **Year** | 2024 |
| **Genres** | Action, Science Fiction, Mystery, Thriller |
| **Recalled by** | The-Hero (`n1`), The-Sage (`n1`) — objective-floor neutral only |
| **Similarity** | 0.451 (best: Sage n1) |
| **Plot** | In a near future with scarce air, a mother and daughter fight for survival when strangers seek their oxygenated haven. |

**Triggering pseudo** (The-Sage · `n1` · neutral):

> *(objective-floor n1 — shared baseline wording; see retrieve.json per_agent THE-SAGE n1)*

- Retrieve: [`01-grid-outage/retrieve.json`](01-grid-outage/retrieve.json) → `per_agent` THE-HERO / THE-SAGE `n1`
- Movie: https://themoviecosmos.com/movie/720321

**Review note:** Entered pool via **neutral channel only** (not persona-toned legs). Survival-scarcity theme; verify it is acceptable as an n1-driven hit.

---

### 6. The Dark Side of the Moon (1990) · tmdb `2154` · **toned**

| Field | Value |
|-------|-------|
| **Year** | 1990 |
| **Genres** | Horror, Action, Thriller, Science Fiction |
| **Recalled by** | The-Sage (`p1`, toned) |
| **Similarity** | 0.471 |
| **Plot** | Stranded on the dark side of the moon with failing oxygen, astronauts board a derelict shuttle — then crew members are possessed and killed one by one. |

**Triggering pseudo** (The-Sage · `p1` · toned):

> *(Sage toned leg on systemic failure / thin-margin framing — see retrieve.json)*

- Pipeline: [`01-grid-outage/personas/The-Sage/persona-pipeline.json`](01-grid-outage/personas/The-Sage/persona-pipeline.json)
- Movie: https://themoviecosmos.com/movie/2154

**Review note:** Sci-fi horror; resource-depletion parallel to grid oxygen/fuel metaphor.

---

### 7. 2012 (2009) · tmdb `14161` · **toned**

| Field | Value |
|-------|-------|
| **Year** | 2009 |
| **Genres** | Action, Adventure, Science Fiction |
| **Recalled by** | The-Creator (`p1`, toned) |
| **Similarity** | 0.444 |
| **Plot** | Solar storms heat the earth's core; governments build arks while one writer tries to save his family amid global cataclysm. |

- Pipeline: [`01-grid-outage/personas/The-Creator/persona-pipeline.json`](01-grid-outage/personas/The-Creator/persona-pipeline.json)
- Movie: https://themoviecosmos.com/movie/14161

**Review note:** Broad disaster epic; common retrieval for infrastructure-collapse news.

---

### 8. Vanishing on 7th Street (2010) · tmdb `43552` · **toned**

| Field | Value |
|-------|-------|
| **Year** | 2010 |
| **Genres** | Mystery, Horror, Thriller |
| **Recalled by** | The-Caregiver (`p1`, toned) |
| **Similarity** | 0.496 |
| **Plot** | After a global blackout, most people vanish; survivors barricade in a tavern as a dark force closes in. |

**Triggering pseudo** (The-Caregiver · `p1` · toned):

> When the critical power source that failed the community—Kepco SPC Power's Unit 2—went offline, a massive power shortage affecting countless homes followed. The cascading failure began with this equipment failure, leaving the region's energy deficit at over 950 megawatts. Protecting the vulnerable system required urgent action: emergency measures to prevent a wider blackout were implemented through load shedding.

- Pipeline: [`01-grid-outage/personas/The-Caregiver/persona-pipeline.json`](01-grid-outage/personas/The-Caregiver/persona-pipeline.json)
- Movie: https://themoviecosmos.com/movie/43552

**Review note:** **Strong blackout thematic fit** for caregiver harm-to-community framing.

---

### 9. The Trigger Effect (1996) · tmdb `58770` · **toned**

| Field | Value |
|-------|-------|
| **Year** | 1996 |
| **Genres** | Drama, Thriller |
| **Recalled by** | The-Sage (`p2`, toned) |
| **Similarity** | 0.457 |
| **Plot** | A citywide blackout forces ordinary people to weigh survival, law, and morality in a predatory environment. |

- Pipeline: [`01-grid-outage/personas/The-Sage/persona-pipeline.json`](01-grid-outage/personas/The-Sage/persona-pipeline.json)
- Movie: https://themoviecosmos.com/movie/58770

**Review note:** **Excellent thematic match** for grid-outage news (literally about blackout cascade).

---

### 10. Metro Manila (2013) · tmdb `158091` · **toned**

| Field | Value |
|-------|-------|
| **Year** | 2013 |
| **Genres** | Crime, Thriller, Drama, Action |
| **Recalled by** | The-Explorer (`p1`, toned) |
| **Similarity** | 0.508 |
| **Plot** | A family leaves rural poverty for Manila; the father finds work with an armored-truck company as urban peril closes in. |

- Pipeline: [`01-grid-outage/personas/The-Explorer/persona-pipeline.json`](01-grid-outage/personas/The-Explorer/persona-pipeline.json)
- Movie: https://themoviecosmos.com/movie/158091

**Review note:** Philippines setting overlap with news geography; crime thriller rather than infrastructure — judge whether locale match is enough.

---

## Lost baseline films (for trade-off context)

These 10 films were in the 3.10 pool but **not** in design-on:

`46221`, `100063`, `111750`, `190738`, `194834`, `210219`, `280492`, `370097`, `431892`, `1223272`

Notable gap-A target still only in baseline: **Survival Family** (`429918`, human_score 2, 表层沾边).

---

## Suggested manual verdict checklist

For each net-new row above, mark:

- [ ] **Thematic fit** — does the film's premise resonate with the grid-outage story?
- [ ] **Channel attribution** — is the recall driven by the expected channel (focalized vs toned vs n1)?
- [ ] **Acceptable replacement** — would you trade one of the lost baseline films for this title?

**Aggregate question:** If ≥7/10 net-new pass individual review, accept the 10-for-10 pool swap and proceed toward 3.11.7 batch.

---

_Source: `pool-diff.json`, `retrieve.json` human_candidates overviews, persona pipelines under `01-grid-outage/personas/`._
