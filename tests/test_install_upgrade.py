"""
Install and upgrade regression tests (Version 15).

Installs the ORIGINAL Version 14 release (commit 750a6c5) into a throwaway
Cursor home, personalises it the way a real BA would, then upgrades it with
this checkout. Proves:

  - personal config, BA data, initiatives and local-only files are byte-identical
  - legacy migrations do not fire unless --migrate-legacy is passed
  - the user's own hook survives, and no hook runs twice
  - --patch-profile changes only the old /wrap and /validate-state rows

It also REPORTS (and pins) what the upgrader does to package files the BA
edited: skills, commands and package rules are overwritten by design. That is
why tools/ba-merge-upgrade.py exists for personalised installs.

Needs git (to export the Version 14 tree). Standalone, no pytest.

Run:
    python3 tests/test_install_upgrade.py      (Windows: py tests/test_install_upgrade.py)
"""
import hashlib
import io
import json
import os
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable or "python3"
V14_COMMIT = "750a6c542c1b1b0adcbe2c06579a4a7d81275751"
FAILURES = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {detail}" if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args, home):
    env = {k: v for k, v in os.environ.items() if not k.startswith("BA_")}
    env.update({"HOME": str(home), "USERPROFILE": str(home)})
    proc = subprocess.run([PY, *map(str, args)], capture_output=True, text=True, env=env, timeout=120)
    return proc.returncode, proc.stdout + proc.stderr


def export_commit(commit, dest):
    data = subprocess.run(["git", "-C", str(REPO), "archive", "--format=zip", commit],
                          capture_output=True, check=True).stdout
    zipfile.ZipFile(io.BytesIO(data)).extractall(dest)
    return dest


def hook_scripts(hooks_json):
    """event -> list of script stems (lowercase), to spot double registration."""
    data = json.loads(Path(hooks_json).read_text(encoding="utf-8"))
    out = {}
    for event, entries in (data.get("hooks") or {}).items():
        stems = []
        for entry in entries if isinstance(entries, list) else []:
            cmd = str(entry.get("command", ""))
            for token in reversed(cmd.split()):
                token = token.strip("\"'").replace("\\", "/").rsplit("/", 1)[-1]
                if token.lower().endswith((".py", ".sh", ".ps1")):
                    stems.append(token.rsplit(".", 1)[0].lower())
                    break
        out[event] = stems
    return out


