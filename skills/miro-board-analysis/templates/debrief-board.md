# Template: Meeting Debrief Board

Patterns for populating meeting debrief content into Miro boards. Covers post-session content population (Pattern 11) and multi-table matrix layouts (Pattern 12).

---

## Pattern 11: Meeting Debrief Board (Post-Session Content Population)

When populating a meeting debrief into an existing frame that already has facilitation content (agenda, goals, stakeholders), the debrief outputs go in the available space between the facilitation setup (left) and the wrap/next-steps area (right).

### Content Types from a Debrief Document

| Section | Board element | Notes |
|---|---|---|
| Summary / overview | Content Panel (header + grey box + text) | Narrative — use standard panel pattern from `design-system.md` |
| Decisions table | Coloured header + grey backdrop + Miro TABLE inside | Table must be visually contained within a labelled section |
| Action items table | Coloured header + grey backdrop + Miro TABLE inside | Same pattern as Decisions |
| Open questions table | Coloured header + grey backdrop + Miro TABLE inside | Same pattern as Decisions |
| RAID updates table | Coloured header + grey backdrop + Miro TABLE inside | Same pattern as Decisions |
| Stakeholder signals | Content Panel (header + grey box + text) | Narrative with bold names |
| Cross-cutting impacts | Content Panel (header + grey box + text) | Narrative with bold labels |
| Before next meeting | Content Panel (header + grey box + text) | Grouped by timeframe |
| Decisions deferred | Content Panel or TABLE | Depends on volume |
| Knowns confirmed | Content Panel or TABLE | Depends on volume |
| Attendance | Content Panel (header + grey box + text) | If not already in facilitation content |

**CRITICAL: Tables must be wrapped in labelled sections.** A bare Miro table on the board with no header or visual container is unreadable when zoomed out — the viewer cannot tell what the table represents without reading individual cells. Every table MUST have:
1. A coloured header shape directly above it identifying the section (e.g. "Decisions (D-053 to D-059)")
2. A grey backdrop rectangle sized to contain the table with padding
3. The header and backdrop visually grouped so the section reads as one unit

### Layout — Two-Row Horizontal Arrangement (verified May 2026)

Don't scatter sections or stack them vertically. Use a **two-row** layout:

```
ROW 1 (y ~80-1000):   [Summary] → [Decisions TABLE] → [Actions TABLE] → [Before Next Meeting] → [Wrap/Day N+1]
ROW 2 (y ~1200-2000): [Open Questions TABLE] → [RAID TABLE] → [Stakeholder Signals] → [Cross-Cutting Impacts]
```

Key structural rules:
- **Tables go side-by-side, not stacked.** Decisions and Actions at the same y-level. Questions and RAID at the same y-level.
- **"Before Next Meeting" goes in Row 1** (top, prominent) — it's action-oriented and people need to see it without scrolling.
- **Narrative panels** (Signals, Cross-Cutting) go in Row 2 below the tables — they're reference material, not action items.

### Sizing Rules for Debrief Sections

- **Narrative panels** (Summary, Signals, Cross-Cutting, Before Next Meeting): Width 700-1150px. Size to fit text density — don't over-size. Text width should be ~45-90px narrower than grey box width. Bullet lists can be as narrow as w=330 for a tight scannable column.
- **Table sections** (Decisions, Actions, Questions, RAID): Table width is auto from `table_create`. The header shape width should match the table's rendered width.
- **Header-to-table alignment**: Header center x MUST match table center x. Verify after creation.
- **Row spacing**: ~100-120px gap between Row 1 bottom and Row 2 headers.
- **Overall density**: Don't spread content across the full frame — pull everything left to keep the board compact and scannable.

### Header Colour Convention for Debrief Sections

| Section | Header tier | Fill | Text colour |
|---|---|---|---|
| Debrief Summary | Primary | `#7b14ef` | `#ffffff` |
| Decisions | Tertiary | `#fff854` | `#394666` |
| Action Items | Dark | `#232428` | `#ffffff` |
| Open Questions | Secondary | `#c497fe` | `#7b14ef` |
| RAID Updates | Custom (red) | `#ef4444` | `#ffffff` |
| Stakeholder Signals | Secondary | `#c497fe` | `#7b14ef` |
| Cross-Cutting Impacts | Dark | `#232428` | `#ffffff` |
| Before Next Meeting | Tertiary | `#fff854` | `#394666` |
| Knowns Confirmed | Primary | `#7b14ef` | `#ffffff` |
| Decisions Deferred | Custom (amber) | `#f59e0b` | `#ffffff` |

### Common Mistakes to Avoid (verified May 2026)

