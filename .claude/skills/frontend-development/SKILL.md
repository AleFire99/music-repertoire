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

The current design system is **Modernist** (established by issue #107,
replacing #105's Minimal Monochrome Editorial wholesale after it read as
too severe/cold on live review) — imported directly from claude.ai/design
and customized with a blue accent in place of the source system's default
red. Flat and architectural: one typeface (Archivo, self-hosted) distinguished
only by weight, `--radius: 0` everywhere, strong 2px dividers between major
sections. Reuse it rather than reintroducing ad hoc styling:

- Tokens (color, type, spacing) live as CSS custom properties in
  `frontend/src/app.css` — consume `var(--...)`, don't hardcode hex values
  or one-off `rem` sizes.
- `App.svelte` is a sidebar + single-active-view shell (`activeView`
  `$state` string, not a router) — it is not a scrolling stack of panels.
  A new top-level feature is a new nav entry (in the "Practice" or
  "Library" sidebar group) + view branch, not a new section appended to
  the page.
- Wrap each view in a `SectionHeader.svelte` (kicker/title/subtitle, then
  a search/actions row) rather than the old eyebrow-panel heading.
- One family, two roles: `--font-heading` / `--font-body` both resolve to
  self-hosted Archivo, distinguished by `--font-heading-weight: 800`.
  `.readout` and `.numeral` (tabular durations, totals, stat digits) use
  the heading weight.
- Use `.card`/`.card-kicker`/`.card-title` for flat surface blocks (a 2px
  top edge carries the emphasis), `.tag`/`.tag-accent`/`.tag-neutral`/
  `.tag-outline` for chips and status pills, `.table` for tabular views
  (not a `.row-list` when the data has several comparable columns —
  Pieces is table-based), `.pill` for segmented filters, `.row-list` for
  simpler list-of-items views, `.meta-line` for secondary metadata,
  `.icon-btn` for hover-revealed row actions, and the base
  `button`/`input`/`select`/`textarea` styles plus
  `.primary`/`.secondary`/`.danger` button variants — don't redefine these
  per component.
- Icons come from the Lucide-style, hand-copied sprite at
  `frontend/public/icons.svg` (24x24 grid) via `<Icon name="..." />`
  (`frontend/src/lib/Icon.svelte`) — don't add a new icon library or
  inline one-off SVGs.
- Create/edit interactions go through the shared `Modal.svelte` component,
  not an inline form rendered in the page flow. A form component used in a
  modal should accept an `onCancel` prop and render a Cancel button
  alongside its submit button.
- Theme is `prefers-color-scheme` by default, with a manual toggle (sidebar
  footer) that sets `data-theme` on `<html>`, persisted to `localStorage`.
  A new component's dark-mode look must come from the existing tokens
  (which already flip under both the media query and `[data-theme]`), not
  a bespoke `@media` block.
- If a new element doesn't fit an existing pattern, add a token-driven
  utility class to `app.css` rather than inlining new colors/spacing.

## Before considering a change done

`docker compose exec frontend npm run check` (svelte-check — this is the lint+typecheck gate, there's no separate ESLint setup yet) and `npm run build`.
