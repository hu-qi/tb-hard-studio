# tb-hard Procurement Interpretation

This document is a working interpretation of the supplied tb-hard procurement requirement. It is not a substitute for a signed statement of work.

## Task objective

Create high-difficulty, containerized programming benchmark tasks that fill the gap between routine synthetic coding exercises and Terminal-Bench 2 hard tasks.

## Target characteristics

- Expected success rate of roughly 30–60% for the agreed frontier-agent evaluation protocol.
- Meaningful iterative exploration, debugging, and implementation effort rather than a linear one-command setup.
- At least three approved difficulty dimensions per task.
- Expert-solvable, automatically verifiable, reproducible Docker environment.
- Deliverable must include public instruction, environment, tests, category/tag metadata, and agreed run configuration or export adapter.

## Known clarification risk

The source requirement asks for a batch of 10 tasks while also expressing broad per-category/per-language coverage. Treat language/category coverage as a batch-level optimization unless the purchaser explicitly defines an achievable coverage matrix. Record any updated clarification in `TASK-MATRIX.md`.

## Required confirmation before scale-up

1. Exact evaluation protocol for the 30–60% target: model versions, agent wrappers, number of attempts, timeouts, and aggregation method.
2. Required format for the “correct trajectory” evidence: raw logs, structured command traces, Harbor artifacts, or a reproducibility report.
3. Exact delivery adapter requirements if they differ from canonical Harbor task structure.
4. Whether reference solutions and hidden verifier assets are delivered separately, encrypted, or retained by the author until acceptance.
