# Miro Visual Design System

Single source of truth for all pixel values, colours, fonts, patterns, and DSL snippets. Referenced by `algorithm.md` (Pass 5) and all templates.

Based on two established workshop board templates from prior kickoff and discovery-day sessions.

---

## Coordinate System

- **Board-absolute**: Center is (0, 0). Positive X → right. Positive Y → down.
- **Frame-relative**: When targeting a frame via `moveToWidget`, coordinates are relative to the **frame's top-left corner** (0, 0). Items must fit within the frame's width and height.

### Spacing Guidelines

| Content type | X spacing | Y spacing | Recommended size |
|---|---|---|---|
| Sticky notes (Q&A pair) | 453 (column-to-column) | 180 (Q to A), 470 (pair-to-pair) | w=365, rectangle |
| Sticky notes (RAID / brainstorm) | 200-250 (free scatter) | 200-250 | w=154 (small square), w=212 (medium) |
| Sticky notes (stakeholder names) | 90 (tight row) | 90 | w=80, square |
| Sticky notes (timeline milestones) | variable along x-axis | — | w=119, square |
| Content panel (header + body) | — | 130-170 (header to first zone) | w=874 (standard), w=1004 (actions) |
| RAID columns | 797 (center-to-center) | — | w=756, h=1675 |
| Sections (horizontal) | ~950 (between major sections) | — | Varies by content |
| Documents | 900 | — | 800 x auto |
| Tables | 1500 | — | auto |
| Diagrams | 2000-3000 | — | auto |

---

## Dimensional Reference Table

Hard pixel values derived from a verified reference frame (D2 Kickoff template). All dimensions in pixels.

### Element Dimensions

| Element | Width | Height | Font size | Notes |
|---|---|---|---|---|
| Standard column | 874 | varies | — | Single section width. All elements in the column share this width. |
| Double column | 1821 | varies | — | 2x standard + 1 gap. For wider content areas. |
| Header bar (standard) | =column_w | 82 | 64 | `type=round_rectangle`. Most common header. |
| Header bar (wide banner) | custom | 119 | 64 | Spans multiple columns. For section group headers. |
| Header bar (emphasis) | custom | 157 | 100 | Large callout style (e.g. "Questions"). Rare. |
| Sub-header label | 446 | 97 | 48 | "IN", "OUT", "Future scope", "WHAT'S BEEN BUILT" |
| Grey content box | =column_w | calculated | — | `type=rectangle fill=#e6e6e6`. Content always `""`. Height from algorithm Pass 3. |
| Body text | column_w - 88 | auto | 30–36 | `align=left`. 44px padding each side within grey box. |
| Description/subtitle text | column_w - 88 | auto | 24 | Accent text, fine print. |
| Accent/link text | varies | auto | 19–39 | Purple labels, doc references. |
| RAID column container | 756 | 1675 | — | `fill=#ffffff fill_opacity=0.0 border_color=#abacf1 border_width=8.0` |
| RAID column title | auto | auto | 80 | `color=#7b14ef` |
| RAID column description | auto | auto | 24 | `color=#8241aa` |
| Sticky (Q&A grid) | 365 | auto | — | `shape=rectangle` |
| Sticky (RAID) | 264 | auto | — | `shape=rectangle` |
| Card (stakeholder) | 283 | 47 | — | Themed by role |

### Spacing Constants

| Spacing | Value | Notes |
|---|---|---|
| Column gap (adjacent sections) | 45 | Between edge of one column and edge of next |
| Section group gap | 100–200 | Between major section groups |
| Frame top margin | 200 | Frame top edge to first header centre y=146 means ~105px from top to header top |
| Frame bottom margin | 200 | Last element bottom edge to frame bottom |
| Frame left/right margin | 200 | Content start/end to frame edges |
| Header to grey box gap | 15 | From header bottom edge to grey box top edge |
| Grey box top padding | 15 | From grey box top edge to text start (empirically calibrated) |
| Grey box bottom padding | 50 | From text end to grey box bottom edge |
| Grey box side padding | 44 | Each side (column_w - text_w = 88, split evenly) |
| Vertical gap between stacked sub-sections | 80 | Between one sub-section bottom and next sub-section header top |
| RAID column spacing | ~800 center-to-center | Between RAID column centres |
| Sticky vertical spacing (Q&A pair) | 180 | Question to answer |
| Sticky vertical spacing (pair to pair) | 470 | Between Q&A pair groups |
| Sticky horizontal spacing | 453 | Column to column in Q&A grids |

### Key Ratios

| Ratio | Value | Use |
|---|---|---|
| Header height : font size | 1.28:1 | h=82 for size=64. Scale proportionally for other sizes. |
| Body text width : column width | 0.90:1 | text_w = column_w × 0.9 (rounded to column_w - 88) |
| Header width : grey box width | 1:1 | Always match. Misalignment looks broken. |
| Body font : header font | 0.47:1 | size=30 body with size=64 headers. ALL headers use size=64. |

### Minimum Thresholds (hard limits — never go below)

