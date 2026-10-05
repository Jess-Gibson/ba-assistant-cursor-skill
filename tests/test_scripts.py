"""
Tests for the _workstream helper scripts added in Version 15:
scan-outlook-mail.py, generate-initiative-snapshots.py, and the config-driven
highlights in roll-calendar-eod.py.

Outlook itself is never touched: the mail triage logic is exercised with fake
mail objects, and the "unable to check" exit path is checked on any OS that is
not Windows (or has no Outlook).

Standalone, no pytest. Every case runs in a throwaway folder.

Run:
    python3 tests/test_scripts.py      (Windows: py tests/test_scripts.py)
"""
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import time
import zipfile
from datetime import datetime
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
PY = sys.executable or "python3"
FAILURES = []


def check(name, ok, detail=""):
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {detail}" if not ok and detail else ""))
    if not ok:
        FAILURES.append(name)


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class FakeMail:
    Class = 43

    def __init__(self, subject, body="", unread=False, folder="Inbox", sender="Pat Example"):
        self.Subject = subject
        self.Body = body
        self.UnRead = unread
        self.SenderName = sender
        self.SenderEmailAddress = "pat@example.com"
        self.To = "me@example.com"
        self.CC = ""
        self.EntryID = "0000ABCDEF"
        self.ConversationTopic = subject
        self.ReceivedTime = datetime(2026, 9, 16, 10, 30)
        self.SentOn = datetime(2026, 9, 16, 10, 30)
        self.Parent = type("Folder", (), {"Name": folder})()


def mail_tests(tmp):
    mail = load_module(REPO / "_workstream" / "scan-outlook-mail.py", "scan_mail")
    rules = (
        'name: "Sam Example"   # shown in outputs\n'
        "mail_noise_subjects: Weekly numbers, Build report\n"
        'mail_ignore_folders: "Change notices"\n'
        "mail_noise_repos: team-repo\n"
    )
    cfg = mail.MailConfig(rules)
    check("Mail config: name read without the trailing comment", cfg.ba_name == "Sam Example", cfg.ba_name)
    check("Mail config: mention token from first name", cfg.mention == "@sam", cfg.mention)

    row = mail.item_row(FakeMail("Weekly numbers for September"), "inbox", cfg)
    check("Mail: configured noise subject is noise", row["noise"] and not row["action_hint"], row)
    row = mail.item_row(FakeMail("Can you review the draft?", "please confirm by Friday"), "inbox", cfg)
    check("Mail: a real ask is flagged for action", row["action_hint"] and not row["noise"], row)
    row = mail.item_row(FakeMail("Please review", folder="Change notices"), "inbox", cfg)
    check("Mail: mail in an ignored folder is noise", row["noise"] and not row["action_hint"], row)
    row = mail.item_row(FakeMail("[team-repo] Fix the thing"), "inbox", cfg)
    check("Mail: repo mail is noise unless mentioned", row["noise"], row)
    row = mail.item_row(FakeMail("[team-repo] Fix the thing", "hey @sam can you look"), "inbox", cfg)
    check("Mail: repo mail that mentions the BA is kept", not row["noise"], row)

    from datetime import date as _d
    check("Mail: default lookback Monday -> Friday", mail.default_since(_d(2026, 9, 14)) == _d(2026, 9, 11))
    check("Mail: default lookback Tuesday -> Monday", mail.default_since(_d(2026, 9, 15)) == _d(2026, 9, 14))
    check("Mail: default lookback Saturday -> Friday", mail.default_since(_d(2026, 9, 19)) == _d(2026, 9, 18))

    empty = mail.MailConfig("")
    row = mail.item_row(FakeMail("Weekly numbers for September", "can you check"), "inbox", empty)
    check("Mail: with no config, nothing organisation-specific is filtered", not row["noise"], row)
    check("Mail: placeholders never leak into matching", not empty.is_noise_text("[your-noise-subject-1]"))

    inbox = [mail.item_row(FakeMail("Re: Budget", "please advise", unread=False), "inbox", cfg),
             mail.item_row(FakeMail("New ask", "can you", unread=True), "inbox", cfg)]
    sent = [mail.item_row(FakeMail("Budget"), "sent", cfg)]
    out = mail.classify(inbox, sent)
    check("Mail: reply matched via sent subject counts as already handled",
          len(out["likely_already_handled"]) == 1 and len(out["unread"]) == 1)

    proc = subprocess.run([PY, str(REPO / "_workstream" / "scan-outlook-mail.py"), "--cursor-home", str(tmp)],
                          capture_output=True, text=True, timeout=30)
    if os.name != "nt":
        check("Mail: off Windows exits 2 with one 'unable to check' line",
              proc.returncode == 2 and proc.stdout.strip().startswith("Mail: unable to check"),
              proc.stdout + proc.stderr)
    else:
        check("Mail: exits 0 (scanned) or 2 (unable to check), never a traceback",
              proc.returncode in (0, 2) and "Traceback" not in proc.stderr, proc.stdout + proc.stderr)


