#!/usr/bin/env bash
# Removes worktrees (created by scripts/new-feature.sh) that are safe to discard:
# their branch has a MERGED pull request on GitHub, and the worktree has no
# uncommitted changes. Anything not yet merged, or with local changes, is left
# alone and explained rather than guessed at — a branch merely matching
# `git branch --merged develop` isn't a safe signal on its own (a freshly
# created, not-yet-started worktree is trivially "merged" too, since it has no
# commits yet).
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
cd "$REPO_ROOT"

git worktree list --porcelain | awk '/^worktree /{path=$2} /^branch /{print path, $2}' |
while read -r WT_PATH WT_REF; do
  BRANCH="${WT_REF#refs/heads/}"
  [[ "$WT_PATH" == "$REPO_ROOT" ]] && continue

  if [[ -n "$(git -C "$WT_PATH" status --porcelain)" ]]; then
    echo "SKIP  $BRANCH — uncommitted changes in $WT_PATH"
    continue
  fi

  MERGED_PR=$(gh pr list -R "$REPO" --state merged --head "$BRANCH" --json number -q '.[0].number' 2>/dev/null || true)
  if [[ -z "$MERGED_PR" ]]; then
    echo "SKIP  $BRANCH — no merged PR found yet"
    continue
  fi

  echo "REMOVE $BRANCH — merged via PR #$MERGED_PR"
  if ! git worktree remove "$WT_PATH" 2>/dev/null; then
    echo "  git worktree remove failed (Windows symlink quirk?) — falling back to manual delete"
    rm -rf "$WT_PATH" 2>/dev/null || powershell.exe -NoProfile -Command "Remove-Item -Recurse -Force '$WT_PATH'"
    git worktree prune
  fi
  git branch -d "$BRANCH" 2>/dev/null || echo "  (local branch $BRANCH already gone or has unmerged commits — left as-is)"
done
