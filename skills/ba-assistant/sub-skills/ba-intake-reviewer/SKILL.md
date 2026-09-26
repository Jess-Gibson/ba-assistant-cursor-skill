---
name: ba-intake-reviewer
description: Reviews a PM's all-in-one or initial brief, challenges vague statements, and sets up the initiative's starting files.
disable-model-invocation: true
---

# Skill: Intake Reviewer

## Description

The Intake Reviewer is the first specialist skill invoked by the BA Initiative Navigator.  It reviews the PM's **all‑in‑one** or initial brief to extract key context about the initiative.  It asks clarifying questions to challenge vague statements, identifies early scope ambiguities, surfaces obvious risks and assumptions, and prepares preliminary RAID items.  The goal is to provide a clear starting point and agenda for subsequent stakeholder alignment.

> **Cross-cutting rule:** This skill produces multiple artefact-class outputs (Project-hub, SESSION-CONTEXT, initiative-tracker, status-data.json, confluence-pages.json, optionally workshop pack). Before generating outputs, apply the **"What I'll produce next" declaration** rule from `references/co-thinking-protocol.md`, surface planned artefacts upfront and ask the user to select which to produce. The exit gate (final step) is the highest-risk point for over-production. There is no canvas step here, canvas is on demand only (`/canvas`, `/status`).

## Load cross-initiative learnings first

Before reviewing the intake, **read `_workstream/learnings.md`** (the canonical, persistent cross-initiative learnings file — not the sample shipped at `skills/ba-assistant/learnings.md`). This file contains patterns and watchlist items from previous initiatives that should inform how this intake is conducted.

Use the learnings to:
- Pre-populate the Anti-Pattern Detector's initiative-specific watchlist with relevant patterns
- Tailor intake questions to probe for patterns that have appeared before
- Surface any patterns that look immediately relevant ("this initiative has data work  -  we know from learnings that data policy decisions are long-lead, let's flag that now")

Do not lecture the user with the full learnings file. Use it silently to tune the intake conversation, surfacing patterns only when they become relevant.

## Opening prompt

Phase 0 is **not** a single "tell me about it then I'll take it from there" exchange. It is a deliberate, visible sequence with the user, who must always be able to see which step is running, what has been captured, and what is coming next.

Open with (workspace context and research already happened in `ba-new-initiative` before this point):

> "Now that I've got the background, let's make sure we really understand the
> problem and what success looks like.
>
> First question: **what are we working on?** Share your PM brief, initiative name,
> or just tell me what you know."

## Intake sequence

Run these steps in order. The user sees them as a numbered Phase 0 progress checklist in chat; the table below is internal sequencing.

**Before step 1:** `ba-new-initiative` already scaffolded the folder, ran workspace
context, and did the multi-source research (Confluence, Jira, Glean, web, regulator
gate, AI source verification). Read its findings from `SESSION-CONTEXT.md`. Only
redo workspace context or research here if this initiative predates that skill, or
its output is missing or clearly stale.

| # | Step | What it does | Sub-skill invoked |
|---|---|---|---|
| 1 | **Confirm complexity** | Present a complexity choice (Lean / Standard / Full) via `AskQuestion`, informed by `ba-new-initiative`'s research. If a regulator gate fired during that research, Lean is unavailable. |  -  (this skill) |
| 2 | **Problem statement interrogation** | Invoke Requirements Interrogator in Discovery mode for the problem statement. One good question at a time, follow the thread, surface the underlying need. Lean intakes skip, straight to scope + RAID. | `ba-requirements-interrogator` |
| 3 | **Success metrics interrogation** | Invoke Requirements Interrogator in Discovery mode for success metrics. Same conversational pattern. Lean intakes skip, straight to scope + RAID. | `ba-requirements-interrogator` |
| 4 | **Scope slicing light pass** | Invoke Feature Slicing & Sequencing in *intake light pass mode*. Produce 2-3 candidate slice axes with reasoning + trade-offs + recommendation. Get user co-shaping via `AskQuestion`. Result writes to `status-data.json → initiative.intakeLightSlices` and feeds Phase 3 slicing as a starting point. Strict scope: light pass only, full slice register, critical path, sequencing plan, MoSCoW matrix are Phase 3 outputs. Lean intakes skip. | `ba-feature-slicing-and-sequencing` |
| 5 | **Phase 0 exit gate** | Present the intake summary + draft RAID back to the user. No canvas here, canvas is on demand only (`/canvas`, `/status`). Every v1 artefact (problem statement, success metrics, scope, RAID) is marked "draft pending PM approval" by default. Record the PM name and approval status in the **tracker's PM approval register** (`raid-format.md` § Tracker-owned structured registers); the `status-data.json → initiative.pmApproval` mirror follows on next canvas refresh, whenever that happens. End with an `AskQuestion` offering proceed / refine problem / refine metrics / pull more context / request PM review now. Never auto-advance to Phase 1. Never present v1 outputs as authoritative until PM sign-off is captured. |  -  (this skill) |

