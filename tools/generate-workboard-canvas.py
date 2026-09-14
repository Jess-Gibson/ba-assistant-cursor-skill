#!/usr/bin/env python3
"""Generate a portable BA Workboard Cursor Canvas from canonical local data."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, timedelta
from pathlib import Path

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


def posix(path: Path) -> str:
    return str(path).replace("\\", "/")


def read_json(path: Path, default: object) -> object:
    if not path.exists():
        return default
    text = path.read_text(encoding="utf-8-sig")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        cleaned = re.sub(r",(\s*[}\]])", r"\1", text)
        value, _ = json.JSONDecoder().raw_decode(cleaned.lstrip())
        return value


def parse_rule_value(text: str, key: str) -> str | None:
    patterns = [
        rf"^\s*{re.escape(key)}\s*:\s*(.+?)\s*$",
        rf"^\s*{re.escape(key)}\s*=\s*(.+?)\s*$",
    ]
    for line in text.splitlines():
        for pattern in patterns:
            match = re.match(pattern, line.strip())
            if match:
                value = match.group(1).strip().strip('"').strip("'")
                if value and value not in {"[Your Name]", "TBC"}:
                    return value
    return None


def resolve_canvas_path(cursor_home: Path) -> str:
    direct = cursor_home / "projects"
    existing = sorted(direct.glob("*/canvases/ba-workboard.canvas.tsx"))
    if existing:
        return posix(existing[-1])
    canvases = sorted(direct.glob("*/canvases"))
    if len(canvases) == 1:
        return posix(canvases[0] / "ba-workboard.canvas.tsx")
    return posix(cursor_home / "projects" / "<workspace>" / "canvases" / "ba-workboard.canvas.tsx")


def resolve_initiatives_root(cursor_home: Path, rules_text: str) -> str:
    for key in ("initiatives_root", "BA_INITIATIVES_ROOT"):
        value = parse_rule_value(rules_text, key)
        if value:
            return value.replace("\\", "/")
    analysis = cursor_home / "-- analysis --"
    if analysis.exists():
        return posix(analysis)
    initiatives = cursor_home / "initiatives"
    if initiatives.exists():
        return posix(initiatives)
    return posix(cursor_home / "initiatives")


def load_workboard_config(cursor_home: Path) -> dict:
    home = cursor_home.expanduser().resolve()
    workstream = home / "_workstream"
    rules_text = ""
    for name in ("ba-assistant-config.mdc", "ba-profile.mdc"):
        path = home / "rules" / name
        if path.exists():
            rules_text += path.read_text(encoding="utf-8") + "\n"

    ba_name = parse_rule_value(rules_text, "ba_name") or parse_rule_value(rules_text, "name") or "[BA name]"
    stakeholder_name = parse_rule_value(rules_text, "stakeholder_name") or parse_rule_value(
        rules_text, "stakeholder_prep_name"
    )
    downloads = parse_rule_value(rules_text, "BA_DOWNLOADS_PATH") or posix(Path.home() / "Downloads")

    use_jess = (workstream / "jess-actions.json").exists()
    if use_jess:
        actions_file = "jess-actions"
        actions_format = "jess-actions-format.md"
        sync_command = "sync-jess-actions"
        sync_gate = "jess-actions-sync"
        action_id_pattern = "JA-NNN"
        regenerate_script = "regenerate-jess-actions-md.py"
        summary_field = "jess_actions_summary"
    else:
        actions_file = "ba-actions"
        actions_format = "ba-actions-format.md"
        sync_command = "sync-ba-actions"
        sync_gate = "ba-actions-sync"
        action_id_pattern = "BA-NNN"
        regenerate_script = "regenerate-ba-actions-md.py"
        summary_field = "ba_actions_summary"

    return {
        "cursor_home": posix(home),
        "ba_name": ba_name,
        "ba_first_name": ba_name.split()[0] if ba_name not in ("[BA name]", "", "TBC") else "BA",
        "initiatives_root": resolve_initiatives_root(home, rules_text),
        "downloads_path": downloads.replace("\\", "/"),
        "downloads_cmd": f'cmd /c dir "{downloads.replace(chr(92), chr(92)*2)}" /a-d /o-d',
        "actions_file": actions_file,
        "actions_format_file": actions_format,
        "sync_command": sync_command,
        "sync_gate": sync_gate,
        "action_id_pattern": action_id_pattern,
        "regenerate_script": regenerate_script,
        "actions_summary_field": summary_field,
        "stakeholder_name": stakeholder_name,
        "canvas_path": resolve_canvas_path(home),
        "workboard_command": posix(home / "commands" / "workboard.md"),
        "wrap_command": posix(home / "commands" / "wrap.md"),
    }


def parse_iso_date(value: object) -> date | None:
    day = iso_day(value)
    return date.fromisoformat(day) if day else None


def sort_open_actions(actions: list[dict]) -> list[dict]:
    def key(action: dict):
        due = parse_iso_date(action.get("due")) or date.max
        pri = PRIORITY_ORDER.get(str(action.get("priority", "medium")), 9)
        return (due, pri, str(action.get("task") or ""))

    return sorted(actions, key=key)


def today_meetings(workboard: dict, calendar: dict, today: str) -> list[dict]:
    if isinstance(calendar.get("meetings"), list):
        current = [item for item in calendar["meetings"] if str(item.get("start", "")).startswith(today)]
        if current:
            return current
    for day in calendar.get("days", []):
        if day.get("date") == today:
            return day.get("meetings", [])
    if workboard.get("meetings_date") == today and isinstance(workboard.get("meetings_today"), list):
        return workboard["meetings_today"]
    return []


def normalize_downloads(workboard: dict) -> list[str]:
    if isinstance(workboard.get("unprocessed_downloads"), list):
        return [str(item) for item in workboard["unprocessed_downloads"]]
    source = workboard.get("downloads_since_refresh", {})
    if not isinstance(source, dict):
        return []
    return [
        *[str(item) for item in source.get("new_since_last", [])],
        *[str(item) for item in source.get("still_untriaged", [])],
    ]


def iso_day(value: object) -> str | None:
    value = str(value or "")
    return value[:10] if re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:.*)?", value) else None


def clock_minutes(value: object) -> int | None:
    match = re.search(r"(?:T)?(\d{2}):(\d{2})", str(value or ""))
    if not match:
        return None
    hours, minutes = int(match.group(1)), int(match.group(2))
    return hours * 60 + minutes if hours < 24 and minutes < 60 else None


def clock_label(minutes: int) -> str:
    hours, remainder = divmod(minutes, 60)
    suffix = "am" if hours < 12 else "pm"
    twelve_hour = hours % 12 or 12
    return f"{twelve_hour}:{remainder:02d} {suffix}"


def normalized_calendar(meetings: list[dict], work_start: int = 600, work_end: int = 1140) -> tuple[list[dict], list[dict]]:
    blocks: list[dict] = []
    for raw in meetings:
        start = clock_minutes(raw.get("time") or raw.get("start"))
        end = clock_minutes(raw.get("end"))
        if start is None:
            continue
        if end is None:
            end = start + int(raw.get("duration_min") or 30)
        start, end = max(work_start, start), min(work_end, end)
        if end <= start:
            continue
        subject = str(raw.get("subject") or raw.get("label") or "").strip()
        organizer = str(raw.get("organizer") or "").strip()
        cancelled = bool(raw.get("canceled") or raw.get("cancelled") or subject.lower().startswith("canceled:"))
        focus = not subject or subject.lower() in {"focus block", "focus time"}
        blocks.append(
            {
                "start": start,
                "end": end,
                "startLabel": clock_label(start),
                "endLabel": clock_label(end),
                "title": "Focus time" if focus else subject,
                "organizer": organizer,
                "cancelled": cancelled,
                "focus": focus,
                "highlight": bool(raw.get("highlight")),
            }
        )
    blocks.sort(key=lambda item: (item["start"], item["end"], item["title"]))
    clusters: list[list[dict]] = []
    cluster_end = work_start
    for block in blocks:
        if clusters and block["start"] < cluster_end:
            clusters[-1].append(block)
            cluster_end = max(cluster_end, block["end"])
        else:
            clusters.append([block])
            cluster_end = block["end"]
    for cluster in clusters:
        lane_ends: list[int] = []
        for block in cluster:
            for lane, lane_end in enumerate(lane_ends):
                if lane_end <= block["start"]:
                    break
            else:
                lane = len(lane_ends)
                lane_ends.append(block["start"])
            lane_ends[lane] = block["end"]
            block["lane"] = lane
        for block in cluster:
            block["laneCount"] = len(lane_ends)

    occupied = sorted(
        [(block["start"], block["end"]) for block in blocks if not block["cancelled"]],
        key=lambda item: item[0],
    )
    merged: list[list[int]] = []
    for start, end in occupied:
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    free_blocks: list[dict] = []
    cursor = work_start
    for start, end in merged:
        if start > cursor:
            free_blocks.append(
                {
                    "start": cursor,
                    "end": start,
                    "startLabel": clock_label(cursor),
                    "endLabel": clock_label(start),
                    "minutes": start - cursor,
                }
            )
        cursor = max(cursor, end)
    if cursor < work_end:
        free_blocks.append(
            {
                "start": cursor,
                "end": work_end,
                "startLabel": clock_label(cursor),
                "endLabel": clock_label(work_end),
                "minutes": work_end - cursor,
            }
        )
    return blocks, [block for block in free_blocks if block["minutes"] >= 30]


def priority_queue(actions: list[dict], today: str, refreshed_today: bool) -> list[dict]:
    refresh = {
        "kind": "refresh",
        "title": "Refresh the board before acting on stale evidence",
        "initiative": None,
        "instruction": "Use Update to check calendar, Jira, Downloads and action changes.",
        "reason": "Morning control check",
        "rank": 0,
    }
    urgent, advance = [], []
    for action in actions:
        due, remind = iso_day(action.get("due")), iso_day(action.get("remind_on"))
        status, priority = str(action.get("status", "open")), str(action.get("priority", "medium"))
        if status in {"done", "cancelled"}:
            continue
        if due and due < today:
            rank, reason = 1, f"{today} priority: overdue since {due}"
        elif remind and remind <= today:
            rank, reason = 2, "Reminder is due today" if remind == today else f"Reminder overdue since {remind}"
        elif due == today:
            rank, reason = 3, "Due today"
        elif action.get("blocked"):
            rank, reason = 4, "Blocked -- resolve or escalate today"
        elif priority == "high" and due == str(date.fromisoformat(today) + timedelta(days=1)):
            rank, reason = 6, "High priority due tomorrow -- prepare today"
        elif priority == "high":
            rank, reason = 7, "Open high-priority action"
        else:
            continue
        item = {
            "kind": "action",
            "title": str(action.get("task") or "Untitled action"),
            "initiative": action.get("initiativeName") or action.get("initiative"),
            "instruction": "Resolve, progress or explicitly re-plan this action in Open actions.",
            "reason": reason,
            "rank": rank,
            "actionId": action.get("id"),
        }
        (urgent if rank < 6 else advance).append(item)
    urgent.sort(key=lambda item: (item["rank"], item["title"]))
    advance.sort(key=lambda item: (item["rank"], item["title"]))
    refresh_item = [] if refreshed_today else [refresh]
    return [*refresh_item, *urgent, *advance][:15]


def normalize_stakeholder_raise(workboard: dict, config: dict) -> dict:
    raw = workboard.get("stakeholder_raise") or workboard.get("alice_raise") or {}
    name = raw.get("name") or config.get("stakeholder_name")
    if not name and workboard.get("alice_raise"):
        name = "Alice"
    items: list[dict] = []
    for item in raw.get("items") or []:
        if item.get("status") != "open":
            continue
        topic = str(item.get("topic") or "")
        ask = str(item.get("ask") or "")
        kind = "fyi"
        if not topic.upper().startswith("FYI") and "no decision needed" not in ask.lower():
            kind = "ask"
        items.append(
            {
                "id": item.get("id"),
                "topic": topic,
                "initiative": item.get("initiative"),
                "ask": ask,
                "context": item.get("context"),
                "priority": item.get("priority", "medium"),
                "kind": kind,
            }
        )
    priority_order = {"high": 0, "medium": 1, "low": 2}
    items.sort(
        key=lambda row: (
            0 if row["kind"] == "ask" else 1,
            priority_order.get(str(row["priority"]), 9),
            row["topic"],
        )
    )
    asks = [row for row in items if row["kind"] == "ask"]
    fyis = [row for row in items if row["kind"] == "fyi"]
    meeting_note = raw.get("meetingNote") or raw.get("meeting_today")
    visible = bool(name and (asks or fyis or meeting_note))
    return {
        "visible": visible,
        "name": name or "",
        "description": raw.get("description"),
        "meetingNote": meeting_note,
        "lastRefreshed": raw.get("last_refreshed"),
        "asks": asks,
        "fyis": fyis,
        "openCount": len(items),
        "askCount": len(asks),
        "sourceField": "stakeholder_raise" if workboard.get("stakeholder_raise") else (
            "alice_raise" if workboard.get("alice_raise") else None
        ),
    }


def build_update_prompt(config: dict) -> str:
    ba = config["ba_first_name"]
    return f"""/workboard

