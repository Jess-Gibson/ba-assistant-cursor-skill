#!/usr/bin/env python3
"""List files in a folder modified within the last N days, newest first.

Cross-platform (Windows/Mac/Linux) replacement for a folder-listing script
that only ever existed as a Windows-only reference, never shipped. Uses
plain Python directory scanning (pathlib), not the OS shell -- so it doesn't
depend on `cmd /c dir` or PowerShell's Get-ChildItem, and doesn't inherit
either platform's own quirks with those tools on some Downloads folders.

Usage:
  python3 list-downloads-recent.py --path "~/Downloads" --days 3
"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser(
        description="List recently modified files in a folder, newest first"
    )
    ap.add_argument("--path", required=True, type=Path)
    ap.add_argument("--days", type=int, default=3)
    args = ap.parse_args()

    folder = args.path.expanduser().resolve()
    if not folder.is_dir():
        print(f"ERROR: not a folder: {folder}", file=sys.stderr)
        return 1

    cutoff = datetime.now() - timedelta(days=args.days)
    entries: list[tuple[datetime, Path]] = []
    for entry in folder.iterdir():
        if not entry.is_file():
            continue
        try:
            mtime = datetime.fromtimestamp(entry.stat().st_mtime)
        except OSError:
            continue
        if mtime >= cutoff:
            entries.append((mtime, entry))

    entries.sort(key=lambda pair: pair[0], reverse=True)

    if not entries:
        print(f"No files modified in the last {args.days} day(s) in {folder}")
        return 0

    for mtime, entry in entries:
        print(f"{mtime.strftime('%Y-%m-%d %H:%M:%S')}  {entry.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
