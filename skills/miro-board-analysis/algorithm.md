# Board Construction Algorithm (MANDATORY  -  6 passes)

**This algorithm replaces ad-hoc board creation.** Before any `layout_create` call, the agent MUST complete passes 1–4 and show the working. Do not skip passes. Do not start writing DSL until Pass 5. The algorithm prevents the #1 recurring failure: elements that are too small, overlapping, or poorly spaced because the agent started building without planning dimensions.

> **Self-check (run this before proceeding):** Did you arrive here by reading `SKILL.md` first and following its routing table? If you opened this file directly from memory or a conversation summary  -  stop. Go read `SKILL.md`, confirm the board type, load the template, then come back. The orchestrator sets context that this file depends on (board type, template loaded, DSL spec cached). Skipping the orchestrator is how boards get built wrong.

**Prerequisites:** Before starting Pass 1, complete these preparation steps:

1. **Understand the task**  -  gather workshop purpose, desired outcomes, attendee count, activities planned, whether populating an existing board or building new
2. **`context_explore` (mandatory if a board URL exists)**  -  call `context_explore` on the target board **before** Pass 1. Paste the frame inventory into the plan file under `## Board inventory (context_explore)`. Do not guess what is on the board from memory or a prior chat.
3. **Get DSL spec**  -  call `layout_get_dsl` once to cache the DSL syntax for the conversation
4. **Read the active template**  -  the orchestrator (`SKILL.md`) tells you which template file to load. Read it now.
5. **Read the design system**  -  open `design-system.md` for dimensional values, colour system, and DSL patterns
6. **Style reference frames**  -  run `layout_read mode=structured` on at least two existing frames **from the inventory** (not random frames from memory)

---

## Pass 1: Structure Analysis

Determine what the board needs before thinking about coordinates.

1. **Board type:** workshop / analysis / debrief / status / retrospective / comparison / spike
2. **List all sections** in logical reading order (left to right):
   - For each section: what element types does it contain? (header + text, header + grey box + text, header + stickies, header + table, header + diagram, RAID columns, comparison columns)
3. **Cross-check for missing sections** against the active template's standard structure
4. **Determine reading order:** context/problem first → analysis/findings → options/solutions → RAID/risks → actions/next steps

Output: An ordered list like:
```
Section 1: "Problem & Scope"  -  header + grey_box + text (problem statement), header + grey_box + text (scope)
Section 2: "Key People & Dates"  -  header + grey_box + text, header + grey_box + text
Section 3: "Analysis Findings"  -  header + grey_box + text (3 sub-sections stacked)
Section 4: "Solution Options"  -  3x side-by-side comparison columns with headers + stickies
Section 5: "RAID"  -  4x bordered columns with stickies
Section 6: "Actions"  -  header + urgency-tiered stickies + header + text
```

---

## Pass 2: Layout Grid

For each section from Pass 1, assign a width and calculate the frame.

**Width assignment**  -  use these defaults, overridden by the active template if it specifies section widths:

| Section content | Width to assign |
|---|---|
| Single text column (problem, agenda, docs) | 874 (standard) |
| Double text column (stakeholders, scope with IN/OUT) | 1821 (double) |
| Wide text area (analysis with multiple sub-sections stacked) | 1821–2162 |
| Comparison columns (3 options side-by-side) | 3 × 874 + 2 × 45 = 2712 |
| RAID (4 bordered columns) | 4 × 756 + 3 × 50 = 3174 |
| Actions + next steps | 1004–1821 |
| Custom (diagrams, tables) | measure content, minimum 874 |

**Column count constraint:** If the layout produces more than 4 columns at the same horizontal level, regroup: stack related sections vertically within one column to reduce column count to 3-4. Example: Problem + Where We Are = 1 stacked column. Key People + Scope = 1 stacked column. This keeps frame width manageable and text readable at zoom-to-fit (see `design-system.md` Zoom-to-Fit Readability Check).

**Frame width calculation:**
```
frame_w = left_margin(200) + sum(section_widths) + (n_gaps × gap_size) + right_margin(200)
```
- Gap between adjacent sections in the same group: 100px
- Gap between major section groups: 200px
- **Minimum frame width: 5000px** (never smaller for analytical content)

**Frame height:** calculated in Pass 3.

---

## Pass 2b: Board placement (MANDATORY when adding a frame to an existing board)

**Do this before Pass 3 if the board already has content.** Skipping this pass caused Jul 2026 frame-on-frame overlap (new analysis frame landed on an existing release-planning cluster).