This is a morning or mid-day refresh of my daily operating surface. Do the full workboard procedure. Do not stop at a one-line summary. The goal is an honest Today queue I can run from: real priorities, real initiative health, current calendar, and current {ba} actions.

Read first, then follow:
- skills/ba-assistant/references/workboard-procedure.md
- skills/ba-assistant/references/workboard-format.md (score initiative status from evidence; never default to on-track)
- skills/ba-assistant/references/{config['actions_format_file']} section 4b Daily update
- _workstream/{config['actions_file']}.md and _workstream/{config['actions_file']}.json
- _workstream/calendar-feed.json
- _workstream/workboard.json
- {config['workboard_command']}

Initiative state lives under {config['initiatives_root']}/{{slug}}/. Read SESSION-CONTEXT.md (tail about 50 lines) and initiative-tracker.md when present. Do not glob the .cursor root.

Then:
1. Refresh calendar for today and the next working day into workboard.json.
2. Morning-prep scan of {ba} actions: overdue; remind_on today or overdue; due today; blocked items that today's meetings could unblock; then high-priority due tomorrow. Surface these first in chat, not buried in the full list.
3. For each initiative, refresh phase, milestone, blocker, risk, next action, and status from canonical files. Score status using workboard-format.md.
4. Downloads: run {config['downloads_cmd']} (never Get-ChildItem). Triage files newer than last_refreshed. Skip installers, zips, lnk, ini.
5. Jira movement for initiatives with jira_project. If Jira is unavailable, record unable to check and continue.
6. Run {config['sync_command']} only if a debrief or tracker added {ba}-owned actions, then py _workstream/{config['regenerate_script']}.
7. Write the snapshot to _workstream/workboard.json (including {config['actions_summary_field']}, downloads, last_refreshed). Keep Today as a read-only ordered day plan. Editable status, due, and notes belong only on Open actions.
8. Generate the canvas from the portable template so these button prompts survive:
   py _workstream/generate-workboard-canvas.py --cursor-home "{config['cursor_home']}" --canvas "{config['canvas_path']}"
