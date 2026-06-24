---
name: harbor-oracle-verifier
description: Implement a legitimate Harbor Oracle solution and validate its behavior against an independent verifier without weakening the task contract.
argument-hint: "<case_id>"
user-invocable: true
context: fork
agent: oracle-solution-engineer
model: opus
effort: xhigh
allowed-tools: Read Write Edit Glob Grep Bash
---

# Harbor Oracle Verification

Target case: `$ARGUMENTS`

The Oracle proves solvability. Work only in `cases/<case_id>/task/solution/` unless the main agent explicitly assigns a verifier defect investigation. Do not weaken or redesign tests, public constraints, or task semantics to make the Oracle pass.

Solve from the same baseline available to a competent solver. Do not hardcode public samples or read private briefs, calibration evidence, hidden grader material, or authoring assets. Run `make oracle CASE=<case_id>` from a clean environment and preserve command/log metadata under `evidence/<case_id>/oracle/`.

Return changed files, run command, reward, logs, and any independently reviewable coverage concern.
