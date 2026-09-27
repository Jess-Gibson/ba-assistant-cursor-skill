#!/usr/bin/env python3
"""
Personalised-install upgrade helper (Version 15).

For a BA who has customised their installed BA Assistant (edited skills, own
rules, own skills, tone) and wants a new package version WITHOUT losing any of
it. The plain upgrader overwrites package files; this tool wraps it in a safe,
reviewable flow:

    backup -> stage -> classify -> (decide) -> apply-staging -> deploy-plan -> deploy
                                                                   rollback (any time after backup)

What this tool decides for you: nothing. It sorts files, and for behaviour
files you and the new version both changed it runs git's line merge
(git merge-file). A clean result is written to <session>/merged/ and still
needs your sign-off (auto_merged_reviewed in decisions.json) before anything
is built; an overlap becomes a question for a person (or Cursor, with you
approving) to resolve by hand.

Your naming is kept. The public package is generic (ba-actions, [BA name]);
your install may use your own names (for example alex-actions). Give classify a
rules.json of {"local": "...", "generic": "..."} pairs (the same pairs your
sync-to-repo skill uses) and every file taken from the new version is written
in YOUR naming, file names included. Your data files are never touched.

Everything is standard-library Python and runs on Windows, macOS and Linux.
Windows: use `py` instead of `python3`, or tools/ba-merge-upgrade.ps1.

Steps (see docs/PERSONALISED-UPGRADE.md for the full walkthrough):

  python3 tools/ba-merge-upgrade.py backup
      Hash manifest + zip + zip test + restore rehearsal of your install.
      Prints the session folder (default ~/ba-assistant-upgrade-<timestamp>).

  python3 tools/ba-merge-upgrade.py stage --session <dir>
      Copies the verified snapshot into <session>/staging (a throwaway Cursor home).

  python3 tools/ba-merge-upgrade.py classify --session <dir> --base <V14 checkout> --new <V15 checkout>
                                    [--rules rules.json]
      Three-way comparison. Writes report.md, classification.json and a
      decisions.json to fill in.

  python3 tools/ba-merge-upgrade.py apply-staging --session <dir>
      Builds the upgraded install in staging from your decisions: new files in
      your naming, your files kept, merged files copied in, hooks.json merged
      hook by hook. Checks your data in staging is unchanged.

  python3 tools/ba-merge-upgrade.py deploy-plan --session <dir>
      Lists exactly which files would change in your real install.

  python3 tools/ba-merge-upgrade.py deploy --session <dir> --plan-sha <sha from deploy-plan> [--include-canvas]
      Drift check, copy only planned files, verify, auto-rollback on failure.

  python3 tools/ba-merge-upgrade.py rollback --session <dir>
      Puts every backed-up file back byte for byte (moves the current files
      aside first). Symlinks and cache folders are listed, not restored.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from datetime import datetime
from pathlib import Path, PurePosixPath

TOOL_VERSION = 1

# Top-level entries of the Cursor home that belong to BA Assistant and get
# backed up. Anything else (extensions, caches, other tools) is never touched.
HOME_INCLUDE = (
    "skills",
    "rules",
    "commands",
    "hooks",
    "hooks.json",
    "_workstream",
    "canvases",
    "initiatives",
    ".ba-assistant-installed.json",
)
# Never backed up or deployed: old upgrade backups and interpreter caches.
EXCLUDE_DIR_NAMES = {"__pycache__", "ba-assistant-backups", ".git", "node_modules"}
EXCLUDE_FILE_SUFFIXES = (".pyc",)
BACKUP_NAME_RE = re.compile(r"\.bak-\d{8}-\d{6}$")

PERSONAL_FILES = {"rules/ba-profile.mdc", "rules/ba-assistant-config.mdc"}
# Top-level folders never searched for initiatives (Cursor's own, or huge).
NOT_INITIATIVE_DIRS = {"extensions", "projects", "ai-tracking", "worktrees", "plugins", "logs"}

# Filled from session.json: extra top-level folders of the Cursor home that
# hold initiatives (for example a folder not called "initiatives"). They are
# backed up, staged and treated as data, never deployed.
CTX: dict = {"extra_home_dirs": (), "personal_files": set(PERSONAL_FILES)}


def home_includes() -> tuple[str, ...]:
    return HOME_INCLUDE + tuple(d for d in CTX["extra_home_dirs"] if d not in HOME_INCLUDE)


def staging_home(session: Path) -> Path:
    """Staging is a whole fake user home, so tools can run against it with
    HOME/USERPROFILE pointed here (see the run command)."""
    return session / "stage-home"


def staging_dir(session: Path) -> Path:
    return staging_home(session) / ".cursor"
VOICE_HINTS = ("voice", "tone")
GENERATED_FILES = {"canvases/ba-workboard.canvas.tsx"}
DATA_SUFFIXES = (".json", ".md", ".txt", ".csv")


# --------------------------------------------------------------------------
# Small helpers
# --------------------------------------------------------------------------

def say(msg: str = "") -> None:
    try:
        print(msg)
    except UnicodeEncodeError:
        print(msg.encode("ascii", "replace").decode("ascii"))


def die(msg: str) -> "NoReturn":  # noqa: F821
    say(f"STOP: {msg}")
    raise SystemExit(1)


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def posix(rel: Path | PurePosixPath | str) -> str:
    return str(rel).replace("\\", "/")


def is_excluded(rel_parts: tuple[str, ...]) -> bool:
    if any(p in EXCLUDE_DIR_NAMES for p in rel_parts):
        return True
    name = rel_parts[-1] if rel_parts else ""
    return name.endswith(EXCLUDE_FILE_SUFFIXES) or bool(BACKUP_NAME_RE.search(name))


def walk_files(root: Path) -> tuple[dict[str, Path], list[str]]:
    """{posix relative path: absolute path} for regular files under root,
    plus a list of symlinks that were skipped (never followed)."""
    files: dict[str, Path] = {}
    skipped: list[str] = []
    if root.is_file():
        return {root.name: root}, skipped
    if not root.exists():
        return files, skipped
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        d = Path(dirpath)
        keep_dirs = []
        for name in dirnames:
            full = d / name
            rel_parts = full.relative_to(root).parts
            if full.is_symlink():
                skipped.append(posix(full.relative_to(root)))
            elif not is_excluded(rel_parts):
                keep_dirs.append(name)
        dirnames[:] = keep_dirs
        for name in filenames:
            full = d / name
            rel_parts = full.relative_to(root).parts
            if is_excluded(rel_parts):
                continue
            if full.is_symlink():
                skipped.append(posix(full.relative_to(root)))
                continue
            files[posix(full.relative_to(root))] = full
    return files, skipped


def load_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_config_value(cursor_home: Path, key: str) -> str:
    """First `key:` found in ba-assistant-config.mdc, then any other rule file
    (a profile may hold it under a personal file name)."""
    rules = cursor_home / "rules"
    if not rules.exists():
        return ""
    files = [rules / "ba-assistant-config.mdc"] + sorted(p for p in rules.glob("*.mdc") if p.name != "ba-assistant-config.mdc")
    for cfg in files:
        if not cfg.exists():
            continue
        for line in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
            m = re.match(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", line)
            if m:
                value = m.group(1).split(" #", 1)[0].strip().strip("\"'")
                if value and not value.startswith("["):
                    return value
    return ""


def detect_initiative_dirs(cursor_home: Path) -> list[str]:
    """Top-level folders of the Cursor home (other than the standard ones) that
    contain a SESSION-CONTEXT.md within three levels. No names are assumed."""
    found = []
    for top in sorted(cursor_home.iterdir()) if cursor_home.exists() else []:
        if not top.is_dir() or top.is_symlink() or top.name in HOME_INCLUDE or top.name in NOT_INITIATIVE_DIRS:
            continue
        if top.name in EXCLUDE_DIR_NAMES or top.name.startswith("."):
            continue
        base_depth = len(top.parts)
        for dirpath, dirnames, filenames in os.walk(top):
            if "SESSION-CONTEXT.md" in filenames:
                found.append(top.name)
                break
            if len(Path(dirpath).parts) - base_depth >= 3:
                dirnames[:] = []
            else:
                dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIR_NAMES]
    configured = read_config_value(cursor_home, "initiativesRoot")
    if configured:
        p = Path(os.path.expanduser(configured))
        try:
            rel = p.resolve().relative_to(cursor_home.resolve())
            if rel.parts and rel.parts[0] not in HOME_INCLUDE and rel.parts[0] not in found:
                found.append(rel.parts[0])
        except (ValueError, OSError):
            pass
    return found


def load_session(session: Path) -> dict:
    meta = load_json(session / "session.json")
    if not meta:
        die(f"{session} is not a ba-merge-upgrade session folder (no session.json). Run backup first.")
    CTX["extra_home_dirs"] = tuple(meta.get("extra_home_dirs") or ())
    return meta


# --------------------------------------------------------------------------
# Roots: the Cursor home plus an initiatives folder that lives elsewhere
# --------------------------------------------------------------------------

def collect_roots(cursor_home: Path, extra: list[str]) -> dict[str, Path]:
    roots = {"home": cursor_home}
    candidates = []
    init_root = read_config_value(cursor_home, "initiativesRoot")
    if init_root:
        candidates.append(init_root)
    candidates.extend(extra or [])
    n = 0
    for c in candidates:
        p = Path(os.path.expanduser(c)).resolve()
        if not p.exists():
            continue
        try:
            p.relative_to(cursor_home.resolve())
            continue  # already inside the Cursor home
        except ValueError:
            pass
        if any(p == r for r in roots.values()):
            continue
        n += 1
        roots[f"ext{n}"] = p
    return roots


def root_files(label: str, root: Path) -> tuple[dict[str, Path], list[str]]:
    """Manifest keys are '<label>/<path>'. For home, only the included entries."""
    files: dict[str, Path] = {}
    skipped: list[str] = []
    if label == "home":
        for entry in home_includes():
            p = root / entry
            if p.is_symlink():
                skipped.append(f"home/{entry}")
                continue
            if p.is_file():
                files[f"home/{entry}"] = p
            elif p.is_dir():
                sub, sk = walk_files(p)
                files.update({f"home/{entry}/{k}": v for k, v in sub.items()})
                skipped.extend(f"home/{entry}/{s}" for s in sk)
    else:
        sub, sk = walk_files(root)
        files.update({f"{label}/{k}": v for k, v in sub.items()})
        skipped.extend(f"{label}/{s}" for s in sk)
    return files, skipped


# --------------------------------------------------------------------------
# backup
# --------------------------------------------------------------------------

def cmd_backup(args) -> int:
    cursor_home = Path(os.path.expanduser(args.cursor_home)).resolve()
    if not (cursor_home / "skills").exists():
        die(f"{cursor_home} does not look like a Cursor home with BA Assistant installed.")
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    session = Path(os.path.expanduser(args.session)).resolve() if args.session else Path.home() / f"ba-assistant-upgrade-{ts}"
    if (session / "session.json").exists():
        die(f"{session} already holds a session. Use a new --session folder.")
    session.mkdir(parents=True, exist_ok=True)

    roots = collect_roots(cursor_home, args.extra)
    CTX["extra_home_dirs"] = tuple(detect_initiative_dirs(cursor_home))
    say("Backing up (explicit include list):")
    for label, root in roots.items():
        if label == "home":
            present = [e for e in home_includes() if (root / e).exists()]
            say(f"  {label}: {root}")
            say(f"      includes: {', '.join(present)}")
            if CTX["extra_home_dirs"]:
                say(f"      initiative folders found (kept as data, never changed): {', '.join(CTX['extra_home_dirs'])}")
        else:
            say(f"  {label}: {root} (initiatives or extra folder outside the Cursor home)")
    say(f"  excludes: {', '.join(sorted(EXCLUDE_DIR_NAMES))}, *.pyc, *.bak-<timestamp> files,"
        " and everything else in the Cursor home (extensions, caches, other tools)")

    all_files: dict[str, Path] = {}
    skipped: list[str] = []
    for label, root in roots.items():
        f, s = root_files(label, root)
        all_files.update(f)
        skipped.extend(s)

    manifest = {}
    for key, path in sorted(all_files.items()):
        manifest[key] = {"sha256": sha256_file(path), "size": path.stat().st_size}

    zip_path = session / "backup.zip"
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED, allowZip64=True) as zf:
        for key, path in sorted(all_files.items()):
            zf.write(path, key)
    with zipfile.ZipFile(zip_path) as zf:
        bad = zf.testzip()
    if bad:
        die(f"zip integrity test failed at {bad}. Nothing was changed. Delete {session} and retry.")

    # Restore rehearsal: extract and re-hash every file. The result is kept as
    # the read-only snapshot that classify and stage use.
    snapshot = session / "snapshot"
    with zipfile.ZipFile(zip_path) as zf:
        zf.extractall(snapshot)
    mismatches = []
    for key, meta in manifest.items():
        p = snapshot / key
        if not p.exists() or sha256_file(p) != meta["sha256"]:
            mismatches.append(key)
    extracted, _ = walk_files(snapshot)
    extra_in_zip = sorted(set(extracted) - set(manifest))
    if mismatches or extra_in_zip:
        die(f"restore rehearsal failed: {len(mismatches)} mismatched, {len(extra_in_zip)} unexpected. "
            f"First: {(mismatches or extra_in_zip)[:5]}")

    write_json(session / "manifest.json", {
        "created": datetime.now().isoformat(timespec="seconds"),
        "roots": {k: str(v) for k, v in roots.items()},
        "files": manifest,
        "skipped_symlinks": skipped,
    })
    (session / "manifest.sha256").write_text(
        "".join(f"{m['sha256']}  {k}\n" for k, m in sorted(manifest.items())), encoding="utf-8")
    write_json(session / "session.json", {
        "tool_version": TOOL_VERSION,
        "created": datetime.now().isoformat(timespec="seconds"),
        "cursor_home": str(cursor_home),
        "roots": {k: str(v) for k, v in roots.items()},
        "extra_home_dirs": list(CTX["extra_home_dirs"]),
    })
    write_rollback_doc(session, roots)

    say("")
    say(f"Backed up {len(manifest)} files. Zip test: OK. Restore rehearsal: {len(manifest)}/{len(manifest)} hashes match.")
    if skipped:
        say(f"NOTE {len(skipped)} symlink(s) were not followed or backed up: {skipped[:5]}")
    say(f"Session folder: {session}")
    say(f"Rollback steps: {session / 'ROLLBACK.md'}")
    say("Next: stage --session \"" + str(session) + "\"")
    return 0


def write_rollback_doc(session: Path, roots: dict[str, Path]) -> None:
    py = "py" if os.name == "nt" else "python3"
    lines = [
        "# Rollback",
        "",
        "Puts every backed-up BA Assistant file back byte for byte, as it was when this backup was taken.",
        "Symlinks and cache folders (__pycache__) were not backed up; they are listed in manifest.json.",
        "",
        "## One command",
        "",
        "```",
        f'{py} tools/ba-merge-upgrade.py rollback --session "{session}"',
        "```",
        "",
        "It moves the current BA Assistant files aside to `rolled-back-<timestamp>/` in this",
        "folder (so files added by the new version cannot linger), extracts `backup.zip`,",
        "then re-hashes every file against `manifest.json`.",
        "",
        "## By hand (if the tool itself is broken)",
        "",
        "1. Close Cursor.",
        "2. Move these out of the way (do not delete them yet):",
    ]
    for label, root in roots.items():
        if label == "home":
            lines += [f"   - `{root / e}`" for e in home_includes() if (root / e).exists()]
        else:
            lines.append(f"   - `{root}`")
    lines += [
        "3. Unzip `backup.zip`. Inside it, `home/` goes back into your Cursor home and each",
        "   `extN/` goes back to the folder listed below.",
        "",
        "| Zip folder | Restores to |",
        "|---|---|",
    ]
    lines += [f"| `{label}/` | `{root}` |" for label, root in roots.items()]
    lines += ["", "4. Check hashes against `manifest.sha256` (optional)."]
    (session / "ROLLBACK.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# stage
# --------------------------------------------------------------------------

def cmd_stage(args) -> int:
    session = Path(os.path.expanduser(args.session)).resolve()
    load_session(session)
    src = session / "snapshot" / "home"
    staging = staging_dir(session)
    if staging_home(session).exists():
        if not args.fresh:
            die(f"{staging} already exists. Pass --fresh to rebuild it from the snapshot.")
        shutil.rmtree(staging_home(session))
        (session / "staging-result.json").unlink(missing_ok=True)
    staging.parent.mkdir(parents=True)
    shutil.copytree(src, staging)
    manifest = load_json(session / "manifest.json")["files"]
    bad = [k for k, m in manifest.items() if k.startswith("home/")
           and sha256_file(staging / k[len("home/"):]) != m["sha256"]]
    if bad:
        die(f"staging copy does not match the backup: {bad[:5]}")
    say(f"Staging ready: {staging}")
    say("It is a full copy of your install. Nothing in your real Cursor home was touched.")
    external = {k: v for k, v in (load_json(session / "manifest.json", {}) or {}).get("roots", {}).items() if k != "home"}
    if external:
        say("WARNING these folders are outside the Cursor home and are NOT copied into staging. Commands run "
            "with 'run' read them live, and a command that writes to them writes to the real folder: "
            + ", ".join(external.values()))
    say(f'Test tools against it with: run --session "{session}" -- <command>')
    return 0


def cmd_run(args) -> int:
    """Run a command with HOME / USERPROFILE pointed at the staging home, so
    hooks and scripts read staging's rules, workstream and initiatives."""
    session = Path(os.path.expanduser(args.session)).resolve()
    load_session(session)
    home = staging_home(session)
    if not (home / ".cursor").exists():
        die("no staging folder. Run stage first.")
    cmd = list(args.command)
    if cmd and cmd[0] == "--":
        cmd = cmd[1:]
    if not cmd:
        die("nothing to run. Example: run --session S -- py stage-home/.cursor/hooks/session-init.py")
    env = dict(os.environ)
    env.update({"HOME": str(home), "USERPROFILE": str(home)})
    env.pop("BA_INITIATIVES_ROOT", None)
    env.pop("CURSOR_SESSION_CONTEXT_PATH", None)
    say(f"[staging home: {home}]")
    external = {k: v for k, v in (load_json(session / "manifest.json", {}) or {}).get("roots", {}).items() if k != "home"}
    if external:
        say(f"[read live, not staged: {', '.join(external.values())}]")
    # Hooks read stdin until it closes, so always give them input (empty by default).
    feed = Path(args.stdin).read_text(encoding="utf-8") if args.stdin else ""
    return subprocess.run(cmd, env=env, input=feed, text=True).returncode


