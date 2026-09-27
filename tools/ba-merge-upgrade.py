#!/usr/bin/env python3
"""
Personalised-install upgrade helper (Version 15).

For a BA who has customised their installed BA Assistant (edited skills, own
rules, own skills, tone) and wants a new package version WITHOUT losing any of
it. The plain upgrader overwrites package files; this tool wraps it in a safe,
reviewable flow:

    backup -> stage -> classify -> (decide) -> apply-staging -> deploy-plan -> deploy
                                                                   rollback (any time after backup)

What this tool does NOT do: it never merges file content and never decides.
Files that both you and the new version changed are listed for a person (or
Cursor, with you approving) to merge by hand into <session>/merged/.

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
      Puts the backup back exactly (moves the current files aside first).
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
    cfg = cursor_home / "rules" / "ba-assistant-config.mdc"
    if not cfg.exists():
        return ""
    for line in cfg.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$", line)
        if m:
            value = m.group(1).split(" #", 1)[0].strip().strip("\"'")
            return value
    return ""


def load_session(session: Path) -> dict:
    meta = load_json(session / "session.json")
    if not meta:
        die(f"{session} is not a ba-merge-upgrade session folder (no session.json). Run backup first.")
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
    """Manifest keys are '<label>/<path>'. For home, only HOME_INCLUDE entries."""
    files: dict[str, Path] = {}
    skipped: list[str] = []
    if label == "home":
        for entry in HOME_INCLUDE:
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
    say("Backing up (explicit include list):")
    for label, root in roots.items():
        if label == "home":
            present = [e for e in HOME_INCLUDE if (root / e).exists()]
            say(f"  {label}: {root}")
            say(f"      includes: {', '.join(present)}")
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
        "Puts your BA Assistant install back exactly as it was when this backup was taken.",
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
            lines += [f"   - `{root / e}`" for e in HOME_INCLUDE if (root / e).exists()]
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
    staging = session / "staging"
    if staging.exists():
        if not args.fresh:
            die(f"{staging} already exists. Pass --fresh to rebuild it from the snapshot.")
        shutil.rmtree(staging)
    shutil.copytree(src, staging)
    manifest = load_json(session / "manifest.json")["files"]
    bad = [k for k, m in manifest.items() if k.startswith("home/")
           and sha256_file(staging / k[len("home/"):]) != m["sha256"]]
    if bad:
        die(f"staging copy does not match the backup: {bad[:5]}")
    say(f"Staging ready: {staging}")
    say("It is a full copy of your install. Nothing in your real Cursor home was touched.")
    return 0


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
    if path in PERSONAL_FILES:
        return True
    if path.startswith("rules/") and any(h in path.lower() for h in VOICE_HINTS):
        return True
    return False


def is_immutable_data(path: str) -> bool:
    if path.startswith("initiatives/"):
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

    new_layout = package_layout(new)
    base_layout = package_layout(base, fallback=new_layout)
    # Package files mapped to where they sit in YOUR install (your naming).
    base_map = {loc.path(k): v for k, v in package_map(base, base_layout).items()}
    new_map = {loc.path(k): v for k, v in package_map(new, new_layout).items()}
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

    write_json(session / "classification.json", {
        "base": str(base), "new": str(new), "rules": str(rules_path) if rules_path else None,
        "new_commit": git_head(new), "base_commit": git_head(base),
        "rows": rows,
    })
    decisions_path = session / "decisions.json"
    if decisions_path.exists() and not args.overwrite_decisions:
        say(f"NOTE {decisions_path} already exists and was left alone (pass --overwrite-decisions to regenerate).")
    else:
        write_json(decisions_path, {
            "_help": "Set each 'ask' to take_new, keep_mine, or merged (merged = you wrote the result, in your "
                     "own naming, to <session>/merged/<path>). For class G, take_new restores the package file; "
                     "keep_mine leaves it missing. For class F, remove moves your copy aside at deploy. "
                     "patch_profile true replaces only the old /wrap and /validate-state rows in ba-profile.mdc.",
            "patch_profile": False,
            "files": {r["path"]: {"class": r["class"], "decision": r["decision"]} for r in rows
                      if r["class"] not in ("U", "DATA", "H")},
        })
    write_report(session, rows, by_class, loc, base, new)
    say(f"Classified {len(rows)} files.")
    for cls in ("D", "A-review", "G", "F", "E", "A", "B", "C", "P", "M", "H", "GEN", "DATA", "U"):
        if cls in by_class:
            say(f"  {cls:9} {len(by_class[cls]):4}  {CLASS_HELP[cls]}")
    localised = sum(1 for r in rows if r.get("localised"))
    if loc.rules:
        say(f"  {localised} new-version file(s) will be written in your naming.")
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


def write_report(session: Path, rows, by_class, loc: Localiser, base: Path, new: Path) -> None:
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
    staging = session / "staging"
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
    new = Path(cls_data["new"])
    loc = Localiser(Path(cls_data["rules"]) if cls_data.get("rules") else None)
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

    # Profile: only the old /wrap and /validate-state rows, in your naming.
    profile = staging / "rules" / "ba-profile.mdc"
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
    staging = session / "staging"
    snapshot = session / "snapshot" / "home"
    staged = {}
    for entry in HOME_INCLUDE:
        p = staging / entry
        if p.is_file():
            staged[entry] = p
        elif p.is_dir():
            sub, _ = walk_files(p)
            staged.update({f"{entry}/{k}": v for k, v in sub.items()})
    orig = {}
    for entry in HOME_INCLUDE:
        p = snapshot / entry
        if p.is_file():
            orig[entry] = p
        elif p.is_dir():
            sub, _ = walk_files(p)
            orig.update({f"{entry}/{k}": v for k, v in sub.items()})

    classes = {r["path"]: r["class"] for r in (load_json(session / "classification.json", {}) or {}).get("rows", [])}
    entries = []
    problems = []
    for path in sorted(set(staged) | set(orig)):
        s, o = staged.get(path), orig.get(path)
        sh = sha256_file(s) if s else None
        oh = sha256_file(o) if o else None
        if sh == oh:
            continue
        cls = classes.get(path)
        if path in GENERATED_FILES:
            kind = "canvas"
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
              "check it); seed = a new data file that did not exist; canvas = the generated workboard "
              "(only deployed with --include-canvas). Removals are moved aside, never deleted.",
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
    staging = session / "staging"
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    removed_dir = session / f"removed-{ts}"
    done = []
    try:
        for e in plan["entries"]:
            if e["kind"] == "canvas" and not args.include_canvas:
                say(f"SKIP canvas {e['path']} (pass --include-canvas to deploy it)")
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
        say("Rollback complete; your install is exactly as it was." if rc == 0 else
            f"Rollback reported a problem. Follow {session / 'ROLLBACK.md'} by hand.")
        return 1

    write_json(session / "deploy-result.json", {"deployed": done, "at": ts})
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
            for entry in HOME_INCLUDE:
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
    p.set_defaults(func=cmd_classify)

    p = sub.add_parser("apply-staging", help="build the upgraded install in staging from decisions.json")
    p.add_argument("--session", required=True)
    p.set_defaults(func=cmd_apply_staging)

    p = sub.add_parser("deploy-plan", help="list the exact files deploy would change")
    p.add_argument("--session", required=True)
    p.set_defaults(func=cmd_deploy_plan)

    p = sub.add_parser("deploy", help="drift check, copy planned files, verify, auto-rollback on failure")
    p.add_argument("--session", required=True)
    p.add_argument("--plan-sha", required=True, help="the id printed by deploy-plan")
    p.add_argument("--include-canvas", action="store_true")
    p.set_defaults(func=cmd_deploy)

    p = sub.add_parser("drift", help="has the real install changed since the backup?")
    p.add_argument("--session", required=True)
    p.set_defaults(func=cmd_drift)

    p = sub.add_parser("rollback", help="restore the backup exactly")
    p.add_argument("--session", required=True)
    p.set_defaults(func=cmd_rollback)

    args = ap.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
