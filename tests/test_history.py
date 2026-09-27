"""
Tests for _workstream/initiative-history.py: private local version history per
initiative folder, so any change can be undone in plain English.

Run:
    python3 tests/test_history.py      (Windows: py tests/test_history.py)
"""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
HIST = REPO / "_workstream" / "initiative-history.py"
CAPTURE = REPO / "_workstream" / "capture.py"
PY = sys.executable or "python3"
results = []


def check(name, ok, detail=""):
    ok = bool(ok)
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}" + (f"\n      {detail}" if not ok and detail else ""))


def env_for(home, extra=None):
    env = {k: v for k, v in os.environ.items()
           if not k.startswith("BA_") and not k.startswith("GIT_") and k != "CURSOR_SESSION_CONTEXT_PATH"}
    env.update({"HOME": str(home), "USERPROFILE": str(home)})
    env.update(extra or {})
    return env


def hist(home, *args, extra_env=None):
    proc = subprocess.run([PY, str(HIST), *args, "--cursor-home", str(home / ".cursor")], capture_output=True,
                          text=True, env=env_for(home, extra_env), timeout=60)
    return proc.returncode, proc.stdout


def git_log(folder):
    return subprocess.run(["git", "log", "--format=%s"], cwd=folder, capture_output=True, text=True).stdout.splitlines()


def make_home(tmp, names=("refunds",)):
    home = Path(tempfile.mkdtemp(dir=tmp))
    for n in names:
        d = home / ".cursor" / "initiatives" / n
        d.mkdir(parents=True)
        (d / "SESSION-CONTEXT.md").write_text(f"# {n}\n", encoding="utf-8")
        (d / "initiative-tracker.md").write_text("## Decisions\n", encoding="utf-8")
    (home / ".cursor" / "_workstream").mkdir(parents=True, exist_ok=True)
    return home


