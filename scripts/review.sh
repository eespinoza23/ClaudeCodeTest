#!/usr/bin/env bash
# Display all decisions flagged REVIEW DUE in a readable format.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV="$SCRIPT_DIR/../memory/decisions.csv"

py - "$CSV" << 'PYEOF'
import csv, sys, pathlib, textwrap

csv_path = sys.argv[1]
p = pathlib.Path(csv_path)

if not p.exists():
    print("No decisions.csv found.")
    sys.exit(0)

with open(p, newline="", encoding="utf-8") as f:
    due = [r for r in csv.DictReader(f) if r["status"] == "REVIEW DUE"]

if not due:
    print("No decisions pending review.")
    sys.exit(0)

W = 62
print(f"\n{'='*W}")
label = f"  DECISIONS PENDING REVIEW  ({len(due)} item{'s' if len(due) != 1 else ''})"
print(label)
print(f"{'='*W}\n")

INDENT = "               "
for i, r in enumerate(due, 1):
    print(f"  [{i}] Logged:     {r['date']}")
    print(f"      Decision:   " + textwrap.fill(
        r["decision"], W - 16, subsequent_indent=INDENT))
    print(f"      Reasoning:  " + textwrap.fill(
        r["reasoning"], W - 16, subsequent_indent=INDENT))
    print(f"      Expected:   " + textwrap.fill(
        r["expected_outcome"], W - 16, subsequent_indent=INDENT))
    print(f"      Review due: {r['review_date']}")
    if i < len(due):
        print(f"  {'-'*(W-2)}")
print(f"\n{'='*W}\n")
PYEOF
