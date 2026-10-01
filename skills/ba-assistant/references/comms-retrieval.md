# Comms retrieval (shared by commitment scan and catch-up)

How to read the BA's Outlook, Slack and Microsoft Teams. One procedure, two users:

| Skill | Window | What it keeps |
|---|---|---|
| `ba-commitment-scan` (end of day) | The closeout day | What the BA promised, and what people asked the BA to do → BA actions |
| `ba-comms-debrief` (`/catchup`, every few hours) | Since the last catch-up (`catchup-watch.py plan` gives it) | Any update to an initiative's state → tracker, SESSION-CONTEXT, register (via review) |

At end of day, both run from **one** retrieval: search once, hand the same evidence to both skills.

## Safety (always)

- **Read-only.** Never post, reply, react, DM, forward, create a channel, move or flag mail, or mark anything read.
- Read the minimum: parent message plus snippets first; open a full thread only when those can't settle what happened.
- A message is evidence, not a decision, unless it states the decision and who made it.
- If a connector is missing or fails, say which source was skipped and carry on with the rest (`PARTIAL`).

## Retrieval sequence

Search inside the window only. Run the passes in this order and stop expanding once the picture is clear.

### 1. Addressed to the BA (always)

These are the highest-signal messages and the most often missed.

- **Outlook:** Inbox and Sent in the window. Skip notifications and auto-replies unless they change a real work item.
- **Slack:** **every** DM and group DM with a message in the window, **including ones the BA hasn't replied to** (an unanswered "can you look at this?" is exactly what this pass exists for). All @mentions of the BA. Replies in threads the BA started, replied to or reacted to.
- **Teams:** every 1:1 and group chat with a message in the window (again, including unreplied ones). Channel posts and replies where the BA is @mentioned or has replied.

Resolve the BA's own user id first where the tool needs it.

### 2. The BA's own messages

Messages the BA sent in the window (Sent mail, Slack and Teams messages authored by the BA). Look for first-person commitments: `I'll`, `I will`, `let me`, `will update`, `happy to`, `can take`, `on it`, and for questions the BA asked (which later replies may answer).

### 3. Watch-list passes (`/catchup` only)

From `catchup-watch.py plan`:

- **People:** messages from each person in `people` in channels, threads or chats the BA is in, within the window.
- **Keywords and keys:** initiative names, Jira project keys, epic and ticket keys, requirement and tracker IDs (`OQ-7`, `HLR-02`), in channels or threads the BA is in.

Never search organisation-wide conversations the BA isn't part of.

### 4. Expand only when needed

Open a thread or an email chain only when the parent plus snippets can't tell you whether something is answered, decided, done, changed or still open. Follow a link to a doc or ticket only when the message depends on it.

## Evidence record (what each kept item carries)

`source` (Slack / Teams / Outlook), `where` (channel, chat or mail subject), `who`, `when`, a short **verbatim quote**, the permalink or message id, and `confidence`:

| Confidence | Meaning |
|---|---|
| explicit | The message states it plainly ("approved", "Amex doesn't return categories") |
| implied | Reasonable reading, not stated ("sounds good" on a proposal) |
| context-elsewhere | Leans on a conversation you can't see ("as discussed", "per our call", "yep go with that", "option B") |

`implied` and `context-elsewhere` items are never applied as fact: they go on the card under **Needs you**, with the question to confirm.

## Deduplication

The same update often arrives twice (a Slack DM and an email). Keep one item, list both sources. Match to existing state by tracker ID, then BA action `source` permalink, then task fingerprint (see `ba-actions-format.md`), then initiative plus date proximity.
