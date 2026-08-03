# Sync Procedures Reference

**Location:** `~/.cursor/skills/ba-assistant/references/sync-procedures.md`
**Owner:** sync-gates.mdc (pointer, always-on), this reference (procedures)
**Last reviewed:** 2026-07-08

Demoted from the always-on `sync-gates.mdc` in the always-on restructure. Load when a sync
trigger fires or a sync command (`/validate-state`, `/wrap`) runs. The 20-turn breakpoint
check is now deterministic (stop-hook `stop-sync-check.sh`) and no longer relies on this file.

## Procedures (formerly the sync-gates.mdc body)

State drift is the number one workflow pain. This rule defines **when** and **how** the agent checks that canonical files are in sync.

## Two sync layers

| Layer | Trigger | Agent action |
|-------|---------|-------------|
| **Inline capture** | Every conversation turn | Context Capture skill silently appends to SESSION-CONTEXT.md. No user-visible action. |
| **Sync gate** | See triggers below | Run sync check, present sync card if drift detected. Fix on `/wrap`; report-only on `/validate-state`. |

## Commands (simplified)

| Command | Purpose | Mutates? |
|---------|---------|----------|
| `/validate-state` | Mid-session drift report  -  "am I behind?" | No (read-only, offers fix options) |
| `/wrap` | End-of-session closeout  -  runs validate-state then promotes + refreshes workboard + suggests new chat | Yes |

**`/sync-check` is retired.** Use `/validate-state` for diagnostics or `/wrap` to close out. If the user types `/sync-check`, treat it as `/validate-state`.

## Sync gate triggers (mandatory)

The agent MUST run a **quick sync check** at each of these breakpoints:

1. **After a debrief completes** -- the debrief just wrote to SESSION-CONTEXT and possibly tracker. Check: did all outputs land? Is status-data.json still consistent?
2. **Before switching initiatives** -- when the user says "Data Collection resume" after working on Sample Initiative, run sync on the OUTGOING initiative before loading the new one.
3. **Before any Confluence publish** -- check that local files are current before pushing stale data to Confluence.
4. **On `/validate-state` command** -- user-initiated, runs for current initiative (report only).
5. **On `/validate-state all` command** -- runs across all initiatives (report only).
6. **On `/wrap` command** -- session closeout: run the **full end-of-day closeout sequence** (see below) -- Downloads check, meeting reconciliation + recall, full-file state validation, action runthrough, promote, refresh workboard, rewrite canvas, next-working-day prep, suggest new chat.
7. **At 20 turns in a BA thread** -- regardless of topic drift. Run a lightweight mid-session sync: check for unpromoted items in SESSION-CONTEXT, promote if >3 items, suggest a checkpoint. Present as a brief inline note, not a full sync card. If the user defers, don't ask again until 40 turns.

## Quick sync check procedure

When a sync gate fires, the agent performs these checks (fast, no MCP calls unless needed):

### Step 1: SESSION-CONTEXT vs initiative-tracker
- Scan SESSION-CONTEXT.md for items tagged with sync markers (decisions, risks, unknowns, actions) that don't appear in initiative-tracker.md
- Look for: `DEC-`, `RISK-`, `OQ-`, `ACT-`, `DEP-` prefixes, or items under `## Decisions`, `## Open Questions`, `## New Risks` headings
- Flag any items present in SESSION-CONTEXT but missing from tracker as "unpromoted"

### Step 2: status-data.json consistency
- If status-data.json exists, check that its `workstreams` or `features` statuses match what's described in the tracker narrative
- Flag mismatches (e.g. tracker says "in progress" but status-data says "not started")

### Step 3: Confluence staleness (lightweight)
- Read `confluence-pages.json` for the current initiative
- For each registered page with a `last_published_hash`, compare against current local file hash
- Flag pages where local content has changed since last publish

