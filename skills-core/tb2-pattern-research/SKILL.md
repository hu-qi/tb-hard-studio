---
name: tb2-pattern-research
description: Research Harbor and Terminal-Bench 2 patterns to design an original tb-hard task. Use before approving a design brief or when checking whether a candidate is too shallow or derivative.
argument-hint: "<case_id or topic>"
user-invocable: true
context: fork
agent: tb2-task-designer
model: sonnet
effort: high
allowed-tools: Read Glob Grep Bash
---

# TB2 Pattern Research

Research target: `$ARGUMENTS`

Use official Harbor documentation and the Terminal-Bench 2 repository as a pattern library only. Do not reproduce task wording, tests, solution code, hidden fixtures, or task assets.

For a case ID, write `cases/<case_id>/private/pattern-research.md`; otherwise return a self-contained memo. Include up to five relevant task patterns, hard elements, expected agent failure modes, originality constraints, asset/provenance risks, and a proceed/reshape/reject recommendation.

Reject a candidate when it is primarily service installation, a known linear recipe, obscured documentation lookup, slow setup, or a static-file exercise. Explain how the proposed case manifests at least three substantive difficulty dimensions in actual solver work.
