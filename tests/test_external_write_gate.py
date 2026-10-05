"""
Tests for hooks/external-write-gate.py (beforeMCPExecution, Runlayer only).

Every MCP call arrives as Runlayer `execute_tool` with the real tool name inside
tool_input. The gate must: allow reads, ask on external writes, deny any email
send / reply / forward / draft, and log each decision to _workstream/audit-log.jsonl.

Run:
    python3 tests/test_external_write_gate.py      (Windows: py tests/test_external_write_gate.py)
"""
import json
import os
import subprocess
import sys
import tempfile

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GATE = os.path.join(REPO, "hooks", "external-write-gate.py")
PY = sys.executable or "python3"
MAIL_MSG = "BA Assistant doesn't send email. The text is in chat for you to copy."

results = []


def check(name, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}")
    if not ok and detail:
        print(f"      {detail}")


def run_gate(stdin_text, home):
    env = dict(os.environ)
    env["HOME"] = home
    env["USERPROFILE"] = home
    env.pop("CURSOR_SESSION_CONTEXT_PATH", None)
    env.pop("BA_INITIATIVES_ROOT", None)
    proc = subprocess.run([PY, GATE], input=stdin_text, capture_output=True, text=True, env=env, timeout=30)
    return proc.returncode, json.loads(proc.stdout.strip().splitlines()[-1])


def runlayer(tool, arguments=None, outer="execute_tool"):
    return json.dumps({
        "hook_event_name": "beforeMCPExecution",
        "tool_name": outer,
        "tool_input": json.dumps({"tool_name": tool, "arguments": arguments or {}}),
    })