# --------------------------------------------------------------------------
# Package mapping: repo path -> installed path
# --------------------------------------------------------------------------

def load_module(path: Path, name: str):
    if not path.exists():
        return None
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        return None
    mod = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(mod)
    except Exception:  # an old package's tool may not import cleanly; fall back
        return None
    return mod


def package_layout(pkg: Path, fallback: dict | None = None) -> dict:
    """Read the install rules from the package's own installer and upgrader, so
    this tool maps files exactly the way they get installed."""
    inst = load_module(pkg / "tools" / "install-ba-assistant.py", f"inst_{abs(hash(str(pkg)))}")
    upg = load_module(pkg / "tools" / "upgrade-ba-assistant.py", f"upg_{abs(hash(str(pkg)))}")
    fb = fallback or {}
    return {
        "package_rules": list(getattr(upg, "PACKAGE_RULES", None) or fb.get("package_rules") or []),
        "companions": list(getattr(upg, "COMPANION_SKILLS", None) or fb.get("companions") or []),
        "skip_in_skill": set(getattr(upg, "SKIP_IN_SKILL_TREE", None) or fb.get("skip_in_skill") or {"learnings.md"}),
        "ws_tool_scripts": list(getattr(inst, "WORKSTREAM_TOOL_SCRIPTS", None) or fb.get("ws_tool_scripts") or []),
        "ws_package_files": list(getattr(inst, "WORKSTREAM_PACKAGE_FILES", None) or fb.get("ws_package_files") or []),
    }


