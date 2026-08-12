# Orchestration (Future)

**Status: aspirational, manual-only today.** No orchestrator exists. This document describes the conventions to follow *when* multi-agent parallelism is introduced — do not build automation around this until the manual workflow below has been validated by hand across a few real features.

## Why wait

> The orchestrator should eventually automate a workflow that has already been validated manually.

Build the orchestrator only once issue → feature branch → agent → tests → PR → review → CI → merge has been run manually enough times to know what actually needs automating.

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