def main():
    with tempfile.TemporaryDirectory(prefix="ewg-") as home:
        os.makedirs(os.path.join(home, ".cursor", "initiatives"))

        # --- reads: allow, no prompt ---
        for tool in ("getJiraIssue", "searchJiraIssuesUsingJql", "atlassian__search", "getConfluencePage",
                     "searchConfluenceUsingCql", "getAccessibleAtlassianResources",
                     "outlook_calendar_list_calendar_view", "outlook_mail_search", "context_explore",
                     "getJiraIssueRemoteIssueLinks"):
            code, out = run_gate(runlayer(tool), home)
            check(f"read allowed: {tool}", code == 0 and out["permission"] == "allow", str(out))
        code, out = run_gate(json.dumps({"tool_name": "search_tools", "tool_input": "{\"query\": \"jira\"}"}), home)
        check("Runlayer search_tools (discovery) allowed", out["permission"] == "allow", str(out))

        # --- external writes: ask ---
        for tool in ("createConfluencePage", "updateConfluencePage", "editJiraIssue", "transitionJiraIssue",
                     "addCommentToJiraIssue", "outlook_calendar_create_event", "outlook_calendar_update_event",
                     "layout_create", "slack_send_message", "teams_post_message"):
            code, out = run_gate(runlayer(tool), home)
            check(f"write asks: {tool}", out["permission"] == "ask" and tool in out["user_message"], str(out))
        code, out = run_gate(runlayer("createJiraIssue", {"issueTypeName": "Bug", "summary": "Export crashes"}), home)
        check("Jira Bug create asks", out["permission"] == "ask", str(out))
        code, out = run_gate(runlayer("createJiraIssue", {"issueTypeName": "Story", "summary": "Add export button"}), home)
        check("Jira Story create is never allowed without the BA (DoR check runs)",
              out["permission"] in ("ask", "deny"), str(out))

        # --- email hidden behind a generic tool name: the arguments give it away ---
        for tool, args in (("execute", {"to": "priya@example.com", "subject": "Refunds", "body": "Hi"}),
                           ("sendNotification", {"toRecipients": [{"emailAddress": {"address": "a@b.co.nz"}}]}),
                           ("run_action", {"cc": ["x@y.com"], "text": "fyi"})):
            code, out = run_gate(runlayer(tool, args), home)
            check(f"email recipients in arguments deny: {tool}",
                  out["permission"] == "deny" and out["user_message"] == MAIL_MSG, str(out))
        for tool, args in (("outlook_calendar_create_event", {"attendees": [{"email": "a@b.com"}], "to": "a@b.com"}),
                           ("transitionJiraIssue", {"to": "Done"}),
                           ("execute", {"query": "status"})):
            code, out = run_gate(runlayer(tool, args), home)
            check(f"no email recipients, not denied: {tool}", out["permission"] == "ask", str(out))
        for tool in ("outlook_mail_search", "search_messages", "list_emails", "getMessages"):
            code, out = run_gate(runlayer(tool, {"to": "someone@example.com", "since": "2026-09-28"}), home)
            check(f"a read filtered by recipient is still a read (allowed): {tool}", out["permission"] == "allow", str(out))

        # --- email: always deny, with the copy-and-paste message ---
        for tool in ("send_mail", "outlook_send_email", "outlook__send_mail", "sendMail", "reply_to_message",
                     "replyAll", "forward_message", "outlook_mail_forward", "create_draft",
                     "outlook_mail_create_draft_message", "createDraftEmail", "send"):
            code, out = run_gate(runlayer(tool), home)
            check(f"mail denied: {tool}", out["permission"] == "deny" and out["user_message"] == MAIL_MSG, str(out))
        for outer in ("user-runlayer-plugin-execute_tool", "mcp_user-runlayer-plugin_execute_tool"):
            code, out = run_gate(runlayer("send_mail", outer=outer), home)
            check(f"mail denied through server-prefixed wrapper {outer}", out["permission"] == "deny", str(out))
        code, out = run_gate(json.dumps({"tool_name": "execute_tool", "tool_input": {
            "tool_name": "reply_to_message", "arguments": "{\"body\": \"Sure\"}"}}), home)
        check("mail denied when tool_input is an object and arguments a string", out["permission"] == "deny", str(out))
        code, out = run_gate(json.dumps({"tool_name": "send_mail", "tool_input": "{}"}), home)
        check("mail denied even if not wrapped by Runlayer", out["permission"] == "deny", str(out))
        code, out = run_gate(runlayer("send_invite_for_calendar_event"), home)
        check("calendar invite is a write (ask), not a mail deny", out["permission"] == "ask", str(out))

        # --- a write anywhere in the name wins over a read verb, whatever the word order ---
        mixed = ("findAndReplaceConfluencePage", "previewAndPublishPage", "list_and_archive",
                 "searchThenDeleteIssue", "getAndUpdatePage", "readAndCommentJiraIssue",
                 "fetchAndTransitionIssue", "getAndDeleteIssue", "search_and_replace", "view_update",
                 "check_and_close", "read_and_mark", "fetchThenPost", "lookupAndUpsertRecord")
        for tool in mixed:
            code, out = run_gate(runlayer(tool), home)
            check(f"mixed read/write asks: {tool}", out["permission"] == "ask" and tool in out["user_message"], str(out))

        # --- composing email is denied like sending it; composing anything else is not email ---
        for tool in ("composeEmail", "generateEmail", "createEmailDraft", "prepareAndSendMail",
                     "previewAndSendEmail", "outlook_compose_message", "newMail", "write_email_reply"):
            code, out = run_gate(runlayer(tool), home)
            check(f"mail compose denied: {tool}", out["permission"] == "deny" and out["user_message"] == MAIL_MSG, str(out))
        for tool in ("generateReport", "composeConfluencePage", "outlook_calendar_create_event", "frobnicateWidgetAndThings"):
            code, out = run_gate(runlayer(tool), home)
            check(f"not email, asks: {tool}", out["permission"] == "ask", str(out))
        for tool in ("outlook_mail_search", "getJiraIssue", "glean_chat"):
            code, out = run_gate(runlayer(tool), home)
            check(f"pure read still allowed: {tool}", out["permission"] == "allow", str(out))

        # --- unknown / malformed: ask, never crash ---
        code, out = run_gate(runlayer("frobnicate_widget"), home)
        check("unrecognised tool asks", out["permission"] == "ask", str(out))
        code, out = run_gate(json.dumps({"tool_name": "execute_tool", "tool_input": "{}"}), home)
        check("execute_tool with no inner tool name asks", out["permission"] == "ask", str(out))
        for bad in ("not json", "[1, 2]", ""):
            code, out = run_gate(bad, home)
            check(f"malformed payload {bad!r} asks, exit 0", code == 0 and out["permission"] == "ask", str(out))

        # --- F21: mail name / recipients deny first; mcp_server_name only for bare names ---
        code, out = run_gate(json.dumps({
            "tool_name": "send_email", "mcp_server_name": "slack", "tool_input": {},
        }), home)
        check("[F21] send_email + slack still denies (server never relaxes mail)",
              out["permission"] == "deny", str(out))
        code, out = run_gate(json.dumps({
            "tool_name": "send_email", "mcp_server_name": "teams", "tool_input": {},
        }), home)
        check("[F21] send_email + teams still denies", out["permission"] == "deny", str(out))
        code, out = run_gate(json.dumps({
            "tool_name": "sendNotification", "mcp_server_name": "ms365-teams",
            "tool_input": {"to": "a@example.com"},
        }), home)
        check("[F21] recipients on ms365-teams deny", out["permission"] == "deny", str(out))
        code, out = run_gate(json.dumps({
            "tool_name": "send_message", "mcp_server_name": "slack", "tool_input": "{}",
        }), home)
        check("[F21] slack send_message asks (not mail deny)", out["permission"] == "ask", str(out))
        code, out = run_gate(json.dumps({
            "tool_name": "send_message", "mcp_server_name": "outlook", "tool_input": "{}",
        }), home)
        check("[F21] outlook send_message denies as mail",
              out["permission"] == "deny" and out["user_message"] == MAIL_MSG, str(out))
        code, out = run_gate(json.dumps({"tool_name": "send_mail", "tool_input": "{}"}), home)
        check("[F21] send_mail denies", out["permission"] == "deny", str(out))
        code, out = run_gate(runlayer("send_mail"), home)
        check("[F21] Runlayer-wrapped execute_tool with inner send_mail is still denied",
              out["permission"] == "deny", str(out))

        # --- audit log: one line per call, tool + decision, never payload text ---
        log = os.path.join(home, ".cursor", "_workstream", "audit-log.jsonl")
        rows = [json.loads(l) for l in open(log, encoding="utf-8")] if os.path.exists(log) else []
        check("audit log written for every call", len(rows) >= 40, f"{len(rows)} rows")
        check("audit rows carry tool and decision",
              all({"ts", "tool", "decision"} <= set(r) for r in rows), str(rows[:2]))
        by_tool = {r["tool"]: r for r in rows}
        check("audit records a mixed read/write name as an external write, not a read",
              by_tool.get("findAndReplaceConfluencePage", {}).get("decision") == "ask"
              and by_tool.get("findAndReplaceConfluencePage", {}).get("reason") == "external write",
              str(by_tool.get("findAndReplaceConfluencePage")))
        check("audit records mail compose as a deny",
              by_tool.get("composeEmail", {}).get("decision") == "deny", str(by_tool.get("composeEmail")))
        check("audit log never stores payload text",
              not any("Export crashes" in json.dumps(r) or "Sure" in json.dumps(r) for r in rows))

    passed = sum(results)
    print(f"\n{passed}/{len(results)} external-write-gate checks passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