def package_map(pkg: Path, layout: dict) -> dict[str, Path]:
    """{installed posix path: source file in the package}."""
    out: dict[str, Path] = {}

    def add_tree(src_root: Path, dest_prefix: str, skip: set[str] = frozenset()):
        files, _ = walk_files(src_root)
        for rel, p in files.items():
            if rel in skip:
                continue
            out[f"{dest_prefix}/{rel}"] = p

    add_tree(pkg / "skills" / "ba-assistant", "skills/ba-assistant", layout["skip_in_skill"])
    for name in layout["companions"]:
        add_tree(pkg / "skills" / name, f"skills/{name}")
    for name in layout["package_rules"]:
        p = pkg / "rules" / name
        if p.exists():
            out[f"rules/{name}"] = p
    for p in sorted((pkg / "commands").glob("*.md")) if (pkg / "commands").exists() else []:
        out[f"commands/{p.name}"] = p
    for p in sorted((pkg / "hooks").glob("*.py")) if (pkg / "hooks").exists() else []:
        out[f"hooks/{p.name}"] = p
    if (pkg / "hooks" / "hooks.json").exists():
        out["hooks.json"] = pkg / "hooks" / "hooks.json"
    for name in layout["ws_tool_scripts"]:
        p = pkg / "tools" / name
        if p.exists():
            out[f"_workstream/{name}"] = p
    for name in layout["ws_package_files"]:
        p = pkg / "_workstream" / name
        if p.exists():
            out[f"_workstream/{name}"] = p
    return out


# --------------------------------------------------------------------------
# Comparison with normalisation
# --------------------------------------------------------------------------

def read_text_or_none(path: Path | None) -> str | None:
    if path is None or not path.exists():
        return None
    data = path.read_bytes()
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError:
        return None
    return text


def canon(text: str, is_json: bool) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    if is_json:
        try:
            return json.dumps(json.loads(text), sort_keys=True, indent=1, ensure_ascii=False)
        except ValueError:
            pass
    return "\n".join(line.rstrip() for line in text.split("\n")).rstrip("\n")


class Localiser:
    """Turns generic package text into the BA's own naming (generic -> local).

    rules.json: {"rules": [{"local": "alex-actions", "generic": "ba-actions"}, ...]}
    ("find"/"replace" are accepted as local/generic, the direction a
    sync-to-repo skill uses.) Longest generic strings are applied first so
    "ba-actions-format" is not half-replaced by a shorter rule. Hits are
    counted per rule; values are never reported.
    """

    def __init__(self, rules_path: Path | None):
        self.rules: list[dict] = []
        self.hits: dict[int, int] = {}
        self.broad: set[int] = set()
        if rules_path:
            data = load_json(rules_path, {})
            for i, r in enumerate(data.get("rules") or []):
                local = str(r.get("local", r.get("find")) or "")
                generic = str(r.get("generic", r.get("replace")) or "")
                if not local or not generic or local == generic:
                    continue
                self.rules.append({"local": local, "generic": generic, "n": i + 1})
                if len(generic) < 4 or generic.isspace():
                    self.broad.add(i + 1)
            self.rules.sort(key=lambda r: len(r["generic"]), reverse=True)

    def apply(self, text: str, record: bool = False) -> tuple[str, set[int]]:
        used: set[int] = set()
        for r in self.rules:
            n = text.count(r["generic"])
            if n:
                text = text.replace(r["generic"], r["local"])
                used.add(r["n"])
                if record:
                    self.hits[r["n"]] = self.hits.get(r["n"], 0) + n
        return text, used

    def path(self, rel: str) -> str:
        return self.apply(rel)[0]


def same(a: str | None, b: str | None, is_json: bool) -> bool:
    if a is None or b is None:
        return a is None and b is None
    return canon(a, is_json) == canon(b, is_json)


def is_personal(path: str) -> bool:
    if path in PERSONAL_FILES or path in CTX["personal_files"]:
        return True
    if path.startswith("rules/") and any(h in path.lower() for h in VOICE_HINTS):
        return True
    return False


def is_immutable_data(path: str) -> bool:
    if path.startswith("initiatives/") or path.split("/", 1)[0] in CTX["extra_home_dirs"]:
        return True
    if path.startswith("canvases/"):
        return path not in GENERATED_FILES
    if path.startswith("_workstream/"):
        return path.endswith(DATA_SUFFIXES)
    return False


def managed_area(path: str, layout: dict) -> bool:
    """Is this a place the package installs into (so an unknown file here is
    the BA's own local-only file, class H)?"""
    top = path.split("/", 1)[0]
    if top in ("commands", "hooks", "rules"):
        return True
    if path.startswith("skills/ba-assistant/"):
        return True
    return any(path.startswith(f"skills/{c}/") for c in layout["companions"])


