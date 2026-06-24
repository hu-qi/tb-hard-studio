#!/usr/bin/env python3
"""Generate a deterministic purchaser-v1 zip from the canonical Harbor task."""
from __future__ import annotations

import argparse
import json
import os
import stat
import tempfile
import zipfile
from pathlib import Path

from common import ROOT, parse_simple_yaml, resolve_case, sha256_file, sha256_tree, utc_now
from validate_case import validate_case

PRIVATE_EXCLUDES = ["task/solution", "private", "evidence", ".agents", ".claude", "docs", "AGENTS.md", "CLAUDE.md"]


def add_file(zf: zipfile.ZipFile, archive_name: str, source: Path) -> None:
    info = zipfile.ZipInfo(archive_name)
    info.date_time = (1980, 1, 1, 0, 0, 0)
    info.compress_type = zipfile.ZIP_DEFLATED
    mode = source.stat().st_mode
    info.external_attr = (stat.S_IMODE(mode) & 0xFFFF) << 16
    zf.writestr(info, source.read_bytes())


def main() -> int:
    parser = argparse.ArgumentParser(description="Export a canonical Harbor task into purchaser-v1 format.")
    parser.add_argument("--case", required=True)
    parser.add_argument("--allow-unvalidated", action="store_true")
    parser.add_argument("--output-dir", type=Path)
    args = parser.parse_args()

    case_dir = resolve_case(args.case)
    issues = validate_case(case_dir, strict=True, deep=True)
    errors = [item for item in issues if item[0] == "ERROR"]
    if errors:
        for level, path, message in errors:
            print(f"{level}: {path}: {message}")
        return 1

    metadata = parse_simple_yaml(case_dir / "case.yaml")
    if metadata.get("status") not in {"validated", "released"} and not args.allow_unvalidated:
        print("ERROR: purchaser export requires case status validated or released; use --allow-unvalidated only for a review draft")
        return 1

    task = case_dir / "task"
    dockerfile = task / "environment" / "Dockerfile"
    instruction = task / "instruction.md"
    tests = task / "tests"
    if not dockerfile.exists():
        print("ERROR: purchaser-v1 requires task/environment/Dockerfile")
        return 1
    if not instruction.exists() or not tests.exists():
        print("ERROR: canonical task is missing instruction or tests")
        return 1
    tag = str(metadata.get("purchaser_tag", "")).strip()
    if not tag or tag == "TBD":
        print("ERROR: case.yaml purchaser_tag must be set")
        return 1

    output_dir = args.output_dir or (ROOT / "delivery" / "final")
    output_dir.mkdir(parents=True, exist_ok=True)
    archive = output_dir / f"{case_dir.name}-purchaser-v1.zip"
    manifest_dir = case_dir / "exports" / "purchaser-v1"
    manifest_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = manifest_dir / "delivery-manifest.json"

    with tempfile.TemporaryDirectory(prefix="tb-hard-export-") as temp_name:
        staging = Path(temp_name) / case_dir.name
        (staging / "test").mkdir(parents=True)
        (staging / "Dockerfile").write_bytes(dockerfile.read_bytes())
        (staging / "instruction.md").write_bytes(instruction.read_bytes())
        (staging / "tag.txt").write_text(tag + "\n", encoding="utf-8")
        for file in sorted(p for p in tests.rglob("*") if p.is_file()):
            target = staging / "test" / file.relative_to(tests)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(file.read_bytes())
            os.chmod(target, stat.S_IMODE(file.stat().st_mode))

        included = sorted(path.relative_to(staging).as_posix() for path in staging.rglob("*") if path.is_file())
        forbidden = [name for name in included if any(token in f"/{name}/" for token in ("/solution/", "/private/", "/evidence/", "/.agents/", "/.claude/"))]
        if forbidden:
            print(f"ERROR: export contains forbidden file(s): {forbidden}")
            return 1

        with zipfile.ZipFile(archive, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for relative in included:
                add_file(zf, f"{case_dir.name}/{relative}", staging / relative)

    manifest = {
        "case_id": case_dir.name,
        "export_version": "purchaser-v1",
        "generated_at_utc": utc_now(),
        "canonical_task_sha256": sha256_tree(task),
        "archive_sha256": sha256_file(archive),
        "archive_path": archive.relative_to(ROOT).as_posix(),
        "included_files": [f"{case_dir.name}/{item}" for item in included],
        "excluded_private_paths": PRIVATE_EXCLUDES,
        "task_revision": str(metadata.get("task_revision", "uncommitted")),
    }
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"EXPORTED: {archive.relative_to(ROOT)}")
    print(f"MANIFEST: {manifest_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
