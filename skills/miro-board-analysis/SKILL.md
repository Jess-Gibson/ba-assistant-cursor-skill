---
name: miro-board-analysis
description: "Collaborative Miro board facilitator  -  builds workshop boards, populates frames with structured content (sticky notes, diagrams, tables, documents, shapes), creates brainstorming spaces, and reads board context. Use when the user provides a Miro board URL, asks to create workshop content, populate a template, build a facilitation board, or extract content from a Miro board."
---

# Miro Board Workshop Facilitator

A collaborative workspace skill for building, populating, and reading Miro boards. This file is the **orchestrator**  -  it routes to the right template, algorithm, and design system files. Do not build boards from this file alone.

**Critical principle:** The board MUST read sequentially against the goal/agenda or logical steps towards outcomes. Sections are laid out left-to-right in the order they will be addressed during the session. A participant scanning left-to-right should experience the board in the same order as the meeting itself.

---

## Modular Architecture

| File | Purpose | When to read |
|---|---|---|
| `SKILL.md` (this file) | Orchestrator: routing, MCP setup, pre-flight | Always  -  first file loaded |
| `algorithm.md` | 6-pass board construction + populate/read workflows | Before any board creation |
| `design-system.md` | All pixel values, colours, fonts, DSL snippets | During algorithm Pass 5 (DSL generation) |
| `verification-checklist.md` | Post-build checks (Pass 6 detail) | After every `layout_create` call |
| `recurring-mistakes.md` | Living error log with corrective rules | When debugging or after a failed build |
| `templates/analysis-board.md` | Analysis / status board sections and content rules | When board type = analysis |
| `templates/workshop-board.md` | Workshop patterns 1-10 + facilitation templates | When board type = workshop / kickoff / retro |
| `templates/debrief-board.md` | Meeting debrief + multi-table matrix patterns | When board type = debrief |
| `templates/comparison-board.md` | Options comparison layout + evaluation criteria | When board type = comparison |
| `templates/kickoff-board-template.md` | Verified kickoff DSL reference (D2 template) | When building a kickoff board |
| `templates/spike-card-template.md` | Spike card DSL reference | When building spike cards |

---

## Board Type Routing

Classify the task, then load the matching template:

| Board type | Signals | Template to load |
|---|---|---|
| **Workshop / Kickoff** | "build a workshop", "kickoff board", "facilitation", "retro" | `templates/workshop-board.md` |
| **Analysis / Status** | "analysis board", "status board", "initiative overview", RAID + decisions + options | `templates/analysis-board.md` |
| **Debrief** | "debrief board", "meeting outcomes on the board", "populate the debrief" | `templates/debrief-board.md` |
| **Comparison** | "compare options", "solution options board", "trade-off board" | `templates/comparison-board.md` |
| **Spike cards** | "spike cards", "spike board" | `templates/spike-card-template.md` |
| **Read / Extract** | "read the board", "what's on the board", "summarise the board" | No template  -  use read workflow in `algorithm.md` |

**After loading the template**, follow the execution flow below.

---

## Execution Flow

```
0. context_explore on target board → paste inventory into plan
1. Pre-flight checks (this file)
2. Load template for board type
3. Follow algorithm.md passes 1-4 → produce coordinate plan (inventory + placement sections)
4. STOP  -  present plan to user for review
5. On approval → algorithm.md Pass 5 (DSL generation, styles from design-system.md)
6. After creation → verification-checklist.md (NEVER SKIP  -  Step 0 re-runs context_explore if board changed)
7. Report to user
```

### Plan Review Gate

After algorithm Pass 4, write the coordinate manifest to:
```
_workstream/miro-plans/[board-name].plan.md
```
Present to the user with frame dimensions, section list, full coordinate manifest, and these **hook-required plan sections**:

1. **`## Board inventory (context_explore)`**  -  output of `context_explore` pasted as a frame table (Pass 2b-0)
2. **`## Board placement`**  -  neighbour collision math, proposed x/y, gap verification (Pass 2b)

**Wait for approval before Pass 5.**

The pre-flight hook **denies** `layout_create` if either section is missing. Chat memory does not count; the plan file does.

---

## STOP Gates (non-negotiable)

These checks exist because agents  -  including the one that wrote these files  -  have bypassed the algorithm by "knowing" the content from memory or prior context. Memory is not a substitute for following the process.

**Before generating ANY layout DSL, verify ALL of these are true:**

- [ ] You have read `algorithm.md` in THIS conversation (not a prior one)
- [ ] You have read the active template file (e.g. `templates/analysis-board.md`)
- [ ] You have read `design-system.md`
- [ ] You have called **`context_explore`** on the target board and pasted the frame inventory into the plan (`## Board inventory (context_explore)`)
- [ ] You have completed Passes 1-4 and produced a coordinate manifest (including `## Board placement`)
- [ ] The coordinate manifest has been presented to the user (or the user said "don't ask, just build")
- [ ] You are working from the manifest, not from memory