### Step 4: Jira delta (only on full reconciliation or if explicitly requested)
- Query `searchJiraIssuesUsingJql` for the initiative's active tickets
- Compare ticket statuses against status-data.json
- Flag any tickets that have moved since last recorded state

## Sync card output

When drift is detected, present a compact sync card:

```
--- Sync Check: [initiative] ---
Unpromoted items: 2 (1 decision, 1 open question)
Status-data drift: PROJ-4275 is "Done" in Jira but "In Progress" in status-data
Confluence stale: 1 page (status page, last published 3 days ago)

Options:
  [Approve all updates] -- write all fixes now
  [Show details] -- expand each item before deciding
  [Defer] -- skip for now, I'll handle it later
  [Just promote items] -- update tracker only, skip Jira/Confluence
---
```

Use AskQuestion to present options. If "Approve all", execute all writes. If "Show details", expand each item with the specific content that would be written.

## Automated state cascade

When a sync gate fires and detects unpromoted items (Step 1), the agent SHOULD auto-promote them  -  **unless** the user is in a `/validate-state` (report-only) context.

### Auto-promotion rules

1. **Decisions** (`DEC-` or items under `## Decisions`)  -  copy to the tracker's decisions table with the timestamp from SESSION-CONTEXT. If no timestamp exists, use the file modification time.
2. **Risks** (`RISK-` or `## New Risks`)  -  add to tracker's risk table.
3. **Open questions** (`OQ-` or `## Open Questions`)  -  add to tracker's unknowns section.
4. **Actions** (`ACT-`)  -  add to tracker's actions section.
5. **Dependencies** (`DEP-`)  -  add to tracker's dependencies section.

After promotion, add a `[promoted]` tag to the item in SESSION-CONTEXT so it is not promoted again.

### When NOT to auto-promote

- During `/validate-state` (read-only mode)  -  report only, let the user choose
- If the item's content is ambiguous or incomplete  -  flag it for review instead
- If the tracker section doesn't exist yet  -  create it, but flag this as a structural addition

## Action runthrough (part of `/wrap`)

Canonical store: `_workstream/ba-actions.json`. Human view: `_workstream/ba-actions.md` (regenerate before the runthrough; never hand-edit).

### 5a. EOD critical scan (before one-by-one walk)

Read `ba-actions.json` and `ba-actions.md`. **Surface first** (callout table in chat, before AskQuestion):

| Bucket | Rule |
|--------|------|
| **Overdue** | `due` before closeout date and status still `open` / `in_progress` / `blocked` |
| **Due today** | `due` equals closeout date and not `done` / `cancelled` |
| **Remind today** | `remind_on` equals closeout date and status still active |
| **High + due within 2 working days** | `priority: high` and due soon  -  flag if the BA said she would finish today and has not |

Say plainly what is still open that [BA name] committed to by end of day. Do not bury this inside the full list.

### 5b. One-by-one walk (every open action)

Walk **every** action in `ba-actions.json` with status `open`, `in_progress`, or `blocked`, **highest urgency first** (overdue → due today → remind today → high → medium → low). For each action:

1. Present task text, initiative, due, status, and `reminder` text (if any) via **AskQuestion** with options:
   - **Done**  -  mark `done`, clear `remind_on` if set
   - **In progress**  -  update notes; keep or set `remind_on` if needed
   - **Follow up**  -  stays open; capture who/when in `notes`; optional new `remind_on` + `reminder`
   - **Move deadline**  -  ask for new date; update `due` and/or `remind_on`
   - **Cancel**  -  mark `cancelled` with reason in `notes`
   - **No update**  -  leave as-is
2. Write changes to `ba-actions.json` immediately after each answer (or batch at end of a group if the user prefers speed  -  but never skip the question).
3. If the user surfaces new actions during the runthrough, insert with next `JA-NNN` via `/todo` rules or direct JSON upsert.

After the runthrough, regenerate `ba-actions.md`, print `Gate: ba-actions-sync: PASS/FAIL`, present a summary table of changes, then proceed to step 6 (promote).

