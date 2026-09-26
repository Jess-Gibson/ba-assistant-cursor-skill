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
import importlib.util
import json
import platform
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

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

# Relative paths (posix, relative to skills/ba-assistant/) that a *running*
# install writes real content INTO, not just reads. A reinstall must never
# silently destroy these once they hold genuine user content.
#
# learnings.md used to live inside this tree and accumulated real
# cross-initiative learnings via /retro, so a plain "wipe + copy fresh
# package files" install (see copy_tree) used to erase it with zero backup.
# It has since been relocated to `_workstream/learnings.md` (see
# seed_learnings()), alongside ba-actions.json / workboard.json, which is why
# copy_tree excludes it from the tree it replaces (EXCLUDE_FROM_SKILL_TREE
# below) rather than protecting it in place. It stays listed here so
# seed_learnings() can recognise and migrate a pre-fix install's legacy copy
# instead of losing it.
USER_STATE = {
    "learnings.md",
}

# Paths (posix, relative to skills/ba-assistant/) that copy_tree must never
# copy into the destination tree, because their canonical runtime location has
# moved elsewhere. The package still ships a sample at this path (for
# seed_learnings() to seed from); it is simply never installed here anymore.
EXCLUDE_FROM_SKILL_TREE = {
    "learnings.md",
}

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


def files_differ(a: Path, b: Path) -> bool:
    """True unless both paths exist and are byte-identical."""
    if not a.exists() or not b.exists():
        return True
    try:
        return a.read_bytes() != b.read_bytes()
    except OSError:
        return True


def copy_tree(
    src: Path,
    dest: Path,
    dry_run: bool,
    user_state: set[str] | None = None,
    exclude: set[str] | None = None,
) -> int:
    """Copy every file under src into dest, replacing dest's contents.

    user_state: relative posix paths that must never be silently clobbered
    once dest's copy holds real content (i.e. it exists and differs, byte for
    byte, from src's own fresh copy of the same file). A first-time install
    (no existing dest file) or a dest file that's still identical to the
    package sample is not "real content" and is copied/reseeded normally;
    only a dest file that has genuinely diverged is PRESERVEd.

    exclude: relative posix paths to skip entirely, for files whose canonical
    runtime location has moved outside this tree (the caller is expected to
    seed/migrate them elsewhere before calling this).
    """
    count = 0
    user_state = user_state or set()
    exclude = exclude or set()
    if not src.exists():
        log(f"SKIP missing {src}")
        return 0

    # Snapshot dest's current file set and protect any user-state content
    # BEFORE the wipe below — rmtree would otherwise destroy both the
    # evidence needed to tell SEED from UPDATE and the content we must
    # preserve.
    existing_files: set[str] = set()
    preserved: dict[str, bytes] = {}
    if dest.exists():
        for f in dest.rglob("*"):
            if f.is_file():
                existing_files.add(f.relative_to(dest).as_posix())
        for rel in user_state:
            existing = dest / rel
            fresh_sample = src / rel
            if existing.exists() and files_differ(existing, fresh_sample):
                try:
                    preserved[rel] = existing.read_bytes()
                except OSError:
                    log(f"WARN could not read {existing} to preserve it; it may be overwritten")

    if dest.exists() and not dry_run:
        shutil.rmtree(dest)

    for f in src.rglob("*"):
        if not f.is_file():
            continue
        rel = f.relative_to(src)
        rel_posix = rel.as_posix()
        target = dest / rel
        if rel_posix in exclude:
            log(f"SKIP {target} (relocated out of this tree; see seed_learnings)")
            continue
        if rel_posix in preserved:
            log(f"PRESERVE {target} (existing content differs from package sample, not overwritten)")
            if not dry_run:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(preserved[rel_posix])
            count += 1
            continue
        verb = "UPDATE" if rel_posix in existing_files else "SEED"
        log(f"{verb} {f} -> {target}")
        if not dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(f, target)
        count += 1
    return count


