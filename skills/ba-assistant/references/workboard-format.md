# Workboard Format Standard

**Location:** `~/.cursor/skills/ba-assistant/references/workboard-format.md`
**Owner:** `/workboard` procedure (`workboard-procedure.md`) + status scoring (this standard)
**Last reviewed:** 2026-09-25

Canonical source for status scoring, `workboard.json` initiative fields, and canvas display rules. Any `/workboard` refresh or `/wrap` workboard update MUST apply this standard. Do not default every initiative to `on-track`.

**Related but different:** per-initiative **milestone** status inside `status-data.json` uses `on-track | at-risk | missed | complete` (see `references/canvas-data-model.md`). Workboard **initiative** status is a separate enum with additional values (`new`, `monitoring`, `closed`, `archived`). Do not conflate the two.

---

## 1. Initiative status enum (canonical)

Allowed values for `workboard.json → initiatives[].status` and the workboard canvas `StatusDot`:

| Status | Use when | Do not use when |
|--------|----------|-----------------|
| `new` | Pre-kick-off, no blueprint, scope/ownership TBD | Any active delivery work |
| `on-track` | Active delivery, credible dates, owners assigned, no material slip vs last agreed plan | It is the default because nothing bad happened yet |
| `at-risk` | Missed a prior target, blockers without owners, key decisions unresolved near a deadline, or capacity gap (e.g. key person on leave) | One minor open question with a clear owner |
| `critical` | Go-live or compliance blocked this week with no mitigation path | Ordinary backlog noise |
| `monitoring` | Shipped/live; BA work is operational follow-through only | Active build still in flight for core scope |
| `closed` | Delivery initiative complete; ops obligations may remain but no BA delivery track | Dev tickets still open for core scope |
| `archived` | `ba-initiative-closeout` has run: folder moved to `archive/`, no further BA work expected | Initiative is merely quiet/deprioritised but the folder still lives under the active initiatives root |

---

## 2. Scoring rules (mandatory on every refresh)

Apply in order. **Escalate to the strictest status that matches** — do not downgrade because of recent partial progress.

1. **Missing original target date → at least `at-risk`.**
2. **Live/post-go-live → `monitoring`, not `on-track`.**
3. **GTM-only monitoring with no build → `closed`.**
4. **`ba-initiative-closeout` has moved the folder to `archive/` → `archived`, not `closed`.** This is the only status `/workboard` should never assign itself — it's set once, by that skill, as part of the move.
5. **`on-track` requires named owners on the next 2 weeks of critical path.**
6. **`critical` is rare.** Reserve for hard external deadlines this week with no mitigation.
7. **When in doubt between `on-track` and `at-risk`, choose `at-risk`.**

See decision flow in section 3 for the full tree.

---

## 3. Decision flow (apply per initiative on refresh)

```
START
  ├─ ba-initiative-closeout has moved the folder to archive/? ───► archived
  ├─ No blueprint / pre-kick-off only? ──────────────────────────► new
  ├─ Core delivery complete, no active BA track? ────────────────► closed
  ├─ Live in production, follow-through only? ───────────────────► monitoring
  ├─ Go-live/compliance blocked THIS WEEK, no mitigation? ───────► critical
  ├─ Missed target / unowned blockers / capacity gap / etc. ─────► at-risk
  └─ Active delivery, credible dates, owners assigned ─────────────► on-track
```

Re-read `initiative-tracker.md` (if present) and SESSION-CONTEXT tail before scoring.

---

## 4. `workboard.json` initiative fields

Each entry in `initiatives[]`:

| Field | Purpose | Notes |
|-------|---------|-------|
| `slug` | Registry key | Matches initiative folder slug |
| `name` | Display name | Full product/initiative name |
| `phase` | One-line where we are | Phase label + most recent significant event |
| `status` | Initiative health | One of the six enum values above |
| `top_blocker` | Single biggest blocker | `null` if none; plain language |
| `top_risk` | Single biggest risk | Material delivery risk |
| `next_action` | What [BA name] should do next | One paragraph max |
| `next_milestone` | `{ what, date, days_out }` | Recalculate `days_out` from refresh date |
| `key_dates` | Recent + upcoming dates | Append new; mark done items |
| `last_session` | ISO timestamp | Last significant SESSION-CONTEXT activity |
| `jira_project` | Project key or `null` | For Jira delta step |
| `delivery_progress` | Optional | e.g. "14/14 tickets Done" |

**`sync_status.{slug}`** tracks drift vs tracker and Jira sync timestamps.

### Optional top-level fields

| Field | Purpose |
|-------|---------|
| `meetings_today` / `meetings_tomorrow` / `meetings_date` | Calendar snapshot for Today tab and EOD |
| `ba_actions_summary` | `{ open, blocked, overdue, high_due_soon }` from `ba-actions.json` |
| `stakeholder_raise` | Optional stakeholder prep (`name`, `meetingNote`, `items[]`) |
| `review_queue` | Cross-initiative artefact triage rows |
| `unprocessed_downloads` | Downloads flagged since last refresh |

Populate meetings from `_workstream/calendar-feed.json` when present.

---

## 5. Canvas display rules

File: `canvases/ba-workboard.canvas.tsx` (from `templates/ba-workboard.canvas.tsx.template`)

### Tab contract

| Tab | Purpose |
|-----|---------|
| **Today** | Focus callout, calendar timeline, read-only priority queue with staging checkboxes, downloads |
| **Initiatives** | Full-width initiative cards |
| **Open actions** | Editable drafts (status, due, notes) |
| **Stakeholder raise** | Optional when `stakeholder_raise.name` is set and open items exist |

**End of Day** is a header button (starts `/wrap` via embedded prompt), not a tab.

### Interaction rules

- **Update**, **End of Day**, **Save staged updates**, **Discard unsaved changes**
- Today checkboxes stage `done` until **Save staged updates** writes `ba-actions.json`
- Prompts injected by `generate-workboard-canvas.py` into `DATA.prompts`

---

## 6. Anti-patterns

| Anti-pattern | Fix |
|--------------|-----|
| Default all initiatives to `on-track` | Apply decision flow |
| One-line Update / End of Day prompts | Regenerate from portable template |
| Treat canvas drafts as canonical | Apply through actions JSON + regenerate MD |

---

## 7. Personal actions

| File | Role |
|------|------|
| `_workstream/ba-actions.json` | Canonical store |
| `_workstream/ba-actions.md` | Derived view |

Sync: `ba-actions-format.md` section 3 (`sync-ba-actions`).

---

## 8. Integration

Update in the same batch when this changes: this file, `workboard-procedure.md`, `sync-procedures.md`, `ba-actions-format.md`, and regenerate canvases.
