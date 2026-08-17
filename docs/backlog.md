# Backlog

Source of truth until these are transcribed into GitHub Issues (`gh issue create`, one per item below). Milestone: **v0.1 — Repertoire Foundation**.

## Infrastructure

- [x] Init git repo, Git Flow branches (main/develop)
- [x] `.gitignore` / `.editorconfig` / LICENSE (MIT)
- [x] docs/ skeleton + CLAUDE.md
- [x] `.claude/skills/` (6 skills)
- [x] `.claude/settings.json` local safety hook
- [x] Backend scaffold via uv (pyproject, ruff/mypy config)
- [x] Frontend scaffold via Vite+Svelte+TS
- [x] `docker-compose.yml` (postgres + backend + frontend, all containerized)
- [x] Backend + frontend Dockerfiles (dev-mode)
- [x] GitHub Actions CI workflow
- [x] GitHub issue templates + PR template + CODEOWNERS
- [x] Install + configure `gh` CLI
- [x] GitHub milestone, labels, issues, Project (v2) board for kanban tracking
- [x] Project board automation (GitHub's built-in workflows: auto-add, Done on close/merge — replaced an earlier custom Actions version)

## Domain

- [x] `Piece` SQLAlchemy model
- [x] Alembic scaffold + `0001_create_pieces_table` migration
- [x] Pydantic schemas (`PieceCreate`/`PieceUpdate`/`PieceRead`)

## Backend

- [x] FastAPI entrypoint + `/api/health` (DB connectivity check)
- [x] DB engine/session + `get_db` dependency
- [x] Piece CRUD routes (create/list/get/update/delete)
- [x] pytest scaffold: `conftest.py` (test DB fixture + TestClient override)
- [x] `test_health.py`
- [x] `test_pieces.py` (CRUD integration tests)

## Frontend

- [x] Vite hello page fetching `/api/health`
- [x] Read-only Piece list view (`GET /api/pieces`)
- [x] API base URL config + dev-server proxy

## Workflow

- [x] Write architecture/development/git-flow/testing/agent-model/orchestration/definition-of-done docs
- [x] ADRs 0001–0004
- [x] First release: `develop` → `release/0.1.0` → `main`, tag `v0.1.0`

## v0.2.0 — Piece status/tags + image publishing

- [x] Piece `status` field (backlog/learning/memorized/maintaining/performance-ready/archived, default backlog) — issue #18
- [x] Piece `tags` field (list of strings, default empty) — issue #18
- [x] `GET /api/pieces` filtering by `status` and by `tag` — issue #18
- [x] Frontend: status/tags shown per piece, status filter control — issue #18
- [x] CI workflow publishing `backend`/`frontend` images to GHCR on release/tag — issue #20 (ad hoc, not part of the repertoire-extensions epic)
- [x] Release: `develop` → `release/0.2.0` → `main`, tag `v0.2.0`

## v0.3.0 — Practice insights, sheet resources, and Piece descriptive fields

- [x] Full Piece CRUD UI (create/edit/delete forms, not just read-only list) — issue #28
- [x] Practice session recording (piece, date/time, duration, notes, rating, section) — issue #31
- [x] Practice statistics (total minutes, per-piece totals, session counts, last-practiced) — issue #41
- [x] Sheet-music resources for a Piece (external URL / physical reference / local document, no file storage) — issue #43
- [x] Piece favorites (toggle + filter) — issue #46
- [x] Piece key/tempo/difficulty/instrument fields — issue #50
- [x] Recently-practiced and neglected pieces in practice stats — issue #56
- [x] Release: `develop` → `release/0.3.0` → `main`, tag `v0.3.0`

## v0.4.0 — Practice timer/streaks, repertoire lists

- [x] Practice session timer (stopwatch, auto-fills duration_minutes) — issue #63
- [x] Practice streaks (current/longest consecutive-day streaks) — issue #67
- [x] Repertoire lists (named lists of pieces) — issue #70
- [x] Release: `develop` → `release/0.4.0` → `main`, tag `v0.4.0`

## v0.5.0 — Practice epic completion, Repertoire epic completion

- [x] Practice statistics by week and month — issue #78
- [x] Section-level practice breakdowns — issue #81
- [x] Fix: cascade-delete practice sessions when their piece is deleted — issue #83
- [x] Piece-level learning goals (goal text + target date) — issue #88
- [x] Practice time goals (weekly target + progress) — issue #91
- [x] Repertoire rotation planner (in-focus pieces view) — issue #95
- [x] Release: `develop` → `release/0.5.0` → `main`, tag `v0.5.0`

## Post-0.5.0 slices (not yet cut into a release)

- [x] Practice stats: 14-week consistency heatmap — issue #107 (bundled with the UI redesign below; small deterministic addition, same category as already-shipped stats features)
- [x] Practice stats: deterministic "suggested next" practice plan (due goals, neglected pieces, low-rated sessions — no LLM) — issue #107
- [x] UI design pass v3 ("Modernist": Archivo, zero-radius, 2px dividers, blue accent, manual light/dark toggle, imported from claude.ai/design) — issue #107, replacing #105's Minimal Monochrome Editorial
- [x] UI design pass v4 ("Iris": Material 3-inspired, violet accent, Figtree, per-element radius scale, state-layer hover/pressed, two-layer elevation shadows), plus a Pieces card-grid view and `PieceRead.sheet_resource_kinds` — issue #114, replacing #107's Modernist

---

## Future epics (not implemented, do not start without a new milestone)

**Confirmed next direction (scoped in a recap/planning conversation after v0.5.0 + the Iris redesign)**: File storage → Jazz reference wiki → Music theory engine, in that order. Each is its own epic, shipped one slice at a time like everything else — the order below reflects that sequencing, not just a flat list.

### Repertoire
Fully delivered — see issue #5 for the shipped-item checklist. No remaining scope; new Repertoire-epic ideas need their own scoping discussion before being added here.

### Practice
Fully delivered — see issue #6 for the shipped-item checklist. No remaining scope; new Practice-epic ideas need their own scoping discussion before being added here.

### Sheet-music file storage (epic 1 of the confirmed next direction — in progress)
Real upload/storage for sheet-music PDFs, reversing the "no file storage" decision sheet resources shipped with (#43) — the user wants to move their existing downloaded PDFs (mostly from musescore.com) into the app itself, alongside continued references for physical books and not-yet-downloaded pieces. Scope: a new `SheetResourceKind` for uploaded files (distinct from `local-doc`, which means "a path on your machine," not "stored by the app"), a Docker named volume for storage (local-first, no cloud storage), upload/download/delete endpoints with PDF-only + size-cap validation, and frontend upload UI. No in-app PDF viewer for v1 — download/open is enough to start.

Shipped so far:
- [x] `uploaded` `SheetResourceKind` + file metadata columns, named-volume storage, upload/download/delete endpoints (PDF-only, 20MB cap), frontend upload/download UI — issue #123

### Jazz reference wiki (epic 2 of the confirmed next direction)
A navigable personal reference wiki (pages the user writes/browses), initially standalone with no AI dependency — build it useful on its own first. Explicit eventual intent (not scoped yet): an AI agent reading from it to answer questions, once the Music theory engine below exists to ground those answers in something deterministic. Needs its own scoping pass when its turn comes (content model, navigation, whether pages are freeform or piece-linked).

### Music representation
MIDI import, MusicXML import, chord representation, measure representation, sections, annotations. **Audio → MIDI → chord extraction is explicitly out of scope indefinitely** — not a v-next item, a permanent non-goal unless a concrete future requirement changes that.

### Music theory engine (epic 3 of the confirmed next direction)
Deterministic analysis: ii-V-I / ii-V-i, cadences, secondary dominants, substitutions, modulations, repeated harmonic/melodic patterns, transposed patterns, cross-piece relationships, especially across lead sheets. Must stay deterministic — see `docs/architecture.md`'s "LLM is never the source of truth for musical facts" rule. **Confirmed input method: manual entry** of chords/key/form by the user (the PDF stays a reference read while typing it in) — OCR/parsing the user's actual PDF/scan files was explicitly considered and rejected as a starting point (research-grade, unreliable even in commercial tools, not advisable for a personal project). Looking up existing chord-chart metadata for known standards online is a possible easier future input path the user wants to research separately later — not scoped as work yet, just noted so it isn't forgotten.

### Learning assistant
LLM explanations of theoretical findings (never the source of the findings themselves), piece similarity, related-piece suggestions, focused practice exercise generation, recurring-concept identification across the repertoire.

### Workflow / infra
Real Gitea Actions experiment (currently GitHub-only), production frontend Dockerfile (nginx static build) once there's a real deployment target, multi-agent orchestrator (see `docs/orchestration.md`), CHANGELOG automation.
