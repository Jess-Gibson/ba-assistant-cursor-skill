# Post-Build Verification Checklist

**NEVER SKIP THIS CHECKLIST.** The user has explicitly flagged skipped verification as a recurring problem. Run every check after every `layout_create` call, even if you are confident the dimensions are correct.

This is Pass 6 of the Board Construction Algorithm (`algorithm.md`).

---

## Step 1: Read the Created Content

Run `layout_read mode=full` on the new frame immediately after `layout_create` succeeds.

```
CallMcpTool → toolName: "layout_read", miro_url: "{frame_url}", mode: "full"
```

If `layout_read` is not available (only `user-miro-desktop` server), note this to the user and skip to Step 9 — the verification cannot be automated without `layout_read`.

---

## Step 2: Overlap Check

**What to verify:** No two items in the same x-column have overlapping vertical bounding boxes (unless one is a deliberate backdrop).

**How:** For every pair of items at similar x-coordinates, compute `[y - h/2, y + h/2]` for each. These ranges must NOT intersect.

**Failure looks like:** Two shapes visually stacked on top of each other, text hidden behind a grey box, or headers overlapping content.

**Fix:** Adjust y-coordinates to add spacing. Minimum 45px gap between adjacent element edges.

---

## Step 3: Text Containment Check

**What to verify:** For every TEXT + grey box pair, the text is fully inside the grey box.

**How:** Compute:
- `text_top = text_y - (estimated_text_height / 2)`
- `text_bottom = text_y + (estimated_text_height / 2)`
- `grey_top = grey_y - (grey_h / 2)`
- `grey_bottom = grey_y + (grey_h / 2)`

Verify: `text_top > grey_top` AND `text_bottom < grey_bottom`

**Failure looks like:** Text visibly extends below or above its grey backdrop box.

**Fix:** Increase grey box height (`grey_h`), recalculate `grey_y`, and recreate. Use the formula from `design-system.md`: `grey_box_h = (estimated_text_height × 1.15) + 65`.

---

## Step 4: Text Top-Alignment Check

**What to verify:** Text appears near the TOP of its grey box, not vertically centered.

**How:** Compare `text_y` vs `grey_y`. The text center should be **significantly above** the grey box center. Specifically: `text_y` should be close to `grey_top + 15 + (text_height / 2)`.

**Failure looks like:** Text appears in the middle of a tall grey box with empty space above it.

**Fix:** Recalculate `text_y = grey_top + 15 + (estimated_text_height / 2)`. The 15px value is empirically calibrated.

---

## Step 5: Centering Check

**What to verify:** All content columns are horizontally centered in the frame.

**How:** Compute:
- `leftmost_edge = min(all_element_left_edges)`
- `rightmost_edge = max(all_element_right_edges)`
- `left_margin = leftmost_edge`
- `right_margin = frame_w - rightmost_edge`

Verify: `abs(left_margin - right_margin) <= 20px`

**Failure looks like:** Content visibly off-center — more whitespace on one side.

**Fix:** Shift all elements horizontally by `(right_margin - left_margin) / 2`.

---

## Step 6: Bounds Check

**What to verify:** No element extends outside the frame boundaries.

**How:** For every item, verify:
- `item_left >= 0` (where `item_left = item_x - item_w/2`)
- `item_right <= frame_w`
- `item_top >= 0`
- `item_bottom <= frame_h`

**Failure looks like:** Elements clipped at frame edges, or invisible because they're outside the frame.

**Fix:** Either move the element inside or expand the frame dimensions.

---

## Step 7: Spacing Check

**What to verify:** Minimum 45px gap between adjacent column edges.

**How:** For each pair of adjacent columns, compute the gap between `column_A_right_edge` and `column_B_left_edge`.

**Failure looks like:** Columns visually touching or too close together.

**Fix:** Increase gaps or reduce column widths.

---

## Step 8: Duplicate Title Check

**What to verify:** The frame's name text and the title shape text are NOT the same.

**How:** Compare the frame `title="..."` with the first header shape's content text.

**Failure looks like:** Two visible title bars at the top — one from the frame name (small label), one from the shape (large header). Both say the same thing.

**Fix:** Frame name = short ID (e.g. "3. Solution Options"). Title shape = descriptive text (e.g. "Solution Options (23 Jun Reframe)").

---

## Step 9: Width Check

**What to verify:** No singular text box is wider than ~900px unless it contains a table, diagram, image, or multi-column content.

**How:** Check all TEXT items. If `text_w > 900` and the text is a single narrative/bullet block (not a table or flow), flag it.

**Failure looks like:** Very wide text with short lines and large empty right margins.

**Fix:** Reduce width to 812-874px. Let text wrap naturally.

---

## Step 10: Header Hierarchy Check

**What to verify:** ALL headers (frame title AND section headers) use h=82/size=64. Visual hierarchy comes from WIDTH and COLOR TIER, not font size. Frame title = full-width. Section headers = column-width. Sub-labels use h=36/size=22.

**How:** Check each header shape's h and size values. All should be h=82, size=64. Differentiation comes from width (full-width title vs narrower section headers) and color tier (Primary, Secondary, Tertiary, Dark, Black).

**Failure looks like:** Headers at different font sizes (e.g. size=42 for sections) — at wide frame zoom levels, smaller headers become unreadable.

**Fix:** Set ALL headers to h=82, size=64. Use width and color tier for hierarchy. See `design-system.md` Header Hierarchy.

---

## Step 11: Fix and Report

After running all checks:

1. **If issues found:** Delete the problematic elements and recreate with corrected coordinates. Run verification again on the fixed content.
2. **If all checks pass:** Report to the user:
   - What was created (frame name, section count, content summary)
   - Board URL
   - **Expected manual adjustments** (always flag these):
     - Table column widths (API cannot set individual column widths)
     - Header widths over tables (may need manual alignment)
     - Grey box corner radius (user adjusts from 0px to 20px)
     - Any elements flagged during verification that couldn't be auto-fixed
