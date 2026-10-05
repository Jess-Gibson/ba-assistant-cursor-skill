---
name: ba-commitment-scan
description: Read-only commitment scan of the user's Slack, Microsoft Teams and Outlook. Use during `/workboard end-of-day`, or when the user asks what they promised, completed, discussed, or needs captured from messages. Scan DMs, replies, @mentions and threads they reacted to. Extract commitments, decisions, completed work, risks and action changes, then update only evidence-backed local BA state. Never post or reply.
disable-model-invocation: true
---

# Skill: Commitment Scan (EOD)

## Standards used

- `references/ba-actions-format.md` — action IDs, fields, sync and regenerate rules
- `references/comms-retrieval.md`: how to search Outlook, Slack and Teams (shared with `ba-comms-debrief`). At end of day use passes 1, 2 and 4 for the closeout day (pass 3 is for `/catchup` only). Hand the same evidence to `ba-comms-debrief` in EOD step 1c instead of searching twice.

If standards conflict with skill-specific guidance below, the standard wins.

## Description

The job is to keep the local BA state honest without making the user repeat updates already visible in Slack, Microsoft Teams or Outlook. It is a reconciliation pass, not just a promise detector.

## Scope and safety

- **Read-only in communication systems:** never post, react, DM, reply, create a Teams channel, or change mail.
- Scan the closeout day by default.
- Prioritise direct messages, group DMs, replies to the user, @mentions, and threads the user replied to or reacted to. Do not read every organisation-wide conversation.
- Open source links or message permalinks only when needed to establish whether an item is open, done, changed, or ambiguous.
- Treat a message as evidence, not a final decision, unless it explicitly records the decision owner and outcome.

## Retrieval sequence

### 1. Outlook

Use the normal EOD mail triage first. Read Inbox and Sent from the closeout day.

Extract:
- new incoming asks and replies required
- the user's Sent commitments
- evidence that a previously open thread is handled, blocked or waiting

Do not treat a notification or auto-reply as an action unless it changes a real work item.

### 2. Slack

Use the connected Slack read tools.

1. Resolve the user's own Slack user id when needed.
2. Search all accessible Slack surfaces, in this order:
   - DMs and group DMs the user participated in
   - @mentions of the user
   - threads the user started, replied to or reacted to
   - channel messages only where one of those signals is present
3. Make a closeout-day pass for messages authored by the user in those high-signal surfaces.
4. Make targeted passes for first-person commitments: `I'll`, `I will`, `let me`, `will update`, `happy to`, `can take`.
5. Read a full thread only when the parent plus snippets cannot establish the outcome.

### 3. Microsoft Teams

Use Teams read tools in proportion to signal:

1. List chats and prioritise active 1:1s, group chats, direct replies and @mentions involving the user — chats where the user is a direct participant, is mentioned, or has replied or reacted, not every chat they belong to.
2. Read recent messages from those high-signal chats, including replies where available.
3. Read channel messages only when the user is mentioned, replied in the thread, reacted, or the channel is clearly an active initiative surface.
4. Inspect only the minimal surrounding thread/context required to classify an item.

Teams evidence may capture a channel created, a handoff made, a question asked, or a response that settles an action. Do not assume a channel exists or an ask was sent until it is visible in the retrieved evidence.

## Classify and reconcile

Classify each deduplicated real-world item as one of:

| Type | Meaning |
|---|---|
| Commitment | The user volunteered, promised or accepted work |
| Follow-up | The user needs to review, check, chase, create, update or revisit |
| Decision / context | A meaningful fact, decision, scope or sequencing change |
| Completion | Clear evidence an existing task is done or no longer needed |
| Watchpoint | A condition needing monitoring or escalation |
| Open question | Unresolved owner, threshold, dependency or choice |

### Update rules

Match existing actions by tracker reference, then task fingerprint, then initiative plus date proximity. A meeting the BA ran, or a thread they started, does not make another person's words evidence of the BA's commitment.

**Tier 1, apply now.** Write only when the owner is unambiguous and no inference is needed. Evidence is either:

- **BA-authored:** an exact message from the BA's account, or an observable action by them.
- **Addressed request:** a message explicitly addressed to the BA, with a concrete deliverable. It can create an action or set a due date only. It cannot mark work done or change a status.

| Change | Evidence allowed |
|---|---|
| New BA action | BA-authored or addressed request |
| Due date set or changed | BA-authored or addressed request |
| BA action marked `done` | BA-authored only |
| Reminder or notes | BA-authored only |
| Capture to `SESSION-CONTEXT.md` | Evidence allowed by the row, tagged `[unverified]` when needed |

Use the next `BA-NNN` per `references/ba-actions-format.md`. Tier 1 writes go through `ba-actions.py` and `capture.py`. Before the first Tier 1 write, snapshot the initiative. Regenerate `_workstream/ba-actions.md` once at the end.

**Tier 2, review card.** Propose only. Write these to `_workstream/eod-staged-commitments.json` and apply them only after BA approval:

- Changes to a decision, requirement, approval, sign-off, priority, scope or RAID status.
- Marking an action `cancelled`.
- Promoting anything to the tracker.
- Actions owned by someone else, unclear ownership, implied agreement, reactions, or conflicting messages.

Write the staged file atomically. At the start of end of day, carry forward items from an earlier run. After the review card, remove only approved or rejected items. Cancel or failure leaves the file intact. Never sync this file.

## Output

Show the exceptions first, then a compact reconciliation table:

| Item | Source | Type | State change | Next action |
|---|---|---|---|---|

Use source permalinks or Outlook subjects where available. Include resolved items only when they change existing state. Do not pad the table with FYIs.

Then print:

`Gate: ba-commitment-scan: PASS (N evidence items, A actions added, U actions updated, C captures)`

or a partial result such as:

`Gate: ba-commitment-scan: PARTIAL (Teams unavailable; Slack and mail reconciled)`

## EOD integration

Run after mail triage and before meeting reconciliation. Its updates are inputs to the later action runthrough, SESSION-CONTEXT promotion, workboard refresh and next-day prep. See `references/eod-closeout-procedure.md` for the full sequence.

## Working-hours rule for any focus block found during reconciliation

This skill never books anything. It may propose focus blocks. End of day books them automatically only when the BA's working-preferences file in `_workstream/` has `autoBookFocus: true`; otherwise after the BA confirms. Read that preferences file first. Focus blocks must stay within configured working hours, avoid lunch, and sit in a free calendar gap unless the BA explicitly asks for an exception. The end-of-day step checks live Outlook immediately before it creates or updates an event.
