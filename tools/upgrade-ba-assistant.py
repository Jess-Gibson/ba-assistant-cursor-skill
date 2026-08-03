#!/usr/bin/env python3
"""
Upgrade an existing BA Assistant install to Version 10 without clobbering personal config.

Usage:
  python upgrade-ba-assistant.py --package "C:\\path\\to\\ba-assistant-cursor-skill" [--dry-run]
  python upgrade-ba-assistant.py --package "..." --apply

Default is dry-run. Always backs up before --apply.
"""
from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

VERSION = "10"

PROTECTED_RULE_NAMES = {"ba-profile.mdc"}
VOICE_HINTS = ("voice", "jess-voice")

PACKAGE_RULES = [
    "skills-routing.mdc",
    "todo-quick-capture.mdc",
    "sync-gates.mdc",
    "agent-behavior.mdc",
    "execution-router.mdc",
    "critical-gates.mdc",
    "ba-delivery-process.mdc",
    "agent-behavior-extended.mdc",
]

PACKAGE_COMMANDS = [
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
]


def cursor_home() -> Path:
    return Path.home() / ".cursor"


def log(msg: str) -> None:
    # Avoid Windows cp1252 crashes on arrows / non-ASCII in plan lines
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def copy_tree_merge(src: Path, dest: Path, dry_run: bool, label: str) -> list[str]:
    actions = []
    if not src.exists():
        return [f"SKIP missing package path {src}"]
    for f in src.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(src)
        # Never overwrite ba-setup from an old personal fork incorrectly — package wins for skills tree
        target = dest / rel
        actions.append(f"UPDATE {label}/{rel.as_posix()}")
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
    return actions


def backup(paths: list[Path], backup_root: Path) -> None:
    backup_root.mkdir(parents=True, exist_ok=True)
    for p in paths:
        if not p.exists():
            continue
        rel = p.name if p.is_file() else p.name
        dest = backup_root / rel
        if p.is_dir():
            if dest.exists():
                shutil.rmtree(dest)
            shutil.copytree(p, dest)
        else:
            shutil.copy2(p, dest)


