---
name: ba-workshop-design
description: Design and run workshops across the initiative lifecycle â€” kickoff, current state, discovery, slicing, solution shaping, retro, change kickoff. Owns facilitation patterns, templates, agendas, attendee logic, and post-workshop debrief routing.
---

# Skill: Workshop Design

## Description

The Workshop Design skill owns the **facilitation engine** for the BA Assistant. Any time the user needs to plan, run, or recover from a workshop, this skill provides the template, agenda, attendee logic, facilitation patterns, and debrief routing.

Workshops are the highest-bandwidth way the BA gathers information and aligns stakeholders. A well-designed workshop produces decisions; a poorly-designed one produces fatigue. This skill exists to make the design deliberate, not improvised.

**This skill absorbed `ba-kickoff-preparation`** during Wave 3 consolidation â€” the Kickoff workshop is now one template among several inside this skill. Kickoff is the most prominent and detailed template, but the same engine powers all workshop types.

> **Cross-cutting rule:** This skill produces multiple artefact-class outputs (facilitation pack, agenda, attendee list, pre-reads, debrief instructions, anti-patterns/do-not-say lists). Before generating outputs, apply the **"What I'll produce next" declaration** rule from `ba-assistant\SKILL.md â†’ Co-thinking and artefact production protocol` â€” surface planned artefacts upfront and ask the user to select. The RBA dry-run produced a full 60-min pack on a `deeper_workshop` selection because the option label conflated topic with depth â€” see also "AskQuestion authoring guidelines" in BA Assistant SKILL.md.

## When to invoke

- **Phase 1 / M1** â€” Initiative kickoff (D1)
- **Phase 2 / M2** â€” Current state workshops, discovery workshops, stakeholder interviews
- **Phase 3 / M3** â€” Slicing workshops, prioritisation workshops
- **Phase 4 / M4** â€” Solution shaping workshops, ADR review
- **Phase 5 / M5** â€” Refinement workshops, spike review
- **Phase 6 / M6** â€” Playback workshops, sign-off sessions
- **M8 Change Strategy** â€” Audience change kickoff, change checkpoint workshops
- **Any phase** â€” Retrospective workshops (per `ba-retrospective-and-learning`)
- **Any phase** â€” Ad-hoc unblocking workshops

## Mandatory hooks

| Hook | When | Why |
|---|---|---|
| **miro-board-analysis** | Pre-workshop (launch mode Step 5) | Build or populate the Miro board. MUST load the skill and follow its Pre-Creation Checklist, Content Panel Pattern, and verified templates. Match existing board styling. |
| **Communication_Drafter** (or `Playback_and_Enablement` after Wave 3 merge) | Always | Workshop invite, pre-read, agenda distribution, post-workshop comms |
| **Stakeholder_Strategy** | Pre-workshop | Attendee identification â€” who needs to be in the room and why |
| **Risk_and_Tracker** | Post-workshop | Log decisions, actions, OQs, RAID surfaced during the workshop |
| **ba-meeting-debrief** | Post-workshop | Process the workshop output (transcript / notes / verbal recall) and route updates to specialist skills |
| **Visual_Storytelling** | Pre-workshop | Diagrams, journey maps, current state visuals to anchor the conversation |
| **Sponsor_Engagement** | Pre-workshop for high-stakes workshops | Sponsor pre-brief; sponsor presence (yes/no/proxy) confirmed |

## Workshop templates

This skill ships with templates for the workshop types BAs actually run. Each template specifies: purpose, attendees, agenda, pre-read, activities, decisions sought, success criteria.

### Template 1 â€” Initiative Kickoff (D1)

**Purpose:** Align all relevant stakeholders on problem, scope, timeframe, priorities, and initial RAID. First moment where the team becomes "the team".

**Attendees (typical):**
- Sponsor (executive)
- PM / Product Manager
- BA (facilitator)
- Engineering lead(s)
- Compliance / legal (if relevant to domain)
- Design lead (if customer-facing)
- Operations lead (if process change)
- Service design (if cross-channel)
- Data lead (if analytics-heavy)

Identification logic: cross-reference Stakeholder_Strategy output with initiative scope. Call out missing roles whose absence would cause rework later.

