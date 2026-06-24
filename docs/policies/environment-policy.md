# Environment Policy

## Principle

The environment should be difficult because of the intended engineering problem, not because the author forgot to package dependencies or relied on a mutable host state.

## Required controls

- Pin base images and package versions where practical.
- Generate deterministic data with fixed seeds and record provenance/checksums.
- Set `network_mode` explicitly.
- Keep `/app` and any required services in a reproducible initial state.
- Use health checks when service readiness is part of the task.
- Measure CPU, memory, storage, and timeout requirements before release.
- Confirm that the baseline is unsolved before handing it to an agent.

## Prohibited shortcuts

Do not copy `solution/`, `tests/`, `private/`, `evidence/`, `.agents/`, `.claude/`, repository Git metadata, or local package caches into the solver image. Avoid image-layer history containing answer-generating commands or credentials.

## Compose and sidecars

Use Docker Compose only when a real multi-service dependency is a deliberate part of the task. When a sidecar holds trusted scoring evidence, collect it through Harbor sidecar artifacts or collect hooks and use a separate verifier for tamper-sensitive final grading.