9. Keep tabs Today / Initiatives / Open actions, optional Stakeholder raise when configured, and buttons Update, End of Day, Save staged updates.

Do not walk every open {ba} action (that is End of Day). Optional short AskQuestion only on today's remind or due items if yesterday was not closed out.

End with: what changed, the ordered Today queue, and AskQuestion for which priority to tackle first."""


def build_eod_prompt(config: dict) -> str:
    ba = config["ba_first_name"]
    return f"""/wrap

This is end-of-day closeout so tomorrow's board and {ba} actions are honest. Follow skills/ba-assistant/references/sync-procedures.md (Full end-of-day closeout sequence) in full. Do not skip steps. Do not output only a summary.

Also read:
- skills/ba-assistant/references/{config['actions_format_file']} section 4b End of day
- skills/ba-assistant/references/workboard-procedure.md
- skills/ba-assistant/references/workboard-format.md
- _workstream/{config['actions_file']}.md
- _workstream/{config['actions_file']}.json
- _workstream/calendar-feed.json
- {config['wrap_command']}

Cursor home: {config['cursor_home']}
Initiative folders: {config['initiatives_root']}/{{slug}}/

Do these in order:

0. EOD critical scan first (before meetings). From {config['actions_file']}.json, call out overdue, due today, remind today, and high items I said I would finish today. Say plainly what is still open.

