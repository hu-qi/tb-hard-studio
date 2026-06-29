# Atomcode Implementation Guide

This guide is written for running `atomcode -y` in this repository. The goal is to implement the highest-value improvements identified in the current tb-hard Studio audit without changing unrelated task semantics.

## Context

Repository root:

```bash
/Users/huqi/Develop/gpdi/GPDI_AI/AIDataLabel/202606/tb-hard-studio
```

This repository is a private authoring workspace for Harbor / Terminal-Bench-style hard tasks. It is not a solver environment. Follow `AGENTS.md` and the policy docs before making changes.

Read these files first:

1. `AGENTS.md`
2. `docs/procurement-spec.md`
3. `docs/harbor-alignment.md`
4. `docs/quality-gates.md`
5. `docs/policies/verifier-security.md`
6. `docs/policies/calibration-protocol.md`
7. `TASK-MATRIX.md`

Do not move case directories to express status. Status belongs in `case.yaml` and `registry/tasks.csv`.

## Primary Objective

Make the repository quality gates usable and harder to bypass, then prepare the first case, `gitops-atomic-release`, for real implementation.

Prioritize the factory/tooling improvements before filling in the entire task environment.

## Required Working Style

- Make small, reviewable changes.
- Preserve existing project structure and conventions.
- Do not modify generated delivery artifacts by hand.
- Do not weaken verifier/security checks to make validation pass.
- Do not use `--no-verify`.
- Do not delete or revert unrelated user changes.
- If an issue fails three times, stop and document attempts, errors, and simpler alternatives.

For non-trivial code changes, create and maintain `IMPLEMENTATION_PLAN.md` using the staged format required by `AGENTS.md`. Remove it only after all stages are complete.

## Stage 1: Fix Local Validation Tooling

### Problem

`make validate-all` currently fails on macOS default Python:

```text
Python 3.9.6
ModuleNotFoundError: No module named 'tomllib'
```

The scripts import `tomllib`, which exists only in Python 3.11+.

### Goal

Make `make doctor` and `make validate-all` fail with a clear actionable message, or run successfully when a compatible Python is available.

### Preferred Implementation

Choose the simplest consistent approach:

1. If the project requires Python 3.11+, make that explicit and enforce it cleanly.
   - Add a clear version check before importing `tomllib`.
   - Update README / quick-start docs if needed.
   - Consider adding `.python-version` with `3.11` or `3.11.x` if consistent with the repo.

2. If compatibility is preferred, add a fallback:
   - Try `import tomllib`.
   - Fall back to `import tomli as tomllib`.
   - Ensure `doctor.sh` verifies that either Python 3.11+ or `tomli` is available.

Do not add a dependency manager unless there is already a project pattern for it.

### Acceptance

Run:

```bash
make doctor
make validate-all
```

Expected outcome:

- No Python traceback.
- If environment is unsupported, the error must be concise and actionable.
- If fallback compatibility is implemented, validation should proceed under Python 3.9 with `tomli` installed.

## Stage 2: Strengthen Status and Evidence Gates

### Problem

`validate_case.py` checks structure and metadata, but status advancement can still be claimed without sufficient evidence.

### Goal

Extend validation so case lifecycle statuses require matching evidence.

### Required Rules

Add checks in `scripts/validate_case.py` or a focused helper module:

- `oracle-passed` or later:
  - `oracle_status: passed`
  - At least one evidence directory under `evidence/<case_id>/oracle/`
  - An Oracle console/environment record exists.

- `redteam-passed` or later:
  - `redteam_status: passed`
  - `cases/<case_id>/private/reviews/redteam-report.md` exists.

- `calibrated` or later:
  - `calibration_status: passed`
  - `evidence/<case_id>/calibration/report.md` exists.
  - `evidence/<case_id>/calibration/aggregate.csv` exists.
  - `aggregate.csv` must not contain only `unknown` rewards.

- `validated` or `released`:
  - `release_status` must be `ready` or an equivalent repo-approved value before final release.
  - `task_revision` must not be `uncommitted`.
  - Oracle, red-team, and calibration statuses must all be `passed`.

Use warnings for draft/active states where evidence is not yet expected. Use errors when a status claims a later lifecycle gate.

### Acceptance

Run:

```bash
make validate CASE=gitops-atomic-release
make validate-all
```

Expected outcome for the current draft case:

- It may warn about placeholders.
- It should not require Oracle/red-team/calibration evidence while still `draft`.
- If status is manually advanced without evidence, validation must fail.

## Stage 3: Improve Rollout Evidence Collection

### Problem

`scripts/run_rollouts.sh` writes `reward=unknown` and asks humans to fill it in later. This makes calibration evidence incomplete and easy to forget.

