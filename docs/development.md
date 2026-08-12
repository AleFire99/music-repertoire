# Local Development

## Prerequisites

- Docker + Docker Compose
- (Optional, for editor tooling outside containers) Python 3.11 + [uv](https://docs.astral.sh/uv/), Node 24 + npm

## First-time setup

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec backend uv run alembic upgrade head
```

- Backend: http://localhost:8000/api/health, http://localhost:8000/api/pieces
- Frontend: http://localhost:5173

## Day-to-day

```bash
docker compose up -d          # start the stack
docker compose logs -f backend
docker compose down           # stop (data persists in the postgres_data volume)
```

### Backend commands (inside the `backend` container or locally via `uv run` in `backend/`)

```bash
docker compose exec backend uv run pytest
docker compose exec backend uv run ruff check .
docker compose exec backend uv run mypy src
docker compose exec backend uv run alembic revision --autogenerate -m "message"
docker compose exec backend uv run alembic upgrade head
```

### Frontend commands (inside the `frontend` container or locally via `npm` in `frontend/`)

```bash
docker compose exec frontend npm run check   # svelte-check, doubles as lint + typecheck
docker compose exec frontend npm run build
```

## Environment variables

See `.env.example` at repo root — consumed by both `docker-compose.yml` and `backend/src/repertoire/config.py`.

| Variable | Purpose |
|---|---|
| `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` | Postgres container credentials |
| `DATABASE_URL` | SQLAlchemy connection string used by the backend |
| `POSTGRES_HOST_PORT` / `BACKEND_HOST_PORT` / `FRONTEND_HOST_PORT` | Optional host port overrides — only needed for parallel worktrees, see below |

## Creating a feature

See [git-flow.md](git-flow.md) and the `git-flow` skill (`.claude/skills/git-flow/SKILL.md`) for the exact branch/commit sequence. Short version: branch `feature/issue-<n>-<slug>` off `develop`, implement, open a PR back to `develop`.

## Working on multiple features in parallel

A single checkout can only have one branch checked out at a time — two Claude Code sessions (or two terminals) working in the *same* folder will fight over branch switches and uncommitted changes. To genuinely work on two features at once (e.g. one Claude Code session per feature), use a separate **git worktree** per feature instead of a second clone.

### Automated setup

`scripts/new-feature.sh "<issue title>" "<issue body>" [label]` does the boilerplate for you: creates the GitHub issue, a worktree with the correctly-numbered branch off `develop`, a `.env` with ports derived from the issue number (so they never collide across worktrees without any scanning), and prints a ready-to-paste prompt for a new Claude Code session. It does **not** launch the session, watch its PR, merge it, or clean up afterwards — those stay manual/human-supervised (see [orchestration.md](orchestration.md) for why).

```bash
scripts/new-feature.sh "Add practice session recording" "Track piece, date, duration, notes per docs/backlog.md" feature
```

### Manual setup (what the script automates)

```bash
# from the main checkout
git worktree add ../music-repertoire-issue-12 -b feature/issue-12-<slug> develop
cd ../music-repertoire-issue-12
cp .env.example .env
# edit .env: set POSTGRES_HOST_PORT/BACKEND_HOST_PORT/FRONTEND_HOST_PORT to unused ports,
# e.g. 5433/8001/5174
docker compose up -d --build
docker compose exec backend uv run alembic upgrade head
```

This creates a sibling folder with its own working directory and branch, sharing the same `.git` history/objects — no need to re-clone or re-authenticate `gh`. Open a new Claude Code session with that folder as its working directory (new terminal/window, `cd` into it, or open it as a separate folder in your editor). Container/volume/network names are already namespaced automatically by Compose using the folder name, so only ports need overriding.

### Cleanup after merge

```bash
git worktree remove ../music-repertoire-issue-12
git branch -d feature/issue-12-<slug>
```

If `git worktree remove` fails on Windows with `Function not implemented`, it's usually an npm-created symlink/reparse point inside `node_modules` that git-bash's `rm` can't handle — delete the folder with PowerShell instead (`Remove-Item -Recurse -Force <path>`), then `git worktree prune`.

See [orchestration.md](orchestration.md) for the worktree conventions this is based on (written for a future multi-agent orchestrator, but the same rules apply to two humans/sessions working manually — one worktree, one branch, never shared).