CLASS_HELP = {
    "A": "You never changed it; the new version did. Take new.",
    "A-review": "Looks untouched, but only after a very short or general naming rule. Check it.",
    "B": "Only you changed it. Keep yours.",
    "C": "You and the new version made the same change. Nothing to decide.",
    "D": "Both you and the new version changed it. Needs a merge.",
    "E": "New in the new version. Add it.",
    "F": "Removed or renamed in the new version. Your copy is kept unless you choose otherwise.",
    "G": "In the old version but missing from your install (deleted on purpose, or never installed).",
    "H": "Your own file (not part of the package). Never touched.",
    "P": "Personal config (profile, config, tone). Only approved, targeted patches.",
    "M": "hooks.json. Merged by the upgrader hook by hook; your own hooks are kept.",
    "U": "Unchanged everywhere.",
    "DATA": "Your data (actions, workboard, calendar, initiatives). Never changed.",
    "GEN": "Generated canvas. Regenerated by the new version; deployed only if you approve.",
}
DEFAULT_DECISION = {
    "A": "take_new", "A-review": "ask", "B": "keep_mine", "C": "keep_mine", "D": "ask", "E": "take_new",
    "F": "keep_mine", "G": "ask", "H": "keep_mine", "P": "keep_mine", "M": "take_new", "U": "keep_mine",
    "DATA": "keep_mine", "GEN": "keep_mine",
}


def hook_registrations(text: str | None) -> list[str]:
    if not text:
        return []
    try:
        data = json.loads(text)
    except ValueError:
        return ["<invalid JSON>"]
    regs = []
    for event, entries in sorted((data.get("hooks") or {}).items()):
        for e in entries if isinstance(entries, list) else []:
            if not isinstance(e, dict):
                continue
            cmd = str(e.get("command") or e.get("type") or "?")
            script = None
            for token in reversed(cmd.split()):
                token = token.strip("\"'").replace("\\", "/").rsplit("/", 1)[-1]
                if "." in token:
                    script = token
                    break
            regs.append(f"{event}: {script or cmd[:40]}")
    return regs


def load_port_manifest(path: Path | None) -> dict:
    """{generic installed path: {"category": ..., "reason": ...}} or {}."""
    if not path or not path.exists():
        return {}
    data = load_json(path, {}) or {}
    return data.get("files") or {}


def merge3(mine: str, base: str, theirs: str) -> tuple[str | None, int | None]:
    """Line-based three-way merge with git merge-file. Returns (text, conflicts);
    (None, None) when git is not available. Conflicted text carries markers."""
    git = shutil.which("git")
    if not git:
        return None, None
    with tempfile.TemporaryDirectory(prefix="ba-merge3-") as tmp:
        paths = []
        for name, text in (("yours", mine), ("old", base), ("new", theirs)):
            f = Path(tmp) / name
            f.write_text(text.replace("\r\n", "\n"), encoding="utf-8")
            paths.append(str(f))
        proc = subprocess.run([git, "merge-file", "-p", "--diff3", "-L", "yours", "-L", "old version",
                               "-L", "new version", *paths], capture_output=True, text=True, encoding="utf-8")
    if proc.returncode < 0 or proc.returncode > 127:
        return None, None
    return proc.stdout, proc.returncode


def hook_entry_key(event: str, entry: dict) -> tuple[str, str]:
    cmd = str(entry.get("command") or "")
    for token in reversed(cmd.split()):
        token = token.strip("\"'").replace("\\", "/").rsplit("/", 1)[-1]
        if "." in token:
            return event, token
    if entry.get("type") == "prompt":
        return event, "prompt: " + str(entry.get("prompt", ""))[:40]
    return event, cmd[:40] or "?"


def simulate_hooks_merge(new: Path, local_text: str | None, loc) -> dict:
    """What the package merge would do to YOUR hooks.json: dropped, added and
    changed registrations (failClosed, matcher, timeout)."""
    inst = load_module(new / "tools" / "install-ba-assistant.py", "sim_installer")
    pkg_file = new / "hooks" / "hooks.json"
    if inst is None or not pkg_file.exists() or not local_text:
        return {}
    try:
        pkg = json.loads(loc.apply(pkg_file.read_text(encoding="utf-8"))[0])
        existing = json.loads(local_text).get("hooks") or {}
    except (ValueError, AttributeError):
        return {"error": "your hooks.json is not valid JSON; it will not be merged"}
    pkg_hooks = pkg.get("hooks") or {}
    inst.rewrite_package_python_interpreters(pkg_hooks)
    inst.guard_dor_gate_interpreter(pkg_hooks)
    merged, _ = inst.merge_hooks_object(pkg_hooks, existing)

    def index(hooks: dict) -> dict:
        out = {}
        for event, entries in hooks.items():
            for e in entries if isinstance(entries, list) else []:
                if isinstance(e, dict):
                    out[hook_entry_key(event, e)] = {k: e.get(k) for k in ("failClosed", "matcher", "timeout")}
        return out

    before, after = index(existing), index(merged)
    dropped = sorted(f"{k[0]}: {k[1]}" for k in before if k not in after)
    added = sorted(f"{k[0]}: {k[1]}" for k in after if k not in before)
    changed = sorted(
        f"{k[0]}: {k[1]} {field} {before[k][field]!r} -> {after[k][field]!r}"
        for k in before if k in after
        for field in ("failClosed", "matcher", "timeout") if before[k][field] != after[k][field]
    )
    return {"dropped": dropped, "added": added, "changed": changed}


