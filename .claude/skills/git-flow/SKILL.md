---
name: git-flow
description: Use when starting a feature, cutting a release, or applying a hotfix in this repo — exact git command sequences for the Git Flow branching model.
---

Full rules: `docs/git-flow.md`. This skill is the command cheat sheet only.

## Start a feature

```bash
git checkout develop && git pull
git checkout -b feature/issue-<n>-<slug>
```

## Finish a feature

```bash
git push -u origin feature/issue-<n>-<slug>
gh pr create --base develop --title "..." --body "Closes #<n>\n\n..."
# wait for CI, then:
gh pr merge --merge
git branch -d feature/issue-<n>-<slug>
```

## Cut a release

```bash
git checkout develop && git pull
git checkout -b release/x.y.z
# bump version numbers, fix release-blocking bugs only — no new features
git push -u origin release/x.y.z
gh pr create --base main --title "release: x.y.z"
# after CI + merge:
git tag vx.y.z main && git push origin vx.y.z
git checkout develop && git merge --no-ff main && git push
```

## Hotfix

Same as release but branch from `main` (`hotfix/x.y.z`), merge into both `main` and `develop`.

## Commit message format

Conventional Commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `ci:`, `chore:`. One logical change per commit.
