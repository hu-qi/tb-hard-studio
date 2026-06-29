# 中文文档中心

`tb-hard Studio` 是一个面向高难度终端 / Coding Agent 基准题的**内部出题工作台**。它不是题目执行容器，也不是被测 Agent 的提示词包；它负责把“题目设计、环境搭建、标准解、独立验收、红队审查、真实 Agent 校准、采购格式导出”固化成可复现流程。

> 英文规则文件仍是自动化和 Agent 的执行源；本目录用于中文阅读、培训与协作。

## 推荐阅读顺序

1. [快速开始](quick-start.md)：安装、初始化、第一条命令。
2. [架构与目录](architecture.md)：仓库、case、私有资产和交付物如何隔离。
3. [Harbor / Terminal-Bench 2 对齐](harbor-tb2-alignment.md)：什么内容必须沿用 Harbor 任务约定，什么属于本仓库扩展。
4. [出题全流程](authoring-workflow.md)：从 Brief 到发布的状态机、角色和产物。
5. [Skills 与 Subagents](skills-subagents.md)：如何让 AI 协作出题而不自证正确。
6. [质量、反作弊与交付](quality-delivery.md)：Oracle、Verifier、红队、校准、采购包。
7. [CI 与 GitHub Actions](ci-actions.md)：自动检查、手动导出和排错。
8. [完整使用手册](tb-hard-studio-完整使用手册.md)：面向培训和日常操作的一站式长文档。

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

## 最小闭环

```bash
make doctor
make new CASE=<case_id>
make validate CASE=<case_id>
make oracle CASE=<case_id>
make rollouts CASE=<case_id> AGENT=<agent> MODEL=<model> TRIALS=3
make export CASE=<case_id>
make release-check CASE=<case_id>
```

其中 `make oracle` 与 `make rollouts` 依赖本地 Harbor 和可用容器环境；其余命令可用于结构、隔离和导出检查。
