---
name: tb-hard-release-audit
description: Audit a calibrated Harbor task for deterministic purchaser export, leakage, evidence completeness, and release readiness.
argument-hint: "<case_id>"
user-invocable: true
context: fork
agent: harbor-release-auditor
model: sonnet
effort: high
allowed-tools: Read Write Edit Glob Grep Bash
---

# tb-hard Release Audit

Target case: `$ARGUMENTS`

Audit only frozen validated tasks. Confirm current Oracle, red-team, and calibration evidence; inspect package contents; run leakage/isolation checks; confirm reward paths and task metadata; and verify the purchaser adapter does not diverge from the canonical Harbor task.

Write audit evidence under `evidence/<case_id>/release/`. Do not edit task semantics, solution, tests, or delivery archives. Return `ready`, `ready-with-nonblocking-notes`, or `blocked` with exact remediation and retest requirements.
