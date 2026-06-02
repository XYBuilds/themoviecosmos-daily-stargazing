# Shared Hard Rules · De-entification

> SSOT: PRD v0.4 §4.3 · ADR-0002 · Phase 3.5 已实现「承重保留」例外（规则 2/4）。
> Every Persona's output must pass through this "anonymization" layer before it is vectorized for retrieval.
> Goal: make the pseudo-overview read like a "movie synopsis" rather than a "news bulletin," so it aligns with the style distribution of the movie library's overviews and improves retrieval relevance.

## Hard Rules (must not be violated)

1. **No real personal names**
   - Not allowed: Elon Musk / Biden / John Doe / a head of state / Taylor Swift
   - Replace with a role identity: "a tech oligarch" / "a political leader" / "a pop idol"

2. **Places — default abstract, load-bearing exception (ADR-0002)**
   - **Default**: replace real place names with environmental traits ("a northern port city" / "a war-torn inland enclave").
   - **Exception**: when a place name is **load-bearing** for surface/context resonance (e.g. Mumbai heatwave → Mumbai), you **may keep** that proper name instead of blurring it to "a coastal megacity."
   - Still avoid piling in full addresses or every tag from the deconstruction ladder unless needed.

3. **No real institutions / brands / parties / company names**
   - Not allowed: Tesla / the UN / the Republican Party / OpenAI / ByteDance
   - Replace with a type: "a multinational energy company" / "an international arbitration body forged by great powers" / "a ruling party" / "a maker company"

4. **Numbers and dates — default blur, load-bearing exception (ADR-0002)**
   - **Default**: blur to magnitude ("recently" / "a vast sum" / "thousands" / "one in ten").
   - **Exception**: when a **specific number or date is load-bearing** for the hook (death toll, temperature record, grid MW peak), you **may keep** it.
   - Do not copy every statistic from the deconstruction JSON by reflex.

5. **No journalistic boilerplate**
   - Banned: "it is reported" / "the statement said" / "the other day" / "sources said" / "according to" / "reportedly"

6. **Output language = English (unified)**
   - Regardless of the source material language, each pseudo-overview is always written in **English**.
   - Rationale: the movie index (TMDB tagline + overview) is English-only, so an English query is same-distribution and gives more stable Top-K retrieval. Display/copywriting in other languages happens in a later stage, not here.

## Soft Rules (keep the movie-synopsis voice)

* The subject must be "a / some / one [role]," never a named entity (unless rule 2 exception applies).
* Prefer the present tense (common in movie synopses).
* Length **60 – 120 words per pseudo**, **single paragraph** each.
* No meta-description at the end: no "A film about…" / "This movie tells…".
* Do not write about "directing style" or "cinematography"; write only the **core of the story**.

## Self-check (recite after writing each pseudo)

- [ ] No gratuitous real proper nouns (only load-bearing ones kept on purpose)?
- [ ] Subject is an abstract role, not a named entity (unless place exception)?
- [ ] No boilerplate words?
- [ ] Each pseudo length within bounds?
- [ ] Written in English?
- [ ] Reads like an IMDb / TMDB overview, not a news summary?