def snapshot_tests(tmp):
    home = tmp / "snap-home" / ".cursor"
    root = tmp / "snap-home" / "my initiatives folder"
    (home / "rules").mkdir(parents=True)
    ws = home / "_workstream"
    ws.mkdir()
    (home / "rules" / "ba-profile.mdc").write_text(
        f'paths:\n  initiativesRoot: "{root.as_posix()}"   # set by setup\n', encoding="utf-8")
    init = root / "payments"
    init.mkdir(parents=True)
    (init / "SESSION-CONTEXT.md").write_text("# Payments\n**Next concrete action:** Chase sign-off\n", encoding="utf-8")
    (init / "initiative-tracker.md").write_text(
        "## Decisions\n| ID | Decision | Date |\n|---|---|---|\n| DEC-1 | Go | 2026-09-01 |\n", encoding="utf-8")
    (ws / "workboard.json").write_text(json.dumps({"initiatives": [{"slug": "payments", "name": "Payments uplift"}]}),
                                       encoding="utf-8")
    (ws / "ba-actions.json").write_text(json.dumps({"actions": [
        {"id": "BA-001", "task": "Chase", "status": "open", "initiative": "payments"}]}), encoding="utf-8")
    script = REPO / "_workstream" / "generate-initiative-snapshots.py"
    env = {k: v for k, v in os.environ.items() if k != "BA_INITIATIVES_ROOT"}

    def run(*args):
        p = subprocess.run([PY, str(script), "--cursor-home", str(home), *args], capture_output=True, text=True,
                           timeout=30, env=env)
        return p.returncode, p.stdout + p.stderr

    code, out = run("--check", "payments")
    check("Snapshot: missing reports MISSING (exit 1)", code == 1 and "MISSING" in out, out)
    code, out = run()
    snap = ws / "snapshots" / "payments.json"
    check("Snapshot: generated from the initiatives root in the profile", code == 0 and snap.exists(), out)
    data = json.loads(snap.read_text(encoding="utf-8"))
    check("Snapshot: is a non-canonical retrieval index with sources",
          data["canonical"] is False and data["sources"]["SESSION-CONTEXT.md"]["exists"]
          and data["current"]["nextAction"] == "Chase sign-off" and data["actions"][0]["id"] == "BA-001", data)
    code, out = run("--check", "payments")
    check("Snapshot: fresh right after generating (exit 0)", code == 0 and "FRESH" in out, out)
    (ws / "ba-actions.json").write_text(json.dumps({"actions": [
        {"id": "BA-002", "task": "Different", "status": "open", "initiative": "payments"}]}), encoding="utf-8")
    code, out = run("--check", "payments")
    check("Snapshot: a changed action (workstream input) makes it STALE", code == 1 and "ba-actions.json" in out, out)
    run()
    code, out = run("--check", "payments")
    check("Snapshot: fresh again after regenerating", code == 0 and "FRESH" in out, out)
    ctx = init / "SESSION-CONTEXT.md"
    st = ctx.stat()
    ctx.write_text(ctx.read_text(encoding="utf-8") + "new line\n", encoding="utf-8")
    os.utime(ctx, (st.st_atime, st.st_mtime))  # same timestamp as before: an mtime check would miss it
    code, out = run("--check", "payments")
    check("Snapshot: an edit with an unchanged timestamp is still STALE", code == 1 and "STALE" in out, out)
    (init / "Project-hub.md").write_text("# hub\n", encoding="utf-8")
    run()
    (init / "Project-hub.md").unlink()
    code, out = run("--check", "payments")
    check("Snapshot: a source file that disappeared makes it STALE", code == 1 and "Project-hub.md" in out, out)
    snap.write_text("{ not json", encoding="utf-8")
    code, out = run("--check", "payments")
    check("Snapshot: unreadable file is MALFORMED (exit 1)", code == 1 and "MALFORMED" in out, out)
    code, out = run("--slug", "nope")
    check("Snapshot: unknown slug fails clearly", code == 1 and "no initiative" in out, out)
    env["BA_INITIATIVES_ROOT"] = str(tmp / "no-such-folder")
    code, out = run()
    data = json.loads(snap.read_text(encoding="utf-8"))
    check("Snapshot: a stale BA_INITIATIVES_ROOT (not a folder) is ignored, config still applies",
          code == 0 and "no-such-folder" not in data["initiative"]["root"], out)
    (tmp / "elsewhere").mkdir(exist_ok=True)
    env["BA_INITIATIVES_ROOT"] = str(tmp / "elsewhere")
    code, out = run()
    data = json.loads(snap.read_text(encoding="utf-8"))
    check("Snapshot: BA_INITIATIVES_ROOT overrides config", str(tmp / "elsewhere") in data["initiative"]["root"], data)


