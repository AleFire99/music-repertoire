#!/usr/bin/env bash
# Removes worktrees (created by scripts/new-feature.sh) that are safe to discard:
# their branch has a MERGED pull request on GitHub, and the worktree has no
# uncommitted changes. Anything not yet merged, or with local changes, is left
# alone and explained rather than guessed at — a branch merely matching
# `git branch --merged develop` isn't a safe signal on its own (a freshly
# created, not-yet-started worktree is trivially "merged" too, since it has no
# commits yet).
#
# Before deleting a worktree, tears down its docker compose stack (containers,
# locally-built backend/frontend images, the postgres volume) — `--rmi local`
# only removes images compose built itself (backend/frontend), never a shared
# pulled base image like postgres:16-alpine. Must run from inside the worktree
# while the compose file still exists, so this happens before removal, not after.
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

  if command -v docker >/dev/null 2>&1 && docker info >/dev/null 2>&1; then
    if [[ -f "$WT_PATH/docker-compose.yml" ]]; then
      echo "  tearing down docker compose stack (containers, local images, volumes)"
      (cd "$WT_PATH" && docker compose down --rmi local --volumes --remove-orphans) 2>&1 | sed 's/^/  /'
    fi
  else
    echo "  docker not running — skipping container/image cleanup for $WT_PATH (run 'docker compose down --rmi local -v' there manually once it's up)"
  fi

  cd "$REPO_ROOT"  # never attempt to delete a directory we're currently inside — Windows locks it
  if ! git worktree remove "$WT_PATH" 2>/dev/null; then
    echo "  git worktree remove failed (Windows symlink quirk?) — falling back to manual delete"
    REMOVED=0
    for attempt in 1 2 3; do
      if rm -rf "$WT_PATH" 2>/dev/null || powershell.exe -NoProfile -Command "Remove-Item -Recurse -Force '$WT_PATH'" 2>/dev/null; then
        REMOVED=1
        break
      fi
      sleep 2
    done
    if [[ "$REMOVED" == "0" ]]; then
      echo "  could not delete $WT_PATH after 3 attempts — something still has a handle on it"
      echo "  (an editor's file watcher indexing .worktrees/, or Docker Desktop's file-sharing layer, are the usual suspects on Windows)"
      echo "  git already unregistered it as a worktree; delete the folder by hand once it's released, then 'git worktree prune'"
      continue
    fi
    git worktree prune
  fi
  git branch -d "$BRANCH" 2>/dev/null || echo "  (local branch $BRANCH already gone or has unmerged commits — left as-is)"
done
