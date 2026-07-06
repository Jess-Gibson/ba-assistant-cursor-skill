# Visual Output Format Standard

**Location:** `~/.cursor/skills/ba-assistant/references/visual-output-format.md`
**Owner:** ba-visual-storytelling (primary), ba-project-canvas (canvas-specific outputs)
**Last reviewed:** 2026-05-30

This file is the canonical source for how the BA Assistant produces visual artefacts. Any sub-skill producing a diagram, flowchart, timeline, journey map, or visual status output MUST conform to this standard. Anti-Pattern Detector flags non-conformant output.

---

## 1. Decision: when to produce a visual at all

Default to prose unless ANY of these are true:

- The reader needs to see relationships between elements that don't reduce to a list (process flow, system architecture, dependency graph)
- Time or sequence matters (timeline, sequence diagram, Gantt)
- Comparison across two or more dimensions (journey map, swimlane, matrix)
- The audience is a meeting or playback where visual carry is needed for retention
- The user explicitly asks for one

Don't produce a visual when:

- A list or table communicates the same content more directly
- The visual would have <4 nodes (a sentence works better)
- The relationships are trivially linear (numbered list works better)
- The user is asking a question, not requesting an artefact

---

## 2. Default output format: interactive HTML

The default format for any standalone visual is **self-contained interactive HTML**. Reasons:

1. Renders identically anywhere (browser, attached to Confluence, sent as a link, opened from email)
2. No plugin dependency (Mermaid plugin is not universally available in modern Confluence / Jira tooling)
3. Interactivity supports detail-on-demand without bloating the visual itself
4. Print-to-PDF produces a clean static export when needed

Mermaid is a fallback for inline-in-Confluence cases only. See Section 8 for embedding strategy.

---

## 3. The shared design system

Every interactive HTML diagram uses the same design system so they feel like one product.

### Colours (CSS custom properties)

```css
:root {
  --bg: #faf9f6;
  --panel: #ffffff;
  --ink: #1c1c1c;
  --ink-soft: #4a4a4a;
  --ink-faint: #8a8a8a;
  --rule: #e5e3dd;

  /* Node taxonomy (process flow default) */
  --deterministic: #2563eb;  /* automated, rule-based, programmatic */
  --ai: #0891b2;             /* probabilistic, model-driven */
  --human: #059669;          /* human-in-the-loop */
  --decision: #d97706;       /* gates, branches */
  --output: #7c3aed;         /* outcomes, terminal states */

  /* Backgrounds for each taxonomy colour */
  --deterministic-bg: #dbeafe;
  --ai-bg: #cffafe;
  --human-bg: #d1fae5;
  --decision-bg: #fed7aa;
  --output-bg: #ede9fe;
}
```

### Typography

- Display: Source Serif Pro 600 (titles, big numbers)
- Body: IBM Plex Sans 400/500/600
- Monospace: IBM Plex Mono (codes, IDs, timestamps)
- All loaded from Google Fonts CDN for portability

### Layout

- Max width 1280px, centred
- Generous padding (32px+) on cards and panels
- Panels: white background, 1px rule border (`--rule`), 6-8px border radius
- Stats bars: grid layout, 1px internal rules, one stat per cell

### Interaction pattern

- Click a node → slide-out detail panel from the right
- Detail panel shows: type chip (colour-coded), title, actor, duration, what happens, failure modes, connected requirements / RAID tags
- Esc key closes the detail panel
- Hover on a node: subtle brightness shift and translateY(-1px)
- Active node: stroke-width doubles

### Required elements on every visual

- Header with eyebrow / title / subtitle / metadata (owner, last reviewed, ID)
- Stats bar showing counts per type
- Colour legend
- Footer with generation date and short note
- Slide-out detail panel (HTML always present, CSS hidden by default)

---

## 4. Supported diagram types — and when to use each

Every visual must earn its place: it answers a specific question or anchors a specific decision. If it just duplicates the text, skip it (or replace the text).