### Step 2b-0: Board inventory (context_explore)  -  write to plan first

**Tool call (required):**

```
CallMcpTool → plugin-miro-miro → context_explore
  miro_url: https://miro.com/app/board/{boardId}/
```

Copy the output into the plan file **before** placement math. Required section:

```markdown
## Board inventory (context_explore)

**Board URL:** https://miro.com/app/board/uXjVHdjL1c4=/
**Explored:** this session (before layout_create)

| Frame title | Widget ID | Board x | Board y | w | h | Relevant to this build? |
|---|---|---|---|---|---|---|
| MoSCoW 20 Jul | 3458764678608204701 | 286983 | 2359 | 5900 | 2400 | style reference |
| Release pillars | 3458764678608456596 | 286633 | 5621 | 5200 | 3629 | neighbour  -  overlap risk |
| Prior analysis frame | 3458764678609592937 | 287000 | 9800 | 5000 | 10800 | prior attempt  -  do not overlap |

**Frames in placement zone (~20k px of target):** Release pillars, MoSCoW 20 Jul, …
**Empty zone confirmed:** no / yes  -  if yes, cite inventory rows
```

If the board is genuinely empty, still run `context_explore` and record: `No frames returned  -  new/empty board confirmed.`

The pre-flight hook **denies** `layout_create` without this section.

### Step 2b-1: Discover neighbours

1. Use the **inventory table above**  -  do not skip straight to placement from memory.
2. Identify all frames within ~20,000px of the intended placement zone (from inventory x/y).
3. Run `layout_read mode=structured` on **each neighbour frame** listed as relevant.

### Step 2b-2: Compute occupied area (item-level, not frame box)

For every item in each neighbour frame, compute board-absolute edges:

```
item_board_y_top    = neighbour_frame_y + item_y - (item_h / 2)   # shapes; tables may differ  -  trust layout_read
item_board_y_bottom = neighbour_frame_y + item_y + (item_h / 2)
item_board_x_left   = neighbour_frame_x + item_x - (item_w / 2)
item_board_x_right  = neighbour_frame_x + item_x + (item_w / 2)
```

Record:

```
occupied_top    = min(all item tops)
occupied_bottom = max(all item bottoms)   # often BELOW frame_y + frame_h
occupied_left   = min(all item lefts)
occupied_right  = max(all item rights)
```

**Never use `neighbour_frame_y + neighbour_frame_h` alone.** Tables spill outside frames.

### Step 2b-3: Choose placement

| Priority | Strategy | Formula |
|---|---|---|
| **1 (default)** | New column to the right | `new_x = occupied_right + 500` ; align `new_y` with cluster top or user-specified anchor |
| **2** | Stack below (only if horizontal space exhausted) | `new_y = occupied_bottom + 2000` |
| **3** | User override | [BA name] says "below pillars" or "right of MoSCoW"  -  still verify gap ≥2000px / ≥500px |

Horizontal overlap check:

```
new_right = new_x + frame_w
FAIL if new_x < occupied_right + 500 AND new_right > occupied_left   # unless deliberate overlap requested
```

Vertical overlap check:

```
new_bottom = new_y + frame_h
FAIL if new_y < occupied_bottom + 2000 AND new_bottom > occupied_top
```

### Step 2b-4: Write to plan file (required section)

Every coordinate manifest MUST include:

```markdown
## Board placement

| Neighbour | Frame ID | Frame box (x, y, w, h) | Content bottom (board-absolute) | Content right |
|---|---|---|---|---|
| Release pillars | 3458764678608456596 | 286633, 5621, 5200, 3629 | **9250+ (items spill)** | 291833 |

**Proposed new frame:** x=293500, y=5621, w=5000, h=10800
**Gap:** 167px horizontal from content right (FAIL  -  need ≥500) → revised x=292400
**Placement gate:** PASS after revision
**Default used:** right column / below cluster / [BA name] override: …
```

**Do not proceed to Pass 5** until Placement gate = PASS.

---

## Pass 3: Content Sizing

For each section, measure the actual content and calculate element heights.

### Step 3a: Count content lines

For each text block, count:
- Bullet points (`<li>` items)
- Paragraph breaks (`<p>` tags)
- Line breaks (`<br/>` tags)
- Bold headings within text

### Step 3b: Estimate rendered height

Miro renders text wider than expected  -  bold text, HTML entities, and inline formatting consume more horizontal space, causing more line wraps than a simple character count suggests. **Always estimate generously.**

