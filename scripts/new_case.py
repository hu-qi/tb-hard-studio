#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from common import CASE_ID_RE, ROOT, parse_simple_yaml, update_registry


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a stable tb-hard case from the canonical template.")
    parser.add_argument("case_id")
    parser.add_argument("--owner", default="TBD")
    parser.add_argument("--category", default="TBD")
    parser.add_argument("--language", default="TBD")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()

    if not CASE_ID_RE.match(args.case_id):
        print("ERROR: case_id must match ^[a-z0-9][a-z0-9-]{2,63}$", file=sys.stderr)
        return 2
    template = ROOT / "cases" / "_template"
    destination = ROOT / "cases" / args.case_id
    if destination.exists():
        if not args.force:
            print(f"ERROR: case already exists: {destination}", file=sys.stderr)
            return 2
        shutil.rmtree(destination)
    shutil.copytree(template, destination)
    replacements = {
        "__CASE_ID__": args.case_id,
        "owner: TBD": f"owner: {args.owner}",
        "primary_category: TBD": f"primary_category: {args.category}",
        "primary_language: TBD": f"primary_language: {args.language}",
    }
    for path in destination.rglob("*"):
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        for old, new in replacements.items():
            text = text.replace(old, new)
        path.write_text(text, encoding="utf-8")
    data = parse_simple_yaml(destination / "case.yaml")
    update_registry(data)
    print(f"CREATED: {destination.relative_to(ROOT)}")
    print("NEXT: fill private/design-brief.md, then run make validate CASE=" + args.case_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
