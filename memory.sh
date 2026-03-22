#!/usr/bin/env bash
# memory.sh — Launch Claude Code with rich project context as system prompt

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"

# Gather context
BRANCH=$(git -C "$REPO_ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
RECENT_COMMITS=$(git -C "$REPO_ROOT" log --oneline -5 2>/dev/null || echo "(no commits)")
MODIFIED_FILES=$(git -C "$REPO_ROOT" status --short 2>/dev/null || echo "(none)")
LESSONS=$(cat "$REPO_ROOT/tasks/lessons.md" 2>/dev/null || echo "(no lessons yet)")
MEMORY_LOG=$(cat "$REPO_ROOT/.claude-memory.md" 2>/dev/null || echo "(no memory log yet)")

SYSTEM_PROMPT="$(cat <<EOF
## Project: ClaudeCodeTest
Branch: $BRANCH

### Recent Commits
$RECENT_COMMITS

### Modified Files
$MODIFIED_FILES

### Lessons Learned
$LESSONS

### Commit History Log
$MEMORY_LOG
EOF
)"

# Launch Claude with context
claude \
  --permission-mode acceptEdits \
  --allowedTools "Bash(git:*) Bash(npm:*) Edit Write Read" \
  --system-prompt "$SYSTEM_PROMPT" \
  "$@"
