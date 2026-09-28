---
description: BA Assistant — undo the last change to an initiative's files (plain English, no git needed)
---
Run the BA Assistant `/undo` command: put an initiative's files back the way they were before a change the assistant made (a capture, a debrief, `/wrap`, end of day, or any reply).

Every initiative keeps a private version history inside its folder (`~/.cursor/_workstream/initiative-history.py`; nothing leaves the machine). Never mention git, commits or ids unless the BA asks.

1. **Which initiative.** Use the one this chat is about. If unclear, AskQuestion with the initiative names.
2. **Show what can be undone.** Run `python3 ~/.cursor/_workstream/initiative-history.py history --initiative <slug> --limit 8` (Windows: `py`). Turn it into a short plain-English list: when, what happened, how many files. Example: "10 min ago: Debrief: steerco (3 files)".
3. **AskQuestion:** **Undo the latest change** (recommended) / **Go back further** (pick from the list) / **Cancel**.
4. **Undo.** Latest: `... undo --initiative <slug> --steps 1`. Further back: `... undo --initiative <slug> --to <id from the list>`. Report the result line in plain words: which files were put back, and to when.
5. **Say how to reverse it.** Undo never deletes anything: running `/undo` again puts the change back.

If it prints "History: unavailable" (for example git is not installed, or the folder is inside a git repo of the BA's own), say undo isn't available for this initiative and offer to restore the specific file by hand from what is in the chat.
