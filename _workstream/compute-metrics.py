#!/usr/bin/env python3
"""Compute the four BA quality metrics for one initiative from status-data.json.

Formulas are the ones in references/canvas-data-model.md section 4. A metric
that cannot be computed is null ("n/a"), never 0%. Writes metrics-cache.json
next to status-data.json (derived, never canonical) and prints a short table
for /status, /metrics and retros.

  python3 _workstream/compute-metrics.py --initiative payments
  python3 _workstream/compute-metrics.py --status-data path/to/status-data.json --json

Windows: use `py`. Exit 0 computed, 1 status-data.json missing or unreadable.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import statistics
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

THRESHOLDS = {"moscowCoverage": 0.80, "dorHitRate": 0.70, "interrogationRate": 0.95}
INTERROGATED_STATES = {"interrogated", "accepted", "in-flight", "delivered", "evaluated"}


def parse_rule_value(text: str, key: str) -> str | None:
    for line in text.splitlines():
        match = re.match(rf"^\s*{re.escape(key)}\s*[:=]\s*(.+?)\s*$", line.strip())
        if match:
            value = match.group(1).strip().strip("\"'").split(" #", 1)[0].strip()
            if value and value != "TBC" and not value.startswith("["):
                return value
    return None


def initiatives_root(home: Path) -> Path:
    env = os.environ.get("BA_INITIATIVES_ROOT", "").strip()
    if env:
        return Path(os.path.expanduser(env))
    for name in ("ba-assistant-config.mdc", "ba-profile.mdc"):
        path = home / "rules" / name
        if path.exists():
            value = parse_rule_value(path.read_text(encoding="utf-8", errors="replace"), "initiativesRoot")
            if value:
                return Path(os.path.expanduser(value))
    return home / "initiatives"


def as_date(value) -> date | None:
    try:
        return date.fromisoformat(str(value)[:10]) if value else None
    except ValueError:
        return None


def working_days(start: date, end: date) -> int:
    days, cursor = 0, start
    while cursor < end:
        cursor += timedelta(days=1)
        if cursor.weekday() < 5:
            days += 1
    return days


def ratio(part: int, whole: int) -> float | None:
    return round(part / whole, 3) if whole else None


def scope_id(value) -> str:
    return str(value.get("id")) if isinstance(value, dict) else str(value or "initiative")


def compute(sd: dict, today: date) -> dict:
    requirements = sd.get("requirements") or []
    rated = [r for r in requirements if any((c or {}).get("rating") for c in r.get("moscowMatrix") or [])]
    per_scope: dict[str, list[int]] = {}
    for req in requirements:
        for cell in req.get("moscowMatrix") or []:
            counts = per_scope.setdefault(scope_id(cell.get("scope")), [0, 0])
            counts[1] += 1
            counts[0] += 1 if cell.get("rating") else 0

    window = [c for c in sd.get("dorChecks") or [] if (as_date(c.get("checkedAt")) or date.min) >= today - timedelta(days=30)]
    first_pass = [c for c in window if str(c.get("firstAttempt") or c.get("result") or "").lower() == "pass"]

    interrogated = [r for r in requirements if r.get("interrogated") is True or r.get("interrogationArtefact")
                    or str(r.get("lifecycleState") or "").lower() in INTERROGATED_STATES]

    signoffs = sd.get("signOffs") or []
    times = sorted(working_days(as_date(s["requestedDate"]), as_date(s["approvedDate"]))
                   for s in signoffs if as_date(s.get("requestedDate")) and as_date(s.get("approvedDate")))
    open_long = [s.get("id") for s in signoffs
                 if not s.get("approvedDate") and as_date(s.get("requestedDate"))
                 and working_days(as_date(s["requestedDate"]), today) > 7
                 and str(s.get("status") or "pending").lower() not in {"withdrawn", "rejected"}]
    p90 = times[min(len(times) - 1, max(0, round(0.9 * len(times)) - 1))] if times else None

    metrics = {
        "moscowCoverage": {"value": ratio(len(rated), len(requirements)), "rated": len(rated), "total": len(requirements),
                           "perScope": {k: ratio(v[0], v[1]) for k, v in per_scope.items()}},
        "dorHitRate": {"value": ratio(len(first_pass), len(window)), "passedFirstTime": len(first_pass), "checks30d": len(window)},
        "interrogationRate": {"value": ratio(len(interrogated), len(requirements)), "interrogated": len(interrogated),
                              "total": len(requirements)},
        "signOffCycleTime": {"medianWorkingDays": statistics.median(times) if times else None, "p90WorkingDays": p90,
                             "completed": len(times), "openOver7WorkingDays": open_long},
    }
    warnings = []
    for key, limit in THRESHOLDS.items():
        value = metrics[key]["value"]
        if value is not None and value < limit:
            warnings.append(f"{key} {value:.0%} is under {limit:.0%}")
    median = metrics["signOffCycleTime"]["medianWorkingDays"]
    if median is not None and median > 5:
        warnings.append(f"sign-off median {median} working days (over 5)")
    if open_long:
        warnings.append(f"{len(open_long)} sign-off(s) open over 7 working days: {', '.join(str(i) for i in open_long)}")
    return {"computedAt": datetime.now().astimezone().isoformat(timespec="seconds"), "metrics": metrics, "warnings": warnings}


def pct(value) -> str:
    return "n/a" if value is None else f"{value:.0%}"


def main(argv: list[str] | None = None) -> int:
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    parser = argparse.ArgumentParser(description="BA quality metrics from status-data.json")
    where = parser.add_mutually_exclusive_group(required=True)
    where.add_argument("--initiative")
    where.add_argument("--status-data")
    parser.add_argument("--cursor-home", default=str(Path.home() / ".cursor"))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--today", default=None, help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    home = Path(os.path.expanduser(args.cursor_home))
    source = Path(os.path.expanduser(args.status_data)) if args.status_data else initiatives_root(home) / args.initiative / "status-data.json"
    try:
        sd = json.loads(source.read_text(encoding="utf-8-sig"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Metrics: FAIL (cannot read {source}: {exc})")
        return 1
    today = date.fromisoformat(args.today) if args.today else date.today()
    result = compute(sd, today)
    cache = source.parent / "metrics-cache.json"
    previous = {}
    try:
        previous = json.loads(cache.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    # Keep the n/a streak so /status can nudge after 3 runs with a metric missing.
    streak = previous.get("naStreak", {}) if isinstance(previous.get("naStreak"), dict) else {}
    result["naStreak"] = {k: (streak.get(k, 0) + 1 if result["metrics"][k].get("value", result["metrics"][k].get("medianWorkingDays")) is None else 0)
                          for k in result["metrics"]}
    for key in ("learningSurfacings",):
        if key in previous:
            result[key] = previous[key]
    # Trend: compare with the newest run at least 7 days old (history kept in the cache).
    m = result["metrics"]
    point = {"date": today.isoformat(), "moscowCoverage": m["moscowCoverage"]["value"], "dorHitRate": m["dorHitRate"]["value"],
             "interrogationRate": m["interrogationRate"]["value"], "signOffMedian": m["signOffCycleTime"]["medianWorkingDays"]}
    history = [h for h in previous.get("history", []) if isinstance(h, dict) and h.get("date") != point["date"]][-59:] + [point]
    result["history"] = history
    older = [h for h in history if (as_date(h.get("date")) or today) <= today - timedelta(days=7)]
    base = older[-1] if older else None

    def trend(key: str, higher_is_better: bool = True) -> str:
        now, then = point[key], (base or {}).get(key)
        if now is None or then is None:
            return "-"
        if abs(now - then) < 0.01:
            return "→"
        return "↗" if now > then else "↘"
    result["trend"] = {k: trend(k) for k in ("moscowCoverage", "dorHitRate", "interrogationRate", "signOffMedian")}
    cache.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    s = m["signOffCycleTime"]
    t = result["trend"]
    print("| Metric | Value | Trend (7 days) | Basis |")
    print("|---|---|---|---|")
    print(f"| MoSCoW coverage | {pct(m['moscowCoverage']['value'])} | {t['moscowCoverage']} | {m['moscowCoverage']['rated']} of {m['moscowCoverage']['total']} requirements rated |")
    for scope, value in m["moscowCoverage"]["perScope"].items():
        print(f"| MoSCoW coverage ({scope}) | {pct(value)} | - | per-scope cells rated |")
    print(f"| Preflight first-pass rate (30 days, structural only) | {pct(m['dorHitRate']['value'])} | {t['dorHitRate']} | {m['dorHitRate']['passedFirstTime']} of {m['dorHitRate']['checks30d']} passed first time |")
    print(f"| Requirement interrogation rate | {pct(m['interrogationRate']['value'])} | {t['interrogationRate']} | {m['interrogationRate']['interrogated']} of {m['interrogationRate']['total']} challenged |")
    median = "n/a" if s["medianWorkingDays"] is None else f"{s['medianWorkingDays']} working days (p90 {s['p90WorkingDays']})"
    print(f"| Sign-off cycle time | {median} | {t['signOffMedian']} | {s['completed']} completed, {len(s['openOver7WorkingDays'])} open over 7 working days |")
    for warning in result["warnings"]:
        print(f"⚠ {warning}")
    nudges = [k for k, v in result["naStreak"].items() if v >= 3]
    if nudges:
        print(f"n/a for 3+ runs: {', '.join(nudges)} (likely missing data; offer to look)")
    print(f"Metrics cached: {cache}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
