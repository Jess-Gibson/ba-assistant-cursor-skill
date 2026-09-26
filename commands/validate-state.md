---
description: BA Assistant — write what this chat captured into the initiative files and ba-actions
---
Run the BA Assistant /validate-state command using `~/.cursor/skills/ba-assistant/sub-skills/ba-state-validator/SKILL.md`.

`/validate-state` checks this whole chat against the current initiative files and captures anything missing, so a new chat can pick up with nothing lost. Write what this chat decided, learned or produced into the right files: `SESSION-CONTEXT.md`, the tracker, and `status-data.json` where those files already exist, and upsert the BA actions that came from this chat into `~/.cursor/_workstream/ba-actions.json`. Then re-read those files and confirm they match the chat. Do not refresh the workboard. Do not walk every open action. Do not invent files. If something has no obvious home, say so and ask.

Steps:

1. **Scan the chat.** List every decision, risk, assumption, open question, dependency, requirement change, action, and output from this chat.
2. **Compare with the files.** For each item, check whether `SESSION-CONTEXT.md`, the tracker, `status-data.json` or `ba-actions.json` already has it.
3. **Write what is missing** to the right file. Promote clear `DEC-` / `RISK-` / `OQ-` / `ACT-` / `DEP-` items to the tracker and tag them `[promoted]`.
4. **Sync actions.** Upsert this chat's BA actions, regenerate `~/.cursor/_workstream/ba-actions.md` (`python3 ~/.cursor/_workstream/regenerate-ba-actions-md.py`; on Windows use `py`), and print `Gate: ba-actions-sync: PASS/FAIL`.
5. **Report.** A short table: item, where it now lives. Then anything still uncertain, and one line: `Safe to start a new chat: yes` (or `no`, with what is missing).

This is not end of day.
