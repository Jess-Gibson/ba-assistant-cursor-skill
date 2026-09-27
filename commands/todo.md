---
description: Quick-capture a personal task into ba-actions
---
Follow the `todo-quick-capture` rule (`~/.cursor/rules/todo-quick-capture.mdc`): parse the task(s) from $ARGUMENTS, write them with `python3 ~/.cursor/_workstream/ba-actions.py` (Windows: `py`; it upserts `ba-actions.json`, regenerates `ba-actions.md` and prints the gate), and confirm compactly. No status dump, no orchestrator.
