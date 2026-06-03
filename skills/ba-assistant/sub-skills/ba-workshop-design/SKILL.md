---
name: ba-workshop-design
description: Design and run workshops across the initiative lifecycle — kickoff, current state, discovery, slicing, solution shaping, retro, change kickoff. Owns facilitation patterns, templates, agendas, attendee logic, and post-workshop debrief routing.
---

# Skill: Workshop Design

## Description

The Workshop Design skill owns the **facilitation engine** for the BA Assistant. Any time the user needs to plan, run, or recover from a workshop, this skill provides the template, agenda, attendee logic, facilitation patterns, and debrief routing.

Workshops are the highest-bandwidth way the BA gathers information and aligns stakeholders. A well-designed workshop produces decisions; a poorly-designed one produces fatigue. This skill exists to make the design deliberate, not improvised.

**This skill absorbed `ba-kickoff-preparation`** during Wave 3 consolidation — the Kickoff workshop is now one template among several inside this skill. Kickoff is the most prominent and detailed template, but the same engine powers all workshop types.

> **Cross-cutting rule:** This skill produces multiple artefact-class outputs (facilitation pack, agenda, attendee list, pre-reads, debrief instructions, anti-patterns/do-not-say lists). Before generating outputs, apply the **"What I'll produce next" declaration** rule from `ba-assistant\SKILL.md → Co-thinking and artefact production protocol` — surface planned artefacts upfront and ask the user to select. The [previous initiative] produced a full 60-min pack on a `deeper_workshop` selection because the option label conflated topic with depth — see also "AskQuestion authoring guidelines" in BA Assistant SKILL.md.

## When to invoke

- **Phase 1 / M1** — Initiative kickoff (D1)
- **Phase 2 / M2** — Current state workshops, discovery workshops, stakeholder interviews
- **Phase 3 / M3** — Slicing workshops, prioritisation workshops
- **Phase 4 / M4** — Solution shaping workshops, ADR review
- **Phase 5 / M5** — Refinement workshops, spike review
- **Phase 6 / M6** — Playback workshops, sign-off sessions
- **M8 Change Strategy** — Audience change kickoff, change checkpoint workshops
- **Any phase** — Retrospective workshops (per `ba-retrospective-and-learning`)
- **Any phase** — Ad-hoc unblocking workshops

## Mandatory hooks

| Hook | When | Why |
|---|---|---|
| **Communication_Drafter** (or `Playback_and_Enablement` after Wave 3 merge) | Always | Workshop invite, pre-read, agenda distribution, post-workshop comms |
| **Stakeholder_Strategy** | Pre-workshop | Attendee identification — who needs to be in the room and why |
| **Risk_and_Tracker** | Post-workshop | Log decisions, actions, OQs, RAID surfaced during the workshop |
| **ba-meeting-debrief** | Post-workshop | Process the workshop output (transcript / notes / verbal recall) and route updates to specialist skills |
| **Visual_Storytelling** | Pre-workshop | Diagrams, journey maps, current state visuals to anchor the conversation |
| **Sponsor_Engagement** | Pre-workshop for high-stakes workshops | Sponsor pre-brief; sponsor presence (yes/no/proxy) confirmed |

## Workshop templates

This skill ships with templates for the workshop types BAs actually run. Each template specifies: purpose, attendees, agenda, pre-read, activities, decisions sought, success criteria.

### Template 1 — Initiative Kickoff (D1)

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

**Agenda (typical 60–90 minutes):**

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
- Separate problem framing from solution discussion explicitly — solutions get parked, not discussed
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

### Template 2 — Current State Workshop

**Purpose:** Build shared understanding of how things work today across process, system, data, people. Surface tribal knowledge.

**Attendees:**
- BA (facilitator)
- Operational practitioners who actually do the work today (NOT just their managers)
- Technical SME(s) for systems involved
- Customer-facing roles if user-experience is in scope

Identification logic: prioritise people who *do* the work, not people who *describe* it. Tribal knowledge holders are often not the obvious org-chart picks.

**Pre-read:**
- Initiative context
- Whatever current state documentation exists (mark it "starting point — please correct")
- A draft process map (deliberately imperfect — invites correction)

**Agenda (typical 90 minutes):**

