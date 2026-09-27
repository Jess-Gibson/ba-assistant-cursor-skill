"""
Tests for the scripts that took mechanical work off the model in Version 15:
ba-actions.py, capture.py, validate-state.py, compute-metrics.py,
render-initiative-canvas.py, and the per-initiative snapshot freshness.

Standalone, no pytest. Every case runs in a throwaway folder with its own
~/.cursor layout; nothing under the real home is read or written.

Run:
    python3 tests/test_efficiency_scripts.py      (Windows: py tests/test_efficiency_scripts.py)
"""
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable or "python3"
FIXTURE = REPO / "tests" / "fixtures" / "sample-status-data.json"
FAILURES = []
ENV = {k: v for k, v in os.environ.items() if k != "BA_INITIATIVES_ROOT"}


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {detail}" if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def run(script, *args, stdin=None):
    p = subprocess.run([PY, str(script), *[str(a) for a in args]], capture_output=True, text=True, encoding="utf-8",
                       input=stdin, timeout=60, env=ENV)
    return p.returncode, p.stdout + p.stderr


def make_home(tmp: Path, name: str) -> Path:
    """A fake ~/.cursor with the package's _workstream scripts copied in, like an install."""
    home = tmp / name / ".cursor"
    ws = home / "_workstream"
    ws.mkdir(parents=True)
    for script in ("ba-actions.py", "regenerate-ba-actions-md.py", "capture.py", "validate-state.py",
                   "compute-metrics.py", "generate-initiative-snapshots.py"):
        shutil.copy(REPO / "_workstream" / script, ws / script)
    shutil.copy(REPO / "tools" / "render-initiative-canvas.py", ws / "render-initiative-canvas.py")
    (home / "rules").mkdir()
    (home / "rules" / "ba-assistant-config.mdc").write_text(
        f"paths:\n  initiativesRoot: {home / 'initiatives'}\n", encoding="utf-8")
    return home


def actions_tests(tmp):
    home = make_home(tmp, "actions")
    script = home / "_workstream" / "ba-actions.py"
    store = home / "_workstream" / "ba-actions.json"
    T = ("--today", "2026-09-28")

    code, out = run(script, *T, "add", "--task", "Chase data export", "--initiative", "payments", "--due", "2026-09-29")
    data = json.loads(store.read_text(encoding="utf-8"))
    check("Actions: add creates BA-001 with the gate lines",
          code == 0 and data["actions"][0]["id"] == "BA-001" and "Gate: ba-actions-sync: PASS" in out
          and "Gate: ba-actions-md-regen: PASS" in out, out)
    check("Actions: due within 2 working days defaults to high priority", data["actions"][0]["priority"] == "high")
    check("Actions: ba-actions.md regenerated", (home / "_workstream" / "ba-actions.md").exists())

    code, out = run(script, *T, "add", "--task", "Chase the data export!", "--initiative", "payments", "--notes", "ping Sam")
    data = json.loads(store.read_text(encoding="utf-8"))
    check("Actions: near-duplicate wording updates the same row, no new id",
          len(data["actions"]) == 1 and data["actions"][0]["notes"] == "ping Sam" and "Updated" in out, out)

    code, out = run(script, *T, "add", "--task", "Chase data export from vendor", "--initiative", "payments")
    data = json.loads(store.read_text(encoding="utf-8"))
    check("Actions: a genuinely different task gets a new id", len(data["actions"]) == 2 and data["actions"][1]["id"] == "BA-002")

    code, out = run(script, *T, "done", "BA-002")
    code, out = run(script, *T, "set", "BA-002", "--status", "open")
    data = json.loads(store.read_text(encoding="utf-8"))
    check("Actions: a done row is never reopened without --reopen",
          code == 1 and data["actions"][1]["status"] == "done" and "FAIL" in out, out)
    code, out = run(script, *T, "add", "--task", "Chase data export from vendor", "--initiative", "payments", "--status", "open")
    data = json.loads(store.read_text(encoding="utf-8"))
    check("Actions: an upsert that matches a done row keeps it done", data["actions"][1]["status"] == "done", out)

    rows = json.dumps([{"task": "Draft AC for refunds", "initiative": "payments", "due": "2026-09-25",
                        "source": {"type": "debrief", "label": "Refund workshop 28 Sep"}},
                       {"task": "Book playback", "initiative": "payments", "remind_on": "2026-09-28", "reminder": "Find a slot"}])
    code, out = run(script, *T, "upsert", "--json", "-", stdin=rows)
    check("Actions: upsert adds a batch in one call", code == 0 and "2 added" in out, out)

    code, out = run(script, *T, "eod-scan", "--closeout-date", "2026-09-28", "--json")
    scan = json.loads(out)
    walk = [a["id"] for a in scan["walk"]]
    check("Actions: eod-scan buckets overdue and remind-today",
          scan["critical"]["Overdue"] == ["BA-003"] and scan["critical"]["Remind today"] == ["BA-004"], out[:400])
    check("Actions: eod-scan walk is ordered overdue first and skips closed rows",
          walk[0] == "BA-003" and "BA-002" not in walk, str(walk))

    code, out = run(script, *T, "set", "BA-404", "--status", "done")
    check("Actions: unknown id fails clearly", code == 1 and "no action BA-404" in out, out)


