---
name: ba-playback-and-enablement
description: Playback materials, sign-offs, enablement. Use for playback phase in BA Assistant.
---

# Skill: Playback and Enablement

## Description

The Playback and Enablement skill ensures that the initiative is communicated clearly to stakeholders, that sign‑offs are secured at appropriate stages, and that operational teams and customers are prepared for the changes.  It helps create materials for solution playbacks, stakeholder reviews, executive updates, and training sessions.  It tracks sign‑offs and prepares documentation for deployment, training, and communications.

> **Cross-cutting rule:** This skill produces multiple artefact-class outputs (playback decks, sign-off log, comms artefacts, enablement plan, training materials, change comms drafts). Before generating outputs, apply the **"What I'll produce next" declaration** rule from `ba-assistant\SKILL.md → Co-thinking and artefact production protocol` — surface planned artefacts upfront and ask the user to select. The Communication Drafter section in this skill is invokable cross-cutting and is also prone to over-production.

## Tasks

1. **Prepare playback content** – Create concise, narrative‑driven materials (e.g., slide outlines, meeting notes) that summarise the problem, evidence gathered, feature slices, solution direction, key decisions, and next steps.  Suggest diagrams and tables where appropriate.
2. **Plan stakeholder reviews** – Identify which stakeholders need to review or approve each artefact.  Schedule playbacks and sign‑off sessions.  Provide questions to solicit feedback and uncover remaining concerns.
3. **Track sign‑offs** – Maintain a sign‑off log capturing who has approved which artefacts (requirements, solution design, backlog).  Identify outstanding sign‑offs and their impact on schedule.  Escalate if delays threaten the critical path.
4. **Enablement planning** – For operational rollout, identify training needs, process documentation updates, knowledge base articles, and user communications.  Suggest a plan for developing these materials and scheduling training sessions.
5. **Communication planning** – Work with product management and marketing to draft external messaging (if applicable) to customers about changes.  Suggest communication timelines and channels.
6. **Final RAID update** – Ensure the risk, assumptions, decisions, and dependency logs reflect all final decisions.  Highlight any unresolved items.

## Typical Questions to Ask

- What is the most compelling narrative to explain the problem, evidence, solution slices, and plan to stakeholders?  What key data or diagrams should be included?
- Who needs to review or sign off on which artefacts (e.g., PM, compliance, legal, design, engineering, operations)?  Do we have all the required approvals before starting delivery?
- Are there any outstanding sign‑offs or unresolved decisions that could block deployment?  Who is accountable?
- What training will operations/support teams need to adopt the new solution?  What materials (step‑by‑step guides, process maps, FAQs) are required?
- What changes need to be communicated to customers or end users?  When should these communications occur?  Through which channels (email, in‑app, help center)?
- Have we updated the RAID log to reflect final decisions, removed resolved assumptions, and added any new risks?  Do we need any final validation before deployment?

## Output Guidelines

The Playback and Enablement skill should produce:

- **Playback pack outline** – A structured outline for a playback meeting or slide deck, including sections: Problem & objectives, Evidence & insights, Feature slices & rationale, Solution direction & options considered, Risks & mitigations, Sequencing & critical path, Next steps & decisions required.
- **Sign‑off checklist** – A table listing artefacts (requirements, solution, backlog, compliance, design), the approver, status (Approved/Pending), date, and impact if pending.  Provide a short escalation note if a sign‑off is overdue.
- **Enablement plan** – A list of training and documentation tasks with owners, deadlines, and required materials.  Identify whether operations, support, or other teams need training and what resources will be created (e.g., updated SOPs, knowledge base articles, training sessions).
- **Communication plan** – A draft schedule for external and internal communications, indicating what needs to be communicated, to whom, by whom, through which channel, and when.  Include contingencies for negative feedback or issues.
- **Final RAID summary** – An updated risk/assumption/decision/dependency log summarising the final state before deployment.  Highlight any open items and who owns them.

## Challenge Rules

The Playback and Enablement skill should ensure smooth stakeholder engagement and rollout:

- **Clarity and brevity** – Avoid overly detailed or technical presentations; focus on telling the story and highlighting key decisions and risks.  Summarise complex information visually where possible.
- **Accountability** – For each sign‑off and enablement task, identify a clear owner.  If responsibilities are unclear, prompt the user to assign roles.
- **Timing** – Warn if sign‑offs are delayed or training is scheduled too late relative to deployment.  Suggest adjusting the timeline or prioritising activities to protect the critical path.
- **Inclusive communications** – Remind the user to consider all audiences (internal and external) and plan messaging that is appropriate for each.  Suggest early reviews with marketing or communications teams.
- **Final RAID hygiene** – Ensure the RAID log accurately reflects the final state.  Remove resolved items, clearly mark accepted risks, and assign owners to remaining open items.

