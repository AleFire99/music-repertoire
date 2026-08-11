---
name: backend-development
description: Use when adding or changing a backend endpoint, model, or migration in backend/src/repertoire — the model-to-tested-endpoint workflow for this FastAPI + SQLAlchemy + Alembic project.
---

## Workflow for a new/changed endpoint

1. Add or edit the SQLAlchemy model in `backend/src/repertoire/models/`.
2. Generate a migration: `docker compose exec backend uv run alembic revision --autogenerate -m "..."`. **Always review the generated migration by hand** — autogenerate misses some changes (renames, some constraint changes).
3. Apply it: `docker compose exec backend uv run alembic upgrade head`.
4. Add/update the Pydantic schema in `backend/src/repertoire/schemas/`.
5. Add/update the router in `backend/src/repertoire/api/`, register it in `main.py` if it's a new router.
6. Add a test in `backend/tests/` — real behavior against the test DB (see `testing` skill), not a smoke import.
7. Before considering it done: `uv run ruff check .`, `uv run mypy src`, `uv run pytest` — all inside the `backend` container or locally via `uv run` in `backend/`.

## Conventions already in place

- Sync SQLAlchemy (not async) — kept boring on purpose, see ADR 0002.
- `Depends(get_db)` FastAPI idiom — `ruff` has `B008` disabled specifically for this.
- Routers are prefixed under `/api` in `main.py`, not in the router files themselves.