def capture_tests(tmp):
    home = make_home(tmp, "capture")
    init = home / "initiatives" / "payments"
    init.mkdir(parents=True)
    ctx = init / "SESSION-CONTEXT.md"
    ctx.write_text("# Payments\n\n## Mid-session captures - 2026-09-28\n\n### Decisions\n"
                   "- 09:00 Use vendor X for ID checks - source: chat\n\n## Closeout 27 Sep\nold notes\n", encoding="utf-8")
    script = home / "_workstream" / "capture.py"
    items = json.dumps([
        {"type": "decision", "text": "Going with option B for the refunds API", "context": "Cheaper"},
        {"type": "decision", "text": "Use vendor X for ID checks"},
        {"type": "requirement", "text": "Refunds over $500 need a second approver"},
        {"type": "answered", "text": "Does the batch job support partial refunds?", "resolution": "Yes (infra)"},
        {"type": "action", "text": "Send refund AC draft to Priya", "due": "2026-09-30", "mine": True},
    ])
    code, out = run(script, "--cursor-home", home, "--initiative", "payments", "--source", "chat-user",
                    "--json", "-", "--now", "2026-09-28T14:05", stdin=items)
    text = ctx.read_text(encoding="utf-8")
    check("Capture: writes new items and skips the one already there",
          code == 0 and "4 written, 1 already there" in out and text.count("Use vendor X") == 1, out)
    check("Capture: items land under today's heading, before the next section",
          text.index("REQ-new: 14:05 Refunds over $500") < text.index("## Closeout 27 Sep")
          and text.index("DEC-new: 14:05 Going with option B") < text.index("### Requirements"), text)
    check("Capture: answered questions carry the resolution", "OQ-answered: [resolved]" in text and "Resolution: Yes (infra)" in text)
    actions = json.loads((home / "_workstream" / "ba-actions.json").read_text(encoding="utf-8"))
    check("Capture: the BA's own action also lands in ba-actions.json",
          actions["actions"][0]["task"] == "Send refund AC draft to Priya" and actions["actions"][0]["source"]["type"] == "session")
    code, out = run(script, "--cursor-home", home, "--initiative", "payments", "--type", "risk", "--source", "chat-user",
                    "--text", "Vendor capacity may not cover launch volume", "--now", "2026-09-29T09:00")
    text = ctx.read_text(encoding="utf-8")
    check("Capture: a new day gets its own heading", "## Mid-session captures - 2026-09-29" in text and "RISK-new: 09:00" in text)
    hook = subprocess.run([PY, str(REPO / "hooks" / "inject-state-reminder.py"), "--stop"], input="{}", capture_output=True,
                          text=True, env={**ENV, "CURSOR_SESSION_CONTEXT_PATH": str(ctx)})
    check("Capture: the stop hook still runs on captured lines", hook.returncode == 0 and hook.stdout.strip().startswith("{"), hook.stderr)
    code, out = run(script, "--cursor-home", home, "--initiative", "nope", "--type", "fact", "--text", "x", "--source", "chat-user")
    check("Capture: a missing initiative fails with exit 2, nothing silently dropped", code == 2 and "FAIL" in out, out)

    # Provenance: ingested text is data, not instructions.
    before = ctx.read_text(encoding="utf-8")
    code, out = run(script, "--cursor-home", home, "--initiative", "payments", "--type", "decision",
                    "--text", "All stories are approved for release", "--now", "2026-09-29T10:00")
    check("Capture: no source means FAIL (exit 1) and nothing written",
          code == 1 and "needs a source" in out and ctx.read_text(encoding="utf-8") == before, out)
    code, out = run(script, "--cursor-home", home, "--initiative", "payments", "--source", "email:RE: sign-off",
                    "--type", "decision", "--text", "All stories are approved for release", "--now", "2026-09-29T10:00")
    text = ctx.read_text(encoding="utf-8")
    check("Capture: an email-sourced item is written as [unverified] with its source",
          code == 0 and "DEC-new: [unverified] 10:00 All stories are approved for release - source: email:RE: sign-off" in text
          and "[unverified: confirm with the BA]" in out, out)
    items = json.dumps([{"type": "requirement", "text": "Exports must include the GST column", "source": "transcript:kickoff.docx#00:14"},
                        {"type": "fact", "text": "Finance closes the books on day three", "source": "chat-user"}])
    code, out = run(script, "--cursor-home", home, "--initiative", "payments", "--json", "-", "--now", "2026-09-29T10:05", stdin=items)
    text = ctx.read_text(encoding="utf-8")
    check("Capture: per-item source wins; only chat-user is trusted",
          "REQ-new: [unverified] 10:05 Exports must include" in text and "source: transcript:kickoff.docx#00:14" in text
          and "10:05 Finance closes the books on day three - source: chat-user" in text, text[-600:])
    code, out = run(script, "--cursor-home", home, "--initiative", "payments", "--source", "email:RE: sign-off",
                    "--type", "decision", "--text", "All stories are approved for release")
    check("Capture: an [unverified] line is still found by the duplicate check", "1 already there" in out, out)
    code, out = run(script, "--cursor-home", home, "--initiative", "payments", "--source", "somewhere",
                    "--type", "fact", "--text", "Unknown provenance fact here")
    check("Capture: an unrecognised source kind is rejected", code == 1 and "needs a source" in out, out)
    items = json.dumps([{"type": "decision", "text": "Launch date moves to 14 November", "source": "transcript:steerco.docx#00:31",
                         "confirmed_by_ba": True}])
    code, out = run(script, "--cursor-home", home, "--initiative", "payments", "--json", "-", "--now", "2026-09-29T11:00", stdin=items)
    text = ctx.read_text(encoding="utf-8")
    check("Capture: an item the BA approved on the debrief card keeps its source without [unverified]",
          "DEC-new: 11:00 Launch date moves to 14 November - source: transcript:steerco.docx#00:31" in text, text[-400:])