**Pre-read:**
- Intake summary table (from Intake_Reviewer)
- Problem statement (provisional)
- Initial RAID (provisional)
- Confidence scores
- Workshop agenda + decisions needed

**Agenda (typical 60â€“90 minutes):**

| Time | Section | Lead | Decisions sought |
|---|---|---|---|
| 0:00 | Welcome + purpose | BA | n/a |
| 0:05 | Problem framing (read-then-discuss) | Sponsor or PM | Problem statement confirmed |
| 0:20 | Scope confirmation (in/out) | PM | Scope boundaries agreed |
| 0:35 | Success metrics | PM | Metrics confirmed + measurable |
| 0:45 | Stakeholder roles + RACI overview | BA | Roles confirmed |
| 0:55 | RAID surfacing | All | Risks added; assumptions challenged |
| 1:10 | Cadence + next steps | BA | Meeting cadence agreed; immediate actions assigned |
| 1:25 | Open questions + close | BA | OQs logged with owners |

**Facilitation tips:**
- Separate problem framing from solution discussion explicitly â€” solutions get parked, not discussed
- Use a visible "parking lot" for off-topic items
- Capture decisions in real-time (visible to room), not after the meeting
- For each decision: state who decided, what was decided, what was the alternative
- For each OQ: state who can answer + by when

**Success criteria:**
- Problem statement confirmed by all attendees (not just the loudest voices)
- Scope boundaries explicit (in AND out)
- Sponsor visibly present and aligned
- Top 3 risks named
- Next decision moments and owners agreed
- BA has the inputs needed to begin Phase 2 / M2 Discovery

### Template 2 â€” Current State Workshop

**Purpose:** Build shared understanding of how things work today across process, system, data, people. Surface tribal knowledge.

**Attendees:**
- BA (facilitator)
- Operational practitioners who actually do the work today (NOT just their managers)
- Technical SME(s) for systems involved
- Customer-facing roles if user-experience is in scope

Identification logic: prioritise people who *do* the work, not people who *describe* it. Tribal knowledge holders are often not the obvious org-chart picks.

**Pre-read:**
- Initiative context
- Whatever current state documentation exists (mark it "starting point â€” please correct")
- A draft process map (deliberately imperfect â€” invites correction)

**Agenda (typical 90 minutes):**

| Time | Section | Activity |
|---|---|---|
| 0:00 | Welcome + frame | "I've drafted what I think happens â€” your job is to correct me" |
| 0:05 | Walk through draft (5â€“10 min per major step) | BA narrates the draft; attendees interrupt with corrections |
| 0:30 | Pain points â€” go around the room | Each attendee names their top 1â€“2 pain points |
| 0:45 | Edge cases + exceptions | "What breaks this? What do you do when it breaks?" |
| 1:00 | Workarounds + manual steps | "What do you do that's not in the doc?" |
| 1:15 | Open questions + close | OQs logged |

**Facilitation tips:**
- The draft process map is a *provocation*, not an answer. Be visibly comfortable with being wrong.
- Don't argue with corrections â€” capture them all, reconcile later.
- Tribal knowledge surfaces when people are correcting something, not when they're explaining from scratch.

**Success criteria:**
- Corrected process map approved by attendees
- Pain heatmap from real practitioners
- Tribal knowledge register with at least 3 items not in any documentation
- Workarounds catalogued

### Template 3 â€” Discovery Workshop

**Purpose:** Extract candidate requirements from stakeholders by topic / domain.

**Attendees:** Stakeholders for the specific domain being discovered. Smaller and more focused than kickoff.

**Pre-read:** Topic-specific question bank generated by Discovery & Requirements skill.

**Agenda:** Topic-driven, not time-driven. For each major topic:
1. Frame the topic + show what's already known
2. Open questions to the room
3. Probe for unstated requirements
4. Capture candidate requirements (each â†’ Requirements_Interrogator afterwards)

**Success criteria:**
- Candidate requirements list with source attributed
- Open questions logged with owners
- Decisions deferred logged explicitly (don't pretend they're decided)

### Template 4 â€” Slicing Workshop

**Purpose:** Break the initiative into independently valuable slices and agree sequencing.

