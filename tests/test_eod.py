"""
End-of-day regression tests (Version 15): one calendar roll per closeout date,
fail-closed on inconsistent roll markers, and a canvas End of Day prompt that
defers to eod-closeout-procedure.md instead of carrying its own stale copy.

Standalone (no pytest), same style as tests/test_hooks.py. Everything runs in a
throwaway folder.

Run:
    python3 tests/test_eod.py      (Windows: py tests/test_eod.py)
"""
import hashlib
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
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


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def make_workstream(tmp, meetings_date="2026-09-16", rolled=None):
    """A _workstream with Wed 16, Thu 17 and Fri 18 Sep 2026 meetings."""
    home = Path(tempfile.mkdtemp(dir=tmp))
    ws = home / ".cursor" / "_workstream"
    ws.mkdir(parents=True)
    (home / ".cursor" / "rules").mkdir(parents=True)
    meetings = [
        {"start": "2026-09-16T09:00:00+12:00", "duration_min": 30, "subject": "Wed standup"},
        {"start": "2026-09-17T10:00:00+12:00", "duration_min": None, "subject": "Thu review"},
        {"start": "2026-09-18T11:00:00+12:00", "subject": "Fri planning"},
    ]
    cal = {"meetings": meetings}
    if rolled:
        cal.update(rolled)
    (ws / "calendar-feed.json").write_text(json.dumps(cal, indent=2), encoding="utf-8")
    (ws / "workboard.json").write_text(json.dumps({"meetings_date": meetings_date, "initiatives": []}, indent=2),
                                       encoding="utf-8")
    shutil.copy2(REPO / "tools" / "roll-calendar-eod.py", ws / "roll-calendar-eod.py")
    return home, ws


def roll(ws, *args):
    proc = subprocess.run([PY, str(ws / "roll-calendar-eod.py"), "--workstream", str(ws), *args],
                          capture_output=True, text=True, timeout=30)
    return proc.returncode, proc.stdout + proc.stderr


