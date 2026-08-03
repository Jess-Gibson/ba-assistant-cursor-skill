# Canvas generation  -  context gathering, architecture, template
<!-- Wave 10: moved verbatim from SKILL.md. Read AFTER the router; read canvas-tab-specs.md next. -->

## Workflow: Context → Canvas

### Phase 1: Discover the project (automatic  -  do NOT ask first)

**Do not ask the user where files are.** Find them automatically:

**Step 1  -  Find the project folder.** Search the workspace for the project's blueprint/analysis directory. Common patterns:
- `<workspace>/blueprints/<project-name>/` -- flat structure (Sample Initiative pattern, preferred)
- `<workspace>/blueprints/Project NNN - <name>/` -- numbered project format
- `<workspace>/<project-name>/docs/` -- simpler layout

Search strategy:
1. Glob for `**/blueprints/**/SESSION-CONTEXT.md` or `**/blueprints/**/Project-hub.md`
2. Glob for `**/blueprints/**/*.md` to find all project folders
3. If multiple projects exist, present them via `AskQuestion` and let the user pick
4. If no project folder is found, THEN ask the user

**Step 2  -  Read ALL files in the project folder.** This is MANDATORY. Read every single file:

```
MUST READ (in priority order  -  start with richest sources):
1. SESSION-CONTEXT.md           -  richest single source: decisions, OQs, risks, stakeholders, Jira tickets, delivery sequence, compliance status, milestones
2. initiative-tracker*.md       -  decisions, risks, OQs, assumptions, spikes, confidence scores
3. Project-hub.md               -  high-level status, stakeholders, key outputs
4. confluence-pages.json        -  Confluence page IDs and URLs, Jira epic keys
5. Compliance-*.md              -  compliance decisions, sign-off packs, decision packs
6. Meeting-*.md                 -  workshop outcomes, actions, attendees
7. solution-options*.md         -  solution direction, ADRs, options comparison
8. Requirements*.md / BRD*.md   -  business requirements
9. Analysis-*.md                -  deep dive analyses
10. Spike-*.md                  -  technical spike findings
11. Program-*.md                -  program sequencing, task backlog
12. *.html                      -  previous status snapshots (check for data)
13. ANY OTHER .md files         -  read them ALL, no exceptions
```

**Do NOT skip files.** Every `.md` file in the project folder contributes context. The more files you read, the more accurate and complete the canvas will be. If a file is large, still read it  -  truncate only if it exceeds your context window, and note what you skipped.

**Also search up one directory level**  -  check the parent `docs/` or `blueprints/` folder for:
- `README.md`, `AGENTS.md`, `!CLAUDE.md`  -  project-level config
- Additional `*.md` files not in the analysis subfolder

### Phase 2: Gather live data from external sources

**Step 3  -  Ask the user ONLY for genuinely missing information** (via `AskQuestion`):

