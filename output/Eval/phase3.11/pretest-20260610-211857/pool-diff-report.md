# Phase 3.11.1 Pretest — Pool Diff Report

Gap A samples in manifest: 8

## Go/No-Go (heuristic · requires human approve)

- **Verdict:** Conditional Go
- **Reason:** 40 net-new candidates but none match Gap A targets; manual review whether additions are resonance vs noise.

## Per-run pool diff

### 01-grid-outage

- Baseline candidates: 19
- Pretest candidates: 15
- Net-new tmdb_ids (8): 40663, 58770, 139329, 472921, 530076, 720321, 949698, 1484253
- Lost vs baseline (12): 33495, 33787, 46221, 100063, 111750, 190738, 194834, 210219, 370097, 431892

**Gap A targets already in baseline (not net-new):**
- Survival Family (tmdb 429918)

### 02-corporate-layoff

- Baseline candidates: 19
- Pretest candidates: 16
- Net-new tmdb_ids (6): 16020, 55561, 116741, 402907, 753232, 1161617
- Lost vs baseline (9): 16814, 53416, 56589, 71172, 88442, 133463, 485162, 762823, 1173076

**Gap A targets already in baseline (not net-new):**
- The Plan (tmdb 619090)
- At War (tmdb 485162)

### 03-election-upset

- Baseline candidates: 19
- Pretest candidates: 15
- Net-new tmdb_ids (7): 9440, 10411, 50033, 52657, 158715, 432301, 933554
- Lost vs baseline (11): 379, 21711, 46563, 100420, 239070, 342442, 376455, 532869, 536176, 1168015

**Gap A targets already in baseline (not net-new):**
- The Campaign (tmdb 77953)
- 120 Seconds to Get Elected (tmdb 239070)

### 07-migration-border

- Baseline candidates: 19
- Pretest candidates: 12
- Net-new tmdb_ids (5): 20348, 117251, 204046, 253412, 1014629
- Lost vs baseline (12): 1775, 9366, 49097, 127822, 151708, 210913, 252990, 273481, 362202, 1006462

**Gap A targets already in baseline (not net-new):**
- Transpecos (tmdb 381018)
- Sicario (tmdb 273481)

### 09-cultural-backlash

- Baseline candidates: 19
- Pretest candidates: 19
- Net-new tmdb_ids (14): 665, 4486, 48605, 63400, 98301, 126200, 128042, 216457, 270124, 323426, 468735, 665894, 1047128, 1250508
- Lost vs baseline (14): 27425, 32690, 45054, 118379, 133369, 179100, 197082, 333266, 446173, 525825

**Gap A targets already in baseline (not net-new):**
- L'Odissea (tmdb 194224)

## Center element granularity (OPEN c)

- Center counts: `{'result-0': 11, 'who-1': 10, 'who-3': 4, 'how-2': 2, 'who-0': 8, 'who-2': 5, 'result-1': 5, 'how-0': 5, 'result-3': 1, 'why-1': 1, 'result-2': 1, 'why-0': 2, 'where-0': 1, 'how-3': 1, 'who-4': 1}`
- Channel counts: `{'toned': 38, 'focalized': 20}`
- Focal who-* counts: `{'who-1': 10, 'who-2': 6, 'who-0': 3, 'who-3': 1}`
- Note: Centers span who/where/why/how/result element ids; observe whether salience-greedy who-* centers unlock POV focalization without over-coarse buckets.