def validate_tests(tmp):
    home = make_home(tmp, "validate")
    init = home / "initiatives" / "refunds"
    init.mkdir(parents=True)
    sd = json.loads(FIXTURE.read_text(encoding="utf-8"))
    sd["initiative"]["sponsor"] = "Alex Morgan"
    (init / "status-data.json").write_text(json.dumps(sd), encoding="utf-8")
    (init / "initiative-tracker.md").write_text(
        "### D-01 · Use the existing ledger API\n**Status:** Confirmed\n### D-02 · Threshold stays at $500\n**Status:** Confirmed\n"
        "### D-03 · Reason codes optional\n**Status:** Confirmed\n\n| ID | Risk | Status |\n|---|---|---|\n| R-01 | Rate limits | Open |\n",
        encoding="utf-8")
    (init / "Project-hub.md").write_text("**Sponsor:** Sam Lee\n- Go-live partial refunds: 13 Nov 2026\n", encoding="utf-8")
    (init / "README.md").write_text("**Status:** Active\n", encoding="utf-8")
    (home / "_workstream" / "workboard.json").write_text(json.dumps({"initiatives": [{"slug": "refunds", "status": "closed"}]}),
                                                         encoding="utf-8")
    script = home / "_workstream" / "validate-state.py"
    code, out = run(script, "--cursor-home", home, "--initiative", "refunds", "--json")
    rows = json.loads(out)["divergences"]
    facts = " | ".join(r["fact"] for r in rows)
    check("Validate: tracker item missing from status-data.json", any("D-03" in r["found"] for r in rows), facts)
    check("Validate: status mismatch between tracker and status-data.json", "D-02 status" in facts, facts)
    check("Validate: sponsor name drift in Project-hub.md", "Sponsor name" in facts, facts)
    check("Validate: milestone date drift in Project-hub.md", "Go-live partial refunds date" in facts, facts)
    check("Validate: README status vs workboard.json", "Initiative status" in facts, facts)
    code, out = run(script, "--cursor-home", home, "--initiative", "refunds")
    check("Validate: table output ends with a DRIFT gate", code == 0 and "Gate: state-validation: DRIFT (5)" in out, out[-400:])

    clean = init.parent / "clean"
    clean.mkdir()
    (clean / "status-data.json").write_text(json.dumps({"initiative": {"name": "Clean"}}), encoding="utf-8")
    code, out = run(script, "--cursor-home", home, "--initiative", "clean")
    check("Validate: a clean initiative is ALIGNED", code == 0 and "ALIGNED" in out, out)
    code, out = run(script, "--cursor-home", home, "--initiative", "missing")
    check("Validate: missing folder exits 1", code == 1, out)


