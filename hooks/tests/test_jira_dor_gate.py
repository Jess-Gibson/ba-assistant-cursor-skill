"""
Fixture tests for hooks/jira-dor-gate.py.

Standalone (no pytest dependency) so it can be run with either `py` or `python3`
directly, matching how the hook itself gets invoked. Each test case spins up an
isolated temp "initiative" directory with its own status-data.json, points the
gate at it via CURSOR_SESSION_CONTEXT_PATH, feeds a beforeMCPExecution-shaped
payload on stdin, and checks the returned permission.

Run:
    py hooks/tests/test_jira_dor_gate.py
    python3 hooks/tests/test_jira_dor_gate.py

Exits 0 if every case matches its expected permission, 1 otherwise.
"""
import json
import os
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GATE = os.path.join(REPO_ROOT, "hooks", "jira-dor-gate.py")
PY = sys.executable or "python3"


def make_initiative(tmpdir, name, status_data_text):
    """Create an isolated initiative dir with a status-data.json (raw text, so we can
    also test malformed/invalid JSON) and a dummy context marker file."""
    d = os.path.join(tmpdir, name)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "status-data.json"), "w", encoding="utf-8") as f:
        f.write(status_data_text)
    ctx = os.path.join(d, "SESSION-CONTEXT.md")
    with open(ctx, "w", encoding="utf-8") as f:
        f.write("# dummy session context marker\n")
    return ctx


def run_gate(payload, ctx_path):
    env = dict(os.environ)
    env["CURSOR_SESSION_CONTEXT_PATH"] = ctx_path
    env.pop("BA_INITIATIVES_ROOT", None)
    proc = subprocess.run(
        [PY, GATE],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        env=env,
        timeout=15,
    )
    if not proc.stdout.strip():
        raise AssertionError(f"gate produced no stdout. stderr:\n{proc.stderr}")
    try:
        result = json.loads(proc.stdout.strip().splitlines()[-1])
    except Exception as e:
        raise AssertionError(f"gate stdout wasn't valid JSON: {proc.stdout!r} ({e})\nstderr:\n{proc.stderr}")
    return result, proc.stderr


def create_payload(summary, issuetype="Story", tool_name="createJiraIssue", extra_fields=None, issue_key=None):
    fields = {"summary": summary, "issuetype": {"name": issuetype}}
    if extra_fields:
        fields.update(extra_fields)
    tool_input = {"fields": fields}
    if issue_key:
        tool_input["issueIdOrKey"] = issue_key
    return {
        "hook_event_name": "beforeMCPExecution",
        "tool_name": tool_name,
        "tool_input": json.dumps(tool_input),
    }


results = []


def case(name, expected, payload, ctx_path):
    result, stderr = run_gate(payload, ctx_path)
    got = result.get("permission")
    ok = got == expected
    results.append((name, expected, got, ok))
    if not ok:
        print(f"    payload: {json.dumps(payload)}")
        print(f"    stderr:  {stderr.strip()}")
        print(f"    full result: {result}")


