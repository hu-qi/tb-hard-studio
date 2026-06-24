# tb-hard Quality Gates

## Gate 0 — Case registration

A case has one stable `cases/<case_id>/` directory, a valid `case.yaml`, and a matching row in `registry/tasks.csv`.

## Gate 1 — Design

The private design brief defines a primary category/language, at least three difficulty dimensions, public contract, observable acceptance criteria, expert path, shortcut risks, and provenance.

## Gate 2 — Canonical Harbor structure

`task/` contains `instruction.md`, `task.toml`, `environment/`, `solution/solve.sh`, and `tests/test.sh`. The task uses current Harbor-compatible configuration and explicit network policy.

## Gate 3 — Oracle

A clean Harbor Oracle run earns full reward. The Oracle is a legitimate solution and does not read verifier-only assets or hardcode public samples.

## Gate 4 — Verifier security

Static isolation/leakage checks pass. Independent red-team review finds no unresolved bypass. Use separate verifier mode when shared-mode tampering remains credible.

## Gate 5 — Calibration

The frozen task is evaluated under the agreed Harbor protocol. Evidence distinguishes real technical difficulty from ambiguity, instability, infrastructure faults, and tooling mismatch.

## Gate 6 — Release

The final Oracle is rerun after content freeze. `make release-check` passes, purchaser export is deterministic, and the package contains only agreed public artifacts.
