---
name: harbor-rollout-calibration
description: Calibrate a frozen tb-hard task using Harbor Oracle and real-agent rollouts, then distinguish authentic difficulty from ambiguity, flakiness, leakage, or infrastructure failure.
argument-hint: "<case_id>"
user-invocable: true
context: fork
agent: harbor-rollout-analyst
model: opus
effort: xhigh
allowed-tools: Read Write Edit Glob Grep Bash
---

# Harbor Rollout Calibration

Target case: `$ARGUMENTS`

Follow `tooling/calibration-protocol.v1.yaml`. Do not calibrate until the Oracle has full reward, red-team review has no unresolved P0/P1 finding, and public task content is frozen.

Run or analyze Harbor trials with fixed task revision, protocol metadata, and preserved logs. Use `make rollouts CASE=<case_id> AGENT=<agent> MODEL=<model> TRIALS=<n>` where local execution is available.

Write `evidence/<case_id>/calibration/report.md`. Report pass rate, runtime, timeout rate, trajectory-depth observations, failure taxonomy, evidence for the intended difficulty dimensions, and one decision: accept, strengthen, clarify, repair, or reject. Low pass rate alone is not evidence of quality.
