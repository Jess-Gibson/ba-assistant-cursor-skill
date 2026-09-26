# stop hook (--stop): computed unpromoted-state reminder (C3). Off unless
# `stopFollowup: true` in ba-assistant-config.mdc, and even then it nudges at most
# once per conversation. It never runs on each prompt: the package does not register
# a beforeSubmitPrompt hook (Cursor ignores that event's additional_context). The
# non --stop branch at the bottom only lets an old hooks.json entry exit cleanly.
#
# It checks only the initiative session-init.py named for this chat
# (CURSOR_SESSION_CONTEXT_PATH). No named initiative = silent. It never falls back
# to "newest SESSION-CONTEXT.md by modified time".
#
# What it computes (cheap, local-file-only, <50ms):
#   1. Unpromoted DEC-/RISK-/OQ-/ACT-/DEP- lines (no [promoted] tag) -> promote / run /wrap.
#   2. status-data.json older than initiative-tracker.md by >1h -> staleness note.
# Silence when state is clean.

import json, os, re, sys
from pathlib import Path


def stop_followup_enabled() -> bool:
    """Opt-in only (B4c): the stop hook's followup_message auto-submits a ghost
    user turn. Default OFF. Set `stopFollowup: true` in ba-assistant-config.mdc
    to opt in. Absent/false/unparseable config => disabled, matching the
    documented default-off contract."""
    for name in ("ba-assistant-config.mdc", "ba-profile.mdc"):
        path = Path.home() / ".cursor" / "rules" / name
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        for line in text.splitlines():
            m = re.match(r"\s*stopFollowup\s*[:=]\s*(\S+)", line.strip(), re.I)
            if m:
                return m.group(1).strip().strip("\"'").lower() in ("true", "1", "yes", "on")
    return False


def named_session_context():
    ctx = os.environ.get("CURSOR_SESSION_CONTEXT_PATH", "")
    return ctx if ctx and os.path.isfile(ctx) else ""

STOP_MODE = "--stop" in sys.argv
loop_count = 0
try:
    _payload = json.loads(sys.stdin.read() or "{}")
    loop_count = int(_payload.get("loop_count", 0) or 0)
except Exception:
    pass

notes = []
sc = named_session_context()
if sc:
    try:
        text = open(sc, encoding="utf-8", errors="ignore").read()
        unpromoted = [l for l in text.splitlines()
                      if re.match(r'\s*[-*]?\s*(DEC|RISK|OQ|ACT|DEP)-', l.strip())
                      and "[promoted]" not in l]
        if len(unpromoted) >= 3:
            notes.append(f"{len(unpromoted)} unpromoted items in SESSION-CONTEXT (decisions/risks/OQs). "
                         f"Promote to the tracker or suggest /wrap before the session ends.")
        d = os.path.dirname(sc)
        tracker, sd = os.path.join(d, "initiative-tracker.md"), os.path.join(d, "status-data.json")
        if os.path.isfile(tracker) and os.path.isfile(sd):
            if os.path.getmtime(tracker) - os.path.getmtime(sd) > 3600:
                notes.append("status-data.json is stale relative to the tracker — regenerate before any /status, canvas, or publish.")
    except Exception:
        pass

out = ""
if notes:
    out = "STATE REMINDER (computed, sessionState hook): " + " | ".join(notes[:2])

if STOP_MODE:
    # Cursor docs (5 Jul 2026): the stop hook's only supported output is followup_message
    # (auto-submits a user message, i.e. a "ghost" turn the user didn't type). Default OFF
    # (B4c) -- opt in with `stopFollowup: true` in ba-assistant-config.mdc. Nudge at most
    # ONCE per conversation when opted in (loop_count guard); after the agent promotes
    # items they gain [promoted] tags, so the recheck goes silent naturally.
    if out and loop_count == 0 and stop_followup_enabled():
        print(json.dumps({"followup_message":
            "Automated sync check (stop hook): " + " | ".join(notes[:2]) +
            " — promote the items to the tracker (or run /wrap), reply with a one-line confirmation, and stop."}))
    else:
        print(json.dumps({}))
else:
    # Retired beforeSubmitPrompt entry in an old hooks.json: let the prompt through, say nothing.
    print(json.dumps({"continue": True}))
