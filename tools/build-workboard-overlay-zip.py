#!/usr/bin/env python3
"""Assemble dist/ba-workboard-overlay zip from repo capability files."""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "dist" / "ba-workboard-overlay"
ZIP_PATH = ROOT / "dist" / "ba-workboard-overlay.zip"

COPY_PATHS = [
    "tools/upgrade-workboard.py",
    "tools/upgrade-workboard.ps1",
    "tools/upgrade-workboard.sh",
    "tools/generate-workboard-canvas.py",
    "commands/workboard.md",
    "skills/ba-assistant/templates/ba-workboard.canvas.tsx.template",
    "skills/ba-assistant/references/workboard-procedure.md",
    "skills/ba-assistant/references/workboard-format.md",
    "_workstream/regenerate-ba-actions-md.py",
    "skills/ba-assistant/references/ba-actions-format.md",
    "tools/workboard-overlay-docs/INSTALL-WORKBOARD.md",
    "tools/workboard-overlay-docs/CURSOR-INSTALL-PROMPT.md",
]


def main() -> int:
    if OUT_DIR.exists():
        shutil.rmtree(OUT_DIR)
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for rel in COPY_PATHS:
        src = ROOT / rel
        if not src.exists():
            print(f"SKIP missing {rel}")
            continue
        if rel.startswith("tools/workboard-overlay-docs/"):
            dest = OUT_DIR / Path(rel).name
        else:
            dest = OUT_DIR / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
        print(f"COPY {rel}")

    if ZIP_PATH.exists():
        ZIP_PATH.unlink()
    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for path in OUT_DIR.rglob("*"):
            if path.is_file():
                zf.write(path, path.relative_to(OUT_DIR))
    print(f"Wrote {ZIP_PATH}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
