# Judge rerun pilot: runs 05 & 06 (3.10.1b logic 0-guard)

- **prompt_version**: 3.10.1b-logic-0-guard
- **eval_dir**: `output/Eval/phase3.10-visible`
- **prior scores**: `llm-judge-scores-rerun-05-06.json.bak` (holdout baseline)
- **rerun output**: `llm-judge-scores-rerun-05-06.json`

## Score distribution (judge 0/1/2)

| run | before | after |
|---|---|---|
| 05-climate-disaster | {0: 3, 1: 7, 2: 7} | {0: 9, 1: 4, 2: 4} |
| 06-tech-monopoly | {0: 4, 1: 15} | {0: 17, 1: 2} |

## Transition counts (all pairs)

- 0→0: **7**
- 1→0: **18**
- 1→1: **3**
- 1→2: **1**
- 2→0: **1**
- 2→1: **3**
- 2→2: **3**

## judge=1 → 0 (18 pairs)

### The Sweet Hereafter (1997) [THE-JESTER] (05-climate-disaster)
- **tmdb_id**: 10217
- **old type**: 表层沾边
- **new rationale**: No concrete load-bearing surface element shared (child deaths are abstract, and disasters differ: flood vs. bus accident). Underlying logic cannot be defined with a 'X under constraint Z drives Y' sentence specific to both without failing the 0-guard (e.g., unrelated child tragedy news would also fit).

### Jet Stream (2013) [THE-MAGICIAN, THE-CAREGIVER] (05-climate-disaster)
- **tmdb_id**: 210219
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: Extreme weather phenomena, under the constraint of overwhelmed natural barriers or unpredictable atmospheric conditions, force emergency evacuations and scientific interventions to prevent catastrophic loss of life.
- **new rationale**: No concrete, load-bearing surface element shared; any weather-related news could fit the film. Underlying logic sentence (e.g., 'Unpredictable weather events under infrastructure constraints drive catastrophes') is too general, failing the 0-guard as it would hold for unrelated news paired with the film.

### Geostorm (2017) [THE-OUTLAW] (05-climate-disaster)
- **tmdb_id**: 274855
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: Human-engineered control systems under environmental and operational constraints drive catastrophic failures requiring urgent response — true of both the news' flood management systems failing under heavy rains and the film's satellite climate-control system malfunctioning.
- **new rationale**: No load-bearing surface element: floods or disasters are too abstract and not specific, failing the 0-guard as unrelated news (e.g., earthquake) could pair equally with Geostorm. Underlying logic fails: while a causal sentence like 'environmental control systems under extreme natural forces drive failures' could be written, it is too broad and would hold for unrelated news (e.g., power grid failure), so no specific engine is shared.

### World Gone Wild (1987) [THE-OUTLAW] (05-climate-disaster)
- **tmdb_id**: 38141
- **old type**: 表层沾边
- **new rationale**: Water is a shared surface element, but it fails the 0-guard as unrelated news (e.g., drought) could resonate equally with the film's theme. No common 'X under constraint Z drives Y' sentence holds because the news involves water abundance causing floods, while the film centers on water scarcity driving conflict—opposite causal engines.

### Flood (2007) [THE-SAGE, THE-INNOCENT, THE-EVERYMAN, THE-CAREGIVER, THE-LOVER] [优质·多agent] (05-climate-disaster)
- **tmdb_id**: 6309
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: Extreme weather-induced water surges, under the constraint of infrastructure capacity, drive catastrophic flooding that endangers human populations.
- **new rationale**: Surface element 'flood' is generic; many unrelated flood news items could pair with the film equally well, failing the 0-guard. Underlying logic 'extreme water under constraint drives destruction' is too general and not specific to this pair, failing the logic 0-guard.

### A Ticket to Space (2006) [THE-INNOCENT, THE-HERO, THE-CREATOR, THE-MAGICIAN, THE-JESTER] [优质·多agent] (06-tech-monopoly)
- **tmdb_id**: 13748
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: Regulatory or governmental authorities, under legal constraints or public scrutiny, drive corrective actions to address anti-competitive behavior or communication gaps — true of both news and film.
- **new rationale**: No concrete, nameable surface element shared (e.g., setting, occupation, event type) that is load-bearing; abstract government-action pairing fails 0-guard. No specific causal-stakes engine invariant under POV/scale; any broad 'X under constraint Z drives Y' sentence would hold for unrelated news items paired with the film, so Axis 2 = NO.

