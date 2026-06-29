# CI 与 GitHub Actions

## 1. Authoring fast check

触发：推送到 `main` 或提交 PR 时自动运行。

检查内容：

- `make doctor`；
- Python / Git / Make 基础环境；
- Skill 投影是否同步；
- 所有 case 的静态结构、隔离和泄露检查；
- `.agents/skills/`、`.claude/skills/` 与 `.codex/agents/` 是否已提交最新结果。

它不运行 Docker、不执行真实 Agent，也不代表题目已经完成 Oracle 或 calibration。

### 失败处理

本地先复现：

```bash
make doctor
make materialize-skills
make validate-all
```

常见修复：

| 报错 | 通常原因 | 修复 |
|---|---|---|
| skill projections out of sync | 修改了 `skills-core/` 但没同步 | `make materialize-skills` 后提交生成目录 |
| case structural checks failed | 缺文件、元数据无效或泄露扫描命中 | 对照 `make validate CASE=<id>` 的详细输出修复 |
| Docker isolation failed | 可能 `COPY .` 或 build context 包含私有资产 | 缩小 Dockerfile 的 COPY 范围 |

## 2. Case export check

触发方式：在 GitHub Actions 页面手动运行，输入 `case_id`。

流程：

1. 执行 `make validate CASE=<case_id>`；
2. 执行 `make export CASE=<case_id>`；
3. 执行 `make release-check CASE=<case_id>`；
4. 上传生成的 purchaser-v1 zip 作为 artifact。

适合在准备发给采购方前使用。它验证的是“可导出、包结构正确”，不是完整 Oracle 或多模型 rollout。

## 3. 推荐的提交检查

| 改动类型 | 至少执行 |
|---|---|
| 修改 Skill / Subagent | `make materialize-skills && make doctor` |
| 修改 Brief 或 case.yaml | `make validate CASE=<id>` |
| 修改环境 / 题干 / solution / tests | `make validate CASE=<id> && make oracle CASE=<id>` |
| 修改 verifier | 加做红队复测和 rollout 校准 |
| 准备导出 | `make release-check CASE=<id>` + Case export check |

## 4. 不要把 CI 当成完整 benchmark

CI 擅长阻止低成本错误：目录缺失、格式错乱、Skill 漏同步、明显泄露、导出不完整。

真实难度仍要依赖 Harbor Oracle、独立 verifier、红队审查和多次 rollout。CI 通过只意味着“结构上可以继续”，不意味着“已经是一道合格 Hard 题”。
