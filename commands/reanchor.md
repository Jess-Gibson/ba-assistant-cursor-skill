---
description: BA Assistant — re-read orchestrator + active project state after long-thread drift
---
Run BA Assistant `/reanchor` as **resume and continue**, not a status dump.

Re-read the orchestrator and the active initiative when long-thread drift is obvious (skills not firing, status headers missing, next action forgotten) or when the user wants to pick an initiative back up.

**Read, in this order:**

1. `skills/ba-assistant/SKILL.md`
2. `skills/ba-assistant/instructions.md`
3. `skills/ba-assistant/hook-contracts.md` (inter-skill calls; do not skip)
4. Active initiative under `BA_INITIATIVES_ROOT` (default `~/.cursor/initiatives`): `SESSION-CONTEXT.md`, `status-data.json`, `initiative-tracker.md`. Path lookup: `references/workspace-operations.md`.

Then follow **SKILL.md Step 2** (resume): state validator, snapshot if available, Downloads check, re-entry card, bounded readiness pass.

**Downloads check (every `/reanchor`):** follow `workspace-operations.md` for the platform-appropriate directory listing over `BA_DOWNLOADS_PATH`. Check the **last 7 days** of files (any file type, not just `.docx`), cross-reference against what is already debriefed in SESSION-CONTEXT.md / initiative-tracker.md, and flag anything unprocessed before the re-entry card.

Confirm current work and the **single most useful next action**. If a cheap reversible artefact is grounded, prepare or draft it in the same reply (`references/proactive-assistance-protocol.md`). Do not invent work.

End with AskQuestion: continue recommended / debrief a flagged new file / re-prioritise. If no BA initiative is active in this workspace, say so - do not invent one.
