---
name: code-review
description: Use when reviewing a PR or diff in this repo — the repo-specific Definition of Done checklist, distinct from generic code review.
---

Full checklist: `docs/definition-of-done.md`. This skill is the condensed review pass for this repo specifically:

- Is there a migration for every schema change, and does it look right by hand (not just autogenerate output)?
- Does every new/changed endpoint have a real test (see `testing` skill for what "real" means)?
- Any direct commit to `main`/`develop` in the branch history? (Should never happen — flag it if it did.)
- Conventional Commit messages?
- Does the PR description reference an issue and explain the "why," not just restate the diff?
- `ruff check`, `mypy`, `pytest` (backend) and `svelte-check`, `build` (frontend) all green in CI — don't approve on "works on my machine."
- Scope creep: does this PR quietly implement something from `docs/backlog.md`'s future epics (practice tracking, analysis engine, auth, etc.) that wasn't the issue's stated scope?

This is distinct from the general-purpose `code-review` skill/command — this one only checks repo-specific process, not general bug-hunting.
