---
name: testing
description: Use when writing a backend test or checking test coverage for a change — pytest conventions and the "real test" bar for this project.
---

## Backend (pytest)

- Tests live in `backend/tests/`, named `test_*.py`.
- `conftest.py` provides: `_reset_schema` (autouse — creates/drops all tables per test against a real Postgres `repertoire_test` database), `db` (a session), `client` (FastAPI `TestClient` with `get_db` overridden to the test session).
- Write against the `client` fixture for endpoint tests; use `db` directly only for tests that need to set up state the API can't produce.
- Run: `docker compose exec backend uv run pytest` (Postgres must be up — `docker compose up -d postgres` first if running outside the full stack).

## What makes a test "real"

It must fail if the behavior it protects breaks. Assert on response status codes, response bodies, and/or DB state — not on the absence of exceptions alone. A test that would pass against a stub implementation isn't testing the real behavior.

## Frontend

No test framework yet (Vitest is backlog, see `docs/backlog.md`). Don't invent frontend unit tests without adding the framework properly first — flag it as a gap instead of writing a fake test.
