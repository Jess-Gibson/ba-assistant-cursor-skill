---
name: ba-meeting-debrief
description: Process a meeting (transcript, notes, or recall) into structured updates — decisions, actions, open questions, new/changed requirements, RAID items. Routes updates to the right specialist skills and updates the living tracker. Callable from any phase.
---

# Skill: Meeting Debrief

## Description

The Meeting Debrief skill captures the value of a meeting and propagates it through the BA Assistant's living tracker and specialist skills. It can be invoked **any time** — meetings happen across all phases (kickoffs, discovery workshops, solution review, sprint planning, stakeholder check-ins, sponsor 1:1s, retros, ad-hoc syncs).

The skill exists because the most expensive failure mode after a meeting is **not capturing the information**: decisions get forgotten, action items get dropped, new requirements get assumed instead of interrogated, RAID items don't get logged, and the next meeting starts by re-relitigating last meeting's outcomes. Conversations where work actually happens get lost.

This skill is **proactive**. When the user signals a meeting has happened (verbally, by sharing a transcript, by saying "I just got out of…"), or when the orchestrator notices a meeting day in available context, this skill should prompt to debrief — it should not wait to be explicitly invoked.

## When to invoke

- **User shares a meeting transcript** (Zoom, Teams, Otter, Fireflies, manual notes)
- **User mentions a meeting just happened** ("I just had a sync with…", "Coming out of the workshop…", "Spoke to the sponsor and…")
- **User mentions a meeting tomorrow** (pre-meeting prep — preview agenda, surface decisions needed)
- **Calendar context shows a meeting day** (if the user has shared calendar context with the assistant)
- **Orchestrator notices a gap** — last 1:1 with sponsor was 3 weeks ago and the cadence is fortnightly; prompt the debrief skill ahead of the next session
- **Recurring meeting day patterns** — The user's meeting patterns may cluster on certain days; pre-emptively offer the debrief flow when calendar context suggests heavy meeting days
- **Session start / resume** — always check `the user's configured downloads path (set via BA_DOWNLOADS_PATH environment variable, or the OS default Downloads folder)` for `.docx` files newer than the last session (see `workspace-operations.mdc` Downloads Check (downloads path is configurable via BA_DOWNLOADS_PATH or OS default)). The user downloads transcripts after meetings and expects them processed without being asked. **Do not assume there are no files — always check.**

## Trigger phrases (proactively detect these)

- "I just had a [meeting/sync/workshop/1:1/standup/retro/playback/refinement] with…"
- "Coming out of [meeting name]…"
- "The [stakeholder name] meeting just happened…"
- "Here's the transcript from…"
- "Notes from the meeting:"
- "We met about…"
- "I just got off a call with…"
- "Quick debrief on the [meeting]…"

When any of these appear, propose: *"Want me to run this through the meeting debrief — extract decisions, actions, open questions, new/changed requirements, and update the tracker?"*

## Tasks

1. **Capture the meeting context** — Before extracting anything, confirm:
   - Meeting name / purpose
   - Date and time
   - Attendees (names + roles)
   - Phase / scope this relates to (initiative-wide, feature-specific, cohort/slice-specific)
   - Format (workshop / 1:1 / standup / playback / refinement / retro / ad-hoc)
   - Source of the input (transcript / notes / verbal recall / agenda only)

2. **Ingest the input** — Accept the input in whatever form provided:
   - Full transcript → process verbatim, attribute statements to speakers
   - Notes → process as user-curated summary (less attribution, more reliable on outcomes)
   - Verbal recall → guide with structured prompts to extract the same categories
   - Mixed → treat each section appropriately

3. **Scan Miro board for session content (when applicable)** — If a Miro board was used during the session:
   - Read every relevant frame using `layout_read` — not just topic-level scan but item-level content
   - Look for stickies, cards, text, and shapes added during the session that may NOT appear in the transcript (participants type on Miro without speaking)
   - Cross-reference Miro content against transcript — anything on the board but not in the transcript is a capture gap
   - Cross-reference transcript against Miro — anything discussed but not on the board is a documentation gap
   - Surface both gaps to the user before extraction

   **Anti-pattern:** Claiming "no new info on the board" after a topic-level scan. Topic coverage ≠ item coverage. Every sticky, card, and text item must be individually assessed.

4. **Track attendance and participation** — Before extracting content, note:
   - Who was present for the full session
   - Who joined late (and what they missed)
   - Who left early (and what happened after they left)
   - For anyone who left early: create a mandatory catch-up action tied to their domain areas that were discussed after departure
   - For anyone absent who was expected: note what they missed and whether a briefing is needed