**If any box is unchecked: STOP. Go back to the first unchecked step.**

This applies even if:
- You authored these files earlier in this conversation
- You "already know" the design system values
- The user said "go ahead and make the fixes" or "don't stop"
- You're resuming from a previous conversation where you read them

The algorithm exists to produce better boards. Skipping it produces worse boards. This has been proven empirically.

---

## Pre-Creation Checklist (MANDATORY)

Run through before any `layout_create`, `table_create`, or content creation call. Skipping this is the #1 cause of rework.

### 1. Tool selection (decide once, don't switch mid-task)

- [ ] **Styled content** (shapes, headers, text panels, stickies) → `layout_create` DSL
- [ ] **Tables** → `table_create` + `table_sync_rows`
- [ ] **Diagrams** → `diagram_create`
- [ ] **Rich text documents** (standalone, not matching board styling) → `doc_create`
- [ ] **NEVER** use `user-miro-desktop` `create_shape`/`create_text` for styled content  -  they silently drop styling params

### 2. Discover existing board (`context_explore` FIRST, then `layout_read`)

- [ ] Call **`context_explore`** on the board URL  -  paste frame list into plan (`## Board inventory (context_explore)`). **Hook blocks build without this.**
- [ ] Run `layout_read mode=structured` on at least 2 frames **from that inventory** (style reference + nearest neighbour)
- [ ] Note: header shape types, fill colours, font sizes, grey box patterns
- [ ] Note: x/y positioning patterns, spacing between sections
- [ ] Match these exactly in your new content

### 3. Shape type rules

- [ ] **Headers** (coloured) → `type=round_rectangle`
- [ ] **Grey backdrop boxes** (`fill=#e6e6e6`) → `type=rectangle` (user manually adjusts radius)
- [ ] **NEVER** use `round_rectangle` for grey backdrops  -  default 50px radius looks wrong

### 4. Text positioning

- [ ] TEXT inside grey boxes is a **separate overlaid item**, not the grey box's content string
- [ ] Grey box content string stays `""`
- [ ] **SHAPE y = center-anchored. TEXT y = top-edge-anchored.** These are different coordinate systems.
- [ ] TEXT `y` formula: `text_y = (grey_box_y - grey_box_h/2) + 15`  -  grey box top edge + 15px margin
- [ ] **NEVER** set `text_y = grey_box_y` (this places text top at the grey box center  -  looks wrong)
- [ ] Full positioning rules → `design-system.md` CRITICAL POSITIONING RULES

### 5. Layout pattern

- [ ] **Max 4 content columns per horizontal row**  -  if content needs 5+, stack related sections vertically in one column (see `design-system.md` Column Count Guidance)
- [ ] **NEVER normalise grey box heights**  -  content-fit each independently. Uneven bottom edges are correct.
- [ ] **ALL headers h=82, size=64**  -  differentiate frame title from sections via width (full-width vs column-width) and color tier, not font size
- [ ] **Every table has a coloured header shape above it**  -  no bare tables
- [ ] Frame size tight to content, not oversized
- [ ] **Never use full-width text boxes** unless content is a diagram, table, or flow
- [ ] **Prefer text wrap**  -  narrower boxes that wrap naturally are better than wide short-line boxes
- [ ] **Zoom-to-fit check**  -  if `30 × (1920 / frame_w) < 10`, frame is too wide. Reduce columns.

### 6. Title bar  -  no duplication

- [ ] Frame name = short identifier (e.g. "3. Solution Options")
- [ ] Title shape = descriptive name (e.g. "Solution Options (23 Jun Reframe)")
- [ ] These MUST be different  -  Miro renders both visibly

### 7. Post-creation verification

- [ ] **Run `verification-checklist.md` after every `layout_create`**  -  this is not optional
- [ ] Fix any issues before telling the user the board is ready

---

## MCP Servers

Three Miro MCP servers may be available. Check what's listed before calling:

| Server identifier | Tool set | Notes |
|---|---|---|
| `plugin-miro-miro` | Full (35 tools: layout DSL, tables, diagrams, docs, images, comments, context) | **Preferred.** May require re-auth  -  if "Unauthorized", ask user to re-auth in Cursor settings. |
| `user-miro-mcp` | Full (same as above) | Alternate full server. Same re-auth behaviour. |
| `user-miro-desktop` | Basic (9 tools: create_frame, create_shape, create_text, create_sticky_note, create_connector, read_board_items, delete_item, upload_image, update_sticky_note) | **Always available fallback.** No DSL, no tables, no diagrams, no layout_read. One API call per item. Uses `boardId` not `miro_url`. Uses `parentId` not `parent=` DSL alias. |

### Auth Troubleshooting

