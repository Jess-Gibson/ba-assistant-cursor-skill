"""
Run every package test in one go. For people changing this repo, before a push.

These never run while a BA uses the assistant: the installer does not copy
tests/ or hooks/tests/, and no skill, rule, hook or command calls them.

Run:
    python3 tests/run_all.py      (Windows: py tests/run_all.py)
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SUITES = [
    REPO / "hooks" / "tests" / "test_jira_dor_gate.py",
    REPO / "tests" / "test_hooks.py",
    REPO / "tests" / "test_package_consistency.py",
    REPO / "tests" / "test_eod.py",
    REPO / "tests" / "test_scripts.py",
    REPO / "tests" / "test_install_upgrade.py",
    REPO / "tests" / "test_merge_tool.py",
]


def main():
    failed = []
    for suite in SUITES:
        print(f"\n=== {suite.relative_to(REPO)} ===", flush=True)
        if subprocess.run([sys.executable, str(suite)], cwd=REPO).returncode != 0:
            failed.append(suite.name)
    print("\n" + ("ALL SUITES PASSED" if not failed else "FAILED: " + ", ".join(failed)))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
