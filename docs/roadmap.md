# Roadmap

Sequences *when* things get built, and states the interim UI convention while
visual design is deliberately deferred. `docs/backlog.md` is the flat,
authoritative list of what's in/out of scope per epic; this document only
orders the epics and records the feature-first decision so it doesn't stay
implicit.

## Sequencing principle

Feature-first: keep shipping backend + minimal-functional-frontend slices for
the Repertoire and Practice epics before investing in a dedicated
design/styling pass. This mirrors how v0.1 stayed scoped to Piece CRUD before
extending it — validate a feature's data model and UX shape cheaply before
styling something that might still change shape.

## Near-term (current epics, no new milestone needed to continue)

1. **Repertoire epic** (in progress) — status/tags (#18), full CRUD UI (#28),
   sheet resources (#43) done; favorites (#46) in progress. Remaining: goals,
   repertoire lists, performance history, repertoire rotation,
   key/tempo/difficulty/instrument fields.
2. **Practice epic** (in progress) — session recording (#31), basic stats
   (#41) done. Remaining: timer, weekly goals, statistics by week/month,
   neglected pieces, recently practiced, progress toward goals, practice
   streaks, section-level practice breakdowns.

Work continues one small slice at a time via `scripts/new-feature.sh`, same
cadence as issues #18–#46.

## UI design system (Iris, established by #114)

#107's **Modernist** pass shipped but the user still wanted something more
polished/rounded. #114 replaced it (not a reopen of #107 — same underlying
data/behavior, new presentation) with **Iris**, a Material 3-inspired
direction chosen from a second 3-way design panel (Soft Bench / Iris /
Commonplace) after comparing live rendered mockups of all three. This is
the final pick for v0.1 — no further redesign passes without a new,
separate request. New feature UI should follow it rather than
reintroducing ad hoc styling:

- **Direction**: a violet-leaning accent, with neutral surfaces tinted off
  that hue (`--surface-container*`, not true gray) so elevation reads
  through both shadow and tone shift, not shadow alone. Real two-layer
  elevation shadows (`--elevation-1..4`, a tight "key" shadow + a soft wide
  "ambient" shadow), state-layer hover/pressed overlays (a flat
  `color-mix()` overlay of a foreground color at a fixed opacity —
  `--state-hover: 0.08` / `--state-focus: 0.1` / `--state-pressed: 0.12`
  — composited over whatever's beneath, not hand-picked hover hexes), and
  a per-element radius scale (`--radius-xs` 8px small chips through
  `--radius-full` 999px pills/buttons/active-nav) replace Modernist's flat
  `--radius: 0` signature. Light/dark are both first-class
  (`prefers-color-scheme` default, plus a manual toggle in the sidebar
  footer that sets `data-theme` on `<html>`, persisted to `localStorage`
  — unchanged mechanism from #107). Dark mode's accent ramp gets lighter/
  less saturated, not the light value reused.
- **Shell, not a scrolling page**: `App.svelte` is a fixed-width sidebar +
  single active view, switched via a plain `activeView` `$state` string —
  explicitly not a router (unchanged since #105/#107). Five views: Today &
  Focus, Sessions, Progress, Pieces, Lists, grouped in the sidebar under
  "Practice" and "Library" section labels. The sidebar is collapsible to a
  64px icon-only rail (state persisted to `localStorage`) and its footer
  carries a weekly-goal mini progress bar (or a link to set one), the
  "Start a session" primary action, and the theme toggle.
- **Interaction pattern**: create/edit forms open in `Modal.svelte` —
  unchanged mechanics (native `<dialog>`, Escape/backdrop-click to close,
  explicit close button), now with a `size?: 'small' | 'medium' | 'large'`
  prop (default `'medium'`) mapping to a `data-size` attribute, a real
  `--elevation-4` shadow, and `--radius-xl` rounded corners instead of the
  old accent top-border + bare-color `--shadow` misuse. `PieceForm.svelte`
  uses `size="large"` and switches to a two-column field grid; the
  weekly-goal form uses `size="small"`. Every form component takes an
  `onCancel` prop.
- **Tokens**: colors, type, spacing, radius, elevation, and state-layer
  opacities are CSS custom properties in `frontend/src/app.css` —
  components consume tokens, never hardcode hex values or ad hoc sizes.
  Legacy token names (`--border`, `--surface-hover`, `--accent-tint`) are
  kept as aliases onto the new tokens so every view repaints consistently
  even where a component wasn't individually restyled in this pass.
- **Type — one family, two roles**: `--font-heading` / `--font-body` both
  resolve to self-hosted Figtree (`frontend/src/assets/fonts/`, weights
  400/500/700, `font-display: swap`), distinguished by
  `--font-heading-weight: 700` (down from Archivo's 800 — Material's own
  scale reads aggressive at that weight). `.readout` (tabular numerals for
  durations, totals, the session timer) and `.numeral` (bold tabular stat
  digits) both use the heading weight.
- **Iconography**: a Lucide-style, hand-copied (not the npm package)
  inline SVG sprite at `frontend/public/icons.svg` (24x24 grid), consumed
  via `Icon.svelte` (`<svg><use href="/icons.svg#{name}"/></svg>`). Color
  comes from the consumer's CSS `color` through `currentColor`.
- **Recurring patterns**: `.card` / `.card-kicker` / `.card-title` /
  `.card-body` / `.card-meta` (surface-container tiles at `--radius-lg`,
  `--elevation-1` resting / `--elevation-2` + 1px lift on hover — focus
  pieces, suggested-plan, repertoire lists, `PieceGrid.svelte` tiles),
  `.tag` / `.tag-accent` / `.tag-neutral` / `.tag-outline` (pill-shaped via
  `--radius-full` — genre chips, status pills, list counts), `.table` (a
  `--radius-md` surface-container shell with `--elevation-1`; the Pieces
  view also has a `PieceGrid.svelte` card alternative behind a
  `localStorage`-persisted view-mode toggle, same idiom as the
  sidebar-collapse state), `SectionHeader.svelte` (kicker/title/subtitle +
  a search/actions row, per-view), `.row-list` with `.accented`,
  `.meta-line`, `.row-hover` + `.icon-btn` (circular state-layer hover,
  revealed on row hover *or* keyboard focus-within), `Modal.svelte`, and
  shared `button`/`input`/`select`/`textarea` base styles plus
  `.primary`/`.secondary`/`.danger` variants (pill-shaped, state-layer
  hover).
- **Adding a new view**: reuse these tokens and patterns. Route any new
  create/edit interaction through `Modal.svelte`. If a new recurring
  element doesn't fit an existing pattern, add it to `app.css` as a
  token-driven utility class, not a one-off inline style.
- **Backend-derived addition shipped with this pass**: `PieceRead` gained a
  computed `sheet_resource_kinds` field (`backend/src/repertoire/schemas/
  piece.py`), populated in `list_pieces` via one grouped query against
  `sheet_resources` so `PieceGrid.svelte`'s resource-kind badge row doesn't
  cause an N+1 waterfall — no new endpoint, no migration (derived, not
  stored).
- **Two backend-derived additions from the prior pass (#107), unchanged**:
  the Progress view's 14-week consistency heatmap (`consistency_heatmap`
  on `GET /api/practice-sessions/stats`) and the Today & Focus view's
  suggested-plan card (`suggested_plan` on the same endpoint).

This was intentionally a single cross-cutting pass (not spread across
feature PRs) because a design system only holds together if it's applied
consistently everywhere at once.

## Longer-term (future epics, unchanged from docs/backlog.md)

- Music representation (MIDI/MusicXML import, chord/measure/section
  representation, annotations). Audio → MIDI → chord extraction remains a
  permanent non-goal.
- Music theory engine (deterministic analysis only — see
  `docs/architecture.md`'s "LLM is never the source of truth for musical
  facts" rule).
- Learning assistant (LLM explanations of theory findings, piece similarity,
  practice exercise generation).
- Workflow/infra: Gitea Actions experiment, production frontend Dockerfile,
  multi-agent orchestrator (`docs/orchestration.md`), CHANGELOG automation.

See `docs/backlog.md` for the authoritative per-epic item lists.
