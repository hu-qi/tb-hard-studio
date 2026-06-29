#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shlex
import sys
from pathlib import Path

from common import printable_issue, resolve_case

FORBIDDEN_SEGMENTS = {"solution", "private", "evidence", ".agents", ".claude", ".codex", ".git"}
SUSPICIOUS_COPY = {"solution", "tests", "private", "evidence", ".agents", ".claude", ".codex", ".git"}


def docker_copy_sources(line: str) -> list[str]:
    stripped = line.strip()
    if not re.match(r"^(COPY|ADD)\s+", stripped, flags=re.I):
        return []
    without_comment = stripped.split("#", 1)[0].strip()
    try:
        tokens = shlex.split(without_comment)
    except ValueError:
        return ["<unparseable>"]
    if len(tokens) < 3:
        return ["<unparseable>"]
    payload = [token for token in tokens[1:] if not token.startswith("--")]
    return payload[:-1] if len(payload) >= 2 else ["<unparseable>"]


def scan_case(case_dir: Path) -> list[tuple[str, Path, str]]:
    issues: list[tuple[str, Path, str]] = []
    task_dir = case_dir / "task"
    env_dir = task_dir / "environment"
    if not env_dir.exists():
        issues.append(("ERROR", env_dir, "missing environment directory"))
        return issues

    for file in env_dir.rglob("*"):
        if not file.is_file():
            continue
        parts = set(file.relative_to(env_dir).parts)
        bad = parts & FORBIDDEN_SEGMENTS
        if bad:
            issues.append(("ERROR", file, f"solver environment path contains forbidden segment(s): {sorted(bad)}"))

    dockerfiles = list(env_dir.rglob("Dockerfile")) + list((task_dir / "tests").rglob("Dockerfile")) if (task_dir / "tests").exists() else list(env_dir.rglob("Dockerfile"))
    for dockerfile in dockerfiles:
        for number, raw in enumerate(dockerfile.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            sources = docker_copy_sources(raw)
            for source in sources:
                lowered = source.lower()
                if source == ".":
                    issues.append(("ERROR", dockerfile, f"line {number}: ambiguous COPY/ADD '.' may include private task assets; use explicit sources"))
                if source.startswith("../") or "/../" in source:
                    issues.append(("ERROR", dockerfile, f"line {number}: COPY/ADD may escape the environment boundary: {source}"))
                for forbidden in SUSPICIOUS_COPY:
                    if forbidden in lowered.split("/") or f"/{forbidden}/" in f"/{lowered}/":
                        issues.append(("ERROR", dockerfile, f"line {number}: COPY/ADD references restricted source '{source}'"))
    return issues


def main() -> int:
    parser = argparse.ArgumentParser(description="Check solver-image isolation for one tb-hard case.")
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
        print(f"PASS: isolation scan: {case_dir.name}")
    return 1 if any(level == "ERROR" for level, _, _ in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
