---
name: ba-feature-slicing-and-sequencing
description: Feature slices before epics, prioritisation, critical path. Use when slicing or sequencing work in BA Assistant.
---

# Skill: Feature Slicing and Sequencing

## Description

The Feature Slicing and Sequencing skill breaks an initiative into manageable, independently valuable **feature slices** before converting them into epics and stories.  It balances business priorities, uncertainty, critical path dependencies, and lead times to propose a delivery order and parallelisation plan.  It distinguishes business priority (what's most valuable), analysis priority (what needs understanding first), delivery priority (what should be built first), and **critical path priority** (what must start earliest to avoid blocking later).  This skill integrates PM input on dates and priorities and surfaces long‑lead activities such as compliance reviews, design, or spikes.

## Intake light pass mode (added May 2026 after [previous initiative retro])

This section is invoked from **Intake Reviewer hook 4.5** — a *light* slicing pass run during Phase 0 intake, BEFORE the deeper Phase 3 slicing work below. The purpose is to surface candidate slice axes early so the BA and PM can co-shape scope at intake, not have it dropped on them at Phase 3.

### Strict scope — what the light pass produces

- 2-3 **candidate slice axes** with reasoning + trade-offs (e.g., "by compliance vs commercial workstream", "by cohort", "by feature", "by user persona")
- For each candidate axis: 1-line rationale, what it surfaces well, what it hides
- A recommended axis with reasoning (the assistant's take, not fence-sitting)
- An `AskQuestion` for user co-shaping: pick the recommended axis / pick a different axis / combine axes / defer to Phase 3

### Strict scope — what the light pass does NOT produce

- Full slice register
- Critical path tracker (deferred to Phase 3)
- Sequencing plan or parallelisation map
- Story-level breakdown
- MoSCoW matrix per slice

These are explicit Phase 3 outputs. The light pass exists to inform Phase 3, not pre-empt it.

### Format

When invoked from Intake Reviewer hook 4.5, produce a chat output following this pattern:

```
Candidate slicing axes for this initiative:

1. By workstream (e.g. compliance vs commercial)
   - Surfaces well: distinct timelines, distinct stakeholder groups, distinct risk profiles
   - Hides: cross-workstream dependencies, shared infrastructure
   - Best when: the initiative has a regulatory deadline and a separate commercial outcome

2. By cohort (e.g. existing customers vs new customers)
   - Surfaces well: persona-specific UX, segmentation logic, cohort-specific KPIs
   - Hides: shared platform changes, common compliance lifts
   - Best when: cohorts have materially different needs or constraints

3. By feature (e.g. payment screen, T&C, settings)
   - Surfaces well: traditional dev sequencing, technical dependencies
   - Hides: outcome traceability, cross-feature user journeys
   - Best when: solution direction is locked and persona work is uniform

Recommended axis: [axis with reasoning — the assistant's take]
Trade-off if you take the recommendation: [what's given up]

[AskQuestion: agree with recommendation / pick a different axis / combine axes (free-text) / defer to Phase 3]
```

The output candidate axes set is initiative-specific — the 3 above are generic examples. Tailor the axes to the actual initiative shape (e.g. for a regulatory + commercial dual-track, suggest "by workstream" and "by regulatory deadline phase"; for a multi-cohort feature rollout, suggest "by cohort" and "by feature"; etc.).

### Outputs

- Candidate axes set + user-selected axis → `status-data.json → initiative.intakeLightSlices` (preliminary, marked `phase: 'intake-light'`)
- User-selected axis → tracker as a Decision (with `Owner / Made by` and Date columns populated)
- Carries forward to Phase 3 slicing as the starting point — Phase 3 builds on it, doesn't restart from blank

### When to skip the light pass

- **Lean intake** — skips this hook by default (lean = single feature, no cohorts, no parallel workstreams)
- **User-deferred** — user explicitly defers via the `AskQuestion` (decision logged in tracker)
- **Already-sliced initiatives** — if a prior session has produced an axis, hook 4.5 reads it and offers to confirm or revise rather than re-deriving from scratch

This light-pass mode **does not replace Phase 3 slicing**. It exists to ensure scope-shape is co-thinking territory at intake, not a post-hoc Phase 3 surprise.

> **Cross-cutting rule:** This skill produces multiple artefact-class outputs at full Phase 3 invocation (slice register, critical path tracker, sequencing rationale, priority alignment, parallelisation plan). Before generating outputs, apply the **"What I'll produce next" declaration** rule from `ba-assistant\SKILL.md → Co-thinking and artefact production protocol` — surface planned artefacts upfront and ask the user to select. The intake light pass mode (above) is intentionally constrained and does NOT trigger the multi-artefact rule.

---

## Tasks

1. **Identify feature boundaries** – Use the high‑level requirements and current state understanding to group functionality into discrete slices that can be analysed and delivered independently.  Consider user journeys, system components, data flows, and value streams.
2. **Assess priorities** – For each slice, evaluate:
   - *Business priority*: contribution to business goals or user value.
   - *Analysis priority*: the degree of unknowns or uncertainty.
   - *Delivery priority*: ordering for development based on dependencies and critical path.
   - *Critical path priority*: long‑lead items that must start early (e.g., compliance approvals, design work, external integrations).
3. **Identify critical path items** – List activities with fixed dates or long lead times (compliance, legal, design, service design, spikes, ADRs, data analysis, stakeholder sign‑offs).  For each, note the owner, due date, lead time, what it blocks, and its current status and risk.
4. **Propose sequencing** – Recommend a delivery order that balances value, risk, and dependency management.  Identify which slices can be executed in parallel versus sequentially.  Suggest deferring slices that have low value or heavy dependencies until later.
5. **Capture rationale** – For each slice and sequencing decision, record the reasoning: why it's ordered first, next, or later; what dependencies it has; and what the potential risks are.
6. **Interact with PM priorities** – Ask the PM/product owner about target dates and must‑have outcomes.  Incorporate these into the sequencing plan.  Highlight conflicts between business priorities and critical path needs.
7. **Update tracker** – Pass the slicing plan, critical path items, and sequencing rationale to the Risk & Tracker skill and orchestrator for ongoing management.

## Impact Mapping — alternative / complementary slicing technique

For initiatives where the business goal is clear but the path is fuzzy (e.g. "increase merchant onboarding completion by 15%"), run **Impact Mapping** before — or alongside — feature slicing. Impact Mapping forces the slicing conversation to start from the *goal*, not the *backlog*.

The four levels:

```
GOAL (WHY)
  └── ACTORS (WHO — can influence the goal)
       └── IMPACTS (HOW — behaviour changes from each actor that would help achieve the goal)
            └── DELIVERABLES (WHAT — features/things we could build to cause those behaviour changes)
```

**Example — "Increase new feature onboarding completion to 90%":**

```
GOAL: 90% new feature onboarding completion (up from 72%)

  ACTOR: Existing customer (< 12 months)
    IMPACT: Completes new feature sign-up in the same session as bank verification
      DELIVERABLE: Pre-fill form from existing customer application
      DELIVERABLE: Single-page confirmation step
    IMPACT: Doesn't drop off when shown the T&C page
      DELIVERABLE: Summarised T&C with explicit changes from v3 to v4
      DELIVERABLE: Allow T&C review post-signup (deferred consent)

  ACTOR: [ops team]
    IMPACT: Approves new feature applications within 4 hours (vs 24 hours)
      DELIVERABLE: Auto-approval rule for low-risk segment
      DELIVERABLE: Triage queue showing new feature applications separately
    IMPACT: Doesn't have to look up source customer record manually
      DELIVERABLE: Linked record view in ops portal

  ACTOR: Compliance team
    IMPACT: Signs off the auto-approval rule
      DELIVERABLE: Auto-approval logic documented + audit trail
    IMPACT: Doesn't require re-verification for in-scope cohort
      DELIVERABLE: Confluence policy update + sign-off
```

**Why this helps slicing:**

- Slices map naturally to *Actor + Impact* combinations (e.g. "Customer pre-fill slice", "Ops auto-approve slice", "Compliance sign-off slice")
- Deliverables can be ranked by which Impact they most efficiently cause — easy to defer or cut
- The Goal stays visible — features get cut without losing line-of-sight to outcomes
- Surfaces non-software deliverables (Confluence policy update, Ops portal training) that pure feature slicing tends to miss
- Surfaces actors we haven't engaged (in this example: compliance was easy to forget if we'd started from features)

**When to use Impact Mapping vs jump straight to feature slicing:**

| Use Impact Mapping when | Skip to feature slicing when |
|---|---|
| Goal is measurable but path is unclear | Solution direction already locked |
| Multiple actors influence the outcome | Single user type / single workflow |
| Behaviour change is part of the goal | Pure technical / system change |
| Hard to choose what to cut | Scope already minimal |
| Stakeholders are arguing about scope | Stakeholders aligned on scope |

**Output:** Hand off the four-level structure to **Visual_Storytelling** to produce a mind-map diagram (Mermaid `mindmap` or `flowchart LR` with explicit hierarchy). The mind-map itself becomes a slicing and prioritisation tool — point at branches and say "what if we don't do this Impact?" or "which Deliverable for this Impact is highest leverage?"

## Typical Questions to Ask

- What are the natural feature or capability boundaries within this initiative?  Can we separate the work into distinct slices that deliver independent value?
- For each slice:
  - How important is this to the overall business goal or customer outcome?  (Business priority)
  - How much is unknown or unclear?  Are there open requirements or technical questions?  (Analysis priority)
  - Does this slice depend on another slice or external team?  (Delivery priority)
  - Are there any long‑lead activities (compliance reviews, legal approvals, service design, spikes, ADRs, design/copy) that must start early?  (Critical path priority)
- What fixed dates or milestones exist (e.g., regulatory deadlines, external commitments, product launch dates)?
- Which slices could developers start immediately to avoid idle time while analysis continues for later slices?
- Which slices reduce the most risk or uncertainty if tackled first?  Which deliver value fastest?
- Which slices or tasks can run in parallel without blocking each other?  Which must be sequential?
- Are there slices that might be deferred because their value is low or dependencies are high?  What are the trade‑offs?
- How do PM priorities (must‑have features, target release dates) map to your sequencing plan?  Are there conflicts between business priority and critical path needs?

## Output Guidelines

The Feature Slicing and Sequencing skill should produce:

- **Feature breakdown table** – A table listing each slice with columns such as:
  - *Slice name*
  - *Business priority* (High/Medium/Low)
  - *Analysis priority* (High/Medium/Low)
  - *Delivery priority* (High/Medium/Low)
  - *Critical path priority* (High/Medium/Low)
  - *Dependencies* (teams, systems, compliance, legal, design, spikes)
  - *Reasons for order* (short justification)
  - *Can run in parallel?* (Yes/No)
  - *Deferred?* (Yes/No with explanation)
- **Critical path tracker** – A table of long‑lead items with columns: Item, Owner, Needed by (date), Lead time, Blocks, Status, Risk.  This feeds into the Risk & Tracker skill.
- **Sequencing rationale** – A paragraph or bullet list explaining the recommended order: which slices are first, which are parallel, which are deferred, and why.  Highlight trade‑offs between value, uncertainty, and critical path.
- **Priority alignment notes** – Notes summarising PM/product owner priorities and how the sequencing plan addresses or conflicts with them.  If conflicts exist, propose mitigation or escalation.
- **Parallelisation suggestions** – A list of tasks that could be run concurrently (e.g., dev spike for slice A, compliance review for slice B, UX design for slice C) to reduce overall duration.

## Challenge Rules

The slicing skill must protect against typical pitfalls:

- **Premature solutioning:** Do not define epics or stories until feature slices are understood.  Avoid committing to technical solutions during slicing; focus on value and uncertainty.
- **Overscoping:** If a slice encompasses too many disparate capabilities, challenge the user to break it further.  Smaller slices deliver value faster and reduce risk.
- **Ignoring long‑lead items:** Surface long‑lead activities as critical path items.  Highlight if something needs to start early despite its business priority being low.
- **Misaligned priorities:** Challenge if the PM's priority conflicts with critical path; propose an alternative approach or highlight risk.
- **Lack of rationale:** Require a reason for ordering decisions.  If the user cannot justify, mark it as an assumption or risk.
- **Gating flexibility:** Recognise that unknowns might allow slices to proceed in parallel or be deferred.  Use the active prompting approach rather than strict gating.

---

## Critical Path and Priority Analysis (Wave 3 — merged from ba-critical-path-and-priority)

This section absorbs the former `ba-critical-path-and-priority` skill. Critical path and priority analysis are the **zoom-out view** of slicing — they consider cross-slice dependencies, external deadlines, long-lead items, and reconcile business priority with sequencing reality. They live here because every critical-path decision changes the sequencing plan and vice versa.

### Critical-path tasks

1. **Identify critical path items** — Compile a list of tasks, approvals, and activities that have long lead times or fixed deadlines (e.g., compliance reviews, legal sign-offs, design work, integration agreements, data migrations). For each item, record: owner, required-by date, lead time, what it blocks, status, and risk.
2. **Analyse schedule constraints** — Gather known dates from stakeholders (PM's must-have delivery dates, regulatory deadlines, release windows, marketing launches) and compare them with the slicing plan and backlog sequence. Highlight conflicts or tight lead times.
3. **Reconcile priorities** — Compare business priorities (from the PM/product owner via the MoSCoW matrix) with critical-path realities. Identify mismatches (e.g., a Must rated feature requiring a long lead time starting late). Suggest adjustments or trade-offs.
4. **Propose start dates** — Recommend when each critical-path item and slice should start to meet deadlines. Suggest initiating long-lead activities early, even if they deliver later, to reduce risk.
5. **Maintain the critical-path tracker** — Produce and update a table summarising all critical-path items. Provide visual cues (high-risk / at-risk) when an item is at risk of missing its start date. This data flows into `status-data.json → criticalPath[]` and renders in the Canvas → Critical Path tab.
6. **Support scenario analysis** — Allow the user to explore "What if?" scenarios (e.g., "What if compliance takes an extra month?") and adjust the schedule accordingly. Explain how schedule changes impact priority and sequencing decisions.

### Priority types — always distinguish (do not collapse)

| Priority type | Meaning | Where it comes from |
|---|---|---|
| **Business priority** | What stakeholders value most | PM/product owner via MoSCoW matrix |
| **Analysis priority** | What must be understood before other analysis can proceed | BA judgment + Discovery findings |
| **Delivery priority** | What engineering needs to start first | Tech Lead + delivery team |
| **Critical-path priority** | What blocks delivery if not started early (compliance, design, legal, data) | This section |

A low business priority item may still need early action due to long compliance lead times. Always evaluate: *what could block delivery later, what needs to start now, what can safely wait.*

### Critical-path-specific questions

- What tasks require significant lead time (compliance review, legal sign-off, design iterations, external integrations, hardware ordering, procurement)? Have we accounted for these in the slicing and sequencing plan?
- Are there fixed deadlines we must meet (regulatory compliance, contractual dates, marketing launches)? What is the latest start date for each long-lead item to meet these deadlines?
- Which slices have dependencies on critical-path items? How will delays impact overall delivery?
- What are the PM's MoSCoW priorities? Do they conflict with critical-path realities? Which priorities can be adjusted vs which are non-negotiable?
- How should we sequence the start of analysis, design, compliance, development, and testing to ensure the critical path is protected? Is it possible to parallelise some tasks?
- What are the risks if a critical-path item is delayed? What mitigations can we plan (early engagement, parallel work, additional resources)?
- What happens if a critical-path assumption changes (e.g., compliance needs more time)? How will this affect the schedule? Are there contingency plans?

### Critical-path-specific outputs

- **Critical path tracker** — A table listing all long-lead tasks with columns: Item, Owner, Required-by date, Lead time, Blocks, Status (Not Started / In Progress / At Risk / Complete), Risk level. Include notes on mitigation or next actions. Writes to `status-data.json → criticalPath[]`.
- **Schedule alignment report** — A summary comparing business priorities with critical-path realities. Note where the slicing or sequencing plan needs adjustment and propose new start dates. Use bullet points or a small table to present conflicts and recommendations.
- **Priority reconciliation** — A short narrative explaining any trade-offs between business priority and critical-path priority. Clearly state which priorities drive the schedule and which might be adjusted. Suggest stakeholder conversations if alignment is needed.
- **Scenario recommendations** — If the user explores alternative scenarios, produce updated critical-path and sequencing plans, highlighting the impact on delivery dates and resource utilisation.

### Critical-path-specific challenge rules

- **Be realistic** — Do not ignore lead times or rely on optimistic assumptions. When in doubt, use conservative estimates and highlight risks.
- **Separate priority types** — Always distinguish between business priority (value), delivery priority (development order), analysis priority (unknown reduction), and critical-path priority (schedule risk). Explain why differences matter.
- **Promote early starts** — Recommend starting long-lead tasks early even if their slice is lower priority. Warn that delaying such items could jeopardise the entire timeline.
- **Facilitate trade-off discussions** — If the PM's priorities conflict with critical-path, recommend bringing this to stakeholder attention. Provide talking points for negotiation.
- **Stay updated** — Update the critical-path tracker whenever lead times, deadlines, or dependencies change. Notify the orchestrator of changes.

### Migration note (Wave 3)

This content was previously the `ba-critical-path-and-priority` skill. The standalone skill is now a SUPERSEDED marker; all critical-path work is performed here as part of slicing + sequencing.
