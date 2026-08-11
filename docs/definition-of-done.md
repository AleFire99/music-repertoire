# Definition of Done

Use judgment — not every item applies to every change. A typo fix in a doc doesn't need a migration check. A schema change needs all of it.

## Per-PR checklist

- [ ] Implementation matches the issue's acceptance criteria
- [ ] Tests exist for new/changed behavior and pass (`pytest` for backend)
- [ ] `ruff check .` and `mypy src` pass (backend)
- [ ] `npm run check` passes (frontend — svelte-check, doubles as lint+typecheck)
- [ ] Documentation updated where behavior or setup changed
- [ ] Migration included if the schema changed (`alembic revision --autogenerate`, reviewed by hand)
- [ ] Docker/build behavior preserved (`docker compose build` still succeeds)
- [ ] Commits follow Conventional Commits
- [ ] No direct commits to `main`/`develop` — went through a feature branch + PR
- [ ] PR description filled out (see `.github/pull_request_template.md`)
- [ ] CI green

## Per-milestone checklist

- [ ] All backlog issues for the milestone closed or explicitly deferred
- [ ] `docs/backlog.md` updated to reflect what shipped vs. what moved
- [ ] Release cut per [git-flow.md](git-flow.md) (`release/x.y.z` → `main`, tagged, back-merged into `develop`)

## Known limitation

The local `.claude/hooks/guard-git.sh` safety hook is verified working for Claude Code sessions (see `CLAUDE.md`), but only covers this checkout — it doesn't stop a commit made outside Claude Code or from another machine. Real enforcement is a GitHub ruleset on `main`/`develop` (see `docs/git-flow.md`) — verified live by a rejected direct push. This required making the repo public (Pro is required for private-repo branch protection on the free plan).