Show a visible status header to the user every time a sub-skill is invoked, e.g.
`> Running: Requirements Interrogator (Discovery mode) → problem statement`. See Phase 0 progress checklist in the orchestrator for the user-facing step names.

If step 2 or 3 surfaces that the problem or metrics need more thinking, log them
as unknowns in the tracker and still proceed to steps 4-5. The Phase 0 gate gives
the user the choice to refine or move on at risk.

### PM approval state (mandatory at the exit gate)

Before moving to Phase 1 kickoff prep, present the intake summary table, draft RAID, and confidence scores back to the user, and **end with an AskQuestion** offering: proceed to Phase 1 / refine the problem statement / refine success metrics / pull in more context first / **request PM review now (draft message)**. Do not auto-advance.

- Capture the PM's name in `status-data.json → initiative.pmApproval.pm`.
- Set `initiative.pmApproval.status = 'pending'` (or `'requested'` if the user has chosen to draft the review message now).
- All v1 outputs (problem statement, success metrics, scope, RAID) are drafts until `initiative.pmApproval.status === 'approved'`.
- The canvas, status-snapshot HTML, and project hub page MUST display a visible `DRAFT  -  pending <PM name> approval` banner until sign-off is captured.
- If the user does not yet know who the PM is, record `pm: 'TBC'` and flag it as the top unknown in the tracker, but still display the banner.

Never present v1 outputs as authoritative, to the user, to downstream skills, or in Confluence/Jira, until the PM approval state is recorded as `approved`.

---

## Complexity signal

Not every intake needs the full Phase 0 treatment. Adapt depth to size of work.

| Level | Definition | Scope | What runs |
|---|---|---|---|
| **Lean** | Small, incremental, well-understood, low blast radius | 1–3 stories, 1 feature, 1–4 weeks, no compliance, no new stakeholders | Confirm complexity + context extraction + PM questions + scope exploration + RAID + exit gate. Skips whatever each Task above marks "Lean intakes skip" (problem/metrics interrogation, slicing). |
| **Standard** | Medium initiative with some uncertainty | Multiple stories, 1–2 features, 1–3 months, normal compliance touch, known stakeholders | All Tasks above. |
| **Full** | Major initiative, multi-feature, sustained change | Multi-feature, 3+ months, compliance-driven, new sponsor or stakeholders, high blast radius | All Tasks above, plus Current State Assessment, Sponsor Engagement, Workshop Design (kickoff) before the exit gate. |

**Ask the user AFTER `ba-new-initiative`'s research findings are in hand**, not before, so they pick informed by what was found. If the regulator gate fired during that research, Lean is unavailable; tell the user why ("Lean isn't available, regulator trigger detected").

**Override the user's pick** when the situation demands it. Examples: compliance work in scope → Lean → Standard; multi-cohort scope → Standard → Full; sparse 1-line brief with nothing found → Lean → Standard. Always tell the user what you bumped and why. They can re-override and accept the risk; log the decision in the tracker.

**Compliance scope expansion warning:** When a regulatory/compliance keyword is detected ([regulator] and the regulators/standards configured for your jurisdiction per CUSTOMIZATION.md §6), surface this risk flag: *"Compliance initiatives frequently expand in scope once implementation complexity is understood. Even 'simple registration' tasks have historically grown into multi-week architecture and lifecycle work. Budget for scope discovery  -  consult engineering on Day 1 before committing to timelines."* (Added 23 Jun 2026 Sample-Compliance-Initiative retro  -  initiative went from "2-day fix" to multi-week architecture piece once engineering was consulted.)

**Recording:** write `initiative.complexity` to `status-data.json` after the user picks. The canvas and other skills read this to tune behaviour.

**Revisit anytime**  -  at any phase boundary or when scope grows, the user can bump complexity up or down.

## Source skepticism principles (apply throughout intake)

Every source the assistant reads  -  Confluence page, Jira ticket, Glean result, web
page  -  must be **vetted before it informs analysis**. Default stance: **skeptical,
not credulous.** Documents are often stale, written by AI without verification, or
authored by someone who doesn't have current context.

For every source, capture and surface:

| Signal | What to record | Action if poor |
|---|---|---|
| **Last modified date** | ISO date | If >6 months for fast-moving topics or >12 months for stable topics → flag as **stale**. Challenge the user: "this hasn't been updated since X  -  should I treat it as current?" |
| **Author** | Person or "unknown" | If author no longer at [Organisation] or unknown, flag for verification. |
| **AI-generated signal** | Detect AI markers: overly polished prose, generic phrasing, hedging language, no specific examples, no named people or dates, "this document outlines..." preamble | If suspected AI-generated and unverified → flag as **unverified AI content**. Do NOT treat as authoritative. Ask the user: "this looks AI-generated  -  do you know who verified it?" |
| **Authority** | Authoritative (signed-off Confluence page, official policy doc, vendor doc) / Informal (Slack thread, draft page, personal notes) / Unknown | Weight authoritative sources higher. Treat informal as evidence, not fact. |
| **Recency vs topic velocity** | Match document age against how fast the topic moves (regulation = stable; product changes = fast) | Flag mismatches. |

