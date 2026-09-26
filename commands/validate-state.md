---
description: BA Assistant — write what this chat captured into the initiative files and ba-actions
---
Run the BA Assistant /validate-state command using `~/.cursor/skills/ba-assistant/sub-skills/ba-state-validator/SKILL.md`.

`/validate-state` checks this chat against the current initiative. Write what this chat captured into the right files: `SESSION-CONTEXT.md`, the tracker, and `status-data.json` where those files already exist, and upsert only the BA actions that came from this chat into `~/.cursor/_workstream/ba-actions.json`. Do not refresh the workboard. Do not walk every open action. Do not invent files. If something has no obvious home, say so and ask.

After upserting actions, regenerate `~/.cursor/_workstream/ba-actions.md` (`python3 ~/.cursor/_workstream/regenerate-ba-actions-md.py`; on Windows use `py`) and print `Gate: ba-actions-sync: PASS/FAIL`. This is not end of day.
