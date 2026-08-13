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

The current design system is **Minimal Monochrome Editorial** (established
by issue #105, replacing #102's teal "slick/modern" system wholesale) — a
"critical edition's index" aesthetic: pure neutral grayscale, one accent
(the "editor's blue pencil") reserved for annotation/reference only, and
`--radius: 0` everywhere. Reuse it rather than reintroducing ad hoc styling:

- Tokens (color, type, spacing) live as CSS custom properties in
  `frontend/src/app.css` — consume `var(--...)`, don't hardcode hex values
  or one-off `rem` sizes.
- `App.svelte` is a sidebar + single-active-view shell (`activeView`
  `$state` string, not a router) — it is not a scrolling stack of panels.
  A new top-level feature is a new nav entry + view branch, not a new
  section appended to the page.
- Wrap each view in a `SectionHeader.svelte` (serif headline, italic dek
  line, full-width hairline rule, then a filter/action row) rather than
  the old eyebrow-panel heading.
- Three type roles: `--font-serif` for headlines/hero numerals (via the
  `.numeral` utility), the existing `--font-sans` for UI chrome/forms/
  labels, `--font-mono` for genuinely tabular data (`.readout`).
- Use `.row-list` for list-of-items views, `.meta-line` for secondary
  metadata (values auto-joined by middle dots), `.icon-btn` for
  hover-revealed row actions (edit/delete), `.text-toggle`/`.toggle-row`
  for filter switches (not boxed `<select>`s), `.index-table` for tabular
  breakdowns, and the base `button`/`input`/`select`/`textarea` styles
  plus `.secondary`/`.danger` button variants — don't redefine these per
  component. The old `.chip`/`.chip-accent`/`.chip-quiet` pill badges are
  retired.
- Icons come from the hand-rolled sprite at `frontend/public/icons.svg` via
  `<Icon name="..." />` (`frontend/src/lib/Icon.svelte`) — don't add a new
  icon library or inline one-off SVGs.
- Create/edit interactions go through the shared `Modal.svelte` component,
  not an inline form rendered in the page flow. A form component used in a
  modal should accept an `onCancel` prop and render a Cancel button
  alongside its submit button.
- If a new element doesn't fit an existing pattern, add a token-driven
  utility class to `app.css` rather than inlining new colors/spacing.

## Before considering a change done

`docker compose exec frontend npm run check` (svelte-check — this is the lint+typecheck gate, there's no separate ESLint setup yet) and `npm run build`.
