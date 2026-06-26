# BA Project Canvas

Generate and maintain an interactive Cursor Canvas dashboard for any BA/PM initiative. The canvas provides a visual, tabbed overview of project state â€” a living status board you can open beside the chat.

**This skill is self-bootstrapping.** It works whether or not the user has previously run the BA Assistant, whether or not project files exist, and regardless of project maturity. It gathers its own context, adapts to what's available, and produces the canvas.

> **Cross-cutting rule:** This skill produces multiple artefact-class outputs (canvas .tsx, status-snapshot.html, status-data.json, optionally intake-form.canvas.tsx). Before generating outputs, apply the **"What I'll produce next" declaration** rule from `ba-assistant\SKILL.md â†’ Co-thinking and artefact production protocol` â€” surface planned artefacts upfront and ask the user to select. Auto-generation triggers (`/canvas`, `/status`, end-of-Phase-0, every phase gate) are the highest-volume invocation points.

---

## NON-NEGOTIABLE REQUIREMENTS (read these first)

These rules MUST be followed on every canvas generation or refresh. Failure to follow these rules produces an incomplete, broken output.

### 1. ALWAYS produce exactly 8 tabs (Wave 3 â€” was 7)

Every canvas MUST contain these 8 tabs in this order:

```
type TabId = "overview" | "workstreams" | "features" | "timeline" | "dependencies" | "traceability" | "critical-path" | "tracker";
```

**Never omit a tab.** If data is insufficient for a tab, render the tab with an empty-state Callout explaining what's needed. Never replace these 8 tabs with different tabs (e.g. a "Compliance" tab is NOT a substitute for Traceability or Timeline).

**Wave 3 + demo iteration (May 2026) â€” what's new:**
- **Workstreams tab (2nd, was "Modes")**: shows the workstream grid per scope. The 8 workstreams (no M-codes in the user-facing UI) across the top: Intake, Kickoff, Discovery, Slicing & Sequencing, Solution, Delivery, Playback, Eval & Retro. Scopes down the side (cohorts indented with `â†³` and zebra-striped, divider lines between initiative/features/cohorts groups). States in cells: ðŸŸ¢ Done, ðŸ”µ Active, â¸ Paused, â—‹ Not started, Â· N/A. **In-progress MUST be BLUE.** Compact horizontal legend BELOW the grid (not vertical chrome). The internal data model field may still be `modes` for backwards compat; section ID and all labels use "Workstreams".
- **Scope navigator (top of canvas, above tabs)**: hierarchical multi-select pill cluster with three visually-grouped sections separated by `|`: (1) "ðŸ›ï¸ Initiative level" pill (default selected, blue/info tone, âœ“ prefix when active), (2) feature pills, (3) cohort pills. **UX contract:**
  - Clicking "Initiative level" clears all other selections.
  - Clicking a feature/cohort auto-deselects "Initiative level".
  - If all selections cleared, snap back to "Initiative level" (never empty).
  - Show a "Showing: X, Y, Z" line in plain text below the pills.
  - Selected pills get a âœ“ prefix and `info` tone; unselected pills `neutral`.
  - ALL tabs become scope-filtered when a sub-scope is selected.
- **MoSCoW matrix**: visible in Features tab (per requirement, emoji-rated) and surfaced as warnings (warn-and-flag) in Tracker tab and Overview tab.
- **Tracker tab gains Actions section**: action register is a first-class collection alongside Decisions/Risks/OQs/Assumptions. RAID cards use icons (ðŸ“ŒðŸ§¨â“âš ï¸ðŸŽ¯). **"Show outstanding only" toggle defaults to CHECKED** so the section opens to what needs attention.
- **Timeline**: real Gantt with **Milestones swimlane at the TOP** (each milestone = emoji + label + date stacked, e.g. "âš–ï¸ / Legal sign-off / 27 May"), then team lanes (BA Analysis, Compliance/Legal, F1 Eng, F2 Comms, etc). Vertical **blue dashed Today line** + vertical **red dashed Deadline line** with â›” date label. Bar length = `weeks Ã— colWidth âˆ’ 4`. Bars auto-pack into sub-rows so they never overlap. Date headers in actual dates (e.g. "18 May, 25 Mayâ€¦"), NOT week codes (W21, W22).
- **Emoji set**: use real Unicode throughout â€” ðŸŸ¢ ðŸ”µ ðŸ”´ ðŸŸ¡ â¸ â›” ðŸ“… ðŸš€ âš–ï¸ ðŸ“§ ðŸ“Š ðŸ§¨ âš ï¸ ðŸ“Œ ðŸ“‹ ðŸ• ðŸŽŸï¸ ðŸ›ï¸. Never use ASCII shapes (`âœ“ â— â—‹ â€”`) where Unicode emoji is available.
- **Eval & Retro merged**: previously separate workstreams Evaluation and Retro are now one column "Eval & Retro" (8 columns total, not 9).

### 2. ALWAYS read ALL project files before generating

Before writing any canvas code, you MUST read every `.md` file in the project's analysis folder and any related project directories. This is mandatory, not optional. See Phase 2 Step 2 for the exhaustive list. If you skip reading files, you will produce an inaccurate or incomplete canvas.

### 3. ALWAYS produce both outputs

Every invocation produces TWO files:
1. **`.canvas.tsx`** â€” the Cursor Canvas (interactive, 8 tabs)
2. **`status-snapshot.html`** â€” a standalone HTML file (interactive, 8 tabs, self-contained)

Both files use the same data and the same 8-tab structure.

### 4. Canvas MUST include these interactive features

- Multi-select feature filter (Pills)
- Click-to-highlight in Dependencies DAG (BFS traversal)
- Click-to-highlight in Traceability DAG (bidirectional traversal)a
- Collapsible RAID cards
- Open/Closed filter toggle
- Hover tooltips on DAG nodes and Critical Chain pills
- `computeDAGLayout` for both DAGs
- `useStatusColours()` for consistent colouring

### 5. Context gathering is MANDATORY, not optional

The agent MUST exhaustively read project context before generation. The "Ask the user" step is a FALLBACK for gaps â€” not the starting point. Read files first, ask questions only for what's genuinely missing.

### 6. PM-approval banner is MANDATORY on Phase 0 outputs (added May 2026 after RBA demo retro)

Whenever `status-data.json â†’ initiative.pmApproval.status` is `pending` or `requested` (the default for all Phase 0 outputs), the canvas AND the HTML snapshot MUST display a prominent banner at the top of every tab:

```
âš ï¸ DRAFT â€” pending approval from <pmName>
Problem statement, success metrics, scope, and RAID are draft v1 outputs. Do not treat as authoritative until PM sign-off is captured.
```

Banner styling: amber/warning tone, full width, sticky at top of canvas viewport, dismissible only when `pmApproval.status === 'approved'`. The status-snapshot HTML must mirror it exactly.

If the data model has `initiative.pmApproval` absent (legacy projects pre-May 2026), treat as `status: 'pending', pm: 'TBC'` and show the banner with `pm = 'TBC â€” capture in intake hook 6'`.

This banner is non-negotiable for Phase 0 outputs. The Anti-Pattern Detector watches for v1 artefacts without PM approval state captured.

---

## When to invoke

- User runs `/canvas` within a BA Assistant session
- User asks for a "project canvas", "project dashboard", "visual status", or "generate canvas"
- **At Phase 0 intake completion (auto-generate, mandatory)** â€” initial canvas with mostly empty-state callouts. Acts as a visual roadmap of what comes next.
- At Phase 1 kickoff completion (auto-generate) â€” populated with stakeholders, scope, RAID
- After any phase gate (refresh)
- **After any major decision logged or RAID item added (refresh)** â€” keeps the canvas live as the conversation progresses, not just at gates
- User runs `/status` (canvas is refreshed as a side-effect)
- First time a new user runs the skill on an existing project

### Phase 0 initial canvas â€” what to expect

When invoked at Phase 0 end (hook 5 of the Intake Reviewer skill), the canvas
will be sparse by design. Most tabs will show empty-state Callouts. This is
**not a failure mode** â€” the empty states explain what each tab will hold and act
as a roadmap for the user. Tell the user explicitly:

> "Canvas generated at `<path>`. It's mostly empty-state at this point â€” it will
> fill in as we work through the phases. Open it now so you can see progress
> visually from here on."

At Phase 0, the canvas typically contains:
- **Overview** â€” initiative name, current phase pill (Phase 0), confidence scores (all Low/Unknown), workspace context
- **Features & Delivery** â€” empty-state Callout explaining slices will appear after Phase 3
- **Timeline** â€” single Analysis swimlane with the intake bar
- **Dependencies** â€” empty-state Callout
- **Traceability** â€” empty-state Callout
- **Critical Path & Actions** â€” initial actions (kickoff meeting prep, MCP pre-search findings to action)
- **RAID & Tracker** â€” draft RAID from intake, unknowns, assumptions

### "After major decision" refresh â€” when to trigger

Trigger a canvas refresh (lightweight â€” just overwrite both files with current
tracker state) when any of these happen mid-phase:

- A decision is recorded in the living tracker (ðŸ“Œ)
- A risk is logged or its severity changes (ðŸ§¨)
- A dependency is added or resolved (ðŸš§)
- A sign-off is captured (âœ…)
- A feature slice is confirmed or deferred (Phase 3+)
- A solution option is selected (Phase 4+)

This is in addition to phase-gate refreshes. Do not refresh after every user reply â€”
only when something material has changed in the tracker.

---

## Intake Form Canvas (Wave 4 â€” NEW)

Some BAs prefer a **form-style UI** for capturing initiative intake rather than answering questions sequentially in chat. The Intake Form Canvas is a **separate canvas variant** that renders all intake fields as editable inputs in a Cursor Canvas. The BA fills the form, copies the auto-generated JSON output, and pastes it back into chat â€” the assistant reads the JSON and populates `status-data.json`.

### When to generate the intake form canvas

At the very start of Phase 0 (before the chat-style intake conversation), the orchestrator should offer:

```
> Running: Project Canvas â†’ offering intake form canvas option

How would you like to capture intake context?
[ ] Chat-style â€” I'll ask you questions one at a time (default, recommended for first-time users)
[ ] Form canvas â€” I'll generate an interactive form you can fill in beside the chat (faster if you already have most context handy)
[ ] Both â€” generate the form canvas AND start the chat conversation in parallel
```

If the user picks form canvas or both, this skill generates `intake-form.canvas.tsx` and tells the user how to use it.

### File location

```
<workspace-root>/canvases/<initiative-slug>-intake-form.canvas.tsx
```

E.g. `canvases/rba-surcharge-ban-intake-form.canvas.tsx`.

### Template structure

The intake form canvas is a single `.canvas.tsx` file. It MUST follow these rules:

1. **Imports only from `cursor/canvas`** â€” same as any canvas (no fetch, no network).
2. **Uses `useCanvasState<T>(key, initial)`** for every input field so values persist as the BA edits.
3. **Renders a "Copy this JSON" panel at the bottom** that shows the current form state formatted as JSON. The BA copies it and pastes back to chat.
4. **Groups fields into sections** matching the form-style intake screens (Workspace IDs, Templates and context, Problem and metrics, Stakeholders, RAID seed).
5. **Validation cues** â€” fields that are required for proceeding to Phase 1 show a small `required` label; the JSON output flags any missing required fields with `"_missing": [...]`.

### Sections and fields

