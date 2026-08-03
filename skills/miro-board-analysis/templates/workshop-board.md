# Template: Workshop / Facilitation Board

Patterns for building workshop boards  -  kickoffs, discovery sessions, retrospectives, and general facilitation. All dimensional values and colours reference `design-system.md`.

For verified kickoff-specific DSL patterns, see `kickoff-board-template.md`.
For spike card DSL, see `spike-card-template.md`.

---

## Pattern 1: Full Workshop Board Layout (Kickoff)

Build a complete kickoff workshop board as a single wide frame. One horizontal frame containing all sections.

**Approach:**
1. Call `layout_get_dsl` once to get the DSL spec
2. Plan the full layout  -  calculate frame sizes and positions
3. Build all content in a single `layout_create` call (or split into logical batches if content exceeds 50,000 chars)

**Verified kickoff board structure (horizontal, ~27500 x 2540):**

```
┌──────────────────────────────────────────────────────────────────────────────────────────────┐
│ SINGLE FRAME: "[Initiative] - Internal kick off ([Date])"                                    │
│                                                                                              │
│ ┌─────┐ ┌──────────┐ ┌──────────┐ ┌─────┐ ┌────────────────┐ ┌────────────┐ ┌────────────┐ │
│ │Agenda│ │Problem   │ │Metrics   │ │SLAs │ │  Questions     │ │ Plan Table │ │ HLR        │ │
│ │     │ │statement │ │         │ │     │ │  (Q&A grid)   │ │            │ │            │ │
│ ├─────┤ ├──────────┤ ├──────────┤ │     │ │                │ │            │ │            │ │
│ │Docs │ │Stakehold.│ │Scope     │ │     │ │                │ │            │ │            │ │
│ │& ref│ │(names)   │ │(IN/OUT)  │ │     │ │                │ │            │ │            │ │
│ └─────┘ └──────────┘ └──────────┘ └─────┘ └────────────────┘ └────────────┘ └────────────┘ │
│                                                                                              │
│ ┌────────────────────┐ ┌────────────────────┐ ┌───────┐ ┌────────┐ ┌────────────┐           │
│ │ Service design      │ │ RAID (4 columns)    │ │ Next  │ │Actions │ │ Things to  │           │
│ │ (diagrams/flows)    │ │ R | A | I | D       │ │ steps │ │& follow│ │ remember   │           │
│ │                    │ │ [bordered columns]  │ │       │ │ ups    │ │            │           │
│ └────────────────────┘ └────────────────────┘ └───────┘ └────────┘ └────────────┘           │
└──────────────────────────────────────────────────────────────────────────────────────────────┘
```

Each section uses the Content Panel Pattern from `design-system.md`:
1. Coloured header shape (round_rectangle, one of the 5 tiers, h=82 standard)
2. Grey backdrop box below the header (`fill=#e6e6e6 type=rectangle`, sized to fit actual content)
3. Text element positioned **inside** the grey box  -  text y near the TOP (NOT vertically centered)
4. Other content (stickies, tables, cards) positioned as needed within or around the grey zone

---

## Pattern 2: Brainstorming Space

Create an open area for participants to add stickies. The facilitator provides the prompt; participants fill in.

**Build with `layout_create`:**
- A **frame** sized generously (e.g., 3000 x 2000)
- A **title shape** (Secondary tier: `fill=#c497fe color=#7b14ef`) at the top with the brainstorm prompt
- **Seed stickies** (2-3 examples using `light_yellow` to prime thinking)
- Leave the rest of the frame empty  -  participants add their own stickies during the session

**Color convention for brainstorming:**

| Color | Role |
|---|---|
| Secondary header shape (`#c497fe`) | Facilitator prompt / section title |
| `light_yellow` stickies | Participant input (default) |
| `light_green` stickies | Facilitator seed examples or positive items |
| `orange` stickies (square, `w=154-212`) | Medium concerns or notable items |
| `red` stickies (square, `w=154`) | Critical items, blockers |

