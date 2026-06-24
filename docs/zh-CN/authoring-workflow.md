# 出题全流程

## 1. 状态机

```text
draft → active → oracle-passed → redteam-passed → calibrated → validated → released
```

状态不是“做了多少文件”，而是是否通过相应质量门。任何对 `task/` 的实质改动都会使之前的 Oracle、红队或 calibration 证据失效，应退回合适状态重新运行。

## 2. 每个阶段的输入、输出与退出条件

| 阶段 | 主要产物 | 退出条件 |
|---|---|---|
| `draft` | design brief、选题研究、初步风险 | 明确真实场景、验收目标、主语言、3+难度维度 |
| `active` | 初始任务目录、环境、题干、测试草案 | 环境可构建，题干与验收没有明显冲突 |
| `oracle-passed` | `solution/solve.sh`、Oracle 日志 | 从干净环境运行得到完整 reward |
| `redteam-passed` | 红队报告、修复记录 | 已验证常见绕测、泄露和篡改路径不可用 |
| `calibrated` | rollout 结果、失败归因、校准报告 | 难度来自真实推理与调试，不是歧义或环境故障 |
| `validated` | 完整证据索引、release-check 通过 | 所有质量门通过，元数据完整 |
| `released` | 采购导出包、manifest、交付记录 | 导出可复现且不包含内部资产 |

## 3. 从 Brief 开始，而不是从 Dockerfile 开始

一份合格 Brief 至少回答：

1. 真实工程问题是什么？为什么不是“安装几个包”即可解决？
2. Agent 最终要达到的外部成功状态是什么？
3. 至少三个难度维度分别是什么？
4. 哪些部分可能被硬编码、删除逻辑、修改测试或读取泄露资产绕过？
5. 专家可行的技术路径是什么？它不需要写成题干教程。
6. 哪些输入、数据、服务或时间因素需要固定，避免 flaky？

## 4. 角色分工

| 角色 | 可以写 | 不可以写 |
|---|---|---|
| Task designer | `private/` | 最终测试和环境实现 |
| Environment engineer | `task/environment/`、环境配置 | 难度目标、验收门槛 |
| Oracle engineer | `task/solution/` | 降低 verifier 要求 |
| Verifier reviewer | `private/reviews/` | 直接改弱测试 |
| Rollout analyst | `evidence/<case_id>/` | 为了提高通过率而删约束 |
| Release auditor | manifest、审计证据 | 改变任务语义 |

## 5. 推荐的最小迭代节奏

1. 设计 1 道 Pilot。
2. 先完成 Oracle 与独立测试，再考虑“难不难”。
3. 跑一次红队，优先修泄露和绕测。
4. 对目标 Agent 做 3 次以上 rollout。
5. 区分“Agent 不会”与“题目坏了”。
6. 固化模板、脚本和失败案例，再开始批量出题。

## 6. 如何判定难度有效

以下都不能单独证明题目 Hard：

- Agent 超时；
- 依赖下载慢；
- 题干模糊；
- Docker 构建失败；
- 隐藏了关键前提；
- 测试随机失败。

有效难度应来自可解释的技术工作：跨域排查、深度领域知识、精确边界、真实多步骤依赖、复杂状态恢复、对抗约束或大规模代码理解。
