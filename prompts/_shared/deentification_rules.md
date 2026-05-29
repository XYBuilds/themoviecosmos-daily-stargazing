# Shared Hard Rules · De-entification

> Every Persona's output must pass through this "anonymization" layer before it is vectorized for retrieval.
> Goal: make the pseudo-overview read like a "movie synopsis" rather than a "news bulletin," so it aligns with the style distribution of the movie library's overviews and improves retrieval relevance.

## Hard Rules (must not be violated)

1. **No real personal names**
   - Not allowed: Elon Musk / Biden / John Doe / a head of state / Taylor Swift
   - Replace with a role identity: "a tech oligarch" / "a political leader" / "a pop idol"

2. **No real place names / countries / cities**
   - Not allowed: New York / Gaza / China / Beijing / Silicon Valley
   - Replace with environmental traits: "a northern port city" / "a war-torn inland enclave" / "a great eastern power" / "a technological enclave"

3. **No real institutions / brands / parties / company names**
   - Not allowed: Tesla / the UN / the Republican Party / OpenAI / ByteDance
   - Replace with a type: "a multinational energy company" / "an international arbitration body forged by great powers" / "a ruling party" / "a maker company"

4. **No specific dates / exact amounts / precise numbers**
   - Not allowed: May 2026 / 3 billion dollars / 17,234 people
   - Blur to magnitude: "recently" / "a vast sum" / "thousands" / "one in ten"

5. **No journalistic boilerplate**
   - Banned: "it is reported" / "the statement said" / "the other day" / "sources said" / "according to" / "reportedly"

6. **Output language = English (unified)**
   - Regardless of the source news language (Chinese or English), the pseudo-overview is always written in **English**.
   - Rationale: the movie index (TMDB tagline + overview) is English-only, so an English query is same-distribution and gives more stable Top-K retrieval. Display/copywriting in other languages happens in a later stage, not here.

## Soft Rules (keep the movie-synopsis voice)

* The subject must be "a / some / one [role]," never a named entity.
* Prefer the present tense (common in movie synopses).
* Length **60 – 120 words**, **single paragraph**.
* No meta-description at the end: no "A film about…" / "This movie tells…".
* Do not write about "directing style" or "cinematography"; write only the **core of the story**.

## Self-check (recite after writing)

- [ ] No real proper nouns anywhere?
- [ ] Subject is an abstract role, not a named entity?
- [ ] No boilerplate words?
- [ ] Length within bounds?
- [ ] Written in English?
- [ ] Reads like an IMDb / TMDB overview, not a news summary?
