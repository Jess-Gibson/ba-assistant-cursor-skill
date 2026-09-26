# _workstream

Cross-initiative working data for BA Assistant **Version 14**.

This folder lives in your Cursor **user profile** — `~/.cursor/_workstream/` — not inside a project workspace, because the workboard spans every workspace you work in.

| File | Written by | Role |
|---|---|---|
| `workboard.json` | `/workboard` procedure | Canonical cross-initiative data — see `references/workboard-format.md` + `workboard-procedure.md` |
| `ba-actions.json` | `/todo`, debrief sync, `/wrap` | Canonical personal BA actions — see `references/ba-actions-format.md` |
| `ba-actions.md` | Regenerated from JSON | Human view of open/closed BA actions (do not hand-edit) |
| `regenerate-ba-actions-md.py` | After any `ba-actions.json` write | Full MD derive — run `python3 _workstream/regenerate-ba-actions-md.py` (Windows: `py`) |
| `generate-workboard-canvas.py` | `/workboard` refresh | Generates the portable interactive canvas from this BA's data |
| `roll-calendar-eod.py` | `/workboard end-of-day` step 7b | Rolls `calendar-feed.json` + `workboard.json` meetings to the next working day (mandatory at EOD; run once, never alongside `generate-workboard-canvas.py --eod-roll` — that flag already calls it) |
| `calendar-feed.json` | Your calendar script (optional) | Feeds the workboard Today tab and EOD meeting reconciliation |
| `calendar-feed.sample.json` | Reference | Example shape for optional calendar feed |

First-run **ba-setup** (or the upgrade script) seeds empty `workboard.json` and `ba-actions.json` if missing.

The workboard canvas is generated inside the active Cursor workspace's
`projects/<workspace>/canvases/` folder. It is never copied with another BA's
initiatives or action data.

**Workboard overlay upgrade:** `tools/upgrade-workboard.py` (or the zip in
`dist/ba-workboard-overlay/`) refreshes template, procedure, format, generator,
and `/workboard` command only. It does not overwrite `workboard.json`,
`ba-actions.json`, `calendar-feed.json`, or profile rules.

**Deprecated:** writing new rows to `workboard.json → personal_tasks[]`. Use `ba-actions.json`.
