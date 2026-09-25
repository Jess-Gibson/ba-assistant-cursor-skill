---
name: ba-commitment-scan
description: Read-only commitment scan of the user's Slack, Microsoft Teams and Outlook. Use during `/workboard end-of-day`, or when the user asks what they promised, completed, discussed, or needs captured from messages. Scan DMs, replies, @mentions and threads they reacted to. Extract commitments, decisions, completed work, risks and action changes, then update only evidence-backed local BA state. Never post or reply.
---

# Skill: Commitment Scan (EOD)

## Standards used

- `references/ba-actions-format.md` — action IDs, fields, sync and regenerate rules

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

1. Match existing actions by tracker reference, then task fingerprint, then initiative plus date proximity.
2. Create an action only for an owned, concrete next step. Use the next `BA-NNN` per `references/ba-actions-format.md`.
3. Update a due date, reminder, source link or notes when supported by evidence.
4. Mark `done` only on explicit completion evidence. Mark `cancelled` only when the work is explicitly dropped.
5. If evidence conflicts or does not identify ownership, keep the action open and add a short evidence note or capture an open question.
6. Append an attributed, dated `📝 Captured:` entry to the appropriate `SESSION-CONTEXT.md`.
7. Promote unambiguous material RAID items through the ordinary EOD promotion process. Do not change reviewed or confirmed requirements without the normal review-control diff and approval.
8. Regenerate `_workstream/ba-actions.md` after any JSON mutation.

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

Read the user's working-hours preferences file in `_workstream/` before proposing or booking a focus block, if one exists. Focus blocks must stay within the user's configured working hours, avoid the protected lunch window, and sit only in a free calendar gap with no existing meetings, unless the user explicitly asks for an exception. Check live Outlook immediately before creating or updating an event.
