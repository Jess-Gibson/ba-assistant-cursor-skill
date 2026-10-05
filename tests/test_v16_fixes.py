"""Regression checks for Version 16 fix-pack items (Stage B3).

Standalone, no pytest. Throwaway HOME only. No network. No real initiative data.

Run:
    python3 tests/test_v16_fixes.py      (Windows: py tests/test_v16_fixes.py)
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable or "python3"
FAILURES: list[str] = []
ENV = {k: v for k, v in os.environ.items() if k != "BA_INITIATIVES_ROOT"}


def check(name: str, ok: bool, detail: str = "") -> None:
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {detail}" if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def run(script: Path, *args, home: Path | None = None, stdin: str | None = None):
    env = dict(ENV)
    if home is not None:
        env["USERPROFILE"] = str(home)
        env["HOME"] = str(home)
    p = subprocess.run(
        [PY, str(script), *[str(a) for a in args]],
        capture_output=True,
        text=True,
        encoding="utf-8",
        input=stdin,
        timeout=60,
        env=env,
    )
    return p.returncode, (p.stdout or "") + (p.stderr or "")


def make_home(tmp: Path) -> Path:
    home = tmp / ".cursor"
    ws = home / "_workstream"
    ws.mkdir(parents=True)
    for name in ("validate-state.py", "ba-actions.py", "regenerate-ba-actions-md.py", "capture.py"):
        shutil.copy(REPO / "_workstream" / name, ws / name)
    shutil.copy(REPO / "tools" / "catchup-watch.py", ws / "catchup-watch.py")
    shutil.copy(REPO / "tools" / "render-initiative-canvas.py", ws / "render-initiative-canvas.py")
    shutil.copytree(REPO / "hooks", home / "hooks")
    (home / "rules").mkdir()
    (home / "rules" / "ba-assistant-config.mdc").write_text(
        'name: "Test BA"\n'
        f'initiativesRoot: "{(tmp / "initiatives").as_posix()}"\n'
        "catchupEveryMinutes: 180\n"
        'catchupHours: "09:00-17:00"\n',
        encoding="utf-8",
    )
    (tmp / "initiatives").mkdir()
    (ws / "ba-actions.json").write_text(
        json.dumps({"schema_version": 1, "next_id": 1, "actions": [], "watching": []}),
        encoding="utf-8",
    )
    (ws / "workboard.json").write_text(json.dumps({"initiatives": []}), encoding="utf-8")
    return home


def write_initiative(root: Path, rel: str, *, status: str = "active") -> Path:
    folder = root / rel
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "SESSION-CONTEXT.md").write_text("# Session\n", encoding="utf-8")
    (folder / "initiative-tracker.md").write_text("# Tracker\n", encoding="utf-8")
    (folder / "status-data.json").write_text(
        json.dumps(
            {
                "initiative": {"name": folder.name, "status": status, "slug": folder.name},
                "tickets": [],
                "registers": {},
                "sync": {},
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    return folder


def test_f02_catchup_hours():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        home = make_home(tmp)
        cfg = home / "rules" / "ba-assistant-config.mdc"
        due = home / "_workstream" / "catchup-watch.py"
        for bad in ("00:00-24:00", "22:00-06:00", "banana"):
            text = cfg.read_text(encoding="utf-8")
            text = re.sub(r'^catchupHours:.*$', f'catchupHours: "{bad}"', text, flags=re.M)
            cfg.write_text(text, encoding="utf-8")
            rc, out = run(due, "due", home=tmp)
            data = json.loads(out)
            check(f"[F02] bad catchupHours {bad!r} does not crash", rc == 0 and "warning" in data, out[:300])
        text = cfg.read_text(encoding="utf-8")
        text = re.sub(r'^catchupHours:.*$', 'catchupHours: "09:00-17:00"', text, flags=re.M)
        cfg.write_text(text, encoding="utf-8")
        rc, out = run(due, "due", home=tmp)
        data = json.loads(out)
        check("[F02] good catchupHours has no warning", rc == 0 and "warning" not in data, out[:300])


def test_f03_banner():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        home = make_home(tmp)
        rc, out = run(home / "hooks" / "session-init.py", home=tmp, stdin="{}")
        check("[F03] session-init exits 0", rc == 0, out[:300])
        try:
            ctx = json.loads(out).get("additional_context", "")
        except json.JSONDecodeError:
            ctx = out
        check("[F03] banner has Otherwise ignore this block", "Otherwise ignore this" in ctx)
        check("[F03] banner drops whatever the ask", "whatever the ask" not in ctx)
        check("[F03] banner points at execution-router section 5",
              "execution-router.mdc section 5" in ctx, ctx[:400])


def test_f02_session_init_bad_catchup_hours():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        home = make_home(tmp)
        cfg = home / "rules" / "ba-assistant-config.mdc"
        text = cfg.read_text(encoding="utf-8")
        text = re.sub(r'^catchupHours:.*$', 'catchupHours: "00:00-24:00"', text, flags=re.M)
        cfg.write_text(text, encoding="utf-8")
        rc, out = run(home / "hooks" / "session-init.py", home=tmp, stdin="{}")
        check("[F02] session-init exits 0 on catchupHours 00:00-24:00", rc == 0, out[:300])
        try:
            ctx = json.loads(out).get("additional_context", "")
        except json.JSONDecodeError:
            ctx = out
        check("[F02] session-init notes bad catchupHours", "not understood" in ctx, ctx[:500])


def test_f09_oldest_jira():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        home = make_home(tmp)
        root = tmp / "initiatives"
        folder = write_initiative(root, "payment-retry")
        old = (datetime.now(timezone.utc) - timedelta(days=2)).isoformat()
        fresh = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
        missing_old = (datetime.now(timezone.utc) - timedelta(days=5)).isoformat()
        sd = {
            "initiative": {"name": "Payment Retry", "status": "active"},
            "tickets": [
                {"key": "PROJ-1001", "lastJiraSync": fresh},
                {"key": "PROJ-1002", "lastJiraSync": old},
                {"key": "PROJ-1003", "lastJiraSync": missing_old, "jiraMissing": True},
            ],
            "sync": {"lastJiraSync": fresh},
            "registers": {},
        }
        (folder / "status-data.json").write_text(json.dumps(sd, indent=2), encoding="utf-8")
        rc, out = run(home / "_workstream" / "validate-state.py", "--initiative", "payment-retry", "--json", home=tmp)
        check("[F09] validate-state exits 0", rc == 0, out[:400])
        data = json.loads(out)
        summary = data.get("summary") or data
        age = summary.get("jiraSyncAgeMinutes")
        stale = summary.get("jiraStaleTickets")
        check("[F09] oldest stamp wins (about 2 days)", isinstance(age, int) and age >= 24 * 60, str(summary))
        check("[F09] jiraMissing ignored in stale count", stale == 1, str(summary))


def test_8b_short_term():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        home = make_home(tmp)
        root = tmp / "initiatives"
        write_initiative(root, "payment-retry")
        write_initiative(root, "short-term/ops-sync")
        write_initiative(root, "short-term/card-scheme")
        vs = home / "_workstream" / "validate-state.py"
        rc, out = run(vs, "--initiative", "ops-sync", "--json", home=tmp)
        check("[8b] bare short-term slug resolves in validate-state", rc == 0, out[:400])
        rc, out = run(vs, "--initiative", "not-a-real-initiative", home=tmp)
        check("[8b] fake slug fails validate-state", rc != 0 and "FAIL" in out, out[:400])
        rc, out = run(vs, "--all", "--json", home=tmp)
        check("[8b] --all exits 0", rc == 0, out[:400])
        data = json.loads(out)
        count = data.get("count") or len(data.get("initiatives") or [])
        check("[8b] --all covers every live initiative in fixture", count == 3, str(data)[:400])
        rc, out = run(
            home / "_workstream" / "render-initiative-canvas.py",
            "--initiative",
            "ops-sync",
            home=tmp,
        )
        # Canvas may fail later without a full template install; resolution must succeed first.
        resolve_failed = "no initiative folder" in out.lower() or "State validation: FAIL" in out
        check(
            "[8b] bare short-term slug resolves in render-initiative-canvas",
            not resolve_failed,
            out[:500],
        )


def test_status_template_panels():
    path = REPO / "skills" / "ba-assistant" / "references" / "status-page-template.adf.json"
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    allowed = {"info", "note", "success", "warning", "error", "{{SUMMARY_PANEL_TYPE}}", "SUMMARY"}
    found = set()

    def walk(node):
        if isinstance(node, dict):
            attrs = node.get("attrs") or {}
            if "panelType" in attrs:
                found.add(str(attrs["panelType"]))
            for v in node.values():
                walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(data)
    bad = [p for p in found if p not in allowed and "SUMMARY" not in p]
    check("[status] ADF template has no plain panelType", "plain" not in found, str(found))
    check("[status] every panelType is allowed", not bad, f"found={found} bad={bad}")


def test_f01_no_bare_py():
    hits = []
    for folder in ("commands", "rules", "skills"):
        root = REPO / folder
        if not root.exists():
            continue
        for path in root.rglob("*"):
            if not path.is_file() or path.suffix not in {".md", ".mdc", ".py", ".tsx", ".template"}:
                continue
            for i, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
                if "`py " in line and "python3" not in line and "Windows:" not in line:
                    hits.append(f"{path.relative_to(REPO)}:{i}")
    check("[F01] no bare `py` without python3", not hits, "; ".join(hits[:10]))


def test_f18_archived_filter():
    text = (REPO / "skills" / "ba-assistant" / "templates" / "ba-workboard.canvas.tsx.template").read_text(
        encoding="utf-8"
    )
    check(
        "[F18] workboard template filters archived from active",
        'status !== "archived"' in text or "status !== 'archived'" in text,
    )


def _load_catchup():
    import importlib.util

    path = REPO / "tools" / "catchup-watch.py"
    spec = importlib.util.spec_from_file_location("ba_catchup_watch", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_f05_register_by_header():
    catchup = _load_catchup()
    with tempfile.TemporaryDirectory() as td:
        folder = Path(td) / "payments-retry"
        folder.mkdir()
        shutil.copy(REPO / "tests" / "fixtures" / "register-unified.md", folder / "requirements-register.md")
        watch = catchup.register_watch(folder)
        ids = [w["id"] for w in watch]
        statuses = {w["id"]: w["status"] for w in watch}
        check("[F05] register status read by header: only proposed open", ids == ["HLR-02", "HLR-01.2"], str(watch))
        check(
            "[F05] register status values are proposed",
            statuses.get("HLR-02") == "proposed" and statuses.get("HLR-01.2") == "proposed",
            str(statuses),
        )


def test_f06_short_term_in_plan():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        home = make_home(tmp)
        root = tmp / "initiatives"
        write_initiative(root, "payments-retry")
        write_initiative(root, "short-term/quick-fix")
        arch = root / "_archive" / "old"
        arch.mkdir(parents=True)
        (arch / "SESSION-CONTEXT.md").write_text("# old\n", encoding="utf-8")
        (arch / "status-data.json").write_text(
            json.dumps({"initiative": {"name": "old", "status": "active"}}), encoding="utf-8"
        )
        rc, out = run(home / "_workstream" / "catchup-watch.py", "plan", home=tmp)
        check("[F06] plan exits 0", rc == 0, out[:400])
        data = json.loads(out)
        slugs = [i.get("slug") for i in data.get("initiatives") or []]
        check("[F06] plan lists top-level and short-term", "payments-retry" in slugs and "quick-fix" in slugs, str(slugs))
        check("[F06] plan skips _archive", "old" not in slugs, str(slugs))


def _load_session_init():
    import importlib.util

    path = REPO / "hooks" / "session-init.py"
    spec = importlib.util.spec_from_file_location("ba_session_init_f16", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_f16_transcript_detection():
    si = _load_session_init()
    check("[F16] trailing (N) stripped from meeting title",
          si.normalize_meeting_title("Weekly sync (2)") == "weekly sync")
    subjects = {"weekly sync"}
    teams = Path("Weekly sync (2).docx")
    check("[F16] Teams .docx matched to meeting subject is a transcript",
          si.is_transcript_file(teams, subjects) is True)
    check("[F16] random .txt is not a transcript",
          si.is_transcript_file(Path("shopping-list.txt"), subjects) is False)
    check("[F16] .vtt is always a transcript",
          si.is_transcript_file(Path("caption.vtt"), set()) is True)
    # Integration: scan_downloads puts Teams docx + vtt in transcripts, random txt in other
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        dl = tmp / "Downloads"
        dl.mkdir()
        (dl / "Weekly sync (2).docx").write_bytes(b"x")
        (dl / "shopping-list.txt").write_text("milk", encoding="utf-8")
        (dl / "caption.vtt").write_text("WEBVTT\n", encoding="utf-8")
        transcripts, other = si.scan_downloads(
            [str(dl)], since_mtime=0.0, transcript_since=0.0, processed=set(), calendar_subjects=subjects,
        )
        tnames = {t["name"] for t in transcripts}
        onames = {t["name"] for t in other}
        check("[F16] Teams docx goes to transcripts list", "Weekly sync (2).docx" in tnames, str(tnames))
        check("[F16] .vtt goes to transcripts list", "caption.vtt" in tnames, str(tnames))
        check("[F16] random .txt goes to other downloads", "shopping-list.txt" in onames, str(onames))


def _load_workboard_gen():
    import importlib.util

    path = REPO / "tools" / "generate-workboard-canvas.py"
    spec = importlib.util.spec_from_file_location("ba_wb_gen_f19", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_f19_calendar_window():
    gen = _load_workboard_gen()
    # Synthetic: working 09:00-17:00 drives view; lunch 12:00-13:00 skipped in free blocks.
    config = {
        "catchup_start": 10 * 60,
        "catchup_end": 18 * 60,
        "view_start": 9 * 60,
        "view_end": 17 * 60,
        "work_start": 9 * 60,
        "work_end": 17 * 60,
        "lunch_start": 12 * 60,
        "lunch_end": 13 * 60,
    }
    meetings = [
        {"subject": "Early sync", "start": "07:00", "end": "07:30"},
        {"subject": "Stand-up", "start": "09:00", "end": "09:15"},
        {"subject": "Late call", "start": "21:30", "end": "22:30"},
    ]
    cal = gen.build_calendar(meetings, config)
    check("[F19] calendarStart is 07:00 (420) after early meeting widen",
          cal["calendarStart"] == 420, str(cal["calendarStart"]))
    check("[F19] calendarEnd is 22:00 (1320) day cap",
          cal["calendarEnd"] == 1320, str(cal["calendarEnd"]))
    titles = {b["title"]: b for b in cal["calendarBlocks"]}
    check("[F19] Stand-up and Early sync drawn",
          "Stand-up" in titles and "Early sync" in titles, str(list(titles)))
    late = titles.get("Late call") or {}
    check("[F19] late meeting clipped to 21:30-22:00 with continuesAfter",
          late.get("start") == 1290 and late.get("end") == 1320 and late.get("continuesAfter") is True,
          str(late))
    free_starts = [b["start"] for b in cal["freeBlocks"]]
    free_spans = [(b["start"], b["end"]) for b in cal["freeBlocks"]]
    # Stand-up occupies 09:00-09:15, so the first free block starts at 09:15.
    check("[F19] free blocks skip lunch (starts 09:15 and 13:00)",
          free_starts == [555, 780], str(free_starts))
    check("[F19] free block spans stay inside working hours",
          free_spans == [(555, 720), (780, 1020)], str(free_spans))

    # Fallback levels with no meetings: workingHours → catchupHours → 08:30-17:30.
    empty = []
    working_only = {
        "catchup_start": 10 * 60, "catchup_end": 18 * 60,
        "view_start": 9 * 60, "view_end": 17 * 60,
        "work_start": 9 * 60, "work_end": 17 * 60,
        "lunch_start": None, "lunch_end": None,
    }
    cal_w = gen.build_calendar(empty, working_only)
    # 09:00-17:00 +/-30 -> 08:30-17:30 -> hour-round 08:00-18:00
    check("[F19] workingHours view is 08:00-18:00 after +/-30 and hour round",
          cal_w["calendarStart"] == 8 * 60 and cal_w["calendarEnd"] == 18 * 60,
          f"{cal_w['calendarStart']}-{cal_w['calendarEnd']}")

    catchup_only = {
        "catchup_start": 10 * 60, "catchup_end": 18 * 60,
        "view_start": 10 * 60, "view_end": 18 * 60,
        "work_start": 10 * 60, "work_end": 18 * 60,
        "lunch_start": None, "lunch_end": None,
    }
    cal_c = gen.build_calendar(empty, catchup_only)
    # 10:00-18:00 +/-30 -> 09:30-18:30 -> hour-round 09:00-19:00
    check("[F19] catchupHours fallback view is 09:00-19:00 after +/-30 and hour round",
          cal_c["calendarStart"] == 9 * 60 and cal_c["calendarEnd"] == 19 * 60,
          f"{cal_c['calendarStart']}-{cal_c['calendarEnd']}")

    default_only = {
        "catchup_start": 8 * 60 + 30, "catchup_end": 17 * 60 + 30,
        "view_start": 8 * 60 + 30, "view_end": 17 * 60 + 30,
        "work_start": 8 * 60 + 30, "work_end": 17 * 60 + 30,
        "lunch_start": None, "lunch_end": None,
    }
    cal_d = gen.build_calendar(empty, default_only)
    check("[F19] default 08:30-17:30 view is 08:00-18:00 after +/-30 and hour round",
          cal_d["calendarStart"] == 8 * 60 and cal_d["calendarEnd"] == 18 * 60,
          f"{cal_d['calendarStart']}-{cal_d['calendarEnd']}")


def test_calendar_feed_bom():
    """get-calendar.ps1 writes UTF-8 with BOM; readers must use utf-8-sig."""
    si = _load_session_init()
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        home = make_home(tmp)
        feed = home / "_workstream" / "calendar-feed.json"
        today = datetime.now().astimezone().replace(hour=10, minute=0, second=0, microsecond=0)
        payload = {
            "meetings": [
                {
                    "subject": "Stand-up",
                    "start": today.isoformat(),
                    "end": (today + timedelta(minutes=15)).isoformat(),
                }
            ],
            "meeting_count": 1,
        }
        feed.write_bytes(b"\xef\xbb\xbf" + json.dumps(payload).encode("utf-8"))
        old_up = os.environ.get("USERPROFILE")
        old_home = os.environ.get("HOME")
        try:
            os.environ["USERPROFILE"] = str(tmp)
            os.environ["HOME"] = str(tmp)
            block = si.calendar_block()
            subjects = si.calendar_meeting_subjects()
        finally:
            if old_up is None:
                os.environ.pop("USERPROFILE", None)
            else:
                os.environ["USERPROFILE"] = old_up
            if old_home is None:
                os.environ.pop("HOME", None)
            else:
                os.environ["HOME"] = old_home
        check("[BOM] calendar_block reads BOM feed", "CALENDAR:" in block and "1 meeting" in block, block)
        check("[BOM] calendar_meeting_subjects reads BOM feed", "stand-up" in subjects, str(subjects))


def test_f04_tracker_table_columns():
    text = (REPO / "skills" / "ba-assistant" / "templates" / "initiative-tracker.md.template").read_text(
        encoding="utf-8"
    )
    lines = text.splitlines()
    mismatches = []
    i = 0
    while i < len(lines) - 1:
        header = lines[i]
        sep = lines[i + 1]
        if header.startswith("|") and sep.startswith("|") and re.fullmatch(r"\|?(?:\s*:?-{3,}:?\s*\|)+", sep):
            h_cols = [c for c in header.strip().strip("|").split("|")]
            s_cols = [c for c in sep.strip().strip("|").split("|")]
            if len(h_cols) != len(s_cols):
                mismatches.append((i + 1, len(h_cols), len(s_cols), header.strip()))
            i += 2
            continue
        i += 1
    check("[F04] every tracker template table has matching header/separator columns",
          not mismatches, str(mismatches))


def test_f16_merge_upgrade_copies_ps1():
    import importlib.util

    path = REPO / "tools" / "ba-merge-upgrade.py"
    spec = importlib.util.spec_from_file_location("ba_merge_upgrade_f16", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    layout = mod.package_layout(REPO)
    mapping = mod.package_map(REPO, layout)
    check("[F16] package_map includes hooks/get-calendar.ps1",
          "hooks/get-calendar.ps1" in mapping, str(sorted(k for k in mapping if k.startswith("hooks/"))))


def test_f21_mail_deny_before_server():
    gate = REPO / "hooks" / "external-write-gate.py"
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        home = tmp / ".cursor"
        (home / "hooks").mkdir(parents=True)
        (home / "_workstream").mkdir(parents=True)
        shutil.copy(gate, home / "hooks" / "external-write-gate.py")
        cases = [
            ('{"tool_name":"send_email","mcp_server_name":"slack","tool_input":{}}', "deny"),
            ('{"tool_name":"send_email","mcp_server_name":"teams","tool_input":{}}', "deny"),
            ('{"tool_name":"sendNotification","mcp_server_name":"ms365-teams","tool_input":{"to":"a@example.com"}}', "deny"),
            ('{"tool_name":"send_message","mcp_server_name":"slack","tool_input":{}}', "ask"),
        ]
        for payload, expected in cases:
            p = subprocess.run(
                [PY, str(home / "hooks" / "external-write-gate.py")],
                input=payload,
                capture_output=True,
                text=True,
                encoding="utf-8",
                env={**ENV, "USERPROFILE": str(tmp), "HOME": str(tmp)},
                timeout=30,
            )
            out = json.loads(p.stdout.strip().splitlines()[-1])
            check(f"[F21] {payload[:40]}... -> {expected}", out.get("permission") == expected, str(out))


def main() -> int:
    test_f02_catchup_hours()
    test_f02_session_init_bad_catchup_hours()
    test_f03_banner()
    test_f09_oldest_jira()
    test_8b_short_term()
    test_status_template_panels()
    test_f01_no_bare_py()
    test_f18_archived_filter()
    test_f05_register_by_header()
    test_f06_short_term_in_plan()
    test_f16_transcript_detection()
    test_f19_calendar_window()
    test_calendar_feed_bom()
    test_f04_tracker_table_columns()
    test_f16_merge_upgrade_copies_ps1()
    test_f21_mail_deny_before_server()
    print()
    if FAILURES:
        print(f"{len(FAILURES)} v16 fix checks failed")
        return 1
    print("All v16 fix checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
