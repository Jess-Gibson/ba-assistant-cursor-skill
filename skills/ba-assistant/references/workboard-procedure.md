# Workboard procedure (cross-initiative refresh)

**Location:** `~/.cursor/skills/ba-assistant/references/workboard-procedure.md`  
**Owner:** `/workboard` (routed via `rules/skills-routing.mdc`)  
**Related:** `workboard-format.md` (status scoring and canvas contract), `ba-actions-format.md` (personal BA actions)  
**Last reviewed:** 2026-09-14

Cross-initiative dashboard procedure. Not a sub-skill. Triggered by `/workboard`, "what should I work on", "my priorities", "what's next across everything", "show me my tasks", or the workboard canvas **Update** button.

Distinct from `ba-project-canvas` (deep single-initiative dashboard).

Commands below use `python3` (Mac/Linux); on Windows, substitute `py`.

---

## Outputs

| File | Role |
|---|---|
| `_workstream/workboard.json` | Canonical cross-initiative snapshot |
| `_workstream/ba-actions.json` | Canonical personal BA action store |
| `_workstream/ba-actions.md` | Derived human view of open and closed actions |
| `_workstream/calendar-feed.json` | Optional meeting feed |
| `_workstream/generate-workboard-canvas.py` | Installed generator: converts this BA's JSON into their canvas |
| `canvases/ba-workboard.canvas.tsx` | Generated visual surface |

`_workstream/` lives in the Cursor user profile (`~/.cursor/_workstream/`), not inside one initiative folder.

---

## Initiative path resolution

For each `initiatives[].slug`, resolve its folder in this order:

1. `initiatives/{slug}/` when present (default `BA_INITIATIVES_ROOT`)
2. `blueprints/{slug}/` in a packaged workspace
3. Any custom path set in `ba-assistant-config.mdc`

Read `SESSION-CONTEXT.md` (tail around 50 lines) and `initiative-tracker.md` when present. Use `initiatives[].path` when it is set.

---

## Full refresh procedure

1. **Calendar.** Read `_workstream/calendar-feed.json` for today's and tomorrow's meetings; update `meetings_today`, `meetings_tomorrow`, and `meetings_date` when available.
2. **Current state.** Read `_workstream/workboard.json` and `_workstream/ba-actions.json` + `_workstream/ba-actions.md`.
2b. **Morning prep scan** (per `ba-actions-format.md` section 4b): surface `remind_on` today/overdue, high-priority due today/tomorrow, blocked items. Optionally AskQuestion today's remind/due items (Done / In progress / Follow up / Move deadline / Cancel / No update).
3. **Per initiative.** Refresh phase, milestone, blocker, risk, next action, and status from canonical files. Score status with `workboard-format.md`; never default to `on-track`.
4. **Downloads / transcripts check (best-effort).** Use the platform-appropriate listing from `workspace-operations.md` and `BA_DOWNLOADS_PATH`. Check all file types newer than the last refresh. Write filenames to `unprocessed_downloads[]`.
5. **Jira delta (best-effort).** For initiatives with `jira_project`, query recent ticket movement since `jira_last_synced`. On MCP failure: note "Jira: unable to check" and continue.
6. **Sync actions** if a debrief or tracker added/changed BA-owned actions (`sync-ba-actions`), then `python3 _workstream/regenerate-ba-actions-md.py`.
7. **Write** the refreshed snapshot back to `workboard.json`, including `ba_actions_summary`, downloads/review data when available, optional `stakeholder_raise`, and `last_refreshed`.
8. **Generate the canvas** from the portable template (this preserves Update and End of Day prompts):

   ```text
   python3 _workstream/generate-workboard-canvas.py --canvas "<absolute path>/canvases/ba-workboard.canvas.tsx"
   ```

   Omit `--canvas` only when a single Cursor project canvases folder exists. Keep **Today / Initiatives / Open actions**, optional **Stakeholder raise** when configured, **Update**, **End of Day**, and **Save staged updates**. Today is a read-only ordered day plan with checkboxes that stage done in Open actions. Editable status, due, and notes belong only in **Open actions**.

   Canvas **Update** and **End of Day** prompts are built by `generate-workboard-canvas.py` into `DATA.prompts` from this procedure, `sync-procedures.md`, and the BA's configured paths. Keep `commands/workboard.md` aligned when you change the procedure.
9. **AskQuestion:** which priority to tackle first.

---

## Canvas draft apply procedure

When the user clicks **Save staged updates** (or pastes the generated apply prompt):

1. Validate each `BA-NNN` ID against `_workstream/ba-actions.json`.
2. Accept only `open|in_progress|done|cancelled|blocked` status values and ISO `YYYY-MM-DD` due dates (or blank).
3. Merge approved changes, set `last_updated`, then run `python3 _workstream/regenerate-ba-actions-md.py`.
4. Regenerate the canvas to clear the draft overlay and report `Gate: ba-actions-sync: PASS/FAIL`.

Do not write new personal actions to deprecated `workboard.json → personal_tasks[]`.

---

## First use (empty workboard)

If `workboard.json` has no initiatives, run `/setup` or add initiative slugs manually, then `/workboard` again.

---

## Overlay upgrade (shared installs)

When a BA receives a **workboard overlay** package (see `tools/workboard-overlay-docs/INSTALL-WORKBOARD.md` in the repo, or `INSTALL-WORKBOARD.md` in the zip), only capability files are replaced: template, procedure, format, generator, and optionally generic `/workboard`. Their `workboard.json`, `ba-actions.json`, calendar feed, and profile rules are never wiped. After apply, run `/workboard` once to regenerate the canvas from their existing data.
