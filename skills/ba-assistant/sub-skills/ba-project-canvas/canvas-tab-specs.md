# Canvas tab specifications, HTML snapshot spec, and pre-delivery self-check
<!-- Wave 10: moved verbatim from SKILL.md. Read together with canvas-generate.md when producing outputs. -->

## Tab specifications

### Overview tab

1. **Workstream strip (replaces old phase strip)** — Pill strip showing initiative-level workstreams with their current state. Use friendly names (Intake, Kickoff, Discovery, Slicing & Sequencing, Solution, Delivery, Playback, Eval & Retro) — NO M-codes. Colour + emoji communicates state (🟢 Done / 🔵 Active / ⏸ Paused / ○ Not started). Multiple workstreams can be `active` simultaneously (this is the whole point of the parallel model).
2. **Top stats** — Grid of 4 stakeholder-readable Stat components. Choose from: days to key deadline (`danger` tone if approaching), features on track (e.g. `"2 / 3"`), active blockers count, decisions confirmed (e.g. `"4 / 5"`). Avoid BA jargon (no "MoSCoW coverage %" on Overview — that lives in Features tab). **Do NOT compute an overall progress %** — initiatives have highly variable workstream durations and a misleading % is worse than none. The workstream strip already communicates progress visually.
3. **"Where we are right now" callout** — 2–4 sentence narrative summary, info tone.
4. **Top blockers grid** — 2×2 grid of Callouts with emoji-prefixed titles (e.g. "🔴 Acquirer C — no commitment for 24 Jun"). No separate "Warnings & Call-outs" section — top blockers cover it.
5. **Where each scope is right now table** — Scope, currently in workstream(s), status (emoji-prefixed plain English).
6. **Confidence table** — Table with Area, Score (emoji-prefixed), Note. Row tones by score (success/warning/danger).

### Workstreams tab (was Modes — renamed in demo iteration)

Shows the full per-scope workstream grid. Primary place to see "where is what".

**Layout — SVG grid:**
- **Y axis (rows):** scopes — Initiative (top, bold), then each feature (bold), then each cohort (indented with `↳` prefix, zebra-striped backgrounds, section divider line above cohort group).
- **X axis (columns):** 8 workstreams with friendly labels — Intake, Kickoff, Discovery, Slicing & Sequencing, Solution, Delivery, Playback, Eval & Retro. NO M-codes shown in user-facing UI.
- **Cells:** rounded rect coloured by state:
  - `not-started` — light grey (theme.fill.tertiary), emoji ○
  - `active` — accent **BLUE** (theme.accent.primary) — NOT amber/brown. Emoji 🔵.
  - `paused` — red wash (theme.diff.stripRemoved). Emoji ⏸.
  - `complete` — green (theme.diff.stripAdded). Emoji 🟢.
  - `na` — 8% opacity grey. Emoji · or blank.
- **Cell content:** emoji + short label (e.g. "🟢 Done", "🔵 Active") with consistent text alignment (centred horizontally and vertically).
- **Cell tooltip:** `${scope.label} — ${workstream.label}: ${state.label}`.
- **Section dividers:** thin hairline between initiative / features / cohorts groups.

**Below the matrix:**
- **Horizontal compact legend (NOT vertical chrome on the side)** — five colour swatches inline with emoji labels: `🟢 Done · 🔵 Active · ⏸ Paused · ○ Not started · · N/A`.
- **Recent workstream changes log:** table of `Date | Scope | Workstream | Change` (row-toned by change type).
- **Active anti-patterns** (from anti-pattern-detector, if any) — table of workstream-related anti-patterns currently flagged.

**Click behaviour:**
- Click a row label (scope) → drills into that scope via the scope navigator.
- Click a cell → shows a panel below with the workstream's recent activity, hooks active for that scope + workstream, and skills involved.

### Workstreams tab — exact SVG dimensions

Reference values from the demo build (use these as defaults — adjust only if scope count justifies it):

```tsx
const cellW = 102;     // workstream column width
const cellH = 32;      // row height per scope
const labelW = 220;    // left label column width
const headerH = 38;    // column header band height
const gap = 2;         // gap between cells

const svgW = labelW + WORKSTREAMS.length * (cellW + gap) + 20;
const svgH = headerH + orderedRows.length * (cellH + gap) + 20;
```

Row ordering: `initiative` first, then `feature`s, then `cohort`s. Cohort rows MUST be indented (`indent = 16`) and prefixed with `"↳ "`. Cohort labels use `fontWeight="500"`; initiative + feature labels use `"700"`. Add a `<line>` divider (`stroke={theme.stroke.secondary}, strokeWidth={1}`) above the first feature row and above the first cohort row.

Zebra striping: `if (ri % 2 === 0)` draw a rect over the label column area only (`opacity={0.15}`, fill `theme.fill.tertiary`) — not across the cells (the cell fills do their own colouring).

Cell text: `state !== "na"` → render `${STATE_EMOJI[state]} ${STATE_LABEL[state]}` centred, `fontSize={10}`, `fontWeight="700"` if state is active otherwise `"500"`. `state === "na"` → render no text, just the faded rect.

### Workstreams tab — empty state

If the initiative is still at Intake (M0) only and no sub-scopes exist yet, the matrix shows only the Initiative row with `intake` active and rest grey. Add a Callout explaining: "Sub-scope workstreams will populate once features and cohorts are defined in Discovery."

### Features & Delivery tab

Receives `isActive: ScopeFilter` prop. Filters items by whether their scope (`feature` or `cohort`) is currently active.

