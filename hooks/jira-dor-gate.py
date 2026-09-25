import json, os, re, sys, glob

MIN_MATCH_LEN = 6  # minimum normalised length before a title/key may be used in ANY match.
                    # Blocks Hole A (empty-string wildcard: "" in anything == True in Python).

def log(msg):
    try:
        print(f"[jira-dor-gate] {msg}", file=sys.stderr)
    except Exception:
        pass

def out(permission, agent="", user=""):
    # Cursor hooks docs (checked 5 Jul 2026): output fields are snake_case
    # (agent_message / user_message). camelCase kept for back-compat.
    print(json.dumps({"permission": permission, "agent_message": agent, "user_message": user,
                      "agentMessage": agent, "userMessage": user}))
    sys.exit(0)

try:
    payload = json.loads(sys.stdin.read())
except Exception as e:
    # We don't even know what tool this is for -> can't attribute this to a Story create.
    # Fail open here matches hooks.json's failClosed:false contract for "we genuinely don't know".
    log(f"could not parse hook payload from stdin: {e}")
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

# --- Which MCP tool is this? Key off the actual tool-name field the hook delivers, not a ---
# --- hardcoded/stale server+tool name assumption. Cursor's beforeMCPExecution payload    ---
# --- carries the tool identity under one of these keys depending on server/runtime; try  ---
# --- them in order and only fall back to a whole-payload text scan if none is present    ---
# --- (and then ONLY to decide whether the gate applies at all -- never to grant a pass).  ---
def get_tool_name(p):
    for key in ("tool_name", "toolName", "tool", "mcp_tool_name", "mcpToolName"):
        v = p.get(key)
        if isinstance(v, str) and v.strip():
            return v.strip()
    return ""

tool_name = get_tool_name(payload)
CREATE_ISSUE_RE = re.compile(r'create.{0,12}(jira)?.{0,12}issue|jira.{0,12}create', re.I)

if tool_name:
    is_create_call = bool(CREATE_ISSUE_RE.search(tool_name))
else:
    is_create_call = bool(CREATE_ISSUE_RE.search(blob))

if not is_create_call:
    out("allow")

# Read the actual arguments being sent, not the whole hook envelope (conversation id,
# tool name, etc). Falls back to the whole payload only if tool_input isn't a dict
# (malformed/unexpected shape) so we still have a shot at finding fields.
args_source = payload.get("tool_input") if isinstance(payload.get("tool_input"), dict) else payload

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
find_issuetype(args_source)

if issuetype and issuetype != "story":
    out("allow")            # explicit non-story type (spike, bug, enabler, chore, task)
if not issuetype and not re.search(r'\bstory\b', blob, re.I):
    out("allow")            # no type found and nothing story-ish in the call

# Pull the summary/title and (if this is really an edit of an already-keyed issue) the
# issue key, for matching against the tracker.
summary = ""
story_key = ""
def walk(o):
    global summary, story_key
    if isinstance(o, dict):
        for k, v in o.items():
            lk = k.lower()
            if lk == "summary" and isinstance(v, str) and not summary:
                summary = v.lower()
            elif lk in ("issueidorkey", "issuekey", "key") and isinstance(v, str) and not story_key:
                story_key = v.lower()
            walk(v)
    elif isinstance(o, list):
        for i in o:
            walk(i)
walk(args_source)


def norm_text(s):
    s = str(s or "").strip().lower()
    return re.sub(r'\s+', ' ', s)


def is_pass_result(raw):
    # Normalise case/whitespace/punctuation before comparing, so "DoR:PASS", "dor - pass",
    # "DOR PASS", "Pass" etc are all recognised -- but this is ONLY normalisation of the
    # tracker's own result field, never a substitute for binding to the right row (Hole A/B).
    n = re.sub(r'[^a-z0-9\s]', ' ', str(raw or "").lower())
    n = re.sub(r'\s+', ' ', n).strip()
    if not n:
        return False
    tokens = set(n.split())
    if not tokens:
        return False
    if tokens & {"fail", "failed", "not", "pending", "partial", "no"}:
        return False
    return bool(tokens & {"pass", "passed"})


