# Design Brief — gitops-atomic-release

## Premise

Repair and complete a deliberately inconsistent local GitOps deployment system so that authenticated pushes trigger atomic static-site releases, failed releases roll back safely, concurrent pushes do not publish partial content, and deployment audit evidence survives service restart.

## Classification

- Primary category: 运维、网络与基础设施
- Primary language: Go
- Secondary technologies: Bash, Git, Nginx, Docker
- Difficulty dimensions: 跨域集成、多步依赖链、底层系统与权限、对抗性与可观测性

## Public contract

- Inputs: an existing bare Git repository, a partially broken deployment service, Nginx configuration, release metadata store, and integration tests generated at verification time.
- Required behavior: `git push` must publish a complete versioned release only after validation; a failed release must preserve the last known-good site; concurrent pushes must have deterministic ordering/locking; the deployment service must emit auditable records; the site must recover after relevant service restart.
- Constraints: operate entirely locally; do not remove validation, make deployment synchronous by sleeping, or bypass Git hooks/service boundaries; the solver may modify application, hook, service, and configuration files inside `/app`.
- Observable acceptance criteria: hidden verifier performs valid push, invalid push, concurrent push, restart recovery, rollback, and audit-integrity checks against HTTP behavior and an isolated service-side evidence artifact.

## Expected expert investigation path

An expert must inspect repository hooks, service users and permissions, Nginx root/symlink behavior, lock/transaction behavior, release metadata, process lifecycle, and failure ordering. The task should require iterative end-to-end debugging rather than a single configuration edit.

## Shortcut, leakage, and verifier risks

Potential shortcuts include serving a static canned page, deleting validation, modifying test wrappers, writing fake audit records, or exploiting shared verifier state. Plan for a separate verifier and sidecar/service-collected audit evidence. Keep test fixtures and expected release IDs private.

## Environment and calibration hypothesis

Use a local multi-service Docker environment only if the services are materially needed. The baseline should contain several interacting faults rather than one intentional typo. Target selected agent pass rate: 30–60% under the repository calibration protocol, with failed runs showing real investigation into hooks, locks, process lifecycle, permissions, and rollback semantics.

## Asset provenance and unresolved questions

All data can be generated locally; no external downloads are needed. Before implementation, decide whether the deployment orchestrator is provided as a partial Go service or must be reconstructed from system scripts, and define the exact trusted audit artifact for separate verification.