1. **Features in flight table** — Feature, Active workstream(s) (concatenated labels with ` + `, or `—` if none), Owner, Health (emoji-prefixed plain English), Priority cover (%). Row tones: `"success"` for healthy F1, `"warning"` for solutioning F2, `"danger"` for at-risk F3. Filter rows by `s.level === "feature" && isActive(s.id)`.
2. **Stories in flight table** — Title, Feature, Cohort (display short label or "All cohorts"), Priority (MoSCoW), Status (emoji-prefixed), Key (Jira). Row tones: `"danger"` if priority starts with `—` (unrated → blocked), otherwise mapped from status. Filter:
   ```tsx
   const visibleStories = STORIES.filter(
     (st) =>
       isActive(st.feature) ||
       (st.cohort !== "all-cohorts" && isActive(st.cohort)) ||
       (st.cohort === "all-cohorts" && isActive("initiative"))
   );
   ```
3. **MoSCoW priority matrix table** — Rows = requirements, columns = cohorts. Cells = emoji-prefixed rating (`🔴 Must` / `🟡 Should` / `🔵 Could` / `⚪ Won't` / `⚠ — unrated`). The matrix is a single `<Table>` — no separate per-feature card stack.
4. Use plain `Text size="small" tone="secondary"` for explanatory paragraphs above each table.

**MoSCoW emoji + tone mapping (use everywhere MoSCoW appears):**
| Rating | Emoji | Pill tone |
|---|---|---|
| Must | 🔴 | `danger` |
| Should | 🟡 | `warning` |
| Could | 🔵 | `info` |
| Won't | ⚪ | `neutral` |
| (Missing / unrated) | ⚠ | `warning` (text "⚠ Missing" or row prefixed with `🔴 — unrated` if it blocks sprint pickup) |

### Timeline tab (SVG Gantt with Milestones swimlane at TOP)

Receives `isActive: ScopeFilter` prop. Filters lanes AND bars by whether any of their scopes match.

**Layout (mandatory — rebuild MUST follow this):**

1. **Two-line header row** — Top line: actual date (bold, fontSize 10, e.g. "18 May"). Bottom line: short week marker (fontSize 9, tertiary tone, e.g. "wk 1"). Never use bare week codes like "W21" / "W22" as the visible date — use real dates.
2. **Vertical grid lines** every column (dashed `stroke-dasharray="2 4"`, `stroke={theme.stroke.tertiary}`), spanning from `milestoneLaneTop` to `bodyBottom`.
3. **Today line** — vertical dashed BLUE line (`stroke={theme.accent.primary}`, `strokeWidth={2}`, `strokeDasharray="4 4"`) positioned at `labelWidth + todayWeek * colWidth`. Label `"Today"` 4px to the right, 6px above the line, blue + bold.
4. **Deadline line** — vertical dashed RED line (`stroke={colours.blocked}`, `strokeWidth={2}`, `strokeDasharray="6 3"`) positioned at `labelWidth + deadlineWeek * colWidth`. Label `"⛔ <date>"` (e.g. `"⛔ 1 Jul"`) red + bold, immediately right of the line.
5. **Milestones swimlane at the TOP** — a 56px-tall band immediately below the header, faded grey background (`fill={theme.fill.tertiary}, opacity={0.18}`). Lane title `"📅 Milestones"` left-aligned. For each milestone, render a 3-line stack centred on its week:
   - Line 1: emoji at `fontSize={16}`
   - Line 2: label (e.g. "Legal sign-off") at `fontSize={9}`, primary text, `fontWeight="600"`
   - Line 3: date (e.g. "27 May") at `fontSize={9}`, tertiary tone
6. **Team / area swimlanes** below the milestone lane. Lanes are scoped (each lane declares which `scopes` it covers). Only render lanes where `lane.scopes.some(isActive)`. Even-index lanes get a 25% opacity grey background.
7. **Bar packing** — each lane packs its bars into sub-rows so they never overlap. Algorithm:
   ```tsx
   const barRowIndex = new Map<string, number>();
   const laneSubRows = new Map<LaneId, number>();
   filteredLanes.forEach((lane) => {
     const laneBars = filteredBars.filter((b) => b.lane === lane.id);
     const rows: Bar[][] = [];
     laneBars.forEach((bar) => {
       let placed = false;
       for (let i = 0; i < rows.length; i++) {
         const last = rows[i][rows[i].length - 1];
         if (last.startWeek + last.weeks <= bar.startWeek) {
           rows[i].push(bar);
           barRowIndex.set(bar.id, i);
           placed = true;
           break;
         }
       }
       if (!placed) { rows.push([bar]); barRowIndex.set(bar.id, rows.length - 1); }
     });
     laneSubRows.set(lane.id, Math.max(rows.length, 1));
   });
   ```
8. **Bar rendering** — `width = Math.max(bar.weeks * colWidth - 4, 24)`. Fill `colours[bar.status]` at `opacity={0.88}`, `rx={4}`. Label inside the bar: `${itemStatusEmoji(bar.status)} ${bar.label}` at `fontSize={10}`, `fontWeight="500"`, `dominantBaseline="middle"`, 6px left padding.

**Dimensions (defaults from demo):**

```tsx
const colWidth = 92;        // pixel width per week
const rowHeight = 34;       // per-sub-row inside a lane
const labelWidth = 160;     // left label column
const headerHeight = 36;    // date + week-marker header band
const lanePad = 12;
const milestoneLaneH = 56;  // dedicated swimlane height
const milestoneLaneTop = headerHeight + 8;
const lanesStart = milestoneLaneTop + milestoneLaneH + 4;
```

