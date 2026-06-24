#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 <case_id>" >&2
  exit 2
fi

CASE_ID="$1"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CASE_DIR="$ROOT/cases/$CASE_ID"

python3 "$ROOT/scripts/validate_case.py" --case "$CASE_ID" --strict --deep
python3 "$ROOT/scripts/check_task_isolation.py" --case "$CASE_ID"
python3 "$ROOT/scripts/check_solution_leaks.py" --case "$CASE_ID"

for required in \
  "$ROOT/evidence/$CASE_ID/calibration/report.md" \
  "$ROOT/cases/$CASE_ID/private/reviews/redteam-report.md"; do
  if [[ ! -f "$required" ]]; then
    echo "ERROR: required release evidence missing: ${required#$ROOT/}" >&2
    exit 1
  fi
done

python3 "$ROOT/scripts/export_purchaser.py" --case "$CASE_ID"
ARCHIVE="$ROOT/delivery/final/$CASE_ID-purchaser-v1.zip"
sha256sum "$ARCHIVE" > "$ARCHIVE.sha256"
echo "RELEASE CHECK PASSED: ${ARCHIVE#$ROOT/}"
