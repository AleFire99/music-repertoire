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

The current design system is **Iris** (established by issue #114, replacing
#107's Modernist), a Material 3-inspired direction: a violet-leaning accent,
neutral surfaces tinted off that hue (`--surface-container*`, not true
gray), real two-layer elevation shadows (`--elevation-1..4`), state-layer
hover/pressed overlays (`color-mix()` composited at `--state-hover` /
`--state-focus` / `--state-pressed` opacity), and a per-element radius
scale (`--radius-xs` through `--radius-full`) in place of Modernist's flat
`--radius: 0`. Reuse it rather than reintroducing ad hoc styling:

- Tokens (color, type, spacing, radius, elevation, state-layer opacity)
  live as CSS custom properties in `frontend/src/app.css` — consume
  `var(--...)`, don't hardcode hex values or one-off `rem` sizes. Some
  legacy names (`--border`, `--surface-hover`, `--accent-tint`) are kept as
  aliases onto the new tokens for components not individually restyled —
  prefer the new names (`--outline`, `--outline-variant`, the
  `--elevation-*`/`--radius-*` scales) in new code.
- `App.svelte` is a sidebar + single-active-view shell (`activeView`
  `$state` string, not a router) — it is not a scrolling stack of panels.
  A new top-level feature is a new nav entry (in the "Practice" or
  "Library" sidebar group) + view branch, not a new section appended to
  the page.
- Wrap each view in a `SectionHeader.svelte` (kicker/title/subtitle, then
  a search/actions row) rather than the old eyebrow-panel heading.
- One family, two roles: `--font-heading` / `--font-body` both resolve to
  self-hosted Figtree, distinguished by `--font-heading-weight: 700`.
  `.readout` and `.numeral` (tabular durations, totals, stat digits) use
  the heading weight.
- Use `.card`/`.card-kicker`/`.card-title` for surface-container tiles
  (`--radius-lg`, elevation promotes + 1px lift on hover),
  `.tag`/`.tag-accent`/`.tag-neutral`/`.tag-outline` for pill-shaped chips
  and status pills, `.table` for tabular views (not a `.row-list` when the
  data has several comparable columns — Pieces is table-based, with a
  `PieceGrid.svelte` card-view alternative behind a view-mode toggle),
  `.row-list` for simpler list-of-items views, `.meta-line` for secondary
  metadata, `.row-hover` on the row element + `.icon-btn` for
  hover-*or*-focus-revealed row actions (circular state-layer background),
  and the base `button`/`input`/`select`/`textarea` styles plus
  `.primary`/`.secondary`/`.danger` button variants — don't redefine these
  per component.
- Icons come from the Lucide-style, hand-copied sprite at
  `frontend/public/icons.svg` (24x24 grid) via `<Icon name="..." />`
  (`frontend/src/lib/Icon.svelte`) — don't add a new icon library or
  inline one-off SVGs.
- Create/edit interactions go through the shared `Modal.svelte` component,
  not an inline form rendered in the page flow. `Modal` takes a
  `size?: 'small' | 'medium' | 'large'` prop (default `'medium'`) — use
  `'large'` for field-heavy forms (e.g. `PieceForm`, which switches to a
  two-column grid at that size) and `'small'` for single-field forms. A
  form component used in a modal should accept an `onCancel` prop and
  render a Cancel button alongside its submit button.
- Theme is `prefers-color-scheme` by default, with a manual toggle (sidebar
  footer) that sets `data-theme` on `<html>`, persisted to `localStorage`.
  A new component's dark-mode look must come from the existing tokens
  (which already flip under both the media query and `[data-theme]`), not
  a bespoke `@media` block.
- If a new element doesn't fit an existing pattern, add a token-driven
  utility class to `app.css` rather than inlining new colors/spacing.

## Before considering a change done

`docker compose exec frontend npm run check` (svelte-check — this is the lint+typecheck gate, there's no separate ESLint setup yet) and `npm run build`.