| Property | Minimum | What happens if violated |
|---|---|---|
| Frame width | 5000px | Content too cramped, text unreadable |
| Frame height | 2000px | Sections cut off at bottom |
| Header font size | 64 | Headers become invisible at board zoom level. Frame 1 (gold standard) uses 64 for all headers. |
| Body text font size | 30 | Body text unreadable. Frame 1 uses 30. Never use 26-28 even if a reference frame does. |
| Grey box per section | 1 per text block | Text floats without visual container |

---

## Shape Headers — 5 Tiers

| Tier | Fill | Text colour | Font size | Use | Example labels |
|---|---|---|---|---|---|
| **Primary** (strong) | `#7b14ef` (deep purple) | `#ffffff` (white) | 64-72 | Main section headers, key structural areas | "Problem statement", "High level scope", "High level service design", "Actions & Owners" |
| **Secondary** (medium) | `#c497fe` (light purple) | `#7b14ef` (purple) | 48-100 | Sub-headers, categories, labeled zones, clickable callouts | "Questions" (size 100), "IN", "OUT", "Future scope", "Current state", "RAID" (size 64), "Things worth remembering" |
| **Tertiary** (accent/data) | `#fff854` (bright yellow) | `#394666` (dark blue-grey) | 59-64 | Attention-drawing headers, data/metric sections | "Agenda", "Success metrics", "High level requirements", "Stakeholders", "Next steps", "CXNPL - SLAs" |
| **Dark** (structural) | `#232428` (near-black) | `#ffffff` (white) | 64 | Structural/foundational sections, action-oriented | "Docs & references", "Draft high level plan", "Actions & follow ups" |
| **Black** (alternate) | `#000000` (black) | `#ffffff` (white) | 59 | Supporting / secondary structural | "Supporting data" |

### Shape DSL Properties (Consistent Across All Headers)

```
type=round_rectangle fill_opacity=1.0 border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0
```

### Font Handling (CRITICAL — updated Jun 2026)

- **Do NOT specify `font=` for headers or body text.** Omit the parameter entirely. Miro uses its built-in default sans-serif, which is what all reference boards use.
- The Miro API reports this default font as `font=unknown` on read-back. This is normal — it means the font was set via Miro's UI, not the API.
- Only specify an explicit font (`font=open_sans`, `font=noto_sans`, `font=plex_mono`) when deliberately choosing a non-default font (e.g. code blocks, monospace data).
- **Never use `font=plex_sans` or `font=arial` for headers** — these render differently from Miro's default and look wrong.

### Height Patterns (from reference frame)

- Standard header: `h=82` (single line title at size=64)
- Wide banner header: `h=119` (section group header at size=64)
- Emphasis header: `h=157` (large callout at size=100, e.g. "Questions")
- Sub-label ("IN"/"OUT"): `h=97` (at size=48)

### Header Hierarchy

All headers use `h=82, size=64`. Visual hierarchy comes from **width** and **color tier**, not font size.

- **Frame title** (main): full-width (`w = frame content width`), `h=82, size=64` — one per frame at the top. Spans all columns.
- **Section headers** (within frame): column-width (`w = column_w`, typically 874), `h=82, size=64` — one per content column/section. Differentiate from the title via narrower width and color tier (Primary, Secondary, Tertiary, Dark, Black).
- **Sub-labels** (status/accent): `h=36, size=22` — below section headers (e.g. "LEANING — Effort: Low")

Frame 1 (gold-standard reference) uses `h=82, size=64` for ALL headers — Problem Statement, Scope, Key People, Key Dates, Decisions — and distinguishes structure through width (2100px title vs 874px sections) and color tier.

### Standard Header DSL Template (omit font to get Miro default)

```
id SHAPE parent=frameRef x=center_x y=146 w=874 h=82 type=round_rectangle fill=#7b14ef fill_opacity=1.0 color=#ffffff size=64 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "Section Title"
```

---

## Content Panel Pattern (Card Structure) — CORRECTED May 2026

Every section follows the same visual structure — a header shape with a grey backdrop box behind body text:

```
┌─────────────────────────────┐  ← Header shape (coloured, round_rectangle, h=82)
│                             │     center y ≈ 146
├─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─┤  ← ~15px gap
│  ┌───────────────────────┐  │  ← Grey backdrop box (rectangle, fill=#e6e6e6)
│  │ [TEXT element]         │  │  ← Text positioned near TOP of grey box
│  │                       │  │     text_y = grey_box_top + 15 (TEXT y = top edge)
│  │                       │  │     NOT grey_box_y (which is the center)
│  └───────────────────────┘  │
└─────────────────────────────┘
```

### CRITICAL POSITIONING RULES

**Coordinate system difference (root cause of all text-in-box alignment bugs):**
- `SHAPE` elements (grey boxes, headers): `y` is the **vertical center** of the shape. Top edge = `y - h/2`.
- `TEXT` elements: `y` is the **top edge** of the text block. Text renders downward from `y`.