1. Downloads. Run {config['downloads_cmd']} (never Get-ChildItem). Triage all file types newer than last session. Process relevant files into the matching SESSION-CONTEXT.md.

2. Meeting reconciliation from calendar-feed.json. Table: Time | Meeting | Initiative | Captured? List only uncaptured meetings that involved other people (skip solo blocks).

3. Per-meeting AskQuestion recall for each uncaptured meeting, then a catch-all for Slack, side conversations, and hallway agreements. Write captures to the relevant SESSION-CONTEXT.md with a dated header and a Captured tag.

4. Full-file state validation across all initiatives (entire SESSION-CONTEXT.md, initiative-tracker.md, status-data.json). Report drift with item counts. Do not invent owners or dates.

5. Action runthrough. Walk every open, in_progress, or blocked {ba} action one-by-one, highest urgency first, using AskQuestion: Done, In progress, Follow up, Move deadline, Cancel, No update. Write {config['actions_file']}.json after answers. Then py _workstream/{config['regenerate_script']} and print Gate: {config['sync_gate']}: PASS/FAIL.

6. Promote unpromoted SESSION-CONTEXT items to the tracker, tagged [promoted]. Then run {config['sync_command']} again.

7. Refresh _workstream/workboard.json: rescore initiative status (never default to on-track), recalc milestone days_out, mark today's meetings done, set last_refreshed now.