def roll_highlight_tests(tmp):
    roll = load_module(REPO / "tools" / "roll-calendar-eod.py", "roll_hl")
    home = tmp / "roll-home" / ".cursor"
    (home / "rules").mkdir(parents=True)
    (home / "_workstream").mkdir()
    (home / "rules" / "ba-assistant-config.mdc").write_text(
        "calendar_highlight_substrings: Steering, weekly 1:1\n", encoding="utf-8")
    hl = roll.load_highlight_substrings(home / "_workstream")
    check("Roll: highlight substrings read from config", hl == ("Steering", "weekly 1:1"), str(hl))
    m = roll.build_workboard_meeting({"start": "2026-09-16T09:00:00", "subject": "Payments steering group",
                                      "duration_min": 30}, None, hl)
    check("Roll: configured substring highlights a meeting (case-insensitive)", m["highlight"] is True)
    m = roll.build_workboard_meeting({"start": "2026-09-16T09:00:00", "subject": "Standup", "duration_min": 15,
                                      "highlight": True}, None, hl)
    check("Roll: feed highlight flag still works", m["highlight"] is True)
    m = roll.build_workboard_meeting({"start": "2026-09-16T09:00:00", "subject": "Standup", "duration_min": 15},
                                     None, ())
    check("Roll: no config, no flag, no highlight", m["highlight"] is False)


def _minimal_docx(path: Path) -> None:
    xml = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
        "<w:body><w:p><w:r><w:t>Hello transcript</w:t></w:r></w:p></w:body></w:document>"
    )
    with zipfile.ZipFile(path, "w") as zf:
        zf.writestr("word/document.xml", xml)
        zf.writestr(
            "[Content_Types].xml",
            '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Override PartName="/word/document.xml" '
            'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
            "</Types>",
        )


