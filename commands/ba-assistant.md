---
name: ba-assistant
description: Start BA Assistant. Install package files if missing, run personalisation, then choose a guided first task
---

# BA Assistant

1. If `~/.cursor/skills/ba-assistant/SKILL.md` is missing, follow
   `sub-skills/ba-install/SKILL.md` (clone
   https://github.com/Jess-Gibson/ba-assistant-cursor-skill if needed) and run
   `tools/install-ba-assistant.py --apply`.
2. Read and follow `~/.cursor/skills/ba-assistant/SKILL.md`.
3. **Catch-up check:** `py ~/.cursor/_workstream/catchup-watch.py due`. Skip this if the chat has no Slack, Teams or Outlook connectors, or `/catchup` already ran in this chat. If it says due, run `/catchup` (`ba-comms-debrief`) and show its review card before the guided first tasks, and add "Catch up on messages" as the first option.
4. Run personalisation (`ba-setup`) if `ba-assistant-config.mdc` is missing or
   still has placeholders.
5. After setup, offer guided first tasks:
   - `/workboard`
   - attach a permitted Teams transcript and `/debrief`
   - start a new initiative
   - MCP / Runlayer help

Read skills **only** from `~/.cursor/skills/ba-assistant/`. Do not search other
skill folders on the machine.
