#!/usr/bin/env python3
"""Story Readiness Preflight for one Story, computed from the initiative files.

A minimum STRUCTURAL check, not the Definition of Ready. The Definition of Ready
stays the BA's judgement (ba-story-writing/SKILL.md): business value and scope,
semantic AC coverage and edge cases, NFRs, feasibility and sizing, independence,
and any design, legal, compliance or stakeholder approval. None of those are
checked here. A pass prints "Structural preflight passed", never "DoR met".

Shared by the external-write-gate hook (at Jira create time) and the agent
(before asking the BA to create). It never trusts a stored pass: every run
recomputes the result from the current files and the story text. The file name,
arguments, exit codes and the `Gate: dor-check:` line are kept from the old
"DoR check" so existing installs and skills keep working.

Five structural conditions:
  requirement   a linked requirement exists and every linked one is
                interrogated or confirmed (or later) in the requirements register.
                IDs: HLR-01, detailed HLR-01.1 / HLR-08.21 (canonical), and legacy
                type-prefixed IDs (REQ-1, FR-001, BR-001, NFR-001, ...). A detailed
                ID is its own requirement: HLR-08 never stands in for HLR-08.1.
  acs           Given / When / Then acceptance criteria are present
  dependencies  dependencies are listed (a "Dependencies:" line or heading, even
                "None", or dependsOn on the story record). TBD / TBC / ? / unknown
                and empty sections don't count.
  moscow        MoSCoW is set for the story's scope (story record, the linked
                requirement's moscowMatrix for that scope, or a "MoSCoW:" line)
  risks         risks are logged (a "Risks:" line or heading, even "None
                identified", or a risk in status-data.json for the story's scope /
                requirements). Placeholders don't count, and a word such as
                "Risk-free" is not a Risks section.

Where the story is found: status-data.json -> stories[] (matched by Jira key or
title), plus the text being sent to Jira (summary + description, ADF flattened).

  python3 ~/.cursor/_workstream/dor-check.py --initiative refunds --title "Partial refund API" \
      --description-file story.md [--record] [--json]

--record upserts status-data.json -> dorChecks (field names kept for older
initiatives; a "pass" there means the structural preflight passed, nothing more) (storyTitle, result, firstAttempt
on the first run, missingCriteria, checkedAt) for the metrics. The gate does not
read dorChecks. Exit 0 = pass, 3 = not ready, 1 = bad input / initiative not found.
Windows: use `py` instead of `python3`.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

CHECK_NAME = "Story Readiness Preflight"
PASS_TEXT = "Structural preflight passed"
FAIL_TEXT = "Structural preflight not passed"
NOT_CHECKED = ("It confirms a linked requirement, Given/When/Then acceptance criteria, dependencies, MoSCoW "
               "and risks are present. It does not confirm semantic completeness, required sign-offs, "
               "feasibility, sizing or NFR coverage. Semantic readiness and required human approvals "
               "still need review.")
CRITERIA = ("requirement", "acs", "dependencies", "moscow", "risks")
LABELS = {
    "requirement": "no interrogated/confirmed requirement linked",
    "acs": "no Given/When/Then ACs",
    "dependencies": "dependencies not listed",
    "moscow": "MoSCoW unset for its scope",
    "risks": "risks not logged",
}
READY_STATUSES = {"interrogated", "confirmed", "in-flight", "inflight", "delivered"}
MOSCOW_RE = re.compile(r"\bmo\s*s\s*co\s*w\b\s*[:=\-]?\s*(must|should|could|won'?t|wont)\b", re.I)
GWT_RE = re.compile(r"\bgiven\b.{1,400}?\bwhen\b.{1,400}?\bthen\b", re.I | re.S)
# A labelled section: "Dependencies: ...", "**Risks:** ...", "- Risks: ...", or a
# heading that starts with the word ("## Risks", "### Risks and mitigations") with
# its value on the next line. A word that merely starts with the label
# ("Risk-free", "Dependency injection is used") is not a section.
def _label_re(word: str) -> re.Pattern:
    return re.compile(
        rf"^[ \t]*(?:"
        rf"(?:[-*][ \t]*)?(?:\*\*)?(?:{word})(?:\*\*)?[ \t]*:(?:\*\*)?[ \t]*(?P<v>.*)"
        rf"|#+[ \t]*(?:\*\*)?(?:{word})(?![\w-])[^\n]*"
        rf"|(?:\*\*)?(?:{word})(?:\*\*)?[ \t]*$)", re.I | re.M)


DEPS_RE = _label_re(r"dependenc(?:y|ies)")
RISKS_RE = _label_re(r"risks?")
PLACEHOLDERS = {"tbd", "tbc", "tba", "todo", "to do", "to be confirmed", "to be determined", "?", "??",
                "???", "unknown", "pending", "xxx", "..."}
# Requirement IDs: canonical HLR-01 / HLR-01.1 / HLR-08.21, and legacy type-prefixed
# IDs (REQ-1, FR-001, BR-001, NFR-001, COMP-001, ...). The optional letter suffix
# (REQ-1a) is kept from the old parser.
REQ_ID = r"[A-Z][A-Z0-9]{0,9}-\d{1,4}(?:\.\d{1,3})*[a-z]?"
REQ_ID_FULL_RE = re.compile(rf"^{REQ_ID}$")
REG_HEADING_RE = re.compile(rf"^#{{2,5}}\s+({REQ_ID})(?![\w.])", re.M)
STATUS_LINE_RE = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?status(?:\*\*)?\s*[:|]\s*(?:\*\*)?\s*([A-Za-z\-]+)", re.I | re.M)


# ---------- helpers ----------

def norm(s) -> str:
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


def flatten(obj) -> str:
    """Plain text from a string, a list, or Atlassian Document Format (ADF)."""
    if obj is None:
        return ""
    if isinstance(obj, str):
        return obj
    if isinstance(obj, list):
        return "\n".join(flatten(x) for x in obj)
    if isinstance(obj, dict):
        parts = []
        if isinstance(obj.get("text"), str):
            parts.append(obj["text"])
        for key in ("content", "value"):
            if key in obj and not isinstance(obj[key], str):
                parts.append(flatten(obj[key]))
        block = "\n" if obj.get("type") in ("paragraph", "heading", "listItem", "tableRow", "doc") else " "
        return block.join(p for p in parts if p)
    return str(obj)


def titles_match(a: str, b: str) -> bool:
    a, b = norm(a), norm(b)
    if len(a) < 6 or len(b) < 6:
        return False
    if a == b:
        return True
    shorter, longer = (a, b) if len(a) <= len(b) else (b, a)
    return len(shorter) >= 0.7 * len(longer) and longer.startswith(shorter)


def load_json(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8", errors="ignore"))
    except (OSError, ValueError):
        return None


# ---------- where things live ----------

def config_initiatives_root(cursor_home: Path) -> str:
    text = ""
    for name in ("ba-assistant-config.mdc", "ba-profile.mdc"):
        try:
            text += (cursor_home / "rules" / name).read_text(encoding="utf-8", errors="ignore") + "\n"
        except OSError:
            pass
    m = re.search(r'^\s*initiativesRoot\s*:\s*["\']?([^"\'#\n]+)', text, re.M)
    value = m.group(1).strip() if m else ""
    return "" if not value or value.startswith("[") else os.path.expanduser(value)


def folder_key(path) -> tuple | str:
    """Same folder, however it is spelled: initiatives/ and Initiatives/ on a
    case-insensitive disk (macOS, Windows), symlinks, short names."""
    try:
        st = os.stat(path)
        if st.st_ino:
            return (st.st_dev, st.st_ino)
    except OSError:
        pass
    return os.path.normcase(os.path.realpath(str(path)))


def initiative_roots(cursor_home: Path) -> list[Path]:
    roots = [os.environ.get("BA_INITIATIVES_ROOT", "") or config_initiatives_root(cursor_home),
             str(cursor_home / "initiatives"), str(cursor_home / "Initiatives"), str(cursor_home / "blueprints")]
    out: list[Path] = []
    keys: set = set()
    for r in roots:
        if r and os.path.isdir(r) and folder_key(r) not in keys:
            keys.add(folder_key(r))
            out.append(Path(r))
    return out


def all_initiatives(cursor_home: Path) -> list[Path]:
    found: list[Path] = []
    keys: set = set()
    for root in initiative_roots(cursor_home):
        for marker in ("status-data.json", "SESSION-CONTEXT.md"):
            for p in glob.glob(str(root / "**" / marker), recursive=True):
                d = Path(p).parent
                if folder_key(d) not in keys:
                    keys.add(folder_key(d))
                    found.append(d)
    return found


def find_story_record(sd: dict | None, title: str, key: str) -> dict | None:
    if not isinstance(sd, dict):
        return None
    for s in sd.get("stories") or []:
        if not isinstance(s, dict):
            continue
        if key and norm(s.get("key")) == norm(key):
            return s
        if titles_match(s.get("title", ""), title):
            return s
    return None


def locate_initiative(cursor_home: Path, title: str, key: str, hint: str = "") -> tuple[Path | None, str]:
    """(folder, how it was found). The story's own record wins; then the chat's
    initiative from session-init; then the only initiative there is."""
    candidates = all_initiatives(cursor_home)
    for d in candidates:
        if find_story_record(load_json(d / "status-data.json"), title, key):
            return d, "story record"
    if hint:
        h = Path(hint)
        d = h.parent if h.is_file() else h
        if d.is_dir():
            return d, "this chat's initiative"
    if len(candidates) == 1:
        return candidates[0], "only initiative"
    return None, ""


def register_statuses(init_dir: Path) -> dict[str, str]:
    """{requirement id: status} from the requirements register (headings with a
    Status line, and index tables with ID and status columns)."""
    files = []
    for pattern in ("**/requirements-register.md", "**/register.md", "**/requirements/register.md"):
        files += glob.glob(str(init_dir / pattern), recursive=True)
    statuses: dict[str, str] = {}
    for f in sorted(set(files)):
        try:
            text = Path(f).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        heads = list(REG_HEADING_RE.finditer(text))
        for i, h in enumerate(heads):
            block = text[h.end(): heads[i + 1].start() if i + 1 < len(heads) else len(text)]
            m = STATUS_LINE_RE.search(block)
            if m:
                statuses.setdefault(h.group(1), m.group(1).lower())
        cols = None
        for line in text.splitlines():
            if not line.strip().startswith("|"):
                cols = None if not line.strip() else cols
                continue
            cells = [c.strip().strip("*`") for c in line.strip().strip("|").split("|")]
            lower = [c.lower() for c in cells]
            if "status" in lower and "id" in lower:
                cols = (lower.index("id"), lower.index("status"))
                continue
            if cols and len(cells) > max(cols) and REQ_ID_FULL_RE.match(cells[cols[0]]):
                statuses.setdefault(cells[cols[0]], cells[cols[1]].lower())
    return statuses


def id_in_text(rid: str, text: str) -> bool:
    """HLR-08 matches "HLR-08" and "HLR-08," but not "HLR-08.1" or "HLR-080"."""
    return re.search(rf"(?<![\w.-]){re.escape(rid)}(?!\w|\.\d)", text) is not None


def section_listed(label_re: re.Pattern, text: str) -> bool:
    """True when a labelled section has a real value (placeholders don't count)."""
    for m in label_re.finditer(text):
        value = (m.group("v") or "").strip()
        if not value:
            rest = text[m.end():].splitlines()
            nxt = next((ln.strip() for ln in rest if ln.strip()), "")
            value = "" if nxt.startswith("#") else nxt
        value = re.sub(r"^[-*\s]+|[*`_\s.]+$", "", value).strip()
        if value and value.lower() not in PLACEHOLDERS:
            return True
    return False


# ---------- the check ----------

def check_story(init_dir: Path | None, title: str, description: str = "", key: str = "") -> dict:
    text = f"{title}\n{description}"
    sd = load_json(init_dir / "status-data.json") if init_dir else None
    sd = sd if isinstance(sd, dict) else {}
    record = find_story_record(sd, title, key) or {}
    statuses = register_statuses(init_dir) if init_dir else {}

    linked = [r for r in record.get("linkedRequirements") or [] if isinstance(r, str)]
    for rid in statuses:
        if id_in_text(rid, text) and rid not in linked:
            linked.append(rid)

    checks: dict[str, dict] = {}
    if not init_dir:
        checks["requirement"] = {"ok": False, "detail": "couldn't tell which initiative this story belongs to"}
    elif not linked:
        checks["requirement"] = {"ok": False, "detail": "no requirement ID linked (story record or description)"}
    else:
        not_ready = [f"{r} ({statuses.get(r, 'not in register')})" for r in linked
                     if statuses.get(r, "") not in READY_STATUSES]
        checks["requirement"] = {"ok": not not_ready,
                                 "detail": ("not interrogated/confirmed: " + ", ".join(not_ready)) if not_ready
                                 else "linked: " + ", ".join(linked)}

    checks["acs"] = {"ok": bool(GWT_RE.search(text)), "detail": "Given/When/Then found" if GWT_RE.search(text)
                     else "no Given/When/Then in the story text"}

    deps_ok = "dependsOn" in record or section_listed(DEPS_RE, description)
    checks["dependencies"] = {"ok": deps_ok, "detail": "listed" if deps_ok
                              else "no Dependencies section with a value (write 'None' if none; TBD doesn't count)"}

    scope = record.get("scope") or ""
    moscow = record.get("moscow") or ""
    if not moscow:
        m = MOSCOW_RE.search(text)
        moscow = m.group(1) if m else ""
    if not moscow and scope:
        for req in sd.get("requirements") or []:
            if isinstance(req, dict) and req.get("id") in linked:
                for cell in req.get("moscowMatrix") or []:
                    if isinstance(cell, dict) and cell.get("scope") == scope and cell.get("rating"):
                        moscow = str(cell["rating"])
    checks["moscow"] = {"ok": bool(moscow), "detail": f"{moscow}" + (f" for {scope}" if scope else "") if moscow
                        else "no MoSCoW on the story or its requirement for scope " + (scope or "(unknown)")}

    risks = sd.get("raid", {}).get("risks") if isinstance(sd.get("raid"), dict) else None
    matched = [r.get("id") for r in risks or [] if isinstance(r, dict) and (
        (scope and r.get("scope") == scope) or set(r.get("linkedRequirements") or []) & set(linked))]
    risks_ok = bool(matched) or section_listed(RISKS_RE, description)
    checks["risks"] = {"ok": risks_ok, "detail": ("logged: " + ", ".join(str(m) for m in matched)) if matched
                       else ("Risks section in the story" if risks_ok
                             else "no risk logged for this scope and no Risks section with a value")}

    missing = [c for c in CRITERIA if not checks[c]["ok"]]
    return {"check": CHECK_NAME, "result": "pass" if not missing else "fail", "missing": missing,
            "missing_labels": [LABELS[c] for c in missing], "checks": checks,
            "story": title, "initiative": str(init_dir) if init_dir else "", "linkedRequirements": linked}


def record_result(init_dir: Path, outcome: dict, key: str = "") -> None:
    """Upsert status-data.json -> dorChecks for the metrics (never the gate's evidence)."""
    path = init_dir / "status-data.json"
    sd = load_json(path) if path.exists() else {}
    if not isinstance(sd, dict):
        raise ValueError(f"{path} is not a JSON object; not recording")
    rows = sd.setdefault("dorChecks", [])
    row = next((r for r in rows if isinstance(r, dict) and (
        (key and norm(r.get("storyKey")) == norm(key)) or titles_match(r.get("storyTitle", ""), outcome["story"]))), None)
    if row is None:
        row = {"storyTitle": outcome["story"], "firstAttempt": outcome["result"]}
        rows.append(row)
    if key:
        row["storyKey"] = key
    row.update({"result": outcome["result"], "missingCriteria": outcome["missing"],
                "checkedAt": date.today().isoformat(), "checkedBy": "dor-check.py"})
    path.write_text(json.dumps(sd, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Story Readiness Preflight (structural checks only) for one Story")
    ap.add_argument("--initiative", help="initiative slug (folder under the initiatives root)")
    ap.add_argument("--title", required=True, help="the story summary exactly as it will go to Jira")
    ap.add_argument("--description", default="")
    ap.add_argument("--description-file")
    ap.add_argument("--key", default="", help="Jira key, if the story already has one")
    ap.add_argument("--cursor-home", default=str(Path.home() / ".cursor"))
    ap.add_argument("--record", action="store_true", help="upsert the result into status-data.json -> dorChecks")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    home = Path(os.path.expanduser(args.cursor_home))
    desc = args.description
    if args.description_file:
        desc = Path(args.description_file).read_text(encoding="utf-8", errors="ignore")
    if args.initiative:
        init_dir = next((d for d in all_initiatives(home) if d.name == args.initiative), None)
        if init_dir is None:
            print(f"{CHECK_NAME}: could not run (initiative '{args.initiative}' not found under {', '.join(map(str, initiative_roots(home)))})")
            return 1
    else:
        init_dir, _ = locate_initiative(home, args.title, args.key, os.environ.get("CURSOR_SESSION_CONTEXT_PATH", ""))
    outcome = check_story(init_dir, args.title, desc, args.key)
    if args.record and init_dir:
        record_result(init_dir, outcome, args.key)
    if args.json:
        print(json.dumps(outcome, indent=2))
    else:
        for c in CRITERIA:
            ch = outcome["checks"][c]
            print(f"{'PASS' if ch['ok'] else 'MISS'}  {c:<12} {ch['detail']}")
        print(f"Gate: dor-check: {'PASS' if outcome['result'] == 'pass' else 'NOT READY (' + ', '.join(outcome['missing_labels']) + ')'}")
        if outcome["result"] == "pass":
            print(f"{CHECK_NAME}: {PASS_TEXT}. {NOT_CHECKED}")
        else:
            print(f"{CHECK_NAME}: {FAIL_TEXT}: {', '.join(outcome['missing_labels'])}. "
                  "Creating it anyway is a BA override.")
    return 0 if outcome["result"] == "pass" else 3


if __name__ == "__main__":
    sys.exit(main())