def main():
    if not shutil.which("git"):
        print("SKIP  git not installed: history tests need git (the script itself degrades to a no-op)")
        return 0
    with tempfile.TemporaryDirectory(prefix="hist-") as tmp:
        tmp = Path(tmp)
        home = make_home(tmp, ("refunds", "payroll"))
        init = home / ".cursor" / "initiatives" / "refunds"

        code, out = hist(home, "ensure", "--all")
        check("ensure --all starts a history in every initiative",
              code == 0 and "started for refunds" in out and "started for payroll" in out
              and (init / ".git").is_dir(), out)
        code, out = hist(home, "ensure", "--initiative", "refunds")
        check("ensure is idempotent", "already on for refunds" in out, out)
        check("history repos have no remote", subprocess.run(["git", "remote"], cwd=init, capture_output=True,
                                                               text=True).stdout.strip() == "")

        code, out = hist(home, "snapshot", "--initiative", "refunds", "--label", "Nothing changed")
        check("snapshot with no changes saves nothing", out.strip() == "" and len(git_log(init)) == 1, out)

        # capture.py saves a version before and after it writes
        subprocess.run([PY, str(CAPTURE), "--cursor-home", str(home / ".cursor"), "--initiative", "refunds",
                        "--source", "chat-user", "--type", "decision", "--text", "Use the ledger API for refunds"],
                       capture_output=True, text=True, env=env_for(home), timeout=60)
        log = git_log(init)
        check("capture.py leaves a version after writing", log[0].startswith("Captured 1 item"), str(log))

        (init / "initiative-tracker.md").write_text("## Decisions\n- D-01 wrong decision\n", encoding="utf-8")
        (init / "debriefs").mkdir()
        (init / "debriefs" / "steerco.md").write_text("# Steerco\n", encoding="utf-8")
        code, out = hist(home, "snapshot", "--initiative", "refunds", "--label", "Debrief: steerco")
        check("snapshot saves a labelled version", "saved refunds (Debrief: steerco)" in out, out)

        code, out = hist(home, "history", "--initiative", "refunds")
        check("history is plain English, newest first",
              "Recent versions of refunds" in out and "0. just now: Debrief: steerco, 2 file(s)" in out
              and "commit" not in out.lower(), out)

        (init / "SESSION-CONTEXT.md").write_text("# refunds\nunsaved note\n", encoding="utf-8")
        code, out = hist(home, "undo", "--initiative", "refunds")
        tracker = (init / "initiative-tracker.md").read_text(encoding="utf-8")
        check("undo puts files back and removes a file the change added",
              code == 0 and out.startswith("Undo: PASS") and "wrong decision" not in tracker
              and not (init / "debriefs" / "steerco.md").exists(), out)
        check("undo keeps unsaved edits recoverable (saved as 'Before undo' first)",
              "Before undo (edits not saved yet)" in git_log(init), str(git_log(init)))
        code, out = hist(home, "undo", "--initiative", "refunds")
        check("undo is itself undoable (undo again brings the change back)",
              "wrong decision" in (init / "initiative-tracker.md").read_text(encoding="utf-8"), out)

        first = subprocess.run(["git", "rev-list", "--max-parents=0", "HEAD"], cwd=init, capture_output=True,
                               text=True).stdout.strip()[:7]
        code, out = hist(home, "undo", "--initiative", "refunds", "--to", first)
        check("undo --to goes back to a chosen version",
              "History started" in out and not (init / "debriefs" / "steerco.md").exists(), out)

        # stop hook saves the chat's initiative after each reply
        (init / "SESSION-CONTEXT.md").write_text("# refunds\nreply edit\n", encoding="utf-8")
        subprocess.run([PY, str(REPO / "hooks" / "inject-state-reminder.py"), "--stop"], input="{}",
                       capture_output=True, text=True, timeout=30,
                       env=env_for(home, {"CURSOR_SESSION_CONTEXT_PATH": str(init / "SESSION-CONTEXT.md")}))
        check("stop hook saves a version after an assistant reply", git_log(init)[0] == "After assistant reply",
              str(git_log(init)[:3]))

        # session start saves every initiative that already has a history (never starts one)
        (home / ".cursor" / "initiatives" / "payroll" / "initiative-tracker.md").write_text("changed\n", encoding="utf-8")
        fresh = home / ".cursor" / "initiatives" / "newone"
        fresh.mkdir()
        (fresh / "SESSION-CONTEXT.md").write_text("# new\n", encoding="utf-8")
        shutil.copy(HIST, home / ".cursor" / "_workstream" / "initiative-history.py")
        subprocess.run([PY, str(REPO / "hooks" / "session-init.py")], input="{}", capture_output=True, text=True,
                       timeout=60, env=env_for(home, {"TMPDIR": str(tmp), "XDG_RUNTIME_DIR": str(tmp),
                                                      "LOCALAPPDATA": str(tmp)}))
        check("session start saves initiatives that have a history",
              git_log(home / ".cursor" / "initiatives" / "payroll")[0] == "Start of chat")
        check("session start never starts a history (can be slow on big folders)", not (fresh / ".git").exists())

        # a folder inside the BA's own git repo is left alone
        own = make_home(tmp, ("inside",))
        subprocess.run(["git", "init", "-q"], cwd=own / ".cursor", capture_output=True)
        code, out = hist(own, "ensure", "--all")
        check("an initiative inside the BA's own git repo is left alone",
              "left alone" in out and not (own / ".cursor" / "initiatives" / "inside" / ".git").exists(), out)

        # no git: silent no-op, exit 0, capture still works
        nogit = make_home(tmp, ("offline",))
        bindir = tmp / "bin-nogit"
        bindir.mkdir()
        code, out = hist(nogit, "snapshot", "--all", extra_env={"PATH": str(bindir)})
        check("no git: one plain line, exit 0", code == 0 and out.startswith("History: unavailable (git is not installed"),
              out)
        proc = subprocess.run([PY, str(CAPTURE), "--cursor-home", str(nogit / ".cursor"), "--initiative", "offline",
                               "--source", "chat-user", "--type", "fact", "--text", "Month end is on the third"],
                              capture_output=True, text=True, timeout=60, env=env_for(nogit, {"PATH": str(bindir)}))
        check("no git: capture still writes", proc.returncode == 0 and "Capture: PASS" in proc.stdout, proc.stdout)

    passed = sum(results)
    print(f"\n{passed}/{len(results)} history checks passed")
    return 0 if passed == len(results) else 1


if __name__ == "__main__":
    sys.exit(main())