**Never assume documents are current or correct.** Default to challenging the user
when you find content that might be stale, AI-generated, or unverified  -  using
`AskQuestion` with clear options (use it / verify it / ignore it).

This stance is informed by the Glean `confidence-signals` skill and the always-active
`glean-result-vetting.mdc` rule. Apply the same rigour to non-Glean sources.

---

## Multi-source research: already done

`ba-new-initiative` runs the full search (Confluence, Jira, Glean, web), the
regulator gate, AI source verification, and skip-acknowledgement, and writes
findings to `SESSION-CONTEXT.md` before this skill is invoked. Read that instead of
re-searching. Only redo it here if this initiative predates that skill, its findings
are missing, or something has clearly gone stale since. If you do redo it, follow
the same procedure documented in `sub-skills/ba-new-initiative/SKILL.md` step 6, it
is the one place that procedure is written down now.

---

## Workspace setup

`sub-skills/ba-new-initiative/SKILL.md` captures this at scaffolding time for any
initiative created after that skill existed. Before Task 1 below, check
`status-data.json -> initiative` (or the tracker) for a cached workspace context
first. If it's there, use it and go straight to Task 1. Only run the capture below
for an initiative that predates that skill or skipped the question.

When capture is needed, batch related questions into one or two `AskQuestion` panels
rather than 8 sequential questions, the user is filling in a form, not being
interviewed.

Capture:

- **Jira project key**  -  e.g. PROJ, SW
- **Jira template story** (optional)  -  paste a key (e.g. `PROJ-XXXX`) to use its structure as the template for new stories, or "use most recent" to pick the project's latest, or "skip" (ask again at Delivery Definition). Stored as `initiative.jiraTemplateKey`.
- **Confluence space + parent page**  -  record page IDs in `confluence-pages.json`
- **All-in-one / intake doc link**  -  Confluence URL, PM brief, BRD, PRD, or pasted text
- **Repositories**  -  if technical
- **Slack / Teams channel**  -  where initiative comms happen
- **Source of the intake**  -  verbal / all-in-one doc / Confluence / BRD / Jira ticket
- **Stakeholders already involved**  -  who's been engaged, where the conversations are captured

If the user only knows half the answers, leave blanks and log gaps as unknowns in the tracker.

Cache the workspace context so every subsequent skill can write Jira / Confluence / Slack outputs without re-asking.

### Confluence hierarchy mapping (mandatory at Phase 0)

If the initiative has an existing Confluence space or hub page:

1. **Query the hierarchy**  -  use `getConfluencePageDescendants` to map all existing child pages under the initiative hub
2. **Create `confluence-pages.json`**  -  record every page with its `pageId`, `parentPageId`, `title`, and `url`. Include feature parent pages and analysis hub pages.
3. **Define parent rules**  -  document in `SESSION-CONTEXT.md` which parent page new pages should be created under (e.g., "Feature B pages → parent = `<id>`"). This prevents pages being created under the wrong parent.
4. **Record in SESSION-CONTEXT.md**  -  add the full page hierarchy table so every session starts with correct Confluence structure.

This prevents the common pattern of pages being created ad-hoc under wrong parents, requiring later audits and moves.

## Tasks

Workspace context and multi-source research happened in `ba-new-initiative` before
this skill was invoked (see the two sections above). These tasks form the visible
intake conversation and close out Phase 0.

