﻿---
name: ba-state-validator
description: >
  Cross-document state validation for BA initiatives. Detects drift between canonical state files
  (initiative-tracker.md, status-data.json, SESSION-CONTEXT.md) and downstream artefacts (canvas,
  HTML snapshot, Confluence pages, project hub). Produces a divergence report and optionally
  propagates updates. Runs on demand via `/validate-state`, as Step 1 of the session resume flow,
  before `/publish-status`, and at end of any session where canonical state was modified.
---

# Skill: State Validator

## Description

The State Validator skill solves the cross-document staleness problem: a fact gets updated in one
place (e.g. a milestone date pushes back in initiative-tracker.md) but doesn't propagate to every
artefact that references it (canvas, HTML, status page on Confluence, project hub, SESSION-CONTEXT).
The result is that future work references stale values and the BA ends up re-correcting the same
date across multiple files in subsequent sessions.

This skill detects divergences across canonical state files and downstream artefacts, reports them
in a single table, and propagates updates on user confirmation. It is **read-mostly** by default,
never auto-edits without explicit per-divergence approval.

> **Cross-cutting rule:** Before producing a propagation plan, apply the **"What I'll produce next"
> declaration** rule from `ba-assistant/SKILL.md`. Validation is read-only; propagation is the
> artefact-producing step that needs the user to confirm scope.

## When to invoke

- **`/validate-state`** on demand
- **Step 1 of Session Resume** â€” catch drift before the user resumes work (silent unless divergences found)
- **Before `/publish-status`** â€” prevent publishing stale derivatives to Confluence
- **At session end** â€” offer to validate before wrapping, especially if status-data.json or tracker was modified this session
- **After any requirement change** â€” when a requirement changes mid-flight, dates and dependencies often need to propagate; this skill catches the cases where they didn't
- **When the user says "is everything up to date" or "did that propagate"** â€” natural language trigger

## Canonical ownership reference

This skill enforces the canonical ownership policy documented in `ba-assistant/SKILL.md â†’
Canonical ownership`. Quick reference:

| Fact type | Canonical source |
|---|---|
| Narrative RAID, decisions, assumptions, OQs, dependencies | `initiative-tracker.md` |
| Structured RAID (IDs, owners, dates as data) | `status-data.json` (derived from tracker) |
| Ticket statuses | `status-data.json` (synced from Jira) |
| Workstream states per scope | `status-data.json` |
| Confidence scores | `status-data.json` |
| Sponsor / PM / Tech Lead names, pmApproval state | `status-data.json â†’ initiative` |
| Sprint context (day number, dates, days to deadline) | `status-data.json â†’ sprintContext` (derived from calendar + tracker metadata) |
| Session-scoped working memory | `SESSION-CONTEXT.md` (never canonical for facts that outlive the session) |

## Mandatory hooks

| Hook | When | Why |
|---|---|---|
| **ba-jira-sync** | Before validation | Refresh ticket statuses so Jira-derived facts in status-data.json are current before comparison |
| **ba-project-canvas (Data Model section)** | Before validation | Refresh status-data.json from tracker so structured view matches narrative source |
| **Anti-Pattern Detector** | After validation | Log every divergence type observed so patterns can promote to the watchlist |
| **Communication_Drafter** (in Playback) | If divergences include Confluence pages that need superseding | Draft the supersede banner content |

## Tasks

### 1. Establish the validation context

Read the project's analysis folder and identify every live artefact. Default set:

- `initiative-tracker.md`
- `status-data.json`
- `SESSION-CONTEXT.md`
- `SESSION-CONTEXT.team.md` (if it exists â€” team-facing extract)
- `Project-hub.md`
- `confluence-pages.json` (page registry)
- `superseded-pages.json` (if it exists)
- `<initiative-slug>.canvas.tsx` â€” see **Canvas discovery** below
- `status-snapshot.html`
- `learnings.md` (read-only â€” never propagate INTO learnings, only ever read FROM)

Plus, for each entry in `confluence-pages.json` flagged as live (not superseded):