---

## Communication Drafter (Wave 3 — merged from ba-communication-drafter)

This section absorbs the former `ba-communication-drafter` skill. Communication Drafter produces actual human-facing communications — not plans for them, not templates, but ready-to-send drafts: emails, Slack messages, meeting invites, status updates, escalations, change notices, sign-off requests, retrospective summaries.

> **Architectural note (Wave 3):** Communication Drafter is genuinely cross-cutting — it's invoked by 12+ skills (Discovery, Workshop Design, Risk & Tracker, Stakeholder Strategy, Requirements Interrogator in-flight, Retro, Meeting Debrief, Solution Evaluation, Sponsor Engagement, Change Strategy, DoR/Delivery Definition for MoSCoW messages, and Playback). It lives here because Playback is the highest-volume consumer of polished comms and because keeping it as a peer-level skill with so many callers was creating hook noise. **Any skill can still invoke `Communication_Drafter` as a hook** — internally, that hook now reads this section.

### Core principle

**Write the message, not a template for the message.**

Generic templated phrases ("Hope you're well, just wanted to circle back") signal that no thought went into the communication. Every message should be specific to:
- This initiative
- This audience
- This moment
- This ask

If a message could apply to any initiative, it isn't done.

### Inputs needed before drafting

Before drafting, the skill needs five things. Ask if unclear.

| Input | Why it matters |
|---|---|
| Audience | Tone, length, jargon level, decision authority |
| Purpose | Inform / request / escalate / celebrate / apologise / decide |
| Channel | Email (long-form, formal), Slack (short, casual), Teams (medium), in-person (talking points) |
| Urgency | FYI / soon / immediate — affects subject line, opening, ask |
| Relationship | Peer / manager / junior / external / first-contact — affects formality |

If the user provides only "draft a status update", ask for audience and channel before drafting.

### Tone calibration by audience

| Audience | Tone | Length | Style |
|---|---|---|---|
| Exec / senior leader | Tight, decision-focused, top-down | 3-4 sentences max | Lead with the ask, then context |
| PM / product owner | Collaborative, options-presented | 5-10 sentences | Lead with the decision needed |
| Engineering lead | Precise, technical, context-rich | As long as needed | Technical detail welcome |
| Engineering team | Practical, action-oriented | Concise | Direct, no buildup |
| Ops / support | Practical, change-impact-focused | Medium | Lead with "what changes for you" |
| External / customer | Clear, jargon-free, benefit-led | Short | Avoid internal terminology |
| First contact | Slightly more formal | Medium | More context, less assumed |

### Message types and structures

**Meeting invite:**
```
Subject: [Initiative] — [Purpose] — [Date]

[1 sentence: what this meeting is]

What we'll cover:
- [Topic 1]
- [Topic 2]
- [Topic 3]

Pre-read: [link or summary]
Outcome we're aiming for: [specific decision or alignment]

[Date/time/duration]
```

**Pre-read summary:**
```
Pre-read for [meeting name]

Context: [2-3 sentences]
What's been done: [bullets]
What we need from you: [specific asks]
Open questions: [list]

Full doc: [link]
```

**Post-meeting summary:**
```
[Meeting name] — summary and actions

What we decided:
- [Decision 1]
- [Decision 2]

Open questions to resolve:
- [Question — owner — by when]

Next steps:
- [Action — owner — by when]

Next meeting: [date or "TBD"]
```

**Stakeholder status update** — tailor format to audience tone above. Common structure:
```
[Initiative] — [Date] status

Where we are: [phase / progress signal]
What's changed since last update:
- [Change 1]
- [Change 2]

What's blocking us:
- [Blocker — owner]

What we need from you: [specific or "nothing right now"]
```

**Escalation for overdue sign-off** — firm but professional. Lead with impact, not blame:
```
Subject: [Initiative] — [Item] sign-off needed by [date]

Hi [Name],

[Item] sign-off was due [date] and is now [N] days overdue. Without it:
- [Specific impact 1]
- [Specific impact 2]

To unblock: [specific ask — review / decide / delegate]

Happy to walk through it — [proposed time].
```

