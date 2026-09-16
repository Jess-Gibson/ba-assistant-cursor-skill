---
description: BA Workboard — cross-initiative priorities, tasks, and calendar in one view
---
Run `/workboard` as a full morning or mid-day refresh of my daily operating surface. Do the whole procedure. Do not stop at a one-line summary. The goal is an honest Today queue I can run from: real priorities, real initiative health, current calendar, and current BA actions.

Read first, then follow:
- `skills/ba-assistant/references/workboard-procedure.md`
- `skills/ba-assistant/references/workboard-format.md` (score initiative status from evidence; never default to on-track)
- `skills/ba-assistant/references/ba-actions-format.md` section 4b Daily update
- `_workstream/ba-actions.md` and `_workstream/ba-actions.json`
- `_workstream/calendar-feed.json`
- `_workstream/workboard.json`

Initiative state lives under the folder configured in `ba-assistant-config.mdc` (`BA_INITIATIVES_ROOT`, default `~/.cursor/initiatives/{slug}/`). Read `SESSION-CONTEXT.md` (tail about 50 lines) and `initiative-tracker.md` when present.

Then:
1. Refresh calendar for today and the next working day into `workboard.json`.
2. Morning-prep scan of BA actions: overdue; `remind_on` today or overdue; due today; blocked items that today's meetings could unblock; then high-priority due tomorrow. Surface these first in chat.
3. For each initiative, refresh phase, milestone, blocker, risk, next action, and status from canonical files. Score status using `workboard-format.md`.
4. Downloads: use the platform-appropriate listing from `workspace-operations.md` and `BA_DOWNLOADS_PATH`. Triage files newer than `last_refreshed`. Skip installers, zips, lnk, ini.
5. Jira movement for initiatives with `jira_project`. If Jira is unavailable, record unable to check and continue.
6. Run `sync-ba-actions` only if a debrief or tracker added BA-owned actions, then `py _workstream/regenerate-ba-actions-md.py`.
7. Write the snapshot to `_workstream/workboard.json` (including `ba_actions_summary`, downloads, `last_refreshed`). Keep **Today** as a read-only ordered day plan with staging checkboxes. Editable status, due, and notes belong only on **Open actions**.
8. Generate the canvas from the portable template (preserves Update and End of Day prompts):
   `py _workstream/generate-workboard-canvas.py --canvas "<absolute path>/canvases/ba-workboard.canvas.tsx"`
9. Keep tabs Today / Initiatives / Open actions, optional Stakeholder raise when configured, and buttons Update, End of Day, Save staged updates.

Do not walk every open BA action (that is End of Day / `/wrap`). Optional short AskQuestion only on today's remind or due items if yesterday was not closed out.

End with: what changed, the ordered Today queue, and AskQuestion for which priority to tackle first.
