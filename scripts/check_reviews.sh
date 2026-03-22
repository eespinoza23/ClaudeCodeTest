#!/usr/bin/env bash
# Daily check: flag any decisions whose review_date has passed.
# Appends REVIEW DUE status in-place on matching rows.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV="$SCRIPT_DIR/../memory/decisions.csv"

py - "$CSV" << 'PYEOF'
import csv, sys, datetime, pathlib

csv_path = sys.argv[1]
p = pathlib.Path(csv_path)

if not p.exists():
    print("No decisions.csv found — nothing to check.")
    sys.exit(0)

today = datetime.date.today()
flagged = 0
rows = []

with open(p, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    fieldnames = reader.fieldnames
    for row in reader:
        if row["status"] == "PENDING":
            try:
                review_date = datetime.date.fromisoformat(row["review_date"])
            except ValueError:
                rows.append(row)
                continue
            if review_date <= today:
                row["status"] = "REVIEW DUE"
                flagged += 1
        rows.append(row)

with open(p, "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=fieldnames)
    w.writeheader()
    w.writerows(rows)

if flagged:
    print(f"[check_reviews] Flagged {flagged} decision(s) as REVIEW DUE.")
else:
    print(f"[check_reviews] No new reviews due as of {today.isoformat()}.")
PYEOF
