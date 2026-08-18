# Music Repertoire

Personal music-learning and repertoire-management app: track the pieces you're learning, log practice sessions, store/reference sheet music, and (eventually) get deterministic music-theory analysis with LLM-generated explanations layered on top.

This project is also a deliberate learning lab for a full engineering workflow: Git Flow, Claude Code multi-agent conventions, CI/CD, and Docker — see [docs/agent-model.md](docs/agent-model.md) and [docs/orchestration.md](docs/orchestration.md).

Now at **v0.5** — the Repertoire and Practice epics are fully shipped; sheet-music file storage is the current epic in progress, followed by a jazz reference wiki and a manual-entry music-theory engine. See [docs/backlog.md](docs/backlog.md) for the exact shipped/planned breakdown and [docs/architecture.md](docs/architecture.md) for design decisions.

## Features

- **Pieces**: full CRUD with title, composer, key, tempo, difficulty, instrument, tags, favorites, status (backlog/learning/memorized/maintaining/performance-ready/archived), and per-piece learning goals. Table and card grid views.
- **Practice tracking**: session logging (date, duration, notes, rating, section), a stopwatch timer, current/longest streaks, weekly/monthly stats, section-level breakdowns, weekly time goals with progress, and recently-practiced/neglected views.
- **Repertoire lists**: named lists of pieces, plus a rotation planner for an "in-focus" working set.
- **Sheet music**: reference-only resources (URL, physical copy, local file path) or real uploaded PDFs stored and served by the app. Quick-upload creates a piece straight from a PDF, guessing title/composer via PDF text-layer extraction and a MusicBrainz lookup, then opens the edit form to confirm/correct.
- **UI**: a from-scratch "Iris" design system (Material 3-inspired, sidebar navigation, light/dark mode, no component library dependency).

## How to use it

Start the stack (below), then open the frontend at http://localhost:5173 — it's a normal single-page app, no separate setup needed beyond that. To explore or script against the API directly, see the API docs links further down.

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

## API docs

FastAPI generates interactive docs for free, no extra setup — once the backend is running:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Raw OpenAPI schema: http://localhost:8000/openapi.json
- Health check: http://localhost:8000/api/health

All application routes are mounted under `/api` (e.g. http://localhost:8000/api/pieces); the docs endpoints above are the only ones at the root.
