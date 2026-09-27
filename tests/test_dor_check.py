"""
Tests for the Definition of Ready check (_workstream/dor-check.py) and how the
external-write-gate hook uses it on Jira Story creates.

The check recomputes readiness from the initiative files every time; a stored
`result: pass` row is never evidence. A Story is a Jira write, so the hook
always asks the BA: "DoR met" when every criterion passes, otherwise
"DoR not met: <missing>. Approve to create anyway as a BA override."

Run:
    python3 tests/test_dor_check.py      (Windows: py tests/test_dor_check.py)
"""
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
GATE = REPO / "hooks" / "external-write-gate.py"
DOR = REPO / "_workstream" / "dor-check.py"
PY = sys.executable or "python3"
results = []

GWT = ("Given a month with transactions\nWhen I export the report\nThen I get one CSV row per transaction\n\n"
       "Dependencies: none\n\nRisks: large months may time out (R-1)")


def check(name, ok, detail=""):
    ok = bool(ok)
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {detail}" if not ok and detail else ""))


def env_for(home, extra=None):
    env = {k: v for k, v in os.environ.items() if not k.startswith("BA_") and k != "CURSOR_SESSION_CONTEXT_PATH"}
    env.update({"HOME": str(home), "USERPROFILE": str(home)})
    env.update(extra or {})
    return env


def gate(home, fields=None, tool="createJiraIssue", runlayer=True, extra_env=None, script=GATE):
    args = {"cloudId": "x", "projectKey": "PROJ", **(fields or {})}
    if runlayer:
        payload = {"tool_name": "execute_tool", "tool_input": json.dumps({"tool_name": tool, "arguments": args})}
    else:
        payload = {"tool_name": tool, "tool_input": json.dumps(args)}
    proc = subprocess.run([PY, str(script)], input=json.dumps(payload), capture_output=True, text=True,
                          env=env_for(home, extra_env), timeout=30)
    return json.loads(proc.stdout.strip().splitlines()[-1])


def dor_cli(home, *args):
    proc = subprocess.run([PY, str(DOR), "--cursor-home", str(home / ".cursor"), *args], capture_output=True,
                          text=True, env=env_for(home), timeout=30)
    return proc.returncode, proc.stdout


def make_initiative(home, name, stories=None, requirements=None, risks=None, register=None, dor_rows=None, raw=None):
    d = home / ".cursor" / "initiatives" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / "SESSION-CONTEXT.md").write_text(f"# {name}\n", encoding="utf-8")
    if raw is not None:
        (d / "status-data.json").write_text(raw, encoding="utf-8")
    else:
        sd = {"stories": stories or [], "requirements": requirements or [], "raid": {"risks": risks or []}}
        if dor_rows is not None:
            sd["dorChecks"] = dor_rows
        (d / "status-data.json").write_text(json.dumps(sd), encoding="utf-8")
    if register is not None:
        (d / "requirements-register.md").write_text(register, encoding="utf-8")
    return d


def ready_home(tmp, name="export"):
    home = Path(tempfile.mkdtemp(dir=tmp))
    make_initiative(home, name,
                    stories=[{"title": "Export the monthly report", "scope": "feature_export",
                              "linkedRequirements": ["REQ-1"], "dependsOn": []}],
                    requirements=[{"id": "REQ-1", "moscowMatrix": [{"scope": "feature_export", "rating": "Must"}]}],
                    risks=[{"id": "R-1", "title": "Large files time out", "scope": "feature_export"}],
                    register="### REQ-1 · Monthly export\n**Status:** Confirmed\n")
    return home


def story(summary="Export the monthly report", description=GWT, itype="Story"):
    f = {"summary": summary, "description": description}
    if itype is not None:
        f["issueTypeName"] = itype
    return f


