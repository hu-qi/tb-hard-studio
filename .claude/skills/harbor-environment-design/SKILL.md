---
name: harbor-environment-design
description: Build or repair a deterministic Harbor task environment with explicit resources, network policy, health checks, and safe solver-visible boundaries.
argument-hint: "<case_id>"
user-invocable: true
context: fork
agent: harbor-env-engineer
model: sonnet
effort: high
allowed-tools: Read Write Edit Glob Grep Bash
---

# Harbor Environment Design

Target case: `$ARGUMENTS`

Read the approved private design brief and preserve the public task contract. Modify only `cases/<case_id>/task/environment/` and environment-related portions of `task/task.toml`.

Build from deterministic assets, pin data generation, declare `network_mode`, and keep the initial state genuinely unsolved. Use Compose only when multi-service behavior is part of the intended capability. Add health checks and sidecar artifact strategy when applicable.

Never copy solution, tests, private notes, evidence, skills, subagents, Git metadata, credentials, or caches into the solver image. Run `make validate CASE=<case_id>` after edits and return build commands, baseline-state evidence, resource/network decisions, and any recommendation for separate verification.