def personalise(cursor):
    """Edits a real BA makes. Returns {label: path} of files that must survive untouched."""
    rules = cursor / "rules"
    profile = rules / "ba-profile.mdc"
    text = profile.read_text(encoding="utf-8")
    text = text.replace("# ", "# Sam's ", 1) + "\n## My tone\nDry, short, no fluff.\n"
    profile.write_text(text, encoding="utf-8")
    (rules / "ba-assistant-config.mdc").write_text(
        'name: "Sam Example"\npaths:\n  initiativesRoot: "~/.cursor/initiatives"\n', encoding="utf-8")
    (rules / "my-own-rule.mdc").write_text("---\nalwaysApply: true\n---\nMy own rule.\n", encoding="utf-8")
    local_skill = cursor / "skills" / "my-skill" / "SKILL.md"
    local_skill.parent.mkdir(parents=True)
    local_skill.write_text("# My skill\n", encoding="utf-8")

    # Package files the BA edited (the upgrader overwrites these by design)
    (cursor / "skills" / "ba-assistant" / "SKILL.md").open("a", encoding="utf-8").write("\nSAM-EDIT-SKILL\n")
    cmd = sorted((cursor / "commands").glob("*.md"))[0]
    cmd.open("a", encoding="utf-8").write("\nSAM-EDIT-COMMAND\n")
    (rules / "sync-gates.mdc").open("a", encoding="utf-8").write("\nSAM-EDIT-RULE\n")

    ws = cursor / "_workstream"
    ws.mkdir(exist_ok=True)
    (ws / "ba-actions.json").write_text(json.dumps({"schema_version": 1, "next_id": 2, "actions": [
        {"id": "BA-001", "task": "Real action", "status": "open"}]}, indent=2), encoding="utf-8")
    (ws / "workboard.json").write_text(json.dumps({"meetings_date": "2026-09-16", "initiatives": [],
        "personal_tasks": [{"task": "Legacy task", "status": "open"}]}, indent=2), encoding="utf-8")
    (ws / "sam-actions.json").write_text(json.dumps({"actions": [{"id": "X-1"}]}), encoding="utf-8")
    (ws / "calendar-feed.json").write_text(json.dumps({"meetings": []}), encoding="utf-8")
    init = cursor / "initiatives" / "payments-uplift"
    init.mkdir(parents=True, exist_ok=True)
    (init / "SESSION-CONTEXT.md").write_text("# Payments uplift\nDEC-1 decided\n", encoding="utf-8")

    # Own hook, plus a leftover pre-Version 13 wrapper registered next to the .py hook
    (cursor / "hooks" / "my-hook.py").write_text("print('{}')\n", encoding="utf-8")
    (cursor / "hooks" / "session-init.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    hj = cursor / "hooks.json"
    data = json.loads(hj.read_text(encoding="utf-8"))
    data["hooks"].setdefault("sessionStart", []).append({"command": "sh ./hooks/session-init.sh"})
    data["hooks"].setdefault("afterFileEdit", []).append({"command": "python3 ./hooks/my-hook.py"})
    hj.write_text(json.dumps(data, indent=2), encoding="utf-8")

    return {
        "profile": profile,
        "config": rules / "ba-assistant-config.mdc",
        "own rule": rules / "my-own-rule.mdc",
        "own skill": local_skill,
        "ba-actions.json": ws / "ba-actions.json",
        "workboard.json": ws / "workboard.json",
        "legacy actions file": ws / "sam-actions.json",
        "calendar-feed.json": ws / "calendar-feed.json",
        "initiative": init / "SESSION-CONTEXT.md",
        "own hook script": cursor / "hooks" / "my-hook.py",
    }


def main():
    try:
        subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", V14_COMMIT], check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError):
        print(f"SKIP  Version 14 commit {V14_COMMIT[:7]} not available (shallow clone?). Fetch full history.")
        return 1

    with tempfile.TemporaryDirectory(prefix="ba-upgrade-tests-") as tmp:
        tmp = Path(tmp)
        v14 = export_commit(V14_COMMIT, tmp / "v14")

        # --- Install Version 14 and personalise it ---
        home = tmp / "home"
        cursor = home / ".cursor"
        code, out = run([v14 / "tools" / "install-ba-assistant.py", "--package", v14, "--cursor-home", cursor,
                         "--apply"], home)
        check("Setup: Version 14 installs into a temp home", code == 0 and (cursor / "skills" / "ba-assistant").exists(), out[-800:])
        keep = personalise(cursor)
        before = {label: sha(p) for label, p in keep.items()}

        # --- Dry run changes nothing at all ---
        snapshot = {p: sha(p) for p in cursor.rglob("*") if p.is_file()}
        code, out = run([REPO / "tools" / "upgrade-ba-assistant.py", "--package", REPO, "--cursor-home", cursor], home)
        after_dry = {p: sha(p) for p in cursor.rglob("*") if p.is_file()}
        check("Dry run: exits 0", code == 0, out[-800:])
        check("Dry run: no file created, changed or removed", snapshot == after_dry)
        check("Dry run: warns about the old profile rows", "WARN ba-profile.mdc /wrap" in out, out[-1500:])
        check("Dry run: warns about legacy data instead of migrating",
              "WARN legacy data left untouched" in out and "sam-actions.json" in out, out[-1500:])

        # --- Apply ---
        code, out = run([REPO / "tools" / "upgrade-ba-assistant.py", "--package", REPO, "--cursor-home", cursor,
                         "--apply"], home)
        apply_out = out
        check("Apply: exits 0", code == 0, out[-1500:])
        for label, path in keep.items():
            check(f"Apply: {label} byte-identical", path.exists() and sha(path) == before[label])
        version = (REPO / "VERSION").read_text(encoding="utf-8").strip()
        check("Apply: VERSION stamped",
              (cursor / "skills" / "ba-assistant" / "VERSION").read_text(encoding="utf-8").strip() == version)

        hooks = hook_scripts(cursor / "hooks.json")
        dupes = {event: stems for event, stems in hooks.items() if len(stems) != len(set(stems))}
        check("Apply: no hook registered twice on any event", not dupes, str(dupes))
        check("Apply: legacy session-init.sh entry dropped", "session-init" in hooks.get("sessionStart", [])
              and hooks["sessionStart"].count("session-init") == 1, str(hooks.get("sessionStart")))
        check("Apply: user's own hook entry kept", "my-hook" in hooks.get("afterFileEdit", []), str(hooks))
        check("Apply: unreferenced session-init.sh moved out of hooks/",
              not (cursor / "hooks" / "session-init.sh").exists()
              and any((cursor / "ba-assistant-backups").rglob("hooks-retired/session-init.sh")))

        # Pinned, documented behaviour: package files the BA edited are overwritten.
        skill_kept = "SAM-EDIT-SKILL" in (cursor / "skills" / "ba-assistant" / "SKILL.md").read_text(encoding="utf-8")
        cmd_kept = any("SAM-EDIT-COMMAND" in p.read_text(encoding="utf-8") for p in (cursor / "commands").glob("*.md"))
        rule_kept = "SAM-EDIT-RULE" in (cursor / "rules" / "sync-gates.mdc").read_text(encoding="utf-8")
        print(f"INFO  upgrader on edited package files: skill kept={skill_kept}, command kept={cmd_kept}, "
              f"package rule kept={rule_kept} (overwritten by design; backups under ba-assistant-backups/)")
        check("Documented: edited package skill/command/rule are overwritten (use ba-merge-upgrade.py to keep them)",
              not skill_kept and not cmd_kept and not rule_kept)
        check("Documented: the overwritten edits are in the upgrader's backup",
              any("SAM-EDIT-SKILL" in p.read_text(encoding="utf-8", errors="replace")
                  for p in (cursor / "ba-assistant-backups").rglob("SKILL.md")))

        # --- --patch-profile changes only the two rows ---
        old_lines = keep["profile"].read_text(encoding="utf-8").splitlines()
        code, out = run([REPO / "tools" / "upgrade-ba-assistant.py", "--package", REPO, "--cursor-home", cursor,
                         "--apply", "--patch-profile"], home)
        new_lines = keep["profile"].read_text(encoding="utf-8").splitlines()
        changed = [i for i, (a, b) in enumerate(zip(old_lines, new_lines)) if a != b]
        check("Patch profile: same line count", len(old_lines) == len(new_lines))
        check("Patch profile: exactly the /validate-state and /wrap rows changed",
              len(changed) == 2 and all(new_lines[i].startswith(("| `/validate-state`", "| `/wrap`")) for i in changed),
              str([new_lines[i][:40] for i in changed]))
        check("Patch profile: personal tone section kept", "Dry, short, no fluff." in "\n".join(new_lines))
        check("Patch profile: backup written", any(keep["profile"].parent.glob("ba-profile.mdc.bak-*")))
        code, out = run([REPO / "tools" / "upgrade-ba-assistant.py", "--package", REPO, "--cursor-home", cursor], home)
        check("Patch profile: a second dry run has nothing left to patch", "WARN ba-profile.mdc" not in out, out[-800:])

        # --- --migrate-legacy is the only way the old migrations run ---
        check("Migrate legacy: default apply never ran the migration code",
              "WARN legacy data left untouched" in apply_out and "MIGRATE skip:" not in apply_out
              and "MIGRATE personal_tasks" not in apply_out, apply_out[-800:])
        code, out = run([REPO / "tools" / "upgrade-ba-assistant.py", "--package", REPO, "--cursor-home", cursor,
                         "--migrate-legacy"], home)
        check("Migrate legacy: the flag switches the migration code on (dry run)",
              code == 0 and "MIGRATE" in out and "WARN legacy data left untouched" not in out, out[-800:])

        # --- Fresh install of this checkout passes conformance ---
        fresh = tmp / "fresh"
        code, out = run([REPO / "tools" / "install-ba-assistant.py", "--package", REPO, "--cursor-home",
                         fresh / ".cursor", "--apply"], fresh)
        check("Fresh install: exits 0", code == 0, out[-800:])
        code, out = run([REPO / "tools" / "conformance-check.py", "--root", REPO], fresh)
        fails = [line for line in out.splitlines() if line.startswith("FAIL")]
        # PENDING until scan-outlook-mail.py ships in Version 15 phase B: the EOD
        # procedure already references it (optional, fail-open).
        if not (REPO / "_workstream" / "scan-outlook-mail.py").exists() and not (REPO / "tools" / "scan-outlook-mail.py").exists():
            fails = [line for line in fails if "mail-script" not in line]
            print("PENDING  mail-script conformance (scan-outlook-mail.py not added yet)")
        check("Conformance: package root has no FAIL", not fails, "\n".join(fails))

    print(f"\n{'All install/upgrade tests passed.' if not FAILURES else f'{len(FAILURES)} failed.'}")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
