---
name: frontend-development
description: Use when adding or changing a Svelte component or frontend feature in frontend/src — component/API-helper conventions for this Vite + Svelte + TypeScript project.
---

## Conventions

- API calls go through `frontend/src/lib/api.ts` — typed fetch helpers, one function per endpoint. Don't call `fetch` directly from components.
- Components live in `frontend/src/lib/`; `App.svelte` composes them.
- The Vite dev server proxies `/api/*` to the backend (`vite.config.ts`, `VITE_API_PROXY_TARGET` env var set by `docker-compose.yml`) — never hardcode a backend URL in a component.
- Svelte 5 runes (`$state`, `$effect`, `onMount`) — this project uses the modern Svelte 5 API, not the older `export let` / reactive-statement style.

## Do NOT add without explicit sign-off

- State-management library (no Redux/Zustand equivalent needed for this app's size)
- Router library (single page in v0.1)
- CSS framework

## Interim styling convention (see docs/roadmap.md)

Visual design is deliberately deferred until the Repertoire/Practice epics are
substantially built out. Until that dedicated pass starts, keep new feature
UI functional-only: reuse the minimal styling already in `App.svelte`
(system-ui font stack, single `max-width` container, `.error` class) rather
than introducing new visual patterns or per-feature polish.

## Before considering a change done

`docker compose exec frontend npm run check` (svelte-check — this is the lint+typecheck gate, there's no separate ESLint setup yet) and `npm run build`.