| Element | Height per unit | Line-wrap multiplier |
|---|---|---|
| Text line at size=30 (short, <40 chars) | ~46px | 1.0 |
| Text line at size=30 (medium, 40-80 chars at w=786) | ~46px | 1.5–2.0 (will wrap to 2-3 rendered lines) |
| Text line at size=30 (long, >80 chars at w=786) | ~46px | 2.0–3.0 (will wrap to 3+ rendered lines) |
| `<li>` item at size=36 | ~52px | same multiplier logic |
| `<li>` item at size=30 | ~46px | same multiplier logic |
| `<p>` break (empty paragraph) | ~38px | 1.0 (no content) |
| `<br/>` break | ~22px | 1.0 |
| Bold sub-heading in text | ~48px | 1.0 (usually short) |
| Empty line between sections | ~30px | 1.0 |

**Line-wrap estimation:** At size=30 with `w=786` and `align=left`, assume ~42 characters per rendered line (including bold/HTML overhead). Divide each text line's character count by 42, round up, then multiply by line height. This is the #1 source of sizing errors  -  agents consistently underestimate wrapping.

Formula: `estimated_text_height = sum(line_height × ceil(char_count / 42))` for each content line

**After summing**, apply the 15% safety margin when calculating grey box height (see Step 3c).

### Step 3c: Calculate grey box height
```
grey_box_h = (estimated_text_height × 1.15) + 65  (15px top padding + 50px bottom padding + 15% safety margin)
```

**NEVER normalise grey box heights across a row.** Each grey box is independently sized to its content via this formula. If two columns in the same row have different content lengths, their grey boxes will be different heights  -  uneven bottom edges are correct and expected. Normalising to the tallest box creates massive empty grey space (confirmed: Frame 8 V3 had 656-1184px of wasted grey in shorter sections).

### Step 3d: Calculate section total height
```
section_h = header_h(82) + header_to_greybox_gap(15) + grey_box_h
```

If a section has multiple stacked sub-sections (e.g. problem statement above scope):
```
section_h = sub_section_1_h + gap(80) + sub_section_2_h + gap(80) + ...
```

### Step 3e: Calculate frame height
```
frame_h = top_margin(200) + max(all_section_heights) + bottom_margin(200)
```
- **Minimum frame height: 2000px**

---

## Pass 4: Coordinate Calculation

With frame dimensions and section sizes known, compute exact x, y, w, h for every element.

**Horizontal positioning (x-axis):**
```
section_1_center_x = left_margin(200) + (section_1_width / 2)
section_2_center_x = section_1_center_x + (section_1_width / 2) + gap + (section_2_width / 2)
... and so on for each section
```

**Vertical positioning (y-axis) within each section:**

**CRITICAL:** SHAPE elements (grey boxes, headers) use **center-anchored y**. TEXT elements use **top-edge-anchored y**. These are different coordinate systems  -  never mix them up.

```
header_y = 146                                    # standard: near frame top (center of header shape)
grey_box_top = header_y + (header_h / 2) + 15     # 15px below header bottom edge
grey_box_y = grey_box_top + (grey_box_h / 2)       # centre of grey box (SHAPE = center-anchored)
text_y = grey_box_top + 15                          # TEXT = top-edge-anchored, so +15px = 15px margin from grey box top
text_w = section_width - 88                         # 44px padding each side
text_x = section_center_x                           # same centre as header
```

The old formula `text_y = grey_box_top + 15 + (est_text_h / 2)` was wrong  -  it assumed TEXT y was center-anchored like SHAPE y. TEXT y is the top edge. The correct formula is simply `text_y = grey_box_top + 15`.

**Centering validation (mandatory):**
```
content_span = rightmost_column_right_edge - leftmost_column_left_edge
left_margin_actual = leftmost_column_left_edge
right_margin_actual = frame_w - rightmost_column_right_edge
```
If `left_margin_actual` differs from `right_margin_actual` by more than 20px, adjust column positions to centre content in the frame.

**Output: A coordinate manifest.** Every element listed with its type and exact coordinates before any DSL is written:
```
FRAME: x=center, y=center, w=calculated, h=calculated
Section 1 header: x=637, y=146, w=874, h=82
Section 1 grey box: x=637, y=540, w=874, h=700
Section 1 text: x=637, y=410, w=786
Section 2 header: x=1556, y=146, w=874, h=82
...
```

---

## Plan Review Gate (MANDATORY)

**After completing Pass 4, STOP.** Write the coordinate manifest to a plan file:

```
_workstream/miro-plans/[board-name].plan.md
```