### Goal

Automatically collect reward when Harbor writes a verifier reward file, or clearly mark the trial as evidence-incomplete.

### Suggested Implementation

After each Harbor run:

- Search the run log and common output/artifact paths for:
  - `reward.txt`
  - `reward.json`
  - `/logs/verifier/reward.txt`
  - `/logs/verifier/reward.json`
- If a numeric reward is found, write it to:
  - the trial `summary.md`
  - `aggregate.csv`
- If not found, write `missing` instead of `unknown`, and include a clear note in `summary.md`.

Keep this logic conservative. Do not parse arbitrary unrelated numbers as rewards.

### Acceptance

Run a dry or local test if Harbor is unavailable by adding unit-style coverage for the reward parser. If this repo has no test harness, add a small script-level test or documented manual test command.

Required commands:

```bash
make validate-all
```

If Harbor is installed:

```bash
make rollouts CASE=gitops-atomic-release AGENT=<agent> MODEL=<model> TRIALS=1
```

## Stage 4: Prepare `gitops-atomic-release` for Real Task Buildout

### Problem

The first case is currently a scaffold:

- `cases/gitops-atomic-release/task/instruction.md` is placeholder text.
- `cases/gitops-atomic-release/task/task.toml` has TODO/TBD fields.
- `cases/gitops-atomic-release/task/tests/test.sh` only writes `0` reward and exits failure.

### Goal

Create a minimal but coherent task specification and implementation plan for this case without pretending it is complete.

### Required Changes

Update only files that represent draft design/specification unless you are also building the environment end-to-end.

At minimum:

- Replace placeholder `instruction.md` with a solver-facing draft that states:
  - goal
  - available system/files
  - constraints
  - observable behavior
  - what counts as success
  - no Oracle or hidden verifier details

- Replace obvious TODO/TBD fields in `task.toml` with accurate draft metadata:
  - `[task].description`
  - `[task].authors`
  - `[task].keywords`
  - `[metadata].category`
  - `[metadata].difficulty_explanation`
  - `[metadata].tags`
  - expert/junior estimates

- Keep `case.yaml` status as `draft` unless a real runnable task, Oracle, verifier, and evidence exist.

- Document remaining implementation work in the private design brief or a new private implementation note.

### Verifier Direction

This case should strongly prefer a separate verifier because shared verifier tampering is credible.

If changing `task.toml`, consider:

```toml
[verifier]
environment_mode = "separate"
```

Only make this change if it is compatible with the current Harbor schema and planned artifact flow.

### Acceptance

Run:

```bash
make validate CASE=gitops-atomic-release
```

Expected outcome:

- No TODO/TBD errors in solver-visible files.
- Draft status is preserved.
- Missing runnable implementation may remain a warning if the repo policy allows draft warnings.

## Stage 5: Deterministic Export Check

### Problem

`export_purchaser.py` creates deterministic zip entries, but the manifest includes `generated_at_utc`, which changes on every run.

### Goal

Make deterministic export verification explicit.

### Suggested Implementation

Add a command or script that can export twice and compare archive hashes.

Possible target:

```bash
make export-check CASE=<case_id>
```

It should:

1. Run export into two temporary directories.
2. Compare purchaser zip SHA-256 values.
3. Report pass/fail.

Do not require a validated case unless the existing export path requires it. For draft review, use an explicit `--allow-unvalidated` path only if already supported.

### Acceptance

Run:

```bash
make export-check CASE=gitops-atomic-release
```

If the case is still draft, the command may explain that deterministic export requires a validated case, or may run with an explicit draft flag. Avoid silent success.

## Tests and Verification

At minimum, run:

```bash
make doctor
make validate-all
git status --short
```

If adding parser/helper code, add focused tests using the repository's existing style. If no test framework exists, prefer simple deterministic script tests over introducing a large new dependency.

Before finishing, report:

- Files changed.
- Commands run.
- Any commands that could not run and why.
- Remaining known risks.

## Out of Scope

Do not do these unless explicitly requested:

- Do not create all 10 planned tasks.
- Do not run expensive Harbor rollouts repeatedly.
- Do not mark any case as `validated` or `released` without evidence.
- Do not hand-edit `delivery/final/` or generated purchaser exports.
- Do not weaken leakage/isolation checks.
- Do not include private design notes, Oracle strategy, or solution content in solver-visible task files.

## Recommended First Command

```bash
atomcode -y "Read ATOMCODE_IMPLEMENTATION_GUIDE.md and implement Stage 1 and Stage 2 first. Keep changes small, run make doctor and make validate-all, then summarize remaining stages."
```
