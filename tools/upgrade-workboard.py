#!/usr/bin/env python3
"""Upgrade workboard capability files without wiping personal data.

Usage:
  python tools/upgrade-workboard.py --package "C:\\path\\to\\ba-assistant-cursor-skill"
  python tools/upgrade-workboard.py --package "..." --apply
  python tools/upgrade-workboard.py --package "..." --apply --replace-wrap

Default is dry-run. Always backs up before --apply.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

OVERLAY_FILES = [
    ("skills/ba-assistant/templates/ba-workboard.canvas.tsx.template", "skills/ba-assistant/templates/ba-workboard.canvas.tsx.template"),
    ("skills/ba-assistant/references/workboard-procedure.md", "skills/ba-assistant/references/workboard-procedure.md"),
    ("skills/ba-assistant/references/workboard-format.md", "skills/ba-assistant/references/workboard-format.md"),
    ("tools/generate-workboard-canvas.py", "_workstream/generate-workboard-canvas.py"),
    ("tools/roll-calendar-eod.py", "_workstream/roll-calendar-eod.py"),
]

OPTIONAL_COMMANDS = [
    ("commands/workboard.md", "commands/workboard.md"),
]

OPTIONAL_IF_MISSING = [
    ("_workstream/regenerate-ba-actions-md.py", "_workstream/regenerate-ba-actions-md.py"),
    ("skills/ba-assistant/references/ba-actions-format.md", "skills/ba-assistant/references/ba-actions-format.md"),
]

OPTIONAL_WRAP = ("commands/wrap.md", "commands/wrap.md")

PROTECTED_NAMES = {
    "ba-profile.mdc",
    "ba-assistant-config.mdc",
}

PROTECTED_WORKSTREAM = {
    "workboard.json",
    "ba-actions.json",
    "ba-actions.md",
    "calendar-feed.json",
}


def log(msg: str) -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def cursor_home() -> Path:
    return Path.home() / ".cursor"


def backup_file(src: Path, backup_root: Path, home: Path) -> None:
    if not src.exists():
        return
    try:
        rel = src.relative_to(home)
    except ValueError:
        rel = Path(src.name)
    dest = backup_root / rel
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def copy_overlay(src: Path, dest: Path, dry_run: bool) -> str:
    action = f"UPDATE {dest}"
    if not dry_run:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest)
    return action


def _json_actions_empty(path: Path) -> bool:
    if not path.exists() or path.stat().st_size == 0:
        return True
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(payload, dict):
        return False
    return not (payload.get("actions") or payload.get("watching"))


def _markdown_empty(path: Path) -> bool:
    if not path.exists():
        return True
    try:
        return not path.read_text(encoding="utf-8").strip()
    except OSError:
        return False


def migrate_legacy_actions(
    workstream: Path, backup_root: Path, home: Path, dry_run: bool
) -> list[str]:
    """Copy legacy action data once when the generic stores are absent/empty.

    Legacy filename literals are intentionally isolated in this migration.
    Normal runtime reads only ba-actions files. On apply, the legacy file is
    always moved into this run's backup afterwards (whether it was copied or
    the current file already won), so it can never be copied again later.
    Files are never merged.
    """
    actions: list[str] = []
    pairs = (
        (workstream / "jess-actions.json", workstream / "ba-actions.json", _json_actions_empty),
        (workstream / "jess-actions.md", workstream / "ba-actions.md", _markdown_empty),
    )
    for legacy, current, current_is_empty in pairs:
        if not legacy.exists():
            continue
        try:
            archive = backup_root / legacy.relative_to(home)
        except ValueError:
            archive = backup_root / legacy.name
        if current_is_empty(current):
            actions.append(f"MIGRATE {legacy.name} -> {current.name}, then ARCHIVE {legacy.name} -> {archive}")
            if dry_run:
                continue
            backup_file(current, backup_root, home)
            current.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(legacy, current)
        else:
            actions.append(
                f"ARCHIVE {legacy.name} -> {archive} ({current.name} already contains data and wins; files not merged)"
            )
            if dry_run:
                continue
        archive.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(legacy), str(archive))
    return actions


def main() -> int:
    ap = argparse.ArgumentParser(description="Workboard overlay upgrade (capability files only)")
    ap.add_argument("--package", required=True, help="Path to ba-assistant-cursor-skill checkout or extracted zip")
    ap.add_argument("--apply", action="store_true", help="Apply changes (default dry-run)")
    ap.add_argument("--replace-workboard-command", action="store_true", help="Replace commands/workboard.md (backed up first). Default: write workboard.md.package only")
    ap.add_argument("--replace-wrap", action="store_true", help="Also replace commands/wrap.md (backed up first)")
    ap.add_argument("--preview-canvas", action="store_true", default=True, help="After apply, generate ba-workboard-overlay-preview.canvas.tsx (default on)")
    ap.add_argument("--no-preview-canvas", dest="preview_canvas", action="store_false", help="Skip preview canvas generation")
    ap.add_argument("--cursor-home", type=Path, default=None, help="Override ~/.cursor path")
    args = ap.parse_args()
    dry_run = not args.apply

    pkg = Path(args.package).expanduser().resolve()
    home = (args.cursor_home or cursor_home()).expanduser().resolve()
    if not (pkg / "skills" / "ba-assistant").exists():
        log(f"ERROR: package not found at {pkg}")
        return 1

    log(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    log(f"Package: {pkg}")
    log(f"Cursor home: {home}")
    log("")

    plan: list[str] = []
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = home / "ba-assistant-backups" / f"workboard-overlay-{ts}"
    plan.append(f"BACKUP -> {backup_root}")

    plan.extend(migrate_legacy_actions(home / "_workstream", backup_root, home, dry_run))

    for name in PROTECTED_WORKSTREAM:
        plan.append(f"PROTECT {home / '_workstream' / name} (never overwrite)")

    for rules_name in PROTECTED_NAMES:
        plan.append(f"PROTECT {home / 'rules' / rules_name} (never overwrite)")

    targets: list[tuple[Path, Path]] = []
    for pkg_rel, home_rel in OVERLAY_FILES:
        src = pkg / pkg_rel
        dest = home / home_rel
        if not src.exists():
            plan.append(f"SKIP missing package file {src}")
            continue
        targets.append((src, dest))
        if dest.exists():
            plan.append(f"REPLACE {dest}")
        else:
            plan.append(f"CREATE {dest}")

    for pkg_rel, home_rel in OPTIONAL_IF_MISSING:
        src = pkg / pkg_rel
        dest = home / home_rel
        if not src.exists():
            continue
        if dest.exists():
            plan.append(f"SKIP optional {dest} (already present; not overwriting custom copy)")
            package_copy = dest.with_suffix(dest.suffix + ".package")
            plan.append(f"WRITE package reference {package_copy} (if --apply)")
            if not dry_run:
                shutil.copy2(src, package_copy)
        else:
            targets.append((src, dest))
            plan.append(f"CREATE optional {dest}")

    for pkg_rel, home_rel in OPTIONAL_COMMANDS:
        src = pkg / pkg_rel
        dest = home / home_rel
        if not src.exists():
            continue
        if args.replace_workboard_command:
            targets.append((src, dest))
            plan.append(f"REPLACE command {dest} (--replace-workboard-command)")
        elif dest.exists():
            package_copy = dest.with_suffix(dest.suffix + ".package")
            plan.append(f"KEEP {dest} (personalised command left in place)")
            plan.append(f"WRITE {package_copy} for comparison")
            if not dry_run:
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, package_copy)
        else:
            targets.append((src, dest))
            plan.append(f"CREATE command {dest}")

    if args.replace_wrap:
        src = pkg / OPTIONAL_WRAP[0]
        dest = home / OPTIONAL_WRAP[1]
        if src.exists():
            targets.append((src, dest))
            plan.append(f"REPLACE wrap command {dest} (--replace-wrap)")

    if not dry_run:
        backup_root.mkdir(parents=True, exist_ok=True)
        for _, dest in targets:
            backup_file(dest, backup_root, home)

    for src, dest in targets:
        plan.append(copy_overlay(src, dest, dry_run))

    if args.preview_canvas and dry_run:
        plan.append("PREVIEW would write canvases/ba-workboard-overlay-preview.canvas.tsx (live ba-workboard.canvas.tsx untouched)")

    preview_path = None
    if args.preview_canvas and not dry_run:
        generator = home / "_workstream" / "generate-workboard-canvas.py"
        projects = sorted((home / "projects").glob("*/canvases"))
        if generator.exists() and projects:
            preview_path = projects[-1] / "ba-workboard-overlay-preview.canvas.tsx"
            import subprocess

            subprocess.run(
                [sys.executable, str(generator), "--cursor-home", str(home), "--canvas", str(preview_path)],
                check=False,
            )
            plan.append(f"PREVIEW canvas {preview_path} (live ba-workboard.canvas.tsx not touched)")
        else:
            plan.append("PREVIEW skipped: generator or canvases folder not found")

    plan.append("")
    plan.append("Protected: workboard.json, actions JSON/MD, calendar-feed.json, ba-profile.mdc.")
    plan.append("Live canvas is NOT overwritten by this installer. Open ba-workboard-overlay-preview.canvas.tsx first, or wait for confirmation before regenerating ba-workboard.canvas.tsx.")

    log("=== PLAN ===")
    for line in plan:
        log(line)
    log("=== END ===")
    if dry_run:
        log("Dry-run only. Re-run with --apply to execute.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