| # | Type | When | What it shows | Format | Watch for |
|---|---|---|---|---|---|
| 1 | Initiative one-pager | PM/exec needs the initiative in 60 seconds | Problem → stakeholder impact → gap vs future state → solution at a glance → success metrics → key blockers | Interactive HTML (or static SVG for decks) | Density — must read in under 60s |
| 2 | Current state architecture | Solution shaping, technical discovery, onboarding | Services, data stores, integration points, external dependencies | Mermaid `flowchart` / HTML flowchart template | Only the boxes that matter for THIS initiative |
| 3 | Future state architecture | Solution shaping, ADRs, playback | Current-state shape with proposed changes highlighted | Mermaid / HTML | Mark new vs unchanged explicitly |
| 4 | Sequence diagram | A specific cross-service flow where order matters | Actors + messages chronologically | Mermaid `sequenceDiagram` | Don't use when sequence doesn't matter |
| 5 | Slice dependency diagram | After Feature Slicing | Slices as nodes, dependencies as edges, critical path highlighted, parallel tracks visible | Mermaid `flowchart LR` with criticality classes | Show what BLOCKS what, not just what exists |
| 6 | Stakeholder influence × interest grid | Stakeholder Strategy | 2×2 grid, engagement strategy per quadrant | SVG/HTML (spatial accuracy beats Mermaid) | Anchor placement in evidence, not impressions |
| 7 | Progress dashboard | Risk & Tracker snapshots | Phase %, confidence deltas, risk trend, sign-off rate, overdue items | HTML widget | Highlight what CHANGED, not everything |
| 8 | Gantt timeline | Date-sensitive work, critical path | Items on a timeline, dependencies, critical path, slack | Mermaid `gantt` or SVG | Show slack and risk, not just bars |
| 9 | Side-by-side option comparison | Solution Shaping with 2-3 options | Parallel columns, SAME dimensions per option (pros, cons, effort, risk) | HTML widget | Apples to apples — identical dimensions |
| 10 | Decision tree | Non-trivial ADR with branching consequences | Question, options, consequence of each | Mermaid `flowchart` | One decision per tree |
| 11 | Journey map (current vs future) | UX / service design / operational change | User steps, pain points highlighted, future state side by side | SVG/HTML (see §7) | Map the ACTUAL flow, not the sanitised one |
| 12 | Risk heatmap | 5+ open risks | Probability × impact plot, mitigation status marked | SVG/HTML | Show what's mitigated vs still open |

### Template file mapping (local — kept from the pre-W10 table)

| Type | Template file |
|---|---|
| **Flowchart** (current/future state, logic, decision flow, end-to-end process) | `references/templates/flowchart.html` |
| **Swimlane** | `references/templates/swimlane.html` (TODO) |
| **Timeline / Gantt** | `references/templates/timeline.html` (TODO) |
| **Journey map** | `references/templates/journey.html` (TODO) |
| **State diagram** | `references/templates/state.html` (TODO) |
| **Sequence diagram** | `references/templates/sequence.html` (TODO) |
| **Architecture / system** | `references/templates/architecture.html` (TODO) |
| **Decision tree** | `references/templates/decision-tree.html` (TODO) |

Flowchart is the only template fully built. The others are TODO until first real use. When a sub-skill needs a non-flowchart visual, the first instance of producing that type triggers the template creation (using the flowchart template as the design-system anchor).

---

## 5. Flowchart-specific structure

### Node types (with colour taxonomy)

| Type | When | Colour | Shape |
|---|---|---|---|
| Deterministic | Automated rule-based or programmatic step (system action, scheduled job, API call with deterministic outcome) | Blue (`--deterministic`) | Rounded rectangle |
| AI / probabilistic | Model-driven step with confidence score, classification, scoring, or recommendation | Cyan (`--ai`) | Rounded rectangle |
| Human-in-loop | Manual action, review, approval, or judgement step | Green (`--human`) | Rounded rectangle |
| Decision gate | Branching point with explicit conditions | Amber (`--decision`) | Diamond |
| Output | Terminal state, outcome, deliverable | Purple (`--output`) | Rounded rectangle with thicker stroke |

### Required content per node

Every node has, captured in the `nodes` JS object:
- `type` — one of: deterministic / ai / human / decision / output
- `title` — short label visible on the node
- `actor` — who or what performs the step
- `duration` — typical time
- `desc` — 1-2 sentence plain-English description of what happens
- `failures` — known failure modes (1-2 sentences)
- `tags` — array of related requirement IDs, RAID IDs, ADR IDs

### Required content on edges