This means: if you set `text_y = grey_box_y`, the text top edge lands at the grey box's vertical midpoint — creating massive blank space above the text. This is wrong.

**The formula:**
```
text_y = grey_box_top + 15
       = (grey_box_y - grey_box_h / 2) + 15
```

The 15px offset is empirically calibrated — it gives a clean top margin without visible whitespace. Do NOT use 0 (text touches the edge) or 30+ (too much gap).

1. **Always calculate `text_y` from the grey box top edge + 15px.** Never copy the grey box's `y` directly. Never estimate. Always compute: `text_y = grey_box_y - grey_box_h/2 + 15`.

2. **NEVER set text_y = grey_box_y.** This is the most common mistake. It places the text top at the grey box center, which looks wrong.

3. **Grey box height should match actual content.** Do not blindly copy template grey box dimensions — size the box to fit the real text content with appropriate padding (15px top + 50px bottom + 15% safety margin on text height).

4. **Section widths should be adjusted for content density.** A section with a table needs different width than one with short bullets. Resize proportionally.

5. **Consistency check:** After calculating all text positions, verify that every `text_y` in a given row shares the same offset pattern from its grey box top. Inconsistent offsets produce the "wildly inconsistent text alignment" problem.

### Grey Box Properties

- `type=rectangle fill=#e6e6e6 fill_opacity=1.0` — always use `rectangle` for grey backdrop boxes. Miro's DSL cannot set a custom corner radius; `round_rectangle` defaults to ~50px which looks too round. Use `rectangle` (0px) and the user will manually adjust to 20px radius if desired.
- `border_color=#ffffff border_style=normal border_width=1.0`
- Omit `font=` — grey boxes have no visible text (content is always `""`)
- Content always empty string `""`
- Width: same as the header above it (typically 874 for standard columns)
- **Grey boxes must NEVER overlap** — verify `y_range = [y - h/2, y + h/2]` for all boxes in the same x-column do not intersect
- **Grey box heights are ALWAYS content-fitted.** NEVER normalise grey boxes to a uniform height across a row. If sections in the same row have different content lengths, their grey boxes will be different heights. Uneven bottom edges are correct and expected. Normalisation creates the "too much grey space" problem — confirmed empirically in Frame 8 V3 where 656-1184px of empty grey appeared in shorter sections.

**Grey Box DSL Template:**
```
id SHAPE parent=frameRef x=center_x y=grey_box_y w=874 h=calculated type=rectangle fill=#e6e6e6 fill_opacity=1.0 color=#1a1a1a size=25 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 ""
```

### Grey Card Shape Type — CRITICAL (updated May 2026)

- **Always use `type=rectangle` for grey backdrop boxes.** The Miro DSL cannot set a custom corner radius. `round_rectangle` uses Miro's default radius (~50px) which looks too round. `rectangle` (0px radius) is the better default — the user will manually adjust to 20px radius after creation.
- This applies to ALL grey backdrop shapes (`fill=#e6e6e6`), not just debrief content.
- For **header shapes** (coloured, like Primary/Secondary/Tertiary/Dark): continue using `round_rectangle` — the default radius looks acceptable on smaller header shapes and matches the established board style.
- **Summary:** Headers = `round_rectangle`. Grey backdrops = `rectangle`.

### TEXT Positioning Inside Grey Cards (CRITICAL — #1 recurring issue)

- TEXT is a **separate item overlaid on the grey card** — it is NOT the grey card's content string (which stays `""`)
- **TEXT `y` is the TOP EDGE of the text block** (not the center). SHAPE `y` is the CENTER. These are different coordinate systems.
- **Formula:** `text_y = grey_card_top + 15 = (grey_card_y - grey_card_h/2) + 15`. If the grey card is at y=464, h=525 → top = 464-262 = 202 → text_y = 202+15 = 217. The 15px value is empirically calibrated from user-approved layouts.
- **NEVER set `text_y = grey_card_y`** — this places the text top at the grey card's vertical midpoint, creating massive blank space above the text.
- TEXT should use `align=left` for horizontal alignment — NEVER `align=center` for body text inside grey cards.

### Content Panel Sizing Rules (prevents text-outside-card)

TEXT items auto-height in Miro — you cannot set their height. This means you MUST estimate the rendered height and size the grey card accordingly. Getting this wrong is the #1 recurring layout issue.

**Estimating TEXT rendered height (use algorithm Pass 3):**

| Content element | Height at size=30 | Height at size=36 | Notes |
|---|---|---|---|
| Single rendered line | ~46px | ~52px | Per RENDERED line after wrapping. At w=786 assume ~42 chars/line. |
| `<li>` bullet item | ~46px | ~52px | Per rendered line. Bold items wrap sooner. |
| `<p>` paragraph break | ~38px | ~42px | Empty paragraph spacer |
| `<br/>` line break | ~22px | ~25px | Inline break |
| Bold sub-heading in text | ~48px | ~54px | Usually short, 1 line |
| Empty line between sections | ~30px | ~35px | Visual separator |

