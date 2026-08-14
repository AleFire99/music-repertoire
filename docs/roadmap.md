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

## UI design system (Modernist, established by #107)

#105's **Minimal Monochrome Editorial** pass shipped but read as too
severe/cold on live review. #107 replaced it (not a reopen of #105 — same
underlying data/behavior, new presentation) with **Modernist**, imported
directly from claude.ai/design and customized with a blue accent in place
of the source system's default red. New feature UI should follow it rather
than reintroducing ad hoc styling:

- **Direction**: flat and architectural — one typeface (Archivo,
  self-hosted) distinguished only by weight, `--radius: 0` /
  `--radius-sm: 0` everywhere (the loudest structural decision, unchanged
  from #105), and strong 2px dividers between major sections (1px for
  repeated row separators inside tables/lists) rather than hairlines. The
  accent is used sparingly — the primary action, the active-nav rail, small
  emphasis — the system is mostly ink on ground. Light/dark are both
  first-class (`prefers-color-scheme` default, plus a manual toggle in the
  sidebar footer that sets `data-theme` on `<html>`, persisted to
  `localStorage` — same "plain state, no new dependency" approach as the
  sidebar-collapse state).
- **Shell, not a scrolling page**: `App.svelte` is a fixed-width sidebar +
  single active view, switched via a plain `activeView` `$state` string —
  explicitly not a router (unchanged from #105). Six views: Today & Focus,
  Sessions, Progress, Pieces, Sheet Music, Lists, grouped in the sidebar
  under "Practice" and "Library" section labels. The sidebar is collapsible
  to a 64px icon-only rail (state persisted to `localStorage`) and its
  footer carries a weekly-goal mini progress bar, the "Start a session"
  primary action, and the theme toggle.
- **Interaction pattern**: create/edit forms open in `Modal.svelte`
  (unchanged mechanics — native `<dialog>`, Escape/backdrop-click to close,
  explicit close button, now with a 3px accent top border). Every form
  component takes an `onCancel` prop.
- **Tokens**: colors, type, and spacing are CSS custom properties in
  `frontend/src/app.css` — components consume tokens, never hardcode hex
  values or ad hoc sizes.
- **Type — one family, two roles**: `--font-heading` / `--font-body` both
  resolve to self-hosted Archivo (`frontend/src/assets/fonts/`, weights
  400/600/800, `font-display: swap`), distinguished by
  `--font-heading-weight: 800`. `.readout` (tabular numerals for durations,
  totals, the session timer) and `.numeral` (bold tabular stat digits) both
  use the heading weight.
- **Iconography**: a Lucide-style, hand-copied (not the npm package)
  inline SVG sprite at `frontend/public/icons.svg` (24x24 grid), consumed
  via `Icon.svelte` (`<svg><use href="/icons.svg#{name}"/></svg>`). Color
  comes from the consumer's CSS `color` through `currentColor`.
- **Recurring patterns**: `.card` / `.card-kicker` / `.card-title` /
  `.card-body` / `.card-meta` (flat surface blocks with a 2px top edge
  carrying the emphasis — focus pieces, suggested-plan, repertoire lists),
  `.tag` / `.tag-accent` / `.tag-neutral` / `.tag-outline` (genre chips,
  status pills, list counts), `.table` (real tables — the Pieces view is
  table-based per the imported design), `.pill` (segmented status filters),
  `SectionHeader.svelte` (kicker/title/subtitle + a search/actions row,
  per-view), `.row-list` with `.accented`, `.meta-line`, `.icon-btn`,
  `Modal.svelte`, and shared `button`/`input`/`select`/`textarea` base
  styles plus `.primary`/`.secondary`/`.danger` variants.
- **Adding a new view**: reuse these tokens and patterns. Route any new
  create/edit interaction through `Modal.svelte`. If a new recurring
  element doesn't fit an existing pattern, add it to `app.css` as a
  token-driven utility class, not a one-off inline style.
- **Two small backend-derived additions shipped with this pass**: the
  Progress view's 14-week consistency heatmap (`consistency_heatmap` on
  `GET /api/practice-sessions/stats`, a 98-day daily-minutes series) and
  the Today & Focus view's suggested-plan card (`suggested_plan` on the
  same endpoint — a deterministic heuristic over due/overdue goals,
  longest-neglected pieces, and low-rated last sessions; no LLM, no
  music-theory logic, same category as the neglected-pieces feature #56).

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
