#!/usr/bin/env bash
# Log a decision to memory/decisions.csv
# Usage: ./scripts/log_decision.sh "decision" "reasoning" "expected_outcome"
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV="$SCRIPT_DIR/../memory/decisions.csv"

if [ $# -lt 3 ]; then
  echo "Usage: $0 \"decision\" \"reasoning\" \"expected_outcome\""
  exit 1
fi

py - "$CSV" "$1" "$2" "$3" << 'PYEOF'
import csv, sys, datetime, pathlib

csv_path  = sys.argv[1]
decision  = sys.argv[2]
reasoning = sys.argv[3]
outcome   = sys.argv[4]

today  = datetime.date.today()
review = today + datetime.timedelta(days=30)

p = pathlib.Path(csv_path)
p.parent.mkdir(parents=True, exist_ok=True)
needs_header = not p.exists() or p.stat().st_size == 0

with open(p, "a", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    if needs_header:
        w.writerow(["date","decision","reasoning","expected_outcome","review_date","status"])
    w.writerow([today.isoformat(), decision, reasoning, outcome, review.isoformat(), "PENDING"])

print(f"Decision logged.")
print(f"  Date:        {today.isoformat()}")
print(f"  Decision:    {decision}")
print(f"  Review due:  {review.isoformat()}")
PYEOF
