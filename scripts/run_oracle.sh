#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <case_id> [extra harbor run args...]" >&2
  exit 2
fi

CASE_ID="$1"
shift
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CASE_DIR="$ROOT/cases/$CASE_ID"
TASK_DIR="$CASE_DIR/task"
RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-oracle"
EVIDENCE_DIR="$ROOT/evidence/$CASE_ID/oracle/$RUN_ID"
mkdir -p "$EVIDENCE_DIR"

python3 "$ROOT/scripts/validate_case.py" --case "$CASE_ID" --deep
if ! command -v harbor >/dev/null 2>&1; then
  echo "ERROR: Harbor is required. Install with: uv tool install harbor" >&2
  exit 127
fi

printf '%q ' harbor run -p "$TASK_DIR" -a oracle "$@" > "$EVIDENCE_DIR/command.txt"
printf '\n' >> "$EVIDENCE_DIR/command.txt"
{
  echo "run_id=$RUN_ID"
  echo "started_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "case_id=$CASE_ID"
  echo "task_dir=$TASK_DIR"
  echo "harbor_version=$(harbor --version 2>/dev/null || true)"
  echo "task_revision=$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo uncommitted)"
  echo "network_mode=$(grep -A8 '^\[environment\]' "$TASK_DIR/task.toml" | grep '^network_mode' || true)"
} > "$EVIDENCE_DIR/environment.txt"

set +e
harbor run -p "$TASK_DIR" -a oracle "$@" 2>&1 | tee "$EVIDENCE_DIR/console.log"
status=${PIPESTATUS[0]}
set -e
{
  echo "ended_at=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "exit_code=$status"
  echo "NOTE: copy the Harbor job/trial reference and verifier logs here if your Harbor provider stores them outside this repository."
} >> "$EVIDENCE_DIR/environment.txt"

if [[ "$status" -eq 0 ]]; then
  echo "Oracle command completed. Confirm Harbor reward and update case.yaml/evidence before advancing status."
else
  echo "Oracle command failed; inspect $EVIDENCE_DIR/console.log" >&2
fi
exit "$status"