8. Generate canvases/ba-workboard.canvas.tsx from the portable template:
   py _workstream/generate-workboard-canvas.py --cursor-home "{config['cursor_home']}" --canvas "{config['canvas_path']}"
   Preserve Today / Initiatives / Open actions, optional Stakeholder raise, and Update, End of Day, Save staged updates. Today stays read-only.

9. Next-working-day prep (skip Sat/Sun unless critical meetings remain today). Include Reminders (commitments to start) from remind_on / due tomorrow, plus one concrete first action before standup.

10. Mandatory output: heading New thread: copy from here. Fill every section of the sync-procedures.md step 10 template (where to start, then, reminders, skills, canonical files, session state, meetings, blockers, do not). Not a one-liner.

If something cannot be checked (Jira, email), say unable to check and continue."""


def build_apply_prompt_prefix(config: dict) -> str:
    return (
        f"Apply the workboard action drafts below. Validate {config['action_id_pattern']} IDs and allowed "
        f"statuses/dates in _workstream/{config['actions_file']}.json, write only valid changes, regenerate "
        f"{config['actions_file']}.md with py _workstream/{config['regenerate_script']}, then refresh the "
        f"workboard canvas."
    )


def build_data(workboard: dict, actions_data: dict, calendar: dict, today: str, config: dict) -> dict:
    initiatives = workboard.get("initiatives", [])
    names = {str(item.get("slug")): str(item.get("name") or item.get("slug")) for item in initiatives if item.get("slug")}
    actions = []
    for action in actions_data.get("actions", []):
        if action.get("status") in {"done", "cancelled"}:
            continue
        row = dict(action)
        row["initiativeName"] = names.get(str(action.get("initiative")), action.get("initiative"))
        actions.append(row)
    actions = sort_open_actions(actions)
    meetings = today_meetings(workboard, calendar, today)
    calendar_blocks, free_blocks = normalized_calendar(meetings)
    refreshed = str(workboard.get("last_refreshed") or "")
    refreshed_today = refreshed.startswith(today)
    top_action = next((item for item in priority_queue(actions, today, refreshed_today) if item["kind"] == "action"), None)
    go_live_today = [
        str(initiative.get("next_milestone", {}).get("what"))
        for initiative in initiatives
        if str(initiative.get("next_milestone", {}).get("date", ""))[:10] == today
    ]
    suggested_focus = None
    suitable_gap = next((gap for gap in free_blocks if gap["minutes"] >= 60), None)
    if top_action and suitable_gap:
        suggested_focus = {
            "startLabel": suitable_gap["startLabel"],
            "endLabel": suitable_gap["endLabel"],
            "title": top_action["title"],
            "instruction": top_action["instruction"],
        }
    at_risk = sum(1 for item in initiatives if item.get("status") in {"at-risk", "critical"})
    high = sum(1 for item in actions if item.get("priority") == "high")
    summary = workboard.get(config["actions_summary_field"]) or workboard.get("ba_actions_summary") or workboard.get(
        "jess_actions_summary"
    ) or {}
    stakeholder = normalize_stakeholder_raise(workboard, config)
    return {
        "today": today,
        "refreshed": workboard.get("last_refreshed") or "Not refreshed yet",
        "actionsSync": actions_data.get("last_synced") or "",
        "initiatives": initiatives,
        "actions": actions,
        "meetings": meetings,
        "calendarBlocks": calendar_blocks,
        "freeBlocks": free_blocks,
        "suggestedFocus": suggested_focus,
        "refreshedToday": refreshed_today,
        "priorityQueue": priority_queue(actions, today, refreshed_today),
        "focusSummary": {
            "mustDo": top_action["title"] if top_action else None,
            "goLiveToday": go_live_today,
        },
        "downloads": normalize_downloads(workboard),
        "syncStatus": workboard.get("sync_status", {}),
        "actionSummary": summary,
        "atRiskCount": at_risk,
        "priorityBanner": workboard.get("priority_banner")
        or f"{at_risk} initiative(s) at risk. {high} high-priority action(s) open.",
        "stakeholderRaise": stakeholder,
        "ui": {
            "actionsFile": config["actions_file"],
            "actionsLabel": config["ba_first_name"],
        },
        "prompts": {
            "update": build_update_prompt(config),
            "eod": build_eod_prompt(config),
            "applyPrefix": build_apply_prompt_prefix(config),
        },
    }


def resolve_template_path(cursor_home: Path) -> Path:
    installed = cursor_home / "skills" / "ba-assistant" / "templates" / "ba-workboard.canvas.tsx.template"
    if installed.exists():
        return installed
    package_root = Path(__file__).resolve().parent.parent
    packaged = package_root / "skills" / "ba-assistant" / "templates" / "ba-workboard.canvas.tsx.template"
    if packaged.exists():
        return packaged
    raise FileNotFoundError(f"Workboard canvas template not found under {installed} or {packaged}")


def resolve_actions_path(workstream: Path, config: dict) -> Path:
    preferred = workstream / f"{config['actions_file']}.json"
    if preferred.exists():
        return preferred
    for name in ("jess-actions", "ba-actions"):
        candidate = workstream / f"{name}.json"
        if candidate.exists():
            return candidate
    return preferred


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate the BA Workboard canvas")
    parser.add_argument("--cursor-home", type=Path, default=Path.home() / ".cursor")
    parser.add_argument("--source-home", type=Path, help="Read _workstream data from this home (defaults to --cursor-home)")
    parser.add_argument("--canvas", type=Path, help="Absolute target .canvas.tsx path")
    parser.add_argument("--today", default=date.today().isoformat())
    args = parser.parse_args()

    home = args.cursor_home.expanduser().resolve()
    source_home = (args.source_home or home).expanduser().resolve()
    workstream = source_home / "_workstream"
    config = load_workboard_config(home)
    if args.canvas:
        config["canvas_path"] = posix(args.canvas.expanduser().resolve())

    workboard = read_json(workstream / "workboard.json", {"initiatives": []})
    actions = read_json(resolve_actions_path(workstream, config), {"actions": []})
    calendar = read_json(workstream / "calendar-feed.json", {"days": []})
    template = resolve_template_path(home).read_text(encoding="utf-8")
    data = build_data(workboard, actions, calendar, args.today, config)
    result = template.replace("/* WORKBOARD_DATA */", json.dumps(data, indent=2, ensure_ascii=False))
    canvas_path = Path(config["canvas_path"])
    canvas_path.parent.mkdir(parents=True, exist_ok=True)
    canvas_path.write_text(result, encoding="utf-8")
    print(f"Generated {canvas_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