5. **Extract structured items** — Pass through the transcript / notes and surface, with quote/source where possible.

   ### Action taxonomy (5 types — all mandatory to scan for)

   | Type | What to look for | Examples |
   |---|---|---|
   | **Explicit actions** | Formal commitments with owner | "[PM Name] to set up the pricing meeting", "[Team Member] will send the screenshots" |
   | **Decisions** | Explicit choices made | "We decided X", "Let's go with Y", "Agreed that Z" |
   | **Open questions** | Questions raised without answers | Unanswered questions, "we need to find out…" |
   | **Soft commitments** | Implied follow-ups phrased as discussion | "We should probably book that in", "We need to have a chat with reporting", "Let's plan that for week 2" |
   | **Direct-to-assistant instructions** | Participants asking the tool/assistant to track something | "Hopefully cursor can catch it", "Note that down", "Can you get that?" |

   **Critical:** Types 4 and 5 are the most commonly missed. They sound like conversation, not action items. Scan for these patterns explicitly:
   - "we should…" / "we need to…" / "let's…" / "we'll have to…" / "I'll probably…"
   - "cursor can…" / "note that" / "add that to…" / "track that" / "catch that"

   ### Other extraction categories

   | Category | What to look for |
   |---|---|
   | **Decisions deferred** | "We'll decide later", "Need more info before deciding", "Park this" |
   | **New requirements / changes** | Anything that sounds like "we need to also…", "actually we should…", "what if it also did…" |
   | **RAID items** | New risks, assumptions, issues, dependencies surfaced |
   | **Sentiment / sponsor signal** | If sponsor present — engagement level, surprises, concerns, signs of waning interest |
   | **Stakeholder concerns** | Pushback, resistance, alignment gaps |
   | **Cross-cutting topics** | Compliance, legal, security, ops impacts mentioned |
   | **Followups for other people** | Things that need to go to people not in the meeting |
   | **Contradictions** | Where speakers disagree — surface, don't smooth over |
   | **Knowns confirmed** | Facts established during the session that should be logged as K-items |

4. **Route updates to specialist skills (mandatory)** — Each extracted item gets routed:

   | Extracted item | Routed to |
   |---|---|
   | New requirement or requirement change | `ba-requirements-interrogator` (Discovery mode for new; Rethink/In-flight mode for changes) |
   | Decision made | `ba-risk-and-tracker` decisions log (include who decided, when, status) |
   | Action item | `ba-risk-and-tracker` (action register) + Communication_Drafter (if a follow-up message is needed) |
   | Open question | `ba-risk-and-tracker` unknowns log |
   | New risk / assumption / dependency | `ba-risk-and-tracker` RAID |
   | Sponsor signal | `ba-sponsor-engagement` (update sponsor profile + recent engagement notes) |
   | Change strategy / adoption signal | `ba-change-strategy` (audience concerns, resistance signals) |
   | Stakeholder dynamics | `ba-stakeholder-strategy` (update stakeholder grid) |
   | Anti-pattern observed | `ba-anti-pattern-detector` watchlist update |
   | Solution evaluation evidence (post-launch meetings) | `ba-solution-evaluation` |

   **Important:** the debrief skill does not modify other skills' artefacts directly. It produces a routing report — "here's what I extracted, here's where each item should land" — and either invokes the relevant skill or hands off to the orchestrator to do so. This keeps each skill the owner of its own artefacts.

7. **Cross-reference against existing tracker** — Before updating, compare every extracted item against what's already tracked:
   - Read the living tracker (initiative-tracker.md or equivalent)
   - For each extracted item: is it already tracked? If yes, does the meeting change its status, owner, or detail?
   - Flag duplicates (already tracked and unchanged) — don't re-add
   - Flag updates (already tracked but status/detail changed) — update, don't duplicate
   - Flag net-new items — these are the additions
   - Surface the net-new and updated items to the user for confirmation before writing

8. **Question-to-action gap check** — For every open question extracted:
   - Does an action exist to answer it? (Who will find out? By when?)
   - If not, create a paired action: "Reach out to [person] re: [question]" or "Investigate [topic] to resolve [question]"
   - A question without a corresponding action is a tracking gap — the question documents what we need to know, the action documents who will go find out

9. **Update the living tracker** — Apply the routed items to the tracker (decisions table, RAID, OQ log, action register, sponsor decisions log). Each entry carries the source: meeting name + date + attendees + (where applicable) speaker.

