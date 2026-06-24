# tb-hard Studio — Execution Guide

This private repository produces high-difficulty terminal benchmark tasks aligned with Harbor and Terminal-Bench 2 patterns. It is an **authoring workspace**, never a solver environment.

## Start here

Read these files before changing a task:

1. `docs/procurement-spec.md`
2. `docs/harbor-alignment.md`
3. `docs/quality-gates.md`
4. `docs/policies/verifier-security.md`
5. `docs/policies/calibration-protocol.md`
6. `TASK-MATRIX.md`

If they conflict, record the conflict in `cases/<case_id>/private/design-brief.md`. Do not silently choose an interpretation.

## Canonical case layout

Each task has one stable path. **Never move a case to express status.** Update `case.yaml` and `registry/tasks.csv` instead.

```text
cases/<case_id>/
├── case.yaml                  # Status, ownership, category, language, dimensions
├── private/                   # Authoring-only; never solver-visible or exported
│   ├── design-brief.md
│   ├── pattern-research.md
│   └── reviews/
├── task/                      # Canonical Harbor task tree
│   ├── instruction.md
│   ├── task.toml
│   ├── environment/
│   ├── solution/
│   └── tests/
└── exports/purchaser-v1/      # Generated manifests only; no hand edits
```

The canonical Harbor task is `cases/<case_id>/task/`. Harbor expects `instruction.md`, `task.toml`, `environment/`, optional `solution/`, and `tests/`; tb-hard requires a working Oracle even though Harbor makes `solution/` optional.

## Required commands

```bash
make doctor
make new CASE=<case_id>
make validate CASE=<case_id>
make oracle CASE=<case_id>
make rollouts CASE=<case_id> AGENT=<agent> MODEL=<model> TRIALS=3
make export CASE=<case_id>
make release-check CASE=<case_id>
```

`make validate` runs structural, isolation, and leakage checks. `make oracle` and `make rollouts` require a local Harbor installation and a container-capable environment.

## Non-negotiable rules

- A task must have at least three declared difficulty dimensions and observable acceptance criteria.
- Define verifier behavior before finalizing the environment.
- The Oracle proves solvability; it must not weaken the verifier or rely on hidden grader assets.
- `tests/test.sh` must always write `/logs/verifier/reward.txt` or `/logs/verifier/reward.json`, including on failure.
- Use a separate verifier when grading secrecy, tamper resistance, or sidecar evidence requires it.
- Solver-visible assets must not contain authoring prompts, design notes, reference solutions, hidden tests, credentials, trajectories, or calibration reports.
- A task is not hard merely because it is slow, ambiguous, flaky, or missing dependencies.
- Any substantive change to `task/` after calibration invalidates prior Oracle/calibration evidence.
- Never hand-edit `delivery/final/` or `exports/purchaser-v1/`; regenerate via scripts.

## Lifecycle and status

`draft` → `active` → `oracle-passed` → `redteam-passed` → `calibrated` → `validated` → `released`

The release gate requires: clean Oracle success, no unresolved red-team bypass, a calibration report, a leakage scan, and a deterministic purchaser export.

## Boundaries by role

- **Designer:** may write `private/` only.
- **Environment engineer:** may modify `task/environment/` and environment sections in `task.toml`.
- **Oracle engineer:** may modify `task/solution/` only.
- **Verifier reviewer:** may write `private/reviews/` only; never weaken tests.
- **Rollout analyst:** may write `evidence/<case_id>/` only.
- **Release auditor:** may write audit evidence/manifests only; never change task semantics.

Detailed policies live under `docs/policies/`. Keep this file short enough to be followed on every task.
