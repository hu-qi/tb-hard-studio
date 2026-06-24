#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import subprocess
import sys
import tomllib
from pathlib import Path
from typing import Any

from common import CASE_ID_RE, STATUSES, printable_issue, read_registry, repo_root, resolve_case, parse_simple_yaml

ROOT = repo_root()
REQUIRED_CASE_FIELDS = {
    "case_id", "status", "version", "task_revision", "primary_category", "primary_language",
    "difficulty_dimensions", "purchaser_tag", "owner", "oracle_status", "redteam_status",
    "calibration_status", "release_status",
}
REQUIRED_TASK_FILES = [
    "instruction.md",
    "task.toml",
    "environment/Dockerfile",
    "solution/solve.sh",
    "tests/test.sh",
]
STATUS_ORDER = {"draft": 0, "active": 1, "oracle-passed": 2, "redteam-passed": 3, "calibrated": 4, "validated": 5, "released": 6, "rejected": -1}


def issue(issues: list[tuple[str, Path, str]], level: str, path: Path, msg: str) -> None:
    issues.append((level, path, msg))


def task_word_count(instruction: Path) -> int:
    return len(re.findall(r"\S+", instruction.read_text(encoding="utf-8", errors="ignore")))


def validate_case(case_dir: Path, strict: bool = False, deep: bool = False) -> list[tuple[str, Path, str]]:
    issues: list[tuple[str, Path, str]] = []
    metadata_path = case_dir / "case.yaml"
    if not metadata_path.exists():
        issue(issues, "ERROR", metadata_path, "missing case metadata")
        return issues
    try:
        data = parse_simple_yaml(metadata_path)
    except Exception as exc:
        issue(issues, "ERROR", metadata_path, f"invalid supported YAML subset: {exc}")
        return issues

    missing = sorted(REQUIRED_CASE_FIELDS - data.keys())
    if missing:
        issue(issues, "ERROR", metadata_path, f"missing required field(s): {', '.join(missing)}")
    case_id = str(data.get("case_id", ""))
    if not CASE_ID_RE.match(case_id):
        issue(issues, "ERROR", metadata_path, "case_id must match ^[a-z0-9][a-z0-9-]{2,63}$")
    if case_id and case_id != case_dir.name:
        issue(issues, "ERROR", metadata_path, f"case_id '{case_id}' does not match directory '{case_dir.name}'")
    status = str(data.get("status", ""))
    if status not in STATUSES:
        issue(issues, "ERROR", metadata_path, f"unsupported status '{status}'")

    dims = data.get("difficulty_dimensions", [])
    if not isinstance(dims, list):
        issue(issues, "ERROR", metadata_path, "difficulty_dimensions must be a YAML list")
    elif len([d for d in dims if str(d).strip()]) < 3:
        level = "ERROR" if strict or STATUS_ORDER.get(status, 0) >= STATUS_ORDER["active"] else "WARN"
        issue(issues, level, metadata_path, "declare at least three non-empty difficulty dimensions")

    for key in ("primary_category", "primary_language", "purchaser_tag", "owner"):
        value = str(data.get(key, "")).strip()
        if value in {"", "TBD"}:
            level = "ERROR" if strict or STATUS_ORDER.get(status, 0) >= STATUS_ORDER["active"] else "WARN"
            issue(issues, level, metadata_path, f"field '{key}' must be set before active status")

    matching_rows = [row for row in read_registry() if row.get("case_id") == case_id]
    if len(matching_rows) != 1:
        issue(issues, "ERROR", ROOT / "registry/tasks.csv", f"expected exactly one registry row for case '{case_id}', found {len(matching_rows)}")
    else:
        row = matching_rows[0]
        for field in ("status", "version", "primary_category", "primary_language", "owner"):
            if row.get(field, "") != str(data.get(field, "")):
                issue(issues, "ERROR", ROOT / "registry/tasks.csv", f"registry {field} differs from case.yaml")

    task = case_dir / "task"
    for rel in REQUIRED_TASK_FILES:
        path = task / rel
        if not path.exists():
            level = "ERROR" if strict or STATUS_ORDER.get(status, 0) >= STATUS_ORDER["active"] else "WARN"
            issue(issues, level, path, "required canonical Harbor file missing")

    toml_path = task / "task.toml"
    config: dict[str, Any] = {}
    if toml_path.exists():
        try:
            config = tomllib.loads(toml_path.read_text(encoding="utf-8"))
        except Exception as exc:
            issue(issues, "ERROR", toml_path, f"TOML parse failed: {exc}")
        else:
            if str(config.get("schema_version", "")) != "1.3":
                issue(issues, "WARN", toml_path, "schema_version is not repository baseline 1.3; verify installed Harbor compatibility")
            task_table = config.get("task", {})
            env = config.get("environment", {})
            agent = config.get("agent", {})
            verifier = config.get("verifier", {})
            if task_table.get("name") != f"tb-hard/{case_id}":
                issue(issues, "ERROR", toml_path, f"[task].name must equal tb-hard/{case_id}")
            for key in ("description", "authors", "keywords"):
                if not task_table.get(key):
                    level = "ERROR" if strict or STATUS_ORDER.get(status, 0) >= STATUS_ORDER["active"] else "WARN"
                    issue(issues, level, toml_path, f"[task].{key} is required before active status")
            if env.get("network_mode") not in {"no-network", "public", "allowlist"}:
                issue(issues, "ERROR", toml_path, "[environment].network_mode must be no-network, public, or allowlist")
            for table_name, table in (("agent", agent), ("verifier", verifier)):
                timeout = table.get("timeout_sec")
                if not isinstance(timeout, (int, float)) or timeout <= 0:
                    issue(issues, "ERROR", toml_path, f"[{table_name}].timeout_sec must be a positive number")
            mode = verifier.get("environment_mode", "shared")
            if mode not in {"shared", "separate"}:
                issue(issues, "ERROR", toml_path, "[verifier].environment_mode must be shared or separate")
            metadata = config.get("metadata", {})
            for key in ("category", "difficulty_explanation"):
                if not metadata.get(key):
                    level = "ERROR" if strict or STATUS_ORDER.get(status, 0) >= STATUS_ORDER["active"] else "WARN"
                    issue(issues, level, toml_path, f"[metadata].{key} is required before active status")

    instruction = task / "instruction.md"
    if instruction.exists():
        count = task_word_count(instruction)
        if STATUS_ORDER.get(status, 0) >= STATUS_ORDER["active"] and not (150 <= count <= 500):
            issue(issues, "ERROR", instruction, f"instruction has {count} words; procurement target is 150–500")
        elif status == "draft" and count < 150:
            issue(issues, "WARN", instruction, f"instruction has {count} words; still a draft placeholder or too short")
        if "TODO:" in instruction.read_text(encoding="utf-8", errors="ignore"):
            level = "ERROR" if strict or STATUS_ORDER.get(status, 0) >= STATUS_ORDER["active"] else "WARN"
            issue(issues, level, instruction, "contains TODO placeholder")

    for rel in ("environment/Dockerfile", "solution/solve.sh", "tests/test.sh"):
        path = task / rel
        if path.exists() and "TODO:" in path.read_text(encoding="utf-8", errors="ignore"):
            level = "ERROR" if strict or STATUS_ORDER.get(status, 0) >= STATUS_ORDER["active"] else "WARN"
            issue(issues, level, path, "contains TODO placeholder")

    test_script = task / "tests/test.sh"
    if test_script.exists():
        content = test_script.read_text(encoding="utf-8", errors="ignore")
        if "/logs/verifier/reward.txt" not in content and "/logs/verifier/reward.json" not in content:
            issue(issues, "ERROR", test_script, "must write a Harbor reward file")

    if deep and task.exists():
        from check_task_isolation import scan_case as isolation_scan
        from check_solution_leaks import scan_case as leak_scan
        issues.extend(isolation_scan(case_dir))
        issues.extend(leak_scan(case_dir))

    if strict and status in {"validated", "released"}:
        if data.get("oracle_status") != "passed":
            issue(issues, "ERROR", metadata_path, "validated/released case requires oracle_status: passed")
        if data.get("redteam_status") != "passed":
            issue(issues, "ERROR", metadata_path, "validated/released case requires redteam_status: passed")
        if data.get("calibration_status") != "passed":
            issue(issues, "ERROR", metadata_path, "validated/released case requires calibration_status: passed")

    return issues


def collect_cases() -> list[Path]:
    cases_root = ROOT / "cases"
    return sorted(path for path in cases_root.iterdir() if path.is_dir() and not path.name.startswith("_"))


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate tb-hard case metadata, Harbor structure, and optional isolation/leakage checks.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--case")
    group.add_argument("--all", action="store_true")
    parser.add_argument("--strict", action="store_true", help="treat draft incompleteness as errors")
    parser.add_argument("--deep", action="store_true", help="run isolation and leakage scans")
    args = parser.parse_args()

    try:
        cases = collect_cases() if args.all else [resolve_case(args.case)]
    except FileNotFoundError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if not cases:
        print("PASS: no cases registered")
        return 0

    errors = 0
    warns = 0
    for case_dir in cases:
        issues = validate_case(case_dir, strict=args.strict, deep=args.deep)
        if not issues:
            print(f"PASS: {case_dir.name}")
        for level, path, message in issues:
            print(printable_issue(level, path, message))
            errors += int(level == "ERROR")
            warns += int(level == "WARN")
    print(f"SUMMARY: cases={len(cases)} errors={errors} warnings={warns}")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
