# 架构与目录说明

## 1. 两层资产：生产资产与基准资产

仓库必须同时服务两个完全不同的对象：

- **出题者 / 审查者 / AI 辅助 Agent**：需要看到 Brief、参考资料、标准解、审查报告和校准记录。
- **被测 Agent**：只能看到题干和被允许操作的任务环境，不能看到答案、隐藏测试、作者提示或历史轨迹。

因此本仓库将资产划分为“内部生产资产”和“Canonical Harbor 任务源”。任何将两者混入 Docker build context 的做法，都会污染 benchmark。

## 2. 仓库顶层目录

| 路径 | 作用 | 是否可进入 Solver 环境 |
|---|---|---|
| `skills-core/` | 7 个核心 Skill 的唯一来源 | 否 |
| `.claude/agents/` | Claude Code Subagent 定义 | 否 |
| `.codex/agents/` | Codex 项目级 agents 定义 | 否 |
| `.claude/skills/`、`.agents/skills/` | 由 `sync_skills.py` 生成的 Skill 投影 | 否 |
| `docs/` | 制度、协议、对齐说明 | 否 |
| `templates/` | Brief 与审查模板 | 否 |
| `cases/` | 所有题目及其私有资产 | 仅 `cases/<id>/task/` 有条件可见 |
| `evidence/` | rollout、轨迹、校准、审查证据 | 否 |
| `scripts/` | 质量门禁、导出、运行封装 | 否 |
| `adapters/` | Harbor 源格式到采购格式的映射 | 否 |
| `delivery/` | 最终生成的交付物 | 仅采购方收到，不进 Solver |

## 3. 单题 Case 结构

```text
cases/<case_id>/
├── case.yaml
├── private/
│   ├── design-brief.md
│   ├── pattern-research.md
│   └── reviews/
├── task/
│   ├── instruction.md
│   ├── task.toml
│   ├── environment/
│   │   ├── Dockerfile
│   │   └── docker-compose.yaml      # 仅真实多服务任务需要时使用
│   ├── solution/
│   │   └── solve.sh
│   └── tests/
│       ├── test.sh
│       └── test_outputs.py
└── exports/
    └── purchaser-v1/
```

### `case.yaml`

内部元数据与状态机入口。至少应表达：

- `id`、标题、状态、负责人；
- 主领域、主语言；
- 至少 3 个难度维度；
- 网络策略、资源预期、Verifier 模式；
- Oracle / 红队 / 校准 / 发布等证据的索引。

### `private/`

只服务出题流程。内容可以包含原始需求、题型研究、候选方案、失败原因、评审意见，但绝不能写入任务镜像或导出包。

### `task/`

唯一的 canonical Harbor task。它是本地 Harbor 运行、Oracle、rollout 和导出的输入源。

### `exports/`

只存生成物和 manifest。手工改这里不会回写到任务源，下次导出会被覆盖。

## 4. 为什么状态不能靠移动文件夹表达

不要将 case 在 `draft/`、`active/`、`validated/` 之间移动：

- Harbor `-p` 路径会变化；
- rollout 证据、任务引用、CI artifact 会失效；
- 导出记录难以追溯；
- 多人协作时容易出现重复目录。

正确做法是保持 `cases/<case_id>/` 永久不变，只更新 `case.yaml` 和 `registry/tasks.csv`。
