# Template: Options Comparison Board

A board layout for comparing 2-4 solution options side by side, with evaluation criteria, a recommendation section, and feedback capture. Use when the task is a solution options workshop, trade-off assessment, or decision support board.

---

## Standard Structure

```
[Context/Problem] → [Option 1] [Option 2] [Option 3] → [Evaluation Criteria] → [Recommendation] → [Feedback]
```

## Section Specifications

| Section | Width | Header tier | Content |
|---|---|---|---|
| Context / Problem | 874 | Primary (#7b14ef) | Problem statement, constraints, decision context |
| Option columns (N) | 874 each | Primary (#7b14ef) per option | Description text in grey box + pro/con stickies below |
| Evaluation criteria | 874–1821 | Tertiary (#fff854) | Table with criteria and scoring per option |
| Recommendation | 874 | Custom green (#22c55e) callout | Decision sticky + rationale text |
| Feedback area | 874–1821 | Secondary (#c497fe) | Empty brainstorm frame for attendee reactions |

## Column Layout by Option Count

| Options | Total options width | Layout |
|---|---|---|
| 2 options | 2 × 874 + 1 × 45 = 1793 | Side by side |
| 3 options | 3 × 874 + 2 × 45 = 2712 | Side by side |
| 4 options | 4 × 874 + 3 × 45 = 3631 | Side by side, or 2×2 grid if frame is narrow |

---

## Option Column Layout

Each option gets its own column:
- **Column header:** Primary tier, `w=874 h=82 size=64` with option name (e.g. "Option A: Direct Integration")
- **Body text:** `size=30`, option description in grey box (sized to actual content using algorithm Pass 3)
- **Pro stickies:** `color=light_green shape=rectangle w=365` — placed below the grey box
- **Con stickies:** `color=light_pink shape=rectangle w=365` — placed below the pros
- Stickies placed below the grey box, not inside it
- Sticky vertical spacing: ~260px between centres

### Recommended Option Callout

The recommended option gets a green banner above its column header:
```
SHAPE parent={frameUrl} x={option_center_x} y={banner_y} w=874 h=50 type=round_rectangle fill=#22c55e fill_opacity=1.0 color=#ffffff size=28 align=center valign=middle border_color=#ffffff border_style=normal border_width=1.0 border_opacity=1.0 "RECOMMENDED"
```

---

## Action Urgency Tiers (for Actions section)

If the board includes an actions section, use urgency-tiered headers:

| Urgency | Header fill | Sticky colour |
|---|---|---|
| Critical (today/tomorrow) | `#ef4444` (red) | `light_pink` |
| High (this week) | `#f59e0b` (amber) | `light_yellow` |
| Waiting on others | `#232428` (dark) | `light_green` |
| Parkable / deferred | `#22c55e` (green) | `light_blue` |

---

## Evaluation Criteria Table

**Build with `table_create`:**
- Columns: Criterion (text) | Weight (text) | Option A (select) | Option B (select) | Option C (select) | Notes (text)
- Rating options: `Strong#79E49B`, `Moderate#FFED7B`, `Weak#FFADAD`, `Unknown#D6D6D6`
- Always include a coloured header shape above the table (Tertiary tier)

---

## Building This Board Type

1. Follow the 6-pass Board Construction Algorithm (`algorithm.md`)
2. In Pass 1, determine option count and whether the board needs evaluation criteria / feedback sections
3. In Pass 2, assign widths from the table above — total frame width scales with option count
4. After Pass 4, output the plan for review
5. After Pass 5, run `verification-checklist.md`
