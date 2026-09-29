#!/usr/bin/env python3
"""Render an initiative's 8-tab status canvas and HTML snapshot from status-data.json.

The agent keeps status-data.json current (Jira sync, tracker re-derive: the
judgement work). This script does the rest the same way every time, so /canvas
no longer means reading every project file and hand-writing a large .canvas.tsx:

  - builds one compact data block from status-data.json (scopes, workstream grid,
    stats, timeline, dependency and traceability graphs, RAID with outstanding flags);
  - writes <canvases>/<slug>-status.canvas.tsx from the packaged template
    (skills/ba-assistant/templates/initiative-status.canvas.tsx.template);
  - writes <initiative>/status-snapshot.html (self-contained, same 8 sections);
  - prints what each tab is missing, so the agent can say what to add.

  python3 _workstream/render-initiative-canvas.py --initiative payments
  python3 _workstream/render-initiative-canvas.py --status-data path/to/status-data.json --canvas path/x.canvas.tsx

Windows: use `py`. Exit 0 rendered, 1 status-data.json missing or unreadable.
Optional status-data.json blocks this script reads when present (all optional):
`timeline` {lanes, bars}, `dependencyGraph` {nodes, edges}, `traceability` [rows],
`workstreamChanges` [{date, scope, workstream, change}], `initiative.deadline`.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

WORKSTREAMS = [
    ("intake", "Intake", ("intake", "M0")),
    ("kickoff", "Kickoff", ("kickoff", "M1")),
    ("discovery", "Discovery", ("discovery", "M2")),
    ("slicing", "Slicing & Sequencing", ("featureSlicing", "slicing", "M3")),
    ("solution", "Solution", ("solutionShaping", "solution", "M4")),
    ("delivery", "Delivery", ("delivery", "M5")),
    ("playback", "Playback", ("playback", "verification", "M6")),
    ("eval", "Eval & Retro", ("evalRetro", "evaluation", "retro", "closure", "M7")),
]
CLOSED_WORDS = {"confirmed", "closed", "resolved", "done", "agreed", "approved", "moot", "dropped",
                "booked", "complete", "completed", "mitigated", "cancelled", "reversed", "answered", "validated"}


# ---------- small helpers ----------

def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def as_date(value) -> date | None:
    if not value:
        return None
    text = str(value).strip()
    try:
        return date.fromisoformat(text[:10])
    except ValueError:
        pass
    for fmt in ("%d %b %Y", "%d %B %Y", "%d-%b-%Y", "%d %b", "%d %B"):
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed.date() if "%Y" in fmt else parsed.replace(year=date.today().year).date()
        except ValueError:
            continue
    return None


def short_date(value) -> str:
    d = as_date(value)
    return f"{d.day} {d.strftime('%b')}" if d else (str(value) if value else "")


def scope_id(value) -> str:
    if isinstance(value, dict):
        return str(value.get("id") or "initiative")
    return str(value) if value else "initiative"


def text_of(item: dict, *keys: str) -> str:
    for key in keys:
        if item.get(key):
            return str(item[key])
    return ""


def item_status(value) -> str:
    """One status vocabulary for every visual: done / in-progress / pending / blocked / at-risk / conditional."""
    s = str(value or "").strip().lower().replace("_", "-")
    if s in {"done", "complete", "completed", "approved", "confirmed", "closed", "resolved", "delivered", "mitigated"}:
        return "done"
    if s in {"in-progress", "in progress", "active", "delivering", "in flight", "on-track", "on track", "in review", "requested"}:
        return "in-progress"
    if s in {"blocked", "overdue", "missed", "rejected", "realised", "critical"}:
        return "blocked"
    if s in {"at-risk", "at risk", "monitor"}:
        return "at-risk"
    if s in {"conditional", "tentative", "deferred", "paused"}:
        return "conditional"
    return "pending"


def ws_state(value) -> str:
    s = str(value or "").strip().lower().replace("_", "-").replace(" ", "-")
    if s in {"complete", "completed", "done"}:
        return "complete"
    if s in {"active", "delivering", "in-progress"}:
        return "active"
    if s == "blocked":
        return "blocked"
    if s == "paused":
        return "paused"
    if s in {"na", "n/a", "not-applicable"}:
        return "na"
    return "not-started"


def outstanding(status) -> bool:
    return str(status or "").strip().lower() not in CLOSED_WORDS


def short_label(label: str, limit: int = 18) -> str:
    label = re.sub(r"\s+", " ", label).strip()
    return label if len(label) <= limit else label[: limit - 1].rstrip() + "…"


# ---------- data build ----------

def build_scopes(sd: dict) -> list[dict]:
    scopes = [{"id": "initiative", "label": "Initiative level", "shortLabel": "Initiative", "level": "initiative"}]
    seen = {"initiative"}

    def add(sid, label, level, short=None):
        sid = str(sid)
        if not sid or sid in seen:
            return
        seen.add(sid)
        label = label or sid
        scopes.append({"id": sid, "label": label, "shortLabel": short or short_label(label), "level": level})

    for s in sd.get("scopes", []):
        level = s.get("level") if s.get("level") in {"feature", "cohort", "slice"} else "feature"
        add(s.get("id"), s.get("label"), "cohort" if level == "slice" else level, s.get("shortLabel"))
    for f in sd.get("features", []):
        add(f.get("id"), f.get("name"), "feature", f.get("shortName"))
    for c in sd.get("cohorts", []) + sd.get("slices", []):
        add(c.get("id"), c.get("name"), "cohort", c.get("shortName"))
    order = {"initiative": 0, "feature": 1, "cohort": 2}
    return sorted(scopes, key=lambda s: order[s["level"]])


def build_grid(sd: dict, scopes: list[dict]) -> dict:
    grid = {s["id"]: {w[0]: "not-started" for w in WORKSTREAMS} for s in scopes}
    block = sd.get("workstreams") or {}
    for ws_id, _, aliases in WORKSTREAMS:
        for alias in aliases:
            cells = block.get(alias)
            if isinstance(cells, dict):
                for sid, state in cells.items():
                    grid.setdefault(sid, {w[0]: "not-started" for w in WORKSTREAMS})[ws_id] = ws_state(state)
    # Fallback: per-scope `modes` objects (M0-M7) when there is no workstreams block.
    if not block:
        sources = [("initiative", (sd.get("modes") or {}).get("initiative") or {})]
        sources += [(x.get("id"), x.get("modes") or {}) for x in sd.get("features", []) + sd.get("cohorts", []) + sd.get("slices", [])]
        for sid, modes in sources:
            if not sid or not isinstance(modes, dict):
                continue
            for ws_id, _, aliases in WORKSTREAMS:
                for alias in aliases:
                    if alias in modes:
                        grid.setdefault(sid, {w[0]: "not-started" for w in WORKSTREAMS})[ws_id] = ws_state(modes[alias])
    return grid


def active_workstreams(grid: dict, sid: str) -> list[str]:
    labels = {w[0]: w[1] for w in WORKSTREAMS}
    return [labels[k] for k, v in grid.get(sid, {}).items() if v == "active"]


def build_raid(sd: dict) -> dict:
    tracker = sd.get("tracker") or {}
    raid = sd.get("raid") or {}

    def rows(items, text_keys, owner_keys, status_keys, extra=None):
        out = []
        for i, item in enumerate(items or []):
            if not isinstance(item, dict):
                continue
            status = text_of(item, *status_keys) or "Open"
            row = {
                "id": str(item.get("id") or f"#{i + 1}"),
                "text": text_of(item, *text_keys),
                "owner": text_of(item, *owner_keys),
                "status": status,
                "outstanding": outstanding(status),
                "scope": scope_id(item.get("scope")),
            }
            if extra:
                row.update(extra(item))
            out.append(row)
        return out

    decisions = rows(sd.get("decisions") or tracker.get("decisions"), ("title", "decision"), ("owner", "madeBy"), ("status",),
                     lambda d: {"date": short_date(d.get("date"))})
    risks = rows((raid.get("risks") or []) + (tracker.get("risks") or []), ("title", "risk", "description"), ("owner",), ("status",),
                 lambda r: {"severity": str(r.get("severity") or r.get("impact") or "medium").lower()})
    questions = rows((sd.get("openQuestions") or []) + (tracker.get("unknowns") or []), ("question", "description", "title"),
                     ("owner",), ("status",))
    assumptions = rows((raid.get("assumptions") or []) + (tracker.get("assumptions") or []), ("assumption", "title", "description"),
                       ("owner",), ("status", "validation"), lambda a: {"confidence": text_of(a, "confidence") or "-"})
    actions = rows(tracker.get("actions"), ("description", "action", "title"), ("owner",), ("status",),
                   lambda a: {"due": a.get("due")})
    return {"decisions": decisions, "risks": risks, "questions": questions, "assumptions": assumptions, "actions": actions}


def build_confidence(sd: dict) -> list[dict]:
    names = {"problemClarity": "Problem clarity", "requirementsCompleteness": "Requirements completeness",
             "dependencyAwareness": "Dependency awareness", "complianceReadiness": "Compliance readiness",
             "solutionViability": "Solution viability", "definitionOfReady": "Definition of ready"}
    out = []
    for key, value in (sd.get("confidenceScores") or {}).items():
        if isinstance(value, dict):
            evidence = (value.get("evidence") or {}).get("type") or ""
            out.append({"area": names.get(key, key), "score": str(value.get("current") or "unknown").lower(),
                        "note": {"data": "Grounded in data", "qualitative": "Judgement call"}.get(evidence, "")})
    for item in sd.get("confidence") or []:
        if isinstance(item, dict):
            out.append({"area": item.get("area", ""), "score": str(item.get("score") or "unknown").lower(), "note": item.get("note", "")})
    return out


def build_stories(sd: dict) -> list[dict]:
    out, seen = [], set()
    for s in (sd.get("stories") or []) + (sd.get("tickets") or []):
        key = str(s.get("key") or "")
        if key and key in seen:
            continue
        seen.add(key)
        out.append({
            "key": key, "title": text_of(s, "title", "summary"), "scope": scope_id(s.get("scope")),
            "moscow": str(s.get("moscow") or "").capitalize() or None, "status": item_status(s.get("status")),
            "statusText": str(s.get("status") or "Not started"),
            "requirements": [str(r) for r in (s.get("linkedRequirements") or s.get("linkedRequirementIds") or [])],
            "slice": s.get("linkedSlice"),
            "start": s.get("startedAt") or s.get("startDate"), "end": s.get("doneAt") or s.get("endDate"),
            "dependsOn": [str(d) for d in (s.get("dependsOn") or s.get("blockedBy") or [])],
        })
    return out


def build_moscow(sd: dict) -> dict:
    columns, rows = [], []
    for req in sd.get("requirements") or []:
        cells = {}
        for cell in req.get("moscowMatrix") or []:
            sid = scope_id(cell.get("scope"))
            cells[sid] = str(cell.get("rating") or "")
            if sid not in columns:
                columns.append(sid)
        rows.append({"id": str(req.get("id") or ""), "text": text_of(req, "description", "title"), "cells": cells})
    return {"columns": columns, "rows": rows}


def build_timeline(sd: dict, stories: list[dict], today: date) -> dict:
    explicit = sd.get("timeline") if isinstance(sd.get("timeline"), dict) else {}
    milestones = []
    for m in sd.get("milestones") or []:
        d = as_date(m.get("targetDate") or m.get("actualDate"))
        if d:
            milestones.append({"id": str(m.get("id") or m.get("title")), "label": text_of(m, "title", "name"), "date": d.isoformat(),
                               "status": item_status(m.get("status")), "scope": scope_id(m.get("scope"))})
    known = {m["label"].lower() for m in milestones}
    for c in sd.get("criticalPath") or []:
        d = as_date(c.get("date"))
        if d and str(c.get("milestone", "")).lower() not in known:
            milestones.append({"id": f"cp-{c.get('id')}", "label": str(c.get("milestone") or ""), "date": d.isoformat(),
                               "status": item_status(c.get("status")), "scope": scope_id(c.get("scope"))})
    for m in milestones:
        low = m["label"].lower()
        m["emoji"] = ("⚖️" if any(w in low for w in ("legal", "sign-off", "signoff", "compliance")) else
                      "🚀" if any(w in low for w in ("launch", "go-live", "go live", "release")) else
                      "📧" if any(w in low for w in ("comms", "email", "send")) else
                      "📊" if "report" in low else "📅")

    lanes = list(explicit.get("lanes") or [])
    bars = []
    for b in explicit.get("bars") or []:
        start, end = as_date(b.get("start")), as_date(b.get("end"))
        if start:
            bars.append({"id": str(b.get("id") or b.get("label")), "label": str(b.get("label") or ""), "lane": str(b.get("lane") or "work"),
                         "start": start.isoformat(), "end": (end or start + timedelta(days=7)).isoformat(),
                         "status": item_status(b.get("status")), "scope": scope_id(b.get("scope")), "forecast": bool(b.get("forecast"))})
    if not explicit.get("bars"):
        for so in sd.get("signOffs") or []:
            start = as_date(so.get("requestedDate"))
            if not start:
                continue
            end = as_date(so.get("approvedDate"))
            status = item_status(so.get("status"))
            bars.append({"id": f"so-{so.get('id')}", "label": text_of(so, "artefact", "title"), "lane": "signoffs",
                         "start": start.isoformat(), "end": (end or max(today, start) + timedelta(days=7)).isoformat(),
                         "status": status, "scope": scope_id(so.get("scope")), "forecast": end is None and status != "done"})
        for st in stories:
            start = as_date(st["start"])
            if not start:
                continue
            end = as_date(st["end"])
            label = f"{st['key']} {st['title']}".strip()
            bars.append({"id": f"st-{st['key'] or label}", "label": f"{label} ({short_date(start)})", "lane": "delivery",
                         "start": start.isoformat(), "end": (end or max(today, start) + timedelta(days=7)).isoformat(),
                         "status": st["status"], "scope": st["scope"], "forecast": end is None and st["status"] != "done"})
        used = {b["lane"] for b in bars}
        lanes = [lane for lane in ({"id": "signoffs", "label": "Sign-offs", "scopes": []},
                                   {"id": "delivery", "label": "Delivery", "scopes": []}) if lane["id"] in used]
    for lane in lanes:
        lane.setdefault("scopes", [])
        if not lane["scopes"]:
            lane["scopes"] = sorted({b["scope"] for b in bars if b["lane"] == lane["id"]}) or ["initiative"]

    initiative = sd.get("initiative") or {}
    dates = [as_date(m["date"]) for m in milestones] + [as_date(b["start"]) for b in bars] + [as_date(b["end"]) for b in bars]
    dates = [d for d in dates if d]
    start = as_date(initiative.get("startedAt")) or (min(dates) if dates else today)
    start -= timedelta(days=start.weekday())
    deadline = as_date(initiative.get("deadline")) or (max(as_date(m["date"]) for m in milestones) if milestones else None)
    last = max(dates + [today] + ([deadline] if deadline else []))
    weeks = min(max(4, (last - start).days // 7 + 2), 30)
    return {"start": start.isoformat(), "weeks": weeks, "deadline": deadline.isoformat() if deadline else None,
            "milestones": sorted(milestones, key=lambda m: m["date"]), "lanes": lanes, "bars": bars}


def build_dependencies(sd: dict, stories: list[dict], milestones: list[dict]) -> dict:
    explicit = sd.get("dependencyGraph") if isinstance(sd.get("dependencyGraph"), dict) else None
    if explicit and explicit.get("nodes"):
        nodes = [{"id": str(n.get("id")), "label": str(n.get("label") or n.get("id")), "status": item_status(n.get("status")),
                  "kind": n.get("kind") or "internal", "scope": scope_id(n.get("scope"))} for n in explicit["nodes"]]
        ids = {n["id"] for n in nodes}
        edges = [{"from": str(e.get("from")), "to": str(e.get("to"))} for e in explicit.get("edges") or []
                 if str(e.get("from")) in ids and str(e.get("to")) in ids]
        return {"nodes": nodes, "edges": edges, "final": explicit.get("final")}

    nodes: dict[str, dict] = {}
    edges: list[dict] = []
    by_label: dict[str, str] = {}

    def node(nid, label, status, kind, scope):
        nid = str(nid)
        if nid not in nodes:
            nodes[nid] = {"id": nid, "label": label or nid, "status": status, "kind": kind, "scope": scope}
            by_label[str(label or nid).lower()] = nid
        return nid

    for m in milestones:
        node(m["id"], m["label"], m["status"], "milestone", m["scope"])
    raid, tracker = sd.get("raid") or {}, sd.get("tracker") or {}
    for dep in (raid.get("dependencies") or []) + (tracker.get("dependencies") or []):
        text = text_of(dep, "title", "description", "dependency")
        kind = "external" if any(w in text.lower() for w in ("vendor", "partner", "acquirer", "third", "external")) else "internal"
        nid = node(dep.get("id") or text, text, item_status(dep.get("status")), kind, scope_id(dep.get("scope")))
        target = str(dep.get("blocks") or "").strip()
        if target:
            tid = target if target in nodes else by_label.get(target.lower()) or node(f"t-{target}", target, "pending", "milestone", scope_id(dep.get("scope")))
            edges.append({"from": nid, "to": tid})
    for st in stories:
        if st["dependsOn"]:
            sid = node(st["key"] or st["title"], f"{st['key']} {st['title']}".strip(), st["status"], "story", st["scope"])
            for dep in st["dependsOn"]:
                did = dep if dep in nodes else node(dep, dep, "pending", "story", st["scope"])
                edges.append({"from": did, "to": sid})
    for m in sd.get("milestones") or []:
        link = m.get("linkedSignOff")
        if link:
            so = next((s for s in sd.get("signOffs") or [] if s.get("id") == link), None)
            if so:
                soid = node(link, text_of(so, "artefact"), item_status(so.get("status")), "internal", scope_id(so.get("scope")))
                edges.append({"from": soid, "to": str(m.get("id") or m.get("title"))})
    final = milestones[-1]["id"] if milestones else None
    return {"nodes": list(nodes.values()), "edges": edges, "final": final}


def build_traceability(sd: dict, stories: list[dict]) -> dict:
    initiative = sd.get("initiative") or {}
    nodes: dict[str, dict] = {}
    edges: set[tuple[str, str]] = set()
    rows = []

    def node(nid, label, kind, scope="initiative"):
        nodes.setdefault(nid, {"id": nid, "label": label, "kind": kind, "scope": scope})
        return nid

    drivers = initiative.get("drivers") or [initiative.get("name") or "Initiative"]
    driver_ids = [node(f"drv-{i}", str(d), "driver") for i, d in enumerate(drivers)]
    unrated = {st["key"] for st in stories if not st["moscow"]}
    adrs_by_req: dict[str, list[str]] = {}
    for d in sd.get("decisions") or []:
        for rid in d.get("linkedRequirements") or []:
            if d.get("linkedADR"):
                adrs_by_req.setdefault(str(rid), []).append(str(d["linkedADR"]))
    for req in sd.get("requirements") or []:
        rid = str(req.get("id") or "")
        if not rid:
            continue
        scopes = [scope_id(c.get("scope")) for c in req.get("moscowMatrix") or []]
        rnode = node(f"req-{rid}", f"{rid} {text_of(req, 'description', 'title')}"[:60], "requirement", scopes[0] if scopes else "initiative")
        for did in driver_ids:
            edges.add((did, rnode))
        linked = [st for st in stories if rid in st["requirements"]]
        slices = sorted({str(st["slice"]) for st in linked if st["slice"]})
        for sl in slices:
            edges.add((rnode, node(f"sl-{sl}", sl, "slice")))
        for st in linked:
            snode = node(f"st-{st['key'] or st['title']}", f"{st['key']} {st['title']}"[:60].strip(), "story", st["scope"])
            edges.add((f"sl-{st['slice']}" if st["slice"] else rnode, snode))
        for adr in adrs_by_req.get(rid, []):
            edges.add((rnode, node(f"adr-{adr}", adr, "adr")))
        rows.append({"driver": ", ".join(str(d) for d in drivers), "requirement": f"{rid} {text_of(req, 'description', 'title')}".strip(),
                     "slice": ", ".join(slices) or "-", "stories": ", ".join(st["key"] or st["title"] for st in linked) or "-",
                     "adrs": ", ".join(adrs_by_req.get(rid, [])) or "-", "nodeId": rnode,
                     "warn": any(st["key"] in unrated for st in linked), "scope": nodes[rnode]["scope"]})
    for row in sd.get("traceability") or []:
        if isinstance(row, dict):
            rows.append({"driver": str(row.get("driver") or ""), "requirement": str(row.get("requirement") or row.get("requirementId") or ""),
                         "slice": str(row.get("slice") or "-"), "stories": ", ".join(row.get("stories") or []) or "-",
                         "adrs": ", ".join(row.get("adrs") or []) or "-", "nodeId": None, "warn": False,
                         "scope": scope_id(row.get("scope"))})
    if len(nodes) <= len(driver_ids):
        return {"nodes": [], "edges": [], "rows": rows}
    return {"nodes": list(nodes.values()), "edges": [{"from": a, "to": b} for a, b in sorted(edges)], "rows": rows}


def build_data(sd: dict, today: date, source: Path) -> tuple[dict, list[str]]:
    initiative = sd.get("initiative") or {}
    scopes = build_scopes(sd)
    grid = build_grid(sd, scopes)
    stories = build_stories(sd)
    raid = build_raid(sd)
    timeline = build_timeline(sd, stories, today)
    approval = initiative.get("pmApproval") or {}
    approval_status = str(approval.get("status") or "pending").lower()

    features = []
    for f in sd.get("features") or [{"id": s["id"], "name": s["label"]} for s in scopes if s["level"] == "feature"]:
        fid = str(f.get("id"))
        fstories = [st for st in stories if st["scope"] == fid]
        rated = [st for st in fstories if st["moscow"]]
        features.append({"id": fid, "name": text_of(f, "name", "label") or fid, "status": item_status(f.get("status")),
                         "statusText": str(f.get("status") or "not started"), "owner": f.get("owner") or "",
                         "workstreams": active_workstreams(grid, fid),
                         "cover": f"{round(100 * len(rated) / len(fstories))}%" if fstories else "n/a"})

    blockers = []
    for b in sd.get("blockers") or []:
        target = as_date(b.get("targetDate"))
        blockers.append({"id": str(b.get("id") or ""), "title": text_of(b, "description", "title"), "impact": b.get("impact") or "",
                         "owner": b.get("owner") or "", "target": short_date(target) if target else "",
                         "daysOverdue": (today - target).days if target and target < today else 0, "scope": scope_id(b.get("scope"))})

    deadline = as_date(timeline["deadline"])
    decisions = raid["decisions"]
    stats = {
        "deadline": {"label": "Days to deadline", "value": str((deadline - today).days) if deadline else "n/a",
                     "tone": "danger" if deadline and (deadline - today).days <= 14 else "info"},
        "features": f"{sum(1 for f in features if f['status'] not in {'blocked', 'at-risk'})} / {len(features)}" if features else "n/a",
        "blockers": str(len(blockers)),
        "decisions": f"{sum(1 for d in decisions if not d['outstanding'])} / {len(decisions)}" if decisions else "n/a",
    }

    week_end = today + timedelta(days=7)
    actions_week = sorted(
        [a for a in raid["actions"] if a["outstanding"] and (as_date(a.get("due")) or date.max) <= week_end],
        key=lambda a: as_date(a.get("due")) or date.max)
    for item in sd.get("thisWeek") or []:
        actions_week.append({"id": "", "text": str(item.get("item") or ""), "owner": item.get("owner") or "", "due": None,
                             "status": "At risk" if item.get("atRisk") else "Planned", "outstanding": True,
                             "scope": scope_id(item.get("scope"))})

    critical = [{"id": str(c.get("id") or i + 1), "milestone": str(c.get("milestone") or ""), "date": short_date(c.get("date")),
                 "status": item_status(c.get("status")), "owner": c.get("owner") or "", "scope": scope_id(c.get("scope"))}
                for i, c in enumerate(sd.get("criticalPath") or [])]
    if not critical:
        critical = [{"id": m["id"], "milestone": m["label"], "date": short_date(m["date"]), "status": m["status"], "owner": "",
                     "scope": m["scope"]} for m in timeline["milestones"]]

    data = {
        "generated": datetime.now().astimezone().strftime("%d %b %Y, %H:%M"),
        "today": today.isoformat(),
        "source": str(source),
        "initiative": {"name": initiative.get("name") or source.parent.name, "slug": initiative.get("slug") or source.parent.name,
                       "phase": initiative.get("phase") or initiative.get("stage") or "",
                       "sponsor": initiative.get("sponsor") or "", "pm": initiative.get("productManager") or initiative.get("pm") or "",
                       "techLead": initiative.get("techLead") or "", "ba": initiative.get("businessAnalyst") or initiative.get("ba") or "",
                       "lastUpdated": initiative.get("lastUpdated") or sd.get("computedAt") or ""},
        "approval": {"show": approval_status != "approved", "status": approval_status,
                     "approver": approval.get("approver") or approval.get("pm") or initiative.get("productManager") or "the PM"},
        "narrative": sd.get("narrative") or "",
        "scopes": scopes,
        "workstreams": [{"id": w[0], "label": w[1]} for w in WORKSTREAMS],
        "grid": grid,
        "changes": [{"date": short_date(c.get("date")), "scope": scope_id(c.get("scope")), "workstream": str(c.get("workstream") or ""),
                     "change": str(c.get("change") or "")} for c in sd.get("workstreamChanges") or []],
        "stats": stats,
        "blockers": blockers,
        "confidence": build_confidence(sd),
        "features": features,
        "stories": stories,
        "moscow": build_moscow(sd),
        "timeline": timeline,
        "dependencies": build_dependencies(sd, stories, timeline["milestones"]),
        "traceability": build_traceability(sd, stories),
        "criticalPath": critical,
        "actionsThisWeek": actions_week,
        "raid": raid,
    }

    gaps = []
    checks = [
        ("Overview", data["narrative"], "a 2-4 sentence `narrative`"),
        ("Workstreams", sd.get("workstreams") or sd.get("modes"), "a `workstreams` block (state per scope)"),
        ("Features", features or stories, "`features` or `stories`"),
        ("Timeline", timeline["milestones"] or timeline["bars"], "`milestones` with target dates (or `timeline.bars`)"),
        ("Dependencies", data["dependencies"]["nodes"], "`raid.dependencies` with `blocks`, or `dependencyGraph`"),
        ("Traceability", data["traceability"]["rows"], "`requirements` plus `stories[].linkedRequirements`"),
        ("Critical path", critical, "`criticalPath` or `milestones`"),
        ("RAID", any(raid.values()), "`decisions`, `raid.*` or `tracker.*`"),
    ]
    for tab, present, need in checks:
        if not present:
            gaps.append(f"{tab}: empty (needs {need})")
    return data, gaps


# ---------- HTML snapshot ----------

COLOURS = {"done": "#22c55e", "in-progress": "#3b82f6", "pending": "#9ca3af", "blocked": "#ef4444",
           "at-risk": "#f59e0b", "conditional": "#d1d5db"}
EMOJI = {"done": "🟢", "in-progress": "🔵", "pending": "○", "blocked": "🔴", "at-risk": "🟡", "conditional": "◐"}
LABEL = {"done": "Done", "in-progress": "In progress", "pending": "Not started", "blocked": "Blocked", "at-risk": "At risk",
         "conditional": "Conditional"}
WS_EMOJI = {"complete": "🟢 Done", "active": "🔵 Active", "paused": "⏸ Paused", "blocked": "🔴 Blocked", "not-started": "○ Not started", "na": ""}
WS_CLASS = {"complete": "done", "active": "in-progress", "paused": "blocked", "blocked": "blocked", "not-started": "pending", "na": "na"}
MOSCOW = {"Must": "🔴 Must", "Should": "🟡 Should", "Could": "🔵 Could", "Won't": "⚪ Won't", "Wont": "⚪ Won't"}


def e(value) -> str:
    return html.escape(str(value if value is not None else ""))


def table(headers: list[str], rows: list[list[str]], attrs: list[str] | None = None, empty: str = "Nothing recorded yet.") -> str:
    if not rows:
        return f'<p class="muted">{e(empty)}</p>'
    head = "".join(f"<th>{e(h)}</th>" for h in headers)
    body = "".join(f"<tr {attrs[i] if attrs else ''}>" + "".join(f"<td>{c}</td>" for c in row) + "</tr>" for i, row in enumerate(rows))
    return f'<table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def scope_attr(sid: str, extra: str = "") -> str:
    return f'data-scope="{e(sid)}" {extra}'.strip()


def gantt_svg(tl: dict, today: date) -> str:
    if not tl["milestones"] and not tl["bars"]:
        return '<p class="muted">No milestones or dated work yet. Add `milestones` with target dates to status-data.json.</p>'
    start = as_date(tl["start"])
    col, label_w, header_h, ms_h, row_h = 92, 160, 36, 56, 34

    def x(d):
        return label_w + ((as_date(d) - start).days / 7) * col

    lanes = tl["lanes"]
    lane_rows, packed = {}, {}
    for lane in lanes:
        rows: list[list[dict]] = []
        for bar in sorted((b for b in tl["bars"] if b["lane"] == lane["id"]), key=lambda b: b["start"]):
            for i, row in enumerate(rows):
                if row[-1]["end"] <= bar["start"]:
                    row.append(bar)
                    packed[bar["id"]] = i
                    break
            else:
                rows.append([bar])
                packed[bar["id"]] = len(rows) - 1
        lane_rows[lane["id"]] = max(len(rows), 1)
    width = label_w + tl["weeks"] * col + 20
    lanes_top = header_h + 8 + ms_h + 4
    height = lanes_top + sum(r * row_h + 12 for r in lane_rows.values()) + 20
    parts = [f'<svg viewBox="0 0 {width} {height}" width="{width}" height="{height}" class="gantt" role="img">']
    for w in range(tl["weeks"] + 1):
        d = start + timedelta(days=7 * w)
        gx = label_w + w * col
        parts.append(f'<line x1="{gx}" y1="{header_h}" x2="{gx}" y2="{height - 10}" class="grid"/>')
        if w < tl["weeks"]:
            parts.append(f'<text x="{gx + 4}" y="14" class="hd">{d.day} {d.strftime("%b")}</text><text x="{gx + 4}" y="28" class="wk">wk {w + 1}</text>')
    parts.append(f'<rect x="0" y="{header_h + 8}" width="{width}" height="{ms_h}" class="mslane"/><text x="6" y="{header_h + 26}" class="lane">📅 Milestones</text>')
    for m in tl["milestones"]:
        mx = x(m["date"])
        parts.append(f'<g {scope_attr(m["scope"])}><title>{e(m["label"])} - {e(short_date(m["date"]))}</title>'
                     f'<text x="{mx}" y="{header_h + 26}" text-anchor="middle" font-size="16">{m["emoji"]}</text>'
                     f'<text x="{mx}" y="{header_h + 40}" text-anchor="middle" class="ml">{e(short_label(m["label"], 22))}</text>'
                     f'<text x="{mx}" y="{header_h + 52}" text-anchor="middle" class="wk">{e(short_date(m["date"]))}</text></g>')
    y = lanes_top
    for li, lane in enumerate(lanes):
        h = lane_rows[lane["id"]] * row_h + 12
        if li % 2 == 0:
            parts.append(f'<rect x="0" y="{y}" width="{width}" height="{h}" class="zebra"/>')
        parts.append(f'<text x="6" y="{y + 20}" class="lane">{e(lane["label"])}</text>')
        for bar in (b for b in tl["bars"] if b["lane"] == lane["id"]):
            bx, by = x(bar["start"]) + 2, y + 6 + packed[bar["id"]] * row_h
            bw = max(((as_date(bar["end"]) - as_date(bar["start"])).days / 7) * col - 4, 24)
            dash = ' stroke-dasharray="4 2" stroke="#6b7280"' if bar["forecast"] else ""
            label = f'{EMOJI[bar["status"]]} {bar["label"]}{" (forecast)" if bar["forecast"] else ""}'
            parts.append(f'<g {scope_attr(bar["scope"])}><title>{e(bar["label"])} - {LABEL[bar["status"]]}</title>'
                         f'<rect x="{bx:.1f}" y="{by}" width="{bw:.1f}" height="{row_h - 8}" rx="4" fill="{COLOURS[bar["status"]]}" opacity="0.88"{dash}/>'
                         f'<text x="{bx + 6:.1f}" y="{by + (row_h - 8) / 2 + 4}" class="bar">{e(short_label(label, int(bw / 6.5) or 4))}</text></g>')
        y += h
    tx = x(today.isoformat())
    parts.append(f'<line x1="{tx:.1f}" y1="{header_h}" x2="{tx:.1f}" y2="{height - 10}" stroke="#3b82f6" stroke-width="2" stroke-dasharray="4 4"/>'
                 f'<text x="{tx + 4:.1f}" y="{header_h + 4}" fill="#3b82f6" font-weight="700" font-size="10">Today</text>')
    if tl["deadline"]:
        dx = x(tl["deadline"])
        parts.append(f'<line x1="{dx:.1f}" y1="{header_h}" x2="{dx:.1f}" y2="{height - 10}" stroke="#ef4444" stroke-width="2" stroke-dasharray="6 3"/>'
                     f'<text x="{dx + 4:.1f}" y="{height - 14}" fill="#ef4444" font-weight="700" font-size="10">⛔ {e(short_date(tl["deadline"]))}</text>')
    parts.append("</svg>")
    return f'<div class="scroll">{"".join(parts)}</div>'


def legend() -> str:
    return '<p class="legend">' + " ".join(f'<span><i style="background:{COLOURS[k]}"></i>{EMOJI[k]} {LABEL[k]}</span>'
                                          for k in ("done", "in-progress", "pending", "blocked")) + "</p>"


def raid_card(title: str, rows: list[dict], headers: list[str], cells, open_: bool) -> str:
    total, out = len(rows), sum(1 for r in rows if r["outstanding"])
    body = table(headers + ["ID"], [cells(r) + [f'<small class="muted">{e(r["id"])}</small>'] for r in rows],
                 [scope_attr(r["scope"], f'data-outstanding="{str(r["outstanding"]).lower()}"') for r in rows])
    return f'<details {"open" if open_ else ""}><summary>{title} ({total} total · {out} outstanding)</summary>{body}</details>'


def render_html(data: dict, today: date) -> str:
    ini, stats = data["initiative"], data["stats"]
    scopes = {s["id"]: s for s in data["scopes"]}
    label = lambda sid: e(scopes.get(sid, {}).get("shortLabel", sid))  # noqa: E731
    pills = []
    for level in ("initiative", "feature", "cohort"):
        group = [s for s in data["scopes"] if s["level"] == level]
        if group and pills:
            pills.append('<span class="sep">|</span>')
        for s in group:
            text = f'🏛️ {s["label"]}' if level == "initiative" else s["label"]
            pills.append(f'<button class="pill{" on" if level == "initiative" else ""}" data-pick="{e(s["id"])}" data-short="{e(s["shortLabel"])}">{e(text)}</button>')

    banner = ""
    if data["approval"]["show"]:
        banner = (f'<div class="banner">⚠️ DRAFT - pending approval from {e(data["approval"]["approver"])}. Problem statement, success metrics, '
                  'scope, and RAID are draft v1 outputs. Do not treat as authoritative until PM sign-off is captured.</div>')

    ws_strip = " ".join(f'<span class="pill {WS_CLASS[data["grid"]["initiative"][w["id"]]]}">{(WS_EMOJI[data["grid"]["initiative"][w["id"]]] or "·").split(" ")[0]} {e(w["label"])}</span>'
                        for w in data["workstreams"])
    blockers = "".join(f'<div class="callout danger" {scope_attr(b["scope"])}><h4>🔴 {e(b["title"])}</h4><p>{e(b["impact"])}'
                       f'{" · owner " + e(b["owner"]) if b["owner"] else ""}{" · " + str(b["daysOverdue"]) + "d overdue" if b["daysOverdue"] else ""}</p></div>'
                       for b in data["blockers"][:4]) or '<p class="muted">No active blockers recorded.</p>'
    where = table(["Scope", "In workstream(s)", "Status"],
                  [[e(s["label"]), e(" + ".join(active_workstreams(data["grid"], s["id"])) or "-"),
                    next((f'{EMOJI[f["status"]]} {LABEL[f["status"]]}' for f in data["features"] if f["id"] == s["id"]), "")]
                   for s in data["scopes"]], [scope_attr(s["id"]) for s in data["scopes"]])
    score_emoji = {"high": "🟢 High", "medium": "🟡 Medium", "low": "🔴 Low"}
    confidence = table(["Area", "Score", "Note"], [[e(c["area"]), score_emoji.get(c["score"], "○ " + e(c["score"].title())), e(c["note"])]
                                                   for c in data["confidence"]], empty="No confidence scores yet.")
    overview = (f'<div class="strip">{ws_strip}</div><div class="stats">'
                f'<div class="stat {stats["deadline"]["tone"]}"><b>{e(stats["deadline"]["value"])}</b><span>Days to deadline</span></div>'
                f'<div class="stat"><b>{e(stats["features"])}</b><span>Features on track</span></div>'
                f'<div class="stat"><b>{e(stats["blockers"])}</b><span>Active blockers</span></div>'
                f'<div class="stat"><b>{e(stats["decisions"])}</b><span>Decisions confirmed</span></div></div>'
                f'<div class="callout info"><h4>Where we are right now</h4><p>{e(data["narrative"]) or "No narrative yet."}</p></div>'
                f'<h3>Top blockers</h3><div class="grid2">{blockers}</div><h3>Where each scope is right now</h3>{where}<h3>Confidence</h3>{confidence}')

    head = "".join(f"<th>{e(w['label'])}</th>" for w in data["workstreams"])
    grid_rows = []
    for s in data["scopes"]:
        prefix = "↳ " if s["level"] == "cohort" else ""
        cells = "".join(f'<td class="cell {WS_CLASS[data["grid"].get(s["id"], {}).get(w["id"], "not-started")]}" '
                        f'title="{e(s["label"])} - {e(w["label"])}">{WS_EMOJI[data["grid"].get(s["id"], {}).get(w["id"], "not-started")]}</td>'
                        for w in data["workstreams"])
        grid_rows.append(f'<tr class="lvl-{s["level"]}" {scope_attr(s["id"])}><th>{prefix}{e(s["label"])}</th>{cells}</tr>')
    changes = table(["Date", "Scope", "Workstream", "Change"], [[e(c["date"]), label(c["scope"]), e(c["workstream"]), e(c["change"])]
                                                                 for c in data["changes"]], empty="No workstream changes logged.")
    workstreams = (f'<div class="scroll"><table class="wsgrid"><thead><tr><th>Scope</th>{head}</tr></thead><tbody>{"".join(grid_rows)}</tbody></table></div>'
                   '<p class="legend">🟢 Done · 🔵 Active · ⏸ Paused · 🔴 Blocked · ○ Not started</p>'
                   f'<h3>Recent workstream changes</h3>{changes}')

    features = table(["Feature", "Active workstream(s)", "Owner", "Health", "Priority cover"],
                     [[e(f["name"]), e(" + ".join(f["workstreams"]) or "-"), e(f["owner"]), f'{EMOJI[f["status"]]} {LABEL[f["status"]]}', e(f["cover"])]
                      for f in data["features"]], [scope_attr(f["id"]) for f in data["features"]], "No features defined yet.")
    stories = table(["Title", "Scope", "Priority", "Status", "Key"],
                    [[e(s["title"]), label(s["scope"]), MOSCOW.get(s["moscow"] or "", "⚠ unrated"), f'{EMOJI[s["status"]]} {e(s["statusText"])}', e(s["key"])]
                     for s in data["stories"]], [scope_attr(s["scope"]) for s in data["stories"]], "No stories yet.")
    mc = data["moscow"]
    matrix = table(["Requirement"] + [scopes.get(c, {}).get("shortLabel", c) for c in mc["columns"]],
                   [[e(f'{r["id"]} {r["text"]}')] + [MOSCOW.get(r["cells"].get(c, ""), "⚠ unrated") for c in mc["columns"]] for r in mc["rows"]],
                   empty="No MoSCoW ratings yet.")
    features_tab = f'<h3>Features in flight</h3>{features}<h3>Stories in flight</h3>{stories}<h3>MoSCoW priority matrix</h3>{matrix}'

    timeline_tab = gantt_svg(data["timeline"], today) + legend() + '<p class="muted">Bar length = duration in weeks. Bars auto-pack into sub-rows so they never overlap.</p>'

    dep = data["dependencies"]
    labels = {n["id"]: n for n in dep["nodes"]}
    dep_rows = [[f'{EMOJI[labels[x["from"]]["status"]]} {e(labels[x["from"]]["label"])}', "→",
                 f'{EMOJI[labels[x["to"]]["status"]]} {e(labels[x["to"]]["label"])}', e(labels[x["from"]]["kind"])] for x in dep["edges"]]
    dependencies_tab = (f'<div class="grid2">{blockers}</div><h3>What depends on what</h3>'
                        + table(["From", "", "To", "Kind"], dep_rows, [scope_attr(labels[x["from"]]["scope"]) for x in dep["edges"]],
                                "No dependency links yet. Add `blocks` to dependencies, or a `dependencyGraph` block.") + legend())

    tr = data["traceability"]
    trace_tab = ('<p class="legend">⚖️ Driver · 📋 Requirement · 🍕 Slice · 🎟️ Story · 📌 ADR</p>'
                 + table(["⚖️ Driver", "📋 Requirement", "🍕 Slice", "🎟️ Stories", "📌 ADRs"],
                         [[e(r["driver"]), ("⚠ " if r["warn"] else "") + e(r["requirement"]), e(r["slice"]), e(r["stories"]), e(r["adrs"])] for r in tr["rows"]],
                         [scope_attr(r["scope"]) for r in tr["rows"]], "No requirement-to-story links yet."))

    cp = table(["#", "Milestone", "Date", "Status", "Owner"],
               [[e(c["id"]), e(c["milestone"]), e(c["date"]), f'{EMOJI[c["status"]]} {LABEL[c["status"]]}', e(c["owner"])] for c in data["criticalPath"]],
               [scope_attr(c["scope"]) for c in data["criticalPath"]], "No critical path yet.")
    aw = table(["Action", "Owner", "Due", "Status"],
               [[e(a["text"]), e(a["owner"]), e(short_date(a.get("due"))), e(a["status"])] for a in data["actionsThisWeek"]],
               [scope_attr(a["scope"]) for a in data["actionsThisWeek"]], "No actions due this week.")
    unrated = [s for s in data["stories"] if not s["moscow"]]
    warn = f'<div class="callout warning"><h4>⚠ {len(unrated)} stories have no MoSCoW rating</h4></div>' if unrated else ""
    critical_tab = f'<h3>Critical path to deadline</h3>{cp}<h3>Actions due this week</h3>{aw}{warn}'

    sev = {"critical": "🔴 CRITICAL", "high": "🔴 HIGH", "medium": "🟡 MEDIUM", "low": "🔵 LOW"}
    rd = data["raid"]
    tracker_tab = ('<label class="toggle"><input type="checkbox" id="outstanding" checked> Show outstanding items only</label>'
                   + raid_card("📌 Decisions", rd["decisions"], ["Decision", "Made by", "Status"], lambda r: [e(r["text"]), e(r["owner"]), e(r["status"])], True)
                   + raid_card("🧨 Risks", rd["risks"], ["Risk", "Owner", "Severity"], lambda r: [e(r["text"]), e(r["owner"]), sev.get(r["severity"], e(r["severity"]))], True)
                   + raid_card("❓ Open questions", rd["questions"], ["Question", "Owner", "Status"], lambda r: [e(r["text"]), e(r["owner"]), e(r["status"])], False)
                   + raid_card("⚠️ Assumptions", rd["assumptions"], ["Assumption", "Owner", "Confidence"], lambda r: [e(r["text"]), e(r["owner"]), e(r["confidence"])], False)
                   + raid_card("🎯 Actions", rd["actions"], ["Action", "Owner", "Status"], lambda r: [e(r["text"]), e(r["owner"]), e(r["status"])], True))

    tabs = [("overview", "Overview", overview), ("workstreams", "Workstreams", workstreams), ("features", "Features & Delivery", features_tab),
            ("timeline", "Timeline", timeline_tab), ("dependencies", "Dependencies", dependencies_tab), ("traceability", "Traceability", trace_tab),
            ("critical-path", "Critical Path & Actions", critical_tab), ("tracker", "RAID & Tracker", tracker_tab)]
    active_cls = ' class="active"'
    nav = "".join(f'<button data-tab="{t}"{active_cls if i == 0 else ""}>{e(n)}</button>' for i, (t, n, _) in enumerate(tabs))
    sections = "".join(f'<section id="tab-{t}"{"" if i == 0 else " hidden"}><h2>{e(n)}</h2>{body}</section>' for i, (t, n, body) in enumerate(tabs))
    people = " · ".join(f"{k}: {e(v)}" for k, v in (("Sponsor", ini["sponsor"]), ("PM", ini["pm"]), ("Tech lead", ini["techLead"]), ("BA", ini["ba"])) if v)
    return f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{e(ini["name"])} - Status as at {e(short_date(data["today"]))}</title>
<style>
:root{{--bg:#fff;--text:#1f2937;--muted:#6b7280;--border:#e5e7eb;--card:#f9fafb;--accent:#3b82f6}}
@media (prefers-color-scheme:dark){{:root{{--bg:#111827;--text:#f3f4f6;--muted:#9ca3af;--border:#374151;--card:#1f2937}}}}
body{{margin:0;padding:16px 24px;background:var(--bg);color:var(--text);font:14px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}}
h1{{margin:0 0 4px}} h2{{margin:8px 0 12px}} h3{{margin:20px 0 8px;font-size:15px}}
.muted,small{{color:var(--muted)}} .banner{{position:sticky;top:0;z-index:5;background:#f59e0b;color:#111;padding:10px 12px;border-radius:6px;margin:8px 0;font-weight:600}}
nav{{display:flex;gap:6px;flex-wrap:wrap;margin:12px 0}} nav button,.pill{{border:1px solid var(--border);background:var(--card);color:var(--text);border-radius:999px;padding:4px 12px;cursor:pointer;font:inherit}}
nav button.active,.pill.on{{background:var(--accent);color:#fff;border-color:var(--accent)}} .sep{{color:var(--muted);margin:0 4px}}
.pill.done{{border-color:#22c55e}} .pill.in-progress{{border-color:#3b82f6}} .pill.blocked{{border-color:#ef4444}}
table{{border-collapse:collapse;width:100%;margin:4px 0}} th,td{{border-bottom:1px solid var(--border);padding:6px 8px;text-align:left;vertical-align:top}}
.stats{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:12px 0}} .stat{{background:var(--card);border:1px solid var(--border);border-radius:8px;padding:10px}}
.stat b{{display:block;font-size:22px}} .stat.danger b{{color:#ef4444}} .grid2{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:10px}}
.callout{{border-left:4px solid var(--accent);background:var(--card);padding:8px 12px;border-radius:6px;margin:8px 0}} .callout h4{{margin:0 0 4px}}
.callout.danger{{border-color:#ef4444}} .callout.warning{{border-color:#f59e0b}} .strip{{display:flex;flex-wrap:wrap;gap:6px}}
.wsgrid td.cell{{text-align:center;font-size:12px;white-space:nowrap}} .cell.done{{background:#22c55e33}} .cell.in-progress{{background:#3b82f64d;font-weight:700}}
.cell.blocked{{background:#ef444433}} .cell.pending{{background:#9ca3af1a}} .lvl-cohort th{{padding-left:22px;font-weight:500}} .lvl-cohort:nth-child(even){{background:#9ca3af14}}
.lvl-initiative th,.lvl-feature th{{font-weight:700}} .scroll{{overflow-x:auto}} .legend span{{margin-right:12px}} .legend i{{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:4px;vertical-align:-1px}}
details{{border:1px solid var(--border);border-radius:8px;padding:6px 10px;margin:8px 0}} summary{{cursor:pointer;font-weight:600}}
.gantt text{{fill:var(--text);font-size:10px}} .gantt .hd{{font-weight:700}} .gantt .wk,.gantt .ml{{font-size:9px}} .gantt .wk{{fill:var(--muted)}}
.gantt .grid{{stroke:var(--border);stroke-dasharray:2 4}} .gantt .mslane{{fill:#9ca3af;opacity:.18}} .gantt .zebra{{fill:#9ca3af;opacity:.1}} .gantt .lane{{font-weight:600}} .gantt .bar{{fill:#fff;font-weight:500}}
body.only-outstanding tr[data-outstanding="false"]{{display:none}} .hide-scope{{display:none!important}}
footer{{margin-top:24px;color:var(--muted);font-size:12px}}
</style></head><body class="only-outstanding">
<header><h1>{e(ini["name"])}</h1><div class="muted">{e(ini["phase"])}{" · " if ini["phase"] else ""}Status as at {e(short_date(data["today"]))}{" · " + people if people else ""}</div></header>
{banner}
<div class="scope-nav">Filter scope: {"".join(pills)}<div class="muted" id="scope-desc">Showing the whole initiative (Initiative level) · click a feature or cohort to drill in · click "Initiative level" to reset</div></div>
<nav>{nav}</nav><main>{sections}</main>
<footer>Generated {e(data["generated"])} by render-initiative-canvas.py from {e(data["source"])}. Status data last updated {e(ini["lastUpdated"])}.</footer>
<script>
document.querySelectorAll('nav button').forEach(function(btn){{btn.addEventListener('click',function(){{
  document.querySelectorAll('main > section').forEach(function(s){{s.hidden=true}});
  document.getElementById('tab-'+btn.dataset.tab).hidden=false;
  document.querySelectorAll('nav button').forEach(function(b){{b.classList.remove('active')}});btn.classList.add('active');}})}});
document.getElementById('outstanding').addEventListener('change',function(ev){{document.body.classList.toggle('only-outstanding',ev.target.checked)}});
var picked=['initiative'];
function applyScope(){{
  var all=picked.length===1&&picked[0]==='initiative';
  document.querySelectorAll('.scope-nav .pill').forEach(function(p){{p.classList.toggle('on',picked.indexOf(p.dataset.pick)>=0)}});
  document.querySelectorAll('main [data-scope]').forEach(function(el){{el.classList.toggle('hide-scope',!all&&picked.indexOf(el.dataset.scope)<0)}});
  document.getElementById('scope-desc').textContent=all?'Showing the whole initiative (Initiative level) · click a feature or cohort to drill in · click "Initiative level" to reset':'Showing: '+picked.map(function(id){{var p=document.querySelector('[data-pick="'+id+'"]');return p?p.dataset.short:id}}).join(', ')+' · click "Initiative level" to reset';
}}
document.querySelectorAll('.scope-nav .pill').forEach(function(p){{p.addEventListener('click',function(){{
  var id=p.dataset.pick;
  if(id==='initiative'){{picked=['initiative']}}else{{var was=picked.indexOf(id)>=0;picked=picked.filter(function(s){{return s!=='initiative'&&s!==id}});if(!was)picked.push(id);if(!picked.length)picked=['initiative'];}}
  applyScope();}})}});
</script></body></html>
"""


