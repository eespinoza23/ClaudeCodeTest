# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

**ClaudeCodeTest** — Persistent memory infrastructure testbed for Claude Code. Acts as a sandbox for:
- Memory system design and validation
- Skills development and testing (.agents/skills/)
- Documentation for cross-project work (docs/superpowers/)

**Status:** Cleaned 2026-04-11. Archive of legacy experiments at `ClaudeCodeTest-archive/` (outside git).

## Repository Structure

### `memory/` — Session-independent context
Persists across all sessions (indexed at `~/.claude/projects/.../memory/MEMORY.md`):
- `decisions.md` — Architectural decisions with reasoning
- `people.md` — People and roles across projects
- `preferences.md` — Coding conventions (e.g., Python launcher, HTML format)
- `user.md` — User environment facts
- `decisions.csv` — Decision log with 30-day review tracking

Update memory during work; these files inform all future sessions on this project.

### `.remember/` — Session-specific logs
Daily captures of patterns, discoveries, and context. Not version-controlled; for in-session reference.

### `.agents/skills/` — Testbed for skill development
Skills under development or testing:
- `caveman-compress/` — Token compression for memory files
- `caveman/`, `caveman-commit/`, `caveman-help/`, `caveman-review/` — Caveman toolkit variants
- `compress/` — Generic compression utility

Skills here may be reference implementations or experimental versions.

### `docs/superpowers/` — Cross-project planning
Design specs and implementation plans for major projects (Poker Points, PI Dashboard, etc.):
- `specs/` — Technical design documents with architecture, API, UI flow
- `plans/` — Step-by-step implementation roadmaps with TDD structure

## Working with This Repo

### Memory Updates
Update `memory/` files when you:
- Learn a coding pattern or preference
- Make a significant architectural decision
- Need to record who's involved in what

These changes persist across all future sessions; they're the primary value of this repo.

### Skills Development
Skills in `.agents/skills/` are testbed projects. If working on a skill:
1. Work in a worktree to isolate changes
2. Follow the skill's own CLAUDE.md or SKILL.md for development guidance
3. Commit regularly to avoid losing work

### Git Workflow
- Commit after each meaningful change (not batched at session end)
- Push immediately after each commit: `git add -A && git commit -m "..." && git push`
- Use imperative, specific messages: `fix: handle edge case in decision logging` not `update`