Bold text (`<strong>`) does not change height. Add 65px total padding (15 top + 50 bottom) plus a 15% safety margin on text height.

### Content Panel Coordinate Formulas (matches algorithm Pass 4)

```
estimated_text_height = sum(all_line_heights)  -- from table above
grey_card_h = (estimated_text_height × 1.15) + 65  -- 15% safety margin + 15px top + 50px bottom
grey_card_top = header_y + (header_h / 2) + 15  -- 15px below header bottom edge
grey_card_y = grey_card_top + (grey_card_h / 2) -- centre of grey box (SHAPE = center-anchored)
text_y = grey_card_top + 15                      -- TEXT y = top edge, +15px margin from grey box top
text_w = column_w - 88                          -- 44px padding each side
```

### Complete Content Panel DSL Template (standard column)

```
# Header (Primary tier)
h1 SHAPE parent=frameRef x=637 y=146 w=874 h=82 type=round_rectangle fill=#7b14ef fill_opacity=1.0 color=#ffffff size=64 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "Section Title"

# Grey backdrop (sized to content — example: 400px content = (400×1.15)+65 = 525px box)
# grey_box_top = 146 + 41 + 15 = 202. grey_box_y = 202 + 262 = 464.
g1 SHAPE parent=frameRef x=637 y=464 w=874 h=525 type=rectangle fill=#e6e6e6 fill_opacity=1.0 color=#1a1a1a size=25 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 ""

# Body text (TEXT y = top edge, 15px below grey box top — empirically calibrated)
# text_y = grey_card_top + 15 = 202 + 15 = 217
t1 TEXT parent=frameRef x=637 y=217 w=786 color=#1a1a1a fill=#ffffff fill_opacity=0.0 size=30 align=left "<p>Body content here</p>"
```

### Validation Check (run after layout_read)

For each TEXT + grey card pair, verify:
- `text_top > grey_card_top` (text starts inside card)
- `text_bottom < grey_card_bottom` (text ends inside card)

If either fails, adjust the grey card y and h to contain the text.

---

## Layout Rules

### Vertical Section Spacing

- Gap between one section's bottom and the next header's top: ~100-120px (header height ~82px + 20-40px margin)
- Do NOT leave large empty gaps between sections — tighten vertically
- After placing all sections, check for wasted vertical space and compress

### Horizontal Layout Density

- Don't spread sections across the full frame width — let content density determine spacing
- Reference/context material (agenda, docs, stakeholders, session context) goes in the leftmost ~2100px
- Activity sections (facilitation activities in agenda order) fill the middle
- Wrap/actions/next steps go on the right
- Typical effective width for a 16000px frame is ~13000-14000px (leave breathing room on right)

### Width Discipline — prefer text wrap over wide boxes

- **NEVER use full-width sections for singular text boxes.** Full-width (matching frame or 3-column span) is only appropriate for diagrams, tables, images, flows, or multi-column content that genuinely needs the space.
- **Prefer narrower text boxes that let text wrap.** A 1200-1500px text box at size=28 is usually plenty. Don't stretch to 2800px just because the frame is wide.
- If a section has short paragraph content (6-10 lines), it should be column-width (900-1500px), not frame-width.

### Side-by-side Sections (multi-column layout)

When a frame has N distinct sections with moderate content, lay them out as **N horizontal columns** rather than stacking vertically or mixing stacked/side-by-side. Match the number of sections to the number of columns:
- 2 sections → 2 columns
- 3 sections → 3 columns (w=900 each with 60px gaps in a 3200px frame)
- 4+ sections → consider 2 rows of 2, or group related sections

Layout formula for 2-column bottom sections in a 3200px frame:
```
col_gap = 150          # gap between the two columns
total_content_w = frame_w - left_margin(190) - right_margin(190) - col_gap
left_col_w = total_content_w × 0.55   # slightly wider for the primary section
right_col_w = total_content_w × 0.45
left_col_x = left_margin + left_col_w / 2
right_col_x = frame_w - right_margin - right_col_w / 2
```
Both columns share the same y position (headers aligned horizontally).

### Column Count Guidance

Prefer **3-4 content columns max** per horizontal row. If content requires 5+ columns, group related sections vertically within a single column (e.g. Problem + Where We Are stacked, Key People + Scope stacked). This reduces frame width and keeps text readable at zoom-to-fit.

Frame 1 (gold standard, 2400px wide) uses 2 columns. Frame 3 (also good, 3200px wide) uses 3 columns. Both are readable at zoom-to-fit. Frame 8 V3 (6400px wide, 6 columns in Row 1) required excessive zoom-out and text became unreadable.

### Zoom-to-Fit Readability Check

After calculating frame width, estimate the zoom-to-fit text size:

```
effective_font = actual_size × (1920 / frame_w)
```

Body text at `size=30` in a 6400px frame renders at ~9px effective — borderline unreadable. If effective font drops below **10px**, reduce column count by grouping/stacking related sections, or reduce frame width.

