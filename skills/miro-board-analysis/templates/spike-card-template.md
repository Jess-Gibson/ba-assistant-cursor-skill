# Spike Card Template  -  Miro DSL Reference

> Extracted from the BA's verified reference layout (Frame 15, widget `3458764674327280316` on board `uXjVHdjL1c4=`).
> Each spike is its own frame (w=2025, h=1500). Two-column layout with questions on the left, scope + priority on the right.

## Frame structure

**Individual frame per spike card**  -  NOT shapes inside a shared frame. This prevents overlap.

```
FRAME w=2025 h=1500 fill=#ffffff "S-{n} · {title} · {PRIORITY_LEVEL}"
```

## Layout  -  two-column inside a bordered card

```
┌─────────────────────────────────────────────────────────────────────┐
│  FRAME (w=2025, h=1500, fill=#ffffff)                               │
│                                                                     │
│  ┌── LEFT COLUMN (x ~505) ──────┐  ┌── RIGHT COLUMN (x ~1300+) ──┐│
│  │ [PRIORITY HEADER] S-n title  │  │ [IN label] + grey box + text ││
│  │ (w=920, h=70, fill=priority) │  │ [OUT label] + grey box + text││
│  │                              │  │                              ││
│  │ [WHY sub-header]             │  │ [Priority header] yellow     ││
│  │ (w=880, h=42, fill=#c497fe)  │  │ (w=880, h=42, fill=#fff854) ││
│  │                              │  │                              ││
│  │ [WHY grey box + text]        │  │ [MoSCoW priority chips]      ││
│  │ (w=872, h=130, fill=#f5f5f5) │  │ 5 chips in a row             ││
│  │                              │  │                              ││
│  │ [QUESTIONS sub-header]       │  │                              ││
│  │ (w=880, h=42, fill=#7b14ef)  │  │                              ││
│  │                              │  │                              ││
│  │ [question stickies grid]     │  │                              ││
│  │ 3 cols x N rows              │  │                              ││
│  │ each w=257                   │  │                              ││
│  └──────────────────────────────┘  └──────────────────────────────┘│
│                                                                     │
│  ┌── WHITE BORDERED CONTAINER (covers right + lower area) ─────────┐│
│  │ (w=1957, h=920, fill=#ffffff, border=#abacf1 width=4)           ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

## Priority colour coding

| Priority | Header fill | Text colour |
|----------|------------|-------------|
| Critical | `#cc0000` | `#ffffff` |
| High | `#e67e00` | `#ffffff` |
| Medium | `#f1c40f` | `#000000` |

## Exact DSL properties per element

### 1. Frame
```
FRAME x={col_x} y={row_y} w=2025 h=1500 fill=#ffffff "S-{n} · {title} · {PRIORITY}"
```

### 2. Priority header (top-left)
```
SHAPE parent={frame} x=525 y=100 w=920 h=70 type=round_rectangle fill={priority_color} fill_opacity=1.0 color={text_color} font=noto_sans size=28 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "S-{n} · {title}"
```

### 3. White bordered container (right column backdrop)
```
SHAPE parent={frame} x=1020 y=611 w=1957 h=920 type=round_rectangle fill=#ffffff fill_opacity=1.0 color=#1a1a1a font=noto_sans size=14 align=left valign=top border_color=#abacf1 border_style=normal border_width=4.0 border_opacity=1.0 ""
```

### 4. "Why we need this spike" sub-header
```
SHAPE parent={frame} x=505 y=202 w=880 h=42 type=round_rectangle fill=#c497fe fill_opacity=1.0 color=#7b14ef font=noto_sans size=22 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "Why we need this spike"
```

### 5. Why grey box
```
SHAPE parent={frame} x=505 y=298 w=872 h=130 type=rectangle fill=#f5f5f5 fill_opacity=1.0 color=#1a1a1a font=noto_sans size=14 align=left valign=top border_color=#e6e6e6 border_style=normal border_width=1.0 border_opacity=1.0 ""
```

### 6. Why TEXT (overlaid on grey box)
```
TEXT parent={frame} x=505 y=298 w=848 color=#1a1a1a fill=#ffffff fill_opacity=0.0 font=open_sans size=20 align=left "{business_reason_text}"
```

Content guidance for the "Why" text:
- Business-focused, not solution-assuming
- Explain the business problem or risk, not the technical approach
- Reference decisions (D-xxx) or knowns (K-xxx) where relevant
- Keep concise (2-3 sentences max)

### 7. "Key questions for the spike" sub-header
```
SHAPE parent={frame} x=505 y=451 w=880 h=42 type=round_rectangle fill=#7b14ef fill_opacity=1.0 color=#ffffff font=noto_sans size=22 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "Key questions for the spike"
```

### 8. Question stickies  -  dark_blue, rectangle, w=257

Grid layout: 3 columns, as many rows as needed.

```
# Row 1
STICKY parent={frame} x=194 y=569 w=257 color=dark_blue shape=rectangle align=left valign=top "{question_1}"
STICKY parent={frame} x=486 y=569 w=257 color=dark_blue shape=rectangle align=left valign=top "{question_2}"
STICKY parent={frame} x=793 y=569 w=257 color=dark_blue shape=rectangle align=left valign=top "{question_3}"

# Row 2 (y += 177)
STICKY parent={frame} x=194 y=746 w=257 color=dark_blue shape=rectangle align=left valign=top "{question_4}"
STICKY parent={frame} x=486 y=746 w=257 color=dark_blue shape=rectangle align=left valign=top "{question_5}"
# ... as many as needed
```

Content guidance for questions:
- Research insights, not implementation tasks
- Focus on what we need to LEARN, not what we need to BUILD
- Include business value/context questions where relevant
- Variable count  -  use as many stickies as needed for key research insights