def metrics_tests(tmp):
    home = make_home(tmp, "metrics")
    init = home / "initiatives" / "refunds"
    init.mkdir(parents=True)
    sd = json.loads(FIXTURE.read_text(encoding="utf-8"))
    sd["requirements"][1]["moscowMatrix"] = []
    sd["requirements"][0]["interrogated"] = True
    sd["dorChecks"] = [{"storyTitle": "a", "checkedAt": "2026-10-01", "firstAttempt": "pass"},
                       {"storyTitle": "b", "checkedAt": "2026-10-02", "firstAttempt": "partial"}]
    (init / "status-data.json").write_text(json.dumps(sd), encoding="utf-8")
    script = home / "_workstream" / "compute-metrics.py"
    code, out = run(script, "--cursor-home", home, "--initiative", "refunds", "--today", "2026-10-05", "--json")
    m = json.loads(out)["metrics"]
    check("Metrics: MoSCoW coverage counts rated requirements", m["moscowCoverage"]["value"] == 0.5, str(m["moscowCoverage"]))
    check("Metrics: DoR hit rate uses firstAttempt", m["dorHitRate"]["value"] == 0.5, str(m["dorHitRate"]))
    check("Metrics: interrogation rate", m["interrogationRate"]["value"] == 0.5, str(m["interrogationRate"]))
    check("Metrics: no completed sign-offs is n/a, never 0", m["signOffCycleTime"]["medianWorkingDays"] is None
          and m["signOffCycleTime"]["openOver7WorkingDays"] == ["SO-01"], str(m["signOffCycleTime"]))
    check("Metrics: cache written next to status-data.json", (init / "metrics-cache.json").exists())
    sd.pop("dorChecks")
    (init / "status-data.json").write_text(json.dumps(sd), encoding="utf-8")
    for day in ("2026-10-06", "2026-10-07"):
        run(script, "--cursor-home", home, "--initiative", "refunds", "--today", day)
    code, out = run(script, "--cursor-home", home, "--initiative", "refunds", "--today", "2026-10-13")
    check("Metrics: n/a for 3+ runs is called out", "n/a for 3+ runs: dorHitRate" in out, out)
    check("Metrics: trend compares with a run 7+ days old", re.search(r"MoSCoW coverage \| 50% \| →", out) is not None, out)


def canvas_tests(tmp):
    home = make_home(tmp, "canvas")
    init = home / "initiatives" / "refunds"
    init.mkdir(parents=True)
    shutil.copy(FIXTURE, init / "status-data.json")
    (home / "projects" / "ws" / "canvases").mkdir(parents=True)
    script = home / "_workstream" / "render-initiative-canvas.py"
    # The installed layout has the template under skills/ba-assistant/templates.
    tpl = home / "skills" / "ba-assistant" / "templates"
    tpl.mkdir(parents=True)
    shutil.copy(REPO / "skills" / "ba-assistant" / "templates" / "initiative-status.canvas.tsx.template", tpl)
    code, out = run(script, "--cursor-home", home, "--initiative", "refunds", "--today", "2026-09-28")
    canvas = home / "projects" / "ws" / "canvases" / "refunds-status.canvas.tsx"
    html = init / "status-snapshot.html"
    check("Canvas: renders the canvas into the workspace canvases folder and the HTML next to the data",
          code == 0 and canvas.exists() and html.exists() and "Gate: canvas-render: PASS" in out, out)
    body = canvas.read_text(encoding="utf-8")
    check("Canvas: data placeholder replaced with JSON", "/* CANVAS_DATA */" not in body and '"Sample refunds uplift"' in body)
    for tab in ("overview", "workstreams", "features", "timeline", "dependencies", "traceability", "critical-path", "tracker"):
        check(f"Canvas: tab {tab} in the canvas and the HTML", f'"{tab}"' in body and f'id="tab-{tab}"' in html.read_text(encoding="utf-8"))
    page = html.read_text(encoding="utf-8")
    check("Canvas: DRAFT banner while PM approval is pending", "DRAFT - pending approval from [PM]" in page)
    check("Canvas: outstanding-only toggle defaults on", 'id="outstanding" checked' in page and 'body class="only-outstanding"' in page)
    check("Canvas: all 8 tabs have data for the fixture", "Tabs with data: 8 / 8" in out, out)
    check("Canvas: HTML escapes labels with < and >", "Partial refunds (&lt;$500)" in page)

    sd = json.loads(FIXTURE.read_text(encoding="utf-8"))
    sd["initiative"]["pmApproval"]["status"] = "approved"
    (init / "status-data.json").write_text(json.dumps(sd), encoding="utf-8")
    run(script, "--cursor-home", home, "--initiative", "refunds", "--today", "2026-09-28")
    check("Canvas: no DRAFT banner once approved", "DRAFT - pending approval" not in html.read_text(encoding="utf-8"))

    (init / "status-data.json").write_text(json.dumps({"initiative": {"name": "Brand new"}}), encoding="utf-8")
    code, out = run(script, "--cursor-home", home, "--initiative", "refunds", "--today", "2026-09-28")
    check("Canvas: a near-empty status-data.json still renders, and says what each tab needs",
          code == 0 and "Tabs with data: 0 / 8" in out and "Timeline: empty (needs" in out, out)
    code, out = run(script, "--cursor-home", home, "--initiative", "missing")
    check("Canvas: missing status-data.json fails clearly", code == 1 and "FAIL" in out, out)


