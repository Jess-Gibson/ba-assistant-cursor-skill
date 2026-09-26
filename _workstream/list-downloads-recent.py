#!/usr/bin/env python3
"""List files in a folder modified within the last N days, newest first.

Cross-platform (Windows/Mac/Linux) recent-file listing. Uses pathlib normally.
On Windows only, if pathlib raises or incorrectly returns no files, it falls
back to `cmd /c dir`; file timestamps still come from Python metadata.

Usage:
  python3 list-downloads-recent.py --path "~/Downloads" --days 3
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path


def windows_dir_files(folder: Path) -> list[Path]:
    """Discover filenames without parsing locale-dependent dir timestamps."""
    try:
        proc = subprocess.run(
            ["cmd", "/c", "dir", "/a-d", "/o-d", "/b", str(folder)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if proc.returncode != 0:
        return []
    files = []
    for name in proc.stdout.splitlines():
        name = name.strip()
        if not name:
            continue
        candidate = folder / name
        try:
            if candidate.is_file():
                files.append(candidate)
        except OSError:
            continue
    return files


def list_files(folder: Path) -> list[Path]:
    if sys.platform != "win32":
        return [entry for entry in folder.iterdir() if entry.is_file()]
    try:
        files = [entry for entry in folder.iterdir() if entry.is_file()]
    except OSError:
        files = []
    return files or windows_dir_files(folder)


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
    for entry in list_files(folder):
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
