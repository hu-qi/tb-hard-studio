# Skills 与 Subagents 使用指南

## 1. 为什么需要多 Agent 分工

高难基准题最容易出现“自证正确”问题：同一个 Agent 设计题目、写环境、写标准解、写测试、再宣布题目通过。这样通常会产生可被自身测试误判的浅题。

本仓库通过 Skills 复用流程，通过 Subagents 分隔权限与职责。AI 可以加速生产，但不能替代独立验证。

## 2. 7 个 Skills

| Skill | 何时使用 | 主要输出 |
|---|---|---|
| `harbor-task-create` | 新建任务或补齐骨架 | Harbor 目录、元数据、创建检查清单 |
| `tb2-pattern-research` | 研究同类真实任务形态 | 模式摘要、差异化建议、不可复制清单 |
| `harbor-environment-design` | 搭建初始问题环境 | Docker / Compose 设计、数据生成与隔离建议 |
| `harbor-oracle-verifier` | 编写标准解与验收 | Oracle 方案、Verifier 合同、reward 设计 |
| `harbor-redteam-verifier` | 查绕测、泄露与篡改 | 攻击路径、严重性、修复和复测建议 |
| `harbor-rollout-calibration` | 真实 Agent 跑题后分析 | 通过率、耗时、失败分类和难度建议 |
| `tb-hard-release-audit` | 准备发布或采购导出 | 交付清单、泄露检查、release 判定 |

Skill 的唯一源是 `skills-core/`。执行：

```bash
make materialize-skills
```

它会更新 `.claude/skills/` 与 `.agents/skills/` 投影。不要直接编辑生成目录，否则后续同步会覆盖修改。

## 3. 6 个 Subagents

| Subagent | 核心职责 | 写入边界 |
|---|---|---|
| `tb2-task-designer` | 设计 Brief 与难度结构 | `private/` |
| `harbor-env-engineer` | 初始环境、服务和数据 | `task/environment/` |
| `oracle-solution-engineer` | 标准解 | `task/solution/` |
| `verifier-security-reviewer` | 对抗审查 | `private/reviews/` |
| `harbor-rollout-analyst` | 运行结果与校准报告 | `evidence/<case_id>/` |
| `harbor-release-auditor` | 发布审计与 manifest | 审计证据与生成物 |

## 4. 推荐协作顺序

```text
Task designer
  → Environment engineer
  → Oracle solution engineer
  → Verifier security reviewer
  → Rollout analyst
  → Release auditor
```

请特别注意：Verifier reviewer 不能为了让 Oracle 通过而放宽测试；Rollout analyst 不能为了让模型通过而删掉真实约束；Release auditor 不能修改题目语义。

## 5. 与 Claude Code / Codex 的关系

- `.claude/agents/`：项目级 Claude Code Subagents。
- `.claude/skills/`：提供给 Claude Code 的 Skill 投影。
- `.agents/skills/`：通用 Agent / Codex 侧可使用的投影。
- `skills-core/`：唯一可编辑的核心来源。

这些资产只用于**出题工作台**。不得复制进 `cases/<case_id>/task/environment/`，也不得随采购包交付给被测 Agent。