### The Last One of the Six (1941) [THE-SAGE] (06-tech-monopoly)
- **tmdb_id**: 142977
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: Past profitable actions under constraint of accountability or revelation drive investigative and punitive outcomes.
- **new rationale**: No concrete, load-bearing surface element is shared (e.g., news is about EU regulatory fine for digital market abuse, film is a 1940s Paris murder mystery). No underlying causal-stakes engine can be formulated that is literal and specific to both without failing the logic 0-guard (e.g., a generic misconduct sentence applies to many unrelated scenarios).

### The Cat (1988) [THE-RULER, THE-LOVER] [优质·多agent] (06-tech-monopoly)
- **tmdb_id**: 148866
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: An actor under strict external oversight drives self-beneficial actions that exploit systemic opportunities and provoke enforcement responses.
- **new rationale**: No shared concrete, load-bearing surface element (e.g., setting, occupation, event type). Underlying logic fails the 0-guard: a generic sentence like 'a powerful actor under external oversight uses hidden tactics to favor its own interests' would hold for many unrelated news items paired with the film, and no specific causal engine ties Google's search self-preferencing to the bank robbery's hidden mastermind.

### Stolen: Heist of the Century (2025) [THE-OUTLAW] (06-tech-monopoly)
- **tmdb_id**: 1513598
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: Entities, under the constraint of prohibitive systems, drive risky actions to secure high-stakes financial or competitive gains — true of both Google's self-preferencing under EU regulations and the thieves' heist under security and legal barriers.
- **new rationale**: No concrete surface element shared (news is about digital regulatory fines, film is about a physical diamond heist). No specific underlying logic engine that passes the falsifiable causal counter-test and 0-guard; any broad 'actors under constraints drive illicit actions' sentence would apply to unrelated news items paired with the film, making it non-specific.

### Dead Weight (2002) [THE-JESTER] (06-tech-monopoly)
- **tmdb_id**: 18457
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: Under legal or personal constraints, pursuers drive actions to penalize or recover from entities that wrongfully appropriate advantages or assets.
- **new rationale**: No concrete surface element is shared: the news centers on EU regulatory fines for search self-preferencing, while the film focuses on a convict's chase to recover a lottery ticket. For underlying logic, no 'X under constraint Z drives Y' sentence can be written that is literally true of both without being overly abstract or failing the specificity test (e.g., regulatory enforcement vs. personal pursuit are distinct engines).

### The Clearstream Affair (2015) [THE-EVERYMAN, THE-HERO, THE-MAGICIAN] (06-tech-monopoly)
- **tmdb_id**: 320318
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: European regulatory or judicial authorities, under the constraint of competition or anti-corruption laws, drive investigations and penalties against large institutions for alleged market or financial misconduct.
- **new rationale**: No concrete surface element shared (news focuses on tech/digital markets, film on banking finance); underlying causal logic is too broad (e.g., 'regulatory or investigative pressure drives exposure of misconduct') and fails the logic 0-guard as it would apply to many unrelated news-film pairs.

### Gabbar Is Back (2015) [THE-HERO, THE-CAREGIVER, THE-EVERYMAN, THE-EXPLORER, THE-CREATOR] (06-tech-monopoly)
- **tmdb_id**: 337876
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: Harmful self-interest that undermines public good under regulatory or moral constraints drives enforcement actions to restore fairness.
- **new rationale**: No concrete surface element is load-bearing in both stories; underlying logic differs, with no specific causal engine shared between regulatory antitrust enforcement and vigilante justice.

### The International (2009) [THE-LOVER, THE-OUTLAW, THE-EVERYMAN] (06-tech-monopoly)
- **tmdb_id**: 4959
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: A powerful corporation's misconduct under legal or regulatory constraints drives authorities or investigators to enforce accountability through penalties or pursuit.
- **new rationale**: No concrete surface element overlaps; the underlying logic (legal accountability for powerful institutions) is too general and would hold for unrelated news items, failing the specificity test.

### Nothing to Declare (2010) [THE-EXPLORER, THE-CREATOR] [优质·多agent] (06-tech-monopoly)
- **tmdb_id**: 52077
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: Authority figures, under the constraint of shifting regulatory boundaries, drive punitive or collaborative measures to uphold order.
- **new rationale**: No shared concrete surface element: news is about digital market regulation and fines for self-preferencing, film is about physical border elimination and customs officer collaboration. No specific underlying logic engine: cannot write a bidirectional 'X under constraint Z drives Y' sentence true for both without being overly general (e.g., 'regulatory changes drive enforcement or adaptation' applies to many unrelated news-film pairs, failing the logic 0-guard).

