#!/usr/bin/env python3
"""Generate a portable BA Workboard Cursor Canvas from canonical local data.

The generated canvas is a display surface. Its interactive action edits are
stored in the canvas sidecar and must be applied through the BA Assistant flow.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import date, datetime, timedelta
from pathlib import Path


def read_json(path: Path, default: object) -> object:
    if not path.exists():
        return default
    text = path.read_text(encoding="utf-8-sig")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Older local workboards may contain a trailing comma. Accept that
        # non-canonical display input without ever rewriting the source file.
        # raw_decode deliberately ignores a stray unmatched closing brace after
        # the first valid top-level JSON object.
        cleaned = re.sub(r",(\s*[}\]])", r"\1", text)
        value, _ = json.JSONDecoder().raw_decode(cleaned.lstrip())
        return value


def initiative_name_map(initiatives: list[dict]) -> dict[str, str]:
    return {
        str(item.get("slug")): str(item.get("name") or item.get("slug"))
        for item in initiatives
        if item.get("slug")
    }


def today_meetings(workboard: dict, calendar: dict, today: str) -> list[dict]:
    if isinstance(workboard.get("meetings_today"), list):
        return workboard["meetings_today"]
    if isinstance(calendar.get("meetings"), list):
        return [
            meeting
            for meeting in calendar["meetings"]
            if str(meeting.get("start", "")).startswith(today)
        ]
    for day in calendar.get("days", []):
        if day.get("date") == today:
            return day.get("meetings", [])
    return []


def normalize_downloads(workboard: dict) -> list[str]:
    direct = workboard.get("unprocessed_downloads")
    if isinstance(direct, list):
        return [str(item) for item in direct]
    source = workboard.get("downloads_since_refresh", {})
    if not isinstance(source, dict):
        return []
    return [
        *[str(item) for item in source.get("new_since_last", [])],
        *[str(item) for item in source.get("still_untriaged", [])],
    ]


def normalize_review_queue(workboard: dict) -> list[dict]:
    queue = workboard.get("review_queue", [])
    if isinstance(queue, list):
        return queue
    if isinstance(queue, dict) and isinstance(queue.get("items"), list):
        return queue["items"]
    return []


def iso_day(value: object) -> str | None:
    value = str(value or "")
    return value[:10] if re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:.*)?", value) else None


def priority_queue(actions: list[dict], meetings: list[dict], today: str) -> list[dict]:
    """Build a read-only daily run order from calendar and canonical actions."""
    refresh = {
        "kind": "refresh",
        "title": "Refresh the board before acting on stale evidence",
        "initiative": None,
        "instruction": "Use Update to check calendar, Jira, Downloads and action changes.",
        "reason": "Morning control check",
        "rank": 0,
    }
    urgent_actions: list[dict] = []
    advance_actions: list[dict] = []
    for action in actions:
        due = iso_day(action.get("due"))
        remind = iso_day(action.get("remind_on"))
        status = str(action.get("status", "open"))
        priority = str(action.get("priority", "medium"))
        if status in {"done", "cancelled"}:
            continue
        if due and due < today:
            rank, reason = 1, f"{today} priority: overdue since {due}"
        elif remind and remind <= today:
            rank, reason = 2, "Reminder is due today" if remind == today else f"Reminder overdue since {remind}"
        elif due == today:
            rank, reason = 3, "Due today"
        elif action.get("blocked"):
            rank, reason = 4, "Blocked — resolve or escalate today"
        elif priority == "high" and due == str(date.fromisoformat(today) + timedelta(days=1)):
            rank, reason = 6, "High priority due tomorrow — prepare today"
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
        (urgent_actions if rank < 6 else advance_actions).append(item)
    meeting_items = []
    for meeting in meetings:
        if meeting.get("done") or meeting.get("canceled"):
            continue
        title = str(meeting.get("subject") or meeting.get("label") or "").strip()
        if not title:
            continue
        meeting_items.append({
            "kind": "meeting",
            "title": title,
            "initiative": meeting.get("initiative"),
            "instruction": "Read the relevant context, prepare decisions or questions, then capture and debrief outcomes.",
            "reason": f"Calendar · {meeting.get('time') or str(meeting.get('start', ''))[11:16] or 'Today'}",
            "rank": 5,
        })
    # Calendar commitments must remain visible even when the action backlog is
    # large; keep room for every meeting before filling the queue with advance
    # preparation items.
    urgent_actions.sort(key=lambda item: (item["rank"], item["title"]))
    meeting_items.sort(key=lambda item: item["reason"])
    advance_actions.sort(key=lambda item: (item["rank"], item["title"]))
    available_for_urgent = max(0, 14 - len(meeting_items))
    queue = [refresh, *urgent_actions[:available_for_urgent], *meeting_items]
    return [*queue, *advance_actions][:15]


def build_canvas_data(workboard: dict, actions_data: dict, calendar: dict, today: str) -> dict:
    initiatives = workboard.get("initiatives", [])
    names = initiative_name_map(initiatives)
    actions = []
    for action in actions_data.get("actions", []):
        if action.get("status") in {"done", "cancelled"}:
            continue
        copy = dict(action)
        copy["initiativeName"] = names.get(str(action.get("initiative")), action.get("initiative"))
        actions.append(copy)

    at_risk = sum(
        1 for item in initiatives if item.get("status") in {"at-risk", "critical"}
    )
    high_due = sum(1 for action in actions if action.get("priority") == "high")
    priority_banner = (
        workboard.get("priority_banner")
        or f"{at_risk} initiative(s) at risk. {high_due} high-priority action(s) open."
    )
    return {
        "today": today,
        "refreshed": workboard.get("last_refreshed") or "Not refreshed yet",
        "initiatives": initiatives,
        "actions": actions,
        "meetings": today_meetings(workboard, calendar, today),
        "priorityQueue": priority_queue(actions, today_meetings(workboard, calendar, today), today),
        "downloads": normalize_downloads(workboard),
        "reviewQueue": normalize_review_queue(workboard),
        "syncStatus": workboard.get("sync_status", {}),
        "actionSummary": workboard.get("ba_actions_summary") or workboard.get("jess_actions_summary") or {},
        "atRiskCount": at_risk,
        "priorityBanner": priority_banner,
    }


def default_canvas_path(cursor_home: Path) -> Path | None:
    candidates = sorted((cursor_home / "projects").glob("*/canvases"))
    return candidates[0] / "ba-workboard.canvas.tsx" if len(candidates) == 1 else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate portable BA Workboard canvas")
    parser.add_argument("--cursor-home", type=Path, default=Path.home() / ".cursor")
    parser.add_argument(
        "--source-home",
        type=Path,
        help="Read source _workstream data from this Cursor home; defaults to --cursor-home.",
    )
    parser.add_argument("--canvas", type=Path, help="Absolute target .canvas.tsx path")
    parser.add_argument("--today", default=date.today().isoformat())
    args = parser.parse_args()

    cursor_home = args.cursor_home.expanduser().resolve()
    canvas_path = args.canvas or default_canvas_path(cursor_home)
    if canvas_path is None:
        parser.error(
            "multiple or no Cursor project canvases found; pass --canvas "
            '"C:\\Users\\You\\.cursor\\projects\\<workspace>\\canvases\\ba-workboard.canvas.tsx"'
        )

    package_root = Path(__file__).resolve().parent.parent
    template_path = package_root / "skills" / "ba-assistant" / "templates" / "ba-workboard.canvas.tsx.template"
    template = template_path.read_text(encoding="utf-8")
    source_home = (args.source_home or cursor_home).expanduser().resolve()
    source_workstream = source_home / "_workstream"
    workboard = read_json(source_workstream / "workboard.json", {"initiatives": []})
    actions_path = source_workstream / "ba-actions.json"
    if not actions_path.exists():
        actions_path = source_workstream / "jess-actions.json"
    actions = read_json(actions_path, {"actions": []})
    calendar = read_json(source_workstream / "calendar-feed.json", {"days": []})

    data = build_canvas_data(workboard, actions, calendar, args.today)
    result = template.replace("/* WORKBOARD_DATA */", json.dumps(data, indent=2, ensure_ascii=False))
    canvas_path.parent.mkdir(parents=True, exist_ok=True)
    canvas_path.write_text(result, encoding="utf-8")
    print(f"Generated {canvas_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