| Frame width | Body text (size=30) effective | Readable? |
|---|---|---|
| 2400px | ~24px | Yes |
| 3200px | ~18px | Yes |
| 5000px | ~12px | Acceptable |
| 6400px | ~9px | Borderline — reduce columns |
| 8000px | ~7px | Too small — must split or regroup |

### Collaborative Sticky Rows

- Always create **3+ rows** of Q&A pairs or blank stickies in collaborative sections
- 2 rows is not enough capture space for a real workshop — people need room to contribute
- Row spacing: ~220-240px between sticky centres (not 180px which causes overlap)

### Sticky Note Spacing

Stickies in vertical lists need **~260px vertical gaps** between centers. Using 180px causes visual overlap because stickies render taller than their DSL coordinate height.

### RAID Stickies

Use `w=264` (narrower than Q&A stickies), positioned left-aligned within their column (offset x slightly left of column center).

### Stakeholder Items

Use `SHAPE type=round_rectangle` (NOT `CARD` — CARD items have minimum size constraints). Size: `w=227 h=43` for compact labels, `h=60` for longer text. Position between the header and the grey box, not inside it.

### Font Sizes for Real Content

Increase font sizes from template defaults for readability — compliance/emphasis text at size 34, cross-cutting notes at size 36, link text at size 24, stream card descriptions at size 30.

---

## Content Area Backgrounds

| Fill | Opacity | Use |
|---|---|---|
| `#e6e6e6` | `1.0` | Standard content panel backgrounds |
| `#f5f5f5` | `1.0` | Questions/sticky grid backgrounds (lighter) |
| `#d5d8ed` | `1.0` | Scope section outer layer (lavender) |
| `#ffffff` | `1.0` | Scope section inner layer / RAID column containers |
| `#ffffff` | `0.0` | Transparent — text items |

### Questions Area Background

For the "Questions" section with sticky grids:
- Background shape: `fill=#f5f5f5 fill_opacity=1.0` (very light grey, lighter than content panels)
- Creates a subtle contrast behind the sticky note grid

### Scope Section — Layered Depth Effect

The "High level scope" area uses layered shapes to create visual depth:
1. Outer layer: `fill=#d5d8ed` (lavender) — `type=round_rectangle`
2. Inner layer: `fill=#ffffff` (white) — slightly smaller, on top
3. A thin vertical divider shape separates "IN" and "OUT"

---

## Text Colours

| Colour | Size range | Use |
|---|---|---|
| `#1a1a1a` | 30-36 | Body text (primary), bullet lists, descriptions |
| `#000000` | 32-36 | Strong body text (action lists, outcomes) |
| `#232428` | 32 | Actions text on light backgrounds |
| `#7b14ef` | 19-39 | Accent text — labels, links, doc references, timing annotations in agendas |
| `#8241aa` | 24 | Descriptive subtext (RAID column descriptions, fine print) |
| `#2d9bf0` | 39 | External partner/team labels (underlined) |
| `#394666` | 35-64 | Text on yellow backgrounds |
| `#ffffff` | 45-64 | White text on dark/purple backgrounds, white links on purple callouts |
| `#e18e9b` | 92 | Attention callout ("Needs further input") — soft pink, large |

---

## Sticky Note Colours

### Pattern A: Q&A Grid (standard workshop pattern)

| DSL color | Role | Notes |
|---|---|---|
| `black` | Question prompt (top sticky) | Contains the question text |
| `violet` | Answer/response (bottom sticky) | Participant fills in response |

**Layout:** Columns of pairs, x-spacing ~450px, y-spacing between Q and A ~180px, y-spacing between pairs ~470px.

### Pattern B: Q&A Grid (variant — used in Solo Money kickoff)

| DSL color | Role |
|---|---|
| `dark_blue` | Question prompt (top) |
| `light_yellow` | Response (bottom) |

### Pattern C: RAID Board Stickies (rectangle)

| DSL color | Shape | Size | Semantic use |
|---|---|---|---|
| `red` | `rectangle` | `w=154` (small) | Critical risks, hard blockers |
| `orange` | `rectangle` | `w=154-212` | Concerns, medium risks, notable items |
| `light_yellow` | `rectangle` | `w=154` | Assumptions, noted dependencies |
| `light_green` | `rectangle` | `w=154` | Actionable dependencies, positive items |
| `light_pink` | `rectangle` | `w=350` | HIGH severity risks (larger, detailed) |
| `light_blue` | `rectangle` | `w=350` | Assumptions (larger, detailed) |

### Pattern D: Stakeholder Cards

Use the card-based stakeholder structure from the D2 kickoff board. Each stakeholder gets a coloured card themed by role type.

| Card theme hex | Role type |
|---|---|
| `#af7e04` (amber) | BA / PM leads |
| `#fe02a7` (magenta) | PM / Commercial |
| `#659df2` (blue) | Design |
| `#ffdc4a` (gold) | Tech team |
| `#067429` (dark green) | Specialist tech |
| `#2dc75c` (green) | PMM / Marketing |