This pattern works because:
- EOD critical scan catches commitments before the long tail
- One-by-one AskQuestion forces structured review at end of day
- It captures verbal context and turns it into formal state updates
- It naturally identifies new actions and follow-ups

## Full end-of-day closeout sequence (`/wrap`, canvas End of Day button)

The Action runthrough above and the sync gate procedure cover the core of `/wrap`, but the full closeout  -  also what the workboard canvas's "End of Day" button triggers, keep both in sync  -  runs these steps in order:

1. **Downloads check.** Run `cmd /c dir "[Downloads folder - set BA_DOWNLOADS_PATH]" /a-d /o-d`  -  never `Get-ChildItem` or PowerShell/.NET enumeration (see `ba-assistant/references/workspace-operations.md`). Check ALL file types newer than the last known session timestamp, not just `.docx`. Triage by extension (docx → extract + debrief, pdf → read + assess relevance, images → check filename/context, spreadsheets → check relevance, installers/zips/lnk/ini → skip). Process anything relevant into the matching initiative's SESSION-CONTEXT.md.
2. **Meeting reconciliation.** Read `_workstream/calendar-feed.json`. For each meeting today that involved other people (skip solo blocks), check whether its initiative/topic has a same-day SESSION-CONTEXT.md entry. Present a reconciliation table (`Time | Meeting | Initiative | Captured?`), then list only the uncaptured ones.
3. **Per-meeting targeted recall.** For each uncaptured meeting, ask via AskQuestion: "[Time] [Meeting name]  -  any decisions, actions, commitments, or risks from this one?" (options: "Nothing to capture" / "Yes  -  let me tell you"). Write anything surfaced to the relevant SESSION-CONTEXT.md with a dated header and a `📝 Captured` tag. Finish with a catch-all: "Anything else from today  -  side conversations, Slack decisions, hallway agreements  -  that didn't happen in a formal meeting?"
4. **Full-file state validation across all initiatives.** For each initiative, read the **entire** SESSION-CONTEXT.md (not just the tail) and initiative-tracker.md, and check status-data.json consistency. Report drift with specific item IDs and counts (this is a deeper pass than the Quick sync check above, which only scans for sync markers).
5. **Action runthrough**  -  as described above.
6. **Promote unpromoted items**  -  per the Automated state cascade rules above, tagging each with `[promoted]`.
6b. **Sync BA actions**  -  run `sync-ba-actions` per `references/ba-actions-format.md` §3: upsert BA-owned rows from today's debriefs, SESSION-CONTEXT captures, and initiative tracker action registers; then **`py _workstream/regenerate-ba-actions-md.py`** (full MD derive from JSON  -  never hand-edit MD); print `Gate: ba-actions-sync: PASS/FAIL`. This step closes the debrief→tracker→[BA name]-list gap.
7. **Refresh `_workstream/workboard.json`**  -  initiative status updates (score per `references/workboard-format.md`  -  do not default to `on-track`), milestone `days_out` recalculated from today's date, `last_refreshed` updated, today's meetings marked done. BA personal task counts come from `ba-actions.json`, not legacy `personal_tasks[]`.
8. **Rewrite `canvases/ba-workboard.canvas.tsx`** with the refreshed data  -  same layout, Update button, and End of Day button, both preserved with their prompts.
9. **Next-working-day prep.** Determine the next working day (skip Sat/Sun)  -  unless critical meetings remain later today, in which case prep for the rest of today first. Read `calendar-feed.json` for that day and summarise: meetings (highlight critical ones), top priority tasks, prep items.

   **Morning prep from BA actions (mandatory):** Read `_workstream/ba-actions.json` and `_workstream/ba-actions.md`. Surface:
   - **`remind_on` on the next working day** (or overdue) where status is still `open` / `in_progress` / `blocked`
   - **High-priority actions due that day**
   - **Blocked items** that need a nudge before first meeting

   Present as **Reminders (commitments to start)** with date, task, and `reminder` text. Suggest the best opening move (one concrete first action before standup).
