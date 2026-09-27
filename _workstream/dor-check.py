#!/usr/bin/env python3
"""Definition of Ready check for one Story, computed from the initiative files.

Shared by the external-write-gate hook (at Jira create time) and the agent
(before asking the BA to create). It never trusts a stored pass: every run
recomputes the result from the current files and the story text.

Criteria (ba-story-writing/SKILL.md, Definition of Ready):
  requirement   a linked requirement exists and every linked one is
                interrogated or confirmed (or later) in the requirements register
  acs           Given / When / Then acceptance criteria are present
  dependencies  dependencies are listed (a "Dependencies" section, even "None",
                or dependsOn on the story record)
  moscow        MoSCoW is set for the story's scope (story record, the linked
                requirement's moscowMatrix for that scope, or a "MoSCoW:" line)
  risks         risks are logged (a "Risks" section, even "None identified", or a
                risk in status-data.json for the story's scope / requirements)

Where the story is found: status-data.json -> stories[] (matched by Jira key or
title), plus the text being sent to Jira (summary + description, ADF flattened).

  python3 ~/.cursor/_workstream/dor-check.py --initiative refunds --title "Partial refund API" \
      --description-file story.md [--record] [--json]

--record upserts status-data.json -> dorChecks (storyTitle, result, firstAttempt
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
DEPS_RE = re.compile(r"(^|\n)\s*(#+\s*|\*\*|[-*]\s*)?dependenc(y|ies)\b", re.I)
RISKS_RE = re.compile(r"(^|\n)\s*(#+\s*|\*\*|[-*]\s*)?risks?\b", re.I)
REG_HEADING_RE = re.compile(r"^#{2,5}\s+([A-Z][A-Z0-9]{0,9}-\d{1,4}[a-z]?)\b", re.M)
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


def initiative_roots(cursor_home: Path) -> list[Path]:
    roots = [os.environ.get("BA_INITIATIVES_ROOT", "") or config_initiatives_root(cursor_home),
             str(cursor_home / "initiatives"), str(cursor_home / "Initiatives"), str(cursor_home / "blueprints")]
    out: list[Path] = []
    for r in roots:
        if r and os.path.isdir(r) and os.path.realpath(r) not in [os.path.realpath(x) for x in out]:
            out.append(Path(r))
    return out


def all_initiatives(cursor_home: Path) -> list[Path]:
    found: list[Path] = []
    for root in initiative_roots(cursor_home):
        for marker in ("status-data.json", "SESSION-CONTEXT.md"):
            for p in glob.glob(str(root / "**" / marker), recursive=True):
                d = Path(p).parent
                if d not in found:
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
            if cols and len(cells) > max(cols) and re.match(r"^[A-Z][A-Z0-9]{0,9}-\d{1,4}[a-z]?$", cells[cols[0]]):
                statuses.setdefault(cells[cols[0]], cells[cols[1]].lower())
    return statuses


# ---------- the check ----------

def check_story(init_dir: Path | None, title: str, description: str = "", key: str = "") -> dict:
    text = f"{title}\n{description}"
    sd = load_json(init_dir / "status-data.json") if init_dir else None
    sd = sd if isinstance(sd, dict) else {}
    record = find_story_record(sd, title, key) or {}
    statuses = register_statuses(init_dir) if init_dir else {}

    linked = [r for r in record.get("linkedRequirements") or [] if isinstance(r, str)]
    for rid in statuses:
        if re.search(rf"\b{re.escape(rid)}\b", text) and rid not in linked:
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

    deps_ok = "dependsOn" in record or bool(DEPS_RE.search(description))
    checks["dependencies"] = {"ok": deps_ok, "detail": "listed" if deps_ok else "no Dependencies section (write 'None' if none)"}

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
    risks_ok = bool(matched) or bool(RISKS_RE.search(description))
    checks["risks"] = {"ok": risks_ok, "detail": ("logged: " + ", ".join(str(m) for m in matched)) if matched
                       else ("Risks section in the story" if risks_ok else "no risk logged for this scope and no Risks section")}

    missing = [c for c in CRITERIA if not checks[c]["ok"]]
    return {"result": "pass" if not missing else "fail", "missing": missing,
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
    ap = argparse.ArgumentParser(description="Definition of Ready check for one Story")
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
            print(f"DoR: FAIL (initiative '{args.initiative}' not found under {', '.join(map(str, initiative_roots(home)))})")
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
    return 0 if outcome["result"] == "pass" else 3


if __name__ == "__main__":
    sys.exit(main())