### Speaking of Murder (1957) [THE-OUTLAW, THE-JESTER] (06-tech-monopoly)
- **tmdb_id**: 58926
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: Entities engaging in concealed advantageous practices under the constraint of exposure drive institutional or personal confrontations.
- **new rationale**: No concrete, nameable surface element is load-bearing in both stories (e.g., EU regulation vs. Paris garage crime). For underlying logic, no 'X under constraint Z drives Y' sentence can be written that is specific to both and passes the 0-guard; the news involves regulatory penalties for self-preferencing, while the film involves criminal deception and informer suspicion, with no invariant causal engine.

### Special Section (1975) [THE-EVERYMAN, THE-EXPLORER, THE-CREATOR, THE-RULER, THE-SAGE, THE-LOVER] [优质·多agent] (06-tech-monopoly)
- **tmdb_id**: 79921
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: Governing authorities under external regulatory or coercive constraints drive disproportionate punitive enforcement actions against selected targets — true of both the EU fining Google under the Digital Markets Act and the Vichy government executing innocent men under Nazi demands.
- **new rationale**: No shared concrete, load-bearing surface element: news is about EU regulatory fine for anti-competitive search practices, film is about Nazi-occupied France sham trial. Underlying logic fails: no specific 'X under constraint Z drives Y' sentence can be written that is true for both without being too general (e.g., authorities enforcing rules against violators), which would also apply to unrelated news paired with the film, violating the logic 0-guard.

### To Skin a Spy (1966) [THE-MAGICIAN, THE-CAREGIVER] [优质·多agent] (06-tech-monopoly)
- **tmdb_id**: 82098
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: Official enforcers under strict institutional constraints drive corrective actions against rule violators to uphold systemic order and integrity.
- **new rationale**: No concrete shared surface elements (news focuses on EU digital regulation, film on espionage); no specific 'X under constraint Z drives Y' sentence holds for both without being overly vague or passing the logic 0-guard for unrelated pairs.

### Your Lucky Day (2023) [THE-LOVER, THE-JESTER] (06-tech-monopoly)
- **tmdb_id**: 923993
- **old type**: 深层共振（仅逻辑，无表层）
- **old causal_test**: The pursuit of substantial financial rewards under restrictive conditions drives actors to unethical or violent means, true of both the EU fining Google for anti-competitive self-preferencing and the hostage violence over a lottery ticket in the film.
- **new rationale**: No load-bearing concrete surface element shared; news centers on regulatory fines for self-preferencing in digital markets, while film focuses on a hostage situation over lottery winnings. Underlying logics diverge: news involves institutional enforcement of competition laws, film involves personal moral escalation under financial duress, failing the causal-test for a bidirectional invariant engine.

## judge=2 regressions (4 pairs)

- **Raining Cats and Frogs (2003) [THE-HERO, THE-EXPLORER, THE-INNOCENT, THE-CREATOR, THE-OUTLAW]** (05-climate-disaster, tmdb 22624): 2→1 (强共振（表层 + 逻辑） → 深层共振（仅逻辑，无表层）)
- **Water Wrackets (1978) [THE-JESTER, THE-MAGICIAN, THE-HERO]** (05-climate-disaster, tmdb 249011): 2→0 (强共振（表层 + 逻辑） → None)
- **Tidal Wave (2009) [THE-EXPLORER]** (05-climate-disaster, tmdb 33196): 2→1 (强共振（表层 + 逻辑） → 深层共振（仅逻辑，无表层）)
- **Dry (2022) [THE-INNOCENT, THE-EVERYMAN]** (05-climate-disaster, tmdb 797840): 2→1 (强共振（表层 + 逻辑） → 深层共振（仅逻辑，无表层）)

## Recommendation

- **Flag**: 4 prior judge=2 pair(s) dropped to 0/1 — spot-check before full holdout.
- Logic 0-guard aggressively demoted generic TYPE_DEEP / surface-only causal_test sentences; pilot shows intended tightening.
- **Suggest**: spot-check 2–3 demoted pairs plus all 2→0/1 regressions; if acceptable, proceed full holdout rerun with same prompt_version.
- If demotions feel over-broad, tune wording (e.g. clarify unrelated-news test applies primarily to TYPE_DEEP score-1 logic-only paths).
