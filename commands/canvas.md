---
description: BA Assistant — render the interactive project canvas and HTML snapshot (on demand only)
---
Run the BA Assistant /canvas command (`~/.cursor/skills/ba-assistant/sub-skills/ba-project-canvas/SKILL.md`, "Generate or refresh" row). In short: confirm the initiative, bring `status-data.json` up to date with `~/.cursor/skills/ba-assistant/references/status-refresh.md` (change only what is out of date; Jira only if the last sync is 60 minutes old or more), then run `python3 ~/.cursor/_workstream/render-initiative-canvas.py --initiative <slug>` (Windows: `py`). It writes the 8-tab `.canvas.tsx` and `status-snapshot.html`. Do not read every project file and do not hand-write canvas code. Report the paths and any tabs the script says are empty.