- The Confluence page body (fetch via `getConfluencePage`)

Skip files explicitly marked superseded or archived.

#### Canvas discovery

Canvas files may live **outside** the blueprint analysis folder. Common locations:

1. Inside the analysis folder: `<analysis-folder>/<slug>.canvas.tsx`
2. In the Cursor canvases directory: `<project-folder>/canvases/*.canvas.tsx`
3. In a workspace-level canvases folder

Use `Glob` for `**/*.canvas.tsx` scoped to the workspace to find all canvases. Match by
initiative name, slug, or related keywords (e.g. `analysis-sprint-plan`, `[initiative-slug]-*`).
All matching canvases are downstream artefacts for validation.

#### Team-facing extracts

If `SESSION-CONTEXT.team.md` exists alongside `SESSION-CONTEXT.md`, include it as a downstream
artefact. It mirrors a subset of decisions, knowns, and questions from the tracker â€” and drifts
when the tracker updates but the team file doesn't.

### 2. Refresh upstream sources first

Before comparing, refresh the structured layer from the narrative layer:

1. **Run ba-jira-sync** â€” pull current ticket statuses into status-data.json
2. **Re-derive status-data.json from initiative-tracker.md** â€” for any decision / RAID item / OQ
   present in the tracker but absent or stale in status-data.json, update status-data.json
3. **Log every refresh action** so the user can see what changed before validation runs

This is the source-of-truth alignment step. Without it, the validator would report drift that's
actually correct (tracker has new info; status-data.json is stale; the validator would wrongly
suggest "update tracker to match status-data.json").

### 3. Build the fact registry

For each canonical fact in the upstream sources, record:

- Fact ID (composed from type + key, e.g. `decision:D-04`, `milestone:legal-signoff`)
- Canonical source file
- Canonical value
- Last-modified date (from file mtime or in-file metadata)

Fact types to check:

| Type | Examples |
|---|---|
| Milestones / key dates | Legal sign-off date, launch date, sprint end |
| Sprint day number | `sprintDay: 8` in status-data.json vs `SPRINT_DAY = 7` in canvas |
| Days to deadline | Computed from today's date vs hardcoded values in canvas / HTML / hub |
| Decision dates and owners | "Decided 18 May 2026, owner: [Team Member]" |
| Decision register completeness | Tracker has D-001 to D-103; downstream only shows up to D-088 |
| Knowns / questions register completeness | Same pattern â€” count and last ID |
| Ticket statuses | PROJ-001: In Progress |
| Session completion status | Session shown as "ðŸŸ¡ today" or "M (must attend)" when it's actually "âœ… done" |
| Sponsor / PM / Tech Lead names | Anywhere these names appear |
| pmApproval state | pending / approved / TBC |
| Confidence scores | Each of the 6 |
| Workstream states per scope | Discovery active for Stale Drafts, Delivery active for Quick T2P, etc. |
| Workspace context | Jira project key, Confluence space, parent page ID |
| Version strings | Canvas footer, HTML title, hub "last updated" â€” must reflect current sprint day |

### 4. Scan downstream artefacts for each fact

For every fact in the registry, search every non-canonical artefact for occurrences. Match
flexibly (date formats vary: "6 Jun 2026", "6-Jun-2026", "2026-06-06"). Record:

- Where the fact was found
- What value was found
- Whether it matches the canonical value

#### Canvas-specific scanning

Canvas files (`.canvas.tsx`) contain **hardcoded data** â€” they are not data-driven from
`status-data.json`. This means every fact that changes in canonical sources must be manually
propagated to matching canvas constants. Key locations to scan:

| Canvas element | What to check | Typical variable / location |
|---|---|---|
| Sprint day constant | `const SPRINT_DAY = N` | Top-level constant |
| Days to deadline | `Stat value="N"` for deadline countdown | Overview tab stats, timeline tab stats |
| Overview callout | Callout title text with day number + days to go | `<Callout tone="info" title="...">` |
| Version string | Footer text with last-updated date and day number | `<Text tone="secondary" ...>vX.Y (updated ...)` |
| Critical path entries | Session/milestone statuses (ðŸŸ¡ vs âœ…) | `CRITICAL_PATH` array |
| Attendance data | Planned (`M`) vs actual (`âœ…`) for completed sessions | `W1_ATTENDANCE`, `W2_ATTENDANCE` arrays |
| Risk / blocker tables | Items resolved since last canvas update | `RISKS`, `BLOCKERS` arrays |

Canvases often have the **same fact in multiple locations** (e.g. days-to-deadline appears in
overview stats, timeline stats, callout text, and version string). Use Grep within the file to
find all occurrences before reporting.

#### Confluence page scanning

For each live page in `confluence-pages.json`, fetch the page body via `getConfluencePage` and
scan for fact occurrences. Common divergence sources:

- Status pages with stale milestone dates or decision counts
- FAQ or reference pages with outdated pricing or scope statements
- Pages created during earlier phases that reference superseded decisions

If the Confluence MCP is unavailable, skip and note in the validation report header.

### 5. Build the divergence table

Group results by fact. Only include facts where â‰¥1 downstream artefact has a value that differs
from canonical. Format:

```
State validation â€” <Initiative Name> â€” <timestamp>

Canonical sources refreshed: <list>
Artefacts scanned: <count local files> + <count Confluence pages>
Divergences found: <count>

| # | Fact | Canonical | Found in | Found value | Last modified | Suggested action |
|---|---|---|---|---|---|---|
| 1 | Legal sign-off date | 6 Jun 2026 (tracker) | status-snapshot.html | 30 May 2026 | 23 May, 2:10pm | Regenerate canvas + HTML |
| 2 | Legal sign-off date | 6 Jun 2026 (tracker) | Confluence page 1238472 (Status as at 23 May) | 30 May 2026 | 23 May | Mark page superseded; publish new status page |
| 3 | PROJ-001 status | In Progress (status-data.json, synced from Jira) | SESSION-CONTEXT.md | To Do | 18 May | Update SESSION-CONTEXT.md |
```

If no divergences, output:

```
State validation â€” <Initiative Name> â€” <timestamp>
âœ“ All artefacts aligned with canonical state. Nothing to propagate.
```

### 6. Surface and confirm via AskQuestion

End the validation report with an AskQuestion that lets the user pick per-divergence:

```
Selection per divergence:
[Propagate from canonical] [Update canonical instead â€” the downstream value is correct] [Mark
superseded â€” for historical artefacts] [Skip this one] [Discuss first]

Or for bulk: [Propagate all from canonical] [Review each one] [Skip all â€” just report]
```

### 7. Propagate (only after user confirmation)

For each divergence the user approved for propagation:

- **Local files (tracker, status-data.json, SESSION-CONTEXT.md, project-hub)** â€” edit in place
  using str_replace or equivalent, log the change
- **Canvas (.canvas.tsx)** â€” canvas files contain hardcoded data, not data bindings. For canvases
  driven by `status-data.json` (e.g. a status canvas), invoke ba-project-canvas to regenerate.
  For sprint-plan or other standalone canvases, edit the specific constants and data arrays
  in place (e.g. `SPRINT_DAY`, `CRITICAL_PATH`, attendance arrays, stat values, callout text).
  Use Grep within the canvas file to find all occurrences of the stale value before editing â€”
  the same fact often appears in multiple locations.
- **HTML snapshot** â€” regenerate from refreshed status-data.json via ba-project-canvas, or
  rebuild manually if the HTML is not canvas-derived