def row_matches_story(chk, story_key, summary):
    # Bind the DoR pass to the SPECIFIC story being created, never to "does the tracker
    # contain a pass anywhere" (Hole B) and never via an empty/near-empty title acting as
    # a wildcard (Hole A).
    row_key = norm_text(chk.get("storyKey", ""))
    row_title = norm_text(chk.get("storyTitle", ""))
    sk = norm_text(story_key)
    sm = norm_text(summary)

    if sk and row_key:
        return len(sk) >= 3 and len(row_key) >= 3 and row_key == sk

    if len(row_title) < MIN_MATCH_LEN or len(sm) < MIN_MATCH_LEN:
        return False
    if row_title == sm:
        return True
    # Truncation-only fallback (a stored/displayed title got cut off, e.g. the original
    # code's `summary[:40]` convention) -- NOT open substring containment. A short,
    # generic phrase like "SSO integration" must not match merely because some unrelated,
    # much longer, already-passed row's title happens to contain it somewhere in the
    # middle. Only accept a PREFIX relationship, and only when the shorter side is close
    # in length to the longer side (>= 70%), so real truncation still matches but a short
    # common substring inside a long unrelated title does not.
    shorter, longer = (row_title, sm) if len(row_title) <= len(sm) else (sm, row_title)
    if len(shorter) < 0.7 * len(longer):
        return False
    return longer.startswith(shorter)


def find_initiative_dirs():
    dirs = []
    ctx = os.environ.get("CURSOR_SESSION_CONTEXT_PATH", "")
    if ctx and os.path.isfile(ctx):
        dirs.append(os.path.dirname(ctx))
    root = os.environ.get("BA_INITIATIVES_ROOT", "")
    if root and os.path.isdir(root):
        dirs += [os.path.dirname(p) for p in glob.glob(os.path.join(root, "**", "status-data.json"), recursive=True)]
    return dirs


allowed = False
parse_error = False

for d in find_initiative_dirs():
    sd = os.path.join(d, "status-data.json")
    if not os.path.isfile(sd):
        continue
    try:
        data = json.load(open(sd, encoding="utf-8", errors="ignore"))
    except Exception as e:
        log(f"failed to parse {sd}: {e}")
        parse_error = True
        continue
    if not isinstance(data, dict):
        log(f"unexpected status-data.json shape in {sd}: top level is not an object")
        parse_error = True
        continue
    checks = data.get("dorChecks", [])
    if not isinstance(checks, list):
        log(f"unexpected status-data.json shape in {sd}: dorChecks is not a list")
        parse_error = True
        continue
    for chk in checks:
        if not isinstance(chk, dict):
            continue
        result = chk.get("firstAttempt", chk.get("result", ""))
        if is_pass_result(result) and row_matches_story(chk, story_key, summary):
            allowed = True
            break
    if allowed:
        break

if allowed:
    out("allow")

if parse_error:
    log("denying Story create/edit: status-data.json was unreadable or malformed for this initiative")
    out("deny",
        agent=("BLOCKED by DoR gate (jira-dor-gate hook): a Story is being created in Jira but this "
               "initiative's status-data.json tracker could not be read (malformed or unexpected shape), "
               "so no DoR evidence could be checked. Fix the tracker file (or re-run the DoR check once "
               "it's readable) and retry. This block applies only to this Story; other Jira work and other "
               "tool calls are unaffected."),
        user="Story blocked: the DoR tracker file couldn't be read, so DoR status can't be confirmed. Fix the tracker and retry.")

out("deny",
    agent=("BLOCKED by DoR gate (jira-dor-gate hook): a Story is being created in Jira with no verified "
           "Definition of Ready pass recorded for THIS specific story in the tracker. Ask the BA to confirm "
           "DoR status for this story (run the DoR section of ba-story-writing), or have the PM log an "
           "explicit override decision in the tracker and reference it on the ticket, then retry."),
    user="Story creation blocked: no verified DoR pass recorded for this specific story. Confirm DoR status with the BA, or log a PM override decision in the tracker, then retry.")
