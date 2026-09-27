---
description: BA Assistant — next actions you can actually do, scoped to this chat
---
Run BA Assistant `/next` as **do-the-work**, not a status dump.

## Scope (pick one, silently)

1. **Initiative-anchored:** this chat is re-anchored to one initiative (SESSION-CONTEXT / tracker in play, user named the initiative, `/reanchor`). Read only the tracker/session sections needed to ground the chosen next action. Use BA actions for that slug only.
2. **Cross-initiative / workboard:** this chat is a workboard update, wrap, or spans multiple initiatives. Use `_workstream/ba-actions.json` (due today, overdue, remind today, high) plus `_workstream/workboard.json` Today queue. Do not invent an initiative.

If both apply, prefer what the user last named. If unclear, AskQuestion once: this initiative vs today's open actions.

## What to output

Name **at most 3** next items, ranked by: due/remind today, blocked items today's meetings can unblock, then critical path. Label each with initiative **name**, not an internal code.

Then **start the first item in this reply**. Do not wait for a second click if the prep is cheap and grounded:

- Comms (Teams/email): write the text in the user's voice in chat for them to copy. Correct names (voice-to-text typos). Read the thread in Outlook/Glean when it exists; never create an Outlook draft or send. Flag if go-live is not confirmed yet.
- Meetings: 5-line prep + questions to ask.
- Tests/POCs: a short test plan from SESSION-CONTEXT (pass/fail, what failed last time).
- Publish/tidy: the exact files and the first concrete edit.

End with **AskQuestion** (clickable): do this first / text is ready to copy / tweak the text / skip to item 2 / pick a different focus.

## Do not

- List three analysis workstreams and stop.
- Ask "which of these three?" with no draft, plan, or message.
- Default to one particular initiative when the user is on the workboard.
- Default to workboard when the user re-anchored to one initiative.