# ---------- paths and main ----------

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


def default_canvas_path(home: Path, slug: str) -> Path:
    name = f"{Path(slug).name}-status.canvas.tsx"
    existing = sorted((home / "projects").glob(f"*/canvases/{name}"))
    if existing:
        return existing[-1]
    canvases = sorted((home / "projects").glob("*/canvases"))
    if len(canvases) == 1:
        return canvases[0] / name
    return home / "canvases" / name


def template_path(home: Path) -> Path:
    for base in (home / "skills" / "ba-assistant", Path(__file__).resolve().parent.parent / "skills" / "ba-assistant"):
        path = base / "templates" / "initiative-status.canvas.tsx.template"
        if path.exists():
            return path
    raise FileNotFoundError("initiative-status.canvas.tsx.template not found under ~/.cursor/skills/ba-assistant/templates/")


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description="Render the initiative canvas + HTML snapshot from status-data.json")
    where = parser.add_mutually_exclusive_group(required=True)
    where.add_argument("--initiative", help="initiative slug (folder under paths.initiativesRoot)")
    where.add_argument("--status-data", help="explicit path to status-data.json")
    parser.add_argument("--cursor-home", default=str(Path.home() / ".cursor"))
    parser.add_argument("--canvas", help="target .canvas.tsx (default: ~/.cursor/projects/<workspace>/canvases/<slug>-status.canvas.tsx)")
    parser.add_argument("--html", help="target HTML (default: <initiative>/status-snapshot.html)")
    parser.add_argument("--no-html", action="store_true", help="canvas only")
    parser.add_argument("--today", default=None, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    home = Path(os.path.expanduser(args.cursor_home))
    source = Path(os.path.expanduser(args.status_data)) if args.status_data else initiatives_root(home) / args.initiative / "status-data.json"
    if not source.exists():
        print(f"Canvas: FAIL (no status-data.json at {source}). Build it from the tracker first (status-page-and-data.md).")
        return 1
    try:
        sd = read_json(source)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Canvas: FAIL (cannot read {source}: {exc})")
        return 1
    today = date.fromisoformat(args.today) if args.today else date.today()
    data, gaps = build_data(sd, today, source)
    slug = args.initiative or data["initiative"]["slug"]

    canvas = Path(os.path.expanduser(args.canvas)) if args.canvas else default_canvas_path(home, slug)
    body = template_path(home).read_text(encoding="utf-8").replace("/* CANVAS_DATA */", json.dumps(data, indent=1, ensure_ascii=False))
    canvas.parent.mkdir(parents=True, exist_ok=True)
    canvas.write_text(body, encoding="utf-8")
    print(f"Canvas: {canvas}")
    if not args.no_html:
        target = Path(os.path.expanduser(args.html)) if args.html else source.parent / "status-snapshot.html"
        target.write_text(render_html(data, today), encoding="utf-8")
        print(f"HTML snapshot: {target}")
    print(f"Tabs with data: {8 - len(gaps)} / 8")
    for gap in gaps:
        print(f"  - {gap}")
    print("Gate: canvas-render: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