---

## Pattern 2b: Q&A Sticky Grid

Structured question-and-answer pairs  -  a grid of alternating coloured stickies.

**Build with `layout_create`:**
- A **background shape** (`fill=#f5f5f5`, `type=rectangle` for the content area, or `type=round_rectangle` for bounded zones)
- A **header shape** (Secondary tier: `fill=#c497fe color=#7b14ef` size 100 titled "Questions")
- **Columns** of sticky pairs:
  - `dark_blue` sticky (top, `w=365`, `shape=rectangle`) = the question prompt
  - `light_yellow` sticky (below, +180 y offset, same width) = space for the response
- Multiple columns side by side (x spacing ~453px per column, center-to-center)
- Multiple rows of pairs (y spacing ~470px per pair group)
- Grid fits inside the background shape  -  typically 5-6 columns across `w=2397`

**DSL example (single Q&A pair):**
```
STICKY parent={frameUrl} x=4352 y=465 w=365 color=dark_blue shape=rectangle align=center valign=middle "Question text here"
STICKY parent={frameUrl} x=4352 y=652 w=365 color=light_yellow shape=rectangle align=center valign=middle ""
```

**Use for:** Structured workshop questions, interview prompts, compliance check questions, "what do we know / what don't we know" grids

---

## Pattern 3: Sticky Stack (Structured Input)

Participants respond to a specific question  -  a vertical column of stickies.

**Build with `layout_create`:**
- A **frame** (600 x 2000  -  narrow and tall)
- A **question text** or shape at the top
- Pre-placed **numbered stickies** as slots (e.g., "1. [Your idea]", "2. [Your idea]") OR leave empty for free-form contribution

**Use for:** "What are the risks?", "Name one blocker", "What should we keep doing?"

---

## Pattern 4: Decision / Outcome Capture

After discussion, capture decisions, owners, and actions.

**Build with `table_create` + `table_sync_rows`:**
- Create a table with columns: Decision | Owner | Date | Status
- Use `select` columns for Status with color-coded options (To Do = `#D6D6D6`, In-progress = `#A0C4FB`, Done = `#79E49B`)
- Populate rows with outcomes from the session

**Alternatively, use `layout_create` for a visual layout:**
- A Dark header shape (`fill=#232428 color=#ffffff` size 64) titled "Actions & follow ups"
- Content panel below (grey zone pattern: small `round_rectangle` h=284 + large `rectangle` h=825, both `fill=#e6e6e6`)
- Text item inside with `<ol><li><strong>Action</strong> - Owner</li></ol>` format
- Use `<s>...</s>` for completed items (strikethrough)
- A Tertiary header shape (`fill=#fff854 color=#394666` size 64) titled "Next steps" for follow-ups
- Adjacent panel: "Things worth remembering" with Secondary header (`fill=#c497fe color=#394666`)

### Pattern 4b: Actions List with Text (Long Format)

For detailed action lists captured during workshops  -  see DSL snippet in `design-system.md` under "Dark Header" and "Content Panel" templates.

---

## Pattern 5: Populate an Existing Template/Frame

When the user provides a URL pointing to a specific frame that already has structure (e.g., a Miro template), populate it with content.

**Workflow:**
1. `layout_read` the target frame to understand existing structure
2. Identify empty sections, placeholder text, or prompt stickies
3. Use `layout_update` to replace placeholder content with real content
4. Use `layout_create` (targeting the frame URL) to add new items in empty areas
5. Report back what was populated

---

## Pattern 6: Voting / Prioritisation Board

Structured space for dot-voting or priority ranking.

**Build with `layout_create`:**
- A frame with options as large shapes (rectangles) arranged horizontally
- Each option has a label and description
- Below each option, empty space for vote stickies
- A divider line and "Instructions" text at the top

---

## Pattern 7: Retrospective Board

