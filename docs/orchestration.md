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

## Required integration: project board automation

`.github/workflows/project-board.yml` already moves issue cards on the "Music Repertoire" project board based on generic git/PR lifecycle events (branch push matching `feature/issue-<n>-*` → In Progress, PR opened → Review, CI success → CI, PR merged → Done). This was built deliberately generic — it reacts to git/GitHub state, not to *who* opened the PR, so it keeps working unchanged when an orchestrator starts dispatching agents.

**When the orchestrator is built, it must not duplicate or race this automation.** Specifically:
- Do not have the orchestrator also write the project board's Status field directly for the same transitions this workflow already covers — two writers on the same field will fight and produce flapping/incorrect state.
- If the orchestrator needs additional states this workflow doesn't cover (e.g. "agent assigned" before a branch is even pushed), extend `.github/scripts/move-project-card.js` / `project-board.yml` rather than writing a parallel path.
- If the orchestrator changes the branch naming convention (`feature/issue-<n>-<slug>`) or the PR-closing-keyword convention (`Closes #<n>`), update the regexes in `.github/scripts/move-project-card.js` — the automation depends on both.
