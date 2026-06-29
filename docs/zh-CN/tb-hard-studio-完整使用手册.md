# tb-hard Studio 使用手册

本手册写给实际参与出题、审查、校准和交付的人看。读完你能独立跑完一道题从立项到发布的全过程，知道每一步该改什么文件、跑什么命令、踩哪些坑。

> 最后更新：2026-06-24　仓库版本：v2　语言：中文

---

## 目录

- [一、这个仓库在做什么](#一这个仓库在做什么)
- [二、核心思想](#二核心思想)
- [三、架构与目录](#三架构与目录)
- [四、一道题长什么样](#四一道题长什么样)
- [五、从零开始跑通一道题](#五从零开始跑通一道题)
- [六、状态机与质量门](#六状态机与质量门)
- [七、谁写什么：角色边界](#七谁写什么角色边界)
- [八、Skills 和 Subagents](#八skills-和-subagents)
- [九、Harbor 和 TB2 怎么对齐](#九harbor-和-tb2-怎么对齐)
- [十、环境怎么搭才不泄题](#十环境怎么搭才不泄题)
- [十一、Verifier 和反作弊](#十一verifier-和反作弊)
- [十二、校准：怎么证明题真的难](#十二校准怎么证明题真的难)
- [十三、导出采购包](#十三导出采购包)
- [十四、CI 自动检查](#十四ci-自动检查)
- [十五、命令速查](#十五命令速查)
- [十六、常见坑](#十六常见坑)
- [十七、十题规划](#十七十题规划)

---

## 一、这个仓库在做什么

我们要生产一批高难度的终端编程基准题，给前沿 AI Agent 做 benchmark 用。题目要满足：

- 在 Harbor 框架下能跑起来，形式对齐 Terminal-Bench 2 (TB2)；
- 通过率在 30%–60% 之间——不是送分题，也不是不可能完成的题；
- 每道题至少有 3 个真实的难度维度，不是靠慢、靠模糊、靠依赖装不上来"显得难"；
- 有标准解 (Oracle) 证明可解，有独立验收 (Verifier) 判断 Agent 是否真做对了；
- 最后能导出成采购方要的格式交付。

这个仓库是**出题工厂**，不是跑题环境。真正跑题的是 Harbor。我们不在这里评测 Agent，只生产题、验题、导出题。

---

## 二、核心思想

### 1. 一个源，一个包

`cases/<case_id>/task/` 是唯一能改的地方。采购方拿到的包是从它生成的，不要手改生成物。

### 2. 状态写在元数据里，别移动目录

题目进度用 `case.yaml` 和 `registry/tasks.csv` 表达，不要把目录从 `draft/` 移到 `active/`。路径一变，Harbor 引用、证据、CI artifact 全乱套。

### 3. Oracle ≠ Verifier

Oracle 是答案，证明题能做。Verifier 是判官，独立判断 Agent 的结果对不对。最忌讳让 tests 直接调用 solve.sh——那就变成"你抄了作者答案吗"，不是"你做对了吗"。

### 4. 难度要真

Agent 超时、依赖下载慢、题干写不清楚、Docker build 失败——这些都不叫难。真正的难来自跨域排查、深度领域知识、精确边界、多步依赖链、复杂状态恢复这类东西。

### 5. 私有资产不出库

设计 brief、标准解、审查报告、rollout 轨迹——这些永远不能进 Solver 能看到的镜像或采购包。一旦泄露，题就废了。

---

## 三、架构与目录

### 整体结构

```
tb-hard-studio/
│
├── skills-core/          ← 7 个 Skill 的唯一源（手动维护）
├── .claude/              ← Claude Code 用的 Subagent 和 Skill 投影（生成物）
├── .codex/agents/        ← Codex 项目级 agents
├── .agents/skills/       ← 给 Codex 等其他 Agent 用的 Skill 投影（生成物）
│
├── cases/                ← 所有题目，每题一个固定目录
│   ├── _template/        ← 新题模板，make new 时复制
│   └── gitops-atomic-release/  ← Pilot 题（运维 / Go）
│
├── docs/                 ← 规则文档（英文是执行源，中文供阅读）
│   ├── policies/         ← 四份核心政策
│   └ zh-CN/              ← 中文文档
│
├── scripts/              ← doctor / validate / export / oracle / rollout 等脚本
├── adapters/purchaser-v1/← Harbor 格式 → 采购格式的映射
├── delivery/final/       ← 最终交付包（禁止手改）
├── evidence/             ← rollout、校准、审查证据
├── registry/tasks.csv    ← 机器可读的题目台账
├── policy/               ← case schema 和泄露扫描规则
├── templates/            ← brief 和审查模板
├── tooling/              ← 版本和协议配置
├── Makefile              ← 所有命令入口
├── AGENTS.md             ← 执行规则（出题者必读）
└── TASK-MATRIX.md        ← 10 题规划表
```

### 资产隔离模型

这是整个仓库最重要的设计：出题者的东西和被测 Agent 能看到的东西必须物理隔离。

```
┌─────────────────────────────────┐    ┌──────────────────────────┐
│      出题工作台（本仓库）         │    │   被测 Agent 能看到的     │
│                                 │    │                          │
│  private/    brief、研究、审查   │    │  instruction.md  题干     │
│  solution/   Oracle 标准解       │    │  environment/    环境初始态│
│  evidence/   rollout 轨迹        │    │  （干净的、未解的初始态）  │
│  skills/     出题流程            │    │                          │
│  ───────────────────────────    │    │  看不到：                 │
│  task/       canonical 源        │───→│  solution/、tests/、      │
│  （唯一可编辑的题目源）           │    │  private/、evidence/、    │
│                                 │    │  skills/、作者提示        │
└─────────────────────────────────┘    └──────────────────────────┘
        ↓ export_purchaser.py                  ↑ Agent 在这里做题
┌─────────────────────────────────┐
│   delivery/final/  采购交付包    │
│   Dockerfile + instruction +    │
│   test/ + tag.txt               │
└─────────────────────────────────┘
```

关键原则：`task/` 是唯一可编辑源，采购包和 Harbor 运行都从它派生。`private/`、`evidence/`、`skills/` 永远不进 Solver 环境。

### 数据流：一道题从生到交付

```
  design-brief.md        task.toml + instruction.md
        │                          │
        │  设计阶段                 │  实现阶段
        ▼                          ▼
  ┌──────────┐              ┌──────────────┐
  │ private/ │──设计指导──→ │ task/        │
  │  brief   │              │  environment │← 环境工程师写
  │  research│              │  solution    │← Oracle 工程师写
  │  reviews │←──审查────── │  tests       │← Verifier 审查者写
  └──────────┘              └──────┬───────┘
                                   │
              ┌────────────────────┼────────────────────┐
              │                    │                    │
              ▼                    ▼                    ▼
        make validate         make oracle          make rollouts
        （静态检查）           （标准解跑通）       （Agent 跑题校准）
              │                    │                    │
              └────────────────────┼────────────────────┘
                                   │
                                   ▼
                          make export + release-check
                                   │
                                   ▼
                          delivery/final/*.zip
                          （交给采购方）
```

---

## 四、一道题长什么样

每个 case 固定住在 `cases/<case_id>/` 下，结构如下：

```
cases/gitops-atomic-release/
├── case.yaml                  ← 元数据：状态、领域、语言、难度维度、负责人
├── private/                   ← 出题者私有，永不导出
│   ├── design-brief.md        ← 设计简报：真实问题、验收标准、绕测风险
│   ├── pattern-research.md    ← 同类题研究
│   └── reviews/               ← 红队审查报告
├── task/                      ← canonical Harbor 任务（唯一可改的运行源）
│   ├── instruction.md         ← 题干：只写目标和边界，不写怎么做
│   ├── task.toml              ← Harbor 配置：超时、网络、verifier 模式
│   ├── environment/           ← Docker 环境
│   │   └── Dockerfile
│   ├── solution/              ← Oracle 标准解
│   │   └── solve.sh
│   └── tests/                 ← 验收脚本（独立于 solution）
│       ├── test.sh
│       └── test_outputs.py
└── exports/purchaser-v1/      ← 导出生成物（别手改）
```

`case.yaml` 是状态机入口，必填字段：

```yaml
case_id: gitops-atomic-release      # 小写 kebab-case
status: draft                       # draft→active→oracle-passed→...→released
version: 0.1.0                      # 语义版本
task_revision: uncommitted          # git commit hash，发布时固化
primary_category: 运维、网络与基础设施
primary_language: Go
secondary_technologies: [Bash, Git, Nginx, Docker]
difficulty_dimensions:              # 至少 3 个
  - 跨域集成
  - 多步依赖链
  - 底层系统与权限
  - 对抗性与可观测性
purchaser_tag: 运维、网络与基础设施-GitOps-原子发布
owner: huqi
oracle_status: not-run              # not-run / passed / failed
redteam_status: not-run
calibration_status: not-run
release_status: not-ready
```

---

## 五、从零开始跑通一道题

### 1. 装环境

| 要装的东西 | 干嘛用的 | 必须吗 |
|---|---|---|
| Git、Python 3.11+、Make | 基础工具 | 必须 |
| Docker | 构建环境、跑 Harbor | 跑 Oracle/rollout 时必须 |
| uv | 装 Harbor 的推荐方式 | 推荐 |
| Harbor | 跑题和评测 | 跑 Oracle/rollout 时必须 |

```bash
uv tool install harbor
make doctor          # 检查环境 + Skill 同步 + 所有 case 静态结构
```

`doctor` 里 Harbor 或 Docker 缺了只是警告；但结构、泄露、元数据错误会直接报失败。

### 2. 建题

```bash
make new CASE=gitops-atomic-release
```

从 `cases/_template/` 复制出骨架。别用移动目录表达进度，只改 `case.yaml` 和 `registry/tasks.csv`。

### 3. 按顺序干活

**先想清楚再写代码**，顺序很重要：

1. 写 `private/design-brief.md`——回答六个问题（见下方）
2. 更新 `case.yaml` 的领域、语言、难度维度、负责人
3. **先定验收标准**（外部可观察的成功条件），再搭环境
4. 写 `task/instruction.md`——只写目标、输入输出、限制，别泄露解法
5. 搭 `task/environment/`——确保初始状态能稳定复现
6. 写 `task/solution/solve.sh`——证明专家能做出来
7. 写 `task/tests/`——验收逻辑，别依赖 solution 的实现细节
8. `make validate CASE=<id>` 跑静态检查

### 4. 跑 Oracle 和校准

```bash
make oracle CASE=gitops-atomic-release
make rollouts CASE=gitops-atomic-release AGENT=<agent> MODEL=<model> TRIALS=3
```

Oracle 必须在干净环境拿到完整 reward。Oracle 挂了别急着改测试放宽——先判断是环境问题、解法问题、题干问题还是 verifier 问题。

### 5. 导出

```bash
make export CASE=gitops-atomic-release
make release-check CASE=gitops-atomic-release
```

导出器从 canonical task 生成采购包，默认排除 private、solution、evidence、skills 等。别手改 `exports/` 或 `delivery/`。

### Brief 要回答的六个问题

1. 真实工程问题是什么？为什么不是装几个包就能搞定？
2. Agent 最终要达到什么外部成功状态？
3. 至少三个难度维度分别是什么？
4. 哪些地方可能被硬编码、删逻辑、改测试、读泄露文件绕过？
5. 专家可行的技术路径是什么？（不用写成教程）
6. 哪些输入、数据、服务、时间因素要固定，防止 flaky？

---

## 六、状态机与质量门

### 状态流转

```
draft → active → oracle-passed → redteam-passed → calibrated → validated → released
                                                                  ↘ rejected
```

状态不是"你写了多少文件"，是"你过了哪个门"。只要动了 `task/` 里的实质内容，之前的 Oracle、红队、校准证据全部作废，得退回去重跑。

### 六道门

| 门 | 怎么过 | 退出条件 |
|---|---|---|
| Gate 0 注册 | 有稳定目录、有效 `case.yaml`、`tasks.csv` 对应行 | 目录和元数据齐全 |
| Gate 1 设计 | 人工评审 brief | 真实场景、验收目标、主语言、3+难度维度明确 |
| Gate 2 结构 | `make validate` | 文件齐全、Docker 隔离、无泄露 |
| Gate 3 Oracle | `make oracle` | 干净环境完整 reward，不靠 hidden 数据 |
| Gate 4 红队 | 红队审查 | 常见绕测、泄露、篡改路径全部阻断 |
| Gate 5 校准 | `make rollouts` + 分析 | 多次 rollout，难度来自真实技术工作 |
| Gate 6 发布 | `make release-check` | Oracle 重跑通过、导出确定性、包干净 |

---

## 七、谁写什么：角色边界

| 角色 | 能写 | 不能写 |
|---|---|---|
| 出题者 | `private/` | 测试和环境的最终实现 |
| 环境工程师 | `task/environment/` | 难度目标、验收门槛 |
| Oracle 工程师 | `task/solution/` | 降低 verifier 要求 |
| 验收审查者 | `private/reviews/` | 为了让 Oracle 过而改弱测试 |
| 校准分析师 | `evidence/<case_id>/` | 为提高通过率删约束 |
| 发布审计 | manifest、审计证据 | 改任务语义 |

推荐顺序：出题者 → 环境工程师 → Oracle 工程师 → 验收审查者 → 校准分析师 → 发布审计。

三条红线别碰：

- 审查者不能为让 Oracle 过而放宽测试；
- 分析师不能为让模型过而删真实约束；
- 审计不能改任务语义。

---

## 八、Skills 和 Subagents

### 为什么要分这么多 Agent

最怕"自证正确"：同一个 Agent 出题、写环境、写解法、写测试、再宣布通过——通常产出的是能被自己测试误判的浅题。用 Skills 复用流程，用 Subagents 分隔权限。

### 7 个 Skills

| Skill | 什么时候用 | 产出 |
|---|---|---|
| `harbor-task-create` | 新建任务或补骨架 | Harbor 目录、元数据、检查清单 |
| `tb2-pattern-research` | 研究同类真实任务 | 模式摘要、差异化建议、不可复制清单 |
| `harbor-environment-design` | 搭初始环境 | Docker/Compose 设计、隔离建议 |
| `harbor-oracle-verifier` | 写标准解和验收 | Oracle 方案、Verifier 合同、reward 设计 |
| `harbor-redteam-verifier` | 查绕测和泄露 | 攻击路径、严重性、修复建议 |
| `harbor-rollout-calibration` | Agent 跑完题后分析 | 通过率、耗时、失败分类、难度建议 |
| `tb-hard-release-audit` | 准备发布或导出 | 交付清单、泄露检查、release 判定 |

Skill 唯一源在 `skills-core/`。跑 `make materialize-skills` 会投影到 `.claude/skills/` 和 `.agents/skills/`。Codex 项目级 agents 放在 `.codex/agents/`。**别直接改 Skill 投影目录**，下次同步会覆盖。

### 6 个 Subagents

| Subagent | 干什么 | 写入边界 |
|---|---|---|
| `tb2-task-designer` | 设计 brief 和难度结构 | `private/` |
| `harbor-env-engineer` | 环境、服务、数据 | `task/environment/` |
| `oracle-solution-engineer` | 标准解 | `task/solution/` |
| `verifier-security-reviewer` | 对抗审查 | `private/reviews/` |
| `harbor-rollout-analyst` | 跑题结果和校准报告 | `evidence/<case_id>/` |
| `harbor-release-auditor` | 发布审计和 manifest | 审计证据与生成物 |

这些只用于出题工作台，**不能复制进任务环境或采购包**。

---

## 九、Harbor 和 TB2 怎么对齐

本仓库不是 Harbor 或 TB2 的 fork。Harbor 负责"把题跑起来拿结果"，TB2 提供真实任务形态的参考，我们额外加了采购交付、红队、批量生产的工程约束。

### Harbor 管的事

- 从任务目录启动 Agent；
- 准备容器环境；
- 运行 Oracle 或指定 Agent；
- 执行 verifier；
- 采集 reward、日志、job/trial、artifacts。

运行核心目录保持 Harbor 语义：`instruction.md` / `task.toml` / `environment/` / `solution/` / `tests/`，统一放在 `cases/<case_id>/task/`。

### task.toml 必填项

基线 schema 版本 `1.3`（见 `tooling/versions.env`），改之前先查 Harbor release notes。每题必须显式设：

- `[task]`：name（必须是 `tb-hard/<case_id>`）、description、authors、keywords
- `[metadata]`：category、difficulty_explanation、tags、human time estimates
- `[agent].timeout_sec`、`[verifier].timeout_sec`：必须是正数
- `[environment].network_mode`：`no-network` / `public` / `allowlist`
- `[verifier].environment_mode`：`shared`（默认）或 `separate`
- `artifacts`：独立 verifier 需要接收 solver 输出时声明

默认网络策略是 `no-network`。别为了装包方便改 `public`，要预 build 依赖或用白名单。

### Reward 合同

`tests/test.sh` 是 verifier 入口。**成功和失败两条路径都必须写 reward 文件**：

- 单一指标：写 `/logs/verifier/reward.txt`，一个数值；
- 多指标：写 `/logs/verifier/reward.json`。

测试要用绝对路径、验行为不验源码布局、在声明的资源/网络策略下确定性运行。

### 共享 vs 独立 Verifier

默认共享（solver 和 verifier 同一容器状态）。以下情况用独立 verifier（`environment_mode = "separate"`）：

- 隐藏测试/答案不能被 solver 读到；
- solver 可能篡改测试入口、日志、依赖；
- 要从 sidecar 采集数据库、审计日志等证据；
- 安全、逆向、对抗性任务。

独立 verifier 只接收显式声明的 artifacts，别隐式共享整个工作目录。

---

## 十、环境怎么搭才不泄题

### 原则

环境应该因为"工程问题本身难"而难，不是因为你忘了打包依赖或依赖宿主状态而难。

必须做的：

- 固定 base image 和包版本；
- 用固定种子生成数据，记录 checksum；
- 显式设 `network_mode`；
- `/app` 和服务保持可复现初始态；
- 服务就绪属任务一部分时加 health check；
- 发布前测 CPU/内存/存储/timeout；
- 确认 baseline 交给 Agent 前是未解状态。

### 最危险的写法

```dockerfile
COPY . /app
```

这会把 solution、tests、private、evidence、Agent 提示全塞进 solver 镜像。应该只 COPY 运行必需的公开文件。

### 禁止进 solver 镜像的东西

`solution/`、`tests/`、`private/`、`evidence/`、`.agents/`、`.claude/`、`.codex/`、`.git/`、本地包缓存。

---

## 十一、Verifier 和反作弊

### 威胁模型

假设 solver 能读改容器内一切、起持久进程、查文件名和镜像层、改启动脚本、硬编码样例、滥用共享验收状态。

### 红队必须尝试的攻击

1. 删掉或 stub 掉核心逻辑，看还能不能过；
2. 硬编码可见样例输出或解析公开测试；
3. 替换 entrypoint、wrapper、PATH、环境变量；
4. 翻 Docker layer、Git 历史、注释、shell history、缓存、挂载文件、残留进程；
5. 生成表面合法但没满足真实要求的 artifacts；
6. 滥用网络、service account、共享 volume、sidecar、可写 verifier state；
7. 共享模式下篡改测试脚本或评分依赖。

### 评分规则

- 验可观察行为、协议/状态正确性、输出正确性、可度量性能；
- 不要求特定源码布局或命令序列；
- 每个实质验收标准要有直接覆盖或文档化的复合测试；
- solver 产物一律视为不可信；
- 共享模式有可信攻击就切独立 verifier。

**任何能拿到 reward 却没完成真实任务的绕测都是 P0/P1，直接阻断发布。**

### 泄露扫描规则

`policy/leak-rules.yaml` 定义了禁止路径和禁止文本：

- 禁止路径片段：`/solution/`、`/private/`、`/evidence/`、`/.agents/`、`/.claude/`、`/.codex/`、`/.git/`
- 禁止文本模式：`solution`、`reference solution`、`oracle-only`、`hidden verifier`、`authoring-only`、`design-brief`、`pattern-research`、`calibration/report`
- 可疑 Docker COPY 源：`../`、`solution`、`tests`、`private`、`evidence`、`.agents`、`.claude`、`.codex`、`.git`

---

## 十二、校准：怎么证明题真的难

### 校准要证明什么

依据 `tooling/calibration-protocol.v1.yaml`：

- 题能被胜任专家通过公开合同解决；
- 难度来自实质性技术原因；
- 重复跑稳定；
- 没有捷径或泄露让题变简单；
- 在选定 Agent 上达到约定的通过率/时间/轨迹目标。

### 执行参数基线

| 参数 | 值 |
|---|---|
| Harbor 最低版本 | 0.15.0 |
| task schema 版本 | 1.3 |
| 环境提供方 | docker |
| 并发 | 1 |
| 网络策略 | 继承任务设置 |
| 默认超时 | 120 分钟 |
| 每 agent/model 默认 trial 数 | 3 |
| 聚合方式 | trial 均值 |
| 目标通过率 | 30%–60% |
| 决策前最少 trial 数 | 3 |

### 每次 rollout 要记录

task_revision、harbor_version、agent、agent_version、model、model_configuration、command、timeout_sec、network_policy、start_time、end_time、wall_clock_sec、reward、job/trial_reference、artifact_log_location。

### 必须产出的分析

通过率、耗时分布、超时率、轨迹深度观察、失败分类、难度维度证据、校准结论。

### 失败分类法

每次失败归入一类或多类：

1. 技术推理错误
2. 部分实现但有真实缺陷
3. 调研/搜索失败
4. 真实超时
5. 人为时间黑洞（非真实超时）
6. 题干歧义
7. 环境/搭建失败
8. verifier 缺陷
9. 答案泄露或捷径
10. 与目标能力无关的 Agent-工具不兼容

**只有 1 和 4 支持难度主张。光看通过率低不能说明题难。**

### 证据目录

```
evidence/<case_id>/
├── oracle/<run_id>/
├── redteam/
├── calibration/
│   ├── aggregate.csv
│   ├── report.md
│   └── runs/<run_id>/
└── release/
```

原始轨迹含专有提示/模型输出，保持私有；除非采购方明确要，只导出脱敏摘要。

### 怎么判断难度有效

以下都不能单独证明题难：

- Agent 超时
- 依赖下载慢
- 题干模糊
- Docker 构建失败
- 藏了关键前提
- 测试随机失败

有效难度来自：跨域排查、深度领域知识、精确边界、真实多步依赖、复杂状态恢复、对抗约束、大规模代码理解。

---

## 十三、导出采购包

### 唯一源

`cases/<case_id>/task/` 是唯一可编辑源，所有采购交付物从它生成。

### 生成命令

```bash
make export CASE=<case_id>
make release-check CASE=<case_id>
```

### 采购包结构

生成的 zip 里是一个 `<case_id>/` 根目录：

```
<case_id>/
├── Dockerfile
├── instruction.md
├── tag.txt
└── test/
```

### Harbor → 采购格式映射

| Harbor 源 | 采购包 |
|---|---|
| `task/environment/Dockerfile` | `Dockerfile` |
| `task/instruction.md` | `instruction.md` |
| `task/tests/` | `test/` |
| `case.yaml.purchaser_tag` | `tag.txt` |
| `task/solution/` | 排除 |

### 排除清单

solution、Oracle 私有 helper、Skills、Subagents、Codex agents、插件配置、文档、模板、brief、reviews、轨迹、校准报告、凭证、缓存、Git 元数据。

sidecar manifest 保留在包外，记录 task checksum、导出文件、排除路径、构建时间戳、脚本版本。

### 冻结规则

只在状态为 `validated` 后跑 `release-check`。生成后别手改包；改了任务就要重跑 Oracle、定向校准、审计、导出。

---

## 十四、CI 自动检查

### Authoring fast check

推 `main` 或提 PR 时自动跑。检查内容：`make doctor`、基础环境、Skill 投影同步、所有 case 静态结构/隔离/泄露、`.agents/skills/`、`.claude/skills/` 和 `.codex/agents/` 是否提交了最新生成结果。

不跑 Docker、不执行真实 Agent、不代表题已完成 Oracle 或校准。

### 失败了怎么办

本地先复现：

```bash
make doctor
make materialize-skills
make validate-all
```

| 报错 | 原因 | 修法 |
|---|---|---|
| skill projections out of sync | 改了 `skills-core/` 没同步 | `make materialize-skills` 后提交生成目录 |
| case structural checks failed | 缺文件、元数据无效或泄露命中 | 对照 `make validate CASE=<id>` 输出修 |
| Docker isolation failed | `COPY .` 或 build context 含私有资产 | 缩小 COPY 范围 |

### Case export check

GitHub Actions 页面手动触发，输入 case_id。流程：validate → export → release-check → 上传 zip artifact。适合交付前验证"能导出、包结构对"。

### 按改动类型的最小检查

| 改了什么 | 至少跑 |
|---|---|
| Skill / Subagent | `make materialize-skills && make doctor` |
| Brief 或 case.yaml | `make validate CASE=<id>` |
| 环境/题干/solution/tests | `make validate CASE=<id> && make oracle CASE=<id>` |
| verifier | 加红队复测 + rollout 校准 |
| 准备导出 | `make release-check CASE=<id>` + Case export check |

CI 只挡低成本错误（缺文件、格式错、Skill 漏同步、明显泄露、导出不完整）。**CI 过不代表题合格，真难度靠 Oracle、红队、多次 rollout。**

---

## 十五、命令速查

```bash
# 基础
make doctor                              # 环境健康检查
make materialize-skills                  # 同步 skills-core → .claude/skills 与 .agents/skills

# 出题
make new CASE=<case_id>                  # 从模板建题
make validate CASE=<case_id>             # 静态结构+隔离+泄露检查（--deep）
make validate-all                        # 所有 case 静态检查

# 评测（需 Harbor + Docker）
make oracle CASE=<case_id>               # 跑标准解
make rollouts CASE=<case_id> AGENT=<agent> MODEL=<model> TRIALS=3  # 校准跑题

# 交付
make export CASE=<case_id>               # 生成采购包
make release-check CASE=<case_id>        # 发布前完整检查
```

最小闭环：

```bash
make doctor
make new CASE=<case_id>
make validate CASE=<case_id>
make oracle CASE=<case_id>
make rollouts CASE=<case_id> AGENT=<agent> MODEL=<model> TRIALS=3
make export CASE=<case_id>
make release-check CASE=<case_id>
```

---

## 十六、常见坑

| 坑 | 后果 | 怎么避 |
|---|---|---|
| 只写了 Dockerfile，没 Oracle 或 verifier | 不是可交付基准题 | 补齐 `solution/solve.sh` 和 `tests/test.sh` |
| `COPY . /app` 把 solution/tests 带进 solver 镜像 | 泄题 | 只 COPY 运行必需的公开文件 |
| 跑一轮 Agent 失败就说题难 | 可能是歧义/环境坏/依赖缺 | 至少 3 次 rollout，按失败分类法归因 |
| 先写题干再补验收 | 目标和评分对不上 | 先定外部可观察成功条件，再写环境 |
| Oracle 挂了先改测试放宽 | 验收变成"抄没抄答案" | 先排查环境/解法/题干/verifier 哪个有问题 |
| 手改 `exports/` 或 `delivery/` | 下次导出被覆盖 | 只改 canonical task，重新生成 |
| 移动 case 目录表示进度 | Harbor 路径失效、证据失溯 | 只改 `case.yaml` 和 `registry/tasks.csv` |
| 让 tests 直接调 solve.sh | 验收失去独立性 | tests 验行为，不验实现 |

---

## 十七、十题规划

采购方要 10 道题。在批次层面平衡领域和语言覆盖，不要求每题覆盖所有语言。每题 1 个主领域 + 1 个主语言，至少 3 个难度维度。

| # | 主领域 | 主语言 | 候选形态 | 难度维度 |
|---|---|---:|---|---|
| 01 | 运维、网络与基础设施 | Go / Bash | GitOps 原子发布与审计恢复 | 跨域、依赖链、系统、对抗 |
| 02 | 编译器、解释器与语言设计 | Rust | 受限 DSL 解释器或迁移 | 语言语义、精度、创造性约束 |
| 03 | 系统编程、工具链与底层 | C/C++ | ABI/ISA 或工具链恢复 | 底层系统、精度、依赖链 |
| 04 | 密码学、安全与逆向 | Python / C | 密码分析或二进制分析 | 专有知识、对抗、精度 |
| 05 | 数据工程、ETL | Python | 容错对账流水线 | 大数据、约束、多步链 |
| 06 | 数据库、查询与知识图谱 | Java | 查询/事务性能修复 | 数据库内核、精度、调试 |
| 07 | 并行、分布式、HPC | Go | 确定性并发恢复 | 并发、精确性、故障恢复 |
| 08 | 应用开发与交互系统 | TypeScript | 有状态浏览器/服务调试 | 交互系统、跨域、隐藏状态 |
| 09 | 机器学习、训练与推理 | Python | 鲁棒可复现模型行为 | 不确定性、性能、反捷径 |
| 10 | 图形学与多媒体 | C++ / JS | 逆向/精度渲染流水线 | 逆向、精度、性能 |

当前台账看 `registry/tasks.csv`，别在 `TASK-MATRIX.md` 手工重复活动状态。

### Pilot 案例

`gitops-atomic-release`（运维 / Go）已在仓库中，状态 `draft`，Oracle/红队/校准均未跑。

---

## 附录：关键文件在哪

| 要找什么 | 去哪看 |
|---|---|
| 执行规则 | `AGENTS.md` |
| 采购需求解读 | `docs/procurement-spec.md` |
| Harbor 对齐规范 | `docs/harbor-alignment.md` |
| 质量门定义 | `docs/quality-gates.md` |
| 轨迹证据规范 | `docs/trajectory-protocol.md` |
| Verifier 安全策略 | `docs/policies/verifier-security.md` |
| 校准协议 | `docs/policies/calibration-protocol.md` + `tooling/calibration-protocol.v1.yaml` |
| 环境策略 | `docs/policies/environment-policy.md` |
| 交付契约 | `docs/policies/delivery-contract.md` |
| case schema | `policy/case.schema.json` |
| 泄露扫描规则 | `policy/leak-rules.yaml` |
| 采购适配器映射 | `adapters/purchaser-v1/mapping.yaml` |
| Brief 模板 | `templates/task-design-brief.md` |
| 审查模板 | `templates/task-review.md` |
