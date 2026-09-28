#!/usr/bin/env python3
"""Local version history for initiative folders, so any change can be undone.

Initiative folders under ~/.cursor/initiatives are not synced or backed up.
This keeps a private git history inside each initiative folder. The BA never
needs to know git: they see "Undo the last change" and a plain-English list.

- No remote, no push. History never leaves the machine.
- Never blocks BA work. If git is missing or anything fails, it prints one
  "History: unavailable (...)" line and exits 0.
- Undo never deletes history: it restores the chosen earlier version and saves
  that as a new version ("Undo: ..."), so an undo can itself be undone.

  python3 ~/.cursor/_workstream/initiative-history.py ensure   --initiative <slug> | --all
  python3 ~/.cursor/_workstream/initiative-history.py snapshot --initiative <slug> --label "before /wrap"
  python3 ~/.cursor/_workstream/initiative-history.py history  --initiative <slug> [--limit 10]
  python3 ~/.cursor/_workstream/initiative-history.py undo     --initiative <slug> [--steps 1 | --to <id>]

--initiative also accepts a folder path or a SESSION-CONTEXT.md path.
Windows: use `py` instead of `python3`.
"""
from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

GIT_ID = ["-c", "user.name=BA Assistant", "-c", "user.email=ba-assistant@localhost",
          "-c", "commit.gpgsign=false", "-c", "core.hooksPath=", "-c", "core.autocrlf=false"]
MARK = "ba-assistant-history"   # written into .git/description so we only ever touch our own repos


def git_exe() -> str | None:
    return shutil.which("git")


