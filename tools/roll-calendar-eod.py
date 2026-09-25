"""EOD calendar roll-forward: next working day becomes Today on workboard + canvas.

Run after workboard step 7 (today's meetings marked done), before canvas generate.
Use your platform's Python launcher: `py` on Windows, `python3` on Mac/Linux.

  py _workstream/roll-calendar-eod.py                                    # Windows
  python3 _workstream/roll-calendar-eod.py                               # Mac/Linux
  python3 _workstream/roll-calendar-eod.py --closeout-date 2026-09-15
  python3 _workstream/roll-calendar-eod.py --workstream /path/to/.cursor/_workstream
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

TZ = timezone(timedelta(hours=12))


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
                if value and value not in {"[Your Name]", "[BA name]", "TBC"}:
                    return value
    return None


def load_ba_name(workstream: Path) -> str | None:
    """Read the configured BA name the same way generate-workboard-canvas.py does,
    so a solo focus block (empty subject, single required attendee) can be
    recognised without hardcoding any one person's name."""
    home = workstream.parent
    text = ""
    for name in ("ba-assistant-config.mdc", "ba-profile.mdc"):
        path = home / "rules" / name
        if path.exists():
            text += path.read_text(encoding="utf-8") + "\n"
    return parse_rule_value(text, "ba_name") or parse_rule_value(text, "name")


def next_working_day(d: date) -> date:
    d = d + timedelta(days=1)
    while d.weekday() >= 5:
        d += timedelta(days=1)
    return d


def meeting_date(start: str) -> date | None:
    if not start or len(start) < 10:
        return None
    try:
        y, m, day = map(int, start[:10].split("-"))
        return date(y, m, day)
    except ValueError:
        return None


def end_time(start: str, dur: int) -> str:
    h, m = int(start[11:13]), int(start[14:16])
    total = h * 60 + m + dur
    return f"{total // 60:02d}:{total % 60:02d}"


def build_workboard_meeting(raw: dict, ba_name: str | None) -> dict:
    subj = raw.get("subject") or ""
    required = str(raw.get("required", "")).strip()
    if not subj.strip() and required and (ba_name is None or required.lower() == ba_name.lower()):
        subj = "(focus block)"
    start = raw.get("start", "")
    return {
        "time": start[11:16] if len(start) >= 16 else "",
        "end": end_time(start, int(raw.get("duration_min", 30))),
        "subject": subj,
        "duration_min": raw.get("duration_min", 0),
        "organizer": raw.get("organizer", ""),
        "done": False,
        "canceled": "cancel" in subj.lower(),
        # Highlighting is data-driven from calendar-feed.json (matches
        # generate-workboard-canvas.py's own reading of raw.get("highlight")),
        # not a hardcoded keyword list -- whatever produces the feed marks
        # the meetings that matter for this BA.
        "highlight": bool(raw.get("highlight")),
        "is_online": raw.get("is_online", True),
    }


def summarize_day(meetings: list[dict]) -> str:
    if not meetings:
        return ""
    highlights = [m for m in meetings if m.get("highlight")]
    picks = highlights[:4] if highlights else meetings[:3]
    parts = []
    for m in picks:
        t = m.get("time", "")
        s = (m.get("subject") or "").strip() or "(block)"
        if len(s) > 40:
            s = s[:37] + "..."
        parts.append(f"{t} {s}" if t else s)
    return "; ".join(parts)


