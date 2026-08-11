# Agent Model

These roles describe how Claude Code agents should divide responsibility on this project. **No orchestrator automation exists yet** — this is manual/human-driven guidance for how a person directs one or more Claude Code sessions, not a dispatch system. See [orchestration.md](orchestration.md) for the future multi-agent worktree conventions.

Introduce roles incrementally as the project needs them — do not spin up all of them for a small task.

## Architect

Requirements analysis, architecture, domain modeling, ADRs, task decomposition. Should generally **not** implement large amounts of application code — hands off well-scoped issues to Backend/Frontend agents.

## Backend Agent

Domain model, API, database, migrations, backend tests. Consults `docs/architecture.md`, the `backend-development` skill, and `docs/definition-of-done.md`.

## Frontend Agent

UI, UX, frontend state, frontend tests. Consults the `frontend-development` skill.

## Test Agent

Test strategy, missing tests, integration tests, end-to-end tests, regression testing. Consults the `testing` skill and `docs/testing.md`.

## Reviewer

Reviews implementation, checks acceptance criteria, finds edge cases, identifies architectural problems, checks tests. Should be independent of the implementation agent when practical (a fresh Claude Code session/context, not the same one that wrote the code). Consults the `code-review` skill and `docs/definition-of-done.md`.

## DevOps Agent

Docker, CI, CD, registries, deployment, release automation. Consults the `release` skill.

## How this maps to today's workflow

Right now, one Claude Code session typically plays several of these roles across a single feature (implement + self-review), because there's no orchestrator to run them concurrently in separate worktrees. That's expected at this stage — see [orchestration.md](orchestration.md) for when and how that changes.
