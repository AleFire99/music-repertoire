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

## Creating a feature

See [git-flow.md](git-flow.md) and the `git-flow` skill (`.claude/skills/git-flow/SKILL.md`) for the exact branch/commit sequence. Short version: branch `feature/issue-<n>-<slug>` off `develop`, implement, open a PR back to `develop`.