**Attendees:** PM, BA, Engineering lead, key SMEs. Smaller working session.

**Pre-read:**
- High-level requirements
- Impact map (if generated â€” see Feature Slicing & Sequencing skill)
- Critical path items / long-lead activities

**Agenda:**
1. Confirm the goal (anchor the slicing conversation)
2. Walk the Impact Map (if available) or feature inventory
3. Group into slices â€” each slice deliverable independently with explicit value
4. Score each slice on 4 priority types (business / analysis / delivery / critical-path)
5. Propose sequencing + parallelisation
6. Identify slices to defer

**Success criteria:**
- Slice list with names, scope, and value
- Sequencing decision with rationale
- Deferral decisions explicit (with reason)

### Template 5 â€” Solution Shaping Workshop

**Purpose:** Generate diverse solution options, evaluate trade-offs, narrow to direction.

**Attendees:** Engineering lead(s), architect (if available), BA, PM, key SMEs (compliance / design / data if relevant to options).

**Pre-read:**
- Requirements (interrogated, with JTBD breakdowns where applicable)
- Constraints (compliance, technical, timeline)
- Spike outputs (if any)

**Agenda:**
1. Frame: what are we trying to solve, in one sentence
2. Generate options (target 3+ that vary along at least 2 dimensions per Solution Shaping skill)
3. Each option: pros / cons / risks / spikes needed / JTBD coverage
4. Surface ADRs needed
5. Recommend direction (or top 2 + criteria for decision)

**Facilitation tips:**
- Don't let the loudest engineer's option win by default â€” force option generation BEFORE evaluation
- For each option, ask "what does this NOT solve?"
- JTBD-tagged requirements: explicitly score functional / emotional / social coverage

**Success criteria:**
- Multiple options with explicit trade-offs
- ADR topics surfaced
- Spikes identified with owners
- Direction recommended (with criteria if not yet locked)

### Template 6 â€” Refinement Workshop

**Purpose:** Take stories from "draft" to "ready for development" â€” Definition of Ready check.

**Attendees:** Engineering team, BA, PM.

**Pre-read:** Story drafts, acceptance criteria, dependencies.

**Agenda:** Per story:
1. Read the story aloud
2. Acceptance criteria walkthrough
3. Engineering team asks questions
4. DoR check (per Definition of Ready skill / Delivery Definition skill after Wave 3 merge)
5. Story rated: ready / needs more work / blocked

**Success criteria:**
- Each story explicitly rated
- "Needs more work" items have specific next-step actions and owners
- MoSCoW rating confirmed per scope (warn-and-flag if missing)

### Template 7 â€” Playback Workshop

**Purpose:** Communicate solution direction to broader stakeholder set, secure sign-off, surface late objections.

**Attendees:** All stakeholders who need to sign off + anyone whose objection would block progress.

**Pre-read:**
- Playback pack (one-pager via Visual_Storytelling)
- Decisions needed at this session
- RAID highlights

**Agenda:**
1. Recap problem + scope + journey to date
2. Solution direction with rationale
3. Trade-offs made (be honest about what was chosen NOT to do)
4. Sequence and timeline
5. Risks and dependencies
6. Sign-offs sought (specific yes/no questions)
7. Outstanding objections logged

**Facilitation tips:**
- Sponsor pre-briefed; sponsor visibly backing (or visibly absent â€” and surface that)
- Use Visual_Storytelling-produced one-pagers, not detailed delivery views
- Explicit yes/no on sign-offs â€” no "I'm comfortable" without a documented record

**Success criteria:**
- Sign-offs captured in writing per artefact
- Objections logged with mitigation plans
- Path to launch clear

### Template 8 â€” Retrospective Workshop

**Purpose:** Capture what worked, what didn't, what to do differently. (Detailed agenda lives in `ba-retrospective-and-learning` skill â€” this template provides the workshop frame for that skill's content.)

### Template 9 â€” Change Kickoff Workshop

**Purpose:** Per-audience change kickoff â€” Awareness + Desire for ADKAR (per `ba-change-strategy`).

**Attendees:** The impacted audience + their line managers + sponsor (visible).

