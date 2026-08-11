# Testing

## Philosophy

Tests protect meaningful behavior, not coverage numbers. Don't write a test that would pass even if the feature were broken.

## Backend

- `pytest`, run against a **real Postgres** database (`repertoire_test`, same container as dev — see `backend/tests/conftest.py`), not mocks.
- Fixtures: `_reset_schema` (autouse, creates/drops tables per test), `db` (session), `client` (FastAPI `TestClient` with `get_db` overridden to use the test session).
- A "real test" asserts on actual behavior — response status, response body, DB state — not `assert True` or a trivial import check.
- Run: `docker compose exec backend uv run pytest`

## Frontend

No automated test framework in v0.1 — deliberately deferred (see [backlog.md](backlog.md)). `npm run check` (svelte-check) is the only automated gate today: type errors and template errors.

## Integration / E2E

Not set up yet. When practice tracking or the analysis engine lands, add integration tests hitting the real API + DB, and consider Playwright for key user workflows (add a piece → log practice → see stats) once there's more than one page to click through.

## Definition of a passing PR

See [definition-of-done.md](definition-of-done.md). In short: `pytest`, `ruff check`, `mypy`, `svelte-check`, and `docker compose build` all succeed in CI before merge.
