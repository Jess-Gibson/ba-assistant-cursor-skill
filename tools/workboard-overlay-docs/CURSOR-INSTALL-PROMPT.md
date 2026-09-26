# Paste this into Cursor after unzipping the workboard overlay

Give your friend the zip **and** this prompt. The agent must not wipe their actions, profile, or live canvas.

---

## Prompt (copy from here)

```
I have the BA Workboard overlay package extracted on my machine.

Goal: install the richer workboard (Today checkboxes, calendar, full Update / End of Day prompts, Save staged updates) WITHOUT losing my personalisation.

Hard rules:
- Do NOT run upgrade-ba-assistant.py (that replaces the whole skill tree).
- Do NOT overwrite _workstream/workboard.json, ba-actions.json, ba-actions.md, calendar-feed.json, ba-profile.mdc, or ba-assistant-config.mdc.
- Do NOT regenerate or overwrite my live canvases/ba-workboard.canvas.tsx until I explicitly say the preview looks good.
- Do NOT replace commands/workboard.md or commands/wrap.md unless I confirm. If they already exist, leave them and write *.package siblings for comparison.

Please:
1. Find the extracted folder (it contains tools/upgrade-workboard.py). Run a dry-run using
   whichever Python launcher actually resolves on this machine (`python3` on Mac/Linux,
   `py` on Windows — try one, fall back to the other):
   python3 tools/upgrade-workboard.py --package "<extracted folder>"

2. Show me REPLACE vs PROTECT vs KEEP. Stop and ask if anything looks like it would overwrite my data or a file I customised.

3. After I confirm, apply with preview (not live canvas):
   python3 tools/upgrade-workboard.py --package "<extracted folder>" --apply
   That writes capability files and generates canvases/ba-workboard-overlay-preview.canvas.tsx from MY existing JSON.

4. Open or tell me how to open the preview canvas. Ask: keep preview only, promote preview to my live ba-workboard.canvas.tsx, or discard.

5. If I like the preview, regenerate the live canvas from my data:
   python3 _workstream/generate-workboard-canvas.py --canvas "<my canvases folder>/ba-workboard.canvas.tsx"
   Do not seed empty JSON. Do not invent initiatives.

If you are unsure whether a file is personalised, ASK ME. Do not guess.
```

---

## Shorter prompt (preview already applied)

```
I already ran the workboard overlay with --apply. Open ba-workboard-overlay-preview.canvas.tsx. Do not overwrite ba-workboard.canvas.tsx, workboard.json, or my actions until I say the preview is good.
```
