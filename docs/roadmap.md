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

## Interim UI guideline (while the epics above are in progress)

No dedicated design/styling investment yet. Each feature slice's frontend
work should stay functional-only:

- Reuse the minimal styling already established in `App.svelte` (system-ui
  font stack, single `max-width` container, `.error` class) — don't
  introduce new visual patterns, layout systems, or component libraries per
  feature.
- Don't hand-polish one view more than another. Consistent plainness beats
  partial, mismatched polish that would need to be undone later.
- See the `frontend-development` skill's "Do NOT add without explicit
  sign-off" list — CSS frameworks are excluded there for the same reason.

## Design / UI polish pass (next epic after Repertoire + Practice substantially land)

Once the two epics above are substantially built out — or sooner if the bare
styling becomes actively confusing to use — start a dedicated pass: layout
system, typography, spacing, color, component consistency across every
shipped view (pieces, practice sessions, stats, sheet resources, favorites,
etc.). Treat it as its own epic/issue(s), not a side effect of a feature PR.

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