def main():
    with tempfile.TemporaryDirectory(prefix="ba-eod-tests-") as tmp:
        tmp = Path(tmp)

        # --- Roll once, then a repeat for the same date writes nothing ---
        home, ws = make_workstream(tmp)
        code, out = roll(ws, "--closeout-date", "2026-09-16")
        wb = json.loads((ws / "workboard.json").read_text(encoding="utf-8"))
        check("Roll: first roll PASS and moves Wed -> Thu",
              code == 0 and "calendar-roll: PASS" in out and wb["meetings_date"] == "2026-09-17", out)
        check("Roll: duration_min null does not crash and leaves end time blank",
              any(m["subject"] == "Thu review" and m["end"] == "" for m in wb["meetings_today"]), wb)
        before = (sha(ws / "calendar-feed.json"), sha(ws / "workboard.json"))
        code, out = roll(ws, "--closeout-date", "2026-09-16")
        after = (sha(ws / "calendar-feed.json"), sha(ws / "workboard.json"))
        check("Roll: repeat for same date is SKIPPED with exit 0", code == 0 and "SKIPPED" in out, out)
        check("Roll: repeat for same date leaves both files byte-identical", before == after)

        # --- Omitted date after a roll fails closed (the old silent double roll) ---
        code, out = roll(ws)
        check("Roll: omitted --closeout-date after a roll fails closed",
              code == 1 and "FAIL" in out and "--closeout-date" in out, out)
        check("Roll: failed omitted-date roll wrote nothing",
              (sha(ws / "calendar-feed.json"), sha(ws / "workboard.json")) == before)

        # --- A genuinely later closeout still rolls ---
        code, out = roll(ws, "--closeout-date", "2026-09-17")
        wb = json.loads((ws / "workboard.json").read_text(encoding="utf-8"))
        check("Roll: later closeout date (Thu) rolls to Fri",
              code == 0 and "PASS" in out and wb["meetings_date"] == "2026-09-18", out)

        # --- Friday rolls to Monday ---
        code, out = roll(ws, "--closeout-date", "2026-09-18")
        wb = json.loads((ws / "workboard.json").read_text(encoding="utf-8"))
        check("Roll: Friday closeout rolls to Monday", wb["meetings_date"] == "2026-09-21", out)

        # --- Inconsistent markers: feed says rolled, workboard never moved ---
        home, ws = make_workstream(tmp, meetings_date="2026-09-16",
                                   rolled={"rolled_from": "2026-09-16", "rolled_to": "2026-09-17"})
        before = (sha(ws / "calendar-feed.json"), sha(ws / "workboard.json"))
        code, out = roll(ws, "--closeout-date", "2026-09-16")
        check("Roll: partial roll (workboard not moved) fails closed", code == 1 and "partial" in out, out)
        check("Roll: partial roll check wrote nothing",
              (sha(ws / "calendar-feed.json"), sha(ws / "workboard.json")) == before)

        # --- Wrong rolled_to also fails closed ---
        home, ws = make_workstream(tmp, meetings_date="2026-09-18",
                                   rolled={"rolled_from": "2026-09-16", "rolled_to": "2026-09-18"})
        code, out = roll(ws, "--closeout-date", "2026-09-16")
        check("Roll: rolled_to that is not the next working day fails closed", code == 1, out)

        # --- Morning catch-up: close yesterday explicitly on a fresh feed ---
        home, ws = make_workstream(tmp, meetings_date="2026-09-16")
        code, out = roll(ws, "--closeout-date", "2026-09-16")
        check("Roll: explicit earlier closeout date on a fresh feed rolls", code == 0 and "PASS" in out, out)

        # --- Bad date string ---
        code, out = roll(ws, "--closeout-date", "16/09/2026")
        check("Roll: malformed --closeout-date fails with a clear message", code == 1 and "YYYY-MM-DD" in out, out)

        # --- Canvas --eod-roll path gets the same guard ---
        home, ws = make_workstream(tmp)
        gen = [PY, str(REPO / "tools" / "generate-workboard-canvas.py"), "--cursor-home", str(home / ".cursor"),
               "--canvas", str(home / "canvas.tsx"), "--eod-roll", "--closeout-date", "2026-09-16"]
        p1 = subprocess.run(gen, capture_output=True, text=True, timeout=60)
        wb1 = json.loads((ws / "workboard.json").read_text(encoding="utf-8"))
        p2 = subprocess.run(gen, capture_output=True, text=True, timeout=60)
        wb2 = json.loads((ws / "workboard.json").read_text(encoding="utf-8"))
        check("Canvas --eod-roll: first run rolls Wed -> Thu", wb1["meetings_date"] == "2026-09-17", p1.stdout + p1.stderr)
        check("Canvas --eod-roll: second run for same date does not roll again",
              wb2["meetings_date"] == "2026-09-17" and "SKIPPED" in p2.stdout, p2.stdout + p2.stderr)
        check("Canvas --eod-roll: no duplicate FAIL line on skip", "FAIL" not in p2.stdout, p2.stdout)

        # --- Canvas --eod-roll stops on a failed roll (no canvas, exit 1) ---
        home, ws = make_workstream(tmp, meetings_date="2026-09-16",
                                   rolled={"rolled_from": "2026-09-16", "rolled_to": "2026-09-17"})
        canvas = home / "canvas.tsx"
        p3 = subprocess.run([PY, str(REPO / "tools" / "generate-workboard-canvas.py"), "--cursor-home", str(home / ".cursor"),
                             "--canvas", str(canvas), "--eod-roll", "--closeout-date", "2026-09-16"],
                            capture_output=True, text=True, timeout=60)
        check("Canvas --eod-roll: partial roll exits 1 and writes no canvas",
              p3.returncode == 1 and not canvas.exists() and "FAIL" in p3.stdout, p3.stdout + p3.stderr)
        (ws / "calendar-feed.json").unlink()
        p4 = subprocess.run([PY, str(REPO / "tools" / "generate-workboard-canvas.py"), "--cursor-home", str(home / ".cursor"),
                             "--canvas", str(canvas), "--eod-roll", "--closeout-date", "2026-09-16"],
                            capture_output=True, text=True, timeout=60)
        check("Canvas --eod-roll: missing calendar feed exits 1 and writes no canvas",
              p4.returncode == 1 and not canvas.exists(), p4.stdout + p4.stderr)

        # --- Canvas End of Day prompt ---
        gen_mod = load_module(REPO / "tools" / "generate-workboard-canvas.py", "gen_canvas_eod")
        config = gen_mod.load_workboard_config(home / ".cursor")
        prompt = gen_mod.build_eod_prompt(config)
        check("EOD prompt: points at eod-closeout-procedure.md", "eod-closeout-procedure.md" in prompt)
        check("EOD prompt: no stale sync-procedures.md Full end-of-day pointer",
              "sync-procedures.md (Full end-of-day" not in prompt and "sync-procedures.md" not in prompt)
        invocations = len(re.findall(r"--eod-roll", prompt)) + len(re.findall(r"\S*roll-calendar-eod\.py\s+--", prompt))
        check("EOD prompt: exactly one calendar-roll invocation", invocations == 1, str(invocations))
        check("EOD prompt: passes --closeout-date", "--closeout-date" in prompt)
        check("EOD prompt: does not tell the agent to walk every open action",
              "Walk every open" not in prompt and "Do not walk every open action" in prompt)
        mail = prompt.find("scan-outlook-mail.py"), prompt.find("MCP"), prompt.find("Mail: unable to check")
        check("EOD prompt: mail order is script, then MCP, then unable to check",
              -1 not in mail and mail[0] < mail[1] < mail[2], str(mail))

        # --- Procedure and command agree with the prompt ---
        proc_text = (REPO / "skills" / "ba-assistant" / "references" / "eod-closeout-procedure.md").read_text(encoding="utf-8")
        step = proc_text[proc_text.index("7b+8."):proc_text.index("9. **Next-working-day prep")]
        check("Procedure 7b+8: one canonical command, no two-step alternative",
              step.count("--eod-roll") == 1 and "Or two steps" not in step)
        mail_step = proc_text[proc_text.index("1. **Mail check"):proc_text.index("1b. **Commitment scan")]
        # the last "unable to check" is the final fallback; (b) may quote the script's own message
        m = mail_step.find("scan-outlook-mail.py"), mail_step.find("MCP"), mail_step.rfind("Mail: unable to check")
        check("Procedure step 1: mail order is script, then MCP, then unable to check",
              -1 not in m and m[0] < m[1] < m[2], str(m))
        cmd_text = (REPO / "commands" / "workboard.md").read_text(encoding="utf-8")
        check("commands/workboard.md defers end of day to eod-closeout-procedure.md",
              "eod-closeout-procedure.md" in cmd_text)

    print(f"\n{'All EOD tests passed.' if not FAILURES else f'{len(FAILURES)} failed.'}")
    return 1 if FAILURES else 0


if __name__ == "__main__":
    sys.exit(main())
