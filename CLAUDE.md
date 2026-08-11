# CLAUDE.md

## Purpose

Personal music-learning and repertoire-management app: pieces, sheet-music sources, practice tracking, eventually deterministic music-theory analysis with LLM-generated explanations. Also a deliberate learning lab for Git Flow, CI/CD, Docker, and multi-agent Claude Code development — the engineering process is a first-class requirement here, not incidental. See [docs/architecture.md](docs/architecture.md).

**v0.1 ("Repertoire Foundation") is intentionally small: Piece CRUD only.** Do not expand scope without an explicit new milestone.

## Repository layout

```
backend/          ← FastAPI + SQLAlchemy + Alembic (uv-managed), src/repertoire/
frontend/         ← Svelte + TypeScript + Vite
docs/             ← architecture, git-flow, testing, agent-model, orchestration, DoD, backlog, adr/
.claude/          ← skills, hooks, settings.json
.github/          ← CI workflow, issue templates, PR template, CODEOWNERS
docker-compose.yml ← 3 services: postgres, backend, frontend
```

## Tech stack

Backend: Python, FastAPI, PostgreSQL, SQLAlchemy 2.0, Alembic, pytest, Ruff, mypy, uv.
Frontend: TypeScript, Svelte, Vite, npm.
Runtime: Docker Compose, fully containerized (no native dev-server dependency).

## Git Flow (critical)

Never commit directly to `main` or `develop`. Always branch from `develop` (`feature/issue-<n>-<slug>`), open a PR back to `develop`, wait for CI, then merge. Conventional Commits required (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `ci:`, `chore:`). Full detail: [docs/git-flow.md](docs/git-flow.md).

## Common commands

```bash
docker compose up -d --build
docker compose exec backend uv run pytest
docker compose exec backend uv run ruff check .
docker compose exec backend uv run mypy src
docker compose exec backend uv run alembic revision --autogenerate -m "..."
docker compose exec backend uv run alembic upgrade head
docker compose exec frontend npm run check   # svelte-check: lint + typecheck
docker compose exec frontend npm run build
```

## Definition of Done

See [docs/definition-of-done.md](docs/definition-of-done.md). Use judgment — not every item applies to trivial changes.

## Agent roles

See [docs/agent-model.md](docs/agent-model.md) and [docs/orchestration.md](docs/orchestration.md). **No orchestrator automation exists** — this is manual guidance for how a human directs Claude Code sessions, not a dispatch system. Don't build orchestration automation without an explicit request.

## Skills available

- `git-flow` — feature/release/hotfix branch command sequences
- `backend-development` — model → migration → schema → router → test workflow
- `frontend-development` — Svelte component conventions
- `testing` — pytest conventions, test DB setup
- `code-review` — repo-specific review checklist
- `release` — release branch → tag → back-merge sequence

## v0.1 scope guardrails (do NOT build yet)

- Practice tracking, sheet-music resources, music-theory analysis engine — see [docs/backlog.md](docs/backlog.md) future epics
- Multi-agent orchestrator automation
- Authentication/authorization
- Kubernetes, microservices, event sourcing, CQRS, message brokers
- Audio → MIDI → chord extraction (permanent non-goal, not just deferred)

If a task seems to need one of these, stop and confirm scope before proceeding rather than building it silently.

## Safety hook

`.claude/hooks/guard-git.sh` blocks `git commit` on `main`/`develop` and warns on force-push. This is a **convenience nudge**, not a verified technical boundary — its exact hook schema was not confirmed against this Claude Code build at write time. Verify with `/hooks` before relying on it; real protection belongs to GitHub branch protection rules.

## General rules

Read the relevant doc before modifying code in that area. Make the smallest coherent change for the issue at hand. Don't rewrite unrelated code or silently change architecture. Never `git reset --hard`, force-push, or use `--no-verify` unless explicitly instructed. Don't modify another agent's worktree.