**Data structures:**

```tsx
type LaneId = string; // project-specific (e.g. "ba", "compliance", "f1-eng")
interface Lane { id: LaneId; label: string; scopes: ScopeId[] }

interface Bar { id: string; label: string; lane: LaneId; startWeek: number; weeks: number; status: ItemStatus; scope: ScopeId }

interface Milestone { id: string; label: string; date: string; week: number; emoji: string; lane?: LaneId }
```

**Tooltip text:**
- Bar: `"${bar.label} — ${itemStatusLabel(bar.status)} — scope: ${shortLabel}"`
- Milestone: `"${m.label} — ${m.date}"`

**Legend BELOW the chart, horizontal compact form** (NOT vertical side chrome):
```
Legend:  ▢ 🟢 Done   ▢ 🔵 In progress   ▢ ○ Pending   ▢ 🔴 Blocked
```

Each swatch = 11×11 div with rounded corners. Use `Row gap={4} align="center"` per swatch+label pair, all wrapped in a single `Row gap={12} wrap`.

Add a `Text size="small" tone="tertiary"` line below the legend: `"Bar length = duration in weeks × column width. Bars auto-pack into sub-rows so they never overlap."`

**Date computation rules:**
- `todayWeek = (today - weekZeroDate) / 7` (fractional)
- `deadlineWeek = (deadline - weekZeroDate) / 7` (fractional)
- For sprint-derived planned bars, see Phase 2 step 3g + 3h.
- **Never** shrink an in-progress bar to end at "today". It should extend to a realistic completion estimate past today.

**Forecast / unscheduled bars** — render with `pending` colour + `strokeDasharray="4 2"` border and `"(forecast)"` suffix in the label.

**Timeline accuracy rules (mandatory — never violate these):**

1. **Bar end ≠ status = done.** A bar that visually ends at or before "today" on the chart MUST NOT be coded as `status: "done"` unless the work is actually confirmed complete. If work is in-progress and still ongoing, the bar should extend past today and use `status: "in-progress"`.
2. **Compliance-dependent items are never done until compliance confirms.** Draft requirements, analysis work pending compliance responses, and open questions cannot be marked `done` just because initial drafts exist. Use `in-progress` (ongoing work) or `pending` (not started / waiting).
3. **Start dates reflect actual work start, not sprint start.** A ticket's `startWeek` must come from the Jira changelog "To Do → In Progress" transition date (see step 3g), not from the sprint it was assigned to. If a ticket was created on 14 May and moved to In Progress on 15 May, its startWeek should reflect 15 May — even if the sprint nominally starts on 19 May. Calculate `startWeek` as `(inProgressDate - projectKickoffDate) / 7`.
4. **Label accuracy.** When an item is in-progress and waiting on an external dependency (e.g. compliance responses), reflect this in the label: `"Draft reqs (compliance pending)"`, not just `"Requirements"`.
5. **Never shrink in-progress items to fit "today".** If requirements have been in-progress since wk 1 and are still ongoing, the bar should span from wk 1 to a realistic completion date (e.g. wk 7), not from wk 1 to wk 3 (today). An item that ends at "today" implies it was completed just in time — this is almost always misleading.
6. **Analysis swimlane.** Always include a dedicated Analysis swimlane when a BA is on the project. It should show: intake/scoping, current state analysis, requirements drafting (mark in-progress if compliance not confirmed), process mapping, gap analysis, solution shaping. Do NOT collapse BA work into the compliance or feature swimlanes.
7. **Done tickets use real dates from Jira changelog.** When a ticket is "Done", its bar width must span from the actual "In Progress" date to the actual "Done" date (from changelog, step 3g). If both transitions happened on the same day, use `weeks: 0.5` so the bar remains visible. Never use sprint-length estimates for done work when real dates are available.
8. **Include actual dates in timeline labels.** For done and in-progress tickets, append the start date to the label: `"PROJ-4305 Domain Model (15 May)"`. This makes the timeline self-documenting and verifiable at a glance without needing to cross-reference Jira.
9. **Point-proportional bar width for pending/unstarted tickets.** When a ticket has story points but no real start/end dates yet, calculate bar width using velocity: `weeks = (storyPoints / velocityPerSprint) * sprintLengthWeeks`. For example, at 5 pts/sprint over 2-week sprints: a 2-point ticket = 0.8 weeks, a 3-point ticket = 1.2 weeks. This gives an at-a-glance visual of relative effort. Done and in-progress tickets still use real dates (rules 3 and 7).

### Dependencies tab (Interactive SVG DAG with click-to-highlight)

Receives `isActive: ScopeFilter` prop.

**Above the graph — Active blockers callouts:**
- 1–3 `<Callout>` components (tone="danger" or "warning") for the most urgent blockers, with the same emoji-prefixed titles as the Overview tab.

**Node kinds (use the same colour and shape — vary by `kind`):**
- `external` — vendor / acquirer / partner dependencies (e.g. Acquirer C API)
- `internal` — sign-offs, audits, briefs (e.g. Legal sign-off)
- `story` — Jira tickets (PROJ-XXXX)
- `milestone` — feature go-live, comms send, deadline

```tsx
interface DepNode { id: string; label: string; status: ItemStatus; scope: ScopeId; kind: "external" | "internal" | "story" | "milestone" }
```

