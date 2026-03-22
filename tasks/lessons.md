# Lessons Learned

Patterns and corrections to carry forward. Read this at the start of every session.

---

## Python on Windows
- Use `py` (not `python` or `python3`) in Git Bash — Windows launcher at `/c/Windows/py`
- f-strings with backslashes in expressions fail on Python <3.12: extract to variable first

## HTML Single-File Projects
- Avoid string-to-page mapping for slide thumbnails; use page number as primary key directly
- HTML entities (`&amp;`) in JS string matching will silently break comparisons

## Rebuilding HTML from Python
- Write the Python script to a file first, then run it — avoids heredoc quote conflicts
- For large files (>1MB), use Write tool not Bash echo/cat

## Git Workflow
- Push after every meaningful commit, not just at end of session
- Keep commit messages specific and action-oriented
