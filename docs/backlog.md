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

## Post-0.4.0 slices (not yet cut into a release)

- [x] Practice statistics by week and month — issue #78
- [x] Section-level practice breakdowns — issue #81
- [x] Fix: cascade-delete practice sessions when their piece is deleted — issue #83
- [x] Piece-level learning goals (goal text + target date) — issue #88
- [x] Practice time goals (weekly target + progress) — issue #91
- [x] Repertoire rotation planner (in-focus pieces view) — issue #95

---

## Future epics (not implemented, do not start without a new milestone)

### Repertoire
Fully delivered — see issue #5 for the shipped-item checklist. No remaining scope; new Repertoire-epic ideas need their own scoping discussion before being added here.

### Practice
Fully delivered — see issue #6 for the shipped-item checklist. No remaining scope; new Practice-epic ideas need their own scoping discussion before being added here.

### Music representation
MIDI import, MusicXML import, chord representation, measure representation, sections, annotations. **Audio → MIDI → chord extraction is explicitly out of scope indefinitely** — not a v-next item, a permanent non-goal unless a concrete future requirement changes that.

### Music theory engine
Deterministic analysis: ii-V-I / ii-V-i, cadences, secondary dominants, substitutions, modulations, repeated harmonic/melodic patterns, transposed patterns, cross-piece relationships. Must stay deterministic — see `docs/architecture.md`'s "LLM is never the source of truth for musical facts" rule.

### Learning assistant
LLM explanations of theoretical findings (never the source of the findings themselves), piece similarity, related-piece suggestions, focused practice exercise generation, recurring-concept identification across the repertoire.

### Workflow / infra
Real Gitea Actions experiment (currently GitHub-only), production frontend Dockerfile (nginx static build) once there's a real deployment target, multi-agent orchestrator (see `docs/orchestration.md`), CHANGELOG automation.