**Pre-read:** Audience-specific change one-pager.

**Agenda:** Why (problem) â†’ What (change) â†’ When (timeline) â†’ How (support) â†’ Q&A.

**Success criteria:** Audience visibly understanding (A in ADKAR) and showing engagement (D in ADKAR).

## Launch Mode (`/workshop launch`)

Launch mode is an orchestrated multi-step flow that takes a workshop from "I need a session on X" to "meeting is booked, pre-reads sent, Miro board ready" in one conversation. It integrates with the calendar feed, comms drafting, and Miro board creation.

### When to use

- User says `/workshop launch`, "set up a workshop for X", "I need to run a session on Y", "prep a workshop"
- User is in a phase that needs a workshop (kickoff, discovery, slicing, etc.) and hasn't scheduled one yet
- Calendar feed shows no upcoming meeting for a topic that needs a workshop

### Launch sequence

The agent walks through each step, using AskQuestion at each gate:

**Step 1: Define the workshop**
- Auto-detect the template from context (e.g. Phase 2 discovery â†’ Template 3)
- Ask user to confirm: template, purpose, target date range, duration
- Check `_workstream/calendar-feed.json` for free slots in the target range
- Propose 2-3 time options based on calendar gaps and attendee patterns

**Step 2: Identify attendees**
- Cross-reference `ba-stakeholder-strategy` and initiative context
- Propose attendee list with roles and must-attend / should-attend tags
- AskQuestion: confirm list, add/remove people
- Flag missing critical roles (e.g. no compliance rep for a compliance-scoped workshop)

**Step 3: Create the workshop pack**
- Generate the full workshop pack (purpose, agenda, activities, decisions sought, success criteria)
- Adapt the template to the specific context (pull relevant OQs, decisions needed, RAID items)
- AskQuestion: approve pack, or edit sections

**Step 4: Create pre-read**
- Generate a 1-page pre-read summarising:
  - Where we are on the initiative (from tracker)
  - What decisions this workshop needs to make
  - What input attendees should bring
- Draft in Jess's voice (load `jess-voice-and-style.mdc`)
- AskQuestion: approve, edit, or skip pre-read

**Step 5: Create Miro board (MANDATORY for workshops with activities)**

This step uses the **`miro-board-analysis` skill** and its Miro MCP tools. The agent MUST load and follow that skill file before creating any board content. Key rules:

- **Before any creation**: Call `layout_get_dsl` to get DSL spec. Call `layout_read` on existing frames to match board styling.
- **Use `layout_create` for all styled content** (headers, grey backdrops, text, stickies). NEVER use `user-miro-desktop` `create_shape`/`create_text`.
- **Use the verified template patterns** from `miro-board-analysis`:
  - Full workshop â†’ **Pattern 1** (single wide horizontal frame, sections in agenda order)
  - Brainstorming â†’ **Pattern 2** (prompt sticky + seed examples + open space)
  - Q&A grids â†’ **Pattern 2b** (dark_blue questions, light_yellow responses)
  - RAID capture â†’ **Pattern 7b** (four bordered columns with coloured stickies)
  - Decisions/outcomes â†’ **Pattern 4** (table with header + grey backdrop)
  - Dot voting â†’ **Pattern 6** (options as shapes + empty vote areas)
  - Retro â†’ **Pattern 7** (three-column sticky layout)
- **Follow the Content Panel Pattern**: coloured `round_rectangle` header â†’ grey `rectangle` backdrop (`fill=#e6e6e6`) â†’ TEXT positioned near TOP of grey box (formula: `text_y = card_top + 50 + text_height/2`)
- **Use the 5-tier brand palette** for headers (Primary `#7b14ef`, Secondary `#c497fe`, Tertiary `#fff854`, Dark `#232428`, Black `#000000`)
- **Left-to-right layout matches the agenda order** â€” context first, activities in sequence, outcomes last
- **Run Pre-Creation Checklist** from `miro-board-analysis` before every creation call
- **Run `layout_read` after creation** to verify no overlaps, misaligned headers, or text-outside-card issues

