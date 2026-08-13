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

## UI design system (established by the #102 design pass)

The interim "stay minimal" convention is retired — issue #102 delivered a
real design system, applied to every existing view. New feature UI should
follow it rather than reintroducing ad hoc styling:

- **Direction**: a "manuscript" theme grounded in printed sheet music —
  warm paper background, ink text, a sealing-wax red accent for actions,
  aged brass for annotations. Light/dark are both first-class (via
  `prefers-color-scheme`), not an afterthought.
- **Tokens**: all colors, type, and spacing are CSS custom properties
  defined once in `frontend/src/app.css` (`--paper`, `--ink`, `--accent`,
  `--brass`, `--space-*`, `--text-*`, etc.) — components consume tokens,
  they don't hardcode hex values or ad hoc sizes.
- **Type**: a serif display face (`--font-display`) for headings, a plain
  sans body face (`--font-body`) for content and forms, tabular numerals
  (`--font-mono`) for tempo/timer/durations.
- **Recurring patterns**: `.sheet` (card wrapping each section),
  `SectionHeader.svelte` (the barline + 5-line staff-rule divider used on
  every section heading — the system's one signature device),
  `.manuscript-list` (list items with a left accent bar), `.chip` (the
  small-caps badge used for status/difficulty/tags/kind/counts, echoing
  engraved performance directions), and shared `button`/`input`/`select`/
  `textarea` base styles plus `.secondary`/`.danger` button variants.
- **Adding a new view**: reuse these tokens and patterns rather than
  inventing new ones. If a new recurring element doesn't fit an existing
  pattern, add it to `app.css` as a token-driven utility class, not a
  one-off inline style.

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