**Filter:** `filteredNodes = depNodes.filter((n) => isActive(n.scope) || n.id === "FINAL-DEADLINE")` — always keep the final-deadline node visible regardless of scope so the graph terminates somewhere meaningful.

**Layout (mandatory params):**
```tsx
computeDAGLayout({
  nodes: filteredNodes.map((n) => ({ id: n.id })),
  edges: filteredEdges,
  direction: "horizontal",
  nodeWidth: 132,
  nodeHeight: 44,
  rankGap: 52,
  nodeGap: 18,
});
```

**Interactive selection:**
```tsx
const [selectedNode, setSelectedNode] = useCanvasState<string | null>("dep-selected", null);

const getUpstream = (nodeId: string): Set<string> => { /* BFS over edges where to === nodeId */ };
const getDownstream = (nodeId: string): Set<string> => { /* BFS over edges where from === nodeId */ };

const chain = selectedNode
  ? new Set([...getUpstream(selectedNode), selectedNode, ...getDownstream(selectedNode)])
  : null;
```

**Render rules:**
- Each node = rounded rect, fill from `colours[node.status]`. `opacity={chain && !chain.has(node.id) ? 0.2 : 1}`.
- Each edge: `strokeWidth={chain && chain.has(edge.from) && chain.has(edge.to) ? 2.5 : 1}`, `opacity={chain && !(chain.has(edge.from) && chain.has(edge.to)) ? 0.15 : 0.6}`.
- Arrow markers on edges via `<marker>` in `<defs>`.
- Each node has a `<title>` tooltip: `"<label> — <itemStatusLabel(status)>"`.
- "Clear selection" ghost `<Button>` appears when `selectedNode !== null`.

**Below the graph — Critical chains as horizontal Pill chains:**

Render the most important paths (e.g. Solo cohort path and Business cohort path) as horizontal sequences of `<Pill size="sm">` linked by `<Text size="small" tone="tertiary">→</Text>` separators. Each path lives inside a `<Callout>` with a chain-status title.

**Horizontal compact legend** (same pattern as Workstreams/Timeline):
```
Legend:  🟢 Done   🔵 In progress   ○ Pending   🔴 Blocked
```

### Traceability tab (Interactive SVG DAG)

Same click-to-highlight pattern as Dependencies but **bidirectional** (traces both up and down from the selected node):

```tsx
const [selectedTrace, setSelectedTrace] = useCanvasState<string | null>("trace-selected", null);
```

**Node kinds (use the same colours):**
- ⚖️ `driver` (e.g. Regulatory Mandate) — `theme.diff.stripRemoved`
- 📋 `requirement` — `theme.accent.primary`
- 🍕 `slice` — `theme.fill.secondary`
- 🎟️ `story` — `theme.fill.tertiary`
- 📌 `adr` — `theme.diff.stripAdded`

Each node's label is prefixed with its kind emoji.

**Below the DAG — full traceability table:** Columns `Driver | Requirement | Slice | Stories | ADRs`. Row tone `"info"` for any row matching `selectedTrace`. Row tone `"warning"` for any requirement whose stories include unrated MoSCoW (blocks delivery).

**Horizontal legend** showing the 5 node kinds with their emojis.

Data structure:
```tsx
interface TraceNode { id: string; label: string; kind: "driver" | "requirement" | "slice" | "story" | "adr"; scope?: ScopeId }
interface TraceLink { requirementId: string; requirementText: string; slice: string; stories: string[]; adrs: string[]; moscow?: Record<ScopeId, MoSCoW> }
```

### Critical Path & Actions tab

Receives `isActive: ScopeFilter` prop.

1. **Critical path to deadline table** — Columns: #, Milestone, Date, Status (emoji-prefixed: 🟢 / 🔵 / 🟡 / 🔴 / ⛔ for the deadline), Owner. Row tones map from status. Filter by `isActive(milestone.scope)` where applicable.
2. **Actions due this week table** — Columns: #, Action, Owner, Due, Priority (emoji-prefixed: 🔴 Critical / 🟡 High / 🔵 Medium). Row tones map from priority. Sort by due date ascending.
3. Optional: **MoSCoW warnings callout** if any stories lack MoSCoW for the current scope.

### RAID & Tracker tab

Receives `isActive: ScopeFilter` prop.

1. **Header row** — `<H2>RAID & Tracker</H2>` on the left, `<Checkbox checked={outstandingOnly}>Show outstanding items only</Checkbox>` on the right. **Defaults to CHECKED.**
2. **Five collapsible RAID cards** in this exact order (use icons in summary text):
   - 📌 Decisions — Decision, Made by, Status (emoji-prefixed), ID (small font column)
   - 🧨 Risks — Risk, Owner, Severity (🔴 HIGH / 🟡 MEDIUM / 🔵 LOW), ID
   - ❓ Open questions — Question, Owner, Status, ID
   - ⚠️ Assumptions — Assumption, Owner, Confidence, ID
   - 🎯 Actions — Action, Owner, Status, ID
