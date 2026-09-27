"""beforeMCPExecution hook: the one gate every MCP call passes through.

Runlayer is the only MCP path, so every call arrives as Runlayer `execute_tool`
with the real tool name inside tool_input:
    execute_tool { "tool_name": "createJiraIssue", "arguments": {...} }
This hook unwraps that (as the DoR gate always has), then decides:

  deny   email send / reply / forward / draft (Outlook or any mail tool).
         BA Assistant never sends email or creates Outlook drafts; the text goes
         in chat (or a local .md file) for the BA to copy.
  ask    any other external write: Jira, Confluence, calendar, Miro, Slack/Teams
         posts. Cursor shows an approval dialog; the BA's click is the decision.
  allow  reads (get / search / list / fetch / ...), so reads never prompt.

Unknown tool names (no verb we recognise) get "ask": the hook is the safety net
whatever auto-run setting the BA uses.

Story creates in Jira also run the Definition of Ready check
(_workstream/dor-check.py, recomputed from the initiative files every time; a
stored pass is never trusted). A Story is still a Jira write, so the BA always
gets the approval dialog: "DoR met" when every criterion passes, otherwise
"DoR not met: <missing>. Approve to create anyway as a BA override."

Every decision is appended to ~/.cursor/_workstream/audit-log.jsonl: tool name
and decision, plus the DoR outcome and story title for Story creates. Never the
rest of the payload.

Never crashes: hooks.json registers this with failClosed:true, so a crash would
block every MCP call. Any unexpected error answers "ask".
"""
import datetime
import importlib.util
import json
import os
import re
import sys

READ_VERBS = {
    "get", "search", "list", "fetch", "read", "query", "lookup", "find", "describe",
    "explore", "view", "show", "retrieve", "download", "count", "check", "chat",
    "summarize", "summarise", "info", "whoami", "preview", "browse", "context",
}
WRITE_VERBS = {
    "create", "update", "edit", "delete", "remove", "transition", "comment", "publish",
    "post", "send", "reply", "replyall", "forward", "move", "add", "set", "assign",
    "upload", "attach", "archive", "close", "merge", "invite", "book", "schedule",
    "write", "put", "patch", "insert", "link", "unlink", "rename", "copy", "share",
    "submit", "approve", "reject", "resolve", "reopen", "label", "tag", "react", "pin",
    "accept", "decline", "cancel", "complete", "mark", "draft", "drafts", "new", "save",
    "import", "sync", "bulk", "execute", "run", "trigger", "restore", "clear", "respond",
}
# Mail-sending words. Denied unless the name is clearly about something that is
# not email (a chat post, a Confluence page, a calendar invite, a Jira issue).
MAIL_SEND_WORDS = {"send", "reply", "replyall", "forward", "draft", "drafts", "respond"}
NOT_MAIL_CONTEXT = {
    "slack", "teams", "chat", "channel", "confluence", "page", "pages", "jira", "issue",
    "issues", "miro", "board", "calendar", "event", "events", "invite", "meeting",
}

MAIL_DENY_USER = "BA Assistant doesn't send email. The text is in chat for you to copy."
MAIL_DENY_AGENT = (
    "BLOCKED by policy (external-write-gate): BA Assistant never sends, replies to, forwards "
    "or drafts email in Outlook or any mail tool. Put the email text in chat (or a local .md "
    "file) for the BA to copy and send themselves. Do not retry with a different mail tool."
)


def tokens(name):
    """createJiraIssue -> [create, jira, issue]; outlook__send_mail -> [outlook, send, mail]."""
    spaced = re.sub(r"([a-z0-9])([A-Z])", r"\1 \2", name or "")
    spaced = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", spaced)
    return [t for t in re.split(r"[^a-zA-Z0-9]+", spaced.lower()) if t]


def unwrap(payload):
    """(real tool name, real arguments dict). Unwraps Runlayer execute_tool."""
    name = ""
    for key in ("tool_name", "toolName", "tool", "mcp_tool_name", "mcpToolName"):
        v = payload.get(key)
        if isinstance(v, str) and v.strip():
            name = v.strip()
            break
    args = payload.get("tool_input")
    if isinstance(args, str):
        try:
            args = json.loads(args)
        except Exception:
            args = {}
    if not isinstance(args, dict):
        args = {}
    wrapped = name.lower().endswith("execute_tool")
    if wrapped:
        inner = args.get("tool_name") or args.get("toolName")
        inner_args = args.get("arguments")
        if isinstance(inner_args, str):
            try:
                inner_args = json.loads(inner_args)
            except Exception:
                inner_args = {}
        if isinstance(inner, str) and inner.strip():
            return inner.strip(), inner_args if isinstance(inner_args, dict) else {}, True
        return "", {}, True
    return name, args, False


def classify(name):
    """(decision, reason) for a real (unwrapped) tool name."""
    toks = tokens(name)
    if not toks:
        return "ask", "unrecognised MCP call"
    tokset = set(toks)
    if tokset & MAIL_SEND_WORDS and not tokset & NOT_MAIL_CONTEXT:
        return "deny", "email send/reply/forward/draft"
    for t in toks:                      # the first verb in the name decides
        if t in READ_VERBS:
            return "allow", "read"
        if t in WRITE_VERBS:
            return "ask", "external write"
    return "ask", "unrecognised MCP call"


def is_issue_create(name):
    return bool(re.search(r"create.{0,12}(jira)?.{0,12}issue|jira.{0,12}create", name, re.I))


