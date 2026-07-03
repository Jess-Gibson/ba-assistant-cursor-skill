# Kickoff Board Template — Miro DSL Reference

> Extracted from a verified D2 Kickoff template (a prior kickoff board's reference frame).
> 112 items, ~26,300 x 2,750px single frame.

## Frame structure

**Single wide frame** containing all sections horizontally. Reads left-to-right matching the meeting agenda.

```
Frame: w=26307 h=2747 fill=#ffffff
```

## Section map (left-to-right, with x-coordinates)

| X range | Section | Header tier | Header text |
|---------|---------|-------------|-------------|
| 0–950 | Agenda + Docs & refs | Tertiary (#fff854) + Dark (#232428) | "Agenda" / "Docs & references" |
| 950–1900 | Problem statement | Primary (#7b14ef) | "Problem statement" |
| 1900–2900 | Success metrics | Secondary (#c497fe) | "Success metrics" |
| 2400–3900 | High level scope (IN/OUT/Future) | Primary (#7b14ef) | "High level scope" |
| 2900–3800 | [unnamed section] | Tertiary (#fff854) | Empty (placeholder) |
| 4000–5200 | Supporting data | Black (#000000) | "Supporting data" |
| 5200–6200 | Dependencies | Primary (#7b14ef) | "Dependancies" [sic] |
| 5700–6200 | [extra grey panel] | — | — |
| 4600–6200 | Current state | Secondary (#c497fe) | "Current state" |
| 6000–8800 | Questions (Q&A sticky grid) | Secondary (#c497fe, size 100) | "Questions" |
| 8800–10800 | Proposed timeline | — (text label) | "Proposed timeline" |
| 10000–12700 | Draft high level plan | Dark (#232428) | "Draft high level plan" |
| 13000–17200 | High level requirements | Tertiary (#fff854) | "High level requirements" |
| 17400–21100 | High level service design | Primary (#7b14ef) | "High level service design" |
| 21400–24800 | RAID (4 columns) | Secondary (#c497fe, opacity 0.7) | "RAID" |
| 25000–26000 | Actions & Owners + Next steps | Primary (#7b14ef) + Tertiary (#fff854) | "Actions & Owners" / "Next steps" |

## Header shapes — exact DSL patterns

### Tertiary header (Agenda)
```
SHAPE x=505 y=146 w=874 h=82 type=round_rectangle fill=#fff854 fill_opacity=1.0 color=#394666 font=unknown size=64 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "<p><span style=\"color:rgb(57,70,102)\">A</span>genda</p>"
```

### Primary header (Problem statement)
```
SHAPE x=1452 y=146 w=874 h=82 type=round_rectangle fill=#7b14ef fill_opacity=1.0 color=#ffffff font=unknown size=64 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "<p>Problem statement</p>"
```

### Secondary header (Success metrics)
```
SHAPE x=2425 y=146 w=874 h=82 type=round_rectangle fill=#c497fe fill_opacity=1.0 color=#394666 font=unknown size=64 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "<p><span style=\"color:rgb(57,70,102)\">Success metrics</span></p>"
```

### Dark header (Docs & references)
```
SHAPE x=505 y=750 w=874 h=82 type=round_rectangle fill=#232428 fill_opacity=1.0 color=#ffffff font=unknown size=64 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "<p><span style=\"color:rgb(255,255,255)\">Docs & references</span></p>"
```

### Black header (Supporting data)
```
SHAPE x=4581 y=146 w=1155 h=82 type=round_rectangle fill=#000000 fill_opacity=1.0 color=#ffffff font=unknown size=59 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "<p><span style=\"color:rgb(255,255,255)\">Supporting data</span></p>"
```

### Wide banner (High level scope)
```
SHAPE x=2921 y=970 w=1694 h=124 type=round_rectangle fill=#7b14ef fill_opacity=1.0 color=#ffffff font=unknown size=72 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "<p>High level scope</p>"
```

### Questions header (large size)
```
SHAPE x=7448 y=183 w=2397 h=157 type=round_rectangle fill=#c497fe fill_opacity=1.0 color=#7b14ef font=unknown size=100 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "<p><span style=\"color:rgb(123,20,239)\">Questions</span></p>"
```

## Grey backdrop boxes

All use: `type=round_rectangle fill=#e6e6e6 fill_opacity=1.0 border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0`

Note: skill says use `type=rectangle` for grey backdrops (user adjusts radius manually). Template uses `round_rectangle` — follow the skill guidance for new boards.

### Standard panel (under Problem statement)
```
SHAPE x=1452 y=691 w=874 h=979 type=round_rectangle fill=#e6e6e6 ...
```

### Small panel (under Agenda)
```
SHAPE x=505 y=438 w=874 h=473 type=round_rectangle fill=#e6e6e6 ...
```

### Docs panel (under Docs header)
```
SHAPE x=505 y=1103 w=874 h=595 type=round_rectangle fill=#e6e6e6 ...
```

## Text elements — patterns

### Body text (inside grey panel)
```
TEXT x=1452 y=378 w=786 color=#1a1a1a fill=#ffffff fill_opacity=0.0 font=unknown size=30 align=left "<p><strong>Problem Statement:</strong></p>..."
```

### Agenda (ordered list with purple timing)
```
TEXT x=488 y=369 w=818 color=#1a1a1a fill=#ffffff fill_opacity=0.0 font=unknown size=32 align=left "<ol><li data-list=\"ordered\">...<span style=\"color:rgb(123,20,239)\"> - 5 mins</span></li>...</ol>"
```

### Accent label (purple link)
```
TEXT x=188 y=864 w=195 color=#7b14ef fill=#ffffff fill_opacity=0.0 font=unknown size=39 align=left "<p><span style=\"color:rgb(123,20,239)\">All in one:</span></p>"
```

### Link text
```
TEXT x=580 y=864 w=588 color=#7b14ef fill=#ffffff fill_opacity=0.0 font=unknown size=19 align=left "<p><u><a href=\"https://...\">add link</a></u></p>"
```

## Q&A sticky grid

Pattern: columns of black (question) + violet (answer) sticky pairs.

```
# Column spacing: ~453px center-to-center
# Row spacing: Q to A = ~183px, pair to pair = ~279px (Q1→Q2 centers)
# Sticky size: w=365, shape=rectangle

# Column 1
STICKY x=6536 y=494 w=365 color=black shape=rectangle align=center valign=middle "Questions here"
STICKY x=6536 y=676 w=365 color=violet shape=rectangle align=center valign=middle "Answers here"
STICKY x=6536 y=956 w=365 color=black shape=rectangle align=center valign=middle ""
STICKY x=6536 y=1151 w=365 color=violet shape=rectangle align=center valign=middle ""

# Column 2 (x += 453)
STICKY x=6989 y=494 w=365 color=black shape=rectangle ...
STICKY x=6989 y=676 w=365 color=violet shape=rectangle ...
```

Q&A grid background:
```
SHAPE x=7439 y=1299 w=2380 h=2036 type=round_rectangle fill=#e6e6e6 fill_opacity=0.3 ...
```

## Scope section

Layered structure with bordered container, IN/OUT labels, and divider.

### Container
```
SHAPE x=2908 y=1855 w=1868 h=1580 type=round_rectangle fill=#ffffff fill_opacity=0.0 border_color=#d5d8ed border_style=normal border_width=12.0 ...
```

### IN / OUT labels
```
SHAPE x=2448 y=1163 w=446 h=97 type=round_rectangle fill=#c497fe fill_opacity=1.0 color=#7b14ef font=unknown size=48 ... "<p><span style=\"color:rgb(123,20,239)\">IN</span></p>"
SHAPE x=3368 y=1163 w=446 h=97 type=round_rectangle fill=#c497fe fill_opacity=1.0 color=#7b14ef font=unknown size=48 ... "<p><span style=\"color:rgb(123,20,239)\">OUT</span></p>"
```

### Future scope label
```
SHAPE x=3368 y=1797 w=446 h=97 type=round_rectangle fill=#c497fe ... "<p><span style=\"color:rgb(123,20,239)\">F</span>uture scope</p>"
```

### What's been built label
```
SHAPE x=2425 y=2221 w=446 h=97 type=round_rectangle fill=#c497fe ... "<p>WHAT'S BEEN BUILT</p>"
```

### Divider line
```
SHAPE x=2921 y=1849 w=8 h=1415 type=round_rectangle fill=#7b14ef fill_opacity=0.3 ...
```

## RAID section

### RAID banner header
```
SHAPE x=23008 y=135 w=3147 h=119 type=round_rectangle fill=#c497fe fill_opacity=0.7 color=#394666 font=unknown size=64 ... "<p><span style=\"color:rgb(57,70,102)\">R</span>AID</p>"
```

### RAID column containers (4 columns, ~800px apart)
```
SHAPE x=21804 y=1117 w=756 h=1675 type=round_rectangle fill=#ffffff fill_opacity=0.0 border_color=#abacf1 border_style=normal border_width=8.0 border_opacity=1.0 ""
SHAPE x=22610 y=1111 w=756 h=1675 type=round_rectangle fill=#ffffff fill_opacity=0.0 border_color=#abacf1 ...
SHAPE x=23407 y=1120 w=756 h=1675 type=round_rectangle fill=#ffffff fill_opacity=0.0 border_color=#abacf1 ...
SHAPE x=24204 y=1120 w=756 h=1675 type=round_rectangle fill=#ffffff fill_opacity=0.0 border_color=#abacf1 ...
```

### RAID column titles
```
TEXT x=21807 y=367 w=206 color=#7b14ef font=unknown size=80 align=left "<p>Risks</p>"
TEXT x=22627 y=367 w=497 color=#7b14ef font=unknown size=80 align=left "<p>Assumptions</p>"
TEXT x=23415 y=367 w=246 color=#7b14ef font=unknown size=80 align=left "<p>Issues</p>"
TEXT x=24227 y=367 w=549 color=#7b14ef font=unknown size=80 align=left "<p>Dependencies</p>"
```

### RAID column descriptions
```
TEXT x=21817 y=435 w=518 color=#8241aa font=unknown size=24 align=left "<p><span style=\"color:rgb(130,65,170)\">Potential problems that might impact success</span></p>"
TEXT x=22609 y=435 w=686 color=#8241aa font=unknown size=24 align=left "<p><span style=\"color:rgb(130,65,170)\">F</span>actors considered true for planning but yet to be confirmed</p>"
TEXT x=23407 y=435 w=727 color=#8241aa font=unknown size=24 align=left "<p>Existing problems that need to be addressed to minimise impact</p>"
TEXT x=24204 y=435 w=705 color=#8241aa font=unknown size=24 align=left "<p>Internal and external factors that we are relying on to succeed</p>"
```

## Stakeholder cards

Grouped under "Stakeholders" tertiary header. Cards themed by role:

```
SHAPE x=988 y=1476 w=1821 h=82 type=round_rectangle fill=#fff854 ... "<p><span style=\"color:rgb(57,70,102)\">S</span>takeholders</p>"

CARD x=231 y=1588 w=227 h=42 theme=#659df2 "<p>Designers</p>"
CARD x=231 y=1639 w=227 h=42 theme=#ffdc4a "<p>Tech + Delivery</p>"
CARD x=231 y=1691 w=227 h=42 theme=#fe02a7 "<p>Product</p>"
CARD x=487 y=1639 w=227 h=42 theme=#067429 "<p>CXNPL</p>"
CARD x=487 y=1691 w=227 h=42 theme=#2dc75c "<p>GSB</p>"
CARD x=487 y=1588 w=227 h=42 theme=#af7e04 "<p>S&O</p>"
```

## Actions & Owners + Next steps

```
# Primary header
SHAPE x=25469 y=143 w=1004 h=108 type=round_rectangle fill=#7b14ef ... "<p>Actions & Owners</p>"

# Grey panel
SHAPE x=25474 y=660 w=994 h=877 type=round_rectangle fill=#e6e6e6 ...

# Actions list
TEXT x=25474 y=269 w=932 color=#000000 font=unknown size=36 align=left "<ol><li data-list=\"bullet\">...</li></ol>"

# Tertiary header
SHAPE x=25479 y=1226 w=1004 h=108 type=round_rectangle fill=#fff854 ... "<p><span style=\"color:rgb(57,70,102)\">N</span>ext steps</p>"

# Next steps panel
SHAPE x=25484 y=1744 w=994 h=877 type=round_rectangle fill=#e6e6e6 ...

# Next steps list
TEXT x=25484 y=1601 w=932 color=#000000 font=unknown size=36 align=left "<ol><li data-list=\"bullet\">...</li></ol>"
```

## Key measurements

| Measurement | Value | Note |
|-------------|-------|------|
| Standard header height | 82px | Most sections |
| Wide banner header height | 119–124px | Scope, RAID, Requirements |
| Standard grey panel width | 874px | Most content panels |
| Standard content text width | 786–826px | ~50px narrower than grey panel |
| Q&A sticky width | 365px | Rectangle shape |
| Q&A column spacing | 453px | Center-to-center |
| Q&A row spacing (Q→A) | 183px | Center-to-center |
| Q&A pair spacing (pair→pair) | 279px | Between question centers |
| RAID column width | 756px | Bordered container |
| RAID column spacing | 797px | Center-to-center |
| Stakeholder card size | 227 x 42px | Compact |
| First header y (all sections) | ~146px | From frame top |

## Usage

When creating a new kickoff board, use this template to:
1. Size the frame based on section count (each section ~950–1800px wide)
2. Copy header DSL patterns exactly (fill, font, size, border)
3. Apply the Content Panel Pattern (header → grey backdrop → text overlay)
4. Use the Q&A grid pattern for structured questions
5. Use the RAID column pattern for risk capture
6. Use stakeholder cards themed by role
7. Place all content in a single `layout_create` call (or use frame URL for subsequent calls)
