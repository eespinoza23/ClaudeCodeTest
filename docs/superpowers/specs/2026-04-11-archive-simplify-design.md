# Design: Archive & Simplify ClaudeCodeTest

**Date:** 2026-04-11  
**Goal:** Remove obsolete files and clean up the repository, leaving only essential infrastructure.

---

## Current State

ClaudeCodeTest has accumulated files from multiple experiments and historical cleanup iterations:

**Active content:** None (verified with user)

**Obsolete files (to archive):**
- Historical cleanup/remediation documents (COMPLETE-HISTORY-CLEANUP.md, REMEDIATION-SUMMARY-SAFE-TRAINER.md, SECURITY-AUDIT.md, etc.)
- QR code generator (qr-generator/, generate_qr_codes.py, qr_generator.py, excel_reader.py, read_excel.ps1)
- PI Dashboard/planner (pi-planner-source.html, pi-planner-source.html)
- Supporting scripts and utilities (encryption.py, extract_from_images.py, memory.sh, serve.ps1)
- Tasks folder (tasks/ — lessons.md, todo.md are session-specific, not persistent)
- Tests and documentation (tests/, docs/ EXCEPT superpowers/specs and superpowers/plans, scripts/)
- Data files (sample_data.xlsx, ocr_output.txt, requirements.txt)
- Python/test artifacts (__pycache__/, .pytest_cache/)
- HTTPS support folder (https/)

---

## Design

### 1. Archive Location

Create `ClaudeCodeTest-archive/` at the same parent level:
```
I:\Mon disque\Canada 2026\01 - Development\
  ├── ClaudeCodeTest/          (cleaned, minimal)
  └── ClaudeCodeTest-archive/  (all obsolete content)
```

Archive folder is **not version controlled** — manual backup responsibility. Keeps main repo simple and fast.

### 2. Files to Archive

Move to `ClaudeCodeTest-archive/`:
- All `.md` files except README.md and CLAUDE.md
- Folders: qr-generator/, docs/, tests/, scripts/, __pycache__/, .pytest_cache/, .worktrees/, https/
- Python files: encryption.py, excel_reader.py, extract_from_images.py, generate_qr_codes.py, qr_generator.py
- PowerShell: read_excel.ps1, serve.ps1, memory.sh
- Data files: sample_data.xlsx, ocr_output.txt, requirements.txt
- Metadata: .claude-memory.md (session-only, not persistent)

### 3. Files to Keep

**In ClaudeCodeTest root:**
- `.git/`, `.gitignore` — version control
- `README.md` — simplified, describes memory infrastructure only
- `CLAUDE.md` — Claude Code instructions (unchanged)
- `memory/` — persistent memory (decisions.md, people.md, preferences.md, user.md, decisions.csv)
- `.remember/` — daily/session logs

**In `.claude/`:**
- `settings.json` — user settings
- `settings.local.json` — local overrides
- `skills/` — custom skills

### 4. Cleanup Steps

1. Create archive directory outside git
2. Move all obsolete files (preserves them, not deleted)
3. Remove from git (git rm, not delete)
4. Update README.md to describe current state
5. Single commit: "refactor: archive legacy files and simplify project"

### 5. Result

**ClaudeCodeTest becomes:**
- A clean testbed for future experiments
- Persistent memory infrastructure in place
- No dead code or historical cruft
- Fast git operations
- ~200 KB instead of current size

---

## Success Criteria

✓ All non-essential files moved to archive/  
✓ All moved files removed from git staging  
✓ Commit reflects the cleanup  
✓ Root directory contains only: .git/, .gitignore, .claude/, README.md, CLAUDE.md, memory/, .remember/  
✓ README.md describes current minimal state  
✓ `.pytest_cache/`, `https/`, and all `.md` cleanup files removed from repo
