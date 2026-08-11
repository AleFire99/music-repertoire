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

The local `.claude/hooks/guard-git.sh` safety hook is a convenience nudge, not a guaranteed technical boundary (see `CLAUDE.md`). Real enforcement of "no direct commits to protected branches" belongs to GitHub branch protection rules — set these up on the remote (Settings → Branches) once the manual workflow is validated.