- Direction is enforced by arrow markers
- Labels only on decision-gate outgoing edges (e.g. "Low risk", "High risk", "Pass", "Block")

### Anti-patterns for flowcharts

- More than 12 nodes on one diagram → split into sub-flows
- Decision gates with more than 4 outgoing edges → restructure
- No `desc` or no `failures` content → fails the standard
- Generic node titles ("Process step 1") → fails the standard
- Mixed taxonomy (a node coloured human but described as automated) → fails the standard

---

## 6. Timeline / Gantt-specific structure

(Template TODO. When first needed, build with these rules:)

### Row organisation

- Rows grouped by workstream (matches `status-data.json` workstream model)
- Each row is one work item: epic, story, spike, milestone, or dependency
- Workstream label on the left, swimlane background tint per workstream

### Bar colouring

- Workstream colour for the body of the bar
- Stripe pattern for spikes (distinguishes investigative from build work)
- Solid for confirmed work; outlined-only for tentative or at-risk
- Milestone markers as diamonds, not bars

### Required interactivity

- Click any bar → slide-out detail panel (same pattern as flowchart)
- Detail panel shows: work item title, type, scope, owner, dates, dependencies, status, linked tickets
- Today line visible as vertical rule
- Past work fades slightly (opacity 0.7); current and future at full opacity

---

## 7. Journey map-specific structure

(Template TODO. When first needed, build with these rules:)

### Grid structure

- Columns are phases (acquisition, onboarding, activation, retention, etc.)
- Rows are: touchpoints, user actions, user thoughts, sentiment, pain points, opportunities
- Cells contain short text or single icons

### Sentiment colouring

- Positive sentiment: green tint
- Neutral: no tint (panel background)
- Negative: amber tint
- Pain point cells: red border (not full background)

### Required interactivity

- Click any cell → slide-out detail panel with full description, evidence (research data, ticket links, customer quotes), opportunity sizing

---

## 8. Embedding in Confluence

Three patterns depending on environment support.

### Pattern A — Confluence supports native Mermaid

Inline the Mermaid block in the Confluence page. Use the same colour taxonomy via `classDef`:

```
classDef det fill:#dbeafe,stroke:#2563eb,stroke-width:1.5px,color:#1c1c1c
classDef ai fill:#cffafe,stroke:#0891b2,stroke-width:1.5px,color:#1c1c1c
classDef hum fill:#d1fae5,stroke:#059669,stroke-width:1.5px,color:#1c1c1c
classDef dec fill:#fed7aa,stroke:#d97706,stroke-width:1.5px,color:#1c1c1c
classDef out fill:#ede9fe,stroke:#7c3aed,stroke-width:2px,color:#1c1c1c
```

Use this when the reader will only consume in Confluence and the diagram has <12 nodes.

### Pattern B — Confluence does NOT support native Mermaid (no Mermaid plugin installed)

1. Generate the interactive HTML standalone file
2. Attach to the Confluence page (`createConfluenceAttachment` or manual upload)
3. Take a screenshot of the rendered HTML and embed the image inline as a preview
4. Add a caption: "Interactive version attached to this page. Click to download for clickable detail."

### Pattern C — Standalone link (Slack, email, ticket)

1. Generate the interactive HTML file in the initiative's `visuals/` folder
2. Share the file directly or host on internal share

### Decision rule

The Visual Storytelling skill decides based on context:
- If output destination is Confluence AND environment has Mermaid plugin → Pattern A
- If output destination is Confluence AND no plugin → Pattern B (default when no Mermaid plugin)
- If output destination is non-Confluence (Slack, email, attached file) → Pattern C

When ambiguous, ask the user once via AskQuestion. Don't guess.

---

## 9. Template invocation

When a sub-skill needs to produce a visual:

1. Read `references/templates/<type>.html`
2. Identify the `nodes` (or equivalent data structure) JS object near the bottom of the template
3. Replace with the actual content for this initiative
4. Update the header (title, subtitle, metadata)
5. Update the stats bar counts
6. Save to `<initiative-folder>/visuals/<slug>.html`
7. If publishing to Confluence in Pattern B mode, also generate a PNG screenshot via the browser's print API and attach both files

The template HTML files are the source of truth for design system + interaction pattern. Don't reinvent the design system per visual; copy the template and replace content.

---