def migrate_personal_tasks(workstream: Path, dry_run: bool) -> list[str]:
    actions = []
    wb = workstream / "workboard.json"
    ba = workstream / "ba-actions.json"
    if not wb.exists():
        return ["MIGRATE skip: no workboard.json"]
    try:
        data = json.loads(wb.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return ["MIGRATE fail: workboard.json invalid JSON"]

    pts = [p for p in data.get("personal_tasks", []) if p.get("status") in (None, "open", "in_progress", "blocked")]
    if not pts:
        return ["MIGRATE skip: no open personal_tasks"]

    existing = {"actions": [], "schema_version": 1, "next_id": 1}
    if ba.exists():
        try:
            existing = json.loads(ba.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    if existing.get("actions"):
        return ["MIGRATE skip: ba-actions.json already has actions (not overwriting)"]

    actions_out = []
    next_id = int(existing.get("next_id") or 1)
    for pt in pts:
        aid = f"BA-{next_id:03d}"
        next_id += 1
        actions_out.append(
            {
                "id": aid,
                "task": pt.get("task") or pt.get("description") or "Migrated task",
                "initiative": pt.get("initiative"),
                "raised": pt.get("raised") or datetime.now(timezone.utc).date().isoformat(),
                "due": pt.get("due"),
                "status": pt.get("status") or "open",
                "priority": pt.get("priority") or "medium",
                "blocked": bool(pt.get("blocked")),
                "blocker_notes": pt.get("blocker_notes") or pt.get("notes"),
                "source": {"type": "migrate", "label": "personal_tasks→ba-actions Version 10"},
                "remind_on": pt.get("remind_on"),
                "reminder": pt.get("reminder"),
            }
        )
    payload = {
        "schema_version": 1,
        "last_synced": datetime.now(timezone.utc).isoformat(),
        "next_id": next_id,
        "actions": actions_out,
    }
    actions.append(f"MIGRATE {len(actions_out)} personal_tasks -> ba-actions.json")
    if not dry_run:
        ba.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        # Archive personal_tasks in workboard
        data["personal_tasks_archived_v10"] = data.get("personal_tasks", [])
        data["personal_tasks"] = []
        wb.write_text(json.dumps(data, indent=2), encoding="utf-8")
        actions.append("MIGRATE archived personal_tasks into personal_tasks_archived_v10; cleared personal_tasks[]")
    return actions


def seed_workstream(workstream: Path, dry_run: bool) -> list[str]:
    actions = []
    if not dry_run:
        workstream.mkdir(parents=True, exist_ok=True)
    actions.append(f"SEED dir {workstream}")
    ba = workstream / "ba-actions.json"
    wb = workstream / "workboard.json"
    if not ba.exists():
        actions.append("SEED ba-actions.json")
        if not dry_run:
            ba.write_text(
                json.dumps(
                    {"schema_version": 1, "last_synced": None, "next_id": 1, "actions": []},
                    indent=2,
                ),
                encoding="utf-8",
            )
    if not wb.exists():
        actions.append("SEED workboard.json")
        if not dry_run:
            wb.write_text(
                json.dumps(
                    {
                        "last_refreshed": None,
                        "initiatives": [],
                        "upcoming_meetings": [],
                        "sync_status": {},
                        "personal_tasks": [],
                    },
                    indent=2,
                ),
                encoding="utf-8",
            )
    return actions


def main() -> int:
    ap = argparse.ArgumentParser(description="Upgrade BA Assistant to Version 10")
    ap.add_argument("--package", required=True, help="Path to ba-assistant-cursor-skill checkout or extract")
    ap.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    ap.add_argument("--force-personal", action="store_true", help="Allow overwriting ba-profile.mdc (dangerous)")
    args = ap.parse_args()
    dry_run = not args.apply

    pkg = Path(args.package).expanduser().resolve()
    skills_pkg = pkg / "skills" / "ba-assistant"
    rules_pkg = pkg / "rules"
    commands_pkg = pkg / "commands"
    if not skills_pkg.exists():
        log(f"ERROR: package skills not found at {skills_pkg}")
        return 1

    home = cursor_home()
    skills_dest = home / "skills" / "ba-assistant"
    rules_dest = home / "rules"
    commands_dest = home / "commands"
    workstream = home / "_workstream"

    installed_ver = "pre-10"
    ver_file = skills_dest / "VERSION"
    if ver_file.exists():
        installed_ver = ver_file.read_text(encoding="utf-8").strip() or "pre-10"

    log(f"Installed version: {installed_ver}")
    log(f"Target version: {VERSION}")
    log(f"Mode: {'APPLY' if args.apply else 'DRY-RUN'}")
    log(f"Package: {pkg}")

    plan: list[str] = []

    # Protect ba-profile
    profile = rules_dest / "ba-profile.mdc"
    if profile.exists() and not args.force_personal:
        plan.append(f"PROTECT {profile} (personalised - skipped)")
    elif profile.exists() and args.force_personal:
        plan.append(f"FORCE UPDATE {profile}")

    # Protect voice rules
    if rules_dest.exists():
        for r in rules_dest.glob("*.mdc"):
            if any(h in r.name.lower() for h in VOICE_HINTS):
                plan.append(f"PROTECT {r} (voice)")

    plan.append(f"PROTECT {workstream} data files (migrate only; no wipe)")

    # Backup
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = home / "ba-assistant-backups" / f"pre-v{VERSION}-{ts}"
    plan.append(f"BACKUP -> {backup_root}")
    if not dry_run:
        to_bak = []
        if skills_dest.exists():
            to_bak.append(skills_dest)
        if (home / "hooks.json").exists():
            to_bak.append(home / "hooks.json")
        for name in PACKAGE_RULES:
            p = rules_dest / name
            if p.exists():
                to_bak.append(p)
        backup(to_bak, backup_root)

    # Skills tree replace
    plan.extend(copy_tree_merge(skills_pkg, skills_dest, dry_run, "skills/ba-assistant"))

    # Delete obsolete ba-workboard
    obsolete = skills_dest / "sub-skills" / "ba-workboard"
    if obsolete.exists():
        plan.append(f"DELETE obsolete {obsolete}")
        if not dry_run:
            shutil.rmtree(obsolete)

    # Rules (except ba-profile)
    for name in PACKAGE_RULES:
        src = rules_pkg / name
        dest = rules_dest / name
        if not src.exists():
            continue
        if name in PROTECTED_RULE_NAMES and dest.exists() and not args.force_personal:
            plan.append(f"SKIP rule {name} (protected)")
            continue
        plan.append(f"UPDATE rule {name}")
        if not dry_run:
            rules_dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    # Commands
    for name in PACKAGE_COMMANDS:
        src = commands_pkg / name
        dest = commands_dest / name
        if not src.exists():
            continue
        plan.append(f"UPDATE command {name}")
        if not dry_run:
            commands_dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)

    # Workstream seed + migrate
    plan.extend(seed_workstream(workstream, dry_run))
    plan.extend(migrate_personal_tasks(workstream, dry_run))

    # VERSION stamp
    plan.append(f"WRITE {skills_dest / 'VERSION'} = {VERSION}")
    if not dry_run:
        skills_dest.mkdir(parents=True, exist_ok=True)
        (skills_dest / "VERSION").write_text(VERSION + "\n", encoding="utf-8")

    log("")
    log("=== PLAN ===")
    for line in plan:
        log(line)
    log("=== END ===")
    if dry_run:
        log("Dry-run only. Re-run with --apply to execute.")
    else:
        log("Applied. Re-open Cursor / start a new chat, then run /workboard once.")
        log("hooks.json was NOT replaced; merge calendar sessionStart yourself if desired.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