def run_git(folder: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    proc = subprocess.run([git_exe(), *GIT_ID, *args], cwd=str(folder), capture_output=True, text=True,
                          encoding="utf-8", errors="replace", env=env, timeout=30)
    if check and proc.returncode != 0:
        raise RuntimeError((proc.stderr or proc.stdout).strip()[:300])
    return proc


# ---------- where initiatives are ----------

def config_initiatives_root(cursor_home: Path) -> str:
    text = ""
    for name in ("ba-assistant-config.mdc", "ba-profile.mdc"):
        try:
            text += (cursor_home / "rules" / name).read_text(encoding="utf-8", errors="ignore") + "\n"
        except OSError:
            pass
    m = re.search(r'^\s*initiativesRoot\s*:\s*["\']?([^"\'#\n]+)', text, re.M)
    value = m.group(1).strip() if m else ""
    return "" if not value or value.startswith("[") else os.path.expanduser(value)


def initiatives_root(cursor_home: Path) -> Path:
    env = os.path.expanduser(os.environ.get("BA_INITIATIVES_ROOT", "").strip())
    if env and os.path.isdir(env):   # a stale, missing folder is ignored
        return Path(env)
    return Path(config_initiatives_root(cursor_home) or cursor_home / "initiatives")


def all_initiatives(cursor_home: Path) -> list[Path]:
    root = initiatives_root(cursor_home)
    if not root.is_dir():
        return []
    found = []
    for ctx in root.rglob("SESSION-CONTEXT.md"):
        d = ctx.parent
        if ".git" in d.parts or any(p.endswith("(archived)") for p in d.parts):
            continue
        if d not in found:
            found.append(d)
    return sorted(found)


def resolve(cursor_home: Path, initiative: str) -> Path | None:
    p = Path(os.path.expanduser(initiative))
    if p.is_file():
        p = p.parent
    if p.is_dir():
        return p
    for d in all_initiatives(cursor_home):
        if d.name == initiative:
            return d
    return None


# ---------- history ----------

def is_ours(folder: Path) -> bool:
    desc = folder / ".git" / "description"
    try:
        return desc.read_text(encoding="utf-8", errors="ignore").strip() == MARK
    except OSError:
        return False


def ensure(folder: Path) -> str:
    """Start a history for this folder if it has none. Never adopts someone else's repo."""
    if (folder / ".git").exists():
        return "exists" if is_ours(folder) else "foreign"
    # Inside a git repo of the BA's own (e.g. a versioned ~/.cursor or workspace)? Leave it:
    # a nested repo would change how their repo sees this folder.
    if run_git(folder, "rev-parse", "--show-toplevel", check=False).returncode == 0:
        return "foreign"
    run_git(folder, "init", "-q")
    (folder / ".git" / "description").write_text(MARK + "\n", encoding="utf-8")
    run_git(folder, "add", "-A")
    run_git(folder, "commit", "-q", "--allow-empty", "-m", "History started")
    return "created"


def snapshot(folder: Path, label: str) -> str:
    """Save the folder as a version if anything changed. 'saved', 'clean' or 'no-history'."""
    if not is_ours(folder):
        return "no-history"
    run_git(folder, "add", "-A")
    if not run_git(folder, "status", "--porcelain").stdout.strip():
        return "clean"
    run_git(folder, "commit", "-q", "-m", label[:200] or "Saved")
    return "saved"


def versions(folder: Path, limit: int = 20) -> list[dict]:
    out = run_git(folder, "log", f"-n{limit}", "--format=%h%x09%ct%x09%s", "--shortstat").stdout
    rows, cur = [], None
    for line in out.splitlines():
        if "\t" in line:
            vid, ts, label = line.split("\t", 2)
            cur = {"id": vid, "when": datetime.fromtimestamp(int(ts)), "label": label, "files": 0}
            rows.append(cur)
        elif cur is not None and "changed" in line:
            m = re.search(r"(\d+) files? changed", line)
            cur["files"] = int(m.group(1)) if m else 0
    return rows


def ago(when: datetime) -> str:
    secs = int((datetime.now() - when).total_seconds())
    if secs < 90:
        return "just now"
    if secs < 3600:
        return f"{secs // 60} min ago"
    if secs < 86400:
        return f"{secs // 3600} h ago"
    return when.strftime("%d %b %H:%M")


def changed_files(folder: Path, older: str, newer: str) -> list[str]:
    return [l for l in run_git(folder, "diff", "--name-only", older, newer).stdout.splitlines() if l.strip()]


def undo(folder: Path, steps: int = 1, to: str = "") -> str:
    if not is_ours(folder):
        return "History: unavailable (this initiative has no history yet; run ensure)"
    # Pick the target from the SAVED versions first: "undo the last change" means the
    # last saved change (a capture, debrief, /wrap, reply), not edits made since.
    rows = versions(folder, limit=max(steps + 1, 50))
    # Then keep any unsaved edits as their own version, so undoing again brings them back.
    if snapshot(folder, "Before undo (edits not saved yet)") == "saved":
        rows = [versions(folder, limit=1)[0]] + rows
        steps += 1
    if to:
        target = next((r for r in rows if r["id"].startswith(to)), None)
        if target is None:
            return f"Undo: FAIL (no version {to} in the last {len(rows)} versions)"
    else:
        if len(rows) <= steps:
            return "Undo: nothing to undo (this is the first version)"
        target = rows[steps]
    head = rows[0]["id"]
    files = changed_files(folder, target["id"], head)
    if not files:
        return "Undo: nothing to undo (files already match that version)"
    run_git(folder, "read-tree", "-u", "--reset", target["id"])
    run_git(folder, "commit", "-q", "-m", f"Undo: back to \"{target['label']}\" ({target['id']})")
    shown = ", ".join(files[:8]) + (f" and {len(files) - 8} more" if len(files) > 8 else "")
    return (f"Undo: PASS. Put back {len(files)} file(s) as they were at \"{target['label']}\" "
            f"({ago(target['when'])}): {shown}. To reverse this undo, undo again.")


# ---------- CLI ----------

def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description="Local undo history for initiative folders")
    ap.add_argument("action", choices=("ensure", "snapshot", "history", "undo"))
    ap.add_argument("--initiative", help="slug, folder or SESSION-CONTEXT.md path")
    ap.add_argument("--all", action="store_true", help="every initiative (ensure / snapshot)")
    ap.add_argument("--label", default="Saved")
    ap.add_argument("--existing-only", action="store_true",
                    help="snapshot: only folders that already have a history (never start one)")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--steps", type=int, default=1)
    ap.add_argument("--to", default="")
    ap.add_argument("--cursor-home", default=str(Path.home() / ".cursor"))
    args = ap.parse_args(argv)
    home = Path(os.path.expanduser(args.cursor_home))

    if not git_exe():
        print("History: unavailable (git is not installed, so changes can't be undone automatically; "
              "BA work carries on normally)")
        return 0
    if args.all:
        folders = all_initiatives(home)
    elif args.initiative:
        f = resolve(home, args.initiative)
        if f is None:
            print(f"History: unavailable (initiative '{args.initiative}' not found)")
            return 0
        folders = [f]
    else:
        print("History: FAIL (give --initiative <slug> or --all)")
        return 1

    try:
        if args.action == "ensure":
            for f in folders:
                state = ensure(f)
                print({"created": f"History: started for {f.name}", "exists": f"History: already on for {f.name}",
                       "foreign": f"History: skipped {f.name} (it is already a git repo of your own; left alone)"}[state])
        elif args.action == "snapshot":
            for f in folders:
                if not is_ours(f) and not (f / ".git").exists() and not args.existing_only:
                    ensure(f)
                state = snapshot(f, args.label)
                if state == "saved":
                    print(f"History: saved {f.name} ({args.label})")
        elif args.action == "history":
            f = folders[0]
            if not is_ours(f):
                print(f"History: none yet for {f.name}")
                return 0
            print(f"Recent versions of {f.name} (newest first):")
            for i, r in enumerate(versions(f, args.limit)):
                files = f", {r['files']} file(s)" if r["files"] else ""
                print(f"  {i}. {ago(r['when'])}: {r['label']}{files}   [id {r['id']}]")
            print("To undo the latest change: undo --steps 1. To go back further: undo --to <id>.")
        elif args.action == "undo":
            print(undo(folders[0], args.steps, args.to))
    except Exception as exc:          # history must never break BA work
        print(f"History: unavailable ({exc})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
