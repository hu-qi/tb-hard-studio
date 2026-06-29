# 质量、反作弊与交付

## 1. 四道核心质量门

### 1. 静态结构门

```bash
make validate CASE=<case_id>
```

检查任务结构、`case.yaml`、难度维度、Docker 隔离、solution 泄露和导出约束。

### 2. Oracle 门

```bash
make oracle CASE=<case_id>
```

Oracle 证明任务可解。必须从干净环境取得完整 reward；不能依赖 hidden verifier 数据、手工预置文件或上一次运行缓存。

### 3. 红队门

重点不是发现普通 bug，而是模拟恶意或投机 Solver：

- 删除核心逻辑是否仍能通过？
- 只硬编码可见样例是否能通过？
- 修改启动脚本、测试入口或 PATH 是否能绕过？
- Docker layer、Git 历史、文件名、注释、日志是否泄露答案？
- 是否能重用缓存或持久化进程？
- 是否能通过网络、sidecar 或共享目录偷取评分信息？

任何已验证绕测都必须阻断发布。

### 4. Calibration 门

至少记录：

- Agent / 模型 / 版本 / 运行参数；
- trial 数、随机性或种子、时间预算；
- reward、成功状态、耗时、互动深度；
- 失败归因；
- 对题目继续强化、澄清、修复或淘汰的建议。

不能用单次失败代替校准结论。

## 2. Oracle 与 Verifier 的边界

| Oracle | Verifier |
|---|---|
| 证明存在正确解 | 判断当前 Agent 结果是否正确 |
| 可以知道推荐解法 | 不应依赖某一种实现 |
| 位于 `solution/` | 位于 `tests/` |
| 不应进入 Solver 可见环境 | 视模式决定是否对 Solver 隐藏 |

一个常见错误是让 tests 直接调用 `solution/solve.sh` 或检查其内部文件。这会让“验收”变成“是否复用了作者答案”。

## 3. Docker 隔离原则

最危险的写法：

```dockerfile
COPY . /app
```

这会把 `solution/`、`tests/`、私有文档甚至 Agent 提示一起带入 Solver 镜像。应只复制运行环境必需的公开文件，或在 build context 中明确排除私有资产。

## 4. 网络与依赖

- 默认不开放网络；确实需要网络时，应把网络访问本身写入题目设计和验收边界。
- 不要让题目的难度依赖临时下载、第三方服务稳定性或当前网页内容。
- 基础工具链与运行时可预置；不能预装只为直接解出题目的专用数据、答案库或完整破解工具。

## 5. 采购导出

```bash
make export CASE=<case_id>
make release-check CASE=<case_id>
```

导出器以 canonical Harbor task 为唯一来源，生成采购方要求的目录和 manifest。默认排除：

- `private/`；
- Oracle / 标准解；
- 隐藏评分逻辑（按双方交付协议决定是否单独提供）；
- Skills、Subagents、Codex agents、作者提示；
- rollout 轨迹、审查报告和内部证据；
- 凭证、密钥、缓存和构建临时文件。

最终交付前必须从生成包反向检查：它是否可解压、目录是否符合合同、是否缺少 required file、是否包含不应公开的资产。
