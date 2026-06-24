#!/usr/bin/env python3
"""Materialize generic skills into Claude and .agents discovery directories.

Use copies by default so archives and Windows checkouts do not depend on symlink support.
"""
from __future__ import annotations

import argparse
import filecmp
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "skills-core"
TARGETS = [ROOT / ".claude" / "skills", ROOT / ".agents" / "skills"]


def files(root: Path):
    return sorted(root.glob("*/SKILL.md"))


def sync(check: bool) -> int:
    source_files = files(SOURCE)
    if not source_files:
        print("ERROR: skills-core contains no SKILL.md files", file=sys.stderr)
        return 2
    changed = False
    for src in source_files:
        skill = src.parent.name
        for target_root in TARGETS:
            dst = target_root / skill / "SKILL.md"
            same = dst.exists() and filecmp.cmp(src, dst, shallow=False)
            if not same:
                changed = True
                if check:
                    print(f"OUT-OF-SYNC: {dst.relative_to(ROOT)}")
                else:
                    dst.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(src, dst)
                    print(f"SYNCED: {dst.relative_to(ROOT)}")
    # Flag orphan projections too.
    source_names = {p.parent.name for p in source_files}
    for target_root in TARGETS:
        for dst in files(target_root):
            if dst.parent.name not in source_names:
                changed = True
                print(f"ORPHAN: {dst.relative_to(ROOT)}")
    if check and changed:
        return 1
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    raise SystemExit(sync(args.check))
