# [BA name] Actions  -  canonical personal task store

**Location:** `~/.cursor/skills/ba-assistant/references/ba-actions-format.md`  
**Canonical data:** `_workstream/ba-actions.json`  
**Human view (derived, do not hand-edit):** `_workstream/ba-actions.md`  
**Last reviewed:** 2026-07-20

BA-owned and [BA name]-coordinated actions live here. Initiative trackers remain the team RAID; this file is **the BA's working list only**.

---

## 1. Why JSON + derived MD (not MD-only or workboard-only)

| Layer | File | Role |
|-------|------|------|
| **Canonical** | `_workstream/ba-actions.json` | Structured store agents read/write; stable IDs; upsert on sync |
| **Derived** | `_workstream/ba-actions.md` | Regenerated on every sync; open first, closed at bottom; [BA name] reads this |
| **Display** | `canvases/ba-workboard.canvas.tsx` | Curated subset (high + due-soon) for cross-initiative dashboard |
| **Team RAID** | `blueprints/{slug}/initiative-tracker.md` | Everyone's actions; [BA name] rows **feed** ba-actions on sync |

**Do not** maintain dated snapshot MD files (e.g. `ba-active-actions-snapshot.md`) as the working list. Use them only for one-off audits, then retire.

**Deprecated (do not add new items):**
- `workboard.json  ->  personal_tasks[]` (legacy `PT-*`; groom separately)
- `workboard.json  ->  ba_active_focus` (merged into ba-actions.json Jul 2026)

---

## 2. Schema (`ba-actions.json`)

```json
{
  "schema_version": 1,
  "last_synced": "ISO-8601",
  "last_generated_md": "ISO-8601",
  "next_id": 29,
  "actions": [
    {
      "id": "BA-001",
      "task": "Plain-language task description",
      "initiative": "Sample Initiative",
      "raised": "2026-07-20",
      "due": "2026-07-21",
      "status": "open",
      "priority": "high",
      "blocked": false,
      "blocker_notes": null,
      "source": {
        "type": "debrief",
        "label": "MoSCoW 20 Jul",
        "file": "blueprints/Sample Initiative/debriefs/sample-workshop-debrief.md",
        "date": "2026-07-20"
      },
      "tracker_ref": "A-252",
      "notes": "Optional context",
      "last_updated": "ISO-8601"
    }
  ],
  "watching": [
    {
      "id": "JW-001",
      "task": "What someone else owns that [BA name] tracks",
      "owner": "[Team Member]",
      "initiative": "Sample Initiative",
      "due": "2026-07-24",
      "source": { "type": "debrief", "label": "MoSCoW 20 Jul", "date": "2026-07-20" },
      "notes": null
    }
  ]
}
```

### Field rules

| Field | Required | Values / notes |
|-------|----------|----------------|
| `id` | Yes | `BA-NNN` sequential; never reuse |
| `task` | Yes | Plain language; no bare tracker codes in task text |
| `initiative` | No | Slug (`Sample Initiative`, `Data Collection`, `sample-reassessment-initiative`) or `null` |
| `raised` | Yes | ISO date action first captured |
| `due` | No | ISO date or `null` |
| `status` | Yes | `open`, `in_progress`, `done`, `cancelled`, `blocked` |
| `priority` | Yes | `high`, `medium`, `low` |
| `blocked` | Yes | Boolean; if true, set `status` to `blocked` or `open` with `blocked: true` |
| `blocker_notes` | No | Why blocked |
| `source.type` | Yes | `debrief`, `tracker`, `session`, `quick-capture`, `wrap` |
| `source.label` | Yes | Human-readable origin (meeting name + date) |
| `source.file` | No | Relative path to debrief or artefact |
| `source.date` | Yes | ISO date of source event |
| `tracker_ref` | No | Internal link to tracker action row for sync only |
| `notes` | No | Extra context |
| `remind_on` | No | ISO date to **start** or be nudged on this task (separate from `due`; used in `/wrap` and re-entry) |
| `reminder` | No | Short nudge text shown on `remind_on` (plain language; what to do when the date hits) |
| `last_updated` | Yes | ISO timestamp of last write |

