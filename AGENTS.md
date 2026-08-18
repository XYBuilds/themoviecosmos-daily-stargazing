# Daily Stargazing Repository Guidance

Daily Stargazing is an independently owned editorial and publication repository for The Movie Cosmos. Chronicle owns product-level identity and producer contracts. This repository owns news intake, persona rewrite, retrieval, editor review, and Daily publication. Do not copy Chronicle-owned runtime, frontend, or galaxy-model rules into this repository.

## Agent skills

### Issue tracker

Issues live in the private Daily Stargazing GitLab project. Use the `glab` CLI for Issue and merge-request operations. See [`docs/agents/issue-tracker.md`](docs/agents/issue-tracker.md). Provider Issue numbers and URLs are aliases; portable identities use `tmc:daily:<ULID>`.

### Triage labels

Triage uses the five canonical Matt skills labels. See [`docs/agents/triage-labels.md`](docs/agents/triage-labels.md).

### Domain docs

Read `CONTEXT.md`, `docs/SSOT/`, and `docs/adr/` for Daily-local decisions. Create or update `CONTEXT.md` and ADRs only when domain terms or durable design decisions are actually resolved through the domain-modeling workflow. See [`docs/agents/domain.md`](docs/agents/domain.md).

## Delivery workflow

Repository delivery is **tool-neutral**. External discovery, specification, and review skills may help agents work, but they are not repository authority.

Required delivery checks, regardless of host:

- Work from an Issue-owned branch off an up-to-date default base (`main` unless otherwise specified).
- Run the verification that matches the changed scope (`python -m pytest` for the existing suite, plus any Issue-named checks). `git diff --check` is required.
- Delivery Issues and merge requests must include an explicit human risk declaration (R0–R3 + protected surfaces). Do not invent a path classifier.
- Do not rewrite accepted ADRs as silent edits.
- **Human merge and Issue closure approval are mandatory.** Agents may prepare evidence and open a merge request when authorized, but must not merge or close the Issue without explicit human approval.

Ignored `.env` values are replaceable Bitwarden deployment copies, not the secrets authority. Editorial and publication behavior stay outside P0 development-restore work.