- **Confluence pages** â€” for "Status as at X" pages, either:
  - Update the existing page (if it's the current status page) using `updateConfluencePage`
  - Mark superseded by adding a banner at the top via `updateConfluencePage` AND adding the page to
    `superseded-pages.json` so future context gathering skips it
- **Jira tickets** â€” never auto-edit Jira from the validator. If a Jira ticket field disagrees
  with canonical, the validator reports it but the user resolves it manually in Jira

After propagation, run a second-pass scan to confirm all approved divergences are now resolved.

### 8. Update confluence-pages.json and superseded-pages.json

If any Confluence page was marked superseded:

```json
// superseded-pages.json
[
  {
    "pageId": "1238472",
    "title": "Status as at 23 May 2026",
    "supersededOn": "2026-05-30",
    "supersededBy": "1245891",
    "reason": "Replaced by Status as at 30 May 2026"
  }
]
```

The Intake Reviewer and any other context-gathering skill reads this file and skips superseded
pages when collecting context.

### 9. Log to learnings.md (only if a divergence pattern is observed)

If validation runs find the same fact diverging across multiple sessions (e.g. "Legal sign-off date
has drifted 3 times in this initiative"), log to learnings.md as a watchlist item: "<fact> drifts
repeatedly â€” auto-propagate without confirmation, or add a stronger update gate."

Do not log every individual divergence. Only patterns.

### 10. Fire APD hook â€” log divergence types for pattern detection

After validation completes (whether or not propagation was requested), pass the divergence list
to the Anti-Pattern Detector for pattern analysis:

1. **Classify each divergence** into a divergence type:
   - `day-boundary-staleness` â€” sprint day, days-to-deadline, stage label not updated across files
   - `register-incompleteness` â€” decisions/knowns/questions added to tracker but not propagated
   - `session-status-drift` â€” session shown as planned/in-progress when it's actually completed
   - `milestone-date-drift` â€” a key date changed in one place but not others
   - `structural-absence` â€” a required file (status-data.json, confluence-pages.json) doesn't exist
   - `name-or-role-drift` â€” person names or roles changed in one file but not others
   - `confidence-score-drift` â€” scores updated in one source but stale elsewhere

2. **Check if any type has appeared in 3+ validation runs** for this initiative. If so, it's a
   pattern â€” log to `learnings.md` per Task 9.

3. **Pass the type counts to the APD** so it can update its initiative-specific watchlist. The APD
   uses this to calibrate which triggers to watch more aggressively during normal operation.

If this is the first validation run for the initiative, note the divergence types observed but
don't promote to patterns yet â€” a single run doesn't establish a pattern.

## Outputs

| Output | Format | Where it goes |
|---|---|---|
| Validation report | Markdown table in chat | Chat |
| Propagation actions | Edits to local files + Confluence pages | The files themselves |
| Updated confluence-pages.json | JSON | Project analysis folder |
| Updated superseded-pages.json | JSON | Project analysis folder |
| Pattern entries | Markdown rows | learnings.md (only if patterns detected) |

## Failure modes

| Failure | What to do |
|---|---|
| Jira MCP unavailable during pre-refresh | Skip Jira sync; note in validation report that ticket statuses may be stale |
| Confluence MCP unavailable | Skip Confluence pages; validation covers local artefacts only; flag at top of report |
| Tracker and status-data.json disagree on a fact and neither is obviously canonical | Report both with last-modified dates; ask user to pick |
| A fact appears in only one artefact (no comparison possible) | Skip â€” nothing to validate |
| Validation finds >20 divergences in a single run | Surface as "significant drift" warning; recommend full audit pass before propagating |
| Canvas file not found in analysis folder | Run Glob for `**/*.canvas.tsx` across workspace; if found elsewhere, note the path in the report and scan it |
| Canvas has hardcoded data that doesn't map to any status-data.json field | Canvas was built before status-data.json existed or independently; compare against initiative-tracker.md directly |
| SESSION-CONTEXT.team.md exists but isn't in the default artefact list | Include it â€” it drifts when the tracker updates but the team extract doesn't |

## Output anti-patterns to prevent

- **Auto-propagating without user confirmation** â€” even for trivial-looking divergences, never write without explicit per-divergence approval
- **Treating SESSION-CONTEXT.md as canonical** â€” facts in SESSION-CONTEXT.md are session-scoped working memory; if a fact there disagrees with the tracker, the tracker wins (unless the user explicitly tells the validator that SESSION-CONTEXT.md has the latest update â€” they then promote it to the tracker)
- **Validating against stale upstream** â€” always run the Step 2 refresh before comparing, or the validator will report drift that's actually correct
- **Treating Confluence pages older than the current status page as live** â€” pages flagged as superseded in superseded-pages.json are ignored
- **Editing Jira from the validator** â€” Jira is upstream of status-data.json (via Jira Sync). The validator reports Jira divergences but never writes back to Jira

## Integration with other skills

| Caller | Why |
|---|---|
| Session resume flow (Step 2.75 in SKILL.md) | Step 1 of resume â€” catch drift before resuming work |
| `/publish-status` command | Pre-publish gate â€” never publish stale derivatives |
| End-of-session checkpoint | Offered when the session modified canonical state |
| Requirements Interrogator (In-flight mode) | When a requirement changes, run the validator to catch downstream artefacts that need updating |
| Intake Reviewer (Hook 2) | Run after Confluence/Jira context gathering if a previous status page is found, to confirm it's current before relying on it |

## Standard conformance check (Wave 7)

After cross-document validation completes, run a standard conformance check
on artefacts that have a governing reference standard.

For each live artefact:
1. Identify which reference standard governs it (from the Standards index in `SKILL.md`)
2. Check structural conformance (required fields present, format matches)
3. Report any conformance failures in the divergence table with action "Update to conform"

Example output entry:

| # | Fact | Canonical | Found in | Found value | Action |
|---|---|---|---|---|---|
| 5 | Story acceptance criteria format | references/user-story-format.md (Given/When/Then or table) | PROJ-001 (Jira) | Plain bullet list | Reformat to conform |

This check is **non-blocking** â€” conformance is a quality measure, not a gate.
The user can defer fixes. But it surfaces drift before it accumulates.

### Standard conformance map (Wave 7 complete)

| Artefact type | Reference standard | Conformance check |
|---|---|---|
| Story / spike / bug / enabler ticket | `references/user-story-format.md` | Sections present, INVEST passes, DoR checklist present, scope linked |
| Story in Jira | + `references/jira-ticket-format.md`, + your project-specific `jira-templates` skill | ADF format used, canonical example mirrored, custom fields populated |
| RAID entry (R / A / I / DEP / D / OQ) | `references/raid-format.md` | Required fields present, status in valid set, age-based flags |
| Requirement entry | `references/requirement-format.md` | Required fields present, interrogator output linked for confirmed, acceptance for met present |
| MoSCoW matrix | `references/requirement-format.md` | Per-scope coverage, override decisions linked |
| Confluence status page | `references/status-page-format.md` | Section order, outcome health present, DRAFT banner if applicable, supersede chain correct |
| Visual (flowchart, etc.) | `references/visual-output-format.md` | Template used, colour taxonomy applied, node detail complete |
| status-data.json | `references/canvas-data-model.md` | Schema match, required fields, valid state values |

Each check is non-blocking â€” surfaces in the divergence table with action "Update to conform". The user can defer fixes.

## Hook contract

Add to `hook-contracts.md`:

| Hook ID | Callee | Trigger | Inputs | Outputs | Failure mode | Status |
|---|---|---|---|---|---|---|
| HK-SV-JS-presync | Jira_Sync | Always before validation | Ticket list from status-data.json | Refreshed ticket statuses | Warn â€” proceed with stale; flag in report | ðŸŸ£ W5 |
| HK-SV-CANV-refresh | Project_Canvas (Data Model section) | Always before validation | Tracker content | Refreshed status-data.json | Block â€” can't validate against stale derived state | ðŸŸ£ W5 |
| HK-SV-APD-patterns | Anti_Pattern_Detector | After validation | Divergence list | Updated watchlist entries (only if patterns) | Warn | ðŸŸ£ W5 |
| HK-SV-COMD-supersede | Communication_Drafter | When pages need superseding | Page list | Supersede banner content | Warn â€” manual fallback | ðŸŸ£ W5 |