10. **New-thread handoff prompt (mandatory `/wrap` output).** End every `/wrap` with a **copy-paste-ready** block the user can drop into a **new chat** to resume without re-explaining context. Not a one-liner. Use the template below and fill every section from the session you just closed.

### New-thread handoff prompt template (step 10)

Present under heading **`## New thread  -  copy from here`**. Structure:

```
Sample Initiative resume  -  [day date]  -  [one-line goal for the session]

**Initiative:** [slug and full name, or cross-initiative if applicable]

**Where to start (first action):**
[Single concrete first move, e.g. send PT-105 draft, continue HLR-06 interrogation]

**Then:**
[Ordered list of 2–4 next actions with dates/deadlines]

**Reminders (commitments to start):**
- [Remind on date] [Task]  -  [reminder text] (due [date] if different)
[Include every open action where remind_on is today, tomorrow, or overdue; omit if none]

**Skills to load:**
- [e.g. ba-assistant orchestrator, ba-requirements-interrogator for Mode 4 HLR Q&A]
- [others only if needed this session]

**Canonical files (read before acting):**
- [absolute or workspace paths for SESSION-CONTEXT.md tail, initiative-tracker.md, active artefact e.g. requirements-register.md]
- [kickoff/summary files if relevant]

**Session state (do not re-litigate unless I say):**
- [HLR / phase status table or bullet summary]
- [Open gates: e.g. HLR-05 stays proposed until Sally/[Team Member] after spike]
- [Drift flags: e.g. status-data.json stale  -  regenerate before /status or publish]

**Process reminders for this thread:**
- [Mode 4 rules, interrogation closure ceremony, scope bullet standard, etc.  -  only what applies next]

**Today's meetings:** [count + critical names/times from calendar-feed.json]

**Open blockers:** [top 3]

**Do not:** [e.g. mark HLR-05 interrogated without executive decision; skip Q&A before register writes]
```

Keep the block self-contained so a fresh agent can execute without reading the prior thread. If multiple initiatives were active, lead with the primary initiative and note cross-initiative items in **Then**.

**Short opener (optional second line):** After the full block, you may add one sentence: "Suggested first message if you prefer minimal paste: …"

## What NOT to sync-gate

- Do not run sync gates on every single message (that's what inline capture is for)
- Do not block the user from working if sync is out of date -- always offer "defer"
- Do not auto-write without approval (except inline capture to SESSION-CONTEXT, which is already approved by design)
- Do not run Jira MCP calls on every sync gate -- only on full reconciliation or when the user asks

## Integration with other rules

- `execution-router.mdc`: On BA-resume, the router already reads state files. After reading, if the re-entry card shows sync issues, mention them but don't block.
- `ba-state-validator`: The full State Validator is the "heavy" version of this. Sync gates are the "light" version that runs at breakpoints. They share the same mental model but sync gates skip the cross-document deep diff.
- `ba-context-capture`: Context Capture is Layer 1. It writes to SESSION-CONTEXT. Sync gates (Layer 2) check whether those writes have been promoted to the tracker.

## Canonical file hierarchy (for conflict resolution)

If two files disagree, the canonical source wins:

1. **initiative-tracker.md** -- canonical for narrative RAID, decisions, requirements
2. **status-data.json** -- canonical for structured ticket/workstream data (should reflect Jira)
3. **SESSION-CONTEXT.md** -- scratch space, gets promoted to tracker
4. **ba-actions.json** -- canonical for BA personal/coordinated actions; `ba-actions.md` is derived
5. **workboard.json** -- derived from all initiative trackers + Jira + calendar; initiative `status` scored per `references/workboard-format.md`
6. **Confluence pages** -- derived from local files, published on command
7. **Canvas / HTML snapshots** -- derived from status-data.json and ba-actions (display subset), regenerated on demand

When in doubt: tracker > status-data > SESSION-CONTEXT > everything else.

