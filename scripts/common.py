#!/usr/bin/env python3
"""Shared helpers for tb-hard authoring scripts. Standard library only."""
from __future__ import annotations

import csv
import hashlib
import os
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CASE_ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
STATUSES = {
    "draft",
    "active",
    "oracle-passed",
    "redteam-passed",
    "calibrated",
    "validated",
    "released",
    "rejected",
}


def repo_root() -> Path:
    return ROOT


def resolve_case(case_arg: str) -> Path:
    candidate = Path(case_arg)
    if candidate.exists():
        return candidate.resolve()
    case_dir = ROOT / "cases" / case_arg
    if not case_dir.exists():
        raise FileNotFoundError(f"Case not found: {case_arg}")
    return case_dir


def parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return ""
    if value in {"[]", "{}"}:
        return [] if value == "[]" else {}
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.lower() in {"null", "none", "~"}:
        return None
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [parse_scalar(piece) for piece in inner.split(",")]
    return value


def parse_simple_yaml(path: Path) -> dict[str, Any]:
    """Parse the small, controlled YAML subset used by case.yaml.

    Supports top-level scalars, flow lists, and one-level `- item` lists. It
    intentionally rejects nested maps to keep this repository dependency-free.
    """
    data: dict[str, Any] = {}
    active_list: str | None = None
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") or line.startswith("- "):
            if active_list is None:
                raise ValueError(f"{path}:{line_no}: list item without parent key")
            data.setdefault(active_list, []).append(parse_scalar(line.split("-", 1)[1].strip()))
            continue
        if line.startswith(" ") or ":" not in line:
            raise ValueError(f"{path}:{line_no}: unsupported YAML; use top-level keys and simple lists")
        key, raw_value = line.split(":", 1)
        key = key.strip()
        if not key:
            raise ValueError(f"{path}:{line_no}: empty key")
        value = raw_value.strip()
        if not value:
            data[key] = []
            active_list = key
        else:
            data[key] = parse_scalar(value)
            active_list = None
    return data


def task_revision(case_dir: Path) -> str:
    try:
        output = subprocess.check_output(
            ["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
        dirty = subprocess.call(
            ["git", "-C", str(ROOT), "diff", "--quiet"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )
        return output + ("-dirty" if dirty else "")
    except Exception:
        return "uncommitted"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def sha256_tree(path: Path, exclude: set[str] | None = None) -> str:
    exclude = exclude or set()
    digest = hashlib.sha256()
    for item in sorted(p for p in path.rglob("*") if p.is_file()):
        rel = item.relative_to(path).as_posix()
        if any(rel == name or rel.startswith(name.rstrip("/") + "/") for name in exclude):
            continue
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(item.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def read_registry() -> list[dict[str, str]]:
    registry = ROOT / "registry" / "tasks.csv"
    if not registry.exists():
        return []
    with registry.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def update_registry(case_data: dict[str, Any]) -> None:
    registry = ROOT / "registry" / "tasks.csv"
    rows = read_registry()
    fields = [
        "case_id", "status", "version", "primary_category", "primary_language",
        "difficulty_dimensions", "owner", "task_revision",
    ]
    row = {
        "case_id": str(case_data.get("case_id", "")),
        "status": str(case_data.get("status", "")),
        "version": str(case_data.get("version", "")),
        "primary_category": str(case_data.get("primary_category", "")),
        "primary_language": str(case_data.get("primary_language", "")),
        "difficulty_dimensions": "|".join(str(x) for x in case_data.get("difficulty_dimensions", []) if str(x)),
        "owner": str(case_data.get("owner", "")),
        "task_revision": str(case_data.get("task_revision", "")),
    }
    replaced = False
    for index, existing in enumerate(rows):
        if existing.get("case_id") == row["case_id"]:
            rows[index] = row
            replaced = True
            break
    if not replaced:
        rows.append(row)
    registry.parent.mkdir(parents=True, exist_ok=True)
    with registry.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(sorted(rows, key=lambda item: item["case_id"]))


def printable_issue(level: str, path: Path | str, message: str) -> str:
    try:
        rendered = Path(path).resolve().relative_to(ROOT).as_posix()
    except Exception:
        rendered = str(path)
    return f"{level}: {rendered}: {message}"
