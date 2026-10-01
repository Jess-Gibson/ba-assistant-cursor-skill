---
name: ba-comms-debrief
description: Catch-up on Slack, Microsoft Teams and Outlook since the last catch-up, like a meeting debrief but from messages. Finds any update that touches an initiative (answers, decisions, confirmations, sign-offs, status changes, new asks, risks, contradictions), shows one review card, and writes to the tracker, SESSION-CONTEXT and BA actions only after the BA approves. Read-only in every communication system. Runs on /catchup, when the session hook says a catch-up is due, and at end of day with the commitment scan.
disable-model-invocation: true
---

# Skill: Comms debrief (`/catchup`)

> **Hook ids:** none. Standards: `references/comms-retrieval.md` (how to search), `references/ba-actions-format.md` (actions), `references/raid-format.md` (tracker rows).

## What it's for

Things move in text between meetings: someone answers a question, a PM says "approved", a dependency owner says "slipping to next week", a stakeholder asks the BA for something. This skill is `/debrief` for those messages. It keeps the initiative files current without the BA copying updates in by hand.

It is **not** limited to things the BA is waiting on. The watch list says what's live, so the model recognises updates quickly. Any update that touches an initiative counts.

## When it runs

| Trigger | What happens |
|---|---|
| `/catchup` | Full run, all active initiatives (or the one named: `/catchup payment retry`) |
| Session context says `CATCH-UP DUE` | On a resume or `/workboard`: run it and show the card after the re-entry card. On any other ask: answer first, then offer `/catchup` in one line. Never more than once per chat |
| `/workboard end-of-day` step 1c | Runs on the evidence commitment scan already retrieved in step 1b (no second search) |
| Start commands: `/ba-assistant`, `/reanchor`, `/workboard`, `/debrief` (after its card) | Their catch-up check (`catchup-watch.py due`) runs this when due. `/next` and `/status` only offer it |

No connectors for Slack, Teams or Outlook in this chat → say so in one line and stop. Don't guess from memory.

## Steps

### 1. Plan (script, no reading by you)

    python3 ~/.cursor/_workstream/catchup-watch.py plan            (Windows: py; add --initiative <slug> when one is named)

It returns `since` (the last catch-up, or the start of today, capped at 3 days), and per initiative: `keywords`, `ticketKeys`, `people`, and `watch` (open questions, dependencies, risks, pending decisions and sign-offs, PM approval, requirements not yet confirmed, open tracker and BA actions). Don't open the trackers yourself for this.

### 2. Retrieve

Follow `references/comms-retrieval.md`, passes 1 to 4, inside the `since` window. At end of day, skip this: use the evidence from commitment scan's retrieval.

### 3. Match each message to an initiative

