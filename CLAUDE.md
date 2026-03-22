# CLAUDE.md

@.claude-memory.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Context

**Project:** ClaudeCodeTest — HTML5 browser games (shooter, tictactoe) + tooling experiments

## Project Rules

- **At session start:** read `tasks/lessons.md` to recall past corrections
- **During work:** update `tasks/todo.md` as tasks are started and completed
- **At session end:** update `tasks/lessons.md` with any new patterns or corrections learned

## Persistent Memory

A `memory/` directory stores context that persists across sessions. **At the start of every session**, read all four files:

```
memory/decisions.md   — architectural/technical choices and rationale
memory/people.md      — people involved in or related to the project
memory/preferences.md — coding conventions and workflow habits
memory/user.md        — stable facts about the user and environment
```

**At the end of every session** (or after any significant discovery), update the relevant files:
- New architectural decision made → append to `decisions.md` AND log it to `decisions.csv` (see below)
- Learned something about the user's style or tooling → update `preferences.md` or `user.md`
- New person mentioned → add to `people.md`
- Keep entries concise; remove or correct anything that turns out to be wrong

## Decision Logging

Whenever the user describes a decision they are making, immediately log it to `memory/decisions.csv` using:

```bash
bash scripts/log_decision.sh "decision" "reasoning" "expected_outcome"
```

The CSV tracks: `date, decision, reasoning, expected_outcome, review_date (30 days out), status`.

**Review workflow:**
- `scripts/check_reviews.sh` — flags rows whose `review_date` has passed (sets status → `REVIEW DUE`)
- `scripts/review.sh` — prints only `REVIEW DUE` items in a readable format
- A cron job runs `check_reviews.sh` daily at 8:23 AM (session-only; re-register on new sessions)

**Python interpreter on this machine:** use `py` (Windows launcher, available in Git Bash at `/c/Windows/py`).

## Project Overview

This repo contains two standalone HTML5 browser games — no build system, no dependencies, no package manager. Each game is a single self-contained file (HTML + CSS + JS inline).

## Running the Games

Open either file directly in a browser:
- `shooter.html` — "SURVIVOR", a top-down canvas shooter
- `tictactoe.html` — two-player Tic Tac Toe

No server required. No compilation step.

## Git Workflow

Commit and push to GitHub regularly throughout work — after each meaningful change, not just at the end. This ensures work is never lost.

- Use clear, specific commit messages describing what changed and why (e.g. `fix: clamp player position to canvas bounds` not `update`)
- Push after every commit: `git add -A && git commit -m "..." && git push`
- Never leave significant work uncommitted at the end of a session

## Architecture

### shooter.html
- Canvas-based game loop using `requestAnimationFrame`
- State machine: `STATE = { MENU, PLAYING, LEVEL_COMPLETE, GAME_OVER, VICTORY, PAUSED }`
- 5 levels defined in `LEVELS[]`; 3 enemy types in `ENEMY_DEFS` (grunt, charger, tank)
- Each frame: `updatePlaying(dt)` handles physics/collisions, then `drawPlaying()` renders
- Player aims at mouse cursor; fires on `mousedown`; moves with WASD/arrow keys
- `dt` is capped at 50ms to prevent spiral-of-death on tab blur

### tictactoe.html
- Pure DOM manipulation, no canvas
- Game state: flat 9-element `board[]` array, `current` player, `over` flag, `scores` object
- Win detection iterates `WINS[]` (8 possible lines) after each move
- Scores persist in memory only (reset on page reload)
