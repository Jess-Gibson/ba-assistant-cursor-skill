#!/usr/bin/env python3
"""Local drift scan for one initiative: the mechanical half of ba-state-validator.

The agent used to build the fact registry and grep every artefact itself on each
resume. This script does steps 3 to 5 of ba-state-validator/SKILL.md for local
files (fact registry, scan, divergence table) and prints the table. The agent
keeps the judgement: Confluence pages (MCP), deciding what to propagate, asking
the user, and the writes.

Checks (all read-only):
  1. Registers: every D-/R-/OQ-/A-/DEP- item in initiative-tracker.md is in
     status-data.json, with the same status.
  2. Freshness: status-data.json vs the tracker; status-snapshot.html and the
     initiative canvas vs status-data.json.
  3. People: Sponsor / PM / Tech lead / BA names in Project-hub.md and README.md
     vs status-data.json -> initiative.
  4. Milestone dates: lines in Project-hub.md / README.md that name a milestone
     with a different date from status-data.json -> milestones.
  5. Status line: README.md "Status:" vs workboard.json for this initiative.
  6. Unpromoted captures in SESSION-CONTEXT.md (DEC-/REQ-/RISK-/OQ-/ASM-/ACT-/DEP-
     lines without [promoted]).
  7. Jira freshness (reported, not a divergence): oldest ticket `lastJiraSync` in
     status-data.json (ignoring tickets marked jiraMissing), so /status and /canvas
     can skip Jira when it is recent. Printed as "Jira sync (oldest ticket)".

  python3 _workstream/validate-state.py --initiative payments
  python3 _workstream/validate-state.py --initiative payments --json
  python3 _workstream/validate-state.py --all --json

Windows: use `py`. Exit 0 when the scan ran (the last line says ALIGNED or DRIFT),
1 initiative folder not found. --all exits 0 when every initiative scanned, 1 if none found.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date, datetime
from pathlib import Path

REGISTERS = {"D": "decision", "DEC": "decision", "R": "risk", "RISK": "risk", "OQ": "open question",
             "A": "assumption", "ASM": "assumption", "DEP": "dependency", "I": "issue"}
ID_RX = re.compile(r"\b(DEC|RISK|DEP|OQ|ASM|D|R|A|I)-(\d+)\b")
DONE_WORDS = {"confirmed", "closed", "resolved", "done", "agreed", "approved", "answered", "mitigated", "complete", "completed",
              "validated", "dropped", "abandoned", "reversed", "cancelled", "moot"}
MONTHS = {m: i for i, m in enumerate(["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}
DATE_RX = re.compile(r"\b(\d{4}-\d{2}-\d{2}|\d{1,2}[ -](?:jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*(?:[ -]\d{4})?)\b", re.I)


def parse_rule_value(text: str, key: str) -> str | None:
    for line in text.splitlines():
        match = re.match(rf"^\s*{re.escape(key)}\s*[:=]\s*(.+?)\s*$", line.strip())
        if match:
            value = match.group(1).strip()
            if value[:1] in {'"', "'"}:
                end = value.find(value[0], 1)
                value = value[1:end] if end > 0 else value[1:]
            else:
                value = value.split(" #", 1)[0].strip()
            if value and value != "TBC" and not value.startswith("["):
                return value
    return None


def initiatives_root(home: Path) -> Path:
    env = os.environ.get("BA_INITIATIVES_ROOT", "").strip()
    if env and os.path.isdir(os.path.expanduser(env)):   # a stale, missing folder is ignored
        return Path(os.path.expanduser(env))
    for name in ("ba-assistant-config.mdc", "ba-profile.mdc"):
        path = home / "rules" / name
        if path.exists():
            value = parse_rule_value(path.read_text(encoding="utf-8", errors="replace"), "initiativesRoot")
            if value:
                return Path(os.path.expanduser(value))
    return home / "initiatives"


def _skip_depth1(name: str) -> bool:
    return name in {"_archive", "archive", "closed"} or name.startswith(".") or name.startswith("_")


def _read_json(path: Path, default):
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return default


def _live_initiative(folder: Path) -> bool:
    """Match catchup-watch: SESSION-CONTEXT present and initiative.status not closed."""
    if not folder.is_dir() or not (folder / "SESSION-CONTEXT.md").is_file():
        return False
    status = str(
        ((_read_json(folder / "status-data.json", {}) or {}).get("initiative") or {}).get("status", "")
    ).lower()
    return status not in ("closed", "archived", "complete", "completed", "cancelled")


def collect_live_initiatives(root: Path) -> list[Path]:
    """SESSION-CONTEXT.md at depth 1, or depth 2 (short-term\\slug). Same list as catch-up plan."""
    out: list[Path] = []
    if not root.is_dir():
        return out
    for folder in sorted(p for p in root.iterdir() if p.is_dir()):
        if _skip_depth1(folder.name):
            continue
        if _live_initiative(folder):
            out.append(folder.resolve())
        try:
            children = [p for p in folder.iterdir() if p.is_dir()]
        except OSError:
            continue
        for child in sorted(children):
            if _live_initiative(child):
                out.append(child.resolve())
    return out


def resolve_initiative(home: Path, slug: str) -> tuple[Path, str]:
    """Resolve --initiative to a folder.

    Accepts bare <slug> or short-term/<slug>. Checks initiativesRoot/<slug>
    then initiativesRoot/short-term/<slug>. Errors if both exist, or if none match.
    Absolute paths that already exist are accepted as-is.
    """
    raw = (slug or "").strip()
    if not raw:
        raise SystemExit("State validation: FAIL (empty --initiative)")
    expanded = Path(os.path.expanduser(raw))
    if expanded.is_absolute() and expanded.is_dir():
        return expanded.resolve(), expanded.name

    root = initiatives_root(home)
    wanted = raw.replace("\\", "/").strip("/")

    if wanted.startswith("short-term/"):
        leaf = wanted.split("/", 1)[1].strip("/")
        if not leaf or "/" in leaf:
            raise SystemExit(
                f"State validation: FAIL (invalid short-term initiative {wanted!r})"
            )
        candidate = root / "short-term" / leaf
        if candidate.is_dir():
            return candidate.resolve(), leaf
        raise SystemExit(f"State validation: FAIL (no initiative folder at {candidate})")

    primary = root / wanted
    nested = root / "short-term" / wanted
    primary_ok = primary.is_dir()
    nested_ok = nested.is_dir()
    if primary_ok and nested_ok:
        raise SystemExit(
            "State validation: FAIL (ambiguous --initiative "
            f"{wanted!r}: both {primary} and {nested} exist). "
            f"Pass short-term/{wanted} or --root <path>."
        )
    if primary_ok:
        return primary.resolve(), wanted
    if nested_ok:
        return nested.resolve(), wanted
    raise SystemExit(
        f"State validation: FAIL (no initiative folder at {primary} or {nested})"
    )


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def norm_id(prefix: str, number: str) -> str:
    kind = {"DEC": "D", "RISK": "R", "ASM": "A"}.get(prefix, prefix)
    return f"{kind}-{int(number)}"


def status_bucket(value: str) -> str:
    return "closed" if str(value or "").strip().lower() in DONE_WORDS else "open"


def parse_day(text: str, year_hint: int) -> date | None:
    text = text.strip().lower()
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        pass
    match = re.match(r"(\d{1,2})[ -]([a-z]{3})[a-z]*(?:[ -](\d{4}))?", text)
    if match and match.group(2) in MONTHS:
        try:
            return date(int(match.group(3) or year_hint), MONTHS[match.group(2)], int(match.group(1)))
        except ValueError:
            return None
    return None


def fmt_day(d: date | None) -> str:
    return f"{d.day} {d.strftime('%b %Y')}" if d else "?"


def tracker_items(text: str) -> dict[str, dict]:
    """Register items from `### D-04 · Title` blocks (with **Status:**) and from
    table rows whose first cell is an id."""
    items: dict[str, dict] = {}
    lines = text.splitlines()
    for i, line in enumerate(lines):
        heading = re.match(r"^#{2,4}\s+(DEC|RISK|DEP|OQ|ASM|D|R|A|I)-(\d+)\s*[·:\-–]\s*(.+)$", line.strip())
        if heading:
            status = ""
            for follow in lines[i + 1:i + 12]:
                if follow.startswith("#"):
                    break
                found = re.match(r"^\*\*Status:\*\*\s*(.+)$", follow.strip())
                if found:
                    status = found.group(1).strip()
                    break
            key = norm_id(heading.group(1), heading.group(2))
            items[key] = {"id": f"{heading.group(1)}-{heading.group(2)}", "title": heading.group(3).strip(), "status": status, "line": i + 1}
    header: list[str] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped.startswith("|"):
            header = []
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not header:
            header = [c.lower() for c in cells]
            continue
        if all(set(c) <= set("-: ") for c in cells):
            continue
        match = ID_RX.fullmatch(cells[0]) if cells else None
        if match:
            key = norm_id(match.group(1), match.group(2))
            status = cells[header.index("status")] if "status" in header and header.index("status") < len(cells) else ""
            items.setdefault(key, {"id": cells[0], "title": cells[1] if len(cells) > 1 else "", "status": status, "line": i + 1})
    return items


def status_data_items(sd: dict) -> dict[str, dict]:
    raid, tracker = sd.get("raid") or {}, sd.get("tracker") or {}
    groups = [sd.get("decisions"), tracker.get("decisions"), raid.get("risks"), tracker.get("risks"), sd.get("openQuestions"),
              tracker.get("unknowns"), raid.get("assumptions"), tracker.get("assumptions"), raid.get("dependencies"),
              tracker.get("dependencies"), raid.get("issues")]
    items: dict[str, dict] = {}
    for group in groups:
        for item in group or []:
            if not isinstance(item, dict):
                continue
            match = ID_RX.fullmatch(str(item.get("id") or ""))
            if match:
                key = norm_id(match.group(1), match.group(2))
                items.setdefault(key, {"id": key, "status": str(item.get("status") or "")})
    return items


def mtime(path: Path) -> float | None:
    try:
        return path.stat().st_mtime
    except OSError:
        return None


def when(ts: float | None) -> str:
    return datetime.fromtimestamp(ts).strftime("%d %b, %H:%M") if ts else "?"


def parse_stamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        stamp = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    return stamp if stamp.tzinfo else stamp.astimezone()


def sync_sort_key(value: str) -> float:
    stamp = parse_stamp(value)
    return stamp.timestamp() if stamp else 0.0


def age_minutes(value: str | None) -> int | None:
    stamp = parse_stamp(value)
    if not stamp:
        return None
    return max(0, int((datetime.now().astimezone() - stamp).total_seconds() // 60))


def age_text(minutes: int | None) -> str:
    """'never', '25m ago', '3h 10m ago', or '50 days ago' once it is 48 hours or more."""
    if minutes is None:
        return "never"
    if minutes >= 48 * 60:
        return f"{minutes // (24 * 60)} days ago"
    return f"{minutes // 60}h {minutes % 60}m ago" if minutes >= 60 else f"{minutes}m ago"


def find_canvas(home: Path, slug: str) -> Path | None:
    name = f"{Path(slug).name}-status.canvas.tsx"
    found = sorted((home / "projects").glob(f"*/canvases/{name}")) + sorted((home / "canvases").glob(name))
    return found[-1] if found else None


def validate(root: Path, slug: str, home: Path) -> tuple[list[dict], dict]:
    divergences: list[dict] = []
    tracker_path, sd_path = root / "initiative-tracker.md", root / "status-data.json"
    session_path = root / "SESSION-CONTEXT.md"
    downstream = [p for p in (root / "Project-hub.md", root / "README.md") if p.exists()]
    try:
        sd = json.loads(read(sd_path)) if sd_path.exists() else {}
    except json.JSONDecodeError:
        sd = {}
        divergences.append({"fact": "status-data.json", "canonical": "valid JSON", "found_in": "status-data.json",
                            "found": "unreadable", "modified": when(mtime(sd_path)), "action": "Rebuild status-data.json from the tracker"})
    year = date.today().year

    # 1. Registers: tracker is canonical for RAID and decisions.
    tracker_text = read(tracker_path)
    t_items, s_items = tracker_items(tracker_text), status_data_items(sd)
    if tracker_text and sd:
        missing = sorted(set(t_items) - set(s_items), key=lambda k: (k.split("-")[0], int(k.split("-")[1])))
        if missing:
            divergences.append({"fact": f"{len(missing)} tracker item(s) not in status-data.json", "canonical": "initiative-tracker.md",
                                "found_in": "status-data.json", "found": ", ".join(t_items[k]["id"] for k in missing[:12]) + (" ..." if len(missing) > 12 else ""),
                                "modified": when(mtime(sd_path)), "action": "Re-derive status-data.json from the tracker"})
        for key in sorted(set(t_items) & set(s_items)):
            t_status, s_status = t_items[key]["status"], s_items[key]["status"]
            if t_status and s_status and status_bucket(t_status) != status_bucket(s_status):
                divergences.append({"fact": f"{t_items[key]['id']} status ({REGISTERS.get(key.split('-')[0], 'item')})", "canonical": f"{t_status} (tracker)",
                                    "found_in": "status-data.json", "found": s_status, "modified": when(mtime(sd_path)),
                                    "action": "Update status-data.json"})

    # 2. Freshness of derived files.
    t_m, s_m = mtime(tracker_path), mtime(sd_path)
    if t_m and s_m and t_m - s_m > 3600:
        divergences.append({"fact": "status-data.json freshness", "canonical": f"tracker changed {when(t_m)}", "found_in": "status-data.json",
                            "found": f"last written {when(s_m)}", "modified": when(s_m), "action": "Re-derive status-data.json from the tracker"})
    for label, path in (("status-snapshot.html", root / "status-snapshot.html"), ("initiative canvas", find_canvas(home, slug))):
        d_m = mtime(path) if path else None
        if d_m and s_m and s_m - d_m > 60:
            divergences.append({"fact": f"{label} freshness", "canonical": f"status-data.json {when(s_m)}", "found_in": str(path.name),
                                "found": f"rendered {when(d_m)}", "modified": when(d_m), "action": "Run /canvas (render-initiative-canvas.py)"})

    # 3. People names.
    ini = sd.get("initiative") or {}
    people = {"Sponsor": ini.get("sponsor"), "PM": ini.get("productManager") or ini.get("pm"),
              "Product manager": ini.get("productManager") or ini.get("pm"), "Tech lead": ini.get("techLead"),
              "BA": ini.get("businessAnalyst") or ini.get("ba")}
    for doc in downstream:
        for n, line in enumerate(read(doc).splitlines(), 1):
            for role, canonical in people.items():
                if not canonical or str(canonical).startswith("["):
                    continue
                match = re.match(rf"^\s*(?:[-*]\s*)?(?:\*\*)?{re.escape(role)}(?:\*\*)?\s*:?\s*(?:\*\*)?\s*[:|]?\s*(.+?)\s*\|?\s*$", line, re.I)
                if match and match.group(1) and not match.group(1).startswith("|"):
                    found = match.group(1).strip("*| ").strip()
                    if found and found.lower() != str(canonical).lower() and str(canonical).lower() not in found.lower():
                        divergences.append({"fact": f"{role} name", "canonical": f"{canonical} (status-data.json)", "found_in": f"{doc.name}:{n}",
                                            "found": found, "modified": when(mtime(doc)), "action": f"Update {doc.name}"})

    # 4. Milestone dates.
    for m in sd.get("milestones") or []:
        title = str(m.get("title") or "").strip()
        canonical = parse_day(str(m.get("targetDate") or ""), year)
        if len(title) < 6 or not canonical:
            continue
        for doc in downstream:
            for n, line in enumerate(read(doc).splitlines(), 1):
                if title.lower() not in line.lower():
                    continue
                for raw in DATE_RX.findall(line):
                    found = parse_day(raw, canonical.year)
                    if found and found != canonical:
                        divergences.append({"fact": f"{title} date", "canonical": f"{fmt_day(canonical)} (status-data.json)",
                                            "found_in": f"{doc.name}:{n}", "found": fmt_day(found), "modified": when(mtime(doc)),
                                            "action": f"Update {doc.name}"})
                        break

    # 5. README status line vs workboard.json.
    readme = root / "README.md"
    workboard = {}
    try:
        workboard = json.loads(read(home / "_workstream" / "workboard.json") or "{}")
    except json.JSONDecodeError:
        pass
    entry = next((i for i in workboard.get("initiatives", []) if i.get("slug") == slug), None)
    if entry and readme.exists():
        match = re.search(r"^\s*(?:[-*]\s*)?\**Status\**\s*:\**\s*(.+)$", read(readme), re.M | re.I)
        wb_status = str(entry.get("status") or "").lower()
        if match and wb_status:
            found = match.group(1).strip("* ").lower()
            closed_wb, closed_readme = wb_status in {"closed", "archived"}, any(w in found for w in ("closed", "archived"))
            if closed_wb != closed_readme:
                divergences.append({"fact": "Initiative status", "canonical": f"{wb_status} (workboard.json)", "found_in": "README.md",
                                    "found": match.group(1).strip(), "modified": when(mtime(readme)), "action": "Update README.md"})

    # 6. Unpromoted captures.
    unpromoted = [line.strip() for line in read(session_path).splitlines()
                  if re.match(r"^\s*[-*]?\s*(DEC|REQ|RISK|OQ|ASM|ACT|DEP)-", line.strip()) and "[promoted]" not in line]
    # 7. Jira freshness: oldest lastJiraSync across tickets still in Jira.
    # A top-level sync.lastJiraSync counts as the older of itself and that oldest ticket.
    # Tickets with jiraMissing true are ignored (set only on definitive evidence).
    ticket_stamps: list[str | None] = []
    stale_tickets = 0
    for ticket in sd.get("tickets") or []:
        if not isinstance(ticket, dict) or ticket.get("jiraMissing") is True:
            continue
        raw = ticket.get("lastJiraSync")
        stamp = str(raw) if raw else None
        ticket_stamps.append(stamp)
        ticket_age = age_minutes(stamp)
        if ticket_age is None or ticket_age >= 60:
            stale_tickets += 1
    if any(stamp is None for stamp in ticket_stamps):
        oldest_ticket: str | None = None
    elif ticket_stamps:
        oldest_ticket = min((stamp for stamp in ticket_stamps if stamp is not None), key=sync_sort_key)
    else:
        oldest_ticket = None
    sync_block = sd.get("sync") if isinstance(sd.get("sync"), dict) else {}
    block_stamp = str(sync_block["lastJiraSync"]) if sync_block.get("lastJiraSync") else None
    if ticket_stamps and oldest_ticket is None:
        jira_synced = None
    elif ticket_stamps and block_stamp and oldest_ticket is not None:
        jira_synced = min((oldest_ticket, block_stamp), key=sync_sort_key)
    elif ticket_stamps:
        jira_synced = oldest_ticket
    else:
        jira_synced = block_stamp
    summary = {"initiative": slug, "root": str(root), "trackerItems": len(t_items), "statusDataItems": len(s_items),
               "artefactsScanned": [p.name for p in downstream], "unpromoted": unpromoted,
               "statusDataWritten": when(s_m) if s_m else None, "tickets": len(sd.get("tickets") or []),
               "jiraSyncedAt": jira_synced, "jiraSyncAgeMinutes": age_minutes(jira_synced),
               "jiraStaleTickets": stale_tickets}
    return divergences, summary


def _print_text_report(slug: str, summary: dict, divergences: list) -> None:
    stamp = datetime.now().strftime("%d %b %Y, %H:%M")
    print(f"State validation - {slug} - {stamp} (local files; Confluence not checked by this script)")
    print(
        f"Artefacts scanned: tracker ({summary['trackerItems']} items), "
        f"status-data.json ({summary['statusDataItems']} items)"
        + (", " + ", ".join(summary["artefactsScanned"]) if summary["artefactsScanned"] else "")
    )
    if not divergences:
        print("✓ All local artefacts aligned with canonical state. Nothing to propagate.")
    else:
        print(f"Divergences found: {len(divergences)}\n")
        print("| # | Fact | Canonical | Found in | Found value | Last modified | Suggested action |")
        print("|---|---|---|---|---|---|---|")
        for i, d in enumerate(divergences, 1):
            print(
                f"| {i} | {d['fact']} | {d['canonical']} | {d['found_in']} | "
                f"{d['found']} | {d['modified']} | {d['action']} |"
            )
    age = summary["jiraSyncAgeMinutes"]
    if summary["tickets"]:
        stale = summary["jiraStaleTickets"]
        stale_note = f", {stale} over an hour old" if stale else ""
        print(
            f"\nJira sync (oldest ticket): {age_text(age)} "
            f"({summary['tickets']} tickets in status-data.json{stale_note})"
        )
    if summary["unpromoted"]:
        print(
            f"\nUnpromoted captures in SESSION-CONTEXT.md: "
            f"{len(summary['unpromoted'])} (promote at /wrap or end of day)"
        )
    print(f"Gate: state-validation: {'DRIFT (' + str(len(divergences)) + ')' if divergences else 'ALIGNED'}")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description="Local drift scan for one initiative (read-only)")
    where = parser.add_mutually_exclusive_group(required=True)
    where.add_argument("--initiative", help="initiative slug (bare or short-term/<slug>)")
    where.add_argument("--root", help="explicit initiative folder")
    where.add_argument(
        "--all",
        action="store_true",
        help="scan every live initiative (same list as catch-up plan)",
    )
    parser.add_argument("--cursor-home", default=str(Path.home() / ".cursor"))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    home = Path(os.path.expanduser(args.cursor_home))

    if args.all:
        folders = collect_live_initiatives(initiatives_root(home))
        if not folders:
            print("State validation: FAIL (no live initiatives found)")
            return 1
        results = []
        root_base = initiatives_root(home).resolve()
        for folder in folders:
            try:
                rel = folder.resolve().relative_to(root_base).as_posix()
            except ValueError:
                rel = folder.name
            slug = folder.name
            divergences, summary = validate(folder, slug, home)
            summary = dict(summary)
            summary["initiativeKey"] = rel
            results.append({"summary": summary, "divergences": divergences})
            if not args.json:
                _print_text_report(rel, summary, divergences)
                print()
        if args.json:
            print(json.dumps({"initiatives": results, "count": len(results)}, indent=2, ensure_ascii=False))
        else:
            print(f"Gate: state-validation-all: {len(results)} initiatives scanned")
        return 0

    if args.root:
        root = Path(os.path.expanduser(args.root))
        slug = root.name
        if not root.is_dir():
            print(f"State validation: FAIL (no initiative folder at {root})")
            return 1
    else:
        try:
            root, slug = resolve_initiative(home, args.initiative)
        except SystemExit as exc:
            print(exc)
            return 1

    divergences, summary = validate(root, slug, home)
    if args.json:
        print(json.dumps({"summary": summary, "divergences": divergences}, indent=2, ensure_ascii=False))
        return 0
    _print_text_report(slug, summary, divergences)
    return 0


if __name__ == "__main__":
    sys.exit(main())