def cmd_classify(args) -> int:
    session = Path(os.path.expanduser(args.session)).resolve()
    load_session(session)
    base = Path(os.path.expanduser(args.base)).resolve()
    new = Path(os.path.expanduser(args.new)).resolve()
    for p, label in ((base, "--base"), (new, "--new")):
        if not (p / "skills" / "ba-assistant").exists():
            die(f"{label} {p} is not a BA Assistant package checkout.")
    local_root = session / "snapshot" / "home"
    rules_path = Path(os.path.expanduser(args.rules)).resolve() if args.rules else None
    loc = Localiser(rules_path)
    CTX["personal_files"] = {loc.path(p) for p in PERSONAL_FILES}
    manifest_path = Path(os.path.expanduser(args.port_manifest)).resolve() if args.port_manifest else new / "docs" / "port-manifest.json"
    port = load_port_manifest(manifest_path)

    new_layout = package_layout(new)
    base_layout = package_layout(base, fallback=new_layout)
    # Package files mapped to where they sit in YOUR install (your naming).
    base_generic = package_map(base, base_layout)
    new_generic = package_map(new, new_layout)
    base_map = {loc.path(k): v for k, v in base_generic.items()}
    new_map = {loc.path(k): v for k, v in new_generic.items()}
    generic_of = {loc.path(k): k for k in list(base_generic) + list(new_generic)}
    merged_dir = session / "merged"
    hooks_review: dict = {}
    local_files, _ = walk_files(local_root)

    def pkg_text(src: Path | None, record: bool = False) -> tuple[str | None, set[int]]:
        t = read_text_or_none(src)
        if t is None:
            return None, set()
        return loc.apply(t, record=record)

    # Rename detection: a file gone from NEW whose content appears at a new path.
    new_by_content = {}
    for path, src in new_map.items():
        t, _ = pkg_text(src)
        if t is not None:
            new_by_content.setdefault(canon(t, path.endswith(".json")), path)

    rows = []
    for path in sorted(set(base_map) | set(new_map) | set(local_files)):
        is_json = path.endswith(".json")
        b, b_used = pkg_text(base_map.get(path))
        n, n_used = pkg_text(new_map.get(path), record=True)
        lp = local_files.get(path)
        l = read_text_or_none(lp)
        in_pkg = path in base_map or path in new_map
        note = ""

        if path == "hooks.json":
            cls = "M"
            mine = sorted(set(hook_registrations(l)) - set(hook_registrations(b)) - set(hook_registrations(n)))
            note = ("your own hook registrations (kept by the merge): " + "; ".join(mine)) if mine else "no hooks of your own"
            hooks_review = simulate_hooks_merge(new, l, loc)
        elif path in GENERATED_FILES:
            cls = "GEN"
        elif is_immutable_data(path) and not in_pkg:
            cls = "DATA"
        elif is_personal(path):
            cls = "P"
        elif (not in_pkg and path.startswith("hooks/") and path.lower().endswith((".sh", ".ps1"))
              and f"hooks/{PurePosixPath(path).stem}.py" in new_map):
            cls = "F"
            note = "old package hook wrapper, replaced by the .py hook; moved aside unless hooks.json still uses it"
        elif not in_pkg:
            if not managed_area(path, new_layout):
                continue  # outside anything the package installs; not reported
            cls = "H"
        elif (lp is not None and l is None) or (path in new_map and n is None and new_map[path].exists()):
            # Binary or non-UTF-8 file: compare bytes only, never rename content.
            srcs = [base_map.get(path), new_map.get(path)]
            lh = sha256_file(lp) if lp else None
            bh = sha256_file(srcs[0]) if srcs[0] else None
            nh = sha256_file(srcs[1]) if srcs[1] else None
            if lh is None:
                cls = "E" if bh is None else "G"
            elif lh == nh:
                cls = "C" if bh != nh else "U"
            elif lh == bh:
                cls = "A"
            elif bh == nh:
                cls = "B"
            else:
                cls = "D"
            note = "binary, compared byte for byte"
        elif b is None and n is not None:
            if l is None:
                cls = "E"
            elif same(l, n, is_json):
                cls = "C"
            else:
                cls, note = "D", "you have a file where the new version adds one"
        elif b is not None and n is None:
            if l is None:
                continue  # gone from the package and not installed: nothing to do
            cls = "F"
            renamed_to = new_by_content.get(canon(b, is_json))
            if renamed_to:
                note = f"renamed in the new version to {renamed_to}"
        elif l is None:
            cls = "G"
        elif same(l, b, is_json):
            if same(n, b, is_json):
                cls = "U"
            elif b_used & loc.broad:
                cls, note = "A-review", "matched the old version only via a short naming rule"
            else:
                cls = "A"
        elif same(n, b, is_json):
            cls = "B"
        elif same(l, n, is_json):
            cls = "C"
        else:
            cls = "D"

        row = {"path": path, "class": cls, "decision": DEFAULT_DECISION[cls], "note": note}
        if cls == "F" and note.startswith("old package hook wrapper"):
            row["decision"] = "remove"
        entry = port.get(generic_of.get(path, path)) if port else None
        if entry:
            row["category"] = entry.get("category")
            row["why"] = entry.get("reason", "")
        if cls == "M" and (hooks_review.get("dropped") or hooks_review.get("changed") or hooks_review.get("error")):
            row["decision"] = "ask"
            row["hooks_review"] = hooks_review
        elif cls == "M" and hooks_review:
            row["hooks_review"] = hooks_review
        if port and cls in ("A", "A-review", "D", "G") and (not entry or entry.get("category") == "wording"):
            # Only behaviour changes are ported into a personalised install.
            row["decision"] = "keep_mine"
            row["note"] = ("wording only in the new version; yours kept" if entry
                           else "not in the port manifest; yours kept")
        elif port and cls == "D" and entry and str(entry.get("category", "")).startswith("behaviour"):
            text, conflicts = merge3(l, b, n) if (l is not None and b is not None and n is not None) else (None, None)
            target = merged_dir / path
            if text is None:
                row["decision"] = "ask"
                row["note"] = "behaviour change; no git for an automatic merge, merge by hand"
            elif conflicts == 0:
                target.parent.mkdir(parents=True, exist_ok=True)
                raw = lp.read_bytes() if lp else b""
                out = text.replace("\n", "\r\n") if b"\r\n" in raw else text
                target.write_bytes(out.encode("utf-8"))
                row["decision"] = "merged"
                row["auto_merged"] = True
                row["note"] = "auto-merged: your changes and the new version's do not overlap; review it"
            else:
                conflict_file = target.with_name(target.name + ".conflict")
                conflict_file.parent.mkdir(parents=True, exist_ok=True)
                conflict_file.write_text(text, encoding="utf-8")
                row["decision"] = "ask"
                row["note"] = (f"{conflicts} overlapping section(s); resolve {conflict_file.name} into "
                               f"merged/{path} and set merged")
        if path in new_map:
            row["new_src"] = str(new_map[path])
        if (b_used | n_used) and cls in ("A", "A-review", "E", "D", "C"):
            row["localised"] = True
        if cls == "D" and l is not None and b is not None and n is not None:
            row["size_of_changes"] = {
                "yours_vs_old_lines": diff_size(b, l),
                "new_vs_old_lines": diff_size(b, n),
            }
        rows.append(row)

    flag_missing_naming_rules(rows)

    by_class: dict[str, list[dict]] = {}
    for r in rows:
        by_class.setdefault(r["class"], []).append(r)

    findings = []
    if not (local_root / "rules" / "ba-assistant-config.mdc").exists():
        root_value = read_config_value(local_root, "initiativesRoot")
        findings.append(
            "No rules/ba-assistant-config.mdc. Session start, the Jira DoR gate and the shared-repo guard read "
            "paths.* from it (then from your profile). "
            + ("Your initiatives root was found in another rule file, so they will work. "
               if root_value else "No paths.initiativesRoot was found anywhere, so they would look only in "
               "~/.cursor/initiatives. ")
            + "Set create_config true in decisions.json to add one from the template, then fill it in staging.")
    for d in CTX["extra_home_dirs"]:
        root_value = read_config_value(local_root, "initiativesRoot")
        if not root_value or d not in root_value:
            findings.append(f"Initiatives found in the folder '{d}', but no paths.initiativesRoot points at it. "
                            f"Add initiativesRoot: \"~/.cursor/{d}\" to your config so session start and the DoR "
                            "gate find them.")
    if port:
        findings.append(f"Port manifest used: {manifest_path.name}. Only behaviour changes are brought in; "
                        "wording-only changes keep your version.")

    classification_id = hashlib.sha256(
        json.dumps([(r["path"], r["class"], r["decision"]) for r in rows], sort_keys=True).encode("utf-8")
    ).hexdigest()[:16]
    write_json(session / "classification.json", {
        "id": classification_id,
        "base": str(base), "new": str(new), "rules": str(rules_path) if rules_path else None,
        "new_commit": git_head(new), "base_commit": git_head(base),
        "personal_files": sorted(CTX["personal_files"]),
        "findings": findings,
        "hooks_review": hooks_review,
        "rows": rows,
    })
    decisions_path = session / "decisions.json"
    if decisions_path.exists() and not args.overwrite_decisions:
        old_id = (load_json(decisions_path, {}) or {}).get("classification_id")
        if old_id != classification_id:
            say(f"WARNING {decisions_path} was made for a different classification. apply-staging will refuse it. "
                "Re-run classify with --overwrite-decisions (your answers are then asked again).")
        else:
            say(f"NOTE {decisions_path} already exists and still matches; left alone.")
    else:
        write_json(decisions_path, {
            "_help": "Set each 'ask' to take_new, keep_mine, or merged (merged = you wrote the result, in your "
                     "own naming, to <session>/merged/<path>). For class G, take_new restores the package file; "
                     "keep_mine leaves it missing. For class F, remove moves your copy aside at deploy. "
                     "patch_profile true replaces only the old /wrap, /validate-state, /status and /todo rows in ba-profile.mdc.",
            "classification_id": classification_id,
            "auto_merged_reviewed": False,
            "patch_profile": False,
            "create_config": False,
            "files": {r["path"]: {"class": r["class"], "decision": r["decision"]} for r in rows
                      if r["class"] not in ("U", "DATA", "H")},
        })
    write_report(session, rows, by_class, loc, base, new, findings, hooks_review)
    say(f"Classified {len(rows)} files.")
    for cls in ("D", "A-review", "G", "F", "E", "A", "B", "C", "P", "M", "H", "GEN", "DATA", "U"):
        if cls in by_class:
            say(f"  {cls:9} {len(by_class[cls]):4}  {CLASS_HELP[cls]}")
    localised = sum(1 for r in rows if r.get("localised"))
    if loc.rules:
        say(f"  {localised} new-version file(s) will be written in your naming.")
    auto = sum(1 for r in rows if r.get("auto_merged"))
    if port:
        say(f"  {auto} behaviour file(s) auto-merged (review them); wording-only changes keep your version.")
    for f in findings:
        say(f"FINDING {f}")
    asks = sum(1 for r in rows if r["decision"] == "ask")
    say(f"Report: {session / 'report.md'}")
    say(f"Decisions to make: {asks} (in {decisions_path})")
    return 0


def flag_missing_naming_rules(rows: list[dict]) -> None:
    """A new package file (E) sitting next to a similarly named file of your
    own (H) usually means a naming rule is missing (e.g. the package adds
    ba-actions-format.md beside your renamed copy). Never add it silently:
    turn it into a question and say why."""
    own = [r["path"] for r in rows if r["class"] in ("H", "F")]
    for r in rows:
        if r["class"] != "E":
            continue
        folder, _, name = r["path"].rpartition("/")
        for other in own:
            o_folder, _, o_name = other.rpartition("/")
            if o_folder != folder or o_name == name:
                continue
            if difflib.SequenceMatcher(None, name.lower(), o_name.lower()).ratio() >= 0.7:
                r["decision"] = "ask"
                r["note"] = (f"looks like your {o_name}; a naming rule may be missing. "
                             "Add the rule and re-run classify, or choose take_new / keep_mine")
                break


def diff_size(a: str, b: str) -> int:
    return sum(1 for line in difflib.unified_diff(canon(a, False).split("\n"), canon(b, False).split("\n"), lineterm="", n=0)
               if line[:1] in "+-" and not line.startswith(("+++", "---")))


