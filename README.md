# tb-hard Studio

[English](README.md) | [简体中文](docs/zh-CN/README.md)

Private production workspace for high-difficulty terminal benchmark tasks aligned with [Harbor](https://www.harborframework.com/) and Terminal-Bench 2 task patterns.

This repository is an **authoring factory**, not a solver environment. It contains task design policies, reusable Skills, Claude Code/Codex project agents, validation scripts, evidence conventions, and a deterministic purchaser export adapter. None of the authoring assets belong in a solver-visible benchmark image.

## Highlights

- Stable case paths under `cases/<case_id>/`; lifecycle state lives in `case.yaml` and `registry/tasks.csv`.
- Canonical Harbor task source under `cases/<case_id>/task/`.
- Seven reusable Skills sourced from `skills-core/` and materialized to `.claude/skills/` and `.agents/skills/`.
- Six role-scoped Claude Code / Codex project agents with explicit write boundaries.
- Static quality gates for metadata, Harbor structure, Docker isolation, solution leakage, lifecycle evidence, and delivery checks.
- Harbor Oracle and rollout wrappers that preserve reproducible evidence.
- Harbor to purchaser-v1 export adapter that emits only `Dockerfile`, `instruction.md`, `test/`, and `tag.txt`.

## Quick Start

```bash
uv tool install harbor
make doctor
make new CASE=gitops-atomic-release
make validate CASE=gitops-atomic-release
```

`make oracle` and `make rollouts` require a working Harbor installation and Docker or another supported container environment. Structural checks and documentation work can run without Harbor.

## Documentation

| Topic | English | 简体中文 |
|---|---|---|
| Start here | [AGENTS.md](AGENTS.md) | [中文文档中心](docs/zh-CN/README.md) |
| Quick start | This README | [快速开始](docs/zh-CN/quick-start.md) |
| Documentation index | [English docs](docs/README.md) | [中文文档中心](docs/zh-CN/README.md) |
| Architecture | [Harbor alignment](docs/harbor-alignment.md) | [架构与目录](docs/zh-CN/architecture.md) |
| Workflow | [Quality gates](docs/quality-gates.md) | [出题全流程](docs/zh-CN/authoring-workflow.md) |
| Skills and agents | [SCAFFOLD_MANIFEST.json](SCAFFOLD_MANIFEST.json) | [Skills 与 Subagents](docs/zh-CN/skills-subagents.md) |
| Security and delivery | [Policies](docs/policies/) | [质量、反作弊与交付](docs/zh-CN/quality-delivery.md) |
| Full manual | Policy docs under `docs/` | [完整使用手册](docs/zh-CN/tb-hard-studio-完整使用手册.md) |

## Core Workflow

```bash
make new CASE=<case_id>
make validate CASE=<case_id>
make oracle CASE=<case_id>
make rollouts CASE=<case_id> AGENT=<agent> MODEL=<model> TRIALS=3
make export CASE=<case_id>
make release-check CASE=<case_id>
```

The wrappers retain commands and console logs under `evidence/<case_id>/`. Copy Harbor job/trial references and verifier artifacts there when your provider stores them elsewhere.

## Agent Assets

- `AGENTS.md`: repository-level execution rules for Codex and compatible agents.
- `.claude/agents/`: Claude Code project subagents.
- `.codex/agents/`: Codex project agents.
- `skills-core/`: editable source for project Skills.
- `.claude/skills/` and `.agents/skills/`: generated Skill projections. Run `make materialize-skills` after editing `skills-core/`.

These assets are private authoring aids. They must not be copied into solver images or purchaser exports.

## Case Layout

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
└── exports/purchaser-v1/      # generated manifests only
```

## Status

This is a private production workspace. Treat `docs/`, `AGENTS.md`, and `TASK-MATRIX.md` as the source of truth before changing task semantics or lifecycle status.