| Section | Field | Type | Required |
|---|---|---|---|
| **1. Workspace IDs** | Jira project key | Text | Yes |
|  | Confluence space + parent page URL | Text | Yes |
|  | All-in-one / intake doc link | URL | No |
|  | Slack / Teams channel | Text | No |
| **2. Templates and context** | Jira template story key | Text (e.g. PROJ-XXXX) | No |
|  | Use most recent story as template? | Toggle | No |
|  | Repositories in scope | Multi-line text | No |
|  | Source of intake | Dropdown (verbal / all-in-one / Confluence page / BRD / Jira ticket) | Yes |
|  | Stakeholders already involved | Multi-line text | No |
| **3. Initiative basics** | Initiative name | Text | Yes |
|  | Complexity signal | Dropdown (lean / standard / full) | Yes |
|  | Stage | Dropdown (M0 Intake / M1 Kickoff / further) | Yes |
|  | PM name | Text | Yes |
|  | BA name | Text | Yes |
|  | Tech Lead name | Text | No |
|  | Charter / brief URL | URL | No |
| **4. Problem + success metrics** | Provisional problem statement | Multi-line text | Yes |
|  | Provisional success metrics | Multi-line text | Yes |
|  | Known target customers / personas | Multi-line text | No |
| **5. Scope** | In scope | Multi-line text | Yes |
|  | Out of scope | Multi-line text | No |
|  | Dependencies known so far | Multi-line text | No |
| **6. RAID seed** | Known risks | Multi-line text (one per line) | No |
|  | Known assumptions | Multi-line text | No |
|  | Known issues | Multi-line text | No |
|  | Open questions | Multi-line text | No |

### Copy JSON panel

At the bottom of the canvas, render a section that shows the form state as JSON, ready to paste back to chat:

```
## Copy this JSON and paste it back to chat

```json
{
  "initiative": {
    "name": "[Initiative Name]",
    "code": "",
    "stage": "M0",
    "complexity": "standard",
    "pm": "Alex",
    "ba": "[BA Name]",
    "techLead": "",
    "charterUrl": "https://...",
    "jiraProjectKey": "FCM",
    "confluenceSpace": "FSP",
    "allInOneDocUrl": "https://...",
    "slackChannel": "#[initiative-channel]",
    "jiraTemplate": { "sourceKey": "PROJ-099" }
  },
  "problem": "...",
  "metrics": [ "..." ],
  "scope": { "in": [ "..." ], "out": [ "..." ] },
  "raid": { "risks": [ ... ], "assumptions": [ ... ], "issues": [], "openQuestions": [ ... ] },
  "_missing": []
}
```
```

Use the canvas `Code` component (or equivalent) so the BA can click-to-copy.

### Honest limitations (Wave 4 documentation)

Cursor canvases are **display-only**. They cannot write directly to chat or to a file the assistant reads automatically. The pattern is:

1. Assistant generates `intake-form.canvas.tsx` and tells the user where it is.
2. User opens the canvas (Command Palette â†’ "Cursor: Open Canvas").
3. User fills the form. State persists within the canvas as they edit (`useCanvasState`).
4. User clicks the "Copy this JSON" panel and copies the JSON.
5. User pastes the JSON into chat.
6. Assistant parses the JSON, populates `status-data.json`, and confirms what was captured.

This is one extra step compared to a "magic" form that auto-syncs. The trade-off is that the BA gets a true form UI rather than 8 sequential questions. For BAs who prefer the chat flow, the default (chat-style intake) is unchanged.

### Refresh behaviour

If the BA wants to update intake info later (e.g. complexity changes from `standard` to `full`, or a Jira template story is added), they can:

- Re-open the canvas and edit fields (state persists)
- Copy the updated JSON and paste back to chat
- The assistant detects the diff and updates `status-data.json` accordingly

The orchestrator should treat intake form canvas updates as a Phase 0 refresh, not a full re-intake.

### Example canvas (skeleton â€” generate per-initiative)

```tsx
import { Stack, H1, H2, Text, Input, Select, Toggle, Textarea, Code, Divider, useCanvasState } from 'cursor/canvas';

export default function IntakeForm() {
  const [name, setName] = useCanvasState<string>('initiative.name', '');
  const [complexity, setComplexity] = useCanvasState<'lean' | 'standard' | 'full'>('initiative.complexity', 'standard');
  const [jiraKey, setJiraKey] = useCanvasState<string>('initiative.jiraProjectKey', '');
  const [jiraTemplate, setJiraTemplate] = useCanvasState<string>('initiative.jiraTemplate.sourceKey', '');
  // ... all other fields

  const json = {
    initiative: {
      name,
      complexity,
      jiraProjectKey: jiraKey,
      jiraTemplate: jiraTemplate ? { sourceKey: jiraTemplate } : null,
      // ... rest
    },
    _missing: [
      !name && 'initiative.name',
      !jiraKey && 'initiative.jiraProjectKey',
      // ...
    ].filter(Boolean),
  };

  return (
    <Stack gap={20}>
      <H1>Intake Form â€” RBA Surcharge Ban</H1>
      <Text tone="secondary">Fill in what you know. Leave blanks for unknowns â€” they'll be logged as gaps. When done, copy the JSON at the bottom and paste it into chat.</Text>

      <Divider />
      <H2>1. Workspace IDs</H2>
      <Input label="Jira project key" value={jiraKey} onChange={setJiraKey} required />
      {/* ... */}

      <Divider />
      <H2>3. Initiative basics</H2>
      <Input label="Initiative name" value={name} onChange={setName} required />
      <Select label="Complexity signal" value={complexity} options={['lean', 'standard', 'full']} onChange={setComplexity} required />
      {/* ... */}

      <Divider />
      <H2>Copy this JSON and paste it back to chat</H2>
      <Code language="json">{JSON.stringify(json, null, 2)}</Code>
    </Stack>
  );
}
```

(Adjust component names to actual `cursor/canvas` exports â€” verify against the SDK declarations in `~/.cursor/skills-cursor/canvas/sdk/index.d.ts` before generating the real file.)

### Slop check (per canvas skill rules)

- No emojis as visual labels â€” use `required` text instead
- No gradients, no box shadows
- One H1 (initiative name + "Intake Form"); H2s per section
- Group fields with `Stack` and `Divider`, not nested cards

---

## Metrics computation (Wave 6 â€” new)

The Project Canvas computes four derivable BA quality metrics from existing state. These are surfaced in `/status`, `/snapshot`, and feed every retro automatically (per `ba-retrospective-and-learning` Metrics integration section).

### The four metrics

#### 1. MoSCoW coverage rate

```
mosCoWCoverageRate (per scope) =
  (requirements WITH a MoSCoW rating for this scope) /
  (total requirements visible to this scope)
```

Source: requirements register in `initiative-tracker.md` cross-referenced with the per-scope MoSCoW matrix in `status-data.json`. Compute per scope (initiative / each feature / each cohort). Track current value and trend (current vs 7 days ago, 14 days ago).

Threshold for warning: below 80% for any scope with Delivery (M5) active. Surface in `/status` MoSCoW summary.

#### 2. DoR hit rate

```
dorHitRate (per scope, rolling 30 days) =
  (stories that passed DoR first time) /
  (total stories that reached the DoR check)
```

Source: a new `dorChecks` array in `status-data.json` capturing every DoR run with `storyKey`, `firstAttempt: pass | partial | fail`, `date`, `scope`. Delivery Definition writes to this array on every DoR check.

Threshold for warning: below 70% for any scope with active Delivery. Trend matters more than absolute value â€” a falling rate is the signal.

#### 3. Requirement interrogation rate

```
requirementInterrogationRate (per scope) =
  (requirements with Requirements Interrogator output) /
  (total requirements in register)
```

Source: requirements register cross-referenced with the existence of an interrogation artefact (either inline in the requirement entry or in a separate `interrogations/` folder). Discovery and Requirements should already be writing these.

Threshold for warning: below 95% for any scope past Discovery completion. Below 95% means at least one requirement entered the register without challenge â€” which is the failure mode the Interrogator exists to prevent.

#### 4. Sign-off cycle time

```
signOffCycleTime (per sign-off) =
  approvedDate - requestedDate
```

Aggregate: median, 90th percentile, and count of sign-offs currently open >7 days.

Source: sign-off entries in the tracker need both `requestedDate` and `approvedDate`. Add `requestedDate` field if not present.

Threshold for warning: median >5 working days OR any sign-off open >10 working days. Surface in `/status` and `/next`.

### Computation invocation

Compute these:
- Before every `/status` output (after Jira sync, before the chat status text is generated)
- Before every retro (Type 2 / Type 3 â€” the retro skill reads them)
- Before every `/snapshot`
- On demand via `/metrics` (new command)

### Storage

