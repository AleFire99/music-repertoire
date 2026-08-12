# Orchestration (Future)

**Status: setup is scripted, dispatch/merge/integration is still manual.** No orchestrator exists. The manual workflow below has now been run enough times — including two features built by a genuinely independent, parallel Claude Code session with no collisions — to validate the pattern itself. `scripts/new-feature.sh` automates the repetitive, safe part of it (issue + worktree + ports + prompt). It deliberately stops there: launching the session, watching CI, merging, and cleanup stay human-supervised, because that manual step has already caught real bugs (a stale local `main` ref silently no-opping a back-merge; a Windows-specific `git worktree remove` failure) that fully automating this would have baked in without anyone noticing. Don't build the next layer (auto-launch, auto-merge, auto-cleanup) without an explicit request — see CLAUDE.md's agent-roles section.

## Why wait

> The orchestrator should eventually automate a workflow that has already been validated manually.

Build the orchestrator only once issue → feature branch → agent → tests → PR → review → CI → merge has been run manually enough times to know what actually needs automating.

## When it's actually worth running features in parallel

Parallel worktrees have real overhead — each running stack is its own postgres+backend+frontend containers (real RAM/CPU), and every parallel session is one more thing to check in on. Worth it when:

- **The features touch disjoint files/areas.** Piece status+tags (#18, backend model+schema+API+App.svelte) and GHCR publishing (#20, a new standalone workflow file) ran in parallel with zero conflict because they shared almost nothing. Practice session recording (#31, new model/router/frontend view) was deliberately started only *after* confirming the in-flight Piece CRUD UI work (#28) wasn't also mid-rewrite of the same `App.svelte` — running both at once would have guaranteed a merge conflict on that file.
- **Each slice is small enough to review/merge independently** — a whole multi-week epic handed to one worktree isn't a parallel-friendly unit; break it into the same kind of focused slices used for solo work first (see `docs/backlog.md`'s pattern of one epic → several scoped issues).
- **You're not choosing between exploring an approach and committing to one.** If a feature's design is genuinely uncertain, let one session settle it first rather than parallelizing something that might get thrown away.

Don't parallelize when: two candidate slices would both need to edit the same core file heavily (shared schema, shared main layout component, shared router registration) — sequence them instead, or split the shared-file change out as its own small prerequisite PR first. Rule of thumb from experience so far: 2-3 concurrent worktrees is comfortable; more than that turns into more context-switching than the parallelism saves.

## Worktree rules (for when multi-agent work starts)

- Each implementation agent works in its **own** Git worktree and branch — never a shared mutable worktree.
- Branch naming stays the same as solo work: `feature/issue-<n>-<slug>`.
- Prefer splitting work along clear boundaries: backend/domain, frontend, tests, documentation, infrastructure.
- Do not parallelize tasks that heavily modify the same files unless there's a clear reason (e.g., a backend agent and a test agent both touching the same new module is fine if scoped to different files within it).

## Agent hand-off report

Every agent should report, at minimum:

- branch
- worktree path
- issue reference
- files/components modified
- tests executed (and result)
- remaining concerns / follow-ups

## Integration discipline

The orchestrator (once it exists) must integrate work deliberately — parallel branches are not automatically compatible. Expect to run a real merge/rebase and re-run tests after combining agents' work, not just fast-forward everything.

## Today's manual equivalent

```
issue → feature branch → agent (this session) → tests → PR → review (self, or a fresh session) → CI → merge
```

## Project board automation

The board (Backlog / In Progress / Done) uses GitHub Projects' **built-in workflow automations** (configured in the Project's UI, not custom code): issue/PR closed and PR merged both auto-set Done; new issues/PRs auto-add via a filter rule. Backlog → In Progress is a manual drag — there's no built-in trigger for "work started" and it wasn't worth custom code for a two-state manual transition.

An earlier custom Actions-based version (`.github/workflows/project-board.yml` + a PAT-scoped secret) covered more granular transitions (branch push → In Progress, PR opened → Review, CI passed → CI) but was replaced — more maintenance surface than a solo project's board needed. If the orchestrator eventually needs those finer-grained states back (e.g. "agent assigned" before a branch exists), it should set the Status field directly via the GraphQL API rather than reintroducing a parallel automation path — there's no existing custom writer left to race against.