**Change communication (in-flight requirement change):**
```
Subject: [Initiative] — change to [requirement / story]

[1 sentence: what changed and why]

What was agreed: [original]
What we're now proposing: [new]
Why: [reason — new info, scope clarification, user feedback]

Impact:
- [Affected story / ticket — action needed]
- [Affected design doc — update]

What I need: [confirmation / re-sign-off / discussion]
By: [date]
```

**Sign-off request:**
```
Subject: [Initiative] — sign-off needed: [Item]

Hi [Name],

[Item] is ready for your sign-off. Summary:
- [Key decision 1]
- [Key decision 2]
- [Key risk]

Full doc: [link]

Please review and confirm by [date]. Happy to walk through if useful.
```

**Risk flag:**
```
Subject: [Initiative] — risk: [short description]

Risk: [1 sentence]
Probability / impact: [H/M/L × H/M/L]
What it affects: [specific items]
Mitigation in flight: [what's happening]
What we need: [decision / resources / acceptance / nothing yet]
```

**Retro summary:**
```
[Initiative or phase] — retrospective summary

What worked:
- [Item]

What didn't:
- [Item]

What we'll do differently next time:
- [Action — owner]

Patterns for the next initiative:
- [Watchlist item]
```

**MoSCoW gap message (Wave 3):**
```
Subject: [Initiative] — MoSCoW rating needed for [stories]

Hi [PM name],

[N] stories for [scope: cohort / feature / slice] are moving into delivery but don't have a MoSCoW rating yet:
- [PROJ-XXXX — story name]
- [PROJ-YYYY — story name]

For each, can you confirm: Must / Should / Could / Won't for [scope]?

If you'd rather we proceed without ratings for now, I'll log that as an explicit decision and we'll capture it before playback.

By: [date]
```

**Slack/Teams short message:**
```
[1 line: what + who + when]
[Optional: 1 line context]
[Link or action]
```

### Drafting tasks

1. **Confirm inputs** — if audience/purpose/channel/urgency/relationship aren't clear, ask before drafting.
2. **Choose structure** — match the message type to the structures above.
3. **Calibrate tone** — apply the tone table for the audience.
4. **Pull content** — use actual content from the initiative tracker, not placeholders.
5. **Draft** — produce the full message, ready to send.
6. **Self-critique** — would this land? Is it the right length? Is the ask clear?
7. **Output** — produce the draft along with the subject line, channel recommendation, and an offer to adjust tone/length.

### Self-critique checklist (run before output)

- [ ] Is the ask clear and specific?
- [ ] Is the length right for the audience and channel?
- [ ] Is the tone right — not too formal, not too casual?
- [ ] Are there any generic phrases that should be replaced with specifics?
- [ ] Does the subject line communicate what this is about?
- [ ] Is there a clear next step?
- [ ] Would I send this if it had my name on it?

If any check fails, revise before outputting.

### Two modes

**Quick mode** — short message, clear context, audience known. Draft and output.

**Considered mode** — high-stakes message (exec update, change communication, escalation, customer-facing). Draft, self-critique, offer variants, let the user pick.

### Variants

When the user is uncertain about tone or approach, offer two variants:
- **Direct vs diplomatic** — same message, different forcefulness
- **Short vs detailed** — same message, different length
- **Formal vs casual** — same message, different register
- **Action vs FYI** — same message, different framing

Present variants side by side, let the user pick. Don't impose a tone if the user hasn't indicated preference.

### Follow-up handling

If a first message didn't get a response and the user asks for a follow-up:

1. **Wait time check** — has it been long enough? (3+ business days for email, 1 day for Slack)
2. **Escalate or remind?** — has the urgency changed?
3. **Tone shift** — second message is slightly more direct but never blames the recipient ("circling back" is fine; "you didn't reply" is not)
4. **Add value** — a follow-up should add something (new context, deadline pressure, alternative option), not just repeat

**Gentle nudge:** `Hi [Name], following up on this — is [date] still realistic for [item]? Happy to discuss if anything's blocking it.`

**Escalation-with-deadline:** `Hi [Name], [item] sign-off is now [N] days overdue. I'll need to flag this to [next-level person] by [date] if we can't get unblocked. Can we do [specific time]?`

**Re-route:** `Hi [Name], I haven't heard back on [item] — should I be looping in [alternative person]? Don't want to bypass you, just want to keep this moving.`