def backup_existing_install(cursor_home: Path, package: Path, dry_run: bool) -> None:
    """Back up the current skills/ba-assistant tree + hooks.json before any
    destructive write, the same way upgrade-ba-assistant.py's backup() does.
    A fresh install onto an empty target has nothing to back up, so this is a
    no-op unless cursor_home already has an install.
    """
    skills_dest = cursor_home / "skills" / "ba-assistant"
    if not skills_dest.exists():
        return
    version_file = package / "VERSION"
    version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "unknown"
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = cursor_home / "ba-assistant-backups" / f"pre-install-v{version}-{ts}"
    log(f"BACKUP {skills_dest} -> {backup_root}")
    hooks_json = cursor_home / "hooks.json"
    if hooks_json.exists():
        log(f"BACKUP {hooks_json} -> {backup_root / 'hooks.json'}")
    if dry_run:
        return
    backup_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(skills_dest, backup_root / "ba-assistant")
    if hooks_json.exists():
        shutil.copy2(hooks_json, backup_root / "hooks.json")


def seed_learnings(cursor_home: Path, package: Path, dry_run: bool) -> None:
    """Seed `_workstream/learnings.md` — the canonical runtime location for
    cross-initiative learnings — from the package's shipped sample, without
    ever silently overwriting real accumulated content.

    Mirrors seed_workstream()'s ba-actions.json/workboard.json pattern: only
    write when nothing is there yet. Additionally migrates a pre-fix install's
    legacy copy at skills/ba-assistant/learnings.md (which used to be the
    runtime location, and which copy_tree's rmtree would otherwise destroy)
    the first time this runs against it, so real learnings aren't lost across
    the upgrade to this fixed installer.

    Must run before copy_tree touches the skills tree, so the legacy file (if
    any) still exists to migrate from.
    """
    ws = cursor_home / "_workstream"
    dest = ws / "learnings.md"
    sample = package / "skills" / "ba-assistant" / "learnings.md"
    legacy = cursor_home / "skills" / "ba-assistant" / "learnings.md"

    if dest.exists():
        log(f"PRESERVE {dest} (existing learnings kept)")
        return

    if legacy.exists() and files_differ(legacy, sample):
        log(f"MIGRATE {legacy} -> {dest} (preserving accumulated learnings from the pre-fix install location)")
        if not dry_run:
            ws.mkdir(parents=True, exist_ok=True)
            shutil.copy2(legacy, dest)
        return

    if sample.exists():
        log(f"SEED {dest} (from package sample)")
        if not dry_run:
            ws.mkdir(parents=True, exist_ok=True)
            shutil.copy2(sample, dest)
    else:
        log(f"SKIP {dest} (no package sample found at {sample})")


# Script extensions recognised when matching a hook entry's `command` to a
# package-owned script (e.g. "python ./hooks/jira-dor-gate.py" -> "jira-dor-gate.py").
HOOK_SCRIPT_EXTENSIONS = (".py", ".ps1", ".sh", ".js", ".cjs", ".mjs")


def hook_entry_script_name(entry: dict) -> str | None:
    """Return the script basename a hook entry's `command` invokes, or None if
    the entry has no `command` (e.g. `"type": "prompt"` entries) or none of
    its tokens look like a script path. None-basename entries are never
    treated as matching anything else, so they are always kept as-is.
    """
    cmd = entry.get("command")
    if not isinstance(cmd, str) or not cmd.strip():
        return None
    for token in reversed(cmd.split()):
        # A quoted absolute path (e.g. `py "C:\Users\...\session-init.py"`) splits
        # on whitespace into a token still wrapped in its quote characters -- strip
        # them before checking the extension, or a legitimately quoted package hook
        # is invisible to matching and gets duplicated on merge instead of replaced.
        token = token.strip('"\'')
        candidate = token.replace("\\", "/").rsplit("/", 1)[-1]
        if candidate.lower().endswith(HOOK_SCRIPT_EXTENSIONS):
            return candidate
    return None