1. **Placing tables without headers or visual containers.** The #1 issue. A standalone Miro table floating on the board is useless at zoom-out. Always wrap in header + grey backdrop.
2. **Headers misaligned with their content.** Header center x must match the content center x. If a table is at x=5500, the header must also be centered at x=5500 (or at whatever the table's rendered center ends up being).
3. **Grey boxes too wide.** Size to content. A narrative section with 5 bullet points doesn't need an 1800px-wide grey box.
4. **Ignoring reading order.** Sections must flow left-to-right matching the document structure. Don't scatter sections based on what fits — the board must tell a story.
5. **Not including ALL text from the source document.** Every section of the debrief file should appear on the board. Omitting content (e.g. Decisions Deferred, Knowns Confirmed) breaks the purpose of having the debrief on the board.
6. **Using `doc_create` for debrief content.** Miro documents don't match the visual system of the board (they render as standalone documents, not as styled panels). Use the Content Panel Pattern instead.
7. **Using `create_shape`/`create_text` from `user-miro-desktop` for styled content.** These tools have limited styling parameters and silently drop colour, font, alignment values. Always use `layout_create` DSL from `plugin-miro-miro` or `user-miro-mcp` for content that needs specific styling.

### Build Sequence for Debrief Content

1. `layout_read` the target frame — understand what exists and where space is available
2. Map debrief sections to horizontal positions in reading order
3. Create all narrative sections (header + grey box + text) via a single `layout_create` call
4. Create Miro tables via `table_create` + `table_sync_rows` at the correct positions
5. Create header shapes above each table via `layout_create` (matching table center x)
6. `layout_read` to verify — check for overlaps, misalignment, missing content

---

## Pattern 12: Multi-Table Matrix Board (Channel/Owner Matrix, GTM Readiness, etc.)

When a document contains **multiple related tables** (e.g. channel categories, function breakdowns, stakeholder groups), lay them out in a **multi-column grid**, not a vertical stack.

### Verified Layout Structure (Comms Channel/Owner Matrix, May 2026)

```
┌───────────────────────────────────────────────────────────────────────────────────────┐
│ FRAME: "Comms Channel / Owner Matrix — Sample Initiative"   (~9500 x 2500)        │
│                                                                                       │
│ ┌────────┐ ┌────────┐  ┌─ COL 1 ──────┐  ┌─ COL 2 ──────┐  ┌─ COL 3 ──────┐       │
│ │Overview│ │Ownership│  │ [Header]     │  │ [Header]     │  │ [Header]     │       │
│ │(purple)│ │Model   │  │ XF Snapshot  │  │ Cust Channels│  │ Enablement   │       │
│ │        │ │(dark)  │  │ TABLE (12r)  │  │ TABLE (10r)  │  │ TABLE (5r)   │       │
│ │text... │ │text... │  │              │  │              │  │              │       │
│ │        │ ├────────┤  │              │  ├──────────────┤  ├──────────────┤       │
│ ├────────┤ │Key Obs │  │              │  │ [Header]     │  │ [Header]     │       │
│ │Next    │ │(purple)│  │              │  │ Partner Ch.  │  │ XF Teams     │       │
│ │Steps   │ │text... │  │              │  │ TABLE (4r)   │  │ TABLE (8r)   │       │
│ │(yellow)│ │        │  │              │  │              │  │              │       │
│ │text... │ │        │  │              │  │              │  │              │       │
│ └────────┘ └────────┘  └──────────────┘  └──────────────┘  └──────────────┘       │
│  narrative panels ←→   tables in columns ←────────────────────────────────→       │
└───────────────────────────────────────────────────────────────────────────────────────┘
```

### Layout Rules for Multi-Table Matrix

1. **Narrative panels on the left** — Overview, ownership model, key observations, next steps. These provide context for the tables. Stack them in 1-2 tight columns.
2. **Tables in a multi-column grid** — Group related tables into columns. Pair smaller tables vertically within the same column (e.g. Partner Channels below Customer Channels, XF Teams below Enablement).
3. **Each table gets a coloured header shape above it** — Use the same colour-coding system as Pattern 11.
4. **Frame size should be tight** — Don't over-size the frame. Let the content determine the dimensions. A 5-table matrix with narrative panels fits in ~9500 x 2500.

### Table Header Alignment (API limitation)

Miro tables auto-size to their content — the API does not expose rendered table width. This means:
- **You cannot perfectly match header width to table width via API.** Header width must be estimated or set to a reasonable default (e.g. 1800px).
- **x-coordinate alignment:** Tables report their x as their left-edge anchor (not centre). The header shape x is its centre. To centre a 1800px header over a table at `table_x`, use `header_x = table_x + (estimated_table_width / 2)`. For a 6-column table this is roughly `table_x + 900`.
- **Expect manual adjustment** — The user will likely fine-tune header widths and positions. Columns may also need manual width adjustment within the table itself.
- **After creation, always run `layout_read`** to capture where the user moved things, so you can learn the actual positions for future boards.

### Table Column Width Limitation

- Miro API does not support setting individual column widths. Table columns auto-size based on content.
- Some columns (e.g. short select values like "MUST"/"SHOULD") render narrow, while text-heavy columns (e.g. "Content needed") render wider.
- If the user needs narrower columns, they must manually adjust in the Miro UI.

---

## Debrief-Specific Best Practices

1. **Every table needs a visible header** — a Miro table without a labelled header shape above it is invisible when zoomed out. Always create a coloured header shape before or above the table.
2. **Include ALL source document content** — if the debrief markdown has 10 sections, the board must have 10 sections. Don't drop "Decisions Deferred", "Knowns Confirmed", or "Attendance" because they seem minor.
3. **Match document reading order** — the board must read left-to-right in the same order as the source document sections.
4. **Size to content, not template** — grey backdrop boxes should fit the actual text/table. A 5-bullet narrative doesn't need an 1800px-wide box.
5. **Use `layout_create` DSL for all styled content** — never use `user-miro-desktop` `create_shape`/`create_text` for content that needs specific styling.
6. **Tables inside grey backdrops** — for structured data (Decisions, Actions, Questions, RAID), the Miro table should sit inside a grey backdrop rectangle with a coloured header above.
