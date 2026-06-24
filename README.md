# tb-hard Studio

Private production workspace for high-difficulty terminal benchmark tasks aligned with [Harbor](https://www.harborframework.com/) and Terminal-Bench 2 task patterns.

This is an **authoring factory**, not a solver environment. It contains project instructions, reusable Skills, Claude Code Subagents, validation scripts, evidence conventions, and a deterministic purchaser export adapter. None of the authoring assets belong in a solver-visible benchmark image.

## What changed in v2

- Stable case paths: `cases/<case_id>/`; status lives in `case.yaml` and `registry/tasks.csv`.
- Canonical Harbor source: `cases/<case_id>/task/` only.
- Seven reusable Skills sourced from `skills-core/` and copied to `.claude/skills/` and `.agents/skills/` by `scripts/sync_skills.py`.
- Six Claude Code Subagents with explicit write boundaries.
- Static quality gates: structure, metadata, Docker isolation, solution-leak scanning, and delivery checks.
- Harbor Oracle/rollout wrapper scripts that preserve reproducible evidence.
- A Harbor → purchaser-v1 adapter that exports only `Dockerfile`, `instruction.md`, `test/`, and `tag.txt`.

## 中文文档

面向中文使用者的完整说明位于 [`docs/zh-CN/`](docs/zh-CN/README.md)：

- [快速开始](docs/zh-CN/quick-start.md)
- [架构与目录](docs/zh-CN/architecture.md)
- [Harbor / Terminal-Bench 2 对齐](docs/zh-CN/harbor-tb2-alignment.md)
- [出题全流程](docs/zh-CN/authoring-workflow.md)
- [Skills 与 Subagents](docs/zh-CN/skills-subagents.md)
- [质量、反作弊与交付](docs/zh-CN/quality-delivery.md)
- [CI 与 GitHub Actions](docs/zh-CN/ci-actions.md)

## First use

```bash
uv tool install harbor
make doctor
make new CASE=gitops-atomic-release
make validate CASE=gitops-atomic-release
```

For Claude Code, start in the repository root. Project Skills are in `.claude/skills/`; project Subagents are in `.claude/agents/`.

## Core workflow

```bash
make new CASE=<case_id>
make validate CASE=<case_id>
make oracle CASE=<case_id>
make rollouts CASE=<case_id> AGENT=<agent> MODEL=<model> TRIALS=3
make release-check CASE=<case_id>
```

`make oracle` and `make rollouts` require a working Harbor installation and Docker or another supported environment provider. The wrappers retain commands and console logs under `evidence/<case_id>/`; copy Harbor job/trial references and verifier artifacts there when your provider stores them elsewhere.

## Case layout

```text
cases/<case_id>/
├── case.yaml
├── private/                   # briefs, research, reviews; never exported
├── task/                      # canonical Harbor task
│   ├── instruction.md
│   ├── task.toml
│   ├── environment/
│   ├── solution/
│   └── tests/
└── exports/purchaser-v1/      # generated manifest only
```

Read `AGENTS.md` for execution rules and `docs/` for the detailed policies.
