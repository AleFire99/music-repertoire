---
name: release
description: Use when cutting or preparing a release (e.g. "cut a release", "prepare release 0.2.0") — the release branch → tag → back-merge sequence.
---

Full flow: `docs/git-flow.md`.

```bash
git checkout develop && git pull
git checkout -b release/x.y.z
# bump version in backend/pyproject.toml and frontend/package.json
# release-blocking fixes only — no new features on a release branch
git push -u origin release/x.y.z
gh pr create --base main --title "release: x.y.z"
# after CI is green:
gh pr merge --merge
git tag vx.y.z main
git push origin vx.y.z
# a pushed tag alone is NOT a GitHub Release — create one explicitly, or it
# silently doesn't show up under the repo's Releases page (found live: v0.3.0
# had only a bare tag until this was added). Match the "## Highlights" /
# "## Images" format of prior releases (gh release view vX.Y.Z to check).
gh release create vx.y.z --title "vx.y.z" --notes "..."
# back-merge via PR — the ruleset blocks direct pushes to develop, even fast-forward merges
git checkout develop && git checkout -b chore/back-merge-x.y.z
git merge --no-ff main && git push -u origin chore/back-merge-x.y.z
gh pr create --base develop --title "chore: back-merge x.y.z into develop"
gh pr merge --merge
git branch -d release/x.y.z
```

Update `docs/backlog.md` to mark what shipped in this milestone before opening the release PR.
