---
description: BA Assistant — process a meeting transcript into decisions, actions, risks, tracker updates
---
Run the BA Assistant meeting debrief (~/.cursor/skills/ba-assistant/sub-skills/ba-meeting-debrief): find the newest unprocessed transcript (CURSOR_NEW_TRANSCRIPTS / BA_DOWNLOADS_PATH) or ask me to paste one, auto-detect the initiative, extract decisions, actions, open questions, requirement changes and RAID, and route each to the right skill and the tracker.

**Review first, then apply:** show the complete proposed changes and the batch update ("WILL WRITE TO...") card in chat before asking for approval. Never write canonical files before the card is approved.

**Downloads (debrief only — not the full folder):** skip the orchestrator resume 7-day Downloads check. If a transcript path was attached, **do not scan Downloads** — use that path only. Otherwise follow the debrief sub-skill's 3-day Downloads triage (`workspace-operations.md` for the platform-appropriate listing, `BA_DOWNLOADS_PATH`).

**Catch-up check** (after the debrief card is answered): `python3 ~/.cursor/_workstream/catchup-watch.py due` (Windows: `py`). Skip this if the chat has no Slack, Teams or Outlook connectors, or `/catchup` already ran in this chat. If it says due, run `/catchup` (`ba-comms-debrief`) next: messages after a meeting often add to it. Skip anything the debrief just wrote.

**Docx sources:** follow the debrief sub-skill's docx ingestion section — never nested `powershell -Command`, nested `powershell -File`, or `Expand-Archive` for `.docx`.
