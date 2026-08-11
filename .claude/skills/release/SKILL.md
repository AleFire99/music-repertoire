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
git checkout develop && git merge --no-ff main && git push
git branch -d release/x.y.z
```

Update `docs/backlog.md` to mark what shipped in this milestone before opening the release PR.
