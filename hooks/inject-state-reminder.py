# beforeSubmitPrompt hook — computed context injection (C3).
# Replaces static always-on reminder rules with ONE relevant line per turn, computed
# from actual state. Cuts the always-on tax AND fires reliably (it's code, not vibes).
#
# stdin: hook JSON (user prompt etc — verify field names against current Cursor docs)
# stdout: {"additional_context": "..."} (empty string = inject nothing)
#
# What it computes (cheap, local-file-only, <50ms):
#   1. Unpromoted items in the newest SESSION-CONTEXT.md (DEC-/RISK-/OQ-/ACT-/DEP-
#      lines without a [promoted] tag) → reminder to promote / run /wrap.
#   2. status-data.json older than initiative-tracker.md by >1h → staleness note.
# One line max. Silence when state is clean — the reminder only exists when earned.

import json, os, re, sys, glob, time

def newest_session_context():
    cands = []
    ctx = os.environ.get("CURSOR_SESSION_CONTEXT_PATH", "")
    if ctx and os.path.isfile(ctx):
        return ctx
    for root in filter(None, [os.environ.get("BA_INITIATIVES_ROOT", ""),
                              os.path.expanduser("~/.cursor/blueprints"),
                              os.path.expanduser("~/ba-initiatives")]):
        cands += glob.glob(os.path.join(root, "**", "SESSION-CONTEXT.md"), recursive=True)
    return max(cands, key=os.path.getmtime) if cands else ""

STOP_MODE = "--stop" in sys.argv
loop_count = 0
try:
    _payload = json.loads(sys.stdin.read() or "{}")
    loop_count = int(_payload.get("loop_count", 0) or 0)
except Exception:
    pass

notes = []
sc = newest_session_context()
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
    # (auto-submits a user message). Nudge ONCE per conversation (loop_count guard); after the
    # agent promotes items they gain [promoted] tags, so the recheck goes silent naturally.
    if out and loop_count == 0:
        print(json.dumps({"followup_message":
            "Automated sync check (stop hook): " + " | ".join(notes[:2]) +
            " — promote the items to the tracker (or run /wrap), reply with a one-line confirmation, and stop."}))
    else:
        print(json.dumps({}))
else:
    # beforeSubmitPrompt: additional_context is NOT a documented output for this event
    # (docs list continue/user_message only). Emitted anyway - harmless if ignored,
    # future-proof if Cursor adds support. continue:true keeps the prompt flowing.
    print(json.dumps({"continue": True, "additional_context": out}))
