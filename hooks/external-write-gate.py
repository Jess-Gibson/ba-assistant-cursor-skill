"""beforeMCPExecution hook: the one gate every MCP call passes through.

Runlayer is the only MCP path, so every call arrives as Runlayer `execute_tool`
with the real tool name inside tool_input:
    execute_tool { "tool_name": "createJiraIssue", "arguments": {...} }
This hook unwraps that, then decides:

Precedence, checked in this order over every word in the tool name (word order
in the name never matters, so a write can't hide behind a read verb):

  1. deny   email send / reply / forward / draft, or composing email
            (compose / generate / create / prepare / write / new + email, mail,
            Outlook). Also denied: any call whose arguments carry email
            recipients (to / cc / bcc / *Recipients holding an address), so a
            generic tool name (execute, sendNotification) can't carry an email
            past the gate. BA Assistant never sends email or creates Outlook
            drafts; the text goes in chat (or a local .md file) for the BA to copy.
  2. ask    any write verb anywhere in the name: Jira, Confluence, calendar,
            Miro, Slack/Teams posts. Cursor shows an approval dialog; the BA's
            click is the decision. findAndReplacePage asks, it is not a read.
  3. allow  otherwise, a read verb (get / search / list / fetch / ...), so pure
            reads never prompt.
  4. ask    anything else (no verb we recognise): the hook is the safety net
            whatever auto-run setting the BA uses.

Story creates in Jira also run the Story Readiness Preflight
(_workstream/dor-check.py, recomputed from the initiative files every time; a
stored pass is never trusted). It checks five structural conditions only; the
Definition of Ready stays the BA's judgement. A Story is still a Jira write, so
the BA always gets the approval dialog: "Structural preflight passed ..." (with
what it does not check), otherwise "Structural preflight not passed ...: <missing>.
Approve to create anyway as a BA override."

Every decision is appended to ~/.cursor/_workstream/audit-log.jsonl: tool name
and decision, plus the preflight outcome and story title for Story creates. Never
the rest of the payload.

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
    "replace", "upsert", "modify", "overwrite", "append", "revert", "grant", "revoke",
    "enable", "disable", "deploy", "push", "notify", "reset", "purge", "destroy", "clone",
    "duplicate", "migrate", "subscribe", "unsubscribe",
}
# Mail-sending words. Denied unless the name is clearly about something that is
# not email (a chat post, a Confluence page, a calendar invite, a Jira issue).
MAIL_SEND_WORDS = {"send", "reply", "replyall", "forward", "draft", "drafts", "respond"}
# Composing words only count as email when the name also says email, mail or
# Outlook (generateReport and composeConfluencePage are not email).
MAIL_COMPOSE_WORDS = {"compose", "generate", "create", "prepare", "write", "new"}
MAIL_WORDS = {"email", "emails", "mail", "mails", "outlook", "inbox", "mailbox"}
NOT_MAIL_CONTEXT = {
    "slack", "teams", "chat", "channel", "confluence", "page", "pages", "jira", "issue",
    "issues", "miro", "board", "calendar", "event", "events", "invite", "meeting",
}

# What a structural pass does and does not show. Shown in every pass dialog.
PREFLIGHT_SCOPE = ("It confirms a linked requirement, Given/When/Then acceptance criteria, dependencies, "
                   "MoSCoW and risks are present. It does not confirm semantic completeness, required "
                   "sign-offs, feasibility, sizing or NFR coverage.")

# Argument keys that mean "email recipients" when they hold an address.
RECIPIENT_KEYS = {"to", "cc", "bcc", "torecipients", "ccrecipients", "bccrecipients", "recipients"}
EMAIL_ADDRESS = re.compile(r"[\w.+-]+@[\w-]+(\.[\w-]+)+")

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
    if not tokset & NOT_MAIL_CONTEXT:
        if tokset & MAIL_SEND_WORDS:
            return "deny", "email send/reply/forward/draft"
        if tokset & MAIL_COMPOSE_WORDS and tokset & MAIL_WORDS:
            return "deny", "email compose"
    if tokset & WRITE_VERBS:            # a write anywhere in the name wins over any read verb
        return "ask", "external write"
    if tokset & READ_VERBS:
        return "allow", "read"
    return "ask", "unrecognised MCP call"


def has_mail_recipients(args):
    """True when the arguments address an email: a to/cc/bcc/*Recipients key
    whose value (string, list or nested dict) contains an email address."""
    for _parent, k, v in _walk(args):
        if re.sub(r"[^a-z]", "", str(k).lower()) in RECIPIENT_KEYS and EMAIL_ADDRESS.search(json.dumps(v, default=str)):
            return True
    return False


def classify_call(name, args):
    """classify() plus the payload check: a write or unknown call whose arguments
    carry email recipients is denied, unless the name is clearly about a non-email
    tool (calendar, Jira, chat). Reads are never denied here: a mail search
    filtered by recipient ("to": "someone@...") is a read, not a send."""
    decision, reason = classify(name)
    if decision == "ask" and not set(tokens(name)) & NOT_MAIL_CONTEXT and has_mail_recipients(args):
        return "deny", "email recipients in arguments"
    return decision, reason


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
    decision, reason = classify_call(name, _args)

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
            reason = "structural preflight could not run"
            user = (f"Story Readiness Preflight couldn't run ({err}). Check the story is ready "
                    "before approving.")
            agent = "The Story Readiness Preflight could not run; the BA must decide. If they approve, log it as a BA decision."
            extra = {"dor": "error"}
        elif outcome["result"] == "pass":
            reason = "structural preflight passed"
            user = (f"Structural preflight passed for \"{outcome['story']}\". " + PREFLIGHT_SCOPE +
                    " Approve to create in Jira.")
            agent = ("Show the final payload in chat before calling it; if the BA declines, do not retry. "
                     "Structural preflight passed; this is not a full Definition of Ready. Do not tell the "
                     "BA the story is ready or that sign-offs, AC coverage, NFRs, feasibility or sizing "
                     "were checked unless this conversation shows they were.")
            extra = {"dor": "pass", "story": outcome["story"]}
        else:
            reason = "structural preflight not passed"
            user = (f"Structural preflight not passed for \"{outcome['story']}\": " +
                    ", ".join(outcome["missing_labels"]) +
                    ". Approve to create anyway as a BA override.")
            agent = ("Structural preflight not passed for this Story (" + ", ".join(outcome["missing_labels"]) +
                     "). The BA decides in Cursor's dialog. If they approve, record the override as a "
                     "decision row in the tracker (who, date, story, missing conditions). If they decline, "
                     "fix the gaps and re-run _workstream/dor-check.py.")
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
