# tb-hard Studio 中文文档

[English](../../README.md) | [简体中文](README.md)

`tb-hard Studio` 是一个面向高难度终端 / Coding Agent 基准题的**内部出题工作台**。它不是题目执行容器，也不是被测 Agent 的提示词包；它负责把题目设计、环境搭建、标准解、独立验收、红队审查、真实 Agent 校准、采购格式导出固化成可复现流程。

> 英文规则文件仍是自动化和 Agent 的执行源；本目录用于中文阅读、培训与协作。

## 快速开始

```bash
uv tool install harbor
make doctor
make new CASE=<case_id>
make validate CASE=<case_id>
```

`make oracle` 和 `make rollouts` 需要本地 Harbor 与可用容器环境；结构检查、文档维护和静态校验可以先不安装 Harbor。

## 文档导航

| 目标 | 文档 | 适合场景 |
|---|---|---|
| 先跑起来 | [快速开始](quick-start.md) | 安装、初始化、第一条命令 |
| 看懂目录 | [架构与目录](architecture.md) | 仓库、case、私有资产和交付物如何隔离 |
| 对齐 Harbor/TB2 | [Harbor / Terminal-Bench 2 对齐](harbor-tb2-alignment.md) | 确认任务结构、reward、verifier 模式 |
| 按流程出题 | [出题全流程](authoring-workflow.md) | 从 Brief 到发布的状态机、角色和产物 |
| 使用 AI 协作 | [Skills 与 Subagents](skills-subagents.md) | Claude Code / Codex agents、Skills、写入边界 |
| 做质量审查 | [质量、反作弊与交付](quality-delivery.md) | Oracle、Verifier、红队、校准、采购包 |
| 看 CI 规则 | [CI 与 GitHub Actions](ci-actions.md) | 自动检查、手动导出和排错 |
| 系统学习 | [完整使用手册](tb-hard-studio-完整使用手册.md) | 培训、交接、日常操作速查 |

## 核心命令

```bash
make doctor
make materialize-skills
make new CASE=<case_id>
make validate CASE=<case_id>
make oracle CASE=<case_id>
make rollouts CASE=<case_id> AGENT=<agent> MODEL=<model> TRIALS=3
make export CASE=<case_id>
make release-check CASE=<case_id>
```

## Agent 资产位置

| 路径 | 用途 |
|---|---|
| `AGENTS.md` | Codex 和兼容 Agent 的仓库级执行规则 |
| `.claude/agents/` | Claude Code 项目级 Subagents |
| `.codex/agents/` | Codex 项目级 agents |
| `skills-core/` | 7 个核心 Skill 的唯一可编辑来源 |
| `.claude/skills/` | Claude Code Skill 投影 |
| `.agents/skills/` | Codex / 通用 Agent Skill 投影 |

这些资产只服务出题工作台，不得进入 `cases/<case_id>/task/environment/`、Solver 镜像或采购交付包。

## 术语速查

| 术语 | 含义 |
|---|---|
| Case | 一道稳定编号的基准题，目录为 `cases/<case_id>/`。 |
| Canonical Harbor task | 真实运行的任务源，固定在 `cases/<case_id>/task/`。 |
| Oracle | 标准解。它证明题目可解，但不等于评分器。 |
| Verifier | 独立验收逻辑，判断 Agent 是否真的完成任务。 |
| Rollout | 让指定 Agent / 模型实际跑题的过程。 |
| Calibration | 根据多次 rollout 的通过率、耗时、轨迹和失败原因校准难度。 |
| Private assets | 设计 Brief、内部审查、参考资料等，只能留在 `private/`。 |
| Purchaser export | 按采购方格式导出的交付包，不等于 Harbor 源目录。 |

## 推荐阅读顺序

1. [快速开始](quick-start.md)
2. [架构与目录](architecture.md)
3. [出题全流程](authoring-workflow.md)
4. [质量、反作弊与交付](quality-delivery.md)
5. [完整使用手册](tb-hard-studio-完整使用手册.md)
