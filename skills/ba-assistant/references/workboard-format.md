# Workboard Format Standard

**Location:** `~/.cursor/skills/ba-assistant/references/workboard-format.md`
**Owner:** `/workboard` procedure (`skills-routing.mdc`), this standard (format)
**Last reviewed:** 2026-09-04 (Workboard Control Centre)

Canonical source for cross-initiative workboard status scoring, `workboard.json` initiative fields, and canvas display rules. Any `/workboard` refresh or `/wrap` workboard update MUST apply this standard. Do not default every initiative to `on-track`.

**Related but different:** per-initiative **milestone** status inside `status-data.json` uses `on-track | at-risk | missed | complete` (see `references/canvas-data-model.md`). Workboard **initiative** status is a separate enum with additional values (`new`, `monitoring`, `closed`). Do not conflate the two.

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

---

## 2. Scoring rules (mandatory on every refresh)

Apply in order. **Escalate to the strictest status that matches**  -  do not downgrade because of recent partial progress.

1. **Missing original target date → at least `at-risk`.** If the initiative missed a previously agreed milestone (e.g. end-June delivery, go-live date) and has not formally re-baselined with a new credible plan, score `at-risk` even if recent tickets moved or a session produced good decisions.

2. **Live/post-go-live → `monitoring`, not `on-track`.** Once core delivery is in production, BA work is operational follow-through (scorecards, handoffs, follow-on tickets). Use `monitoring` until the initiative is formally closed out.

3. **GTM-only monitoring with no build → `closed`.** Pattern: regulatory/enforcement live, monitoring period complete, no active engineering. Residual ops obligations (reporting, ownership questions) do not keep the initiative `on-track`.

4. **`on-track` requires named owners on the next 2 weeks of critical path.** If the next fortnight's must-do items (from tracker, SESSION-CONTEXT, or milestone table) lack a named owner, the initiative cannot be `on-track`. Score `at-risk` instead.

5. **`critical` is rare.** Reserve for: compliance/go-live this week with no owner and no mitigation, or a blocker that will miss a hard external deadline with no fallback. Do not use for a long backlog of unowned actions alone  -  that is `at-risk`.

6. **When in doubt between `on-track` and `at-risk`, choose `at-risk`.** Conservative scoring is intentional. Optimism belongs in narrative (`next_action`), not the status field.

---

## 3. Decision flow (apply per initiative on refresh)

```
START
  │
  ├─ No blueprint / pre-kick-off only? ──────────────────────────► new
  │
  ├─ Core delivery complete, no active BA track? ────────────────► closed
  │     (ops obligations OK to remain)
  │
  ├─ Live in production, follow-through only? ───────────────────► monitoring
  │
  ├─ Go-live/compliance blocked THIS WEEK, no mitigation? ───────► critical
  │
  ├─ ANY of:
  │    • missed original target without re-baseline
  │    • blockers without owners
  │    • key decisions unresolved near deadline
  │    • capacity gap on critical path
  │    • next-2-week critical path items lack named owners
  │                                                              ► at-risk
  │
  └─ Active delivery, credible dates, owners assigned,
     no material slip vs last agreed plan ───────────────────────► on-track
```

Re-read `initiative-tracker.md` (if present) and SESSION-CONTEXT tail before scoring. Status must reflect evidence, not mood.

---

## 4. `workboard.json` initiative fields

Each entry in `initiatives[]`:

| Field | Purpose | Notes |
|-------|---------|-------|
| `slug` | Registry key | Matches initiative folder slug (`initiatives/{slug}/` on this machine; `blueprints/{slug}/` in packaged workspaces) |
| `name` | Display name | Full product/initiative name |
| `phase` | One-line where we are | Phase label + most recent significant event |
| `status` | Initiative health | One of the six enum values above |
| `top_blocker` | Single biggest blocker | `null` if none; plain language, no bare tracker IDs in canvas |
| `top_risk` | Single biggest risk | Material delivery risk, not noise |
| `next_action` | What [BA name] should do next | One paragraph max; actionable |
| `next_milestone` | `{ what, date, days_out }` | Recalculate `days_out` from refresh date |
| `key_dates` | Recent + upcoming dates | Append new; mark done items |
| `last_session` | ISO timestamp | Last significant SESSION-CONTEXT activity |
| `jira_project` | Project key or `null` | For Jira delta step |
| `delivery_progress` | Optional | e.g. "14/14 tickets Done" for monitoring initiatives |

**`sync_status.{slug}`** (sibling object): tracks drift vs tracker, Confluence staleness, `jira_last_synced`, and refresh notes. Not the same as initiative `status`.

### Optional top-level fields (derived on refresh)

| Field | Purpose |
|-------|---------|
| `meetings_today` | Today's meetings for canvas Today tab and EOD reconciliation (`time`, `label`, `sub`, `duration`, `highlight`, `alert`, `done`) |
| `meetings_tomorrow` | Tomorrow's meetings for next-working-day prep |
| `meetings_date` | ISO date the meeting arrays apply to |
| `ba_actions_summary` | `{ open, blocked, overdue, high_due_soon }` counts from `ba-actions.json` |
| `review_queue` | Cross-initiative artefact triage rows (`path`, `priority`, `note`, optional `initiative`) |
| `unprocessed_downloads` | Downloads flagged since last refresh |