### Status semantics

- **`open`:** Not started
- **`in_progress`:** Started, not finished
- **`blocked`:** Cannot proceed (also set `blocked: true` and `blocker_notes`)
- **`done`:** Complete
- **`cancelled`:** No longer needed

**Never** auto-reopen `done` or `cancelled` without user confirmation.

---

## 3. Sync procedure (`sync-ba-actions`)

Run after **every meeting debrief write**, **`/todo` capture**, **`/wrap` step 6b**, and **`/done`** status change.

### 3.1 Collect candidates (same calendar day + unpromoted backlog)

For each active initiative touched:

1. **Debriefs**  -  Read debrief action tables where Owner contains `[BA name]` or `Gibson`.
2. **Tracker**  -  Read `initiative-tracker.md` action register where Owner is [BA name] (or [BA name] coordinates).
3. **SESSION-CONTEXT**  -  Scan today's dated entries and unpromoted `📝 Captured` lines for the BA commitments not yet in ba-actions.
4. **Quick capture**  -  Items added via `/todo` in this session (already in JSON; skip duplicate insert).

For **`/wrap`**, also scan debriefs dated **today** across all initiatives.

### 3.2 Upsert rules

1. **Match order:** `tracker_ref` (if present)  ->  normalized task fingerprint (lowercase, strip punctuation, first 80 chars)  ->  fuzzy match on same initiative + due within 2 days.
2. **Insert** if no match: assign next `BA-NNN`, set `raised` to source date (or today if unknown).
3. **Update** if match: refresh `due`, `source`, `notes`, `tracker_ref`; do **not** overwrite `status` if already `done`/`cancelled`.
4. **Priority default:** `high` if due within 2 working days; `medium` if due within 2 weeks; `low` otherwise; bump to `high` if `blocked`.
5. **Watching:** Upsert `JW-*` from debrief actions owned by others that [BA name] explicitly tracks (MoSCoW chase items, etc.).

### 3.3 Regenerate markdown (mandatory, full derive  -  never hand-edit)

**Hard rule:** `_workstream/ba-actions.md` is **always** produced by a **full regenerate** from `ba-actions.json`. After **every** JSON write (`/todo`, `/done`, action runthrough, debrief sync, `/wrap` 6b), run:

```text
py _workstream/regenerate-ba-actions-md.py
```

(or regenerate the entire MD in the same agent turn using the same rules below  -  **never** patch sections by hand, never a "top priority" subset that omits closed rows, never stale rows left in Open after status  ->  `done`).

Script: `_workstream/regenerate-ba-actions-md.py` (canonical implementation of this section).

Output structure:

1. Header: last synced timestamp, open count, blocked count, overdue count, closed count.
2. **Reminders**  -  all open/in_progress/blocked actions where `remind_on` is set, grouped **Overdue**  ->  **Today**  ->  **Tomorrow**  ->  **Upcoming** (relative to sync date). Columns: Task | Reminder | Due. Mandatory; if none, show "No start-by reminders set."
3. **Open actions**  -  **every** open/in_progress/blocked row from JSON (not a curated subset). Sort: `blocked` first, then `priority` (high  ->  low), then `due` (nulls last), then `raised`.
4. **Watching**  -  table of others' items [BA name] tracks.
5. **Closed actions**  -  `done` and `cancelled`, most recently updated first (cap display at 30 with overflow note).

When the user says "remind me today/tomorrow/Friday" during action updates or `/todo`, set `remind_on` + `reminder` (do not bury in `notes` only). Clear `remind_on` when the reminder fires and work has started (`in_progress`) or the task is done/cancelled.

Use plain language in the MD body (no bare `BA-*` in task rows; IDs OK in a narrow ID column for `/done BA-012`).

