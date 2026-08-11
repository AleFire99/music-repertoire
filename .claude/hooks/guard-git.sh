#!/usr/bin/env bash
# PreToolUse hook for the Bash tool: blocks `git commit` while on main/develop,
# and warns on force-push. Convenience nudge only — see docs/git-flow.md.
set -euo pipefail

input=$(cat)
command=$(echo "$input" | grep -o '"command"[[:space:]]*:[[:space:]]*"[^"]*"' | sed -E 's/.*"command"[[:space:]]*:[[:space:]]*"([^"]*)"/\1/')

if [[ "$command" != *"git commit"* && "$command" != *"git push"* ]]; then
  exit 0
fi

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

if [[ "$command" == *"git commit"* && ( "$branch" == "main" || "$branch" == "develop" ) ]]; then
  echo "{\"hookSpecificOutput\": {\"permissionDecision\": \"deny\", \"permissionDecisionReason\": \"Refusing to commit directly on '$branch'. Branch from develop first (see docs/git-flow.md).\"}}" >&2
  exit 2
fi

if [[ "$command" == *"git push"* && ( "$command" == *"--force"* || "$command" == *" -f "* || "$command" == *"--force-with-lease"* ) ]]; then
  echo "{\"hookSpecificOutput\": {\"permissionDecision\": \"ask\", \"permissionDecisionReason\": \"Force-push detected — confirm this is intentional.\"}}" >&2
  exit 2
fi

exit 0
