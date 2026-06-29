#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from common import printable_issue, resolve_case

DIRECT_LEAK_PATTERNS = [
    re.compile(r"(?i)(?:^|[^a-z0-9_])solution/solve\.sh"),
    re.compile(r"(?i)(?:^|[^a-z0-9_])reference solution(?:$|[^a-z0-9_])"),
    re.compile(r"(?i)(?:^|[^a-z0-9_])oracle-only(?:$|[^a-z0-9_])"),
    re.compile(r"(?i)(?:^|[^a-z0-9_])authoring-only(?:$|[^a-z0-9_])"),
    re.compile(r"(?i)(?:^|[^a-z0-9_])design-brief(?:$|[^a-z0-9_])"),
    re.compile(r"(?i)(?:^|[^a-z0-9_])pattern-research(?:$|[^a-z0-9_])"),
    re.compile(r"(?:^|/)\.agents(?:/|$)"),
    re.compile(r"(?:^|/)\.claude(?:/|$)"),
    re.compile(r"(?:^|/)\.codex(?:/|$)"),
    re.compile(r"(?:^|/)private(?:/|$)"),
    re.compile(r"(?:^|/)evidence(?:/|$)"),
]
FORBIDDEN_NAMES = {"solution", "private", "evidence", ".agents", ".claude", ".codex", ".git"}


def text_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file() and path.stat().st_size <= 1_000_000:
            yield path


def normalize_line(line: str) -> str:
    return " ".join(line.strip().split())


def scan_case(case_dir: Path) -> list[tuple[str, Path, str]]:
    issues: list[tuple[str, Path, str]] = []
    task = case_dir / "task"
    solver_roots = [task / "instruction.md", task / "task.toml", task / "environment"]
    solution = task / "solution"

    solution_lines: set[str] = set()
    if solution.exists():
        for path in text_files(solution):
            for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
                norm = normalize_line(line)
                if len(norm) >= 80 and not norm.startswith("#"):
                    solution_lines.add(norm)

    for root in solver_roots:
        candidates = [root] if root.is_file() else list(text_files(root)) if root.exists() else []
        for path in candidates:
            rel_parts = set(path.relative_to(task).parts)
            forbidden = rel_parts & FORBIDDEN_NAMES
            if forbidden:
                issues.append(("ERROR", path, f"solver-visible path includes forbidden segment(s): {sorted(forbidden)}"))
            content = path.read_text(encoding="utf-8", errors="ignore")
            for number, line in enumerate(content.splitlines(), 1):
                clean = line.split("#", 1)[0] if path.name == "Dockerfile" else line
                if not clean.strip():
                    continue
                for pattern in DIRECT_LEAK_PATTERNS:
                    if pattern.search(clean):
                        issues.append(("ERROR", path, f"line {number}: direct authoring/solution reference: {clean.strip()[:160]}"))
                        break
                norm = normalize_line(clean)
                if norm in solution_lines:
                    issues.append(("ERROR", path, f"line {number}: matches a long Oracle solution line"))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan solver-visible task assets for common answer leakage.")
    parser.add_argument("--case", required=True)
    args = parser.parse_args()
    try:
        case_dir = resolve_case(args.case)
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    issues = scan_case(case_dir)
    for level, path, message in issues:
        print(printable_issue(level, path, message))
    if not issues:
        print(f"PASS: leakage scan: {case_dir.name}")
    return 1 if any(level == "ERROR" for level, _, _ in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