def main():
    with tempfile.TemporaryDirectory(prefix="dor-") as tmp:
        tmp = Path(tmp)

        # --- auto-pass: every criterion met ---
        home = ready_home(tmp)
        out = gate(home, story())
        check("Ready story: DoR met, the BA still approves the Jira write",
              out["permission"] == "ask" and out["user_message"].startswith("DoR met"), str(out))
        code, txt = dor_cli(home, "--initiative", "export", "--title", "Export the monthly report", "--description", GWT)
        check("dor-check.py CLI: ready story exits 0 with a PASS gate line", code == 0 and "Gate: dor-check: PASS" in txt, txt)

        # --- a stored pass is never evidence ---
        home = Path(tempfile.mkdtemp(dir=tmp))
        make_initiative(home, "export", stories=[{"title": "Export the monthly report"}],
                        dor_rows=[{"storyTitle": "Export the monthly report", "result": "pass", "firstAttempt": "pass"}])
        out = gate(home, story(description="Export it please"))
        check("A stored result: pass row does not make an unready story pass",
              out["permission"] == "ask" and out["user_message"].startswith("DoR not met")
              and "no Given/When/Then ACs" in out["user_message"] and "BA override" in out["user_message"], str(out))

        # --- each criterion on its own ---
        home = ready_home(tmp)
        (home / ".cursor" / "initiatives" / "export" / "requirements-register.md").write_text(
            "### REQ-1 · Monthly export\n**Status:** Proposed\n", encoding="utf-8")
        out = gate(home, story())
        check("Requirement only proposed -> 'no interrogated/confirmed requirement linked'",
              "no interrogated/confirmed requirement linked" in out["user_message"], str(out))
        home = ready_home(tmp)
        sd_path = home / ".cursor" / "initiatives" / "export" / "status-data.json"
        sd = json.loads(sd_path.read_text(encoding="utf-8"))
        sd["requirements"][0]["moscowMatrix"] = [{"scope": "other_scope", "rating": "Must"}]
        sd_path.write_text(json.dumps(sd), encoding="utf-8")
        out = gate(home, story())
        check("MoSCoW set for another scope only -> 'MoSCoW unset for its scope'",
              out["user_message"] == "DoR not met: MoSCoW unset for its scope. Approve to create anyway as a BA override.",
              str(out))
        home = ready_home(tmp)
        sd = json.loads((home / ".cursor" / "initiatives" / "export" / "status-data.json").read_text(encoding="utf-8"))
        del sd["stories"][0]["dependsOn"]
        sd["raid"]["risks"] = []
        (home / ".cursor" / "initiatives" / "export" / "status-data.json").write_text(json.dumps(sd), encoding="utf-8")
        out = gate(home, story(description="Given x When y Then z"))
        check("No dependencies and no risks -> both named",
              "dependencies not listed" in out["user_message"] and "risks not logged" in out["user_message"], str(out))

        # --- the ticket text alone can satisfy it (no story record yet) ---
        home = Path(tempfile.mkdtemp(dir=tmp))
        make_initiative(home, "solo", register="| ID | Requirement | status |\n|---|---|---|\n| REQ-7 | Audit trail | interrogated |\n")
        desc = ("Implements REQ-7.\nMoSCoW: Should\n\nGiven an admin When they open the log Then every change is listed\n\n"
                "## Dependencies\nNone\n\n## Risks\nNone identified")
        out = gate(home, story("Show the audit trail to admins", desc))
        check("Description-only story (register table, MoSCoW line, sections) passes",
              out["user_message"].startswith("DoR met"), str(out))

        # --- the same folder reached two ways (initiatives/ and Initiatives/ on macOS/Windows) ---
        home = Path(tempfile.mkdtemp(dir=tmp))
        make_initiative(home, "solo", register="### REQ-7 · Audit trail\n**Status:** Confirmed\n")
        try:
            os.symlink(home / ".cursor" / "initiatives", home / ".cursor" / "Initiatives", target_is_directory=True)
            alias_made = True
        except OSError:
            alias_made = False
        if alias_made:
            out = gate(home, story("Show the audit trail to admins",
                                   "Implements REQ-7.\nMoSCoW: Should\nGiven a When b Then c\nDependencies: none\nRisks: none"))
            check("One initiative reached through two folder spellings still counts as one",
                  out["user_message"].startswith("DoR met"), str(out))

        # --- which initiative ---
        home = ready_home(tmp, "beta")
        make_initiative(home, "alpha")
        out = gate(home, story())
        check("Two initiatives, no chat initiative: the story's own record decides", out["user_message"].startswith("DoR met"), str(out))
        home = Path(tempfile.mkdtemp(dir=tmp))
        make_initiative(home, "alpha")
        make_initiative(home, "beta")
        out = gate(home, story("Brand new story nobody recorded"))
        check("Unknown initiative -> DoR not met, BA decides (never silently allowed)",
              out["permission"] == "ask" and "DoR not met" in out["user_message"], str(out))

        # --- which calls count as a Story create ---
        home = ready_home(tmp)
        for label, fields, runlayer in (
                ("direct createJiraIssue (not wrapped)", story(), False),
                ("'User Story' issue type", story(itype="User Story"), True),
                ("issue type given only by id", {"summary": "Export the monthly report", "description": GWT,
                                                 "issuetype": {"id": "10001"}}, True)):
            out = gate(home, fields, runlayer=runlayer)
            check(f"DoR runs for {label}", out["permission"] == "ask" and "DoR" in out["user_message"], str(out))
        out = gate(home, {"summary": "Export crashes", "description": "found while testing story PROJ-12",
                          "issueTypeName": "Bug"})
        check("A Bug mentioning a story is a plain Jira write (no DoR)",
              out["permission"] == "ask" and "DoR" not in out["user_message"], str(out))
        spec = importlib.util.spec_from_file_location("ewg", GATE)
        ewg = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(ewg)
        _, _, _, key = ewg.story_fields({"fields": {"project": {"key": "PROJ"}, "summary": "x", "issuetype": {"name": "Story"}}})
        check("project.key is never taken as the story's key", key == "", key)

        # --- robustness ---
        home = Path(tempfile.mkdtemp(dir=tmp))
        make_initiative(home, "broken", raw="{not json")
        out = gate(home, story())
        check("Malformed status-data.json: no crash, DoR not met, BA decides",
              out["permission"] == "ask" and "DoR not met" in out["user_message"], str(out))
        lone = tmp / "lone-hooks"
        lone.mkdir()
        shutil.copy(GATE, lone / "external-write-gate.py")
        out = gate(Path(tempfile.mkdtemp(dir=tmp)), story(), script=lone / "external-write-gate.py")
        check("dor-check.py missing: the gate still asks and says the check couldn't run",
              out["permission"] == "ask" and "couldn't run" in out["user_message"], str(out))

        # --- --record keeps dorChecks for metrics ---
        home = ready_home(tmp)
        args = ("--initiative", "export", "--title", "Export the monthly report", "--record")
        code, txt = dor_cli(home, *args, "--description", "no criteria here")
        code2, txt2 = dor_cli(home, *args, "--description", GWT)
        rows = json.loads((home / ".cursor" / "initiatives" / "export" / "status-data.json").read_text())["dorChecks"]
        check("--record: first run sets firstAttempt; a later pass updates result only",
              code == 3 and code2 == 0 and len(rows) == 1 and rows[0]["firstAttempt"] == "fail"
              and rows[0]["result"] == "pass" and rows[0]["checkedBy"] == "dor-check.py", str(rows))

        # --- audit log ---
        home = ready_home(tmp)
        gate(home, story())
        gate(home, story(description="nothing"))
        log = home / ".cursor" / "_workstream" / "audit-log.jsonl"
        rows = [json.loads(l) for l in log.read_text(encoding="utf-8").splitlines()] if log.exists() else []
        check("Audit log records the DoR outcome for each Story create",
              [r.get("dor") for r in rows] == ["pass", "fail"] and rows[1].get("missing"), str(rows))

    passed = sum(results)
    print(f"\n{passed}/{len(results)} DoR checks passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
