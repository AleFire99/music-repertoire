#!/usr/bin/env bash
# Automates the repetitive, safe setup for a new feature: creates a GitHub issue,
# a git worktree with the correctly-numbered branch (off develop), a per-worktree
# .env with non-colliding docker-compose ports (derived from the issue number so
# no port-scanning is needed), and prints a ready-to-paste prompt for a new
# Claude Code session.
#
# Deliberately does NOT: launch a Claude Code session, watch its PR, merge it, or
# clean up afterwards — those stay manual/human-supervised. See docs/orchestration.md.
#
# Usage: scripts/new-feature.sh "<issue title>" "<issue body>" [label]
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 \"<issue title>\" \"<issue body>\" [label]" >&2
  exit 1
fi

TITLE="$1"
BODY="$2"
LABEL="${3:-feature}"

REPO_ROOT="$(git rev-parse --show-toplevel)"
REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"

cd "$REPO_ROOT"
git checkout develop >/dev/null 2>&1
git pull --ff-only >/dev/null 2>&1

ISSUE_URL=$(gh issue create -R "$REPO" --title "$TITLE" --label "$LABEL" --body "$BODY")
ISSUE_NUM=$(basename "$ISSUE_URL")

SLUG=$(echo "$TITLE" | tr '[:upper:]' '[:lower:]' | sed -E 's/[^a-z0-9]+/-/g; s/^-+|-+$//g' | cut -c1-40)
BRANCH="feature/issue-${ISSUE_NUM}-${SLUG}"
WORKTREE_PATH="$REPO_ROOT/.worktrees/issue-${ISSUE_NUM}"

mkdir -p "$REPO_ROOT/.worktrees"

git worktree add "$WORKTREE_PATH" -b "$BRANCH" develop

POSTGRES_PORT=$((5432 + ISSUE_NUM))
BACKEND_PORT=$((8000 + ISSUE_NUM))
FRONTEND_PORT=$((5173 + ISSUE_NUM))

cp "$REPO_ROOT/.env.example" "$WORKTREE_PATH/.env"
{
  echo "POSTGRES_HOST_PORT=${POSTGRES_PORT}"
  echo "BACKEND_HOST_PORT=${BACKEND_PORT}"
  echo "FRONTEND_HOST_PORT=${FRONTEND_PORT}"
} >> "$WORKTREE_PATH/.env"

WORKTREE_ABS_PATH="$(cd "$WORKTREE_PATH" && pwd -W)"

cat <<EOF

Issue:       $ISSUE_URL
Branch:      $BRANCH
Worktree:    $WORKTREE_ABS_PATH
Ports:       postgres=$POSTGRES_PORT backend=$BACKEND_PORT frontend=$FRONTEND_PORT
Chat name:   issue-${ISSUE_NUM}-${SLUG}   (name the new chat this, so it's identifiable alongside other open feature chats)

Paste this into a Claude Code session (new or existing — it switches itself into
the worktree, so you don't need to separately open a window/terminal there first):
----------------------------------------------------------------------
Your first action, before anything else, must be calling the EnterWorktree tool
with path=$WORKTREE_ABS_PATH. Do not assume you're already in the worktree just
because this text says so — verify by actually switching via the tool, since a
session that skips this step silently runs every following command against the
main checkout instead, which has happened before and corrupts branch state.

Once EnterWorktree confirms the switch, you're working on branch $BRANCH for
GitHub issue #$ISSUE_NUM. Read CLAUDE.md at the repo root, then read issue
#$ISSUE_NUM (gh issue view $ISSUE_NUM) for the task spec.

.env is already configured with non-colliding ports for this worktree — just
docker compose up -d --build and docker compose exec backend uv run alembic upgrade head.

Follow the backend-development / frontend-development / testing skills as relevant.
Run the full check suite before opening a PR (pytest, ruff, mypy, svelte-check, build),
commit with Conventional Commits, push, open a PR to develop referencing the issue
(Closes #$ISSUE_NUM), wait for CI to go green, then merge — solo project, self-merge
once CI is green is the accepted convention (docs/definition-of-done.md). Report back:
files changed, tests run and results, remaining concerns.
----------------------------------------------------------------------
EOF