Cards display: Name, Role, and are grouped by function or team. Use `card_create` or shapes with team labels.

### Pattern E: Timeline Milestone Stickies

| DSL color | Shape | Size | Use |
|---|---|---|---|
| `red` | `square` | `w=119` | Hard deadline milestones on plan |
| `light_yellow` | `square` | `w=240` | Questions/notes on plan |

---

## RAID Column Styling

| Element | Style |
|---|---|
| Section header | Secondary tier shape (`#c497fe fill_opacity=0.7 color=#394666`) — note the 0.7 opacity |
| Container shape | `fill=#ffffff fill_opacity=0.0 border_color=#abacf1 border_style=normal border_width=8.0` |
| Column title | Text item, colour `#7b14ef`, size 80 |
| Column description | Text item, colour `#8241aa`, size 24 |
| Column spacing | ~800px apart (center-to-center) |
| Column size | `w=756 h=1674` |

**RAID column descriptions (consistent text):**
- Risks: "Potential problems that might impact success"
- Assumptions: "Factors considered true for planning but yet to be confirmed"
- Issues: "Existing problems that need to be addressed to minimise impact"
- Dependencies: "Internal and external factors that we are relying on to succeed"

---

## Divider / Separator Line

Thin vertical shape: `fill=#7b14ef fill_opacity=0.3 width=8` (or `fill=#ffffff` with divider role)

---

## Typography Patterns

| Visual intent | Implementation | Size |
|---|---|---|
| Section title | `round_rectangle` shape, Primary or Tertiary tier | 64-72 |
| Sub-label | `round_rectangle` shape, Secondary tier | 48 |
| Large emphasis label | Secondary shape, for section banners | 100 |
| Body content | `TEXT` item, `#1a1a1a`, align left | 30-36 |
| Agenda / numbered list | `TEXT` item with `<ol><li>` HTML, time annotations in `color:rgb(123,20,239)` | 32 |
| Accent label | `TEXT` item, `#7b14ef` | 36-39 |
| Fine print / descriptions | `TEXT` item, `#8241aa` | 19-24 |
| Attention callout | `TEXT` item, `#e18e9b`, large | 92 |
| External partner label | `TEXT` item, `#2d9bf0`, underlined | 39 |
| Link text | `<a href="...">` wrapped, colour `#7b14ef` | 19-24 |
| Bold emphasis in body | `<p><strong>Label:</strong> content</p>` | — |
| Strikethrough (completed) | `<s>completed action</s>` | — |

### Agenda Formatting Convention

Agenda items use an ordered list with **timing annotations** in purple inline:

```html
<ol>
  <li>Meeting purpose <span style="color:rgb(123,20,239)">- 10 mins</span></li>
  <li class="ql-indent-1">Sub-item detail</li>
  ...
</ol>
```

---

## Frame Sizes by Purpose

| Purpose | Width x Height | Notes |
|---|---|---|
| Full workshop canvas (kickoff) | `27500 x 2540` | Contains all sections in one horizontal frame. From both verified boards: 26000–27500 wide, 2540–2750 tall |
| Header / banner (wide) | `6600 x 119` | Full-width emphasis header (e.g., "High level requirements") |
| Header / banner (section) | `2844 x 119` | Mid-width structural header (e.g., "Draft high level plan") |
| Header / banner (narrow) | `1004 x 108` | Single-section header (e.g., "Next steps", "Actions & follow ups") |
| Small info panel (agenda, docs) | `874 x 112` | Header + `874 x 508` content + `874 x 175` small zone |
| Problem / context panel | `874 x 804` | Problem statement area — header (106h) + small zone (276h) + large zone (803h) |
| Metrics / info panel | `874 x 524` | Supporting content with text items inside |
| Brainstorm area | `3000 x 2000` | Open space for stickies |
| Q&A sticky grid | `2397 x 1810` | Background shape with columns of dark_blue/light_yellow pairs. Header above at `2397 x 157` |
| Q&A grid (variant/larger) | `2397 x 2433` | Extended version with more pair rows |
| Scope section (IN/OUT) | `1506 x 1378` | Layered: lavender outer (`#d5d8ed`) + white inner, divided by thin separator |
| RAID columns | `3147 x 119` header + 4x `756 x 1675` columns | Four bordered columns (`border_color=#abacf1 border_width=8.0`) |
| High level plan (table area) | `2844 x 1009` | Grey rectangle with milestone stickies overlaid |
| Stakeholder panel | `874 x 964` | Content area with mini-stickies (`w=80`, square) for names |
| Actions & next steps | `1004 x 982` | Vertical layout: header + grey content area |
| Actions & follow ups | `1004 x 825` | Alternate vertical: header + content (with text list inside) |
| "Things worth remembering" | `1004 x 982` | Same structure as next steps — mirror panel |
| Requirements zone (wide) | `6596 x 119` header + content below | Wide header with requirement stickies/text beneath |

---

## Section Spacing & Positioning Conventions

Based on verified boards, sections are laid out **horizontally following the meeting agenda sequence**. The board reads left-to-right in the same order as the session itself:

| Horizontal position (x range) | Section | Agenda alignment |
|---|---|---|
| 0–950 | Agenda + Docs & references | Pre-read / setup |
| 950–1900 | Problem statement + Stakeholders | Agenda item 1: Meeting purpose |
| 1900–2900 | Metrics + Scope (IN/OUT) | Agenda item 1 (cont.): context |
| 2900–4300 | SLAs / Supporting info | Agenda item 1 (cont.): context |
| 4300–7700 | Questions (Q&A grid) | Agenda item 5: Questions |
| 6700–10000 | Plan table + High level plan | Agenda item 3: Planning |
| 10000–20000 | Requirements + Service design | Agenda items 2-3: Stories + Design |
| 20000–24200 | RAID | Agenda item 4: RAID capture |
| 24200–26200 | Next steps + Actions | Agenda item 5+: Wrap-up |
| 26200–27500 | "Things worth remembering" | Post-meeting reference |

**Key principle:** If the agenda changes, the board layout changes to match. Always position sections in the order they will be discussed.

**Vertical spacing:**
- Header to first content element: ~130-170px gap
- Small grey zone to large grey zone: ~50-100px
- Between content text lines: standard line height
- Sticky note pairs: Q sticky to A sticky = ~180px center-to-center vertically

---

## DSL Quick Reference — Copy-Paste Snippets

Replace `{frameUrl}` with the actual parent frame URL. All positions are frame-relative (top-left = 0,0).

### Primary Header (section title)

```
SHAPE parent={frameUrl} x=500 y=130 w=874 h=112 type=round_rectangle fill=#7b14ef fill_opacity=1.0 color=#ffffff font=unknown size=64 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "<p>Section Title</p>"
```

### Secondary Header (sub-section)

```
SHAPE parent={frameUrl} x=500 y=130 w=874 h=112 type=round_rectangle fill=#c497fe fill_opacity=1.0 color=#394666 font=unknown size=64 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "<p><span style=\"color:rgb(123,20,239)\">Sub-section Title</span></p>"
```

### Tertiary Header (attention/data)

```
SHAPE parent={frameUrl} x=500 y=130 w=874 h=112 type=round_rectangle fill=#fff854 fill_opacity=1.0 color=#394666 font=unknown size=64 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "<p><span style=\"color:rgb(57,70,102)\">Data Section</span></p>"
```

### Dark Header (structural)

```
SHAPE parent={frameUrl} x=500 y=1270 w=874 h=126 type=round_rectangle fill=#232428 fill_opacity=1.0 color=#ffffff font=unknown size=64 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "<p><span style=\"color:rgb(255,255,255)\">Docs & references</span></p>"
```

### Content Panel (small grey zone)

```
SHAPE parent={frameUrl} x=500 y=295 w=874 h=175 type=rectangle fill=#e6e6e6 fill_opacity=1.0 color=#1a1a1a font=open_sans size=25 align=left valign=top border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 ""
```

### Content Panel (large grey zone)

```
SHAPE parent={frameUrl} x=500 y=505 w=874 h=508 type=rectangle fill=#e6e6e6 fill_opacity=1.0 color=#1a1a1a font=open_sans size=25 align=left valign=top border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 ""
```

### Body Text (inside content panel)

```
TEXT parent={frameUrl} x=520 y=450 w=822 color=#1a1a1a fill=#ffffff fill_opacity=0.0 font=unknown size=36 align=left "<p>Body text content goes here. Can include <strong>bold</strong> and <em>italic</em>.</p>"
```

### Accent Label (purple link-style)

```
TEXT parent={frameUrl} x=340 y=1686 w=471 color=#7b14ef fill=#ffffff fill_opacity=0.0 font=unknown size=36 align=left "<p>Feature requirements (WIP)</p>"
```

### Bullet List (inside content panel)

```
TEXT parent={frameUrl} x=2432 y=1884 w=827 color=#1a1a1a fill=#ffffff fill_opacity=0.0 font=unknown size=36 align=left "<ol><li data-list=\"bullet\"><span class=\"ql-ui\"></span>First item</li><li data-list=\"bullet\"><span class=\"ql-ui\"></span>Second item</li><li data-list=\"bullet\" class=\"ql-indent-1\"><span class=\"ql-ui\"></span>Sub-item</li></ol>"
```

### Agenda (numbered list with time annotations)

```
TEXT parent={frameUrl} x=523 y=452 w=875 color=#1a1a1a fill=#ffffff fill_opacity=0.0 font=unknown size=32 align=left "<ol><li data-list=\"ordered\"><span class=\"ql-ui\"></span>Meeting purpose<span style=\"color:rgb(123,20,239)\"> -10 mins</span></li><li data-list=\"ordered\" class=\"ql-indent-1\"><span class=\"ql-ui\"></span>Sub-item detail</li><li data-list=\"ordered\"><span class=\"ql-ui\"></span>Discussion <span style=\"color:rgb(123,20,239)\">- 15 mins</span></li></ol>"
```