def merge_hook_event(event_name: str, user_entries: list, pkg_entries: list) -> tuple[list, list[str]]:
    """Merge one hooks.<event> array.

    The package's own entries for this event (matched by script basename)
    always reflect the package's current version. Any entry the user added
    that this package doesn't own for this event (including any `"type":
    "prompt"` entry, which has no script basename to match on) is preserved.
    Returns (merged_list, log_lines).
    """
    pkg_names = {hook_entry_script_name(e) for e in pkg_entries}
    pkg_names.discard(None)
    kept: list = []
    logs: list[str] = []
    for entry in user_entries:
        name = hook_entry_script_name(entry)
        if name is not None and name in pkg_names:
            logs.append(f"DROP hooks.{event_name} stale user entry ({name}, superseded by package)")
            continue
        kept.append(entry)
        logs.append(f"KEEP hooks.{event_name} user entry ({name or entry.get('type', 'entry')})")
    for entry in pkg_entries:
        name = hook_entry_script_name(entry)
        logs.append(f"APPLY hooks.{event_name} package entry ({name or entry.get('type', 'entry')})")
    return kept + list(pkg_entries), logs


def merge_hooks_object(pkg_hooks: dict, existing_hooks: dict) -> tuple[dict, list[str]]:
    """Deep-merge the `"hooks"` object: per-event array merge via
    merge_hook_event, plus untouched preservation of any event key the
    package doesn't define at all.
    """
    logs: list[str] = []
    merged = dict(existing_hooks)
    for event_name, pkg_entries in pkg_hooks.items():
        user_entries = existing_hooks.get(event_name, [])
        if not isinstance(user_entries, list):
            user_entries = []
        if not isinstance(pkg_entries, list):
            merged[event_name] = pkg_entries
            logs.append(f"REPLACE hooks.{event_name} (non-list value in package hooks.json, package wins)")
            continue
        merged_list, event_logs = merge_hook_event(event_name, user_entries, pkg_entries)
        merged[event_name] = merged_list
        logs.extend(event_logs)
    for event_name in existing_hooks:
        if event_name not in pkg_hooks:
            logs.append(f"KEEP hooks.{event_name} (event not defined by package, left untouched)")
    return merged, logs


# Recognised interpreter tokens: only these get rewritten. This is
# deliberately narrow so the rewrite never touches a command that merely
# happens to invoke a .py script through something else (e.g. a wrapper
# shell script) — only the literal "python"/"python3"/"py" leading token.
PYTHON_INTERPRETER_TOKENS = {"python", "python3", "py"}


def package_python_command() -> str:
    """OS-correct interpreter token for package-owned hooks/*.py scripts.

    Runs ON the user's own machine at install time, so platform.system() here
    reflects the machine that will actually execute the hook — unlike the
    package's shipped hooks.json, which has to pick one static token for
    everyone. Windows commonly has no bare `python`/`python3` on PATH (either
    nothing, or the Microsoft Store stub that prints "Python was not found");
    the `py` launcher is the one thing a standard Windows Python install
    reliably provides. Mac/Linux commonly ship `python3` but not a bare
    `python`.
    """
    return "py" if platform.system() == "Windows" else "python3"


def rewrite_package_python_interpreters(pkg_hooks: dict) -> int:
    """Rewrite the leading interpreter token of every PACKAGE-OWNED hook
    command that invokes a hooks/*.py script, to the OS-correct token for
    this machine (see package_python_command()).

    Only touches an entry whose `command` both (a) names a .py script via
    hook_entry_script_name — i.e. it is one of THIS package's own hook
    scripts, never a user-added entry with a different command shape, since
    this runs on `pkg_hooks` (the package's own template) before it is merged
    with any existing user hooks.json — and (b) already starts with a
    recognised Python interpreter token. Mutates `pkg_hooks` in place
    (each entry dict is rewritten by reference) and returns the count of
    commands changed, for logging.
    """
    interpreter = package_python_command()
    rewritten = 0
    for entries in pkg_hooks.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            cmd = entry.get("command")
            if not isinstance(cmd, str) or not cmd.strip():
                continue
            script = hook_entry_script_name(entry)
            if not script or not script.lower().endswith(".py"):
                continue
            tokens = cmd.split()
            if not tokens or tokens[0] not in PYTHON_INTERPRETER_TOKENS:
                continue
            if tokens[0] == interpreter:
                continue
            tokens[0] = interpreter
            entry["command"] = " ".join(tokens)
            rewritten += 1
    return rewritten