def main():
    with tempfile.TemporaryDirectory(prefix="jira-dor-gate-tests-") as tmp:

        # --- Case 1: empty-title passing dorChecks row exists (Hole A); the story being
        # created has NO evidence of its own -> must DENY.
        ctx = make_initiative(tmp, "case1", json.dumps({
            "dorChecks": [
                {"storyTitle": "", "storyKey": "", "firstAttempt": "pass"}
            ]
        }))
        case(
            "1. empty-title wildcard row exists, target story has no evidence -> DENY",
            "deny",
            create_payload("Brand new story with zero DoR evidence anywhere"),
            ctx,
        )

        # --- Case 2: Story X passed DoR; story Y's title is only mentioned elsewhere in
        # the tracker prose (not its own approved row) -> creating Y must DENY.
        # (This is the old whole-tracker-file regex hole -- initiative-tracker.md is no
        # longer consulted at all, but we still prove Y doesn't inherit X's pass via
        # status-data.json either.)
        tracker_md = (
            "### Story X: Automate invoice retry logic\n"
            "DoR: PASS\n\n"
            "Notes: see also Story Y: Improve dashboard filters for power users, for related context.\n"
        )
        ctx2_dir = os.path.join(tmp, "case2")
        os.makedirs(ctx2_dir, exist_ok=True)
        with open(os.path.join(ctx2_dir, "status-data.json"), "w", encoding="utf-8") as f:
            json.dump({
                "dorChecks": [
                    {"storyTitle": "Automate invoice retry logic", "firstAttempt": "pass"}
                ]
            }, f)
        with open(os.path.join(ctx2_dir, "initiative-tracker.md"), "w", encoding="utf-8") as f:
            f.write(tracker_md)
        ctx2 = os.path.join(ctx2_dir, "SESSION-CONTEXT.md")
        with open(ctx2, "w", encoding="utf-8") as f:
            f.write("# dummy\n")
        case(
            "2. story X passed, Y only mentioned in tracker prose, create Y -> DENY",
            "deny",
            create_payload("Improve dashboard filters for power users"),
            ctx2,
        )

        # --- Case 3: create payload self-stamps "DoR: PASS" in its own description, but
        # Y's tracker row does not show a pass (Hole C) -> must DENY.
        ctx3 = make_initiative(tmp, "case3", json.dumps({
            "dorChecks": [
                {"storyTitle": "Improve dashboard filters for power users", "firstAttempt": "fail"}
            ]
        }))
        case(
            "3. payload self-stamps 'DoR: PASS', tracker row for Y shows no pass -> DENY",
            "deny",
            create_payload(
                "Improve dashboard filters for power users",
                extra_fields={"description": "DoR: PASS (override, see decision D-014)"},
            ),
            ctx3,
        )

        # --- Case 4: Y's own tracker row genuinely shows a pass tied to Y's own id/title
        # -> must ALLOW.
        ctx4 = make_initiative(tmp, "case4", json.dumps({
            "dorChecks": [
                {"storyKey": "PROJ-501", "storyTitle": "Improve dashboard filters for power users", "firstAttempt": "pass"}
            ]
        }))
        case(
            "4. Y's own row genuinely passed -> ALLOW",
            "allow",
            create_payload("Improve dashboard filters for power users"),
            ctx4,
        )
        # Same case, but matched via issue key instead of title, and a punctuation/case
        # variant of the pass marker ("DOR - Pass") to prove normalisation works without
        # reopening Hole A/B.
        ctx4b = make_initiative(tmp, "case4b", json.dumps({
            "dorChecks": [
                {"storyKey": "PROJ-501", "storyTitle": "Improve dashboard filters for power users", "firstAttempt": "DOR - Pass"}
            ]
        }))
        case(
            "4b. key-based match + normalised pass marker -> ALLOW",
            "allow",
            create_payload("Improve dashboard filters for power users", issue_key="PROJ-501"),
            ctx4b,
        )

        # --- Case 5: creating a Spike / Bug / Enabler / Chore (not a Story) -> ALLOW,
        # gate doesn't apply, regardless of tracker state.
        ctx5 = make_initiative(tmp, "case5", json.dumps({"dorChecks": []}))
        for issuetype in ("Spike", "Bug", "Enabler", "Chore"):
            case(
                f"5. creating a {issuetype} (not a Story) -> ALLOW",
                "allow",
                create_payload(f"Some {issuetype} with no DoR evidence at all", issuetype=issuetype),
                ctx5,
            )

        # --- Case 7: a SHORT, generic new-story title happens to appear as a substring
        # inside a much longer, already-passed, UNRELATED row's title. Must DENY -- a short
        # common phrase matching somewhere inside a long unrelated title is not the same
        # story, and open substring containment (no length-ratio check) would wrongly
        # allow this. This is a narrower cousin of Hole B that the original A/B/C fixture
        # cases above don't exercise.
        ctx7 = make_initiative(tmp, "case7", json.dumps({
            "dorChecks": [
                {"storyTitle": "Implement OAuth2 SSO integration for merchant portal onboarding flow", "firstAttempt": "pass"}
            ]
        }))
        case(
            "7. short generic title substring-collides with unrelated long passed row -> DENY",
            "deny",
            create_payload("SSO integration"),
            ctx7,
        )

        # --- Case 6: malformed/unparseable status-data.json.
        # 6a: Story create in that initiative -> DENY (fail closed for Story-create only).
        ctx6 = make_initiative(tmp, "case6", "{not valid json,,, at all")
        case(
            "6a. malformed status-data.json, Story create -> DENY",
            "deny",
            create_payload("Any story at all"),
            ctx6,
        )
        # 6b: a non-Story MCP call in the SAME broken-tracker state -> ALLOW (fail open).
        case(
            "6b. malformed status-data.json, non-Story create -> ALLOW",
            "allow",
            create_payload("Any spike at all", issuetype="Spike"),
            ctx6,
        )
        # 6c: a totally unrelated (non-Jira, non-create) MCP call in the same broken-tracker
        # state -> ALLOW (fail open; gate shouldn't even engage).
        case(
            "6c. malformed status-data.json, unrelated MCP tool -> ALLOW",
            "allow",
            {"hook_event_name": "beforeMCPExecution", "tool_name": "layout_read", "tool_input": json.dumps({"miro_url": "x"})},
            ctx6,
        )

    # --- Report ---
    print()
    print(f"{'Case':<70} {'Expect':<7} {'Got':<7} {'Result'}")
    print("-" * 100)
    all_ok = True
    for name, expected, got, ok in results:
        print(f"{name:<70} {expected:<7} {str(got):<7} {'PASS' if ok else 'FAIL'}")
        all_ok = all_ok and ok
    print("-" * 100)
    total = len(results)
    passed = sum(1 for *_, ok in results if ok)
    print(f"{passed}/{total} cases passed")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