### Q&A Sticky Pair (question + answer space)

```
STICKY parent={frameUrl} x=4352 y=465 w=365 color=black shape=rectangle align=center valign=middle "Your question text here?"
STICKY parent={frameUrl} x=4352 y=652 w=365 color=violet shape=rectangle align=center valign=middle ""
```

### RAID Column Container

```
SHAPE parent={frameUrl} x=21766 y=1121 w=756 h=1675 type=round_rectangle fill=#ffffff fill_opacity=0.0 color=#394666 font=plex_sans size=59 align=center valign=middle border_color=#abacf1 border_style=normal border_width=8.0 border_opacity=1.0 ""
TEXT parent={frameUrl} x=21760 y=368 w=206 color=#7b14ef fill=#ffffff fill_opacity=0.0 font=unknown size=80 align=left "<p>Risks</p>"
TEXT parent={frameUrl} x=21771 y=436 w=518 color=#8241aa fill=#ffffff fill_opacity=0.0 font=unknown size=24 align=left "<p><span style=\"color:rgb(130,65,170)\">Potential problems that might impact success</span></p>"
```

### RAID Sticky (critical)

```
STICKY parent={frameUrl} x=21534 y=585 w=155 color=red shape=rectangle align=center valign=middle "<p>Risk description here</p>"
```

### RAID Sticky (concern)

```
STICKY parent={frameUrl} x=21970 y=789 w=213 color=orange shape=rectangle align=center valign=middle "<p>Concern or moderate issue</p>"
```

### Stakeholder Card (use card_create)

Cards are themed by role type. Use `card_create` with the appropriate theme colour from Pattern D:
- `#af7e04` (amber) for BA / PM leads
- `#fe02a7` (magenta) for PM / Commercial
- `#659df2` (blue) for Design
- `#ffdc4a` (gold) for Tech team
- `#067429` (dark green) for Specialist tech
- `#2dc75c` (green) for PMM / Marketing

### Team Label (internal)

```
TEXT parent={frameUrl} x=1104 y=1384 w=122 color=#7b14ef fill=#ffffff fill_opacity=0.0 font=unknown size=39 align=left "<p><u style=\"color:rgb(123,20,239)\">Internal Team</u></p>"
```

### Team Label (external partner)

```
TEXT parent={frameUrl} x=1192 y=2082 w=299 color=#2d9bf0 fill=#ffffff fill_opacity=0.0 font=unknown size=39 align=left "<p><u>Partner Name</u></p>"
```

### Attention Callout (soft pink)

```
TEXT parent={frameUrl} x=8361 y=627 w=1198 color=#e18e9b fill=#ffffff fill_opacity=0.0 font=unknown size=92 align=left "<p><span style=\"color:rgb(225,142,155)\">Needs further input</span></p>"
```

### Timeline Milestone Sticky

```
STICKY parent={frameUrl} x=9215 y=1173 w=120 color=red shape=square align=center valign=middle "<p>Milestone name</p><p>Date</p>"
```

### Scope Section (IN/OUT labels)

```
SHAPE parent={frameUrl} x=2448 y=1163 w=446 h=97 type=round_rectangle fill=#c497fe fill_opacity=1.0 color=#7b14ef font=unknown size=48 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "<p><span style=\"color:rgb(123,20,239)\">IN</span></p>"
SHAPE parent={frameUrl} x=3412 y=1163 w=446 h=97 type=round_rectangle fill=#c497fe fill_opacity=1.0 color=#7b14ef font=unknown size=48 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "<p><span style=\"color:rgb(123,20,239)\">OUT</span></p>"
```

### Table Section (header + grey backdrop for a Miro TABLE)

Use this pattern when placing a `table_create` table inside a visually contained section. The header and grey backdrop are created via `layout_create`; the table is created separately via `table_create`. Coordinates must be calculated so the table sits inside the grey box.

```
# Step 1: Create header + grey backdrop via layout_create
SHAPE parent={frameUrl} x={section_center_x} y={header_y} w={section_width} h=82 type=round_rectangle fill=#fff854 fill_opacity=1.0 color=#394666 font=open_sans size=48 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "Decisions (D-053 to D-059)"
SHAPE parent={frameUrl} x={section_center_x} y={grey_box_y} w={section_width} h={table_height+100} type=rectangle fill=#e6e6e6 fill_opacity=1.0 color=#1a1a1a font=open_sans size=25 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 ""

# Step 2: Create table via table_create at position inside grey box
# table x,y should be within the grey box bounds
# table_create → table_sync_rows to populate
```

**Coordinate calculation:**
- `header_y` = section top + (header_h / 2) = section_top + 41
- `grey_box_top` = header_y + (header_h / 2) + 15 (gap) = header_y + 56
- `grey_box_y` = grey_box_top + (grey_box_h / 2)
- Table position: centered within grey box (roughly `grey_box_y - some_offset` for top of table)

**Key rule:** Header center x MUST equal grey box center x MUST equal table center x. Misaligned centers look broken.
