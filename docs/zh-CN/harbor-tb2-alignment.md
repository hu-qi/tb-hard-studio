# Harbor 与 Terminal-Bench 2 对齐

## 1. 对齐目标

本仓库不是 Harbor 或 Terminal-Bench 2 的 fork。它采用 Harbor 作为运行与评测底座，借鉴 Terminal-Bench 2 的真实任务形态、端到端验收思路和 Hard 难度标签方式，同时增加采购交付、红队和批量生产所需的工程约束。

## 2. Harbor 负责什么

Harbor 负责“把任务真正跑起来并得到可比较结果”：

- 从任务目录启动 Agent；
- 准备容器或其他环境提供方；
- 运行 Oracle 或指定 Agent；
- 执行 verifier；
- 采集 reward、日志、job/trial 和相关 artifacts。

因此任务运行的核心目录必须保持 Harbor 语义：

```text
instruction.md
task.toml
environment/
solution/
tests/
```

在本仓库里，它们统一位于 `cases/<case_id>/task/`。

## 3. TB2 提供什么参考

Terminal-Bench 2 的价值不在于复制题目，而在于学习任务结构：

- 题目来自真实工程、运维、调试、迁移或系统集成问题；
- 指令描述最终目标与边界，而不是给出逐步教程；
- 通过端到端行为验收，而不是检查某个文件是否存在；
- 任务可能跨多个服务、配置、工具或语言；
- Hard 是相对标签，不等同于“故意拖时长”或“环境很难装”。

## 4. tb-hard 的额外约束

相比一般 Harbor / TB2 任务，本仓库额外要求：

1. 每题至少声明 3 个难度维度。
2. 必须提供可运行 Oracle，即使底层框架把 `solution/` 视为可选。
3. 静态检查 Docker build context、私有资产和 solution 泄露。
4. 需要红队审查和 Agent rollout 校准证据。
5. 通过导出适配器生成采购方包，避免维护两套手写任务。

## 5. Reward 与 Verifier

Verifier 是验收权威，不是 Oracle 脚本的副本。

- `tests/test.sh` 必须在成功或失败时写入 `/logs/verifier/reward.txt` 或 `/logs/verifier/reward.json`。
- 单一成功/失败任务可使用 reward.txt；有多个可度量目标时，优先 reward.json。
- 只验证外部可观察行为：接口、文件内容、进程状态、数据库结果、部署结果、性能边界等。
- 不要强制某个实现语言、固定命令序列或目录内部结构，除非这本身就是题目约束。

## 6. 什么时候使用独立 Verifier

默认共享环境可以简化任务；但以下场景应评估独立 Verifier：

- 隐藏测试、答案或评分逻辑不能被 Solver 读取；
- Solver 可能篡改测试入口、日志或依赖；
- 需要从 sidecar 服务采集数据库、审计日志、计数器等证据；
- 安全、逆向、对抗性或高价值验收任务。

独立 Verifier 只应接收显式声明的 artifacts，避免隐式共享整个工作目录。
