# ClaudeCodeTest

Persistent memory and context infrastructure for Claude Code sessions.

## Structure

- **memory/** — Persistent context across sessions
  - `decisions.md` — Architectural decisions and their rationale
  - `people.md` — People and roles in the project
  - `preferences.md` — Coding conventions and workflow patterns
  - `user.md` — User profile and environment facts
  - `decisions.csv` — Decision log with review dates and status

- **.remember/** — Session and daily logs
  - Daily capture of patterns, corrections, and discoveries
  - Persists context within and across sessions

## Usage

Update memory files as you work:
- New decision → append to `memory/decisions.md` and log to `decisions.csv`
- Learned pattern → update `memory/preferences.md`
- New person involved → add to `memory/people.md`

Archive-related files have been moved to `ClaudeCodeTest-archive/` (not version controlled).

For full Claude Code documentation, see `CLAUDE.md`.