Classic retro format with columns  -  uses the same visual system as RAID columns.

**Build with `layout_create`:**
- Wide frame (4000 x 2000)
- Three or four vertical sections using bordered columns (`fill=#ffffff fill_opacity=0.0 border_color=#abacf1 border_width=8.0 type=round_rectangle w=756 h=1675`)
- Column headers as text items in `#7b14ef` size 80:
  - "What went well"
  - "What didn't go well"
  - "Actions / Try next"
  - Optionally: "Shout-outs"
- Column descriptions in `#8241aa` size 24 (same pattern as RAID descriptions)
- Stickies in semantic colours (all `shape=rectangle`):
  - `light_green` (w=154) for "went well"
  - `red` (w=154) for "didn't go well" / critical
  - `orange` (w=154-212) for "concerns / moderate"
  - `light_yellow` (w=154) for neutral / "try next"
  - `light_blue` (w=154) for "shout-outs"
- Footer area with an "Actions" table or Dark header + text list pattern

---

## Pattern 7b: RAID Board

Dedicated RAID capture area  -  matches the verified board structure.

**Build with `layout_create`:**
- Section header: Secondary tier shape, `fill=#c497fe fill_opacity=0.7 color=#394666` size 64, wide (`w=3147 h=119`)  -  titled "RAID"
- Four columns, each:
  - Column container: `type=round_rectangle fill=#ffffff fill_opacity=0.0 border_color=#abacf1 border_style=normal border_width=8.0 border_opacity=1.0 w=756 h=1675`
  - Title text: `color=#7b14ef size=80`  -  "Risks", "Assumptions", "Issues", "Dependencies"
  - Description text: `color=#8241aa size=24`
  - Spacing: ~800px apart center-to-center
- Stickies inside columns follow Pattern C (see `design-system.md` Sticky Note Colours):
  - `red rectangle w=154` for critical
  - `orange rectangle w=154-212` for medium
  - `light_yellow rectangle w=154` for noted items
  - `light_green rectangle w=154` for actionable/positive

**DSL example (RAID column container):**
```
SHAPE parent={frameUrl} x=21766 y=1121 w=756 h=1675 type=round_rectangle fill=#ffffff fill_opacity=0.0 color=#394666 font=plex_sans size=59 align=center valign=middle border_color=#abacf1 border_style=normal border_width=8.0 border_opacity=1.0 ""
TEXT parent={frameUrl} x=21760 y=368 w=206 color=#7b14ef fill=#ffffff fill_opacity=0.0 font=unknown size=80 align=left "Risks"
TEXT parent={frameUrl} x=21771 y=436 w=518 color=#8241aa fill=#ffffff fill_opacity=0.0 font=unknown size=24 align=left "Potential problems that might impact success"
```

---

## Pattern 8: Current State / Future State Mapping

Two-panel comparison layout.

**Build with `layout_create`:**
- Two side-by-side frames: "Current State" and "Future State"
- Each contains a flowchart diagram OR a set of process-step shapes connected with connectors
- Use color to distinguish: current state in neutral tones, future state in blue/green

---

## Pattern 9: Stakeholder Panel

Display team members grouped by organisation or function using coloured cards.

**Build with `layout_create` or `card_create`:**
- Tertiary header shape (`fill=#fff854 color=#394666` size 64) titled "Stakeholders"
- Content panel (standard grey pattern)
- Team labels as text items: `color=#7b14ef size=39` for internal (e.g., "[Organisation]"), `color=#2d9bf0 size=39` underlined for external (e.g., "CXNPL", "GSB")
- Cards for each stakeholder, themed by role type (see Pattern D in `design-system.md`):
  - `#af7e04` (amber)  -  BA / PM leads
  - `#fe02a7` (magenta)  -  PM / Commercial
  - `#659df2` (blue)  -  Design
  - `#ffdc4a` (gold)  -  Tech team
  - `#067429` (dark green)  -  Specialist tech
  - `#2dc75c` (green)  -  PMM / Marketing
