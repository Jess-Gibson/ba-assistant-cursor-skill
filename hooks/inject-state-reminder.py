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


def config_initiatives_root() -> str:
    """paths.initiativesRoot from ba-assistant-config.mdc (setup writes it there;
    it does not set an environment variable)."""
    path = Path.home() / ".cursor" / "rules" / "ba-assistant-config.mdc"
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""
    m = re.search(r'^\s*initiativesRoot\s*:\s*["\']?([^"\'#\n]+)', text, re.M)
    return os.path.expanduser(m.group(1).strip()) if m else ""


def newest_session_context():
    cands = []
    ctx = os.environ.get("CURSOR_SESSION_CONTEXT_PATH", "")
    if ctx and os.path.isfile(ctx):
        return ctx
    roots = [os.environ.get("BA_INITIATIVES_ROOT", "") or config_initiatives_root(),
             os.path.expanduser("~/.cursor/initiatives"),
             # Legacy fallbacks so an older setup still works.
             os.path.expanduser("~/.cursor/Initiatives"),
             os.path.expanduser("~/.cursor/blueprints"),
             os.path.expanduser("~/ba-initiatives")]
    seen = set()
    for root in roots:
        if not root or root in seen:
            continue
        seen.add(root)
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
    # beforeSubmitPrompt: additional_context is NOT a documented output for this event
    # (docs list continue/user_message only). Emitted anyway - harmless if ignored,
    # future-proof if Cursor adds support. continue:true keeps the prompt flowing.
    print(json.dumps({"continue": True, "additional_context": out}))
