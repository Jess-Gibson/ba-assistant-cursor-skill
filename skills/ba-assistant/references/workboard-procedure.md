# Workboard procedure (cross-initiative refresh)

**Location:** `~/.cursor/skills/ba-assistant/references/workboard-procedure.md`  
**Owner:** `/workboard` (routed via `rules/skills-routing.mdc`)  
**Related:** `workboard-format.md` (status scoring), `ba-actions-format.md` (personal BA actions)  
**Last reviewed:** 2026-08-03 (Version 10)

Cross-initiative dashboard procedure. Not a sub-skill. Triggered by `/workboard`, "what should I work on", "my priorities", "what's next across everything", "show me my tasks", or the workboard canvas Update button.

Distinct from `ba-project-canvas` (deep single-initiative dashboard).

---

## Outputs

| File | Role |
|---|---|
| `_workstream/workboard.json` | Canonical cross-initiative data |
| `_workstream/ba-actions.json` | Canonical personal BA actions (not `personal_tasks[]`) |
| `_workstream/ba-actions.md` | Derived human view of BA actions |
| `canvases/ba-workboard.canvas.tsx` | Visual surface, regenerated from the JSON above |

`_workstream/` lives in the Cursor user profile (`~/.cursor/_workstream/`), not inside one initiative folder.

---

## Full refresh procedure

1. **Calendar.** Read `_workstream/calendar-feed.json` for today's + tomorrow's meetings (optional; skip gracefully if missing).
2. **Current state.** Read `_workstream/workboard.json` and `_workstream/ba-actions.json` + `_workstream/ba-actions.md` (open BA actions).
2b. **Morning prep scan** (per `ba-actions-format.md`): surface `remind_on` today/overdue, high-priority due today/tomorrow, blocked items. Optionally AskQuestion today's remind/due items (Done / In progress / Follow up / Move deadline / Cancel / No update).
3. **Per initiative.** For each entry in `initiatives[]` (by slug), read `blueprints/{slug}/SESSION-CONTEXT.md` (tail ~50 lines) + `initiative-tracker.md` if it exists.
4. **Downloads / transcripts check (best-effort).** Use the platform-appropriate listing from `workspace-operations.md` and `BA_DOWNLOADS_PATH`. Check all file types newer than the last refresh. Flag unprocessed transcripts or reference material. Do not assume `.docx` only.
5. **Jira delta (best-effort).** For initiatives with a `jira_project` set, query recent ticket movement since `jira_last_synced`. On MCP failure: note "Jira: unable to check" and continue.
5b. **Score initiative status** per `workboard-format.md` (decision flow + scoring rules). Do **not** default to `on-track`.
5c. **Run `sync-ba-actions`** if debriefs or tracker changed since last sync (`ba-actions-format.md` §3).
6. **Write** updated initiative statuses, phases, milestones, blockers, next actions, meeting done-flags, and `last_refreshed` back to `workboard.json`.
7. **Update the canvas:** rewrite `canvases/ba-workboard.canvas.tsx` with refreshed data (initiatives, BA-action subset from ba-actions, calendar events, callouts) embedded inline. Keep the same layout, Update button, and End of Day button (with their prompts). Friendly date formats (e.g. "Friday 13 June"). StatusDot must support all six enum values from `workboard-format.md`.
8. **Display:** priorities table, today's meetings, initiative sync status, open BA actions (link full list in `_workstream/ba-actions.md`).
9. **AskQuestion:** which task to tackle, or add/complete a task.

---

## First use (empty workboard)

If `_workstream/` or `workboard.json` is missing, create them (see `ba-setup` and `_workstream/README.md`). If `initiatives[]` is empty, prefer **Context Bootstrap** (`references/context-bootstrap.md`) before treating empty as OK. AskQuestion: run bootstrap / discover folders / add initiatives manually / skip. Then run the refresh.

---

## Calendar (optional)

Populate `_workstream/calendar-feed.json` via an OS-appropriate sample under `references/sample-scripts/` (Windows Outlook `.ps1`, macOS sample). Not wired automatically; opt in via setup or hooks. Workboard degrades gracefully without it.

---

## Deprecated

Do **not** write new personal tasks to `workboard.json → personal_tasks[]`. Use `ba-actions.json` via `/todo` and `sync-ba-actions`.
