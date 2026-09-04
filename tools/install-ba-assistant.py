#!/usr/bin/env python3
"""Install BA Assistant into a Cursor home directory.

Copies skills, rules, hooks, and commands from this package (or a clone)
into ~/.cursor (or --cursor-home). Does not run the personalisation wizard;
the agent runs ba-setup after install.

Usage:
  python tools/install-ba-assistant.py --dry-run
  python tools/install-ba-assistant.py --apply
  python tools/install-ba-assistant.py --apply --cursor-home "C:\\Users\\You\\.cursor"
  python tools/install-ba-assistant.py --apply --package "C:\\path\\to\\ba-assistant-cursor-skill"
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "11"

PACKAGE_RULES = [
    "skills-routing.mdc",
    "todo-quick-capture.mdc",
    "sync-gates.mdc",
    "agent-behavior.mdc",
    "execution-router.mdc",
    "critical-gates.mdc",
    "ba-delivery-process.mdc",
    "agent-behavior-extended.mdc",
    "markdown-readability.mdc",
]

# ba-profile.mdc is the always-on persona. Never overwrite a personalised one.
# Wizard config is written later to ba-assistant-config.mdc.
PROTECTED_RULE_NAMES = {"ba-profile.mdc", "ba-assistant-config.mdc"}

PACKAGE_COMMANDS = [
    "ba-assistant.md",
    "setup.md",
    "workboard.md",
    "todo.md",
    "wrap.md",
    "status.md",
    "canvas.md",
    "validate-state.md",
    "handover.md",
    "debrief.md",
    "metrics.md",
    "reanchor.md",
    "retro.md",
    "next.md",
    "report.md",
    "fast-track.md",
    "publish-status.md",
    "snapshot.md",
    "audit-standards.md",
]


def log(msg: str) -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def package_root_from_script() -> Path:
    return Path(__file__).resolve().parent.parent


def ensure_dir(path: Path, dry_run: bool) -> None:
    if dry_run:
        log(f"MKDIR {path}")
        return
    path.mkdir(parents=True, exist_ok=True)


def copy_file(src: Path, dest: Path, dry_run: bool) -> None:
    log(f"COPY {src} -> {dest}")
    if dry_run:
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)


def copy_tree(src: Path, dest: Path, dry_run: bool) -> int:
    count = 0
    if not src.exists():
        log(f"SKIP missing {src}")
        return 0
    if dest.exists() and not dry_run:
        shutil.rmtree(dest)
    for f in src.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(src)
        target = dest / rel
        copy_file(f, target, dry_run)
        count += 1
    return count


def merge_hooks_json(package_hooks: Path, dest_hooks: Path, dry_run: bool) -> None:
    if not package_hooks.exists():
        log("SKIP hooks.json (missing in package)")
        return
    pkg = json.loads(package_hooks.read_text(encoding="utf-8"))
    if dest_hooks.exists():
        try:
            existing = json.loads(dest_hooks.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            existing = {}
        # Shallow merge: package keys win for BA hooks; preserve unknown keys
        merged = dict(existing)
        for k, v in pkg.items():
            merged[k] = v
        out = merged
        log(f"MERGE hooks.json -> {dest_hooks}")
    else:
        out = pkg
        log(f"COPY hooks.json -> {dest_hooks}")
    if not dry_run:
        dest_hooks.parent.mkdir(parents=True, exist_ok=True)
        dest_hooks.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")


def seed_workstream(cursor_home: Path, package: Path, dry_run: bool) -> None:
    ws = cursor_home / "_workstream"
    ensure_dir(ws, dry_run)
    wb = ws / "workboard.json"
    ba = ws / "ba-actions.json"
    if not wb.exists():
        payload = {
            "initiatives": [],
            "last_refreshed": None,
        }
        log(f"SEED {wb}")
        if not dry_run:
            wb.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    if not ba.exists():
        payload = {
            "schema_version": 1,
            "last_synced": None,
            "last_generated_md": None,
            "next_id": 1,
            "actions": [],
            "watching": [],
        }
        log(f"SEED {ba}")
        if not dry_run:
            ba.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    readme_src = package / "_workstream" / "README.md"
    if readme_src.exists():
        copy_file(readme_src, ws / "README.md", dry_run)


def seed_initiatives(cursor_home: Path, dry_run: bool) -> Path:
    initiatives = cursor_home / "initiatives"
    ensure_dir(initiatives, dry_run)
    readme = initiatives / "README.md"
    if not readme.exists():
        text = (
            "# BA initiatives\n\n"
            "Default root for BA Assistant initiative folders "
            "(`BA_INITIATIVES_ROOT`).\n\n"
            "Create initiatives with: "
            '"Start a new initiative called [name]"\n'
        )
        log(f"SEED {readme}")
        if not dry_run:
            readme.write_text(text, encoding="utf-8")
    return initiatives


def write_install_marker(cursor_home: Path, package: Path, dry_run: bool) -> None:
    marker = cursor_home / ".ba-assistant-installed.json"
    payload = {
        "version": VERSION,
        "installed_at": datetime.now(timezone.utc).isoformat(),
        "package_path": str(package),
        "skills": True,
        "rules": True,
        "commands": True,
        "hooks": True,
    }
    log(f"WRITE {marker}")
    if not dry_run:
        marker.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def install(package: Path, cursor_home: Path, dry_run: bool) -> int:
    log(f"Package: {package}")
    log(f"Cursor home: {cursor_home}")
    log(f"Mode: {'DRY-RUN' if dry_run else 'APPLY'}")
    log("-" * 60)

    skills_src = package / "skills" / "ba-assistant"
    if not (skills_src / "SKILL.md").exists():
        log(f"FATAL: {skills_src / 'SKILL.md'} not found")
        return 2

    ensure_dir(cursor_home / "skills", dry_run)
    ensure_dir(cursor_home / "rules", dry_run)
    ensure_dir(cursor_home / "commands", dry_run)
    ensure_dir(cursor_home / "hooks", dry_run)

    # Skills (full replace of ba-assistant tree)
    copy_tree(skills_src, cursor_home / "skills" / "ba-assistant", dry_run)

    # Optional Miro companion
    miro = package / "skills" / "miro-board-analysis"
    if miro.exists():
        copy_tree(miro, cursor_home / "skills" / "miro-board-analysis", dry_run)

    # Rules
    for name in PACKAGE_RULES:
        src = package / "rules" / name
        if src.exists():
            copy_file(src, cursor_home / "rules" / name, dry_run)

    # Persona rule: install only if missing
    persona = package / "rules" / "ba-profile.mdc"
    dest_persona = cursor_home / "rules" / "ba-profile.mdc"
    if persona.exists():
        if dest_persona.exists():
            log(f"KEEP existing {dest_persona} (persona / personalised)")
        else:
            copy_file(persona, dest_persona, dry_run)

    # Commands
    for name in PACKAGE_COMMANDS:
        src = package / "commands" / name
        if src.exists():
            copy_file(src, cursor_home / "commands" / name, dry_run)
    # Copy any other command stubs present in package
    cmd_dir = package / "commands"
    if cmd_dir.exists():
        for src in cmd_dir.glob("*.md"):
            if src.name not in PACKAGE_COMMANDS:
                copy_file(src, cursor_home / "commands" / src.name, dry_run)

    # Hooks scripts
    hooks_dir = package / "hooks"
    if hooks_dir.exists():
        for src in hooks_dir.iterdir():
            if src.name == "hooks.json":
                continue
            if src.is_file():
                copy_file(src, cursor_home / "hooks" / src.name, dry_run)
        merge_hooks_json(hooks_dir / "hooks.json", cursor_home / "hooks.json", dry_run)

    seed_workstream(cursor_home, package, dry_run)
    initiatives = seed_initiatives(cursor_home, dry_run)
    write_install_marker(cursor_home, package, dry_run)

    log("-" * 60)
    log("Install complete." if not dry_run else "Dry-run complete.")
    log(f"Default initiatives folder: {initiatives}")
    log("Next: restart Cursor (or open a new chat), then run /setup")
    log("     or say: run BA Assistant setup wizard")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Install BA Assistant into Cursor home")
    ap.add_argument(
        "--package",
        type=Path,
        default=None,
        help="Path to ba-assistant-cursor-skill package (default: parent of tools/)",
    )
    ap.add_argument(
        "--cursor-home",
        type=Path,
        default=None,
        help="Cursor home (default: ~/.cursor)",
    )
    ap.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    ap.add_argument("--dry-run", action="store_true", help="Show actions only (default)")
    args = ap.parse_args()

    package = (args.package or package_root_from_script()).resolve()
    cursor_home = (args.cursor_home or (Path.home() / ".cursor")).resolve()
    dry_run = not args.apply
    if args.dry_run:
        dry_run = True

    return install(package, cursor_home, dry_run)


if __name__ == "__main__":
    sys.exit(main())
