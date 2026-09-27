# Re-entry card (BA-resume reply)

Moved out of the always-on `execution-router.mdc` (Version 15) so it is read only on resume, not on every turn. `execution-router.mdc` §7 points here; commands such as `/reanchor`, `/next`, `/workboard` add only their deltas on top of this card.

### Pre-card actions (silent)

Use what `SKILL.md` Step 2 already read (snapshot or files); do not read the same file twice.

1. Read `SESSION-CONTEXT.md` (tail 50) and `initiative-tracker.md` via Read tool (or the fresh snapshot)
2. Read `_workstream/workboard.json` for cross-initiative context
2b. Read `_workstream/ba-actions.json` — count open/blocked; note overdue. Full list: `_workstream/ba-actions.md`.
3. Read `_workstream/calendar-feed.json` for today's meetings
4. Check `CURSOR_NEW_TRANSCRIPT_COUNT` / `CURSOR_NEW_TRANSCRIPTS` (set by the sessionStart hook)
5. If the initiative has a Jira project key, run a quick Jira status delta

### Card format

```
--- Re-entry: [initiative] | [phase] | Day [N] ---

Where we are: [One sentence — last significant action + current state]
Next action: [The single most valuable thing to do right now]

Today's meetings: [count] ([names])
New transcripts: [count or "none"]
Jira delta: [tickets moved since last check, or "no changes"]
Sync status: [ok / N items unpromoted / stale pages]

---
```

Then AskQuestion: recommended next action (first, marked recommended), 2-3 alternatives, "Show full status", "Debrief [meeting]" if new transcripts.

### Cross-initiative resume

"Resume" with no initiative name → mini-workboard, then AskQuestion: which initiative, or `/workboard`:

```
--- Cross-initiative re-entry ---

Sample Initiative:            [phase] — [one-line state]
Sample Onboarding Initiative:  [phase] — [one-line state]
Sample Reassessment Initiative: [phase] — [one-line state]

Top 3 actions:
1. [highest priority task from workboard]
2. [next]
3. [next]

Today: [count] meetings | [count] new transcripts

---
```

### Non-negotiables

- Read state files BEFORE the card — never generate from memory or summary alone
- Always include the next action
- Always include AskQuestion — the card without options is a dead end
- Keep it one screen; `/status` is the deep view
- Jira delta is best-effort — "Jira: unable to check" and proceed on MCP failure
