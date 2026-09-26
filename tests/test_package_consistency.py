"""
Text-level regression checks over the package's skills, rules and commands.

Cheap string checks for mistakes that keep coming back: a retired write path, a
skill that is not shipped, a dangling file name, a skill missing from the user
guide. Package repo only; never installed, never run by the assistant.

Run:
    python3 tests/test_package_consistency.py   (Windows: py ...)
"""
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SHIPPED = [REPO / "skills", REPO / "rules", REPO / "commands", REPO / "hooks"]
FAILURES = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {detail}" if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def shipped_files():
    for root in SHIPPED:
        for p in root.rglob("*"):
            if p.is_file() and p.suffix in {".md", ".mdc", ".py", ".json"} and "tests" not in p.parts:
                yield p


def grep(pattern, files=None):
    rx = re.compile(pattern)
    hits = []
    for p in files or shipped_files():
        for i, line in enumerate(p.read_text(encoding="utf-8", errors="ignore").splitlines(), 1):
            if rx.search(line):
                hits.append(f"{p.relative_to(REPO)}:{i}")
    return hits


def main():
    skill = REPO / "skills" / "ba-assistant"

    hits = grep(r"ACTIVE INITIATIVE CONTEXT")
    check("P1 nothing labels an initiative ACTIVE from session start", not hits, ", ".join(hits))

    debrief = skill / "sub-skills" / "ba-meeting-debrief" / "SKILL.md"
    hits = grep(r"(?i)(add|write|append)[^.]*personal[ _]tasks?[^.]*workboard\.json", [debrief])
    hits += grep(r"PERSONAL TASKS \(", [debrief])
    check("P2 debrief never writes personal tasks to workboard.json", not hits, ", ".join(hits))

    hits = [h for h in grep(r"\[your-jira-templates\]") if "CUSTOMIZATION" not in h]
    check("P3 no routing on the unshipped [your-jira-templates] skill", not hits, ", ".join(hits))

    fmt = (skill / "references" / "jira-ticket-format.md").read_text(encoding="utf-8")
    check("P3 Jira format has the BA approval gate before create",
          "BA approval before any create" in fmt and "Create in Jira" in fmt)
    story = (skill / "sub-skills" / "ba-story-writing" / "SKILL.md").read_text(encoding="utf-8")
    check("P3 story-writing has draft -> approve -> create", "Jira create (draft" in story)

    hits = grep(r"Schema_Field_Validator")
    check("P4 no hard dependency on Schema_Field_Validator", not hits, ", ".join(hits))
    check("P4 story-writing carries the internal schema checklist", "internal checklist" in story)

    hits = grep(r"slash-commands-ux\.md|\*\*agent-memory\*\*|`mcps/|(?<![<\w])/summary\b|ba-status-page-publisher \(workflow\)")
    check("B no dangling file or command names", not hits, ", ".join(hits))

    guide = (skill / "BA_Assistant_User_Guide.md").read_text(encoding="utf-8")
    missing = [d.name for d in (skill / "sub-skills").iterdir()
               if d.is_dir() and f"`{d.name}`" not in guide]
    check("A user guide lists every sub-skill folder", not missing, ", ".join(missing))
    missing = [c.stem for c in (REPO / "commands").glob("*.md")
               if c.stem != "install-ba-assistant" and f"`/{c.stem}" not in guide]
    check("A user guide lists every slash command", not missing, ", ".join(missing))

    step2 = (skill / "SKILL.md").read_text(encoding="utf-8")
    reanchor = (REPO / "commands" / "reanchor.md").read_text(encoding="utf-8")
    check("H resume read order lives in SKILL.md Step 2 only",
          "Resume read order" in step2 and "Step 2, item 3" in reanchor
          and "Read, in this order" not in reanchor)

    profile = (REPO / "rules" / "execution-router.mdc").read_text(encoding="utf-8")
    check("Config: always-on router maps placeholders to setup values",
          all(k in profile for k in ("jira.projectKey", "confluence.spaceKey", "domainDocs",
                                    "paths.initiativesRoot", "paths.downloadsPath", "`name`")))
    template = (skill / "ba-profile.template.mdc").read_text(encoding="utf-8")
    setup = (skill / "sub-skills" / "ba-setup" / "SKILL.md").read_text(encoding="utf-8")
    for key in ("domainDocs", "initiativesRoot", "downloadsPath", "projectKey", "spaceKey"):
        check(f"Config: setup captures {key} and the template has it", key in setup and key in template)

    print(f"\n{'All consistency checks passed.' if not FAILURES else f'{len(FAILURES)} failed.'}")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
