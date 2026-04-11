# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

**Project:** ClaudeCodeTest — Persistent memory infrastructure testbed for Claude Code

**Repo status (2026-04-11):** Cleaned & minimal. Legacy experiments archived to `ClaudeCodeTest-archive/` (outside git). Active content: memory infrastructure, design specs, implementation plans.

## Persistent Memory

The `memory/` directory in this repo stores context across sessions:

```
memory/decisions.md   — architectural decisions + rationale
memory/people.md      — people involved in projects
memory/preferences.md — coding conventions and patterns
memory/user.md        — stable user facts and environment
memory/decisions.csv  — decision log with review dates
```

**Workflow:**
- **Session start:** Read these files (loaded via MEMORY.md index in ~/.claude/)
- **During work:** Log decisions to decisions.csv as they're made
- **Session end:** Update memory files with new patterns/decisions/people

**How to update:**
```bash
# Log a decision (auto-adds 30-day review date)
bash scripts/log_decision.sh "decision" "reasoning" "expected_outcome"

# View decisions due for review
bash scripts/review.sh
```

**Key memory files outside repo:** Global memories stored in `C:\Users\learn\.claude\projects\I--Mon-disque-Canada-2026-01---Development-ClaudeCodeTest\memory\` — these persist across all sessions and include:
- project_claudecodetest_cleaned.md
- feedback_subagent_workflow.md
- feedback_token_optimization.md
- reference_paths.md
- project_pi_dashboard.md (deployment pending)

## Git Workflow

Commit and push to GitHub regularly throughout work — after each meaningful change, not just at the end. This ensures work is never lost.

- Use clear, specific commit messages describing what changed and why (e.g. `fix: clamp player position to canvas bounds` not `update`)
- Push after every commit: `git add -A && git commit -m "..." && git push`
- Never leave significant work uncommitted at the end of a session

