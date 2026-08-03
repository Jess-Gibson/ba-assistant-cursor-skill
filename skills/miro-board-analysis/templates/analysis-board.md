# Template: Analysis / Status Board

A horizontal board for initiative analysis, status updates, or solution comparison. Use for boards like "ACMA SMS  -  Payments Analysis" or any initiative overview that combines problem context, analysis findings, solution options, RAID, and actions.

---

## Standard Structure (left to right)

```
[Problem/Context] → [Analysis/Findings] → [Options/Solutions] → [RAID] → [Actions/Next Steps]
```

## Section Specifications

All section headers use `h=82, size=64`. Differentiate via color tier, not font size. See `design-system.md` Header Hierarchy.

| Section | Width | Column type | Header tier | Content |
|---|---|---|---|---|
| Problem & Scope | 874–1821 | Standard or double | Primary (#7b14ef) | Problem statement text + scope (IN/OUT) |
| Key People & Dates | 874 | Standard | Tertiary (#fff854) | Names + role labels, key dates list |
| Analysis Findings | 1821–2162 | Double or wider | Primary (#7b14ef) + Secondary (#c497fe) | Multiple stacked sub-sections (one per meeting/topic), each with own header + grey box |
| Solution Options | 3 × 874 + 2 × 45 = 2712 | Three side-by-side columns | Primary (#7b14ef) per option | Option description text + pro/con stickies below. Recommended option gets a green (#22c55e) callout above. |
| RAID | 4 × 756 + 3 × 50 = 3174 | Four bordered columns | Secondary (#c497fe, opacity 0.7) | Standard RAID column pattern (see `design-system.md` RAID Column Styling) |
| Actions & Next Steps | 1004–1821 | Standard or double | Primary (#7b14ef) for urgency headers, Tertiary (#fff854) for next steps | Urgency-tiered: Critical (red banner), High (amber banner), Waiting on Others (dark), Parkable (green) |

**Typical total frame width:** 200 + 874 + 100 + 874 + 200 + 2162 + 200 + 2712 + 200 + 3174 + 200 + 1821 + 200 = ~12917px (adjust per actual content)

**Frame height:** Varies by content density. Simple analysis boards: 2200-3000px. Comprehensive boards (problem + options + full RAID + actions + timeline): may exceed 5000px tall. Always content-fitted  -  never pad height for visual uniformity.

---

## Layout Guidance for Comprehensive Analysis Boards

When a board combines problem context, solution options, full RAID, actions, timeline, and confidence scores in a single frame, follow these column grouping rules to prevent the frame from becoming too wide and text too small at zoom-to-fit.

**Target 3-4 content columns per horizontal row.** Group related sections vertically:

```
Row 1: [Problem + Where We Are] [Key People + Scope] [Options or wider content cols]
        stacked in 1 column      stacked in 1 column   2-3 columns max

Row 2: [Full-width RAID bar]
        [Risks] [Assumptions] [Dependencies] [Unknowns]
        4 columns OK  -  RAID is a recognized 4-column pattern

Row 3: [Full-width Actions bar]
        [Decisions] [Comms] [Actions] [Timeline + Confidence]
        3-4 columns max
```

Use full-width banner bars (Dark tier, `fill=#232428`) between major rows to create clear visual breaks.

**Grey box heights within each row are independently content-fitted**  -  NEVER normalised to the tallest. Uneven bottom edges are correct.

---

## Solution Option Comparison Layout

Each option gets its own column within the wider section:
- Column header: Primary tier, `w=874 h=82 size=64` with option name
- Body text: `size=30`, option description in grey box
- Pro sticky: `color=light_green shape=rectangle w=365`
- Con sticky: `color=light_pink shape=rectangle w=365`
- Stickies placed below the grey box, not inside it

## Action Urgency Tiers

| Urgency | Header fill | Sticky colour |
|---|---|---|
| Critical (today/tomorrow) | `#ef4444` (red) | `light_pink` |
| High (this week) | `#f59e0b` (amber) | `light_yellow` |
| Waiting on others | `#232428` (dark) | `light_green` |
| Parkable / deferred | `#22c55e` (green) | `light_blue` |

---

## Content Completeness Checklist (MANDATORY for analysis boards)

Before building, **read ALL source documents**  -  do not summarise from memory:

- [ ] `initiative-tracker.md`  -  decisions, RAID, requirements, knowns, unknowns
- [ ] `SESSION-CONTEXT.md`  -  recent session decisions, blockers, open questions
- [ ] Solution option outputs (e.g. `solution-options-*.md`)
- [ ] Meeting debriefs (all relevant `debriefs/*.md`)
- [ ] Confluence pages (if referenced in the tracker)

### Content rules

- [ ] ALL RAID items (risks, assumptions, issues, dependencies) from the tracker must appear on the board
- [ ] ALL decisions from the tracker must appear  -  with ID, date, owner, status
- [ ] No sections omitted as "minor" (Decisions Deferred, Knowns, Attendance, etc.)
- [ ] All text from the source is included  -  not summarised or truncated
- [ ] **Decision-aware filtering**  -  if a decision has been made (e.g. "going with Option A"), filter content accordingly. Don't include architecture decisions or details that only apply to rejected/parked options.
- [ ] **Cross-reference multiple sources**  -  solution options, debriefs, and tracker may have different information. Include all relevant items from each.

---

## Building This Board Type

1. Follow the 6-pass Board Construction Algorithm (`algorithm.md`)
2. In Pass 1, cross-check against the section list above  -  flag any missing sections
3. In Pass 2, assign widths from the table above
4. In Pass 3, read ALL source documents and measure actual content
5. After Pass 4, output the plan for review
6. After Pass 5, run `verification-checklist.md`