10. **Surface "before next meeting"** — Identify anything that must happen before the next scheduled meeting with the same group:
   - Decisions that need pre-confirmation
   - Actions due
   - Open questions that need answers
   - Artefacts to share
   - Pre-reads to send

11. **Draft post-meeting summary** — Hand off to `Communication_Drafter` (or `Playback_and_Enablement` if merged) to draft:
    - Internal Slack post / email recap to attendees + non-attendees who need to know
    - Sponsor briefing (if sponsor not in the meeting)
    - Stakeholder updates (if relevant)
    - Action item DMs to owners

12. **Detect requirement changes in-flight** — If extracted items reveal a requirement change, automatically invoke `ba-requirements-interrogator` in **Rethink** or **In-flight** mode (depending on whether dev has started). Don't silently absorb scope creep through meeting notes.

13. **Detect anti-patterns** — Watch for and flag during the debrief:
    - Decisions made by people without decision rights (vs. RACI)
    - Requirements being added without interrogation
    - Action items with no owner
    - Action items with no date
    - Open questions that have been open across multiple meetings (rotting)
    - Sponsor absent from a meeting where they had decisions to make
    - Same topic being re-discussed without progress
    - **Soft commitments not captured** — "we should…" / "we need to…" used in transcript but no corresponding action in the debrief
    - **Partial attendance without catch-up action** — someone left early and their domain was discussed after departure
    - **Questions without paired actions** — OQ logged but no action to find the answer

14. **Generate a Pre-meeting brief (when invoked ahead of a scheduled meeting)** — If the user signals a meeting is upcoming, run in reverse:
    - Pull recent decisions, actions, open questions related to the attendees / topic
    - Surface what's outstanding from the last meeting with this group
    - Identify decisions needed at this meeting
    - Propose an agenda
    - Draft a pre-read for sponsor / key attendees if appropriate

## Typical Questions to Ask

### When the user shares a meeting / transcript

- What meeting was this? Who attended?
- What was the purpose / intended outcome?
- Did the meeting achieve its purpose, or did something change?
- Were there any surprises — things that came up that weren't on the agenda?
- Was the sponsor present? How did they engage?
- Did anything change about scope, priority, or requirements?

### When extracting items

- Is this action item really an action, or just a discussion point? Who owns it? By when?
- Is this a decision or a preference?
- Is this requirement new, or a change to an existing one?
- Did this risk just appear, or was it always there and we now see it?
- Is the meeting outcome consistent with what's already in the tracker, or is there a conflict?

### When detecting drift

- This requirement was logged differently last week — did it change, or did our understanding change?
- This action has been listed in the last three meetings unactioned — is it real, or should it be dropped?
- The sponsor has been absent from the last two sessions where decisions were needed — should we escalate or change cadence?

## Output Guidelines

### Meeting debrief report

```
Meeting: [name]
Date / time: [date], [time]
Attendees: [names + roles — note who joined late / left early]
Phase / scope: [phase, feature, cohort, slice]
Source: [transcript / notes / verbal / Miro board]

ATTENDANCE
| Person | Role | Status | Notes |
| ... | ... | Full / Late / Left early / Absent | What they missed, catch-up action needed? |

MIRO BOARD SCAN (if applicable)
| Frame | New items found | In transcript? | Tracker action |
| ... | ... | Yes / No | Add / Already tracked / Needs discussion |

DECISIONS MADE
| Decision | Decider | Date | Status | Logged in |
| ... |

DECISIONS DEFERRED
| Topic | Why deferred | When revisit | Owner |
| ... |

ACTION ITEMS (all 5 types)
| # | Type | Action | Owner | Due | Status | Source quote |
| ... | Explicit / Soft commitment / Direct-to-assistant / Decision follow-up / Catch-up | ... | ... | ... | ... | ... |

OPEN QUESTIONS (with paired actions)
| Question | Who can answer | Priority | Action to resolve | Action owner |
| ... |

NEW / CHANGED REQUIREMENTS
| Requirement (provisional) | New or Changed | Routed to | Interrogator mode |
| ... |

KNOWNS CONFIRMED
| Known | Source / speaker | Tracker ID (if existing) |
| ... |

RAID UPDATES
| Type | Item | Severity | Owner |
| ... |

CROSS-REFERENCE (against existing tracker)
| Extracted item | Already tracked? | Status change? | Action |
| ... | Yes (ID) / No | Changed / Unchanged | Update / Add / Skip |

SPONSOR / STAKEHOLDER SIGNALS
- ...

CROSS-CUTTING IMPACTS (compliance / legal / security / ops)
- ...

ANTI-PATTERNS OBSERVED
- ...

BEFORE NEXT MEETING WITH THIS GROUP
- ...
```

