"""
End-to-end test for tools/ba-merge-upgrade.py (Version 15).

Builds a personalised Version 14 install the way a real BA's looks after years
of use: their own name for the actions store ("sam-actions" instead of the
package's generic "ba-actions", file names included), a personal profile and
tone rule, their own skill and rule, an edited package file the new version
did not touch, an edited package file the new version also changed, a deleted
package file, Windows line endings, and live action data.

Then runs the whole flow (backup, stage, classify, apply-staging, deploy-plan,
deploy, rollback) against this checkout and checks:

  - nothing personal or data changes; no generic ba-actions file appears
  - every file taken from the new version is written in the BA's naming
  - the drift check blocks a deploy when the live install changed
  - rollback restores every file exactly and removes files the upgrade added
  - the report never prints naming-rule values

Needs git. Standalone, no pytest.

Run:
    python3 tests/test_merge_tool.py      (Windows: py tests/test_merge_tool.py)
"""
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable or "python3"
TOOL = REPO / "tools" / "ba-merge-upgrade.py"
V14_COMMIT = "750a6c542c1b1b0adcbe2c06579a4a7d81275751"
FAILURES = []
SECRET_URL = "https://intranet.example.internal/space/TEAM"


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {detail}" if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(args, home):
    env = {k: v for k, v in os.environ.items() if not k.startswith("BA_")}
    env.update({"HOME": str(home), "USERPROFILE": str(home)})
    proc = subprocess.run([PY, *map(str, args)], capture_output=True, text=True, env=env, timeout=300)
    return proc.returncode, proc.stdout + proc.stderr


def export_commit(commit, dest):
    data = subprocess.run(["git", "-C", str(REPO), "archive", "--format=zip", commit],
                          capture_output=True, check=True).stdout
    zipfile.ZipFile(io.BytesIO(data)).extractall(dest)
    return dest


def changed_since_v14():
    out = subprocess.run(["git", "-C", str(REPO), "diff", "--name-only", V14_COMMIT, "--", "skills/ba-assistant"],
                         capture_output=True, text=True, check=True).stdout
    tracked_dirty = subprocess.run(["git", "-C", str(REPO), "diff", "--name-only", "--", "skills/ba-assistant"],
                                   capture_output=True, text=True, check=True).stdout
    return set(out.split()) | set(tracked_dirty.split())


def localise_install(cursor):
    """Rename ba-actions -> sam-actions in every package text file and file name,
    the way a BA's own install looks before their sync skill genericises it."""
    for root in ("skills", "rules", "commands", "hooks", "_workstream"):
        base = cursor / root
        if not base.exists():
            continue
        for p in sorted(base.rglob("*"), key=lambda x: len(x.parts), reverse=True):
            if p.is_file() and p.suffix in (".md", ".mdc", ".py", ".json", ".tsx", ".template", ".txt"):
                t = p.read_text(encoding="utf-8", errors="strict")
                if "ba-actions" in t:
                    p.write_text(t.replace("ba-actions", "sam-actions"), encoding="utf-8")
            if "ba-actions" in p.name:
                p.rename(p.with_name(p.name.replace("ba-actions", "sam-actions")))
    hj = cursor / "hooks.json"
    if hj.exists():
        hj.write_text(hj.read_text(encoding="utf-8").replace("ba-actions", "sam-actions"), encoding="utf-8")