1. Try `plugin-miro-miro` first with any tool (e.g. `user_who_am_i`).
2. If "Unauthorized" or server not listed: ask user to re-auth the Miro plugin in Cursor.
3. After re-auth, the server may re-appear or may only work via `user-miro-desktop`.
4. If only `user-miro-desktop` is available: use it. One call per item is slower but functional. Key differences:
   - Uses `boardId` param (e.g. `"uXjVHDIdgWg="`) not `miro_url`
   - Uses `parentId` (frame ID string) not `parent=` DSL alias
   - `create_shape` supports `shape`, `content`, `fillColor`, `borderColor`, `x`, `y`, `width`, `height`, `parentId`
   - `create_text` supports `content` (HTML), `x`, `y`, `width`, `fontSize`, `parentId`
   - `create_sticky_note` supports `content` (HTML), `fillColor` (limited palette: light_yellow, light_green, light_blue, light_pink, violet, dark_blue, gray, black), `x`, `y`, `parentId`
   - No `layout_create`, `layout_read`, `table_create`, `diagram_create`, `doc_create`
   - Coordinates are board-absolute when no parentId; frame-relative when parentId is set

### Fallback Strategy (user-miro-desktop only)

When only the basic 9-tool set is available:
1. Create frames first (`create_frame`)  -  note the returned IDs.
2. Build section headers as `create_shape` with `shape: "round_rectangle"` and `fillColor` matching the brand palette.
3. Add body text as `create_text` with HTML formatting.
4. Add RAID/brainstorm items as `create_sticky_note` with semantic colours.
5. Batch parallel calls where possible (multiple independent items).
6. Cannot create tables  -  use text with formatted HTML or suggest user creates tables manually.
7. Cannot verify layout post-creation  -  note this to user and suggest manual adjustment.

---

## URL Parsing

```
https://miro.com/app/board/{boardId}/                         → Board-level
https://miro.com/app/board/{boardId}/?moveToWidget={itemId}   → Specific frame/item
https://miro.com/app/board/{boardId}/?focusWidget={itemId}    → Specific frame/item
```

When a URL targets a frame via `moveToWidget`, all items created are placed INSIDE that frame with coordinates relative to the frame's top-left corner (0,0).

---

## Quick Decision: Which Tool to Use

| I want to... | Use |
|---|---|
| Build a complete board section with mixed content | `layout_get_dsl` → `layout_create` |
| Add a single document with rich formatting | `doc_create` |
| Create a decision/tracking table | `table_create` + `table_sync_rows` |
| Add a process flow or architecture diagram | `diagram_get_dsl` → `diagram_create` |
| Show code in a workshop | `code_widget_create` |
| Place a public image | `image_create` with `image_url` |
| Upload a local screenshot | `image_get_upload_url` → shell PUT → `image_create` |
| Read what's on a board | `context_explore` → `context_get` or `layout_read` |
| Modify existing board content | `layout_read` → `layout_update` |
| Update specific table rows | `table_list_rows` → `table_sync_rows` with `rowId` |
| Edit a document | `doc_get` → `doc_update` |
| Find a board by name | `board_search_boards` |
| Leave a comment or feedback on an item | `comment_create` |

---

## Limitations

| Limitation | Workaround |
|---|---|
| No native connectors in layout DSL (between arbitrary items) | Use `diagram_create` for connected flows; or shapes with arrows as labels |
| Can't style individual text within a sticky (bold/italic) | Use multiple stickies or a `doc_create` for rich text |
| Sticky notes have limited text length | Use docs for longer content; stickies for 2-3 lines max |
| Can't move existing items (no position update in layout_update) | Use `layout_update` to delete + recreate at new position |
| Tables can't be visually customized beyond column types | Combine table_create for data with layout stickies for visual annotations |
| Max 50,000 chars per layout_create call | Split into multiple calls; create frames first, then populate one-by-one |
| `parent=` alias only works within the same `layout_create` call | If content exceeds 50K chars, use the frame's full Miro URL as `parent=` in subsequent calls, NOT the alias |
| Image upload requires a two-step flow | Prefer `image_url` for public images; use the upload flow only for local files |

---

## Integration with BA Assistant

This skill complements `ba-workshop-design` and `ba-assistant`. When a workshop agenda is designed:

1. **BA Workshop Design** produces the agenda, activities, attendees, and outcomes
2. **This skill** builds the physical Miro board to match that agenda
3. **During the workshop**, the facilitator uses the board with participants
4. **After the workshop**, this skill can read the board content and route outputs to:
   - `ba-meeting-debrief` for decisions and actions
   - `ba-risk-and-tracker` for new risks/assumptions
   - `ba-requirements-interrogator` for new requirements surfaced

### Handoff from Workshop Design

When `ba-workshop-design` produces an agenda, translate each activity into a board element:

| Activity type | Board element |
|---|---|
| Presentation / context setting | Content panel (header + grey box + text) |
| Brainstorm | Large frame with prompt sticky + empty space |
| Affinity grouping | Pre-labeled column frames with header stickies |
| Dot voting | Options as shapes with empty vote areas below |
| Discussion | Frame with discussion prompts as stickies |
| Decision | Table with options, criteria, recommendation |
| Action planning | `table_create` with Action, Owner, Due, Status |
| Retrospective | Multi-column sticky layout (went well / improve / try) |