Populate from `_workstream/calendar-feed.json` when present; otherwise leave arrays empty and let the canvas show a neutral no-feed callout.

---

## 5. Canvas display rules

File: `canvases/ba-workboard.canvas.tsx`

### Tab contract (mandatory)

| Tab | Purpose |
|-----|---------|
| **Today** | Priority banner, at-risk/urgent callouts, stats, today's meetings, do-first actions, unprocessed downloads |
| **Initiatives** | One full-width card per initiative (single column) with status, phase, milestone, blocker, risk, next action |
| **Open actions** | Editable draft controls per open action (status dropdown, due date, notes) + filters |

**End of Day is a header button, not a tab.** It starts `/wrap`. Do not add an End of day tab — that duplicated the button and confused users.

### Visual rules

- **StatusDot / badge** must support all six enum values: `new`, `on-track`, `at-risk`, `critical`, `monitoring`, `closed`.
- **Colour escalation:** `critical` and overdue/urgent actions → red (`theme.category.red`). `at-risk` initiatives → orange (`theme.category.orange`). Do not use amber/brown for in-progress delivery.
- Header stat row: count initiatives by status honestly (do not show "4 On Track" when none qualify).
- **Callouts** should reflect status honestly (e.g. multiple at-risk initiatives get a combined warning callout, not only success tones).
- **Update**, **End of Day**, and **Apply action updates** (when draft changes exist) button prompts must reference this file, `workboard-procedure.md`, `references/sync-procedures.md`, and **`_workstream/ba-actions.md`**. Keep all four in sync when the procedure changes.

### Draft overlay (canvas interactivity)

- Canvas edits to actions are **draft-only** in `ba-workboard.canvas.data.json` (`draft-actions` key).
- **Apply action updates** opens a Composer chat with the draft JSON and instructions to validate + write `_workstream/ba-actions.json`, then run `py _workstream/regenerate-ba-actions-md.py`.
- Never treat canvas sidecar state as canonical. Clear drafts on the next canvas regeneration after a successful apply.

---

## 6. Anti-patterns (do not do these)

| Anti-pattern | Why it fails | Fix |
|--------------|--------------|-----|
| Default all initiatives to `on-track` | Hides real delivery risk; workboard becomes useless | Apply decision flow every refresh |
| `on-track` because "we had a good session today" | Sessions produce decisions; they do not erase missed targets or unowned actions | Score on evidence across tracker + Jira + dates |
| `monitoring` while core dev tickets still open | Monitoring means shipped; build means active delivery | Use `at-risk` or `on-track` until go-live |
| `closed` while core scope tickets remain open | Closed means BA delivery track done | Wait until delivery complete or explicitly descoped |
| Conflating milestone status with initiative status | Different enums, different scope | Milestone = one date; initiative = whole programme health |

---

## 7. Worked examples (the BA's initiatives, Jul 2026)

| Initiative | Status | Why |
|------------|--------|-----|
| Sample-Compliance-Initiative | `closed` | Enforcement live, D+7 monitoring complete, no build. Reporting OQs are ops. |
| Sample Initiative | `at-risk` | Many June/July actions without owners; design freeze imminent; Sally walkthrough pressure. Good sessions do not clear this. |
| Data Collection | `at-risk` | Feature A paused; Feature B missed end-June target; pilot forecast Aug. |
| sample-reassessment-initiative | `monitoring` | Live 6 Jul; 14/14 delivery tickets Done. Follow-through: PROJ-4371, scorecard, ops owner. |
| Sardine | `new` | Pre-kick-off only; scope TBD. |

---

## 8. Integration

| Trigger | Load this file |
|---------|----------------|
| `/workboard` | Before writing `initiatives[].status` (step 5b in `skills-routing.mdc`) |
| `/wrap` workboard refresh | Step 7 in `references/sync-procedures.md` |
| Canvas Update / End of Day buttons | Prompt references this file |
| New initiative added to `blueprints/README.md` | Score as `new` until first delivery phase starts |

When this standard changes, update in the same batch: this file, `skills-routing.mdc` workboard row, `references/sync-procedures.md` closeout step 7, `references/ba-actions-format.md`, and canvas button prompts.

---

## 9. BA personal actions (separate from initiative health)

BA-owned tasks are **not** stored in `workboard.json` initiative fields or legacy `personal_tasks[]`.

| File | Role |
|------|------|
| `_workstream/ba-actions.json` | Canonical BA action store |
| `_workstream/ba-actions.md` | Auto-generated human view (open first, closed at bottom) |

Sync procedure: `references/ba-actions-format.md` §3 (`sync-ba-actions`). Triggers: debrief complete, `/todo`, `/wrap` step 6b.

Canvas **Open actions** tab: show open actions with draft controls; curated Today subset = high priority + due within 3 working days (max 15 rows). Full list always in `ba-actions.md`.