def git_head(path: Path) -> str | None:
    try:
        return subprocess.run(["git", "-C", str(path), "rev-parse", "HEAD"], capture_output=True, text=True,
                              check=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def write_report(session: Path, rows, by_class, loc: Localiser, base: Path, new: Path,
                 findings: list[str] | None = None, hooks_review: dict | None = None) -> None:
    lines = [
        "# Upgrade classification report",
        "",
        f"- Old version (BASE): `{base}` at `{git_head(base) or 'unknown commit'}`",
        f"- New version (NEW): `{new}` at `{git_head(new) or 'unknown commit'}`",
        "- Your install (LOCAL): the verified snapshot in this session folder",
        "",
        "This report lists file paths and classes only. It never shows file contents or the",
        "values your find/replace rules matched.",
        "",
        "## Summary",
        "",
        "| Class | Files | Meaning |",
        "|---|---:|---|",
    ]
    order = ("D", "A-review", "G", "F", "E", "A", "B", "C", "P", "M", "H", "GEN", "DATA", "U")
    for cls in order:
        if cls in by_class:
            lines.append(f"| {cls} | {len(by_class[cls])} | {CLASS_HELP[cls]} |")
    if findings:
        lines += ["", "## Findings", ""] + [f"- {f}" for f in findings]
    if hooks_review:
        lines += ["", "## hooks.json: what the merge would change", ""]
        if hooks_review.get("error"):
            lines.append(f"- {hooks_review['error']}")
        for label in ("dropped", "changed", "added"):
            for item in hooks_review.get(label) or []:
                lines.append(f"- {label}: {item}")
        if not any(hooks_review.get(k) for k in ("dropped", "changed", "added", "error")):
            lines.append("- nothing changes")
    decided = [r for r in rows if r.get("auto_merged")]
    if decided:
        lines += ["", "## Auto-merged (review these)", ""]
        for r in decided:
            why = f": {r['why']}" if r.get("why") else ""
            lines.append(f"- `{r['path']}` ({r.get('category', '')}){why}")
    if loc.rules:
        lines += ["", "## Naming rules (generic package name -> your name)", ""]
        for r in sorted(loc.rules, key=lambda r: r["n"]):
            lines.append(f"- rule {r['n']}: used {loc.hits.get(r['n'], 0)} time(s) in the new version's files")
        if loc.broad:
            lines += ["", "**Check rules " + ", ".join(str(n) for n in sorted(loc.broad)) +
                      ":** very short. A short rule can rename things it should not."]
    else:
        lines += ["", "**No naming rules given.** New files will use the generic package names "
                  "(for example ba-actions). If your install uses your own names, re-run classify with --rules."]
    for cls in order:
        if cls in ("U", "DATA") or cls not in by_class:
            continue
        lines += ["", f"## {cls}: {CLASS_HELP[cls]}", ""]
        for r in by_class[cls]:
            extra = ""
            if r.get("size_of_changes"):
                s = r["size_of_changes"]
                extra = f" (your changes: {s['yours_vs_old_lines']} lines, new version's: {s['new_vs_old_lines']} lines)"
            note = f" ({r['note']})" if r.get("note") else ""
            if r.get("localised"):
                note += " [written in your naming]"
            lines.append(f"- `{r['path']}`{extra}{note}")
    if "DATA" in by_class:
        lines += ["", f"## DATA: {len(by_class['DATA'])} files of your data, never changed", ""]
    (session / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


# --------------------------------------------------------------------------
# apply-staging
# --------------------------------------------------------------------------

def cmd_apply_staging(args) -> int:
    """Build the upgraded install in staging, file by file, from decisions.json.

    The plain upgrader is NOT run here: it writes generic names (ba-actions),
    seeds data files and overwrites edited package files. Instead each package
    file is written in the BA's own naming, hooks.json is merged with the new
    package's own merge (your hooks kept), and nothing under your data paths
    is written.
    """
    session = Path(os.path.expanduser(args.session)).resolve()
    load_session(session)
    staging = staging_dir(session)
    if not staging.exists():
        die("no staging folder. Run stage first.")
    if (session / "staging-result.json").exists():
        die("staging was already built. Run stage --fresh, then apply-staging again.")
    cls_data = load_json(session / "classification.json")
    if not cls_data:
        die("no classification.json. Run classify first.")
    decisions = load_json(session / "decisions.json", {})
    files = decisions.get("files") or {}
    pending = sorted(p for p, d in files.items() if d.get("decision") == "ask")
    if pending:
        die(f"{len(pending)} decision(s) still 'ask' in decisions.json, e.g. {pending[:5]}")
    if decisions.get("classification_id") != cls_data.get("id"):
        die("decisions.json does not match the latest classify run. Re-run classify with --overwrite-decisions.")
    auto = [r["path"] for r in cls_data["rows"] if r.get("auto_merged") and files.get(r["path"], {}).get("decision") == "merged"]
    if auto and not decisions.get("auto_merged_reviewed"):
        die(f"{len(auto)} auto-merged file(s) in merged/ have not been signed off. Review them "
            "(report.md lists them), then set auto_merged_reviewed to true in decisions.json.")
    new = Path(cls_data["new"])
    loc = Localiser(Path(cls_data["rules"]) if cls_data.get("rules") else None)
    CTX["personal_files"] = set(cls_data.get("personal_files") or PERSONAL_FILES)
    rows = {r["path"]: r for r in cls_data["rows"]}
    upg = load_module(new / "tools" / "upgrade-ba-assistant.py", "new_upgrader")
    inst = load_module(new / "tools" / "install-ba-assistant.py", "new_installer")
    if upg is None or inst is None:
        die("could not load the new package's installer/upgrader.")

    applied = []
    for path, d in sorted(files.items()):
        decision = d.get("decision")
        row = rows.get(path, {})
        target = staging / path
        if path == "hooks.json":
            if decision == "take_new":
                inst.merge_hooks_json(new / "hooks" / "hooks.json", target, False)
                applied.append("MERGE      hooks.json (package hooks updated, your own hooks kept)")
            elif decision == "merged":
                shutil.copy2(session / "merged" / path, target)
                applied.append("MERGED     hooks.json")
            continue
        if decision == "keep_mine":
            if row.get("class") == "G" and target.exists():
                target.unlink()
            applied.append(f"KEEP MINE  {path}")
        elif decision == "take_new":
            src = Path(row["new_src"]) if row.get("new_src") else None
            if src is None or not src.exists():
                die(f"take_new for {path} but the new version has no such file")
            target.parent.mkdir(parents=True, exist_ok=True)
            text = read_text_or_none(src)
            if text is None:
                shutil.copy2(src, target)
            else:
                raw = src.read_bytes()
                newline = "\r\n" if b"\r\n" in raw else "\n"
                localised, _ = loc.apply(text.replace("\r\n", "\n"))
                target.write_bytes(localised.replace("\n", newline).encode("utf-8"))
            applied.append(f"TAKE NEW   {path}" + ("  [your naming]" if row.get("localised") else ""))
        elif decision == "merged":
            src = session / "merged" / path
            if not src.exists():
                die(f"decision 'merged' for {path} but {src} does not exist")
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, target)
            applied.append(f"MERGED     {path}")
        elif decision == "remove":
            hooks_text = (staging / "hooks.json").read_text(encoding="utf-8") if (staging / "hooks.json").exists() else ""
            if path.startswith("hooks/") and PurePosixPath(path).name in hooks_text:
                applied.append(f"KEEP       {path} (hooks.json still uses it)")
                continue
            if target.exists():
                target.unlink()
            applied.append(f"REMOVE     {path} (moved aside at deploy, never deleted)")
        else:
            die(f"unknown decision {decision!r} for {path}")

    # Config file from the template, when the install has none and you asked for it.
    config = staging / "rules" / "ba-assistant-config.mdc"
    if decisions.get("create_config") and not config.exists():
        template = new / "skills" / "ba-assistant" / "ba-profile.template.mdc"
        text = loc.apply(template.read_text(encoding="utf-8"))[0]
        extra = list(CTX["extra_home_dirs"])
        if len(extra) == 1 and not read_config_value(staging, "initiativesRoot"):
            text = re.sub(r'(^\s*initiativesRoot:\s*)"[^"]*"', rf'\g<1>"~/.cursor/{extra[0]}"', text, count=1, flags=re.M)
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(text, encoding="utf-8")
        applied.append("CONFIG     rules/ba-assistant-config.mdc created from the template: FILL IT IN (in staging) "
                       "before deploy-plan")

    # Profile: only the old /wrap, /validate-state, /status and /todo rows, in your naming.
    profile = staging / loc.path("rules/ba-profile.mdc")
    if decisions.get("patch_profile") and profile.exists():
        raw = profile.read_bytes()
        newline = "\r\n" if b"\r\n" in raw else "\n"
        lines = raw.decode("utf-8").split(newline)
        new_rows = {k: loc.apply(v)[0] for k, v in upg.package_profile_rows(new).items()}
        changed = 0
        for i, line in enumerate(lines):
            for command, marker in upg.OLD_PROFILE_ROW_MARKERS.items():
                if line.startswith(upg.profile_row_prefix(command)) and marker in line and command in new_rows:
                    lines[i] = new_rows[command]
                    changed += 1
        if changed:
            profile.write_bytes(newline.join(lines).encode("utf-8"))
        applied.append(f"PATCH      rules/ba-profile.mdc ({changed} row(s))")

    # Version stamp.
    version = (new / "VERSION").read_text(encoding="utf-8").strip() if (new / "VERSION").exists() else "unknown"
    (staging / "skills" / "ba-assistant").mkdir(parents=True, exist_ok=True)
    (staging / "skills" / "ba-assistant" / "VERSION").write_text(version + "\n", encoding="utf-8")
    marker = staging / ".ba-assistant-installed.json"
    if marker.exists():
        try:
            data = json.loads(marker.read_text(encoding="utf-8"))
            data["version"] = version
            data["upgraded_at"] = datetime.now().isoformat(timespec="seconds")
            write_json(marker, data)
        except ValueError:
            pass
    applied.append(f"VERSION    {version}")

    # Your data must be byte-identical in staging.
    manifest = load_json(session / "manifest.json")["files"]
    changed_data = []
    for key, meta in manifest.items():
        if not key.startswith("home/"):
            continue
        rel = key[len("home/"):]
        if is_immutable_data(rel) and rel not in rows or rows.get(rel, {}).get("class") == "DATA":
            p = staging / rel
            if not p.exists() or sha256_file(p) != meta["sha256"]:
                changed_data.append(rel)
        elif rel.split("/", 1)[0] in CTX["extra_home_dirs"]:
            p = staging / rel
            if not p.exists() or sha256_file(p) != meta["sha256"]:
                changed_data.append(rel)
    if changed_data:
        die(f"your data changed in staging, which must not happen: {changed_data[:10]}")
    write_json(session / "staging-result.json", {"applied": applied, "version": version})
    (session / "staging-log.txt").write_text("\n".join(applied) + "\n", encoding="utf-8")
    say(f"Built version {version} in staging: {len(applied)} step(s). Log: {session / 'staging-log.txt'}")
    say("Your data in staging is byte-identical to the backup.")
    say("Next: test in staging (see docs/PERSONALISED-UPGRADE.md), then deploy-plan.")
    return 0


# --------------------------------------------------------------------------
# deploy-plan / deploy
# --------------------------------------------------------------------------

def build_plan(session: Path) -> dict:
    staging = staging_dir(session)
    snapshot = session / "snapshot" / "home"
    staged = {}
    for entry in home_includes():
        p = staging / entry
        if p.is_file():
            staged[entry] = p
        elif p.is_dir():
            sub, _ = walk_files(p)
            staged.update({f"{entry}/{k}": v for k, v in sub.items()})
    orig = {}
    for entry in home_includes():
        p = snapshot / entry
        if p.is_file():
            orig[entry] = p
        elif p.is_dir():
            sub, _ = walk_files(p)
            orig.update({f"{entry}/{k}": v for k, v in sub.items()})

    cls_data = load_json(session / "classification.json", {}) or {}
    classes = {r["path"]: r["class"] for r in cls_data.get("rows", [])}
    CTX["personal_files"] = set(cls_data.get("personal_files") or PERSONAL_FILES)
    entries = []
    problems = []
    for path in sorted(set(staged) | set(orig)):
        s, o = staged.get(path), orig.get(path)
        sh = sha256_file(s) if s else None
        oh = sha256_file(o) if o else None
        if sh == oh:
            continue
        cls = classes.get(path)
        if path in GENERATED_FILES or path.startswith("_workstream/snapshots/"):
            kind = "generated"  # rebuilt by the tools; only deployed with --include-generated
        elif cls not in (None, "DATA") and not is_personal(path):
            kind = "package"  # package-owned file that happens to live under _workstream/
        elif is_immutable_data(path):
            if o is None:
                kind = "seed"  # a data file the upgrader created because it did not exist
            else:
                problems.append(path)
                continue
        elif is_personal(path):
            kind = "personal"
        else:
            kind = "package"
        action = "add" if o is None else ("remove" if s is None else "replace")
        entries.append({"path": path, "action": action, "kind": kind, "sha256": sh, "was_sha256": oh})
    return {"entries": entries, "problems": problems}


def plan_digest(plan: dict) -> str:
    return hashlib.sha256(json.dumps(plan["entries"], sort_keys=True).encode("utf-8")).hexdigest()[:16]


def cmd_deploy_plan(args) -> int:
    session = Path(os.path.expanduser(args.session)).resolve()
    meta = load_session(session)
    if not (session / "staging-result.json").exists():
        die("run apply-staging first.")
    plan = build_plan(session)
    if plan["problems"]:
        die(f"staging changed your data files, refusing to plan: {plan['problems'][:10]}")
    digest = plan_digest(plan)
    plan["sha"] = digest
    write_json(session / "deploy-plan.json", plan)
    home = meta["cursor_home"]
    lines = [f"# Deploy plan {digest}", "", f"Target: `{home}`", "",
             "| Action | Kind | Path |", "|---|---|---|"]
    for e in plan["entries"]:
        lines.append(f"| {e['action']} | {e['kind']} | `{e['path']}` |")
    lines += ["", "Kinds: package = BA Assistant code; personal = your profile/config (edited in staging, "
              "check it); seed = a new data file that did not exist; generated = the workboard canvas or "
              "initiative snapshots rebuilt in staging (only deployed with --include-generated). Removals are moved aside, never deleted.",
              "", "Your data files are not in this plan and are never written."]
    (session / "deploy-plan.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    counts: dict[str, int] = {}
    for e in plan["entries"]:
        counts[f"{e['action']}/{e['kind']}"] = counts.get(f"{e['action']}/{e['kind']}", 0) + 1
    say(f"Deploy plan {digest}: {len(plan['entries'])} file(s) -> {home}")
    for k, v in sorted(counts.items()):
        say(f"  {k}: {v}")
    personal = [e["path"] for e in plan["entries"] if e["kind"] == "personal"]
    if personal:
        say(f"CHECK personal files that would change: {personal}")
    say(f"Full list: {session / 'deploy-plan.md'}")
    say(f"To deploy exactly this plan: deploy --session \"{session}\" --plan-sha {digest}")
    return 0


def live_drift(session: Path) -> list[str]:
    meta = load_session(session)
    manifest = load_json(session / "manifest.json")
    roots = {k: Path(v) for k, v in manifest["roots"].items()}
    now: dict[str, Path] = {}
    for label, root in roots.items():
        f, _ = root_files(label, root)
        now.update(f)
    drift = []
    for key, m in manifest["files"].items():
        p = now.get(key)
        if p is None:
            drift.append(f"removed  {key}")
        elif sha256_file(p) != m["sha256"]:
            drift.append(f"changed  {key}")
    for key in sorted(set(now) - set(manifest["files"])):
        drift.append(f"added    {key}")
    _ = meta
    return drift


def cmd_deploy(args) -> int:
    session = Path(os.path.expanduser(args.session)).resolve()
    meta = load_session(session)
    plan = load_json(session / "deploy-plan.json")
    if not plan:
        die("no deploy-plan.json. Run deploy-plan first.")
    fresh = build_plan(session)
    if plan_digest(fresh) != plan["sha"]:
        die("staging changed since deploy-plan was made. Run deploy-plan again and review it.")
    if args.plan_sha != plan["sha"]:
        die(f"--plan-sha {args.plan_sha} does not match the reviewed plan {plan['sha']}.")

    drift = live_drift(session)
    if drift:
        say("Your real install changed since the backup (another Cursor chat, a hook, or an edit):")
        for d in drift[:30]:
            say(f"  {d}")
        die("nothing deployed. Close other Cursor windows, then start again from backup with a new session.")

    home = Path(meta["cursor_home"])
    staging = staging_dir(session)
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    removed_dir = session / f"removed-{ts}"
    done = []
    try:
        for e in plan["entries"]:
            if e["kind"] == "generated" and not args.include_generated:
                say(f"SKIP generated {e['path']} (pass --include-generated to deploy it)")
                continue
            target = home / e["path"]
            if e["action"] == "remove":
                dest = removed_dir / e["path"]
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(target), str(dest))
            else:
                src = staging / e["path"]
                if sha256_file(src) != e["sha256"]:
                    raise RuntimeError(f"staging file changed after planning: {e['path']}")
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, target)
            done.append(e)

        # Verify: every deployed file matches, everything else matches the backup.
        manifest = load_json(session / "manifest.json")["files"]
        touched = {e["path"] for e in done}
        errors = []
        for e in done:
            p = home / e["path"]
            if e["action"] == "remove":
                if p.exists():
                    errors.append(f"still present after remove: {e['path']}")
            elif sha256_file(p) != e["sha256"]:
                errors.append(f"hash mismatch after copy: {e['path']}")
        manifest_roots = load_json(session / "manifest.json")["roots"]
        for key, m in manifest.items():
            label, _, rel = key.partition("/")
            if label == "home" and rel in touched:
                continue
            p = Path(manifest_roots[label]) / rel
            if not p.exists() or sha256_file(p) != m["sha256"]:
                errors.append(f"untouched file changed: {key}")
        if errors:
            raise RuntimeError("; ".join(errors[:10]))
    except Exception as exc:  # roll back to the exact backup on any failure
        say(f"DEPLOY FAILED: {exc}")
        say("Rolling back to the backup ...")
        rc = do_rollback(session)
        say("Rollback complete; every backed-up file matches the backup." if rc == 0 else
            f"Rollback reported a problem. Follow {session / 'ROLLBACK.md'} by hand.")
        return 1

    write_json(session / "deploy-result.json", {"deployed": done, "at": ts})
    baseline = {}
    for entry in home_includes():
        p = home / entry
        files_now = {entry: p} if p.is_file() else {f"{entry}/{k}": v for k, v in walk_files(p)[0].items()} if p.is_dir() else {}
        baseline.update({k: sha256_file(v) for k, v in files_now.items()})
    write_json(session / "post-deploy-manifest.json", {"at": ts, "files": baseline})
    say(f"Deployed {len(done)} file(s). Every deployed file and every untouched file verified by hash.")
    say("Open a NEW Cursor chat and run /ba-assistant, then /workboard.")
    say(f"If anything feels wrong: rollback --session \"{session}\"")
    return 0


