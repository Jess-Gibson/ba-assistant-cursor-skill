# Workboard procedure (cross-initiative refresh)

**Location:** `~/.cursor/skills/ba-assistant/references/workboard-procedure.md`  
**Owner:** `/workboard` (routed via `rules/skills-routing.mdc`)  
**Related:** `workboard-format.md` (status scoring + canvas contract), `ba-actions-format.md` (personal BA actions)
**Last reviewed:** 2026-09-04 (Workboard Control Centre)

Cross-initiative dashboard procedure. Not a sub-skill. Triggered by `/workboard`, "what should I work on", "my priorities", "what's next across everything", "show me my tasks", or the workboard canvas **Update** button.

Distinct from `ba-project-canvas` (deep single-initiative dashboard).

---

## Outputs

| File | Role |
|---|---|
| `_workstream/workboard.json` | Canonical cross-initiative data |
| `_workstream/ba-actions.json` | Canonical personal BA actions (not `personal_tasks[]`) |
| `_workstream/ba-actions.md` | Derived human view of BA actions |
| `_workstream/calendar-feed.json` | Optional meeting feed (see sample `calendar-feed.sample.json`) |
| `canvases/ba-workboard.canvas.tsx` | Visual surface, generated from the portable canvas template |
| `_workstream/generate-workboard-canvas.py` | Installed generator: converts a BA's own JSON into their canvas |

`_workstream/` lives in the Cursor user profile (`~/.cursor/_workstream/`), not inside one initiative folder.

---

## Initiative path resolution (mandatory)

For each `initiatives[].slug`, resolve the initiative folder in this order:

1. **`initiatives/{slug}/`** — Jess's local Cursor home (preferred on this machine)
2. **`-- analysis --/{slug}/`** — local analysis masters (`analysis-path-resolver.mdc`)
3. **`blueprints/{slug}/`** — packaged BA Assistant workspaces

Read `SESSION-CONTEXT.md` (tail ~50 lines) and `initiative-tracker.md` when present. Use `initiatives[].path` from `workboard.json` when set.

---

## Full refresh procedure

1. **Calendar.** Read `_workstream/calendar-feed.json` for today's + tomorrow's meetings (optional; skip gracefully if missing). Copy into `workboard.json → meetings_today`, `meetings_tomorrow`, `meetings_date` when refreshing.
2. **Current state.** Read `_workstream/workboard.json` and `_workstream/ba-actions.json` + `_workstream/ba-actions.md` (open BA actions).
2b. **Morning prep scan** (per `ba-actions-format.md` §4b): surface `remind_on` today/overdue, high-priority due today/tomorrow, blocked items. Optionally AskQuestion today's remind/due items (Done / In progress / Follow up / Move deadline / Cancel / No update).
3. **Per initiative.** For each entry in `initiatives[]` (by slug), read initiative folder per path resolution above.
4. **Downloads / transcripts check (best-effort).** Use the platform-appropriate listing from `workspace-operations.md` and `BA_DOWNLOADS_PATH`. Check all file types newer than the last refresh. Flag unprocessed transcripts or reference material. Write filenames to `unprocessed_downloads[]`.
4b. **Email scan (optional, best-effort).** If Outlook/Runlayer tools are available: inbox + sentitems, past 7 days, signal-only (@BA / URGENT / partner / compliance asks). Update `ba-actions.json` on real deltas. If unavailable: note "unable to check email" and continue.
5. **Jira delta (best-effort).** For initiatives with a `jira_project` set, query recent ticket movement since `jira_last_synced`. On MCP failure: note "Jira: unable to check" and continue.
5b. **Score initiative status** per `workboard-format.md` (decision flow + scoring rules). Do **not** default to `on-track`.
5c. **Run `sync-ba-actions`** if debriefs or tracker changed since last sync (`ba-actions-format.md` §3).
5d. **Regenerate `ba-actions.md`:** `py _workstream/regenerate-ba-actions-md.py` after any `ba-actions.json` write.
6. **Write** updated initiative statuses, phases, milestones, blockers, next actions, `ba_actions_summary`, meeting done-flags, optional `review_queue`, and `last_refreshed` back to `workboard.json`.
7. **Update the canvas:** generate `canvases/ba-workboard.canvas.tsx` from the installed portable template:

   ```text
   py _workstream/generate-workboard-canvas.py --canvas "<absolute Cursor project canvases path>/ba-workboard.canvas.tsx"
   ```

   It embeds the current BA's `workboard.json`, `ba-actions.json`, and optional calendar feed. Keep **Today / Initiatives / Open actions** tabs, **Update**, **End of Day**, and **Apply action updates** buttons. Do not add an End of day tab. Friendly date formats (e.g. "Friday 13 June"). Status badges must support all six enum values.
8. **Display:** priority banner, today's meetings, initiative sync status, open BA actions (link full list in `_workstream/ba-actions.md`).
9. **AskQuestion:** which task to tackle, or add/complete a task.

---

## Canvas draft apply procedure

When the user clicks **Apply action updates** on the canvas (or pastes the generated prompt):

1. Read draft patches from the chat prompt (sourced from `ba-workboard.canvas.data.json → draft-actions`).
2. Validate each `BA-NNN` ID exists in `ba-actions.json`.
3. Validate `status` ∈ `open|in_progress|done|cancelled|blocked` and `due` is ISO `YYYY-MM-DD` or empty.
4. Merge approved changes; set `last_updated` on each touched row.
5. Run `py _workstream/regenerate-ba-actions-md.py`.
6. Refresh workboard canvas (clear draft keys on regeneration).
7. Print `Gate: ba-actions-sync: PASS/FAIL`.

---

## First use (empty workboard)

If `_workstream/` or `workboard.json` is missing, create them (see `ba-setup` and `_workstream/README.md`). If `initiatives[]` is empty, prefer **Context Bootstrap** (`references/context-bootstrap.md`) before treating empty as OK. AskQuestion: run bootstrap / discover folders / add initiatives manually / skip. Then run the refresh.

---

## Calendar (optional)

Populate `_workstream/calendar-feed.json` via an OS-appropriate sample under `references/sample-scripts/` or copy `_workstream/calendar-feed.sample.json`. Not wired automatically; opt in via setup or hooks. Workboard degrades gracefully without it.

---

## Deprecated

Do **not** write new personal tasks to `workboard.json → personal_tasks[]`. Use `ba-actions.json` via `/todo` and `sync-ba-actions`.
