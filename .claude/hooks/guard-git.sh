#!/usr/bin/env bash
# PreToolUse hook for the Bash tool: blocks `git commit` while on main/develop,
# and warns on force-push. Convenience nudge only — see docs/git-flow.md.
# Settings.json hook registration changes require a Claude Code session restart to take effect.
set -euo pipefail

input=$(cat)
command=$(python -c "import json,sys; print(json.load(sys.stdin).get('tool_input', {}).get('command', ''))" <<< "$input")

branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "")

emit_decision() {
  python -c "
import json, sys
decision, reason = sys.argv[1], sys.argv[2]
print(json.dumps({'hookSpecificOutput': {'hookEventName': 'PreToolUse', 'permissionDecision': decision, 'permissionDecisionReason': reason}}))
" "$1" "$2"
  exit 0
}

deny() { emit_decision "deny" "$1"; }
ask() { emit_decision "ask" "$1"; }

if [[ "$command" == *"git commit"* && ( "$branch" == "main" || "$branch" == "develop" ) ]]; then
  deny "Refusing to commit directly on '$branch'. Branch from develop first (see docs/git-flow.md)."
fi

if [[ "$command" == *"git push"* && ( "$command" == *"--force"* || "$command" == *" -f "* || "$command" == *"--force-with-lease"* ) ]]; then
  ask "Force-push detected — confirm this is intentional."
fi

exit 0
