#!/usr/bin/env python3
"""Generate compact, source-linked local snapshots for BA commands.

Snapshots are a retrieval index only. They are never canonical. Commands must
follow `sources.*.path` (or the initiative root) to cite, update, or confirm a
fact. If a snapshot field disagrees with a listed source file, the source wins.
Snapshots never decide which initiative a chat is for.

  python3 _workstream/generate-initiative-snapshots.py               # all initiatives in workboard.json
  python3 _workstream/generate-initiative-snapshots.py --slug <slug>  # one initiative
  python3 _workstream/generate-initiative-snapshots.py --check <slug> # FRESH (exit 0) or STALE/MISSING/MALFORMED (exit 1)
  python3 _workstream/generate-initiative-snapshots.py --ensure <slug> # resume: FRESH as is, or rebuilt (REFRESHED); exit 1 if it cannot be built

Windows: use `py` instead of `python3`.

Initiatives folder: BA_INITIATIVES_ROOT, else paths.initiativesRoot in
~/.cursor/rules/ba-assistant-config.mdc (or ba-profile.mdc), else
~/.cursor/initiatives. Output: _workstream/snapshots/<slug>.json.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
from datetime import datetime
from pathlib import Path


def load_json(path: Path, default: object) -> object:
    return json.loads(path.read_text(encoding="utf-8-sig")) if path.exists() else default


def parse_rule_value(text: str, key: str) -> str | None:
    """`key: value` reader shared with the other BA Assistant scripts. Matches a
    nested YAML key too (`  initiativesRoot: ...` under `paths:`)."""
    patterns = [
        rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$",
        rf"^\s*{re.escape(key)}\s*=\s*(.+?)\s*$",
    ]
    for line in text.splitlines():
        for pattern in patterns:
            match = re.match(pattern, line.strip())
            if match:
                value = match.group(1).strip()
                if value[:1] in {'"', "'"}:
                    end = value.find(value[0], 1)
                    value = value[1:end] if end > 0 else value[1:]
                else:
                    value = value.split(" #", 1)[0].strip()
                if value and value not in {"[Your Name]", "[BA name]", "TBC"} and not value.startswith("["):
                    return value
    return None


def load_rules_text(cursor_home: Path) -> str:
    text = ""
    for name in ("ba-assistant-config.mdc", "ba-profile.mdc"):
        path = cursor_home / "rules" / name
        if path.exists():
            text += path.read_text(encoding="utf-8", errors="replace") + "\n"
    return text


def resolve_initiatives_root(cursor_home: Path, rules_text: str) -> Path:
    """Same order as hooks/session-init.py: env, then config, then the default."""
    env = os.environ.get("BA_INITIATIVES_ROOT", "").strip()
    if env:
        return Path(os.path.expanduser(env))
    value = parse_rule_value(rules_text, "initiativesRoot")
    if value:
        return Path(os.path.expanduser(value))
    return cursor_home / "initiatives"


SOURCE_FILES = ("initiative-tracker.md", "SESSION-CONTEXT.md", "Project-hub.md", "status-data.json", "status-snapshot.html")


def section(text: str, title: str, limit: int = 1200) -> str:
    match = re.search(rf"^## {re.escape(title)}\s*$([\s\S]*?)(?=^## |\Z)", text, re.M)
    return match.group(1).strip()[:limit] if match else ""


def table_rows(text: str, title: str, maximum: int = 5) -> list[str]:
    rows = [line.strip() for line in section(text, title).splitlines() if line.strip().startswith("|")]
    return [row for row in rows[2:] if row.count("|") >= 3][:maximum]


def first_value(text: str, label: str) -> str | None:
    match = re.search(rf"^\*\*{re.escape(label)}:\*\*\s*(.+)$", text, re.M)
    return match.group(1).strip() if match else None


def file_sha256(path: Path) -> str | None:
    try:
        return hashlib.sha256(path.read_bytes()).hexdigest()
    except OSError:
        return None


def file_info(path: Path) -> dict:
    exists = path.exists()
    return {
        "path": str(path),
        "exists": exists,
        "modifiedAt": datetime.fromtimestamp(path.stat().st_mtime).astimezone().isoformat() if exists else None,
        "sha256": file_sha256(path) if exists else None,
    }


# Workstream files a snapshot reads (actions, status, meetings). Only this
# initiative's slice of each counts: its workboard row, its actions (any
# status) and its matching meetings. A /todo for another initiative or a
# calendar refresh that does not touch this initiative's meetings leaves the
# snapshot FRESH; a change to anything the snapshot shows makes it STALE.
WORKSTREAM_INPUTS = ("workboard.json", "ba-actions.json", "calendar-feed.json")


def meeting_terms(slug: str, initiative: dict) -> set[str]:
    terms = {slug.lower()}
    terms.update(word.lower() for word in str(initiative.get("name") or "").split() if len(word) > 4)
    return terms


def workstream_slices(workstream: Path, slug: str) -> dict[str, object]:
    workboard = load_json(workstream / "workboard.json", {})
    initiative = next((i for i in workboard.get("initiatives", []) if i.get("slug") == slug), None)
    actions = load_json(workstream / "ba-actions.json", {}).get("actions", [])
    calendar = load_json(workstream / "calendar-feed.json", {})
    terms = meeting_terms(slug, initiative or {})
    return {
        "workboard.json": initiative,
        "ba-actions.json": [a for a in actions if a.get("initiative") == slug],
        "calendar-feed.json": [m for m in calendar.get("meetings", []) if any(t in str(m).lower() for t in terms)],
    }


def slice_sha256(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()


def slice_info(path: Path, value: object) -> dict:
    return {"path": str(path), "exists": path.exists(), "slice": "this initiative only", "sha256": slice_sha256(value)}


def snapshot(initiatives_root: Path, initiative: dict, actions: list[dict], calendar: dict,
             workstream: Path | None = None) -> dict:
    slug = str(initiative["slug"])
    root = initiatives_root / slug
    tracker, session = root / "initiative-tracker.md", root / "SESSION-CONTEXT.md"
    tracker_text = tracker.read_text(encoding="utf-8", errors="replace") if tracker.exists() else ""
    session_text = session.read_text(encoding="utf-8", errors="replace") if session.exists() else ""
    recent_actions = [
        {"id": item.get("id"), "task": item.get("task"), "due": item.get("due"), "status": item.get("status")}
        for item in actions
        if item.get("initiative") == slug and item.get("status") in {"open", "in_progress", "blocked"}
    ][:8]
    terms = meeting_terms(slug, initiative)
    meetings = [
        {"subject": item.get("subject"), "start": item.get("start"), "end": item.get("end")}
        for item in calendar.get("meetings", [])
        if any(term in str(item).lower() for term in terms)
    ][:5]
    sources = {name: file_info(root / name) for name in SOURCE_FILES}
    if workstream is not None:
        for name, value in workstream_slices(workstream, slug).items():
            sources[f"_workstream/{name}"] = slice_info(workstream / name, value)
    return {
        "schemaVersion": 1,
        "role": "retrieval-index",
        "canonical": False,
        "use": "Read this first to decide which source files to open. Do not treat snapshot fields as source of truth.",
        "generatedAt": datetime.now().astimezone().isoformat(),
        "initiative": {"slug": slug, "name": initiative.get("name"), "root": str(root)},
        "current": {
            "status": initiative.get("status"),
            "phase": initiative.get("phase"),
            "nextAction": initiative.get("next_action") or first_value(session_text, "Next concrete action") or first_value(session_text, "Recommended next action"),
        },
        "decisions": table_rows(tracker_text, "Decisions"),
        "openQuestions": table_rows(tracker_text, "Open questions"),
        "actions": recent_actions,
        "pendingSessionItems": session_text.count("[pending]"),
        "upcomingMeetings": meetings,
        "sources": sources,
    }


def check_snapshot(snapshots: Path, initiatives_root: Path, slug: str, workstream: Path) -> tuple[str, str]:
    """FRESH only when the snapshot parses, every initiative file it was built
    from is byte-identical (SHA-256) to when it was made (including files that
    have appeared or disappeared since), and this initiative's slice of each
    workstream file is unchanged. Anything else: refresh it or read the files."""
    path = snapshots / f"{slug}.json"
    if not path.exists():
        return "MISSING", f"no snapshot at {path}"
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
        recorded = data["sources"]
        if data.get("initiative", {}).get("slug") != slug or not isinstance(recorded, dict):
            return "MALFORMED", "snapshot is for a different initiative"
    except (ValueError, KeyError, TypeError, AttributeError):
        return "MALFORMED", f"cannot read {path}"
    root = initiatives_root / slug
    current = {name: file_sha256(root / name) for name in SOURCE_FILES}
    try:
        slices = workstream_slices(workstream, slug)
    except (ValueError, AttributeError, TypeError):
        return "STALE", "a workstream file could not be read"
    current.update({f"_workstream/{name}": slice_sha256(value) for name, value in slices.items()})
    for name, digest in current.items():
        entry = recorded.get(name)
        if not isinstance(entry, dict) or "sha256" not in entry:
            return "STALE", f"snapshot does not record {name} (made by an older version)"
        if name.startswith("_workstream/") and entry.get("slice") is None:
            return "STALE", f"snapshot hashed all of {name} (made by an older version)"
        if digest != entry.get("sha256"):
            return "STALE", f"{name} changed after the snapshot was made"
    return "FRESH", str(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="Compact, source-linked initiative snapshots (resume shortcut only)")
    parser.add_argument("--slug", help="generate one initiative snapshot")
    parser.add_argument("--check", metavar="SLUG", help="report FRESH / STALE / MISSING / MALFORMED for one initiative")
    parser.add_argument("--ensure", metavar="SLUG", help="resume: use the snapshot if FRESH, otherwise rebuild it first (REFRESHED)")
    parser.add_argument("--cursor-home", default=str(Path.home() / ".cursor"))
    args = parser.parse_args()
    home = Path(os.path.expanduser(args.cursor_home))
    initiatives_root = resolve_initiatives_root(home, load_rules_text(home))
    workstream = home / "_workstream"
    snapshots = workstream / "snapshots"

    if args.check:
        state, detail = check_snapshot(snapshots, initiatives_root, args.check, workstream)
        print(f"Snapshot: {state} ({detail})")
        return 0 if state == "FRESH" else 1

    if args.ensure:
        state, detail = check_snapshot(snapshots, initiatives_root, args.ensure, workstream)
        if state == "FRESH":
            print(f"Snapshot: FRESH ({detail})")
            return 0
        args.slug = args.ensure

    workboard = load_json(workstream / "workboard.json", {})
    actions = load_json(workstream / "ba-actions.json", {}).get("actions", [])
    calendar = load_json(workstream / "calendar-feed.json", {})
    initiatives = [item for item in workboard.get("initiatives", []) if not args.slug or item.get("slug") == args.slug]
    if args.slug and not initiatives:
        print(f"Snapshot: no initiative {args.slug!r} in workboard.json")
        return 1
    for initiative in initiatives:
        slug = str(initiative["slug"])
        # Nested slugs (e.g. short-term/example-slug) need parent dirs
        output = snapshots / f"{slug}.json"
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(
            json.dumps(snapshot(initiatives_root, initiative, actions, calendar, workstream), indent=2) + "\n",
            encoding="utf-8",
        )
        print(f"Snapshot: {'REFRESHED' if args.ensure else 'written'} ({output})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
