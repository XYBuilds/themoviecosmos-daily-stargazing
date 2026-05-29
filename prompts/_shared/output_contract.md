# Output Contract

> MVP minimal version. Add JSON schema / field-level constraints once the pipeline is stable.

## Output Format

* **Plain text, single paragraph.**
* No Markdown headings / lists / code blocks / wrapping the whole paragraph in quotes.
* No preamble ("Sure, here is...") and no postscript ("Hope this helps").
* Output the pseudo-overview itself, directly.

## Language & Length

* **Language: English** (the index is English-only; see `deentification_rules.md` rule 6).
* Length: **60 – 120 words**.
* Too long → the caller truncates at the nearest period.

## Style Baseline

* Like a TMDB / IMDb overview: describe the story plainly, judge sparingly, leave suspense.
* Do not write "this movie," "this film," "the director uses...".
* No digressions, no dedications, no explaining your own persona setup.

## Behavior on Failure (caller convention)

* If the model returns an empty string / pure refusal text / a length far out of bounds / a clear hard-rule violation (a named entity) → the caller logs it in the day's briefing `errors` section, the main flow continues, no retry (MVP).