Only ask if you couldn't determine these from the files you read:
- Initiative name (if not in any file header)
- Current phase (if SESSION-CONTEXT doesn't state it)
- Parent Jira epic key (if not in `confluence-pages.json` or SESSION-CONTEXT)
- Key deadlines (if not mentioned anywhere)
- Stakeholders (if not listed in any file)

**Step 3  -  Pull live data from Jira** (mandatory when Jira MCP is available)

**Jira is the source of truth for all ticket data.** Never use hardcoded ticket status, titles, or estimates when Jira is reachable. Always execute this full sync sequence:

**3a. Resolve the Jira cloud ID**
```
getAccessibleAtlassianResources → pick the cloud ID for your Jira site
```
If your-jira-cloud is not in the list, Jira auth is missing for this session  -  fall back to markdown sources and note the gap in the canvas footer.

**3b. Find the project parent epic(s)**
The parent epic key should be sourced from (in priority order):
1. `confluence-pages.json`  -  look for a `jiraEpic` or `jiraParent` field
2. `PROJECT-CONTEXT.md` or `SESSION-CONTEXT.md`  -  scan for lines like `Epic: PROJ-XXXX` or `Parent: PROJ-XXXX`
3. `Project-hub.md`  -  look for Jira links
4. Ask the user: `"What is the parent Jira epic or programme key for this initiative?"`

**3c. Fetch all epics under the programme (if programme key exists)**
```
searchJiraIssuesUsingJql:
  jql: "project = PROJ AND issueType = Epic AND 'Epic Link' = <programme-key> ORDER BY key ASC"
  OR: "project = PROJ AND parent = <programme-key> ORDER BY key ASC"
  fields: [summary, status, assignee, labels, priority, customfield_10016, customfield_10004]
  maxResults: 50
```

**3d. Fetch all stories under each epic**
For each epic found (or directly if user provides an epic key like PROJ-4304):
```
searchJiraIssuesUsingJql:
  jql: "'Epic Link' = <epic-key> ORDER BY key ASC"
  OR: "parent = <epic-key> ORDER BY key ASC"
  fields: [summary, status, assignee, priority, customfield_10016, customfield_10004, customfield_10007, issuelinks]
  maxResults: 100
```

**3e. Extract and map from each issue:**
| Jira field | Canvas field |
|---|---|
| `issue.key` | `id` |
| `issue.fields.summary` | `label` (truncate to ~60 chars if needed) |
| `issue.fields.status.name` | Map to canvas status (see mapping below) |
| `issue.fields.customfield_10016` OR `issue.fields.customfield_10004` | `storyPoints` (number or null  -  used for velocity forecasting; null values get median-filled per step 3i). **Field varies by Jira instance**  -  check both `customfield_10016` (Jira Software story points) and `customfield_10004` (Story Points classic) and use whichever is non-null. If neither is populated, treat as null. |
| `issue.fields.customfield_10007[0].name` | `sprint` label |
| `issue.fields.customfield_10007[0].startDate` | Sprint start date (ISO)  -  used for timeline `startWeek` when ticket is still To Do |
| `issue.fields.customfield_10007[0].endDate` | Sprint end date (ISO)  -  used to calculate planned `weeks` duration |
| `issue.fields.assignee.displayName` | `assignee` |
| `issue.fields.issuelinks` | `dependsOn` (filter `inwardIssue` where type = "blocks") |
| `issue.fields.priority.name` | Note if High/Critical for critical path |

**3f. Jira → canvas status mapping:**
| Jira status | Canvas `ItemStatus` |
|---|---|
| Done, Closed, Released | `"done"` |
| In Progress, In Development, In Review | `"in-progress"` |
| To Do, Open, Backlog, Selected for Development | `"pending"` |
| Blocked, On Hold, Impediment | `"blocked"` |
| Won't Do, Duplicate | skip (exclude from canvas) |

**3g. Fetch changelog for status transition dates** (mandatory for timeline accuracy)

For every ticket that will appear on the timeline, fetch it individually with `expand: "changelog"` to extract real status transition dates:

```
getJiraIssue:
  cloudId: <your-jira-cloud-cloud-id>
  issueIdOrKey: "PROJ-XXXX"
  expand: "changelog"
  fields: [summary, status, created, updated, assignee]
```

From the changelog `histories` array, extract all entries where `items[].field === "status"`. Build a status transition timeline for each ticket:

| Changelog field | What to extract |
|---|---|
| `history.created` | Timestamp of the status change |
| `items[].fromString` | Previous status name |
| `items[].toString` | New status name |

Key transitions to capture:
- **In Progress date**  -  first transition where `toString` is "In Progress" (or "In Development"). This is the ticket's **actual start date** for the timeline bar.
- **Done date**  -  first transition where `toString` is "Done", "Closed", or "Released". This is the ticket's **actual end date**.
- **Created date**  -  `fields.created`  -  fallback if no In Progress transition exists yet.

**Mapping real dates to timeline weeks:**
```
startWeek = (inProgressDate - projectKickoffDate) / 7 days
weeks = status === "done"
  ? (doneDate - inProgressDate) / 7 days   // minimum 0.5
  : (today - inProgressDate) / 7 days + 2  // extend past today for in-progress
```

**Rules:**
- If a ticket went To Do → In Progress → Done all on the same day, show `weeks: 0.5` minimum so the bar is visible
- If a ticket is "Done" but the done date is before the timeline's Sprint 1 start, position it at the correct historical week  -  do NOT push it to Sprint 1
- Add the actual date to the label: `"PROJ-4305 Domain Model (15 May)"`  -  this makes the timeline self-documenting
- **Never assume a ticket starts at Sprint 1** just because it's in the sprint. Real start = first "In Progress" changelog entry

**Sprint-based planned timeline (for tickets still in To Do / Backlog):**

When a ticket has no "In Progress" changelog entry (status = To Do / Backlog), use the **sprint field** to derive its planned start week:

1. **Extract sprint dates from the API response.** The sprint field (`customfield_10007`) returns an array with `startDate` and `endDate` as ISO timestamps (e.g. `"2026-05-19T13:00:00.000Z"`). The sprint `name` also often encodes the date in a team-specific convention (e.g. `PROJ Sprint 37 20260513-527` → `20260513` = 13 May).
   - **Prefer `startDate`/`endDate` from the API** over parsing the name  -  they're the authoritative values.
   - The `state` field indicates `"active"`, `"future"`, or `"closed"`  -  use this to validate against the ticket's status.
2. **Calculate planned startWeek:** `(sprintStartDate - projectKickoffDate) / 7 days`
3. **Calculate planned weeks:** `(sprintEndDate - sprintStartDate) / 7 days`  -  gives the actual sprint length from Jira rather than assuming 2 weeks.
4. **Label convention:** Include `"(Sprint NN, est.)"` or `"(To Do)"` in the label so it's visually distinguishable from real dates.
5. **If no sprint is assigned:** Position the ticket after the last known sprint with `status: "pending"` and label `"(unscheduled)"`.

```
Example: PROJ-4301 is in Sprint 37 (starts 13 May), project kickoff was 28 Apr.
  sprintStartDate = 13 May 2026
  startWeek = (13 May - 28 Apr) / 7 = ~2.1
  weeks = 2 (default sprint length)
  label = "PROJ-4301 Churned State CS (Sprint 37, est.)"
  status = "pending"
```

**Priority order for determining startWeek:**
1. **Changelog "In Progress" date**  -  always preferred when it exists (real date)
2. **Sprint start date**  -  use when ticket is still To Do but assigned to a sprint (planned date)
3. **Ticket creation date**  -  last resort, only for unscheduled tickets that need a position on the timeline

This ensures the timeline always reflects the best available data: real dates when work has started, planned sprint dates for upcoming work, and creation dates as a fallback.

**3h. After fetching, update canvas data arrays:**
- `STORIES` / `WORK_ITEMS`  -  replace entirely with live Jira data
- `allItems` in `TimelineTab`  -  update `status`, `label`, `startWeek`, and `weeks` from Jira changelog dates; never keep estimated dates when real dates are available
- `depNodes` in `DependenciesTab`  -  update `status` from Jira
- Collapsible card counts in RAID tab automatically reflect the data

**3i. Story points and velocity forecasting** (mandatory when story points exist)

Story points from Jira (`customfield_10016`) drive velocity-based forecasting for unscheduled work.

**Extract and normalise story points:**

1. For each ticket, record `storyPoints = issue.fields.customfield_10016 ?? issue.fields.customfield_10004` (use whichever is non-null; `customfield_10004` is "Story Points (classic)" common in your-jira-cloud).
2. **Median fill for blanks:** Calculate the median story points from all pointed tickets in this project/epic. If a ticket has `storyPoints === null`, assign the project median. If no tickets have points at all (cold start), use `3` as the default.
3. **Mark estimated values:** Any ticket whose points were filled via median MUST be labelled with `(est.)` suffix in all table displays  -  e.g. `"3 (est.)"`. Use italic text styling in the canvas (`fontStyle: "italic"`) and in HTML (`<em>3 (est.)</em>`).

**Calculate team velocity:**

```
velocity = totalPointsCompletedInClosedSprints / numberOfClosedSprints
```

To compute this automatically:
1. From all tickets with `status === "done"`, group by their sprint (`customfield_10007`).
2. Only count sprints where `state === "closed"` (not the active sprint  -  it's incomplete).
3. Sum the `storyPoints` (real + median-filled) per closed sprint.
4. `velocity = sum(sprintPoints) / closedSprintCount`
5. If no closed sprints exist (project too new), ask the user: `"What is your team's velocity in story points per sprint?"` via `AskQuestion`.
6. If user doesn't know either, use `10 points/sprint` as a conservative default and note it in the canvas footer.

**Forecast completion for unscheduled / pending work:**

For tickets in `To Do` or `Backlog` without a sprint assignment:
1. Sum their story points (real + median) → `remainingPoints`
2. `sprintsNeeded = Math.ceil(remainingPoints / velocity)`
3. `forecastWeeks = sprintsNeeded * sprintLengthWeeks` (derive sprint length from closed sprint dates, or default to 2 weeks)
4. Position these tickets on the timeline starting after the last scheduled sprint ends, spaced by `forecastWeeks`.
5. Label them with `"(velocity forecast)"` to distinguish from sprint-assigned estimates.

**Display in canvas:**

| Location | What to show |
|---|---|
| **Features & Delivery table** | Add `SP` column. Show real points as-is, median-filled as `"3 (est.)"` in italic. |
| **Overview stats** | Add a Stat: `velocity` value (e.g. `"12 pts/sprint"`) with label `"Team velocity"`. If calculated, `tone="info"`. If defaulted, `tone="warning"`. |
| **Timeline tab** | Unscheduled tickets forecasted using velocity get bars positioned at the forecast start date with `status: "pending"` and label suffix `"(velocity forecast)"`. |
| **Critical Path tab** | Add a row: `"Remaining backlog forecast"` with target = calculated date, status = forecast. |

**Velocity display in HTML:**
- Same SP column with `<em>` for estimated values.
- Velocity stat in Overview section.
- Timeline forecast bars use the `pending` colour class with italic labels.

**Step 5  -  From Confluence MCP** (if available and `confluence-pages.json` exists):
- Use page IDs from `confluence-pages.json` to read specific pages
- Read the project hub page and key child pages
- Extract: stakeholders, decisions, timeline, requirements

### Phase 3: Synthesise and generate BOTH outputs

With all gathered context, generate both outputs. Data is embedded directly in both files.

**Mandatory outputs (both required on every invocation):**

1. **`.canvas.tsx`**  -  Cursor Canvas with all 8 interactive tabs
2. **`status-snapshot.html`**  -  Standalone HTML with same data, same 8 sections

**If insufficient data for a tab:** Always render all 8 tabs/sections, but show a clear prompt in empty sections explaining what's missing and how to populate it. NEVER reduce the tab count.

**After generation, tell the user:**
> "Canvas and HTML snapshot generated. The HTML file is at `<path>/status-snapshot.html`  -  you can open it in any browser, email it, or attach it to Confluence for stakeholders without Cursor access."

## Canvas architecture

### Eight interactive tabs (using `useCanvasState`)  -  Wave 3 + demo iteration

| Tab | Content | Visuals |
|---|---|---|
| **Overview** | Workstream strip (friendly names + emojis, no M-codes), 4 stakeholder-readable stats (days to deadline / features on track / blockers / decisions confirmed), "Where we are right now" callout, 2×2 Top blockers grid with emoji-prefixed titles, "Where each scope is right now" table, confidence table | Stat grid + Callouts + Tables (no charts) |
| **Workstreams** | Workstream grid  -  scopes down (cohorts indented + zebra-striped + section dividers), 8 workstreams across (Intake / Kickoff / Discovery / Slicing & Sequencing / Solution / Delivery / Playback / Eval & Retro  -  no M-codes), cells coloured by state (🟢 Done, 🔵 Active, ⏸ Paused, ○ Not started, · N/A). **In-progress MUST be BLUE.** Compact horizontal legend BELOW the grid. Recent workstream changes log. | Custom SVG grid + horizontal legend + Table |
| **Features & Delivery** | Feature status table (with active workstreams summary per feature), Jira-style stories table (filtered by scope) with MoSCoW column (emoji-prefixed), MoSCoW priority matrix per cohort | Tables with row tones |
| **Timeline** | SVG Gantt with **Milestones swimlane at the TOP** (each milestone = emoji + label + date stacked, e.g. "⚖️ / Legal sign-off / 27 May"), then team/area swimlanes (BA Analysis, Compliance/Legal, F1 Eng, etc), vertical **blue dashed Today line**, vertical **red dashed ⛔ Deadline line**, bar length = `weeks × colWidth − 4`, bars auto-pack into sub-rows so they never overlap, **date headers in real dates** ("18 May, 25 May…") NOT week codes (W21, W22). | Custom SVG Gantt |
| **Dependencies** | Interactive DAG (real Requirement / Story / Milestone → Deadline graph)  -  click any node to highlight upstream + downstream chain via BFS. Critical chains as horizontal Pill chains below. | `computeDAGLayout` + SVG + Pills |
| **Traceability** | Interactive DAG  -  bidirectional click-to-highlight. ⚖️ Driver → 📋 Requirement → 🍕 Slice → 🎟️ Story → 📌 ADR. Requirement nodes carry MoSCoW pills per scope. Below the DAG: full mapping table. | `computeDAGLayout` + SVG + Table |
| **Critical Path & Actions** | Milestone table with status emoji pills, actions due this week (from action register), MoSCoW warnings if any | Tables with row tones |
| **RAID & Tracker** | 5 card-style RAID collections (📌 Decisions, 🧨 Risks, ❓ Open Questions, ⚠️ Assumptions, 🎯 Actions) using `<Card collapsible>`. **"Show outstanding items only" toggle defaults to CHECKED.** IDs in small font column; descriptions in prime column. | Cards + Tables + Checkbox toggle |

### Scope navigator (demo iteration  -  replaces old breadcrumb)

A **horizontal multi-select pill cluster** above the tab strip. Three visually-grouped clusters separated by `|` characters as `Text size="small" tone="tertiary"`:

```
Filter scope:  [✓ 🏛️ Initiative level]  |  [F1 …]  [F2 …]  [F3 …]  |  [Cohort: Solo]  [Cohort: AccountRight]  [Cohort: Business]
Showing the whole initiative (Initiative level) · click a feature or cohort to drill in · click "Initiative level" to reset
```

**UX contract (mandatory  -  these rules must NEVER be relaxed):**

| Action | Behaviour |
|---|---|
| Default state on load | `selectedScopes = ["initiative"]`  -  "Initiative level" pill `active`, `tone="info"`, with `✓ ` prefix |
| Click "🏛️ Initiative level" | Clear all other selections; result = `["initiative"]` |
| Click a feature or cohort while Initiative is the only selection | Remove `"initiative"`; add clicked scope. Initiative pill goes inactive (neutral tone, no `✓`) |
| Click a feature or cohort while it is already selected | Remove it from selection |
| Click a feature or cohort while others (not initiative) are selected | Toggle it (add or remove) |
| Result of any action ends with empty `selectedScopes` | Snap back to `["initiative"]`  -  never leave the array empty |

**State and helpers (use exactly this shape):**

```tsx
type ScopeLevel = "initiative" | "feature" | "cohort";
type ScopeId = "initiative" | /* project-specific feature ids */ | /* project-specific cohort ids */;

interface Scope { id: ScopeId; label: string; shortLabel: string; level: ScopeLevel }
const SCOPES: Scope[] = [
  { id: "initiative", label: "Initiative level", shortLabel: "Initiative", level: "initiative" },
  // ...features then cohorts in display order
];
```

#### Scope label naming  -  MANDATORY rule (no BA jargon in user-facing labels)

**Internal IDs MAY be coded** (e.g. `"F-A"`, `"C-A"`, `"F-B"`)  -  these are not user-facing and are used only for routing, filtering, and code references.

**Display labels MUST use real business context**  -  `label` and `shortLabel` must describe what the feature or cohort actually IS in plain business terms. Never use `"Feature A"`, `"Feature B"`, `"Cohort A"`, `"Cohort B"` etc. as the displayed name. Those abstract codes mean nothing to a stakeholder reading the canvas.

| ❌ Bad (BA jargon) | ✅ Good (real business context) |
|---|---|
| `label: "F-A Rule Uplift"` | `label: "Data Collection Uplift Collection Uplift"` |
| `shortLabel: "Feature A"` | `shortLabel: "Data Collection Uplift Uplift"` |
| `label: "Cohort A: Stale Draft"` | `label: "Stale Drafts (<30d, never live)"` |
| `shortLabel: "Cohort A"` | `shortLabel: "Stale Drafts"` |
| `label: "Cohort B: Churned >7yr"` | `label: "Churned merchants (>7yr)"` |
| `shortLabel: "Cohort B"` | `shortLabel: "Churned >7yr"` |

**This rule applies everywhere a label is displayed**  -  SCOPES, timeline lane labels, timeline bar labels, dependency DAG node labels, traceability DAG slice/requirement labels, critical path milestones, RAID descriptions, callout text, narrative copy, table cells, chain card headers. Anywhere the user sees text.

**`shortLabel` constraint**: ≤ 18 characters, used in dense visuals (workstreams SVG, filter pills, timeline lane labels). `label`: longer descriptive form, used in tooltips and tables where space permits. Never repeat the descriptor between the two (`label: "Stale Drafts (stale drafts)"` is wrong).

**One exception  -  Jira-mirrored text**: if a Jira ticket title literally contains "Cohort A" or "Feature B" as Jira-authoritative terminology, you may keep it in the `STORIES` array title field exactly as it appears in Jira. But the canvas should still render the cohort/feature column using `SCOPES.shortLabel` (real business name), not the BA code.

**Why this rule exists**: stakeholders reading the canvas (HoP, compliance, vendor partners) have no mental model for what "Cohort B" means; they DO have a mental model for "Churned merchants (>7yr)". The canvas is a stakeholder artefact, not a BA workbook.

#### JSX-safe character handling  -  MANDATORY (avoids parse errors)

Scope labels and shortLabels often legitimately contain `<`, `>`, `&`, `{`, `}` characters (e.g. `"Stale Drafts (<30d, never live)"`, `"Churned merchants (>7yr)"`, `"R&D Squad"`). These are SAFE in **JS string literals** (the SCOPES array, status-data.json, prop values via `{variable}` expressions)  -  React auto-escapes them at render time.

These are **UNSAFE** when typed directly in JSX text content (between tags). The JSX parser sees `>` as a tag delimiter and throws:

> `The character ">" is not valid inside a JSX element ... Did you mean to escape it as "{'>'}" instead?`

**Three rules to avoid this**:

1. **Prefer expression rendering**: always reference scope labels via `{variable}` (e.g. `<Text>{scope.shortLabel}</Text>`), never copy-paste the label text into JSX between tags.
2. **For hardcoded prose** that mentions a scope (callouts, narrative text, card headers, chain card titles), use HTML entities: `&gt;` for `>`, `&lt;` for `<`, `&amp;` for `&`. Example: `<CardHeader>Chain B  -  Churned &gt;7yr (blocked)</CardHeader>`.
3. **After any scope rename**, run a quick lint check. The canvas Skill self-check pre-delivery list MUST include: "no unescaped `<` or `>` in JSX text content  -  search for `>[A-Za-z0-9]` outside of `{...}` expressions".

**If you ever introduce a label containing `<` or `>`**, prefer parenthetical notation that avoids ambiguity in spoken/written use too: `"Churned merchants (>7yr)"` or alternative phrasings like `"Long-Churned (over 7yr)"` or `"Stale Drafts (under 30 days)"`. Both convey the same business semantics without forcing every JSX-text consumer to escape.

#### Scope state management

```tsx
const [selectedScopes, setSelectedScopes] = useCanvasState<ScopeId[]>("selectedScopes", ["initiative"]);

const toggleScope = (id: ScopeId) => {
  if (id === "initiative") { setSelectedScopes(["initiative"]); return; }
  const wasSelected = selectedScopes.includes(id);
  let next = selectedScopes.filter((s) => s !== "initiative");
  next = wasSelected ? next.filter((s) => s !== id) : [...next, id];
  if (next.length === 0) next = ["initiative"];
  setSelectedScopes(next);
};

const showingInitiative = selectedScopes.length === 1 && selectedScopes[0] === "initiative";
const isScopeActive: (id: ScopeId) => boolean = (id) =>
  showingInitiative || selectedScopes.includes(id);

const filterDescription = showingInitiative
  ? "Showing the whole initiative (Initiative level)"
  : `Showing: ${SCOPES.filter((s) => selectedScopes.includes(s.id)).map((s) => s.shortLabel).join(", ")}`;
```

**Filter-down pattern (do NOT pass a single `activeScope` object  -  pass the `isScopeActive` callback):**

```tsx
type ScopeFilter = (id: ScopeId) => boolean;

{section === "overview" && <OverviewTab isActive={isScopeActive} />}
{section === "workstreams" && <WorkstreamsTab isActive={isScopeActive} />}
// ...etc  -  every tab takes `isActive: ScopeFilter`
```

Every tab uses `isActive(scope.id)` to decide whether to show a row, bar, or node. This pattern enables true multi-scope views (e.g. "show me F1 + Cohort Solo on the same timeline") without forcing a single-scope drill-down.

**Pill rendering pattern (every scope pill follows this):**

```tsx
{SCOPES.filter((s) => s.level === "feature").map((s) => {
  const isOn = selectedScopes.includes(s.id);
  return (
    <Pill key={s.id} active={isOn} tone={isOn ? "info" : "neutral"} onClick={() => toggleScope(s.id)}>
      {isOn ? "✓ " : ""}{s.label}
    </Pill>
  );
})}
```

The Initiative-level pill additionally prefixes `🏛️ ` to the label. Use `Text size="small" tone="tertiary"` for the `|` separators between clusters. The "Showing: …" description line uses `Text size="small" tone="secondary"`.

### Interactivity features

1. **Section navigation**  -  `useCanvasState<SectionId>("section", "overview")` with Pill toggles (8 Pills, one per tab).
2. **Scope navigator**  -  `useCanvasState<ScopeId[]>("selectedScopes", ["initiative"])` (see UX contract above). Every tab respects `isScopeActive`.
3. **Click-to-highlight (Dependencies)**  -  `useCanvasState<string | null>("dep-selected", null)`. Click a node → BFS upstream + downstream → chain highlights with accent blue; unrelated nodes dim to ~20% opacity, unrelated edges to ~15% opacity. "Clear selection" ghost Button appears when a node is selected.
4. **Click-to-highlight (Traceability)**  -  Same pattern: `useCanvasState<string | null>("trace-selected", null)`. Bidirectional BFS traversal highlights the full connected chain.
5. **Collapsible sections**  -  `<Card collapsible>` (or `<details>` in HTML) for each RAID collection.
6. **Outstanding-only filter**  -  `useCanvasState<boolean>("outstandingOnly", true)` Checkbox toggle in RAID tab. **Defaults to CHECKED** so the page opens to what needs attention.
7. **Hover tooltips**  -  SVG `<title>` elements inside each `<g>` node. Format examples:
   - Workstream cell: `"F1 Fee Detection  -  Solution: Done"`
   - Gantt bar: `"F1 Product deploy  -  In progress  -  scope: Product-A"`
   - Milestone: `"Legal sign-off  -  27 May"`
   - Dep / trace node: `"PROJ-5103: block fee overlay ≥ 1 Jul (in progress)"`
8. **No old activeFilters[] feature filter**  -  this was superseded by the scope navigator. Do NOT also render a separate "Features" multi-select; that's duplication.

### Colour scheme (mandatory  -  use consistently)

Use the `useStatusColours()` helper pattern. All status colours MUST use theme tokens  -  no hardcoded hex.

| Status | Token | Visual in dark mode |
|---|---|---|
| Done | `theme.diff.stripAdded` | Green |
| In Progress | `theme.accent.primary` | Blue |
| Pending | `theme.fill.tertiary` | Faint grey |
| Blocked | `theme.diff.stripRemoved` | Red/pink |
| Conditional | `theme.fill.secondary` | Light grey |

Define a helper function for consistency:

```tsx
function useStatusColours() {
  const theme = useHostTheme();
  return {
    done: theme.diff.stripAdded,
    "in-progress": theme.accent.primary,
    pending: theme.fill.tertiary,
    blocked: theme.diff.stripRemoved,
    conditional: theme.fill.secondary,
  };
}
```

### Per-scope colour helpers and emoji conventions

Status colour helper (mandatory  -  use these tokens, never hardcode hex):

```tsx
type ItemStatus = "done" | "in-progress" | "pending" | "blocked";

function useStatusColours() {
  const theme = useHostTheme();
  return {
    done: theme.diff.stripAdded,       // green
    "in-progress": theme.accent.primary, // BLUE  -  not amber, not brown
    pending: theme.fill.tertiary,       // greyed
    blocked: theme.diff.stripRemoved,   // red
  };
}

const itemStatusEmoji = (s: ItemStatus): string => {
  if (s === "done") return "🟢";
  if (s === "in-progress") return "🔵";
  if (s === "blocked") return "🔴";
  return "○";
};

const itemStatusLabel = (s: ItemStatus): string => {
  if (s === "done") return "Done";
  if (s === "in-progress") return "In progress";
  if (s === "blocked") return "Blocked";
  return "Not started";
};
```

Workstream state colour helper (for the Workstreams tab grid):

```tsx
type WorkstreamState = "complete" | "active" | "paused" | "not-started" | "na";

const STATE_EMOJI: Record<WorkstreamState, string> = {
  complete: "🟢",
  active: "🔵",
  paused: "⏸",
  "not-started": "○",
  na: "·",
};

const STATE_LABEL: Record<WorkstreamState, string> = {
  complete: "Done",
  active: "Active",
  paused: "Paused",
  "not-started": "Not started",
  na: "N/A",
};

// In Workstreams tab:
const stateColor = (state: WorkstreamState) => {
  if (state === "complete") return theme.diff.stripAdded;
  if (state === "active") return theme.accent.primary;       // BLUE
  if (state === "paused") return theme.diff.stripRemoved;
  if (state === "not-started") return theme.fill.tertiary;
  return "transparent";
};
// Cell opacity: 0.8 for non-na states; 0.08 for na (faded-out grey).
```

### Empty state handling

When a tab has insufficient data, render the tab with:
- A clear heading (same as normal)
- A Callout (tone="info") explaining what's needed
- A concrete action the user can take

```tsx
<Stack gap={12}>
  <H2>Dependencies</H2>
  <Callout tone="info" title="No dependency data yet">
    <Text size="small">To populate this tab, I need story dependencies (linked Jira issues or 'gates on' relationships). Run /canvas after defining your backlog with dependency links.</Text>
  </Callout>
</Stack>
```

## Template structure

```tsx
import {
  Button,
  Callout,
  Card,
  CardBody,
  CardHeader,
  computeDAGLayout,
  Divider,
  Grid,
  H1,
  H2,
  Pill,
  Row,
  Spacer,
  Stack,
  Stat,
  Table,
  Text,
  useCanvasState,
  useHostTheme,
} from "cursor/canvas";

type TabId = "overview" | "workstreams" | "features" | "timeline" | "dependencies" | "traceability" | "critical-path" | "tracker";
type FeatureId = /* project-specific feature slugs */;
type ScopeLevel = "initiative" | "feature" | "cohort" | "slice";
interface ActiveScope { level: ScopeLevel; id: string; featureId?: string }
// Internal data model may still use ModeId/ModeState for backwards compat;
// user-facing labels use the friendly names below.
type WorkstreamKey = "intake" | "kickoff" | "discovery" | "slicing" | "solution" | "delivery" | "playback" | "eval-retro";
type WorkstreamState = "not-started" | "active" | "paused" | "complete" | "na";
// Eval & Retro is a single merged workstream (was Evaluation + Retro pre-demo iteration).
type MoSCoW = "Must" | "Should" | "Could" | "Won't" | null;
type ItemStatus = "done" | "in-progress" | "pending" | "blocked" | "conditional";

function useStatusColours() {
  const theme = useHostTheme();
  return {
    done: theme.diff.stripAdded,
    "in-progress": theme.accent.primary,
    pending: theme.fill.tertiary,
    blocked: theme.diff.stripRemoved,
    conditional: theme.fill.secondary,
  };
}

/* ─── HorizontalBarChart  -  use this instead of BarChart for RAID and delivery summaries ─── */
interface HBarSeries { name: string; value: number; tone: "success" | "warning" | "info" | "neutral" }
interface HBarRow { label: string; series: HBarSeries[] }
function HorizontalBarChart({ rows }: { rows: HBarRow[] }) {
  const theme = useHostTheme();
  const toneColor = (tone: HBarSeries["tone"]) => {
    if (tone === "success") return theme.diff.stripAdded;
    if (tone === "warning") return theme.diff.stripRemoved;
    if (tone === "info") return theme.accent.primary;
    return theme.fill.secondary;
  };
  const maxTotal = Math.max(...rows.map((r) => r.series.reduce((s, x) => s + x.value, 0)), 1);
  const barHeight = 20, rowGap = 32, labelW = 110, barMaxW = 320, legendDotSize = 10;
  const allSeries = rows[0]?.series ?? [];
  const svgH = rows.length * rowGap + 28;
  const svgW = labelW + barMaxW + 60;
  return (
    <div style={{ overflowX: "auto" }}>
      <svg width={svgW} height={svgH} style={{ display: "block" }}>
        {rows.map((row, ri) => {
          const y = ri * rowGap + 4; let x = labelW;
          return (
            <g key={row.label}>
              <text x={0} y={y + barHeight / 2 + 1} fontSize={11} fill={theme.text.secondary} dominantBaseline="middle">{row.label}</text>
              {row.series.map((seg) => {
                const w = Math.max((seg.value / maxTotal) * barMaxW, seg.value > 0 ? 20 : 0);
                const rx = x; x += w;
                return (
                  <g key={seg.name}>
                    <rect x={rx} y={y} width={w} height={barHeight} fill={toneColor(seg.tone)} opacity={0.75} />
                    {seg.value > 0 && <text x={rx + w / 2} y={y + barHeight / 2 + 1} textAnchor="middle" fontSize={10} fontWeight="600" fill={theme.text.primary} dominantBaseline="middle">{seg.value}</text>}
                  </g>
                );
              })}
            </g>
          );
        })}
        {allSeries.map((seg, i) => (
          <g key={seg.name}>
            <rect x={labelW + i * 80} y={rows.length * rowGap + 6} width={legendDotSize} height={legendDotSize} fill={toneColor(seg.tone)} opacity={0.75} rx={2} />
            <text x={labelW + i * 80 + legendDotSize + 4} y={rows.length * rowGap + 6 + legendDotSize / 2 + 1} fontSize={11} fill={theme.text.secondary} dominantBaseline="middle">{seg.name}</text>
          </g>
        ))}
      </svg>
    </div>
  );
}

export default function <ProjectName>Status() {
  const [section, setSection] = useCanvasState<TabId>("section", "overview");
  const [selectedScopes, setSelectedScopes] = useCanvasState<ScopeId[]>("selectedScopes", ["initiative"]);

  const toggleScope = (id: ScopeId) => {
    if (id === "initiative") { setSelectedScopes(["initiative"]); return; }
    const wasSelected = selectedScopes.includes(id);
    let next = selectedScopes.filter((s) => s !== "initiative");
    next = wasSelected ? next.filter((s) => s !== id) : [...next, id];
    if (next.length === 0) next = ["initiative"];
    setSelectedScopes(next);
  };

  const showingInitiative = selectedScopes.length === 1 && selectedScopes[0] === "initiative";
  const isScopeActive = (id: ScopeId): boolean => showingInitiative || selectedScopes.includes(id);
  const filterDescription = showingInitiative
    ? "Showing the whole initiative (Initiative level)"
    : `Showing: ${SCOPES.filter((s) => selectedScopes.includes(s.id)).map((s) => s.shortLabel).join(", ")}`;

  return (
    <Stack gap={24}>
      {/* H1 title + metadata Text */}
      <WorkstreamStrip />
      {/* Scope filter: "Filter scope:" label + initiative pill | feature pills | cohort pills + filterDescription line */}
      {/* Section nav: Row of 8 Pills, one per TabId */}
      <Divider />
      {section === "overview" && <OverviewTab isActive={isScopeActive} />}
      {section === "workstreams" && <WorkstreamsTab isActive={isScopeActive} />}
      {section === "features" && <FeaturesTab isActive={isScopeActive} />}
      {section === "timeline" && <TimelineTab isActive={isScopeActive} />}
      {section === "dependencies" && <DependenciesTab isActive={isScopeActive} />}
      {section === "traceability" && <TraceabilityTab isActive={isScopeActive} />}
      {section === "critical-path" && <CriticalPathTab isActive={isScopeActive} />}
      {section === "tracker" && <TrackerTab isActive={isScopeActive} />}
      <Divider />
      {/* Footer Text with last-updated date and version */}
    </Stack>
  );
}

type ScopeFilter = (id: ScopeId) => boolean;
```

The full reference implementation is `~/.cursor/projects/<workspace>/canvases/sample-initiative-demo.canvas.tsx`. Mirror its structure (component decomposition into `WorkstreamStrip`, `OverviewTab`, `WorkstreamsTab`, `FeaturesTab`, `TimelineTab`, `DependenciesTab`, `TraceabilityTab`, `CriticalPathTab`, `TrackerTab`)  -  do not invent a different layout.


---

## Ported from the pre-split SKILL.md (Wave 10  -  local extras the router condenses)

### Phase 0 initial canvas  -  what to expect

When invoked at Phase 0 end (hook 5 of the Intake Reviewer skill), the canvas
will be sparse by design. Most tabs will show empty-state Callouts. This is
**not a failure mode**  -  the empty states explain what each tab will hold and act
as a roadmap for the user. Tell the user explicitly:

> "Canvas generated at `<path>`. It's mostly empty-state at this point  -  it will
> fill in as we work through the phases. Open it now so you can see progress
> visually from here on."

At Phase 0, the canvas typically contains:
- **Overview**  -  initiative name, current phase pill (Phase 0), confidence scores (all Low/Unknown), workspace context
- **Features & Delivery**  -  empty-state Callout explaining slices will appear after Phase 3
- **Timeline**  -  single Analysis swimlane with the intake bar
- **Dependencies**  -  empty-state Callout
- **Traceability**  -  empty-state Callout
- **Critical Path & Actions**  -  initial actions (kickoff meeting prep, MCP pre-search findings to action)
- **RAID & Tracker**  -  draft RAID from intake, unknowns, assumptions

### Triple-output contract (with BA Assistant / standalone)
Invoked when `/canvas` or `/status` is run. The orchestrator passes current initiative context. The canvas is generated/refreshed automatically.

**`/status` MUST trigger all three outputs:**

1. **Chat status**  -  the standard `/status` text output in the conversation
2. **Canvas refresh**  -  overwrite the living `.canvas.tsx` file with current data (ALL 8 TABS)
3. **HTML snapshot**  -  overwrite the standalone HTML file with current data (ALL 8 SECTIONS)

If the agent runs `/status`, all three outputs are mandatory. Never generate only the chat status without also refreshing the canvas and HTML. Never produce fewer than 8 tabs/sections in either output.

**`/canvas` MUST trigger both file outputs:**
1. **Canvas**  -  `.canvas.tsx` with 8 interactive tabs
2. **HTML**  -  `status-snapshot.html` with 8 interactive sections

### Standalone (without BA Assistant)
Can be triggered directly by a user asking for "project canvas" or running the `/canvas` command. The skill self-bootstraps by:
1. **Automatically** searching for project files (Glob for `**/blueprints/**/*.md`, `**/docs/**/*.md`)
2. **Reading ALL** `.md` files found in the project directory (mandatory  -  no exceptions)
3. **Attempting** Jira MCP sync if available
4. **Only then** asking the user for genuinely missing information via `AskQuestion`

The output is always both files: `.canvas.tsx` + `status-snapshot.html`, both with 8 tabs/sections.

### Refresh cycle
Each refresh overwrites the single living canvas file AND the HTML snapshot. Both files are regenerated from current data. All interactive state (active tab, filter selections, selected nodes) is preserved via `useCanvasState` across rebuilds  -  stored in a `.canvas.data.json` sidecar file.

### File locations summary

| Output | Path | Purpose |
|

### Opening the canvas
After generation, instruct the user:
1. Open Cursor Command Palette (Cmd/Ctrl+Shift+P)
2. Search "Cursor: Open Canvas"
3. Select the generated canvas from the list

Or: Click the "Canvases" icon in the sidebar (if visible) and select the canvas.