3. **Summary in card header** — `📌 Decisions (5 total · 1 outstanding)` so the user sees the count at a glance without expanding.
4. **ID column placement** — IDs (DEC-001, R-001 etc) MUST be the LAST column with small font/secondary tone. Descriptions get the prime column. This was a specific user requirement.
5. **Outstanding-only filter logic** — when `outstandingOnly === true`, hide rows whose status maps to one of: `"Confirmed", "Closed", "Resolved", "Done", "Agreed", "Approved", "Moot", "Dropped", "Booked"`. Mark each row with a `data-outstanding="true|false"` attribute (HTML) or an `outstanding: boolean` flag (canvas) so the filter is single-pass.
6. **Scope filtering** — Every tracker item carries a `scope` field. Filter by `isActive(item.scope)`. Show a small `Text size="small" tone="secondary"` note at the top: "Showing tracker items for: <scope name>" when not initiative-level.
7. **Decisions table MUST include Made by + Status** — this matches `jess-ba-profile.mdc`'s "Decisions must be recorded as a table" requirement.
8. By default Decisions, Risks, and Actions cards open; OQs and Assumptions cards closed (use `defaultOpen` per card).
9. **Do NOT render a HorizontalBarChart in this tab in the rebuild iteration** — the user feedback was that the page had too much duplication; counts in card headers do the same job in less space.

## Data extraction rules

### From initiative tracker / project hub

1. **Confidence scores** → Table (no chart). Map each area to High/Medium/Low.
2. **Decisions** → ID, Decision (truncate ~80 chars), Owner, Date, Status
3. **Risks** → ID, Risk, Severity, Mitigation, Owner, Status
4. **Status mapping** for row tones:
   - "Confirmed" / "Closed" / "Resolved" / "Done" / "Agreed" → `"success"`
   - "In Progress" / "In flight" → `"info"`
   - "Open" → `undefined` (no tone)
   - "Blocked" / "Critical" → `"danger"`
   - "Monitor" / "Pending" / "TBC" / "Gated" → `"warning"`
   - "Deferred" / "Moot" / "Conditional" → `"neutral"`

### From Jira MCP

- Epic status → overall project status
- Story statuses → Features & Delivery tab population. **Always prefer Jira status over markdown status.**
- Story dependencies (linked issues, "is blocked by") → Dependencies tab edges
- Sprint assignment → Timeline tab positioning
- Story labels/components → swimlane/feature grouping

### From Confluence MCP

- Decision logs → RAID Decisions table
- RAID pages → direct population of tracker tab
- Requirements pages → Traceability tab
- Status pages → verify/supplement Overview tab

## Scaling for large projects

For projects with 100+ stories/items:

1. **Feature filter** — always include. Scopes every filtered tab to one workstream at a time.
2. **Collapsible cards** — use `Card collapsible defaultOpen={false}` for detail sections.
3. **Striped + stickyHeader tables** — set `striped` and `stickyHeader` props on large tables.
4. **Pagination** — for very large datasets, add pagination with `useCanvasState("page", 0)` and "Show more" buttons.
5. **DAG layout** — `computeDAGLayout` adapts to node count. For 50+ nodes, increase `rankGap` and use the feature filter to show subsets.

## Pre-delivery self-check

Before returning canvas code, verify EVERY item. This list grew from real demo-iteration failures — skipping any item likely reintroduces a known regression.

### Structural

1. All imports exist in `cursor/canvas` (the only allowed import source). `Button, Callout, Card, CardBody, CardHeader, Checkbox, computeDAGLayout, Divider, Grid, H1, H2, H3, Pill, Row, Spacer, Stack, Stat, Table, Text, useCanvasState, useHostTheme` is the canonical set.
2. No `fetch()`, no external imports, no npm packages.
3. Data is inline (embedded in the `.canvas.tsx`).
4. `useCanvasState` keys are unique strings across the file (collisions silently overwrite state).
5. Default export, PascalCase component name, function components only.
6. **ALL 8 sections exist** as TabId: `overview | workstreams | features | timeline | dependencies | traceability | critical-path | tracker`. NEVER fewer.

### Scope navigator (demo iteration UX contract)

7. `useCanvasState<ScopeId[]>("selectedScopes", ["initiative"])` default state is `["initiative"]`.
8. Three visually-grouped pill clusters with `|` separators (`Text size="small" tone="tertiary"`).
9. "🏛️ Initiative level" pill has `🏛️ ` prefix and `✓ ` prefix when active. Tone `"info"` when active, `"neutral"` when inactive.
10. Clicking "Initiative level" clears all other selections.
11. Clicking a feature/cohort auto-deselects "Initiative level".
12. If `next.length === 0` after a toggle, snap back to `["initiative"]` (never empty).
13. `filterDescription` line is `Text size="small" tone="secondary"` — plain-English, includes "click 'Initiative level' to reset".
14. Every tab takes `isActive: ScopeFilter` callback (NOT a single `activeScope` object).
15. EVERY tab actually FILTERS using `isActive` — Overview, Workstreams, Features, Timeline, Dependencies, Traceability, Critical Path, Tracker. **The most common regression is sections that ignore `isActive` and show all data regardless.**

### Workstreams (terminology + visuals)

16. Label is "Workstreams" (NOT "Modes"). 8 columns (NOT 9). Eval & Retro is a single merged column.
17. NO `M0`/`M1`/.../`M8` codes anywhere in the user-facing UI.
18. Cohort rows indented with `↳ ` prefix.
19. Section divider lines above the first feature row AND above the first cohort row.
20. Zebra striping on every even-indexed row (label column only, `opacity={0.15}`).
21. In-progress cells fill is `theme.accent.primary` (BLUE). NEVER amber / brown / orange.
22. Each cell renders `${STATE_EMOJI[state]} ${STATE_LABEL[state]}` centred — NOT just the abbreviation.
23. Horizontal compact legend BELOW the grid (NOT vertical chrome on the side).

### Timeline