# --------------------------------------------------------------------------
# rollback
# --------------------------------------------------------------------------

def do_rollback(session: Path) -> int:
    manifest = load_json(session / "manifest.json")
    roots = {k: Path(v) for k, v in manifest["roots"].items()}
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    aside = session / f"rolled-back-{ts}"
    for label, root in roots.items():
        if label == "home":
            for entry in home_includes():
                p = root / entry
                if p.exists() or p.is_symlink():
                    dest = aside / label / entry
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    shutil.move(str(p), str(dest))
        elif root.exists():
            dest = aside / label
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(root), str(dest))
    with zipfile.ZipFile(session / "backup.zip") as zf:
        for info in zf.infolist():
            label, _, rel = info.filename.partition("/")
            if label not in roots or not rel or info.is_dir():
                continue
            target = roots[label] / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info) as src, open(target, "wb") as dst:
                shutil.copyfileobj(src, dst)
    bad = []
    for key, m in manifest["files"].items():
        label, _, rel = key.partition("/")
        p = roots[label] / rel
        if not p.exists() or sha256_file(p) != m["sha256"]:
            bad.append(key)
    say(f"Moved the previous files aside to {aside}")
    if bad:
        say(f"Rollback verification FAILED for {len(bad)} file(s): {bad[:10]}")
        return 1
    say(f"Restored {len(manifest['files'])} files; every hash matches the backup.")
    return 0


