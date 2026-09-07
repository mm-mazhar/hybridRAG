#!/usr/bin/env bash
set -euo pipefail
MSG=$(cat "$1")
PATTERN='^(feat|fix|bugfix|refactor|docs|style|test|chore|ci|perf|build|revert)(\(.+\))?!?: .{1,100}$'
if ! echo "$MSG" | grep -qE "$PATTERN"; then
  echo "Invalid commit message format."
  echo ""
  echo "Expected: <type>(<scope>): <subject>"
  echo "  Types: feat, fix, bugfix, refactor, docs, style, test, chore, ci, perf, build, revert"
  echo "  Append ! before the colon to mark a breaking change: feat(api)!: drop v1 endpoints"
  echo "  Example: feat(api): add pagination to list endpoint"
  echo ""
  echo "Got: $MSG"
  exit 1
fi