24. Date column headers in REAL DATES ("18 May", "25 May"…) — NOT week codes ("W21", "W22").
25. Two-line header: date (bold, fontSize 10) on top, "wk N" (fontSize 9, tertiary tone) below.
26. **Milestones swimlane at the TOP** (between header and team lanes). 56px tall, light grey background, `"📅 Milestones"` label.
27. Each milestone renders as a 3-line stack: emoji (16px) → label (9px) → date (9px tertiary).
28. **Today line** vertical BLUE dashed (`stroke={theme.accent.primary}`, `strokeDasharray="4 4"`, `strokeWidth={2}`), with "Today" label.
29. **Deadline line** vertical RED dashed (`stroke={colours.blocked}`, `strokeDasharray="6 3"`, `strokeWidth={2}`), with "⛔ <date>" label.
30. Bars auto-pack into sub-rows (no overlaps). Use the documented packing algorithm.
31. Bar width = `Math.max(bar.weeks * colWidth - 4, 24)`.
32. Bar label inside the bar: `${itemStatusEmoji(bar.status)} ${bar.label}` — emoji-prefixed.
33. Lanes filtered by `lane.scopes.some(isActive)`.

### DAGs (Dependencies + Traceability)

34. `computeDAGLayout` nodes have unique IDs; edges reference valid node IDs only.
35. Click-to-highlight uses BFS for Dependencies (upstream + downstream) and bidirectional for Traceability.
36. Unrelated nodes dim to `opacity: 0.2`; unrelated edges to `opacity: 0.15`.
37. Selected chain edges get `strokeWidth: 2.5`.
38. Arrow markers defined in SVG `<defs>` for both DAGs.
39. "Clear selection" ghost Button appears when a node is selected.
40. Every node has a `<title>` element with full hover context.
41. Below the Dependencies DAG: Critical chains rendered as horizontal Pill chains inside Callouts.

### Emojis + colour

42. Real Unicode emojis throughout: 🟢 🔵 🔴 🟡 ⏸ ⛔ 📅 🚀 ⚖️ 📧 📊 🧨 ⚠️ 📌 📋 🍕 🎟️ 🏛️ 🎯 ❓ ↳. NEVER ASCII substitutes (`✓`, `●`, `○` — `○` is acceptable for "not started" inside the workstream grid only).
43. Status colour mapping is consistent across ALL tabs: Done=green, In-progress=BLUE, Pending=grey, Blocked=red.

### RAID & Tracker

44. `useCanvasState<boolean>("outstandingOnly", true)` defaults to `true` (Checkbox checked).
45. Five RAID cards in order: 📌 Decisions, 🧨 Risks, ❓ Open questions, ⚠️ Assumptions, 🎯 Actions.
46. Card headers show count summary: "📌 Decisions (5 total · 1 outstanding)".
47. ID column LAST in every RAID table, small font / secondary tone. Descriptions get the prime column.
48. Decisions table includes "Made by" column (per `jess-ba-profile.mdc`).

### Overview

49. 4 stakeholder-readable Stat tiles (NOT MoSCoW % / velocity jargon as the headline metrics).
50. "Where we are right now" callout in info tone.
51. 2×2 Top blockers grid with emoji-prefixed titles (e.g. "🔴 Acquirer C — no commitment for 24 Jun"). No separate "Anti-pattern" / "Warnings & Call-outs" section — top blockers cover it.

### Legends

52. Every visual (Workstreams grid, Timeline, Dependencies, Traceability) has a HORIZONTAL compact legend BELOW it, not vertical chrome.
53. Legends use `Row gap={4} align="center"` per swatch+label pair, wrapped in `Row gap={12} wrap`.

### Theme tokens

54. All SVG fills/strokes use theme tokens via `useStatusColours()` or `useHostTheme()`. No hardcoded hex.
55. Tables use `rowTone` for semantic status colouring (NEVER inline `style={{ background: ... }}`).
56. Empty tabs show informative Callout prompts (not blank).

### Critical failure mode to prevent

**The most common failure is producing fewer than 8 tabs (was 7 pre-Wave 3).** This happens when:
- The agent doesn't read the SKILL.md fully and invents its own tab structure
- The agent reads some project files but not all, and decides some tabs "aren't needed"
- The agent replaces a required tab with a project-specific tab (e.g. "Compliance" instead of "Traceability")
- The agent forgets the Workstreams tab (Wave 3, was "Modes")

**Prevention:** The 8 tabs are fixed by design. Project-specific content goes INSIDE the tabs, not as replacement tabs. For example:
- Compliance decisions go in the **RAID & Tracker** tab (decisions section)
- Cohort models go in the **Traceability** tab (requirement → slice → story mapping) AND **Features tab** (cohort cards when a feature is in scope)
- Workshop schedules go in the **Critical Path** tab (milestones/actions)
- Per-feature/cohort workstream state goes in the **Workstreams** tab (NOT in Features — Features shows status summary; Workstreams shows the full grid)
- MoSCoW gaps go in **Tracker** (warnings section) and **Overview** (warning callouts)

### HTML snapshot output (mandatory — same 8 sections)

On every `/status` or `/canvas` invocation, generate (or overwrite) a standalone HTML file at:

```
<project-analysis-folder>/status-snapshot.html
```

For example: `blueprints/Project 002 - sample-initiative/outputs/status-snapshot.html`

