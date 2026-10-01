#!/usr/bin/env python3
"""Read and write the BA action list (ba-actions.json) without the agent hand-editing JSON.

The agent still decides WHAT to capture (task wording, initiative, dates). This
script does the mechanical part the same way every time: next BA-NNN id, the
duplicate check from ba-actions-format.md section 3.2, priority defaults, never
reopening done/cancelled rows, regenerating ba-actions.md, and the gate line.

  python3 _workstream/ba-actions.py add --task "Chase data export" --initiative payments --due 2026-10-02
  python3 _workstream/ba-actions.py upsert --json rows.json          # many rows (debrief, /wrap, /validate-state)
  python3 _workstream/ba-actions.py set BA-012 --status in_progress --remind-on 2026-10-01 --reminder "Prep first thing"
  python3 _workstream/ba-actions.py done BA-013 BA-014
  python3 _workstream/ba-actions.py list [--initiative slug] [--overdue]
  python3 _workstream/ba-actions.py eod-scan --closeout-date 2026-09-30   # end of day 5a buckets + 5b walk list

Windows: use `py` instead of `python3`. Dates are ISO (YYYY-MM-DD); `today` and
`tomorrow` are also accepted. Resolve "Friday" / "next week" to a date first.
Exit codes: 0 ok, 1 bad input or missing id, 2 the store could not be read.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent
JSON_PATH = ROOT / "ba-actions.json"
REGEN_SCRIPT = ROOT / "regenerate-ba-actions-md.py"

ACTIVE = {"open", "in_progress", "blocked"}
CLOSED = {"done", "cancelled"}
STATUSES = ACTIVE | CLOSED
PRIORITIES = ("high", "medium", "low")
SOURCE_TYPES = ("debrief", "tracker", "session", "quick-capture", "wrap", "comms")
PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def now_iso() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def parse_day(value: str | None, today: date) -> str | None:
    if value is None:
        return None
    text = value.strip().lower()
    if text in {"", "none", "null"}:
        return None
    if text == "today":
        return today.isoformat()
    if text == "tomorrow":
        return (today + timedelta(days=1)).isoformat()
    try:
        return date.fromisoformat(text[:10]).isoformat()
    except ValueError:
        raise SystemExit(f"Not a date: {value!r}. Use YYYY-MM-DD, today or tomorrow.")


def as_date(value) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


def working_days_between(start: date, end: date) -> int:
    """Working days after start up to and including end (0 when end <= start)."""
    days, cursor = 0, start
    while cursor < end:
        cursor += timedelta(days=1)
        if cursor.weekday() < 5:
            days += 1
    return days


def fingerprint(text: str) -> str:
    """ba-actions-format.md 3.2: lowercase, strip punctuation, first 80 chars."""
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", str(text).lower())).strip()[:80]


def load_store() -> dict:
    if not JSON_PATH.exists():
        return {"schema_version": 1, "last_synced": None, "last_generated_md": None,
                "next_id": 1, "actions": [], "watching": []}
    try:
        data = json.loads(JSON_PATH.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Gate: ba-actions-sync: FAIL (cannot read {JSON_PATH}: {exc})")
        raise SystemExit(2)
    data.setdefault("actions", [])
    data.setdefault("watching", [])
    return data


def next_id(data: dict) -> str:
    highest = 0
    for row in data["actions"]:
        match = re.fullmatch(r"BA-(\d+)", str(row.get("id", "")))
        if match:
            highest = max(highest, int(match.group(1)))
    number = max(int(data.get("next_id") or 1), highest + 1)
    data["next_id"] = number + 1
    return f"BA-{number:03d}"


def default_priority(due: str | None, blocked: bool, today: date) -> str:
    if blocked:
        return "high"
    due_day = as_date(due)
    if due_day is None:
        return "medium"
    if working_days_between(today, due_day) <= 2:
        return "high"
    return "medium" if (due_day - today).days <= 14 else "low"


def find_match(data: dict, row: dict) -> dict | None:
    """Match order from ba-actions-format.md 3.2: tracker_ref, fingerprint, then
    same initiative with a similar task and due within 2 days."""
    ref = row.get("tracker_ref")
    if ref:
        for existing in data["actions"]:
            if existing.get("tracker_ref") == ref and existing.get("initiative") == row.get("initiative"):
                return existing
    # Exact wording matches only within the same initiative: two initiatives can
    # both have "Send meeting notes", and matching across them would move the
    # row to the other initiative. A row with no initiative yet can still match
    # (quick capture first, initiative added later).
    print_ = fingerprint(row.get("task", ""))
    for existing in data["actions"]:
        if fingerprint(existing.get("task", "")) != print_:
            continue
        mine, theirs = row.get("initiative"), existing.get("initiative")
        if mine and theirs and mine != theirs:
            continue
        return existing
    # Fuzzy: same initiative, mostly the same words, and due dates (when both
    # are set) within 2 days. Only open work is matched this way, so a new
    # action is never folded into an old closed one by a loose match.
    due = as_date(row.get("due"))
    words = set(print_.split())
    for existing in data["actions"]:
        if existing.get("initiative") != row.get("initiative") or existing.get("status") in CLOSED:
            continue
        other_due = as_date(existing.get("due"))
        other_words = set(fingerprint(existing.get("task", "")).split())
        overlap = len(words & other_words) / max(1, len(words | other_words))
        dates_close = due is None or other_due is None or abs((other_due - due).days) <= 2
        if dates_close and overlap >= 0.75:
            return existing
    return None


def clean_row(raw: dict, today: date) -> dict:
    task = str(raw.get("task") or "").strip()
    if not task:
        raise SystemExit("Every action needs a task.")
    row = {"task": task}
    for key in ("initiative", "notes", "reminder", "tracker_ref", "blocker_notes"):
        if raw.get(key) not in (None, ""):
            row[key] = str(raw[key])
    for key in ("due", "remind_on", "started_on"):
        if key in raw:
            row[key] = parse_day(raw.get(key), today)
    if raw.get("priority"):
        if raw["priority"] not in PRIORITIES:
            raise SystemExit(f"priority must be one of {', '.join(PRIORITIES)}")
        row["priority"] = raw["priority"]
    if raw.get("status"):
        if raw["status"] not in STATUSES:
            raise SystemExit(f"status must be one of {', '.join(sorted(STATUSES))}")
        row["status"] = raw["status"]
    if raw.get("blocked") is not None:
        row["blocked"] = bool(raw["blocked"])
    source = raw.get("source") if isinstance(raw.get("source"), dict) else {}
    source_type = source.get("type") or raw.get("source_type") or "quick-capture"
    if source_type not in SOURCE_TYPES:
        raise SystemExit(f"source type must be one of {', '.join(SOURCE_TYPES)}")
    row["source"] = {
        "type": source_type,
        "label": source.get("label") or raw.get("source_label") or {"quick-capture": "Quick capture"}.get(source_type, source_type.title()),
        "date": parse_day(source.get("date") or raw.get("source_date"), today) or today.isoformat(),
    }
    source_file = source.get("file") or raw.get("source_file")
    if source_file:
        row["source"]["file"] = str(source_file)
    return row


def upsert(data: dict, raw: dict, today: date) -> tuple[str, dict]:
    row = clean_row(raw, today)
    existing = find_match(data, row)
    stamp = now_iso()
    if existing is None:
        blocked = bool(row.get("blocked")) or row.get("status") == "blocked"
        action = {
            "id": next_id(data),
            "task": row["task"],
            "initiative": row.get("initiative"),
            "raised": row["source"]["date"],
            "due": row.get("due"),
            "status": row.get("status", "blocked" if blocked else "open"),
            "priority": row.get("priority") or default_priority(row.get("due"), blocked, today),
            "blocked": blocked,
            "blocker_notes": row.get("blocker_notes"),
            "source": row["source"],
            "notes": row.get("notes"),
            "last_updated": stamp,
        }
        for key in ("tracker_ref", "remind_on", "reminder", "started_on"):
            if row.get(key) is not None:
                action[key] = row[key]
        data["actions"].append(action)
        return "added", action
    # Update: refresh due/source/notes/tracker_ref and anything given. Never
    # reopen or overwrite the status of a done/cancelled row (format 3.2.3).
    changed = False
    for key in ("due", "notes", "tracker_ref", "remind_on", "reminder", "started_on", "priority", "blocker_notes", "initiative"):
        if key in row and row[key] is not None and existing.get(key) != row[key]:
            existing[key] = row[key]
            changed = True
    if "status" in row and existing.get("status") not in CLOSED and existing.get("status") != row["status"]:
        existing["status"] = row["status"]
        changed = True
    if "blocked" in row and existing.get("status") not in CLOSED and existing.get("blocked") != row["blocked"]:
        existing["blocked"] = row["blocked"]
        changed = True
    if (raw.get("source") or raw.get("source_type") or raw.get("source_label")) and existing.get("source") != row["source"]:
        existing["source"] = row["source"]
        changed = True
    if changed:
        existing["last_updated"] = stamp
        return "updated", existing
    return "unchanged", existing


def save_and_regenerate(data: dict) -> bool:
    data["last_synced"] = now_iso()
    JSON_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    if not REGEN_SCRIPT.exists():
        print(f"Gate: ba-actions-md-regen: FAIL (missing {REGEN_SCRIPT.name})")
        return False
    proc = subprocess.run([sys.executable, str(REGEN_SCRIPT)], capture_output=True, text=True, encoding="utf-8")
    if proc.returncode != 0:
        print(f"Gate: ba-actions-md-regen: FAIL ({(proc.stderr or proc.stdout).strip()[-300:]})")
        return False
    print("Gate: ba-actions-md-regen: PASS")
    return True


def open_count(data: dict) -> int:
    return sum(1 for a in data["actions"] if a.get("status") in ACTIVE)


def describe(action: dict) -> str:
    bits = [f"{action['id']}: {action.get('task')}"]
    if action.get("initiative"):
        bits.append(f"#{action['initiative']}")
    if action.get("due"):
        bits.append(f"due {action['due']}")
    if action.get("remind_on"):
        bits.append(f"remind {action['remind_on']}")
    if action.get("priority") == "high":
        bits.append("high")
    return " ".join(bits)


def report(results: list[tuple[str, dict]], data: dict) -> None:
    headings = {"added": "Added", "updated": "Updated", "unchanged": "Already there"}
    for kind in ("added", "updated", "unchanged"):
        rows = [a for k, a in results if k == kind]
        if rows:
            print(f"{headings[kind]}:")
            for action in rows:
                print(f"- {describe(action)}")
    added = sum(1 for k, _ in results if k == "added")
    updated = sum(1 for k, _ in results if k == "updated")
    print(f"({open_count(data)} open actions)")
    print(f"Gate: ba-actions-sync: PASS ({open_count(data)} open, {added} added, {updated} updated)")


def cmd_add(args, today: date) -> int:
    data = load_store()
    raw = {k: v for k, v in vars(args).items() if k not in {"func", "today"} and v is not None}
    result = upsert(data, raw, today)
    ok = save_and_regenerate(data) if result[0] != "unchanged" else True
    report([result], data)
    return 0 if ok else 1


def cmd_upsert(args, today: date) -> int:
    text = sys.stdin.read() if args.json == "-" else Path(args.json).read_text(encoding="utf-8-sig")
    rows = json.loads(text)
    if isinstance(rows, dict):
        rows = rows.get("actions", [rows])
    data = load_store()
    results = [upsert(data, raw, today) for raw in rows]
    ok = True
    if any(kind != "unchanged" for kind, _ in results):
        ok = save_and_regenerate(data)
    report(results, data)
    return 0 if ok else 1


def find_ids(data: dict, ids: list[str]) -> list[dict] | None:
    by_id = {a.get("id"): a for a in data["actions"]}
    missing = [i for i in ids if i not in by_id]
    if missing:
        print(f"Gate: ba-actions-sync: FAIL (no action {', '.join(missing)})")
        return None
    return [by_id[i] for i in ids]


def cmd_set(args, today: date) -> int:
    data = load_store()
    found = find_ids(data, [args.id])
    if found is None:
        return 1
    action = found[0]
    if action.get("status") in CLOSED and args.status and args.status not in CLOSED and not args.reopen:
        print(f"{args.id} is {action['status']}. Pass --reopen if the user confirmed reopening it.")
        print("Gate: ba-actions-sync: FAIL (would reopen a closed action)")
        return 1
    if args.status:
        action["status"] = args.status
        action["blocked"] = args.status == "blocked"
        if args.status in CLOSED:
            action.pop("remind_on", None)
    for key in ("due", "remind_on", "started_on"):
        value = getattr(args, key)
        if value is not None:
            action[key] = parse_day(value, today)
    for key in ("priority", "notes", "reminder", "blocker_notes", "initiative", "task"):
        value = getattr(args, key)
        if value is not None:
            action[key] = value
    action["last_updated"] = now_iso()
    ok = save_and_regenerate(data)
    report([("updated", action)], data)
    return 0 if ok else 1


def cmd_done(args, today: date) -> int:
    data = load_store()
    found = find_ids(data, args.ids)
    if found is None:
        return 1
    for action in found:
        action["status"] = "done"
        action["blocked"] = False
        action.pop("remind_on", None)
        action["last_updated"] = now_iso()
    ok = save_and_regenerate(data)
    report([("updated", a) for a in found], data)
    return 0 if ok else 1


def sort_key(action: dict):
    return (0 if action.get("status") == "blocked" else 1,
            PRIORITY_ORDER.get(action.get("priority"), 9),
            as_date(action.get("due")) or date.max)


def cmd_list(args, today: date) -> int:
    data = load_store()
    rows = [a for a in data["actions"] if a.get("status") in ACTIVE]
    if args.initiative:
        rows = [a for a in rows if a.get("initiative") == args.initiative]
    if args.overdue:
        rows = [a for a in rows if (as_date(a.get("due")) or date.max) < today]
    rows.sort(key=sort_key)
    if args.json:
        print(json.dumps(rows, indent=2, ensure_ascii=False))
        return 0
    for action in rows:
        overdue = (as_date(action.get("due")) or date.max) < today
        print(f"- {describe(action)}{' OVERDUE' if overdue else ''}{' BLOCKED' if action.get('status') == 'blocked' else ''}")
    print(f"({len(rows)} shown, {open_count(data)} open in total)")
    return 0


def cmd_eod_scan(args, today: date) -> int:
    """eod-closeout-procedure.md 5a buckets and the 5b walk list, so the agent
    presents them instead of re-deriving the filter from the whole JSON."""
    closeout = as_date(parse_day(args.closeout_date, today)) or today
    data = load_store()
    active = [a for a in data["actions"] if a.get("status") in ACTIVE]
    buckets: dict[str, list[dict]] = {"Overdue": [], "Due today": [], "Remind today": [], "High, due within 2 working days": []}
    for action in active:
        due, remind = as_date(action.get("due")), as_date(action.get("remind_on"))
        if due and due < closeout:
            buckets["Overdue"].append(action)
        elif due == closeout:
            buckets["Due today"].append(action)
        if remind == closeout:
            buckets["Remind today"].append(action)
        if action.get("priority") == "high" and due and due > closeout and working_days_between(closeout, due) <= 2:
            buckets["High, due within 2 working days"].append(action)

    def rank(action: dict) -> int:
        due, remind = as_date(action.get("due")), as_date(action.get("remind_on"))
        if due and due < closeout:
            return 0
        if due == closeout:
            return 1
        if remind == closeout:
            return 2
        if action.get("status") == "blocked":
            return 3
        if action.get("priority") == "high":
            return 4
        if as_date(action.get("started_on")) == closeout:
            return 5
        return 9

    walk = sorted((a for a in active if rank(a) < 9), key=lambda a: (rank(a), as_date(a.get("due")) or date.max))
    excluded = len(active) - len(walk)
    if args.json:
        print(json.dumps({"closeoutDate": closeout.isoformat(),
                          "critical": {k: [a["id"] for a in v] for k, v in buckets.items()},
                          "walk": walk, "excludedCount": excluded}, indent=2, ensure_ascii=False))
        return 0
    print(f"End of day action scan for {closeout.isoformat()} ({len(active)} active)")
    for name, rows in buckets.items():
        print(f"\n{name} ({len(rows)})")
        for action in rows:
            print(f"- {describe(action)}")
    print(f"\nWalk one by one, most urgent first ({len(walk)}):")
    for action in walk:
        reminder = f" | reminder: {action['reminder']}" if action.get("reminder") else ""
        print(f"- {describe(action)} [{action.get('status')}]{reminder}")
    print(f"\nNot walked (update in the canvas Open actions tab): {excluded}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Read and write ba-actions.json, then regenerate ba-actions.md")
    parser.add_argument("--today", default=None, help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)

    add = sub.add_parser("add", help="add one action (or update the matching one)")
    add.add_argument("--task", required=True)
    add.add_argument("--initiative")
    add.add_argument("--priority", choices=PRIORITIES)
    add.add_argument("--due")
    add.add_argument("--remind-on", dest="remind_on")
    add.add_argument("--reminder")
    add.add_argument("--notes")
    add.add_argument("--status", choices=sorted(STATUSES))
    add.add_argument("--tracker-ref", dest="tracker_ref")
    add.add_argument("--source-type", dest="source_type", choices=SOURCE_TYPES)
    add.add_argument("--source-label", dest="source_label")
    add.add_argument("--source-file", dest="source_file")
    add.add_argument("--source-date", dest="source_date")
    add.set_defaults(func=cmd_add)

    ups = sub.add_parser("upsert", help="add or update many actions from a JSON list (file path or - for stdin)")
    ups.add_argument("--json", required=True)
    ups.set_defaults(func=cmd_upsert)

    st = sub.add_parser("set", help="change fields on one action")
    st.add_argument("id")
    st.add_argument("--status", choices=sorted(STATUSES))
    st.add_argument("--reopen", action="store_true", help="allow done/cancelled back to active (user confirmed)")
    st.add_argument("--due")
    st.add_argument("--remind-on", dest="remind_on")
    st.add_argument("--started-on", dest="started_on")
    st.add_argument("--priority", choices=PRIORITIES)
    st.add_argument("--notes")
    st.add_argument("--reminder")
    st.add_argument("--blocker-notes", dest="blocker_notes")
    st.add_argument("--initiative")
    st.add_argument("--task")
    st.set_defaults(func=cmd_set)

    dn = sub.add_parser("done", help="mark one or more actions done")
    dn.add_argument("ids", nargs="+")
    dn.set_defaults(func=cmd_done)

    ls = sub.add_parser("list", help="list open / in progress / blocked actions")
    ls.add_argument("--initiative")
    ls.add_argument("--overdue", action="store_true")
    ls.add_argument("--json", action="store_true")
    ls.set_defaults(func=cmd_list)

    eod = sub.add_parser("eod-scan", help="end of day critical scan (5a) and walk list (5b)")
    eod.add_argument("--closeout-date", default="today")
    eod.add_argument("--json", action="store_true")
    eod.set_defaults(func=cmd_eod_scan)
    return parser


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    args = build_parser().parse_args(argv)
    today = date.fromisoformat(args.today) if args.today else date.today()
    return args.func(args, today)


if __name__ == "__main__":
    sys.exit(main())
