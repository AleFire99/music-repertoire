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

Worktrees live **inside the repo**, under `.worktrees/` (gitignored) — not as sibling folders next to the repo, which would clutter the parent directory alongside unrelated projects. `docker compose`'s automatic project naming still works fine since it's based on each worktree's own leaf directory name (`issue-12`, `issue-31`, ...), which stays unique.

### Automated setup

`scripts/new-feature.sh "<issue title>" "<issue body>" [label]` does the boilerplate for you: creates the GitHub issue, a worktree at `.worktrees/issue-<n>` with the correctly-numbered branch off `develop`, a `.env` with ports derived from the issue number (so they never collide across worktrees without any scanning), and prints a ready-to-paste prompt for a new Claude Code session. It does **not** launch the session, watch its PR, merge it, or clean it up afterwards — those stay manual/human-supervised (see [orchestration.md](orchestration.md) for why).

```bash
scripts/new-feature.sh "Add practice session recording" "Track piece, date, duration, notes per docs/backlog.md" feature
```

### Manual setup (what the script automates)

```bash
# from the main checkout
git worktree add .worktrees/issue-12 -b feature/issue-12-<slug> develop
cd .worktrees/issue-12
cp .env.example .env
# edit .env: set POSTGRES_HOST_PORT/BACKEND_HOST_PORT/FRONTEND_HOST_PORT to unused ports,
# e.g. 5433/8001/5174
docker compose up -d --build
docker compose exec backend uv run alembic upgrade head
```

This creates a working directory and branch sharing the same `.git` history/objects as the main checkout — no need to re-clone or re-authenticate `gh`.

**Getting a Claude Code session actually into that folder is not optional or automatic.** In the VSCode extension, a new session's working directory is not necessarily the worktree just because a human meant it to be — a session that isn't told to switch will simply run every command against wherever it started (usually the main checkout), silently corrupting branch/file state there instead. Two ways to get it right:

- Have the session call the `EnterWorktree` tool with `path=<absolute worktree path>` as its first action (this is what `scripts/new-feature.sh`'s generated prompt now instructs it to do) — the session must not assume it's already there just because it was told so in text.
- Or open the worktree folder directly as its own VSCode window/workspace (not a tab within the main repo's window) before starting Claude Code in it.

This was found the hard way: a feature session ended up making uncommitted model/API/frontend changes directly in the main checkout instead of its `.worktrees/issue-<n>` folder, because nothing forced the working-directory switch.

### Cleanup after merge

`scripts/cleanup-worktrees.sh` removes any worktree whose branch has an actual **merged PR on GitHub** and no uncommitted changes — run it any time, it's safe to call repeatedly and skips (with a reason) anything not ready:

```bash
scripts/cleanup-worktrees.sh
```

It deliberately doesn't trust "branch is merged into develop" as the sole signal — a freshly created worktree with no commits yet trivially satisfies that too, and would be wrongly deleted right after `new-feature.sh` creates it. Requiring a real merged PR avoids that.

Before deleting a worktree it also tears down its docker compose stack — `docker compose down --rmi local --volumes --remove-orphans` from inside the worktree, removing that worktree's containers, its locally-built `backend`/`frontend` images, and its postgres volume (never the shared pulled `postgres:16-alpine` base image). If Docker isn't running it skips this step with a note rather than failing.

**Windows caveat, live-verified while building this:** deleting the worktree folder afterward can fail if something still has a file handle open on it — most often an editor's file watcher indexing `.worktrees/` (it's inside the open workspace, unlike the old sibling-folder layout), occasionally Docker Desktop's file-sharing layer briefly after teardown. The script retries a few times; if it still can't delete the folder, it says so plainly and leaves it for you to remove by hand once whatever's holding it releases, followed by `git worktree prune` — it does not loop forever or pretend success.

Manual equivalent, if you'd rather do it by hand:

```bash
git worktree remove .worktrees/issue-12
git branch -d feature/issue-12-<slug>
```

If `git worktree remove` fails on Windows with `Function not implemented`, it's usually an npm-created symlink/reparse point inside `node_modules` that git-bash's `rm` can't handle — delete the folder with PowerShell instead (`Remove-Item -Recurse -Force <path>`), then `git worktree prune`. `cleanup-worktrees.sh` already does this fallback automatically.

See [orchestration.md](orchestration.md) for the worktree conventions this is based on, and for guidance on when running features in parallel is actually worth it versus working sequentially.