**The HTML file MUST:**
- Be a **single self-contained file** (inline CSS + inline JS, no external dependencies, no CDN links)
- Use the **same data** as the canvas — same feature status, decisions, risks, milestones, actions, dependencies
- Have **interactive tab navigation** (JavaScript `onclick` to show/hide tab panels)
- Include all **8 sections** matching the canvas tabs (Wave 3, refined in canvas demo iteration May 2026):
  1. **Overview** — stakeholder-readable stats (Days to deadline, Features on track, Active blockers, Decisions confirmed), "Where we are right now" callout, Top blockers grid (no separate "Warnings & call-outs" section), Where each scope is, Confidence table — all rows emoji-prefixed
  2. **Workstreams** — Workstream grid (HTML table with scopes as rows and **8 workstreams** as columns: Intake, Kickoff, Discovery, Slicing & Sequencing, Solution, Delivery, Playback, Eval & Retro). NO M0–M8 codes in the user-facing UI. Cells coloured by state (🟢 Done, 🔵 Active, ⏸ Paused, ○ Not started, · N/A). Cohort rows indented with `↳` prefix and zebra-striped. Section divider lines between initiative / features / cohorts groups. Horizontal compact legend BELOW the grid. Recent workstream changes log below.
  3. **Features & Delivery** — feature table with active workstreams pill, cohort/slice cards when a feature is in scope, Jira ticket table with MoSCoW column (emoji-prefixed: 🔴 Must, 🟡 Should, 🔵 Could, ⚪ Won't, ⚠ unrated), MoSCoW matrix table per requirement
  4. **Timeline** — HTML/CSS Gantt with **Milestones swimlane at the TOP** (each milestone = emoji + label + date stacked below, e.g. "⚖️ / Legal sign-off / 27 May"), then team/area swimlanes (BA Analysis, Compliance/Legal, F1 Eng, F2 Comms, F3 Reporting). Vertical **blue dashed Today line** + vertical **red dashed Deadline line** with ⛔ date label. Bar length = duration in weeks × column width. Bars auto-pack into sub-rows so they never overlap. Date column headers in actual dates (e.g. "18 May, 25 May…") NOT week codes (W21, W22). Horizontal compact legend below.
  5. **Dependencies** — Active blockers callouts at top, then static rendering of the dependency DAG (HTML table showing From → To with status colours, or inline SVG with click-to-highlight if feasible). Critical chains shown as horizontal pill chains beneath.
  6. **Traceability** — table-based: ⚖️ Driver → 📋 Requirement → 🍕 Slice → 🎟️ Story → 📌 ADR mapping with colour coding. Requirement rows show MoSCoW pills per scope.
  7. **Critical Path & Actions** — milestone table with status emoji pills, this-week actions from action register, MoSCoW warnings if any, workshop schedule
  8. **RAID & Tracker** — RAID cards (📌 Decisions, 🧨 Risks, ❓ Open Questions, ⚠️ Assumptions, 🎯 Actions) using `<details>/<summary>` collapsibles. **"Show outstanding items only" toggle defaults to CHECKED** (so the page opens to what needs attention). IDs in the last column with small font; descriptions get the prime column.
- **Scope navigator** rendered above the tab strip with three visually-grouped pill clusters separated by `|`:
  - "🏛️ Initiative level" pill (default selected, blue/info tone with ✓ prefix when active)
  - Feature pills (F1, F2, F3)
  - Cohort pills
  - **UX rules:** Clicking "Initiative level" clears all other selections. Clicking a feature or cohort auto-deselects "Initiative level". If all selections cleared, snap back to "Initiative level". A "Showing: X, Y, Z" line directly below the pills shows the active filter state in plain text. Selected pills get a ✓ prefix and `info` tone; unselected pills `neutral` tone.
- Be viewable in **any modern browser** without a dev server or build step
- Include a **"Generated" timestamp** and version in the footer
- Include **project name, date, BA/PM/TL names** in a header
- Use a **clean, professional layout** with:
  - CSS variables for status colours. **In-progress MUST be BLUE (`#3b82f6`)**, never amber/brown. Done = green, Pending = grey, Blocked = red.
  - Responsive design (works on mobile and desktop)
  - `<details>/<summary>` for collapsible RAID sections (native HTML, no JS library needed)
  - Horizontal bar charts rendered as inline SVG (same visual as canvas `HorizontalBarChart`)
  - Timeline Gantt rendered as inline SVG (matches the canvas pattern — swimlanes as rect rows, bars as positioned rects, today/deadline as vertical dashed lines, milestone strip as the TOP lane)
  - Workstream grid rendered as inline SVG (consistent cell positioning, hover tooltips, zebra row backgrounds, section dividers between scope groups)
  - All legends rendered horizontally as small inline elements below their visual (not vertical lists in the page chrome)
  - Tab navigation via simple JS that shows/hides `<section>` elements
- **Emoji set (use real Unicode, never ASCII shapes):**
  - Status: 🟢 Done, 🔵 In progress / Active, 🔴 Blocked / At risk, 🟡 At risk / Medium, ⏸ Paused, ○ Not started / Pending, ⛔ Hard deadline / Blocker
  - Workstream / scope markers: 🏛️ Initiative level, ↳ Indent for cohorts
  - Milestones: 📅 Date, 🚀 Launch, ⚖️ Legal sign-off, 📧 Comms send, 📊 Reporting milestone
  - RAID cards: 📌 Decisions, 🧨 Risks, ❓ Open questions, ⚠️ Assumptions, 🎯 Actions
  - Traceability node kinds: ⚖️ Driver, 📋 Requirement, 🍕 Slice, 🎟️ Story, 📌 ADR
  - Never use ASCII substitutes (`✓ ● ○ —`) where Unicode emoji is available

**HTML template structure:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Project Name] — Status as at [Date]</title>
  <style>
    :root {
      --done: #22c55e; --in-progress: #3b82f6; --pending: #9ca3af;
      --blocked: #ef4444; --conditional: #d1d5db;
      --bg: #ffffff; --text: #1f2937; --muted: #6b7280;
      --border: #e5e7eb; --card-bg: #f9fafb;
    }
    @media (prefers-color-scheme: dark) {
      :root { --bg: #111827; --text: #f3f4f6; --muted: #9ca3af; --border: #374151; --card-bg: #1f2937; }
    }
    /* ... full responsive layout styles ... */
  </style>
</head>
<body>
  <header><!-- Project name, date, stakeholders --></header>
  <div class="scope-nav"><!-- Breadcrumb: Initiative ▸ Feature ▸ Cohort/Slice + Clear scope button --></div>
  <nav><!-- 8 tab buttons --></nav>
  <main>
    <section id="tab-overview"><!-- Stakeholder stats, "where we are right now" callout, Top blockers grid, Where each scope is, Confidence --></section>
    <section id="tab-workstreams"><!-- SVG workstream grid: scopes as rows (cohorts indented + zebra striped), 8 workstreams as columns (Intake → Eval & Retro), no M-codes. Horizontal legend below. Transitions log. --></section>
    <section id="tab-features"><!-- Feature table with active workstreams, cohort/slice cards, Jira tickets with MoSCoW column (emoji-prefixed), MoSCoW matrix --></section>
    <section id="tab-timeline"><!-- SVG Gantt with Milestones swimlane at TOP, then team lanes. Today + Deadline vertical lines. --></section>
    <section id="tab-dependencies"><!-- Active blockers callouts, dependency DAG, critical chains --></section>
    <section id="tab-traceability"><!-- ⚖️ Driver → 📋 Requirement → 🍕 Slice → 🎟️ Story → 📌 ADR with MoSCoW pills per scope --></section>
    <section id="tab-critical-path"><!-- Milestones with status emojis, actions from register, MoSCoW warnings, workshops --></section>
    <section id="tab-tracker"><!-- RAID cards (📌🧨❓⚠️🎯) with <details> collapsibles, "Show outstanding only" toggle defaults true --></section>
  </main>
  <footer><!-- Generated timestamp, version --></footer>
  <script>
    // Tab switching logic (vanilla JS, ~10 lines)
    document.querySelectorAll('nav button').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('main > section').forEach(s => s.hidden = true);
        document.getElementById('tab-' + btn.dataset.tab).hidden = false;
        document.querySelectorAll('nav button').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });

    // Scope navigator (Wave 3) — sets body[data-scope-level] and body[data-scope-id]
    // CSS rules using [data-scope-level="feature"] [data-scope-id="..."] hide non-matching rows.
    // Each scope-aware row in tables/cards has data-scope-level and data-scope-id attributes.
    document.querySelectorAll('.scope-nav [data-scope]').forEach(btn => {
      btn.addEventListener('click', () => {
        const level = btn.dataset.scopeLevel;
        const id = btn.dataset.scopeId;
        document.body.dataset.scopeLevel = level;
        document.body.dataset.scopeId = id;
        // Update breadcrumb visible state
        document.querySelectorAll('.scope-nav .crumb').forEach(c => c.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  </script>
</body>
</html>
```

**HTML-specific visualizations (replace canvas SDK components):**

| Canvas component | HTML equivalent |
|---|---|
| `Stat` | `<div class="stat"><span class="stat-value">X</span><span class="stat-label">Y</span></div>` |
| `Pill` | `<span class="pill pill--done">Done</span>` (CSS classes for tone) |
| `Table` | `<table class="status-table">` with `<tr class="row-tone-success">` |
| `Callout` | `<div class="callout callout--danger"><h4>Title</h4><p>Body</p></div>` |
| `Card collapsible` | `<details><summary>Title (N items)</summary><div>Content</div></details>` |
| `HorizontalBarChart` | Inline `<svg>` with same bar logic (copy the pattern from canvas template) |
| `computeDAGLayout` | Render as a styled table: columns = From, To, Status, Type. Or inline SVG if simple. |
| Timeline swimlane | CSS Grid: `grid-template-columns: 140px repeat(N, 90px)` with positioned bar `<div>`s |
| `useCanvasState` tab nav | `<nav><button data-tab="overview" class="active">Overview</button>...</nav>` + JS |

**Story points and velocity in HTML:**
- Feature and Jira ticket tables include an `SP` column. Median-filled values rendered as `<em>3 (est.)</em>`.
- Overview stats include a "Team velocity" stat (e.g. `"12 pts/sprint"`).
- Timeline forecast bars use `pending` colour with `border-style: dashed` and italic label text with `"(forecast)"` suffix.

This HTML snapshot serves as a portable, shareable status page that can be opened outside Cursor, attached to emails, or published to Confluence as an attachment.


---

## Reference implementation

If a previously generated canvas and HTML snapshot exist anywhere in the workspace (from an earlier initiative), treat the most recent pair as the canonical reference for pattern, dimensions, naming, and filter behaviour — read both files when in doubt rather than re-deriving the structure from scratch. On a fresh install with no prior example, build strictly from the tab specifications and non-negotiable requirements above. The pre-delivery self-check above was distilled from real regressions caught during iterative demo feedback.
