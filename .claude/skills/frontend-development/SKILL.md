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

## Styling convention (see docs/roadmap.md)

A real design system landed in issue #102 — the "manuscript" theme
(warm paper/ink palette, serif display type, brass/red accents). Reuse it
rather than reintroducing ad hoc styling:

- Tokens (color, type, spacing) live as CSS custom properties in
  `frontend/src/app.css` — consume `var(--...)`, don't hardcode hex values
  or one-off `rem` sizes.
- Wrap each top-level view section in a `.sheet` card with a
  `SectionHeader.svelte` (the staff-rule + barline heading).
- Use `.manuscript-list` for list-of-items views, `.chip` for
  status/tag/count-style badges, and the base `button`/`input`/`select`/
  `textarea` styles plus `.secondary`/`.danger` button variants — don't
  redefine these per component.
- If a new element doesn't fit an existing pattern, add a token-driven
  utility class to `app.css` rather than inlining new colors/spacing.

## Before considering a change done

`docker compose exec frontend npm run check` (svelte-check — this is the lint+typecheck gate, there's no separate ESLint setup yet) and `npm run build`.