def merge_hooks_json(package_hooks: Path, dest_hooks: Path, dry_run: bool, strategy: str = "merge") -> None:
    """Install/merge hooks.json per --hooks-strategy.

    - "skip": never touch an existing hooks.json. A missing one is still
      seeded from the package so a fresh install has working hooks.
    - "replace": blind overwrite with the package's hooks.json (old
      behaviour), still backed up first if a destination file exists.
    - "merge" (default): deep-merge inside hooks.<event> arrays so package
      hooks stay current while user-owned hook entries and user-only event
      keys are preserved. Refuses to proceed (without touching the file) if
      the existing hooks.json isn't valid JSON, and tells the user how to
      force it with --hooks-strategy=replace.
    """
    if not package_hooks.exists():
        log("SKIP hooks.json (missing in package)")
        return
    pkg = json.loads(package_hooks.read_text(encoding="utf-8"))

    pkg_hook_events_for_rewrite = pkg.get("hooks")
    if isinstance(pkg_hook_events_for_rewrite, dict):
        n_rewritten = rewrite_package_python_interpreters(pkg_hook_events_for_rewrite)
        if n_rewritten:
            log(
                f"REWRITE {n_rewritten} package hook command(s) to use "
                f"'{package_python_command()}' interpreter (detected OS: {platform.system()})"
            )

    if not dest_hooks.exists():
        log(f"COPY hooks.json -> {dest_hooks}")
        if not dry_run:
            dest_hooks.parent.mkdir(parents=True, exist_ok=True)
            dest_hooks.write_text(json.dumps(pkg, indent=2) + "\n", encoding="utf-8")
        return

    if strategy == "skip":
        log(f"SKIP hooks.json (--hooks-strategy=skip; leaving {dest_hooks} untouched)")
        return

    # A destination file exists and we intend to touch it (merge or replace):
    # back it up first, unconditionally, before any write.
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_path = dest_hooks.parent / f"hooks.json.bak-{ts}"
    if dry_run:
        log(f"BACKUP {dest_hooks} -> {backup_path} (dry-run, not written)")
    else:
        shutil.copy2(dest_hooks, backup_path)
        log(f"BACKUP {dest_hooks} -> {backup_path}")

    if strategy == "replace":
        log(f"REPLACE hooks.json -> {dest_hooks} (--hooks-strategy=replace)")
        if not dry_run:
            dest_hooks.write_text(json.dumps(pkg, indent=2) + "\n", encoding="utf-8")
        return

    # strategy == "merge"
    try:
        existing = json.loads(dest_hooks.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        log(f"ERROR: {dest_hooks} is not valid JSON ({exc}); refusing to merge it.")
        log(
            f"Fix the file manually (a backup is at {backup_path}), or re-run with "
            "--hooks-strategy=replace to overwrite it anyway."
        )
        return
    if not isinstance(existing, dict):
        log(f"ERROR: {dest_hooks} does not contain a JSON object at the top level; refusing to merge it.")
        log(
            f"Fix the file manually (a backup is at {backup_path}), or re-run with "
            "--hooks-strategy=replace to overwrite it anyway."
        )
        return

    merged = dict(existing)
    pkg_hook_events = pkg.get("hooks")
    if isinstance(pkg_hook_events, dict):
        existing_hook_events = existing.get("hooks")
        if not isinstance(existing_hook_events, dict):
            existing_hook_events = {}
        merged_hooks_obj, hook_logs = merge_hooks_object(pkg_hook_events, existing_hook_events)
        for line in hook_logs:
            log(line)
        merged["hooks"] = merged_hooks_obj
    # Shallow merge for every other top-level key: package wins, unknown user keys preserved.
    for k, v in pkg.items():
        if k == "hooks":
            continue
        merged[k] = v
    log(f"MERGE hooks.json -> {dest_hooks}")
    if not dry_run:
        dest_hooks.write_text(json.dumps(merged, indent=2) + "\n", encoding="utf-8")


def migrate_legacy_actions(cursor_home: Path, package: Path, dry_run: bool) -> None:
    """Reuse the canonical migrate-once implementation from upgrade-workboard.

    Runs after seed_workstream(), so a freshly seeded empty ba-actions.json
    still receives legacy data once.
    """
    script = package / "tools" / "upgrade-workboard.py"
    if not script.exists():
        log(f"MIGRATE skip: missing canonical workboard upgrader {script}")
        return
    spec = importlib.util.spec_from_file_location("ba_upgrade_workboard", script)
    if spec is None or spec.loader is None:
        log(f"MIGRATE skip: cannot load canonical workboard upgrader {script}")
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup_root = cursor_home / "ba-assistant-backups" / f"legacy-actions-{ts}"
    for line in module.migrate_legacy_actions(cursor_home / "_workstream", backup_root, cursor_home, dry_run):
        log(line)


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
    generator_src = package / "tools" / "generate-workboard-canvas.py"
    if generator_src.exists():
        copy_file(generator_src, ws / "generate-workboard-canvas.py", dry_run)
    calendar_roll_src = package / "tools" / "roll-calendar-eod.py"
    if calendar_roll_src.exists():
        copy_file(calendar_roll_src, ws / "roll-calendar-eod.py", dry_run)
    calendar_sample_src = package / "_workstream" / "calendar-feed.sample.json"
    if calendar_sample_src.exists():
        copy_file(calendar_sample_src, ws / "calendar-feed.sample.json", dry_run)
    # These three already live under the package's own _workstream/ (not tools/) --
    # copy them by name the same way. Previously only README.md was copied from here;
    # the scripts themselves were referenced everywhere but never actually seeded.
    for name in ("regenerate-ba-actions-md.py", "extract-docx-text.py", "list-downloads-recent.py"):
        src = package / "_workstream" / name
        if src.exists():
            copy_file(src, ws / name, dry_run)


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
    version_file = package / "VERSION"
    version = version_file.read_text(encoding="utf-8").strip() if version_file.exists() else "unknown"
    payload = {
        "version": version,
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


def install(package: Path, cursor_home: Path, dry_run: bool, hooks_strategy: str = "merge") -> int:
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

    # Back up any existing install before the first destructive write below.
    # No-op on a fresh install (nothing exists yet to back up).
    backup_existing_install(cursor_home, package, dry_run)

    # Seed/migrate _workstream/learnings.md BEFORE copy_tree's rmtree can
    # destroy a pre-fix install's legacy in-tree copy. See seed_learnings().
    seed_learnings(cursor_home, package, dry_run)

    # Skills (full replace of ba-assistant tree). learnings.md is excluded:
    # its canonical runtime home is now _workstream/learnings.md (seeded
    # above), not this replaceable tree.
    copy_tree(
        skills_src,
        cursor_home / "skills" / "ba-assistant",
        dry_run,
        user_state=USER_STATE,
        exclude=EXCLUDE_FROM_SKILL_TREE,
    )

    # Optional Miro companion
    miro = package / "skills" / "miro-board-analysis"
    if miro.exists():
        copy_tree(miro, cursor_home / "skills" / "miro-board-analysis", dry_run)

    # Optional Confluence publishing companion
    confluence = package / "skills" / "publish-docs-to-confluence"
    if confluence.exists():
        copy_tree(confluence, cursor_home / "skills" / "publish-docs-to-confluence", dry_run)

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
        merge_hooks_json(hooks_dir / "hooks.json", cursor_home / "hooks.json", dry_run, strategy=hooks_strategy)

    seed_workstream(cursor_home, package, dry_run)
    migrate_legacy_actions(cursor_home, package, dry_run)
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
    ap.add_argument(
        "--hooks-strategy",
        choices=["merge", "skip", "replace"],
        default="merge",
        help=(
            "How to handle an existing hooks.json (default: merge). "
            "merge = deep-merge per hook event, package's own hooks win, user-added "
            "hooks and user-only event keys are preserved. "
            "skip = never touch an existing hooks.json. "
            "replace = blind overwrite with the package's hooks.json (old behaviour); "
            "an existing file is always backed up first regardless of strategy."
        ),
    )
    args = ap.parse_args()

    package = (args.package or package_root_from_script()).resolve()
    cursor_home = (args.cursor_home or (Path.home() / ".cursor")).resolve()
    dry_run = not args.apply
    if args.dry_run:
        dry_run = True

    return install(package, cursor_home, dry_run, hooks_strategy=args.hooks_strategy)


if __name__ == "__main__":
    sys.exit(main())
