---
name: harbor-task-create
description: Create or evolve a canonical Harbor task inside a stable tb-hard case directory. Use after the design brief names observable acceptance criteria and at least three difficulty dimensions.
argument-hint: "<case_id>"
user-invocable: true
model: inherit
effort: high
allowed-tools: Read Write Edit Glob Grep Bash
---

# Harbor Task Creation

Target case: `$ARGUMENTS`

1. Read `AGENTS.md`, `docs/harbor-alignment.md`, `docs/quality-gates.md`, and `cases/<case_id>/private/design-brief.md`.
2. Create the case first with `make new CASE=<case_id>` when it does not exist.
3. Keep all runnable benchmark assets under `cases/<case_id>/task/`; never create alternate task roots.
4. Define the verifier checklist before finalizing the environment. The public instruction must state goals, inputs, outputs, constraints, and measurable acceptance criteria without exposing tests or solution strategy.
5. Set an explicit Harbor network policy, timeouts, resources, and task metadata in `task/task.toml`.
6. Populate only solver-visible baseline assets in `task/environment/`. Keep solution and tests outside the environment image.
7. Create incomplete placeholders only when a follow-up Oracle or verifier role owns the next step; do not claim readiness.
8. Run `make validate CASE=<case_id>` and report failures honestly.

Stop and request design revision when acceptance is not observable, difficulty relies on ambiguity, the task is a linear installation recipe, or no credible Oracle path exists.

Return changed files, public contract summary, verifier checklist, environment decisions, and unresolved risks.
