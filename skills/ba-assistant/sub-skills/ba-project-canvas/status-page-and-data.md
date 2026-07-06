# Data tasks and status page publication
<!-- Wave 10: moved verbatim from SKILL.md. This is the "Data Model section" that
     HK-CANV-DATA-internal and HK-SV-CANV-refresh route to. -->

## Data model

See `references/canvas-data-model.md` for the canonical schema,
workstream state transition rules, metric computation rules, and
canvas tab structure.

### Data tasks (formerly ba-status-data-model)

**1. Create or update `status-data.json`** — When `/status` or `/publish-status` is invoked:
- If `status-data.json` does not exist, create it from the current state (SESSION-CONTEXT, Jira, open-questions, etc.).
- If it exists, read it and update only the fields that have changed.
- Always invoke `ba-jira-sync` before updating ticket statuses.
- Compute `daysOverdue` for each blocker by comparing `targetDate` to today's date.
- Compute `ageDays` for each open action and unknown.

**2. Feed downstream outputs** — After `status-data.json` is updated, these outputs read from it:
- `ba-project-canvas` → `.canvas.tsx` (this skill)
- `status-snapshot.html` (this skill)
- Status Page Standard Format (in `jess-ba-profile.mdc`) → Confluence markdown body

**Change the data once, regenerate all three outputs.**

**3. Date-aware status computation** — For blockers and critical path items with `targetDate`:
| Condition | Computed status |
|---|---|
| targetDate is null | Use manually set status |
| targetDate > today + 3 days | `pending` or `in-progress` (as set) |
| targetDate is within 3 days | `imminent` — flag in outputs |
| targetDate = today | `due-today` — flag prominently |
| targetDate < today | `overdue` — auto-escalate per `ba-risk-and-tracker` rules |

**4. Validation before output** — Before any output is generated, validate:
- Every ticket in `tickets[]` has been synced within the last 24 hours (check `lastJiraSync`).
- Every blocker has an `owner`.
- Every critical path item with status `in-progress` has a `date`.
- No decision has `status: "TBC"` for more than 7 days without being logged as a risk.
- Every requirement in `delivered` state has linked tickets all marked Done.
- Tickets in `In Progress` with `moscowFlag: missing` surface a warn-and-flag entry.

**5. Migration for existing initiatives** — For initiatives that already have status outputs but no `status-data.json`:
- Read SESSION-CONTEXT.md, open-questions.md, confluence-pages.json, and the latest Confluence status page.
- Extract structured data and populate `status-data.json`.
- This is a one-time migration — after that, `status-data.json` is the source of truth.

### Data anti-patterns to prevent

- **Never update a downstream output directly without also updating `status-data.json`** — if someone asks to change a status, update the JSON first, then regenerate.
- **Never add a ticket to `status-data.json` without a Jira key** — all tickets must be traceable.
- **Never skip the Jira sync** — stale ticket data is worse than no data.
- **Never store computed fields** (`daysOverdue`, `ageDays`, `moscowFlag`) — recalculate on every read so they're always current.
- **Computing a metric as 0% when data is missing.** If a metric can't be computed, show `n/a`. Fabricated zeros look like real signals and trigger false alarms.
- **Caching metrics longer than 1 hour.** Stale metric values create false confidence. Recompute on every status output.

### Status page output (Wave 7)

Status page publication lives in this skill (there is no separate `ba-status-page-publisher` sub-skill).

#### Standards used

- `references/status-page-format.md` — page structure, section ordering, outcome health gate, supersede protocol
- `references/raid-format.md` — RAID rendering on the status page
- `references/canvas-data-model.md` — source data (status-data.json and metrics-cache.json)

If standards conflict with skill-specific guidance below, the standard wins.

#### Output format
Status pages conform to `references/status-page-format.md`. Read that file before publishing any status page. The format is the authoritative source.