**Validation:** After regenerate, Open table must contain **exactly** the JSON rows where `status` ∈ {open, in_progress, blocked}. Closed rows must **not** appear under Open. Print `Gate: ba-actions-md-regen: PASS`.

### 3.4 Workboard canvas hook

After sync, refresh canvas embedded open actions from `ba-actions.json` where `priority === high` OR due within 3 working days (cap at 15 rows for Today tab subset). Update callout to point at `_workstream/ba-actions.md`.

**Draft overlay:** The Open actions tab may hold unsynced edits in `ba-workboard.canvas.data.json`. On **Apply action updates**, follow `workboard-procedure.md → Canvas draft apply procedure`. Never write canonical JSON from canvas code directly.

### 3.5 Validation line (visible)

After sync, print: `Gate: ba-actions-sync: PASS (N open, M added, K updated)` or `FAIL` with reason.

---

## 4. Integration map

| Trigger | Step |
|---------|------|
| `ba-meeting-debrief` task 10 | Replace old `personal_tasks` write with `sync-ba-actions` |
| `/todo`, `/done` | Read/write `ba-actions.json`; regenerate MD |
| `/wrap` step 5 | EOD critical scan + one-by-one AskQuestion runthrough (see `sync-procedures.md` §5a–5b) |
| `/wrap` step 6b | Full sync after tracker promotion (step 6) |
| `/workboard` step 5 | Read open counts from ba-actions for "High tasks" stat |
| `/workboard` step 8 | **Morning prep scan:** surface `remind_on` + high-priority due tomorrow (see `sync-procedures.md` step 9) |
| `/todo list` | List from ba-actions.json, not personal_tasks |
| Canvas **Update** button | Same morning-prep scan when refresh runs start-of-day |
| Canvas **End of Day** button | Full `/wrap` including ba-actions EOD critical scan + runthrough |
| Canvas **Apply action updates** | Validates draft patches from canvas sidecar → writes JSON → `py _workstream/regenerate-ba-actions-md.py` |

---

## 4b. EOD and daily update behaviour

### End of day (`/wrap`, canvas End of Day)

1. Regenerate or read `ba-actions.md` so counts are current.
2. Run **EOD critical scan** (`sync-procedures.md` §5a): overdue, due today, remind today, high items the BA said she would finish today.
3. Present critical items in a callout **before** meeting reconciliation or initiative validation.
4. Walk **every** open action one-by-one with AskQuestion (§5b options: Done, In progress, Follow up, Move deadline, Cancel, No update).
5. After runthrough + step 6b sync, the handoff block (step 10) must include **Reminders (commitments to start)** from `remind_on` / due tomorrow.

### Daily update (`/workboard`, canvas Update)

When the user runs a morning or mid-day refresh (not full `/wrap`):

1. Read `ba-actions.json` + `ba-actions.md`.
2. Surface **first-thing priorities:**
   - `remind_on` today or overdue (active status)
   - High priority due today or tomorrow
   - Blocked items with meetings today that could unblock them
3. Optionally run a **short** AskQuestion pass on today's remind/due items only (same options as §5b) if the user has not closed out since yesterday.
4. Embed the curated subset in canvas `OPEN_TASKS` (high + due within 3 working days, max 15 rows). Full list always linked to `ba-actions.md`.

---

## 5. Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| Debrief writes tracker only | Always run `sync-ba-actions` before debrief complete |
| Hand-editing `ba-actions.md` | Edit JSON or use `/todo`; run `regenerate-ba-actions-md.py` |
| Partial MD update / stale Open rows | **Always** full regenerate from JSON after every write; Open table = exact JSON filter |
| Dated snapshot MD as working list | One rolling `ba-actions.md` |
| Canvas as canonical store | Canvas is display only |
| Duplicate in personal_tasks + ba-actions | New items  ->  ba-actions only |

---

## 6. Migration note (Jul 2026)

Initial population from `workboard.json  ->  ba_active_focus` (28 actions + 9 watching). Legacy `personal_tasks[]` remains for historical PT IDs; groom stale open rows in a separate session.