### Post-meeting comms (handed off to Communication_Drafter)

- Recap email / Slack post to attendees + selected non-attendees
- Action item DMs to owners with clear ask + date
- Sponsor briefing if not in attendance
- Stakeholder updates as appropriate

### Pre-meeting brief (when run ahead of a scheduled meeting)

```
Meeting: [name]
Date / time: [date], [time]
Attendees expected: [names]

OUTSTANDING FROM LAST MEETING
| Item | Owner | Status |

DECISIONS NEEDED THIS MEETING
| Decision | Driver | Pre-brief needed? |

PROPOSED AGENDA
1. ...

PRE-READ DRAFT (for sponsor / key attendees)
[content]
```

## Challenge Rules

- **Don't extract silently** — show the extracted items back to the user for confirmation before routing. Misattributed quotes or wrong decisions captured in the tracker are very expensive to fix.
- **Don't smooth over disagreement** — if the transcript shows two people disagreed and the disagreement wasn't resolved, surface it. Don't pick one and call it "the decision".
- **Don't accept actions without owner + date** — flag and ask. "Action: [name] to think about it" is not an action.
- **Don't let requirements slip in unannounced** — anything that looks like a new or changed requirement triggers `ba-requirements-interrogator`. No exceptions.
- **Don't silently absorb scope creep** — if a meeting added scope, flag it and route to Requirements Interrogator (Rethink/In-flight). The fact that the addition happened verbally is not a reason to skip interrogation.
- **Don't ignore sponsor absence** — sponsors missing decision moments is a 🧨 risk, not neutral. Surface.
- **Don't bury contradictions** — if the meeting outcome conflicts with what's in the tracker, raise it. Don't quietly overwrite.
- **Don't post a summary the user hasn't seen** — communication drafts go to the user for approval before sending.
- **Don't process every meeting at full depth** — small status standups don't need the full debrief flow. Match depth to meeting weight (1:1 with sponsor = full; daily standup = action items + blockers only).
- **Don't claim "nothing new on the board" without item-level verification** — topic-level Miro scans miss specific stickies, cards, and text items. Read every item in the frame.
- **Don't log a question without a paired action** — "Q: What's the reporting impact?" is incomplete without "Action: [BA Name] to check with reporting team". The question documents the gap; the action fills it.
- **Don't skip soft commitments** — "we should probably book a session for that" IS an action, just not a formal one. Surface it, propose an owner and date, confirm with the user.
- **Don't ignore early departures** — someone leaving at minute 30 of a 120-minute session means 75% of the content needs a catch-up. Create the action.
- **Don't treat direct-to-assistant instructions as background noise** — "hopefully cursor can catch it" or "can you note that" is a first-class instruction. Track it as an action with the assistant as owner.

## Integration with BA Assistant

**Mode (post-Wave 3):** Cross-cutting capability — runs across all scopes and modes. Event-driven, not phase-bound.

**Pre-Wave 3 (current sequential model):** Invoked at any phase whenever a meeting happens. Most active at Phases 1, 2, 4, 6 (kickoffs, discovery workshops, solution review, playback) and post-launch (evaluation reviews, sponsor checkpoints).

**Hooks called by this skill (mandatory routing):**
- `ba-requirements-interrogator` (Discovery for new requirements; Rethink/In-flight for changes)
- `ba-risk-and-tracker` (decisions, RAID, open questions, action register)
- `ba-sponsor-engagement` (sponsor signal, sponsor decision log)
- `ba-change-strategy` (audience concerns, resistance signals)
- `ba-stakeholder-strategy` (stakeholder dynamics)
- `ba-anti-pattern-detector` (patterns observed)
- `ba-solution-evaluation` (post-launch meeting evidence)
- `Communication_Drafter` (post-meeting summary, action DMs, sponsor briefing)

**Hooks calling this skill:**
- Orchestrator when trigger phrases detected
- Kickoff Preparation post-meeting
- Playback & Enablement post-playback
- Sponsor Engagement after sponsor 1:1
- User direct invocation ("debrief this meeting")
- `/status` if it detects a recent meeting wasn't debriefed

**Living tracker updates:** decisions, RAID, action register, open questions, sponsor signals, stakeholder dynamics, change signals, source meeting per item.

**Anti-pattern this skill prevents:** "The meeting was the work" — valuable conversations happened, decisions were made, requirements were changed, RAID items surfaced, and none of it made it into the tracker. The next meeting starts by re-litigating the last. Compounds over a multi-month initiative until the team is doing change management in their heads and decisions are being made twice.
