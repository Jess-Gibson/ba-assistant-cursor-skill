#!/usr/bin/env python3
"""preCompact hook - snapshot SESSION-CONTEXT before context compaction.

Single cross-platform replacement for the former snapshot-before-compact.ps1
and snapshot-before-compact.sh twins. Job is unchanged from both originals:
copy the file at CURSOR_SESSION_CONTEXT_PATH (set by session-init.py's
sessionStart hook) to a timestamped file in the scratch dir, and print `{}`.

`{}` is deliberate, not a placeholder: Cursor's preCompact hook output is
user_message-only per its docs, so this hook cannot re-inject context — it
can only leave a disk snapshot as a safety net. Do not add fields here.
"""
from __future__ import annotations

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


def scratch_dir() -> Path:
    """Matches session-init.py's scratch_dir() exactly (see that file for the
    per-OS rationale) — both hooks must agree on where the scratch dir is.
    """
    if sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "Temp" / "cursor-agent-scratch"
    if sys.platform == "darwin":
        base = os.environ.get("TMPDIR") or "/tmp"
    else:
        base = os.environ.get("XDG_RUNTIME_DIR") or "/tmp"
    return Path(base) / "cursor-agent-scratch"


def main() -> int:
    scratch = scratch_dir()
    try:
        scratch.mkdir(parents=True, exist_ok=True)
    except OSError:
        pass

    ctx_path = os.environ.get("CURSOR_SESSION_CONTEXT_PATH", "").strip()
    if not ctx_path or not Path(ctx_path).is_file():
        print("{}")
        return 0

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    dest = scratch / f"SESSION-CONTEXT-precompact-{stamp}.md"
    try:
        shutil.copy2(ctx_path, dest)
    except OSError:
        pass

    print("{}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