Use the watch list, keywords, ticket keys, people and thread context. A message can touch more than one. A message addressed to the BA that matches no initiative goes under **Not matched** on the card (don't force it into one). Drop chit-chat, FYIs that change nothing, and anything already recorded.

### 4. Classify

| Type | Example | Proposed write (after approval) |
|---|---|---|
| **Answer** (full / partial) | Tom: "Visa and MC return categories, Amex doesn't" → OQ-007 | Tracker: answer and source on the OQ. Close only if full and explicit; partial keeps it open with the new fact |
| **Decision** | "Let's go with 3 retries" | Tracker: new or updated DEC row (who, when, source) |
| **Confirmation / sign-off** | "Happy with problem statement v1, approved" | Tracker: PM approval or sign-off register row. Requirement confirmations never change the register here: list them for `ba-requirements-interrogator` closure |
| **Status update** | "Legal review slipping to 14 Oct" | Tracker: DEP / ACT / risk row updated (date, status, note) |
| **New ask to the BA** | "[BA name], can you send the FAQ draft by Thursday?" | BA action (`sync-ba-actions`, requester in notes, permalink in source) |
| **New risk / issue / blocker** | "Scheme rules cap us at 2 retries" | Tracker: new RISK / ISS row, owner TBC unless stated |
| **Change / contradiction** | "Merchants need their own schedule, not just on/off" | Not written. Route to `ba-requirements-interrogator` (Rethink / In-flight) and flag on the card |
| **New fact** | "Support now sees 120 retry requests a week" | SESSION-CONTEXT `📝 Captured:` line with source |

Keep the confidence from the evidence record. `implied` and `context-elsewhere` never become facts: they go under **Needs you** with the question to confirm. A text reply often leans on something said out loud ("as discussed", "yep, go with that"): say what's missing rather than filling the gap.

### 5. Show the card (nothing written yet)

Same one-approval pattern as `/debrief`. One block per initiative, then the cross-cutting sections.

```
--- Catch-up: since [Wed 11:05] | [N] updates | [K] initiatives | sources: Slack, Teams, Outlook ---

[Initiative name]
WILL WRITE TO initiative-tracker.md:
  ~ OQ-007: partial answer (Tom, Slack DM 14:02): Visa and MC return categories, Amex doesn't. Stays open for Amex
  + DEC-005: Retry max 3 attempts over 5 days (Priya, #payments-retry 15:10)
  ~ PM approval, problem statement v1: approved (Priya, Slack 15:12) [explicit]
WILL WRITE TO SESSION-CONTEXT.md:
  + 📝 Captured: support volume now ~120/week (Ana, Teams 13:30)
WILL ADD BA ACTIONS:
  + Send the retry FAQ draft to Ana (due Thu 2 Oct; asked in Teams 13:30)

Needs you:
  ? Priya (email 16:00): "as discussed, let's go with option B". Which decision is option B? Not recorded until you say
  ? Requirement change for HLR-03 (Priya, Slack 15:20): routed to interrogation, not written

Not matched to an initiative:
  - [who, where, one line] → add as a BA action / ignore

Skipped sources: [none / Teams unavailable]
---
```

Then AskQuestion: **Approve all** (recommended when nothing is under Needs you) / **Review each** / **Skip this time**. Answers to "Needs you" items can be typed in the same reply.

### 6. Apply (after approval only)

- Tracker writes follow normal promotion rules (`raid-format.md`), each row carrying `source: [Slack/Teams/Outlook] [who] [date]` and the permalink where there is one.
- BA actions: `sync-ba-actions`, `source.type: comms`, then regenerate `ba-actions.md`.
- SESSION-CONTEXT: dated `📝 Captured:` lines with source.
- Frozen artefacts (anything `interrogated`, `confirmed` or marked reviewed) are never edited here. They get the review-control diff through their owning skill.
- `status-data.json` is not written here; the next `/status` picks the tracker changes up.

### 7. Stamp

    python3 ~/.cursor/_workstream/catchup-watch.py stamp            (at end of day: --by eod)

Stamp once the card is answered (approved, partly approved, or skipped). If the BA never answers it, don't stamp: the next run re-reads the same window, and dedupe keeps it clean.

### 8. Gate line

`Gate: ba-comms-debrief: PASS (N messages read, U updates proposed, A applied, Q need you)`, or `PARTIAL (Teams unavailable; Slack and Outlook read)`.

## Rules

- Read-only in Slack, Teams and Outlook. No Jira writes. No Confluence writes.
- Nothing is written before the card is approved, not even `📝 Captured:` lines.
- Never close a question, record a decision or mark a sign-off from an `implied` or `context-elsewhere` message.
- Never invent who said what: every line on the card has a source you actually read.
- Keep it quick: watch-list guided, minimal thread expansion. If the window is over a day, say so and offer to narrow to one initiative.

## Relationship to other skills

| Skill | Difference |
|---|---|
| `ba-commitment-scan` | End of day, the BA's own commitments and asks made of the BA → BA actions. This skill: any initiative update → tracker, via a review card. At end of day they share one retrieval; a new ask found by both is added once (dedupe by permalink) |
| `ba-meeting-debrief` | Same idea from a transcript. A message that says "per the meeting" points at a debrief that may not have happened yet: mention it |
| `ba-context-capture` | Captures facts the BA types in chat. This skill captures facts other people typed elsewhere |