Present the plan to the user with:
- Board type and template used
- **`## Board inventory (context_explore)`**  -  frame table from the tool call (mandatory)
- **`## Board placement`**  -  Pass 2b neighbour collision math (mandatory)
- Frame dimensions
- Section list with assigned widths
- Full coordinate manifest
- Any flags (sections that may not fit, content that was truncated, assumptions made)

**Wait for user approval before proceeding to Pass 5.** If the user requests changes, update the manifest and re-present.

The pre-flight hook (`gate-miro-preflight.py`) **denies** `layout_create` unless the plan file contains **both** required sections. Chat memory does not count; the plan file does.

---

## Pass 5: DSL Generation

Convert the coordinate manifest into layout DSL text.

**Order of creation:**
1. Frame definition (always first)
2. Sections left to right: for each section, emit header shape → grey box shape → text element
3. Overlays: stickies, connectors, cards (after their parent sections)
4. Split into batches if total DSL exceeds ~40,000 chars (leave buffer below 50K limit). Use the frame's full Miro URL as `parent=` in subsequent batch calls.

**Style rules:** Apply all styles from `design-system.md`:
- Header shapes: `h=82, size=64` for ALL headers including section headers. Differentiate frame title from sections via width (full-width vs column-width) and color tier. Use the 5-tier colour system for color differentiation.
- Grey boxes: `type=rectangle fill=#e6e6e6` with content `""`. Content-fitted heights only  -  NEVER normalise.
- Body text: `size=30` minimum, `align=left`
- Omit `font=` parameter entirely for headers and body text
- Use the Dimensional Reference Table for all hard values
- Use the DSL Quick Reference snippets as copy-paste starting points

**Critical DSL rules:**
- `parent=` alias only works within the same `layout_create` call. If content exceeds 50K chars and requires multiple calls, use the frame's full Miro URL (returned from the first call) as `parent=` in subsequent calls  -  NOT the alias.
- Frame name ≠ title shape text. Frame name = short ID (e.g. "3. Solution Options"). Title shape = descriptive text.

---

## Pass 6: Post-build Verification

**Run the full `verification-checklist.md` procedure.** This pass is not optional  -  the user has explicitly flagged skipped verification as a recurring problem.

Summary of what verification covers (see `verification-checklist.md` for the full procedure):
1. Run `layout_read mode=full` on the new frame
2. Overlap check for all items
3. Text containment check for all text + grey box pairs
4. Centering check
5. Bounds check
6. Spacing check
7. Width check
8. Fix any issues before reporting to user

---

## Workflow: Populating an Existing Frame

When the task is to populate an existing frame (not build from scratch), use this adapted workflow:

### Step 1: Read the current state
```
CallMcpTool → toolName: "layout_read", miro_url: "{frame_url}", mode: "full"
```

### Step 2: Identify what to populate

Look for:
- Empty frames with only titles
- Placeholder text ("Add your ideas here", "[TBD]", etc.)
- Prompt stickies without responses
- Empty table rows
- Sections that match the workshop agenda but lack content

### Step 3: Populate using the right tool

| What to add | Tool | Approach |
|---|---|---|
| Stickies with analysis content | `layout_create` (targeting frame) | Position relative to frame top-left |
| Replace placeholder text | `layout_update` | Find old DSL text, replace with populated content |
| Fill a table | `table_sync_rows` | Add rows with project-specific data |
| Update a document | `doc_update` | Find-and-replace on markdown content |
| Add a diagram | `diagram_create` (targeting frame) | Place at specific coordinates within frame |

### Step 4: Preserve existing content

**Never delete or overwrite existing participant contributions.** When populating:
- Place new items in empty areas only
- Use different colors to distinguish facilitator-added content from participant content
- Add items below or beside existing content, not on top of it

---

## Workflow: Reading and Synthesizing Board Content

When the task is to extract content from a board (not build):

### Step 1: Explore the board
```
CallMcpTool → toolName: "context_explore", miro_url: "{board_url}"
```
Returns all frames, docs, tables, diagrams with URLs and titles.

### Step 2: Get detailed content

For specific items:
```
CallMcpTool → toolName: "context_get", miro_url: "{item_url_with_moveToWidget}"
```

For layout-level detail (positions, colors, types):
```
CallMcpTool → toolName: "layout_read", miro_url: "{frame_url}", mode: "full"
```

### Step 3: Read tables
```
CallMcpTool → toolName: "table_list_rows", miro_url: "{table_url}"
```

### Step 4: Read sticky notes
```
CallMcpTool → toolName: "board_list_items", miro_url: "{frame_url}", limit: 100, item_type: "sticky_note"
```