def cmd_rollback(args) -> int:
    session = Path(os.path.expanduser(args.session)).resolve()
    load_session(session)
    return do_rollback(session)


def cmd_changed_since_deploy(args) -> int:
    """Files added or changed in the real install since deploy: the allowlist
    for the first sync back to the repo (so kept-as-yours wording files that
    you have not touched are never pushed back)."""
    session = Path(os.path.expanduser(args.session)).resolve()
    meta = load_session(session)
    base = load_json(session / "post-deploy-manifest.json")
    if not base:
        die("no post-deploy-manifest.json: deploy has not run in this session.")
    home = Path(meta["cursor_home"])
    now = {}
    for entry in home_includes():
        p = home / entry
        if p.is_file():
            now[entry] = p
        elif p.is_dir():
            now.update({f"{entry}/{k}": v for k, v in walk_files(p)[0].items()})
    changed = []
    for path, p in sorted(now.items()):
        if path.split("/", 1)[0] in CTX["extra_home_dirs"] or is_immutable_data(path):
            continue  # data is never synced to the package
        if base["files"].get(path) != sha256_file(p):
            changed.append(("added" if path not in base["files"] else "changed", path))
    removed = sorted(p for p in base["files"] if p not in now and not is_immutable_data(p))
    for kind, path in changed:
        say(f"{kind:8} {path}")
    for path in removed:
        say(f"removed  {path}")
    if not changed and not removed:
        say("Nothing changed since deploy: nothing to sync.")
    if args.out:
        Path(os.path.expanduser(args.out)).write_text(
            "\n".join([p for _, p in changed] + removed) + "\n", encoding="utf-8")
        say(f"Allowlist written to {args.out}")
    return 0


def cmd_drift(args) -> int:
    session = Path(os.path.expanduser(args.session)).resolve()
    drift = live_drift(session)
    if drift:
        for d in drift:
            say(d)
        return 1
    say("No drift: your install matches the backup exactly.")
    return 0


# --------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("backup", help="hash manifest, zip, zip test, restore rehearsal")
    p.add_argument("--cursor-home", default=str(Path.home() / ".cursor"))
    p.add_argument("--session", help="session folder (default ~/ba-assistant-upgrade-<timestamp>)")
    p.add_argument("--extra", action="append", default=[], help="extra folder to back up (repeatable)")
    p.set_defaults(func=cmd_backup)

    p = sub.add_parser("stage", help="copy the verified snapshot into <session>/staging")
    p.add_argument("--session", required=True)
    p.add_argument("--fresh", action="store_true", help="rebuild staging from the snapshot")
    p.set_defaults(func=cmd_stage)

    p = sub.add_parser("classify", help="three-way comparison, writes report.md and decisions.json")
    p.add_argument("--session", required=True)
    p.add_argument("--base", required=True, help="old package checkout (the version you installed)")
    p.add_argument("--new", required=True, help="new package checkout (pinned commit)")
    p.add_argument("--rules", help='rules.json: {"rules": [{"local": "alex-actions", "generic": "ba-actions"}]}')
    p.add_argument("--overwrite-decisions", action="store_true")
    p.add_argument("--port-manifest", help="which new-version changes are behaviour vs wording "
                   "(default: docs/port-manifest.json in the new checkout, if present)")
    p.set_defaults(func=cmd_classify)

    p = sub.add_parser("apply-staging", help="build the upgraded install in staging from decisions.json")
    p.add_argument("--session", required=True)
    p.set_defaults(func=cmd_apply_staging)

    p = sub.add_parser("run", help="run a command with HOME pointed at the staging home")
    p.add_argument("--session", required=True)
    p.add_argument("--stdin", help="file to feed the command on stdin (for hooks)")
    p.add_argument("command", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_run)

    p = sub.add_parser("deploy-plan", help="list the exact files deploy would change")
    p.add_argument("--session", required=True)
    p.set_defaults(func=cmd_deploy_plan)

    p = sub.add_parser("deploy", help="drift check, copy planned files, verify, auto-rollback on failure")
    p.add_argument("--session", required=True)
    p.add_argument("--plan-sha", required=True, help="the id printed by deploy-plan")
    p.add_argument("--include-generated", "--include-canvas", dest="include_generated", action="store_true",
                   help="also deploy the regenerated workboard canvas and initiative snapshots")
    p.set_defaults(func=cmd_deploy)

    p = sub.add_parser("drift", help="has the real install changed since the backup?")
    p.add_argument("--session", required=True)
    p.set_defaults(func=cmd_drift)

    p = sub.add_parser("changed-since-deploy", help="files you changed after deploy: the allowlist for your first sync")
    p.add_argument("--session", required=True)
    p.add_argument("--out", help="write the list of paths to this file")
    p.set_defaults(func=cmd_changed_since_deploy)

    p = sub.add_parser("rollback", help="restore every backed-up file byte for byte")
    p.add_argument("--session", required=True)
    p.set_defaults(func=cmd_rollback)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