## 10. Output anti-patterns (Anti-Pattern Detector triggers)

| Watching | Trigger | Anti-pattern flagged |
|---|---|---|
| Visual Storytelling | Visual produced as Mermaid AND destination is Confluence Pattern B (no native render) | Mermaid in non-rendering environment — should be interactive HTML |
| Visual Storytelling | Visual produced AND no colour taxonomy applied (default browser styling) | Off-standard visual — missing design system |
| Visual Storytelling | Flowchart >12 nodes on one page | Diagram too dense — split into sub-flows |
| Visual Storytelling | Node lacks `desc` or `failures` content in the data object | Incomplete node detail — fails the standard |
| Visual Storytelling | Mixed taxonomy (e.g. node coloured human but described as system action) | Taxonomy mismatch |
| Project Canvas | Canvas regenerated AND visual outputs not refreshed | Stale linked visuals — canvas update implies visual update |

---

## 11. Versioning

This standard is versioned. Each visual generated should include a comment at the top:

```html
<!-- Visual produced against visual-output-format.md v1.0 / 2026-05-30 -->
```

When the standard changes, the version increments. Visuals produced against older versions don't auto-regenerate, but a `/audit-visuals` command (TODO) can list visuals against outdated standards.

---

## 12. Quick reference card

```
DEFAULT: Interactive HTML
COLOUR TAXONOMY: deterministic / AI / human / decision / output
INTERACTION: click for slide-out detail
ATTACH TO CONFLUENCE: HTML file + PNG preview inline
MERMAID: only for Confluence pages with working plugin AND <12 nodes
TEMPLATE LOCATION: references/templates/<type>.html
```
---

## 13. Storytelling framework (for narrative visuals)

For any narrative-driven visual (one-pagers, playback decks, status comms), structure the story as:

1. **Problem** — what's the situation, who experiences it, why does it matter?
2. **Evidence** — what do we know, what data backs it, what was investigated?
3. **Choice** — what are the options, what's recommended, what was rejected?
4. **Consequence** — what happens if we proceed; what changes, what doesn't?
5. **Ask** — what decision is needed, from whom, by when?

Not every visual needs all five, but the arc should be visible. For multi-visual outputs (playback deck, sectioned one-pager), sequence the visuals along this arc — each one moves the narrative forward. A visual that is pretty but supports no decision or finding gets redone or cut.

---

## 14. Production workflow

### Two modes

**Quick mode (default):** the user asked for a specific visual, content is clear, destination implied. Generate, output, one-line self-critique.
**Deep mode:** stakeholder communication, narrative visual, or vague request. Clarify first (what question does this answer? who's the audience? where will it live? what decision does it support?), apply §13 fully.

### Steps

1. Pick the type from §4. 2. **Anchor in content** — pull actuals from the tracker, register, or solution options; never emit a generic template. 3. Produce per the format decision (§8) and template (§9). 4. Apply §13 if narrative. 5. Self-critique: does it answer the question? readable in 60 seconds? does it earn its place vs the text? 6. Output with the block below and offer iteration.

### Output block (every visual)

```
What this shows: <one line>
Audience: <who> · Destination: <where> · Format: <Mermaid / HTML / SVG>
[the visual]
Self-critique: <what would a senior reviewer push back on?>
```

### Iteration loop

Visuals rarely land first time. Offer: more/less detail, different format, shifted emphasis. If the user says it isn't hitting the mark, don't regenerate blind — ask what specifically isn't working (usual suspects: wrong detail level, wrong story emphasis, wrong format for destination, generic where it needed to be specific).

### Boundaries (unchanged from the skill)

Doesn't write text content (pulls it from other skills' outputs); doesn't pick the recommended option (shows the options); complements narrative, never replaces it; no visuals for their own sake.

### Summoning a visual directly (Wave 10 — discoverability)

Users can invoke this standard without naming any skill: "interactive HTML flowchart of X", "clickable flow diagram", "HTML diagram I can send to stakeholders" all route here (see `skills-routing.mdc`). For flowcharts specifically: read §5 + §9, start from `references/templates/flowchart.html` (design system, interaction pattern, and detail panel stay as-is; replace header, stats, nodes, edges, and the `nodes` JS object with real content), save to `<initiative-folder>/visuals/<slug>.html`.
