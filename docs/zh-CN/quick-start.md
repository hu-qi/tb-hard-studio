# 快速开始

本指南帮助你从空白环境进入“可以新建并校验一道题”的状态。建议先完成 `gitops-atomic-release` Pilot，再扩展到其余题目。

## 1. 前置条件

| 工具 | 用途 | 是否必须 |
|---|---|---|
| Git | 版本管理与协作 | 必须 |
| Python 3.11+ | 执行仓库脚本 | 必须 |
| Make | 统一命令入口 | 必须 |
| Docker | 构建任务环境、运行 Harbor | 做 Oracle / rollout 时必须 |
| uv | 安装 Harbor 的推荐方式 | 推荐 |
| Harbor | 运行 Oracle 和 Agent rollout | 做真实评测时必须 |

安装 Harbor：

```bash
uv tool install harbor
```

确认环境：

```bash
make doctor
```

`make doctor` 会检查 Python、Git、Make、Harbor、Docker、Skill 投影一致性以及所有 case 的静态结构。Harbor 或 Docker 缺失时通常是警告；结构、泄露或元数据错误会导致失败。

## 2. 创建新题

case ID 采用小写 kebab-case，并尽量使用“领域-核心任务”的语义命名：

```bash
make new CASE=gitops-atomic-release
```

新 case 会生成固定目录：

```text
cases/gitops-atomic-release/
├── case.yaml
├── private/
│   └── design-brief.md
├── task/
│   ├── instruction.md
│   ├── task.toml
│   ├── environment/
│   ├── solution/
│   └── tests/
└── exports/purchaser-v1/
```

不要用移动目录表示进度。状态始终写入 `case.yaml`，并同步到 `registry/tasks.csv`。

## 3. 第一轮工作顺序

1. 在 `private/design-brief.md` 写清真实场景、主领域、主语言、至少 3 个难度维度、验收目标和潜在绕测。
2. 更新 `case.yaml`：状态、领域、语言、难度维度、负责人、网络策略等元数据。
3. 先定义“外部可观察的成功条件”，再写 Docker 环境。
4. 编写 `task/instruction.md`。题干只描述目标、输入输出、限制和验收边界；不要泄露实现路径。
5. 搭建 `task/environment/`，确保问题初始状态能稳定复现。
6. 编写 `task/solution/solve.sh`，证明专家可以完成任务。
7. 编写 `task/tests/`，让验收逻辑独立于标准解。
8. 运行静态检查：

```bash
make validate CASE=gitops-atomic-release
```

## 4. 执行 Oracle 与校准

当 Harbor 与 Docker 已就绪：

```bash
make oracle CASE=gitops-atomic-release
make rollouts CASE=gitops-atomic-release AGENT=<agent> MODEL=<model> TRIALS=3
```

Oracle 必须拿到完整 reward。不要在 Oracle 失败时先改测试放宽要求；先判断是环境、解法、题干还是 verifier 的问题。

## 5. 导出交付包

```bash
make export CASE=gitops-atomic-release
make release-check CASE=gitops-atomic-release
```

导出器会从 canonical Harbor task 生成采购方格式，默认排除 `private/`、标准解、轨迹、内部审查、Skills 和 Subagents。不要手工编辑 `exports/` 或 `delivery/` 下生成的文件。

## 常见错误

- **只完成 Dockerfile，没有 Oracle 或 verifier**：这不是可交付基准题。
- **把 tests 或 solution 复制进 Solver 镜像**：会泄题。
- **只用一轮 Agent 失败证明难题**：失败可能来自歧义、环境损坏或依赖缺失。
- **先写题干再补验收**：很容易导致目标与评分不一致。