| Time | Section | Activity |
|---|---|---|
| 0:00 | Welcome + frame | "I've drafted what I think happens — your job is to correct me" |
| 0:05 | Walk through draft (5–10 min per major step) | BA narrates the draft; attendees interrupt with corrections |
| 0:30 | Pain points — go around the room | Each attendee names their top 1–2 pain points |
| 0:45 | Edge cases + exceptions | "What breaks this? What do you do when it breaks?" |
| 1:00 | Workarounds + manual steps | "What do you do that's not in the doc?" |
| 1:15 | Open questions + close | OQs logged |

**Facilitation tips:**
- The draft process map is a *provocation*, not an answer. Be visibly comfortable with being wrong.
- Don't argue with corrections — capture them all, reconcile later.
- Tribal knowledge surfaces when people are correcting something, not when they're explaining from scratch.

**Success criteria:**
- Corrected process map approved by attendees
- Pain heatmap from real practitioners
- Tribal knowledge register with at least 3 items not in any documentation
- Workarounds catalogued

### Template 3 — Discovery Workshop

**Purpose:** Extract candidate requirements from stakeholders by topic / domain.

**Attendees:** Stakeholders for the specific domain being discovered. Smaller and more focused than kickoff.

**Pre-read:** Topic-specific question bank generated by Discovery & Requirements skill.

**Agenda:** Topic-driven, not time-driven. For each major topic:
1. Frame the topic + show what's already known
2. Open questions to the room
3. Probe for unstated requirements
4. Capture candidate requirements (each → Requirements_Interrogator afterwards)

**Success criteria:**
- Candidate requirements list with source attributed
- Open questions logged with owners
- Decisions deferred logged explicitly (don't pretend they're decided)

### Template 4 — Slicing Workshop

**Purpose:** Break the initiative into independently valuable slices and agree sequencing.

**Attendees:** PM, BA, Engineering lead, key SMEs. Smaller working session.

**Pre-read:**
- High-level requirements
- Impact map (if generated — see Feature Slicing & Sequencing skill)
- Critical path items / long-lead activities

**Agenda:**
1. Confirm the goal (anchor the slicing conversation)
2. Walk the Impact Map (if available) or feature inventory
3. Group into slices — each slice deliverable independently with explicit value
4. Score each slice on 4 priority types (business / analysis / delivery / critical-path)
5. Propose sequencing + parallelisation
6. Identify slices to defer

**Success criteria:**
- Slice list with names, scope, and value
- Sequencing decision with rationale
- Deferral decisions explicit (with reason)

### Template 5 — Solution Shaping Workshop

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
- Don't let the loudest engineer's option win by default — force option generation BEFORE evaluation
- For each option, ask "what does this NOT solve?"
- JTBD-tagged requirements: explicitly score functional / emotional / social coverage

**Success criteria:**
- Multiple options with explicit trade-offs
- ADR topics surfaced
- Spikes identified with owners
- Direction recommended (with criteria if not yet locked)

### Template 6 — Refinement Workshop

**Purpose:** Take stories from "draft" to "ready for development" — Definition of Ready check.

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

### Template 7 — Playback Workshop

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
- Sponsor pre-briefed; sponsor visibly backing (or visibly absent — and surface that)
- Use Visual_Storytelling-produced one-pagers, not detailed delivery views
- Explicit yes/no on sign-offs — no "I'm comfortable" without a documented record

**Success criteria:**
- Sign-offs captured in writing per artefact
- Objections logged with mitigation plans
- Path to launch clear

### Template 8 — Retrospective Workshop

**Purpose:** Capture what worked, what didn't, what to do differently. (Detailed agenda lives in `ba-retrospective-and-learning` skill — this template provides the workshop frame for that skill's content.)

### Template 9 — Change Kickoff Workshop

**Purpose:** Per-audience change kickoff — Awareness + Desire for ADKAR (per `ba-change-strategy`).

**Attendees:** The impacted audience + their line managers + sponsor (visible).

**Pre-read:** Audience-specific change one-pager.

**Agenda:** Why (problem) → What (change) → When (timeline) → How (support) → Q&A.

**Success criteria:** Audience visibly understanding (A in ADKAR) and showing engagement (D in ADKAR).

