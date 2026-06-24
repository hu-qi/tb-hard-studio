#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 4 ]]; then
  echo "Usage: $0 <case_id> <agent> <model> <trials> [extra harbor run args...]" >&2
  exit 2
fi

CASE_ID="$1"; AGENT="$2"; MODEL="$3"; TRIALS="$4"; shift 4
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
CASE_DIR="$ROOT/cases/$CASE_ID"
TASK_DIR="$CASE_DIR/task"
BASE="$ROOT/evidence/$CASE_ID/calibration"
mkdir -p "$BASE/runs"

python3 "$ROOT/scripts/validate_case.py" --case "$CASE_ID" --deep

for required in "oracle_status: passed" "redteam_status: passed"; do
  if ! grep -qx "$required" "$CASE_DIR/case.yaml"; then
    echo "ERROR: calibration requires $required in cases/$CASE_ID/case.yaml" >&2
    exit 1
  fi
done
if ! command -v harbor >/dev/null 2>&1; then
  echo "ERROR: Harbor is required. Install with: uv tool install harbor" >&2
  exit 127
fi
if ! [[ "$TRIALS" =~ ^[1-9][0-9]*$ ]]; then
  echo "ERROR: trials must be a positive integer" >&2
  exit 2
fi

AGG="$BASE/aggregate.csv"
if [[ ! -f "$AGG" ]]; then
  echo 'run_id,agent,model,trial,start_utc,end_utc,wall_clock_sec,exit_code,reward,task_revision,log_dir' > "$AGG"
fi

for ((i = 1; i <= TRIALS; i++)); do
  RUN_ID="$(date -u +%Y%m%dT%H%M%SZ)-${AGENT//[^a-zA-Z0-9]/-}-$i"
  RUN_DIR="$BASE/runs/$RUN_ID"
  mkdir -p "$RUN_DIR"
  start_epoch="$(date +%s)"
  start_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  printf '%q ' harbor run -p "$TASK_DIR" -a "$AGENT" -m "$MODEL" "$@" > "$RUN_DIR/command.txt"
  printf '\n' >> "$RUN_DIR/command.txt"
  set +e
  harbor run -p "$TASK_DIR" -a "$AGENT" -m "$MODEL" "$@" 2>&1 | tee "$RUN_DIR/console.log"
  status=${PIPESTATUS[0]}
  set -e
  end_epoch="$(date +%s)"
  end_utc="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  duration=$((end_epoch - start_epoch))
  revision="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo uncommitted)"
  cat > "$RUN_DIR/summary.md" <<SUMMARY
# Rollout $RUN_ID

- Agent: $AGENT
- Model: $MODEL
- Trial: $i / $TRIALS
- Start: $start_utc
- End: $end_utc
- Wall clock seconds: $duration
- Exit code: $status
- Task revision: $revision
- Reward: inspect Harbor job/trial/verifier artifacts and fill in after collection.
SUMMARY
  echo "$RUN_ID,$AGENT,$MODEL,$i,$start_utc,$end_utc,$duration,$status,unknown,$revision,$RUN_DIR" >> "$AGG"
done

echo "Rollouts complete. Analyze $BASE/aggregate.csv and write $BASE/report.md before changing task status."
