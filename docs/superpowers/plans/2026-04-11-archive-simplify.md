# Archive & Simplify ClaudeCodeTest Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Move all obsolete files to an archive folder, clean up git, and update README — resulting in a minimal, focused repository.

**Architecture:** Simple three-phase approach: (1) Create archive directory and copy obsolete files, (2) Remove moved files from git staging, (3) Update documentation and commit.

**Tech Stack:** Bash, git, file system operations.

---

## File Structure

**Files to modify/create:**
- Create: `I:\Mon disque\Canada 2026\01 - Development\ClaudeCodeTest-archive\` (outside git)
- Modify: `README.md` — simplify to describe memory infrastructure only
- Remove from git: ~40 obsolete files and folders (see task lists)

**Files to keep:**
- `.git/`, `.gitignore`, `CLAUDE.md`
- `memory/`, `.remember/`, `.claude/`

---

## Phase 1: Create Archive and Move Files

### Task 1: Create Archive Directory

- [ ] **Step 1: Create archive folder**

```bash
mkdir -p "I:/Mon disque/Canada 2026/01 - Development/ClaudeCodeTest-archive"
```

Expected: Folder created at parent level

- [ ] **Step 2: Verify creation**

```bash
ls -la "I:/Mon disque/Canada 2026/01 - Development/" | grep -i archive
```

Expected: `ClaudeCodeTest-archive` folder listed

### Task 2: Move Historical .md Files to Archive

**Files to move:**
- COMPLETE-HISTORY-CLEANUP.md
- CRITICAL-FIX-COMMIT-MESSAGE.md
- FINAL-COMMIT-SUBJECT-CLEANUP.md
- FINAL-SUMMARY.md
- FRESH-CLEAN-REPOSITORY.md
- GIT-HISTORY-CLEANUP.md
- PASSWORD-UPDATE.md
- PROJECT-COMPLETION.md
- REMEDIATION-SUMMARY-SAFE-TRAINER.md
- SECURITY-AUDIT.md
- SECURITY-AUDIT-SAFE-TRAINER.md
- .claude-memory.md

- [ ] **Step 1: Copy .md files to archive**

From `I:\Mon disque\Canada 2026\01 - Development\ClaudeCodeTest\`:

```bash
cd "I:/Mon disque/Canada 2026/01 - Development/ClaudeCodeTest"
cp COMPLETE-HISTORY-CLEANUP.md CRITICAL-FIX-COMMIT-MESSAGE.md FINAL-COMMIT-SUBJECT-CLEANUP.md FINAL-SUMMARY.md FRESH-CLEAN-REPOSITORY.md GIT-HISTORY-CLEANUP.md PASSWORD-UPDATE.md PROJECT-COMPLETION.md REMEDIATION-SUMMARY-SAFE-TRAINER.md SECURITY-AUDIT.md SECURITY-AUDIT-SAFE-TRAINER.md .claude-memory.md "../ClaudeCodeTest-archive/"
```

Expected: All 12 .md files copied

- [ ] **Step 2: Verify copies**

```bash
ls -1 "../ClaudeCodeTest-archive/" | wc -l
```

Expected: At least 12 files listed

### Task 3: Move Folders to Archive

**Folders to move:**
- qr-generator/
- docs/ (EXCEPT superpowers/specs and superpowers/plans which stay in git)
- tests/
- tasks/ (session-specific lessons and todos)
- scripts/
- __pycache__/
- .pytest_cache/
- .worktrees/
- https/

- [ ] **Step 1: Copy non-docs folders to archive**

```bash
cd "I:/Mon disque/Canada 2026/01 - Development/ClaudeCodeTest"
cp -r qr-generator tests tasks scripts __pycache__ .pytest_cache .worktrees https "../ClaudeCodeTest-archive/" 2>/dev/null || true
```

Expected: Folders copied (some may not exist, that's OK)

- [ ] **Step 2: Copy docs/ excluding superpowers/ subdirectory**

```bash
mkdir -p "../ClaudeCodeTest-archive/docs"
for item in docs/*; do
  if [ ! -d "$item" ] || [ "$(basename "$item")" != "superpowers" ]; then
    cp -r "$item" "../ClaudeCodeTest-archive/docs/" 2>/dev/null || true
  fi
done
```

This excludes the superpowers/ directory, which stays in git with the plans and specs.

- [ ] **Step 3: Verify folder count**

```bash
find "../ClaudeCodeTest-archive" -maxdepth 1 -type d | wc -l
```

Expected: ~10 directories

### Task 4: Move Python Files and Data Files to Archive

**Files to move:**
- encryption.py
- excel_reader.py
- extract_from_images.py
- generate_qr_codes.py
- qr_generator.py
- read_excel.ps1
- serve.ps1
- memory.sh
- sample_data.xlsx
- ocr_output.txt
- requirements.txt

- [ ] **Step 1: Copy Python, PowerShell, and data files**

```bash
cd "I:/Mon disque/Canada 2026/01 - Development/ClaudeCodeTest"
cp encryption.py excel_reader.py extract_from_images.py generate_qr_codes.py qr_generator.py read_excel.ps1 serve.ps1 memory.sh sample_data.xlsx ocr_output.txt requirements.txt "../ClaudeCodeTest-archive/" 2>/dev/null || true
```

Expected: All files copied

- [ ] **Step 2: Verify copies**

```bash
ls -1 "../ClaudeCodeTest-archive/" | grep -E "\.(py|ps1|sh|xlsx|txt)$" | wc -l
```

Expected: At least 11 files listed

---

## Phase 2: Remove Files from Git

### Task 5: Stage Removals of Historical .md Files

- [ ] **Step 1: Remove .md files from git**

```bash
cd "I:/Mon disque/Canada 2026/01 - Development/ClaudeCodeTest"
git rm COMPLETE-HISTORY-CLEANUP.md CRITICAL-FIX-COMMIT-MESSAGE.md FINAL-COMMIT-SUBJECT-CLEANUP.md FINAL-SUMMARY.md FRESH-CLEAN-REPOSITORY.md GIT-HISTORY-CLEANUP.md PASSWORD-UPDATE.md PROJECT-COMPLETION.md REMEDIATION-SUMMARY-SAFE-TRAINER.md SECURITY-AUDIT.md SECURITY-AUDIT-SAFE-TRAINER.md .claude-memory.md 2>/dev/null || true
```

Expected: Files staged for removal

- [ ] **Step 2: Verify staging**

```bash
git status | grep -E "deleted:"
```

Expected: 12 deleted entries listed

### Task 6: Remove Folders from Git

- [ ] **Step 1: Remove folders from git (keeping docs/superpowers/)**

```bash
git rm -r qr-generator tests tasks scripts __pycache__ .pytest_cache .worktrees https 2>/dev/null || true
```

Expected: Folders staged for removal

- [ ] **Step 2: Remove only non-superpowers docs files from git**

```bash
cd docs
for item in *; do
  if [ ! -d "$item" ] || [ "$item" != "superpowers" ]; then
    git rm -r "$item" 2>/dev/null || true
  fi
done
cd ..
```

This removes docs/ contents except the superpowers/ directory which stays in git.

- [ ] **Step 3: Verify staging**

```bash
git status | grep "deleted:" | wc -l
```

Expected: Count shows multiple deleted entries (folders with many files)

### Task 7: Remove Python, PowerShell, and Data Files from Git

- [ ] **Step 1: Remove individual files from git**

```bash
git rm encryption.py excel_reader.py extract_from_images.py generate_qr_codes.py qr_generator.py read_excel.ps1 serve.ps1 memory.sh sample_data.xlsx ocr_output.txt requirements.txt 2>/dev/null || true
```

Expected: Files staged for removal

- [ ] **Step 2: Check git status for remaining untracked files**

```bash
git status
```

Expected: Shows only deleted files and possibly modified files (README.md)

---

## Phase 3: Update Documentation and Commit

### Task 8: Update README.md

- [ ] **Step 1: Read current README.md**

```bash
cat README.md
```

- [ ] **Step 2: Replace README.md with minimal version**

Create new `README.md`:

```markdown
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
```

- [ ] **Step 3: Write the new README**

```bash
cat > README.md << 'EOF'
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
EOF
```

Expected: README.md replaced with new content

- [ ] **Step 4: Verify README content**

```bash
head -15 README.md
```

Expected: New content with "Persistent memory" heading visible

### Task 9: Final Cleanup Commit

- [ ] **Step 1: Check git status**

```bash
git status --short | head -30
```

Expected: Mix of deleted files (D) and modified README.md (M)

- [ ] **Step 2: Stage README.md update**

```bash
git add README.md
```

Expected: README.md now staged

- [ ] **Step 3: Create final commit**

```bash
git commit -m "refactor: archive legacy files and simplify project

- Move obsolete files to ClaudeCodeTest-archive/ (outside version control)
- Archive: QR generator, dashboard, tests, tasks/, docs (except superpowers/), scripts
- Remove 40+ historical, cleanup, and utility files from git
- Preserve: memory/, .remember/, docs/superpowers/ (specs and plans)
- Update README to describe persistent memory infrastructure only"
```

Expected: Commit created with detailed message

- [ ] **Step 4: Verify commit**

```bash
git log --oneline -1
```

Expected: New commit message visible

### Task 10: Final Verification

- [ ] **Step 1: Check repository size**

```bash
du -sh .git
```

Expected: Should be relatively small (memory and basic structure only)

- [ ] **Step 2: List root directory**

```bash
ls -la | grep -v "^d" | awk '{print $9}' | grep -v "^$"
```

Expected: Only .gitignore, README.md, CLAUDE.md, plus directories

- [ ] **Step 3: List root directories and verify docs/superpowers exists**

```bash
ls -d */ 2>/dev/null
ls docs/
```

Expected: 
- Root dirs: `.git/`, `.claude/`, `.remember/`, `memory/`, `docs/`
- docs/ contains: `superpowers/` (only this directory)

- [ ] **Step 4: Verify archive exists**

```bash
ls -la "../ClaudeCodeTest-archive/" | head -20
```

Expected: Archive folder contains 40+ files

- [ ] **Step 5: Confirm no files accidentally deleted**

```bash
ls "../ClaudeCodeTest-archive/" | wc -l
```

Expected: Count > 40 (all moved files present)

---

## Success Checklist

✓ Archive directory created outside git  
✓ All obsolete files copied to archive  
✓ All obsolete files removed from git (git rm)  
✓ README.md updated with minimal description  
✓ Final commit created with clear message  
✓ Root directory contains only essential files  
✓ No files accidentally deleted (all in archive)  
