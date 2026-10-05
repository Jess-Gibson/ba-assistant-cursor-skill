---
description: "BA Assistant: catch up on Slack, Teams and Outlook since the last catch-up. Review card first, nothing written until you approve"
---
Run the BA Assistant catch-up (`~/.cursor/skills/ba-assistant/sub-skills/ba-comms-debrief/SKILL.md`) for all active initiatives, or only the one I name after `/catchup`.

1. `python3 ~/.cursor/_workstream/catchup-watch.py plan` (Windows: `py`; add `--initiative <slug>` if I named one). Use its `since` window and watch list. Don't open the trackers yourself for this.
2. Read Outlook, Slack and Teams per `references/comms-retrieval.md`, inside the window only. Read-only: never post, reply or react.
3. Find every update that touches an initiative (answers, decisions, confirmations, sign-offs, status changes, new asks to me, risks, contradictions), not only things I'm waiting on.
4. Show the catch-up review card. Nothing is written before I approve it. Anything implied, or that depends on a conversation you can't see, goes under "Needs you".
5. After I answer the card: apply what I approved, then `catchup-watch.py stamp`.

If Slack, Teams or Outlook connectors aren't available in this chat, say which and stop.