### 9. "IN" scope label
```
SHAPE parent={frame} x=1303 y=210 w=432 h=36 type=round_rectangle fill=#ebdcfd fill_opacity=1.0 color=#7b14ef font=noto_sans size=18 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "IN"
```

### 10. IN grey box + text
```
SHAPE parent={frame} x=1303 y=291 w=432 h=90 type=rectangle fill=#f5f5f5 fill_opacity=1.0 color=#1a1a1a font=noto_sans size=14 align=left valign=top border_color=#e6e6e6 border_style=normal border_width=1.0 border_opacity=1.0 ""
TEXT parent={frame} x=1305 y=293 w=408 color=#1a1a1a fill=#ffffff fill_opacity=0.0 font=open_sans size=18 align=left "{in_scope_text}"
```

### 11. "OUT" scope label  -  same as IN but at x=1751
```
SHAPE parent={frame} x=1751 y=210 w=432 h=36 type=round_rectangle fill=#ebdcfd fill_opacity=1.0 color=#7b14ef font=noto_sans size=18 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "OUT"
```

### 12. OUT grey box + text  -  same pattern, x=1751
```
SHAPE parent={frame} x=1751 y=291 w=432 h=90 type=rectangle fill=#f5f5f5 fill_opacity=1.0 color=#1a1a1a font=noto_sans size=14 align=left valign=top border_color=#e6e6e6 border_style=normal border_width=1.0 border_opacity=1.0 ""
TEXT parent={frame} x=1753 y=293 w=408 color=#1a1a1a fill=#ffffff fill_opacity=0.0 font=open_sans size=18 align=left "{out_scope_text}"
```

### 13. "Priority" header (yellow)
```
SHAPE parent={frame} x=1527 y=451 w=880 h=42 type=round_rectangle fill=#fff854 fill_opacity=1.0 color=#000000 font=noto_sans size=22 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "Priority"
```

### 14. MoSCoW chips  -  5 round_rectangles in a row at y=542

Each chip: `w=148 h=90 type=round_rectangle border_width=3.0 fill_opacity=0.3`
Spacing: ~165px between centers.

```
# MUST Highest priority
SHAPE parent={frame} x=1197 y=542 w=148 h=90 type=round_rectangle fill=#bd0a0a fill_opacity=0.3 color=#000000 font=noto_sans size=18 align=center valign=middle border_color=#bd0a0a border_style=normal border_width=3.0 border_opacity=1.0 "<p>MUST</p><p>Highest priority</p>"

# MUST
SHAPE parent={frame} x=1362 y=542 w=148 h=90 type=round_rectangle fill=#bd0a0a fill_opacity=0.3 color=#000000 font=noto_sans size=18 align=center valign=middle border_color=#bd0a0a border_style=normal border_width=3.0 border_opacity=1.0 "<p>MUST</p>"

# Should
SHAPE parent={frame} x=1527 y=542 w=148 h=90 type=round_rectangle fill=#e97200 fill_opacity=0.3 color=#000000 font=noto_sans size=18 align=center valign=middle border_color=#e97200 border_style=normal border_width=3.0 border_opacity=1.0 "<p>Should</p>"

# Could
SHAPE parent={frame} x=1692 y=542 w=148 h=90 type=round_rectangle fill=#659df2 fill_opacity=0.3 color=#000000 font=noto_sans size=18 align=center valign=middle border_color=#0070cd border_style=normal border_width=3.0 border_opacity=1.0 "<p>Could</p>"

# Won't
SHAPE parent={frame} x=1857 y=542 w=148 h=90 type=round_rectangle fill=#b0b0b0 fill_opacity=0.3 color=#000000 font=noto_sans size=18 align=center valign=middle border_color=#595959 border_style=normal border_width=3.0 border_opacity=1.0 "<p>Won't</p>"
```

## Grid placement for multiple cards

When placing multiple spike cards in a parent frame:

| Measurement | Value | Notes |
|-------------|-------|-------|
| Card width | 2025px | Fixed |
| Card height | 1500px | Fixed |
| Column gap | 100px | Between card edges |
| Row gap | 100px | Between card edges |
| Column spacing | 2125px | center-to-center |
| Row spacing | 1600px | center-to-center |
| Grid | 3 columns x N rows | Scale rows to spike count |

**Placement must be intentional**  -  ensure cards sit below/beside existing facilitation content, not overlapping it. Always check the parent frame's existing content positions before placing.

### Starting position calculation

1. Read the parent frame via `layout_read`
2. Find the lowest y-coordinate of existing content
3. Place the first row at least 200px below that lowest content
4. Calculate column positions based on desired card alignment

## Content guidance

### "Why" text  -  business-focused
- Explain the business problem or risk being addressed
- Do NOT assume a solution (avoid words like "migration", "refactor", "rebuild")
- Reference decisions (D-xxx) or knowns (K-xxx) where relevant
- Focus on: what we don't know, what risk exists, what blocks delivery

### Questions  -  research insights
- Variable count (not fixed at 4)
- Focus on what we need to LEARN
- Include questions about business value, data availability, feasibility
- Include questions about scope boundaries and dependencies
- Avoid implementation questions (those come AFTER the spike)

### IN/OUT scope
- Business boundary, not technical boundary
- What the spike will investigate vs what it explicitly won't touch
- Helps the team stay focused during the spike

## Usage

1. Determine how many spikes need cards
2. Calculate grid positions in the target frame
3. Build DSL for each card using the exact patterns above
4. Each `layout_create` call can hold ~6 cards (138 items) within the 50K char limit
5. Always parent each element to its frame using `parent={frame_id}`