## Common tasks across all templates

1. **Participant identification** — Cross-reference with `ba-stakeholder-strategy`. Call out missing roles whose absence would cause rework. Flag who *must* attend vs who *should* attend vs *informed only*.

2. **Pre-read drafting** — Hand off to `Communication_Drafter` (or `Playback_and_Enablement` after Wave 3 merge). Pre-read is usually 1 page max; longer pre-reads don't get read.

3. **Agenda creation** — Pick the appropriate template + adapt to the specific workshop. Time-box every section. Build in buffer (10% minimum).

4. **Activity selection** — Match activity to outcome:
   - For *alignment* — read-then-discuss (everyone reads the same statement, then discusses)
   - For *surfacing tribal knowledge* — provoke with imperfect draft
   - For *generating options* — silent ideation first, share after
   - For *prioritising* — dot voting, MoSCoW per scope, value/effort matrix
   - For *decision* — explicit yes/no, written record

5. **Upstream dependency check** — For every decision on the agenda, ask: "What input, approval, or deliverable from another person or team does this decision need BEFORE the room can make it?" If the upstream input isn't confirmed ready, either (a) defer the decision to a later session, (b) reframe as conditional ("we'll decide X provisionally, pending Y"), or (c) get the upstream input before the session. *Source: [previous initiative retro] — segmentation gating comms MoSCoW was a Day 5 surprise because nobody checked whether [PM Name]'s segmentation work was ready before scheduling the MoSCoW decision.*

6. **Facilitation tips** — Adapt to the audience. Sponsor-in-the-room workshops need explicit decision moments. Working-group workshops can be more exploratory.

7. **Capture during the workshop** — Decisions, actions, OQs surface in real time; capture them visibly so attendees can correct. Don't try to take notes silently and reconstruct later.

8. **Post-workshop debrief** — Hand off to `ba-meeting-debrief` immediately after the workshop. The debrief skill routes extracted items to the right specialist skills and updates the tracker.

9. **Communications** — Hand off to `Communication_Drafter` for recap email / Slack post / sponsor briefing / action DMs.

## Typical Questions to Ask

### When designing a workshop
- What is the *single outcome* this workshop must produce? (If there are 3, run 3 workshops.)
- Who must be in the room for that outcome? Who can be informed afterwards?
- What's the right time-box?
- What pre-read will be read? (Be honest — if it's >1 page, it won't be.)
- What's the highest-risk part — alignment, decision, or activation?
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
| Purpose | One sentence — what this workshop produces |
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

- **Don't run a workshop without a single outcome** — if there are 3 outcomes, that's 3 workshops.
- **Don't invite people for political reasons** — attendees should be people whose presence or input matters to the outcome.
- **Don't skip the pre-read** — workshops where people read for the first time in the room are 30 minutes longer.
- **Don't run high-stakes workshops without sponsor pre-brief** — surprises in those rooms cause withdrawals of cover.
- **Don't take notes silently and reconstruct after** — capture visibly, in real-time, so attendees can correct.
- **Don't conflate refinement with discovery** — refinement is "is this story ready"; discovery is "do we have the right requirement". Different audiences, different facilitation.
- **Don't skip the debrief** — every workshop must be processed by `ba-meeting-debrief` post-meeting, or the value evaporates.
- **Don't let workshops become ritual** — recurring workshops with no decisions are theatre. Re-design or cancel.
- **Don't paper over absent stakeholders** — if a must-attend person didn't show, name it. Decisions made without them may need re-confirming.

## Integration with BA Assistant

**Mode (post-Wave 3):** Cross-cutting capability — runs at any mode, any scope.

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

**Anti-pattern this skill prevents:** "Workshop as ritual" — recurring meetings where nothing is decided, attendance dwindles, and the BA does the actual decision-making after the workshop in 1:1s. The workshop should produce the decision, not be the venue where the decision is rubber-stamped.

---

## Migration note (Wave 3 consolidation)

This skill **absorbed `ba-kickoff-preparation`** in Wave 3. The Kickoff workshop is now Template 1 here. Hooks previously calling `ba-kickoff-preparation` should now call `ba-workshop-design` with `template: "kickoff"` (or just invoke the skill and it will route to the right template based on context).
