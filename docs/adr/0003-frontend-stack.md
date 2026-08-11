# 0003 — Frontend Stack: Svelte + TypeScript + Vite

## Status

Accepted

## Context

v0.1's UI is a couple of pages (piece list, piece detail later). Needs a modern, typed frontend without introducing more moving parts than a 2-page app warrants.

## Decision

Svelte (plain SPA, not SvelteKit) + TypeScript + Vite + npm, fully containerized in `docker-compose.yml` alongside the backend and database.

Alternatives considered and rejected for v0.1:
- **SvelteKit** — brings SSR, file-based routing, and server load functions; none of that is needed for a small client-only SPA hitting a separate FastAPI backend. Revisit if SSR/SEO ever becomes a real requirement (unlikely for a personal tool).
- **React** — equally valid choice; Svelte was picked instead as a deliberate preference, compiles to less runtime code, no virtual DOM overhead for a small app.

No state-management library, no router, and no CSS framework in v0.1 — none are justified yet by a 2-page app. `svelte-check` is the only automated frontend gate for now (acts as both lint and typecheck); a dedicated ESLint setup and a test framework (e.g. Vitest) are backlog items, not silently skipped.

## Consequences

The frontend dev server runs in its own container (`frontend/Dockerfile`, dev-mode only — no production nginx build yet) with hot reload via a bind mount, using an anonymous volume over `node_modules` so the Linux container's native dependencies don't get shadowed by the Windows host's `node_modules`.
