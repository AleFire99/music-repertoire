# Music Repertoire

Personal music-learning and repertoire-management app. Tracks pieces, sheet music sources, and practice sessions; eventually adds deterministic music-theory analysis with LLM-generated explanations.

This project is also a learning lab for a full engineering workflow: Git Flow, Claude Code multi-agent conventions, CI/CD, and Docker.

v0.1 is deliberately small — see [docs/architecture.md](docs/architecture.md) and [docs/backlog.md](docs/backlog.md) for scope. Start with [docs/development.md](docs/development.md) for local setup.

## Running the stack manually

Requires Docker + Docker Compose.

```bash
cp .env.example .env
docker compose up -d --build
docker compose exec backend uv run alembic upgrade head
```

- Backend: http://localhost:8000/api/health, http://localhost:8000/api/pieces
- Frontend: http://localhost:5173

Day-to-day:

```bash
docker compose up -d          # start the stack
docker compose logs -f backend
docker compose down           # stop (data persists in the postgres_data volume)
```

See [docs/development.md](docs/development.md) for backend/frontend check commands, environment variables, and running multiple features in parallel via worktrees.