def snapshot_slice_tests(tmp):
    home = make_home(tmp, "snap")
    ws = home / "_workstream"
    for slug in ("payments", "refunds"):
        (home / "initiatives" / slug).mkdir(parents=True)
        (home / "initiatives" / slug / "SESSION-CONTEXT.md").write_text(f"# {slug}\n", encoding="utf-8")
    (ws / "workboard.json").write_text(json.dumps({"initiatives": [{"slug": "payments", "name": "Payments uplift"},
                                                                    {"slug": "refunds", "name": "Refunds"}]}), encoding="utf-8")
    actions = {"actions": [{"id": "BA-001", "task": "Chase", "status": "open", "initiative": "payments"}]}
    (ws / "ba-actions.json").write_text(json.dumps(actions), encoding="utf-8")
    (ws / "calendar-feed.json").write_text(json.dumps({"meetings": [{"subject": "Payments standup"}]}), encoding="utf-8")
    script = ws / "generate-initiative-snapshots.py"
    run(script, "--cursor-home", home)
    actions["actions"].append({"id": "BA-002", "task": "Other work", "status": "open", "initiative": "refunds"})
    (ws / "ba-actions.json").write_text(json.dumps(actions), encoding="utf-8")
    (ws / "calendar-feed.json").write_text(json.dumps({"meetings": [{"subject": "Payments standup"}, {"subject": "Dentist"}]}),
                                           encoding="utf-8")
    code, out = run(script, "--cursor-home", home, "--check", "payments")
    check("Snapshot: another initiative's action and an unrelated meeting keep it FRESH", code == 0 and "FRESH" in out, out)
    code, out = run(script, "--cursor-home", home, "--check", "refunds")
    check("Snapshot: its own new action makes it STALE", code == 1 and "ba-actions.json" in out, out)
    code, out = run(script, "--cursor-home", home, "--ensure", "refunds")
    check("Snapshot: --ensure rebuilds a stale snapshot", code == 0 and "REFRESHED" in out, out)
    code, out = run(script, "--cursor-home", home, "--ensure", "refunds")
    check("Snapshot: --ensure then reports FRESH", code == 0 and "FRESH" in out, out)
    code, out = run(script, "--cursor-home", home, "--ensure", "nope")
    check("Snapshot: --ensure on an unknown initiative exits 1", code == 1, out)


