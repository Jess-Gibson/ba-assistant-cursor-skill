---
name: ba-meeting-debrief
description: Process a meeting (transcript, notes, or recall) into structured updates  -  decisions, actions, open questions, new/changed requirements, RAID items. Routes updates to the right specialist skills and updates the living tracker. Callable from any phase.
---

# Skill: Meeting Debrief

## Description

The Meeting Debrief skill captures the value of a meeting and propagates it through the BA Assistant's living tracker and specialist skills. It can be invoked **any time**  -  meetings happen across all phases (kickoffs, discovery workshops, solution review, sprint planning, stakeholder check-ins, sponsor 1:1s, retros, ad-hoc syncs).

The skill exists because the most expensive failure mode after a meeting is **not capturing the information**: decisions get forgotten, action items get dropped, new requirements get assumed instead of interrogated, RAID items don't get logged, and the next meeting starts by re-relitigating last meeting's outcomes. Conversations where work actually happens get lost.

This skill is **proactive**. When the user signals a meeting has happened (verbally, by sharing a transcript, by saying "I just got out of…"), or when the orchestrator notices a meeting day in available context, this skill should prompt to debrief  -  it should not wait to be explicitly invoked.

## When to invoke

- **User shares a meeting transcript** (Zoom, Teams, Otter, Fireflies, manual notes)
- **User mentions a meeting just happened** ("I just had a sync with…", "Coming out of the workshop…", "Spoke to the sponsor and…")
- **User mentions a meeting tomorrow** (pre-meeting prep  -  preview agenda, surface decisions needed)
- **Calendar context shows a meeting day** (check `_workstream/calendar-feed.json` for today's meetings)
- **Orchestrator notices a gap**  -  last 1:1 with sponsor was 3 weeks ago and the cadence is fortnightly; prompt the debrief skill ahead of the next session
- **Recurring meeting day patterns**  -  the BA's pattern shows certain days have most meetings (Tuesdays/Wednesdays typically); pre-emptively offer the debrief flow
- **Session start / resume**  -  check `CURSOR_NEW_TRANSCRIPTS` env var (set by session-init hook) for unprocessed files in Downloads and `[org shared drive / recordings folder]\Recordings`. [BA name] downloads transcripts after meetings and expects them processed without being asked.
- **User says "debrief"**  -  find the newest transcript across Downloads and Recordings, auto-detect initiative, and process

## Trigger phrases (proactively detect these)

- "I just had a [meeting/sync/workshop/1:1/standup/retro/playback/refinement] with…"
- "Coming out of [meeting name]…"
- "The [stakeholder name] meeting just happened…"
- "Here's the transcript from…"
- "Notes from the meeting:"
- "We met about…"
- "I just got off a call with…"
- "Quick debrief on the [meeting]…"

When any of these appear, propose: *"Want me to run this through the meeting debrief  -  extract decisions, actions, open questions, new/changed requirements, and update the tracker?"*

## Auto-initiative detection

When the user says "debrief" without specifying an initiative, the skill must detect which initiative(s) the meeting relates to. This removes the friction of having to specify context every time.

### Detection procedure

1. **Check transcript content**  -  Scan the transcript/notes for initiative markers:
   - **Sample Initiative / fee overlay / scheme fee / blocking / cohort / NP / Sample Payments Product / ARL** → Sample Initiative
   - **Data Collection / Business Verification / [vendor] / stale draft / data minimisation / verification / identity** → Data Collection
   - **sample-reassessment-initiative / telemetry / bug bash / auto-approval / OSP / support tool** → sample-reassessment-initiative
   - **Multiple matches** → tag as cross-initiative, list which initiatives are touched

2. **Check calendar match**  -  Read `_workstream/calendar-feed.json`. Match the meeting subject against:
   - Known recurring meetings (Standup = all initiatives; Sample Product Tier = cross-initiative)
   - Attendee overlap with initiative stakeholders ([Team Member]/[Team Member]/[Tech Lead] = Data Collection; [Team Member]/[Team Member]/[Team Member] = Sample Initiative; [Team Member]/[BA name] Lee/[Team Member] = sample-reassessment-initiative)
   - Meeting subject keywords (same markers as above)

3. **Confirm with user (once)**  -  Present the auto-detected initiative(s) and ask to confirm:
   ```
   Detected: This looks like a Data Collection meeting (mentions [vendor], [Team Member], stale drafts).
   [Correct - proceed with Data Collection] [Actually it's Sample Initiative] [Cross-initiative] [Let me specify]
   ```
   If the user has already stated the initiative in their message, skip this confirmation.

4. **Load initiative context**  -  Once confirmed, read:
   - `blueprints/{slug}/SESSION-CONTEXT.md` (tail 50 lines)
   - `blueprints/{slug}/initiative-tracker.md` (if it exists)
   - `blueprints/{slug}/status-data.json` (if it exists)
   
   This ensures the cross-reference step (Task 7) has the current tracker to compare against.

## Batch routing (one-approval flow)

Instead of asking for approval at each routing step, the debrief produces a **single batch update card** after extraction. This is the biggest time-saver -- one review, one approval, all files updated.

### Batch update card format

After extraction is complete, present everything in one card:

```
--- Debrief: [meeting name] → [initiative] ---

WILL WRITE TO SESSION-CONTEXT.md:
  + DEC-XX: [decision text] (decider: [name], date: [date])
  + OQ-XX: [open question]
  + A-XX: [action] (owner: [name], due: [date])
  + RISK-XX: [risk text]

WILL UPDATE initiative-tracker.md:
  ~ Updated: DEC-15 status changed from "pending" to "confirmed"
  + New: RISK-042 [description]
  - Closed: OQ-12 (answered in this meeting)

WILL UPDATE status-data.json:
  ~ Feature B status: "not started" → "in progress"

WILL FLAG FOR CONFLUENCE:
  ! Status page is 3 days stale  -  mark for update

PERSONAL TASKS (→ _workstream/workboard.json):
  + Chase [person] re: [topic] by [date]
  + Send pre-reads for next session

COMMS TO DRAFT (after approval):
  - Recap to attendees
  - Catch-up brief for [person who left early]

Options:
  [Approve all]  -  write everything now
  [Show me the details]  -  expand each item before approving
  [Edit before approving]  -  let me modify items
  [Approve writes, skip comms]  -  update files but don't draft messages
```

Use AskQuestion to present options. On "Approve all", execute all writes in sequence:
1. Append to SESSION-CONTEXT.md
2. Update initiative-tracker.md
3. Update status-data.json (if changes)
4. Add personal tasks to `_workstream/workboard.json`
5. Trigger sync gate check (per `sync-gates.mdc`)
6. Offer to draft comms

### Cross-initiative debriefs

If a meeting touches multiple initiatives (e.g. a program-level sync), the batch card groups updates by initiative:

```
--- Cross-initiative debrief: [meeting] ---

Sample Initiative updates:
  + DEC-XX: ...
  + A-XX: ...

Data Collection updates:
  + OQ-XX: ...
  + RISK-XX: ...

Cross-cutting:
  + Personal task: ...
```

Each initiative's files are updated separately. The sync gate runs for each affected initiative.

## Downloads triage (debrief only  -  3 days, not full folder)

**Do not** run the orchestrator resume Downloads check (`cmd /c dir ... /o-d` over the whole folder, 7-day mental filter). That is for `/workboard`, `/reanchor`, and resume only.

| Situation | What to run |
|---|---|
| User attached `@` path(s) or named file(s) in the message | **Skip Downloads scan.** Use those paths only. |
| User said "debrief" with no file  -  find newest transcript | 3-day scoped list only (below) |
| User said "debrief [initiative]" with no file | 3-day scoped list only, then auto-detect from filenames + content |

**Command (mandatory when scanning is needed):**

```powershell
& "$env:USERPROFILE\.cursor\_workstream\list-downloads-recent.ps1" -Days 3
```

The script uses `cmd /c dir` internally (sorted newest-first) and stops when files are older than 3 days. Typical result: ~10 files, not 100+.

**Never during debrief:** `cmd /c dir "[Downloads folder - set BA_DOWNLOADS_PATH]" /a-d /o-d` (full folder).

Cross-reference the 3-day list against SESSION-CONTEXT / tracker for what's already debriefed. Prefer transcript-like files (`.docx`, `.vtt`, `.txt`) when auto-picking "newest unprocessed".

**No Shell for JSON/workboard:** Read `ba-actions.json` (canonical) or `workboard.json` only for initiative context. Never write `tmp-workboard-filter.ps1` or similar.

## Docx transcript ingestion (mandatory  -  agent Shell)

The Read tool **cannot** open `.docx`. When the source is a Word transcript (Downloads, `@` attachment, or path in the user message), **never** use nested `powershell -Command`, inline `$path`/`$zip`/`$xml` variables, or `Expand-Archive` in Shell.

**Always run this exact pattern** (replace paths only). Cursor's shell is **already PowerShell**  -  use direct call (`&`), not nested `powershell -NoProfile -File`:

```powershell
& "$env:USERPROFILE\.cursor\_workstream\extract-docx-text.ps1" -DocxPath "FULL_PATH_TO.docx" -OutPath "$env:USERPROFILE\.cursor\_workstream\debrief-extract-SLUG.txt"
```

**Before Shell:** `Test-Path` the `-OutPath`. If the text file exists and is newer than the docx, **skip extraction** and Read the out file directly.

| Canonical outputs (Sample Initiative 17 Jul debrief) | Path |
|---|---|
| Arthur no-regrets transcript | `_workstream\debrief-extract-rba-noregrets-17jul.txt` |
| ARL scope transcript | `_workstream\debrief-extract-arl-scope.txt` |

Then **Read** the `-OutPath` text file and debrief from that.

| Need | Script |
|---|---|
| Text for debrief (default) | `_workstream\extract-docx-text.ps1` |
| Unzip docx XML only | `_workstream\extract-docx.ps1` |

If `beforeShellExecution` blocks a nested `-Command`, **immediately retry** with the `-File` line above. Do not retry the blocked pattern.

Fallback if the script fails: `py -c "import zipfile,re,sys; ..."` (see `workspace-operations.md`). Never nest `powershell -Command`.

## Tasks

1. **Capture the meeting context**  -  Before extracting anything, confirm:
   - Meeting name / purpose
   - Date and time
   - Attendees (names + roles)
   - Phase / scope this relates to (initiative-wide, feature-specific, cohort/slice-specific)
   - Format (workshop / 1:1 / standup / playback / refinement / retro / ad-hoc)
   - Source of the input (transcript / notes / verbal recall / agenda only)

2. **Ingest the input**  -  Accept the input in whatever form provided:
   - Full transcript → process verbatim, attribute statements to speakers
   - Notes → process as user-curated summary (less attribution, more reliable on outcomes)
   - Verbal recall → guide with structured prompts to extract the same categories
   - Mixed → treat each section appropriately

3. **Scan Miro board for session content (when applicable)**  -  If a Miro board was used during the session:
   - Read every relevant frame using `layout_read`  -  not just topic-level scan but item-level content
   - Look for stickies, cards, text, and shapes added during the session that may NOT appear in the transcript (participants type on Miro without speaking)
   - Cross-reference Miro content against transcript  -  anything on the board but not in the transcript is a capture gap
   - Cross-reference transcript against Miro  -  anything discussed but not on the board is a documentation gap
   - Surface both gaps to the user before extraction

   **Anti-pattern:** Claiming "no new info on the board" after a topic-level scan. Topic coverage ≠ item coverage. Every sticky, card, and text item must be individually assessed.

4. **Track attendance and participation**  -  Before extracting content, note:
   - Who was present for the full session
   - Who joined late (and what they missed)
   - Who left early (and what happened after they left)
   - For anyone who left early: create a mandatory catch-up action tied to their domain areas that were discussed after departure
   - For anyone absent who was expected: note what they missed and whether a briefing is needed

5. **Extract structured items**  -  Pass through the transcript / notes and surface, with quote/source where possible.

   ### Action taxonomy (5 types  -  all mandatory to scan for)

   | Type | What to look for | Examples |
   |---|---|---|
   | **Explicit actions** | Formal commitments with owner | "[Team Member] to set up the pricing meeting", "[Team Member] will send the screenshots" |
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
   | **Sentiment / sponsor signal** | If sponsor present  -  engagement level, surprises, concerns, signs of waning interest |
   | **Stakeholder concerns** | Pushback, resistance, alignment gaps |
   | **Cross-cutting topics** | Compliance, legal, security, ops impacts mentioned |
   | **Followups for other people** | Things that need to go to people not in the meeting |
   | **Contradictions** | Where speakers disagree  -  surface, don't smooth over |
   | **Knowns confirmed** | Facts established during the session that should be logged as K-items |

4. **Route updates to specialist skills (mandatory)**  -  Each extracted item gets routed:

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

   **Important:** the debrief skill does not modify other skills' artefacts directly. It produces a routing report  -  "here's what I extracted, here's where each item should land"  -  and either invokes the relevant skill or hands off to the orchestrator to do so. This keeps each skill the owner of its own artefacts.

7. **Cross-reference against existing tracker**  -  Before updating, compare every extracted item against what's already tracked:
   - Read the living tracker (initiative-tracker.md or equivalent)
   - For each extracted item: is it already tracked? If yes, does the meeting change its status, owner, or detail?
   - Flag duplicates (already tracked and unchanged)  -  don't re-add
   - Flag updates (already tracked but status/detail changed)  -  update, don't duplicate
   - Flag net-new items  -  these are the additions
   - Surface the net-new and updated items to the user for confirmation before writing

7a. **Inference-vs-explicit cross-check**  -  For every decision extracted that was *derived by reasoning* (data analysis, synthesis of multiple statements, BA judgement) rather than *directly stated* by a speaker: re-scan the same source material specifically for explicit, direct statements on the same topic, even ones that appeared earlier or later in the transcript, in a different part of the conversation. If a direct statement conflicts with the inference-based decision, the direct statement wins by default  -  surface the conflict to the user rather than presenting the inferred decision as confirmed. Tag inference-based decisions with `basis: inferred` vs `basis: explicit-quote` in the tracker so this check is auditable later. *(Added 2 Jul 2026, Sample Initiative mid-initiative retro  -  see D-147 vs D-163.)*

8. **Question-to-action gap check**  -  For every open question extracted:
   - Does an action exist to answer it? (Who will find out? By when?)
   - If not, create a paired action: "Reach out to [person] re: [question]" or "Investigate [topic] to resolve [question]"
   - A question without a corresponding action is a tracking gap  -  the question documents what we need to know, the action documents who will go find out

9. **Update the living tracker**  -  Apply the routed items to the tracker (decisions table, RAID, OQ log, action register, sponsor decisions log). Each entry carries the source: meeting name + date + attendees + (where applicable) speaker.

10. **Sync BA actions**  -  Run `sync-ba-actions` per `references/ba-actions-format.md` §3 after tracker writes: upsert BA-owned/coordinated rows from this debrief into `_workstream/ba-actions.json`, regenerate `_workstream/ba-actions.md`, print gate line. Do **not** append to legacy `workboard.json → personal_tasks[]`.

11. **Trigger sync gate**  -  After all writes complete, run the sync gate check for the affected initiative(s) per `sync-gates.mdc`. This catches any remaining drift between SESSION-CONTEXT, tracker, and status-data. Present the sync card if drift is found; otherwise confirm: "All files in sync after debrief."

12. **Surface "before next meeting"**  -  Identify anything that must happen before the next scheduled meeting with the same group:
   - Decisions that need pre-confirmation
   - Actions due
   - Open questions that need answers
   - Artefacts to share
   - Pre-reads to send

13. **Draft post-meeting summary**  -  Hand off to `Communication_Drafter` (or `Playback_and_Enablement` if merged) to draft:
    - Internal Slack post / email recap to attendees + non-attendees who need to know
    - Sponsor briefing (if sponsor not in the meeting)
    - Stakeholder updates (if relevant)
    - Action item DMs to owners
    - **Slack/Teams DMs:** load `your voice-and-style rule (if installed)` → **Slack paste format (mandatory)**  -  bullets, single section breaks, labeled paste block; no paragraph-gap-only layout

14. **Detect requirement changes in-flight**  -  If extracted items reveal a requirement change, automatically invoke `ba-requirements-interrogator` in **Rethink** or **In-flight** mode (depending on whether dev has started). Don't silently absorb scope creep through meeting notes.

15. **Detect anti-patterns**  -  Watch for and flag during the debrief:
    - Decisions made by people without decision rights (vs. RACI)
    - Requirements being added without interrogation
    - Action items with no owner
    - Action items with no date
    - Open questions that have been open across multiple meetings (rotting)
    - Sponsor absent from a meeting where they had decisions to make
    - Same topic being re-discussed without progress
    - **Soft commitments not captured**  -  "we should…" / "we need to…" used in transcript but no corresponding action in the debrief
    - **Partial attendance without catch-up action**  -  someone left early and their domain was discussed after departure
    - **Questions without paired actions**  -  OQ logged but no action to find the answer

16. **Generate a Pre-meeting brief (when invoked ahead of a scheduled meeting)**  -  If the user signals a meeting is upcoming, run in reverse:
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
- Were there any surprises  -  things that came up that weren't on the agenda?
- Was the sponsor present? How did they engage?
- Did anything change about scope, priority, or requirements?

### When extracting items

- Is this action item really an action, or just a discussion point? Who owns it? By when?
- Is this a decision or a preference?
- Is this requirement new, or a change to an existing one?
- Did this risk just appear, or was it always there and we now see it?
- Is the meeting outcome consistent with what's already in the tracker, or is there a conflict?

### When detecting drift

- This requirement was logged differently last week  -  did it change, or did our understanding change?
- This action has been listed in the last three meetings unactioned  -  is it real, or should it be dropped?
- The sponsor has been absent from the last two sessions where decisions were needed  -  should we escalate or change cadence?

## Output Guidelines

### Meeting debrief report

```
Meeting: [name]
Date / time: [date], [time]
Attendees: [names + roles  -  note who joined late / left early]
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

- **Don't extract silently**  -  show the extracted items back to the user for confirmation before routing. Misattributed quotes or wrong decisions captured in the tracker are very expensive to fix.
- **Don't smooth over disagreement**  -  if the transcript shows two people disagreed and the disagreement wasn't resolved, surface it. Don't pick one and call it "the decision".
- **Don't accept actions without owner + date**  -  flag and ask. "Action: [name] to think about it" is not an action.
- **Don't let requirements slip in unannounced**  -  anything that looks like a new or changed requirement triggers `ba-requirements-interrogator`. No exceptions.
- **Don't silently absorb scope creep**  -  if a meeting added scope, flag it and route to Requirements Interrogator (Rethink/In-flight). The fact that the addition happened verbally is not a reason to skip interrogation.
- **Don't ignore sponsor absence**  -  sponsors missing decision moments is a 🧨 risk, not neutral. Surface.
- **Don't bury contradictions**  -  if the meeting outcome conflicts with what's in the tracker, raise it. Don't quietly overwrite.
- **Don't post a summary the user hasn't seen**  -  communication drafts go to the user for approval before sending.
- **Don't process every meeting at full depth**  -  small status standups don't need the full debrief flow. Match depth to meeting weight (1:1 with sponsor = full; daily standup = action items + blockers only).
- **Don't claim "nothing new on the board" without item-level verification**  -  topic-level Miro scans miss specific stickies, cards, and text items. Read every item in the frame.
- **Don't log a question without a paired action**  -  "Q: What's the reporting impact?" is incomplete without "Action: [BA name] to check with reporting team". The question documents the gap; the action fills it.
- **Don't skip soft commitments**  -  "we should probably book a session for that" IS an action, just not a formal one. Surface it, propose an owner and date, confirm with the user.
- **Don't ignore early departures**  -  someone leaving at minute 30 of a 120-minute session means 75% of the content needs a catch-up. Create the action.
- **Don't treat direct-to-assistant instructions as background noise**  -  "hopefully cursor can catch it" or "can you note that" is a first-class instruction. Track it as an action with the assistant as owner.

## Integration with BA Assistant

**Mode (post-Wave 3):** Cross-cutting capability  -  runs across all scopes and modes. Event-driven, not phase-bound.

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

**Anti-pattern this skill prevents:** "The meeting was the work"  -  valuable conversations happened, decisions were made, requirements were changed, RAID items surfaced, and none of it made it into the tracker. The next meeting starts by re-litigating the last. Compounds over a multi-month initiative until the team is doing change management in their heads and decisions are being made twice.
