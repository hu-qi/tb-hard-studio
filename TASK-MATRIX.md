# tb-hard Task Matrix

`registry/tasks.csv` is the machine-readable source for case registration and status consistency. This file is the human planning view.

## Batch planning rules

- The purchaser requests 10 tasks. Balance category and language coverage across the **batch**; do not promise every language in every category.
- Each case has one primary category and one primary language for reporting, even when the task is multi-language.
- Every case must declare at least three difficulty dimensions in `case.yaml` and demonstrate them in calibration evidence.
- A case status changes only after its required gate evidence exists; do not move its directory.

## Initial target portfolio

| Slot | Primary category | Primary language | Candidate shape | Intended dimensions |
|---|---|---:|---|---|
| 01 | 运维、网络与基础设施 | Bash / Git | GitOps atomic release and audit recovery | cross-domain, dependency chain, systems, adversarial |
| 02 | 编译器、解释器与语言设计 | Rust | constrained DSL interpreter or migration | language semantics, precision, creative constraints |
| 03 | 系统编程、工具链与底层机制 | C/C++ | ABI/ISA or toolchain recovery | low-level systems, precision, dependency chain |
| 04 | 密码学、安全与逆向工程 | Python / C | cryptanalytic or binary-analysis workflow | specialist knowledge, adversarial, precision |
| 05 | 数据工程、ETL 与分析 | Python | corruption-aware reconciliation pipeline | large data, constraints, multi-step chain |
| 06 | 数据库、查询与知识图谱 | Java | query/transaction performance repair | database internals, precision, debugging |
| 07 | 并行、分布式与高性能计算 | Go | deterministic concurrent recovery | concurrency, exactness, failure recovery |
| 08 | 应用开发与交互式系统 | TypeScript | stateful browser/service debugging | interactive system, cross-domain, hidden states |
| 09 | 机器学习、模型训练与推理 | Python | robust reproducible model behavior | uncertainty, performance, anti-shortcut |
| 10 | 图形学与多媒体处理 | C++ / JavaScript | reverse/precision rendering pipeline | reverse engineering, precision, performance |

## Case status ledger

Use `registry/tasks.csv` for the current ledger. Do not manually duplicate active case status here.
