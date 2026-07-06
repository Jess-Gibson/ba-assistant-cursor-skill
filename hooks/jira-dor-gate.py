import json, os, re, sys, glob

def out(permission, agent="", user=""):
    # Cursor hooks docs (checked 5 Jul 2026): output fields are snake_case
    # (agent_message / user_message). camelCase kept for back-compat.
    print(json.dumps({"permission": permission, "agent_message": agent, "user_message": user,
                      "agentMessage": agent, "userMessage": user}))
    sys.exit(0)

try:
    payload = json.loads(sys.stdin.read())
except Exception:
    out("allow")

# beforeMCPExecution delivers tool_input as a JSON-params STRING (Cursor docs, 5 Jul 2026).
# Parse it so the issuetype/summary walkers can see inside.
ti = payload.get("tool_input")
if isinstance(ti, str):
    try:
        payload["tool_input"] = json.loads(ti)
    except Exception:
        pass

blob = json.dumps(payload).lower()

# Not a Jira create-issue call → allow. (Matches common MCP tool namings.)
if not re.search(r'create.{0,12}(jira)?.{0,12}issue|jira.{0,12}create', blob):
    out("allow")

# Extract the issue type if findable; only gate Stories.
issuetype = ""
def find_issuetype(o):
    global issuetype
    if isinstance(o, dict):
        for k, v in o.items():
            if k.lower() == "issuetype":
                if isinstance(v, dict):
                    issuetype = str(v.get("name", "")).lower()
                elif isinstance(v, str):
                    issuetype = v.lower()
            find_issuetype(v)
    elif isinstance(o, list):
        for i in o:
            find_issuetype(i)
find_issuetype(payload)

if issuetype and issuetype != "story":
    out("allow")            # explicit non-story type (spike, bug, enabler, task)
if not issuetype and 'story' not in blob:
    out("allow")            # no type found and nothing story-ish in the call

# (a) DoR marker stamped in the payload itself
if re.search(r'dor[:\s\-]*pass', blob):
    out("allow")

# (b) dorChecks lookup in the active initiative
def find_initiative_dirs():
    dirs = []
    ctx = os.environ.get("CURSOR_SESSION_CONTEXT_PATH", "")
    if ctx and os.path.isfile(ctx):
        dirs.append(os.path.dirname(ctx))
    root = os.environ.get("BA_INITIATIVES_ROOT", "")
    if root and os.path.isdir(root):
        dirs += [os.path.dirname(p) for p in glob.glob(os.path.join(root, "**", "status-data.json"), recursive=True)]
    return dirs

# Try to pull the summary being created, for matching
summary = ""
def walk(o):
    global summary
    if isinstance(o, dict):
        for k, v in o.items():
            if k.lower() == "summary" and isinstance(v, str):
                summary = v.lower()
            walk(v)
    elif isinstance(o, list):
        for i in o:
            walk(i)
walk(payload)

for d in find_initiative_dirs():
    # Post E-promote: tracker owns DoR results
    tracker = os.path.join(d, "initiative-tracker.md")
    if os.path.isfile(tracker):
        try:
            t = open(tracker, encoding="utf-8", errors="ignore").read().lower()
            if summary and summary[:40] in t and re.search(r'dor[^\n]{0,40}pass', t):
                out("allow")
        except Exception:
            pass
    # Pre E-promote: status-data.json dorChecks
    sd = os.path.join(d, "status-data.json")
    if os.path.isfile(sd):
        try:
            data = json.load(open(sd, encoding="utf-8", errors="ignore"))
            for chk in data.get("dorChecks", []):
                title = str(chk.get("storyTitle", chk.get("storyKey", ""))).lower()
                result = str(chk.get("firstAttempt", "")).lower()
                if result == "pass" and summary and (title in summary or summary[:40] in title):
                    out("allow")
        except Exception:
            pass

out("deny",
    agent=("BLOCKED by DoR gate (jira-dor-gate hook): a Story is being created in Jira with no "
           "evidence of a Definition of Ready pass. Run the DoR section of ba-story-writing for this "
           "story first; a passing story is stamped 'DoR: PASS' in its description and logged to the "
           "DoR checks register. If the PM is explicitly overriding, log the override decision in the "
           "tracker and include 'DoR: PASS (override, see decision D-NNN)' in the ticket."),
    user="Story creation blocked: no DoR pass recorded for this story. Run the DoR check first (or log a PM override).")