def main():
    try:
        subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", V14_COMMIT], check=True, capture_output=True)
    except (OSError, subprocess.CalledProcessError):
        print(f"SKIP  Version 14 commit {V14_COMMIT[:7]} not available (shallow clone?). Fetch full history.")
        return 1

    with tempfile.TemporaryDirectory(prefix="ba-merge-tests-") as tmp:
        tmp = Path(tmp)
        v14 = export_commit(V14_COMMIT, tmp / "v14")
        home = tmp / "home"
        cursor = home / ".cursor"
        code, out = run([v14 / "tools" / "install-ba-assistant.py", "--package", v14, "--cursor-home", cursor,
                         "--apply"], home)
        check("Setup: Version 14 installed", code == 0, out[-500:])

        # ---- Personalise ----
        localise_install(cursor)
        ws = cursor / "_workstream"
        for stray in ("ba-actions.json", "ba-actions.md"):
            (ws / stray).unlink(missing_ok=True)
        (ws / "sam-actions.json").write_text(json.dumps({"schema_version": 1, "next_id": 3, "actions": [
            {"id": "BA-001", "task": "Chase sign-off", "status": "open"},
            {"id": "BA-002", "task": "Draft stories", "status": "done"}]}, indent=2), encoding="utf-8")
        (ws / "workboard.json").write_text(json.dumps({"meetings_date": "2026-09-16", "initiatives": []}), encoding="utf-8")
        init = cursor / "initiatives" / "payments"
        init.mkdir(parents=True, exist_ok=True)
        (init / "SESSION-CONTEXT.md").write_text("# Payments\nDEC-1\n", encoding="utf-8")
        profile = cursor / "rules" / "ba-profile.mdc"
        profile.write_text(profile.read_text(encoding="utf-8") + "\nSam's tone: dry.\n", encoding="utf-8")
        tone = cursor / "rules" / "sam-tone-of-voice.mdc"
        tone.write_text("Dry. Short.\n", encoding="utf-8")
        own_rule = cursor / "rules" / "sam-own.mdc"
        own_rule.write_text("My rule.\n", encoding="utf-8")
        own_skill = cursor / "skills" / "sam-skill" / "SKILL.md"
        own_skill.parent.mkdir(parents=True)
        own_skill.write_text("# Mine\n", encoding="utf-8")
        own_sub = cursor / "skills" / "ba-assistant" / "sub-skills" / "sam-extra" / "SKILL.md"
        own_sub.parent.mkdir(parents=True)
        own_sub.write_text("# My sub-skill\n", encoding="utf-8")

        changed = changed_since_v14()
        sub_root = cursor / "skills" / "ba-assistant"
        pkg_files = sorted(p for p in sub_root.rglob("*.md") if "sam-" not in str(p) and "sam-actions" not in p.name)
        rel = lambda p: "skills/ba-assistant/" + p.relative_to(sub_root).as_posix()
        untouched_by_new = [p for p in pkg_files if rel(p) not in changed
                            and "ba-actions" not in (REPO / rel(p)).read_text(encoding="utf-8")]
        touched_by_new = [p for p in pkg_files if rel(p) in changed and (REPO / rel(p)).exists()
                          and "ba-actions" not in (REPO / rel(p)).read_text(encoding="utf-8")]
        b_file, crlf_file, g_file = untouched_by_new[0], untouched_by_new[1], untouched_by_new[2]
        d_file = touched_by_new[0]
        b_file.write_text(b_file.read_text(encoding="utf-8") + "\nSAM EDIT B\n", encoding="utf-8")
        d_file.write_text(d_file.read_text(encoding="utf-8") + "\nSAM EDIT D\n", encoding="utf-8")
        crlf_file.write_bytes(crlf_file.read_bytes().replace(b"\r\n", b"\n").replace(b"\n", b"\r\n"))
        g_file.unlink()

        keep = {"sam-actions.json": ws / "sam-actions.json", "workboard.json": ws / "workboard.json",
                "initiative": init / "SESSION-CONTEXT.md", "profile": profile, "tone rule": tone,
                "own rule": own_rule, "own skill": own_skill, "own sub-skill": own_sub, "B edit": b_file}
        before = {k: sha(v) for k, v in keep.items()}

        rules = tmp / "rules.json"
        rules.write_text(json.dumps({"rules": [
            {"local": "sam-actions", "generic": "ba-actions"},
            {"local": SECRET_URL, "generic": "https://confluence.example.com/wiki"},
        ]}), encoding="utf-8")
        session = tmp / "session"

        # ---- backup / stage / classify ----
        code, out = run([TOOL, "backup", "--cursor-home", cursor, "--session", session], home)
        check("Backup: OK with zip test and restore rehearsal", code == 0 and "Restore rehearsal" in out, out[-800:])
        check("Backup: ROLLBACK.md written", (session / "ROLLBACK.md").exists())
        code, out = run([TOOL, "stage", "--session", session], home)
        check("Stage: OK", code == 0, out[-500:])
        code, out = run([TOOL, "classify", "--session", session, "--base", v14, "--new", REPO, "--rules", rules], home)
        check("Classify: OK", code == 0, out[-1500:])
        for line in out.splitlines():
            if line.startswith("  "):
                print(f"INFO  classify {line.strip()}")
        cls = {r["path"]: r for r in json.loads((session / "classification.json").read_text(encoding="utf-8"))["rows"]}
        c = lambda p: cls.get(p if isinstance(p, str) else p.relative_to(cursor).as_posix(), {}).get("class")
        check("Classify: own edit, new version unchanged -> B", c(b_file) == "B", c(b_file))
        check("Classify: both changed -> D", c(d_file) == "D", c(d_file))
        check("Classify: CRLF-only difference is not a change", c(crlf_file) in ("U", "A"), c(crlf_file))
        check("Classify: deleted package file -> G", c(g_file) == "G", c(g_file))
        check("Classify: own skill and sub-skill -> H",
              c("skills/ba-assistant/sub-skills/sam-extra/SKILL.md") == "H", c("skills/ba-assistant/sub-skills/sam-extra/SKILL.md"))
        check("Classify: own rule -> H", c("rules/sam-own.mdc") == "H", c("rules/sam-own.mdc"))
        check("Classify: old package .sh hook wrapper -> F (remove), not 'your own file'",
              c("hooks/jira-dor-gate.sh") == "F" and cls["hooks/jira-dor-gate.sh"]["decision"] == "remove",
              str(cls.get("hooks/jira-dor-gate.sh")))
        check("Classify: tone rule -> P (personal)", c("rules/sam-tone-of-voice.mdc") == "P")
        check("Classify: actions data -> DATA", c("_workstream/sam-actions.json") == "DATA")
        check("Classify: package paths are mapped into the BA's naming",
              "skills/ba-assistant/references/sam-actions-format.md" in cls
              and "skills/ba-assistant/references/ba-actions-format.md" not in cls)
        report = (session / "report.md").read_text(encoding="utf-8")
        check("Report: naming-rule values never printed", SECRET_URL not in report and "confluence.example.com" not in report)

        # ---- decide ----
        dec_path = session / "decisions.json"
        dec = json.loads(dec_path.read_text(encoding="utf-8"))
        for path, d in dec["files"].items():
            if d["decision"] == "ask":
                d["decision"] = "keep_mine" if d["class"] in ("D", "G", "E") else "take_new"
        dec["patch_profile"] = True
        dec_path.write_text(json.dumps(dec, indent=2), encoding="utf-8")

        code, out = run([TOOL, "apply-staging", "--session", session], home)
        check("Apply-staging: OK", code == 0, out[-1500:])
        staging = session / "staging"
        check("Staging: no generic ba-actions file anywhere",
              not [p for p in staging.rglob("*") if "ba-actions" in p.name], "")
        eod = staging / "skills" / "ba-assistant" / "references" / "eod-closeout-procedure.md"
        check("Staging: taken-new file is written in the BA's naming",
              "sam-actions" in eod.read_text(encoding="utf-8") and "ba-actions" not in eod.read_text(encoding="utf-8"))
        hook = (staging / "hooks" / "session-init.py").read_text(encoding="utf-8")
        check("Staging: hook script uses the BA's actions file", "sam-actions.json" in hook and "ba-actions.json" not in hook)
        check("Staging: D file kept as the BA's (keep_mine)", "SAM EDIT D" in (staging / d_file.relative_to(cursor)).read_text(encoding="utf-8"))
        prof = (staging / "rules" / "ba-profile.mdc").read_text(encoding="utf-8")
        check("Staging: profile patched only in the two rows, tone kept",
              "Sam's tone: dry." in prof and "Chat checkpoint only" in prof and "End-of-session closeout" not in prof)

        # ---- deploy plan, drift, deploy ----
        code, out = run([TOOL, "deploy-plan", "--session", session], home)
        m = re.search(r"--plan-sha (\w+)", out)
        check("Deploy-plan: OK", code == 0 and m, out[-1000:])
        plan = json.loads((session / "deploy-plan.json").read_text(encoding="utf-8"))
        plan_paths = {e["path"] for e in plan["entries"]}
        check("Deploy-plan: data never in the plan",
              not any(p.endswith(("sam-actions.json", "workboard.json")) or p.startswith("initiatives/") for p in plan_paths))
        check("Deploy-plan: own files never in the plan",
              not {"rules/sam-own.mdc", "skills/sam-skill/SKILL.md", "rules/sam-tone-of-voice.mdc"} & plan_paths)

        (ws / "sam-actions.json").write_text("{}", encoding="utf-8")  # another chat writes mid-upgrade
        code, out = run([TOOL, "deploy", "--session", session, "--plan-sha", m.group(1)], home)
        check("Deploy: drift in the live install blocks the deploy", code == 1 and "changed" in out, out[-600:])
        (ws / "sam-actions.json").write_bytes((session / "snapshot" / "home" / "_workstream" / "sam-actions.json").read_bytes())
        code, out = run([TOOL, "deploy", "--session", session, "--plan-sha", "wrong"], home)
        check("Deploy: refuses a plan id that was not reviewed", code == 1, out[-300:])

        code, out = run([TOOL, "deploy", "--session", session, "--plan-sha", m.group(1)], home)
        check("Deploy: OK and verified", code == 0 and "verified by hash" in out, out[-1500:])
        for k, v in keep.items():
            if k == "profile":
                continue
            check(f"Deploy: {k} byte-identical", sha(v) == before[k])
        check("Deploy: no generic ba-actions file in the live install",
              not [p for p in cursor.rglob("*") if "ba-actions" in p.name])
        version = (REPO / "VERSION").read_text(encoding="utf-8").strip()
        check("Deploy: version stamped",
              (cursor / "skills" / "ba-assistant" / "VERSION").read_text(encoding="utf-8").strip() == version)
        added = [e["path"] for e in plan["entries"] if e["action"] == "add"]

        # ---- rollback ----
        code, out = run([TOOL, "rollback", "--session", session], home)
        check("Rollback: OK", code == 0 and "every hash matches" in out, out[-800:])
        check("Rollback: profile restored exactly", sha(profile) == before["profile"])
        check("Rollback: files the upgrade added are gone", not any((cursor / p).exists() for p in added), str(added[:3]))
        code, out = run([TOOL, "drift", "--session", session], home)
        check("Rollback: install matches the backup exactly (no drift)", code == 0, out[-800:])

    print(f"\n{'All merge tool tests passed.' if not FAILURES else f'{len(FAILURES)} failed.'}")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