- Each card shows: Name, Role
- Grouped by function or team under the relevant label

---

## Pattern 10: Table with Project Plan

Use Miro tables for structured plans with select-type columns.

**Build with `table_create`:**
- Columns: Title (text) | Assignee (text) | Status (select) | Estimate (text) | Description (text) | Start Date (text) | End Date (text) | Color (select) | Priority (select) | Group (select)
- Status options: `To do#D6D6D6`, `In-progress#A0C4FB`, `Done#79E49B`
- Priority options: `Low#A0C4FB`, `Medium#FFED7B`, `High#FFADAD`
- Color options: `Red#FFADAD`, `Violet#AAA1FC`, `Orange#FFBD83`, `Yellow#FFED7B`, `Green#79E49B`, `Blue#A0C4FB`, `Grey#D6D6D6`, `Black#1C1C1E`
- Group options (label by workstream): custom per project

**Use for:** Draft high-level plans, backlog views, delivery tracking

---

## Ready-to-Build Workshop Templates

### Initiative Kickoff

| Frame | Content |
|---|---|
| Header | Title, date, facilitator, attendees, charter link |
| Context | Problem statement doc, background, constraints |
| Stakeholders | RACI table (table_create with select columns for R/A/C/I) |
| Scope | In-scope / out-of-scope sticky columns |
| Open Questions | Brainstorm sticky area |
| Next Steps | Actions table with Owner, Due, Status |

### Discovery Workshop

| Frame | Content |
|---|---|
| Header | Title, sprint, participants |
| Current State | Process flow diagram + pain points stickies |
| User Personas | Sticky clusters per persona |
| Requirements Brainstorm | Open brainstorm area |
| Prioritisation | MoSCoW grid (4 columns) with stickies |
| Unknowns & Risks | Two-column sticky layout |

### Sprint Retrospective

| Frame | Content |
|---|---|
| Header | Sprint name, date, team |
| What Went Well | Green sticky column |
| What Didn't Go Well | Pink sticky column |
| Actions / Try Next | Blue sticky column |
| Shout-outs | Violet sticky row |
| Actions Tracker | Table with Action, Owner, Due, Status |

### Solution Options Workshop

| Frame | Content |
|---|---|
| Header | Decision title, context, constraints |
| Options | Side-by-side frames per option, each with: description doc, pros (green stickies), cons (pink stickies) |
| Evaluation Criteria | Table with criteria and scoring per option |
| Recommendation | Decision sticky + rationale doc |

### Stakeholder Playback

| Frame | Content |
|---|---|
| Header | Playback title, date, audience |
| Summary | Key findings doc (doc_create with markdown) |
| Detailed Findings | Diagram + supporting stickies |
| Recommendations | Numbered decision stickies (blue) |
| Feedback Area | Empty brainstorm frame for attendee reactions |
| Sign-off | Table with Stakeholder, Status (Approved/Pending/Rejected), Comments |

---

## Facilitation Best Practices

1. **Leave space for humans**  -  don't fill every pixel; workshops need room for participant contribution
2. **Seed, don't solve**  -  provide 2-3 example stickies to prime thinking, not a complete answer
3. **Structure enables contribution**  -  clear prompts and labeled areas reduce confusion
4. **Q&A pairs for structured questions**  -  `black` prompt on top, `violet` space below for answers (standard pattern)
5. **RAID stickies are rectangles**  -  `w=154` for items, `w=212` for items needing more text, all `shape=rectangle`
6. **Open canvas for divergent thinking**  -  when brainstorming, give maximum space with minimal structure
7. **Use real clock times**  -  agenda timings must use actual meeting times (e.g. "11:00–11:15 AEST"), not relative offsets
8. **Actionable facilitation instructions**  -  never use vague labels like "DOT VOTE HERE". Always include clear participant instructions: what to do, how many, and the outcome
