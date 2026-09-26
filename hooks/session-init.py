#!/usr/bin/env python3
"""sessionStart hook v3 - inject latest SESSION-CONTEXT snippet + DETERMINISTIC
downloads check (D5).

Single cross-platform replacement for the former session-init.ps1 (Windows)
and session-init.sh (Mac/Linux) twins. hooks/hooks.json now points sessionStart
at this one script; tools/install-ba-assistant.py rewrites the interpreter
token in its "command" string (py / python3) for the OS actually running the
install, so the shipped hooks.json never has to hardcode one.

The two originals had drifted apart. This port reconciles that rather than
picking one arbitrarily:
  - Persisted last-session timestamp + CURSOR_LAST_SESSION env var: only
    session-init.ps1 had this (writes/reads a timestamp file in the scratch
    dir, emits CURSOR_LAST_SESSION). session-init.sh never persisted a
    timestamp file and never emitted CURSOR_LAST_SESSION at all - a real gap,
    not a deliberate omission (nothing in the .sh explains dropping it).
    Ported from the .ps1.
  - Workboard open-task check and calendar-today check (WORKBOARD:/CALENDAR:
    context lines): only session-init.ps1 had these blocks. Ported from the
    .ps1; the Windows-only Outlook-COM get-calendar.ps1 call is replaced below
    with an OS-appropriate best-effort call (get-calendar.ps1 on Windows,
    get-calendar.mac.sh on macOS; other systems skip calendar refresh — both optional sample scripts under
    references/sample-scripts/, silently skipped if not installed under
    ~/.cursor/hooks/, exactly like the .ps1 skipped it when the script was
    missing).
  - "OTHER NEW DOWNLOADS" (non-transcript) block and .vtt extension support:
    only session-init.ps1 had these. Ported from the .ps1.
  - Search roots: session-init.sh searched MORE roots than session-init.ps1
    (it also checked ~/ba-initiatives, ~/Initiatives, ~/projects, in addition
    to ~/.cursor/Initiatives and ~/.cursor/blueprints). Kept the broader .sh
    list — nothing suggested the narrower .ps1 list was a deliberate trim.
  - CURSOR_NEW_TRANSCRIPTS join character: .ps1 joined paths with ';', .sh
    joined with a raw newline (fragile in an env var). Kept ';' (.ps1's).
Kept from both: AGENTS.md/README.md guidance line, SESSION-CONTEXT tail
snippet (last 45 lines), and the JSON output contract Cursor's sessionStart
hook expects: {"additional_context": str, "env": {...}}.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

TRANSCRIPT_EXTENSIONS = {".docx", ".vtt"}
OTHER_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".xlsx", ".csv", ".txt", ".md", ".pptx"}
TAIL_LINES = 45
MAX_OTHER_LISTED = 10


def eprint(msg: str) -> None:
    print(msg, file=sys.stderr)


def scratch_dir() -> Path:
    """OS-appropriate scratch dir. Matches the old .ps1's
    %LOCALAPPDATA%\\Temp\\cursor-agent-scratch on Windows, and the old .sh's
    ${TMPDIR:-/tmp} (mac) / ${XDG_RUNTIME_DIR:-/tmp} (linux) elsewhere.
    """
    if sys.platform.startswith("win"):
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "Temp" / "cursor-agent-scratch"
    if sys.platform == "darwin":
        base = os.environ.get("TMPDIR") or "/tmp"
    else:
        base = os.environ.get("XDG_RUNTIME_DIR") or "/tmp"
    return Path(base) / "cursor-agent-scratch"


def read_last_session_time(timestamp_file: Path) -> datetime | None:
    if not timestamp_file.exists():
        return None
    try:
        raw = timestamp_file.read_text(encoding="utf-8").strip()
        return datetime.fromisoformat(raw)
    except (OSError, ValueError):
        return None


def write_last_session_time(timestamp_file: Path) -> None:
    try:
        timestamp_file.parent.mkdir(parents=True, exist_ok=True)
        timestamp_file.write_text(datetime.now(timezone.utc).astimezone().isoformat(), encoding="utf-8")
    except OSError:
        pass


def search_roots() -> list[str]:
    roots = []
    initiatives_root = os.environ.get("BA_INITIATIVES_ROOT")
    if initiatives_root:
        roots.append(initiatives_root)
    home = str(Path.home())
    # Broader list from session-init.sh (nothing suggested the .ps1's
    # narrower 2-root list was a deliberate trim — see module docstring).
    roots += [
        str(Path(home) / ".cursor" / "Initiatives"),
        str(Path(home) / ".cursor" / "blueprints"),
        str(Path(home) / "ba-initiatives"),
        str(Path(home) / "Initiatives"),
        str(Path(home) / "projects"),
    ]
    # De-dupe, preserve order.
    seen = set()
    out = []
    for r in roots:
        if r not in seen:
            seen.add(r)
            out.append(r)
    return out


def find_latest_session_context(roots: list[str]) -> tuple[Path | None, float]:
    latest_path: Path | None = None
    latest_mtime = 0.0
    for root in roots:
        root_path = Path(root)
        if not root_path.is_dir():
            continue
        try:
            candidates = root_path.rglob("SESSION-CONTEXT.md")
        except OSError:
            continue
        for f in candidates:
            try:
                mtime = f.stat().st_mtime
            except OSError:
                continue
            if mtime > latest_mtime:
                latest_mtime = mtime
                latest_path = f
    return latest_path, latest_mtime


def tail_text(path: Path, n: int = TAIL_LINES) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    except OSError:
        return ""
    return "\n".join(lines[-n:] if len(lines) > n else lines)


def windows_dir_files(folder: Path) -> list[Path]:
    """Discover files through cmd when pathlib cannot enumerate Downloads.

    `/b` keeps the output to filenames only, avoiding locale-dependent date,
    time, and size columns. Recency still comes from Path.stat() below.
    """
    try:
        proc = subprocess.run(
            ["cmd", "/c", "dir", "/a-d", "/o-d", "/b", str(folder)],
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if proc.returncode != 0:
        return []
    files = []
    for name in proc.stdout.splitlines():
        name = name.strip()
        if not name:
            continue
        candidate = folder / name
        try:
            if candidate.is_file():
                files.append(candidate)
        except OSError:
            continue
    return files


def scan_downloads(folders: list[str], since_mtime: float) -> tuple[list[dict], list[dict]]:
    new_transcripts: list[dict] = []
    other_new: list[dict] = []
    seen = set()
    for folder in folders:
        if not folder or folder in seen:
            continue
        seen.add(folder)
        folder_path = Path(folder)
        if not folder_path.is_dir():
            continue
        try:
            entries = [entry for entry in folder_path.iterdir() if entry.is_file()]
        except OSError:
            entries = []
        if sys.platform == "win32" and not entries:
            entries = windows_dir_files(folder_path)
        for f in entries:
            try:
                st = f.stat()
            except OSError:
                continue
            if st.st_mtime <= since_mtime:
                continue
            entry = {
                "name": f.name,
                "path": str(f),
                "modified": datetime.fromtimestamp(st.st_mtime).strftime("%Y-%m-%d %H:%M"),
                "folder": str(folder_path),
            }
            ext = f.suffix.lower()
            if ext in TRANSCRIPT_EXTENSIONS:
                new_transcripts.append(entry)
            elif ext in OTHER_EXTENSIONS:
                other_new.append(entry)
    return new_transcripts, other_new


def workboard_block() -> str:
    workboard_path = Path.home() / ".cursor" / "_workstream" / "workboard.json"
    if not workboard_path.exists():
        return ""
    try:
        wb = json.loads(workboard_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    tasks = wb.get("personal_tasks") or []
    open_count = sum(1 for t in tasks if isinstance(t, dict) and t.get("status") == "open")
    if open_count > 0:
        return f"\nWORKBOARD: {open_count} open personal tasks. Say /workboard for full view."
    return ""


def run_calendar_refresh() -> None:
    """Best-effort calendar feed refresh, mirroring session-init.ps1's call to
    ~/.cursor/hooks/get-calendar.ps1 — but OS-appropriate. Neither sample
    calendar puller (references/sample-scripts/get-calendar.ps1 or
    get-calendar.mac.sh) is installed automatically; this only runs one if the
    user has copied it into ~/.cursor/hooks/ themselves, and is a silent
    no-op otherwise (same as the old hooks when the script was missing).
    """
    hooks_dir = Path.home() / ".cursor" / "hooks"
    try:
        if sys.platform == "win32":
            script = hooks_dir / "get-calendar.ps1"
            if script.exists():
                subprocess.run(
                    ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), "-DaysAhead", "2"],
                    capture_output=True, timeout=15, check=False,
                )
        elif sys.platform == "darwin":
            script = hooks_dir / "get-calendar.mac.sh"
            if script.exists():
                subprocess.run(["bash", str(script), "2"], capture_output=True, timeout=15, check=False)
    except (OSError, subprocess.SubprocessError) as exc:
        eprint(f"Calendar refresh failed: {exc}")


def calendar_block() -> str:
    calendar_path = Path.home() / ".cursor" / "_workstream" / "calendar-feed.json"
    if not calendar_path.exists():
        return ""
    try:
        cal = json.loads(calendar_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ""
    meetings = cal.get("meetings") or []
    today = datetime.now().date()
    today_count = 0
    for m in meetings:
        start = m.get("start")
        if not start:
            continue
        try:
            start_dt = datetime.fromisoformat(str(start).replace("Z", "+00:00"))
        except ValueError:
            continue
        if start_dt.date() == today:
            today_count += 1
    if today_count > 0:
        return f"\nCALENDAR: {today_count} meeting(s) today. Check /workboard for details."
    return ""


def main() -> int:
    # Windows terminals commonly default stdout/stderr to a legacy codepage
    # (cp1252), which raises UnicodeEncodeError on non-ASCII content that can
    # legitimately appear in a SESSION-CONTEXT.md tail (emoji, curly quotes,
    # em dashes). Force UTF-8 so this hook never crashes on that content
    # instead of emitting its JSON contract. No-op where stdout is already
    # UTF-8 (Mac/Linux).
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass

    eprint(f"session-init.py v3 running - {datetime.now().strftime('%H:%M:%S')}")

    scratch = scratch_dir()
    timestamp_file = scratch / "last-session-timestamp.txt"
    last_session_time = read_last_session_time(timestamp_file)
    write_last_session_time(timestamp_file)

    # --- 1. Find latest SESSION-CONTEXT.md ---
    roots = search_roots()
    latest, latest_mtime = find_latest_session_context(roots)

    context_block = (
        "No SESSION-CONTEXT.md found under configured initiative roots. "
        "Set BA_INITIATIVES_ROOT (ba-setup wizard) if initiatives live elsewhere."
    )
    if latest is not None:
        modified = datetime.fromtimestamp(latest_mtime).strftime("%Y-%m-%d %H:%M")
        snippet = tail_text(latest)
        context_block = (
            f"ACTIVE INITIATIVE CONTEXT (auto-injected from {latest}, modified {modified}):\n"
            "On BA-resume threads, READ the full file before acting. Do not rely on this snippet alone.\n"
            "If the open workspace has AGENTS.md at its root, read it as primary project context "
            "(else README.md). Load BA skills only from ~/.cursor/skills/ba-assistant/.\n\n"
            "--- SESSION-CONTEXT tail ---\n"
            f"{snippet}\n"
            "--- end ---"
        )

    # --- 2. Deterministic downloads check (D5) ---
    downloads_path = os.environ.get("BA_DOWNLOADS_PATH")
    folders = [downloads_path] if downloads_path else []
    folders.append(str(Path.home() / "Downloads"))
    since = last_session_time.timestamp() if last_session_time else 0.0
    new_transcripts, other_new = scan_downloads(folders, since)

    transcript_block = ""
    if new_transcripts:
        file_list = "\n".join(f"  - {t['name']} ({t['modified']}) in {t['folder']}" for t in new_transcripts)
        transcript_block = (
            f"\n\nNEW TRANSCRIPTS DETECTED ({len(new_transcripts)} file(s) since last session):\n"
            f"{file_list}\n"
            "Process these as meeting debriefs (ba-meeting-debrief) before or alongside the user's first ask."
        )
    if other_new:
        other_list = "\n".join(f"  - {t['name']} ({t['modified']})" for t in other_new[:MAX_OTHER_LISTED])
        transcript_block += (
            f"\n\nOTHER NEW DOWNLOADS ({len(other_new)} file(s) - PDFs/images/sheets can carry decisions "
            "and proposals too):\n"
            f"{other_list}\n"
            "Triage per the workspace-operations reference before asking the user what they need."
        )

    # --- 3 & 4. Workboard + calendar ---
    wb_block = workboard_block()
    run_calendar_refresh()
    cal_block = calendar_block()

    full_context = context_block + transcript_block + wb_block + cal_block

    output = {
        "additional_context": full_context,
        "env": {
            "CURSOR_SESSION_CONTEXT_PATH": str(latest) if latest else "",
            "CURSOR_LAST_SESSION": last_session_time.isoformat() if last_session_time else "",
            "CURSOR_NEW_TRANSCRIPTS": ";".join(t["path"] for t in new_transcripts),
            "CURSOR_NEW_TRANSCRIPT_COUNT": str(len(new_transcripts)),
        },
    }
    print(json.dumps(output, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
