# End-of-day closeout procedure

**Location:** `~/.cursor/skills/ba-assistant/references/eod-closeout-procedure.md`
**Owner:** `sync-procedures.md` (pointer, base sync logic), this reference (the heavy, once-a-day tier)
**Split from `sync-procedures.md`:** this file bundled three tiers of
very different weight (`/validate-state`, light and frequent; `/wrap`, moderate;
`/workboard end-of-day`, heavy and once-a-day) into one load. This file is only
read when `/workboard end-of-day` (or the workboard canvas's End of Day button)
actually fires, not on every sync check.

Commands below use `python3` (Mac/Linux); on Windows, substitute `py`.

## Action runthrough (part of `/workboard end-of-day`)

Canonical store: `_workstream/ba-actions.json`. Human view: `_workstream/ba-actions.md` (regenerate before the runthrough; never hand-edit).

### 5a. EOD critical scan (before one-by-one walk)

Read `ba-actions.json` and `ba-actions.md`. **Surface first** (callout table in chat, before AskQuestion):

| Bucket | Rule |
|--------|------|
| **Overdue** | `due` before closeout date and status still `open` / `in_progress` / `blocked` |
| **Due today** | `due` equals closeout date and not `done` / `cancelled` |
| **Remind today** | `remind_on` equals closeout date and status still active |
| **High + due within 2 working days** | `priority: high` and due soon, flag if the user said they would finish today and have not |

Say plainly what is still open that the user committed to by end of day. Do not bury this inside the full list.

### 5b. One-by-one walk (today's key actions only)

Walk only actions matching **any** of: `status: blocked`, `due` on or before the closeout date (overdue/due today), `remind_on` equals the closeout date, `priority: high`, or `started_on` equals the closeout date. **Do not walk every open/in_progress action** — the user updates the rest directly in the canvas's Open actions tab; walking all of them means asking about things they haven't touched and have no update for. Order highest urgency first (overdue → due today → remind today → high → started today). Note the count of open/in_progress items excluded by this filter in the closing summary, so nothing silently disappears from view.

For each action walked:

1. Present task text, initiative, due, status, and `reminder` text (if any) via **AskQuestion** with options (slim set, avoid overlapping choices):
   - **Done** — mark `done`, clear `remind_on` if set
   - **Move to tomorrow** — set `due` and `remind_on` to the **next working day**; update `reminder` with one-line intent for that block
   - **Pick another date** — ask for ISO date in chat; update `due` and/or `remind_on` + `reminder`
   - **Schedule focus block** — user names a theme (or picks a suggested group); agent finds a free hour on the next working day from `calendar-feed.json` **and live Outlook** (`outlook_calendar_list_calendar_view`); proposes title + action list; on confirm, set `remind_on`/`reminder` on grouped rows and **create or update** a solo Outlook event (`outlook_calendar_create_event` / `outlook_calendar_update_event`) with action IDs and a one-line definition of done in the body. Do not duplicate an event the user already booked.
   - **Cancel** — mark `cancelled` with reason in `notes`
   - **Skip** — leave as-is (replaces "No update")
   - **Started today** (optional, when user actually began work) — set `started_on` to today; keep status `open` unless also Done

   Do **not** offer generic **In progress**, **Follow up**, or **Move deadline** as separate chips — they duplicate Skip / Move to tomorrow / Pick another date in practice.
2. Write changes to `ba-actions.json` immediately after each answer (or batch at end of a group if the user prefers speed, but never skip the question).
3. If the user surfaces new actions during the runthrough, insert with next `BA-NNN` via `/todo` rules or direct JSON upsert.

**Proactive focus-block offer.** After the walk, if two or more due-today/overdue items still have no scheduled focus block, don't wait for the user to pick the chip per item — offer once: "You've got N action items due/overdue with no time blocked. Want me to find a free slot and book them in?" Use the same Outlook mechanism as the per-item option above.

After the runthrough, regenerate `ba-actions.md`, print `Gate: ba-actions-sync: PASS/FAIL`, present a summary table of changes (including the excluded-item count), then proceed to step 6 (promote).

This pattern works because:
- EOD critical scan catches commitments before the long tail
- One-by-one AskQuestion forces structured review at end of day
- It captures verbal context and turns it into formal state updates
- It naturally identifies new actions and follow-ups

## Full end-of-day closeout sequence (`/workboard end-of-day`, canvas End of Day button)

The Action runthrough above and `sync-procedures.md`'s quick sync check cover the
core of the full closeout. The workboard canvas's End of Day button triggers this
procedure. It runs these steps in order:

1. **Mail triage (Inbox + Sent).** Run `python3 _workstream/scan-outlook-mail.py --since <today or last working day if morning gap> --out _workstream/mail-triage-latest.json`. Reconcile against what the user already handled today: unread first; open threads needing reply; Sent items that create a follow-up; mark noise aside. For each open non-noise thread: read latest replies and recommend next step or draft a reply. Do not rely on Downloads `.msg` alone. On failure: "Mail: unable to check" and continue.
1b. **Commitment scan (read-only).** Load `sub-skills/ba-commitment-scan/SKILL.md`. Reconcile the closeout-day Outlook triage, Slack (DMs, replies, mentions, threads the user reacted to) and Microsoft Teams (high-signal chats and accessible channels). Capture evidence-backed commitments, completions, decisions, risks and action changes into local state, then regenerate `ba-actions.md`. Read the user's working-hours preferences file in `_workstream/` (if one exists) before proposing any focus block. Never post, reply, react or create a communication artefact. On partial access failure, state the unavailable source and continue.
2. **Meeting reconciliation.** Read `_workstream/calendar-feed.json`. Check whether each meeting today (skip solo blocks) has a same-day SESSION-CONTEXT.md entry. Present one reconciliation table listing every meeting (`Time | Meeting | Initiative | Captured?`).
3. **Single recall question (not per-meeting).** Ask **one** AskQuestion covering the whole day: list today's meetings from the table above, then "Anything from any of these, or from side conversations, Slack decisions, hallway agreements, that isn't captured yet?" (options: "Nothing to add" / "Yes, let me tell you"). If yes, let the user describe freely across multiple meetings in one go, then write each item to the relevant initiative's SESSION-CONTEXT.md with a dated header and a `📝 Captured` tag. **Never loop meeting-by-meeting** — that costs a round-trip per meeting for meetings with nothing to add.
4. **State validation — active, touched, delta-only.** This step must never read a full `SESSION-CONTEXT.md` or full `initiative-tracker.md` unless the fallback in step (c) below triggers. Algorithm per initiative in `workboard.json`:
   a. **Skip if `status: closed` or `status: archived`** (e.g. Legacy Initiative). No read at all. `archived` additionally means: don't rescore, don't touch `last_validated` — it's fully out of the loop until unarchived.
   b. **Skip if `last_session` is not today.** Nothing changed since the last time this initiative was validated — don't open the file to check.
   c. **Otherwise, delta-read `SESSION-CONTEXT.md`.** Read `last_validated` for this initiative from `workboard.json` (treat missing as "never"). Find every `### <date> — ...` heading in the file dated **after** `last_validated` and read only those sections (the static preamble sections above the dated log — Quick context, Workspace context, PM approval state, etc. — don't need re-reading; they're reference, not a daily log). **Fallback:** if the file has no parseable `### <date>` headings, or `last_validated` is missing/unparseable, read the entire file this one time and say so in the drift report ("full read — no prior checkpoint" or "full read — unparseable date headers").
   d. **Check the tracker by targeted lookup, not full read.** For each `DEC-`/`RISK-`/`OQ-`/`ACT-`/`DEP-` marker found in the delta, grep `initiative-tracker.md` for that specific ID to confirm it was promoted. Do not read the tracker top to bottom — it isn't organised by date (a large initiative's tracker can be hundreds of thousands of characters of thematic RAID tables, not a daily log) and a targeted ID lookup answers the only question that matters here: did this specific item make it in.
   e. `status-data.json` is small and structured — keep reading it in full, no delta needed there.
   f. After validating, write today's closeout date to `last_validated` for this initiative in `workboard.json`.

   Report drift with specific item IDs and counts (this is a deeper pass than `sync-procedures.md`'s Quick sync check, which only scans for sync markers). **This replaces full-file reads for the common case** (a large initiative's SESSION-CONTEXT.md and tracker together can be hundreds of thousands of tokens; a typical day's delta should be a few hundred lines). `/validate-state all` (unchanged, on-demand, report-only) remains the full deep-sweep safety net for whenever the user wants one — suggest it occasionally rather than forcing it into every EOD.
5. **Action runthrough** — as described above.
6. **Promote unpromoted items** — copy decisions/risks/open questions/actions/dependencies already logged in SESSION-CONTEXT.md (from today's captures) into the initiative-tracker.md so the tracker stays the single source of truth, per `sync-procedures.md`'s Automated state cascade rules, tagging each with `[promoted]` so it isn't copied again.
6b. **Sync actions** — run `sync-ba-actions` per `references/ba-actions-format.md` §3: upsert user-owned rows from today's debriefs, SESSION-CONTEXT captures, and initiative tracker action registers; then **`python3 _workstream/regenerate-ba-actions-md.py`** (full MD derive from JSON, never hand-edit MD); print `Gate: ba-actions-sync: PASS/FAIL`. This step closes the debrief→tracker→action-list gap.
7. **Refresh `_workstream/workboard.json`** — initiative status updates (score per `references/workboard-format.md`, do not default to `on-track`), milestone `days_out` recalculated from today's date, `last_refreshed` updated, today's meetings marked done. Personal task counts come from `ba-actions.json`, not legacy `personal_tasks[]`.
7b+8. **Roll calendar once, then generate canvas (mandatory at EOD).** After step 7 marks today's meetings done, advance the board to the next working day. **Do exactly one path, never both** (running `roll-calendar-eod.py` and then `generate-workboard-canvas.py --eod-roll` double-rolls: Wed→Thu then Thu→Fri).

   **Preferred (single command):**
   `python3 _workstream/generate-workboard-canvas.py --eod-roll --closeout-date <closeout YYYY-MM-DD> --cursor-home "<~/.cursor>" --canvas "<path>/canvases/ba-workboard.canvas.tsx"`

   **Or two steps (no `--eod-roll` on generate):**
   1. `python3 _workstream/roll-calendar-eod.py --workstream "<~/.cursor>/_workstream" --closeout-date <closeout YYYY-MM-DD>`
   2. `python3 _workstream/generate-workboard-canvas.py --today <meetings_date from workboard.json> --cursor-home "<~/.cursor>" --canvas "<path>/canvases/ba-workboard.canvas.tsx"`

   Pass `--closeout-date` as the day being closed (usually today), not the already-rolled `meetings_date`. Print `Gate: calendar-roll: PASS/FAIL`. If the day after tomorrow is not in the feed, set `meetings_tomorrow_note` to re-pull Outlook on morning `/workboard` Update. Preserve Today / Initiatives / Open actions / optional Stakeholder raise, Update, End of Day, and Save staged updates. Today is read-only; draft edits are only on Open actions.
9. **Next-working-day prep.** Determine the next working day (skip Sat/Sun), unless critical meetings remain later today, in which case prep for the rest of today first. Read `calendar-feed.json` for that day and summarise: meetings (highlight critical ones), top priority tasks, prep items.

   **Morning prep from actions (mandatory):** Read `_workstream/ba-actions.json` and `_workstream/ba-actions.md`. Surface:
   - **`remind_on` on the next working day** (or overdue) where status is still `open` / `in_progress` / `blocked`
   - **High-priority actions due that day**
   - **Blocked items** that need a nudge before first meeting

   Present as **Reminders (commitments to start)** with date, task, and `reminder` text. Suggest the best opening move (one concrete first action before standup). This is the closeout's final step — end here, no handoff block.