1. **Confirm complexity** – Now that research findings are known, present a complexity `AskQuestion` (Lean / Standard / Full) with the findings visible. If the regulator gate fired, Lean is unavailable.
2. **Context extraction** – Summarise the PM's all-in-one or early brief: problem, objective, proposed success metrics, high-level scope, stakeholders, deadlines, constraints. Translate into a concise summary suitable for kickoff. Pull in anything relevant from the research findings.
3. **Interrogate the problem statement** – Invoke Requirements Interrogator in Discovery mode. One good question at a time. Surface: who experiences the problem, what does it cost them, how are they dealing with it today, what would change without it. Output → provisional problem statement marked "draft  -  pending PM approval".
4. **Interrogate success metrics** – Invoke Requirements Interrogator in Discovery mode. Surface: what behaviour changes if this works, how would we know, what data already exists, what's the smallest measurable signal. Output → provisional metric statement(s) marked "draft  -  pending PM approval".
5. **Scope slicing light pass** – Invoke `ba-feature-slicing-and-sequencing` in *intake light pass mode*. Surface 2-3 candidate slice axes (by workstream / by cohort / by feature) with rationale + trade-offs + recommendation. Get user co-shaping via `AskQuestion`. Output → `status-data.json → initiative.intakeLightSlices` and a Decision row in the tracker. Strict scope: light pass only  -  no full slice register, no sequencing plan, no MoSCoW matrix (those are Phase 3). Lean intakes skip.
6. **Questions for PM** – For everything *other than* problem, success metrics, and slicing axes (stakeholders, deadlines, constraints, untested claims from source material, missing baselines), build the `questions-for-pm.md` list per the Output Guidelines template. Put each question to the user in chat  -  they may have the answer informally from the PM (capture with verbal provenance), or it goes on the list for the PM-BA alignment meeting.
7. **Scope and out-of-scope exploration** – Challenge proposed scope: what's in, what's out, what dependencies on other teams or systems exist, where might scope creep occur.
8. **Early RAID identification** – Highlight obvious Risks, Assumptions, Issues, and Dependencies. Record in preliminary RAID log (handed to Risk & Tracker skill). Decisions table format: `ID | Decision | Owner / Made by | Date | Status`.
9. **Prepare kickoff agenda items** – Suggest agenda points and questions for the stakeholder kickoff meeting based on gaps identified. Hand to Kickoff Preparation skill.
10. **Phase 0 exit gate** – Present the intake summary table + draft RAID + confidence scores + `questions-for-pm.md`. No canvas here, canvas is on demand (`/canvas`, `/status`). Confirm PM name and capture approval status in the **tracker's PM approval register**; the status-data mirror follows whenever the canvas is next refreshed. Make the approval state visible everywhere v1 outputs appear (project hub, status page, and the canvas whenever it exists). End with `AskQuestion`: proceed to Phase 1 / request PM review now (draft message) / refine problem statement / refine success metrics / pull more context first. Never auto-advance.

## Typical Questions to Ask

- What problem are we solving and who experiences it?  Why is it important now?
- What measurable outcome would indicate success (e.g., KPIs, targets)?
- What is the proposed high‑level scope?  What features or processes are in scope?  What is explicitly out of scope?
- Who are the key stakeholders (PM, sponsors, compliance, legal, design, operations, engineering)?
- Are there any fixed deadlines or regulatory dates?
- What known constraints (budget, resourcing, policy) exist?
- Have any assumptions been made about compliance, design, or technical feasibility?
- Are there known risks or dependencies already?

## Output Guidelines

The Intake Reviewer should produce:

- **Intake summary table** – A concise table capturing problem, objective, success metrics, high‑level scope, stakeholders, deadlines, constraints, assumptions, and initial RAID items. Clear labels and short phrases rather than long paragraphs.
- **`questions-for-pm.md`** – A structured list of questions for the PM that surfaced during source reading and interrogation. This is a primary Phase 0 output, not a side artefact. Goal: a pre-D1 PM-BA alignment meeting with this list as the agenda.
- **Kickoff agenda suggestions** – A short agenda outline for the first stakeholder meeting, highlighting key alignment points and decisions that need to be made early.
- **Preliminary RAID log** – A draft list of risks, assumptions, issues, and dependencies identified during intake. Pass this to the Risk & Tracker skill for ongoing management.

### `questions-for-pm.md` template

```markdown
# Questions for PM  -  [Initiative name]

Generated during Phase 0 intake by [BA name]. To be reviewed with [PM name] before D1 kickoff.

Each question came from one of: source critique (reading a Confluence page / Jira ticket / regulator doc surfaced an assumption or untested claim); interrogation (drafting problem statement / metrics / scope generated a question the BA couldn't answer alone); stakeholder gap (a stakeholder mentioned in sources but not yet engaged).

Status legend: `informal` = PM answered verbally (provenance captured) · `open` = needs PM input · `blocked` = can't progress past intake without this.

| ID | Question | Source / Trigger | Status | PM answer (if informal) | Provenance |
|---|---|---|---|---|---|
| Q-01 | [question] | [source] | open / informal / blocked | [verbal answer if any] | [date + how heard] |

**Pre-D1 alignment recommendation:** [30 / 45 / 60 min] meeting between PM and BA before D1 kickoff with these questions as the agenda.
```

## Challenge Rules

The Intake Reviewer challenges vague or unjustified statements immediately but does not deep‑dive into discovery.  When something is unclear:

- State the ambiguity succinctly and propose a clarifying question.
- If an assumption is unstated, call it out: "It seems we're assuming X.  Should we validate that?"
- Highlight potential scope creep if the PM's description is broad or unspecific.  Suggest clearly defining what is out of scope.
- Do not block progress; simply capture questions and assumptions and proceed to kickoff preparation.
