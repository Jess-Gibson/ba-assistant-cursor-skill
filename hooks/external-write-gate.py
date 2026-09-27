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

Story creates in Jira also go through the DoR check; the stricter of the two
answers wins (deny > ask > allow) and both messages are shown.

Every decision is appended to ~/.cursor/_workstream/audit-log.jsonl (tool name
and decision only, never the payload).

Never crashes: hooks.json registers this with failClosed:true, so a crash would
block every MCP call. Any unexpected error answers "ask".
"""
import datetime
import json
import os
import re
import subprocess
import sys

RANK = {"allow": 0, "ask": 1, "deny": 2}

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


def is_story_create(name):
    return bool(re.search(r"create.{0,12}(jira)?.{0,12}issue|jira.{0,12}create", name, re.I))


def dor_decision(raw_stdin):
    """Run the Story DoR check (same folder) on the original payload."""
    script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "jira-dor-gate.py")
    if not os.path.isfile(script):
        return None
    try:
        proc = subprocess.run([sys.executable, script], input=raw_stdin, capture_output=True,
                              text=True, timeout=6)
        return json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception:
        return {"permission": "ask",
                "user_message": "The DoR check could not run. Check the story is ready before approving.",
                "agent_message": "DoR check failed to run; the BA must decide."}


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

    if decision != "deny" and is_story_create(name):
        dor = dor_decision(raw)
        if dor and dor.get("permission") in RANK:
            if RANK[dor["permission"]] > RANK[decision]:
                decision = dor["permission"]
                reason = "DoR gate"
                user = dor.get("user_message") or user
                agent = dor.get("agent_message") or agent
            elif dor.get("user_message"):
                user = f"{user} {dor['user_message']}".strip()

    audit(shown, decision, reason)
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