Computed metrics are NOT stored in `status-data.json` as canonical (they're derived). They're cached in a sibling file `metrics-cache.json` that includes a `computedAt` timestamp. Anything older than 1 hour is recomputed on next request.

### Surfacing in /status

Add a new section to the `/status` output template:

```
## Quality metrics (rolling 30 days)

| Metric | Value | Trend | Warn? |
|---|---|---|---|
| MoSCoW coverage (initiative) | 87% | â†— | âœ“ |
| MoSCoW coverage (Cohort A) | 92% | â†’ | âœ“ |
| MoSCoW coverage (Cohort B) | 64% | â†˜ | ðŸ”´ below threshold |
| DoR hit rate (Cohort A) | 78% | â†’ | âœ“ |
| DoR hit rate (Cohort B) | 55% | â†˜ | ðŸ”´ below threshold |
| Requirement interrogation rate | 91% | â†’ | ðŸŸ¡ below 95% target |
| Sign-off cycle time (median) | 6.5 days | â†— | ðŸ”´ above 5d target |
```

### Failure handling

If any metric can't be computed (insufficient data â€” e.g. no DoR checks logged yet on a new initiative), display `n/a` in the metrics table, NOT 0% or a fabricated value. Showing `n/a` is honest; showing 0% looks like everything is broken.

After 3 status outputs with the same metric `n/a`, surface a one-line nudge: "DoR hit rate has been n/a for 3 status runs â€” likely missing instrumentation in Delivery Definition. Want me to look?"

### New `/metrics` command

Add to the orchestrator's command set:

| `/metrics` | Pull and display all four metrics with per-scope breakdown and trend. Equivalent to the metrics section of `/status` but without the rest of the status output. Useful for quick check-ins. Always follow with an `AskQuestion` on whether to dig into a specific metric. |

---

## Workflow: Context â†’ Canvas

### Phase 1: Discover the project (automatic â€” do NOT ask first)

**Do not ask the user where files are.** Find them automatically:

**Step 1 â€” Find the project folder.** Search the workspace for the project's blueprint/analysis directory. Common patterns:
- `<workspace>/blueprints/<project-name>/` -- flat structure (RBA pattern, preferred)
- `<workspace>/blueprints/Project NNN - <name>/` -- numbered project format
- `<workspace>/<project-name>/docs/` -- simpler layout

Search strategy:
1. Glob for `**/blueprints/**/SESSION-CONTEXT.md` or `**/blueprints/**/Project-hub.md`
2. Glob for `**/blueprints/**/*.md` to find all project folders
3. If multiple projects exist, present them via `AskQuestion` and let the user pick
4. If no project folder is found, THEN ask the user

**Step 2 â€” Read ALL files in the project folder.** This is MANDATORY. Read every single file:

```
MUST READ (in priority order â€” start with richest sources):
1. SESSION-CONTEXT.md          â€” richest single source: decisions, OQs, risks, stakeholders, Jira tickets, delivery sequence, compliance status, milestones
2. initiative-tracker*.md      â€” decisions, risks, OQs, assumptions, spikes, confidence scores
3. Project-hub.md              â€” high-level status, stakeholders, key outputs
4. confluence-pages.json       â€” Confluence page IDs and URLs, Jira epic keys
5. Compliance-*.md             â€” compliance decisions, sign-off packs, decision packs
6. Meeting-*.md                â€” workshop outcomes, actions, attendees
7. solution-options*.md        â€” solution direction, ADRs, options comparison
8. Requirements*.md / BRD*.md  â€” business requirements
9. Analysis-*.md               â€” deep dive analyses
10. Spike-*.md                 â€” technical spike findings
11. Program-*.md               â€” program sequencing, task backlog
12. *.html                     â€” previous status snapshots (check for data)
13. ANY OTHER .md files        â€” read them ALL, no exceptions
```

**Do NOT skip files.** Every `.md` file in the project folder contributes context. The more files you read, the more accurate and complete the canvas will be. If a file is large, still read it â€” truncate only if it exceeds your context window, and note what you skipped.

**Also search up one directory level** â€” check the parent `docs/` or `blueprints/` folder for:
- `README.md`, `AGENTS.md`, `!CLAUDE.md` â€” project-level config
- Additional `*.md` files not in the analysis subfolder

### Phase 2: Gather live data from external sources

**Step 3 â€” Ask the user ONLY for genuinely missing information** (via `AskQuestion`):

Only ask if you couldn't determine these from the files you read:
- Initiative name (if not in any file header)
- Current phase (if SESSION-CONTEXT doesn't state it)
- Parent Jira epic key (if not in `confluence-pages.json` or SESSION-CONTEXT)
- Key deadlines (if not mentioned anywhere)
- Stakeholders (if not listed in any file)

**Step 3 â€” Pull live data from Jira** (mandatory when Jira MCP is available)

**Jira is the source of truth for all ticket data.** Never use hardcoded ticket status, titles, or estimates when Jira is reachable. Always execute this full sync sequence:

**3a. Resolve the Jira cloud ID**
```
getAccessibleAtlassianResources â†’ pick the cloud ID for [your-instance].atlassian.net
```
If your instance is not in the list, Jira auth is missing for this session â€” fall back to markdown sources and note the gap in the canvas footer.

**3b. Find the project parent epic(s)**
The parent epic key should be sourced from (in priority order):
1. `confluence-pages.json` â€” look for a `jiraEpic` or `jiraParent` field
2. `PROJECT-CONTEXT.md` or `SESSION-CONTEXT.md` â€” scan for lines like `Epic: PROJ-XXXX` or `Parent: PROJ-XXXX`
3. `Project-hub.md` â€” look for Jira links
4. Ask the user: `"What is the parent Jira epic or programme key for this initiative?"`

**3c. Fetch all epics under the programme (if programme key exists)**
```
searchJiraIssuesUsingJql:
  jql: "project = FCM AND issueType = Epic AND 'Epic Link' = <programme-key> ORDER BY key ASC"
  OR: "project = FCM AND parent = <programme-key> ORDER BY key ASC"
  fields: [summary, status, assignee, labels, priority, customfield_10016, customfield_10004]
  maxResults: 50
```

**3d. Fetch all stories under each epic**
For each epic found (or directly if user provides an epic key like PROJ-304):
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
| `issue.fields.customfield_10016` OR `issue.fields.customfield_10004` | `storyPoints` (number or null â€” used for velocity forecasting; null values get median-filled per step 3i). **Field varies by Jira instance** â€” check both `customfield_10016` (Jira Software story points) and `customfield_10004` (Story Points classic) and use whichever is non-null. If neither is populated, treat as null. |
| `issue.fields.customfield_10007[0].name` | `sprint` label |
| `issue.fields.customfield_10007[0].startDate` | Sprint start date (ISO) â€” used for timeline `startWeek` when ticket is still To Do |
| `issue.fields.customfield_10007[0].endDate` | Sprint end date (ISO) â€” used to calculate planned `weeks` duration |
| `issue.fields.assignee.displayName` | `assignee` |
| `issue.fields.issuelinks` | `dependsOn` (filter `inwardIssue` where type = "blocks") |
| `issue.fields.priority.name` | Note if High/Critical for critical path |

**3f. Jira â†’ canvas status mapping:**
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
  cloudId: <your-cloud-id>
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
- **In Progress date** â€” first transition where `toString` is "In Progress" (or "In Development"). This is the ticket's **actual start date** for the timeline bar.
- **Done date** â€” first transition where `toString` is "Done", "Closed", or "Released". This is the ticket's **actual end date**.
- **Created date** â€” `fields.created` â€” fallback if no In Progress transition exists yet.

**Mapping real dates to timeline weeks:**
```
startWeek = (inProgressDate - projectKickoffDate) / 7 days
weeks = status === "done"
  ? (doneDate - inProgressDate) / 7 days   // minimum 0.5
  : (today - inProgressDate) / 7 days + 2  // extend past today for in-progress
```

**Rules:**
- If a ticket went To Do â†’ In Progress â†’ Done all on the same day, show `weeks: 0.5` minimum so the bar is visible
- If a ticket is "Done" but the done date is before the timeline's Sprint 1 start, position it at the correct historical week â€” do NOT push it to Sprint 1
- Add the actual date to the label: `"PROJ-305 Domain Model (15 May)"` â€” this makes the timeline self-documenting
- **Never assume a ticket starts at Sprint 1** just because it's in the sprint. Real start = first "In Progress" changelog entry

**Sprint-based planned timeline (for tickets still in To Do / Backlog):**

When a ticket has no "In Progress" changelog entry (status = To Do / Backlog), use the **sprint field** to derive its planned start week:

1. **Extract sprint dates from the API response.** The sprint field (`customfield_10007`) returns an array with `startDate` and `endDate` as ISO timestamps (e.g. `"2026-05-19T13:00:00.000Z"`). The sprint `name` also often encodes the date in a team-specific convention (e.g. `FCM Sprint 37 20260513-527` â†’ `20260513` = 13 May).
   - **Prefer `startDate`/`endDate` from the API** over parsing the name â€” they're the authoritative values.
   - The `state` field indicates `"active"`, `"future"`, or `"closed"` â€” use this to validate against the ticket's status.
2. **Calculate planned startWeek:** `(sprintStartDate - projectKickoffDate) / 7 days`
3. **Calculate planned weeks:** `(sprintEndDate - sprintStartDate) / 7 days` â€” gives the actual sprint length from Jira rather than assuming 2 weeks.
4. **Label convention:** Include `"(Sprint NN, est.)"` or `"(To Do)"` in the label so it's visually distinguishable from real dates.
5. **If no sprint is assigned:** Position the ticket after the last known sprint with `status: "pending"` and label `"(unscheduled)"`.

```
Example: PROJ-301 is in Sprint N (starts [date]), project kickoff was 28 Apr.
  sprintStartDate = 13 May 2026
  startWeek = (13 May - 28 Apr) / 7 = ~2.1
  weeks = 2 (default sprint length)
  label = "PROJ-301 Churned State CS (Sprint 37, est.)"
  status = "pending"
```

**Priority order for determining startWeek:**
1. **Changelog "In Progress" date** â€” always preferred when it exists (real date)
2. **Sprint start date** â€” use when ticket is still To Do but assigned to a sprint (planned date)
3. **Ticket creation date** â€” last resort, only for unscheduled tickets that need a position on the timeline

This ensures the timeline always reflects the best available data: real dates when work has started, planned sprint dates for upcoming work, and creation dates as a fallback.

**3h. After fetching, update canvas data arrays:**
- `STORIES` / `WORK_ITEMS` â€” replace entirely with live Jira data
- `allItems` in `TimelineTab` â€” update `status`, `label`, `startWeek`, and `weeks` from Jira changelog dates; never keep estimated dates when real dates are available
- `depNodes` in `DependenciesTab` â€” update `status` from Jira
- Collapsible card counts in RAID tab automatically reflect the data

**3i. Story points and velocity forecasting** (mandatory when story points exist)

Story points from Jira (`customfield_10016`) drive velocity-based forecasting for unscheduled work.

**Extract and normalise story points:**

1. For each ticket, record `storyPoints = issue.fields.customfield_10016 ?? issue.fields.customfield_10004` (use whichever is non-null; `customfield_10004` is "Story Points (classic)" common in some Jira cloud instances).
2. **Median fill for blanks:** Calculate the median story points from all pointed tickets in this project/epic. If a ticket has `storyPoints === null`, assign the project median. If no tickets have points at all (cold start), use `3` as the default.
3. **Mark estimated values:** Any ticket whose points were filled via median MUST be labelled with `(est.)` suffix in all table displays â€” e.g. `"3 (est.)"`. Use italic text styling in the canvas (`fontStyle: "italic"`) and in HTML (`<em>3 (est.)</em>`).

**Calculate team velocity:**

```
velocity = totalPointsCompletedInClosedSprints / numberOfClosedSprints
```

To compute this automatically:
1. From all tickets with `status === "done"`, group by their sprint (`customfield_10007`).
2. Only count sprints where `state === "closed"` (not the active sprint â€” it's incomplete).
3. Sum the `storyPoints` (real + median-filled) per closed sprint.
4. `velocity = sum(sprintPoints) / closedSprintCount`
5. If no closed sprints exist (project too new), ask the user: `"What is your team's velocity in story points per sprint?"` via `AskQuestion`.
6. If user doesn't know either, use `10 points/sprint` as a conservative default and note it in the canvas footer.

**Forecast completion for unscheduled / pending work:**

For tickets in `To Do` or `Backlog` without a sprint assignment:
1. Sum their story points (real + median) â†’ `remainingPoints`
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

**Step 5 â€” From Confluence MCP** (if available and `confluence-pages.json` exists):
- Use page IDs from `confluence-pages.json` to read specific pages
- Read the project hub page and key child pages
- Extract: stakeholders, decisions, timeline, requirements

### Phase 3: Synthesise and generate BOTH outputs

With all gathered context, generate both outputs. Data is embedded directly in both files.

**Mandatory outputs (both required on every invocation):**

1. **`.canvas.tsx`** â€” Cursor Canvas with all 8 interactive tabs
2. **`status-snapshot.html`** â€” Standalone HTML with same data, same 8 sections

**If insufficient data for a tab:** Always render all 8 tabs/sections, but show a clear prompt in empty sections explaining what's missing and how to populate it. NEVER reduce the tab count.

**After generation, tell the user:**
> "Canvas and HTML snapshot generated. The HTML file is at `<path>/status-snapshot.html` â€” you can open it in any browser, email it, or attach it to Confluence for stakeholders without Cursor access."

## Canvas location and naming

**Single living canvas per project** â€” overwrite on each refresh.

Path: `~/.cursor/projects/<workspace>/canvases/<project-slug>-status.canvas.tsx`

Naming: kebab-case the initiative name. Examples:
- `auto-reassessment-status.canvas.tsx`
- `[initiative-slug]-status.canvas.tsx`
- `merchant-onboarding-status.canvas.tsx`

## Canvas architecture

### Eight interactive tabs (using `useCanvasState`) â€” Wave 3 + demo iteration

| Tab | Content | Visuals |
|---|---|---|
| **Overview** | Workstream strip (friendly names + emojis, no M-codes), 4 stakeholder-readable stats (days to deadline / features on track / blockers / decisions confirmed), "Where we are right now" callout, 2Ã—2 Top blockers grid with emoji-prefixed titles, "Where each scope is right now" table, confidence table | Stat grid + Callouts + Tables (no charts) |
| **Workstreams** | Workstream grid â€” scopes down (cohorts indented + zebra-striped + section dividers), 8 workstreams across (Intake / Kickoff / Discovery / Slicing & Sequencing / Solution / Delivery / Playback / Eval & Retro â€” no M-codes), cells coloured by state (ðŸŸ¢ Done, ðŸ”µ Active, â¸ Paused, â—‹ Not started, Â· N/A). **In-progress MUST be BLUE.** Compact horizontal legend BELOW the grid. Recent workstream changes log. | Custom SVG grid + horizontal legend + Table |
| **Features & Delivery** | Feature status table (with active workstreams summary per feature), Jira-style stories table (filtered by scope) with MoSCoW column (emoji-prefixed), MoSCoW priority matrix per cohort | Tables with row tones |
| **Timeline** | SVG Gantt with **Milestones swimlane at the TOP** (each milestone = emoji + label + date stacked, e.g. "âš–ï¸ / Legal sign-off / 27 May"), then team/area swimlanes (BA Analysis, Compliance/Legal, F1 Eng, etc), vertical **blue dashed Today line**, vertical **red dashed â›” Deadline line**, bar length = `weeks Ã— colWidth âˆ’ 4`, bars auto-pack into sub-rows so they never overlap, **date headers in real dates** ("18 May, 25 Mayâ€¦") NOT week codes (W21, W22). | Custom SVG Gantt |
| **Dependencies** | Interactive DAG (real Requirement / Story / Milestone â†’ Deadline graph) â€” click any node to highlight upstream + downstream chain via BFS. Critical chains as horizontal Pill chains below. | `computeDAGLayout` + SVG + Pills |
| **Traceability** | Interactive DAG â€” bidirectional click-to-highlight. âš–ï¸ Driver â†’ ðŸ“‹ Requirement â†’ ðŸ• Slice â†’ ðŸŽŸï¸ Story â†’ ðŸ“Œ ADR. Requirement nodes carry MoSCoW pills per scope. Below the DAG: full mapping table. | `computeDAGLayout` + SVG + Table |
| **Critical Path & Actions** | Milestone table with status emoji pills, actions due this week (from action register), MoSCoW warnings if any | Tables with row tones |
| **RAID & Tracker** | 5 card-style RAID collections (ðŸ“Œ Decisions, ðŸ§¨ Risks, â“ Open Questions, âš ï¸ Assumptions, ðŸŽ¯ Actions) using `<Card collapsible>`. **"Show outstanding items only" toggle defaults to CHECKED.** IDs in small font column; descriptions in prime column. | Cards + Tables + Checkbox toggle |

### Scope navigator (demo iteration â€” replaces old breadcrumb)

A **horizontal multi-select pill cluster** above the tab strip. Three visually-grouped clusters separated by `|` characters as `Text size="small" tone="tertiary"`:

```
Filter scope:  [âœ“ ðŸ›ï¸ Initiative level]  |  [F1 â€¦]  [F2 â€¦]  [F3 â€¦]  |  [Cohort: Solo]  [Cohort: AccountRight]  [Cohort: Business]
Showing the whole initiative (Initiative level) Â· click a feature or cohort to drill in Â· click "Initiative level" to reset
```

**UX contract (mandatory â€” these rules must NEVER be relaxed):**

| Action | Behaviour |
|---|---|
| Default state on load | `selectedScopes = ["initiative"]` â€” "Initiative level" pill `active`, `tone="info"`, with `âœ“ ` prefix |
| Click "ðŸ›ï¸ Initiative level" | Clear all other selections; result = `["initiative"]` |
| Click a feature or cohort while Initiative is the only selection | Remove `"initiative"`; add clicked scope. Initiative pill goes inactive (neutral tone, no `âœ“`) |
| Click a feature or cohort while it is already selected | Remove it from selection |
| Click a feature or cohort while others (not initiative) are selected | Toggle it (add or remove) |
| Result of any action ends with empty `selectedScopes` | Snap back to `["initiative"]` â€” never leave the array empty |

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

#### Scope label naming â€” MANDATORY rule (no BA jargon in user-facing labels)

**Internal IDs MAY be coded** (e.g. `"F-A"`, `"C-A"`, `"F-B"`) â€” these are not user-facing and are used only for routing, filtering, and code references.

**Display labels MUST use real business context** â€” `label` and `shortLabel` must describe what the feature or cohort actually IS in plain business terms. Never use `"Feature A"`, `"Feature B"`, `"Cohort A"`, `"Cohort B"` etc. as the displayed name. Those abstract codes mean nothing to a stakeholder reading the canvas.

| âŒ Bad (BA jargon) | âœ… Good (real business context) |
|---|---|
| `label: "F-A Rule Uplift"` | `label: "[Feature Name]"` |
| `shortLabel: "Feature A"` | `shortLabel: "[Short Name]"` |
| `label: "Cohort A: Stale Draft"` | `label: "Stale Drafts (<30d, never live)"` |
| `shortLabel: "Cohort A"` | `shortLabel: "Stale Drafts"` |
| `label: "Cohort B: Churned >7yr"` | `label: "Churned merchants (>7yr)"` |
| `shortLabel: "Cohort B"` | `shortLabel: "Churned >7yr"` |

**This rule applies everywhere a label is displayed** â€” SCOPES, timeline lane labels, timeline bar labels, dependency DAG node labels, traceability DAG slice/requirement labels, critical path milestones, RAID descriptions, callout text, narrative copy, table cells, chain card headers. Anywhere the user sees text.

**`shortLabel` constraint**: â‰¤ 18 characters, used in dense visuals (workstreams SVG, filter pills, timeline lane labels). `label`: longer descriptive form, used in tooltips and tables where space permits. Never repeat the descriptor between the two (`label: "Stale Drafts (stale drafts)"` is wrong).

**One exception â€” Jira-mirrored text**: if a Jira ticket title literally contains "Cohort A" or "Feature B" as Jira-authoritative terminology, you may keep it in the `STORIES` array title field exactly as it appears in Jira. But the canvas should still render the cohort/feature column using `SCOPES.shortLabel` (real business name), not the BA code.

**Why this rule exists**: stakeholders reading the canvas (HoP, compliance, vendor partners) have no mental model for what "Cohort B" means; they DO have a mental model for "Churned merchants (>7yr)". The canvas is a stakeholder artefact, not a BA workbook.

#### JSX-safe character handling â€” MANDATORY (avoids parse errors)

Scope labels and shortLabels often legitimately contain `<`, `>`, `&`, `{`, `}` characters (e.g. `"Stale Drafts (<30d, never live)"`, `"Churned merchants (>7yr)"`, `"R&D Squad"`). These are SAFE in **JS string literals** (the SCOPES array, status-data.json, prop values via `{variable}` expressions) â€” React auto-escapes them at render time.

These are **UNSAFE** when typed directly in JSX text content (between tags). The JSX parser sees `>` as a tag delimiter and throws:

> `The character ">" is not valid inside a JSX element ... Did you mean to escape it as "{'>'}" instead?`

**Three rules to avoid this**:

1. **Prefer expression rendering**: always reference scope labels via `{variable}` (e.g. `<Text>{scope.shortLabel}</Text>`), never copy-paste the label text into JSX between tags.
2. **For hardcoded prose** that mentions a scope (callouts, narrative text, card headers, chain card titles), use HTML entities: `&gt;` for `>`, `&lt;` for `<`, `&amp;` for `&`. Example: `<CardHeader>Chain B â€” Churned &gt;7yr (blocked)</CardHeader>`.
3. **After any scope rename**, run a quick lint check. The canvas Skill self-check pre-delivery list MUST include: "no unescaped `<` or `>` in JSX text content â€” search for `>[A-Za-z0-9]` outside of `{...}` expressions".

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

**Filter-down pattern (do NOT pass a single `activeScope` object â€” pass the `isScopeActive` callback):**

```tsx
type ScopeFilter = (id: ScopeId) => boolean;

{section === "overview" && <OverviewTab isActive={isScopeActive} />}
{section === "workstreams" && <WorkstreamsTab isActive={isScopeActive} />}
// ...etc â€” every tab takes `isActive: ScopeFilter`
```

Every tab uses `isActive(scope.id)` to decide whether to show a row, bar, or node. This pattern enables true multi-scope views (e.g. "show me F1 + Cohort Solo on the same timeline") without forcing a single-scope drill-down.

**Pill rendering pattern (every scope pill follows this):**

```tsx
{SCOPES.filter((s) => s.level === "feature").map((s) => {
  const isOn = selectedScopes.includes(s.id);
  return (
    <Pill key={s.id} active={isOn} tone={isOn ? "info" : "neutral"} onClick={() => toggleScope(s.id)}>
      {isOn ? "âœ“ " : ""}{s.label}
    </Pill>
  );
})}
```

The Initiative-level pill additionally prefixes `ðŸ›ï¸ ` to the label. Use `Text size="small" tone="tertiary"` for the `|` separators between clusters. The "Showing: â€¦" description line uses `Text size="small" tone="secondary"`.

### Interactivity features

1. **Section navigation** â€” `useCanvasState<SectionId>("section", "overview")` with Pill toggles (8 Pills, one per tab).
2. **Scope navigator** â€” `useCanvasState<ScopeId[]>("selectedScopes", ["initiative"])` (see UX contract above). Every tab respects `isScopeActive`.
3. **Click-to-highlight (Dependencies)** â€” `useCanvasState<string | null>("dep-selected", null)`. Click a node â†’ BFS upstream + downstream â†’ chain highlights with accent blue; unrelated nodes dim to ~20% opacity, unrelated edges to ~15% opacity. "Clear selection" ghost Button appears when a node is selected.
4. **Click-to-highlight (Traceability)** â€” Same pattern: `useCanvasState<string | null>("trace-selected", null)`. Bidirectional BFS traversal highlights the full connected chain.
5. **Collapsible sections** â€” `<Card collapsible>` (or `<details>` in HTML) for each RAID collection.
6. **Outstanding-only filter** â€” `useCanvasState<boolean>("outstandingOnly", true)` Checkbox toggle in RAID tab. **Defaults to CHECKED** so the page opens to what needs attention.
7. **Hover tooltips** â€” SVG `<title>` elements inside each `<g>` node. Format examples:
   - Workstream cell: `"F1 Surcharge Detection â€” Solution: Done"`
   - Gantt bar: `"F1 Solo deploy â€” In progress â€” scope: Solo"`
   - Milestone: `"Legal sign-off â€” 27 May"`
   - Dep / trace node: `"PROJ-5103: block surcharge â‰¥ 1 Jul (in progress)"`
8. **No old activeFilters[] feature filter** â€” this was superseded by the scope navigator. Do NOT also render a separate "Features" multi-select; that's duplication.

### Colour scheme (mandatory â€” use consistently)

Use the `useStatusColours()` helper pattern. All status colours MUST use theme tokens â€” no hardcoded hex.

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

Status colour helper (mandatory â€” use these tokens, never hardcode hex):

```tsx
type ItemStatus = "done" | "in-progress" | "pending" | "blocked";

function useStatusColours() {
  const theme = useHostTheme();
  return {
    done: theme.diff.stripAdded,       // green
    "in-progress": theme.accent.primary, // BLUE â€” not amber, not brown
    pending: theme.fill.tertiary,       // greyed
    blocked: theme.diff.stripRemoved,   // red
  };
}

const itemStatusEmoji = (s: ItemStatus): string => {
  if (s === "done") return "ðŸŸ¢";
  if (s === "in-progress") return "ðŸ”µ";
  if (s === "blocked") return "ðŸ”´";
  return "â—‹";
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
  complete: "ðŸŸ¢",
  active: "ðŸ”µ",
  paused: "â¸",
  "not-started": "â—‹",
  na: "Â·",
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

/* â”€â”€â”€ HorizontalBarChart â€” use this instead of BarChart for RAID and delivery summaries â”€â”€â”€ */
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

The full reference implementation is `~/.cursor/projects/<workspace>/canvases/rba-surcharge-ban-demo.canvas.tsx`. Mirror its structure (component decomposition into `WorkstreamStrip`, `OverviewTab`, `WorkstreamsTab`, `FeaturesTab`, `TimelineTab`, `DependenciesTab`, `TraceabilityTab`, `CriticalPathTab`, `TrackerTab`) â€” do not invent a different layout.

## Tab specifications

### Overview tab

1. **Workstream strip (replaces old phase strip)** â€” Pill strip showing initiative-level workstreams with their current state. Use friendly names (Intake, Kickoff, Discovery, Slicing & Sequencing, Solution, Delivery, Playback, Eval & Retro) â€” NO M-codes. Colour + emoji communicates state (ðŸŸ¢ Done / ðŸ”µ Active / â¸ Paused / â—‹ Not started). Multiple workstreams can be `active` simultaneously (this is the whole point of the parallel model).
2. **Top stats** â€” Grid of 4 stakeholder-readable Stat components. Choose from: days to key deadline (`danger` tone if approaching), features on track (e.g. `"2 / 3"`), active blockers count, decisions confirmed (e.g. `"4 / 5"`). Avoid BA jargon (no "MoSCoW coverage %" on Overview â€” that lives in Features tab). **Do NOT compute an overall progress %** â€” initiatives have highly variable workstream durations and a misleading % is worse than none. The workstream strip already communicates progress visually.
3. **"Where we are right now" callout** â€” 2â€“4 sentence narrative summary, info tone.
4. **Top blockers grid** â€” 2Ã—2 grid of Callouts with emoji-prefixed titles (e.g. "ðŸ”´ Acquirer C â€” no commitment for 24 Jun"). No separate "Warnings & Call-outs" section â€” top blockers cover it.
5. **Where each scope is right now table** â€” Scope, currently in workstream(s), status (emoji-prefixed plain English).
6. **Confidence table** â€” Table with Area, Score (emoji-prefixed), Note. Row tones by score (success/warning/danger).

### Workstreams tab (was Modes â€” renamed in demo iteration)

Shows the full per-scope workstream grid. Primary place to see "where is what".

**Layout â€” SVG grid:**
- **Y axis (rows):** scopes â€” Initiative (top, bold), then each feature (bold), then each cohort (indented with `â†³` prefix, zebra-striped backgrounds, section divider line above cohort group).
- **X axis (columns):** 8 workstreams with friendly labels â€” Intake, Kickoff, Discovery, Slicing & Sequencing, Solution, Delivery, Playback, Eval & Retro. NO M-codes shown in user-facing UI.
- **Cells:** rounded rect coloured by state:
  - `not-started` â€” light grey (theme.fill.tertiary), emoji â—‹
  - `active` â€” accent **BLUE** (theme.accent.primary) â€” NOT amber/brown. Emoji ðŸ”µ.
  - `paused` â€” red wash (theme.diff.stripRemoved). Emoji â¸.
  - `complete` â€” green (theme.diff.stripAdded). Emoji ðŸŸ¢.
  - `na` â€” 8% opacity grey. Emoji Â· or blank.
- **Cell content:** emoji + short label (e.g. "ðŸŸ¢ Done", "ðŸ”µ Active") with consistent text alignment (centred horizontally and vertically).
- **Cell tooltip:** `${scope.label} â€” ${workstream.label}: ${state.label}`.
- **Section dividers:** thin hairline between initiative / features / cohorts groups.

**Below the matrix:**
- **Horizontal compact legend (NOT vertical chrome on the side)** â€” five colour swatches inline with emoji labels: `ðŸŸ¢ Done Â· ðŸ”µ Active Â· â¸ Paused Â· â—‹ Not started Â· Â· N/A`.
- **Recent workstream changes log:** table of `Date | Scope | Workstream | Change` (row-toned by change type).
- **Active anti-patterns** (from anti-pattern-detector, if any) â€” table of workstream-related anti-patterns currently flagged.

**Click behaviour:**
- Click a row label (scope) â†’ drills into that scope via the scope navigator.
- Click a cell â†’ shows a panel below with the workstream's recent activity, hooks active for that scope + workstream, and skills involved.

### Workstreams tab â€” exact SVG dimensions

Reference values from the demo build (use these as defaults â€” adjust only if scope count justifies it):

```tsx
const cellW = 102;     // workstream column width
const cellH = 32;      // row height per scope
const labelW = 220;    // left label column width
const headerH = 38;    // column header band height
const gap = 2;         // gap between cells

const svgW = labelW + WORKSTREAMS.length * (cellW + gap) + 20;
const svgH = headerH + orderedRows.length * (cellH + gap) + 20;
```

Row ordering: `initiative` first, then `feature`s, then `cohort`s. Cohort rows MUST be indented (`indent = 16`) and prefixed with `"â†³ "`. Cohort labels use `fontWeight="500"`; initiative + feature labels use `"700"`. Add a `<line>` divider (`stroke={theme.stroke.secondary}, strokeWidth={1}`) above the first feature row and above the first cohort row.

Zebra striping: `if (ri % 2 === 0)` draw a rect over the label column area only (`opacity={0.15}`, fill `theme.fill.tertiary`) â€” not across the cells (the cell fills do their own colouring).

Cell text: `state !== "na"` â†’ render `${STATE_EMOJI[state]} ${STATE_LABEL[state]}` centred, `fontSize={10}`, `fontWeight="700"` if state is active otherwise `"500"`. `state === "na"` â†’ render no text, just the faded rect.

### Workstreams tab â€” empty state

If the initiative is still at Intake (M0) only and no sub-scopes exist yet, the matrix shows only the Initiative row with `intake` active and rest grey. Add a Callout explaining: "Sub-scope workstreams will populate once features and cohorts are defined in Discovery."

### Features & Delivery tab

Receives `isActive: ScopeFilter` prop. Filters items by whether their scope (`feature` or `cohort`) is currently active.

1. **Features in flight table** â€” Feature, Active workstream(s) (concatenated labels with ` + `, or `â€”` if none), Owner, Health (emoji-prefixed plain English), Priority cover (%). Row tones: `"success"` for healthy F1, `"warning"` for solutioning F2, `"danger"` for at-risk F3. Filter rows by `s.level === "feature" && isActive(s.id)`.
2. **Stories in flight table** â€” Title, Feature, Cohort (display short label or "All cohorts"), Priority (MoSCoW), Status (emoji-prefixed), Key (Jira). Row tones: `"danger"` if priority starts with `â€”` (unrated â†’ blocked), otherwise mapped from status. Filter:
   ```tsx
   const visibleStories = STORIES.filter(
     (st) =>
       isActive(st.feature) ||
       (st.cohort !== "all-cohorts" && isActive(st.cohort)) ||
       (st.cohort === "all-cohorts" && isActive("initiative"))
   );
   ```
3. **MoSCoW priority matrix table** â€” Rows = requirements, columns = cohorts. Cells = emoji-prefixed rating (`ðŸ”´ Must` / `ðŸŸ¡ Should` / `ðŸ”µ Could` / `âšª Won't` / `âš  â€” unrated`). The matrix is a single `<Table>` â€” no separate per-feature card stack.
4. Use plain `Text size="small" tone="secondary"` for explanatory paragraphs above each table.

**MoSCoW emoji + tone mapping (use everywhere MoSCoW appears):**
| Rating | Emoji | Pill tone |
|---|---|---|
| Must | ðŸ”´ | `danger` |
| Should | ðŸŸ¡ | `warning` |
| Could | ðŸ”µ | `info` |
| Won't | âšª | `neutral` |
| (Missing / unrated) | âš  | `warning` (text "âš  Missing" or row prefixed with `ðŸ”´ â€” unrated` if it blocks sprint pickup) |

### Timeline tab (SVG Gantt with Milestones swimlane at TOP)

Receives `isActive: ScopeFilter` prop. Filters lanes AND bars by whether any of their scopes match.

**Layout (mandatory â€” rebuild MUST follow this):**

1. **Two-line header row** â€” Top line: actual date (bold, fontSize 10, e.g. "18 May"). Bottom line: short week marker (fontSize 9, tertiary tone, e.g. "wk 1"). Never use bare week codes like "W21" / "W22" as the visible date â€” use real dates.
2. **Vertical grid lines** every column (dashed `stroke-dasharray="2 4"`, `stroke={theme.stroke.tertiary}`), spanning from `milestoneLaneTop` to `bodyBottom`.
3. **Today line** â€” vertical dashed BLUE line (`stroke={theme.accent.primary}`, `strokeWidth={2}`, `strokeDasharray="4 4"`) positioned at `labelWidth + todayWeek * colWidth`. Label `"Today"` 4px to the right, 6px above the line, blue + bold.
4. **Deadline line** â€” vertical dashed RED line (`stroke={colours.blocked}`, `strokeWidth={2}`, `strokeDasharray="6 3"`) positioned at `labelWidth + deadlineWeek * colWidth`. Label `"â›” <date>"` (e.g. `"â›” 1 Jul"`) red + bold, immediately right of the line.
5. **Milestones swimlane at the TOP** â€” a 56px-tall band immediately below the header, faded grey background (`fill={theme.fill.tertiary}, opacity={0.18}`). Lane title `"ðŸ“… Milestones"` left-aligned. For each milestone, render a 3-line stack centred on its week:
   - Line 1: emoji at `fontSize={16}`
   - Line 2: label (e.g. "Legal sign-off") at `fontSize={9}`, primary text, `fontWeight="600"`
   - Line 3: date (e.g. "27 May") at `fontSize={9}`, tertiary tone
6. **Team / area swimlanes** below the milestone lane. Lanes are scoped (each lane declares which `scopes` it covers). Only render lanes where `lane.scopes.some(isActive)`. Even-index lanes get a 25% opacity grey background.
7. **Bar packing** â€” each lane packs its bars into sub-rows so they never overlap. Algorithm:
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
8. **Bar rendering** â€” `width = Math.max(bar.weeks * colWidth - 4, 24)`. Fill `colours[bar.status]` at `opacity={0.88}`, `rx={4}`. Label inside the bar: `${itemStatusEmoji(bar.status)} ${bar.label}` at `fontSize={10}`, `fontWeight="500"`, `dominantBaseline="middle"`, 6px left padding.

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
- Bar: `"${bar.label} â€” ${itemStatusLabel(bar.status)} â€” scope: ${shortLabel}"`
- Milestone: `"${m.label} â€” ${m.date}"`

**Legend BELOW the chart, horizontal compact form** (NOT vertical side chrome):
```
Legend:  â–¢ ðŸŸ¢ Done   â–¢ ðŸ”µ In progress   â–¢ â—‹ Pending   â–¢ ðŸ”´ Blocked
```

Each swatch = 11Ã—11 div with rounded corners. Use `Row gap={4} align="center"` per swatch+label pair, all wrapped in a single `Row gap={12} wrap`.

Add a `Text size="small" tone="tertiary"` line below the legend: `"Bar length = duration in weeks Ã— column width. Bars auto-pack into sub-rows so they never overlap."`

**Date computation rules:**
- `todayWeek = (today - weekZeroDate) / 7` (fractional)
- `deadlineWeek = (deadline - weekZeroDate) / 7` (fractional)
- For sprint-derived planned bars, see Phase 2 step 3g + 3h.
- **Never** shrink an in-progress bar to end at "today". It should extend to a realistic completion estimate past today.

**Forecast / unscheduled bars** â€” render with `pending` colour + `strokeDasharray="4 2"` border and `"(forecast)"` suffix in the label.

**Timeline accuracy rules (mandatory â€” never violate these):**

1. **Bar end â‰  status = done.** A bar that visually ends at or before "today" on the chart MUST NOT be coded as `status: "done"` unless the work is actually confirmed complete. If work is in-progress and still ongoing, the bar should extend past today and use `status: "in-progress"`.
2. **Compliance-dependent items are never done until compliance confirms.** Draft requirements, analysis work pending compliance responses, and open questions cannot be marked `done` just because initial drafts exist. Use `in-progress` (ongoing work) or `pending` (not started / waiting).
3. **Start dates reflect actual work start, not sprint start.** A ticket's `startWeek` must come from the Jira changelog "To Do â†’ In Progress" transition date (see step 3g), not from the sprint it was assigned to. If a ticket was created on 14 May and moved to In Progress on 15 May, its startWeek should reflect 15 May â€” even if the sprint nominally starts on 19 May. Calculate `startWeek` as `(inProgressDate - projectKickoffDate) / 7`.
4. **Label accuracy.** When an item is in-progress and waiting on an external dependency (e.g. compliance responses), reflect this in the label: `"Draft reqs (compliance pending)"`, not just `"Requirements"`.
5. **Never shrink in-progress items to fit "today".** If requirements have been in-progress since wk 1 and are still ongoing, the bar should span from wk 1 to a realistic completion date (e.g. wk 7), not from wk 1 to wk 3 (today). An item that ends at "today" implies it was completed just in time â€” this is almost always misleading.
6. **Analysis swimlane.** Always include a dedicated Analysis swimlane when a BA is on the project. It should show: intake/scoping, current state analysis, requirements drafting (mark in-progress if compliance not confirmed), process mapping, gap analysis, solution shaping. Do NOT collapse BA work into the compliance or feature swimlanes.
7. **Done tickets use real dates from Jira changelog.** When a ticket is "Done", its bar width must span from the actual "In Progress" date to the actual "Done" date (from changelog, step 3g). If both transitions happened on the same day, use `weeks: 0.5` so the bar remains visible. Never use sprint-length estimates for done work when real dates are available.
8. **Include actual dates in timeline labels.** For done and in-progress tickets, append the start date to the label: `"PROJ-305 Domain Model (15 May)"`. This makes the timeline self-documenting and verifiable at a glance without needing to cross-reference Jira.
9. **Point-proportional bar width for pending/unstarted tickets.** When a ticket has story points but no real start/end dates yet, calculate bar width using velocity: `weeks = (storyPoints / velocityPerSprint) * sprintLengthWeeks`. For example, at 5 pts/sprint over 2-week sprints: a 2-point ticket = 0.8 weeks, a 3-point ticket = 1.2 weeks. This gives an at-a-glance visual of relative effort. Done and in-progress tickets still use real dates (rules 3 and 7).

### Dependencies tab (Interactive SVG DAG with click-to-highlight)

Receives `isActive: ScopeFilter` prop.

**Above the graph â€” Active blockers callouts:**
- 1â€“3 `<Callout>` components (tone="danger" or "warning") for the most urgent blockers, with the same emoji-prefixed titles as the Overview tab.

**Node kinds (use the same colour and shape â€” vary by `kind`):**
- `external` â€” vendor / acquirer / partner dependencies (e.g. Acquirer C API)
- `internal` â€” sign-offs, audits, briefs (e.g. Legal sign-off)
- `story` â€” Jira tickets (PROJ-XXXX)
- `milestone` â€” feature go-live, comms send, deadline

```tsx
interface DepNode { id: string; label: string; status: ItemStatus; scope: ScopeId; kind: "external" | "internal" | "story" | "milestone" }
```

**Filter:** `filteredNodes = depNodes.filter((n) => isActive(n.scope) || n.id === "[initiative-id]")` â€” always keep the final-deadline node visible regardless of scope so the graph terminates somewhere meaningful.

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
- Each node has a `<title>` tooltip: `"<label> â€” <itemStatusLabel(status)>"`.
- "Clear selection" ghost `<Button>` appears when `selectedNode !== null`.

**Below the graph â€” Critical chains as horizontal Pill chains:**

Render the most important paths (e.g. Solo cohort path and Business cohort path) as horizontal sequences of `<Pill size="sm">` linked by `<Text size="small" tone="tertiary">â†’</Text>` separators. Each path lives inside a `<Callout>` with a chain-status title.

**Horizontal compact legend** (same pattern as Workstreams/Timeline):
```
Legend:  ðŸŸ¢ Done   ðŸ”µ In progress   â—‹ Pending   ðŸ”´ Blocked
```

### Traceability tab (Interactive SVG DAG)

Same click-to-highlight pattern as Dependencies but **bidirectional** (traces both up and down from the selected node):

```tsx
const [selectedTrace, setSelectedTrace] = useCanvasState<string | null>("trace-selected", null);
```

**Node kinds (use the same colours):**
- âš–ï¸ `driver` (e.g. RBA Mandate) â€” `theme.diff.stripRemoved`
- ðŸ“‹ `requirement` â€” `theme.accent.primary`
- ðŸ• `slice` â€” `theme.fill.secondary`
- ðŸŽŸï¸ `story` â€” `theme.fill.tertiary`
- ðŸ“Œ `adr` â€” `theme.diff.stripAdded`

Each node's label is prefixed with its kind emoji.

**Below the DAG â€” full traceability table:** Columns `Driver | Requirement | Slice | Stories | ADRs`. Row tone `"info"` for any row matching `selectedTrace`. Row tone `"warning"` for any requirement whose stories include unrated MoSCoW (blocks delivery).

**Horizontal legend** showing the 5 node kinds with their emojis.

Data structure:
```tsx
interface TraceNode { id: string; label: string; kind: "driver" | "requirement" | "slice" | "story" | "adr"; scope?: ScopeId }
interface TraceLink { requirementId: string; requirementText: string; slice: string; stories: string[]; adrs: string[]; moscow?: Record<ScopeId, MoSCoW> }
```

### Critical Path & Actions tab

Receives `isActive: ScopeFilter` prop.

1. **Critical path to deadline table** â€” Columns: #, Milestone, Date, Status (emoji-prefixed: ðŸŸ¢ / ðŸ”µ / ðŸŸ¡ / ðŸ”´ / â›” for the deadline), Owner. Row tones map from status. Filter by `isActive(milestone.scope)` where applicable.
2. **Actions due this week table** â€” Columns: #, Action, Owner, Due, Priority (emoji-prefixed: ðŸ”´ Critical / ðŸŸ¡ High / ðŸ”µ Medium). Row tones map from priority. Sort by due date ascending.
3. Optional: **MoSCoW warnings callout** if any stories lack MoSCoW for the current scope.

### RAID & Tracker tab

Receives `isActive: ScopeFilter` prop.

1. **Header row** â€” `<H2>RAID & Tracker</H2>` on the left, `<Checkbox checked={outstandingOnly}>Show outstanding items only</Checkbox>` on the right. **Defaults to CHECKED.**
2. **Five collapsible RAID cards** in this exact order (use icons in summary text):
   - ðŸ“Œ Decisions â€” Decision, Made by, Status (emoji-prefixed), ID (small font column)
   - ðŸ§¨ Risks â€” Risk, Owner, Severity (ðŸ”´ HIGH / ðŸŸ¡ MEDIUM / ðŸ”µ LOW), ID
   - â“ Open questions â€” Question, Owner, Status, ID
   - âš ï¸ Assumptions â€” Assumption, Owner, Confidence, ID
   - ðŸŽ¯ Actions â€” Action, Owner, Status, ID
3. **Summary in card header** â€” `ðŸ“Œ Decisions (5 total Â· 1 outstanding)` so the user sees the count at a glance without expanding.
4. **ID column placement** â€” IDs (DEC-001, R-001 etc) MUST be the LAST column with small font/secondary tone. Descriptions get the prime column. This was a specific user requirement.
5. **Outstanding-only filter logic** â€” when `outstandingOnly === true`, hide rows whose status maps to one of: `"Confirmed", "Closed", "Resolved", "Done", "Agreed", "Approved", "Moot", "Dropped", "Booked"`. Mark each row with a `data-outstanding="true|false"` attribute (HTML) or an `outstanding: boolean` flag (canvas) so the filter is single-pass.
6. **Scope filtering** â€” Every tracker item carries a `scope` field. Filter by `isActive(item.scope)`. Show a small `Text size="small" tone="secondary"` note at the top: "Showing tracker items for: <scope name>" when not initiative-level.
7. **Decisions table MUST include Made by + Status** â€” this matches `ba-profile.mdc`'s "Decisions must be recorded as a table" requirement.
8. By default Decisions, Risks, and Actions cards open; OQs and Assumptions cards closed (use `defaultOpen` per card).
9. **Do NOT render a HorizontalBarChart in this tab in the rebuild iteration** â€” the user feedback was that the page had too much duplication; counts in card headers do the same job in less space.

## Canvas accuracy guardrails

Before writing the final canvas, run through this checklist:

| Check | What to verify |
|---|---|
| **No premature completion** | Is any `status: "done"` item actually still in-progress? Check against project notes. Compliance sign-off, requirements, and analysis items are frequently mislabelled done. |
| **Timeline bar lengths are honest** | Do in-progress items extend past "today"? They should. Only done items should end before today. |
| **Compliance-gated items** | Anything requiring compliance/legal/privacy sign-off should be `pending` or `in-progress` until that sign-off is recorded in the RAID log or Decision Pack. |
| **Analysis swimlane present** | Is there a BA/PM analysis swimlane that shows the full analysis workflow, not just "requirements done"? |
| **Week 0 = project start** | Does the timeline start from the D1 kickoff week, not "today"? For active projects, "today" should be ~week 3â€“8, not week 0. |
| **Jira statuses used** | If Jira MCP is available, did you fetch actual ticket statuses? Never hardcode them. |

If any check fails, fix the data before rendering.

---

## Data extraction rules

### From initiative tracker / project hub

1. **Confidence scores** â†’ Table (no chart). Map each area to High/Medium/Low.
2. **Decisions** â†’ ID, Decision (truncate ~80 chars), Owner, Date, Status
3. **Risks** â†’ ID, Risk, Severity, Mitigation, Owner, Status
4. **Status mapping** for row tones:
   - "Confirmed" / "Closed" / "Resolved" / "Done" / "Agreed" â†’ `"success"`
   - "In Progress" / "In flight" â†’ `"info"`
   - "Open" â†’ `undefined` (no tone)
   - "Blocked" / "Critical" â†’ `"danger"`
   - "Monitor" / "Pending" / "TBC" / "Gated" â†’ `"warning"`
   - "Deferred" / "Moot" / "Conditional" â†’ `"neutral"`

### From Jira MCP

- Epic status â†’ overall project status
- Story statuses â†’ Features & Delivery tab population. **Always prefer Jira status over markdown status.**
- Story dependencies (linked issues, "is blocked by") â†’ Dependencies tab edges
- Sprint assignment â†’ Timeline tab positioning
- Story labels/components â†’ swimlane/feature grouping

### From Confluence MCP

- Decision logs â†’ RAID Decisions table
- RAID pages â†’ direct population of tracker tab
- Requirements pages â†’ Traceability tab
- Status pages â†’ verify/supplement Overview tab

## Scaling for large projects

For projects with 100+ stories/items:

1. **Feature filter** â€” always include. Scopes every filtered tab to one workstream at a time.
2. **Collapsible cards** â€” use `Card collapsible defaultOpen={false}` for detail sections.
3. **Striped + stickyHeader tables** â€” set `striped` and `stickyHeader` props on large tables.
4. **Pagination** â€” for very large datasets, add pagination with `useCanvasState("page", 0)` and "Show more" buttons.
5. **DAG layout** â€” `computeDAGLayout` adapts to node count. For 50+ nodes, increase `rankGap` and use the feature filter to show subsets.

## Pre-delivery self-check

Before returning canvas code, verify EVERY item. This list grew from real demo-iteration failures â€” skipping any item likely reintroduces a known regression.

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
9. "ðŸ›ï¸ Initiative level" pill has `ðŸ›ï¸ ` prefix and `âœ“ ` prefix when active. Tone `"info"` when active, `"neutral"` when inactive.
10. Clicking "Initiative level" clears all other selections.
11. Clicking a feature/cohort auto-deselects "Initiative level".
12. If `next.length === 0` after a toggle, snap back to `["initiative"]` (never empty).
13. `filterDescription` line is `Text size="small" tone="secondary"` â€” plain-English, includes "click 'Initiative level' to reset".
14. Every tab takes `isActive: ScopeFilter` callback (NOT a single `activeScope` object).
15. EVERY tab actually FILTERS using `isActive` â€” Overview, Workstreams, Features, Timeline, Dependencies, Traceability, Critical Path, Tracker. **The most common regression is sections that ignore `isActive` and show all data regardless.**

### Workstreams (terminology + visuals)

16. Label is "Workstreams" (NOT "Modes"). 8 columns (NOT 9). Eval & Retro is a single merged column.
17. NO `M0`/`M1`/.../`M8` codes anywhere in the user-facing UI.
18. Cohort rows indented with `â†³ ` prefix.
19. Section divider lines above the first feature row AND above the first cohort row.
20. Zebra striping on every even-indexed row (label column only, `opacity={0.15}`).
21. In-progress cells fill is `theme.accent.primary` (BLUE). NEVER amber / brown / orange.
22. Each cell renders `${STATE_EMOJI[state]} ${STATE_LABEL[state]}` centred â€” NOT just the abbreviation.
23. Horizontal compact legend BELOW the grid (NOT vertical chrome on the side).

### Timeline

24. Date column headers in REAL DATES ("18 May", "25 May"â€¦) â€” NOT week codes ("W21", "W22").
25. Two-line header: date (bold, fontSize 10) on top, "wk N" (fontSize 9, tertiary tone) below.
26. **Milestones swimlane at the TOP** (between header and team lanes). 56px tall, light grey background, `"ðŸ“… Milestones"` label.
27. Each milestone renders as a 3-line stack: emoji (16px) â†’ label (9px) â†’ date (9px tertiary).
28. **Today line** vertical BLUE dashed (`stroke={theme.accent.primary}`, `strokeDasharray="4 4"`, `strokeWidth={2}`), with "Today" label.
29. **Deadline line** vertical RED dashed (`stroke={colours.blocked}`, `strokeDasharray="6 3"`, `strokeWidth={2}`), with "â›” <date>" label.
30. Bars auto-pack into sub-rows (no overlaps). Use the documented packing algorithm.
31. Bar width = `Math.max(bar.weeks * colWidth - 4, 24)`.
32. Bar label inside the bar: `${itemStatusEmoji(bar.status)} ${bar.label}` â€” emoji-prefixed.
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

42. Real Unicode emojis throughout: ðŸŸ¢ ðŸ”µ ðŸ”´ ðŸŸ¡ â¸ â›” ðŸ“… ðŸš€ âš–ï¸ ðŸ“§ ðŸ“Š ðŸ§¨ âš ï¸ ðŸ“Œ ðŸ“‹ ðŸ• ðŸŽŸï¸ ðŸ›ï¸ ðŸŽ¯ â“ â†³. NEVER ASCII substitutes (`âœ“`, `â—`, `â—‹` â€” `â—‹` is acceptable for "not started" inside the workstream grid only).
43. Status colour mapping is consistent across ALL tabs: Done=green, In-progress=BLUE, Pending=grey, Blocked=red.

### RAID & Tracker

44. `useCanvasState<boolean>("outstandingOnly", true)` defaults to `true` (Checkbox checked).
45. Five RAID cards in order: ðŸ“Œ Decisions, ðŸ§¨ Risks, â“ Open questions, âš ï¸ Assumptions, ðŸŽ¯ Actions.
46. Card headers show count summary: "ðŸ“Œ Decisions (5 total Â· 1 outstanding)".
47. ID column LAST in every RAID table, small font / secondary tone. Descriptions get the prime column.
48. Decisions table includes "Made by" column (per `ba-profile.mdc`).

### Overview

49. 4 stakeholder-readable Stat tiles (NOT MoSCoW % / velocity jargon as the headline metrics).
50. "Where we are right now" callout in info tone.
51. 2Ã—2 Top blockers grid with emoji-prefixed titles (e.g. "ðŸ”´ Acquirer C â€” no commitment for 24 Jun"). No separate "Anti-pattern" / "Warnings & Call-outs" section â€” top blockers cover it.

### Legends

52. Every visual (Workstreams grid, Timeline, Dependencies, Traceability) has a HORIZONTAL compact legend BELOW it, not vertical chrome.
53. Legends use `Row gap={4} align="center"` per swatch+label pair, wrapped in `Row gap={12} wrap`.

### Theme tokens

54. All SVG fills/strokes use theme tokens via `useStatusColours()` or `useHostTheme()`. No hardcoded hex.
55. Tables use `rowTone` for semantic status colouring (NEVER inline `style={{ background: ... }}`).
56. Empty tabs show informative Callout prompts (not blank).

## Integration

### With BA Assistant
Invoked when `/canvas` or `/status` is run. The orchestrator passes current initiative context. The canvas is generated/refreshed automatically.

**`/status` MUST trigger all three outputs:**

1. **Chat status** â€” the standard `/status` text output in the conversation
2. **Canvas refresh** â€” overwrite the living `.canvas.tsx` file with current data (ALL 8 TABS)
3. **HTML snapshot** â€” overwrite the standalone HTML file with current data (ALL 8 SECTIONS)

If the agent runs `/status`, all three outputs are mandatory. Never generate only the chat status without also refreshing the canvas and HTML. Never produce fewer than 8 tabs/sections in either output.

**`/canvas` MUST trigger both file outputs:**
1. **Canvas** â€” `.canvas.tsx` with 8 interactive tabs
2. **HTML** â€” `status-snapshot.html` with 8 interactive sections

### Critical failure mode to prevent

**The most common failure is producing fewer than 8 tabs (was 7 pre-Wave 3).** This happens when:
- The agent doesn't read the SKILL.md fully and invents its own tab structure
- The agent reads some project files but not all, and decides some tabs "aren't needed"
- The agent replaces a required tab with a project-specific tab (e.g. "Compliance" instead of "Traceability")
- The agent forgets the Workstreams tab (Wave 3, was "Modes")

**Prevention:** The 8 tabs are fixed by design. Project-specific content goes INSIDE the tabs, not as replacement tabs. For example:
- Compliance decisions go in the **RAID & Tracker** tab (decisions section)
- Cohort models go in the **Traceability** tab (requirement â†’ slice â†’ story mapping) AND **Features tab** (cohort cards when a feature is in scope)
- Workshop schedules go in the **Critical Path** tab (milestones/actions)
- Per-feature/cohort workstream state goes in the **Workstreams** tab (NOT in Features â€” Features shows status summary; Workstreams shows the full grid)
- MoSCoW gaps go in **Tracker** (warnings section) and **Overview** (warning callouts)

### HTML snapshot output (mandatory â€” same 8 sections)

On every `/status` or `/canvas` invocation, generate (or overwrite) a standalone HTML file at:

```
<project-analysis-folder>/status-snapshot.html
```

For example: `blueprints/[initiative-slug]/outputs/status-snapshot.html`

**The HTML file MUST:**
- Be a **single self-contained file** (inline CSS + inline JS, no external dependencies, no CDN links)
- Use the **same data** as the canvas â€” same feature status, decisions, risks, milestones, actions, dependencies
- Have **interactive tab navigation** (JavaScript `onclick` to show/hide tab panels)
- Include all **8 sections** matching the canvas tabs (Wave 3, refined in canvas demo iteration May 2026):
  1. **Overview** â€” stakeholder-readable stats (Days to deadline, Features on track, Active blockers, Decisions confirmed), "Where we are right now" callout, Top blockers grid (no separate "Warnings & call-outs" section), Where each scope is, Confidence table â€” all rows emoji-prefixed
  2. **Workstreams** â€” Workstream grid (HTML table with scopes as rows and **8 workstreams** as columns: Intake, Kickoff, Discovery, Slicing & Sequencing, Solution, Delivery, Playback, Eval & Retro). NO M0â€“M8 codes in the user-facing UI. Cells coloured by state (ðŸŸ¢ Done, ðŸ”µ Active, â¸ Paused, â—‹ Not started, Â· N/A). Cohort rows indented with `â†³` prefix and zebra-striped. Section divider lines between initiative / features / cohorts groups. Horizontal compact legend BELOW the grid. Recent workstream changes log below.
  3. **Features & Delivery** â€” feature table with active workstreams pill, cohort/slice cards when a feature is in scope, Jira ticket table with MoSCoW column (emoji-prefixed: ðŸ”´ Must, ðŸŸ¡ Should, ðŸ”µ Could, âšª Won't, âš  unrated), MoSCoW matrix table per requirement
  4. **Timeline** â€” HTML/CSS Gantt with **Milestones swimlane at the TOP** (each milestone = emoji + label + date stacked below, e.g. "âš–ï¸ / Legal sign-off / 27 May"), then team/area swimlanes (BA Analysis, Compliance/Legal, F1 Eng, F2 Comms, F3 Reporting). Vertical **blue dashed Today line** + vertical **red dashed Deadline line** with â›” date label. Bar length = duration in weeks Ã— column width. Bars auto-pack into sub-rows so they never overlap. Date column headers in actual dates (e.g. "18 May, 25 Mayâ€¦") NOT week codes (W21, W22). Horizontal compact legend below.
  5. **Dependencies** â€” Active blockers callouts at top, then static rendering of the dependency DAG (HTML table showing From â†’ To with status colours, or inline SVG with click-to-highlight if feasible). Critical chains shown as horizontal pill chains beneath.
  6. **Traceability** â€” table-based: âš–ï¸ Driver â†’ ðŸ“‹ Requirement â†’ ðŸ• Slice â†’ ðŸŽŸï¸ Story â†’ ðŸ“Œ ADR mapping with colour coding. Requirement rows show MoSCoW pills per scope.
  7. **Critical Path & Actions** â€” milestone table with status emoji pills, this-week actions from action register, MoSCoW warnings if any, workshop schedule
  8. **RAID & Tracker** â€” RAID cards (ðŸ“Œ Decisions, ðŸ§¨ Risks, â“ Open Questions, âš ï¸ Assumptions, ðŸŽ¯ Actions) using `<details>/<summary>` collapsibles. **"Show outstanding items only" toggle defaults to CHECKED** (so the page opens to what needs attention). IDs in the last column with small font; descriptions get the prime column.
- **Scope navigator** rendered above the tab strip with three visually-grouped pill clusters separated by `|`:
  - "ðŸ›ï¸ Initiative level" pill (default selected, blue/info tone with âœ“ prefix when active)
  - Feature pills (F1, F2, F3)
  - Cohort pills
  - **UX rules:** Clicking "Initiative level" clears all other selections. Clicking a feature or cohort auto-deselects "Initiative level". If all selections cleared, snap back to "Initiative level". A "Showing: X, Y, Z" line directly below the pills shows the active filter state in plain text. Selected pills get a âœ“ prefix and `info` tone; unselected pills `neutral` tone.
- Be viewable in **any modern browser** without a dev server or build step
- Include a **"Generated" timestamp** and version in the footer
- Include **project name, date, BA/PM/TL names** in a header
- Use a **clean, professional layout** with:
  - CSS variables for status colours. **In-progress MUST be BLUE (`#3b82f6`)**, never amber/brown. Done = green, Pending = grey, Blocked = red.
  - Responsive design (works on mobile and desktop)
  - `<details>/<summary>` for collapsible RAID sections (native HTML, no JS library needed)
  - Horizontal bar charts rendered as inline SVG (same visual as canvas `HorizontalBarChart`)
  - Timeline Gantt rendered as inline SVG (matches a project canvas pattern â€” swimlanes as rect rows, bars as positioned rects, today/deadline as vertical dashed lines, milestone strip as the TOP lane)
  - Workstream grid rendered as inline SVG (consistent cell positioning, hover tooltips, zebra row backgrounds, section dividers between scope groups)
  - All legends rendered horizontally as small inline elements below their visual (not vertical lists in the page chrome)
  - Tab navigation via simple JS that shows/hides `<section>` elements
- **Emoji set (use real Unicode, never ASCII shapes):**
  - Status: ðŸŸ¢ Done, ðŸ”µ In progress / Active, ðŸ”´ Blocked / At risk, ðŸŸ¡ At risk / Medium, â¸ Paused, â—‹ Not started / Pending, â›” Hard deadline / Blocker
  - Workstream / scope markers: ðŸ›ï¸ Initiative level, â†³ Indent for cohorts
  - Milestones: ðŸ“… Date, ðŸš€ Launch, âš–ï¸ Legal sign-off, ðŸ“§ Comms send, ðŸ“Š Reporting milestone
  - RAID cards: ðŸ“Œ Decisions, ðŸ§¨ Risks, â“ Open questions, âš ï¸ Assumptions, ðŸŽ¯ Actions
  - Traceability node kinds: âš–ï¸ Driver, ðŸ“‹ Requirement, ðŸ• Slice, ðŸŽŸï¸ Story, ðŸ“Œ ADR
  - Never use ASCII substitutes (`âœ“ â— â—‹ â€”`) where Unicode emoji is available

**HTML template structure:**

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>[Project Name] â€” Status as at [Date]</title>
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
  <div class="scope-nav"><!-- Breadcrumb: Initiative â–¸ Feature â–¸ Cohort/Slice + Clear scope button --></div>
  <nav><!-- 8 tab buttons --></nav>
  <main>
    <section id="tab-overview"><!-- Stakeholder stats, "where we are right now" callout, Top blockers grid, Where each scope is, Confidence --></section>
    <section id="tab-workstreams"><!-- SVG workstream grid: scopes as rows (cohorts indented + zebra striped), 8 workstreams as columns (Intake â†’ Eval & Retro), no M-codes. Horizontal legend below. Transitions log. --></section>
    <section id="tab-features"><!-- Feature table with active workstreams, cohort/slice cards, Jira tickets with MoSCoW column (emoji-prefixed), MoSCoW matrix --></section>
    <section id="tab-timeline"><!-- SVG Gantt with Milestones swimlane at TOP, then team lanes. Today + Deadline vertical lines. --></section>
    <section id="tab-dependencies"><!-- Active blockers callouts, dependency DAG, critical chains --></section>
    <section id="tab-traceability"><!-- âš–ï¸ Driver â†’ ðŸ“‹ Requirement â†’ ðŸ• Slice â†’ ðŸŽŸï¸ Story â†’ ðŸ“Œ ADR with MoSCoW pills per scope --></section>
    <section id="tab-critical-path"><!-- Milestones with status emojis, actions from register, MoSCoW warnings, workshops --></section>
    <section id="tab-tracker"><!-- RAID cards (ðŸ“ŒðŸ§¨â“âš ï¸ðŸŽ¯) with <details> collapsibles, "Show outstanding only" toggle defaults true --></section>
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

    // Scope navigator (Wave 3) â€” sets body[data-scope-level] and body[data-scope-id]
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

### Standalone (without BA Assistant)
Can be triggered directly by a user asking for "project canvas" or running the `/canvas` command. The skill self-bootstraps by:
1. **Automatically** searching for project files (Glob for `**/blueprints/**/*.md`, `**/docs/**/*.md`)
2. **Reading ALL** `.md` files found in the project directory (mandatory â€” no exceptions)
3. **Attempting** Jira MCP sync if available
4. **Only then** asking the user for genuinely missing information via `AskQuestion`

The output is always both files: `.canvas.tsx` + `status-snapshot.html`, both with 8 tabs/sections.

### Reference implementation

The canonical reference for both outputs is the **project canvas demo**:
- Canvas: `~/.cursor/projects/<your-project>/canvases/[initiative-slug]-demo.canvas.tsx`
- HTML: `~/.cursor/projects/<your-project>/canvases/[initiative-slug]-demo.html`

When in doubt about pattern, dimensions, naming, or filter behaviour, read those two files. The pre-delivery self-check above was distilled from real regressions caught during demo-iteration feedback (May 2026).

### Refresh cycle
Each refresh overwrites the single living canvas file AND the HTML snapshot. Both files are regenerated from current data. All interactive state (active tab, filter selections, selected nodes) is preserved via `useCanvasState` across rebuilds â€” stored in a `.canvas.data.json` sidecar file.

### File locations summary

| Output | Path | Purpose |
|---|---|---|
| Canvas | `~/.cursor/projects/<workspace>/canvases/<project-slug>-status.canvas.tsx` | Interactive dashboard in Cursor |
| HTML | `<project-analysis-folder>/status-snapshot.html` | Shareable status page for non-Cursor users |
| State | `~/.cursor/projects/<workspace>/canvases/<project-slug>-status.canvas.data.json` | Preserves interactive state (auto-managed) |

### Opening the canvas
After generation, instruct the user:
1. Open Cursor Command Palette (Cmd/Ctrl+Shift+P)
2. Search "Cursor: Open Canvas"
3. Select the generated canvas from the list
4. The canvas opens as a live interactive panel beside the chat

Or: Click the "Canvases" icon in the sidebar (if visible) and select the canvas.

---

## Data model

See `references/canvas-data-model.md` for the canonical schema,
workstream state transition rules, metric computation rules, and
canvas tab structure.

### Data tasks (formerly ba-status-data-model)

**1. Create or update `status-data.json`** â€” When `/status` or `/publish-status` is invoked:
- If `status-data.json` does not exist, create it from the current state (SESSION-CONTEXT, Jira, open-questions, etc.).
- If it exists, read it and update only the fields that have changed.
- Always invoke `ba-jira-sync` before updating ticket statuses.
- Compute `daysOverdue` for each blocker by comparing `targetDate` to today's date.
- Compute `ageDays` for each open action and unknown.

**2. Feed downstream outputs** â€” After `status-data.json` is updated, these outputs read from it:
- `ba-project-canvas` â†’ `.canvas.tsx` (this skill)
- `status-snapshot.html` (this skill)
- Status Page Standard Format (in `ba-profile.mdc`) â†’ Confluence markdown body

**Change the data once, regenerate all three outputs.**

**3. Date-aware status computation** â€” For blockers and critical path items with `targetDate`:
| Condition | Computed status |
|---|---|
| targetDate is null | Use manually set status |
| targetDate > today + 3 days | `pending` or `in-progress` (as set) |
| targetDate is within 3 days | `imminent` â€” flag in outputs |
| targetDate = today | `due-today` â€” flag prominently |
| targetDate < today | `overdue` â€” auto-escalate per `ba-risk-and-tracker` rules |

**4. Validation before output** â€” Before any output is generated, validate:
- Every ticket in `tickets[]` has been synced within the last 24 hours (check `lastJiraSync`).
- Every blocker has an `owner`.
- Every critical path item with status `in-progress` has a `date`.
- No decision has `status: "TBC"` for more than 7 days without being logged as a risk.
- Every requirement in `delivered` state has linked tickets all marked Done.
- Tickets in `In Progress` with `moscowFlag: missing` surface a warn-and-flag entry.

**5. Migration for existing initiatives** â€” For initiatives that already have status outputs but no `status-data.json`:
- Read SESSION-CONTEXT.md, open-questions.md, confluence-pages.json, and the latest Confluence status page.
- Extract structured data and populate `status-data.json`.
- This is a one-time migration â€” after that, `status-data.json` is the source of truth.

### Data anti-patterns to prevent

- **Never update a downstream output directly without also updating `status-data.json`** â€” if someone asks to change a status, update the JSON first, then regenerate.
- **Never add a ticket to `status-data.json` without a Jira key** â€” all tickets must be traceable.
- **Never skip the Jira sync** â€” stale ticket data is worse than no data.
- **Never store computed fields** (`daysOverdue`, `ageDays`, `moscowFlag`) â€” recalculate on every read so they're always current.
- **Computing a metric as 0% when data is missing.** If a metric can't be computed, show `n/a`. Fabricated zeros look like real signals and trigger false alarms.
- **Caching metrics longer than 1 hour.** Stale metric values create false confidence. Recompute on every status output.

### Status page output (Wave 7)

Status page publication lives in this skill (there is no separate `ba-status-page-publisher` sub-skill).

#### Standards used

- `references/status-page-format.md` â€” page structure, section ordering, outcome health gate, supersede protocol
- `references/raid-format.md` â€” RAID rendering on the status page
- `references/canvas-data-model.md` â€” source data (status-data.json and metrics-cache.json)

If standards conflict with skill-specific guidance below, the standard wins.

#### Output format
Status pages conform to `references/status-page-format.md`. Read that file before publishing any status page. The format is the authoritative source.