def docs_tests():
    shipped = [p for root in ("skills", "rules", "commands") for p in (REPO / root).rglob("*") if p.suffix in {".md", ".mdc"}]
    text = {p: p.read_text(encoding="utf-8", errors="ignore") for p in shipped}
    hits = [str(p.relative_to(REPO)) for p, t in text.items()
            if re.search(r"(?i)read (every|all) (single )?(\.md )?(project )?files? (in the project folder|before generating)", t)
            or "ALWAYS read ALL project files" in t]
    check("Docs: nothing tells the agent to read every project file for a canvas", not hits, ", ".join(hits))
    status = (REPO / "commands" / "status.md").read_text(encoding="utf-8")
    check("Docs: /status does not render the canvas", "triple" not in status.lower() and "Do not render the canvas" in status)
    router = (REPO / "rules" / "execution-router.mdc").read_text(encoding="utf-8")
    check("Docs: always-on router points at the re-entry card reference instead of carrying it",
          "references/re-entry-card.md" in router and "### Card format" not in router
          and (REPO / "skills" / "ba-assistant" / "references" / "re-entry-card.md").exists())
    check("Docs: context capture still runs every BA turn and writes via capture.py",
          "After every user message" in router and "capture.py" in router)
    check("Docs: passive capture is paused while a transcript is debriefed (the debrief card decides)",
          "its items go on the debrief card" in router)
    inst = (REPO / "tools" / "install-ba-assistant.py").read_text(encoding="utf-8")
    missing = [s for s in ("ba-actions.py", "capture.py", "validate-state.py", "compute-metrics.py", "render-initiative-canvas.py")
               if f'"{s}"' not in inst]
    check("Install: every new script is in the installer's copy lists", not missing, ", ".join(missing))


ALWAYS_ON_BUDGET = 24000  # characters across every alwaysApply rule plus the config template (was about 33000 before Version 15)


def always_on_tests():
    rules = [p for p in (REPO / "rules").glob("*.mdc") if re.search(r"^alwaysApply:\s*true", p.read_text(encoding="utf-8"), re.M)]
    template = REPO / "skills" / "ba-assistant" / "ba-profile.template.mdc"
    sizes = {p.name: len(p.read_text(encoding="utf-8")) for p in rules + [template]}
    total = sum(sizes.values())
    print(f"INFO  always-on characters: {total} " + ", ".join(f"{k}={v}" for k, v in sorted(sizes.items())))
    check(f"Always-on: rules + config template stay under {ALWAYS_ON_BUDGET} characters", total <= ALWAYS_ON_BUDGET, str(sizes))
    text = {p.name: p.read_text(encoding="utf-8") for p in rules + [template]}
    check("Always-on: no wave / changelog history notes", not [n for n, t in text.items() if "(Wave:" in t])
    check("Always-on: no command table (commands live in ~/.cursor/commands/)",
          not [n for n, t in text.items() if re.search(r"^\| `/[\w-]+` \|", t, re.M)])
    profile = text["ba-profile.mdc"]
    check("Always-on: profile points at ~/.cursor/commands/ for typed commands", "~/.cursor/commands/<name>.md" in profile)
    check("Always-on: every command file exists for the commands the rules offer",
          all((REPO / "commands" / f"{c}.md").exists() for c in ("wrap", "canvas", "next", "reanchor")))
    behaviour = text["agent-behavior.mdc"]
    check("Always-on: AskQuestion rules live in agent-behavior.mdc (with the never-re-ask rule)",
          "## AskQuestion" in behaviour and "Never re-ask a decision" in behaviour
          and "## AskQuestion" not in text["execution-router.mdc"] and "## 4. AskQuestion" not in text["execution-router.mdc"])
    for name, needle in (("agent-behavior.mdc", "Lock block when the brief is thin"), ("agent-behavior.mdc", "Review-control gate"),
                         ("agent-behavior.mdc", "Default-deny"), ("agent-behavior.mdc", "No em dashes"),
                         ("ba-profile.mdc", "Strict sequencing"), ("ba-profile.mdc", "Decisions are always a table"),
                         ("ba-profile.mdc", "Priority types"), ("execution-router.mdc", "Publish guard"),
                         ("execution-router.mdc", "Anti-Pattern Detector"), ("execution-router.mdc", "Context Capture"),
                         ("execution-router.mdc", "Mid-thread opt-out"), ("critical-gates.mdc", "Interrogate before register"),
                         ("critical-gates.mdc", "Jira story preflight")):
        check(f"Always-on: {name} still has '{needle}'", needle in text[name])
    commands = [c.stem for c in (REPO / "commands").glob("*.md")]
    thin = [c for c in commands if "ba-profile.mdc" in (REPO / "commands" / f"{c}.md").read_text(encoding="utf-8")]
    check("Commands: no command file depends on the removed profile table", not thin, ", ".join(thin))


def main():
    with tempfile.TemporaryDirectory(prefix="ba-efficiency-tests-") as tmp:
        tmp = Path(tmp)
        actions_tests(tmp)
        capture_tests(tmp)
        validate_tests(tmp)
        metrics_tests(tmp)
        canvas_tests(tmp)
        snapshot_slice_tests(tmp)
    docs_tests()
    always_on_tests()
    print(f"\n{'All efficiency script tests passed.' if not FAILURES else f'{len(FAILURES)} failed.'}")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
