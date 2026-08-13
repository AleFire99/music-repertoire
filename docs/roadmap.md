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

## UI design system (Minimal Monochrome Editorial, established by #105)

Issue #102's teal-accented "slick/modern/minimal" pass was replaced wholesale
by #105 after live review — the single-scrolling-page layout read as
document-like rather than app-like. **Minimal Monochrome Editorial** ("a
critical edition's index") is the current system, applied to every view in
one pass. New feature UI should follow it rather than reintroducing ad hoc
styling:

- **Direction**: pure neutral grayscale plus one accent (the "editor's blue
  pencil"), reserved strictly for annotation/reference — links, the
  sidebar's active-nav tick, the current-streak numeral — never used
  decoratively. `--radius: 0` everywhere (buttons, modal, inputs, sidebar
  rows) is the loudest structural decision: sharp edges read as page/table,
  not app card. Light/dark are both first-class (via
  `prefers-color-scheme`).
- **Shell, not a scrolling page**: `App.svelte` is a fixed-width sidebar +
  single active view, switched via a plain `activeView` `$state` string —
  explicitly not a router. Six views: Pieces, Focus, Sessions, Statistics,
  Resources, Lists. The sidebar is collapsible to a 64px icon-only rail,
  state persisted to `localStorage`.
- **Interaction pattern**: create/edit forms open in `Modal.svelte`
  (unchanged mechanics — native `<dialog>`, Escape/backdrop-click to close,
  explicit close button with the crossing-hairline close icon). Every form
  component takes an `onCancel` prop.
- **Tokens**: colors, type, and spacing are CSS custom properties in
  `frontend/src/app.css` — components consume tokens, never hardcode hex
  values or ad hoc sizes.
- **Type — three roles**: `--font-serif` (Georgia/Times/Liberation Serif)
  for display headlines and hero numerals; the existing `--font-sans` for
  all UI chrome, forms, and labels; the existing `--font-mono` for
  genuinely tabular data (dates, durations), with the old neon-LCD chip
  styling retired — it's now plain tabular text via `.readout`.
- **Iconography**: a hand-rolled ~14-glyph inline SVG sprite at
  `frontend/public/icons.svg` (20x20 grid, 1.5px stroke, no fill, square
  corners — "engraver's/proofing marks"), consumed via `Icon.svelte`
  (`<svg><use href="/icons.svg#{name}"/></svg>`). Color comes from the
  consumer's CSS `color` through `currentColor`.
- **Recurring patterns**: `.panel`, `SectionHeader.svelte` (now a
  page-level header per view: serif headline, italic dek line, full-width
  hairline rule, then a filter/action row), `.row-list` with `.accented`
  for a left accent bar, `.meta-line` (values joined by middle dots via
  `::before` on `span + span`), `.text-toggle` / `.toggle-row` (underlined
  text filters replacing boxed `<select>`s), `.icon-btn` (hover-revealed
  row actions — pencil-nib edit, strike-mark delete), `.index-table` (real
  tables for tabular breakdowns, right-aligned numerics), `.numeral` /
  `.caption` (serif hero number + small-caps label pairing), `Modal.svelte`,
  and shared `button`/`input`/`select`/`textarea` base styles plus
  `.secondary`/`.danger` variants. The old `.chip`/`.chip-accent`/
  `.chip-quiet` pill badges are retired in favor of small-caps text labels.
- **Adding a new view**: reuse these tokens and patterns. Route any new
  create/edit interaction through `Modal.svelte`. If a new recurring
  element doesn't fit an existing pattern, add it to `app.css` as a
  token-driven utility class, not a one-off inline style.

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
