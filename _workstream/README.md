# _workstream

Cross-initiative working data for BA Assistant **Version 10**.

This folder lives in your Cursor **user profile** — `~/.cursor/_workstream/` — not inside a project workspace, because the workboard spans every workspace you work in.

| File | Written by | Role |
|---|---|---|
| `workboard.json` | `/workboard` procedure | Canonical cross-initiative data — see `references/workboard-format.md` + `workboard-procedure.md` |
| `ba-actions.json` | `/todo`, debrief sync, `/wrap` | Canonical personal BA actions — see `references/ba-actions-format.md` |
| `ba-actions.md` | Regenerated from JSON | Human view of open/closed BA actions (do not hand-edit) |
| `calendar-feed.json` | Your calendar script (optional) | Feeds the workboard calendar section |

First-run **ba-setup** (or the upgrade script) seeds empty `workboard.json` and `ba-actions.json` if missing.

**Deprecated:** writing new rows to `workboard.json → personal_tasks[]`. Use `ba-actions.json`.
