# Git Flow

This repo uses Git Flow. See [ADR 0004](adr/0004-git-flow-branching.md) for why (a deliberate workflow-learning goal, not a requirement of the app's own complexity).

## Branches

- `main` — production-ready code only. Never commit here directly.
- `develop` — integration branch. Never commit here directly (bootstrap exception: see below).
- `feature/issue-<n>-<slug>` — one feature/subtask, branched from `develop`, merged back via PR.
- `release/x.y.z` — cut from `develop` when a milestone is ready; merges into `main` (tagged) and back into `develop`.
- `hotfix/x.y.z` — cut from `main` for urgent fixes; merges into both `main` and `develop`.

## Rules

- Every feature branch corresponds to one GitHub issue (or one clearly scoped subtask).
- PRs target `develop`, not `main` (except release/hotfix PRs, which target `main`).
- CI must pass before merge.
- Merges into `develop`/`main` use `--no-ff` (a merge commit), preserving branch history.
- Reference the issue in the PR body (e.g. `Closes #12`) for traceability — but note GitHub only **auto-closes** the issue on merges into the repo's *default branch* (`main`). Since feature PRs target `develop`, merging one does **not** auto-close the linked issue; either close it manually (`gh issue close <n>`) once the work is confirmed done, or let it close naturally when the containing release reaches `main`.

**Bootstrap exception:** the very first commits (repo scaffold) were made on `feature/bootstrap-skeleton` off `develop` and merged via a real PR — there was no other way to get initial content onto `develop` without violating "never commit directly to develop." This was a one-time exception, not a precedent.

## Conventional Commits

```
feat: add piece model
fix: correct practice duration calculation
test: add practice session integration tests
docs: document Git Flow workflow
refactor: simplify piece repository
ci: add pull request test workflow
chore: update dependencies
```

Keep commits focused — no bundling unrelated changes.

## Feature flow

```bash
git checkout develop
git pull
git checkout -b feature/issue-12-practice-sessions
# ... implement, commit ...
git push -u origin feature/issue-12-practice-sessions
gh pr create --base develop
# after CI passes and review:
gh pr merge --merge
```

## Release flow

```bash
git checkout develop
git checkout -b release/0.2.0
# bump versions, final fixes only — no new features
git push -u origin release/0.2.0
gh pr create --base main --title "release: 0.2.0"
# after CI passes:
gh pr merge --merge
git tag v0.2.0 main
git push origin v0.2.0
# back-merge into develop
git checkout develop
git merge --no-ff main
git push
```

## Hotfix flow

Same as release, but branched from `main` instead of `develop`, and merged into **both** `main` and `develop`.

## Local safety

`.claude/hooks/guard-git.sh` blocks `git commit` while on `main`/`develop` and warns on force-push, via a `PreToolUse` hook on the Bash tool (`.claude/settings.json`). Verified live: a real `git commit` attempt on `develop` was denied with `permissionDecision: "deny"` and the expected reason text.

This only protects Claude Code sessions working in this checkout — it does not stop a plain `git commit` run outside Claude Code, another tool, or a push from anywhere else. Real enforcement is a GitHub repository ruleset (`protect-develop-main`, id 20684274) on `main` and `develop`: requires a PR (no direct pushes, verified — a direct `git push origin HEAD:develop` was rejected with `GH013: Repository rule violations`), requires the `backend` and `frontend` CI checks to pass, blocks force-push and branch deletion, and applies even to the repo owner (`current_user_can_bypass: never`).

**Note:** classic branch protection and rulesets both require GitHub Pro for *private* repos on the free plan — this repo is public specifically to enable this. If privacy matters more than server-side enforcement, revert to private and rely on the local hook alone.
