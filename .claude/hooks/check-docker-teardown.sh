#!/usr/bin/env bash
# Stop hook: when a feature session's turn ends, if it's working in a
# .worktrees/issue-<n> checkout whose branch already has a merged PR, and its
# docker compose stack is still running, tear it down automatically.
# Containers/images being left running past merge (relying on someone
# remembering to run scripts/cleanup-worktrees.sh later) was a recurring gap
# — see docs/development.md. This catches it the moment the session that
# owns the stack finishes, instead of waiting for manual housekeeping.
#
# Never blocks stopping: this is a side effect, not a permission decision,
# and Stop hooks have no documented loop-guard for exit-2 (block-and-continue),
# so this always exits 0 regardless of outcome.
set -euo pipefail

input=$(cat)
cwd=$(python -c "import json,sys; print(json.load(sys.stdin).get('cwd', ''))" <<< "$input" 2>/dev/null || true)

case "$cwd" in
  */.worktrees/issue-*) ;;
  *) exit 0 ;;
esac

[[ -f "$cwd/docker-compose.yml" ]] || exit 0
command -v docker >/dev/null 2>&1 || exit 0
docker info >/dev/null 2>&1 || exit 0

running=$(cd "$cwd" && docker compose ps -q 2>/dev/null || true)
[[ -n "$running" ]] || exit 0

branch=$(git -C "$cwd" branch --show-current 2>/dev/null || true)
[[ -n "$branch" ]] || exit 0

repo=$(gh repo view --json nameWithOwner -q .nameWithOwner 2>/dev/null || true)
[[ -n "$repo" ]] || exit 0

merged_pr=$(gh pr list -R "$repo" --state merged --head "$branch" --json number -q '.[0].number' 2>/dev/null || true)
[[ -n "$merged_pr" ]] || exit 0

(cd "$cwd" && docker compose down --rmi local --volumes --remove-orphans) >/dev/null 2>&1 || exit 0

python -c "
import json, sys
print(json.dumps({'systemMessage': sys.argv[1]}))
" "check-docker-teardown: '$branch' has merged PR #$merged_pr but its docker stack was still running — tore it down automatically (containers, local images, volumes)."

exit 0