Specific to workshop launch:
- Map each agenda activity to a board section using the activity â†’ board element table from the Miro skill's "Integration with BA Assistant" section
- Pre-populate: agenda (with real clock times, not relative), discussion prompts as Q&A stickies, RAID columns, parking lot, actions table
- Include relevant diagrams from `Visual_Storytelling` (current state maps, journey maps, etc.)
- Create 3+ rows of Q&A pairs (not 2 â€” need room for real workshop input)
- Leave generous brainstorming space (3000x2000px minimum)

AskQuestion: approve board, skip Miro, or I'll do it manually

**Step 6: Draft meeting invite + reminder**
- Use `Communication_Drafter` to draft:
  - Meeting invite with agenda, pre-read link, Miro link
  - Reminder message for 24h before the workshop
- AskQuestion: approve invite text, edit, send reminder manually

**Step 7: Add to workboard + calendar**
- Add the workshop as a personal task in `_workstream/workboard.json` (with prep checklist)
- Note: the actual calendar invite is sent by the user (Cursor can't send Outlook invites via COM)
- Confirm: "Workshop pack ready. Send the invite, share the pre-read, and you're set."

### Launch mode output summary

After all steps complete, present a summary:

```
--- Workshop Launch Complete ---
Workshop:   [name]
Template:   [template number and name]
Date/time:  [proposed date]
Duration:   [duration]
Attendees:  [count] ([key names])
Pre-read:   [created / skipped]
Miro board: [created / skipped]
Invite:     [drafted / skipped]

Files created/updated:
  - blueprints/{slug}/workshops/[name].md (workshop pack)
  - _workstream/workboard.json (prep task added)

Next: Send the invite, share the pre-read, review the Miro board.
---
```

### Partial launch

The user can exit launch mode at any step. Progress is saved -- they can say "continue workshop launch" to pick up where they left off. Each step's output is independent and useful on its own.

## Common tasks across all templates

1. **Participant identification** â€” Cross-reference with `ba-stakeholder-strategy`. Call out missing roles whose absence would cause rework. Flag who *must* attend vs who *should* attend vs *informed only*.

2. **Pre-read drafting** â€” Hand off to `Communication_Drafter` (or `Playback_and_Enablement` after Wave 3 merge). Pre-read is usually 1 page max; longer pre-reads don't get read.

3. **Agenda creation** â€” Pick the appropriate template + adapt to the specific workshop. Time-box every section. Build in buffer (10% minimum).

4. **Activity selection** â€” Match activity to outcome:
   - For *alignment* â€” read-then-discuss (everyone reads the same statement, then discusses)
   - For *surfacing tribal knowledge* â€” provoke with imperfect draft
   - For *generating options* â€” silent ideation first, share after
   - For *prioritising* â€” dot voting, MoSCoW per scope, value/effort matrix
   - For *decision* â€” explicit yes/no, written record

5. **Upstream dependency check** â€” For every decision on the agenda, ask: "What input, approval, or deliverable from another person or team does this decision need BEFORE the room can make it?" If the upstream input isn't confirmed ready, either (a) defer the decision to a later session, (b) reframe as conditional ("we'll decide X provisionally, pending Y"), or (c) get the upstream input before the session. *Source: RBA Week 1 retro â€” segmentation gating comms MoSCoW was a Day 5 surprise because nobody checked whether Alice's segmentation work was ready before scheduling the MoSCoW decision.*

6. **Facilitation tips** â€” Adapt to the audience. Sponsor-in-the-room workshops need explicit decision moments. Working-group workshops can be more exploratory.

7. **Capture during the workshop** â€” Decisions, actions, OQs surface in real time; capture them visibly so attendees can correct. Don't try to take notes silently and reconstruct later.

8. **Post-workshop debrief** â€” Hand off to `ba-meeting-debrief` immediately after the workshop. The debrief skill routes extracted items to the right specialist skills and updates the tracker.

9. **Communications** â€” Hand off to `Communication_Drafter` for recap email / Slack post / sponsor briefing / action DMs.

## Typical Questions to Ask

### When designing a workshop
- What is the *single outcome* this workshop must produce? (If there are 3, run 3 workshops.)
- Who must be in the room for that outcome? Who can be informed afterwards?
- What's the right time-box?
- What pre-read will be read? (Be honest â€” if it's >1 page, it won't be.)
- What's the highest-risk part â€” alignment, decision, or activation?
- Is the sponsor needed? In person or proxy?

### When the workshop is high-stakes (sign-off, escalation, sponsor decision)
- Has the sponsor been pre-briefed? Will they be visibly engaged?
- Are decisions framed as explicit yes/no?
- Is there a fallback plan if sign-off doesn't happen?

### When running a recurring workshop (refinement, retro)
- Is the cadence still right? Are people showing up?
- Has the format become ritual without value? Re-design.

## Output Guidelines

For each workshop, produce:

### Workshop pack

| Section | Content |
|---|---|
| Purpose | One sentence â€” what this workshop produces |
| Type / template | Kickoff / current state / discovery / slicing / solution / refinement / playback / retro / change kickoff / ad-hoc |
| Date, time, duration | |
| Attendees | Names + roles + must-attend or should-attend or informed |
| Pre-read | Linked artefacts (max 1 page summary) |
| Agenda | Time-boxed sections with leads and decisions sought |
| Activities | Per section, the activity to use |
| Decisions sought | Explicit list of decisions the workshop must produce |
| Success criteria | How we know it worked |

### Post-workshop summary (hand off to ba-meeting-debrief)

Per the Meeting Debrief skill output format. Includes decisions, actions, OQs, requirement changes, RAID updates, anti-patterns observed.

## Challenge Rules

- **Don't run a workshop without a single outcome** â€” if there are 3 outcomes, that's 3 workshops.
- **Don't invite people for political reasons** â€” attendees should be people whose presence or input matters to the outcome.
- **Don't skip the pre-read** â€” workshops where people read for the first time in the room are 30 minutes longer.
- **Don't run high-stakes workshops without sponsor pre-brief** â€” surprises in those rooms cause withdrawals of cover.
- **Don't take notes silently and reconstruct after** â€” capture visibly, in real-time, so attendees can correct.
- **Don't conflate refinement with discovery** â€” refinement is "is this story ready"; discovery is "do we have the right requirement". Different audiences, different facilitation.
- **Don't skip the debrief** â€” every workshop must be processed by `ba-meeting-debrief` post-meeting, or the value evaporates.
- **Don't let workshops become ritual** â€” recurring workshops with no decisions are theatre. Re-design or cancel.
- **Don't paper over absent stakeholders** â€” if a must-attend person didn't show, name it. Decisions made without them may need re-confirming.

## Integration with BA Assistant

**Mode (post-Wave 3):** Cross-cutting capability â€” runs at any mode, any scope.

**Hooks called by this skill:** Communication_Drafter (pre/post comms), Stakeholder_Strategy (attendee logic), Risk_and_Tracker (decisions/RAID), ba-meeting-debrief (post-workshop processing), Visual_Storytelling (workshop visuals), Sponsor_Engagement (sponsor pre-brief).

**Hooks calling this skill:**
- Orchestrator when entering a phase / mode that needs a workshop
- Discovery & Requirements (for discovery workshops + stakeholder interviews)
- Feature Slicing & Sequencing (for slicing workshops)
- Solution Shaping (for solution workshops)
- Delivery Definition (for refinement workshops)
- Playback & Enablement (for playback workshops)
- Change Strategy (for change kickoff workshops)
- Retrospective & Learning (for retro workshops)
- User direct invocation ("design me a workshop for X")

**Living tracker updates:** Workshop schedule, attendee confirmation status, decisions made, actions assigned, OQs surfaced. Cross-link each tracker item to the workshop where it originated.

**Anti-pattern this skill prevents:** "Workshop as ritual" â€” recurring meetings where nothing is decided, attendance dwindles, and the BA does the actual decision-making after the workshop in 1:1s. The workshop should produce the decision, not be the venue where the decision is rubber-stamped.

---

## Migration note (Wave 3 consolidation)

This skill **absorbed `ba-kickoff-preparation`** in Wave 3. The Kickoff workshop is now Template 1 here. Hooks previously calling `ba-kickoff-preparation` should now call `ba-workshop-design` with `template: "kickoff"` (or just invoke the skill and it will route to the right template based on context).