def _walk(obj, parent=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield parent, k, v
            yield from _walk(v, k.lower())
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v, parent)


def story_fields(args):
    """(is_story, summary, description, key). A type that says "story" (Story,
    User Story) or a type given only by id (we can't tell) counts as a Story;
    Bug/Task/Spike/Enabler by name do not. No type at all: only a summary that
    says "story". project.key is never taken as the story's key."""
    itype, type_seen, summary, key, desc = "", False, "", "", None
    for parent, k, v in _walk(args):
        lk = k.lower()
        if lk in ("issuetype", "issuetypename", "issue_type"):
            type_seen = True
            if isinstance(v, dict):
                itype = str(v.get("name") or "").lower()
            elif isinstance(v, str):
                itype = v.lower()
        elif lk == "summary" and isinstance(v, str) and not summary:
            summary = v
        elif lk == "description" and desc is None:
            desc = v
        elif lk in ("issueidorkey", "issuekey", "key") and isinstance(v, str) and not key and parent != "project":
            key = v
    if itype:
        is_story = "story" in itype
    elif type_seen:
        is_story = True
    else:
        is_story = bool(re.search(r"\bstory\b", summary, re.I))
    return is_story, summary, desc, key


def load_dor_check():
    here = os.path.dirname(os.path.abspath(__file__))
    for path in (os.path.join(here, "..", "_workstream", "dor-check.py"),
                 os.path.join(os.path.expanduser("~"), ".cursor", "_workstream", "dor-check.py")):
        if os.path.isfile(path):
            spec = importlib.util.spec_from_file_location("ba_dor_check", path)
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            return mod
    return None


def dor_outcome(args):
    """(outcome dict or None, error text). Never raises."""
    try:
        mod = load_dor_check()
        if mod is None:
            return None, "dor-check.py is not installed"
        _, summary, desc, key = story_fields(args)
        home = mod.Path(os.path.expanduser("~")) / ".cursor"
        init_dir, _how = mod.locate_initiative(home, summary, key, os.environ.get("CURSOR_SESSION_CONTEXT_PATH", ""))
        return mod.check_story(init_dir, summary, mod.flatten(desc), key), ""
    except Exception as exc:
        return None, f"DoR check error: {exc}"


def audit(tool, decision, reason, extra=None):
    try:
        path = os.path.join(os.path.expanduser("~"), ".cursor", "_workstream", "audit-log.jsonl")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        row = {"ts": datetime.datetime.now().isoformat(timespec="seconds"),
               "hook": "external-write-gate", "tool": tool, "decision": decision, "reason": reason}
        if extra:
            row.update(extra)
        with open(path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass


def emit(permission, user="", agent=""):
    print(json.dumps({"permission": permission, "user_message": user, "agent_message": agent}))
    sys.exit(0)


def main():
    raw = sys.stdin.read()
    try:
        payload = json.loads(raw or "{}")
    except Exception:
        payload = None
    if not isinstance(payload, dict):
        audit("", "ask", "unreadable hook payload")
        emit("ask", "BA Assistant couldn't read this tool call. Approve only if you expected it.",
             "Hook payload unreadable; the BA must approve.")

    name, _args, wrapped = unwrap(payload)
    shown = name or ("Runlayer execute_tool (no tool name)" if wrapped else "unknown MCP tool")
    decision, reason = classify(name)

    user = agent = ""
    if decision == "deny":
        user, agent = MAIL_DENY_USER, MAIL_DENY_AGENT
    elif decision == "ask":
        user = f"BA Assistant wants to run {shown}. Check the draft shown in chat before approving."
        agent = ("This external write needs the BA's approval in Cursor's dialog. Show the final "
                 "payload in chat before calling it; if the BA declines, do not retry.")

    extra = None
    if decision != "deny" and is_issue_create(name) and story_fields(_args)[0]:
        outcome, err = dor_outcome(_args)
        decision = "ask"                       # a Story is a Jira write: the BA always decides
        if outcome is None:
            reason = "DoR check could not run"
            user = f"DoR check couldn't run ({err}). Check the story is ready before approving."
            agent = "The DoR check could not run; the BA must decide. If they approve, log it as a BA decision."
            extra = {"dor": "error"}
        elif outcome["result"] == "pass":
            reason = "DoR met"
            user = f"DoR met. BA Assistant wants to create the Story \"{outcome['story']}\" in Jira. Approve to create."
            extra = {"dor": "pass", "story": outcome["story"]}
        else:
            reason = "DoR not met"
            user = ("DoR not met: " + ", ".join(outcome["missing_labels"]) +
                    ". Approve to create anyway as a BA override.")
            agent = ("DoR not met for this Story (" + ", ".join(outcome["missing_labels"]) + "). The BA decides in "
                     "Cursor's dialog. If they approve, record the override as a decision row in the tracker "
                     "(who, date, story, missing criteria). If they decline, fix the gaps and re-run "
                     "_workstream/dor-check.py.")
            extra = {"dor": "fail", "story": outcome["story"], "missing": outcome["missing"]}

    audit(shown, decision, reason, extra)
    emit(decision, user, agent)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as exc:   # never crash: failClosed would block every MCP call
        try:
            print(f"[external-write-gate] {exc}", file=sys.stderr)
        except Exception:
            pass
        emit("ask", "BA Assistant's safety check hit an error. Approve only if you expected this call.",
             "external-write-gate error; the BA must approve.")