def f17_extract_mark_processed(tmp: Path):
    home = tmp / "f17-home" / ".cursor"
    ws = home / "_workstream"
    ws.mkdir(parents=True)
    downloads = tmp / "f17-home" / "Downloads"
    downloads.mkdir(parents=True)
    docx = downloads / "Weekly sync - Transcript.docx"
    _minimal_docx(docx)
    out = tmp / "f17-out.txt"
    extract = REPO / "_workstream" / "extract-docx-text.py"
    env = {k: v for k, v in os.environ.items()}
    env["HOME"] = str(tmp / "f17-home")
    env["USERPROFILE"] = str(tmp / "f17-home")
    # Script writes processed-transcripts next to itself when installed; copy it into the throwaway workstream.
    import shutil

    shutil.copy(extract, ws / "extract-docx-text.py")
    shutil.copy(REPO / "_workstream" / "list-downloads-recent.py", ws / "list-downloads-recent.py")
    proc = subprocess.run(
        [PY, str(ws / "extract-docx-text.py"), "--docx-path", str(docx), "--out-path", str(out)],
        capture_output=True, text=True, env=env, timeout=30,
    )
    check("[F17] extract without flag exits 0", proc.returncode == 0, proc.stdout + proc.stderr)
    processed = ws / "processed-transcripts.json"
    after_extract = processed.read_text(encoding="utf-8") if processed.exists() else ""
    check("[F17] extract without flag does not mark processed",
          str(docx.resolve()) not in after_extract and docx.name not in after_extract, after_extract[:300])
    proc = subprocess.run(
        [PY, str(ws / "list-downloads-recent.py"), "--mark-processed", str(docx)],
        capture_output=True, text=True, env=env, timeout=30,
    )
    check("[F17] --mark-processed via list-downloads-recent exits 0", proc.returncode == 0, proc.stdout + proc.stderr)
    after_mark = processed.read_text(encoding="utf-8") if processed.exists() else ""
    check("[F17] --mark-processed records the transcript",
          str(docx.resolve()) in after_mark or docx.name in after_mark, after_mark[:400])


def f30_regenerate_help(tmp: Path):
    ws = tmp / "f30-ws"
    ws.mkdir()
    import shutil

    script = ws / "regenerate-ba-actions-md.py"
    shutil.copy(REPO / "_workstream" / "regenerate-ba-actions-md.py", script)
    data = {"schema_version": 1, "next_id": 1, "last_synced": "2026-10-05T12:00:00+13:00",
            "actions": [{"id": "BA-001", "task": "Demo", "status": "open", "priority": "medium",
                         "raised": "2026-10-01", "due": None}], "watching": []}
    json_path = ws / "ba-actions.json"
    md_path = ws / "ba-actions.md"
    json_path.write_text(json.dumps(data), encoding="utf-8")
    md_path.write_text("# before\n", encoding="utf-8")
    before_json = json_path.read_bytes()
    before_md = md_path.read_bytes()
    # Patch script paths: it binds JSON_PATH/MD_PATH at import to its own directory.
    proc = subprocess.run([PY, str(script), "--help"], capture_output=True, text=True, timeout=30)
    check("[F30] --help exits 0", proc.returncode == 0, proc.stdout + proc.stderr)
    check("[F30] --help prints usage", "usage:" in (proc.stdout + proc.stderr).lower(), (proc.stdout + proc.stderr)[:300])
    check("[F30] --help leaves JSON unchanged", json_path.read_bytes() == before_json)
    check("[F30] --help leaves MD unchanged", md_path.read_bytes() == before_md)


def main():
    with tempfile.TemporaryDirectory(prefix="ba-script-tests-") as tmp:
        tmp = Path(tmp)
        mail_tests(tmp)
        snapshot_tests(tmp)
        roll_highlight_tests(tmp)
        f17_extract_mark_processed(tmp)
        f30_regenerate_help(tmp)
    print(f"\n{'All script tests passed.' if not FAILURES else f'{len(FAILURES)} failed.'}")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
