---
name: harbor-redteam-verifier
description: Red-team a Harbor verifier for answer leakage, reward hacking, shared-container tampering, artifact manipulation, and semantic under-testing.
argument-hint: "<case_id>"
user-invocable: true
context: fork
agent: verifier-security-reviewer
model: sonnet
effort: high
allowed-tools: Read Write Edit Glob Grep Bash
---

# Harbor Verifier Red Team

Target case: `$ARGUMENTS`

Treat the solver as adversarial. Inspect `task/`, Docker build boundaries, task metadata, verifier mode, artifact declarations, sidecars, startup behavior, and test coverage.

Attempt to pass without solving by deleting functionality, hardcoding visible samples, tampering with wrappers/PATH/environment, reading image layers or Git history, abusing caches/processes/sidecars, or modifying shared verification state. Determine whether a separate verifier is necessary.

Write `cases/<case_id>/private/reviews/redteam-report.md` with severity, exploit path, grading impact, minimal remediation, and retest steps. Do not edit benchmark semantics or silently relax the verifier.