def roll_calendar_eod(workstream: Path, closeout_date: date | None = None) -> dict:
    workstream = workstream.resolve()
    cal_path = workstream / "calendar-feed.json"
    wb_path = workstream / "workboard.json"

    if not cal_path.exists():
        raise FileNotFoundError(f"calendar-feed.json not found: {cal_path}")

    with open(cal_path, encoding="utf-8-sig") as f:
        cal = json.load(f)

    closeout = closeout_date
    if closeout is None and wb_path.exists():
        with open(wb_path, encoding="utf-8") as f:
            wb_probe = json.load(f)
        md = wb_probe.get("meetings_date")
        if md:
            closeout = date(*map(int, md.split("-")))
    if closeout is None:
        closeout = datetime.now(TZ).date()

    today = next_working_day(closeout)
    tomorrow = next_working_day(today)
    ba_name = load_ba_name(workstream)

    all_meetings = cal.get("meetings") or []
    today_raw = [m for m in all_meetings if meeting_date(m.get("start", "")) == today]
    tomorrow_raw = [m for m in all_meetings if meeting_date(m.get("start", "")) == tomorrow]
    # Keep today + tomorrow in feed; drop closeout day and earlier
    kept = [
        m
        for m in all_meetings
        if meeting_date(m.get("start", "")) is not None
        and meeting_date(m.get("start", "")) >= today
    ]

    now = datetime.now(TZ)
    cal["range_start"] = f"{today.isoformat()}T00:00:00.0000000+12:00"
    cal["range_end"] = f"{(tomorrow + timedelta(days=1)).isoformat()}T00:00:00.0000000+12:00"
    cal["meetings"] = kept
    cal["meeting_count"] = len(kept)
    cal["last_updated"] = now.isoformat()
    cal["rolled_from"] = closeout.isoformat()
    cal["rolled_to"] = today.isoformat()
    if not tomorrow_raw:
        cal["note"] = (
            f"EOD roll {closeout.isoformat()} -> {today.isoformat()}. "
            f"{tomorrow.isoformat()} not in feed yet; re-pull Outlook on morning /workboard Update."
        )
    else:
        cal["note"] = f"EOD roll {closeout.isoformat()} -> {today.isoformat()}."

    with open(cal_path, "w", encoding="utf-8") as f:
        json.dump(cal, f, indent=2, ensure_ascii=False)
        f.write("\n")

    meetings_today = [
        build_workboard_meeting(m, ba_name) for m in sorted(today_raw, key=lambda x: x.get("start", ""))
    ]
    meetings_tomorrow = [
        build_workboard_meeting(m, ba_name) for m in sorted(tomorrow_raw, key=lambda x: x.get("start", ""))
    ]

    wb = {}
    if wb_path.exists():
        with open(wb_path, encoding="utf-8") as f:
            wb = json.load(f)

    wb["meetings_date"] = today.isoformat()
    wb["meetings_today"] = meetings_today
    wb["meetings_tomorrow"] = meetings_tomorrow
    wb["meetings_tomorrow_date"] = tomorrow.isoformat()
    if meetings_tomorrow:
        wb["meetings_tomorrow_note"] = summarize_day(meetings_tomorrow)
    elif not tomorrow_raw:
        wb["meetings_tomorrow_note"] = (
            f"{tomorrow.strftime('%a %d %b')}: not in calendar-feed yet. "
            "Re-pull from Outlook on morning /workboard Update."
        )
    else:
        wb["meetings_tomorrow_note"] = f"{tomorrow.strftime('%a %d %b')}: no meetings in feed."

    summary = summarize_day(meetings_today)
    wb["meeting_today"] = (
        f"{today.strftime('%a %d %b')}: {summary}" if summary else f"{today.strftime('%a %d %b')}: no meetings in feed."
    )

    with open(wb_path, "w", encoding="utf-8") as f:
        json.dump(wb, f, indent=2, ensure_ascii=False)
        f.write("\n")

    return {
        "closeout_date": closeout.isoformat(),
        "today": today.isoformat(),
        "tomorrow": tomorrow.isoformat(),
        "today_count": len(meetings_today),
        "tomorrow_count": len(meetings_tomorrow),
        "feed_count": len(kept),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Roll calendar-feed + workboard to next working day (EOD)")
    parser.add_argument(
        "--workstream",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="Path to _workstream folder",
    )
    parser.add_argument(
        "--closeout-date",
        type=str,
        default=None,
        help="Date being closed out (YYYY-MM-DD). Default: workboard meetings_date or today.",
    )
    args = parser.parse_args()

    closeout = None
    if args.closeout_date:
        closeout = date(*map(int, args.closeout_date.split("-")))

    try:
        result = roll_calendar_eod(args.workstream, closeout)
    except FileNotFoundError as exc:
        print(f"Gate: calendar-roll: FAIL ({exc})")
        return 1

    print(
        f"Gate: calendar-roll: PASS "
        f"({result['today_count']} meetings {result['today']}, "
        f"{result['tomorrow_count']} preview {result['tomorrow']})"
    )
    print(
        f"calendar-feed: rolled {result['closeout_date']} -> {result['today']} "
        f"({result['feed_count']} rows kept)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
