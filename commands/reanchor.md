---
description: BA Assistant — re-read orchestrator + active project state after long-thread drift
---
Run BA Assistant `/reanchor` as **resume and continue**, not a status dump.

Re-read the orchestrator and the active initiative when long-thread drift is obvious (skills not firing, status headers missing, next action forgotten) or when the user wants to pick an initiative back up.

**Which initiative:** the name given with `/reanchor <name>` or earlier in this chat. If none, list the initiatives under `paths.initiativesRoot` (from `ba-assistant-config.mdc`) and AskQuestion which one. Never pick the most recently modified one by default.

**Read:** `~/.cursor/skills/ba-assistant/SKILL.md` and `instructions.md`, then the initiative files in the order given by **SKILL.md Step 2, item 3** (the only copy of that list).

Do not read the whole `hook-contracts.md`. If a skill names a hook id and you need its contract, open that row only.

Then follow **SKILL.md Step 2** (resume): state validator, snapshot if available, Downloads check, re-entry card, bounded readiness pass.

**Downloads check (every `/reanchor`):** follow `workspace-operations.md` for the platform-appropriate directory listing over the downloads folder (`paths.downloadsPath` in `ba-assistant-config.mdc`; `BA_DOWNLOADS_PATH` overrides). Check the **last 7 days** of files (any file type, not just `.docx`), cross-reference against what is already debriefed in SESSION-CONTEXT.md / initiative-tracker.md, and flag anything unprocessed before the re-entry card.

Confirm current work and the **single most useful next action**. If a cheap reversible artefact is grounded, prepare or draft it in the same reply (`~/.cursor/skills/ba-assistant/references/proactive-assistance-protocol.md`). Do not invent work.

**Catch-up check:** `py ~/.cursor/_workstream/catchup-watch.py due`. Skip this if the chat has no Slack, Teams or Outlook connectors, or `/catchup` already ran in this chat. If it says due, run `/catchup` (`ba-comms-debrief`) right after the re-entry card and show its review card; new answers and asks can change the next action.

End with AskQuestion: continue recommended / debrief a flagged new file / re-prioritise. If no initiative has been named and none can be confirmed, ask. Do not invent one.
