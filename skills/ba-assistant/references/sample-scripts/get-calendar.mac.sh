#!/usr/bin/env bash
# Sample calendar feed for macOS — BA Assistant /workboard
# Writes: ~/.cursor/_workstream/calendar-feed.json
# Optional: copy to ~/.cursor/hooks/ and wire into hooks.json sessionStart yourself.
# Requires: macOS + Calendar.app access (osascript). Adapt for Google Calendar / icalBuddy if needed.
#
# Usage: bash get-calendar.mac.sh [days_ahead]
# Default days_ahead = 2

set -euo pipefail

DAYS_AHEAD="${1:-2}"
OUT="${HOME}/.cursor/_workstream/calendar-feed.json"
mkdir -p "$(dirname "$OUT")"

# AppleScript pulls events from Calendar for the next N days.
# Grant Automation / Calendar permission when prompted.
JSON=$(osascript <<EOF
set daysAhead to $DAYS_AHEAD
set startDate to current date
set time of startDate to 0
set endDate to startDate + (daysAhead * days)
set output to ""
tell application "Calendar"
  set eventCount to 0
  repeat with c in calendars
    try
      set evs to (every event of c whose start date ≥ startDate and start date < endDate)
      repeat with e in evs
        set eventCount to eventCount + 1
        if eventCount > 50 then exit repeat
        set subj to summary of e
        set s to start date of e
        set en to end date of e
        set loc to ""
        try
          set loc to location of e
        end try
        -- Build a simple pipe-delimited line; Python/JSON shaping below is easier in shell
        set output to output & subj & "|||" & (s as string) & "|||" & (en as string) & "|||" & loc & linefeed
      end repeat
    end try
    if eventCount > 50 then exit repeat
  end repeat
end tell
return output
EOF
) || {
  echo "Calendar access failed. Writing empty feed."
  cat > "$OUT" <<EMPTY
{"last_updated":"$(date -u +"%Y-%m-%dT%H:%M:%SZ")","range_start":"","range_end":"","meeting_count":0,"meetings":[],"error":"Calendar access failed"}
EMPTY
  exit 0
}

# Shape JSON with Python for stable ISO-ish output
export CAL_RAW="$JSON"
export CAL_OUT="$OUT"
export CAL_DAYS="$DAYS_AHEAD"
python3 - <<'PY'
import json, os, datetime as dt
raw = os.environ.get("CAL_RAW", "")
out = os.environ["CAL_OUT"]
days = int(os.environ.get("CAL_DAYS", "2"))
meetings = []
for line in raw.splitlines():
    if not line.strip() or "|||" not in line:
        continue
    parts = line.split("|||")
    if len(parts) < 3:
        continue
    meetings.append({
        "subject": parts[0],
        "start": parts[1],
        "end": parts[2],
        "location": parts[3] if len(parts) > 3 else "",
        "organizer": "",
        "required": "",
        "is_all_day": False,
        "is_online": "Teams" in (parts[3] if len(parts) > 3 else "") or "Zoom" in (parts[3] if len(parts) > 3 else ""),
        "duration_min": None,
        "body_preview": "",
    })
now = dt.datetime.now().astimezone()
payload = {
    "last_updated": now.isoformat(),
    "range_start": now.replace(hour=0, minute=0, second=0, microsecond=0).isoformat(),
    "range_end": (now.replace(hour=0, minute=0, second=0, microsecond=0) + dt.timedelta(days=days)).isoformat(),
    "meeting_count": len(meetings),
    "meetings": meetings,
}
with open(out, "w", encoding="utf-8") as f:
    json.dump(payload, f, indent=2)
print(f"Calendar feed written: {len(meetings)} meetings to {out}")
PY