### Output format

For each draft:

```
To: [recipient]
Channel: [email / Slack / Teams / in-person talking points]
Subject (if email): [draft subject]

[Full message text]

Self-critique: <one line on what a reviewer might push back on>
Want to adjust? <offer variant: more direct / more diplomatic / shorter / longer>
```

For multi-stakeholder communications (same news, different audiences), produce the matrix: same message, different tones.

### Comms-specific challenge rules

- **Specific over generic** — no "I hope this finds you well", no "just wanted to circle back", no "I wanted to touch base"
- **Lead with the ask** — for exec audiences, the ask is the first sentence
- **Cut hedging** — "I think maybe we should consider possibly..." → "We should..."
- **Don't over-apologise** — one sober acknowledgement of an issue is enough
- **Right length** — most messages are shorter than people draft. Default to brief.
- **Honest about uncertainty** — when you're unsure, say so. Don't pretend confidence that isn't there.
- **Subject lines do work** — a vague subject line means the email won't be opened

### What this section does NOT do

- Does not send messages — only drafts
- Does not negotiate on the user's behalf
- Does not invent context — pulls from the tracker, requirements, decisions
- Does not produce generic templates — every draft is initiative-specific

### When to invoke the Comms Drafter (restored from pre-Wave 1)

- Kickoff Preparation (via `ba-workshop-design` Template 1) needs a meeting invite, pre-read, or post-meeting summary
- Playback and Enablement needs stakeholder communications (any of the artefacts above)
- Risk and Tracker needs overdue sign-off chase emails
- Stakeholder Strategy needs per-stakeholder engagement messages
- Requirements Interrogator (in-flight / Rethink mode) needs change communications
- Retrospective and Learning needs a retro summary
- Meeting Debrief routes actions / decisions that need to be communicated
- Solution Evaluation needs results readouts
- Change Strategy needs change comms
- User asks: "draft an email for X", "what should I say to Y", "send a message about Z"
- A decision has been made and stakeholders need to be informed

### Typical questions to ask before drafting (restored from pre-Wave 1)

- Who is this going to specifically?
- What is the primary purpose — informing them, asking them for something, flagging a risk?
- How urgent is this?
- What's the relationship — peer, manager, external?
- What channel — email, Slack, Teams?
- Is there a deadline or specific date to reference?
- Should I keep it short or include more context?

### Integration with other skills (restored from pre-Wave 1)

| Invoking skill | Communication produced |
|---|---|
| `ba-workshop-design` (Template 1 Kickoff or any workshop) | Meeting invite, pre-read summary, post-meeting summary |
| `ba-discovery-and-requirements` | Stakeholder interview invites, follow-up clarification messages |
| `ba-playback-and-enablement` (this skill's other sections) | Playback invite, executive readout, ops change notice, customer comms |
| `ba-risk-and-tracker` | Overdue sign-off chase, risk flag escalation, action-due reminder |
| `ba-stakeholder-strategy` | Per-stakeholder engagement messages |
| `ba-requirements-interrogator` (Rethink mode) | Change communications for affected tickets and stakeholders |
| `ba-retrospective-and-learning` | Retro summary, learnings broadcast |
| `ba-meeting-debrief` | Decision communications, action assignments |
| `ba-solution-evaluation` | Post-launch results readout |
| `ba-sponsor-engagement` | Sponsor briefing notes, escalations |
| `ba-change-strategy` | Change kickoff comms, stakeholder change notices |
| `ba-story-writing` (DoR MoSCoW gate) | MoSCoW gap messages to PM |

### Failure modes (restored from pre-Wave 1)

| Failure | What it looks like | Mitigation |
|---|---|---|
| Generic template language | "Hope you're well, just circling back" | Cut every phrase that could apply to any message |
| Wrong tone for audience | Technical detail to exec | Apply the tone table |
| Missing the ask | Status update with no next step | Self-critique: what is the ask? |
| Over-long | 8 paragraphs when 3 sentences would do | Default to brief, expand only if needed |
| Over-hedged | "I think we might possibly..." | Cut hedging unless uncertainty is real |
| Buried lead | The point is in paragraph 4 | Lead with the ask or the news |

### Migration note (Wave 3)

This content was previously the `ba-communication-drafter` skill. The standalone skill is now a SUPERSEDED marker; comms drafting runs as a utility section within Playback and Enablement but is invokable by any other skill via the `Communication_Drafter` hook name.


