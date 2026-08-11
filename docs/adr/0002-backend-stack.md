# 0002 — Backend Stack: FastAPI + PostgreSQL + SQLAlchemy + Alembic

## Status

Accepted

## Context

Need a backend for a small personal CRUD app today that can grow into structured musical-analysis data (chord progressions, MIDI-derived structures) later, without a rewrite.

## Decision

Python + FastAPI + PostgreSQL + SQLAlchemy 2.0 (typed models) + Alembic (migrations) + pytest + Ruff + mypy, managed with `uv`.

Alternatives considered and rejected for v0.1:
- **Django** — batteries-included ORM/admin is more than a small API needs; FastAPI's explicit routing/typing fits the "boring, explicit" principle better here.
- **Flask** — less built-in typing/validation than FastAPI; would need extra libraries to match what FastAPI gives for free.
- **MongoDB** — the domain (pieces, practice sessions, eventually harmonic structures) is relational; Postgres's JSONB columns cover any semi-structured needs (e.g. chord progression data) without giving up relational integrity elsewhere.

## Consequences

Schema changes require an Alembic migration (enforced by [definition-of-done.md](../definition-of-done.md)). SQLAlchemy 2.0's native typing (`Mapped`/`mapped_column`) means no separate mypy plugin is needed.
