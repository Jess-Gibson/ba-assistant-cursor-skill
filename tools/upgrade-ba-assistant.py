#!/usr/bin/env python3
"""
Upgrade an existing BA Assistant install to the current package version (see VERSION / CHANGELOG.md) without clobbering personal config.

Usage:
  python upgrade-ba-assistant.py --package "C:\\path\\to\\ba-assistant-cursor-skill" [--dry-run]
  python upgrade-ba-assistant.py --package "..." --apply

Default is dry-run. Always backs up before --apply.

Version 15 safety defaults:
  - _workstream data is never changed unless you pass --migrate-legacy. Without
    it, legacy data that an older release would have migrated (personal_tasks[]
    in workboard.json, a legacy <name>-actions.json) is reported as WARN and left
    byte-identical.
  - ba-profile.mdc is never overwritten. Old /wrap, /validate-state, /status and /todo rows are
    reported as WARN with the exact replacement; --patch-profile replaces only
    those rows (after a backup).
  - Leftover .sh/.ps1 hook wrappers are moved to the backup only when hooks.json
    no longer references them.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

PROTECTED_RULE_NAMES = {"ba-profile.mdc", "ba-assistant-config.mdc"}
VOICE_HINTS = ("voice",)

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

# Companion skills installed alongside ba-assistant when the package ships them.
COMPANION_SKILLS = ("miro-board-analysis", "publish-docs-to-confluence")

# Files inside skills/ba-assistant/ that hold BA data, not package code.
SKIP_IN_SKILL_TREE = {"learnings.md"}


def load_installer(package: Path):
    """Reuse the installer's hook merge and workstream-script copy, so install
    and upgrade can never drift. Upgrade still does NOT call install(): that
    recopies whole skill trees and can re-seed files."""
    script = package / "tools" / "install-ba-assistant.py"
    spec = importlib.util.spec_from_file_location("ba_installer", script)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load installer {script}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def default_cursor_home() -> Path:
    return Path.home() / ".cursor"


def log(msg: str) -> None:
    # Avoid Windows cp1252 crashes on arrows / non-ASCII in plan lines
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def copy_tree_merge(src: Path, dest: Path, dry_run: bool, label: str, skip: set[str] | None = None) -> list[str]:
    actions = []
    if not src.exists():
        return [f"SKIP missing package path {src}"]
    for f in src.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(src)
        if skip and rel.as_posix() in skip:
            actions.append(f"KEEP {label}/{rel.as_posix()} (BA data, not package code)")
            continue
        # Package wins for skill files; files the BA added to the tree are left alone.
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

    pts = [p for p in data.get("personal_tasks") or [] if p.get("status") in (None, "open", "in_progress", "blocked")]
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
        data["personal_tasks_archived_v10"] = data.get("personal_tasks") or []
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


def run_workboard_action_migration(
    package: Path, workstream: Path, backup_root: Path, home: Path, dry_run: bool
) -> list[str]:
    """Reuse the canonical migrate-once implementation from upgrade-workboard."""
    script = package / "tools" / "upgrade-workboard.py"
    if not script.exists():
        return [f"MIGRATE skip: missing canonical workboard upgrader {script}"]
    spec = importlib.util.spec_from_file_location("ba_upgrade_workboard", script)
    if spec is None or spec.loader is None:
        return [f"MIGRATE skip: cannot load canonical workboard upgrader {script}"]
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.migrate_legacy_actions(workstream, backup_root, home, dry_run)


PROFILE_ROW_COMMANDS = ("/validate-state", "/wrap", "/status", "/todo")
# Phrases only the pre-Version 14 rows used. A row that has been personalised
# in some other way is left alone and reported, never rewritten.
OLD_PROFILE_ROW_MARKERS = {
    "/validate-state": "Read-only drift report",
    "/wrap": "End-of-session closeout",
    "/status": "triple-output: chat + canvas + HTML",
    "/todo": "Quick-capture a personal task into the workboard",
}


def profile_row_prefix(command: str) -> str:
    return f"| `{command}` |"


def package_profile_rows(pkg: Path) -> dict[str, str]:
    src = pkg / "rules" / "ba-profile.mdc"
    rows: dict[str, str] = {}
    if not src.exists():
        return rows
    for line in src.read_text(encoding="utf-8").splitlines():
        for command in PROFILE_ROW_COMMANDS:
            if line.startswith(profile_row_prefix(command)):
                rows[command] = line
    return rows


def plan_profile_patch(profile: Path, pkg: Path) -> tuple[list[str], str | None]:
    """(plan lines, patched text or None). Only rows still carrying the old
    wording are replaced; everything else in the file is untouched."""
    if not profile.exists():
        return [], None
    new_rows = package_profile_rows(pkg)
    raw = profile.read_bytes()
    text = raw.decode("utf-8")
    newline = "\r\n" if b"\r\n" in raw else "\n"
    lines = text.split(newline)
    plan: list[str] = []
    changed = False
    for i, line in enumerate(lines):
        for command in PROFILE_ROW_COMMANDS:
            if not line.startswith(profile_row_prefix(command)):
                continue
            replacement = new_rows.get(command)
            if not replacement or line == replacement:
                continue
            if OLD_PROFILE_ROW_MARKERS[command] in line:
                plan.append(f"WARN ba-profile.mdc {command} row describes the old behaviour")
                plan.append(f"     old: {line}")
                plan.append(f"     new: {replacement}")
                lines[i] = replacement
                changed = True
            else:
                plan.append(f"NOTE ba-profile.mdc {command} row is personalised; left as is")
    return plan, (newline.join(lines) if changed else None)


def leftover_hook_wrappers(home: Path, pkg: Path) -> list[Path]:
    """.sh/.ps1 files in ~/.cursor/hooks whose .py twin the package ships."""
    hooks_dir = home / "hooks"
    if not hooks_dir.exists():
        return []
    py_stems = {p.stem.lower() for p in (pkg / "hooks").glob("*.py")}
    return sorted(
        p for p in hooks_dir.iterdir()
        if p.is_file() and p.suffix.lower() in (".sh", ".ps1") and p.stem.lower() in py_stems
    )


def retire_hook_wrappers(home: Path, pkg: Path, backup_root: Path, dry_run: bool) -> list[str]:
    plan: list[str] = []
    hooks_json = home / "hooks.json"
    referenced = hooks_json.read_text(encoding="utf-8") if hooks_json.exists() else ""
    for wrapper in leftover_hook_wrappers(home, pkg):
        if wrapper.name in referenced:
            plan.append(f"KEEP hooks/{wrapper.name} (still referenced in hooks.json)")
            continue
        dest = backup_root / "hooks-retired" / wrapper.name
        plan.append(f"RETIRE hooks/{wrapper.name} -> {dest} (no longer referenced)")
        if not dry_run:
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(wrapper), str(dest))
    return plan


def detect_legacy_workstream(workstream: Path) -> list[str]:
    """What --migrate-legacy would act on. Read-only."""
    found: list[str] = []
    wb = workstream / "workboard.json"
    if wb.exists():
        try:
            data = json.loads(wb.read_text(encoding="utf-8-sig"))
            open_pts = [
                p for p in data.get("personal_tasks") or []
                if isinstance(p, dict) and p.get("status") in (None, "open", "in_progress", "blocked")
            ]
            if open_pts:
                found.append(f"{len(open_pts)} open personal_tasks in workboard.json")
        except (json.JSONDecodeError, OSError):
            pass
    if workstream.exists():
        for legacy in sorted(workstream.glob("*-actions.json")) + sorted(workstream.glob("*-actions.md")):
            if legacy.name.startswith("ba-actions"):
                continue
            found.append(f"actions file {legacy.name} (if it is your live actions file, leave it: "
                         "do NOT pass --migrate-legacy)")
    return found


def main() -> int:
    ap = argparse.ArgumentParser(description="Upgrade BA Assistant to the current package version")
    ap.add_argument("--package", required=True, help="Path to ba-assistant-cursor-skill checkout or extract")
    ap.add_argument("--apply", action="store_true", help="Apply changes (default is dry-run)")
    ap.add_argument("--force-personal", action="store_true", help="Allow overwriting ba-profile.mdc (dangerous)")
    ap.add_argument("--cursor-home", default=None, help="Cursor home (default: ~/.cursor)")
    ap.add_argument(
        "--migrate-legacy",
        action="store_true",
        help="Also run the old personal_tasks / legacy actions-file migrations (changes _workstream data)",
    )
    ap.add_argument(
        "--patch-profile",
        action="store_true",
        help="Replace only the old /wrap, /validate-state, /status and /todo rows in ba-profile.mdc (backed up first)",
    )
    args = ap.parse_args()
    dry_run = not args.apply

    pkg = Path(args.package).expanduser().resolve()
    skills_pkg = pkg / "skills" / "ba-assistant"
    rules_pkg = pkg / "rules"
    commands_pkg = pkg / "commands"
    if not skills_pkg.exists():
        log(f"ERROR: package skills not found at {skills_pkg}")
        return 1

    pkg_ver_file = pkg / "VERSION"
    VERSION = pkg_ver_file.read_text(encoding="utf-8").strip() if pkg_ver_file.exists() else "unknown"

    home = Path(args.cursor_home).expanduser().resolve() if args.cursor_home else default_cursor_home()
    installer = load_installer(pkg)
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
    elif profile.exists() and args.force_personal and (rules_pkg / "ba-profile.mdc").exists():
        plan.append(f"FORCE UPDATE {profile}")
        if not dry_run:
            shutil.copy2(rules_pkg / "ba-profile.mdc", profile)
    if profile.exists() and not args.force_personal:
        profile_plan, patched = plan_profile_patch(profile, pkg)
        plan.extend(profile_plan)
        if patched is not None and args.patch_profile:
            ts_prof = datetime.now().strftime("%Y%m%d-%H%M%S")
            profile_backup = profile.with_name(f"ba-profile.mdc.bak-{ts_prof}")
            plan.append(f"PATCH {profile} (only the rows above; backup {profile_backup})")
            if not dry_run:
                shutil.copy2(profile, profile_backup)
                profile.write_bytes(patched.encode("utf-8"))
        elif patched is not None:
            plan.append("WARN re-run with --patch-profile to replace only those rows (backup first)")
    plan.append(f"PROTECT {rules_dest / 'ba-assistant-config.mdc'} (personal config - never touched)")
    plan.append(f"PROTECT {home / 'initiatives'} (initiative data - never touched)")

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
        if (home / "hooks").exists():
            to_bak.append(home / "hooks")
        if commands_dest.exists():
            to_bak.append(commands_dest)
        for name in PACKAGE_RULES:
            p = rules_dest / name
            if p.exists():
                to_bak.append(p)
        backup(to_bak, backup_root)

    # Skills tree replace
    plan.extend(copy_tree_merge(skills_pkg, skills_dest, dry_run, "skills/ba-assistant", skip=SKIP_IN_SKILL_TREE))

    # Companion skills, if the package ships them
    for name in COMPANION_SKILLS:
        src = pkg / "skills" / name
        if src.exists():
            plan.extend(copy_tree_merge(src, home / "skills" / name, dry_run, f"skills/{name}"))

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

    # Commands: every commands/*.md the package ships (globbed, no hand list)
    for src in sorted(commands_pkg.glob("*.md")) if commands_pkg.exists() else []:
        plan.append(f"UPDATE command {src.name}")
        if not dry_run:
            commands_dest.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, commands_dest / src.name)

    # Hook scripts + hooks.json merge (same merge the installer uses)
    hooks_pkg = pkg / "hooks"
    if hooks_pkg.exists():
        for src in sorted(hooks_pkg.glob("*.py")):
            plan.append(f"UPDATE hook {src.name}")
            if not dry_run:
                (home / "hooks").mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, home / "hooks" / src.name)
        plan.append(f"MERGE hooks.json -> {home / 'hooks.json'} (your own hook entries are kept)")
        installer.merge_hooks_json(hooks_pkg / "hooks.json", home / "hooks.json", dry_run)
        if dry_run:
            for wrapper in leftover_hook_wrappers(home, pkg):
                plan.append(f"RETIRE hooks/{wrapper.name} if hooks.json no longer references it after the merge")
        else:
            plan.extend(retire_hook_wrappers(home, pkg, backup_root, dry_run))

    # Workboard helper scripts (code only; _workstream JSON data is never replaced)
    plan.append(f"UPDATE workboard helper scripts in {workstream}")
    installer.copy_workstream_scripts(home, pkg, dry_run)

    # Workstream seed + migrate
    plan.extend(seed_workstream(workstream, dry_run))
    if args.migrate_legacy:
        plan.extend(run_workboard_action_migration(pkg, workstream, backup_root, home, dry_run))
        plan.extend(migrate_personal_tasks(workstream, dry_run))
    else:
        legacy = detect_legacy_workstream(workstream)
        for item in legacy:
            plan.append(f"WARN legacy data left untouched: {item} (re-run with --migrate-legacy to migrate it)")
        if not legacy:
            plan.append("MIGRATE none needed (no legacy workstream data found)")

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
    return 0


if __name__ == "__main__":
    sys.exit(main())
